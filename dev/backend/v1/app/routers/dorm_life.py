"""宿舍生活类申请 endpoint。

4 种申请都采用 v1.0 单状态字段模式：
- 寮生行事企画申請
- 寮日課変更願
- 冷蔵庫購入届
- 物品所持許可願
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    get_current_teacher,
    require_permission,
)

router = APIRouter(prefix="/api/v1/dorm-life", tags=["dorm-life"])


def _now_jst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def _filter_student_scope(stmt, student_id_column, teacher: models.Teacher):
    """按老师负责寮 + 演示隔离过滤学生提交类申请。

    总 join 学生表叠加 demo 过滤：真老师只看真实学生申请 / 演示老师只看演示学生申请。
    （原先跨寮老师 dorm_units=None 时直接 return stmt 完全不过滤，演示数据会漏给真老师 —
    现改成无论是否跨寮都按 demo 过滤，仅 dorm 限制是条件叠加的。）
    """
    dorm_units = dorm_units_for_teacher(teacher)
    stmt = stmt.join(models.Student, models.Student.id == student_id_column).where(
        demo_scope_for_teacher(teacher)
    )
    if dorm_units is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(dorm_units))
    return stmt


def _ensure_pending(current_status: str) -> None:
    if current_status != "pending":
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )


# ---------------------------------------------------------------
# 寮生行事企画申請
# ---------------------------------------------------------------
@router.post(
    "/event-proposals",
    response_model=schemas.DormEventProposalOut,
    status_code=status.HTTP_201_CREATED,
)
def create_event_proposal(
    body: schemas.DormEventProposalCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    record = models.DormEventProposal(proposer_id=student.id, **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.DormEventProposalOut.model_validate(record)


@router.get("/event-proposals/mine", response_model=list[schemas.DormEventProposalOut])
def list_my_event_proposals(
    result_filter: str | None = Query(None, alias="result"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.DormEventProposal)
        .where(models.DormEventProposal.proposer_id == student.id)
        .order_by(models.DormEventProposal.submitted_at.desc())
    )
    if result_filter:
        stmt = stmt.where(models.DormEventProposal.result == result_filter)
    rows = db.scalars(stmt).all()
    return [schemas.DormEventProposalOut.model_validate(row) for row in rows]


@router.get("/event-proposals", response_model=list[schemas.DormEventProposalOut])
def list_event_proposals(
    result_filter: str | None = Query("pending", alias="result"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = select(models.DormEventProposal).order_by(
        models.DormEventProposal.submitted_at.asc()
    )
    if result_filter:
        stmt = stmt.where(models.DormEventProposal.result == result_filter)
    stmt = _filter_student_scope(stmt, models.DormEventProposal.proposer_id, teacher)
    rows = db.scalars(stmt).all()
    return [schemas.DormEventProposalOut.model_validate(row) for row in rows]


@router.post(
    "/event-proposals/{proposal_id}/decision",
    response_model=schemas.DormEventProposalOut,
)
def decide_event_proposal(
    proposal_id: UUID,
    body: schemas.DormEventProposalDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    record = db.get(models.DormEventProposal, proposal_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    # 提出学生若已被删（proposer 关系悬空 None），不能直接读 None.is_demo（否则 500）。
    # 学生缺失时当作申請不存在 404，与「缺数据即拒绝」方向一致。
    if record.proposer is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    assert_student_demo_match(teacher, record.proposer)
    _ensure_pending(record.result)
    # 原子条件更新：只有 result 仍是 pending 才写决定。两老师并发审批同一申請时，
    # 后写者命中 0 行 → 409，避免覆盖前者的 decided_by/comment（照 outings.py confirm 做法）。
    affected = db.execute(
        update(models.DormEventProposal)
        .where(
            models.DormEventProposal.id == proposal_id,
            models.DormEventProposal.result == "pending",
        )
        .values(
            result=body.decision,
            decided_by=teacher.id,
            decided_at=_now_jst(),
            comment=body.comment,
        )
    )
    if affected.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    db.commit()
    db.refresh(record)
    return schemas.DormEventProposalOut.model_validate(record)


@router.post(
    "/event-proposals/{proposal_id}/resubmit",
    response_model=schemas.DormEventProposalOut,
)
def resubmit_event_proposal(
    proposal_id: UUID,
    body: schemas.DormEventProposalCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """提出学生本人が「再提出を求める(resubmit)」判定の企画を修正して再提出。

    老师が result='resubmit' にした企画のみ再提出可。再提出すると内容を上書き +
    result='pending' に戻し、decided_by/decided_at/comment をクリアして再審査に回す。
    其他状态（pending 审查中 / approved / approved_conditional / rejected）不可重提。
    """
    record = db.get(models.DormEventProposal, proposal_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    if record.proposer_id != student.id:
        raise HTTPException(
            403, {"code": "FORBIDDEN", "message": "他人の申請は再提出できません"}
        )
    if record.result != "resubmit":
        raise HTTPException(
            409,
            {
                "code": "CANNOT_RESUBMIT",
                "message": "再提出を求められた申請のみ再提出できます",
            },
        )
    # 原子条件更新：只有 result 仍是 'resubmit' 才写成功（防并发 / 重复重提覆盖）。
    affected = db.execute(
        update(models.DormEventProposal)
        .where(
            models.DormEventProposal.id == proposal_id,
            models.DormEventProposal.result == "resubmit",
        )
        .values(
            result="pending",
            decided_by=None,
            decided_at=None,
            comment=None,
            submitted_at=_now_jst(),
            **body.model_dump(),
        )
    )
    if affected.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "CANNOT_RESUBMIT",
                "message": "再提出を求められた申請のみ再提出できます",
            },
        )
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="dorm_event_proposal.resubmit",
            target_type="dorm_event_proposal",
            target_id=proposal_id,
            payload={"title": body.title},
        )
    )
    db.commit()
    db.refresh(record)
    return schemas.DormEventProposalOut.model_validate(record)


# ---------------------------------------------------------------
# 寮日課変更願
# ---------------------------------------------------------------
@router.post(
    "/schedule-changes",
    response_model=schemas.DormScheduleChangeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule_change(
    body: schemas.DormScheduleChangeCreateIn,
    db: Session = Depends(get_db),
    # 补权限闸：与同资源 GET（list_my / list_schedule_changes 的 C_APPROVAL VIEW）口径一致，
    # 不再裸用 get_current_teacher（原来任何老师令牌都能创建、绕过权限簇声明）。TW-071/110。
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    record = models.DormScheduleChange(requester_id=teacher.id, **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.DormScheduleChangeOut.model_validate(record)


@router.get(
    "/schedule-changes/mine", response_model=list[schemas.DormScheduleChangeOut]
)
def list_my_schedule_changes(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = (
        select(models.DormScheduleChange)
        .where(models.DormScheduleChange.requester_id == teacher.id)
        .order_by(models.DormScheduleChange.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.DormScheduleChange.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.DormScheduleChangeOut.model_validate(row) for row in rows]


@router.get("/schedule-changes", response_model=list[schemas.DormScheduleChangeOut])
def list_schedule_changes(
    status_filter: str | None = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = select(models.DormScheduleChange).order_by(
        models.DormScheduleChange.submitted_at.asc()
    )
    if status_filter:
        stmt = stmt.where(models.DormScheduleChange.status == status_filter)
    # 演示隔离 — 寮日課変更願是「老师提交」的（requester_id → teachers.id），没有学生，
    # 故不能用 _filter_student_scope（那个 join Student）。改 join 申请老师表按 is_demo 对齐：
    # 真老师只看真老师提交的申请、演示老师只看演示老师提交的，防演示数据漏给真老师。
    stmt = stmt.join(
        models.Teacher, models.Teacher.id == models.DormScheduleChange.requester_id
    ).where(models.Teacher.is_demo == teacher.is_demo)
    rows = db.scalars(stmt).all()
    return [schemas.DormScheduleChangeOut.model_validate(row) for row in rows]


@router.post(
    "/schedule-changes/{change_id}/decision",
    response_model=schemas.DormScheduleChangeOut,
)
def decide_schedule_change(
    change_id: UUID,
    body: schemas.DormScheduleChangeDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    record = db.get(models.DormScheduleChange, change_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    # 演示隔离 — 本申请由老师提交（无学生），故不能用 assert_student_demo_match（那个比学生 is_demo）。
    # 比申请老师（record.requester）与当前老师 is_demo：演示老师只能决定演示老师的申请，反之亦然。
    # 提交老师若已被删（requester 关系悬空 None），不能直接读 None.is_demo（否则 500），当作不存在 404。
    if record.requester is None or record.requester.is_demo != teacher.is_demo:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    _ensure_pending(record.status)
    # 原子条件更新：只有 status 仍是 pending 才写决定，防两老师并发审批互相覆盖（照 outings.py 做法）。
    affected = db.execute(
        update(models.DormScheduleChange)
        .where(
            models.DormScheduleChange.id == change_id,
            models.DormScheduleChange.status == "pending",
        )
        .values(
            status=body.decision,
            decided_by=teacher.id,
            decided_at=_now_jst(),
            comment=body.comment,
        )
    )
    if affected.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    db.commit()
    db.refresh(record)
    return schemas.DormScheduleChangeOut.model_validate(record)


# ---------------------------------------------------------------
# 冷蔵庫購入届
# ---------------------------------------------------------------
@router.post(
    "/fridge-purchases",
    response_model=schemas.FridgePurchaseRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_fridge_purchase(
    body: schemas.FridgePurchaseRequestCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    record = models.FridgePurchaseRequest(student_id=student.id, **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.FridgePurchaseRequestOut.model_validate(record)


@router.get(
    "/fridge-purchases/mine", response_model=list[schemas.FridgePurchaseRequestOut]
)
def list_my_fridge_purchases(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.FridgePurchaseRequest)
        .where(models.FridgePurchaseRequest.student_id == student.id)
        .order_by(models.FridgePurchaseRequest.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.FridgePurchaseRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.FridgePurchaseRequestOut.model_validate(row) for row in rows]


@router.get("/fridge-purchases", response_model=list[schemas.FridgePurchaseRequestOut])
def list_fridge_purchases(
    status_filter: str | None = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = select(models.FridgePurchaseRequest).order_by(
        models.FridgePurchaseRequest.submitted_at.asc()
    )
    if status_filter:
        stmt = stmt.where(models.FridgePurchaseRequest.status == status_filter)
    stmt = _filter_student_scope(stmt, models.FridgePurchaseRequest.student_id, teacher)
    rows = db.scalars(stmt).all()
    return [schemas.FridgePurchaseRequestOut.model_validate(row) for row in rows]


@router.post(
    "/fridge-purchases/{request_id}/decision",
    response_model=schemas.FridgePurchaseRequestOut,
)
def decide_fridge_purchase(
    request_id: UUID,
    body: schemas.FridgePurchaseDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    record = db.get(models.FridgePurchaseRequest, request_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    # 提出学生若已被删（student 关系悬空 None），不能直接读 None.is_demo（否则 500），当作不存在 404。
    if record.student is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    assert_student_demo_match(teacher, record.student)
    # 冷蔵庫購入届合法状态流转白名单：pending→ordered/rejected、ordered→delivered
    # 白名单外（ordered→rejected、已 delivered/rejected 再次决定、同状态重复覆盖等）一律拒绝
    _allowed_fridge_transitions: dict[str, set[str]] = {
        "pending": {"ordered", "rejected"},
        "ordered": {"delivered"},
    }
    # 记下读到的当前状态 — 既校验白名单，又作为原子更新的 WHERE 条件防并发覆盖
    current_status = record.status
    if body.decision not in _allowed_fridge_transitions.get(current_status, set()):
        # pending 想直接跳 delivered 的情况用专用提示引导
        if current_status == "pending" and body.decision == "delivered":
            raise HTTPException(
                409,
                {"code": "CANNOT_DELIVER", "message": "注文済みの申請だけ引き渡せます"},
            )
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    # 原子条件更新：WHERE status = 校验时读到的状态。若并发请求已把状态改掉（如已 ordered），
    # 本次命中 0 行 → 409，避免两老师并发把同一申請推到冲突状态（照 outings.py 做法）。
    values: dict = {
        "status": body.decision,
        "decided_by": teacher.id,
        "decided_at": _now_jst(),
        "comment": body.comment,
    }
    if body.delivered_sign is not None:
        values["delivered_sign"] = body.delivered_sign
    affected = db.execute(
        update(models.FridgePurchaseRequest)
        .where(
            models.FridgePurchaseRequest.id == request_id,
            models.FridgePurchaseRequest.status == current_status,
        )
        .values(**values)
    )
    if affected.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    db.commit()
    db.refresh(record)
    return schemas.FridgePurchaseRequestOut.model_validate(record)


# ---------------------------------------------------------------
# 物品所持許可願
# ---------------------------------------------------------------
@router.post(
    "/item-possessions",
    response_model=schemas.ItemPossessionRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_item_possession(
    body: schemas.ItemPossessionRequestCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    record = models.ItemPossessionRequest(student_id=student.id, **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.ItemPossessionRequestOut.model_validate(record)


@router.get(
    "/item-possessions/mine", response_model=list[schemas.ItemPossessionRequestOut]
)
def list_my_item_possessions(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.ItemPossessionRequest)
        .where(models.ItemPossessionRequest.student_id == student.id)
        .order_by(models.ItemPossessionRequest.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.ItemPossessionRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.ItemPossessionRequestOut.model_validate(row) for row in rows]


@router.get("/item-possessions", response_model=list[schemas.ItemPossessionRequestOut])
def list_item_possessions(
    status_filter: str | None = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = select(models.ItemPossessionRequest).order_by(
        models.ItemPossessionRequest.submitted_at.asc()
    )
    if status_filter:
        stmt = stmt.where(models.ItemPossessionRequest.status == status_filter)
    stmt = _filter_student_scope(stmt, models.ItemPossessionRequest.student_id, teacher)
    rows = db.scalars(stmt).all()
    return [schemas.ItemPossessionRequestOut.model_validate(row) for row in rows]


@router.post(
    "/item-possessions/{request_id}/decision",
    response_model=schemas.ItemPossessionRequestOut,
)
def decide_item_possession(
    request_id: UUID,
    body: schemas.ItemPossessionDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    record = db.get(models.ItemPossessionRequest, request_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    # 提出学生若已被删（student 关系悬空 None），不能直接读 None.is_demo（否则 500），当作不存在 404。
    if record.student is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "申請が見つかりません"}
        )
    assert_student_demo_match(teacher, record.student)
    _ensure_pending(record.status)
    # 原子条件更新：只有 status 仍是 pending 才写决定，防两老师并发审批互相覆盖（照 outings.py 做法）。
    affected = db.execute(
        update(models.ItemPossessionRequest)
        .where(
            models.ItemPossessionRequest.id == request_id,
            models.ItemPossessionRequest.status == "pending",
        )
        .values(
            status=body.decision,
            decided_by=teacher.id,
            decided_at=_now_jst(),
            comment=body.comment,
        )
    )
    if affected.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    db.commit()
    db.refresh(record)
    return schemas.ItemPossessionRequestOut.model_validate(record)
