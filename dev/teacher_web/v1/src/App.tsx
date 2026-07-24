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
import { OutingsPage } from "./components/OutingsPage";
import { ProxyApplicationPage } from "./components/ProxyApplicationPage";
import { OutstayDetailModal } from "./components/OutstayDetailModal";
import { DisciplinePage } from "./components/DisciplinePage";
import { CleaningPage } from "./components/CleaningPage";
import { FrontDeskPage } from "./components/FrontDeskPage";
import { ReportsPage } from "./components/ReportsPage";
import { RollCallReportsPage } from "./components/RollCallReportsPage";
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
  // web#42: useMemo 只算一次，避免每次渲染都 sessionStorage.getItem + JSON.parse
  const { _restoredAuth, _restoredTeacher } = React.useMemo(() => {
    let auth: any = null;
    try {
      const raw = sessionStorage.getItem("tomoshibi_auth");
      auth = raw ? JSON.parse(raw) : null;
    } catch (e) {
      auth = null;
    }
    // 5-27 拍板：实名账户登录后直接进 app（旧 select-teacher 中间页砍）。
    // 从 backend TeacherOut.profile 派生 UI 用 teacher 字段 — assigned_dorm: 4=女寮 / 其他=男寮。
    const teacher =
      auth && auth.profile
        ? {
            id: auth.profile.id,
            name: auth.profile.name,
            dorm: auth.profile.assigned_dorm === 4 ? "women" : "men",
            initial: (auth.profile.name || "?").charAt(0),
            lastLoginMins: null,
            // A1 修复: 把 role + assigned_dorm 带进 teacher，否则权限按钮(一括进级/行事/巴士增删改)永不显示
            role: auth.profile.role,
            assigned_dorm: auth.profile.assigned_dorm,
            // 带上有效权限组，供 InfoPage / AccountsPage 用 canManage 判功能入口显隐（TW-001/048）
            permission_group: auth.profile.permission_group ?? null,
          }
        : null;
    return { _restoredAuth: auth, _restoredTeacher: teacher };
  }, []);
  const [route, setRoute] = React.useState(
    _restoredAuth && _restoredAuth.token ? "app" : "login",
  );
  // web#13: 删死代码 teachers/setTeachers（无渲染路径、无 prop 传出；TeachersAdminPage 自行拉列表）
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
  // web#13: 删死代码 backendTeachers（全 App 无读取渲染路径；listTeachers effect 一并删）
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

  // web#45: 无 trend 后端端点 → 删假趋势数据（不再传给 RollCallLanding）

  // Auto-logout 30min with 25min warning
  const lastActivity = React.useRef(Date.now());
  // web#43: students 的 ref 镜像，供 WS checkin 回调里查姓名朗读（不放进 setStudents updater）
  const studentsRef = React.useRef(students);
  studentsRef.current = students;
  // web#11: warned 用 ref 存——活动 bump 时复位，否则 25 分警告后动一下再空闲只会到 30 分直接踢、不再警告
  const idleWarned = React.useRef(false);
  React.useEffect(() => {
    const bump = () => {
      lastActivity.current = Date.now();
      idleWarned.current = false; // web#11: 有操作则重置警告，下次空闲可再弹 25 分提醒
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
    const id = setInterval(() => {
      const idle = Date.now() - lastActivity.current;
      if (idle > TIMEOUT_MS) {
        // 5-27 拍板：超时返回 login 第 1 屏（旧 select-teacher 中间页砍）
        // sessionStorage 不清 — lastTeacherId 保留可让卡片高亮「前回」
        // 点呼 session/students/nfcSeq 也要清（与 401 回调 / logout 对齐）——原来
        // 不清导致再登录后顶栏假显「点呼実施中」、恢复会带过期 session 进大屏。
        // session 置 null 会让 WS effect 自动断开连接。不调 rollcallEnd：running
        // 场次由后端调度器到 auto_end 自动结算，前端不替不在场的老师提前记欠席
        setRoute("login");
        setTeacher(null);
        setAuthToken(null);
        setAuthProfile(null);
        setLiveMode(false);
        setSession(null);
        setStudents([]);
        setNfcSeq(0);
        // C4: 清上一场点呼结果，防同浏览器换老师登录串号看到前一位的点呼结果
        setLastEnded(null);
        setLastSummary(null);
        idleWarned.current = false; // web#11: 踢回登录后清警告标记
        try {
          sessionStorage.removeItem("tomoshibi_auth");
        } catch (e) {
          /* sessionStorage 失败忽略 */
        }
        setToast({
          type: "warn",
          msg: "操作がないため再ログイン画面に戻りました",
        });
      } else if (!idleWarned.current && idle > TIMEOUT_WARN_MS) {
        idleWarned.current = true; // web#11
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
          "[App] rollcallTodaySessions 失敗 → backendReachable=false",
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
      // C4: 清上一场点呼结果，防同浏览器换老师登录串号看到前一位的点呼结果
      setLastEnded(null);
      setLastSummary(null);
      setToast({
        type: "warn",
        msg: "セッションが切れました。再度ログインしてください。",
      });
    });
    // cleanup：传 null 清除 401 拦截回调（client.ts 签名已放宽收 null）。
    return () => api.setOnUnauthorized(null);
  }, []);

  // web#13: 删 listTeachers effect（结果只写进死状态 backendTeachers，无消费方）

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
    const fetchApps = () => {
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
    };
    fetchApps();
    // 复审 W2：侧栏「申請」徽章 60 秒自动重拉（旧 Shell 内 60s 轮询迁到 App 单一数据源后漏了 liveness）。
    // 别的学生新提交一份需本人审的届时，老师停在任意页也能看到徽章更新、不用手动刷新。
    const timer = setInterval(fetchApps, 60000);
    return () => {
      cancelled = true;
      clearInterval(timer);
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
            // web#43: 朗读移出 setStudents updater（StrictMode 开发模式 updater 双调用会重复朗读）
            const hit = studentsRef.current.find(
              (s) => s.key === event.student_id,
            );
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
            setStudents((list) =>
              list.map((s) =>
                s.key === event.student_id
                  ? {
                      ...s,
                      status: event.status === "late" ? "late" : "ok",
                      checkinAt:
                        event.checked_at ||
                        new Date().toTimeString().slice(0, 8),
                      // web#12: WS 若带 event_id 则回写 lastEventId（后端当前 checkin 广播未推该字段，有则用、无则保留）
                      lastEventId: event.event_id || s.lastEventId,
                    }
                  : s,
              ),
            );
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
                      // web#12: WS override 若带 event_id 则回写（后端当前未推，有则用）
                      lastEventId: event.event_id || s.lastEventId,
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
        // 带上有效权限组供 canManage 判功能入口显隐（TW-001/048）
        permission_group: (profile && profile.permission_group) ?? null,
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
  // web#13: 删死代码 pickTeacher（无调用点；登录走 loginOk）
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
    // C4: 清上一场点呼结果，防同浏览器换老师登录串号看到前一位的点呼结果
    setLastEnded(null);
    setLastSummary(null);
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
    // 后端 checked_in_at 是完整 ISO 串，归一成 JST 的 HH:MM:SS，与 WS checkin 路径显示一致
    checkinAt: e.checked_in_at
      ? new Date(e.checked_in_at).toLocaleTimeString("en-GB", {
          timeZone: "Asia/Tokyo",
          hour12: false,
        })
      : e.checked_in_at,
    // 5-27: 该学生最新 RollCallEvent.id — OverrideModal 调 PATCH /events/{id} 用
    // init 状态学生没 event = null（OverrideModal 收到 null 走 demo 路径）
    lastEventId: e.last_event_id || null,
    health: null,
    pending: null,
    override: null,
    exemptReason: null,
  });

  const startSession = async (name: string) => {
    setNfcSeq(0); // 新场次先清零 NFC 计数，否则指示灯继承上一场计数、未刷卡就显「受信 OK」（codex 复审 minor / C31 配套）
    // 从 name 判别 backend session：含「朝」判 morning，其余（夜点呼等）判 evening。
    // 非「朝」一律归 evening，这样不依赖晩/夜的表记差异也能正确判别（C32 修复）。
    const wantType = name.includes("朝") ? "morning" : "evening";
    // web#44: wantType 必非空，「wantType &&」永真无过滤 → 直接按 session_type 找
    const sess =
      backendReachable &&
      (todaySessions || []).find((s: any) => s.session_type === wantType);

    if (sess && authToken) {
      try {
        try {
          await api.rollcallStart(sess.id, authToken);
        } catch (startErr: any) {
          // 場次已在跑（空闲超时清了本地状态 / 别的端已开始）→ 不是失败，
          // 直接拉 board 重进 live。不识别这个码的话老师会被挡在「開始できません」
          // 外面，而后端场次还在跑、点呼机还在收
          if (!startErr || startErr.code !== "ALREADY_RUNNING") {
            throw startErr;
          }
        }
        const board = await api.rollcallBoard(sess.id, authToken);
        const students = (board.entries || []).map((e) =>
          _boardEntryToStudent(e, teacher.dorm),
        );
        setStudents(students);
        // 经过时间基准：重进已在跑的场次（ALREADY_RUNNING 路径）用后端真实开始
        // 时刻，否则大屏「経過」从重进瞬间起算是错的；新开场次列表快照里
        // started_at 还是 null → 用当前时刻
        const startedAtMs = sess.started_at
          ? new Date(sess.started_at).getTime()
          : Date.now();
        setSession({ name, sessionId: sess.id, startedAt: startedAtMs });
        setLiveMode(true);
        setToast({
          type: "ok",
          msg: `サーバーに接続しました：${board.entries.length}名`,
        });
        return;
      } catch (err) {
        // C5: 无演示继续逻辑，旧「デモ表示で継続」warn 文案撒谎且会被下方 error toast 覆盖。
        // rollcallStart 可能已让后端场次起动（点呼机已在收卡），board 拉取才失败——
        // 此时再点一次会走上面的 ALREADY_RUNNING 分支救回，故提示为可重试的准确文案并 return。
        console.warn("[App] rollcallStart/Board 失敗", err);
        setToast({
          type: "error",
          msg: "通信に失敗しました。点呼は開始されている可能性があります。もう一度お試しください。",
        });
        return;
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
    let endFailed = false; // 终了保存失败标志 — 末尾据此决定弹成功还是保留失败警告
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
        endFailed = true;
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
    // 终了保存失败时保留 catch 里的失败警告——原来这里的 if/else 两分支完全相同、
    // 都无条件弹成功 toast，把「保存に失敗しました」覆盖成「保存されました」，
    // 老师以为落库了实际没有
    if (!endFailed) {
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
    const backendStatus = _frontStatusToBackend(patch.status);
    // 真实 session（有 sessionId + authToken）= 走后端落库；否则是 demo 模式（纯本地）。
    const hasRealSession = !!(
      authToken &&
      session &&
      session.sessionId &&
      target
    );
    let backendOk = false;
    // web#12: 成功后要把 eventId 写回学生 lastEventId，否则同生第二次改判仍走 POST
    let resolvedEventId: string | null = target ? target.lastEventId : null;
    if (hasRealSession) {
      // baselineCreated：init 学生的 POST 基线已落库（codex M1）。若随后 PATCH 失败，DB 里
      // 已有一条 present/late 基线、与本地不一致 → catch 里要重拉 board 让 UI 对齐 DB，
      // 不能简单报「失败」让老师以为啥都没改（实际学生已被标到场）。
      let baselineCreated = false;
      try {
        let eventId = target.lastEventId;
        if (!eventId) {
          // init（未点呼）学生本场没有 event：先 POST 建一条手动基线 checkin 落库，再按需
          // PATCH 到目标状态。原来这种情况直接跳过后端、只改前端，点呼结束 _settle_absent
          // 会把这名「老师当面确认出席」的学生记成欠席 + 扣 1.0 分（TW-008，点呼最常见操作）。
          const created = await api.rollcallCheckin(
            session.sessionId,
            { student_id: target.key, status_source: "manual_checkin" },
            authToken,
          );
          baselineCreated = true;
          eventId = created.id;
          // POST 按时刻判 present/late；与老师选的目标状态不一致时再 PATCH 修正
          // （一致则跳过，避免撞 PATCH 的 no-op 守卫 409）。
          if (created.base_status !== backendStatus) {
            await api.patchRollcallEvent(
              eventId,
              { to_status: backendStatus, reason: patch.reason },
              authToken,
            );
          }
        } else {
          await api.patchRollcallEvent(
            eventId,
            { to_status: backendStatus, reason: patch.reason },
            authToken,
          );
        }
        resolvedEventId = eventId; // web#12: POST/PATCH 成功后的 event id
        backendOk = true;
        setToast({
          type: "ok",
          msg: `${target.name} の状態を「${_statusLabelJa(patch.status)}」に変更しました`,
        });
        // 注：backend 异步 WebSocket broadcast 也会回推 setStudents，这里乐观更新保证 UI 即时反映
      } catch (err) {
        console.warn("[App] saveOverride backend 失败", err);
        // TW-042：失败时不要乐观改色、不要报成功。原来失败也照走本地更新 + 末尾无条件
        // 「調整が反映されました」成功 toast，覆盖掉警告，让老师误以为改判成功（实际后端没变）。
        if (baselineCreated && session && session.sessionId) {
          // codex M1：POST 基线已落库但 PATCH 失败 → DB 已记 present/late，与本地不一致。
          // 重拉 board 让 UI 反映 DB 真实状态（学生此刻是「到场」基线），并提示老师再调整一次
          // （此时该生已有 event，再次改判走 PATCH 路径即可）。避免「UI 说失败、DB 却记了到场」。
          try {
            const board = await api.rollcallBoard(session.sessionId, authToken);
            setStudents(
              (board.entries || []).map((e) =>
                _boardEntryToStudent(e, teacher.dorm),
              ),
            );
          } catch (_) {
            /* board 重拉失败忽略，下次刷新自愈 */
          }
          setToast({
            type: "warn",
            msg: `${target.name} の基準は記録されましたが状態調整に失敗しました。もう一度調整してください`,
          });
        } else {
          setToast({
            type: "error",
            msg: "変更の保存に失敗しました。もう一度お試しください",
          });
        }
        setOverrideTarget(null);
        return;
      }
    }
    // 本地 state 同步：仅在 backend 成功、或 demo 模式（无真实 session）时更新。
    setStudents((list) =>
      list.map((s) =>
        s.key === overrideTarget.key
          ? {
              ...s,
              status: patch.status,
              // web#12: 回写 lastEventId，避免同生二次改判仍当 init 走 POST
              lastEventId: resolvedEventId || s.lastEventId,
              checkinAt:
                patch.status === "ok"
                  ? s.checkinAt || new Date().toTimeString().slice(0, 8)
                  : s.checkinAt,
              override: {
                reason: patch.reason,
                by: teacher.name + " 先生",
              },
              // pending 不在这里清 — 弹层里的假「承認/却下」已删（审批走申请页
              // 真接口），标记保持到审批完成后刷新
              pending: s.pending,
              exemptReason:
                patch.status === "exempt"
                  ? s.exemptReason || patch.reason
                  : s.exemptReason,
            }
          : s,
      ),
    );
    setOverrideTarget(null);
    // demo 模式（无真实 session）才在这里补一个成功 toast；真实 session 的成功 toast 上面已出。
    if (!hasRealSession) {
      setToast({ type: "ok", msg: "調整が反映されました" });
    }
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

  // web#13: 删死代码 onTeacherDelete / onTeacherAdd（仅互相引用 setTeachers，从不作 prop 传出）

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
  // SelectTeacherScreen 组件保留在 src/components/SelectTeacherScreen.tsx，作为 v1.1 候补 — 暂不使用。
  // app
  if (liveMode && session) {
    return (
      <>
        <LiveRollCall
          teacher={teacher}
          sessionName={session.name}
          startedAt={session.startedAt}
          students={students}
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
    case "rollcall-reports":
      // 点呼「学生からの報告」处理页 —— 从着陆页入口进（onNav），点「戻る」回点呼首页。
      body = (
        <RollCallReportsPage
          authToken={authToken}
          onBack={() => setPage("roll-call")}
        />
      );
      break;
    case "applications":
      body = (
        <ApplicationsPage
          onOpen={setOutstayTarget}
          backendApplications={backendApplications}
          onNav={nav}
          authToken={authToken}
        />
      );
      break;
    case "outings":
      // 2026-07-22 itsuki 拍板「事后确认制」— 外出申请（当天回寮）的老师侧管理页。
      // 跟上面的 applications（出寮届 / 过夜 / 多级审批）是两套东西，别合并。
      body = <OutingsPage authToken={authToken} />;
      break;
    case "proxy-application":
      // 2026-06-05 杭田需求「五-3」— 老师代録出寮届表单
      body = <ProxyApplicationPage authToken={authToken} />;
      break;
    case "discipline":
      body = <DisciplinePage teacher={teacher} authToken={authToken} />;
      break;
    case "cleaning":
      body = <CleaningPage teacher={teacher} authToken={authToken} />;
      break;
    case "records":
      body = <RecordsPage params={pageParams} authToken={authToken} />;
      break;
    case "active-leaves":
      // 2026-06-04 杭田需求「四、出寮者一覧」— 纯只读出寮中寮生表
      body = <ActiveLeavesPage authToken={authToken} />;
      break;
    case "search":
      body = <SearchPage query={searchQuery} authToken={authToken} />;
      break;
    case "notifications":
      body = <NotificationsPage onNav={nav} authToken={authToken} />;
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
    case "reports":
      body = <ReportsPage authToken={authToken} />;
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
          teacher={teacher}
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
        // web#10: sessionActive=session&&!liveMode 永不可达（startSession 总 setLiveMode(true)；
        // 所有 setLiveMode(false) 同时清 session）→ 恒传 false，关掉「点呼実施中」假入口
        sessionActive={false}
        onLogout={logout}
        backendReachable={backendReachable}
        wsStatus={wsStatus}
        authToken={authToken}
        canViewAuditLog={canViewAuditLog}
        // web#51: 待审申请数由 App 单一数据源下传。pendingForMe 已按「待我审」筛好
        // （后端 status ∈ {pending, approved_partial}——多级审批链里前序角色批过仍等本人批的也算），
        // 故直接取长度，别再按 status===pending 收窄（复审 W1：否则 approved_partial 件漏计、数字偏少）。
        pendingAppsCount={
          Array.isArray(backendApplications) ? backendApplications.length : null
        }
        onSwitchTeacher={() => {
          // 5-27 拍板：切替＝ログアウト相当（实名账户 = 必須再認証）。
          // sessionStorage 不清 — lastTeacherId 保留可让 LoginScreen 卡片高亮「前回」
          logout();
        }}
        onSearch={search}
        // web#10: onResumeLive 假入口一并废掉（无可达 sessionActive 路径）
        onResumeLive={() => {}}
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
            // 只有 approve/reject 真的落库 → 才报成功。其余动作（如「保留/質問あり」）后端
            // 无对应处理，不能给成功 toast（TW-045：原来一律报「…しました」，让老师误以为
            // 已处理，实际申请仍 pending、学生零通知）。「質問あり」按钮本身已在 Modal 移除。
            if (a === "approved" || a === "rejected") {
              setToast({
                type: "ok",
                msg: `申請を${a === "approved" ? "承認" : "却下"}しました · 寮生へメール通知送信済み`,
              });
            }
          }}
          onReturn={async (reason) => {
            // 差戻 —— 把届退回给学生修改重提（C42 老师侧）。
            // web#9: 只有 backend 真实数据才调接口并报成功；demo 不报「送信済み」
            const backendApp = outstayTarget._backend;
            if (backendApp && authToken) {
              try {
                await api.returnApplication(backendApp.id, reason, authToken);
                // 成功后 refetch pending list（该 application 会从待审列表消失）
                try {
                  const refreshed = await api.pendingForMe(authToken);
                  setBackendApplications(refreshed);
                } catch (_) {
                  // refetch 失败忽略（UI 下次打开时会自愈）
                }
                setOutstayTarget(null);
                // web#9: 成功 toast 只在 backend 成功分支内
                setToast({
                  type: "ok",
                  msg: "申請を差戻しました · 寮生へメール通知送信済み",
                });
              } catch (err: any) {
                console.warn("[App] returnApplication 失敗", err);
                // 后端失败码：409 CANNOT_RETURN（非审查中）/ 403 APPROVAL_NOT_REQUIRED（非当前审批者）
                // web#9：失败用 error 红色（web#8 已引入 danger 配色），与「デモ未保存」黄 warn 区分
                setToast({
                  type: "error",
                  msg: `申請を差戻できませんでした（${err.status || "通信エラー"}）。画面は閉じます。`,
                });
                setOutstayTarget(null);
              }
            } else {
              // web#9: demo / 无 _backend — 只关弹窗并诚实提示，不许假报「送信済み」
              setOutstayTarget(null);
              setToast({
                type: "warn",
                msg: "デモデータのため保存されません",
              });
            }
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
  // web#8: error 用红色 danger；原先非 ok 一律黄 warn，失败 toast 看起来像警告
  const c =
    toast.type === "ok"
      ? [T.ok, T.okSoft, T.okBorder]
      : toast.type === "error"
        ? [T.danger, T.dangerSoft, T.dangerBorder]
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
