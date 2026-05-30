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


# ---------------------------------------------------------------
# 6. #1 blocker — token 归属转移不撞唯一约束
# ---------------------------------------------------------------
def test_device_token_ownership_transfer(client, _engine):
    """同一 token 从学生 A 转给学生 B，upsert 复用行，不撞 UniqueConstraint。"""
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=_engine)
    TOKEN = "shared-device-token-transfer-test"

    # 创建两个学生
    with Session() as s:
        student_a = models.Student(
            grade_code="09",
            class_code="01",
            seat_no="01",
            name="学生A",
            gender="male",
            room_no="M901",
            dorm_unit=1,
            is_overseas=False,
        )
        student_b = models.Student(
            grade_code="09",
            class_code="01",
            seat_no="02",
            name="学生B",
            gender="male",
            room_no="M902",
            dorm_unit=1,
            is_overseas=False,
        )
        s.add_all([student_a, student_b])
        s.flush()
        s.add(
            models.Account(
                student_id=student_a.id, password_hash=security.hash_password("pass_a")
            )
        )
        s.add(
            models.Account(
                student_id=student_b.id, password_hash=security.hash_password("pass_b")
            )
        )
        s.commit()
        jwt_a = security.create_access_token(student_a.id, "student")
        jwt_b = security.create_access_token(student_b.id, "student")
        sid_b = student_b.id

    # 学生 A 注册 token
    r1 = client.post(
        "/api/v1/notifications/device-token",
        json={"platform": "ios", "token": TOKEN},
        headers={"Authorization": f"Bearer {jwt_a}"},
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["created"] is True

    # 学生 B 用同一 token 注册 — 应该成功而不是 409/500
    r2 = client.post(
        "/api/v1/notifications/device-token",
        json={"platform": "ios", "token": TOKEN},
        headers={"Authorization": f"Bearer {jwt_b}"},
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    # 归属已转移给 B
    assert str(body["student_id"]) == str(sid_b)


# ---------------------------------------------------------------
# 7. #1 blocker — 撤销过的 token 重新注册不报 500（复活旧行）
# ---------------------------------------------------------------
def test_revoked_token_reregister_200(client, _engine):
    """学生的 token 被 revoke 后再次注册，应返回 200 而非约束错误 500。"""
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=_engine)
    TOKEN = "revoked-token-reregister-test-001"

    with Session() as s:
        student, jwt = _make_student(s)
        # 直接在 DB 插一条已 revoke 的 token 行
        dt = models.DeviceToken(
            id=uuid.uuid4(),
            student_id=student.id,
            platform="ios",
            token=TOKEN,
            revoked_at=datetime.now(timezone.utc),  # 已撤销
        )
        s.add(dt)
        s.commit()

    # 重新注册同一 token — 修复前会撞 UniqueConstraint → 500，修复后应 200
    res = client.post(
        "/api/v1/notifications/device-token",
        json={"platform": "ios", "token": TOKEN},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    # revoked_at 已被清空（复活），platform 正确
    assert body["platform"] == "ios"
