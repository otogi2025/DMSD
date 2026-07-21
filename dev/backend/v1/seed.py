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
    cd dev/backend/v1
    APP_ENV=dev python -m seed         # 本机 dev 用
    APP_ENV=production python -m seed  # VPS 部署用
"""

from __future__ import annotations

import logging
import os
import uuid
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

# dev 本机 op（系统最高运维账号）密码 —— 仅本机 SQLite 用，方便测「登录页系统管理者入口」。
# ⚠️ 生产环境绝不用这个：seed_prod 仍只在 env OP_PASSWORD 设置时建 op，密码绝不入仓库（安全铁律）。
DEV_OP_PASSWORD = "op123456"

# dev 纯 demo：现在还没人注册，真实学生 / 老师一律不建种子，全走 _seed_demo_data 的演示数据
# itsuki 拍板：删 shingu，dev 只留 demo 账号，学生名字之类的只放 demo
DEV_STUDENTS = []

DEV_TEACHERS = []


def seed_dev(db) -> None:
    """dev dummy 数据 — 本机 SQLite 开发用（纯 demo：只建演示老师 + 演示学生 + op 运维账号）。"""
    # itsuki 拍板：dev 只留 demo 账号 → 先建演示数据，后面的学习名簿 / 校车便都挂到 demo 上
    _seed_demo_data(db)

    # op 运维账号（最高权限，permission_group="op"）—— 登录页不上墙，走「ログイン」单独入口
    # （输 login_id="op" + 密码登录）。dev 本机用已知密码方便测；幂等，重复跑不重建。
    # ⚠️ 安全护栏：只在 SQLite 库（= 本机 dev）建这个已知密码 op，防 `python -m seed` 在
    # 生产（Postgres）漏设 APP_ENV=production 时误走 dev 分支、建出 op123456 账户。生产 op
    # 永远走 seed_prod 的 env OP_PASSWORD 路径。
    from app.config import get_settings

    if not get_settings().is_sqlite:
        log.warning(
            "非 SQLite 库（疑似生产）— 跳过 dev op 账号创建，op 应走 seed_prod + OP_PASSWORD"
        )
    else:
        existing_op = db.scalars(
            select(models.Teacher).where(
                models.Teacher.login_id == OP_TEACHER["login_id"]
            )
        ).first()
        if existing_op:
            log.info("op 账号已存在 — 跳过")
        else:
            db.add(
                models.Teacher(
                    **OP_TEACHER, password_hash=security.hash_password(DEV_OP_PASSWORD)
                )
            )
            log.info("加 op 账号 login_id=op（密码见 seed.py 常量 DEV_OP_PASSWORD）")
        db.commit()

    pw_hash = security.hash_password(DEV_PASSWORD)

    # B-低-22：DEV_STUDENTS / DEV_TEACHERS / homeroom_pairs 当前都是空列表（dev 纯 demo），
    # 下面三段循环加 if 短路 —— 既明示「当前不执行」、又保留这些列表作为将来重新填真实
    # 种子时的扩展点（直接往列表里加 dict 即可，无需重写循环体）。
    # 学生
    if DEV_STUDENTS:
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
    if DEV_TEACHERS:
        for t_data in DEV_TEACHERS:
            existing = db.scalars(
                select(models.Teacher).where(
                    models.Teacher.login_id == t_data["login_id"]
                )
            ).first()
            if existing:
                log.info("跳过教师: %s 已存在", t_data["login_id"])
                continue
            teacher = models.Teacher(**t_data, password_hash=pw_hash)
            db.add(teacher)
            log.info("加教师: %s (role=%s)", teacher.login_id, teacher.role)

    db.commit()

    # 担任绑定
    homeroom_pairs: list[tuple[str, str, str]] = []
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

    # 学习名簿（晚自习对象）
    # demo 演示故意留 1 名演示学生（学号 980401，演示学生花子）不进名簿，演示「非晚自习对象」的
    # 样子，不再让 demo 学生全员默认开 —— 更贴真实规则「中学全员 + 高中手动追加」。
    study_roster_demo_exclude = {
        "980401"
    }  # 学号 980401 演示学生花子：演示「非晚自习对象」
    # 只给演示学生建名簿，防误跑到含真实学生的库时污染真实学生
    all_students = db.scalars(
        select(models.Student).where(models.Student.is_demo == True)  # noqa: E712
    ).all()
    for student in all_students:
        if student.student_no in study_roster_demo_exclude:
            continue
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

    def make_session(
        session_type: str, h: int, m: int, dorm_unit_set: list[int]
    ) -> None:
        window_start = datetime(
            today_jst.year, today_jst.month, today_jst.day, h, m, tzinfo=JST
        )
        # 按 dedupe_key 判重（同窗不同寮集合是两条场次，不能只比 window_start）
        key = models.rollcall_dedupe_key(today_jst, session_type, dorm_unit_set)
        existing = db.scalars(
            select(models.RollCallSession).where(
                models.RollCallSession.dedupe_key == key,
            )
        ).first()
        if existing:
            log.info(
                "跳过 rollcall session: %s %s dorm=%s 已存在",
                session_type,
                window_start,
                dorm_unit_set,
            )
            return
        db.add(
            models.RollCallSession(
                dorm_unit_set=dorm_unit_set,
                session_type=session_type,
                schedule_mode="split",
                day_type="weekday",
                session_status="draft",
                scheduled_window_start_at=window_start,
                scheduled_on_time_end_at=window_start + timedelta(minutes=10),
                scheduled_late_end_at=window_start + timedelta(minutes=20),
                scheduled_auto_end_at=window_start + timedelta(minutes=30),
                # 审查 backend#17：防重键（uq_rcs_dedupe_key 唯一索引）
                dedupe_key=key,
            )
        )
        log.info(
            "加 rollcall session: %s %s dorm=%s",
            session_type,
            window_start,
            dorm_unit_set,
        )

    # 男寮 [1,2] + 女寮 [4] 各一条，与 DEMO_STUDENTS / demo_study assigned_dorm=4 对齐
    make_session("morning", 6, 30, [1, 2])
    make_session("morning", 6, 30, [4])
    make_session("evening", 22, 0, [1, 2])
    make_session("evening", 22, 0, [4])
    db.commit()

    # 巴士便 + 行事日历 — 抽成共用函数（dev / production 都种，挂演示老师名下）
    _seed_bus_routes(db)
    _seed_dorm_events(db)

    log.info("=" * 60)
    log.info("dev seed 完成（纯 demo）")
    log.info(
        "演示老师 login: demo / demo_general / demo_study / demo_approval（密码 demo123 共通）"
    )
    log.info("演示学生 login: 980101 980201 980401（密码 demo123）")
    log.info(
        "op 运维账号 login: op（密码见 seed.py 常量 DEV_OP_PASSWORD，走登录页系统管理者入口）"
    )
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
    permission_group="寮管理者",  # 全权限·个人（teacher_permission_v1.md §3）
    assigned_dorm=None,
)

# op 账号（系统最高运维账号，teacher_permission_v1.md §7）— 全权限·非个人。
# 密码绝不入仓库 / 迁移 / seed：seed 时从环境变量 OP_PASSWORD 读取，缺失则不建 op（不设缺省值）。
# role 仅显示用、不参与鉴权；权限由 permission_group="op" 决定。
OP_TEACHER = dict(
    login_id="op",
    name="システム管理 (op)",
    email=os.environ.get("OP_EMAIL", "op@tomoshibi.example"),
    role="寮務部長",
    permission_group="op",
    assigned_dorm=None,
    is_demo=False,
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
    # H-13：改走 env，默认 .example 占位（与 OP_EMAIL 同款）。原硬编码真实域名
    # reviewer@tomoshibi.cc，审批通过会往真实邮箱发邮件 —— 部署时显式设 REVIEWER_EMAIL 才用真域名。
    email=os.environ.get("REVIEWER_EMAIL", "reviewer@tomoshibi.example"),
    is_demo=True,  # 关键标志 — admin 学生列表 / 出席统计自动过滤
)

# 宿舍演示 / Apple 审核用「演示老师 + 演示学生」（is_demo=True，对真老师全隐身）。
# itsuki 拍板：登录页每个权限组各放一个 demo 老师，方便演示 / 体验不同权限的界面。
# 4 个权限组各一个（op 运维组不在登录页上墙、不建 demo —— op 走单独入口，见 seed_dev 的 op 段）。
# 全部 is_demo=True、共用密码（取 env DEMO_TEACHER_PASSWORD，缺失用 "demo123"）。
# 第 0 个 login_id="demo"（寮管理者）是主演示老师 —— 巴士便 / 演示公告都挂它名下（下面靠 login_id 查）。
DEMO_TEACHERS = [
    dict(
        login_id="demo",
        name="デモ",
        email="demo-teacher@tomoshibi.example",
        role="寮務部長",  # 跨寮 → 演示老师能看到所有演示寮（1/2/4）的演示学生
        permission_group="寮管理者",  # 全功能可见（演示数据范围内）
        assigned_dorm=None,
        is_demo=True,
    ),
    dict(
        login_id="demo_general",
        name="デモ（一般）",
        email="demo-general@tomoshibi.example",
        role="管理係",  # 一般宿管 对应职位
        permission_group="一般宿管",  # 受限：日常运营，无晚自习/学习管理
        assigned_dorm=1,  # 男子寮
        is_demo=True,
    ),
    dict(
        login_id="demo_study",
        name="デモ（夜学習）",
        email="demo-study@tomoshibi.example",
        role="寮監",  # 一般宿管+晚自习 对应职位
        permission_group="一般宿管+晚自习",  # 存储值用「晚自习」，UI 显示「夜学習」
        assigned_dorm=4,  # 女子寮（演示不同寮的样子）
        is_demo=True,
    ),
    dict(
        login_id="demo_approval",
        name="デモ（承認）",
        email="demo-approval@tomoshibi.example",
        role="国際交流部長",  # 申請承認専用 对应职位
        permission_group="申請承認専用",  # 以审批为核心，其余只读
        assigned_dorm=None,
        is_demo=True,
    ),
]
# 主演示老师（巴士便 / 演示公告挂它名下）—— 第 0 个 = 寮管理者 login_id="demo"
DEMO_TEACHER = DEMO_TEACHERS[0]
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

# 演示宿舍公告（is_demo=True，挂演示老师名下）— 与 iOS 演示版本地 SEED.swift 内容一字对齐
# （itsuki 提供的真实宿舍公告原文，新谷和之 寮監 · Google Classroom，纯日语不含翻译）。
# id 用固定 UUID（与 iOS SEED 的 AAAA000x 段一致），幂等检查按 id；scope 全 all（同 iOS）。
# created_at 用「现在往前推 days_ago 天」还原时间线（同 iOS Date().addingTimeInterval(-86400*N)）。
DEMO_ANNOUNCEMENTS = [
    dict(
        id=uuid.UUID("aaaa0001-0000-0000-0000-000000000001"),
        title="ごみの捨て方について",
        body=(
            "昨日の罰則清掃時に複数個所で飲みかけのペットボトル，缶が捨ててあり，コバエが飛んでいました。\n"
            "今後，特に飲食物を捨てる場合は全て空にした状態で捨てるようにして下さい。\n"
            "寮内が臭くなり，不衛生となります。\n"
            "衛生環境を整えるように一人一人が意識して気を付けるようにして下さい。\n"
            "また，清掃分担でゴミ捨ての担当者はゴミの状況を確認して早めに捨てるようにしましょう。"
        ),
        scope="all",
        days_ago=1,
    ),
    dict(
        id=uuid.UUID("aaaa0002-0000-0000-0000-000000000002"),
        title="廊下のコンセントの利用について",
        body=(
            "①サッカー部\n"
            "・現状，サッカー部の靴乾燥機に使用している寮生が多いですが，廊下のコンセントを使う場合は盗電扱いとなります。盗電は犯罪です。譲歩策として本日から廊下のコンセントの使用をなくし，部屋のコンセントを使用して廊下に出して使用して下さい。\n"
            "※またはトレーニングルームで乾燥をするようにして下さい（現在相談中のため現時点では上記で乾燥をするように）。\n"
            "②一般生\n"
            "・一般生の中にも廊下のコンセントを使用している生徒がいます。本日より，使用しないようにして下さい。上記同様，盗電扱いです。\n"
            "③廊下のコンセント使用可能な場合の事例\n"
            "・普段の寮清掃時の掃除機等の使用（個人的使用は不可）\n"
            "・特別な許可を得ている場合（相談は新谷まで）\n"
            "・個室のコンセントの不具合等で使用ができない場合（代替措置）"
        ),
        scope="all",
        days_ago=3,
    ),
    dict(
        id=uuid.UUID("aaaa0003-0000-0000-0000-000000000003"),
        title="男子寮防災訓練について",
        body=(
            "明日の学習時間に男子のみ防災訓練があります。\n"
            "男子生徒は学習に参加せず，寮での待機となります。\n"
            "ただし，全体が遅くなった場合は学習を行いますので，全員が速やかに避難できるように放送を注意して聞いてください。\n"
            "また，イヤホンをしていて放送を聞いていない，お風呂に入っていたなどの理由で防災訓練に参加しなかった場合は指導の対象となります。\n"
            "※女子は通常通り学習があります。"
        ),
        scope="all",
        days_ago=3,
    ),
    dict(
        id=uuid.UUID("aaaa0004-0000-0000-0000-000000000004"),
        title="夜学習について",
        body=(
            "6月5日（金）は夜学習は自室学習となります。\n"
            "自由時間ではないので，必ず学習に取り組むように。"
        ),
        scope="all",
        days_ago=8,
    ),
    dict(
        id=uuid.UUID("aaaa0005-0000-0000-0000-000000000005"),
        title="ホタル祭りについて",
        body=(
            "◯ホタル祭りに参加する寮生の注意事項\n"
            "１．ホタル祭りに参加する生徒は外出簿に記名し，鍵を提出すること。\n"
            "２．ホタルの見学に参加する生徒は必ず男子寮玄関前に20:00に集合し，指示に従うこと。\n"
            "３．ホタル祭りに参加する生徒の最終門限は21:30として，その場で点呼（健康観察）。\n"
            "４．ホタル祭りに参加した生徒の入浴は23:00までとする（浴室のシャワー，個室のシャワーを使用すること）\n"
            "５．30日土曜日の清掃は自室の清掃をしっかりすること。\n"
            "◯ホタル祭りに参加しない生徒の注意事項\n"
            "１．通常の寮の休日時程に準ずる（門限は19:50，点呼は20:00）。\n"
            "２．30日土曜日の清掃は自室の清掃をしっかりすること。"
        ),
        scope="all",
        days_ago=13,
    ),
    dict(
        id=uuid.UUID("aaaa0006-0000-0000-0000-000000000006"),
        title="金銭のやり取りについて",
        body=(
            "寮生間での金銭のやり取りは禁止しています。\n"
            "金銭を渡して，雑用や課題（宿題）をしてもらうことは絶対してはいけません。\n"
            "それ以外でも金銭が関わることについては絶対にしないように。"
        ),
        scope="all",
        days_ago=29,
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

    # 1b. op 账号（最高运维，teacher_permission_v1.md §7）— 仅当 OP_PASSWORD 设置时建。
    # 密码绝不入仓库；环境变量缺失则跳过（不设缺省值）。
    op_password = os.environ.get("OP_PASSWORD")
    if not op_password:
        log.info("OP_PASSWORD 未设置 — 跳过建 op 账号（teacher_permission_v1 §7）")
    else:
        existing_op = db.scalars(
            select(models.Teacher).where(
                models.Teacher.login_id == OP_TEACHER["login_id"]
            )
        ).first()
        if existing_op:
            log.info("op 账号已存在 — 跳过")
        else:
            db.add(
                models.Teacher(
                    **OP_TEACHER, password_hash=security.hash_password(op_password)
                )
            )
            log.info("加 op 账号 login_id=op permission_group=op")

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

    # 4b. 演示巴士便 + 行事日历 — 同样挂演示老师名下（接口按创建者 is_demo 过滤），
    # 审核员打开 バス / 行事 页不再空白；真实学生看不到这批数据
    _seed_bus_routes(db)
    _seed_dorm_events(db)

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

    # 演示老师 —— 每个权限组各一个（幂等，逐个按 login_id 查重）
    for t_data in DEMO_TEACHERS:
        existing_demo_teacher = db.scalars(
            select(models.Teacher).where(models.Teacher.login_id == t_data["login_id"])
        ).first()
        if existing_demo_teacher:
            log.info("演示老师 %s 已存在 — 跳过", t_data["login_id"])
            continue
        db.add(models.Teacher(**t_data, password_hash=demo_pw_hash))
        log.info(
            "加演示老师 login_id=%s group=%s is_demo=True",
            t_data["login_id"],
            t_data["permission_group"],
        )

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

    # 演示公告（is_demo=True，挂演示老师名下）— 幂等，按固定 id 检查，重复跑不重建。
    # 演示老师 / 演示学生看得到，真老师 / 真实学生被 is_demo 隔离过滤掉，上线不污染。
    demo_teacher = db.scalars(
        select(models.Teacher).where(
            models.Teacher.login_id == DEMO_TEACHER["login_id"]
        )
    ).first()
    if demo_teacher:
        for a_data in DEMO_ANNOUNCEMENTS:
            if db.get(models.Announcement, a_data["id"]):
                log.info("演示公告「%s」已存在 — 跳过", a_data["title"])
                continue
            created = datetime.now(timezone.utc) - timedelta(days=a_data["days_ago"])
            db.add(
                models.Announcement(
                    id=a_data["id"],
                    title=a_data["title"],
                    body=a_data["body"],
                    scope=a_data["scope"],
                    author_teacher_id=demo_teacher.id,
                    is_demo=True,
                    created_at=created,
                    updated_at=created,
                )
            )
            log.info("加演示公告「%s」is_demo=True", a_data["title"])
        db.commit()


def _seed_bus_routes(db) -> None:
    """巴士便种子（spec §7.6）— 寮生特別運行（dorm_special）+ 平日通学便（daily_commute）。

    dev / production 共用：全挂 login_id="demo" 演示老师名下（created_by_teacher_id）。
    bus_routes 表无 is_demo 列，隔离靠接口按创建者 is_demo 过滤（bus_routes.py）——
    演示账号（含 Apple 审核员）可见、真实学生不可见。
    幂等：按 name + schedule_at 查重跳过。数据内容与原 seed_dev 内联版一字未改。
    iOS BusListView / 老师网页 都靠 GET /api/v1/bus/routes 读这批数据。
    """
    JST = timezone(timedelta(hours=9))
    demo_teacher = db.scalars(
        select(models.Teacher).where(models.Teacher.login_id == "demo")
    ).first()
    if demo_teacher:
        # (kind, name, direction, 月, 日, 出发时, 出发分, 到达时, 到达分(无则 None), visible_to, note)
        bus_rows = [
            # ── 寮生特別運行便：外宿 / 回家 / 购物 / 回国机场接送 ──
            (
                "dorm_special",
                "外泊・帰省 朝便",
                "高校棟 → 岡山駅西口",
                8,
                13,
                7,
                30,
                8,
                25,
                "dorm_only",
                "8/13 外泊・帰省者向け特別運行便。",
            ),
            (
                "dorm_special",
                "外泊・帰省 金川便",
                "高校棟 → 金川駅",
                8,
                13,
                10,
                10,
                10,
                35,
                "dorm_only",
                "8/13 買い物・帰省者向け。",
            ),
            (
                "dorm_special",
                "帰寮 夕便",
                "金川駅 → 寮",
                8,
                15,
                17,
                31,
                17,
                55,
                "dorm_only",
                "8/15 帰寮日。乗車名簿への事前チェック必要。",
            ),
            (
                "dorm_special",
                "空港送迎便（帰国）",
                "寮 → 岡山空港",
                8,
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
                8,
                25,
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
                8,
                25,
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
                8,
                25,
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
                    created_by_teacher_id=demo_teacher.id,
                )
            )
            log.info("加巴士便: %s %s", name, schedule_at)
        db.commit()


# 演示行事日历（spec §7.5）— 合理假数据（itsuki 拍板：审核员打开行事页不空白即可）。
# dorm_events 表无 is_demo 列，隔离靠接口按创建者 is_demo 过滤（events.py）——
# 挂演示老师名下 → 演示账号（含审核员）可见、真实学生不可见。
# id 用固定 UUID（bbbb 段，避开公告 aaaa 段），幂等按 id 查重。
DEMO_EVENTS = [
    dict(
        id=uuid.UUID("bbbb0001-0000-0000-0000-000000000001"),
        title="夏季休業前 大掃除",
        category="寮行事",
        event_date=date(2026, 7, 23),
        description="帰省前の全体大掃除。分担表は各階の掲示板を確認すること。",
    ),
    dict(
        id=uuid.UUID("bbbb0002-0000-0000-0000-000000000002"),
        title="1学期終業式・帰省開始",
        category="学校行事",
        event_date=date(2026, 7, 24),
        description="終業式後、帰省届提出者から順次帰省。",
    ),
    dict(
        id=uuid.UUID("bbbb0003-0000-0000-0000-000000000003"),
        title="帰寮日（夏季休業明け）",
        category="寮行事",
        event_date=date(2026, 8, 24),
        description="21:00 までに帰寮し、点呼を受けること。",
    ),
    dict(
        id=uuid.UUID("bbbb0004-0000-0000-0000-000000000004"),
        title="防災訓練",
        category="学校行事",
        event_date=date(2026, 9, 1),
        description="夜学習の時間帯に実施。放送の指示に従うこと。",
    ),
    dict(
        id=uuid.UUID("bbbb0005-0000-0000-0000-000000000005"),
        title="体育祭",
        category="学校行事",
        event_date=date(2026, 10, 10),
        description=None,
    ),
    dict(
        id=uuid.UUID("bbbb0006-0000-0000-0000-000000000006"),
        title="寮祭",
        category="寮行事",
        event_date=date(2026, 11, 14),
        description="実行委員は前日 19:00 から準備。",
    ),
    dict(
        id=uuid.UUID("bbbb0007-0000-0000-0000-000000000007"),
        title="冬季休業前 大掃除・帰省開始",
        category="寮行事",
        event_date=date(2026, 12, 22),
        description=None,
    ),
    dict(
        id=uuid.UUID("bbbb0008-0000-0000-0000-000000000008"),
        title="帰寮日（冬季休業明け）",
        category="寮行事",
        event_date=date(2027, 1, 7),
        description="21:00 までに帰寮し、点呼を受けること。",
    ),
]


def _seed_dorm_events(db) -> None:
    """行事日历种子（spec §7.5）— 演示假数据，dev / production 共用。

    全部全天行事（start_at / end_at = NULL），notify_students=False（不触发推送）。
    幂等：按固定 id 查重，重复跑不重建。
    """
    demo_teacher = db.scalars(
        select(models.Teacher).where(models.Teacher.login_id == "demo")
    ).first()
    if not demo_teacher:
        log.info("演示老师不存在 — 跳过行事种子")
        return
    for e in DEMO_EVENTS:
        if db.get(models.DormEvent, e["id"]):
            log.info("演示行事「%s」已存在 — 跳过", e["title"])
            continue
        db.add(
            models.DormEvent(
                id=e["id"],
                title=e["title"],
                category=e["category"],
                event_date=e["event_date"],
                description=e["description"],
                created_by_teacher_id=demo_teacher.id,
                notify_students=False,
            )
        )
        log.info("加演示行事「%s」%s", e["title"], e["event_date"])
    db.commit()


# =============================================================
# Entry point
# =============================================================


def main() -> None:
    from app.config import get_settings

    # 只在本机 SQLite 建表；生产/staging 表由 alembic 迁移建，seed 不碰（防与 alembic_version 漂移）
    if get_settings().is_sqlite:
        create_all()
    db = SessionLocal()
    try:
        env = os.environ.get("APP_ENV", "dev").lower()
        log.info("APP_ENV=%s", env)
        # 审查 backend#11：env 只可能是 dev/staging/production —— 上面 get_settings() 已用
        # config.app_env（Literal["dev","staging","production"]）校验过，别的值在那一步就
        # 抛 ValidationError、到不了这里。原白名单里的 development/local/test 是够不到的死分支，
        # 收窄成只认 dev，避免「看起来支持其实永远进不来」的误导。
        if env == "production":
            seed_prod(db)
        elif env == "dev":
            seed_dev(db)
        else:
            # staging（唯一能到这里的非 dev/prod 值）拒绝执行，防误种演示数据
            log.error("APP_ENV=%s 不允许 seed（防 staging 误种演示数据）", env)
            raise SystemExit(f"APP_ENV={env} 不允许 seed（防 staging 误种演示数据）")
    finally:
        db.close()


if __name__ == "__main__":
    main()
