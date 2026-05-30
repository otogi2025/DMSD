"""学生个人档案聚合 + 一括进级 端点测试 (spec §7.10 / §4.2)。

覆盖：
- GET /api/v1/students/{id}/profile
  - 寮務系老师：200 含全块（含指导履历）
  - 学生本人：200 指导履历返空（C 案）
  - 非寮務老师：403
  - 他の学生 token：403
  - 不存在学生：404

- POST /api/v1/students/bulk-promote
  - dry_run=True：预览正确分组（promote / graduate）
  - dry_run=False：真改 grade_code / status
  - 高 3 进级变 graduated
  - target_grade_codes 过滤
  - 非 ADMIN_ROLES：403
"""

from __future__ import annotations

import pytest

from app import models, security


# -----------------------------------------------------------------------
# fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def profile_seed(db_session):
    """寮務系老师 + 国際交流部長（非寮務）+ 学生（含指导记录 / 扣分 / 出寮届）。"""
    pw = security.hash_password("test-password-12345")

    # 学生（高 2）
    student = models.Student(
        grade_code="05",
        class_code="01",
        seat_no="01",
        name="テスト学生",
        gender="male",
        room_no="M101",
        dorm_unit=1,
        is_overseas=False,
    )
    db_session.add(student)
    db_session.flush()
    db_session.add(models.Account(student_id=student.id, password_hash=pw))

    # 另一个学生（403 测试用）
    other = models.Student(
        grade_code="04",
        class_code="01",
        seat_no="02",
        name="他の学生",
        gender="male",
        room_no="M102",
        dorm_unit=1,
        is_overseas=False,
    )
    db_session.add(other)
    db_session.flush()
    db_session.add(models.Account(student_id=other.id, password_hash=pw))

    # 寮務課長（寮務系 → 全块可见）
    ryomu = models.Teacher(
        login_id="ryomu_test",
        name="寮務先生",
        email="ryomu@test.jp",
        password_hash=pw,
        role="寮務課長",
    )
    db_session.add(ryomu)

    # 国際交流部長（非寮務 → 403）
    kokukou = models.Teacher(
        login_id="kokukou_test",
        name="国際先生",
        email="kokukou@test.jp",
        password_hash=pw,
        role="国際交流部長",
    )
    db_session.add(kokukou)
    db_session.flush()

    # 指导记录（confidential）
    from datetime import date

    gr = models.GuidanceRecord(
        student_id=student.id,
        teacher_id=ryomu.id,
        content="面談した",
        category="生活态度",
        guidance_date=date(2026, 5, 1),
        confidential=True,
    )
    db_session.add(gr)

    # 扣分记录
    de = models.DemeritEvent(
        student_id=student.id,
        source_type="manual",
        points=2.0,
        reason="テスト扣分",
        month="2026-05",
    )
    db_session.add(de)

    db_session.commit()
    return {
        "student": student,
        "other": other,
        "ryomu": ryomu,
        "kokukou": kokukou,
    }


def _tok(client, login_id: str, password: str = "test-password-12345") -> str:
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _student_tok(client, student_no: str, password: str = "test-password-12345") -> str:
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": student_no, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


