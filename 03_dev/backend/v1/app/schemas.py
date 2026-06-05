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


class MealSkipEntry(BaseModel):
    """食事不要エントリ — 日付 + 食事種別。spec §7.7 食堂 Excel 対応形式。"""

    date: date
    meal: Literal["朝食", "昼食", "夕食"]


# ---------------------------------------------------------------
# 認証
# ---------------------------------------------------------------
class StudentLoginIn(BaseModel):
    student_no: Annotated[str, Field(pattern=r"^\d{6}$")]
    password: str = Field(..., min_length=6, max_length=128)


class TeacherLoginIn(BaseModel):
    """老师登录：login_id 或 teacher_id 至少传一个。
    2026-05-27 拍板「实名账户登录」方式：前端从 GET /teachers/public 拿 UUID（id）后用 teacher_id 登录，
    避免把 login_id 列表暴露给无认证爬虫（防止枚举攻击 + 针对性爆破）。
    原 login_id + password 形式保留作 backward-compat（CLI / 旧测试）。"""

    login_id: Optional[str] = Field(default=None, max_length=32)
    teacher_id: Optional[UUID] = None
    password: str = Field(..., min_length=6, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class TeacherTokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    teacher: "TeacherOut"


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

    reason: Optional[str] = Field(None, max_length=500)
    leave_date: date
    leave_method: str = Field(..., max_length=200)
    leave_time: time
    return_date: date
    return_method: str = Field(..., max_length=200)
    return_time: time
    contact_phone: Optional[str] = Field(None, max_length=64)
    meal_note: Optional[str] = Field(None, max_length=2000)
    # 出租车预约「タクシー予約」时刻（itsuki 2026-06-03）— null = 不预约
    taxi_reservation_time: Optional[time] = None

    @model_validator(mode="after")
    def _check_dates(self) -> "ApplicationBase":
        if self.return_date < self.leave_date:
            raise ValueError("return_date must be on or after leave_date")
        # 同日时帰寮必须晚于出寮（codex 审查 中-1：原来只比日期，同日 17:00 出 /
        # 08:00 帰 这种倒挂能过；放后端 = 5 端所有客户端统一兜底）
        if self.return_date == self.leave_date and self.return_time <= self.leave_time:
            raise ValueError("return_time must be after leave_time on the same day")
        return self


# ---------------------------------------------------------------
# 出寮届 — 種類別 (discriminated)
# ---------------------------------------------------------------
class KisheiCreateIn(ApplicationBase):
    """帰省届 (一時的に実家に帰る)。最も簡素。"""

    kind: Literal["帰省"] = "帰省"
    is_long_vacation: bool = False


class GaihakuCreateIn(ApplicationBase):
    """外泊届 (寮以外で泊まる)。+ 滞在先 + 食事不要リスト。"""

    kind: Literal["外泊"] = "外泊"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list)
    companion: Optional[str] = Field(None, max_length=500)
    dest_cities: Optional[str] = Field(None, max_length=500)


