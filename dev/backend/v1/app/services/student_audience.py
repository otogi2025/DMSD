"""学生通知 / 推送的「可见范围」单一真值（§7.13.1 投稿通知开关）。

两个方向共用同一套可见性规则，避免推送侧和 feed 侧各写一份、日后漂移：

- 方向 A（给定内容 → 查可见学生）：老师投稿勾选「学生に通知する」时广播推送用。
- 方向 B（给定学生 → 查可见内容范围）：学生通知中心 feed 过滤用（routers/student_notifications.py）。

可见性规则：
- 公告 scope:  all=全员 / male=男生 / female=女生（对 Student.gender）。按 ann.is_demo 隔离。
- 巴士 visible_to: all / dorm_only / men=男生 / women=女生。
  ⚠️ dorm_only 当前与 all 等价（全员皆寮生、无通学生字段可区分）；真实「仅寮生」过滤留第二波。
- 行事: 无范围字段 → 全员。

demo 隔离（2026-06-16 codex 复审修）：巴士 / 行事 表本身无 is_demo 列，但都有
created_by_teacher_id → 按「创建老师的 is_demo」隔离（与公告 ann.is_demo 对称）。
- 方向 A（推送）：按创建老师 is_demo 选学生（见 _creator_is_demo）。
- 方向 B（feed，routers/student_notifications.py）：join teachers 过滤 Teacher.is_demo == student.is_demo。
两侧一致 —— 演示学生只看演示老师内容、真实学生只看真实老师内容（之前 feed 不过滤、演示学生能看到真实巴士/行事，已修）。
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select

from .. import models
from . import push

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# 方向 A：给定内容 → 查可见学生（投稿勾选「通知」时广播推送用）
# ---------------------------------------------------------------
def _active_students(db, *, is_demo: bool) -> list[models.Student]:
    return list(
        db.scalars(
            select(models.Student).where(
                models.Student.status == "active",
                models.Student.is_demo == is_demo,
            )
        )
    )


def students_for_announcement(db, ann: models.Announcement) -> list[models.Student]:
    stu = _active_students(db, is_demo=ann.is_demo)
    if ann.scope in ("male", "female"):
        stu = [s for s in stu if s.gender == ann.scope]
    return stu


def _creator_is_demo(db, teacher_id) -> bool:
    """创建者老师的 is_demo（巴士 / 行事无自身 is_demo 列 → 按创建老师隔离，与公告 ann.is_demo 对称）。"""
    if teacher_id is None:
        return False
    teacher = db.get(models.Teacher, teacher_id)
    return bool(teacher.is_demo) if teacher is not None else False


def students_for_bus(db, bus: models.BusRoute) -> list[models.Student]:
    stu = _active_students(db, is_demo=_creator_is_demo(db, bus.created_by_teacher_id))
    if bus.visible_to == "men":
        stu = [s for s in stu if s.gender == "male"]
    elif bus.visible_to == "women":
        stu = [s for s in stu if s.gender == "female"]
    elif bus.visible_to == "dorm_only":
        # backend#53：当前全员皆寮生，Student 表没有「通学生 / 寮生」区分字段，
        # 故 dorm_only 与 all 行为等价（都不做额外过滤，只保留在册 active 学生）。
        # 真实「仅寮生」过滤留第二波——届时按学生的寮生/通学生标志过滤。
        # 枚举值不可删（老师网页字面标「寮生のみ」，前端仍在传 dorm_only）。
        pass
    # visible_to == "all"（或未知值）→ 不额外过滤
    return stu


def students_for_event(db, event: models.DormEvent) -> list[models.Student]:
    return _active_students(
        db, is_demo=_creator_is_demo(db, event.created_by_teacher_id)
    )


def broadcast_push(
    db, *, students: list[models.Student], title: str, body: str
) -> None:
    """给一批学生发推送（push 当面 stub 空跑、不真发、不 raise）。

    best-effort：单个学生推送失败只记日志，不中断（投稿主业务已先 commit、不受影响）。
    调用方负责在之后 db.commit() 持久化 notification_log。

    backend#54：一次 IN 查出全部目标学生的有效设备令牌，再按 student_id 分组投递，
    避免「每个学生单独查 device_tokens」的 N+1。
    """
    if not students:
        return

    student_ids = [stu.id for stu in students]
    # 一次批量取出所有目标学生的未撤销令牌（device_tokens.student_id → students.id）
    all_tokens = list(
        db.scalars(
            select(models.DeviceToken).where(
                models.DeviceToken.student_id.in_(student_ids),
                models.DeviceToken.revoked_at.is_(None),
            )
        )
    )
    tokens_by_student: dict = defaultdict(list)
    for dt in all_tokens:
        tokens_by_student[dt.student_id].append(dt)

    template_key = "content_notify"
    for stu in students:
        tokens = tokens_by_student.get(stu.id, [])
        if not tokens:
            continue
        try:
            for dt in tokens:
                payload = {
                    "title": title,
                    "body": body,
                    "platform": dt.platform,
                    "token_id": str(dt.id),
                }
                log = models.NotificationLog(
                    channel="push",
                    template_key=template_key,
                    target_type="student",
                    target_id=stu.id,
                    target_email=None,
                    payload=payload,
                    status="pending",
                    attempts=0,
                )
                db.add(log)
                db.flush()  # log.id 确定

                try:
                    sent, error = push._dispatch_one(
                        platform=dt.platform,
                        token=dt.token,
                        title=title,
                        body=body,
                        data=None,
                        template_key=template_key,
                    )
                except Exception as exc:  # noqa: BLE001 — 推送投递任何异常都不得中断业务
                    sent, error = False, f"dispatch raised: {exc}"

                log.attempts = 1
                if sent:
                    log.status = "sent"
                    log.sent_at = datetime.now(timezone.utc)
                elif error and (
                    "not configured" in error or "not implemented" in error
                ):
                    log.status = "skipped_no_provider"
                    log.last_error = error[:500]
                    logger.warning(
                        "broadcast_push: provider not ready (platform=%s): %s",
                        dt.platform,
                        error,
                    )
                else:
                    log.status = "failed"
                    log.last_error = (error or "unknown error")[:500]
                    logger.error(
                        "broadcast_push: failed (platform=%s token_id=%s): %s",
                        dt.platform,
                        dt.id,
                        error,
                    )
        except Exception:  # noqa: BLE001 — 推送是副作用，绝不能拖垮投稿
            logger.warning(
                "broadcast_push 单学生失败 student=%s", stu.id, exc_info=True
            )


# ---------------------------------------------------------------
# 方向 B：给定学生 → 该学生可见的内容范围（学生通知 feed 过滤用）
# ---------------------------------------------------------------
def announcement_scopes_for_student(student: models.Student) -> tuple[str, ...]:
    """学生能看到的公告 scope 集合：全员 + 自己性别。"""
    return ("all", student.gender)


def bus_visible_to_for_student(student: models.Student) -> tuple[str, ...]:
    """学生能看到的巴士 visible_to 集合。"""
    own = "men" if student.gender == "male" else "women"
    return ("all", "dorm_only", own)
