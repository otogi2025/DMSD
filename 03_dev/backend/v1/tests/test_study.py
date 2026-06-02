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
    cd 03_dev/backend/v1
    pytest tests/test_study.py -v
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app import models


@pytest.fixture
def study_roster(db_session, seed_data):
    """060218 学生加学習名簿（晩学習対象者）。"""
    today = date.today()
    season = "spring" if today.month <= 8 else "fall"
    roster = models.StudyRoster(
        student_id=seed_data["student"].id,
        academic_term=f"{today.year}-{season}",
    )
    db_session.add(roster)
    db_session.commit()
    return roster


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
        data = res.json()
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
        assert res.status_code in (200, 201), res.text
        data = res.json()
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
        assert res_create.status_code in (200, 201)
        req_id = res_create.json()["id"]

        # 教师承认
        res = client.post(
            f"/api/v1/study/absence-requests/{req_id}/decision",
            json={"decision": "approved", "comment": "了承"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "approved"

    def test_list_absence_requests_teacher(self, client, teacher_token):
        """教师拉欠席届一览 — 即使空也返回 200。"""
        res = client.get(
            "/api/v1/study/absence-requests",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)


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
        self, client, db_session, seed_data, student_token
    ):
        """只数当月（按 target_date）+ 全状态都算（含 rejected）+ 跨月排除。"""
        student = seed_data["student"]
        today = date.today()
        # 当月 2 条（不同日避开唯一约束）：1 条 pending 默认 + 1 条 rejected → 都该计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(today.year, today.month, 1),
                period="full",
                reason="当月1",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=date(today.year, today.month, 2),
                period="full",
                reason="当月2(被拒)",
                status="rejected",
            )
        )
        # 上个月 1 条 + 下个月 1 条 → 都不应计入
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=today - timedelta(days=40),
                period="full",
                reason="上月",
                status="approved",
            )
        )
        db_session.add(
            models.StudyAbsenceRequest(
                student_id=student.id,
                target_date=today + timedelta(days=40),
                period="full",
                reason="下月",
            )
        )
        db_session.commit()

        res = client.get(
            "/api/v1/study/absence-requests/me/summary",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["count"] == 2
        assert data["month"] == today.strftime("%Y-%m")


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
        assert res.json()["detail"]["code"] == "FORBIDDEN", res.text

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
        data = res.json()
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
        assert "cancelled_count" in res.json()
