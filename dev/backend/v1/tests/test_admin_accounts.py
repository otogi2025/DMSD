"""学生账号管理 admin 端点测试。

覆盖：
- GET /api/v1/students（列表 / 过滤 / 权限）
- POST /api/v1/accounts/{id}/password-reset（成功 / 403 / 404）
- POST /api/v1/accounts/{id}/unlock（成功 / 403 / 404）
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app import models, security

# -----------------------------------------------------------------
# 通用 helpers
# -----------------------------------------------------------------
ADMIN_ROLE_TESTS = [
    ("寮務部長", "buchou_admin"),
    ("寮務課長", "kachou_admin"),
    ("管理係", "kanri_admin"),
]


@pytest.fixture
def admin_seed(db_session):
    """3 人の管理役职 + 学生 3 人（うち 1 人 is_demo）を作成。"""
    pw = security.hash_password("test-password-12345")

    # 管理役职 3 人
    teachers: dict[str, models.Teacher] = {}
    for role, login_id in ADMIN_ROLE_TESTS:
        t = models.Teacher(
            login_id=login_id,
            name=f"{role}先生",
            email=f"{login_id}@test.jp",
            password_hash=pw,
            role=role,
        )
        db_session.add(t)
        db_session.flush()
        teachers[login_id] = t

    # 権限なし教师
    no_perm = models.Teacher(
        login_id="no_perm",
        name="無権限先生",
        email="noperm@test.jp",
        password_hash=pw,
        role="寮監",
    )
    db_session.add(no_perm)
    db_session.flush()
    teachers["no_perm"] = no_perm

    # 学生 A（男寮 / active）
    student_a = models.Student(
        grade_code="06",
        class_code="01",
        seat_no="01",
        name="テスト 太郎",
        gender="male",
        room_no="M101",
        dorm_unit=1,
        status="active",
        is_demo=False,
    )
    db_session.add(student_a)
    db_session.flush()
    db_session.add(models.Account(student_id=student_a.id, password_hash=pw))

    # 学生 B（女寮 / active）
    student_b = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="02",
        name="テスト 花子",
        gender="female",
        room_no="W201",
        dorm_unit=4,
        status="active",
        is_demo=False,
    )
    db_session.add(student_b)
    db_session.flush()
    db_session.add(models.Account(student_id=student_b.id, password_hash=pw))

    # 学生 C（demo account — 一覧に出てはいけない）
    student_demo = models.Student(
        grade_code="99",
        class_code="99",
        seat_no="99",
        name="デモ ユーザ",
        gender="male",
        room_no="M999",
        dorm_unit=1,
        status="active",
        is_demo=True,
    )
    db_session.add(student_demo)
    db_session.flush()
    db_session.add(models.Account(student_id=student_demo.id, password_hash=pw))

    db_session.commit()
    return {
        "teachers": teachers,
        "student_a": student_a,
        "student_b": student_b,
        "student_demo": student_demo,
    }


def _teacher_token(client, login_id: str) -> str:
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


# -----------------------------------------------------------------
# GET /api/v1/students
# -----------------------------------------------------------------


class TestListStudents:
    def test_403_no_token(self, client, admin_seed):
        """未认证 → 401。"""
        res = client.get("/api/v1/students")
        assert res.status_code == 401

    def test_403_wrong_role(self, client, admin_seed):
        """寮監 → 学生名单可查看（200）。

        权限分级改造（teacher_permission_v1.md §5 第 12 行「学生账号管理」对 5 个权限组
        全部至少给查看 V）后，旧的「寮監连学生名单都看不了 → 403」行为被废弃。
        寮監 默认映射到「一般宿管+晚自习」操作组，对学生账号管理有 M（含 V）。
        """
        token = _teacher_token(client, "no_perm")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_200_returns_real_students_only(self, client, admin_seed):
        """管理係 → 200、is_demo 学生が含まれない、total が実学生数と一致。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        # demo 学生（student_demo）を除く 2 人だけ
        assert data["total"] == 2
        student_nos = [item["student_no"] for item in data["items"]]
        assert "999999" not in student_nos  # demo の学号は含まれない

    def test_200_buchou_allowed(self, client, admin_seed):
        """寮務部長 → 200（役职 gate 確認）。"""
        token = _teacher_token(client, "buchou_admin")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_200_kachou_allowed(self, client, admin_seed):
        """寮務課長 → 200（役职 gate 確認）。"""
        token = _teacher_token(client, "kachou_admin")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_filter_dorm_unit(self, client, admin_seed):
        """dorm_unit=4 → 女寮だけ返る。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students?dorm_unit=4",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["dorm_unit"] == 4

    def test_filter_q_by_name(self, client, admin_seed):
        """q=花子 → 名前マッチの学生だけ。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students?q=%E8%8A%B1%E5%AD%90",  # 花子
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert "花子" in data["items"][0]["name"]

    def test_filter_status(self, client, admin_seed):
        """status=active → active だけ返る。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students?status=active",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert all(item["status"] == "active" for item in data["items"])

    def test_response_fields(self, client, admin_seed):
        """レスポンスに必要フィールドが全部含まれること。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        item = res.json()["items"][0]
        for field in (
            "id",
            "student_no",
            "name",
            "room_no",
            "dorm_unit",
            "gender",
            "status",
            "is_locked",
        ):
            assert field in item, f"フィールド {field} がレスポンスに含まれない"

    def test_locked_flag_true_when_locked(self, client, admin_seed, db_session):
        """locked_until が将来 → is_locked=True。"""
        student_a = admin_seed["student_a"]
        # account を取得してロック状態にセット
        from sqlalchemy import select as sa_select

        acct = db_session.scalars(
            sa_select(models.Account).where(models.Account.student_id == student_a.id)
        ).first()
        acct.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session.commit()

        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        item = next(
            i for i in res.json()["items"] if i["student_no"] == student_a.student_no
        )
        assert item["is_locked"] is True


