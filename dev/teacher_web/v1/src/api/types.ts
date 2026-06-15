// 后端 API 请求/响应类型 —— 严格对齐 backend schemas.py（单源真值）。
// 2026-06-05 三路审查（workflow+codex+自审）后按 schemas.py 逐类型重写对齐，行号见各注释。

// ── 老师档案（原 store/auth.TeacherProfile，本地化）──
export interface TeacherProfile {
  id: string;
  login_id: string;
  name: string;
  email: string;
  role: string;
  assigned_dorm: number | null;
}

export interface TeacherLoginOut {
  access_token: string;
  teacher: TeacherProfile;
}

// ── 申請（出寮届）──
// 对齐 schemas.py StayLocation(29-35)
export interface StayLocation {
  kind: string; // 必填：ホテル / 親戚宅 / 自宅 等
  name: string; // 必填，max 200
  address?: string | null; // 可选，max 500
  phone?: string | null; // 可选，max 32
}

// 对齐 schemas.py MealSkipEntry(38-42)
export interface MealSkip {
  date: string;
  meal: "朝食" | "昼食" | "夕食";
}

export type AppStatus =
  | "pending"
  | "approved_partial"
  | "approved"
  | "rejected"
  | "withdrawn"
  | "returned";

export interface ApprovalStep {
  approver_role: string;
  decision: "approve" | "reject" | null;
  decided_at: string | null;
  comment: string | null;
  approver_id: string | null;
}

export interface StudentBrief {
  id: string;
  student_no: string;
  name: string;
  dorm_unit: number;
  is_overseas: boolean;
  room_no: string;
}

// 对齐 schemas.py ApplicationOut(182-223)。date/time/datetime 序列化成字符串 → string。
export interface Application {
  id: string;
  student_id: string;
  student: StudentBrief | null;
  kind: "帰省" | "外泊" | "帰国";
  leave_date: string;
  leave_method: string;
  leave_time: string;
  return_date: string;
  return_method: string;
  return_time: string;
  contact_phone: string | null;
  meal_note: string | null;
  stay_locations: StayLocation[] | null;
  meals_skip: MealSkip[] | null;
  companion: string | null;
  dest_cities: string | null;
  receipt_submitted: boolean; // 后端 bool=False，非可空
  reason: string | null;
  is_long_vacation: boolean; // 后端 bool=False，非可空
  flight_dep_air: string | null;
  flight_dep_at: string | null;
  flight_arr_air: string | null;
  flight_arr_at: string | null;
  taxi_reservation_time: string | null; // 后端 Optional[time]
  bus_route_id: string | null;
  submitted_at: string;
  status: AppStatus;
  withdrawn_at: string | null;
  approval_chain: ApprovalStep[];
}

export interface AuditEntry {
  id: string;
  actor_type: string;
  actor_id: string | null;
  action: string;
  payload: unknown;
  created_at: string;
}

// ── 学習出席（对齐 schemas.py 377-413/450-462）──
export interface StudyAttendeeOut {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
  expected_status: "expected" | "exempted_outstay" | "exempted_absence";
  exemption_reason: string | null;
  checkin: { checked_at: string | null; status: string } | null;
}

export interface StudyTodayOut {
  target_date: string;
  study_start_at: string;
  expected_attendees: StudyAttendeeOut[];
  exempted_count: { outstay: number; absence_request: number };
  summary: {
    expected: number;
    checked_in: number;
    late: number;
    absent: number;
  };
}

export interface StudyCheckinOut {
  student_id: string;
  target_date: string;
  checked_at: string | null;
  status: string;
}

export interface StudyAbsenceRequestOut {
  id: string;
  student_id: string;
  target_date: string;
  period: "first_half" | "second_half" | "full"; // 请假范围（前半节/后半节/全部）
  reason: string;
  submitted_at: string;
  status: "pending" | "approved" | "rejected";
  decided_by: string | null;
  decided_at: string | null;
  comment: string | null;
}

// 学習対象名簿 在籍者
export interface StudyRosterItem {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
}

