"""Pydantic v2 schemas — request / response。

#2 出寮届 schema 中心。3 種 (帰省 / 外泊 / 帰国) は kind discriminator で逐层累積。
"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Annotated, Any, Literal, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# ---------------------------------------------------------------
# 共通
# ---------------------------------------------------------------
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StayLocation(BaseModel):
    """外泊・帰国 時の宿泊先 (複数可)。"""

    kind: str = Field(..., description="ホテル / 親戚宅 / 自宅 等")
    name: str = Field(..., max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=32)


# ---------------------------------------------------------------
# 認証
# ---------------------------------------------------------------
class StudentLoginIn(BaseModel):
    student_no: Annotated[str, Field(pattern=r"^\d{6}$")]
    password: str = Field(..., min_length=8, max_length=128)


class TeacherLoginIn(BaseModel):
    login_id: str = Field(..., max_length=32)
    password: str = Field(..., min_length=8, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


# ---------------------------------------------------------------
# 学生 (出寮届で参照)
# ---------------------------------------------------------------
class StudentBrief(BaseModel):
    id: UUID
    student_no: str
    name: str
    dorm_unit: int
    is_overseas: bool
    room_no: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 出寮届 — 共通フィールド
# ---------------------------------------------------------------
class ApplicationBase(BaseModel):
    """3 種共通フィールド。"""

    leave_date: date
    leave_method: str = Field(..., max_length=200)
    leave_time: time
    return_date: date
    return_method: str = Field(..., max_length=200)
    return_time: time

    @model_validator(mode="after")
    def _check_dates(self) -> "ApplicationBase":
        if self.return_date < self.leave_date:
            raise ValueError("return_date must be on or after leave_date")
        return self


# ---------------------------------------------------------------
# 出寮届 — 種類別 (discriminated)
# ---------------------------------------------------------------
class KisheiCreateIn(ApplicationBase):
    """帰省届 (一時的に実家に帰る)。最も簡素。"""

    kind: Literal["帰省"] = "帰省"


class GaihakuCreateIn(ApplicationBase):
    """外泊届 (寮以外で泊まる)。+ 滞在先 + 食事不要期間。"""

    kind: Literal["外泊"] = "外泊"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip_from: Optional[datetime] = None
    meals_skip_to: Optional[datetime] = None

    @model_validator(mode="after")
    def _check_meals(self) -> "GaihakuCreateIn":
        if self.meals_skip_from and self.meals_skip_to:
            if self.meals_skip_to <= self.meals_skip_from:
                raise ValueError("meals_skip_to must be after meals_skip_from")
        return self


class KikokuCreateIn(ApplicationBase):
    """帰国届 (国外帰省, 留学生がメイン)。+ 飛行機情報。"""

    kind: Literal["帰国"] = "帰国"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip_from: Optional[datetime] = None
    meals_skip_to: Optional[datetime] = None
    flight_dep_air: str = Field(..., max_length=64)
    flight_dep_at: datetime
    flight_arr_air: str = Field(..., max_length=64)
    flight_arr_at: datetime

    @model_validator(mode="after")
    def _check_flight(self) -> "KikokuCreateIn":
        if self.flight_arr_at <= self.flight_dep_at:
            raise ValueError("flight_arr_at must be after flight_dep_at")
        if self.meals_skip_from and self.meals_skip_to:
            if self.meals_skip_to <= self.meals_skip_from:
                raise ValueError("meals_skip_to must be after meals_skip_from")
        return self


# Discriminated union — POST /applications で kind 値で type が決まる
ApplicationCreateIn = Annotated[
    KisheiCreateIn | GaihakuCreateIn | KikokuCreateIn,
    Field(discriminator="kind"),
]


# ---------------------------------------------------------------
# 出寮届 — Out (#5 承认状态查询)
# ---------------------------------------------------------------
class ApprovalStepOut(BaseModel):
    """承认 chain の 1 step。"""

    approver_role: str
    decision: Optional[Literal["approve", "reject"]] = None
    decided_at: Optional[datetime] = None
    comment: Optional[str] = None
    approver_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationOut(BaseModel):
    """#5 承认状态查询で返す。"""

    id: UUID
    student_id: UUID
    student: Optional[StudentBrief] = None
    kind: Literal["帰省", "外泊", "帰国"]

    leave_date: date
    leave_method: str
    leave_time: time
    return_date: date
    return_method: str
    return_time: time

    stay_locations: Optional[list[dict[str, Any]]] = None
    meals_skip_from: Optional[datetime] = None
    meals_skip_to: Optional[datetime] = None

    flight_dep_air: Optional[str] = None
    flight_dep_at: Optional[datetime] = None
    flight_arr_air: Optional[str] = None
    flight_arr_at: Optional[datetime] = None

    bus_route_id: Optional[UUID] = None

    submitted_at: datetime
    status: Literal[
        "pending", "approved_partial", "approved", "rejected", "withdrawn"
    ]
    withdrawn_at: Optional[datetime] = None

    approval_chain: list[ApprovalStepOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 通知 (#6 SendGrid テスト)
# ---------------------------------------------------------------
class NotificationTestIn(BaseModel):
    to: EmailStr
    subject: str = Field("Tomoshibi 邮件送达测试", max_length=200)
    body_text: str = Field(
        "これは Tomoshibi バックエンドからの送達テストです。届いていれば SendGrid 設定 OK。",
        max_length=2000,
    )


class NotificationTestOut(BaseModel):
    sent: bool
    notification_log_id: UUID
    sendgrid_status_code: Optional[int] = None
    error: Optional[str] = None


# ---------------------------------------------------------------
# 食堂 食数 (#7)
# ---------------------------------------------------------------
class MealsExportQuery(BaseModel):
    """GET /meals/export クエリ。"""

    from_: date = Field(..., alias="from")
    to: date

    @field_validator("to")
    @classmethod
    def _check_to(cls, v: date, info) -> date:
        if "from_" in info.data and v < info.data["from_"]:
            raise ValueError("to must be on or after from")
        return v


class MealDailyCount(BaseModel):
    target_date: date
    breakfast_skip: int
    lunch_skip: int
    dinner_skip: int


class MealsCalcOut(BaseModel):
    """GET /meals/calc — Excel ではなく JSON で返す debug 用 endpoint。"""

    range_from: date
    range_to: date
    daily: list[MealDailyCount]
    total: dict[str, int]