# -----------------------------------------------------------------
# POST /api/v1/accounts/{student_id}/password-reset
# -----------------------------------------------------------------


class TestPasswordReset:
    def test_403_no_token(self, client, admin_seed):
        sid = str(admin_seed["student_a"].id)
        res = client.post(f"/api/v1/accounts/{sid}/password-reset")
        assert res.status_code == 401

    def test_403_wrong_role(self, client, admin_seed):
        """寮監 → 可重置学生密码（200）。

        权限分级改造（teacher_permission_v1.md §5 第 12 行「学生账号管理」一般宿管系=M）后，
        旧的「寮監非账号管理角色 → 403」行为被废弃：寮監 默认映射到「一般宿管+晚自习」操作组，
        对学生账号管理有管理权 M。生产环境如需限制，给该账号显式指定「申請承認専用」组即可。
        """
        token = _teacher_token(client, "no_perm")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_404_student_not_found(self, client, admin_seed):
        """存在しない student_id → 404。"""
        import uuid

        token = _teacher_token(client, "kanri_admin")
        res = client.post(
            f"/api/v1/accounts/{uuid.uuid4()}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404

    def test_404_demo_student_excluded(self, client, admin_seed):
        """is_demo=True の学生 → 404（管理端点から見えない）。"""
        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_demo"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404

    def test_200_returns_temporary_password(self, client, admin_seed):
        """成功 → 200 + temporary_password が 16 桁英数字。"""
        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert "temporary_password" in data
        pw = data["temporary_password"]
        assert len(pw) == 16
        assert pw.isalnum()

    def test_password_reset_clears_lock(self, client, admin_seed, db_session):
        """パスワードリセット → locked_until / failed_count / lock_level がクリアされる。"""
        student_a = admin_seed["student_a"]
        from sqlalchemy import select as sa_select

        acct = db_session.scalars(
            sa_select(models.Account).where(models.Account.student_id == student_a.id)
        ).first()
        acct.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        acct.failed_count = 5
        acct.lock_level = 2
        db_session.commit()

        token = _teacher_token(client, "kanri_admin")
        sid = str(student_a.id)
        res = client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

        db_session.expire(acct)
        db_session.refresh(acct)
        assert acct.locked_until is None
        assert acct.failed_count == 0
        assert acct.lock_level == 0

    def test_password_changed_can_login(self, client, admin_seed):
        """パスワードリセット後 → 新しい仮 PW でログインできる。"""
        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )
        temp_pw = res.json()["temporary_password"]

        # 新 PW でログイン
        login_res = client.post(
            "/api/v1/sessions/student",
            json={
                "student_no": admin_seed["student_a"].student_no,
                "password": temp_pw,
            },
        )
        assert login_res.status_code == 200, login_res.text

    def test_audit_log_written(self, client, admin_seed, db_session):
        """audit_logs に account.password_reset が記録される。"""
        from sqlalchemy import select as sa_select

        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        client.post(
            f"/api/v1/accounts/{sid}/password-reset",
            headers={"Authorization": f"Bearer {token}"},
        )

        log = db_session.scalars(
            sa_select(models.AuditLog).where(
                models.AuditLog.action == "account.password_reset"
            )
        ).first()
        assert log is not None
        assert log.actor_type == "teacher"


