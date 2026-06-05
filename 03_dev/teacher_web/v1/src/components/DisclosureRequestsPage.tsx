import React from "react";
import { RYO, type RyoTokens } from "../theme";
import { api } from "../api/client";
import type { DisclosureRequest, DisclosureDecisionIn } from "../api/types";

// 源 index.html 28347-28593（accounts.jsx 块，只搬 DisclosureRequestsPage）。
// 界面冻结：JSX 结构 + 内联 style 一字不改，仅改作用域引用（window.RYO→RYO / window.tomoshibiApi→api）。

// 决定决定一栏右上角的轻提示气泡（成功绿 / 失败红）
type Toast = { type: "ok" | "err"; msg: string } | null;

export function DisclosureRequestsPage({
  authToken,
}: {
  authToken: string | null;
}) {
  const T = RYO;
  const [items, setItems] = React.useState<DisclosureRequest[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [deciding, setDeciding] = React.useState<Record<string, boolean>>({}); // {[id]: true} 防重复提交
  const [toast, setToast] = React.useState<Toast>(null);

  const fetchList = React.useCallback(() => {
    if (!authToken) return;
    setLoading(true);
    setLoadError(null);
    api
      .listDisclosureRequests(authToken)
      .then((res) => {
        setItems(res.items || []);
        setLoading(false);
      })
      .catch((e) => {
        setLoadError(e.message || "申請一覧の取得に失敗しました");
        setLoading(false);
      });
  }, [authToken]);

  React.useEffect(() => {
    fetchList();
  }, [fetchList]);

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(id);
    }
  }, [toast]);

  // decision: "approved_full" | "approved_partial" | "rejected"
  const handleDecide = (
    item: DisclosureRequest,
    decision: DisclosureDecisionIn["decision"],
  ) => {
    if (deciding[item.id]) return;
    setDeciding((d) => ({ ...d, [item.id]: true }));
    const body: DisclosureDecisionIn = { decision };
    api
      .decideDisclosure(item.id, body, authToken as string)
      .then(() => {
        setDeciding((d) => ({ ...d, [item.id]: false }));
        const labels: Record<DisclosureDecisionIn["decision"], string> = {
          approved_full: "全部開示",
          approved_partial: "部分開示",
          rejected: "拒否",
        };
        setToast({
          type: decision === "rejected" ? "err" : "ok",
          msg: `${item.student_no} の申請を「${labels[decision]}」しました`,
        });
        fetchList();
      })
      .catch((e) => {
        setDeciding((d) => ({ ...d, [item.id]: false }));
        setToast({ type: "err", msg: e.message || "決定に失敗しました" });
      });
  };

  const statusLabel: Record<string, string> = {
    pending: "待処理",
    approved_full: "全部開示済",
    approved_partial: "部分開示済",
    rejected: "拒否済",
  };
  const statusColor = (s: string) =>
    s === "pending"
      ? // 源用 T.amber || "#f59e0b"；theme.ts 无 amber 字段，运行时恒为 #f59e0b，保留同等行为
        (T as RyoTokens & { amber?: string }).amber || "#f59e0b"
      : s === "rejected"
        ? T.danger
        : T.ok;

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
        指導履歴
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          letterSpacing: -0.3,
          margin: "4px 0 20px",
        }}
      >
        開示申請審査
      </h1>

      {/* 轻提示气泡 */}
      {toast && (
        <div
          style={{
            padding: "10px 14px",
            background: toast.type === "ok" ? T.okSoft : T.dangerSoft,
            border: `1px solid ${toast.type === "ok" ? T.okBorder : T.dangerBorder}`,
            borderRadius: 8,
            color: toast.type === "ok" ? T.ok : T.danger,
            fontSize: 13,
            marginBottom: 16,
          }}
        >
          {toast.type === "ok" ? "✓" : "⚠️"} {toast.msg}
        </div>
      )}

      {/* 错误横幅 */}
      {loadError && (
        <div
          style={{
            padding: "10px 14px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            color: T.danger,
            fontSize: 13,
            marginBottom: 16,
          }}
        >
          ⚠️ {loadError}
        </div>
      )}

      {loading && (
        <div style={{ color: T.ink3, fontSize: 14 }}>読み込み中…</div>
      )}

      {!loading && !loadError && items.length === 0 && (
        <div
          style={{
            padding: "40px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 14,
          }}
        >
          開示申請はありません
        </div>
      )}

      {!loading && items.length > 0 && (
        <div
          style={{
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 10,
            overflow: "hidden",
          }}
        >
          {items.map((item, i) => (
            <div
              key={item.id}
              style={{
                padding: "14px 18px",
                borderTop: i === 0 ? "none" : `1px solid ${T.line}`,
                display: "flex",
                alignItems: "center",
                gap: 14,
                flexWrap: "wrap",
              }}
            >
              {/* 状态徽章 */}
              <span
                style={{
                  padding: "2px 8px",
                  borderRadius: 999,
                  fontSize: 11,
                  fontWeight: 700,
                  background: statusColor(item.status) + "22",
                  color: statusColor(item.status),
                  whiteSpace: "nowrap",
                }}
              >
                {statusLabel[item.status] || item.status}
              </span>

              {/* 学生信息 */}
              <div style={{ flex: 1, minWidth: 120 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>
                  {item.student_no}
                </div>
                <div style={{ fontSize: 12, color: T.ink3 }}>
                  申請:{" "}
                  {item.requested_at ? item.requested_at.slice(0, 10) : "—"}
                  {item.reason && (
                    <span style={{ marginLeft: 8 }}>理由: {item.reason}</span>
                  )}
                </div>
              </div>

              {/* 决定按钮 — 仅 pending 显示 */}
              {item.status === "pending" && (
                <div style={{ display: "flex", gap: 6 }}>
                  {(
                    [
                      ["approved_full", "全部開示", T.ok],
                      ["approved_partial", "部分開示", T.cobalt],
                      ["rejected", "拒否", T.danger],
                    ] as [DisclosureDecisionIn["decision"], string, string][]
                  ).map(([val, label, color]) => (
                    <button
                      key={val}
                      disabled={!!deciding[item.id]}
                      onClick={() => handleDecide(item, val)}
                      style={{
                        padding: "6px 12px",
                        background: color,
                        color: "#fff",
                        border: "none",
                        borderRadius: 7,
                        fontFamily: "inherit",
                        fontSize: 12,
                        fontWeight: 700,
                        cursor: deciding[item.id] ? "not-allowed" : "pointer",
                        opacity: deciding[item.id] ? 0.5 : 1,
                      }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              )}

              {/* 已决定 — 显示决定备注 */}
              {item.status !== "pending" && item.decision_note && (
                <div style={{ fontSize: 12, color: T.ink3 }}>
                  メモ: {item.decision_note}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
