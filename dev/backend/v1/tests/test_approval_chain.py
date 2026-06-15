"""审批链服务单元测试 — B-中-18（2026-06-15 全维度审查）。

app/services/approval_chain.py 的 resolve_homeroom_teacher / collect_recipients 此前无单测。
本文件覆盖两条核心逻辑：
  - resolve_homeroom_teacher 的学年边界（4 月切学年：on_date.month>=4 算当年度、<4 算前年度）
  - 演示隔离（真实学生只解析到真老师、演示学生只解析到演示老师；collect_recipients 同理）

直接测 service 层（用 db_session 夹具造数据），不经 HTTP。

跑：
    cd dev/backend/v1
    .venv/bin/python -m pytest tests/test_approval_chain.py -q
"""

from __future__ import annotations

from datetime import date, time

from app import models
from app import security
from app.services import approval_chain


def _mk_teacher(db, login_id, name, role, *, is_demo=False, dorm=None):
    t = models.Teacher(
        login_id=login_id,
        name=name,
        email=f"{login_id}@test.jp",
        password_hash=security.hash_password("test-password-12345"),
        role=role,
        assigned_dorm=dorm,
        is_demo=is_demo,
    )
    db.add(t)
    db.flush()
    return t


def _mk_student(db, grade, klass, seat, *, is_demo=False, overseas=False, dorm=1):
    prefix = "M" if dorm in (1, 2) else "W"
    s = models.Student(
        grade_code=grade,
        class_code=klass,
        seat_no=seat,
        name="テスト学生",
        gender="male",
        room_no=f"{prefix}{grade}{seat}",
        dorm_unit=dorm,
        is_overseas=overseas,
        is_demo=is_demo,
        email="s@test.jp",
    )
    db.add(s)
    db.flush()
    return s


def _mk_homeroom(db, teacher, grade, klass, year):
    db.add(
        models.ClassTeacherAssignment(
            teacher_id=teacher.id,
            grade_code=grade,
            class_code=klass,
            academic_year=year,
            is_homeroom=True,
            effective_from=date(year, 4, 1),
        )
    )
    db.flush()


class TestResolveHomeroomTeacher:
    def test_resolves_within_same_academic_year(self, db_session):
        """4 月以后的日期 → 算当年度 → 命中当年度担任绑定。"""
        student = _mk_student(db_session, "06", "02", "18")
        tannin = _mk_teacher(db_session, "tn2026", "担任太郎", "寮務一般教師", dorm=1)
        _mk_homeroom(db_session, tannin, "06", "02", 2026)
        db_session.commit()

        got = approval_chain.resolve_homeroom_teacher(
            db_session, student, on_date=date(2026, 5, 10)
        )
        assert got is not None
        assert got.id == tannin.id

    def test_academic_year_boundary_before_april(self, db_session):
        """3 月（< 4 月）的日期 → 算「前一年度」(2025)，命中 2025 年度绑定、不命中 2026 年度。"""
        student = _mk_student(db_session, "06", "02", "18")
        # 同班两个年度各一个担任
        tannin_2025 = _mk_teacher(
            db_session, "tn2025", "旧担任", "寮務一般教師", dorm=1
        )
        tannin_2026 = _mk_teacher(
            db_session, "tn2026b", "新担任", "寮務一般教師", dorm=1
        )
        _mk_homeroom(db_session, tannin_2025, "06", "02", 2025)
        _mk_homeroom(db_session, tannin_2026, "06", "02", 2026)
        db_session.commit()

        # 2026-03-15 < 4 月 → academic_year = 2025 → 应解析到 2025 年度担任
        got = approval_chain.resolve_homeroom_teacher(
            db_session, student, on_date=date(2026, 3, 15)
        )
        assert got is not None
        assert got.id == tannin_2025.id, "3 月应落到前年度（2025）担任"

    def test_no_assignment_returns_none(self, db_session):
        """没有任何担任绑定 → None（不抛错）。"""
        student = _mk_student(db_session, "07", "03", "05")
        db_session.commit()
        got = approval_chain.resolve_homeroom_teacher(
            db_session, student, on_date=date(2026, 5, 1)
        )
        assert got is None

    def test_demo_isolation_real_student_skips_demo_teacher(self, db_session):
        """演示隔离：真实学生的担任只解析到真老师，不会解析到演示老师。"""
        real_student = _mk_student(db_session, "06", "02", "18", is_demo=False)
        demo_tannin = _mk_teacher(
            db_session, "demo_tn", "演示担任", "寮務一般教師", is_demo=True, dorm=1
        )
        # 只有演示老师绑了这个班 —— 真实学生应解析不到（demo != real）
        _mk_homeroom(db_session, demo_tannin, "06", "02", 2026)
        db_session.commit()

        got = approval_chain.resolve_homeroom_teacher(
            db_session, real_student, on_date=date(2026, 5, 1)
        )
        assert got is None, "真实学生不应解析到演示老师担任"

    def test_demo_isolation_demo_student_resolves_demo_teacher(self, db_session):
        """演示隔离反向：演示学生能解析到演示老师担任。"""
        demo_student = _mk_student(db_session, "06", "02", "18", is_demo=True)
        demo_tannin = _mk_teacher(
            db_session, "demo_tn2", "演示担任", "寮務一般教師", is_demo=True, dorm=1
        )
        _mk_homeroom(db_session, demo_tannin, "06", "02", 2026)
        db_session.commit()

        got = approval_chain.resolve_homeroom_teacher(
            db_session, demo_student, on_date=date(2026, 5, 1)
        )
        assert got is not None
        assert got.id == demo_tannin.id


class TestCollectRecipients:
    def test_real_student_recipients_exclude_demo_teachers(self, db_session):
        """collect_recipients：真实学生（留学生 → 触发 5 役职 chain）的收件人里不含演示老师。"""
        student = _mk_student(db_session, "06", "02", "18", overseas=True)
        tannin = _mk_teacher(db_session, "tn_r", "担任", "寮務一般教師", dorm=1)
        _mk_homeroom(db_session, tannin, "06", "02", 2026)
        # 真老师 + 同 role 的演示老师各一名
        _mk_teacher(db_session, "rb_real", "寮務部長真", "寮務部長")
        _mk_teacher(db_session, "rb_demo", "寮務部長演示", "寮務部長", is_demo=True)
        db_session.commit()

        # 造一条申请，再解出它的收件人
        application = models.Application(
            student_id=student.id,
            kind="帰国",
            leave_date=date(2026, 8, 1),
            leave_method="飛行機",
            leave_time=time(10, 0),
            return_date=date(2026, 8, 20),
            return_method="飛行機",
            return_time=time(18, 0),
        )
        db_session.add(application)
        db_session.flush()

        teachers, emails = approval_chain.collect_recipients(db_session, application)
        # 不应含任何演示老师
        assert all(not t.is_demo for t in teachers), "真实学生收件人不应含演示老师"
        assert "rb_demo@test.jp" not in emails
        assert "rb_real@test.jp" in emails
