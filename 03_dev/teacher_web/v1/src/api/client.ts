/**
 * Tomoshibi Teacher Web — API client.
 * Base URL = /api/v1 (Vite proxy → localhost:8000)
 */

const BASE = "/api/v1";

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw { status: res.status, ...(err?.error ?? err?.detail ?? err) };
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Auth
  teacherLogin: (login_id: string, password: string) =>
    request<{ access_token: string; teacher: import("../store/auth").TeacherProfile }>(
      "POST", "/sessions/teacher", { login_id, password }
    ),

  // Applications
  pendingForMe: (token: string) =>
    request<Application[]>("GET", "/applications/pending-for-me", undefined, token),

  getApplication: (id: string, token: string) =>
    request<Application>("GET", `/applications/${id}`, undefined, token),

  decide: (id: string, decision: "approve" | "reject", comment: string | undefined, token: string) =>
    request<Application>("POST", `/applications/${id}/approvals`, { decision, comment }, token),

  getAuditLog: (id: string, token: string) =>
    request<AuditEntry[]>("GET", `/applications/${id}/audit`, undefined, token),

  // Study
  studyTodayAttendees: (token: string) =>
    request<StudyTodayOut>("GET", "/study/today/attendees", undefined, token),

  studyCheckin: (student_id: string, token: string) =>
    request<StudyCheckinOut>("POST", "/study/checkins", { student_id }, token),

  studyFinalize: (token: string) =>
    request<{ finalized_count: number }>("POST", "/study/checkins/bulk-finalize", {}, token),

  absenceRequests: (token: string, target_date?: string) =>
    request<StudyAbsenceRequestOut[]>(
      "GET",
      `/study/absence-requests${target_date ? `?target_date=${target_date}` : ""}`,
      undefined,
      token
    ),

  decideAbsence: (
    id: string,
    decision: "approved" | "rejected",
    comment: string | undefined,
    token: string
  ) =>
    request<StudyAbsenceRequestOut>(
      "POST",
      `/study/absence-requests/${id}/decision`,
      { decision, comment },
      token
    ),

  cancelToday: (token: string) =>
    request<{ cancelled_count: number }>("POST", "/study/cancel-today", {}, token),

  // Rollcall
  rollcallTodaySessions: (token: string) =>
    request<RollCallSessionOut[]>("GET", "/rollcall/today/sessions", undefined, token),

  rollcallStart: (session_id: string, token: string) =>
    request<RollCallSessionOut>("POST", `/rollcall/sessions/${session_id}/start`, {}, token),

  rollcallEnd: (session_id: string, token: string) =>
    request<RollCallSessionOut>("POST", `/rollcall/sessions/${session_id}/end`, {}, token),

  rollcallBoard: (session_id: string, token: string) =>
    request<RollCallBoardOut>("GET", `/rollcall/sessions/${session_id}/board`, undefined, token),

  rollcallSummary: (session_id: string, token: string) =>
    request<RollCallSummaryOut>("GET", `/rollcall/sessions/${session_id}/summary`, undefined, token),

  // Teachers
  listTeachers: (token: string) =>
    request<TeacherOut[]>("GET", "/teachers/", undefined, token),

  createInvitation: (body: InvitationIn, token: string) =>
    request<InvitationOut>("POST", "/teachers/invitations", body, token),
};

// ── 型定義 ──────────────────────────────────────────

export type AppStatus = "pending" | "approved_partial" | "approved" | "rejected" | "withdrawn";

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
  submitted_at: string;
  status: AppStatus;
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
  summary: { expected: number; checked_in: number; late: number; absent: number };
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
