"""add students.needs_renewal (学年更新 / 学生自设番号) 20260605

2026-06-05: 学年更新 / 学生自设番号功能 — students 表加 needs_renewal 标记列。
老师点「学年更新を開始」开闸后，给中1~高2 active 学生置 needs_renewal=True
（学生 App 顶部据此显示「更新番号」按钮）；学生自设番号成功后置 False。
高3（grade_code='06'）开闸时直接 status='graduated'，不打标记。
推翻 2026-04-30「老师代改 / 学生只读」方案。见 system_features §4.2。itsuki 2026-06-05 拍板。

Revision ID: b2c3d4e5f6a7
Revises: e1f2a3b4c5d6
Create Date: 2026-06-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 加 needs_renewal 列 — NOT NULL + server_default false（既有行全部默认未待更新）
    op.add_column(
        "students",
        sa.Column(
            "needs_renewal",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("idx_students_needs_renewal", "students", ["needs_renewal"])


def downgrade() -> None:
    op.drop_index("idx_students_needs_renewal", table_name="students")
    op.drop_column("students", "needs_renewal")
