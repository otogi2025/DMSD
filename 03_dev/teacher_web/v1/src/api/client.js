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
      // backend envelope: {error: {...}} | {detail: '...'} | raw
      const inner = err && (err.error || err.detail || err);
      if (inner && typeof inner === "object") Object.assign(wrapped, inner);
      else wrapped.message = inner;
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

    // ── Teachers ──
    listTeachers: (token) => request("GET", "/teachers/", undefined, token),
    createInvitation: (body, token) =>
      request("POST", "/teachers/invitations", body, token),

    // ── Announcements (FC-027 工程注记: backend 端权限契约
    //   get_current_student vs get_current_teacher 待 Task #6 一起补) ──
    listAnnouncements: (token) =>
      request("GET", "/announcements", undefined, token),
    getAnnouncement: (id, token) =>
      request("GET", `/announcements/${id}`, undefined, token),
    createAnnouncement: (body, token) =>
      request("POST", "/announcements", body, token),
    deleteAnnouncement: (id, token) =>
      request("DELETE", `/announcements/${id}`, undefined, token),

    // 学生登録码 admin 接口（§7.16 + WEB_DESIGN_LOG §11.9.1）
    // 仅寮務部長 / 寮務課長 / 管理係 三类角色返 200，其他教师 403。
    // 返回结构：{code, created_at, expires_at, expires_in_seconds}
    getRegistrationCodeCurrent: (token) =>
      request("GET", "/admin/registration-code/current", undefined, token),
    refreshRegistrationCode: (token) =>
      request("POST", "/admin/registration-code/refresh", {}, token),
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
