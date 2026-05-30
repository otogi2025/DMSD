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
    // 5-27 拍板：实名账户登录方式 — 优先用 teacher_id (UUID) 登录（避免 login_id 暴露给爬虫）。
    // login_id 形式保留作 backward-compat（CLI / 旧测试 / fallback）。
    // 用法：teacherLogin({teacher_id, password}) 或 teacherLogin({login_id, password})。
    teacherLogin: (body) => request("POST", "/sessions/teacher", body),

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
    // 5-27 新增：教师改判单条 event — OverrideModal 调
    // body = { to_status: "present"|"late"|"absent"|"exempt_range", reason: str, evidence?: str }
    // backend 收到后自动跑 spec §11.4 改判扣分联动 + WebSocket broadcast {type:"override"}
    patchRollcallEvent: (event_id, body, token) =>
      request("PATCH", `/rollcall/events/${event_id}`, body, token),

    // ── Teachers ──
    // 5-27 新增：登录页第 1 屏用 — 无认证、最小字段（id+name+assigned_dorm+last_login_at）
    listTeachersPublic: () => request("GET", "/teachers/public", undefined),
    listTeachers: (token) => request("GET", "/teachers/", undefined, token),
    createInvitation: (body, token) =>
      request("POST", "/teachers/invitations", body, token),
    // 5-27 新增：教师管理页 — 直接创建（v1.0 简化版、跳过邀请码流程）
    // body = { login_id, name, email, password, role, assigned_dorm? }
    createTeacher: (body, token) => request("POST", "/teachers/", body, token),
    // 5-27 新增：教师管理页 — 删除（自己删自己时 backend 返 400 CANNOT_DELETE_SELF）
    deleteTeacher: (teacher_id, token) =>
      request("DELETE", `/teachers/${teacher_id}`, undefined, token),

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

    // ── Accounts（学生账号管理 §7.1 — 5-30 新增）──
    // 老师网页「账号管理页」/「搜索页」用。仅寮務部長 / 寮務課長 / 管理係三类角色。
    // params 可含 q（学号 or 姓名模糊）/ dorm_unit（整数）/ status（active 等）。
    listStudents: (params, token) => {
      const q = [];
      if (params && params.q) q.push(`q=${encodeURIComponent(params.q)}`);
      if (params && params.dorm_unit != null)
        q.push(`dorm_unit=${encodeURIComponent(params.dorm_unit)}`);
      if (params && params.status)
        q.push(`status=${encodeURIComponent(params.status)}`);
      const qs = q.length ? `?${q.join("&")}` : "";
      return request("GET", `/students${qs}`, undefined, token);
    },
    // 重置密码 — 返回 {student_id, temporary_password, message}。临时密码仅此次响应。
    resetStudentPassword: (studentId, token) =>
      request(
        "POST",
        `/accounts/${studentId}/password-reset`,
        undefined,
        token,
      ),
    // 解锁被锁账号 — 返回 {student_id, message}。
    unlockStudentAccount: (studentId, token) =>
      request("POST", `/accounts/${studentId}/unlock`, undefined, token),

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
  // 用法: const handle = window.tomoshibiApi.openTeacherWS(token, onMessage, onStatus?)
  //       handle.close()         — 关闭并停止重连
  //       handle.getStatus()     — 当前状态字符串
  //
  // onStatus 回调参数: "connecting" / "connected" / "disconnected" / "failed"
  //   - connecting   = 首次建立或重连中
  //   - connected    = 握手成功
  //   - disconnected = 服务器断开 / 网络断 → 自动重连中
  //   - failed       = 重连超过 max 次（默认 8 次）放弃
  //
  // 重连策略（spec §11.8）— 指数退避：1s / 2s / 4s / 8s / 16s / 30s（封顶）/ 30s / 30s
  // close() 显式调用后不再重连
  api.openTeacherWS = (token, onMessage, onStatus) => {
    const base = window.API_BASE || "/api/v1";
    let wsUrl;
    if (base.startsWith("http")) {
      // 绝对地址：http(s):// → ws(s)://，保留 /api/v1 前缀后接 /ws/teacher → /api/v1/ws/teacher
      wsUrl = base.replace(/^http/, "ws") + "/ws/teacher";
    } else {
      // 相对地址：当前页面 host + base(/api/v1) + /ws/teacher
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${proto}//${location.host}${base}/ws/teacher`;
    }
    const fullUrl = `${wsUrl}?token=${encodeURIComponent(token)}`;

    const MAX_ATTEMPTS = 8;
    const BACKOFF_MS = [1000, 2000, 4000, 8000, 16000, 30000, 30000, 30000];

    let ws = null;
    let closedByUser = false;
    let attempt = 0;
    let retryTimer = null;
    let currentStatus = "connecting";

    const setStatus = (s) => {
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
      setStatus(attempt === 0 ? "connecting" : "connecting");
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
      ws.addEventListener("message", (ev) => {
        try {
          onMessage(JSON.parse(ev.data));
        } catch (e) {
          console.error("[tomoshibiApi WS] parse error", e, ev.data);
        }
      });
      ws.addEventListener("error", (e) => {
        console.warn("[tomoshibiApi WS] error", e);
        // error 后通常会触发 close，重连交给 close handler
      });
      ws.addEventListener("close", (ev) => {
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
      // 兼容旧代码 — ws.close() / ws.readyState 直接用
      get readyState() {
        return ws ? ws.readyState : WebSocket.CLOSED;
      },
    };
  };

  window.tomoshibiApi = api;
})();
