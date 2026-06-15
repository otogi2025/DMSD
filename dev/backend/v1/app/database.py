"""SQLAlchemy 2.x 同步 engine + session.

设计权威 BACKEND_DESIGN_LOG.md §1.1 は async を推奨だが、本実装は同期版で起手:
- itsuki がコード読みやすい
- FastAPI の sync route で十分パフォーマンス出る
- async 化は後で `Session` → `AsyncSession` 置換でいける

dev = SQLite ファイル (auto-create), prod = PostgreSQL 16+。
"""

from collections.abc import Generator
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from .config import get_settings

settings = get_settings()

# 全系统时区口径（宿舍在日本，单一时区）
_UTC = timezone.utc
_JST = ZoneInfo("Asia/Tokyo")


class TZDateTime(TypeDecorator):
    """全 ORM 时间列统一时区口径 —— 解决「SQLite 读回丢时区、不同字段存的时区还不一样」的混乱。

    - 写入(process_bind_param)：一律转成世界标准时(UTC)存。
      值带时区 → astimezone(UTC)；值无时区 → 视为已是 UTC
      （应用层写入要么 datetime.now(timezone.utc)，要么各 router 输入侧已归一成带时区；
       func.now() 服务端默认本身就是 UTC）。
    - 读出(process_result_value)：一律返回带时区的日本时间(Asia/Tokyo, +09:00)。
      SQLite 读回是无时区的 UTC 墙钟 → 补 UTC 再转 JST；
      PostgreSQL 读回本就带时区 → 直接 astimezone(JST)。

    效果：dev(SQLite) 与 prod(PostgreSQL) 的 API 时间输出完全一致，永远 "...+09:00"，
    iOS / Android 解码不用再「猜」时区（之前无时区会整段解码失败，是真 bug）。
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        # ⚠️ 方法名必须是 process_bind_param（不是 process_bind_value）—— SQLAlchemy 靠
        # 检测子类有没有重写 process_bind_param 来决定要不要生成写入处理器；名字写错会
        # 静默不生效（写入不转换，读出却照转，造成「读对写错」的诡异 bug）。
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return value.astimezone(_UTC)

    def process_result_value(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return value.astimezone(_JST)


class Base(DeclarativeBase):
    """全 ORM model 的 base (declarative 2.x スタイル)。"""

    pass


# SQLite では check_same_thread=False が必要 (FastAPI worker 跨スレッド対応)
_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

# H-12：连接池调优。原来只设 pool_pre_ping，长连接被 DB / 中间网关掐断后才靠 ping 重连。
# - pool_recycle=1800：连接存活超 30 分钟主动回收重建，躲开 Postgres / 云网关的空闲超时
#   （pre_ping 是「用前探测」，recycle 是「定时换新」，两者互补）。SQLite 下无害。
# - pool_size / max_overflow：只对真实连接池（Postgres）有意义，SQLite 用别的池类型，
#   传了会被忽略或报错，所以仅非 SQLite 时显式设。
_pool_kwargs: dict = {"pool_pre_ping": True, "pool_recycle": 1800}
if not settings.is_sqlite:
    _pool_kwargs["pool_size"] = 5
    _pool_kwargs["max_overflow"] = 10

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=(settings.app_env == "dev" and settings.log_level == "DEBUG"),
    **_pool_kwargs,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依存注入用 — request スコープで session を払い出す。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    """开发用 — 启动时全表自动建立。production は Alembic migration へ。"""
    # models を import すると Base.metadata に登録される (循環参照避けで関数内 import)
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
