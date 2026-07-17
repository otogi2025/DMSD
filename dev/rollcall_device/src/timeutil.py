"""时间工具 —— 全链路 JST（日本标准时间，UTC+9）。

契约依据：
- `specs/API_CONVENTIONS.md` §12：所有时间戳用 ISO 8601 带 JST 时区偏移（如
  `2026-07-17T21:55:00+09:00`），不用 UTC 的 `Z` 结尾、不用 UNIX 秒数。
- `specs/rollcall/Device_Contract.md` §3：设备给签到盖的 `swipe_time` 由本机 NTP
  校准，格式同上。

本模块只提供「取当前 JST 时间」与「ISO 串解析」两个纯函数，不含硬件依赖，可在 Mac 直接跑测试。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# JST 固定偏移 +09:00（日本无夏令时，可写死）
JST = timezone(timedelta(hours=9))


def now_jst() -> datetime:
    """返回当前 JST 时间（带时区信息）。

    假定系统时钟已由 systemd-timesyncd / NTP 校准（部署 SOP 要求开启对时）。
    """
    return datetime.now(JST)


def now_jst_iso() -> str:
    """返回当前 JST 时间的 ISO 8601 字符串，秒精度，带 `+09:00` 偏移。

    例：`2026-07-17T21:55:00+09:00`。用作签到请求里的 `swipe_time` 与认证请求里的 `ts`。
    """
    return now_jst().isoformat(timespec="seconds")


def parse_iso(value: str) -> datetime:
    """解析 ISO 8601 时间串为带时区的 datetime。

    后端回传的 `expires_at`（令牌过期时刻）等字段用它解析。缺时区信息时按 JST 补齐。
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=JST)
    return parsed
