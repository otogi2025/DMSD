"""设备推送令牌端点 — spec §7.13。

POST /api/v1/notifications/device-token
  学生 App 启动时调用，注册 / 更新本机推送令牌。
  幂等：同一 token 已存在 → 只更新 last_seen_at，不重复插入。
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_student

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["push"])


def _claim_existing_token(
    existing: models.DeviceToken,
    *,
    student_id: uuid.UUID,
    platform: str,
    now: datetime,
) -> bool:
    """把一条已存在的 token 行改挂到当前学生（upsert 复用同一行）。

    为什么允许归属转移（而不是直接拒绝）：
      APNs / FCM 的 token 是操作系统按「设备 + App 安装」发的，不是按账号发的。
      同一台手机换人登录、或设备转手后重装 App，系统可能复用同一个 token 串。
      这种情况 token 必须跟着新主人走 —— 否则发给旧主人的推送会继续投到一台
      他已经不再持有的设备上（比单纯归属转移更严重的隐私泄漏）。
      所以「最后注册者拥有该 token」对设备绑定型 token 来说是语义正确的。

    安全说明（审查 E-中-05 / IDOR 推送劫持）：
      本端点无法只凭一次注册请求区分「真·设备转手」和「攻击者拿到他人 token 串后
      冒名注册」—— 两者请求里都只有一个 token 串 + 一个 JWT，没有「物理持有该设备」
      的证明。真正的防线是平台层校验（APNs / FCM 投递回执），但当前 push.py 的投递
      还是 stub 未实现。在补上平台层校验之前，这里至少把「归属发生转移」这件事
      记成 warning 日志，让安全事件可观测、可审计（之前是静默转移，查都查不到）。

    返回值：归属是否发生了转移（旧主人 != 当前学生）。
    """
    transferred = existing.student_id != student_id
    if transferred:
        logger.warning(
            "device-token 归属转移：token_id=%s 从学生 %s 改挂到学生 %s（platform=%s）",
            existing.id,
            existing.student_id,
            student_id,
            platform,
        )
    existing.student_id = student_id
    existing.platform = platform
    existing.last_seen_at = now
    existing.revoked_at = None  # 如果之前被 revoke，复活
    return transferred


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
    # 注意：不加 revoked_at IS NULL — 已撤销的 token 也要查到，走"复活旧行"路径，
    # 避免撞 UniqueConstraint("token") 导致 500
    existing = db.scalars(
        select(models.DeviceToken).where(
            models.DeviceToken.token == body.token,
        )
    ).first()

    if existing:
        # upsert 复用同一行（不撞唯一约束）；归属若发生转移会在 helper 里记 warning 日志。
        # 归属转移（旧主人 != 当前学生）视为"新建"，created=True。
        created = _claim_existing_token(
            existing,
            student_id=student.id,
            platform=body.platform,
            now=now,
        )
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
    try:
        db.commit()
    except IntegrityError:
        # 并发竞态：另一个请求在「查不到 → 插入」之间先插了同一 token（撞 UNIQUE）。
        # 回滚后复用那行、改成当前学生，兜成幂等成功（codex Finding 5）。
        db.rollback()
        existing = db.scalars(
            select(models.DeviceToken).where(models.DeviceToken.token == body.token)
        ).first()
        if existing is None:
            raise
        created = _claim_existing_token(
            existing,
            student_id=student.id,
            platform=body.platform,
            now=now,
        )
        db.commit()
        db.refresh(existing)
        return schemas.DeviceTokenRegisterOut(
            id=existing.id,
            student_id=existing.student_id,
            platform=existing.platform,
            created=created,
        )
    db.refresh(dt)

    return schemas.DeviceTokenRegisterOut(
        id=dt.id,
        student_id=dt.student_id,
        platform=dt.platform,
        created=True,
    )
