"""学生注册码 admin 端点（限定寮务管理 role）。

权威 spec：
- BACKEND_DESIGN_LOG.md §5.x（教师 admin 学生登录码）
- system_features.md §7.16（核心规则 8 条）

2026-05-03 itsuki 拍板背景：App Store 上架对策。完整经过 → 05_logs/raw/2026-05-03.md §11。
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import assert_not_demo_teacher, require_teacher_roles

router = APIRouter(
    prefix="/api/v1/admin/registration-code",
    tags=["admin / registration-code"],
)

# §7.16.2-4: 注册码有效期（应用层算 expires_at，不依赖 DB default）。
# 30 分钟自动失效（itsuki 2026-05-31 拍板：老师生成后写黑板 / 口头告知，30 分钟够全班输入；
# 老师也可点「关闭」手动提前作废 —— 见下面 close 端点）。
REGISTRATION_CODE_TTL_MINUTES = 30

# §3.4 教师权限「寮务管理」对应的 role（spec 未细分，先取 3 个最相关）
ADMIN_ROLES = ("寮務部長", "寮務課長", "管理係")


def _generate_code() -> str:
    """生成 6 桁随机数字。理论碰撞概率 1/百万，实际靠应用层 retry 兜底。
    上限 999998 — '999999' 是审核员永久码 reserved（spec §7.16 例外条款）。
    """
    return f"{random.randint(0, 999998):06d}"


def _to_out(row: models.StudentRegistrationCode) -> schemas.RegistrationCodeOut:
    """ORM row → 响应 DTO（剩余秒数 = 算出字段，给客户端做倒计时）。"""
    now = datetime.now(timezone.utc)
    # SQLite 取出来的 datetime 没 tzinfo，补成 UTC 再算差
    expires_at = (
        row.expires_at
        if row.expires_at.tzinfo is not None
        else row.expires_at.replace(tzinfo=timezone.utc)
    )
    diff_seconds = (expires_at - now).total_seconds()
    return schemas.RegistrationCodeOut(
        code=row.code,
        created_at=row.created_at,
        expires_at=row.expires_at,
        expires_in_seconds=max(0, int(diff_seconds)),
    )


@router.get("/current", response_model=schemas.RegistrationCodeOut | None)
def get_current(
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """返回当前生效的码；没有则返回 null。

    教师 Web「学生注册码」面板挂载时调用，每 30 秒轮询一次。
    """
    # 演示老师禁读真实注册码（否则能拿真实码→自注册建真实学生账号、绕过整套演示隔离）→ 403
    assert_not_demo_teacher(teacher)
    now = datetime.now(timezone.utc)
    row = db.scalars(
        select(models.StudentRegistrationCode)
        .where(
            models.StudentRegistrationCode.invalidated_at.is_(None),
            models.StudentRegistrationCode.expires_at > now,
            # 审核员永久码不出现在老师面板（防泄漏：老师看不到 = 没法截图传播）
            models.StudentRegistrationCode.is_reviewer.is_(False),
        )
        .order_by(models.StudentRegistrationCode.created_at.desc())
        .limit(1)
    ).first()
    if not row:
        return None
    return _to_out(row)


@router.post(
    "/refresh",
    response_model=schemas.RegistrationCodeOut,
    status_code=status.HTTP_201_CREATED,
)
def refresh_code(
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """生成新码 + 立即作废旧码（§7.16.2 规则 3）。

    流程：
        1. UPDATE 既有 active SET invalidated_at = now()
        2. 生成 6 桁随机数字（碰撞时 retry）
        3. INSERT 新行
        4. 写 audit log
    """
    # 演示老师禁止刷新全局学生注册码（会作废真实码、绕过演示隔离）→ 403
    assert_not_demo_teacher(teacher)
    now = datetime.now(timezone.utc)

    # 1. 把所有现存 active 码作废（§7.16.2 规则 3 — 同时只能 1 个有效）
    #    审核员永久码（is_reviewer=True）不作废 — spec §7.16 例外条款
    db.execute(
        update(models.StudentRegistrationCode)
        .where(
            models.StudentRegistrationCode.invalidated_at.is_(None),
            models.StudentRegistrationCode.is_reviewer.is_(False),
        )
        .values(invalidated_at=now)
    )

    # 2. 生成新码（5 次 retry — 全部碰撞实际概率为零，仅作兜底）
    code = ""
    for _ in range(5):
        code = _generate_code()
        existing = db.scalars(
            select(models.StudentRegistrationCode)
            .where(models.StudentRegistrationCode.code == code)
            .limit(1)
        ).first()
        if existing is None:
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "CODE_GEN_FAILED", "message": "码生成失败"},
        )

    # 3. INSERT — 显式给 created_at 微秒精度，绕开 SQLite server_default 秒级精度
    #    导致连续两次 refresh 的 created_at 相同、history 排序不稳定的问题
    row = models.StudentRegistrationCode(
        code=code,
        created_by=teacher.id,
        created_at=now,
        expires_at=now + timedelta(minutes=REGISTRATION_CODE_TTL_MINUTES),
    )
    db.add(row)
    db.flush()

    # 4. audit log（§4.10 末尾要求）
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="registration_code.refresh",
            target_type="student_registration_code",
            target_id=row.id,
            payload={"new_code": code},
        )
    )
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.post("/close", status_code=status.HTTP_204_NO_CONTENT)
def close_code(
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """老师手动关闭当前注册码 —— 立即作废、不生成新码（itsuki 2026-05-31：点「关闭」即无效）。

    把现存 active 非审核员码标 invalidated_at；审核员永久码不动。
    没有 active 码时也安全返回（幂等）。
    """
    # 演示老师禁止关闭全局学生注册码（会作废真实码、绕过演示隔离）→ 403
    assert_not_demo_teacher(teacher)
    now = datetime.now(timezone.utc)
    # 只关「生效中（未过期）」的码 —— 与 /current 同口径（invalidated IS NULL + expires_at > now）。
    # 过期码 /current 本就返回 null → close 应 no-op、不记 audit（Codex 5.5 P3）。
    # refresh 保证同时最多 1 个生效码，直接改 SELECT 出来的这一行；不用 bulk update().where(expires_at > now)，
    # 否则 ORM 在 Python 端 evaluate 该 where 会撞 naive(SQLite 读回) / aware(now) datetime 比较 → TypeError。
    active = db.scalars(
        select(models.StudentRegistrationCode)
        .where(
            models.StudentRegistrationCode.invalidated_at.is_(None),
            models.StudentRegistrationCode.expires_at > now,
            models.StudentRegistrationCode.is_reviewer.is_(False),
        )
        .order_by(models.StudentRegistrationCode.created_at.desc())
        .limit(1)
    ).first()
    if active is not None:
        active.invalidated_at = now
        db.add(
            models.AuditLog(
                actor_type="teacher",
                actor_id=teacher.id,
                action="registration_code.close",
                target_type="student_registration_code",
                target_id=active.id,
                payload={"code": active.code},
            )
        )
    db.commit()


@router.get("/history", response_model=schemas.RegistrationCodeHistoryOut)
def get_history(
    limit: int = Query(50, ge=1, le=200),
    teacher: models.Teacher = Depends(require_teacher_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """过去发行历史（新→旧）。

    §7.16.5 功能矩阵的「码生成 / 使用 audit log」中「生成侧」view。
    「使用侧」view（哪个学生用了哪个码注册）= 单独 endpoint，v1.1 再做。
    """
    # 演示老师禁读真实注册码历史（含真实码明文）→ 403
    assert_not_demo_teacher(teacher)
    rows = db.execute(
        select(
            models.StudentRegistrationCode,
            models.Teacher.name,
        )
        .join(
            models.Teacher,
            models.StudentRegistrationCode.created_by == models.Teacher.id,
        )
        .order_by(models.StudentRegistrationCode.created_at.desc())
        .limit(limit)
    ).all()
    items = [
        schemas.RegistrationCodeHistoryEntry(
            code=row.code,
            created_at=row.created_at,
            expires_at=row.expires_at,
            invalidated_at=row.invalidated_at,
            created_by_teacher_name=name,
        )
        for row, name in rows
    ]
    return schemas.RegistrationCodeHistoryOut(items=items)
