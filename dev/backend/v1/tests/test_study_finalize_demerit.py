"""自习结算（bulk-finalize）自动扣分链测试 — I2（2026-06-15 新增）。

覆盖 POST /api/v1/study/checkins/bulk-finalize 的缺席扣分写入逻辑：
- roster 内：到场者不建扣分，缺席者建 1 条 study_absent DemeritEvent（points=1.5）
- 重复 finalize 同一天 → 唯一约束幂等，不重复写扣分
- target_date 传未来日期 → 422 TARGET_DATE_FUTURE
- target_date 传 40 天前 → 422 TARGET_DATE_TOO_OLD

跑：
    cd dev/backend/v1
    pytest tests/test_study_finalize_demerit.py -v
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app import models
from app.routers.study import STUDY_ABSENT_POINTS, _academic_term


def _login_teacher(client, login_id: str) -> str:
    """辅助函数：老师登录拿 access_token。"""
    res = client.post(
        "/api/v1/sessions/teacher",
        json={"login_id": login_id, "password": "test-password-12345"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _add_to_roster(db_session, student, teacher) -> models.StudyRoster:
    """辅助函数：直接往 DB 写名簿记录，避免通过 HTTP 绕权限逻辑。"""
    today = date.today()
    term = _academic_term(today)
    roster = models.StudyRoster(
        student_id=student.id,
        academic_term=term,
        added_by=teacher.id,
    )
    db_session.add(roster)
    db_session.commit()
    return roster


def _mark_checkin_present(
    db_session, student, teacher, target_date: date
) -> models.StudyCheckin:
    """辅助函数：直接往 DB 写一条「已到场」StudyCheckin，模拟学生出席。"""
    checkin = models.StudyCheckin(
        student_id=student.id,
        target_date=target_date,
        status="present",
        recorded_by=teacher.id,
    )
    db_session.add(checkin)
    db_session.commit()
    db_session.refresh(checkin)
    return checkin


def _count_study_absent_events(db_session, student_id, target_date: date) -> int:
    """辅助函数：查指定学生在指定日期对应月份的 study_absent 扣分条数（含撤销的不计）。"""
    month = target_date.strftime("%Y-%m")
    rows = db_session.scalars(
        select(models.DemeritEvent).where(
            models.DemeritEvent.student_id == student_id,
            models.DemeritEvent.source_type == "study_absent",
            models.DemeritEvent.month == month,
            models.DemeritEvent.revoked_at.is_(None),
        )
    ).all()
    return len(rows)


@pytest.fixture
def study_teacher_token(client, seed_data):
    """寮務課長（ryomu_kachou）的 token — 对 C_STUDY 有 MANAGE 权限（GROUP_DORM_ADMIN）。"""
    return _login_teacher(client, "ryomu_kachou")


@pytest.fixture
def second_student(db_session, seed_data):
    """额外建一名真实学生（同寮），用于「1 到场 1 缺席」场景。"""
    from app import security

    pw = security.hash_password("test-password-12345")
    student = models.Student(
        grade_code="06",
        class_code="02",
        seat_no="19",
        name="テスト 二郎",
        gender="male",
        room_no="M102",
        dorm_unit=1,
        is_overseas=False,
        email="taro2@test.jp",
    )
    db_session.add(student)
    db_session.flush()
    db_session.add(models.Account(student_id=student.id, password_hash=pw))
    db_session.commit()
    return student


class TestBulkFinalizeBasic:
    """基本扣分链：1 到场 1 缺席场景。"""

    def test_absent_student_gets_demerit_present_does_not(
        self, client, db_session, seed_data, second_student, study_teacher_token
    ):
        """roster 内 1 到场 1 缺席：bulk-finalize 后只给缺席者建扣分，到场者不建。"""
        teacher = seed_data["teachers"]["ryomu_kachou"]
        student_present = seed_data["student"]  # 这名学生标记为「到场」
        student_absent = second_student  # 这名学生不签到 → 缺席

        # 两人都加入名簿
        _add_to_roster(db_session, student_present, teacher)
        _add_to_roster(db_session, student_absent, teacher)

        # 给「到场」那名学生写 present checkin
        today = date.today()
        _mark_checkin_present(db_session, student_present, teacher, today)

        # 执行 bulk-finalize（不传 target_date → 默认今天 JST）
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 200, res.text
        data = res.json()

        # 结算数应为 1（仅缺席者）
        assert data["finalized_count"] == 1

        # 缺席者：应该有 1 条 study_absent 扣分，点数 = STUDY_ABSENT_POINTS (1.5)
        absent_count = _count_study_absent_events(db_session, student_absent.id, today)
        assert absent_count == 1, "缺席者应有且仅有 1 条未撤销 study_absent 扣分"

        # 查点数
        month = today.strftime("%Y-%m")
        events_absent = db_session.scalars(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == student_absent.id,
                models.DemeritEvent.source_type == "study_absent",
                models.DemeritEvent.month == month,
                models.DemeritEvent.revoked_at.is_(None),
            )
        ).all()
        assert events_absent[0].points == STUDY_ABSENT_POINTS

        # 到场者：不应有任何 study_absent 扣分
        present_count = _count_study_absent_events(
            db_session, student_present.id, today
        )
        assert present_count == 0, "到场者不应建任何 study_absent 扣分"

    def test_finalize_sets_correct_source_event_id(
        self, client, db_session, seed_data, study_teacher_token
    ):
        """finalize 写的 DemeritEvent.source_event_id 应指向对应 StudyCheckin 的 id。"""
        teacher = seed_data["teachers"]["ryomu_kachou"]
        student = seed_data["student"]

        _add_to_roster(db_session, student, teacher)

        today = date.today()
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 200, res.text

        # 找到对应 StudyCheckin
        checkin = db_session.scalars(
            select(models.StudyCheckin).where(
                models.StudyCheckin.student_id == student.id,
                models.StudyCheckin.target_date == today,
            )
        ).first()
        assert checkin is not None, "finalize 应建 StudyCheckin 行"
        assert checkin.status == "absent"

        # 找到对应 DemeritEvent
        month = today.strftime("%Y-%m")
        event = db_session.scalars(
            select(models.DemeritEvent).where(
                models.DemeritEvent.student_id == student.id,
                models.DemeritEvent.source_type == "study_absent",
                models.DemeritEvent.month == month,
            )
        ).first()
        assert event is not None, "finalize 应建 DemeritEvent"
        # source_event_id 应指向刚才建的 StudyCheckin
        assert event.source_event_id == checkin.id


class TestBulkFinalizeIdempotency:
    """重复 finalize 同一天 → 唯一约束保证幂等，不重复扣分。"""

    def test_double_finalize_does_not_duplicate_demerit(
        self, client, db_session, seed_data, study_teacher_token
    ):
        """连续跑两次 bulk-finalize 同一天 → 缺席者仍只有 1 条 study_absent 扣分。"""
        teacher = seed_data["teachers"]["ryomu_kachou"]
        student = seed_data["student"]

        _add_to_roster(db_session, student, teacher)

        today = date.today()

        # 第一次 finalize
        res1 = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res1.status_code == 200, res1.text
        assert res1.json()["finalized_count"] == 1

        # 第二次 finalize（同一天）
        res2 = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res2.status_code == 200, res2.text
        # 第二次 finalized_count 应为 0（该生 absent checkin 已存在，不再算入 to_absent）
        assert res2.json()["finalized_count"] == 0

        # 整个 study_absent 扣分仍只有 1 条（唯一约束幂等）
        count = _count_study_absent_events(db_session, student.id, today)
        assert count == 1, "重复 finalize 后扣分条数应仍为 1，不重复写"


class TestBulkFinalizeDateValidation:
    """target_date 边界校验 — 未来 / 超过 30 天前 均应 422。"""

    def test_future_target_date_returns_422(
        self, client, seed_data, study_teacher_token
    ):
        """target_date 传明天（未来日期）→ 422，code=TARGET_DATE_FUTURE。"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={"target_date": tomorrow},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 422, res.text
        detail = res.json().get("detail", {})
        assert detail.get("code") == "TARGET_DATE_FUTURE"

    def test_target_date_40_days_ago_returns_422(
        self, client, seed_data, study_teacher_token
    ):
        """target_date 传 40 天前（超出 30 天窗口）→ 422，code=TARGET_DATE_TOO_OLD。"""
        old_date = (date.today() - timedelta(days=40)).isoformat()
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={"target_date": old_date},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 422, res.text
        detail = res.json().get("detail", {})
        assert detail.get("code") == "TARGET_DATE_TOO_OLD"

    def test_today_target_date_is_valid(self, client, seed_data, study_teacher_token):
        """target_date 传今天 → 不报 422（合法边界值）。"""
        today = date.today().isoformat()
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={"target_date": today},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        # 今天是合法日期，应 200（roster 空时 finalized_count=0 也是 200）
        assert res.status_code == 200, res.text

    def test_30_days_ago_is_valid(self, client, seed_data, study_teacher_token):
        """target_date 传恰好 30 天前 → 不报 422（边界内）。"""
        boundary = (date.today() - timedelta(days=30)).isoformat()
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={"target_date": boundary},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 200, res.text


