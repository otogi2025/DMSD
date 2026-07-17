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
