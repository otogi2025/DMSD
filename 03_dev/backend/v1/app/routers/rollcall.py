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

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_teacher

router = APIRouter(prefix="/api/v1/rollcall", tags=["rollcall"])

# spec §7.5 + propose §1.2 自动扣分点数
# late 1 点 / absent 2 点（与改判联动 _OVERRIDE_DEMERIT_MAP 中 present→late=+0.5 /
# present→absent=+1.0 的差额对齐 — 整数 vs 差额是两套机制：
# - 这里 = 学生本来就 late/absent 的初始扣分
# - 改判联动 = 老师改判时新增 / 减少的差额）
ROLLCALL_LATE_POINTS = 1.0
ROLLCALL_ABSENT_POINTS = 2.0


def _today_jst() -> date:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _now_jst() -> datetime:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo"))


# ---------------------------------------------------------------
# GET /rollcall/today/sessions
# ---------------------------------------------------------------
@router.get("/today/sessions", response_model=list[schemas.RollCallSessionOut])
def today_sessions(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    today = _today_jst()
    # 今日作成された session を返す (cron がなければ空)
    stmt = select(models.RollCallSession).where(
        models.RollCallSession.scheduled_window_start_at
        >= datetime(
            today.year,
            today.month,
            today.day,
            0,
            0,
            0,
            tzinfo=__import__("zoneinfo").ZoneInfo("Asia/Tokyo"),
        )
    )
    # R4 dorm filter
    sessions = db.scalars(stmt).all()
    if teacher.assigned_dorm is not None and teacher.role not in {
        "寮務部長",
        "寮務課長",
        "国際交流部長",
        "国際交流課長",
    }:
        dorm_set = [1, 2] if teacher.assigned_dorm == 1 else [teacher.assigned_dorm]
        sessions = [s for s in sessions if any(d in s.dorm_unit_set for d in dorm_set)]

    return [schemas.RollCallSessionOut.model_validate(s) for s in sessions]


# ---------------------------------------------------------------
# GET /rollcall/sessions?from=&to=  — 历史列表 (教师 Web RecordsPage 用)
# 5-27 新增：从已有 RollCallSession model 派生 SELECT 查询，不需要新 schema。
# 日期范围 from / to 是 YYYY-MM-DD，不指定时默认查过去 7 天（含今天）。
# R4 寮过滤跟 today_sessions 同样逻辑：役职 4 人跨寮全件，其他按 assigned_dorm。
# ---------------------------------------------------------------
@router.get("/sessions", response_model=list[schemas.RollCallSessionOut])
def list_sessions_history(
    from_: Optional[date] = None,
    to: Optional[date] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
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

    # R4 寮过滤 — 役职（跨寮 4 人）看全件，其他只看 assigned_dorm
    if teacher.assigned_dorm is not None and teacher.role not in {
        "寮務部長",
        "寮務課長",
        "国際交流部長",
        "国際交流課長",
    }:
        dorm_set = [1, 2] if teacher.assigned_dorm == 1 else [teacher.assigned_dorm]
        sessions = [s for s in sessions if any(d in s.dorm_unit_set for d in dorm_set)]

    return [schemas.RollCallSessionOut.model_validate(s) for s in sessions]


# ---------------------------------------------------------------
# POST /rollcall/sessions/{id}/start — 手動開始
# ---------------------------------------------------------------
@router.post("/sessions/{session_id}/start", response_model=schemas.RollCallSessionOut)
def start_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
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

    # -5min 前チェック (RollCall_Spec §5.4)
    window_minus5 = session.scheduled_window_start_at.replace(
        minute=session.scheduled_window_start_at.minute - 5
    )
    if now < window_minus5.replace(minute=max(0, window_minus5.minute)):
        raise HTTPException(
            409, {"code": "NOT_YET_ALLOWED", "message": "開始時刻の 5 分前より早いです"}
        )

    session.session_status = "running"
    session.started_at = now
    session.started_source = "teacher"
    session.started_by = teacher.id
    db.commit()
    db.refresh(session)
    return schemas.RollCallSessionOut.model_validate(session)


# ---------------------------------------------------------------
# POST /rollcall/sessions/{id}/end — 手動終了
# ---------------------------------------------------------------
@router.post("/sessions/{session_id}/end", response_model=schemas.RollCallSessionOut)
def end_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    session = _get_session_or_404(db, session_id)
    if session.session_status != "running":
        raise HTTPException(
            409,
            {
                "code": "SESSION_NOT_RUNNING",
                "message": "実行中のセッションではありません",
            },
        )

    now = _now_jst()
    session.session_status = "ended"
    session.ended_at = now
    session.ended_source = "teacher"
    session.ended_by = teacher.id

    # 未チェックの学生を absent に
    _settle_absent(db, session)
    db.commit()
    db.refresh(session)
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
    teacher: models.Teacher = Depends(get_current_teacher),
):
    session = _get_session_or_404(db, session_id)
    if session.session_status != "running":
        raise HTTPException(
            409,
            {
                "code": "SESSION_NOT_RUNNING",
                "message": "実行中の点呼セッションがありません",
            },
        )

    now = body.ts_local or _now_jst()
    student: Optional[models.Student] = None

    # A-020 (2026-05-21): path_hint 一致性校验（client 显式标路径时挡假数据）
    if body.path_hint == "A" and not body.card_uid:
        raise HTTPException(
            422,
            {
                "code": "PATH_HINT_MISMATCH",
                "message": "path_hint=A 必须有 card_uid",
            },
        )
    if body.path_hint == "B" and not body.idempotency_key:
        raise HTTPException(
            422,
            {
                "code": "PATH_HINT_MISMATCH",
                "message": "path_hint=B 必须有 idempotency_key",
            },
        )

    if body.card_uid:
        # 路径 A: NFC カード UID で学生特定
        # card_uid は student.card_uid に紐付け (将来 NFC_CARD テーブルで管理予定)
        # 今は student テーブルに card_uid カラムなし → 暫定で手動 student_id fallback
        if not body.student_id:
            raise HTTPException(
                422,
                {
                    "code": "UNKNOWN_CARD",
                    "message": "カード UID に対応する学生が見つかりません (P1 実装待ち)",
                },
            )
        student = db.get(models.Student, body.student_id)
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
    base_status = "present" if now <= session.scheduled_on_time_end_at else "late"

    event = models.RollCallEvent(
        session_id=session_id,
        student_id=student.id,
        path_type="A" if body.card_uid else ("B" if body.idempotency_key else "manual"),
        base_status=base_status,
        status_source=body.status_source,
        checked_in_at=now,
        idempotency_key=body.idempotency_key,
        card_uid=body.card_uid,
    )
    db.add(event)

    # spec §7.5 自动扣分 — late 即扣 1 点
    # 老师之后改判 late → present 走 _OVERRIDE_DEMERIT_MAP 自动 revoke
    if base_status == "late":
        db.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="rollcall_late",
                source_event_id=session.id,
                points=ROLLCALL_LATE_POINTS,
                reason=f"点呼遅刻（{session.session_type}）",
                month=session.scheduled_window_start_at.strftime("%Y-%m"),
                created_by_teacher_id=None,
            )
        )

    db.commit()
    db.refresh(event)
    return schemas.RollCallEventOut.model_validate(event)


