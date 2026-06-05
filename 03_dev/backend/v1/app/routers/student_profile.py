"""学生个人档案聚合页 endpoint (spec §7.10 #32)。

端点:
- GET /api/v1/students/{student_id}/profile  — 聚合返回该学生所有维度的履历

角色 gate:
- 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教師/管理係）— 可看全部(含指导履历)
- 学生本人 — 只能看自己（指导履历 tab 不返回，符合 §7.10 C 案默认不显示）

实现说明:
- 只读现有表，不建表、不建迁移
- 各子块给最近 N 条（默认 20），带独立 limit query 参数
- 指导履历块：非寮務角色/学生自己 → 返空列表而非 403（符合 C 案"不显示 tab"语义）
- 用 Annotated[Optional[str], Header()] 取 Authorization header，避免 ruff 删 import
"""

# 注意：不加 `from __future__ import annotations`，避免 ruff 以为 Header 未使用而删 import

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import (
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
)

router = APIRouter(prefix="/api/v1", tags=["student / profile"])

# 有权查看指导履历块的角色（同 guidance.py）
_GUIDANCE_ROLES = {
    "寮務部長",
    "寮務課長",
    "寮監",
    "寮務一般教師",
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


# IX-008: 登录学生看自己的基本信息（iOS 各页显示当前用户用 — 替换演示假数据 SEED.user）。
# 路由放在 /students/{student_id}/profile 之前 — "me" 是单段、不会被当 UUID 解析（A-013 教训）。
@router.get("/students/me", response_model=schemas.StudentProfileBasic)
def get_my_basic_profile(
    student: models.Student = Depends(get_current_student),
) -> schemas.StudentProfileBasic:
    """GET /students/me — 当前登录学生的基本信息（仿老师端 /teachers/me）。"""
    return schemas.StudentProfileBasic.model_validate(student)


# 学生自设番号（番号再設定，spec §4.2 — 2026-06-05 学生自设方案）。
# 身份从登录令牌取（get_current_student），不信任客户端传 student_id。
# 路由 /students/me/renew-number 是字面段，不会被 /students/{id}/profile 吞。
@router.post("/students/me/renew-number", response_model=schemas.StudentProfileBasic)
def renew_my_number(
    body: schemas.StudentRenewNumberIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> schemas.StudentProfileBasic:
    """学生自设番号 — 选新的 学年/组/出席番号，撞号返 422。

    流程：
        1. 应用层查重：新「年级+班级+出席番号」被别人占（排除自己）→ 422
        2. 改本人三段番号 + 清 needs_renewal=False
        3. commit；并发抢同号 → DB 唯一约束 uq_students_no 兜底，转 422
        4. 写 audit_logs（actor=学生本人）
    """
    new_no = f"{body.grade_code}{body.class_code}{body.seat_no}"

    # 1. 应用层查重（排除自己）— 照 accounts.py 注册查重模式
    existing = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == body.grade_code,
            models.Student.class_code == body.class_code,
            models.Student.seat_no == body.seat_no,
            models.Student.id != student.id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に他の人が設定しています",
            },
        )

    # 2. 改本人三段番号 + 清待更新标记
    student.grade_code = body.grade_code
    student.class_code = body.class_code
    student.seat_no = body.seat_no
    student.needs_renewal = False

    # 3. audit + commit（并发抢同号 → uq_students_no 唯一约束抛 IntegrityError → 转 422）
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="student.renew_number",
            target_type="student",
            target_id=student.id,
            payload={"new_student_no": new_no},
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に他の人が設定しています",
            },
        )

    db.refresh(student)
    return schemas.StudentProfileBasic.model_validate(student)


@router.get(
    "/students/{student_id}/profile",
    response_model=schemas.StudentProfileOut,
)
def get_student_profile(
    student_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="各子块返回最多条数"),
    db: Session = Depends(get_db),
    principal: models.Student | models.Teacher = Depends(get_current_principal),
) -> schemas.StudentProfileOut:
    """学生个人档案聚合页 (#32)。

    调用者可以是:
    - 寮務系老师: 可看全部，含指导履历
    - 学生本人: 只能看自己，指导履历返空（C 案）
    - 其他老师: 403
    """
    actor_teacher: models.Teacher | None = None
    actor_student: models.Student | None = None

    if isinstance(principal, models.Teacher):
        actor_teacher = principal
    else:
        actor_student = principal

    # ---- 老师鉴权：只有寮務系才能查，且受寮边界限制 ----
    if actor_teacher is not None:
        if actor_teacher.role not in _GUIDANCE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": "学生个人档案需要寮務系老师权限",
                },
            )
        # R4 寮边界：先取学生信息才能比对 dorm_unit
        _student_for_check = _get_student_or_404(student_id, db)
        allowed = dorm_units_for_teacher(actor_teacher)
        if allowed is not None and _student_for_check.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当寮外の学生プロフィールは閲覧できません",
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

    # 3. 点呼记录（rollcall_events 表）— join session 取 session_type（朝/夜）
    #    杭田 2026-06-04 五-5：个人档案点呼履历要朝点呼/夜点呼分开，故带上 session_type
    rollcall_rows = db.execute(
        select(models.RollCallEvent, models.RollCallSession.session_type)
        .join(
            models.RollCallSession,
            models.RollCallSession.id == models.RollCallEvent.session_id,
        )
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

    # 6. 在线学习申请履历（study_online_requests 表，含契約書文件信息）
    #    老师点进学生个人页能看到该学生历史上传的所有合同。
    study_online_requests = db.scalars(
        select(models.StudyOnlineRequest)
        .where(models.StudyOnlineRequest.student_id == student_id)
        .order_by(models.StudyOnlineRequest.submitted_at.desc())
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
            category=student.category,
            room_no=student.room_no,
            dorm_unit=student.dorm_unit,
            is_overseas=student.is_overseas,
            email=student.email,
            phone=student.phone,
            avatar_url=student.avatar_url,
            status=student.status,
            registered_at=student.registered_at,
            needs_renewal=student.needs_renewal,
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
                session_type=session_type,
                base_status=rce.base_status,
                status_source=rce.status_source,
                checked_in_at=rce.checked_in_at,
            )
            for rce, session_type in rollcall_rows
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
        study_online_requests=[
            schemas.ProfileStudyOnlineEntry(
                id=so.id,
                period_from=so.period_from,
                period_to=so.period_to,
                status=so.status,
                submitted_at=so.submitted_at,
                contract_file_name=so.contract_file_name,
                contract_mime=so.contract_mime,
                contract_size=so.contract_size,
            )
            for so in study_online_requests
        ],
    )
