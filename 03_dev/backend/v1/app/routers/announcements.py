"""老师公告端点。

权威 spec：
- system_features.md §7.15（12 子节）
- 性质：老师 → 学生 单向 Classroom 风通知（学生回复是附带能力）
- scope: all / male / female（学生只看到自己 gender 对应的那部分，自动 filter）

API（§7.15.9）：
- GET    /announcements                  — 列表（按当前学生 scope 自动过滤）
- GET    /announcements/:id              — 详情 + 回复列表 + 自动写已读
- GET    /announcements/unread-count     — 主页 badge 用未读数
- POST   /announcements/:id/replies      — 回复（学生 / 老师都能调）
- DELETE /announcements/:id/replies/:rid — 回复软删（自己 or 老师）
- POST   /announcements                  — 老师专用：发公告
- PATCH  /announcements/:id              — 老师专用：编辑
- DELETE /announcements/:id              — 老师专用：软删

注：本文件 raise 的 detail.message 字段是给学生用户看的 UI 文案，按 spec 用日语；
注释一律中文。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func as sa_func, select
from sqlalchemy.orm import Session

from .. import models, permissions, schemas, security
from ..database import get_db
from ..deps import (
    _parse_bearer,
    assert_not_demo_teacher,
    get_current_principal,
    get_current_student,
    require_permission,
)

router = APIRouter(prefix="/api/v1/announcements", tags=["announcements"])

# 列表 view 显示的本文摘要最大字符数（§7.15.4）
SUMMARY_LENGTH = 80


def _scopes_for_student(student: models.Student) -> tuple[str, ...]:
    """学生 gender → 该学生能看到的 scope 集合（§7.15.1）。"""
    return ("all", student.gender)  # 男生 → ('all', 'male')；女生 → ('all', 'female')


def _summarize(body: str) -> str:
    """本文截 80 字摘要 — 换行先正规化为空格，避免列表里破版。"""
    cleaned = body.replace("\n", " ").replace("\r", " ").strip()
    if len(cleaned) <= SUMMARY_LENGTH:
        return cleaned
    return cleaned[:SUMMARY_LENGTH] + "…"


def _resolve_reply_author_name(reply: models.AnnouncementReply, db: Session) -> str:
    """按 author_kind 取学生 or 老师的名字（回复列表显示用）。"""
    if reply.author_kind == "teacher":
        teacher = db.get(models.Teacher, reply.author_id)
        return teacher.name if teacher else "(削除済教師)"
    student = db.get(models.Student, reply.author_id)
    return student.name if student else "(削除済学生)"


def _resolve_actor(
    authorization: Optional[str], db: Session
) -> Tuple[str, UUID, object]:
    """从 Authorization header 解出当前是学生还是老师。

    返回 (author_kind, author_id, ORM 对象)。
    专门给「学生 / 老师都能调」的端点（回复发 / 删）共用，避免每个端点重复 JWT 解析。
    """
    raise_unauth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_CREDENTIALS", "message": "ログインが必要です"},
    )
    if not authorization:
        raise raise_unauth
    try:
        token = _parse_bearer(authorization)
        payload = security.decode_token(token)
    except (security.JWTError, HTTPException):
        raise raise_unauth

    role = payload.get("role", "")
    # sub 缺失 / 非法 UUID 不能抛未捕获异常变成 500 — 返回友好 401
    try:
        actor_id = UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise raise_unauth
    if role == "student":
        actor = db.get(models.Student, actor_id)
        if not actor or actor.status != "active":
            raise raise_unauth
        return "student", actor_id, actor
    if role.startswith("teacher:"):
        actor = db.get(models.Teacher, actor_id)
        if not actor or actor.status != "active":
            raise raise_unauth
        return "teacher", actor_id, actor
    raise raise_unauth


# ---------------------------------------------------------------
# 学生 + 老师 共用：GET 系
# ---------------------------------------------------------------


@router.get("", response_model=schemas.AnnouncementListOut)
def list_announcements(
    principal: models.Student | models.Teacher = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    """列表 (FC-027 修复: 学生 + 老师都能调)。

    学生: scope 自动过滤 (按 gender) + 已读状态 + 回复数。
    老师: 全部公告 (不过滤 scope, 让老师能看到所有 scope 的内容) + is_read=False。
    """
    is_teacher = isinstance(principal, models.Teacher)
    if is_teacher:
        # 老师看全部公告 (准备发新的或巡查)
        rows = db.execute(
            select(models.Announcement, models.Teacher.name)
            .join(
                models.Teacher,
                models.Announcement.author_teacher_id == models.Teacher.id,
            )
            .where(models.Announcement.deleted_at.is_(None))
            .order_by(models.Announcement.created_at.desc())
        ).all()
        read_ids: set = set()
    else:
        # 学生按 scope (gender) 过滤
        scopes = _scopes_for_student(principal)
        rows = db.execute(
            select(models.Announcement, models.Teacher.name)
            .join(
                models.Teacher,
                models.Announcement.author_teacher_id == models.Teacher.id,
            )
            .where(
                models.Announcement.deleted_at.is_(None),
                models.Announcement.scope.in_(scopes),
            )
            .order_by(models.Announcement.created_at.desc())
        ).all()
        read_ids = set(
            db.scalars(
                select(models.AnnouncementRead.announcement_id).where(
                    models.AnnouncementRead.student_id == principal.id
                )
            ).all()
        )

    # 每个公告的回复数（announcement_id → count）
    reply_counts_raw = db.execute(
        select(
            models.AnnouncementReply.announcement_id,
            sa_func.count(models.AnnouncementReply.id),
        )
        .where(models.AnnouncementReply.deleted_at.is_(None))
        .group_by(models.AnnouncementReply.announcement_id)
    ).all()
    reply_counts = {aid: cnt for aid, cnt in reply_counts_raw}

    items = [
        schemas.AnnouncementBrief(
            id=ann.id,
            title=ann.title,
            body_summary=_summarize(ann.body),
            scope=ann.scope,
            author_teacher_id=ann.author_teacher_id,
            author_teacher_name=teacher_name,
            created_at=ann.created_at,
            updated_at=ann.updated_at,
            is_read=(ann.id in read_ids),
            reply_count=reply_counts.get(ann.id, 0),
        )
        for ann, teacher_name in rows
    ]
    return schemas.AnnouncementListOut(items=items)


@router.get("/unread-count", response_model=schemas.AnnouncementUnreadCountOut)
def get_unread_count(
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """主页 badge 用 — 当前学生 scope 内未读公告数 (学生 only — 老师没有未读概念)。"""
    scopes = _scopes_for_student(student)
    total = db.scalar(
        select(sa_func.count(models.Announcement.id)).where(
            models.Announcement.deleted_at.is_(None),
            models.Announcement.scope.in_(scopes),
        )
    )
    read_count = db.scalar(
        select(sa_func.count(models.AnnouncementRead.announcement_id))
        .join(
            models.Announcement,
            models.Announcement.id == models.AnnouncementRead.announcement_id,
        )
        .where(
            models.AnnouncementRead.student_id == student.id,
            models.Announcement.deleted_at.is_(None),
            models.Announcement.scope.in_(scopes),
        )
    )
    return schemas.AnnouncementUnreadCountOut(
        unread_count=max(0, (total or 0) - (read_count or 0))
    )


@router.get("/{announcement_id}", response_model=schemas.AnnouncementDetailOut)
def get_announcement_detail(
    announcement_id: UUID,
    principal: models.Student | models.Teacher = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    """详情 view (FC-027 修复: 学生 + 老师都能调).

    学生: scope 过滤 + 自动写 AnnouncementRead 已读.
    老师: 不过滤 scope (能看全部) + 不写已读 (AnnouncementRead 只学生表)。
    """
    is_teacher = isinstance(principal, models.Teacher)
    ann = db.get(models.Announcement, announcement_id)
    if not ann or ann.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "公告が見つかりません"},
        )
    # scope 过滤只对学生生效
    if not is_teacher and ann.scope not in _scopes_for_student(principal):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "この公告は閲覧対象外です"},
        )

    # 取作者老师的名字
    author = db.get(models.Teacher, ann.author_teacher_id)
    author_name = author.name if author else "(削除済教師)"

    # 写已读只对学生 (AnnouncementRead 表只有 student_id 字段)
    if not is_teacher:
        existing_read = db.get(
            models.AnnouncementRead,
            {"announcement_id": ann.id, "student_id": principal.id},
        )
        if existing_read is None:
            db.add(
                models.AnnouncementRead(
                    announcement_id=ann.id,
                    student_id=principal.id,
                )
            )
            db.commit()

    # 回复列表（旧→新，§7.15.6 Slack 风）
    reply_rows = db.scalars(
        select(models.AnnouncementReply)
        .where(
            models.AnnouncementReply.announcement_id == ann.id,
            models.AnnouncementReply.deleted_at.is_(None),
        )
        .order_by(models.AnnouncementReply.created_at.asc())
    ).all()
    # 作者名批量解析（避免按回复逐条 db.get 的 N+1）：
    # 先按 author_kind 把 author_id 分组，各做一次 IN 查询建 id→name 字典。
    teacher_ids = {r.author_id for r in reply_rows if r.author_kind == "teacher"}
    student_ids = {r.author_id for r in reply_rows if r.author_kind != "teacher"}
    teacher_names = (
        dict(
            db.execute(
                select(models.Teacher.id, models.Teacher.name).where(
                    models.Teacher.id.in_(teacher_ids)
                )
            ).all()
        )
        if teacher_ids
        else {}
    )
    student_names = (
        dict(
            db.execute(
                select(models.Student.id, models.Student.name).where(
                    models.Student.id.in_(student_ids)
                )
            ).all()
        )
        if student_ids
        else {}
    )

    def _reply_author_name(r: models.AnnouncementReply) -> str:
        if r.author_kind == "teacher":
            return teacher_names.get(r.author_id, "(削除済教師)")
        return student_names.get(r.author_id, "(削除済学生)")

    replies = [
        schemas.AnnouncementReplyOut(
            id=r.id,
            author_kind=r.author_kind,
            author_id=r.author_id,
            author_name=_reply_author_name(r),
            body=r.body,
            created_at=r.created_at,
        )
        for r in reply_rows
    ]

    return schemas.AnnouncementDetailOut(
        id=ann.id,
        title=ann.title,
        body=ann.body,
        scope=ann.scope,
        author_teacher_id=ann.author_teacher_id,
        author_teacher_name=author_name,
        created_at=ann.created_at,
        updated_at=ann.updated_at,
        replies=replies,
    )


# ---------------------------------------------------------------
# 学生 + 老师 共用：回复发 / 删
# ---------------------------------------------------------------


@router.post(
    "/{announcement_id}/replies",
    response_model=schemas.AnnouncementReplyOut,
    status_code=status.HTTP_201_CREATED,
)
def post_reply(
    announcement_id: UUID,
    body: schemas.AnnouncementReplyCreateIn,
    authorization: Annotated[Optional[str], Header()] = None,
    db: Session = Depends(get_db),
):
    """发回复 — 学生 / 老师都行（按 JWT 自动判 author_kind）。"""
    author_kind, author_id, actor = _resolve_actor(authorization, db)
    # 演示老师禁回复公告（公告无 is_demo，演示老师回复会出现在真实公告下、真实学生可见）→ 403
    if author_kind == "teacher":
        assert_not_demo_teacher(actor)

    ann = db.get(models.Announcement, announcement_id)
    if not ann or ann.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "公告が見つかりません"},
        )
    # 学生只能给自己 scope 内的公告回复
    if author_kind == "student" and ann.scope not in _scopes_for_student(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "この公告には返信できません"},
        )

    reply = models.AnnouncementReply(
        announcement_id=ann.id,
        author_kind=author_kind,
        author_id=author_id,
        body=body.body,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return schemas.AnnouncementReplyOut(
        id=reply.id,
        author_kind=reply.author_kind,
        author_id=reply.author_id,
        author_name=_resolve_reply_author_name(reply, db),
        body=reply.body,
        created_at=reply.created_at,
    )


@router.delete(
    "/{announcement_id}/replies/{reply_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reply(
    announcement_id: UUID,
    reply_id: UUID,
    authorization: Annotated[Optional[str], Header()] = None,
    db: Session = Depends(get_db),
):
    """删回复 — 自己发的 or 任意老师都能删。"""
    author_kind, author_id, _actor = _resolve_actor(authorization, db)
    is_teacher = author_kind == "teacher"
    # 演示老师禁删回复（「老师能删任何回复」会让演示老师删真实学生在真实公告下的回复）→ 403
    if is_teacher:
        assert_not_demo_teacher(_actor)

    reply = db.get(models.AnnouncementReply, reply_id)
    if not reply or reply.announcement_id != announcement_id or reply.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "返信が見つかりません"},
        )

    # 老师能删任何回复；学生只能删自己的
    if not is_teacher and reply.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "削除権限がありません"},
        )

    reply.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return None


# ---------------------------------------------------------------
# 老师专用：发公告 / 编辑 / 软删
# ---------------------------------------------------------------


@router.post(
    "", response_model=schemas.AnnouncementBrief, status_code=status.HTTP_201_CREATED
)
def post_announcement(
    body: schemas.AnnouncementCreateIn,
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """老师发公告 — 任何老师 role 都可以（不限定职务，§7.15.7）。"""
    # 演示老师禁发公告（公告无 is_demo、读侧只按性别过滤，会推送给全体真实学生）→ 403
    assert_not_demo_teacher(teacher)
    ann = models.Announcement(
        title=body.title,
        body=body.body,
        scope=body.scope,
        author_teacher_id=teacher.id,
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return schemas.AnnouncementBrief(
        id=ann.id,
        title=ann.title,
        body_summary=_summarize(ann.body),
        scope=ann.scope,
        author_teacher_id=ann.author_teacher_id,
        author_teacher_name=teacher.name,
        created_at=ann.created_at,
        updated_at=ann.updated_at,
        is_read=False,
        reply_count=0,
    )


@router.patch("/{announcement_id}", response_model=schemas.AnnouncementBrief)
def update_announcement(
    announcement_id: UUID,
    body: schemas.AnnouncementUpdateIn,
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """老师编辑 — v1.0 仅作者本人可编辑（寮监 admin 编辑 = v1.1）。"""
    ann = db.get(models.Announcement, announcement_id)
    if not ann or ann.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "公告が見つかりません"},
        )
    if ann.author_teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "投稿者本人のみ編集可"},
        )

    if body.title is not None:
        ann.title = body.title
    if body.body is not None:
        ann.body = body.body
    if body.scope is not None:
        ann.scope = body.scope
    db.commit()
    db.refresh(ann)

    return schemas.AnnouncementBrief(
        id=ann.id,
        title=ann.title,
        body_summary=_summarize(ann.body),
        scope=ann.scope,
        author_teacher_id=ann.author_teacher_id,
        author_teacher_name=teacher.name,
        created_at=ann.created_at,
        updated_at=ann.updated_at,
        is_read=False,
        reply_count=0,
    )


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: UUID,
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ANNOUNCE, permissions.MANAGE)
    ),
    db: Session = Depends(get_db),
):
    """老师软删 — v1.0 仅作者本人可删（寮监 admin 删 = v1.1）。"""
    ann = db.get(models.Announcement, announcement_id)
    if not ann or ann.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "公告が見つかりません"},
        )
    if ann.author_teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "投稿者本人のみ削除可"},
        )
    ann.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return None
