"""WebSocket ConnectionManager — 全局单例。

老师端 (`/api/v1/ws/teacher`) 连过来后 register 到 manager；
rollcall / applications 等业务 router 在事件发生时调 broadcast() 推给所有活跃老师连接。

事件 schema (frontend client.js LiveRollCall 期待):
  { type: "checkin",     student_id, status, checked_at, name?, room_no? }
  { type: "outstay_new", application_id, student_id, kind, leave_date }
  { type: "override",    student_id, status, override_reason }

设计:
  - in-memory list （单进程 v1.0 足够；多进程后期换 Redis pub/sub）
  - 每个连接带 teacher_id（供未来按 dorm 过滤 — 当前广播全部）
  - broadcast 失败 (连接断了) 自动从 list 移除，不抛错
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class _TeacherConn:
    teacher_id: UUID
    websocket: WebSocket
    assigned_dorm: int | None  # 跨寮 4 类 = None / 男寮 = 1 / 女寮 = 4


class TeacherConnectionManager:
    """老师端 WebSocket 连接管理 — 单进程内存版。"""

    def __init__(self) -> None:
        self._conns: list[_TeacherConn] = []
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        teacher_id: UUID,
        assigned_dorm: int | None,
    ) -> None:
        await websocket.accept()
        async with self._lock:
            self._conns.append(
                _TeacherConn(
                    teacher_id=teacher_id,
                    websocket=websocket,
                    assigned_dorm=assigned_dorm,
                )
            )
        logger.info(
            "WS teacher connected teacher_id=%s dorm=%s active=%d",
            teacher_id,
            assigned_dorm,
            len(self._conns),
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._conns = [c for c in self._conns if c.websocket is not websocket]
        logger.info("WS teacher disconnected active=%d", len(self._conns))

    async def broadcast(self, event: dict[str, Any]) -> None:
        """推给所有活跃老师连接。失败连接自动剔除。"""
        async with self._lock:
            targets = list(self._conns)
        dead: list[_TeacherConn] = []
        for c in targets:
            try:
                await c.websocket.send_json(event)
            except Exception as e:
                logger.warning("WS send failed teacher=%s err=%s", c.teacher_id, e)
                dead.append(c)
        if dead:
            async with self._lock:
                self._conns = [c for c in self._conns if c not in dead]

    def broadcast_sync(self, event: dict[str, Any]) -> None:
        """同步 router (def, 不是 async def) 触发广播用。

        把事件丢到 event loop 里 schedule，不阻塞 router 返回。
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.broadcast(event))
            else:
                loop.run_until_complete(self.broadcast(event))
        except RuntimeError:
            # 没 event loop（测试 / 命令行）— 静默跳过
            logger.debug("WS broadcast_sync skipped: no running loop")


# 全局单例
manager = TeacherConnectionManager()
