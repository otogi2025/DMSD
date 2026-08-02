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


# C-14：教师职位 Literal — 9 个值必须与 models.TEACHER_ROLES 逐字一致。
# 用 Literal 而非裸 str，让非法 role 在请求解析阶段就被 422 拦下，
# 不再拖到 DB CHECK 约束才报 500。改动 TEACHER_ROLES 时本处需同步。
TeacherRoleLiteral = Literal[
    "校長",
    "寮務部長",
    "寮務課長",
    "国際交流部長",
    "国際交流課長",
    "管理係",
    "寮監",
    "学習担当",
    "寮務一般教師",
]

# codex-C-2：在线学习申请的周课表形状 — 与 iOS NetworkModels.swift 的
# [String: [[String: String]]] 一一对应（外层 dict 键=星期，内层 list 的每个
# dict 是一节课的字段）。输入侧 / 输出侧共用此别名，避免输出退化成 dict[str, Any]
# 导致 iOS 拿到非双层嵌套时解码炸。
WeeklyScheduleType = dict[str, list[dict[str, str]]]


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
    """学生登录：student_no 或 email 必须且只能传一个（对齐 TeacherLoginIn「至少传一个」口径，
    额外禁止两个都传，避免客户端歧义）。"""

    student_no: Optional[Annotated[str, Field(pattern=r"^\d{6}$")]] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6, max_length=128)

    @model_validator(mode="after")
    def _need_exactly_one_identifier(self) -> "StudentLoginIn":
        has_no = bool(self.student_no)
        has_email = bool(self.email)
        if not has_no and not has_email:
            raise ValueError("学号またはメールアドレスのいずれかを入力してください")
        if has_no and has_email:
            raise ValueError("学号とメールは同時に入力できません")
        return self


class TeacherLoginIn(BaseModel):
    """老师登录：login_id 或 teacher_id 至少传一个。
    2026-05-27 拍板「实名账户登录」方式：前端从 GET /teachers/public 拿 UUID（id）后用 teacher_id 登录，
    避免把 login_id 列表暴露给无认证爬虫（防止枚举攻击 + 针对性爆破）。
    原 login_id + password 形式保留作 backward-compat（CLI / 旧测试）。"""

    login_id: Optional[str] = Field(default=None, max_length=32)
    teacher_id: Optional[UUID] = None
    password: str = Field(..., min_length=6, max_length=128)
    # 登录时选今晚负责的寮：1=男子寮（→1+2 寮）/ 4=女子寮（→4 寮）。写进令牌驱动寮过滤
    # （deps.dorm_units_for_teacher）。op / 申請承認専用 组忽略本值、永远看全部。前端登录页
    # 除承認组外必选；不传（旧客户端 / 申請承認専用）则不限制、看全部（向后兼容）。
    selected_dorm: Optional[Literal[1, 4]] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class TeacherTokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    teacher: "TeacherOut"


class WSTicketOut(BaseModel):
    # 老师 WS 短时票据（60秒TTL，无单次消费机制）（C20）— 不把老师 JWT 放进 WS
    # 的 query 参数，改为换成 60 秒 TTL 的短时票据来握手（票据是无状态 JWT、不做
    # 单次消费，60 秒窗口内可重放，理由见 routers/ws.py teacher_ws 校验处）。
    ticket: str
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
    stay_locations: list[StayLocation] = Field(..., min_length=1, max_length=20)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list, max_length=200)
    companion: Optional[str] = Field(None, max_length=500)
    dest_cities: Optional[str] = Field(None, max_length=500)


class KikokuCreateIn(ApplicationBase):
    """帰国届 (国外帰省, 留学生がメイン)。+ 飛行機情報。"""

    kind: Literal["帰国"] = "帰国"
    stay_locations: list[StayLocation] = Field(..., min_length=1, max_length=20)
    meals_skip: list[MealSkipEntry] = Field(default_factory=list, max_length=200)
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

    # B-低-25：用结构化类型解码 DB JSON list，恢复字段校验（原 list[dict] 丢结构）。
    # 入库侧本就是 StayLocation/MealSkipEntry.model_dump() 写的，形状保证一致；
    # Pydantic v2 会把 dict 自动 coerce 回模型，meals_skip 的 date 字符串也会解析回 date。
    stay_locations: Optional[list[StayLocation]] = None
    meals_skip: Optional[list[MealSkipEntry]] = None
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


class OutingRejectIn(BaseModel):
    """PATCH /outings/{id}/reject — 老师却下外出申请（2026-07-22 事后确认制）。

    reason 可选：itsuki 拍板「老师填拒绝理由不强制」。填了就带进学生收到的通知正文。
    请求体整体也可省略（不传 body = 不填理由）。
    """

    reason: Optional[str] = Field(None, max_length=500)


