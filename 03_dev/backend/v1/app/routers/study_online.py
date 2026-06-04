"""在线学习申请 endpoint。

POST /api/v1/study/online-requests                 — 学生提交
GET  /api/v1/study/online-requests/mine            — 学生看自己的申请
GET  /api/v1/study/online-requests                 — 老师看待审列表
POST /api/v1/study/online-requests/{id}/decision   — 老师审批 / 取消许可
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import get_settings
from ..database import get_db
from ..deps import (
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
    get_current_teacher,
    require_teacher_roles,
)

router = APIRouter(prefix="/api/v1/study/online-requests", tags=["study"])

ONLINE_NOTICE_DAYS = 3

# 契約書（合同）允许的文件类型 → 存盘扩展名。
# 注意 content_type 由客户端发来、可被伪造；当前阶段（校内网 + 老师目视核对）白名单够用，
# v1.1 可加文件头 magic bytes 二次校验。
ALLOWED_CONTRACT_MIME: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/heic": ".heic",
    "application/pdf": ".pdf",
}


def _today_jst() -> date:
    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _now_jst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def _safe_filename(name: str | None, ext: str) -> str:
    """清理上传文件的原始文件名 — 去控制字符 / 换行（防 Content-Disposition 头注入）、
    去路径分隔符、限长。这个名字只作显示 + 下载默认名，存盘路径另用申请 id。"""
    if not name:
        return f"contract{ext}"
    cleaned = "".join(c for c in name if c.isprintable() and c not in "/\\").strip()
    if not cleaned:
        return f"contract{ext}"
    if len(cleaned) > 120:
        cleaned = cleaned[:120]
    return cleaned


@router.post(
    "",
    response_model=schemas.StudyOnlineRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_online_request(
    body: schemas.StudyOnlineRequestIn,
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    # 在线学习申请必须在开始 3 天前提交。
    earliest_start = _today_jst() + timedelta(days=ONLINE_NOTICE_DAYS)
    if body.period_from < earliest_start:
        raise HTTPException(
            422,
            {
                "code": "ONLINE_REQUEST_TOO_LATE",
                "message": "オンライン学習申請は開始 3 日前までに提出してください",
            },
        )

    record = models.StudyOnlineRequest(
        student_id=student.id,
        reason=body.reason,
        period_from=body.period_from,
        period_to=body.period_to,
        weekly_schedule=body.weekly_schedule,
        contract_ref=body.contract_ref,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.StudyOnlineRequestOut.model_validate(record)


@router.get("/mine", response_model=list[schemas.StudyOnlineRequestOut])
def list_my_online_requests(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    stmt = (
        select(models.StudyOnlineRequest)
        .where(models.StudyOnlineRequest.student_id == student.id)
        .order_by(models.StudyOnlineRequest.submitted_at.desc())
    )
    if status_filter:
        stmt = stmt.where(models.StudyOnlineRequest.status == status_filter)
    rows = db.scalars(stmt).all()
    return [schemas.StudyOnlineRequestOut.model_validate(row) for row in rows]


@router.get("", response_model=list[schemas.StudyOnlineRequestOut])
def list_online_requests(
    status_filter: str | None = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    stmt = select(models.StudyOnlineRequest).order_by(
        models.StudyOnlineRequest.submitted_at.asc()
    )
    if status_filter:
        stmt = stmt.where(models.StudyOnlineRequest.status == status_filter)
    # R4 寮边界：寮監等 dorm-scoped 老师只看本寮学生的申请；全寮角色（寮務部長等）
    # dorm_units_for_teacher 返回 None → 不过滤。列表含契約書文件名等元数据，
    # 跨寮可见会泄露别寮学生姓名 / 课程信息。
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.join(
            models.Student,
            models.Student.id == models.StudyOnlineRequest.student_id,
        ).where(models.Student.dorm_unit.in_(allowed))
    rows = db.scalars(stmt).all()
    return [schemas.StudyOnlineRequestOut.model_validate(row) for row in rows]


@router.post(
    "/{request_id}/decision",
    response_model=schemas.StudyOnlineRequestOut,
)
def decide_online_request(
    request_id: UUID,
    body: schemas.StudyOnlineDecisionIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_teacher_roles("学習担当", "寮務部長", "寮務課長", "寮監")
    ),
):
    record = db.get(models.StudyOnlineRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})

    # R4 寮边界：寮監是 dorm-scoped 角色，只能审批本寮学生的在线申请
    student = db.get(models.Student, record.student_id)
    if student:
        allowed = dorm_units_for_teacher(teacher)
        if allowed is not None and student.dorm_unit not in allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の学生への操作はできません",
                },
            )

    if body.decision == "revoked":
        if record.status != "approved":
            raise HTTPException(
                409,
                {
                    "code": "CANNOT_REVOKE",
                    "message": "許可済みの申請だけ取り消せます",
                },
            )
    elif record.status != "pending":
        raise HTTPException(
            409,
            {"code": "APPROVAL_ALREADY_DECIDED", "message": "既に決定済みです"},
        )

    record.status = body.decision
    record.decided_by = teacher.id
    record.decided_at = _now_jst()
    record.comment = body.comment
    db.commit()
    db.refresh(record)
    return schemas.StudyOnlineRequestOut.model_validate(record)


@router.post(
    "/{request_id}/contract",
    response_model=schemas.StudyOnlineRequestOut,
)
def upload_contract(
    request_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """学生给自己的在线学习申请上传契約書（合同 = 网课报名凭证）照片 / PDF。

    - 只能传自己的申请
    - 只有 pending（审查中）状态能传 / 换；已审批的不让改
    - 类型限 JPEG / PNG / HEIC / PDF，大小限 contract_max_bytes（默认 10 MB）
    - 存盘文件名用申请 id（防路径穿越 + 一个申请固定一个合同文件，重传即覆盖）
    """
    record = db.get(models.StudyOnlineRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})
    if record.student_id != student.id:
        raise HTTPException(
            403,
            {"code": "FORBIDDEN", "message": "他の学生の申請には添付できません"},
        )
    if record.status != "pending":
        raise HTTPException(
            409,
            {
                "code": "ALREADY_DECIDED",
                "message": "審査済みの申請の契約書は変更できません",
            },
        )

    ext = ALLOWED_CONTRACT_MIME.get((file.content_type or "").lower())
    if ext is None:
        raise HTTPException(
            422,
            {
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": "契約書は JPEG / PNG / HEIC / PDF のみ添付できます",
            },
        )

    contents = file.file.read()
    settings = get_settings()
    if len(contents) == 0:
        raise HTTPException(422, {"code": "EMPTY_FILE", "message": "ファイルが空です"})
    if len(contents) > settings.contract_max_bytes:
        mb = settings.contract_max_bytes // (1024 * 1024)
        raise HTTPException(
            422,
            {
                "code": "FILE_TOO_LARGE",
                "message": f"契約書は {mb} MB 以下にしてください",
            },
        )

    contracts_dir = os.path.join(settings.upload_dir, "contracts")
    os.makedirs(contracts_dir, exist_ok=True)
    rel_path = os.path.join("contracts", f"{record.id}{ext}")
    abs_path = os.path.join(settings.upload_dir, rel_path)

    # 先写新文件 → 提交 DB → 最后才删旧文件。任一步失败时旧文件 + 旧 DB 路径仍一致，
    # 不会出现 DB 指向已删文件的孤儿状态。
    old_rel = record.contract_file_path
    with open(abs_path, "wb") as f:
        f.write(contents)

    record.contract_file_path = rel_path
    record.contract_file_name = _safe_filename(file.filename, ext)
    record.contract_mime = (file.content_type or "").lower()
    record.contract_size = len(contents)
    db.commit()
    db.refresh(record)

    # 提交成功后清理旧扩展名文件（如先 PDF 后改 JPG），避免残留占盘
    if old_rel and old_rel != rel_path:
        old_abs = os.path.join(settings.upload_dir, old_rel)
        if os.path.isfile(old_abs):
            os.remove(old_abs)

    return schemas.StudyOnlineRequestOut.model_validate(record)


@router.get("/{request_id}/contract")
def download_contract(
    request_id: UUID,
    db: Session = Depends(get_db),
    principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """下载 / 查看某在线学习申请的契約書文件。

    谁能下：
    - 学生本人（看自己上传的）
    - 老师（受 R4 寮边界限制：寮監只能看本寮学生的；寮務部長等全寮可见）
    """
    record = db.get(models.StudyOnlineRequest, request_id)
    if not record or not record.contract_file_path:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "契約書が見つかりません"}
        )

    if isinstance(principal, models.Teacher):
        student = db.get(models.Student, record.student_id)
        allowed = dorm_units_for_teacher(principal)
        if (
            allowed is not None
            and student is not None
            and student.dorm_unit not in allowed
        ):
            raise HTTPException(
                403,
                {
                    "code": "FORBIDDEN_DORM",
                    "message": "担当外の寮の学生の契約書は閲覧できません",
                },
            )
    else:
        if principal.id != record.student_id:
            raise HTTPException(
                403,
                {"code": "FORBIDDEN", "message": "他の学生の契約書は閲覧できません"},
            )

    abs_path = os.path.join(get_settings().upload_dir, record.contract_file_path)
    if not os.path.isfile(abs_path):
        raise HTTPException(
            404,
            {"code": "FILE_MISSING", "message": "契約書ファイルが見つかりません"},
        )

    return FileResponse(
        abs_path,
        media_type=record.contract_mime or "application/octet-stream",
        filename=record.contract_file_name or "contract",
    )
