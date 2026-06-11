"""指導履歴 + 事案録入 测试 (spec §7.9/§7.10)。

覆盖：
- 指导记录: POST 创建 / GET 列表 / 403 非寮務老师 / 404 学生不存在
- 开示申请: 学生 POST 申请 / 重复申请 409 / 403 只能申请自己的
- 老师查开示列表 / POST 决定开示 / 决定后再决定 409
- 事案: POST 创建 / GET 列表 / GET 详情 / PATCH 编辑 / DELETE 软删
- 事案 403 非寮務 / 404 不存在
"""

from __future__ import annotations

import pytest


# -----------------------------------------------------------------------
# 辅助 fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def ryomu_token(client, seed_data):
    """寮務課長 token — 有指导履历 + 事案权限。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryomu_kachou", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def tannin_token(client, seed_data):
    """寮務一般教師 token — 也有指导履历 + 事案权限（同属寮務系）。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "tannin", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def kokukou_token(client, seed_data):
    """国際交流部長 token — 不在 _GUIDANCE_ROLES / _INCIDENT_ROLES，应 403。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "kokukou_buchou", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _student_id(seed_data) -> str:
    return str(seed_data["student"].id)


# -----------------------------------------------------------------------
# 指导记录 tests
# -----------------------------------------------------------------------
class TestGuidanceRecords:
    def test_create_and_list(self, client, seed_data, ryomu_token):
        """老师创建指导记录 → 列表能查到。"""
        sid = _student_id(seed_data)
        res = client.post(
            f"/api/v1/students/{sid}/guidance",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={
                "student_id": sid,
                "content": "授業中の態度について指導した",
                "category": "生活态度",
                "guidance_date": "2026-05-30",
                "confidential": True,
            },
        )
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["student_id"] == sid
        assert data["content"] == "授業中の態度について指導した"
        assert data["confidential"] is True

        # 列表查到
        res2 = client.get(
            f"/api/v1/students/{sid}/guidance",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res2.status_code == 200
        assert len(res2.json()["items"]) == 1

    def test_create_403_non_ryomu(self, client, seed_data, kokukou_token):
        """国際交流部長无权录入指导记录 → 403。"""
        sid = _student_id(seed_data)
        res = client.post(
            f"/api/v1/students/{sid}/guidance",
            headers={"Authorization": f"Bearer {kokukou_token}"},
            json={
                "student_id": sid,
                "content": "テスト",
                "guidance_date": "2026-05-30",
            },
        )
        assert res.status_code == 403

    def test_create_404_student_not_found(self, client, seed_data, ryomu_token):
        """不存在的学生 ID → 404。"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = client.post(
            f"/api/v1/students/{fake_id}/guidance",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={
                "student_id": fake_id,
                "content": "テスト",
                "guidance_date": "2026-05-30",
            },
        )
        assert res.status_code == 404

    def test_list_403_non_ryomu(self, client, seed_data, kokukou_token):
        """国際交流部長 → 可查看指导记录列表（200）。

        权限分级改造（teacher_permission_v1.md §5 第 15 行「指导履历」5 组全部至少 V）后，
        旧「国際交流部長不在指导角色集 → 403」废弃。国際 默认映射「申請承認専用」，对指导履历有 V（查看）。
        管理动作（录入）仍需 M，下方 test_create_403_non_ryomu 保持 403。
        """
        sid = _student_id(seed_data)
        res = client.get(
            f"/api/v1/students/{sid}/guidance",
            headers={"Authorization": f"Bearer {kokukou_token}"},
        )
        assert res.status_code == 200


