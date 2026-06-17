import React from "react";
import { RYO, dormLabel, API_BASE, TIMEOUT_MS, TIMEOUT_WARN_MS } from "./theme";
import { api } from "./api/client";
import { Shell } from "./Shell";
import { LoginScreen } from "./components/LoginScreen";
import { LiveRollCall } from "./components/LiveRollCall";
import { OverrideModal } from "./components/OverrideModal";
import { RollCallLanding } from "./components/RollCallLanding";
import { RollCallSummary } from "./components/RollCallSummary";
import { ApplicationsPage } from "./components/ApplicationsPage";
import { ProxyApplicationPage } from "./components/ProxyApplicationPage";
import { OutstayDetailModal } from "./components/OutstayDetailModal";
import { DisciplinePage } from "./components/DisciplinePage";
import { CleaningPage } from "./components/CleaningPage";
import { FrontDeskPage } from "./components/FrontDeskPage";
import { RecordsPage } from "./components/RecordsPage";
import { ActiveLeavesPage } from "./components/ActiveLeavesPage";
import { SearchPage } from "./components/SearchPage";
import { NotificationsPage } from "./components/NotificationsPage";
import { InfoPage, BusPage } from "./components/InfoPage";
import { CommunityPage } from "./components/CommunityPage";
import { AccountsPage } from "./components/AccountsPage";
import { RegistrationCodePanel } from "./components/RegistrationCodePanel";
import { TeachersAdminPage } from "./components/TeachersAdminPage";
import { StudyAttendancePage } from "./components/StudyAttendancePage";
import { AuditLogPage } from "./components/AuditLogPage";
import { canView, C_AUDIT_LOG } from "./api/permissions";

