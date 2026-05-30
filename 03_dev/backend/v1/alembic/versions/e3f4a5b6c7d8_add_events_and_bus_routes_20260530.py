"""add events and bus routes 20260530

新增 2 张表：
- dorm_events   行事予定日历 (spec §7.5)
- bus_routes    巴士时刻表 (spec §7.6)

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-05-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e3f4a5b6c7d8"
down_revision: Union[str, Sequence[str], None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 行事予定 (spec §7.5)
    op.create_table(
        "dorm_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "category IN ('学校行事','寮行事','外部','その他')",
            name="ck_dorm_events_category",
        ),
    )
    op.create_index("idx_dorm_events_date", "dorm_events", ["event_date"])

    # 巴士时刻表 (spec §7.6)
    op.create_table(
        "bus_routes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("schedule_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "visible_to",
            sa.String(length=16),
            nullable=False,
            server_default="all",
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "deprecated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
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
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "kind IN ('daily_commute','dorm_special')",
            name="ck_bus_routes_kind",
        ),
        sa.CheckConstraint(
            "visible_to IN ('all','dorm_only','men','women')",
            name="ck_bus_routes_visible_to",
        ),
    )
    op.create_index(
        "idx_bus_routes_kind_deprecated", "bus_routes", ["kind", "deprecated"]
    )
    op.create_index("idx_bus_routes_schedule_at", "bus_routes", ["schedule_at"])


def downgrade() -> None:
    op.drop_index("idx_bus_routes_schedule_at", table_name="bus_routes")
    op.drop_index("idx_bus_routes_kind_deprecated", table_name="bus_routes")
    op.drop_table("bus_routes")

    op.drop_index("idx_dorm_events_date", table_name="dorm_events")
    op.drop_table("dorm_events")
