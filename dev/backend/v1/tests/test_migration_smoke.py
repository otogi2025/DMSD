"""迁移链 smoke + 回归保护测试（C1 / db-models-2 / db-models-3）。

三个 recreate='always' → 'auto' 改动后的回归保护，分三层：

1. **SQLite 全链 smoke**：从 base 到 head 在全新 SQLite 库跑通（auto 在 SQLite 仍按需
   重建表完成 b2c3(CHECK+drop_column) / a8b9(unique) / c3d4(CHECK) 变更，不破裂）。
2. **静态守卫**：禁止任何迁移再用 recreate='always'。C1 的崩溃是 PostgreSQL-only，
   SQLite 上 always/auto 行为相同测不出 → 用静态扫描兜回归，谁再写 always 立刻红。
3. **真 PG 迁移（可选）**：设 TEST_PG_URL 后在真 PostgreSQL 上跑全链，验证 auto 不抛
   DependentObjectsStillExist。本机无 PG 时明确 skip（诚实的「没测」，不是假绿）。
"""

from __future__ import annotations

import os
import pathlib

import pytest


def test_migrations_base_to_head_on_fresh_sqlite(tmp_path, monkeypatch):
    """从 base 跑到 head 不抛异常即通过（recreate='auto' 在 SQLite 的回归保护）。"""
    from alembic import command
    from alembic.config import Config

    db_file = tmp_path / "migsmoke.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    assert db_file.exists()


def test_no_recreate_always_in_migrations():
    """静态守卫：禁止 alembic 迁移使用 batch_alter_table(recreate='always')。

    C1 教训：always 在 PostgreSQL 上无条件「建临时表→拷数据→DROP 原表→改名」。
    若原表被外键 CASCADE 引用（如 applications ← application_approvals），DROP 时抛
    DependentObjectsStillExist，整条迁移链中断 → 无法从零建 PG 库（灾备 / 换机 / CI）。
    SQLite 上 always 与 auto 行为相同，所以这种 PG-only 崩溃用 SQLite 测试测不到。
    本守卫静态扫描所有迁移，确保不再有人引入 always（回归保护）。
    确有必要用 always 时：在此显式豁免该文件名 + 人工确认目标表无外键依赖、PG 不崩。
    """
    versions = pathlib.Path(__file__).resolve().parent.parent / "alembic" / "versions"
    offenders = []
    for f in versions.glob("*.py"):
        text = f.read_text(encoding="utf-8")
        if 'recreate="always"' in text or "recreate='always'" in text:
            offenders.append(f.name)
    assert offenders == [], (
        f"以下迁移使用了 recreate='always'（PG 上对被外键引用的表会崩，见 C1）：{offenders}。"
        "改用 recreate='auto'，或在 test_no_recreate_always_in_migrations 显式豁免并人工验 PG。"
    )


@pytest.mark.skipif(
    not os.environ.get("TEST_PG_URL"),
    reason="无 PostgreSQL（设 TEST_PG_URL=postgresql+psycopg://user:pw@host:5432/db 启用；"
    "本项目驱动是 psycopg3，裸 postgresql:// 方言会去找不存在的 psycopg2）；"
    "C1 是 PG-only bug，SQLite 测不到，故此测试在无 PG 时明确 skip 而非假绿",
)
def test_migrations_base_to_head_on_postgresql(monkeypatch):
    """在真 PostgreSQL 上跑完整迁移链 base→head，验证 recreate='auto' 不抛
    DependentObjectsStillExist（C1 的真实回归保护）。

    TEST_PG_URL 必须指向一个**全新空**测试 PG 库（C1 场景就是「从零建 PG 库」）。
    不做 downgrade（c1eaf6d 的 downgrade 已标记不可逆），直接 upgrade head。
    CI 起 postgres 容器并设 TEST_PG_URL 即可真验证；未设则 skip——这是诚实的「没测」，
    区别于 SQLite smoke 那种「测了但测不到 PG 行为」的假绿。
    """
    from alembic import command
    from alembic.config import Config

    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_PG_URL"])
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