# -----------------------------------------------------------------------
# 开示申请 tests
# -----------------------------------------------------------------------
class TestGuidanceDisclosure:
    def test_student_submit_and_teacher_list(
        self, client, seed_data, student_token, ryomu_token
    ):
        """学生提交开示申请 → 老师列表能查到。"""
        sid = _student_id(seed_data)
        res = client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"reason": "自分の指導記録を確認したい"},
        )
        assert res.status_code == 201, res.text
        req_id = res.json()["id"]
        assert res.json()["status"] == "pending"

        # 老师查列表
        res2 = client.get(
            "/api/v1/guidance/disclosure-requests",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res2.status_code == 200
        ids = [item["id"] for item in res2.json()["items"]]
        assert req_id in ids

    def test_duplicate_pending_409(self, client, seed_data, student_token):
        """学生已有 pending 申请时再提交 → 409。"""
        sid = _student_id(seed_data)
        payload = {"reason": "確認したい"}
        client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json=payload,
        )
        res2 = client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json=payload,
        )
        assert res2.status_code == 409

    def test_student_cannot_apply_for_others(
        self, client, seed_data, student_token, db_session
    ):
        """学生不能替别人提申请 → 403。"""
        from app import models, security

        other = models.Student(
            grade_code="07",
            class_code="01",
            seat_no="01",
            name="別の学生",
            gender="male",
            room_no="M201",
            dorm_unit=1,
        )
        db_session.add(other)
        db_session.flush()
        db_session.add(
            models.Account(
                student_id=other.id,
                password_hash=security.hash_password("test-password-12345"),
            )
        )
        db_session.commit()

        res = client.post(
            f"/api/v1/students/{other.id}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"reason": "他人の記録を見たい"},
        )
        assert res.status_code == 403

    def test_teacher_decide_approved_full(
        self, client, seed_data, student_token, ryomu_token
    ):
        """老师决定全部开示 → status 变 approved_full。"""
        sid = _student_id(seed_data)
        res = client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"reason": "確認したい"},
        )
        req_id = res.json()["id"]

        res2 = client.post(
            f"/api/v1/guidance/disclosure-requests/{req_id}/decision",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"decision": "approved_full", "decision_note": "問題なし"},
        )
        assert res2.status_code == 200, res2.text
        assert res2.json()["status"] == "approved_full"

    def test_decide_already_decided_409(
        self, client, seed_data, student_token, ryomu_token
    ):
        """已决定的申请再决定 → 409。"""
        sid = _student_id(seed_data)
        res = client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json={},
        )
        req_id = res.json()["id"]

        client.post(
            f"/api/v1/guidance/disclosure-requests/{req_id}/decision",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"decision": "rejected"},
        )
        res2 = client.post(
            f"/api/v1/guidance/disclosure-requests/{req_id}/decision",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"decision": "approved_full"},
        )
        assert res2.status_code == 409

    def test_decide_404_not_found(self, client, seed_data, ryomu_token):
        """不存在的申请 ID → 404。"""
        fake = "00000000-0000-0000-0000-000000000000"
        res = client.post(
            f"/api/v1/guidance/disclosure-requests/{fake}/decision",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"decision": "rejected"},
        )
        assert res.status_code == 404

    def test_list_403_non_ryomu(self, client, seed_data, kokukou_token):
        """国際交流部長 → 可查看开示申请列表（200）。

        同指导履历（teacher_permission_v1.md §5 第 15 行 5 组全部至少 V）：国際 默认「申請承認専用」有 V。
        """
        res = client.get(
            "/api/v1/guidance/disclosure-requests",
            headers={"Authorization": f"Bearer {kokukou_token}"},
        )
        assert res.status_code == 200


