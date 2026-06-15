"""开示申请加「同一学生同时只能一条 pending」部分唯一索引

路由层 create_disclosure_request 先 SELECT pending 再 INSERT 的检查会被并发绕过
（两个请求各自查到无 pending → 都通过 409 检查 → 各 INSERT 一条 pending），破坏
「同时只能有一条待处理」不变量。用 DB 层部分唯一索引兜底：只约束 status='pending'
的行，已决定（approved_full/approved_partial/rejected）的历史行不受限，学生处理完一条
后仍可再提下一条。SQLite（dev）与 PostgreSQL（prod）都支持部分索引。

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-06-15 00:00:20.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9e0f1a2b3c4"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 部分唯一索引：unique=True + sqlite_where/postgresql_where 限定只覆盖 pending 行。
    op.create_index(
        "uq_gdr_one_pending_per_student",
        "guidance_disclosure_requests",
        ["student_id"],
        unique=True,
        sqlite_where=sa.text("status = 'pending'"),
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_gdr_one_pending_per_student",
        table_name="guidance_disclosure_requests",
    )
