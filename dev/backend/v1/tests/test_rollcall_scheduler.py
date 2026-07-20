"""点呼调度器测试 — 审查 S1（backend#15 / backend#17）新增。

覆盖：
- backend#15：错过整个启动窗口仍 draft 的场次 → 置 ended 但不结算
  （不记缺席不扣分、ended_at=计划 auto_end、started_at 保持 NULL）
- backend#17：rollcall_sessions.dedupe_key 唯一索引（DB 层防重复建场）
  + 调度器建场写键 + 重跑 tick 不重复建场
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import models
from app import rollcall_scheduler as sched
from app.config import get_settings

_JST = ZoneInfo("Asia/Tokyo")

# 固定基准：2026-07-15 是周三（weekday 时刻表：morning 07:40 / evening 22:00）
_FIXED_DAY = (2026, 7, 15)


def _fake_datetime(hour: int, minute: int):
    """生成 datetime 替身类：now() 恒返回固定日 hour:minute JST，其余行为不变。"""

    class FakeDT(datetime):
        @classmethod
        def now(cls, tz=None):  # noqa: N805
            return datetime(*_FIXED_DAY, hour, minute, tzinfo=tz or _JST)

    return FakeDT


class TestMissedWindowDraft:
    """backend#15：错过窗口的 draft 收口。"""

    def test_zombie_draft_ended_without_settle(self, db_session, monkeypatch):
        """深夜（两场 auto_end 都已过）跑 tick：建出的场次直接置 ended、不结算。

        场次从未 running、学生想签也签不了 —— 不记缺席、不扣分（不拿系统故障罚学生）；
        ended_at = 计划 auto_end（不是 now，防止把设备离线补传窗拉长到重启时刻）；
        started_at 保持 NULL 作「从未开跑」标记。
        """
        monkeypatch.setattr(sched, "datetime", _fake_datetime(23, 30))
        sched._run_tick()

        sessions = db_session.scalars(select(models.RollCallSession)).all()
        assert len(sessions) == 2  # morning + evening 都建出并收口

        auto_end_minutes = get_settings().rollcall_auto_end_minutes
        expected_auto_end = {
            "morning": datetime(*_FIXED_DAY, 7, 40, tzinfo=_JST),
            "evening": datetime(*_FIXED_DAY, 22, 0, tzinfo=_JST),
        }
        for s in sessions:
            assert s.session_status == "ended"
            assert s.started_at is None, "从未开跑的场次 started_at 必须保持 NULL"
            assert s.ended_source == "system"
            # ended_at = 计划 auto_end（on_time_end + 配置分钟数），不是 now(23:30)
            want = expected_auto_end[s.session_type]
            got = s.ended_at
            assert got is not None
            assert (got - want).total_seconds() == auto_end_minutes * 60
            # dedupe_key 已写（backend#17）
            assert s.dedupe_key == f"2026-07-15:{s.session_type}:1,2,4"

        # 不结算：零签到事件、零扣分
        assert db_session.scalars(select(models.RollCallEvent)).first() is None
        assert db_session.scalars(select(models.DemeritEvent)).first() is None

    def test_second_tick_idempotent(self, db_session, monkeypatch):
        """重跑 tick 不重复建场（先查后插 + dedupe_key 双保险）。"""
        monkeypatch.setattr(sched, "datetime", _fake_datetime(23, 30))
        sched._run_tick()
        sched._run_tick()
        sessions = db_session.scalars(select(models.RollCallSession)).all()
        assert len(sessions) == 2


class TestDedupeKeyUnique:
    """backend#17：dedupe_key 唯一索引（DB 层）。"""

    def test_duplicate_dedupe_key_rejected(self, db_session):
        def _make():
            base = datetime(*_FIXED_DAY, 21, 55, tzinfo=_JST)
            return models.RollCallSession(
                dorm_unit_set=[1, 2, 4],
                session_type="evening",
                schedule_mode="merged_normal",
                day_type="weekday",
                session_status="draft",
                scheduled_window_start_at=base,
                scheduled_on_time_end_at=base,
                scheduled_late_end_at=base,
                scheduled_auto_end_at=base,
                dedupe_key="2026-07-15:evening:1,2,4",
            )

        db_session.add(_make())
        db_session.commit()
        db_session.add(_make())
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_null_dedupe_key_rows_coexist(self, db_session):
        """NULL 不参与唯一性 —— 测试/历史直建场次不受索引影响。"""
        base = datetime(*_FIXED_DAY, 6, 30, tzinfo=_JST)
        for _ in range(2):
            db_session.add(
                models.RollCallSession(
                    dorm_unit_set=[1, 2],
                    session_type="morning",
                    schedule_mode="split",
                    day_type="weekday",
                    session_status="draft",
                    scheduled_window_start_at=base,
                    scheduled_on_time_end_at=base,
                    scheduled_late_end_at=base,
                    scheduled_auto_end_at=base,
                )
            )
        db_session.commit()  # 不抛 = NULL 共存成立
