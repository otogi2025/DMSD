"""学習 (晚自习) endpoint tests — C-050 (2026-05-21) 新增。

覆盖：
- GET /study/today/attendees — 今日预定参加者
- POST /study/checkins — 学生 / 教师 签到
- POST /study/checkins/bulk-finalize — 教师 21:00 一括 finalize
- POST /study/absence-requests — 学生欠席届
- POST /study/absence-requests/:id/decision — 教师承认 / 拒绝
- GET /study/absence-requests — 教师一覧
- POST /study/cancel-today — 教师 cancel

跑：
    cd dev/backend/v1
    pytest tests/test_study.py -v
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app import models
from app.routers import study
from app.routers.study import _academic_term


@pytest.fixture
def study_roster(db_session, seed_data):
    """060218 学生加学習名簿（晩学習対象者）。"""
    today = date.today()
    roster = models.StudyRoster(
        student_id=seed_data["student"].id,
        academic_term=_academic_term(today),
    )
    db_session.add(roster)
    db_session.commit()
    return roster


@pytest.fixture
def low_role_teacher_token(client, seed_data):
    """管理係（不在名簿管理 gate 里）token — 用于断言 403 无权。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "kanri", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


class TestStudyToday:
    """GET /study/today/attendees"""

    def test_today_attendees_requires_teacher(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/study/today/attendees")
        assert res.status_code == 401

    def test_today_attendees_returns_list(self, client, teacher_token, study_roster):
        """带教师 token → 返回 today list（含 expected_attendees 字段）。"""
        res = client.get(
            "/api/v1/study/today/attendees",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert "expected_attendees" in data
        assert "summary" in data
        assert isinstance(data["expected_attendees"], list)


class TestAbsenceRequest:
    """POST /study/absence-requests + decision"""

    def test_create_absence_request(self, client, student_token):
        """学生创建欠席届。"""
        res = client.post(
            "/api/v1/study/absence-requests",
            json={
                "target_date": str(date.today() + timedelta(days=1)),
                "period": "full",
                "reason": "体調不良のため",
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["status"] == "pending"
        assert data["reason"] == "体調不良のため"

    def test_decide_absence_request_approve(self, client, student_token, teacher_token):
        """教师承认欠席届 → status → approved。"""
        # 学生提出
        res_create = client.post(
            "/api/v1/study/absence-requests",
            json={
                "target_date": str(date.today() + timedelta(days=1)),
                "period": "full",
                "reason": "体調不良のため",
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_create.status_code == 201
        req_id = res_create.json()["data"]["id"]

        # 教师承认
        res = client.post(
            f"/api/v1/study/absence-requests/{req_id}/decision",
            json={"decision": "approved", "comment": "了承"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "approved"

    def test_list_absence_requests_teacher(self, client, teacher_token):
        """教师拉欠席届一览 — 即使空也返回 200。"""
        res = client.get(
            "/api/v1/study/absence-requests",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)

    def test_list_includes_student_summary_and_status_filter(
        self, client, student_token, teacher_token
    ):
        """审查 S2 web#6 回归：一览每条带学生摘要（老师原来认不出「谁请哪天假」
        就能点承認/却下），status=pending 过滤生效。"""
        res_create = client.post(
            "/api/v1/study/absence-requests",
            json={
                "target_date": str(date.today() + timedelta(days=1)),
                "period": "full",
                "reason": "体調不良のため",
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_create.status_code == 201

        res = client.get(
            "/api/v1/study/absence-requests?status=pending",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data, "pending 过滤应含刚提交的欠席届"
        first = data[0]
        assert first["status"] == "pending"
        assert first["student_name"]  # 摘要三件套非空
        assert first["student_no"]
        assert first["room_no"]


class TestMyAbsenceSummary:
    """GET /study/absence-requests/me/summary — 当前学生当月请假次数（IX-034）。"""

    def test_requires_auth(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/study/absence-requests/me/summary")
        assert res.status_code == 401

    def test_rejects_teacher(self, client, teacher_token):
        """教师 token → 403（学生专用端点）。"""
        res = client.get(
            "/api/v1/study/absence-requests/me/summary",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 403

    def test_counts_current_month_only_all_statuses(
        self, client, db_session, seed_data, student_token, monkeypatch
    ):
        """只数当月（按 target_date）+ 全状态都算（含 rejected）+ 跨月排除。

        固定 _now_jst 到月中（2026-06-15 JST），避免依赖本机时区 / 运行日期 ——
        端点用 _now_jst() 算当月、测试若用 date.today() 在非 JST 机器月末边界会 flaky。
        """
        student = seed_data["student"]
        monkeypatch.setattr(
            study,
            "_now_jst",
            lambda: datetime(2026, 6, 15, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )
        # 当月（6 月）首尾各 1 条：1 条 pending 默认 + 1 条 rejected → 都该计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 6, 1),
                period="full",
                reason="当月1",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 6, 30),
                period="full",
                reason="当月2(被拒)",
                status="rejected",
            )
        )
        # 上个月最后一天 + 下个月第一天 → 边界外、都不应计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 5, 31),
                period="full",
                reason="上月末",
                status="approved",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 7, 1),
                period="full",
                reason="下月初",
            )
        )
        db_session.commit()

        res = client.get(
            "/api/v1/study/absence-requests/me/summary",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["count"] == 2
        assert data["month"] == "2026-06"

    def test_counts_handles_year_end_boundary(
        self, client, db_session, seed_data, student_token, monkeypatch
    ):
        """12 月跨年边界：当月 = 12 月、next 月须算成翌年 1/1，排除 11 月 / 翌 1 月。

        固定 _now_jst 到 2026-12-31 23:50 JST —— 触发端点 now.month == 12 →
        date(year+1, 1, 1) 那条跨年分支，且压在月末/年末最深的边界上。
        """
        student = seed_data["student"]
        monkeypatch.setattr(
            study,
            "_now_jst",
            lambda: datetime(2026, 12, 31, 23, 50, tzinfo=ZoneInfo("Asia/Tokyo")),
        )
        # 当月（12 月）首尾各 1 条 → 都计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 12, 1),
                period="full",
                reason="12月初",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 12, 31),
                period="full",
                reason="12月末(被拒)",
                status="rejected",
            )
        )
        # 上月（11 月末）+ 翌年（1 月初）→ 都不计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2026, 11, 30),
                period="full",
                reason="11月末",
                status="approved",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(2027, 1, 1),
                period="full",
                reason="翌1月初",
            )
        )
        db_session.commit()

        res = client.get(
            "/api/v1/study/absence-requests/me/summary",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["count"] == 2
        assert data["month"] == "2026-12"


class TestCheckin:
    """POST /study/checkins"""

    def test_student_self_checkin_forbidden(
        self, client, student_token, seed_data, study_roster
    ):
        """晚自习签到是 teacher-only（老师操作端）— 学生 token 自助调用 → 403 FORBIDDEN。

        migtest-06: 旧测试名「学生自己 checkin」却只断言 < 500；该端点 Depends(get_current_teacher)，
        学生本就得 403，弱断言把这层边界整个盖住。这里锁死「学生不能自助签到」的真实行为。
        若将来要支持学生自助晚自习签到，是另开端点 / 放宽鉴权的设计变更（目前老师操作，需 itsuki 决策）。
        """
        res = client.post(
            "/api/v1/study/checkins",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN", res.text

    def test_teacher_checkin_records(
        self, client, teacher_token, seed_data, study_roster
    ):
        """老师给学生记晚自习签到 → 201，返回记录含该学生 + present/late 状态。

        migtest-06: 合法 teacher+student 首次签到恒 201（时间窗只决定 present/late、不报 422；
        404=学生不存在 / 403=寮边界 / 409=重复签到 才是别的码）。收紧到 201 + 断字段 ——
        否则 422 会放过请求体 schema 回归。
        """
        res = client.post(
            "/api/v1/study/checkins",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["student_id"] == str(seed_data["student"].id)
        assert data["status"] in ("present", "late")


class TestCancelToday:
    """POST /study/cancel-today"""

    def test_cancel_today_teacher_only(self, client, student_token):
        """学生 token → 403（教师专用）。"""
        res = client.post(
            "/api/v1/study/cancel-today",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 403

    def test_cancel_today_returns_count(self, client, teacher_token):
        """教师 cancel → 返回 cancelled_count。"""
        res = client.post(
            "/api/v1/study/cancel-today",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert "cancelled_count" in res.json()["data"]


class TestRoster:
    """学習対象名簿 管理 — GET / POST / DELETE /study/roster（杭田 060604 五-2）。"""

    def test_list_roster_requires_role(self, client, low_role_teacher_token):
        """管理係 → 可查看学習名簿（200）。

        权限分级改造（teacher_permission_v1.md §5 第 11 行「晚自习出席记录」名簿查看=V，
        一般宿管系含 V）后，旧「管理係不在名簿角色集 → 403」废弃。管理係 默认映射「一般宿管」对 study 有 V。
        管理动作（增删名簿）仍需 M（一般宿管 = V<M），下方 test_remove_requires_role 保持 403。
        """
        res = client.get(
            "/api/v1/study/roster",
            headers={"Authorization": f"Bearer {low_role_teacher_token}"},
        )
        assert res.status_code == 200, res.text

    def test_add_to_roster(self, client, teacher_token, seed_data):
        """老师把学生加入名簿 → 201，且记录 added_by = 操作老师。"""
        res = client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["student_id"] == str(seed_data["student"].id)
        # added_by 非空 = 老师手动加入（不是系统自动）
        assert data["added_by"] is not None

    def test_add_by_student_no(self, client, teacher_token, seed_data):
        """老师按学号（6 位）加入名簿 → 201。seed 学生学号 = 060218。"""
        res = client.post(
            "/api/v1/study/roster",
            json={"student_no": seed_data["student"].student_no},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["data"]["student_id"] == str(seed_data["student"].id)

    def test_add_no_identifier_422(self, client, teacher_token):
        """既不给 student_id 也不给 student_no → 422 请求体校验失败。"""
        res = client.post(
            "/api/v1/study/roster",
            json={},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422, res.text

    def test_add_then_listed(self, client, teacher_token, seed_data):
        """加入后，GET /study/roster 一览里能看到这个学生。"""
        client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        res = client.get(
            "/api/v1/study/roster",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        ids = [e["student_id"] for e in res.json()["data"]]
        assert str(seed_data["student"].id) in ids

    def test_add_nonexistent_student_404(self, client, teacher_token):
        """加一个不存在的 student_id → 404 NOT_FOUND。"""
        res = client.post(
            "/api/v1/study/roster",
            json={"student_id": "00000000-0000-0000-0000-000000000000"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 404, res.text
        assert res.json()["error"]["code"] == "NOT_FOUND"

    def test_add_duplicate_409(self, client, teacher_token, seed_data):
        """同学期同学生再加一次（已在籍）→ 409 ALREADY_IN_ROSTER。"""
        client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        res = client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "ALREADY_IN_ROSTER"

    def test_remove_then_not_listed(self, client, teacher_token, seed_data):
        """加入 → 移出（软删）后，一览里不再返回这个学生。"""
        client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        res_del = client.delete(
            f"/api/v1/study/roster/{seed_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res_del.status_code == 200, res_del.text
        assert res_del.json()["data"]["removed"] is True

        res = client.get(
            "/api/v1/study/roster",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        ids = [e["student_id"] for e in res.json()["data"]]
        assert str(seed_data["student"].id) not in ids

    def test_remove_soft_delete_keeps_row(
        self, client, db_session, teacher_token, seed_data
    ):
        """软删 = 行还在、只是 removed_at 非空（不物理删除）。"""
        from datetime import date

        from app import models

        client.post(
            "/api/v1/study/roster",
            json={"student_id": str(seed_data["student"].id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        client.delete(
            f"/api/v1/study/roster/{seed_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        today = date.today()
        term = _academic_term(today)
        rows = (
            db_session.query(models.StudyRoster)
            .filter(
                models.StudyRoster.student_id == seed_data["student"].id,
                models.StudyRoster.academic_term == term,
            )
            .all()
        )
        # 物理行仍在（软删），removed_at 已置非空
        assert len(rows) == 1
        assert rows[0].removed_at is not None

    def test_revive_removed_no_unique_clash(self, client, teacher_token, seed_data):
        """移出后再加入 → 复活旧行（removed_at 置回 None），不撞唯一约束、不新建第二行。"""

        sid = str(seed_data["student"].id)
        client.post(
            "/api/v1/study/roster",
            json={"student_id": sid},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        client.delete(
            f"/api/v1/study/roster/{sid}",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        # 再加入 — 应复活成功（201），而非 500 唯一约束冲突
        res = client.post(
            "/api/v1/study/roster",
            json={"student_id": sid},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text

        # 一览里又出现这个学生
        res_list = client.get(
            "/api/v1/study/roster",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        ids = [e["student_id"] for e in res_list.json()["data"]]
        assert sid in ids

    def test_remove_not_in_roster_404(self, client, teacher_token, seed_data):
        """移出一个不在名簿的学生 → 404 NOT_IN_ROSTER。"""
        res = client.delete(
            f"/api/v1/study/roster/{seed_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 404, res.text
        assert res.json()["error"]["code"] == "NOT_IN_ROSTER"

    def test_remove_requires_role(self, client, low_role_teacher_token, seed_data):
        """名簿管理 gate 外的角色移出 → 403。"""
        res = client.delete(
            f"/api/v1/study/roster/{seed_data['student'].id}",
            headers={"Authorization": f"Bearer {low_role_teacher_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_ROLE"


class TestCancelTodaySelectedDorm:
    """study-1：cancel_today 按登录选寮裁剪 roster。

    学習担当（→「一般宿管+晚自习」组，对 C_STUDY 是 MANAGE 且受选寮限制）选男寮
    中止时不应波及女寮学生 + 撤销其缺席扣分；不选寮（向后兼容）仍中止全部。
    """

    def _setup(self, db_session, seed_data):
        from app import security

        today = date.today()
        term = _academic_term(today)
        male = seed_data["student"]  # dorm_unit=1（男寮）
        female = models.Student(
            grade_code="05",
            class_code="03",
            seat_no="07",
            name="女寮study生",
            gender="female",
            room_no="W403",
            dorm_unit=4,
            is_overseas=False,
            email="joshi_study@test.jp",
        )
        db_session.add(female)
        db_session.flush()
        db_session.add(
            models.Account(
                student_id=female.id, password_hash=security.hash_password("x")
            )
        )
        db_session.add(models.StudyRoster(student_id=male.id, academic_term=term))
        db_session.add(models.StudyRoster(student_id=female.id, academic_term=term))
        db_session.add(
            models.Teacher(
                login_id="study_tantou",
                name="学習担当",
                email="study_tantou@test.jp",
                password_hash=security.hash_password("test-password-12345"),
                role="学習担当",
            )
        )
        db_session.commit()
        return male, female

    def _login(self, client, selected_dorm=None):
        body = {"login_id": "study_tantou", "password": "test-password-12345"}
        if selected_dorm is not None:
            body["selected_dorm"] = selected_dorm
        r = client.post("/api/v1/sessions/teacher", json=body)
        assert r.status_code == 200, r.text
        return r.json()["data"]["access_token"]

    def _checkin_of(self, db_session, student_id):
        from sqlalchemy import select

        return db_session.scalars(
            select(models.StudyCheckin).where(
                models.StudyCheckin.student_id == student_id
            )
        ).first()

    def test_cancel_today_selected_male_skips_female(
        self, client, seed_data, db_session
    ):
        male, female = self._setup(db_session, seed_data)
        tok = self._login(client, selected_dorm=1)  # 选男寮
        r = client.post(
            "/api/v1/study/cancel-today",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["cancelled_count"] == 1  # 只男寮 1 人
        db_session.expire_all()
        male_ci = self._checkin_of(db_session, male.id)
        female_ci = self._checkin_of(db_session, female.id)
        assert male_ci is not None and male_ci.status == "exempt"
        assert female_ci is None  # 女寮学生未被中止（不在男寮裁剪范围）

    def test_cancel_today_no_selection_cancels_all(self, client, seed_data, db_session):
        male, female = self._setup(db_session, seed_data)
        tok = self._login(client)  # 不选寮 → 全集（向后兼容）
        r = client.post(
            "/api/v1/study/cancel-today",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["cancelled_count"] == 2  # 男 + 女都中止
        db_session.expire_all()
        assert self._checkin_of(db_session, male.id).status == "exempt"
        assert self._checkin_of(db_session, female.id).status == "exempt"


class TestCheckinIntegrityErrorFallback:
    """审查 backend#8：签到与 finalize 撞 uq_sc_date 时的兜底不再原样返回 absent。"""

    def test_race_with_finalize_upgrades_absent_and_revokes_demerit(
        self, client, db_session, teacher_token, seed_data, study_roster, monkeypatch
    ):
        """模拟并发窗口：预查扑空 → INSERT 撞 uq_sc_date → 兜底重查到 finalize 刚写的
        absent 行 → 必须升级成 present/late 并撤销缺席扣分，而不是原样返回 absent。

        手法沿用本仓库既有先例（test_registration_code 的学号并发测试）：
        monkeypatch Session.scalars 让「既存レコード確認」预查第一次返回空。
        """
        from datetime import datetime
        from uuid import uuid4
        from zoneinfo import ZoneInfo

        from sqlalchemy import select
        from sqlalchemy.orm import Session

        from app import models

        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]
        today = datetime.now(ZoneInfo("Asia/Tokyo")).date()

        # 先落一条 finalize 形状的 absent 行 + 配套 study_absent 扣分
        absent_row = models.StudyCheckin(
            student_id=student.id,
            target_date=today,
            status="absent",
            recorded_by=teacher.id,
        )
        db_session.add(absent_row)
        db_session.flush()
        db_session.add(
            models.DemeritEvent(
                student_id=student.id,
                source_type="study_absent",
                source_event_id=absent_row.id,
                points=1.5,
                reason="学習欠席（テスト）",
                month=today.strftime("%Y-%m"),
                created_by_teacher_id=None,
            )
        )
        db_session.commit()
        absent_row_id = absent_row.id

        # 预查扑空一次 → 端点走 INSERT 路径 → 撞 uq_sc_date → IntegrityError 兜底
        real_scalars = Session.scalars
        state = {"suppress": True}

        def patched(self, statement, *a, **k):
            sql = str(statement)
            if state["suppress"] and "study_checkins" in sql and "target_date" in sql:
                state["suppress"] = False
                return real_scalars(
                    self,
                    select(models.StudyCheckin).where(
                        models.StudyCheckin.id == uuid4()
                    ),
                )
            return real_scalars(self, statement, *a, **k)

        monkeypatch.setattr(Session, "scalars", patched)

        res = client.post(
            "/api/v1/study/checkins",
            json={"student_id": str(student.id)},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["status"] in ("present", "late"), (
            "兜底把 finalize 的 absent 原样返回了（backend#8 回归）"
        )

        # 同一行被升级（不是另插一行），缺席扣分被撤销
        db_session.expire_all()
        row = db_session.get(models.StudyCheckin, absent_row_id)
        assert row.status in ("present", "late")
        dem = db_session.scalars(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == student.id,
                models.DemeritEvent.source_type == "study_absent",
                models.DemeritEvent.source_event_id == absent_row_id,
            )
        ).first()
        assert dem is not None and dem.revoked_at is not None, "缺席扣分未撤销"