// ── 点呼（对齐 schemas.py 693-757）──
export interface RollCallSessionOut {
  id: string;
  dorm_unit_set: number[];
  session_type: "morning" | "evening";
  day_type: string;
  session_status: "draft" | "running" | "ended";
  started_at: string | null;
  ended_at: string | null;
  scheduled_window_start_at: string;
  scheduled_on_time_end_at: string;
  scheduled_late_end_at: string;
  scheduled_auto_end_at: string;
}

// 对齐 RollCallBoardEntryOut(740-749)
export interface RollCallBoardEntry {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  base_status: "init" | "present" | "late" | "absent" | "exempt_range";
  checked_in_at: string | null;
  last_event_id: string | null; // 本场次该生最新 event id，OverrideModal 改判用；init 学生为 null
}

export interface RollCallBoardOut {
  session_id: string;
  session_status: string;
  entries: RollCallBoardEntry[];
  summary: Record<string, number>;
}

export interface RollCallSummaryOut {
  session_id: string;
  absent: { student_id: string; name: string; room_no: string }[];
  late: { student_id: string; name: string; room_no: string }[];
  health_issue: unknown[];
  exempted_outstay: { student_id: string; name: string; room_no: string }[];
}

// PATCH /rollcall/events/{id} 返回，对齐 RollCallEventOut(729-737)
export interface RollCallEventOut {
  id: string;
  student_id: string;
  base_status: string; // init/present/late/absent/exempt_range
  status_source: string; // auto_nfc / manual
  checked_in_at: string;
  path_type: string | null;
}

// ── 教员账户 ──
export interface TeacherOut {
  id: string;
  login_id: string;
  name: string;
  email: string;
  role: string;
  // 权限组（teacher_permission_v1 §3）— 决定每个功能簇的权限级别；null = 未显式配组（后端按职位回退默认组）
  permission_group: string | null;
  assigned_dorm: number | null;
  status: string;
  created_at: string;
}

export interface TeacherPublic {
  id: string;
  name: string;
  assigned_dorm: number | null;
  last_login_at: string | null;
  // 有效权限组（后端已按职位回退）— 登录页按权限组分栏用
  permission_group: string | null;
}

export interface TeacherCreateIn {
  login_id: string;
  name: string;
  email: string;
  password: string;
  role: string; // 职位标签（仅显示）
  permission_group?: string | null; // 权限组（决定功能权限）
  assigned_dorm?: number;
}

export interface InvitationIn {
  target_email: string;
  target_role: string;
  target_dorm?: number;
}

export interface InvitationOut {
  id: string;
  token: string;
  target_email: string;
  target_role: string;
  expires_at: string;
}

// ── 公告 ──
export type AnnouncementScope = "all" | "male" | "female";

export interface AnnouncementBrief {
  id: string;
  title: string;
  body_summary: string;
  scope: AnnouncementScope;
  author_teacher_id: string;
  author_teacher_name: string;
  created_at: string;
  updated_at: string;
  is_read: boolean;
  reply_count: number;
}

export interface AnnouncementReplyOut {
  id: string;
  author_kind: "student" | "teacher";
  author_id: string;
  author_name: string;
  body: string;
  created_at: string;
}

export interface AnnouncementDetail {
  id: string;
  title: string;
  body: string;
  scope: AnnouncementScope;
  author_teacher_id: string;
  author_teacher_name: string;
  created_at: string;
  updated_at: string;
  replies: AnnouncementReplyOut[];
}

export interface AnnouncementCreateIn {
  title: string;
  body: string;
  scope: AnnouncementScope;
}

// ── 学生登録码（admin）──
export interface RegistrationCode {
  code: string;
  created_at: string;
  expires_at: string;
  expires_in_seconds: number;
}

// ── 清扫安排（罚则清扫）— 一条记录 = 一个学生 ──
export interface CleaningItem {
  id: string;
  student_id: string;
  area: string; // 改动2：自由文本（旧版是 7 选 1 枚举）
  scheduled_at: string; // 改动1：带时区 datetime（ISO8601）。旧版是 scheduled_date(date)
  status: "assigned" | "done" | "passed" | "failed" | "skipped";
  assigned_by_teacher_id: string | null;
  assigned_at: string;
  done_at: string | null;
  inspected_by_teacher_id: string | null;
  inspected_at: string | null;
  failure_reason: string | null;
  demerit_event_id: string | null;
}

