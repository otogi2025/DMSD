"""点呼 endpoint tests — C-050 (2026-05-21) 新增。

覆盖：
- POST /rollcall/sessions/:id/start — 教师开点呼
- POST /rollcall/sessions/:id/end — 教师结束
- POST /rollcall/sessions/:id/checkins — 学生 NFC / 手动签到
  - 幂等：相同 idempotency_key 不重复事件（A-011）
  - path_hint 校验（A-020）
- GET /rollcall/sessions/:id/board — 出席板
- GET /rollcall/today/sessions — 今日 session 列表

跑：
    cd 03_dev/backend/v1
    pytest tests/test_rollcall.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app import models


@pytest.fixture
def rollcall_session(db_session, seed_data):
    """建一个 running 状态的点呼 session（dorm_unit=1，含 060218 学生）。"""
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    session = models.RollCallSession(
        dorm_unit_set=[1, 2],
        session_type="evening",
        day_type="weekday",
        session_status="running",
        started_at=now,
        scheduled_window_start_at=now - timedelta(minutes=5),
        scheduled_on_time_end_at=now + timedelta(minutes=10),
        scheduled_late_end_at=now + timedelta(minutes=20),
        scheduled_auto_end_at=now + timedelta(minutes=30),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


class TestCheckin:
    """POST /rollcall/sessions/:id/checkins"""

    def test_manual_checkin_creates_event(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """老师手动签到 → 创建 present 事件。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "manual_checkin",
                "path_hint": "manual",
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["student_id"] == student_id
        assert data["base_status"] == "present"
        assert data["status_source"] == "manual_checkin"

    def test_idempotency_same_key_returns_existing(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-011: 同 idempotency_key 第二次 POST 返回原事件（不创建新事件）。"""
        student_id = str(seed_data["student"].id)
        body = {
            "student_id": student_id,
            "idempotency_key": "test-key-001",
            "status_source": "auto_nfc",
            "path_hint": "B",
        }
        res1 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json=body,
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res1.status_code == 201
        event_id_1 = res1.json()["id"]

        # 第二次相同 key
        res2 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json=body,
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res2.status_code in (200, 201)
        assert res2.json()["id"] == event_id_1

    def test_path_hint_a_requires_card_uid(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-020: path_hint=A 必须有 card_uid。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "auto_nfc",
                "path_hint": "A",
                # 故意缺 card_uid
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422
        assert res.json()["detail"]["code"] == "PATH_HINT_MISMATCH"

    def test_path_hint_b_requires_idempotency_key(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-020: path_hint=B 必须有 idempotency_key。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "auto_nfc",
                "path_hint": "B",
                # 故意缺 idempotency_key
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422
        assert res.json()["detail"]["code"] == "PATH_HINT_MISMATCH"

    def test_missing_identifier_returns_422(
        self, client, teacher_token, rollcall_session
    ):
        """既无 card_uid 也无 student_id → 422。"""
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={"status_source": "auto_nfc"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422


class TestSessionLifecycle:
    """start / end session"""

    def test_get_today_sessions_requires_teacher(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/rollcall/today/sessions")
        assert res.status_code == 401

    def test_get_today_sessions_returns_list(self, client, teacher_token):
        """已带教师 token → 返回 list（即使为空）。"""
        res = client.get(
            "/api/v1/rollcall/today/sessions",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)


class TestBoard:
    """GET /rollcall/sessions/:id/board"""

    def test_board_excludes_demo_students(
        self, client, teacher_token, rollcall_session
    ):
        """A-040 verify: is_demo=True 学生不进出席板。"""
        res = client.get(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/board",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "entries" in data
        # 没 demo 学生 — seed_data 创建的 060218 不是 demo
        assert all(e.get("student_no") != "999999" for e in data["entries"])


class TestNoEffectiveWindowShift:
    """A-022 b1 regression — 窗口永远固定 (effective_* 已删).

    防回滚：保证未来没人重新把窗口平移逻辑加回来。
    若任何代码引入 effective_window_start_at / effective_on_time_end_at /
    effective_late_end_at / effective_auto_end_at / effective_group / applied_group
    字段或概念 → 本测试 fail。

    itsuki 2026-05-21 拍板：点呼时间永远按 scheduled_* 算，老师提前按按钮
    只改 started_at 显示，不平移判定窗口。
    """

    def test_rollcall_event_has_no_applied_group_column(self, db_session):
        """ORM model 不应再有 applied_group 字段。"""
        cols = {c.key for c in models.RollCallEvent.__table__.columns}
        assert "applied_group" not in cols, (
            "applied_group 字段已在 A-022 (2026-05-21) 删除 — "
            "请勿再加回 ORM model（窗口平移概念已废弃）"
        )

    def test_rollcall_session_uses_scheduled_only(self, db_session):
        """RollCallSession 只能有 scheduled_*_at 4 字段，不应再有 effective_*_at。"""
        cols = {c.key for c in models.RollCallSession.__table__.columns}
        effective_cols = {
            "effective_window_start_at",
            "effective_on_time_end_at",
            "effective_late_end_at",
            "effective_auto_end_at",
        }
        intersection = cols & effective_cols
        assert not intersection, (
            f"窗口平移字段已在 A-022 (2026-05-21) 删除，禁止恢复: {intersection}"
        )
        # 同时 scheduled_*_at 4 字段必须存在（判定 / 结算 / 倒计时全靠它们）
        scheduled_cols = {
            "scheduled_window_start_at",
            "scheduled_on_time_end_at",
            "scheduled_late_end_at",
            "scheduled_auto_end_at",
        }
        assert scheduled_cols.issubset(cols), (
            f"scheduled_*_at 4 字段是判定基准，必须保留: 缺 {scheduled_cols - cols}"
        )
