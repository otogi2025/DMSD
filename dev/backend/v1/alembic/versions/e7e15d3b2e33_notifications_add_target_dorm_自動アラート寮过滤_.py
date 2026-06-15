"""notifications add target_dorm 自動アラート寮过滤 20260616

Revision ID: e7e15d3b2e33
Revises: 37c1e1cd3f1e
Create Date: 2026-06-16 00:12:16.039547

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7e15d3b2e33"
down_revision: Union[str, Sequence[str], None] = "37c1e1cd3f1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. notifications 加 target_dorm（可空）。

    NULL = 全员通知（所有现有通知行）；非 NULL = 仅管辖该 dorm_unit 的老师可见
    （自動アラート用，取 feed 时按 dorm_units_for_teacher 过滤）。可空 → 旧行自动 NULL，
    无需回填，保持原「全员可见」行为。
    """
    op.add_column(
        "notifications",
        sa.Column("target_dorm", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("notifications", "target_dorm")
