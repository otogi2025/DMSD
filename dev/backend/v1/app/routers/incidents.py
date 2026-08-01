"""事案録入 endpoint (spec §7.9 #33)。

端点:
- POST   /api/v1/incidents           — 老师录入事案
- GET    /api/v1/incidents           — 老师查事案列表
- GET    /api/v1/incidents/{id}      — 老师查事案详情
- PATCH  /api/v1/incidents/{id}      — 老师编辑事案
- DELETE /api/v1/incidents/{id}      — 老师软删事案

角色 gate: 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教師/管理係）
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    require_permission,
)

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])

# 事案记录的功能权限（C_INCIDENT：管理动作 M / 查看动作 V）由各端点的 require_permission 闸判定，
# 不再按职位拦（旧 _INCIDENT_ROLES 职位集已随权限分级改造移除）。
# 寮守卫：dorm_units_for_teacher 按令牌 selected_dorm 返回可见寮
# （选男→[1,2] / 选女→[4] / 未选或 op·承認组→[1,2,4]）；
# 涉及学生有任一不在可见寮 → FORBIDDEN_DORM（与 guidance / discipline 同口径）。


def _parse_involved_uuids(row: models.IncidentRecord) -> list[UUID]:
    """从事案的 involved_student_ids 抽出合法 UUID 列表（脏数据跳过）。"""
    uuids: list[UUID] = []
    for s in row.involved_student_ids or []:
        try:
            uuids.append(UUID(str(s)))
        except (ValueError, TypeError):
            # 入库前已全转成合法 UUID 字符串，这里只是防御历史脏数据
            pass
    return uuids


def _assert_student_in_dorm(teacher: models.Teacher, student: models.Student) -> None:
    """寮边界写校验 — 单个学生不在老师可见寮 → 403（照 discipline / guidance）。"""
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_DORM",
                "message": "担当外の寮の学生への操作はできません",
            },
        )


def _assert_incident_in_dorm(
    db: Session, teacher: models.Teacher, row: models.IncidentRecord
) -> None:
    """寮边界读/写校验 — 事案涉及学生必须全部在可见寮内，否则 403。

    判定口径见下方「全部可见」：正文是自由文本，可能写有真名；只要有一名
    不可见寮学生，放行整条就会泄漏其姓名/情节。无涉及学生 → 放行。
    """
    allowed = dorm_units_for_teacher(teacher)
    if allowed is None:
        return
    uuids = _parse_involved_uuids(row)
    if not uuids:
        return
    students = db.scalars(
        select(models.Student).where(models.Student.id.in_(uuids))
    ).all()
    by_id = {stu.id: stu for stu in students}
    for sid in uuids:
        student = by_id.get(sid)
        # 学生已删 / 找不到，或 dorm_unit 不在可见寮 → 一律拦（fail closed）
        if student is None or student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の事案への操作はできません",
                },
            )


def _filter_incidents_by_dorm(
    db: Session, rows: list[models.IncidentRecord], teacher: models.Teacher
) -> list[models.IncidentRecord]:
    """列表寮过滤 — 只保留「涉及学生全部在可见寮」的事案（批量查，避免逐条 N+1）。

    与 _assert_incident_in_dorm 同一口径；无涉及学生的事案保留。
    """
    allowed = dorm_units_for_teacher(teacher)
    if allowed is None:
        return rows
    uuids: set[UUID] = set()
    for row in rows:
        uuids.update(_parse_involved_uuids(row))
    if not uuids:
        return rows
    students = db.scalars(
        select(models.Student).where(models.Student.id.in_(uuids))
    ).all()
    dorm_by_id = {stu.id: stu.dorm_unit for stu in students}
    visible: list[models.IncidentRecord] = []
    for row in rows:
        involved = _parse_involved_uuids(row)
        if not involved:
            visible.append(row)
            continue
        if all(
            (d := dorm_by_id.get(sid)) is not None and d in allowed for sid in involved
        ):
            visible.append(row)
    return visible


def _build_student_name_map(
    db: Session, rows: list[models.IncidentRecord], teacher: models.Teacher
) -> dict[str, str]:
    """汇总多条事案的全部涉及学生 id，一次性批量查姓名，避免逐条 N+1 查询（B-中-21）。

    返回 id 字符串 → 姓名 的映射。只收录当前老师 demo_scope + 可见寮内能解析到的学生：
    演示老师只解析到演示学生、真老师只解析到真实学生，超出范围的 id 不进 map。
    """
    uuids: set[UUID] = set()
    for row in rows:
        uuids.update(_parse_involved_uuids(row))
    if not uuids:
        return {}
    stmt = select(models.Student).where(
        models.Student.id.in_(uuids),
        demo_scope_for_teacher(teacher),
    )
    # 防御性寮过滤：即使列表/详情已按寮裁剪，姓名 chip 也不回传可见寮外学生真名
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    students = db.scalars(stmt).all()
    return {str(stu.id): stu.name for stu in students}


def _to_incident_out(
    row: models.IncidentRecord, name_map: dict[str, str]
) -> schemas.IncidentRecordOut:
    """ORM 事案行 → 输出 schema，用预先批量查好的 name_map 填涉及学生姓名。

    杭田 2026-06-04 五-6: 前端要把涉及学生姓名做成可点击 chip 跳个人档案，所以解析姓名。

    演示隔离 + 计数防泄漏（B-低-20）: 只输出在 name_map 里能解析到姓名的学生 chip。
    被 demo_scope 过滤掉（演示老师看真实学生、或学生已删）的 id 直接不出现 ——
    既删掉了旧的恒真过滤死逻辑，也不再以「（不明）」占位泄漏「该事案有 N 名我看不到的学生」。
    """
    out = schemas.IncidentRecordOut.model_validate(row)
    raw_ids = [str(s) for s in (row.involved_student_ids or [])]
    out.involved_students = [
        schemas.IncidentStudentBrief(id=s, name=name_map[s])
        for s in raw_ids
        if s in name_map
    ]
    return out


def _to_incident_out_single(
    db: Session, row: models.IncidentRecord, teacher: models.Teacher
) -> schemas.IncidentRecordOut:
    """单条事案的 → 输出 schema（create / get / patch 用），内部批量查一次姓名后转换。"""
    name_map = _build_student_name_map(db, [row], teacher)
    return _to_incident_out(row, name_map)


@router.post("", response_model=schemas.IncidentRecordOut, status_code=201)
def create_incident(
    body: schemas.IncidentRecordCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_INCIDENT, permissions.MANAGE)
    ),
):
    """老师录入新事案。"""

    # 校验涉及学生是否都存在
    for sid in body.involved_student_ids:
        student = db.get(models.Student, sid)
        if not student:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": "対象の学生が見つかりません",
                },
            )
        # 演示隔离：演示老师不能把真实学生挂进事案、真老师不能挂演示学生（否则 404）
        assert_student_demo_match(teacher, student)
        # 寮边界：不许给不可见寮的学生建事案
        _assert_student_in_dorm(teacher, student)

    row = models.IncidentRecord(
        title=body.title,
        body=body.body,
        involved_student_ids=[str(s) for s in body.involved_student_ids],
        recorded_by=teacher.id,
        incident_date=body.incident_date,
    )
    db.add(row)
    db.flush()  # 让 row.id 生效
    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.create",
            target_type="incident_records",
            target_id=row.id,
            payload={
                "title": body.title,
                "incident_date": str(body.incident_date),
                "involved_count": len(body.involved_student_ids),
            },
        )
    )
    db.commit()
    db.refresh(row)
    return _to_incident_out_single(db, row, teacher)


@router.get("", response_model=schemas.IncidentRecordListOut)
def list_incidents(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_INCIDENT, permissions.VIEW)
    ),
):
    """老师查事案列表（按事发日期倒序，排除软删）。"""

    # 演示隔离：按事案创建者(recorded_by)的 is_demo 过滤 —— 演示老师只看演示老师建的事案、
    # 真老师只看真老师建的（事案本身没 demo 列，用现有创建者关系判，不改 schema）
    rows = db.scalars(
        select(models.IncidentRecord)
        .join(models.Teacher, models.Teacher.id == models.IncidentRecord.recorded_by)
        .where(
            models.IncidentRecord.deleted_at.is_(None),
            models.Teacher.is_demo == teacher.is_demo,
        )
        .order_by(models.IncidentRecord.incident_date.desc())
    ).all()
    # 寮过滤：只返回涉及学生全部在可见寮内的事案
    rows = _filter_incidents_by_dorm(db, list(rows), teacher)
    # B-中-21: 先把全部事案涉及的学生 id 汇总，一次批量查姓名，再分发给各行，避免逐条 N+1
    name_map = _build_student_name_map(db, list(rows), teacher)
    return schemas.IncidentRecordListOut(
        items=[_to_incident_out(r, name_map) for r in rows]
    )


@router.get("/{incident_id}", response_model=schemas.IncidentRecordOut)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_INCIDENT, permissions.VIEW)
    ),
):
    """老师查事案详情。"""

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 演示隔离：演示老师只能看演示老师建的事案（按创建者 is_demo），否则当作不存在 404
    if row.recorder is None or row.recorder.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 寮边界：涉及学生有不在可见寮的 → 403（与 student_profile 同口径，明示越权）
    _assert_incident_in_dorm(db, teacher, row)
    return _to_incident_out_single(db, row, teacher)


@router.patch("/{incident_id}", response_model=schemas.IncidentRecordOut)
def patch_incident(
    incident_id: UUID,
    body: schemas.IncidentRecordPatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_INCIDENT, permissions.MANAGE)
    ),
):
    """老师编辑事案（部分更新）。"""

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 演示隔离：演示老师只能改演示老师建的事案（按创建者 is_demo），否则当作不存在 404
    if row.recorder is None or row.recorder.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 寮边界：先拦对不可见寮事案的编辑
    _assert_incident_in_dorm(db, teacher, row)

    if body.title is not None:
        row.title = body.title
    if body.body is not None:
        row.body = body.body
    if body.involved_student_ids is not None:
        for sid in body.involved_student_ids:
            student = db.get(models.Student, sid)
            if not student:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "STUDENT_NOT_FOUND",
                        "message": "対象の学生が見つかりません",
                    },
                )
            # 演示隔离：替换涉及学生时同样禁止跨 demo 边界挂学生（否则 404）
            assert_student_demo_match(teacher, student)
            # 寮边界：不许把不可见寮学生挂进事案
            _assert_student_in_dorm(teacher, student)
        row.involved_student_ids = [str(s) for s in body.involved_student_ids]
    if body.incident_date is not None:
        row.incident_date = body.incident_date

    row.updated_at = datetime.now(timezone.utc)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.patch",
            target_type="incident_records",
            target_id=row.id,
            payload={"title": row.title},
        )
    )
    db.commit()
    db.refresh(row)
    return _to_incident_out_single(db, row, teacher)


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_INCIDENT, permissions.MANAGE)
    ),
):
    """老师软删事案（设 deleted_at，不物理删除）。"""

    row = db.get(models.IncidentRecord, incident_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 演示隔离：演示老师只能删演示老师建的事案（按创建者 is_demo），否则当作不存在 404
    if row.recorder is None or row.recorder.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INCIDENT_NOT_FOUND",
                "message": "該当する事案が見つかりません",
            },
        )
    # 寮边界：不许删不可见寮的事案
    _assert_incident_in_dorm(db, teacher, row)

    row.deleted_at = datetime.now(timezone.utc)

    db.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=teacher.id,
            action="incident.delete",
            target_type="incident_records",
            target_id=row.id,
            payload={},
        )
    )
    db.commit()
