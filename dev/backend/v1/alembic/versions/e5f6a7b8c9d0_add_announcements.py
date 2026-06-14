"""add_announcements

2026-05-04: 老师公告（お知らせ，§7.15）— 2026-05-03 拍板。
  - announcements: 公告本体（title / body / scope / author / 软删 deleted_at）
  - announcement_reads: 已读跟踪（announcement_id × student_id 复合主键）
  - announcement_replies: 回复（学生和老师都能发，全员互见，§7.15.6）

scope: all / male / female（按学生 gender 自动过滤）
SQLite 兼容: 不支持 ENUM → 改用 String 列 + CHECK 约束

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("scope", sa.String(length=8), nullable=False),
        sa.Column(
            "author_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "scope IN ('all','male','female')", name="ck_announcement_scope"
        ),
    )
    op.create_index(
        "idx_announcement_created", "announcements", ["created_at"]
    )
    op.create_index(
        "idx_announcement_scope_active", "announcements", ["scope", "deleted_at"]
    )

    op.create_table(
        "announcement_reads",
        sa.Column(
            "announcement_id",
            sa.Uuid(),
            sa.ForeignKey("announcements.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "announcement_replies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "announcement_id",
            sa.Uuid(),
            sa.ForeignKey("announcements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("author_kind", sa.String(length=8), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "author_kind IN ('student','teacher')", name="ck_reply_author_kind"
        ),
    )
    op.create_index(
        "idx_reply_announcement",
        "announcement_replies",
        ["announcement_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_reply_announcement", table_name="announcement_replies")
    op.drop_table("announcement_replies")
    op.drop_table("announcement_reads")
    op.drop_index("idx_announcement_scope_active", table_name="announcements")
    op.drop_index("idx_announcement_created", table_name="announcements")
    op.drop_table("announcements")
