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
    )

    @property
    def student_no(self) -> str:
        return f"{self.grade_code}{self.class_code}{self.seat_no}"


# ---------------------------------------------------------------
# 教师
# ---------------------------------------------------------------
# D12 拍板: 管理係 単独 ENUM 値で追加 (実物表必有審批人)
TEACHER_ROLES = (
    "寮務部長",
    "寮務課長",
    "国際交流部長",
    "国際交流課長",
    "管理係",
    "寮監",
    "学習担当",
    "寮務一般教师",
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
            "role IN ('寮務部長','寮務課長','国際交流部長','国際交流課長',"
            "'管理係','寮監','学習担当','寮務一般教师')",
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
    "returned",   # 退回 — 老師退回學生修改 (spec §7.2.4-5)
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

    # 外泊 / 帰国 only
    stay_locations: Mapped[Optional[list]] = mapped_column(JSON)
    meals_skip: Mapped[Optional[list]] = mapped_column(JSON)  # [{date, meal}] 形式

    # 申請理由 (全 kind · spec §7.2.4-5 修改届で必須)
    reason: Mapped[Optional[str]] = mapped_column(Text)

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
            "approver_role IN ('担任','寮務部長','寮務課長','国際交流部長','国際交流課長','管理係')",
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
NOTIFICATION_STATUSES = ("pending", "sent", "failed", "retrying")


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
            "status IN ('pending','sent','failed','retrying')", name="ck_notif_status"
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
        CheckConstraint(
            "session_type IN ('morning','evening')", name="ck_rcs_type"
        ),
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
    applied_group: Mapped[Optional[str]] = mapped_column(
        String(16)
    )  # 'normal' | 'soccer'
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
    invalidated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    __table_args__ = (
        # SQLite 不支持 regex CHECK，只能用 LENGTH；应用层 '^[0-9]{6}$' 严格校验
        CheckConstraint("LENGTH(code) = 6", name="ck_src_code_len"),
        Index("idx_src_code_active", "code", "invalidated_at"),
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
