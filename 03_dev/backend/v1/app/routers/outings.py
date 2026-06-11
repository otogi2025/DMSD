"""外出申请 endpoint — 当天回寮的短时间外出，单一老师确认（itsuki 2026-06-04 拍板）。

POST   /api/v1/outings                 — 学生提出外出申请
GET    /api/v1/outings/mine            — 学生看自己的外出申请
GET    /api/v1/outings/pending-for-me  — 老师看待确认列表（按 R4 寮边界过滤）
GET    /api/v1/outings/{id}            — 详情（学生本人 / 受寮边界的老师）
PATCH  /api/v1/outings/{id}/confirm    — 老师确认（确认者从登录令牌取，不信任客户端）
PATCH  /api/v1/outings/{id}/withdraw   — 学生撤回自己 pending 的申请

跟出寮届（applications）的区别见 system_features §7.2.7：不过夜 / 没有多级审查 /
一名老师确认即可，确认老师从登录令牌自动记录。
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
    require_permission,
)

_JST = ZoneInfo("Asia/Tokyo")

router = APIRouter(prefix="/api/v1/outings", tags=["outings"])


def _to_outing_out(o: models.Outing) -> schemas.OutingOut:
    """ORM 外出对象 → 输出 schema；confirmed_by_name 从确认老师关系取姓名。"""
    student_brief = None
    if o.student:
        student_brief = schemas.StudentBrief(
            id=o.student.id,
            student_no=o.student.student_no,
            name=o.student.name,
            dorm_unit=o.student.dorm_unit,
            is_overseas=o.student.is_overseas,
            room_no=o.student.room_no,
        )
    return schemas.OutingOut(
        id=o.id,
        student_id=o.student_id,
        student=student_brief,
        outing_date=o.outing_date,
        destination=o.destination,
        leave_time=o.leave_time,
        return_time=o.return_time,
        taxi_reservation_time=o.taxi_reservation_time,
        reason=o.reason,
        status=o.status,
        submitted_at=o.submitted_at,
        withdrawn_at=o.withdrawn_at,
        confirmed_by_teacher_id=o.confirmed_by_teacher_id,
        confirmed_by_name=(o.confirmed_by.name if o.confirmed_by else None),
        confirmed_at=o.confirmed_at,
    )


# ---------------------------------------------------------------
# POST /outings — 学生提出外出申请
# ---------------------------------------------------------------
@router.post("", response_model=schemas.OutingOut, status_code=status.HTTP_201_CREATED)
def create_outing(
    body: schemas.OutingCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    # 外出是当天回寮，外出日不能是过去（今天及以后都允许，跟出寮届「明天起」不同）
    if body.outing_date < datetime.now(_JST).date():
        raise HTTPException(
            status_code=422,
            detail={
                "code": "OUTING_DATE_PAST",
                "message": "外出日は本日以降を指定してください",
            },
        )

    outing = models.Outing(
        student_id=student.id,
        outing_date=body.outing_date,
        destination=body.destination,
        leave_time=body.leave_time,
        return_time=body.return_time,
        taxi_reservation_time=body.taxi_reservation_time,
        reason=body.reason,
        status="pending",
    )
    outing.student = student
    db.add(outing)
    db.flush()

    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="outing.submit",
            target_type="outing",
            target_id=outing.id,
            payload={"outing_date": outing.outing_date.isoformat()},
        )
    )
    db.commit()
    db.refresh(outing)
    return _to_outing_out(outing)


# ---------------------------------------------------------------
# GET /outings/mine — 学生看自己的外出申请
# ---------------------------------------------------------------
@router.get("/mine", response_model=list[schemas.OutingOut])
def list_mine(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.Outing)
        .where(models.Outing.student_id == student.id)
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
        .order_by(models.Outing.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.Outing.status == status_filter)
    return [_to_outing_out(o) for o in db.scalars(stmt).all()]


# ---------------------------------------------------------------
# GET /outings/pending-for-me — 老师看待确认列表（必须在 /{id} 之前注册）
#
# 跟 applications/pending-for-me 同理：静态路径在前 / 动态路径在后，
# 否则 "pending-for-me" 会被当成 UUID 解析 → 422。
# ---------------------------------------------------------------
@router.get("/pending-for-me", response_model=list[schemas.OutingOut])
def list_pending_for_me(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    stmt = (
        select(models.Outing)
        .join(models.Student, models.Student.id == models.Outing.student_id)
        .where(
            models.Outing.status == "pending",
            demo_scope_for_teacher(teacher),
        )
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
        .order_by(models.Outing.submitted_at.asc())
    )
    # R4 寮边界：非跨寮角色只看自己寮的学生
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    return [_to_outing_out(o) for o in db.scalars(stmt).all()]


def _load_outing(db: Session, outing_id: UUID) -> models.Outing:
    outing = db.scalars(
        select(models.Outing)
        .where(models.Outing.id == outing_id)
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
    ).first()
    if not outing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "外出申請が見つかりません"},
        )
    return outing


# ---------------------------------------------------------------
# GET /outings/{id} — 详情（学生本人 / 受寮边界的老师）
# ---------------------------------------------------------------
@router.get("/{outing_id}", response_model=schemas.OutingOut)
def get_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    actor: models.Student | models.Teacher = Depends(get_current_principal),
):
    outing = _load_outing(db, outing_id)
    if isinstance(actor, models.Student):
        if outing.student_id != actor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "他人の申請は閲覧できません"},
            )
    else:
        # 演示读隔离：演示老师只能看演示学生的外出详情、真老师只能看真实学生（否则 404）。
        # 防演示老师凭真实 outing UUID 越权读真实学生外出详情（codex 第4轮审查指出）。
        assert_student_demo_match(actor, outing.student)
        allowed = dorm_units_for_teacher(actor)
        if allowed is not None and outing.student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "担当寮外の申請です"},
            )
    return _to_outing_out(outing)


# ---------------------------------------------------------------
# PATCH /outings/{id}/confirm — 老师确认
#
# 安全核心：确认者 teacher_id 从登录令牌（get_current_teacher）取，
# 不接受客户端传入；按 R4 寮边界校验老师能不能确认这个学生。
# ---------------------------------------------------------------
@router.patch("/{outing_id}/confirm", response_model=schemas.OutingOut)
def confirm_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    outing = _load_outing(db, outing_id)

    # 演示写隔离：演示老师只能确认演示学生的申请、真老师只能确认真实学生（否则 404）
    assert_student_demo_match(teacher, outing.student)

    # R4 寮边界：非跨寮角色只能确认自己寮的学生
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and outing.student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "担当寮外の申請は確認できません"},
        )

    # 原子条件更新：只有 status 仍是 pending 才确认成功。
    # 防两个老师并发确认 / 确认与撤回并发时都读到 pending、最后一次写覆盖前一次
    # （codex 2026-06-04 审查指出的竞态）。rowcount != 1 说明已被别的请求改掉 → 409。
    result = db.execute(
        update(models.Outing)
        .where(models.Outing.id == outing_id, models.Outing.status == "pending")
        .values(
            status="approved",
            confirmed_by_teacher_id=teacher.id,
            confirmed_at=datetime.now(timezone.utc),
        )
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "OUTING_NOT_PENDING",
                "message": "確認待ちの申請ではありません",
            },
        )

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="outing.confirm",
            target_type="outing",
            target_id=outing_id,
            payload={"teacher_name": teacher.name},
        )
    )
    db.commit()
    # commit 后对象已 expire，重新查（带 selectinload）拿确认后的最新状态 + 确认老师姓名
    return _to_outing_out(_load_outing(db, outing_id))


# ---------------------------------------------------------------
# PATCH /outings/{id}/withdraw — 学生撤回自己 pending 的申请
# ---------------------------------------------------------------
@router.patch("/{outing_id}/withdraw", response_model=schemas.OutingOut)
def withdraw_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    outing = _load_outing(db, outing_id)
    if outing.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "他人の申請は取消できません"},
        )
    # 原子条件更新：只有 status 仍是 pending 才能撤回（防与老师确认并发互相覆盖）
    result = db.execute(
        update(models.Outing)
        .where(models.Outing.id == outing_id, models.Outing.status == "pending")
        .values(status="withdrawn", withdrawn_at=datetime.now(timezone.utc))
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "OUTING_NOT_PENDING",
                "message": "確認待ちの申請のみ取消できます",
            },
        )

    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="outing.withdraw",
            target_type="outing",
            target_id=outing_id,
            payload={},
        )
    )
    db.commit()
    return _to_outing_out(_load_outing(db, outing_id))
