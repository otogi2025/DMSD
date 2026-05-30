"""事案録入 endpoint (spec §7.9 #33)。

端点:
- POST   /api/v1/incidents           — 老师录入事案
- GET    /api/v1/incidents           — 老师查事案列表
- GET    /api/v1/incidents/{id}      — 老师查事案详情
- PATCH  /api/v1/incidents/{id}      — 老师编辑事案
- DELETE /api/v1/incidents/{id}      — 老师软删事案

角色 gate: 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教师/管理係）
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_teacher

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])

_INCIDENT_ROLES = {
    "寮務部長",
    "寮務課長",
    "寮監",
    "寮務一般教师",
    "管理係",
}


def _require_incident_role(teacher: models.Teacher) -> None:
    if teacher.role not in _INCIDENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "事案录入需要寮務系老师权限",
            },
        )


@router.post("", response_model=schemas.IncidentRecordOut, status_code=201)
def create_incident(
    body: schemas.IncidentRecordCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师录入新事案。"""
    _require_incident_role(teacher)

    # 校验涉及学生是否都存在
    for sid in body.involved_student_ids:
        if not db.get(models.Student, sid):
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"涉及学生 {sid} 不存在",
                },
            )

    row = models.IncidentRecord(
        title=body.title,
        body=body.body,
        involved_student_ids=[str(s) for s in body.involved_student_ids],
        recorded_by=teacher.id,
        incident_date=body.incident_date,
    )
    db.add(row)
    db.flush()  # 让 row.id 生效
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.create",
            target_type="incident_records",
            target_id=row.id,
            payload={
                "title": body.title,
                "incident_date": str(body.incident_date),
                "involved_count": len(body.involved_student_ids),
            },
        )
    )
    db.commit()
    db.refresh(row)
    return schemas.IncidentRecordOut.model_validate(row)


@router.get("", response_model=schemas.IncidentRecordListOut)
def list_incidents(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师查事案列表（按事发日期倒序，排除软删）。"""
    _require_incident_role(teacher)

    rows = db.scalars(
        select(models.IncidentRecord)
        .where(models.IncidentRecord.deleted_at.is_(None))
        .order_by(models.IncidentRecord.incident_date.desc())
    ).all()
    return schemas.IncidentRecordListOut(
        items=[schemas.IncidentRecordOut.model_validate(r) for r in rows]
    )


@router.get("/{incident_id}", response_model=schemas.IncidentRecordOut)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师查事案详情。"""
    _require_incident_role(teacher)

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": "事案不存在"},
        )
    return schemas.IncidentRecordOut.model_validate(row)


@router.patch("/{incident_id}", response_model=schemas.IncidentRecordOut)
def patch_incident(
    incident_id: UUID,
    body: schemas.IncidentRecordPatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师编辑事案（部分更新）。"""
    _require_incident_role(teacher)

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": "事案不存在"},
        )

    if body.title is not None:
        row.title = body.title
    if body.body is not None:
        row.body = body.body
    if body.involved_student_ids is not None:
        for sid in body.involved_student_ids:
            if not db.get(models.Student, sid):
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "STUDENT_NOT_FOUND",
                        "message": f"涉及学生 {sid} 不存在",
                    },
                )
        row.involved_student_ids = [str(s) for s in body.involved_student_ids]
    if body.incident_date is not None:
        row.incident_date = body.incident_date

    row.updated_at = datetime.now(timezone.utc)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.patch",
            target_type="incident_records",
            target_id=row.id,
            payload={"title": row.title},
        )
    )
    db.commit()
    db.refresh(row)
    return schemas.IncidentRecordOut.model_validate(row)


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师软删事案（设 deleted_at，不物理删除）。"""
    _require_incident_role(teacher)

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": "事案不存在"},
        )

    row.deleted_at = datetime.now(timezone.utc)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.delete",
            target_type="incident_records",
            target_id=row.id,
            payload={},
        )
    )
    db.commit()
