"""教師管理 endpoint (§3.4 教師権限 + 招待登録フロー).

POST /api/v1/teachers/invitations         — 招待トークン発行 (役職者のみ)
POST /api/v1/teachers/register            — 招待トークンで新教師登録
GET  /api/v1/teachers                     — 教師一覧 (寮務部長 以上)
GET  /api/v1/teachers/me                  — 自分のプロフィール
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_teacher, require_teacher_roles
from ..security import hash_password

router = APIRouter(prefix="/api/v1/teachers", tags=["teachers"])

INVITATION_EXPIRE_DAYS = 7

# 招待発行できる役職 (寮務部長 / 寮務課長 / 寮監 — §3.4)
INVITE_ALLOWED_ROLES = {"寮務部長", "寮務課長", "寮監", "学習担当"}


# ---------------------------------------------------------------
# POST /teachers/invitations — 招待トークン発行
# ---------------------------------------------------------------
@router.post(
    "/invitations",
    response_model=schemas.TeacherInvitationOut,
    status_code=201,
)
def create_invitation(
    body: schemas.TeacherInvitationIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    if teacher.role not in INVITE_ALLOWED_ROLES:
        raise HTTPException(
            403,
            {"code": "FORBIDDEN_ROLE", "message": "招待を発行できる役職ではありません"},
        )

    # target_role が有効かチェック
    if body.target_role not in models.TEACHER_ROLES:
        raise HTTPException(
            422,
            {"code": "INVALID_ROLE", "message": f"無効な役職: {body.target_role}"},
        )

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    invitation = models.TeacherInvitation(
        token=token,
        invited_by=teacher.id,
        target_email=body.target_email,
        target_role=body.target_role,
        target_dorm=body.target_dorm,
        expires_at=now + timedelta(days=INVITATION_EXPIRE_DAYS),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return schemas.TeacherInvitationOut.model_validate(invitation)


# ---------------------------------------------------------------
# POST /teachers/register — 招待トークンで新教師登録
# ---------------------------------------------------------------
@router.post("/register", response_model=schemas.TeacherOut, status_code=201)
def register_teacher(
    body: schemas.TeacherRegisterIn,
    db: Session = Depends(get_db),
):
    invitation = db.scalars(
        select(models.TeacherInvitation).where(
            models.TeacherInvitation.token == body.token
        )
    ).first()

    if not invitation:
        raise HTTPException(
            404,
            {"code": "INVALID_TOKEN", "message": "招待トークンが無効です"},
        )
    now = datetime.now(timezone.utc)
    if invitation.expires_at < now:
        raise HTTPException(
            410,
            {
                "code": "TOKEN_EXPIRED",
                "message": "招待トークンの有効期限が切れています",
            },
        )
    if invitation.used_at is not None:
        raise HTTPException(
            409,
            {"code": "TOKEN_USED", "message": "この招待トークンは既に使用済みです"},
        )

    # A-012 (2026-05-21): confirmation_email 必须跟 invitation.target_email 严格对比
    # 防止 token 被截图 / 转发 → 任何拿到 token 的人能注册
    if (
        body.confirmation_email.strip().lower()
        != invitation.target_email.strip().lower()
    ):
        raise HTTPException(
            403,
            {
                "code": "EMAIL_MISMATCH",
                "message": "確認メールが招待先と一致しません",
            },
        )

    # login_id 重複チェック
    dup = db.scalars(
        select(models.Teacher).where(models.Teacher.login_id == body.login_id)
    ).first()
    if dup:
        raise HTTPException(
            409,
            {
                "code": "DUPLICATE_LOGIN_ID",
                "message": "この login ID は既に使用されています",
            },
        )

    new_teacher = models.Teacher(
        login_id=body.login_id,
        name=body.name,
        email=invitation.target_email,
        password_hash=hash_password(body.password),
        role=invitation.target_role,
        assigned_dorm=invitation.target_dorm,
    )
    db.add(new_teacher)
    db.flush()

    # トークンを消費済みにする
    invitation.used_at = now
    invitation.used_by = new_teacher.id

    db.commit()
    db.refresh(new_teacher)
    return schemas.TeacherOut.model_validate(new_teacher)


# ---------------------------------------------------------------
# GET /teachers — 教師一覧 (寮務部長 / 寮務課長 限定)
# ---------------------------------------------------------------
@router.get("/", response_model=list[schemas.TeacherOut])
def list_teachers(
    role_filter: str | None = Query(None, alias="role"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("寮務部長", "寮務課長", "寮監")
    ),
):
    stmt = select(models.Teacher).where(models.Teacher.status == "active")
    if role_filter:
        stmt = stmt.where(models.Teacher.role == role_filter)
    teachers = db.scalars(stmt.order_by(models.Teacher.name)).all()
    return [schemas.TeacherOut.model_validate(t) for t in teachers]


# ---------------------------------------------------------------
# GET /teachers/me — 自分のプロフィール
# ---------------------------------------------------------------
@router.get("/me", response_model=schemas.TeacherOut)
def me(teacher: models.Teacher = Depends(get_current_teacher)):
    return schemas.TeacherOut.model_validate(teacher)


# ---------------------------------------------------------------
# GET /teachers/public — 登录页第 1 屏用（无认证、最小字段）
# 2026-05-27 itsuki 拍板：实名账户登录方式，前端进 web 就能看到老师卡片列表。
# 只返 id+name+assigned_dorm+last_login_at — 不返 login_id/email/role/status。
# ---------------------------------------------------------------
@router.get("/public", response_model=list[schemas.TeacherPublicOut])
def list_teachers_public(db: Session = Depends(get_db)):
    stmt = (
        select(models.Teacher)
        .where(models.Teacher.status == "active")
        .order_by(models.Teacher.name)
    )
    teachers = db.scalars(stmt).all()
    return [schemas.TeacherPublicOut.model_validate(t) for t in teachers]


# ---------------------------------------------------------------
# POST /teachers — 已登录教师 + 寮務管理権限 → 直接创建新教师（v1.0 简化版）
# §3.4「前台不允许自助注册任何教师账号 / 必须先用现有教师账号登录 → 加 / 删」
# ---------------------------------------------------------------
@router.post("/", response_model=schemas.TeacherOut, status_code=201)
def create_teacher(
    body: schemas.TeacherCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(require_teacher_roles(*INVITE_ALLOWED_ROLES)),
):
    if body.role not in models.TEACHER_ROLES:
        raise HTTPException(
            422,
            {"code": "INVALID_ROLE", "message": f"無効な役職: {body.role}"},
        )
    # 唯一性検査 — login_id / email
    existing = db.scalars(
        select(models.Teacher).where(
            (models.Teacher.login_id == body.login_id)
            | (models.Teacher.email == body.email)
        )
    ).first()
    if existing:
        raise HTTPException(
            409,
            {"code": "DUPLICATE", "message": "login_id または email が既に存在"},
        )

    new_teacher = models.Teacher(
        login_id=body.login_id,
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        assigned_dorm=body.assigned_dorm,
        status="active",
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return schemas.TeacherOut.model_validate(new_teacher)


# ---------------------------------------------------------------
# DELETE /teachers/{teacher_id} — 已登录教师 + 寮務管理権限 → 删除教师
# 自己删自己防止（最后一个账号没人能登录）
# ---------------------------------------------------------------
@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(
    teacher_id: str,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(require_teacher_roles(*INVITE_ALLOWED_ROLES)),
):
    if str(teacher.id) == teacher_id:
        raise HTTPException(
            400,
            {"code": "CANNOT_DELETE_SELF", "message": "自分自身は削除できません"},
        )
    target = db.get(models.Teacher, teacher_id)
    if not target:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "教師が見つかりません"}
        )
    db.delete(target)
    db.commit()
    return None
