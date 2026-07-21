"""src one active partial unique index backend23

Revision ID: 9ff1a7778b8e
Revises: 134d631496f1
Create Date: 2026-07-21 16:11:46.953434

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9ff1a7778b8e"
down_revision: Union[str, Sequence[str], None] = "134d631496f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """加 student_registration_codes 部分唯一索引（审查 backend#23）。

    「同时至多 1 个 active 非审核员码」原靠 refresh 里 SELECT FOR UPDATE，但行锁挡不住
    「零 active 行并发各插一条」和 PostgreSQL EvalPlanQual 窗口 → 仍可能留下多条 active 码。
    部分唯一索引在 DB 层兜底，与 models.py __table_args__ 的 uq_src_one_active 同名同定义。
    谓词把范围限在 invalidated_at IS NULL AND is_reviewer=false,唯一列 is_reviewer 在此范围
    恒为 false → 至多一行。审核员永久码(is_reviewer=true)不进索引、不受约束。
    """
    # 建索引前先去重：若历史遗留多条 active 非审核员码,只保留 created_at 最新的一条,
    # 其余标 invalidated_at,否则唯一索引会因冲突创建失败。生产库全新从迁移建 → 无数据、空操作。
    op.execute(
        """
        UPDATE student_registration_codes
        SET invalidated_at = created_at
        WHERE invalidated_at IS NULL
          AND is_reviewer = false
          AND id NOT IN (
              SELECT id FROM (
                  SELECT id FROM student_registration_codes
                  WHERE invalidated_at IS NULL AND is_reviewer = false
                  ORDER BY created_at DESC
                  LIMIT 1
              ) AS keep
          )
        """
    )
    op.create_index(
        "uq_src_one_active",
        "student_registration_codes",
        ["is_reviewer"],
        unique=True,
        sqlite_where=sa.text("invalidated_at IS NULL AND is_reviewer = 0"),
        postgresql_where=sa.text("invalidated_at IS NULL AND is_reviewer = false"),
    )


def downgrade() -> None:
    """回滚：删部分唯一索引（去重的数据变更不回滚 — 作废的旧码本就该作废）。"""
    op.drop_index("uq_src_one_active", table_name="student_registration_codes")
