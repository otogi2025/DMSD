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

    def test_create_with_taxi_reservation(self, client, student_token):
        """带出租车预约时刻提出「帰省届」→ 201 + taxi_reservation_time 回显。"""
        body = _kisei_body()
        body["taxi_reservation_time"] = "18:30:00"
        res = client.post(
            "/api/v1/applications",
            json=body,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["taxi_reservation_time"] == "18:30:00"

    def test_create_without_taxi_defaults_null(self, client, student_token):
        """不带出租车预约 → taxi_reservation_time 为 null。"""
        res = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["taxi_reservation_time"] is None


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

    def test_update_records_amend_reason_in_audit(
        self, client, student_token, db_session
    ):
        """修改理由 amend_reason → 写进 audit payload，不覆盖申请本身的 reason。"""
        from uuid import UUID

        from app import models

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
        # amend_reason 不能覆盖申请本身的 reason（_kisei_body 设的 "帰省"）；真改的字段要写入
        db_session.expire_all()
        row = db_session.get(models.Application, UUID(app_id))
        assert row.reason == "帰省", f"reason 被 amend_reason 覆盖了: {row.reason}"
        assert row.return_method == "バス", row.return_method

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
        # 审批链已全删重建：所有 approval 行都是未决（decision=None）
        db_session.expire_all()
        approvals = (
            db_session.query(models.ApplicationApproval)
            .filter_by(application_id=UUID(app_id))
            .all()
        )
        assert approvals, "审批链为空（应重建）"
        assert all(a.decision is None for a in approvals), [
            a.decision for a in approvals
        ]

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

    def test_update_noop_rejected(self, client, student_token):
        """没有真实字段变化（只填 amend_reason）→ 422 NO_CHANGES，不重置审批链。"""
        app_id = self._create_pending(client, student_token)
        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"amend_reason": "理由だけ書いた"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["detail"]["code"] == "NO_CHANGES", res.text

    def test_audit_teacher_outside_dorm_forbidden(
        self, client, student_token, seed_data, db_session
    ):
        """非担当寮老师读 audit → 403（payload 含 amend_reason，不能任意老师读任意申请履历）。"""
        from app import models, security

        app_id = self._create_pending(client, student_token)
        # 造一个「女寮(unit4)担当、非跨寮 role」老师，对男寮(unit1)的 seed 学生应 403
        other = models.Teacher(
            login_id="onna_tannin",
            name="女寮担任",
            email="ot@test.jp",
            password_hash=security.hash_password("test-password-12345"),
            role="寮務一般教師",
            assigned_dorm=4,
        )
        db_session.add(other)
        db_session.commit()
        token = security.create_access_token(other.id, f"teacher:{other.role}")
        res = client.get(
            f"/api/v1/applications/{app_id}/audit",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403, res.text

    def test_audit_cross_dorm_teacher_allowed(
        self, client, student_token, teacher_token
    ):
        """跨寮 role 老师（寮務課長）读 audit → 200（确认范围检查没把正常老师也挡掉）。"""
        app_id = self._create_pending(client, student_token)
        res = client.get(
            f"/api/v1/applications/{app_id}/audit",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text

    def test_update_missing_amend_reason_rejected(self, client, student_token):
        """真改了字段但没填修改理由 → 422 AMEND_REASON_REQUIRED（后端兜底必填）。"""
        app_id = self._create_pending(client, student_token)
        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"return_method": "バス"},  # 改了字段、但没 amend_reason
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["detail"]["code"] == "AMEND_REASON_REQUIRED", res.text

    def test_update_same_field_value_noop(self, client, student_token, db_session):
        """传与现值相同的业务字段（+理由）→ 422 NO_CHANGES，已承认的审批行不被清。"""
        from uuid import UUID

        from app import models

        app_id = self._create_pending(client, student_token)
        uuid = UUID(app_id)
        # 给一个审批行打上「已承认」，验证 no-op 不会把链删掉重建
        appr = (
            db_session.query(models.ApplicationApproval)
            .filter_by(application_id=uuid)
            .first()
        )
        appr.decision = "approve"
        db_session.commit()
        appr_id = appr.id

        # return_method 传与 _kisei_body 相同的 "新幹線" = 没真改
        res = client.put(
            f"/api/v1/applications/{app_id}",
            json={"amend_reason": "理由", "return_method": "新幹線"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["detail"]["code"] == "NO_CHANGES", res.text
        # 同一审批行还在、decision 仍是 approve（没被删除重建）
        db_session.expire_all()
        appr2 = db_session.get(models.ApplicationApproval, appr_id)
        assert appr2 is not None and appr2.decision == "approve", appr2


class TestApprovalNotifiesStudent:
    """杭田 2026-06-04：审批走到终态后给提出者本人发邮件（template_key=application_decided）。

    部分通过（approved_partial）/ 审批中（pending）不通知，只在 approved / rejected 终态发。
    dev 环境没配 SENDGRID_API_KEY，不会真发，只在 notification_log 留一行。
    """

    def _create_pending(self, client, student_token) -> str:
        res = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        return res.json()["id"]

    def test_reject_notifies_submitter_by_email(
        self, client, student_token, teacher_token, db_session
    ):
        """却下（rejected）→ 给提出者本人发 application_decided 通知（日志 1 行、收件人=学生 email）。"""
        from app import models

        app_id = self._create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/approvals",
            json={"decision": "reject", "comment": "書類に不備があります"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "rejected", res.text

        logs = (
            db_session.query(models.NotificationLog)
            .filter_by(template_key="application_decided")
            .all()
        )
        assert len(logs) == 1, "审批结果通知日志应恰好 1 条"
        log = logs[0]
        assert log.channel == "email"
        assert log.target_type == "student"
        assert log.target_email == "ryu@test.jp"
        assert log.payload.get("result") == "rejected"

    def test_partial_approve_does_not_notify(
        self, client, student_token, teacher_token, db_session
    ):
        """部分通过（approved_partial）阶段不通知——只在终态发。"""
        from app import models

        app_id = self._create_pending(client, student_token)
        res = client.post(
            f"/api/v1/applications/{app_id}/approvals",
            json={"decision": "approve"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        st = res.json()["status"]
        logs = (
            db_session.query(models.NotificationLog)
            .filter_by(template_key="application_decided")
            .count()
        )
        # 留学生帰省审批链是多役职 → 单人 approve 仍是 approved_partial（通知 0 条）。
        # 万一链只有 1 役职就会直接 approved（通知 1 条）。两种都做一致校验。
        if st == "approved":
            assert logs == 1
        else:
            assert st == "approved_partial", res.text
            assert logs == 0, "途中段階で通知してはいけない"

    def test_full_approve_notifies_submitter(
        self, client, student_token, teacher_token, db_session
    ):
        """全役职 approve → approved → 给提出者本人发 application_decided 通知。"""
        from datetime import datetime, timezone
        from uuid import UUID

        from app import models

        app_id = self._create_pending(client, student_token)
        uuid = UUID(app_id)
        # 把 teacher_token（寮務課長）以外的 pending 审批行直接置 approve，凑出终态
        rows = (
            db_session.query(models.ApplicationApproval)
            .filter_by(application_id=uuid)
            .all()
        )
        for r in rows:
            if r.approver_role != "寮務課長":
                r.decision = "approve"
                r.decided_at = datetime.now(timezone.utc)
        db_session.commit()

        res = client.post(
            f"/api/v1/applications/{app_id}/approvals",
            json={"decision": "approve"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "approved", res.text

        logs = (
            db_session.query(models.NotificationLog)
            .filter_by(template_key="application_decided")
            .all()
        )
        assert len(logs) == 1, "全承認時に通知 1 行"
        assert logs[0].payload.get("result") == "approved"
        assert logs[0].target_email == "ryu@test.jp"


class TestActiveLeaves:
    """杭田 2026-06-04 四: GET /applications/active 出寮者一覧。

    只返 status='approved' 且 leave_date <= 指定日 <= return_date 的届；
    approved_partial / pending 不算；按 R4 寮边界过滤；纯只读无编辑接口。
    """

    def _approved_active(
        self, client, student_token, db_session, *, leave_delta=-1, return_delta=1
    ) -> str:
        """造一条 approved 且当天在出寮期间内的届（直接改库绕过「出寮日必须未来」校验）。"""
        from datetime import date, timedelta
        from uuid import UUID

        from app import models

        res = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        app_id = res.json()["id"]
        row = db_session.get(models.Application, UUID(app_id))
        row.status = "approved"
        row.leave_date = date.today() + timedelta(days=leave_delta)
        row.return_date = date.today() + timedelta(days=return_delta)
        db_session.commit()
        return app_id

    def test_active_lists_approved_in_range(
        self, client, student_token, teacher_token, db_session
    ):
        """approved + 今天在出寮期间内 → 出现在一覧。"""
        app_id = self._approved_active(client, student_token, db_session)
        res = client.get(
            "/api/v1/applications/active",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert app_id in [a["id"] for a in res.json()]

    def test_active_excludes_pending(
        self, client, student_token, teacher_token, db_session
    ):
        """pending（未审批）不出现在一覧。"""
        res0 = client.post(
            "/api/v1/applications",
            json=_kisei_body(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        pid = res0.json()["id"]
        res = client.get(
            "/api/v1/applications/active",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert pid not in [a["id"] for a in res.json()]

    def test_active_excludes_out_of_range(
        self, client, student_token, teacher_token, db_session
    ):
        """approved 但出寮日在未来（还没出寮）→ 不出现。"""
        app_id = self._approved_active(
            client, student_token, db_session, leave_delta=5, return_delta=8
        )
        res = client.get(
            "/api/v1/applications/active",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert app_id not in [a["id"] for a in res.json()]

    def test_active_dorm_boundary(self, client, student_token, db_session):
        """dorm4 担任老师看不到 dorm1 学生的出寮（R4 边界）。"""
        from app import models, security

        app_id = self._approved_active(client, student_token, db_session)
        other = models.Teacher(
            login_id="onna_t2",
            name="女寮担任2",
            email="ot2@test.jp",
            password_hash=security.hash_password("test-password-12345"),
            role="寮務一般教師",
            assigned_dorm=4,
        )
        db_session.add(other)
        db_session.commit()
        token = security.create_access_token(other.id, f"teacher:{other.role}")
        res = client.get(
            "/api/v1/applications/active",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        assert app_id not in [a["id"] for a in res.json()]

    def test_active_requires_teacher(self, client, student_token):
        """学生 token 不能看出寮者一覧。"""
        res = client.get(
            "/api/v1/applications/active",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code in (401, 403), res.text
