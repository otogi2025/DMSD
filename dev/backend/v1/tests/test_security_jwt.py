"""JWT 负路径单元测试 — B-中-16（2026-06-15 全维度审查）。

app/security.py 的 decode_token 此前只间接测了「缺 token → 401」，没测 JWT 本身的
失效路径。本文件补两条核心负路径 + 正路径对照：
  - 过期 token（exp 已过）→ decode_token 抛 JWTError
  - 篡改签名 / 错密钥 token → decode_token 抛 JWTError
  - 正常 token → decode 成功且 claim 原样取回

直接测 security 层函数（不经 HTTP），保证「token 校验本身」这层的契约。

跑：
    cd dev/backend/v1
    .venv/bin/python -m pytest tests/test_security_jwt.py -q
"""

from __future__ import annotations

import pytest
from jose import JWTError, jwt

from app import security
from app.config import get_settings


class TestDecodeTokenNegativePaths:
    def test_valid_token_roundtrip(self):
        """正路径对照 —— 正常签发的 token 能 decode 回原 claim。"""
        token = security.create_access_token("student-123", "student")
        payload = security.decode_token(token)
        assert payload["sub"] == "student-123"
        assert payload["role"] == "student"

    def test_expired_token_raises(self):
        """过期 token（expire_minutes 设负数 → exp 已过）→ JWTError。"""
        token = security.create_access_token(
            "student-123", "student", expire_minutes=-1
        )
        with pytest.raises(JWTError):
            security.decode_token(token)

    def test_tampered_signature_raises(self):
        """篡改 payload 后用错密钥重签 → 与本服务密钥对不上 → JWTError。"""
        # 用一个与服务不同的密钥重签同一份 payload，模拟伪造 / 篡改 token
        forged = jwt.encode(
            {"sub": "attacker", "role": "teacher:寮務部長"},
            "a-completely-different-secret-key-32b",
            algorithm=get_settings().jwt_algorithm,
        )
        with pytest.raises(JWTError):
            security.decode_token(forged)

    def test_garbled_token_raises(self):
        """结构损坏的 token 串 → JWTError，不静默放行。"""
        with pytest.raises(JWTError):
            security.decode_token("not.a.valid.jwt")


class TestPasswordHash:
    """顺带补 bcrypt 哈希正负路径（同属 security.py 的认证基元）。"""

    def test_hash_then_verify_ok(self):
        h = security.hash_password("Correct-Horse-Battery-Staple")
        assert security.verify_password("Correct-Horse-Battery-Staple", h)

    def test_verify_wrong_password_false(self):
        h = security.hash_password("Correct-Horse-Battery-Staple")
        assert not security.verify_password("wrong-password", h)

    def test_verify_malformed_hash_false_not_raise(self):
        # 坏哈希串不应抛异常、应安全返回 False（verify_password 内 catch）
        assert not security.verify_password("anything", "not-a-bcrypt-hash")
