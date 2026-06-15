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

from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from .. import models, permissions, schemas, ws_manager as _ws
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    get_current_student,
    require_permission,
)
from ..services import approval_chain, email as email_svc

# 出寮届的终态 — 到这几个状态后不再接受任何承认/拒否（不可重新打开）。
# returned（退回）是学生可继续修改的中间状态，不算终态、不放进来。
_APPLICATION_TERMINAL_STATUSES = ("approved", "rejected", "withdrawn")


def _find_application_by_idempotency_key(
    db: Session, *, actor_type: str, actor_id: UUID, key: str
) -> Optional[models.Application]:
    """同一提交者 + 同一 Idempotency-Key 的提交 audit 已存在时，返回那条届（幂等去重）。

    Application 表不能加 idempotency_key 列（models.py 由别人负责），所以改用
    提交时写进 AuditLog.payload 的 idempotency_key 反查。重复 POST（重试 / 双击）
    时不会多生成届 + 审批链 + 邮件。没命中返回 None（继续走新建）。
    """
    log = db.scalars(
        select(models.AuditLog)
        .where(
            models.AuditLog.actor_type == actor_type,
            models.AuditLog.actor_id == actor_id,
            models.AuditLog.target_type == "application",
            models.AuditLog.action.in_(
                ["application.submit", "application.submit_by_teacher"]
            ),
            models.AuditLog.payload["idempotency_key"].as_string() == key,
        )
        .order_by(models.AuditLog.created_at.asc())
    ).first()
    if log is None:
        return None
    return db.scalars(
        select(models.Application)
        .where(models.Application.id == log.target_id)
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
    ).first()


_JST = ZoneInfo("Asia/Tokyo")

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
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    # 幂等：客户端传了 Idempotency-Key 且这个 key 之前提交过 → 直接返回那条届，
    # 不重复建届 / 审批链 / 发邮件（重试、双击会触发同 key 的重复 POST）。
    # 没传 key 就跳过、保持原行为（与改动前一致，不强制客户端必须传）。
    if idempotency_key and idempotency_key.strip():
        existing = _find_application_by_idempotency_key(
            db,
            actor_type="student",
            actor_id=student.id,
            key=idempotency_key.strip(),
        )
        if existing is not None:
            return _to_application_out(existing)

    # (#3) 出寮日 = 明天起 — 学生本人只能提明天起；老师当日代録走 /by-teacher
    if body.leave_date <= datetime.now(_JST).date():
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
        "taxi_reservation_time": body.taxi_reservation_time,
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
    _submit_payload = {
        "kind": application.kind,
        "notification_log_id": str(notification_log.id),
    }
    # 把幂等 key 写进 audit payload，重复提交时靠它反查到这条届（见 _find_application_by_idempotency_key）
    if idempotency_key and idempotency_key.strip():
        _submit_payload["idempotency_key"] = idempotency_key.strip()
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="application.submit",
            target_type="application",
            target_id=application.id,
            payload=_submit_payload,
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
        },
        student_is_demo=student.is_demo,
    )

    # evidence pending な chain は header に警告
    if approval_chain.is_provisional(application.kind, student.is_overseas):
        response.headers["X-Approval-Chain-Provisional"] = "true"

    return _to_application_out(application)


