"""add content_reports + song/lost_found soft delete 20260720

2026-07-20: App Store 审核指南 1.2 UGC 治理（itsuki 拍板 A 方案）。
学生互见投稿（点歌 / 公告回复 / 遗失物）此前无任何治理机制
（原「通报+累计封禁」体系 itsuki 2026-06-13 拍板彻底删除），
上架合规要求最低限的「通報 + 管理删除」：
1. 新表 content_reports — 学生通報记录（content_type + content_id 指向投稿）
2. song_requests / lost_found_posts 各加 deleted_at — 老师软删列
   （announcement_replies 本来就有 deleted_at，不动）

Revision ID: a1c2e3f4b5d6
Revises: d3f7a1b9c2e4
Create Date: 2026-07-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1c2e3f4b5d6"
down_revision: Union[str, Sequence[str], None] = "d3f7a1b9c2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "content_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("content_type", sa.String(24), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column(
            "reporter_student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "handled_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "content_type IN ('song','announcement_reply','lost_found')",
            name="ck_creport_type",
        ),
        sa.CheckConstraint("status IN ('open','handled')", name="ck_creport_status"),
        sa.UniqueConstraint(
            "content_type",
            "content_id",
            "reporter_student_id",
            name="uq_creport_target_reporter",
        ),
    )
    op.create_index("ix_content_reports_content_id", "content_reports", ["content_id"])
    op.create_index(
        "ix_content_reports_reporter_student_id",
        "content_reports",
        ["reporter_student_id"],
    )
    op.create_index(
        "idx_creport_status_created", "content_reports", ["status", "created_at"]
    )
    op.add_column(
        "song_requests",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "lost_found_posts",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("lost_found_posts", "deleted_at")
    op.drop_column("song_requests", "deleted_at")
    op.drop_index("idx_creport_status_created", table_name="content_reports")
    op.drop_index(
        "ix_content_reports_reporter_student_id", table_name="content_reports"
    )
    op.drop_index("ix_content_reports_content_id", table_name="content_reports")
    op.drop_table("content_reports")
