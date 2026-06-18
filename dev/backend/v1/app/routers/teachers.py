"""教師管理 endpoint (§3.4 教師権限 + 招待登録フロー).

POST /api/v1/teachers/invitations         — 招待トークン発行 (役職者のみ)
POST /api/v1/teachers/register            — 招待トークンで新教師登録
GET  /api/v1/teachers                     — 教師一覧 (寮務部長 以上)
GET  /api/v1/teachers/me                  — 自分のプロフィール
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .. import permissions
from ..deps import require_permission
from ..security import hash_password

router = APIRouter(prefix="/api/v1/teachers", tags=["teachers"])

INVITATION_EXPIRE_DAYS = 7


# 教师账户管理（POST / DELETE）权限 — 职位退化为纯显示标签后，「谁是老师账号管理员」
# 不再数职位标签，改由 effective_group 对「老师账号管理」簇是否达 MANAGE 判定
# （仅 op / 寮管理者 有 M；permission_group 为 NULL 时按职位回退兜底）。
def _has_teacher_account_admin(teacher: models.Teacher) -> bool:
    return permissions.has_permission(
        permissions.effective_group(teacher),
        permissions.C_TEACHER_ACCOUNT,
        permissions.MANAGE,
    )


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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_TEACHER_ACCOUNT, permissions.MANAGE)
    ),
):
    # 2026-06-15 itsuki 拍板：演示账号同样可发招待 / 列老师 / 增删老师（取消 assert_not_demo_teacher 闸）。
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
# 路径用 "" 而非 "/" — canonical path 不带尾斜杠（FastAPI 惯例，与本项目
# 其余集合端点 bus_routes / announcements / events 等一致）。改前不带尾斜杠的
# 客户端要靠 307 重定向才能到达，改后直达。
@router.get("", response_model=list[schemas.TeacherOut])
def list_teachers(
    role_filter: str | None = Query(None, alias="role"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_TEACHER_ACCOUNT, permissions.VIEW)
    ),
):
    # 2026-06-15 itsuki 拍板：演示账号同样可列真实老师（取消 assert_not_demo_teacher 闸）。
    stmt = select(models.Teacher).where(models.Teacher.status == "active")
    if role_filter:
        stmt = stmt.where(models.Teacher.role == role_filter)
    teachers = db.scalars(stmt.order_by(models.Teacher.name)).all()
    return [schemas.TeacherOut.model_validate(t) for t in teachers]


# ---------------------------------------------------------------
# GET /teachers/me — 自分のプロフィール
# ---------------------------------------------------------------
@router.get("/me", response_model=schemas.TeacherOut)
def me(
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_TEACHER_ACCOUNT, permissions.VIEW)
    ),
):
    return schemas.TeacherOut.model_validate(teacher)


# ---------------------------------------------------------------
# GET /teachers/public — 登录页第 1 屏用（无认证、最小字段）
# 2026-05-27 itsuki 拍板：实名账户登录方式，前端进 web 就能看到老师卡片列表。
# 只返 id+name+assigned_dorm+last_login_at+permission_group — 不返 login_id/email/role/status。
# permission_group 返「有效权限组」（已按职位回退）供登录页按权限组分栏；属半公开信息。
# ---------------------------------------------------------------
@router.get("/public", response_model=list[schemas.TeacherPublicOut])
def list_teachers_public(db: Session = Depends(get_db)):
    stmt = (
        select(models.Teacher)
        .where(models.Teacher.status == "active")
        .order_by(models.Teacher.name)
    )
    teachers = db.scalars(stmt).all()
    # op 运维账号不上墙（登录页 4 个权限组栏不含 op，本就不显示）—— 这里从源头剔除，
    # 连 op 的姓名 / 最后登录时间也不半公开泄露。op 走「システム管理者ログイン」单独入口
    # （前端输 login_id + 密码登录，不靠这个公开列表）。
    return [
        schemas.TeacherPublicOut(
            id=t.id,
            name=t.name,
            assigned_dorm=t.assigned_dorm,
            last_login_at=t.last_login_at,
            permission_group=permissions.effective_group(t),
        )
        for t in teachers
        if permissions.effective_group(t) != permissions.GROUP_OP
    ]


# ---------------------------------------------------------------
# POST /teachers — 已登录教师 + 寮务管理权限 → 直接创建新教师（v1.0 简化版）
# §3.4「前台不允许自助注册任何教师账号 / 必须先用现有教师账号登录 → 加 / 删」
# 5-27 codex 审查 #2: 权限只给「老师账号管理」MANAGE 组（require_permission，防越权）
# 5-27 codex 审查 #5: 唯一性预查 + IntegrityError 双重保护防并发 race
# ---------------------------------------------------------------
# 路径用 "" 而非 "/" — 与上面 GET 列表端点保持同一 canonical path（/api/v1/teachers，
# 无尾斜杠）。若此处仍留 "/"，则 /api/v1/teachers/ 这个带尾斜杠路径会被 POST 占用，
# 导致带尾斜杠的 GET 请求拿到 405（而非 FastAPI 的去尾斜杠重定向）→ 破坏老客户端。
@router.post("", response_model=schemas.TeacherOut, status_code=201)
def create_teacher(
    body: schemas.TeacherCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_TEACHER_ACCOUNT, permissions.MANAGE)
    ),
):
    # 2026-06-15 itsuki 拍板：演示账号同样可创建真实老师（取消 assert_not_demo_teacher 闸）。
    if body.role not in models.TEACHER_ROLES:
        raise HTTPException(
            422,
            {"code": "INVALID_ROLE", "message": f"無効な役職: {body.role}"},
        )
    # 权限组校验（teacher_permission_v1.md §3）— 省略则建账号后按职位回退默认组。
    # 不允许经此端点创建 op（系统运维账号只走 seed + 环境变量 OP_PASSWORD）。
    if body.permission_group is not None and body.permission_group not in (
        permissions.GROUP_DORM_ADMIN,
        permissions.GROUP_GENERAL,
        permissions.GROUP_GENERAL_STUDY,
        permissions.GROUP_APPROVAL,
    ):
        raise HTTPException(
            422,
            {
                "code": "INVALID_PERMISSION_GROUP",
                "message": f"無効な権限グループ: {body.permission_group}",
            },
        )
    # 唯一性预检 — login_id / email（不能完全防 race，仅给友好错误）
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
        permission_group=body.permission_group,
        assigned_dorm=body.assigned_dorm,
        status="active",
    )
    db.add(new_teacher)
    try:
        db.commit()
    except IntegrityError:
        # 并发 race — 预检通过但 commit 时 unique constraint 撞车
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "DUPLICATE",
                "message": "login_id または email が既に存在（並行作成と衝突）",
            },
        )
    db.refresh(new_teacher)
    return schemas.TeacherOut.model_validate(new_teacher)


# ---------------------------------------------------------------
# DELETE /teachers/{teacher_id} — 已登录教师 + 寮务管理权限 → 删除教师
# 自己删自己拦截（防最后一个账号没人能登录）
# 5-27 codex 审查 #2: 权限只给「老师账号管理」MANAGE 组（require_permission，不给学習担当）
# 5-27 codex 审查 #3 + 2026-06-12 F4: 删最后一个有该管理权的老师拦截（按 effective_group 判，防 lockout）
# ---------------------------------------------------------------
@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(
    teacher_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_TEACHER_ACCOUNT, permissions.MANAGE)
    ),
):
    # 2026-06-15 itsuki 拍板：演示账号同样可删除老师（取消 assert_not_demo_teacher 闸）。
    if teacher.id == teacher_id:
        raise HTTPException(
            400,
            {"code": "CANNOT_DELETE_SELF", "message": "自分自身は削除できません"},
        )
    target = db.get(models.Teacher, teacher_id)
    if not target:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "教師が見つかりません"}
        )

    # 删最后一个「老师账号管理」管理员拦截 — 防系统 lockout
    # 2026-06-12 codex 审查 F4：按 effective_group 实际权限判，不再数职位标签。
    # effective_group 含 NULL 时按职位回退，故 SQL 无法直接表达 → 取 active 老师在 Python 里数。
    if _has_teacher_account_admin(target):
        others = db.scalars(
            select(models.Teacher).where(
                models.Teacher.status == "active",
                models.Teacher.id != target.id,
            )
        ).all()
        remaining = sum(1 for t in others if _has_teacher_account_admin(t))
        if remaining < 1:
            raise HTTPException(
                400,
                {
                    "code": "LAST_ADMIN",
                    "message": "最後の寮務管理権限教師は削除できません（システムロックアウト防止）",
                },
            )

    # 软删而非物理 delete（与学生侧 accounts.py delete_account_me 同口径）：
    # ① status → 'disabled'（ck_teachers_status CHECK 已允许该值）保留行本身供审计追溯；
    # ② 清 password_hash 防被删老师再登录；③ 写 AuditLog 留痕。
    # 物理 db.delete 在生产 PostgreSQL 会因 student_registration_codes.created_by /
    # teacher_invitations.invited_by 等 nullable=False 无 ondelete 的外键抛 IntegrityError
    # → 经 main.py 全局兜底变不透明 500，且 dev(SQLite 默认不强制外键)与 prod 行为分叉。
    target.status = "disabled"
    target.password_hash = ""  # 清空哈希，bcrypt 永远无法匹配
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="teacher.delete",
            target_type="teacher",
            target_id=target.id,
            payload={"deleted_login_id": target.login_id},
        )
    )
    db.commit()
    return None
