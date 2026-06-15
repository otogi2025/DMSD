"""audit_logs target 改可空 + action 加宽 — 操作记录页全量自动埋点 20260616

操作履历审计（老师操作记录）改为中间件自动记全部写操作（app/audit.py）。
中间件按路径自动埋点，不一定能解析出具体对象 → target_type/target_id 改可空；
action 改存 "METHOD 归一化路径"（如 "POST discipline/{id}/revoke"，比旧的
"registration_code.refresh" 长）→ 由 64 加宽到 128。
既有行（registration_code.refresh/close 语义记录）不受影响、值仍合法。

Revision ID: a9b8c7d6e5f4
Revises: e7e15d3b2e33
Create Date: 2026-06-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, Sequence[str], None] = "e7e15d3b2e33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """action 64→128 + target_type/target_id NOT NULL → NULL。

    batch_alter_table：SQLite 走表重建、PostgreSQL 直接 ALTER COLUMN —— 两库通用。
    """
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.alter_column(
            "action",
            existing_type=sa.String(length=64),
            type_=sa.String(length=128),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "target_type",
            existing_type=sa.String(length=32),
            nullable=True,
        )
        batch_op.alter_column(
            "target_id",
            existing_type=sa.Uuid(),
            nullable=True,
        )


def downgrade() -> None:
    """反向：target 改回 NOT NULL、action 收回 64。

    ⚠️ 降级前若已有 target 为 NULL 的中间件记录，需先清理 / 回填，否则 NOT NULL 约束失败。
    """
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.alter_column(
            "target_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )
        batch_op.alter_column(
            "target_type",
            existing_type=sa.String(length=32),
            nullable=False,
        )
        batch_op.alter_column(
            "action",
            existing_type=sa.String(length=128),
            type_=sa.String(length=64),
            existing_nullable=False,
        )
