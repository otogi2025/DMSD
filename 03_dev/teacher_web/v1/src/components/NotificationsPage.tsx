import React from "react";
import { RYO } from "../theme";
import type { TeacherProfile } from "../api/types";

// 源 index.html 20771-20898（pages-records 块）。界面原样搬，仅 window.RYO→RYO。
export function NotificationsPage({
  teacher,
  onNav,
}: {
  teacher: TeacherProfile;
  onNav: (view: string) => void;
}) {
  const T = RYO;
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
        通知
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 18px",
          letterSpacing: -0.3,
        }}
      >
        通知中心
      </h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <NotifCard
          n="—"
          label="審査待ち申請"
          color={T.cobalt}
          onClick={() => onNav("applications")}
        />
        <NotifCard
          n="—"
          label="清掃審査"
          color={T.warn}
          onClick={() => onNav("cleaning")}
        />
        <NotifCard
          n="—"
          label="通報"
          color={T.danger}
          onClick={() => onNav("community")}
        />
        <NotifCard
          n="—"
          label="警告リスト"
          color={T.warn}
          onClick={() => onNav("discipline")}
        />
      </div>
      <div
        style={{
          fontSize: 12,
          color: T.ink3,
          letterSpacing: 1.5,
          fontWeight: 700,
          marginBottom: 10,
        }}
      >
        最近の通知
      </div>
      {/* 通知功能本期未实装 — 准备中占位 */}
      <div
        style={{
          background: T.surface,
          border: `1px dashed ${T.lineStrong}`,
          borderRadius: 12,
          padding: "32px 0",
          textAlign: "center",
          color: T.ink3,
          fontSize: 13,
        }}
      >
        通知機能は準備中です
      </div>
    </div>
  );
}

function NotifCard({
  n,
  label,
  color,
  onClick,
}: {
  n: string;
  label: string;
  color: string;
  onClick: () => void;
}) {
  const T = RYO;
  return (
    <button
      onClick={onClick}
      style={{
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        padding: "18px 20px",
        boxShadow: T.shadow1,
        textAlign: "left",
        fontFamily: "inherit",
        cursor: "pointer",
      }}
    >
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          fontFamily: T.mono,
          color,
        }}
      >
        {n}
      </div>
      <div style={{ fontSize: 12, color: T.ink2, marginTop: 2 }}>{label}</div>
      <div
        style={{
          fontSize: 11,
          color: T.cobalt,
          fontWeight: 600,
          marginTop: 8,
        }}
      >
        開く →
      </div>
    </button>
  );
}
