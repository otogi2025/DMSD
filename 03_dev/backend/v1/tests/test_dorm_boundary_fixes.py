"""寮边界越权修复测试 — codex 复审 #1/#2/#3。

覆盖：
- #1  WS broadcast dorm_unit 过滤（单元测试：直接测 manager.broadcast 行为）
- #2  guidance list_guidance / list_disclosure_requests 寮过滤（越权场景 403）
- #3  student_profile get_current_principal 鉴权（学生 token 看他人 → 403）
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app import models
from app.ws_manager import TeacherConnectionManager, _TeacherConn


# ─────────────────────────────────────────────────────────────
# #1  WS broadcast dorm_unit 过滤（单元测试）
# ─────────────────────────────────────────────────────────────
class TestWsBroadcastDormFilter:
    """broadcast(dorm_unit=X) 只推给对应寮或跨寮管理员。"""

    def _make_conn(self, assigned_dorm: int | None) -> _TeacherConn:
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        return _TeacherConn(
            teacher_id=uuid4(),
            websocket=ws,
            assigned_dorm=assigned_dorm,
        )

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_broadcast_no_filter_reaches_all(self):
        """dorm_unit=None（全局广播）— 所有连接都收到。"""
        mgr = TeacherConnectionManager()
        c1 = self._make_conn(1)  # 男寮老师
        c4 = self._make_conn(4)  # 女寮老师
        cn = self._make_conn(None)  # 跨寮管理员
        mgr._conns = [c1, c4, cn]
        self._run(mgr.broadcast({"type": "test"}, dorm_unit=None))
        c1.websocket.send_json.assert_called_once()
        c4.websocket.send_json.assert_called_once()
        cn.websocket.send_json.assert_called_once()

    def test_broadcast_dorm1_skips_dorm4(self):
        """dorm_unit=1 — 女寮老师（assigned_dorm=4）不收到，男寮老师和跨寮管理员收到。"""
        mgr = TeacherConnectionManager()
        c1 = self._make_conn(1)
        c4 = self._make_conn(4)
        cn = self._make_conn(None)
        mgr._conns = [c1, c4, cn]
        self._run(mgr.broadcast({"type": "checkin"}, dorm_unit=1))
        c1.websocket.send_json.assert_called_once()
        c4.websocket.send_json.assert_not_called()  # 女寮老师不收
        cn.websocket.send_json.assert_called_once()  # 跨寮管理员收

    def test_broadcast_dorm4_skips_dorm1(self):
        """dorm_unit=4 — 男寮老师（assigned_dorm=1）不收到，女寮老师和跨寮管理员收到。"""
        mgr = TeacherConnectionManager()
        c1 = self._make_conn(1)
        c4 = self._make_conn(4)
        cn = self._make_conn(None)
        mgr._conns = [c1, c4, cn]
        self._run(mgr.broadcast({"type": "checkin"}, dorm_unit=4))
        c1.websocket.send_json.assert_not_called()
        c4.websocket.send_json.assert_called_once()
        cn.websocket.send_json.assert_called_once()


# ─────────────────────────────────────────────────────────────
# 共用 fixture：男寮学生 + 女寮老师（越权场景）
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def cross_dorm_setup(db_session, seed_data):
    """
    seed_data 里已有男寮学生（dorm_unit=1），
    再创建一个女寮专职老师（assigned_dorm=4、寮務一般教师）用于越权测试。
    """
    from app import security

    pw = security.hash_password("test-password-12345")

    # 女寮专职老师（寮務一般教师 = 有指导履历权限，但管辖范围是女寮）
    joshi_teacher = models.Teacher(
        login_id="joshi_tannin",
        name="女寮先生",
        email="joshi@test.jp",
        password_hash=pw,
        role="寮務一般教师",
        assigned_dorm=4,  # 女寮
    )
    db_session.add(joshi_teacher)
    db_session.commit()
    return {
        "student": seed_data["student"],  # dorm_unit=1（男寮）
        "joshi_teacher": joshi_teacher,
        "teachers": seed_data["teachers"],
    }


@pytest.fixture
def joshi_token(client, cross_dorm_setup):
    """女寮专职老师的登录令牌。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "joshi_tannin", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


