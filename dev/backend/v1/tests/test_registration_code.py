"""学生注册码 + POST /accounts 测试。

覆盖:
- /admin/registration-code/{current,refresh,history} 权限 + 行为
- POST /accounts: 注册码验证 / 学号重复 / room_no↔dorm_unit 一致性 / 成功路径
"""

from __future__ import annotations


# ---------- /admin/registration-code/* ----------


def test_refresh_requires_admin_role(client, student_token):
    """学生 token → 403（端点限定寮务管理 role）。"""
    res = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 403, res.text


def test_refresh_no_token_401(client):
    """没带 token → 401。"""
    res = client.post("/api/v1/admin/registration-code/refresh")
    assert res.status_code == 401, res.text


def test_refresh_returns_6_digit_code(client, teacher_token):
    """寮務課長（在 ADMIN_ROLES 里）→ 201 + 6 桁数字。"""
    res = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert "code" in data
    assert len(data["code"]) == 6
    assert data["code"].isdigit()
    assert data["expires_in_seconds"] > 0
    assert data["expires_in_seconds"] <= 30 * 60  # itsuki 2026-05-31: 30 分钟有效


def test_current_returns_active_code(client, teacher_token):
    """refresh 之后 current 返回同一个 code。"""
    refresh_res = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    current_res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert current_res.status_code == 200
    assert current_res.json()["data"]["code"] == refresh_res.json()["data"]["code"]


def test_close_invalidates_current(client, teacher_token):
    """老师点「关闭」→ 当前码立即失效、/current 返回 null（itsuki 2026-05-31 手动关闭）。"""
    client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    before = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert before.status_code == 200 and before.json()["data"] is not None

    close = client.post(
        "/api/v1/admin/registration-code/close",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert close.status_code == 204, close.text

    after = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert after.status_code == 200
    assert after.json()["data"] is None


def test_close_requires_admin_role(client, student_token):
    """学生 token 不能关闭注册码 → 403。"""
    res = client.post(
        "/api/v1/admin/registration-code/close",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 403


def test_current_null_when_no_active(client, teacher_token):
    """还没 refresh 时 current 返回 null。"""
    res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"] is None


def test_refresh_invalidates_previous(client, teacher_token):
    """连续 refresh 两次：旧 code 的 invalidated_at 应有值（用 history 端点验证）。"""
    first = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]
    second = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]
    # 两次 refresh 必产出不同 code（新 code 生成）。理论 1/百万 碰撞概率可忽略。
    assert first["code"] != second["code"]

    history = client.get(
        "/api/v1/admin/registration-code/history",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]
    # 历史按新→旧 — items[0] = second，items[1] = first
    assert history["items"][0]["code"] == second["code"]
    assert history["items"][0]["invalidated_at"] is None
    # first 应已 invalidate
    assert history["items"][1]["invalidated_at"] is not None


# ---------- POST /accounts ----------


def _new_account_body(code: str, **overrides):
    """测试默认 body — 用 overrides 局部覆盖。"""
    body = {
        "name": "新入生 太郎",
        "name_kana": "シンニュウセイ タロウ",
        "gender": "male",
        "grade_code": "07",
        "class_code": "01",
        "seat_no": "05",
        # 2 寮男生：房号 A 前缀（§5.0：A1〜A12），dorm_unit=2（旧默认 M205+dorm2 是非法组合，
        # 靠当时后端 bug 蒙混过关；现已对齐 spec/DB CHECK，A 前缀才是 2 寮合法房号）
        "room_no": "A5",
        "dorm_unit": 2,
        "is_overseas": False,
        "password": "test-password-12345",
        "registration_code": code,
    }
    body.update(overrides)
    return body


def test_create_account_invalid_code(client, seed_data):
    """无效 code → 422 INVALID_REGISTRATION_CODE。"""
    res = client.post("/api/v1/accounts", json=_new_account_body("999999"))
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_REGISTRATION_CODE"


