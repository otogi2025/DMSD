"""add dorm application forms 20260528

2026-05-28: 实物申请表规范改动落库。

- applications 增加 6 个实物表补充字段
- application_approvals.approver_role 增加「校長」
- teachers.role 增加「校長」，让校長审批环能绑定真实老师账号
- 新增在线学习申请表
- 新增 4 张宿舍生活类申请表

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-05-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TEACHER_ROLE_CHECK = (
    "role IN ('校長','寮務部長','寮務課長','国際交流部長','国際交流課長',"
    "'管理係','寮監','学習担当','寮務一般教师')"
)
TEACHER_ROLE_CHECK_DOWN = (
    "role IN ('寮務部長','寮務課長','国際交流部長','国際交流課長',"
    "'管理係','寮監','学習担当','寮務一般教师')"
)
APPROVER_ROLE_CHECK = (
    "approver_role IN ('担任','校長','寮務部長','寮務課長','国際交流部長',"
    "'国際交流課長','管理係')"
)
APPROVER_ROLE_CHECK_DOWN = (
    "approver_role IN ('担任','寮務部長','寮務課長','国際交流部長',"
    "'国際交流課長','管理係')"
)


def upgrade() -> None:
    # applications 新字段；布尔字段保留 nullable，默认值用于新写入和既有行回填。
    with op.batch_alter_table("applications", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("contact_phone", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("companion", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("dest_cities", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "receipt_submitted",
                sa.Boolean(),
                nullable=True,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_long_vacation",
                sa.Boolean(),
                nullable=True,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(sa.Column("meal_note", sa.Text(), nullable=True))

    # teachers.role 加「校長」，否则校長审批环无法由老师账号承接。
    with op.batch_alter_table("teachers", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_teachers_role", type_="check")
        batch_op.create_check_constraint("ck_teachers_role", TEACHER_ROLE_CHECK)

    # application_approvals.approver_role 加「校長」。
    with op.batch_alter_table("application_approvals", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_approval_role", type_="check")
        batch_op.create_check_constraint("ck_approval_role", APPROVER_ROLE_CHECK)

    op.create_table(
        "study_online_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("period_from", sa.Date(), nullable=False),
        sa.Column("period_to", sa.Date(), nullable=False),
        sa.Column("weekly_schedule", sa.JSON(), nullable=False),
        sa.Column("contract_ref", sa.Text(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected','revoked')",
            name="ck_sor_status",
        ),
    )
    op.create_index(
        "idx_sor_student_status", "study_online_requests", ["student_id", "status"]
    )
    op.create_index("idx_sor_submitted", "study_online_requests", ["submitted_at"])

    op.create_table(
        "dorm_event_proposals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "proposer_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False
        ),
        sa.Column("team_name", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("held_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("place", sa.Text(), nullable=False),
        sa.Column("expected_count", sa.Integer(), nullable=False),
        sa.Column("target", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("risk_solution", sa.Text(), nullable=False),
        sa.Column("expected_cost", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "result", sa.String(length=32), nullable=False, server_default="pending"
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "result IN ('pending','approved','approved_conditional','resubmit','rejected')",
            name="ck_dep_result",
        ),
    )
    op.create_index(
        "idx_dep_proposer_result", "dorm_event_proposals", ["proposer_id", "result"]
    )
    op.create_index(
        "idx_dep_result_submitted", "dorm_event_proposals", ["result", "submitted_at"]
    )

    op.create_table(
        "dorm_schedule_changes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "requester_id", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=False
        ),
        sa.Column("class_or_club", sa.Text(), nullable=False),
        sa.Column("period_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_to", sa.DateTime(timezone=True), nullable=False),
        sa.Column("student_count", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("change_content", sa.Text(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_dsc_status"
        ),
    )
    op.create_index(
        "idx_dsc_requester_status",
        "dorm_schedule_changes",
        ["requester_id", "status"],
    )
    op.create_index(
        "idx_dsc_status_submitted",
        "dorm_schedule_changes",
        ["status", "submitted_at"],
    )

    op.create_table(
        "fridge_purchase_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("contact_phone", sa.Text(), nullable=False),
        sa.Column("contact_wechat", sa.Text(), nullable=True),
        sa.Column("product", sa.String(length=1), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("delivered_sign", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint("product IN ('A','B')", name="ck_fpr_product"),
        sa.CheckConstraint(
            "status IN ('pending','ordered','delivered','rejected')",
            name="ck_fpr_status",
        ),
    )
    op.create_index(
        "idx_fpr_student_status",
        "fridge_purchase_requests",
        ["student_id", "status"],
    )
    op.create_index(
        "idx_fpr_status_submitted",
        "fridge_purchase_requests",
        ["status", "submitted_at"],
    )

    op.create_table(
        "item_possession_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("room_no", sa.String(length=16), nullable=False),
        sa.Column("item", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("guardian_name", sa.Text(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_ipr_status"
        ),
    )
    op.create_index(
        "idx_ipr_student_status",
        "item_possession_requests",
        ["student_id", "status"],
    )
    op.create_index(
        "idx_ipr_status_submitted",
        "item_possession_requests",
        ["status", "submitted_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_ipr_status_submitted", table_name="item_possession_requests")
    op.drop_index("idx_ipr_student_status", table_name="item_possession_requests")
    op.drop_table("item_possession_requests")

    op.drop_index("idx_fpr_status_submitted", table_name="fridge_purchase_requests")
    op.drop_index("idx_fpr_student_status", table_name="fridge_purchase_requests")
    op.drop_table("fridge_purchase_requests")

    op.drop_index("idx_dsc_status_submitted", table_name="dorm_schedule_changes")
    op.drop_index("idx_dsc_requester_status", table_name="dorm_schedule_changes")
    op.drop_table("dorm_schedule_changes")

    op.drop_index("idx_dep_result_submitted", table_name="dorm_event_proposals")
    op.drop_index("idx_dep_proposer_result", table_name="dorm_event_proposals")
    op.drop_table("dorm_event_proposals")

    op.drop_index("idx_sor_submitted", table_name="study_online_requests")
    op.drop_index("idx_sor_student_status", table_name="study_online_requests")
    op.drop_table("study_online_requests")

    with op.batch_alter_table("application_approvals", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_approval_role", type_="check")
        batch_op.create_check_constraint(
            "ck_approval_role", APPROVER_ROLE_CHECK_DOWN
        )

    with op.batch_alter_table("teachers", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_teachers_role", type_="check")
        batch_op.create_check_constraint("ck_teachers_role", TEACHER_ROLE_CHECK_DOWN)

    with op.batch_alter_table("applications", recreate="always") as batch_op:
        batch_op.drop_column("meal_note")
        batch_op.drop_column("is_long_vacation")
        batch_op.drop_column("receipt_submitted")
        batch_op.drop_column("dest_cities")
        batch_op.drop_column("companion")
        batch_op.drop_column("contact_phone")
