"""NFC 硬件抽象接口 —— 隔离真实硬件，Mac 无硬件也能跑测试与 --simulate。

设计原则（任务要求）：所有硬件访问都藏在接口后。真实实现在 `pn532_reader.py` /
`st25dv.py`（带 import 守卫），假实现在本模块，供测试与 --simulate 用。
"""

from __future__ import annotations

import collections
from abc import ABC, abstractmethod


class CardReader(ABC):
    """实体卡读头抽象（路径 A）。"""

    @abstractmethod
    def read_uid(self, timeout: float = 0.5) -> str | None:
        """轮询一次，读到卡返回 14 位小写 hex UID，超时无卡返回 None。"""

    def close(self) -> None:
        """释放硬件资源（默认空实现）。"""


class MailboxReader(ABC):
    """ST25DV 邮箱读取抽象（路径 B）。"""

    @abstractmethod
    def poll(self) -> bytes | None:
        """检查邮箱是否有手机写入的新消息。

        有则读走并复位邮箱，返回原始字节（未经载荷校验）；无则返回 None。
        """

    def close(self) -> None:
        """释放硬件资源（默认空实现）。"""


class FakeCardReader(CardReader):
    """假卡读头 —— 从预置队列吐 UID，供测试用。"""

    def __init__(self, uids: list[str] | None = None) -> None:
        self._uids: collections.deque[str] = collections.deque(uids or [])

    def feed(self, uid: str) -> None:
        self._uids.append(uid)

    def read_uid(self, timeout: float = 0.5) -> str | None:
        if self._uids:
            return self._uids.popleft()
        return None


class FakeMailboxReader(MailboxReader):
    """假邮箱 —— 从预置队列吐原始载荷字节，供测试用。"""

    def __init__(self, payloads: list[bytes] | None = None) -> None:
        self._payloads: collections.deque[bytes] = collections.deque(payloads or [])

    def feed(self, payload: bytes) -> None:
        self._payloads.append(payload)

    def poll(self) -> bytes | None:
        if self._payloads:
            return self._payloads.popleft()
        return None
