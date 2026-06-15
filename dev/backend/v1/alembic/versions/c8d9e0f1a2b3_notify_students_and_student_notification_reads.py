"""三表加 notify_students + 新建 student_notification_reads（§7.13.1 投稿通知开关）

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-06-15 00:00:10.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 公告 / 行事 / 巴士 各加「投稿时是否通知学生」开关。
    # 历史行回填 false（不补发通知，避免老内容突然轰炸学生）。
    op.add_column(
        "announcements",
        sa.Column(
            "notify_students",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "dorm_events",
        sa.Column(
            "notify_students",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "bus_routes",
        sa.Column(
            "notify_students",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    # 学生通知中心 feed 里 巴士 / 行事 的已读跟踪（公告复用 announcement_reads）。
    # ref_id 跨 bus_routes / dorm_events 两表、按 kind 区分，DB 层不加 FK、应用层保证。
    op.create_table(
        "student_notification_reads",
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=8), nullable=False),
        sa.Column("ref_id", sa.Uuid(), nullable=False),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("student_id", "kind", "ref_id"),
        sa.CheckConstraint(
            "kind IN ('bus','event')", name="ck_student_notif_read_kind"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("student_notification_reads")
    op.drop_column("bus_routes", "notify_students")
    op.drop_column("dorm_events", "notify_students")
    op.drop_column("announcements", "notify_students")
