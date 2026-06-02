"""B 类安全修复测试（B1/B2/B6/B7/B10）。

2026-05-30 新增 — 覆盖 5 条安全/接口补丁：
- B1  DELETE /api/v1/sessions/current — 登出端点
- B2  DELETE /api/v1/accounts/me — 学生自删账号
- B6  学生登录失败计数 + 锁定
- B7  注册码一次性（用后 invalidated_at 标废）
- B10 dorm_unit=3 拒绝（Literal[1,2,4]）
"""

from __future__ import annotations


# ─────────────────────────────────────────
# helpers
# ─────────────────────────────────────────


def _make_reg_code(client, teacher_token: str) -> str:
    """生成一枚注册码，返回 code 字符串。"""
    res = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 201, res.text
    return res.json()["code"]


_REGISTER_BASE = {
    "name": "テスト学生",
    "gender": "male",
    "grade_code": "05",
    "class_code": "01",
    "seat_no": "01",
    "room_no": "M501",
    "dorm_unit": 1,
    "password": "password123",
}


def _register(client, code: str, overrides: dict | None = None) -> dict:
    body = {**_REGISTER_BASE, "registration_code": code}
    if overrides:
        body.update(overrides)
    return client.post("/api/v1/accounts", json=body)


# ─────────────────────────────────────────
# B1 — DELETE /sessions/current
# ─────────────────────────────────────────


