"""通知 (admin / dev) endpoint。

POST /api/v1/notifications/test  — SendGrid 送達 smoke テスト (#6 完成定義)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import assert_not_demo_teacher, require_permission
from ..services import email as email_svc

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("/test", response_model=schemas.NotificationTestOut)
def send_test(
    body: schemas.NotificationTestIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
):
    # 演示老师禁用真实发邮件通道（防滥发 / 钓鱼 / 耗 SendGrid 配额 / 损发信域名信誉）→ 403
    assert_not_demo_teacher(teacher)

    log, status_code, error = email_svc.send_test_email(
        db,
        to=body.to,
        subject=body.subject,
        body_text=body.body_text,
        actor_id=teacher.id,
    )
    db.commit()

    return schemas.NotificationTestOut(
        sent=(log.status == "sent"),
        notification_log_id=log.id,
        sendgrid_status_code=status_code,
        error=error,
    )
