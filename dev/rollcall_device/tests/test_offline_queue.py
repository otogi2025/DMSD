"""离线队列测试（契约 §6）—— 入队 / 出队 / 补传语义。"""

from src.offline.queue import (
    OfflineQueue,
    ReplayAction,
    classify_replay_result,
)


def _body(uid: str, swipe="2026-07-17T21:00:00+09:00"):
    return {"path_type": "A", "card_uid": uid, "swipe_time": swipe}


def test_enqueue_and_count(tmp_path):
    q = OfflineQueue(tmp_path / "q.sqlite3")
    q.enqueue(_body("aa"))
    q.enqueue(_body("bb"))
    assert q.count() == 2
    q.close()


def test_peek_all_is_fifo(tmp_path):
    q = OfflineQueue(tmp_path / "q.sqlite3")
    q.enqueue(_body("aa"))
    q.enqueue(_body("bb"))
    q.enqueue(_body("cc"))
    items = q.peek_all()
    assert [i.body["card_uid"] for i in items] == ["aa", "bb", "cc"]
    q.close()


def test_classify_success_and_duplicate_dequeue():
    # ok=true（含 duplicate=true 那条也是 ok=true）→ 出队
    assert classify_replay_result(True, None) is ReplayAction.DEQUEUE


def test_classify_session_ended_dequeue_no_retry():
    # 契约 §6：swipe_time 晚于场次结束 → SESSION_NOT_RUNNING 出队不重试（7-17 拍板删 TIMEOUT）
    assert classify_replay_result(False, "SESSION_NOT_RUNNING") is ReplayAction.DEQUEUE


def test_classify_business_errors_dequeue():
    for code in ("UNKNOWN_CARD", "UNREGISTERED_UID", "SESSION_NOT_RUNNING"):
        assert classify_replay_result(False, code) is ReplayAction.DEQUEUE


def test_classify_auth_error_stops():
    assert classify_replay_result(False, "UNAUTHORIZED") is ReplayAction.STOP_AUTH
    assert classify_replay_result(False, "DEVICE_NOT_ACTIVE") is ReplayAction.STOP_AUTH


def test_replay_dequeues_delivered_and_stops_on_network(tmp_path):
    q = OfflineQueue(tmp_path / "q.sqlite3")
    q.enqueue(_body("aa"))  # 将成功
    q.enqueue(_body("bb"))  # 将 SESSION_NOT_RUNNING（终态，出队）
    q.enqueue(_body("cc"))  # 网络未通 → 停，保留

    def sender(body):
        uid = body["card_uid"]
        if uid == "aa":
            return (True, None)
        if uid == "bb":
            return (False, "SESSION_NOT_RUNNING")
        return None  # cc：网络层失败

    removed = q.replay(sender)
    assert removed == 2
    remaining = [i.body["card_uid"] for i in q.peek_all()]
    assert remaining == ["cc"]
    q.close()


def test_replay_stops_and_keeps_on_auth_error(tmp_path):
    q = OfflineQueue(tmp_path / "q.sqlite3")
    q.enqueue(_body("aa"))
    q.enqueue(_body("bb"))

    def sender(body):
        return (False, "UNAUTHORIZED")

    removed = q.replay(sender)
    assert removed == 0
    assert q.count() == 2  # 鉴权失败保留全部，交上层刷新令牌后再补
    q.close()


def test_replay_all_success_empties_queue(tmp_path):
    q = OfflineQueue(tmp_path / "q.sqlite3")
    for uid in ("aa", "bb", "cc"):
        q.enqueue(_body(uid))
    removed = q.replay(lambda body: (True, None))
    assert removed == 3
    assert q.count() == 0
    q.close()


def test_persistence_across_reopen(tmp_path):
    path = tmp_path / "q.sqlite3"
    q1 = OfflineQueue(path)
    q1.enqueue(_body("aa"))
    q1.close()
    q2 = OfflineQueue(path)  # 重新打开，数据还在（落盘）
    assert q2.count() == 1
    q2.close()


def test_invalid_credentials_never_dequeues(tmp_path):
    """2026-07-18 cursor 审查 blocker 2 的回归：INVALID_CREDENTIALS 是后端令牌过期时
    实际返回的码。它若不在鉴权集合里，断网攒下的签到会被当终态业务错误逐条丢光。"""
    q = OfflineQueue(tmp_path / "q.sqlite3")
    for uid in ("aa", "bb", "cc"):
        q.enqueue(_body(uid))

    assert classify_replay_result(False, "INVALID_CREDENTIALS") is ReplayAction.STOP_AUTH
    removed = q.replay(lambda body: (False, "INVALID_CREDENTIALS"))
    assert removed == 0
    assert q.count() == 3, "令牌失效时一条都不许出队"
    q.close()


def test_auth_codes_shared_with_feedback_layer():
    """反馈层（白灯）与队列层（不出队）必须认同一套鉴权码 —— 两边各存一份就是
    blocker 2 的成因，现在统一在 api.envelope，这条测试锁死它们不再分家。"""
    from src.api.envelope import AUTH_ERROR_CODES as envelope_codes
    from src.feedback import _AUTH_ERROR_CODES as feedback_codes
    from src.offline.queue import AUTH_ERROR_CODES as queue_codes

    assert queue_codes is envelope_codes
    assert feedback_codes is envelope_codes
    assert "INVALID_CREDENTIALS" in envelope_codes
