"""applications.receipt_submitted / is_long_vacation 改 NOT NULL（A-485）

两列原来 nullable=True + default=False，引入了「NULL / True / False」三态。
DB 真出 NULL 时喂给非 Optional 的 ApplicationOut.receipt_submitted: bool / is_long_vacation: bool
会触发 500（响应模型校验失败）。本迁移：
  1. 先把存量 NULL 行回填成 False（语义上「未提交收据 / 非长假」就是默认 False）。
  2. 再把两列改成 NOT NULL，从 schema 层杜绝三态。

SQLite（dev）不支持直接 ALTER COLUMN 改 nullable，用 op.batch_alter_table（copy-and-move）兼容；
PostgreSQL（prod）batch 模式同样可用。upgrade / downgrade 都可逆。

Revision ID: f9a0b1c2d3e4
Revises: d9e0f1a2b3c4
Create Date: 2026-06-15 01:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9a0b1c2d3e4"
down_revision: Union[str, Sequence[str], None] = "d9e0f1a2b3c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 存量 NULL 回填 False（必须在改 NOT NULL 前做，否则旧 NULL 行会让 NOT NULL 约束失败）。
    op.execute(
        sa.text(
            "UPDATE applications SET receipt_submitted = 0 "
            "WHERE receipt_submitted IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE applications SET is_long_vacation = 0 "
            "WHERE is_long_vacation IS NULL"
        )
    )

    # 2. 改 NOT NULL（batch 模式兼容 SQLite）。server_default=false 让历史 / 将来直接 INSERT
    #    不带这两列的行也落到 False，与 model 的 default=False 一致、不破坏现有写路径。
    with op.batch_alter_table("applications") as batch_op:
        batch_op.alter_column(
            "receipt_submitted",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )
        batch_op.alter_column(
            "is_long_vacation",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )


def downgrade() -> None:
    """Downgrade schema."""
    # 回退成 nullable=True 并撤掉 server_default，恢复迁移前状态。
    with op.batch_alter_table("applications") as batch_op:
        batch_op.alter_column(
            "receipt_submitted",
            existing_type=sa.Boolean(),
            nullable=True,
            server_default=None,
        )
        batch_op.alter_column(
            "is_long_vacation",
            existing_type=sa.Boolean(),
            nullable=True,
            server_default=None,
        )
