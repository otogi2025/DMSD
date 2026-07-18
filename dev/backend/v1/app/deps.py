"""FastAPI 依存注入 (ヘッダ → 認証ユーザー解決)。

`Authorization: Bearer <jwt>` を解いて、現在ログインしているのが
- 学生 (sub = students.id)
- 教師 (sub = teachers.id)
を Student / Teacher ORM オブジェクトで返す。

R4 寮過滤 helper — `dorm_units_for_teacher(teacher)` 是全 router 共用的过滤工具。
"""

from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, permissions, security
from .database import get_db

# R4 — 跨寮角色能看全件
CROSS_DORM_ROLES = frozenset(
    {"校長", "寮務部長", "寮務課長", "国際交流部長", "国際交流課長"}
)


def is_teacher_expired(teacher: models.Teacher) -> bool:
    """临时账户是否已过期（永久账户 expires_at=NULL → 永不过期）。

    给所有「自己解 JWT、不走 get_current_teacher」的鉴权入口（ws / applications._resolve_actor /
    announcements._resolve_actor）共用，避免过期临时账户拿没过期的令牌从这些旁路绕过。
    """
    return teacher.expires_at is not None and teacher.expires_at <= datetime.now(
        timezone.utc
    )


def dorm_units_for_teacher(teacher: models.Teacher) -> Optional[list[int]]:
    """寮过滤 — 返回该教师能看到的 dorm_unit 列表（None = 不限制 / 看全部）。

    2026-06-18 itsuki 拍板**按登录时选的寮过滤**（取代 6-13 全局取消）：老师登录时选
    今晚负责男子寮还是女子寮，这个选择写进令牌（claim `selected_dorm`），由
    get_current_teacher / get_current_principal 挂到 teacher._selected_dorm 上，本函数据此过滤：

    - op / 申請承認専用 组 → 永远看全部 `[1, 2, 4]`（承認组默认看所有男女生 + 所有申请）。
    - 其他组按选的寮：选男（selected_dorm=1）→ `[1, 2]`；选女（=4）→ `[4]`。
    - **未选**（旧令牌 / 非登录页客户端 / 测试夹具不带 selected_dorm）→ 不限制 `[1, 2, 4]`，
      向后兼容（保持 6-13「看全部」行为，重新登录选寮后才生效过滤）。

    返回全集而非 None：有些调用点直接 `.in_(allowed)` 没有 `if allowed is not None`
    守卫，返回 None 会让 SQL 的 `.in_(None)` 报错；返回全集则无论有无守卫都匹配到全部。
    """
    group = permissions.effective_group(teacher)
    # op / 申請承認専用：永远看全部，忽略选寮
    if group in (permissions.GROUP_OP, permissions.GROUP_APPROVAL):
        return [1, 2, 4]
    selected = getattr(teacher, "_selected_dorm", None)
    if selected == 4:
        return [4]  # 女子寮
    if selected in (1, 2):
        return [1, 2]  # 男子寮（1+2 寮）
    return [1, 2, 4]  # 未选 → 不限制（向后兼容）


def demo_scope_for_teacher(teacher: models.Teacher):
    """演示隔离过滤条件 — 返回作用在 Student.is_demo 上的 SQLAlchemy 条件。

    与 R4 寮过滤（dorm_units_for_teacher）正交，叠加用：
    - 真老师（is_demo=False）→ Student.is_demo IS False（只看真实学生，行为同改造前）
    - 演示老师（is_demo=True）→ Student.is_demo IS True（只看演示学生）

    用法（替换散落各 router 的硬编码 .where(Student.is_demo.is_(False))）：
        stmt = stmt.where(demo_scope_for_teacher(teacher))

    注：改造前各处硬编码 .is_(False) 等价于「真老师」分支，故真老师查询结果不变；
    本函数只多开了「演示老师只看演示学生」这条反向通路。
    """
    return models.Student.is_demo.is_(teacher.is_demo)


def assert_student_demo_match(teacher: models.Teacher, student: models.Student) -> None:
    """演示写隔离 — 演示老师只能操作演示学生、真老师只能操作真实学生，否则当作不存在 404。

    用于按 student_id / application_id 写单个学生数据的端点（checkin / 审批 / 扣分 等），
    防演示老师构造真实 student_id 越权写真实数据（反之真老师写演示学生）。真老师行为同改造前。
    """
    if student.is_demo != teacher.is_demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": "学生が見つかりません"},
        )


def assert_not_demo_teacher(teacher: models.Teacher) -> None:
    """演示老师禁止账号 / 全局管理操作（创建/邀请/删除老师、刷新/关闭学生注册码等）→ 403。

    演示账号只能在演示数据范围内只读/操作演示数据，不能制造真实账号、不能影响全局配置 ——
    否则演示老师可造一个 is_demo=False 的真实老师账号、用它登录绕过整个演示隔离（隔离根基漏洞）。
    """
    if teacher.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DEMO_FORBIDDEN",
                "message": "デモアカウントはこの操作を実行できません",
            },
        )


def _parse_bearer(auth_header: str | None) -> str:
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "ログインが必要です"},
        )
    return auth_header.split(" ", 1)[1]


def get_current_student(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> models.Student:
    token = _parse_bearer(authorization)
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    if payload.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "学生 token が必要です"},
        )
    # sub 缺失 / 非法 UUID 不能抛未捕获异常变成 500 — 仿 get_current_principal 统一返回 401
    try:
        student_uuid = UUID(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    student = db.get(models.Student, student_uuid)
    if not student or student.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウントが利用不可です"},
        )
    return student


