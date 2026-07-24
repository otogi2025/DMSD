import React from "react";
import { RYO } from "../theme";
import { DormBadge, StateBadge } from "./shared";
import { isLateSubmission } from "../utils";
import type { Application, StudyOnlineRequestOut } from "../api/types";
import { api } from "../api/client";

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
    applicant: a.student ? a.student.name : "（削除済み）",
    room: a.student ? a.student.room_no : "",
    dorm: a.student && a.student.dorm_unit === 4 ? "women" : "men",
    depart: `${a.leave_date} ${a.leave_time}`,
    return_: `${a.return_date} ${a.return_time}`,
    city:
      (a.stay_locations && a.stay_locations[0] && a.stay_locations[0].name) ||
      a.reason ||
      "",
    submitted: a.submitted_at,
    // approved_partial（他役职已批、仍待当前役职决裁）归「未処理(pending)」：本列表数据源
    // pending-for-me 只返回「待当前役职决裁」的届，故 approved_partial 在这里语义就是
    // 「还等我处理」。原来把它和 approved 一起映成「承認済」，导致它从未処理徽章 + 默认
    // 待审视图漏掉，多级审批链中段役职看不到自己的待决裁案件（TW-009）。
    state:
      a.status === "pending"
        ? "pending"
        : a.status === "approved_partial"
          ? "pending"
          : a.status === "approved"
            ? "approved"
            : a.status === "rejected"
              ? "rejected"
              : a.status === "returned"
                ? "question"
                : a.status,
    _backend: a,
  }));
}