class KikokuCreateIn(ApplicationBase):
    """帰国届 (国外帰省, 留学生がメイン)。+ 飛行機情報。"""

    kind: Literal["帰国"] = "帰国"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list)
    companion: Optional[str] = Field(None, max_length=500)
    dest_cities: Optional[str] = Field(None, max_length=500)
    flight_dep_air: str = Field(..., max_length=64)
    flight_dep_at: datetime
    flight_arr_air: str = Field(..., max_length=64)
    flight_arr_at: datetime

    @model_validator(mode="after")
    def _check_flight(self) -> "KikokuCreateIn":
        if self.flight_arr_at <= self.flight_dep_at:
            raise ValueError("flight_arr_at must be after flight_dep_at")
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
    contact_phone: Optional[str] = None
    meal_note: Optional[str] = None

    stay_locations: Optional[list[dict[str, Any]]] = None
    meals_skip: Optional[list[dict[str, Any]]] = None
    companion: Optional[str] = None
    dest_cities: Optional[str] = None
    receipt_submitted: bool = False
    reason: Optional[str] = None
    is_long_vacation: bool = False

    flight_dep_air: Optional[str] = None
    flight_dep_at: Optional[datetime] = None
    flight_arr_air: Optional[str] = None
    flight_arr_at: Optional[datetime] = None
    taxi_reservation_time: Optional[time] = None

    bus_route_id: Optional[UUID] = None

    submitted_at: datetime
    status: Literal[
        "pending", "approved_partial", "approved", "rejected", "withdrawn", "returned"
    ]
    withdrawn_at: Optional[datetime] = None

    approval_chain: list[ApprovalStepOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 外出申请 — 单一老师确认（itsuki 2026-06-04 拍板; 见 system_features §7.2.7）
# ---------------------------------------------------------------
class OutingCreateIn(BaseModel):
    """POST /outings — 学生提出外出申请（当天回寮）。"""

    outing_date: date
    destination: Optional[str] = Field(None, max_length=200)  # 去向
    leave_time: Optional[time] = None  # 外出时刻
    return_time: Optional[time] = None  # 回寮预定时刻（同一天）
    taxi_reservation_time: Optional[time] = None  # 出租车预约时刻; null=不预约
    reason: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def _check_times(self) -> "OutingCreateIn":
        # 当天回寮：两个时刻都填时，回寮时刻不能早于外出时刻
        if (
            self.leave_time is not None
            and self.return_time is not None
            and self.return_time < self.leave_time
        ):
            raise ValueError("return_time must be on or after leave_time")
        return self


class OutingOut(BaseModel):
    """外出申请查询返回。confirmed_by_name = 确认老师的姓名（学生侧显示「確認 · ○○ 先生」）。"""

    id: UUID
    student_id: UUID
    student: Optional[StudentBrief] = None
    outing_date: date
    destination: Optional[str] = None
    leave_time: Optional[time] = None
    return_time: Optional[time] = None
    taxi_reservation_time: Optional[time] = None
    reason: Optional[str] = None
    status: Literal["pending", "approved", "withdrawn"]
    submitted_at: datetime
    withdrawn_at: Optional[datetime] = None
    confirmed_by_teacher_id: Optional[UUID] = None
    confirmed_by_name: Optional[str] = None
    confirmed_at: Optional[datetime] = None

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


# ---------------------------------------------------------------
# 出寮届 — 追加 endpoints
# ---------------------------------------------------------------
class ApprovalIn(BaseModel):
    """POST /applications/:id/approvals — 役職承認/拒否。"""

    decision: Literal["approve", "reject"]
    comment: Optional[str] = Field(None, max_length=1000)


class ApplicationUpdateIn(BaseModel):
    """PUT /applications/:id — 学生が承認前に内容修正 (chain リセット)。"""

    reason: Optional[str] = Field(None, max_length=500)
    # 修改理由 — 学生改届时填、只写进 audit 给老师看，不覆盖申请本身的 reason（申请理由）。
    amend_reason: Optional[str] = Field(None, max_length=500)
    leave_date: Optional[date] = None
    leave_method: Optional[str] = Field(None, max_length=200)
    leave_time: Optional[time] = None
    return_date: Optional[date] = None
    return_method: Optional[str] = Field(None, max_length=200)
    return_time: Optional[time] = None
    contact_phone: Optional[str] = Field(None, max_length=64)
    companion: Optional[str] = Field(None, max_length=500)
    dest_cities: Optional[str] = Field(None, max_length=500)
    meal_note: Optional[str] = Field(None, max_length=2000)
    # 出租车预约暂为 create-only：修改届不改 taxi（取消需三态语义，见 TODO N-004）
    is_long_vacation: Optional[bool] = None
    stay_locations: Optional[list[StayLocation]] = None
    meals_skip: Optional[list[MealSkipEntry]] = None
    flight_dep_air: Optional[str] = Field(None, max_length=64)
    flight_dep_at: Optional[datetime] = None
    flight_arr_air: Optional[str] = Field(None, max_length=64)
    flight_arr_at: Optional[datetime] = None


class AuditLogOut(BaseModel):
    """GET /applications/:id/audit — 審査履歴エントリ。"""

    id: UUID
    actor_type: str
    actor_id: Optional[UUID]
    action: str
    payload: Optional[Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 学習 (Study)
# ---------------------------------------------------------------
class StudyAttendeeOut(BaseModel):
    """GET /study/today/attendees の 1 エントリ。"""

    student_id: UUID
    student_no: str
    name: str
    room_no: str
    dorm_unit: int
    expected_status: str  # 'expected' | 'exempted_outstay' | 'exempted_absence'
    exemption_reason: Optional[str] = None
    checkin: Optional[dict[str, Any]] = None


class StudyTodayOut(BaseModel):
    """GET /study/today/attendees — 全体レスポンス。"""

    target_date: date
    study_start_at: datetime
    expected_attendees: list[StudyAttendeeOut]
    exempted_count: dict[str, int]
    summary: dict[str, int]


class StudyCheckinIn(BaseModel):
    """POST /study/checkins — 学習担当が出席を記録。"""

    student_id: UUID
    checked_at: Optional[datetime] = None  # None = now


class StudyCheckinOut(BaseModel):
    student_id: UUID
    target_date: date
    checked_at: Optional[datetime]
    status: str

    model_config = ConfigDict(from_attributes=True)


class StudyFinalizeIn(BaseModel):
    """POST /study/checkins/bulk-finalize — 一本道の終了ボタン。"""

    target_date: Optional[date] = None  # None = today


class StudyFinalizeOut(BaseModel):
    finalized_count: int
    absent_students: list[dict[str, Any]]


class StudyCheckinPatch(BaseModel):
    """PATCH /study/checkins/:id — 手動修正。"""

    status: Literal["present", "late", "absent", "exempt"]
    override_reason: str = Field(..., min_length=1, max_length=500)


class StudyAbsenceRequestIn(BaseModel):
    """POST /study/absence-requests — 学生が当日 19:40 前に提出。"""

    target_date: date
    # 欠席する範囲: 前半節 / 後半節 / 両方
    period: Literal["first_half", "second_half", "full"]
    reason: str = Field(..., min_length=1, max_length=2000)


class StudyAbsenceDecisionIn(BaseModel):
    """POST /study/absence-requests/:id/decision — 学習担当が approve/reject。"""

    decision: Literal["approved", "rejected"]
    comment: Optional[str] = Field(None, max_length=1000)


class StudyAbsenceRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    target_date: date
    period: Literal["first_half", "second_half", "full"]
    reason: str
    submitted_at: datetime
    status: str
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class StudyRosterEntryOut(BaseModel):
    """GET /study/roster 返回的一条记录 — 名簿在籍中的一名学生。"""

    student_id: UUID
    student_no: str
    name: str
    room_no: str
    dorm_unit: int
    academic_term: str
    # added_by 为空 = 系统自动加入（中学全员）/ 非空 = 老师手动加入
    added_by: Optional[UUID]
    added_at: datetime


class StudyRosterAddIn(BaseModel):
    """POST /study/roster — 把一名学生加入学習対象名簿。

    两种指定方式二选一（至少给一个）：
    - student_id：学生 UUID（客户端已拿到 id 时用）
    - student_no：学号（6 位 = 年级 2 + 班级 2 + 座号 2），老师网页直接输学号用。
      老师网页名簿管理页用学号 —— 避免依赖账号管理搜索接口（那个接口角色 gate 更窄）。
    """

    student_id: Optional[UUID] = None
    student_no: Optional[str] = Field(None, min_length=6, max_length=6)

    @model_validator(mode="after")
    def _need_one(self) -> "StudyRosterAddIn":
        if self.student_id is None and not self.student_no:
            raise ValueError("student_id か student_no のどちらかが必要です")
        return self


class StudyOnlineRequestIn(BaseModel):
    """学生提交在线学习申请。"""

    reason: str = Field(..., min_length=1, max_length=2000)
    period_from: date
    period_to: date
    weekly_schedule: dict[str, list[dict[str, str]]]
    contract_ref: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def _check_period(self) -> "StudyOnlineRequestIn":
        if self.period_to < self.period_from:
            raise ValueError("period_to must be on or after period_from")
        return self


class StudyOnlineDecisionIn(BaseModel):
    """老师对在线学习申请做单人审批。"""

    decision: Literal["approved", "rejected", "revoked"]
    comment: Optional[str] = Field(None, max_length=1000)


class StudyOnlineRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    reason: str
    period_from: date
    period_to: date
    weekly_schedule: dict[str, Any]
    contract_ref: Optional[str]
    # 契約書文件信息 — 不暴露服务器物理路径 contract_file_path（安全）。
    # 客户端按 contract_file_name 是否非空判断「有没有上传文件」，
    # 要看内容时调 GET /study/online-requests/{id}/contract。
    contract_file_name: Optional[str] = None
    contract_mime: Optional[str] = None
    contract_size: Optional[int] = None
    submitted_at: datetime
    status: Literal["pending", "approved", "rejected", "revoked"]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DormEventProposalCreateIn(BaseModel):
    """学生提交寮生行事企画申請。"""

    team_name: Optional[str] = Field(None, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    held_at: datetime
    place: str = Field(..., min_length=1, max_length=500)
    expected_count: int = Field(..., ge=0)
    target: str = Field(..., min_length=1, max_length=500)
    purpose: str = Field(..., min_length=1, max_length=2000)
    content: str = Field(..., min_length=1, max_length=4000)
    risk_solution: str = Field(..., min_length=1, max_length=4000)
    expected_cost: str = Field(..., min_length=1, max_length=1000)
    note: Optional[str] = Field(None, max_length=2000)


class DormEventProposalDecisionIn(BaseModel):
    decision: Literal["approved", "approved_conditional", "resubmit", "rejected"]
    comment: Optional[str] = Field(None, max_length=1000)


class DormEventProposalOut(BaseModel):
    id: UUID
    proposer_id: UUID
    team_name: Optional[str]
    title: str
    held_at: datetime
    place: str
    expected_count: int
    target: str
    purpose: str
    content: str
    risk_solution: str
    expected_cost: str
    note: Optional[str]
    submitted_at: datetime
    result: Literal[
        "pending", "approved", "approved_conditional", "resubmit", "rejected"
    ]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DormScheduleChangeCreateIn(BaseModel):
    """老师提交寮日課変更願。"""

    class_or_club: str = Field(..., min_length=1, max_length=500)
    period_from: datetime
    period_to: datetime
    student_count: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1, max_length=2000)
    change_content: str = Field(..., min_length=1, max_length=4000)

    @model_validator(mode="after")
    def _check_period(self) -> "DormScheduleChangeCreateIn":
        if self.period_to <= self.period_from:
            raise ValueError("period_to must be after period_from")
        return self


class DormScheduleChangeDecisionIn(BaseModel):
    decision: Literal["approved", "rejected"]
    comment: Optional[str] = Field(None, max_length=1000)


class DormScheduleChangeOut(BaseModel):
    id: UUID
    requester_id: UUID
    class_or_club: str
    period_from: datetime
    period_to: datetime
    student_count: int
    reason: str
    change_content: str
    submitted_at: datetime
    status: Literal["pending", "approved", "rejected"]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class FridgePurchaseRequestCreateIn(BaseModel):
    """学生提交冷蔵庫購入届。"""

    contact_phone: str = Field(..., min_length=1, max_length=64)
    contact_wechat: Optional[str] = Field(None, max_length=128)
    product: Literal["A", "B"]


class FridgePurchaseDecisionIn(BaseModel):
    decision: Literal["ordered", "delivered", "rejected"]
    delivered_sign: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=1000)


class FridgePurchaseRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    contact_phone: str
    contact_wechat: Optional[str]
    product: Literal["A", "B"]
    submitted_at: datetime
    delivered_sign: Optional[str]
    status: Literal["pending", "ordered", "delivered", "rejected"]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ItemPossessionRequestCreateIn(BaseModel):
    """学生提交物品所持許可願。"""

    room_no: str = Field(..., min_length=1, max_length=16)
    item: str = Field(..., min_length=1, max_length=1000)
    reason: str = Field(..., min_length=1, max_length=2000)
    guardian_name: str = Field(..., min_length=1, max_length=200)


class ItemPossessionDecisionIn(BaseModel):
    decision: Literal["approved", "rejected"]
    comment: Optional[str] = Field(None, max_length=1000)


class ItemPossessionRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    room_no: str
    item: str
    reason: str
    guardian_name: str
    submitted_at: datetime
    status: Literal["pending", "approved", "rejected"]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 点呼 (Roll Call)
# ---------------------------------------------------------------
class RollCallSessionOut(BaseModel):
    id: UUID
    dorm_unit_set: list[int]
    session_type: str
    day_type: str
    session_status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    scheduled_window_start_at: datetime
    scheduled_on_time_end_at: datetime
    scheduled_late_end_at: datetime
    scheduled_auto_end_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RollCallCheckinIn(BaseModel):
    """POST /rollcall/sessions/:id/checkins — NFC or 手動点呼。

    2026-05-21 加 path_hint（A-020）：client 显式标路径，backend 校验字段一致性。
    避免「同时有 card_uid + idempotency_key 时 backend 推断错路径」。
    """

    card_uid: Optional[str] = Field(None, max_length=32)  # 路径 A
    student_id: Optional[UUID] = None  # 路径 B / 手動
    idempotency_key: Optional[str] = Field(None, max_length=64)  # 路径 B
    status_source: str = "auto_nfc"  # auto_nfc / manual_checkin
    ts_local: Optional[datetime] = None
    # A-020 (2026-05-21): client 显式标路径
    # - "A" = NFC 卡（必须有 card_uid）
    # - "B" = iPhone tap（必须有 idempotency_key；v1.1 起追加 nonce + signature）
    # - "manual" = 老师手动签到（card_uid / idempotency_key 都可缺）
    # 为兼容旧 client 暂保持 Optional；下一个 minor 版本改 required
    path_hint: Optional[Literal["A", "B", "manual"]] = None


class RollCallEventOut(BaseModel):
    id: UUID
    student_id: UUID
    base_status: str
    status_source: str
    checked_in_at: datetime
    path_type: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class RollCallBoardEntryOut(BaseModel):
    student_id: UUID
    student_no: str
    name: str
    room_no: str
    base_status: str  # init / present / late / absent / exempt_range
    checked_in_at: Optional[datetime]
    # 该学生在本场次最新一条 RollCallEvent 的 id — frontend OverrideModal
    # 调 PATCH /events/{id} 改判时用。init 状态学生没 event = None
    last_event_id: Optional[UUID] = None


class RollCallBoardOut(BaseModel):
    session_id: UUID
    session_status: str
    entries: list[RollCallBoardEntryOut]
    summary: dict[str, int]


class RollCallSummaryOut(BaseModel):
    session_id: UUID
    absent: list[dict[str, Any]]
    late: list[dict[str, Any]]
    health_issue: list[dict[str, Any]]
    exempted_outstay: list[dict[str, Any]]


class RollCallEventPatch(BaseModel):
    """PATCH /rollcall/events/:id — 教師改判 (RollCall_Spec §11)。"""

    to_status: Literal["present", "late", "absent", "exempt_range"]
    reason: str = Field(..., min_length=1, max_length=500)
    evidence: Optional[str] = Field(None, max_length=500)


# ---------------------------------------------------------------
# 教師管理 (Teacher Invitation — §3.4)
# ---------------------------------------------------------------
class TeacherInvitationIn(BaseModel):
    target_email: EmailStr
    target_role: str
    target_dorm: Optional[int] = None


class TeacherInvitationOut(BaseModel):
    id: UUID
    token: str
    target_email: str
    target_role: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherRegisterIn(BaseModel):
    """POST /teachers/register?token=... — 招待トークンで新規登録。

    2026-05-21 加 confirmation_email（A-012）：
        - 注册者必须重输 email，跟 invitation.target_email 严格对比
        - 防止 token 被截图 / 转发 → 任何拿到 token 的人能注册
    """

    token: str
    name: str = Field(..., min_length=1, max_length=100)
    login_id: str = Field(..., min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    confirmation_email: str = Field(
        ..., max_length=200
    )  # A-012: 跟 invitation.target_email 对比


class TeacherOut(BaseModel):
    id: UUID
    login_id: str
    name: str
    email: str
    role: str
    assigned_dorm: Optional[int]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherPublicOut(BaseModel):
    """GET /teachers/public — 登录页第 1 屏用，无认证可见。
    只暴露 id + name + assigned_dorm + last_login_at — 不暴露 login_id / email / role / status / failed_count（防爬虫枚举）。
    last_login_at 由前端转「N 分前 / 本日未 / 初回」显示。"""

    id: UUID
    name: str
    assigned_dorm: Optional[int]
    last_login_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class TeacherCreateIn(BaseModel):
    """POST /teachers — 已登录教师 + 寮務管理权限 → 直接创建新教师（v1.0 简化版，跳过邀请码流程）。
    邀请码流程（POST /teachers/invitations + /register）保留 backend 但 v1.0 web 不实装 UI。"""

    login_id: str = Field(..., min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str
    assigned_dorm: Optional[int] = None


# ---------------------------------------------------------------
# 学生注册码（Student Registration Code）
#   权威 spec：system_features §7.16 + BACKEND §4.10 + §5.1.5（2026-05-03 拍板）
# ---------------------------------------------------------------
class RegistrationCodeOut(BaseModel):
    """GET/POST registration-code/* 通用响应。"""

    code: str = Field(..., min_length=6, max_length=6)
    created_at: datetime
    expires_at: datetime
    # 剩余秒数 — 给客户端做倒计时显示用（= max(0, expires_at - now)）
    expires_in_seconds: int

    model_config = ConfigDict(from_attributes=True)


class RegistrationCodeHistoryEntry(BaseModel):
    code: str
    created_at: datetime
    expires_at: datetime
    invalidated_at: Optional[datetime]
    created_by_teacher_name: str

    model_config = ConfigDict(from_attributes=True)


class RegistrationCodeHistoryOut(BaseModel):
    items: list[RegistrationCodeHistoryEntry]


# ---------------------------------------------------------------
# 学生新规注册（POST /accounts — spec §5.1.5）
#   2026-05-03 拍板：必须传 registration_code（App Store 上架对策）
# ---------------------------------------------------------------
class StudentAccountCreateIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    name_kana: Optional[str] = Field(None, max_length=100)
    birthday: Optional[date] = None
    gender: Literal["male", "female"]
    grade_code: str = Field(..., min_length=2, max_length=2, pattern=r"^\d{2}$")
    class_code: str = Field(..., min_length=2, max_length=2, pattern=r"^\d{2}$")
    seat_no: str = Field(..., min_length=2, max_length=2, pattern=r"^\d{2}$")
    category: str = Field(default="一般寮生", max_length=32)
    room_no: str = Field(..., min_length=3, max_length=8)
    # spec §5.0：寮号只有 1/2（男寮）、4（女寮）— 没有 3，与 models.py CHECK 约束对齐
    # B10：原来 ge=1, le=4 允许 3，DB CHECK 只接受 1/2/4，改为 Literal 精确限定
    dorm_unit: Literal[1, 2, 4]
    is_overseas: bool = False
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    # 老师在后台生成的 6 桁码（默认 30 分钟内有效）
    registration_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

    # B10：validator 已删 — Literal[1,2,4] 本身就拦 3，无需额外校验器


class StudentAccountCreateOut(BaseModel):
    """201 — JWT（永久 session，和 login 同等）+ 学生 brief。"""

    access_token: str
    # 跟 TokenOut 对齐，方便 iOS 复用同一个 Decodable
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    student: StudentBrief


# ---------------------------------------------------------------
# 老师公告（Announcement）
#   权威 spec：system_features §7.15（2026-05-03 itsuki 拍板，2026-05-04 实装）
#   scope：all = 全员 / male = 男寮 / female = 女寮
# ---------------------------------------------------------------
class AnnouncementReplyOut(BaseModel):
    id: UUID
    author_kind: Literal["student", "teacher"]
    author_id: UUID
    # 用 join 取的发言人名字（回复列表显示需要）
    author_name: str
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementBrief(BaseModel):
    """列表 view 用 — 本文 80 字摘要 + 回复数。"""

    id: UUID
    title: str
    # 本文头 80 字（服务端切出来，避免前端拿到全文浪费流量）
    body_summary: str
    scope: Literal["all", "male", "female"]
    author_teacher_id: UUID
    author_teacher_name: str
    created_at: datetime
    updated_at: datetime
    # 当前学生的已读状态
    is_read: bool
    reply_count: int

    model_config = ConfigDict(from_attributes=True)


class AnnouncementListOut(BaseModel):
    items: list[AnnouncementBrief]


class AnnouncementDetailOut(BaseModel):
    """详情 view — 本文全文 + 回复列表。"""

    id: UUID
    title: str
    body: str
    scope: Literal["all", "male", "female"]
    author_teacher_id: UUID
    author_teacher_name: str
    created_at: datetime
    updated_at: datetime
    replies: list[AnnouncementReplyOut]


class AnnouncementCreateIn(BaseModel):
    """老师专用 — 发公告。"""

    title: str = Field(..., min_length=1, max_length=120)
    body: str = Field(..., min_length=1, max_length=4000)
    scope: Literal["all", "male", "female"]


class AnnouncementUpdateIn(BaseModel):
    """老师专用 — 编辑（title / body / scope 都可 partial update）。"""

    title: Optional[str] = Field(None, min_length=1, max_length=120)
    body: Optional[str] = Field(None, min_length=1, max_length=4000)
    scope: Optional[Literal["all", "male", "female"]] = None


class AnnouncementReplyCreateIn(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class AnnouncementUnreadCountOut(BaseModel):
    """主页 badge 用 — 当前学生 scope 内未读数。"""

    unread_count: int


# ---------------------------------------------------------------
# 扣分（spec §7.5 規律処分）— 5-27 凌晨新增
# ---------------------------------------------------------------
class DemeritEventOut(BaseModel):
    """单条扣分事件输出。"""

    id: UUID
    student_id: UUID
    source_type: Literal[
        "rollcall_late",
        "rollcall_absent",
        "cleaning_failed",
        "curfew_violation",
        "study_absent",
        "manual",
    ]
    source_event_id: Optional[UUID]
    points: float
    reason: str
    month: str
    created_at: datetime
    created_by_teacher_id: Optional[UUID]
    revoked_at: Optional[datetime]
    revoked_by_teacher_id: Optional[UUID]
    revoke_reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DemeritRankingEntryOut(BaseModel):
    """月排名一条 — 学生 + 累计扣分。"""

    student_id: UUID
    student_no: str
    name: str
    room_no: str
    dorm_unit: int
    total_points: float
    # 阈值标记 — itsuki 5-22 拍板 4 清扫 / 8 禁足
    is_cleaning_threshold: bool  # total_points >= 4
    is_curfew_threshold: bool  # total_points >= 8


class DemeritRankingOut(BaseModel):
    """月排名响应 — top N + 阈值学生列表。"""

    month: str
    entries: list[DemeritRankingEntryOut]
    cleaning_threshold_count: int  # >= 4 点的学生数
    curfew_threshold_count: int  # >= 8 点的学生数


class MyDisciplineSummaryOut(BaseModel):
    """当前登录学生的当月扣分汇总（iOS 当前用户统计用，IX-008b）。

    与 /ranking 同口径：只算当月（month == 当月 YYYY-MM）+ 排除已撤销。
    late_count / absent_count 只数点呼的遅刻 / 欠席（rollcall_late / rollcall_absent），
    不含扫除 / 门禁 / 晚自习等其它扣分来源。total_points 仍是当月全部来源之和。
    """

    month: str
    total_points: float
    late_count: int
    absent_count: int


class MyAbsenceSummaryOut(BaseModel):
    """当前登录学生的当月学習欠席届次数（iOS 当前用户统计用，IX-034）。

    口径：按 target_date（请假针对日）落在 JST 当月计数，数全部状态
    （pending / approved / rejected）—— 与 iOS 现有「提交即 +1」行为一致。
    学習欠席届无撤销机制（status 仅三态、无 withdrawn），故不排除任何状态。
    """

    month: str
    count: int


class DemeritManualIn(BaseModel):
    """手动加扣分输入（寮監权限）。"""

    student_id: UUID
    points: float = Field(..., gt=0, le=100)
    reason: str = Field(..., min_length=1, max_length=2000)


class DemeritRevokeIn(BaseModel):
    """撤销扣分输入。"""

    revoke_reason: str = Field(..., min_length=1, max_length=2000)


# ---------------------------------------------------------------
# 清扫安排（spec §7.10）— 5-27 凌晨新增
# ---------------------------------------------------------------
class CleaningAssignmentOut(BaseModel):
    id: UUID
    student_id: UUID
    area: str
    scheduled_date: date
    status: Literal["assigned", "done", "passed", "failed", "skipped"]
    assigned_by_teacher_id: Optional[UUID]
    assigned_at: datetime
    done_at: Optional[datetime]
    inspected_by_teacher_id: Optional[UUID]
    inspected_at: Optional[datetime]
    failure_reason: Optional[str]
    demerit_event_id: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class CleaningAssignmentCreateIn(BaseModel):
    """老师分配清扫输入。"""

    student_id: UUID
    area: Literal["浴室", "廊下", "トイレ", "共用キッチン", "階段", "玄関", "その他"]
    scheduled_date: date


class CleaningInspectIn(BaseModel):
    """老师审核输入 — passed / failed + 不通过原因。"""

    result: Literal["passed", "failed"]
    failure_reason: Optional[str] = Field(None, max_length=2000)


# ---------------------------------------------------------------
# 前台业务（spec §7.12 宅配 + 失物招领）— 5-27 凌晨新增
# ---------------------------------------------------------------
class FrontDeskItemOut(BaseModel):
    id: UUID
    kind: Literal["delivery", "lost_and_found"]
    student_id: Optional[UUID]
    description: str
    location: Optional[str]
    status: Literal["pending", "notified", "picked_up", "expired", "discarded"]
    created_by_teacher_id: UUID
    created_at: datetime
    notified_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FrontDeskItemCreateIn(BaseModel):
    """老师登记新条目输入。"""

    kind: Literal["delivery", "lost_and_found"]
    student_id: Optional[UUID] = None
    description: str = Field(..., min_length=1, max_length=2000)
    location: Optional[str] = Field(None, max_length=200)
    # 默认 expires_in_days: delivery=7 / lost_and_found=30（router 层应用）

    @model_validator(mode="after")
    def _delivery_requires_student(self):
        # 宅配(delivery)必须指定收件学生 —— 否则学生端 GET /mine 按 student_id 过滤永远查不到、
        # 登记成功但无人收到通知（codex 第三轮 major #2）。失物招领的 student_id 是捡到人、可空。
        if self.kind == "delivery" and self.student_id is None:
            raise ValueError("宅配は受取人（student_id）の指定が必須です")
        return self


# ---------------------------------------------------------------
# 学生账号管理（admin 端，spec §7.1）— 2026-05-30 实装
#   权威 spec：system_features.md §7.1
#   角色 gate：寮務部長 / 寮務課長 / 管理係（同注册码 ADMIN_ROLES）
# ---------------------------------------------------------------
class StudentAccountListItem(BaseModel):
    """GET /students 列表 — 每个学生一条。"""

    id: UUID
    student_no: str
    # 学号三段分量 — 老师网页按「年级 → A/B 班」分组折叠用（spec §4.2）
    grade_code: str
    class_code: str
    seat_no: str
    name: str
    room_no: str
    dorm_unit: int
    gender: Literal["male", "female"]
    status: str
    # 学年更新「待更新」标记 — 老师网页列表显示谁还没改番号（spec §4.2）
    needs_renewal: bool
    # Account.locked_until > now() = 被锁定（locked_until IS NULL 或 <= now = 未锁）
    is_locked: bool
    # Account.last_login_at（Account 表有该字段则返回）
    last_login_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class StudentAccountListOut(BaseModel):
    """GET /students 整体响应。"""

    total: int
    items: list[StudentAccountListItem]


class PasswordResetOut(BaseModel):
    """POST /accounts/{student_id}/password-reset 响应 — 临时密码明文（仅此一次）。"""

    student_id: UUID
    # 临时密码明文 — 仅此次响应返回，不存 DB 不记日志
    temporary_password: str
    message: str = "パスワードをリセットしました。学生に仮パスワードをお伝えください。"


class UnlockOut(BaseModel):
    """POST /accounts/{student_id}/unlock 响应。"""

    student_id: UUID


# ---------------------------------------------------------------
# 行事予定 (spec §7.5)
# ---------------------------------------------------------------
class DormEventCreateIn(BaseModel):
    """POST /events — 老师新建行事预定。"""

    title: str = Field(..., max_length=200)
    category: str = Field(..., description="学校行事 / 寮行事 / 外部 / その他")
    event_date: date
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=2000)


class DormEventPatchIn(BaseModel):
    """PATCH /events/{id} — 部分更新。"""

    title: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = None
    event_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=2000)


class DormEventOut(ORMModel):
    """行事预定响应体。"""

    id: UUID
    title: str
    category: str
    event_date: date
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    description: Optional[str]
    created_by_teacher_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]


class DormEventListOut(BaseModel):
    """GET /events 列表包装。"""

    items: list[DormEventOut]


# ---------------------------------------------------------------
# 巴士时刻表 (spec §7.6)
# ---------------------------------------------------------------
class BusRouteCreateIn(BaseModel):
    """POST /bus/routes — 老师新建巴士便。"""

    kind: str = Field(
        ..., description="daily_commute=平日通学便 / dorm_special=寮特殊便"
    )
    name: str = Field(..., max_length=200)
    direction: str = Field(..., max_length=200)
    schedule_at: datetime
    arrival_at: Optional[datetime] = None
    visible_to: str = Field(default="all", description="all / dorm_only / men / women")
    note: Optional[str] = Field(None, max_length=2000)


class BusRoutePatchIn(BaseModel):
    """PATCH /bus/routes/{id} — 部分更新。"""

    kind: Optional[str] = None
    name: Optional[str] = Field(None, max_length=200)
    direction: Optional[str] = Field(None, max_length=200)
    schedule_at: Optional[datetime] = None
    arrival_at: Optional[datetime] = None
    visible_to: Optional[str] = None
    note: Optional[str] = Field(None, max_length=2000)
    deprecated: Optional[bool] = None


class BusRouteOut(ORMModel):
    """巴士便响应体。"""

    id: UUID
    kind: str
    name: str
    direction: str
    schedule_at: datetime
    arrival_at: Optional[datetime]
    visible_to: str
    note: Optional[str]
    deprecated: bool
    created_by_teacher_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]


