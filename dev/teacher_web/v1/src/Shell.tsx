import React from "react";
import { RYO } from "./theme";
import { api } from "./api/client";
import { DormBadge } from "./components/shared";
import tomoshibiIcon from "./assets/tomoshibi-icon.png";

// Shell — 左侧导航 + 顶栏（全局搜索 + WebSocket 状态指示灯 + 登出）。
// 除 /login、/login/select-teacher、/roll-call/live 外的所有页面都用它。

// Shell 在 App() 里接收的 teacher 是从 backend TeacherOut.profile 派生的 UI 对象，
// 字段（name / initial / dorm）与 api/types.ts 的 TeacherProfile 不同 — 这里只列实际用到的字段。
type ShellTeacher = {
  name: string;
  initial: string;
  dorm: string;
};

export function Shell({
  teacher,
  active,
  onNav,
  children,
  sessionActive,
  onLogout,
  onSwitchTeacher,
  onSearch,
  onResumeLive,
  backendReachable,
  wsStatus,
  authToken,
  canViewAuditLog,
}: {
  teacher: ShellTeacher | null;
  active: string;
  onNav: (id: string) => void;
  children: React.ReactNode;
  sessionActive: boolean;
  onLogout: () => void;
  onSwitchTeacher: () => void;
  onSearch: (q: string) => void;
  onResumeLive: () => void;
  // Task #6 真接口对接: null 未知 / true 接通 / false 不可達
  backendReachable: boolean | null;
  // 5-27 spec §11.8: WebSocket 状态 null / connecting / connected / disconnected / failed
  wsStatus: string | null;
  // 全局搜索学生建议用
  authToken: string | null;
  // 操作履历审计页只给管理角色显示（与后端 C_AUDIT_LOG 权限闸一致）。
  canViewAuditLog: boolean;
}) {
  const T = RYO;
  // Task #6 (5-27): 删 WebSocket demo 模拟，按 backendReachable 真实状态切指示灯。
  // backendReachable 来自 App() 的 rollcallTodaySessions fetch 结果（authToken 变化时更新）。
  const wsOk = backendReachable !== false; // null/true → 绿 / false → 红
  const [q, setQ] = React.useState("");
  const [focused, setFocused] = React.useState(false);
  const [nowLabel, setNowLabel] = React.useState(() => formatNowJa());
  // 侧栏徽章真实数字（替代写死的 7 / 3）— 通知未读数 + 待审申请数
  const [notifUnread, setNotifUnread] = React.useState<number | null>(null);
  const [pendingApps, setPendingApps] = React.useState<number | null>(null);
  // 顶栏实时时钟
  React.useEffect(() => {
    const id = setInterval(() => setNowLabel(formatNowJa()), 30000);
    return () => clearInterval(id);
  }, []);
  // ⌘K 聚焦
  React.useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        document.getElementById("global-search-input")?.focus();
      }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  // 侧栏徽章数字 — authToken 来了就拉（通知未读数 + 待审申请数）。
  // 阶段2-C：每 60 秒自动重拉一次，事件产生后侧栏数字会自己更新，老师不用手动刷新。
  // 周期取 60 秒（不是更短）：unread-count 接口每次会触发后端扫现有事件表做懒同步，
  // 频率越高后端越费 —— codex 审查指出这点，小宿舍规模 60 秒足够、又不浪费。
  // （真·WebSocket 瞬时推 + 后端增量水位线同步留 v1.1 — 见 TODO；现有老师 WS 只在点呼会话时连。）
  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    const refresh = () => {
      api
        .notificationUnreadCount(authToken)
        .then((r) => {
          if (!cancelled) setNotifUnread(r.unread_count);
        })
        .catch(() => {
          if (!cancelled) setNotifUnread(null);
        });
      api
        .pendingForMe(authToken)
        .then((list) => {
          if (!cancelled) setPendingApps((list || []).length);
        })
        .catch(() => {
          if (!cancelled) setPendingApps(null);
        });
    };
    refresh();
    const id = setInterval(refresh, 60000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [authToken]);

  // 职位退化为纯显示标签后，菜单不再按职位隐藏 —— 所有老师都能查看所有功能页，
  // 「增删改」的权限由后端权限闸（require_permission）按权限组把关。
  // 7-17 适老化审查拍板（决策 2）：4 组「系统功能分类」改 3 组「宿管任务分类」——
  // 宿管每晚必用的置顶（「今晩の業務」），翻记录类归一组（「記録を見る」），偶尔用的沉底（「管理・設定」）。
  // 徽章（通知未读 / 申请待审）随所属项保留。
  type NavItem = [string, string, number?];
  const NAV_GROUPS: Array<{ title: string; items: NavItem[] }> = [
    {
      title: "今晩の業務",
      items: [
        ["roll-call", "点呼"],
        ["study", "夜学習出席"],
        ["active-leaves", "出寮者一覧"],
        ["applications", "申請", pendingApps || undefined],
        ["notifications", "通知", notifUnread || undefined],
      ],
    },
    {
      title: "記録を見る",
      items: [
        ["records", "点呼記録"],
        ["discipline", "減点・処分"],
        ["cleaning", "清掃罰則"],
      ],
    },
    {
      title: "管理・設定",
      items: [
        ["info", "お知らせ"],
        ["bus", "バス時刻表"],
        // 「コミュニティ管理」= 冷冻中（页面未接后端，菜单摘除防空头承诺；
        // App.tsx 路由 + CommunityPage 组件 + 后端 songs 接口原样保留，复活时恢复本行即可）
        // 投稿通報一覧（App Store UGC 治理 — itsuki 2026-07-20 拍板 A 方案）
        ["reports", "投稿の通報"],
        ["front-desk", "フロント業務"],
        ["accounts", "学生アカウント管理"],
        ["admin-registration-code", "学生登録コード"],
        ["teachers-admin", "教員アカウント管理"],
        // 操作履歴 = 操作记录审计页，只给管理角色显示（后端 C_AUDIT_LOG 把关）。
        ...(canViewAuditLog ? ([["audit-log", "操作履歴"]] as NavItem[]) : []),
      ],
    },
  ];

  const pageLabel =
    {
      "roll-call": "点呼",
      notifications: "通知",
      discipline: "減点・処分",
      cleaning: "清掃罰則",
      applications: "申請",
      "proxy-application": "代録",
      study: "夜学習出席",
      records: "点呼記録",
      "active-leaves": "出寮者一覧",
      info: "お知らせ",
      bus: "バス時刻表",
      community: "コミュニティ管理",
      "front-desk": "フロント業務",
      accounts: "学生アカウント管理",
      "admin-registration-code": "学生登録コード",
      "teachers-admin": "教員アカウント管理",
      "audit-log": "操作履歴",
      summary: "点呼集計",
      search: "検索結果",
    }[active] || "";

  const normalize = (s: string) => (s || "").replace(/\s+/g, "").toLowerCase();
  const qn = normalize(q);
  // 真后端学生检索建议（替代假名单）
  const [backendSuggestions, setBackendSuggestions] = React.useState<
    Array<{ label: string; meta: string; kind: string }>
  >([]);
  React.useEffect(() => {
    if (q.length === 0 || !authToken) {
      setBackendSuggestions([]);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      api
        .listStudents({ q }, authToken)
        .then((res) => {
          if (cancelled) return;
          const items = res.items || [];
          setBackendSuggestions(
            items.map((s) => ({
              label: s.name,
              meta: `${s.room_no}号室 · ${s.student_no}`,
              kind: "student",
            })),
          );
        })
        .catch(() => {
          if (!cancelled) setBackendSuggestions([]);
        });
    }, 200); // 200ms 防抖，避免每键一次请求
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [q, authToken]);
  const studentSuggestions = backendSuggestions;
  // web#14: 「本日/昨日」点呼建议按 JST 当天/前一天动态生成（硬编码 2026-04-22/21 会标错日）
  const jstYmd = (d: Date) =>
    d.toLocaleDateString("sv-SE", { timeZone: "Asia/Tokyo" });
  const todayYmd = jstYmd(new Date());
  const yesterdayYmd = jstYmd(new Date(Date.now() - 86400000));
  const extraSuggestions =
    q.length > 0
      ? [
          {
            label: todayYmd,
            meta: "点呼記録 · 本日",
            kind: "date",
            hay: todayYmd,
          },
          {
            label: yesterdayYmd,
            meta: "点呼記録 · 昨日",
            kind: "date",
            hay: yesterdayYmd,
          },
        ].filter((s) => s.hay.includes(qn))
      : [];
  const suggestions = [...studentSuggestions, ...extraSuggestions].slice(0, 6);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.paper,
        color: T.ink,
        fontFamily: T.font,
        display: "flex",
      }}
    >
      <aside
        style={{
          width: 232,
          flexShrink: 0,
          background: T.surface,
          borderRight: `1px solid ${T.line}`,
          display: "flex",
          flexDirection: "column",
          position: "sticky",
          top: 0,
          height: "100vh",
        }}
      >
        <div
          style={{
            padding: "18px 20px 14px",
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <img
            src={tomoshibiIcon}
            alt=""
            style={{ width: 42, height: 42, borderRadius: 10, flexShrink: 0 }}
          />
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>
              Tomoshibi
            </div>
            <div style={{ fontSize: 10, color: T.ink3, marginTop: 1 }}>
              寮管理システム
            </div>
          </div>
        </div>
        <div style={{ height: 1, background: T.line }} />
        <nav style={{ padding: "10px 10px", flex: 1, overflowY: "auto" }}>
          {NAV_GROUPS.map((group, gi) => (
            <div
              key={group.title}
              style={{
                marginTop: gi === 0 ? 2 : 12,
                paddingTop: gi === 0 ? 0 : 10,
                borderTop: gi === 0 ? "none" : `1px solid ${T.line}`,
              }}
            >
              {/* 7-17 适老化拍板⑦：组标题 11px→12px、导航项 13.5px→15px — 主用户是年长宿管，老花眼基准上调 */}
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  color: T.ink2,
                  letterSpacing: 1,
                  padding: "0 12px 7px",
                }}
              >
                {group.title}
              </div>
              {group.items.map(([id, label, badge]) => {
                const isActive = id === active;
                return (
                  <button
                    key={id}
                    onClick={() => onNav && onNav(id)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      width: "100%",
                      padding: "9px 12px",
                      marginBottom: 2,
                      background: isActive ? T.cobaltSoft : "transparent",
                      color: isActive ? T.cobaltDeep : T.ink2,
                      fontFamily: "inherit",
                      fontSize: 15,
                      fontWeight: isActive ? 600 : 500,
                      border: "none",
                      borderRadius: 8,
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                  >
                    <span>{label}</span>
                    {badge != null && (
                      <span
                        style={{
                          fontSize: 11,
                          background: isActive ? T.cobalt : T.lineStrong,
                          color: "#fff",
                          padding: "1px 8px",
                          borderRadius: 10,
                          fontWeight: 600,
                          fontVariantNumeric: "tabular-nums",
                        }}
                      >
                        {badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
        <div
          style={{
            padding: "12px 16px",
            borderTop: `1px solid ${T.line}`,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 17,
              background: T.cobaltSoft,
              color: T.cobaltDeep,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
              position: "relative",
            }}
          >
            {teacher ? teacher.initial : "田"}
            <span
              title="当番中"
              style={{
                position: "absolute",
                bottom: -2,
                right: -2,
                width: 11,
                height: 11,
                borderRadius: 6,
                background: T.ok,
                border: "2px solid #fff",
              }}
            />
          </div>
          <div style={{ fontSize: 12, flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontWeight: 600,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {teacher ? teacher.name : "—"} 先生
            </div>
            <div style={{ marginTop: 2 }}>
              <DormBadge dorm={teacher ? teacher.dorm : "men"} />
            </div>
          </div>
          <button
            onClick={onSwitchTeacher}
            title="担当者切替"
            style={{
              border: "none",
              background: "transparent",
              color: T.ink3,
              cursor: "pointer",
              padding: 6,
              borderRadius: 6,
              fontSize: 11,
            }}
          >
            切替
          </button>
        </div>
      </aside>

      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
        }}
      >
        <header
          style={{
            height: 60,
            borderBottom: `1px solid ${T.line}`,
            background: T.surface,
            display: "flex",
            alignItems: "center",
            padding: "0 24px",
            gap: 16,
            position: "sticky",
            top: 0,
            zIndex: 5,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: T.ink,
              minWidth: 100,
            }}
          >
            {pageLabel}
          </div>

          {/* 全局搜索 */}
          <div style={{ flex: 1, maxWidth: 520, position: "relative" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                background: T.surfaceAlt,
                border: `1px solid ${focused ? T.cobalt : T.line}`,
                borderRadius: 10,
                padding: "0 10px",
                height: 38,
                gap: 8,
                transition: "border-color .15s",
              }}
            >
              <span style={{ color: T.ink3, fontSize: 14 }}>🔍</span>
              <input
                id="global-search-input"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setTimeout(() => setFocused(false), 150)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && q.trim()) onSearch(q.trim());
                }}
                placeholder="学生名・部屋番号・日付で検索…"
                style={{
                  flex: 1,
                  border: "none",
                  outline: "none",
                  background: "transparent",
                  fontFamily: "inherit",
                  fontSize: 13,
                  color: T.ink,
                }}
              />
              <span
                style={{
                  fontFamily: T.mono,
                  fontSize: 10,
                  color: T.ink3,
                  padding: "2px 6px",
                  border: `1px solid ${T.line}`,
                  borderRadius: 4,
                  background: T.surface,
                }}
              >
                ⌘K
              </span>
            </div>
            {focused && suggestions.length > 0 && (
              <div
                style={{
                  position: "absolute",
                  top: 44,
                  left: 0,
                  right: 0,
                  background: T.surface,
                  border: `1px solid ${T.line}`,
                  borderRadius: 10,
                  boxShadow: T.shadow2,
                  overflow: "hidden",
                  zIndex: 20,
                }}
              >
                {suggestions.map((s, i) => (
                  <div
                    key={i}
                    onMouseDown={() => onSearch(s.label)}
                    style={{
                      padding: "9px 12px",
                      cursor: "pointer",
                      fontSize: 13,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                    }}
                  >
                    <span>{s.label}</span>
                    <span
                      style={{
                        fontSize: 11,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {s.meta}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={{ flex: 1 }} />
          {sessionActive && (
            <button
              onClick={onResumeLive}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "5px 12px",
                background: T.okSoft,
                color: T.ok,
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 600,
                border: `1px solid ${T.okBorder}`,
                fontFamily: "inherit",
                cursor: "pointer",
                flexShrink: 0,
                whiteSpace: "nowrap",
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 4,
                  background: T.ok,
                  animation: "pulse 1.6s infinite",
                }}
              />
              点呼実施中
            </button>
          )}
          <div
            title={
              backendReachable === false
                ? "サーバーに接続できません（デモデータで表示中）"
                : backendReachable === true
                  ? "サーバーに接続中（実データ）"
                  : "サーバー接続を確認中（ログイン直後など）"
            }
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              fontSize: 11,
              color: T.ink3,
              flexShrink: 0,
              whiteSpace: "nowrap",
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                background: wsOk ? T.ok : T.danger,
                animation: wsOk ? "none" : "pulse 1s infinite",
              }}
            />
            <span style={{ fontFamily: T.mono }}>
              {backendReachable === false
                ? "DEMO"
                : backendReachable === true
                  ? "LIVE"
                  : "..."}
            </span>
          </div>
          <div
            style={{
              fontSize: 12,
              color: T.ink3,
              fontFamily: T.mono,
              flexShrink: 0,
              whiteSpace: "nowrap",
            }}
          >
            {nowLabel}
          </div>
          <button
            onClick={onLogout}
            style={{
              padding: "6px 10px",
              background: "transparent",
              color: T.ink3,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 11,
              cursor: "pointer",
              flexShrink: 0,
              whiteSpace: "nowrap",
            }}
          >
            ログアウト
          </button>
        </header>
        {/* 5-27 spec §11.8: WebSocket 再接続中 / 切断 banner */}
        {wsStatus && wsStatus !== "connected" && (
          <div
            style={{
              padding: "8px 18px",
              background: wsStatus === "failed" ? T.dangerSoft : T.warnSoft,
              borderBottom: `1px solid ${wsStatus === "failed" ? T.danger : T.warnBorder}`,
              color: wsStatus === "failed" ? T.danger : T.warn,
              fontSize: 12,
              fontFamily: T.mono,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                background: wsStatus === "failed" ? T.danger : T.warn,
                animation:
                  wsStatus === "failed" ? "none" : "pulse 1.2s infinite",
              }}
            />
            {wsStatus === "connecting" && "リアルタイム接続中…"}
            {wsStatus === "disconnected" &&
              "リアルタイム再接続中… 操作は続行できます"}
            {wsStatus === "failed" &&
              "リアルタイム接続に失敗しました。画面の自動更新が停止しています。ページを再読み込みしてください"}
          </div>
        )}
        <div style={{ flex: 1, overflow: "auto", position: "relative" }}>
          {children}
        </div>
      </div>
    </div>
  );
}

// Shell 私有时刻格式化助手 — 不 export。
function formatNowJa() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const jaDay = ["日", "月", "火", "水", "木", "金", "土"][d.getDay()];
  return `${y}-${m}-${day}（${jaDay}） ${hh}:${mm}`;
}
