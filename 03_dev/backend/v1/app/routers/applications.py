"""出寮届 endpoint (#2 schema + #5 GET + #6 メール).

POST /api/v1/applications        — 提出 (帰省 / 外泊 / 帰国 discriminator)
GET  /api/v1/applications/mine   — 自分の履歴
GET  /api/v1/applications/{id}   — #5 承认状态查询
"""
from __future__ import annotations

from datetime import date as date_type
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
        "leave_date": body.leave_date,
        "leave_method": body.leave_method,
        "leave_time": body.leave_time,
        "return_date": body.return_date,
        "return_method": body.return_method,
        "return_time": body.return_time,
        "status": "pending",
    }
    if isinstance(body, schemas.GaihakuCreateIn):
        app_kwargs.update(
            stay_locations=[loc.model_dump() for loc in body.stay_locations],
            meals_skip_from=body.meals_skip_from,
            meals_skip_to=body.meals_skip_to,
        )
    elif isinstance(body, schemas.KikokuCreateIn):
        app_kwargs.update(
            stay_locations=[loc.model_dump() for loc in body.stay_locations],
            meals_skip_from=body.meals_skip_from,
            meals_skip_to=body.meals_skip_to,
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
            payload={"kind": application.kind, "notification_log_id": str(notification_log.id)},
        )
    )

    db.commit()
    db.refresh(application)

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
    if teacher.role in {"寮務部長", "寮務課長", "国際交流部長", "国際交流課長", "管理係"}:
        return True
    # assigned_dorm = 1 → 男寮 (1+2 暗指)
    if teacher.assigned_dorm is None:
        return True
    if teacher.assigned_dorm == 1 and student.dorm_unit in (1, 2):
        return True
    if teacher.assigned_dorm == student.dorm_unit:
        return True
    return False


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
        leave_date=app.leave_date,
        leave_method=app.leave_method,
        leave_time=app.leave_time,
        return_date=app.return_date,
        return_method=app.return_method,
        return_time=app.return_time,
        stay_locations=app.stay_locations,
        meals_skip_from=app.meals_skip_from,
        meals_skip_to=app.meals_skip_to,
        flight_dep_air=app.flight_dep_air,
        flight_dep_at=app.flight_dep_at,
        flight_arr_air=app.flight_arr_air,
        flight_arr_at=app.flight_arr_at,
        bus_route_id=app.bus_route_id,
        submitted_at=app.submitted_at,
        status=app.status,
        withdrawn_at=app.withdrawn_at,
        approval_chain=chain,
    )
