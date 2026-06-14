import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { TeacherProfile, RollCallSessionOut } from "../api/types";

// 源 index.html 18892-19119（pages-records 块 RecordsPage）。
// 界面原样搬，仅 window.RYO→RYO / window.tomoshibiApi→api / 日语注释翻成中文。

// 点呼 session 历史行 — 后端 rollcallSessionsHistory 返回里带 summary 统计字段，
// 这几个统计字段不在 RollCallSessionOut 声明内，本页只读取展示，故扩成可选。
type RecordsSessionRow = RollCallSessionOut & {
  name?: string | null;
  present_count?: number | null;
  late_count?: number | null;
  absent_count?: number | null;
};

export function RecordsPage({
  params,
  authToken,
}: {
  teacher: TeacherProfile;
  params?: { date?: string };
  onNav: (view: string) => void;
  authToken: string;
}) {
  const T = RYO;
  const date = (params && params.date) || "2026-04-21";

  // 5-27 backend commit c0a22d1 — 拉过去 7 天点呼 session 历史
  const [backendHistory, setBackendHistory] = React.useState<
    RecordsSessionRow[] | null
  >(null);
  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    api
      .rollcallSessionsHistory(authToken)
      .then((rows) => {
        if (!cancelled) setBackendHistory(rows);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[RecordsPage] rollcallSessionsHistory 失败", e);
        setBackendHistory(null);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

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
        記録
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 18px",
          letterSpacing: -0.3,
        }}
      >
        点呼記録
      </h1>

      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600 }}>
          日付
        </label>
        <input
          type="date"
          defaultValue={date}
          style={{
            padding: "7px 10px",
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: T.mono,
            fontSize: 13,
          }}
        />
        <label
          style={{
            fontSize: 11,
            color: T.ink2,
            fontWeight: 600,
            marginLeft: 10,
          }}
        >
          点呼名
        </label>
        <select
          style={{
            padding: "7px 10px",
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 13,
          }}
        >
          <option>晩点呼・普通寮生</option>
          <option>朝点呼・普通寮生</option>
        </select>
        <div style={{ flex: 1 }} />
        <button
          onClick={() => alert("この機能は準備中です")}
          style={{
            padding: "6px 12px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          CSV 出力
        </button>
        <button
          onClick={() => window.print()}
          style={{
            padding: "6px 12px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          印刷・PDF 保存
        </button>
      </div>

      {/* 点呼 session 历史列表 — 来自后端 rollcallSessionsHistory */}
      {backendHistory === null ? (
        <div
          style={{
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
          }}
        >
          {authToken ? "点呼記録を読み込み中..." : "ログインしてください"}
        </div>
      ) : backendHistory.length === 0 ? (
        <div
          style={{
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
          }}
        >
          点呼記録がありません
        </div>
      ) : (
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
              gridTemplateColumns: "1fr 160px 120px 100px 100px",
              background: T.surfaceAlt,
              fontSize: 11,
              color: T.ink2,
              fontWeight: 600,
              letterSpacing: 1,
              borderBottom: `1px solid ${T.line}`,
            }}
          >
            {["点呼名", "日時", "出席", "遅刻", "欠席"].map((h) => (
              <div key={h} style={{ padding: "10px 12px" }}>
                {h}
              </div>
            ))}
          </div>
          {backendHistory.map((s, i) => (
            <div
              key={s.id || i}
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 160px 120px 100px 100px",
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                fontSize: 12.5,
                alignItems: "center",
              }}
            >
              <div style={{ padding: "9px 12px", fontWeight: 600 }}>
                {s.name || s.session_type || "—"}
              </div>
              <div
                style={{
                  padding: "9px 12px",
                  fontFamily: T.mono,
                  color: T.ink2,
                  fontSize: 12,
                }}
              >
                {s.started_at
                  ? new Date(s.started_at).toLocaleString("ja-JP", {
                      month: "2-digit",
                      day: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "—"}
              </div>
              <div style={{ padding: "9px 12px", color: T.ok }}>
                {s.present_count ?? "—"}
              </div>
              <div style={{ padding: "9px 12px", color: T.late }}>
                {s.late_count ?? "—"}
              </div>
              <div style={{ padding: "9px 12px", color: T.danger }}>
                {s.absent_count ?? "—"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