# -----------------------------------------------------------------------
# 事案録入 tests
# -----------------------------------------------------------------------
class TestIncidentRecords:
    def _create(self, client, token, **kw):
        payload = {
            "title": "門限違反事案",
            "body": "<p>22時以降に帰寮した事案を記録する。</p>",
            "involved_student_ids": [],
            "incident_date": "2026-05-30",
        }
        payload.update(kw)
        res = client.post(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        return res

    def test_create_and_list(self, client, seed_data, ryomu_token):
        """老师创建事案 → 列表能查到。"""
        res = self._create(client, ryomu_token, title="テスト事案")
        assert res.status_code == 201, res.text
        inc_id = res.json()["id"]

        res2 = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res2.status_code == 200
        ids = [i["id"] for i in res2.json()["items"]]
        assert inc_id in ids

    def test_get_detail(self, client, seed_data, ryomu_token):
        """创建后按 ID 查详情。"""
        inc_id = self._create(client, ryomu_token, title="詳細テスト").json()["id"]
        res = client.get(
            f"/api/v1/incidents/{inc_id}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res.status_code == 200
        assert res.json()["title"] == "詳細テスト"

    def test_patch(self, client, seed_data, ryomu_token):
        """编辑事案标题。"""
        inc_id = self._create(client, ryomu_token, title="旧タイトル").json()["id"]
        res = client.patch(
            f"/api/v1/incidents/{inc_id}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"title": "新タイトル"},
        )
        assert res.status_code == 200
        assert res.json()["title"] == "新タイトル"
        assert res.json()["updated_at"] is not None

    def test_soft_delete(self, client, seed_data, ryomu_token):
        """软删后列表查不到，详情也 404。"""
        inc_id = self._create(client, ryomu_token, title="削除テスト").json()["id"]

        res_del = client.delete(
            f"/api/v1/incidents/{inc_id}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res_del.status_code == 204

        # 列表查不到
        res_list = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        ids = [i["id"] for i in res_list.json()["items"]]
        assert inc_id not in ids

        # 详情 404
        res_get = client.get(
            f"/api/v1/incidents/{inc_id}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res_get.status_code == 404

    def test_create_with_involved_students(self, client, seed_data, ryomu_token):
        """涉及学生列表正常录入。"""
        sid = _student_id(seed_data)
        res = self._create(
            client,
            ryomu_token,
            title="複数学生事案",
            involved_student_ids=[sid],
        )
        assert res.status_code == 201
        assert sid in res.json()["involved_student_ids"]
        # 杭田 2026-06-04 五-6: involved_students 带姓名（前端做可点击跳个人档案的 chip）
        involved = res.json()["involved_students"]
        assert len(involved) == 1, involved
        assert involved[0]["id"] == sid
        assert involved[0]["name"], "涉及学生姓名应非空"

    def test_create_invalid_student_404(self, client, seed_data, ryomu_token):
        """涉及学生 ID 不存在 → 404。"""
        fake = "00000000-0000-0000-0000-000000000000"
        res = self._create(client, ryomu_token, involved_student_ids=[fake])
        assert res.status_code == 404

    def test_create_403_non_ryomu(self, client, seed_data, kokukou_token):
        """国際交流部長无权录入事案 → 403。"""
        res = self._create(client, kokukou_token)
        assert res.status_code == 403

    def test_list_403_non_ryomu(self, client, seed_data, kokukou_token):
        """国際交流部長 → 可查看事案列表（200）。

        权限分级改造（teacher_permission_v1.md §5 第 14 行「事案记录」5 组全部至少 V）后，
        旧「国際交流部長不在事案角色集 → 403」废弃。国際 默认「申請承認専用」有 V（查看）。
        管理动作（录入）仍需 M，上方 test_create_403_non_ryomu 保持 403。
        """
        res = client.get(
            "/api/v1/incidents",
            headers={"Authorization": f"Bearer {kokukou_token}"},
        )
        assert res.status_code == 200

    def test_get_404_not_found(self, client, seed_data, ryomu_token):
        """不存在的事案 ID → 404。"""
        fake = "00000000-0000-0000-0000-000000000000"
        res = client.get(
            f"/api/v1/incidents/{fake}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res.status_code == 404

    def test_patch_404_not_found(self, client, seed_data, ryomu_token):
        """不存在的事案 PATCH → 404。"""
        fake = "00000000-0000-0000-0000-000000000000"
        res = client.patch(
            f"/api/v1/incidents/{fake}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
            json={"title": "新タイトル"},
        )
        assert res.status_code == 404

    def test_delete_404_not_found(self, client, seed_data, ryomu_token):
        """不存在的事案 DELETE → 404。"""
        fake = "00000000-0000-0000-0000-000000000000"
        res = client.delete(
            f"/api/v1/incidents/{fake}",
            headers={"Authorization": f"Bearer {ryomu_token}"},
        )
        assert res.status_code == 404


# -----------------------------------------------------------------------
# #2 major — guidance 写操作寮边界测试
# -----------------------------------------------------------------------
class TestGuidanceDormBoundary:
    """create_guidance / decide_disclosure 对跨寮老师应返回 403。

    场景：学生在 dorm_unit=1（男寮），女寮老师（assigned_dorm=4）无权操作。
    """

    @pytest.fixture
    def joshi_token(self, client, seed_data, db_session):
        """女寮担当・寮務一般教師 — dorm_unit=4 管辖，学生 dorm_unit=1 → 跨寮。"""
        from app import models, security

        t = models.Teacher(
            login_id="joshi_tannin",
            name="女寮太郎",
            email="jt@test.jp",
            password_hash=security.hash_password("test-password-12345"),
            role="寮務一般教師",
            assigned_dorm=4,  # 女寮 → dorm_units_for_teacher 返回 [4]
        )
        db_session.add(t)
        db_session.commit()
        res = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "joshi_tannin", "password": "test-password-12345"},
        )
        assert res.status_code == 200, res.text
        return res.json()["access_token"]

    def test_create_guidance_cross_dorm_403(self, client, seed_data, joshi_token):
        """女寮老师对男寮学生录入指导记录 → 403 FORBIDDEN_DORM。"""
        sid = _student_id(seed_data)  # 学生 dorm_unit=1
        res = client.post(
            f"/api/v1/students/{sid}/guidance",
            headers={"Authorization": f"Bearer {joshi_token}"},
            json={
                "student_id": sid,
                "content": "跨寮録入テスト",
                "guidance_date": "2026-05-30",
            },
        )
        assert res.status_code == 403, res.text
        assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"

    def test_decide_disclosure_cross_dorm_403(
        self, client, seed_data, student_token, joshi_token
    ):
        """女寮老师审批男寮学生的开示申请 → 403 FORBIDDEN_DORM。"""
        sid = _student_id(seed_data)
        # 学生先提交开示申请
        r = client.post(
            f"/api/v1/students/{sid}/guidance/disclosure-request",
            headers={"Authorization": f"Bearer {student_token}"},
            json={},
        )
        assert r.status_code == 201, r.text
        req_id = r.json()["id"]

        # 女寮老师尝试审批 → 跨寮，应 403
        res = client.post(
            f"/api/v1/guidance/disclosure-requests/{req_id}/decision",
            headers={"Authorization": f"Bearer {joshi_token}"},
            json={"decision": "approved_full"},
        )
        assert res.status_code == 403, res.text
        assert res.json()["detail"]["code"] == "FORBIDDEN_DORM"