export function App() {
  const T = RYO;
  // route: 'login' | 'select-teacher' | 'app'
  // Task #15 §11.5 W5: 把 JWT 存进 sessionStorage —— F5 刷新后恢复 / Safari 关闭时自动清空
  // sessionStorage 用「tomoshibi_auth」键保存 {token, profile} 的 JSON。
  const _restoredAuth = (() => {
    try {
      const raw = sessionStorage.getItem("tomoshibi_auth");
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  })();
  // 5-27 拍板：实名账户登录后直接进 app（旧 select-teacher 中间页砍）。
  // 从 backend TeacherOut.profile 派生 UI 用 teacher 字段 — assigned_dorm: 4=女寮 / 其他=男寮。
  const _restoredTeacher =
    _restoredAuth && _restoredAuth.profile
      ? {
          id: _restoredAuth.profile.id,
          name: _restoredAuth.profile.name,
          dorm: _restoredAuth.profile.assigned_dorm === 4 ? "women" : "men",
          initial: (_restoredAuth.profile.name || "?").charAt(0),
          lastLoginMins: null,
          // A1 修复: 把 role + assigned_dorm 带进 teacher，否则权限按钮(一括进级/行事/巴士增删改)永不显示
          role: _restoredAuth.profile.role,
          assigned_dorm: _restoredAuth.profile.assigned_dorm,
        }
      : null;
  const [route, setRoute] = React.useState(
    _restoredAuth && _restoredAuth.token ? "app" : "login",
  );
  const [teachers, setTeachers] = React.useState<any>(null); // null=未取得(loading)，后端拉取，失败显错误态不显假老师
  const [teacher, setTeacher] = React.useState<any>(_restoredTeacher);
  const [lastTeacherId, setLastTeacherId] = React.useState<any>(
    _restoredTeacher ? _restoredTeacher.id : null,
  );
  // FC-024 修复后: 保存 backend 认证返回的 JWT + teacher profile
  const [authToken, setAuthToken] = React.useState<string | null>(
    _restoredAuth ? _restoredAuth.token || null : null,
  );
  const [authProfile, setAuthProfile] = React.useState<any>(
    _restoredAuth ? _restoredAuth.profile || null : null,
  );
  // Task #6 真接口对接: backend 返回的本日点呼 session 一览（null = 未 fetch / [] = backend 不可达 / [...] = 已取得）
  const [todaySessions, setTodaySessions] = React.useState<any>(null);
  const [backendReachable, setBackendReachable] = React.useState<
    boolean | null
  >(null); // null / true / false
  // 5-27 spec §11.8: WebSocket 连接状态 — connecting / connected / disconnected / failed
  // 非点呼会话进行中时为 null（不显示 banner）
  const [wsStatus, setWsStatus] = React.useState<string | null>(null);
  // 实时大屏 NFC 接收指示灯计数 — 每收到一条 WebSocket checkin 事件 +1，
  // 驱动 LiveRollCall 右上角指示灯由「待機中」变成「受信中」并显示序号（C31）。
  const [nfcSeq, setNfcSeq] = React.useState(0);
  // Task #6 第 6 步: 申请 pending list (backend Application[]) - 担当教师宛て未承认
  const [backendApplications, setBackendApplications] =
    React.useState<any>(null);
  // Task #10 (5-27): 从 backend listTeachers 取得的教师一览 (SelectTeacherScreen 用)
  // null = 未取得 / [] = backend 不可达 → window.TEACHERS fallback / [...] = 真值
  const [backendTeachers, setBackendTeachers] = React.useState<any>(null);
  const [page, setPage] = React.useState("roll-call");
  const [pageParams, setPageParams] = React.useState<any>(null);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [toast, setToast] = React.useState<{
    type: string;
    msg: string;
  } | null>(null);

  // Session state
  const [session, setSession] = React.useState<any>(null); // {name, startedAt}
  const [students, setStudents] = React.useState<any[]>([]);
  const [liveMode, setLiveMode] = React.useState(false); // fullscreen live view
  const [lastEnded, setLastEnded] = React.useState<any>(null);
  // Task #13 spec §5.6 「点呼総結」中层页: rollcallSummary 拿 4 区块 (absent/late/health_issue/exempted_outstay)
  const [lastSummary, setLastSummary] = React.useState<any>(null);
  const [overrideTarget, setOverrideTarget] = React.useState<any>(null);
  const [outstayTarget, setOutstayTarget] = React.useState<any>(null);

  // Trend demo
  const trend = [
    { date: "2026-04-15", late: 1, absent: 0 },
    { date: "2026-04-16", late: 0, absent: 0 },
    { date: "2026-04-17", late: 2, absent: 1 },
    { date: "2026-04-18", late: 1, absent: 0 },
    { date: "2026-04-19", late: 0, absent: 0 },
    { date: "2026-04-20", late: 1, absent: 0 },
    { date: "2026-04-21", late: 0, absent: 1 },
  ];

  // Auto-logout 30min with 25min warning
  const lastActivity = React.useRef(Date.now());
  React.useEffect(() => {
    const bump = () => {
      lastActivity.current = Date.now();
    };
    ["mousemove", "keydown", "click", "touchstart"].forEach((e) =>
      window.addEventListener(e, bump),
    );
    return () =>
      ["mousemove", "keydown", "click", "touchstart"].forEach((e) =>
        window.removeEventListener(e, bump),
      );
  }, []);
  React.useEffect(() => {
    if (route !== "app") return;
    let warned = false;
    const id = setInterval(() => {
      const idle = Date.now() - lastActivity.current;
      if (idle > TIMEOUT_MS) {
        // 5-27 拍板：超时返回 login 第 1 屏（旧 select-teacher 中间页砍）
        // sessionStorage 不清 — lastTeacherId 保留可让卡片高亮「前回」
        setRoute("login");
        setTeacher(null);
        setAuthToken(null);
        setAuthProfile(null);
        setLiveMode(false);
        try {
          sessionStorage.removeItem("tomoshibi_auth");
        } catch (e) {
          /* sessionStorage 失败忽略 */
        }
        setToast({
          type: "warn",
          msg: "操作がないため再ログイン画面に戻りました",
        });
      } else if (!warned && idle > TIMEOUT_WARN_MS) {
        warned = true;
        setToast({
          type: "warn",
          msg: "あと5分でログイン画面に戻ります",
        });
      }
    }, 5000);
    return () => clearInterval(id);
  }, [route]);

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 4500);
      return () => clearTimeout(id);
    }
  }, [toast]);

  // Task #6 真接口对接: authToken 来了就 fetch backend rollcallTodaySessions
  // (api.rollcallTodaySessions(token) → RollCallSessionOut[])。
  // backend 不可达 (fetch 失败 / 5xx) 则 backendReachable=false → UI 显示警告。
  React.useEffect(() => {
    if (!authToken) {
      setTodaySessions(null);
      setBackendReachable(null);
      return;
    }
    let cancelled = false;
    api
      .rollcallTodaySessions(authToken)
      .then((sessions) => {
        if (cancelled) return;
        setTodaySessions(sessions);
        setBackendReachable(true);
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn(
          "[App] rollcallTodaySessions 失敗 → demo seed fallback",
          err,
        );
        setTodaySessions([]);
        setBackendReachable(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  // §11.5 W3: 401 全局拦截 — 任意 API 收 401 时强制 logout
  // client.js request() 内部 401 时调本 callback。logout 用 inline 不依赖闭包 logout。
  React.useEffect(() => {
    api.setOnUnauthorized(() => {
      try {
        sessionStorage.removeItem("tomoshibi_auth");
      } catch (e) {
        /* sessionStorage 失败忽略 */
      }
      setRoute("login");
      setTeacher(null);
      setAuthToken(null);
      setAuthProfile(null);
      setLiveMode(false);
      setSession(null);
      setToast({
        type: "warn",
        msg: "セッションが切れました。再度ログインしてください。",
      });
    });
    // cleanup：传 null 清除 401 拦截回调（client.ts 签名已放宽收 null）。
    return () => api.setOnUnauthorized(null);
  }, []);

  // Task #10 (5-27): authToken 来了就 fetch backend listTeachers
  // 把 backend TeacherOut {id, login_id, name, role, assigned_dorm, ...}
  // adapt 成 UI 用的 {id, name, dorm, initial, lastLoginMins}。
  // assigned_dorm: 1 (一寮) → men, 2 (二寮) → women (跟 spec 的 dorm_unit 命名一致，
  // 从 dorm_unit 数值映射为暂定方案。多寮支持留到 v1.1)。
  React.useEffect(() => {
    if (!authToken) {
      setBackendTeachers(null);
      return;
    }
    let cancelled = false;
    api
      .listTeachers(authToken)
      .then((rows) => {
        if (cancelled) return;
        // 5-27 codex 审查 #12 修：backend assigned_dorm 4=女寮 / 1+2=男寮（一寮+二寮）/ null=跨寮
        // 之前误写 `=== 2 ? women : men` 把男二寮老师映射到女寮列
        const adapted = (rows || []).map((t) => ({
          id: t.id,
          name: t.name,
          dorm: t.assigned_dorm === 4 ? "women" : "men",
          initial: (t.name || "?").charAt(0),
          lastLoginMins: null, // backend 本字段未提供，UI 显示 fallback
        }));
        setBackendTeachers(adapted);
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn("[App] listTeachers 失敗 → window.TEACHERS fallback", err);
        setBackendTeachers([]);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  // Task #6 第 6 步: authToken 来了就 fetch 申请 pending list
  // (api.pendingForMe(token) → Application[])。
  // ApplicationsPage / OutstayList / DetailModal 里用它替代 window.OUTSTAY_APPS
  // (backend 不可达则照旧用假数据)。
  React.useEffect(() => {
    if (!authToken) {
      setBackendApplications(null);
      return;
    }
    let cancelled = false;
    api
      .pendingForMe(authToken)
      .then((apps) => {
        if (cancelled) return;
        setBackendApplications(apps);
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn(
          "[App] pendingForMe 失敗 → window.OUTSTAY_APPS fallback",
          err,
        );
        setBackendApplications([]);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  // Task #6 第 5 步 + 5-27 spec §11.8: backend 点呼会话进行中时连 WebSocket /ws/teacher
  // 实时收 checkin / outstay_new / override 事件，更新 students state。
  // 5-27 改造：用新 openTeacherWS（指数退避重连 + onStatus 回调）+ wsStatus state 驱动 banner
  // demo 模式 (sessionId=null) 不建立 WS 连接，wsStatus 保持 null
  React.useEffect(() => {
    if (!session || !session.sessionId || !authToken) {
      setWsStatus(null);
      return;
    }
    // backend 实时 override broadcast 的 status 是 backend 字段值
    // present / late / absent / exempt_range — 映射回 frontend ok / late / absent / exempt
    const _backendStatusToFront = (s: string) =>
      s === "present" ? "ok" : s === "exempt_range" ? "exempt" : s; // late / absent 原样
    let handle: any;
    try {
      handle = api.openTeacherWS(
        authToken,
        (event: any) => {
          // event.type: 'checkin' | 'outstay_new' | 'override' | ...
          if (event.type === "checkin" && event.student_id) {
            // 收到一条签到 → 指示灯计数 +1（驱动大屏 NFC 指示灯，C31）
            setNfcSeq((n) => n + 1);
            setStudents((list) => {
              // 生产：WebSocket 经由的 checkin 用日语名读上げ（从旧 demo poll 移植）
              const hit = list.find((s) => s.key === event.student_id);
              if (hit && hit.name && window.speechSynthesis) {
                try {
                  window.speechSynthesis.cancel();
                  const u = new SpeechSynthesisUtterance(hit.name);
                  u.lang = "ja-JP";
                  u.rate = 0.95;
                  window.speechSynthesis.speak(u);
                } catch (e) {
                  /* 读上げ失败忽略 */
                }
              }
              return list.map((s) =>
                s.key === event.student_id
                  ? {
                      ...s,
                      status: event.status === "late" ? "late" : "ok",
                      checkinAt:
                        event.checked_at ||
                        new Date().toTimeString().slice(0, 8),
                    }
                  : s,
              );
            });
          } else if (event.type === "outstay_new" && event.student_id) {
            setStudents((list) =>
              list.map((s) =>
                s.key === event.student_id
                  ? {
                      ...s,
                      pending: {
                        reason: event.reason || "外泊申請",
                        submittedAt:
                          event.submitted_at ||
                          new Date().toTimeString().slice(0, 5),
                      },
                    }
                  : s,
              ),
            );
          } else if (event.type === "override" && event.student_id) {
            setStudents((list) =>
              list.map((s) =>
                s.key === event.student_id
                  ? {
                      ...s,
                      status: _backendStatusToFront(event.status) || s.status,
                      override: {
                        reason: event.override_reason || event.reason || "",
                        by: event.by || "別端末",
                      },
                    }
                  : s,
              ),
            );
          }
        },
        (status) => setWsStatus(status),
      );
    } catch (err) {
      console.warn("[App] WebSocket 连接失败", err);
      setWsStatus("failed");
    }
    return () => {
      if (handle && typeof handle.close === "function") handle.close();
      setWsStatus(null);
    };
  }, [session, authToken]);

  // FC-024 + Task #15: backend 认证成功 → 更新 state + sessionStorage 持久化 (F5 恢复)
  // 5-27 拍板：实名账户登录 — LoginScreen 内一次性拿 token + profile + pickedTeacher
  // pickedTeacher = LoginScreen 屏 1 选中的卡片 {id, name, dorm, initial} （从 GET /teachers/public 派生）
  // 直接进 app，跳过旧 select-teacher 中间页。
  const loginOk = (token: any, profile: any, pickedTeacher: any) => {
    setAuthToken(token);
    setAuthProfile(profile);
    try {
      sessionStorage.setItem(
        "tomoshibi_auth",
        JSON.stringify({ token, profile }),
      );
    } catch (e) {
      // private mode 等情况下失败也让 login 继续 (state 里还留着)
      console.warn("[App] sessionStorage write 失敗", e);
    }
    if (pickedTeacher) {
      // A1 修复: 把 profile 的 role + assigned_dorm 合进 teacher（pickedTeacher 卡片只有 id/name/dorm/initial）
      setTeacher({
        ...pickedTeacher,
        role: profile && profile.role,
        assigned_dorm: profile && profile.assigned_dorm,
      });
      setLastTeacherId(pickedTeacher.id);
    }
    const home = _roleHomePage(profile && profile.role);
    setPage(home);
    setRoute("app");
    if (pickedTeacher) {
      setToast({
        type: "ok",
        msg: `${pickedTeacher.name} 先生でログインしました・${dormLabel(pickedTeacher.dorm)}担当`,
      });
    }
  };
  // 2026-06-16 itsuki 拍板：登录后默认页统一为「点呼」（不再按角色分流到 申請 / 夜学習）。
  // 点呼是日常值班的核心操作，所有角色登录都先落在这里。参数保留以兼容现有两处调用点。
  const _roleHomePage = (_role: any) => "roll-call";
  const pickTeacher = (t: any) => {
    setTeacher(t);
    setLastTeacherId(t.id);
    setRoute("app");
    const home = _roleHomePage(authProfile && authProfile.role);
    setPage(home);
    setToast({
      type: "ok",
      msg: `${t.name} 先生でログインしました・${dormLabel(t.dorm)}担当`,
    });
  };
  // Task #15 W5 拍板: backend revoke + frontend clear 两边都做
  // backend 失败也让 frontend 必定 clear (防 UI 锁死)
  const logout = async () => {
    if (authToken) {
      try {
        await fetch(`${API_BASE}/sessions/current`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${authToken}` },
        });
      } catch (e) {
        console.warn("[App] backend logout 失敗 (frontend clear 続行)", e);
      }
    }
    try {
      sessionStorage.removeItem("tomoshibi_auth");
    } catch (e) {
      /* sessionStorage 失败忽略 */
    }
    setRoute("login");
    setTeacher(null);
    setAuthToken(null);
    setAuthProfile(null);
    setLiveMode(false);
    setSession(null);
  };

  // Task #6 真接口对接: 调 rollcallStart + rollcallBoard 在 backend 起动 session。
  // 把 backend RollCallBoardEntry → 内部 student shape:
  //   {student_id, student_no, name, room_no, base_status, checked_in_at}
  //   → {key, id, room, name, dorm, status, checkinAt, health, pending, override, exemptReason}
  const _boardEntryToStudent = (e: any, dormHint: any) => ({
    key: e.student_id,
    id: e.student_no,
    room: e.room_no,
    name: e.name,
    dorm: dormHint,
    // backend base_status: init/present/late/absent/exempt_range → 内部 status 映射
    status:
      e.base_status === "present"
        ? "ok"
        : e.base_status === "exempt_range"
          ? "exempt"
          : e.base_status === "init"
            ? "unknown"
            : e.base_status, // late / absent 原样保留
    checkinAt: e.checked_in_at,
    // 5-27: 该学生最新 RollCallEvent.id — OverrideModal 调 PATCH /events/{id} 用
    // init 状态学生没 event = null（OverrideModal 收到 null 走 demo 路径）
    lastEventId: e.last_event_id || null,
    health: null,
    pending: null,
    override: null,
    exemptReason: null,
  });

  const startSession = async (name: string) => {
    // 从 name 判别 backend session：含「朝」判 morning，其余（夜点呼等）判 evening。
    // 非「朝」一律归 evening，这样不依赖晩/夜的表记差异也能正确判别（C32 修复）。
    const wantType = name.includes("朝") ? "morning" : "evening";
    const sess =
      backendReachable &&
      wantType &&
      (todaySessions || []).find((s: any) => s.session_type === wantType);

    if (sess && authToken) {
      try {
        await api.rollcallStart(sess.id, authToken);
        const board = await api.rollcallBoard(sess.id, authToken);
        const students = (board.entries || []).map((e) =>
          _boardEntryToStudent(e, teacher.dorm),
        );
        setStudents(students);
        setSession({ name, sessionId: sess.id, startedAt: Date.now() });
        setLiveMode(true);
        setToast({
          type: "ok",
          msg: `サーバーに接続しました：${board.entries.length}名`,
        });
        return;
      } catch (err) {
        console.warn(
          "[App] rollcallStart/Board 失敗 → demo seed fallback",
          err,
        );
        setToast({
          type: "warn",
          msg: "サーバーに接続できないため、デモ表示で継続します",
        });
      }
    }

    // 后端不可达 / session 未找到 — 显示错误，不用假数据填充
    setToast({
      type: "error",
      msg: "点呼を開始できません。サーバーに接続できないか、本日の点呼が見つかりません。",
    });
  };
  // Task #6 真接口对接: session.sessionId 是 UUID 则调 backend rollcallEnd。
  // session.sessionId 为 null (demo 模式) 则照旧只用 state 做终了处理。
  const endSession = async () => {
    const cnt = students.reduce((a, s) => {
      a[s.status] = (a[s.status] || 0) + 1;
      return a;
    }, {});
    const total = students.length;
    const rate = `${(cnt.ok || 0) + (cnt.exempt || 0) + (cnt.late || 0)}/${total}`;
    const d = new Date();
    const t2 = (d: Date) =>
      `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;

    // 有 backend session 就调终了 API + 取 summary (失败也让 UI 关闭)
    let backendSummary = null;
    if (session.sessionId && authToken) {
      try {
        await api.rollcallEnd(session.sessionId, authToken);
        // Task #13 spec §5.6: 终了直后取 summary 进「点呼総結」中层页
        try {
          backendSummary = await api.rollcallSummary(
            session.sessionId,
            authToken,
          );
        } catch (sErr) {
          console.warn("[App] rollcallSummary 失敗", sErr);
        }
      } catch (err) {
        console.warn("[App] rollcallEnd 失敗 (UI 側は終了処理続行)", err);
        setToast({
          type: "warn",
          msg: "点呼終了の保存に失敗しました（画面は閉じます）",
        });
      }
    }

    // demo 模式 (sessionId=null) 也从 students 组 summary (spec §5.6 4 区块)
    let summaryForUi = backendSummary;
    if (!summaryForUi) {
      summaryForUi = {
        session_id: session.sessionId || "demo",
        absent: students
          .filter((s) => s.status === "absent")
          .map((s) => ({
            student_id: s.key,
            name: s.name,
            room_no: s.room,
          })),
        late: students
          .filter((s) => s.status === "late")
          .map((s) => ({
            student_id: s.key,
            name: s.name,
            room_no: s.room,
          })),
        health_issue: students
          .filter((s) => s.health)
          .map((s) => ({
            student_id: s.key,
            name: s.name,
            room_no: s.room,
            reason: s.health,
          })),
        exempted_outstay: students
          .filter((s) => s.status === "exempt")
          .map((s) => ({
            student_id: s.key,
            name: s.name,
            room_no: s.room,
            reason: s.exemptReason || "",
          })),
      };
    }

    setLastEnded({
      name: session.name,
      start: t2(new Date(session.startedAt)),
      end: t2(d),
      rate,
      sessionName: session.name,
    });
    setLastSummary(summaryForUi);
    setLiveMode(false);
    setSession(null);
    // Task #13 spec §5.6: 终了后自动迁移到「点呼総結」中层页
    setPage("summary");
    // backend session 终了时如果上面没出 warn，就出 ok 的 toast
    if (!(session.sessionId && authToken)) {
      setToast({ type: "ok", msg: "点呼が保存されました" });
    } else {
      setToast({ type: "ok", msg: "点呼が保存されました" });
    }
  };
  const openOverride = (s: any) => setOverrideTarget(s);
  // 5-27: 真接 backend PATCH /api/v1/rollcall/events/{event_id}
  // backend 收到后自动跑 spec §11.4 改判扣分联动 + WebSocket broadcast {type:"override"}
  // 状态映射：frontend ok/late/absent/exempt → backend present/late/absent/exempt_range
  // overrideTarget.lastEventId 为 null（init 状态学生）或 demo 模式时走旧本地 state 路径
  const _frontStatusToBackend = (s: string) =>
    s === "ok" ? "present" : s === "exempt" ? "exempt_range" : s; // late / absent 原样
  // 状态值日语化（toast 给老师看，避免露 ok/late/absent 英文）
  const _statusLabelJa = (s: string): string =>
    ({
      ok: "出席",
      late: "遅刻",
      absent: "欠席",
      exempt: "外泊（対象外）",
      unknown: "未確認",
    })[s] || s;
  const saveOverride = async (patch: any) => {
    const target = overrideTarget;
    // 真接 backend：有 lastEventId + authToken + sessionId 时调 PATCH
    if (
      target &&
      target.lastEventId &&
      authToken &&
      session &&
      session.sessionId
    ) {
      try {
        await api.patchRollcallEvent(
          target.lastEventId,
          {
            to_status: _frontStatusToBackend(patch.status),
            reason: patch.reason,
          },
          authToken,
        );
        setToast({
          type: "ok",
          msg: `${target.name} の状態を「${_statusLabelJa(patch.status)}」に変更しました`,
        });
        // 注：backend 异步 WebSocket broadcast 也会回推 setStudents，这里乐观更新保证 UI 即时反映
      } catch (err) {
        console.warn("[App] patchRollcallEvent 失败 → 仅本地更新", err);
        setToast({
          type: "warn",
          msg: "変更の保存に失敗しました。表示のみ更新します",
        });
      }
    }
    // 本地 state 同步（成功 / 失败 / demo 模式都更新一次，保证 UI 反应）
    setStudents((list) =>
      list.map((s) =>
        s.key === overrideTarget.key
          ? {
              ...s,
              status: patch.status,
              checkinAt:
                patch.status === "ok"
                  ? s.checkinAt || new Date().toTimeString().slice(0, 8)
                  : s.checkinAt,
              override: {
                reason: patch.reason,
                by: teacher.name + " 先生",
              },
              pending: patch.approveLeave ? null : s.pending,
              exemptReason:
                patch.status === "exempt"
                  ? s.exemptReason || patch.reason
                  : s.exemptReason,
            }
          : s,
      ),
    );
    setOverrideTarget(null);
    setToast({ type: "ok", msg: "調整が反映されました" });
  };
  const resetLive = async () => {
    // 从后端重新拉 board，不再用假数据
    if (session && session.sessionId && authToken) {
      try {
        const board = await api.rollcallBoard(session.sessionId, authToken);
        const fresh = (board.entries || []).map((e) =>
          _boardEntryToStudent(e, teacher.dorm),
        );
        setStudents(fresh);
        setToast({ type: "warn", msg: "点呼をリセットしました" });
      } catch (err) {
        console.warn("[App] resetLive board 再取得失敗", err);
        setToast({
          type: "error",
          msg: "リセットに失敗しました：サーバーからデータを取得できませんでした",
        });
      }
    } else {
      setToast({
        type: "error",
        msg: "リセットに失敗しました：有効な点呼がありません",
      });
    }
  };

  const nav = (id: string, params?: any) => {
    setPage(id);
    setPageParams(params || null);
    if (id !== "search") setSearchQuery("");
  };
  const search = (q: string) => {
    setSearchQuery(q);
    setPage("search");
  };

  const onTeacherDelete = (id: any) =>
    setTeachers((list: any[]) => list.filter((t) => t.id !== id));
  const onTeacherAdd = (data: any) =>
    setTeachers((list: any[]) => [
      ...list,
      { ...data, id: "t" + Date.now(), lastLoginMins: null },
    ]);

  // --- RENDER ---

  if (route === "login") {
    return (
      <>
        <LoginScreen onLogin={loginOk} lastTeacherId={lastTeacherId} />
        <ToastSlot toast={toast} />
      </>
    );
  }
  // 5-27 拍板：旧 route === "select-teacher" 中间页砍 —
  // LoginScreen 内部已合并「列表 + 密码」2 屏，登录成功直接进 app。
  // window.SelectTeacherScreen 组件保留（10531 行附近）作为 v1.1 候补 — 暂不使用。
  // app
  if (liveMode && session) {
    return (
      <>
        <LiveRollCall
          teacher={teacher}
          sessionName={session.name}
          startedAt={session.startedAt}
          students={students}
          setStudents={setStudents}
          onEnd={endSession}
          onOverride={openOverride}
          onReset={resetLive}
          nfcSeq={nfcSeq}
        />
        {overrideTarget && (
          <OverrideModal
            student={overrideTarget}
            onClose={() => setOverrideTarget(null)}
            onSave={saveOverride}
          />
        )}
        <ToastSlot toast={toast} />
      </>
    );
  }

  // route !== "login" 说明已登录，authToken 必非空（登录时同步设置 route + authToken）。
  // 这个守卫让 TS 把 authToken 从 string|null 窄化成 string，传给各页面 prop —— 不改 JSX/界面。
  if (authToken === null) return null;

  let body;
  switch (page) {
    case "roll-call":
      body = (
        <RollCallLanding
          teacher={teacher}
          onStart={startSession}
          lastEnded={lastEnded}
          onNav={nav}
          trend={trend}
          authToken={authToken}
          onShowSummary={lastSummary ? () => setPage("summary") : undefined}
        />
      );
      break;
    case "summary":
      // Task #13 spec §5.6 「点呼総結」中层页
      body = (
        <RollCallSummary
          summary={lastSummary}
          lastEnded={lastEnded}
          onBack={() => setPage("roll-call")}
        />
      );
      break;
    case "applications":
      body = (
        <ApplicationsPage
          onOpen={setOutstayTarget}
          backendApplications={backendApplications}
          authToken={authToken}
          onNav={nav}
        />
      );
      break;
    case "proxy-application":
      // 2026-06-05 杭田需求「五-3」— 老师代録出寮届表单
      body = <ProxyApplicationPage authToken={authToken} />;
      break;
    case "discipline":
      body = (
        <DisciplinePage teacher={teacher} onNav={nav} authToken={authToken} />
      );
      break;
    case "cleaning":
      body = <CleaningPage authToken={authToken} />;
      break;
    case "records":
      body = (
        <RecordsPage
          teacher={teacher}
          params={pageParams}
          onNav={nav}
          authToken={authToken}
        />
      );
      break;
    case "active-leaves":
      // 2026-06-04 杭田需求「四、出寮者一覧」— 纯只读出寮中寮生表
      body = <ActiveLeavesPage authToken={authToken} />;
      break;
    case "search":
      body = (
        <SearchPage
          teacher={teacher}
          query={searchQuery}
          authToken={authToken}
        />
      );
      break;
    case "notifications":
      body = (
        <NotificationsPage
          teacher={teacher}
          onNav={nav}
          authToken={authToken}
        />
      );
      break;
    case "info":
      body = <InfoPage teacher={teacher} authToken={authToken} />;
      break;
    case "bus":
      body = <BusPage teacher={teacher} authToken={authToken} />;
      break;
    case "community":
      body = <CommunityPage teacher={teacher} />;
      break;
    case "front-desk":
      body = <FrontDeskPage teacher={teacher} authToken={authToken} />;
      break;
    case "accounts":
      body = <AccountsPage teacher={teacher} authToken={authToken} />;
      break;
    case "admin-registration-code":
      // Task #14: 学生登録コードパネル (§11.9.1)
      body = <RegistrationCodePanel authToken={authToken} />;
      break;
    case "teachers-admin":
      // 5-27 拍板: 教員アカウント管理 (§3.4「前台不允许自助注册 / 现教师后台加删」)
      body = (
        <TeachersAdminPage
          authToken={authToken}
          currentTeacherId={authProfile && authProfile.id}
        />
      );
      break;
    case "study":
      // Task #17: 学習出席页 (§11.1 P0 + §7.3)
      body = <StudyAttendancePage teacher={teacher} authToken={authToken} />;
      break;
    case "audit-log":
      // 2026-06-16: 操作履历审计页（操作记录）— 只读，后端 C_AUDIT_LOG 权限把关
      body = <AuditLogPage authToken={authToken} />;
      break;
    default:
      body = (
        <RollCallLanding
          teacher={teacher}
          onStart={startSession}
          lastEnded={lastEnded}
          onNav={nav}
          trend={trend}
          authToken={authToken}
        />
      );
  }

  // 操作履历审计页可见性 — 统一走 permissions.ts 权限矩阵（C_AUDIT_LOG 簇）。
  // canView 内部已处理 permission_group 优先、为空按职位回退（ROLE_DEFAULT_GROUP）。仅控制菜单显隐，
  // 真正的访问控制在后端 require_permission（非管理角色直连接口仍 403）。
  const canViewAuditLog = !!(authProfile && canView(authProfile, C_AUDIT_LOG));

  return (
    <>
      <Shell
        teacher={teacher}
        active={page === "search" ? "search" : page}
        onNav={nav}
        sessionActive={session && !liveMode}
        onLogout={logout}
        backendReachable={backendReachable}
        wsStatus={wsStatus}
        authToken={authToken}
        canViewAuditLog={canViewAuditLog}
        onSwitchTeacher={() => {
          // 5-27 拍板：切替＝ログアウト相当（实名账户 = 必須再認証）。
          // sessionStorage 不清 — lastTeacherId 保留可让 LoginScreen 卡片高亮「前回」
          logout();
        }}
        onSearch={search}
        onResumeLive={() => session && setLiveMode(true)}
      >
        {body}
      </Shell>
      {outstayTarget && (
        <OutstayDetailModal
          app={outstayTarget}
          authToken={authToken}
          onClose={() => setOutstayTarget(null)}
          onAction={async (a, comment) => {
            // Task #6 第 7 步: 调 backend decide() (outstayTarget._backend 有 = backend
            // adapt 来的数据 / 无 = window.OUTSTAY_APPS demo 数据)。
            // a='approved'/'rejected' → map 成 backend 'approve'/'reject'。
            // a='pending' (保留) 在 backend decide 里没有所以 skip (只关 UI)。
            const backendApp = outstayTarget._backend;
            if (
              backendApp &&
              authToken &&
              (a === "approved" || a === "rejected")
            ) {
              const decision = a === "approved" ? "approve" : "reject";
              try {
                await api.decide(
                  backendApp.id,
                  decision,
                  comment || undefined,
                  authToken,
                );
                // 成功时 refetch pending list (该 application 会消失)
                try {
                  const refreshed = await api.pendingForMe(authToken);
                  setBackendApplications(refreshed);
                } catch (_) {
                  // refetch 失败忽略 (UI 下次打开时会自愈)
                }
              } catch (err: any) {
                console.warn("[App] decide 失敗", err);
                setToast({
                  type: "warn",
                  msg: `申請の承認・却下を保存できませんでした（${err.status || "通信エラー"}）。画面は閉じます。`,
                });
                setOutstayTarget(null);
                return;
              }
            }
            setOutstayTarget(null);
            setToast({
              type: "ok",
              msg: `申請を${a === "approved" ? "承認" : a === "rejected" ? "却下" : "保留"}しました${a === "approved" || a === "rejected" ? " · 学生へメール通知送信済み" : ""}`,
            });
          }}
        />
      )}
      <ToastSlot toast={toast} />
    </>
  );
}

function ToastSlot({ toast }: { toast: { type: string; msg: string } | null }) {
  const T = RYO;
  if (!toast) return null;
  const c =
    toast.type === "ok"
      ? [T.ok, T.okSoft, T.okBorder]
      : [T.warn, T.warnSoft, T.warnBorder];
  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        left: "50%",
        transform: "translateX(-50%)",
        background: c[1],
        color: c[0],
        border: `1px solid ${c[2]}`,
        padding: "10px 18px",
        borderRadius: 999,
        fontSize: 13,
        fontWeight: 600,
        fontFamily: T.font,
        zIndex: 1000,
        boxShadow: T.shadow2,
        animation: "toastIn .3s ease-out",
      }}
    >
      {toast.msg}
    </div>
  );
}