# ---------------------------------------------------------------
# demo 隔离测试 — 注：seed_data 中没有 is_demo=True 的老师，
# 需要构造演示老师才能测。bulk-finalize 对 is_demo=True 的老师
# 直接返回 403 DEMO_READONLY（study.py 第 389 行），不走到学生过滤。
# 这里只测「演示老师被拒绝」这一行为（不测演示学生隔离逻辑，
# 因为 seed_data 没有演示学生，构造成本过高）。
# ---------------------------------------------------------------
class TestBulkFinalizeDemoIsolation:
    """演示账号访问 bulk-finalize → 403 DEMO_READONLY。"""

    def test_demo_teacher_cannot_finalize(self, client, db_session, seed_data):
        """is_demo=True 的老师调 bulk-finalize → 403。"""
        from app import security

        pw = security.hash_password("test-password-12345")

        # 建一个 is_demo=True 的演示老师
        demo_teacher = models.Teacher(
            login_id="demo_teacher_test",
            name="演示老師",
            email="demo@test.jp",
            password_hash=pw,
            role="寮務課長",  # 职位映射到 GROUP_DORM_ADMIN → C_STUDY MANAGE
            is_demo=True,
        )
        db_session.add(demo_teacher)
        db_session.commit()

        # 登录拿 token
        res_login = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "demo_teacher_test", "password": "test-password-12345"},
        )
        assert res_login.status_code == 200, res_login.text
        demo_token = res_login.json()["access_token"]

        # 调 bulk-finalize → 应 403
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {demo_token}"},
        )
        assert res.status_code == 403, res.text
        detail = res.json().get("detail", {})
        assert detail.get("code") == "DEMO_READONLY"


