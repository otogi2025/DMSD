"""ST25DV.begin() 初始化序列测试（2026-07-29 邮箱看门狗回归）。

两条要守住的性质：
1. 会话没开就不许往下走 —— 系统寄存器会被芯片静默拒写，程序照跑但邮箱永远收不到东西
2. MB_WDG 必须被关掉 —— 出厂默认约两秒超时，采集线程偶发卡顿就会静默丢签到
"""

import pytest

from src.nfc.st25dv import (
    I2C_ADDR_SYSTEM,
    MB_WDG_DISABLED,
    PWD_DEFAULT,
    REG_MB_WDG,
    ST25DV,
)


class FakeChip(ST25DV):
    """绕过 __init__ 的假芯片：记录每一次寄存器写，读值可预置。"""

    def __init__(self, *, session_open=True, mb_wdg=0x07):  # noqa: D107
        self.writes = []
        self._password = PWD_DEFAULT
        self._session_open = session_open
        self._regs = {(I2C_ADDR_SYSTEM, REG_MB_WDG): mb_wdg}

    def _read_reg(self, dev_addr, mem_addr):
        return self._regs.get((dev_addr, mem_addr), 0x00)

    def _write(self, dev_addr, mem_addr, data):
        self.writes.append((dev_addr, mem_addr, bytes(data)))

    def session_open(self):
        return self._session_open


def _wdg_writes(chip):
    return [w for w in chip.writes if w[:2] == (I2C_ADDR_SYSTEM, REG_MB_WDG)]


def test_begin_disables_mailbox_watchdog():
    # 出厂默认 0x07 → begin() 必须写回 0x00 关掉超时
    chip = FakeChip(mb_wdg=0x07)
    chip.begin()
    assert _wdg_writes(chip) == [
        (I2C_ADDR_SYSTEM, REG_MB_WDG, bytes([MB_WDG_DISABLED]))
    ]


def test_begin_skips_watchdog_write_when_already_disabled():
    # 已经是 0 就别重写 —— MB_WDG 在 EEPROM 里，每次开机都写是白磨寿命
    chip = FakeChip(mb_wdg=MB_WDG_DISABLED)
    chip.begin()
    assert _wdg_writes(chip) == []


def test_begin_raises_when_session_not_open():
    # 口令不对 → 后面的系统寄存器全会被静默拒写，必须当场报错而不是带病启动
    chip = FakeChip(session_open=False)
    with pytest.raises(RuntimeError, match="安全会话未打开"):
        chip.begin()
    # 报错点必须在写任何系统寄存器之前
    assert chip.writes[1:] == []  # writes[0] = present_password 本身


def test_watchdog_disabled_before_mailbox_enabled():
    # MB_WDG 要在 MB_MODE 使能之前写好，避免中间窗口里进来的消息按旧超时被丢
    from src.nfc.st25dv import REG_MB_MODE

    chip = FakeChip(mb_wdg=0x07)
    chip.begin()
    order = [w[1] for w in chip.writes]
    assert order.index(REG_MB_WDG) < order.index(REG_MB_MODE)
