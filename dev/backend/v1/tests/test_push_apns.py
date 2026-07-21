"""APNs 真实投递测试 — spec §7.13（push.py _send_via_apns 实装部分）。

覆盖：
  1. 成功（200）→ (True, None)，请求头 / 网关地址正确
  2. 4xx 失败 → (False, 错误串含状态码 + 响应体)
  3. 凭证缺失（部分缺）→ (False, "... not configured")，send_push 记 skipped_no_provider
  4. rollcall 模板 → aps 带 interruption-level=time-sensitive；generic 模板不带
  5. provider token 50 分钟内复用缓存，不重签
  6. 网络异常 → (False, "APNs request error: ...")，不 raise
"""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.services import push as push_svc


# ---------------------------------------------------------------
# helpers
# ---------------------------------------------------------------
def _make_ec_pem() -> str:
    """生成一把测试用 P-256 私钥（APNs .p8 同款算法），PEM 文本。"""
    key = ec.generate_private_key(ec.SECP256R1())
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


class _FakeSettings:
    """只带 push.py 用到的字段的假设置对象。"""

    def __init__(self, **overrides):
        self.apns_key = overrides.get("apns_key", _make_ec_pem())
        self.apns_key_id = overrides.get("apns_key_id", "TESTKEY123")
        self.apns_team_id = overrides.get("apns_team_id", "TESTTEAM12")
        self.apns_bundle_id = overrides.get("apns_bundle_id", "com.itsuki.tomoshibi")
        self.apns_use_sandbox = overrides.get("apns_use_sandbox", False)


class _FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def json(self):
        # 忠实模拟 httpx.Response.json()：解析 text 里的 JSON（APNs 4xx 返回
        # {"reason":"..."}），供 push._send_via_apns 判恒久失败（backend#117）
        import json

        return json.loads(self.text)


class _FakeClient:
    """记录 post 调用参数、按预设返回响应（或抛异常）。"""

    def __init__(self, response: _FakeResponse | None = None, raise_exc=None):
        self.response = response or _FakeResponse(200)
        self.raise_exc = raise_exc
        self.calls: list[dict] = []

    def post(self, url, *, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        if self.raise_exc:
            raise self.raise_exc
        return self.response


@pytest.fixture(autouse=True)
def _reset_apns_state(monkeypatch):
    """每个测试前清 provider token 缓存，防止测试间串味。"""
    monkeypatch.setattr(
        push_svc, "_apns_token_cache", {"token": None, "issued_at": 0.0}
    )


def _patch(monkeypatch, settings: _FakeSettings, client: _FakeClient):
    monkeypatch.setattr(push_svc, "get_settings", lambda: settings)
    monkeypatch.setattr(push_svc, "_get_apns_client", lambda: client)


# ---------------------------------------------------------------
# 1. 成功（200）
# ---------------------------------------------------------------
def test_apns_send_success(monkeypatch):
    client = _FakeClient(_FakeResponse(200))
    _patch(monkeypatch, _FakeSettings(), client)

    sent, error, _ = push_svc._send_via_apns(
        "device-token-001", "タイトル", "本文", None
    )
    assert sent is True
    assert error is None

    call = client.calls[0]
    # 生产网关 + token 进 URL
    assert call["url"] == "https://api.push.apple.com/3/device/device-token-001"
    # 必备请求头
    assert call["headers"]["apns-topic"] == "com.itsuki.tomoshibi"
    assert call["headers"]["apns-push-type"] == "alert"
    assert call["headers"]["authorization"].startswith("bearer ")
    # aps 载荷
    aps = call["json"]["aps"]
    assert aps["alert"] == {"title": "タイトル", "body": "本文"}


# ---------------------------------------------------------------
# 2. 4xx → (False, 错误串)
# ---------------------------------------------------------------
def test_apns_send_4xx_failed(monkeypatch):
    client = _FakeClient(_FakeResponse(400, '{"reason":"BadDeviceToken"}'))
    _patch(monkeypatch, _FakeSettings(), client)

    sent, error, permanent = push_svc._send_via_apns("bad-token", "t", "b", None)
    assert sent is False
    assert "400" in error
    assert "BadDeviceToken" in error
    assert (
        permanent is True
    )  # backend#117：BadDeviceToken 属恒久失败，send_push 据此撤销死令牌


# ---------------------------------------------------------------
# 3. 凭证缺失 → not configured（上层 send_push 记 skipped_no_provider）
# ---------------------------------------------------------------
def test_apns_missing_credentials(monkeypatch):
    client = _FakeClient()
    # key 有、其余三个全空 → 报缺的字段名
    _patch(
        monkeypatch,
        _FakeSettings(apns_key_id="", apns_team_id="", apns_bundle_id=""),
        client,
    )

    sent, error, _ = push_svc._send_via_apns("token", "t", "b", None)
    assert sent is False
    assert "not configured" in error
    assert "APNS_KEY_ID" in error
    assert client.calls == []  # 凭证不齐不该发出任何请求


# ---------------------------------------------------------------
# 4. rollcall 模板 → Time Sensitive；generic 不带
# ---------------------------------------------------------------
def test_apns_rollcall_time_sensitive(monkeypatch):
    client = _FakeClient(_FakeResponse(200))
    _patch(monkeypatch, _FakeSettings(), client)

    push_svc._send_via_apns(
        "token", "点呼", "点呼が始まります", None, template_key="rollcall_evening"
    )
    push_svc._send_via_apns(
        "token", "お知らせ", "一般通知", None, template_key="generic"
    )

    rollcall_aps = client.calls[0]["json"]["aps"]
    generic_aps = client.calls[1]["json"]["aps"]
    assert rollcall_aps["interruption-level"] == "time-sensitive"
    assert "interruption-level" not in generic_aps


# ---------------------------------------------------------------
# 5. provider token 缓存复用（50 分钟内不重签）
# ---------------------------------------------------------------
def test_apns_provider_token_cached(monkeypatch):
    client = _FakeClient(_FakeResponse(200))
    _patch(monkeypatch, _FakeSettings(), client)

    push_svc._send_via_apns("token", "t1", "b1", None)
    push_svc._send_via_apns("token", "t2", "b2", None)

    auth_1 = client.calls[0]["headers"]["authorization"]
    auth_2 = client.calls[1]["headers"]["authorization"]
    assert auth_1 == auth_2  # 同一枚缓存 token，没重签


# ---------------------------------------------------------------
# 6. 网络异常 → (False, ...)，不往上抛
# ---------------------------------------------------------------
def test_apns_network_error(monkeypatch):
    client = _FakeClient(raise_exc=ConnectionError("connection refused"))
    _patch(monkeypatch, _FakeSettings(), client)

    sent, error, _ = push_svc._send_via_apns("token", "t", "b", None)
    assert sent is False
    assert "APNs request error" in error
    assert "connection refused" in error


# ---------------------------------------------------------------
# 7. 沙盒开关 → 打 sandbox 网关
# ---------------------------------------------------------------
def test_apns_sandbox_host(monkeypatch):
    client = _FakeClient(_FakeResponse(200))
    _patch(monkeypatch, _FakeSettings(apns_use_sandbox=True), client)

    push_svc._send_via_apns("token", "t", "b", None)
    assert client.calls[0]["url"].startswith(
        "https://api.sandbox.push.apple.com/3/device/"
    )
