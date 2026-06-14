"""FastAPI app — Tomoshibi Backend v1.0.

启动:
    cd dev/backend/v1
    cp .env.example .env
    pip install -r requirements.txt
    uvicorn app.main:app --reload

OpenAPI: http://localhost:8000/docs

会话 E 追加 (2026-05-01):
- GET/POST /api/v1/study/*               学習 #14-#20
- GET/POST/PATCH /api/v1/rollcall/*      点呼 #16-#20
- POST /api/v1/teachers/*                教師管理 §3.4
- GET /applications/pending-for-me       役職承認待ち一覧
- POST /applications/{id}/approvals      役職承認/拒否 #10-#13
- PUT /applications/{id}                 修改届
- GET /applications/{id}/audit           審査 audit log
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import get_settings
from .database import create_all
from .routers import (
    accounts,
    admin_accounts,
    admin_registration_code,
    announcements,
    applications,
    auth,
    bus_routes,
    device_tokens,
    discipline,
    dorm_life,
    events,
    front_desk,
    guidance,
    incidents,
    lost_found,
    meals,
    misc_requests,
    notifications,
    outings,
    rollcall,
    songs,
    student_profile,
    student_promote,
    study,
    study_online,
    teachers,
    ws,
)

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("tomoshibi.startup")


def _warn_if_db_schema_outdated() -> None:
    """开发数据库 schema 落后自检（只读 / 只打日志 / 绝不阻断启动）。

    dev 用 create_all() 建表，它只补缺失的表、不会给已存在的旧表加新列。
    切分支或拉新代码后若别人写了新 Alembic 迁移、而本地库没 `alembic upgrade head`，
    任何查到该表的接口都会 500（2026-06-13 teachers.permission_group 真事故）。
    本函数比对「库当前迁移版本 vs 最新 head」，落后则醒目提示，让人开网页 500 前就看到。
    """
    try:
        from pathlib import Path

        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory

        from .database import engine

        cfg = Config()
        cfg.set_main_option(
            "script_location", str(Path(__file__).resolve().parent.parent / "alembic")
        )
        heads = set(ScriptDirectory.from_config(cfg).get_heads())

        with engine.connect() as conn:
            current = MigrationContext.configure(conn).get_current_revision()

        # current=None：全新 create_all 建的库（schema 本就是最新），不告警
        if current is not None and current not in heads:
            logger.warning(
                "⚠️  [STARTUP] 数据库 schema 落后！当前版本=%s，最新=%s。"
                " 切分支/拉新代码后常见——请在 dev/backend/v1 跑"
                " `.venv/bin/alembic upgrade head` 再用，否则查到相关表的接口会返回 500。",
                current,
                ",".join(sorted(heads)) or "(无)",
            )
    except Exception as exc:  # 自检自身出错绝不能拖垮启动
        logger.debug("[STARTUP] 迁移版本自检跳过（%s）", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # RUN-1: 启动时明显打印当前 APP_ENV，让 ops 一眼确认模式
    logger.info("=" * 60)
    logger.info(
        "[STARTUP] APP_ENV=%s — %s",
        settings.app_env,
        "开发模式（dev）"
        if settings.app_env == "dev"
        else "Staging 模式"
        if settings.app_env == "staging"
        else "生产模式（production）",
    )
    logger.info(
        "[STARTUP] DATABASE_URL prefix: %s", settings.database_url.split("://")[0]
    )
    logger.info("=" * 60)

    # RUN-1: 生产特征（PostgreSQL）但 APP_ENV 不是 production → 大声 WARNING，疑似误配
    _is_postgres = settings.database_url.startswith(
        "postgresql"
    ) or settings.database_url.startswith("postgres")
    if _is_postgres and settings.app_env != "production":
        logger.warning(
            "⚠️  [STARTUP] 疑似生产数据库（PostgreSQL）但 APP_ENV=%s（非 production）！"
            " 这会导致跳过生产校验、使用 create_all() 而非 Alembic 迁移。"
            " 请检查 .env 的 APP_ENV 是否漏设为 production。",
            settings.app_env,
        )

    # dev 环境自动建表；production 仍然必须由 Alembic 管理 schema。
    if settings.app_env == "dev":
        create_all()
        # create_all 不给已存在的旧表补新列 → 切分支后库可能落后于最新迁移，启动时提醒
        _warn_if_db_schema_outdated()

    # WS 广播需要主 event loop 引用 — sync router 在 threadpool 线程靠它把协程提交回主 loop（rollcall-06）
    from .ws_manager import manager as _ws_manager

    _ws_manager.set_loop(asyncio.get_running_loop())
    yield


app = FastAPI(
    title="Tomoshibi Backend v1",
    description=(
        "Tomoshibi (灯火 / ともしび) — 宿舍管理 v1.0 backend. \n"
        "DMSD (Dormitory Management System Digitalization) 项目代号. \n"
        "本 deployment 目前は P0 範囲 (出寮届 + メール + 食堂) のみ実装。"
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Tomoshibi Backend v1",
        "version": __version__,
        "env": settings.app_env,
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(admin_accounts.router)
app.include_router(admin_registration_code.router)
app.include_router(announcements.router)
app.include_router(applications.router)
app.include_router(outings.router)
app.include_router(meals.router)
app.include_router(notifications.router)
app.include_router(device_tokens.router)
app.include_router(study.router)
app.include_router(study_online.router)
app.include_router(dorm_life.router)
app.include_router(rollcall.router)
app.include_router(teachers.router)
app.include_router(discipline.router)
app.include_router(front_desk.router)
app.include_router(events.router)
app.include_router(bus_routes.router)
app.include_router(guidance.router)
app.include_router(incidents.router)
app.include_router(songs.router)
app.include_router(lost_found.router)
app.include_router(misc_requests.router)
app.include_router(student_profile.router)
app.include_router(student_promote.router)
app.include_router(ws.router)

# B5: 老师网页静态文件服务（同 origin 部署）
# TEACHER_WEB_DIR 为空时跳过（dev 下用 vite/standalone 单跑，不需要后端 serve）
# 设了才挂，挂在所有 API 路由之后，确保 /api/v1 和 /healthz 不被 catch-all 吞掉
_teacher_web_dir = os.environ.get("TEACHER_WEB_DIR", "")
if _teacher_web_dir and os.path.isdir(_teacher_web_dir):
    app.mount(
        "/teacher",
        StaticFiles(directory=_teacher_web_dir, html=True),
        name="teacher_web",
    )
    logger.info(
        "[STARTUP] TEACHER_WEB_DIR=%s → /teacher 静态文件服务已挂载", _teacher_web_dir
    )
else:
    if _teacher_web_dir:
        logger.warning(
            "[STARTUP] TEACHER_WEB_DIR=%s 目录不存在，跳过静态文件挂载。",
            _teacher_web_dir,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(settings.app_env == "dev"),
    )
