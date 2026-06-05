import React from "react";
import { RYO } from "../theme";
import type { RollCallSummaryOut } from "../api/types";

// Task #13 —「点呼総結」中层页 (spec §5.6 + WEB_DESIGN_LOG §11.1 P0)
// 显示 backend GET /rollcall/sessions/:id/summary 返回的 4 区块:
//   absent / late / health_issue / exempted_outstay
//「回主页」按钮回 /roll-call landing。RollCallLanding 的 lastEnded card 也有
//「看本场结果」入口（再次查看用）。

// 区块内单条学生记录的形状。健康报告(health_issue)等区块可能带 reason 备注。
interface SummaryEntry {
  student_id: string;
  name: string;
  room_no: string;
  reason?: string;
}

// 上一场已结束点呼的概要（点呼页结束时由 setLastEnded 写入）。
interface LastEnded {
  name: string;
  start: string;
  end: string;
  rate: string;
  sessionName?: string;
}

// 源 index.html 13461-13680（roll-call-summary 块）。界面原样搬，仅 window.RYO→RYO。
export function RollCallSummary({
  summary,
  lastEnded,
  onBack,
}: {
  summary: RollCallSummaryOut | null;
  lastEnded: LastEnded | null;
  onBack: () => void;
}) {
  const T = RYO;
  if (!summary) {
    return (
      <div style={{ padding: 48, textAlign: "center", color: T.ink3 }}>
        <div style={{ fontSize: 14, marginBottom: 16 }}>
          集計結果がありません
        </div>
        <button
          onClick={onBack}
          style={{
            padding: "10px 20px",
            background: T.cobalt,
            color: "#fff",
            border: "none",
            borderRadius: 10,
            fontFamily: "inherit",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          ホームに戻る
        </button>
      </div>
    );
  }
  const sections = [
    {
      key: "absent",
      label: "欠席",
      color: T.danger,
      soft: T.dangerSoft,
      border: T.dangerBorder,
      list: (summary.absent || []) as SummaryEntry[],
    },
    {
      key: "late",
      label: "遅刻",
      color: T.late,
      soft: T.lateSoft,
      border: T.lateBorder,
      list: (summary.late || []) as SummaryEntry[],
    },
    {
      key: "health_issue",
      label: "体調報告（要配慮）",
      color: T.warn,
      soft: T.warnSoft,
      border: T.warnBorder,
      list: (summary.health_issue || []) as SummaryEntry[],
    },
    {
      key: "exempted_outstay",
      label: "外泊につき対象外",
      color: T.ink2,
      soft: T.graySoft,
      border: T.grayBorder,
      list: (summary.exempted_outstay || []) as SummaryEntry[],
    },
  ];
  return (
    <div style={{ padding: "28px 32px 48px", color: T.ink }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 600,
        }}
      >
        点呼 &gt; 集計
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 6px",
          letterSpacing: -0.3,
        }}
      >
        点呼集計
      </h1>
      {lastEnded && (
        <div
          style={{
            fontSize: 13,
            color: T.ink3,
            marginBottom: 22,
            fontFamily: T.mono,
          }}
        >
          {lastEnded.sessionName || lastEnded.name} · {lastEnded.start} →{" "}
          {lastEnded.end} · 出席率 {lastEnded.rate}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: 16,
          marginBottom: 24,
        }}
      >
        {sections.map((sec) => (
          <div
            key={sec.key}
            style={{
              background: T.surface,
              border: `1px solid ${sec.border}`,
              borderRadius: 12,
              padding: 16,
              boxShadow: T.shadow1,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  fontSize: 13,
                  color: sec.color,
                  fontWeight: 700,
                  letterSpacing: 1,
                }}
              >
                {sec.label}
              </div>
              <div
                style={{
                  background: sec.soft,
                  color: sec.color,
                  border: `1px solid ${sec.border}`,
                  padding: "2px 10px",
                  borderRadius: 999,
                  fontSize: 12,
                  fontWeight: 700,
                  fontFamily: T.mono,
                }}
              >
                {sec.list.length}名
              </div>
            </div>
            {sec.list.length === 0 ? (
              <div
                style={{
                  padding: 12,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 12,
                }}
              >
                該当なし
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                {sec.list.map((entry) => (
                  <div
                    key={entry.student_id}
                    style={{
                      padding: "8px 10px",
                      background: T.surfaceAlt,
                      borderRadius: 8,
                      fontSize: 13,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>{entry.name}</span>
                    <span
                      style={{
                        fontFamily: T.mono,
                        fontSize: 11,
                        color: T.ink3,
                      }}
                    >
                      {entry.room_no}
                      {entry.reason ? ` · ${entry.reason}` : ""}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={onBack}
        style={{
          padding: "12px 28px",
          background: T.cobalt,
          color: "#fff",
          border: "none",
          borderRadius: 10,
          fontFamily: "inherit",
          fontSize: 14,
          fontWeight: 700,
          cursor: "pointer",
          boxShadow: "0 4px 12px rgba(43,77,140,.22)",
        }}
      >
        ホームに戻る
      </button>
    </div>
  );
}
