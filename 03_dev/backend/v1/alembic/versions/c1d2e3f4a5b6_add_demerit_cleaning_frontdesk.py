"""add demerit_event cleaning_assignment front_desk_item

2026-05-27: P0 / P1 实装配套迁移 — 5-27 凌晨 CC 加 3 张新表，但漏写 migration。
本 revision 补齐 production 部署所需 schema。

- demerit_event: 扣分事件 (spec §7.5 規律処分)
- cleaning_assignment: 清扫安排 (spec §7.10)
- front_desk_item: 宅配 + 失物招领 (spec §7.12)

SQLite 兼容: ENUM 改 String + CheckConstraint

Revision ID: c1d2e3f4a5b6
Revises: b9c0d1e2f3a4
Create Date: 2026-05-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b9c0d1e2f3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # demerit_event — 扣分事件 (spec §7.5)
    # ---------------------------------------------------------------
    op.create_table(
        "demerit_event",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_event_id", sa.Uuid(), nullable=True),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "revoked_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("revoke_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "source_type IN ('rollcall_late','rollcall_absent','cleaning_failed',"
            "'curfew_violation','study_absent','manual')",
            name="ck_demerit_source",
        ),
    )
    op.create_index("ix_demerit_event_student_id", "demerit_event", ["student_id"])
    op.create_index("ix_demerit_event_month", "demerit_event", ["month"])
    op.create_index(
        "idx_demerit_student_month", "demerit_event", ["student_id", "month"]
    )
    op.create_index(
        "idx_demerit_month_active", "demerit_event", ["month", "revoked_at"]
    )

    # ---------------------------------------------------------------
    # cleaning_assignment — 清扫安排 (spec §7.10)
    # ---------------------------------------------------------------
    op.create_table(
        "cleaning_assignment",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=False,
        ),
        sa.Column("area", sa.String(length=32), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="assigned"
        ),
        sa.Column(
            "assigned_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "inspected_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "demerit_event_id",
            sa.Uuid(),
            sa.ForeignKey("demerit_event.id"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "area IN ('浴室','廊下','トイレ','共用キッチン','階段','玄関','ロビー','その他')",
            name="ck_cleaning_area",
        ),
        sa.CheckConstraint(
            "status IN ('assigned','done','passed','failed','skipped')",
            name="ck_cleaning_status",
        ),
    )
    op.create_index(
        "ix_cleaning_assignment_student_id", "cleaning_assignment", ["student_id"]
    )
    op.create_index(
        "ix_cleaning_assignment_scheduled_date",
        "cleaning_assignment",
        ["scheduled_date"],
    )
    op.create_index(
        "idx_cleaning_student_date",
        "cleaning_assignment",
        ["student_id", "scheduled_date"],
    )

    # ---------------------------------------------------------------
    # front_desk_item — 宅配 + 失物招领 (spec §7.12)
    # ---------------------------------------------------------------
    op.create_table(
        "front_desk_item",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_by_teacher_id",
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
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("picked_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "kind IN ('delivery','lost_and_found')", name="ck_front_desk_kind"
        ),
        sa.CheckConstraint(
            "status IN ('pending','notified','picked_up','expired','discarded')",
            name="ck_front_desk_status",
        ),
    )
    op.create_index(
        "idx_front_desk_status_expires",
        "front_desk_item",
        ["status", "expires_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_front_desk_status_expires", table_name="front_desk_item")
    op.drop_table("front_desk_item")

    op.drop_index("idx_cleaning_student_date", table_name="cleaning_assignment")
    op.drop_index(
        "ix_cleaning_assignment_scheduled_date", table_name="cleaning_assignment"
    )
    op.drop_index("ix_cleaning_assignment_student_id", table_name="cleaning_assignment")
    op.drop_table("cleaning_assignment")

    op.drop_index("idx_demerit_month_active", table_name="demerit_event")
    op.drop_index("idx_demerit_student_month", table_name="demerit_event")
    op.drop_index("ix_demerit_event_month", table_name="demerit_event")
    op.drop_index("ix_demerit_event_student_id", table_name="demerit_event")
    op.drop_table("demerit_event")
