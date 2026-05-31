"""ログイン (学生 / 教师) — JWT 発行。

P0 範囲では POST /applications / GET /applications/:id 等が
認証付き endpoint なので、最低限のログインを提供する。

2026-05-21 加：教师 login 失败计数 + 锁定（A-006）
    - 教师端权限高（改判 / 发邀请码 / 解 NFC 绑定），蛮力破解危害大
    - 3 次失败 → 锁 30 分钟（学生端阈值待主会话拍板 A-005）
    - 用 teachers.failed_count + teachers.locked_until 字段（已存在）

2026-05-30 加：
    - DELETE /sessions/current — B1 无状态登出（JWT 客户端丢弃即可）
    - 学生 login 失败计数 + 锁定 — B6（照抄教师逻辑，用 accounts 表字段）
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db
from ..deps import get_current_principal  # B1 登出端点用（老师 + 学生都能调）

router = APIRouter(prefix="/api/v1/sessions", tags=["auth"])

# 教师 login 锁定阈值（A-006）
TEACHER_LOCK_THRESHOLD = 3  # 3 次失败立锁
TEACHER_LOCK_DURATION_MIN = 30  # 锁 30 分钟

# B6：学生 login 锁定阈值（与教师对齐，5 次 → 锁 15 分钟）
STUDENT_LOCK_THRESHOLD = 5
STUDENT_LOCK_DURATION_MIN = 15

# auth-account-09：时序侧信道加固。
# 账号（学号/教师）不存在时，原本会短路跳过 bcrypt 校验导致响应明显更快，
# 可被用来枚举哪些账号已注册。这里预算一个固定 dummy hash，账号缺失时也
# 跑一次 verify_password，让 bcrypt 耗时在「存在」与「不存在」两种情况下一致。
# 模块加载时算一次，不影响每次请求性能。
_DUMMY_PASSWORD_HASH = security.hash_password("dummy-password-for-timing-equalization")


@router.post("/student", response_model=schemas.TokenOut)
def login_student(body: schemas.StudentLoginIn, db: Session = Depends(get_db)):
    grade, klass, seat = body.student_no[:2], body.student_no[2:4], body.student_no[4:6]

    student = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == grade,
            models.Student.class_code == klass,
            models.Student.seat_no == seat,
        )
    ).first()

    # 先取 account（后面锁定逻辑需要），找不到学生也走到 401
    account = None
    if student:
        account = db.scalars(
            select(models.Account).where(models.Account.student_id == student.id)
        ).first()

    now = datetime.now(timezone.utc)
    # SQLite 返回 naive datetime，PostgreSQL 生产返回 aware datetime。
    # 统一去掉时区信息后比较，避免 TypeError。
    now_naive = now.replace(tzinfo=None)

    def _is_locked(dt) -> bool:
        """判断 locked_until 是否还在未来（naive/aware 两种情况都兼容）。"""
        if dt is None:
            return False
        compare = dt.replace(tzinfo=None) if dt.tzinfo else dt
        return compare > now_naive

    def _remaining_min(dt) -> int:
        compare = dt.replace(tzinfo=None) if dt.tzinfo else dt
        return int((compare - now_naive).total_seconds() / 60) + 1

    # B6：检查账号是否被锁
    if account and _is_locked(account.locked_until):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "ACCOUNT_LOCKED",
                "message": f"アカウントロック中（残り約 {_remaining_min(account.locked_until)} 分）",
            },
        )

    # 密码校验失败 → 失败计数 + 触发锁
    # auth-account-09：无论账号是否存在都跑一次 bcrypt，等化响应耗时，防账号枚举。
    password_hash = account.password_hash if account else _DUMMY_PASSWORD_HASH
    password_ok = security.verify_password(body.password, password_hash)
    if not student or not account or not password_ok:
        if account:
            account.failed_count = (account.failed_count or 0) + 1
            if account.failed_count >= STUDENT_LOCK_THRESHOLD:
                # 写 naive datetime — SQLite 兼容；PG 本番 DateTime(timezone=True) 也能存
                account.locked_until = now_naive + timedelta(
                    minutes=STUDENT_LOCK_DURATION_MIN
                )
                account.lock_level = (account.lock_level or 0) + 1
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "学号 or 密码が違います"},
        )

    if student.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント停止中"},
        )

    settings = get_settings()
    token = security.create_access_token(
        student.id,
        "student",
        extra={
            "dorm_unit": student.dorm_unit,
            "is_overseas": student.is_overseas,
            "name": student.name,
        },
    )
    # 登录成功 → 清失败计数 + 清锁
    account.last_login_at = now
    account.failed_count = 0
    account.lock_level = 0
    account.locked_until = None
    db.commit()
    return schemas.TokenOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
    )


@router.post("/teacher", response_model=schemas.TeacherTokenOut)
def login_teacher(body: schemas.TeacherLoginIn, db: Session = Depends(get_db)):
    # 5-27 拍板：支持 teacher_id (UUID) 或 login_id，至少一个
    if not body.teacher_id and not body.login_id:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "MISSING_IDENTIFIER",
                "message": "teacher_id or login_id is required",
            },
        )
    if body.teacher_id:
        teacher = db.get(models.Teacher, body.teacher_id)
    else:
        teacher = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == body.login_id)
        ).first()

    now = datetime.now(timezone.utc)

    # A-006: 检查教师是否被锁
    if teacher and teacher.locked_until and teacher.locked_until > now:
        remaining = int((teacher.locked_until - now).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "ACCOUNT_LOCKED",
                "message": f"アカウントロック中（残り約 {remaining} 分）",
            },
        )

    # 密码校验失败 → 失败计数 + 触发锁
    # auth-account-09：无论账号是否存在都跑一次 bcrypt，等化响应耗时，防账号枚举。
    password_hash = teacher.password_hash if teacher else _DUMMY_PASSWORD_HASH
    password_ok = security.verify_password(body.password, password_hash)
    if not teacher or not password_ok:
        if teacher:
            teacher.failed_count = (teacher.failed_count or 0) + 1
            if teacher.failed_count >= TEACHER_LOCK_THRESHOLD:
                teacher.locked_until = now + timedelta(
                    minutes=TEACHER_LOCK_DURATION_MIN
                )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "ID or 密码が違います"},
        )
    if teacher.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント停止中"},
        )

    settings = get_settings()
    token = security.create_access_token(
        teacher.id,
        f"teacher:{teacher.role}",
        extra={
            "name": teacher.name,
            "teacher_role": teacher.role,
            "assigned_dorm": teacher.assigned_dorm,
        },
    )
    # 登录成功 → 清失败计数 + 清锁
    teacher.last_login_at = now
    teacher.failed_count = 0
    teacher.locked_until = None
    db.commit()
    return schemas.TeacherTokenOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
        teacher=schemas.TeacherOut.model_validate(teacher),
    )


@router.delete("/current", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """B1 — 登出（学生 + 老师都可调）。

    系统用无状态 JWT，服务端不存 token。
    客户端收到 204 后把本地 token 丢弃即可完成登出。

    真正的服务端吊销（防 token 被盗后仍可用）需 v1.1 加 jti 黑名单表，
    本版本不实现，符合 v1.0 安全基线。
    """
    return  # 204 No Content
