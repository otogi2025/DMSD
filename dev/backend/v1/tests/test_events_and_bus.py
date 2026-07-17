"""行事予定 + 巴士时刻表 CRUD 测试 (spec §7.5 / §7.6)。

覆盖：
- 行事予定: GET 列表 / POST 创建 / PATCH 编辑 / DELETE 删除 / 403 权限
- 巴士时刻表: GET 列表 / GET 详情 / POST 创建 / PATCH 编辑 / DELETE 停用 / 403 / 404
"""

from __future__ import annotations

import pytest


# -----------------------------------------------------------------------
# 辅助：获取有编辑权限的老师 token（寮務部長）
# -----------------------------------------------------------------------
@pytest.fixture
def edit_token(client, seed_data):
    """寮務部長 token — 有行事/巴士增删改权限。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryomu_buchou", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


@pytest.fixture
def readonly_token(client, seed_data):
    """寮務一般教師 token — 只有读权限（无增删改）。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "tannin", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


# -----------------------------------------------------------------------
# 行事予定 tests
# -----------------------------------------------------------------------
def _make_event(client, token, **kw):
    payload = {
        "title": "入学式",
        "category": "学校行事",
        "event_date": "2026-04-01",
    }
    payload.update(kw)
    res = client.post(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]
class TestDormEvents:
    def test_create_and_list(self, client, seed_data, edit_token):
        """创建行事予定 → 列表能查到。"""
        ev = _make_event(client, edit_token, title="始業式", event_date="2026-04-08")

        res = client.get(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["id"] == ev["id"]
        assert items[0]["title"] == "始業式"

    def test_list_date_filter(self, client, seed_data, edit_token):
        """日期范围过滤 — from_date / to_date。"""
        _make_event(client, edit_token, title="4 月行事", event_date="2026-04-01")
        _make_event(client, edit_token, title="5 月行事", event_date="2026-05-01")

        # 只查 4 月
        res = client.get(
            "/api/v1/events?from_date=2026-04-01&to_date=2026-04-30",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["title"] == "4 月行事"

    def test_patch_event(self, client, seed_data, edit_token):
        """PATCH 更新标题 + event_date。"""
        ev = _make_event(
            client, edit_token, title="旧タイトル", event_date="2026-04-01"
        )

        res = client.patch(
            f"/api/v1/events/{ev['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"title": "新タイトル", "event_date": "2026-04-10"},
        )
        assert res.status_code == 200
        body = res.json()["data"]
        assert body["title"] == "新タイトル"
        assert body["event_date"] == "2026-04-10"
        assert body["updated_at"] is not None

    def test_delete_event(self, client, seed_data, edit_token):
        """DELETE 后列表为空。"""
        ev = _make_event(client, edit_token)

        del_res = client.delete(
            f"/api/v1/events/{ev['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert del_res.status_code == 204

        items = client.get(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {edit_token}"},
        ).json()["data"]["items"]
        assert len(items) == 0

    def test_create_403_no_permission(self, client, seed_data, readonly_token):
        """一般教师 → 可创建行事（201）。

        权限分级改造（teacher_permission_v1.md §5 第 7 行「行事·活动」5 组全部 M）后，
        旧「一般教师不在编辑角色集 → 403」废弃：该功能簇人人可管。仅演示老师另被隔离闸拦截。
        """
        res = client.post(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {readonly_token}"},
            json={
                "title": "始業式",
                "category": "学校行事",
                "event_date": "2026-04-01",
            },
        )
        assert res.status_code == 201

    def test_patch_403_no_permission(
        self, client, seed_data, edit_token, readonly_token
    ):
        """一般教师 → 可编辑行事（200）。

        同 create：teacher_permission_v1.md §5 第 7 行「行事·活动」5 组全部 M，人人可管。
        """
        ev = _make_event(client, edit_token)
        res = client.patch(
            f"/api/v1/events/{ev['id']}",
            headers={"Authorization": f"Bearer {readonly_token}"},
            json={"title": "改名"},
        )
        assert res.status_code == 200

    def test_patch_404_not_found(self, client, seed_data, edit_token):
        """PATCH 不存在的 id → 404。"""
        import uuid

        res = client.patch(
            f"/api/v1/events/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"title": "不存在"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "EVENT_NOT_FOUND"

    def test_delete_404_not_found(self, client, seed_data, edit_token):
        """DELETE 不存在的 id → 404。"""
        import uuid

        res = client.delete(
            f"/api/v1/events/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 404

    def test_create_invalid_category(self, client, seed_data, edit_token):
        """非法 category → 400。"""
        res = client.post(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={
                "title": "テスト",
                "category": "不正カテゴリ",
                "event_date": "2026-04-01",
            },
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "INVALID_CATEGORY"

    def test_create_start_after_end_422(self, client, seed_data, edit_token):
        """开始时刻晚于结束时刻 → 422 INVALID_TIME_RANGE（A-575）。"""
        res = client.post(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={
                "title": "テスト",
                "category": "寮行事",
                "event_date": "2026-04-01",
                "start_at": "2026-04-01T18:00:00+09:00",
                "end_at": "2026-04-01T09:00:00+09:00",
            },
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "INVALID_TIME_RANGE"

    def test_create_start_equals_end_ok(self, client, seed_data, edit_token):
        """开始时刻等于结束时刻 → 允许（边界值，瞬时行事）。"""
        res = client.post(
            "/api/v1/events",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={
                "title": "テスト",
                "category": "寮行事",
                "event_date": "2026-04-01",
                "start_at": "2026-04-01T09:00:00+09:00",
                "end_at": "2026-04-01T09:00:00+09:00",
            },
        )
        assert res.status_code == 201, res.text

    def test_patch_start_after_end_422_merged(self, client, seed_data, edit_token):
        """PATCH 只改 start_at 使其晚于库里已有的 end_at → 422（合并值校验，A-575）。"""
        ev = _make_event(
            client,
            edit_token,
            start_at="2026-04-01T09:00:00+09:00",
            end_at="2026-04-01T12:00:00+09:00",
        )
        res = client.patch(
            f"/api/v1/events/{ev['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"start_at": "2026-04-01T18:00:00+09:00"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "INVALID_TIME_RANGE"

    def test_list_inverted_range_422(self, client, seed_data, edit_token):
        """from_date > to_date → 422 INVALID_DATE_RANGE，不静默返空（A-581）。"""
        res = client.get(
            "/api/v1/events?from_date=2026-05-01&to_date=2026-04-01",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 422, res.text
        assert res.json()["error"]["code"] == "INVALID_DATE_RANGE"


# -----------------------------------------------------------------------
# 巴士时刻表 tests
# -----------------------------------------------------------------------
def _make_bus(client, token, **kw):
    payload = {
        "kind": "daily_commute",
        "name": "朝便 6:50",
        "direction": "寮→駅",
        "schedule_at": "2026-05-30T06:50:00+09:00",
    }
    payload.update(kw)
    res = client.post(
        "/api/v1/bus/routes",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]
class TestBusRoutes:
    def test_create_and_list(self, client, seed_data, edit_token):
        """创建巴士便 → 列表能查到。"""
        bus = _make_bus(client, edit_token, name="夕方便 18:00", kind="dorm_special")

        res = client.get(
            "/api/v1/bus/routes",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["id"] == bus["id"]
        assert items[0]["deprecated"] is False

    def test_list_kind_filter(self, client, seed_data, edit_token):
        """kind 过滤 — daily_commute 只返回平日便。"""
        _make_bus(client, edit_token, name="平日便", kind="daily_commute")
        _make_bus(client, edit_token, name="特殊便", kind="dorm_special")

        res = client.get(
            "/api/v1/bus/routes?kind=daily_commute",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        items = res.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["kind"] == "daily_commute"

    def test_get_detail(self, client, seed_data, edit_token):
        """GET /bus/routes/{id} 返回单条详情。"""
        bus = _make_bus(client, edit_token)
        res = client.get(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["id"] == bus["id"]

    def test_patch_bus(self, client, seed_data, edit_token):
        """PATCH 更新名称 + note。"""
        bus = _make_bus(client, edit_token, name="旧名称")

        res = client.patch(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"name": "新名称", "note": "備考テキスト"},
        )
        assert res.status_code == 200
        body = res.json()["data"]
        assert body["name"] == "新名称"
        assert body["note"] == "備考テキスト"
        assert body["updated_at"] is not None

    def test_delete_marks_deprecated(self, client, seed_data, edit_token):
        """DELETE → deprecated=True（不物理删除），默认列表不再出现。"""
        bus = _make_bus(client, edit_token)

        del_res = client.delete(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert del_res.status_code == 204

        # 默认列表不出现
        items = client.get(
            "/api/v1/bus/routes",
            headers={"Authorization": f"Bearer {edit_token}"},
        ).json()["data"]["items"]
        assert len(items) == 0

        # include_deprecated=true 能看到
        items_all = client.get(
            "/api/v1/bus/routes?include_deprecated=true",
            headers={"Authorization": f"Bearer {edit_token}"},
        ).json()["data"]["items"]
        assert len(items_all) == 1
        assert items_all[0]["deprecated"] is True

    def test_create_403_no_permission(self, client, seed_data, readonly_token):
        """一般教师 → 可创建巴士便（201）。

        权限分级改造（teacher_permission_v1.md §5 第 6 行「巴士路线」5 组全部 M）后，
        旧「一般教师不在编辑角色集 → 403」废弃：该功能簇人人可管。仅演示老师另被隔离闸拦截。
        """
        res = client.post(
            "/api/v1/bus/routes",
            headers={"Authorization": f"Bearer {readonly_token}"},
            json={
                "kind": "daily_commute",
                "name": "朝便",
                "direction": "寮→駅",
                "schedule_at": "2026-05-30T06:50:00+09:00",
            },
        )
        assert res.status_code == 201

    def test_patch_403_no_permission(
        self, client, seed_data, edit_token, readonly_token
    ):
        """一般教师 → 可编辑巴士便（200）。

        同 create：teacher_permission_v1.md §5 第 6 行「巴士路线」5 组全部 M，人人可管。
        """
        bus = _make_bus(client, edit_token)
        res = client.patch(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {readonly_token}"},
            json={"name": "改名"},
        )
        assert res.status_code == 200

    def test_get_detail_404(self, client, seed_data, edit_token):
        """GET 不存在的 id → 404。"""
        import uuid

        res = client.get(
            f"/api/v1/bus/routes/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "BUS_ROUTE_NOT_FOUND"

    def test_patch_404_not_found(self, client, seed_data, edit_token):
        """PATCH 不存在的 id → 404。"""
        import uuid

        res = client.patch(
            f"/api/v1/bus/routes/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"name": "不存在"},
        )
        assert res.status_code == 404

    def test_delete_404_not_found(self, client, seed_data, edit_token):
        """DELETE 不存在的 id → 404。"""
        import uuid

        res = client.delete(
            f"/api/v1/bus/routes/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {edit_token}"},
        )
        assert res.status_code == 404

    def test_create_invalid_kind(self, client, seed_data, edit_token):
        """非法 kind → 400。"""
        res = client.post(
            "/api/v1/bus/routes",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={
                "kind": "invalid_kind",
                "name": "テスト",
                "direction": "寮→駅",
                "schedule_at": "2026-05-30T06:50:00+09:00",
            },
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "INVALID_KIND"

    def test_create_defaults_kind_and_name(self, client, seed_data, edit_token):
        """表单去掉「種別」「便名」后：只传 direction + schedule_at →
        kind 默认 dorm_special、name 用 direction 回填。
        """
        res = client.post(
            "/api/v1/bus/routes",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={
                "direction": "高校棟 → 岡山駅西口",
                "schedule_at": "2026-05-30T07:30:00+09:00",
            },
        )
        assert res.status_code == 201, res.text
        body = res.json()["data"]
        assert body["kind"] == "dorm_special"
        assert body["name"] == "高校棟 → 岡山駅西口"

    def test_purpose_roundtrip(self, client, seed_data, edit_token):
        """用途说明 purpose 在 create / get / patch 全程往返。"""
        bus = _make_bus(
            client,
            edit_token,
            purpose="帰国届を提出する場合の空港送迎便です。",
        )
        assert bus["purpose"] == "帰国届を提出する場合の空港送迎便です。"

        got = client.get(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
        ).json()["data"]
        assert got["purpose"] == "帰国届を提出する場合の空港送迎便です。"

        patched = client.patch(
            f"/api/v1/bus/routes/{bus['id']}",
            headers={"Authorization": f"Bearer {edit_token}"},
            json={"purpose": "買い物・帰省者向けの臨時便です。"},
        )
        assert patched.status_code == 200
        assert patched.json()["data"]["purpose"] == "買い物・帰省者向けの臨時便です。"
