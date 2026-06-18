"""WebSocket endpoint — 老师端实时事件流。

GET /api/v1/ws/teacher?token=<JWT>
  → frontend client.js openTeacherWS 调用
  → LiveRollCall 收 checkin / override 事件实时刷新座席表
  → ApplicationsPage 收 outstay_new 推送实时刷新 pending 计数

设计:
  - token 走 query param (WebSocket 不能带 Authorization header)
  - 进入 ConnectionManager 后被动等事件
  - frontend disconnect / 心跳超时 → 自动 cleanup
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from .. import models, security
from ..database import SessionLocal
from ..deps import is_teacher_expired
from ..ws_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


@router.websocket("/teacher")
async def teacher_ws(
    websocket: WebSocket,
    token: str = Query(..., description="教师 JWT — query param 形式"),
):
    """老师端 WebSocket — 收 rollcall / outstay 实时事件。"""
    # token 验证 — JWT decode + role 检查
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    role = payload.get("role", "")
    if not role.startswith("teacher:"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # sub 缺失 / 非法 UUID 不能抛未捕获异常导致连接异常中断 —
    # 仿 deps.get_current_teacher 的守卫，畸形 token 统一 WS_1008 优雅关闭
    try:
        teacher_id = UUID(payload.get("sub"))
    except (TypeError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 拉 teacher.assigned_dorm 用于未来按 dorm 过滤推送
    # 用独立 SessionLocal（WebSocket 不走 FastAPI Depends 注入）
    with SessionLocal() as db:
        teacher = db.get(models.Teacher, teacher_id)
        if not teacher or teacher.status != "active":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        # 临时账户过期也拒连（本路径自解 JWT、不走 deps.get_current_teacher）
        if is_teacher_expired(teacher):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        assigned_dorm = teacher.assigned_dorm
        is_demo = teacher.is_demo  # 演示隔离 — 连接带 is_demo，broadcast 按它过滤

    await manager.connect(websocket, teacher_id, assigned_dorm, is_demo)
    try:
        while True:
            # frontend 不主动发消息（被动接收）— 仅处理 ping/pong / 心跳
            # 任何收到的文本当 keepalive 处理
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.warning("WS teacher loop error: %s", e)
        await manager.disconnect(websocket)
