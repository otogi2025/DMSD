"""老师通知中心 阶段1 端点测试 — feed 同步 / 幂等 / 已读 / 全部已读 / 鉴权。

通知由 routers/notifications.py 取 feed 时扫现有事件表（扣分等）同步生成，
本测试用扣分事件（DemeritEvent）当来源验证整条链路。
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app import models


def _feed(client, token):
    """拉一次通知流，返回 JSON body。"""
    res = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    return res.json()


def _add_demerit(db_session, student, reason="遅刻", points=1.0):
    """给学生加一条扣分事件（通知同步的来源之一）。"""
    ev = models.DemeritEvent(
        student_id=student.id,
        source_type="manual",
        points=points,
        reason=reason,
        month="2026-06",
    )
    db_session.add(ev)
    db_session.commit()
    return ev


def test_feed_empty(client, seed_data, teacher_token):
    res = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["items"] == []
    assert body["unread_count"] == 0


def test_feed_syncs_demerit_event(client, seed_data, teacher_token, db_session):
    _add_demerit(db_session, seed_data["student"], reason="門限超過")
    res = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["category"] == "demerit"
    assert "門限超過" in item["body"]
    assert item["is_read"] is False
    assert item["related_student_id"] == str(seed_data["student"].id)
    assert body["unread_count"] == 1


def test_sync_is_idempotent(client, seed_data, teacher_token, db_session):
    _add_demerit(db_session, seed_data["student"])
    for _ in range(3):
        res = client.get(
            "/api/v1/notifications/feed",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
    # 多次同步同一事件只生成 1 条通知
    assert len(res.json()["items"]) == 1
    assert res.json()["unread_count"] == 1


def test_mark_read(client, seed_data, teacher_token, db_session):
    _add_demerit(db_session, seed_data["student"])
    feed = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
    nid = feed["items"][0]["id"]
    res = client.post(
        f"/api/v1/notifications/{nid}/read",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["unread_count"] == 0
    feed2 = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
    assert feed2["items"][0]["is_read"] is True
    assert feed2["unread_count"] == 0


def test_read_all(client, seed_data, teacher_token, db_session):
    _add_demerit(db_session, seed_data["student"], reason="A")
    _add_demerit(db_session, seed_data["student"], reason="B")
    client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    res = client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["unread_count"] == 0


def test_unread_count_endpoint(client, seed_data, teacher_token, db_session):
    _add_demerit(db_session, seed_data["student"])
    res = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["unread_count"] == 1


def test_feed_rejects_student_token(client, seed_data, student_token):
    res = client.get(
        "/api/v1/notifications/feed",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 403


def test_mark_read_unknown_404(client, seed_data, teacher_token):
    res = client.post(
        f"/api/v1/notifications/{uuid.uuid4()}/read",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 404


# ---------------------------------------------------------------
# 阶段2：第二批通知来源（7 类申请表）。这里抽查 3 类，
# 覆盖 2 个字段名坑：proposer_id（行事企画）/ created_at（杂项）。
# ---------------------------------------------------------------


def test_feed_syncs_outing(client, seed_data, teacher_token, db_session):
    """外出申请 → category=outing 进通知流。"""
    db_session.add(
        models.Outing(
            student_id=seed_data["student"].id,
            outing_date=date(2026, 6, 20),
            destination="駅前",
        )
    )
    db_session.commit()
    body = _feed(client, teacher_token)
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["category"] == "outing"
    assert "駅前" in item["body"]
    assert item["related_student_id"] == str(seed_data["student"].id)


def test_feed_syncs_misc_request(client, seed_data, teacher_token, db_session):
    """杂项申请 → category=misc（时间列是 created_at，不是 submitted_at）。"""
    db_session.add(
        models.MiscRequest(
            student_id=seed_data["student"].id,
            kind="repair",
            subject="エアコン故障",
        )
    )
    db_session.commit()
    body = _feed(client, teacher_token)
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["category"] == "misc"
    assert "修繕" in item["body"]
    assert "エアコン故障" in item["body"]


def test_feed_syncs_dorm_event_proposal(client, seed_data, teacher_token, db_session):
    """行事企画申请 → category=dorm_event（学生外键是 proposer_id，状态列是 result）。"""
    db_session.add(
        models.DormEventProposal(
            proposer_id=seed_data["student"].id,
            title="夏祭り企画",
            held_at=datetime(2026, 8, 1, 18, 0, tzinfo=timezone.utc),
            place="食堂",
            expected_count=50,
            target="全寮生",
            purpose="交流",
            content="屋台と花火",
            risk_solution="消火器準備",
            expected_cost="3万円",
        )
    )
    db_session.commit()
    body = _feed(client, teacher_token)
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["category"] == "dorm_event"
    assert "夏祭り企画" in item["body"]
    assert item["related_student_id"] == str(seed_data["student"].id)


def test_insert_skip_conflicts_dedup(db_session, seed_data):
    """并发兜底：用同一 (source_table, source_id) 插第二条通知应被跳过、不抛错、不重复。

    模拟两个请求竞争同一未同步源行的场景：第一条已落库，第二条撞 uq_notif_source。
    _insert_skip_conflicts 应靠 savepoint 跳过它而不是冒泡成 IntegrityError/500。
    """
    from app.routers import notifications as notif_mod

    sid = uuid.uuid4()
    now = datetime(2026, 6, 14, 20, 0, tzinfo=timezone.utc)
    n1 = models.Notification(
        category="demerit",
        source_table="demerit_event",
        source_id=sid,
        title="t1",
        body="b1",
        is_demo=False,
        event_at=now,
    )
    db_session.add(n1)
    db_session.commit()

    n2 = models.Notification(
        category="demerit",
        source_table="demerit_event",
        source_id=sid,  # 同源 → 撞唯一约束
        title="t2",
        body="b2",
        is_demo=False,
        event_at=now,
    )
    notif_mod._insert_skip_conflicts(db_session, [n2])  # 不应抛错
    db_session.commit()

    cnt = (
        db_session.query(models.Notification)
        .filter(models.Notification.source_id == sid)
        .count()
    )
    assert cnt == 1  # 第二条被跳过，没重复


def test_insert_skip_conflicts_reraises_other_integrity(db_session, seed_data):
    """codex ②：非 uq_notif_source 的完整性错误不能被吞，要重新抛出。

    构造一条 category=None（违反 NOT NULL）的通知，_insert_skip_conflicts 应让它
    抛出 IntegrityError 而不是静默跳过（否则会掩盖外键/非空/check 类真 bug）。
    """
    from app.routers import notifications as notif_mod

    bad = models.Notification(
        category=None,  # 违反 NOT NULL → 期望被重新抛出
        source_table="x",
        source_id=uuid.uuid4(),
        title="t",
        body="b",
        is_demo=False,
        event_at=datetime(2026, 6, 14, 20, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(IntegrityError):
        notif_mod._insert_skip_conflicts(db_session, [bad])
    db_session.rollback()
