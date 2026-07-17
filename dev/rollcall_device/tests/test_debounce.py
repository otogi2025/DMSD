"""UID 防抖测试 —— 同一 UID 2 秒内重复只算一次。"""

from src.nfc.debounce import UidDebouncer


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_first_read_accepted():
    d = UidDebouncer(window=2.0, clock=FakeClock())
    assert d.accept("aa") is True


def test_repeat_within_window_rejected():
    clock = FakeClock()
    d = UidDebouncer(window=2.0, clock=clock)
    assert d.accept("aa") is True
    clock.advance(1.0)  # 窗口内
    assert d.accept("aa") is False


def test_repeat_after_window_accepted():
    clock = FakeClock()
    d = UidDebouncer(window=2.0, clock=clock)
    assert d.accept("aa") is True
    clock.advance(2.5)  # 超窗口
    assert d.accept("aa") is True


def test_different_uid_not_debounced():
    clock = FakeClock()
    d = UidDebouncer(window=2.0, clock=clock)
    assert d.accept("aa") is True
    assert d.accept("bb") is True  # 不同卡各自计时


def test_hold_still_keeps_suppressing():
    # 贴住不动持续读到：每次都在窗口内 → 一直压制
    clock = FakeClock()
    d = UidDebouncer(window=2.0, clock=clock)
    assert d.accept("aa") is True
    for _ in range(5):
        clock.advance(0.5)
        assert d.accept("aa") is False
