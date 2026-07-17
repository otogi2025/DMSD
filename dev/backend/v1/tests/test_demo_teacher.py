"""演示账号真隔离测试 — 2026-06-07 演示老师 is_demo 功能。

覆盖（teachers.is_demo + demo_scope_for_teacher 隔离）：
- 演示老师（is_demo=True）登录 → 学生列表只看演示学生，看不到真实学生
- 真老师（is_demo=False）登录 → 学生列表只看真实学生，看不到演示学生（行为同改造前）
- 演示老师对真实学生做写操作 → 404（演示老师只碰演示学生）
- 真老师对演示学生做写操作 → 404（行为同改造前：演示学生隐身）
- 演示老师对演示学生做写操作 → 成功（正向通路）

依赖 conftest.py 的 seed_data（真老师 6 + 真学生 1）+ client / teacher_token fixtures。
"""

from __future__ import annotations

import pytest

from app import models, security


@pytest.fixture
def demo_data(db_session, seed_data):
    """在 seed_data 真实数据之上追加：1 演示老师 + 1 演示学生（都 is_demo=True）。"""
    pw = security.hash_password("demo-pass-12345")

    demo_teacher = models.Teacher(
        login_id="demo",
        name="デモ教員",
        email="demo-teacher@test.jp",
        password_hash=pw,
        role="寮務部長",  # 跨寮 → 演示老师能看到所有演示寮的演示学生
        assigned_dorm=None,
        is_demo=True,
    )
    db_session.add(demo_teacher)
    db_session.flush()

    demo_student = models.Student(
        grade_code="98",
        class_code="01",
        seat_no="01",
        name="デモ一郎",
        name_kana="デモイチロウ",
        gender="male",
        category="一般寮生",
        room_no="D101",
        dorm_unit=1,
        is_overseas=False,
        email="demo-s1@test.jp",
        is_demo=True,
    )
    db_session.add(demo_student)
    db_session.flush()
    db_session.add(models.Account(student_id=demo_student.id, password_hash=pw))
    db_session.commit()

    return {"demo_teacher": demo_teacher, "demo_student": demo_student}


@pytest.fixture
def demo_teacher_token(client, demo_data):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "demo", "password": "demo-pass-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def test_demo_teacher_sees_only_demo_students(
    client, demo_teacher_token, demo_data, seed_data
):
    """演示老师登录 → 学生列表只含演示学生，不含真实学生。"""
    res = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text
    ids = {it["id"] for it in res.json()["data"]["items"]}
    assert str(demo_data["demo_student"].id) in ids  # 看到演示学生
    assert str(seed_data["student"].id) not in ids  # 看不到真实学生


def test_real_teacher_sees_only_real_students(
    client, teacher_token, demo_data, seed_data
):
    """真老师登录 → 学生列表只含真实学生，不含演示学生（行为同改造前）。"""
    res = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    ids = {it["id"] for it in res.json()["data"]["items"]}
    assert str(seed_data["student"].id) in ids  # 看到真实学生
    assert str(demo_data["demo_student"].id) not in ids  # 看不到演示学生


