"""学生账号管理 admin 端点（限定寮务管理 role）。

权威 spec：
- system_features.md §7.1（学生账号管理）
- BACKEND_DESIGN_LOG.md §5.x

角色 gate：寮務部長 / 寮務課長 / 管理係（同 admin_registration_code.py ADMIN_ROLES）
"""

from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import dorm_units_for_teacher, require_teacher_roles
from ..security import hash_password

router = APIRouter(
    prefix="/api/v1",
    tags=["admin / accounts"],
)

# 同 admin_registration_code.py ADMIN_ROLES — §3.4 寮务管理 3 个角色
ADMIN_ROLES = ("寮務部長", "寮務課長", "管理係")

# 临时密码：16 桁英数字混合（大文字 + 小文字 + 数字 — 猜测难度足够，不用特殊符号避免输错）
_TEMP_PW_LENGTH = 16
_TEMP_PW_CHARS = string.ascii_letters + string.digits


def _generate_temp_password() -> str:
    """生成 16 桁随机临时密码（secrets.choice = 加密安全随机）。"""
    return "".join(secrets.choice(_TEMP_PW_CHARS) for _ in range(_TEMP_PW_LENGTH))


def _is_locked(account: models.Account) -> bool:
    """account.locked_until > now(UTC) = 被锁。"""
    if account.locked_until is None:
        return False
    now = datetime.now(timezone.utc)
    locked_until = (
        account.locked_until
        if account.locked_until.tzinfo is not None
        else account.locked_until.replace(tzinfo=timezone.utc)
    )
    return locked_until > now


def _get_student_or_404(student_id: UUID, db: Session) -> models.Student:
    """按 student_id 查学生，找不到就 raise 404。排除 demo/reviewer 账号。"""
    student = db.get(models.Student, student_id)
    if not student or student.is_demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    return student


def _get_account_or_404(student_id: UUID, db: Session) -> models.Account:
    """按 student_id 查 Account，找不到就 raise 404。"""
    account = db.scalars(
        select(models.Account).where(models.Account.student_id == student_id)
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ACCOUNT_NOT_FOUND",
                "message": "アカウントが見つかりません（未登録の可能性）",
            },
        )
    return account