class BusRouteListOut(BaseModel):
    """GET /bus/routes 列表包装。"""

    items: list[BusRouteOut]


# ---------------------------------------------------------------
# 指導履歴（spec §7.9/§7.10）
# ---------------------------------------------------------------
class GuidanceRecordCreateIn(BaseModel):
    """老师录入指导记录。"""

    student_id: UUID
    content: str = Field(..., min_length=1, max_length=4000)
    category: Optional[str] = Field(None, max_length=100)
    guidance_date: date
    confidential: bool = True


class GuidanceRecordOut(ORMModel):
    id: UUID
    student_id: UUID
    teacher_id: UUID
    content: str
    category: Optional[str]
    guidance_date: date
    confidential: bool
    created_at: datetime
    deleted_at: Optional[datetime]


class GuidanceRecordListOut(BaseModel):
    items: list[GuidanceRecordOut]


class GuidanceDisclosureRequestIn(BaseModel):
    """学生提交开示申请（查看自己的指导履历）。"""

    reason: Optional[str] = Field(None, max_length=2000)


class GuidanceDisclosureDecisionIn(BaseModel):
    """老师决定开示申请。"""

    decision: Literal["approved_full", "approved_partial", "rejected"]
    decision_note: Optional[str] = Field(None, max_length=2000)
    # 部分开示时必填
    visible_from: Optional[date] = None
    visible_until: Optional[date] = None

    @model_validator(mode="after")
    def _check_partial(self) -> "GuidanceDisclosureDecisionIn":
        if self.decision == "approved_partial" and (
            self.visible_from is None or self.visible_until is None
        ):
            raise ValueError("部分开示时 visible_from / visible_until 必填")
        if (
            self.visible_from is not None
            and self.visible_until is not None
            and self.visible_until < self.visible_from
        ):
            raise ValueError("visible_until 不能早于 visible_from")
        return self


