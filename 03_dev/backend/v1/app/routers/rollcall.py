"""点呼 endpoint (#16-#20 点呼 部分).

GET  /api/v1/rollcall/today/sessions              — 当日セッション一覧
POST /api/v1/rollcall/sessions/{id}/start         — 手動開始
POST /api/v1/rollcall/sessions/{id}/end           — 手動終了
POST /api/v1/rollcall/sessions/{id}/checkins      — NFC/手動チェックイン
GET  /api/v1/rollcall/sessions/{id}/board         — 全座席現状
GET  /api/v1/rollcall/sessions/{id}/summary       — 総結中層ページ
PATCH /api/v1/rollcall/events/{id}                — 教師改判
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_teacher, require_teacher_roles

router = APIRouter(prefix="/api/v1/rollcall", tags=["rollcall"])


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
        models.RollCallSession.scheduled_window_start_at >= datetime(
            today.year, today.month, today.day, 0, 0, 0,
            tzinfo=__import__("zoneinfo").ZoneInfo("Asia/Tokyo"),
        )
    )
    # R4 dorm filter
    sessions = db.scalars(stmt).all()
    if teacher.assigned_dorm is not None and teacher.role not in {
        "寮務部長", "寮務課長", "国際交流部長", "国際交流課長",
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
        raise HTTPException(409, {"code": "ALREADY_RUNNING", "message": "既に開始済みです"})
    if session.session_status == "ended":
        raise HTTPException(409, {"code": "ALREADY_ENDED", "message": "終了済みのセッションです"})

    # -5min 前チェック (RollCall_Spec §5.4)
    window_minus5 = session.scheduled_window_start_at.replace(
        minute=session.scheduled_window_start_at.minute - 5
    )
    if now < window_minus5.replace(minute=max(0, window_minus5.minute)):
        raise HTTPException(409, {"code": "NOT_YET_ALLOWED", "message": "開始時刻の 5 分前より早いです"})

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
        raise HTTPException(409, {"code": "SESSION_NOT_RUNNING", "message": "実行中のセッションではありません"})

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
        raise HTTPException(409, {"code": "SESSION_NOT_RUNNING", "message": "実行中の点呼セッションがありません"})

    now = body.ts_local or _now_jst()
    student: Optional[models.Student] = None

    if body.card_uid:
        # 路径 A: NFC カード UID で学生特定
        # card_uid は student.card_uid に紐付け (将来 NFC_CARD テーブルで管理予定)
        # 今は student テーブルに card_uid カラムなし → 暫定で手動 student_id fallback
        if not body.student_id:
            raise HTTPException(
                422,
                {"code": "UNKNOWN_CARD", "message": "カード UID に対応する学生が見つかりません (P1 実装待ち)"},
            )
        student = db.get(models.Student, body.student_id)
    elif body.student_id:
        # 路径 B / 手動
        student = db.get(models.Student, body.student_id)
    else:
        raise HTTPException(422, {"code": "MISSING_IDENTIFIER", "message": "card_uid か student_id が必要"})

    if not student:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "学生が見つかりません"})

    # 幂等 check (同 session + 同 student で既存があれば OK で返す)
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
    students = db.scalars(
        select(models.Student).where(
            models.Student.dorm_unit.in_(session.dorm_unit_set),
            models.Student.status == "active",
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
        if e.student_id not in event_map or e.checked_in_at > event_map[e.student_id].checked_in_at:
            event_map[e.student_id] = e

    entries: list[schemas.RollCallBoardEntryOut] = []
    summary: dict[str, int] = {"present": 0, "late": 0, "absent": 0, "init": 0, "exempt_range": 0}
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
        if e.student_id not in event_map or e.checked_in_at > event_map[e.student_id].checked_in_at:
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
# PATCH /rollcall/events/{id} — 教師改判 (RollCall_Spec §11)
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
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "点呼イベントが見つかりません"})

    # append-only: 既存行は変えず新しい override 行を追加
    override_event = models.RollCallEvent(
        session_id=event.session_id,
        student_id=event.student_id,
        path_type="manual",
        base_status=body.to_status,
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
                "from": event.base_status,
                "to": body.to_status,
                "reason": body.reason,
                "evidence": body.evidence,
            },
        )
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
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "セッションが見つかりません"})
    return session


def _settle_absent(db: Session, session: models.RollCallSession) -> None:
    """セッション終了時 — チェックインなし学生を absent に記録。"""
    students = db.scalars(
        select(models.Student).where(
            models.Student.dorm_unit.in_(session.dorm_unit_set),
            models.Student.status == "active",
        )
    ).all()

    checked_ids = set(
        db.scalars(
            select(models.RollCallEvent.student_id).where(
                models.RollCallEvent.session_id == session.id,
                models.RollCallEvent.base_status.in_(["present", "late", "exempt_range"]),
            )
        ).all()
    )

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