class OutingOut(BaseModel):
    """外出申请查询返回。

    confirmed_by_teacher_id / confirmed_by_name / confirmed_at 是「処理した先生」——
    status=approved 时是确认者、status=rejected 时是却下者（2026-07-22 事后确认制起共用），
    客户端显示文案要按 status 分支，不能一律写「確認 · ○○ 先生」。
    reject_reason 只在 status=rejected 时可能有值（老师没填理由时仍为 null）。
    """

    id: UUID
    student_id: UUID
    student: Optional[StudentBrief] = None
    outing_date: date
    destination: Optional[str] = None
    leave_time: Optional[time] = None
    return_time: Optional[time] = None
    taxi_reservation_time: Optional[time] = None
    reason: Optional[str] = None
    status: Literal["pending", "approved", "rejected", "withdrawn"]
    submitted_at: datetime
    withdrawn_at: Optional[datetime] = None
    confirmed_by_teacher_id: Optional[UUID] = None
    confirmed_by_name: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    reject_reason: Optional[str] = None

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

    @model_validator(mode="after")
    def _check_to(self) -> "MealsExportQuery":
        # B-低-24：改用 after 校验器 — 只在 from_ / to 两个字段都成功解析后才跑，
        # 不再依赖 info.data['from_'] 是否存在（from 解析失败时不会静默跳过区间校验，
        # 而是 from 字段先各自报 422）。
        if self.to < self.from_:
            raise ValueError("to must be on or after from")
        return self


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


class ApplicationReturnIn(BaseModel):
    """POST /applications/:id/return — 役職が学生に差戻(再提出を求める)。"""

    # 差戻理由必填 — 学生要知道改哪里。写进 audit + pending 承認行 comment 给学生看。
    comment: str = Field(..., min_length=1, max_length=1000)


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
    # 'expected' | 'exempted_outstay' | 'exempted_online' | 'exempted_absence' | 'exempted_cancel'
    expected_status: str
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
    # 学生摘要 — 老师欠席届列表用（原来只回 student_id，老师无法辨认「谁请哪天假」
    # 就能点承認/却下）。老师端点填充；学生自查等场景保持 None
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    room_no: Optional[str] = None

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
    weekly_schedule: WeeklyScheduleType
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
    # codex-C-2：与输入侧同形 — 强类型双层嵌套，对齐 iOS [String: [[String: String]]]
    weekly_schedule: WeeklyScheduleType
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
    # 学生摘要 — 老师在线学习申请列表用（原来只回 student_id，老师无法辨认「谁申请
    # 哪段在线学习」就能点承認/却下）。老师端点填充；学生自查等场景保持 None
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    room_no: Optional[str] = None

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


class RollCallSessionHistoryOut(RollCallSessionOut):
    """点呼履歴一覧（老师网页 RecordsPage）用 —— 在场次基础信息上附本场出席统计。

    present_count / late_count / absent_count 按 latest-per-student 聚合。原 list 端点
    返回纯 RollCallSessionOut（无这三个计数），前端读 present_count 等永远取不到、
    历史页三列恒显「—」，历史出勤回看功能实际不可用（TW-040）。
    """

    present_count: int = 0
    late_count: int = 0
    absent_count: int = 0


class MyRollCallTodaySession(BaseModel):
    """学生端「今日の自分の点呼」— GET /rollcall/me/today 的单条。

    = 今天我所属寮的一个点呼场次 + 我在该场的签到状态。
    iOS 用它真实算出 idle / 进行中倒计时 / 時間内 / 遅刻，不再本地写死。
    """

    session_id: UUID
    session_type: str  # morning / evening
    day_type: str  # weekday / weekend_holiday
    session_status: str  # draft / running / ended
    scheduled_window_start_at: datetime
    scheduled_on_time_end_at: datetime
    scheduled_late_end_at: datetime
    scheduled_auto_end_at: datetime
    # 我在该场的签到判定：present/late/absent/exempt_range/init；None = 还没签到
    my_status: Optional[str] = None
    my_checked_in_at: Optional[datetime] = None


class RollCallCheckinIn(BaseModel):
    """POST /rollcall/sessions/:id/checkins — NFC or 手動点呼。

    2026-05-21 加 path_hint（A-020）：client 显式标路径，backend 校验字段一致性。
    避免「同时有 card_uid + idempotency_key 时 backend 推断错路径」。
    """

    # 与 DeviceCheckinIn / NfcCardCreateIn 对齐：卡 UID 固定 14 字符，非法长度 422
    card_uid: Optional[str] = Field(None, min_length=14, max_length=14)  # 路径 A
    student_id: Optional[UUID] = None  # 路径 B / 手動
    idempotency_key: Optional[str] = Field(None, max_length=64)  # 路径 B
    # 审查 backend#6：只留两个「真实签到」值 —— auto_settle 只能由结算写入、
    # teacher_override 只能走 PATCH /events，客户端自选这俩会污染审计口径，
    # schema 层直接 422。落库值服务端按路径推导（router 不信本字段），字段保留
    # 仅为接口兼容。model 层 CheckConstraint 仍是 4 值（内部写入者用）。
    status_source: Literal["auto_nfc", "manual_checkin"] = "auto_nfc"
    # 已不参与判定（7-06 拍板 server_now，见 API_CONVENTIONS §4）——判定/落库/广播时刻恒取
    # 服务器收到请求的时刻。字段保留仅为接口兼容（旧 client 仍会上送，backend 静默忽略）。
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
# 点呼机接入（device）— Device_Contract §2/§4
# ---------------------------------------------------------------
class DeviceCreateIn(BaseModel):
    """POST /devices — 管理员创建设备记录（Device_Contract §2.2）。"""

    device_id: str = Field(..., min_length=1, max_length=64)
    device_type: Literal["card_reader", "iphone_tag", "hybrid"]
    device_location: str = Field(..., min_length=1, max_length=200)
    device_notes: Optional[str] = Field(None, max_length=500)