export function ApplicationsPage({
  onOpen,
  backendApplications,
  onNav,
  authToken,
}: {
  onOpen: (app: OutstayUiApp) => void;
  backendApplications: Application[] | null;
  // 代録（代学生提交出寮届）入口跳转 — 低频功能，已从左侧导航移除，入口收到本页。
  onNav: (view: string) => void;
  // 在线学习申请 tab 自给自足拉取 + 审批要用（不走 backendApplications 统一流）
  authToken: string | null;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("outstay");
  const [sub, setSub] = React.useState("pending");

  // 在线学习申请（UI 上的「オンライン学習」tab）— 独立端点 /study/online-requests，
  // 权限 C_APPROVAL（与外泊等同属「申請」页，但数据结构独立、不走 pendingForMe）。
  // 本 tab 自己拉待审列表 + 承認/却下，审批后刷新（照夜学習页欠席届收件箱做法）。
  const [onlineList, setOnlineList] = React.useState<
    StudyOnlineRequestOut[] | null
  >(null);
  const [onlineErr, setOnlineErr] = React.useState("");
  const [onlineActing, setOnlineActing] = React.useState<
    Record<string, boolean>
  >({});

  const refetchOnline = React.useCallback(async () => {
    // C9: 无令牌也要让 onlineList 从 null 收敛，否则永远卡「読み込み中…」
    if (!authToken) {
      setOnlineList([]);
      return;
    }
    setOnlineErr("");
    try {
      const list = await api.onlineRequests(authToken, "pending");
      setOnlineList(list || []);
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 403) {
        setOnlineErr("オンライン学習申請の審査は「承認」権限が必要です");
      } else {
        setOnlineErr(`申請の取得に失敗 (${(ex && ex.status) || "network"})`);
      }
      // C9: 失败时也让加载态收敛（null→[]），否则 spinner 与错误红条同时永久显示
      setOnlineList([]);
    }
  }, [authToken]);

  React.useEffect(() => {
    refetchOnline();
  }, [refetchOnline]);

  const doDecideOnline = async (
    id: string,
    decision: "approved" | "rejected",
  ) => {
    if (onlineActing[id]) return; // 防双击窗口重复承認/却下
    setOnlineActing((m) => ({ ...m, [id]: true }));
    try {
      await api.decideOnlineRequest(id, decision, undefined, authToken!);
      await refetchOnline();
    } catch (e) {
      const ex = e as { status?: number };
      setOnlineErr(`申請処理に失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setOnlineActing((m) => ({ ...m, [id]: false }));
    }
  };

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
  // 列表只拉 status=pending，故全部即待审数
  const onlinePending = (onlineList || []).length;
  const tabs = [
    { k: "outstay", label: "外泊", badge: outstayPending },
    { k: "return", label: "帰国", badge: returnPending },
    { k: "home", label: "帰省", badge: homePending },
    { k: "taxi", label: "タクシー", badge: taxiPending },
    { k: "online", label: "オンライン学習", badge: onlinePending },
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
      {/* web#20: DeadlineBadge 仅外泊规则 — 只在 outstay tab 传 showDeadline */}
      {tab === "outstay" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={outstayApps}
          showDeadline
        />
      )}
      {tab === "return" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={returnApps}
          showDeadline={false}
        />
      )}
      {tab === "home" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={homeApps}
          showDeadline={false}
        />
      )}
      {tab === "taxi" && (
        <OutstayList
          sub={sub}
          setSub={setSub}
          onOpen={onOpen}
          apps={taxiApps}
          showDeadline={false}
        />
      )}

      {/* オンライン学習申請 収件箱 — 独立端点，收件箱样式照夜学習页欠席届一览。
          只拉 status=pending，承認/却下后从列表消失（下一次 refetchOnline 只回 pending）。*/}
      {tab === "online" && (
        <>
          {onlineErr && (
            <div
              style={{
                padding: 12,
                background: T.dangerSoft,
                color: T.danger,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 8,
                fontSize: 12,
                marginBottom: 14,
              }}
            >
              {onlineErr}
            </div>
          )}
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
                gridTemplateColumns: "180px 160px 1fr 80px 90px 150px 160px",
                background: T.surfaceAlt,
                color: T.ink2,
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: 1,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              {[
                "学生",
                "期間",
                "理由",
                "契約書",
                "状態",
                "提出時刻",
                "操作",
              ].map((h) => (
                <div key={h} style={{ padding: "10px 14px" }}>
                  {h}
                </div>
              ))}
            </div>
            {onlineList === null && (
              <div
                style={{
                  padding: 40,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 13,
                }}
              >
                読み込み中…
              </div>
            )}
            {onlineList !== null && onlineList.length === 0 && (
              <div
                style={{
                  padding: 40,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 13,
                }}
              >
                審査待ちのオンライン学習申請はありません
              </div>
            )}
            {(onlineList || []).map((o, i) => (
              <div
                key={o.id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "180px 160px 1fr 80px 90px 150px 160px",
                  borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                  alignItems: "center",
                  fontSize: 13,
                }}
              >
                {/* 学生摘要（姓名/学号/房号）— 老师端点填充，认得出「谁申请」再审批 */}
                <div style={{ padding: "10px 14px" }}>
                  {o.student_name ? (
                    <>
                      <div style={{ fontWeight: 600 }}>{o.student_name}</div>
                      {o.student_no && (
                        <div
                          style={{
                            fontSize: 11,
                            color: T.ink3,
                            fontFamily: T.mono,
                          }}
                        >
                          {o.student_no}
                          {o.room_no ? ` · ${o.room_no}` : ""}
                        </div>
                      )}
                    </>
                  ) : (
                    <span style={{ fontFamily: T.mono, fontSize: 11 }}>
                      {String(o.student_id).slice(0, 8)}…
                    </span>
                  )}
                </div>
                <div
                  style={{
                    padding: "10px 14px",
                    fontFamily: T.mono,
                    fontSize: 12,
                  }}
                >
                  {o.period_from} 〜 {o.period_to}
                </div>
                <div style={{ padding: "10px 14px" }}>{o.reason}</div>
                <div style={{ padding: "10px 14px", fontSize: 12 }}>
                  {o.contract_file_name ? (
                    <span style={{ color: T.ok, fontWeight: 600 }}>あり</span>
                  ) : (
                    <span style={{ color: T.ink3 }}>なし</span>
                  )}
                </div>
                <div style={{ padding: "10px 14px" }}>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 4,
                      background: T.warnSoft,
                      color: T.warn,
                      border: `1px solid ${T.warnBorder}`,
                    }}
                  >
                    審査待ち
                  </span>
                </div>
                <div
                  style={{
                    padding: "10px 14px",
                    fontFamily: T.mono,
                    fontSize: 11,
                    color: T.ink3,
                  }}
                >
                  {new Date(o.submitted_at).toLocaleString("ja-JP", {
                    timeZone: "Asia/Tokyo",
                  })}
                </div>
                <div style={{ padding: "10px 14px", display: "flex", gap: 6 }}>
                  <button
                    onClick={() => doDecideOnline(o.id, "approved")}
                    disabled={onlineActing[o.id]}
                    style={{
                      padding: "4px 12px",
                      background: T.ok,
                      color: "#fff",
                      border: "none",
                      borderRadius: 6,
                      fontFamily: "inherit",
                      fontSize: 11,
                      fontWeight: 700,
                      cursor: onlineActing[o.id] ? "not-allowed" : "pointer",
                    }}
                  >
                    承認
                  </button>
                  <button
                    onClick={() => doDecideOnline(o.id, "rejected")}
                    disabled={onlineActing[o.id]}
                    style={{
                      padding: "4px 12px",
                      background: T.surface,
                      color: T.danger,
                      border: `1px solid ${T.dangerBorder}`,
                      borderRadius: 6,
                      fontFamily: "inherit",
                      fontSize: 11,
                      fontWeight: 700,
                      cursor: onlineActing[o.id] ? "not-allowed" : "pointer",
                    }}
                  >
                    却下
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
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
  showDeadline = false, // web#20: 仅外泊 tab 显示期限徽章
}: {
  sub: string;
  setSub: (s: string) => void;
  onOpen: (app: OutstayUiApp) => void;
  apps: OutstayUiApp[];
  showDeadline?: boolean;
}) {
  const T = RYO;
  // Task #6 第 6 步 + Task #16: apps prop 是 array 就一定用（空数组也显示空状态）。
  const apps = Array.isArray(appsProp) ? appsProp : [];
  // 数据源是 pending-for-me（后端只返回「待当前役职决裁」的届：pending / approved_partial）。
  // 已审结的届（批准 / 却下 / 退回质问）结构上永远不会进这个列表 → 移除这三个恒空子标签，
  // 只留 pending（待审）+ all（全部）两个有意义的视图，不再给老师点开却永远空的死标签
  // （TW-044）。历史查询需另建带状态过滤的老师端端点，本列表不承担。
  const subs = ["pending", "all"];
  const subLabels: Record<string, string> = {
    pending: "審査待ち",
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
            "帰寮予定",
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
              {/* web#20: 非外泊不用外泊期限规则，列显示「—」防误标 */}
              {showDeadline ? (
                <DeadlineBadge depart={a.depart} submitted={a.submitted} />
              ) : (
                "—"
              )}
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
