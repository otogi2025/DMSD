/**
 * Tomoshibi Teacher Web — API client (standalone JS 版)
 *
 * 从 client.ts 转过来 — 删 TS 类型 + 改 import("../store/auth") 死链 + 暴露到 window.tomoshibiApi。
 * standalone HTML 不编译 TS，所以这个文件是当前真接口对接路径上唯一被加载的 client。
 *
 * 用法（任意组件里）:
 *   const data = await window.tomoshibiApi.teacherLogin('tomoshibi', '...');
 *   const apps = await window.tomoshibiApi.pendingForMe(token);
 *
 * BASE URL — 通过 window.API_BASE 全局配置（index.html 顶部定义）。
 * 默认 '/api/v1'（同 origin 部署 — FastAPI StaticFiles 时直接生效）。
 * standalone 单跑（python -m http.server 8787）时 itsuki 把 API_BASE 改成绝对 URL
 * 'http://localhost:8000/api/v1' 并 backend 开 CORS（FastAPI middleware）。
 *
 * Endpoint 全集 26 个（按 backend FastAPI routers 分类）：
 *   Auth         — teacherLogin
 *   Applications — pendingForMe / getApplication / decide / getAuditLog
 *   Study        — studyTodayAttendees / studyCheckin / studyFinalize /
 *                  absenceRequests / decideAbsence / cancelToday
 *   Rollcall     — rollcallTodaySessions / rollcallStart / rollcallEnd /
 *                  rollcallBoard / rollcallSummary
 *   Teachers     — listTeachers / createInvitation
 *   Announcements— listAnnouncements / getAnnouncement / createAnnouncement /
 *                  deleteAnnouncement
 *
 * cross-ref:
 *   - 源 ts 文件: src/api/client.ts（仍保留，未来 TS 重构时复用）
 *   - 字段定义: backend/v1/app/schemas.py + 01_specs/rollcall/FIELD_REGISTRY.md
 *   - FC-025/026/027 字段对齐: itsuki 5-26 TODO §L 标 N/A，真接口对接时重新审视
 */

