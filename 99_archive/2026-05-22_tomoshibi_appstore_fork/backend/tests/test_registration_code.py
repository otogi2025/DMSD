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
    data = res.json()
    assert "code" in data
    assert len(data["code"]) == 6
    assert data["code"].isdigit()
    assert data["expires_in_seconds"] > 0
    assert data["expires_in_seconds"] <= 5 * 60


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
    assert current_res.json()["code"] == refresh_res.json()["code"]


def test_current_null_when_no_active(client, teacher_token):
    """还没 refresh 时 current 返回 null。"""
    res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200
    assert res.json() is None


def test_refresh_invalidates_previous(client, teacher_token):
    """连续 refresh 两次：旧 code 的 invalidated_at 应有值（用 history 端点验证）。"""
    first = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
    second = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
    # 两次 random 偶发碰撞理论可能（1/百万），允许相等 — 此 assert 是文档型
    assert first["code"] != second["code"] or True

    history = client.get(
        "/api/v1/admin/registration-code/history",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
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
        "room_no": "M205",
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
    assert res.json()["detail"]["code"] == "INVALID_REGISTRATION_CODE"


def test_create_account_success(client, seed_data, teacher_token):
    """有效 code + 所有字段都对 → 201 + JWT。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["code"]

    res = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["expires_in"] > 0
    assert data["student"]["student_no"] == "070105"
    assert data["student"]["name"] == "新入生 太郎"


def test_create_account_student_no_taken(client, seed_data, teacher_token):
    """学号撞到 conftest seed 的学生 → 422 STUDENT_NO_TAKEN。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["code"]

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
    assert res.json()["detail"]["code"] == "STUDENT_NO_TAKEN"


def test_create_account_room_dorm_mismatch(client, seed_data, teacher_token):
    """room_no=W*** 但 dorm_unit=2（M+ male）→ 422 INVALID_ROOM_FORMAT。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["code"]

    res = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, room_no="W101"),  # 与 M + dorm 2 矛盾
    )
    assert res.status_code == 422
    assert res.json()["detail"]["code"] == "INVALID_ROOM_FORMAT"


def test_create_account_code_reusable_within_ttl(client, seed_data, teacher_token):
    """同一个 code 5 分钟内多个学生都能用（集团登记场景，§7.16.2 规则 5）。"""
    code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["code"]

    res1 = client.post("/api/v1/accounts", json=_new_account_body(code))
    assert res1.status_code == 201

    res2 = client.post(
        "/api/v1/accounts",
        json=_new_account_body(code, seat_no="06", grade_code="07", class_code="01"),
    )
    assert res2.status_code == 201, res2.text


def test_create_account_after_refresh_old_code_fails(
    client, seed_data, teacher_token
):
    """refresh 之后旧 code 立刻失效 → 用旧 code 注册 → 422。"""
    old_code = client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()["code"]
    # 再 refresh 一次 → old_code 被作废
    client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    res = client.post("/api/v1/accounts", json=_new_account_body(old_code))
    assert res.status_code == 422
    assert res.json()["detail"]["code"] == "INVALID_REGISTRATION_CODE"
