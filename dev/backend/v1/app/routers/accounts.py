"""学生新规注册端点（POST /accounts）。

权威 spec：
- BACKEND_DESIGN_LOG.md §5.1.5（请求 / 响应 / 错误码）
- system_features.md §7.16 + §3.4 + §5.0 room_no 编码规则

2026-05-03 拍板：必须传 registration_code（App Store 上架对策）。

注：本文件下面 raise 的 detail.message 字段是给学生用户看的 UI 文案，
按 spec §7.16.2 规则 7 固定为日语；这与「注释一律中文」规则不冲突。
"""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db
from ..deps import get_current_student
from ..ratelimit import limiter

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])

# 限速器单例见 ..ratelimit（已在 import 区导入，与全后端共用计数）


# §5.0 房号编码 ↔ dorm_unit ↔ gender（与 §8.1 DB CHECK 1426-1428 同源）：
#   1 寮 = M[0-9]{3} (male) / 2 寮 = A[0-9]{1,2} (male) / 4 寮 = W[0-9]{3} (female)
_ROOM_PATTERN_BY_DORM: dict[int, str] = {
    1: r"^M[0-9]{3}$",
    2: r"^A[0-9]{1,2}$",
    4: r"^W[0-9]{3}$",
}


def validate_room_dorm_match(room_no: str, dorm_unit: int, gender: str) -> None:
    """校验 room_no、dorm_unit、gender 三者一致（§5.0 房号编码 + §8.1 DB CHECK）。

    1 寮 = M*** (male) / 2 寮 = A* (male) / 4 寮 = W*** (female)。
    在应用层用与 DB CHECK 同源的正则提前挡掉非法组合，否则落到 DB 触发 IntegrityError → 500。
    （旧实现对 2 寮一律期望 M 前缀，与 DB CHECK（2 寮要求 A 前缀）矛盾，导致 2 寮学生无法注册。）
    """
    expected_gender = "male" if dorm_unit in (1, 2) else "female"
    pattern = _ROOM_PATTERN_BY_DORM.get(dorm_unit)
    if (
        pattern is None
        or gender != expected_gender
        or re.match(pattern, room_no) is None
    ):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_ROOM_FORMAT",
                "message": (
                    f"room_no '{room_no}' と dorm_unit={dorm_unit} / gender={gender} "
                    "が不整合です (1寮=M***+male / 2寮=A*+male / 4寮=W***+female)"
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
@limiter.limit(
    # 注册接口：6 位注册码暴力枚举防护
    # 10次/小时/IP — 正常学生注册顶多 1-2 次，10 次已足够容错
    "10/hour"
)
def create_account(
    request: Request,
    body: schemas.StudentAccountCreateIn,
    db: Session = Depends(get_db),
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
    validate_room_dorm_match(body.room_no, body.dorm_unit, body.gender)

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
    # 查重键 strip + lower（大小写不敏感，与 login_student 邮箱查找口径一致）；
    # 存库同样 strip（见下方 email=body.email.strip()）但不 lower —— 保留客户端大小写，
    # 靠 lower(email) 唯一索引兜大小写重复。strip 存/查两侧一致，防带空白值绕过索引（backend#20）。
    if body.email:
        email_key = body.email.strip().lower()
        existing_email = db.scalars(
            select(models.Student).where(func.lower(models.Student.email) == email_key)
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
        # 存前 strip：查重键用 body.email.strip().lower()，若存原始带空白值（" Foo@x "）
        # 则 lower(email) 索引算出带空白的键、绕过唯一约束 → 存值与查重口径必须一致（审查 backend#20）。
        email=body.email.strip() if body.email else None,
        phone=body.phone,
    )
    db.add(student)
    # accounts-be-2：上面的学号/email 查重是 check-then-insert，两个并发请求可能都通过前置
    # 查重、第二个写入时才撞 DB 约束。uq_students_no 撞约束在 flush（INSERT students）这一刻
    # 抛 IntegrityError（不是 commit）→ 必须把 flush + 后续写入一起纳入兜底。捕获后回滚重查
    # 判断撞因，返回与前置查重同样的 422 业务错误而非不透明 500（跨 SQLite/PG 一致，不依赖约束名）。
    # 注：学号有 uq_students_no 唯一约束、email 有大小写不敏感表达式唯一索引
    # uq_students_email_lower（审查 backend#20 已加）→ 并发撞任一约束都会在 flush 抛
    # IntegrityError，下面 except 里 STUDENT_NO_TAKEN / EMAIL_TAKEN 两条分支现均可能被触发。
    try:
        db.flush()  # INSERT students；uq_students_no 撞约束在此抛
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
        # B7 存疑：不改。spec §7.16.2 规则 5 明确「注册码本身可重用
        # （有效期内多个学生可用同一码注册）」— 集团登记场景，设计是有意的多人共用 5 分钟窗口。
        # invalidated_at 只在 /refresh 生成新码时由 admin_registration_code.py 设置，
        # 注册成功本身不作废码，行为正确。
        db.commit()
    except IntegrityError:
        db.rollback()
        dup_student = db.scalars(
            select(models.Student).where(
                models.Student.grade_code == body.grade_code,
                models.Student.class_code == body.class_code,
                models.Student.seat_no == body.seat_no,
            )
        ).first()
        if dup_student is not None:
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
        if body.email:
            email_key = body.email.strip().lower()
            dup_email = db.scalars(
                select(models.Student).where(
                    func.lower(models.Student.email) == email_key
                )
            ).first()
            if dup_email is not None:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "EMAIL_TAKEN",
                        "message": f"email {body.email} は既に使われています",
                    },
                )
        raise
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


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_me(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """B2 — 学生自己删除账号（App Store 审核规则 5.1.1(v) 强制要求）。

    设计选择：软删除（保留历史记录完整性）
    - Student.status → 'paused'（不存在 'deleted' 枚举值；点呼历史 / 申请历史不物理删，保留审计用）
    - Account 行保留但 password_hash 换成随机不可用口令的合法 bcrypt 哈希（防止继续登录，
      且登录校验仍走完整 bcrypt 耗时，避免空哈希时序侧信道——审查 backend#18）
    - 写 AuditLog 留痕，action='account.delete_self' 区分"自删"语义

    用 'paused' 而非 'deleted' 的原因：'deleted' 不在 ck_students_status
    CHECK 枚举里，而 'paused' 已在枚举内。这里复用 'paused' 表示"账号已停用/自删"。
    （已知局限：自删与管理员停用都落到 'paused'，状态层面无法区分，
    要分辨自删需看 AuditLog 的 action='account.delete_self'。）

    Account.student_id 有 ondelete='CASCADE'，
    但物理删 Student 会连锁删 Account + 所有申请历史 — 违反审计完整性，
    所以选软删而非 db.delete()。
    """
    now = datetime.now(timezone.utc)

    # 软删 Student — 用 'paused' 状态（已在 ck_students_status CHECK 枚举里）
    # 'deleted' 不在 CHECK 枚举，物理删除会破坏点呼/申请历史审计完整性，
    # 所以用 paused 表示"账号已停用/自删"，保留所有历史行
    student.status = "paused"

    # Account：换成随机不可用口令的合法 bcrypt 哈希，防止继续登录；
    # 保留行本身（历史审计用）。不用空串——空哈希会让 bcrypt 瞬间失败，
    # 形成时序侧信道（审查 backend#18）。
    account = db.scalars(
        select(models.Account).where(models.Account.student_id == student.id)
    ).first()
    if account:
        account.password_hash = security.hash_password(secrets.token_urlsafe(32))

    # 审计日志
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="account.delete_self",
            target_type="student",
            target_id=student.id,
            payload={"student_no": student.student_no, "deleted_at": now.isoformat()},
        )
    )
    db.commit()
    return  # 204 No Content