# -----------------------------------------------------------------
# POST /api/v1/accounts/{student_id}/unlock
# -----------------------------------------------------------------


class TestUnlockAccount:
    def test_403_no_token(self, client, admin_seed):
        sid = str(admin_seed["student_a"].id)
        res = client.post(f"/api/v1/accounts/{sid}/unlock")
        assert res.status_code == 401

    def test_403_wrong_role(self, client, admin_seed):
        """寮監 → 可解锁学生账号（200）。

        同 password-reset：权限分级改造后旧「寮監非账号管理角色 → 403」废弃，
        寮監 默认映射到「一般宿管+晚自习」操作组，对学生账号管理有 M（teacher_permission_v1 §5 行 12）。
        """
        token = _teacher_token(client, "no_perm")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_404_student_not_found(self, client, admin_seed):
        import uuid

        token = _teacher_token(client, "kanri_admin")
        res = client.post(
            f"/api/v1/accounts/{uuid.uuid4()}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404

    def test_200_unlock_clears_lock_fields(self, client, admin_seed, db_session):
        """ロック中の学生 → unlock → locked_until / failed_count / lock_level がクリア。"""
        student_a = admin_seed["student_a"]
        from sqlalchemy import select as sa_select

        acct = db_session.scalars(
            sa_select(models.Account).where(models.Account.student_id == student_a.id)
        ).first()
        acct.locked_until = datetime.now(timezone.utc) + timedelta(hours=2)
        acct.failed_count = 5
        acct.lock_level = 1
        db_session.commit()

        token = _teacher_token(client, "kanri_admin")
        sid = str(student_a.id)
        res = client.post(
            f"/api/v1/accounts/{sid}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text

        db_session.expire(acct)
        db_session.refresh(acct)
        assert acct.locked_until is None
        assert acct.failed_count == 0
        assert acct.lock_level == 0

    def test_200_idempotent_on_unlocked_account(self, client, admin_seed):
        """すでにロックされていない学生でも unlock は 200 を返す（幂等）。"""
        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    def test_audit_log_written(self, client, admin_seed, db_session):
        """audit_logs に account.unlock が記録される。"""
        from sqlalchemy import select as sa_select

        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        client.post(
            f"/api/v1/accounts/{sid}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )

        log = db_session.scalars(
            sa_select(models.AuditLog).where(models.AuditLog.action == "account.unlock")
        ).first()
        assert log is not None
        assert log.actor_type == "teacher"

    def test_unlock_then_list_shows_not_locked(self, client, admin_seed, db_session):
        """unlock 後 → GET /students で is_locked=False になる。"""
        student_a = admin_seed["student_a"]
        from sqlalchemy import select as sa_select

        acct = db_session.scalars(
            sa_select(models.Account).where(models.Account.student_id == student_a.id)
        ).first()
        acct.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session.commit()

        token = _teacher_token(client, "kanri_admin")
        sid = str(student_a.id)
        client.post(
            f"/api/v1/accounts/{sid}/unlock",
            headers={"Authorization": f"Bearer {token}"},
        )

        res = client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {token}"},
        )
        item = next(
            i for i in res.json()["items"] if i["student_no"] == student_a.student_no
        )
        assert item["is_locked"] is False


# -----------------------------------------------------------------
# POST /api/v1/accounts/{id}/renew-seat — 老师兜底改番号
# A-527（2026-06-15 全维度审查）：在籍校验回归
# -----------------------------------------------------------------


class TestTeacherRenewSeat:
    def test_200_active_student_ok(self, client, admin_seed):
        """active 学生 → 改番号成功、needs_renewal 清零。"""
        token = _teacher_token(client, "kanri_admin")
        sid = str(admin_seed["student_a"].id)
        res = client.post(
            f"/api/v1/accounts/{sid}/renew-seat",
            headers={"Authorization": f"Bearer {token}"},
            json={"grade_code": "05", "class_code": "03", "seat_no": "07"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["grade_code"] == "05"
        assert data["class_code"] == "03"
        assert data["seat_no"] == "07"

    @pytest.mark.parametrize(
        "bad_status", ["graduated", "paused", "locked", "transferred"]
    )
    def test_409_non_active_student_rejected(
        self, client, admin_seed, db_session, bad_status
    ):
        """非 active（毕业 / 停用 / 锁定 / 転寮）学生 → 409 STUDENT_NOT_ACTIVE，番号不变。"""
        student_a = admin_seed["student_a"]
        orig_grade = student_a.grade_code
        orig_class = student_a.class_code
        orig_seat = student_a.seat_no
        # 直接改库把学生置成非在籍状态
        student_a.status = bad_status
        db_session.commit()

        token = _teacher_token(client, "kanri_admin")
        sid = str(student_a.id)
        res = client.post(
            f"/api/v1/accounts/{sid}/renew-seat",
            headers={"Authorization": f"Bearer {token}"},
            json={"grade_code": "05", "class_code": "03", "seat_no": "07"},
        )
        assert res.status_code == 409, res.text
        assert res.json()["detail"]["code"] == "STUDENT_NOT_ACTIVE"

        # 番号未被改动
        db_session.refresh(student_a)
        assert student_a.grade_code == orig_grade
        assert student_a.class_code == orig_class
        assert student_a.seat_no == orig_seat


# -----------------------------------------------------------------
# GET /api/v1/students 模糊搜 LIKE 通配符转义
# B-低-27（2026-06-15 全维度审查）
# -----------------------------------------------------------------


class TestListStudentsLikeEscape:
    def test_percent_in_q_is_literal_not_wildcard(self, client, admin_seed):
        """q 含 % → 当字面量处理，不匹配全部学生（转义生效）。"""
        token = _teacher_token(client, "kanri_admin")
        # admin_seed 有 2 个真实学生（太郎 / 花子），名字里都没有 % 字符
        res = client.get(
            "/api/v1/students",
            params={"q": "%"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        # 若 % 未转义会被当通配符匹配全部 → 转义后应 0 命中
        assert res.json()["total"] == 0

    def test_underscore_in_q_is_literal_not_wildcard(self, client, admin_seed):
        """q 含 _ → 当字面量处理，不匹配任意单字符（转义生效）。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students",
            params={"q": "_"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["total"] == 0

    def test_normal_q_still_matches(self, client, admin_seed):
        """普通查询（不含通配符）→ 转义后照常命中（不回归正常搜索）。"""
        token = _teacher_token(client, "kanri_admin")
        res = client.get(
            "/api/v1/students",
            params={"q": "花子"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["total"] == 1
        assert "花子" in data["items"][0]["name"]
