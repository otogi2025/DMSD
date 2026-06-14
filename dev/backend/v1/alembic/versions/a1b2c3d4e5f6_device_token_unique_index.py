"""device_tokens.token 改为 unique 索引（A11 bug 修复）

原来是普通 Index("idx_dt_token")，无唯一约束，
同一 token 可被多个学生注册导致推送混乱。
改为 UniqueConstraint("uq_dt_token")。

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-30

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite 不支持 ALTER ADD CONSTRAINT，用 batch 模式（copy-and-move）
    with op.batch_alter_table("device_tokens") as batch_op:
        batch_op.drop_index("idx_dt_token")
        batch_op.create_unique_constraint("uq_dt_token", ["token"])


def downgrade() -> None:
    with op.batch_alter_table("device_tokens") as batch_op:
        batch_op.drop_constraint("uq_dt_token", type_="unique")
        batch_op.create_index("idx_dt_token", ["token"], unique=False)
