"""add guidance and incidents 20260530

新增 3 张表：
- guidance_records              指导履历记录 (spec §7.9/§7.10)
- guidance_disclosure_requests  开示申请 (spec §7.10 C 案)
- incident_records              事案录入 (spec §7.9 #33)

Revision ID: f7a8b9c0d1e2
Revises: e3f4a5b6c7d8
Create Date: 2026-05-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e3f4a5b6c7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 指导履历记录 (spec §7.9)
    op.create_table(
        "guidance_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False
        ),
        sa.Column(
            "teacher_id", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column(
            "confidential",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("guidance_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_gr_student", "guidance_records", ["student_id", "deleted_at"])
    op.create_index(
        "idx_gr_teacher", "guidance_records", ["teacher_id", "guidance_date"]
    )

    # 开示申请 (spec §7.10 C 案)
    op.create_table(
        "guidance_disclosure_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "student_id", sa.Uuid(), sa.ForeignKey("students.id"), nullable=False
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=24),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("visible_from", sa.Date(), nullable=True),
        sa.Column("visible_until", sa.Date(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','approved_full','approved_partial','rejected')",
            name="ck_gdr_status",
        ),
    )
    op.create_index(
        "idx_gdr_student_status",
        "guidance_disclosure_requests",
        ["student_id", "status"],
    )
    op.create_index(
        "idx_gdr_status_requested",
        "guidance_disclosure_requests",
        ["status", "requested_at"],
    )

    # 事案录入 (spec §7.9 #33)
    op.create_table(
        "incident_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("involved_student_ids", sa.JSON(), nullable=False),
        sa.Column(
            "recorded_by", sa.Uuid(), sa.ForeignKey("teachers.id"), nullable=False
        ),
        sa.Column("incident_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_ir_recorded_by", "incident_records", ["recorded_by", "incident_date"]
    )
    op.create_index(
        "idx_ir_date_active", "incident_records", ["incident_date", "deleted_at"]
    )


def downgrade() -> None:
    op.drop_index("idx_ir_date_active", table_name="incident_records")
    op.drop_index("idx_ir_recorded_by", table_name="incident_records")
    op.drop_table("incident_records")

    op.drop_index("idx_gdr_status_requested", table_name="guidance_disclosure_requests")
    op.drop_index("idx_gdr_student_status", table_name="guidance_disclosure_requests")
    op.drop_table("guidance_disclosure_requests")

    op.drop_index("idx_gr_teacher", table_name="guidance_records")
    op.drop_index("idx_gr_student", table_name="guidance_records")
    op.drop_table("guidance_records")
