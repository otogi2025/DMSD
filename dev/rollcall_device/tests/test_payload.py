"""ST25DV 邮箱载荷解析测试（契约 §7）—— 34 字节合法 / 非法。"""

import uuid

import pytest

from src.nfc.payload import (
    CHECKIN_TYPE_EVENING,
    CHECKIN_TYPE_ROLLCALL,
    PayloadError,
    build_mailbox_payload,
    parse_mailbox_payload,
)


def test_parse_valid_34_bytes_roundtrip():
    sid = str(uuid.uuid4())
    idem = str(uuid.uuid4())
    raw = build_mailbox_payload(sid, idem, CHECKIN_TYPE_ROLLCALL)
    assert len(raw) == 34
    parsed = parse_mailbox_payload(raw)
    assert parsed.version == 0x01
    assert parsed.checkin_type == CHECKIN_TYPE_ROLLCALL
    assert parsed.student_id == sid
    assert parsed.idempotency_key == idem


def test_uuid_is_big_endian_rfc4122():
    # 手工摆 16 字节 → 应还原成对应 UUID（big-endian）
    sid_bytes = bytes(range(16))
    idem_bytes = bytes(range(16, 32))
    raw = bytearray(34)
    raw[0] = 0x01
    raw[1] = 0x01
    raw[2:18] = sid_bytes
    raw[18:34] = idem_bytes
    parsed = parse_mailbox_payload(bytes(raw))
    assert parsed.student_id == str(uuid.UUID(bytes=sid_bytes))
    assert parsed.idempotency_key == str(uuid.UUID(bytes=idem_bytes))


def test_evening_type_preserved():
    raw = build_mailbox_payload(
        str(uuid.uuid4()), str(uuid.uuid4()), CHECKIN_TYPE_EVENING
    )
    assert parse_mailbox_payload(raw).checkin_type == CHECKIN_TYPE_EVENING


def test_reject_wrong_length():
    with pytest.raises(PayloadError):
        parse_mailbox_payload(b"\x01\x01" + b"\x00" * 10)  # 12 字节


def test_reject_length_33_and_35():
    for n in (33, 35):
        body = bytearray(build_mailbox_payload(str(uuid.uuid4()), str(uuid.uuid4())))
        if n < 34:
            body = body[:n]
        else:
            body = body + b"\x00"
        with pytest.raises(PayloadError):
            parse_mailbox_payload(bytes(body))


def test_reject_wrong_version():
    raw = bytearray(build_mailbox_payload(str(uuid.uuid4()), str(uuid.uuid4())))
    raw[0] = 0x02  # 版本非 0x01
    with pytest.raises(PayloadError):
        parse_mailbox_payload(bytes(raw))
