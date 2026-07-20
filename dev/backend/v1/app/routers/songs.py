"""点歌（UI「リクエスト曲」）endpoint — spec §7.11（投稿 + 一览 + 老师删除）。

itsuki 2026-06-06 拍板：学生投稿 + 学生/老师按男女寮看一览。
（原通报 + 累计封禁 + 自动解禁 cron + 老师管理页设计 itsuki 2026-06-13 拍板彻底删除，不再降 v1.1）
2026-07-20 拍板 A 方案（App Store UGC 治理）：加回最小治理 = 通報（reports.py）+ 老师软删本文件。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_principal, get_current_student, get_current_teacher

router = APIRouter(prefix="/api/v1/songs", tags=["songs"])


@router.post("", response_model=schemas.SongRequestOut, status_code=201)
def create_song_request(
    body: schemas.SongRequestCreateIn,
    student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生投稿点歌 — dorm_unit 自动取登录学生的寮（不信任客户端传入）。"""
    row = models.SongRequest(
        student_id=student.id,
        dorm_unit=student.dorm_unit,
        song_title=body.song_title,
        artist=body.artist,
        note=body.note,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.SongRequestOut.model_validate(row)


@router.get("", response_model=list[schemas.SongRequestOut])
def list_song_requests(
    dorm: Optional[int] = Query(
        None, description="按寮过滤：1/2 男寮 / 4 女寮；不传=全部"
    ),
    db: Session = Depends(get_db),
    principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """点歌一览（投稿顺，新→旧）。学生 + 老师都能看；dorm 参数给老师男/女寮 tab 用。"""
    # dorm 取值校验（照 bus_routes 做法）：传了非法寮号直接 400，
    # 不静默返回空列表被误读为「真没投稿」。
    if dorm is not None and dorm not in (1, 2, 4):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_DORM", "message": "dorm 必须是 1 / 2 / 4"},
        )
    # 演示隔离：principal（学生 / 老师都有 is_demo）只看与自己同侧学生的投稿
    # —— 演示老师 / 演示学生只看演示投稿，真老师 / 真学生只看真实投稿（双向防泄漏）
    stmt = (
        select(models.SongRequest)
        .join(models.Student, models.SongRequest.student_id == models.Student.id)
        .where(
            models.Student.is_demo == principal.is_demo,
            models.SongRequest.deleted_at.is_(None),
        )
        .order_by(models.SongRequest.created_at.desc())
    )
    if dorm is not None:
        stmt = stmt.where(models.SongRequest.dorm_unit == dorm)
    rows = db.scalars(stmt).all()
    return [schemas.SongRequestOut.model_validate(r) for r in rows]


@router.delete("/{song_id}", status_code=204)
def delete_song_request(
    song_id: UUID,
    teacher: models.Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """老师软删一条点歌投稿（App Store UGC 治理 — 通報处理用）。"""
    row = db.get(models.SongRequest, song_id)
    if not row or row.deleted_at is not None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "投稿が見つかりません"}
        )
    row.deleted_at = datetime.now(timezone.utc)
    db.commit()
