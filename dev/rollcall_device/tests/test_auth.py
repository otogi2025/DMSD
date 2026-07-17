"""设备认证测试（契约 §2）—— 签名串 / 密钥文件权限 / 公钥格式 / 签名可验。"""

import base64
import os
import stat

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from src.api.auth import DeviceKey, build_token_signing_string


def test_signing_string_format():
    # 契约 §2.3：签名串 = "{device_id}\n{ts}\n{nonce}"
    s = build_token_signing_string("dorm-1-01", "2026-07-17T21:55:00+09:00", "deadbeef")
    assert s == "dorm-1-01\n2026-07-17T21:55:00+09:00\ndeadbeef"


def test_key_file_created_with_0600(tmp_path):
    key_path = tmp_path / "device_key"
    DeviceKey.load_or_create(key_path)
    assert key_path.exists()
    mode = stat.S_IMODE(os.stat(key_path).st_mode)
    assert mode == 0o600


def test_public_key_is_base64_raw_32_bytes(tmp_path):
    key = DeviceKey.load_or_create(tmp_path / "device_key")
    b64 = key.public_key_base64()
    raw = base64.b64decode(b64)
    assert len(raw) == 32  # Ed25519 原始公钥 32 字节


def test_load_existing_key_is_stable(tmp_path):
    path = tmp_path / "device_key"
    key1 = DeviceKey.load_or_create(path)
    key2 = DeviceKey.load_or_create(path)  # 第二次应加载同一把，不重新生成
    assert key1.public_key_base64() == key2.public_key_base64()


def test_signature_verifies_with_public_key(tmp_path):
    key = DeviceKey.load_or_create(tmp_path / "device_key")
    message = build_token_signing_string(
        "dorm-1-01", "2026-07-17T21:55:00+09:00", "abc123"
    )
    sig_b64 = key.sign_base64(message)
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(key.public_key_base64()))
    # verify 不抛异常即通过
    pub.verify(base64.b64decode(sig_b64), message.encode("utf-8"))
