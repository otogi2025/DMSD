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
  currentRole,
  authToken,
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
  // 5-27 codex 审查 #11: backend authProfile.role — 教师管理 nav 按角色 hide
  currentRole: string | null;
  // 全局搜索学生建议用
  authToken: string | null;
}) {
  const T = RYO;
  // Task #6 (5-27): 删 WebSocket demo 模拟，按 backendReachable 真实状态切指示灯。
  // backendReachable 来自 App() 的 rollcallTodaySessions fetch 结果（authToken 变化时更新）。
  const wsOk = backendReachable !== false; // null/true → 绿 / false → 红
  const [q, setQ] = React.useState("");
  const [focused, setFocused] = React.useState(false);
  const [nowLabel, setNowLabel] = React.useState(() => formatNowJa());
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

  // 5-27 codex 审查 #11: 教师管理 nav 按 currentRole 过滤（与 backend teachers.py TEACHER_ADMIN_ROLES 对齐）
  const TEACHER_ADMIN_ROLES_FRONT = ["寮務部長", "寮務課長", "寮監"];
  const canManageTeachers =
    currentRole && TEACHER_ADMIN_ROLES_FRONT.includes(currentRole);
  // 5-30: 事案録入 + 指導履歴 — 寮務系角色可见（与 backend incidents.py _INCIDENT_ROLES 对齐）
  const GUIDANCE_ROLES_FRONT = [
    "寮務部長",
    "寮務課長",
    "寮監",
    "寮務一般教師",
    "管理係",
  ];
  const canGuidance = currentRole && GUIDANCE_ROLES_FRONT.includes(currentRole);
  // 2026-06-05 代録（出寮届）— 限寮務系 5 角色（与 backend _DAIROKU_ROLES 对齐）
  const DAIROKU_ROLES_FRONT = [
    "寮務部長",
    "寮務課長",
    "寮監",
    "寮務一般教師",
    "管理係",
  ];
  const canProxyApply =
    currentRole && DAIROKU_ROLES_FRONT.includes(currentRole);
  const NAV: Array<[string, string, number?]> = [
    ["roll-call", "点呼"],
    ["notifications", "通知", 7],
    ["discipline", "規律・処分"],
    ["applications", "申請", 3],
    ...(canProxyApply
      ? ([["proxy-application", "代録"]] as Array<[string, string]>)
      : []),
    ["study", "学習出席"],
    ["records", "記録"],
    ["active-leaves", "出寮者一覧"],
    ["cleaning", "清掃確認"],
    ["info", "お知らせ・バス"],
    ["community", "コミュニティ管理"],
    ["front-desk", "フロント業務"],
    ["accounts", "学生アカウント管理"],
    ["admin-registration-code", "学生登録コード"],
    ...(canGuidance
      ? ([["incidents", "事案記録"]] as Array<[string, string]>)
      : []),
    ...(canGuidance
      ? ([["disclosure-requests", "開示申請"]] as Array<[string, string]>)
      : []),
    ...(canManageTeachers
      ? ([["teachers-admin", "教員アカウント管理"]] as Array<[string, string]>)
      : []),
  ];

  const pageLabel =
    {
      "roll-call": "点呼",
      notifications: "通知",
      discipline: "規律・処分",
      applications: "申請",
      "proxy-application": "代録",
      study: "学習出席",
      records: "記録",
      "active-leaves": "出寮者一覧",
      cleaning: "清掃確認",
      info: "お知らせ・バス",
      community: "コミュニティ管理",
      "front-desk": "フロント業務",
      accounts: "学生アカウント管理",
      "admin-registration-code": "学生登録コード",
      "teachers-admin": "教員アカウント管理",
      incidents: "事案記録",
      "disclosure-requests": "開示申請",
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
  const extraSuggestions =
    q.length > 0
      ? [
          {
            label: "2026-04-22",
            meta: "点呼記録 · 本日",
            kind: "date",
            hay: "2026-04-22",
          },
          {
            label: "2026-04-21",
            meta: "点呼記録 · 昨日",
            kind: "date",
            hay: "2026-04-21",
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
            style={{ width: 30, height: 30, borderRadius: 8 }}
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
          {NAV.map(([id, label, badge]) => {
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
                  fontSize: 13.5,
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
          <div style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono }}>
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
