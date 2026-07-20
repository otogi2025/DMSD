"""设备身份与认证（契约 §2）—— Ed25519 密钥 + enroll + 12h 短期令牌。

流程（契约 §2.1-§2.4）：
1. 首启本地生成 Ed25519 密钥对，私钥落盘文件权限 0600，公钥上报后端。
2. enroll：`POST /devices/{device_id}/enroll` body `{enroll_code, public_key}`
   （public_key = base64 原始 32 字节）。
3. token：`POST /devices/{device_id}/token` body `{ts, nonce, signature}`，
   签名串 = `"{device_id}\n{ts}\n{nonce}"`（UTF-8 逐字拼接），signature = base64(Ed25519 签名)。
   返回 `{access_token, expires_at}`，JWT 12h。
4. 剩余寿命过半时主动换新。

密钥用 `cryptography` 库（契约 / 任务指定）。
"""

from __future__ import annotations

import base64
import os
import secrets
import stat
import threading
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ..timeutil import now_jst, now_jst_iso, parse_iso
from .envelope import ApiResponse, NetworkError, unwrap


class AuthError(Exception):
    """认证流程失败（enroll 被拒 / 取令牌被拒）。"""


class DeviceKey:
    """Ed25519 设备密钥的生成 / 加载 / 签名。"""

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        self._private_key = private_key

    @classmethod
    def load_or_create(cls, key_path: str | Path) -> DeviceKey:
        """加载私钥；不存在则生成并以 0600 落盘（契约 §2.1）。"""
        path = Path(key_path)
        if path.exists():
            data = path.read_bytes()
            private_key = serialization.load_pem_private_key(data, password=None)
            if not isinstance(private_key, Ed25519PrivateKey):
                raise AuthError("密钥文件不是 Ed25519 私钥")
            return cls(private_key)
        return cls._create(path)

    @classmethod
    def _create(cls, path: Path) -> DeviceKey:
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        # 先建空文件并设 0600，再写内容，避免私钥短暂以宽权限存在
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, pem)
        finally:
            os.close(fd)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
        return cls(private_key)

    def public_key_base64(self) -> str:
        """公钥 = base64(原始 32 字节)（契约 §2.2）。"""
        raw = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(raw).decode("ascii")

    def sign_base64(self, message: str) -> str:
        """对 UTF-8 消息签名，返回 base64（契约 §2.3）。"""
        sig = self._private_key.sign(message.encode("utf-8"))
        return base64.b64encode(sig).decode("ascii")


def build_token_signing_string(device_id: str, ts: str, nonce: str) -> str:
    """令牌签名串（契约 §2.3）：`"{device_id}\\n{ts}\\n{nonce}"`。"""
    return f"{device_id}\n{ts}\n{nonce}"


class AuthManager:
    """管理设备令牌：enroll、取令牌、过半自动续期、提供 Authorization 头。"""

    def __init__(
        self,
        device_id: str,
        key: DeviceKey,
        base_url: str,
        http: httpx.Client,
    ) -> None:
        self._device_id = device_id
        self._key = key
        self._base_url = base_url.rstrip("/")
        self._http = http
        self._access_token: str | None = None
        self._expires_at = None  # datetime | None
        self._issued_at = None  # datetime | None
        self._lock = threading.Lock()

    # --------------------------- enroll ---------------------------

    def enroll(self, enroll_code: str) -> ApiResponse:
        """用一次性激活码登记公钥（契约 §2.2 步骤 3）。"""
        url = f"{self._base_url}/api/v1/devices/{self._device_id}/enroll"
        body = {"enroll_code": enroll_code, "public_key": self._key.public_key_base64()}
        resp = unwrap(self._post_raw(url, body))
        if not resp.ok:
            raise AuthError(f"enroll 失败：{resp.error_code}")
        return resp

    def _post_raw(self, url: str, body: dict) -> httpx.Response:
        # 传输层异常统一转 NetworkError —— 本类被 main 直接调用（不经 ApiClient
        # 的转换层），裸 httpx 异常会穿透调用方的 (AuthError, NetworkError) 捕获、
        # 冒到消费线程笼统 except 卡死 LED（S2 终审 Fable 5 high 抓出的逃逸路径）。
        # 语义：取令牌/enroll 时网络断 = 网络失败，AuthError 只留给后端明确拒绝
        try:
            return self._http.post(url, json=body)
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc

    # --------------------------- token ---------------------------

    def obtain_token(self) -> None:
        """签名换取新令牌（契约 §2.3）。"""
        ts = now_jst_iso()
        nonce = secrets.token_hex(16)  # 随机 16 字节的 hex
        signing_string = build_token_signing_string(self._device_id, ts, nonce)
        signature = self._key.sign_base64(signing_string)
        url = f"{self._base_url}/api/v1/devices/{self._device_id}/token"
        body = {"ts": ts, "nonce": nonce, "signature": signature}
        resp = unwrap(self._post_raw(url, body))
        if not resp.ok:
            raise AuthError(f"取令牌失败：{resp.error_code}")
        data = resp.data or {}
        with self._lock:
            self._access_token = data.get("access_token")
            self._expires_at = (
                parse_iso(data["expires_at"]) if data.get("expires_at") else None
            )
            self._issued_at = now_jst()

    def _needs_renewal(self) -> bool:
        """令牌缺失或剩余寿命过半 → 需换新（契约 §2.3）。"""
        if self._access_token is None:
            return True
        if self._expires_at is None or self._issued_at is None:
            return True
        lifetime = self._expires_at - self._issued_at
        half_point = self._issued_at + lifetime / 2
        return now_jst() >= half_point

    def ensure_token(self) -> str:
        """返回可用令牌，必要时自动续期。"""
        with self._lock:
            need = self._needs_renewal()
        if need:
            self.obtain_token()
        with self._lock:
            if self._access_token is None:
                raise AuthError("无可用令牌")
            return self._access_token

    def invalidate(self) -> None:
        """令牌被后端拒（鉴权错误）时清空，强制下次换新。"""
        with self._lock:
            self._access_token = None
            self._expires_at = None
            self._issued_at = None

    def auth_header(self) -> dict[str, str]:
        """构造 `Authorization: Bearer <device JWT>`（契约 §2.4）。"""
        return {"Authorization": f"Bearer {self.ensure_token()}"}

    @property
    def token(self) -> str | None:
        return self._access_token
