"""WebSocket endpoint — 老师端实时事件流。

GET /api/v1/ws/teacher?token=<JWT>
  → frontend client.js openTeacherWS 调用
  → LiveRollCall 收 checkin / override 事件实时刷新座席表
  → ApplicationsPage 收 outstay_new 推送实时刷新 pending 计数

设计:
  - token 走 query param (WebSocket 不能带 Authorization header)
  - 进入 ConnectionManager 后被动等事件
  - frontend disconnect / 心跳超时 → 自动 cleanup
  - 同步 SQLAlchemy 一律经 run_in_threadpool 跑，避免阻塞 asyncio 事件循环
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from starlette.concurrency import run_in_threadpool

from .. import models, security
from ..database import SessionLocal
from ..deps import device_enr_matches, is_teacher_expired
from ..ws_manager import device_manager, manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


def _load_teacher_for_ws(teacher_id: UUID) -> tuple[int | None, bool] | None:
    """同步查教师鉴权信息 — Session 仅在本函数（线程池工作线程）内新开。

    返回 (assigned_dorm, is_demo)；教师不存在 / 非 active / 已过期 → None（由 async 侧关连接）。
    """
    with SessionLocal() as db:
        teacher = db.get(models.Teacher, teacher_id)
        if not teacher or teacher.status != "active":
            return None
        # 临时账户过期也拒连（本路径自解 JWT、不走 deps.get_current_teacher）
        if is_teacher_expired(teacher):
            return None
        # 标量拷出后再关 Session，避免 ORM 对象出线程
        return (teacher.assigned_dorm, teacher.is_demo)


def _device_ws_auth_ok(device_id: str, enr: object) -> bool:
    """同步校验点呼机可否连 WS — Session 仅在本函数（线程池工作线程）内新开。

    存在 + active + 未注销 + 令牌世代（enr）匹配 → True；否则 False。
    """
    with SessionLocal() as db:
        device = (
            db.query(models.RollCallDevice)
            .filter(models.RollCallDevice.device_id == device_id)
            .one_or_none()
        )
        if device is None or not device.device_active or device.retired_at is not None:
            return False
        if not device_enr_matches(device, enr):
            return False
        return True


def _touch_device_last_seen(device_id: str, fw_version: str | None) -> None:
    """收到设备心跳 → 更新 last_seen_at（+ fw_version）。独立 session，失败只记日志。

    由 async 侧经 run_in_threadpool 调用 — 本函数本身是同步阻塞 DB，勿在事件循环线程直接跑。
    """
    try:
        with SessionLocal() as db:
            device = (
                db.query(models.RollCallDevice)
                .filter(models.RollCallDevice.device_id == device_id)
                .one_or_none()
            )
            if device is not None:
                device.last_seen_at = datetime.now(timezone.utc)
                if fw_version:
                    device.fw_version = fw_version[:32]
                db.commit()
    except Exception as e:  # noqa: BLE001 — 心跳落库失败不能拖垮 WS 循环
        logger.warning(
            "WS device heartbeat persist failed device=%s err=%s", device_id, e
        )


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
    # 同步 DB 委托线程池，Session 在 _load_teacher_for_ws 内新开（不跨线程）
    loaded = await run_in_threadpool(_load_teacher_for_ws, teacher_id)
    if loaded is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    assigned_dorm, is_demo = (
        loaded  # is_demo = 演示隔离 — 连接带 is_demo，broadcast 按它过滤
    )

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


@router.websocket("/device")
async def device_ws(
    websocket: WebSocket,
    token: str = Query(..., description="点呼机 device JWT — query param 形式"),
):
    """点呼机端 WebSocket（Device_Contract §5）— 收 session_started / session_ended /
    roster_updated / audio_updated；发 heartbeat 更新 last_seen_at。仿老师通道。"""
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if payload.get("role") != "device":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    device_id = payload.get("sub")
    if not device_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 校验设备存在 + active + 未注销 + 令牌世代未失效（自解 JWT、不走 deps.get_current_device，
    # 故须显式调 device_enr_matches —— 漏了它，reset-enroll 作废的旧令牌仍能连上 WS 收学生
    # 名单推送，与契约 §2.2「旧公钥即刻作废」矛盾）
    # 同步 DB 委托线程池，Session 在 _device_ws_auth_ok 内新开（不跨线程）
    if not await run_in_threadpool(_device_ws_auth_ok, device_id, payload.get("enr")):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await device_manager.connect(websocket, device_id)
    try:
        while True:
            raw = await websocket.receive_text()
            # 设备侧唯一主动消息 = heartbeat（Device_Contract §5）；其余当 keepalive 忽略
            try:
                msg = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(msg, dict) and msg.get("type") == "heartbeat":
                data = msg.get("data") or {}
                fw = data.get("fw_version") if isinstance(data, dict) else None
                # 心跳落库最频繁 — 必须线程池化，否则 DB 慢时拖垮整个事件循环
                await run_in_threadpool(_touch_device_last_seen, device_id, fw)
    except WebSocketDisconnect:
        await device_manager.disconnect(websocket)
    except Exception as e:
        logger.warning("WS device loop error: %s", e)
        await device_manager.disconnect(websocket)
