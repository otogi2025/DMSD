"""学生通知中心 feed（§7.13.1 投稿通知开关）。

老师投稿 公告 / 巴士 / 行事 时勾选「学生に通知する」(notify_students=True) 的内容，
按当前学生的可见范围聚合成一个统一通知列表返回。可见范围规则 = services/student_audience。

已读：
- 公告 → 复用 announcement_reads（与公告详情已读同源，两处一致）。
- 巴士 / 行事 → student_notification_reads（本功能新表）。
未读数 = 三类各自独立 COUNT（不经 limit）再相加，驱动 app 铃铛 badge。
feed items 仍每类 .limit 后合并截断；角标与列表分页解耦（backend#43）。

demo 隔离（2026-06-16 codex 复审修）：巴士 / 行事 表无自身 is_demo 列 → feed 查询 join teachers
按「创建老师 is_demo == 当前学生 is_demo」过滤（公告则按 ann.is_demo）。演示学生只看演示老师内容、
真实学生只看真实老师内容，两侧（feed + 推送）口径一致。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import exists, func, select
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


def _assert_bus_or_event_visible(
    db: Session, student: models.Student, kind: str, ref_id
) -> None:
    """确认巴士 / 行事存在且对该生可见（与 feed 同口径），否则 404。"""
    if kind == "bus":
        bus_vis = student_audience.bus_visible_to_for_student(student)
        visible = db.scalar(
            select(models.BusRoute.id)
            .join(
                models.Teacher,
                models.BusRoute.created_by_teacher_id == models.Teacher.id,
            )
            .where(
                models.BusRoute.id == ref_id,
                models.BusRoute.notify_students.is_(True),
                models.BusRoute.deprecated.is_(False),
                models.BusRoute.visible_to.in_(bus_vis),
                models.Teacher.is_demo == student.is_demo,
            )
        )
    else:  # event
        visible = db.scalar(
            select(models.DormEvent.id)
            .join(
                models.Teacher,
                models.DormEvent.created_by_teacher_id == models.Teacher.id,
            )
            .where(
                models.DormEvent.id == ref_id,
                models.DormEvent.notify_students.is_(True),
                models.Teacher.is_demo == student.is_demo,
            )
        )
    if visible is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "通知が見つかりません"},
        )


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
    items = items[:limit]

    # unread_count：三类独立 COUNT（不 limit），条件与上面 is_read 判定一致
    # 公告未读 = 可见通知公告 且 announcement_reads 无本学生行
    ann_unread = (
        db.scalar(
            select(func.count())
            .select_from(models.Announcement)
            .where(
                models.Announcement.notify_students.is_(True),
                models.Announcement.deleted_at.is_(None),
                models.Announcement.is_demo == student.is_demo,
                models.Announcement.scope.in_(ann_scopes),
                ~exists(
                    select(models.AnnouncementRead.announcement_id).where(
                        models.AnnouncementRead.announcement_id
                        == models.Announcement.id,
                        models.AnnouncementRead.student_id == student.id,
                    )
                ),
            )
        )
        or 0
    )
    # 巴士未读 = 可见通知巴士 且 student_notification_reads 无 (bus, id)
    bus_unread = (
        db.scalar(
            select(func.count())
            .select_from(models.BusRoute)
            .join(
                models.Teacher,
                models.BusRoute.created_by_teacher_id == models.Teacher.id,
            )
            .where(
                models.BusRoute.notify_students.is_(True),
                models.BusRoute.deprecated.is_(False),
                models.BusRoute.visible_to.in_(bus_vis),
                models.Teacher.is_demo == student.is_demo,
                ~exists(
                    select(models.StudentNotificationRead.ref_id).where(
                        models.StudentNotificationRead.student_id == student.id,
                        models.StudentNotificationRead.kind == "bus",
                        models.StudentNotificationRead.ref_id == models.BusRoute.id,
                    )
                ),
            )
        )
        or 0
    )
    # 行事未读 = 通知行事 且 student_notification_reads 无 (event, id)
    event_unread = (
        db.scalar(
            select(func.count())
            .select_from(models.DormEvent)
            .join(
                models.Teacher,
                models.DormEvent.created_by_teacher_id == models.Teacher.id,
            )
            .where(
                models.DormEvent.notify_students.is_(True),
                models.Teacher.is_demo == student.is_demo,
                ~exists(
                    select(models.StudentNotificationRead.ref_id).where(
                        models.StudentNotificationRead.student_id == student.id,
                        models.StudentNotificationRead.kind == "event",
                        models.StudentNotificationRead.ref_id == models.DormEvent.id,
                    )
                ),
            )
        )
        or 0
    )
    unread_count = ann_unread + bus_unread + event_unread
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
        exists_row = db.get(
            models.StudentNotificationRead,
            {"student_id": student.id, "kind": body.kind, "ref_id": body.ref_id},
        )
        if exists_row is None:
            # 插入前确认资源存在且对该生可见（防任意 UUID 幂等写成已读）
            _assert_bus_or_event_visible(db, student, body.kind, body.ref_id)
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
