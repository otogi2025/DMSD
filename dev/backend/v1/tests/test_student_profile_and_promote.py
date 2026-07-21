"""学生个人档案聚合 + 一括进级 端点测试 (spec §7.10 / §4.2)。

覆盖：
- GET /api/v1/students/{id}/profile
  - 寮務系老师：200 含全块（含指导履历）
  - 学生本人：200 指导履历返空（C 案）
  - 申請承認専用组对 C_GUIDANCE 有 VIEW→可看 profile
  - 他の学生 token：403
  - 不存在学生：404

- POST /api/v1/students/renewal-start（开闸 — 2026-06-05 学生自设方案）
  - dry_run=True：预览（notify 中1~高2 / graduate 高3）
  - dry_run=False：中1~高2 打 needs_renewal、高3 毕业、grade_code 不变
  - 非 ADMIN_ROLES：403
- POST /api/v1/students/me/renew-number（学生自设番号：成功 / 撞号 422 / 身份从令牌取 / 401）
- GET /api/v1/students/renewal-progress（老师看谁没改：5 人 / 越权 403）
- POST /api/v1/accounts/{id}/renew-seat（老师单件改番号：成功 / 撞号 422 / 越权 403）
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

    # 国際交流部長（默认组「申請承認専用」→ 对 C_GUIDANCE 有 VIEW，可看 profile）
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
    return res.json()["data"]["access_token"]


def _student_tok(client, student_no: str, password: str = "test-password-12345") -> str:
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": student_no, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


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
        data = res.json()["data"]
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
        data = res.json()["data"]
        assert data["student"]["student_no"] == "050101"
        # 指导履历返空（学生侧 C 案）
        assert data["guidance_records"] == []
        # 扣分仍可见
        assert len(data["demerit_events"]) == 1

    def test_kokukou_now_allowed(self, client, profile_seed):
        """权限组体系迁移后：国際交流部長（默认组「申請承認専用」）对 C_GUIDANCE 有 VIEW
        → 可看 profile，与 guidance.py 的 require_permission(C_GUIDANCE) 一致。
        旧行为「非寮務职位 → 403」（_GUIDANCE_ROLES 职位集判定）已随权限分级改造废弃。"""
        tok = _tok(client, "kokukou_test")
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200

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

    def test_cross_dorm_now_allowed(self, client, db_session, profile_seed):
        """#2 寮过滤已取消 2026-06-13：女寮老师（assigned_dorm=4）查男寮学生（dorm_unit=1）→ 现在允许。"""
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
        # profile_seed 的学生 dorm_unit=1（男寮），跨寮现已放开
        sid = str(profile_seed["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text

    def test_rollcall_entries_carry_session_type(
        self, client, db_session, profile_seed
    ):
        """杭田 2026-06-04 五-5: 点呼履历每条带 session_type（morning/evening），能分朝/夜。"""
        from datetime import datetime, timezone

        student = profile_seed["student"]
        now = datetime(2026, 5, 10, 7, 0, tzinfo=timezone.utc)
        sess = models.RollCallSession(
            dorm_unit_set=[1, 2],
            session_type="morning",
            day_type="weekday",
            scheduled_window_start_at=now,
            scheduled_on_time_end_at=now,
            scheduled_late_end_at=now,
            scheduled_auto_end_at=now,
        )
        db_session.add(sess)
        db_session.flush()
        ev = models.RollCallEvent(
            session_id=sess.id,
            student_id=student.id,
            base_status="present",
            status_source="auto_nfc",
            checked_in_at=now,
        )
        db_session.add(ev)
        db_session.commit()

        tok = _tok(client, "ryomu_test")
        res = client.get(
            f"/api/v1/students/{student.id}/profile",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        rc = res.json()["data"]["rollcall_events"]
        assert len(rc) == 1, rc
        assert rc[0]["session_type"] == "morning", rc[0]


# -----------------------------------------------------------------------
# 学年更新 / 学生自设番号 tests（spec §4.2 — 2026-06-05 学生自设方案）
# -----------------------------------------------------------------------
@pytest.fixture
def promote_seed(db_session):
    """6 学年各 1 人 + is_demo 1 人 + 管理者 + 権限なし教师を作成。"""
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

    # 低权限老师夹具 — 显式配「申請承認専用」组（对学生账号管理只有 V、无 M），
    # 用作"无管理权"测试。显式配组、不依赖职位回退（2026-06-12 F5 已把学習担当回退组
    # 改成一般宿管+晚自习，故不能再靠 role 回退当低权限夹具）。
    no_perm = models.Teacher(
        login_id="gakushu_promote",
        name="学習先生",
        email="gakushu@promote.jp",
        password_hash=pw,
        role="学習担当",
        permission_group="申請承認専用",
    )
    db_session.add(no_perm)
    db_session.flush()
    db_session.commit()

    return {"students": students, "demo": demo, "admin": admin, "no_perm": no_perm}


class TestRenewalStart:
    """POST /students/renewal-start — 老师开闸（中1~高2 打标记 + 高3 毕业）。"""

    def test_dry_run_preview(self, client, promote_seed):
        """dry_run=True → 通知 5 人（中1~高2）+ 毕业 1 人（高3），demo 排除，DB 不变。"""
        tok = _tok(client, "buchou_promote")
        res = client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["dry_run"] is True
        assert data["notify_count"] == 5  # 中1〜高2
        assert data["graduate_count"] == 1  # 高3
        assert data["total_affected"] == 6
        # demo 学生不在范围内
        assert all(e["student_no"] != "030199" for e in data["entries"])

    def test_dry_run_no_db_change(self, client, promote_seed, db_session):
        """dry_run=True → needs_renewal / status 都没变。"""
        tok = _tok(client, "buchou_promote")
        client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        from sqlalchemy import select

        db_session.expire_all()
        students = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(False))
        ).all()
        assert all(not s.needs_renewal for s in students)
        assert all(s.status == "active" for s in students)

    def test_real_start(self, client, promote_seed, db_session):
        """dry_run=False → 中1~高2 打 needs_renewal=True，高3 毕业，grade_code 全不变。"""
        tok = _tok(client, "buchou_promote")
        res = client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": False},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["dry_run"] is False
        assert data["notify_count"] == 5
        assert data["graduate_count"] == 1

        from sqlalchemy import select

        db_session.expire_all()
        students = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(False))
        ).all()
        by_name = {s.name: s for s in students}

        # 中1~高2 → needs_renewal=True，grade_code 没动
        assert by_name["1年生"].needs_renewal
        assert by_name["1年生"].grade_code == "01"
        assert by_name["5年生"].needs_renewal
        assert by_name["5年生"].grade_code == "05"
        # 高3 → graduated，不打标记
        assert by_name["6年生"].status == "graduated"
        assert not by_name["6年生"].needs_renewal
        assert by_name["6年生"].grade_code == "06"

    def test_demo_excluded(self, client, promote_seed, db_session):
        """is_demo 学生不参与开闸（不打标记 / 不毕业）。"""
        tok = _tok(client, "buchou_promote")
        client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": False},
        )
        from sqlalchemy import select

        db_session.expire_all()
        demo = db_session.scalars(
            select(models.Student).where(models.Student.is_demo.is_(True))
        ).first()
        assert not demo.needs_renewal
        assert demo.status == "active"

    def test_forbidden_role(self, client, promote_seed):
        """无权限老师（学習担当）→ 403。"""
        tok = _tok(client, "gakushu_promote")
        res = client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": True},
        )
        assert res.status_code == 403


