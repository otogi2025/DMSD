"""点呼场次自动保障后台任务 — RollCall_Spec §5.5 + 附录 C.5 落地。

职责（每 tick，默认 60 秒）：
1. 按时刻表确保当日 morning / evening 场次存在（不存在则建 draft）。
2. 到 on_time_end − 3min 仍 draft → 自动 start（started_source=system）。
3. 到 scheduled_auto_end_at 仍 running → 自动 end + 结算（ended_source=system，复用 _settle_absent）。
start/end 同时向点呼机广播 session_started / session_ended（Device_Contract §5）。

⚠️ 由 settings.rollcall_scheduler_enabled 控制，**默认关**：测试 / dev 交互不跑，
不影响既有测试、不误建场次。生产在 .env 置 ROLLCALL_SCHEDULER_ENABLED=true 开启。

本波约定（v1.1 冻结 §2.3）：day_type 仅按周六日判定（无节假日表）；足球分组不启用；
dorm_unit_set 固定 [1,2,4]（全寮一场）。窗口写死：window_start=on_time_end−5min、
late_end=on_time_end+1s、auto_end=on_time_end+X 分钟（X=配置项，默认 15）。
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from starlette.concurrency import run_in_threadpool

from . import models
from .config import get_settings
from .database import SessionLocal
from .ws_manager import device_manager

logger = logging.getLogger("tomoshibi.rollcall_scheduler")

_JST = ZoneInfo("Asia/Tokyo")

# 本波固定：全寮一场（男 1+2 / 女 4），足球分组不启用
_DORM_UNIT_SET = [1, 2, 4]

# 普通寮生 on_time_end 时刻表（RollCall_Spec §4）：(session_type, day_type) → time
_ON_TIME_END: dict[tuple[str, str], time] = {
    ("morning", "weekday"): time(7, 40),
    ("evening", "weekday"): time(22, 0),
    ("morning", "weekend_holiday"): time(8, 50),
    ("evening", "weekend_holiday"): time(20, 0),
}

# 自动开始提前量（on_time_end − 3min，§5.5）
_AUTO_START_LEAD = timedelta(minutes=3)
# 窗口开放提前量（on_time_end − 5min，§5.3/§5.4）
_WINDOW_LEAD = timedelta(minutes=5)


def _day_type(d: date) -> str:
    """本波：周六(5)/周日(6) → weekend_holiday，其余 weekday（无节假日表）。"""
    return "weekend_holiday" if d.weekday() >= 5 else "weekday"


def _schedule_times(
    d: date, session_type: str, day_type: str, auto_end_minutes: int
) -> tuple[datetime, datetime, datetime, datetime]:
    """返回 (window_start, on_time_end, late_end, auto_end) 四个 JST-aware 时刻。

    late_end 仅为 DB 兼容值（on_time_end+1s，7-17 拍板：列保留写入、判定不读取，
    见 RollCall_Spec §5.3 修订注）。
    """
    ote_time = _ON_TIME_END[(session_type, day_type)]
    on_time_end = datetime.combine(d, ote_time, tzinfo=_JST)
    window_start = on_time_end - _WINDOW_LEAD
    late_end = on_time_end + timedelta(seconds=1)
    auto_end = on_time_end + timedelta(minutes=auto_end_minutes)
    return window_start, on_time_end, late_end, auto_end


def _broadcast_session_started(session: models.RollCallSession) -> None:
    device_manager.broadcast_sync(
        {
            "type": "session_started",
            "data": {
                "session_id": str(session.id),
                "session_type": session.session_type,
                "scheduled_on_time_end_at": session.scheduled_on_time_end_at.isoformat()
                if session.scheduled_on_time_end_at
                else None,
                # 7-17 拍板删 late_end 概念 → 契约 §5 改播 auto_end
                "scheduled_auto_end_at": session.scheduled_auto_end_at.isoformat()
                if session.scheduled_auto_end_at
                else None,
            },
        }
    )


def _broadcast_session_ended(session_id) -> None:
    device_manager.broadcast_sync(
        {"type": "session_ended", "data": {"session_id": str(session_id)}}
    )


def _run_tick() -> None:
    """一次 tick 的同步逻辑（在 threadpool 线程跑，用独立 SessionLocal）。"""
    settings = get_settings()
    auto_end_minutes = settings.rollcall_auto_end_minutes
    now = datetime.now(_JST)
    today = now.date()
    day_type = _day_type(today)

    with SessionLocal() as db:
        # 当日窗口边界（按 scheduled_window_start_at 归属当天）
        day_start = datetime.combine(today, time(0, 0), tzinfo=_JST)
        day_end = day_start + timedelta(days=1)
        todays = db.scalars(
            select(models.RollCallSession).where(
                models.RollCallSession.scheduled_window_start_at >= day_start,
                models.RollCallSession.scheduled_window_start_at < day_end,
            )
        ).all()

        for session_type in ("morning", "evening"):
            window_start, on_time_end, late_end, auto_end = _schedule_times(
                today, session_type, day_type, auto_end_minutes
            )

            # 找当天该 session_type、全寮一场（dorm_unit_set=[1,2,4]）的场次
            existing = next(
                (
                    s
                    for s in todays
                    if s.session_type == session_type
                    and (s.dorm_unit_set or []) == _DORM_UNIT_SET
                ),
                None,
            )

            # 1. 不存在 → 建 draft
            if existing is None:
                existing = models.RollCallSession(
                    dorm_unit_set=_DORM_UNIT_SET,
                    session_type=session_type,
                    schedule_mode="merged_normal",
                    day_type=day_type,
                    session_status="draft",
                    scheduled_window_start_at=window_start,
                    scheduled_on_time_end_at=on_time_end,
                    scheduled_late_end_at=late_end,
                    scheduled_auto_end_at=auto_end,
                )
                db.add(existing)
                db.commit()
                db.refresh(existing)
                logger.info(
                    "[scheduler] 建 draft 场次 type=%s day=%s id=%s",
                    session_type,
                    day_type,
                    existing.id,
                )

            # 2. 到 on_time_end − 3min 仍 draft → 自动 start（原子领取防并发）
            auto_start_at = on_time_end - _AUTO_START_LEAD
            if existing.session_status == "draft" and auto_start_at <= now <= auto_end:
                claimed = db.execute(
                    update(models.RollCallSession)
                    .where(
                        models.RollCallSession.id == existing.id,
                        models.RollCallSession.session_status == "draft",
                    )
                    .values(
                        session_status="running",
                        started_at=now,
                        started_source="system",
                    )
                )
                if claimed.rowcount == 1:
                    db.commit()
                    db.refresh(existing)
                    logger.info("[scheduler] 自动 start 场次 id=%s", existing.id)
                    _broadcast_session_started(existing)
                else:
                    db.rollback()

            # 3. 到 auto_end 仍 running → 自动 end + 结算（原子领取防与老师端并发双结算）
            if existing.session_status == "running" and now >= auto_end:
                claimed = db.execute(
                    update(models.RollCallSession)
                    .where(
                        models.RollCallSession.id == existing.id,
                        models.RollCallSession.session_status == "running",
                    )
                    .values(
                        session_status="ended",
                        ended_at=now,
                        ended_source="system",
                    )
                )
                if claimed.rowcount == 1:
                    db.refresh(existing)
                    # 复用现有结算逻辑（未签到 → absent + 扣分）
                    from .routers.rollcall import _settle_absent

                    _settle_absent(db, existing)
                    db.commit()
                    logger.info("[scheduler] 自动 end + 结算 场次 id=%s", existing.id)
                    _broadcast_session_ended(existing.id)
                else:
                    db.rollback()


async def _scheduler_loop() -> None:
    settings = get_settings()
    tick = max(5, settings.rollcall_scheduler_tick_seconds)
    logger.info("[scheduler] 点呼场次自动保障任务启动（tick=%ds）", tick)
    while True:
        try:
            await run_in_threadpool(_run_tick)
        except asyncio.CancelledError:
            logger.info("[scheduler] 任务取消，退出")
            raise
        except Exception:  # 单 tick 失败不能拖垮循环
            logger.warning("[scheduler] tick 执行异常", exc_info=True)
        await asyncio.sleep(tick)


def start_scheduler() -> asyncio.Task | None:
    """按 settings 开关启动后台任务；关闭时返回 None（不启动）。"""
    settings = get_settings()
    if not settings.rollcall_scheduler_enabled:
        logger.info("[scheduler] rollcall_scheduler_enabled=False → 不启动")
        return None
    return asyncio.create_task(_scheduler_loop())
