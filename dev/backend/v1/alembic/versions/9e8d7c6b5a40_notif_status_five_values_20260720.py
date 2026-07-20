"""notification_log ck_notif_status 四值→五值重建（审查 migrations#0）

2026-07-20 五端审查：建表迁移 7a15771bdc7b 写死的 CHECK 只有
'pending','sent','failed','retrying' 四值，此后 38 个迁移从未改过；但
models.py（NOTIFICATION_STATUSES）与 push.py 早已是含 'skipped_no_provider'
的五值 —— push 凭证未配置时正常写入该值。pytest 用 create_all 按 models
建库所以永绿；经 alembic 升出来的 SQLite 开发库 / PostgreSQL 生产库仍是
旧四值 CHECK，学生有未撤销 device_token 且 APNs/FCM 未配置时，send_push
落 log 直接 IntegrityError，若与业务同事务还会连带回滚业务写入。

⚠️ 部署注记：生产开推送前必须先把本迁移升上去（alembic upgrade head），
顺序反了就是上面那个炸法。

Revision ID: 9e8d7c6b5a40
Revises: f0a1b2c3d4e5
Create Date: 2026-07-20

"""

from typing import Sequence, Union

from alembic import op

revision: str = "9e8d7c6b5a40"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FIVE = "status IN ('pending','sent','failed','retrying','skipped_no_provider')"
_FOUR = "status IN ('pending','sent','failed','retrying')"


def upgrade() -> None:
    # recreate="auto"：PG 走原生 ALTER 不重建表（无条件重建的写法在 PG 会因
    # 外键 CASCADE 崩，见 test_migration_smoke 静态守卫）；SQLite 按需重建。
    with op.batch_alter_table("notification_log", recreate="auto") as batch_op:
        batch_op.drop_constraint("ck_notif_status", type_="check")
        batch_op.create_check_constraint("ck_notif_status", _FIVE)


def downgrade() -> None:
    # 降级前把五值专属行归并成 failed（通知日志行，语义损失可接受），
    # 否则四值 CHECK 重建时存量行冲突、降级失败。
    op.execute(
        "UPDATE notification_log SET status = 'failed', "
        "last_error = COALESCE(last_error, 'downgrade: was skipped_no_provider') "
        "WHERE status = 'skipped_no_provider'"
    )
    with op.batch_alter_table("notification_log", recreate="auto") as batch_op:
        batch_op.drop_constraint("ck_notif_status", type_="check")
        batch_op.create_check_constraint("ck_notif_status", _FOUR)
