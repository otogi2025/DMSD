"""日语播报 + 提示音 —— `aplay` 子进程播放。

契约 §9 声音列（后端预生成 wav 下发，本机只播放，设计日志 §10-D3）：
- 成功：先播学生姓名 wav（`{student_number}.wav`，缓存命中）；缺失 → 通用确认音（成功提示音）
- 失败：失败音
- SESSION_NOT_RUNNING：短提示音（等待音）
- duplicate=true / 鉴权异常：静默（不播）

内置 3 个提示音（成功 / 失败 / 等待）由 `tools/gen_tones.py` 用正弦波生成，放 `assets/`。
「新声音掐断老声音」：播新音前先杀掉上一个未放完的 aplay 进程（设计日志 §3.1）。
"""

from __future__ import annotations

import subprocess
import threading
from enum import Enum
from pathlib import Path

# 内置提示音资源目录（本包同级的 assets/）
_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"


class Tone(Enum):
    """内置提示音。"""

    SUCCESS = "success"  # 成功 / 通用确认音
    FAIL = "fail"  # 失败音
    WAITING = "waiting"  # 等待音（SESSION_NOT_RUNNING 短提示）


_TONE_FILES = {
    Tone.SUCCESS: "tone_success.wav",
    Tone.FAIL: "tone_fail.wav",
    Tone.WAITING: "tone_waiting.wav",
}


class AudioPlayer:
    """aplay 播放器。

    `audio_output` = aplay 的 `-D` 设备串（契约 §10 config `audio_output`，如 `plughw:1,0`）。
    `cache_dir` = 学生姓名 wav 缓存目录（契约 §4.3 差量下载落地处）。
    """

    def __init__(
        self,
        audio_output: str,
        cache_dir: Path,
        assets_dir: Path = _ASSETS_DIR,
        aplay_bin: str = "aplay",
    ) -> None:
        self._audio_output = audio_output
        self._cache_dir = Path(cache_dir)
        self._assets_dir = Path(assets_dir)
        self._aplay_bin = aplay_bin
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def _play_file(self, path: Path) -> bool:
        """播放指定 wav；文件不存在返回 False 由调用方降级。"""
        if not path.exists():
            return False
        with self._lock:
            self._stop_locked()  # 新声音掐断老声音
            cmd = [self._aplay_bin, "-q", "-D", self._audio_output, str(path)]
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                # 无 aplay（开发机）—— 视为播放失败但不崩
                self._proc = None
                return False
        return True

    def play_tone(self, tone: Tone) -> bool:
        """播内置提示音。"""
        return self._play_file(self._assets_dir / _TONE_FILES[tone])

    def play_name(self, audio_file: str) -> bool:
        """播学生姓名 wav（缓存命中）；缺失 → 通用确认音（成功提示音）。契约 §9。"""
        if self._play_file(self._cache_dir / audio_file):
            return True
        return self.play_tone(Tone.SUCCESS)

    def _stop_locked(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:  # noqa: BLE001
                pass
        self._proc = None

    def stop(self) -> None:
        with self._lock:
            self._stop_locked()

    def close(self) -> None:
        self.stop()
