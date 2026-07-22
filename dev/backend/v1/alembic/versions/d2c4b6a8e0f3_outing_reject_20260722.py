"""outings 加 rejected 状态 + reject_reason（外出事后确认制 2026-07-22）

itsuki 2026-07-22 拍板：外出申请（当天回寮的短时间外出）语义从「事前审批制」
改成「事后确认制」——学生提交即生效可以出门，老师点「確認」只是留记录；老师仍可
「却下」（现实中很少用），却下只发通知 + 留记录，不要求学生立刻回寮。

本迁移做两件事（只动 outings 表，出寮届 applications 一行不碰）：
1. CHECK 约束 ck_outing_status 三值 → 四值，加 'rejected'
2. 新增可空列 reject_reason（老师填的却下理由，可选填）

⚠️ SQLite 不支持直接改 CHECK 约束，必须整表重建 → 用 batch_alter_table。
recreate="auto"：PG 走原生 ALTER 不重建表（无条件重建的写法在 PG 会因外键
CASCADE 崩，见 test_migration_smoke 静态守卫）；SQLite 按需重建。

Revision ID: d2c4b6a8e0f3
Revises: 9ff1a7778b8e
Create Date: 2026-07-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d2c4b6a8e0f3"
down_revision: Union[str, Sequence[str], None] = "9ff1a7778b8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FOUR = "status IN ('pending','approved','rejected','withdrawn')"
_THREE = "status IN ('pending','approved','withdrawn')"


def upgrade() -> None:
    with op.batch_alter_table("outings", recreate="auto") as batch_op:
        batch_op.add_column(sa.Column("reject_reason", sa.Text(), nullable=True))
        batch_op.drop_constraint("ck_outing_status", type_="check")
        batch_op.create_check_constraint("ck_outing_status", _FOUR)


def downgrade() -> None:
    # 降级前先把 rejected 行归并成 withdrawn（同属「没生效的终态」，语义损失可接受），
    # 否则三值 CHECK 重建时存量 rejected 行冲突、降级直接失败。
    op.execute("UPDATE outings SET status = 'withdrawn' WHERE status = 'rejected'")
    with op.batch_alter_table("outings", recreate="auto") as batch_op:
        batch_op.drop_constraint("ck_outing_status", type_="check")
        batch_op.create_check_constraint("ck_outing_status", _THREE)
        batch_op.drop_column("reject_reason")
