"""GET /api/v1/discipline/students — 手动扣分挑学生接口测试。

2026-06-14 选学生统一改造 §5 约束2：扣分页新增「搜任意学生 → 手动扣分」入口需要
一个权限与扣分对齐（C_DEMERIT）的搜学生接口，区别于 front-desk 的 C_FRONTDESK。
"""

from __future__ import annotations


def _login_teacher(client, login_id):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_demerit_student_search_works(client, seed_data):
    """有扣分管理权限的老师（寮務課長）搜学生 → 200 且含 seed 学生。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.get(
        "/api/v1/discipline/students",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    names = {s["name"] for s in res.json()}
    assert seed_data["student"].name in names
    # 返回的是挑人最小字段（与 FrontDeskStudentBrief 同形）
    sample = res.json()[0]
    assert {"id", "name", "room_no", "student_no", "dorm_unit"} <= set(sample.keys())


def test_demerit_student_search_filters_by_q(client, seed_data):
    """q 搜不到的关键字 → 空列表（证明 q 真在筛）。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.get(
        "/api/v1/discipline/students?q=ZZZNOMATCH",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json() == []


def test_demerit_student_search_rejects_student_token(client, seed_data, student_token):
    """学生令牌访问老师接口 → 拒绝（非老师身份）。"""
    res = client.get(
        "/api/v1/discipline/students",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code in (401, 403), res.text
