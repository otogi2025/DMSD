"""Demo 账号 / 审核员永久注册码测试 — 5-08 修复。

覆盖:
- is_reviewer=True 注册码不被普通 /refresh 作废（spec §7.16 例外条款）
- is_reviewer=True 注册码可正常注册学生（POST /accounts）
- is_demo=True 学生不出现在老师点呼板 (rollcall.session_board)
- _generate_code 范围排除 999999
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import models, security


# ---------- is_reviewer 注册码行为 ----------


def test_reviewer_code_not_invalidated_by_refresh(
    client, db_session, seed_data, teacher_token
):
    """is_reviewer=True 永久码 — 老师按 refresh 生成新普通码后仍然 active。"""
    admin = seed_data["teachers"]["ryomu_kachou"]
    db_session.add(
        models.StudentRegistrationCode(
            code="999999",
            created_by=admin.id,
            expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
            is_reviewer=True,
        )
    )
    db_session.commit()

    # 老师生成新普通码
    res = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 201

    # reviewer 码应仍 active（invalidated_at=NULL）
    db_session.expire_all()
    reviewer_code = (
        db_session.query(models.StudentRegistrationCode).filter_by(code="999999").one()
    )
    assert reviewer_code.invalidated_at is None, "is_reviewer 码不应被普通 refresh 作废"
    assert reviewer_code.is_reviewer is True


def test_reviewer_code_can_register_account(client, db_session, seed_data):
    """is_reviewer=True 永久码 — 学生可正常用它跑 POST /accounts 注册。"""
    admin = seed_data["teachers"]["ryomu_kachou"]
    db_session.add(
        models.StudentRegistrationCode(
            code="999999",
            created_by=admin.id,
            expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
            is_reviewer=True,
        )
    )
    db_session.commit()

    res = client.post(
        "/api/v1/accounts",
        json={
            "grade_code": "04",
            "class_code": "01",
            "seat_no": "05",
            "name": "テスト 学生",
            "name_kana": "テスト ガクセイ",
            "gender": "male",
            "category": "一般寮生",
            "room_no": "M105",
            "dorm_unit": 1,
            "is_overseas": False,
            "password": "TestPassword123!",
            "registration_code": "999999",
        },
    )
    assert res.status_code == 201, res.text
    assert "access_token" in res.json()["data"]


def test_reviewer_code_not_visible_in_current(
    client, db_session, seed_data, teacher_token
):
    """is_reviewer=True 码 — 老师 GET /current 看不到（防泄漏：老师面板不显示永久码）。"""
    admin = seed_data["teachers"]["ryomu_kachou"]
    db_session.add(
        models.StudentRegistrationCode(
            code="999999",
            created_by=admin.id,
            expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
            is_reviewer=True,
        )
    )
    db_session.commit()

    res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"] is None, "is_reviewer 码不应出现在老师 current 面板"


# ---------- is_demo 学生过滤 ----------


def test_demo_student_excluded_from_session_board(
    client,
    db_session,
    seed_data,
    teacher_token,
):
    """is_demo=True 学生不应出现在老师点呼板（rollcall session_board）。"""
    pw = security.hash_password("test-password-12345")

    # 加 1 个 demo 学生（is_demo=True，跟 seed_data 学生同 dorm_unit=1）
    demo_student = models.Student(
        grade_code="99",
        class_code="99",
        seat_no="99",
        name="App Reviewer",
        gender="male",
        room_no="M999",
        dorm_unit=1,
        is_overseas=False,
        is_demo=True,
    )
    db_session.add(demo_student)
    db_session.flush()
    db_session.add(models.Account(student_id=demo_student.id, password_hash=pw))

    # 创建一个点呼 session（覆盖 dorm 1）— 老师可以查看
    now = datetime.now(timezone.utc)
    session = models.RollCallSession(
        dorm_unit_set=[1, 2],
        session_type="evening",
        schedule_mode="split",
        day_type="weekday",
        session_status="running",
        scheduled_window_start_at=now,
        scheduled_on_time_end_at=now + timedelta(minutes=10),
        scheduled_late_end_at=now + timedelta(minutes=20),
        scheduled_auto_end_at=now + timedelta(minutes=30),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    res = client.get(
        f"/api/v1/rollcall/sessions/{session.id}/board",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text

    entries = res.json()["data"]["entries"]
    student_ids = [e["student_id"] for e in entries]
    # demo 学生不应出现
    assert str(demo_student.id) not in student_ids, "is_demo=True 学生不应出现在点呼板"
    # seed_data 的 normal 学生 060218 应该在（确认过滤是 demo-only 不是把所有人都过滤掉）
    seed_student = seed_data["student"]
    assert str(seed_student.id) in student_ids, (
        "is_demo=False 的正常学生应该出现在点呼板"
    )


# ---------- _generate_code 范围 ----------


def test_generate_code_never_returns_999999():
    """_generate_code 范围排除 999999（reviewer 码 reserved）。
    跑 1000 次抽样验证；理论上 secrets.randbelow(999999)（0..999998）永不返回 999999。
    """
    from app.routers.admin_registration_code import _generate_code

    codes = {_generate_code() for _ in range(1000)}
    assert "999999" not in codes
    # 每个 code 都是 6 位
    assert all(len(c) == 6 for c in codes)
    assert all(c.isdigit() for c in codes)
