"""设备推送令牌端点 — spec §7.13。

POST /api/v1/notifications/device-token
  学生 App 启动时调用，注册 / 更新本机推送令牌。
  幂等：同一 token 已存在 → 只更新 last_seen_at，不重复插入。
"""

from __future__ import annotations

from datetime import datetime, timezone

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student

router = APIRouter(prefix="/api/v1/notifications", tags=["push"])


@router.post(
    "/device-token",
    response_model=schemas.DeviceTokenRegisterOut,
    status_code=status.HTTP_200_OK,
)
def register_device_token(
    body: schemas.DeviceTokenRegisterIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """注册 / 更新本机推送令牌（幂等）。

    - 同一 token 字符串已存在（且未 revoke）→ 更新 last_seen_at，返回 created=False
    - 新 token → 插入新行，返回 created=True
    - 同一学生可以有多个设备，每台设备有独立行
    """
    now = datetime.now(timezone.utc)

    # 幂等检查：同一 token（不管是不是同一学生，token 全局唯一）
    existing = db.scalars(
        select(models.DeviceToken).where(
            models.DeviceToken.token == body.token,
            models.DeviceToken.revoked_at.is_(None),
        )
    ).first()

    if existing:
        # upsert 复用行：不管 token 原属谁，直接把这行改成当前学生
        # 这样既不会撞唯一约束，推送也会发给新学生（语义正确）
        created = existing.student_id != student.id  # 归属转移视为"新建"
        existing.student_id = student.id
        existing.platform = body.platform
        existing.last_seen_at = now
        existing.revoked_at = None  # 如果之前被 revoke，复活
        db.commit()
        db.refresh(existing)
        return schemas.DeviceTokenRegisterOut(
            id=existing.id,
            student_id=existing.student_id,
            platform=existing.platform,
            created=created,
        )

    # token 全新 → 插入新行
    dt = models.DeviceToken(
        id=uuid.uuid4(),
        student_id=student.id,
        platform=body.platform,
        token=body.token,
        last_seen_at=now,
    )
    db.add(dt)
    db.commit()
    db.refresh(dt)

    return schemas.DeviceTokenRegisterOut(
        id=dt.id,
        student_id=dt.student_id,
        platform=dt.platform,
        created=True,
    )
