"""权限矩阵单元测试 — B-中-15（2026-06-15 全维度审查）。

app/permissions.py 的 PRESET（5 权限组 × 17 功能簇）是鉴权单源真值，此前无直接单测。
本文件把矩阵里几个关键边界格断言一遍，锁死「申請承認専用 V vs M」「一般宿管 在学习簇被降级到 V」
这类容易在重排时被改错的格子，再做几条整体不变量检查（每组每簇级别合法 / MANAGE 蕴含 VIEW）。

跑：
    cd dev/backend/v1
    .venv/bin/python -m pytest tests/test_permissions.py -q
"""

from __future__ import annotations

from app import permissions as P


class TestPresetBoundaryCells:
    """逐个断言矩阵里语义关键 / 易错的边界格。"""

    def test_approval_group_view_only_on_rollcall(self):
        # 申請承認専用 对点呼运营只读（V），不能管理（M）
        assert P.group_level(P.GROUP_APPROVAL, P.C_ROLLCALL) == P.VIEW

    def test_approval_group_manage_on_approval(self):
        # 申請承認専用 的本职 —— 申请审批必须是 MANAGE
        assert P.group_level(P.GROUP_APPROVAL, P.C_APPROVAL) == P.MANAGE

    def test_approval_group_view_only_on_demerit(self):
        # 申請承認専用 对扣分管理只读
        assert P.group_level(P.GROUP_APPROVAL, P.C_DEMERIT) == P.VIEW

    def test_general_group_view_only_on_study(self):
        # 一般宿管（不含晚自习）对晚自习出席记录只读 V，区别于「一般宿管+晚自习」的 M
        assert P.group_level(P.GROUP_GENERAL, P.C_STUDY) == P.VIEW

    def test_general_study_group_manage_on_study(self):
        assert P.group_level(P.GROUP_GENERAL_STUDY, P.C_STUDY) == P.MANAGE

    def test_reg_code_all_groups_manage(self):
        # C_REG_CODE：2026-06-14 itsuki 拍板所有组都 MANAGE（含 申請承認専用）
        for g in P.ALL_GROUPS:
            assert P.group_level(g, P.C_REG_CODE) == P.MANAGE, g

    def test_teacher_account_only_op_and_dorm_admin_manage(self):
        # 老师账号管理：只有 op / 寮管理者 是 MANAGE，其余三组 VIEW
        assert P.group_level(P.GROUP_OP, P.C_TEACHER_ACCOUNT) == P.MANAGE
        assert P.group_level(P.GROUP_DORM_ADMIN, P.C_TEACHER_ACCOUNT) == P.MANAGE
        assert P.group_level(P.GROUP_GENERAL, P.C_TEACHER_ACCOUNT) == P.VIEW
        assert P.group_level(P.GROUP_GENERAL_STUDY, P.C_TEACHER_ACCOUNT) == P.VIEW
        assert P.group_level(P.GROUP_APPROVAL, P.C_TEACHER_ACCOUNT) == P.VIEW

    def test_op_and_dorm_admin_manage_everything(self):
        # op 与 寮管理者 对全部 17 簇都是 MANAGE（全权限组）
        for c in P.ALL_CLUSTERS:
            assert P.group_level(P.GROUP_OP, c) == P.MANAGE, c
            assert P.group_level(P.GROUP_DORM_ADMIN, c) == P.MANAGE, c


class TestPresetInvariants:
    """矩阵整体不变量。"""

    def test_matrix_covers_all_clusters(self):
        # PRESET 必须给全部 17 簇定义级别
        assert set(P.PRESET.keys()) == set(P.ALL_CLUSTERS)

    def test_every_cell_is_valid_level(self):
        # 每格只能是 NONE / VIEW / MANAGE，且每簇都给全 5 个组定义了级别
        valid = {P.NONE, P.VIEW, P.MANAGE}
        for cluster, row in P.PRESET.items():
            assert set(row.keys()) == set(P.ALL_GROUPS), cluster
            for group, level in row.items():
                assert level in valid, (cluster, group, level)

    def test_has_permission_manage_implies_view(self):
        # has_permission：达到 MANAGE 的格子必然满足 VIEW 要求（M 蕴含 V）
        for cluster, row in P.PRESET.items():
            for group, level in row.items():
                if level == P.MANAGE:
                    assert P.has_permission(group, cluster, P.VIEW), (cluster, group)
                    assert P.has_permission(group, cluster, P.MANAGE), (cluster, group)
                elif level == P.VIEW:
                    assert P.has_permission(group, cluster, P.VIEW), (cluster, group)
                    assert not P.has_permission(group, cluster, P.MANAGE), (
                        cluster,
                        group,
                    )

    def test_unknown_group_and_cluster_default_none(self):
        # 无组（None）/ 未知簇 → NONE，不可越权
        assert P.group_level(None, P.C_ROLLCALL) == P.NONE
        assert P.group_level(P.GROUP_OP, "不存在的功能簇") == P.NONE
        assert not P.has_permission(None, P.C_APPROVAL, P.VIEW)