# ---------------------------------------------------------------
# POST /applications/by-teacher — 杭田 2026-06-04 五-3: 老师代学生当日补录
# ---------------------------------------------------------------
@router.post(
    "/by-teacher",
    response_model=schemas.ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_application_by_teacher(
    body: schemas.ApplicationCreateIn,
    student_id: UUID = Query(...),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    """老师代学生补录出寮届（杭田五-3「老师可代学生当日补录」）。

    与学生自助提交 POST /applications 的区别：
    ① 鉴权需「申请审批」权限；② student_id 由老师指定（受 R4 寮边界）；
    ③ 允许当日（leave_date >= 今天，仅禁过去日；学生侧必须明天以后）。
    其余（审批链 / 提交邮件通知 / WebSocket 推送）与学生提交完全一致。
    """
    # 幂等：同 create_application — 老师重复 POST（重试 / 双击）同一 key 时返回已存届，
    # 不重复建届 + 审批链 + 邮件。这里幂等以老师为 actor（actor_type=teacher）。
    if idempotency_key and idempotency_key.strip():
        existing = _find_application_by_idempotency_key(
            db,
            actor_type="teacher",
            actor_id=teacher.id,
            key=idempotency_key.strip(),
        )
        if existing is not None:
            return _to_application_out(existing)

    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )

    # 演示写隔离：演示老师只能给演示学生代録、真老师只能给真实学生（否则当 404）
    assert_student_demo_match(teacher, student)

    # R4 寮边界：老师只能给管辖寮的学生代録
    if not _teacher_can_view(teacher, student):
        raise HTTPException(
            403, {"code": "FORBIDDEN_DORM", "message": "担当外の寮の学生です"}
        )

    # 老师代録放宽到当日（学生侧禁当日），但仍禁过去日
    if body.leave_date < datetime.now(_JST).date():
        raise HTTPException(
            422,
            {
                "code": "LEAVE_DATE_PAST",
                "message": "出寮日は本日以降を指定してください",
            },
        )

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
        "taxi_reservation_time": body.taxi_reservation_time,
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
    application.student = student
    db.add(application)
    db.flush()

    approval_chain.build_chain(db, application)
    teachers, to_emails = approval_chain.collect_recipients(db, application)
    notification_log = email_svc.send_application_submitted(
        db,
        application=application,
        student=student,
        teachers=teachers,
        to_emails=to_emails,
    )

    _submit_payload = {
        "kind": application.kind,
        "student_id": str(student.id),
        "notification_log_id": str(notification_log.id),
    }
    # 把幂等 key 写进 audit payload，重复提交时靠它反查到这条届（见 _find_application_by_idempotency_key）
    if idempotency_key and idempotency_key.strip():
        _submit_payload["idempotency_key"] = idempotency_key.strip()
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="application.submit_by_teacher",
            target_type="application",
            target_id=application.id,
            payload=_submit_payload,
        )
    )
    db.commit()
    db.refresh(application)

    _ws.manager.broadcast_sync(
        {
            "type": "outstay_new",
            "application_id": str(application.id),
            "student_id": str(student.id),
            "kind": application.kind,
            "leave_date": application.leave_date.isoformat(),
            "return_date": application.return_date.isoformat(),
            "student_name": student.name,
        },
        student_is_demo=student.is_demo,
    )

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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
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
            demo_scope_for_teacher(teacher),
        )
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
        .order_by(models.Application.submitted_at.asc())
    )
    # 寮过滤已取消（itsuki 2026-06-13）：所有老师看所有寮的待审申请。
    apps = db.scalars(stmt).all()
    return [_to_application_out(a) for a in apps]


