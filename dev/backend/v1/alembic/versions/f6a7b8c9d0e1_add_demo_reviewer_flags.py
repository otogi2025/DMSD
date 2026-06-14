"""add_demo_reviewer_flags

2026-05-08: Demo 账号 / 审核员注册码合规化（itsuki 拍板）
  - students.is_demo: 标记 demo / reviewer 账号 → admin 学生列表 / 出席统计自动过滤
  - student_registration_codes.is_reviewer: 标记审核员永久码 → refresh 不作废 + 跟普通 5 分钟 TTL 码并存
  - 权威 spec: system_features.md §7.16 (例外条款) + §7.20 (Demo 账号)
  - 背景: 5-08 上架冲刺时 fork 直接塞 999999 永久码进 prod DB → 主 CC review 戳穿 5 个 bug → 重做

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column(
            "is_demo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("idx_students_is_demo", "students", ["is_demo"])

    op.add_column(
        "student_registration_codes",
        sa.Column(
            "is_reviewer",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        "idx_src_is_reviewer",
        "student_registration_codes",
        ["is_reviewer", "invalidated_at"],
    )

    # 5-08 应急: 把已塞进 VPS prod DB 的 hardcode '999999' 行 invalidate
    # （fork seed.py 写的 expires_at=2030 永久码 — 现在 schema 升级了，把它清掉
    #  让 reseed 用 is_reviewer=True 的合规版本重建）
    op.execute(
        "UPDATE student_registration_codes "
        "SET invalidated_at = CURRENT_TIMESTAMP "
        "WHERE code = '999999' AND invalidated_at IS NULL"
    )


def downgrade() -> None:
    op.drop_index("idx_src_is_reviewer", table_name="student_registration_codes")
    op.drop_column("student_registration_codes", "is_reviewer")
    op.drop_index("idx_students_is_demo", table_name="students")
    op.drop_column("students", "is_demo")
