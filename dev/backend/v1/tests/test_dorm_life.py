"""寮生活类申请端点冒烟测试 — B-低-18（2026-06-15 全维度审查）。

审查盘点发现 /api/v1/dorm-life 的 16 个端点此前无任何专属测试覆盖（间接覆盖也几乎没有）。
本文件给最核心的「寮生行事企画申請」流程补一条端到端冒烟：
  学生创建企划 → 学生查自己的列表 → 老师查 pending 列表 → 老师审批 → 状态落地。
覆盖 create / list-mine / list（老师）/ decision 4 个端点 + 鉴权（学生 vs 老师）。

跑：
    cd dev/backend/v1
    .venv/bin/python -m pytest tests/test_dorm_life.py -q
"""

from __future__ import annotations


def _proposal_payload() -> dict:
    return {
        "title": "寮祭の出し物",
        "held_at": "2026-09-01T18:00:00+09:00",
        "place": "食堂",
        "expected_count": 30,
        "target": "全寮生",
        "purpose": "交流",
        "content": "屋台と演奏",
        "risk_solution": "消火器を準備",
        "expected_cost": "1万円",
    }


class TestDormEventProposalFlow:
    def test_student_create_then_teacher_decide(
        self, client, student_token, teacher_token, seed_data
    ):
        """学生提企划 → 出现在自己列表 + 老师 pending 列表 → 老师批准 → result=approved。"""
        # 1. 学生创建
        res = client.post(
            "/api/v1/dorm-life/event-proposals",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        proposal = res.json()
        proposal_id = proposal["id"]
        assert proposal["result"] == "pending"
        assert proposal["title"] == "寮祭の出し物"

        # 2. 学生查自己的列表 — 能看到刚提的这条
        mine = client.get(
            "/api/v1/dorm-life/event-proposals/mine",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert mine.status_code == 200, mine.text
        assert any(p["id"] == proposal_id for p in mine.json())

        # 3. 老师查 pending 列表 — 也能看到
        pending = client.get(
            "/api/v1/dorm-life/event-proposals",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert pending.status_code == 200, pending.text
        assert any(p["id"] == proposal_id for p in pending.json())

        # 4. 老师审批通过
        decide = client.post(
            f"/api/v1/dorm-life/event-proposals/{proposal_id}/decision",
            json={"decision": "approved", "comment": "OK"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert decide.status_code == 200, decide.text
        assert decide.json()["result"] == "approved"

        # 5. 再审一次 → 已决定，409（原子条件更新挡住）
        again = client.post(
            f"/api/v1/dorm-life/event-proposals/{proposal_id}/decision",
            json={"decision": "rejected"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert again.status_code == 409, again.text

    def test_create_requires_student_token(self, client, teacher_token, seed_data):
        """老师令牌创建企划 → 403（该端点是学生专用 get_current_student）。"""
        res = client.post(
            "/api/v1/dorm-life/event-proposals",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 403, res.text

    def test_decide_nonexistent_404(self, client, teacher_token, seed_data):
        """审批不存在的企划 → 404。"""
        import uuid

        res = client.post(
            f"/api/v1/dorm-life/event-proposals/{uuid.uuid4()}/decision",
            json={"decision": "approved"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 404, res.text


class TestDormEventProposalResubmit:
    """C43（2026-06-17）：老师判定「再提出を求める(resubmit)」后，学生修正重提端点。"""

    def _create_and_set_resubmit(self, client, student_token, teacher_token) -> str:
        """造一个被老师判 resubmit 的企划，返回 id。"""
        res = client.post(
            "/api/v1/dorm-life/event-proposals",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        pid = res.json()["id"]
        dec = client.post(
            f"/api/v1/dorm-life/event-proposals/{pid}/decision",
            json={"decision": "resubmit", "comment": "予算の内訳を追記してください"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert dec.status_code == 200, dec.text
        assert dec.json()["result"] == "resubmit"
        return pid

    def test_resubmit_after_decision_back_to_pending(
        self, client, student_token, teacher_token, seed_data
    ):
        """resubmit 判定 → 学生改内容重提 → result 回 pending、决定字段清空、可再被审批。"""
        pid = self._create_and_set_resubmit(client, student_token, teacher_token)
        new_body = {
            **_proposal_payload(),
            "expected_cost": "2万円（内訳：飲食1万＋装飾1万）",
        }
        res = client.post(
            f"/api/v1/dorm-life/event-proposals/{pid}/resubmit",
            json=new_body,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["result"] == "pending"
        assert body["expected_cost"] == "2万円（内訳：飲食1万＋装飾1万）"
        assert body["decided_by"] is None
        assert body["decided_at"] is None
        # 重提后老师可再次审批
        dec2 = client.post(
            f"/api/v1/dorm-life/event-proposals/{pid}/decision",
            json={"decision": "approved"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert dec2.status_code == 200, dec2.text
        assert dec2.json()["result"] == "approved"

    def test_resubmit_pending_proposal_409(
        self, client, student_token, teacher_token, seed_data
    ):
        """未被要求重提（pending 审查中）的企划不能重提。"""
        res = client.post(
            "/api/v1/dorm-life/event-proposals",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        pid = res.json()["id"]
        r = client.post(
            f"/api/v1/dorm-life/event-proposals/{pid}/resubmit",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r.status_code == 409, r.text
        assert r.json()["detail"]["code"] == "CANNOT_RESUBMIT"

    def test_resubmit_requires_student_token(self, client, teacher_token, seed_data):
        """老师 token 不能调学生重提端点。"""
        import uuid

        res = client.post(
            f"/api/v1/dorm-life/event-proposals/{uuid.uuid4()}/resubmit",
            json=_proposal_payload(),
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code in (401, 403), res.text
