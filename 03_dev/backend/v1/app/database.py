"""SQLAlchemy 2.x 同步 engine + session.

设计权威 BACKEND_DESIGN_LOG.md §1.1 は async を推奨だが、本実装は同期版で起手:
- itsuki がコード読みやすい
- FastAPI の sync route で十分パフォーマンス出る
- async 化は後で `Session` → `AsyncSession` 置換でいける

dev = SQLite ファイル (auto-create), prod = PostgreSQL 16+。
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """全 ORM model 的 base (declarative 2.x スタイル)。"""
    pass


# SQLite では check_same_thread=False が必要 (FastAPI worker 跨スレッド対応)
_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    echo=(settings.app_env == "dev" and settings.log_level == "DEBUG"),
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
