"""add announcements.is_demo (公告 demo 隔离) 20260613

2026-06-13: 公告 demo 隔离 — announcements 表加 is_demo 标记列，与 students.is_demo /
teachers.is_demo 对称。演示老师发的公告 is_demo=True；演示老师 / 演示学生只看 is_demo=True
公告，真老师 / 真实学生只看 is_demo=False，上线后演示公告不污染真实学生。
本次同时种入 6 条演示宿舍公告（seed.py _seed_demo_data），与 iOS 演示版本地 SEED 内容对齐。

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-06-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 加 is_demo 列 — NOT NULL + server_default false（既有公告行全部默认非演示）
    op.add_column(
        "announcements",
        sa.Column(
            "is_demo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("idx_announcement_is_demo", "announcements", ["is_demo"])


def downgrade() -> None:
    op.drop_index("idx_announcement_is_demo", table_name="announcements")
    op.drop_column("announcements", "is_demo")
