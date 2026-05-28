"""ログイン (学生 / 教师) — JWT 発行。

P0 範囲では POST /applications / GET /applications/:id 等が
認証付き endpoint なので、最低限のログインを提供する。

2026-05-21 加：教师 login 失败计数 + 锁定（A-006）
    - 教师端权限高（改判 / 发邀请码 / 解 NFC 绑定），蛮力破解危害大
    - 3 次失败 → 锁 30 分钟（学生端阈值待主会话拍板 A-005）
    - 用 teachers.failed_count + teachers.locked_until 字段（已存在）
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db

router = APIRouter(prefix="/api/v1/sessions", tags=["auth"])

# 教师 login 锁定阈值（2026-05-21 A-006）
TEACHER_LOCK_THRESHOLD = 3  # 3 次失败立锁
TEACHER_LOCK_DURATION_MIN = 30  # 锁 30 分钟


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
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "学号 or 密码が違います"},
        )
    account = db.scalars(
        select(models.Account).where(models.Account.student_id == student.id)
    ).first()
    if not account or not security.verify_password(
        body.password, account.password_hash
    ):
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
    account.last_login_at = datetime.now(timezone.utc)
    account.failed_count = 0
    account.lock_level = 0
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
    if not teacher or not security.verify_password(
        body.password, teacher.password_hash
    ):
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
