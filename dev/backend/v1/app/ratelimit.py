"""限速器单例（slowapi）— 按真实客户端 IP 识别（反代后取 X-Forwarded-For）。

全后端共用这一个 limiter 实例：main.py 挂中间件 + 异常处理器，
accounts / auth 等接口用 @limiter.limit 装饰器。集中成单例保证计数真正共享、
enabled 开关只控一处（原先 main/accounts/auth 各建独立实例，计数互不相通）。

enabled 策略：仅 staging / production 启用限速；dev（含 pytest 测试套件）关闭。
否则测试里大量登录会瞬间撞 429，且本地开发不需要限速。
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import get_settings

# dev（含测试）关、staging / production 开
_rate_limit_enabled = get_settings().app_env in ("staging", "production")


def _client_ip(request) -> str:
    """限速分桶键 — 取 X-Forwarded-For 最右一跳（自家反代确认的对端 IP）。

    生产是 Caddy 反向代理 → gunicorn，未配信任代理头时 request.client.host 对
    所有外部客户端都是 Caddy 的内网 IP，slowapi 默认的 get_remote_address 会让
    全站共享一个桶 —— 登录限速（学生 20/min、老师 10/min、注册码 10/hour）退化成
    桶级 DoS（一台机器打满共享桶，全体被 429 挡在登录外）。
    取值必须用**最右**而非最左：XFF 左侧是客户端可自带的任意内容，取最左值等于
    信攻击者自报 IP，每请求换一个伪造值即换一个新桶、限速整个失效；最右一跳无论
    代理是「替换」还是「追加」模式都是自家代理写入的对端地址（2026-07-17 审查
    安-中-2 修复，audit.py 同口径）。无 XFF（本地直连 / 测试）回退 client.host。
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_client_ip, enabled=_rate_limit_enabled)
