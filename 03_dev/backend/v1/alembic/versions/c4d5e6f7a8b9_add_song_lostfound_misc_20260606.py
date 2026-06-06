"""add song_requests + lost_found_posts + misc_requests 20260606

2026-06-06: iOS 三个边缘功能接真后端 — 点歌（UI「リクエスト曲」最小版）/
遗失物社区投稿 / 修繕·来訪·代理受取 杂项申请。itsuki 2026-06-06 拍板「全做」。

Revision ID: c4d5e6f7a8b9
Revises: b1c2d3e4f5a6
Create Date: 2026-06-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 点歌（最小版）
    op.create_table(
        "song_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("dorm_unit", sa.SmallInteger(), nullable=False),
        sa.Column("song_title", sa.Text(), nullable=False),
        sa.Column("artist", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_song_requests_student_id", "song_requests", ["student_id"])
    op.create_index(
        "idx_song_dorm_created", "song_requests", ["dorm_unit", "created_at"]
    )

    # 遗失物社区投稿
    op.create_table(
        "lost_found_posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("post_type", sa.String(length=8), nullable=False),
        sa.Column("item_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("post_type IN ('found','lost')", name="ck_lfp_type"),
        sa.CheckConstraint("status IN ('open','resolved')", name="ck_lfp_status"),
    )
    op.create_index(
        "ix_lost_found_posts_student_id", "lost_found_posts", ["student_id"]
    )
    op.create_index(
        "idx_lfp_status_created", "lost_found_posts", ["status", "created_at"]
    )

    # 修繕 / 来訪 / 代理受取 杂项申请
    op.create_table(
        "misc_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("confirmed_by_teacher_id", sa.Uuid(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["confirmed_by_teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "kind IN ('repair','guest','proxy_receipt')", name="ck_misc_kind"
        ),
        sa.CheckConstraint(
            "status IN ('pending','confirmed','withdrawn')", name="ck_misc_status"
        ),
    )
    op.create_index("ix_misc_requests_student_id", "misc_requests", ["student_id"])
    op.create_index(
        "idx_misc_student_status", "misc_requests", ["student_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("idx_misc_student_status", table_name="misc_requests")
    op.drop_index("ix_misc_requests_student_id", table_name="misc_requests")
    op.drop_table("misc_requests")
    op.drop_index("idx_lfp_status_created", table_name="lost_found_posts")
    op.drop_index("ix_lost_found_posts_student_id", table_name="lost_found_posts")
    op.drop_table("lost_found_posts")
    op.drop_index("idx_song_dorm_created", table_name="song_requests")
    op.drop_index("ix_song_requests_student_id", table_name="song_requests")
    op.drop_table("song_requests")
