"""点呼 endpoint tests — C-050 (2026-05-21) 新增。

覆盖：
- POST /rollcall/sessions/:id/start — 教师开点呼
- POST /rollcall/sessions/:id/end — 教师结束
- POST /rollcall/sessions/:id/checkins — 学生 NFC / 手动签到
  - 幂等：相同 idempotency_key 不重复事件（A-011）
  - path_hint 校验（A-020）
- GET /rollcall/sessions/:id/board — 出席板
- GET /rollcall/today/sessions — 今日 session 列表

跑：
    cd dev/backend/v1
    pytest tests/test_rollcall.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app import models


@pytest.fixture
def rollcall_session(db_session, seed_data):
    """建一个 running 状态的点呼 session（dorm_unit=1，含 060218 学生）。"""
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    session = models.RollCallSession(
        dorm_unit_set=[1, 2],
        session_type="evening",
        day_type="weekday",
        session_status="running",
        started_at=now,
        scheduled_window_start_at=now - timedelta(minutes=5),
        scheduled_on_time_end_at=now + timedelta(minutes=10),
        scheduled_late_end_at=now + timedelta(minutes=20),
        scheduled_auto_end_at=now + timedelta(minutes=30),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def _make_running_session(db_session, *, on_time_offset_min: int):
    """建一个 running 场次，on_time 截止 = now + on_time_offset_min 分钟（负数 = 已过窗）。

    用于 ts_local 伪造测试：offset 负 → 服务器判定必然 late；offset 正 → present。
    """
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    session = models.RollCallSession(
        dorm_unit_set=[1, 2],
        session_type="evening",
        day_type="weekday",
        session_status="running",
        started_at=now,
        scheduled_window_start_at=now - timedelta(minutes=30),
        scheduled_on_time_end_at=now + timedelta(minutes=on_time_offset_min),
        scheduled_late_end_at=now + timedelta(minutes=on_time_offset_min + 20),
        scheduled_auto_end_at=now + timedelta(minutes=on_time_offset_min + 30),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def _parse_jst(iso: str) -> datetime:
    """把响应里的 checked_in_at ISO 串解析成 JST-aware datetime（读回若丢 tz 则补 JST）。"""
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Asia/Tokyo"))
    return dt


class TestCheckin:
    """POST /rollcall/sessions/:id/checkins"""

    def test_manual_checkin_creates_event(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """老师手动签到 → 创建 present 事件。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "manual_checkin",
                "path_hint": "manual",
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["student_id"] == student_id
        assert data["base_status"] == "present"
        assert data["status_source"] == "manual_checkin"

    def test_idempotency_same_key_returns_existing(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-011: 同 idempotency_key 第二次 POST 返回原事件（不创建新事件）。"""
        student_id = str(seed_data["student"].id)
        body = {
            "student_id": student_id,
            "idempotency_key": "test-key-001",
            "status_source": "auto_nfc",
            "path_hint": "B",
        }
        res1 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json=body,
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res1.status_code == 201
        event_id_1 = res1.json()["data"]["id"]

        # 第二次相同 key
        res2 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json=body,
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res2.status_code in (200, 201)
        assert res2.json()["data"]["id"] == event_id_1

    def test_idempotency_different_keys_same_student_reuse_row(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """B-中-19：同学生同 session、第二次换 idempotency_key —— 不再新建第二条事件。

        点呼 event 表对 (session_id, student_id) 是「1 学生 1 场次 1 行」幂等模型
        （models.RollCallEvent docstring + idx_rce_session_student），换 key 也应命中同一行，
        不能因为 key 不同就漏出第二条 present 事件。原幂等测试只覆盖「同 key 返回原事件」，
        没测「不同 key 不复用」这条更关键的去重路径。
        """
        student_id = str(seed_data["student"].id)
        res1 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "idempotency_key": "key-aaa",
                "status_source": "auto_nfc",
                "path_hint": "B",
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res1.status_code == 201, res1.text
        event_id_1 = res1.json()["data"]["id"]

        res2 = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "idempotency_key": "key-bbb",  # 换了 key
                "status_source": "auto_nfc",
                "path_hint": "B",
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res2.status_code in (200, 201), res2.text
        # 关键断言：同学生同场次仍只一行（命中既有事件，不因换 key 而复制）
        assert res2.json()["data"]["id"] == event_id_1, (
            "同学生同场次换 key 不应建出第二条事件"
        )

    def test_path_hint_a_requires_card_uid(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-020: path_hint=A 必须有 card_uid。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "auto_nfc",
                "path_hint": "A",
                # 故意缺 card_uid
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "PATH_HINT_MISMATCH"

    def test_path_hint_b_requires_idempotency_key(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """A-020: path_hint=B 必须有 idempotency_key。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "auto_nfc",
                "path_hint": "B",
                # 故意缺 idempotency_key
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "PATH_HINT_MISMATCH"

    def test_missing_identifier_returns_422(
        self, client, teacher_token, rollcall_session
    ):
        """既无 card_uid 也无 student_id → 422。"""
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={"status_source": "auto_nfc"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 422

    def test_forged_ts_local_earlier_in_window_cannot_escape_late(
        self, client, teacher_token, seed_data, db_session
    ):
        """7-06 拍板 server_now：伪造「早于真实、且落在旧容忍窗口内」的 ts_local 不能逃避迟到。

        场次 on_time 截止已过 3 分钟 → 服务器判定必为 late。客户端伪造 ts_local = 真实时刻前
        6 分钟（落在旧代码 [server_now-10min, +2min] 采纳窗内、且早于 on_time 截止）。旧逻辑会
        采纳该值判成 present（漏扣迟到）；改为恒取 server_now 后必须仍是 late，且 checked_in_at
        按服务器时间落库、不被伪造值带偏。
        """
        session = _make_running_session(db_session, on_time_offset_min=-3)
        student_id = str(seed_data["student"].id)
        server_ref = datetime.now(ZoneInfo("Asia/Tokyo"))
        forged = server_ref - timedelta(minutes=6)
        res = client.post(
            f"/api/v1/rollcall/sessions/{session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "manual_checkin",
                "path_hint": "manual",
                "ts_local": forged.isoformat(),
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        # 判定按服务器时间 → late（旧逻辑会被伪造成 present）
        assert data["base_status"] == "late", data
        # checked_in_at 贴服务器当前时刻，而非被伪造值（早 6 分钟）带偏
        checked_in = _parse_jst(data["checked_in_at"])
        assert abs((checked_in - server_ref).total_seconds()) < 120, checked_in
        assert abs((checked_in - forged).total_seconds()) > 120, checked_in

    def test_forged_ts_local_far_future_out_of_window_ignored(
        self, client, teacher_token, seed_data, db_session
    ):
        """7-06 拍板 server_now：伪造「晚于真实、且落在旧窗口外」的 ts_local 同样被忽略。

        场次 on_time 截止在 10 分钟后 → 服务器判定为 present。客户端伪造 ts_local = 真实时刻后
        1 天（远超旧代码 +2min 采纳上限）。结果必须仍按服务器时间：present，且 checked_in_at
        贴服务器当前时刻，绝不被写成未来的伪造值。
        """
        session = _make_running_session(db_session, on_time_offset_min=10)
        student_id = str(seed_data["student"].id)
        server_ref = datetime.now(ZoneInfo("Asia/Tokyo"))
        forged = server_ref + timedelta(days=1)
        res = client.post(
            f"/api/v1/rollcall/sessions/{session.id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "manual_checkin",
                "path_hint": "manual",
                "ts_local": forged.isoformat(),
            },
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        data = res.json()["data"]
        assert data["base_status"] == "present", data
        checked_in = _parse_jst(data["checked_in_at"])
        assert abs((checked_in - server_ref).total_seconds()) < 120, checked_in
        # 绝不被写成 1 天后的伪造未来时刻
        assert abs((checked_in - forged).total_seconds()) > 3600, checked_in


class TestSessionLifecycle:
    """start / end session"""

    def test_get_today_sessions_requires_teacher(self, client):
        """未带 token → 401。"""
        res = client.get("/api/v1/rollcall/today/sessions")
        assert res.status_code == 401

    def test_get_today_sessions_returns_list(self, client, teacher_token):
        """已带教师 token → 返回 list（即使为空）。"""
        res = client.get(
            "/api/v1/rollcall/today/sessions",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)


class TestBoard:
    """GET /rollcall/sessions/:id/board"""

    def test_board_excludes_demo_students(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """A-040 verify: is_demo=True 学生不进出席板。

        migtest-07: 真造一个 demo 学生验过滤 —— 旧版在无 demo 数据下断言恒真（假覆盖）。
        """
        # 造 demo 学生（dorm_unit=1 落在本 session 寮范围；座位 99 避开 seed 的 06/02/18）
        demo = models.Student(
            grade_code="06",
            class_code="02",
            seat_no="99",
            name="デモ太郎",
            gender="male",
            room_no="M199",
            dorm_unit=1,
            is_overseas=False,
            email="demo@test.jp",
            is_demo=True,
        )
        db_session.add(demo)
        db_session.commit()

        res = client.get(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/board",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200
        nos = {e.get("student_no") for e in res.json()["data"]["entries"]}
        # demo 学生（060299）必须被过滤掉
        assert demo.student_no not in nos, f"demo 学生未被过滤: {nos}"
        # 非 demo 的 seed 学生（060218）必须在板上 — 证明板非空、过滤没误杀正常学生
        assert seed_data["student"].student_no in nos, f"seed 学生不在板上: {nos}"

    def test_board_premarks_approved_outstay(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """杭田 2026-06-04 三-3/5: 有 approved 出寮願覆盖今天的学生，live 板预标 exempt_range。

        无点呼 event 也要显示成「外泊免除」，让寮監一眼看到不用管，不必等结算。
        """
        from datetime import date, datetime, time, timedelta, timezone

        sid = seed_data["student"].id
        today = date.today()
        app = models.Application(
            student_id=sid,
            kind="帰省",
            leave_date=today - timedelta(days=1),
            leave_method="新幹線",
            leave_time=time(19, 0),
            return_date=today + timedelta(days=1),
            return_method="新幹線",
            return_time=time(20, 0),
            status="approved",
            submitted_at=datetime.now(timezone.utc),
        )
        db_session.add(app)
        db_session.commit()

        res = client.get(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/board",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        entries = res.json()["data"]["entries"]
        mine = next(
            (e for e in entries if e["student_no"] == seed_data["student"].student_no),
            None,
        )
        assert mine is not None, entries
        assert mine["base_status"] == "exempt_range", mine


class TestNoEffectiveWindowShift:
    """A-022 b1 regression — 窗口永远固定 (effective_* 已删).

    防回滚：保证未来没人重新把窗口平移逻辑加回来。
    若任何代码引入 effective_window_start_at / effective_on_time_end_at /
    effective_late_end_at / effective_auto_end_at / effective_group / applied_group
    字段或概念 → 本测试 fail。

    itsuki 2026-05-21 拍板：点呼时间永远按 scheduled_* 算，老师提前按按钮
    只改 started_at 显示，不平移判定窗口。
    """

    def test_rollcall_event_has_no_applied_group_column(self, db_session):
        """ORM model 不应再有 applied_group 字段。"""
        cols = {c.key for c in models.RollCallEvent.__table__.columns}
        assert "applied_group" not in cols, (
            "applied_group 字段已在 A-022 (2026-05-21) 删除 — "
            "请勿再加回 ORM model（窗口平移概念已废弃）"
        )

    def test_rollcall_session_uses_scheduled_only(self, db_session):
        """RollCallSession 只能有 scheduled_*_at 4 字段，不应再有 effective_*_at。"""
        cols = {c.key for c in models.RollCallSession.__table__.columns}
        effective_cols = {
            "effective_window_start_at",
            "effective_on_time_end_at",
            "effective_late_end_at",
            "effective_auto_end_at",
        }
        intersection = cols & effective_cols
        assert not intersection, (
            f"窗口平移字段已在 A-022 (2026-05-21) 删除，禁止恢复: {intersection}"
        )
        # 同时 scheduled_*_at 4 字段必须存在（判定 / 结算 / 倒计时全靠它们）
        scheduled_cols = {
            "scheduled_window_start_at",
            "scheduled_on_time_end_at",
            "scheduled_late_end_at",
            "scheduled_auto_end_at",
        }
        assert scheduled_cols.issubset(cols), (
            f"scheduled_*_at 4 字段是判定基准，必须保留: 缺 {scheduled_cols - cols}"
        )


class TestPatchEvent:
    """PATCH /rollcall/events/{id} — 教师改判。

    Codex 5.5 审查补回归（此端点此前 0 覆盖）：
    - rollcall-07 终态门：ended 场次禁止改判
    - rollcall-07 no-op 门 + 防重复刷扣分：old_status 取「当前最新状态」，
      重复 PATCH 同一旧 event 到同状态会被挡（旧实现用被 PATCH 行的 base_status，挡不住）
    - 授权顺序：寮边界检查必须在终态探测之前（管辖外老师得 403，不泄露场次状态）
    """

    def _checkin(self, client, token, session_id, student_id):
        res = client.post(
            f"/api/v1/rollcall/sessions/{session_id}/checkins",
            json={
                "student_id": student_id,
                "status_source": "manual_checkin",
                "path_hint": "manual",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201, res.text
        return res.json()["data"]["id"]

    def test_override_present_to_late(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """改判 present→late 创建 override 行并返回 late。"""
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)
        res = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["data"]["base_status"] == "late"

    def test_repeat_patch_same_status_blocked(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """重复 PATCH 同一旧 event 到同状态 → 第二次 409 NO_OP_OVERRIDE（防累积刷扣分）。

        旧实现 old_status=被 PATCH 行的 base_status（恒为 present）→ 第二次仍 present→late 不算 no-op
        → 会再建 override + 再扣分。修复后 old_status 取最新状态（已是 late）→ 第二次被挡。
        """
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)
        res1 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res1.status_code == 200, res1.text
        # 再 PATCH 同一个旧 event_id 还是 →late：当前最新已是 late → no-op
        res2 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻2"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res2.status_code == 409, res2.text
        assert res2.json()["error"]["code"] == "NO_OP_OVERRIDE"

    def test_patch_ended_session_allowed(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """改判无时限（2026-07-17 拍板③）：session ended 后照样可改判，扣分联动照常。

        原「终态门：ended → 409 SESSION_ENDED」已删——结合拍板②「结束前一律迟到」，
        老师点完「点呼終了」后发现误判必须能当场更正，否则错误扣分进台账无法修正。
        """
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)
        sess = db_session.get(models.RollCallSession, rollcall_session.id)
        sess.session_status = "ended"
        db_session.commit()
        res = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 200, res.text
        # 扣分联动照常：present→late 记一条 0.5 有效扣分
        db_session.expire_all()
        active = (
            db_session.query(models.DemeritEvent)
            .filter(
                models.DemeritEvent.student_id == seed_data["student"].id,
                models.DemeritEvent.source_event_id == rollcall_session.id,
                models.DemeritEvent.revoked_at.is_(None),
            )
            .all()
        )
        assert len(active) == 1
        assert active[0].points == 0.5

    def test_cross_dorm_teacher_can_override_ended_session(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """寮过滤已取消 2026-06-13（7-17 拍板「分角色跨寮」第二波再收）：跨寮老师
        改判不被 FORBIDDEN_DORM 挡；结合 7-17 拍板③改判无时限，改已结束场次也成功。"""
        from app import security

        student_id = str(seed_data["student"].id)  # 学生 dorm_unit=1
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)

        # 建一个只管 4 栋（女寮）的老师 — 与学生（1 栋）不同寮，过去会被 FORBIDDEN_DORM 挡
        t4 = models.Teacher(
            login_id="ryomu4",
            name="女寮太郎",
            email="r4@test.jp",
            password_hash=security.hash_password("test-password-12345"),
            role="寮務一般教師",
            assigned_dorm=4,
        )
        db_session.add(t4)
        # 把 session 标 ended
        sess = db_session.get(models.RollCallSession, rollcall_session.id)
        sess.session_status = "ended"
        db_session.commit()

        login = client.post(
            "/api/v1/sessions/teacher",
            json={"login_id": "ryomu4", "password": "test-password-12345"},
        )
        assert login.status_code == 200, login.text
        token4 = login.json()["data"]["access_token"]

        res = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {token4}"},
        )
        assert res.status_code == 200, res.text

    def test_multistep_override_recomputes_demerit(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """改判扣分按当前状态重算：present→absent→late 后只剩 0.5 分（迟到），不累积也不全撤。

        旧实现负 delta 把整条扣分全撤，absent→late 会变 0 分（少扣）——本测试锁死修复。
        分值依 spec §862 冻结：迟到 0.5 / 缺席 1.0。
        """
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)

        # present → absent（扣 1.0）
        r1 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "absent", "reason": "欠席"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r1.status_code == 200, r1.text

        # absent → late（应把那条 1.0 撤掉、重记 0.5）
        r2 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r2.status_code == 200, r2.text

        db_session.expire_all()
        active = (
            db_session.query(models.DemeritEvent)
            .filter(
                models.DemeritEvent.student_id == seed_data["student"].id,
                models.DemeritEvent.source_event_id == rollcall_session.id,
                models.DemeritEvent.revoked_at.is_(None),
            )
            .all()
        )
        assert len(active) == 1, f"应只剩 1 条有效扣分，实际 {len(active)} 条"
        assert active[0].source_type == "rollcall_late"
        assert active[0].points == 0.5, f"迟到应扣 0.5，实际 {active[0].points}"

    def test_override_late_to_absent_reescalates_demerit(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """B-低-17：补全状态转移矩阵 —— present→late→absent 反方向（升级）也按当前状态重算。

        原矩阵只测了 absent→late（降级）一条。本测试锁死「先迟到 0.5、再改判缺席」时
        旧的 0.5 被撤掉、重记 1.0 缺席，最终只剩 1 条 1.0，不残留迟到的 0.5、不叠加。
        分值依 spec §862 冻结：迟到 0.5 / 缺席 1.0。
        """
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)

        # present → late（扣 0.5）
        r1 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "late", "reason": "遅刻"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r1.status_code == 200, r1.text

        # late → absent（应撤掉 0.5、重记 1.0）
        r2 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "absent", "reason": "欠席"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r2.status_code == 200, r2.text

        db_session.expire_all()
        active = (
            db_session.query(models.DemeritEvent)
            .filter(
                models.DemeritEvent.student_id == seed_data["student"].id,
                models.DemeritEvent.source_event_id == rollcall_session.id,
                models.DemeritEvent.revoked_at.is_(None),
            )
            .all()
        )
        assert len(active) == 1, f"应只剩 1 条有效扣分，实际 {len(active)} 条"
        assert active[0].source_type == "rollcall_absent"
        assert active[0].points == 1.0, f"缺席应扣 1.0，实际 {active[0].points}"

    def test_override_to_present_clears_demerit(
        self, client, teacher_token, seed_data, rollcall_session, db_session
    ):
        """B-低-17：absent→present（撤销迟到/缺席判定）应把扣分全撤，无残留有效扣分行。"""
        student_id = str(seed_data["student"].id)
        event_id = self._checkin(client, teacher_token, rollcall_session.id, student_id)

        # present → absent（扣 1.0）
        r1 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "absent", "reason": "欠席"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r1.status_code == 200, r1.text

        # absent → present（纠正回出席：扣分应全撤）
        r2 = client.patch(
            f"/api/v1/rollcall/events/{event_id}",
            json={"to_status": "present", "reason": "誤判訂正"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert r2.status_code == 200, r2.text

        db_session.expire_all()
        active = (
            db_session.query(models.DemeritEvent)
            .filter(
                models.DemeritEvent.student_id == seed_data["student"].id,
                models.DemeritEvent.source_event_id == rollcall_session.id,
                models.DemeritEvent.revoked_at.is_(None),
            )
            .all()
        )
        assert len(active) == 0, f"改判回出席后应无有效扣分，实际 {len(active)} 条"


class TestMyTodayRollCall:
    """GET /rollcall/me/today — 学生端今日自分点呼（R-1/R-2 iOS 真实显示数据源）。"""

    def test_requires_student_token(self, client, teacher_token, rollcall_session):
        """老师令牌访问 → 403（学生专用端点）。"""
        res = client.get(
            "/api/v1/rollcall/me/today",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 403, res.text

    def test_returns_my_dorm_session_unsigned(
        self, client, student_token, rollcall_session
    ):
        """我寮今日场次未签到 → 返回 1 条、my_status=None、四时间窗齐全。"""
        res = client.get(
            "/api/v1/rollcall/me/today",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()["data"]
        assert len(body) == 1, body
        row = body[0]
        assert row["session_id"] == str(rollcall_session.id)
        assert row["session_type"] == "evening"
        assert row["session_status"] == "running"
        assert row["my_status"] is None
        assert row["my_checked_in_at"] is None
        # 四个时间窗时刻都要有（iOS 算 idle/进行中/時間内/遅刻 全靠它）
        for key in (
            "scheduled_window_start_at",
            "scheduled_on_time_end_at",
            "scheduled_late_end_at",
            "scheduled_auto_end_at",
        ):
            assert row[key], f"{key} 缺失"

    def test_shows_my_status_after_checkin(
        self, client, db_session, student_token, seed_data, rollcall_session
    ):
        """已签到 → my_status / my_checked_in_at 返回真实判定。"""
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        db_session.add(
            models.RollCallEvent(
                session_id=rollcall_session.id,
                student_id=seed_data["student"].id,
                base_status="present",
                status_source="manual_checkin",
                checked_in_at=now,
            )
        )
        db_session.commit()
        res = client.get(
            "/api/v1/rollcall/me/today",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        row = res.json()["data"][0]
        assert row["my_status"] == "present"
        assert row["my_checked_in_at"] is not None

    def test_excludes_other_dorm_session(
        self, client, db_session, student_token, rollcall_session
    ):
        """女寮 [4] 今日场次不返回给一寮（dorm_unit=1）学生。"""
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        db_session.add(
            models.RollCallSession(
                dorm_unit_set=[4],
                session_type="evening",
                day_type="weekday",
                session_status="running",
                started_at=now,
                scheduled_window_start_at=now - timedelta(minutes=5),
                scheduled_on_time_end_at=now + timedelta(minutes=10),
                scheduled_late_end_at=now + timedelta(minutes=20),
                scheduled_auto_end_at=now + timedelta(minutes=30),
            )
        )
        db_session.commit()
        res = client.get(
            "/api/v1/rollcall/me/today",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()["data"]
        # 只返回我寮（[1,2]）那条，不含女寮 [4]
        assert len(body) == 1, body
        assert body[0]["session_id"] == str(rollcall_session.id)


class TestRealCheckinPartialUnique:
    """审查 backend#1：uq_rce_real_checkin 部分唯一索引行为。"""

    def test_double_real_checkin_blocked_by_db(
        self, db_session, seed_data, rollcall_session
    ):
        """同生同场第二条真实签到行（无 idempotency_key）被 DB 层挡住。

        路径 A / 手动代签 idempotency_key 恒 NULL，uq_rce_idempotency 挡不住——
        这正是并发双插 present 的根因，部分唯一索引是唯一的 DB 层防线。
        """
        from sqlalchemy.exc import IntegrityError as IE

        student = seed_data["student"]
        db_session.add(
            models.RollCallEvent(
                session_id=rollcall_session.id,
                student_id=student.id,
                path_type="manual",
                base_status="present",
                status_source="manual_checkin",
            )
        )
        db_session.commit()

        db_session.add(
            models.RollCallEvent(
                session_id=rollcall_session.id,
                student_id=student.id,
                path_type="manual",
                base_status="late",
                status_source="auto_nfc",
            )
        )
        with pytest.raises(IE):
            db_session.commit()
        db_session.rollback()

    def test_settle_row_and_real_checkin_coexist(
        self, db_session, seed_data, rollcall_session
    ):
        """结算 absent 行（auto_settle）+ 离线补传真实签到行合法共存 —— 索引谓词
        只圈 auto_nfc/manual_checkin，不能挡 append-only 纠错履历（补传回归）。"""
        from sqlalchemy import select

        student = seed_data["student"]
        db_session.add(
            models.RollCallEvent(
                session_id=rollcall_session.id,
                student_id=student.id,
                path_type="manual",
                base_status="absent",
                status_source="auto_settle",
            )
        )
        db_session.commit()

        db_session.add(
            models.RollCallEvent(
                session_id=rollcall_session.id,
                student_id=student.id,
                path_type="A",
                base_status="present",
                status_source="auto_nfc",
            )
        )
        db_session.commit()  # 不抛 = 共存成立

        rows = db_session.scalars(
            select(models.RollCallEvent).where(
                models.RollCallEvent.session_id == rollcall_session.id,
                models.RollCallEvent.student_id == student.id,
            )
        ).all()
        assert len(rows) == 2


class TestStatusSourceServerDerived:
    """审查 backend#6：status_source 服务端推导、不信客户端。"""

    def test_client_cannot_send_teacher_override(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """客户端自选 teacher_override / auto_settle → schema 层 422（改判只走 PATCH /events）。"""
        student_id = str(seed_data["student"].id)
        for forged in ("teacher_override", "auto_settle"):
            res = client.post(
                f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
                json={"student_id": student_id, "status_source": forged},
                headers={"Authorization": f"Bearer {teacher_token}"},
            )
            assert res.status_code == 422, f"{forged} 应被 422 拒绝: {res.text}"

    def test_no_card_uid_stored_as_manual_even_if_client_says_auto_nfc(
        self, client, teacher_token, seed_data, rollcall_session
    ):
        """无 card_uid 的签到即使客户端声称 auto_nfc，落库也是 manual_checkin（服务端推导）。"""
        student_id = str(seed_data["student"].id)
        res = client.post(
            f"/api/v1/rollcall/sessions/{rollcall_session.id}/checkins",
            json={"student_id": student_id, "status_source": "auto_nfc"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert res.status_code == 201, res.text
        assert res.json()["data"]["status_source"] == "manual_checkin"
