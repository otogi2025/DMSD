"""食堂 食数 (#7 / Q7) — 計算 + Excel 导出。

GET /api/v1/meals/calc?from=&to=          — JSON (debug 用)
GET /api/v1/meals/export?from=&to=        — .xlsx ダウンロード
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_teacher
from ..services import meals as meals_svc

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])


# 食堂データを見て良い役职 (寮務 + 管理係)
_ALLOWED_ROLES = {"寮務部長", "寮務課長", "管理係", "寮務一般教师"}


def _check_role(teacher: models.Teacher) -> None:
    if teacher.role not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE",
                "message": "食堂データへのアクセス権限がありません",
            },
        )


@router.get("/calc", response_model=schemas.MealsCalcOut)
def calc(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    _check_role(teacher)
    if to < from_:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_RANGE", "message": "to は from 以後にしてください"},
        )
    result = meals_svc.calc_meals(db, range_from=from_, range_to=to)
    return schemas.MealsCalcOut(
        range_from=result.range_from,
        range_to=result.range_to,
        daily=[
            schemas.MealDailyCount(
                target_date=d.target_date,
                breakfast_skip=d.breakfast_skip,
                lunch_skip=d.lunch_skip,
                dinner_skip=d.dinner_skip,
            )
            for d in result.daily
        ],
        total=result.total,
    )


@router.get("/export")
def export(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(get_current_teacher),
):
    _check_role(teacher)
    if to < from_:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_RANGE", "message": "to は from 以後にしてください"},
        )
    result = meals_svc.calc_meals(db, range_from=from_, range_to=to)
    payload = meals_svc.export_excel(result)
    filename = meals_svc.export_filename(from_, to)

    return StreamingResponse(
        iter([payload]),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(payload)),
        },
    )
