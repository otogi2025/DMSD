"""在线学习申请 契約書（合同 = 网课报名凭证）上传 / 下载 endpoint tests — 2026-06-04 新增。

覆盖：
- POST /study/online-requests/{id}/contract — 学生上传合同（照片 / PDF）
- GET  /study/online-requests/{id}/contract — 本人 / 老师下载（含 R4 寮边界）
- GET  /students/{id}/profile               — 老师档案页含在线学习申请 + 合同信息

跑：
    cd dev/backend/v1
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
        # 带合法 PDF 文件头 → 先过 magic 校验，再触发大小上限（确保测的是「太大」而非「类型不符」）
        big = b"%PDF-1.4\n" + b"x" * (10 * 1024 * 1024 + 1)
        res = _upload(client, student_token, rid, name="big.pdf", body=big)
        assert res.status_code == 422
        assert res.json()["detail"]["code"] == "FILE_TOO_LARGE"

    def test_reject_magic_mismatch(self, client, student_token):
        """声明 image/jpeg 但内容是 PDF 字节 → 文件头 magic 校验拒绝（防伪造扩展名落盘成凭证）。"""
        rid = _create_request(client, student_token)
        res = _upload(
            client,
            student_token,
            rid,
            name="fake.jpg",
            body=PDF_BYTES,
            mime="image/jpeg",
        )
        assert res.status_code == 422, res.text
        assert res.json()["detail"]["code"] == "UNSUPPORTED_FILE_TYPE"

    def test_reject_pdf_magic_not_at_start(self, client, student_token):
        """%PDF- 藏在文件中段而非开头 → 拒绝（startswith 而非 contains，codex 复审逮到的绕过）。"""
        rid = _create_request(client, student_token)
        res = _upload(
            client,
            student_token,
            rid,
            name="evil.pdf",
            body=b"<html><!-- %PDF-1.4 --><script>x</script></html>",
            mime="application/pdf",
        )
        assert res.status_code == 422, res.text
        assert res.json()["detail"]["code"] == "UNSUPPORTED_FILE_TYPE"

    def test_upload_forces_extension_to_validated_type(self, client, student_token):
        """上传名 report.html 但内容是合法 PDF + 声明 pdf → 存盘文件名后缀强制 .pdf（不信原始后缀）。"""
        rid = _create_request(client, student_token)
        res = _upload(
            client,
            student_token,
            rid,
            name="report.html",
            body=PDF_BYTES,
            mime="application/pdf",
        )
        assert res.status_code == 200, res.text
        assert res.json()["contract_file_name"] == "report.pdf"

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
        # 安全头：阻止浏览器 MIME 嗅探 + 强制以附件下载（不内联渲染）
        assert res.headers.get("x-content-type-options") == "nosniff"
        assert "attachment" in res.headers.get("content-disposition", "")

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


class TestSubmitOverlap:
    """A-623（2026-06-15 修）：同一学生不允许提交与现有 pending/approved 申请时间段重叠的新申请。"""

    def test_overlap_same_period_rejected(self, client, student_token):
        # 第一份申请：第 5 天单日
        rid = _create_request(client, student_token, offset_days=5)
        assert rid
        # 第二份同一天 → 重叠 → 409
        pf = (date.today() + timedelta(days=5)).isoformat()
        res = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "重複期間",
                "period_from": pf,
                "period_to": pf,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 409, res.text
        assert res.json()["detail"]["code"] == "ONLINE_REQUEST_OVERLAP"

    def test_overlap_partial_range_rejected(self, client, student_token):
        # 第一份：第 5~8 天
        pf1 = (date.today() + timedelta(days=5)).isoformat()
        pt1 = (date.today() + timedelta(days=8)).isoformat()
        r1 = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "範囲1",
                "period_from": pf1,
                "period_to": pt1,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r1.status_code == 201, r1.text
        # 第二份：第 7~10 天，与第一份相交 → 409
        pf2 = (date.today() + timedelta(days=7)).isoformat()
        pt2 = (date.today() + timedelta(days=10)).isoformat()
        r2 = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "範囲2",
                "period_from": pf2,
                "period_to": pt2,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r2.status_code == 409, r2.text

    def test_non_overlap_allowed(self, client, student_token):
        # 第一份：第 5~8 天
        pf1 = (date.today() + timedelta(days=5)).isoformat()
        pt1 = (date.today() + timedelta(days=8)).isoformat()
        r1 = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "範囲1",
                "period_from": pf1,
                "period_to": pt1,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r1.status_code == 201, r1.text
        # 第二份：第 9~12 天，与第一份不相交 → 201 放行
        pf2 = (date.today() + timedelta(days=9)).isoformat()
        pt2 = (date.today() + timedelta(days=12)).isoformat()
        r2 = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "範囲2",
                "period_from": pf2,
                "period_to": pt2,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert r2.status_code == 201, r2.text

    def test_rejected_request_does_not_block(
        self, client, student_token, teacher_token
    ):
        # 第一份申请被老师 rejected 后，同期间再申请应放行（只有 pending/approved 才占用）
        rid = _create_request(client, student_token, offset_days=5)
        dec = client.post(
            f"/api/v1/study/online-requests/{rid}/decision",
            json={"decision": "rejected"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert dec.status_code == 200, dec.text
        pf = (date.today() + timedelta(days=5)).isoformat()
        res = client.post(
            "/api/v1/study/online-requests",
            json={
                "reason": "再申請",
                "period_from": pf,
                "period_to": pf,
                "weekly_schedule": {"月": [{"start": "19:40", "end": "21:00"}]},
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201, res.text


class TestDownloadOrphanStudent:
    """F-中-17（2026-06-15 修）：student 行被删（student_id 悬空）时，老师下载契約書必须 404，
    不能跳过演示/寮隔离校验直接放行文件（fail-closed）。"""

    def test_teacher_download_orphan_student_404(
        self, client, student_token, teacher_token, db_session, seed_data
    ):
        import uuid as _uuid

        rid = _create_request(client, student_token)
        _upload(client, student_token, rid)
        # 直接把这条申请的 student_id 改成不存在的 UUID（模拟 student 行被删 / 悬空）。
        # 先关外键约束再改，避免 SQLite 拒绝写入。
        from sqlalchemy import text

        db_session.execute(text("PRAGMA foreign_keys=OFF"))
        rec = db_session.get(models.StudyOnlineRequest, _uuid.UUID(rid))
        rec.student_id = _uuid.uuid4()
        db_session.commit()
        res = client.get(
            f"/api/v1/study/online-requests/{rid}/contract",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 404, res.text


class TestReuploadKeepsOldContract:
    """Q4 回归（codex 第一轮复审 2026-06-15）：已有合同时再传超大文件失败，旧合同必须完好
    （不被 open(,"wb") 截断、不被删）—— 改流式后写 .tmp + os.replace 原子替换保证。"""

    def test_reupload_too_large_keeps_old_contract(self, client, student_token):
        import glob
        import os

        rid = _create_request(client, student_token)
        # 1. 先成功传一份小 PDF
        r1 = _upload(client, student_token, rid, name="ok.pdf", body=PDF_BYTES)
        assert r1.status_code == 200, r1.text
        contracts_dir = os.path.join(get_settings().upload_dir, "contracts")
        matches = [
            m
            for m in glob.glob(os.path.join(contracts_dir, f"{rid}.*"))
            if not m.endswith(".tmp")
        ]
        assert len(matches) == 1, f"应有 1 份合同文件，实际 {matches}"
        old_abs = matches[0]
        with open(old_abs, "rb") as f:
            assert f.read() == PDF_BYTES

        # 2. 再传超大 → 422
        big = b"x" * (10 * 1024 * 1024 + 1)
        r2 = _upload(client, student_token, rid, name="big.pdf", body=big)
        assert r2.status_code == 422, r2.text

        # 3. 旧合同必须完好（没被截断、没被删）
        assert os.path.isfile(old_abs), "重传失败不应删旧合同"
        with open(old_abs, "rb") as f:
            assert f.read() == PDF_BYTES, "重传失败不应截断旧合同"
        # 不留 .tmp 残留
        assert not glob.glob(os.path.join(contracts_dir, "*.tmp")), (
            "失败后不应残留 .tmp"
        )
