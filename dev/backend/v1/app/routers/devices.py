"""点呼机接入（device）端点 — Device_Contract §2/§4/§5 落地。

三组端点合于本文件：
1. 设备管理（老师 op 权限组，权限簇复用 C_ROLLCALL 点呼运营）：
   POST/GET /api/v1/devices、PATCH /api/v1/devices/{device_id}、
   POST /api/v1/devices/{device_id}/reset-enroll
2. 设备自助（无 token — 设备此刻还没令牌）：
   POST /api/v1/devices/{device_id}/enroll、POST /api/v1/devices/{device_id}/token
3. 设备日常（device JWT）：
   POST /api/v1/rollcall/device-checkins（核心签到）、
   GET /api/v1/devices/me/roster、audio-manifest、audio/{file}、
   POST /api/v1/devices/me/heartbeat
4. 卡绑定（老师 C_ROLLCALL）：POST/GET /api/v1/cards、DELETE /api/v1/cards/{card_uid}

判定时间基准 = 设备盖章的 swipe_time（Device_Contract §3）；老师代签端点（rollcall.py 的
POST /sessions/{id}/checkins）维持 server_now、行为不变、本文件不碰。
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import and_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import device_auth, models, permissions, schemas
from .. import ws_manager as _ws
from ..config import get_settings
from ..database import SessionLocal, get_db
from ..deps import (
    assert_not_demo_teacher,
    assert_student_demo_match,
    demo_scope_for_teacher,
    device_enr_token_claim,
    dorm_units_for_teacher,
    get_current_device,
    require_permission,
)
from ..security import create_access_token
from .rollcall import (
    ROLLCALL_LATE_POINTS,
    _assert_student_in_dorm,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["devices"])

# 设备令牌有效期 12 小时（Device_Contract §2.3）
_DEVICE_TOKEN_MINUTES = 12 * 60
# 令牌换取的时钟容忍 ±600 秒（§2.3）
_TS_TOLERANCE_SECONDS = 600
# nonce 防重放保留 24 小时（§2.3）
_NONCE_RETENTION_HOURS = 24
# card_uid = 14 位小写 hex（FIELD_REGISTRY §2.2）
_CARD_UID_RE = re.compile(r"^[0-9a-f]{14}$")
# 音频文件名白名单（防路径穿越）
_AUDIO_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+\.wav$")
# 音频 sha256 缓存：(绝对路径, mtime_ns, size) → hex digest；内容未变复用，避免每次全读全算
_audio_sha256_cache: dict[tuple[str, int, int], str] = {}
# 设备时钟异常审计的 action 名（写入与限流查询共用，防两处写岔）
_CLOCK_SKEW_ACTION = "device.clock_skew_clamped"

_JST = ZoneInfo("Asia/Tokyo")


def _now_jst() -> datetime:
    return datetime.now(_JST)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _as_jst_aware(value: datetime) -> datetime:
    """SQLite 读回 timezone=True 时可能丢 tzinfo，比较前统一补成 JST（同 rollcall._as_jst_aware）。"""
    if value.tzinfo is None:
        return value.replace(tzinfo=_JST)
    return value.astimezone(_JST)


def _get_device_or_404(db: Session, device_id: str) -> models.RollCallDevice:
    device = db.scalar(
        select(models.RollCallDevice).where(
            models.RollCallDevice.device_id == device_id
        )
    )
    if device is None:
        raise HTTPException(
            404, {"code": "UNKNOWN_DEVICE", "message": "デバイスが見つかりません"}
        )
    return device


# ===============================================================
# 1. 设备管理（老师 C_ROLLCALL）
# ===============================================================
@router.post("/devices", response_model=schemas.DeviceCreateOut, status_code=201)
def create_device(
    body: schemas.DeviceCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """创建设备记录（Device_Contract §2.2）— 返回一次性激活码明文，库里只存哈希。"""
    # 演示老师禁止创建真实硬件设备（全局基础设施，非演示沙盒范围）
    assert_not_demo_teacher(teacher)

    exists = db.scalar(
        select(models.RollCallDevice).where(
            models.RollCallDevice.device_id == body.device_id
        )
    )
    if exists is not None:
        raise HTTPException(
            409,
            {
                "code": "DEVICE_ALREADY_EXISTS",
                "message": "この device_id は既に存在します",
            },
        )

    enroll_code = device_auth.generate_enroll_code()
    device = models.RollCallDevice(
        device_id=body.device_id,
        device_type=body.device_type,
        device_location=body.device_location,
        device_notes=body.device_notes,
        enroll_code_hash=device_auth.hash_enroll_code(enroll_code),
        device_active=True,
        registered_by=teacher.id,
    )
    db.add(device)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "DEVICE_ALREADY_EXISTS",
                "message": "この device_id は既に存在します",
            },
        )
    db.refresh(device)
    return schemas.DeviceCreateOut(
        device_id=device.device_id,
        device_type=device.device_type,
        device_location=device.device_location,
        device_notes=device.device_notes,
        enroll_code=enroll_code,
        device_active=device.device_active,
    )


@router.get("/devices", response_model=list[schemas.DeviceOut])
def list_devices(
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    """设备一览（不含激活码 / 哈希 / 公钥）。"""
    # 审查 backend#32：设备表（RollCallDevice）无 is_demo / demo 归属字段——真实硬件是
    # 全局基础设施，不属于演示沙盒。create/patch/reset-enroll 已用 assert_not_demo_teacher
    # 挡住演示老师写；本 GET 对称：演示老师一律返回空列表，看不到真实点呼机资产。
    # （对照 list_cards 靠 Student.is_demo + demo_scope_for_teacher 过滤；设备无对等字段，
    #  故不能走同款 where，只能空列表。）
    if teacher.is_demo:
        return []
    rows = db.scalars(
        select(models.RollCallDevice).order_by(models.RollCallDevice.registered_at)
    ).all()
    return [schemas.DeviceOut.model_validate(d) for d in rows]


@router.patch("/devices/{device_id}", response_model=schemas.DeviceOut)
def patch_device(
    device_id: str,
    body: schemas.DevicePatchIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """临时停用/恢复 toggle + 永久注销（DEVICE_REGISTRY §5）。

    永久注销（retire=true）后禁止再把 device_active 置回 true（§5.2）。
    """
    assert_not_demo_teacher(teacher)
    device = _get_device_or_404(db, device_id)

    if body.retire:
        # 永久注销：retired_at=now + device_active=false（两字段同变，§5.2）
        if device.retired_at is None:
            device.retired_at = _now_utc()
        device.device_active = False
    elif body.device_active is not None:
        # 已永久注销的设备禁止再激活
        if device.retired_at is not None and body.device_active:
            raise HTTPException(
                409,
                {
                    "code": "DEVICE_RETIRED",
                    "message": "永久注销済みのデバイスは再有効化できません",
                },
            )
        device.device_active = body.device_active

    db.commit()
    db.refresh(device)
    return schemas.DeviceOut.model_validate(device)


@router.post(
    "/devices/{device_id}/reset-enroll", response_model=schemas.DeviceResetEnrollOut
)
def reset_device_enroll(
    device_id: str,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """重发激活码 + 作废旧公钥（Device_Contract §3）— 重新激活须先走本端点。"""
    assert_not_demo_teacher(teacher)
    device = _get_device_or_404(db, device_id)
    if device.retired_at is not None:
        raise HTTPException(
            409,
            {"code": "DEVICE_RETIRED", "message": "永久注销済みのデバイスです"},
        )
    enroll_code = device_auth.generate_enroll_code()
    device.enroll_code_hash = device_auth.hash_enroll_code(enroll_code)
    device.public_key = None  # 作废旧公钥
    device.enrolled_at = None
    db.commit()
    return schemas.DeviceResetEnrollOut(
        device_id=device.device_id, enroll_code=enroll_code
    )


# ===============================================================
# 2. 设备自助（无 token）
# ===============================================================
@router.post("/devices/{device_id}/enroll", response_model=schemas.DeviceEnrollOut)
def enroll_device(
    device_id: str,
    body: schemas.DeviceEnrollIn,
    db: Session = Depends(get_db),
):
    """设备首启激活（Device_Contract §2.2）— 激活码 + 公钥换「已激活」。"""
    device = _get_device_or_404(db, device_id)
    if device.retired_at is not None or not device.device_active:
        raise HTTPException(
            403, {"code": "DEVICE_NOT_ACTIVE", "message": "デバイスが停止中です"}
        )
    # 快速失败（已激活）— 真正防并发覆盖靠下方条件 UPDATE（审查 backend#31）。
    # 错误码保持原契约 422 INVALID_INPUT（点呼机客户端 + 测试依赖，#31 只闭合竞态不改契约）。
    if device.enrolled_at is not None:
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "既に有効化済みです（再有効化は管理者へ）",
            },
        )
    if not device_auth.verify_enroll_code(body.enroll_code, device.enroll_code_hash):
        raise HTTPException(
            422, {"code": "INVALID_INPUT", "message": "有効化コードが正しくありません"}
        )
    if not device_auth.is_valid_ed25519_pubkey(body.public_key):
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "公開鍵の形式が不正です（base64 32 バイト）",
            },
        )
    # 审查 backend#31：条件 UPDATE 原子占用（镜像 teachers 令牌占用 / rollcall start_session）
    # —— 只有 enrolled_at IS NULL 才写入公钥；并发两首启只有一个 rowcount=1，后到者 422（同预检契约）。
    enrolled_at = _now_utc()
    claimed = db.execute(
        update(models.RollCallDevice)
        .where(
            models.RollCallDevice.id == device.id,
            models.RollCallDevice.enrolled_at.is_(None),
        )
        .values(
            public_key=body.public_key,
            enrolled_at=enrolled_at,
            enroll_code_hash=None,  # 作废激活码
        )
    )
    if claimed.rowcount != 1:
        # 并发另一请求已抢先占用（rowcount=0）→ 与上方预检同契约 422 INVALID_INPUT
        db.rollback()
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "既に有効化済みです（再有効化は管理者へ）",
            },
        )
    db.commit()
    db.refresh(device)
    return schemas.DeviceEnrollOut(
        device_id=device.device_id, enrolled_at=device.enrolled_at
    )


def _cleanup_expired_nonces(db: Session) -> None:
    """顺手清理超 24h 的 nonce 占位行（best-effort，不阻塞主流程）。"""
    cutoff = _now_utc() - timedelta(hours=_NONCE_RETENTION_HOURS)
    db.query(models.DeviceAuthNonce).filter(
        models.DeviceAuthNonce.created_at < cutoff
    ).delete(synchronize_session=False)


@router.post("/devices/{device_id}/token", response_model=schemas.DeviceTokenOut)
def device_token(
    device_id: str,
    body: schemas.DeviceTokenIn,
    db: Session = Depends(get_db),
):
    """挑战签名换 12h 令牌（Device_Contract §2.3）。

    签名串 = "{device_id}\\n{ts}\\n{nonce}"（UTF-8 逐字拼接）。
    校验：设备存在且 active 且已 enroll → |server_now − ts| ≤ 600s → nonce 24h 未用 → 验签。
    失败码：UNKNOWN_DEVICE / DEVICE_NOT_ACTIVE / INVALID_SIGNATURE（reason 细分）。
    """
    device = _get_device_or_404(db, device_id)
    if device.retired_at is not None or not device.device_active:
        raise HTTPException(
            403, {"code": "DEVICE_NOT_ACTIVE", "message": "デバイスが停止中です"}
        )
    if not device.public_key or device.enrolled_at is None:
        raise HTTPException(
            403,
            {
                "code": "DEVICE_NOT_ACTIVE",
                "message": "デバイスが未有効化です",
                "reason": "not_enrolled",
            },
        )

    # 1. ts 时钟窗口校验（±600s）
    try:
        ts_dt = datetime.fromisoformat(body.ts)
    except ValueError:
        raise HTTPException(
            401,
            {
                "code": "INVALID_SIGNATURE",
                "message": "認証に失敗しました",
                "reason": "ts_malformed",
            },
        )
    if ts_dt.tzinfo is None:
        ts_dt = ts_dt.replace(tzinfo=timezone.utc)
    drift = abs((_now_utc() - ts_dt).total_seconds())
    if drift > _TS_TOLERANCE_SECONDS:
        raise HTTPException(
            401,
            {
                "code": "INVALID_SIGNATURE",
                "message": "認証に失敗しました",
                "reason": "ts_expired",
            },
        )

    # 2. 验签（用存的公钥；失败不细分原因）
    message = f"{device_id}\n{body.ts}\n{body.nonce}"
    if not device_auth.verify_ed25519(device.public_key, message, body.signature):
        raise HTTPException(
            401,
            {
                "code": "INVALID_SIGNATURE",
                "message": "認証に失敗しました",
                "reason": "bad_signature",
            },
        )

    # 3. nonce 防重放（24h 内单次）。落行占位；撞唯一约束 = 重放。
    _cleanup_expired_nonces(db)
    db.add(models.DeviceAuthNonce(device_id=device_id, nonce=body.nonce))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            401,
            {
                "code": "INVALID_SIGNATURE",
                "message": "認証に失敗しました",
                "reason": "nonce_replay",
            },
        )

    # enr claim = 本次激活的时刻戳。老师走 reset-enroll 重发激活码后 enrolled_at 被清空/刷新，
    # 旧令牌的 enr 对不上 → deps.get_current_device 判 401（契约 §2.2「旧公钥即刻作废」的
    # 安全意图要求旧设备身份同时失效，不能靠 12 小时自然过期）。
    token = create_access_token(
        device_id,
        "device",
        extra={"enr": device_enr_token_claim(device)},
        expire_minutes=_DEVICE_TOKEN_MINUTES,
    )
    expires_at = _now_jst() + timedelta(minutes=_DEVICE_TOKEN_MINUTES)
    return schemas.DeviceTokenOut(access_token=token, expires_at=expires_at)


# ===============================================================
# 3. 设备日常（device JWT）
# ===============================================================
def _audit_clock_skew(
    device: models.RollCallDevice, raw_swipe: datetime, server_now: datetime
) -> None:
    """设备 swipe_time 落在未来被钳制时留一条审计（Device_Contract §3）。

    走独立 session：这条留痕跟签到本身成不成功无关（签到后续可能抛 409 回滚），
    时钟异常这件事本身就该记下来。写失败只 warning，不影响签到主流程。

    **限流每台设备每分钟至多 1 条** —— 一台 NTP 坏掉的机器每次刷卡都会命中钳制，不限流
    就会把 `audit_logs` 灌满（真正要留的信息是「这台机器某段时间时钟不对」，不是每一次刷卡）。
    """
    db = SessionLocal()
    try:
        recent = db.scalar(
            select(models.AuditLog.id)
            .where(
                models.AuditLog.action == _CLOCK_SKEW_ACTION,
                models.AuditLog.target_id == device.id,
                models.AuditLog.created_at >= server_now - timedelta(minutes=1),
            )
            .limit(1)
        )
        if recent is not None:
            return
        db.add(
            models.AuditLog(
                # actor_type 受 ck_audit_actor_type 约束限定为 student/teacher/system，
                # 点呼机属系统组件 → system；具体是哪台机器看 target_id / payload。
                actor_type="system",
                actor_id=device.id,
                action=_CLOCK_SKEW_ACTION,
                target_type="rollcall_device",
                target_id=device.id,
                payload={
                    "device_id": device.device_id,
                    "raw_swipe_time": raw_swipe.isoformat(),
                    "server_now": server_now.isoformat(),
                    "skew_seconds": round((raw_swipe - server_now).total_seconds(), 3),
                },
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.warning(
            "[device] 时钟异常审计写入失败 device_id=%s",
            device.device_id,
            exc_info=True,
        )
    finally:
        db.close()


def _find_session_for_checkin(
    db: Session, student: models.Student, decision_time: datetime
) -> Optional[models.RollCallSession]:
    """定位该生该次签到应归属的场次 —— 一律按 decision_time（=swipe_time）落在哪个场次的
    时间窗内来判，不看「当下哪场在跑」。

    窗口 = [下限, 上限]：
    - 下限 = `scheduled_window_start_at`；老师若早于计划窗手动开场（异常但不该拒真实签到），
      取 `started_at` 作下限兜底。窗前刷卡不归任何场次 → SESSION_NOT_RUNNING（RollCall_Spec
      §7：present 要求 `scheduled_window_start_at ≤ t`）。
    - 上限 = running 场次无上限（还在接受签到）；ended 场次为 `ended_at`（7-17 拍板删
      late_end/TIMEOUT，结束后的签到一律 SESSION_NOT_RUNNING，见 RollCall_Spec §5.3 修订注）。

    为什么不能「有 running 就直接返回它」（2026-07-18 cursor 审查 blocker 1）：早间场次已
    auto_settle 置 absent、晚间场次已 running 时，队列里残留的早间刷卡会被记到晚间场次
    （早间 swipe_time 远早于晚间准时截止 → 误判 present），早间缺席与扣分永不回退。离线补传
    必须按 swipe_time 归属（Device_Contract §6）。

    审查 backend#33：时间窗条件下推到 SQL（等价于原 Python 的 lower/upper 判定），避免
    ended 行随运营天数全表加载。dorm_unit_set 是 JSON 列，跨库包含查询不可移植，故寮
    过滤仍在 Python 侧（与 rollcall.my_today_rollcall 同款）；候选集已被时间窗大幅收窄。
    """
    # SQL 等价条件（对照原 Python）：
    # - lower = min(scheduled_window_start_at, started_at or scheduled…)
    #   → decision_time >= lower ⇔ start_at≤t OR (started_at IS NOT NULL AND started_at≤t)
    # - ended 上限：decision_time ≤ ended_at（ended_at 非空）；running 无上限
    rows = db.scalars(
        select(models.RollCallSession).where(
            models.RollCallSession.session_status.in_(["running", "ended"]),
            or_(
                models.RollCallSession.scheduled_window_start_at <= decision_time,
                and_(
                    models.RollCallSession.started_at.is_not(None),
                    models.RollCallSession.started_at <= decision_time,
                ),
            ),
            or_(
                models.RollCallSession.session_status == "running",
                and_(
                    models.RollCallSession.session_status == "ended",
                    models.RollCallSession.ended_at.is_not(None),
                    models.RollCallSession.ended_at >= decision_time,
                ),
            ),
        )
    ).all()
    mine = [s for s in rows if student.dorm_unit in (s.dorm_unit_set or [])]
    if mine:
        # 理论上窗口不重叠；真重叠时取最晚开窗的那场（离 swipe_time 最近）
        # （原 covering 循环在 SQL 已等价过滤，此处 mine 即 covering）
        return max(mine, key=lambda s: _as_jst_aware(s.scheduled_window_start_at))
    return None


def _add_late_demerit(
    db: Session, student_id: UUID, session: models.RollCallSession, month: str
) -> None:
    """记一条迟到扣分（幂等 + SAVEPOINT 兜唯一约束 uq_demerit_source）。

    与老师代签 create_checkin / _apply_override_demerit 的迟到分口径一致（0.5 分，spec §862）。
    """
    # 审查 backend#30：写 DemeritEvent 前锁学生行（照抄 discipline.create_manual_demerit /
    # revoke_demerit）。SQLite no-op / PG 行锁；与「手动设定绝对分」互斥，防穿插打乱总分。
    # （device_checkin 外层已持同学生行锁；函数内再锁一次保证本函数单独被调时也遵守协议。）
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == student_id)
        .with_for_update()
    )
    existing = db.scalar(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.source_event_id == session.id,
            models.DemeritEvent.source_type == "rollcall_late",
            models.DemeritEvent.revoked_at.is_(None),
        )
    )
    if existing is not None:
        return  # 已有有效迟到扣分 → 幂等，不重复
    try:
        with db.begin_nested():
            db.add(
                models.DemeritEvent(
                    student_id=student_id,
                    source_type="rollcall_late",
                    source_event_id=session.id,
                    points=ROLLCALL_LATE_POINTS,
                    reason=f"点呼遅刻（{session.session_type}）NFC 自動",
                    month=month,
                    created_by_teacher_id=None,
                )
            )
    except IntegrityError:
        # 并发首签各插一条撞约束 → 忽略（已有一条有效迟到扣分即可）
        pass


def _revoke_settle_absent_demerit(
    db: Session, student_id: UUID, session: models.RollCallSession
) -> None:
    """离线补传覆盖 auto_settle absent → 撤销那条自动缺席扣分（回退结算扣分，Device_Contract §6）。"""
    # 审查 backend#30：撤扣分前锁学生行（照抄 discipline.revoke_demerit）
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == student_id)
        .with_for_update()
    )
    absent_dem = db.scalar(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.source_event_id == session.id,
            models.DemeritEvent.source_type == "rollcall_absent",
            models.DemeritEvent.revoked_at.is_(None),
        )
    )
    if absent_dem is not None:
        absent_dem.revoked_at = _now_utc()
        absent_dem.revoke_reason = "オフライン補送で出席確認、欠席判定取消"


def _checkin_response(
    student: models.Student,
    session_id: UUID,
    base_status: str,
    *,
    duplicate: bool,
    superseded_by_teacher: bool = False,
) -> schemas.DeviceCheckinOut:
    audio_file = f"{student.student_no}.wav"
    return schemas.DeviceCheckinOut(
        student_id=student.id,
        student_number=student.student_no,
        student_name=student.name,
        base_status=base_status,
        session_id=session_id,
        duplicate=duplicate,
        led="green",
        audio_file=audio_file,
        broadcast_text=student.name,
        superseded_by_teacher=superseded_by_teacher,
    )


@router.post("/rollcall/device-checkins", response_model=schemas.DeviceCheckinOut)
def device_checkin(
    body: schemas.DeviceCheckinIn,
    device: models.RollCallDevice = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """点呼机核心签到入口（Device_Contract §4.1 + §6）。"""
    # 0. 路径/字段一致性
    if body.path_type == "A" and not body.card_uid:
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "path_type=A には card_uid が必要です",
            },
        )
    if body.path_type == "B" and body.student_id is None:
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "path_type=B には student_id が必要です",
            },
        )
    # 路径 B 的 idempotency_key 来自手机写入邮箱的载荷（每次新 UUID，Device_Contract §7），
    # 缺它就没法靠 (session_id, idempotency_key) 唯一约束挡并发重复 → 必填（§4.1）。
    if body.path_type == "B" and body.idempotency_key is None:
        raise HTTPException(
            422,
            {
                "code": "INVALID_INPUT",
                "message": "path_type=B には idempotency_key が必要です",
            },
        )

    # 1. 解析学生
    card_uid_norm: Optional[str] = None
    if body.path_type == "A":
        card_uid_norm = (body.card_uid or "").lower()
        if not _CARD_UID_RE.match(card_uid_norm):
            raise HTTPException(
                422, {"code": "UNKNOWN_CARD", "message": "不明なカードです"}
            )
        active_card = db.scalar(
            select(models.NfcCard).where(
                models.NfcCard.card_uid == card_uid_norm,
                models.NfcCard.revoked_at.is_(None),
            )
        )
        if active_card is None:
            # 区分 UNKNOWN_CARD（UID 全无记录）vs UNREGISTERED_UID（有记录但已作废）
            any_card = db.scalar(
                select(models.NfcCard).where(models.NfcCard.card_uid == card_uid_norm)
            )
            if any_card is None:
                raise HTTPException(
                    422,
                    {"code": "UNKNOWN_CARD", "message": "登録されていないカードです"},
                )
            raise HTTPException(
                422, {"code": "UNREGISTERED_UID", "message": "無効化されたカードです"}
            )
        student = db.get(models.Student, active_card.student_id)
        if student is None or student.status != "active" or student.is_demo:
            raise HTTPException(
                422, {"code": "UNREGISTERED_UID", "message": "無効なカードです"}
            )
    else:  # path B
        student = db.get(models.Student, body.student_id)
        if student is None or student.status != "active" or student.is_demo:
            raise HTTPException(
                422, {"code": "UNREGISTERED_UID", "message": "無効な学生です"}
            )

    # 2. 判定时刻（swipe_time；未来超 30 秒钳制为 server_now，Device_Contract §3）
    now = _now_jst()
    swipe = _as_jst_aware(body.swipe_time)
    if swipe > now + timedelta(seconds=30):
        decision_time = now
        # 契约 §3 要求钳制时写审计（设备时钟异常要留痕，事后能查是哪台机器 NTP 坏了）
        _audit_clock_skew(device, swipe, now)
    else:
        decision_time = swipe

    # 3. 定位场次
    session = _find_session_for_checkin(db, student, decision_time)
    if session is None:
        raise HTTPException(
            409,
            {"code": "SESSION_NOT_RUNNING", "message": "点呼が開始されていません"},
        )

    # 审查 backend#4/#5 族（Q2）：读 events 前先锁该学生行，锁持有到 commit ——
    # 与 _settle_absent 的「学生行锁内重查」配对，闭合「设备签到读旧快照 vs end 结算」
    # 双向竞态：本请求先拿锁则结算重查看得见新签到；结算先拿锁则本请求等到 end 事务
    # 提交后才读 events，能看见 absent 行走 was_settled_absent 撤扣分。故意只锁学生行
    # 不锁 session 行（点呼高峰几十人连刷，锁 session 会全场串行化；设备路径永不
    # FOR UPDATE session 行，与 end/代签/改判的 session→student 锁序在显式锁层面不成环。
    # 严格说 PG 下仍有一条极窄隐式环：INSERT rollcall_events 会对被引用 session 行拿
    # FOR KEY SHARE，与代签持有的 session FOR UPDATE 冲突——同一学生同一瞬间「设备刷卡
    # × 老师代签」才可能互等，PG 死锁检测 ~1s 会砍掉一边报错，重试即恢复，可接受。
    # 这个锁同时覆盖下游 _add_late_demerit / _revoke_settle_absent_demerit 的
    # 扣分写入协议（逻-中-5）学生行锁要求。
    db.execute(
        select(models.Student.id)
        .where(models.Student.id == student.id)
        .with_for_update()
    )

    # 4. 幂等 + 离线补传冲突（Device_Contract §4.1 步骤 3 / §6）
    events = db.scalars(
        select(models.RollCallEvent).where(
            models.RollCallEvent.session_id == session.id,
            models.RollCallEvent.student_id == student.id,
        )
    ).all()
    key_str = str(body.idempotency_key) if body.idempotency_key is not None else None

    if key_str is not None:
        for e in events:
            if e.idempotency_key == key_str:
                return _checkin_response(
                    student, session.id, e.base_status, duplicate=True
                )

    def _latest(evs):
        return max(evs, key=lambda e: (_as_jst_aware(e.checked_in_at), e.id))

    override_events = [e for e in events if e.status_source == "teacher_override"]
    if override_events:
        # 老师改判优先：设备丢弃补传，绿灯不重播（§6）
        return _checkin_response(
            student,
            session.id,
            _latest(override_events).base_status,
            duplicate=True,
            superseded_by_teacher=True,
        )

    latest = _latest(events) if events else None
    if latest is not None and latest.base_status == "exempt_range":
        # 免点呼学生（外泊等）已被结算/预标 → 无需签到
        return _checkin_response(student, session.id, "exempt_range", duplicate=True)

    positive = [
        e
        for e in events
        if e.status_source in ("auto_nfc", "manual_checkin")
        and e.base_status in ("present", "late")
    ]
    if positive:
        # 已有真实签到 → 重复（不重复播报、绿灯即可）
        return _checkin_response(
            student, session.id, _latest(positive).base_status, duplicate=True
        )

    was_settled_absent = any(
        e.status_source == "auto_settle" and e.base_status == "absent" for e in events
    )

    # 5. 时间窗判定（present / late — 7-17 拍板「迟到无截止」：准时截止后到场次结束前一律
    #    late；scheduled_late_end_at 列保留但判定不读。结束后的补传已在定位场次时按 ended_at
    #    截断 → SESSION_NOT_RUNNING（RollCall_Spec §5.3/§7 修订 + Device_Contract §4.1/§6）
    on_time_end = _as_jst_aware(session.scheduled_on_time_end_at)
    base_status = "present" if decision_time <= on_time_end else "late"

    # 6. 追加签到事件（append-only；checked_in_at=server_now 保证补传行是最新、覆盖旧 absent）
    event = models.RollCallEvent(
        session_id=session.id,
        student_id=student.id,
        device_id=device.id,
        path_type=body.path_type,
        base_status=base_status,
        status_source="auto_nfc",
        checked_in_at=now,
        idempotency_key=key_str,
        card_uid=card_uid_norm,
    )
    db.add(event)

    # 7. 扣分联动
    month = _as_jst_aware(session.scheduled_window_start_at).strftime("%Y-%m")
    if was_settled_absent:
        # 离线补传覆盖结算：撤销自动缺席扣分 + 按补传状态重记（§6）
        _revoke_settle_absent_demerit(db, student.id, session)
    if base_status == "late":
        _add_late_demerit(db, student.id, session, month)

    try:
        db.commit()
    except IntegrityError:
        # 并发同 idempotency_key / 同生同场撞唯一约束 → 回滚重查、幂等返回
        db.rollback()
        if key_str is not None:
            existing = db.scalar(
                select(models.RollCallEvent).where(
                    models.RollCallEvent.session_id == session.id,
                    models.RollCallEvent.idempotency_key == key_str,
                )
            )
            if existing is not None:
                return _checkin_response(
                    student, session.id, existing.base_status, duplicate=True
                )
        # 审查 backend#4：路径 A 无 idempotency_key（恒 NULL），并发双刷撞的是
        # uq_rce_real_checkin 部分唯一索引 —— 按 session+student+真实签到 source
        # 重查已存事件，按契约 §4.1 返回 duplicate=true（对齐 rollcall.py 同款兜底），
        # 不再把并发第二刷炸成 500。
        existing = db.scalar(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id == session.id,
                models.RollCallEvent.student_id == student.id,
                models.RollCallEvent.status_source.in_(["auto_nfc", "manual_checkin"]),
            )
        )
        if existing is not None:
            return _checkin_response(
                student, session.id, existing.base_status, duplicate=True
            )
        raise
    db.refresh(event)

    # 8. WS 推老师端（设备签到只涉及真实学生 → is_demo=False）
    _ws.manager.broadcast_sync(
        {
            "type": "checkin",
            "session_id": str(session.id),
            "student_id": str(student.id),
            "status": base_status,
            "checked_at": now.isoformat(),
            "name": student.name,
            "room_no": student.room_no,
        },
        dorm_unit=student.dorm_unit,
        student_is_demo=student.is_demo,
    )

    return _checkin_response(student, session.id, base_status, duplicate=False)


@router.post("/devices/me/heartbeat")
def device_heartbeat(
    body: schemas.DeviceHeartbeatIn,
    device: models.RollCallDevice = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """WS 不可用时的兜底心跳（Device_Contract §4.4）→ 更新 last_seen_at。"""
    device.last_seen_at = _now_utc()
    if body.fw_version:
        device.fw_version = body.fw_version[:32]
    db.commit()
    return {"last_seen_at": _now_jst().isoformat()}


@router.get("/devices/me/roster", response_model=schemas.DeviceRosterOut)
def device_roster(
    device: models.RollCallDevice = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """离线兜底名单（Device_Contract §4.2）— active 非演示学生 + 各自 active card_uids。

    设备不 dorm-bound（附录 C.1），返回全体在寮非演示学生。
    """
    students = db.scalars(
        select(models.Student).where(
            models.Student.status == "active",
            models.Student.is_demo.is_(False),
        )
    ).all()
    student_ids = [s.id for s in students]
    cards_by_student: dict[UUID, list[str]] = {}
    if student_ids:
        cards = db.scalars(
            select(models.NfcCard).where(
                models.NfcCard.student_id.in_(student_ids),
                models.NfcCard.revoked_at.is_(None),
            )
        ).all()
        for c in cards:
            cards_by_student.setdefault(c.student_id, []).append(c.card_uid)
    return schemas.DeviceRosterOut(
        generated_at=_now_jst(),
        students=[
            schemas.DeviceRosterStudentOut(
                student_id=s.id,
                student_number=s.student_no,
                name=s.name,
                card_uids=cards_by_student.get(s.id, []),
            )
            for s in students
        ],
    )


def _audio_dir() -> Path:
    return Path(get_settings().rollcall_audio_dir)


@router.get("/devices/me/audio-manifest", response_model=schemas.DeviceAudioManifestOut)
def device_audio_manifest(
    device: models.RollCallDevice = Depends(get_current_device),
):
    """音频清单（Device_Contract §4.3）— 目录不存在返回空 manifest。"""
    audio_dir = _audio_dir()
    if not audio_dir.is_dir():
        return schemas.DeviceAudioManifestOut(files=[])
    files: list[schemas.DeviceAudioFileOut] = []
    for entry in sorted(os.listdir(audio_dir)):
        if not _AUDIO_NAME_RE.match(entry):
            continue
        fpath = audio_dir / entry
        if not fpath.is_file():
            continue
        st = fpath.stat()
        cache_key = (str(fpath.resolve()), st.st_mtime_ns, st.st_size)
        digest = _audio_sha256_cache.get(cache_key)
        if digest is None:
            digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
            _audio_sha256_cache[cache_key] = digest
        files.append(
            schemas.DeviceAudioFileOut(
                name=entry,
                sha256=digest,
                size=st.st_size,
            )
        )
    return schemas.DeviceAudioManifestOut(files=files)


@router.get("/devices/me/audio/{file}")
def device_audio_file(
    file: str,
    device: models.RollCallDevice = Depends(get_current_device),
):
    """取单个音频原文件（Device_Contract §4.3）— 文件名白名单防路径穿越。"""
    if not _AUDIO_NAME_RE.match(file):
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "音声ファイルが見つかりません"}
        )
    audio_dir = _audio_dir()
    fpath = (audio_dir / file).resolve()
    # 双保险：解析后必须仍在音频目录下（防 symlink / 编码穿越）
    try:
        fpath.relative_to(audio_dir.resolve())
    except ValueError:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "音声ファイルが見つかりません"}
        )
    if not fpath.is_file():
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "音声ファイルが見つかりません"}
        )
    return Response(content=fpath.read_bytes(), media_type="audio/wav")


# ===============================================================
# 4. 卡绑定（老师 C_ROLLCALL）
# ===============================================================
@router.post("/cards", response_model=schemas.NfcCardOut, status_code=201)
def create_card(
    body: schemas.NfcCardCreateIn,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """绑卡（Device_Contract §5）— card_uid 14 位小写 hex；同 UID 只能绑一个未作废学生。"""
    card_uid = body.card_uid.lower()
    if not _CARD_UID_RE.match(card_uid):
        raise HTTPException(
            422,
            {"code": "INVALID_INPUT", "message": "card_uid は 14 桁の小文字 hex です"},
        )
    student = db.get(models.Student, body.student_id)
    if student is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "学生が見つかりません"}
        )
    # 寮边界 + 演示隔离（真老师绑真实学生 / 演示老师绑演示学生）
    _assert_student_in_dorm(teacher, student)
    assert_student_demo_match(teacher, student)

    active = db.scalar(
        select(models.NfcCard).where(
            models.NfcCard.card_uid == card_uid,
            models.NfcCard.revoked_at.is_(None),
        )
    )
    if active is not None:
        raise HTTPException(
            409,
            {
                "code": "CARD_ALREADY_BOUND",
                "message": "このカードは既に有効な学生に紐付いています",
            },
        )
    card = models.NfcCard(
        card_uid=card_uid,
        student_id=student.id,
        card_active=True,
        issued_by=teacher.id,
    )
    db.add(card)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            {
                "code": "CARD_ALREADY_BOUND",
                "message": "このカードは既に有効な学生に紐付いています",
            },
        )
    db.refresh(card)
    return schemas.NfcCardOut.model_validate(card)


@router.delete("/cards/{card_uid}", response_model=schemas.NfcCardOut)
def revoke_card(
    card_uid: str,
    body: Optional[schemas.NfcCardRevokeIn] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.MANAGE)
    ),
):
    """作废卡（软删，Device_Contract §5）— 作废后同 UID 可重新绑给新学生。"""
    card_uid = card_uid.lower()
    card = db.scalar(
        select(models.NfcCard).where(
            models.NfcCard.card_uid == card_uid,
            models.NfcCard.revoked_at.is_(None),
        )
    )
    if card is None:
        raise HTTPException(
            404, {"code": "NOT_FOUND", "message": "有効なカードが見つかりません"}
        )
    student = db.get(models.Student, card.student_id)
    if student is not None:
        _assert_student_in_dorm(teacher, student)
        assert_student_demo_match(teacher, student)
    card.card_active = False
    card.revoked_at = _now_utc()
    card.revoked_by = teacher.id
    if body is not None and body.revoke_reason:
        card.revoke_reason = body.revoke_reason
    db.commit()
    db.refresh(card)
    return schemas.NfcCardOut.model_validate(card)


@router.get("/cards", response_model=list[schemas.NfcCardOut])
def list_cards(
    student_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_ROLLCALL, permissions.VIEW)
    ),
):
    """卡一览（Device_Contract §5）— 可按 student_id 过滤；R4 寮 + 演示隔离。"""
    # 先算出老师可见的学生集合（寮 + demo），再据此过滤卡
    dorm_units = dorm_units_for_teacher(teacher)
    student_q = select(models.Student.id).where(demo_scope_for_teacher(teacher))
    if dorm_units is not None:
        student_q = student_q.where(models.Student.dorm_unit.in_(dorm_units))
    if student_id is not None:
        student_q = student_q.where(models.Student.id == student_id)
    allowed_ids = set(db.scalars(student_q).all())
    if not allowed_ids:
        return []
    rows = db.scalars(
        select(models.NfcCard)
        .where(models.NfcCard.student_id.in_(allowed_ids))
        .order_by(models.NfcCard.issued_at.desc())
    ).all()
    return [schemas.NfcCardOut.model_validate(c) for c in rows]
