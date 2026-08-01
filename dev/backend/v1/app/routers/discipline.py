"""扣分 / 規律処分 endpoint (spec §7.5)。

5-27 凌晨新增 — itsuki 设 /goal v1.0 完整体 + 让 CC 替默认决策。本 router 实装 P0
DisciplinePage 接 backend 的核心 endpoint。

包含：
- GET  /api/v1/discipline/ranking?month=YYYY-MM   — 月排名 + 阈值标记
- POST /api/v1/discipline/manual                   — 手动设定本月扣分总分(绝对值) (寮監 / 寮務全员)
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
from sqlalchemy import func, select, update
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
from ..services.student_picker import query_students_for_picker

router = APIRouter(prefix="/api/v1/discipline", tags=["discipline"])

# itsuki 5-22 拍板的扣分阈值（2026-06-15 罚扫重做恢复 4 分阈值）
CLEANING_THRESHOLD = 4.0  # ≥4 分 → 需要罚扫（清扫罚则）
CURFEW_THRESHOLD = 8.0  # ≥8 分 → 外出禁止（禁足）


def current_month_total_points(
    db: Session, student_id: UUID, *, month: str | None = None
) -> float:
    """某学生指定月份（默认 JST 当月）的有效扣分总分。

    口径与 /ranking、/me/summary、手动设定绝对分完全一致：
    同月（DemeritEvent.month == 'YYYY-MM'）+ 排除已撤销（revoked_at IS NULL）。
    月份归属统一用 JST，防跨月凌晨归错月。

    抽成函数是为了让「≥8 分外出禁止」这类阈值判定（routers/outings.py 提交拦截）
    跟排行榜共用同一套算法，不各写一遍 SUM 导致口径漂移。
    """
    if month is None:
        month = datetime.now(_JST).strftime("%Y-%m")
    total = db.scalar(
        select(func.coalesce(func.sum(models.DemeritEvent.points), 0.0)).where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.month == month,
            models.DemeritEvent.revoked_at.is_(None),
        )
    )
    return float(total or 0.0)


@router.get("/ranking", response_model=schemas.DemeritRankingOut)
def get_ranking(
    month: str,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.VIEW)
    ),
):
    """月排名 — month 是 YYYY-MM 字符串。

    R4 寮过滤：走 deps.dorm_units_for_teacher（登录选寮 + 权限组）。
    op / 申請承認専用 组看全部；其他组按令牌 selected_dorm（男→[1,2] / 女→[4]）；
    职位不参与鉴权。
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
        is_cleaning = total >= CLEANING_THRESHOLD
        is_curfew = total >= CURFEW_THRESHOLD
        if is_cleaning:
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
                is_cleaning_threshold=is_cleaning,
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
        # ≥4 分 → 需要罚扫（对称于 8 分外出禁止；到 8 分时 iOS 端按分档优先显示外出禁止）
        needs_cleaning=total_points >= CLEANING_THRESHOLD,
    )


@router.get("/students", response_model=list[schemas.FrontDeskStudentBrief])
def search_students_for_demerit(
    q: str | None = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.VIEW)
    ),
):
    """手动加扣分时挑学生用 —— 扣分管理 V 权限即可。

    为什么单独建此端点、不复用 front-desk 的 GET /students：那个要「前台·宅配」权限，
    但能扣分的老师（寮監 / 寮務）未必有前台权限 —— 权限簇不同，复用会把寮監锁在外面
    （6-14 选学生统一改造 §5 约束2 倾向①：新建权限与扣分对齐的轻量接口）。
    返回字段复用 FrontDeskStudentBrief（挑人最小字段），老师网页 StudentPicker 统一消费。
    同样按老师管辖男/女寮过滤 + 演示隔离。
    """
    # backend#104：查询本体与 front_desk.search_recipients 逐行相同，共用 student_picker
    return query_students_for_picker(db, teacher, q)


