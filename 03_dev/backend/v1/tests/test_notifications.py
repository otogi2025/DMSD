"""老师通知中心 阶段1 端点测试 — feed 同步 / 幂等 / 已读 / 全部已读 / 鉴权。

通知由 routers/notifications.py 取 feed 时扫现有事件表（扣分等）同步生成，
本测试用扣分事件（DemeritEvent）当来源验证整条链路。
"""

from __future__ import annotations

import uuid

from app import models


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