class TestPatchCheckinReabsentRevives:
    """Q2 回归（codex 第一轮复审 2026-06-15）：缺席→出席→再缺席，扣分必须复活，
    不能被旧软删行还占着的唯一键挡掉导致漏扣。"""

    def test_absent_present_absent_revives_demerit(
        self, client, db_session, seed_data, study_teacher_token
    ):
        teacher = seed_data["teachers"]["ryomu_kachou"]
        student = seed_data["student"]
        today = date.today()
        _add_to_roster(db_session, student, teacher)

        # 1. finalize → 学生缺席 → 1 条 study_absent 扣分
        res = client.post(
            "/api/v1/study/checkins/bulk-finalize",
            json={},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert _count_study_absent_events(db_session, student.id, today) == 1

        # 取该生今天的 absent checkin
        checkin = db_session.scalar(
            select(models.StudyCheckin).where(
                models.StudyCheckin.student_id == student.id,
                models.StudyCheckin.target_date == today,
            )
        )
        assert checkin is not None and checkin.status == "absent"
        cid = str(checkin.id)

        # 2. 改成 present → 撤销扣分（count 归 0）
        r2 = client.patch(
            f"/api/v1/study/checkins/{cid}",
            json={"status": "present", "override_reason": "出席確認"},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert r2.status_code == 200, r2.text
        db_session.expire_all()
        assert _count_study_absent_events(db_session, student.id, today) == 0

        # 3. 再改回 absent → 扣分必须复活（不能漏）
        r3 = client.patch(
            f"/api/v1/study/checkins/{cid}",
            json={"status": "absent", "override_reason": "やはり欠席"},
            headers={"Authorization": f"Bearer {study_teacher_token}"},
        )
        assert r3.status_code == 200, r3.text
        db_session.expire_all()
        assert _count_study_absent_events(db_session, student.id, today) == 1, (
            "再缺席应复活扣分(不能被旧软删行的唯一键挡掉漏扣)"
        )
