"""align_application_schema

2026-05-02: iOS ↔ backend フィールド対齐 (F2/F3/F5/Q1)
  - Application.reason 列追加 (F5)
  - meals_skip_from / meals_skip_to 削除 + meals_skip JSON 列追加 (F3)
  - status CHECK に "returned" 追加 (Q1)

Revision ID: b2c3d4e5f6a7
Revises: 7a15771bdc7b
Create Date: 2026-05-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = '7a15771bdc7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite は ALTER TABLE で CHECK 制約変更不可 → batch_alter_table でテーブル再作成
    with op.batch_alter_table('applications', recreate='always') as batch_op:
        # F5: reason 列追加
        batch_op.add_column(sa.Column('reason', sa.Text(), nullable=True))
        # F3: meals_skip JSON 列追加
        batch_op.add_column(sa.Column('meals_skip', sa.JSON(), nullable=True))
        # F3: 旧 meals_skip_from / meals_skip_to 削除
        batch_op.drop_column('meals_skip_from')
        batch_op.drop_column('meals_skip_to')
        # Q1: status CHECK に "returned" 追加
        batch_op.drop_constraint('ck_app_status', type_='check')
        batch_op.create_check_constraint(
            'ck_app_status',
            "status IN ('pending','approved_partial','approved','rejected','withdrawn','returned')",
        )


def downgrade() -> None:
    with op.batch_alter_table('applications', recreate='always') as batch_op:
        batch_op.drop_column('reason')
        batch_op.drop_column('meals_skip')
        batch_op.add_column(
            sa.Column('meals_skip_from', sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column('meals_skip_to', sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.drop_constraint('ck_app_status', type_='check')
        batch_op.create_check_constraint(
            'ck_app_status',
            "status IN ('pending','approved_partial','approved','rejected','withdrawn')",
        )
