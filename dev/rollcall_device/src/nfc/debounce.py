"""UID 防抖 —— 同一张卡在时间窗内重复读到只算一次。

PN532 近场读卡时，学生把卡贴住不动会被连续读到很多次；本模块保证同一 UID 在
`window` 秒内只放行第一次。用可注入的 `clock` 便于测试（默认单调时钟）。

契约无强制窗口值，取 2 秒（任务要求）。
"""

from __future__ import annotations

import time
from collections.abc import Callable

DEFAULT_WINDOW_SECONDS = 2.0


class UidDebouncer:
    """UID 防抖器。

    `accept(uid)` 返回 True 表示这次读卡应当放行（首次或已过窗口）；返回 False 表示
    是窗口内的重复读，应忽略。
    """

    def __init__(
        self,
        window: float = DEFAULT_WINDOW_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._window = window
        self._clock = clock
        self._last_seen: dict[str, float] = {}

    def accept(self, uid: str) -> bool:
        now = self._clock()
        last = self._last_seen.get(uid)
        if last is not None and (now - last) < self._window:
            # 窗口内重复 —— 刷新时间戳（贴住不动时持续压制），但不放行
            self._last_seen[uid] = now
            return False
        self._last_seen[uid] = now
        return True

    def reset(self) -> None:
        self._last_seen.clear()
