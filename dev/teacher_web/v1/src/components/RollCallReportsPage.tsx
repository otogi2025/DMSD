import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { RollCallReportOut } from "../api/types";

// 点呼「学生からの報告」处理页 —— 老师看学生在点呼时上报的问题（身体不适 / 当日缺席 / 其他）
// 并标记「対応済み」。后端 GET /rollcall/reports（C_ROLLCALL VIEW）+ PATCH /reports/{id}/resolve
// （C_ROLLCALL MANAGE）。grok 三方对齐审查发现：后端接口早已实装、老师网页从未接线（学生
// 上报后老师端无处处理）。从点呼着陆页入口进、点「戻る」回着陆页（仿 RollCallSummary 中层页）。

// kind → 显示标签 + 配色。三种对应 iOS 点呼界面的三个上报弹窗。
function kindMeta(
  kind: RollCallReportOut["kind"],
  T: typeof RYO,
): { label: string; color: string; soft: string; border: string } {
  switch (kind) {
    case "health":
      return {
        label: "体調不良",
        color: T.warn,
        soft: T.warnSoft,
        border: T.warnBorder,
      };
    case "absence":
      return {
        label: "当日欠席",
        color: T.danger,
        soft: T.dangerSoft,
        border: T.dangerBorder,
      };
    default:
      return {
        label: "その他",
        color: T.ink2,
        soft: T.surfaceAlt,
        border: T.line,
      };
  }
}

const GRID = "180px 100px 1fr 160px 96px 140px";

export function RollCallReportsPage({
  authToken,
  onBack,
}: {
  authToken: string;
  onBack: () => void;
}) {
  const T = RYO;
  const [list, setList] = React.useState<RollCallReportOut[] | null>(null);
  const [err, setErr] = React.useState("");
  // 防双击窗口：同一条上报处理中禁止再次点击
  const [acting, setActing] = React.useState<Record<string, boolean>>({});
  // 默认只看未対応（老师日常只关心待处理的）；切到「すべて」看含已处理的历史。
  const [unresolvedOnly, setUnresolvedOnly] = React.useState(true);

  const refetch = React.useCallback(async () => {
    setErr("");
    try {
      const rows = await api.rollcallReports(authToken, unresolvedOnly);
      setList(rows || []);
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 403) {
        setErr("寮生からの報告の閲覧には「点呼」権限が必要です");
      } else {
        setErr(`報告の取得に失敗 (${(ex && ex.status) || "network"})`);
      }
    }
  }, [authToken, unresolvedOnly]);

  React.useEffect(() => {
    refetch();
  }, [refetch]);

  const doResolve = async (id: string) => {
    if (acting[id]) return;
    setActing((m) => ({ ...m, [id]: true }));
    try {
      await api.resolveRollcallReport(id, authToken);
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      // 409 = 别的老师已先处理；一并刷新即可让它从未対応列表消失。
      if (ex && ex.status === 403) {
        setErr("報告の処理には「点呼」の管理権限が必要です");
      } else if (ex && ex.status === 409) {
        await refetch();
      } else {
        setErr(`処理に失敗 (${(ex && ex.status) || "network"})`);
      }
    } finally {
      setActing((m) => ({ ...m, [id]: false }));
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1080, margin: "0 auto" }}>
      {/* 页头 —— 标题 + 戻る */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 18,
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: T.ink }}>
            寮生からの報告
          </h2>
          <div style={{ fontSize: 12, color: T.ink3, marginTop: 4 }}>
            点呼時に寮生が提出した体調・欠席などの報告を確認し、対応済みにできます
          </div>
        </div>
        <button
          onClick={onBack}
          style={{
            padding: "8px 18px",
            background: T.surface,
            color: T.ink2,
            border: `1px solid ${T.line}`,
            borderRadius: 10,
            fontFamily: "inherit",
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          点呼ホームに戻る
        </button>
      </div>

      {/* 过滤切换 —— 未対応のみ / すべて */}
      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        {[
          { v: true, label: "未対応のみ" },
          { v: false, label: "すべて" },
        ].map((opt) => (
          <button
            key={String(opt.v)}
            onClick={() => setUnresolvedOnly(opt.v)}
            style={{
              padding: "6px 14px",
              background: unresolvedOnly === opt.v ? T.cobalt : T.surface,
              color: unresolvedOnly === opt.v ? "#fff" : T.ink2,
              border: `1px solid ${unresolvedOnly === opt.v ? T.cobalt : T.line}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {err && (
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
          {err}
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
        {/* 表头 */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: GRID,
            background: T.surfaceAlt,
            color: T.ink2,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {["寮生", "種別", "内容", "提出時刻", "状態", "操作"].map((h) => (
            <div key={h} style={{ padding: "10px 14px" }}>
              {h}
            </div>
          ))}
        </div>

        {list === null && (
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
        {list !== null && list.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            {unresolvedOnly
              ? "未対応の報告はありません"
              : "報告はまだありません"}
          </div>
        )}
        {(list || []).map((r, i) => {
          const km = kindMeta(r.kind, T);
          const resolved = r.resolved_at !== null;
          return (
            <div
              key={r.id}
              style={{
                display: "grid",
                gridTemplateColumns: GRID,
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                alignItems: "center",
                fontSize: 13,
              }}
            >
              {/* 学生摘要（姓名/学号/房号）— 老师端点填充，认得出「谁上报」再处理 */}
              <div style={{ padding: "10px 14px" }}>
                {r.student_name ? (
                  <>
                    <div style={{ fontWeight: 600 }}>{r.student_name}</div>
                    {r.student_no && (
                      <div
                        style={{
                          fontSize: 11,
                          color: T.ink3,
                          fontFamily: T.mono,
                        }}
                      >
                        {r.student_no}
                        {r.room_no ? ` · ${r.room_no}` : ""}
                      </div>
                    )}
                  </>
                ) : (
                  <span style={{ fontFamily: T.mono, fontSize: 11 }}>
                    {String(r.student_id).slice(0, 8)}…
                  </span>
                )}
              </div>
              {/* 種別 badge */}
              <div style={{ padding: "10px 14px" }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    background: km.soft,
                    color: km.color,
                    border: `1px solid ${km.border}`,
                  }}
                >
                  {km.label}
                </span>
              </div>
              {/* 内容 */}
              <div
                style={{
                  padding: "10px 14px",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {r.body}
              </div>
              {/* 提出時刻 */}
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  fontSize: 11,
                  color: T.ink3,
                }}
              >
                {new Date(r.created_at).toLocaleString("ja-JP")}
              </div>
              {/* 状態 */}
              <div style={{ padding: "10px 14px" }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    background: resolved ? T.surfaceAlt : T.warnSoft,
                    color: resolved ? T.ink3 : T.warn,
                    border: `1px solid ${resolved ? T.line : T.warnBorder}`,
                  }}
                >
                  {resolved ? "対応済" : "未対応"}
                </span>
              </div>
              {/* 操作 */}
              <div style={{ padding: "10px 14px" }}>
                {resolved ? (
                  <span style={{ color: T.ink3, fontSize: 12 }}>—</span>
                ) : (
                  <button
                    onClick={() => doResolve(r.id)}
                    disabled={acting[r.id]}
                    style={{
                      padding: "4px 12px",
                      background: T.ok,
                      color: "#fff",
                      border: "none",
                      borderRadius: 6,
                      fontFamily: "inherit",
                      fontSize: 11,
                      fontWeight: 700,
                      cursor: acting[r.id] ? "not-allowed" : "pointer",
                    }}
                  >
                    対応済みにする
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
