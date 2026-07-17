"""add rollcall_devices, nfc_cards, device_auth_nonces（点呼机接入）

2026-07-17：点呼功能真实装 — 设备注册 / 卡绑定 / 令牌防重放三张新表配套迁移。
权威契约 = specs/rollcall/Device_Contract.md §2/§4/§5 + DEVICE_REGISTRY.md + FIELD_REGISTRY.md。

SQLite（dev）/ PostgreSQL（prod）双兼容：均为新建表，op.create_table 直接可用（无需
batch_alter_table，那只针对改既有表）；nfc_cards 的部分唯一索引用 sqlite_where /
postgresql_where 双写（同 demerit_event.uq_demerit_source 口径）。

Revision ID: d3f7a1b9c2e4
Revises: c1eaf6d23b07
Create Date: 2026-07-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d3f7a1b9c2e4"
down_revision: Union[str, Sequence[str], None] = "c1eaf6d23b07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # rollcall_devices — 点呼机注册表（Device_Contract §2）
    # ---------------------------------------------------------------
    op.create_table(
        "rollcall_devices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("device_type", sa.String(length=16), nullable=False),
        sa.Column("device_location", sa.Text(), nullable=False),
        sa.Column("device_notes", sa.Text(), nullable=True),
        sa.Column("public_key", sa.Text(), nullable=True),
        sa.Column("enroll_code_hash", sa.String(length=128), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "device_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "registered_by",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column(
            "registered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fw_version", sa.String(length=32), nullable=True),
        sa.CheckConstraint(
            "device_type IN ('card_reader','iphone_tag','hybrid')",
            name="ck_rollcall_device_type",
        ),
        sa.UniqueConstraint("device_id", name="uq_rollcall_device_device_id"),
    )
    op.create_index(
        "idx_rollcall_device_active",
        "rollcall_devices",
        ["device_active", "retired_at"],
    )

    # ---------------------------------------------------------------
    # nfc_cards — 卡绑定表（Device_Contract §5 / FIELD_REGISTRY §2.9）
    # ---------------------------------------------------------------
    op.create_table(
        "nfc_cards",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("card_uid", sa.String(length=14), nullable=False),
        sa.Column(
            "student_id",
            sa.Uuid(),
            sa.ForeignKey("students.id"),
            nullable=False,
        ),
        sa.Column(
            "card_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "issued_by",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "revoked_by",
            sa.Uuid(),
            sa.ForeignKey("teachers.id"),
            nullable=True,
        ),
        sa.Column("revoke_reason", sa.Text(), nullable=True),
        sa.CheckConstraint("LENGTH(card_uid) = 14", name="ck_nfc_card_uid_len"),
    )
    op.create_index("ix_nfc_cards_student_id", "nfc_cards", ["student_id"])
    op.create_index("idx_nfc_card_student", "nfc_cards", ["student_id", "card_active"])
    # 部分唯一索引：同一 UID 只能绑一个未作废学生（作废行不占槽 → 可重新绑定）
    op.create_index(
        "uq_nfc_card_uid_active",
        "nfc_cards",
        ["card_uid"],
        unique=True,
        sqlite_where=sa.text("revoked_at IS NULL"),
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    # ---------------------------------------------------------------
    # device_auth_nonces — 令牌换取 nonce 防重放（Device_Contract §2.3）
    # ---------------------------------------------------------------
    op.create_table(
        "device_auth_nonces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("nonce", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("device_id", "nonce", name="uq_device_auth_nonce"),
    )
    op.create_index(
        "idx_device_auth_nonce_created", "device_auth_nonces", ["created_at"]
    )


def downgrade() -> None:
    op.drop_index("idx_device_auth_nonce_created", table_name="device_auth_nonces")
    op.drop_table("device_auth_nonces")

    op.drop_index("uq_nfc_card_uid_active", table_name="nfc_cards")
    op.drop_index("idx_nfc_card_student", table_name="nfc_cards")
    op.drop_index("ix_nfc_cards_student_id", table_name="nfc_cards")
    op.drop_table("nfc_cards")

    op.drop_index("idx_rollcall_device_active", table_name="rollcall_devices")
    op.drop_table("rollcall_devices")
