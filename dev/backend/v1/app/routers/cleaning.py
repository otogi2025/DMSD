"""清扫安排 / 罚扫审查 endpoint (spec §7.10)。

2026-06-15 重建 — itsuki 拍板重做清扫罚扫功能。CleaningPage 接 backend 用。

相对 2026-06-10 删除前的旧版两处升级：
- scheduled_date(date) → scheduled_at(带时区 datetime)，排罚扫精确到几点。
- area 老师自由文本（去掉 7 选 1 枚举校验）。
鉴权从旧的按职位（_ADMIN_ROLES）改成当前权限组体系
（require_permission，清扫罚扫归扣分管理簇 C_DEMERIT）。

端点:
- GET  /api/v1/cleaning                  — 列未审核（assigned/done）的清扫安排（老师，C_DEMERIT V）
- GET  /api/v1/cleaning/me               — 学生查自己的清扫履历
- POST /api/v1/cleaning                  — 老师新建清扫分配（C_DEMERIT M）
- POST /api/v1/cleaning/{id}/inspect     — 老师审核（passed / failed 不通过自动扣 2.5 分）
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    require_permission,
)

_JST = ZoneInfo("Asia/Tokyo")

# 不通过自动加的 DemeritEvent points（与旧版一致）
CLEANING_FAILED_POINTS = 2.5

router = APIRouter(prefix="/api/v1/cleaning", tags=["cleaning"])


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


@router.get("", response_model=list[schemas.CleaningAssignmentOut])
def list_cleaning(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.VIEW)
    ),
):
    """列未审核（assigned/done）的清扫安排 — R4 寮过滤 + 演示隔离，按计划时刻升序。

    重做后罚扫带具体时刻（scheduled_at），老师工作流是「看待处理 → 审核」，
    故默认拉未结案项（不再按单日过滤）；已审核（passed/failed/skipped）不在此列。
    """
    # 寮过滤 + 演示隔离下推 SQL：JOIN Student 一次取回已过滤行 + 学生摘要，
    # 避免先全表载入再 Python 端 continue 过滤。
    stmt = (
        select(models.CleaningAssignment, models.Student)
        .join(
            models.Student,
            models.Student.id == models.CleaningAssignment.student_id,
        )
        .where(
            models.CleaningAssignment.status.in_(("assigned", "done")),
            demo_scope_for_teacher(teacher),
        )
        .order_by(models.CleaningAssignment.scheduled_at)
    )
    dorm_units = dorm_units_for_teacher(teacher)
    if dorm_units is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(dorm_units))
    out = []
    for assignment, student in db.execute(stmt).all():
        item = schemas.CleaningAssignmentOut.model_validate(assignment)
        item.student_name = student.name
        item.student_no = student.student_no
        item.room_no = student.room_no
        out.append(item)
    return out


@router.get("/me", response_model=list[schemas.CleaningAssignmentOut])
def list_my_cleaning(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生查自己的清扫罚扫履历（iOS 个人主页「罚扫履历」接真后端）。

    按计划时刻倒序返回本人全部清扫安排（含 assigned / passed / failed）。
    路由 /me 是字面段，放在带 query 的 GET "" 之后不冲突。
    """
    rows = db.scalars(
        select(models.CleaningAssignment)
        .where(models.CleaningAssignment.student_id == student.id)
        .order_by(models.CleaningAssignment.scheduled_at.desc())
    ).all()
    return [schemas.CleaningAssignmentOut.model_validate(r) for r in rows]


