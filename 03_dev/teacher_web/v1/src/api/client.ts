// Tomoshibi 老师网站 — API client（TypeScript ES 模块版）
//
// 从 client.js 转来：去掉 IIFE 包装 + window.tomoshibiApi 挂载，改 ES export + 加泛型类型。
// BASE 用 theme 的 API_BASE（同 origin 部署直接生效，dev 走 vite proxy /api→8000）。
//
// 用法（任意组件）：
//   import { api } from "../api/client";
//   const apps = await api.pendingForMe(token);
//
// 错误约定：request 把后端响应信封 {error|detail|...} 铺平到抛出对象顶层 —— 组件用 e.code / e.message / e.status。

import { API_BASE } from "../theme";
import type {
  TeacherLoginOut,
  Application,
  AuditEntry,
  StudentBrief,
  ApplicationCreateBody,
  StudyTodayOut,
  StudyCheckinOut,
  StudyAbsenceRequestOut,
  StudyRosterItem,
  RollCallSessionOut,
  RollCallBoardOut,
  RollCallSummaryOut,
  RollCallEventOut,
  TeacherOut,
  TeacherPublic,
  TeacherCreateIn,
  InvitationIn,
  InvitationOut,
  AnnouncementBrief,
  AnnouncementDetail,
  AnnouncementReplyOut,
  AnnouncementCreateIn,
  RegistrationCode,
  DisciplineRankingOut,
  DemeritEvent,
  ManualDemeritIn,
  StudentAccountListOut,
  PasswordResetOut,
  SimpleMessageOut,
  EventItem,
  EventCreateIn,
  EventListOut,
  BusRoute,
  BusRouteCreateIn,
  BusRouteListOut,
  CleaningItem,
  CleaningCreateIn,
  CleaningInspectIn,
  FrontDeskItem,
  FrontDeskCreateIn,
  StudentProfile,
  GuidanceItem,
  GuidanceCreateIn,
  DisclosureRequest,
  DisclosureDecisionIn,
  IncidentItem,
  IncidentDetail,
  IncidentCreateIn,
  RenewalStartIn,
  RenewalStartOut,
  RenewalProgressOut,
  TeacherRenewSeatIn,
  RenewSeatOut,
  WSStatus,
  TeacherWSHandle,
} from "./types";

