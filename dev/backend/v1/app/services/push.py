"""推送通知服务 — spec §7.13。

设计原则（照 email.py 的结构）：
- 失败只写 notification_log，不中断业务流
- 外部投递凭证（APNS_KEY / FCM_KEY）未配置时记 status='skipped_no_provider'，开发不受阻
- 真实 APNs / FCM 调用处留明确 stub，等凭证备齐后替换

当前 status 枚举约定（notification_log.status）：
  pending           → 默认值
  sent              → 投递成功（外部服务 2xx）
  failed            → 投递失败（网络 / provider 错误）
  skipped_no_provider → 凭证未配置（dev 环境正常状态）

⚠️ 缺口（需 iOS/Android 工程师配合才能填）：
  1. APNS_KEY（苹果推送私钥 .p8）+ APNS_KEY_ID + APNS_TEAM_ID + APNS_BUNDLE_ID
  2. FCM_KEY（Firebase Server Key 或 Service Account JSON）
  3. 客户端 App 启动时调 POST /api/v1/notifications/device-token 注册本机 token
  4. 真实 HTTP 投递代码（本文件 _send_via_apns / _send_via_fcm stub 处）
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Provider stubs（凭证备齐后在这里实现）
# ---------------------------------------------------------------


def _send_via_apns(
    token: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]],
) -> tuple[bool, str | None]:
    """APNs HTTP/2 投递 stub。

    TODO: 实现步骤
      1. 读 settings.apns_key（PEM 内容）/ settings.apns_key_id / settings.apns_team_id
      2. 用 PyJWT 签 ES256 provider token（10 分钟有效期）
      3. httpx.post("https://api.push.apple.com/3/device/{token}", ...) HTTP/2
      4. 200 → (True, None)；4xx/5xx → (False, error_str)

    需要的环境变量:
      APNS_KEY        (完整 .p8 私钥内容，含 BEGIN PRIVATE KEY 行)
      APNS_KEY_ID     (10 位字符串，Apple 后台查)
      APNS_TEAM_ID    (10 位字符串，Apple Developer 账号)
      APNS_BUNDLE_ID  (App Bundle Identifier，如 com.example.Tomoshibi)
    """
    # ⚠️ stub — 凭证未配置，直接返回未实现
    settings = get_settings()
    if not getattr(settings, "apns_key", None):
        return False, "APNS_KEY not configured"
    # 真实实现放这里 ↑ 上面 if 块之后
    return False, "APNs send not implemented yet"


def _send_via_fcm(
    token: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]],
) -> tuple[bool, str | None]:
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
        return False, "FCM_KEY not configured"
    return False, "FCM send not implemented yet"


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
) -> tuple[bool, str | None]:
    """根据平台路由到对应 provider。返回 (sent, error)。"""
    if platform == "ios":
        return _send_via_apns(token, title, body, data)
    elif platform == "android":
        return _send_via_fcm(token, title, body, data)
    return False, f"unknown platform: {platform}"


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

        sent, error = _dispatch_one(
            platform=dt.platform,
            token=dt.token,
            title=title,
            body=body,
            data=data,
        )
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
        logs.append(log)

    return logs
