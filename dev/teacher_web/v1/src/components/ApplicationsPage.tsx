import React from "react";
import { RYO } from "../theme";
import { DormBadge, StateBadge } from "./shared";
import { isLateSubmission } from "../utils";
import type { Application } from "../api/types";

// 源 index.html 15790-16408（components/applications.jsx 块）。
// /applications 落地页 + 外泊详情弹窗（按真实表单数字化）。
//
// ⭐ 外泊申請の提出期限ルール (2026-04-22 itsuki 拍板):
//   出発日の属する週の水曜日 23:59 / 出発予定時刻の 48 時間前，いずれか早い方。
//   期限後の申請は受付不可 → iOS App でも送信ブロック，寮監との直接面談必要。
//   老師 Web 側では "期限超過" badge + modal でアラート表示。
//
// 界面冻结：JSX 结构 + 所有内联 style 一字不改，仅改作用域引用方式。
// StateBadge / DormBadge 从 ./shared、JST 时间助手 isLateSubmission 从 ../utils import
//（原走 window / 块内重复定义，已迁模块）。
// 块内的 SkeletonTabBody 是死代码（ApplicationsPage 没渲染它）→ 不搬。

// ApplicationsPage / OutstayList / OutstayDetailModal 共用的「UI 形 app」。
// _adaptBackendAppsByKind 把后端 Application[] 转成这个形，_backend 里放原始 Application。
interface OutstayUiApp {
  id: string;
  applicant: string;
  room: string;
  dorm: string;
  depart: string;
  return_: string;
  city: string;
  submitted: string;
  state: string;
  _backend: Application;
}

// Task #6 第 6 步: backendApplications prop 来了就用后端 pendingForMe 的
// Application[] 代替原 window.OUTSTAY_APPS（仅 filter 对应 kind）。
// backendApplications=null/[] 则照旧返回 null（调用方走空状态）。
// backend Application shape 含 kind/leave_date/leave_time/student/status，
// 适配成既有 UI 的 {applicant, room, dorm, depart, return_, city, state, ...} 形。
// Task #16 (5-27): 帰国 / 帰省 / 外泊 3 kind 全部适配。backend Application.kind 是
//「外泊」「帰国」「帰省」3 值 (NetworkModels.swift + schemas.py 一致)。
// taxi 不在 backend kind 里，所以原块用 Skeleton 占位（系统外，Round 4 议题）。
function _adaptBackendAppsByKind(
  apps: Application[] | null | undefined,
  kind: string,
): OutstayUiApp[] | null {
  if (!Array.isArray(apps)) return null;
  const filtered = apps.filter((a) => a.kind === kind);
  if (filtered.length === 0) return null;
  return filtered.map((a) => ({
    id: a.id,
    applicant: a.student ? a.student.name : "(unknown)",
    room: a.student ? a.student.room_no : "",
    dorm: a.student && a.student.dorm_unit ? "men" : "women",
    depart: `${a.leave_date} ${a.leave_time}`,
    return_: `${a.return_date} ${a.return_time}`,
    city:
      (a.stay_locations && a.stay_locations[0] && a.stay_locations[0].name) ||
      a.reason ||
      "",
    submitted: a.submitted_at,
    state:
      a.status === "pending"
        ? "pending"
        : a.status === "approved" || a.status === "approved_partial"
          ? "approved"
          : a.status === "rejected"
            ? "rejected"
            : a.status === "returned"
              ? "question"
              : a.status,
    _backend: a,
  }));
}

// 向后兼容 alias（旧 _adaptBackendOutstay 调用还在的话）
function _adaptBackendOutstay(
  apps: Application[] | null | undefined,
): OutstayUiApp[] | null {
  return _adaptBackendAppsByKind(apps, "外泊");
}

