"""行事予定 endpoint (spec §7.5)。

端点:
- GET  /api/v1/events?from_date=&to_date=  — 列日期范围内行事（老师+学生都可看）
- POST /api/v1/events                       — 役职老师新建
- PATCH /api/v1/events/{id}                 — 役职老师编辑
- DELETE /api/v1/events/{id}                — 役职老师删除

权限: GET 全老师可看 / 增删改限役职（寮務部長 / 寮務課長 / 管理係）
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import (
    assert_not_demo_teacher,
    get_current_principal,
    get_current_teacher,
)

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# 增删改权限 — 役职老师
_EDIT_ROLES = {"寮務部長", "寮務課長", "管理係"}

# 合法 category 值
_VALID_CATEGORIES = {"学校行事", "寮行事", "外部", "その他"}


def _require_edit_role(teacher: models.Teacher) -> None:
    # 演示老师禁增删改全局行事（行事无 is_demo，会污染真实学生看到的日程）→ 403
    assert_not_demo_teacher(teacher)
    if teacher.role not in _EDIT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "行事予定の増删改には 寮務部長 / 寮務課長 / 管理係 権限が必要です",
            },
        )


@router.get("", response_model=schemas.DormEventListOut)
def list_events(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """列行事予定 — 按日期范围过滤（from_date / to_date 均可选）。学生+老师均可看。"""
    stmt = select(models.DormEvent).order_by(models.DormEvent.event_date)
    if from_date:
        stmt = stmt.where(models.DormEvent.event_date >= from_date)
    if to_date:
        stmt = stmt.where(models.DormEvent.event_date <= to_date)
    rows = db.scalars(stmt).all()
    return schemas.DormEventListOut(
        items=[schemas.DormEventOut.model_validate(r) for r in rows]
    )


@router.post("", response_model=schemas.DormEventOut, status_code=201)
def create_event(
    body: schemas.DormEventCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师新建行事予定。"""
    _require_edit_role(teacher)
    if body.category not in _VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": f"category 必须是 {_VALID_CATEGORIES} 之一",
            },
        )
    row = models.DormEvent(
        title=body.title,
        category=body.category,
        event_date=body.event_date,
        start_at=body.start_at,
        end_at=body.end_at,
        description=body.description,
        created_by_teacher_id=teacher.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.DormEventOut.model_validate(row)


@router.patch("/{event_id}", response_model=schemas.DormEventOut)
def patch_event(
    event_id: UUID,
    body: schemas.DormEventPatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师编辑行事予定（部分更新）。"""
    _require_edit_role(teacher)
    row = db.get(models.DormEvent, event_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "EVENT_NOT_FOUND", "message": "行事予定が見つかりません"},
        )
    if body.category is not None and body.category not in _VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": f"category 必须是 {_VALID_CATEGORIES} 之一",
            },
        )
    for field in (
        "title",
        "category",
        "event_date",
        "start_at",
        "end_at",
        "description",
    ):
        val = getattr(body, field)
        if val is not None:
            setattr(row, field, val)
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.DormEventOut.model_validate(row)


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师删除行事予定（物理删除）。"""
    _require_edit_role(teacher)
    row = db.get(models.DormEvent, event_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "EVENT_NOT_FOUND", "message": "行事予定が見つかりません"},
        )
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="event.delete",
            target_type="dorm_events",
            target_id=event_id,
            payload={"title": row.title, "event_date": str(row.event_date)},
        )
    )
    db.delete(row)
    db.commit()
