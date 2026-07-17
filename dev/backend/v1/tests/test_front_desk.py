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
    data = res.json()["data"]
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
    assert res.json()["data"] == []


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
    data = res.json()["data"]
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
    data = res.json()["data"]
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
    assert [d["description"] for d in res.json()["data"]] == ["新しい", "古い"]


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


def _login_teacher(client, login_id):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def test_list_now_shows_all_dorms(client, seed_data, db_session):
    """GET /front-desk 寮过滤已取消 2026-06-13：所有老师看全部寮的条目。
    - 男寮 scope 老师（tannin assigned_dorm=1）现在也能看到女寮学生的条目
    - 跨寮老师（寮務課長 assigned_dorm=None）看全部（不变）
    """
    male_student = seed_data["student"]  # dorm_unit=1（男寮）
    teacher = seed_data["teachers"]["ryomu_kachou"]  # 登记人

    # 女寮学生（dorm_unit=4 / female）
    female = models.Student(
        grade_code="06",
        class_code="03",
        seat_no="01",
        name="女子 学生",
        gender="female",
        room_no="W101",
        dorm_unit=4,
        is_overseas=False,
        email="female@test.jp",
    )
    db_session.add(female)
    db_session.flush()

    _make_item(
        db_session,
        student_id=male_student.id,
        teacher_id=teacher.id,
        description="男寮の荷物",
    )
    _make_item(
        db_session,
        student_id=female.id,
        teacher_id=teacher.id,
        description="女寮の荷物",
    )
    # 无关联学生的无主失物 → 所有老师可见
    _make_item(
        db_session,
        student_id=None,
        teacher_id=teacher.id,
        description="無主の忘れ物",
        kind="lost_and_found",
    )

    # 男寮 scope 老师：寮过滤取消后看全部（男寮 + 女寮 + 无主条目）
    male_token = _login_teacher(client, "tannin")
    res = client.get(
        "/api/v1/front-desk",
        headers={"Authorization": f"Bearer {male_token}"},
    )
    assert res.status_code == 200, res.text
    descs = {i["description"] for i in res.json()["data"]}
    assert "男寮の荷物" in descs
    assert "無主の忘れ物" in descs
    assert "女寮の荷物" in descs  # 寮过滤取消后女寮条目也可见

    # 跨寮老师：全部可见
    cross_token = _login_teacher(client, "ryomu_kachou")
    res2 = client.get(
        "/api/v1/front-desk",
        headers={"Authorization": f"Bearer {cross_token}"},
    )
    assert res2.status_code == 200, res2.text
    descs2 = {i["description"] for i in res2.json()["data"]}
    assert {"男寮の荷物", "女寮の荷物", "無主の忘れ物"} <= descs2


def test_search_recipients_ryokan_can_access_all_dorms(client, seed_data, db_session):
    """GET /front-desk/students 挑收件学生：
    - 寮監能访问（核心修复：账号管理的 /students 角色集不含寮監，会 403）
    - 寮过滤已取消 2026-06-13：男寮監现在也能搜到女寮学生。
    """
    from app import security

    # 男寮 寮監（assigned_dorm=1 → 管 dorm_unit 1,2）
    ryokan = models.Teacher(
        login_id="ryokan_m",
        name="男寮監",
        email="rm@test.jp",
        password_hash=security.hash_password("test-password-12345"),
        role="寮監",
        assigned_dorm=1,
    )
    db_session.add(ryokan)
    # 女寮学生（dorm_unit=4）
    female = models.Student(
        grade_code="06",
        class_code="03",
        seat_no="02",
        name="女子 受取人",
        gender="female",
        room_no="W102",
        dorm_unit=4,
        is_overseas=False,
        email="female2@test.jp",
    )
    db_session.add(female)
    db_session.commit()

    token = _login_teacher(client, "ryokan_m")
    res = client.get(
        "/api/v1/front-desk/students",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text  # 核心：寮監不再 403
    names = {s["name"] for s in res.json()["data"]}
    assert seed_data["student"].name in names  # 男寮学生可见
    assert "女子 受取人" in names  # 寮过滤取消后女寮学生也可见


def test_search_recipients_non_admin_can_view(client, seed_data):
    """寮務一般教師（tannin）→ 可查看前台挑学生接口（200）。

    权限分级改造（teacher_permission_v1.md §5 第 4 行「前台·宅配」5 组全部至少给查看 V）后，
    旧的「寮務一般教師不在前台角色集 → 403」行为被废弃。tannin 默认映射「一般宿管」，对前台有 M（含 V）。
    """
    token = _login_teacher(client, "tannin")
    res = client.get(
        "/api/v1/front-desk/students",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text


# ---------------------------------------------------------------
# 件数 item_count + description 按 kind 校验（2026-06-14 选学生统一 + 快递改造）
# ---------------------------------------------------------------
def _create_url():
    return "/api/v1/front-desk"


def test_create_delivery_default_item_count(client, seed_data):
    """宅配登记不传 item_count → 默认 1。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.post(
        _create_url(),
        json={
            "kind": "delivery",
            "student_id": str(seed_data["student"].id),
            "description": "ヤマト",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["data"]["item_count"] == 1


def test_create_delivery_with_item_count(client, seed_data):
    """宅配登记传 item_count=3 → 落库 + 回显 3。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.post(
        _create_url(),
        json={
            "kind": "delivery",
            "student_id": str(seed_data["student"].id),
            "item_count": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["data"]["item_count"] == 3


def test_create_item_count_must_be_positive(client, seed_data):
    """item_count=0 → 422（下限 1）。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.post(
        _create_url(),
        json={
            "kind": "delivery",
            "student_id": str(seed_data["student"].id),
            "item_count": 0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422, res.text


def test_create_delivery_description_optional(client, seed_data):
    """宅配 description 可不传 → 201 + 缺省存空串（6-14 备注改可选）。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.post(
        _create_url(),
        json={
            "kind": "delivery",
            "student_id": str(seed_data["student"].id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["data"]["description"] == ""


def test_create_lost_and_found_requires_description(client, seed_data):
    """失物招领不传 description → 422（物品说明仍必填）。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.post(
        _create_url(),
        json={
            "kind": "lost_and_found",
            "location": "食堂",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422, res.text
