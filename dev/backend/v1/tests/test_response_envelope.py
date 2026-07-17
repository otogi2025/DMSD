"""响应信封 {ok,data} 专项 —— 排除路径 / 204 / 失败壳 / 校验错误。"""

from __future__ import annotations


def test_healthz_not_enveloped(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body == {"status": "ok", "db": "ok"}
    assert "ok" not in body


def test_root_not_enveloped(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert "service" in body
    assert "ok" not in body


def test_success_enveloped(client, seed_data):
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": "060218", "password": "test-password-12345"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert "error" not in body
    assert "access_token" in body["data"]


def test_http_error_enveloped(client):
    res = client.get("/api/v1/students/me")
    assert res.status_code == 401
    body = res.json()
    assert body["ok"] is False
    assert "data" not in body
    assert body["error"]["code"]
    assert body["error"]["message"]


def test_validation_error_enveloped(client):
    res = client.post("/api/v1/sessions/teacher", json={})
    assert res.status_code == 422
    body = res.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INVALID_INPUT"
    assert "errors" in body["error"]["detail"]


def test_204_has_no_body(client, seed_data, teacher_token):
    """关闭注册码返回 204，无 body（中间件不得塞信封）。"""
    client.post(
        "/api/v1/admin/registration-code/refresh",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    res = client.post(
        "/api/v1/admin/registration-code/close",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert res.status_code == 204
    assert res.content == b""
