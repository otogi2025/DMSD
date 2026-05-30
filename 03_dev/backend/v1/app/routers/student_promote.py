"""学号一括进级 endpoint (spec §4.2)。

端点:
- POST /api/v1/students/bulk-promote  — 全员（或筛选）grade_code +1

§4.2 规则：
- 进级时（每年 4 月）：全寮 grade_code +1
- 高 3（grade_code='06'）= 毕业生 → status 改为 'graduated'，grade_code 不变
- 中 6 年制编码：01(中1) ... 06(高3)，进级后 05→06(高3) 是最后一步
- 操作必须带 dry_run=True 先预览，确认后再 dry_run=False 真改
- 写 audit_logs（action=student.bulk_promote）
- 不建新表，只改 students.grade_code / students.status

角色 gate: 寮務部長 / 寮務課長 / 管理係（ADMIN_ROLES，同 admin_accounts.py）

TODO（本次未实装，规格待拍板）:
- 班级编成变更（年度内个别 patch） → 走 admin_accounts.py PATCH /accounts/:id，不在本 router
- 转校生年度途中编入 → 走 POST /students（新学生注册）
- 进级后 push 通知学生 → v1.1+ 议题（通知系统对接）
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import require_teacher_roles

router = APIRouter(prefix="/api/v1/students", tags=["student / promote"])

# 同 admin_accounts.py ADMIN_ROLES
_ADMIN_ROLES = ("寮務部長", "寮務課長", "管理係")

# 高 3 = 最高学年（graduation 触发）
_MAX_GRADE = "06"


@router.post(
    "/bulk-promote",
    response_model=schemas.BulkPromoteOut,
    status_code=status.HTTP_200_OK,
)
def bulk_promote(
    body: schemas.BulkPromoteIn,
    teacher: models.Teacher = Depends(require_teacher_roles(*_ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """一括进级 — 全员 grade_code +1（高 3 毕业）。

    流程：
    1. 查所有 active 学生（排除 is_demo / 非 active 状态）
    2. 可选按 grade_code 过滤（body.target_grade_codes，默认全员）
    3. 分两类：
       - grade_code < '06' → grade_code +1（进级）
       - grade_code == '06' → status = 'graduated'（毕业，grade_code 不变）
    4. dry_run=True → 只返回预览列表，不写 DB
    5. dry_run=False → 真改 + 写 audit_logs
    """
    # 1. 查询 active 真实学生（只取 grade_code 合法的 '01'~'06'，跳过脏数据防 500）
    _VALID_GRADES = ["01", "02", "03", "04", "05", "06"]
    stmt = select(models.Student).where(
        models.Student.status == "active",
        models.Student.is_demo.is_(False),
        models.Student.grade_code.in_(_VALID_GRADES),
    )

    # 2. 可选年级过滤
    if body.target_grade_codes:
        stmt = stmt.where(models.Student.grade_code.in_(body.target_grade_codes))

    students = db.scalars(stmt.order_by(models.Student.grade_code)).all()

    # 3. 分类计算变更内容（不管 dry_run 都要算，给预览用）
    promote_entries: list[schemas.BulkPromoteEntry] = []
    graduate_entries: list[schemas.BulkPromoteEntry] = []

    for s in students:
        if s.grade_code == _MAX_GRADE:
            # 高 3 → 毕业
            graduate_entries.append(
                schemas.BulkPromoteEntry(
                    student_id=s.id,
                    student_no=s.student_no,
                    name=s.name,
                    old_grade_code=s.grade_code,
                    new_grade_code=s.grade_code,  # 不变
                    action="graduate",
                    old_status=s.status,
                    new_status="graduated",
                )
            )
        else:
            # 进级：grade_code +1（格式 "01"~"05" → "02"~"06"）
            new_grade = str(int(s.grade_code) + 1).zfill(2)
            promote_entries.append(
                schemas.BulkPromoteEntry(
                    student_id=s.id,
                    student_no=s.student_no,
                    name=s.name,
                    old_grade_code=s.grade_code,
                    new_grade_code=new_grade,
                    action="promote",
                    old_status=s.status,
                    new_status=s.status,  # 状态不变
                )
            )

    all_entries = promote_entries + graduate_entries

    # 4. dry_run → 直接返回预览，不写 DB
    if body.dry_run:
        return schemas.BulkPromoteOut(
            dry_run=True,
            promote_count=len(promote_entries),
            graduate_count=len(graduate_entries),
            total_affected=len(all_entries),
            entries=all_entries,
        )

    # 5. 真改：按 student_id 一个个 update
    student_map: dict[UUID, models.Student] = {s.id: s for s in students}

    for entry in promote_entries:
        student_map[entry.student_id].grade_code = entry.new_grade_code

    for entry in graduate_entries:
        student_map[entry.student_id].status = "graduated"

    # 6. 写 audit_logs（一条汇总 audit，payload 带受影响学生 ID 列表）
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="student.bulk_promote",
            target_type="students",
            target_id=teacher.id,  # 批量操作没单一 target，暂用 teacher.id 占位
            payload={
                "promote_count": len(promote_entries),
                "graduate_count": len(graduate_entries),
                "target_grade_codes": body.target_grade_codes or "all",
                "promoted_ids": [str(e.student_id) for e in promote_entries],
                "graduated_ids": [str(e.student_id) for e in graduate_entries],
            },
        )
    )

    db.commit()

    return schemas.BulkPromoteOut(
        dry_run=False,
        promote_count=len(promote_entries),
        graduate_count=len(graduate_entries),
        total_affected=len(all_entries),
        entries=all_entries,
    )
