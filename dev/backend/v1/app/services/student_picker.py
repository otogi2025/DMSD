"""挑人共用查询 —— 前台/扣分两处 StudentPicker 端点共用查询本体。

backend#104：front_desk.search_recipients 与 discipline.search_students_for_demerit
的「demo 隔离 + LIKE 转义 + 寮过滤 + limit(20) → FrontDeskStudentBrief」几乎逐行重复，
仅权限簇不同（C_FRONT_DESK / C_DEMERIT）。抽到此处，两端各自包一层 require_permission
后调本函数复用；后续改转义/过滤只改一处。
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import demo_scope_for_teacher, dorm_units_for_teacher


def query_students_for_picker(
    db: Session,
    teacher: models.Teacher,
    q: Optional[str] = None,
) -> list[schemas.FrontDeskStudentBrief]:
    """demo 隔离 + LIKE 转义 + 寮过滤 + limit(20) → FrontDeskStudentBrief。"""
    stmt = select(models.Student).where(demo_scope_for_teacher(teacher))
    if q:
        # 转义用户输入里的 LIKE 通配符 % 和 _（与 admin_accounts.py 同款），否则老师
        # 输入含 % 的查询会被当通配符匹配全部（功能性瑕疵，非注入——值已被 SQLAlchemy
        # 参数化）。escape='\\' 指定反斜杠为转义字符，先转义反斜杠自身再转义 % 和 _。
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        stmt = stmt.where(
            models.Student.name.like(like, escape="\\")
            | (
                models.Student.grade_code
                + models.Student.class_code
                + models.Student.seat_no
            ).like(like, escape="\\")
        )
    allowed = dorm_units_for_teacher(teacher)
    if allowed is not None:
        stmt = stmt.where(models.Student.dorm_unit.in_(allowed))
    stmt = stmt.order_by(models.Student.room_no).limit(20)
    return [
        schemas.FrontDeskStudentBrief(
            id=s.id,
            name=s.name,
            room_no=s.room_no,
            student_no=f"{s.grade_code}{s.class_code}{s.seat_no}",
            dorm_unit=s.dorm_unit,
        )
        for s in db.scalars(stmt).all()
    ]
