"""推送通知骨架测试 — spec §7.13。

覆盖：
  1. 令牌注册成功 (created=True)
  2. 同一 token 再次注册 → 幂等 (created=False)
  3. 未鉴权 → 401
  4. send_push 无 provider 时 status='skipped_no_provider'
"""

from __future__ import annotations

import uuid


from app import models, security
from app.services import push as push_svc


# ---------------------------------------------------------------
# helpers
# ---------------------------------------------------------------
def _make_student(db_session):
    """创建一个最小学生 + account，返回 (student, token)。"""
    student = models.Student(
        grade_code="01",
        class_code="01",
        seat_no="01",
        name="テスト太郎",
        gender="male",
        room_no="M201",
        dorm_unit=1,
        is_overseas=False,
    )
    db_session.add(student)
    db_session.flush()
    db_session.add(
        models.Account(
            student_id=student.id,
            password_hash=security.hash_password("testpass123"),
        )
    )
    db_session.commit()
    jwt = security.create_access_token(student.id, "student")
    return student, jwt


# ---------------------------------------------------------------
# 1. 令牌注册成功
# ---------------------------------------------------------------
def test_register_device_token_created(client, _engine):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=_engine)
    with Session() as s:
        student, jwt = _make_student(s)

    res = client.post(
        "/api/v1/notifications/device-token",
        json={"platform": "ios", "token": "abc-device-token-ios-001"},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["created"] is True
    assert body["platform"] == "ios"
    assert "id" in body


# ---------------------------------------------------------------
# 2. 同一 token 幂等 → created=False
# ---------------------------------------------------------------
def test_register_device_token_idempotent(client, _engine):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=_engine)
    with Session() as s:
        student, jwt = _make_student(s)

    token_str = "abc-device-token-android-002"
    for i in range(2):
        res = client.post(
            "/api/v1/notifications/device-token",
            json={"platform": "android", "token": token_str},
            headers={"Authorization": f"Bearer {jwt}"},
        )
        assert res.status_code == 200, res.text

    body = res.json()
    assert body["created"] is False  # 第 2 次应该是幂等更新


# ---------------------------------------------------------------
# 3. 未鉴权 → 401
# ---------------------------------------------------------------
def test_register_device_token_401(client):
    res = client.post(
        "/api/v1/notifications/device-token",
        json={"platform": "ios", "token": "some-token"},
    )
    assert res.status_code == 401


# ---------------------------------------------------------------
# 4. send_push 无 provider → skipped_no_provider
# ---------------------------------------------------------------
def test_send_push_no_provider(db_session):
    """凭证未配置时 notification_log.status = 'skipped_no_provider'，不 raise。"""
    student = models.Student(
        grade_code="02",
        class_code="01",
        seat_no="01",
        name="プッシュ花子",
        gender="female",
        room_no="W101",
        dorm_unit=4,
        is_overseas=False,
    )
    db_session.add(student)
    db_session.flush()

    # 先给学生注册一个 device_token
    dt = models.DeviceToken(
        id=uuid.uuid4(),
        student_id=student.id,
        platform="ios",
        token="test-push-token-no-provider",
    )
    db_session.add(dt)
    db_session.flush()

    logs = push_svc.send_push(
        db_session,
        student_id=student.id,
        title="テスト通知",
        body="これはテストです",
        template_key="test",
    )

    # dev 环境没有 APNS_KEY → skipped_no_provider（不是 failed，不 raise）
    assert len(logs) == 1
    log = logs[0]
    assert log.channel == "push"
    assert log.status == "skipped_no_provider"
    assert log.attempts == 1
    assert log.last_error is not None


# ---------------------------------------------------------------
# 5. send_push 学生无设备 → 返回空列表
# ---------------------------------------------------------------
def test_send_push_no_devices(db_session):
    student = models.Student(
        grade_code="03",
        class_code="01",
        seat_no="01",
        name="デバイスなし次郎",
        gender="male",
        room_no="M301",
        dorm_unit=1,
        is_overseas=False,
    )
    db_session.add(student)
    db_session.flush()

    logs = push_svc.send_push(
        db_session,
        student_id=student.id,
        title="通知",
        body="本文",
    )
    assert logs == []
