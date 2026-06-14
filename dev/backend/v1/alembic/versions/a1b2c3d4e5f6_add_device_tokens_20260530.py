"""add device_tokens 20260530

新增 1 张表：
- device_tokens   学生设备推送令牌（APNs / FCM）— spec §7.13

Revision ID: a1b2c3d4e5f6
Revises: f7a8b9c0d1e2
Create Date: 2026-05-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # ios = APNs device token / android = FCM registration token
        sa.Column("platform", sa.String(length=8), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # App 每次启动时更新，用来判断 token 是否还活跃
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        # 软删 — revoked_at 非 NULL 表示已失效（App 卸载、用户注销等）
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("platform IN ('ios','android')", name="ck_dt_platform"),
    )
    op.create_index(
        "idx_dt_student_active", "device_tokens", ["student_id", "revoked_at"]
    )
    op.create_index("idx_dt_token", "device_tokens", ["token"])


def downgrade() -> None:
    op.drop_index("idx_dt_token", table_name="device_tokens")
    op.drop_index("idx_dt_student_active", table_name="device_tokens")
    op.drop_table("device_tokens")
