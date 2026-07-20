"""rollcall_sessions 防重键 dedupe_key（审查 backend#17）

2026-07-20 五端审查：点呼场次表没有「同日同类型同寮集合」的 DB 层唯一保证，
只靠 scheduler 先查后插的应用层幂等。当前生产单 worker 触发不了，但加 worker
或未来出现第二个建场入口时，同日双场会让签到/结算对错场次。

修法（辩论定案·薄版）：加规范化列 dedupe_key（"JST日期:类型:排序寮集合"，
如 "2026-07-20:morning:1,2,4"）+ 全列唯一索引。列 nullable —— NULL 不参与
唯一性（SQLite/PG 都判 distinct），测试直建场次不受影响；scheduler / seed
两个建场现场从源头 date 局部变量算键写入（不读库、无时区回读坑），撞
IntegrityError 时回滚重查当良性去重。

回填：迁移内 Python 逐行算（不写方言 SQL）。scheduled_window_start_at 落库
是 UTC（TZDateTime 口径），必须先转 JST 再取日期 —— 早点呼 07:35 JST 即
前一天 22:35 UTC，直接取 date 会错一天。存量出现同键重复时保留最早建的
一场，其余行键加 ":dup-<id前8位>" 后缀 —— 不删行（删场次会级联删签到事件，
毁历史）。

Revision ID: 8d7c6b5a4f30
Revises: 9e8d7c6b5a40
Create Date: 2026-07-20

"""

import json
from datetime import datetime, timezone
from typing import Sequence, Union
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision: str = "8d7c6b5a4f30"
down_revision: Union[str, Sequence[str], None] = "9e8d7c6b5a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_JST = ZoneInfo("Asia/Tokyo")


def _as_jst_date(value) -> str:
    """DB 读回的 scheduled_window_start_at → JST 日期串。SQLite 回 naive UTC 字符串 /
    datetime，PG 回带时区 datetime；统一补 UTC 再转 JST 取日期。"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(_JST).date().isoformat()


def _dorm_key(value) -> str:
    """dorm_unit_set JSON 列 → 排序拼串。SQLite 回 JSON 文本，PG 回 list。"""
    if isinstance(value, str):
        value = json.loads(value)
    return ",".join(str(u) for u in sorted(value or []))


def upgrade() -> None:
    op.add_column(
        "rollcall_sessions",
        sa.Column("dedupe_key", sa.String(length=64), nullable=True),
    )

    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT id, session_type, dorm_unit_set, scheduled_window_start_at "
            "FROM rollcall_sessions ORDER BY created_at, id"
        )
    ).fetchall()
    seen: set[str] = set()
    for row in rows:
        key = f"{_as_jst_date(row[3])}:{row[1]}:{_dorm_key(row[2])}"
        if key in seen:
            key = f"{key}:dup-{str(row[0])[:8]}"
        seen.add(key)
        bind.execute(
            sa.text(
                "UPDATE rollcall_sessions SET dedupe_key = :key WHERE id = :row_id"
            ),
            {"key": key, "row_id": row[0]},
        )

    op.create_index(
        "uq_rcs_dedupe_key",
        "rollcall_sessions",
        ["dedupe_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_rcs_dedupe_key", table_name="rollcall_sessions")
    with op.batch_alter_table("rollcall_sessions", recreate="auto") as batch_op:
        batch_op.drop_column("dedupe_key")
