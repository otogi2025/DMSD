"""学年更新「开闸」endpoint (spec §4.2)。

端点:
- POST /api/v1/students/renewal-start  — 老师开闸（学年更新を開始）

§4.2 规则（2026-06-05 学生自设方案，推翻 4-30 老师代改）:
- 老师每年 4 月点「学年更新を開始」一次 = 开闸 + 通知，本身不改任何番号。
- 中1~高2（grade_code != '06'）active 学生 → 打 needs_renewal=True 标记
  （学生 App 顶部据此显示「更新番号」按钮，由学生本人自设新番号）。
- 高3（grade_code == '06'）active 学生 → status='graduated'（毕业离寮，不打标记、不提醒）。
- dry_run=True 先预览，确认后 dry_run=False 真改。
- 写 audit_logs（action=student.renewal_start）。
- 不建新表，只改 students.needs_renewal / students.status。

权限 gate: require_permission(学生账号管理簇, 管理 M) — teacher_permission_v1.md §6
将 renewal 列为「学生账号管理」cluster 的管理动作（2026-06-11 权限分级；职位 role 退化为纯显示标签，不再参与鉴权）。body 内保留 demo 隔离 + 寮过滤（只开闸本人管辖寮）。

后续（本次未实装）:
- 开闸后 push 通知学生 → v1.1+ 议题（通知系统对接）
- 学生自设番号接口 = student_profile.py POST /students/me/renew-number
- 老师单件改番号兜底 = admin_accounts.py POST /accounts/{id}/renew-seat
- 看谁还没改进度 = admin_accounts.py GET /students/renewal-progress
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    require_permission,
)

router = APIRouter(prefix="/api/v1/students", tags=["student / renewal"])

# 高 3 = 最高学年（开闸时毕业，不打 needs_renewal 标记）
_MAX_GRADE = "06"
_VALID_GRADES = ["01", "02", "03", "04", "05", "06"]


@router.post(
    "/renewal-start",
    response_model=schemas.RenewalStartOut,
    status_code=status.HTTP_200_OK,
)
def renewal_start(
    body: schemas.RenewalStartIn,
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_STUDENT_ACCOUNT, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """开闸（学年更新を開始）— 中1~高2 打「待更新」标记、高3 毕业。

    流程：
    1. 查所有 active 真实学生（排除 is_demo / 非 active 状态 / 脏 grade_code）
    2. 分两类：
       - grade_code != '06' → action='notify'（needs_renewal=True，让学生自设）
       - grade_code == '06' → action='graduate'（status='graduated'，毕业离寮）
    3. dry_run=True → 只返回预览列表，不写 DB
    4. dry_run=False → 真改 + 写 audit_logs
    """
    # 0. 演示账号写隔离：开闸是 session 级批量写（影响一组学生，无法按单个学生判 demo），
    #    演示老师一律禁止
    if teacher.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DEMO_READONLY",
                "message": "デモアカウントは操作できません",
            },
        )

    # 1. 查询 active 真实学生（只取 grade_code 合法 '01'~'06'，跳过脏数据防 500）
    stmt = select(models.Student).where(
        models.Student.status == "active",
        demo_scope_for_teacher(teacher),
        models.Student.grade_code.in_(_VALID_GRADES),
    )
    # R4 寮边界：跨寮角色（寮務部長/課長）allowed=None 看全部；分寮管理係只开闸本人管辖寮
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    students = db.scalars(stmt.order_by(models.Student.grade_code)).all()

    # 2. 分类计算变更内容（不管 dry_run 都要算，给预览用）
    notify_entries: list[schemas.RenewalStartEntry] = []
    graduate_entries: list[schemas.RenewalStartEntry] = []

    for s in students:
        if s.grade_code == _MAX_GRADE:
            graduate_entries.append(
                schemas.RenewalStartEntry(
                    student_id=s.id,
                    student_no=s.student_no,
                    name=s.name,
                    grade_code=s.grade_code,
                    action="graduate",
                )
            )
        else:
            notify_entries.append(
                schemas.RenewalStartEntry(
                    student_id=s.id,
                    student_no=s.student_no,
                    name=s.name,
                    grade_code=s.grade_code,
                    action="notify",
                )
            )

    all_entries = notify_entries + graduate_entries

    # 3. dry_run → 直接返回预览，不写 DB
    if body.dry_run:
        return schemas.RenewalStartOut(
            dry_run=True,
            notify_count=len(notify_entries),
            graduate_count=len(graduate_entries),
            total_affected=len(all_entries),
            entries=all_entries,
        )

    # 4. 真改：按 student_id 一个个 update
    student_map: dict[UUID, models.Student] = {s.id: s for s in students}

    for entry in notify_entries:
        student_map[entry.student_id].needs_renewal = True

    for entry in graduate_entries:
        student_map[entry.student_id].status = "graduated"

    # 5. 写 audit_logs（一条汇总 audit，payload 带受影响学生 ID 列表）
    #    批量操作没单一 target，target_id 用 teacher.id 占位（target_id nullable=False）
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="student.renewal_start",
            target_type="students",
            target_id=teacher.id,
            payload={
                "notify_count": len(notify_entries),
                "graduate_count": len(graduate_entries),
                "notified_ids": [str(e.student_id) for e in notify_entries],
                "graduated_ids": [str(e.student_id) for e in graduate_entries],
            },
        )
    )

    db.commit()

    return schemas.RenewalStartOut(
        dry_run=False,
        notify_count=len(notify_entries),
        graduate_count=len(graduate_entries),
        total_affected=len(all_entries),
        entries=all_entries,
    )
