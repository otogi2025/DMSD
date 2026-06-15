"""操作履历审计中间件 — 老师写操作全量自动记日志（operation audit log）。

设计（2026-06-16 itsuki 拍板）：
- 范围：老师对后端发起的所有「写操作」(POST/PUT/PATCH/DELETE) 全部自动记一笔。
- 做法：一道总关卡(纯 ASGI 中间件)统一记，不逐个端点手写埋点 —— 自动覆盖现有 + 将来端点、不漏。
- 记什么：谁(actor_id=老师)、何时(created_at)、哪个操作(action = "METHOD 归一化路径")、
  成功状态(只记 2xx/3xx 成功操作)、请求详情(payload, 脱敏后存请求体/查询参数/状态码)、ip/ua。
- 只记老师 actor（学生 / 匿名请求跳过 —— 本功能是「老师操作记录」）。
- 写库失败绝不影响请求本身（try/except 吞掉 + warning）。
- 写库在响应发完后经 run_in_threadpool 跑（同步 SQLAlchemy 不阻塞事件循环）。

读取侧（老师网页「操作履歴」页）= routers/audit_log.py，按权限组 C_AUDIT_LOG 只给管理角色看。

为什么用纯 ASGI 中间件而不是 @app.middleware("http")：纯 ASGI 能用 receive 包装稳妥捕获
请求体（BaseHTTPMiddleware 读 body 后再 call_next 在历史上有兼容坑），用 send 包装拿响应状态码，
版本无关、不依赖 Starlette 内部路由细节（action 用正则归一化路径，不依赖 scope["route"]）。
"""

from __future__ import annotations

import json
import logging
import re
import uuid as _uuid
from typing import Optional
from urllib.parse import parse_qsl

from starlette.concurrency import run_in_threadpool

from . import models, security
from .database import SessionLocal

logger = logging.getLogger("tomoshibi.audit")

# 记的方法（写操作）。GET / HEAD / OPTIONS 是读，不记。
_MUTATING = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# 登录 / 登出走 /sessions：登录请求带明文密码且此刻还没有老师 token（actor 解析不出、本会跳过），
# 整段一律不记 —— 它们不是对宿舍数据的「操作」。
_SKIP_PREFIXES = ("/api/v1/sessions",)

# 注：部分端点（注册码 refresh/close、出寮届审批等约 12 个 router）内部还会写自己的语义级
# audit 行（action 形如 "registration_code.refresh"，带语义详情，供各功能自身使用）。
# 中间件不跳过它们 —— 而是统一记一条 "METHOD 归一化路径" 行；操作记录页的读取端点只展示
# 中间件这种 "METHOD 路径" 行（见 routers/audit_log.py 的 action 前缀过滤），所以同一操作
# 在操作记录页只出现一次、不与语义行重复。语义行仍留在表里供各功能（如注册码历史）自用。

_MAX_BODY_BYTES = 16 * 1024  # 超 16KB 的请求体不入 payload（文件上传等），存标记
# 键名含这些词的值脱敏（密码 / 令牌 / 密钥 / 凭据 / cookie 等绝不入库）
# 审计场景过度脱敏（误伤普通字段）远比漏脱敏安全 —— 宁可多 *** 也不让密钥落库。
_SENSITIVE_KEY_RE = re.compile(
    r"pass|pwd|secret|token|credential|api[_-]?key|apikey|authorization|cookie|otp",
    re.IGNORECASE,
)
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_INT_RE = re.compile(r"^\d+$")


def _normalize_path(path: str) -> str:
    """把路径里的具体 id 段替换成 {id}，得到稳定的操作键（去掉 /api/v1 前缀）。

    例：/api/v1/discipline/3fa.../revoke → discipline/{id}/revoke
    """
    p = path
    if p.startswith("/api/v1/"):
        p = p[len("/api/v1/") :]
    p = p.strip("/")
    if not p:
        return ""
    segs = []
    for seg in p.split("/"):
        if _UUID_RE.match(seg) or _INT_RE.match(seg):
            segs.append("{id}")
        else:
            segs.append(seg)
    return "/".join(segs)


def _first_uuid_in_path(path: str) -> Optional[_uuid.UUID]:
    """路径里第一个 UUID 段当 target_id（没有则 None）。"""
    for seg in path.split("/"):
        if _UUID_RE.match(seg):
            try:
                return _uuid.UUID(seg)
            except ValueError:
                return None
    return None


def _resource_of(normalized: str) -> Optional[str]:
    """归一化路径首段当 target_type（资源名，如 discipline / applications），限 32 字符。"""
    head = normalized.split("/", 1)[0] if normalized else ""
    return head[:32] or None


def _sanitize(obj):
    """递归脱敏：键名含密码 / 令牌等的值替换成 '***'。只处理 dict/list，列表截断防超大。"""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and _SENSITIVE_KEY_RE.search(k):
                out[k] = "***"
            else:
                out[k] = _sanitize(v)
        return out
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj[:50]]
    return obj