@router.post("", response_model=schemas.CleaningAssignmentOut, status_code=201)
def create_cleaning(
    body: schemas.CleaningAssignmentCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.MANAGE)
    ),
):
    """老师新建清扫分配。area 自由文本，scheduled_at 不能排到已过去时间。"""
    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    # R4 寮边界：寮監等寮 scoped 角色不能给管辖外寮学生派清扫
    _assert_student_in_dorm(teacher, student)
    # 演示写隔离：演示老师只能给演示学生派清扫、真老师只能给真实学生
    assert_student_demo_match(teacher, student)

    # 改动 4：不能排到已过去时间。scheduled_at 经 schema 解析后通常为 aware datetime；
    # 万一传进 naive（无时区），按 JST 解读后再与当前 UTC 时刻比较。
    scheduled_at = body.scheduled_at
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=_JST)
    if scheduled_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "SCHEDULED_IN_PAST",
                "message": "過去の時刻には予定できません",
            },
        )

    row = models.CleaningAssignment(
        student_id=body.student_id,
        area=body.area,
        scheduled_at=scheduled_at,
        status="assigned",
        assigned_by_teacher_id=teacher.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.CleaningAssignmentOut.model_validate(row)


@router.post("/{cleaning_id}/inspect", response_model=schemas.CleaningAssignmentOut)
def inspect_cleaning(
    cleaning_id: UUID,
    body: schemas.CleaningInspectIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.MANAGE)
    ),
):
    """老师审核 — passed 通过 / failed 不通过（自动扣 2.5 分）。"""
    row = db.get(models.CleaningAssignment, cleaning_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CLEANING_NOT_FOUND",
                "message": "掃除当番の予定が見つかりません",
            },
        )
    # R4 寮边界 + 演示隔离：审核前确认学生属本老师管辖寮 / demo 一致
    student = db.get(models.Student, row.student_id)
    if student:
        _assert_student_in_dorm(teacher, student)
        assert_student_demo_match(teacher, student)
    # failed 必须带 failure_reason —— 在原子领取前校验，避免领取后才发现参数非法又回滚
    if body.result == "failed" and not body.failure_reason:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MISSING_REASON",
                "message": "不合格の場合は理由を入力してください",
            },
        )

    # 月份归属用 JST（与 discipline.py manual 扣分一致，防跨月凌晨归错月）
    now_jst = datetime.now(_JST)
    # 原子领取审核权：只有还没审核（status 不在 passed/failed/skipped）才能写结果。
    # 防两老师并发审核同一清扫单各写各的结果 —— passed 分支原本无任何唯一约束兜底
    # （仅 failed 靠 uq_demerit_source 撞约束），passed 裸赋值会双写 status / inspected_by。
    claimed = db.execute(
        update(models.CleaningAssignment)
        .where(
            models.CleaningAssignment.id == cleaning_id,
            models.CleaningAssignment.status.not_in(["passed", "failed", "skipped"]),
        )
        .values(
            status=body.result,
            inspected_by_teacher_id=teacher.id,
            inspected_at=datetime.now(timezone.utc),
        )
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "ALREADY_INSPECTED",
                "message": "この予定は既に確認済み、またはスキップ済みです",
            },
        )
    db.refresh(row)

    if body.result == "failed":
        row.failure_reason = body.failure_reason
        # 自动加 DemeritEvent（罚扫不通过扣 2.5 分），存 demerit_event_id 关联，
        # 撤销该扣分时 discipline.revoke 会联动把本清扫单退回 assigned。
        demerit = models.DemeritEvent(
            student_id=row.student_id,
            source_type="cleaning_failed",
            source_event_id=row.id,
            points=CLEANING_FAILED_POINTS,
            reason=f"掃除不合格（{row.area}）：{body.failure_reason}",
            month=now_jst.strftime("%Y-%m"),
            created_by_teacher_id=teacher.id,
        )
        db.add(demerit)
        # 并发兜底：flush 时 INSERT demerit，若两个 failed 审核并发都过了状态检查、
        # 各自建 cleaning_failed 扣分行 → 第二个在此撞 uq_demerit_source 唯一约束
        # （uq_demerit_source 冲突在 flush 这一刻抛，不是 commit；inspect 的数据已校验
        # 合法，此处 flush 的 IntegrityError 只可能是该唯一约束）。回滚后按「已审核」返
        # 409（与串行重复审核同语义），不抛 500。
        try:
            db.flush()  # 拿到 demerit.id；唯一约束冲突在此抛
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ALREADY_INSPECTED",
                    "message": "この予定は既に確認済み、またはスキップ済みです",
                },
            )
        row.demerit_event_id = demerit.id

    db.commit()
    db.refresh(row)
    return schemas.CleaningAssignmentOut.model_validate(row)
