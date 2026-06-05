// 后端 API 请求/响应类型 —— 对齐 backend schemas.py + 01_specs FIELD_REGISTRY。
// 核心类型从归档 client_5-27_类型参考.ts 复用（已对齐 iOS NetworkModels + schemas）。
// 标注「阶段3 核对」的新接口类型据 client.js 注释推断，搬对应页面时跟 schemas.py 精校。

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
// backend ApplicationOut.status 6 值
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

export interface StayLocation {
  date: string;
  location: string;
  contact?: string | null;
}

export interface MealSkip {
  date: string;
  meal: "朝食" | "昼食" | "夕食";
}

export interface Application {
  id: string;
  student_id: string;
  student: StudentBrief | null;
  kind: "帰省" | "外泊" | "帰国";
  reason: string | null;
  leave_date: string;
  leave_method: string;
  leave_time: string;
  return_date: string;
  return_method: string;
  return_time: string;
  stay_locations: StayLocation[] | null;
  meals_skip: MealSkip[] | null;
  flight_dep_air: string | null;
  flight_dep_at: string | null;
  flight_arr_air: string | null;
  flight_arr_at: string | null;
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

// ── 学習出席 ──
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
  reason: string;
  submitted_at: string;
  status: "pending" | "approved" | "rejected";
  decided_by: string | null;
  decided_at: string | null;
  comment: string | null;
}

// 学習対象名簿 在籍者（阶段3 核对 schemas.py StudyRoster*）
export interface StudyRosterItem {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
}

// ── 点呼 ──
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

