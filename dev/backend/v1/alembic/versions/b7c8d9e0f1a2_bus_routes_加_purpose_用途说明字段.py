"""bus_routes 加 purpose 用途说明字段

Revision ID: b7c8d9e0f1a2
Revises: 0e1f2a3b4c5d
Create Date: 2026-06-15 00:00:05.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "0e1f2a3b4c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("bus_routes", sa.Column("purpose", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("bus_routes", "purpose")
