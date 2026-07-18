"""离线队列 —— SQLite 落盘的断网补传队列（契约 §6）。

语义（契约 §6 + 任务要求）：
1. POST 失败（网络 / 5xx）→ 完整请求体入队（含原始 `swipe_time` 盖章值）。
2. 网络恢复 → 按入队顺序（FIFO）补传。
3. 补传得到后端响应即视为「已投递」出队：
   - 成功（ok=true，含 duplicate=true）→ 出队。
   - 终态业务错误（UNKNOWN_CARD / UNREGISTERED_UID / SESSION_NOT_RUNNING 等）
     → 出队 + 记日志（重试也不会成功）。契约 §6：`swipe_time` 晚于场次结束 →
     SESSION_NOT_RUNNING 出队不重试（7-17 拍板删 late_end/TIMEOUT 概念）。
   - 鉴权类错误（UNAUTHORIZED 等）→ 不出队、停止本轮补传，交由上层刷新令牌后再补。
   - 网络错误 / 5xx（没拿到业务响应）→ 不出队、停止本轮补传，下次再来。

补传结果判定由 `classify_replay_result()` 给出，纯函数、可单测。
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# 鉴权类错误码（契约 §2.3 / §9「白灯闪烁」类）—— 需刷新令牌，不出队。
# 单一真值在 api.envelope，反馈层用的是同一份（曾各存一份漏了 INVALID_CREDENTIALS）。
from ..api.envelope import AUTH_ERROR_CODES


class ReplayAction(Enum):
    """一条补传的处理动作。"""

    DEQUEUE = "dequeue"  # 已投递（成功或终态业务错误）→ 出队
    STOP_AUTH = "stop_auth"  # 鉴权失败 → 停补传、刷新令牌，不出队
    STOP_RETRY = "stop_retry"  # 网络未通 → 停补传、下次再来，不出队


@dataclass(frozen=True)
class QueueItem:
    """队列中的一条待补传签到。"""

    row_id: int
    body: dict  # device-checkins 请求体


def classify_replay_result(ok: bool, error_code: str | None) -> ReplayAction:
    """根据补传得到的响应决定动作（纯函数）。

    `ok` / `error_code` 来自后端业务响应；网络层失败请调用方直接传 STOP_RETRY 语义
    （见 `OfflineQueue.replay`）。
    """
    if ok:
        return ReplayAction.DEQUEUE
    if error_code in AUTH_ERROR_CODES:
        return ReplayAction.STOP_AUTH
    # 其余业务错误（UNKNOWN_CARD / UNREGISTERED_UID / SESSION_NOT_RUNNING …）
    # 均为终态：后端已判定，重试不会变好 → 出队 + 记日志
    return ReplayAction.DEQUEUE


class OfflineQueue:
    """SQLite 离线队列。线程安全（单连接 + 锁）。"""

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False：线程 B 与补传可能不同调用点，用锁自行串行化
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offline_checkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    body_json TEXT NOT NULL,
                    swipe_time TEXT NOT NULL,
                    enqueued_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )

    def enqueue(self, body: dict) -> int:
        """入队一条签到请求体，返回行 id。"""
        swipe_time = str(body.get("swipe_time", ""))
        with self._lock, self._conn:
            cur = self._conn.execute(
                "INSERT INTO offline_checkins (body_json, swipe_time) VALUES (?, ?)",
                (json.dumps(body, ensure_ascii=False), swipe_time),
            )
            return int(cur.lastrowid)

    def peek_all(self) -> list[QueueItem]:
        """按入队顺序（FIFO）返回全部待补传项。"""
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, body_json FROM offline_checkins ORDER BY id ASC"
            ).fetchall()
        return [
            QueueItem(row_id=row["id"], body=json.loads(row["body_json"]))
            for row in rows
        ]

    def delete(self, row_id: int) -> None:
        """出队指定行。"""
        with self._lock, self._conn:
            self._conn.execute("DELETE FROM offline_checkins WHERE id = ?", (row_id,))

    def count(self) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM offline_checkins"
            ).fetchone()
        return int(row["n"])

    def replay(self, sender) -> int:
        """按序补传。

        `sender(body) -> tuple[bool, str | None] | None`：
        - 返回 `(ok, error_code)`：拿到了后端业务响应。
        - 返回 `None`：网络层失败（连不上 / 5xx），本轮停止。

        返回本轮成功出队的条数。
        """
        removed = 0
        for item in self.peek_all():
            result = sender(item.body)
            if result is None:
                # 网络未通 → 停止本轮，保留剩余项下次再补
                break
            ok, error_code = result
            action = classify_replay_result(ok, error_code)
            if action is ReplayAction.DEQUEUE:
                self.delete(item.row_id)
                removed += 1
            elif action is ReplayAction.STOP_AUTH:
                # 鉴权失败 → 停补传，交上层刷新令牌，本项保留
                break
            else:  # STOP_RETRY
                break
        return removed

    def close(self) -> None:
        with self._lock:
            self._conn.close()
