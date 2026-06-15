"""audit_logs 加 actor_is_demo — 操作记录页演示隔离去规范化 20260616

操作记录页的演示隔离原本靠 join teachers.is_demo 判，硬删老师后其历史操作行会从列表消失
（codex 复审 M3 = 审计可用性漏洞）。本迁移给 audit_logs 加 actor_is_demo 列，中间件写行时
去规范化 actor 的 is_demo 到行上；读取端点据本列做演示隔离（不依赖 join），硬删老师后中间件行
仍可见、名字回退「削除済み」。语义行 / 旧行该列为 NULL（本就不在操作记录页展示）。

Revision ID: c5d6e7f8a9b0
Revises: a9b8c7d6e5f4
Create Date: 2026-06-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, Sequence[str], None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("actor_is_demo", sa.Boolean(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_column("actor_is_demo")
