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
from .. import permissions
from ..deps import (
    assert_student_demo_match,
    demo_scope_for_teacher,
    dorm_units_for_teacher,
    get_current_principal,
    get_current_student,
    require_permission,
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_APPROVAL, permissions.VIEW)
    ),
):
    # 总是 join Student：演示隔离过滤（demo_scope_for_teacher）必须对全部角色生效，
    # 否则全寮角色（dorm_units_for_teacher 返回 None）的演示老师会看到真实学生申请。
    stmt = (
        select(models.StudyOnlineRequest)
        .join(
            models.Student,
            models.Student.id == models.StudyOnlineRequest.student_id,
        )
        .where(demo_scope_for_teacher(teacher))
        .order_by(models.StudyOnlineRequest.submitted_at.asc())
    )
    if status_filter:
        stmt = stmt.where(models.StudyOnlineRequest.status == status_filter)
    # R4 寮边界：寮監等 dorm-scoped 老师只看本寮学生的申请；全寮角色（寮務部長等）
    # dorm_units_for_teacher 返回 None → 不按寮过滤。列表含契約書文件名等元数据，
    # 跨寮可见会泄露别寮学生姓名 / 课程信息。
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
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
        require_permission(permissions.C_APPROVAL, permissions.MANAGE)
    ),
):
    record = db.get(models.StudyOnlineRequest, request_id)
    if not record:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})

    # R4 寮边界：寮監是 dorm-scoped 角色，只能审批本寮学生的在线申请
    student = db.get(models.Student, record.student_id)
    if student:
        # 演示写隔离：演示老师只能审批演示学生的申请，否则 404（防越权审批真实学生）
        assert_student_demo_match(teacher, student)
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

    settings = get_settings()
    contracts_dir = os.path.join(settings.upload_dir, "contracts")
    os.makedirs(contracts_dir, exist_ok=True)
    rel_path = os.path.join("contracts", f"{record.id}{ext}")
    abs_path = os.path.join(settings.upload_dir, rel_path)

    # 流式分块读取 — 不把整份文件 read() 进内存，防超大上传导致 OOM。
    # 策略：每次读 64 KB 块，累计字节数超限立即关闭文件并返回 422，
    # 字节数为 0（空文件）返回 422。写入目标文件也同步分块写，减少峰值内存占用。
    # 先写新文件 → 提交 DB → 最后才删旧文件。任一步失败时旧文件 + 旧 DB 路径仍一致，
    # 不会出现 DB 指向已删文件的孤儿状态。
    _CHUNK = 64 * 1024  # 每次读取块大小：64 KB
    old_rel = record.contract_file_path
    total_bytes = 0
    try:
        with open(abs_path, "wb") as out_f:
            while True:
                chunk = file.file.read(_CHUNK)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > settings.contract_max_bytes:
                    # 超限：删掉已写的临时文件，立即拒绝
                    out_f.close()
                    if os.path.isfile(abs_path):
                        os.remove(abs_path)
                    mb = settings.contract_max_bytes // (1024 * 1024)
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        {
                            "code": "FILE_TOO_LARGE",
                            "message": f"契約書は {mb} MB 以下にしてください",
                        },
                    )
                out_f.write(chunk)
    except HTTPException:
        raise
    except OSError as exc:
        # 磁盘写入失败（权限 / 满盘等）→ 500
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"code": "STORAGE_ERROR", "message": "ファイルの保存に失敗しました"},
        ) from exc

    if total_bytes == 0:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        raise HTTPException(422, {"code": "EMPTY_FILE", "message": "ファイルが空です"})

    record.contract_file_path = rel_path
    record.contract_file_name = _safe_filename(file.filename, ext)
    record.contract_mime = (file.content_type or "").lower()
    record.contract_size = total_bytes
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
        # 演示读隔离：演示老师只能下载演示学生的契約書，否则 404（防凭真实 request UUID 越权下载）
        if student is not None:
            assert_student_demo_match(principal, student)
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
