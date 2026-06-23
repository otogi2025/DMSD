"""迁移链 smoke 测试（C1 / db-models-2 / db-models-3）。

三个 recreate='always' → 'auto' 改动后，验证从 base 到 head 的完整迁移链在全新
SQLite 库可跑通：auto 在 SQLite 仍会按需重建表完成 b2c3(CHECK+drop_column) /
a8b9(unique) / c3d4(CHECK) 的变更，不破裂。

PG 路径（auto 不重建、走普通 ALTER，C1「DROP applications 被外键引用而崩溃」随之
消失）本机无 PostgreSQL 不在此验证，由 alembic batch 语义 + codex 复核保证。
"""

from __future__ import annotations


def test_migrations_base_to_head_on_fresh_sqlite(tmp_path, monkeypatch):
    """从 base 跑到 head 不抛异常即通过（recreate='auto' 回归保护）。"""
    from alembic import command
    from alembic.config import Config

    db_file = tmp_path / "migsmoke.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    assert db_file.exists()