def test_create_account_success(client, seed_data, teacher_token):
    """有效 code + 所有字段都对 → 201 + JWT。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    res = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert "access_token" in data
    assert data["expires_in"] > 0
    assert data["student"]["student_no"] == "070105"
    assert data["student"]["name"] == "新入生 太郎"


def test_create_account_student_no_taken(client, seed_data, teacher_token):
    """学号撞到 conftest seed 的学生 → 422 STUDENT_NO_TAKEN。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    res = client.post(
        "/api/v1/accounts",
        json=_new_account_body(
            code,
            grade_code="06",
            class_code="02",
            seat_no="18",
            room_no="M101",
            dorm_unit=1,
        ),
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "STUDENT_NO_TAKEN"


def test_create_account_room_dorm_mismatch(client, seed_data, teacher_token):
    """room_no=W*** 但 dorm_unit=2（应为 A 前缀 male）→ 422 INVALID_ROOM_FORMAT。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    res = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, room_no="W101"),  # 与 dorm_unit=2（A 前缀）矛盾
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_ROOM_FORMAT"


def test_create_account_2dorm_rejects_M_prefix(client, seed_data, teacher_token):
    """回归守卫：2 寮（dorm_unit=2）必须 A 前缀房号；旧 bug 用 M205 也能过 → 现应 422。

    起因：旧 validate_room_dorm_match 对 dorm_unit∈{1,2} 一律期望 M 前缀，与 §5.0 +
    §8.1 DB CHECK（2 寮要求 ^A[0-9]{1,2}$）矛盾，导致 2 寮 A 房号被拒、M 房号反被放行。
    """
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    # M205 + dorm_unit=2：旧实现误判通过，修复后应被 DB CHECK 同源正则拒绝
    res = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, room_no="M205", dorm_unit=2),
    )
    assert res.status_code == 422, res.text
    assert res.json()["error"]["code"] == "INVALID_ROOM_FORMAT"


def test_create_account_2dorm_A_prefix_success(client, seed_data, teacher_token):
    """2 寮合法注册：A 前缀房号 + dorm_unit=2 + male → 201（修复前必被 422 拒，2 寮根本注册不了）。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    res = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, room_no="A12", dorm_unit=2),
    )
    assert res.status_code == 201, res.text


def test_create_account_code_reusable_within_ttl(client, seed_data, teacher_token):
    """同一个 code 5 分钟内多个学生都能用（集团登记场景，§7.16.2 规则 5）。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    res1 = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert res1.status_code == 201

    res2 = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, seat_no="06", grade_code="07", class_code="01"),
    )
    assert res2.status_code == 201, res2.text


def test_create_account_after_refresh_old_code_fails(client, seed_data, teacher_token):
    """refresh 之后旧 code 立刻失效 → 用旧 code 注册 → 422。"""
    old_code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]
    # 再 refresh 一次 → old_code 被作废
    client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    res = client.post("/api/v1/accounts", json=_new_account_body(old_code))
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_REGISTRATION_CODE"


def test_create_account_integrity_fallback_student_no(
    client, seed_data, teacher_token, monkeypatch
):
    """accounts-be-2 并发兜底：前置学号查重未命中（模拟并发窗口），但 DB 已有同学号
    → commit 撞 uq_students_no → 兜底返 422 STUDENT_NO_TAKEN（而非不透明 500）。

    单线程没法真并发，用 monkeypatch 把「学号前置查重」第一次短路成空结果，
    模拟「查时对方还没提交、commit 时才撞」的竞态窗口。
    """
    from uuid import uuid4

    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app import models

    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["data"]["code"]

    # 先正常注册占用学号 07/01/05（_new_account_body 默认学号）
    r1 = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert r1.status_code == 201, r1.text

    # monkeypatch：让 create_account 的「学号前置查重」第一次返回空（模拟并发窗口）
    real_scalars = Session.scalars
    state = {"suppress": True}

    def patched(self, statement, *a, **k):
        sql = str(statement)
        if state["suppress"] and "grade_code = :" in sql and "seat_no = :" in sql:
            state["suppress"] = False
            return real_scalars(
                self, select(models.Student).where(models.Student.id == uuid4())
            )
        return real_scalars(self, statement, *a, **k)

    monkeypatch.setattr(Session, "scalars", patched)

    # 再次注册同学号 → 前置查重被短路 → insert+commit 撞 uq_students_no → 兜底 STUDENT_NO_TAKEN
    r2 = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "STUDENT_NO_TAKEN"
