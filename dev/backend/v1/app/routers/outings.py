"""外出申请 endpoint — 当天回寮的短时间外出，单一老师事后确认（itsuki 2026-06-04 拍板）。

POST   /api/v1/outings                 — 学生提出外出申请（提交即生效）
GET    /api/v1/outings/mine            — 学生看自己的外出申请
GET    /api/v1/outings/pending-for-me  — 老师看待确认列表（按 R4 寮边界过滤）
GET    /api/v1/outings/for-me          — 老师看全状态列表（含已处理历史，可按 status 过滤）
GET    /api/v1/outings/{id}            — 详情（学生本人 / 受寮边界的老师）
PATCH  /api/v1/outings/{id}/confirm    — 老师确认（确认者从登录令牌取，不信任客户端）
PATCH  /api/v1/outings/{id}/reject     — 老师却下（同上；只发通知 + 留记录）
PATCH  /api/v1/outings/{id}/withdraw   — 学生撤回自己 pending 的申请

跟出寮届（applications）的区别见 system_features §7.2.7：不过夜 / 没有多级审查 /
一名老师处理即可，处理老师从登录令牌自动记录。

2026-07-22 itsuki 拍板 — 语义从「事前审批制」改成「事后确认制」（只影响本文件的
outings，出寮届 applications 的多级审批一行不动）：
- 学生提交后立刻生效，可以直接出门，不用等老师同意；老师点「確認」= 留记录，不是放行开关
- 老师仍可「却下」（现实中很少用）：只发通知 + 留记录，不要求学生立刻回寮
- 扣分 ≥8 分（外出禁止 / 禁足）的学生在 POST 阶段就被挡住（OUTING_BANNED）
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
    require_permission,
)
from ..services import email as email_svc
from ..services import push as push_svc
from .discipline import CURFEW_THRESHOLD, current_month_total_points

_JST = ZoneInfo("Asia/Tokyo")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/outings", tags=["outings"])


def _to_outing_out(o: models.Outing) -> schemas.OutingOut:
    """ORM 外出对象 → 输出 schema；confirmed_by_name 从处理老师关系取姓名。"""
    student_brief = None
    if o.student:
        student_brief = schemas.StudentBrief(
            id=o.student.id,
            student_no=o.student.student_no,
            name=o.student.name,
            dorm_unit=o.student.dorm_unit,
            is_overseas=o.student.is_overseas,
            room_no=o.student.room_no,
        )
    return schemas.OutingOut(
        id=o.id,
        student_id=o.student_id,
        student=student_brief,
        outing_date=o.outing_date,
        destination=o.destination,
        leave_time=o.leave_time,
        return_time=o.return_time,
        taxi_reservation_time=o.taxi_reservation_time,
        reason=o.reason,
        status=o.status,
        submitted_at=o.submitted_at,
        withdrawn_at=o.withdrawn_at,
        confirmed_by_teacher_id=o.confirmed_by_teacher_id,
        confirmed_by_name=(o.confirmed_by.name if o.confirmed_by else None),
        confirmed_at=o.confirmed_at,
        reject_reason=o.reject_reason,
    )


# ---------------------------------------------------------------
# POST /outings — 学生提出外出申请
# ---------------------------------------------------------------
@router.post("", response_model=schemas.OutingOut, status_code=status.HTTP_201_CREATED)
def create_outing(
    body: schemas.OutingCreateIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    # 外出是当天回寮，外出日不能是过去（今天及以后都允许，跟出寮届「明天起」不同）
    if body.outing_date < datetime.now(_JST).date():
        raise HTTPException(
            status_code=422,
            detail={
                "code": "OUTING_DATE_PAST",
                "message": "外出日は本日以降を指定してください",
            },
        )

    # 外出禁止（禁足）闸 — itsuki 2026-07-22 拍板：扣分 ≥8 分的学生不能提交外出申请。
    # 事后确认制下提交即生效、老师事后才看到，所以这道闸必须放在提交时点、不能靠老师人工挡。
    # 分数口径复用 discipline.current_month_total_points（= /ranking 的 is_curfew_threshold
    # 同一套算法：JST 当月 + 排除已撤销），避免两处各算一遍导致「排行榜说禁足、提交却放行」。
    # 判定时点 = 提交那一刻的分数（提交时 7 分、外出当天涨到 8 分 不追溯，itsuki 明示不管）。
    if current_month_total_points(db, student.id) >= CURFEW_THRESHOLD:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "OUTING_BANNED",
                "message": (
                    "外出禁止中のため申請できません。"
                    "特別な事情がある場合は寮監に相談してください"
                ),
            },
        )

    outing = models.Outing(
        student_id=student.id,
        outing_date=body.outing_date,
        destination=body.destination,
        leave_time=body.leave_time,
        return_time=body.return_time,
        taxi_reservation_time=body.taxi_reservation_time,
        reason=body.reason,
        status="pending",
    )
    outing.student = student
    db.add(outing)
    db.flush()

    db.add(
        models.AuditLog(
            actor_type="student",
            actor_id=student.id,
            action="outing.submit",
            target_type="outing",
            target_id=outing.id,
            payload={"outing_date": outing.outing_date.isoformat()},
        )
    )
    db.commit()
    db.refresh(outing)
    return _to_outing_out(outing)


# ---------------------------------------------------------------
# GET /outings/mine — 学生看自己的外出申请
# ---------------------------------------------------------------
@router.get("/mine", response_model=list[schemas.OutingOut])
def list_mine(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.Outing)
        .where(models.Outing.student_id == student.id)
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
        .order_by(models.Outing.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.Outing.status == status_filter)
    return [_to_outing_out(o) for o in db.scalars(stmt).all()]


def _teacher_scoped_outings(
    db: Session,
    teacher: models.Teacher,
    *,
    status_filter: Optional[str],
    newest_first: bool,
) -> list[schemas.OutingOut]:
    """老师视角的外出申请查询 — 演示隔离 + R4 寮边界 + 可选状态过滤。

    pending-for-me（待处理队列，最老的排前面先处理）和 for-me（含历史的全状态列表，
    最新的排前面）共用，避免两个接口各写一套过滤逻辑导致寮边界漂移。
    """
    stmt = (
        select(models.Outing)
        .join(models.Student, models.Student.id == models.Outing.student_id)
        .where(demo_scope_for_teacher(teacher))
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
        .order_by(
            models.Outing.submitted_at.desc()
            if newest_first
            else models.Outing.submitted_at.asc()
        )
    )
    if status_filter:
        stmt = stmt.where(models.Outing.status == status_filter)
    # R4 寮边界：非跨寮角色只看自己寮的学生
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    return [_to_outing_out(o) for o in db.scalars(stmt).all()]


# ---------------------------------------------------------------
# GET /outings/pending-for-me — 老师看待确认列表（必须在 /{id} 之前注册）
#
# 跟 applications/pending-for-me 同理：静态路径在前 / 动态路径在后，
# 否则 "pending-for-me" 会被当成 UUID 解析 → 422。
# ---------------------------------------------------------------
@router.get("/pending-for-me", response_model=list[schemas.OutingOut])
def list_pending_for_me(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    return _teacher_scoped_outings(
        db, teacher, status_filter="pending", newest_first=False
    )


# ---------------------------------------------------------------
# GET /outings/for-me — 老师看全状态列表（含已处理的历史）
#
# 事后确认制（itsuki 2026-07-22 拍板）下老师端要能按「確認待ち / 確認済 / 却下済 / 取消済」
# 四态筛选看，pending-for-me 只出待处理的、看不到历史，所以另开这个接口。
# status 参数写法对齐 study.list_absence_requests（alias="status" 的可选过滤）。
# 同样必须注册在 /{id} 之前，否则 "for-me" 会被当 UUID 解析。
# ---------------------------------------------------------------
@router.get("/for-me", response_model=list[schemas.OutingOut])
def list_for_me(
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="pending（確認待ち）/ approved（確認済）/ rejected（却下済）/ withdrawn（学生取消）；不传 = 全部",
    ),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    return _teacher_scoped_outings(
        db, teacher, status_filter=status_filter, newest_first=True
    )


def _load_outing(db: Session, outing_id: UUID) -> models.Outing:
    outing = db.scalars(
        select(models.Outing)
        .where(models.Outing.id == outing_id)
        .options(
            selectinload(models.Outing.student),
            selectinload(models.Outing.confirmed_by),
        )
    ).first()
    if not outing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "外出申請が見つかりません"},
        )
    # 学生已删/悬空：后续 demo/寮校验会碰 outing.student → AttributeError→500；
    # 与 rollcall.patch_event 同口径 fail-closed 404。
    if outing.student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "外出申請が見つかりません"},
        )
    return outing


def _transition_outing(
    db: Session,
    outing_id: UUID,
    *,
    from_status: str,
    values: dict,
    audit_action: str,
    actor_type: str,
    actor_id: UUID,
    audit_payload: dict,
    conflict_message: str,
) -> models.Outing:
    """pending→目标状态的原子条件更新 + 审计 + 重载。

    竞态：rowcount != 1 说明已被别的请求改掉 → rollback + 409。
    confirm_outing / withdraw_outing 共用，避免两端各写一套同构逻辑。
    """
    result = db.execute(
        update(models.Outing)
        .where(models.Outing.id == outing_id, models.Outing.status == from_status)
        .values(**values)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "OUTING_NOT_PENDING",
                "message": conflict_message,
            },
        )
    db.add(
        models.AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=audit_action,
            target_type="outing",
            target_id=outing_id,
            payload=audit_payload,
        )
    )
    db.commit()
    return _load_outing(db, outing_id)


# ---------------------------------------------------------------
# GET /outings/{id} — 详情（学生本人 / 受寮边界的老师）
# ---------------------------------------------------------------
@router.get("/{outing_id}", response_model=schemas.OutingOut)
def get_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    actor: models.Student | models.Teacher = Depends(get_current_principal),
):
    outing = _load_outing(db, outing_id)
    if isinstance(actor, models.Student):
        if outing.student_id != actor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "他人の申請は閲覧できません"},
            )
    else:
        # 演示读隔离：演示老师只能看演示学生的外出详情、真老师只能看真实学生（否则 404）。
        # 防演示老师凭真实 outing UUID 越权读真实学生外出详情（codex 第4轮审查指出）。
        assert_student_demo_match(actor, outing.student)
        allowed = dorm_units_for_teacher(actor)
        if allowed is not None and outing.student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "担当寮外の申請です"},
            )
    return _to_outing_out(outing)


# ---------------------------------------------------------------
# PATCH /outings/{id}/confirm — 老师确认
#
# 安全核心：确认者 teacher_id 从登录令牌（get_current_teacher）取，
# 不接受客户端传入；按 R4 寮边界校验老师能不能确认这个学生。
# 2026-07-22 起「確認」是事后留记录、不是放行开关（学生提交时就已经能出门了）。
# ---------------------------------------------------------------
@router.patch("/{outing_id}/confirm", response_model=schemas.OutingOut)
def confirm_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    outing = _load_outing(db, outing_id)

    # 演示写隔离：演示老师只能确认演示学生的申请、真老师只能确认真实学生（否则 404）
    assert_student_demo_match(teacher, outing.student)

    # R4 寮边界：非跨寮角色只能确认自己寮的学生
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and outing.student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "担当寮外の申請は確認できません"},
        )

    # 原子条件更新：只有 status 仍是 pending 才确认成功。
    # 防两个老师并发确认 / 确认与撤回并发时都读到 pending、最后一次写覆盖前一次
    # （codex 2026-06-04 审查指出的竞态）。rowcount != 1 说明已被别的请求改掉 → 409。
    return _to_outing_out(
        _transition_outing(
            db,
            outing_id,
            from_status="pending",
            values={
                "status": "approved",
                "confirmed_by_teacher_id": teacher.id,
                "confirmed_at": datetime.now(timezone.utc),
            },
            audit_action="outing.confirm",
            actor_type="teacher",
            actor_id=teacher.id,
            audit_payload={"teacher_name": teacher.name},
            conflict_message="確認待ちの申請ではありません",
        )
    )


def _notify_outing_rejected(
    db: Session,
    *,
    outing: models.Outing,
    teacher: models.Teacher,
    reason: Optional[str],
) -> None:
    """把「却下了」通知给学生本人（邮件 + 推送）。

    itsuki 2026-07-22 拍板：却下不是「立刻回寮」的指示，只发通知 + 留记录。
    正文 = 老师填的评论（可选）+ 末尾固定加一句「※ 詳しくは寮監に確認してください」。

    只用项目已有的两套机制：邮件走 services/email（跟出寮届审批结果通知同一个形状，
    是「留得下」的通知）、推送走 services/push.send_push（当天外出，学生可能已经出门，
    要即时到达）。学生端没有「app 内通知」表 —— models.Notification 是老师通知中心专用
    （按 is_demo 做 realm 隔离、已读状态按老师各记各的），学生看不到，所以只有这两路。

    却下本身在 _transition_outing 里已经 commit 过了。两路通知各包一层 SAVEPOINT
    （db.begin_nested）单独隔离，写法与 applications.py 提交通知 / notifications.py /
    study.py 的兜底同形：某一路的 NotificationLog 写失败只回滚它自己那一段，不影响
    已成立的却下，也不影响另一路。
    """
    student = outing.student
    body_text = (
        f"{outing.outing_date} の外出申請が却下されました。\n"
        + (f"\n先生のコメント: {reason}\n" if reason else "")
        + "\n※ 詳しくは寮監に確認してください"
    )
    try:
        with db.begin_nested():
            email_svc.send_outing_rejected(
                db,
                outing=outing,
                student=student,
                teacher_name=teacher.name,
                reason=reason,
            )
    except Exception:  # noqa: BLE001 — 通知写入失败不能把已成立的却下带走
        logger.warning("外出却下的邮件通知写入失败 outing=%s", outing.id, exc_info=True)
    try:
        with db.begin_nested():
            push_svc.send_push(
                db,
                student_id=outing.student_id,
                title="外出申請 却下",
                body=body_text,
                template_key="outing_rejected",
                data={"kind": "outing", "outing_id": str(outing.id)},
            )
    except Exception:  # noqa: BLE001 — 同上
        logger.warning("外出却下的推送通知写入失败 outing=%s", outing.id, exc_info=True)
    db.commit()


# ---------------------------------------------------------------
# PATCH /outings/{id}/reject — 老师却下
#
# 事后确认制（itsuki 2026-07-22 拍板）：外出提交即生效，却下不要求学生立刻回寮，
# 只发通知 + 留记录。权限 / 寮边界 / 演示隔离全部跟 confirm 同一套。
# ---------------------------------------------------------------
@router.patch("/{outing_id}/reject", response_model=schemas.OutingOut)
def reject_outing(
    outing_id: UUID,
    body: Optional[schemas.OutingRejectIn] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    outing = _load_outing(db, outing_id)

    # 演示写隔离：演示老师只能却下演示学生的申请、真老师只能却下真实学生（否则 404）
    assert_student_demo_match(teacher, outing.student)

    # R4 寮边界：非跨寮角色只能处理自己寮的学生
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None and outing.student.dorm_unit not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "担当寮外の申請は却下できません"},
        )

    # 却下理由是可选的（itsuki 拍板：不强制老师写理由）。整个请求体省略也能通过。
    reason = body.reason if body is not None else None

    # 原子条件更新：只有 status 仍是 pending 才却下成功（与 confirm / withdraw 同款竞态防护）
    outing = _transition_outing(
        db,
        outing_id,
        from_status="pending",
        values={
            "status": "rejected",
            # confirmed_* 是「処理した先生 / 処理時刻」— 确认和却下共用（见 models.Outing 注释）
            "confirmed_by_teacher_id": teacher.id,
            "confirmed_at": datetime.now(timezone.utc),
            "reject_reason": reason,
        },
        audit_action="outing.reject",
        actor_type="teacher",
        actor_id=teacher.id,
        audit_payload={"teacher_name": teacher.name, "reason": reason},
        conflict_message="確認待ちの申請ではありません",
    )
    # 却下落库确定之后才给学生发通知（通知是副作用 — 失败也不影响已成立的却下）
    out = _to_outing_out(outing)
    _notify_outing_rejected(db, outing=outing, teacher=teacher, reason=reason)
    return out


# ---------------------------------------------------------------
# PATCH /outings/{id}/withdraw — 学生撤回自己 pending 的申请
# ---------------------------------------------------------------
@router.patch("/{outing_id}/withdraw", response_model=schemas.OutingOut)
def withdraw_outing(
    outing_id: UUID,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    outing = _load_outing(db, outing_id)
    if outing.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "他人の申請は取消できません"},
        )
    # 原子条件更新：只有 status 仍是 pending 才能撤回（防与老师确认并发互相覆盖）
    return _to_outing_out(
        _transition_outing(
            db,
            outing_id,
            from_status="pending",
            values={
                "status": "withdrawn",
                "withdrawn_at": datetime.now(timezone.utc),
            },
            audit_action="outing.withdraw",
            actor_type="student",
            actor_id=student.id,
            audit_payload={},
            conflict_message="確認待ちの申請のみ取消できます",
        )
    )
