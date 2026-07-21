"""出寮届 差戻(returned) + 撤回(withdrawn) 端点测试 — C42（2026-06-17 新增）。

覆盖：
- POST /applications/:id/withdraw — 学生本人撤回未确定的届
- POST /applications/:id/return    — 当前审批者把届差戻让学生重提
- 差戻后 decide_approval 被 APPLICATION_RETURNED 闸挡住
- 差戻后学生 PUT 重提 → status 回 pending

跑：
    cd dev/backend/v1
    pytest tests/test_application_return_withdraw.py -v
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from app import models

from tests.helpers_applications import _kisei_body


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_pending(client, student_token, offset: int = 3) -> str:
    res = client.post(
        "/api/v1/applications",
        json=_kisei_body(offset),
        headers=_auth(student_token),
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]["id"]


class TestWithdraw:
    """学生撤回 — pending / approved_partial / returned 可撤回，终态不可。"""

    def test_withdraw_pending_ok(self, client, student_token):
        app_id = _create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 200, res.text
        body = res.json()["data"]
        assert body["status"] == "withdrawn"
        assert body["withdrawn_at"] is not None

    def test_double_withdraw_409(self, client, student_token):
        app_id = _create_pending(client, student_token)
        client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        res = client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "CANNOT_WITHDRAW"

    def test_withdraw_returned_ok(self, client, student_token, teacher_token):
        """差戻中(returned)的届也可被学生撤回。"""
        app_id = _create_pending(client, student_token)
        r = client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "日程を見直してください"},
            headers=_auth(teacher_token),
        )
        assert r.status_code == 200, r.text
        res = client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "withdrawn"

    def test_withdraw_requires_auth(self, client, student_token):
        app_id = _create_pending(client, student_token)
        res = client.post(f"/api/v1/applications/{app_id}/withdraw")
        assert res.status_code in (401, 403), res.text

    def test_withdraw_approved_terminal_409(self, client, student_token, db_session):
        """approved（终态）届不能撤回 → 409。

        applications-2：撤回读取行已加 .with_for_update()（PG 行锁、SQLite no-op）。
        本测试走通「行锁查询 + selectinload(student) 组合」并落到终态守卫，
        既证明该查询组合不抛错、又覆盖 CANNOT_WITHDRAW 路径。
        """
        app_id = _create_pending(client, student_token)
        # 直接置终态 approved（绕过完整审批链）
        app = db_session.get(models.Application, UUID(app_id))
        app.status = "approved"
        db_session.commit()
        res = client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "CANNOT_WITHDRAW"


class TestReturn:
    """老师差戻 — 设 status=returned + 差戻理由进 audit；差戻后审批被挡、学生可重提。"""

    def test_teacher_return_sets_status_and_audit(
        self, client, student_token, teacher_token, db_session
    ):
        app_id = _create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "宿泊先の住所を追記してください"},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "returned"

        log = (
            db_session.query(models.AuditLog)
            .filter_by(action="application.return", target_id=UUID(app_id))
            .first()
        )
        assert log is not None, "差戻应写一条 application.return audit"
        assert log.payload.get("comment") == "宿泊先の住所を追記してください"

    def test_return_comment_required(self, client, student_token, teacher_token):
        app_id = _create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/return",
            json={},  # 缺 comment
            headers=_auth(teacher_token),
        )
        assert res.status_code == 422, res.text

    def test_return_requires_teacher(self, client, student_token):
        app_id = _create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "x"},
            headers=_auth(student_token),  # 学生无权差戻
        )
        assert res.status_code in (401, 403), res.text

    def test_return_then_decide_blocked(self, client, student_token, teacher_token):
        """差戻中的届不能被老师继续审批（APPLICATION_RETURNED）。"""
        app_id = _create_pending(client, student_token)
        client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "再確認"},
            headers=_auth(teacher_token),
        )
        res = client.post(
            f"/api/v1/applications/{app_id}/approvals",
            json={"decision": "approve"},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "APPLICATION_RETURNED"

    def test_return_then_student_resubmit_back_to_pending(
        self, client, student_token, teacher_token
    ):
        """差戻 → 学生 PUT 修改重提 → status 回 pending、审批链重建。"""
        app_id = _create_pending(client, student_token, offset=3)
        client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "出発日を変更してください"},
            headers=_auth(teacher_token),
        )
        # offset=3 的届 出寮=今+3 / 帰寮=今+5；改出寮到今+4（仍早于帰寮、且未来）。
        new_leave = (date.today() + timedelta(days=4)).isoformat()
        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"leave_date": new_leave, "amend_reason": "出発日を変更しました"},
            headers=_auth(student_token),
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] == "pending"

    def test_return_finalized_409(self, client, student_token, teacher_token):
        """已撤回(终态)的届不能差戻。"""
        app_id = _create_pending(client, student_token)
        client.post(
            f"/api/v1/applications/{app_id}/withdraw", headers=_auth(student_token)
        )
        res = client.post(
            f"/api/v1/applications/{app_id}/return",
            json={"comment": "x"},
            headers=_auth(teacher_token),
        )
        assert res.status_code == 409, res.text
        assert res.json()["error"]["code"] == "CANNOT_RETURN"
