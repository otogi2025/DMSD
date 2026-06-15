"""学生通知 / 推送的「可见范围」单一真值（§7.13.1 投稿通知开关）。

两个方向共用同一套可见性规则，避免推送侧和 feed 侧各写一份、日后漂移：

- 方向 A（给定内容 → 查可见学生）：老师投稿勾选「学生に通知する」时广播推送用。
- 方向 B（给定学生 → 查可见内容范围）：学生通知中心 feed 过滤用（routers/student_notifications.py）。

可见性规则：
- 公告 scope:  all=全员 / male=男生 / female=女生（对 Student.gender）。按 ann.is_demo 隔离。
- 巴士 visible_to: all / dorm_only=全员 / men=男生 / women=女生。
- 行事: 无范围字段 → 全员。

demo 隔离（2026-06-16 codex 复审修）：巴士 / 行事 表本身无 is_demo 列，但都有
created_by_teacher_id → 按「创建老师的 is_demo」隔离（与公告 ann.is_demo 对称）。
- 方向 A（推送）：按创建老师 is_demo 选学生（见 _creator_is_demo）。
- 方向 B（feed，routers/student_notifications.py）：join teachers 过滤 Teacher.is_demo == student.is_demo。
两侧一致 —— 演示学生只看演示老师内容、真实学生只看真实老师内容（之前 feed 不过滤、演示学生能看到真实巴士/行事，已修）。
"""

from __future__ import annotations

import logging

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
    return stu


def students_for_event(db, event: models.DormEvent) -> list[models.Student]:
    return _active_students(
        db, is_demo=_creator_is_demo(db, event.created_by_teacher_id)
    )


def broadcast_push(
    db, *, students: list[models.Student], title: str, body: str
) -> None:
    """给一批学生逐个发推送（push.send_push 当面 stub 空跑、不真发、不 raise）。

    best-effort：单个学生推送失败只记日志，不中断（投稿主业务已先 commit、不受影响）。
    调用方负责在之后 db.commit() 持久化 notification_log。
    """
    for stu in students:
        try:
            push.send_push(
                db,
                student_id=stu.id,
                title=title,
                body=body,
                template_key="content_notify",
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
