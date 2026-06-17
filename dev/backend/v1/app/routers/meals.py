"""食堂食数统计 (#7 / Q7) — 计算 + Excel 导出。

GET /api/v1/meals/calc?from=&to=          — JSON（debug 用）
GET /api/v1/meals/export?from=&to=        — .xlsx 下载
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

# 范围跨度上限：食数表实际只按月 / 学期导出。无上限时传 from=0001-01-01&to=9999-12-31
# 会让 services.meals._date_range 逐日迭代构造约 365 万个聚合对象 + 同规模 Excel 行，
# 单请求即可耗尽内存 / CPU 拖垮整个后端（认证后 DoS）。限 1 年既够用又封死放大攻击。
_MAX_RANGE_DAYS = 366


def _validate_meals_range(from_: date, to: date) -> None:
    if to < from_:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_RANGE",
                "message": "to は from 以後にしてください",
            },
        )
    if (to - from_).days > _MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "RANGE_TOO_LARGE",
                "message": "期間は1年以内で指定してください",
            },
        )


@router.get("/calc", response_model=schemas.MealsCalcOut)
def calc(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db),
    teacher: models.Teacher = Depends(
        require_permission(permissions.C_MEAL, permissions.VIEW)
    ),
):
    _validate_meals_range(from_, to)
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
    _validate_meals_range(from_, to)
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
