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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..services import student_audience
from ..deps import (
    assert_not_demo_teacher,
    get_current_principal,
    require_permission,
)

router = APIRouter(prefix="/api/v1/bus/routes", tags=["bus"])

# 增删改权限 — 役职老师
_EDIT_ROLES = {"寮務部長", "寮務課長", "管理係"}

_VALID_KINDS = {"daily_commute", "dorm_special"}
_VALID_VISIBLE_TO = {"all", "dorm_only", "men", "women"}


def _require_edit_role(teacher: models.Teacher) -> None:
    # 演示老师禁增删改全局巴士便（巴士无 is_demo，会污染真实学生看到的班次）→ 403。
    # 权限组判定（巴士路线 = M）已上移到端点的 require_permission 闸；此处只剩演示隔离。
    assert_not_demo_teacher(teacher)


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
    # 演示隔离：按创建者 is_demo 过滤 —— 演示账号只看演示老师创建的巴士便，真实侧只看
    # 真实老师创建的（与 student_audience 通知 feed 同口径）。原列表端点不过滤，演示账号
    # 打开巴士页能读到真实运营班次、反之真实学生混入演示数据（TW-012）。
    stmt = (
        select(models.BusRoute)
        .join(
            models.Teacher,
            models.Teacher.id == models.BusRoute.created_by_teacher_id,
        )
        .where(models.Teacher.is_demo == _principal.is_demo)
        .order_by(models.BusRoute.schedule_at)
    )
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
    # 演示隔离：跨 demo 的便对当前主体隐藏存在性（fail-closed，与 list 同口径）。
    creator = db.get(models.Teacher, row.created_by_teacher_id)
    if creator is None or creator.is_demo != _principal.is_demo:
        raise HTTPException(
            status_code=404,
            detail={"code": "BUS_ROUTE_NOT_FOUND", "message": "巴士便が見つかりません"},
        )
    return schemas.BusRouteOut.model_validate(row)


@router.post("", response_model=schemas.BusRouteOut, status_code=201)
def create_bus_route(
    body: schemas.BusRouteCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_BUS, permissions.MANAGE)
    ),
):
    """役职老师新建巴士便。"""
    _require_edit_role(teacher)
    # kind / name 缺省补全（2026-06-15 表单去掉「種別」「便名」两栏）：
    # 表单不再传 kind → 默认 dorm_special（寮特殊便）；不再传 name → 用 direction 回填。
    kind = body.kind or "dorm_special"
    name = (body.name or "").strip() or body.direction
    if kind not in _VALID_KINDS:
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
        kind=kind,
        name=name,
        direction=body.direction,
        schedule_at=body.schedule_at,
        arrival_at=body.arrival_at,
        visible_to=body.visible_to,
        note=body.note,
        purpose=body.purpose,
        created_by_teacher_id=teacher.id,
        notify_students=body.notify_students,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    # 勾选「学生に通知する」→ 广播推送（feed 靠 notify_students 字段；推送当面 stub）§7.13.1
    if row.notify_students:
        student_audience.broadcast_push(
            db,
            students=student_audience.students_for_bus(db, row),
            title=row.name,
            body=row.direction,
        )
        db.commit()
    return schemas.BusRouteOut.model_validate(row)


@router.patch("/{route_id}", response_model=schemas.BusRouteOut)
def patch_bus_route(
    route_id: UUID,
    body: schemas.BusRoutePatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_BUS, permissions.MANAGE)
    ),
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
    # 用 exclude_unset 区分「字段没传=不动」与「字段显式传 null=清空」（TW-014）。原来
    # `if val is not None` 把 null 也跳过，导致老师无法清空可选字段（arrival_at / note /
    # purpose），输入框清空保存后旧值仍留着。前端编辑路径对显式清空的字段发 null。
    provided = body.model_dump(exclude_unset=True)
    for field in (
        "kind",
        "name",
        "direction",
        "schedule_at",
        "arrival_at",
        "visible_to",
        "note",
        "purpose",
        "deprecated",
        # notify_students 故意不在此 — 编辑路径不碰它（见下方注释，§7.13.1 修订 2026-06-16）
    ):
        if field in provided:
            setattr(row, field, provided[field])
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
                    "purpose",
                    "deprecated",
                )
                if getattr(body, k) is not None
            },
        )
    )
    db.commit()
    db.refresh(row)
    # 编辑不碰 notify_students（§7.13.1 修订 2026-06-16 codex 复审）：它是「是否进通知 feed」的持久开关，
    # 编辑默认不勾会把已通知内容移出 feed（数据丢失）/ 保持勾又每次编辑重推全员 → 编辑路径不动该字段，
    # 通知只在「新建」时决定。需重新通知请删后重发。
    return schemas.BusRouteOut.model_validate(row)


@router.delete("/{route_id}", status_code=204)
def delete_bus_route(
    route_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_BUS, permissions.MANAGE)
    ),
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
