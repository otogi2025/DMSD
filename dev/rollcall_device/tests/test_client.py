"""HTTP 客户端测试（契约 §4）—— httpx MockTransport 假后端 + 信封解包 + 令牌头。"""

import json

import httpx
import pytest

from src.api.auth import AuthManager, DeviceKey
from src.api.client import ApiClient
from src.api.envelope import NetworkError


def _future_iso():
    from datetime import timedelta

    from src.timeutil import now_jst

    return (now_jst() + timedelta(hours=12)).isoformat(timespec="seconds")


def _make_client(tmp_path, handler):
    key = DeviceKey.load_or_create(tmp_path / "device_key")
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport, base_url="")
    auth = AuthManager("dorm-1-01", key, "https://api.example.test", http)
    api = ApiClient("https://api.example.test", auth, http, fw_version="fw-test")
    return api


def _token_response():
    return httpx.Response(
        200,
        json={
            "ok": True,
            "data": {"access_token": "TOK123", "expires_at": _future_iso()},
        },
    )


def test_checkin_success_unwraps_envelope_and_sends_bearer(tmp_path):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        if request.url.path.endswith("/device-checkins"):
            seen["auth"] = request.headers.get("Authorization")
            seen["body"] = json.loads(request.content)
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "data": {
                        "student_id": "s-1",
                        "student_number": "10023",
                        "student_name": "山田太郎",
                        "base_status": "present",
                        "duplicate": False,
                        "led": "green",
                        "audio_file": "10023.wav",
                        "broadcast_text": "山田太郎",
                    },
                },
            )
        return httpx.Response(404, json={"ok": False, "error": {"code": "NOT_FOUND"}})

    api = _make_client(tmp_path, handler)
    resp = api.post_checkin({"path_type": "A", "card_uid": "04a1", "swipe_time": "t"})
    assert resp.ok is True
    assert resp.data["base_status"] == "present"
    assert seen["auth"] == "Bearer TOK123"
    assert seen["body"]["card_uid"] == "04a1"


def test_business_error_returns_apiresponse_not_raise(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        return httpx.Response(
            422,
            json={
                "ok": False,
                "error": {"code": "UNKNOWN_CARD", "message": "未登记的卡"},
            },
        )

    api = _make_client(tmp_path, handler)
    resp = api.post_checkin({"path_type": "A", "card_uid": "x", "swipe_time": "t"})
    assert resp.ok is False
    assert resp.error_code == "UNKNOWN_CARD"


def test_5xx_raises_network_error(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        return httpx.Response(503, text="upstream down")

    api = _make_client(tmp_path, handler)
    with pytest.raises(NetworkError):
        api.post_checkin({"path_type": "A", "card_uid": "x", "swipe_time": "t"})


def test_connection_error_raises_network_error(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        raise httpx.ConnectError("no route")

    api = _make_client(tmp_path, handler)
    with pytest.raises(NetworkError):
        api.post_checkin({"path_type": "A", "card_uid": "x", "swipe_time": "t"})


def test_fetch_roster_parses_students(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        if request.url.path.endswith("/roster"):
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "data": {
                        "generated_at": "2026-07-17T00:00:00+09:00",
                        "students": [
                            {
                                "student_id": "s-1",
                                "student_number": "10023",
                                "name": "山田太郎",
                                "card_uids": ["04a1"],
                            }
                        ],
                    },
                },
            )
        return httpx.Response(404, json={"ok": False, "error": {"code": "NOT_FOUND"}})

    api = _make_client(tmp_path, handler)
    generated_at, students = api.fetch_roster()
    assert generated_at == "2026-07-17T00:00:00+09:00"
    assert students[0]["student_number"] == "10023"


def test_token_obtained_only_once_when_valid(tmp_path):
    calls = {"token": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            calls["token"] += 1
            return _token_response()
        return httpx.Response(
            200, json={"ok": True, "data": {"duplicate": False, "led": "green"}}
        )

    api = _make_client(tmp_path, handler)
    api.post_checkin({"path_type": "A", "card_uid": "x", "swipe_time": "t"})
    api.post_checkin({"path_type": "A", "card_uid": "y", "swipe_time": "t"})
    # 12h 令牌未过半 → 只取一次
    assert calls["token"] == 1


def test_sync_audio_rejects_traversal_filename(tmp_path):
    """2026-07-18 cursor 审查 minor 9：manifest 里的文件名设备侧自己也要校验，
    不能因为后端有白名单就直接拿来拼路径（纵深防御）。"""
    downloaded_names = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        if request.url.path.endswith("/audio-manifest"):
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "data": {
                        "files": [
                            {"name": "../../evil.wav", "sha256": "x"},
                            {"name": "sub/dir.wav", "sha256": "y"},
                            {"name": "10023.wav", "sha256": "z"},
                        ]
                    },
                },
            )
        downloaded_names.append(request.url.path.rsplit("/", 1)[-1])
        return httpx.Response(200, content=b"RIFF-fake-wav")

    api = _make_client(tmp_path, handler)
    cache = tmp_path / "audio"
    count = api.sync_audio(cache)

    assert count == 1, "只有合法文件名该被下载"
    assert downloaded_names == ["10023.wav"]
    assert not (tmp_path.parent / "evil.wav").exists()
    assert (cache / "10023.wav").exists()
