"""`{ok,data}` / `{ok,error}` 信封解包（API_CONVENTIONS §1）。

后端所有 HTTP 响应都包一层信封：
- 成功：`{"ok": true, "data": {...}}`
- 失败：`{"ok": false, "error": {"code", "message", "detail"}}`

本模块把 httpx 响应解成结构化 `ApiResponse`；网络层失败（连不上 / 超时 / 5xx）抛
`NetworkError`，由上层转入离线队列（契约 §6.1：网络 / 5xx 一律降级）。
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


class NetworkError(Exception):
    """网络层失败（连接错误 / 超时 / 5xx）—— 触发离线降级。"""


# 鉴权类错误码 —— 全设备唯一真值，反馈层（白灯闪烁）与离线队列（不出队、停补传刷令牌）
# 必须认同一套，两边各存一份曾导致漏码丢签到（2026-07-18 cursor 审查 blocker 2）。
#
# `INVALID_CREDENTIALS` 是后端 deps.get_current_device 在 JWT 解码失败 / 令牌世代过期时
# 实际返回的码（信封保留 detail.code，不会改写成 UNAUTHORIZED）—— 漏了它，令牌过期时
# 攒了一晚的补传会被当成「终态业务错误」逐条出队丢光。
AUTH_ERROR_CODES = frozenset(
    {
        "UNAUTHORIZED",
        "INVALID_CREDENTIALS",
        "FORBIDDEN",
        "UNKNOWN_DEVICE",
        "DEVICE_NOT_ACTIVE",
        "INVALID_SIGNATURE",
    }
)


@dataclass(frozen=True)
class ApiResponse:
    """解包后的业务响应。"""

    ok: bool
    http_status: int
    data: dict | None = None
    error: dict | None = None

    @property
    def error_code(self) -> str | None:
        if self.error:
            return self.error.get("code")
        return None


def unwrap(response: httpx.Response) -> ApiResponse:
    """把 httpx 响应解成 `ApiResponse`。

    5xx → `NetworkError`（当作网络失败，契约 §6.1）。
    4xx 业务错误 → `ApiResponse(ok=False, error=...)`（正常返回，交反馈逻辑判定）。
    2xx → `ApiResponse(ok=True, data=...)`。
    响应体不是合法 JSON 信封 → `NetworkError`（后端异常，走降级）。
    """
    if response.status_code >= 500:
        raise NetworkError(f"后端 5xx：{response.status_code}")
    try:
        body = response.json()
    except ValueError as exc:
        raise NetworkError(f"响应不是合法 JSON：{exc}") from exc
    if not isinstance(body, dict) or "ok" not in body:
        raise NetworkError("响应缺少 ok 信封字段")
    if body["ok"]:
        return ApiResponse(
            ok=True, http_status=response.status_code, data=body.get("data")
        )
    return ApiResponse(
        ok=False, http_status=response.status_code, error=body.get("error") or {}
    )
