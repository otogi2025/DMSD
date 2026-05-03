"""老师公告 smoke 测试 — 覆盖核心路径。

API spec: system_features.md §7.15 + BACKEND announcements router。
覆盖：
- 老师发公告 → 学生在列表里看到（按 scope 过滤）
- 学生看详情 → 自动写已读
- 学生 / 老师都能发回复
- unread-count 正确算
- 软删后学生看不到
"""
from __future__ import annotations


def _post_announcement(client, teacher_token, scope="all", title="公告 1", body="内容"):
    res = client.post(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": title, "body": body, "scope": scope},
    )
    assert res.status_code == 201, res.text
    return res.json()


def test_post_and_list(client, seed_data, teacher_token, student_token):
    """老师发公告 → 学生列表能看到 + 未读 1 件。"""
    ann = _post_announcement(client, teacher_token, scope="all")

    list_res = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == ann["id"]
    assert items[0]["is_read"] is False

    unread = client.get(
        "/api/v1/announcements/unread-count",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()
    assert unread["unread_count"] == 1


def test_scope_filter_excludes_other_gender(
    client, seed_data, teacher_token, student_token
):
    """conftest 学生 = male → female scope 公告看不到。"""
    _post_announcement(client, teacher_token, scope="female", title="女寮限定")
    _post_announcement(client, teacher_token, scope="all", title="全员")

    items = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()["items"]
    titles = [it["title"] for it in items]
    assert "全员" in titles
    assert "女寮限定" not in titles  # scope 过滤生效


def test_detail_marks_read(client, seed_data, teacher_token, student_token):
    """学生打开详情 → 列表里 is_read 变 True + unread-count 减 1。"""
    ann = _post_announcement(client, teacher_token)

    client.get(
        f"/api/v1/announcements/{ann['id']}",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    items = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()["items"]
    assert items[0]["is_read"] is True

    unread = client.get(
        "/api/v1/announcements/unread-count",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()
    assert unread["unread_count"] == 0


def test_student_and_teacher_can_reply(
    client, seed_data, teacher_token, student_token
):
    """学生和老师都能发回复，全员都能看到。"""
    ann = _post_announcement(client, teacher_token)

    r1 = client.post(
        f"/api/v1/announcements/{ann['id']}/replies",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"body": "学生回复"},
    )
    assert r1.status_code == 201
    assert r1.json()["author_kind"] == "student"

    r2 = client.post(
        f"/api/v1/announcements/{ann['id']}/replies",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"body": "老师回复"},
    )
    assert r2.status_code == 201
    assert r2.json()["author_kind"] == "teacher"

    detail = client.get(
        f"/api/v1/announcements/{ann['id']}",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()
    assert len(detail["replies"]) == 2
    assert [r["body"] for r in detail["replies"]] == ["学生回复", "老师回复"]


def test_soft_delete_hides_from_list(
    client, seed_data, teacher_token, student_token
):
    """老师软删 → 学生列表里消失。"""
    ann = _post_announcement(client, teacher_token)

    del_res = client.delete(
        f"/api/v1/announcements/{ann['id']}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert del_res.status_code == 204

    items = client.get(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()["items"]
    assert len(items) == 0


def test_only_author_can_edit(client, seed_data, teacher_token):
    """v1.0 仅作者本人能编辑（其他老师 → 403）。"""
    # 用 ryomu_kachou (teacher_token) 发
    ann = _post_announcement(client, teacher_token, title="原标题")

    # 切到 ryomu_buchou login (= 不同老师)
    other_login = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "ryomu_buchou", "password": "test-password-12345"},
    )
    other_token = other_login.json()["access_token"]

    res = client.patch(
        f"/api/v1/announcements/{ann['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "改标题"},
    )
    assert res.status_code == 403
