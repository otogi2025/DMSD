"""Resend 邮件发送 (D1)。

設計権威: BACKEND_DESIGN_LOG.md §3.2 §5.6 §10-D1 + system_features.md §7.13。
- 出寮届 提交 → 役职 (R1 = メール固定)
- 学習欠席届 提交 → 学習担当 (R1)
- 学号変更 → 寮務一般教師 (R1, P1 範囲)

設計理念:
- 失败は notification_log に残す (status='failed' + last_error) → 業務 flow は止めない
- API_KEY 未设置的 dev 环境只记日志当成功，不阻碍开发
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
区分:        {"留学生" if student.is_overseas else "一般寮生"}
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


def render_application_decided(
    *,
    application: models.Application,
    student: models.Student,
    result: str,
    decided_role: str,
    comment: str | None,
) -> tuple[str, str]:
    """審査結果（承認 / 却下）を提出者本人へ通知する件名 + 本文。

    杭田 2026-06-04 要件: 役職への通知だけでなく、提出者にも結果を
    「残る」メールで知らせる（プッシュは消して忘れるため不可）。
    """
    is_approved = result == "approved"
    head = "承認されました" if is_approved else "却下されました"
    subject = f"[Tomoshibi] 出寮届 {head}: {student.name} ({application.kind})"

    if is_approved:
        state_line = "全役職の承認が完了しました（承認）"
        tail = "出寮の準備を進めてください。"
    else:
        state_line = f"却下（{decided_role}）"
        tail = "担当の先生に確認のうえ、必要であれば修正して再提出してください。"

    comment_block = f"コメント:    {comment}\n" if comment else ""

    body = f"""出寮届が{head}。

----------
学生:        {student.name} (学号 {student.student_no})
種類:        {application.kind}
出寮日時:    {application.leave_date} {application.leave_time}
帰寮日時:    {application.return_date} {application.return_time}
状態:        {state_line}
{comment_block}----------

{tail}

— Tomoshibi (灯火) システム
"""
    return subject, body


def render_test_email(*, body_text: str) -> str:
    return body_text


def _dorm_label(dorm_unit: int) -> str:
    return {1: "1 寮 (男)", 2: "2 寮 (男)", 4: "4 寮 (女)"}.get(
        dorm_unit, f"{dorm_unit} 寮"
    )


# ---------------------------------------------------------------
# Resend 发送
# ---------------------------------------------------------------
def _send_via_resend(
    *,
    to_emails: list[str],
    subject: str,
    body_text: str,
) -> tuple[bool, int | None, str | None]:
    """实际调 Resend API（HTTP POST https://api.resend.com/emails）。

    标准库 urllib 直接 POST，不引第三方依赖。RESEND_API_KEY 未设置时 dev 模式跳过。

    Returns:
        (sent, http_status_code, error_message)
    """
    settings = get_settings()
    if not settings.resend_api_key:
        logger.warning(
            "RESEND_API_KEY 未设置 — 跳过邮件发送 (dev mode). subject=%s",
            subject,
        )
        return False, None, "RESEND_API_KEY not configured"

    if not to_emails:
        return False, None, "no recipients"

    # lazy import — 标准库，无第三方依赖
    import json
    import urllib.error
    import urllib.request

    payload = json.dumps(
        {
            "from": f"{settings.email_from_name} <{settings.email_from}>",
            "to": to_emails,
            "subject": subject,
            "text": body_text,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        # timeout 3s（TW-019）：这次 urlopen 是同步阻塞，且调用方（applications 提交 /
        # 审批）此时仍持有未提交事务的 DB 连接。Resend 慢时连接被占住，高峰并发提交会把
        # 连接池（pool_size=5/overflow=10）占满拖慢全站。降到 3s 限定占用窗（原 10s）。
        # 彻底解法是先 commit 业务数据再后台队列投递，需引入 task queue，留 v1.1。
        with urllib.request.urlopen(req, timeout=3) as resp:
            code = resp.status
            # Resend 2xx = 受理(实际投递另算)
            ok = 200 <= code < 300
            return ok, code, None if ok else f"HTTP {code}"
    except urllib.error.HTTPError as e:
        logger.warning("Resend send failed: HTTP %s", e.code)
        return False, e.code, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 — network 系は何でも来る
        logger.exception("Resend send failed: %s", e)
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

    sent, status_code, error = _send_via_resend(
        to_emails=to_emails, subject=subject, body_text=body
    )
    log.attempts = 1
    if sent:
        log.status = "sent"
        log.sent_at = datetime.now(timezone.utc)
    else:
        # RESEND_API_KEY 未设置 (dev) 视为 skipped，跟 failed 区分
        if error and "not configured" in error:
            log.status = "pending"
            log.last_error = "dev mode: Resend API key not configured (skipped)"
        else:
            log.status = "failed"
            log.last_error = (error or f"HTTP {status_code}")[:500]
    return log


# ---------------------------------------------------------------
# Public API: 审批结果通知提出者本人 (杭田 2026-06-04 / R1)
# ---------------------------------------------------------------
def send_application_decided(
    db: Session,
    *,
    application: models.Application,
    student: models.Student,
    result: str,
    decided_role: str,
    comment: str | None,
) -> models.NotificationLog:
    """审批终态（承認 / 却下）结果を提出者本人へメール通知する。

    - 收件人 = 学生本人の email（未登録なら failed 記録、業務は止めない）
    - notification_log に 1 行記録（template_key='application_decided'）
    - dev 下 RESEND_API_KEY 未设置则 pending（skipped）
    """
    subject, body = render_application_decided(
        application=application,
        student=student,
        result=result,
        decided_role=decided_role,
        comment=comment,
    )
    to_email = student.email
    payload = {
        "subject": subject,
        "to": [to_email] if to_email else [],
        "student_id": str(student.id),
        "application_id": str(application.id),
        "result": result,
    }

    log = models.NotificationLog(
        channel="email",
        template_key="application_decided",
        target_type="student",
        target_id=student.id,
        target_email=to_email,
        payload=payload,
        status="pending",
        attempts=0,
    )
    db.add(log)
    db.flush()  # log.id 確定

    if not to_email:
        log.status = "failed"
        log.last_error = "提出者本人に email 登録なし"
        log.attempts = 0
        return log

    sent, status_code, error = _send_via_resend(
        to_emails=[to_email], subject=subject, body_text=body
    )
    log.attempts = 1
    if sent:
        log.status = "sent"
        log.sent_at = datetime.now(timezone.utc)
    else:
        if error and "not configured" in error:
            log.status = "pending"
            log.last_error = "dev mode: Resend API key not configured (skipped)"
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

    sent, status_code, error = _send_via_resend(
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
