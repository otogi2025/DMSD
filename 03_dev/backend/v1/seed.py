"""seed — 開発用ダミーデータ投入。

役职 7 種を網羅した教师 + 担任 1 人 + 学生 2 人 (一般 + 留学生)。

実行:
    cd 03_dev/backend/v1
    python -m seed
"""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select

from app import models, security
from app.database import SessionLocal, create_all

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed")

# ---- ダミーパスワード (全員共通、dev only) ----
DEV_PASSWORD = "tomoshibi-dev-2026"

# ---- 学生 ----
STUDENTS = [
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
        is_overseas=True,    # 留学生 (#11) — 5 役职 chain
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
        is_overseas=False,   # 一般 — 3 役职 chain
        email="tanaka.taro@example.jp",
    ),
]

# ---- 教师 (役职 7 種網羅 + 担任候補) ----
TEACHERS = [
    dict(
        login_id="ryomu_buchou",
        name="寮務 太郎 (寮務部長)",
        email="ryomu.buchou@example.jp",
        role="寮務部長",
        assigned_dorm=None,  # 跨寮
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
    # 担任候補 (寮務一般教师 で登録、class_teacher_assignment で担任に紐付け)
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


def main() -> None:
    create_all()
    db = SessionLocal()
    try:
        pw_hash = security.hash_password(DEV_PASSWORD)

        # 学生
        for s_data in STUDENTS:
            existing = db.scalars(
                select(models.Student).where(
                    models.Student.grade_code == s_data["grade_code"],
                    models.Student.class_code == s_data["class_code"],
                    models.Student.seat_no == s_data["seat_no"],
                )
            ).first()
            if existing:
                log.info("skip student: %s%s%s exists",
                         s_data["grade_code"], s_data["class_code"], s_data["seat_no"])
                continue
            student = models.Student(**s_data)
            db.add(student)
            db.flush()
            db.add(models.Account(student_id=student.id, password_hash=pw_hash))
            log.info("added student: %s (no=%s)", student.name, student.student_no)

        # 教师
        for t_data in TEACHERS:
            existing = db.scalars(
                select(models.Teacher).where(models.Teacher.login_id == t_data["login_id"])
            ).first()
            if existing:
                log.info("skip teacher: %s exists", t_data["login_id"])
                continue
            teacher = models.Teacher(
                **t_data,
                password_hash=pw_hash,
            )
            db.add(teacher)
            log.info("added teacher: %s (role=%s)", teacher.login_id, teacher.role)

        db.commit()

        # 担任 紐付け (current academic_year = 2026)
        # 高3 = grade_code '06', A = class_code '01', B = '02'
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
            log.info("added homeroom: %s → %s%s", login_id, grade, klass)
        db.commit()

        log.info("=" * 60)
        log.info("seed 完了")
        log.info("学生 login: 学号 060218 (留学生 リュウ) / 060103 (一般 田中)")
        log.info("教师 login: ryomu_buchou / ryomu_kachou / kokukou_buchou / ...")
        log.info("password (全員共通): %s", DEV_PASSWORD)
        log.info("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
