"""在线学习申请 endpoint。

POST /api/v1/study/online-requests                 — 学生提交
GET  /api/v1/study/online-requests/mine            — 学生看自己的申请
GET  /api/v1/study/online-requests                 — 老师看待审列表
POST /api/v1/study/online-requests/{id}/decision   — 老师审批 / 取消许可
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student, get_current_teacher, require_teacher_roles

router = APIRouter(prefix="/api/v1/study/online-requests", tags=["study"])

ONLINE_NOTICE_DAYS = 3


def _today_jst() -> date:
    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _now_jst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tokyo"))


@router.post(
    "",
    response_model=schemas.StudyOnlineRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_online_request(
    body: schemas.StudyOnlineRequestIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    # 在线学习申请必须在开始 3 天前提交。
    earliest_start = _today_jst() + timedelta(days=ONLINE_NOTICE_DAYS)
    if body.period_from < earliest_start:
        raise HTTPException(
            422,
            {
                "code": "ONLINE_REQUEST_TOO_LATE",
                "message": "オンライン学習申請は開始 3 日前までに提出してください",
            },
        )

    record = models.StudyOnlineRequest(
        student_id=student.id,
        reason=body.reason,
        period_from=body.period_from,
        period_to=body.period_to,
        weekly_schedule=body.weekly_schedule,
        contract_ref=body.contract_ref,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.StudyOnlineRequestOut.model_validate(record)


@router.get("/mine", response_model=list[schemas.StudyOnlineRequestOut])
def list_my_online_requests(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.StudyOnlineRequest)
        .where(models.StudyOnlineRequest.student_id == student.id)
        .order_by(models.StudyOnlineRequest.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.StudyOnlineRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.StudyOnlineRequestOut.model_validate(row) for row in rows]


@router.get("", response_model=list[schemas.StudyOnlineRequestOut])
def list_online_requests(
    status_filter: str | None = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    stmt = select(models.StudyOnlineRequest).order_by(
        models.StudyOnlineRequest.submitted_at.asc()
    )
    if status_filter:
        stmt = stmt.where(models.StudyOnlineRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.StudyOnlineRequestOut.model_validate(row) for row in rows]


@router.post(
    "/{request_id}/decision",
    response_model=schemas.StudyOnlineRequestOut,
)
def decide_online_request(
    request_id: UUID,
    body: schemas.StudyOnlineDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("学習担当", "寮務部長", "寮務課長", "寮監")
    ),
):
    record = db.get(models.StudyOnlineRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})

    if body.decision == "revoked":
        if record.status != "approved":
            raise HTTPException(
                409,
                {
                    "code": "CANNOT_REVOKE",
                    "message": "許可済みの申請だけ取り消せます",
                },
            )
    elif record.status != "pending":
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )

    record.status = body.decision
    record.decided_by = teacher.id
    record.decided_at = _now_jst()
    record.comment = body.comment
    db.commit()
    db.refresh(record)
    return schemas.StudyOnlineRequestOut.model_validate(record)