class DeviceCreateOut(BaseModel):
    """创建设备的响应 — enroll_code 明文仅此一次返回，后端只存哈希。"""

    device_id: str
    device_type: str
    device_location: str
    device_notes: Optional[str]
    enroll_code: str
    device_active: bool


class DeviceOut(BaseModel):
    """GET /devices 列表项 / PATCH 响应 — 不含 enroll_code / 哈希 / 公钥。"""

    device_id: str
    device_type: str
    device_location: str
    device_notes: Optional[str]
    device_active: bool
    enrolled_at: Optional[datetime]
    retired_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    fw_version: Optional[str]
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DevicePatchIn(BaseModel):
    """PATCH /devices/{device_id} — 临时停用/恢复 toggle + 永久注销。"""

    device_active: Optional[bool] = None
    # True = 永久注销（retired_at=now + device_active=false，之后禁止再激活；DEVICE_REGISTRY §5.2）
    retire: Optional[bool] = None


class DeviceResetEnrollOut(BaseModel):
    """POST /devices/{device_id}/reset-enroll 响应 — 重发激活码（明文仅此一次）。"""

    device_id: str
    enroll_code: str


class DeviceEnrollIn(BaseModel):
    """POST /devices/{device_id}/enroll — 设备首启自助激活（Device_Contract §2.2）。"""

    enroll_code: str = Field(..., min_length=1, max_length=128)
    # Ed25519 公钥 = base64 原始 32 字节
    public_key: str = Field(..., min_length=1, max_length=128)


class DeviceEnrollOut(BaseModel):
    device_id: str
    enrolled_at: datetime


class DeviceTokenIn(BaseModel):
    """POST /devices/{device_id}/token — 挑战签名换令牌（Device_Contract §2.3）。

    ts 保持 str（不解析成 datetime）— 验签用的是设备逐字节签名的原始串，
    必须原样喂进 "{device_id}\\n{ts}\\n{nonce}"，不能被序列化改写。
    """

    ts: str = Field(..., min_length=1, max_length=64)
    nonce: str = Field(..., min_length=1, max_length=64)
    signature: str = Field(..., min_length=1, max_length=128)


class DeviceTokenOut(BaseModel):
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"


class DeviceHeartbeatIn(BaseModel):
    """POST /devices/me/heartbeat — WS 不可用时的兜底心跳通道。"""

    fw_version: Optional[str] = Field(None, max_length=32)


class DeviceCheckinIn(BaseModel):
    """POST /rollcall/device-checkins — 点呼机核心签到入口（Device_Contract §4.1）。"""

    path_type: Literal["A", "B"]
    card_uid: Optional[str] = Field(None, max_length=14)  # 路径 A
    student_id: Optional[UUID] = None  # 路径 B
    idempotency_key: Optional[UUID] = None  # 路径 B
    # 设备 NTP 校准盖章时刻（判定基准，Device_Contract §3）
    swipe_time: datetime


class DeviceCheckinOut(BaseModel):
    """签到响应 data（Device_Contract §4.1）。"""

    student_id: UUID
    student_number: str
    student_name: str
    base_status: str  # present / late
    session_id: UUID
    duplicate: bool
    led: str  # green / yellow / red
    audio_file: str
    broadcast_text: str
    # 离线补传冲突：命中老师改判 → true（设备丢弃、绿灯不重播；Device_Contract §6）
    superseded_by_teacher: bool = False


class NfcCardCreateIn(BaseModel):
    """POST /cards — 绑卡（Device_Contract §5）。"""

    card_uid: str = Field(..., min_length=14, max_length=14)
    student_id: UUID


class NfcCardRevokeIn(BaseModel):
    """DELETE /cards/{card_uid} 可选正文 — 作废理由。"""

    revoke_reason: Optional[str] = Field(None, max_length=200)


class NfcCardOut(BaseModel):
    card_uid: str
    student_id: UUID
    card_active: bool
    issued_at: datetime
    revoked_at: Optional[datetime]
    revoke_reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DeviceRosterStudentOut(BaseModel):
    student_id: UUID
    student_number: str
    name: str
    card_uids: list[str]


class DeviceRosterOut(BaseModel):
    """GET /devices/me/roster — 离线兜底名单（Device_Contract §4.2）。"""

    generated_at: datetime
    students: list[DeviceRosterStudentOut]


class DeviceAudioFileOut(BaseModel):
    name: str
    sha256: str
    size: int


