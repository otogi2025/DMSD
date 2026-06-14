import React from "react";
import { RYO, type RyoTokens } from "../theme";

// 跨多个页面复用的小组件 —— 从旧 index.html 各块原样搬（界面冻结）。
// ConfirmModal / DormBadge 自带 RYO；ModalShell / ModalField / ModalFooter 沿用原 props 的 T 参数（调用方传 RYO）。

// 源 index.html 11065-11154（select-teacher 块）
export function ConfirmModal({
  title,
  desc,
  danger,
  confirmLabel,
  onCancel,
  onConfirm,
}: {
  title: string;
  desc?: string;
  danger?: boolean;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const T = RYO;
  return (
    <div
      onClick={onCancel}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,.48)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 200,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 440,
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          padding: "24px 28px",
        }}
      >
        <div style={{ fontSize: 17, fontWeight: 700 }}>{title}</div>
        {desc && (
          <div
            style={{
              fontSize: 13,
              color: T.ink3,
              marginTop: 8,
              lineHeight: 1.6,
            }}
          >
            {desc}
          </div>
        )}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            marginTop: 22,
          }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: "9px 18px",
              background: "transparent",
              color: T.ink,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            キャンセル
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: "9px 18px",
              background: danger ? T.danger : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            {confirmLabel || "確認"}
          </button>
        </div>
      </div>
    </div>
  );
}

// 源 index.html 11902-11921（shell 块）
export function DormBadge({ dorm }: { dorm: string }) {
  const T = RYO;
  const isMen = dorm === "men";
  return (
    <span
      style={{
        fontSize: 10,
        fontWeight: 700,
        padding: "2px 7px",
        borderRadius: 4,
        letterSpacing: 0.5,
        background: isMen ? T.maleSoft : T.femaleSoft,
        color: isMen ? T.maleAccent : T.femaleAccent,
        border: `1px solid ${isMen ? T.maleAccent : T.femaleAccent}33`,
      }}
    >
      {isMen ? "男子寮" : "女子寮"}
    </span>
  );
}

// 源 index.html 18534-18596（front-desk 块）
export function ModalShell({
  T,
  title,
  onClose,
  children,
}: {
  T: RyoTokens;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,0.55)",
        zIndex: 90,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: T.surface,
          borderRadius: 14,
          width: 540,
          maxWidth: "100%",
          boxShadow: T.shadowModal,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "16px 20px",
            borderBottom: `1px solid ${T.line}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ fontSize: 15, fontWeight: 700 }}>{title}</div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 20,
              color: T.ink3,
              cursor: "pointer",
            }}
          >
            ×
          </button>
        </div>
        <div
          style={{
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

// 源 index.html 18597-18613（front-desk 块的 Field，export 名 ModalField）
export function ModalField({
  T,
  label,
  children,
}: {
  T: RyoTokens;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginBottom: 6,
        }}
      >
        {label}
      </div>
      {children}
    </div>
  );
}

// 源 index.html 18615-18660（front-desk 块）
export function ModalFooter({
  T,
  onClose,
  onSubmit,
  disabled,
}: {
  T: RyoTokens;
  onClose: () => void;
  onSubmit: () => void;
  disabled?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "flex-end",
        gap: 8,
        marginTop: 6,
      }}
    >
      <button
        onClick={onClose}
        style={{
          padding: "8px 16px",
          background: T.surface,
          color: T.ink2,
          border: `1px solid ${T.lineStrong}`,
          borderRadius: 8,
          fontFamily: "inherit",
          fontSize: 13,
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        キャンセル
      </button>
      <button
        onClick={onSubmit}
        disabled={disabled}
        style={{
          padding: "8px 16px",
          background: disabled ? T.line : T.cobalt,
          color: "#fff",
          border: "none",
          borderRadius: 8,
          fontFamily: "inherit",
          fontSize: 13,
          fontWeight: 700,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        登録
      </button>
    </div>
  );
}

// 源 index.html 16293-16317（applications 块；ApplicationsPage + OutstayDetailModal 跨块共用）
export function StateBadge({ s }: { s: string }) {
  const T = RYO;
  const map = (
    {
      pending: [T.warn, T.warnSoft, T.warnBorder, "審査待ち"],
      approved: [T.ok, T.okSoft, T.okBorder, "承認済"],
      rejected: [T.danger, T.dangerSoft, T.dangerBorder, "却下"],
      question: [T.cobalt, T.cobaltSoft, T.infoBorder, "質問あり"],
    } as Record<string, [string, string, string, string]>
  )[s];
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: "2px 8px",
        borderRadius: 4,
        background: map[1],
        color: map[0],
        border: `1px solid ${map[2]}`,
        letterSpacing: 0.5,
        whiteSpace: "nowrap",
      }}
    >
      {map[3]}
    </span>
  );
}
