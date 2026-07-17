"""WebSocket 纯逻辑测试（契约 §5）—— 指数退避 + 消息解析。"""

from src.api.ws import (
    BACKOFF_CAP_S,
    BACKOFF_INITIAL_S,
    next_backoff,
    parse_ws_message,
)


def test_backoff_doubles():
    assert next_backoff(1.0) == 2.0
    assert next_backoff(2.0) == 4.0
    assert next_backoff(8.0) == 16.0


def test_backoff_caps_at_60():
    assert next_backoff(40.0) == BACKOFF_CAP_S
    assert next_backoff(60.0) == BACKOFF_CAP_S


def test_backoff_progression_from_initial():
    # 从初始 1 秒一路翻倍应封顶 60（契约 §5：初始 1 秒、上限 60 秒）
    b = BACKOFF_INITIAL_S
    seen = [b]
    for _ in range(10):
        b = next_backoff(b)
        seen.append(b)
    assert max(seen) == 60.0
    assert seen[0] == 1.0


def test_parse_known_message():
    kind, data = parse_ws_message(
        '{"type": "session_started", "data": {"session_id": "abc"}}'
    )
    assert kind == "session_started"
    assert data["session_id"] == "abc"


def test_parse_all_known_types():
    for t in ("session_started", "session_ended", "roster_updated", "audio_updated"):
        parsed = parse_ws_message('{"type": "%s", "data": {}}' % t)
        assert parsed is not None
        assert parsed[0] == t


def test_parse_unknown_type_returns_none():
    assert parse_ws_message('{"type": "heartbeat", "data": {}}') is None


def test_parse_invalid_json_returns_none():
    assert parse_ws_message("not json") is None


def test_parse_missing_data_defaults_empty():
    kind, data = parse_ws_message('{"type": "roster_updated"}')
    assert kind == "roster_updated"
    assert data == {}
