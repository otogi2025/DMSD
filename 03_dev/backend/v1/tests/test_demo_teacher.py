"""演示账号真隔离测试 — 2026-06-07 演示老师 is_demo 功能。

覆盖（teachers.is_demo + demo_scope_for_teacher 隔离）：
- 演示老师（is_demo=True）登录 → 学生列表只看演示学生，看不到真实学生
- 真老师（is_demo=False）登录 → 学生列表只看真实学生，看不到演示学生（行为同改造前）
- 演示老师对真实学生做写操作 → 404（演示老师只碰演示学生）
- 真老师对演示学生做写操作 → 404（行为同改造前：演示学生隐身）
- 演示老师对演示学生做写操作 → 成功（正向通路）

依赖 conftest.py 的 seed_data（真老师 6 + 真学生 1）+ client / teacher_token fixtures。
"""

from __future__ import annotations

import pytest

from app import models, security


@pytest.fixture
def demo_data(db_session, seed_data):
    """在 seed_data 真实数据之上追加：1 演示老师 + 1 演示学生（都 is_demo=True）。"""
    pw = security.hash_password("demo-pass-12345")

    demo_teacher = models.Teacher(
        login_id="demo",
        name="デモ教員",
        email="demo-teacher@test.jp",
        password_hash=pw,
        role="寮務部長",  # 跨寮 → 演示老师能看到所有演示寮的演示学生
        assigned_dorm=None,
        is_demo=True,
    )
    db_session.add(demo_teacher)
    db_session.flush()

    demo_student = models.Student(
        grade_code="98",
        class_code="01",
        seat_no="01",
        name="デモ一郎",
        name_kana="デモイチロウ",
        gender="male",
        category="一般寮生",
        room_no="D101",
        dorm_unit=1,
        is_overseas=False,
        email="demo-s1@test.jp",
        is_demo=True,
    )
    db_session.add(demo_student)
    db_session.flush()
    db_session.add(models.Account(student_id=demo_student.id, password_hash=pw))
    db_session.commit()

    return {"demo_teacher": demo_teacher, "demo_student": demo_student}


@pytest.fixture
def demo_teacher_token(client, demo_data):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "demo", "password": "demo-pass-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_demo_teacher_sees_only_demo_students(
    client, demo_teacher_token, demo_data, seed_data
):
    """演示老师登录 → 学生列表只含演示学生，不含真实学生。"""
    res = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text
    ids = {it["id"] for it in res.json()["items"]}
    assert str(demo_data["demo_student"].id) in ids  # 看到演示学生
    assert str(seed_data["student"].id) not in ids  # 看不到真实学生


def test_real_teacher_sees_only_real_students(
    client, teacher_token, demo_data, seed_data
):
    """真老师登录 → 学生列表只含真实学生，不含演示学生（行为同改造前）。"""
    res = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    ids = {it["id"] for it in res.json()["items"]}
    assert str(seed_data["student"].id) in ids  # 看到真实学生
    assert str(demo_data["demo_student"].id) not in ids  # 看不到演示学生


def test_demo_teacher_cannot_touch_real_student(client, demo_teacher_token, seed_data):
    """演示老师对真实学生做密码重置 → 404（演示老师只能碰演示学生）。"""
    res = client.post(
        f"/api/v1/accounts/{seed_data['student'].id}/password-reset",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_real_teacher_cannot_touch_demo_student(client, teacher_token, demo_data):
    """真老师对演示学生做密码重置 → 404（行为同改造前：演示学生隐身）。"""
    res = client.post(
        f"/api/v1/accounts/{demo_data['demo_student'].id}/password-reset",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_demo_teacher_can_reset_demo_student(client, demo_teacher_token, demo_data):
    """演示老师对演示学生做密码重置 → 成功（正向通路：演示老师能操作演示学生）。"""
    res = client.post(
        f"/api/v1/accounts/{demo_data['demo_student'].id}/password-reset",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert "temporary_password" in res.json()


def test_demo_teacher_cannot_view_real_student_profile(
    client, demo_teacher_token, seed_data
):
    """演示老师 GET 真实学生个人档案聚合 → 404（演示老师只能查演示学生）。"""
    res = client.get(
        f"/api/v1/students/{seed_data['student'].id}/profile",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_real_teacher_cannot_view_demo_student_profile(
    client, teacher_token, demo_data
):
    """真老师 GET 演示学生个人档案聚合 → 404（演示学生对真老师隐身）。"""
    res = client.get(
        f"/api/v1/students/{demo_data['demo_student'].id}/profile",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 404, res.text
