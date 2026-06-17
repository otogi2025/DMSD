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
# content_type 由客户端发来、可被伪造，故除白名单外再用文件头 magic bytes 二次校验真实类型
# （见 _magic_matches）—— 防止任意二进制伪装成 application/pdf / image/jpeg 落盘成「凭证」。
ALLOWED_CONTRACT_MIME: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/heic": ".heic",
    "application/pdf": ".pdf",
}

# ISO-BMFF（HEIC）major brand 白名单：前 4 字节为 box size，[4:8]='ftyp'，[8:12]=major brand
_HEIF_BRANDS: frozenset[bytes] = frozenset(
    {
        b"heic",
        b"heix",
        b"heif",
        b"hevc",
        b"hevx",
        b"mif1",
        b"msf1",
        b"heim",
        b"heis",
        b"hevm",
        b"hevs",
    }
)


def _magic_matches(head: bytes, mime: str) -> bool:
    """用文件头 magic bytes 校验真实类型是否与声明的 content_type 一致。

    head = 文件起始若干字节（取首个读取块即可，必含文件头）。
    mime 已确认在 ALLOWED_CONTRACT_MIME 白名单内。任一不匹配 → 调用方按 422 拒绝。
    """
    if mime == "image/jpeg":
        return head.startswith(b"\xff\xd8\xff")
    if mime == "image/png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if mime == "application/pdf":
        # PDF 规范要求 %PDF- 在文件最前（字节 0）。用 startswith 严格校验，不放宽到「前 1KB 内包含」——
        # 否则 HTML 等任意文件只要前段藏一个 %PDF- 就能伪装通过（codex 复审逮到的绕过）。
        return head.startswith(b"%PDF-")
    if mime == "image/heic":
        return len(head) >= 12 and head[4:8] == b"ftyp" and head[8:12] in _HEIF_BRANDS
    return False


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
    # 强制下载文件名后缀 = 校验后的真实类型 ext，不信原始文件名后缀
    # （防 evil.html 声明成 pdf 通过校验后仍以 .html 名下发；纵深加固，与 magic 校验配套）
    stem = cleaned.rsplit(".", 1)[0] if "." in cleaned else cleaned
    return f"{stem}{ext}"


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

    # 时间段重叠校验 — 同一学生不允许提交与现有 pending（审查中）/ approved（已许可）申请
    # 时间段相交的新申请，否则会叠出多份生效期重叠的许可、审批端难判定谁覆盖谁。
    # 两段 [a_from, a_to] 与 [b_from, b_to] 相交的充要条件：a_from <= b_to 且 b_from <= a_to
    # （含端点重合，因为单日申请 period_from == period_to 也算占用当天）。
    overlap_exists = db.scalar(
        select(models.StudyOnlineRequest.id)
        .where(
            models.StudyOnlineRequest.student_id == student.id,
            models.StudyOnlineRequest.status.in_(("pending", "approved")),
            models.StudyOnlineRequest.period_from <= body.period_to,
            models.StudyOnlineRequest.period_to >= body.period_from,
        )
        .limit(1)
    )
    if overlap_exists is not None:
        raise HTTPException(
            409,
            {
                "code": "ONLINE_REQUEST_OVERLAP",
                "message": "同じ期間の申請が既に存在します",
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
    # 缺数据即拒绝（fail-closed）：student 行被删 / student_id 悬空时，演示与寮隔离
    # 校验失去判定依据 —— 此时必须 404 拒绝，绝不能跳过校验直接放行审批操作。
    if student is None:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "届が見つかりません"})
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

    declared_mime = (file.content_type or "").lower()
    ext = ALLOWED_CONTRACT_MIME.get(declared_mime)
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
    # 策略：每次读 64 KB 块，先写到临时文件（abs_path + ".tmp"），全部校验通过（非空、未超限）后
    # 才 os.replace 原子替换到最终路径。中途失败（空 / 超限 / 磁盘错）只删临时文件、绝不碰旧合同 ——
    # 避免直接 open(最终路径,"wb") 截断旧合同后失败、把旧合同毁掉而 DB 还指向它。
    _CHUNK = 64 * 1024  # 每次读取块大小：64 KB
    old_rel = record.contract_file_path
    tmp_path = f"{abs_path}.tmp"
    total_bytes = 0
    header_checked = False
    try:
        with open(tmp_path, "wb") as out_f:
            while True:
                chunk = file.file.read(_CHUNK)
                if not chunk:
                    break
                if not header_checked:
                    header_checked = True
                    # magic bytes 二次校验：真实文件头与声明 content_type 不符即拒，
                    # 防任意二进制伪造扩展名落盘成「已验证凭证」、绕过老师目视核对前提。
                    if not _magic_matches(chunk, declared_mime):
                        out_f.close()
                        if os.path.isfile(tmp_path):
                            os.remove(tmp_path)
                        raise HTTPException(
                            422,
                            {
                                "code": "UNSUPPORTED_FILE_TYPE",
                                "message": "ファイルの内容が形式と一致しません（JPEG / PNG / HEIC / PDF）",
                            },
                        )
                total_bytes += len(chunk)
                if total_bytes > settings.contract_max_bytes:
                    out_f.close()
                    if os.path.isfile(tmp_path):
                        os.remove(tmp_path)
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
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise
    except OSError as exc:
        # 磁盘写入失败（权限 / 满盘等）→ 500
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"code": "STORAGE_ERROR", "message": "ファイルの保存に失敗しました"},
        ) from exc

    if total_bytes == 0:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(422, {"code": "EMPTY_FILE", "message": "ファイルが空です"})

    # 校验全通过 → 原子替换到最终路径（在此之前旧合同一直完好）
    try:
        os.replace(tmp_path, abs_path)
    except OSError as exc:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"code": "STORAGE_ERROR", "message": "ファイルの保存に失敗しました"},
        ) from exc

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
        # 缺数据即拒绝（fail-closed）：student 行被删 / student_id 悬空时，演示与寮隔离
        # 校验失去判定依据 —— 此时必须 404 拒绝，绝不能跳过校验直接放行文件。
        if student is None:
            raise HTTPException(
                404, {"code": "NOT_FOUND", "message": "契約書が見つかりません"}
            )
        # 演示读隔离：演示老师只能下载演示学生的契約書，否则 404（防凭真实 request UUID 越权下载）
        assert_student_demo_match(principal, student)
        allowed = dorm_units_for_teacher(principal)
        if allowed is not None and student.dorm_unit not in allowed:
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
        # filename= 已带 Content-Disposition: attachment；再加 nosniff 阻止浏览器 MIME 嗅探，
        # 避免存盘内容被当成非声明类型渲染（纵深加固，与上传 magic 校验配套）。
        headers={"X-Content-Type-Options": "nosniff"},
    )
