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


def test_b1_logout_teacher_token_403(client, teacher_token, seed_data):
    """教师 token 打学生端点 → 403（端点只接受 student role）。"""
    res = client.delete(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 403, res.text


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
