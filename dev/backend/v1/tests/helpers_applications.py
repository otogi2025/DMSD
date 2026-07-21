"""申请（帰省届等）测试共用夹具。

backend#126：_kisei_body 原本分别定义在 test_applications.py 与
test_application_return_withdraw.py 两份，抽到此处共用，避免两份漂移。
"""

from __future__ import annotations

from datetime import date, timedelta


def _kisei_body(leave_offset_days: int = 3) -> dict:
    """生成 帰省届 body — 出寮日 = 明日 + offset。"""
    leave = date.today() + timedelta(days=leave_offset_days)
    ret = leave + timedelta(days=2)
    return {
        "kind": "帰省",
        "leave_date": leave.isoformat(),
        "leave_method": "新幹線",
        "leave_time": "19:00:00",
        "return_date": ret.isoformat(),
        "return_method": "新幹線",
        "return_time": "20:00:00",
        "reason": "帰省",
    }