def get_current_teacher(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> models.Teacher:
    token = _parse_bearer(authorization)
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    role = payload.get("role", "")
    if not role.startswith("teacher:"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "教師 token が必要です"},
        )
    # sub 缺失 / 非法 UUID 不能抛未捕获异常变成 500 — 仿 get_current_principal 统一返回 401
    try:
        teacher_uuid = UUID(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    teacher = db.get(models.Teacher, teacher_uuid)
    if not teacher or teacher.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "アカウントが利用不可です"},
        )
    # 临时账户到期：已签发令牌也要拦（防令牌活过账户，24h 令牌 vs「今天内」到期）
    if is_teacher_expired(teacher):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_EXPIRED",
                "message": "臨時アカウントの有効期限が切れています",
            },
        )
    # 把登录时选的寮（令牌 claim）挂到 teacher 上，供 dorm_units_for_teacher 读
    teacher._selected_dorm = payload.get("selected_dorm")
    return teacher


def get_current_principal(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> models.Student | models.Teacher:
    """学生 token 或老师 token 任一都接受。FC-027 公告 list / detail 用 —
    老师也要看公告（决定要不要发新的）+ 学生看自己 scope 内公告。
    返回 Student 或 Teacher ORM 对象，调用方用 isinstance 区分。
    """
    token = _parse_bearer(authorization)
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    role = payload.get("role", "")
    sub = payload.get("sub")
    # sub 缺失 / 非法 UUID 不能抛未捕获异常变成 500 — 统一解析后返回 401
    try:
        actor_uuid = UUID(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    if role == "student":
        student = db.get(models.Student, actor_uuid)
        if not student or student.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "アカウントが利用不可です",
                },
            )
        return student
    if role.startswith("teacher:"):
        teacher = db.get(models.Teacher, actor_uuid)
        if not teacher or teacher.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "アカウントが利用不可です",
                },
            )
        if is_teacher_expired(teacher):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_EXPIRED",
                    "message": "臨時アカウントの有効期限が切れています",
                },
            )
        # 同 get_current_teacher：挂登录时选的寮供 dorm_units_for_teacher 读
        teacher._selected_dorm = payload.get("selected_dorm")
        return teacher
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": "FORBIDDEN", "message": "不明な token role"},
    )


def get_current_device(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> models.RollCallDevice:
    """设备主体鉴权（Device_Contract §2.4）— 仿 get_current_teacher。

    JWT role="device"、sub=device_id（短码，不是本表 UUID 主键）。日常设备端点用它取当前设备。
    - role 非 device → 403（老师 / 学生令牌不能调设备专属端点）。
    - 设备不存在 → 401（UNKNOWN_DEVICE 归到「令牌无效」类，设备侧重新走 enroll/token）。
    - 停用（device_active=false）或已永久注销（retired_at 非 NULL）→ 403 DEVICE_NOT_ACTIVE。
    """
    token = _parse_bearer(authorization)
    try:
        payload = security.decode_token(token)
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "トークンが無効です"},
        )
    if payload.get("role") != "device":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "デバイス token が必要です"},
        )
    device_id = payload.get("sub")
    device = db.scalar(
        select(models.RollCallDevice).where(
            models.RollCallDevice.device_id == device_id
        )
    )
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNKNOWN_DEVICE", "message": "未登録のデバイスです"},
        )
    if not device.device_active or device.retired_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "DEVICE_NOT_ACTIVE", "message": "デバイスが停止中です"},
        )
    # 令牌世代校验：签发时把当次 enrolled_at 秒数写进 enr claim。老师走 reset-enroll 作废旧
    # 公钥后 enrolled_at 被清空（再次 enroll 则刷新）→ 旧令牌 enr 对不上，当场失效，不等
    # 12 小时自然过期（Device_Contract §2.2「旧公钥即刻作废」，2026-07-18 cursor 审查 major 7）。
    enrolled_at = device.enrolled_at
    token_enr = payload.get("enr")
    current_enr = int(enrolled_at.timestamp()) if enrolled_at is not None else None
    if current_enr is None or token_enr != current_enr:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "トークンが無効です（再有効化が必要です）",
            },
        )
    return device


def require_permission(cluster: str, level: int):
    """权限分级闸（teacher_permission_v1.md §5）— 替代裸 get_current_teacher 与旧的按职位鉴权。

    用法：`Depends(require_permission(permissions.C_ROLLCALL, permissions.MANAGE))`
    —— 管理动作传 MANAGE，查看动作传 VIEW。

    按当前老师的有效权限组（permissions.effective_group）查 §5 矩阵：
    - 级别达标 → 放行，返回 Teacher（端点 body 照常拿到老师对象）。
    - 级别不足 → 403，detail.code = "FORBIDDEN_ROLE"（沿用旧闸的错误码，前端无需改）。

    注：寮过滤（dorm_units_for_teacher）与本闸正交叠加 —— 本闸只判「能不能用这个功能」，
    寮过滤在端点 body 内判「能看到哪些寮的学生」。
    """

    def _checker(
        teacher: models.Teacher = Depends(get_current_teacher),
    ) -> models.Teacher:
        group = permissions.effective_group(teacher)
        if not permissions.has_permission(group, cluster, level):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": (
                        f"権限不足（{cluster} には {permissions.level_name(level)} "
                        "権限が必要です）"
                    ),
                },
            )
        return teacher

    return _checker
