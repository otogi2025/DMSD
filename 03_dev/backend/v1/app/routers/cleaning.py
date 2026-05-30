"""清扫安排 endpoint (spec §7.10 清扫审查)。

5-27 凌晨新增 — CleaningPage 接 backend 用。

端点:
- GET  /api/v1/cleaning?date=YYYY-MM-DD  — 列指定日期的所有清扫安排
- POST /api/v1/cleaning                    — 老师新建清扫分配
- POST /api/v1/cleaning/{id}/inspect       — 老师审核（passed / failed 不通过自动加扣分）

待 itsuki review:
- 是否要让学生自己上报 done_at（POST /done 端点）/ 当前只老师 inspect
- 不通过自动加 DemeritEvent points 默认 2.5 是否合理
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import dorm_units_for_teacher, get_current_teacher


def _assert_student_in_dorm(teacher: models.Teacher, student: models.Student) -> None:
    """R4 寮边界写操作校验 — 学生 dorm_unit 不在老师管辖范围 → 403。"""
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生への操作はできません",
            },
        )


router = APIRouter(prefix="/api/v1/cleaning", tags=["cleaning"])

# 清扫审查 / 分配权限 — 寮監 / 寮務 / 管理係
_ADMIN_ROLES = {"寮監", "寮務部長", "寮務課長", "管理係"}

# 不通过自动加的 DemeritEvent points 默认值
CLEANING_FAILED_POINTS = 2.5


@router.get("", response_model=list[schemas.CleaningAssignmentOut])
def list_cleaning(
    scheduled_date: date,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """列指定日期所有清扫安排 — R4 寮过滤。"""
    stmt = (
        select(models.CleaningAssignment)
        .where(models.CleaningAssignment.scheduled_date == scheduled_date)
        .order_by(models.CleaningAssignment.area)
    )
    rows = db.scalars(stmt).all()
    # R4 寮过滤（男寮 1→[1,2] / 女寮 4→[4] / 跨寮 → None 看全部）
    dorm_units = dorm_units_for_teacher(teacher)
    if dorm_units is not None:
        student_ids = {
            s.id
            for s in db.scalars(
                select(models.Student).where(models.Student.dorm_unit.in_(dorm_units))
            ).all()
        }
        rows = [r for r in rows if r.student_id in student_ids]
    return [schemas.CleaningAssignmentOut.model_validate(r) for r in rows]


@router.post("", response_model=schemas.CleaningAssignmentOut, status_code=201)
def create_cleaning(
    body: schemas.CleaningAssignmentCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师新建清扫分配。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "清扫分配需要寮監 / 寮務 / 管理係 权限",
            },
        )
    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
        )
    # R4 寮边界：寮監等寮 scoped 角色不能给管辖外寮学生派清扫
    _assert_student_in_dorm(teacher, student)
    row = models.CleaningAssignment(
        student_id=body.student_id,
        area=body.area,
        scheduled_date=body.scheduled_date,
        status="assigned",
        assigned_by_teacher_id=teacher.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.CleaningAssignmentOut.model_validate(row)


@router.post("/{cleaning_id}/inspect", response_model=schemas.CleaningAssignmentOut)
def inspect_cleaning(
    cleaning_id: UUID,
    body: schemas.CleaningInspectIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师审核 — passed 通过 / failed 不通过（自动加扣分）。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "清扫审核需要寮監 / 寮務 / 管理係 权限",
            },
        )
    row = db.get(models.CleaningAssignment, cleaning_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLEANING_NOT_FOUND", "message": "清扫安排不存在"},
        )
    # R4 寮边界：审核前确认学生属本老师管辖寮
    student = db.get(models.Student, row.student_id)
    if student:
        _assert_student_in_dorm(teacher, student)
    if row.status in {"passed", "failed", "skipped"}:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "ALREADY_INSPECTED",
                "message": "该安排已审核或跳过",
            },
        )

    now = datetime.now(timezone.utc)
    row.status = body.result
    row.inspected_by_teacher_id = teacher.id
    row.inspected_at = now

    if body.result == "failed":
        if not body.failure_reason:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "MISSING_REASON",
                    "message": "不通过必须填 failure_reason",
                },
            )
        row.failure_reason = body.failure_reason
        # 自动加 DemeritEvent
        demerit = models.DemeritEvent(
            student_id=row.student_id,
            source_type="cleaning_failed",
            source_event_id=row.id,
            points=CLEANING_FAILED_POINTS,
            reason=f"清扫不通过（{row.area}）：{body.failure_reason}",
            month=now.strftime("%Y-%m"),
            created_by_teacher_id=teacher.id,
        )
        db.add(demerit)
        db.flush()  # 拿到 demerit.id
        row.demerit_event_id = demerit.id

    db.commit()
    db.refresh(row)
    return schemas.CleaningAssignmentOut.model_validate(row)
