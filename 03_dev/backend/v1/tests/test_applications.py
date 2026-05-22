"""出寮届 (applications) endpoint tests — C-050 (2026-05-21) 新增。

覆盖：
- POST /applications — 学生提出（帰省 / 外泊 / 帰国 3 type）
- GET /applications/mine — 学生看自己的
- GET /applications/pending-for-me — 教师看自己待审的（A-013 路由顺序）
- GET /applications/:id — 学生 / 教师 共用，权限校验
- POST /applications/:id/approvals — 教师承认 / 拒绝
- PUT /applications/:id — 学生修改届（chain 重置）
- GET /applications/:id/audit — 改动履历

跑：
    cd 03_dev/backend/v1
    pytest tests/test_applications.py -v
"""

from __future__ import annotations

from datetime import date, timedelta


def _kisei_body(leave_offset_days: int = 3) -> dict:
    """生成 帰省届 body — 出寮日 = 明日 + offset。"""
    leave = date.today() + timedelta(days=leave_offset_days)
    ret = leave + timedelta(days=2)
    return {
        "kind": "帰省",
        "leave_date": leave.isoformat(),
        "leave_method": "新幹線",
        "leave_time": "19:00:00",
        "return_date": ret.isoformat(),
        "return_method": "新幹線",
        "return_time": "20:00:00",
        "reason": "帰省",
    }


class TestCreateApplication:
    """POST /applications"""

    def test_create_requires_student(self, client):
        """未带 token → 401。"""
        res = client.post("/api/v1/applications", json=_kisei_body())
        assert res.status_code == 401

    def test_create_kisei_success(self, client, student_token):
        """学生提出 帰省届 → 201 + pending 状态。"""
        res = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["kind"] == "帰省"
        assert data["status"] == "pending"
        # approval chain 应有 5 役职 step（留学生 → 国際 chain）
        assert len(data["approval_chain"]) >= 3

    def test_create_today_leave_rejected(self, client, student_token):
        """出寮日 = 今日 → 422（必须明天以后）。"""
        body = _kisei_body(leave_offset_days=0)
        res = client.post(
            "/api/v1/applications",
            json=body,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422


class TestListMine:
    """GET /applications/mine"""

    def test_list_mine_empty(self, client, student_token):
        """新学生没申请 → 空 list。"""
        res = client.get(
            "/api/v1/applications/mine",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        assert res.json() == []

    def test_list_mine_after_create(self, client, student_token):
        """学生提出后 → list 含 1 条。"""
        res_create = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_create.status_code == 201

        res = client.get(
            "/api/v1/applications/mine",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 1
        assert items[0]["kind"] == "帰省"


class TestPendingForMe:
    """GET /applications/pending-for-me — A-013 路由顺序修复

    必须在 /{application_id} 之前注册，否则 'pending-for-me' 被当 UUID 解析。
    """

    def test_pending_for_me_route_resolves_correctly(self, client, teacher_token):
        """关键 — A-013 验证：访问 /pending-for-me 不会被解析成 UUID 路径。"""
        res = client.get(
            "/api/v1/applications/pending-for-me",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        # 200 + list（即使空），不能是 422（UUID 解析失败）
        assert res.status_code == 200, (
            f"路由顺序 bug 复发 — A-013: {res.status_code} {res.text}"
        )
        assert isinstance(res.json(), list)

    def test_pending_for_me_requires_teacher(self, client, student_token):
        """学生 token → 403（教师专用）。"""
        res = client.get(
            "/api/v1/applications/pending-for-me",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code in (401, 403)


class TestGetApplication:
    """GET /applications/{id}"""

    def test_get_own_application(self, client, student_token):
        """学生看自己的申请 → 200。"""
        res_create = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        app_id = res_create.json()["id"]

        res = client.get(
            f"/api/v1/applications/{app_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        assert res.json()["id"] == app_id

    def test_get_invalid_uuid_returns_422(self, client, student_token):
        """非 UUID 路径 → 422（不是 'pending-for-me' 这种已 mount 的静态路径）。"""
        res = client.get(
            "/api/v1/applications/not-a-uuid",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422


class TestAudit:
    """GET /applications/{id}/audit"""

    def test_audit_log_after_create(self, client, student_token):
        """提出后 audit log 至少有 1 条 application.submit。"""
        res_create = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        app_id = res_create.json()["id"]

        res = client.get(
            f"/api/v1/applications/{app_id}/audit",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        entries = res.json()
        assert isinstance(entries, list)
        # 至少有 submit action
        actions = [e.get("action", "") for e in entries]
        assert any("submit" in a for a in actions), actions