class GuidanceDisclosureRequestOut(ORMModel):
    id: UUID
    student_id: UUID
    student_no: str  # join Student 取学号（前端 DisclosureRequestsPage 显示用）
    reason: Optional[str]
    requested_at: datetime
    status: Literal["pending", "approved_full", "approved_partial", "rejected"]
    decided_by: Optional[UUID]
    decided_at: Optional[datetime]
    decision_note: Optional[str]
    visible_from: Optional[date]
    visible_until: Optional[date]
    revoked_at: Optional[datetime]

    @classmethod
    def from_row(cls, row: object) -> "GuidanceDisclosureRequestOut":
        """从 ORM row 构建，取 row.student.student_no。"""
        data = {c: getattr(row, c) for c in cls.model_fields if c != "student_no"}
        data["student_no"] = row.student.student_no  # type: ignore[union-attr]
        return cls(**data)


class GuidanceDisclosureListOut(BaseModel):
    items: list[GuidanceDisclosureRequestOut]


# ---------------------------------------------------------------
# 事案録入（spec §7.9 #33）
# ---------------------------------------------------------------
class IncidentRecordCreateIn(BaseModel):
    """老师录入事案。"""

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=100000)
    involved_student_ids: list[UUID] = Field(default_factory=list)
    incident_date: date


