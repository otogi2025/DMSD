"""
WebSocket 连接管理器

老师 Web 连到 /ws/teacher 订阅实时事件（签到 / 新申请 / 审批结果）。
多老师同时在线：broadcast 给所有连接。
"""
from typing import List
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: dict):
        """给所有连接的老师 Web 推消息。

        事件类型（前端据此 switch）：
        - "checkin" — 学生签到
        - "outstay_new" — 新外宿申请
        - "outstay_updated" — 外宿审批结果
        - "return_home_new" — 新归国申请
        - "return_home_updated" — 归国审批结果
        - "roll_call_started" / "roll_call_ended"
        """
        message = json.dumps({"type": event_type, "data": data}, default=str)
        # 用 list() 复制一份，避免遍历中断开连接时 list 变
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                # 连接已断，从列表移除
                self.disconnect(connection)


# 全局单例
manager = ConnectionManager()
