"""承认 chain 生成 — 以 2026-05-28 实物表校正版为准。

权威 = BACKEND_DESIGN_LOG.md §4.5 + §10 D4 + system_features.md §7.2.2。

5-28 已确认：外泊、帰省、帰国留学生链都按实物表走。
目前只有帰国日本人仍是 evidence 待确认的暂定链。

担任 (homeroom) 按学生班级从 `class_teacher_assignment` 表解决。
其他役职从 teachers.role 查询；校長作为帰国留学生链尾的普通审批环。
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .. import models


# ---------------------------------------------------------------
# Chain 定义 — 2026-05-28 实物表校正版
# ---------------------------------------------------------------
# 担任由学生班级单独解决，本列表不含担任，build_chain 会自动加在最前面。
EXTERNAL_ROLES_BY_KIND: dict[tuple[str, bool], tuple[str, ...]] = {
    # 外泊日本人 = 担任・副担 → 寮務課長 → 寮務部長 → 管理係 = 4 人（5-28 加寮務部長，修旧 3 人记录）
    ("外泊", False): ("寮務課長", "寮務部長", "管理係"),
    # 外泊留学生 = 担任 → 国際交流部長 → 寮務課長 → 寮務部長 → 管理係 = 5 人（不变）
    ("外泊", True): ("国際交流部長", "寮務課長", "寮務部長", "管理係"),
    # 帰省 = 4 人，不分日本人/留学生（itsuki 5-28「跟实物表走」，留学生帰省也无国際交流部長）
    ("帰省", False): ("寮務課長", "寮務部長", "管理係"),
    ("帰省", True): ("寮務課長", "寮務部長", "管理係"),
    # 帰国日本人 = 实物表 evidence 待老师确认，保留旧暂定值
    ("帰国", False): ("寮務課長", "寮務部長", "管理係"),
    # 帰国留学生・長期休暇 = 担任 → 国際交流部長 → 寮務課長 → 寮務部長 → 管理係 → 校長
    ("帰国", True): ("国際交流部長", "寮務課長", "寮務部長", "管理係", "校長"),
}

# 只有帰国日本人还没有实物表 evidence，调用侧用它决定是否加提示 header。
PROVISIONAL_CHAINS: frozenset[tuple[str, bool]] = frozenset(
    {
        ("帰国", False),
    }
)


def is_provisional(kind: str, is_overseas: bool) -> bool:
    """该 (kind, is_overseas) chain 是否仍在等 evidence。

    调用侧用它决定要不要在 response header / log 加
    "X-Approval-Chain-Provisional: true"。
    """
    return (kind, is_overseas) in PROVISIONAL_CHAINS


def get_chain_roles(kind: str, is_overseas: bool) -> tuple[str, ...]:
    """按届种类 + 是否留学生，返回 chain 役职列表。

    返回值是 **以担任开头的完整顺序**（担任 → ... → 管理係）。
    既是写进 DB 的行顺序，也是 UI 显示顺序。
    """
    if kind not in {"帰省", "外泊", "帰国"}:
        raise ValueError(f"unknown application kind: {kind}")
    external = EXTERNAL_ROLES_BY_KIND[(kind, is_overseas)]
    return ("担任", *external)


# ---------------------------------------------------------------
# 担任解析
# ---------------------------------------------------------------
def resolve_homeroom_teacher(
    db: Session,
    student: models.Student,
    *,
    on_date: date | None = None,
) -> models.Teacher | None:
    """返回学生 X 的现任担任（effective_to IS NULL = 仍有效）。"""
    if on_date is None:
        on_date = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    academic_year = on_date.year if on_date.month >= 4 else on_date.year - 1

    stmt = (
        select(models.Teacher)
        .join(
            models.ClassTeacherAssignment,
            models.ClassTeacherAssignment.teacher_id == models.Teacher.id,
        )
        .where(
            models.ClassTeacherAssignment.grade_code == student.grade_code,
            models.ClassTeacherAssignment.class_code == student.class_code,
            models.ClassTeacherAssignment.academic_year == academic_year,
            models.ClassTeacherAssignment.is_homeroom.is_(True),
            or_(
                models.ClassTeacherAssignment.effective_to.is_(None),
                models.ClassTeacherAssignment.effective_to >= on_date,
            ),
            models.ClassTeacherAssignment.effective_from <= on_date,
            # 演示隔离：演示学生的担任只解析到演示老师，真实学生只解析到真实老师
            # （否则跨 cohort 担任绑定时，演示学生的通知邮件会发给真实老师）
            models.Teacher.is_demo == student.is_demo,
            # 审查 backend#52：停用老师不得再被解析为担任（与 resolve_teachers_by_role 同口径）
            models.Teacher.status == "active",
        )
        .limit(1)
    )
    return db.scalars(stmt).first()


# ---------------------------------------------------------------
# 役职 → 教师 list 解析（算邮件收件人用）
# ---------------------------------------------------------------
def resolve_teachers_by_role(
    db: Session,
    role: str,
    *,
    student: models.Student | None = None,
) -> list[models.Teacher]:
    """返回指定 role 的全部现役教师。

    role=担任 时从 student 调 resolve_homeroom_teacher。
    """
    if role == "担任":
        if not student:
            return []
        t = resolve_homeroom_teacher(db, student)
        return [t] if t else []

    stmt = select(models.Teacher).where(
        and_(
            models.Teacher.role == role,
            models.Teacher.status == "active",
        )
    )
    # 演示隔离：真实学生申请只找真老师、演示学生申请只找演示老师
    # （否则演示老师 role=寮務部長 会被算进真实学生申请的审批人 + 收到真实申请邮件）
    if student is not None:
        stmt = stmt.where(models.Teacher.is_demo == student.is_demo)
    return list(db.scalars(stmt).all())


# ---------------------------------------------------------------
# Chain 行生成 (DB INSERT)
# ---------------------------------------------------------------
def build_chain(
    db: Session,
    application: models.Application,
) -> list[models.ApplicationApproval]:
    """按 chain 顺序为 application 建 approval 行并返回（尚未 commit）。

    调用侧（POST /applications）统一做 flush + 发邮件 + commit。
    """
    student = application.student or db.get(models.Student, application.student_id)
    if not student:
        raise ValueError("student not found for application")

    roles = get_chain_roles(application.kind, student.is_overseas)
    rows: list[models.ApplicationApproval] = []
    for idx, role in enumerate(roles):
        row = models.ApplicationApproval(
            application_id=application.id,
            approver_role=role,
            chain_order=idx,
            approver_id=None,
            decided_at=None,
            decision=None,
        )
        db.add(row)
        rows.append(row)
    return rows


# ---------------------------------------------------------------
# 邮件 recipients 计算 (#6 R1)
# ---------------------------------------------------------------
def collect_recipients(
    db: Session,
    application: models.Application,
) -> tuple[list[models.Teacher], list[str]]:
    """对 1 件届，返回全部收件教师 list + 去重后的 email list。"""
    student = application.student or db.get(models.Student, application.student_id)
    if not student:
        return [], []
    roles = get_chain_roles(application.kind, student.is_overseas)

    teachers: list[models.Teacher] = []
    seen_ids: set = set()
    for role in roles:
        for t in resolve_teachers_by_role(db, role, student=student):
            if t.id not in seen_ids:
                teachers.append(t)
                seen_ids.add(t.id)
    emails = _unique_emails(t.email for t in teachers if t.email)
    return teachers, emails


def _unique_emails(emails: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for e in emails:
        e = e.strip().lower()
        if e and e not in seen:
            seen.add(e)
            out.append(e)
    return out