def test_demo_teacher_cannot_touch_real_student(client, demo_teacher_token, seed_data):
    """演示老师对真实学生做密码重置 → 404（演示老师只能碰演示学生）。"""
    res = client.post(
        f"/api/v1/accounts/{seed_data['student'].id}/password-reset",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_real_teacher_cannot_touch_demo_student(client, teacher_token, demo_data):
    """真老师对演示学生做密码重置 → 404（行为同改造前：演示学生隐身）。"""
    res = client.post(
        f"/api/v1/accounts/{demo_data['demo_student'].id}/password-reset",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_demo_teacher_can_reset_demo_student(client, demo_teacher_token, demo_data):
    """演示老师对演示学生做密码重置 → 成功（正向通路：演示老师能操作演示学生）。"""
    res = client.post(
        f"/api/v1/accounts/{demo_data['demo_student'].id}/password-reset",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert "temporary_password" in res.json()["data"]


def test_demo_teacher_cannot_view_real_student_profile(
    client, demo_teacher_token, seed_data
):
    """演示老师 GET 真实学生个人档案聚合 → 404（演示老师只能查演示学生）。"""
    res = client.get(
        f"/api/v1/students/{seed_data['student'].id}/profile",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 404, res.text


def test_real_teacher_cannot_view_demo_student_profile(
    client, teacher_token, demo_data
):
    """真老师 GET 演示学生个人档案聚合 → 404（演示学生对真老师隐身）。"""
    res = client.get(
        f"/api/v1/students/{demo_data['demo_student'].id}/profile",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 404, res.text


# ─────────────────────────────────────────────────────────────
# 全局端点演示隔离 — 演示老师禁碰「全局管理 / 写真实数据」端点（assert_not_demo_teacher → 403）
# 2026-06-08 codex 多视角复审挖出：演示账号默认启用 + 公开密码 demo123 后，这些全局端点
# （公告发 / 日程 / 巴士 / 测试邮件）原本漏的隔离从「需先攻破账号」变零成本可达。
# 这些表无 is_demo 列，只能靠 assert_not_demo_teacher 角色门拦（演示老师 is_demo=True → 403）。
# 注：注册码（current / history / refresh / close）2026-06-14 + 老师账号管理（列 / 招待 / 增 / 删）
#     2026-06-15，均 itsuki 拍板放开演示账号、已移出全局禁止集
#     —— 见 test_demo_teacher_can_read_registration_code / test_demo_teacher_can_list_teachers。
# ─────────────────────────────────────────────────────────────


def test_demo_teacher_can_list_teachers(client, demo_teacher_token):
    """2026-06-15 itsuki 拍板：演示账号可列真实老师目录（取消 assert_not_demo_teacher 闸）→ 不再 403。

    itsuki 在知情（演示账号将能枚举真实老师 login_id/email，且若在高权限组还能增删真实老师账号）
    的前提下选择放开，回退 6-08 演示隔离加固。
    """
    res = client.get(
        "/api/v1/teachers/",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text


def test_demo_teacher_can_read_registration_code(client, demo_teacher_token):
    """2026-06-14 itsuki 拍板：演示账号可读真实注册码（取消 assert_not_demo_teacher 闸）→ 不再 403。

    itsuki 在知情（演示老师能拿真码注册真实学生、破坏 is_demo 隔离）的前提下选择放开。
    body 可能为 null（当前无生效码），但绝非 403。
    """
    res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text


def test_demo_teacher_announcement_isolated_from_real(
    client, demo_teacher_token, teacher_token
):
    """公告补 is_demo 字段后，演示老师可发公告（不再一刀切 403），但发的是 is_demo=True 公告：
    演示老师自己 list 看得到、真老师 list 看不到（双向隔离，不污染真实学生）。"""
    # 演示老师发公告 → 201（发的是演示公告 is_demo=True）
    res = client.post(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={"title": "demo-only", "body": "b", "scope": "all"},
    )
    assert res.status_code == 201, res.text
    demo_ann_id = res.json()["data"]["id"]
    # 演示老师 list 看得到自己发的演示公告
    res = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert demo_ann_id in {a["id"] for a in res.json()["data"]["items"]}
    # 真老师 list 看不到这条演示公告（is_demo 隔离）
    res = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text
    assert demo_ann_id not in {a["id"] for a in res.json()["data"]["items"]}


def test_demo_teacher_cannot_create_event(client, demo_teacher_token):
    """演示老师建行事予定 → 403（行事无 is_demo、污染真实学生日程）。"""
    res = client.post(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={"title": "t", "category": "学校行事", "event_date": "2026-07-01"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["error"]["code"] == "DEMO_FORBIDDEN", res.text


def test_demo_teacher_cannot_create_bus_route(client, demo_teacher_token):
    """演示老师建巴士便 → 403（巴士无 is_demo、污染真实学生班次）。"""
    res = client.post(
        "/api/v1/bus/routes",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={
            "kind": "daily_commute",
            "name": "n",
            "direction": "登校",
            "schedule_at": "2026-07-01T08:00:00",
            "visible_to": "all",
        },
    )
    assert res.status_code == 403, res.text
    assert res.json()["error"]["code"] == "DEMO_FORBIDDEN", res.text


def test_demo_teacher_cannot_send_test_email(client, demo_teacher_token):
    """演示老师用真实发邮件通道 → 403（防滥发 / 钓鱼 / 耗配额）。"""
    res = client.post(
        "/api/v1/notifications/test",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={"to": "x@test.jp", "subject": "s", "body_text": "b"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["error"]["code"] == "DEMO_FORBIDDEN", res.text


def test_real_teacher_not_blocked_by_demo_guard(client, teacher_token):
    """回归：真老师（is_demo=False）调这些全局端点不被新演示 guard 误伤。"""
    # GET 老师目录 — 真老师寮務課長 200
    res = client.get(
        "/api/v1/teachers/", headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert res.status_code == 200, res.text
    # GET 当前注册码 — 真老师 200（可能 body 为 null，但绝非 403）
    res = client.get(
        "/api/v1/admin/registration-code/current",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text


def test_demo_teacher_cannot_reply_real_announcement(
    client, demo_teacher_token, teacher_token
):
    """演示老师回复真实公告 → 404（公告补 is_demo 后：真实公告对演示老师不可见，
    当作不存在，比旧 403 隔离更强 — 连存在性都不暴露）。"""
    # 真老师先发一个真实公告（is_demo=False）
    res = client.post(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "real", "body": "b", "scope": "all"},
    )
    assert res.status_code == 201, res.text
    ann_id = res.json()["data"]["id"]
    # 演示老师试图回复这个真实公告 → 404（看不见，当不存在）
    res = client.post(
        f"/api/v1/announcements/{ann_id}/replies",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={"body": "demo reply"},
    )
    assert res.status_code == 404, res.text
    assert res.json()["error"]["code"] == "NOT_FOUND", res.text


def test_demo_teacher_cannot_delete_real_reply(
    client, demo_teacher_token, teacher_token, student_token
):
    """演示老师删真实公告下的回复 → 404（is_demo 隔离：真实公告对演示老师不可见，
    连同其下回复一起当作不存在）。"""
    # 真老师发真实公告（is_demo=False）
    res = client.post(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "real", "body": "b", "scope": "all"},
    )
    assert res.status_code == 201, res.text
    ann_id = res.json()["data"]["id"]
    # 真学生回复，产生一条真实回复
    res = client.post(
        f"/api/v1/announcements/{ann_id}/replies",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"body": "real reply"},
    )
    assert res.status_code == 201, res.text
    reply_id = res.json()["data"]["id"]
    # 演示老师试图删这条真实回复 → 404（看不到真实公告，当不存在）
    res = client.delete(
        f"/api/v1/announcements/{ann_id}/replies/{reply_id}",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
    )
    assert res.status_code == 404, res.text
    assert res.json()["error"]["code"] == "NOT_FOUND", res.text


# ─────────────────────────────────────────────────────────────
# 前台无主条目 + 社区投稿（front_desk / songs / lost_found）演示隔离
# 2026-06-08 第 2 轮复审挖出：前台无主失物条目演示老师能写穿、社区投稿列表无 demo 过滤双向泄漏
# ─────────────────────────────────────────────────────────────


def test_demo_teacher_cannot_create_unowned_frontdesk_item(client, demo_teacher_token):
    """演示老师建无主失物条目（student_id 空）→ 403（否则污染真实老师前台板）。"""
    res = client.post(
        "/api/v1/front-desk",
        headers={"Authorization": f"Bearer {demo_teacher_token}"},
        json={"kind": "lost_and_found", "description": "傘", "location": "ロビー"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["error"]["code"] == "DEMO_FORBIDDEN", res.text


def test_demo_teacher_cannot_see_real_song_requests(
    client, student_token, demo_teacher_token
):
    """演示老师点歌一览看不到真实学生投稿（principal.is_demo 双向隔离）。"""
    res = client.post(
        "/api/v1/songs",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"song_title": "RealSong", "artist": "A", "note": "n"},
    )
    assert res.status_code == 201, res.text
    res = client.get(
        "/api/v1/songs", headers={"Authorization": f"Bearer {demo_teacher_token}"}
    )
    assert res.status_code == 200, res.text
    assert "RealSong" not in {s["song_title"] for s in res.json()["data"]}


def test_demo_teacher_cannot_see_real_lost_found(
    client, student_token, demo_teacher_token
):
    """演示老师遗失物一览看不到真实学生投稿。"""
    res = client.post(
        "/api/v1/lost-found",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "post_type": "lost",
            "item_name": "RealWallet",
            "description": "d",
            "location": "l",
        },
    )
    assert res.status_code == 201, res.text
    res = client.get(
        "/api/v1/lost-found", headers={"Authorization": f"Bearer {demo_teacher_token}"}
    )
    assert res.status_code == 200, res.text
    assert "RealWallet" not in {p["item_name"] for p in res.json()["data"]}
