"""add teachers.is_demo (演示老师真隔离) 20260607

2026-06-07: 演示账号真隔离 — teachers 表加 is_demo 标记列，与 students.is_demo 对称。
演示老师（is_demo=True）登录只看演示数据（is_demo=True 学生）；真老师（is_demo=False）
只看真实数据，演示数据被过滤掉，上线后不污染。见 system_features §7.20 演示账号。
itsuki 2026-06-07 拍板「做真隔离」（接续 C 方案：同一套生产网页、靠账号区分）。

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-06-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 加 is_demo 列 — NOT NULL + server_default false（既有老师行全部默认非演示）
    op.add_column(
        "teachers",
        sa.Column(
            "is_demo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("idx_teachers_is_demo", "teachers", ["is_demo"])


def downgrade() -> None:
    op.drop_index("idx_teachers_is_demo", table_name="teachers")
    op.drop_column("teachers", "is_demo")
