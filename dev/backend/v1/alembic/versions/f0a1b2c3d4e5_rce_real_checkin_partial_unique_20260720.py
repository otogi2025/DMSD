"""rollcall_events 真实签到部分唯一索引（审查 backend#1 / backend#4）

2026-07-20 五端审查：rollcall_events 对「真实签到行」（status_source =
auto_nfc / manual_checkin）没有任何 DB 层防重 —— 唯一约束只有
(session_id, idempotency_key)，而路径 A / 手动代签的 idempotency_key 恒 NULL，
SQL 标准下多个 NULL 互不冲突。两个并发请求各自通过应用层「先查再插」后，
同一学生同一场次能插出两条 present/late，污染座位图与审计回放。

修法（辩论定案）：加部分唯一索引 uq_rce_real_checkin ——
UNIQUE(session_id, student_id) WHERE status_source IN ('auto_nfc','manual_checkin')。
谓词绝不能扩到 auto_settle / teacher_override：append-only 纠错设计下，
「auto_settle 缺席结算行 + 事后离线补传的 auto_nfc 行 + 多条 teacher_override
改判行」同生同场合法共存，全局唯一约束会把离线补传直接挡死。
写法照 c1eaf6d23b07（uq_demerit_source 部分唯一索引）既有先例。

迁移先清存量重复：同 (session_id, student_id) 多条真实签到行时保留
checked_in_at 最新（次级键 id 最大）那条 —— 与 board / summary / patch_event
的 latest-per-student 取行口径一致，迁移前后看板显示不变。删多余行不影响
扣分记录：DemeritEvent.source_event_id 挂 session 不挂 event，且迟到扣分
本就被 uq_demerit_source 限成每场每生一条。

Revision ID: f0a1b2c3d4e5
Revises: a1c2e3f4b5d6
Create Date: 2026-07-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "a1c2e3f4b5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1) 存量去重 —— Python 逐行分组（不用窗口函数，SQLite/PG 跨方言）。
    #    ORDER BY checked_in_at DESC, id DESC：每组第一行 = 要保留的最新行。
    rows = bind.execute(
        sa.text(
            "SELECT id, session_id, student_id FROM rollcall_events "
            "WHERE status_source IN ('auto_nfc','manual_checkin') "
            "ORDER BY session_id, student_id, checked_in_at DESC, id DESC"
        )
    ).fetchall()
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (str(row[1]), str(row[2]))
        if key in seen:
            # id 原值回传（不 str() 转换）—— PG 是 uuid 类型、SQLite 是驱动自己的
            # 存储格式，用查出来的原对象绑参数两边都对。
            bind.execute(
                sa.text("DELETE FROM rollcall_events WHERE id = :dup_id"),
                {"dup_id": row[0]},
            )
        else:
            seen.add(key)

    # 2) 部分唯一索引（真实签到行每生每场至多一条；auto_settle/teacher_override 不受限）
    op.create_index(
        "uq_rce_real_checkin",
        "rollcall_events",
        ["session_id", "student_id"],
        unique=True,
        sqlite_where=sa.text("status_source IN ('auto_nfc','manual_checkin')"),
        postgresql_where=sa.text("status_source IN ('auto_nfc','manual_checkin')"),
    )


def downgrade() -> None:
    # 索引可直接删；去重删掉的行不可恢复（并发双插的冗余行，本就不该存在）。
    op.drop_index("uq_rce_real_checkin", table_name="rollcall_events")
