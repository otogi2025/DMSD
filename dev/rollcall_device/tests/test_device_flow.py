"""主状态机流程测试 —— 「读卡 → 上报 → 反馈」主流程（在线 + 离线降级）。

用假硬件 + stub API 驱动 `RollCallDevice._handle_checkin`，断言 LED 状态转移、播报、
离线入队。不起真实线程，直接调处理函数（线程 B 的核心逻辑）。
"""

import src.main as main_mod
from src.api.auth import AuthError
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
    """ensure_raises 非 None 时 ensure_token 抛该异常（模拟设备被停用等取令牌被拒）。"""

    def __init__(self, ensure_raises=None):
        self.invalidated = 0
        self.ensured = 0
        self._ensure_raises = ensure_raises

    def invalidate(self):
        self.invalidated += 1

    def ensure_token(self):
        self.ensured += 1
        if self._ensure_raises is not None:
            raise self._ensure_raises
        return "stub-token"


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


def _device(tmp_path, api, roster=None, auth=None):
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
        auth=auth or StubAuth(),
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
    # S2 device#2 后的新语义：AUTH 码 → 刷令牌重发一次 → 仍 AUTH → 入队 + 白灯
    _fast_feedback(monkeypatch)
    api = StubApi(lambda body: _err("UNKNOWN_DEVICE"))
    dev, led, audio, queue = _device(tmp_path, api)
    dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))
    assert LedState.AUTH_ERROR in led.states
    assert audio.calls == []  # 静默
    assert len(api.posted) == 2  # 首发 + 刷令牌后重发一次（不多不少）
    assert dev._auth.ensured == 1
    assert dev._auth.invalidated == 2  # 首次判码 + 重试仍 AUTH
    assert queue.count() == 1  # 鉴权失败不丢签到：入队待补传


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


# ============================================================================
# S2 审查回归：device#0 取令牌 AuthError / device#2 鉴权重试链 / device#3 补传自愈
# ============================================================================


class TestAuthErrorCaptured:
    """device#0：取令牌抛 AuthError 不再冒泡 → 白灯 + 入队 + 回待机。"""

    def test_obtain_token_rejected_white_led_and_enqueued(self, tmp_path, monkeypatch):
        _fast_feedback(monkeypatch)

        def boom(body):
            raise AuthError("取令牌失败：INVALID_SIGNATURE")

        api = StubApi(boom)
        dev, led, audio, queue = _device(tmp_path, api)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert LedState.AUTH_ERROR in led.states
        assert led.states[-1] is LedState.STANDBY  # 不卡 PROCESSING（原病）
        assert queue.count() == 1  # 签到入队待补传，不丢
        assert dev._auth.invalidated == 1
        assert audio.calls == []


class TestAuthCodeRetryChain:
    """device#2：在线签到返 AUTH 码 → 刷令牌重发一次的四条分支。"""

    def test_retry_succeeds_after_token_refresh(self, tmp_path, monkeypatch):
        _fast_feedback(monkeypatch)
        calls = {"n": 0}

        def script(body):
            calls["n"] += 1
            if calls["n"] == 1:
                return _err("UNAUTHORIZED")
            return _ok({"duplicate": False, "led": "green"})

        api = StubApi(script)
        dev, led, _, queue = _device(tmp_path, api)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert len(api.posted) == 2
        assert LedState.SUCCESS in led.states  # 重发成功走正常反馈
        assert queue.count() == 0
        assert dev._auth.invalidated == 1
        assert dev._auth.ensured == 1

    def test_ensure_token_raises_auth_error_enqueues(self, tmp_path, monkeypatch):
        # 两家辩论 TOP 风险：重试链里 ensure_token 抛 AuthError 不得冒泡复现原病
        _fast_feedback(monkeypatch)
        api = StubApi(lambda body: _err("UNAUTHORIZED"))
        auth = StubAuth(ensure_raises=AuthError("DEVICE_NOT_ACTIVE"))
        dev, led, _, queue = _device(tmp_path, api, auth=auth)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert len(api.posted) == 1  # 取不到新令牌，没有第二发
        assert LedState.AUTH_ERROR in led.states
        assert led.states[-1] is LedState.STANDBY
        assert queue.count() == 1
        assert auth.invalidated == 2  # 判码时 + except 里

    def test_ensure_token_network_error_goes_offline(self, tmp_path, monkeypatch):
        # 终审阻断修复回归：重试链里刷新令牌撞网络断（auth 层已转 NetworkError）
        # → 走离线入队，不冒泡卡灯
        _fast_feedback(monkeypatch)
        api = StubApi(lambda body: _err("UNAUTHORIZED"))
        auth = StubAuth(ensure_raises=NetworkError("down"))
        dev, led, _, queue = _device(tmp_path, api, auth=auth)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert len(api.posted) == 1  # 没有第二发
        assert queue.count() == 1  # 离线入队
        assert LedState.FAIL in led.states  # 空名单未命中 → 红灯（离线反馈）
        assert led.states[-1] is LedState.STANDBY

    def test_retry_network_error_goes_offline(self, tmp_path, monkeypatch):
        _fast_feedback(monkeypatch)
        calls = {"n": 0}

        def script(body):
            calls["n"] += 1
            if calls["n"] == 1:
                return _err("UNAUTHORIZED")
            raise NetworkError("down")

        api = StubApi(script)
        dev, led, _, queue = _device(tmp_path, api)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert queue.count() == 1  # 走离线入队
        assert LedState.FAIL in led.states  # 空名单未命中 → 红灯（离线反馈）


class TestReplayAuthRecovery:
    """device#3：补传撞鉴权失败 → 刷令牌重开一轮（仅一次）。"""

    def _seed_queue(self, tmp_path, n):
        q = OfflineQueue(tmp_path / "q.sqlite3")
        for i in range(n):
            q.enqueue({"path_type": "A", "card_uid": f"old{i}", "swipe_time": "t"})
        q.close()

    def test_replay_recovers_after_refresh(self, tmp_path, monkeypatch):
        _fast_feedback(monkeypatch)
        self._seed_queue(tmp_path, 2)
        calls = {"n": 0}

        def script(body):
            calls["n"] += 1
            if calls["n"] == 1:  # 在线签到本体
                return _ok({"duplicate": False, "led": "green"})
            if calls["n"] == 2:  # 补传第 1 轮第 1 条 → 鉴权失败停轮
                return _err("UNAUTHORIZED")
            return _ok({"duplicate": False, "led": "green"})  # 刷令牌后第 2 轮

        api = StubApi(script)
        dev, _, _, queue = _device(tmp_path, api)
        assert queue.count() == 2
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert queue.count() == 0  # 第 2 轮把 2 条全出队
        assert dev._auth.invalidated == 1
        assert dev._auth.ensured == 1

    def test_replay_recovery_only_once(self, tmp_path, monkeypatch):
        # 令牌反复被拒时只重开一轮，不变成重放风暴
        _fast_feedback(monkeypatch)
        self._seed_queue(tmp_path, 1)
        calls = {"n": 0}

        def script(body):
            calls["n"] += 1
            if calls["n"] == 1:
                return _ok({"duplicate": False, "led": "green"})
            return _err("UNAUTHORIZED")  # 补传永远鉴权失败

        api = StubApi(script)
        dev, _, _, queue = _device(tmp_path, api)
        dev._handle_checkin(CardEvent(card_uid="04a1", swipe_time="t"))

        assert calls["n"] == 3  # 在线 1 + 补传两轮各 1，之后收手
        assert queue.count() == 1  # 条目保留，等下次在线成功再试
        assert dev._auth.ensured == 1
