"""遗失物社区投稿 endpoint — 无 spec，CC 最小设计（学生投稿 + 列表 + 投稿者标记解决）。

跟 front_desk 的官方失物招领区别：那是老师前台登记的，这是学生之间「捡到 / 丢了」的社区互助。
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
from ..deps import get_current_principal, get_current_student

router = APIRouter(prefix="/api/v1/lost-found", tags=["lost-found"])


@router.post("", response_model=schemas.LostFoundOut, status_code=201)
def create_lost_found(
    body: schemas.LostFoundCreateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生发遗失物投稿（捡到 found / 丢了 lost）。"""
    row = models.LostFoundPost(
        student_id=student.id,
        post_type=body.post_type,
        item_name=body.item_name,
        description=body.description,
        location=body.location,
        status="open",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.LostFoundOut.model_validate(row)


@router.get("", response_model=list[schemas.LostFoundOut])
def list_lost_found(
    status: Optional[str] = Query(None, description="open / resolved；不传=全部"),
    db: Session = Depends(get_db),
    principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """遗失物一览（新→旧）。学生 + 老师都能看。"""
    # status 取值校验（照 bus_routes 做法）：传了非法状态直接 400，不静默返回空列表。
    if status is not None and status not in ("open", "resolved"):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STATUS",
                "message": "status 必须是 open / resolved",
            },
        )
    # 演示隔离：principal（学生 / 老师都有 is_demo）只看与自己同侧学生的投稿（双向防泄漏）
    stmt = (
        select(models.LostFoundPost)
        .join(models.Student, models.LostFoundPost.student_id == models.Student.id)
        .where(models.Student.is_demo == principal.is_demo)
        .order_by(models.LostFoundPost.created_at.desc())
    )
    if status is not None:
        stmt = stmt.where(models.LostFoundPost.status == status)
    rows = db.scalars(stmt).all()
    return [schemas.LostFoundOut.model_validate(r) for r in rows]


@router.patch("/{post_id}/resolve", response_model=schemas.LostFoundOut)
def resolve_lost_found(
    post_id: UUID,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """投稿者本人标记自己的投稿为已解决（已认领 / 已找回）。"""
    row = db.get(models.LostFoundPost, post_id)
    if not row:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "投稿が見つかりません"}
        )
    if row.student_id != student.id:
        raise HTTPException(
            403, {"code": "FORBIDDEN", "message": "他人の投稿は変更できません"}
        )
    if row.status == "resolved":
        raise HTTPException(
            409, {"code": "ALREADY_RESOLVED", "message": "既に解決済みです"}
        )
    row.status = "resolved"
    row.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.LostFoundOut.model_validate(row)
