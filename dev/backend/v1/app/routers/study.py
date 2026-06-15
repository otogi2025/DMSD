"""学習 endpoint (#14-#20 学習自習).

GET  /api/v1/study/today/attendees              — 一本道入口 (R2)
POST /api/v1/study/checkins                     — 出席記録
POST /api/v1/study/checkins/bulk-finalize       — 終了一括 absent 判定
PATCH /api/v1/study/checkins/{id}               — 手動修正
POST /api/v1/study/absence-requests             — 学習欠席届 (学生)
GET  /api/v1/study/absence-requests             — 欠席届一覧 (学習担当)
POST /api/v1/study/absence-requests/{id}/decision — 承認/拒否
POST /api/v1/study/cancel-today                 — 今日学習中止 (学習担当のみ)
GET    /api/v1/study/roster                      — 学習対象名簿一覧 (学習担当 / 寮務管理)
POST   /api/v1/study/roster                      — 名簿に学生追加
DELETE /api/v1/study/roster/{student_id}         — 名簿から学生を外す (软删)
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.VIEW)
    ),
):
    today = target_date or _today_jst()
    study_start = _study_start_dt(today)

    # 当日有効な study_roster
    # 演示隔离：join Student 加 demo_scope，让真老师只拿真实学生名簿 / 演示老师只拿演示学生名簿。
    # student_ids 是后续 outstay / absence / checkin / 学生详细 全部查询的源头，
    # 在这里收口一次即整页隔离（不必逐查再加 demo 过滤）。
    term = _academic_term(today)
    roster_stmt = (
        select(models.StudyRoster)
        .join(models.Student, models.Student.id == models.StudyRoster.student_id)
        .where(
            models.StudyRoster.academic_term == term,
            models.StudyRoster.removed_at.is_(None),
            demo_scope_for_teacher(teacher),
        )
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    from zoneinfo import ZoneInfo

    today = _today_jst()
    # rollcall-12: 不再无条件信任客户端 checked_at — 仅在 server now 容忍窗口内采纳，
    # 超窗回退 server time，防把迟到的晚自习签到伪造成 present
    server_now = _now_jst()
    checked_at = server_now
    if body.checked_at is not None:
        ca = (
            body.checked_at
            if body.checked_at.tzinfo
            else body.checked_at.replace(tzinfo=ZoneInfo("Asia/Tokyo"))
        )
        if (
            server_now - timedelta(minutes=10)
            <= ca
            <= server_now + timedelta(minutes=2)
        ):
            checked_at = ca
    study_start = _study_start_dt(today)

    student = db.get(models.Student, body.student_id)
    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # 演示隔离：演示老师只能给演示学生写、真老师只能给真实学生写（否则 404）
    assert_student_demo_match(teacher, student)

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
        # absent → present/late：结算缺席后又来签到，要撤掉那条已记的缺席扣分（按本行 id 精确撤）。
        # init → present/late 不涉及扣分（init 还没结算过）。
        if existing.status == "absent":
            _revoke_study_absent_demerit(db, existing, teacher.id)
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

    # 并发兜底：existing 预查与 INSERT 之间若有并发请求先建了同 (student, date) 行，
    # 本次 INSERT 撞 uq_sc_date 唯一约束 → 回滚后重查已存行幂等返回，不冒泡成 500。
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        again = db.scalars(
            select(models.StudyCheckin).where(
                models.StudyCheckin.student_id == body.student_id,
                models.StudyCheckin.target_date == today,
            )
        ).first()
        if again:
            return schemas.StudyCheckinOut.model_validate(again)
        raise
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
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    # 演示隔离：批量结算影响一组学生、无法按单个学生判 demo → 演示老师整体禁止
    if teacher.is_demo:
        raise HTTPException(
            403,
            {"code": "DEMO_READONLY", "message": "デモアカウントは操作できません"},
        )

    today = body.target_date or _today_jst()

    # target_date 边界校验 —— 原来无边界，老师可对任意过去 / 未来日期补判缺席扣分。
    # 上界：不能晚于今天（JST）—— 未来日期的「缺席」无意义。
    # 下界：不早于 30 天前 —— 晚自习当天 / 隔天补结算是常态，给一个月窗口足够补漏，
    #       再早就该当历史归档、不允许凭空补扣分（防误操作 / 滥用刷扣分）。
    today_jst = _today_jst()
    if today > today_jst:
        raise HTTPException(
            422,
            {
                "code": "TARGET_DATE_FUTURE",
                "message": "未来の日付は結算できません",
            },
        )
    if today < today_jst - timedelta(days=30):
        raise HTTPException(
            422,
            {
                "code": "TARGET_DATE_TOO_OLD",
                "message": "30 日より前の日付は結算できません",
            },
        )

    term = _academic_term(today)

    # R4 寮边界：先拉全 roster，再按老师管辖寮过滤（跨寮角色 None → 不过滤）
    # 演示隔离：join Student 加 demo_scope — 真老师只结算真实学生、演示老师只结算演示学生
    all_roster_ids = set(
        db.scalars(
            select(models.StudyRoster.student_id)
            .join(models.Student, models.Student.id == models.StudyRoster.student_id)
            .where(
                models.StudyRoster.academic_term == term,
                models.StudyRoster.removed_at.is_(None),
                demo_scope_for_teacher(teacher),
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

    # 收 (student_id, 这名学生今日的 StudyCheckin 行) —— 扣分的 source_event_id 要指向这条
    # checkin 的 id（不再是 None），后续 PATCH / 重新签到把 absent 改成 present/late 时，
    # 才能按 source_event_id 精确撤销对应这条扣分、不误撤别天 / 别次的 study_absent。
    to_absent: list[tuple[UUID, models.StudyCheckin]] = []
    for sid in roster_ids:
        if sid in exempt_ids:
            continue
        c = existing_map.get(sid)
        if c is None:
            # 新規 absent 行
            c = models.StudyCheckin(
                student_id=sid,
                target_date=today,
                status="absent",
                recorded_by=teacher.id,
            )
            db.add(c)
            to_absent.append((sid, c))
        elif c.status == "init":
            c.status = "absent"
            c.recorded_by = teacher.id
            to_absent.append((sid, c))

    # 先 flush 让新建的 StudyCheckin 拿到自增主键 id（下面扣分要引用 c.id）。
    # 新建 checkin 若撞 uq_sc_date（同学生同日已有行的并发竞态）→ 捕获回滚干净返回，
    # 不让整批结算 500。
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "FINALIZE_CONFLICT",
                "message": "結算中に競合が発生しました。再度お試しください",
            },
        )

    # spec §7.5 学習欠席自动扣 1.5 点（propose §1.2 默认值）
    # finalize 老师 = created_by（不是 None — 老师按了「学習終了」是手动触发）
    month = today.strftime("%Y-%m")
    for sid, c in to_absent:
        # 逐条 SAVEPOINT：撞 uq_demerit_source（该生本场 study_absent 扣分已存在 ——
        # 并发重复结算 / 重新结算）时只回滚这条、跳过，不波及整批与已写的 checkin。
        try:
            with db.begin_nested():
                db.add(
                    models.DemeritEvent(
                        student_id=sid,
                        source_type="study_absent",
                        source_event_id=c.id,
                        points=STUDY_ABSENT_POINTS,
                        reason=f"学習欠席（{today.isoformat()}）",
                        month=month,
                        created_by_teacher_id=teacher.id,
                    )
                )
        except IntegrityError:
            pass

    db.commit()

    absent_students = [{"student_id": str(sid)} for sid, _ in to_absent]
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    record = db.get(models.StudyCheckin, checkin_id)
    if not record:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "記録が見つかりません"}
        )
    # R4 寮边界：通过 checkin 记录找到对应学生，校验老师管辖范围
    student = db.get(models.Student, record.student_id)
    if student:
        # 演示隔离：演示老师只能改演示学生记录、真老师只能改真实学生记录（否则 404）
        assert_student_demo_match(teacher, student)
        _assert_student_in_dorm(teacher, student)

    old_status = record.status
    new_status = body.status

    # 扣分联动：手动修正改变出席状态时，study_absent 扣分要跟着撤 / 加（按本 checkin 行 id 精确定位）。
    # - absent → present/late/exempt：撤掉这条 checkin 对应的缺席扣分。
    # - 非 absent → absent：补记一条缺席扣分（如老师事后改判为缺席）；
    #   用 SAVEPOINT 容忍 uq_demerit_source（已存在该行时跳过、不 500）。
    if old_status == "absent" and new_status != "absent":
        _revoke_study_absent_demerit(db, record, teacher.id)
    elif old_status != "absent" and new_status == "absent":
        # 重新判缺席：先找本 checkin 既有的 study_absent 扣分（含已撤销的 —— 唯一约束不区分 revoked）。
        # 有则复活（清 revoked_*）、无则 INSERT。否则「缺席→出席→再缺席」回归路径下，旧软删行还占着
        # 唯一键，直接 INSERT 会撞约束被静默吞掉、扣分漏记。
        month = record.target_date.strftime("%Y-%m")
        existing = db.scalar(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == record.student_id,
                models.DemeritEvent.source_type == "study_absent",
                models.DemeritEvent.source_event_id == record.id,
            )
        )
        if existing is not None:
            existing.points = STUDY_ABSENT_POINTS
            existing.reason = f"学習欠席（{record.target_date.isoformat()}・手動修正）"
            existing.month = month
            existing.created_by_teacher_id = teacher.id
            existing.revoked_at = None
            existing.revoked_by_teacher_id = None
            existing.revoke_reason = None
        else:
            db.add(
                models.DemeritEvent(
                    student_id=record.student_id,
                    source_type="study_absent",
                    source_event_id=record.id,
                    points=STUDY_ABSENT_POINTS,
                    reason=f"学習欠席（{record.target_date.isoformat()}・手動修正）",
                    month=month,
                    created_by_teacher_id=teacher.id,
                )
            )

    record.status = new_status
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

    # 并发兜底：上面的重复预查与本次 INSERT 之间若有并发提交先建了同 (student, date) 行，
    # 本次 INSERT 撞 uq_sar_date 唯一约束 → 回滚后干净返 409，不冒泡成 500。
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "DUPLICATE_REQUEST",
                "message": "この日の欠席届は既に提出済みです",
            },
        )

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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.VIEW)
    ),
):
    # 演示隔离：join Student 加 demo_scope，让真老师只看真实学生的欠席届 /
    # 演示老师只看演示学生的欠席届（否则演示老师能读到真实学生提交的欠席届）。
    stmt = (
        select(models.StudyAbsenceRequest)
        .join(
            models.Student,
            models.Student.id == models.StudyAbsenceRequest.student_id,
        )
        .where(demo_scope_for_teacher(teacher))
        .order_by(models.StudyAbsenceRequest.submitted_at.asc())
    )
    if target_date:
        stmt = stmt.where(models.StudyAbsenceRequest.target_date == target_date)
    if status_filter:
        stmt = stmt.where(models.StudyAbsenceRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.StudyAbsenceRequestOut.model_validate(r) for r in rows]


# ---------------------------------------------------------------
# GET /study/absence-requests/me/summary — 当前学生当月请假次数 (学生, IX-034)
# ---------------------------------------------------------------
@router.get(
    "/absence-requests/me/summary",
    response_model=schemas.MyAbsenceSummaryOut,
)
def get_my_absence_summary(
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """当前登录学生的当月学習欠席届次数（iOS 当前用户统计，IX-034）。

    口径：按 target_date（请假针对的日期）落在 JST 当月计数，数全部状态
    （pending / approved / rejected）—— 与 iOS 现有「提交即 +1」行为一致。
    学習欠席届无撤销机制（唯一约束保证每天每人最多一条），故不排除任何状态。
    """
    now = _now_jst()
    month = now.strftime("%Y-%m")
    first = date(now.year, now.month, 1)
    nxt = (
        date(now.year + 1, 1, 1)
        if now.month == 12
        else date(now.year, now.month + 1, 1)
    )
    rows = db.scalars(
        select(models.StudyAbsenceRequest).where(
            models.StudyAbsenceRequest.student_id == student.id,
            models.StudyAbsenceRequest.target_date >= first,
            models.StudyAbsenceRequest.target_date < nxt,
        )
    ).all()
    return schemas.MyAbsenceSummaryOut(month=month, count=len(rows))


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
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    record = db.get(models.StudyAbsenceRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})
    # 演示隔离：审批间接关联学生 → 取届对应学生判 demo（演示老师只能审演示学生的届）
    student = db.get(models.Student, record.student_id)
    if student:
        assert_student_demo_match(teacher, student)
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
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    """今日の学習を中止 = 全 roster 学生を 'exempt' に一括設定。"""
    # 演示隔离：全 roster 批量取消影响一组学生、无法按单个学生判 demo → 演示老师整体禁止
    if teacher.is_demo:
        raise HTTPException(
            403,
            {"code": "DEMO_READONLY", "message": "デモアカウントは操作できません"},
        )

    today = _today_jst()
    term = _academic_term(today)

    # 演示隔离：join Student 加 demo_scope — 真老师只取消真实学生、演示老师只取消演示学生
    roster_ids = list(
        db.scalars(
            select(models.StudyRoster.student_id)
            .join(models.Student, models.Student.id == models.StudyRoster.student_id)
            .where(
                models.StudyRoster.academic_term == term,
                models.StudyRoster.removed_at.is_(None),
                demo_scope_for_teacher(teacher),
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
# 学習対象名簿 管理（杭田 2026-06-04 需求「五-2」）
# GET    /study/roster        — 当前名簿在籍者一览（学習担当 / 寮務管理）
# POST   /study/roster        — 把一名学生加入名簿（added_by = 当前老师）
# DELETE /study/roster/{sid}  — 把一名学生移出名簿（软删 removed_at = now）
# ---------------------------------------------------------------
# 名簿管理角色 gate — 跟 bulk-finalize / 欠席届承認 同一组（学習担当 + 寮務管理层）
_ROSTER_ROLES = ("学習担当", "寮務部長", "寮務課長", "寮監")


@router.get("/roster", response_model=list[schemas.StudyRosterEntryOut])
def list_roster(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.VIEW)
    ),
):
    """当前学期名簿在籍者一览 — 给老师网页「学習対象名簿管理」页用。

    口径：removed_at 为空（在籍中）+ 当前学期。带学生姓名 / 房间 / 寮，
    并按 R4 寮边界过滤掉老师管辖外的学生（跨寮角色看全部）。
    """
    today = target_date or _today_jst()
    term = _academic_term(today)

    roster_rows = db.scalars(
        select(models.StudyRoster).where(
            models.StudyRoster.academic_term == term,
            models.StudyRoster.removed_at.is_(None),
        )
    ).all()
    if not roster_rows:
        return []

    student_ids = [r.student_id for r in roster_rows]
    # 演示隔离：真老师只取真实学生 / 演示老师只取演示学生。
    # student_map 缺该学生时下面 for 循环 continue 跳过，等于把异 cohort 名簿行过滤掉。
    students = db.scalars(
        select(models.Student).where(
            models.Student.id.in_(student_ids),
            demo_scope_for_teacher(teacher),
        )
    ).all()
    student_map = {s.id: s for s in students}

    # R4 寮边界：跨寮角色 dorm_units 为 None → 不过滤；dorm-scoped 角色只看管辖寮
    allowed = dorm_units_for_teacher(teacher)

    out: list[schemas.StudyRosterEntryOut] = []
    for r in roster_rows:
        s = student_map.get(r.student_id)
        if not s:
            continue
        if allowed is not None and s.dorm_unit not in allowed:
            continue
        out.append(
            schemas.StudyRosterEntryOut(
                student_id=s.id,
                student_no=s.student_no,
                name=s.name,
                room_no=s.room_no,
                dorm_unit=s.dorm_unit,
                academic_term=r.academic_term,
                added_by=r.added_by,
                added_at=r.added_at,
            )
        )
    out.sort(key=lambda e: e.name)
    return out


@router.post("/roster", response_model=schemas.StudyRosterEntryOut, status_code=201)
def add_to_roster(
    body: schemas.StudyRosterAddIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    """把一名学生加入当前学期名簿。

    - 学生不存在 → 404
    - R4 寮边界：dorm-scoped 角色不能加管辖外学生 → 403
    - 唯一约束 uq_roster_term(student_id, academic_term)：若已有「同学期 + 同学生」的旧行，
      不新建（会撞唯一约束），改为「复活」= removed_at 置回 None + 更新 added_by；
      若该行本就在籍（removed_at 为空）→ 409 已在籍。

    可用 student_id（UUID）或 student_no（6 位学号 = 年级 2 + 班级 2 + 座号 2）指定学生，
    学号由 grade_code + class_code + seat_no 拼成（model 上是 derived property、不是列），
    故按这三段拆开查。
    """
    today = _today_jst()
    term = _academic_term(today)

    student = _resolve_roster_student(db, body)
    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # 演示隔离：演示老师只能把演示学生加进名簿、真老师只能加真实学生（否则 404）
    assert_student_demo_match(teacher, student)

    # R4 寮边界：寮監等 dorm-scoped 角色不能给管辖外学生操作名簿
    _assert_student_in_dorm(teacher, student)

    # 查同学期同学生的既存行（唯一约束限定每学期每人最多一行）
    # 注意：用解析出来的 student.id（不是 body.student_id —— 按学号加入时 body.student_id 为空）
    existing = db.scalars(
        select(models.StudyRoster).where(
            models.StudyRoster.student_id == student.id,
            models.StudyRoster.academic_term == term,
        )
    ).first()

    if existing is not None:
        if existing.removed_at is None:
            raise HTTPException(
                409,
                {"code": "ALREADY_IN_ROSTER", "message": "既に名簿に登録済みです"},
            )
        # 复活：把已移出的旧行重新置为在籍，避免撞唯一约束新建第二行
        existing.removed_at = None
        existing.added_by = teacher.id
        existing.added_at = _now_jst()
        record = existing
    else:
        record = models.StudyRoster(
            student_id=student.id,
            academic_term=term,
            added_by=teacher.id,
        )
        db.add(record)

    # 并发双保护：两个请求同时把同一 (student_id, term) 加进名簿时，都查到「无既存行」
    # 双双走 INSERT，第二个 flush 撞 uq_roster_term 唯一约束。捕获后回滚 + 干净返 409，
    # 不让它冒泡成 500（与 teachers.py 的唯一性预查 + IntegrityError 双保护一致）。
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "ALREADY_IN_ROSTER", "message": "既に名簿に登録済みです"},
        )

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="study_roster.add",
            target_type="study_roster",
            target_id=record.id,
            payload={
                "student_id": str(student.id),
                "academic_term": term,
                "revived": existing is not None,
            },
        )
    )

    db.commit()
    db.refresh(record)
    return schemas.StudyRosterEntryOut(
        student_id=student.id,
        student_no=student.student_no,
        name=student.name,
        room_no=student.room_no,
        dorm_unit=student.dorm_unit,
        academic_term=record.academic_term,
        added_by=record.added_by,
        added_at=record.added_at,
    )


@router.delete("/roster/{student_id}", status_code=200)
def remove_from_roster(
    student_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDY, permissions.MANAGE)
    ),
):
    """把一名学生移出当前学期名簿 — 软删（removed_at 置 now），不物理删除。

    - 学生不存在 / 该学生当前学期不在名簿（无在籍行）→ 404
    - R4 寮边界：dorm-scoped 角色不能移管辖外学生 → 403
    """
    today = _today_jst()
    term = _academic_term(today)

    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # 演示隔离：演示老师只能移演示学生、真老师只能移真实学生（否则 404）
    assert_student_demo_match(teacher, student)

    # R4 寮边界：先校验老师能不能操作这个学生
    _assert_student_in_dorm(teacher, student)

    record = db.scalars(
        select(models.StudyRoster).where(
            models.StudyRoster.student_id == student_id,
            models.StudyRoster.academic_term == term,
            models.StudyRoster.removed_at.is_(None),
        )
    ).first()
    if record is None:
        raise HTTPException(
            404,
            {"code": "NOT_IN_ROSTER", "message": "この学生は名簿に登録されていません"},
        )

    record.removed_at = _now_jst()
    db.flush()

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="study_roster.remove",
            target_type="study_roster",
            target_id=record.id,
            payload={"student_id": str(student_id), "academic_term": term},
        )
    )

    db.commit()
    return {"removed": True, "student_id": str(student_id), "academic_term": term}


# ---------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------
def _revoke_study_absent_demerit(
    db: Session,
    checkin: models.StudyCheckin,
    teacher_id: UUID,
) -> None:
    """学習欠席扣分の撤销 —— 学生が absent 判定後に出席（present / late）へ変わった時に呼ぶ。

    finalize 写缺席扣分时 source_event_id = 这条 StudyCheckin 的 id，故按 source_event_id
    精确定位本场欠席扣分撤销，不会误撤别天 / 别次的 study_absent。软删（保留 revoked_*）。
    一行 checkin 对应至多一条未撤销 study_absent 扣分，循环以防历史脏数据有多条。
    """
    rows = db.scalars(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == checkin.student_id,
            models.DemeritEvent.source_type == "study_absent",
            models.DemeritEvent.source_event_id == checkin.id,
            models.DemeritEvent.revoked_at.is_(None),
        )
    ).all()
    for ev in rows:
        ev.revoked_at = _now_jst()
        ev.revoked_by_teacher_id = teacher_id
        ev.revoke_reason = "学習出席に変更され欠席扣分を撤销"


def _resolve_roster_student(
    db: Session, body: schemas.StudyRosterAddIn
) -> Optional[models.Student]:
    """把名簿加入请求里的 student_id 或 student_no 解析成 Student 行。

    优先用 student_id（UUID 直查）；没有就按 student_no 6 位拆成
    年级 2 + 班级 2 + 座号 2 查（student_no 是 model 的 derived property 不是列，不能直接等值查）。
    解析不到返回 None（调用方转 404）。
    """
    if body.student_id is not None:
        return db.get(models.Student, body.student_id)
    no = (body.student_no or "").strip()
    if len(no) != 6:
        return None
    grade, klass, seat = no[0:2], no[2:4], no[4:6]
    return db.scalars(
        select(models.Student).where(
            models.Student.grade_code == grade,
            models.Student.class_code == klass,
            models.Student.seat_no == seat,
        )
    ).first()


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
        # 演示隔离：按欠席届学生 is_demo 选老师 — 演示学生通知演示老师、真实学生通知真老师
        teachers = db.scalars(
            select(models.Teacher).where(
                models.Teacher.role == "学習担当",
                models.Teacher.status == "active",
                models.Teacher.is_demo == student.is_demo,
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
