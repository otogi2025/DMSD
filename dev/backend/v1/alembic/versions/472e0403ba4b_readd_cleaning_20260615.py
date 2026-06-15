"""re-add cleaning_assignment 清扫罚扫功能重建 — itsuki 2026-06-15 拍板重做

清扫安排 + 罚扫机制整体重建（2026-06-10 删除的逆向 + 两处升级）：
- 重建 cleaning_assignment 表，但 scheduled_date(date) → scheduled_at(带时区 datetime)
  且 area 去掉固定枚举 CHECK（改老师自由文本）。
- demerit_event 的 source_type CHECK 加回 'cleaning_failed'（罚扫 = 清扫不通过自动扣 2.5 分）。

Revision ID: 472e0403ba4b
Revises: f9a0b1c2d3e4
Create Date: 2026-06-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "472e0403ba4b"
down_revision: Union[str, Sequence[str], None] = "f9a0b1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 重建后的扣分来源类型（6 值，加回 cleaning_failed）
_SOURCE_AFTER = (
    "source_type IN "
    "('rollcall_late','rollcall_absent','cleaning_failed',"
    "'curfew_violation','study_absent','manual')"
)
# 重建前的扣分来源类型（5 值，无 cleaning_failed）— 回退用
_SOURCE_BEFORE = (
    "source_type IN "
    "('rollcall_late','rollcall_absent','curfew_violation','study_absent','manual')"
)


def upgrade() -> None:
    # 1. demerit_event 来源类型约束加回 cleaning_failed（SQLite 需 batch 重建表）
    with op.batch_alter_table("demerit_event", schema=None) as batch_op:
        batch_op.drop_constraint("ck_demerit_source", type_="check")
        batch_op.create_check_constraint("ck_demerit_source", _SOURCE_AFTER)

    # 2. 重建 cleaning_assignment 表（scheduled_at 带时区 datetime / area 无枚举约束）
    op.create_table(
        "cleaning_assignment",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=False,
        ),
        sa.Column("area", sa.String(length=32), nullable=False),
        # 改动 1：计划执行时刻 = 带时区 datetime（旧版是 scheduled_date Date）
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "assigned_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "inspected_by_teacher_id",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "demerit_event_id",
            sa.Uuid(),
            sa.ForeignKey("demerit_event.id"),
            nullable=True,
        ),
        # 改动 2：去掉 ck_cleaning_area 枚举约束（area 自由文本），仅保留 status CHECK
        sa.CheckConstraint(
            "status IN ('assigned','done','passed','failed','skipped')",
            name="ck_cleaning_status",
        ),
    )
    op.create_index(
        "ix_cleaning_assignment_student_id", "cleaning_assignment", ["student_id"]
    )
    op.create_index(
        "ix_cleaning_assignment_scheduled_at",
        "cleaning_assignment",
        ["scheduled_at"],
    )
    op.create_index(
        "idx_cleaning_student_scheduled",
        "cleaning_assignment",
        ["student_id", "scheduled_at"],
    )


def downgrade() -> None:
    # 1. 先删清扫表（它有 FK 指向 demerit_event，必须先删）
    op.drop_index("idx_cleaning_student_scheduled", table_name="cleaning_assignment")
    op.drop_index(
        "ix_cleaning_assignment_scheduled_at", table_name="cleaning_assignment"
    )
    op.drop_index("ix_cleaning_assignment_student_id", table_name="cleaning_assignment")
    op.drop_table("cleaning_assignment")
    # 2. 清掉历史「清扫不通过」扣分行 —— 否则重建 CHECK 约束时旧行违反新约束会报错
    op.execute("DELETE FROM demerit_event WHERE source_type = 'cleaning_failed'")
    # 3. demerit_event 来源类型约束去回 5 值
    with op.batch_alter_table("demerit_event", schema=None) as batch_op:
        batch_op.drop_constraint("ck_demerit_source", type_="check")
        batch_op.create_check_constraint("ck_demerit_source", _SOURCE_BEFORE)
