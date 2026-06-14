"""add_student_registration_codes

2026-05-04: 学生注册码 — App Store 上架对策（itsuki 2026-05-03 拍板）
  - 权威 spec: system_features §7.16 + BACKEND §4.10 + §5.1.5
  - 老师在后台生成 6 桁数字 → 5 分钟内有效 → 学生用它完成新规注册
  - 同时有效的码全系统只 1 个（生成新码时旧码立刻 invalidate）
  - SQLite 兼容: regex CHECK 不可，DB 层只查长度；应用层用 '^[0-9]{6}$' 严校

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_registration_codes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=6), nullable=False),
        sa.Column(
            "created_by",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("LENGTH(code) = 6", name="ck_src_code_len"),
    )
    op.create_index(
        "idx_src_code_active",
        "student_registration_codes",
        ["code", "invalidated_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_src_code_active", table_name="student_registration_codes")
    op.drop_table("student_registration_codes")
