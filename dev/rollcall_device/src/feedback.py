"""现场反馈决策 —— 把后端响应 / 离线命中翻译成 LED + 声音 + 播报（契约 §9）。

这是状态机「读卡 → 上报 → 反馈」里「反馈」那一段的核心逻辑，纯函数、可单测，
不碰任何硬件。契约 §9 对照表逐行落地：

| 后端响应 | LED | 声音 | 播报 |
|---|---|---|---|
| 成功 present/late | 绿 | 成功音 | 学生全名（audio_file 命中；缺失→通用确认音）|
| 成功 duplicate=true | 绿 | 静默 | 无 |
| UNKNOWN_CARD | 红 | 失败音 | 无 |
| UNREGISTERED_UID | 红 | 失败音 | 无 |
| SESSION_NOT_RUNNING | 黄 | 短提示音 | 无（未开始 / 已结束都归这行 —— 7-17 拍板删 TIMEOUT）|
| 网络失败（离线队列）| 绿(roster 命中)/红(未命中) | 对应音 | 命中则播报 |
| 鉴权类（UNKNOWN_DEVICE 等）| 白灯闪烁 | 静默 | 无 |
"""

from __future__ import annotations

from dataclasses import dataclass

from .api.envelope import AUTH_ERROR_CODES as _AUTH_ERROR_CODES
from .audio.player import Tone
from .led.controller import LedState


@dataclass(frozen=True)
class Feedback:
    """一次签到的现场反馈指令。"""

    led: LedState
    tone: Tone | None  # None = 静默
    audio_file: str | None = None  # 学生姓名 wav；非空时优先于 tone（播名字）
    broadcast_text: str | None = None  # 播报文本（记日志 / 未来 TTS 用）
    # 入队职责不在此：离线路径由 main._handle_offline 无条件 self._queue.enqueue


def for_response(ok: bool, data: dict | None, error_code: str | None) -> Feedback:
    """后端给了业务响应时的反馈。

    `ok` / `data` / `error_code` 来自 `{ok,data}` / `{ok,error}` 信封解包后的值。
    """
    if ok:
        data = data or {}
        if data.get("duplicate"):
            # 重复签到：绿灯 + 静默 + 不播报（契约 §4.1.3 / §9）
            return Feedback(led=LedState.SUCCESS, tone=None)
        # present / late 均绿 + 成功音 + 播全名
        return Feedback(
            led=LedState.SUCCESS,
            tone=Tone.SUCCESS,
            audio_file=data.get("audio_file"),
            broadcast_text=data.get("broadcast_text"),
        )

    code = error_code or ""
    if code in _AUTH_ERROR_CODES:
        # 鉴权异常：白灯闪烁 + 静默（设备自身问题，上层去刷新令牌）
        return Feedback(led=LedState.AUTH_ERROR, tone=None)
    if code == "SESSION_NOT_RUNNING":
        # 点呼未开始 / 已结束：黄灯 + 短提示音（等待态，区别于失败）
        return Feedback(led=LedState.WAITING, tone=Tone.WAITING)
    # UNKNOWN_CARD / UNREGISTERED_UID / 其余业务错误：红灯 + 失败音
    return Feedback(led=LedState.FAIL, tone=Tone.FAIL)


def for_offline(student: dict | None) -> Feedback:
    """网络失败走离线队列时的即时反馈（契约 §6.2）。

    `student` = 本地 roster 命中的学生记录（含 student_number / name）或 None（未命中）。
    入队由上层 `_handle_offline` 负责（契约 §6.1：POST 失败一律入队）；本函数只出 LED/音/播报。
    """
    if student is not None:
        audio_file = None
        number = student.get("student_number")
        if number:
            audio_file = f"{number}.wav"
        return Feedback(
            led=LedState.SUCCESS,
            tone=Tone.SUCCESS,
            audio_file=audio_file,
            broadcast_text=student.get("name"),
        )
    # 未命中：红灯拒绝（入队仍由上层处理，后端恢复后按 UNKNOWN_CARD 等处理并出队）
    return Feedback(led=LedState.FAIL, tone=Tone.FAIL)
