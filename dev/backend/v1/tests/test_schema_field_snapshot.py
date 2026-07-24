"""关键 Out schema 字段集快照测试 — B-中-17（2026-06-15 全维度审查）。

前后端字段对齐此前没有自动化测试守。本文件给几个核心响应模型（iOS / Android / 老师网页
都消费的 Out schema）的字段集打快照断言：字段名一旦增删 / 改名，本测试立刻失败，
逼开发者同步更新各端 Decodable / data class，避免静默漂移导致客户端解码炸。

⚠️ 这是「期望集」断言，不是描述性测试 —— 当确实要改字段时，先改各端、再来同步本文件的期望集
（修改本文件 = 显式承认「我知道这影响所有客户端」）。

跑：
    cd dev/backend/v1
    .venv/bin/python -m pytest tests/test_schema_field_snapshot.py -q
"""

from __future__ import annotations

from app import schemas

# 各 Out schema 的期望字段集（与 iOS NetworkModels.swift / Android Models.kt 对齐的契约）。
# 改这里前必须先把对应端的解码模型同步好。
EXPECTED_FIELDS: dict[str, set[str]] = {
    "ApplicationOut": {
        "id",
        "student_id",
        "student",
        "kind",
        "leave_date",
        "leave_method",
        "leave_time",
        "return_date",
        "return_method",
        "return_time",
        "contact_phone",
        "meal_note",
        "stay_locations",
        "meals_skip",
        "companion",
        "dest_cities",
        "receipt_submitted",
        "reason",
        "is_long_vacation",
        "flight_dep_air",
        "flight_dep_at",
        "flight_arr_air",
        "flight_arr_at",
        "taxi_reservation_time",
        "bus_route_id",
        "submitted_at",
        "status",
        "withdrawn_at",
        "approval_chain",
    },
    "TeacherOut": {
        "id",
        "login_id",
        "name",
        "email",
        "role",
        "permission_group",
        "assigned_dorm",
        "status",
        "created_at",
        # 临时账户到期时间（2026-06-18 加）— 仅老师网页消费，iOS/Android 学生端不解码 TeacherOut
        "expires_at",
    },
    "OutingOut": {
        "id",
        "student_id",
        "student",
        "outing_date",
        "destination",
        "leave_time",
        "return_time",
        "taxi_reservation_time",
        "reason",
        "status",
        "submitted_at",
        "withdrawn_at",
        "confirmed_by_teacher_id",
        "confirmed_by_name",
        "confirmed_at",
        # 却下理由（2026-07-22 外出事后确认制加）— status=rejected 时才可能有值
        "reject_reason",
    },
    "StudyOnlineRequestOut": {
        "id",
        "student_id",
        "reason",
        "period_from",
        "period_to",
        "weekly_schedule",
        "contract_ref",
        "contract_file_name",
        "contract_mime",
        "contract_size",
        "submitted_at",
        "status",
        "decided_by",
        "decided_at",
        "comment",
        # 学生摘要三字段 — 老师在线学习申请列表辨认「谁申请」用，学生自查场景为 None
        "student_name",
        "student_no",
        "room_no",
    },
    "RegistrationCodeOut": {
        "code",
        "created_at",
        "expires_at",
        "expires_in_seconds",
    },
}


def test_out_schema_fields_match_snapshot():
    """逐个 Out schema 的字段集必须与期望快照完全一致（增 / 删 / 改名都会触发失败）。"""
    mismatches = []
    for name, expected in EXPECTED_FIELDS.items():
        cls = getattr(schemas, name)
        actual = set(cls.model_fields.keys())
        if actual != expected:
            added = actual - expected
            removed = expected - actual
            mismatches.append(
                f"{name}: 新增字段={sorted(added)} 缺失字段={sorted(removed)}"
            )
    assert not mismatches, (
        "Out schema 字段集与快照不符（改字段需同步 iOS/Android/web 解码模型 + 本测试期望集）：\n"
        + "\n".join(mismatches)
    )
