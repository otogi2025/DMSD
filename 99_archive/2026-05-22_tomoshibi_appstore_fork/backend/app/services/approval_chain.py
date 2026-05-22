"""承认 chain 生成 — D4 (実物表 evidence) を中心に。

権威 = BACKEND_DESIGN_LOG.md §4.5 + §10 D4 + system_features.md §7.2.2。

⚠️ 2026-04-30 evidence 状況:
- 外泊届 = 実物表 ×2 (一般 / 留学生) で確定
- 帰省届 / 帰国届 = 実物表 evidence ⏳ 未入手 → 「外泊 chain - 国際交流」を暫定値に
- itsuki が次回老師に会った時に実物表 ×4 (帰省一般+留学生 / 帰国一般+留学生) を持ち帰る予定
- evidence 入手後は本ファイルの定数を書き換えるだけで chain 切替可能

担任 (homeroom) は per-学生 で `class_teacher_assignment` 表から解決。
他 5 役职 (寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長 / 管理係) は teachers.role で 1〜複数人。
"""
from __future__ import annotations

from datetime import date
from typing import Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .. import models


# ---------------------------------------------------------------
# Chain 定義 — 实物表 evidence ベース (D4)
# ---------------------------------------------------------------
# 担任は学生別に解决, 本リストには含めない (build_chain で自動付加)
EXTERNAL_ROLES_BY_KIND: dict[tuple[str, bool], tuple[str, ...]] = {
    # (kind, is_overseas) → 外部役职 chain (担任は除く)
    # ✅ 実物表 evidence 確定
    ("外泊", False): ("寮務課長", "管理係"),
    ("外泊", True): ("国際交流部長", "寮務課長", "寮務部長", "管理係"),
    # ⏳ evidence 未入手 — 暫定 = 外泊 chain - 国際交流
    # itsuki 4-30 prompt: 「先用「外泊 chain - 国際交流」的暂定值实装、evidence 进来再调」
    ("帰省", False): ("寮務課長", "管理係"),
    ("帰省", True): ("寮務課長", "寮務部長", "管理係"),
    ("帰国", False): ("寮務課長", "管理係"),
    ("帰国", True): ("寮務課長", "寮務部長", "管理係"),
}

# evidence pending な chain を呼び出し側で警告できるよう公開
PROVISIONAL_CHAINS: frozenset[tuple[str, bool]] = frozenset(
    {
        ("帰省", False),
        ("帰省", True),
        ("帰国", False),
        ("帰国", True),
    }
)


def is_provisional(kind: str, is_overseas: bool) -> bool:
    """この (kind, is_overseas) chain が evidence 待ちかどうか。

    呼出側で response header / log に "X-Approval-Chain-Provisional: true" を付ける用。
    """
    return (kind, is_overseas) in PROVISIONAL_CHAINS


def get_chain_roles(kind: str, is_overseas: bool) -> tuple[str, ...]:
    """届の種類 + 留学生フラグから chain 役职 list を返す。

    返り値は **担任 を先頭に含む完全な順序** (担任 → ... → 管理係)。
    DB に行を作る順番でもあり、UI 表示順でもある。
    """
    if kind not in {"帰省", "外泊", "帰国"}:
        raise ValueError(f"unknown application kind: {kind}")
    external = EXTERNAL_ROLES_BY_KIND[(kind, is_overseas)]
    return ("担任", *external)


# ---------------------------------------------------------------
# 担任 解決
# ---------------------------------------------------------------
def resolve_homeroom_teacher(
    db: Session,
    student: models.Student,
    *,
    on_date: date | None = None,
) -> models.Teacher | None:
    """学生 X の担任 (現役 = effective_to IS NULL) を返す。"""
    if on_date is None:
        on_date = date.today()
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
        )
        .limit(1)
    )
    return db.scalars(stmt).first()


# ---------------------------------------------------------------
# 役职 → 教師 list 解決 (邮件送信先計算用)
# ---------------------------------------------------------------
def resolve_teachers_by_role(
    db: Session,
    role: str,
    *,
    student: models.Student | None = None,
) -> list[models.Teacher]:
    """指定 role の現役教師を全員返す。

    担任の場合は student から resolve_homeroom_teacher を呼ぶ。
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
    return list(db.scalars(stmt).all())


# ---------------------------------------------------------------
# Chain 行生成 (DB INSERT)
# ---------------------------------------------------------------
def build_chain(
    db: Session,
    application: models.Application,
) -> list[models.ApplicationApproval]:
    """application 行に紐づく approval 行を chain 順で作って return (まだ commit しない)。

    呼出側 (POST /applications) が flush + 邮件送信 + commit をまとめる。
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
# 邮件 recipients 計算 (#6 R1)
# ---------------------------------------------------------------
def collect_recipients(
    db: Session,
    application: models.Application,
) -> tuple[list[models.Teacher], list[str]]:
    """届 1 件に対する 邮件送信先 全教师 list + ユニーク email list を返す。"""
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
