"""学生个人档案聚合页 endpoint (spec §7.10 #32)。

端点:
- GET /api/v1/students/{student_id}/profile  — 聚合返回该学生所有维度的履历

角色 gate:
- 寮務系老师（寮務部長/寮務課長/寮監/寮務一般教師/管理係）— 可看全部(含指导履历)
- 学生本人 — 只能看自己（指导履历 tab 不返回，符合 §7.10 C 案默认不显示）

实现说明:
- 只读现有表，不建表、不建迁移
- 各子块给最近 N 条（默认 20），带独立 limit query 参数
- 指导履历块：非寮務角色/学生自己 → 返空列表而非 403（符合 C 案"不显示 tab"语义）
- 用 Annotated[Optional[str], Header()] 取 Authorization header，避免 ruff 删 import
"""

# 注意：不加 `from __future__ import annotations`，避免 ruff 以为 Header 未使用而删 import

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
)

router = APIRouter(prefix="/api/v1", tags=["student / profile"])


def _get_student_or_404(student_id: UUID, db: Session) -> models.Student:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )
    return student


# IX-008: 登录学生看自己的基本信息（iOS 各页显示当前用户用 — 替换演示假数据 SEED.user）。
# 路由放在 /students/{student_id}/profile 之前 — "me" 是单段、不会被当 UUID 解析（A-013 教训）。
@router.get("/students/me", response_model=schemas.StudentProfileBasic)
def get_my_basic_profile(
    student: models.Student = Depends(get_current_student),
) -> schemas.StudentProfileBasic:
    """GET /students/me — 当前登录学生的基本信息（仿老师端 /teachers/me）。"""
    return schemas.StudentProfileBasic.model_validate(student)


# IX 个人信息编辑：学生改自己的联系方式 / 房间号（iOS 个人主页的「連絡先・部屋編集」接真后端）。
# 路由 /students/me 是字面段，PATCH 与上面 GET 同路径不同方法，不冲突。
@router.patch("/students/me", response_model=schemas.StudentProfileBasic)
def update_my_profile(
    body: schemas.StudentSelfUpdateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> schemas.StudentProfileBasic:
    """学生改自己的个人信息 — 只允许 email / phone / avatar_url / room_no。

    设计（无 spec，CC 取的最小安全方案）：
    - PATCH 只动「显式传了」的字段（exclude_unset），没传的保持原值
    - 番号 / 姓名 / 性别 / 寮 / 类别 不可自助改（番号走 renew-number，其余归老师）
    - email 改动查重（跟注册同口径，不能撞别人）
    - room_no 改动校验前缀与本人 dorm_unit 一致（M*** 男寮 1|2 / W*** 女寮 4），
      防学生换到异性寮 / 错号段；dorm_unit 本身学生改不了，所以等价于「同寮内换房间」
    """
    data = body.model_dump(exclude_unset=True)

    # email 改动查重（排除自己）
    if data.get("email"):
        dup = db.scalars(
            select(models.Student).where(
                models.Student.email == data["email"],
                models.Student.id != student.id,
            )
        ).first()
        if dup:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "EMAIL_TAKEN",
                    "message": f"email {data['email']} は既に使われています",
                },
            )

    # room_no 改动校验前缀 ↔ 本人 dorm_unit 一致
    if data.get("room_no"):
        prefix = data["room_no"][:1].upper()
        expected_prefix = "M" if student.dorm_unit in (1, 2) else "W"
        if prefix != expected_prefix:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_ROOM_FORMAT",
                    "message": (
                        f"部屋番号 '{data['room_no']}' は所属寮（{expected_prefix}***）"
                        "と一致しません"
                    ),
                },
            )

    # 应用更新（只动白名单字段；空字符串视为清空联系方式）
    for field in ("email", "phone", "avatar_url", "room_no"):
        if field in data:
            setattr(student, field, data[field])

    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="student.update_self_profile",
            target_type="student",
            target_id=student.id,
            payload={"fields": sorted(data.keys())},
        )
    )
    db.commit()
    db.refresh(student)
    return schemas.StudentProfileBasic.model_validate(student)


