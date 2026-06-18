"""临时账户 + 登录选寮过滤测试（2026-06-18）。

覆盖：
- dorm_units_for_teacher 按登录选的寮过滤（单元）：选男→[1,2] / 选女→[4] / 未选→全部 / op·承認组永远全部
- 选寮经令牌驱动学生列表过滤（集成）
- 临时账户到期：过期账户登录被拒 + 已签发令牌也被拒
- POST /teachers 带 expires_at 建临时账户
"""

from datetime import datetime, timedelta, timezone

from app import deps, models, permissions, security


# ---------------------------------------------------------------
# 单元：dorm_units_for_teacher 按选寮过滤
# ---------------------------------------------------------------
def _teacher(group, selected=None, role="寮務課長"):
    """造一个不入库的 Teacher（permission_group 显式设，effective_group 直接返回它）。"""
    t = models.Teacher(
        login_id="x",
        name="x",
        email="x@x.jp",
        password_hash="x",
        role=role,
        permission_group=group,
    )
    if selected is not None:
        t._selected_dorm = selected
    return t


def test_dorm_units_select_male_returns_1_2():
    assert deps.dorm_units_for_teacher(_teacher(permissions.GROUP_DORM_ADMIN, 1)) == [
        1,
        2,
    ]


def test_dorm_units_select_female_returns_4():
    assert deps.dorm_units_for_teacher(_teacher(permissions.GROUP_DORM_ADMIN, 4)) == [4]


def test_dorm_units_no_selection_sees_all():
    assert deps.dorm_units_for_teacher(
        _teacher(permissions.GROUP_DORM_ADMIN, None)
    ) == [1, 2, 4]


def test_dorm_units_approval_group_always_all_even_if_selected():
    # 申請承認専用：选了男寮也看全部男女
    assert deps.dorm_units_for_teacher(_teacher(permissions.GROUP_APPROVAL, 1)) == [
        1,
        2,
        4,
    ]


def test_dorm_units_op_always_all():
    assert deps.dorm_units_for_teacher(
        _teacher(permissions.GROUP_OP, 4, role="寮務部長")
    ) == [1, 2, 4]


# ---------------------------------------------------------------
# 集成辅助
# ---------------------------------------------------------------
def _add_student(db, grade, klass, seat, dorm_unit, gender, room):
    s = models.Student(
        grade_code=grade,
        class_code=klass,
        seat_no=seat,
        name=f"S{grade}{klass}{seat}",
        gender=gender,
        room_no=room,
        dorm_unit=dorm_unit,
        is_overseas=False,
        email=f"{grade}{klass}{seat}@t.jp",
    )
    db.add(s)
    db.flush()
    db.add(models.Account(student_id=s.id, password_hash=security.hash_password("x")))
    return s


def _login(client, login_id, **extra):
    body = {"login_id": login_id, "password": "test-password-12345", **extra}
    r = client.post("/api/v1/sessions/teacher", json=body)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ---------------------------------------------------------------
# 集成：选寮经令牌驱动学生列表过滤
# ---------------------------------------------------------------
def test_selected_dorm_filters_student_list(client, seed_data, db_session):
    # seed 自带 1 男生（dorm_unit 1）。再加 1 女生（dorm_unit 4）。
    _add_student(db_session, "05", "03", "01", 4, "female", "W401")
    db_session.commit()

    # 不选 → 看全部（男 + 女）
    tok = _login(client, "ryomu_kachou")
    r = client.get("/api/v1/students", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200, r.text
    dorms_all = {it["dorm_unit"] for it in r.json()["items"]}
    assert 1 in dorms_all and 4 in dorms_all

    # 选男 → 只男寮（1/2）
    tok_m = _login(client, "ryomu_kachou", selected_dorm=1)
    rm = client.get(
        "/api/v1/students", headers={"Authorization": f"Bearer {tok_m}"}
    )
    assert rm.status_code == 200
    items_m = rm.json()["items"]
    assert len(items_m) >= 1
    assert all(it["dorm_unit"] in (1, 2) for it in items_m)

    # 选女 → 只女寮（4）
    tok_f = _login(client, "ryomu_kachou", selected_dorm=4)
    rf = client.get(
        "/api/v1/students", headers={"Authorization": f"Bearer {tok_f}"}
    )
    assert rf.status_code == 200
    items_f = rf.json()["items"]
    assert len(items_f) >= 1
    assert all(it["dorm_unit"] == 4 for it in items_f)


# ---------------------------------------------------------------
# 集成：临时账户到期
# ---------------------------------------------------------------
def _make_temp_teacher(db, login_id, expires_at):
    t = models.Teacher(
        login_id=login_id,
        name="臨時",
        email=f"{login_id}@t.jp",
        password_hash=security.hash_password("test-password-12345"),
        role="管理係",
        permission_group=permissions.GROUP_GENERAL,
        expires_at=expires_at,
    )
    db.add(t)
    db.commit()
    return t


def test_temp_account_expired_login_rejected(client, db_session):
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    _make_temp_teacher(db_session, "temp_expired", past)
    r = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "temp_expired", "password": "test-password-12345"},
    )
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "ACCOUNT_EXPIRED"


def test_temp_account_future_login_ok(client, db_session):
    future = datetime.now(timezone.utc) + timedelta(days=1)
    _make_temp_teacher(db_session, "temp_ok", future)
    r = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "temp_ok", "password": "test-password-12345"},
    )
    assert r.status_code == 200, r.text


def test_issued_token_rejected_after_expiry(client, db_session):
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    t = _make_temp_teacher(db_session, "temp_soon", future)
    tok = _login(client, "temp_soon")
    # 拿到令牌后把到期改到过去 —— 已签发令牌也应被拒
    t.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    r = client.get("/api/v1/students", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "ACCOUNT_EXPIRED"


# ---------------------------------------------------------------
# 集成：POST /teachers 建临时账户
# ---------------------------------------------------------------
def test_create_temp_account_with_expiry(client, teacher_token):
    future = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    r = client.post(
        "/api/v1/teachers",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "login_id": "temp_new",
            "name": "代班先生",
            "email": "temp_new@t.jp",
            "password": "temppass123",
            "role": "管理係",
            "permission_group": permissions.GROUP_GENERAL,
            "expires_at": future,
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["expires_at"] is not None
