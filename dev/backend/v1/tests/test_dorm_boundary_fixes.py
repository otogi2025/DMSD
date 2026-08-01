"""寮边界越权修复测试 — codex 复审 #1/#2/#3。

覆盖：
- #1  WS broadcast dorm_unit 过滤（单元测试：直接测 manager.broadcast 行为）
- #2  guidance list_guidance 跨寮现允许（200；寮过滤已取消）
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
        # asyncio.run() 自建并关闭事件循环 — 避免 get_event_loop() 在
        # Python 3.12 无运行循环时抛 DeprecationWarning（被 pytest 当 error）
        return asyncio.run(coro)

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

    def test_broadcast_dorm1_reaches_dorm2_teacher(self):
        """rollcall-1: dorm_unit=1 的事件，男寮另一栋老师（assigned_dorm=2）也应收到。

        男寮跨两栋（1 寮 + 2 寮）是常态。修复前 allowed = (1,2) if ==1 else (2,)，
        assigned_dorm=2 的老师 allowed=(2,) 收不到 1 寮事件 → 漏推。
        """
        mgr = TeacherConnectionManager()
        c2 = self._make_conn(2)  # 男寮 2 栋老师
        mgr._conns = [c2]
        self._run(mgr.broadcast({"type": "checkin"}, dorm_unit=1))
        c2.websocket.send_json.assert_called_once()

    def test_broadcast_dorm2_reaches_dorm1_teacher(self):
        """对称：dorm_unit=2 的事件，assigned_dorm=1 的男寮老师也收到（男寮全集 1+2）。"""
        mgr = TeacherConnectionManager()
        c1 = self._make_conn(1)  # 男寮 1 栋老师
        mgr._conns = [c1]
        self._run(mgr.broadcast({"type": "checkin"}, dorm_unit=2))
        c1.websocket.send_json.assert_called_once()

    def test_broadcast_dorm1_still_skips_dorm4(self):
        """回归：男寮事件仍不推给女寮老师（assigned_dorm=4 不在男寮全集）。"""
        mgr = TeacherConnectionManager()
        c4 = self._make_conn(4)
        mgr._conns = [c4]
        self._run(mgr.broadcast({"type": "checkin"}, dorm_unit=1))
        c4.websocket.send_json.assert_not_called()


# ─────────────────────────────────────────────────────────────
# 共用 fixture：男寮学生 + 女寮老师（越权场景）
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def cross_dorm_setup(db_session, seed_data):
    """
    seed_data 里已有男寮学生（dorm_unit=1），
    再创建一个女寮专职老师（assigned_dorm=4、寮務一般教師）用于越权测试。
    """
    from app import security

    pw = security.hash_password("test-password-12345")

    # 女寮专职老师（寮務一般教師 = 有指导履历权限，但管辖范围是女寮）
    joshi_teacher = models.Teacher(
        login_id="joshi_tannin",
        name="女寮先生",
        email="joshi@test.jp",
        password_hash=pw,
        role="寮務一般教師",
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
    return res.json()["data"]["access_token"]


# ─────────────────────────────────────────────────────────────
# #2  guidance 寮过滤越权测试
# ─────────────────────────────────────────────────────────────
class TestGuidanceDormBoundary:
    """guidance 寮过滤已取消 — 女寮老师查男寮学生指导履历 → 200。"""

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
        # tannin 是 seed_data 里的男寮老师（寮務一般教師、assigned_dorm=1）
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "tannin", "password": "test-password-12345"},
        )
        tannin_token = res.json()["data"]["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {tannin_token}"},
        )
        assert r.status_code == 200, r.text

    def test_list_guidance_other_dorm_now_allowed(
        self, client, cross_dorm_setup, joshi_token
    ):
        """女寮老师看男寮学生的指导履历 → 现已允许（2026-06-13 取消 guidance 寮过滤）。"""
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {joshi_token}"},
        )
        assert r.status_code == 200, r.text

    def test_cross_dorm_role_can_see_any(self, client, cross_dorm_setup, seed_data):
        """跨寮权限组老师（寮務部長、assigned_dorm=None）可看男女任一寮学生的指导履历。"""
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "ryomu_buchou", "password": "test-password-12345"},
        )
        token = res.json()["data"]["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/guidance",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, r.text


# ─────────────────────────────────────────────────────────────
# #3  student_profile get_current_principal 鉴权越权测试
# ─────────────────────────────────────────────────────────────
class TestStudentProfileAuth:
    """student_profile 改用 get_current_principal 后的鉴权行为。"""

    def test_teacher_guidance_view_allowed(self, client, cross_dorm_setup, seed_data):
        """权限组体系迁移后：国際交流部長（默认组「申請承認専用」）对 C_GUIDANCE 有 VIEW
        → 可访问学生档案（与 guidance.py 的 require_permission(C_GUIDANCE) 一致）。
        旧的「非寮務职位 → 403」职位集（_GUIDANCE_ROLES）判定已随权限分级改造废弃。"""
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "kokukou_buchou", "password": "test-password-12345"},
        )
        token = res.json()["data"]["access_token"]
        student_id = str(cross_dorm_setup["student"].id)
        r = client.get(
            f"/api/v1/students/{student_id}/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, r.text

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
        assert r.json()["data"]["guidance_records"] == []

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
            room_no="W101",
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
        token_a = res.json()["data"]["access_token"]

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


# ─────────────────────────────────────────────────────────────
# codex 第四轮：新增寮边界 403 测试（study / rollcall / discipline / study_online）
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def ryokan_teacher(db_session, seed_data):
    """女寮专职寮監（assigned_dorm=4、role=寮監）— 用于跨寮 403 场景。"""
    from app import security

    pw = security.hash_password("test-password-12345")
    t = models.Teacher(
        login_id="joshi_ryokan",
        name="女寮寮監",
        email="ryokan_joshi@test.jp",
        password_hash=pw,
        role="寮監",
        assigned_dorm=4,  # 女寮
    )
    db_session.add(t)
    db_session.commit()
    return t


@pytest.fixture
def ryokan_token(client, ryokan_teacher):
    """女寮寮監的登录令牌（登录时选女寮 selected_dorm=4，触发选寮过滤）。

    未传 selected_dorm 时 dorm_units 恒为全集 [1,2,4]（兼容路径），测不出跨寮 403。
    对齐 test_dorm_life.py：选了女寮后只能操作 4 寮，碰男寮学生 → FORBIDDEN_DORM。
    """
    res = client.post(
        "/api/v1/sessions/teacher",
        json={
            "login_id": "joshi_ryokan",
            "password": "test-password-12345",
            "selected_dorm": 4,
        },
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


class TestStudyDormBoundary:
    """study.py 寮边界补齐 — 选了女寮的寮監操作男寮学生 → 403。"""

    def test_create_checkin_wrong_dorm_forbidden(
        self, client, ryokan_token, seed_data, db_session
    ):
        """选女寮(selected_dorm=4)的寮監给男寮学生（dorm_unit=1）登出席 → 403 FORBIDDEN_DORM。"""
        student_id = str(seed_data["student"].id)  # dorm_unit=1（男寮）
        res = client.post(
            "/api/v1/study/checkins",
            json={"student_id": student_id},
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_patch_checkin_wrong_dorm_forbidden(
        self, client, ryokan_token, seed_data, db_session
    ):
        """选女寮的寮監修改男寮学生的出席记录 → 403 FORBIDDEN_DORM。"""
        from datetime import date

        # 直接在 DB 建 checkin 行（StudyCheckinOut 没有 id 字段，不能从 API 取）
        checkin = models.StudyCheckin(
            student_id=seed_data["student"].id,
            target_date=date.today(),
            status="init",
        )
        db_session.add(checkin)
        db_session.commit()
        db_session.refresh(checkin)

        patch_res = client.patch(
            f"/api/v1/study/checkins/{checkin.id}",
            json={"status": "absent", "override_reason": "テスト"},
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert patch_res.status_code == 403, patch_res.text
        assert patch_res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_create_checkin_own_dorm_ok(self, client, seed_data, db_session):
        """男寮寮監（assigned_dorm=1）给男寮学生（dorm_unit=1）登出席 → 正常。"""
        from app import security

        pw = security.hash_password("test-password-12345")
        otoko_ryokan = models.Teacher(
            login_id="otoko_ryokan",
            name="男寮寮監",
            email="ryokan_otoko@test.jp",
            password_hash=pw,
            role="寮監",
            assigned_dorm=1,  # 男寮
        )
        db_session.add(otoko_ryokan)
        db_session.commit()

        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "otoko_ryokan", "password": "test-password-12345"},
        )
        token = res.json()["data"]["access_token"]

        student_id = str(seed_data["student"].id)  # dorm_unit=1（男寮）
        r = client.post(
            "/api/v1/study/checkins",
            json={"student_id": student_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        # 201 = 新建 / 409 = 已存在 — 白名单显式断言，避免 500/422 假绿
        assert r.status_code in (201, 409), r.text


class TestRollcallSessionDormBoundary:
    """rollcall.py start/end session 寮边界 — 选了女寮的寮監操作男寮 session → 403。"""

    @pytest.fixture
    def male_dorm_session(self, db_session):
        """男寮点呼 session（dorm_unit_set=[1,2]，draft 状态 — CHECK 约束允许 draft/running/ended）。"""
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        session = models.RollCallSession(
            dorm_unit_set=[1, 2],
            session_type="evening",
            day_type="weekday",
            session_status="draft",
            scheduled_window_start_at=now - timedelta(minutes=10),
            scheduled_on_time_end_at=now + timedelta(minutes=10),
            scheduled_late_end_at=now + timedelta(minutes=20),
            scheduled_auto_end_at=now + timedelta(minutes=30),
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        return session

    @pytest.fixture
    def running_male_dorm_session(self, db_session):
        """男寮点呼 session（running 状态），用于测 end_session。"""
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        session = models.RollCallSession(
            dorm_unit_set=[1, 2],
            session_type="evening",
            day_type="weekday",
            session_status="running",
            started_at=now,
            scheduled_window_start_at=now - timedelta(minutes=5),
            scheduled_on_time_end_at=now + timedelta(minutes=10),
            scheduled_late_end_at=now + timedelta(minutes=20),
            scheduled_auto_end_at=now + timedelta(minutes=30),
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        return session

    def test_start_session_wrong_dorm_forbidden(
        self, client, ryokan_token, male_dorm_session
    ):
        """选女寮的寮監开男寮 session（dorm_unit_set=[1,2]）→ 403 FORBIDDEN_DORM。"""
        res = client.post(
            f"/api/v1/rollcall/sessions/{male_dorm_session.id}/start",
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_end_session_wrong_dorm_forbidden(
        self, client, ryokan_token, running_male_dorm_session
    ):
        """选女寮的寮監结束男寮 running session → 403 FORBIDDEN_DORM。"""
        res = client.post(
            f"/api/v1/rollcall/sessions/{running_male_dorm_session.id}/end",
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"


class TestDisciplineDormBoundary:
    """discipline.py 手动加扣分 / 撤销 寮边界 — 选了女寮的寮監操作男寮学生 → 403。"""

    def test_create_manual_demerit_wrong_dorm_forbidden(
        self, client, ryokan_token, seed_data
    ):
        """选女寮的寮監给男寮学生手动加扣分 → 403 FORBIDDEN_DORM。"""
        student_id = str(seed_data["student"].id)  # dorm_unit=1（男寮）
        res = client.post(
            "/api/v1/discipline/manual",
            json={
                "student_id": student_id,
                "target_points": 1.0,
                "reason": "テスト用手動扣分",
            },
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_revoke_demerit_wrong_dorm_forbidden(
        self, client, ryokan_token, seed_data, db_session
    ):
        """选女寮的寮監撤销男寮学生的扣分记录 → 403 FORBIDDEN_DORM。"""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        # 先直接往 DB 插一条扣分事件（不经 API，避免老师权限绕过）
        event = models.DemeritEvent(
            student_id=seed_data["student"].id,
            source_type="manual",
            points=1.0,
            reason="テスト",
            month=datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m"),
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)

        res = client.post(
            f"/api/v1/discipline/{event.id}/revoke",
            json={"revoke_reason": "テスト撤销"},
            headers={"Authorization": f"Bearer {ryokan_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_cross_dorm_role_can_add_demerit(self, client, seed_data):
        """跨寮役职（寮務課長）给任意学生手动加扣分 → 正常（不受寮限）。"""
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "ryomu_kachou", "password": "test-password-12345"},
        )
        token = res.json()["data"]["access_token"]
        student_id = str(seed_data["student"].id)
        r = client.post(
            "/api/v1/discipline/manual",
            json={
                "student_id": student_id,
                "target_points": 0.5,
                "reason": "跨寮役职测试",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201, r.text


# ─────────────────────────────────────────────────────────────
# incidents.py 事案记录 寮边界测试 —— 该 router 此前是唯一完全没有寮过滤的
# router（男寮当值老师能读到女生事案全文+真名），本组补齐边界测试。
# 判定口径：涉及学生须「全部」在可见寮内，否则 403 FORBIDDEN_DORM（与
# discipline / study / rollcall 同款）；无涉及学生的事案不受寮限制。
# ─────────────────────────────────────────────────────────────
class TestIncidentDormBoundary:
    """incidents.py 寮边界补齐测试。

    男寮学生用 seed_data["student"]（dorm_unit=1），女寮学生用本类的 female_student
    夹具新建（dorm_unit=4）。otoko_token = 选了男寮（selected_dorm=1）的老师令牌，
    与 discipline/study/rollcall 已用的 ryokan_token（选女寮）对称。跨寮基准数据
    用 conftest.py 的 teacher_token（寮務課長、未选寮 → dorm_units_for_teacher
    返回全集 [1,2,4]）来建，因为它不受寮过滤，男女学生都能挂。
    """

    @pytest.fixture
    def female_student(self, db_session, seed_data):
        """女寮学生（dorm_unit=4）—— seed_data 默认只有男寮学生，跨寮测试需要一个女寮对照。"""
        student = models.Student(
            grade_code="05",
            class_code="03",
            seat_no="12",
            name="鈴木花子",
            gender="female",
            room_no="W301",
            dorm_unit=4,
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)
        return student

    @pytest.fixture
    def otoko_token(self, client, seed_data):
        """男寮担当老师（tannin，assigned_dorm=1）登录时选男寮 selected_dorm=1 的令牌。

        必须显式选寮才会触发 dorm_units_for_teacher 的过滤 —— 未选寮时该函数
        向后兼容恒返回全集 [1,2,4]，测不出边界（对齐文件里已有的 ryokan_token 写法）。
        """
        res = client.post(
            "/api/v1/sessions/teacher",
            json={
                "login_id": "tannin",
                "password": "test-password-12345",
                "selected_dorm": 1,
            },
        )
        assert res.status_code == 200, res.text
        return res.json()["data"]["access_token"]

    def _create(self, client, token, involved_student_ids, title="テスト事案"):
        """建事案的公共 helper —— 不预判状态码（201 / 403 都可能），留给调用方断言。"""
        return client.post(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "body": "<p>テスト用の事案内容です。</p>",
                "involved_student_ids": [str(s) for s in involved_student_ids],
                "incident_date": "2026-05-30",
            },
        )

    # ── POST /incidents（建）──────────────────────────────

    def test_create_wrong_dorm_forbidden(self, client, otoko_token, female_student):
        """选男寮的老师建事案挂女寮学生 → 403 FORBIDDEN_DORM。"""
        res = self._create(client, otoko_token, [female_student.id])
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_create_own_dorm_ok(self, client, otoko_token, seed_data):
        """选男寮的老师建事案挂男寮学生 → 201 正常（不能误伤）。"""
        student_id = seed_data["student"].id  # dorm_unit=1（男寮）
        res = self._create(client, otoko_token, [student_id])
        assert res.status_code == 201, res.text

    def test_create_no_students_ok(self, client, otoko_token):
        """无涉及学生的事案 —— 不受寮限制，选了寮的老师也能正常建。"""
        res = self._create(client, otoko_token, [])
        assert res.status_code == 201, res.text

    # ── GET /incidents（列表）─────────────────────────────

    def test_list_hides_other_dorm_incident(
        self, client, otoko_token, teacher_token, female_student
    ):
        """只涉及女寮学生的事案（跨寮老师建）—— 对选了男寮的老师隐藏，列表里看不到。"""
        female_inc = self._create(
            client, teacher_token, [female_student.id], title="女子寮の事案"
        ).json()["data"]["id"]

        res = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 200, res.text
        ids = [i["id"] for i in res.json()["data"]["items"]]
        assert female_inc not in ids

    def test_list_shows_own_dorm_incident(
        self, client, otoko_token, teacher_token, seed_data
    ):
        """只涉及男寮学生的事案 —— 对选了男寮的老师可见（不能误伤）。"""
        male_inc = self._create(
            client, teacher_token, [seed_data["student"].id], title="男子寮の事案"
        ).json()["data"]["id"]

        res = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 200, res.text
        ids = [i["id"] for i in res.json()["data"]["items"]]
        assert male_inc in ids

    def test_list_shows_no_student_incident(self, client, otoko_token, teacher_token):
        """无涉及学生的事案 —— 对选了寮的老师仍可见（不属于任何寮，不误拦）。"""
        no_student_inc = self._create(
            client, teacher_token, [], title="対象学生なしの事案"
        ).json()["data"]["id"]

        res = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 200, res.text
        ids = [i["id"] for i in res.json()["data"]["items"]]
        assert no_student_inc in ids

    def test_list_unrestricted_teacher_sees_both(
        self, client, teacher_token, female_student, seed_data
    ):
        """未选寮（寮務課長、向后兼容路径）的老师 —— 男寮女寮事案都能看到。"""
        female_inc = self._create(
            client, teacher_token, [female_student.id], title="女子寮の事案2"
        ).json()["data"]["id"]
        male_inc = self._create(
            client, teacher_token, [seed_data["student"].id], title="男子寮の事案2"
        ).json()["data"]["id"]

        res = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        ids = [i["id"] for i in res.json()["data"]["items"]]
        assert female_inc in ids
        assert male_inc in ids

    # ── GET /incidents/{id}（详情）────────────────────────

    def test_get_detail_wrong_dorm_forbidden(
        self, client, otoko_token, teacher_token, female_student
    ):
        """选男寮的老师查女寮事案详情 → 403 FORBIDDEN_DORM。"""
        female_inc = self._create(
            client, teacher_token, [female_student.id], title="女子寮の事案詳細"
        ).json()["data"]["id"]

        res = client.get(
            f"/api/v1/incidents/{female_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_get_detail_own_dorm_ok(self, client, otoko_token, seed_data):
        """选男寮的老师查男寮事案详情 → 200 正常。"""
        male_inc = self._create(
            client, otoko_token, [seed_data["student"].id], title="男子寮の事案詳細"
        ).json()["data"]["id"]

        res = client.get(
            f"/api/v1/incidents/{male_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 200, res.text

    # ── PATCH /incidents/{id}（编辑）──────────────────────

    def test_patch_wrong_dorm_forbidden(
        self, client, otoko_token, teacher_token, female_student
    ):
        """选男寮的老师改女寮事案（哪怕只改标题）→ 403 FORBIDDEN_DORM。"""
        female_inc = self._create(
            client, teacher_token, [female_student.id], title="女子寮の事案（改前）"
        ).json()["data"]["id"]

        res = client.patch(
            f"/api/v1/incidents/{female_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
            json={"title": "改後タイトル"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_patch_add_wrong_dorm_student_forbidden(
        self, client, otoko_token, seed_data, female_student
    ):
        """选男寮的老师把男寮事案改成挂女寮学生 → 403 FORBIDDEN_DORM（新学生也要在可见寮内）。"""
        male_inc = self._create(
            client,
            otoko_token,
            [seed_data["student"].id],
            title="男子寮の事案（学生変更）",
        ).json()["data"]["id"]

        res = client.patch(
            f"/api/v1/incidents/{male_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
            json={"involved_student_ids": [str(female_student.id)]},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    # ── DELETE /incidents/{id}（软删）─────────────────────

    def test_delete_wrong_dorm_forbidden(
        self, client, otoko_token, teacher_token, female_student
    ):
        """选男寮的老师删女寮事案 → 403 FORBIDDEN_DORM。"""
        female_inc = self._create(
            client, teacher_token, [female_student.id], title="女子寮の事案（削除用）"
        ).json()["data"]["id"]

        res = client.delete(
            f"/api/v1/incidents/{female_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["error"]["code"] == "FORBIDDEN_DORM"

    def test_delete_own_dorm_ok(self, client, otoko_token, seed_data):
        """选男寮的老师删男寮事案 → 204 正常。"""
        male_inc = self._create(
            client,
            otoko_token,
            [seed_data["student"].id],
            title="男子寮の事案（削除用）",
        ).json()["data"]["id"]

        res = client.delete(
            f"/api/v1/incidents/{male_inc}",
            headers={"Authorization": f"Bearer {otoko_token}"},
        )
        assert res.status_code == 204, res.text

    # ── 姓名 chip 防泄漏（_build_student_name_map 的防御性寮过滤）───

    def test_name_map_excludes_out_of_dorm_student(
        self, db_session, seed_data, female_student
    ):
        """白盒测试 _build_student_name_map：直接在 DB 建一条跨寮混合事案（绕开
        _assert_incident_in_dorm / _filter_incidents_by_dorm 的可见性闸——这两者在
        当前实现下是「全员在寮内才可见」，正常 API 流程走不到「事案可见但涉及学生
        部分不可见」这种状态），验证姓名 map 本身的防御性寮过滤单独生效：
        选了男寮的老师解析姓名时，只认男寮学生，女寮学生不出现在 map 里。
        """
        from datetime import date

        from app.routers.incidents import _build_student_name_map

        row = models.IncidentRecord(
            title="混合寮事案（白盒テスト）",
            body="<p>テスト用の事案内容です。</p>",
            involved_student_ids=[
                str(seed_data["student"].id),  # 男寮 dorm_unit=1
                str(female_student.id),  # 女寮 dorm_unit=4
            ],
            recorded_by=seed_data["teachers"]["tannin"].id,
            incident_date=date(2026, 5, 30),
        )
        db_session.add(row)
        db_session.commit()

        tannin = seed_data["teachers"]["tannin"]
        tannin._selected_dorm = 1  # 手动模拟登录选男寮（不经 JWT/HTTP）
        name_map = _build_student_name_map(db_session, [row], tannin)

        assert str(seed_data["student"].id) in name_map
        assert str(female_student.id) not in name_map
