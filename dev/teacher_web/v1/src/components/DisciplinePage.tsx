import React from "react";
import { RYO, S, dormLabel } from "../theme";
import type { RyoTokens } from "../theme";
import { api } from "../api/client";
import { IncidentsPage } from "./IncidentsPage";
import {
  ModalShell,
  ModalField,
  ModalFooter,
  StudentPicker,
  type PickerStudent,
} from "./shared";
import type {
  TeacherProfile,
  DisciplineRankingOut,
  DemeritEvent,
} from "../api/types";
import { canManage, C_DEMERIT } from "../api/permissions";

// 源 index.html 17197-17882（components/discipline.jsx 块）。
// 界面原样搬，仅 window.RYO→RYO / window.tomoshibiApi→api / window.dormLabel→dormLabel /
// window.ModalShell|ModalField|ModalFooter→从 ./shared import / 日语注释翻成中文。
// /discipline — 规则卡 + 排行 + 清扫/禁足名单 + 警告 + 自动提醒预览。

// 老师档案在本页会读取 teacher.dorm（"men"/"women" 字符串），
// 但严格的 TeacherProfile 只声明 assigned_dorm，故扩展出 dorm 字段供本页读取。
type DisciplineTeacher = TeacherProfile & { dorm: string };

// 排行表整形后的行数据（由后端 DisciplineRankingEntry 派生）
// late/absent 后端 ranking 未提供，不写入行（避免恒 0 误导）
interface RankRow {
  room: string;
  id: string;
  student_id: string;
  name: string;
  total: number;
  is_cleaning_threshold: boolean;
  is_curfew_threshold: boolean;
}

