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
    return res.json()["data"]["access_token"]


def test_demerit_student_search_works(client, seed_data):
    """有扣分管理权限的老师（寮務課長）搜学生 → 200 且含 seed 学生。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.get(
        "/api/v1/discipline/students",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    names = {s["name"] for s in res.json()["data"]}
    assert seed_data["student"].name in names
    # 返回的是挑人最小字段（与 FrontDeskStudentBrief 同形）
    sample = res.json()["data"][0]
    assert {"id", "name", "room_no", "student_no", "dorm_unit"} <= set(sample.keys())


def test_demerit_student_search_filters_by_q(client, seed_data):
    """q 搜不到的关键字 → 空列表（证明 q 真在筛）。"""
    token = _login_teacher(client, "ryomu_kachou")
    res = client.get(
        "/api/v1/discipline/students?q=ZZZNOMATCH",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"] == []


def test_demerit_student_search_rejects_student_token(client, seed_data, student_token):
    """学生令牌访问老师接口 → 拒绝（非老师身份）。"""
    res = client.get(
        "/api/v1/discipline/students",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code in (401, 403), res.text


# ─────────────────────────────────────────────────────────────
# B-中-14：VIEW-only 权限组手动加 / 撤销扣分应 403
# ─────────────────────────────────────────────────────────────
# 国際交流部長 默认落在「申請承認専用」组，对 C_DEMERIT（扣分管理）只有 VIEW；
# create_manual_demerit / revoke_demerit 都要 require_permission(C_DEMERIT, MANAGE)，
# 故该组写扣分必须被 403 挡住。守住这条防止 require_permission 的级别比较写错
# （如 >= 写成 >、或漏掉 C_DEMERIT 簇）时只读组越权写扣分不被测试发现。
def test_manual_demerit_view_only_group_forbidden(client, seed_data):
    """申請承認専用组（国際交流部長、C_DEMERIT 仅 VIEW）手动加扣分 → 403。"""
    token = _login_teacher(client, "kokukou_buchou")
    student_id = str(seed_data["student"].id)
    res = client.post(
        "/api/v1/discipline/manual",
        json={"student_id": student_id, "target_points": 1.0, "reason": "テスト"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403, res.text


def test_revoke_demerit_view_only_group_forbidden(client, seed_data, db_session):
    """申請承認専用组（国際交流部長、C_DEMERIT 仅 VIEW）撤销扣分 → 403。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from app import models

    # 先在 DB 直接建一条扣分事件（不经 API，避免触发写权限）
    event = models.DemeritEvent(
        student_id=seed_data["student"].id,
        source_type="manual",
        points=1.0,
        reason="テスト",
        month=datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m"),
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    token = _login_teacher(client, "kokukou_buchou")
    res = client.post(
        f"/api/v1/discipline/{event.id}/revoke",
        json={"revoke_reason": "テスト撤销"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403, res.text


# ─────────────────────────────────────────────────────────────
# A-473：手动加扣分幂等 —— 同 idempotency_key 重复提交不叠加
# ─────────────────────────────────────────────────────────────
# 老师双击「加扣分」或网络重试时，客户端带同一个 idempotency_key 重复 POST，
# 后端应识别为重复、返回同一条事件、不再叠加扣分（否则会污染 /ranking 累计与 8 分阈值）。
def test_manual_demerit_same_key_returns_existing(client, seed_data):
    """同 idempotency_key 第二次 POST → 返回同一条事件、不新建（幂等）。"""
    import uuid

    token = _login_teacher(client, "ryomu_kachou")  # 寮務課長 = 跨寮 MANAGE
    student_id = str(seed_data["student"].id)
    key = str(uuid.uuid4())
    body = {
        "student_id": student_id,
        "target_points": 2.0,
        "reason": "幂等テスト",
        "idempotency_key": key,
    }
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.post("/api/v1/discipline/manual", json=body, headers=headers)
    assert r1.status_code == 201, r1.text
    r2 = client.post("/api/v1/discipline/manual", json=body, headers=headers)
    # 第二次仍成功响应、且是同一条事件（id 相同）
    assert r2.status_code in (200, 201), r2.text
    assert r1.json()["data"]["id"] == r2.json()["data"]["id"], "同 key 重复提交应返回同一条事件"

    # 幂等：同 key 第二次返回原事件、不新建 → 该学生当月总分仍是 target 2.0
    month = r1.json()["data"]["month"]
    rk = client.get(f"/api/v1/discipline/ranking?month={month}", headers=headers)
    assert rk.status_code == 200, rk.text
    entry = next(e for e in rk.json()["data"]["entries"] if e["student_id"] == student_id)
    assert entry["total_points"] == 2.0, "幂等失败：扣分被叠加了"


def test_manual_demerit_different_keys_create_two(client, seed_data):
    """不同 idempotency_key → 各建一条（证明去重按 key 而非按 student_id）。"""
    import uuid

    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 1.0,
            "reason": "1回目",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers=headers,
    )
    r2 = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 1.5,
            "reason": "2回目",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers=headers,
    )
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text
    assert r1.json()["data"]["id"] != r2.json()["data"]["id"], "不同 key 应各建一条"

    # 两次设定绝对分（target 1.0 → 1.5），各记一条差值事件（+1.0 / +0.5），最终总分 = 最后一次 target 1.5
    month = r1.json()["data"]["month"]
    rk = client.get(f"/api/v1/discipline/ranking?month={month}", headers=headers)
    entry = next(e for e in rk.json()["data"]["entries"] if e["student_id"] == student_id)
    assert entry["total_points"] == 1.5


def test_manual_demerit_no_key_keeps_legacy_behavior(client, seed_data):
    """不带 idempotency_key（老客户端）→ 每次都新建一条，保持原行为。"""
    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}
    body = {"student_id": student_id, "target_points": 1.0, "reason": "キー無し"}

    r1 = client.post("/api/v1/discipline/manual", json=body, headers=headers)
    r2 = client.post("/api/v1/discipline/manual", json=body, headers=headers)
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text
    assert r1.json()["data"]["id"] != r2.json()["data"]["id"], "无 key 时不应去重（原行为）"


def test_manual_demerit_set_absolute_can_lower(client, seed_data):
    """B 方案核心：设定绝对分能把已有扣分调低（不只是加）—— 记一条负差值事件。"""
    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # 先设到 6 分
    r0 = client.post(
        "/api/v1/discipline/manual",
        json={"student_id": student_id, "target_points": 6.0, "reason": "初期設定"},
        headers=headers,
    )
    assert r0.status_code == 201, r0.text
    assert r0.json()["data"]["points"] == 6.0  # 学生本月 0 分起 → 差值 +6.0

    # 再设到 2 分（调低）→ 应记一条 -4 的差值事件
    r = client.post(
        "/api/v1/discipline/manual",
        json={"student_id": student_id, "target_points": 2.0, "reason": "減点修正"},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["data"]["points"] == -4.0, "调低应记负差值事件"

    # 当月总分应恰为 2.0（不是 6 也不是 8）
    month = r.json()["data"]["month"]
    rk = client.get(f"/api/v1/discipline/ranking?month={month}", headers=headers)
    entry = next(e for e in rk.json()["data"]["entries"] if e["student_id"] == student_id)
    assert entry["total_points"] == 2.0, "设定绝对分后总分应等于 target"
