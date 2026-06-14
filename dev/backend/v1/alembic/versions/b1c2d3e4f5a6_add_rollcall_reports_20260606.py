"""add rollcall_reports table (点呼时学生上报：体调/欠席/其他) 20260606

2026-06-06: iOS 点呼界面三个弹窗（体調報告 / 今回欠席の申請 / その他の問題）
接真后端 — 新建 rollcall_reports 表。学生提交一条上报，老师列表可见 + 标记已处理。
kind=health/absence/other；session_id 关联当次点呼场次（可空）。

Revision ID: b1c2d3e4f5a6
Revises: f8a9b0c1d2e3
Create Date: 2026-06-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rollcall_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_teacher_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["rollcall_sessions.id"]),
        sa.ForeignKeyConstraint(["resolved_by_teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("kind IN ('health','absence','other')", name="ck_rcr_kind"),
    )
    op.create_index(
        "ix_rollcall_reports_student_id", "rollcall_reports", ["student_id"]
    )
    op.create_index(
        "idx_rcr_student_created", "rollcall_reports", ["student_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("idx_rcr_student_created", table_name="rollcall_reports")
    op.drop_index("ix_rollcall_reports_student_id", table_name="rollcall_reports")
    op.drop_table("rollcall_reports")
