"""add notifications + notification_reads (老师通知中心) 20260613

2026-06-13: 老师通知中心 阶段1（itsuki 拍板）。新建两张表：
- notifications：把现有事件（申请提交 / 扣分 / 点呼上报）同步成通知行，
  按 (source_table, source_id) 幂等去重；is_demo 做 realm 隔离。
- notification_reads：老师已读记录，每老师每通知最多 1 行（有行 = 已读）。
填充逻辑在 routers/notifications.py（取 feed 时扫现有事件表同步），不写各事件产生点钩子。

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-06-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("source_table", sa.String(length=48), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("related_student_id", sa.Uuid(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["related_student_id"], ["students.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_table", "source_id", name="uq_notif_source"),
    )
    op.create_index("idx_notif_demo_event", "notifications", ["is_demo", "event_at"])

    op.create_table(
        "notification_reads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["notification_id"], ["notifications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notification_id", "teacher_id", name="uq_notif_read"),
    )
    op.create_index("idx_notif_read_teacher", "notification_reads", ["teacher_id"])


def downgrade() -> None:
    op.drop_index("idx_notif_read_teacher", table_name="notification_reads")
    op.drop_table("notification_reads")
    op.drop_index("idx_notif_demo_event", table_name="notifications")
    op.drop_table("notifications")
