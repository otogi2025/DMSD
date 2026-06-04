"""SQLAlchemy 2.x ORM models — P0 范围 (会话 B 担当字段).

权威 = BACKEND_DESIGN_LOG.md §4 + system_features.md §8。

⚠️ 数据类型注意:
- UUID = SQLAlchemy `Uuid` 跨 SQLite/PG 兼容 (SQLite 用 CHAR(32), PG 用 native UUID)
- JSON = `JSON` (SQLAlchemy 抽象, SQLite 用 TEXT, PG 用 JSONB)
- TIMESTAMPTZ → SQLAlchemy `DateTime(timezone=True)` (SQLite 弱対応, PG native)
- 一部 PG 専用 CHECK (CURRENT_DATE 比較等) は app 層で再校验, DB layer は最低限

decision IDs (BACKEND_DESIGN_LOG §10):
- D4 实物表 chain (外泊 一般 = 3 / 留学生 = 5)
- D11 class_teacher_assignment 单独表
- D12 管理係 加 ENUM
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ---------------------------------------------------------------
# 学生
# ---------------------------------------------------------------
class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    grade_code: Mapped[str] = mapped_column(String(2), nullable=False)
    class_code: Mapped[str] = mapped_column(String(2), nullable=False)
    seat_no: Mapped[str] = mapped_column(String(2), nullable=False)
    # student_no は GENERATED ALWAYS AS (PG only) → app 層 derived property で代用
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_kana: Mapped[Optional[str]] = mapped_column(Text)
    birthday: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(8), nullable=False)  # 'male' | 'female'
    category: Mapped[str] = mapped_column(Text, nullable=False, default="一般寮生")
    room_no: Mapped[str] = mapped_column(String(8), nullable=False)
    dorm_unit: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1, 2, 4
    is_overseas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    # demo / reviewer 账号标志 — admin 学生列表 / 出席统计默认过滤掉
    # （审核员 / 老师体验用账号；spec system_features.md §7.20）
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # relations
    applications: Mapped[list["Application"]] = relationship(back_populates="student")

    __table_args__ = (
        CheckConstraint(
            "(gender = 'male' AND dorm_unit IN (1, 2)) OR (gender = 'female' AND dorm_unit = 4)",
            name="ck_students_gender_dorm",
        ),
        CheckConstraint(
            "status IN ('active', 'locked', 'graduated', 'transferred', 'paused')",
            name="ck_students_status",
        ),
        CheckConstraint("dorm_unit IN (1, 2, 4)", name="ck_students_dorm_unit"),
        UniqueConstraint("grade_code", "class_code", "seat_no", name="uq_students_no"),
        Index("idx_students_dorm", "dorm_unit", "status"),
        Index("idx_students_is_demo", "is_demo"),
    )

    @property
    def student_no(self) -> str:
        return f"{self.grade_code}{self.class_code}{self.seat_no}"


# ---------------------------------------------------------------
# 教师
# ---------------------------------------------------------------
# D12 拍板: 管理係 単独 ENUM 値で追加 (実物表必有審批人)
TEACHER_ROLES = (
    "校長",
    "寮務部長",
    "寮務課長",
    "国際交流部長",
    "国際交流課長",
    "管理係",
    "寮監",
    "学習担当",
    "寮務一般教師",
)


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    login_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    # D2 拍板: assigned_dorm = NULL (跨寮) | 1 (男寮 = 1+2 暗指) | 4 (女寮)
    assigned_dorm: Mapped[Optional[int]] = mapped_column(SmallInteger)
    failed_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('校長','寮務部長','寮務課長','国際交流部長','国際交流課長',"
            "'管理係','寮監','学習担当','寮務一般教師')",
            name="ck_teachers_role",
        ),
        CheckConstraint(
            "assigned_dorm IS NULL OR assigned_dorm IN (1, 2, 4)",
            name="ck_teachers_dorm",
        ),
        CheckConstraint("status IN ('active','disabled')", name="ck_teachers_status"),
    )


class ClassTeacherAssignment(Base):
    """D11 拍板: 担任 (homeroom) は teachers.role に入れず本表で紐付け。

    - 1 教師が同時に複数学年・組を担任することがある
    - 学年度更替時に audit 履歴を保持できる
    """

    __tablename__ = "class_teacher_assignment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    grade_code: Mapped[str] = mapped_column(String(2), nullable=False)
    class_code: Mapped[str] = mapped_column(String(2), nullable=False)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_homeroom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "grade_code",
            "class_code",
            "academic_year",
            "is_homeroom",
            "effective_from",
            name="uq_cta_assignment",
        ),
        Index("idx_cta_class", "grade_code", "class_code", "academic_year"),
        Index("idx_cta_teacher", "teacher_id"),
    )


# ---------------------------------------------------------------
# 学生认证 (login)
# ---------------------------------------------------------------
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    failed_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    lock_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ---------------------------------------------------------------
# 出寮届 (#2 schema)
# ---------------------------------------------------------------
APPLICATION_KINDS = ("帰省", "外泊", "帰国")
APPLICATION_STATUSES = (
    "pending",
    "approved_partial",
    "approved",
    "rejected",
    "withdrawn",
    "returned",  # 退回 — 老師退回學生修改 (spec §7.2.4-5)
)


class Application(Base):
    """#2 出寮届 (帰省 / 外泊 / 帰国) — 三种逐层累积フィールド。

    BACKEND_DESIGN_LOG §4.4 + system_features §7.2.1。
    """

    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(8), nullable=False)

    # 共通字段 (3 種共通)
    leave_date: Mapped[date] = mapped_column(Date, nullable=False)
    leave_method: Mapped[str] = mapped_column(Text, nullable=False)
    leave_time: Mapped[time] = mapped_column(Time, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_method: Mapped[str] = mapped_column(Text, nullable=False)
    return_time: Mapped[time] = mapped_column(Time, nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(Text)
    meal_note: Mapped[Optional[str]] = mapped_column(Text)

    # 出租车预约「タクシー予約」时刻（itsuki 2026-06-03）— 学生希望坐出租车出寮 / 帰寮时填想坐车的时刻；null = 不预约
    taxi_reservation_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # 外泊 / 帰国 only
    stay_locations: Mapped[Optional[list]] = mapped_column(JSON)
    meals_skip: Mapped[Optional[list]] = mapped_column(JSON)  # [{date, meal}] 形式
    companion: Mapped[Optional[str]] = mapped_column(Text)
    dest_cities: Mapped[Optional[str]] = mapped_column(Text)
    receipt_submitted: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False
    )

    # 申請理由 (全 kind · spec §7.2.4-5 修改届で必須)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    is_long_vacation: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False
    )

    # 帰国 only
    flight_dep_air: Mapped[Optional[str]] = mapped_column(Text)
    flight_dep_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    flight_arr_air: Mapped[Optional[str]] = mapped_column(Text)
    flight_arr_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 巴士関連 (P2)
    bus_route_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    # 状态
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # relations
    student: Mapped["Student"] = relationship(back_populates="applications")
    approvals: Mapped[list["ApplicationApproval"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationApproval.chain_order",
    )

    __table_args__ = (
        CheckConstraint("kind IN ('帰省','外泊','帰国')", name="ck_app_kind"),
        CheckConstraint(
            "status IN ('pending','approved_partial','approved','rejected','withdrawn','returned')",
            name="ck_app_status",
        ),
        Index("idx_app_student", "student_id", "status"),
        Index("idx_app_status_date", "status", "leave_date"),
    )


# ---------------------------------------------------------------
# 出寮届承认 (#5 + #10)
# ---------------------------------------------------------------
APPROVER_ROLES = (
    "担任",
    "校長",
    "寮務部長",
    "寮務課長",
    "国際交流部長",
    "国際交流課長",
    "管理係",
)
APPROVAL_DECISIONS = ("approve", "reject")


class ApplicationApproval(Base):
    """届ごとの承认者 chain (1 行 / role)。

    chain 生成は services.approval_chain.build_chain() 参照。
    """

    __tablename__ = "application_approvals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    approver_role: Mapped[str] = mapped_column(String(16), nullable=False)
    chain_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )  # chain 表示順 (担任 → ... → 管理係)
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    decision: Mapped[Optional[str]] = mapped_column(String(8))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    application: Mapped["Application"] = relationship(back_populates="approvals")

    __table_args__ = (
        CheckConstraint(
            "approver_role IN ('担任','校長','寮務部長','寮務課長','国際交流部長','国際交流課長','管理係')",
            name="ck_approval_role",
        ),
        CheckConstraint(
            "decision IS NULL OR decision IN ('approve','reject')",
            name="ck_approval_decision",
        ),
        UniqueConstraint("application_id", "approver_role", name="uq_approval_role"),
    )


# ---------------------------------------------------------------
# 通知ログ (#6 R1)
# ---------------------------------------------------------------
NOTIFICATION_CHANNELS = ("email", "push", "in_app")
NOTIFICATION_STATUSES = ("pending", "sent", "failed", "retrying", "skipped_no_provider")


class NotificationLog(Base):
    """送信した (or 試行した) 通知の履歴。retry / 失败 audit に使う。"""

    __tablename__ = "notification_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    template_key: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(16), nullable=False)
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_email: Mapped[Optional[str]] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "channel IN ('email','push','in_app')", name="ck_notif_channel"
        ),
        CheckConstraint(
            "status IN ('pending','sent','failed','retrying','skipped_no_provider')",
            name="ck_notif_status",
        ),
        CheckConstraint(
            "target_type IN ('student','teacher','role')", name="ck_notif_target_type"
        ),
        Index("idx_notif_status", "status", "created_at"),
    )


# ---------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------
class AuditLog(Base):
    """append-only 監査履歴 (BACKEND_DESIGN_LOG §3.7)。"""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('student','teacher','system')", name="ck_audit_actor_type"
        ),
        Index("idx_audit_target", "target_type", "target_id", "created_at"),
        Index("idx_audit_actor", "actor_type", "actor_id", "created_at"),
    )


# ---------------------------------------------------------------
# 学習 (Study self-study session)
# ---------------------------------------------------------------
class StudyRoster(Base):
    """学習対象者名単 — 中学全員自動 + 高校手動追加 (D8 拍板)。"""

    __tablename__ = "study_roster"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    academic_term: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # '2026-spring' / '2026-fall'
    added_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )  # NULL = system (中学全員自動)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    removed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )  # NULL = 在籍中

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        UniqueConstraint("student_id", "academic_term", name="uq_roster_term"),
        Index("idx_roster_term", "academic_term", "removed_at"),
    )


class StudyAbsenceRequest(Base):
    """学習欠席届 — 学生が当日 19:40 前に提出 → 学習担当が approve/reject。"""

    __tablename__ = "study_absence_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    # 欠席する範囲: 前半節 (19:40-20:40) / 後半節 (20:45-21:45) / 両方
    period: Mapped[str] = mapped_column(String(16), nullable=False, default="full")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_sar_status"
        ),
        CheckConstraint(
            "period IN ('first_half','second_half','full')", name="ck_sar_period"
        ),
        # 一日一回（範囲問わず）— 前半 + 後半 を別々に出すなら "full" を出してもらう
        UniqueConstraint("student_id", "target_date", name="uq_sar_date"),
        Index("idx_sar_date_status", "target_date", "status"),
    )


class StudyOnlineRequest(Base):
    """在线学习申请 — 学生申请在自室参加校外在线课程。"""

    __tablename__ = "study_online_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    period_from: Mapped[date] = mapped_column(Date, nullable=False)
    period_to: Mapped[date] = mapped_column(Date, nullable=False)
    weekly_schedule: Mapped[dict] = mapped_column(JSON, nullable=False)
    contract_ref: Mapped[Optional[str]] = mapped_column(Text)
    # 契約書文件（合同 = 网课报名凭证）照片 / PDF。学生提交申请后单独上传，可选。
    # contract_file_path = 服务器上相对 upload_dir 的存放路径（如 contracts/<id>.pdf），不暴露给客户端。
    contract_file_path: Mapped[Optional[str]] = mapped_column(Text)
    # contract_file_name = 学生上传时的原始文件名，老师下载时按这个显示。
    contract_file_name: Mapped[Optional[str]] = mapped_column(Text)
    # contract_mime = 文件类型（image/jpeg | image/png | image/heic | application/pdf）。
    contract_mime: Mapped[Optional[str]] = mapped_column(String(100))
    # contract_size = 文件字节数，列表 / 详情显示大小用。
    contract_size: Mapped[Optional[int]] = mapped_column(Integer)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected','revoked')",
            name="ck_sor_status",
        ),
        Index("idx_sor_student_status", "student_id", "status"),
        Index("idx_sor_submitted", "submitted_at"),
    )


class StudyCheckin(Base):
    """学習出席記録 — 学習担当が 1 件ずつ記録 (NFC or 手動)。"""

    __tablename__ = "study_checkins"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )  # NULL = 未签
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="init"
    )  # init / present / late / absent / exempt
    recorded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    overridden_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    override_reason: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "status IN ('init','present','late','absent','exempt')",
            name="ck_sc_status",
        ),
        UniqueConstraint("student_id", "target_date", name="uq_sc_date"),
        Index("idx_sc_date_status", "target_date", "status"),
    )


# ---------------------------------------------------------------
# 宿舍生活类申请
# ---------------------------------------------------------------
class DormEventProposal(Base):
    """寮生行事企画申請 — 学生或学生团体提交活动企划。"""

    __tablename__ = "dorm_event_proposals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    proposer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    team_name: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    held_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    place: Mapped[str] = mapped_column(Text, nullable=False)
    expected_count: Mapped[int] = mapped_column(Integer, nullable=False)
    target: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    risk_solution: Mapped[str] = mapped_column(Text, nullable=False)
    expected_cost: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    result: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    proposer: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "result IN ('pending','approved','approved_conditional','resubmit','rejected')",
            name="ck_dep_result",
        ),
        Index("idx_dep_proposer_result", "proposer_id", "result"),
        Index("idx_dep_result_submitted", "result", "submitted_at"),
    )


class DormScheduleChange(Base):
    """寮日課変更願 — 老师或责任者提交团体作息变更。"""

    __tablename__ = "dorm_schedule_changes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    requester_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    class_or_club: Mapped[str] = mapped_column(Text, nullable=False)
    period_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    period_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    change_content: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    requester: Mapped["Teacher"] = relationship(foreign_keys=[requester_id])

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_dsc_status"
        ),
        Index("idx_dsc_requester_status", "requester_id", "status"),
        Index("idx_dsc_status_submitted", "status", "submitted_at"),
    )


class FridgePurchaseRequest(Base):
    """冷蔵庫購入届 — 学校指定冷蔵庫の購入申請。"""

    __tablename__ = "fridge_purchase_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    contact_phone: Mapped[str] = mapped_column(Text, nullable=False)
    contact_wechat: Mapped[Optional[str]] = mapped_column(Text)
    product: Mapped[str] = mapped_column(String(1), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    delivered_sign: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint("product IN ('A','B')", name="ck_fpr_product"),
        CheckConstraint(
            "status IN ('pending','ordered','delivered','rejected')",
            name="ck_fpr_status",
        ),
        Index("idx_fpr_student_status", "student_id", "status"),
        Index("idx_fpr_status_submitted", "status", "submitted_at"),
    )


class ItemPossessionRequest(Base):
    """物品所持許可願 — 宿舍内持有物品的许可申请。"""

    __tablename__ = "item_possession_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    room_no: Mapped[str] = mapped_column(String(16), nullable=False)
    item: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    guardian_name: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped["Student"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_ipr_status"
        ),
        Index("idx_ipr_student_status", "student_id", "status"),
        Index("idx_ipr_status_submitted", "status", "submitted_at"),
    )


# ---------------------------------------------------------------
# 点呼 (Roll Call)
# ---------------------------------------------------------------
class RollCallSession(Base):
    """点呼セッション — 1 回の点呼 = 1 行 (cron で自動生成 + 教師手動開始)。"""

    __tablename__ = "rollcall_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dorm_unit_set: Mapped[list] = mapped_column(
        JSON, nullable=False
    )  # [1,2] (男寮) or [4] (女寮)
    session_type: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # 'morning' | 'evening'
    schedule_mode: Mapped[str] = mapped_column(
        String(16), nullable=False, default="split"
    )
    day_type: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # 'weekday' | 'weekend_holiday'
    session_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="draft"
    )  # draft / running / ended
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_source: Mapped[Optional[str]] = mapped_column(
        String(16)
    )  # 'teacher' | 'system'
    started_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_source: Mapped[Optional[str]] = mapped_column(String(16))
    ended_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    scheduled_window_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduled_on_time_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduled_late_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduled_auto_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    settle_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    events: Mapped[list["RollCallEvent"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("session_type IN ('morning','evening')", name="ck_rcs_type"),
        CheckConstraint(
            "schedule_mode IN ('split','merged_normal')", name="ck_rcs_mode"
        ),
        CheckConstraint(
            "day_type IN ('weekday','weekend_holiday')", name="ck_rcs_day_type"
        ),
        CheckConstraint(
            "session_status IN ('draft','running','ended')", name="ck_rcs_status"
        ),
    )


class RollCallEvent(Base):
    """点呼イベント — append-only。1 学生 1 セッション 1 行 (幂等制御)。"""

    __tablename__ = "rollcall_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("rollcall_sessions.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    path_type: Mapped[Optional[str]] = mapped_column(
        String(8)
    )  # 'A' (NFC カード) | 'B' (iPhone tap) | 'manual'
    base_status: Mapped[str] = mapped_column(
        String(24), nullable=False
    )  # present / late / absent / exempt_range
    status_source: Mapped[str] = mapped_column(
        String(24), nullable=False
    )  # auto_nfc / auto_settle / manual_checkin / teacher_override
    # 2026-05-21 (A-022 b1 fix): 原 applied_group 字段已删除
    # 窗口永远固定 (§5.4)，分组直接走 §6.4 student_group (从 session + 学生当前组推导)
    # 不再需要在 event 层存「本次判定使用的 group」 — 因为 group 永远等于 student 当前 group
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        Text
    )  # 路径 B 用 (client が送る UUID)
    card_uid: Mapped[Optional[str]] = mapped_column(
        String(32)
    )  # 路径 A 用 (NFC UID hex)
    reason: Mapped[Optional[str]] = mapped_column(Text)  # override 時必填

    session: Mapped["RollCallSession"] = relationship(back_populates="events")

    __table_args__ = (
        CheckConstraint(
            "base_status IN ('init','present','late','absent','exempt_range')",
            name="ck_rce_status",
        ),
        CheckConstraint(
            "status_source IN ('auto_nfc','auto_settle','manual_checkin','teacher_override')",
            name="ck_rce_source",
        ),
        Index("idx_rce_session_student", "session_id", "student_id"),
        # A-011 (2026-05-21): idempotency_key 同 session 内必须唯一
        # client 用同一 key 重试 → DB 层挡住 + router 先查 key 命中返已存事件
        UniqueConstraint("session_id", "idempotency_key", name="uq_rce_idempotency"),
    )


# ---------------------------------------------------------------
# 教師招待 (Teacher Invitation — §3.4)
# ---------------------------------------------------------------
class TeacherInvitation(Base):
    """旧教師が新教師を招待するためのワンタイムトークン。"""

    __tablename__ = "teacher_invitations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )  # URL-safe random 32 bytes
    invited_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    target_email: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str] = mapped_column(String(32), nullable=False)
    target_dorm: Mapped[Optional[int]] = mapped_column(SmallInteger)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )  # 通常 7 日後
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    used_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (Index("idx_tinv_token", "token"),)


# ---------------------------------------------------------------
# 学生注册码（App Store 上架对策，2026-05-03 itsuki 拍板）
#   权威 spec：system_features.md §7.16 + BACKEND_DESIGN_LOG §4.10 + §5.1.5
#   机制：老师在后台生成 6 桁数字 → 学生 5 分钟内拿这个码完成新规注册
#         同时有效的码全系统只 1 个（生成新码时旧码立刻 invalidate）
# ---------------------------------------------------------------
class StudentRegistrationCode(Base):
    __tablename__ = "student_registration_codes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # = created_at + 5 分钟（应用层算，不放 DB default — TTL 调整只动应用层即可）
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # 生成新码时把旧 active 行的本字段 set 为 now()；NULL = 仍是候选有效码
    invalidated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # 审核员永久码标志 — refresh 不作废 + 跟普通 5 分钟码并存（spec §7.16 例外条款）
    # is_reviewer=True 的码长期有效，专给 Apple 审核员 / itsuki 内测用，普通老师不可见
    is_reviewer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        # SQLite 不支持 regex CHECK，只能用 LENGTH；应用层 '^[0-9]{6}$' 严格校验
        CheckConstraint("LENGTH(code) = 6", name="ck_src_code_len"),
        Index("idx_src_code_active", "code", "invalidated_at"),
        Index("idx_src_is_reviewer", "is_reviewer", "invalidated_at"),
    )


# ---------------------------------------------------------------
# 老师公告 — 2026-05-03 itsuki 拍板，2026-05-04 实装
#   权威 spec：system_features.md §7.15
#   性质：老师 → 学生 单向 Classroom 风通知（学生回复是附带能力）
#   scope：all / male / female（学生只看到自己 gender 对应那部分，自动过滤）
# ---------------------------------------------------------------
ANNOUNCEMENT_SCOPES = ("all", "male", "female")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(String(8), nullable=False)
    author_teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # 软删 — 已删的不出现在学生列表里
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "scope IN ('all','male','female')", name="ck_announcement_scope"
        ),
        Index("idx_announcement_created", "created_at"),
        Index("idx_announcement_scope_active", "scope", "deleted_at"),
    )


class AnnouncementRead(Base):
    """已读跟踪表（学生 × 公告 = 复合主键）。"""

    __tablename__ = "announcement_reads"

    announcement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("announcements.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AnnouncementReply(Base):
    """回复 — 学生和老师都能发，全员互见（§7.15.6 itsuki 拍板）。"""

    __tablename__ = "announcement_replies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    announcement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    # 'student' or 'teacher' — 决定 author_id 指向哪张表
    author_kind: Mapped[str] = mapped_column(String(8), nullable=False)
    # 学生 students.id 或老师 teachers.id；DB 层不加 FK（要按 author_kind 跨表），应用层保证
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "author_kind IN ('student','teacher')", name="ck_reply_author_kind"
        ),
        Index("idx_reply_announcement", "announcement_id", "created_at"),
    )


# ---------------------------------------------------------------
# 扣分事件 — spec §7.5 規律処分 / itsuki 5-22 阈值 4 清扫 / 8 禁足
# ---------------------------------------------------------------
# 5-27 凌晨 CC 替 itsuki 默认决策的字段（起床后可推翻）:
# - source_type ENUM 6 值: rollcall_late / rollcall_absent / cleaning_failed /
#   curfew_violation / study_absent / manual
# - points 默认: late=1.0 / absent=2.0 / cleaning=2.5 / curfew=5.0 / study_absent=1.5
# - 类型 Float（允许 0.5 分罚扫）
# - revoke 软删除（保留 revoked_at + reason，列表过滤掉）
# - manual 类型创建权限: 寮監 + 寮務全员（router 层 check）
class DemeritEvent(Base):
    """扣分事件，DisciplinePage / CleaningPage / 警告列表全部依赖。"""

    __tablename__ = "demerit_event"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False, index=True
    )

    # 扣分事件来源类型
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # 关联到具体事件 ID（source_type 决定指向哪张表）— 应用层保证一致性
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    points: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # 月份汇总用，避免每次 GROUP BY 算 (YYYY-MM 格式)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # NULL = 系统自动判定（cron 跑 rollcall settle）/ 非 NULL = 老师手动加扣
    created_by_teacher_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )

    # 撤销软删除
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_by_teacher_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    revoke_reason: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('rollcall_late','rollcall_absent','cleaning_failed','curfew_violation','study_absent','manual')",
            name="ck_demerit_source",
        ),
        Index("idx_demerit_student_month", "student_id", "month"),
        Index("idx_demerit_month_active", "month", "revoked_at"),
    )


# ---------------------------------------------------------------
# 清扫安排 — spec §7.10 清扫审查
# ---------------------------------------------------------------
# CC 5-27 凌晨替 itsuki 默认决策（起床后可推翻）:
# - area ENUM 8 类（用日文字符串作为 UI 显示值）— itsuki 起床后看实际宿舍区域清单可改
# - status ENUM: assigned 已分配 / done 学生扫完上报 / passed 老师审通过 /
#   failed 审不通过（自动加 DemeritEvent）/ skipped 取消跳过
# - failed → 自动加 DemeritEvent.source_type='cleaning_failed' points=2.5
#   （业务逻辑由 router 层触发）
class CleaningAssignment(Base):
    """清扫安排单。CleaningPage / 警告列表 用。"""

    __tablename__ = "cleaning_assignment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False, index=True
    )
    area: Mapped[str] = mapped_column(String(32), nullable=False)
    # 计划执行日 (YYYY-MM-DD)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="assigned")

    assigned_by_teacher_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # 学生上报扫完时刻
    done_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 老师审核
    inspected_by_teacher_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    inspected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # 不通过时填写
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    # 不通过时自动加的 DemeritEvent.id（关联，方便撤销时一并撤回扣分）
    demerit_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("demerit_event.id")
    )

    __table_args__ = (
        CheckConstraint(
            "area IN ('浴室','廊下','トイレ','共用キッチン','階段','玄関','ロビー','その他')",
            name="ck_cleaning_area",
        ),
        CheckConstraint(
            "status IN ('assigned','done','passed','failed','skipped')",
            name="ck_cleaning_status",
        ),
        Index("idx_cleaning_student_date", "student_id", "scheduled_date"),
    )


# ---------------------------------------------------------------
# 宅配 / 失物招领 — spec §7.12 前台业务
# ---------------------------------------------------------------
# CC 5-27 凌晨替 itsuki 默认决策:
# - kind ENUM: delivery 宅配 / lost_and_found 失物招领
# - status ENUM: pending 登记待处理 / notified 已通知学生 / picked_up 已被取走 /
#   expired 已过期 / discarded 已废弃
# - delivery 默认 expires_in_days = 7（1 周）/ lost_and_found 默认 30 天
# - 取走确认 = 老师手动标 picked_up（学生 NFC 取走是 v1.1+ 议题）
class FrontDeskItem(Base):
    """宅配通知 + 失物招领登记的共通 model。"""

    __tablename__ = "front_desk_item"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    # 宅配时是收件人学生 / 失物时是捡到人（学生或 NULL）
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("students.id")
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # 失物发现位置 / 宅配保管位置
    location: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")

    created_by_teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    picked_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "kind IN ('delivery','lost_and_found')", name="ck_front_desk_kind"
        ),
        CheckConstraint(
            "status IN ('pending','notified','picked_up','expired','discarded')",
            name="ck_front_desk_status",
        ),
        Index("idx_front_desk_status_expires", "status", "expires_at"),
    )


# ---------------------------------------------------------------
# 行事予定 (spec §7.5)
# ---------------------------------------------------------------
class DormEvent(Base):
    """学校・宿舍行事日历。老师录入，学生可见。

    spec §7.5 — GET /events?from=&to= (学生+役职) / POST/PATCH/DELETE (役职)
    """

    __tablename__ = "dorm_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # 学校行事 / 寮行事 / 外部 等
    event_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )  # 主日期（日历定位用）
    start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )  # 开始时刻（NULL=全天）
    end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )  # 结束时刻（NULL=全天）
    description: Mapped[Optional[str]] = mapped_column(Text)  # 说明备注
    created_by_teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "category IN ('学校行事','寮行事','外部','その他')",
            name="ck_dorm_events_category",
        ),
        Index("idx_dorm_events_date", "event_date"),
    )


# ---------------------------------------------------------------
# 巴士时刻表 (spec §7.6)
# ---------------------------------------------------------------
class BusRoute(Base):
    """学校巴士 / 宿舍特殊巴士时刻表。老师录入，学生可见。

    spec §7.6 — GET /bus/routes (学生+役职) / POST/PATCH/DELETE (役职)
    kind: daily_commute=平日通学便 / dorm_special=寮特殊便
    """

    __tablename__ = "bus_routes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # daily_commute / dorm_special
    name: Mapped[str] = mapped_column(Text, nullable=False)  # "朝便 6:50 寮 → 駅" 等
    direction: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # 寮→駅 / 駅→寮 / 寮→空港 等
    schedule_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )  # 出发时刻
    arrival_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )  # 到达时刻（空港便等）
    visible_to: Mapped[str] = mapped_column(
        String(16), nullable=False, default="all"
    )  # all / dorm_only / men / women
    note: Mapped[Optional[str]] = mapped_column(Text)  # 备注
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "kind IN ('daily_commute','dorm_special')",
            name="ck_bus_routes_kind",
        ),
        CheckConstraint(
            "visible_to IN ('all','dorm_only','men','women')",
            name="ck_bus_routes_visible_to",
        ),
        Index("idx_bus_routes_kind_deprecated", "kind", "deprecated"),
        Index("idx_bus_routes_schedule_at", "schedule_at"),
    )


# ---------------------------------------------------------------
# 指導履歴（学生指导记录）— spec §7.9/§7.10
# ---------------------------------------------------------------
class GuidanceRecord(Base):
    """学生指导记录 — 老师录入，学生默认看不到（C 案，§7.10）。"""

    __tablename__ = "guidance_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 类别：生活态度 / 点呼态度 / 同寮纠纷 / 学习 / 其他
    category: Mapped[Optional[str]] = mapped_column(Text)
    # 默认 confidential — 学生申请开示才能看到（§7.10 C 案）
    confidential: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    guidance_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(foreign_keys=[student_id])
    teacher: Mapped["Teacher"] = relationship(foreign_keys=[teacher_id])

    __table_args__ = (
        Index("idx_gr_student", "student_id", "deleted_at"),
        Index("idx_gr_teacher", "teacher_id", "guidance_date"),
    )


class GuidanceDisclosureRequest(Base):
    """指导履历 开示申请 — 学生发起，老师决定（§7.10 C 案）。"""

    __tablename__ = "guidance_disclosure_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id"), nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("teachers.id")
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    decision_note: Mapped[Optional[str]] = mapped_column(Text)
    # 部分开示时的开示范围（全部开示时两字段均 NULL）
    visible_from: Mapped[Optional[date]] = mapped_column(Date)
    visible_until: Mapped[Optional[date]] = mapped_column(Date)
    # 老师事后撤销开示（误开示对策）
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(foreign_keys=[student_id])

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved_full','approved_partial','rejected')",
            name="ck_gdr_status",
        ),
        Index("idx_gdr_student_status", "student_id", "status"),
        Index("idx_gdr_status_requested", "status", "requested_at"),
    )


# ---------------------------------------------------------------
# 设备推送令牌 — spec §7.13
# ---------------------------------------------------------------
class DeviceToken(Base):
    """学生设备的 APNs / FCM 推送令牌。

    同一学生可以有多个设备（手机 + iPad 等）。
    token 全局唯一（同一个 token 换了 student_id 应该先 revoke 再重新注册，但 DB 层只做 unique index）。
    """

    __tablename__ = "device_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    # 'ios' = APNs device token / 'android' = FCM registration token
    platform: Mapped[str] = mapped_column(String(8), nullable=False)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # App 每次启动时更新，用来判断 token 是否还活跃
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # 软删 — revoked_at 非 NULL 表示已失效（App 卸载、用户注销等）
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("platform IN ('ios','android')", name="ck_dt_platform"),
        Index("idx_dt_student_active", "student_id", "revoked_at"),
        # token 全局唯一（同一 token 换 student_id 前必须先 revoke）
        UniqueConstraint("token", name="uq_dt_token"),
    )


# ---------------------------------------------------------------
# 事案録入（事件/事案记录）— spec §7.9 #33
# ---------------------------------------------------------------
class IncidentRecord(Base):
    """事案录入 — 老师录入，富文本内容，可涉及多名学生。"""

    __tablename__ = "incident_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # 正文：富文本（前端 rich text，后端存 HTML 字符串）
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # 涉及学生 ID 列表（JSON 数组）— 支持 tap 跳转到学生数据页 #33
    involved_student_ids: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list
    )
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teachers.id"), nullable=False
    )
    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    recorder: Mapped["Teacher"] = relationship(foreign_keys=[recorded_by])

    __table_args__ = (
        Index("idx_ir_recorded_by", "recorded_by", "incident_date"),
        Index("idx_ir_date_active", "incident_date", "deleted_at"),
    )
