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
    # 不可无损降级（codex 审查 minor）：升级后业务允许同一
    # (student_id, source_type, source_event_id) 同时存在「已撤销旧行 + 未撤销新行」
    # （清扫 failed→撤销→再 failed）。降回全局唯一约束会因这些重复键冲突而失败。
    # 软删行是审计数据、不能为了强行降级而擅自删除（违背 revoke 保留审计的设计意图）。
    # 如确需降级：先人工归档/合并重复软删行，再手动重建全局 uq_demerit_source 唯一约束。
    raise NotImplementedError(
        "不可自动降级：demerit_source 部分唯一索引 → 全局唯一约束，"
        "在存在『撤销后重判』数据时会键冲突。请先人工清理重复软删行再手动重建约束。"
    )
