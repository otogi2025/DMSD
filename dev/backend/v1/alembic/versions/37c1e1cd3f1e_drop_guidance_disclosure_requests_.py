"""drop guidance_disclosure_requests 開示申請功能删除 20260615

開示申請（学生申请查看自己指导履历、老师审批开示）功能 itsuki 2026-06-15 拍板整删。
本迁移删除该功能独占的 guidance_disclosure_requests 表及其索引。
建表来自 f7a8b9c0d1e2，部分唯一索引来自 d9e0f1a2b3c4 —— 两者均不改动（历史不重写），
仅在 head 上新增本「删表」前向迁移。指导记录 guidance_records 表不受影响。

Revision ID: 37c1e1cd3f1e
Revises: 472e0403ba4b
Create Date: 2026-06-15 23:40:22.797273

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "37c1e1cd3f1e"
down_revision: Union[str, Sequence[str], None] = "472e0403ba4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. 删索引后删表（SQLite/PostgreSQL 都先显式删索引更稳）。"""
    op.drop_index(
        "uq_gdr_one_pending_per_student", table_name="guidance_disclosure_requests"
    )
    op.drop_index("idx_gdr_status_requested", table_name="guidance_disclosure_requests")
    op.drop_index("idx_gdr_student_status", table_name="guidance_disclosure_requests")
    op.drop_table("guidance_disclosure_requests")


def downgrade() -> None:
    """Downgrade schema. 按 f7a8b9c0d1e2 + d9e0f1a2b3c4 原样重建表+索引（保证可逆）。"""
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
    op.create_index(
        "uq_gdr_one_pending_per_student",
        "guidance_disclosure_requests",
        ["student_id"],
        unique=True,
        sqlite_where=sa.text("status = 'pending'"),
        postgresql_where=sa.text("status = 'pending'"),
    )
