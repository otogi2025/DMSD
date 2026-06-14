"""通知 (admin / dev) endpoint。

POST /api/v1/notifications/test  — SendGrid 送達 smoke テスト (#6 完成定義)
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import assert_not_demo_teacher, get_current_teacher, require_permission
from ..services import email as email_svc

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("/test", response_model=schemas.NotificationTestOut)
def send_test(
    body: schemas.NotificationTestIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
):
    # 演示老师禁用真实发邮件通道（防滥发 / 钓鱼 / 耗 SendGrid 配额 / 损发信域名信誉）→ 403
    assert_not_demo_teacher(teacher)

    log, status_code, error = email_svc.send_test_email(
        db,
        to=body.to,
        subject=body.subject,
        body_text=body.body_text,
        actor_id=teacher.id,
    )
    db.commit()

    return schemas.NotificationTestOut(
        sent=(log.status == "sent"),
        notification_log_id=log.id,
        sendgrid_status_code=status_code,
        error=error,
    )


# ---------------------------------------------------------------
# 老师通知中心（UI「通知センター」）— 阶段1（itsuki 2026-06-13）
#
# 填充策略：不在各事件产生点写钩子，而是取 feed 时扫现有事件表
# （申请提交 / 扣分 / 点呼上报）幂等同步成通知行（按 source_table+source_id 去重）。
# 好处：只改 models/schemas/本文件 + 迁移，不碰 applications/discipline/rollcall 路由
# （降低与其它会话改后端文件的冲突面）。代价：通知在取 feed 时生成，非事件即时。
# ---------------------------------------------------------------

# 每张事件表每次同步最多扫的行数（小规模宿舍足够；防大表全扫）
_SYNC_SCAN_LIMIT = 200

# 点呼上报 kind → 日语标题
_ROLLCALL_KIND_LABEL = {
    "health": "体調報告",
    "absence": "欠席の申請",
    "other": "その他の問題",
}


def _fmt_points(points: float) -> str:
    """0.5 → "0.5" / 1.0 → "1"（整数去小数点）。"""
    return str(int(points)) if points == int(points) else str(points)


def _sync_notifications(db: Session, *, is_demo: bool) -> None:
    """把现有事件幂等同步成通知行（只处理与 realm[is_demo] 匹配的事件）。

    按 (source_table, source_id) 去重，只插缺失的。source_id 是 UUID 全局唯一，
    故用全量已存在键集合去重，绝不会撞 uq_notif_source 唯一约束。
    """
    existing = {
        (st, sid)
        for st, sid in db.query(
            models.Notification.source_table, models.Notification.source_id
        ).all()
    }
    new_rows: list[models.Notification] = []

    # ① 申请提交
    apps = (
        db.query(models.Application, models.Student)
        .join(models.Student, models.Application.student_id == models.Student.id)
        .filter(models.Student.is_demo == is_demo)
        .order_by(models.Application.submitted_at.desc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for app, stu in apps:
        if ("applications", app.id) in existing:
            continue
        new_rows.append(
            models.Notification(
                category="application",
                source_table="applications",
                source_id=app.id,
                title=f"出寮届の申請（{app.kind}）",
                body=f"{stu.name} さんが{app.kind}を申請しました",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=app.submitted_at,
            )
        )

    # ② 扣分（未撤销）
    demerits = (
        db.query(models.DemeritEvent, models.Student)
        .join(models.Student, models.DemeritEvent.student_id == models.Student.id)
        .filter(
            models.Student.is_demo == is_demo,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .order_by(models.DemeritEvent.created_at.desc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for ev, stu in demerits:
        if ("demerit_event", ev.id) in existing:
            continue
        new_rows.append(
            models.Notification(
                category="demerit",
                source_table="demerit_event",
                source_id=ev.id,
                title=f"減点（{_fmt_points(ev.points)}点）",
                body=f"{stu.name} さん：{ev.reason}",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=ev.created_at,
            )
        )

    # ③ 点呼上报
    reports = (
        db.query(models.RollCallReport, models.Student)
        .join(models.Student, models.RollCallReport.student_id == models.Student.id)
        .filter(models.Student.is_demo == is_demo)
        .order_by(models.RollCallReport.created_at.desc())
        .limit(_SYNC_SCAN_LIMIT)
        .all()
    )
    for rep, stu in reports:
        if ("rollcall_reports", rep.id) in existing:
            continue
        label = _ROLLCALL_KIND_LABEL.get(rep.kind, "点呼の報告")
        new_rows.append(
            models.Notification(
                category="rollcall_report",
                source_table="rollcall_reports",
                source_id=rep.id,
                title=f"点呼報告：{label}",
                body=f"{stu.name} さん：{rep.body}",
                related_student_id=stu.id,
                is_demo=is_demo,
                event_at=rep.created_at,
            )
        )

    if new_rows:
        db.add_all(new_rows)
        db.flush()


def _unread_count(db: Session, teacher: models.Teacher) -> int:
    """当前老师在自己 realm 内的未读通知数 = realm 总通知数 − 本人已读数。"""
    total = (
        db.query(models.Notification)
        .filter(models.Notification.is_demo == teacher.is_demo)
        .count()
    )
    read = (
        db.query(models.NotificationRead)
        .join(
            models.Notification,
            models.NotificationRead.notification_id == models.Notification.id,
        )
        .filter(
            models.Notification.is_demo == teacher.is_demo,
            models.NotificationRead.teacher_id == teacher.id,
        )
        .count()
    )
    return max(0, total - read)


@router.get("/feed", response_model=schemas.NotificationFeedOut)
def get_feed(
    limit: int = 50,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """通知中心「最近の通知」流 + 未读数。任意已登录老师可看自己 realm 的通知。"""
    _sync_notifications(db, is_demo=teacher.is_demo)
    db.commit()

    read_ids = {
        nid
        for (nid,) in db.query(models.NotificationRead.notification_id)
        .filter(models.NotificationRead.teacher_id == teacher.id)
        .all()
    }
    rows = (
        db.query(models.Notification)
        .filter(models.Notification.is_demo == teacher.is_demo)
        .order_by(models.Notification.event_at.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    items = [
        schemas.NotificationItem(
            id=n.id,
            category=n.category,
            title=n.title,
            body=n.body,
            related_student_id=n.related_student_id,
            event_at=n.event_at,
            is_read=(n.id in read_ids),
        )
        for n in rows
    ]
    return schemas.NotificationFeedOut(
        items=items, unread_count=_unread_count(db, teacher)
    )


@router.get("/unread-count", response_model=schemas.NotificationUnreadCountOut)
def get_unread_count(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """侧栏「通知」徽章用 — 当前老师未读数（顺带同步新事件）。"""
    _sync_notifications(db, is_demo=teacher.is_demo)
    db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))


@router.post(
    "/{notification_id}/read", response_model=schemas.NotificationUnreadCountOut
)
def mark_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """标记单条通知为已读（幂等）。返回更新后的未读数。"""
    notif = db.get(models.Notification, notification_id)
    if notif is None or notif.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "通知が見つかりません"},
        )
    already = (
        db.query(models.NotificationRead)
        .filter(
            models.NotificationRead.notification_id == notification_id,
            models.NotificationRead.teacher_id == teacher.id,
        )
        .first()
    )
    if already is None:
        db.add(
            models.NotificationRead(
                notification_id=notification_id, teacher_id=teacher.id
            )
        )
        db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))


@router.post("/read-all", response_model=schemas.NotificationUnreadCountOut)
def mark_all_read(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """把当前老师 realm 内所有通知标记为已读。返回未读数（= 0）。"""
    _sync_notifications(db, is_demo=teacher.is_demo)
    db.commit()
    read_ids = {
        nid
        for (nid,) in db.query(models.NotificationRead.notification_id)
        .filter(models.NotificationRead.teacher_id == teacher.id)
        .all()
    }
    all_ids = [
        nid
        for (nid,) in db.query(models.Notification.id)
        .filter(models.Notification.is_demo == teacher.is_demo)
        .all()
    ]
    for nid in all_ids:
        if nid not in read_ids:
            db.add(models.NotificationRead(notification_id=nid, teacher_id=teacher.id))
    db.commit()
    return schemas.NotificationUnreadCountOut(unread_count=_unread_count(db, teacher))