class IncidentRecordPatchIn(BaseModel):
    """老师编辑事案（部分更新）。"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1, max_length=100000)
    involved_student_ids: Optional[list[UUID]] = None
    incident_date: Optional[date] = None


class IncidentStudentBrief(BaseModel):
    """事案に関わった学生の最小情報（杭田 2026-06-04 五-6: 姓名タップで個人データへ）。"""

    id: UUID
    name: str


class IncidentRecordOut(ORMModel):
    id: UUID
    title: str
    body: str
    involved_student_ids: list[Any]
    # 杭田 2026-06-04 五-6: 涉及学生姓名（前端用来做可点击跳个人档案的 chip）
    involved_students: list[IncidentStudentBrief] = Field(default_factory=list)
    recorded_by: UUID
    incident_date: date
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


class IncidentRecordListOut(BaseModel):
    items: list[IncidentRecordOut]


# ---------------------------------------------------------------
# 学生个人档案聚合页（spec §7.10 #32）— 2026-05-30 实装
#   端点：GET /api/v1/students/{id}/profile
#   角色：寮務系老师（含指导履历块）/ 学生本人（指导履历返空，C 案）
# ---------------------------------------------------------------
class StudentProfileBasic(BaseModel):
    """学生基本信息块。"""

    id: UUID
    student_no: str
    name: str
    name_kana: Optional[str]
    grade_code: str
    class_code: str
    seat_no: str
    gender: str
    category: str  # 寮生类别（一般寮生 等）— iOS 当前用户显示用
    room_no: str
    dorm_unit: int
    is_overseas: bool
    email: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    status: str
    registered_at: datetime
    # 学年更新「待更新」标记 — True 时 iOS 顶部显示「更新番号」按钮（spec §4.2）
    needs_renewal: bool = False

    model_config = ConfigDict(from_attributes=True)


class ProfileApplicationEntry(BaseModel):
    """出寮届履历 — 列表 entry。"""

    id: UUID
    kind: Literal["帰省", "外泊", "帰国"]
    leave_date: date
    return_date: date
    status: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileStudyCheckinEntry(BaseModel):
    """学習出席記録 — 列表 entry。"""

    id: UUID
    target_date: date
    status: str  # init / present / late / absent / exempt
    checked_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ProfileRollCallEntry(BaseModel):
    """点呼记录 — 列表 entry。"""

    id: UUID
    session_id: UUID
    session_type: str  # morning / evening — 杭田 2026-06-04 五-5 要朝/夜分开
    base_status: str  # present / late / absent / exempt_range
    status_source: str
    checked_in_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileGuidanceEntry(BaseModel):
    """指導履歴 — 列表 entry（寮務系老师可见，学生本人返空）。"""

    id: UUID
    category: Optional[str]
    guidance_date: date
    confidential: bool
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileDemeritEntry(BaseModel):
    """扣分记录 — 列表 entry（仅未撤销）。"""

    id: UUID
    source_type: str
    points: float
    reason: str
    month: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileStudyOnlineEntry(BaseModel):
    """在线学习申请 — 列表 entry（含契約書文件信息，老师在学生个人页看历史合同用）。"""

    id: UUID
    period_from: date
    period_to: date
    status: str  # pending / approved / rejected / revoked
    submitted_at: datetime
    # 契約書文件信息 — 非空表示传过合同，点 GET /study/online-requests/{id}/contract 下载查看。
    contract_file_name: Optional[str]
    contract_mime: Optional[str]
    contract_size: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class StudentProfileOut(BaseModel):
    """GET /students/{id}/profile 聚合响应。"""

    student: StudentProfileBasic
    applications: list[ProfileApplicationEntry]
    study_checkins: list[ProfileStudyCheckinEntry]
    rollcall_events: list[ProfileRollCallEntry]
    # 寮務系老师 → 有数据；学生本人 → 空列表（C 案 §7.10）
    guidance_records: list[ProfileGuidanceEntry]
    demerit_events: list[ProfileDemeritEntry]
    # 在线学习申请履历（含契約書文件）— 老师点进学生个人页看历史上传的合同
    study_online_requests: list[ProfileStudyOnlineEntry]


# ---------------------------------------------------------------
# 学年更新 / 学生自设番号（spec §4.2）— 2026-06-05 学生自设方案（推翻 4-30 老师代改）
#   端点：
#     POST /api/v1/students/renewal-start            老师开闸（中1~高2 打 needs_renewal + 高3 毕业）
#     POST /api/v1/students/me/renew-number          学生自设番号（身份从令牌取，不信客户端）
#     GET  /api/v1/students/renewal-progress         老师看谁还没改
#     POST /api/v1/accounts/{student_id}/renew-seat  老师单件改番号（兜底）
#   角色 gate（老师侧）：寮務部長 / 寮務課長 / 管理係
# ---------------------------------------------------------------
class RenewalStartIn(BaseModel):
    """开闸输入。dry_run=True（默认）→ 只预览不写 DB；dry_run=False → 真执行。"""

    dry_run: bool = True


class RenewalStartEntry(BaseModel):
    """开闸预览/结果 — 单条学生。"""

    student_id: UUID
    student_no: str
    name: str
    grade_code: str
    # notify = 打「待更新」标记让学生自设番号；graduate = 高3 毕业离场
    action: Literal["notify", "graduate"]


class RenewalStartOut(BaseModel):
    """POST /students/renewal-start 响应。"""

    dry_run: bool
    notify_count: int  # 被打「待更新」标记的学生数（中1~高2）
    graduate_count: int  # 高3 → graduated 的学生数
    total_affected: int
    entries: list[RenewalStartEntry]


class StudentRenewNumberIn(BaseModel):
    """学生自设番号输入 — 身份从登录令牌取，请求体不含 student_id。"""

    grade_code: Annotated[str, Field(pattern=r"^\d{2}$")]
    class_code: Annotated[str, Field(pattern=r"^\d{2}$")]
    seat_no: Annotated[str, Field(pattern=r"^\d{2}$")]


class RenewalProgressItem(BaseModel):
    """进度 — 一个还没改番号的学生。"""

    id: UUID
    student_no: str
    name: str
    grade_code: str
    class_code: str
    seat_no: str

    model_config = ConfigDict(from_attributes=True)


class RenewalProgressOut(BaseModel):
    """GET /students/renewal-progress 响应 — 老师看谁还没改（needs_renewal=True）。"""

    pending_count: int  # 还没改的人数
    items: list[RenewalProgressItem]


class TeacherRenewSeatIn(BaseModel):
    """老师单件改某学生番号输入（兜底 — 学生不会操作 / 填错时）。"""

    grade_code: Annotated[str, Field(pattern=r"^\d{2}$")]
    class_code: Annotated[str, Field(pattern=r"^\d{2}$")]
    seat_no: Annotated[str, Field(pattern=r"^\d{2}$")]


# ---------------------------------------------------------------
# 推送令牌 — spec §7.13
# ---------------------------------------------------------------
class DeviceTokenRegisterIn(BaseModel):
    """POST /api/v1/notifications/device-token 请求体。"""

    platform: Literal["ios", "android"]
    token: str = Field(..., min_length=10, max_length=512)


class DeviceTokenRegisterOut(BaseModel):
    """POST /api/v1/notifications/device-token 响应。"""

    id: UUID
    student_id: UUID
    platform: str
    created: bool  # True = 新建, False = 幂等更新（已有 token 更新 last_seen_at）

    model_config = ConfigDict(from_attributes=True)
