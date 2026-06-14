"""杂项申请 endpoint — 修繕 / 来訪者 / 代理受取（无 spec，CC 最小设计）。

学生提交 → 老师确认 / 学生撤回。比出寮届（多级审查）+ 外出（单老师确认）更轻。
kind 区分三类：repair 修繕 / guest 来訪者 / proxy_receipt 代理受取。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    require_permission,
)

router = APIRouter(prefix="/api/v1/misc-requests", tags=["misc-requests"])


@router.post("", response_model=schemas.MiscRequestOut, status_code=201)
def create_misc_request(
    body: schemas.MiscRequestCreateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生提交杂项申请（修繕 / 来訪者 / 代理受取）。"""
    row = models.MiscRequest(
        student_id=student.id,
        kind=body.kind,
        subject=body.subject,
        detail=body.detail,
        target_date=body.target_date,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.MiscRequestOut.model_validate(row)


@router.get("/mine", response_model=list[schemas.MiscRequestOut])
def list_my_misc_requests(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生查自己的杂项申请（新→旧）。"""
    rows = db.scalars(
        select(models.MiscRequest)
        .where(models.MiscRequest.student_id == student.id)
        .order_by(models.MiscRequest.created_at.desc())
    ).all()
    return [schemas.MiscRequestOut.model_validate(r) for r in rows]


@router.get("", response_model=list[schemas.MiscRequestOut])
def list_misc_requests(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    """老师查杂项申请列表 — R4 寮过滤（男寮[1,2]/女寮[4]/跨寮看全部）。"""
    rows = db.scalars(
        select(models.MiscRequest).order_by(models.MiscRequest.created_at.desc())
    ).all()
    # R4 寮过滤 + 演示隔离：真老师看真实学生申请 / 演示老师看演示学生申请
    # （跨寮老师 dorm_units=None 原先完全不过滤，演示数据会漏进真老师 — 改成总按 demo 过滤）
    dorm_units = dorm_units_for_teacher(teacher)
    student_q = select(models.Student.id).where(demo_scope_for_teacher(teacher))
    if dorm_units is not None:
        student_q = student_q.where(models.Student.dorm_unit.in_(dorm_units))
    allowed_ids = set(db.scalars(student_q).all())
    rows = [r for r in rows if r.student_id in allowed_ids]
    return [schemas.MiscRequestOut.model_validate(r) for r in rows]


@router.patch("/{request_id}/confirm", response_model=schemas.MiscRequestOut)
def confirm_misc_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    """老师确认杂项申请 — R4 寮边界，非「确认待ち」状态返 409。"""
    row = db.get(models.MiscRequest, request_id)
    if not row:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    student = db.get(models.Student, row.student_id)
    if student:
        # 演示账号写隔离：演示老师只能确认演示学生申请、真老师只能确认真实学生申请（不匹配 raise 404）
        assert_student_demo_match(teacher, student)
        allowed = dorm_units_for_teacher(teacher)
        if allowed is not None and student.dorm_unit not in allowed:
            raise HTTPException(
                403,
                {
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の学生への操作はできません",
                },
            )
    if row.status != "pending":
        raise HTTPException(
            409, {"code": "NOT_PENDING", "message": "確認待ち以外は確認できません"}
        )
    row.status = "confirmed"
    row.confirmed_by_teacher_id = teacher.id
    row.confirmed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.MiscRequestOut.model_validate(row)


@router.patch("/{request_id}/withdraw", response_model=schemas.MiscRequestOut)
def withdraw_misc_request(
    request_id: UUID,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生撤回自己的杂项申请（仅「确认待ち」可撤）。"""
    row = db.get(models.MiscRequest, request_id)
    if not row:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    if row.student_id != student.id:
        raise HTTPException(
            403, {"code": "FORBIDDEN", "message": "他人の申請は取り消せません"}
        )
    if row.status != "pending":
        raise HTTPException(
            409, {"code": "NOT_PENDING", "message": "確認待ち以外は取り消せません"}
        )
    row.status = "withdrawn"
    row.withdrawn_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.MiscRequestOut.model_validate(row)
