"""students email lower unique index backend20

Revision ID: 134d631496f1
Revises: 8d7c6b5a4f30
Create Date: 2026-07-21 14:19:22.706543

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "134d631496f1"
down_revision: Union[str, Sequence[str], None] = "8d7c6b5a4f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """加 students.email 大小写不敏感唯一表达式索引（审查 backend#20）。

    应用层查重有 TOCTOU 竞态,并发可写重复邮箱;DB 层表达式唯一索引兜底,与 models.py
    __table_args__ 的 uq_students_email_lower 同名同定义(防模型/迁移漂移)。
    ⚠️ 若生产库已存在大小写重合的重复 email,本迁移会因唯一冲突失败——部署前需先清理重复。
    NULL 值不受唯一约束(lower(NULL)=NULL),多个空邮箱允许并存。
    """
    # 审查 backend#20：空串邮箱 '' 不是 NULL，lower('')='' 会互相冲突 → 历史遗留多条 email=''
    # 的行会让下面建唯一索引直接失败。建索引前先把空串归一成 NULL（与应用层「空 email 存 NULL」
    # 口径一致），既免冲突又让多个「没填邮箱」的学生合法并存。
    op.execute("UPDATE students SET email = NULL WHERE email = ''")
    op.create_index(
        "uq_students_email_lower",
        "students",
        [sa.text("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    """回滚：删 students.email 大小写不敏感唯一表达式索引。"""
    op.drop_index("uq_students_email_lower", table_name="students")
