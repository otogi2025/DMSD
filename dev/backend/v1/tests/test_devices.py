"""点呼机接入（device）端点测试 — Device_Contract §2/§4/§5 全流程。

覆盖：
- 设备管理（创建返回一次性激活码 / 列表 / toggle active / 永久注销后禁再激活）
- enroll + token 全流程（真生成 Ed25519 键对签名）
- 令牌错误路径（坏签名 / 过期 ts / nonce 重放 / 未激活 / 已注销）
- 绑卡 + 作废 + 作废后重新绑定
- device-checkins 路径 A + B / 迟到无截止（7-17 拍板）/ swipe_time 未来钳制 / 离线补传早于 now
- 结算后补传覆盖 + teacher_override 优先
- roster 排除演示学生
- 权限边界（学生/老师令牌调设备端点被拒；设备令牌调老师端点被拒）

跑：cd dev/backend/v1 && .venv/bin/python -m pytest tests/test_devices.py -v
"""

from __future__ import annotations

import base64
import secrets
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app import models

_JST = ZoneInfo("Asia/Tokyo")


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_ed25519() -> tuple[Ed25519PrivateKey, str]:
    priv = Ed25519PrivateKey.generate()
    pub_raw = priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return priv, base64.b64encode(pub_raw).decode()


def _sign(priv: Ed25519PrivateKey, message: str) -> str:
    return base64.b64encode(priv.sign(message.encode("utf-8"))).decode()


# ---------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------
def _create_device(client, teacher_token, device_id="dorm-1-01", device_type="hybrid"):
    res = client.post(
        "/api/v1/devices",
        json={
            "device_id": device_id,
            "device_type": device_type,
            "device_location": "1寮入口",
            "device_notes": "RPi 3A+",
        },
        headers=_h(teacher_token),
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]


@pytest.fixture
def enrolled_device(client, teacher_token):
    """创建 + 激活一台设备，返回 {device_id, priv, pub_b64}。"""
    data = _create_device(client, teacher_token)
    device_id = data["device_id"]
    enroll_code = data["enroll_code"]
    priv, pub_b64 = _make_ed25519()
    res = client.post(
        f"/api/v1/devices/{device_id}/enroll",
        json={"enroll_code": enroll_code, "public_key": pub_b64},
    )
    assert res.status_code == 200, res.text
    return {"device_id": device_id, "priv": priv, "pub_b64": pub_b64}


def _get_device_token(client, device_id, priv):
    ts = datetime.now(timezone.utc).isoformat()
    nonce = secrets.token_hex(16)
    msg = f"{device_id}\n{ts}\n{nonce}"
    res = client.post(
        f"/api/v1/devices/{device_id}/token",
        json={"ts": ts, "nonce": nonce, "signature": _sign(priv, msg)},
    )
    return res