@router.post("/manual", response_model=schemas.DemeritEventOut, status_code=201)
def create_manual_demerit(
    body: schemas.DemeritManualIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.MANAGE)
    ),
):
    """手动设定学生本月扣分总分为绝对值（扣分管理 M 权限，B 方案差值记录）。"""
    # 校验学生存在
    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    # 演示写隔离：演示老师只能给演示学生扣分（真老师反之），否则 404
    assert_student_demo_match(teacher, student)
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

    # A-473 幂等防重：客户端带了 idempotency_key 时，先查这名学生是否已有同 key 的手动扣分行，
    # 命中就直接返回那条、不再叠加（老师双击 / 网络重试场景）。
    # 实现复用既有 source_event_id 列 + uq_demerit_source 唯一约束：手动扣分原本该列为空，
    # 这里把客户端生成的 key（UUID）写进去，约束 (student_id, source_type, source_event_id)
    # 就能在 DB 层挡住重复键，无需新增表字段。该列对自动扣分来源各有 source_type 隔离
    # （rollcall_absent / study_absent 等），查询从不跨 source_type 取 manual 行，故不会冲突。
    if body.idempotency_key is not None:
        existing = db.scalars(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == body.student_id,
                models.DemeritEvent.source_type == "manual",
                models.DemeritEvent.source_event_id == body.idempotency_key,
            )
        ).first()
        if existing is not None:
            return schemas.DemeritEventOut.model_validate(existing)

    # BL-6 修复：月份归属用 JST，防跨月凌晨归错月（与 rollcall/study 保持一致）
    now = datetime.now(_JST)
    month = now.strftime("%Y-%m")
    # 并发保护（codex 复审 major）：锁住该学生行，串行化对同一学生的并发「设定绝对分」。
    # 否则两请求可能读到相同 current_total、各算 delta 都插入 → 最终总分 != target_points。
    # SQLite(dev/test) 单写者本就串行、with_for_update 是 no-op；PostgreSQL(prod) 靠行锁串行。
    # 2026-07-17（审查逻-中-5）协议扩展：全部 DemeritEvent 写入方（rollcall 迟到/结算/改判、
    # study 结算/手动修正/撤销、本文件撤销）写前都先锁同一学生行——保证下面「读总分→算差值
    # →写回」期间没有其他扣分写入穿插，设完总分恰等于 target_points。
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == body.student_id)
        .with_for_update()
    )
    # B 方案（手动设定绝对分）：算「目标本月总分 − 当前本月总分」的差值，记一条调整事件。
    # 当前总分口径与 /ranking、/me/summary 完全一致（同月 + 排除已撤销），保证设完后该学生
    # 本月总分恰好等于 target_points。差值可正（加分）可负（降分）；0 = 清零本月扣分。
    current_total = current_month_total_points(db, body.student_id, month=month)
    # 乐观锁：堵住「前端再 GET → POST 到达」之间的空档。行锁只保护 POST 内部；
    # 老师核对时看到的分数随 expected_current_points 传来，锁内不一致则拒绝，
    # 避免自动扣分被「设成旧目标」静默抵消。不传（None）= 老客户端行为不变。
    if (
        body.expected_current_points is not None
        and body.expected_current_points != current_total
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "POINTS_CHANGED",
                "message": (
                    f"点数が変わったため設定を中止しました"
                    f"（期待 {body.expected_current_points} 点 → 実際 {current_total} 点）"
                ),
            },
        )
    delta = body.target_points - current_total
    event = models.DemeritEvent(
        student_id=body.student_id,
        source_type="manual",
        # 带幂等键时把 key 存进 source_event_id 供唯一约束去重；不带时仍为空（原行为）
        source_event_id=body.idempotency_key,
        points=delta,
        reason=body.reason,
        month=month,
        created_by_teacher_id=teacher.id,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        # 并发重复提交：两个相同 key 的请求几乎同时到，先查都没命中、各自 add，
        # 第二个 commit 撞 uq_demerit_source 唯一约束 → 回滚后重查已存行幂等返回（而非 500）。
        db.rollback()
        if body.idempotency_key is not None:
            existing = db.scalars(
                select(models.DemeritEvent).where(
                    models.DemeritEvent.student_id == body.student_id,
                    models.DemeritEvent.source_type == "manual",
                    models.DemeritEvent.source_event_id == body.idempotency_key,
                )
            ).first()
            if existing is not None:
                return schemas.DemeritEventOut.model_validate(existing)
        raise
    db.refresh(event)
    return schemas.DemeritEventOut.model_validate(event)


@router.post("/{event_id}/revoke", response_model=schemas.DemeritEventOut)
def revoke_demerit(
    event_id: UUID,
    body: schemas.DemeritRevokeIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_DEMERIT, permissions.MANAGE)
    ),
):
    """撤销扣分 — 软删除（保留 row + 标 revoked_at）。"""
    event = db.get(models.DemeritEvent, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "減点記録が見つかりません"},
        )
    # R4 寮边界：通过扣分事件找对应学生，寮監只能撤销本寮学生的扣分
    student = db.get(models.Student, event.student_id)
    if student:
        # 演示写隔离：演示老师只能撤销演示学生的扣分（真老师反之），否则 404
        assert_student_demo_match(teacher, student)
        allowed = dorm_units_for_teacher(teacher)
        if allowed is not None and student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の学生への操作はできません",
                },
            )
    # 扣分写入协议（2026-07-17 审查逻-中-5）：撤销（改总分）前先锁该学生行，
    # 与本文件「手动设定绝对分」互斥（SQLite no-op / PG 行锁）。
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == event.student_id)
        .with_for_update()
    )
    # 原子领取撤销权：只有 revoked_at 仍为 NULL 才标记撤销。两老师并发撤销同一扣分时，
    # 后到者命中 0 行 → 409，避免「读到 None 都过 409 守卫」导致下面的清扫单退回联动被
    # 执行两次（TW-029）。照 outings/dorm_life 的 rowcount 守卫做法。
    claimed = db.execute(
        update(models.DemeritEvent)
        .where(
            models.DemeritEvent.id == event_id,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .values(
            revoked_at=datetime.now(timezone.utc),
            revoked_by_teacher_id=teacher.id,
            revoke_reason=body.revoke_reason,
        )
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "ALREADY_REVOKED",
                "message": "この記録は既に取り消し済みです",
            },
        )
    db.refresh(event)
    # 撤销「清扫不通过」扣分要联动退回清扫单状态，否则 CleaningPage 仍显示
    # 「不通过」与已撤销的扣分矛盾。仅 cleaning_failed 有父表回指
    # （rollcall/study 是 forward-only，靠 ranking 过滤 revoked_at）。
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
