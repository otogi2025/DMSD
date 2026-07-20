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
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student, get_current_teacher

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


def _load_target(db: Session, content_type: str, content_id: UUID):
    """取被通報的投稿行；不存在或已删返回 None。"""
    if content_type == "song":
        row = db.get(models.SongRequest, content_id)
        return row if row and row.deleted_at is None else None
    if content_type == "announcement_reply":
        row = db.get(models.AnnouncementReply, content_id)
        return row if row and row.deleted_at is None else None
    row = db.get(models.LostFoundPost, content_id)
    return row if row and row.deleted_at is None else None


def _preview(db: Session, content_type: str, content_id: UUID) -> Optional[str]:
    """老师一覧用的内容摘要（前 80 字）。投稿已被删/不存在返回 None。"""
    if content_type == "song":
        row = db.get(models.SongRequest, content_id)
        return row.song_title[:80] if row else None
    if content_type == "announcement_reply":
        row = db.get(models.AnnouncementReply, content_id)
        return row.body[:80] if row else None
    row = db.get(models.LostFoundPost, content_id)
    return row.item_name[:80] if row else None


def _parent_id(db: Session, content_type: str, content_id: UUID) -> Optional[UUID]:
    """公告回复的父公告 id（删回复接口路径要两段）；其他类型 None。"""
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
    """学生通報一条投稿。目标不存在 / 已被删 → 404。"""
    if _load_target(db, body.content_type, body.content_id) is None:
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
    db.commit()
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
