"""seed — 双模式数据投入（dev dummy / production minimal）。

通过环境变量 APP_ENV 切换：
    APP_ENV=dev (default) → dev dummy seed（dummy 学生 2 + 教师 1 + 点呼 session 2 + 学习名簿）
    APP_ENV=production    → production seed（admin 教师 1 + reviewer 学生 1 + reviewer 注册码 1）

production seed 拍板规则（详见 system_features.md §7.20 + §7.16 例外条款）：
    - admin 密码必须通过 env ADMIN_INITIAL_PASSWORD 设置（缺失则拒绝执行）
    - reviewer 学号 999999（grade=99/class=99/seat=99，schema 允许，业务不存在）
    - reviewer 密码必须通过 env REVIEWER_PASSWORD 设置（缺失则拒绝执行）
    - reviewer 学生 is_demo=True → admin 学生列表 / 出席统计自动过滤
    - reviewer 注册码必须通过 env REVIEWER_REGISTRATION_CODE 设置（缺失则拒绝执行）
    - is_reviewer=True → 老师面板不可见 + refresh 不作废 + 永久有效

执行：
    cd 03_dev/backend/v1
    APP_ENV=dev python -m seed         # 本机 dev 用
    APP_ENV=production python -m seed  # VPS 部署用
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo

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
        login_id="shingu",
        name="新股",
        email="shingu@example.jp",
        role="寮務部長",
        assigned_dorm=None,
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
    homeroom_pairs = []
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
    today_jst = datetime.now(
        ZoneInfo("Asia/Tokyo")
    ).date()  # 机器时区无关，始终取日本日期

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

    # 巴士便（spec §7.6）— 寮生特別運行（dorm_special）+ 平日通学便（daily_commute）。
    # 全挂到役职老师 shingu（寮務部長）名下，作为 created_by_teacher_id。
    # iOS BusListView / 老师网页 都靠 GET /api/v1/bus/routes 读这批数据。
    shingu = db.scalars(
        select(models.Teacher).where(models.Teacher.login_id == "shingu")
    ).first()
    if shingu:
        # (kind, name, direction, 月, 日, 出发时, 出发分, 到达时, 到达分(无则 None), visible_to, note)
        bus_rows = [
            # ── 寮生特別運行便：外宿 / 回家 / 购物 / 回国机场接送 ──
            (
                "dorm_special",
                "外泊・帰省 朝便",
                "高校棟 → 岡山駅西口",
                6,
                13,
                7,
                30,
                8,
                25,
                "dorm_only",
                "6/13 外泊・帰省者向け特別運行便。",
            ),
            (
                "dorm_special",
                "外泊・帰省 金川便",
                "高校棟 → 金川駅",
                6,
                13,
                10,
                10,
                10,
                35,
                "dorm_only",
                "6/13 買い物・帰省者向け。",
            ),
            (
                "dorm_special",
                "帰寮 夕便",
                "金川駅 → 寮",
                6,
                15,
                17,
                31,
                17,
                55,
                "dorm_only",
                "6/15 帰寮日。乗車名簿への事前チェック必要。",
            ),
            (
                "dorm_special",
                "空港送迎便（帰国）",
                "寮 → 岡山空港",
                6,
                20,
                9,
                0,
                9,
                50,
                "dorm_only",
                "帰国届提出者向け。空港送迎便。",
            ),
            # ── 平日上下学班车 ──
            (
                "daily_commute",
                "西口登校便",
                "岡山駅西口 → 高校棟",
                6,
                8,
                7,
                0,
                7,
                45,
                "all",
                None,
            ),
            (
                "daily_commute",
                "金川登校便",
                "金川駅 → 高校棟",
                6,
                8,
                7,
                10,
                7,
                40,
                "all",
                None,
            ),
            (
                "daily_commute",
                "西口下校便",
                "高校棟 → 岡山駅西口",
                6,
                8,
                18,
                45,
                19,
                30,
                "all",
                None,
            ),
        ]
        for kind, name, direction, mo, d, sh, sm, ah, am, vis, note in bus_rows:
            schedule_at = datetime(2026, mo, d, sh, sm, tzinfo=JST)
            arrival_at = (
                datetime(2026, mo, d, ah, am, tzinfo=JST) if ah is not None else None
            )
            existing = db.scalars(
                select(models.BusRoute).where(
                    models.BusRoute.name == name,
                    models.BusRoute.schedule_at == schedule_at,
                )
            ).first()
            if existing:
                continue
            db.add(
                models.BusRoute(
                    kind=kind,
                    name=name,
                    direction=direction,
                    schedule_at=schedule_at,
                    arrival_at=arrival_at,
                    visible_to=vis,
                    note=note,
                    created_by_teacher_id=shingu.id,
                )
            )
            log.info("加巴士便: %s %s", name, schedule_at)
        db.commit()

    # itsuki 拍板 B：dev 也建演示数据（演示账号开发期开箱即用，跟 prod 一致）
    _seed_demo_data(db)

    log.info("=" * 60)
    log.info("dev seed 完成")
    log.info("学生 login: 060218 (留学生 リュウ) / 060103 (一般 田中)")
    log.info("教师 login: shingu (新股)")
    log.info("password (全员共通): %s", DEV_PASSWORD)
    log.info("=" * 60)


# =============================================================
# Production seed（APP_ENV=production 用，VPS Postgres）
# =============================================================

# admin 教师 — itsuki 自己用，上线第一个 admin
PROD_ADMIN_TEACHER = dict(
    login_id="admin",
    name="管理者",
    # admin 邮箱用环境变量（生产部署设 ADMIN_EMAIL=真邮箱，不入仓库）；默认占位，不暴露隐私也不跟学生 demo 邮箱撞
    email=os.environ.get("ADMIN_EMAIL", "admin@tomoshibi.example"),
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

# 宿舍演示 / Apple 审核用「演示老师 + 演示学生」（is_demo=True，对真老师全隐身）
# opt-in：仅当 env DEMO_TEACHER_PASSWORD 设置时建（缺失跳过，不破坏现有部署）
DEMO_TEACHER = dict(
    login_id="demo",
    name="デモ教員",
    email="demo-teacher@tomoshibi.example",
    role="寮務部長",  # 跨寮 → 演示老师能看到所有演示寮（1/2/4）的演示学生
    assigned_dorm=None,
    is_demo=True,
)
# 演示学生学号用 98xxxx 段（避开真实学年 01-06 + reviewer 999999），覆盖男/女寮
DEMO_STUDENTS = [
    dict(
        grade_code="98",
        class_code="01",
        seat_no="01",
        name="デモ 一郎",
        name_kana="デモ イチロウ",
        gender="male",
        category="一般寮生",
        room_no="M101",
        dorm_unit=1,
        is_overseas=False,
        email="demo-s1@tomoshibi.example",
        is_demo=True,
    ),
    dict(
        grade_code="98",
        class_code="02",
        seat_no="01",
        name="デモ 二郎",
        name_kana="デモ ジロウ",
        gender="male",
        category="一般寮生",
        room_no="M201",
        dorm_unit=2,
        is_overseas=True,
        email="demo-s2@tomoshibi.example",
        is_demo=True,
    ),
    dict(
        grade_code="98",
        class_code="04",
        seat_no="01",
        name="デモ 花子",
        name_kana="デモ ハナコ",
        gender="female",
        category="一般寮生",
        room_no="W401",
        dorm_unit=4,
        is_overseas=False,
        email="demo-s3@tomoshibi.example",
        is_demo=True,
    ),
]


def seed_prod(db) -> None:
    """production minimal 数据 — VPS Postgres 部署用。

    production 模式下三个凭证 env 变量必须全部显式设置，任一缺失直接 raise 拒绝执行：
        ADMIN_INITIAL_PASSWORD      — admin 教师初始密码
        REVIEWER_PASSWORD           — Apple 审核员账号密码
        REVIEWER_REGISTRATION_CODE  — 审核员永久注册码（is_reviewer=True）
    """
    # SEC-4: production 凭证 fail-fast 校验 — 三个 env 任一缺失就拒绝执行，不允许 fallback 默认值
    _missing = []
    admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD")
    if not admin_password:
        _missing.append("ADMIN_INITIAL_PASSWORD")

    reviewer_password = os.environ.get("REVIEWER_PASSWORD")
    if not reviewer_password:
        _missing.append("REVIEWER_PASSWORD")

    reviewer_registration_code = os.environ.get("REVIEWER_REGISTRATION_CODE")
    if not reviewer_registration_code:
        _missing.append("REVIEWER_REGISTRATION_CODE")

    if _missing:
        raise RuntimeError(
            "Production seed 拒绝执行：以下环境变量未设置 → "
            + ", ".join(_missing)
            + "。请在服务器 .env 或部署脚本里显式设置这些变量后再运行 seed。"
        )

    admin_pw_hash = security.hash_password(admin_password)
    reviewer_pw_hash = security.hash_password(reviewer_password)

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
            models.StudentRegistrationCode.code == reviewer_registration_code,
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
                code=reviewer_registration_code,
                created_by=admin.id,
                expires_at=far_future,
                is_reviewer=True,
            )
        )
        log.info(
            "加 reviewer 注册码 code=%s is_reviewer=True",
            reviewer_registration_code,
        )

    db.commit()

    # 4. 演示数据（opt-in）— 演示老师 + 演示学生，全 is_demo=True，对真老师隐身
    _seed_demo_data(db)

    log.info("=" * 60)
    log.info("production seed 完成（最小必要数据）")
    log.info(
        "admin login: %s / 密码来自: env ADMIN_INITIAL_PASSWORD",
        PROD_ADMIN_TEACHER["login_id"],
    )
    log.info("reviewer 学号: 999999 / 密码来自: env REVIEWER_PASSWORD")
    log.info(
        "reviewer 注册码来自: env REVIEWER_REGISTRATION_CODE (is_reviewer=True 永久)"
    )
    log.info("=" * 60)


# =============================================================
# 演示数据（opt-in）
# =============================================================


def _seed_demo_data(db) -> None:
    """演示老师 + 演示学生（全 is_demo=True）— 默认启用（itsuki 拍板：演示账号开箱即用）。

    演示老师登录只看演示学生（is_demo=True），真老师看不到任何演示数据（is_demo 隔离）。
    密码取 env DEMO_TEACHER_PASSWORD，缺失则用默认 "demo123"
    （演示账号被 is_demo 隔离限死、碰不到真实数据，公开密码可接受）。幂等，重复跑不重建。
    """
    # 密码 env 优先，缺失用默认 "demo123"（演示账号被 is_demo 隔离，碰不到真实数据）
    demo_password = os.environ.get("DEMO_TEACHER_PASSWORD") or "demo123"

    demo_pw_hash = security.hash_password(demo_password)

    # 演示老师（幂等）
    existing_demo_teacher = db.scalars(
        select(models.Teacher).where(
            models.Teacher.login_id == DEMO_TEACHER["login_id"]
        )
    ).first()
    if existing_demo_teacher:
        log.info("演示老师已存在 — 跳过")
    else:
        db.add(models.Teacher(**DEMO_TEACHER, password_hash=demo_pw_hash))
        log.info("加演示老师 login_id=%s is_demo=True", DEMO_TEACHER["login_id"])

    # 演示学生（幂等，各建 Account 共用演示密码）
    for s_data in DEMO_STUDENTS:
        existing = db.scalars(
            select(models.Student).where(
                models.Student.grade_code == s_data["grade_code"],
                models.Student.class_code == s_data["class_code"],
                models.Student.seat_no == s_data["seat_no"],
            )
        ).first()
        if existing:
            log.info(
                "演示学生 %s%s%s 已存在 — 跳过",
                s_data["grade_code"],
                s_data["class_code"],
                s_data["seat_no"],
            )
            continue
        student = models.Student(**s_data)
        db.add(student)
        db.flush()
        db.add(models.Account(student_id=student.id, password_hash=demo_pw_hash))
        log.info("加演示学生 student_no=%s is_demo=True", student.student_no)

    db.commit()


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
