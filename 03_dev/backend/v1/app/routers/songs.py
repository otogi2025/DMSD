"""点歌（UI「リクエスト曲」）endpoint — spec §7.11 最小版（投稿 + 一览）。

itsuki 2026-06-06 拍板做最小版 A：学生投稿 + 学生/老师按男女寮看一览。
通报（通報）+ 累计封禁（ban_level）+ 自动解禁 cron + 老师管理页 属完整版，降 v1.1。
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_principal, get_current_student

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
    # 演示隔离：principal（学生 / 老师都有 is_demo）只看与自己同侧学生的投稿
    # —— 演示老师 / 演示学生只看演示投稿，真老师 / 真学生只看真实投稿（双向防泄漏）
    stmt = (
        select(models.SongRequest)
        .join(models.Student, models.SongRequest.student_id == models.Student.id)
        .where(models.Student.is_demo == principal.is_demo)
        .order_by(models.SongRequest.created_at.desc())
    )
    if dorm is not None:
        stmt = stmt.where(models.SongRequest.dorm_unit == dorm)
    rows = db.scalars(stmt).all()
    return [schemas.SongRequestOut.model_validate(r) for r in rows]