export function ApplicationsPage({
  onOpen,
  backendApplications,
  authToken,
  onNav,
}: {
  onOpen: (app: OutstayUiApp) => void;
  backendApplications: Application[] | null;
  authToken: string;
  // 代録（代学生提交出寮届）入口跳转 — 低频功能，已从左侧导航移除，入口收到本页。
  onNav: (view: string) => void;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("outstay");
  const [sub, setSub] = React.useState("pending");

  // Task #16: 3 kind 全部 backend → UI shape 适配
  const adaptedOutstay = _adaptBackendAppsByKind(backendApplications, "外泊");
  const adaptedReturn = _adaptBackendAppsByKind(backendApplications, "帰国");
  const adaptedHome = _adaptBackendAppsByKind(backendApplications, "帰省");
  const outstayApps = adaptedOutstay || [];
  const returnApps = adaptedReturn || [];
  const homeApps = adaptedHome || [];
  const outstayPending = outstayApps.filter(
    (a) => a.state === "pending",
  ).length;
  const returnPending = returnApps.filter((a) => a.state === "pending").length;
  const homePending = homeApps.filter((a) => a.state === "pending").length;
  // 含タクシー预约的申请（kind 横断・_backend.taxi_reservation_time 非空）— itsuki 2026-06-03 防漏看
  const taxiApps = [...outstayApps, ...returnApps, ...homeApps].filter(
    (a) => a._backend && a._backend.taxi_reservation_time,
  );
  const taxiPending = taxiApps.filter((a) => a.state === "pending").length;
  const tabs = [
    { k: "outstay", label: "外泊", badge: outstayPending },
    { k: "return", label: "帰国", badge: returnPending },
    { k: "home", label: "帰省", badge: homePending },
    { k: "taxi", label: "タクシー", badge: taxiPending },
  ];

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 600,
        }}
      >
        申請 &gt; {tabs.find((t) => t.k === tab)!.label}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          margin: "4px 0 18px",
          gap: 12,
        }}
      >
        <h1
          style={{
            fontSize: 24,
            fontWeight: 700,
            margin: 0,
            letterSpacing: -0.3,
          }}
        >
          申請センター
        </h1>
        {/* 代録（代学生提交出寮届）— 低频功能，从左侧导航移除后入口收到这里。 */}
        <button
          onClick={() => onNav("proxy-application")}
          style={{
            padding: "8px 16px",
            background: T.surface,
            color: T.cobaltDeep,
            border: `1px solid ${T.cobalt}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
            whiteSpace: "nowrap",
            flexShrink: 0,
          }}
        >
          ＋ 代録（出寮届の代理提出）
        </button>
      </div>

      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          marginBottom: 18,
        }}
      >
        {tabs.map((t) => (
          <button
            key={t.k}
            onClick={() => {
              setTab(t.k);
              setSub("pending");
            }}
            style={{
              padding: "10px 18px",
              background: "transparent",
              border: "none",
              borderBottom:
                tab === t.k ? `2px solid ${T.cobalt}` : "2px solid transparent",
              color: tab === t.k ? T.cobaltDeep : T.ink3,
              fontWeight: tab === t.k ? 700 : 500,
              fontFamily: "inherit",
              fontSize: 13,
              cursor: "pointer",
              marginBottom: -1,
              position: "relative",
            }}
          >
            {t.label}
            {t.badge > 0 && (
              <span
                style={{
                  marginLeft: 6,
                  fontSize: 10,
                  background: T.danger,
                  color: "#fff",
                  padding: "1px 6px",
                  borderRadius: 8,
                  fontWeight: 700,
                }}
              >
                {t.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* 外泊期限规则只适用于外泊届 — 帰国/帰省规则不同，所以不显示 */}
      {tab === "outstay" && <OutstayRuleBanner />}

      {/* Task #16: 外泊 / 帰国 / 帰省 3 tab 共用 OutstayList (UI shape 相同)。
          taxi tab 也走 OutstayList（filter 出含タクシー预约的申请）。*/}
      {tab === "outstay" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={outstayApps}
        />
      )}
      {tab === "return" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={returnApps}
        />
      )}
      {tab === "home" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={homeApps}
        />
      )}
      {tab === "taxi" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={taxiApps}
        />
      )}
    </div>
  );
}

// 外泊申请提出期限规则横幅 — 可折叠
function OutstayRuleBanner() {
  const T = RYO;
  const [open, setOpen] = React.useState(true);
  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          padding: "7px 14px",
          background: "transparent",
          color: T.ink3,
          border: `1px dashed ${T.lineStrong}`,
          borderRadius: 8,
          fontFamily: "inherit",
          fontSize: 11,
          cursor: "pointer",
          marginBottom: 14,
        }}
      >
        📅 外泊申請の提出期限ルールを表示
      </button>
    );
  }
  return (
    <div
      style={{
        padding: "12px 16px",
        background: T.cobaltSoft,
        color: T.cobaltDeep,
        border: `1px solid ${T.infoBorder}`,
        borderRadius: 10,
        fontSize: 12,
        lineHeight: 1.7,
        marginBottom: 14,
        display: "flex",
        gap: 12,
        alignItems: "flex-start",
      }}
    >
      <span style={{ fontSize: 16 }}>📅</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>
          外泊申請 提出期限ルール
        </div>
        <div>
          提出期限 = <b>出発日の属する週の水曜日 23:59</b> または{" "}
          <b>出発予定時刻の 48 時間前</b>、<b>いずれか早い方</b>。
        </div>
        <div style={{ marginTop: 3 }}>
          期限後は iOS App から送信できません。やむを得ない事情がある場合は、
          <b>必ず生徒本人が寮監室に来て直接相談</b>してください。
        </div>
      </div>
      <button
        onClick={() => setOpen(false)}
        style={{
          background: "transparent",
          border: "none",
          color: T.cobaltDeep,
          cursor: "pointer",
          fontSize: 14,
          padding: 0,
        }}
      >
        ×
      </button>
    </div>
  );
}

// 申请一覧表（外泊 / 帰国 / 帰省 / タクシー 4 tab 共用）
function OutstayList({
  sub,
  setSub,
  onOpen,
  apps: appsProp,
}: {
  sub: string;
  setSub: (s: string) => void;
  onOpen: (app: OutstayUiApp) => void;
  apps: OutstayUiApp[];
}) {
  const T = RYO;
  // Task #6 第 6 步 + Task #16: apps prop 是 array 就一定用（空数组也显示空状态）。
  const apps = Array.isArray(appsProp) ? appsProp : [];
  const subs = ["pending", "approved", "rejected", "question", "all"];
  const subLabels: Record<string, string> = {
    pending: "審査待ち",
    approved: "承認済",
    rejected: "却下",
    question: "質問あり",
    all: "全て",
  };
  const filtered = sub === "all" ? apps : apps.filter((a) => a.state === sub);

  return (
    <>
      <div
        style={{
          display: "flex",
          gap: 6,
          marginBottom: 14,
          alignItems: "center",
        }}
      >
        {subs.map((s) => (
          <button
            key={s}
            onClick={() => setSub(s)}
            style={{
              padding: "5px 12px",
              background: sub === s ? T.cobalt : T.surface,
              color: sub === s ? "#fff" : T.ink2,
              border: `1px solid ${sub === s ? T.cobalt : T.lineStrong}`,
              borderRadius: 999,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {subLabels[s]}
          </button>
        ))}
        <div style={{ flex: 1 }} />
      </div>

      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: T.shadow1,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "140px 70px 80px 140px 140px 90px 120px 110px 90px 80px",
            background: T.surfaceAlt,
            color: T.ink2,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {[
            "申請者",
            "部屋",
            "担当寮",
            "出発日時",
            "帰舎予定",
            "行先",
            "提出時刻",
            "期限",
            "状態",
            "操作",
          ].map((h) => (
            <div key={h} style={{ padding: "10px 12px" }}>
              {h}
            </div>
          ))}
        </div>
        {filtered.map((a, i) => (
          <div
            key={a.id}
            onClick={() => onOpen(a)}
            style={{
              display: "grid",
              gridTemplateColumns:
                "140px 70px 80px 140px 140px 90px 120px 110px 90px 80px",
              borderTop: i > 0 ? `1px solid ${T.line}` : "none",
              fontSize: 12,
              alignItems: "center",
              cursor: "pointer",
              transition: "background .1s",
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.background = T.surfaceAlt)
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.background = "transparent")
            }
          >
            <div style={{ padding: "10px 12px", fontWeight: 600 }}>
              {a.applicant}
            </div>
            <div style={{ padding: "10px 12px", fontFamily: T.mono }}>
              {a.room}
            </div>
            <div style={{ padding: "10px 12px" }}>
              <DormBadge dorm={a.dorm} />
            </div>
            <div
              style={{
                padding: "10px 12px",
                fontFamily: T.mono,
                color: T.ink2,
              }}
            >
              {a.depart}
            </div>
            <div
              style={{
                padding: "10px 12px",
                fontFamily: T.mono,
                color: T.ink2,
              }}
            >
              {a.return_}
            </div>
            <div style={{ padding: "10px 12px" }}>{a.city}</div>
            <div
              style={{
                padding: "10px 12px",
                fontFamily: T.mono,
                color: T.ink3,
              }}
            >
              {a.submitted}
            </div>
            <div style={{ padding: "10px 12px" }}>
              <DeadlineBadge depart={a.depart} submitted={a.submitted} />
            </div>
            <div style={{ padding: "10px 12px" }}>
              <StateBadge s={a.state} />
            </div>
            <div
              style={{
                padding: "10px 12px",
                color: T.cobalt,
                fontSize: 12,
                fontWeight: 700,
                textAlign: "left",
              }}
            >
              詳細 →
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            まだデータがありません
          </div>
        )}
      </div>
    </>
  );
}

// 提出期限 badge — 期限内 / 期限後 两态（本块私有子组件）
function DeadlineBadge({
  depart,
  submitted,
}: {
  depart: string;
  submitted: string;
}) {
  const T = RYO;
  const late = isLateSubmission(depart, submitted);
  const commonStyle = {
    fontSize: 11,
    fontWeight: 700,
    padding: "2px 8px",
    borderRadius: 4,
    letterSpacing: 0.5,
    whiteSpace: "nowrap" as const,
  };
  if (late)
    return (
      <span
        title="期限後提出 · 寮監との面談が必要"
        style={{
          ...commonStyle,
          background: T.dangerSoft,
          color: T.danger,
          border: `1px solid ${T.dangerBorder}`,
        }}
      >
        ⚠ 期限後
      </span>
    );
  return (
    <span
      title="期限内に提出済"
      style={{
        ...commonStyle,
        background: T.okSoft,
        color: T.ok,
        border: `1px solid ${T.okBorder}`,
      }}
    >
      ✓ 期限内
    </span>
  );
}
