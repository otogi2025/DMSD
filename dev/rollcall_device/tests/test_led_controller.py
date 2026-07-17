"""LED 状态机映射测试 —— LedState → 物理灯颜色（契约 §9 灯列）。"""

from src.led.controller import FakeLedBackend, LedController, LedState


def _controller():
    backend = FakeLedBackend()
    return LedController(backend), backend


def test_boot_is_white():
    ctrl, backend = _controller()
    ctrl.set(LedState.BOOT)
    assert backend.lit_colors() == {"white"}


def test_standby_is_blue():
    ctrl, backend = _controller()
    ctrl.set(LedState.STANDBY)
    assert backend.lit_colors() == {"blue"}


def test_success_is_green():
    ctrl, backend = _controller()
    ctrl.set(LedState.SUCCESS)
    assert backend.lit_colors() == {"green"}


def test_fail_is_red():
    ctrl, backend = _controller()
    ctrl.set(LedState.FAIL)
    assert backend.lit_colors() == {"red"}


def test_waiting_is_red_plus_green_yellow_approx():
    # 硬件无黄灯 → 红+绿同亮近似黄（契约 §9 SESSION_NOT_RUNNING）
    ctrl, backend = _controller()
    ctrl.set(LedState.WAITING)
    assert backend.lit_colors() == {"red", "green"}


def test_auth_error_is_white_blink():
    ctrl, backend = _controller()
    ctrl.set(LedState.AUTH_ERROR)
    assert backend.actions["white"] == "blink"
    # 其余灯灭
    assert backend.lit_colors() == {"white"}


def test_processing_is_blue_blink():
    ctrl, backend = _controller()
    ctrl.set(LedState.PROCESSING)
    assert backend.actions["blue"] == "blink"


def test_startup_all_off():
    # 构造即置 OFF（接线说明 §4 防开机浮空微亮）
    _, backend = _controller()
    assert backend.lit_colors() == set()


def test_switching_states_clears_previous():
    ctrl, backend = _controller()
    ctrl.set(LedState.SUCCESS)
    ctrl.set(LedState.FAIL)
    assert backend.lit_colors() == {"red"}  # 绿已灭