# 学生自设番号（番号再設定，spec §4.2 — 2026-06-05 学生自设方案）。
# 身份从登录令牌取（get_current_student），不信任客户端传 student_id。
# 路由 /students/me/renew-number 是字面段，不会被 /students/{id}/profile 吞。
@router.post("/students/me/renew-number", response_model=schemas.StudentProfileBasic)
def renew_my_number(
    body: schemas.StudentRenewNumberIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> schemas.StudentProfileBasic:
    """学生自设番号 — 选新的 学年/组/出席番号，撞号返 422。

    流程：
        1. 应用层查重：新「年级+班级+出席番号」被别人占（排除自己）→ 422
        2. 改本人三段番号 + 清 needs_renewal=False
        3. commit；并发抢同号 → DB 唯一约束 uq_students_no 兜底，转 422
        4. 写 audit_logs（actor=学生本人）
    """
    new_no = f"{body.grade_code}{body.class_code}{body.seat_no}"

    # 0. 必须老师已开闸（needs_renewal=True）才能自设 — 防绕过开闸直接调 API 改番号。
    #    iOS 顶部按钮也只在 needs_renewal 时显示，这里是后端兜底。
    if not student.needs_renewal:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RENEWAL_NOT_OPEN",
                "message": "学年更新の対象ではありません",
            },
        )

    # 1. 应用层查重（排除自己）— 照 accounts.py 注册查重模式
    existing = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == body.grade_code,
            models.Student.class_code == body.class_code,
            models.Student.seat_no == body.seat_no,
            models.Student.id != student.id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に他の人が設定しています",
            },
        )

    # 2. 改本人三段番号 + 清待更新标记
    student.grade_code = body.grade_code
    student.class_code = body.class_code
    student.seat_no = body.seat_no
    student.needs_renewal = False

    # 3. audit + commit（并发抢同号 → uq_students_no 唯一约束抛 IntegrityError → 转 422）
    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="student.renew_number",
            target_type="student",
            target_id=student.id,
            payload={"new_student_no": new_no},
        )
    )
    try:
        db.commit()
    except IntegrityError:
        # 并发抢同号：撤销本次事务（含上面 add 的「成功」AuditLog 与三段番号改动）。
        db.rollback()
        # rollback 会把成功审计一并回滚，所以这次「学生尝试改番号但撞号失败」原本不留任何痕迹。
        # A-491：补写一条失败审计（防探测他人番号占用），并在独立事务里 commit。
        # rollback 后 session 可继续用、会自动开新事务，故直接 add+commit 即可。
        db.add(
            models.AuditLog(
                actor_type="student",
                actor_id=student.id,
                action="student.renew_number_conflict",
                target_type="student",
                target_id=student.id,
                payload={"attempted_student_no": new_no},
            )
        )
        try:
            db.commit()
        except Exception:
            # 失败审计本身写不进去也不能影响业务返回（撞号仍要正确返 422），吞掉并回滚。
            db.rollback()
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STUDENT_NO_TAKEN",
                "message": f"学号 {new_no} は既に他の人が設定しています",
            },
        )

    db.refresh(student)
    return schemas.StudentProfileBasic.model_validate(student)


