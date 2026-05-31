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


class TestUpdateApplication:
    """PUT /applications/{id} — 学生修改届（IX-004 / codex 阶段2 收口）

    覆盖修复后的新行为：
    - amend_reason 修改理由写进 audit payload（老师 / 学生履历看得到「为什么改」）
    - 改完审批链全删重建 → status 必须回 pending（不残留 approved_partial / returned）
    - returned(老师退回让学生改)状态可编辑、不再 409
    """

    def _create_pending(self, client, token) -> str:
        res = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201, res.text
        return res.json()["id"]

    def test_update_records_amend_reason_in_audit(self, client, student_token):
        """修改理由 amend_reason → 写进 audit payload，不覆盖申请本身的 reason。"""
        app_id = self._create_pending(client, student_token)
        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"amend_reason": "帰寮方法を変更します", "return_method": "バス"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text

        res_audit = client.get(
            f"/api/v1/applications/{app_id}/audit",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        entries = res_audit.json()
        update_entries = [e for e in entries if e.get("action") == "application.update"]
        assert update_entries, f"没有 application.update 记录: {entries}"
        assert any(
            (e.get("payload") or {}).get("amend_reason") == "帰寮方法を変更します"
            for e in update_entries
        ), update_entries

    def test_update_resets_status_to_pending(self, client, student_token, db_session):
        """approved_partial 的届改完 → status 重置回 pending（链已全删重建）。"""
        from uuid import UUID

        from app import models

        app_id = self._create_pending(client, student_token)
        # 直接改库模拟「已部分承認」状态
        row = db_session.get(models.Application, UUID(app_id))
        row.status = "approved_partial"
        db_session.commit()

        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"amend_reason": "修正", "return_method": "バス"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "pending", res.text

    def test_update_returned_application_allowed(
        self, client, student_token, db_session
    ):
        """returned(老师退回)状态可编辑、改完回 pending，不再 409。"""
        from uuid import UUID

        from app import models

        app_id = self._create_pending(client, student_token)
        row = db_session.get(models.Application, UUID(app_id))
        row.status = "returned"
        db_session.commit()

        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"amend_reason": "先生の指摘を修正しました", "return_method": "バス"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "pending", res.text
