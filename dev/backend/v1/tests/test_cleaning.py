"""清扫罚扫（CleaningAssignment）功能测试 — 2026-06-15 罚扫重做。

覆盖:
- POST /cleaning 排罚扫: 成功 / 过去时间 422 / area 自由文本 / 学生 token 拒绝 /
  VIEW 权限拒绝 / 跨寮拒绝
- GET /cleaning/me 学生履历: 只返本人 / 倒序 / 鉴权
- POST /cleaning/{id}/inspect 审核: passed 不扣分 / failed 扣 2.5 / 缺 reason 400 /
  重复 409 / VIEW 权限拒绝
- /discipline/me/summary needs_cleaning 阈值（4 分）
- /discipline/ranking is_cleaning_threshold + cleaning_threshold_count
- 撤销 cleaning_failed 扣分联动退回清扫单状态
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app import models, security

_JST = ZoneInfo("Asia/Tokyo")


def _login_teacher(client, login_id, password="test-password-12345"):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _future_iso(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _past_iso(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _create_cleaning(client, token, student_id, area="廊下 2F", when=None):
    return client.post(
        "/api/v1/cleaning",
        json={
            "student_id": student_id,
            "area": area,
            "scheduled_at": when or _future_iso(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def _set_manual_score(client, token, student_id, target, reason="テスト設定"):
    """B 方案：把学生本月扣分总分设为绝对值 target（不是加增量）。"""
    return client.post(
        "/api/v1/discipline/manual",
        json={"student_id": student_id, "target_points": target, "reason": reason},
        headers={"Authorization": f"Bearer {token}"},
    )


def _add_cleaning(db, *, student_id, area, scheduled_at, status="assigned"):
    row = models.CleaningAssignment(
        student_id=student_id, area=area, scheduled_at=scheduled_at, status=status
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ---------------- POST /cleaning 排罚扫 ----------------


def test_create_cleaning_success(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    res = _create_cleaning(client, teacher_token, sid, area="廊下 2F")
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["area"] == "廊下 2F"
    assert data["status"] == "assigned"
    assert data["student_id"] == sid


def test_create_cleaning_past_time_rejected(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    res = _create_cleaning(client, teacher_token, sid, when=_past_iso())
    assert res.status_code == 422, res.text
    assert res.json()["detail"]["code"] == "SCHEDULED_IN_PAST"


def test_create_cleaning_area_free_text(client, seed_data, teacher_token):
    """area 改自由文本后任意字符串都能存（旧版 7 选 1 枚举 CHECK 会挡）。"""
    sid = str(seed_data["student"].id)
    res = _create_cleaning(client, teacher_token, sid, area="3階の物置スペース")
    assert res.status_code == 201, res.text
    assert res.json()["area"] == "3階の物置スペース"


def test_create_cleaning_student_token_forbidden(client, seed_data, student_token):
    sid = str(seed_data["student"].id)
    res = _create_cleaning(client, student_token, sid)
    assert res.status_code in (401, 403), res.text


def test_create_cleaning_view_only_teacher_forbidden(client, seed_data):
    """国際交流部長 = 申請承認専用组，对扣分管理只有 VIEW → 排罚扫 403。"""
    token = _login_teacher(client, "kokukou_buchou")
    sid = str(seed_data["student"].id)
    res = _create_cleaning(client, token, sid)
    assert res.status_code == 403, res.text


def test_create_cleaning_cross_dorm_now_allowed(client, seed_data, db_session):
    """寮过滤 2026-06-13 已被 itsuki 拍板取消（dorm_units_for_teacher 恒返回 [1,2,4]），
    故女寮監给男寮学生排罚扫现在允许（201）—— 与 manual / front-desk 等端点行为一致。
    保留此测试锁定现状：若将来恢复按寮过滤，这里会变 403、提醒同步更新 cleaning.py。
    """
    pw = security.hash_password("test-password-12345")
    t = models.Teacher(
        login_id="onnaryokan_test",
        name="女寮監テスト",
        email="onnaryokan@test.jp",
        password_hash=pw,
        role="寮監",
        assigned_dorm=4,
    )
    db_session.add(t)
    db_session.commit()
    token = _login_teacher(client, "onnaryokan_test")
    sid = str(seed_data["student"].id)  # dorm_unit=1 男寮
    res = _create_cleaning(client, token, sid)
    assert res.status_code == 201, res.text


# ---------------- GET /cleaning/me 学生履历 ----------------


def test_cleaning_mine_returns_own(client, seed_data, student_token, db_session):
    me = seed_data["student"]
    other = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="19",
        name="他人",
        gender="male",
        room_no="M102",
        dorm_unit=1,
        is_overseas=False,
        email="other@test.jp",
    )
    db_session.add(other)
    db_session.commit()
    _add_cleaning(
        db_session,
        student_id=me.id,
        area="浴室",
        scheduled_at=datetime(2026, 6, 1, 19, 0, tzinfo=_JST),
    )
    _add_cleaning(
        db_session,
        student_id=other.id,
        area="トイレ",
        scheduled_at=datetime(2026, 6, 3, 19, 0, tzinfo=_JST),
    )
    res = client.get(
        "/api/v1/cleaning/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 1
    assert data[0]["student_id"] == str(me.id)


def test_cleaning_mine_ordered_newest_first(
    client, seed_data, student_token, db_session
):
    me = seed_data["student"]
    _add_cleaning(
        db_session,
        student_id=me.id,
        area="浴室",
        scheduled_at=datetime(2026, 6, 1, 19, 0, tzinfo=_JST),
    )
    _add_cleaning(
        db_session,
        student_id=me.id,
        area="廊下",
        scheduled_at=datetime(2026, 6, 9, 19, 0, tzinfo=_JST),
    )
    res = client.get(
        "/api/v1/cleaning/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    areas = [r["area"] for r in res.json()]
    assert areas == ["廊下", "浴室"]  # scheduled_at 倒序


def test_cleaning_mine_requires_auth(client, seed_data):
    res = client.get("/api/v1/cleaning/me")
    assert res.status_code == 401, res.text


def test_cleaning_mine_rejects_teacher(client, seed_data, teacher_token):
    res = client.get(
        "/api/v1/cleaning/me",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code in (401, 403), res.text


# ---------------- POST /cleaning/{id}/inspect 审核 ----------------


def test_inspect_passed_no_demerit(client, seed_data, teacher_token, db_session):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid).json()["id"]
    res = client.post(
        f"/api/v1/cleaning/{cid}/inspect",
        json={"result": "passed"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "passed"
    assert res.json()["demerit_event_id"] is None
    n = (
        db_session.query(models.DemeritEvent)
        .filter_by(source_type="cleaning_failed")
        .count()
    )
    assert n == 0


def test_inspect_failed_adds_demerit(client, seed_data, teacher_token, db_session):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid, area="浴室").json()["id"]
    res = client.post(
        f"/api/v1/cleaning/{cid}/inspect",
        json={"result": "failed", "failure_reason": "床が汚い"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "failed"
    assert body["demerit_event_id"] is not None
    ev = (
        db_session.query(models.DemeritEvent)
        .filter_by(source_type="cleaning_failed")
        .one()
    )
    assert ev.points == 2.5
    assert str(ev.source_event_id) == cid
    assert ev.month == datetime.now(_JST).strftime("%Y-%m")


def test_inspect_failed_missing_reason(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid).json()["id"]
    res = client.post(
        f"/api/v1/cleaning/{cid}/inspect",
        json={"result": "failed"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 400, res.text
    assert res.json()["detail"]["code"] == "MISSING_REASON"


def test_inspect_already_inspected_conflict(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid).json()["id"]
    h = {"Authorization": f"Bearer {teacher_token}"}
    client.post(f"/api/v1/cleaning/{cid}/inspect", json={"result": "passed"}, headers=h)
    res2 = client.post(
        f"/api/v1/cleaning/{cid}/inspect", json={"result": "passed"}, headers=h
    )
    assert res2.status_code == 409, res2.text
    assert res2.json()["detail"]["code"] == "ALREADY_INSPECTED"


def test_inspect_view_only_forbidden(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid).json()["id"]
    view_token = _login_teacher(client, "kokukou_buchou")
    res = client.post(
        f"/api/v1/cleaning/{cid}/inspect",
        json={"result": "passed"},
        headers={"Authorization": f"Bearer {view_token}"},
    )
    assert res.status_code == 403, res.text


# ---------------- summary needs_cleaning 阈值（4 分）----------------


def test_summary_needs_cleaning_threshold(
    client, seed_data, student_token, teacher_token
):
    sid = str(seed_data["student"].id)
    h_stu = {"Authorization": f"Bearer {student_token}"}

    def summary():
        r = client.get("/api/v1/discipline/me/summary", headers=h_stu)
        assert r.status_code == 200, r.text
        return r.json()

    # 初始 0 分 → 不需要罚扫
    assert summary()["needs_cleaning"] is False
    # 设到 3.5 → 仍 False
    _set_manual_score(client, teacher_token, sid, 3.5)
    s = summary()
    assert s["total_points"] == 3.5
    assert s["needs_cleaning"] is False
    # 设到 4.5 ≥4 → True
    _set_manual_score(client, teacher_token, sid, 4.5)
    assert summary()["needs_cleaning"] is True
    # 设到 8.5 ≥8 → 仍 True（后端纯阈值，分档显示交给前端）
    _set_manual_score(client, teacher_token, sid, 8.5)
    s = summary()
    assert s["total_points"] >= 8
    assert s["needs_cleaning"] is True


# ---------------- ranking is_cleaning_threshold ----------------


def test_ranking_cleaning_threshold(client, seed_data, teacher_token):
    sid = str(seed_data["student"].id)
    _set_manual_score(client, teacher_token, sid, 5.0)  # ≥4 <8
    month = datetime.now(_JST).strftime("%Y-%m")
    res = client.get(
        f"/api/v1/discipline/ranking?month={month}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["cleaning_threshold_count"] >= 1
    me_entry = next(e for e in body["entries"] if e["student_id"] == sid)
    assert me_entry["is_cleaning_threshold"] is True
    assert me_entry["is_curfew_threshold"] is False


# ---------------- 撤销 cleaning_failed 联动退回 ----------------


def test_revoke_cleaning_failed_reverts_assignment(
    client, seed_data, teacher_token, db_session
):
    sid = str(seed_data["student"].id)
    cid = _create_cleaning(client, teacher_token, sid, area="玄関").json()["id"]
    h = {"Authorization": f"Bearer {teacher_token}"}
    # inspect failed → 建 cleaning_failed 扣分
    insp = client.post(
        f"/api/v1/cleaning/{cid}/inspect",
        json={"result": "failed", "failure_reason": "未実施"},
        headers=h,
    )
    assert insp.status_code == 200, insp.text
    event_id = insp.json()["demerit_event_id"]
    assert event_id is not None
    # 撤销那条扣分 → cleaning 单应退回 assigned + demerit_event_id 清空
    rev = client.post(
        f"/api/v1/discipline/{event_id}/revoke",
        json={"revoke_reason": "誤判定のため取消"},
        headers=h,
    )
    assert rev.status_code == 200, rev.text
    db_session.expire_all()
    cleaning = db_session.get(models.CleaningAssignment, uuid.UUID(cid))
    assert cleaning.status == "assigned"
    assert cleaning.demerit_event_id is None
    assert cleaning.failure_reason is None
