"""推送通知服务 — spec §7.13。

设计原则（照 email.py 的结构）：
- 失败只写 notification_log，不中断业务流
- 外部投递凭证（APNS_KEY / FCM_KEY）未配置时记 status='skipped_no_provider'，开发不受阻
- APNs 已真实装（provider token 缓存 + HTTP/2 投递 + rollcall 模板 Time Sensitive）；
  FCM 仍是 stub（Android 不上 Google Play，走 APK 直装，推送优先级低）

当前 status 枚举约定（notification_log.status）：
  pending           → 默认值
  sent              → 投递成功（外部服务 2xx）
  failed            → 投递失败（网络 / provider 错误）
  skipped_no_provider → 凭证未配置（dev 环境正常状态）

⚠️ 上线剩余缺口：
  1. 生产 .env 填 APNS_KEY（苹果推送私钥 .p8）+ APNS_KEY_ID + APNS_TEAM_ID + APNS_BUNDLE_ID
  2. FCM_KEY（Firebase Server Key 或 Service Account JSON）+ _send_via_fcm 实装
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import httpx
import jwt as pyjwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# APNs 真实投递（spec §7.13）
# ---------------------------------------------------------------

# provider token 缓存 — 苹果要求 20 分钟~1 小时内复用同一 token，不许每条推送签新的。
# 这里 50 分钟重签一次（留 10 分钟余量）。进程级缓存，多 worker 各自持有一份即可。
_APNS_TOKEN_TTL_SECONDS = 50 * 60
_apns_token_cache: dict[str, Any] = {"token": None, "issued_at": 0.0}

# HTTP/2 连接复用 — 苹果明确要求保持长连接，别每条推送新建连接
_apns_client: httpx.Client | None = None


def _get_apns_provider_token(settings: Any) -> str:
    """签发（或复用缓存的）APNs provider token — ES256 JWT。"""
    now = time.time()
    if (
        _apns_token_cache["token"]
        and now - _apns_token_cache["issued_at"] < _APNS_TOKEN_TTL_SECONDS
    ):
        return _apns_token_cache["token"]
    token = pyjwt.encode(
        {"iss": settings.apns_team_id, "iat": int(now)},
        settings.apns_key,
        algorithm="ES256",
        headers={"kid": settings.apns_key_id},
    )
    _apns_token_cache["token"] = token
    _apns_token_cache["issued_at"] = now
    return token


def _get_apns_client() -> httpx.Client:
    """惰性建 HTTP/2 客户端并复用（连接池由 httpx 管理）。"""
    global _apns_client
    if _apns_client is None:
        _apns_client = httpx.Client(http2=True, timeout=10.0)
    return _apns_client


def _send_via_apns(
    token: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]],
    template_key: str = "generic",
) -> tuple[bool, str | None, bool]:
    """APNs HTTP/2 真实投递。

    返回 (成功, 错误信息, 令牌已永久失效)。
    永久失效 = APNs reason 为 Unregistered / BadDeviceToken，上层应置 revoked_at。

    凭证（生产 .env 设置，任一缺失 → 返回 not configured，上层记 skipped_no_provider）:
      APNS_KEY        (完整 .p8 私钥内容，含 BEGIN PRIVATE KEY 行)
      APNS_KEY_ID     (10 位字符串，Apple 后台查)
      APNS_TEAM_ID    (10 位字符串，Apple Developer 账号)
      APNS_BUNDLE_ID  (App Bundle Identifier，正式版 = com.itsuki.tomoshibi)

    点呼相关模板（template_key 以 rollcall 开头）标记为 Time Sensitive 紧急通知 —
    iOS 端 entitlements 已开 time-sensitive 能力，专注模式 / 静音下仍能立即送达。
    """
    settings = get_settings()
    missing = [
        name
        for name, value in (
            ("APNS_KEY", settings.apns_key),
            ("APNS_KEY_ID", settings.apns_key_id),
            ("APNS_TEAM_ID", settings.apns_team_id),
            ("APNS_BUNDLE_ID", settings.apns_bundle_id),
        )
        if not value
    ]
    if missing:
        return False, f"{'/'.join(missing)} not configured", False

    aps: dict[str, Any] = {
        "alert": {"title": title, "body": body},
        "sound": "default",
    }
    if template_key.startswith("rollcall"):
        # 点呼提醒是分钟级紧急事项 — 苹果的 interruption-level 分级里
        # time-sensitive 可穿透专注模式（勿扰以外），普通通知则不加
        aps["interruption-level"] = "time-sensitive"
    payload: dict[str, Any] = {"aps": aps}
    if data:
        payload.update(data)  # 自定义键放 aps 外层（苹果规范）

    host = (
        "https://api.sandbox.push.apple.com"
        if settings.apns_use_sandbox
        else "https://api.push.apple.com"
    )
    try:
        provider_token = _get_apns_provider_token(settings)
        resp = _get_apns_client().post(
            f"{host}/3/device/{token}",
            json=payload,
            headers={
                "authorization": f"bearer {provider_token}",
                "apns-topic": settings.apns_bundle_id,
                "apns-push-type": "alert",
                "apns-priority": "10",
            },
        )
    except Exception as exc:  # noqa: BLE001 — 网络层任何异常都转 (False, 错误串)
        return False, f"APNs request error: {exc}", False

    if resp.status_code == 200:
        return True, None, False
    # 4xx/5xx — 苹果返回 JSON {"reason": "..."}，截前 200 字进 log 方便排查
    reason = ""
    try:
        reason = resp.json().get("reason", "") or ""
    except Exception:  # noqa: BLE001 — 响应体非 JSON 时忽略，仍记原始 text
        reason = ""
    permanent = reason in ("Unregistered", "BadDeviceToken")
    return False, f"APNs {resp.status_code}: {resp.text[:200]}", permanent


def _send_via_fcm(
    token: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]],
) -> tuple[bool, str | None, bool]:
    """FCM HTTP v1 投递 stub。

    TODO: 实现步骤
      1. 读 settings.fcm_key（Service Account JSON 字符串）
      2. 用 google-auth 库获取 OAuth2 Bearer token
      3. httpx.post("https://fcm.googleapis.com/v1/projects/{project}/messages:send", ...)
      4. 200 → (True, None)；4xx/5xx → (False, error_str)

    需要的环境变量:
      FCM_KEY  (Firebase Service Account JSON 内容，或 Server Key 字符串)
    """
    settings = get_settings()
    if not getattr(settings, "fcm_key", None):
        return False, "FCM_KEY not configured", False
    return False, "FCM send not implemented yet", False


# ---------------------------------------------------------------
# 内部：给单个 token 发一条推送
# ---------------------------------------------------------------
def _dispatch_one(
    *,
    platform: str,
    token: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]],
    template_key: str = "generic",
) -> tuple[bool, str | None, bool]:
    """根据平台路由到对应 provider。返回 (sent, error, token_permanently_invalid)。"""
    if platform == "ios":
        return _send_via_apns(token, title, body, data, template_key=template_key)
    elif platform == "android":
        return _send_via_fcm(token, title, body, data)
    return False, f"unknown platform: {platform}", False


# ---------------------------------------------------------------
# Public API：给指定学生发推送
# ---------------------------------------------------------------
def send_push(
    db: Session,
    *,
    student_id: UUID,
    title: str,
    body: str,
    template_key: str = "generic",
    data: Optional[dict[str, Any]] = None,
) -> list[models.NotificationLog]:
    """给某学生的所有有效设备发推送通知。

    - 查该学生所有 revoked_at IS NULL 的 device_tokens
    - 每个设备写一条 notification_log(channel='push')
    - 调外部投递；凭证未配置时 status='skipped_no_provider'（dev 正常）
    - 失败不 raise，调用方业务不中断
    - 返回所有写入的 NotificationLog 列表（可能为空，如学生没有注册设备）
    """
    tokens = db.scalars(
        select(models.DeviceToken).where(
            models.DeviceToken.student_id == student_id,
            models.DeviceToken.revoked_at.is_(None),
        )
    ).all()

    if not tokens:
        logger.info(
            "send_push: student %s has no active device tokens, skipping", student_id
        )
        return []

    logs: list[models.NotificationLog] = []
    for dt in tokens:
        payload = {
            "title": title,
            "body": body,
            "platform": dt.platform,
            "token_id": str(dt.id),
            **({"data": data} if data else {}),
        }
        log = models.NotificationLog(
            channel="push",
            template_key=template_key,
            target_type="student",
            target_id=student_id,
            target_email=None,
            payload=payload,
            status="pending",
            attempts=0,
        )
        db.add(log)
        db.flush()  # log.id 确定

        # F-codex-低-01：把投递调用包进 try/except，兑现「失败不 raise，调用方业务不中断」
        # 契约（见本函数 docstring）。_dispatch_one 内的 provider 抛意外异常（网络错 / SDK
        # bug）时不再炸穿到调用方业务，而是当作本设备投递失败记 log 继续下一台设备。
        try:
            sent, error, token_dead = _dispatch_one(
                platform=dt.platform,
                token=dt.token,
                title=title,
                body=body,
                data=data,
                template_key=template_key,
            )
        except Exception as exc:  # noqa: BLE001 — 推送投递任何异常都不得中断业务
            sent, error, token_dead = False, f"dispatch raised: {exc}", False
        log.attempts = 1
        if sent:
            log.status = "sent"
            log.sent_at = datetime.now(timezone.utc)
        elif error and ("not configured" in error or "not implemented" in error):
            # 凭证未配置 / stub 未实现 → dev 正常状态，不算 failed
            log.status = "skipped_no_provider"
            log.last_error = error[:500]
            logger.warning(
                "send_push: provider not ready (platform=%s): %s", dt.platform, error
            )
        else:
            log.status = "failed"
            log.last_error = (error or "unknown error")[:500]
            logger.error(
                "send_push: failed (platform=%s token_id=%s): %s",
                dt.platform,
                dt.id,
                error,
            )
            # 死令牌（APNs Unregistered / BadDeviceToken）→ 置 revoked_at，避免下次仍被拾取
            if token_dead:
                dt.revoked_at = datetime.now(timezone.utc)
                logger.info(
                    "send_push: revoked dead device token id=%s (platform=%s)",
                    dt.id,
                    dt.platform,
                )
        logs.append(log)

    return logs