(function () {
  "use strict";

  async function request(method, path, body, token) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const base = window.API_BASE || "/api/v1";
    const res = await fetch(`${base}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      const wrapped = { status: res.status };
      // 后端响应统一信封: {error: {...}} | {detail: '...'} | raw
      const inner = err && (err.error || err.detail || err);
      if (inner && typeof inner === "object") Object.assign(wrapped, inner);
      else wrapped.message = inner;
      // 401 全局拦截 (§11.5 W3 拍板)：通知 App 强制 logout
      if (res.status === 401 && typeof api._onUnauthorized === "function") {
        try {
          api._onUnauthorized();
        } catch (_) {
          /* 钩子内部错误不要影响 throw */
        }
      }
      throw wrapped;
    }
    if (res.status === 204) return undefined;
    return res.json();
  }

  const api = {
    // ── Auth ──
    teacherLogin: (login_id, password) =>
      request("POST", "/sessions/teacher", { login_id, password }),

    // ── Applications ──
    pendingForMe: (token) =>
      request("GET", "/applications/pending-for-me", undefined, token),
    getApplication: (id, token) =>
      request("GET", `/applications/${id}`, undefined, token),
    decide: (id, decision, comment, token) =>
      request(
        "POST",
        `/applications/${id}/approvals`,
        { decision, comment },
        token,
      ),
    getAuditLog: (id, token) =>
      request("GET", `/applications/${id}/audit`, undefined, token),

    // ── Study ──
    studyTodayAttendees: (token) =>
      request("GET", "/study/today/attendees", undefined, token),
    studyCheckin: (student_id, token) =>
      request("POST", "/study/checkins", { student_id }, token),
    studyFinalize: (token) =>
      request("POST", "/study/checkins/bulk-finalize", {}, token),
    absenceRequests: (token, target_date) =>
      request(
        "GET",
        `/study/absence-requests${
          target_date ? `?target_date=${target_date}` : ""
        }`,
        undefined,
        token,
      ),
    decideAbsence: (id, decision, comment, token) =>
      request(
        "POST",
        `/study/absence-requests/${id}/decision`,
        { decision, comment },
        token,
      ),
    cancelToday: (token) => request("POST", "/study/cancel-today", {}, token),

    // ── Rollcall ──
    rollcallTodaySessions: (token) =>
      request("GET", "/rollcall/today/sessions", undefined, token),
    rollcallStart: (session_id, token) =>
      request("POST", `/rollcall/sessions/${session_id}/start`, {}, token),
    rollcallEnd: (session_id, token) =>
      request("POST", `/rollcall/sessions/${session_id}/end`, {}, token),
    rollcallBoard: (session_id, token) =>
      request(
        "GET",
        `/rollcall/sessions/${session_id}/board`,
        undefined,
        token,
      ),
    rollcallSummary: (session_id, token) =>
      request(
        "GET",
        `/rollcall/sessions/${session_id}/summary`,
        undefined,
        token,
      ),
    // 5-27 新增：历史列表 — 教师 Web RecordsPage 用
    // 参数 from / to 是 YYYY-MM-DD 字符串，不传时 backend 默认过去 7 天
    rollcallSessionsHistory: (token, from, to) => {
      const q = [];
      if (from) q.push(`from=${encodeURIComponent(from)}`);
      if (to) q.push(`to=${encodeURIComponent(to)}`);
      const qs = q.length ? `?${q.join("&")}` : "";
      return request("GET", `/rollcall/sessions${qs}`, undefined, token);
    },

    // ── Teachers ──
    listTeachers: (token) => request("GET", "/teachers/", undefined, token),
    createInvitation: (body, token) =>
      request("POST", "/teachers/invitations", body, token),

    // ── Announcements (FC-027 修复完成 — get_current_principal 学生+老师双路) ──
    listAnnouncements: (token) =>
      request("GET", "/announcements", undefined, token),
    getAnnouncement: (id, token) =>
      request("GET", `/announcements/${id}`, undefined, token),
    createAnnouncement: (body, token) =>
      request("POST", "/announcements", body, token),
    updateAnnouncement: (id, body, token) =>
      request("PATCH", `/announcements/${id}`, body, token),
    deleteAnnouncement: (id, token) =>
      request("DELETE", `/announcements/${id}`, undefined, token),
    // 主页 badge — 学生 only（老师不需要未读概念）
    getAnnouncementUnreadCount: (token) =>
      request("GET", "/announcements/unread-count", undefined, token),
    // 回复 — 学生 + 老师都能调（按 JWT 自动判 author_kind）
    postAnnouncementReply: (announcementId, body, token) =>
      request("POST", `/announcements/${announcementId}/replies`, body, token),
    deleteAnnouncementReply: (announcementId, replyId, token) =>
      request(
        "DELETE",
        `/announcements/${announcementId}/replies/${replyId}`,
        undefined,
        token,
      ),

    // 学生登録码 admin 接口（§7.16 + WEB_DESIGN_LOG §11.9.1）
    // 仅寮務部長 / 寮務課長 / 管理係 三类角色返 200，其他教师 403。
    // 返回结构：{code, created_at, expires_at, expires_in_seconds}
    getRegistrationCodeCurrent: (token) =>
      request("GET", "/admin/registration-code/current", undefined, token),
    refreshRegistrationCode: (token) =>
      request("POST", "/admin/registration-code/refresh", {}, token),

    // 扣分 / 規律処分（spec §7.5 + 5-27 backend commit ac0bd90 新增）
    // DisciplinePage 接 backend 用。月排名 + 手动加 + 撤销 3 个核心端点。
    // 权限：寮監 / 寮務部長 / 寮務課長 / 管理係 4 类（学習担当除外，那扣分由 study 自动触发）
    getDisciplineRanking: (token, month) =>
      request(
        "GET",
        `/discipline/ranking?month=${encodeURIComponent(month)}`,
        undefined,
        token,
      ),
    createManualDemerit: (body, token) =>
      request("POST", "/discipline/manual", body, token),
    revokeDemerit: (event_id, body, token) =>
      request("POST", `/discipline/${event_id}/revoke`, body, token),

    // 清扫安排（spec §7.10 + 5-27 backend 新增）
    // CleaningPage 接 backend。失败自动加 DemeritEvent (source_type='cleaning_failed')。
    // 权限：寮監 / 寮務 / 管理係
    listCleaning: (token, scheduledDate) =>
      request(
        "GET",
        `/cleaning?scheduled_date=${encodeURIComponent(scheduledDate)}`,
        undefined,
        token,
      ),
    createCleaning: (body, token) => request("POST", "/cleaning", body, token),
    inspectCleaning: (id, body, token) =>
      request("POST", `/cleaning/${id}/inspect`, body, token),

    // 前台业务（spec §7.12 宅配 + 失物 + 5-27 backend 新增）
    // FrontDeskPage 接 backend。delivery 默认 7 天过期 / lost_and_found 30 天。
    // 权限：寮監 / 寮務 / 管理係
    listFrontDesk: (token, kind) => {
      const q = kind ? `?kind=${encodeURIComponent(kind)}` : "";
      return request("GET", `/front-desk${q}`, undefined, token);
    },
    createFrontDesk: (body, token) =>
      request("POST", "/front-desk", body, token),
    notifyFrontDesk: (id, token) =>
      request("POST", `/front-desk/${id}/notify`, {}, token),
    pickupFrontDesk: (id, token) =>
      request("POST", `/front-desk/${id}/picked-up`, {}, token),

    // 401 全局拦截注册（§11.5 W3 拍板）
    // App() 在 mount 时调 setOnUnauthorized(() => logout()) 注册回调。
    // 任意 API 调用收到 401 时 client.js 自动调这个 callback。
    _onUnauthorized: null,
    setOnUnauthorized(cb) {
      this._onUnauthorized = cb;
    },
  };

  // ── WebSocket helper (D3 路线: /ws/teacher 收 checkin / outstay_new 事件) ──
  // 用法: const ws = window.tomoshibiApi.openTeacherWS(token, (event) => { ... });
  api.openTeacherWS = (token, onMessage) => {
    const base = window.API_BASE || "/api/v1";
    // base 形如 'http://host:port/api/v1' or '/api/v1'
    let wsUrl;
    if (base.startsWith("http")) {
      wsUrl = base.replace(/^http/, "ws").replace(/\/api\/v1$/, "/ws/teacher");
    } else {
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${proto}//${location.host}/ws/teacher`;
    }
    const ws = new WebSocket(`${wsUrl}?token=${encodeURIComponent(token)}`);
    ws.addEventListener("message", (ev) => {
      try {
        onMessage(JSON.parse(ev.data));
      } catch (e) {
        console.error("[tomoshibiApi WS] parse error", e, ev.data);
      }
    });
    ws.addEventListener("error", (e) => {
      console.error("[tomoshibiApi WS] error", e);
    });
    return ws;
  };

  window.tomoshibiApi = api;
})();
