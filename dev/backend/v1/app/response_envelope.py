"""统一响应信封 {ok, data} / {ok, error}。

成功：中间件包 2xx JSON；失败：异常处理器统一成信封。
排除：路径白名单（/healthz 等）+ Content-Type 非 JSON + 204 + WebSocket（天然不进 http 中间件）。
契约真值：specs/API_CONVENTIONS.md §1 / §14 / §15。

实现用纯 ASGI（不用 BaseHTTPMiddleware）—— 后者在 Starlette 下会重复跑请求体 /
搞乱 TestClient + SQLAlchemy session，审计中间件同理已避开。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("tomoshibi.envelope")

# 是 JSON 但不应包信封的路径（探活 / OpenAPI 机器可读表 / 根欢迎页）
_EXCLUDED_PATHS = frozenset(
    {
        "/",
        "/healthz",
        "/openapi.json",
    }
)

# 已知大 JSON payload 端点 — 走字节拼接包装，避免整包 json.loads/dumps 双倍峰值内存
_STREAM_WRAP_PATHS = frozenset(
    {
        "/api/v1/devices/me/roster",
    }
)

# HTTP 状态 → 兜底错误码（detail 为纯字符串时用；§14）
_STATUS_CODE_FALLBACK: dict[int, str] = {
    400: "INVALID_INPUT",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "DUPLICATE_REQUEST",
    410: "DEVICE_NOT_ACTIVE",
    422: "INVALID_INPUT",
    429: "RATE_LIMITED",
    500: "INTERNAL",
}


def build_error_body(
    *,
    code: str,
    message: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """组装失败信封。ok=false 时不含 data 键（互斥规则 §1）。"""
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "detail": detail if detail is not None else {},
    }
    return {"ok": False, "error": error}


def error_body_from_http_detail(status_code: int, detail: Any) -> dict[str, Any]:
    """把 HTTPException.detail 转成失败信封。

    业务路由几乎全是 detail={"code","message",...}；
    字符串 detail 按 §14 补 code。
    """
    if isinstance(detail, dict) and "code" in detail:
        code = str(detail["code"])
        message = str(detail.get("message") or code)
        extra = {k: v for k, v in detail.items() if k not in ("code", "message")}
        return build_error_body(code=code, message=message, detail=extra or {})
    if isinstance(detail, str):
        code = _STATUS_CODE_FALLBACK.get(status_code, "INVALID_INPUT")
        return build_error_body(code=code, message=detail, detail={})
    code = _STATUS_CODE_FALLBACK.get(status_code, "INVALID_INPUT")
    return build_error_body(
        code=code,
        message="请求无法处理",
        detail={"received": detail},
    )


def _header_value(headers: list[tuple[bytes, bytes]], name: bytes) -> str:
    for k, v in headers:
        if k.lower() == name:
            return v.decode("latin-1", "ignore")
    return ""


class ResponseEnvelopeMiddleware:
    """成功响应包 {ok:true, data:...}。挂在 AuditLogMiddleware 内层。

    纯 ASGI：拦截 http.response.start / body，对符合条件的 JSON 2xx 重写 body。
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in _EXCLUDED_PATHS:
            await self.app(scope, receive, send)
            return

        start_message: Message | None = None
        body_chunks: list[bytes] = []
        should_buffer = False

        async def send_wrapper(message: Message) -> None:
            nonlocal start_message, should_buffer

            if message["type"] == "http.response.start":
                start_message = message
                status = message["status"]
                headers = list(message.get("headers", []))
                content_type = _header_value(headers, b"content-type")
                media = content_type.split(";")[0].strip().lower()
                should_buffer = (
                    status != 204
                    and 200 <= status < 300
                    and media == "application/json"
                )
                if not should_buffer:
                    await send(message)
                # 若要缓冲：先不发 start，等 body 收齐再一起发（可能改写）
                return

            if message["type"] == "http.response.body":
                if not should_buffer:
                    await send(message)
                    return

                body_chunks.append(message.get("body", b""))
                if message.get("more_body", False):
                    return

                # body 收齐 → 包信封后发出
                assert start_message is not None
                raw = b"".join(body_chunks)
                # 大列表端点：不整包反序列化，直接拼 {ok,data}（这些端点不会预包信封）
                if path in _STREAM_WRAP_PATHS:
                    wrapped_bytes = _wrap_json_body_stream(raw)
                else:
                    wrapped_bytes = _wrap_json_body(raw)
                headers = [
                    (k, v)
                    for k, v in start_message.get("headers", [])
                    if k.lower() not in (b"content-length", b"content-type")
                ]
                headers.append((b"content-type", b"application/json"))
                headers.append(
                    (b"content-length", str(len(wrapped_bytes)).encode("ascii"))
                )
                await send(
                    {
                        "type": "http.response.start",
                        "status": start_message["status"],
                        "headers": headers,
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": wrapped_bytes,
                        "more_body": False,
                    }
                )
                return

            # 其他消息（如 http.response.trailers）原样转发
            await send(message)

        await self.app(scope, receive, send_wrapper)


def _is_already_envelope(payload: Any) -> bool:
    """强判定：已是 {ok:true/false, data|error} 信封（避免业务 JSON 恰含 ok 键被误跳过）。"""
    if not isinstance(payload, dict):
        return False
    ok = payload.get("ok")
    return (ok is True or ok is False) and ("data" in payload or "error" in payload)


def _wrap_json_body_stream(raw: bytes) -> bytes:
    """大 payload 流式包装：不 json.loads/dumps，字节拼接信封，降低峰值内存。"""
    if not raw:
        return raw
    return b'{"ok":true,"data":' + raw + b"}"


def _wrap_json_body(raw: bytes) -> bytes:
    """把原始 JSON body 包成 {ok:true, data:...}；已是信封或非 JSON 则原样。"""
    if not raw:
        return raw
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return raw
    if _is_already_envelope(payload):
        return raw
    # 已确认 raw 是合法 JSON：字节拼接包装，避免对大对象再 dumps
    return b'{"ok":true,"data":' + raw + b"}"
