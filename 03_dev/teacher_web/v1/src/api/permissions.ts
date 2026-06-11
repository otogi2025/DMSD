// 老师权限分级 — 前端单源真值矩阵（镜像后端 app/permissions.py，实装 teacher_permission_v1.md §5）。
//
// 用途：老师网页据此「按权限组隐藏/置灰功能入口」（设计 §9）。
// ⚠️ 真正的鉴权在后端 require_permission —— 前端这份只用于 UI 显隐/置灰，不是安全边界。
// 改这份时必须同步后端 PRESET，二者保持一致。

export type Level = 0 | 1 | 2; // 0=✕ 无 / 1=V 仅查看 / 2=M 管理
export const NONE: Level = 0;
export const VIEW: Level = 1;
export const MANAGE: Level = 2;

// 5 个权限组（§3）
export const GROUP_OP = "op";
export const GROUP_DORM_ADMIN = "寮管理者";
export const GROUP_GENERAL = "一般宿管";
export const GROUP_GENERAL_STUDY = "一般宿管+晚自习";
export const GROUP_APPROVAL = "申請承認専用";

// 账号创建可选的 4 个组（op 不在此 —— 系统运维账号只由后端 seed + 环境变量建）
export const SELECTABLE_GROUPS: { value: string; label: string }[] = [
  { value: GROUP_DORM_ADMIN, label: "寮管理者（全権限・個人）" },
  { value: GROUP_GENERAL, label: "一般宿管（日常運営全般、晚自習除く）" },
  { value: GROUP_GENERAL_STUDY, label: "一般宿管＋晚自習" },
  {
    value: GROUP_APPROVAL,
    label: "申請承認専用（審批中心＋公共情報、他は閲覧のみ）",
  },
];

// 9 个职位标签（§4）— 仅显示用
export const ROLE_LABELS = [
  "校長",
  "寮務部長",
  "寮務課長",
  "国際交流部長",
  "国際交流課長",
  "管理係",
  "寮監",
  "学習担当",
  "寮務一般教師",
];

// 16 个功能簇（§5 矩阵行）
export const C_ROLLCALL = "点呼运营";
export const C_APPROVAL = "申请审批";
export const C_DEMERIT = "扣分管理";
export const C_FRONTDESK = "前台·宅配";
export const C_ANNOUNCE = "公告";
export const C_BUS = "巴士路线";
export const C_EVENT = "行事·活动";
export const C_LOSTFOUND = "遗失物";
export const C_SONG = "点歌";
export const C_MEAL = "食数计算·导出";
export const C_STUDY = "晚自习出席记录";
export const C_STUDENT_ACCOUNT = "学生账号管理";
export const C_REG_CODE = "注册码管理";
export const C_INCIDENT = "事案记录";
export const C_GUIDANCE = "指导履历";
export const C_TEACHER_ACCOUNT = "老师账号管理";

const M = MANAGE;
const V = VIEW;

// §5 矩阵：cluster → { group: level }（严格照 teacher_permission_v1.md §5）
export const PRESET: Record<string, Record<string, Level>> = {
  [C_ROLLCALL]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_APPROVAL]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_DEMERIT]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_FRONTDESK]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_ANNOUNCE]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_BUS]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_EVENT]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_LOSTFOUND]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_SONG]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_MEAL]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: M,
  },
  [C_STUDY]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: V,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_STUDENT_ACCOUNT]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_REG_CODE]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_INCIDENT]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_GUIDANCE]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: M,
    [GROUP_GENERAL_STUDY]: M,
    [GROUP_APPROVAL]: V,
  },
  [C_TEACHER_ACCOUNT]: {
    [GROUP_OP]: M,
    [GROUP_DORM_ADMIN]: M,
    [GROUP_GENERAL]: V,
    [GROUP_GENERAL_STUDY]: V,
    [GROUP_APPROVAL]: V,
  },
};

// 职位 → 默认权限组（向后兼容回退，镜像后端 ROLE_DEFAULT_GROUP）。
// 仅当 TeacherOut.permission_group 为 null 时用于 UI 推断当前老师有效组。
const ROLE_DEFAULT_GROUP: Record<string, string> = {
  校長: GROUP_DORM_ADMIN,
  寮務部長: GROUP_DORM_ADMIN,
  寮務課長: GROUP_DORM_ADMIN,
  国際交流部長: GROUP_APPROVAL,
  国際交流課長: GROUP_APPROVAL,
  管理係: GROUP_GENERAL,
  寮監: GROUP_GENERAL_STUDY,
  学習担当: GROUP_APPROVAL,
  寮務一般教師: GROUP_GENERAL,
};

export interface TeacherLike {
  role: string;
  permission_group?: string | null;
}

/** 当前老师的有效权限组：显式组优先，否则按职位回退。 */
export function effectiveGroup(teacher: TeacherLike): string {
  if (teacher.permission_group) return teacher.permission_group;
  return ROLE_DEFAULT_GROUP[teacher.role] ?? GROUP_APPROVAL;
}

/** 某老师对某功能簇是否达到所需级别（MANAGE 蕴含 VIEW）。 */
export function hasPermission(
  teacher: TeacherLike,
  cluster: string,
  required: Level,
): boolean {
  const group = effectiveGroup(teacher);
  const level = PRESET[cluster]?.[group] ?? NONE;
  return level >= required;
}

export const canView = (teacher: TeacherLike, cluster: string) =>
  hasPermission(teacher, cluster, VIEW);
export const canManage = (teacher: TeacherLike, cluster: string) =>
  hasPermission(teacher, cluster, MANAGE);
