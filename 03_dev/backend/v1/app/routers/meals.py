"""食堂 食数 (#7 / Q7) — 計算 + Excel 导出。

GET /api/v1/meals/calc?from=&to=          — JSON (debug 用)
GET /api/v1/meals/export?from=&to=        — .xlsx ダウンロード
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import require_permission
from ..services import meals as meals_svc

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])


@router.get("/calc", response_model=schemas.MealsCalcOut)
def calc(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_MEAL, permissions.VIEW)
    ),
):
    if to < from_:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_RANGE",
                "message": "to は from 以後にしてください",
            },
        )
    result = meals_svc.calc_meals(db, teacher=teacher, range_from=from_, range_to=to)
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
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_MEAL, permissions.MANAGE)
    ),
):
    if to < from_:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_RANGE",
                "message": "to は from 以後にしてください",
            },
        )
    result = meals_svc.calc_meals(db, teacher=teacher, range_from=from_, range_to=to)
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
