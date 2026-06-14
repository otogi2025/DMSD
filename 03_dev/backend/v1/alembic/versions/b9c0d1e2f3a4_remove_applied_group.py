"""remove_applied_group_from_rollcall_events

2026-05-21: A-022 b1 修复 — 彻底删除 effective_* 窗口平移概念
  - itsuki 拍板 b1：点呼时间永远固定 / 迟到永远按 scheduled_* 算
  - 老师提前按按钮只改 started_at 显示，不改判定窗口
  - 故 applied_group 字段无意义（窗口不变 → 分组永远 = student 当前 group）
  - 直接走 §6.4 student_group，不在 event 层冗余存
  - 权威：A-022（内部审查记录）
  - 关联：RollCall_Spec §5.4 / §6.4 / §7 / §10

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b9c0d1e2f3a4"
down_revision: Union[str, Sequence[str], None] = "a8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """删除 rollcall_events.applied_group 列。

    注：4 个 effective_*_at 时间字段从未在 ORM model / alembic 里实装过
    （spec 里描述过但未落到数据库），所以本迁移只删 applied_group 一列。
    """
    op.drop_column("rollcall_events", "applied_group")


def downgrade() -> None:
    """回滚：加回 applied_group 列（nullable，无 check 约束 — 跟原 model 一致）。

    回滚后历史数据 applied_group = NULL（信息不可恢复，因为 b1 拍板
    意味着该字段从未承载真实业务区分）。
    """
    op.add_column(
        "rollcall_events",
        sa.Column("applied_group", sa.String(length=16), nullable=True),
    )
