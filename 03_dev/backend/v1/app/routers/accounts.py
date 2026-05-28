"""学生新规注册端点（POST /accounts）。

权威 spec：
- BACKEND_DESIGN_LOG.md §5.1.5（请求 / 响应 / 错误码）
- system_features.md §7.16 + §3.4 + §5.0 room_no 编码规则

2026-05-03 拍板：必须传 registration_code（App Store 上架对策）。

注：本文件下面 raise 的 detail.message 字段是给学生用户看的 UI 文案，
按 spec §7.16.2 规则 7 固定为日语；这与「注释一律中文」规则不冲突。
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


def _validate_room_dorm_match(room_no: str, dorm_unit: int, gender: str) -> None:
    """校验 room_no 前缀和 dorm_unit / gender 是否一致（§5.0）。

    规则：M*** = male & dorm_unit ∈ {1, 2}；W*** = female & dorm_unit = 4。
    """
    prefix = room_no[:1].upper()
    expected_prefix = "M" if dorm_unit in (1, 2) else "W"
    expected_gender = "male" if dorm_unit in (1, 2) else "female"
    if prefix != expected_prefix or gender != expected_gender:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_ROOM_FORMAT",
                "message": (
                    f"room_no '{room_no}' と dorm_unit={dorm_unit} / gender={gender} "
                    "が不整合です (M*** + dorm 1|2 + male / W*** + dorm 4 + female)"
                ),
            },
        )


def _validate_registration_code(
    code: str, db: Session
) -> models.StudentRegistrationCode:
    """返回有效的注册码 row；找不到就 raise INVALID_REGISTRATION_CODE。"""
    now = datetime.now(timezone.utc)
    row = db.scalars(
        select(models.StudentRegistrationCode)
        .where(
            models.StudentRegistrationCode.code == code,
            models.StudentRegistrationCode.invalidated_at.is_(None),
            models.StudentRegistrationCode.expires_at > now,
        )
        .order_by(models.StudentRegistrationCode.created_at.desc())
        .limit(1)
    ).first()
    if not row:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_REGISTRATION_CODE",
                # spec §7.16.2 规则 7 固定文案（给学生看）
                "message": (
                    "コードが正しくないか、有効期限が切れています。"
                    "教師に再発行を依頼してください。"
                ),
            },
        )
    return row


@router.post(
    "",
    response_model=schemas.StudentAccountCreateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    body: schemas.StudentAccountCreateIn, db: Session = Depends(get_db)
):
    """学生新规注册 — 必须传 registration_code。

    §5.1.5 处理流程：
        1. 校验 registration_code
        2. 校验 room_no ↔ dorm_unit ↔ gender 一致
        3. 学号（grade+class+seat 组合）查重
        4. email 查重（email 是 optional 字段）
        5. 一个事务里同时 insert students + accounts
        6. 写 registration_code 使用 audit log
        7. 发永久 session 用的 JWT
    """
    # 1. 校验 registration_code
    code_row = _validate_registration_code(body.registration_code, db)

    # 2. 校验 room_no ↔ dorm_unit ↔ gender 一致
    _validate_room_dorm_match(body.room_no, body.dorm_unit, body.gender)

    # 3. 学号查重
    existing_student = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == body.grade_code,
            models.Student.class_code == body.class_code,
            models.Student.seat_no == body.seat_no,
        )
    ).first()
    if existing_student:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": (
                    f"学号 {body.grade_code}{body.class_code}{body.seat_no} "
                    "は既に登録されています"
                ),
            },
        )

    # 4. email 查重（email 是 optional 字段）
    if body.email:
        existing_email = db.scalars(
            select(models.Student).where(models.Student.email == body.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "EMAIL_TAKEN",
                    "message": f"email {body.email} は既に使われています",
                },
            )

    # 5. 一个事务里同时 insert students + accounts
    student = models.Student(
        grade_code=body.grade_code,
        class_code=body.class_code,
        seat_no=body.seat_no,
        name=body.name,
        name_kana=body.name_kana,
        birthday=body.birthday,
        gender=body.gender,
        category=body.category,
        room_no=body.room_no,
        dorm_unit=body.dorm_unit,
        is_overseas=body.is_overseas,
        email=body.email,
        phone=body.phone,
    )
    db.add(student)
    db.flush()
    db.add(
        models.Account(
            student_id=student.id,
            password_hash=security.hash_password(body.password),
        )
    )

    # 6. 写 registration_code 使用 audit log（§4.10 末尾要求）
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="registration_code.use",
            target_type="student_registration_code",
            target_id=code_row.id,
            payload={"student_no": student.student_no},
        )
    )
    db.commit()
    db.refresh(student)

    # 7. 发永久 session 用的 JWT（和 login 同等 = 86400 秒；IOS_DESIGN_LOG §3.5 永久 session）
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

    return schemas.StudentAccountCreateOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
        student=schemas.StudentBrief.model_validate(student),
    )