class DeviceAudioManifestOut(BaseModel):
    """GET /devices/me/audio-manifest（Device_Contract §4.3）。"""

    files: list[DeviceAudioFileOut]


# ---------------------------------------------------------------
# 教師管理 (Teacher Invitation — §3.4)
# ---------------------------------------------------------------
class TeacherInvitationIn(BaseModel):
    target_email: EmailStr
    # C-14：限定为 TEACHER_ROLES 9 值，非法 role 在解析阶段 422 而非 DB CHECK 500
    target_role: TeacherRoleLiteral
    # 限定为 1/2/4（与 dorm_unit 一致）— 非法寮号（3/99 等）在解析阶段 422，
    # 否则落到 register_teacher 建老师时撞 ck_teachers_dorm CHECK → 不透明 500。
    target_dorm: Optional[Literal[1, 2, 4]] = None


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
    # 权限组（teacher_permission_v1.md §3）— 决定该账号每个功能簇的权限级别；
    # NULL = 还没显式配组（鉴权时按职位回退默认组，见 app/permissions.py）。
    permission_group: Optional[str] = None
    assigned_dorm: Optional[int]
    status: str
    created_at: datetime
    # 临时账户到期时间（NULL = 永久正式账户）— 老师账户管理页显示「臨時 · 期限…」用
    expires_at: Optional[datetime] = None
    # 演示账号标志 —— 前端据此决定给不给看演示内容（itsuki 7-17 决策 5：
    # demo 账户显示演示数据、真账户显示真数据或「準備中」，两者共存）。
    # 只是显示开关，不承担隔离职责 —— 真正的数据隔离在后端（真老师查不到 is_demo 学生）。
    is_demo: bool = False

    model_config = ConfigDict(from_attributes=True)


class TeacherPublicOut(BaseModel):
    """GET /teachers/public — 登录页第 1 屏用，无认证可见。
    只暴露 id + name + assigned_dorm + last_login_at — 不暴露 login_id / email / role / status / failed_count（防爬虫枚举）。
    last_login_at 由前端转「N 分前 / 本日未 / 初回」显示。"""

    id: UUID
    name: str
    assigned_dorm: Optional[int]
    last_login_at: Optional[datetime]
    # 有效权限组（已按职位回退）— 登录页按权限组分栏用。注：方案 B 登录页本就
    # 公开展示老师卡片，权限组属半公开信息（仍不暴露 login_id/email/role）。
    permission_group: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeacherCreateIn(BaseModel):
    """POST /teachers — 已登录教师 + 寮務管理权限 → 直接创建新教师（v1.0 简化版，跳过邀请码流程）。
    邀请码流程（POST /teachers/invitations + /register）保留 backend 但 v1.0 web 不实装 UI。"""

    login_id: str = Field(..., min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    # 对齐 TeacherRegisterIn 的长度约束 —— name 落库要有上界（防超长串撑变 UI / 占库），
    # password 上界防超大字符串占请求体（bcrypt 截断风险已被 security._prep 的 SHA256 化解）。
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    # C-14：职位标签（仅显示，不参与鉴权）— 限定为 TEACHER_ROLES 9 值
    role: TeacherRoleLiteral
    # 权限组（teacher_permission_v1.md §3）— 决定该账号功能权限；省略则建账号后按职位回退默认组。
    permission_group: Optional[str] = None
    # 限定为 1/2/4（与 dorm_unit 一致）— 非法寮号在解析阶段 422，
    # 否则 create_teacher 落库撞 ck_teachers_dorm CHECK，IntegrityError 被误报成 DUPLICATE。
    assigned_dorm: Optional[Literal[1, 2, 4]] = None
    # 临时账户到期时间（NULL = 永久正式账户）。有值 = 临时账户：到期后登录被拒。
    # 临时账户 assigned_dorm 一般留空（登录时选寮），功能组走 permission_group。
    expires_at: Optional[datetime] = None


# ---------------------------------------------------------------
# 学生注册码（Student Registration Code）
#   权威 spec：system_features §7.16 + BACKEND §4.10 + §5.1.5（2026-05-03 拍板）
# ---------------------------------------------------------------
class RegistrationCodeOut(BaseModel):
    """GET/POST registration-code/* 通用响应。"""

    # C-13：与输入侧 ^\d{6}$ 对齐 — 响应码也是纯 6 位数字
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
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
    # min_length=2：2 寮房号最短是 A1〜A9（A + 1 位 = 2 字符，§5.0）；旧 min_length=3 会把
    # A1〜A9 全部挡在 schema 校验外，2 寮学生无法注册。精确格式（M***/A*/W***）由
    # accounts.validate_room_dorm_match 按 dorm_unit 用与 DB CHECK 同源的正则把关。
    room_no: str = Field(..., min_length=2, max_length=8)
    # spec §5.0：寮号只有 1/2（男寮）、4（女寮）— 没有 3，与 models.py CHECK 约束对齐
    # B10：原来 ge=1, le=4 允许 3，DB CHECK 只接受 1/2/4，改为 Literal 精确限定
    dorm_unit: Literal[1, 2, 4]
    is_overseas: bool = False
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=32)
    # min_length=6 对齐 iOS 学生注册本地校验（itsuki 2026-06-14 上架拍板；老师注册密码仍 8 位不降）
    password: str = Field(..., min_length=6, max_length=128)
    # 老师在后台生成的 6 桁码（默认 5 分钟内有效，与 models StudentRegistrationCode TTL 一致）
    registration_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

    # B10：dorm_unit 的 3 由 Literal[1,2,4] 拦下，无需额外校验器。
    # C-8（房号前缀 ↔ dorm_unit/gender 交叉校验）不在本 schema 做 —— accounts.py 的
    # validate_room_dorm_match 已在 router 层校验并返回结构化 422 INVALID_ROOM_FORMAT
    # （见 test_registration_code.py::test_create_account_room_dorm_mismatch）。改成 schema 层
    # ValueError 会让该错误退化成 Pydantic 列表式 422、破坏既有错误契约，故 C-8 判定为误报不改。


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
    # 投稿时勾选「学生に通知する」→ True 才进学生通知 feed + 推送（§7.13.1）
    notify_students: bool = False


