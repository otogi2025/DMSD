"""扣分排名 / 外出禁止（宵禁）门槛测试 — I1（2026-06-15 新增）。

覆盖 GET /api/v1/discipline/ranking 的 8.0 分外出禁止判定逻辑：
- is_curfew_threshold 准确标记（恰好 8.0 / 低于 8.0）
- revoked（已撤销）扣分不计入门槛
- curfew_threshold_count 计数正确

跑：
    cd dev/backend/v1
    pytest tests/test_discipline_curfew.py -v
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from app import models


# 日本时区常量（与 discipline.py 保持一致）
_JST = ZoneInfo("Asia/Tokyo")

# 测试月份：使用固定月份字符串，不随系统时间飘（避免跨月失效）
_TEST_MONTH = "2026-06"


def _login_teacher(client, login_id: str) -> str:
    """辅助函数：老师登录拿 token。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def _add_demerit(db_session, student, teacher, points: float) -> models.DemeritEvent:
    """辅助函数：直接往数据库写一条扣分记录（绕过 HTTP 接口，减少依赖）。"""
    event = models.DemeritEvent(
        student_id=student.id,
        source_type="manual",
        source_event_id=None,
        points=points,
        reason=f"测试扣分 {points} 分",
        month=_TEST_MONTH,
        created_by_teacher_id=teacher.id,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _get_ranking(client, token: str) -> dict:
    """辅助函数：调用 ranking 端点，返回解析后的 JSON。"""
    res = client.get(
        f"/api/v1/discipline/ranking?month={_TEST_MONTH}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]
def _find_entry(ranking_data: dict, student_id) -> dict | None:
    """在 ranking 结果的 entries 列表中按 student_id 找对应条目。"""
    sid_str = str(student_id)
    for entry in ranking_data["entries"]:
        if entry["student_id"] == sid_str:
            return entry
    return None


class TestCurfewThresholdFlag:
    """is_curfew_threshold 标记的判断逻辑。"""

    def test_exactly_8_points_triggers_curfew(self, client, db_session, seed_data):
        """累计恰好 8.0 分 → is_curfew_threshold 应为 True。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        # 写 2 条扣分：4.0 + 4.0 = 8.0
        _add_demerit(db_session, student, teacher, 4.0)
        _add_demerit(db_session, student, teacher, 4.0)

        token = _login_teacher(client, "ryomu_buchou")  # 寮務部長，有扣分查看权限
        data = _get_ranking(client, token)
        entry = _find_entry(data, student.id)

        assert entry is not None, "排名结果里应该能找到该学生"
        assert entry["total_points"] == 8.0
        assert entry["is_curfew_threshold"] is True

    def test_7_5_points_does_not_trigger_curfew(self, client, db_session, seed_data):
        """累计 7.5 分（< 8.0）→ is_curfew_threshold 应为 False。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        # 写 2 条：3.0 + 4.5 = 7.5
        _add_demerit(db_session, student, teacher, 3.0)
        _add_demerit(db_session, student, teacher, 4.5)

        token = _login_teacher(client, "ryomu_buchou")
        data = _get_ranking(client, token)
        entry = _find_entry(data, student.id)

        assert entry is not None, "排名结果里应该能找到该学生"
        assert entry["total_points"] == 7.5
        assert entry["is_curfew_threshold"] is False


class TestRevokedDemeritExclusion:
    """已撤销的扣分不计入 8 分门槛。"""

    def test_revoked_demerit_excluded_from_threshold(
        self, client, db_session, seed_data
    ):
        """写 9.0 分扣分，然后撤销 2.0 分那条，最终有效 7.0 分 → is_curfew_threshold=False。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        # 写 7.0 分（有效）
        _add_demerit(db_session, student, teacher, 7.0)
        # 写 2.0 分（随后撤销）
        event_to_revoke = _add_demerit(db_session, student, teacher, 2.0)

        # 直接在 DB 层标记撤销（模拟 POST /discipline/{id}/revoke 效果）
        event_to_revoke.revoked_at = datetime.now(timezone.utc)
        event_to_revoke.revoked_by_teacher_id = teacher.id
        event_to_revoke.revoke_reason = "测试撤销"
        db_session.commit()

        token = _login_teacher(client, "ryomu_buchou")
        data = _get_ranking(client, token)
        entry = _find_entry(data, student.id)

        assert entry is not None, "排名结果里应该能找到该学生"
        # 有效分 = 7.0（2.0 已撤销不计）
        assert entry["total_points"] == 7.0
        assert entry["is_curfew_threshold"] is False

    def test_revoked_makes_student_drop_below_threshold(
        self, client, db_session, seed_data
    ):
        """本来 8.5 分已过门槛，撤销 1.0 分后有效 7.5 分 → 从 True 变 False。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        # 7.5 分（有效）
        _add_demerit(db_session, student, teacher, 7.5)
        # 1.0 分（有效 + 随后撤销）
        event_to_revoke = _add_demerit(db_session, student, teacher, 1.0)

        # 先确认撤销前总分 8.5，is_curfew_threshold=True
        token = _login_teacher(client, "ryomu_buchou")
        data_before = _get_ranking(client, token)
        entry_before = _find_entry(data_before, student.id)
        assert entry_before is not None
        assert entry_before["total_points"] == 8.5
        assert entry_before["is_curfew_threshold"] is True

        # 撤销 1.0 分
        event_to_revoke.revoked_at = datetime.now(timezone.utc)
        event_to_revoke.revoked_by_teacher_id = teacher.id
        event_to_revoke.revoke_reason = "测试撤销"
        db_session.commit()

        # 撤销后有效 7.5 分 → False
        data_after = _get_ranking(client, token)
        entry_after = _find_entry(data_after, student.id)
        assert entry_after is not None
        assert entry_after["total_points"] == 7.5
        assert entry_after["is_curfew_threshold"] is False


class TestCurfewThresholdCount:
    """curfew_threshold_count 计数正确（多学生场景）。"""

    def test_curfew_count_with_single_student_above(
        self, client, db_session, seed_data
    ):
        """只有 1 名学生，且 >= 8 分 → curfew_threshold_count = 1。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        _add_demerit(db_session, student, teacher, 8.0)

        token = _login_teacher(client, "ryomu_buchou")
        data = _get_ranking(client, token)

        assert data["curfew_threshold_count"] == 1

    def test_curfew_count_with_no_student_above(self, client, db_session, seed_data):
        """所有学生均 < 8 分 → curfew_threshold_count = 0。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        _add_demerit(db_session, student, teacher, 3.0)

        token = _login_teacher(client, "ryomu_buchou")
        data = _get_ranking(client, token)

        assert data["curfew_threshold_count"] == 0

    def test_curfew_count_zero_when_all_demerits_revoked(
        self, client, db_session, seed_data
    ):
        """学生有 10 分但全部被撤销 → curfew_threshold_count = 0，total_points = 0。"""
        student = seed_data["student"]
        teacher = seed_data["teachers"]["ryomu_kachou"]

        event = _add_demerit(db_session, student, teacher, 10.0)

        # 撤销全部
        event.revoked_at = datetime.now(timezone.utc)
        event.revoked_by_teacher_id = teacher.id
        event.revoke_reason = "撤销全部"
        db_session.commit()

        token = _login_teacher(client, "ryomu_buchou")
        data = _get_ranking(client, token)

        assert data["curfew_threshold_count"] == 0
        entry = _find_entry(data, student.id)
        assert entry is not None
        assert entry["total_points"] == 0.0
        assert entry["is_curfew_threshold"] is False