@router.get(
    "/students/{student_id}/profile",
    response_model=schemas.StudentProfileOut,
)
def get_student_profile(
    student_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="各子块返回最多条数"),
    db: Session = Depends(get_db),
    principal: models.Student | models.Teacher = Depends(get_current_principal),
) -> schemas.StudentProfileOut:
    """学生个人档案聚合页 (#32)。

    调用者可以是:
    - 寮務系老师: 可看全部，含指导履历
    - 学生本人: 只能看自己，指导履历返空（C 案）
    - 其他老师: 403
    """
    actor_teacher: models.Teacher | None = None
    actor_student: models.Student | None = None

    if isinstance(principal, models.Teacher):
        actor_teacher = principal
    else:
        actor_student = principal

    # ---- 老师鉴权：需要 C_GUIDANCE VIEW 权限，且受寮边界限制 ----
    if actor_teacher is not None:
        # 直接调用 permissions.has_permission 对已登录老师做权限判定：
        # 用 effective_group（permission_group 优先、为空按职位回退）判该组是否持有 C_GUIDANCE / VIEW（MANAGE 蕴含 VIEW）。
        # 比旧的 role in _GUIDANCE_ROLES 更准确 — 跟随 permission_group 体系，不硬编码职位字符串。
        if not permissions.has_permission(
            permissions.effective_group(actor_teacher),
            permissions.C_GUIDANCE,
            permissions.VIEW,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": "学生个人档案の閲覧には指導履歴の閲覧権限が必要です",
                },
            )
        # R4 寮边界：先取学生信息才能比对 dorm_unit
        _student_for_check = _get_student_or_404(student_id, db)
        # 演示隔离：真老师只能查真实学生，演示老师只能查演示学生
        # （is_demo 不匹配当作不存在 → 404，与 admin_accounts.py 同口径，防演示老师拉真实学生 profile 泄漏）
        if _student_for_check.is_demo != actor_teacher.is_demo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
            )
        allowed = dorm_units_for_teacher(actor_teacher)
        if allowed is not None and _student_for_check.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当寮外の学生プロフィールは閲覧できません",
                },
            )

    # ---- 学生只能查自己 ----
    if actor_student is not None:
        if actor_student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "他の学生のプロフィールは閲覧できません",
                },
            )

    # ---- 查学生基本信息 ----
    student = _get_student_or_404(student_id, db)

    # ---- 子块查询（各最近 limit 条，按时间倒序）----

    # 1. 出寮届履历（applications 表）
    applications = db.scalars(
        select(models.Application)
        .where(models.Application.student_id == student_id)
        .order_by(models.Application.submitted_at.desc())
        .limit(limit)
    ).all()

    # 2. 学习出席记录（study_checkins 表）
    study_checkins = db.scalars(
        select(models.StudyCheckin)
        .where(models.StudyCheckin.student_id == student_id)
        .order_by(models.StudyCheckin.target_date.desc())
        .limit(limit)
    ).all()

    # 3. 点呼记录（rollcall_events 表）— join session 取 session_type（朝/夜）
    #    杭田 2026-06-04 五-5：个人档案点呼履历要朝点呼/夜点呼分开，故带上 session_type
    rollcall_rows = db.execute(
        select(
            models.RollCallEvent,
            models.RollCallSession.session_type,
            # R-1③：带上窗口时刻，iOS 履历详情显真实開始/締切
            models.RollCallSession.scheduled_window_start_at,
            models.RollCallSession.scheduled_on_time_end_at,
        )
        .join(
            models.RollCallSession,
            models.RollCallSession.id == models.RollCallEvent.session_id,
        )
        .where(models.RollCallEvent.student_id == student_id)
        .order_by(models.RollCallEvent.checked_in_at.desc())
        .limit(limit)
    ).all()

    # 4. 指导履历（guidance_records 表）
    #    学生本人 → 空列表（C 案：默认不显示）
    #    寮務系老师 → 全部可见
    if actor_teacher is not None and permissions.has_permission(
        permissions.effective_group(actor_teacher),
        permissions.C_GUIDANCE,
        permissions.VIEW,
    ):
        guidance_records = db.scalars(
            select(models.GuidanceRecord)
            .where(
                models.GuidanceRecord.student_id == student_id,
                models.GuidanceRecord.deleted_at.is_(None),
            )
            .order_by(models.GuidanceRecord.guidance_date.desc())
            .limit(limit)
        ).all()
    else:
        guidance_records = []

    # 5. 扣分记录（demerit_event 表，排除已撤销）
    demerit_events = db.scalars(
        select(models.DemeritEvent)
        .where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.revoked_at.is_(None),
        )
        .order_by(models.DemeritEvent.created_at.desc())
        .limit(limit)
    ).all()

    # 6. 在线学习申请履历（study_online_requests 表，含契約書文件信息）
    #    老师点进学生个人页能看到该学生历史上传的所有合同。
    study_online_requests = db.scalars(
        select(models.StudyOnlineRequest)
        .where(models.StudyOnlineRequest.student_id == student_id)
        .order_by(models.StudyOnlineRequest.submitted_at.desc())
        .limit(limit)
    ).all()

    # ---- 组装响应 ----
    return schemas.StudentProfileOut(
        student=schemas.StudentProfileBasic(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            name_kana=student.name_kana,
            grade_code=student.grade_code,
            class_code=student.class_code,
            seat_no=student.seat_no,
            gender=student.gender,
            category=student.category,
            room_no=student.room_no,
            dorm_unit=student.dorm_unit,
            is_overseas=student.is_overseas,
            email=student.email,
            phone=student.phone,
            avatar_url=student.avatar_url,
            status=student.status,
            registered_at=student.registered_at,
            needs_renewal=student.needs_renewal,
        ),
        applications=[
            schemas.ProfileApplicationEntry(
                id=a.id,
                kind=a.kind,
                leave_date=a.leave_date,
                return_date=a.return_date,
                status=a.status,
                submitted_at=a.submitted_at,
            )
            for a in applications
        ],
        study_checkins=[
            schemas.ProfileStudyCheckinEntry(
                id=sc.id,
                target_date=sc.target_date,
                status=sc.status,
                checked_at=sc.checked_at,
            )
            for sc in study_checkins
        ],
        rollcall_events=[
            schemas.ProfileRollCallEntry(
                id=rce.id,
                session_id=rce.session_id,
                session_type=session_type,
                base_status=rce.base_status,
                status_source=rce.status_source,
                checked_in_at=rce.checked_in_at,
                scheduled_window_start_at=win_start,
                scheduled_on_time_end_at=ontime_end,
            )
            for rce, session_type, win_start, ontime_end in rollcall_rows
        ],
        guidance_records=[
            schemas.ProfileGuidanceEntry(
                id=gr.id,
                category=gr.category,
                guidance_date=gr.guidance_date,
                confidential=gr.confidential,
                content=gr.content,
                created_at=gr.created_at,
            )
            for gr in guidance_records
        ],
        demerit_events=[
            schemas.ProfileDemeritEntry(
                id=de.id,
                source_type=de.source_type,
                points=de.points,
                reason=de.reason,
                month=de.month,
                created_at=de.created_at,
            )
            for de in demerit_events
        ],
        study_online_requests=[
            schemas.ProfileStudyOnlineEntry(
                id=so.id,
                period_from=so.period_from,
                period_to=so.period_to,
                status=so.status,
                submitted_at=so.submitted_at,
                contract_file_name=so.contract_file_name,
                contract_mime=so.contract_mime,
                contract_size=so.contract_size,
            )
            for so in study_online_requests
        ],
    )
