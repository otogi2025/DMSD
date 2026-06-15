"""老师权限分级 — 单源真值矩阵（实装 design/teacher_permission_v1.md §5）。

5 个权限组 × 17 个功能簇 → 三态权限级别（M 管理 / V 查看 / ✕ 无）。
`Teacher.permission_group` 只存组名；本模块把组名展开成每簇的级别。

设计原则（itsuki 2026-06-11）：权限按「权限组」判，职位（teachers.role）退化为纯显示标签、
不参与鉴权。本模块不依赖职位——唯一例外是向后兼容的 ROLE_DEFAULT_GROUP：
当某老师还没显式配权限组（permission_group 为 NULL）时，按职位推一个默认组，
保证迁移前建的老师 / 测试夹具里只给了 role 的老师仍能正常鉴权。生产环境账号创建时
显式指定组，这个职位回退分支不会触发。
"""

from __future__ import annotations

# ---------------------------------------------------------------
# 权限级别（整数，可直接比较：MANAGE > VIEW > NONE）
# ---------------------------------------------------------------
NONE = 0  # ✕ 不可见
VIEW = 1  # V 仅查看（只读）
MANAGE = 2  # M 管理（增删改 + 蕴含查看）

_LEVEL_NAME = {NONE: "✕", VIEW: "V（査看）", MANAGE: "M（管理）"}


def level_name(level: int) -> str:
    return _LEVEL_NAME.get(level, str(level))


# ---------------------------------------------------------------
# 5 个权限组（§3）
# ---------------------------------------------------------------
GROUP_OP = "op"  # 全权限·非个人（系统最高运维账号）
GROUP_DORM_ADMIN = "寮管理者"  # 全权限·个人
GROUP_GENERAL = "一般宿管"  # 受限：日常运营全能，不含晚自习/学习管理
GROUP_GENERAL_STUDY = "一般宿管+晚自习"  # 一般宿管 + 晚自习出席/学习管理
GROUP_APPROVAL = "申請承認専用"  # 以审批为核心 + 部分公共信息管理，其余只读

ALL_GROUPS = (
    GROUP_OP,
    GROUP_DORM_ADMIN,
    GROUP_GENERAL,
    GROUP_GENERAL_STUDY,
    GROUP_APPROVAL,
)

# ---------------------------------------------------------------
# 17 个功能簇（§5 矩阵的行）
# ---------------------------------------------------------------
C_ROLLCALL = "点呼运营"  # 1
C_APPROVAL = "申请审批"  # 2（含在线学习审批）
C_DEMERIT = "扣分管理"  # 3
C_FRONTDESK = "前台·宅配"  # 4
C_ANNOUNCE = "公告"  # 5
C_BUS = "巴士路线"  # 6
C_EVENT = "行事·活动"  # 7
C_LOSTFOUND = "遗失物"  # 8
C_SONG = "点歌"  # 9
C_MEAL = "食数计算·导出"  # 10
C_STUDY = "晚自习出席记录"  # 11
C_STUDENT_ACCOUNT = "学生账号管理"  # 12
C_REG_CODE = "注册码管理"  # 13
C_INCIDENT = "事案记录"  # 14
C_GUIDANCE = "指导履历"  # 15
C_TEACHER_ACCOUNT = "老师账号管理"  # 16
C_AUDIT_LOG = "操作履历审计"  # 17（2026-06-16 itsuki：老师操作记录页，只读审计）

ALL_CLUSTERS = (
    C_ROLLCALL,
    C_APPROVAL,
    C_DEMERIT,
    C_FRONTDESK,
    C_ANNOUNCE,
    C_BUS,
    C_EVENT,
    C_LOSTFOUND,
    C_SONG,
    C_MEAL,
    C_STUDY,
    C_STUDENT_ACCOUNT,
    C_REG_CODE,
    C_INCIDENT,
    C_GUIDANCE,
    C_TEACHER_ACCOUNT,
    C_AUDIT_LOG,
)

