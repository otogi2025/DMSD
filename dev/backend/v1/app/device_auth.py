"""点呼机（device）身份认证 ヘルパー — Ed25519 验签 + 激活码哈希。

Device_Contract §2 落地：
- enroll（激活）：管理员创建设备时后端生成一次性激活码明文（只返回一次），库里只存其
  SHA-256 哈希；设备首启带激活码 + 自生成的 Ed25519 公钥来换取「已激活」状态。
- token（令牌换取）：设备用私钥对 "{device_id}\n{ts}\n{nonce}" 签名，后端用存的公钥验签，
  通过后签发 12 小时 role="device" 的 JWT。

设备私钥永不出设备、后端不保存。cryptography 库来自 python-jose[cryptography] 依赖链
（requirements.txt 已显式声明 cryptography，见该文件说明）。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


# ---------------------------------------------------------------
# 激活码（enroll_code）
# ---------------------------------------------------------------
def generate_enroll_code() -> str:
    """生成一次性激活码明文（URL-safe，约 32 字符高熵随机串）。"""
    return secrets.token_urlsafe(24)


def hash_enroll_code(code: str) -> str:
    """激活码 → SHA-256 十六进制哈希（库里只存哈希）。

    激活码是高熵随机串，SHA-256 足够（同教师招待令牌口径），不需要 bcrypt 慢哈希。
    """
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_enroll_code(code: str, hashed: str | None) -> bool:
    """常数时间比较激活码明文与存的哈希。哈希为空（无待激活）一律 False。"""
    if not hashed:
        return False
    return hmac.compare_digest(hash_enroll_code(code), hashed)


# ---------------------------------------------------------------
# Ed25519 公钥 / 验签
# ---------------------------------------------------------------
def is_valid_ed25519_pubkey(public_key_b64: str) -> bool:
    """校验 base64 公钥能解码成恰好 32 字节（Ed25519 原始公钥长度）。"""
    try:
        raw = base64.b64decode(public_key_b64, validate=True)
    except (ValueError, TypeError):
        return False
    return len(raw) == 32


def verify_ed25519(
    public_key_b64: str | None, message: str, signature_b64: str
) -> bool:
    """用存的 base64 公钥验证对 message（UTF-8）的 base64 Ed25519 签名。

    任何解析 / 长度 / 验签失败一律返回 False（不区分原因、不抛异常）——
    调用方据此统一返回 INVALID_SIGNATURE，不泄露失败细节。
    """
    if not public_key_b64:
        return False
    try:
        pub_raw = base64.b64decode(public_key_b64, validate=True)
        sig = base64.b64decode(signature_b64, validate=True)
        pk = Ed25519PublicKey.from_public_bytes(pub_raw)
        pk.verify(sig, message.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


__all__ = [
    "generate_enroll_code",
    "hash_enroll_code",
    "verify_enroll_code",
    "is_valid_ed25519_pubkey",
    "verify_ed25519",
]
