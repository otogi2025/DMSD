"""demerit_event 加自动扣分防重唯一约束 (student_id, source_type, source_event_id)

并发结算（点呼 end / 学習 finalize）会重复扣分 —— 用 DB 层唯一约束兜底。
source_event_id 可空（手动扣分 manual 时为 NULL），NULL 在唯一约束里互不相等，
故只约束 source_event_id 非空的自动扣分行、手动扣分不受限。

Revision ID: 0e1f2a3b4c5d
Revises: 0dee708c484e
Create Date: 2026-06-15 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0e1f2a3b4c5d"
down_revision: Union[str, Sequence[str], None] = "0dee708c484e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite ALTER TABLE 不能直接加表级约束 → batch 模式（建影子表 + 拷贝数据 + 改名）。
    # PostgreSQL 下 batch_alter_table 会退化成普通 ALTER TABLE ADD CONSTRAINT。
    with op.batch_alter_table("demerit_event") as batch_op:
        batch_op.create_unique_constraint(
            "uq_demerit_source",
            ["student_id", "source_type", "source_event_id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("demerit_event") as batch_op:
        batch_op.drop_constraint("uq_demerit_source", type_="unique")
