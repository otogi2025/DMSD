"""add_study_absence_period

2026-05-03: 学習欠席届に「欠席する範囲」(period) 列追加
  - iOS UI に既に「前半節 / 後半節 / 両方」の 3 選択肢があったが、
    DB / Pydantic / API body にこの値を渡す経路が無く完全に捨てられていた。
  - period 列追加 + CHECK 制約 + デフォルト 'full'（既存行の retro 値）

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite は ALTER TABLE で CHECK 制約追加不可 → batch_alter_table でテーブル再作成
    with op.batch_alter_table('study_absence_requests', recreate='always') as batch_op:
        # 既存行は既に提出済みのため、retro 値として "full"（両方休む扱い）を入れる
        batch_op.add_column(
            sa.Column('period', sa.String(length=16), nullable=False, server_default='full')
        )
        batch_op.create_check_constraint(
            'ck_sar_period',
            "period IN ('first_half','second_half','full')",
        )


def downgrade() -> None:
    with op.batch_alter_table('study_absence_requests', recreate='always') as batch_op:
        batch_op.drop_constraint('ck_sar_period', type_='check')
        batch_op.drop_column('period')
