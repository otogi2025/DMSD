"""食堂食数计算 + Excel 导出 (#7 / Q7)。

権威: system_features.md §7.7。
Q7 答え: 「Excel 表格、要包含的数据是哪些学生不需要餐食、什么期间。要可以一键导出 excel。」

ロジック:
1. status='approved' な applications で meals_skip が非空なものを取得。
2. meals_skip = [{date, meal}, ...] 形式 — 1 エントリ = 1 食不要。
3. 指定期間 [range_from, range_to] に含まれるエントリを日別集計。
4. 出力 = 日別集計 + 学生別詳細 の 2 sheet

⚠️ 2026-05-02 形式変更: 旧 meals_skip_from/to datetime range → 新 [{date, meal}] リスト。
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import date, timedelta, timezone
from typing import Iterable

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from .. import models
from ..deps import demo_scope_for_teacher

JST = timezone(timedelta(hours=9))


@dataclass
class StudentMealDetail:
    student_no: str
    student_name: str
    dorm_unit: int
    room_no: str
    target_date: date
    breakfast_skip: bool
    lunch_skip: bool
    dinner_skip: bool


@dataclass
class DailyAggregate:
    target_date: date
    breakfast_skip: int = 0
    lunch_skip: int = 0
    dinner_skip: int = 0


@dataclass
class MealsCalcResult:
    range_from: date
    range_to: date
    daily: list[DailyAggregate] = field(default_factory=list)
    details: list[StudentMealDetail] = field(default_factory=list)

    @property
    def total(self) -> dict[str, int]:
        return {
            "breakfast_skip": sum(d.breakfast_skip for d in self.daily),
            "lunch_skip": sum(d.lunch_skip for d in self.daily),
            "dinner_skip": sum(d.dinner_skip for d in self.daily),
        }


# ---------------------------------------------------------------
# 計算
# ---------------------------------------------------------------
def _date_range(d_from: date, d_to: date) -> Iterable[date]:
    cur = d_from
    while cur <= d_to:
        yield cur
        cur += timedelta(days=1)


def calc_meals(
    db: Session, *, teacher: models.Teacher, range_from: date, range_to: date
) -> MealsCalcResult:
    """[range_from, range_to] (両端含む) の食事不要数を計算。

    meals_skip = [{date: '2026-05-01', meal: '朝食'}, ...] 形式を集計。

    teacher の演示隔离: demo_scope_for_teacher(teacher) で
    真老师只看真实学生 / 演示老师只看演示学生（防演示账号看到真实学生泄漏）。
    """
    if range_to < range_from:
        raise ValueError("range_to must be >= range_from")

    stmt = (
        select(models.Application, models.Student)
        .join(models.Student, models.Student.id == models.Application.student_id)
        .where(
            and_(
                models.Application.status == "approved",
                models.Application.meals_skip.is_not(None),
                # F-中-09：在 SQL 层按日期范围预筛，缩小候选集 —— meals_skip 条目只可能落在
                # 该申请的 [leave_date, return_date] 出寮窗口内，与查询区间无重叠的申请直接排除，
                # 不再全量 load approved 申请到内存逐条筛。重叠条件：窗口起点 <= 区间终点 且
                # 窗口终点 >= 区间起点。
                models.Application.leave_date <= range_to,
                models.Application.return_date >= range_from,
                demo_scope_for_teacher(teacher),
            )
        )
    )
    rows = db.execute(stmt).all()

    daily_map: dict[date, DailyAggregate] = {
        d: DailyAggregate(target_date=d) for d in _date_range(range_from, range_to)
    }
    # student_no → {date → StudentMealDetail} で重複を避ける
    detail_map: dict[tuple, StudentMealDetail] = {}

    for app, student in rows:
        for entry in app.meals_skip or []:
            # F-中-08：entry 非 dict（脏数据 / 旧形式）时 entry['date'] 会抛 TypeError，
            # 原 except 只 catch (KeyError, ValueError) 漏掉它 → 整个导出 500。
            # 先 isinstance 判断跳过非 dict 条目，再处理键缺失 / 日期格式错。
            if not isinstance(entry, dict):
                continue
            try:
                entry_date = date.fromisoformat(entry["date"])
                meal = entry["meal"]
            except (KeyError, ValueError, TypeError):
                continue
            if entry_date not in daily_map:
                continue

            agg = daily_map[entry_date]
            key = (student.student_no, entry_date)
            if key not in detail_map:
                detail_map[key] = StudentMealDetail(
                    student_no=student.student_no,
                    student_name=student.name,
                    dorm_unit=student.dorm_unit,
                    room_no=student.room_no,
                    target_date=entry_date,
                    breakfast_skip=False,
                    lunch_skip=False,
                    dinner_skip=False,
                )
            det = detail_map[key]
            if meal == "朝食":
                det.breakfast_skip = True
                agg.breakfast_skip += 1
            elif meal == "昼食":
                det.lunch_skip = True
                agg.lunch_skip += 1
            elif meal == "夕食":
                det.dinner_skip = True
                agg.dinner_skip += 1

    return MealsCalcResult(
        range_from=range_from,
        range_to=range_to,
        daily=sorted(daily_map.values(), key=lambda x: x.target_date),
        details=sorted(
            detail_map.values(), key=lambda x: (x.target_date, x.student_no)
        ),
    )


# ---------------------------------------------------------------
# Excel 导出
# ---------------------------------------------------------------
def export_excel(result: MealsCalcResult) -> bytes:
    """openpyxl で .xlsx バイナリを返す。

    Sheet 1: 日別集計 (日付 / 朝 / 昼 / 夕 / 計)
    Sheet 2: 学生別詳細 (学号 / 名前 / 寮 / 部屋 / 日付 / 朝 / 昼 / 夕)
    """
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()

    # ---- Sheet 1: 日別集計 ----
    ws1 = wb.active
    ws1.title = "日別集計"
    ws1.append(["日付", "曜日", "朝食 不要数", "昼食 不要数", "夕食 不要数", "合計"])
    for c in ws1[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="4472C4")
        c.alignment = Alignment(horizontal="center")

    weekday_jp = ["月", "火", "水", "木", "金", "土", "日"]
    for d in result.daily:
        total = d.breakfast_skip + d.lunch_skip + d.dinner_skip
        ws1.append(
            [
                d.target_date.isoformat(),
                weekday_jp[d.target_date.weekday()],
                d.breakfast_skip,
                d.lunch_skip,
                d.dinner_skip,
                total,
            ]
        )
    # 合計行
    totals = result.total
    grand_total = (
        totals["breakfast_skip"] + totals["lunch_skip"] + totals["dinner_skip"]
    )
    ws1.append(
        [
            "合計",
            "",
            totals["breakfast_skip"],
            totals["lunch_skip"],
            totals["dinner_skip"],
            grand_total,
        ]
    )
    last_row = ws1.max_row
    for c in ws1[last_row]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9E1F2")

    # 列幅
    widths = {"A": 12, "B": 6, "C": 14, "D": 14, "E": 14, "F": 10}
    for col, w in widths.items():
        ws1.column_dimensions[col].width = w

    # ---- Sheet 2: 学生別詳細 ----
    ws2 = wb.create_sheet(title="学生別詳細")
    ws2.append(["日付", "学号", "氏名", "寮", "部屋", "朝食", "昼食", "夕食"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="4472C4")
        c.alignment = Alignment(horizontal="center")

    for det in result.details:
        ws2.append(
            [
                det.target_date.isoformat(),
                det.student_no,
                det.student_name,
                _dorm_label(det.dorm_unit),
                det.room_no,
                "○" if det.breakfast_skip else "",
                "○" if det.lunch_skip else "",
                "○" if det.dinner_skip else "",
            ]
        )

    widths2 = {
        "A": 12,
        "B": 10,
        "C": 18,
        "D": 12,
        "E": 8,
        "F": 8,
        "G": 8,
        "H": 8,
    }
    for col, w in widths2.items():
        ws2.column_dimensions[col].width = w
    for col in ("F", "G", "H"):
        for row in range(2, ws2.max_row + 1):
            ws2[f"{col}{row}"].alignment = Alignment(horizontal="center")

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _dorm_label(dorm_unit: int) -> str:
    return {1: "1 寮", 2: "2 寮", 4: "4 寮"}.get(dorm_unit, f"{dorm_unit} 寮")


def export_filename(range_from: date, range_to: date) -> str:
    return f"meals_{range_from.isoformat()}_{range_to.isoformat()}.xlsx"
