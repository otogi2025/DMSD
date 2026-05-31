"""学習 endpoint (#14-#20 学習自習).

GET  /api/v1/study/today/attendees              — 一本道入口 (R2)
POST /api/v1/study/checkins                     — 出席記録
POST /api/v1/study/checkins/bulk-finalize       — 終了一括 absent 判定
PATCH /api/v1/study/checkins/{id}               — 手動修正
POST /api/v1/study/absence-requests             — 学習欠席届 (学生)
GET  /api/v1/study/absence-requests             — 欠席届一覧 (学習担当)
POST /api/v1/study/absence-requests/{id}/decision — 承認/拒否
POST /api/v1/study/cancel-today                 — 今日学習中止 (学習担当のみ)
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import (
    dorm_units_for_teacher,
    get_current_student,
    get_current_teacher,
    require_teacher_roles,
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


router = APIRouter(prefix="/api/v1/study", tags=["study"])

# 学習開始時刻 (JST) — system_features §7.3
STUDY_START_HOUR = 19
STUDY_START_MINUTE = 40
# 欠席届 締切 = 学習開始 と同時刻
ABSENCE_DEADLINE_HOUR = 19
ABSENCE_DEADLINE_MINUTE = 40

# spec §7.5 + propose §1.2 学習欠席自动扣分点数（finalize 时 add DemeritEvent）
STUDY_ABSENT_POINTS = 1.5


def _today_jst() -> date:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _now_jst() -> datetime:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo("Asia/Tokyo"))


def _study_start_dt(target: date) -> datetime:
    from zoneinfo import ZoneInfo

    return datetime(
        target.year,
        target.month,
        target.day,
        STUDY_START_HOUR,
        STUDY_START_MINUTE,
        0,
        tzinfo=ZoneInfo("Asia/Tokyo"),
    )


# ---------------------------------------------------------------
# GET /study/today/attendees — 一本道入口 (#14, R2)
# ---------------------------------------------------------------
@router.get("/today/attendees", response_model=schemas.StudyTodayOut)
def today_attendees(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    today = target_date or _today_jst()
    study_start = _study_start_dt(today)

    # 当日有効な study_roster
    term = _academic_term(today)
    roster_stmt = select(models.StudyRoster).where(
        models.StudyRoster.academic_term == term,
        models.StudyRoster.removed_at.is_(None),
    )
    roster_rows = db.scalars(roster_stmt).all()
    student_ids = [r.student_id for r in roster_rows]
    if not student_ids:
        return schemas.StudyTodayOut(
            target_date=today,
            study_start_at=study_start,
            expected_attendees=[],
            exempted_count={"outstay": 0, "absence_request": 0},
            summary={"expected": 0, "checked_in": 0, "late": 0, "absent": 0},
        )

    # 出寮届で approved + 期間内 → 外出控除
    outstay_ids = set(
        db.scalars(
            select(models.Application.student_id).where(
                models.Application.student_id.in_(student_ids),
                models.Application.status == "approved",
                models.Application.leave_date <= today,
                models.Application.return_date >= today,
            )
        ).all()
    )

    # 学習欠席届 approved 当日 → 欠席控除
    absence_ids = set(
        db.scalars(
            select(models.StudyAbsenceRequest.student_id).where(
                models.StudyAbsenceRequest.student_id.in_(student_ids),
                models.StudyAbsenceRequest.target_date == today,
                models.StudyAbsenceRequest.status == "approved",
            )
        ).all()
    )

    # 学生詳細
    students = db.scalars(
        select(models.Student).where(models.Student.id.in_(student_ids))
    ).all()
    student_map = {s.id: s for s in students}

    # 既存の checkin 記録
    checkin_map = {
        c.student_id: c
        for c in db.scalars(
            select(models.StudyCheckin).where(
                models.StudyCheckin.student_id.in_(student_ids),
                models.StudyCheckin.target_date == today,
            )
        ).all()
    }

    # R4 dorm filter
    dorm_filter: tuple[int, ...]
    if teacher.assigned_dorm is None or teacher.role in {
        "寮務部長",
        "寮務課長",
        "国際交流部長",
        "国際交流課長",
    }:
        dorm_filter = (1, 2, 4)
    elif teacher.assigned_dorm == 1:
        dorm_filter = (1, 2)
    else:
        dorm_filter = (teacher.assigned_dorm,)

    attendees: list[schemas.StudyAttendeeOut] = []
    outstay_cnt = 0
    absence_cnt = 0

    for sid in student_ids:
        s = student_map.get(sid)
        if not s or s.dorm_unit not in dorm_filter:
            continue
        if sid in outstay_ids:
            outstay_cnt += 1
            attendees.append(
                schemas.StudyAttendeeOut(
                    student_id=sid,
                    student_no=s.student_no,
                    name=s.name,
                    room_no=s.room_no,
                    dorm_unit=s.dorm_unit,
                    expected_status="exempted_outstay",
                    exemption_reason="出寮届承認済",
                    checkin=None,
                )
            )
            continue
        if sid in absence_ids:
            absence_cnt += 1
            attendees.append(
                schemas.StudyAttendeeOut(
                    student_id=sid,
                    student_no=s.student_no,
                    name=s.name,
                    room_no=s.room_no,
                    dorm_unit=s.dorm_unit,
                    expected_status="exempted_absence",
                    exemption_reason="学習欠席届承認済",
                    checkin=None,
                )
            )
            continue

        c = checkin_map.get(sid)
        checkin_dict = None
        if c and c.status != "init":
            checkin_dict = {"checked_at": c.checked_at, "status": c.status}

        attendees.append(
            schemas.StudyAttendeeOut(
                student_id=sid,
                student_no=s.student_no,
                name=s.name,
                room_no=s.room_no,
                dorm_unit=s.dorm_unit,
                expected_status="expected",
                checkin=checkin_dict,
            )
        )

    # 五十音 sort
    attendees.sort(key=lambda a: a.name)

    present = sum(
        1
        for a in attendees
        if a.checkin
        and a.checkin["status"] in ("present", "late")
        and a.expected_status == "expected"
    )
    late = sum(
        1
        for a in attendees
        if a.checkin
        and a.checkin["status"] == "late"
        and a.expected_status == "expected"
    )
    absent = sum(
        1
        for a in attendees
        if a.expected_status == "expected"
        and (not a.checkin or a.checkin["status"] == "absent")
    )

    return schemas.StudyTodayOut(
        target_date=today,
        study_start_at=study_start,
        expected_attendees=attendees,
        exempted_count={"outstay": outstay_cnt, "absence_request": absence_cnt},
        summary={
            "expected": sum(1 for a in attendees if a.expected_status == "expected"),
            "checked_in": present,
            "late": late,
            "absent": absent,
        },
    )


# ---------------------------------------------------------------
# POST /study/checkins — 出席記録 (#15)
# ---------------------------------------------------------------
@router.post("/checkins", response_model=schemas.StudyCheckinOut, status_code=201)
def create_checkin(
    body: schemas.StudyCheckinIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    today = _today_jst()
    checked_at = body.checked_at or _now_jst()
    study_start = _study_start_dt(today)

    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # R4 寮边界：寮監等 dorm-scoped 角色不能给管辖外学生写出席记录
    _assert_student_in_dorm(teacher, student)

    # 既存レコード確認 (upsert 相当)
    existing = db.scalars(
        select(models.StudyCheckin).where(
            models.StudyCheckin.student_id == body.student_id,
            models.StudyCheckin.target_date == today,
        )
    ).first()

    determined_status = "present" if checked_at < study_start else "late"

    if existing:
        if existing.status not in ("init", "absent"):
            raise HTTPException(
                409, {"code": "ALREADY_CHECKED_IN", "message": "既に出席記録済みです"}
            )
        existing.checked_at = checked_at
        existing.status = determined_status
        existing.recorded_by = teacher.id
        record = existing
    else:
        record = models.StudyCheckin(
            student_id=body.student_id,
            target_date=today,
            checked_at=checked_at,
            status=determined_status,
            recorded_by=teacher.id,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return schemas.StudyCheckinOut.model_validate(record)


# ---------------------------------------------------------------
# POST /study/checkins/bulk-finalize — 一本道の終了ボタン (#20)
# ---------------------------------------------------------------
@router.post("/checkins/bulk-finalize", response_model=schemas.StudyFinalizeOut)
def bulk_finalize(
    body: schemas.StudyFinalizeIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("学習担当", "寮務部長", "寮務課長", "寮監")
    ),
):
    today = body.target_date or _today_jst()
    term = _academic_term(today)

    # R4 寮边界：先拉全 roster，再按老师管辖寮过滤（跨寮角色 None → 不过滤）
    all_roster_ids = set(
        db.scalars(
            select(models.StudyRoster.student_id).where(
                models.StudyRoster.academic_term == term,
                models.StudyRoster.removed_at.is_(None),
            )
        ).all()
    )
    dorm_units = dorm_units_for_teacher(teacher)
    if dorm_units is not None:
        # 只保留该老师管辖寮的学生
        in_scope = set(
            db.scalars(
                select(models.Student.id).where(
                    models.Student.id.in_(all_roster_ids),
                    models.Student.dorm_unit.in_(dorm_units),
                )
            ).all()
        )
        roster_ids = all_roster_ids & in_scope
    else:
        roster_ids = all_roster_ids

    # 承認済欠席届 → finalize 対象外
    exempt_ids = set(
        db.scalars(
            select(models.StudyAbsenceRequest.student_id).where(
                models.StudyAbsenceRequest.target_date == today,
                models.StudyAbsenceRequest.status == "approved",
            )
        ).all()
    )
    outstay_exempt = set(
        db.scalars(
            select(models.Application.student_id).where(
                models.Application.status == "approved",
                models.Application.leave_date <= today,
                models.Application.return_date >= today,
            )
        ).all()
    )
    exempt_ids.update(outstay_exempt)

    existing_map = {
        c.student_id: c
        for c in db.scalars(
            select(models.StudyCheckin).where(models.StudyCheckin.target_date == today)
        ).all()
    }

    to_absent: list[UUID] = []
    for sid in roster_ids:
        if sid in exempt_ids:
            continue
        c = existing_map.get(sid)
        if c is None:
            # 新規 absent 行
            db.add(
                models.StudyCheckin(
                    student_id=sid,
                    target_date=today,
                    status="absent",
                    recorded_by=teacher.id,
                )
            )
            to_absent.append(sid)
        elif c.status == "init":
            c.status = "absent"
            c.recorded_by = teacher.id
            to_absent.append(sid)

    # spec §7.5 学習欠席自动扣 1.5 点（propose §1.2 默认值）
    # finalize 老师 = created_by（不是 None — 老师按了「学習終了」是手动触发）
    month = today.strftime("%Y-%m")
    for sid in to_absent:
        db.add(
            models.DemeritEvent(
                student_id=sid,
                source_type="study_absent",
                source_event_id=None,
                points=STUDY_ABSENT_POINTS,
                reason=f"学習欠席（{today.isoformat()}）",
                month=month,
                created_by_teacher_id=teacher.id,
            )
        )

    db.commit()

    absent_students = [{"student_id": str(sid)} for sid in to_absent]
    return schemas.StudyFinalizeOut(
        finalized_count=len(to_absent), absent_students=absent_students
    )


# ---------------------------------------------------------------
# PATCH /study/checkins/{checkin_id} — 手動修正 (#20)
# ---------------------------------------------------------------
@router.patch("/checkins/{checkin_id}", response_model=schemas.StudyCheckinOut)
def patch_checkin(
    checkin_id: UUID,
    body: schemas.StudyCheckinPatch,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    record = db.get(models.StudyCheckin, checkin_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "記録が見つかりません"}
        )
    # R4 寮边界：通过 checkin 记录找到对应学生，校验老师管辖范围
    student = db.get(models.Student, record.student_id)
    if student:
        _assert_student_in_dorm(teacher, student)
    record.status = body.status
    record.overridden_by = teacher.id
    record.override_reason = body.override_reason
    db.commit()
    db.refresh(record)
    return schemas.StudyCheckinOut.model_validate(record)


# ---------------------------------------------------------------
# POST /study/absence-requests — 学習欠席届提出 (学生)
# ---------------------------------------------------------------
@router.post(
    "/absence-requests",
    response_model=schemas.StudyAbsenceRequestOut,
    status_code=201,
)
def submit_absence_request(
    body: schemas.StudyAbsenceRequestIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    now = _now_jst()
    # 締切チェック: 当日 19:40 前
    if body.target_date == now.date():
        deadline = time(ABSENCE_DEADLINE_HOUR, ABSENCE_DEADLINE_MINUTE)
        if now.time() >= deadline:
            raise HTTPException(
                422,
                {
                    "code": "LATE_SUBMISSION",
                    "message": "学習欠席届の締切 (19:40) を過ぎています",
                },
            )

    # 重複チェック
    existing = db.scalars(
        select(models.StudyAbsenceRequest).where(
            models.StudyAbsenceRequest.student_id == student.id,
            models.StudyAbsenceRequest.target_date == body.target_date,
        )
    ).first()
    if existing:
        raise HTTPException(
            409,
            {
                "code": "DUPLICATE_REQUEST",
                "message": "この日の欠席届は既に提出済みです",
            },
        )

    record = models.StudyAbsenceRequest(
        student_id=student.id,
        target_date=body.target_date,
        period=body.period,
        reason=body.reason,
    )
    db.add(record)
    db.flush()

    # R1 メール → 学習担当
    _notify_absence_submitted(db, record, student)

    db.commit()
    db.refresh(record)
    return schemas.StudyAbsenceRequestOut.model_validate(record)


# ---------------------------------------------------------------
# GET /study/absence-requests — 一覧 (学習担当)
# ---------------------------------------------------------------
@router.get("/absence-requests", response_model=list[schemas.StudyAbsenceRequestOut])
def list_absence_requests(
    target_date: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    stmt = select(models.StudyAbsenceRequest).order_by(
        models.StudyAbsenceRequest.submitted_at.asc()
    )
    if target_date:
        stmt = stmt.where(models.StudyAbsenceRequest.target_date == target_date)
    if status_filter:
        stmt = stmt.where(models.StudyAbsenceRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.StudyAbsenceRequestOut.model_validate(r) for r in rows]


# ---------------------------------------------------------------
# POST /study/absence-requests/{id}/decision — 学習担当が承認/拒否
# ---------------------------------------------------------------
@router.post(
    "/absence-requests/{request_id}/decision",
    response_model=schemas.StudyAbsenceRequestOut,
)
def decide_absence_request(
    request_id: UUID,
    body: schemas.StudyAbsenceDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("学習担当", "寮務部長", "寮務課長", "寮監")
    ),
):
    record = db.get(models.StudyAbsenceRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})
    if record.status != "pending":
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )
    record.status = body.decision
    record.decided_by = teacher.id
    record.decided_at = _now_jst()
    record.comment = body.comment
    db.commit()
    db.refresh(record)
    return schemas.StudyAbsenceRequestOut.model_validate(record)


# ---------------------------------------------------------------
# POST /study/cancel-today — 今日学習中止 (学習担当のみ)
# ---------------------------------------------------------------
@router.post("/cancel-today", status_code=200)
def cancel_today(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("学習担当", "寮務部長", "寮務課長")
    ),
):
    """今日の学習を中止 = 全 roster 学生を 'exempt' に一括設定。"""
    today = _today_jst()
    term = _academic_term(today)

    roster_ids = list(
        db.scalars(
            select(models.StudyRoster.student_id).where(
                models.StudyRoster.academic_term == term,
                models.StudyRoster.removed_at.is_(None),
            )
        ).all()
    )

    existing_map = {
        c.student_id: c
        for c in db.scalars(
            select(models.StudyCheckin).where(models.StudyCheckin.target_date == today)
        ).all()
    }

    for sid in roster_ids:
        c = existing_map.get(sid)
        if c:
            c.status = "exempt"
            c.overridden_by = teacher.id
            c.override_reason = "今日学習中止"
        else:
            db.add(
                models.StudyCheckin(
                    student_id=sid,
                    target_date=today,
                    status="exempt",
                    recorded_by=teacher.id,
                    override_reason="今日学習中止",
                )
            )

    db.commit()
    return {"cancelled_count": len(roster_ids), "target_date": str(today)}


# ---------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------
def _academic_term(d: date) -> str:
    """date → '2026-spring' / '2026-fall' 形式。"""
    season = "spring" if d.month <= 8 else "fall"
    return f"{d.year}-{season}"


def _notify_absence_submitted(
    db: Session,
    record: models.StudyAbsenceRequest,
    student: models.Student,
) -> None:
    """学習欠席届提出 → 学習担当 email (R1)。失敗しても業務ブロックしない。"""
    try:
        teachers = db.scalars(
            select(models.Teacher).where(
                models.Teacher.role == "学習担当",
                models.Teacher.status == "active",
            )
        ).all()
        to_emails = [t.email for t in teachers if t.email]
        if to_emails:
            log = models.NotificationLog(
                channel="email",
                template_key="study_absence_submitted",
                target_type="role",
                payload={
                    "student_name": student.name,
                    "student_no": student.student_no,
                    "target_date": str(record.target_date),
                    "reason": record.reason,
                    "to_emails": to_emails,
                },
                status="pending",
            )
            db.add(log)
            db.flush()
    except Exception:
        # 通知失败不阻断业务（设计如此），但记日志留排查线索 — 否则学習担当不知道有学生提交了欠席届
        logging.getLogger(__name__).exception("学習欠席届の通知記録に失敗")
