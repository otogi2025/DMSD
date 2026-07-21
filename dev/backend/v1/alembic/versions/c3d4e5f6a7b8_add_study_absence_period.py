"""add_study_absence_period

2026-05-03: 学习欠席届追加「欠席范围」(period) 列
  - iOS UI 已有「前半节 / 后半节 / 两边」3 选项，
    但 DB / Pydantic / API body 没有传这个值的路径，选项被整段丢掉。
  - 追加 period 列 + CHECK 约束 + 默认 'full'（既有行的回填值）

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite 的 ALTER TABLE 不能加 CHECK 约束 → 用 batch_alter_table 重建表
    with op.batch_alter_table("study_absence_requests", recreate="auto") as batch_op:
        # 既有行已提交过，回填 "full"（两边都休）作为 retro 值
        batch_op.add_column(
            sa.Column(
                "period", sa.String(length=16), nullable=False, server_default="full"
            )
        )
        batch_op.create_check_constraint(
            "ck_sar_period",
            "period IN ('first_half','second_half','full')",
        )


def downgrade() -> None:
    with op.batch_alter_table("study_absence_requests", recreate="auto") as batch_op:
        batch_op.drop_constraint("ck_sar_period", type_="check")
        batch_op.drop_column("period")
