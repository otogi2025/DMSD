"""在线学习申请 契約書（合同 = 网课报名凭证）上传 / 下载 endpoint tests — 2026-06-04 新增。

覆盖：
- POST /study/online-requests/{id}/contract — 学生上传合同（照片 / PDF）
- GET  /study/online-requests/{id}/contract — 本人 / 老师下载（含 R4 寮边界）
- GET  /students/{id}/profile               — 老师档案页含在线学习申请 + 合同信息

跑：
    cd 03_dev/backend/v1
    pytest tests/test_study_online.py -v
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app import models, security
from app.config import get_settings

PDF_BYTES = b"%PDF-1.4\n1 0 obj test contract\n%%EOF"
JPEG_BYTES = b"\xff\xd8\xff\xe0 fake jpeg body"


@pytest.fixture(autouse=True)
def _tmp_upload_dir(tmp_path):
    """每个测试用独立临时上传目录 — 不污染真实磁盘、测试间隔离。"""
    settings = get_settings()
    original = settings.upload_dir
    settings.upload_dir = str(tmp_path / "uploads")
    yield
    settings.upload_dir = original


def _create_request(client, token, offset_days=5):
    """造一条在线学习申请（必须 >= 开始 3 天前），返回它的 id。"""
    pf = (date.today() + timedelta(days=offset_days)).isoformat()
    res = client.post(
        "/api/v1/study/online-requests",
        json={
            "reason": "オンライン授業を受けるため",
            "period_from": pf,
            "period_to": pf,
            "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def _upload(
    client, token, rid, name="contract.pdf", body=PDF_BYTES, mime="application/pdf"
):
    return client.post(
        f"/api/v1/study/online-requests/{rid}/contract",
        files={"file": (name, body, mime)},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.fixture
def second_student_token(client, db_session, seed_data):
    """第二个学生（同寮）token — 测「非本人」拒绝。"""
    pw = security.hash_password("test-password-12345")
    s = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="19",
        name="テスト 二郎",
        gender="male",
        room_no="M102",
        dorm_unit=1,
        is_overseas=True,
        email="s2@test.jp",
    )
    db_session.add(s)
    db_session.flush()
    db_session.add(models.Account(student_id=s.id, password_hash=pw))
    db_session.commit()
    res = client.post(
        "/api/v1/sessions/student",
        json={"student_no": "060219", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def female_dorm_teacher_token(client, db_session, seed_data):
    """女寮（assigned_dorm=4）老师 token — 测寮边界：看不到男寮（dorm_unit=1）学生的合同。"""
    pw = security.hash_password("test-password-12345")
    t = models.Teacher(
        login_id="onna_sensei",
        name="女寮先生",
        email="onna@test.jp",
        password_hash=pw,
        role="寮務一般教師",
        assigned_dorm=4,
    )
    db_session.add(t)
    db_session.commit()
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": "onna_sensei", "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


class TestUploadContract:
    def test_requires_auth(self, client, student_token):
        rid = _create_request(client, student_token)
        res = client.post(
            f"/api/v1/study/online-requests/{rid}/contract",
            files={"file": ("c.pdf", PDF_BYTES, "application/pdf")},
        )
        assert res.status_code == 401

    def test_upload_pdf_success(self, client, student_token):
        rid = _create_request(client, student_token)
        res = _upload(client, student_token, rid)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["contract_file_name"] == "contract.pdf"
        assert data["contract_mime"] == "application/pdf"
        assert data["contract_size"] == len(PDF_BYTES)
        # 不暴露服务器物理路径
        assert "contract_file_path" not in data

    def test_upload_image_success(self, client, student_token):
        rid = _create_request(client, student_token)
        res = _upload(
            client,
            student_token,
            rid,
            name="photo.jpg",
            body=JPEG_BYTES,
            mime="image/jpeg",
        )
        assert res.status_code == 200, res.text
        assert res.json()["contract_mime"] == "image/jpeg"

    def test_reject_unsupported_type(self, client, student_token):
        rid = _create_request(client, student_token)
        res = _upload(
            client,
            student_token,
            rid,
            name="note.txt",
            body=b"hello",
            mime="text/plain",
        )
        assert res.status_code == 422

    def test_reject_empty(self, client, student_token):
        rid = _create_request(client, student_token)
        res = _upload(client, student_token, rid, body=b"")
        assert res.status_code == 422

    def test_reject_too_large(self, client, student_token):
        rid = _create_request(client, student_token)
        big = b"x" * (10 * 1024 * 1024 + 1)
        res = _upload(client, student_token, rid, name="big.pdf", body=big)
        assert res.status_code == 422

    def test_reject_not_owner(self, client, student_token, second_student_token):
        rid = _create_request(client, student_token)
        res = _upload(client, second_student_token, rid)
        assert res.status_code == 403

    def test_reject_after_decided(self, client, student_token, teacher_token):
        rid = _create_request(client, student_token)
        dec = client.post(
            f"/api/v1/study/online-requests/{rid}/decision",
            json={"decision": "approved"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert dec.status_code == 200, dec.text
        res = _upload(client, student_token, rid)
        assert res.status_code == 409

    def test_reupload_replaces(self, client, student_token):
        """重传换文件 — contract_size 更新成新文件大小。"""
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        res = _upload(
            client,
            student_token,
            rid,
            name="photo.jpg",
            body=JPEG_BYTES,
            mime="image/jpeg",
        )
        assert res.status_code == 200, res.text
        assert res.json()["contract_mime"] == "image/jpeg"
        assert res.json()["contract_size"] == len(JPEG_BYTES)


class TestDownloadContract:
    def test_owner_download(self, client, student_token):
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        assert res.content == PDF_BYTES

    def test_teacher_download(self, client, student_token, teacher_token):
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert res.content == PDF_BYTES

    def test_no_contract_404(self, client, student_token):
        rid = _create_request(client, student_token)
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 404

    def test_other_student_403(self, client, student_token, second_student_token):
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {second_student_token}"},
        )
        assert res.status_code == 403

    def test_cross_dorm_teacher_now_allowed(
        self, client, student_token, female_dorm_teacher_token
    ):
        """寮过滤已取消 2026-06-13：女寮老师下载男寮学生的契約書 → 现在允许。"""
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {female_dorm_teacher_token}"},
        )
        assert res.status_code == 200, res.text


class TestListCrossDorm:
    def test_cross_dorm_teacher_list_now_includes(
        self, client, student_token, teacher_token, female_dorm_teacher_token
    ):
        """寮过滤已取消 2026-06-13：女寮老师的待审列表现在也含男寮学生的申请。"""
        # 男寮（dorm_unit=1）学生提交一条 pending 申请
        rid = _create_request(client, student_token)
        # 本寮 / 全寮老师能在待审列表看到它
        res_ok = client.get(
            "/api/v1/study/online-requests",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res_ok.status_code == 200, res_ok.text
        assert any(r["id"] == rid for r in res_ok.json())
        # 女寮（assigned_dorm=4）老师现在也能看到男寮学生的申请
        res_block = client.get(
            "/api/v1/study/online-requests",
            headers={"Authorization": f"Bearer {female_dorm_teacher_token}"},
        )
        assert res_block.status_code == 200, res_block.text
        assert any(r["id"] == rid for r in res_block.json())


class TestProfileIncludesOnline:
    def test_profile_has_online_with_contract(
        self, client, student_token, teacher_token, seed_data
    ):
        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        sid = str(seed_data["student"].id)
        res = client.get(
            f"/api/v1/students/{sid}/profile",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert "study_online_requests" in data
        assert len(data["study_online_requests"]) == 1
        entry = data["study_online_requests"][0]
        assert entry["contract_file_name"] == "contract.pdf"
        assert entry["contract_mime"] == "application/pdf"
        assert entry["contract_size"] == len(PDF_BYTES)