// 401 全局拦截回调（§11.5 W3）：App mount 时注册 logout
let onUnauthorized: (() => void) | null = null;
export function setOnUnauthorized(cb: () => void): void {
  onUnauthorized = cb;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  token?: string | null,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const wrapped: Record<string, unknown> = { status: res.status };
    // 后端响应统一信封: {error: {...}} | {detail: '...'} | raw
    const inner = err && (err.error || err.detail || err);
    if (inner && typeof inner === "object") Object.assign(wrapped, inner);
    else wrapped.message = inner;
    // 401 全局拦截：通知 App 强制 logout
    if (res.status === 401 && onUnauthorized) {
      try {
        onUnauthorized();
      } catch {
        /* 钩子内部错误不要影响 throw */
      }
    }
    throw wrapped;
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  setOnUnauthorized,

  // ── Auth ──
  // 实名账户登录：优先 teacher_id（UUID）登录；login_id 形式作 backward-compat。
  teacherLogin: (body: {
    teacher_id?: string;
    login_id?: string;
    password: string;
  }) => request<TeacherLoginOut>("POST", "/sessions/teacher", body),

  // ── Applications ──
  pendingForMe: (token: string) =>
    request<Application[]>(
      "GET",
      "/applications/pending-for-me",
      undefined,
      token,
    ),
  getApplication: (id: string, token: string) =>
    request<Application>("GET", `/applications/${id}`, undefined, token),
  decide: (
    id: string,
    decision: "approve" | "reject",
    comment: string | undefined,
    token: string,
  ) =>
    request<Application>(
      "POST",
      `/applications/${id}/approvals`,
      { decision, comment },
      token,
    ),
  getAuditLog: (id: string, token: string) =>
    request<AuditEntry[]>("GET", `/applications/${id}/audit`, undefined, token),
  // 出寮者一覧 — 当天在出寮期间内、已承认的届（按老师寮边界过滤）
  activeLeaves: (token: string, date?: string) =>
    request<Application[]>(
      "GET",
      "/applications/active" +
        (date ? "?date=" + encodeURIComponent(date) : ""),
      undefined,
      token,
    ),
  // 代録 — 搜可代録的学生（按老师寮边界 + 限代録 5 角色）
  proxyCandidates: (token: string, q?: string) =>
    request<StudentBrief[]>(
      "GET",
      "/applications/proxy-candidates" +
        (q ? "?q=" + encodeURIComponent(q) : ""),
      undefined,
      token,
    ),
  // 代録 — 提交老师代学生的出寮届
  createByTeacher: (
    student_id: string,
    body: ApplicationCreateBody,
    token: string,
  ) =>
    request<Application>(
      "POST",
      "/applications/by-teacher?student_id=" + encodeURIComponent(student_id),
      body,
      token,
    ),

  // ── Study ──
  studyTodayAttendees: (token: string) =>
    request<StudyTodayOut>("GET", "/study/today/attendees", undefined, token),
  studyCheckin: (student_id: string, token: string) =>
    request<StudyCheckinOut>("POST", "/study/checkins", { student_id }, token),
  studyFinalize: (token: string) =>
    request<{ finalized_count: number }>(
      "POST",
      "/study/checkins/bulk-finalize",
      {},
      token,
    ),
  absenceRequests: (token: string, target_date?: string) =>
    request<StudyAbsenceRequestOut[]>(
      "GET",
      `/study/absence-requests${
        target_date ? `?target_date=${target_date}` : ""
      }`,
      undefined,
      token,
    ),
  decideAbsence: (
    id: string,
    decision: "approved" | "rejected",
    comment: string | undefined,
    token: string,
  ) =>
    request<StudyAbsenceRequestOut>(
      "POST",
      `/study/absence-requests/${id}/decision`,
      { decision, comment },
      token,
    ),
  cancelToday: (token: string) =>
    request<{ cancelled_count: number }>(
      "POST",
      "/study/cancel-today",
      {},
      token,
    ),

  // ── 学習対象名簿 管理 ──
  studyRoster: (token: string) =>
    request<StudyRosterItem[]>("GET", "/study/roster", undefined, token),
  studyRosterAdd: (
    body: { student_no?: string; student_id?: string },
    token: string,
  ) => request<StudyRosterItem>("POST", "/study/roster", body, token),
  studyRosterRemove: (student_id: string, token: string) =>
    request<void>("DELETE", `/study/roster/${student_id}`, undefined, token),

  // ── Rollcall ──
  rollcallTodaySessions: (token: string) =>
    request<RollCallSessionOut[]>(
      "GET",
      "/rollcall/today/sessions",
      undefined,
      token,
    ),
  rollcallStart: (session_id: string, token: string) =>
    request<RollCallSessionOut>(
      "POST",
      `/rollcall/sessions/${session_id}/start`,
      {},
      token,
    ),
  rollcallEnd: (session_id: string, token: string) =>
    request<RollCallSessionOut>(
      "POST",
      `/rollcall/sessions/${session_id}/end`,
      {},
      token,
    ),
  rollcallBoard: (session_id: string, token: string) =>
    request<RollCallBoardOut>(
      "GET",
      `/rollcall/sessions/${session_id}/board`,
      undefined,
      token,
    ),
  rollcallSummary: (session_id: string, token: string) =>
    request<RollCallSummaryOut>(
      "GET",
      `/rollcall/sessions/${session_id}/summary`,
      undefined,
      token,
    ),
  // 历史列表 — RecordsPage 用（from/to 是 YYYY-MM-DD，不传默认过去 7 天）
  rollcallSessionsHistory: (token: string, from?: string, to?: string) => {
    const q: string[] = [];
    if (from) q.push(`from=${encodeURIComponent(from)}`);
    if (to) q.push(`to=${encodeURIComponent(to)}`);
    const qs = q.length ? `?${q.join("&")}` : "";
    return request<RollCallSessionOut[]>(
      "GET",
      `/rollcall/sessions${qs}`,
      undefined,
      token,
    );
  },
  // 教师改判单条 event — OverrideModal 调（后端自动跑改判扣分联动 + WS broadcast）
  patchRollcallEvent: (
    event_id: string,
    body: { to_status: string; reason: string; evidence?: string },
    token: string,
  ) =>
    request<RollCallEventOut>(
      "PATCH",
      `/rollcall/events/${event_id}`,
      body,
      token,
    ),

  // ── Teachers ──
  listTeachersPublic: () =>
    request<TeacherPublic[]>("GET", "/teachers/public", undefined),
  listTeachers: (token: string) =>
    request<TeacherOut[]>("GET", "/teachers/", undefined, token),
  createInvitation: (body: InvitationIn, token: string) =>
    request<InvitationOut>("POST", "/teachers/invitations", body, token),
  createTeacher: (body: TeacherCreateIn, token: string) =>
    request<TeacherOut>("POST", "/teachers/", body, token),
  deleteTeacher: (teacher_id: string, token: string) =>
    request<void>("DELETE", `/teachers/${teacher_id}`, undefined, token),

  // ── Announcements ──
  listAnnouncements: (token: string) =>
    request<{ items: AnnouncementBrief[] }>(
      "GET",
      "/announcements",
      undefined,
      token,
    ),
  getAnnouncement: (id: string, token: string) =>
    request<AnnouncementDetail>(
      "GET",
      `/announcements/${id}`,
      undefined,
      token,
    ),
  createAnnouncement: (body: AnnouncementCreateIn, token: string) =>
    request<AnnouncementDetail>("POST", "/announcements", body, token),
  updateAnnouncement: (
    id: string,
    body: Partial<AnnouncementCreateIn>,
    token: string,
  ) =>
    request<AnnouncementDetail>("PATCH", `/announcements/${id}`, body, token),
  deleteAnnouncement: (id: string, token: string) =>
    request<void>("DELETE", `/announcements/${id}`, undefined, token),
  getAnnouncementUnreadCount: (token: string) =>
    request<{ unread_count: number }>(
      "GET",
      "/announcements/unread-count",
      undefined,
      token,
    ),
  postAnnouncementReply: (
    announcementId: string,
    body: { body: string },
    token: string,
  ) =>
    request<AnnouncementReplyOut>(
      "POST",
      `/announcements/${announcementId}/replies`,
      body,
      token,
    ),
  deleteAnnouncementReply: (
    announcementId: string,
    replyId: string,
    token: string,
  ) =>
    request<void>(
      "DELETE",
      `/announcements/${announcementId}/replies/${replyId}`,
      undefined,
      token,
    ),

  // ── 学生登録码（admin）──
  getRegistrationCodeCurrent: (token: string) =>
    request<RegistrationCode>(
      "GET",
      "/admin/registration-code/current",
      undefined,
      token,
    ),
  refreshRegistrationCode: (token: string) =>
    request<RegistrationCode>(
      "POST",
      "/admin/registration-code/refresh",
      {},
      token,
    ),

  // ── 扣分 / 規律処分 ──
  getDisciplineRanking: (token: string, month: string) =>
    request<DisciplineRankingOut>(
      "GET",
      `/discipline/ranking?month=${encodeURIComponent(month)}`,
      undefined,
      token,
    ),
  createManualDemerit: (body: ManualDemeritIn, token: string) =>
    request<DemeritEvent>("POST", "/discipline/manual", body, token),
  revokeDemerit: (
    event_id: string,
    body: { revoke_reason: string },
    token: string,
  ) =>
    request<DemeritEvent>(
      "POST",
      `/discipline/${event_id}/revoke`,
      body,
      token,
    ),

  // ── Accounts（学生账号管理）──
  listStudents: (
    params: { q?: string; dorm_unit?: number; status?: string } | undefined,
    token: string,
  ) => {
    const q: string[] = [];
    if (params && params.q) q.push(`q=${encodeURIComponent(params.q)}`);
    if (params && params.dorm_unit != null)
      q.push(`dorm_unit=${encodeURIComponent(params.dorm_unit)}`);
    if (params && params.status)
      q.push(`status=${encodeURIComponent(params.status)}`);
    const qs = q.length ? `?${q.join("&")}` : "";
    return request<StudentAccountListOut>(
      "GET",
      `/students${qs}`,
      undefined,
      token,
    );
  },
  resetStudentPassword: (studentId: string, token: string) =>
    request<PasswordResetOut>(
      "POST",
      `/accounts/${studentId}/password-reset`,
      undefined,
      token,
    ),
  unlockStudentAccount: (studentId: string, token: string) =>
    request<SimpleMessageOut>(
      "POST",
      `/accounts/${studentId}/unlock`,
      undefined,
      token,
    ),

  // ── 行事予定 ──
  listEvents: (token: string, from_date?: string, to_date?: string) => {
    const q: string[] = [];
    if (from_date) q.push(`from_date=${encodeURIComponent(from_date)}`);
    if (to_date) q.push(`to_date=${encodeURIComponent(to_date)}`);
    const qs = q.length ? `?${q.join("&")}` : "";
    return request<EventListOut>("GET", `/events${qs}`, undefined, token);
  },
  createEvent: (body: EventCreateIn, token: string) =>
    request<EventItem>("POST", "/events", body, token),
  updateEvent: (id: string, body: Partial<EventCreateIn>, token: string) =>
    request<EventItem>("PATCH", `/events/${id}`, body, token),
  deleteEvent: (id: string, token: string) =>
    request<void>("DELETE", `/events/${id}`, undefined, token),

  // ── 巴士时刻表 ──
  listBusRoutes: (token: string, kind?: string) => {
    const qs = kind ? `?kind=${encodeURIComponent(kind)}` : "";
    return request<BusRouteListOut>(
      "GET",
      `/bus/routes${qs}`,
      undefined,
      token,
    );
  },
  createBusRoute: (body: BusRouteCreateIn, token: string) =>
    request<BusRoute>("POST", "/bus/routes", body, token),
  updateBusRoute: (
    id: string,
    body: Partial<BusRouteCreateIn> & { deprecated?: boolean },
    token: string,
  ) => request<BusRoute>("PATCH", `/bus/routes/${id}`, body, token),
  deleteBusRoute: (id: string, token: string) =>
    request<void>("DELETE", `/bus/routes/${id}`, undefined, token),

  // ── 清扫安排 ──
  listCleaning: (token: string, scheduledDate: string) =>
    request<CleaningItem[]>(
      "GET",
      `/cleaning?scheduled_date=${encodeURIComponent(scheduledDate)}`,
      undefined,
      token,
    ),
  createCleaning: (body: CleaningCreateIn, token: string) =>
    request<CleaningItem>("POST", "/cleaning", body, token),
  inspectCleaning: (id: string, body: CleaningInspectIn, token: string) =>
    request<CleaningItem>("POST", `/cleaning/${id}/inspect`, body, token),

  // ── 前台业务（宅配 + 失物）──
  listFrontDesk: (token: string, kind?: string) => {
    const q = kind ? `?kind=${encodeURIComponent(kind)}` : "";
    return request<FrontDeskItem[]>("GET", `/front-desk${q}`, undefined, token);
  },
  createFrontDesk: (body: FrontDeskCreateIn, token: string) =>
    request<FrontDeskItem>("POST", "/front-desk", body, token),
  notifyFrontDesk: (id: string, token: string) =>
    request<FrontDeskItem>("POST", `/front-desk/${id}/notify`, {}, token),
  pickupFrontDesk: (id: string, token: string) =>
    request<FrontDeskItem>("POST", `/front-desk/${id}/picked-up`, {}, token),

  // ── 学生个人档案聚合 ──
  getStudentProfile: (studentId: string, token: string, limit?: number) => {
    const qs = limit ? `?limit=${encodeURIComponent(limit)}` : "";
    return request<StudentProfile>(
      "GET",
      `/students/${studentId}/profile${qs}`,
      undefined,
      token,
    );
  },

  // ── 在线学习申请 契約書下载 ──
  // 文件 blob（照片 / PDF）；手搓 fetch 带 token（不走 request — 它只解 JSON）
  downloadOnlineContract: async (
    requestId: string,
    token: string,
  ): Promise<Blob> => {
    const res = await fetch(
      `${API_BASE}/study/online-requests/${requestId}/contract`,
      { headers: token ? { Authorization: `Bearer ${token}` } : {} },
    );
    if (!res.ok) {
      if (res.status === 401 && onUnauthorized) {
        try {
          onUnauthorized();
        } catch {
          /* 钩子内部错误不要影响 throw */
        }
      }
      throw { status: res.status };
    }
    return res.blob();
  },

  // ── 食堂用「食数表」导出 ──
  // .xlsx blob，手搓 fetch 带 token（不走 request）+ 触发浏览器下载
  downloadMealsExport: async (
    from: string,
    to: string,
    token: string,
  ): Promise<void> => {
    const qs = new URLSearchParams();
    qs.set("from", from);
    qs.set("to", to);
    const res = await fetch(`${API_BASE}/meals/export?${qs.toString()}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      if (res.status === 401 && onUnauthorized) {
        try {
          onUnauthorized();
        } catch {
          /* 钩子内部错误不要影响 throw */
        }
      }
      throw { status: res.status };
    }
    const blob = await res.blob();
    const cd = res.headers.get("Content-Disposition") || "";
    const m = cd.match(/filename="?([^"]+)"?/);
    const filename = m ? m[1] : "meals.xlsx";
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  // ── 指導履歴 ──
  createGuidance: (studentId: string, body: GuidanceCreateIn, token: string) =>
    request<GuidanceItem>(
      "POST",
      `/students/${studentId}/guidance`,
      body,
      token,
    ),
  listGuidance: (studentId: string, token: string) =>
    request<{ items: GuidanceItem[] }>(
      "GET",
      `/students/${studentId}/guidance`,
      undefined,
      token,
    ),
  listDisclosureRequests: (token: string) =>
    request<{ items: DisclosureRequest[] }>(
      "GET",
      "/guidance/disclosure-requests",
      undefined,
      token,
    ),
  decideDisclosure: (
    requestId: string,
    body: DisclosureDecisionIn,
    token: string,
  ) =>
    request<DisclosureRequest>(
      "POST",
      `/guidance/disclosure-requests/${requestId}/decision`,
      body,
      token,
    ),

  // ── 事案録入 ──
  listIncidents: (token: string) =>
    request<{ items: IncidentItem[] }>("GET", "/incidents", undefined, token),
  createIncident: (body: IncidentCreateIn, token: string) =>
    request<IncidentDetail>("POST", "/incidents", body, token),
  getIncident: (id: string, token: string) =>
    request<IncidentDetail>("GET", `/incidents/${id}`, undefined, token),
  updateIncident: (
    id: string,
    body: Partial<IncidentCreateIn>,
    token: string,
  ) => request<IncidentDetail>("PATCH", `/incidents/${id}`, body, token),
  deleteIncident: (id: string, token: string) =>
    request<void>("DELETE", `/incidents/${id}`, undefined, token),

  // ── 学年更新 / 学生自设番号（6-05 学生自设方案，推翻 5-30 老师代改）──
  // 开闸：中1~高2 打 needs_renewal 标记 + 高3 毕业，不直接改番号。body={dry_run}
  startRenewal: (body: RenewalStartIn, token: string) =>
    request<RenewalStartOut>("POST", "/students/renewal-start", body, token),
  // 进度：老师看谁还没自设番号（needs_renewal=true）
  renewalProgress: (token: string) =>
    request<RenewalProgressOut>(
      "GET",
      "/students/renewal-progress",
      undefined,
      token,
    ),
  // 老师单件改某学生番号（兜底 — 学生不会操作 / 填错时）。撞号返 422 STUDENT_NO_TAKEN
  teacherRenewSeat: (
    studentId: string,
    body: TeacherRenewSeatIn,
    token: string,
  ) =>
    request<RenewSeatOut>(
      "POST",
      `/accounts/${studentId}/renew-seat`,
      body,
      token,
    ),

  // ── WebSocket helper (/ws/teacher 收 checkin / outstay_new 事件) ──
  // 用法: const handle = api.openTeacherWS(token, onMessage, onStatus?)
  // 重连策略 — 指数退避 1s/2s/4s/8s/16s/30s 封顶，最多 8 次；close() 后不再重连
  openTeacherWS: (
    token: string,
    onMessage: (data: unknown) => void,
    onStatus?: (s: WSStatus) => void,
  ): TeacherWSHandle => {
    let wsUrl: string;
    if (API_BASE.startsWith("http")) {
      wsUrl = API_BASE.replace(/^http/, "ws") + "/ws/teacher";
    } else {
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${proto}//${location.host}${API_BASE}/ws/teacher`;
    }
    const fullUrl = `${wsUrl}?token=${encodeURIComponent(token)}`;

    const MAX_ATTEMPTS = 8;
    const BACKOFF_MS = [1000, 2000, 4000, 8000, 16000, 30000, 30000, 30000];

    let ws: WebSocket | null = null;
    let closedByUser = false;
    let attempt = 0;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;
    let currentStatus: WSStatus = "connecting";

    const setStatus = (s: WSStatus) => {
      currentStatus = s;
      if (typeof onStatus === "function") {
        try {
          onStatus(s);
        } catch (e) {
          console.error("[tomoshibiApi WS] onStatus callback error", e);
        }
      }
    };

    const connect = () => {
      if (closedByUser) return;
      setStatus("connecting");
      try {
        ws = new WebSocket(fullUrl);
      } catch (e) {
        console.error("[tomoshibiApi WS] new WebSocket throw", e);
        scheduleReconnect();
        return;
      }
      ws.addEventListener("open", () => {
        attempt = 0;
        setStatus("connected");
      });
      ws.addEventListener("message", (ev: MessageEvent) => {
        try {
          onMessage(JSON.parse(ev.data));
        } catch (e) {
          console.error("[tomoshibiApi WS] parse error", e, ev.data);
        }
      });
      ws.addEventListener("error", (e) => {
        console.warn("[tomoshibiApi WS] error", e);
      });
      ws.addEventListener("close", (ev: CloseEvent) => {
        if (closedByUser) return;
        console.warn(
          `[tomoshibiApi WS] closed code=${ev.code} reason=${ev.reason} → reconnect`,
        );
        setStatus("disconnected");
        scheduleReconnect();
      });
    };

    const scheduleReconnect = () => {
      if (closedByUser) return;
      if (attempt >= MAX_ATTEMPTS) {
        setStatus("failed");
        console.error(
          `[tomoshibiApi WS] reconnect 放弃（已尝试 ${MAX_ATTEMPTS} 次）`,
        );
        return;
      }
      const delay = BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)];
      attempt += 1;
      console.warn(`[tomoshibiApi WS] ${delay}ms 后第 ${attempt} 次重连...`);
      retryTimer = setTimeout(connect, delay);
    };

    connect();

    return {
      close: () => {
        closedByUser = true;
        if (retryTimer) clearTimeout(retryTimer);
        if (ws && ws.readyState !== WebSocket.CLOSED) ws.close();
        setStatus("disconnected");
      },
      getStatus: () => currentStatus,
      get readyState() {
        return ws ? ws.readyState : WebSocket.CLOSED;
      },
    };
  },
};

export default api;
