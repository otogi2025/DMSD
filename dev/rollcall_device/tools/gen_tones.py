"""生成 3 个内置提示音 wav（成功 / 失败 / 等待），放 `assets/`。

只用 Python 标准库（wave + math + struct），不引 numpy，Pi 3A+ 也能现场重生成。
音频参数：16-bit PCM / 单声道 / 16kHz —— 够放提示音，文件小。

用法：
    python tools/gen_tones.py            # 写到 dev/rollcall_device/assets/
    python tools/gen_tones.py --out DIR  # 指定输出目录
"""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 16000
AMPLITUDE = 0.6  # 0~1，留余量防削顶


def _tone(freq: float, duration_s: float) -> list[float]:
    """单频正弦，带首尾淡入淡出（5ms）防爆音。"""
    total = int(SAMPLE_RATE * duration_s)
    fade = max(1, int(SAMPLE_RATE * 0.005))
    samples: list[float] = []
    for i in range(total):
        value = math.sin(2 * math.pi * freq * (i / SAMPLE_RATE))
        if i < fade:
            value *= i / fade
        elif i > total - fade:
            value *= (total - i) / fade
        samples.append(value * AMPLITUDE)
    return samples


def _silence(duration_s: float) -> list[float]:
    return [0.0] * int(SAMPLE_RATE * duration_s)


def _write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
        )
        wav.writeframes(frames)


def generate(out_dir: Path) -> list[Path]:
    """生成 3 个提示音，返回文件路径列表。"""
    # 成功：两声上行（愉悦确认）880Hz → 1320Hz
    success = _tone(880, 0.12) + _silence(0.03) + _tone(1320, 0.15)
    # 失败：低沉两声下行（否定）330Hz → 220Hz
    fail = _tone(330, 0.16) + _silence(0.03) + _tone(220, 0.22)
    # 等待：单声中频短提示（中性等待）660Hz
    waiting = _tone(660, 0.18)

    files = {
        "tone_success.wav": success,
        "tone_fail.wav": fail,
        "tone_waiting.wav": waiting,
    }
    written = []
    for name, samples in files.items():
        path = out_dir / name
        _write_wav(path, samples)
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="生成点呼机内置提示音")
    default_out = Path(__file__).resolve().parent.parent / "assets"
    parser.add_argument(
        "--out", default=str(default_out), help="输出目录（默认 assets/）"
    )
    args = parser.parse_args()
    for path in generate(Path(args.out)):
        print(f"已生成：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
