"""add teachers.permission_group (老师权限分级) 20260611

2026-06-11: 老师权限分级系统（design/teacher_permission_v1.md）。
teachers 表加 permission_group 列（5 值枚举 + NULL）：账号创建时指定一个权限组，
权限组决定该账号每个功能簇的权限级别（见 app/permissions.py PRESET 矩阵）。
职位 role 退化为纯显示标签、不参与鉴权。

- 列可空（NULL = 还没显式配组）；鉴权时 app/permissions.effective_group 对 NULL 按 role 回退默认组。
- 本迁移把现有老师按 role 回填一个默认组（与 ROLE_DEFAULT_GROUP 同一套映射）。
  生产环境可随后逐个账号显式改配。
- op 账号（最高运维账号）不在本迁移建 —— 由 seed.py 从环境变量 OP_PASSWORD 注入（密码绝不入仓库）。

Revision ID: f1a2b3c4d5e6
Revises: e6f7a8b9c0d1
Create Date: 2026-06-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 5 个权限组（teacher_permission_v1.md §3）
_GROUPS = ("op", "寮管理者", "一般宿管", "一般宿管+晚自习", "申請承認専用")

# 职位 → 默认权限组回填映射（与 app/permissions.ROLE_DEFAULT_GROUP 一致）
_ROLE_DEFAULT_GROUP = {
    "校長": "寮管理者",
    "寮務部長": "寮管理者",
    "寮務課長": "寮管理者",
    "国際交流部長": "申請承認専用",
    "国際交流課長": "申請承認専用",
    "管理係": "一般宿管",
    "寮監": "一般宿管+晚自习",
    "学習担当": "一般宿管+晚自习",  # 2026-06-12 F5：学習担当 负责晚自习管理，不映到只读的申請承認専用
    "寮務一般教師": "一般宿管",
}


def upgrade() -> None:
    # 1. 加列（可空，无 server_default）
    op.add_column(
        "teachers",
        sa.Column("permission_group", sa.String(length=32), nullable=True),
    )

    # 2. 按 role 回填现有老师
    teachers = sa.table(
        "teachers",
        sa.column("role", sa.String),
        sa.column("permission_group", sa.String),
    )
    for role, group in _ROLE_DEFAULT_GROUP.items():
        op.execute(
            teachers.update()
            .where(teachers.c.role == role)
            .values(permission_group=group)
        )

    # 3. CHECK 约束（5 值或 NULL）— batch 模式兼容 SQLite（Postgres 直接 ADD CONSTRAINT）
    _values = ",".join(f"'{g}'" for g in _GROUPS)
    with op.batch_alter_table("teachers") as batch_op:
        batch_op.create_check_constraint(
            "ck_teachers_permission_group",
            f"permission_group IS NULL OR permission_group IN ({_values})",
        )


def downgrade() -> None:
    with op.batch_alter_table("teachers") as batch_op:
        batch_op.drop_constraint("ck_teachers_permission_group", type_="check")
    op.drop_column("teachers", "permission_group")