export function DisciplinePage({
  teacher,
  authToken,
}: {
  teacher: DisciplineTeacher;
  authToken: string;
}) {
  const T = RYO;
  const dorm = teacher.dorm;
  // 权限：C_DEMERIT 簇里「申請承認専用」组只有 VIEW，后端 routers/discipline.py 的
  // 手动设分/取消均 require_permission(C_DEMERIT, MANAGE)。无 MANAGE 时隐藏写入口，
  // 避免点了必被 403（与 AccountsPage/InfoPage 同款门控）。
  const canWrite = !!teacher && canManage(teacher, C_DEMERIT);

  // 本月键 YYYY-MM，锁 Asia/Tokyo（勿用浏览器本地 getMonth）
  const month = (() => {
    const parts = new Intl.DateTimeFormat("ja-JP", {
      timeZone: "Asia/Tokyo",
      year: "numeric",
      month: "2-digit",
    }).formatToParts(new Date());
    const y = parts.find((p) => p.type === "year")?.value ?? "1970";
    const m = parts.find((p) => p.type === "month")?.value ?? "01";
    return `${y}-${m}`;
  })();
  const [backendRanking, setBackendRanking] =
    React.useState<DisciplineRankingOut | null>(null);
  const [loadingBackend, setLoadingBackend] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  // 手动加扣分 modal 状态
  const [manualTarget, setManualTarget] = React.useState<{
    student_id: string;
    name: string;
    current: number;
  } | null>(null); // {student_id, name, current=当前本月合计点（预填用）}
  // 「任意の学生に手動加算」搜学生入口弹窗开关（2026-06-14，独立于排行榜行的旧入口）
  const [searchAddOpen, setSearchAddOpen] = React.useState(false);
  // 最近手动加扣分记录（用于即时撤销）
  const [lastEvent, setLastEvent] = React.useState<DemeritEvent | null>(null); // DemeritEventOut
  const [lastEventMsg, setLastEventMsg] = React.useState<string | null>(null);
  // 6-15:「事案記録」从独立菜单并入本页 → 页内标签页（"demerit"=「減点・処分」/ "incidents"=「事案記録」）
  const [tab, setTab] = React.useState<"demerit" | "incidents">("demerit");

  const loadRanking = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    setLoadingBackend(true);
    setFetchError(null);
    api
      .getDisciplineRanking(authToken, month)
      .then((r) => {
        if (cancelled) return;
        setBackendRanking(r);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[DisciplinePage] getDisciplineRanking 失败", e);
        setFetchError(e.message || "データ取得に失敗しました");
        setBackendRanking(null);
      })
      .finally(() => {
        if (!cancelled) setLoadingBackend(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken, month]);

  React.useEffect(() => {
    return loadRanking();
  }, [loadRanking]);

  // 手动设定本月合计点为绝对值（B 方案：后端算「目标 − 当前」差值记录）
  const handleManualSubmit = (
    studentId: string,
    name: string,
    targetPoints: number,
    reason: string,
    idempotencyKey?: string,
    expectedCurrentPoints?: number,
  ) => {
    // TW-032：return 把 promise 交回 modal —— modal 的 submitting 防双击守卫靠
    // Promise.resolve(onSubmit(...)).finally(setSubmitting(false))。原来本函数不 return、
    // 返回 undefined，finally 在下一个微任务就复位 submitting，按钮在网络返回前复活、可连点。
    // idempotencyKey：submitting 守卫只挡「响应回来前连点」；这个键补的是「响应丢失后老师
    // 手动重试」——同一次设定意图带同一 key，后端（A-473）识别重复不叠加第二条扣分。
    // expectedCurrentPoints：乐观锁，提交前再 GET 到的当前分，后端锁内比对防 TOCTOU。
    return api
      .createManualDemerit(
        {
          student_id: studentId,
          target_points: targetPoints,
          reason,
          idempotency_key: idempotencyKey,
          expected_current_points: expectedCurrentPoints,
        },
        authToken,
      )
      .then((ev) => {
        setLastEvent(ev);
        setLastEventMsg(
          `${name} の今月の合計点を ${targetPoints} 点に設定しました`,
        );
        setManualTarget(null);
        setSearchAddOpen(false);
        loadRanking();
      })
      .catch((e: { status?: number; code?: string; message?: string }) => {
        // 409 POINTS_CHANGED：分数在 GET→POST 空档变了，中止并让 modal 刷新当前分后重填
        if (e?.status === 409 && e?.code === "POINTS_CHANGED") {
          alert("点数が変わったので設定を中止しました");
          loadRanking();
          throw e;
        }
        alert("スコア設定に失敗しました：" + (e.message || JSON.stringify(e)));
      });
  };

  // 撤销最近一条手动扣分
  const handleRevoke = (ev: DemeritEvent) => {
    const reason = prompt("取り消し理由を入力してください（必須）");
    if (!reason || !reason.trim()) return;
    // TW-032：同 handleManualSubmit，return promise 让调用方的防双击守卫等真结果
    return api
      .revokeDemerit(ev.id, { revoke_reason: reason.trim() }, authToken)
      .then(() => {
        setLastEvent(null);
        setLastEventMsg(null);
        loadRanking();
      })
      .catch((e) => {
        alert("取り消しに失敗しました：" + (e.message || JSON.stringify(e)));
      });
  };

  // 数据整形
  let data: RankRow[] = [];
  if (backendRanking && backendRanking.entries) {
    data = backendRanking.entries.map((e) => ({
      room: e.room_no,
      id: e.student_no,
      student_id: e.student_id,
      name: e.name,
      total: e.total_points,
      is_cleaning_threshold: e.is_cleaning_threshold,
      is_curfew_threshold: e.is_curfew_threshold,
    }));
  }

  // 学生 → 本月合计点 的查表（供搜学生弹窗预填/展示当前分）。
  // ranking 已按同一「demo 隔离 + 寮过滤」口径拉全员（即使 0 点也列出），
  // 而搜学生接口 query_students_for_picker 用完全相同的过滤，故搜到的学生必在此表内。
  const pointsByStudent = React.useMemo(() => {
    const m: Record<string, number> = {};
    if (backendRanking?.entries) {
      for (const e of backendRanking.entries) m[e.student_id] = e.total_points;
    }
    return m;
  }, [backendRanking]);

  const banList = data.filter((d) => d.is_curfew_threshold);
  // ≥4 分罚扫名单；≥8 分只进禁足名单、不重复标罚扫（已 approve 设计第 6 条）
  const cleaningList = data.filter(
    (d) => d.is_cleaning_threshold && !d.is_curfew_threshold,
  );
  const warnList = data.filter((d) => d.total >= 3 && !d.is_cleaning_threshold);

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
        減点・処分
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 6px",
          letterSpacing: -0.3,
        }}
      >
        減点・処分
      </h1>

      {/* 页内标签页：「減点・処分」（本页原内容）/「事案記録」（原独立菜单，6-15 并入）*/}
      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          margin: "14px 0 0",
        }}
      >
        {(
          [
            ["demerit", "減点・処分"],
            ["incidents", "事案記録"],
          ] as Array<["demerit" | "incidents", string]>
        ).map(([k, l]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            style={{
              padding: "10px 18px",
              background: "transparent",
              border: "none",
              borderBottom:
                tab === k ? `2px solid ${T.cobalt}` : "2px solid transparent",
              color: tab === k ? T.cobaltDeep : T.ink3,
              fontWeight: tab === k ? 700 : 500,
              fontFamily: "inherit",
              fontSize: 13,
              cursor: "pointer",
              marginBottom: -1,
            }}
          >
            {l}
          </button>
        ))}
      </div>

      {tab === "incidents" ? (
        <div style={{ marginTop: 20 }}>
          <IncidentsPage teacher={teacher} authToken={authToken} embedded />
        </div>
      ) : (
        <>
          <div style={{ color: T.ink2, fontSize: 13, margin: "18px 0 22px" }}>
            {dormLabel(dorm)} · {month.replace("-", " 年 ")} 月
          </div>

          {/* 错误横幅 */}
          {fetchError && (
            <div
              style={{
                padding: "10px 16px",
                background: T.dangerSoft,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 10,
                color: T.danger,
                fontSize: 13,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <span style={{ flex: 1 }}>{fetchError}</span>
              <button
                onClick={loadRanking}
                className="t-btn"
                style={{
                  ...S.btnGhost,
                  padding: "4px 12px",
                  fontSize: 12,
                  color: T.danger,
                  border: `1px solid ${T.dangerBorder}`,
                  borderRadius: 8,
                }}
              >
                再試行
              </button>
            </div>
          )}

          {/* 手动加分后 即时撤销 横幅 */}
          {lastEventMsg && lastEvent && (
            <div
              style={{
                padding: "10px 16px",
                background: T.okSoft,
                border: `1px solid ${T.okBorder}`,
                borderRadius: 10,
                color: T.ok,
                fontSize: 13,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <span style={{ flex: 1 }}>{lastEventMsg}</span>
              {canWrite && (
                <button
                  onClick={() => handleRevoke(lastEvent)}
                  className="t-btn"
                  style={{
                    ...S.btnGhost,
                    padding: "4px 12px",
                    fontSize: 12,
                    color: T.danger,
                    border: `1px solid ${T.dangerBorder}`,
                    borderRadius: 8,
                  }}
                >
                  取り消し
                </button>
              )}
              <button
                onClick={() => {
                  setLastEvent(null);
                  setLastEventMsg(null);
                }}
                style={{
                  background: "transparent",
                  border: "none",
                  fontSize: 16,
                  color: T.ink3,
                  cursor: "pointer",
                }}
              >
                ×
              </button>
            </div>
          )}

          {/* 规则卡 */}
          <div
            style={{
              ...S.card,
              padding: "18px 22px",
              marginBottom: 20,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                marginBottom: 12,
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 700 }}>
                現在の減点ルール（運用開始前のため、先生方と調整可能です）
              </div>
              <div style={{ flex: 1 }} />
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <RulePill label="遅刻" value="0.5 点" color={T.late} />
              <RulePill label="欠席" value="1.0 点" color={T.danger} />
              <RulePill
                label="罰則清掃の適用"
                value="月累計 ≥ 4 点"
                color={T.warn}
              />
              <RulePill
                label="外出禁止の適用"
                value="月累計 ≥ 8 点"
                color={T.danger}
              />
            </div>
          </div>

          {canWrite && (
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                marginBottom: 12,
              }}
            >
              <button
                onClick={() => setSearchAddOpen(true)}
                className="t-btn"
                style={{
                  ...S.btnPrimary,
                  padding: "9px 16px",
                }}
              >
                ＋ 任意の寮生に手動加算
              </button>
            </div>
          )}
          <SectionH n="1" title="今月全員ランキング" />
          {loadingBackend ? (
            <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
              読み込み中…
            </div>
          ) : fetchError && !backendRanking ? (
            // web#22: 拉取失败 ≠ 空数据 — 明确失败文案（上方已有错误横幅 +「再試行」）
            <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
              取得に失敗しました
            </div>
          ) : (
            <div
              style={{
                ...S.card,
                overflow: "hidden",
                marginBottom: 24,
              }}
            >
              {/* 表格页保守：表头 padding「10px 12px」比 S.tableHead 小，只换颜色 */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "50px 1fr 90px 90px 120px 120px 130px",
                  background: T.surfaceAlt,
                  fontSize: 11,
                  color: T.ink3,
                  fontWeight: 600,
                  letterSpacing: 1,
                  borderBottom: `1px solid ${T.line}`,
                }}
              >
                {[
                  "順位",
                  "寮生",
                  "部屋",
                  "減点合計",
                  "清掃まで残り",
                  "外出禁止まで残り",
                  "操作",
                ].map((h) => (
                  <div key={h} style={{ padding: "10px 12px" }}>
                    {h}
                  </div>
                ))}
              </div>
              {data.length === 0 && (
                <div
                  style={{
                    padding: "16px 16px",
                    color: T.ink3,
                    fontSize: 13,
                  }}
                >
                  まだデータがありません
                </div>
              )}
              {data.map((d, i) => (
                <div
                  key={d.id}
                  className="t-row"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "50px 1fr 90px 90px 120px 120px 130px",
                    borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                    fontSize: 12.5,
                    alignItems: "center",
                  }}
                >
                  <div
                    style={{
                      padding: "9px 12px",
                      fontFamily: T.mono,
                      color: i < 3 ? T.danger : T.ink3,
                      fontWeight: 700,
                    }}
                  >
                    #{i + 1}
                  </div>
                  <div style={{ padding: "9px 12px", fontWeight: 600 }}>
                    {d.name}
                  </div>
                  <div
                    style={{
                      padding: "9px 12px",
                      fontFamily: T.mono,
                      color: T.ink3,
                    }}
                  >
                    {d.room}
                  </div>
                  <div
                    style={{
                      padding: "9px 12px",
                      fontFamily: T.mono,
                      fontWeight: 700,
                      color:
                        d.total >= 4 ? T.danger : d.total >= 3 ? T.warn : T.ink,
                    }}
                  >
                    {d.total.toFixed(1)}
                  </div>
                  <div
                    style={{
                      padding: "9px 12px",
                      fontFamily: T.mono,
                      color: T.ink3,
                    }}
                  >
                    {Math.max(0, 4 - d.total).toFixed(1)} 点
                  </div>
                  <div
                    style={{
                      padding: "9px 12px",
                      fontFamily: T.mono,
                      color: T.ink3,
                    }}
                  >
                    {Math.max(0, 8 - d.total).toFixed(1)} 点
                  </div>
                  <div style={{ padding: "6px 12px" }}>
                    {canWrite && (
                      <button
                        onClick={() =>
                          setManualTarget({
                            student_id: d.student_id,
                            name: d.name,
                            current: d.total,
                          })
                        }
                        className="t-btn"
                        style={{
                          ...S.btnSmall,
                          padding: "4px 10px",
                          fontSize: 11,
                          background: "transparent",
                          color: T.cobalt,
                          border: `1px solid ${T.cobalt}`,
                        }}
                      >
                        手動加算
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <SectionH
            n="2"
            title="罰則清掃リスト（来月対象）"
            note={`${cleaningList.length} 名`}
          />
          <StudentCardRow
            list={cleaningList}
            color={T.warn}
            label="今月減点"
            empty="該当なし"
          />

          <SectionH
            n="3"
            title="外出禁止リスト（来月対象）"
            note={`${banList.length} 名`}
          />
          <StudentCardRow
            list={banList}
            color={T.danger}
            label="今月減点"
            empty="該当なし"
          />

          <SectionH
            n="4"
            title="警告リスト（基準値に接近）"
            note={`${warnList.length} 名`}
          />
          <StudentCardRow
            list={warnList}
            color={T.warn}
            label="今月減点"
            empty="該当なし"
          />

          {/* 自动提醒预览 */}
          <div
            style={{
              marginTop: 30,
              background: T.surface,
              border: `1px dashed ${T.lineStrong}`,
              borderRadius: 16,
              padding: "18px 20px",
              opacity: 0.85,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                marginBottom: 8,
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 700, color: T.ink3 }}>
                自動アラート
              </div>
              <span
                style={{
                  ...S.pill,
                  fontSize: 10,
                  fontWeight: 700,
                  color: T.warn,
                  background: T.warnSoft,
                  padding: "2px 8px",
                  letterSpacing: 1,
                }}
              >
                稼働中
              </span>
            </div>
            <div
              style={{
                fontSize: 12,
                color: T.ink3,
                lineHeight: 1.7,
              }}
            >
              寮生の今月の累計減点が清掃ライン（4点）または外出禁止ライン（8点）に達すると、その寮生が所属する寮の担当教員へ自動的に通知（通知センター）が送られます。各ラインにつき月1回まで。
            </div>
          </div>

          {/* 手动加分 modal —— 从排行榜行点「手動加算」进入（旧方式，保留）*/}
          {manualTarget && (
            <ManualDemeritModal
              T={T}
              target={manualTarget}
              authToken={authToken}
              month={month}
              onClose={() => setManualTarget(null)}
              onSubmit={(sid, pts, rsn, key, expected) =>
                handleManualSubmit(
                  sid,
                  manualTarget.name,
                  pts,
                  rsn,
                  key,
                  expected,
                )
              }
            />
          )}
          {/* 搜任意学生加分 modal —— 2026-06-14 新入口（不必先上排行榜）*/}
          {searchAddOpen && (
            <ManualDemeritSearchModal
              T={T}
              authToken={authToken}
              month={month}
              pointsByStudent={pointsByStudent}
              onClose={() => setSearchAddOpen(false)}
              onSubmit={handleManualSubmit}
            />
          )}
        </>
      )}
    </div>
  );
}

// 手动加分输入框样式 — 套 S.input，保留原 padding / 边框强度
function modalInputStyle(T: RyoTokens): React.CSSProperties {
  return {
    ...S.input,
    width: "100%",
    padding: "9px 12px",
    border: `1px solid ${T.lineStrong}`,
    boxSizing: "border-box",
  };
}

// 从排行榜接口取单个学生的当月合计点（无单学生接口，只能整表拉再取）
async function fetchStudentMonthPoints(
  authToken: string,
  month: string,
  studentId: string,
): Promise<number> {
  const r = await api.getDisciplineRanking(authToken, month);
  const entry = r.entries.find((e) => e.student_id === studentId);
  if (!entry) {
    throw new Error("この寮生の点数が見つかりませんでした");
  }
  return entry.total_points;
}

// 弹窗内：分数刚变过的提示条
function ScoreChangedBanner({
  T,
  from,
  to,
}: {
  T: RyoTokens;
  from: number;
  to: number;
}) {
  return (
    <div
      style={{
        padding: "8px 12px",
        background: T.warnSoft,
        border: `1px solid ${T.warn}`,
        borderRadius: 10,
        color: T.warn,
        fontSize: 12,
        lineHeight: 1.5,
        marginBottom: 12,
      }}
    >
      注意：ページ表示時点から点数が変わりました（{from} → {to}{" "}
      点）。自動減点などが反映されています。
    </div>
  );
}

// 手动设定合计点 modal（本块私有子组件，B 方案：设绝对值、后端算差值）
// 打开瞬间重拉当前分预填 —— 禁止用页面挂载时的排行榜快照（会静默抹掉期间的自动扣分）
function ManualDemeritModal({
  T,
  target,
  authToken,
  month,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  target: { student_id: string; name: string; current: number };
  authToken: string;
  month: string;
  onClose: () => void;
  onSubmit: (
    studentId: string,
    targetPoints: number,
    reason: string,
    idempotencyKey: string,
    expectedCurrentPoints: number,
  ) => void | Promise<unknown>;
}) {
  // score 初始空：加载完成前不给旧快照，避免老师对着过期数字操作
  const [score, setScore] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [fetchState, setFetchState] = React.useState<
    "loading" | "ready" | "error"
  >("loading");
  const [freshCurrent, setFreshCurrent] = React.useState<number | null>(null);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  // 打开时拉到的「現在点」——提交前再比对，挡住填表期间又变了的情况
  const openedCurrentRef = React.useRef<number | null>(null);
  // 请求世代号：重试 / 卸载时丢弃过期响应，防竞态把旧结果写回
  const fetchGenRef = React.useRef(0);
  // A-473 幂等键：本弹窗一次「設定」意图固定一个 key，失败重试复用同一 key，成功即随弹窗关闭
  // 弃用；重开弹窗 = 新意图 = 新 key。
  const idemKey = React.useRef(crypto.randomUUID()).current;

  const reloadCurrent = React.useCallback(() => {
    const gen = ++fetchGenRef.current;
    setFetchState("loading");
    setFetchError(null);
    setScore("");
    setFreshCurrent(null);
    openedCurrentRef.current = null;
    fetchStudentMonthPoints(authToken, month, target.student_id)
      .then((pts) => {
        if (gen !== fetchGenRef.current) return;
        setFreshCurrent(pts);
        openedCurrentRef.current = pts;
        setScore(String(pts));
        setFetchState("ready");
      })
      .catch((e: { message?: string }) => {
        if (gen !== fetchGenRef.current) return;
        // 不许静默 fallback 回旧快照
        setFetchError(e?.message || "現在の点数の取得に失敗しました");
        setFetchState("error");
      });
  }, [authToken, month, target.student_id]);

  React.useEffect(() => {
    reloadCurrent();
    return () => {
      fetchGenRef.current += 1; // 卸载：作废进行中的响应
    };
  }, [reloadCurrent]);

  const parsed = parseFloat(score);
  const disabled =
    fetchState !== "ready" ||
    freshCurrent === null ||
    !reason.trim() ||
    score === "" ||
    isNaN(parsed) ||
    parsed < 0 ||
    submitting;

  const handleSubmit = () => {
    if (disabled || freshCurrent === null) return;
    setSubmitting(true);
    // 保险：提交前再拉一次；打开后填表期间又变了 → 必须老师确认
    fetchStudentMonthPoints(authToken, month, target.student_id)
      .then((latest) => {
        const opened = openedCurrentRef.current;
        if (opened !== null && latest !== opened) {
          const ok = window.confirm(
            `設定画面を開いてから点数が変わりました（${opened} → ${latest} 点）。\nこのまま ${parsed} 点に設定しますか？`,
          );
          if (!ok) {
            setFreshCurrent(latest);
            openedCurrentRef.current = latest;
            return;
          }
          setFreshCurrent(latest);
          openedCurrentRef.current = latest;
        }
        // latest 一并传给后端做乐观锁，堵住 GET→POST 空档
        return Promise.resolve(
          onSubmit(target.student_id, parsed, reason.trim(), idemKey, latest),
        ).catch((e: { status?: number; code?: string }) => {
          // 父层已弹「中止」提示；这里刷新当前分，让老师重新填
          if (e?.status === 409 && e?.code === "POINTS_CHANGED") {
            return fetchStudentMonthPoints(
              authToken,
              month,
              target.student_id,
            ).then((pts) => {
              setFreshCurrent(pts);
              openedCurrentRef.current = pts;
              setScore(String(pts));
            });
          }
        });
      })
      .catch((e) => {
        alert(
          "最新の点数の確認に失敗しました。設定を中止しました：" +
            (e?.message || JSON.stringify(e)),
        );
      })
      .finally(() => setSubmitting(false));
  };

  const scoreLabel =
    fetchState === "loading"
      ? "今月の合計点（現在の点数を取得中…）"
      : fetchState === "error"
        ? "今月の合計点（現在の点数を取得できません）"
        : `今月の合計点（現在 ${freshCurrent} 点・絶対値で上書き）`;

  const snapshotChanged =
    fetchState === "ready" &&
    freshCurrent !== null &&
    freshCurrent !== target.current;

  return (
    <ModalShell T={T} title={`合計点を設定：${target.name}`} onClose={onClose}>
      {fetchState === "loading" && (
        <div
          style={{
            padding: "8px 0 12px",
            color: T.ink3,
            fontSize: 13,
          }}
        >
          現在の点数を取得中…
        </div>
      )}
      {fetchState === "error" && (
        <div
          style={{
            padding: "10px 12px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
            color: T.danger,
            fontSize: 12,
            lineHeight: 1.5,
            marginBottom: 12,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span style={{ flex: 1 }}>
            現在の点数の取得に失敗しました
            {fetchError ? `：${fetchError}` : ""}
            。古い点数での設定はできません。
          </span>
          <button
            type="button"
            onClick={() => reloadCurrent()}
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "4px 12px",
              fontSize: 12,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
              whiteSpace: "nowrap",
            }}
          >
            再試行
          </button>
        </div>
      )}
      {snapshotChanged && freshCurrent !== null && (
        <ScoreChangedBanner T={T} from={target.current} to={freshCurrent} />
      )}
      <ModalField T={T} label={scoreLabel}>
        <input
          type="number"
          min="0"
          step="0.5"
          value={score}
          disabled={fetchState !== "ready"}
          onChange={(e) => setScore(e.target.value)}
          className="t-input"
          style={{
            ...modalInputStyle(T),
            opacity: fetchState === "ready" ? 1 : 0.6,
          }}
        />
      </ModalField>
      <ModalField T={T} label="理由（必須）">
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="例：消灯後廊下で騒いでいた"
          disabled={fetchState !== "ready"}
          className="t-input"
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={handleSubmit}
        disabled={disabled}
        submitLabel="設定"
      />
    </ModalShell>
  );
}

// 搜学生设定合计点 modal（2026-06-14 新入口）—— StudentPicker(single) + 合计点 + 理由 一弹窗搞定。
// 用 searchDemeritStudents（C_DEMERIT 权限）而非 front-desk 的搜学生接口（权限簇不同）。
// 选中学生时重拉当前分 —— 与 ManualDemeritModal 同根因，禁止用页面挂载时的 pointsByStudent 快照。
function ManualDemeritSearchModal({
  T,
  authToken,
  month,
  pointsByStudent,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  authToken: string;
  month: string;
  pointsByStudent: Record<string, number>;
  onClose: () => void;
  onSubmit: (
    studentId: string,
    name: string,
    targetPoints: number,
    reason: string,
    idempotencyKey: string,
    expectedCurrentPoints: number,
  ) => void | Promise<unknown>;
}) {
  const [selected, setSelected] = React.useState<PickerStudent[]>([]);
  const [score, setScore] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [fetchState, setFetchState] = React.useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [freshCurrent, setFreshCurrent] = React.useState<number | null>(null);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const openedCurrentRef = React.useRef<number | null>(null);
  const fetchGenRef = React.useRef(0);
  // A-473 幂等键：失败重试复用同一 key（后端按「学生 + key」去重，中途改选别的学生也安全）；
  // 成功即随弹窗关闭弃用。
  const idemKey = React.useRef(crypto.randomUUID()).current;
  const student = selected[0] || null;
  // 页面挂载时的快照（仅用于「刚变过」提示，绝不作预填/提交依据）
  const snapshotPoints =
    student && pointsByStudent[student.id] !== undefined
      ? pointsByStudent[student.id]
      : null;
  // 老师手输过分数后，换学生才恢复自动预填；同学生重拉成功时仍覆盖（重拉 = 新真值）
  const scoreTouchedRef = React.useRef(false);

  React.useEffect(() => {
    if (!student) {
      fetchGenRef.current += 1;
      setFetchState("idle");
      setFreshCurrent(null);
      openedCurrentRef.current = null;
      setFetchError(null);
      setScore("");
      return;
    }
    const gen = ++fetchGenRef.current;
    setFetchState("loading");
    setFetchError(null);
    setFreshCurrent(null);
    openedCurrentRef.current = null;
    if (!scoreTouchedRef.current) setScore("");
    fetchStudentMonthPoints(authToken, month, student.id)
      .then((pts) => {
        if (gen !== fetchGenRef.current) return;
        setFreshCurrent(pts);
        openedCurrentRef.current = pts;
        if (!scoreTouchedRef.current) setScore(String(pts));
        setFetchState("ready");
      })
      .catch((e: { message?: string }) => {
        if (gen !== fetchGenRef.current) return;
        setFetchError(e?.message || "現在の点数の取得に失敗しました");
        setFetchState("error");
        if (!scoreTouchedRef.current) setScore("");
      });
    return () => {
      fetchGenRef.current += 1;
    };
  }, [student, authToken, month]);

  const retryFetch = () => {
    if (!student) return;
    const gen = ++fetchGenRef.current;
    scoreTouchedRef.current = false;
    setFetchState("loading");
    setFetchError(null);
    setScore("");
    setFreshCurrent(null);
    openedCurrentRef.current = null;
    fetchStudentMonthPoints(authToken, month, student.id)
      .then((pts) => {
        if (gen !== fetchGenRef.current) return;
        setFreshCurrent(pts);
        openedCurrentRef.current = pts;
        setScore(String(pts));
        setFetchState("ready");
      })
      .catch((e: { message?: string }) => {
        if (gen !== fetchGenRef.current) return;
        setFetchError(e?.message || "現在の点数の取得に失敗しました");
        setFetchState("error");
      });
  };

  const parsed = parseFloat(score);
  const disabled =
    !student ||
    fetchState !== "ready" ||
    freshCurrent === null ||
    !reason.trim() ||
    score === "" ||
    isNaN(parsed) ||
    parsed < 0 ||
    submitting;

  const handleSubmit = () => {
    if (disabled || !student || freshCurrent === null) return;
    setSubmitting(true);
    const submittingStudentId = student.id;
    const submittingStudentName = student.name;
    fetchStudentMonthPoints(authToken, month, submittingStudentId)
      .then((latest) => {
        const opened = openedCurrentRef.current;
        if (opened !== null && latest !== opened) {
          const ok = window.confirm(
            `設定画面を開いてから点数が変わりました（${opened} → ${latest} 点）。\nこのまま ${parsed} 点に設定しますか？`,
          );
          if (!ok) {
            setFreshCurrent(latest);
            openedCurrentRef.current = latest;
            return;
          }
          setFreshCurrent(latest);
          openedCurrentRef.current = latest;
        }
        // latest 一并传给后端做乐观锁；学生 id/name 用点击瞬间快照，防飞行中换人选
        return Promise.resolve(
          onSubmit(
            submittingStudentId,
            submittingStudentName,
            parsed,
            reason.trim(),
            idemKey,
            latest,
          ),
        ).catch((e: { status?: number; code?: string }) => {
          if (e?.status === 409 && e?.code === "POINTS_CHANGED") {
            return fetchStudentMonthPoints(
              authToken,
              month,
              submittingStudentId,
            ).then((pts) => {
              setFreshCurrent(pts);
              openedCurrentRef.current = pts;
              setScore(String(pts));
            });
          }
        });
      })
      .catch((e) => {
        alert(
          "最新の点数の確認に失敗しました。設定を中止しました：" +
            (e?.message || JSON.stringify(e)),
        );
      })
      .finally(() => setSubmitting(false));
  };

  const scoreLabel = !student
    ? "今月の合計点（絶対値で設定・差分は自動記録）"
    : fetchState === "loading"
      ? "今月の合計点（現在の点数を取得中…）"
      : fetchState === "error"
        ? "今月の合計点（現在の点数を取得できません）"
        : fetchState === "ready" && freshCurrent !== null
          ? `今月の合計点（現在 ${freshCurrent} 点・絶対値で上書き）`
          : "今月の合計点（現在の点数を取得できません）";

  const snapshotChanged =
    student &&
    fetchState === "ready" &&
    freshCurrent !== null &&
    snapshotPoints !== null &&
    freshCurrent !== snapshotPoints;

  return (
    <ModalShell T={T} title="任意の寮生の合計点を設定" onClose={onClose}>
      <ModalField T={T} label="寮生（必須）">
        {/* submitting 期间禁止换学生：组件本身无禁用态，用 pointer-events + onChange 早退 */}
        <div
          style={{
            pointerEvents: submitting ? "none" : "auto",
            opacity: submitting ? 0.6 : 1,
          }}
        >
          <StudentPicker
            mode="single"
            autoOpen
            searchApi={(q, token) => api.searchDemeritStudents(q, token)}
            selected={selected}
            onChange={(sel) => {
              if (submitting) return;
              scoreTouchedRef.current = false;
              setSelected(sel);
            }}
            authToken={authToken}
            placeholder="氏名 / 学籍番号で検索（クリックで一覧）"
          />
        </div>
      </ModalField>
      {student && fetchState === "loading" && (
        <div
          style={{
            padding: "4px 0 12px",
            color: T.ink3,
            fontSize: 13,
          }}
        >
          現在の点数を取得中…
        </div>
      )}
      {student && fetchState === "error" && (
        <div
          style={{
            padding: "10px 12px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
            color: T.danger,
            fontSize: 12,
            lineHeight: 1.5,
            marginBottom: 12,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span style={{ flex: 1 }}>
            現在の点数の取得に失敗しました
            {fetchError ? `：${fetchError}` : ""}
            。古い点数での設定はできません。
          </span>
          <button
            type="button"
            onClick={retryFetch}
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "4px 12px",
              fontSize: 12,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
              whiteSpace: "nowrap",
            }}
          >
            再試行
          </button>
        </div>
      )}
      {snapshotChanged && freshCurrent !== null && snapshotPoints !== null && (
        <ScoreChangedBanner T={T} from={snapshotPoints} to={freshCurrent} />
      )}
      <ModalField T={T} label={scoreLabel}>
        <input
          type="number"
          min="0"
          step="0.5"
          value={score}
          disabled={!student || fetchState !== "ready"}
          onChange={(e) => {
            scoreTouchedRef.current = true;
            setScore(e.target.value);
          }}
          className="t-input"
          style={{
            ...modalInputStyle(T),
            opacity: student && fetchState === "ready" ? 1 : 0.6,
          }}
        />
      </ModalField>
      <ModalField T={T} label="理由（必須）">
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="例：消灯後廊下で騒いでいた"
          disabled={!student || fetchState !== "ready"}
          className="t-input"
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={handleSubmit}
        disabled={disabled}
        submitLabel="設定"
      />
    </ModalShell>
  );
}

// 规则徽章（本块私有子组件）
function RulePill({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  const T = RYO;
  return (
    <div
      style={{
        ...S.pill,
        background: T.surfaceAlt,
        border: `1px solid ${T.line}`,
        padding: "6px 14px",
        gap: 8,
        fontSize: 12,
        fontWeight: 400,
      }}
    >
      <span style={{ color: T.ink3 }}>{label}</span>
      <span style={{ fontFamily: RYO.mono, fontWeight: 700, color }}>
        {value}
      </span>
    </div>
  );
}

// 区段标题（本块私有子组件）
function SectionH({
  n,
  title,
  note,
}: {
  n: string;
  title: string;
  note?: string;
}) {
  const T = RYO;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        gap: 10,
        margin: "6px 0 10px",
      }}
    >
      <span
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: T.ink3,
          letterSpacing: 1,
          fontFamily: T.mono,
        }}
      >
        §{n}
      </span>
      <span style={{ fontSize: 15, fontWeight: 700 }}>{title}</span>
      {note && <span style={{ fontSize: 11, color: T.ink3 }}>{note}</span>}
    </div>
  );
}

