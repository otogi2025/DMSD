"""学生自查视图端点测试（IX 系列 — iOS 个人主页假数据接真后端）。

覆盖：
- PATCH /api/v1/students/me      学生改自己的联系方式 / 房间号
- POST/GET /api/v1/rollcall/reports  点呼上报（体调/欠席/其他）+ 老师处理
- POST/GET /api/v1/songs             点歌（最小版）
- POST /api/v1/lost-found            遗失物投稿 + 本人 resolve
- POST/GET /api/v1/misc-requests     杂项申请 + 老师确认 / 学生撤回
"""

from __future__ import annotations

import uuid

from app import models, security


def _login_teacher(client, login_id):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["access_token"]


def _add_student(db, *, grade, klass, seat, name, gender, room, dorm, email=None):
    s = models.Student(
        grade_code=grade,
        class_code=klass,
        seat_no=seat,
        name=name,
        gender=gender,
        room_no=room,
        dorm_unit=dorm,
        is_overseas=False,
        email=email,
    )
    db.add(s)
    db.flush()
    db.add(
        models.Account(
            student_id=s.id,
            password_hash=security.hash_password("test-password-12345"),
        )
    )
    return s


# ---------------- PATCH /students/me（个人信息编辑）----------------


def test_update_profile_email_phone(client, seed_data, student_token):
    """改邮箱 + 电话成功，返回新值。"""
    res = client.patch(
        "/api/v1/students/me",
        json={"email": "newmail@test.jp", "phone": "090-1111-2222"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()["data"]
    assert body["email"] == "newmail@test.jp"
    assert body["phone"] == "090-1111-2222"


def test_update_profile_room_same_dorm(client, seed_data, student_token):
    """男寮学生（M101）改成同寮 M205 → 成功。"""
    res = client.patch(
        "/api/v1/students/me",
        json={"room_no": "M205"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"]["room_no"] == "M205"


def test_update_profile_room_cross_dorm_rejected(client, seed_data, student_token):
    """男寮学生想改成女寮 W*** → 422（防换到异性寮）。"""
    res = client.patch(
        "/api/v1/students/me",
        json={"room_no": "W301"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 422, res.text
    assert res.json()["error"]["code"] == "INVALID_ROOM_FORMAT"


def test_update_profile_email_taken(client, seed_data, student_token, db_session):
    """改成别人已用的邮箱 → 422。"""
    _add_student(
        db_session,
        grade="06",
        klass="02",
        seat="20",
        name="占用者",
        gender="male",
        room="M103",
        dorm=1,
        email="taken@test.jp",
    )
    db_session.commit()
    res = client.patch(
        "/api/v1/students/me",
        json={"email": "taken@test.jp"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 422, res.text
    assert res.json()["error"]["code"] == "EMAIL_TAKEN"


def test_update_profile_partial_keeps_others(client, seed_data, student_token):
    """PATCH 只动传了的字段 — 只传 phone，email（seed 原值）不变。"""
    res = client.patch(
        "/api/v1/students/me",
        json={"phone": "080-0000-0000"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()["data"]
    assert body["phone"] == "080-0000-0000"
    assert body["email"] == "ryu@test.jp"  # 没传 → 保持 seed 原值


def test_update_profile_requires_auth(client):
    """无 token → 401。"""
    res = client.patch("/api/v1/students/me", json={"phone": "1"})
    assert res.status_code == 401, res.text


# ---------------- 点呼上报 /rollcall/reports（体调/欠席/其他）----------------


def _add_report(db, *, student_id, kind="health", body="x"):
    r = models.RollCallReport(student_id=student_id, kind=kind, body=body)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_create_report_health(client, seed_data, student_token):
    """学生提交体调上报 → 201，初始未处理。"""
    res = client.post(
        "/api/v1/rollcall/reports",
        json={"kind": "health", "body": "頭痛がします"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 201, res.text
    body = res.json()["data"]
    assert body["kind"] == "health"
    assert body["body"] == "頭痛がします"
    assert body["resolved_at"] is None


def test_create_report_absence_and_other(client, seed_data, student_token):
    """欠席 / 其他两类都能提交。"""
    for kind in ("absence", "other"):
        res = client.post(
            "/api/v1/rollcall/reports",
            json={"kind": kind, "body": "テスト"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["data"]["kind"] == kind


def test_create_report_bad_kind_422(client, seed_data, student_token):
    """非法 kind → 422（schema 校验）。"""
    res = client.post(
        "/api/v1/rollcall/reports",
        json={"kind": "invalid", "body": "x"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 422, res.text


def test_create_report_bad_session_404(client, seed_data, student_token):
    """传了不存在的点呼场次 → 404。"""
    res = client.post(
        "/api/v1/rollcall/reports",
        json={"kind": "health", "body": "x", "session_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 404, res.text


def test_create_report_requires_auth(client):
    """无 token → 401。"""
    res = client.post("/api/v1/rollcall/reports", json={"kind": "health", "body": "x"})
    assert res.status_code == 401, res.text


def test_create_report_rejects_teacher(client, seed_data, teacher_token):
    """老师 token 调学生上报接口 → 403。"""
    res = client.post(
        "/api/v1/rollcall/reports",
        json={"kind": "health", "body": "x"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 403, res.text


def test_my_reports_returns_own(client, seed_data, student_token):
    """学生查自己提交过的上报。"""
    for i in range(2):
        client.post(
            "/api/v1/rollcall/reports",
            json={"kind": "other", "body": f"r{i}"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
    res = client.get(
        "/api/v1/rollcall/reports/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert len(res.json()["data"]) == 2


def test_teacher_list_reports_all_dorms(client, seed_data, db_session):
    """老师查上报列表 — 寮过滤已取消 2026-06-13：所有老师看全部寮的上报。"""
    me = seed_data["student"]  # dorm 1 男寮
    female = _add_student(
        db_session,
        grade="06",
        klass="03",
        seat="01",
        name="女子",
        gender="female",
        room="W101",
        dorm=4,
    )
    _add_report(db_session, student_id=me.id, body="男寮上报")
    _add_report(db_session, student_id=female.id, body="女寮上报")

    token = _login_teacher(client, "tannin")  # assigned_dorm=1 → 寮过滤取消后看全部
    res = client.get(
        "/api/v1/rollcall/reports",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    bodies = {r["body"] for r in res.json()["data"]}
    assert "男寮上报" in bodies
    assert "女寮上报" in bodies  # 寮过滤取消后女寮上报也可见

    token2 = _login_teacher(client, "ryomu_kachou")  # 跨寮役职
    res2 = client.get(
        "/api/v1/rollcall/reports",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert {"男寮上报", "女寮上报"} <= {r["body"] for r in res2.json()["data"]}


def test_teacher_list_reports_includes_student_summary(client, seed_data, db_session):
    """老师上报列表带学生摘要（姓名/学号/房号）— 老师认得出「谁上报」再处理。"""
    me = seed_data["student"]
    _add_report(db_session, student_id=me.id, body="体調不良の報告")
    token = _login_teacher(client, "ryomu_kachou")
    res = client.get(
        "/api/v1/rollcall/reports",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    row = next(r for r in res.json()["data"] if r["body"] == "体調不良の報告")
    assert row["student_name"] == me.name
    assert row["student_no"] == me.student_no
    assert row["room_no"] == me.room_no


def test_teacher_resolve_report(client, seed_data, db_session):
    """老师标记处理 → resolved_at 非空；重复处理 → 409。"""
    me = seed_data["student"]
    r = _add_report(db_session, student_id=me.id)
    token = _login_teacher(client, "ryomu_kachou")
    res = client.patch(
        f"/api/v1/rollcall/reports/{r.id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"]["resolved_at"] is not None
    res2 = client.patch(
        f"/api/v1/rollcall/reports/{r.id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 409, res2.text


def test_teacher_list_only_unresolved(client, seed_data, db_session):
    """only_unresolved=true 只返回还没处理的。"""
    me = seed_data["student"]
    _add_report(db_session, student_id=me.id, body="未処理")
    r2 = _add_report(db_session, student_id=me.id, body="処理済")
    token = _login_teacher(client, "ryomu_kachou")
    client.patch(
        f"/api/v1/rollcall/reports/{r2.id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get(
        "/api/v1/rollcall/reports?only_unresolved=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    bodies = {r["body"] for r in res.json()["data"]}
    assert "未処理" in bodies
    assert "処理済" not in bodies


# ---------------- 点歌 /songs（最小版）----------------


def test_create_song_request(client, seed_data, student_token):
    """学生投稿点歌 → 201，dorm_unit 自动取登录学生的寮。"""
    res = client.post(
        "/api/v1/songs",
        json={"song_title": "Lemon", "artist": "米津玄師"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 201, res.text
    body = res.json()["data"]
    assert body["song_title"] == "Lemon"
    assert body["dorm_unit"] == 1  # seed 学生是男寮


def test_list_songs_dorm_filter(client, seed_data, student_token, db_session):
    """dorm 参数按男/女寮过滤；不传看全部。"""
    me = seed_data["student"]  # dorm 1
    female = _add_student(
        db_session,
        grade="06",
        klass="03",
        seat="05",
        name="女",
        gender="female",
        room="W105",
        dorm=4,
    )
    db_session.add(
        models.SongRequest(student_id=me.id, dorm_unit=1, song_title="男寮曲")
    )
    db_session.add(
        models.SongRequest(student_id=female.id, dorm_unit=4, song_title="女寮曲")
    )
    db_session.commit()
    res = client.get(
        "/api/v1/songs?dorm=1", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 200, res.text
    titles = {s["song_title"] for s in res.json()["data"]}
    assert "男寮曲" in titles
    assert "女寮曲" not in titles
    res2 = client.get(
        "/api/v1/songs", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert {"男寮曲", "女寮曲"} <= {s["song_title"] for s in res2.json()["data"]}


def test_songs_teacher_can_view(client, seed_data, teacher_token):
    """老师也能看点歌一览。"""
    res = client.get(
        "/api/v1/songs", headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert res.status_code == 200, res.text


def test_create_song_requires_auth(client):
    """无 token → 401。"""
    res = client.post("/api/v1/songs", json={"song_title": "x"})
    assert res.status_code == 401, res.text


# ---------------- 遗失物投稿 /lost-found ----------------


def test_create_lost_found(client, seed_data, student_token):
    """学生发遗失物投稿 → 201，初始 open。"""
    res = client.post(
        "/api/v1/lost-found",
        json={"post_type": "found", "item_name": "傘", "location": "玄関"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["data"]["status"] == "open"


def test_lost_found_resolve_by_owner(client, seed_data, student_token):
    """投稿者标记已解决 → resolved；重复 → 409。"""
    res = client.post(
        "/api/v1/lost-found",
        json={"post_type": "lost", "item_name": "鍵"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    pid = res.json()["data"]["id"]
    res2 = client.patch(
        f"/api/v1/lost-found/{pid}/resolve",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res2.status_code == 200, res2.text
    assert res2.json()["data"]["status"] == "resolved"
    res3 = client.patch(
        f"/api/v1/lost-found/{pid}/resolve",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res3.status_code == 409, res3.text


def test_lost_found_resolve_rejects_non_owner(
    client, seed_data, student_token, db_session
):
    """非投稿者不能标记别人的投稿 → 403。"""
    other = _add_student(
        db_session,
        grade="06",
        klass="03",
        seat="06",
        name="他",
        gender="male",
        room="M106",
        dorm=1,
    )
    post = models.LostFoundPost(
        student_id=other.id, post_type="found", item_name="財布", status="open"
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    res = client.patch(
        f"/api/v1/lost-found/{post.id}/resolve",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 403, res.text


# ---------------- 杂项申请 /misc-requests ----------------


def test_create_misc_request_kinds(client, seed_data, student_token):
    """三类杂项申请都能提交。"""
    for kind in ("repair", "guest", "proxy_receipt"):
        res = client.post(
            "/api/v1/misc-requests",
            json={"kind": kind, "subject": "テスト"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["data"]["kind"] == kind
        assert res.json()["data"]["status"] == "pending"


def test_misc_request_mine(client, seed_data, student_token):
    """学生查自己的杂项申请。"""
    client.post(
        "/api/v1/misc-requests",
        json={"kind": "repair", "subject": "蛇口"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    res = client.get(
        "/api/v1/misc-requests/mine",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert len(res.json()["data"]) == 1


def test_misc_teacher_confirm(client, seed_data, student_token, db_session):
    """老师确认 → confirmed；重复确认 → 409。"""
    me = seed_data["student"]
    r = models.MiscRequest(
        student_id=me.id, kind="repair", subject="x", status="pending"
    )
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    token = _login_teacher(client, "ryomu_kachou")
    res = client.patch(
        f"/api/v1/misc-requests/{r.id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"]["status"] == "confirmed"
    res2 = client.patch(
        f"/api/v1/misc-requests/{r.id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 409, res2.text


def test_misc_student_withdraw(client, seed_data, student_token, db_session):
    """学生撤回自己的杂项申请 → withdrawn。"""
    me = seed_data["student"]
    r = models.MiscRequest(
        student_id=me.id, kind="guest", subject="友達", status="pending"
    )
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    res = client.patch(
        f"/api/v1/misc-requests/{r.id}/withdraw",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"]["status"] == "withdrawn"


def test_misc_teacher_all_dorms(client, seed_data, db_session):
    """老师列表 — 寮过滤已取消 2026-06-13：所有老师看全部寮。"""
    me = seed_data["student"]  # dorm 1
    female = _add_student(
        db_session,
        grade="06",
        klass="03",
        seat="07",
        name="女2",
        gender="female",
        room="W107",
        dorm=4,
    )
    db_session.add(
        models.MiscRequest(
            student_id=me.id, kind="repair", subject="男寮申请", status="pending"
        )
    )
    db_session.add(
        models.MiscRequest(
            student_id=female.id, kind="repair", subject="女寮申请", status="pending"
        )
    )
    db_session.commit()
    token = _login_teacher(client, "tannin")  # dorm 1 → 寮过滤取消后看全部
    res = client.get(
        "/api/v1/misc-requests", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    subjects = {r["subject"] for r in res.json()["data"]}
    assert "男寮申请" in subjects
    assert "女寮申请" in subjects  # 寮过滤取消后女寮申请也可见
