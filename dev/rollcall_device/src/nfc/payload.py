"""ST25DV Mailbox 载荷解析（路径 B，契约 §7）。

载荷格式（总长恒 34 字节，逐字节对齐契约 §7 表 + iOS `ST25DVWriter.swift` 写入端）：

| 偏移 | 长度 | 内容 |
|---|---|---|
| 0 | 1 | 格式版本 = 0x01 |
| 1 | 1 | 签到类型：0x01 = 点呼 / 0x02 = 晚自习（v1.1）|
| 2 | 16 | student_id UUID 原始 16 字节（RFC 4122 big-endian 字节序）|
| 18 | 16 | idempotency_key UUID 原始 16 字节 |

校验规则：长度必须 = 34 且版本必须 = 0x01，不符即丢弃（调用方记日志、不上报）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

# 载荷常量（契约 §7）
PAYLOAD_LEN = 34
PAYLOAD_VERSION = 0x01
CHECKIN_TYPE_ROLLCALL = 0x01  # 点呼
CHECKIN_TYPE_EVENING = 0x02  # 晚自习（v1.1 预留）


class PayloadError(ValueError):
    """载荷长度 / 版本不合法时抛出。"""


@dataclass(frozen=True)
class MailboxPayload:
    """解析后的邮箱载荷。"""

    version: int
    checkin_type: int
    student_id: str  # UUID 标准字符串（带连字符）
    idempotency_key: str


def parse_mailbox_payload(raw: bytes) -> MailboxPayload:
    """把 34 字节原始载荷解析成 `MailboxPayload`。

    非法长度 / 非法版本 → 抛 `PayloadError`。
    UUID 用 big-endian（RFC 4122）字节序还原 —— Python 的 `uuid.UUID(bytes=...)` 正是
    big-endian，与契约 §7「两个 UUID big-endian」一致。
    """
    if len(raw) != PAYLOAD_LEN:
        raise PayloadError(f"载荷长度必须为 {PAYLOAD_LEN} 字节，实际 {len(raw)}")
    version = raw[0]
    if version != PAYLOAD_VERSION:
        raise PayloadError(f"载荷版本必须为 0x01，实际 0x{version:02x}")
    checkin_type = raw[1]
    student_id = str(uuid.UUID(bytes=bytes(raw[2:18])))
    idempotency_key = str(uuid.UUID(bytes=bytes(raw[18:34])))
    return MailboxPayload(
        version=version,
        checkin_type=checkin_type,
        student_id=student_id,
        idempotency_key=idempotency_key,
    )


def build_mailbox_payload(
    student_id: str,
    idempotency_key: str,
    checkin_type: int = CHECKIN_TYPE_ROLLCALL,
) -> bytes:
    """构造 34 字节载荷（供测试 / --simulate 模拟手机写入用，与写入端逻辑对称）。"""
    body = bytearray(PAYLOAD_LEN)
    body[0] = PAYLOAD_VERSION
    body[1] = checkin_type
    body[2:18] = uuid.UUID(student_id).bytes
    body[18:34] = uuid.UUID(idempotency_key).bytes
    return bytes(body)
