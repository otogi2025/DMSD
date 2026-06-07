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

from . import models, security
from .database import get_db

# R4 — 跨寮角色能看全件
CROSS_DORM_ROLES = frozenset(
    {"校長", "寮務部長", "寮務課長", "国際交流部長", "国際交流課長"}
)


def dorm_units_for_teacher(teacher: models.Teacher) -> Optional[list[int]]:
    """R4 寮过滤 — 返回该教师能看到的 dorm_unit 列表。

    - 跨寮角色（校長 / 寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長）→ None（看全部）
    - 男寮老师（assigned_dorm=1）→ [1, 2]（spec: 男生 dorm_unit IN (1, 2)）
    - 女寮老师（assigned_dorm=4）→ [4]
    - assigned_dorm IS NULL（跨寮预设）→ None
    """
    if teacher.role in CROSS_DORM_ROLES:
        return None
    if teacher.assigned_dorm is None:
        return None
    if teacher.assigned_dorm == 1:
        return [1, 2]
    return [teacher.assigned_dorm]


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


def require_teacher_roles(*allowed: str):
    """`require_teacher_roles('寮務部長', '寮務課長')` 形式で使う。"""

    def _checker(
        teacher: models.Teacher = Depends(get_current_teacher),
    ) -> models.Teacher:
        if teacher.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": f"権限不足 (必要 role: {', '.join(allowed)})",
                },
            )
        return teacher

    return _checker
