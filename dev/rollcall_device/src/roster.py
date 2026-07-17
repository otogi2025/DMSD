"""本地名单缓存 —— 断网兜底放行（契约 §4.2 + §6.2）。

后端 `GET /devices/me/roster` 返回 `{generated_at, students: [{student_id,
student_number, name, card_uids: []}]}`（仅 active 非演示学生）。本模块把它落盘到
`data_dir/roster.json`，并提供按 card_uid / student_id 的命中查询。

断网时线程 B 用它做即时反馈：命中 → 绿灯 + 播报放行；未命中 → 红灯拒绝（契约 §6.2）。
毕业 / 退寮学生随刷新自然消失（后端只下发 active 名单，覆盖式写盘）。
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Roster:
    """内存名单 + 两个索引（card_uid → 学生 / student_id → 学生）。"""

    generated_at: str = ""
    students: list[dict] = field(default_factory=list)
    _by_uid: dict[str, dict] = field(default_factory=dict, repr=False)
    _by_student_id: dict[str, dict] = field(default_factory=dict, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def _rebuild_index(self) -> None:
        self._by_uid = {}
        self._by_student_id = {}
        for stu in self.students:
            sid = stu.get("student_id")
            if sid:
                self._by_student_id[sid] = stu
            for uid in stu.get("card_uids", []) or []:
                self._by_uid[str(uid).lower()] = stu

    def replace(self, generated_at: str, students: list[dict]) -> None:
        """整表替换 + 重建索引（收到新名单时调）。"""
        with self._lock:
            self.generated_at = generated_at
            self.students = list(students)
            self._rebuild_index()

    def find_by_uid(self, card_uid: str) -> dict | None:
        with self._lock:
            return self._by_uid.get(card_uid.lower())

    def find_by_student_id(self, student_id: str) -> dict | None:
        with self._lock:
            return self._by_student_id.get(student_id)

    def size(self) -> int:
        with self._lock:
            return len(self.students)


def load_roster(path: str | Path) -> Roster:
    """从磁盘加载名单缓存；文件不存在 / 损坏 → 返回空名单。"""
    roster = Roster()
    p = Path(path)
    if not p.exists():
        return roster
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return roster
    roster.replace(data.get("generated_at", ""), data.get("students", []) or [])
    return roster


def save_roster(path: str | Path, generated_at: str, students: list[dict]) -> None:
    """把名单覆盖式写盘（原子写：先写临时文件再替换）。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": generated_at, "students": students}
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
