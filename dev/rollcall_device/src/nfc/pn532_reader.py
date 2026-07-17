"""PN532 SPI 读卡实现（路径 A）。

库选型拍板（设计日志 §10-D1 原在 nfcpy 与 Adafruit 之间未定）：
**选 adafruit-circuitpython-pn532 + Adafruit-Blinka**。依据：
- 接线走 SPI（`hardware_design.md §2.2` + 接线说明 §2：I²C 在 Pi 上不稳，SPI 最稳）。
- nfcpy **不支持 SPI**（只支持 USB / UART / I²C），技术上直接出局。
- adafruit-circuitpython-pn532 提供 `PN532_SPI`，通过 Blinka 的 `board` / `busio` 走
  Pi 硬件 SPI0，官方支持 NTAG2xx（含 NTAG215）。
→ 因此实体卡读头库唯一可选项是 Adafruit，非偏好而是硬约束。

硬件不可用时（Mac 开发机 / 缺库）本模块 import 守卫置 `HARDWARE_AVAILABLE=False`，
构造真实读头即抛异常；测试与 --simulate 用 `interfaces.FakeCardReader`。
"""

from __future__ import annotations

from .interfaces import CardReader

try:
    # Blinka 在非树莓派环境 import 即抛错，用守卫拦住
    import board  # type: ignore
    import busio  # type: ignore
    from adafruit_pn532.spi import PN532_SPI  # type: ignore
    from digitalio import DigitalInOut  # type: ignore

    HARDWARE_AVAILABLE = True
except Exception:  # noqa: BLE001 —— 任何 import 失败都视为无硬件
    HARDWARE_AVAILABLE = False


def uid_to_hex(uid: bytes) -> str:
    """把 PN532 读到的 UID 字节转成 14 位小写 hex 字符串（契约 §4.1：7 字节 → 14 位）。"""
    return uid.hex()


class Pn532CardReader(CardReader):
    """PN532 SPI 真实读头。

    `cs_pin_name` = 片选脚，接线说明 §2 用 CE0（GPIO8）。默认走 `board.D8`。
    """

    def __init__(self, cs_pin_name: str = "D8") -> None:
        if not HARDWARE_AVAILABLE:
            raise RuntimeError(
                "PN532 硬件库不可用（非树莓派环境或未装 adafruit-circuitpython-pn532）。"
                "开发机请用 --simulate。"
            )
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs = DigitalInOut(getattr(board, cs_pin_name))
        self._pn532 = PN532_SPI(spi, cs, debug=False)
        # SAM 配置：把 PN532 设为普通读卡器模式（datasheet SAMConfiguration）
        self._pn532.SAM_configuration()

    def read_uid(self, timeout: float = 0.5) -> str | None:
        uid = self._pn532.read_passive_target(timeout=timeout)
        if uid is None:
            return None
        return uid_to_hex(bytes(uid))


def build_card_reader(cs_pin_name: str = "D8") -> CardReader:
    """工厂：有硬件返回真实读头，无硬件抛错（调用方决定是否降级到 fake）。"""
    return Pn532CardReader(cs_pin_name=cs_pin_name)
