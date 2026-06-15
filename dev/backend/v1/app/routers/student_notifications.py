"""学生通知中心 feed（§7.13.1 投稿通知开关）。

老师投稿 公告 / 巴士 / 行事 时勾选「学生に通知する」(notify_students=True) 的内容，
按当前学生的可见范围聚合成一个统一通知列表返回。可见范围规则 = services/student_audience。

已读：
- 公告 → 复用 announcement_reads（与公告详情已读同源，两处一致）。
- 巴士 / 行事 → student_notification_reads（本功能新表）。
未读数 = 三类未读合计，驱动 app 铃铛 badge。

⚠️ 巴士 / 行事 表无 is_demo → feed 只取真实学生范围（演示学生看不到巴士/行事通知，
   公告则按 is_demo 隔离）。彻底隔离记 TODO。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student
from ..services import student_audience

router = APIRouter(
    prefix="/api/v1/student/notifications", tags=["student-notifications"]
)

# feed 里正文摘要最大字符数
_SUMMARY_LEN = 80


def _summarize(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= _SUMMARY_LEN else text[:_SUMMARY_LEN] + "…"


@router.get("", response_model=schemas.StudentNotificationFeedOut)
def get_student_notification_feed(
    limit: int = 50,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """当前学生的通知 feed — 聚合老师勾了「通知」的 公告 / 巴士 / 行事（时系列 desc）。"""
    items: list[schemas.StudentNotificationItem] = []

    # ① 公告（notify_students=True + scope 可见 + 未删 + demo 隔离）
    ann_scopes = student_audience.announcement_scopes_for_student(student)
    anns = db.scalars(
        select(models.Announcement)
        .where(
            models.Announcement.notify_students.is_(True),
            models.Announcement.deleted_at.is_(None),
            models.Announcement.is_demo == student.is_demo,
            models.Announcement.scope.in_(ann_scopes),
        )
        .order_by(models.Announcement.created_at.desc())
        .limit(limit)
    ).all()
    ann_read_ids = set(
        db.scalars(
            select(models.AnnouncementRead.announcement_id).where(
                models.AnnouncementRead.student_id == student.id
            )
        ).all()
    )
    for a in anns:
        items.append(
            schemas.StudentNotificationItem(
                kind="announcement",
                ref_id=a.id,
                title=a.title,
                body=_summarize(a.body),
                created_at=a.created_at,
                is_read=a.id in ann_read_ids,
            )
        )

    # ② 巴士（notify_students=True + visible_to 可见 + 未停用）
    bus_vis = student_audience.bus_visible_to_for_student(student)
    buses = db.scalars(
        select(models.BusRoute)
        .join(
            models.Teacher,
            models.BusRoute.created_by_teacher_id == models.Teacher.id,
        )
        .where(
            models.BusRoute.notify_students.is_(True),
            models.BusRoute.deprecated.is_(False),
            models.BusRoute.visible_to.in_(bus_vis),
            # demo 隔离：巴士无自身 is_demo 列 → 按创建老师 is_demo 隔离（codex 复审 2026-06-16）
            models.Teacher.is_demo == student.is_demo,
        )
        .order_by(models.BusRoute.created_at.desc())
        .limit(limit)
    ).all()

    # ③ 行事（notify_students=True，全员可见）
    events = db.scalars(
        select(models.DormEvent)
        .join(
            models.Teacher,
            models.DormEvent.created_by_teacher_id == models.Teacher.id,
        )
        .where(
            models.DormEvent.notify_students.is_(True),
            # demo 隔离：行事无自身 is_demo 列 → 按创建老师 is_demo 隔离（codex 复审 2026-06-16）
            models.Teacher.is_demo == student.is_demo,
        )
        .order_by(models.DormEvent.created_at.desc())
        .limit(limit)
    ).all()

    # 巴士 + 行事 已读 —— student_notification_reads（一次查全）
    read_set = {
        (r.kind, r.ref_id)
        for r in db.scalars(
            select(models.StudentNotificationRead).where(
                models.StudentNotificationRead.student_id == student.id
            )
        ).all()
    }
    for b in buses:
        items.append(
            schemas.StudentNotificationItem(
                kind="bus",
                ref_id=b.id,
                title=b.name,
                body=_summarize(b.direction),
                created_at=b.created_at,
                is_read=("bus", b.id) in read_set,
            )
        )
    for e in events:
        items.append(
            schemas.StudentNotificationItem(
                kind="event",
                ref_id=e.id,
                title=e.title,
                body=_summarize(e.description or e.category),
                created_at=e.created_at,
                is_read=("event", e.id) in read_set,
            )
        )

    items.sort(key=lambda x: x.created_at, reverse=True)
    # unread_count 用切片前的全量算（badge 真值）—— 不能从 items[:limit] 推导，
    # 否则未读条数超过一页(limit)时 badge 会低估（codex 复审 2026-06-16）。
    unread_count = sum(1 for i in items if not i.is_read)
    items = items[:limit]
    return schemas.StudentNotificationFeedOut(items=items, unread_count=unread_count)


@router.post("/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_student_notification_read(
    body: schemas.StudentNotificationReadIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """标记一条学生通知已读（幂等 — 已读再标不报错）。

    公告复用 announcement_reads（与公告详情已读同源）；巴士 / 行事 用 student_notification_reads。
    """
    if body.kind == "announcement":
        exists = db.get(
            models.AnnouncementRead,
            {"announcement_id": body.ref_id, "student_id": student.id},
        )
        if exists is None:
            db.add(
                models.AnnouncementRead(
                    announcement_id=body.ref_id, student_id=student.id
                )
            )
            try:
                db.commit()
            except IntegrityError:
                # 并发：另一请求已插同一已读行 → 复合主键冲突，回滚即可（幂等，仍返 204）。
                db.rollback()
    else:  # bus / event（schema Literal 已限定取值）
        exists = db.get(
            models.StudentNotificationRead,
            {"student_id": student.id, "kind": body.kind, "ref_id": body.ref_id},
        )
        if exists is None:
            db.add(
                models.StudentNotificationRead(
                    student_id=student.id, kind=body.kind, ref_id=body.ref_id
                )
            )
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
