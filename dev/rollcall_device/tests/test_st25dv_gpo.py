"""MailboxGpoReader GPO 门控 + I²C 兜底轮询测试（S2 审查 device#1 回归）。

GPO 漏边沿（抖动 / 上电时序 / 回调丢失）时邮箱载荷不能永久漏读：
未见触发标志也要按 GPO_FALLBACK_POLL_S 间隔走一次 I²C 确认。
"""

import src.nfc.st25dv as st25dv_mod
from src.nfc.st25dv import GPO_FALLBACK_POLL_S, MailboxGpoReader


class FakeST25:
    """假 ST25DV：poll() 恒返回预置载荷并计数（幂等语义由真实现保证）。"""

    def __init__(self, payload=b"\x01" * 34):
        self.payload = payload
        self.calls = 0

    def poll(self):
        self.calls += 1
        return self.payload

    def close(self):
        pass


def _reader_with_button(st):
    # CI 无 gpiozero → __init__ 里 _button 落 None（纯轮询分支）。
    # 手动塞假 button 模拟「GPO 已接线」，才能测到门控 + 兜底逻辑
    reader = MailboxGpoReader(st, gpo_pin=24)
    reader._button = object()
    reader._triggered = False
    return reader


def _clock(monkeypatch, start=100.0):
    t = {"now": start}
    monkeypatch.setattr(st25dv_mod.time, "monotonic", lambda: t["now"])
    return t


def test_first_poll_falls_back_immediately(monkeypatch):
    # _last_i2c 初值 0 → 启动后首次 poll 即兜底，扫掉上电前滞留的载荷
    st = FakeST25()
    reader = _reader_with_button(st)
    _clock(monkeypatch)
    assert reader.poll() == st.payload
    assert st.calls == 1


def test_missed_gpo_edge_fallback_after_interval(monkeypatch):
    st = FakeST25()
    reader = _reader_with_button(st)
    t = _clock(monkeypatch)
    reader.poll()  # 首次兜底，计时起点
    # 间隔内未触发 → 不打 I²C
    t["now"] += GPO_FALLBACK_POLL_S / 2
    assert reader.poll() is None
    assert st.calls == 1
    # 超过兜底间隔 → 漏掉的 GPO 边沿由兜底救回
    t["now"] += GPO_FALLBACK_POLL_S
    assert reader.poll() == st.payload
    assert st.calls == 2


def test_gpo_trigger_reads_immediately(monkeypatch):
    # GPO 触发时立即读，不受兜底间隔限制（GPO 仍是「加速唤醒」）
    st = FakeST25()
    reader = _reader_with_button(st)
    t = _clock(monkeypatch)
    reader.poll()  # 兜底一次，计时起点
    t["now"] += 0.1  # 远小于兜底间隔
    reader._triggered = True
    assert reader.poll() == st.payload
    assert st.calls == 2
    assert reader._triggered is False  # 标志被消费


def test_no_gpio_lib_polls_every_time(monkeypatch):
    # 无 gpiozero（_button=None）→ 退化为每次都走 I²C（原有兜底行为不变）
    st = FakeST25()
    reader = MailboxGpoReader(st, gpo_pin=24)
    assert reader._button is None
    _clock(monkeypatch)
    assert reader.poll() == st.payload
    assert reader.poll() == st.payload
    assert st.calls == 2
