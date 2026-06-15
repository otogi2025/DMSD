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
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_not_demo_teacher,
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    require_permission,
)


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

# 默认过期时长
DELIVERY_EXPIRES_DAYS = 7
LOST_AND_FOUND_EXPIRES_DAYS = 30


@router.get("", response_model=list[schemas.FrontDeskItemOut])
def list_items(
    kind: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_FRONTDESK, permissions.VIEW)
    ),
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
    # 总 outerjoin Student：演示隔离（无主条目 student_id=NULL 对所有老师可见；
    # 有主条目按 demo 隔离 — 真老师只看真实学生条目 / 演示老师只看演示学生条目）+ R4 寮过滤叠加。
    allowed = dorm_units_for_teacher(teacher)
    stmt = stmt.outerjoin(
        models.Student, models.FrontDeskItem.student_id == models.Student.id
    ).where(
        or_(
            models.FrontDeskItem.student_id.is_(None),
            demo_scope_for_teacher(teacher),
        )
    )
    if allowed is not None:
        stmt = stmt.where(
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_FRONTDESK, permissions.VIEW)
    ),
):
    """前台登记宅配时挑收件学生用 —— 前台·宅配 V 权限即可，
    按老师管辖男/女寮过滤，只返回挑人需要的最小字段。

    为什么单独建此端点、不复用账号管理的 GET /students：那是「学生账号管理」功能簇，
    会暴露账号锁定 / 最后登录时间等敏感字段，前台挑人不需要、权限级别也不同。
    """
    stmt = select(models.Student).where(demo_scope_for_teacher(teacher))
    if q:
        # E-低-04：转义用户输入里的 LIKE 通配符 % 和 _（与 admin_accounts.py 同款），
        # 否则老师输入含 % 的查询会被当通配符匹配全部（功能性瑕疵，非注入——值已被
        # SQLAlchemy 参数化）。escape='\\' 指定反斜杠为转义字符，先转义反斜杠自身再转义 % 和 _。
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        stmt = stmt.where(
            models.Student.name.like(like, escape="\\")
            | (
                models.Student.grade_code
                + models.Student.class_code
                + models.Student.seat_no
            ).like(like, escape="\\")
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_FRONTDESK, permissions.MANAGE)
    ),
):
    """老师登记新条目。"""
    if body.student_id:
        student = db.get(models.Student, body.student_id)
        if not student:
            raise HTTPException(
                status_code=404,
                detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
            )
        # 演示写隔离：有关联学生时演示老师只能挂演示学生 / 真老师只能挂真实学生
        assert_student_demo_match(teacher, student)
        # R4 寮边界：有关联学生时校验属本老师管辖寮
        _assert_student_in_dorm(teacher, student)
    else:
        # 无主条目（失物招领 student_id 空）无法按学生判 demo，演示老师禁建（否则污染真实老师前台板）→ 403
        assert_not_demo_teacher(teacher)
    days = (
        DELIVERY_EXPIRES_DAYS
        if body.kind == "delivery"
        else LOST_AND_FOUND_EXPIRES_DAYS
    )
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    row = models.FrontDeskItem(
        kind=body.kind,
        student_id=body.student_id,
        # 宅配备注可空 → 缺省存空串（DB 列 NOT NULL）；失物招领 schema 已保证非空。
        description=body.description or "",
        location=body.location,
        item_count=body.item_count,
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_FRONTDESK, permissions.MANAGE)
    ),
):
    """标记已通知学生 — pending → notified。"""
    row = db.get(models.FrontDeskItem, item_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "ITEM_NOT_FOUND", "message": "条目不存在"},
        )
    # 演示写隔离 + R4 寮边界：条目关联学生时校验
    if row.student_id:
        student = db.get(models.Student, row.student_id)
        if student:
            assert_student_demo_match(teacher, student)
            _assert_student_in_dorm(teacher, student)
    else:
        # 无主条目演示老师禁操作（改真实无主条目状态）→ 403
        assert_not_demo_teacher(teacher)
    # 原子条件更新：只有 status 仍是 pending 才转 notified。
    # 防两个老师并发点「已通知」/ 一人点通知一人点取走时都读到 pending、最后一次写覆盖前一次
    # （与 outings.py confirm_outing 对齐的竞态修法）。rowcount != 1 说明已被别的请求改掉 → 409。
    result = db.execute(
        update(models.FrontDeskItem)
        .where(
            models.FrontDeskItem.id == item_id,
            models.FrontDeskItem.status == "pending",
        )
        .values(status="notified", notified_at=datetime.now(timezone.utc))
    )
    if result.rowcount != 1:
        db.rollback()
        # 重新读当前状态拼进提示，便于老师网页判断为何失败
        current = db.get(models.FrontDeskItem, item_id)
        current_status = current.status if current else "unknown"
        raise HTTPException(
            status_code=409,
            detail={
                "code": "WRONG_STATE",
                "message": f"当前 status={current_status}，只能从 pending 转 notified",
            },
        )
    db.commit()
    # commit 后 ORM 对象已 expire，重新读拿转换后的最新状态返回
    row = db.get(models.FrontDeskItem, item_id)
    return schemas.FrontDeskItemOut.model_validate(row)


@router.post("/{item_id}/picked-up", response_model=schemas.FrontDeskItemOut)
def mark_picked_up(
    item_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_FRONTDESK, permissions.MANAGE)
    ),
):
    """标记学生已取走 — pending/notified → picked_up。"""
    row = db.get(models.FrontDeskItem, item_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "ITEM_NOT_FOUND", "message": "条目不存在"},
        )
    # 演示写隔离 + R4 寮边界：条目关联学生时校验
    if row.student_id:
        student = db.get(models.Student, row.student_id)
        if student:
            assert_student_demo_match(teacher, student)
            _assert_student_in_dorm(teacher, student)
    else:
        # 无主条目演示老师禁操作（改真实无主条目状态）→ 403
        assert_not_demo_teacher(teacher)
    # 原子条件更新：只有 status 仍是 pending/notified 才转 picked_up。
    # 防两个老师并发点「已取走」/ 一人点取走一人点通知时都读到旧状态、最后一次写覆盖前一次
    # （与 outings.py confirm_outing 对齐的竞态修法）。rowcount != 1 说明已被别的请求改掉 → 409。
    result = db.execute(
        update(models.FrontDeskItem)
        .where(
            models.FrontDeskItem.id == item_id,
            models.FrontDeskItem.status.in_(["pending", "notified"]),
        )
        .values(status="picked_up", picked_up_at=datetime.now(timezone.utc))
    )
    if result.rowcount != 1:
        db.rollback()
        # 重新读当前状态拼进提示，便于老师网页判断为何失败
        current = db.get(models.FrontDeskItem, item_id)
        current_status = current.status if current else "unknown"
        raise HTTPException(
            status_code=409,
            detail={
                "code": "WRONG_STATE",
                "message": f"当前 status={current_status}，不能转 picked_up",
            },
        )
    db.commit()
    # commit 后 ORM 对象已 expire，重新读拿转换后的最新状态返回
    row = db.get(models.FrontDeskItem, item_id)
    return schemas.FrontDeskItemOut.model_validate(row)
