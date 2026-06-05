"""GET /api/v1/front-desk/mine 学生端包裹查询测试。

front_desk.py 此前无测试文件 — 本文件随 /mine 学生端接口新建
（IX-009 包裹通知真数据源：iOS 通知中心「荷物」标签从此有真数据）。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import models


def _make_item(
    db,
    *,
    student_id,
    teacher_id,
    description,
    kind="delivery",
    status="pending",
    created_at=None,
):
    """测试用 — 建一条前台条目（默认是一个待取的宅配包裹）。"""
    item = models.FrontDeskItem(
        kind=kind,
        student_id=student_id,
        description=description,
        status=status,
        created_by_teacher_id=teacher_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    if created_at is not None:
        item.created_at = created_at
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_mine_returns_own_deliveries(client, seed_data, student_token, db_session):
    student = seed_data["student"]
    teacher = seed_data["teachers"]["kanri"]
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="Amazon の荷物",
    )
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="郵便局の不在票",
    )

    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 2
    assert {d["description"] for d in data} == {"Amazon の荷物", "郵便局の不在票"}
    assert all(d["kind"] == "delivery" for d in data)
    assert all(d["student_id"] == str(student.id) for d in data)


def test_mine_excludes_lost_and_found(client, seed_data, student_token, db_session):
    """失物招领（lost_and_found）那条 student_id 是捡到人、不算「我的包裹」→ 不返回。"""
    student = seed_data["student"]
    teacher = seed_data["teachers"]["kanri"]
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="拾った傘",
        kind="lost_and_found",
    )

    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json() == []


def test_mine_excludes_other_students(client, seed_data, student_token, db_session):
    """别人的包裹绝不出现在我的 /mine 里。"""
    student = seed_data["student"]
    teacher = seed_data["teachers"]["kanri"]
    other = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="19",
        name="タナカ タロウ",
        gender="male",
        room_no="M102",
        dorm_unit=1,
        is_overseas=False,
        email="other@test.jp",
    )
    db_session.add(other)
    db_session.flush()
    _make_item(
        db_session, student_id=other.id, teacher_id=teacher.id, description="他人の荷物"
    )
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="自分の荷物",
    )

    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 1
    assert data[0]["description"] == "自分の荷物"


def test_mine_includes_picked_up(client, seed_data, student_token, db_session):
    """已取走的包裹也返回（历史可见），未读判定交给 iOS（picked_up 视为已读）。"""
    student = seed_data["student"]
    teacher = seed_data["teachers"]["kanri"]
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="受取済み",
        status="picked_up",
    )

    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 1
    assert data[0]["status"] == "picked_up"


def test_mine_ordered_newest_first(client, seed_data, student_token, db_session):
    student = seed_data["student"]
    teacher = seed_data["teachers"]["kanri"]
    old = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)
    new = datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc)
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="古い",
        created_at=old,
    )
    _make_item(
        db_session,
        student_id=student.id,
        teacher_id=teacher.id,
        description="新しい",
        created_at=new,
    )

    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert [d["description"] for d in res.json()] == ["新しい", "古い"]


def test_mine_requires_auth(client):
    """无 token → 401。"""
    res = client.get("/api/v1/front-desk/mine")
    assert res.status_code == 401, res.text


def test_mine_rejects_teacher_token(client, seed_data, teacher_token):
    """老师 token 调学生端接口 → 403。"""
    res = client.get(
        "/api/v1/front-desk/mine",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 403, res.text