class AnnouncementUpdateIn(BaseModel):
    """老师专用 — 编辑（title / body / scope 都可 partial update）。"""

    title: Optional[str] = Field(None, min_length=1, max_length=120)
    body: Optional[str] = Field(None, min_length=1, max_length=4000)
    scope: Optional[Literal["all", "male", "female"]] = None
    # 编辑时勾选「学生に通知する」(True) → 重新推送 + 进 feed；None/False = 不动通知状态（§7.13.1）
    notify_students: Optional[bool] = None


class AnnouncementReplyCreateIn(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class AnnouncementUnreadCountOut(BaseModel):
    """主页 badge 用 — 当前学生 scope 内未读数。"""

    unread_count: int


# ---------------------------------------------------------------
# 学生通知中心 feed（§7.13.1 — 老师勾选「通知」的 公告/巴士/行事 聚合）
# ---------------------------------------------------------------
class StudentNotificationItem(BaseModel):
    """一条学生通知 = 某条 公告/巴士/行事（老师投稿时勾了「通知」）。"""

    kind: Literal["announcement", "bus", "event"]
    ref_id: UUID  # 对应 announcements / bus_routes / dorm_events 的 id（点击跳转用）
    title: str
    body: str  # 摘要
    created_at: datetime
    is_read: bool


class StudentNotificationFeedOut(BaseModel):
    items: list[StudentNotificationItem]
    unread_count: int  # 三类未读合计 — 驱动 app 铃铛 badge


class StudentNotificationReadIn(BaseModel):
    """标记某条学生通知已读。"""

    kind: Literal["announcement", "bus", "event"]
    ref_id: UUID


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
    # 阈值标记 — 4 清扫罚扫 / 8 禁足（2026-06-15 罚扫重做恢复 4 分阈值）
    is_cleaning_threshold: bool  # total_points >= 4
    is_curfew_threshold: bool  # total_points >= 8


class DemeritRankingOut(BaseModel):
    """月排名响应 — top N + 阈值学生列表。"""

    month: str
    entries: list[DemeritRankingEntryOut]
    cleaning_threshold_count: int  # >= 4 点的学生数（需要罚扫）
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
    # ≥4 分 → 需要罚扫（后端纯阈值 total_points>=CLEANING_THRESHOLD；
    # 前端按 4-7 罚扫 / ≥8 外出禁止分档显示，到 8 分不再标罚扫）
    needs_cleaning: bool


class MyAbsenceSummaryOut(BaseModel):
    """当前登录学生的当月学習欠席届次数（iOS 当前用户统计用，IX-034）。

    口径：按 target_date（请假针对日）落在 JST 当月计数，数全部状态
    （pending / approved / rejected）—— 与 iOS 现有「提交即 +1」行为一致。
    学習欠席届无撤销机制（status 仅三态、无 withdrawn），故不排除任何状态。
    """

    month: str
    count: int


class DemeritManualIn(BaseModel):
    """手动设定学生本月扣分总分输入（寮監权限）。

    B 方案（itsuki 2026-06-15 拍板）：老师输入目标绝对分 target_points，后端算
    「目标 − 当前本月总分」的差值，记一条调整事件（可正可负）使该学生本月总分等于
    target_points。不是加 / 减一个增量。target_points 取值 0~100（0 = 清零本月扣分）。
    """

    student_id: UUID
    target_points: float = Field(..., ge=0, le=100)
    reason: str = Field(..., min_length=1, max_length=2000)
    # 幂等键（A-473）—— 客户端每次「加扣分」点击生成一个 UUID 随请求带上，
    # 老师双击 / 网络重试时同一个 key 会被后端识别为重复提交、不再叠加第二条扣分。
    # 可空：不传时退回原行为（不去重），保持对老客户端兼容。
    idempotency_key: Optional[UUID] = None
    # 乐观锁：老师提交前核对到的「当前本月总分」。后端在行锁内比对，不一致则 409
    # POINTS_CHANGED，避免 GET→POST 空档里自动扣分被静默抵消。可空 = 老客户端行为不变。
    expected_current_points: float | None = None


class DemeritRevokeIn(BaseModel):
    """撤销扣分输入。"""

    revoke_reason: str = Field(..., min_length=1, max_length=2000)


# ---------------------------------------------------------------
# 清扫安排（罚则清扫）— spec §7.10 清扫审查 / 2026-06-15 罚扫功能重做
# ---------------------------------------------------------------
class CleaningAssignmentOut(BaseModel):
    """清扫安排输出（老师列表 + 学生履历共用）。"""

    id: UUID
    student_id: UUID
    area: str
    scheduled_at: datetime
    status: Literal["assigned", "done", "passed", "failed", "skipped"]
    assigned_by_teacher_id: Optional[UUID]
    assigned_at: datetime
    done_at: Optional[datetime]
    inspected_by_teacher_id: Optional[UUID]
    inspected_at: Optional[datetime]
    failure_reason: Optional[str]
    demerit_event_id: Optional[UUID]
    # 学生摘要 — 老师列表用（原来卡片只能显 UUID 前 8 位，老师认不出是谁）。
    # 仅老师列表端点填充；学生 /me 自查保持 None（本人不需要）
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    room_no: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CleaningAssignmentCreateIn(BaseModel):
    """老师分配清扫输入。area 自由文本，scheduled_at 带时区 datetime。"""

    student_id: UUID
    # 地点自由文本（旧版是 7 选 1 Literal 枚举，重做去枚举）
    area: str = Field(..., min_length=1, max_length=32)
    # 计划执行时刻（带时区 datetime，精确到几点）
    scheduled_at: datetime


class CleaningInspectIn(BaseModel):
    """老师审核输入 — passed 通过 / failed 不通过 + 不通过原因。"""

    result: Literal["passed", "failed"]
    failure_reason: Optional[str] = Field(None, max_length=2000)


# ---------------------------------------------------------------
# 点呼时学生上报（体调 / 当次缺席 / 其他问题）— IX iOS 点呼弹窗接真后端
# ---------------------------------------------------------------
class RollCallReportCreateIn(BaseModel):
    """学生点呼上报输入。kind 对应 iOS 三个弹窗，body 是学生填写的正文。"""

    kind: Literal["health", "absence", "other"]
    body: str = Field(min_length=1, max_length=2000)
    session_id: Optional[UUID] = None  # 关联当次点呼场次（可空）


class RollCallReportOut(BaseModel):
    id: UUID
    student_id: UUID
    session_id: Optional[UUID]
    kind: Literal["health", "absence", "other"]
    body: str
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by_teacher_id: Optional[UUID]
    # 学生摘要 — 老师上报列表用（原来只回 student_id，老师认不出「谁上报了体调不适」就没法
    # 处理）。老师端点 list_rollcall_reports 填充；学生自查 /reports/mine 保持 None
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    room_no: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 点歌（UI「リクエスト曲」）最小版 — IX iOS 社区功能接真后端
# ---------------------------------------------------------------
class SongRequestCreateIn(BaseModel):
    """学生点歌投稿输入。dorm_unit 后端从登录学生自动取，不收客户端。"""

    song_title: str = Field(min_length=1, max_length=200)
    artist: Optional[str] = Field(None, max_length=200)
    note: Optional[str] = Field(None, max_length=500)


class SongRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    dorm_unit: int
    song_title: str
    artist: Optional[str]
    note: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 遗失物社区投稿 — IX iOS 社区功能接真后端
# ---------------------------------------------------------------
class LostFoundCreateIn(BaseModel):
    """学生遗失物投稿输入（捡到 found / 丢了 lost）。"""

    post_type: Literal["found", "lost"]
    item_name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=200)


