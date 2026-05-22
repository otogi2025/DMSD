"""ログイン (学生 / 教师) — JWT 発行。

P0 範囲では POST /applications / GET /applications/:id 等が
認証付き endpoint なので、最低限のログインを提供する。
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db

router = APIRouter(prefix="/api/v1/sessions", tags=["auth"])


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
    if not account or not security.verify_password(body.password, account.password_hash):
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
    teacher = db.scalars(
        select(models.Teacher).where(models.Teacher.login_id == body.login_id)
    ).first()
    if not teacher or not security.verify_password(body.password, teacher.password_hash):
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
    teacher.last_login_at = datetime.now(timezone.utc)
    teacher.failed_count = 0
    db.commit()
    return schemas.TeacherTokenOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
        teacher=schemas.TeacherOut.model_validate(teacher),
    )
