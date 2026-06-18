"""teachers 加 expires_at — 临时账户到期时间 20260618

临时账户（代班老师等）功能：teachers 加 expires_at（可空 datetime）。
NULL = 永久正式账户；有值 = 临时账户，到期后登录被拒、已发令牌也在
deps.get_current_teacher 处按本列拒绝。存量行该列为 NULL（都是永久账户）。

Revision ID: d1e2f3a4b5c6
Revises: c5d6e7f8a9b0
Create Date: 2026-06-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c5d6e7f8a9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "teachers", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    with op.batch_alter_table("teachers") as batch_op:
        batch_op.drop_column("expires_at")
