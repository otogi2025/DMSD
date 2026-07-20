"""投稿通報 endpoint — App Store 审核指南 1.2 UGC 治理（itsuki 2026-07-20 拍板 A 方案）。

学生对互见投稿（点歌 song / 公告回复 announcement_reply / 遗失物 lost_found）按「通報」，
老师在通報一覧确认后：删投稿（songs / lost-found 的 DELETE 接口）或直接标处理完。
跟 6-13 拍板删除的旧「通报+累计封禁」体系无关 — 本版不含封禁，只有通報 + 老师处理。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student, get_current_teacher

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


def _load_target(db: Session, content_type: str, content_id: UUID, is_demo: bool):
    """取被通報的投稿行；不存在 / 已删 / 与通報人不同演示侧 返回 None。

    演示写隔离（对齐 deps.assert_student_demo_match 的威胁模型）：
    演示学生只能通報演示侧投稿、真实学生只能通報真实侧 — 跨侧当作不存在，
    防跨侧通報把对面内容摘要带进错误侧老师的通報一覧（信息泄漏 + 连锁误删）。
    """
    if content_type == "song":
        row = db.get(models.SongRequest, content_id)
        if not row or row.deleted_at is not None:
            return None
        author = db.get(models.Student, row.student_id)
        return row if author and author.is_demo == is_demo else None
    if content_type == "announcement_reply":
        row = db.get(models.AnnouncementReply, content_id)
        if not row or row.deleted_at is not None:
            return None
        # 回复的侧别跟着父公告走（照 announcements.py 删回复的既有隔离写法）
        parent = db.get(models.Announcement, row.announcement_id)
        return row if parent and parent.is_demo == is_demo else None
    row = db.get(models.LostFoundPost, content_id)
    if not row or row.deleted_at is not None:
        return None
    author = db.get(models.Student, row.student_id)
    return row if author and author.is_demo == is_demo else None


def _preview(db: Session, content_type: str, content_id: UUID) -> Optional[str]:
    """老师一覧用的内容摘要（前 80 字）。投稿已被删/不存在返回 None（软删后一覧显「已删除」占位）。"""
    if content_type == "song":
        row = db.get(models.SongRequest, content_id)
        return row.song_title[:80] if row and row.deleted_at is None else None
    if content_type == "announcement_reply":
        row = db.get(models.AnnouncementReply, content_id)
        return row.body[:80] if row and row.deleted_at is None else None
    row = db.get(models.LostFoundPost, content_id)
    return row.item_name[:80] if row and row.deleted_at is None else None


def _parent_id(db: Session, content_type: str, content_id: UUID) -> Optional[UUID]:
    """公告回复的父公告 id（删回复接口路径要两段）；其他类型 None。

    ⚠️ 本函数与 _preview 自身不做演示侧过滤 — 安全性完全依赖调用方已保证
    「通報属于同侧」（POST 经 _load_target 挡跨侧创建 / GET·PATCH 按 reporter 侧过滤）。
    若未来改动削弱了 POST 的跨侧闸，这两个函数会跟着泄漏对面内容，须同步加闸。
    """
    if content_type != "announcement_reply":
        return None
    row = db.get(models.AnnouncementReply, content_id)
    return row.announcement_id if row else None


@router.post("", response_model=schemas.ContentReportOut, status_code=201)
def create_report(
    body: schemas.ContentReportCreateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生通報一条投稿。目标不存在 / 已被删 / 跨演示侧 → 404。"""
    if _load_target(db, body.content_type, body.content_id, student.is_demo) is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "対象の投稿が見つかりません"}
        )
    # 同一学生对同一投稿重复通報 → 幂等返回已有记录（不堆重复行刷屏老师一覧）
    existing = db.scalars(
        select(models.ContentReport).where(
            models.ContentReport.content_type == body.content_type,
            models.ContentReport.content_id == body.content_id,
            models.ContentReport.reporter_student_id == student.id,
        )
    ).first()
    if existing:
        return schemas.ContentReportOut.model_validate(existing)
    row = models.ContentReport(
        content_type=body.content_type,
        content_id=body.content_id,
        reporter_student_id=student.id,
        reason=body.reason,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # 并发双击撞上唯一约束 uq_creport_target_reporter → 回滚后返回既有记录（幂等语义不变）
        db.rollback()
        existing = db.scalars(
            select(models.ContentReport).where(
                models.ContentReport.content_type == body.content_type,
                models.ContentReport.content_id == body.content_id,
                models.ContentReport.reporter_student_id == student.id,
            )
        ).first()
        if existing:
            return schemas.ContentReportOut.model_validate(existing)
        raise
    db.refresh(row)
    return schemas.ContentReportOut.model_validate(row)


@router.get("", response_model=list[schemas.ContentReportOut])
def list_reports(
    status: Optional[str] = Query(None, description="open / handled；不传=全部"),
    teacher: models.Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """老师看通報一覧（新→旧）。演示隔离：只看与自己同侧（is_demo）学生发的通報。"""
    if status is not None and status not in ("open", "handled"):
        raise HTTPException(
            400,
            {"code": "INVALID_STATUS", "message": "status 必须是 open / handled"},
        )
    stmt = (
        select(models.ContentReport)
        .join(
            models.Student,
            models.ContentReport.reporter_student_id == models.Student.id,
        )
        .where(models.Student.is_demo == teacher.is_demo)
        .order_by(models.ContentReport.created_at.desc())
    )
    if status is not None:
        stmt = stmt.where(models.ContentReport.status == status)
    rows = db.scalars(stmt).all()
    out = []
    for r in rows:
        item = schemas.ContentReportOut.model_validate(r)
        item.content_preview = _preview(db, r.content_type, r.content_id)
        item.content_parent_id = _parent_id(db, r.content_type, r.content_id)
        out.append(item)
    return out


@router.patch("/{report_id}", response_model=schemas.ContentReportOut)
def handle_report(
    report_id: UUID,
    teacher: models.Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """老师标记通報处理完（删了投稿、或判定无问题都算处理完）。"""
    row = db.get(models.ContentReport, report_id)
    if not row:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "通報が見つかりません"}
        )
    # 演示写隔离：通報跟着通報人的侧别走，跨侧当作不存在 404（防拿到 UUID 就能标对面通報）
    reporter = db.get(models.Student, row.reporter_student_id)
    if reporter is None or reporter.is_demo != teacher.is_demo:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "通報が見つかりません"}
        )
    if row.status == "handled":
        raise HTTPException(
            409, {"code": "ALREADY_HANDLED", "message": "既に対応済みです"}
        )
    row.status = "handled"
    row.handled_at = datetime.now(timezone.utc)
    row.handled_by_teacher_id = teacher.id
    db.commit()
    db.refresh(row)
    item = schemas.ContentReportOut.model_validate(row)
    item.content_preview = _preview(db, row.content_type, row.content_id)
    item.content_parent_id = _parent_id(db, row.content_type, row.content_id)
    return item
