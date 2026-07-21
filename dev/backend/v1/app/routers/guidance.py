"""指導履歴 endpoint (spec §7.9)。

端点:
- POST /api/v1/students/{student_id}/guidance       — 老师录入指导记录
- GET  /api/v1/students/{student_id}/guidance       — 查某学生全部指导记录（老师）

角色 gate:
- 录入 / 查记录: 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教師/管理係）
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    dorm_units_for_teacher,
    require_permission,
)

router = APIRouter(prefix="/api/v1", tags=["guidance"])

# 有权录入指导记录 + 查看的角色
# 指导履历的功能权限（C_GUIDANCE：管理动作 M / 查看动作 V）由各端点的 require_permission 闸判定，
# 不再按职位拦（旧 _GUIDANCE_ROLES 职位集已随权限分级改造移除）。
# 寮守卫：dorm_units_for_teacher 按令牌 selected_dorm 返回可见寮
# （选男→[1,2] / 选女→[4] / 未选或 op·承認组→[1,2,4]）；学生不在可见寮内时触发 FORBIDDEN_DORM。


def _get_student_or_404(student_id: UUID, db: Session) -> models.Student:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    return student


# -----------------------------------------------------------------------
# 指导记录 — 老师录入 / 查看
# -----------------------------------------------------------------------
@router.post(
    "/students/{student_id}/guidance",
    response_model=schemas.GuidanceRecordOut,
    status_code=201,
)
def create_guidance(
    student_id: UUID,
    body: schemas.GuidanceRecordCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_GUIDANCE, permissions.MANAGE)
    ),
):
    """老师录入学生指导记录。"""
    student = _get_student_or_404(student_id, db)
    # 演示写隔离：演示老师只能给演示学生写记录、真老师只能给真实学生写（否则 404 隐藏存在性）
    assert_student_demo_match(teacher, student)

    # 选寮老师：学生不在令牌可见寮内 → FORBIDDEN_DORM；未选寮看全部则放行
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生の指導記録は録入できません",
            },
        )

    row = models.GuidanceRecord(
        student_id=student_id,
        teacher_id=teacher.id,
        content=body.content,
        category=body.category,
        guidance_date=body.guidance_date,
        confidential=body.confidential,
    )
    db.add(row)
    db.flush()  # 让 row.id 生效
    # 写审计日志
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="guidance.create",
            target_type="guidance_records",
            target_id=row.id,
            payload={"student_id": str(student_id), "category": body.category},
        )
    )
    db.commit()
    db.refresh(row)
    return schemas.GuidanceRecordOut.model_validate(row)


@router.get(
    "/students/{student_id}/guidance",
    response_model=schemas.GuidanceRecordListOut,
)
def list_guidance(
    student_id: UUID,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_GUIDANCE, permissions.VIEW)
    ),
):
    """老师查某学生全部指导记录（未软删的）。limit 默认 50，最大 200。"""
    student = _get_student_or_404(student_id, db)

    # 演示隔离：老师传任意 student_id 拉指导履历 → 演示老师不能拉真实学生（反之亦然），
    # 否则跨寮演示老师能读到真实学生的指导记录 = 泄漏。当作 404 隐藏存在性。
    if student.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )

    # 选寮老师：学生不在令牌可见寮内 → FORBIDDEN_DORM；未选寮看全部则放行
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生の指導履歴は閲覧できません",
            },
        )

    rows = db.scalars(
        select(models.GuidanceRecord)
        .where(
            models.GuidanceRecord.student_id == student_id,
            models.GuidanceRecord.deleted_at.is_(None),
        )
        .order_by(models.GuidanceRecord.guidance_date.desc())
        .limit(limit)
    ).all()
    return schemas.GuidanceRecordListOut(
        items=[schemas.GuidanceRecordOut.model_validate(r) for r in rows]
    )
