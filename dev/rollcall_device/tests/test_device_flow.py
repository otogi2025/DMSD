"""主状态机流程测试 —— 「读卡 → 上报 → 反馈」主流程（在线 + 离线降级）。

用假硬件 + stub API 驱动 `RollCallDevice._handle_checkin`，断言 LED 状态转移、播报、
离线入队。不起真实线程，直接调处理函数（线程 B 的核心逻辑）。
"""

import src.main as main_mod
from src.api.envelope import ApiResponse, NetworkError
from src.audio.player import Tone
from src.config import parse_config
from src.events import CardEvent, PhoneEvent
from src.led.controller import FakeLedBackend, LedController, LedState
from src.nfc.interfaces import FakeCardReader, FakeMailboxReader
from src.offline.queue import OfflineQueue
from src.roster import Roster
from src.main import RollCallDevice


class RecordingLed(LedController):
    """记录每次 set 的状态，供断言状态转移。"""

    def __init__(self, backend):
        self.states = []
        super().__init__(backend)

    def set(self, state):
        self.states.append(state)
        super().set(state)


class RecordingAudio:
    def __init__(self):
        self.calls = []

    def play_tone(self, tone):
        self.calls.append(("tone", tone))

    def play_name(self, f):
        self.calls.append(("name", f))

    def stop(self):
        pass

    def close(self):
        pass


class StubApi:
    def __init__(self, script):
        self.script = script
        self.posted = []

    def post_checkin(self, body):
        self.posted.append(body)
        return self.script(body)

    def fetch_roster(self):
        raise NetworkError("stub")

    def sync_audio(self, _):
        return 0


class StubAuth:
    def __init__(self):
        self.invalidated = 0

    def invalidate(self):
        self.invalidated += 1


def _cfg(tmp_path):
    return parse_config(
        {
            "device_id": "dorm-1-01",
            "server_url": "https://x.test",
            "ws_url": "wss://x.test",
            "key_path": str(tmp_path / "key"),
            "data_dir": str(tmp_path / "data"),
            "audio_output": "plughw:1,0",
        }
    )


def _device(tmp_path, api, roster=None):
    led = RecordingLed(FakeLedBackend())
    audio = RecordingAudio()
    queue = OfflineQueue(tmp_path / "q.sqlite3")
    dev = RollCallDevice(
        cfg=_cfg(tmp_path),
        card_reader=FakeCardReader(),
        mailbox_reader=FakeMailboxReader(),
        led=led,
        audio=audio,
        api=api,
        auth=StubAuth(),
        offline_queue=queue,
        roster=roster or Roster(),
        ws=None,
        simulate=True,
    )
    return dev, led, audio, queue


def _ok(data):
    return ApiResponse(ok=True, http_status=200, data=data)


def _err(code):
    return ApiResponse(ok=False, http_status=422, error={"code": code})


def _fast_feedback(monkeypatch):
    monkeypatch.setattr(main_mod, "FEEDBACK_HOLD_S", 0.01)


def test_online_success_green_and_broadcast(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(
        lambda body: _ok(
            {
                "duplicate": False,
                "led": "green",
                "audio_file": "10023.wav",
                "broadcast_text": "山田太郎",
            }
        )
    )
    dev, led, audio, _ = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="04a1b2c3d4e5f6", swipe_time="t"))

    assert LedState.PROCESSING in led.states
    assert LedState.SUCCESS in led.states
    assert led.states[-1] is LedState.STANDBY  # 反馈后回待机
    assert ("name", "10023.wav") in audio.calls
    assert api.posted[0]["path_type"] == "A"
    assert api.posted[0]["card_uid"] == "04a1b2c3d4e5f6"


def test_duplicate_green_silent(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _ok({"duplicate": True, "led": "green"}))
    dev, led, audio, _ = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))
    assert LedState.SUCCESS in led.states
    assert audio.calls == []  # 静默：不播报


def test_unknown_card_red_fail(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _err("UNKNOWN_CARD"))
    dev, led, audio, _ = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="ffff", swipe_time="t"))
    assert LedState.FAIL in led.states
    assert ("tone", Tone.FAIL) in audio.calls


def test_session_not_running_yellow(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _err("SESSION_NOT_RUNNING"))
    dev, led, audio, _ = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))
    assert LedState.WAITING in led.states
    assert ("tone", Tone.WAITING) in audio.calls


def test_auth_error_white_blink_and_invalidate(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _err("UNKNOWN_DEVICE"))
    dev, led, audio, _ = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))
    assert LedState.AUTH_ERROR in led.states
    assert audio.calls == []  # 静默
    assert dev._auth.invalidated == 1  # 令牌作废，下次换新


def test_network_failure_roster_hit_green_and_enqueue(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)

    def boom(body):
        raise NetworkError("down")

    roster = Roster()
    roster.replace(
        "t",
        [
            {
                "student_id": "s-1",
                "student_number": "10023",
                "name": "山田太郎",
                "card_uids": ["04a1b2c3d4e5f6"],
            }
        ],
    )
    api = StubApi(boom)
    dev, led, audio, queue = _device(tmp_path, api, roster=roster)
    dev._handle_checkin(CardEvent(card_uid="04a1b2c3d4e5f6", swipe_time="t"))

    assert LedState.SUCCESS in led.states  # 本地名单命中 → 放行
    assert ("name", "10023.wav") in audio.calls
    assert queue.count() == 1  # 契约 §6.1：入队待补传


def test_network_failure_roster_miss_red_but_enqueue(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)

    def boom(body):
        raise NetworkError("down")

    api = StubApi(boom)
    dev, led, audio, queue = _device(tmp_path, api)  # 空名单
    dev._handle_checkin(CardEvent(card_uid="deadbeefdeadbe", swipe_time="t"))

    assert LedState.FAIL in led.states  # 未命中 → 红灯拒绝
    assert queue.count() == 1  # 仍入队（后端恢复后判定并出队）


def test_phone_path_b_body_shape(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _ok({"duplicate": False, "led": "green"}))
    dev, _, _, _ = _device(tmp_path, api)
    dev._handle_checkin(
        PhoneEvent(
            student_id="11111111-1111-1111-1111-111111111111",
            idempotency_key="22222222-2222-2222-2222-222222222222",
            swipe_time="t",
        )
    )
    body = api.posted[0]
    assert body["path_type"] == "B"
    assert body["student_id"] == "11111111-1111-1111-1111-111111111111"
    assert body["idempotency_key"] == "22222222-2222-2222-2222-222222222222"
    assert "card_uid" not in body


def test_online_success_triggers_offline_replay(tmp_path, monkeypatch):
    _fast_feedback(monkeypatch)
    # 先塞一条离线积压，再来一次在线成功 → 应顺手补传出队
    queue_seed = OfflineQueue(tmp_path / "q.sqlite3")
    queue_seed.enqueue({"path_type": "A", "card_uid": "old", "swipe_time": "t"})
    queue_seed.close()

    api = StubApi(lambda body: _ok({"duplicate": False, "led": "green"}))
    dev, _, _, queue = _device(tmp_path, api)
    assert queue.count() == 1
    dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))
    assert queue.count() == 0  # 在线成功后补传清空
