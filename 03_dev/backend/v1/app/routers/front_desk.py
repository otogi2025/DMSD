"""前台业务 endpoint (spec §7.12 宅配 + 失物招领)。

5-27 凌晨新增 — FrontDeskPage 接 backend 用。

端点:
- GET  /api/v1/front-desk?kind=delivery|lost_and_found  — 列指定类型条目
- POST /api/v1/front-desk                                — 老师登记新条目
- POST /api/v1/front-desk/{id}/notify                    — 标记已通知学生
- POST /api/v1/front-desk/{id}/picked-up                 — 标记学生已取走

待 itsuki review:
- expires_in_days 默认 delivery=7 / lost_and_found=30 是否合理
- 学生 NFC 取走自动确认（不用老师手动标）是 v1.1+ 议题
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import dorm_units_for_teacher, get_current_student, get_current_teacher


def _assert_student_in_dorm(teacher: models.Teacher, student: models.Student) -> None:
    """R4 寮边界写操作校验 — 学生 dorm_unit 不在老师管辖范围 → 403。"""
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生への操作はできません",
            },
        )


router = APIRouter(prefix="/api/v1/front-desk", tags=["front-desk"])

# 登记 / 标取走权限 — 寮監 / 寮務 / 管理係
_ADMIN_ROLES = {"寮監", "寮務部長", "寮務課長", "管理係"}

# 默认过期时长
DELIVERY_EXPIRES_DAYS = 7
LOST_AND_FOUND_EXPIRES_DAYS = 30


@router.get("", response_model=list[schemas.FrontDeskItemOut])
def list_items(
    kind: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """列前台条目 — kind 可选过滤 + 按老师管辖男/女寮过滤。"""
    stmt = select(models.FrontDeskItem).order_by(models.FrontDeskItem.created_at.desc())
    if kind:
        if kind not in {"delivery", "lost_and_found"}:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_KIND",
                    "message": "kind 必须是 delivery 或 lost_and_found",
                },
            )
        stmt = stmt.where(models.FrontDeskItem.kind == kind)

    # R4 寮过滤：寮監等管辖男/女寮的老师只看关联学生属于自己男/女寮的条目。
    # itsuki 拍板「按男寮 / 女寮过滤、不细分到楼」—— dorm_units_for_teacher 返回的本就是
    # 男女寮粒度（男寮=[1,2] / 女寮=[4] / 跨寮角色=None=看全部）。
    # 无关联学生的条目（如无主失物 student_id=NULL）对所有老师可见。
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.outerjoin(
            models.Student, models.FrontDeskItem.student_id == models.Student.id
        ).where(
            or_(
                models.FrontDeskItem.student_id.is_(None),
                models.Student.dorm_unit.in_(allowed),
            )
        )
    return [schemas.FrontDeskItemOut.model_validate(r) for r in db.scalars(stmt).all()]


@router.get("/mine", response_model=list[schemas.FrontDeskItemOut])
def list_my_deliveries(
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """学生查自己的宅配（包裹）— iOS 通知中心「荷物」数据源。

    - 只返回 kind='delivery' 且 student_id = 当前学生 的条目
    - 失物招领（lost_and_found）不在此列：那时 student_id 是捡到人、非「我的包裹」语义
    - 不过滤 status：未取走（pending/notified）+ 已取走（picked_up）都返回，
      「哪些算未读 badge」交给 iOS 端按 status 判定（picked_up 视为已读）
    - 按 created_at 倒序（最新包裹在前）
    """
    stmt = (
        select(models.FrontDeskItem)
        .where(
            models.FrontDeskItem.student_id == student.id,
            models.FrontDeskItem.kind == "delivery",
        )
        .order_by(models.FrontDeskItem.created_at.desc())
    )
    return [schemas.FrontDeskItemOut.model_validate(r) for r in db.scalars(stmt).all()]


@router.get("/students", response_model=list[schemas.FrontDeskStudentBrief])
def search_recipients(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """前台登记宅配时挑收件学生用 —— 权限同前台登记(_ADMIN_ROLES，含寮監)，
    按老师管辖男/女寮过滤，只返回挑人需要的最小字段。

    为什么单独建此端点、不复用账号管理的 GET /students：那个端点角色集不含寮監
    （寮監能登记宅配却搜不了学生 → 选择器对寮監直接 403 失效），且会暴露账号锁定 /
    最后登录时间等敏感字段，前台挑人不需要。
    """
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "前台登记需要寮監 / 寮務 / 管理係 权限",
            },
        )
    stmt = select(models.Student).where(models.Student.is_demo.is_(False))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            models.Student.name.like(like)
            | (
                models.Student.grade_code
                + models.Student.class_code
                + models.Student.seat_no
            ).like(like)
        )
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    stmt = stmt.order_by(models.Student.room_no).limit(20)
    return [
        schemas.FrontDeskStudentBrief(
            id=s.id,
            name=s.name,
            room_no=s.room_no,
            student_no=f"{s.grade_code}{s.class_code}{s.seat_no}",
            dorm_unit=s.dorm_unit,
        )
        for s in db.scalars(stmt).all()
    ]


@router.post("", response_model=schemas.FrontDeskItemOut, status_code=201)
def create_item(
    body: schemas.FrontDeskItemCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """老师登记新条目。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "前台登记需要寮監 / 寮務 / 管理係 权限",
            },
        )
    if body.student_id:
        student = db.get(models.Student, body.student_id)
        if not student:
            raise HTTPException(
                status_code=404,
                detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
            )
        # R4 寮边界：有关联学生时校验属本老师管辖寮
        _assert_student_in_dorm(teacher, student)
    days = (
        DELIVERY_EXPIRES_DAYS
        if body.kind == "delivery"
        else LOST_AND_FOUND_EXPIRES_DAYS
    )
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    row = models.FrontDeskItem(
        kind=body.kind,
        student_id=body.student_id,
        description=body.description,
        location=body.location,
        status="pending",
        created_by_teacher_id=teacher.id,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.FrontDeskItemOut.model_validate(row)


@router.post("/{item_id}/notify", response_model=schemas.FrontDeskItemOut)
def notify_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """标记已通知学生 — pending → notified。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "前台操作需要寮監 / 寮務 / 管理係 权限",
            },
        )
    row = db.get(models.FrontDeskItem, item_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "ITEM_NOT_FOUND", "message": "条目不存在"},
        )
    # R4 寮边界：条目关联学生时校验属本老师管辖寮
    if row.student_id:
        student = db.get(models.Student, row.student_id)
        if student:
            _assert_student_in_dorm(teacher, student)
    if row.status != "pending":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "WRONG_STATE",
                "message": f"当前 status={row.status}，只能从 pending 转 notified",
            },
        )
    row.status = "notified"
    row.notified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.FrontDeskItemOut.model_validate(row)


@router.post("/{item_id}/picked-up", response_model=schemas.FrontDeskItemOut)
def mark_picked_up(
    item_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """标记学生已取走 — pending/notified → picked_up。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "前台操作需要寮監 / 寮務 / 管理係 权限",
            },
        )
    row = db.get(models.FrontDeskItem, item_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "ITEM_NOT_FOUND", "message": "条目不存在"},
        )
    # R4 寮边界：条目关联学生时校验属本老师管辖寮
    if row.student_id:
        student = db.get(models.Student, row.student_id)
        if student:
            _assert_student_in_dorm(teacher, student)
    if row.status not in {"pending", "notified"}:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "WRONG_STATE",
                "message": f"当前 status={row.status}，不能转 picked_up",
            },
        )
    row.status = "picked_up"
    row.picked_up_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return schemas.FrontDeskItemOut.model_validate(row)
