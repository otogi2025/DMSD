"""扣分 / 規律処分 endpoint (spec §7.5)。

5-27 凌晨新增 — itsuki 设 /goal v1.0 完整体 + 让 CC 替默认决策。本 router 实装 P0
DisciplinePage 接 backend 的核心 endpoint。

包含：
- GET  /api/v1/discipline/ranking?month=YYYY-MM   — 月排名 + 阈值标记
- POST /api/v1/discipline/manual                   — 手动加扣分 (寮監 / 寮務全员)
- POST /api/v1/discipline/{event_id}/revoke        — 撤销扣分 (寮監 / 寮務全员)

待 itsuki 起床 review:
- ranking 是否要 pagination / 当前一次性返全员
- 阈值 4 / 8 是否硬编码 / 还是 settings table 可调
- 手动加扣分 reason 是否要走预定义模板还是自由文本（当前自由）
- 撤销 24h 内限制是否要加
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_JST = ZoneInfo("Asia/Tokyo")
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import (
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    get_current_teacher,
)

router = APIRouter(prefix="/api/v1/discipline", tags=["discipline"])

# itsuki 5-22 拍板的扣分阈值
CLEANING_THRESHOLD = 4.0
CURFEW_THRESHOLD = 8.0

# 手动加扣分 / 撤销权限 — 跟 cleaning / front_desk 对齐 4 类
# 寮監 + 寮務部長 + 寮務課長 + 管理係
# （学習担当的扣分由 study.py 自动加，不走手动；一般教师 + 国際交流系 不行）
_ADMIN_ROLES = {"寮監", "寮務部長", "寮務課長", "管理係"}


@router.get("/ranking", response_model=schemas.DemeritRankingOut)
def get_ranking(
    month: str,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """月排名 — month 是 YYYY-MM 字符串。

    R4 寮过滤：跨寮役职 (寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長) 看全员，
    其他教师按 assigned_dorm 过滤。
    """
    # month 格式校验 — 错误格式不能静默返回空榜单（否则老师会误以为本月没人扣分）
    try:
        datetime.strptime(month, "%Y-%m")
        if (
            len(month) != 7
        ):  # strptime 会放过 "2026-1"，但 DB 存 "2026-01" 查不到 → 仍误导
            raise ValueError
    except ValueError:
        raise HTTPException(
            422,
            {
                "code": "INVALID_MONTH",
                "message": "month は YYYY-MM 形式で指定してください",
            },
        )
    # 聚合每个学生本月扣分（排除 revoked）
    stmt = (
        select(
            models.DemeritEvent.student_id,
            func.coalesce(func.sum(models.DemeritEvent.points), 0.0).label(
                "total_points"
            ),
        )
        .where(
            models.DemeritEvent.month == month,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .group_by(models.DemeritEvent.student_id)
    )
    rows = db.execute(stmt).all()
    points_by_student: dict[UUID, float] = {r.student_id: r.total_points for r in rows}

    # 拉全员学生（即使本月 0 点也要列出）
    student_stmt = select(models.Student).where(demo_scope_for_teacher(teacher))
    # R4 寮过滤（男寮 1→[1,2] / 女寮 4→[4] / 跨寮 → None 看全部）
    dorm_units = dorm_units_for_teacher(teacher)
    if dorm_units is not None:
        student_stmt = student_stmt.where(models.Student.dorm_unit.in_(dorm_units))
    all_students = db.scalars(student_stmt).all()

    entries: list[schemas.DemeritRankingEntryOut] = []
    cleaning_n = 0
    curfew_n = 0
    for s in all_students:
        total = points_by_student.get(s.id, 0.0)
        is_clean = total >= CLEANING_THRESHOLD
        is_curfew = total >= CURFEW_THRESHOLD
        if is_clean:
            cleaning_n += 1
        if is_curfew:
            curfew_n += 1
        # student_no = grade_code + class_code + seat_no 拼接
        student_no = f"{s.grade_code}{s.class_code}{s.seat_no}"
        entries.append(
            schemas.DemeritRankingEntryOut(
                student_id=s.id,
                student_no=student_no,
                name=s.name,
                room_no=s.room_no,
                dorm_unit=s.dorm_unit,
                total_points=total,
                is_cleaning_threshold=is_clean,
                is_curfew_threshold=is_curfew,
            )
        )
    # 按 total_points 倒序
    entries.sort(key=lambda e: e.total_points, reverse=True)

    return schemas.DemeritRankingOut(
        month=month,
        entries=entries,
        cleaning_threshold_count=cleaning_n,
        curfew_threshold_count=curfew_n,
    )


@router.get("/me/summary", response_model=schemas.MyDisciplineSummaryOut)
def get_my_discipline_summary(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """当前登录学生的当月扣分汇总（iOS 当前用户统计，IX-008b）。

    与 /ranking 同口径：当月（month == 当月 YYYY-MM）+ 排除已撤销。
    late/absent 只数点呼遅刻/欠席（rollcall_late/rollcall_absent）；
    total_points 是当月全部来源之和（跟排行榜 / 阈值判定一致）。
    """
    now = datetime.now(_JST)
    month = now.strftime("%Y-%m")
    events = db.scalars(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == student.id,
            models.DemeritEvent.month == month,
            models.DemeritEvent.revoked_at.is_(None),
        )
    ).all()
    total_points = sum(e.points for e in events)
    late_count = sum(1 for e in events if e.source_type == "rollcall_late")
    absent_count = sum(1 for e in events if e.source_type == "rollcall_absent")
    return schemas.MyDisciplineSummaryOut(
        month=month,
        total_points=total_points,
        late_count=late_count,
        absent_count=absent_count,
    )


@router.post("/manual", response_model=schemas.DemeritEventOut, status_code=201)
def create_manual_demerit(
    body: schemas.DemeritManualIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """手动加扣分（寮監 / 寮務部長 / 寮務課長 / 管理係 权限）。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "手动加扣分需要寮監 / 寮務 / 管理係 权限",
            },
        )
    # 校验学生存在
    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生不存在"},
        )
    # R4 寮边界：寮監是 dorm-scoped 角色，管辖外学生不能手动加扣分
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生への操作はできません",
            },
        )
    # BL-6 修复：月份归属用 JST，防跨月凌晨归错月（与 rollcall/study 保持一致）
    now = datetime.now(_JST)
    event = models.DemeritEvent(
        student_id=body.student_id,
        source_type="manual",
        source_event_id=None,
        points=body.points,
        reason=body.reason,
        month=now.strftime("%Y-%m"),
        created_by_teacher_id=teacher.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return schemas.DemeritEventOut.model_validate(event)


@router.post("/{event_id}/revoke", response_model=schemas.DemeritEventOut)
def revoke_demerit(
    event_id: UUID,
    body: schemas.DemeritRevokeIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """撤销扣分 — 软删除（保留 row + 标 revoked_at）。"""
    if teacher.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "撤销扣分需要寮監 / 寮務 / 管理係 权限",
            },
        )
    event = db.get(models.DemeritEvent, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "扣分事件不存在"},
        )
    # R4 寮边界：通过扣分事件找对应学生，寮監只能撤销本寮学生的扣分
    student = db.get(models.Student, event.student_id)
    if student:
        allowed = dorm_units_for_teacher(teacher)
        if allowed is not None and student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の学生への操作はできません",
                },
            )
    if event.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "ALREADY_REVOKED", "message": "该事件已被撤销"},
        )
    event.revoked_at = datetime.now(timezone.utc)
    event.revoked_by_teacher_id = teacher.id
    event.revoke_reason = body.revoke_reason
    # backend-biz-04 修复：撤销「清扫不通过」扣分要联动退回清扫单状态，
    # 否则 CleaningPage 仍显示「不通过」与已撤销的扣分矛盾。
    # 仅 cleaning_failed 有父表回指（rollcall/study 是 forward-only，靠 ranking 过滤 revoked_at）。
    if event.source_type == "cleaning_failed":
        cleaning = db.scalar(
            select(models.CleaningAssignment).where(
                models.CleaningAssignment.demerit_event_id == event.id
            )
        )
        if cleaning is not None:
            cleaning.status = "assigned"
            cleaning.failure_reason = None
            cleaning.inspected_at = None
            cleaning.inspected_by_teacher_id = None
            cleaning.demerit_event_id = None
    db.commit()
    db.refresh(event)
    return schemas.DemeritEventOut.model_validate(event)