class LostFoundOut(BaseModel):
    id: UUID
    student_id: UUID
    post_type: Literal["found", "lost"]
    item_name: str
    description: Optional[str]
    location: Optional[str]
    status: Literal["open", "resolved"]
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 投稿通報（App Store UGC 治理 — itsuki 2026-07-20 拍板 A 方案）
# ---------------------------------------------------------------
class ContentReportCreateIn(BaseModel):
    """学生通報投稿输入。content_id 指向被通報的投稿。"""

    content_type: Literal["song", "announcement_reply", "lost_found"]
    content_id: UUID
    reason: Optional[str] = Field(None, max_length=500)


class ContentReportOut(BaseModel):
    id: UUID
    content_type: Literal["song", "announcement_reply", "lost_found"]
    content_id: UUID
    reporter_student_id: UUID
    reason: Optional[str]
    status: Literal["open", "handled"]
    created_at: datetime
    handled_at: Optional[datetime]
    handled_by_teacher_id: Optional[UUID]
    # 老师一覧用：被通報投稿的内容摘要（歌名 / 回复正文前 80 字等）；投稿已被删则为 None
    content_preview: Optional[str] = None
    # 老师一覧用：公告回复的父公告 id（删回复接口要 announcement_id + reply_id 两段路径）；其他类型 None
    content_parent_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 杂项申请（修繕 / 来訪者 / 代理受取）— IX iOS 申请页接真后端
