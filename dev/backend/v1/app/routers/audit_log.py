"""老师操作记录（操作履历审计）读取端点。

写入侧 = app/audit.py 的 AuditLogMiddleware（老师写操作全量自动记）。
本路由只读，按权限组 C_AUDIT_LOG 把关：只有管理角色
（op / 寮管理者=寮務部長·寮務課長 / 一般宿管=管理係）能查。
演示隔离：演示老师只看演示老师的操作、真老师只看真老师的操作（按 actor 的 is_demo join 过滤）。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import require_permission

router = APIRouter(prefix="/api/v1/admin/audit-logs", tags=["admin / audit-logs"])


@router.get("", response_model=schemas.AuditLogListOut)
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    actor_id: UUID | None = Query(None, description="限定某老师的操作（UUID）"),
    since: datetime | None = Query(None, description="起始时间（含）"),
    until: datetime | None = Query(None, description="结束时间（含）"),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_AUDIT_LOG, permissions.VIEW)
    ),
    db: Session = Depends(get_db),
):
    """操作记录一覧（新→旧）。

    - 演示隔离：只看与查看者同 is_demo 的老师 actor 的记录。
    - 过滤：actor_id（限定某老师）/ since–until（时间范围）。
    - 分页：limit + offset，附 total 便于前端显示总数 / 翻页。
    """
    # 只展示中间件自动记的「METHOD 归一化路径」行（action 以 HTTP 方法 + 空格开头）。
    # 部分端点内部另写语义级 audit 行（action 形如 "registration_code.refresh"，无方法前缀）——
    # 那些是各功能自用的、且会与中间件行重复，故在操作记录页过滤掉，保证同一操作只出现一次。
    _middleware_action = or_(
        models.AuditLog.action.like("POST %"),
        models.AuditLog.action.like("PUT %"),
        models.AuditLog.action.like("PATCH %"),
        models.AuditLog.action.like("DELETE %"),
    )
    # 演示隔离按行上去规范化的 actor_is_demo 列判（不依赖 join），所以**硬删老师后其历史操作行
    # 仍可见**（codex M3 修复）。actor_name 用 LEFT OUTER JOIN 取，老师已删则为 NULL，前端显示
    # 「削除済み」。actor_type 显式过滤老师，叠加只看中间件行：学生 / 系统 actor 记录被排除。
    base = (
        select(models.AuditLog, models.Teacher.name)
        .outerjoin(models.Teacher, models.AuditLog.actor_id == models.Teacher.id)
        .where(
            models.AuditLog.actor_type == "teacher",
            models.AuditLog.actor_is_demo == teacher.is_demo,
            _middleware_action,
        )
    )
    if actor_id is not None:
        base = base.where(models.AuditLog.actor_id == actor_id)
    if since is not None:
        base = base.where(models.AuditLog.created_at >= since)
    if until is not None:
        base = base.where(models.AuditLog.created_at <= until)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    rows = db.execute(
        base.order_by(models.AuditLog.created_at.desc()).limit(limit).offset(offset)
    ).all()
    items = [
        schemas.AuditLogEntry(
            id=row.AuditLog.id,
            created_at=row.AuditLog.created_at,
            actor_type=row.AuditLog.actor_type,
            actor_id=row.AuditLog.actor_id,
            actor_name=row.name,
            action=row.AuditLog.action,
            target_type=row.AuditLog.target_type,
            target_id=row.AuditLog.target_id,
            payload=row.AuditLog.payload,
            ip_address=row.AuditLog.ip_address,
        )
        for row in rows
    ]
    return schemas.AuditLogListOut(items=items, total=total, limit=limit, offset=offset)