# ---------------------------------------------------------------
# §5 权限矩阵（单源真值）— 行=功能簇，列=权限组 → 级别
#   M=MANAGE, V=VIEW, 缺省=NONE。严格照 teacher_permission_v1.md §5 表，不得自行改动。
# ---------------------------------------------------------------
_M, _V, _N = MANAGE, VIEW, NONE
_O, _DA, _G, _GS, _AP = (
    GROUP_OP,
    GROUP_DORM_ADMIN,
    GROUP_GENERAL,
    GROUP_GENERAL_STUDY,
    GROUP_APPROVAL,
)

PRESET: dict[str, dict[str, int]] = {
    #                       op   寮管理者 一般宿管 +晚自习 申請承認専用
    C_ROLLCALL: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 1
    C_APPROVAL: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 2
    C_DEMERIT: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 3
    C_FRONTDESK: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 4
    C_ANNOUNCE: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 5
    C_BUS: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 6
    C_EVENT: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 7
    C_LOSTFOUND: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 8
    C_SONG: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 9
    C_MEAL: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _M},  # 10
    C_STUDY: {_O: _M, _DA: _M, _G: _V, _GS: _M, _AP: _V},  # 11
    C_STUDENT_ACCOUNT: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 12
    C_REG_CODE: {
        _O: _M,
        _DA: _M,
        _G: _M,
        _GS: _M,
        _AP: _M,
    },  # 13（2026-06-14 itsuki 拍板：所有权限组都能完整用注册码，申請承認専用 V→M）
    C_INCIDENT: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 14
    C_GUIDANCE: {_O: _M, _DA: _M, _G: _M, _GS: _M, _AP: _V},  # 15
    C_TEACHER_ACCOUNT: {_O: _M, _DA: _M, _G: _V, _GS: _V, _AP: _V},  # 16
    # 17（2026-06-16 itsuki：操作记录页只读审计，只给管理角色看）：
    #   op / 寮管理者(寮務部長·寮務課長) 完全访问；一般宿管(管理係) 查看；
    #   一般宿管+晚自习(寮監·学習担当) 与 申請承認専用(国際交流) 无权限。
    C_AUDIT_LOG: {_O: _M, _DA: _M, _G: _V, _GS: _N, _AP: _N},  # 17
}


def group_level(group: str | None, cluster: str) -> int:
    """某权限组对某功能簇的级别（缺省 NONE）。"""
    if not group:
        return NONE
    return PRESET.get(cluster, {}).get(group, NONE)


def has_permission(group: str | None, cluster: str, required: int) -> bool:
    """该组对该簇是否达到所需级别（MANAGE 蕴含 VIEW）。"""
    return group_level(group, cluster) >= required


# ---------------------------------------------------------------
# 职位 → 默认权限组（向后兼容回退，见模块顶部说明）
#   仅当 Teacher.permission_group 为 NULL 时使用。映射依据：让没显式配组的
#   老师拿到与其职位日常职责最接近的组（同时保持现有测试夹具的鉴权预期）。
# ---------------------------------------------------------------
ROLE_DEFAULT_GROUP: dict[str, str] = {
    "校長": GROUP_DORM_ADMIN,
    "寮務部長": GROUP_DORM_ADMIN,
    "寮務課長": GROUP_DORM_ADMIN,
    "国際交流部長": GROUP_APPROVAL,
    "国際交流課長": GROUP_APPROVAL,
    "管理係": GROUP_GENERAL,
    # 寮監 = 一线寮务运营（点呼 / 扣分 / 前台 / 晚自习全要操作）→ 全操作组（含晚自习）。
    "寮監": GROUP_GENERAL_STUDY,
    # 学習担当 = 负责晚自习出席 / 学习管理（itsuki 2026-06-12 确认实际职责）→ 一般宿管+晚自习。
    # （申請承認専用 对晚自习只有 VIEW，会把学習担当锁出晚自习管理，故不映到该组。）
    "学習担当": GROUP_GENERAL_STUDY,
    "寮務一般教師": GROUP_GENERAL,
}


def effective_group(teacher) -> str:
    """当前老师的有效权限组：显式 permission_group 优先，否则按职位回退。"""
    explicit = getattr(teacher, "permission_group", None)
    if explicit:
        return explicit
    return ROLE_DEFAULT_GROUP.get(getattr(teacher, "role", None), GROUP_APPROVAL)
