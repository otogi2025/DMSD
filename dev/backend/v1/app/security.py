"""认证 ヘルパー — JWT + bcrypt。

- access_token: JWT HS256, 24h 期限
- password: bcrypt cost 12
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from .config import get_settings

# bcrypt は 72 バイト超で例外を出す → SHA256 で前段ハッシュして固定 32 バイト化
# (一般的なベストプラクティス。72 byte 超えのパスワードでも切り詰めなしで安全)
import hashlib

_BCRYPT_ROUNDS = 12


def _prep(plain: str) -> bytes:
    """bcrypt 入力前処理 — SHA256 → 32 バイト で 72 バイト制限回避。"""
    return hashlib.sha256(plain.encode("utf-8")).digest()


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(_prep(plain), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_prep(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str | UUID,
    role: str,
    *,
    extra: dict[str, Any] | None = None,
    expire_minutes: int | None = None,
) -> str:
    """JWT 生成。

    Args:
        subject: 主体 ID (学生 uuid or 教师 uuid を str 化したもの)
        role: 'student' | 'teacher:<role>' (例 'teacher:寮務部長')
        extra: 追加 claim (例 dorm_unit / is_overseas / assigned_dorm)
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(
        minutes=expire_minutes or settings.jwt_access_expire_min
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """JWT decode + 期限校验。失败時 JWTError raise。"""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "JWTError",
]