# ─────────────────────────────────────────────────────────────
# #2  guidance 寮过滤越权测试
# ─────────────────────────────────────────────────────────────
class TestGuidanceDormBoundary:
    """女寮老师查男寮学生指导履历 → 403。"""

    def _create_guidance(self, client, student_id, token):
        return client.post(
            f"/api/v1/students/{student_id}/guidance",
            json={
                "content": "テスト指導",
                "category": "life",
                "guidance_date": "2026-05-30",
                "confidential": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_list_guidance_own_dorm_ok(self, client, cross_dorm_setup, seed_data):
        """男寮老师（tannin、assigned_dorm=1）能查看男寮学生的指导履历。"""
        # tannin 是 seed_data 里的男寮老师（寮務一般教师、assigned_dorm=1）
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "tannin", "password": "test-password-12345"},
        )
        tannin_token = res.json()["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {tannin_token}"},
        )
        assert r.status_code == 200, r.text

    def test_list_guidance_other_dorm_403(self, client, cross_dorm_setup, joshi_token):
        """女寮老師が男寮学生の指導履歴を見ようとすると 403。"""
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {joshi_token}"},
        )
        assert r.status_code == 403, r.text
        assert r.json()["detail"]["code"] == "FORBIDDEN_DORM"

    def test_cross_dorm_role_can_see_any(self, client, cross_dorm_setup, seed_data):
        """跨寮役职（寮務部長、assigned_dorm=None）は男女どちらの学生も見れる。"""
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "ryomu_buchou", "password": "test-password-12345"},
        )
        token = res.json()["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, r.text

    def test_list_disclosure_requests_dorm_filter(
        self, client, cross_dorm_setup, joshi_token, student_token
    ):
        """男寮学生提交开示申请后，女寮老师的列表里不包含该申请。"""
        # 学生提交申请
        res = client.post(
            f"/api/v1/students/{cross_dorm_setup['student'].id}/guidance/disclosure-request",
            json={"reason": "確認したい"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text

        # 女寮老师拉列表 → 男寮学生的申请不应出现
        r = client.get(
            "/api/v1/guidance/disclosure-requests",
            headers={"Authorization": f"Bearer {joshi_token}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["items"] == [], "女寮老师不应看到男寮学生的开示申请"

    def test_list_disclosure_requests_own_dorm_visible(
        self, client, cross_dorm_setup, student_token, seed_data
    ):
        """男寮老师能看到男寮学生的开示申请。"""
        # 学生提交申请
        res = client.post(
            f"/api/v1/students/{cross_dorm_setup['student'].id}/guidance/disclosure-request",
            json={"reason": "確認したい"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text

        # 男寮老师（tannin）拉列表 → 应看到 1 条
        res2 = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "tannin", "password": "test-password-12345"},
        )
        tannin_token = res2.json()["access_token"]
        r = client.get(
            "/api/v1/guidance/disclosure-requests",
            headers={"Authorization": f"Bearer {tannin_token}"},
        )
        assert r.status_code == 200, r.text
        assert len(r.json()["items"]) == 1


# ─────────────────────────────────────────────────────────────
# #3  student_profile get_current_principal 鉴权越权测试
# ─────────────────────────────────────────────────────────────
class TestStudentProfileAuth:
    """student_profile 改用 get_current_principal 后的鉴权行为。"""

    def test_teacher_wrong_role_403(self, client, cross_dorm_setup, seed_data):
        """非寮務系老师（国際交流部長）访问学生档案 → 403。"""
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "kokukou_buchou", "password": "test-password-12345"},
        )
        token = res.json()["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 403, r.text

    def test_student_can_see_own_profile(
        self, client, cross_dorm_setup, student_token, seed_data
    ):
        """学生本人能查看自己的档案（指导履历块返回空列表）。"""
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/profile",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["guidance_records"] == []

    def test_student_cannot_see_other_student_profile(
        self, client, cross_dorm_setup, seed_data, db_session
    ):
        """学生 A 查看学生 B 的档案 → 403。"""
        from app import security

        pw = security.hash_password("test-password-12345")
        # 创建另一个学生 B（女寮）
        student_b = models.Student(
            grade_code="05",
            class_code="01",
            seat_no="01",
            name="別の学生",
            gender="female",
            room_no="F101",
            dorm_unit=4,
        )
        db_session.add(student_b)
        db_session.flush()
        db_session.add(models.Account(student_id=student_b.id, password_hash=pw))
        db_session.commit()

        # 用学生 A 的账号登录
        res = client.post(
            "/api/v1/sessions/student",
            json={"student_no": "060218", "password": "test-password-12345"},
        )
        token_a = res.json()["access_token"]

        # 访问学生 B 的档案 → 应被拒绝
        r = client.get(
            f"/api/v1/students/{student_b.id}/profile",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert r.status_code == 403, r.text

    def test_no_token_401(self, client, cross_dorm_setup, seed_data):
        """不带令牌访问 → 401。"""
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(f"/api/v1/students/{student_id}/profile")
        assert r.status_code == 401, r.text
