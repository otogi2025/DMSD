"""采集事件模型 + 签到请求体构造。

线程 A（硬件采集）把读到的东西封装成本模块的事件对象塞进队列；线程 B（网络反馈）
从队列取出后调 `to_checkin_body()` 生成 `POST /rollcall/device-checkins` 的请求体。

请求体字段严格对齐 `Device_Contract.md` §4.1。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CardEvent:
    """路径 A：实体卡刷卡事件。

    `card_uid` = NTAG215 UID，14 位小写 hex（7 字节）。
    `swipe_time` = 线程 A 采集那一刻盖的 NTP 校准 JST 时间戳（ISO 8601）。
    """

    card_uid: str
    swipe_time: str

    def to_checkin_body(self) -> dict:
        # 路径 A 不带 idempotency_key —— 后端按「同生同场次仅一条」去重（契约 §4.1）
        return {
            "path_type": "A",
            "card_uid": self.card_uid,
            "swipe_time": self.swipe_time,
        }


@dataclass(frozen=True)
class PhoneEvent:
    """路径 B：手机把身份数据写进 ST25DV 邮箱的事件。

    `student_id` / `idempotency_key` 来自 Mailbox 载荷解析（契约 §7）。
    `checkin_type` = 载荷第 2 字节（0x01 点呼 / 0x02 晚自习），本波仅记录不入请求体
    （device-checkins 请求体无对应字段，设备不感知 session 类型）。
    """

    student_id: str
    idempotency_key: str
    swipe_time: str
    checkin_type: int = 0x01

    def to_checkin_body(self) -> dict:
        return {
            "path_type": "B",
            "student_id": self.student_id,
            "idempotency_key": self.idempotency_key,
            "swipe_time": self.swipe_time,
        }


@dataclass(frozen=True)
class ControlEvent:
    """WebSocket 推来的控制事件，经队列交给线程 B 处理。

    `kind` 取值：`roster_updated` / `audio_updated` / `session_started` / `session_ended`。
    `data` = 消息原始 data 字段。
    """

    kind: str
    data: dict


# 队列里可能出现的三类事件
CheckinEvent = CardEvent | PhoneEvent
