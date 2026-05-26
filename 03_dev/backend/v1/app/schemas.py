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
    login_id: str = Field(..., max_length=32)
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
    """外泊届 (寮以外で泊まる)。+ 滞在先 + 食事不要リスト。"""

    kind: Literal["外泊"] = "外泊"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list)


class KikokuCreateIn(ApplicationBase):
    """帰国届 (国外帰省, 留学生がメイン)。+ 飛行機情報。"""

    kind: Literal["帰国"] = "帰国"
    stay_locations: list[StayLocation] = Field(..., min_length=1)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list)
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

    stay_locations: Optional[list[dict[str, Any]]] = None
    meals_skip: Optional[list[dict[str, Any]]] = None
    reason: Optional[str] = None

    flight_dep_air: Optional[str] = None
    flight_dep_at: Optional[datetime] = None
    flight_arr_air: Optional[str] = None
    flight_arr_at: Optional[datetime] = None

    bus_route_id: Optional[UUID] = None

    submitted_at: datetime
    status: Literal[
        "pending", "approved_partial", "approved", "rejected", "withdrawn", "returned"
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
    leave_date: Optional[date] = None
    leave_method: Optional[str] = Field(None, max_length=200)
    leave_time: Optional[time] = None
    return_date: Optional[date] = None
    return_method: Optional[str] = Field(None, max_length=200)
    return_time: Optional[time] = None
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
    password: str = Field(..., min_length=6, max_length=128)
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
    # spec §5.0：dorm_unit ↔ room_no 前缀一致（1/2 = M*** male，4 = W*** female）
    dorm_unit: int = Field(..., ge=1, le=4)
    is_overseas: bool = False
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=32)
    password: str = Field(..., min_length=6, max_length=128)
    # 老师在后台生成的 6 桁码（5 分钟内有效）
    registration_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


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


class DemeritManualIn(BaseModel):
    """手动加扣分输入（寮監权限）。"""

    student_id: UUID
    points: float = Field(..., gt=0, le=100)
    reason: str = Field(..., min_length=1, max_length=2000)


class DemeritRevokeIn(BaseModel):
    """撤销扣分输入。"""

    revoke_reason: str = Field(..., min_length=1, max_length=2000)