@pytest.fixture
def device_token(client, enrolled_device):
    res = _get_device_token(
        client, enrolled_device["device_id"], enrolled_device["priv"]
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def _make_running_session(db_session, *, dorm_set=None, on_time_offset_min=10):
    now = datetime.now(_JST)
    session = models.RollCallSession(
        dorm_unit_set=dorm_set if dorm_set is not None else [1, 2],
        session_type="evening",
        day_type="weekday",
        session_status="running",
        started_at=now,
        scheduled_window_start_at=now - timedelta(minutes=30),
        scheduled_on_time_end_at=now + timedelta(minutes=on_time_offset_min),
        scheduled_late_end_at=now + timedelta(minutes=on_time_offset_min + 20),
        scheduled_auto_end_at=now + timedelta(minutes=on_time_offset_min + 30),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


# ===============================================================
# 设备管理
# ===============================================================
class TestDeviceManagement:
    def test_create_requires_teacher_manage(self, client, student_token):
        """学生令牌创建设备 → 403。"""
        res = client.post(
            "/api/v1/devices",
            json={
                "device_id": "d1",
                "device_type": "hybrid",
                "device_location": "x",
            },
            headers=_h(student_token),
        )
        assert res.status_code == 403, res.text

    def test_create_no_token_401(self, client):
        res = client.post(
            "/api/v1/devices",
            json={"device_id": "d1", "device_type": "hybrid", "device_location": "x"},
        )
        assert res.status_code == 401, res.text

    def test_create_returns_enroll_code_once(self, client, teacher_token):
        data = _create_device(client, teacher_token)
        assert data["device_id"] == "dorm-1-01"
        assert data["enroll_code"]
        assert data["device_active"] is True
        # 列表不含激活码
        res = client.get("/api/v1/devices", headers=_h(teacher_token))
        assert res.status_code == 200
        row = res.json()["data"][0]
        assert "enroll_code" not in row
        assert row["device_id"] == "dorm-1-01"

    def test_duplicate_device_id_409(self, client, teacher_token):
        _create_device(client, teacher_token)
        res = client.post(
            "/api/v1/devices",
            json={
                "device_id": "dorm-1-01",
                "device_type": "hybrid",
                "device_location": "x",
            },
            headers=_h(teacher_token),
        )
        assert res.status_code == 409, res.text

    def test_demo_teacher_cannot_create(self, client, db_session, seed_data):
        """演示老师不能创建真实设备 → 403 DEMO_FORBIDDEN。"""
        from app import security

        demo_t = models.Teacher(
            login_id="demo_admin",
            name="デモ管理",
            email="da@test.jp",
            password_hash=security.hash_password("test-password-12345"),
            role="寮務課長",
            is_demo=True,
        )
        db_session.add(demo_t)
        db_session.commit()
        login = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "demo_admin", "password": "test-password-12345"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["data"]["access_token"]
        res = client.post(
            "/api/v1/devices",
            json={"device_id": "d9", "device_type": "hybrid", "device_location": "x"},
            headers=_h(token),
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "DEMO_FORBIDDEN"

    def test_toggle_active(self, client, teacher_token):
        _create_device(client, teacher_token)
        res = client.patch(
            "/api/v1/devices/dorm-1-01",
            json={"device_active": False},
            headers=_h(teacher_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["device_active"] is False

    def test_retire_then_cannot_reactivate(self, client, teacher_token):
        _create_device(client, teacher_token)
        # 永久注销
        res = client.patch(
            "/api/v1/devices/dorm-1-01",
            json={"retire": True},
            headers=_h(teacher_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["device_active"] is False
        assert res.json()["data"]["retired_at"] is not None
        # 注销后禁止再激活
        res2 = client.patch(
            "/api/v1/devices/dorm-1-01",
            json={"device_active": True},
            headers=_h(teacher_token),
        )
        assert res2.status_code == 409, res2.text
        assert res2.json()["error"]["code"] == "DEVICE_RETIRED"


# ===============================================================
# enroll + token
# ===============================================================
class TestEnrollToken:
    def test_full_flow(self, client, device_token):
        """create → enroll → token 全流程成功（device_token fixture 已跑完）。"""
        assert device_token

    def test_enroll_wrong_code(self, client, teacher_token):
        _create_device(client, teacher_token)
        _, pub_b64 = _make_ed25519()
        res = client.post(
            "/api/v1/devices/dorm-1-01/enroll",
            json={"enroll_code": "wrong-code", "public_key": pub_b64},
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "INVALID_INPUT"

    def test_enroll_twice_rejected(self, client, enrolled_device):
        _, pub_b64 = _make_ed25519()
        res = client.post(
            f"/api/v1/devices/{enrolled_device['device_id']}/enroll",
            json={"enroll_code": "any", "public_key": pub_b64},
        )
        assert res.status_code == 422, res.text

    def test_enroll_bad_pubkey(self, client, teacher_token):
        data = _create_device(client, teacher_token)
        res = client.post(
            "/api/v1/devices/dorm-1-01/enroll",
            json={"enroll_code": data["enroll_code"], "public_key": "not-base64!!"},
        )
        assert res.status_code == 422, res.text

    def test_token_bad_signature(self, client, enrolled_device):
        device_id = enrolled_device["device_id"]
        ts = datetime.now(timezone.utc).isoformat()
        nonce = secrets.token_hex(16)
        # 对错误消息签名 → 验签失败
        bad_sig = _sign(enrolled_device["priv"], "totally-different-message")
        res = client.post(
            f"/api/v1/devices/{device_id}/token",
            json={"ts": ts, "nonce": nonce, "signature": bad_sig},
        )
        assert res.status_code == 401, res.text
        assert res.json()["error"]["code"] == "INVALID_SIGNATURE"

    def test_token_expired_ts(self, client, enrolled_device):
        device_id = enrolled_device["device_id"]
        ts = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
        nonce = secrets.token_hex(16)
        sig = _sign(enrolled_device["priv"], f"{device_id}\n{ts}\n{nonce}")
        res = client.post(
            f"/api/v1/devices/{device_id}/token",
            json={"ts": ts, "nonce": nonce, "signature": sig},
        )
        assert res.status_code == 401, res.text
        assert res.json()["error"]["code"] == "INVALID_SIGNATURE"
        assert res.json()["error"]["detail"].get("reason") == "ts_expired"

    def test_token_nonce_replay(self, client, enrolled_device):
        device_id = enrolled_device["device_id"]
        ts = datetime.now(timezone.utc).isoformat()
        nonce = secrets.token_hex(16)
        sig = _sign(enrolled_device["priv"], f"{device_id}\n{ts}\n{nonce}")
        body = {"ts": ts, "nonce": nonce, "signature": sig}
        r1 = client.post(f"/api/v1/devices/{device_id}/token", json=body)
        assert r1.status_code == 200, r1.text
        # 同 nonce 重放 → 401 nonce_replay
        r2 = client.post(f"/api/v1/devices/{device_id}/token", json=body)
        assert r2.status_code == 401, r2.text
        assert r2.json()["error"]["detail"].get("reason") == "nonce_replay"

    def test_token_unenrolled_device(self, client, teacher_token):
        """未激活设备（无公钥）换令牌 → 403 DEVICE_NOT_ACTIVE。"""
        _create_device(client, teacher_token, device_id="dorm-2-01")
        priv, _ = _make_ed25519()
        res = _get_device_token(client, "dorm-2-01", priv)
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "DEVICE_NOT_ACTIVE"

    def test_token_retired_device(self, client, teacher_token, enrolled_device):
        device_id = enrolled_device["device_id"]
        client.patch(
            f"/api/v1/devices/{device_id}",
            json={"retire": True},
            headers=_h(teacher_token),
        )
        res = _get_device_token(client, device_id, enrolled_device["priv"])
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "DEVICE_NOT_ACTIVE"


# ===============================================================
# 权限边界
# ===============================================================
class TestAuthBoundary:
    def test_device_token_cannot_call_teacher_endpoint(self, client, device_token):
        res = client.get("/api/v1/rollcall/today/sessions", headers=_h(device_token))
        assert res.status_code == 403, res.text

    def test_teacher_token_cannot_call_device_endpoint(self, client, teacher_token):
        res = client.get("/api/v1/devices/me/roster", headers=_h(teacher_token))
        assert res.status_code == 403, res.text

    def test_student_token_cannot_call_device_endpoint(self, client, student_token):
        res = client.get("/api/v1/devices/me/roster", headers=_h(student_token))
        assert res.status_code == 403, res.text

    def test_device_token_cannot_manage_devices(self, client, device_token):
        res = client.post(
            "/api/v1/devices",
            json={"device_id": "x", "device_type": "hybrid", "device_location": "y"},
            headers=_h(device_token),
        )
        assert res.status_code == 403, res.text


# ===============================================================
# 绑卡
# ===============================================================
class TestCards:
    def test_bind_card(self, client, teacher_token, seed_data):
        sid = str(seed_data["student"].id)
        res = client.post(
            "/api/v1/cards",
            json={"card_uid": "0123456789abcd", "student_id": sid},
            headers=_h(teacher_token),
        )
        assert res.status_code == 201, res.text
        assert res.json()["data"]["card_active"] is True

    def test_bind_invalid_uid(self, client, teacher_token, seed_data):
        sid = str(seed_data["student"].id)
        res = client.post(
            "/api/v1/cards",
            json={"card_uid": "ZZZ", "student_id": sid},
            headers=_h(teacher_token),
        )
        assert res.status_code == 422, res.text

    def test_bind_duplicate_active_409(self, client, teacher_token, seed_data):
        sid = str(seed_data["student"].id)
        body = {"card_uid": "0123456789abcd", "student_id": sid}
        r1 = client.post("/api/v1/cards", json=body, headers=_h(teacher_token))
        assert r1.status_code == 201
        r2 = client.post("/api/v1/cards", json=body, headers=_h(teacher_token))
        assert r2.status_code == 409, r2.text
        assert r2.json()["error"]["code"] == "CARD_ALREADY_BOUND"

    def test_revoke_then_rebind(self, client, teacher_token, seed_data, db_session):
        sid = str(seed_data["student"].id)
        client.post(
            "/api/v1/cards",
            json={"card_uid": "0123456789abcd", "student_id": sid},
            headers=_h(teacher_token),
        )
        # 作废
        rev = client.delete("/api/v1/cards/0123456789abcd", headers=_h(teacher_token))
        assert rev.status_code == 200, rev.text
        assert rev.json()["data"]["card_active"] is False
        # 作废后同 UID 可重新绑定（给同一学生也可）
        again = client.post(
            "/api/v1/cards",
            json={"card_uid": "0123456789abcd", "student_id": sid},
            headers=_h(teacher_token),
        )
        assert again.status_code == 201, again.text

    def test_list_cards_by_student(self, client, teacher_token, seed_data):
        sid = str(seed_data["student"].id)
        client.post(
            "/api/v1/cards",
            json={"card_uid": "0123456789abcd", "student_id": sid},
            headers=_h(teacher_token),
        )
        res = client.get(f"/api/v1/cards?student_id={sid}", headers=_h(teacher_token))
        assert res.status_code == 200, res.text
        assert len(res.json()["data"]) == 1


# ===============================================================
# device-checkins
# ===============================================================
class TestDeviceCheckin:
    def test_path_b_present(self, client, device_token, seed_data, db_session):
        _make_running_session(db_session, on_time_offset_min=10)
        sid = str(seed_data["student"].id)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": sid,
                "idempotency_key": "11111111-1111-1111-1111-111111111111",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["base_status"] == "present"
        assert data["duplicate"] is False
        assert data["student_number"] == seed_data["student"].student_no
        assert data["led"] == "green"

    def test_path_a_present(self, client, device_token, seed_data, db_session):
        _make_running_session(db_session, on_time_offset_min=10)
        db_session.add(
            models.NfcCard(
                card_uid="0123456789abcd", student_id=seed_data["student"].id
            )
        )
        db_session.commit()
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "A",
                "card_uid": "0123456789ABCD",  # 大写也应归一
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["base_status"] == "present"

    def test_path_a_unknown_card(self, client, device_token, seed_data, db_session):
        _make_running_session(db_session, on_time_offset_min=10)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "A",
                "card_uid": "ffffffffffffff",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "UNKNOWN_CARD"

    def test_path_a_revoked_card_unregistered(
        self, client, device_token, seed_data, db_session
    ):
        _make_running_session(db_session, on_time_offset_min=10)
        db_session.add(
            models.NfcCard(
                card_uid="0123456789abcd",
                student_id=seed_data["student"].id,
                card_active=False,
                revoked_at=datetime.now(timezone.utc),
            )
        )
        db_session.commit()
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "A",
                "card_uid": "0123456789abcd",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "UNREGISTERED_UID"

    def test_demo_student_rejected(self, client, device_token, db_session):
        _make_running_session(db_session, dorm_set=[1, 2], on_time_offset_min=10)
        demo = models.Student(
            grade_code="06",
            class_code="02",
            seat_no="77",
            name="デモ",
            gender="male",
            room_no="M177",
            dorm_unit=1,
            is_demo=True,
        )
        db_session.add(demo)
        db_session.commit()
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(demo.id),
                "idempotency_key": "22222222-2222-2222-2222-222222222222",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "UNREGISTERED_UID"

    def test_no_running_session(self, client, device_token, seed_data):
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "33333333-3333-3333-3333-333333333333",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "SESSION_NOT_RUNNING"

    def test_late(self, client, device_token, seed_data, db_session):
        """on_time 已过 3 分钟 → late。"""
        _make_running_session(db_session, on_time_offset_min=-3)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "44444444-4444-4444-4444-444444444444",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["base_status"] == "late"

    def test_late_has_no_deadline_while_running(
        self, client, device_token, seed_data, db_session
    ):
        """7-17 拍板「迟到无截止」：准时截止后很久、只要场次还 running → late（不再有 TIMEOUT）。"""
        # on_time 已过 40 分钟、场次仍 running → late（旧语义此处是 TIMEOUT，已废）
        _make_running_session(db_session, on_time_offset_min=-40)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "55555555-5555-5555-5555-555555555555",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["base_status"] == "late"

    def test_idempotency_same_key_duplicate(
        self, client, device_token, seed_data, db_session
    ):
        _make_running_session(db_session, on_time_offset_min=10)
        body = {
            "path_type": "B",
            "student_id": str(seed_data["student"].id),
            "idempotency_key": "66666666-6666-6666-6666-666666666666",
            "swipe_time": datetime.now(_JST).isoformat(),
        }
        r1 = client.post(
            "/api/v1/rollcall/device-checkins", json=body, headers=_h(device_token)
        )
        assert r1.status_code == 200, r1.text
        assert r1.json()["data"]["duplicate"] is False
        r2 = client.post(
            "/api/v1/rollcall/device-checkins", json=body, headers=_h(device_token)
        )
        assert r2.status_code == 200, r2.text
        assert r2.json()["data"]["duplicate"] is True

    def test_future_swipe_clamped_to_present(
        self, client, device_token, seed_data, db_session
    ):
        """swipe_time 远超未来（超 30 秒）→ 钳制为 server_now → 仍按当前窗判定（present）。"""
        _make_running_session(db_session, on_time_offset_min=10)
        forged = datetime.now(_JST) + timedelta(days=1)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "77777777-7777-7777-7777-777777777777",
                "swipe_time": forged.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        # 未来时刻被钳制 → server_now 落在 on_time 窗内 → present（伪造未来时刻不获利）
        assert res.json()["data"]["base_status"] == "present"

    def test_offline_replay_earlier_than_now(
        self, client, device_token, seed_data, db_session
    ):
        """离线补传：swipe_time 早于 now、落在准时窗内 → present（按 swipe 判定）。"""
        # on_time 在 5 分钟后；swipe = now - 10 分钟仍 ≤ on_time_end → present
        session = _make_running_session(db_session, on_time_offset_min=5)
        swipe = datetime.now(_JST) - timedelta(minutes=10)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "88888888-8888-8888-8888-888888888888",
                "swipe_time": swipe.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["base_status"] == "present"
        assert res.json()["data"]["session_id"] == str(session.id)

    def test_settled_absent_replay_overrides_and_revokes_demerit(
        self, client, device_token, seed_data, db_session
    ):
        """结算后补传：学生已被 auto_settle 置 absent + 扣分 → 窗内补传覆盖为 present + 回退扣分。"""
        now = datetime.now(_JST)
        # 已结束场次，窗覆盖 swipe（swipe=now-15min 落在 [window_start, on_time_end]）
        session = models.RollCallSession(
            dorm_unit_set=[1, 2],
            session_type="evening",
            day_type="weekday",
            session_status="ended",
            started_at=now - timedelta(minutes=20),
            ended_at=now - timedelta(minutes=5),
            ended_source="system",
            scheduled_window_start_at=now - timedelta(minutes=20),
            scheduled_on_time_end_at=now - timedelta(minutes=10),
            scheduled_late_end_at=now - timedelta(minutes=9),
            scheduled_auto_end_at=now - timedelta(minutes=5),
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        sid = seed_data["student"].id
        # 模拟 auto_settle 的 absent 事件 + 扣分
        db_session.add(
            models.RollCallEvent(
                session_id=session.id,
                student_id=sid,
                base_status="absent",
                status_source="auto_settle",
                checked_in_at=now - timedelta(minutes=5),
            )
        )
        db_session.add(
            models.DemeritEvent(
                student_id=sid,
                source_type="rollcall_absent",
                source_event_id=session.id,
                points=1.0,
                reason="点呼欠席",
                month=now.strftime("%Y-%m"),
            )
        )
        db_session.commit()

        swipe = now - timedelta(
            minutes=15
        )  # 落在 window_start(now-20) ~ on_time_end(now-10)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(sid),
                "idempotency_key": "99999999-9999-9999-9999-999999999999",
                "swipe_time": swipe.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["base_status"] == "present"
        assert data["duplicate"] is False
        # 缺席扣分应被撤销
        db_session.expire_all()
        active_absent = (
            db_session.query(models.DemeritEvent)
            .filter(
                models.DemeritEvent.source_event_id == session.id,
                models.DemeritEvent.source_type == "rollcall_absent",
                models.DemeritEvent.revoked_at.is_(None),
            )
            .all()
        )
        assert len(active_absent) == 0, "结算后补传应回退缺席扣分"

    def test_teacher_override_priority(
        self, client, device_token, seed_data, db_session
    ):
        """已有老师改判 → 补传丢弃、返回 superseded_by_teacher=true，不新建事件。"""
        session = _make_running_session(db_session, on_time_offset_min=10)
        sid = seed_data["student"].id
        db_session.add(
            models.RollCallEvent(
                session_id=session.id,
                student_id=sid,
                base_status="present",
                status_source="teacher_override",
                checked_in_at=datetime.now(_JST),
                reason="教師確認",
            )
        )
        db_session.commit()
        before = (
            db_session.query(models.RollCallEvent)
            .filter(models.RollCallEvent.session_id == session.id)
            .count()
        )
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(sid),
                "idempotency_key": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["duplicate"] is True
        assert data["superseded_by_teacher"] is True
        db_session.expire_all()
        after = (
            db_session.query(models.RollCallEvent)
            .filter(models.RollCallEvent.session_id == session.id)
            .count()
        )
        assert after == before, "老师改判优先时不应新建补传事件"


# ===============================================================
# roster
# ===============================================================
class TestRoster:
    def test_roster_excludes_demo_and_includes_cards(
        self, client, device_token, seed_data, db_session
    ):
        # 给 seed 学生绑一张 active 卡
        db_session.add(
            models.NfcCard(
                card_uid="0123456789abcd", student_id=seed_data["student"].id
            )
        )
        # 造 demo 学生
        demo = models.Student(
            grade_code="06",
            class_code="02",
            seat_no="88",
            name="デモ",
            gender="male",
            room_no="M188",
            dorm_unit=1,
            is_demo=True,
        )
        db_session.add(demo)
        db_session.commit()

        res = client.get("/api/v1/devices/me/roster", headers=_h(device_token))
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        nums = {s["student_number"] for s in data["students"]}
        assert seed_data["student"].student_no in nums
        assert demo.student_no not in nums
        mine = next(
            s
            for s in data["students"]
            if s["student_number"] == seed_data["student"].student_no
        )
        assert "0123456789abcd" in mine["card_uids"]


# ===============================================================
# audio manifest（目录不存在返回空）
# ===============================================================
class TestAudioManifest:
    def test_manifest_empty_when_no_dir(self, client, device_token):
        res = client.get("/api/v1/devices/me/audio-manifest", headers=_h(device_token))
        assert res.status_code == 200, res.text
        # 默认音频目录不存在 → 空清单
        assert res.json()["data"]["files"] == []

    def test_audio_path_traversal_blocked(self, client, device_token):
        res = client.get(
            "/api/v1/devices/me/audio/..%2f..%2fetc%2fpasswd",
            headers=_h(device_token),
        )
        assert res.status_code == 404, res.text


# ===============================================================
# 场次自动保障后台任务（纯逻辑，不起 loop）
# ===============================================================
class TestScheduler:
    def test_day_type(self):
        from datetime import date

        from app.rollcall_scheduler import _day_type

        assert _day_type(date(2026, 7, 18)) == "weekend_holiday"  # 土曜
        assert _day_type(date(2026, 7, 19)) == "weekend_holiday"  # 日曜
        assert _day_type(date(2026, 7, 17)) == "weekday"  # 金曜

    def test_schedule_times_weekday_evening(self):
        from datetime import date

        from app.rollcall_scheduler import _schedule_times

        ws, ote, le, ae = _schedule_times(date(2026, 7, 17), "evening", "weekday", 15)
        assert ote.hour == 22 and ote.minute == 0
        assert ws == ote - timedelta(minutes=5)
        assert le == ote + timedelta(seconds=1)
        assert ae == ote + timedelta(minutes=15)

    def test_run_tick_creates_today_sessions_idempotent(self, _engine):
        """_run_tick 建当日 morning/evening 两场（dorm_unit_set=[1,2,4]）；重跑不重复建。"""
        from app.rollcall_scheduler import _run_tick

        _run_tick()
        _run_tick()  # 幂等

        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=_engine)
        with Session() as s:
            today = datetime.now(_JST).date()
            day_start = datetime(today.year, today.month, today.day, tzinfo=_JST)
            rows = (
                s.query(models.RollCallSession)
                .filter(models.RollCallSession.scheduled_window_start_at >= day_start)
                .all()
            )
        types = sorted(r.session_type for r in rows)
        assert types == ["evening", "morning"], f"应恰好两场，实际 {types}"
        for r in rows:
            assert r.dorm_unit_set == [1, 2, 4]


# ===============================================================
# 2026-07-18 cursor 审查发现的回归测试（blocker 1/2 + major 3/4/6/7）
# ===============================================================
class TestReviewRegressions:
    """每条对应一个审查发现，防这些坑以后被改回去。"""

    def test_replay_lands_on_ended_session_not_the_running_one(
        self, client, device_token, seed_data, db_session
    ):
        """blocker 1：早间场已 ended（学生被判 absent）+ 晚间场正 running 时，
        早间的离线补传必须回到早间那场，不能被记进晚间场。"""
        now = datetime.now(_JST)
        # 早间场：窗口 [now-5h, now-4h50m]，已结束
        morning = models.RollCallSession(
            dorm_unit_set=[1, 2],
            session_type="morning",
            day_type="weekday",
            session_status="ended",
            started_at=now - timedelta(hours=5),
            ended_at=now - timedelta(hours=4, minutes=50),
            ended_source="system",
            scheduled_window_start_at=now - timedelta(hours=5),
            scheduled_on_time_end_at=now - timedelta(hours=4, minutes=55),
            scheduled_late_end_at=now - timedelta(hours=4, minutes=54),
            scheduled_auto_end_at=now - timedelta(hours=4, minutes=50),
        )
        db_session.add(morning)
        db_session.commit()
        db_session.refresh(morning)
        # 晚间场正在跑
        evening = _make_running_session(db_session, on_time_offset_min=10)

        # 早间窗内的刷卡现在才补传上来
        swipe = now - timedelta(hours=4, minutes=58)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "aaaaaaa1-0000-0000-0000-000000000001",
                "swipe_time": swipe.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["session_id"] == str(morning.id), (
            f"补传应归早间场 {morning.id}，实际落到 {data['session_id']}"
            f"（晚间场是 {evening.id}）"
        )
        assert data["base_status"] == "present"

    def test_swipe_before_window_start_rejected(
        self, client, device_token, seed_data, db_session
    ):
        """major 3：swipe_time 早于场次 window_start（不属于任何场次的时间窗）→
        不能被记成该场的 present（RollCall_Spec §7 要求 window_start ≤ t）。"""
        _make_running_session(db_session, on_time_offset_min=10)  # window_start = now-30min
        swipe = datetime.now(_JST) - timedelta(hours=2)  # 远早于窗口下限
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "aaaaaaa1-0000-0000-0000-000000000002",
                "swipe_time": swipe.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "SESSION_NOT_RUNNING"

    def test_path_b_requires_idempotency_key(
        self, client, device_token, seed_data, db_session
    ):
        """major 4：路径 B 的 idempotency_key 是必填（契约 §4.1）。"""
        _make_running_session(db_session, on_time_offset_min=10)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "swipe_time": datetime.now(_JST).isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "INVALID_INPUT"

    def test_future_swipe_writes_audit_row(
        self, client, device_token, seed_data, db_session
    ):
        """major 6：未来 swipe_time 被钳制时要写审计（契约 §3）。"""
        _make_running_session(db_session, on_time_offset_min=10)
        forged = datetime.now(_JST) + timedelta(days=1)
        res = client.post(
            "/api/v1/rollcall/device-checkins",
            json={
                "path_type": "B",
                "student_id": str(seed_data["student"].id),
                "idempotency_key": "aaaaaaa1-0000-0000-0000-000000000003",
                "swipe_time": forged.isoformat(),
            },
            headers=_h(device_token),
        )
        assert res.status_code == 200, res.text
        rows = (
            db_session.query(models.AuditLog)
            .filter(models.AuditLog.action == "device.clock_skew_clamped")
            .all()
        )
        assert len(rows) == 1, f"应恰好一条时钟异常审计，实际 {len(rows)}"
        assert rows[0].payload["device_id"] == "dorm-1-01"
        assert rows[0].payload["skew_seconds"] > 0

    def test_old_token_dies_after_reset_enroll(
        self, client, teacher_token, device_token, seed_data, db_session
    ):
        """major 7：老师重发激活码作废旧公钥后，旧设备令牌必须当场失效，
        不能靠 12 小时自然过期（契约 §2.2）。"""
        _make_running_session(db_session, on_time_offset_min=10)
        # 重置前旧令牌可用
        ok = client.get("/api/v1/devices/me/roster", headers=_h(device_token))
        assert ok.status_code == 200, ok.text

        res = client.post(
            "/api/v1/devices/dorm-1-01/reset-enroll", headers=_h(teacher_token)
        )
        assert res.status_code == 200, res.text

        # 重置后同一个旧令牌应被拒
        dead = client.get("/api/v1/devices/me/roster", headers=_h(device_token))
        assert dead.status_code == 401, dead.text
        assert dead.json()["error"]["code"] == "INVALID_CREDENTIALS"
