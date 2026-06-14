"""FastAPI 依存注入 (ヘッダ → 認証ユーザー解決)。

`Authorization: Bearer <jwt>` を解いて、現在ログインしているのが
- 学生 (sub = students.id)
- 教師 (sub = teachers.id)
を Student / Teacher ORM オブジェクトで返す。

R4 寮過滤 helper — `dorm_units_for_teacher(teacher)` 是全 router 共用的过滤工具。
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from . import models, permissions, security
from .database import get_db

# R4 — 跨寮角色能看全件
CROSS_DORM_ROLES = frozenset(
    {"校長", "寮務部長", "寮務課長", "国際交流部長", "国際交流課長"}
)


def dorm_units_for_teacher(teacher: models.Teacher) -> Optional[list[int]]:
    """寮过滤 — 返回该教师能看到的 dorm_unit 列表（None = 不限制 / 看全部）。

    itsuki 2026-06-13 拍板**取消寮过滤**：所有老师可查看 / 操作所有学生，不再按
    男女宿舍（dorm_unit 1,2=男 / 4=女）隔开 —— 功能权限仍由 require_permission 按
    权限组把关。本函数因此返回全部寮 `[1, 2, 4]`（= 不限制）。

    返回全集而非 None：有些调用点直接 `.in_(allowed)` 没有 `if allowed is not None`
    守卫，返回 None 会让 SQL 的 `.in_(None)` 报错；返回全集则无论有无守卫都匹配到
    全部学生。返回类型仍保留 Optional[list[int]]，便于将来恢复按寮过滤
    （旧逻辑见 git 历史 / CROSS_DORM_ROLES 常量）。
    """
    return [1, 2, 4]


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
        return teacher
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": "FORBIDDEN", "message": "不明な token role"},
    )


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
