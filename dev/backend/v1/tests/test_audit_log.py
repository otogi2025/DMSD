"""操作履历审计（老师操作记录页）测试 — 中间件自动埋点 + 读取端点权限 / 演示隔离。

覆盖：
- 单元：路径归一化（id 段 → {id}）+ 敏感字段脱敏（密码 / 令牌 → ***）。
- 中间件：老师写操作(POST)被记 / GET 不记 / 登录(/sessions)不记。
- 读取端点：管理角色可看(200) / 非管理角色 403 / 演示隔离(demo 只看 demo) / total 计数。
"""

from __future__ import annotations

from app import models, security
from app.audit import _normalize_path, _sanitize


# ---------------------------------------------------------------
# 单元：路径归一化 + 脱敏
# ---------------------------------------------------------------
def test_normalize_path():
    assert _normalize_path("/api/v1/notifications/read-all") == "notifications/read-all"
    uid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert (
        _normalize_path(f"/api/v1/discipline/{uid}/revoke") == "discipline/{id}/revoke"
    )
    assert _normalize_path("/api/v1/events/123") == "events/{id}"


def test_sanitize_strips_sensitive():
    out = _sanitize(
        {"login_id": "x", "password": "secret123", "nested": {"token": "abc"}}
    )
    assert out["login_id"] == "x"
    assert out["password"] == "***"
    assert out["nested"]["token"] == "***"


# ---------------------------------------------------------------
# helper
# ---------------------------------------------------------------
def _login(client, login_id, password="test-password-12345"):
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _make_demo_teacher(db_session):
    t = models.Teacher(
        login_id="demo_audit",
        name="デモ監査",
        email="demo-audit@test.jp",
        password_hash=security.hash_password("demo-pass-12345"),
        role="寮務部長",
        assigned_dorm=None,
        is_demo=True,
    )
    db_session.add(t)
    db_session.flush()
    return t


def _insert_log(db_session, actor_id, action):
    db_session.add(
        models.AuditLog(
            actor_type="teacher",
            actor_id=actor_id,
            action=action,
            target_type=None,
            target_id=None,
            payload={"method": "POST"},
        )
    )


# ---------------------------------------------------------------
# 中间件：写操作被记 / 读操作不记
# ---------------------------------------------------------------
def test_teacher_mutation_is_logged(client, seed_data, teacher_token):
    # 写操作：POST /notifications/read-all（任意老师、无 body、200）
    res = client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200, res.text

    # ryomu_kachou(寮管理者) 是管理角色 → 能查操作记录，应看到刚才的 read-all
    logs = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert logs.status_code == 200, logs.text
    data = logs.json()
    entry = next(
        (e for e in data["items"] if e["action"] == "POST notifications/read-all"),
        None,
    )
    assert entry is not None, data["items"]
    assert entry["actor_name"] == seed_data["teachers"]["ryomu_kachou"].name
    assert entry["actor_type"] == "teacher"
    assert entry["payload"]["status"] == 200


def test_get_and_login_not_logged(client, seed_data, teacher_token):
    # 只做 GET（登录已在 fixture 里 POST /sessions）→ 操作记录应为空（GET / 登录都不记）
    r = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r.status_code == 200
    logs = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert logs.json()["total"] == 0


# ---------------------------------------------------------------
# 读取端点：权限闸
# ---------------------------------------------------------------
def test_non_admin_cannot_view(client, seed_data):
    # 国際交流部長 → 申請承認専用 组 → 无 C_AUDIT_LOG → 403
    token = _login(client, "kokukou_buchou")
    res = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403, res.text


def test_admin_can_view(client, seed_data, teacher_token):
    res = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 200


# ---------------------------------------------------------------
# 读取端点：演示隔离（演示老师只看演示老师的操作）
# ---------------------------------------------------------------
def test_demo_isolation(client, seed_data, db_session):
    real = seed_data["teachers"]["ryomu_kachou"]
    demo = _make_demo_teacher(db_session)
    _insert_log(db_session, real.id, "POST discipline/manual")  # 真老师操作
    _insert_log(db_session, demo.id, "POST cleaning")  # 演示老师操作
    db_session.commit()

    real_token = _login(client, "ryomu_kachou")
    demo_token = _login(client, "demo_audit", "demo-pass-12345")

    real_actions = {
        e["action"]
        for e in client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {real_token}"},
        ).json()["items"]
    }
    assert "POST discipline/manual" in real_actions
    assert "POST cleaning" not in real_actions  # 真老师看不到演示老师操作

    demo_actions = {
        e["action"]
        for e in client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {demo_token}"},
        ).json()["items"]
    }
    assert "POST cleaning" in demo_actions
    assert "POST discipline/manual" not in demo_actions  # 演示老师看不到真老师操作
