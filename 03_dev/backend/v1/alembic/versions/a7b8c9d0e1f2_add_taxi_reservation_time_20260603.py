"""add taxi_reservation_time to applications 20260603

2026-06-03: 出租车预约功能 — applications 表加 taxi_reservation_time
（学生希望坐出租车出寮 / 帰寮时填的时刻；null = 不预约）。
出寮届三种（帰省 / 外泊 / 帰国）共通。

Revision ID: a7b8c9d0e1f2
Revises: b2c3d4e5f6a1
Create Date: 2026-06-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("taxi_reservation_time", sa.Time(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("applications", "taxi_reservation_time")
