"""Resend 邮件发送单元测试（2026-06-05 SendGrid→Resend 迁移）。

- dev 模式（无密钥）：跳过发送、返回 skipped
- 有密钥：用 urllib POST 到 Resend API，带 Bearer 认证 + 正确 payload
"""

from __future__ import annotations

import json
import urllib.request

from app.services import email as email_svc


class _FakeSettings:
    resend_api_key = ""
    email_from = "noreply@tomoshibi.example.jp"
    email_from_name = "Tomoshibi 通知"


def test_resend_dev_mode_skips_without_key(monkeypatch):
    """无 RESEND_API_KEY 时 dev 模式跳过，不真发。"""
    monkeypatch.setattr(email_svc, "get_settings", lambda: _FakeSettings())
    sent, code, err = email_svc._send_via_resend(
        to_emails=["a@b.com"], subject="x", body_text="y"
    )
    assert sent is False
    assert code is None
    assert err == "RESEND_API_KEY not configured"


def test_resend_no_recipients(monkeypatch):
    """有密钥但收件人为空 → 不发。"""
    s = _FakeSettings()
    s.resend_api_key = "re_test"
    monkeypatch.setattr(email_svc, "get_settings", lambda: s)
    sent, code, err = email_svc._send_via_resend(
        to_emails=[], subject="x", body_text="y"
    )
    assert sent is False
    assert err == "no recipients"


def test_resend_posts_to_api_when_key_set(monkeypatch):
    """有密钥时 POST 到 Resend API，验证 URL / Bearer 认证 / payload。"""
    s = _FakeSettings()
    s.resend_api_key = "re_test"
    monkeypatch.setattr(email_svc, "get_settings", lambda: s)

    captured: dict = {}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["auth"] = req.get_header("Authorization")
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    sent, code, err = email_svc._send_via_resend(
        to_emails=["a@b.com"], subject="件名", body_text="本文"
    )
    assert sent is True
    assert code == 200
    assert err is None
    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["auth"] == "Bearer re_test"
    assert captured["body"]["to"] == ["a@b.com"]
    assert captured["body"]["subject"] == "件名"
    assert captured["body"]["from"] == "Tomoshibi 通知 <noreply@tomoshibi.example.jp>"