// 老师排罚扫提交体
export interface CleaningCreateIn {
  student_id: string;
  area: string; // 改动2：自由文本
  scheduled_at: string; // 改动1：ISO8601 datetime
}

// 老师审核罚扫提交体
export interface CleaningInspectIn {
  result: "passed" | "failed";
  failure_reason?: string; // result==="failed" 时必填
}

// ── 扣分 / 規律処分 ──
export type DemeritSourceType =
  | "rollcall_late"
  | "rollcall_absent"
  | "cleaning_failed"
  | "curfew_violation"
  | "study_absent"
  | "manual";

// 对齐 DemeritRankingEntryOut(1025-1036)
export interface DisciplineRankingEntry {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
  total_points: number;
  is_cleaning_threshold: boolean; // >=4 点，清扫线（对称 is_curfew_threshold）
  is_curfew_threshold: boolean; // >=8 点，禁足线
}

// 对齐 DemeritRankingOut(1039-1045)
export interface DisciplineRankingOut {
  month: string;
  entries: DisciplineRankingEntry[];
  cleaning_threshold_count: number;
  curfew_threshold_count: number;
}

// 对齐 DemeritEventOut(999-1022) — createManualDemerit / revokeDemerit 返回
export interface DemeritEvent {
  id: string;
  student_id: string;
  source_type: DemeritSourceType;
  source_event_id: string | null;
  points: number;
  reason: string;
  month: string;
  created_at: string;
  created_by_teacher_id: string | null;
  revoked_at: string | null;
  revoked_by_teacher_id: string | null;
  revoke_reason: string | null;
}

// 对齐 DemeritManualIn(1074-1079)
export interface ManualDemeritIn {
  student_id: string;
  points: number;
  reason: string;
}

// ── 学生账号管理（对齐 StudentAccountListItem 1157-1178）──
export interface StudentAccountListItem {
  id: string;
  student_no: string;
  grade_code: string;
  class_code: string;
  seat_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
  gender: "male" | "female";
  status: string;
  needs_renewal: boolean;
  is_locked: boolean;
  last_login_at: string | null;
}

// 对齐 StudentAccountListOut(1181-1186)
export interface StudentAccountListOut {
  total: number;
  items: StudentAccountListItem[];
}

export interface PasswordResetOut {
  student_id: string;
  temporary_password: string;
  message: string;
}

export interface SimpleMessageOut {
  student_id: string;
  message: string;
}

// ── 行事予定（对齐 DormEventOut 1228-1240）──
export interface EventItem {
  id: string;
  title: string;
  category: string;
  event_date: string;
  start_at: string | null;
  end_at: string | null;
  description: string | null;
  created_by_teacher_id: string;
  created_at: string;
  updated_at: string | null;
}

// 对齐 DormEventListOut(1243-1246)
export interface EventListOut {
  items: EventItem[];
}

export interface EventCreateIn {
  title: string;
  category: string;
  event_date: string;
  start_at?: string;
  end_at?: string;
  description?: string;
}

// ── 巴士时刻表（对齐 BusRouteOut 1279-1293）──
export interface BusRoute {
  id: string;
  kind: "daily_commute" | "dorm_special";
  name: string;
  direction: string;
  schedule_at: string;
  arrival_at: string | null;
  visible_to: string; // 后端非空，默认 'all'
  note: string | null;
  purpose: string | null; // 用途说明 — 学生 iOS 端右上角展示
  deprecated: boolean;
  created_by_teacher_id: string;
  created_at: string;
  updated_at: string | null;
}

// 对齐 BusRouteListOut(1296-1299)
export interface BusRouteListOut {
  items: BusRoute[];
}

export interface BusRouteCreateIn {
  // 6-15: 表单去掉「種別」「便名」后 kind/name 改可选 —— 缺省时后端默认补全。
  kind?: string;
  name?: string;
  direction: string;
  schedule_at: string;
  arrival_at?: string;
  visible_to?: string;
  note?: string;
  purpose?: string;
}

