"""学生个人档案聚合页 endpoint (spec §7.10 #32)。

端点:
- GET /api/v1/students/{student_id}/profile  — 聚合返回该学生所有维度的履历

角色 gate:
- 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教师/管理係）— 可看全部(含指导履历)
- 学生本人 — 只能看自己（指导履历 tab 不返回，符合 §7.10 C 案默认不显示）

实现说明:
- 只读现有表，不建表、不建迁移
- 各子块给最近 N 条（默认 20），带独立 limit query 参数
- 指导履历块：非寮務角色/学生自己 → 返空列表而非 403（符合 C 案"不显示 tab"语义）
- 用 Annotated[Optional[str], Header()] 取 Authorization header，避免 ruff 删 import
"""

# 注意：不加 `from __future__ import annotations`，避免 ruff 以为 Header 未使用而删 import

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db

router = APIRouter(prefix="/api/v1", tags=["student / profile"])

# 有权查看指导履历块的角色（同 guidance.py）
_GUIDANCE_ROLES = {
    "寮務部長",
    "寮務課長",
    "寮監",
    "寮務一般教师",
    "管理係",
}


def _get_student_or_404(student_id: UUID, db: Session) -> models.Student:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    return student


@router.get(
    "/students/{student_id}/profile",
    response_model=schemas.StudentProfileOut,
)
def get_student_profile(
    student_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="各子块返回最多条数"),
    authorization: Annotated[Optional[str], Header()] = None,
    db: Session = Depends(get_db),
) -> schemas.StudentProfileOut:
    """学生个人档案聚合页 (#32)。

    调用者可以是:
    - 寮務系老师: 可看全部，含指导履历
    - 学生本人: 只能看自己，指导履历返空（C 案）
    - 其他老师: 403

    实现: 用 Authorization header 拿到 token，判断是老师还是学生，再做权限分流。
    """
    # ---- 鉴权：解析 Authorization: Bearer <token> ----
    actor_teacher: Optional[models.Teacher] = None
    actor_student: Optional[models.Student] = None

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "ログインが必要です"},
        )

    token = authorization.split(" ", 1)[1]
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )

    role = payload.get("role", "")
    sub = payload.get("sub")

    if role.startswith("teacher:"):
        actor_teacher = db.get(models.Teacher, UUID(sub))
        if not actor_teacher or actor_teacher.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "アカウントが利用不可です",
                },
            )
    elif role == "student":
        actor_student = db.get(models.Student, UUID(sub))
        if not actor_student or actor_student.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "アカウントが利用不可です",
                },
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "不明な token role"},
        )

    # ---- 老师鉴权：只有寮務系才能查 ----
    if actor_teacher is not None:
        if actor_teacher.role not in _GUIDANCE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": "学生个人档案需要寮務系老师权限",
                },
            )

    # ---- 学生只能查自己 ----
    if actor_student is not None:
        if actor_student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "他の学生のプロフィールは閲覧できません",
                },
            )

    # ---- 查学生基本信息 ----
    student = _get_student_or_404(student_id, db)

    # ---- 子块查询（各最近 limit 条，按时间倒序）----

    # 1. 出寮届履历（applications 表）
    applications = db.scalars(
        select(models.Application)
        .where(models.Application.student_id == student_id)
        .order_by(models.Application.submitted_at.desc())
        .limit(limit)
    ).all()

    # 2. 学习出席记录（study_checkins 表）
    study_checkins = db.scalars(
        select(models.StudyCheckin)
        .where(models.StudyCheckin.student_id == student_id)
        .order_by(models.StudyCheckin.target_date.desc())
        .limit(limit)
    ).all()

    # 3. 点呼记录（rollcall_events 表）
    rollcall_events = db.scalars(
        select(models.RollCallEvent)
        .where(models.RollCallEvent.student_id == student_id)
        .order_by(models.RollCallEvent.checked_in_at.desc())
        .limit(limit)
    ).all()

    # 4. 指导履历（guidance_records 表）
    #    学生本人 → 空列表（C 案：默认不显示）
    #    寮務系老师 → 全部可见
    if actor_teacher is not None and actor_teacher.role in _GUIDANCE_ROLES:
        guidance_records = db.scalars(
            select(models.GuidanceRecord)
            .where(
                models.GuidanceRecord.student_id == student_id,
                models.GuidanceRecord.deleted_at.is_(None),
            )
            .order_by(models.GuidanceRecord.guidance_date.desc())
            .limit(limit)
        ).all()
    else:
        guidance_records = []

    # 5. 扣分记录（demerit_event 表，排除已撤销）
    demerit_events = db.scalars(
        select(models.DemeritEvent)
        .where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .order_by(models.DemeritEvent.created_at.desc())
        .limit(limit)
    ).all()

    # ---- 组装响应 ----
    return schemas.StudentProfileOut(
        student=schemas.StudentProfileBasic(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            name_kana=student.name_kana,
            grade_code=student.grade_code,
            class_code=student.class_code,
            seat_no=student.seat_no,
            gender=student.gender,
            room_no=student.room_no,
            dorm_unit=student.dorm_unit,
            is_overseas=student.is_overseas,
            email=student.email,
            phone=student.phone,
            avatar_url=student.avatar_url,
            status=student.status,
            registered_at=student.registered_at,
        ),
        applications=[
            schemas.ProfileApplicationEntry(
                id=a.id,
                kind=a.kind,
                leave_date=a.leave_date,
                return_date=a.return_date,
                status=a.status,
                submitted_at=a.submitted_at,
            )
            for a in applications
        ],
        study_checkins=[
            schemas.ProfileStudyCheckinEntry(
                id=sc.id,
                target_date=sc.target_date,
                status=sc.status,
                checked_at=sc.checked_at,
            )
            for sc in study_checkins
        ],
        rollcall_events=[
            schemas.ProfileRollCallEntry(
                id=rce.id,
                session_id=rce.session_id,
                base_status=rce.base_status,
                status_source=rce.status_source,
                checked_in_at=rce.checked_in_at,
            )
            for rce in rollcall_events
        ],
        guidance_records=[
            schemas.ProfileGuidanceEntry(
                id=gr.id,
                category=gr.category,
                guidance_date=gr.guidance_date,
                confidential=gr.confidential,
                content=gr.content,
                created_at=gr.created_at,
            )
            for gr in guidance_records
        ],
        demerit_events=[
            schemas.ProfileDemeritEntry(
                id=de.id,
                source_type=de.source_type,
                points=de.points,
                reason=de.reason,
                month=de.month,
                created_at=de.created_at,
            )
            for de in demerit_events
        ],
    )