# ---------------------------------------------------------------
# 1. GET /api/v1/students — 学生列表
#    - 給老師网页「账号管理页」/ 「搜索页」
#    - 支持 q（学号 or 姓名模糊）/ dorm_unit filter / status filter
#    - 排除 is_demo=True 的假数据账号
# ---------------------------------------------------------------
@router.get("/students", response_model=schemas.StudentAccountListOut)
def list_students(
    q: str | None = Query(None, description="按学号或姓名模糊搜索"),
    dorm_unit: int | None = Query(None, description="寮号过滤 (1/2/4)"),
    student_status: str | None = Query(
        None, alias="status", description="账号状态过滤 (active/locked/graduated 等)"
    ),
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """学生列表 — 老师网页「账号管理页」挂载时调用。

    流程：
        1. 构建基础 query（排除 is_demo）
        2. 按参数追加 WHERE（模糊搜 / 寮号 / 状态）
        3. JOIN accounts 取锁定状态和最后登录时间
        4. 返回列表 + total
    """
    # 1. 基础 query — 排除 demo 账号（is_demo=False 的真实学生）
    stmt = select(models.Student).where(models.Student.is_demo.is_(False))

    # 2. 可选过滤条件
    if q:
        # 模糊搜 student_no（grade+class+seat 组合）或 name
        # SQLite LIKE 是 case-insensitive（ASCII range），中文姓名也能用 LIKE
        like = f"%{q}%"
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
    if dorm_unit is not None:
        stmt = stmt.where(models.Student.dorm_unit == dorm_unit)
    if student_status is not None:
        stmt = stmt.where(models.Student.status == student_status)

    # 按学号排序（grade → class → seat）
    stmt = stmt.order_by(
        models.Student.grade_code,
        models.Student.class_code,
        models.Student.seat_no,
    )

    students = db.scalars(stmt).all()

    # 3. 批量取 account 信息（一次 IN query，避免 N+1）
    student_ids = [s.id for s in students]
    accounts_map: dict[UUID, models.Account] = {}
    if student_ids:
        account_rows = db.scalars(
            select(models.Account).where(models.Account.student_id.in_(student_ids))
        ).all()
        accounts_map = {a.student_id: a for a in account_rows}

    # 4. 组装响应
    items: list[schemas.StudentAccountListItem] = []
    for s in students:
        acct = accounts_map.get(s.id)
        items.append(
            schemas.StudentAccountListItem(
                id=s.id,
                student_no=s.student_no,
                grade_code=s.grade_code,
                class_code=s.class_code,
                seat_no=s.seat_no,
                name=s.name,
                room_no=s.room_no,
                dorm_unit=s.dorm_unit,
                gender=s.gender,
                status=s.status,
                needs_renewal=s.needs_renewal,
                is_locked=_is_locked(acct) if acct else False,
                last_login_at=acct.last_login_at if acct else None,
            )
        )

    return schemas.StudentAccountListOut(total=len(items), items=items)


# ---------------------------------------------------------------
# 2. POST /api/v1/accounts/{student_id}/password-reset — 重置密码
#    - 生成随机临时密码 → hash 写入 account
#    - 清空 failed_count / locked_until（重置即解锁）
#    - 临时密码明文只在本次响应里出现一次，不存 DB 不记日志
#    - 写 audit_logs
# ---------------------------------------------------------------
@router.post(
    "/accounts/{student_id}/password-reset",
    response_model=schemas.PasswordResetOut,
    status_code=status.HTTP_200_OK,
)
def password_reset(
    student_id: UUID,
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """重置学生密码 — 临时密码明文仅此次响应返回，老师转交学生。

    流程：
        1. 查 student（排除 demo）
        2. 查 account（未注册 → 404）
        3. 生成临时密码 + hash 写入 account
        4. 清 failed_count / locked_until（重置即解锁）
        5. 写 audit_logs（actor=老师，action=account.password_reset）
        6. 返回含明文临时密码的响应（只此一次）
    """
    # 1. 查学生
    _get_student_or_404(student_id, db)

    # 2. 查 account
    account = _get_account_or_404(student_id, db)

    # 3. 生成临时密码（明文仅此处保留，hash 后才进 DB）
    temp_pw = _generate_temp_password()
    account.password_hash = hash_password(temp_pw)

    # 4. 清锁定状态（重置 = 解锁 + 清失败计数）
    account.failed_count = 0
    account.locked_until = None
    account.lock_level = 0

    # 5. audit_logs — payload 不含明文密码（只记操作者和目标）
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="account.password_reset",
            target_type="account",
            target_id=account.id,
            payload={
                "student_id": str(student_id),
                "reset_by_teacher_id": str(teacher.id),
            },
        )
    )
    db.commit()

    # 6. 返回（明文只在这里出现一次，db.commit 之后不再保存任何明文）
    return schemas.PasswordResetOut(
        student_id=student_id,
        temporary_password=temp_pw,
    )


# ---------------------------------------------------------------
# 3. POST /api/v1/accounts/{student_id}/unlock — 解锁账号
#    - 清 locked_until + failed_count + lock_level
#    - 写 audit_logs（action=account.unlock）
# ---------------------------------------------------------------
@router.post(
    "/accounts/{student_id}/unlock",
    response_model=schemas.UnlockOut,
    status_code=status.HTTP_200_OK,
)
def unlock_account(
    student_id: UUID,
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """解锁被锁账号。

    流程：
        1. 查 student（排除 demo）
        2. 查 account
        3. 清 locked_until / failed_count / lock_level
        4. 写 audit_logs（action=account.unlock）
    """
    # 1. 查学生
    _get_student_or_404(student_id, db)

    # 2. 查 account
    account = _get_account_or_404(student_id, db)

    # 3. 清锁定字段（即使当前未锁也幂等地清掉）
    account.locked_until = None
    account.failed_count = 0
    account.lock_level = 0

    # 4. audit_logs
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="account.unlock",
            target_type="account",
            target_id=account.id,
            payload={
                "student_id": str(student_id),
                "unlocked_by_teacher_id": str(teacher.id),
            },
        )
    )
    db.commit()

    return schemas.UnlockOut(student_id=student_id)