// ── 前台业务（对齐 FrontDeskItemOut 1126-1138）──
export interface FrontDeskItem {
  id: string;
  kind: "delivery" | "lost_and_found";
  student_id: string | null;
  description: string; // 宅配可空（缺省空串）/ 失物必填 —— 后端列仍 NOT NULL
  location: string | null;
  item_count: number; // 宅配件数；失物恒 1（2026-06-14 加）
  status: "pending" | "notified" | "picked_up" | "expired" | "discarded";
  created_by_teacher_id: string;
  created_at: string;
  notified_at: string | null;
  picked_up_at: string | null;
  expires_at: string; // 后端必返
}

// 对齐 FrontDeskItemCreateIn(1148-）
export interface FrontDeskCreateIn {
  kind: "delivery" | "lost_and_found";
  student_id?: string;
  description?: string; // 宅配可选备注 / 失物必填（后端按 kind 校验，2026-06-14 改可选）
  location?: string;
  item_count?: number; // 宅配件数，默认 1、下限 1（2026-06-14 加）
}

// 前台登记宅配挑收件学生用的最小字段（对齐后端 schemas.FrontDeskStudentBrief）
export interface FrontDeskStudentBrief {
  id: string;
  name: string;
  room_no: string;
  student_no: string;
  dorm_unit: number;
}

// ── 学生个人档案聚合（对齐 StudentProfileOut 1543-1554 + Profile*Entry 1464-1540）──
export interface StudentProfileBasic {
  id: string;
  student_no: string;
  name: string;
  name_kana: string | null;
  grade_code: string;
  class_code: string;
  seat_no: string;
  gender: string;
  category: string;
  room_no: string;
  dorm_unit: number;
  is_overseas: boolean;
  email: string | null;
  phone: string | null;
  avatar_url: string | null;
  status: string;
  registered_at: string;
  needs_renewal: boolean;
}

export interface ProfileApplicationEntry {
  id: string;
  kind: "帰省" | "外泊" | "帰国";
  leave_date: string;
  return_date: string;
  status: string;
  submitted_at: string;
}

export interface ProfileStudyCheckinEntry {
  id: string;
  target_date: string;
  status: string;
  checked_at: string | null;
}

export interface ProfileRollCallEntry {
  id: string;
  session_id: string;
  session_type: string;
  base_status: string;
  status_source: string;
  checked_in_at: string;
}

export interface ProfileGuidanceEntry {
  id: string;
  category: string | null;
  guidance_date: string;
  confidential: boolean;
  content: string;
  created_at: string;
}

export interface ProfileDemeritEntry {
  id: string;
  source_type: DemeritSourceType;
  points: number;
  reason: string;
  month: string;
  created_at: string;
}

export interface ProfileStudyOnlineEntry {
  id: string;
  period_from: string;
  period_to: string;
  status: string;
  submitted_at: string;
  contract_file_name: string | null;
  contract_mime: string | null;
  contract_size: number | null;
}

export interface StudentProfile {
  student: StudentProfileBasic;
  applications: ProfileApplicationEntry[];
  study_checkins: ProfileStudyCheckinEntry[];
  rollcall_events: ProfileRollCallEntry[];
  guidance_records: ProfileGuidanceEntry[];
  demerit_events: ProfileDemeritEntry[];
  study_online_requests: ProfileStudyOnlineEntry[];
}

// ── 指導履歴（对齐 GuidanceRecordOut 1315-1324）──
export interface GuidanceItem {
  id: string;
  student_id: string;
  teacher_id: string; // 后端字段名是 teacher_id（不是 author_teacher_id）
  content: string;
  category: string | null;
  guidance_date: string;
  confidential: boolean;
  created_at: string;
  deleted_at: string | null;
}

// 对齐 GuidanceRecordCreateIn(1305-1312)
export interface GuidanceCreateIn {
  student_id: string;
  content: string;
  category?: string;
  guidance_date: string;
  confidential: boolean;
}

// ── 開示申請（对齐 GuidanceDisclosureRequestOut 1361-1373）──
export interface DisclosureRequest {
  id: string;
  student_id: string;
  student_no: string; // 后端发的是学号（不是 student_name）
  reason: string | null;
  requested_at: string; // 后端字段名是 requested_at（不是 submitted_at）
  status: "pending" | "approved_full" | "approved_partial" | "rejected";
  decided_by: string | null;
  decided_at: string | null;
  decision_note: string | null;
  visible_from: string | null;
  visible_until: string | null;
  revoked_at: string | null;
}