# -----------------------------------------------------------------------
# 個人档案聚合 tests
# -----------------------------------------------------------------------
class TestStudentProfile:
    def test_ryomu_sees_all_blocks(self, client, profile_seed):
        """寮務系老师能看到全部块，含指导履历。"""
        tok = _tok(client, "ryomu_test")
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        # 基本信息
        assert data["student"]["student_no"] == "050101"
        assert data["student"]["grade_code"] == "05"
        # 指导履历有 1 条
        assert len(data["guidance_records"]) == 1
        assert data["guidance_records"][0]["content"] == "面談した"
        # 扣分有 1 条
        assert len(data["demerit_events"]) == 1
        assert data["demerit_events"][0]["points"] == 2.0

    def test_student_sees_own_no_guidance(self, client, profile_seed):
        """学生本人看自己：200 OK，但指导履历返空（C 案）。"""
        tok = _student_tok(client, "050101")
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["student"]["student_no"] == "050101"
        # 指导履历返空（学生侧 C 案）
        assert data["guidance_records"] == []
        # 扣分仍可见
        assert len(data["demerit_events"]) == 1

    def test_kokukou_forbidden(self, client, profile_seed):
        """非寮務老师（国際交流部長）→ 403。"""
        tok = _tok(client, "kokukou_test")
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 403

    def test_student_cannot_see_others(self, client, profile_seed):
        """学生 A のトークンで学生 B のプロフィールを見ようとする → 403。"""
        tok = _student_tok(client, "050101")
        other_sid = str(profile_seed["other"].id)
        res = client.get(
            f"/api/v1/students/{other_sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 403

    def test_not_found(self, client, profile_seed):
        """存在しない student_id → 404。"""
        import uuid

        tok = _tok(client, "ryomu_test")
        res = client.get(
            f"/api/v1/students/{uuid.uuid4()}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 404

    def test_no_auth(self, client, profile_seed):
        """未ログイン → 401。"""
        sid = str(profile_seed["student"].id)
        res = client.get(f"/api/v1/students/{sid}/profile")
        assert res.status_code == 401

    def test_cross_dorm_forbidden(self, client, db_session, profile_seed):
        """#2 寮边界：女寮老师（assigned_dorm=4）查男寮学生（dorm_unit=1）→ 403。"""
        pw = security.hash_password("test-password-12345")
        # 女寮担当寮監（assigned_dorm=4）
        joshi_kanri = models.Teacher(
            login_id="joshi_kanri_test",
            name="女寮先生",
            email="joshi@test.jp",
            password_hash=pw,
            role="寮監",
            assigned_dorm=4,  # 女寮 = 4
        )
        db_session.add(joshi_kanri)
        db_session.commit()

        tok = _tok(client, "joshi_kanri_test")
        # profile_seed 的学生 dorm_unit=1（男寮），跨寮应该 403
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 403
        assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"


# -----------------------------------------------------------------------
# 一括進級 tests
# -----------------------------------------------------------------------
@pytest.fixture
def promote_seed(db_session):
    """6 学年分 + 管理者 + 権限なし教师を作成。"""
    pw = security.hash_password("test-password-12345")

    # 各学年 1 人（中1〜高3）
    # 注意：seat_no 各自不同（str(g).zfill(2)），
    # 确保进级后 grade_code +1 时不与下一学年的人撞 uq_students_no
    students: list[models.Student] = []
    for g in range(1, 7):
        gc = str(g).zfill(2)
        sn = str(g).zfill(2)  # seat_no 01~06，每人不同
        s = models.Student(
            grade_code=gc,
            class_code="01",
            seat_no=sn,
            name=f"{g}年生",
            gender="male",
            room_no=f"M{g}01",
            dorm_unit=1,
            is_overseas=False,
        )
        db_session.add(s)
        students.append(s)

    # is_demo 学生（進級対象外）
    demo = models.Student(
        grade_code="03",
        class_code="01",
        seat_no="99",
        name="デモ学生",
        gender="male",
        room_no="M399",
        dorm_unit=1,
        is_demo=True,
    )
    db_session.add(demo)

    # 寮務部長（ADMIN_ROLES → 有权限）
    admin = models.Teacher(
        login_id="buchou_promote",
        name="部長先生",
        email="buchou@promote.jp",
        password_hash=pw,
        role="寮務部長",
    )
    db_session.add(admin)

    # 学習担当（无权限）
    no_perm = models.Teacher(
        login_id="gakushu_promote",
        name="学習先生",
        email="gakushu@promote.jp",
        password_hash=pw,
        role="学習担当",
    )
    db_session.add(no_perm)
    db_session.flush()
    db_session.commit()

    return {"students": students, "demo": demo, "admin": admin, "no_perm": no_perm}


class TestBulkPromote:
    def test_dry_run_preview(self, client, promote_seed):
        """dry_run=True → 进级 5 人 + 毕业 1 人，DB 不变。"""
        tok = _tok(client, "buchou_promote")
        res = client.post(
            "/api/v1/students/bulk-promote",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["dry_run"] is True
        assert data["promote_count"] == 5  # 中1〜高2
        assert data["graduate_count"] == 1  # 高3
        assert data["total_affected"] == 6
        # demo 学生不在进级范围内
        assert all(e["student_no"] != "030199" for e in data["entries"])

    def test_dry_run_no_db_change(self, client, promote_seed, db_session):
        """dry_run=True → grade_code 没有真正改变。"""
        tok = _tok(client, "buchou_promote")
        client.post(
            "/api/v1/students/bulk-promote",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        from sqlalchemy import select

        students = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(False))
        ).all()
        # grade_code 仍然是 01〜06，没有变化
        codes = sorted([s.grade_code for s in students])
        assert codes == ["01", "02", "03", "04", "05", "06"]

    def test_real_promote(self, client, promote_seed, db_session):
        """dry_run=False → grade_code 真实变更。"""
        tok = _tok(client, "buchou_promote")
        res = client.post(
            "/api/v1/students/bulk-promote",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": False},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["dry_run"] is False
        assert data["promote_count"] == 5
        assert data["graduate_count"] == 1

        # 确认 DB 变更
        from sqlalchemy import select

        db_session.expire_all()
        students = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(False))
        ).all()
        by_name = {s.name: s for s in students}

        # 中1(原 grade 01) → 02
        assert by_name["1年生"].grade_code == "02"
        # 高2(原 grade 05) → 06
        assert by_name["5年生"].grade_code == "06"
        # 高3(原 grade 06) → graduated，grade_code 不变
        assert by_name["6年生"].status == "graduated"
        assert by_name["6年生"].grade_code == "06"

    def test_target_grade_codes_filter(self, client, promote_seed, db_session):
        """target_grade_codes 指定 → 只进级指定年级。"""
        tok = _tok(client, "buchou_promote")
        res = client.post(
            "/api/v1/students/bulk-promote",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": False, "target_grade_codes": ["04", "05"]},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        # 高1→高2 + 高2→高3 共 2 人
        assert data["total_affected"] == 2
        assert data["promote_count"] == 2
        assert data["graduate_count"] == 0

        # 中1〜中3 不在范围内，grade_code 没变
        from sqlalchemy import select

        db_session.expire_all()
        students = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(False))
        ).all()
        by_name = {s.name: s for s in students}
        assert by_name["1年生"].grade_code == "01"  # 未变化
        assert by_name["4年生"].grade_code == "05"  # 04→05
        assert by_name["5年生"].grade_code == "06"  # 05→06

    def test_forbidden_role(self, client, promote_seed):
        """无权限老师（学習担当）→ 403。"""
        tok = _tok(client, "gakushu_promote")
        res = client.post(
            "/api/v1/students/bulk-promote",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        assert res.status_code == 403
