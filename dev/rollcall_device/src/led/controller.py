"""LED 状态机 —— gpiozero 封装 + 契约 §9 现场行为对照。

硬件（接线说明 §4 + hardware_design §2.4.1）：4 个独立单色 LED，红 17 / 绿 27 /
蓝 22 / 白 23，**5V 驱动 / 低电平点亮**（active-low）。故 gpiozero `LED` 用
`active_high=False`：`.on()` 输出低电平 = 点亮。启动时全部置灭（引脚高电平），
防开机瞬间浮空微亮（接线说明 §4「代码注意」）。

⚠️ 硬件无黄色 LED。契约 §9 的「黄灯」（SESSION_NOT_RUNNING 等待态）用**红+绿同亮**
近似表达（分立 LED 物理上不混色成黄，但红绿同亮是可区分于纯红/纯绿的独立状态）。
这是硬件取舍，硬件联调时如加装黄灯或 RGB 灯可单点改 `_STATE_COLORS`。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class LedState(Enum):
    """逻辑 LED 状态。"""

    OFF = "off"  # 全灭
    BOOT = "boot"  # 白常亮 —— 系统启动中（接线说明 §4）
    STANDBY = "standby"  # 蓝常亮 —— 待机
    PROCESSING = "processing"  # 蓝闪 —— 处理中（设计日志 §3.1 flash_blue）
    SUCCESS = "success"  # 绿 —— 签到成功（契约 §9：present/late 均绿）
    FAIL = "fail"  # 红 —— 失败（UNKNOWN_CARD / UNREGISTERED_UID 等业务错误）
    WAITING = "waiting"  # 黄(红+绿) —— SESSION_NOT_RUNNING 等待态
    AUTH_ERROR = "auth_error"  # 白闪 —— 鉴权异常（设备自身问题，契约 §9）


# 每个状态点亮哪些物理灯（颜色名）。
_STATE_COLORS: dict[LedState, tuple[str, ...]] = {
    LedState.OFF: (),
    LedState.BOOT: ("white",),
    LedState.STANDBY: ("blue",),
    LedState.PROCESSING: ("blue",),
    LedState.SUCCESS: ("green",),
    LedState.FAIL: ("red",),
    LedState.WAITING: ("red", "green"),
    LedState.AUTH_ERROR: ("white",),
}

# 需要闪烁（而非常亮）的状态。
_BLINK_STATES = frozenset({LedState.PROCESSING, LedState.AUTH_ERROR})

_ALL_COLORS = ("red", "green", "blue", "white")


class LedBackend(ABC):
    """4 路 LED 引脚后端抽象。真实实现走 gpiozero，假实现供测试。"""

    @abstractmethod
    def on(self, color: str) -> None: ...

    @abstractmethod
    def off(self, color: str) -> None: ...

    @abstractmethod
    def blink(self, color: str) -> None: ...

    def close(self) -> None: ...


class FakeLedBackend(LedBackend):
    """记录每盏灯当前动作（on/off/blink），供测试断言契约 §9 对照表。"""

    def __init__(self) -> None:
        self.actions: dict[str, str] = {c: "off" for c in _ALL_COLORS}

    def on(self, color: str) -> None:
        self.actions[color] = "on"

    def off(self, color: str) -> None:
        self.actions[color] = "off"

    def blink(self, color: str) -> None:
        self.actions[color] = "blink"

    def lit_colors(self) -> set[str]:
        """当前点亮（on 或 blink）的颜色集合。"""
        return {c for c, a in self.actions.items() if a in ("on", "blink")}


class GpioZeroLedBackend(LedBackend):
    """gpiozero 真实 LED 后端（active-low）。"""

    def __init__(self, pins: dict[str, int]) -> None:
        from gpiozero import LED  # type: ignore

        # active_high=False → on() 拉低电平点亮；initial_value=False → 启动即灭
        self._leds = {
            color: LED(pin, active_high=False, initial_value=False)
            for color, pin in pins.items()
        }

    def on(self, color: str) -> None:
        self._leds[color].on()

    def off(self, color: str) -> None:
        self._leds[color].off()

    def blink(self, color: str) -> None:
        # 0.3s 亮 / 0.3s 灭 循环
        self._leds[color].blink(on_time=0.3, off_time=0.3)

    def close(self) -> None:
        for led in self._leds.values():
            try:
                led.close()
            except Exception:  # noqa: BLE001
                pass


class LedController:
    """把 `LedState` 翻译成 4 盏物理灯的开关。"""

    def __init__(self, backend: LedBackend) -> None:
        self._backend = backend
        self._state = LedState.OFF
        # 启动第一件事：全灭（接线说明 §4 防开机浮空微亮）
        self.set(LedState.OFF)

    @property
    def state(self) -> LedState:
        return self._state

    def set(self, state: LedState) -> None:
        """切到目标状态：点亮该状态的灯（常亮或闪），熄灭其余灯。"""
        lit = _STATE_COLORS[state]
        blink = state in _BLINK_STATES
        for color in _ALL_COLORS:
            if color in lit:
                if blink:
                    self._backend.blink(color)
                else:
                    self._backend.on(color)
            else:
                self._backend.off(color)
        self._state = state

    def close(self) -> None:
        self.set(LedState.OFF)
        self._backend.close()


def build_led_controller(pins: dict[str, int]) -> LedController:
    """工厂：构造 gpiozero 真实 LED 控制器。无 GPIO 库时抛错，调用方决定降级。"""
    return LedController(GpioZeroLedBackend(pins))