# ---------------------------------------------------------------
# GET /rollcall/sessions/{id}/board — 全座席現状
# ---------------------------------------------------------------
@router.get("/sessions/{session_id}/board", response_model=schemas.RollCallBoardOut)
def session_board(
    session_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    session = _get_session_or_404(db, session_id)

    # このセッション対象の学生 (R4: dorm_unit_set で絞る)
    # is_demo 学生排除 — reviewer / 体验账号不进出席板
    students = db.scalars(
        select(models.Student).where(
            models.Student.dorm_unit.in_(session.dorm_unit_set),
            models.Student.status == "active",
            models.Student.is_demo.is_(False),
        )
    ).all()

    # 最新 event を学生ごとに取る
    events = db.scalars(
        select(models.RollCallEvent).where(
            models.RollCallEvent.session_id == session_id
        )
    ).all()
    event_map: dict[UUID, models.RollCallEvent] = {}
    for e in events:
        if (
            e.student_id not in event_map
            or e.checked_in_at > event_map[e.student_id].checked_in_at
        ):
            event_map[e.student_id] = e

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
        st = e.base_status if e else "init"
        summary[st] = summary.get(st, 0) + 1
        entries.append(
            schemas.RollCallBoardEntryOut(
                student_id=s.id,
                student_no=s.student_no,
                name=s.name,
                room_no=s.room_no,
                base_status=st,
                checked_in_at=e.checked_in_at if e else None,
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
    teacher: models.Teacher = Depends(get_current_teacher),
):
    session = _get_session_or_404(db, session_id)
    today = _today_jst()

    events = db.scalars(
        select(models.RollCallEvent)
        .where(models.RollCallEvent.session_id == session_id)
        .options(selectinload(models.RollCallEvent.session))
    ).all()

    # latest per student
    event_map: dict[UUID, models.RollCallEvent] = {}
    for e in events:
        if (
            e.student_id not in event_map
            or e.checked_in_at > event_map[e.student_id].checked_in_at
        ):
            event_map[e.student_id] = e

    absent: list[dict] = []
    late: list[dict] = []
    exempt_outstay: list[dict] = []

    for sid, e in event_map.items():
        s = db.get(models.Student, sid)
        if not s:
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
# spec §11.4 改判扣分联动表
#   key = (from_status, to_status)
#   value = (delta_points, source_type)
#   正 delta = 加扣分（新建 DemeritEvent 行）
#   负 delta = 撤销之前自动扣（找之前 session+student 的自动 event revoke）
#   delta=0 = 不联动
# ---------------------------------------------------------------
_OVERRIDE_DEMERIT_MAP: dict[tuple[str, str], tuple[float, str | None]] = {
    ("present", "late"): (0.5, "rollcall_late"),
    ("present", "absent"): (1.0, "rollcall_absent"),
    ("late", "present"): (-0.5, None),
    ("late", "absent"): (0.5, "rollcall_absent"),
    ("absent", "present"): (-1.0, None),
    ("absent", "late"): (-0.5, None),
    ("exempt_range", "present"): (0.0, None),
    ("exempt_range", "late"): (0.5, "rollcall_late"),
    ("exempt_range", "absent"): (1.0, "rollcall_absent"),
    ("present", "exempt_range"): (0.0, None),
    ("late", "exempt_range"): (-0.5, None),
    ("absent", "exempt_range"): (-1.0, None),
}


def _apply_override_demerit(
    db: Session,
    student_id: UUID,
    session: models.RollCallSession,
    from_status: str,
    to_status: str,
    teacher_id: UUID,
) -> None:
    """spec §11.4 改判扣分联动 — 正 delta 加扣 / 负 delta 撤销之前自动扣分。"""
    from datetime import datetime as _dt
    from datetime import timezone as _tz

    info = _OVERRIDE_DEMERIT_MAP.get((from_status, to_status))
    if not info:
        return
    delta, source_type = info
    if delta == 0.0:
        return

    month = session.scheduled_window_start_at.strftime("%Y-%m")
    now_utc = _dt.now(_tz.utc)
    if delta > 0:
        db.add(
            models.DemeritEvent(
                student_id=student_id,
                source_type=source_type or "manual",
                source_event_id=session.id,
                points=delta,
                reason=f"教師改判: {from_status} → {to_status}（spec §11.4 自動）",
                month=month,
                created_by_teacher_id=teacher_id,
            )
        )
    else:
        # 负 delta — 撤销之前 session+student 的自动扣分 event
        prev = db.scalars(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == student_id,
                models.DemeritEvent.source_event_id == session.id,
                models.DemeritEvent.revoked_at.is_(None),
                models.DemeritEvent.source_type.in_(
                    ["rollcall_late", "rollcall_absent"]
                ),
            )
        ).all()
        for ev in prev:
            ev.revoked_at = now_utc
            ev.revoked_by_teacher_id = teacher_id
            ev.revoke_reason = f"教師改判 {from_status} → {to_status} 自動撤销"


# ---------------------------------------------------------------
# PATCH /rollcall/events/{id} — 教師改判 (RollCall_Spec §11 + §11.4)
# ---------------------------------------------------------------
@router.patch("/events/{event_id}", response_model=schemas.RollCallEventOut)
def patch_event(
    event_id: UUID,
    body: schemas.RollCallEventPatch,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    event = db.get(models.RollCallEvent, event_id)
    if not event:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "点呼イベントが見つかりません"}
        )

    old_status = event.base_status
    new_status = body.to_status

    # append-only: 既存行は変えず新しい override 行を追加
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

    # spec §11.4 改判扣分联动
    session = db.get(models.RollCallSession, event.session_id)
    if session is not None and old_status != new_status:
        _apply_override_demerit(
            db, event.student_id, session, old_status, new_status, teacher.id
        )

    db.commit()
    db.refresh(override_event)
    return schemas.RollCallEventOut.model_validate(override_event)


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

    month = session.scheduled_window_start_at.strftime("%Y-%m")
    for s in students:
        if s.id not in checked_ids:
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
            # spec §7.5 缺席自动扣 2 点；改判 absent → present 走 _OVERRIDE_DEMERIT_MAP 自动 revoke
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