def _header(scope, name: bytes) -> Optional[str]:
    """从 ASGI scope 取某个请求头（小写字节名），没有则 None。"""
    for k, v in scope.get("headers", []):
        if k == name:
            return v.decode("latin-1", "ignore")
    return None


def _teacher_id_from_scope(scope) -> Optional[_uuid.UUID]:
    """从 Authorization 头解析老师身份；非老师 / 无 token / 解析失败 → None（不记）。"""
    auth = _header(scope, b"authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        return None
    if not str(payload.get("role", "")).startswith("teacher:"):
        return None
    try:
        return _uuid.UUID(payload.get("sub"))
    except (TypeError, ValueError):
        return None


def _write_audit_row(
    actor_id: _uuid.UUID,
    action: str,
    target_type: Optional[str],
    target_id: Optional[_uuid.UUID],
    payload: dict,
    ip_address: Optional[str],
    user_agent: Optional[str],
) -> None:
    """同步写一条 audit_logs（独立 session，失败只 warning 不抛）。"""
    db = SessionLocal()
    try:
        # 去规范化 actor 的 is_demo 到行上：操作记录页据此做演示隔离、不依赖事后 join teachers，
        # 硬删老师后其历史操作行仍可见（codex M3）。老师不存在（极罕见竞态）→ None。
        actor = db.get(models.Teacher, actor_id)
        actor_is_demo = actor.is_demo if actor is not None else None
        db.add(
            models.AuditLog(
                actor_type="teacher",
                actor_id=actor_id,
                actor_is_demo=actor_is_demo,
                action=action[:128],
                target_type=target_type,
                target_id=target_id,
                payload=payload,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.warning("[audit] 写操作日志失败 action=%s", action, exc_info=True)
    finally:
        db.close()


class AuditLogMiddleware:
    """纯 ASGI 中间件 — 见模块 docstring。

    捕获请求体(receive 包装) + 响应状态(send 包装)，响应完成后（成功且 actor 为老师时）
    经 run_in_threadpool 异步写一条 audit_logs。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        path = scope.get("path", "")
        if (
            method not in _MUTATING
            or not path.startswith("/api/v1/")
            or path.startswith(_SKIP_PREFIXES)
        ):
            await self.app(scope, receive, send)
            return

        # —— 是否捕获请求体（仅 JSON 且体积可控；文件上传 / 超大不抓）——
        content_type = (_header(scope, b"content-type") or "").lower()
        try:
            content_length = int(_header(scope, b"content-length") or "0")
        except ValueError:
            content_length = 0
        is_json = "application/json" in content_type
        capture_body = is_json and content_length <= _MAX_BODY_BYTES
        # JSON 但 Content-Length 已超限 → 不抓正文，但要在 payload 留「省略」标记
        json_oversized = is_json and content_length > _MAX_BODY_BYTES

        body_chunks: list[bytes] = []
        body_total = 0
        body_too_large = False

        async def receive_wrapper():
            nonlocal body_total, body_too_large
            message = await receive()
            if capture_body and message.get("type") == "http.request":
                chunk = message.get("body", b"")
                body_total += len(chunk)
                if body_total > _MAX_BODY_BYTES:
                    body_too_large = True
                    body_chunks.clear()
                elif not body_too_large:
                    body_chunks.append(chunk)
            return message

        status_holder = {"code": 0}

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                status_holder["code"] = message.get("status", 0)
            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)

        # —— 响应已发完：只记成功(2xx/3xx)的老师写操作，绝不影响请求 ——
        try:
            status_code = status_holder["code"]
            if not (200 <= status_code < 400):
                return
            actor_id = _teacher_id_from_scope(scope)
            if actor_id is None:
                return

            normalized = _normalize_path(path)
            action = f"{method} {normalized}"

            body_obj = None
            if capture_body and not body_too_large and body_chunks:
                try:
                    body_obj = _sanitize(
                        json.loads(b"".join(body_chunks).decode("utf-8"))
                    )
                except (ValueError, UnicodeDecodeError):
                    body_obj = None
            elif body_too_large or json_oversized:
                body_obj = "<省略: リクエストが大きすぎます>"

            payload: dict = {"method": method, "path": path, "status": status_code}
            # 查询参数也要脱敏（?token=... 等不能原样落库），按键名解析后脱敏存 dict。
            query = scope.get("query_string", b"").decode("latin-1", "ignore")
            if query:
                payload["query"] = _sanitize(dict(parse_qsl(query)))
            if body_obj is not None:
                payload["body"] = body_obj

            # client ip — 优先 X-Forwarded-For（反向代理后），否则 scope client
            xff = _header(scope, b"x-forwarded-for")
            if xff:
                ip = xff.split(",")[0].strip()
            else:
                client = scope.get("client")
                ip = client[0] if client else None
            user_agent = _header(scope, b"user-agent")

            await run_in_threadpool(
                _write_audit_row,
                actor_id,
                action,
                _resource_of(normalized),
                _first_uuid_in_path(path),
                payload,
                ip,
                user_agent,
            )
        except Exception:
            logger.warning("[audit] 操作日志中间件记录异常", exc_info=True)