export interface RollCallBoardEntry {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  base_status: "init" | "present" | "late" | "absent" | "exempt_range";
  checked_in_at: string | null;
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

// 教师改判单条 event 后返回（阶段3 核对 schemas.py RollCallEventOut）
export interface RollCallEventOut {
  id: string;
  student_id: string;
  status: string;
  reason: string | null;
  evidence: string | null;
  updated_at: string;
}

// ── 教员账户 ──
export interface TeacherOut {
  id: string;
  login_id: string;
  name: string;
  email: string;
  role: string;
  assigned_dorm: number | null;
  status: string;
  created_at: string;
}

// 登录页第 1 屏无认证用（最小字段）
export interface TeacherPublic {
  id: string;
  name: string;
  assigned_dorm: number | null;
  last_login_at: string | null;
}

export interface TeacherCreateIn {
  login_id: string;
  name: string;
  email: string;
  password: string;
  role: string;
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

// ── 扣分 / 規律処分（阶段3 核对 schemas.py Demerit*）──
export interface DisciplineRankingEntry {
  student_id: string;
  student_no: string;
  name: string;
  room_no: string;
  dorm_unit: number;
  total_points: number;
  rank: number;
}

export interface DisciplineRankingOut {
  month: string;
  entries: DisciplineRankingEntry[];
}

export interface DemeritEvent {
  id: string;
  student_id: string;
  points: number;
  reason: string;
  source_type: string;
  created_at: string;
  revoked_at: string | null;
}

export interface ManualDemeritIn {
  student_id: string;
  points: number;
  reason: string;
}

// ── 学生账号管理（阶段3 核对 schemas.py StudentOut）──
export interface StudentAccount {
  id: string;
  student_no: string;
  name: string;
  dorm_unit: number;
  room_no: string;
  is_overseas: boolean;
  status: string;
  locked: boolean;
  failed_login_count: number;
  email: string | null;
  last_login_at: string | null;
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

// ── 行事予定（阶段3 核对 schemas.py Event*）──
export interface EventItem {
  id: string;
  title: string;
  category: string;
  event_date: string;
  start_at: string | null;
  end_at: string | null;
  description: string | null;
}

export interface EventCreateIn {
  title: string;
  category: string;
  event_date: string;
  start_at?: string;
  end_at?: string;
  description?: string;
}

// ── 巴士时刻表（阶段3 核对 schemas.py BusRoute*）──
export interface BusRoute {
  id: string;
  kind: "daily_commute" | "dorm_special";
  name: string;
  direction: string;
  schedule_at: string;
  arrival_at: string | null;
  visible_to: string | null;
  note: string | null;
  deprecated: boolean;
}

export interface BusRouteCreateIn {
  kind: string;
  name: string;
  direction: string;
  schedule_at: string;
  arrival_at?: string;
  visible_to?: string;
  note?: string;
}

// ── 清扫安排（阶段3 核对 schemas.py Cleaning*）──
export interface CleaningItem {
  id: string;
  scheduled_date: string;
  area: string;
  assignee_student_ids: string[];
  status: string;
  inspected_at: string | null;
  inspector_id: string | null;
  result: string | null;
}

export interface CleaningCreateIn {
  scheduled_date: string;
  area: string;
  assignee_student_ids: string[];
}

export interface CleaningInspectIn {
  result: "passed" | "failed";
  note?: string;
}

// ── 前台业务（宅配 / 失物，阶段3 核对 schemas.py FrontDesk*）──
export interface FrontDeskItem {
  id: string;
  kind: "delivery" | "lost_and_found";
  title: string;
  description: string | null;
  owner_student_id: string | null;
  status: string;
  created_at: string;
  expires_at: string | null;
  notified_at: string | null;
  picked_up_at: string | null;
}

export interface FrontDeskCreateIn {
  kind: string;
  title: string;
  description?: string;
  owner_student_id?: string;
}

// ── 学生个人档案聚合（阶段3 核对 schemas.py StudentProfileOut）──
export interface StudentProfile {
  student: StudentAccount;
  applications: Application[];
  study_checkins: unknown[];
  rollcall_events: unknown[];
  guidance_records: GuidanceItem[];
  demerit_events: DemeritEvent[];
}

// ── 指導履歴（阶段3 核对 schemas.py Guidance*）──
export interface GuidanceItem {
  id: string;
  student_id: string;
  content: string;
  category: string | null;
  guidance_date: string;
  confidential: boolean;
  author_teacher_id: string;
  created_at: string;
}

export interface GuidanceCreateIn {
  student_id: string;
  content: string;
  category?: string;
  guidance_date: string;
  confidential: boolean;
}

// ── 開示申請（阶段3 核对 schemas.py Disclosure*）──
export interface DisclosureRequest {
  id: string;
  student_id: string;
  student_name: string;
  reason: string;
  status: string;
  submitted_at: string;
  decided_at: string | null;
  decision_note: string | null;
}

export interface DisclosureDecisionIn {
  decision: "approved_full" | "approved_partial" | "rejected";
  decision_note?: string;
  visible_from?: string;
  visible_until?: string;
}

// ── 事案録入（阶段3 核对 schemas.py Incident*）──
export interface IncidentItem {
  id: string;
  title: string;
  incident_date: string;
  involved_student_ids: string[];
  created_at: string;
}

export interface IncidentDetail extends IncidentItem {
  body: string;
}

export interface IncidentCreateIn {
  title: string;
  body: string;
  involved_student_ids: string[];
  incident_date: string;
}

// ── 学号一括进级（阶段3 核对 schemas.py BulkPromote*）──
export interface PromoteEntry {
  student_id: string;
  student_no: string;
  name: string;
  old_grade_code: string;
  new_grade_code: string;
  action: string;
  old_status: string;
  new_status: string;
}

export interface PromoteResult {
  dry_run: boolean;
  promote_count: number;
  graduate_count: number;
  total_affected: number;
  entries: PromoteEntry[];
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
  stay_locations?: StayLocation[] | null;
  meals_skip?: MealSkip[] | null;
  flight_dep_air?: string | null;
  flight_dep_at?: string | null;
  flight_arr_air?: string | null;
  flight_arr_at?: string | null;
  bus_route_id?: string | null;
}

// ── WebSocket helper ──
export type WSStatus = "connecting" | "connected" | "disconnected" | "failed";

export interface TeacherWSHandle {
  close: () => void;
  getStatus: () => WSStatus;
  readonly readyState: number;
}
