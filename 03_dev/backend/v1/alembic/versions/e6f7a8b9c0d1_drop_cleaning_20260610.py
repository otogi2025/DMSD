"""drop cleaning feature 清扫功能全删 — itsuki 2026-06-10 拍板

清扫安排 + 罚扫机制随清扫功能整体删除：
- drop table cleaning_assignment
- demerit_event 的 source_type CHECK 约束去掉 'cleaning_failed'
  （罚扫 = 清扫不通过自动扣分，清扫删了这个来源类型也没了）

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-06-10
"""

import sqlalchemy as sa
from alembic import op

revision = "e6f7a8b9c0d1"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None

# 删后的扣分来源类型（5 值，去掉 cleaning_failed）
_SOURCE_AFTER = (
    "source_type IN "
    "('rollcall_late','rollcall_absent','curfew_violation','study_absent','manual')"
)
# 删前的扣分来源类型（6 值，含 cleaning_failed）— 回退用
_SOURCE_BEFORE = (
    "source_type IN "
    "('rollcall_late','rollcall_absent','cleaning_failed',"
    "'curfew_violation','study_absent','manual')"
)


def upgrade() -> None:
    # 1. 先删清扫表（它有 FK 指向 demerit_event，必须先删）
    op.drop_table("cleaning_assignment")
    # 2. 清掉历史「清扫不通过」扣分行 —— 否则下面重建 CHECK 约束时这些旧行违反新约束会报错
    op.execute("DELETE FROM demerit_event WHERE source_type = 'cleaning_failed'")
    # 3. demerit_event 来源类型约束去掉 cleaning_failed（SQLite 需 batch 重建表）
    with op.batch_alter_table("demerit_event", schema=None) as batch_op:
        batch_op.drop_constraint("ck_demerit_source", type_="check")
        batch_op.create_check_constraint("ck_demerit_source", _SOURCE_AFTER)


def downgrade() -> None:
    # 1. 恢复约束含 cleaning_failed
    with op.batch_alter_table("demerit_event", schema=None) as batch_op:
        batch_op.drop_constraint("ck_demerit_source", type_="check")
        batch_op.create_check_constraint("ck_demerit_source", _SOURCE_BEFORE)
    # 2. 重建清扫表（copy 自原始迁移 c1d2e3f4a5b6）
    op.create_table(
        "cleaning_assignment",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False
        ),
        sa.Column("area", sa.String(length=32), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="assigned"
        ),
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
        sa.CheckConstraint(
            "area IN ('浴室','廊下','トイレ','共用キッチン','階段','玄関','その他')",
            name="ck_cleaning_area",
        ),
        sa.CheckConstraint(
            "status IN ('assigned','done','passed','failed','skipped')",
            name="ck_cleaning_status",
        ),
    )
    op.create_index(
        "ix_cleaning_assignment_student_id", "cleaning_assignment", ["student_id"]
    )
    op.create_index(
        "ix_cleaning_assignment_scheduled_date",
        "cleaning_assignment",
        ["scheduled_date"],
    )
    op.create_index(
        "idx_cleaning_student_date",
        "cleaning_assignment",
        ["student_id", "scheduled_date"],
    )
