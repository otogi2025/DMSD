"""设置 (config) — 从 .env / 环境变量读入。

`pydantic_settings.BaseSettings` で型安全な設定読み込み。
`get_settings()` を依存注入経由で使う (キャッシュ済 = process 全体で 1 instance)。

2026-05-21 加: production 环境 fail-fast 校验
    - JWT secret 不能是默认 / 空 / 弱值（A-001 partial — 主会话保留架构层）
    - CORS origins 不能含通配符 "*"（A-007）
    - SQLite 在 production 禁止（A-008）
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# production 禁止的 jwt_secret 默认 / 弱值清单
_FORBIDDEN_JWT_SECRETS = {
    "change-me-in-production",
    "",
    "change_me",
    "secret",
    "default",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    app_env: Literal["dev", "staging", "production"] = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # DB
    database_url: str = "sqlite:///./tomoshibi_dev.db"

    # JWT
    jwt_secret: str = "change-me-in-production"
    # 算法硬锁为安全 HMAC 清单 — 防 .env 误配成 none / 非对称算法导致弱签名或密钥混淆
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_access_expire_min: int = 525600  # 1 年=持久登录（itsuki 2026-06-14 上架拍板；iOS IX-036 据 expires_in 判过期，值大→启动不自动登出，登录后基本不掉，除非手动登出/换手机）
    jwt_refresh_expire_min: int = 43200  # 30d

    # 邮件发送 (D1) — SendGrid 2025 春取消永久免费,换 Resend(永久免费 3000封/月)
    sendgrid_api_key: str = ""  # 弃用,保留避免旧 .env 报错
    resend_api_key: str = ""  # Resend 密钥(re_xxx)— itsuki 注册 resend.com 拿后填 .env;空=dev 模式只记日志不真发
    email_from: str = "noreply@tomoshibi.example.jp"
    email_from_name: str = "Tomoshibi 通知"

    # CORS — 5173 = Vite dev / 3000 = React dev / 8787 = teacher_web standalone HTML 静态服务器
    cors_origins: str = (
        "http://localhost:5173,http://localhost:3000,http://localhost:8787"
    )

    # ログ
    log_level: str = "INFO"

    # 文件上传 — 在线学习申请的契約書（合同 = 网课报名凭证）照片 / PDF
    # upload_dir = 服务器上存上传文件的根目录（相对后端进程工作目录）。
    # 上线时改成挂载盘的绝对路径，如 /var/lib/tomoshibi/uploads。
    upload_dir: str = "./uploads"
    # 单个契約書文件大小上限（字节）— 10 MB。手机拍照 / PDF 一般 1-5 MB，10 MB 留余量。
    contract_max_bytes: int = 10 * 1024 * 1024

    # 点呼机接入（device）— Device_Contract / RollCall_Spec §5.5 + 附录 C.5
    # 场次自动保障后台任务开关。**默认关**：测试 / dev 交互都不跑（防搞挂 546 测试 + 免误建场次）；
    # 生产按需在 .env 置 ROLLCALL_SCHEDULER_ENABLED=true 开启。
    rollcall_scheduler_enabled: bool = False
    # 后台任务轮询间隔（秒）
    rollcall_scheduler_tick_seconds: int = 60
    # auto_end = on_time_end + X 分钟（RollCall_Spec 附录 A.3 候选 5/10/15/30，本波取 15）
    rollcall_auto_end_minutes: int = 15
    # 后端点呼音频目录（运维放置预生成 wav；不存在则 manifest 返回空、播报降级通用提示音）
    rollcall_audio_dir: str = "./var/rollcall_audio"

    # APNs 苹果推送（spec §7.13）— 凭证全空 = dev 正常状态，push.py 记 skipped_no_provider
    # 部署时在生产 .env 填真值：.p8 私钥从 developer.apple.com「Keys」页生成下载（只能下载一次）
    apns_key: str = (
        ""  # .p8 私钥完整 PEM 内容（含 BEGIN/END PRIVATE KEY 行，换行可用 \n 转义）
    )
    apns_key_id: str = ""  # 密钥 ID（10 位，.p8 下载页显示）
    apns_team_id: str = ""  # Apple Developer Team ID（10 位）
    apns_bundle_id: str = ""  # App 的 Bundle ID（正式版 = com.itsuki.tomoshibi）
    # True 打苹果沙盒推送网关（Xcode 直装的开发构建用）；生产 / TestFlight / App Store 构建用 False
    apns_use_sandbox: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


def _validate_production_settings(s: "Settings") -> None:
    """production 环境的 fail-fast 校验。

    上线前必跑：jwt_secret / cors / sqlite 任一不合规直接 raise，
    避免 ops 漏配 .env 时偷偷以默认值起 server。
    """
    if s.app_env != "production":
        return

    # A-001 partial: jwt_secret 不能是默认或弱值
    if s.jwt_secret.strip() in _FORBIDDEN_JWT_SECRETS:
        raise RuntimeError(
            "Production 环境 JWT_SECRET 不能是默认值 / 空 / 弱值。"
            "请设置 .env 的 JWT_SECRET 为 32+ 字符强随机串。"
        )
    if len(s.jwt_secret) < 32:
        raise RuntimeError(
            f"Production 环境 JWT_SECRET 长度不足（当前 {len(s.jwt_secret)} < 32 字符）。"
            "请用 `openssl rand -hex 32` 生成强密钥。"
        )

    # A-007: CORS production 不允许通配符，也不允许 localhost（生产漏配会开放本地跨域）
    if "*" in s.cors_origin_list:
        raise RuntimeError(
            "Production 环境 CORS_ORIGINS 不能含通配符 '*'。"
            "请显式列出 teacher_web / student app 的真实域名 origin。"
        )
    _local_origins = [
        o for o in s.cors_origin_list if "localhost" in o or "127.0.0.1" in o
    ]
    if _local_origins:
        raise RuntimeError(
            f"Production 环境 CORS_ORIGINS 不能含 localhost / 127.0.0.1（检测到：{_local_origins}）。"
            "请将 CORS_ORIGINS 设为真实的 teacher_web 域名，如 https://tomoshibi.example.jp。"
        )
    if not s.cors_origin_list:
        raise RuntimeError(
            "Production 环境 CORS_ORIGINS 不能为空。"
            "请显式列出 teacher_web / student app 的 origin。"
        )

    # A-008: production 不允许 SQLite
    if s.is_sqlite:
        raise RuntimeError(
            f"Production 环境不允许 SQLite（当前 DATABASE_URL={s.database_url}）。"
            "请配置 PostgreSQL：postgresql+psycopg://user:pass@host:5432/dbname"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    _validate_production_settings(s)
    return s
