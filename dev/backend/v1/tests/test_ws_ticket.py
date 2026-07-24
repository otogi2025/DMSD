"""C20 老师 WS 短时票据（60秒TTL，无单次消费机制）—— 鉴权路径回归测试。

老师 JWT 不再直接作为 WS 的 query 参数（会原样落进 uvicorn / nginx 访问日志），
改为先用老师 JWT 换 60 秒 TTL 的短时票据、WS 只收票据。票据是无状态 JWT、靠
exp 限窗（不做单次消费、无 jti），故本文件除正向 / 反向鉴权外，还钉死「过期票据被拒」。
本文件锁住：
  - 票据发行需老师 JWT：无令牌 401 / 学生令牌 403
  - WS 收有效票据可连
  - WS 拒绝普通登录 JWT（purpose 缺失）—— 防旧契约令牌直连绕过 purpose 校验
  - WS 缺 ticket 参数（含旧 ?token= 契约）被拒
  - WS 拒绝已过期票据（exp 在过去）—— 钉死 60 秒 TTL 真的过期即失效
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from starlette.websockets import WebSocketDisconnect

from app.config import get_settings


def _ws_ticket(client, token: str) -> str:
    res = client.post(
        "/api/v1/sessions/ws-ticket",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["ticket"]


class TestWSTicket:
    def test_issue_requires_teacher(self, client, student_token, seed_data):
        # 无令牌 → 401
        res = client.post("/api/v1/sessions/ws-ticket")
        assert res.status_code == 401, res.text
        # 学生令牌 → 403（get_current_teacher 只认老师）
        res = client.post(
            "/api/v1/sessions/ws-ticket",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 403, res.text

    def test_teacher_gets_ticket(self, client, teacher_token, seed_data):
        res = client.post(
            "/api/v1/sessions/ws-ticket",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()["data"]
        assert body["ticket"]
        assert body["expires_in"] == 60

    def test_ws_connects_with_ticket(self, client, teacher_token, seed_data):
        ticket = _ws_ticket(client, teacher_token)
        with client.websocket_connect(f"/api/v1/ws/teacher?ticket={ticket}") as ws:
            # 连接成功即达标 —— 发一条 keepalive 不抛异常
            ws.send_text("ping")

    def test_ws_rejects_raw_login_jwt(self, client, teacher_token, seed_data):
        # 直接拿老师登录 JWT 当票据 —— purpose 缺失，必须被拒
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                f"/api/v1/ws/teacher?ticket={teacher_token}"
            ) as ws:
                ws.receive_text()

    def test_ws_rejects_missing_ticket(self, client, seed_data):
        # 旧契约 ?token= —— 缺必填 ticket 参数，握手被拒
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/v1/ws/teacher?token=whatever") as ws:
                ws.receive_text()

    def test_ws_rejects_expired_ticket(self, client, seed_data):
        # 用 jwt_secret 手工签一张 exp 在过去、purpose=teacher_ws 的合法票据 ——
        # 除过期外身份 / purpose 全对，钉死 60 秒 TTL 真的过期即失效（decode_token
        # verify_exp=True 会拒），而不是靠别的校验碰巧兜住。
        teacher = seed_data["teachers"]["ryomu_kachou"]
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expired = jwt.encode(
            {
                "sub": str(teacher.id),
                "role": f"teacher:{teacher.role}",
                "purpose": "teacher_ws",
                "iat": int((now - timedelta(minutes=5)).timestamp()),
                # exp 落在过去 → 已过期
                "exp": int((now - timedelta(minutes=1)).timestamp()),
            },
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/teacher?ticket={expired}") as ws:
                ws.receive_text()
