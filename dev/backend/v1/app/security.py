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
            不得覆盖保留键；即使误传也会被下方强制写回抹掉。
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expire_minutes or settings.jwt_access_expire_min)
    # 本函数权威值（保留 claim）—— sub/role/iat/exp 一律由参数与本函数计算，
    # 禁止被 extra 覆盖（backend#21）。本函数不发 typ / token_type 等其它标准键。
    sub_claim = str(subject)
    role_claim = role
    iat_claim = int(now.timestamp())
    exp_claim = int(exp.timestamp())
    payload: dict[str, Any] = {
        "sub": sub_claim,
        "role": role_claim,
        "iat": iat_claim,
        "exp": exp_claim,
    }
    if extra:
        payload.update(extra)
        # 保留键强制写回：业务字段（dorm_unit / enr / name …）仍允许 extra 自由加
        payload["sub"] = sub_claim
        payload["role"] = role_claim
        payload["iat"] = iat_claim
        payload["exp"] = exp_claim
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """JWT decode + 期限校验。失败時 JWTError raise。

    options 显式要求 exp / sub claim 存在且校验过期：
    防御纵深 — 缺 exp 的 token（历史脚本 / 测试夹具 / 误签发）一律拒，不靠默认行为兜底。
    注：用的是 python-jose 的 require_exp / require_sub 布尔键写法
    （不是 PyJWT 的 options={"require": [...]} 列表写法 —— 那种在 jose 3.5.0 里会被静默忽略，实测过）。
    """
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require_exp": True, "require_sub": True, "verify_exp": True},
    )


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "JWTError",
]