// 对齐 GuidanceDisclosureDecisionIn(1337-1344)
export interface DisclosureDecisionIn {
  decision: "approved_full" | "approved_partial" | "rejected";
  decision_note?: string;
  visible_from?: string;
  visible_until?: string;
}

// ── 事案録入（对齐 IncidentRecordOut 1415-1426 + IncidentStudentBrief 1408-1413）──
export interface IncidentStudentBrief {
  id: string;
  name: string;
}

export interface IncidentItem {
  id: string;
  title: string;
  body: string;
  incident_date: string;
  involved_student_ids: string[];
  involved_students: IncidentStudentBrief[]; // 6-04 杭田加的可点击 chip
  recorded_by: string;
  created_at: string;
  updated_at?: string | null;
  deleted_at?: string | null;
}

// 后端 listIncidents / getIncident 都返完整 IncidentRecordOut（含 body），列表项即详情
export type IncidentDetail = IncidentItem;

// 对齐 IncidentRecordCreateIn(1390-1396)
export interface IncidentCreateIn {
  title: string;
  body: string;
  involved_student_ids: string[];
  incident_date: string;
}

// ── 学年更新 / 学生自设番号（对齐 schemas.py 1566-1627）— 6-05 学生自设方案 ──
// 端点：POST /students/renewal-start（开闸）/ GET /students/renewal-progress / POST /accounts/{id}/renew-seat（老师兜底）
export interface RenewalStartIn {
  dry_run: boolean;
}

export interface RenewalStartEntry {
  student_id: string;
  student_no: string;
  name: string;
  grade_code: string;
  action: "notify" | "graduate";
}

export interface RenewalStartOut {
  dry_run: boolean;
  notify_count: number;
  graduate_count: number;
  total_affected: number;
  entries: RenewalStartEntry[];
}

export interface RenewalProgressItem {
  id: string;
  student_no: string;
  name: string;
  grade_code: string;
  class_code: string;
  seat_no: string;
}

export interface RenewalProgressOut {
  pending_count: number;
  items: RenewalProgressItem[];
}

// 对齐 TeacherRenewSeatIn(1621-1627)
export interface TeacherRenewSeatIn {
  grade_code: string;
  class_code: string;
  seat_no: string;
}

// ── 代録（老师代学生提出寮届）请求体 ──
// 跟学生侧一样的 kind 分型结构（帰省 / 外泊 / 帰国）
export interface ApplicationCreateBody {
  kind: "帰省" | "外泊" | "帰国";
  reason?: string | null;
  leave_date: string;
  leave_method: string;
  leave_time: string;
  return_date: string;
  return_method: string;
  return_time: string;
  contact_phone?: string | null;
  meal_note?: string | null;
  stay_locations?: StayLocation[] | null;
  meals_skip?: MealSkip[] | null;
  companion?: string | null;
  dest_cities?: string | null;
  flight_dep_air?: string | null;
  flight_dep_at?: string | null;
  flight_arr_air?: string | null;
  flight_arr_at?: string | null;
  taxi_reservation_time?: string | null;
  bus_route_id?: string | null;
}

// ── WebSocket helper ──
export type WSStatus = "connecting" | "connected" | "disconnected" | "failed";

export interface TeacherWSHandle {
  close: () => void;
  getStatus: () => WSStatus;
  readonly readyState: number;
}

// ── 老师通知中心（阶段1）— 对齐后端 schemas.py NotificationItem / NotificationFeedOut ──
export interface NotificationItem {
  id: string;
  // application=出寮届 / demerit=扣分 / rollcall_report=点呼上报 /
  // 阶段2 新增：outing 外出 / study_absence 学习缺席 / study_online 在线学习 /
  // dorm_event 行事企划 / fridge 冰箱 / item 物品 / disclosure 指导开示 / misc 杂项
  category: string;
  title: string;
  body: string;
  related_student_id: string | null;
  event_at: string;
  is_read: boolean;
}

export interface NotificationFeedOut {
  items: NotificationItem[];
  unread_count: number;
}

export interface NotificationUnreadCountOut {
  unread_count: number;
}
