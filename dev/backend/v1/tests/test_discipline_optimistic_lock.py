"""POST /api/v1/discipline/manual — 乐观锁 expected_current_points 测试。

堵住「前端再 GET → POST 到达」空档：老师核对时看到的分数随请求传给后端，
行锁内比对不一致则 409 POINTS_CHANGED、不写入任何 DemeritEvent。
不传该字段时行为与以前完全一致（向后兼容 iOS / Android）。
"""

from __future__ import annotations

from sqlalchemy import func, select

from app import models


def _login_teacher(client, login_id):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def _count_demerits(db_session, student_id) -> int:
    db_session.expire_all()
    return int(
        db_session.scalar(
            select(func.count())
            .select_from(models.DemeritEvent)
            .where(models.DemeritEvent.student_id == student_id)
        )
        or 0
    )


def test_manual_demerit_expected_matches_writes(client, seed_data, db_session):
    """传了 expected_current_points 且与实际一致 → 正常写入。"""
    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # 先把本月总分设到 4，作为「当前实际」
    r0 = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 4.0,
            "reason": "初期",
        },
        headers=headers,
    )
    assert r0.status_code == 201, r0.text
    before = _count_demerits(db_session, seed_data["student"].id)

    # expected=4（与实际一致）→ 设成 6，应成功写入一条 +2 差值事件
    r = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 6.0,
            "reason": "楽観ロック一致",
            "expected_current_points": 4.0,
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["data"]["points"] == 2.0
    assert _count_demerits(db_session, seed_data["student"].id) == before + 1


def test_manual_demerit_expected_mismatch_409_no_write(client, seed_data, db_session):
    """传了 expected_current_points 但不一致 → 409 POINTS_CHANGED，且不写入任何事件。"""
    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # 实际当前 = 5
    r0 = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 5.0,
            "reason": "初期",
        },
        headers=headers,
    )
    assert r0.status_code == 201, r0.text
    before = _count_demerits(db_session, seed_data["student"].id)

    # 老师还以为是 4（模拟 GET→POST 空档里被自动扣了 1 分）→ 应拒绝
    r = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 4.0,
            "reason": "古い期待値で上書きしようとする",
            "expected_current_points": 4.0,
        },
        headers=headers,
    )
    assert r.status_code == 409, r.text
    assert r.json()["error"]["code"] == "POINTS_CHANGED"
    # 消息里应带期待值 / 实际值，方便老师看差多少
    msg = r.json()["error"]["message"]
    assert "4" in msg and "5" in msg
    assert _count_demerits(db_session, seed_data["student"].id) == before


def test_manual_demerit_no_expected_keeps_legacy(client, seed_data, db_session):
    """不传 expected_current_points（None）→ 行为跟以前一样正常写入。"""
    token = _login_teacher(client, "ryomu_kachou")
    student_id = str(seed_data["student"].id)
    headers = {"Authorization": f"Bearer {token}"}

    before = _count_demerits(db_session, seed_data["student"].id)
    r = client.post(
        "/api/v1/discipline/manual",
        json={
            "student_id": student_id,
            "target_points": 3.0,
            "reason": "互換：期待値なし",
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["data"]["points"] == 3.0
    assert _count_demerits(db_session, seed_data["student"].id) == before + 1
