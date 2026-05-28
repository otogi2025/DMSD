"""出寮届 endpoint (#2 #5 #6 #10-#13 修改届 audit).

POST /api/v1/applications                        — 提出 (帰省 / 外泊 / 帰国)
GET  /api/v1/applications/mine                   — 自分の履歴
GET  /api/v1/applications/pending-for-me         — 役職: 自分が承認待ちの一覧
GET  /api/v1/applications/{id}                   — #5 承认状态查询
PUT  /api/v1/applications/{id}                   — 修改届 (pending 中のみ、chain リセット)
GET  /api/v1/applications/{id}/audit             — 審査 audit ログ
POST /api/v1/applications/{id}/approvals         — #10 役職承認/拒否
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas, ws_manager as _ws
from ..database import get_db
from ..deps import get_current_student, get_current_teacher
from ..services import approval_chain, email as email_svc

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


# ---------------------------------------------------------------
# POST /applications — #1 #2 #3 #4 + #6 メール送信
# ---------------------------------------------------------------
@router.post(
    "",
    response_model=schemas.ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    body: schemas.ApplicationCreateIn,
    response: Response,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    # (#3) 出寮日 = 明天起 — 教师当日代録は P1 範囲外、本 endpoint は学生のみ
    if body.leave_date <= date_type.today():
        raise HTTPException(
            status_code=422,
            detail={
                "code": "LEAVE_DATE_NOT_FUTURE",
                "message": "出寮日は明日以降を指定してください",
            },
        )

    # (#1) 学生は自分の届しか出せない (deps から student 取れているので自動的に own)
    # → body に student_id を含めない設計、サーバ側で current student を bind

    app_kwargs = {
        "student_id": student.id,
        "kind": body.kind,
        "reason": body.reason,
        "leave_date": body.leave_date,
        "leave_method": body.leave_method,
        "leave_time": body.leave_time,
        "return_date": body.return_date,
        "return_method": body.return_method,
        "return_time": body.return_time,
        "contact_phone": body.contact_phone,
        "meal_note": body.meal_note,
        "status": "pending",
    }
    if isinstance(body, schemas.KisheiCreateIn):
        app_kwargs.update(is_long_vacation=body.is_long_vacation)
    elif isinstance(body, schemas.GaihakuCreateIn):
        app_kwargs.update(
            stay_locations=[loc.model_dump() for loc in body.stay_locations],
            meals_skip=[e.model_dump(mode="json") for e in body.meals_skip] or None,
            companion=body.companion,
            dest_cities=body.dest_cities,
        )
    elif isinstance(body, schemas.KikokuCreateIn):
        app_kwargs.update(
            stay_locations=[loc.model_dump() for loc in body.stay_locations],
            meals_skip=[e.model_dump(mode="json") for e in body.meals_skip] or None,
            companion=body.companion,
            dest_cities=body.dest_cities,
            flight_dep_air=body.flight_dep_air,
            flight_dep_at=body.flight_dep_at,
            flight_arr_air=body.flight_arr_air,
            flight_arr_at=body.flight_arr_at,
        )

    application = models.Application(**app_kwargs)
    application.student = student  # eager bind for chain build
    db.add(application)
    db.flush()

    # 承认 chain 行作成 (D4 实物表)
    approval_chain.build_chain(db, application)

    # 邮件通知 (#6 R1)
    teachers, to_emails = approval_chain.collect_recipients(db, application)
    notification_log = email_svc.send_application_submitted(
        db,
        application=application,
        student=student,
        teachers=teachers,
        to_emails=to_emails,
    )

    # audit
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="application.submit",
            target_type="application",
            target_id=application.id,
            payload={
                "kind": application.kind,
                "notification_log_id": str(notification_log.id),
            },
        )
    )

    db.commit()
    db.refresh(application)

    # WS broadcast — 老师端 ApplicationsPage 实时 pending 计数 + toast
    _ws.manager.broadcast_sync(
        {
            "type": "outstay_new",
            "application_id": str(application.id),
            "student_id": str(student.id),
            "kind": application.kind,
            "leave_date": application.leave_date.isoformat(),
            "return_date": application.return_date.isoformat(),
            "student_name": student.name,
        }
    )

    # evidence pending な chain は header に警告
    if approval_chain.is_provisional(application.kind, student.is_overseas):
        response.headers["X-Approval-Chain-Provisional"] = "true"

    return _to_application_out(application)


# ---------------------------------------------------------------
# GET /applications/mine — 学生 自分の履歴
# ---------------------------------------------------------------
@router.get("/mine", response_model=list[schemas.ApplicationOut])
def list_mine(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.Application)
        .where(models.Application.student_id == student.id)
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
        .order_by(models.Application.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.Application.status == status_filter)
    apps = db.scalars(stmt).all()
    return [_to_application_out(a) for a in apps]


# ---------------------------------------------------------------
# GET /applications/pending-for-me — 役職: 自分が承認待ちの一覧 (#10)
#
# A-013 (2026-05-21): 必须在 /{application_id} 之前注册
# FastAPI 按注册顺序匹配；静态路径在前 / 动态路径在后，否则 "pending-for-me"
# 会被当成 UUID 解析 → 422 错误。
# ---------------------------------------------------------------
@router.get("/pending-for-me", response_model=list[schemas.ApplicationOut])
def list_pending_for_me(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    """当前役职 (teacher.role) が未決の application_approvals を持つ届を返す。"""
    from sqlalchemy import and_

    stmt = (
        select(models.Application)
        .join(
            models.ApplicationApproval,
            and_(
                models.ApplicationApproval.application_id == models.Application.id,
                models.ApplicationApproval.approver_role == teacher.role,
                models.ApplicationApproval.decision.is_(None),
            ),
        )
        # 永远 join Student 用于 is_demo 过滤（reviewer 学生提交的申请不应出现在老师面板）
        .join(
            models.Student,
            models.Student.id == models.Application.student_id,
        )
        .where(
            models.Application.status.in_(["pending", "approved_partial"]),
            models.Student.is_demo.is_(False),
        )
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
        .order_by(models.Application.submitted_at.asc())
    )
    # R4 dorm filter（join 已在上面加了，这里只追加 where）
    if teacher.assigned_dorm is not None and teacher.role not in {
        "校長",
        "寮務部長",
        "寮務課長",
        "国際交流部長",
        "国際交流課長",
        "管理係",
    }:
        if teacher.assigned_dorm == 1:
            stmt = stmt.where(models.Student.dorm_unit.in_([1, 2]))
        else:
            stmt = stmt.where(models.Student.dorm_unit == teacher.assigned_dorm)
    apps = db.scalars(stmt).all()
    return [_to_application_out(a) for a in apps]


# ---------------------------------------------------------------
# GET /applications/{id} — #5 承认状态查询
# ---------------------------------------------------------------
@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    # 学生 / 教师 両対応の認証 → サブ関数で
    actor = _resolve_actor(db, authorization)

    app = db.scalars(
        select(models.Application)
        .where(models.Application.id == application_id)
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
    ).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "届が見つかりません"},
        )

    # 学生 → 自分のみ。教师 → assigned_dorm 一致 or 跨寮 role
    if isinstance(actor, models.Student):
        if app.student_id != actor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "他人の届は閲覧できません"},
            )
    elif isinstance(actor, models.Teacher):
        if not _teacher_can_view(actor, app.student):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN_DORM", "message": "担当外の寮の届です"},
            )

    return _to_application_out(app)


# ---------------------------------------------------------------
# 補助
# ---------------------------------------------------------------
def _resolve_actor(
    db: Session, authorization: str | None
) -> models.Student | models.Teacher:
    """学生 token と 教师 token どちらでも 受け付ける。"""
    from .. import security as sec

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "ログインが必要です"},
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = sec.decode_token(token)
    except sec.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効"},
        )
    role = payload.get("role", "")
    sub = UUID(payload["sub"])
    if role == "student":
        s = db.get(models.Student, sub)
        if not s:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント無効"},
            )
        return s
    if role.startswith("teacher:"):
        t = db.get(models.Teacher, sub)
        if not t:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント無効"},
            )
        return t
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_CREDENTIALS", "message": "未知の token role"},
    )


def _teacher_can_view(teacher: models.Teacher, student: models.Student) -> bool:
    # 跨寮 role
    if teacher.role in {
        "校長",
        "寮務部長",
        "寮務課長",
        "国際交流部長",
        "国際交流課長",
        "管理係",
    }:
        return True
    # assigned_dorm = 1 → 男寮 (1+2 暗指)
    if teacher.assigned_dorm is None:
        return True
    if teacher.assigned_dorm == 1 and student.dorm_unit in (1, 2):
        return True
    if teacher.assigned_dorm == student.dorm_unit:
        return True
    return False


# A-013 (2026-05-21): GET /applications/pending-for-me 已移到 /{application_id} 之前。


# ---------------------------------------------------------------
# PUT /applications/{id} — 修改届 (pending 中のみ、chain リセット + 再メール)
# ---------------------------------------------------------------
@router.put("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: UUID,
    body: schemas.ApplicationUpdateIn,
    response: Response,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    app = db.scalars(
        select(models.Application)
        .where(models.Application.id == application_id)
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
    ).first()
    if not app:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})
    if app.student_id != student.id:
        raise HTTPException(
            403, {"code": "FORBIDDEN", "message": "他人の届は修正できません"}
        )
    if app.status not in ("pending", "approved_partial"):
        raise HTTPException(
            409,
            {"code": "CANNOT_MODIFY", "message": "承認済 / 拒否済の届は修正できません"},
        )

    # 内容更新 (None フィールドはスキップ)
    update_data = body.model_dump(exclude_none=True)
    if "stay_locations" in update_data:
        update_data["stay_locations"] = [
            loc.model_dump() for loc in body.stay_locations
        ]
    if "meals_skip" in update_data:
        update_data["meals_skip"] = [
            e.model_dump(mode="json") for e in body.meals_skip
        ] or None
    for key, val in update_data.items():
        setattr(app, key, val)

    if body.leave_date and body.leave_date <= date_type.today():
        raise HTTPException(
            422, {"code": "LEAVE_DATE_NOT_FUTURE", "message": "出寮日は明日以降"}
        )

    # chain リセット — 全 approvals 削除 → 再生成
    for row in app.approvals:
        db.delete(row)
    db.flush()
    approval_chain.build_chain(db, app)

    # 再メール (chain 変わった可能性があるので再送)
    teachers, to_emails = approval_chain.collect_recipients(db, app)
    email_svc.send_application_submitted(
        db, application=app, student=student, teachers=teachers, to_emails=to_emails
    )

    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="application.update",
            target_type="application",
            target_id=app.id,
            payload={"updated_fields": list(update_data.keys())},
        )
    )
    db.commit()
    db.refresh(app)

    if approval_chain.is_provisional(app.kind, student.is_overseas):
        response.headers["X-Approval-Chain-Provisional"] = "true"
    return _to_application_out(app)


# ---------------------------------------------------------------
# GET /applications/{id}/audit — 審査 audit ログ
# ---------------------------------------------------------------
@router.get("/{application_id}/audit", response_model=list[schemas.AuditLogOut])
def get_application_audit(
    application_id: UUID,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    # 学生 or 教師 両対応
    actor = _resolve_actor(db, authorization)

    app = db.get(models.Application, application_id)
    if not app:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})

    if isinstance(actor, models.Student) and app.student_id != actor.id:
        raise HTTPException(
            403, {"code": "FORBIDDEN", "message": "他人の届は閲覧できません"}
        )

    logs = db.scalars(
        select(models.AuditLog)
        .where(
            models.AuditLog.target_type == "application",
            models.AuditLog.target_id == application_id,
        )
        .order_by(models.AuditLog.created_at.asc())
    ).all()
    return [schemas.AuditLogOut.model_validate(log) for log in logs]


# ---------------------------------------------------------------
# POST /applications/{id}/approvals — #10 役職承認/拒否
# ---------------------------------------------------------------
@router.post("/{application_id}/approvals", response_model=schemas.ApplicationOut)
def decide_approval(
    application_id: UUID,
    body: schemas.ApprovalIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    app = db.scalars(
        select(models.Application)
        .where(models.Application.id == application_id)
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
    ).first()
    if not app:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})

    # 当前役職の pending 行を探す
    pending_row = next(
        (
            r
            for r in app.approvals
            if r.approver_role == teacher.role and r.decision is None
        ),
        None,
    )
    if not pending_row:
        # 既に決定済か、この役職は chain に含まれない
        already = next(
            (
                r
                for r in app.approvals
                if r.approver_role == teacher.role and r.decision is not None
            ),
            None,
        )
        if already:
            raise HTTPException(
                409,
                {"code": "APPROVAL_ALREADY_DECIDED", "message": "すでに決定済みです"},
            )
        raise HTTPException(
            403,
            {
                "code": "APPROVAL_NOT_REQUIRED",
                "message": "この役職は対象の承認者ではありません",
            },
        )

    from datetime import timezone as tz

    pending_row.approver_id = teacher.id
    pending_row.decision = body.decision
    pending_row.comment = body.comment
    pending_row.decided_at = datetime.now(tz.utc)

    # application.status 自動更新
    _recompute_application_status(app)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action=f"application.{body.decision}",
            target_type="application",
            target_id=app.id,
            payload={"role": teacher.role, "comment": body.comment},
        )
    )
    db.commit()
    db.refresh(app)
    return _to_application_out(app)


def _recompute_application_status(app: models.Application) -> None:
    """全 approval 行を見て application.status を更新 (DB flush 前に呼ぶ)。"""
    decisions = [r.decision for r in app.approvals]
    if any(d == "reject" for d in decisions):
        app.status = "rejected"
    elif all(d == "approve" for d in decisions):
        app.status = "approved"
    elif any(d == "approve" for d in decisions):
        app.status = "approved_partial"
    else:
        app.status = "pending"


def _to_application_out(app: models.Application) -> schemas.ApplicationOut:
    chain = [
        schemas.ApprovalStepOut(
            approver_role=row.approver_role,
            decision=row.decision,
            decided_at=row.decided_at,
            comment=row.comment,
            approver_id=row.approver_id,
        )
        for row in (app.approvals or [])
    ]
    student_brief = None
    if app.student:
        student_brief = schemas.StudentBrief(
            id=app.student.id,
            student_no=app.student.student_no,
            name=app.student.name,
            dorm_unit=app.student.dorm_unit,
            is_overseas=app.student.is_overseas,
            room_no=app.student.room_no,
        )
    return schemas.ApplicationOut(
        id=app.id,
        student_id=app.student_id,
        student=student_brief,
        kind=app.kind,
        reason=app.reason,
        leave_date=app.leave_date,
        leave_method=app.leave_method,
        leave_time=app.leave_time,
        return_date=app.return_date,
        return_method=app.return_method,
        return_time=app.return_time,
        contact_phone=app.contact_phone,
        meal_note=app.meal_note,
        stay_locations=app.stay_locations,
        meals_skip=app.meals_skip,
        companion=app.companion,
        dest_cities=app.dest_cities,
        receipt_submitted=bool(app.receipt_submitted),
        flight_dep_air=app.flight_dep_air,
        flight_dep_at=app.flight_dep_at,
        flight_arr_air=app.flight_arr_air,
        flight_arr_at=app.flight_arr_at,
        bus_route_id=app.bus_route_id,
        is_long_vacation=bool(app.is_long_vacation),
        submitted_at=app.submitted_at,
        status=app.status,
        withdrawn_at=app.withdrawn_at,
        approval_chain=chain,
    )
