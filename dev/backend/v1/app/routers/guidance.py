"""指導履歴 + 开示申请 endpoint (spec §7.9/§7.10)。

端点:
- POST /api/v1/students/{student_id}/guidance       — 老师录入指导记录
- GET  /api/v1/students/{student_id}/guidance       — 查某学生全部指导记录（老师）
- POST /api/v1/students/{student_id}/guidance/disclosure-request  — 学生提交开示申请
- GET  /api/v1/guidance/disclosure-requests         — 老师查开示申请列表
- POST /api/v1/guidance/disclosure-requests/{id}/decision         — 老师决定开示

角色 gate:
- 录入 / 查记录 / 决定开示: 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教師/管理係）
- 提交开示申请: 学生本人
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    require_permission,
)

router = APIRouter(prefix="/api/v1", tags=["guidance"])

# 有权录入指导记录 + 查看 + 决定开示的角色
# 指导履历的功能权限（C_GUIDANCE：管理动作 M / 查看动作 V）由各端点的 require_permission 闸判定，
# 不再按职位拦（旧 _GUIDANCE_ROLES 职位集已随权限分级改造移除）。寮边界仍在端点内单独校验。


def _get_student_or_404(student_id: UUID, db: Session) -> models.Student:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
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

    # R4 寮边界：跨寮角色（返回 None）可写全部；其他老师只能写自己管辖寮的学生
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
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
        )

    # R4 寮边界：跨寮角色（dorm_units_for_teacher 返回 None）可查全部；
    # 其他老师只能查自己管辖寮的学生
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


# -----------------------------------------------------------------------
# 开示申请 — 学生发起
# -----------------------------------------------------------------------
@router.post(
    "/students/{student_id}/guidance/disclosure-request",
    response_model=schemas.GuidanceDisclosureRequestOut,
    status_code=201,
)
def create_disclosure_request(
    student_id: UUID,
    body: schemas.GuidanceDisclosureRequestIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """学生提交查看自己指导履历的开示申请（只能申请自己的）。"""
    if student.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "只能申请查看自己的指导履历"},
        )
    # 已有 pending 申请时不重复提交。这里的预查只是「快路径」给单线程的常见情况一个干净的
    # 409，真正防并发的不变量靠 DB 部分唯一索引 uq_gdr_one_pending_per_student 兜底（见下）。
    existing = db.scalar(
        select(models.GuidanceDisclosureRequest).where(
            models.GuidanceDisclosureRequest.student_id == student_id,
            models.GuidanceDisclosureRequest.status == "pending",
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_PENDING", "message": "已有待处理的开示申请"},
        )

    row = models.GuidanceDisclosureRequest(
        student_id=student_id,
        reason=body.reason,
    )
    db.add(row)
    db.flush()
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="guidance.disclosure.request",
            target_type="guidance_disclosure_requests",
            target_id=row.id,
            payload={"student_id": str(student_id)},
        )
    )
    try:
        db.commit()
    except IntegrityError:
        # 并发兜底：两个请求几乎同时到，预查都没命中、各自 add，第二个 commit 撞
        # uq_gdr_one_pending_per_student 部分唯一索引 → 回滚后转 409（而非 500）。
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_PENDING", "message": "已有待处理的开示申请"},
        ) from None
    db.refresh(row)
    # 手动加载 student relation 以满足 from_row 要求
    _ = row.student
    return schemas.GuidanceDisclosureRequestOut.from_row(row)


# -----------------------------------------------------------------------
# 开示申请 — 老师查列表 + 决定
# -----------------------------------------------------------------------
@router.get(
    "/guidance/disclosure-requests",
    response_model=schemas.GuidanceDisclosureListOut,
)
def list_disclosure_requests(
    include_revoked: bool = False,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_GUIDANCE, permissions.VIEW)
    ),
):
    """老师查开示申请列表（按申请时间倒序）。
    默认过滤 revoked_at IS NULL（未撤销），include_revoked=true 可看全部。
    R4 寮过滤：跨寮角色看全部；其他老师只看自己管辖寮的学生的申请。
    """

    # 演示隔离：始终 join Student 并按 demo 过滤（真老师只看真学生 / 演示老师只看演示学生），
    # 否则跨寮演示老师能看到真实学生的开示申请 = 泄漏。
    stmt = (
        select(models.GuidanceDisclosureRequest)
        .options(selectinload(models.GuidanceDisclosureRequest.student))
        .join(
            models.Student,
            models.GuidanceDisclosureRequest.student_id == models.Student.id,
        )
        .where(demo_scope_for_teacher(teacher))
        .order_by(models.GuidanceDisclosureRequest.requested_at.desc())
    )
    if not include_revoked:
        stmt = stmt.where(models.GuidanceDisclosureRequest.revoked_at.is_(None))

    # R4 寮边界过滤
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))

    rows = db.scalars(stmt).all()
    return schemas.GuidanceDisclosureListOut(
        items=[schemas.GuidanceDisclosureRequestOut.from_row(r) for r in rows]
    )


@router.post(
    "/guidance/disclosure-requests/{request_id}/decision",
    response_model=schemas.GuidanceDisclosureRequestOut,
)
def decide_disclosure(
    request_id: UUID,
    body: schemas.GuidanceDisclosureDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_GUIDANCE, permissions.MANAGE)
    ),
):
    """老师决定开示：全部开示 / 部分开示 / 拒绝。"""

    row = db.scalar(
        select(models.GuidanceDisclosureRequest)
        .where(models.GuidanceDisclosureRequest.id == request_id)
        .options(selectinload(models.GuidanceDisclosureRequest.student))
    )
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "REQUEST_NOT_FOUND", "message": "开示申请不存在"},
        )
    if row.status != "pending":
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_DECIDED", "message": "该申请已有决定"},
        )

    # R4 寮边界：从申请行拿 student_id，查该学生所属寮
    disclosure_student = _get_student_or_404(row.student_id, db)
    # 演示写隔离：演示老师只能决定演示学生的开示申请、真老师只能决定真实学生的（否则 404 隐藏存在性）
    assert_student_demo_match(teacher, disclosure_student)
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and disclosure_student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生の開示申請は審査できません",
            },
        )

    now = datetime.now(timezone.utc)
    row.status = body.decision
    row.decided_by = teacher.id
    row.decided_at = now
    row.decision_note = body.decision_note
    row.visible_from = body.visible_from
    row.visible_until = body.visible_until

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="guidance.disclosure.decide",
            target_type="guidance_disclosure_requests",
            target_id=row.id,
            payload={"decision": body.decision, "student_id": str(row.student_id)},
        )
    )
    db.commit()
    # commit 后 row 属性全部过期；refresh 时显式把 student relation 一并重新加载，
    # 不再依赖随后 from_row 访问 row.student / row.student.student_no 时触发的隐式 lazy load
    # （若将来 refresh 后 session 提前关闭，lazy load 会抛 DetachedInstanceError）。
    db.refresh(row, attribute_names=["student"])
    _ = (
        row.student.student_no
    )  # 顺带把 student 的标量列也加载进 session，from_row 直接用
    return schemas.GuidanceDisclosureRequestOut.from_row(row)