// 学生卡片行（本块私有子组件）
function StudentCardRow({
  list,
  color,
  label,
  empty,
}: {
  list: RankRow[];
  color: string;
  label: string;
  empty: string;
}) {
  const T = RYO;
  if (!list.length)
    return (
      <div
        style={{
          ...S.card,
          padding: "14px 16px",
          fontSize: 12,
          color: T.ink3,
          marginBottom: 18,
        }}
      >
        {empty}
      </div>
    );
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 10,
        marginBottom: 18,
      }}
    >
      {list.map((d, i) => (
        <div
          key={d.id}
          className="t-fade-up"
          style={{
            ...S.card,
            padding: "12px 14px",
            ...(i < 12 ? { animationDelay: `${i * 40}ms` } : null),
          }}
        >
          <div style={{ fontSize: 15, fontWeight: 700 }}>{d.name}</div>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              fontFamily: T.mono,
              marginTop: 2,
            }}
          >
            {d.room} · {d.id}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 4,
              marginTop: 8,
            }}
          >
            <span style={{ fontSize: 10, color: T.ink3 }}>{label}</span>
            <span
              style={{
                fontSize: 18,
                fontWeight: 700,
                fontFamily: T.mono,
                color,
              }}
            >
              {d.total.toFixed(1)}
            </span>
            <span style={{ fontSize: 10, color: T.ink3 }}>点</span>
          </div>
          {/* 迟到/缺席内訳后端 ranking 未提供（恒为 0、会误导），故不显示；合计点已由上方 total 展示（C28）。 */}
        </div>
      ))}
    </div>
  );
}
