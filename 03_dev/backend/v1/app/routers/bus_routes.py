"""巴士时刻表 endpoint (spec §7.6)。

端点:
- GET  /api/v1/bus/routes               — 列巴士便（老师都可看）
- GET  /api/v1/bus/routes/{id}          — 详情
- POST /api/v1/bus/routes               — 役职老师新建
- PATCH /api/v1/bus/routes/{id}         — 役职老师编辑
- DELETE /api/v1/bus/routes/{id}        — 役职老师删除（标 deprecated）

权限: GET 全老师可看 / 增删改限役职（寮務部長 / 寮務課長 / 管理係）
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import (
    assert_not_demo_teacher,
    get_current_principal,
    get_current_teacher,
)

router = APIRouter(prefix="/api/v1/bus/routes", tags=["bus"])

# 增删改权限 — 役职老师
_EDIT_ROLES = {"寮務部長", "寮務課長", "管理係"}

_VALID_KINDS = {"daily_commute", "dorm_special"}
_VALID_VISIBLE_TO = {"all", "dorm_only", "men", "women"}


def _require_edit_role(teacher: models.Teacher) -> None:
    # 演示老师禁增删改全局巴士便（巴士无 is_demo，会污染真实学生看到的班次）→ 403
    assert_not_demo_teacher(teacher)
    if teacher.role not in _EDIT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "巴士便の増删改には 寮務部長 / 寮務課長 / 管理係 権限が必要です",
            },
        )


@router.get("", response_model=schemas.BusRouteListOut)
def list_bus_routes(
    kind: str | None = None,
    include_deprecated: bool = False,
    db: Session = Depends(get_db),
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """列巴士便 — kind 可选过滤（daily_commute / dorm_special）。学生+老师均可看。
    默认只返回有效便（deprecated=False）。
    """
    stmt = select(models.BusRoute).order_by(models.BusRoute.schedule_at)
    if not include_deprecated:
        stmt = stmt.where(models.BusRoute.deprecated.is_(False))
    if kind:
        if kind not in _VALID_KINDS:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_KIND",
                    "message": "kind 必须是 daily_commute 或 dorm_special",
                },
            )
        stmt = stmt.where(models.BusRoute.kind == kind)
    rows = db.scalars(stmt).all()
    return schemas.BusRouteListOut(
        items=[schemas.BusRouteOut.model_validate(r) for r in rows]
    )


@router.get("/{route_id}", response_model=schemas.BusRouteOut)
def get_bus_route(
    route_id: UUID,
    db: Session = Depends(get_db),
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """取单条巴士便详情。学生+老师均可看。"""
    row = db.get(models.BusRoute, route_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "BUS_ROUTE_NOT_FOUND", "message": "巴士便が見つかりません"},
        )
    return schemas.BusRouteOut.model_validate(row)


@router.post("", response_model=schemas.BusRouteOut, status_code=201)
def create_bus_route(
    body: schemas.BusRouteCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师新建巴士便。"""
    _require_edit_role(teacher)
    if body.kind not in _VALID_KINDS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_KIND",
                "message": "kind 必须是 daily_commute 或 dorm_special",
            },
        )
    if body.visible_to not in _VALID_VISIBLE_TO:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_VISIBLE_TO",
                "message": f"visible_to 必须是 {_VALID_VISIBLE_TO} 之一",
            },
        )
    row = models.BusRoute(
        kind=body.kind,
        name=body.name,
        direction=body.direction,
        schedule_at=body.schedule_at,
        arrival_at=body.arrival_at,
        visible_to=body.visible_to,
        note=body.note,
        created_by_teacher_id=teacher.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.BusRouteOut.model_validate(row)


@router.patch("/{route_id}", response_model=schemas.BusRouteOut)
def patch_bus_route(
    route_id: UUID,
    body: schemas.BusRoutePatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师编辑巴士便（部分更新）。
    A9 审查结论：deprecated 软删可逆 — spec §7.6 无不可逆条款，
    DELETE 只是标 deprecated=True，PATCH 允许役职老师改回 deprecated=False（恢复便）。
    """
    _require_edit_role(teacher)
    row = db.get(models.BusRoute, route_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "BUS_ROUTE_NOT_FOUND", "message": "巴士便が見つかりません"},
        )
    if body.kind is not None and body.kind not in _VALID_KINDS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_KIND",
                "message": "kind 必须是 daily_commute 或 dorm_special",
            },
        )
    if body.visible_to is not None and body.visible_to not in _VALID_VISIBLE_TO:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_VISIBLE_TO",
                "message": f"visible_to 必须是 {_VALID_VISIBLE_TO} 之一",
            },
        )
    for field in (
        "kind",
        "name",
        "direction",
        "schedule_at",
        "arrival_at",
        "visible_to",
        "note",
        "deprecated",
    ):
        val = getattr(body, field)
        if val is not None:
            setattr(row, field, val)
    row.updated_at = datetime.now(timezone.utc)
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="bus_route.patch",
            target_type="bus_routes",
            target_id=route_id,
            payload={
                k: getattr(body, k)
                for k in (
                    "kind",
                    "name",
                    "direction",
                    "visible_to",
                    "note",
                    "deprecated",
                )
                if getattr(body, k) is not None
            },
        )
    )
    db.commit()
    db.refresh(row)
    return schemas.BusRouteOut.model_validate(row)


@router.delete("/{route_id}", status_code=204)
def delete_bus_route(
    route_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """役职老师停用巴士便（标 deprecated=True，不物理删除）。"""
    _require_edit_role(teacher)
    row = db.get(models.BusRoute, route_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "BUS_ROUTE_NOT_FOUND", "message": "巴士便が見つかりません"},
        )
    row.deprecated = True
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
