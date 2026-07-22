"""外出申请 (outings) endpoint tests — 2026-06-04 单一老师确认功能
+ 2026-07-22 事后确认制改造。

覆盖：
- POST /outings — 学生提出（今天 OK / 过去日期 422 / 出租车预约回显）
  + 外出禁止闸（当月扣分 ≥8 分不能提交 / 已撤销和上月的分不算）
- GET /outings/mine — 学生看自己的
- GET /outings/pending-for-me — 老师看待确认（R4 寮过滤）
- GET /outings/for-me — 老师看全状态列表（三态筛选 + R4 寮过滤）
- GET /outings/:id — 权限校验（学生本人 / 老师）
- PATCH /outings/:id/confirm — 老师确认（确认者从令牌自动记录 + 学生不能确认 +
  别寮老师 403 + 不能重复确认）
- PATCH /outings/:id/reject — 老师却下（理由可选 + 学生不能却下 + 别寮 403 +
  非 pending 409 + 给学生发通知）
- PATCH /outings/:id/withdraw — 学生撤回自己 pending 的

跑：
    cd dev/backend/v1
    pytest tests/test_outings.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
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


def _make_dorm4_teacher_token(
    client, db_session, *, selected_dorm: int | None = None
) -> str:
    """建一个女寮（dorm 4）的普通老师并登录，返回令牌 — 用于跨寮越权负例。

    selected_dorm：登录时选寮（写进 JWT）。传 4 = 只看女寮，才能测出跨男寮 403 / 列表过滤。
    不传 = 兼容路径 dorm_units 全集，跨寮校验不触发（测不出 enforce）。
    """
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
    body: dict = {"login_id": "ryomu_dorm4", "password": "test-password-12345"}
    if selected_dorm is not None:
        body["selected_dorm"] = selected_dorm
    login = client.post("/api/v1/sessions/teacher", json=body)
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

    def test_pending_excludes_other_dorm_when_selected(
        self, client, student_token, db_session
    ):
        """选女寮(selected_dorm=4)的老师待确认列表不含男寮学生外出（列表端过滤，非 403）。

        对齐 6-18 选寮过滤：未选寮=兼容看全部；选了女寮后 dorm_units=[4]，男寮外出被滤掉。
        """
        outing = _create_outing(client, student_token)  # 学生 dorm_unit=1
        token4 = _make_dorm4_teacher_token(client, db_session, selected_dorm=4)
        res = client.get("/api/v1/outings/pending-for-me", headers=_auth(token4))
        assert res.status_code == 200
        assert outing["id"] not in [o["id"] for o in res.json()["data"]]


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

    def test_other_dorm_teacher_forbidden_when_selected(
        self, client, student_token, db_session
    ):
        """选女寮的老师看男寮学生的外出详情 → 403。"""
        outing = _create_outing(client, student_token)
        token4 = _make_dorm4_teacher_token(client, db_session, selected_dorm=4)
        res = client.get(f"/api/v1/outings/{outing['id']}", headers=_auth(token4))
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN"


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

    def test_confirm_cross_dorm_forbidden_when_selected(
        self, client, student_token, db_session
    ):
        """选女寮的老师确认男寮（dorm 1）学生的外出 → 403。"""
        outing = _create_outing(client, student_token)  # 学生 dorm_unit=1
        token4 = _make_dorm4_teacher_token(client, db_session, selected_dorm=4)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(token4)
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN"


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


# =================================================================
# 2026-07-22 事后确认制改造（itsuki 拍板）
# =================================================================


def _give_points(db_session, student, points: float, *, month_offset: int = 0) -> None:
    """给学生记一条扣分。month_offset=-1 → 记到上个月（测跨月归零）。"""
    now = datetime.now(_JST)
    month = now.strftime("%Y-%m")
    if month_offset:
        y, m = now.year, now.month + month_offset
        while m < 1:
            y, m = y - 1, m + 12
        month = f"{y:04d}-{m:02d}"
    db_session.add(
        models.DemeritEvent(
            student_id=student.id,
            source_type="manual",
            points=points,
            reason="テスト",
            month=month,
        )
    )
    db_session.commit()


class TestOutingBanned:
    """POST /outings 的外出禁止闸 — 当月扣分 ≥8 分（CURFEW_THRESHOLD）禁止提交。"""

    def test_over_threshold_blocked(self, client, student_token, seed_data, db_session):
        """当月 8 分 → 422 OUTING_BANNED（边界值本身就要被挡）。"""
        _give_points(db_session, seed_data["student"], 8.0)
        res = client.post(
            "/api/v1/outings", json=_outing_body(), headers=_auth(student_token)
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "OUTING_BANNED"

    def test_under_threshold_allowed(
        self, client, student_token, seed_data, db_session
    ):
        """当月 7.5 分 → 仍可提交（阈值以下不挡）。"""
        _give_points(db_session, seed_data["student"], 7.5)
        res = client.post(
            "/api/v1/outings", json=_outing_body(), headers=_auth(student_token)
        )
        assert res.status_code == 201, res.text

    def test_revoked_points_not_counted(
        self, client, student_token, seed_data, db_session
    ):
        """已撤销的扣分不计入 → 撤销后能重新提交（口径与排行榜一致）。"""
        _give_points(db_session, seed_data["student"], 10.0)
        blocked = client.post(
            "/api/v1/outings", json=_outing_body(), headers=_auth(student_token)
        )
        assert blocked.status_code == 422
        event = db_session.query(models.DemeritEvent).first()
        event.revoked_at = datetime.now(timezone.utc)
        db_session.commit()
        res = client.post(
            "/api/v1/outings", json=_outing_body(), headers=_auth(student_token)
        )
        assert res.status_code == 201, res.text

    def test_last_month_points_not_counted(
        self, client, student_token, seed_data, db_session
    ):
        """上个月的扣分不计入（扣分按月归零，不是历史累计）。"""
        _give_points(db_session, seed_data["student"], 10.0, month_offset=-1)
        res = client.post(
            "/api/v1/outings", json=_outing_body(), headers=_auth(student_token)
        )
        assert res.status_code == 201, res.text


class TestReject:
    """PATCH /outings/:id/reject — 老师却下（事后确认制：只发通知 + 留记录）。"""

    def test_reject_records_teacher_and_reason(
        self, client, student_token, teacher_token, seed_data
    ):
        """却下 → rejected + 处理老师从令牌记录 + 理由回显。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject",
            json={"reason": "行き先が不明確です"},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["status"] == "rejected"
        assert data["reject_reason"] == "行き先が不明確です"
        teacher = seed_data["teachers"]["ryomu_kachou"]
        assert data["confirmed_by_teacher_id"] == str(teacher.id)
        assert data["confirmed_at"] is not None

    def test_reject_without_reason(self, client, student_token, teacher_token):
        """理由不填也能却下（itsuki 拍板：不强制老师写理由）— 连请求体都省略。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(teacher_token)
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "rejected"
        assert res.json()["data"]["reject_reason"] is None

    def test_reject_requires_teacher(self, client, student_token):
        """学生 token 不能却下 → 403。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(student_token)
        )
        assert res.status_code == 403

    def test_reject_after_confirm_conflict(self, client, student_token, teacher_token):
        """已确认的不能再却下 → 409（原子条件更新防两老师并发）。"""
        outing = _create_outing(client, student_token)
        client.patch(
            f"/api/v1/outings/{outing['id']}/confirm", headers=_auth(teacher_token)
        )
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(teacher_token)
        )
        assert res.status_code == 409

    def test_reject_twice_conflict(self, client, student_token, teacher_token):
        """重复却下 → 409。"""
        outing = _create_outing(client, student_token)
        first = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(teacher_token)
        )
        assert first.status_code == 200
        second = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(teacher_token)
        )
        assert second.status_code == 409

    def test_reject_cross_dorm_forbidden(self, client, student_token, db_session):
        """选女寮的老师却下男寮学生的外出 → 403（R4 寮边界与 confirm 同级）。"""
        outing = _create_outing(client, student_token)
        token4 = _make_dorm4_teacher_token(client, db_session, selected_dorm=4)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(token4)
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN"

    def test_reject_writes_notification(
        self, client, student_token, teacher_token, db_session
    ):
        """却下后给学生写通知记录（邮件那一路 — 学生端没有 app 内通知表）。"""
        outing = _create_outing(client, student_token)
        res = client.patch(
            f"/api/v1/outings/{outing['id']}/reject",
            json={"reason": "テスト"},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 200, res.text
        logs = (
            db_session.query(models.NotificationLog)
            .filter(models.NotificationLog.template_key == "outing_rejected")
            .all()
        )
        assert len(logs) == 1
        assert logs[0].channel == "email"


class TestForMe:
    """GET /outings/for-me — 老师端全状态列表（老师网页三态筛选用）。"""

    def test_for_me_includes_processed(self, client, student_token, teacher_token):
        """不传 status → 含已处理的（pending-for-me 看不到这些）。"""
        outing = _create_outing(client, student_token)
        client.patch(
            f"/api/v1/outings/{outing['id']}/reject", headers=_auth(teacher_token)
        )
        pending = client.get(
            "/api/v1/outings/pending-for-me", headers=_auth(teacher_token)
        )
        assert all(o["id"] != outing["id"] for o in pending.json()["data"])
        res = client.get("/api/v1/outings/for-me", headers=_auth(teacher_token))
        assert res.status_code == 200, res.text
        assert any(o["id"] == outing["id"] for o in res.json()["data"])

    def test_for_me_status_filter(self, client, student_token, teacher_token):
        """status=rejected → 只出却下的那条。"""
        kept = _create_outing(client, student_token)
        rejected = _create_outing(client, student_token)
        client.patch(
            f"/api/v1/outings/{rejected['id']}/reject", headers=_auth(teacher_token)
        )
        res = client.get(
            "/api/v1/outings/for-me?status=rejected", headers=_auth(teacher_token)
        )
        assert res.status_code == 200, res.text
        ids = [o["id"] for o in res.json()["data"]]
        assert rejected["id"] in ids
        assert kept["id"] not in ids

    def test_for_me_cross_dorm_filtered(self, client, student_token, db_session):
        """选女寮的老师看不到男寮学生的外出（R4 寮边界过滤）。"""
        outing = _create_outing(client, student_token)
        token4 = _make_dorm4_teacher_token(client, db_session, selected_dorm=4)
        res = client.get("/api/v1/outings/for-me", headers=_auth(token4))
        assert res.status_code == 200, res.text
        assert all(o["id"] != outing["id"] for o in res.json()["data"])
