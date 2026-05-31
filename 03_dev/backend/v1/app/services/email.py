"""SendGrid メール送信 (D1)。

設計権威: BACKEND_DESIGN_LOG.md §3.2 §5.6 §10-D1 + system_features.md §7.13。
- 出寮届 提交 → 役职 (R1 = メール固定)
- 学習欠席届 提交 → 学習担当 (R1)
- 学号変更 → 寮務一般教師 (R1, P1 範囲)
- 指導履歴 開示申請 → 寮務 (R1)

設計理念:
- 失败は notification_log に残す (status='failed' + last_error) → 業務 flow は止めない
- API_KEY 未設定の dev 環境では「ログだけ書いて成功扱い」にして開発を阻害しない
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# テンプレート
# ---------------------------------------------------------------
def render_application_submitted(
    *, application: models.Application, student: models.Student
) -> tuple[str, str]:
    """件名 + 本文 (text)。"""
    subject = f"[Tomoshibi] 出寮届 提出: {student.name} ({application.kind})"
    body = f"""出寮届が提出されました。承认をお願いします。

----------
学生:        {student.name} (学号 {student.student_no})
寮:          {_dorm_label(student.dorm_unit)}  / 部屋 {student.room_no}
区分:        {'留学生' if student.is_overseas else '一般寮生'}
種類:        {application.kind}
出寮日時:    {application.leave_date} {application.leave_time}
帰寮日時:    {application.return_date} {application.return_time}
出寮方法:    {application.leave_method}
帰寮方法:    {application.return_method}
----------

老師 Web 「出寮届承认」ページから承认 / 不承认 を行ってください。

— Tomoshibi (灯火) システム
"""
    return subject, body


def render_test_email(*, body_text: str) -> str:
    return body_text


def _dorm_label(dorm_unit: int) -> str:
    return {1: "1 寮 (男)", 2: "2 寮 (男)", 4: "4 寮 (女)"}.get(dorm_unit, f"{dorm_unit} 寮")


# ---------------------------------------------------------------
# SendGrid 送信
# ---------------------------------------------------------------
def _send_via_sendgrid(
    *,
    to_emails: list[str],
    subject: str,
    body_text: str,
) -> tuple[bool, int | None, str | None]:
    """実際に SendGrid API を叩く。

    Returns:
        (sent, sendgrid_status_code, error_message)
    """
    settings = get_settings()
    if not settings.sendgrid_api_key:
        logger.warning(
            "SENDGRID_API_KEY 未設定 — メール送信をスキップ (dev mode). subject=%s",
            subject,
        )
        return False, None, "SENDGRID_API_KEY not configured"

    try:
        # lazy import — 依存をオプショナルに保つ
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
    except ImportError as e:
        logger.error("sendgrid package not installed: %s", e)
        return False, None, f"sendgrid not installed: {e}"

    if not to_emails:
        return False, None, "no recipients"

    message = Mail(
        from_email=(settings.email_from, settings.email_from_name),
        to_emails=to_emails,
        subject=subject,
        plain_text_content=body_text,
    )
    try:
        client = SendGridAPIClient(settings.sendgrid_api_key)
        response = client.send(message)
        # SendGrid 2xx = 受理 (実配達は別)
        ok = 200 <= response.status_code < 300
        return ok, response.status_code, None if ok else f"HTTP {response.status_code}"
    except Exception as e:  # noqa: BLE001 — network 系は何でも来る
        logger.exception("SendGrid send failed: %s", e)
        return False, None, str(e)


# ---------------------------------------------------------------
# Public API: 出寮届 提交時通知 (#6 / R1)
# ---------------------------------------------------------------
def send_application_submitted(
    db: Session,
    *,
    application: models.Application,
    student: models.Student,
    teachers: Iterable[models.Teacher],
    to_emails: list[str],
) -> models.NotificationLog:
    """提交届を chain の全役职に送る。

    - notification_log に 1 行記録 (送信先 list は payload に格納)
    - 送信失败は status='failed' で記録、業務 flow は中断しない
    """
    subject, body = render_application_submitted(
        application=application, student=student
    )
    payload = {
        "subject": subject,
        "to": to_emails,
        "teacher_names": [t.name for t in teachers],
        "application_id": str(application.id),
        "kind": application.kind,
    }

    log = models.NotificationLog(
        channel="email",
        template_key="application_submitted",
        target_type="role",
        target_id=None,
        target_email=",".join(to_emails) if to_emails else None,
        payload=payload,
        status="pending",
        attempts=0,
    )
    db.add(log)
    db.flush()  # log.id 確定

    if not to_emails:
        log.status = "failed"
        log.last_error = "no recipients (chain 上の役职に email 登録なし)"
        log.attempts = 0
        return log

    sent, status_code, error = _send_via_sendgrid(
        to_emails=to_emails, subject=subject, body_text=body
    )
    log.attempts = 1
    if sent:
        log.status = "sent"
        log.sent_at = datetime.now(timezone.utc)
    else:
        # SENDGRID_API_KEY 未設定 (dev) は "skipped" 扱い、failed と区別
        if error and "not configured" in error:
            log.status = "pending"
            log.last_error = "dev mode: SendGrid API key not configured (skipped)"
        else:
            log.status = "failed"
            log.last_error = (error or f"HTTP {status_code}")[:500]
    return log


# ---------------------------------------------------------------
# Public API: テストメール (smoke test)
# ---------------------------------------------------------------
def send_test_email(
    db: Session,
    *,
    to: str,
    subject: str,
    body_text: str,
    actor_id: UUID | None = None,
) -> tuple[models.NotificationLog, int | None, str | None]:
    log = models.NotificationLog(
        channel="email",
        template_key="smoke_test",
        target_type="teacher",  # ad-hoc — admin or 開発者向け
        target_id=actor_id,
        target_email=to,
        payload={"subject": subject, "to": [to]},
        status="pending",
        attempts=0,
    )
    db.add(log)
    db.flush()

    sent, status_code, error = _send_via_sendgrid(
        to_emails=[to], subject=subject, body_text=body_text
    )
    log.attempts = 1
    if sent:
        log.status = "sent"
        log.sent_at = datetime.now(timezone.utc)
    else:
        log.status = "failed" if "not configured" not in (error or "") else "pending"
        log.last_error = error[:500] if error else None
    return log, status_code, error