# ---------------------------------------------------------------
# GET /applications/active — 杭田 2026-06-04 四: 事務室 PC 出寮者一覧
# 静态路径 → 必须在动态 /{id} 之前注册，否则 "active" 被当 UUID 解析。
# ---------------------------------------------------------------
@router.get("/active", response_model=list[schemas.ApplicationOut])
def list_active_leaves(
    on_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    """事務室 PC 用「現在出寮中の学生一覧」（只读汇总）。

    指定日（默认 = 本日 JST）出寮中 = status='approved' 且
    leave_date <= 指定日 <= return_date 的届。approved_partial（部分通过）
    还没获准、不计入。按 R4 寮边界过滤，前端再分 1,2寮 / 4寮 两块显示
    （没有编辑接口 = 防误删）。
    """
    target = on_date or datetime.now(_JST).date()
    stmt = (
        select(models.Application)
        .join(
            models.Student,
            models.Student.id == models.Application.student_id,
        )
        .where(
            models.Application.status == "approved",
            models.Application.leave_date <= target,
            models.Application.return_date >= target,
            demo_scope_for_teacher(teacher),
        )
        .options(
            selectinload(models.Application.approvals),
            selectinload(models.Application.student),
        )
        .order_by(
            models.Student.dorm_unit.asc(),
            models.Application.leave_date.asc(),
        )
    )
    # 寮过滤已取消（itsuki 2026-06-13）：所有老师看所有寮的出寮中学生。
    apps = db.scalars(stmt).all()
    return [_to_application_out(a) for a in apps]


# ---------------------------------------------------------------
# GET /applications/proxy-candidates — 老师代録用「搜学生」（杭田五-3）
# ⚠️ 静态路由必须排在 /{application_id} 之前，否则会被当成 application_id
# ---------------------------------------------------------------
@router.get("/proxy-candidates", response_model=list[schemas.StudentBrief])
def list_proxy_candidates(
    q: Optional[str] = Query(None, description="姓名 or 学号 模糊搜"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    """老师代録出寮届时的学生选择器数据源（杭田五-3「老师可代学生当日补录」）。

    刻意不复用 admin 的 GET /students：那个还暴露账号锁定信息。这里权限与代録
    对齐（都需「申请审批」权限），只回精简字段（学号 / 姓名 / 寮 / 是否留学生 /
    房间），并按 R4 寮边界过滤——老师只能搜到自己管辖寮的学生。
    """
    stmt = select(models.Student).where(demo_scope_for_teacher(teacher))

    if q and q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            (models.Student.name.like(like))
            | (
                (
                    models.Student.grade_code
                    + models.Student.class_code
                    + models.Student.seat_no
                ).like(like)
            )
        )

    # 寮过滤已取消（itsuki 2026-06-13）：所有老师可搜到所有寮的学生。
    # limit 100：前端有搜索框，超 100 提示老师用姓名/学号筛选
    stmt = stmt.order_by(
        models.Student.grade_code,
        models.Student.class_code,
        models.Student.seat_no,
    ).limit(100)

    students = db.scalars(stmt).all()
    return [schemas.StudentBrief.model_validate(s) for s in students]


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
        # 演示读隔离：演示老师只能读演示学生的届、真老师只能读真实学生（否则当 404）。
        # 在寮边界前先判，防演示老师知道真实 UUID 就能读全文。
        if app.student is not None:
            assert_student_demo_match(actor, app.student)
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
        # 账号必须存在且 status=='active' — 停用 / 毕业 / 锁定 / 自删的学生哪怕手里还攥着
        # 没过期的 JWT 也不能再读届 / audit（与 ws.py 老师连接的 active 校验同一原则）。
        if not s or s.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント無効"},
            )
        return s
    if role.startswith("teacher:"):
        t = db.get(models.Teacher, sub)
        # 同上：停用（status=='disabled'）的老师即使持有效 JWT 也不能再读届 / audit。
        if not t or t.status != "active":
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
    # itsuki 2026-06-13 取消寮过滤：所有老师可查看所有学生（功能权限由权限组把关）。
    return True


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
    # returned(退回)= 老师退回让学生改，理应可编辑（spec §7.2.4-5）；改完下方会把 status 重置回 pending。
    if app.status not in ("pending", "approved_partial", "returned"):
        raise HTTPException(
            409,
            {"code": "CANNOT_MODIFY", "message": "承認済 / 拒否済の届は修正できません"},
        )

    # 内容更新 (None フィールドはスキップ)
    update_data = body.model_dump(exclude_none=True)
    # amend_reason 是「修改理由」、app 表没这列 — 取出来只写进 audit。
    # codex: 空白 strip 后算没填，防纯换行 / 纯空格绕过「修改理由必填」。
    amend_reason = (update_data.pop("amend_reason", None) or "").strip() or None
    if "stay_locations" in update_data:
        update_data["stay_locations"] = [
            loc.model_dump() for loc in body.stay_locations
        ]
    if "meals_skip" in update_data:
        update_data["meals_skip"] = [
            e.model_dump(mode="json") for e in body.meals_skip
        ] or None

    # codex(IX-004): 只保留真改了的业务字段。空 body / 只填 amend_reason / 传与现值相同的字段
    # 都不该重置审批链 + 重发邮件（否则已部分承認的届能被反复无实质重置 — 滥用面）。
    def _norm(v):
        # SQLite 读回 timezone=True 可能丢 tzinfo，datetime 比较前统一成 JST aware
        # （与 rollcall.py _as_jst_aware 同款），否则 flight 时间同一时刻会被误判成改了。
        if isinstance(v, datetime):
            return v.replace(tzinfo=_JST) if v.tzinfo is None else v.astimezone(_JST)
        return v

    changed = {
        k: v for k, v in update_data.items() if _norm(getattr(app, k)) != _norm(v)
    }
    if not changed:
        raise HTTPException(
            422, {"code": "NO_CHANGES", "message": "変更内容がありません"}
        )
    # codex: 真改了业务字段就必须有修改理由（iOS 已强制必填、后端再兜一道）。
    if amend_reason is None:
        raise HTTPException(
            422,
            {"code": "AMEND_REASON_REQUIRED", "message": "修正理由を入力してください"},
        )
    for key, val in changed.items():
        setattr(app, key, val)

    # 出寮日校验：只校验真改了的出寮日（没改的旧届出寮日可能已过、不该被误拒）。
    if "leave_date" in changed and changed["leave_date"] <= datetime.now(_JST).date():
        raise HTTPException(
            422, {"code": "LEAVE_DATE_NOT_FUTURE", "message": "出寮日は明日以降"}
        )
    # 帰寮日不能早于出寮日（修改届即使只传一个日期，也用合并后的值校验 — 与 create 时 _check_dates 对齐）
    if app.return_date and app.leave_date and app.return_date < app.leave_date:
        raise HTTPException(
            422,
            {
                "code": "RETURN_BEFORE_LEAVE",
                "message": "帰寮日は出寮日以降にしてください",
            },
        )

    # chain リセット — 全 approvals 削除 → 再生成
    for row in app.approvals:
        db.delete(row)
    db.flush()
    approval_chain.build_chain(db, app)
    # codex(IX-004): 链全删重建后状态必须回 pending。否则 approved_partial / returned 的届改完
    # 「审批链全员 pending、但 status 仍是一部承認 / 退回」状态与链不一致，列表和详情会显示错状态。
    app.status = "pending"

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
            payload={
                "updated_fields": list(changed.keys()),
                # 有填修改理由就记进 audit，老师端 / 学生履历能看到「为什么改」。
                **({"amend_reason": amend_reason} if amend_reason else {}),
            },
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

    # codex(IX-004): audit payload 现含 amend_reason — 权限要跟 GET /{id} 详情端点一致。
    # 学生 → 只能看自己；老师 → 只能看担当寮范围内（不能任意老师读任意申请履历）。
    if isinstance(actor, models.Student):
        if app.student_id != actor.id:
            raise HTTPException(
                403, {"code": "FORBIDDEN", "message": "他人の届は閲覧できません"}
            )
    elif isinstance(actor, models.Teacher):
        # 演示读隔离：演示老师只能读演示学生的 audit、真老师只能读真实学生（否则当 404）。
        # 在寮边界前先判，防演示老师知道真实 UUID 就能读 audit（含 amend_reason 全文）。
        if app.student is not None:
            assert_student_demo_match(actor, app.student)
        if not _teacher_can_view(actor, app.student):
            raise HTTPException(
                403, {"code": "FORBIDDEN_DORM", "message": "担当外の寮の届です"}
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
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

    # 演示写隔离：演示老师只能审批演示学生的届、真老师只能审批真实学生（否则当 404）
    if app.student is not None:
        assert_student_demo_match(teacher, app.student)

    # 终态总闸：已通过 / 已却下 / 已撤回的届不能再被审批。
    # 没这道闸时，撤回(withdrawn) / 已终态的届只要链里还有 decision IS NULL 的行，
    # 当事老师就能继续点「承認」、把 status 又改回 approved_partial / approved（spec §7.2.6 终态不可逆）。
    if app.status in _APPLICATION_TERMINAL_STATUSES:
        raise HTTPException(
            409,
            {
                "code": "APPLICATION_FINALIZED",
                "message": "この届はすでに確定 / 取消済みです",
            },
        )

    # 「担任」步必须由这个学生本班的现役担任来批，不能任何挂着 role='担任' 的老师都能批（报告 B5）。
    # 本班绑定真值在 class_teacher_assignment 表，复用 approval_chain.resolve_homeroom_teacher
    # （它按学生 grade_code/class_code + 当前年度 + is_homeroom 解析现役担任，含演示隔离）。
    if teacher.role == "担任":
        homeroom = (
            approval_chain.resolve_homeroom_teacher(db, app.student)
            if app.student is not None
            else None
        )
        if homeroom is None or homeroom.id != teacher.id:
            raise HTTPException(
                403,
                {
                    "code": "NOT_HOMEROOM_TEACHER",
                    "message": "この学生の担任ではありません",
                },
            )

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

    # 原子条件更新（参照 outings.py confirm_outing）：只有这一行 decision 仍是 NULL 才写成功。
    # 防两个并发请求都通过上面的 pending_row 检查、各写一次造成重复审批 / 状态被覆盖。
    # rowcount != 1 说明已被别的并发请求抢先批掉 → 回滚 + 409。
    decided_at = datetime.now(tz.utc)
    result = db.execute(
        update(models.ApplicationApproval)
        .where(
            models.ApplicationApproval.id == pending_row.id,
            models.ApplicationApproval.decision.is_(None),
        )
        .values(
            approver_id=teacher.id,
            decision=body.decision,
            comment=body.comment,
            decided_at=decided_at,
        )
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "すでに決定済みです"},
        )

    # 上面的条件更新走的是 SQL 直更、没经过 ORM，内存里的 approval 行还是旧值（decision=None）。
    # expire 整个 app.approvals 关系（不只当前 pending_row）：否则两个角色并发审批时，另一角色刚批的
    # 那行在本会话内存里仍是旧值，下面 _recompute_application_status 会误判「还有 pending 行」、把已
    # 全批的届错误停在 approved_partial。expire 后 recompute 遍历 app.approvals 会从库重读所有行最新值。
    # （codex 复审发现）recompute / 发邮件 / 写 audit / commit 全在同一事务里，不分开提交。
    db.expire(app, ["approvals"])

    # application.status 自動更新
    _recompute_application_status(app)

    # 杭田 2026-06-04 需求：审批走到终态（approved 通过 / rejected 却下）后，
    # 给提交者本人发邮件通知结果（要「残る」=留痕，不能用推送，推送会被划掉忘记）。
    # approved_partial（部分通过）/ pending（审批中）不通知。
    if app.status in ("approved", "rejected") and app.student is not None:
        email_svc.send_application_decided(
            db,
            application=app,
            student=app.student,
            result=app.status,
            decided_role=teacher.role,
            comment=body.comment,
        )

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
        taxi_reservation_time=app.taxi_reservation_time,
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