class TestStudentRenewNumber:
    """POST /students/me/renew-number — 学生自设番号（身份从令牌取）。"""

    def test_self_renew_success(self, client, seed_data, db_session):
        """学生改自己番号成功 → 新 student_no + needs_renewal 清零。"""
        student = seed_data["student"]
        student.needs_renewal = True  # 模拟开闸后状态
        db_session.commit()
        sid = student.id

        tok = _student_tok(client, "060218")
        res = client.post(
            "/api/v1/students/me/renew-number",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "06", "class_code": "01", "seat_no": "30"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["student_no"] == "060130"
        assert data["needs_renewal"] is False

        db_session.expire_all()
        s = db_session.get(models.Student, sid)
        assert s.seat_no == "30"
        assert s.class_code == "01"
        assert not s.needs_renewal

    def test_self_renew_collision(self, client, seed_data, db_session):
        """目标番号被别人占 → 422 STUDENT_NO_TAKEN。"""
        occupier = models.Student(
            grade_code="06",
            class_code="01",
            seat_no="30",
            name="占位学生",
            gender="male",
            room_no="M130",
            dorm_unit=1,
        )
        db_session.add(occupier)
        seed_data["student"].needs_renewal = True  # 模拟开闸后状态
        db_session.commit()

        tok = _student_tok(client, "060218")
        res = client.post(
            "/api/v1/students/me/renew-number",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "06", "class_code": "01", "seat_no": "30"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "STUDENT_NO_TAKEN"

    def test_self_renew_ignores_body_student_id(self, client, seed_data, db_session):
        """身份从令牌取 — 请求体即使塞 student_id 也被忽略，只改本人。"""
        other = models.Student(
            grade_code="04",
            class_code="02",
            seat_no="05",
            name="他人",
            gender="male",
            room_no="M405",
            dorm_unit=1,
        )
        db_session.add(other)
        seed_data["student"].needs_renewal = True  # 模拟开闸后状态
        db_session.commit()
        other_id = other.id

        tok = _student_tok(client, "060218")
        res = client.post(
            "/api/v1/students/me/renew-number",
            headers={"Authorization": f"Bearer {tok}"},
            json={
                "grade_code": "06",
                "class_code": "01",
                "seat_no": "40",
                "student_id": str(other_id),  # 恶意：试图改别人
            },
        )
        assert res.status_code == 200, res.text
        # 本人（060218）被改成 060140
        assert res.json()["data"]["student_no"] == "060140"
        # 他人完全没动
        db_session.expire_all()
        o = db_session.get(models.Student, other_id)
        assert o.grade_code == "04"
        assert o.class_code == "02"
        assert o.seat_no == "05"

    def test_self_renew_requires_auth(self, client, seed_data):
        """无令牌 → 401。"""
        res = client.post(
            "/api/v1/students/me/renew-number",
            json={"grade_code": "06", "class_code": "01", "seat_no": "30"},
        )
        assert res.status_code == 401

    def test_self_renew_not_open(self, client, seed_data):
        """未开闸（needs_renewal=False，默认）→ 409 RENEWAL_NOT_OPEN，防绕过开闸。"""
        tok = _student_tok(client, "060218")
        res = client.post(
            "/api/v1/students/me/renew-number",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "06", "class_code": "01", "seat_no": "30"},
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "RENEWAL_NOT_OPEN"

    def test_self_renew_db_conflict_writes_failure_audit(
        self, client, seed_data, db_session, monkeypatch
    ):
        """A-491：并发抢同号（绕过应用层查重直接撞 DB 唯一约束）仍返 422，且补写失败审计。

        构造方法：占位学生已占走目标番号，但 monkeypatch 路由里的 select 让应用层查重
        漏看它（模拟 TOCTOU 窗口 / 并发抢号），逼真正走到 db.commit() 触发 uq_students_no
        IntegrityError → rollback → A-491 失败审计补写路径。
        """
        from app.routers import student_profile

        # 占位学生先占走目标番号 060130
        occupier = models.Student(
            grade_code="06",
            class_code="01",
            seat_no="30",
            name="占位学生",
            gender="male",
            room_no="M130",
            dorm_unit=1,
        )
        db_session.add(occupier)
        seed_data["student"].needs_renewal = True  # 模拟开闸后状态
        db_session.commit()

        # 让路由的应用层查重「看不到」占位学生 —— 在 where 子句尾部再追加一个永远为假的条件，
        # 使第 1 步 existing 查询返回 None，请求得以走到 db.commit() 真撞唯一约束。
        _orig_select = student_profile.select

        def _blind_select(*args, **kwargs):
            stmt = _orig_select(*args, **kwargs)
            if args and args[0] is models.Student:
                return stmt.where(models.Student.id != models.Student.id)
            return stmt

        monkeypatch.setattr(student_profile, "select", _blind_select)

        tok = _student_tok(client, "060218")
        res = client.post(
            "/api/v1/students/me/renew-number",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "06", "class_code": "01", "seat_no": "30"},
        )
        # 业务行为不变：撞号仍正确返 422
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "STUDENT_NO_TAKEN"

        # A-491 核心：失败尝试留下审计痕迹（action=student.renew_number_conflict）
        db_session.expire_all()
        audits = (
            db_session.query(models.AuditLog)
            .filter(models.AuditLog.action == "student.renew_number_conflict")
            .all()
        )
        assert len(audits) == 1
        assert audits[0].payload == {"attempted_student_no": "060130"}
        assert audits[0].actor_type == "student"

        # 同时确认「成功」审计被回滚掉、本人番号没被改（事务正确回滚）
        success_audits = (
            db_session.query(models.AuditLog)
            .filter(models.AuditLog.action == "student.renew_number")
            .all()
        )
        assert len(success_audits) == 0
        me = db_session.get(models.Student, seed_data["student"].id)
        assert me.student_no == "060218"
        assert me.needs_renewal is True


class TestRenewalProgress:
    """GET /students/renewal-progress — 老师看谁还没改番号。"""

    def test_progress_after_start(self, client, promote_seed):
        tok = _tok(client, "buchou_promote")
        client.post(
            "/api/v1/students/renewal-start",
            headers={"Authorization": f"Bearer {tok}"},
            json={"dry_run": False},
        )
        res = client.get(
            "/api/v1/students/renewal-progress",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        # 中1~高2 共 5 人待更新（高3 毕业 / demo 排除）
        assert data["pending_count"] == 5
        assert len(data["items"]) == 5
        nos = {i["student_no"] for i in data["items"]}
        assert "060106" not in nos  # 高3 不在
        assert "030199" not in nos  # demo 不在

    def test_progress_empty_before_start(self, client, promote_seed):
        tok = _tok(client, "buchou_promote")
        res = client.get(
            "/api/v1/students/renewal-progress",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["pending_count"] == 0

    def test_progress_approval_group_can_view(self, client, promote_seed):
        """低权限老师（申請承認専用 组）→ 可查看学年更新进度（200）。

        权限分级改造（teacher_permission_v1.md §5 第 12 行「学生账号管理」5 组全部至少 V）后，
        旧「非账号管理角色 → 403」废弃。申請承認専用 组对学生账号管理有 V（查看）。
        管理动作（单件改番号 renew-seat）仍需 M（申請承認専用 = V<M），TestTeacherRenewSeat 保持 403。
        """
        tok = _tok(client, "gakushu_promote")
        res = client.get(
            "/api/v1/students/renewal-progress",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200


class TestTeacherRenewSeat:
    """POST /accounts/{id}/renew-seat — 老师单件改某学生番号（兜底）。"""

    def _s1_id(self, db_session):
        from sqlalchemy import select

        s1 = db_session.scalars(
            select(models.Student).where(models.Student.name == "1年生")
        ).first()
        return s1

    def test_teacher_renew_success(self, client, promote_seed, db_session):
        s1 = self._s1_id(db_session)
        s1.needs_renewal = True
        db_session.commit()
        sid = s1.id

        tok = _tok(client, "buchou_promote")
        res = client.post(
            f"/api/v1/accounts/{sid}/renew-seat",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "01", "class_code": "01", "seat_no": "50"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["student_no"] == "010150"

        db_session.expire_all()
        s = db_session.get(models.Student, sid)
        assert s.seat_no == "50"
        assert not s.needs_renewal

    def test_teacher_renew_collision(self, client, promote_seed, db_session):
        """改成 2年生 的号（020102）→ 撞号 422。"""
        sid = self._s1_id(db_session).id
        tok = _tok(client, "buchou_promote")
        res = client.post(
            f"/api/v1/accounts/{sid}/renew-seat",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "02", "class_code": "01", "seat_no": "02"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "STUDENT_NO_TAKEN"

    def test_teacher_renew_forbidden(self, client, promote_seed, db_session):
        sid = self._s1_id(db_session).id
        tok = _tok(client, "gakushu_promote")
        res = client.post(
            f"/api/v1/accounts/{sid}/renew-seat",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "01", "class_code": "01", "seat_no": "50"},
        )
        assert res.status_code == 403


class TestRenewalDormBoundary:
    """R4 寮边界 — 分寮管理係只能操作本人管辖寮（codex 6-05 审出补）。"""

    def _setup(self, db_session):
        pw = security.hash_password("test-password-12345")
        # 分寮管理係（assigned_dorm=1 → dorm_units_for_teacher 限 [1,2]，非跨寮角色）
        kanri1 = models.Teacher(
            login_id="kanri_dorm1",
            name="管理一郎",
            email="k1@test.jp",
            password_hash=pw,
            role="管理係",
            assigned_dorm=1,
        )
        db_session.add(kanri1)
        # dorm 4（女寮）学生
        girl = models.Student(
            grade_code="05",
            class_code="01",
            seat_no="01",
            name="女寮生",
            gender="female",
            room_no="W101",
            dorm_unit=4,
        )
        db_session.add(girl)
        db_session.commit()
        return girl.id

    def test_renew_seat_other_dorm_now_allowed(self, client, db_session):
        """dorm1 管理係 改 dorm4 学生番号 → 现在允许（寮过滤已取消 2026-06-13）。"""
        girl_id = self._setup(db_session)
        tok = _tok(client, "kanri_dorm1")
        res = client.post(
            f"/api/v1/accounts/{girl_id}/renew-seat",
            headers={"Authorization": f"Bearer {tok}"},
            json={"grade_code": "05", "class_code": "01", "seat_no": "50"},
        )
        assert res.status_code == 200, res.text

    def test_progress_now_includes_other_dorm(self, client, db_session):
        """dorm1 管理係 的进度名单现在也含 dorm4 学生（寮过滤已取消 2026-06-13）。"""
        girl_id = self._setup(db_session)
        girl = db_session.get(models.Student, girl_id)
        girl.needs_renewal = True
        db_session.commit()
        tok = _tok(client, "kanri_dorm1")
        res = client.get(
            "/api/v1/students/renewal-progress",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert res.status_code == 200, res.text
        nos = {i["student_no"] for i in res.json()["data"]["items"]}
        assert "050101" in nos  # 寮过滤取消后 dorm4 女寮生也进入 dorm1 管理係 视野


class TestStudentMe:
    """GET /students/me — 当前登录学生基本信息（IX-008，替换 iOS SEED.user 假数据）。"""

    def test_me_requires_auth(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/students/me")
        assert res.status_code == 401

    def test_me_returns_self(self, client, student_token, seed_data):
        """学生 token → 200，返回自己的基本信息（conftest seed 的留学生 リュウ 060218）。"""
        res = client.get(
            "/api/v1/students/me",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["student_no"] == "060218", data
        assert data["name"] == "リュウ イヒ"
        assert data["room_no"] == "M101"
        assert data["dorm_unit"] == 1
        assert data["is_overseas"] is True
        assert data["category"] == "一般寮生"  # Student model 默认值

    def test_me_rejects_teacher(self, client, teacher_token, seed_data):
        """老师 token → 403（/students/me 只认学生 token）。"""
        res = client.get(
            "/api/v1/students/me",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 403, res.text

    def test_me_not_shadowed_by_profile_route(self, client, student_token, seed_data):
        """关键：'me' 不被 /students/{id}/profile 当 UUID 解析（返回 basic、不是 422）。"""
        res = client.get(
            "/api/v1/students/me",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        # basic 响应（无 applications/study_checkins 等聚合块），区别于 /profile
        assert "applications" not in res.json()["data"]


class TestMyDisciplineSummary:
    """GET /discipline/me/summary — 当前学生当月扣分汇总（IX-008b，iOS 当前用户统计）。"""

    def test_requires_auth(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/discipline/me/summary")
        assert res.status_code == 401

    def test_rejects_teacher(self, client, teacher_token, seed_data):
        """老师 token → 403（只认学生 token）。"""
        res = client.get(
            "/api/v1/discipline/me/summary",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 403, res.text

    def test_current_month_only_and_counts(
        self, client, student_token, seed_data, db_session
    ):
        """只算当月 + 排除已撤销；late/absent 只数点呼遅刻/欠席。"""
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo

        from app import models

        student = seed_data["student"]
        this_month = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m")

        # 当月：2 遅刻(0.5) + 1 欠席(2.0) + 1 手动(1.0) = 4.0 点 / late 2 / absent 1
        for _ in range(2):
            db_session.add(
                models.DemeritEvent(
                    student_id=student.id,
                    source_type="rollcall_late",
                    points=0.5,
                    reason="遅刻",
                    month=this_month,
                )
            )
        db_session.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="rollcall_absent",
                points=2.0,
                reason="欠席",
                month=this_month,
            )
        )
        db_session.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="manual",
                points=1.0,
                reason="手动",
                month=this_month,
            )
        )
        # 过去月份的扣分不该算进当月汇总
        db_session.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="rollcall_late",
                points=0.5,
                reason="先月遅刻",
                month="2020-01",
            )
        )
        # 已撤销的不该算
        db_session.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="rollcall_absent",
                points=2.0,
                reason="撤回済",
                month=this_month,
                revoked_at=datetime.now(timezone.utc),
            )
        )
        db_session.commit()

        res = client.get(
            "/api/v1/discipline/me/summary",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["month"] == this_month, data
        assert data["total_points"] == 4.0, data
        assert data["late_count"] == 2, data
        assert data["absent_count"] == 1, data