# ---------------------------------------------------------------
class MiscRequestCreateIn(BaseModel):
    """学生杂项申请输入。"""

    kind: Literal["repair", "guest", "proxy_receipt"]
    subject: str = Field(min_length=1, max_length=200)
    detail: Optional[str] = Field(None, max_length=2000)
    target_date: Optional[date] = None


class MiscRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    kind: Literal["repair", "guest", "proxy_receipt"]
    subject: str
    detail: Optional[str]
    target_date: Optional[date]
    status: Literal["pending", "confirmed", "withdrawn"]
    created_at: datetime
    confirmed_by_teacher_id: Optional[UUID]
    confirmed_at: Optional[datetime]
    withdrawn_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# 前台业务（spec §7.12 宅配 + 失物招领）— 5-27 凌晨新增
# ---------------------------------------------------------------
class FrontDeskStudentBrief(BaseModel):
    """前台登记宅配时挑收件学生用的最小字段（不含账号锁定 / 登录等敏感信息）。

    与「学生账号管理」的 StudentAccountListItem 区别：本类权限更宽（含寮監，能登记宅配的角色都能搜），
    但只暴露挑人需要的字段，故单独定义、不复用账号管理那套。
    """

    id: UUID
    name: str
    room_no: str
    student_no: str  # grade_code + class_code + seat_no 拼接
    dorm_unit: int


class FrontDeskItemOut(BaseModel):
    id: UUID
    kind: Literal["delivery", "lost_and_found"]
    student_id: Optional[UUID]
    description: str
    location: Optional[str]
    item_count: int  # 宅配件数（delivery）；lost_and_found 恒为 1
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
    # description 必填性按 kind 区分（见 _lost_and_found_requires_description）：
    # 失物招领=物品说明、必填；宅配=可选备注、可空（router 落库时缺省存空串，DB 列仍 NOT NULL）。
    description: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=200)
    # 宅配件数（delivery 用，老师登记几件）；lost_and_found 忽略、恒为 1。默认 1、下限 1、
    # 上限 999（一次宅配登记不会几百件以上，封死写入荒谬大数值撑坏前台板）。
    item_count: int = Field(1, ge=1, le=999)
    # 默认 expires_in_days: delivery=7 / lost_and_found=30（router 层应用）

    @field_validator("student_id", mode="before")
    @classmethod
    def _blank_student_id_to_none(cls, v):
        # 老师网页表单留空常发空字符串 / 纯空白而非 null —— 先归一成 None，
        # 否则 Optional[UUID] 解析空串直接 422：失物招领本应允许空、宅配也拿不到下面那条清晰报错
        # （codex 第四轮 major #1）。
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("description", mode="before")
    @classmethod
    def _blank_description_to_none(cls, v):
        # 表单留空 / 纯空白 → 归一成 None，便于下面按 kind 校验（失物纯空白也算没填）。
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @model_validator(mode="after")
    def _delivery_requires_student(self):
        # 宅配(delivery)必须指定收件学生 —— 否则学生端 GET /mine 按 student_id 过滤永远查不到、
        # 登记成功但无人收到通知（codex 第三轮 major #2）。失物招领的 student_id 是捡到人、可空。
        if self.kind == "delivery" and self.student_id is None:
            raise ValueError("宅配は受取人（student_id）の指定が必須です")
        return self

    @model_validator(mode="after")
    def _lost_and_found_requires_description(self):
        # 失物招领必须有物品说明（description）；宅配的 description 只是可选备注。
        # 配合 6-14 改造：宅配弹窗去掉「配送業者」、备注改可选。
        if self.kind == "lost_and_found" and not self.description:
            raise ValueError("失物招领は物品の説明（description）が必須です")
        return self


# ---------------------------------------------------------------
# 学生账号管理（admin 端，spec §7.1）— 2026-05-30 实装
#   权威 spec：system_features.md §7.1
#   角色 gate：寮務部長 / 寮務課長 / 管理係
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
    # 投稿时勾选「学生に通知する」→ True 才进学生通知 feed + 推送（§7.13.1）
    notify_students: bool = False


class DormEventPatchIn(BaseModel):
    """PATCH /events/{id} — 部分更新。"""

    title: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = None
    event_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=2000)
    # 编辑时勾选「学生に通知する」(True) → 重新推送 + 进 feed（§7.13.1）
    notify_students: Optional[bool] = None


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
    """POST /bus/routes — 老师新建巴士便。

    kind / name 改为可选（2026-06-15 表单去掉「種別」「便名」两栏）：
    - kind 缺省 → 路由侧默认 dorm_special（寮特殊便）；旧数据 / 显式传值仍兼容。
    - name 缺省 → 路由侧用 direction（区间）回填（DB 列仍 NOT NULL）。
    """

    kind: Optional[str] = Field(
        None,
        description="daily_commute=平日通学便 / dorm_special=寮特殊便（缺省=寮特殊便）",
    )
    name: Optional[str] = Field(None, max_length=200)
    direction: str = Field(..., max_length=200)
    schedule_at: datetime
    arrival_at: Optional[datetime] = None
    visible_to: str = Field(default="all", description="all / dorm_only / men / women")
    note: Optional[str] = Field(None, max_length=2000)
    purpose: Optional[str] = Field(
        None, max_length=2000, description="用途说明，学生端右上角展示"
    )
    # 投稿时勾选「学生に通知する」→ True 才进学生通知 feed + 推送（§7.13.1）
    notify_students: bool = False


