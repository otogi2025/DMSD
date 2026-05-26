"""FastAPI app — Tomoshibi Backend v1.0.

启动:
    cd 03_dev/backend/v1
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

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .database import create_all
from .routers import (
    accounts,
    admin_registration_code,
    announcements,
    applications,
    auth,
    cleaning,
    discipline,
    front_desk,
    meals,
    notifications,
    rollcall,
    study,
    teachers,
)

settings = get_settings()
logging.basicConfig(level=settings.log_level)

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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup() -> None:
    # dev 環境のみ自動 create_all。production は Alembic 必須
    if settings.app_env == "dev":
        create_all()


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
app.include_router(admin_registration_code.router)
app.include_router(announcements.router)
app.include_router(applications.router)
app.include_router(meals.router)
app.include_router(notifications.router)
app.include_router(study.router)
app.include_router(rollcall.router)
app.include_router(teachers.router)
app.include_router(discipline.router)
app.include_router(cleaning.router)
app.include_router(front_desk.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(settings.app_env == "dev"),
    )
