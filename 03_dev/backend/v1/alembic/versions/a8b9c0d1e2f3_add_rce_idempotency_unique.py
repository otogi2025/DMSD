"""add_rce_idempotency_unique

2026-05-21: A-011 修复 — RollCallEvent.idempotency_key 没 UniqueConstraint
  - 同 session + 同 key 必须唯一，防 client 重试 / 复用 key 产生重复事件
  - 配套 router 改：先查 idempotency_key 命中 → 直接返已存事件
  - 权威：A-011 in 05_logs/audit_2026-05-19/session_A_findings.md

Revision ID: a8b9c0d1e2f3
Revises: f6a7b8c9d0e1
Create Date: 2026-05-21

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a8b9c0d1e2f3"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 同 session + 同 idempotency_key 必须唯一
    # 注：NULL idempotency_key（路径 A / manual）不参与唯一性约束（SQL 标准行为）
    with op.batch_alter_table("rollcall_events", recreate="always") as batch_op:
        batch_op.create_unique_constraint(
            "uq_rce_idempotency",
            ["session_id", "idempotency_key"],
        )


def downgrade() -> None:
    with op.batch_alter_table("rollcall_events", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_rce_idempotency", type_="unique")
