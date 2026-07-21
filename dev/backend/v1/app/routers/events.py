"""行事予定 endpoint (spec §7.5)。

端点:
- GET  /api/v1/events?from_date=&to_date=  — 列日期范围内行事（老师+学生都可看）
- POST /api/v1/events                       — 役职老师新建
- PATCH /api/v1/events/{id}                 — 役职老师编辑
- DELETE /api/v1/events/{id}                — 役职老师删除

权限: GET 全老师可看 / 增删改限役职（寮務部長 / 寮務課長 / 管理係）
"""

from __future__ import annotations

from datetime import date, datetime, timezone
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

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# 增删改权限 — 役职老师
_EDIT_ROLES = {"寮務部長", "寮務課長", "管理係"}

# 合法 category 值
_VALID_CATEGORIES = {"学校行事", "寮行事", "外部", "その他"}


def _require_edit_role(teacher: models.Teacher) -> None:
    # 演示老师禁增删改全局行事（行事无 is_demo，会污染真实学生看到的日程）→ 403。
    # 权限组判定（行事·活动 = M）已上移到端点的 require_permission 闸；此处只剩演示隔离。
    assert_not_demo_teacher(teacher)


def _check_time_range(start_at: datetime | None, end_at: datetime | None) -> None:
    """开始时刻不能晚于结束时刻。两个都给且倒置时 422。

    只校验 start_at / end_at 两个时刻字段的先后；不强制 event_date 与时刻同日
    （行事可能跨午夜，event_date 表示"挂在哪天显示"，与精确时刻未必同日 — 同日约束属
    产品决策，不在此处兜底）。
    """
    if start_at and end_at and start_at > end_at:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_TIME_RANGE",
                "message": "開始時刻は終了時刻以前にしてください",
            },
        )


@router.get("", response_model=schemas.DormEventListOut)
def list_events(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """列行事予定 — 按日期范围过滤（from_date / to_date 均可选）。学生+老师均可看。"""
    # 范围倒置（from_date > to_date）会静默返回空集，让调用方误以为"该范围真没行事"。
    # 两个边界都给且倒置时直接 422，避免静默吞掉错误的查询参数。
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_DATE_RANGE",
                "message": "開始日は終了日以前にしてください",
            },
        )
    # 演示隔离：按创建者 is_demo 过滤 —— 演示老师 / 演示学生只看演示老师创建的行事，
    # 真实侧只看真实老师创建的（与 student_audience 通知 feed 同口径）。原来列表端点不过滤，
    # 演示账号打开行事页能读到真实运营行事，反之真实学生混入演示数据（TW-012）。
    # created_by_teacher_id 非空（models 约束），inner join 不会漏掉合法行。
    stmt = (
        select(models.DormEvent)
        .join(
            models.Teacher,
            models.Teacher.id == models.DormEvent.created_by_teacher_id,
        )
        .where(models.Teacher.is_demo == _principal.is_demo)
        .order_by(models.DormEvent.event_date)
    )
    if from_date:
        stmt = stmt.where(models.DormEvent.event_date >= from_date)
    if to_date:
        stmt = stmt.where(models.DormEvent.event_date <= to_date)
    rows = db.scalars(stmt).all()
    return schemas.DormEventListOut(
        items=[schemas.DormEventOut.model_validate(r) for r in rows]
    )


@router.post("", response_model=schemas.DormEventOut, status_code=201)
def create_event(
    body: schemas.DormEventCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_EVENT, permissions.MANAGE)
    ),
):
    """役职老师新建行事予定。"""
    _require_edit_role(teacher)
    if body.category not in _VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": f"有効な分類：{'、'.join(sorted(_VALID_CATEGORIES))}",
            },
        )
    _check_time_range(body.start_at, body.end_at)
    row = models.DormEvent(
        title=body.title,
        category=body.category,
        event_date=body.event_date,
        start_at=body.start_at,
        end_at=body.end_at,
        description=body.description,
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
            students=student_audience.students_for_event(db, row),
            title=row.title,
            body=row.description or row.category,
        )
        db.commit()
    return schemas.DormEventOut.model_validate(row)


@router.patch("/{event_id}", response_model=schemas.DormEventOut)
def patch_event(
    event_id: UUID,
    body: schemas.DormEventPatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_EVENT, permissions.MANAGE)
    ),
):
    """役职老师编辑行事予定（部分更新）。"""
    _require_edit_role(teacher)
    row = db.get(models.DormEvent, event_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "EVENT_NOT_FOUND", "message": "行事予定が見つかりません"},
        )
    if body.category is not None and body.category not in _VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": f"有効な分類：{'、'.join(sorted(_VALID_CATEGORIES))}",
            },
        )
    # 用 exclude_unset 区分「字段没传=不动」与「字段显式传 null=清空」（TW-014）。
    # 原来 `if val is not None` 把 null 也跳过，导致老师无法清空可选字段（start_at /
    # end_at / description），把输入框清空保存后旧值仍留着。前端编辑路径会对显式清空
    # 的字段发 null（而非 undefined），后端据 model_fields_set 落实清空。
    provided = body.model_dump(exclude_unset=True)
    # 时刻先后校验也走 provided（codex m1）：用 `body.x is not None` 判会把「显式传 null
    # 清空」误当成「没传」、拿旧值比较，可能错误拒绝一个合法修改（清空 start_at + 改 end_at）。
    # 改用 provided.get(field, 旧值)：传了(含 null)用新值、没传用旧值。
    final_start = provided.get("start_at", row.start_at)
    final_end = provided.get("end_at", row.end_at)
    _check_time_range(final_start, final_end)
    for field in (
        "title",
        "category",
        "event_date",
        "start_at",
        "end_at",
        "description",
        # notify_students 故意不在此 — 编辑路径不碰它（见下方注释，§7.13.1 修订 2026-06-16）
    ):
        if field in provided:
            setattr(row, field, provided[field])
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    # 编辑不碰 notify_students（§7.13.1 修订 2026-06-16 codex 复审）：它是「是否进通知 feed」的持久开关，
    # 编辑默认不勾会把已通知内容移出 feed（数据丢失）/ 保持勾又每次编辑重推全员 → 编辑路径不动该字段，
    # 通知只在「新建」时决定。需重新通知请删后重发。
    return schemas.DormEventOut.model_validate(row)


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_EVENT, permissions.MANAGE)
    ),
):
    """役职老师删除行事予定（物理删除）。"""
    _require_edit_role(teacher)
    row = db.get(models.DormEvent, event_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "EVENT_NOT_FOUND", "message": "行事予定が見つかりません"},
        )
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="event.delete",
            target_type="dorm_events",
            target_id=event_id,
            payload={"title": row.title, "event_date": str(row.event_date)},
        )
    )
    db.delete(row)
    db.commit()
