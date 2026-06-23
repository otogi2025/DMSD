"""demerit_source 改部分唯一索引（cleaning-1）

uq_demerit_source 从全列唯一约束改成 WHERE revoked_at IS NULL 的部分唯一索引：
撤销（软删 revoked_at 非 NULL、行保留作审计）后的扣分行不再占唯一槽，同一来源事件
可被重新判定（清扫 failed→撤销→再 failed）。原全列唯一约束会让软删行永久占槽，
再判时撞约束被 inspect 兜底误当并发重复 409（cleaning-1 bug）。

并发防重语义不变：两个未撤销的并发结算仍受唯一约束挡（都 revoked_at IS NULL）。

Revision ID: c1eaf6d23b07
Revises: d1e2f3a4b5c6
Create Date: 2026-06-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1eaf6d23b07"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # PG: 普通 ALTER 删唯一约束（不重建表）
        op.drop_constraint("uq_demerit_source", "demerit_event", type_="unique")
    else:
        # SQLite 不支持 ALTER 删约束 → batch recreate（auto）重建表时去掉它
        with op.batch_alter_table("demerit_event", recreate="auto") as batch_op:
            batch_op.drop_constraint("uq_demerit_source", type_="unique")
    # 重建为部分唯一索引（仅约束未撤销行）。索引名沿用 uq_demerit_source（语义连续）。
    op.create_index(
        "uq_demerit_source",
        "demerit_event",
        ["student_id", "source_type", "source_event_id"],
        unique=True,
        sqlite_where=sa.text("revoked_at IS NULL"),
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_demerit_source", table_name="demerit_event")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.create_unique_constraint(
            "uq_demerit_source",
            "demerit_event",
            ["student_id", "source_type", "source_event_id"],
        )
    else:
        with op.batch_alter_table("demerit_event", recreate="auto") as batch_op:
            batch_op.create_unique_constraint(
                "uq_demerit_source",
                ["student_id", "source_type", "source_event_id"],
            )
