"""外出申请 (outings) endpoint tests — 2026-06-04 单一老师确认功能。

覆盖：
- POST /outings — 学生提出（今天 OK / 过去日期 422 / 出租车预约回显）
- GET /outings/mine — 学生看自己的
- GET /outings/pending-for-me — 老师看待确认（R4 寮过滤）
- GET /outings/:id — 权限校验（学生本人 / 老师）
- PATCH /outings/:id/confirm — 老师确认（确认者从令牌自动记录 + 学生不能确认 +
  别寮老师 403 + 不能重复确认）
- PATCH /outings/:id/withdraw — 学生撤回自己 pending 的

跑：
    cd dev/backend/v1
    pytest tests/test_outings.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app import models, security

# 跟后端一致用东京时区算「今天」，避免 CI / 非 JST 机器近午夜把今天误判成过去（codex 审查提）
_JST = ZoneInfo("Asia/Tokyo")
_FAKE_UUID = "00000000-0000-0000-0000-000000000000"


def _outing_body(date_offset_days: int = 0) -> dict:
    """生成外出 body — 外出日 = 东京今天 + offset。"""
    d = datetime.now(_JST).date() + timedelta(days=date_offset_days)
    return {
        "outing_date": d.isoformat(),
        "destination": "駅前",
        "leave_time": "13:00:00",
        "return_time": "17:00:00",
        "reason": "買い物",
    }


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_outing(client, student_token, **over) -> dict:
    body = _outing_body()
    body.update(over)
    res = client.post("/api/v1/outings", json=body, headers=_auth(student_token))
    assert res.status_code == 201, res.text
    return res.json()["data"]
def _make_dorm4_teacher_token(client, db_session) -> str:
    """建一个女寮（dorm 4）的普通老师并登录，返回令牌 — 用于跨寮越权负例。"""
    t = models.Teacher(
        login_id="ryomu_dorm4",
        name="女寮先生",
        email="d4@test.jp",
        password_hash=security.hash_password("test-password-12345"),
        role="寮務一般教師",
        assigned_dorm=4,
    )
    db_session.add(t)
    db_session.commit()
    login = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryomu_dorm4", "password": "test-password-12345"},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


class TestCreateOuting:
    """POST /outings"""

    def test_create_requires_student(self, client):
        """未带 token → 401。"""
        res = client.post("/api/v1/outings", json=_outing_body())
        assert res.status_code == 401

    def test_create_success_today(self, client, student_token):
        """当天外出 → 201 + pending + 未确认。"""
        data = _create_outing(client, student_token)
        assert data["status"] == "pending"
        assert data["destination"] == "駅前"
        assert data["confirmed_by_teacher_id"] is None
        assert data["confirmed_by_name"] is None

    def test_create_past_date_rejected(self, client, student_token):
        """外出日 = 昨天 → 422。"""
        body = _outing_body(date_offset_days=-1)
        res = client.post("/api/v1/outings", json=body, headers=_auth(student_token))
        assert res.status_code == 422

    def test_create_with_taxi(self, client, student_token):
        """带出租车预约时刻 → 201 + 回显。"""
        data = _create_outing(client, student_token, taxi_reservation_time="12:30:00")
        assert data["taxi_reservation_time"] == "12:30:00"

    def test_create_ignores_client_student_id(self, client, student_token, seed_data):
        """请求体塞别人的 student_id → 被忽略，仍绑定 token 学生（安全：不信任客户端）。"""
        data = _create_outing(client, student_token, student_id=_FAKE_UUID)
        assert data["student_id"] == str(seed_data["student"].id)

    def test_create_return_before_leave_rejected(self, client, student_token):
        """回寮时刻早于外出时刻 → 422。"""
        body = _outing_body()
        body["leave_time"] = "17:00:00"
        body["return_time"] = "13:00:00"
        res = client.post("/api/v1/outings", json=body, headers=_auth(student_token))
        assert res.status_code == 422


class TestListMine:
    """GET /outings/mine"""

    def test_list_mine(self, client, student_token):
        _create_outing(client, student_token)
        res = client.get("/api/v1/outings/mine", headers=_auth(student_token))
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1


class TestPendingForMe:
    """GET /outings/pending-for-me"""

    def test_pending_for_me_lists_pending(self, client, student_token, teacher_token):
        """老师（寮務課長 跨寮）能看到学生的待确认外出。"""
        _create_outing(client, student_token)
        res = client.get("/api/v1/outings/pending-for-me", headers=_auth(teacher_token))
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

    def test_pending_now_includes_other_dorm(self, client, student_token, db_session):
        """别寮（女寮 dorm 4）老师的待确认列表现在也含男寮学生的外出（寮过滤已取消 2026-06-13）。"""
        outing = _create_outing(client, student_token)  # 学生 dorm_unit=1
        token4 = _make_dorm4_teacher_token(client, db_session)
        res = client.get("/api/v1/outings/pending-for-me", headers=_auth(token4))
        assert res.status_code == 200
        assert outing["id"] in [o["id"] for o in res.json()["data"]]


class TestGetDetail:
    """GET /outings/:id"""

    def test_student_sees_own(self, client, student_token):
        outing = _create_outing(client, student_token)
        res = client.get(
            f"/api/v1/outings/{outing['id']}", headers=_auth(student_token)
        )
        assert res.status_code == 200

    def test_teacher_sees(self, client, student_token, teacher_token):
        outing = _create_outing(client, student_token)
        res = client.get(
            f"/api/v1/outings/{outing['id']}", headers=_auth(teacher_token)
        )
        assert res.status_code == 200

    def test_other_dorm_teacher_now_allowed(self, client, student_token, db_session):
        """别寮老师看男寮学生的外出详情 → 现在允许（寮过滤已取消 2026-06-13）。"""
        outing = _create_outing(client, student_token)
        token4 = _make_dorm4_teacher_token(client, db_session)
        res = client.get(f"/api/v1/outings/{outing['id']}", headers=_auth(token4))
        assert res.status_code == 200, res.text


class TestConfirm:
    """PATCH /outings/:id/confirm — 安全核心：确认者从令牌取。"""

    def test_confirm_records_teacher_from_token(
        self, client, student_token, teacher_token, seed_data
    ):
        """老师确认 → approved + 确认者从令牌自动记录（姓名回显），客户端没传 teacher_id。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(teacher_token)
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["status"] == "approved"
        # teacher_token = ryomu_kachou（寮務次郎）
        teacher = seed_data["teachers"]["ryomu_kachou"]
        assert data["confirmed_by_teacher_id"] == str(teacher.id)
        assert data["confirmed_by_name"] == teacher.name
        assert data["confirmed_at"] is not None

    def test_confirm_requires_teacher(self, client, student_token):
        """学生 token 不能确认 → 403。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(student_token)
        )
        assert res.status_code == 403

    def test_confirm_twice_conflict(self, client, student_token, teacher_token):
        """重复确认 → 409。"""
        outing = _create_outing(client, student_token)
        first = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(teacher_token)
        )
        assert first.status_code == 200
        second = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(teacher_token)
        )
        assert second.status_code == 409

    def test_confirm_ignores_client_teacher_id(
        self, client, student_token, teacher_token, seed_data
    ):
        """确认请求体塞别的 teacher_id → 被忽略，记录的仍是 token 老师（安全核心）。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm",
            json={"confirmed_by_teacher_id": _FAKE_UUID},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 200, res.text
        teacher = seed_data["teachers"]["ryomu_kachou"]
        assert res.json()["data"]["confirmed_by_teacher_id"] == str(teacher.id)

    def test_confirm_cross_dorm_now_allowed(self, client, student_token, db_session):
        """别寮（女寮 dorm 4）老师确认男寮（dorm 1）学生的外出 → 现在允许（寮过滤已取消 2026-06-13）。"""
        outing = _create_outing(client, student_token)  # 学生 dorm_unit=1
        token4 = _make_dorm4_teacher_token(client, db_session)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(token4)
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "approved"


class TestWithdraw:
    """PATCH /outings/:id/withdraw"""

    def test_withdraw_own_pending(self, client, student_token):
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 200
        assert res.json()["data"]["status"] == "withdrawn"

    def test_withdraw_after_confirm_conflict(
        self, client, student_token, teacher_token
    ):
        """已确认的不能再撤回 → 409。"""
        outing = _create_outing(client, student_token)
        client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(teacher_token)
        )
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 409
