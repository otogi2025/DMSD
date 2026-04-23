"""
数据库连接配置

demo 阶段用 SQLite（零配置，文件级数据库）。
部署阶段只改 DATABASE_URL 就能切 PostgreSQL，其他代码不动。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Demo 用 SQLite：dmsd.db 文件会自动生成在 backend 目录下
DATABASE_URL = "sqlite:///./dmsd.db"

# 部署版（将来）：
# DATABASE_URL = "postgresql://user:password@localhost/dmsd"

# connect_args 只在 SQLite 需要（允许多线程访问）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 依赖注入用。每个请求打开一个 session，结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