def test_b1_logout_ok(client, student_token, seed_data):
    """有效 student token → 204。"""
    res = client.delete(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 204, res.text


def test_b1_logout_no_token_401(client):
    """无 token → 401。"""
    res = client.delete("/api/v1/sessions/current")
    assert res.status_code == 401, res.text


def test_b1_logout_teacher_token_204(client, teacher_token, seed_data):
    """#3 修复：教师 token 调登出端点 → 204（get_current_principal 接受老师+学生）。"""
    res = client.delete(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 204, res.text


# ─────────────────────────────────────────
# B2 — DELETE /accounts/me
# ─────────────────────────────────────────


def test_b2_delete_account_ok(client, student_token, seed_data, db_session):
    """成功软删：Student.status → 'deleted'，Account.password_hash 清空。"""
    from app import models

    res = client.delete(
        "/api/v1/accounts/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 204, res.text

    # DB 验证
    db_session.expire_all()
    student = seed_data["student"]
    s = db_session.get(models.Student, student.id)
    # 'paused' = 账号停用（CHECK 枚举内最接近"已删"的状态，物理删会破坏历史审计）
    assert s.status == "paused"

    from sqlalchemy import select

    account = db_session.scalars(
        select(models.Account).where(models.Account.student_id == student.id)
    ).first()
    assert account is not None  # 行保留（历史用）
    assert account.password_hash == ""  # 密码清空

    # AuditLog 写入
    log = db_session.scalars(
        select(models.AuditLog).where(
            models.AuditLog.actor_id == student.id,
            models.AuditLog.action == "account.delete_self",
        )
    ).first()
    assert log is not None


def test_b2_delete_account_no_token_401(client):
    """无 token → 401。"""
    res = client.delete("/api/v1/accounts/me")
    assert res.status_code == 401, res.text


# ─────────────────────────────────────────
# B6 — 学生登录失败计数 + 锁定
# ─────────────────────────────────────────


def test_b6_failed_count_increments(client, seed_data, db_session):
    """密码错误 → accounts.failed_count 递增。"""
    from app import models
    from sqlalchemy import select

    for i in range(3):
        res = client.post(
            "/api/v1/sessions/student",
            json={"student_no": "060218", "password": "wrong!!"},
        )
        assert res.status_code == 401

    db_session.expire_all()
    student = seed_data["student"]
    account = db_session.scalars(
        select(models.Account).where(models.Account.student_id == student.id)
    ).first()
    assert account.failed_count == 3


def test_b6_account_locked_after_threshold(client, seed_data, db_session):
    """5 回失败 → 423 ACCOUNT_LOCKED が返る。"""

    # 连续失败 5 次（阈值 = 5）
    for _ in range(5):
        client.post(
            "/api/v1/sessions/student",
            json={"student_no": "060218", "password": "wrong!!"},
        )

    # 6 回目 → 423
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": "060218", "password": "wrong!!"},
    )
    assert res.status_code == 423
    assert res.json()["detail"]["code"] == "ACCOUNT_LOCKED"


def test_b6_success_clears_failed_count(client, seed_data, db_session):
    """失败 2 回後に正しい密码 → failed_count=0 にリセット。"""
    from app import models
    from sqlalchemy import select

    for _ in range(2):
        client.post(
            "/api/v1/sessions/student",
            json={"student_no": "060218", "password": "wrong!!"},
        )

    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": "060218", "password": "test-password-12345"},
    )
    assert res.status_code == 200

    db_session.expire_all()
    student = seed_data["student"]
    account = db_session.scalars(
        select(models.Account).where(models.Account.student_id == student.id)
    ).first()
    assert account.failed_count == 0
    assert account.locked_until is None


# ─────────────────────────────────────────
# B7 — 注册码一次性
# ─────────────────────────────────────────


def test_b7_code_reusable_within_ttl(client, teacher_token, seed_data, db_session):
    """B7 存疑确认：spec §7.16.2 规则 5 — 同一码 5 分钟内多人可用（集团登记场景）。

    invalidated_at 只在 /refresh 生成新码时设置，注册成功本身不作废码。
    """
    from app import models
    from sqlalchemy import select

    code = _make_reg_code(client, teacher_token)

    # 第一个学生注册 → 成功
    res = _register(client, code)
    assert res.status_code == 201, res.text

    # DB 确认 invalidated_at 仍为 NULL（码未被作废）
    db_session.expire_all()
    row = db_session.scalars(
        select(models.StudentRegistrationCode).where(
            models.StudentRegistrationCode.code == code
        )
    ).first()
    assert row.invalidated_at is None, (
        "注册成功不应作废注册码（spec §7.16.2 规则 5 集团登记）"
    )

    # 第二个学生用同一码注册 → 也成功
    res2 = _register(
        client,
        code,
        overrides={
            "grade_code": "05",
            "class_code": "01",
            "seat_no": "02",
            "room_no": "M502",
        },
    )
    assert res2.status_code == 201, res2.text


# ─────────────────────────────────────────
# B10 — dorm_unit=3 拒绝
# ─────────────────────────────────────────


def test_b10_dorm_unit_3_rejected(client, teacher_token, seed_data):
    """dorm_unit=3 は DB CHECK 違反なので 422 で拒否される。"""
    code = _make_reg_code(client, teacher_token)
    res = _register(
        client, code, overrides={"dorm_unit": 3, "gender": "male", "room_no": "M501"}
    )
    assert res.status_code == 422, res.text


def test_b10_dorm_unit_valid_values(client, teacher_token, seed_data):
    """dorm_unit=1 は通る（2/4 は別テストで seed 重複を避けるため省略）。"""
    code = _make_reg_code(client, teacher_token)
    res = _register(client, code, overrides={"dorm_unit": 1})
    assert res.status_code == 201, res.text


# ─────────────────────────────────────────
# B8 — R4 寮边界 (寮監对管辖外寮学生操作 → 403)
# ─────────────────────────────────────────


def _make_ryokan_token(client, db_session) -> str:
    """女寮担当の寮監 token を作って返す。seed_data の学生は dorm_unit=1 (男寮)。"""
    from app import models, security

    pw = security.hash_password("test-password-12345")
    t = models.Teacher(
        login_id="ryokan_test",
        name="女寮監テスト",
        email="ryokan@test.jp",
        password_hash=pw,
        role="寮監",
        assigned_dorm=4,  # 女寮
    )
    db_session.add(t)
    db_session.commit()

    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryokan_test", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_b8_cleaning_create_cross_dorm_403(client, db_session, seed_data):
    """女寮監が男寮学生 (dorm_unit=1) に清扫分配 → 403。"""
    from datetime import date

    ryokan_token = _make_ryokan_token(client, db_session)
    student_id = str(seed_data["student"].id)  # dorm_unit=1

    res = client.post(
        "/api/v1/cleaning",
        json={
            "student_id": student_id,
            "area": "廊下",
            "scheduled_date": date.today().isoformat(),
        },
        headers={"Authorization": f"Bearer {ryokan_token}"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"


def test_b8_cleaning_create_same_dorm_ok(client, db_session, seed_data):
    """男寮監 (assigned_dorm=1) が男寮学生に清扫分配 → 201。"""
    from datetime import date

    from app import models, security

    pw = security.hash_password("test-password-12345")
    t = models.Teacher(
        login_id="otokan_test",
        name="男寮監テスト",
        email="otokan@test.jp",
        password_hash=pw,
        role="寮監",
        assigned_dorm=1,  # 男寮
    )
    db_session.add(t)
    db_session.commit()

    res_login = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "otokan_test", "password": "test-password-12345"},
    )
    assert res_login.status_code == 200, res_login.text
    token = res_login.json()["access_token"]

    student_id = str(seed_data["student"].id)  # dorm_unit=1
    res = client.post(
        "/api/v1/cleaning",
        json={
            "student_id": student_id,
            "area": "廊下",
            "scheduled_date": date.today().isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text


def test_b8_front_desk_create_cross_dorm_403(client, db_session, seed_data):
    """女寮監が男寮学生 (dorm_unit=1) に宅配登记 → 403。"""
    ryokan_token = _make_ryokan_token(client, db_session)
    student_id = str(seed_data["student"].id)

    res = client.post(
        "/api/v1/front-desk",
        json={
            "kind": "delivery",
            "student_id": student_id,
            "description": "テスト荷物",
        },
        headers={"Authorization": f"Bearer {ryokan_token}"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"


def test_b8_rollcall_checkin_cross_dorm_403(client, db_session, seed_data):
    """女寮監が男寮学生 (dorm_unit=1) に点呼签到 → 403。"""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    from app import models

    ryokan_token = _make_ryokan_token(client, db_session)

    # 创建男寮 dorm_unit=[1,2] 的 running session
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

    res = client.post(
        f"/api/v1/rollcall/sessions/{session.id}/checkins",
        json={
            "student_id": str(seed_data["student"].id),
            "status_source": "manual_checkin",
            "path_hint": "manual",
        },
        headers={"Authorization": f"Bearer {ryokan_token}"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"


# ─────────────────────────────────────────
# IX-008 — get_current_student 畸形 token 防 500（deps.py try/except）
# ─────────────────────────────────────────


def test_ix008_me_malformed_sub_returns_401(client):
    """学生 token 但 sub 非合法 UUID → 401（不是 500）。

    deps.get_current_student 之前直接 UUID(payload["sub"])，畸形 sub 会抛
    未捕获异常变 500；仿 get_current_principal 包 try/except 后统一返 401。
    codex + Claude 双审同时指出这处依赖一致性缺口。
    """
    from app.security import create_access_token

    token = create_access_token("not-a-uuid", "student")
    res = client.get(
        "/api/v1/students/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 401, res.text
    assert res.json()["detail"]["code"] == "INVALID_CREDENTIALS"
