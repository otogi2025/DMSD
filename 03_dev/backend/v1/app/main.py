"""FastAPI app — Tomoshibi Backend v1.0 (P0 範囲).

启动:
    cd 03_dev/backend/v1
    cp .env.example .env  # 編集 (SENDGRID_API_KEY 等)
    pip install -r requirements.txt
    python -m app.main           # or  uvicorn app.main:app --reload

OpenAPI: http://localhost:8000/docs

P0 範囲 (会话 B 担当, 2026-04-30):
- POST /api/v1/applications              #2 schema + #6 メール
- GET  /api/v1/applications/mine
- GET  /api/v1/applications/{id}         #5 承认状态
- GET  /api/v1/meals/calc                #7 (JSON debug)
- GET  /api/v1/meals/export              #7 (Excel)
- POST /api/v1/notifications/test        SendGrid smoke
- POST /api/v1/sessions/student
- POST /api/v1/sessions/teacher
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .database import create_all
from .routers import applications, auth, meals, notifications

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
app.include_router(applications.router)
app.include_router(meals.router)
app.include_router(notifications.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(settings.app_env == "dev"),
    )
