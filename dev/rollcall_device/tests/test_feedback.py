"""反馈决策测试 —— 逐行覆盖契约 §9「错误码 → 设备现场行为对照」表。"""

from src.audio.player import Tone
from src.feedback import for_offline, for_response
from src.led.controller import LedState


def test_success_present_green_success_tone_and_broadcast():
    fb = for_response(
        True,
        {
            "base_status": "present",
            "duplicate": False,
            "led": "green",
            "audio_file": "10023.wav",
            "broadcast_text": "山田太郎",
        },
        None,
    )
    assert fb.led is LedState.SUCCESS
    assert fb.tone is Tone.SUCCESS
    assert fb.audio_file == "10023.wav"
    assert fb.broadcast_text == "山田太郎"


def test_success_late_also_green():
    # 契约 §9：late 与 present 学生侧同显绿
    fb = for_response(
        True, {"base_status": "late", "duplicate": False, "led": "green"}, None
    )
    assert fb.led is LedState.SUCCESS
    assert fb.tone is Tone.SUCCESS


def test_duplicate_green_but_silent():
    fb = for_response(True, {"duplicate": True, "led": "green"}, None)
    assert fb.led is LedState.SUCCESS
    assert fb.tone is None  # 静默，不重复播报
    assert fb.audio_file is None


def test_unknown_card_red_fail():
    fb = for_response(False, None, "UNKNOWN_CARD")
    assert fb.led is LedState.FAIL
    assert fb.tone is Tone.FAIL


def test_unregistered_uid_red_fail():
    fb = for_response(False, None, "UNREGISTERED_UID")
    assert fb.led is LedState.FAIL
    assert fb.tone is Tone.FAIL


def test_session_not_running_yellow_waiting():
    fb = for_response(False, None, "SESSION_NOT_RUNNING")
    assert fb.led is LedState.WAITING
    assert fb.tone is Tone.WAITING


def test_unknown_business_error_red_fail():
    # 未知/未来新增的业务错误码走兜底分支：红灯 + 失败音（7-17 拍板删 TIMEOUT 后此分支为通用兜底）
    fb = for_response(False, None, "SOME_FUTURE_CODE")
    assert fb.led is LedState.FAIL
    assert fb.tone is Tone.FAIL


def test_auth_errors_white_blink_silent():
    # 遍历信封单一真值，避免漏码（如 INVALID_CREDENTIALS）无白灯回归覆盖
    from src.api.envelope import AUTH_ERROR_CODES

    for code in AUTH_ERROR_CODES:
        fb = for_response(False, None, code)
        assert fb.led is LedState.AUTH_ERROR, code
        assert fb.tone is None, code


def test_offline_hit_green_broadcast_and_enqueue():
    fb = for_offline({"student_number": "10023", "name": "山田太郎"})
    assert fb.led is LedState.SUCCESS
    assert fb.tone is Tone.SUCCESS
    assert fb.audio_file == "10023.wav"
    assert fb.broadcast_text == "山田太郎"


def test_offline_miss_red_but_still_enqueue():
    fb = for_offline(None)
    assert fb.led is LedState.FAIL
    assert fb.tone is Tone.FAIL
    # device#17：入队职责归主流程 _handle_offline，Feedback.enqueue 字段已删（原断言随之移除）
