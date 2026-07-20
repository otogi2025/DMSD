"""投稿通報 + 老师删除投稿测试 — App Store UGC 治理（itsuki 2026-07-20 拍板 A 方案）。"""

from __future__ import annotations


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_song(client, student_token, title="テスト曲"):
    res = client.post(
        "/api/v1/songs",
        json={"song_title": title, "artist": "歌手", "note": "聴きたい"},
        headers=_auth(student_token),
    )
    assert res.status_code == 201
    return res.json()["data"]["id"]


def _create_lost(client, student_token):
    res = client.post(
        "/api/v1/lost-found",
        json={"post_type": "found", "item_name": "青い傘", "location": "玄関"},
        headers=_auth(student_token),
    )
    assert res.status_code == 201
    return res.json()["data"]["id"]


# ---------------- 通報 POST /reports ----------------


def test_report_song_and_idempotent(client, seed_data, student_token):
    song_id = _create_song(client, student_token)
    res = client.post(
        "/api/v1/reports",
        json={"content_type": "song", "content_id": song_id, "reason": "不適切"},
        headers=_auth(student_token),
    )
    assert res.status_code == 201
    first_id = res.json()["data"]["id"]
    assert res.json()["data"]["status"] == "open"
    # 同一学生重复通報同一投稿 → 幂等返回同一条记录，不堆重复行
    res2 = client.post(
        "/api/v1/reports",
        json={"content_type": "song", "content_id": song_id},
        headers=_auth(student_token),
    )
    assert res2.status_code == 201
    assert res2.json()["data"]["id"] == first_id


def test_report_nonexistent_target_404(client, seed_data, student_token):
    ghost = "00000000-0000-0000-0000-000000000099"
    for ctype in ("song", "announcement_reply", "lost_found"):
        res = client.post(
            "/api/v1/reports",
            json={"content_type": ctype, "content_id": ghost},
            headers=_auth(student_token),
        )
        assert res.status_code == 404, ctype


def test_report_invalid_type_422(client, seed_data, student_token):
    res = client.post(
        "/api/v1/reports",
        json={
            "content_type": "meal_review",
            "content_id": "00000000-0000-0000-0000-000000000001",
        },
        headers=_auth(student_token),
    )
    assert res.status_code == 422


# ---------------- 老师一覧 GET /reports + 处理 PATCH ----------------


def test_teacher_list_and_handle(client, seed_data, student_token, teacher_token):
    song_id = _create_song(client, student_token, title="一覧テスト曲")
    res = client.post(
        "/api/v1/reports",
        json={"content_type": "song", "content_id": song_id, "reason": "テスト"},
        headers=_auth(student_token),
    )
    report_id = res.json()["data"]["id"]

    # 学生不能看通報一覧（老师专用）
    res = client.get("/api/v1/reports", headers=_auth(student_token))
    assert res.status_code in (401, 403)

    res = client.get("/api/v1/reports?status=open", headers=_auth(teacher_token))
    assert res.status_code == 200
    mine = [r for r in res.json()["data"] if r["id"] == report_id]
    assert len(mine) == 1
    assert mine[0]["content_preview"] == "一覧テスト曲"

    # 老师标处理完；重复标 → 409
    res = client.patch(f"/api/v1/reports/{report_id}", headers=_auth(teacher_token))
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "handled"
    assert res.json()["data"]["handled_by_teacher_id"] is not None
    res = client.patch(f"/api/v1/reports/{report_id}", headers=_auth(teacher_token))
    assert res.status_code == 409


def test_list_reports_invalid_status_400(client, seed_data, teacher_token):
    res = client.get("/api/v1/reports?status=weird", headers=_auth(teacher_token))
    assert res.status_code == 400


# ---------------- 老师删除投稿 ----------------


def test_teacher_delete_song(client, seed_data, student_token, teacher_token):
    song_id = _create_song(client, student_token, title="削除対象曲")
    # 学生不能删
    res = client.delete(f"/api/v1/songs/{song_id}", headers=_auth(student_token))
    assert res.status_code in (401, 403)
    # 老师软删 → 204；一览不再出现；重复删 → 404
    res = client.delete(f"/api/v1/songs/{song_id}", headers=_auth(teacher_token))
    assert res.status_code == 204
    res = client.get("/api/v1/songs", headers=_auth(student_token))
    assert song_id not in [r["id"] for r in res.json()["data"]]
    res = client.delete(f"/api/v1/songs/{song_id}", headers=_auth(teacher_token))
    assert res.status_code == 404
    # 已删投稿不能再被通報
    res = client.post(
        "/api/v1/reports",
        json={"content_type": "song", "content_id": song_id},
        headers=_auth(student_token),
    )
    assert res.status_code == 404


def test_teacher_delete_lost_found(client, seed_data, student_token, teacher_token):
    post_id = _create_lost(client, student_token)
    res = client.delete(f"/api/v1/lost-found/{post_id}", headers=_auth(student_token))
    assert res.status_code in (401, 403)
    res = client.delete(f"/api/v1/lost-found/{post_id}", headers=_auth(teacher_token))
    assert res.status_code == 204
    res = client.get("/api/v1/lost-found", headers=_auth(student_token))
    assert post_id not in [r["id"] for r in res.json()["data"]]
    # 已删投稿投稿者也不能再标解决
    res = client.patch(
        f"/api/v1/lost-found/{post_id}/resolve", headers=_auth(student_token)
    )
    assert res.status_code == 404
