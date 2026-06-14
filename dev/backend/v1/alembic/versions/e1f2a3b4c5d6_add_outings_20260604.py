"""add outings table (外出申請 単一先生確認) 20260604

2026-06-04: 外出申请（当天回寮的短时间外出）单一老师确认功能 — 新建 outings 表。
跟出寮届（applications）分开：不过夜 / 没有多级审查 / 一名老师确认即可，
确认老师从登录令牌自动记录（confirmed_by_teacher_id），不信任客户端传入。
见 system_features §7.2.7。itsuki 2026-06-04 拍板。

Revision ID: e1f2a3b4c5d6
Revises: c9d0e1f2a3b4
Create Date: 2026-06-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("outing_date", sa.Date(), nullable=False),
        sa.Column("destination", sa.Text(), nullable=True),
        sa.Column("leave_time", sa.Time(), nullable=True),
        sa.Column("return_time", sa.Time(), nullable=True),
        sa.Column("taxi_reservation_time", sa.Time(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_by_teacher_id", sa.Uuid(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["confirmed_by_teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending','approved','withdrawn')", name="ck_outing_status"
        ),
    )
    op.create_index("idx_outing_student", "outings", ["student_id", "status"])
    op.create_index("idx_outing_status_date", "outings", ["status", "outing_date"])


def downgrade() -> None:
    op.drop_index("idx_outing_status_date", table_name="outings")
    op.drop_index("idx_outing_student", table_name="outings")
    op.drop_table("outings")