class BusRoutePatchIn(BaseModel):
    """PATCH /bus/routes/{id} — 部分更新。"""

    kind: Optional[str] = None
    name: Optional[str] = Field(None, max_length=200)
    direction: Optional[str] = Field(None, max_length=200)
    schedule_at: Optional[datetime] = None
    arrival_at: Optional[datetime] = None
    visible_to: Optional[str] = None
    note: Optional[str] = Field(None, max_length=2000)
    purpose: Optional[str] = Field(None, max_length=2000)
    deprecated: Optional[bool] = None
    # 编辑时勾选「学生に通知する」(True) → 重新推送 + 进 feed（§7.13.1）
    notify_students: Optional[bool] = None


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
    purpose: Optional[str]
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


# ---------------------------------------------------------------
# 事案録入（spec §7.9 #33）
# ---------------------------------------------------------------
class IncidentRecordCreateIn(BaseModel):
    """老师录入事案。"""

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=100000)
    # 上限 200：一个事案涉及人数有现实上界。无上限时巨型数组会在 router 里逐个 db.get
    # 校验、放大成大量单行查询（认证后轻度 DoS）。
    involved_student_ids: list[UUID] = Field(default_factory=list, max_length=200)
    incident_date: date


class IncidentRecordPatchIn(BaseModel):
    """老师编辑事案（部分更新）。"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1, max_length=100000)
    involved_student_ids: Optional[list[UUID]] = Field(None, max_length=200)
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


class StudentSelfUpdateIn(BaseModel):
    """学生自己改个人信息（iOS マイページ「連絡先・部屋編集」用）。

    只开放低风险字段：email / phone / avatar_url / room_no。
    PATCH 语义 — 只更新「显式传了」的字段（exclude_unset），没传的不动。
    番号 / 姓名 / 性别 / 寮 / 类别 不可自助改：番号走 renew-number 流程，
    换寮 / 改名等敏感操作归老师。room_no 后端会校验前缀与本人 dorm_unit 一致
    （M*** + 男寮 1|2 / W*** + 女寮 4），防换到异性寮 / 错号段。
    """

    # EmailStr：非法格式在 schema 层 422；空串 before 归一成 None（审查 backend#42）
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    room_no: Optional[str] = Field(None, max_length=8)

    @field_validator("email", mode="before")
    @classmethod
    def _blank_email_to_none(cls, v):
        # 空串 / 纯空白 → None，避免写成空串绕过查重、也让「清空邮箱」语义落到 NULL
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


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
    base_status: str  # init / present / late / absent / exempt_range（与 models RollCallEvent CHECK 一致）
    status_source: str
    checked_in_at: datetime
    # R-1③：该场次的窗口时刻（join session 得），iOS 履历详情显真实開始/締切，不再写死 07:00/21:00
    scheduled_window_start_at: Optional[datetime] = None
    scheduled_on_time_end_at: Optional[datetime] = None

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


# ---------------------------------------------------------------
# 老师通知中心（UI「通知センター」）— 阶段1
# ---------------------------------------------------------------
class NotificationItem(ORMModel):
    """通知中心的一条通知（GET /api/v1/notifications/feed 列表项）。"""

    id: UUID
    # application=申请提交 / demerit=扣分 / rollcall_report=点呼上报
    category: str
    title: str
    body: str
    related_student_id: Optional[UUID] = None
    event_at: datetime
    is_read: bool


class NotificationFeedOut(BaseModel):
    """GET /api/v1/notifications/feed 响应：最近通知流 + 未读数。"""

    items: list[NotificationItem]
    unread_count: int


class NotificationUnreadCountOut(BaseModel):
    """GET /unread-count + 标记已读端点 响应：当前老师未读数。"""

    unread_count: int


# ── 操作履历审计（老师操作记录页）2026-06-16 ──
class AuditLogEntry(BaseModel):
    """一条操作记录。写入侧 = app/audit.py 中间件自动埋点 / 端点语义级埋点（注册码等）。

    actor_name = join teachers.name 得到的操作者姓名（系统记录 / 已删账号为 null）。
    target_type/target_id 中间件自动记时可能为空（详情看 payload）。
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    actor_type: str
    actor_id: Optional[UUID] = None
    actor_name: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    payload: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuditLogListOut(BaseModel):
    """GET /api/v1/admin/audit-logs 响应：操作记录一覧（新→旧）+ 分页信息。"""

    items: list[AuditLogEntry]
    total: int
    limit: int
    offset: int
