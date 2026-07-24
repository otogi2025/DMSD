"""点呼 endpoint (#16-#20 点呼 部分).

GET  /api/v1/rollcall/today/sessions              — 当日セッション一覧
GET  /api/v1/rollcall/sessions?from=&to=          — 履歴 (RecordsPage 用)
POST /api/v1/rollcall/sessions/{id}/start         — 手動開始
POST /api/v1/rollcall/sessions/{id}/end           — 手動終了
POST /api/v1/rollcall/sessions/{id}/checkins      — NFC/手動チェックイン
GET  /api/v1/rollcall/sessions/{id}/board         — 全座席現状
GET  /api/v1/rollcall/sessions/{id}/summary       — 総結中層ページ
PATCH /api/v1/rollcall/events/{id}                — 教師改判
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas, ws_manager as _ws
from ..database import get_db
from .. import permissions
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_student,
    require_permission,
)


def _assert_student_in_dorm(teacher: models.Teacher, student: models.Student) -> None:
    """R4 寮边界写操作校验 — 学生 dorm_unit 不在老师管辖范围 → 403。"""
    from fastapi import HTTPException

    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生への操作はできません",
            },
        )


def _assert_session_in_dorm(
    teacher: models.Teacher, session: models.RollCallSession
) -> None:
    """R4 寮边界 — session 的 dorm_unit_set 与老师管辖寮无交集 → 403。

    跨寮角色（helper 返 None）不受限。
    """
    allowed = dorm_units_for_teacher(teacher)
    if allowed is None:
        return
    # session.dorm_unit_set 是 list[int]；只要有任一寮在管辖范围内即可操作
    if not any(d in allowed for d in session.dorm_unit_set):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮のセッションへの操作はできません",
            },
        )


router = APIRouter(prefix="/api/v1/rollcall", tags=["rollcall"])

# spec §7.5 自动扣分点数 — system_features.md §862 冻结决策（2026-04-30）：迟到 0.5 / 缺席 1.0。
# 初始判定与老师改判用同一组值，一个学生迟到永远是 0.5 分、缺席 1.0 分。
# （旧值 late=1.0 / absent=2.0 是违反冻结规格的 drift，2026-05-31 itsuki 指出后改回。）
ROLLCALL_LATE_POINTS = 0.5
ROLLCALL_ABSENT_POINTS = 1.0


def _today_jst() -> date:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _now_jst() -> datetime:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo"))


def _as_jst_aware(value: datetime) -> datetime:
    """SQLite 读回 timezone=True 时可能丢 tzinfo，比较前统一补成 JST。"""
    from zoneinfo import ZoneInfo

    jst = ZoneInfo("Asia/Tokyo")
    if value.tzinfo is None:
        return value.replace(tzinfo=jst)
    return value.astimezone(jst)


def _broadcast_device_session_started(session: models.RollCallSession) -> None:
    """向点呼机通道广播 session_started（Device_Contract §5）。广播是副作用、失败不抛。"""
    _ws.device_manager.broadcast_sync(
        {
            "type": "session_started",
            "data": {
                "session_id": str(session.id),
                "session_type": session.session_type,
                "scheduled_on_time_end_at": _as_jst_aware(
                    session.scheduled_on_time_end_at
                ).isoformat(),
                # 7-17 拍板删 late_end 概念 → 契约 §5 改播 auto_end
                "scheduled_auto_end_at": _as_jst_aware(
                    session.scheduled_auto_end_at
                ).isoformat(),
            },
        }
    )


def _broadcast_device_session_ended(session_id) -> None:
    """向点呼机通道广播 session_ended（Device_Contract §5）。"""
    _ws.device_manager.broadcast_sync(
        {"type": "session_ended", "data": {"session_id": str(session_id)}}
    )


# ---------------------------------------------------------------
# GET /rollcall/today/sessions
# ---------------------------------------------------------------
@router.get("/today/sessions", response_model=list[schemas.RollCallSessionOut])
def today_sessions(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    from zoneinfo import ZoneInfo

    today = _today_jst()
    jst = ZoneInfo("Asia/Tokyo")
    # 当日 0:00:00 JST 起、次日 0:00:00 JST 止（不含）— 无上界会把未来 session 也返回
    day_start = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=jst)
    day_end = day_start + timedelta(days=1)
    stmt = select(models.RollCallSession).where(
        models.RollCallSession.scheduled_window_start_at >= day_start,
        models.RollCallSession.scheduled_window_start_at < day_end,
    )
    # 寮过滤已于 2026-06-13 全局取消（deps.dorm_units_for_teacher 恒返 [1,2,4]）——
    # 原来这里有一段内联寮过滤（硬编码 4 个跨寮角色、且漏了「校長」），与全局取消的决定
    # 冲突且口径不一致，已删除。所有老师看当日全部场次，功能权限仍由 require_permission 把关。
    sessions = db.scalars(stmt).all()
    return [schemas.RollCallSessionOut.model_validate(s) for s in sessions]


# ---------------------------------------------------------------
# GET /rollcall/me/today  — 学生端「今日の自分の点呼」(iOS HomeView / MyPage 用)
# 学生令牌；返回今天「我所属寮」的点呼场次 + 我在每场的签到状态。
# iOS 用四个 scheduled_* 时间窗 + 当前时刻算 idle/进行中/時間内/遅刻，my_status
# 给已签到的真实判定 — 替代原来本地写死的「時間外」「時間内」(R-1/R-2)。
# ---------------------------------------------------------------
@router.get("/me/today", response_model=list[schemas.MyRollCallTodaySession])
def my_today_rollcall(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    from zoneinfo import ZoneInfo

    today = _today_jst()
    jst = ZoneInfo("Asia/Tokyo")
    day_start = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=jst)
    day_end = day_start + timedelta(days=1)
    sessions = db.scalars(
        select(models.RollCallSession)
        .where(
            models.RollCallSession.scheduled_window_start_at >= day_start,
            models.RollCallSession.scheduled_window_start_at < day_end,
        )
        .order_by(models.RollCallSession.scheduled_window_start_at)
    ).all()
    # dorm_unit_set 是 JSON 列（[1,2] 男寮 / [4] 女寮），跨 DB 的 JSON 包含查询不可移植，
    # 故在 Python 侧按学生 dorm_unit 过滤（今日场次量很小，性能无虑）。
    mine = [s for s in sessions if student.dorm_unit in (s.dorm_unit_set or [])]

    # 我在这些场次的签到事件 —— event 是 append-only，同一场次同一学生可能有多条
    # （首次 checkin + 老师 override 改判），所以按 checked_in_at 取最新那条，
    # 口径与 board/summary 的 latest-per-student 一致（不能取「字典最后写入」那条 ——
    # 那取决于查询返回顺序、不保证是最新）。
    events: dict = {}
    session_ids = [s.id for s in mine]
    if session_ids:
        rows = db.scalars(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id.in_(session_ids),
                models.RollCallEvent.student_id == student.id,
            )
        ).all()
        for e in rows:
            cur = events.get(e.session_id)
            if cur is None or (e.checked_in_at, e.id) > (cur.checked_in_at, cur.id):
                events[e.session_id] = e

    out = []
    for s in mine:
        ev = events.get(s.id)
        out.append(
            schemas.MyRollCallTodaySession(
                session_id=s.id,
                session_type=s.session_type,
                day_type=s.day_type,
                session_status=s.session_status,
                scheduled_window_start_at=s.scheduled_window_start_at,
                scheduled_on_time_end_at=s.scheduled_on_time_end_at,
                scheduled_late_end_at=s.scheduled_late_end_at,
                scheduled_auto_end_at=s.scheduled_auto_end_at,
                my_status=ev.base_status if ev else None,
                my_checked_in_at=ev.checked_in_at if ev else None,
            )
        )
    return out


# ---------------------------------------------------------------
# GET /rollcall/sessions?from=&to=  — 历史列表 (教师 Web RecordsPage 用)
# 5-27 新增：从已有 RollCallSession model 派生 SELECT 查询，不需要新 schema。
# 日期范围 from / to 是 YYYY-MM-DD，不指定时默认查过去 7 天（含今天）。
# 寮过滤已于 2026-06-13 全局取消（dorm_units_for_teacher 恒返全集），本端点不再按寮裁剪。
# ---------------------------------------------------------------
@router.get("/sessions", response_model=list[schemas.RollCallSessionHistoryOut])
def list_sessions_history(
    from_: Optional[date] = None,
    to: Optional[date] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    from zoneinfo import ZoneInfo

    jst = ZoneInfo("Asia/Tokyo")
    today = _today_jst()
    # 默认：过去 7 天（含今天）
    if to is None:
        to = today
    if from_ is None:
        from datetime import timedelta

        from_ = to - timedelta(days=7)

    from_dt = datetime(from_.year, from_.month, from_.day, 0, 0, 0, tzinfo=jst)
    to_dt = datetime(to.year, to.month, to.day, 23, 59, 59, tzinfo=jst)

    stmt = (
        select(models.RollCallSession)
        .where(
            models.RollCallSession.scheduled_window_start_at >= from_dt,
            models.RollCallSession.scheduled_window_start_at <= to_dt,
        )
        .order_by(models.RollCallSession.scheduled_window_start_at.desc())
    )
    sessions = db.scalars(stmt).all()

    # 寮过滤已于 2026-06-13 全局取消（deps.dorm_units_for_teacher 恒返 [1,2,4]）——
    # 同 today_sessions：原来这里有一段内联寮过滤（硬编码跨寮角色、漏「校長」），已删除。

    # 各场次出席统计（present/late/absent）—— 一次性取这些场次的全部 event，按 (场次, 学生)
    # 取 latest（与 board/summary 的 (checked_in_at, id) 口径一致）再按场次汇总，避免逐场次
    # N 次查询。RecordsPage 三列统计靠这三个字段；不算则前端恒显「—」（TW-040）。
    session_ids = [s.id for s in sessions]
    counts: dict[UUID, dict[str, int]] = {sid: {} for sid in session_ids}
    if session_ids:
        events = db.scalars(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id.in_(session_ids)
            )
        ).all()
        latest: dict[tuple, models.RollCallEvent] = {}
        for e in events:
            key = (e.session_id, e.student_id)
            cur = latest.get(key)
            if cur is None or (e.checked_in_at, e.id) > (cur.checked_in_at, cur.id):
                latest[key] = e
        # 演示隔离（codex M4）：统计只数与本老师 is_demo 一致的学生，否则演示老师会看到
        # 真实学生的出勤聚合，且历史页数字与 board/summary（两者都按 demo 过滤）对不上。
        # 批量取这些 event 的学生 is_demo（一次 IN 查询，不引 N+1）。
        stu_ids = {stu for (_sess, stu) in latest.keys()}
        demo_map = {
            sid: is_demo
            for sid, is_demo in db.execute(
                select(models.Student.id, models.Student.is_demo).where(
                    models.Student.id.in_(stu_ids)
                )
            ).all()
        }
        for (sid, stu), e in latest.items():
            if demo_map.get(stu) != teacher.is_demo:
                continue
            bucket = counts[sid]
            bucket[e.base_status] = bucket.get(e.base_status, 0) + 1

    result = []
    for s in sessions:
        out = schemas.RollCallSessionHistoryOut.model_validate(s)
        c = counts.get(s.id, {})
        out.present_count = c.get("present", 0)
        out.late_count = c.get("late", 0)
        out.absent_count = c.get("absent", 0)
        result.append(out)
    return result


# ---------------------------------------------------------------
# POST /rollcall/sessions/{id}/start — 手動開始
# ---------------------------------------------------------------
@router.post("/sessions/{session_id}/start", response_model=schemas.RollCallSessionOut)
def start_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    # 演示隔离：演示账号只读点呼，不能操作真实点呼场次（场次无 demo 标记，写会碰真实学生扣分）
    if teacher.is_demo:
        raise HTTPException(
            403,
            {
                "code": "DEMO_READONLY",
                "message": "デモアカウントは点呼を操作できません",
            },
        )
    session = _get_session_or_404(db, session_id)
    now = _now_jst()

    if session.session_status == "running":
        raise HTTPException(
            409, {"code": "ALREADY_RUNNING", "message": "既に開始済みです"}
        )
    if session.session_status == "ended":
        raise HTTPException(
            409, {"code": "ALREADY_ENDED", "message": "終了済みのセッションです"}
        )

    # R4 寮边界：session 的 dorm_unit_set 与老师管辖寮必须有交集
    _assert_session_in_dorm(teacher, session)

    # -5min 前检查 (RollCall_Spec §5.4) — 用 timedelta 算，正确处理跨小时边界
    window_minus5 = _as_jst_aware(session.scheduled_window_start_at) - timedelta(
        minutes=5
    )
    if now < window_minus5:
        raise HTTPException(
            409, {"code": "NOT_YET_ALLOWED", "message": "開始時刻の 5 分前より早いです"}
        )

    # A-503: 过期场次上界校验。原本只校验下界（太早不能开），没有上界 ——
    # 昨天 cron 生成、没人开的 draft 场次今天仍能 start：started_at=今天 now，但判定用
    # scheduled_on_time_end_at（昨天的时刻）→ 今天所有签到一律 now > on_time_end 被记 late，
    # 或 end 时全员未签 → 全员 absent，造成批量误扣分。已过 scheduled_auto_end_at 的场次拒绝开始。
    if now > _as_jst_aware(session.scheduled_auto_end_at):
        raise HTTPException(
            409,
            {
                "code": "SESSION_EXPIRED",
                "message": "終了予定時刻を過ぎたセッションは開始できません",
            },
        )

    # 原子领取：只有 session 仍是 draft 才置 running（带 where session_status=='draft'）。
    # 镜像 end_session —— 防两老师并发点「開始」/ 重复点击：后到者命中 0 行 → 409，
    # 不再二次写 started_* 字段、也不重复广播点呼机。
    claimed = db.execute(
        update(models.RollCallSession)
        .where(
            models.RollCallSession.id == session_id,
            models.RollCallSession.session_status == "draft",
        )
        .values(
            session_status="running",
            started_at=now,
            started_source="teacher",
            started_by=teacher.id,
        )
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409, {"code": "ALREADY_RUNNING", "message": "既に開始済みです"}
        )
    db.refresh(session)
    db.commit()
    # 点呼机通道广播（Device_Contract §5）— 手动开始也通知点呼机进入受理状态
    _broadcast_device_session_started(session)
    return schemas.RollCallSessionOut.model_validate(session)


# ---------------------------------------------------------------
# POST /rollcall/sessions/{id}/end — 手動終了
# ---------------------------------------------------------------
@router.post("/sessions/{session_id}/end", response_model=schemas.RollCallSessionOut)
def end_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    # 演示隔离：演示账号只读点呼，不能操作真实点呼场次（end 会触发 _settle_absent 给真实学生记缺席扣分）
    if teacher.is_demo:
        raise HTTPException(
            403,
            {
                "code": "DEMO_READONLY",
                "message": "デモアカウントは点呼を操作できません",
            },
        )
    session = _get_session_or_404(db, session_id)
    if session.session_status != "running":
        raise HTTPException(
            409,
            {
                "code": "SESSION_NOT_RUNNING",
                "message": "実行中のセッションではありません",
            },
        )

    # R4 寮边界：session 的 dorm_unit_set 与老师管辖寮必须有交集
    _assert_session_in_dorm(teacher, session)

    now = _now_jst()
    # 原子领取：只有 session 仍是 running 才置 ended（带 where session_status=='running'）。
    # 防两老师并发点「点呼結束」/ 重复点击 —— 后到者命中 0 行 → 409，不再二次跑
    # _settle_absent（否则每个缺席学生会被 INSERT 两条 absent 事件行，污染审计/历史回放）。
    claimed = db.execute(
        update(models.RollCallSession)
        .where(
            models.RollCallSession.id == session_id,
            models.RollCallSession.session_status == "running",
        )
        .values(
            session_status="ended",
            ended_at=now,
            ended_source="teacher",
            ended_by=teacher.id,
        )
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "SESSION_NOT_RUNNING",
                "message": "実行中のセッションではありません",
            },
        )
    db.refresh(session)

    # 把未签到的学生结算成 absent（仅 claim 成功的唯一请求才跑结算）
    _settle_absent(db, session)
    db.commit()
    db.refresh(session)
    # 点呼机通道广播（Device_Contract §5）
    _broadcast_device_session_ended(session.id)
    return schemas.RollCallSessionOut.model_validate(session)


# ---------------------------------------------------------------
# POST /rollcall/sessions/{id}/checkins — NFC/手動チェックイン
# ---------------------------------------------------------------
@router.post(
    "/sessions/{session_id}/checkins",
    response_model=schemas.RollCallEventOut,
    status_code=201,
)
def create_checkin(
    session_id: UUID,
    body: schemas.RollCallCheckinIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    session = _get_session_or_404(db, session_id)

    # E-中-08: 学生解析 + 寮/demo 校验必须前置到 session_status 状态门（409）之前。
    # 仿 patch_event（顶部先做 _assert_student_in_dorm + assert_student_demo_match）——
    # 否则管辖外 / 演示老师能靠 409 SESSION_NOT_RUNNING vs 403/404 的返回差异，
    # 对任意 session_id 探测真实场次是否存在 / 是否 running（Codex 5.5 审查同类发现）。
    student: Optional[models.Student] = None

    # A-020 (2026-05-21): path_hint 一致性校验（client 显式标路径时挡假数据）
    if body.path_hint == "A" and not body.card_uid:
        raise HTTPException(
            422,
            {
                "code": "PATH_HINT_MISMATCH",
                "message": "path_hint=A の場合は card_uid が必要です",
            },
        )
    if body.path_hint == "B" and not body.idempotency_key:
        raise HTTPException(
            422,
            {
                "code": "PATH_HINT_MISMATCH",
                "message": "path_hint=B の場合は idempotency_key が必要です",
            },
        )

    if body.card_uid:
        # 路径 A: 用 NfcCard 表按 card_uid 解析学生（镜像 devices.py 设备签到）
        card_uid_norm = body.card_uid.lower()
        active_card = db.scalar(
            select(models.NfcCard).where(
                models.NfcCard.card_uid == card_uid_norm,
                models.NfcCard.revoked_at.is_(None),
            )
        )
        if active_card is not None:
            # 审查 backend#37(终审 minor)：卡命中的学生与老师显式传的 student_id 不一致时，
            # 不静默按卡签（会签错人），要求老师明确二选一。
            if body.student_id and active_card.student_id != body.student_id:
                raise HTTPException(
                    422,
                    {
                        "code": "CARD_STUDENT_MISMATCH",
                        "message": "カードと指定された学生が一致しません",
                    },
                )
            student = db.get(models.Student, active_card.student_id)
        elif body.student_id:
            # 卡表未命中时仍允许老师手传 student_id 代签（兼容未发卡 / 旧前端）
            student = db.get(models.Student, body.student_id)
        else:
            raise HTTPException(
                422,
                {
                    "code": "UNKNOWN_CARD",
                    "message": "カード UID に対応する学生が見つかりません",
                },
            )
    elif body.student_id:
        # 路径 B / 手動
        student = db.get(models.Student, body.student_id)
    else:
        raise HTTPException(
            422,
            {"code": "MISSING_IDENTIFIER", "message": "card_uid か student_id が必要"},
        )

    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # R4 寮边界：寮監等寮 scoped 角色不能给管辖外寮学生签到
    _assert_student_in_dorm(teacher, student)

    # 演示隔离：演示老师只能给演示学生签到、真老师只能给真实学生签到（跨 demo → 404）
    assert_student_demo_match(teacher, student)

    # 审查 backend#38：代签只允许在籍（active）学生；locked/paused/graduated 一律拒。
    # 终审 minor：放在寮/demo 校验之后——否则管辖外/演示老师能靠 422(STUDENT_NOT_ACTIVE)
    # vs 404 的差异探测「某 student_id/card 是真实但已停用学生」（逆 E-中-08 统一 404 防探测）。
    if student.status != "active":
        raise HTTPException(
            422,
            {
                "code": "STUDENT_NOT_ACTIVE",
                "message": "在籍中の学生のみ点呼できます",
            },
        )

    # codex 复审（2026-06-15）：student-session 寮匹配校验。create_rollcall_report 已校验
    # 「学生属于该 session 覆盖的寮」(dorm_unit_set)，但老师代签 create_checkin 漏了同款校验
    # —— 否则老师能把别寮学生签进本场次（dorm_unit_set 不含该生寮），产生错误出勤、扣分挂错
    # 场次。与 create_rollcall_report 口径一致：不属于则 404（不泄露别寮场次细节）。前置到
    # session_status 状态门之前，同 E-中-08 防探测。注：这是数据正确性校验，与 2026-06-13
    # 「取消寮过滤」（查询层老师能看全部寮场次）正交、不冲突。
    if student.dorm_unit not in (session.dorm_unit_set or []):
        raise HTTPException(
            404,
            {"code": "NOT_FOUND", "message": "対象の点呼セッションが見つかりません"},
        )

    # 审查 backend#5：代签与 end_session 结算竞态 —— 先对 session 行加锁再重读状态
    # （复制 patch_event 的 TW-026 模式；PG 行锁 / SQLite 单写者 no-op）。锁持有到
    # commit：end 的原子领取 UPDATE 会被挡住 → 代签先到则结算看得见新事件；end 先到
    # 则这里重读到 ended → 409，不会再出现「出勤事件与缺席扣分同时留下」。
    # 锁放在寮/demo 校验（404/403）之后、状态门之前：探测顺序不变（E-中-08），锁段最短。
    db.execute(
        select(models.RollCallSession.id)
        .where(models.RollCallSession.id == session_id)
        .with_for_update()
    )
    db.refresh(session)

    # 寮/demo 通过后才查 session 状态 —— 探测者拿不到 running/draft 状态信息
    if session.session_status != "running":
        raise HTTPException(
            409,
            {
                "code": "SESSION_NOT_RUNNING",
                "message": "実行中の点呼セッションがありません",
            },
        )

    # rollcall-12 (7-06 拍板 server_now，API_CONVENTIONS §4)：判定时刻恒 = 服务器收到该请求的时刻。
    # 彻底不采纳客户端 ts_local——伪造未来/远古时间都无法绕过迟到扣分（present/late 判定、
    # checked_in_at 落库、WS 广播 checked_at 三处统一喂这个 now）。ts_local 字段仍接收但不参与判定。
    now = _now_jst()

    # A-011 (2026-05-21): 幂等 check 改成「先查 idempotency_key 命中」
    # 1. 如果 client 传了 idempotency_key → 用 (session_id, idempotency_key) 唯一定位
    # 2. 否则 fallback 到原逻辑（同 session + 同 student + 同 source）
    if body.idempotency_key:
        existing = db.scalars(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id == session_id,
                models.RollCallEvent.idempotency_key == body.idempotency_key,
            )
        ).first()
        if existing:
            return schemas.RollCallEventOut.model_validate(existing)

    # fallback: 同 session + 同 student + 同 source（兼容路径 A / manual 无 idempotency_key）
    existing = db.scalars(
        select(models.RollCallEvent).where(
            models.RollCallEvent.session_id == session_id,
            models.RollCallEvent.student_id == student.id,
            models.RollCallEvent.status_source.in_(["auto_nfc", "manual_checkin"]),
        )
    ).first()
    if existing:
        return schemas.RollCallEventOut.model_validate(existing)

    # 時刻判定 (present / late)
    scheduled_on_time_end = _as_jst_aware(session.scheduled_on_time_end_at)
    base_status = "present" if now <= scheduled_on_time_end else "late"

    # 审查 backend#6：status_source 服务端按路径推导，不信客户端 —— 与 path_type 同款
    # 口径（有 card_uid = NFC 签到，其余 = 手动代签）。auto_settle 只能出自 _settle_absent、
    # teacher_override 只能出自 PATCH /events，本接口不接受（schema Literal 已收紧成 422）。
    event = models.RollCallEvent(
        session_id=session_id,
        student_id=student.id,
        path_type="A" if body.card_uid else ("B" if body.idempotency_key else "manual"),
        base_status=base_status,
        status_source="auto_nfc" if body.card_uid else "manual_checkin",
        checked_in_at=now,
        idempotency_key=body.idempotency_key,
        # 审查 backend#37(终审)：存归一化小写 card_uid，与 devices.py 设备路径同口径，
        # 免得将来按 card_uid 关联审计漏掉大写记录。
        card_uid=(body.card_uid.lower() if body.card_uid else None),
    )
    db.add(event)

    # spec §7.5 自动扣分 — late 即扣 0.5 点（§862 冻结值）
    # 老师之后改判走 _apply_override_demerit 按当前状态重算
    if base_status == "late":
        # 扣分写入协议（2026-07-17 审查逻-中-5）：写 DemeritEvent 前先锁学生行，与
        # discipline「手动设定绝对分」互斥（SQLite no-op / PG 行锁），防设分期间穿插写入。
        db.execute(
            select(models.Student.id)
            .where(models.Student.id == student.id)
            .with_for_update()
        )
        db.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="rollcall_late",
                source_event_id=session.id,
                points=ROLLCALL_LATE_POINTS,
                reason=f"点呼遅刻（{session.session_type}）",
                # A-497: month 必须经 _as_jst_aware 再 strftime。SQLite 读回 TZDateTime 可能丢 tzinfo
                # 或带 UTC，直接 strftime 在 JST 月初/月末（如 JST 7-01 00:30 = UTC 6-30 15:30）
                # 会把本月扣分归到上月统计。统一按 JST 取归属月。
                month=_as_jst_aware(session.scheduled_window_start_at).strftime(
                    "%Y-%m"
                ),
                created_by_teacher_id=None,
            )
        )

    try:
        db.commit()
    except IntegrityError:
        # 并发重复提交撞唯一约束 → 回滚后重查已存事件，幂等返回（而非 500）。
        # 两种来源：
        #  - rollcall-05: 路径 B 同 idempotency_key 撞 uq_rce_idempotency
        #  - uq_demerit_source: 同一学生本场迟到扣分被并发首签各插一条 → 第二条撞约束
        # 两种都意味着「这名学生本场已有一条有效签到事件」，重查它返回即可。
        db.rollback()
        if body.idempotency_key:
            existing = db.scalars(
                select(models.RollCallEvent).where(
                    models.RollCallEvent.session_id == session_id,
                    models.RollCallEvent.idempotency_key == body.idempotency_key,
                )
            ).first()
            if existing:
                return schemas.RollCallEventOut.model_validate(existing)
        # 无 idempotency_key（路径 A / manual）的并发首签：按 session + student + source 重查
        existing = db.scalars(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id == session_id,
                models.RollCallEvent.student_id == student.id,
                models.RollCallEvent.status_source.in_(["auto_nfc", "manual_checkin"]),
            )
        ).first()
        if existing:
            return schemas.RollCallEventOut.model_validate(existing)
        raise
    db.refresh(event)

    # WS broadcast — 只推给管辖该学生所在寮的老师连接
    _ws.manager.broadcast_sync(
        {
            "type": "checkin",
            "session_id": str(session_id),
            "student_id": str(student.id),
            "status": base_status,
            "checked_at": now.isoformat(),
            "name": student.name,
            "room_no": student.room_no,
        },
        dorm_unit=student.dorm_unit,
        student_is_demo=student.is_demo,
    )

    return schemas.RollCallEventOut.model_validate(event)


# ---------------------------------------------------------------
# GET /rollcall/sessions/{id}/board — 全座席現状
# ---------------------------------------------------------------
@router.get("/sessions/{session_id}/board", response_model=schemas.RollCallBoardOut)
def session_board(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    session = _get_session_or_404(db, session_id)

    # このセッション対象の学生 (R4: dorm_unit_set で絞る)
    # 演示隔离：真老师看真实学生板 / 演示老师看演示学生板（reviewer/体验账号据此分流）
    students = db.scalars(
        select(models.Student).where(
            models.Student.dorm_unit.in_(session.dorm_unit_set),
            models.Student.status == "active",
            demo_scope_for_teacher(teacher),
        )
    ).all()

    # 最新 event を学生ごとに取る
    events = db.scalars(
        select(models.RollCallEvent).where(
            models.RollCallEvent.session_id == session_id
        )
    ).all()
    # B-低-26: latest-per-student 加 id 次级键兜底。checked_in_at 毫秒级相同（如同时刻两次改判）
    # 时仅比时间结果不确定；用 (checked_in_at, id) 元组比较，与 patch_event 的 order_by 口径一致。
    event_map: dict[UUID, models.RollCallEvent] = {}
    for e in events:
        cur = event_map.get(e.student_id)
        if cur is None or (e.checked_in_at, e.id) > (cur.checked_in_at, cur.id):
            event_map[e.student_id] = e

    # 杭田 2026-06-04 三-3/5: 出寮願（承認済 + 期间内）的学生在 live 板上先标 exempt_range，
    # 让寮監一眼看到「今天有出寮願、不用管」，不必等点呼結束自动结算才显示。
    # 出寮願口径与 _settle_absent 的 outstay_ids 保持一致。
    session_date = _as_jst_aware(session.scheduled_window_start_at).date()
    outstay_ids = set(
        db.scalars(
            select(models.Application.student_id).where(
                models.Application.student_id.in_([s.id for s in students]),
                models.Application.status == "approved",
                models.Application.leave_date <= session_date,
                models.Application.return_date >= session_date,
            )
        ).all()
    )

    entries: list[schemas.RollCallBoardEntryOut] = []
    summary: dict[str, int] = {
        "present": 0,
        "late": 0,
        "absent": 0,
        "init": 0,
        "exempt_range": 0,
    }
    for s in students:
        e = event_map.get(s.id)
        if e:
            st = e.base_status
        elif s.id in outstay_ids:
            st = "exempt_range"  # 有 approved 出寮願、还没点呼 event → 先标免除
        else:
            st = "init"
        summary[st] = summary.get(st, 0) + 1
        entries.append(
            schemas.RollCallBoardEntryOut(
                student_id=s.id,
                student_no=s.student_no,
                name=s.name,
                room_no=s.room_no,
                base_status=st,
                checked_in_at=e.checked_in_at if e else None,
                last_event_id=e.id if e else None,
            )
        )

    return schemas.RollCallBoardOut(
        session_id=session_id,
        session_status=session.session_status,
        entries=entries,
        summary=summary,
    )


# ---------------------------------------------------------------
# GET /rollcall/sessions/{id}/summary — 総結中層ページ (#5.5.5)
# ---------------------------------------------------------------
@router.get("/sessions/{session_id}/summary", response_model=schemas.RollCallSummaryOut)
def session_summary(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    session = _get_session_or_404(db, session_id)
    today = _today_jst()

    events = db.scalars(
        select(models.RollCallEvent)
        .where(models.RollCallEvent.session_id == session_id)
        .options(selectinload(models.RollCallEvent.session))
    ).all()

    # latest per student（B-低-26: 加 id 次级键，毫秒级相同时间也确定取同一行，与 board/patch_event 一致）
    event_map: dict[UUID, models.RollCallEvent] = {}
    for e in events:
        cur = event_map.get(e.student_id)
        if cur is None or (e.checked_in_at, e.id) > (cur.checked_in_at, cur.id):
            event_map[e.student_id] = e

    absent: list[dict] = []
    late: list[dict] = []
    exempt_outstay: list[dict] = []

    # 一次性批量取学生（照 session_board 的写法），避免在 event_map 循环里逐个 db.get
    # 造成 N+1 查询 —— 整寮场次 event_map 可达上百条，逐条查库会拖慢点呼总结页。
    student_map = {
        s.id: s
        for s in db.scalars(
            select(models.Student).where(models.Student.id.in_(list(event_map.keys())))
        ).all()
    }

    for sid, e in event_map.items():
        s = student_map.get(sid)
        if not s:
            continue
        # 演示隔离：跳过跨 demo 学生（演示老师只看演示学生摘要 / 真老师只看真实学生）
        if s.is_demo != teacher.is_demo:
            continue
        entry = {"student_id": str(sid), "name": s.name, "room_no": s.room_no}
        if e.base_status == "absent":
            absent.append(entry)
        elif e.base_status == "late":
            late.append(entry)
        elif e.base_status == "exempt_range":
            exempt_outstay.append(entry)

    return schemas.RollCallSummaryOut(
        session_id=session_id,
        absent=absent,
        late=late,
        health_issue=[],  # P2: 体調不良タグ実装後
        exempted_outstay=exempt_outstay,
    )


# ---------------------------------------------------------------
# spec §11.4 改判扣分联动 + spec §7.5/§862 各状态自动扣分点数
#   迟到 0.5 / 缺席 1.0 / present 与 exempt_range = 0（冻结决策 2026-04-30）
#   改判一律「重算到当前状态对应的分」，不做 delta 增减 —— 多步改判才不会算错。
# ---------------------------------------------------------------
_STATUS_DEMERIT: dict[str, tuple[float, str]] = {
    "late": (ROLLCALL_LATE_POINTS, "rollcall_late"),
    "absent": (ROLLCALL_ABSENT_POINTS, "rollcall_absent"),
}


def _apply_override_demerit(
    db: Session,
    student_id: UUID,
    session: models.RollCallSession,
    from_status: str,
    to_status: str,
    teacher_id: UUID,
) -> None:
    """改判扣分联动 — 把该生本场自动扣分「重算到当前状态对应的分」。

    做法：撤掉本场该生所有非目标类型的自动扣分（rollcall_late / rollcall_absent），
    再按 to_status 重记一条（present / exempt_range 不扣分）。
    老师反复改判（如 present→absent→late）也不会累积或算错 ——
    最终扣分永远等于当前状态该扣的分（迟到 0.5 / 缺席 1.0）。
    （旧实现按 delta 增减、负 delta 把整条旧扣分全撤，多步改判会算错 ——
    Codex 5.5 审查发现 + 2026-05-31 itsuki 确认按当前状态重算。）

    与 uq_demerit_source 唯一约束（student_id + source_type + source_event_id）配合：
    同一 (学生, 类型, 场次) 在 DB 层最多 1 行。旧实现「撤旧行 + 永远 INSERT 新行」会在
    改判轨迹回到旧类型时（present→late→present→late）撞约束（被撤的旧 late 行还在、
    再 INSERT 同键 late 行 500）。改为「按 source_event_id + source_type 精确定位既有行，
    有则原地复活/更新、无则 INSERT」，既消除 500、又天然不重复扣分。
    """
    from datetime import datetime as _dt
    from datetime import timezone as _tz

    now_utc = _dt.now(_tz.utc)
    # A-497: month 经 _as_jst_aware 再 strftime，避免 JST 月初/月末把扣分归错月（见 create_checkin 同处注释）
    month = _as_jst_aware(session.scheduled_window_start_at).strftime("%Y-%m")

    # 扣分写入协议（2026-07-17 审查逻-中-5）：写/撤 DemeritEvent 前先锁学生行，
    # 与 discipline「手动设定绝对分」互斥（SQLite no-op / PG 行锁）。
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == student_id)
        .with_for_update()
    )

    # 本场该生的全部自动扣分行（含已撤销的 —— 唯一约束不区分 revoked，必须连撤销行一起取，
    # 否则后面 INSERT 同键会撞约束）。按 source_type 索引、最多两类各一行。
    rows = db.scalars(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.source_event_id == session.id,
            models.DemeritEvent.source_type.in_(["rollcall_late", "rollcall_absent"]),
        )
    ).all()
    by_type = {ev.source_type: ev for ev in rows}

    target = _STATUS_DEMERIT.get(to_status)  # None = present / exempt_range，不扣分
    target_type = target[1] if target is not None else None

    # 1. 撤掉所有「非目标类型」且当前未撤销的扣分
    for ev in rows:
        if ev.source_type != target_type and ev.revoked_at is None:
            ev.revoked_at = now_utc
            ev.revoked_by_teacher_id = teacher_id
            ev.revoke_reason = f"教師改判 {from_status} → {to_status} 重算"

    # 2. 目标类型：既有行原地复活/更新（避免撞唯一约束），无既有行才 INSERT
    if target is not None:
        points, source_type = target
        existing = by_type.get(source_type)
        if existing is None:
            # 无既有行 → INSERT。SAVEPOINT 兜并发：两个老师同时首次改判同一生同场，
            # 都查无各自 INSERT，第二个撞 uq_demerit_source → 重查另一请求刚建的行、落到下面
            # 更新分支复活/改值，避免裸 500、也不漏改判。
            try:
                with db.begin_nested():
                    db.add(
                        models.DemeritEvent(
                            student_id=student_id,
                            source_type=source_type,
                            source_event_id=session.id,
                            points=points,
                            reason=f"教師改判 → {to_status}（spec §11.4 重算）",
                            month=month,
                            created_by_teacher_id=teacher_id,
                        )
                    )
                    db.flush()
            except IntegrityError as err:
                # 审查 backend#36：只吞 uq_demerit_source 唯一约束冲突（并发首次改判撞车）；
                # 外键 / NOT NULL 等其它完整性错误原样抛出，避免扣分没写成却继续提交改判。
                # 跨方言匹配：PostgreSQL 报约束名；SQLite 报 UNIQUE constraint failed + 列名。
                msg = str(getattr(err, "orig", err)).lower()
                if "uq_demerit_source" not in msg and not (
                    "unique" in msg
                    and "source_type" in msg
                    and "source_event_id" in msg
                ):
                    raise
                existing = db.scalar(
                    select(models.DemeritEvent).where(
                        models.DemeritEvent.student_id == student_id,
                        models.DemeritEvent.source_type == source_type,
                        models.DemeritEvent.source_event_id == session.id,
                    )
                )
        if existing is not None:
            existing.points = points
            existing.reason = f"教師改判 → {to_status}（spec §11.4 重算）"
            existing.month = month
            existing.created_by_teacher_id = teacher_id
            existing.revoked_at = None
            existing.revoked_by_teacher_id = None
            existing.revoke_reason = None


# ---------------------------------------------------------------
# PATCH /rollcall/events/{id} — 教師改判 (RollCall_Spec §11 + §11.4)
# ---------------------------------------------------------------
@router.patch("/events/{event_id}", response_model=schemas.RollCallEventOut)
def patch_event(
    event_id: UUID,
    body: schemas.RollCallEventPatch,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    event = db.get(models.RollCallEvent, event_id)
    if not event:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "点呼イベントが見つかりません"}
        )

    # R4 寮边界：改判前先确认该学生属本老师管辖寮（放在一切业务判定之前）
    student = db.get(models.Student, event.student_id)
    # fail-closed：student 行被删 / student_id 悬空时无法判 demo / 寮归属，直接 404，
    # 不再跳过校验继续改判 + 扣分（与 study_online.decide_online_request 口径一致；
    # 原 `if student:` 是 fail-open，悬空脏数据下演示老师可对真实记录改判 + 扣分）。
    if student is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )
    _assert_student_in_dorm(teacher, student)
    # 演示隔离：演示老师只能改判演示学生、真老师只能改判真实学生（跨 demo → 404）
    assert_student_demo_match(teacher, student)

    session = db.get(models.RollCallSession, event.session_id)
    # 行锁串行化（TW-026 + codex M2）：先锁 session 行再操作，与 end_session 结算互斥——
    # 改判与结算并发时保证「读最新状态 → 判 no-op → 追加 override 行 + 扣分联动」整段
    # 在锁内串行、不交错。PostgreSQL（生产）靠行锁；SQLite（dev/test）单写者天然串行 no-op。
    # 原「ended → 409 SESSION_ENDED 终态门」2026-07-17 拍板③删除：改判无时限（含结束后、
    # 月结后），reason 必填 + append-only 不变（RollCall_Spec §11.3 改写）。
    if session is not None:
        db.execute(
            select(models.RollCallSession.id)
            .where(models.RollCallSession.id == event.session_id)
            .with_for_update()
        )
        db.refresh(session)

    # 改判起点用该学生在本场次的「当前最新状态」，不是被 PATCH 那条 event 的 base_status。
    # event 是 append-only，旧行 base_status 永不变，直接用它会让重复 PATCH 同一条旧 event
    # 反复累积扣分、no-op 门也挡不住（Codex 5.5 审查发现）。
    # 口径与 board/summary 的 latest-per-student 一致：取 checked_in_at 最大那条。
    # B-低-26: 排序加 id 次级键。若同一场次毫秒级连续两次改判 checked_in_at 相同，
    # 仅按 checked_in_at 排 .first() 取谁不确定（latest 计算非确定性）。加 id.desc()
    # 兜底保证返回行确定（id 是随机 UUID 非单调，无法判定真正最新，但消除不确定性，
    # 让 patch_event / board / summary 对同一数据始终取同一行）。
    latest_event = db.scalars(
        select(models.RollCallEvent)
        .where(
            models.RollCallEvent.session_id == event.session_id,
            models.RollCallEvent.student_id == event.student_id,
        )
        .order_by(
            models.RollCallEvent.checked_in_at.desc(),
            models.RollCallEvent.id.desc(),
        )
    ).first()
    old_status = latest_event.base_status if latest_event else event.base_status
    new_status = body.to_status

    # no-op 守卫：与当前最新状态相同的改判不允许（防误操作 / 重复 PATCH 刷扣分）
    if old_status == new_status:
        raise HTTPException(
            409,
            {
                "code": "NO_OP_OVERRIDE",
                "message": "現在と同じ状態への改判はできません",
            },
        )

    # append-only：不改既存行，追加一条新的 override 行
    override_event = models.RollCallEvent(
        session_id=event.session_id,
        student_id=event.student_id,
        path_type="manual",
        base_status=new_status,
        status_source="teacher_override",
        checked_in_at=_now_jst(),
        reason=body.reason,
    )
    db.add(override_event)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="rollcall.override",
            target_type="rollcall_event",
            target_id=event_id,
            payload={
                "from": old_status,
                "to": new_status,
                "reason": body.reason,
                "evidence": body.evidence,
            },
        )
    )

    # spec §11.4 改判扣分联动（session 已在函数顶部取出；old_status != new_status 已由 no-op 守卫保证）
    if session is not None:
        _apply_override_demerit(
            db, event.student_id, session, old_status, new_status, teacher.id
        )

    db.commit()
    db.refresh(override_event)

    # WS broadcast — 只推给管辖该学生所在寮的老师连接
    _ws.manager.broadcast_sync(
        {
            "type": "override",
            "session_id": str(event.session_id),
            "student_id": str(event.student_id),
            "status": new_status,
            "from_status": old_status,
            "override_reason": body.reason,
        },
        dorm_unit=student.dorm_unit,
        student_is_demo=student.is_demo,
    )

    return schemas.RollCallEventOut.model_validate(override_event)


# ---------------------------------------------------------------
# 点呼时学生上报（体调 / 当次缺席 / 其他问题）— IX iOS 点呼弹窗接真后端
# ---------------------------------------------------------------
@router.post("/reports", response_model=schemas.RollCallReportOut, status_code=201)
def create_rollcall_report(
    body: schemas.RollCallReportCreateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生点呼上报 — 体调不适 / 当次缺席 / 其他问题（iOS 点呼界面三弹窗）。

    身份从登录令牌取（不信任客户端传 student_id）。
    传了 session_id 就校验该点呼场次：存在 + 覆盖本学生所属寮 + 正在进行中。
    """
    if body.session_id is not None:
        session = db.get(models.RollCallSession, body.session_id)
        # F-中-13: 原本只校验场次存在，学生可对任意已知 session_id（含别寮 / 已结束 / 未来场次）
        # 上报，造成数据噪声。现要求：① 场次覆盖本学生所属寮 ② 场次进行中（running）。
        # 别寮场次与不存在一律返 404 —— 不泄露别寮场次的存在。
        if session is None or student.dorm_unit not in (session.dorm_unit_set or []):
            raise HTTPException(
                404,
                {
                    "code": "SESSION_NOT_FOUND",
                    "message": "点呼セッションが見つかりません",
                },
            )
        if session.session_status != "running":
            raise HTTPException(
                409,
                {
                    "code": "SESSION_NOT_RUNNING",
                    "message": "実行中の点呼セッションではありません",
                },
            )
    report = models.RollCallReport(
        student_id=student.id,
        session_id=body.session_id,
        kind=body.kind,
        body=body.body,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return schemas.RollCallReportOut.model_validate(report)


@router.get("/reports/mine", response_model=list[schemas.RollCallReportOut])
def list_my_rollcall_reports(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生查自己提交过的点呼上报（按时间倒序）。"""
    rows = db.scalars(
        select(models.RollCallReport)
        .where(models.RollCallReport.student_id == student.id)
        .order_by(models.RollCallReport.created_at.desc())
    ).all()
    return [schemas.RollCallReportOut.model_validate(r) for r in rows]


@router.get("/reports", response_model=list[schemas.RollCallReportOut])
def list_rollcall_reports(
    only_unresolved: bool = False,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    """老师查学生点呼上报列表 — R4 寮过滤，可只看未处理。

    只看本人管辖寮学生的上报（跨寮役职看全部）。
    only_unresolved=True 只返回还没标处理的。
    """
    # R4 寮过滤（男寮 1→[1,2] / 女寮 4→[4] / 跨寮 → None 看全部）
    # + 演示隔离：真老师只看真实学生上报 / 演示老师只看演示学生上报
    # （原先跨寮 dorm_units=None 时完全不过滤，演示学生上报会漏进真老师列表 — 一并修掉）。
    # join Student：既做 demo/寮过滤，又顺手取姓名/学号/房号填进返回（老师认得出「谁上报了
    # 体调不适」再处理）。inner join 天然排除 student 悬空的孤儿上报，等价原 allowed_student_ids。
    stmt = (
        select(models.RollCallReport, models.Student)
        .join(
            models.Student,
            models.RollCallReport.student_id == models.Student.id,
        )
        .where(demo_scope_for_teacher(teacher))
        .order_by(models.RollCallReport.created_at.desc())
    )
    if only_unresolved:
        stmt = stmt.where(models.RollCallReport.resolved_at.is_(None))
    dorm_units = dorm_units_for_teacher(teacher)
    if dorm_units is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(dorm_units))
    out = []
    for report, student in db.execute(stmt).all():
        item = schemas.RollCallReportOut.model_validate(report)
        item.student_name = student.name
        item.student_no = student.student_no
        item.room_no = student.room_no
        out.append(item)
    return out


@router.patch("/reports/{report_id}/resolve", response_model=schemas.RollCallReportOut)
def resolve_rollcall_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """老师标记某条点呼上报为已处理 — R4 寮边界，重复处理返 409。"""
    report = db.get(models.RollCallReport, report_id)
    if not report:
        raise HTTPException(
            404, {"code": "REPORT_NOT_FOUND", "message": "報告が見つかりません"}
        )
    # R4 寮边界：通过上报学生校验老师管辖寮
    student = db.get(models.Student, report.student_id)
    # fail-closed：student 行被删 / student_id 悬空时无法判 demo / 寮归属，直接 404，
    # 不再跳过校验继续标记已处理（镜像 patch_event 同口径）。
    if student is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )
    _assert_student_in_dorm(teacher, student)
    # 演示隔离：演示老师只能处理演示学生上报、真老师只能处理真实学生上报（跨 demo → 404）
    assert_student_demo_match(teacher, student)
    if report.resolved_at is not None:
        raise HTTPException(
            409, {"code": "ALREADY_RESOLVED", "message": "この報告は既に処理済みです"}
        )
    report.resolved_at = _now_jst()
    report.resolved_by_teacher_id = teacher.id
    db.commit()
    db.refresh(report)
    return schemas.RollCallReportOut.model_validate(report)


# ---------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------
def _get_session_or_404(db: Session, session_id: UUID) -> models.RollCallSession:
    session = db.get(models.RollCallSession, session_id)
    if not session:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "セッションが見つかりません"}
        )
    return session


def _settle_absent(db: Session, session: models.RollCallSession) -> None:
    """セッション終了時 — チェックインなし学生を absent に記録。"""
    # is_demo 学生排除 — reviewer / 体验账号不算出席率
    students = db.scalars(
        select(models.Student).where(
            models.Student.dorm_unit.in_(session.dorm_unit_set),
            models.Student.status == "active",
            models.Student.is_demo.is_(False),
        )
    ).all()

    checked_ids = set(
        db.scalars(
            select(models.RollCallEvent.student_id).where(
                models.RollCallEvent.session_id == session.id,
                models.RollCallEvent.base_status.in_(
                    ["present", "late", "exempt_range"]
                ),
            )
        ).all()
    )

    # BL-3 修复：结算前查出当天有批准外宿/出寮届的学生，跳过不扣分
    # 参照 study.py:96-105 的 outstay_ids 写法保持口径一致
    session_date = _as_jst_aware(session.scheduled_window_start_at).date()
    student_ids = [s.id for s in students]
    outstay_ids = set(
        db.scalars(
            select(models.Application.student_id).where(
                models.Application.student_id.in_(student_ids),
                models.Application.status == "approved",
                models.Application.leave_date <= session_date,
                models.Application.return_date >= session_date,
            )
        ).all()
    )

    # 不变量（辩论裁决 2026-07-20）：_settle_absent 全库只有两个触发点 ——
    # end_session（原子领取 UPDATE where running）与 scheduler 自动 end（同款领取），
    # running→ended 只能领取成功一次，故同一场次结算只会跑一遍；auto_settle 行
    # 「每生每场至多一条」由这个结构保证，不额外上唯一索引。
    #
    # A-497: month 经 _as_jst_aware 再 strftime，避免 JST 月初/月末把缺席扣分归错月
    month = _as_jst_aware(session.scheduled_window_start_at).strftime("%Y-%m")
    for s in students:
        if s.id not in checked_ids:
            # 审查 backend#4/#5 族（Q2 配套）：checked_ids 是循环前的陈旧快照，设备
            # 签到可能在快照之后已提交（设备路径先持学生行锁再写入）。所以两个分支
            # 统一「先锁该生行 → 锁内重查该生已有出席/免点行 → 有则跳过」。
            # 这个锁同时是扣分写入协议（2026-07-17 审查逻-中-5）要求的学生行锁，
            # 与 discipline「手动设定绝对分」互斥（SQLite no-op / PG 行锁）。
            db.execute(
                select(models.Student.id)
                .where(models.Student.id == s.id)
                .with_for_update()
            )
            fresh = db.scalars(
                select(models.RollCallEvent.id).where(
                    models.RollCallEvent.session_id == session.id,
                    models.RollCallEvent.student_id == s.id,
                    models.RollCallEvent.base_status.in_(
                        ["present", "late", "exempt_range"]
                    ),
                )
            ).first()
            if fresh is not None:
                continue
            # BL-3：外宿/出寮届承认期间的学生打 exempt_range，不算缺席不扣分
            if s.id in outstay_ids:
                db.add(
                    models.RollCallEvent(
                        session_id=session.id,
                        student_id=s.id,
                        path_type="manual",
                        base_status="exempt_range",
                        status_source="auto_settle",
                        checked_in_at=_now_jst(),
                    )
                )
                continue
            # spec §7.5 缺席自动扣 1 点（§862 冻结值）；改判走 _apply_override_demerit 按当前状态重算。
            #
            # 竞态防线两层：主防线 = 上面「学生行锁内重查」（并发 checkin 已提交则跳过）；
            # 兜底 = uq_demerit_source 唯一约束（student_id + source_type + source_event_id），
            # 同一 (学生, rollcall_absent, 本场次) 只能存在 1 条扣分，撞约束走 SAVEPOINT。
            #
            # 用 SAVEPOINT（begin_nested）把「这名学生的 absent event + 扣分」包成一个嵌套事务：
            # 撞约束时只回滚这名学生这一步，不波及外层（session 状态已置 ended、前面已结算的学生）。
            # 若直接 db.rollback() 会回滚整个会话事务、把 session.session_status='ended' 和之前
            # 学生的结算全冲掉 —— 故必须用 SAVEPOINT 而非整事务回滚。
            # 学生行锁已在循环顶部拿过（同时满足扣分写入协议 逻-中-5），此处不重复加锁。
            try:
                with db.begin_nested():
                    db.add(
                        models.RollCallEvent(
                            session_id=session.id,
                            student_id=s.id,
                            path_type="manual",
                            base_status="absent",
                            status_source="auto_settle",
                            checked_in_at=_now_jst(),
                        )
                    )
                    db.add(
                        models.DemeritEvent(
                            student_id=s.id,
                            source_type="rollcall_absent",
                            source_event_id=session.id,
                            points=ROLLCALL_ABSENT_POINTS,
                            reason=f"点呼欠席（{session.session_type}）",
                            month=month,
                            created_by_teacher_id=None,
                        )
                    )
            except IntegrityError:
                # 该生本场缺席扣分已存在（并发重复结算）→ SAVEPOINT 自动回滚，跳过该生继续结算其余学生
                pass
