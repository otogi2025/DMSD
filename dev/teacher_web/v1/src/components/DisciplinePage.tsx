import React from "react";
import { RYO, dormLabel } from "../theme";
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
  ) => {
    // TW-032：return 把 promise 交回 modal —— modal 的 submitting 防双击守卫靠
    // Promise.resolve(onSubmit(...)).finally(setSubmitting(false))。原来本函数不 return、
    // 返回 undefined，finally 在下一个微任务就复位 submitting，按钮在网络返回前复活、可连点。
    return api
      .createManualDemerit(
        { student_id: studentId, target_points: targetPoints, reason },
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
      .catch((e) => {
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
          <IncidentsPage authToken={authToken} embedded />
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
                background: "#fff0f0",
                border: "1px solid #f5c6cb",
                borderRadius: 8,
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
                style={{
                  padding: "4px 12px",
                  background: "transparent",
                  color: T.danger,
                  border: "1px solid #f5c6cb",
                  borderRadius: 6,
                  fontFamily: "inherit",
                  fontSize: 12,
                  cursor: "pointer",
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
                background: "#f0fff4",
                border: "1px solid #b7ebc8",
                borderRadius: 8,
                color: T.ok,
                fontSize: 13,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <span style={{ flex: 1 }}>{lastEventMsg}</span>
              <button
                onClick={() => handleRevoke(lastEvent)}
                style={{
                  padding: "4px 12px",
                  background: "transparent",
                  color: T.danger,
                  border: `1px solid ${T.dangerBorder}`,
                  borderRadius: 6,
                  fontFamily: "inherit",
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                取り消し
              </button>
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
              background: T.surface,
              border: `1px solid ${T.line}`,
              borderRadius: 12,
              padding: "18px 22px",
              boxShadow: T.shadow1,
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
                label="清掃罰則の適用"
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

          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginBottom: 12,
            }}
          >
            <button
              onClick={() => setSearchAddOpen(true)}
              style={{
                padding: "9px 16px",
                background: T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              ＋ 任意の学生に手動加算
            </button>
          </div>
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
                background: T.surface,
                border: `1px solid ${T.line}`,
                borderRadius: 12,
                overflow: "hidden",
                boxShadow: T.shadow1,
                marginBottom: 24,
              }}
            >
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "50px 1fr 90px 90px 120px 120px 130px",
                  background: T.surfaceAlt,
                  fontSize: 11,
                  color: T.ink2,
                  fontWeight: 600,
                  letterSpacing: 1,
                  borderBottom: `1px solid ${T.line}`,
                }}
              >
                {[
                  "順位",
                  "学生",
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
                    <button
                      onClick={() =>
                        setManualTarget({
                          student_id: d.student_id,
                          name: d.name,
                          current: d.total,
                        })
                      }
                      style={{
                        padding: "4px 10px",
                        background: "transparent",
                        color: T.cobalt,
                        border: `1px solid ${T.cobalt}`,
                        borderRadius: 5,
                        fontFamily: "inherit",
                        fontSize: 11,
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      手動加算
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <SectionH
            n="2"
            title="清掃罰則リスト（来月対象）"
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
              borderRadius: 12,
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
                  fontSize: 10,
                  fontWeight: 700,
                  color: T.warn,
                  background: T.warnSoft,
                  padding: "2px 8px",
                  borderRadius: 4,
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
              学生の今月の累計減点が清掃ライン（4点）または外出禁止ライン（8点）に達すると、その学生が所属する寮の担当教員へ自動的に通知（通知センター）が送られます。各ラインにつき月1回まで。
            </div>
          </div>

          {/* 手动加分 modal —— 从排行榜行点「手動加算」进入（旧方式，保留）*/}
          {manualTarget && (
            <ManualDemeritModal
              T={T}
              target={manualTarget}
              onClose={() => setManualTarget(null)}
              onSubmit={(sid, pts, rsn) =>
                handleManualSubmit(sid, manualTarget.name, pts, rsn)
              }
            />
          )}
          {/* 搜任意学生加分 modal —— 2026-06-14 新入口（不必先上排行榜）*/}
          {searchAddOpen && (
            <ManualDemeritSearchModal
              T={T}
              authToken={authToken}
              onClose={() => setSearchAddOpen(false)}
              onSubmit={handleManualSubmit}
            />
          )}
        </>
      )}
    </div>
  );
}

// 手动加分输入框样式（源 front-desk 块 inputStyle / window.modalInputStyle 的本地副本）
function modalInputStyle(T: RyoTokens): React.CSSProperties {
  return {
    width: "100%",
    padding: "9px 12px",
    border: `1px solid ${T.lineStrong}`,
    borderRadius: 8,
    fontSize: 13,
    fontFamily: "inherit",
    boxSizing: "border-box",
    background: T.surface,
    color: T.ink,
  };
}

// 手动设定合计点 modal（本块私有子组件，B 方案：设绝对值、后端算差值）
function ManualDemeritModal({
  T,
  target,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  target: { student_id: string; name: string; current: number };
  onClose: () => void;
  onSubmit: (studentId: string, targetPoints: number, reason: string) => void;
}) {
  const [score, setScore] = React.useState(String(target.current));
  const [reason, setReason] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const parsed = parseFloat(score);
  const disabled =
    !reason.trim() || score === "" || isNaN(parsed) || parsed < 0 || submitting;
  const handleSubmit = () => {
    if (disabled) return;
    setSubmitting(true);
    Promise.resolve(onSubmit(target.student_id, parsed, reason.trim())).finally(
      () => setSubmitting(false),
    );
  };
  return (
    <ModalShell T={T} title={`合計点を設定：${target.name}`} onClose={onClose}>
      <ModalField
        T={T}
        label={`今月の合計点（現在 ${target.current} 点・絶対値で上書き）`}
      >
        <input
          type="number"
          min="0"
          step="0.5"
          value={score}
          onChange={(e) => setScore(e.target.value)}
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="理由（必須）">
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="例：消灯後廊下で騒いでいた"
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
function ManualDemeritSearchModal({
  T,
  authToken,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  authToken: string;
  onClose: () => void;
  onSubmit: (
    studentId: string,
    name: string,
    targetPoints: number,
    reason: string,
  ) => void;
}) {
  const [selected, setSelected] = React.useState<PickerStudent[]>([]);
  const [score, setScore] = React.useState("0");
  const [reason, setReason] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const student = selected[0] || null;
  const parsed = parseFloat(score);
  const disabled =
    !student ||
    !reason.trim() ||
    score === "" ||
    isNaN(parsed) ||
    parsed < 0 ||
    submitting;
  const handleSubmit = () => {
    if (disabled || !student) return;
    setSubmitting(true);
    Promise.resolve(
      onSubmit(student.id, student.name, parsed, reason.trim()),
    ).finally(() => setSubmitting(false));
  };
  return (
    <ModalShell T={T} title="任意の学生の合計点を設定" onClose={onClose}>
      <ModalField T={T} label="学生（必須）">
        <StudentPicker
          mode="single"
          autoOpen
          searchApi={(q, token) => api.searchDemeritStudents(q, token)}
          selected={selected}
          onChange={setSelected}
          authToken={authToken}
          placeholder="氏名 / 学籍番号で検索（クリックで一覧）"
        />
      </ModalField>
      <ModalField T={T} label="今月の合計点（絶対値で設定・差分は自動記録）">
        <input
          type="number"
          min="0"
          step="0.5"
          value={score}
          onChange={(e) => setScore(e.target.value)}
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="理由（必須）">
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="例：消灯後廊下で騒いでいた"
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
        background: T.surfaceAlt,
        border: `1px solid ${T.line}`,
        borderRadius: 999,
        padding: "6px 14px",
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        fontSize: 12,
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
          padding: "14px 16px",
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 10,
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
      {list.map((d) => (
        <div
          key={d.id}
          style={{
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 10,
            padding: "12px 14px",
            boxShadow: T.shadow1,
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
