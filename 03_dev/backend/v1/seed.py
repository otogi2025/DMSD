"""seed — 双模式数据投入（dev dummy / production minimal）。

通过环境变量 APP_ENV 切换：
    APP_ENV=dev (default) → dev dummy seed（dummy 学生 2 + 教师 9 + 点呼 session 2 + 学习名簿）
    APP_ENV=production    → production seed（admin 教师 1 + reviewer 学生 1 + reviewer 注册码 1）

production seed 5-08 拍板规则（详见 system_features.md §7.20 + §7.16 例外条款）：
    - admin 默认密码从 env ADMIN_INITIAL_PASSWORD 读（fallback "ChangeMe-2026-05" 仅 dev 兜底）
    - reviewer 学号 999999（grade=99/class=99/seat=99，schema 允许，业务不存在）
    - reviewer 密码 "Tomoshibi-Reviewer-2026!"（强度足够 + 品牌前缀）
    - reviewer 学生 is_demo=True → admin 学生列表 / 出席统计自动过滤
    - reviewer 注册码 "999999" + is_reviewer=True → 老师面板不可见 + refresh 不作废 + 永久有效

执行：
    cd 03_dev/backend/v1
    APP_ENV=dev python -m seed         # 本机 dev 用
    APP_ENV=production python -m seed  # VPS 部署用
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timezone, timedelta

from sqlalchemy import select

from app import models, security
from app.database import SessionLocal, create_all

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")


# =============================================================
# Dev dummy seed（APP_ENV=dev 用，本机 SQLite）
# =============================================================

DEV_PASSWORD = "123456"

DEV_STUDENTS = [
    dict(
        grade_code="06",
        class_code="02",
        seat_no="18",
        name="リュウ イヒ",
        name_kana="リュウ イヒ",
        gender="male",
        category="一般寮生",
        room_no="M101",
        dorm_unit=1,
        is_overseas=True,
        email="ryu.ihi@example.jp",
    ),
    dict(
        grade_code="06",
        class_code="01",
        seat_no="03",
        name="田中 太郎",
        name_kana="タナカ タロウ",
        gender="male",
        category="一般寮生",
        room_no="M203",
        dorm_unit=1,
        is_overseas=False,
        email="tanaka.taro@example.jp",
    ),
]

DEV_TEACHERS = [
    dict(
        login_id="ryomu_buchou",
        name="寮務 太郎 (寮務部長)",
        email="ryomu.buchou@example.jp",
        role="寮務部長",
        assigned_dorm=None,
    ),
    dict(
        login_id="ryomu_kachou",
        name="寮務 次郎 (寮務課長)",
        email="ryomu.kachou@example.jp",
        role="寮務課長",
        assigned_dorm=None,
    ),
    dict(
        login_id="kokukou_buchou",
        name="国際 三郎 (国際交流部長)",
        email="kokusai.buchou@example.jp",
        role="国際交流部長",
        assigned_dorm=None,
    ),
    dict(
        login_id="kokukou_kachou",
        name="国際 四郎 (国際交流課長)",
        email="kokusai.kachou@example.jp",
        role="国際交流課長",
        assigned_dorm=None,
    ),
    dict(
        login_id="kanri",
        name="管理 五郎 (管理係)",
        email="kanri@example.jp",
        role="管理係",
        assigned_dorm=None,
    ),
    dict(
        login_id="ryokan_m",
        name="寮監 六郎 (男寮)",
        email="ryokan.m@example.jp",
        role="寮監",
        assigned_dorm=1,
    ),
    dict(
        login_id="gakushuu",
        name="学習 七郎",
        email="gakushuu@example.jp",
        role="学習担当",
        assigned_dorm=None,
    ),
    dict(
        login_id="tannin_high3a",
        name="担任 八郎 (高3A)",
        email="tannin.high3a@example.jp",
        role="寮務一般教师",
        assigned_dorm=1,
    ),
    dict(
        login_id="tannin_high3b",
        name="担任 九郎 (高3B)",
        email="tannin.high3b@example.jp",
        role="寮務一般教师",
        assigned_dorm=1,
    ),
]


def seed_dev(db) -> None:
    """dev dummy 数据 — 本机 SQLite 开发用。"""
    pw_hash = security.hash_password(DEV_PASSWORD)

    # 学生
    for s_data in DEV_STUDENTS:
        existing = db.scalars(
            select(models.Student).where(
                models.Student.grade_code == s_data["grade_code"],
                models.Student.class_code == s_data["class_code"],
                models.Student.seat_no == s_data["seat_no"],
            )
        ).first()
        if existing:
            log.info(
                "跳过学生: %s%s%s 已存在",
                s_data["grade_code"],
                s_data["class_code"],
                s_data["seat_no"],
            )
            continue
        student = models.Student(**s_data)
        db.add(student)
        db.flush()
        db.add(models.Account(student_id=student.id, password_hash=pw_hash))
        log.info("加学生: %s (no=%s)", student.name, student.student_no)

    # 教师
    for t_data in DEV_TEACHERS:
        existing = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == t_data["login_id"])
        ).first()
        if existing:
            log.info("跳过教师: %s 已存在", t_data["login_id"])
            continue
        teacher = models.Teacher(**t_data, password_hash=pw_hash)
        db.add(teacher)
        log.info("加教师: %s (role=%s)", teacher.login_id, teacher.role)

    db.commit()

    # 担任绑定
    homeroom_pairs = [
        ("tannin_high3a", "06", "01"),
        ("tannin_high3b", "06", "02"),
    ]
    for login_id, grade, klass in homeroom_pairs:
        teacher = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == login_id)
        ).first()
        if not teacher:
            continue
        existing = db.scalars(
            select(models.ClassTeacherAssignment).where(
                models.ClassTeacherAssignment.teacher_id == teacher.id,
                models.ClassTeacherAssignment.grade_code == grade,
                models.ClassTeacherAssignment.class_code == klass,
                models.ClassTeacherAssignment.academic_year == 2026,
                models.ClassTeacherAssignment.is_homeroom.is_(True),
            )
        ).first()
        if existing:
            continue
        db.add(
            models.ClassTeacherAssignment(
                teacher_id=teacher.id,
                grade_code=grade,
                class_code=klass,
                academic_year=2026,
                is_homeroom=True,
                effective_from=date(2026, 4, 1),
            )
        )
        log.info("加担任: %s → %s%s", login_id, grade, klass)
    db.commit()

    # 学习名簿
    all_students = db.scalars(select(models.Student)).all()
    for student in all_students:
        existing = db.scalars(
            select(models.StudyRoster).where(
                models.StudyRoster.student_id == student.id,
                models.StudyRoster.academic_term == "2026-spring",
            )
        ).first()
        if not existing:
            db.add(
                models.StudyRoster(
                    student_id=student.id,
                    academic_term="2026-spring",
                )
            )
            log.info("加学习名簿: %s", student.name)
    db.commit()

    # 点呼 session
    JST = timezone(timedelta(hours=9))
    today_jst = date.today()

    def make_session(session_type: str, h: int, m: int) -> None:
        window_start = datetime(
            today_jst.year, today_jst.month, today_jst.day, h, m, tzinfo=JST
        )
        existing = db.scalars(
            select(models.RollCallSession).where(
                models.RollCallSession.scheduled_window_start_at == window_start,
            )
        ).first()
        if existing:
            log.info("跳过 rollcall session: %s %s 已存在", session_type, window_start)
            return
        db.add(
            models.RollCallSession(
                dorm_unit_set=[1, 2],
                session_type=session_type,
                schedule_mode="split",
                day_type="weekday",
                session_status="draft",
                scheduled_window_start_at=window_start,
                scheduled_on_time_end_at=window_start + timedelta(minutes=10),
                scheduled_late_end_at=window_start + timedelta(minutes=20),
                scheduled_auto_end_at=window_start + timedelta(minutes=30),
            )
        )
        log.info("加 rollcall session: %s %s", session_type, window_start)

    make_session("morning", 6, 30)
    make_session("evening", 22, 0)
    db.commit()

    log.info("=" * 60)
    log.info("dev seed 完成")
    log.info("学生 login: 060218 (留学生 リュウ) / 060103 (一般 田中)")
    log.info("教师 login: ryomu_buchou / ryomu_kachou / ...")
    log.info("password (全员共通): %s", DEV_PASSWORD)
    log.info("=" * 60)


# =============================================================
# Production seed（APP_ENV=production 用，VPS Postgres）
# =============================================================

# admin 教师 — itsuki 自己用，上线第一个 admin
PROD_ADMIN_TEACHER = dict(
    login_id="admin",
    name="管理者",
    email="otogi2025@gmail.com",
    role="寮務部長",
    assigned_dorm=None,
)

# Apple 审核员 / 老师体验用账号 — spec system_features.md §7.20
# 学号 999999（grade=99/class=99/seat=99）— 业务范围内不存在，schema 允许
PROD_REVIEWER_STUDENT = dict(
    grade_code="99",
    class_code="99",
    seat_no="99",
    name="App Reviewer",
    name_kana="アップル レビュアー",
    gender="male",
    category="一般寮生",
    room_no="M999",
    dorm_unit=1,
    is_overseas=False,
    email="reviewer@tomoshibi.cc",
    is_demo=True,  # 关键标志 — admin 学生列表 / 出席统计自动过滤
)
# A-014 (2026-05-21): reviewer 凭证从环境变量读，避免 public repo 暴露后门
# - production env 必须设置 REVIEWER_PASSWORD + REVIEWER_REGISTRATION_CODE
# - fallback 默认值仅 dev 兜底，上线 seed 时会 warn
PROD_REVIEWER_PASSWORD = os.environ.get(
    "REVIEWER_PASSWORD", "Tomoshibi-Reviewer-2026!"
)  # Apple Reviewer Notes 给（上线前必设 env）

# 审核员永久注册码 — spec §7.16 例外条款
# is_reviewer=True → 老师面板不可见 + refresh 不作废 + 永久有效
PROD_REVIEWER_REGISTRATION_CODE = os.environ.get(
    "REVIEWER_REGISTRATION_CODE", "999999"
)  # 上线前必设 env


def seed_prod(db) -> None:
    """production minimal 数据 — VPS Postgres 部署用。"""
    # A-014 (2026-05-21): reviewer 凭证 fallback warn
    if PROD_REVIEWER_PASSWORD == "Tomoshibi-Reviewer-2026!":
        log.warning(
            "⚠️ REVIEWER_PASSWORD env 未设，使用 fallback 默认密码。"
            "上线前必须设 env 变量 + Apple Reviewer Notes 写新密码。"
        )
    if PROD_REVIEWER_REGISTRATION_CODE == "999999":
        log.warning(
            "⚠️ REVIEWER_REGISTRATION_CODE env 未设，使用 fallback 默认码 999999（public repo 已知）。"
            "上线前必须设 env 变量为新随机 6 位数字。"
        )

    # admin 默认密码从 env 读（fallback 仅 dev 兜底；上线必须设 env）
    admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD", "ChangeMe-2026-05")
    if admin_password == "ChangeMe-2026-05":
        log.warning(
            "⚠️ ADMIN_INITIAL_PASSWORD env 未设，使用 fallback 默认密码。"
            "上线前必须设 env 变量 + 上线后立刻 web 后台改强密码。"
        )

    admin_pw_hash = security.hash_password(admin_password)
    reviewer_pw_hash = security.hash_password(PROD_REVIEWER_PASSWORD)

    # 1. admin 教师
    existing_admin = db.scalars(
        select(models.Teacher).where(
            models.Teacher.login_id == PROD_ADMIN_TEACHER["login_id"]
        )
    ).first()
    if existing_admin:
        log.info("admin 教师已存在 — 跳过")
    else:
        db.add(models.Teacher(**PROD_ADMIN_TEACHER, password_hash=admin_pw_hash))
        log.info(
            "加 admin 教师 login_id=%s role=%s",
            PROD_ADMIN_TEACHER["login_id"],
            PROD_ADMIN_TEACHER["role"],
        )

    # 2. reviewer 学生（is_demo=True）
    existing_reviewer = db.scalars(
        select(models.Student).where(
            models.Student.grade_code == PROD_REVIEWER_STUDENT["grade_code"],
            models.Student.class_code == PROD_REVIEWER_STUDENT["class_code"],
            models.Student.seat_no == PROD_REVIEWER_STUDENT["seat_no"],
        )
    ).first()
    if existing_reviewer:
        log.info("reviewer 学生已存在 — 跳过")
    else:
        student = models.Student(**PROD_REVIEWER_STUDENT)
        db.add(student)
        db.flush()
        db.add(models.Account(student_id=student.id, password_hash=reviewer_pw_hash))
        log.info("加 reviewer 学生 student_no=%s is_demo=True", student.student_no)

    db.commit()

    # 3. reviewer 注册码（is_reviewer=True 永久有效）
    admin = db.scalars(
        select(models.Teacher).where(
            models.Teacher.login_id == PROD_ADMIN_TEACHER["login_id"]
        )
    ).first()
    existing_code = db.scalars(
        select(models.StudentRegistrationCode).where(
            models.StudentRegistrationCode.code == PROD_REVIEWER_REGISTRATION_CODE,
            models.StudentRegistrationCode.is_reviewer.is_(True),
            models.StudentRegistrationCode.invalidated_at.is_(None),
        )
    ).first()
    if existing_code:
        log.info("reviewer 注册码已存在 — 跳过")
    elif admin:
        # 远期 expires（2099-01-01）— is_reviewer=True 已确保永久有效，expires_at 仅占位
        # 用 99 年后是为了防 _validate_registration_code 把它判过期（多重保险）
        far_future = datetime(2099, 1, 1, tzinfo=timezone.utc)
        db.add(
            models.StudentRegistrationCode(
                code=PROD_REVIEWER_REGISTRATION_CODE,
                created_by=admin.id,
                expires_at=far_future,
                is_reviewer=True,
            )
        )
        log.info(
            "加 reviewer 注册码 code=%s is_reviewer=True",
            PROD_REVIEWER_REGISTRATION_CODE,
        )

    db.commit()

    log.info("=" * 60)
    log.info("production seed 完成（最小必要数据）")
    log.info(
        "admin login: %s / 密码: %s",
        PROD_ADMIN_TEACHER["login_id"],
        "(env ADMIN_INITIAL_PASSWORD)"
        if admin_password != "ChangeMe-2026-05"
        else "ChangeMe-2026-05 ⚠️ fallback",
    )
    log.info("reviewer 学号: 999999 / 密码: %s", PROD_REVIEWER_PASSWORD)
    log.info(
        "reviewer 注册码: %s (is_reviewer=True 永久)", PROD_REVIEWER_REGISTRATION_CODE
    )
    log.info("=" * 60)


# =============================================================
# Entry point
# =============================================================


def main() -> None:
    create_all()
    db = SessionLocal()
    try:
        env = os.environ.get("APP_ENV", "dev").lower()
        log.info("APP_ENV=%s", env)
        if env == "production":
            seed_prod(db)
        else:
            seed_dev(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
