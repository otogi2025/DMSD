"""学生注册码 admin 端点。

权威 spec：
- BACKEND_DESIGN_LOG.md §5.x（教师 admin 学生登录码）
- system_features.md §7.16（核心规则 8 条）

2026-05-03 itsuki 拍板背景：App Store 上架对策。完整经过见内部开发日志。

权限（2026-06-14 itsuki 拍板）：
- 5 个权限组全部可完整使用（C_REG_CODE 矩阵全 MANAGE）。
- 演示账号同样可见 / 操作真实注册码 —— itsuki 在知情（演示老师可用真码注册真实学生、
  破坏 is_demo 演示隔离）的前提下选择取消 6-08 加的 assert_not_demo_teacher 闸，理由是
  演示便利优先、不愿做演示专用假码。决策记录见 logs/decisions/decision_log.md。
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import require_permission

router = APIRouter(
    prefix="/api/v1/admin/registration-code",
    tags=["admin / registration-code"],
)

# §7.16.2-4: 注册码有效期（应用层算 expires_at，不依赖 DB default）。
# 30 分钟自动失效（itsuki 2026-05-31 拍板：老师生成后写黑板 / 口头告知，30 分钟够全班输入；
# 老师也可点「关闭」手动提前作废 —— 见下面 close 端点）。
REGISTRATION_CODE_TTL_MINUTES = 30


def _generate_code() -> str:
    """生成 6 桁随机数字。理论碰撞概率 1/百万，实际靠应用层 retry 兜底。
    上限 999998 — '999999' 是审核员永久码 reserved（spec §7.16 例外条款）。
    必须用 secrets（密码学随机）：注册码是换取真实学生账号的凭据，
    random 的 Mersenne Twister 可由输出预测后续值（2026-07-17 审查安-中-3 修复）。
    """
    return f"{secrets.randbelow(999999):06d}"


def _to_out(row: models.StudentRegistrationCode) -> schemas.RegistrationCodeOut:
    """ORM row → 响应 DTO（剩余秒数 = 算出字段，给客户端做倒计时）。"""
    now = datetime.now(timezone.utc)
    # expires_at 经 TZDateTime 类型层读回，必带时区（JST），与 now（带 UTC 时区）直接相减安全；
    # 不再在此手动补 tzinfo（旧补丁是 TZDateTime 上线前的遗留，现已由类型层统一保证）。
    diff_seconds = (row.expires_at - now).total_seconds()
    return schemas.RegistrationCodeOut(
        code=row.code,
        created_at=row.created_at,
        expires_at=row.expires_at,
        expires_in_seconds=max(0, int(diff_seconds)),
    )


@router.get("/current", response_model=schemas.RegistrationCodeOut | None)
def get_current(
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_REG_CODE, permissions.VIEW)
    ),
    db: Session = Depends(get_db),
):
    """返回当前生效的码；没有则返回 null。

    教师 Web「学生注册码」面板挂载时调用，每 30 秒轮询一次。
    """
    # 2026-06-14 itsuki 拍板：演示账号同样可读真实注册码（取消 assert_not_demo_teacher 闸）。
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_REG_CODE, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """生成新码 + 立即作废旧码（§7.16.2 规则 3）。

    流程：
        1. UPDATE 既有 active SET invalidated_at = now()
        2. 生成 6 桁随机数字（碰撞时 retry）
        3. INSERT 新行
        4. 写 audit log
    """
    # 2026-06-14 itsuki 拍板：演示账号同样可刷新注册码（取消 assert_not_demo_teacher 闸）。
    now = datetime.now(timezone.utc)

    # 1. 把所有现存 active 码作废（§7.16.2 规则 3 — 同时只能 1 个有效）
    #    审核员永久码（is_reviewer=True）不作废 — spec §7.16 例外条款
    # 审查 backend#23：先对目标 active 行加行锁，缩小并发 refresh 撞车窗口；但行锁挡不住
    # 「零 active 行时并发各插一条」和 PostgreSQL EvalPlanQual 窗口 → 真正防线是
    # models 的部分唯一索引 uq_src_one_active（同时至多 1 个 active 非审核员码），
    # 下面插入撞该索引时抛 IntegrityError → 回滚 + 409（后到者重试即拿到最新码）。
    active_rows = list(
        db.scalars(
            select(models.StudentRegistrationCode)
            .where(
                models.StudentRegistrationCode.invalidated_at.is_(None),
                models.StudentRegistrationCode.is_reviewer.is_(False),
            )
            .with_for_update()
        ).all()
    )
    for row in active_rows:
        row.invalidated_at = now

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
    try:
        db.flush()  # 撞 uq_src_one_active（已有 active 非审核员码）在此抛
    except IntegrityError:
        # 审查 backend#23：并发 refresh 已有一方胜出并留下 active 码 → 整体回滚，
        # 让后到者 409 重试（重试会读到胜方的最新码），绝不留下第二条 active 码。
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CODE_REFRESH_CONFLICT",
                "message": "登録コードの更新が競合しました。もう一度お試しください",
            },
        )

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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_REG_CODE, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """老师手动关闭当前注册码 —— 立即作废、不生成新码（itsuki 2026-05-31：点「关闭」即无效）。

    把现存 active 非审核员码标 invalidated_at；审核员永久码不动。
    没有 active 码时也安全返回（幂等）。
    """
    # 2026-06-14 itsuki 拍板：演示账号同样可关闭注册码（取消 assert_not_demo_teacher 闸）。
    now = datetime.now(timezone.utc)
    # 只关「生效中（未过期）」的码 —— 与 /current 同口径（invalidated IS NULL + expires_at > now）。
    # 过期码 /current 本就返回 null → close 应 no-op、不记 audit（Codex 5.5 P3）。
    # refresh 保证同时最多 1 个生效码，直接 SELECT 这一行再改：既能拿到 row 写 audit log，
    # 也避开 bulk update().where(expires_at > now) 在 ORM Python 端 evaluate 时的额外开销。
    # （时区比较本身已安全 —— expires_at 经 TZDateTime 读回必带时区，与 now 带 UTC 时区可直接比。）
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_REG_CODE, permissions.VIEW)
    ),
    db: Session = Depends(get_db),
):
    """过去发行历史（新→旧）。

    §7.16.5 功能矩阵的「码生成 / 使用 audit log」中「生成侧」view。
    「使用侧」view（哪个学生用了哪个码注册）= 单独 endpoint，v1.1 再做。
    """
    # 2026-06-14 itsuki 拍板：演示账号同样可读注册码历史（取消 assert_not_demo_teacher 闸）。
    # 审查 backend#2：排除审核员永久码 —— current/refresh/close 三端点都显式过滤
    # is_reviewer，唯独 history 漏了，老师打开履历就能看到审核员码原文。补齐口径。
    rows = db.execute(
        select(
            models.StudentRegistrationCode,
            models.Teacher.name,
        )
        .join(
            models.Teacher,
            models.StudentRegistrationCode.created_by == models.Teacher.id,
        )
        .where(models.StudentRegistrationCode.is_reviewer.is_(False))
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
