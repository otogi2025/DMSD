"""add contract file columns to study_online_requests 20260604

2026-06-04: 在线学习申请加契約書（合同 = 网课报名凭证）文件上传。
study_online_requests 表加 4 列存上传的照片 / PDF 信息：
- contract_file_path  服务器上相对 upload_dir 的路径（contracts/<id>.<ext>），不暴露给客户端
- contract_file_name  学生上传时的原始文件名（老师下载时显示）
- contract_mime       文件类型（image/jpeg | image/png | image/heic | application/pdf）
- contract_size       文件字节数
全部 nullable —— 合同可选，老申请也不强制有。

Revision ID: c9d0e1f2a3b4
Revises: a7b8c9d0e1f2
Create Date: 2026-06-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "study_online_requests",
        sa.Column("contract_file_path", sa.Text(), nullable=True),
    )
    op.add_column(
        "study_online_requests",
        sa.Column("contract_file_name", sa.Text(), nullable=True),
    )
    op.add_column(
        "study_online_requests",
        sa.Column("contract_mime", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "study_online_requests",
        sa.Column("contract_size", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("study_online_requests", "contract_size")
    op.drop_column("study_online_requests", "contract_mime")
    op.drop_column("study_online_requests", "contract_file_name")
    op.drop_column("study_online_requests", "contract_file_path")
