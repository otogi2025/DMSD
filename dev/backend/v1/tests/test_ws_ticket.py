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


class TestWSTicketCarriesSelectedDorm:
    """当班寮必须一路传到 WS 广播过滤（2026-08-01 上线前复审 F1）。

    老师登录时选今晚负责哪个寮，这个选择进登录令牌、REST 接口按它算可见范围。
    此前换 WS 票据时该选择被丢弃、WS 改读老师档案里的固定 assigned_dorm ——
    档案男寮、今晚代班女寮的老师，点呼大屏显示已连接却收不到一条女寮签到，
    反而收到男寮的。本组钉死三段链路：票据带上它 / 建连按它算 / 未选时看全部。
    """

    def _login(self, client, login_id: str, selected_dorm: int | None) -> str:
        body: dict = {"login_id": login_id, "password": "test-password-12345"}
        if selected_dorm is not None:
            body["selected_dorm"] = selected_dorm
        res = client.post("/api/v1/sessions/teacher", json=body)
        assert res.status_code == 200, res.text
        return res.json()["data"]["access_token"]

    def test_ticket_carries_selected_dorm(self, client, seed_data):
        """登录选女寮 → 换来的 WS 票据里必须带 selected_dorm=4（不带 = F1 的根因）。"""
        ticket = _ws_ticket(client, self._login(client, "tannin", 4))
        settings = get_settings()
        payload = jwt.decode(
            ticket, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        assert payload["purpose"] == "teacher_ws"
        assert payload["selected_dorm"] == 4

    def test_ticket_omits_dorm_when_not_selected(self, client, seed_data):
        """未选寮登录 → 票据里不放这个键（回落到看全部，向后兼容旧客户端）。"""
        ticket = _ws_ticket(client, self._login(client, "tannin", None))
        settings = get_settings()
        payload = jwt.decode(
            ticket, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        assert "selected_dorm" not in payload

    def test_load_teacher_prefers_selected_over_profile(self, seed_data):
        """核心逻辑单测：广播过滤寮取当班寮，不取档案里的 assigned_dorm。"""
        from app.routers.ws import _load_teacher_for_ws

        teacher = seed_data["teachers"]["tannin"]
        assert teacher.assigned_dorm == 1, "前提：这个老师档案上是男寮"

        # 代班女寮 → 按女寮过滤（不是档案里的 1）
        assert _load_teacher_for_ws(teacher.id, 4)[0] == 4
        # 选男寮 → 男寮（ws_manager 侧会把 1 展开成 1+2 两栋）
        assert _load_teacher_for_ws(teacher.id, 1)[0] == 1
        assert _load_teacher_for_ws(teacher.id, 2)[0] == 1
        # 未选 → None = 不限制，看全部（向后兼容）
        assert _load_teacher_for_ws(teacher.id, None)[0] is None

    def test_ws_connection_registers_selected_dorm(self, client, seed_data):
        """端到端：档案男寮的老师选女寮代班，建立的连接按女寮注册。"""
        from app.ws_manager import manager

        teacher = seed_data["teachers"]["tannin"]
        ticket = _ws_ticket(client, self._login(client, "tannin", 4))
        with client.websocket_connect(f"/api/v1/ws/teacher?ticket={ticket}") as ws:
            ws.send_text("ping")
            mine = [c for c in manager._conns if c.teacher_id == teacher.id]
            assert len(mine) == 1, "连接应已注册"
            assert mine[0].assigned_dorm == 4, (
                "连接按当班寮(4)注册，不是档案里的固定寮(1)"
            )