# ---------------------------------------------------------------
# 4. GET /api/v1/students/renewal-progress — 学年更新进度（老师看谁还没改番号）
#    - 列出 needs_renewal=True 的真实学生（排除 is_demo）
#    - 老师网页据此显示「还差 N 人」+ 未改名单（前端按年级→班级分组）
#    - spec §4.2（2026-06-05 学生自设方案）
# ---------------------------------------------------------------
@router.get("/students/renewal-progress", response_model=schemas.RenewalProgressOut)
def renewal_progress(
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """学年更新进度 — 还没自设番号的学生名单（needs_renewal=True）。

    pending_count=0 = 全员改完。老师网页据此显示「全員完了」。
    """
    stmt = select(models.Student).where(
        models.Student.needs_renewal.is_(True),
        models.Student.is_demo.is_(False),
    )
    # R4 寮边界：分寮管理係只看本人管辖寮的未更新名单（跨寮角色 allowed=None 看全部）
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    students = db.scalars(
        stmt.order_by(
            models.Student.grade_code,
            models.Student.class_code,
            models.Student.seat_no,
        )
    ).all()
    items = [
        schemas.RenewalProgressItem(
            id=s.id,
            student_no=s.student_no,
            name=s.name,
            grade_code=s.grade_code,
            class_code=s.class_code,
            seat_no=s.seat_no,
        )
        for s in students
    ]
    return schemas.RenewalProgressOut(pending_count=len(items), items=items)


# ---------------------------------------------------------------
# 5. POST /api/v1/accounts/{student_id}/renew-seat — 老师单件改某学生番号（兜底）
#    - 学生不会操作 / 填错时，老师代改其 grade/class/seat
#    - 查重（排除自己）撞号 422；改完清 needs_renewal=False
#    - 写 audit_logs（action=student.renew_seat_by_teacher）
#    - spec §4.2（2026-06-05 学生自设方案，老师兜底手段）
# ---------------------------------------------------------------
@router.post(
    "/accounts/{student_id}/renew-seat",
    response_model=schemas.StudentProfileBasic,
    status_code=status.HTTP_200_OK,
)
def teacher_renew_seat(
    student_id: UUID,
    body: schemas.TeacherRenewSeatIn,
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """老师单件改某学生番号（兜底 — 学生不会操作 / 填错时）。"""
    student = _get_student_or_404(student_id, db)
    # R4 寮边界：分寮管理係只能改本人管辖寮的学生（跨寮角色 allowed=None 不限）
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当寮外の学生は変更できません",
            },
        )
    new_no = f"{body.grade_code}{body.class_code}{body.seat_no}"

    # 查重（排除该学生自己）
    existing = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == body.grade_code,
            models.Student.class_code == body.class_code,
            models.Student.seat_no == body.seat_no,
            models.Student.id != student_id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に使われています",
            },
        )

    student.grade_code = body.grade_code
    student.class_code = body.class_code
    student.seat_no = body.seat_no
    student.needs_renewal = False

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="student.renew_seat_by_teacher",
            target_type="student",
            target_id=student_id,
            payload={
                "new_student_no": new_no,
                "changed_by_teacher_id": str(teacher.id),
            },
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に使われています",
            },
        )

    db.refresh(student)
    return schemas.StudentProfileBasic.model_validate(student)
