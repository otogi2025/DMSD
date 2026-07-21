"""ログイン (学生 / 教师) — JWT 発行。

P0 範囲では POST /applications / GET /applications/:id 等が
認証付き endpoint なので、最低限のログインを提供する。

2026-05-21 加：教师 login 失败计数 + 锁定（A-006）
    - 教师端权限高（改判 / 发邀请码 / 解 NFC 绑定），蛮力破解危害大
    - 3 次失败 → 锁 30 分钟（学生端阈值待主会话拍板 A-005）
    - 用 teachers.failed_count + teachers.locked_until 字段（已存在）

2026-05-30 加：
    - DELETE /sessions/current — B1 无状态登出（JWT 客户端丢弃即可）
    - 学生 login 失败计数 + 锁定 — B6（照抄教师逻辑，用 accounts 表字段）
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import get_settings
from ..database import get_db
from ..deps import get_current_principal  # B1 登出端点用（老师 + 学生都能调）
from ..ratelimit import limiter

router = APIRouter(prefix="/api/v1/sessions", tags=["auth"])

# 限速器单例见 ..ratelimit（已在 import 区导入，与全后端共用计数）

# 教师 login 锁定阈值（A-006）
TEACHER_LOCK_THRESHOLD = 3  # 3 次失败立锁
TEACHER_LOCK_DURATION_MIN = 30  # 锁 30 分钟

# B6：学生 login 锁定阈值（学生独立阈值：5 次失败锁 15 分；教师是 3 次 / 30 分，两端不一致）
STUDENT_LOCK_THRESHOLD = 5
STUDENT_LOCK_DURATION_MIN = 15

# auth-account-09：时序侧信道加固。
# 账号（学号/教师）不存在时，原本会短路跳过 bcrypt 校验导致响应明显更快，
# 可被用来枚举哪些账号已注册。这里预算一个固定 dummy hash，账号缺失时也
# 跑一次 verify_password，让 bcrypt 耗时在「存在」与「不存在」两种情况下一致。
# 模块加载时算一次，不影响每次请求性能。
_DUMMY_PASSWORD_HASH = security.hash_password("dummy-password-for-timing-equalization")


@router.post("/student", response_model=schemas.TokenOut)
@limiter.limit(
    # 学生登录爆破防护
    # 20次/分钟/IP — 正常登录极少超过 2-3 次，20 次留有余量但足以阻断爆破
    "20/minute"
)
def login_student(
    request: Request,
    body: schemas.StudentLoginIn,
    db: Session = Depends(get_db),
):
    # 学号 / 邮箱二选一找学生。只改「怎么找到 student」这一段；
    # 下面锁定 / 时序等化 / 原子自增 / 统一 401 一律原样保留。
    student = None
    if body.student_no:
        grade, klass, seat = (
            body.student_no[:2],
            body.student_no[2:4],
            body.student_no[4:6],
        )
        student = db.scalars(
            select(models.Student).where(
                models.Student.grade_code == grade,
                models.Student.class_code == klass,
                models.Student.seat_no == seat,
            )
        ).first()
    else:
        # 邮箱路径：大小写不敏感（注册查重同口径）。
        # 历史数据可能存在大小写变体重复（Student.email 无 DB 唯一约束）——
        # 命中多于 1 条时不要随便挑一条（会登错人），当作认证失败走下面 401
        # （仍跑 bcrypt 时序等化，防「多条命中」本身变成可观测差异）。
        email_key = body.email.strip().lower()
        matches = db.scalars(
            select(models.Student).where(func.lower(models.Student.email) == email_key)
        ).all()
        if len(matches) == 1:
            student = matches[0]
        # len != 1 → student 保持 None，与「邮箱不存在」同一条 401 路径

    # 先取 account（后面锁定逻辑需要），找不到学生也走到 401
    account = None
    if student:
        account = db.scalars(
            select(models.Account).where(models.Account.student_id == student.id)
        ).first()

    now = datetime.now(timezone.utc)

    # locked_until 经 TZDateTime 读出是带时区的（JST）。统一补/转成 aware 再比「绝对时刻」，
    # 不能剥时区按墙钟比 —— 旧写法剥时区比 naive，TZDateTime 改造后会把 JST 墙钟当 UTC，
    # 15 分钟的锁会被误判成约 9 小时 15 分（codex 审查 major #1）。与老师登录段口径一致。
    def _is_locked(dt) -> bool:
        if dt is None:
            return False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt > now

    def _remaining_min(dt) -> int:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int((dt - now).total_seconds() / 60) + 1

    # B6：检查账号是否被锁
    if account and _is_locked(account.locked_until):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "ACCOUNT_LOCKED",
                "message": f"アカウントロック中（残り約 {_remaining_min(account.locked_until)} 分）",
            },
        )

    # E-低-09：锁定期满后清失败计数（防可用性 DoS）。
    # 原本只有登录成功才清 failed_count；锁满后计数仍停在阈值（5），
    # 攻击者只要再错 1 次就立刻把账号重新锁死，可长期拒绝服务。
    # 这里在「曾经设过锁、现在已过期」时把计数与锁一起清零 = 滑动窗口起点重置，
    # 让锁满后的失败重新从 0 计起。is_locked 已在上面拦截，能走到这里说明锁已过期。
    if account and account.locked_until is not None:
        account.failed_count = 0
        account.locked_until = None
        db.commit()

    # 密码校验失败 → 失败计数 + 触发锁
    # auth-account-09：无论账号是否存在都跑一次 bcrypt，等化响应耗时，防账号枚举。
    password_hash = account.password_hash if account else _DUMMY_PASSWORD_HASH
    password_ok = security.verify_password(body.password, password_hash)
    if not student or not account or not password_ok:
        if account:
            # F-低-11：原子自增，避免并发失败请求各自读到旧值再 +1 导致丢更新。
            # 直接发 UPDATE ... SET failed_count = failed_count + 1（数据库侧加值），
            # 再 refresh 读回最新值判断是否达阈值。dev SQLite 串行掩盖了竞态，
            # production PostgreSQL 下并发明显，故用 DB 端原子写。
            db.execute(
                update(models.Account)
                .where(models.Account.id == account.id)
                .values(failed_count=models.Account.failed_count + 1)
            )
            db.refresh(account)
            if account.failed_count >= STUDENT_LOCK_THRESHOLD:
                # 写带时区的世界时 —— TZDateTime 写入侧统一转 UTC 存（与老师登录段口径一致）
                account.locked_until = now + timedelta(
                    minutes=STUDENT_LOCK_DURATION_MIN
                )
                account.lock_level = (account.lock_level or 0) + 1
            db.commit()
        # 只按登录方式分文案（学号登录 vs 邮箱登录），不按「哪个字段错」分——防账号枚举侧信道。
        # 学号显示词统一用「アカウント番号」（6-16 拍板，iOS AuthStubs / Android LoginScreen 已用同款），
        # backend 这条原写「学籍番号」是拍板前旧词，与两端对齐改过来。
        if body.student_no:
            fail_message = "アカウント番号またはパスワードが正しくありません"
        else:
            fail_message = "メールアドレスまたはパスワードが正しくありません"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": fail_message},
        )

    if student.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント停止中"},
        )

    settings = get_settings()
    token = security.create_access_token(
        student.id,
        "student",
        extra={
            "dorm_unit": student.dorm_unit,
            "is_overseas": student.is_overseas,
            "name": student.name,
        },
    )
    # 登录成功 → 清失败计数 + 清锁
    account.last_login_at = now
    account.failed_count = 0
    account.lock_level = 0
    account.locked_until = None
    db.commit()
    return schemas.TokenOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
    )


@router.post("/teacher", response_model=schemas.TeacherTokenOut)
@limiter.limit(
    # 老师登录爆破防护
    # 老师权限比学生高（改判/发注册码/解NFC绑定），用更严格的限制
    # 10次/分钟/IP — 比学生端收紧一倍，配合已有的 3 次失败锁定（A-006）形成双重防护
    "10/minute"
)
def login_teacher(
    request: Request,
    body: schemas.TeacherLoginIn,
    db: Session = Depends(get_db),
):
    # 5-27 拍板：支持 teacher_id (UUID) 或 login_id，至少一个
    if not body.teacher_id and not body.login_id:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "MISSING_IDENTIFIER",
                "message": "teacher_id or login_id is required",
            },
        )
    if body.teacher_id:
        teacher = db.get(models.Teacher, body.teacher_id)
    else:
        teacher = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == body.login_id)
        ).first()

    now = datetime.now(timezone.utc)

    # A-006: 检查教师是否被锁
    if teacher and teacher.locked_until and teacher.locked_until > now:
        remaining = int((teacher.locked_until - now).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "ACCOUNT_LOCKED",
                "message": f"アカウントロック中（残り約 {remaining} 分）",
            },
        )

    # E-低-09：锁定期满后清失败计数（防可用性 DoS）。
    # 与学生段同理：原本锁满后 failed_count 仍停在阈值（3），攻击者再错 1 次即重新锁死。
    # 在「曾经设过锁、现在已过期」时把计数与锁一起清零 = 滑动窗口起点重置。
    # 上面已拦截仍在锁定中的情况，能走到这里说明锁已过期。
    if teacher and teacher.locked_until is not None:
        teacher.failed_count = 0
        teacher.locked_until = None
        db.commit()

    # 密码校验失败 → 失败计数 + 触发锁
    # auth-account-09：无论账号是否存在都跑一次 bcrypt，等化响应耗时，防账号枚举。
    password_hash = teacher.password_hash if teacher else _DUMMY_PASSWORD_HASH
    password_ok = security.verify_password(body.password, password_hash)
    if not teacher or not password_ok:
        if teacher:
            # F-低-11：原子自增，避免并发失败请求丢更新（详见学生段同名注释）。
            db.execute(
                update(models.Teacher)
                .where(models.Teacher.id == teacher.id)
                .values(failed_count=models.Teacher.failed_count + 1)
            )
            db.refresh(teacher)
            if teacher.failed_count >= TEACHER_LOCK_THRESHOLD:
                teacher.locked_until = now + timedelta(
                    minutes=TEACHER_LOCK_DURATION_MIN
                )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "IDまたはパスワードが正しくありません",
            },
        )
    if teacher.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウント停止中"},
        )
    # 临时账户到期检查 — 过期则拒绝登录（永久账户 expires_at=NULL 不受影响）
    if teacher.expires_at is not None and teacher.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_EXPIRED",
                "message": "臨時アカウントの有効期限が切れています",
            },
        )

    settings = get_settings()
    token = security.create_access_token(
        teacher.id,
        f"teacher:{teacher.role}",
        extra={
            "name": teacher.name,
            "teacher_role": teacher.role,
            "assigned_dorm": teacher.assigned_dorm,
            # 登录时选的寮（1=男/4=女）写进令牌，驱动寮过滤；未选则不放（看全部，向后兼容）
            **(
                {"selected_dorm": body.selected_dorm}
                if body.selected_dorm is not None
                else {}
            ),
        },
    )
    # 登录成功 → 清失败计数 + 清锁
    teacher.last_login_at = now
    teacher.failed_count = 0
    teacher.locked_until = None
    db.commit()
    return schemas.TeacherTokenOut(
        access_token=token,
        expires_in=settings.jwt_access_expire_min * 60,
        teacher=schemas.TeacherOut.model_validate(teacher),
    )


@router.delete("/current", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    _principal: models.Student | models.Teacher = Depends(get_current_principal),
):
    """B1 — 登出（学生 + 老师都可调）。

    系统用无状态 JWT，服务端不存 token。
    客户端收到 204 后把本地 token 丢弃即可完成登出。

    真正的服务端吊销（防 token 被盗后仍可用）需 v1.1 加 jti 黑名单表，
    本版本不实现，符合 v1.0 安全基线。
    """
    return  # 204 No Content
