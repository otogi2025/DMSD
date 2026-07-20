import React from "react";
import { RYO } from "../theme";

// 源 index.html 13014-13450（components/override-modal.jsx 块）。界面原样搬，仅 window.RYO→RYO。
// 手動調整モーダル — 欠席届承認 / 体調報告 / 調整履歴を統合表示。

// 提出された欠席届の形
interface PendingLeave {
  reason: string;
  submittedAt?: string;
}

// 過去の調整履歴の形
interface OverrideRecord {
  by: string;
  reason: string;
}

// このモーダルが受け取る学生のビューモデル（バックエンド型ではなく画面ローカルの形）
interface OverrideStudent {
  id: string;
  name: string;
  room: string;
  status: string;
  pending?: PendingLeave | null;
  health?: string | null;
  override?: OverrideRecord | null;
}

// 保存時に親へ返す値
interface OverrideSavePayload {
  status: string;
  reason: string;
}

export function OverrideModal({
  student,
  onClose,
  onSave,
}: {
  student: OverrideStudent;
  onClose: () => void;
  onSave: (payload: OverrideSavePayload) => void;
}) {
  const T = RYO;
  const [status, setStatus] = React.useState<string>(
    student.status === "unknown" ? "ok" : student.status,
  );
  const [reason, setReason] = React.useState<string>("");
  const needsReason = status !== student.status || student.pending;
  const canSave = !needsReason || reason.trim().length > 0;

  const statuses = [
    {
      k: "ok",
      label: "時間内",
      color: T.ok,
      soft: T.okSoft,
      hint: "対面確認済み",
    },
    {
      k: "late",
      label: "遅刻",
      color: T.late,
      soft: T.lateSoft,
      hint: "定刻に間に合わず",
    },
    {
      k: "absent",
      label: "欠席",
      color: T.danger,
      soft: T.dangerSoft,
      hint: "未確認のまま終了",
    },
    {
      k: "exempt",
      label: "免除",
      color: T.info,
      soft: T.infoSoft,
      hint: "本日は点呼対象外",
    },
  ];

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,.48)",
        backdropFilter: "blur(2px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        fontFamily: T.font,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 620,
          maxHeight: "92vh",
          overflow: "auto",
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          color: T.ink,
        }}
      >
        <div
          style={{
            padding: "20px 24px 16px",
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              letterSpacing: 2,
              fontWeight: 600,
            }}
          >
            手動調整
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 12,
              marginTop: 4,
            }}
          >
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: -0.3,
              }}
            >
              {student.name}
            </div>
            <div style={{ fontSize: 12, fontFamily: T.mono, color: T.ink3 }}>
              {student.room} · {student.id}
            </div>
          </div>
        </div>

        <div style={{ padding: "18px 24px" }}>
          {/* 提出済み申請の只読展開 — 原来这里有假的「承認/却下」按钮 + 「保存で
              確定し学生にプッシュ通知」的伪成功文案，实际从不调审批接口也不发通知
              （审查 web#5）。审批走申请页的真接口（带审批权限校验），这里只提示 */}
          {student.pending && (
            <div
              style={{
                padding: 14,
                background: T.warnSoft,
                border: `1px solid ${T.warnBorder}`,
                borderRadius: 10,
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  fontSize: 11,
                  color: T.warn,
                  fontWeight: 700,
                  letterSpacing: 1,
                  marginBottom: 6,
                }}
              >
                提出された申請
              </div>
              <div style={{ fontSize: 13, color: T.ink, marginBottom: 8 }}>
                {student.pending.reason}
              </div>
              {student.pending.submittedAt && (
                <div
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    fontFamily: T.mono,
                    marginBottom: 10,
                  }}
                >
                  提出：{student.pending.submittedAt}
                </div>
              )}
              <div style={{ fontSize: 11, color: T.ink3 }}>
                ※承認・却下は「申請」ページで行ってください。
              </div>
            </div>
          )}

          {/* 体調報告の展開 */}
          {student.health && (
            <div
              style={{
                padding: 14,
                background: T.dangerSoft,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 10,
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  fontSize: 11,
                  color: T.danger,
                  fontWeight: 700,
                  letterSpacing: 1,
                  marginBottom: 6,
                }}
              >
                体調報告
              </div>
              <div style={{ fontSize: 13, color: T.ink, marginBottom: 10 }}>
                {student.health}
              </div>
              <div style={{ fontSize: 10, color: T.ink3 }}>
                ※「保存して反映」時に既読として記録されます
              </div>
            </div>
          )}

          {/* 調整履歴 */}
          {student.override && (
            <div
              style={{
                padding: 12,
                background: T.surfaceAlt,
                border: `1px solid ${T.line}`,
                borderRadius: 10,
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  fontWeight: 700,
                  letterSpacing: 1,
                  marginBottom: 6,
                }}
              >
                調整履歴
              </div>
              <div
                style={{
                  fontSize: 12,
                  color: T.ink2,
                  fontFamily: T.mono,
                }}
              >
                {student.override.by} · 19:35
              </div>
              <div style={{ fontSize: 12, color: T.ink }}>
                {student.override.reason}
              </div>
            </div>
          )}

          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              letterSpacing: 1.5,
              fontWeight: 600,
              marginBottom: 10,
              textTransform: "uppercase",
            }}
          >
            状態を選択
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: 8,
              marginBottom: 18,
            }}
          >
            {statuses.map((o) => (
              <button
                key={o.k}
                onClick={() => setStatus(o.k)}
                style={{
                  textAlign: "left",
                  padding: "11px 14px",
                  borderRadius: 10,
                  cursor: "pointer",
                  background: status === o.k ? o.soft : T.surface,
                  border:
                    status === o.k
                      ? `2px solid ${o.color}`
                      : `1px solid ${T.line}`,
                  color: T.ink,
                  fontFamily: "inherit",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <span
                    style={{
                      width: 14,
                      height: 14,
                      borderRadius: 8,
                      border: `2px solid ${status === o.k ? o.color : T.lineStrong}`,
                      background: status === o.k ? o.color : "transparent",
                      boxShadow:
                        status === o.k
                          ? `inset 0 0 0 3px ${T.surface}`
                          : "none",
                    }}
                  />
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: status === o.k ? o.color : T.ink,
                    }}
                  >
                    {o.label}
                  </span>
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    marginTop: 3,
                    marginLeft: 24,
                  }}
                >
                  {o.hint}
                </div>
              </button>
            ))}
          </div>

          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              letterSpacing: 1.5,
              fontWeight: 600,
              marginBottom: 6,
              textTransform: "uppercase",
            }}
          >
            調整理由{" "}
            {needsReason && <span style={{ color: T.danger }}>※必須</span>}
          </div>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            placeholder="例：未携帯・対面で確認済み / 保健室で休養中"
            style={{
              width: "100%",
              padding: "10px 12px",
              background: T.surface,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              color: T.ink,
              outline: "none",
              boxSizing: "border-box",
              resize: "vertical",
            }}
          />
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              marginTop: 6,
              fontFamily: T.mono,
            }}
          >
            記録は監査ログに残ります
          </div>
        </div>

        <div
          style={{
            padding: "14px 24px",
            borderTop: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            borderRadius: "0 0 14px 14px",
          }}
        >
          <button
            onClick={onClose}
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
            disabled={!canSave}
            onClick={() => onSave({ status, reason })}
            style={{
              padding: "9px 20px",
              background: canSave ? T.cobalt : T.lineStrong,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: canSave ? "pointer" : "not-allowed",
            }}
          >
            保存して反映
          </button>
        </div>
      </div>
    </div>
  );
}
