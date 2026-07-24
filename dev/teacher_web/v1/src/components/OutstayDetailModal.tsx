import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import { ConfirmModal, StateBadge } from "./shared";
import {
  outstayDeadline,
  parseJst,
  isLateSubmission,
  formatJstDeadline,
} from "../utils";
import type { Application, ApprovalStep } from "../api/types";

// 源 index.html 16409-17195（components/outstay-detail-modal.jsx 块）。
// 界面冻结：JSX 结构 + 所有内联 style 一字不改，仅改作用域引用方式。
// 外泊申请详情弹窗 —— 参考 02_gaihaku_form_reference.jpeg 数字化。
// StateBadge 从 ./shared、4 个 JST 时间助手从 ../utils import（原走 window，已迁模块）。

// app prop 是 _adaptBackendAppsByKind 做的 UI shape。
// _backend 字段里放着原始的 pendingForMe Application。
type OutstayUiApp = {
  applicant: string;
  state: string;
  depart: string;
  submitted: string;
  return_: string;
  _backend?: Application | null;
};

// OutstayDetailModal —— 打开时同时用 getApplication(id) 拉完整 ApplicationOut，
// 再用 getAuditLog(id) 取审计日志。
export function OutstayDetailModal({
  app,
  onClose,
  onAction,
  onReturn,
  authToken,
}: {
  app: OutstayUiApp;
  onClose: () => void;
  onAction: (action: string, comment: string) => void;
  // 差戻 —— 把届退回给学生修改重提。reason 是差戻理由（必填）。
  onReturn: (reason: string) => void;
  authToken: string;
}) {
  const T = RYO;
  const [confirm, setConfirm] = React.useState<{
    action: string;
    label: string;
  } | null>(null);
  // 杭田 2026-06-04 二-4：审批时给学生看的评论输入（补强旧 UI 弱点）
  const [comment, setComment] = React.useState("");
  // 差戻理由输入弹窗的开关 / 输入内容 / 校验错误提示
  const [returnOpen, setReturnOpen] = React.useState(false);
  const [returnReason, setReturnReason] = React.useState("");
  const [returnError, setReturnError] = React.useState<string | null>(null);
  // backend 取来的完整 ApplicationOut
  const [detail, setDetail] = React.useState<Application | null>(null);
  // 审计日志 —— 后端返回 created_at / action 字段，保持松类型不改渲染
  const [auditLog, setAuditLog] = React.useState<any[]>([]);
  const [loadingDetail, setLoadingDetail] = React.useState(false);
  const [detailError, setDetailError] = React.useState<string | null>(null);

  // 每次打开都取完整 detail + 审计日志
  React.useEffect(() => {
    const backendApp = app && app._backend;
    if (!backendApp || !authToken) return;
    let cancelled = false;
    setLoadingDetail(true);
    setDetailError(null);
    Promise.all([
      api.getApplication(backendApp.id, authToken),
      api.getAuditLog(backendApp.id, authToken).catch(() => []),
    ])
      .then(([det, log]) => {
        if (cancelled) return;
        setDetail(det);
        setAuditLog(Array.isArray(log) ? log : []);
      })
      .catch((e) => {
        if (cancelled) return;
        setDetailError(e.message || "詳細取得に失敗しました");
      })
      .finally(() => {
        if (!cancelled) setLoadingDetail(false);
      });
    return () => {
      cancelled = true;
    };
  }, [app, authToken]);

  const Section = ({
    title,
    children,
  }: {
    title: string;
    children: React.ReactNode;
  }) => (
    <div style={{ marginBottom: 18 }}>
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 700,
          marginBottom: 8,
          paddingBottom: 4,
          borderBottom: `1px solid ${T.line}`,
        }}
      >
        § {title}
      </div>
      {children}
    </div>
  );
  const F = ({
    label,
    children,
    mono,
  }: {
    label: string;
    children?: React.ReactNode;
    mono?: boolean;
  }) => (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "160px 1fr",
        gap: 10,
        fontSize: 13,
        padding: "5px 0",
      }}
    >
      <div style={{ color: T.ink3, fontSize: 12 }}>{label}</div>
      <div style={{ color: T.ink, fontFamily: mono ? T.mono : "inherit" }}>
        {children || "—"}
      </div>
    </div>
  );

  // 显示 ApplicationOut 的 approval_chain 用的助手
  const chainDecisionLabel = (d: string | null) => {
    if (!d) return [T.ink3, T.surfaceAlt, T.line, "未審査"];
    if (d === "approve") return [T.ok, T.okSoft, T.okBorder, "✓ 承認"];
    if (d === "reject")
      return [T.danger, T.dangerSoft, T.dangerBorder, "✗ 却下"];
    return [T.ink3, T.surfaceAlt, T.line, d];
  };

  // applicant 名：有 detail 用 detail.student.name，没有就用 app.applicant（已 adapt）
  const applicantName =
    (detail && detail.student && detail.student.name) || app.applicant;
  const kindLabel =
    (detail && detail.kind) || (app._backend && app._backend.kind) || "";
  const titleLabel =
    kindLabel === "帰国"
      ? "帰国届"
      : kindLabel === "帰省"
        ? "帰省届"
        : "外泊許可願";

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,.55)",
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
          width: 860,
          maxHeight: "94vh",
          overflow: "auto",
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          color: T.ink,
        }}
      >
        {/* 头部 */}
        <div
          style={{
            padding: "22px 28px 18px",
            borderBottom: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            borderRadius: "14px 14px 0 0",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
              }}
            >
              申請 &gt; {kindLabel} &gt; {applicantName} の申請
            </div>
            <div style={{ flex: 1 }} />
            <StateBadge s={app.state} />
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 14,
              marginTop: 8,
            }}
          >
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: -0.3,
              }}
            >
              {titleLabel}
            </div>
            <div style={{ fontSize: 12, fontFamily: T.mono, color: T.ink3 }}>
              {app._backend && String(app._backend.id).slice(0, 8)}… · 提出{" "}
              {app.submitted}
            </div>
          </div>
        </div>

        {/* 主体 */}
        <div style={{ padding: "22px 28px" }}>
          {loadingDetail && (
            <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
              詳細を読み込み中…
            </div>
          )}
          {detailError && (
            <div
              style={{
                padding: "10px 14px",
                background: "#fff0f0",
                border: "1px solid #f5c6cb",
                borderRadius: 8,
                color: T.danger,
                fontSize: 13,
                marginBottom: 16,
              }}
            >
              {detailError}
            </div>
          )}

          {/* 申请者本人 */}
          <Section title="申請者本人">
            <F label="氏名">{applicantName}</F>
            {detail && detail.student && (
              <>
                <F label="部屋番号" mono>
                  {detail.student.room_no}
                </F>
                <F label="寮" mono>
                  {detail.student.dorm_unit
                    ? `${detail.student.dorm_unit}寮`
                    : "—"}
                </F>
              </>
            )}
            <F label="本人連絡先" mono>
              {(detail && detail.contact_phone) || "—"}
            </F>
            <F label="同行者">{(detail && detail.companion) || "—"}</F>
          </Section>

          {/* 日时·移动 */}
          <Section title="日時・移動手段">
            <F label="出発日" mono>
              {detail ? String(detail.leave_date) : app.depart}
            </F>
            <F label="出発時刻" mono>
              {detail ? String(detail.leave_time) : "—"}
            </F>
            <F label="出発方法">{detail ? detail.leave_method : "—"}</F>
            <F label="帰寮予定日" mono>
              {detail ? String(detail.return_date) : app.return_}
            </F>
            <F label="帰寮予定時刻" mono>
              {detail ? String(detail.return_time) : "—"}
            </F>
            <F label="帰寮方法">{detail ? detail.return_method : "—"}</F>
            <F label="タクシー予約">
              {detail && detail.taxi_reservation_time
                ? String(detail.taxi_reservation_time)
                : "予約なし"}
            </F>
          </Section>

          {/* 回国航班信息（仅 kind=帰国） */}
          {detail && detail.kind === "帰国" && (
            <Section title="帰国便情報">
              <F label="出発空港" mono>
                {detail.flight_dep_air}
              </F>
              <F label="出発日時" mono>
                {detail.flight_dep_at
                  ? new Date(detail.flight_dep_at).toLocaleString("ja-JP")
                  : "—"}
              </F>
              <F label="到着空港" mono>
                {detail.flight_arr_air}
              </F>
              <F label="到着日時" mono>
                {detail.flight_arr_at
                  ? new Date(detail.flight_arr_at).toLocaleString("ja-JP")
                  : "—"}
              </F>
            </Section>
          )}

          {/* 住宿地 */}
          {detail &&
            detail.stay_locations &&
            detail.stay_locations.length > 0 && (
              <Section title="宿泊先">
                {detail.stay_locations.map((loc, i) => (
                  <div
                    key={i}
                    style={{
                      marginBottom:
                        i < detail.stay_locations!.length - 1 ? 10 : 0,
                    }}
                  >
                    {detail.stay_locations!.length > 1 && (
                      <div
                        style={{
                          fontSize: 11,
                          color: T.ink3,
                          fontWeight: 600,
                          marginBottom: 4,
                        }}
                      >
                        {i + 1} カ所目
                      </div>
                    )}
                    <F label="名称">{loc.name || "—"}</F>
                    <F label="住所">{loc.address || "—"}</F>
                    <F label="電話" mono>
                      {loc.phone || "—"}
                    </F>
                  </div>
                ))}
              </Section>
            )}

          {/* 目的地城市 / 理由 */}
          <Section title="行先・理由">
            {!(detail && detail.kind === "帰国") && (
              <F label="行先都市">{(detail && detail.dest_cities) || "—"}</F>
            )}
            <F label="長期休暇区分">
              {/* web#35: detail 未就绪时不假装「通常外出」——避免老师误判 */}
              {detail
                ? detail.is_long_vacation
                  ? "長期休暇"
                  : "通常外出"
                : "—"}
            </F>
            {detail && detail.reason && (
              <div
                style={{
                  marginTop: 6,
                  background: T.surfaceAlt,
                  border: `1px solid ${T.line}`,
                  borderRadius: 8,
                  padding: "10px 12px",
                  fontSize: 13,
                  lineHeight: 1.7,
                }}
              >
                {detail.reason}
              </div>
            )}
          </Section>

          {/* 餐食跳过 */}
          {detail && detail.meals_skip && detail.meals_skip.length > 0 && (
            <Section title="欠食">
              {detail.meals_skip.map((m: any, i) => (
                <F key={i} label={String(m.date || i)} mono>
                  {/* 后端 MealSkipEntry = {date, meal}（meal 已是「朝食/昼食/夕食」）。
                      原来读 m.breakfast/lunch/dinner 三个不存在的字段 → 每行恒显「—」（TW-116）。 */}
                  {m.meal || "—"}
                </F>
              ))}
              {detail.meal_note && <F label="食事備考">{detail.meal_note}</F>}
            </Section>
          )}

          {/* 提交期限（仅外泊能算出来） */}
          {kindLabel === "外泊" && <DeadlineSection app={app} />}

          {/* 承认链 (approval_chain) */}
          {detail &&
            detail.approval_chain &&
            detail.approval_chain.length > 0 && (
              <Section title="承認経路">
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                  }}
                >
                  {detail.approval_chain.map((step: ApprovalStep, i) => {
                    const [col, bg, bd, lbl] = chainDecisionLabel(
                      step.decision,
                    );
                    return (
                      <div
                        key={i}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          padding: "10px 14px",
                          background: bg,
                          border: `1px solid ${bd}`,
                          borderRadius: 8,
                        }}
                      >
                        <span
                          style={{
                            width: 22,
                            height: 22,
                            borderRadius: 11,
                            background: col,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 11,
                            color: "#fff",
                            fontWeight: 700,
                            flexShrink: 0,
                          }}
                        >
                          {i + 1}
                        </span>
                        <div style={{ flex: 1 }}>
                          <div
                            style={{
                              fontSize: 12,
                              fontWeight: 700,
                              color: T.ink,
                            }}
                          >
                            {step.approver_role}
                          </div>
                          {step.decided_at && (
                            <div
                              style={{
                                fontSize: 11,
                                color: T.ink3,
                                fontFamily: T.mono,
                              }}
                            >
                              {new Date(step.decided_at).toLocaleString(
                                "ja-JP",
                              )}
                            </div>
                          )}
                          {step.comment && (
                            <div
                              style={{
                                fontSize: 12,
                                color: T.ink2,
                                marginTop: 3,
                                fontStyle: "italic",
                              }}
                            >
                              「{step.comment}」
                            </div>
                          )}
                        </div>
                        <span
                          style={{
                            fontSize: 11,
                            fontWeight: 700,
                            color: col,
                            padding: "2px 8px",
                            borderRadius: 4,
                            border: `1px solid ${bd}`,
                            whiteSpace: "nowrap",
                          }}
                        >
                          {lbl}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </Section>
            )}

          {/* 审计日志 */}
          {auditLog.length > 0 && (
            <Section title="監査ログ">
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                {auditLog.map((entry, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      gap: 12,
                      fontSize: 12,
                      padding: "7px 10px",
                      background: T.surfaceAlt,
                      borderRadius: 6,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: T.mono,
                        color: T.ink3,
                        minWidth: 130,
                      }}
                    >
                      {entry.created_at
                        ? new Date(entry.created_at).toLocaleString("ja-JP")
                        : "—"}
                    </span>
                    <span style={{ color: T.ink2 }}>
                      {entry.action || entry.event || JSON.stringify(entry)}
                    </span>
                  </div>
                ))}
              </div>
            </Section>
          )}
        </div>

        {/* 杭田 2026-06-04 二-4：给学生看的评论输入栏（承认/却下时通知学生） */}
        <div style={{ padding: "12px 28px 0", background: T.surfaceAlt }}>
          <label
            style={{
              display: "block",
              fontSize: 12,
              fontWeight: 600,
              color: T.ink2,
              marginBottom: 6,
            }}
          >
            学生へのコメント（任意・承認/却下時に学生へメールで通知されます）
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="例：書類の不備を修正してください"
            rows={2}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "8px 10px",
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              resize: "vertical",
            }}
          />
        </div>

        {/* 底部 —— 操作按钮 */}
        <div
          style={{
            padding: "14px 28px",
            borderTop: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            display: "flex",
            gap: 8,
            borderRadius: "0 0 14px 14px",
          }}
        >
          <button
            onClick={onClose}
            style={{
              padding: "10px 18px",
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
            閉じる
          </button>
          <div style={{ flex: 1 }} />
          {/* 「質問あり（保留）」按钮已移除（TW-024）：后端 decide 只支持 approve/reject，
              保留无对应处理，点了会谎报「保留しました」但申请实际仍 pending、学生零通知。
              退回/保留是 v1.1 功能（需后端 returned 状态 + 通知），实装后再恢复入口。 */}
          {/* 差戻 —— 中性/警示色（warn 系）。点击打开差戻理由输入弹窗（理由必填） */}
          <button
            onClick={() => {
              setReturnReason("");
              setReturnError(null);
              setReturnOpen(true);
            }}
            style={{
              padding: "10px 18px",
              background: "transparent",
              color: T.warn,
              border: `1px solid ${T.warnBorder}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            差戻
          </button>
          <button
            onClick={() => setConfirm({ action: "rejected", label: "却下" })}
            style={{
              padding: "10px 18px",
              background: "transparent",
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            却下
          </button>
          <button
            onClick={() => setConfirm({ action: "approved", label: "承認" })}
            style={{
              padding: "10px 20px",
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
            承認
          </button>
        </div>
      </div>

      {confirm && (
        <ConfirmModal
          title={`${applicantName} の${kindLabel}申請を${confirm.label}しますか？`}
          desc="承認・却下の結果は学生へメールで通知されます（入力したコメントも一緒に届きます）。"
          danger={confirm.action === "rejected"}
          confirmLabel={confirm.label}
          onCancel={() => setConfirm(null)}
          onConfirm={() => {
            onAction(confirm.action, comment);
            setConfirm(null);
          }}
        />
      )}

      {/* 差戻理由入力弹窗 —— 参照 ConfirmModal 样式，但带必填 textarea。
          理由必填（1〜1000 字），通过校验才调 onReturn。 */}
      {returnOpen && (
        <div
          onClick={() => setReturnOpen(false)}
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
              width: 480,
              background: T.surface,
              borderRadius: 14,
              boxShadow: T.shadowModal,
              padding: "24px 28px",
              fontFamily: T.font,
            }}
          >
            <div style={{ fontSize: 17, fontWeight: 700 }}>
              {applicantName} の{kindLabel}申請を差戻しますか？
            </div>
            <div
              style={{
                fontSize: 13,
                color: T.ink3,
                marginTop: 8,
                lineHeight: 1.6,
              }}
            >
              差戻すと申請は学生に返され、修正のうえ再提出できます。差戻理由は学生へメールで通知されます。
            </div>
            <label
              style={{
                display: "block",
                fontSize: 12,
                fontWeight: 600,
                color: T.ink2,
                margin: "16px 0 6px",
              }}
            >
              差戻理由（必須）
            </label>
            <textarea
              value={returnReason}
              onChange={(e) => {
                setReturnReason(e.target.value);
                if (returnError) setReturnError(null);
              }}
              placeholder="例：出発時刻と帰寮時刻に矛盾があります。再確認のうえ修正してください。"
              rows={3}
              autoFocus
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "8px 10px",
                border: `1px solid ${returnError ? T.danger : T.lineStrong}`,
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                resize: "vertical",
              }}
            />
            {returnError && (
              <div
                style={{
                  fontSize: 12,
                  color: T.danger,
                  marginTop: 6,
                }}
              >
                {returnError}
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
                onClick={() => setReturnOpen(false)}
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
                onClick={() => {
                  // 校验：理由必填、1〜1000 字（对齐后端约束）
                  const reason = returnReason.trim();
                  if (reason.length === 0) {
                    setReturnError("差戻理由を入力してください。");
                    return;
                  }
                  if (reason.length > 1000) {
                    setReturnError(
                      "差戻理由は 1000 字以内で入力してください。",
                    );
                    return;
                  }
                  onReturn(reason);
                  setReturnOpen(false);
                }}
                style={{
                  padding: "9px 18px",
                  background: T.warn,
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                差戻
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// DeadlineSection —— OutstayDetailModal 的私有子组件，只在外泊申请里显示提交期限。
// 用到的 outstayDeadline / parseJst / isLateSubmission / formatJstDeadline 从 ../utils import。
function DeadlineSection({ app }: { app: OutstayUiApp }) {
  const T = RYO;
  // 四个函数均为命名 import，恒可用——不再套旧 window 全局时代的 truthy 守卫
  const deadline = outstayDeadline(app.depart);
  const submittedDt = parseJst(app.submitted);
  const late = isLateSubmission(app.depart, app.submitted);
  // 仅两端都解析成功时才算差分文，避免 null→0→「0.0 時間」与「—」矛盾
  const hasDiff = deadline != null && submittedDt != null;
  const diffMs =
    deadline != null && submittedDt != null
      ? submittedDt.getTime() - deadline.getTime()
      : 0;
  const diffHours = Math.abs(diffMs) / 3600000;
  const diffText =
    diffHours >= 48
      ? `${Math.floor(diffHours / 24)} 日`
      : `${diffHours.toFixed(1)} 時間`;

  return (
    <div style={{ marginBottom: 18 }}>
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 700,
          marginBottom: 8,
          paddingBottom: 4,
          borderBottom: `1px solid ${T.line}`,
        }}
      >
        § 提出期限
      </div>
      <div
        style={{
          padding: 14,
          background: late ? T.dangerSoft : T.okSoft,
          border: `1px solid ${late ? T.dangerBorder : T.okBorder}`,
          borderRadius: 10,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            marginBottom: 10,
          }}
        >
          {late ? (
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                padding: "3px 10px",
                borderRadius: 4,
                background: T.danger,
                color: "#fff",
                letterSpacing: 0.5,
                whiteSpace: "nowrap",
              }}
            >
              ⚠ 期限後
            </span>
          ) : (
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                padding: "3px 10px",
                borderRadius: 4,
                background: T.ok,
                color: "#fff",
                letterSpacing: 0.5,
                whiteSpace: "nowrap",
              }}
            >
              ✓ 期限内
            </span>
          )}
          {hasDiff && (
            <span style={{ fontSize: 12, color: T.ink2 }}>
              {late
                ? `期限の ${diffText} 後に提出`
                : `期限の ${diffText} 前に提出`}
            </span>
          )}
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "140px 1fr",
            gap: "5px 10px",
            fontSize: 13,
          }}
        >
          <div style={{ color: T.ink3, fontSize: 12 }}>提出期限</div>
          <div style={{ fontFamily: T.mono, color: T.ink }}>
            {formatJstDeadline(deadline)}
          </div>
          <div style={{ color: T.ink3, fontSize: 12 }}>実際の提出時刻</div>
          <div style={{ fontFamily: T.mono, color: late ? T.danger : T.ink }}>
            {formatJstDeadline(submittedDt)}
          </div>
        </div>
        {late && (
          <div
            style={{
              marginTop: 12,
              padding: "10px 12px",
              background: T.surface,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
              fontSize: 12,
              lineHeight: 1.7,
              color: T.ink2,
            }}
          >
            <b style={{ color: T.danger }}>⚠ 面談必須</b> · 本来は iOS App
            から送信できない申請です（紙申請または管理者代理で登録されたもの）。
            <b>
              生徒本人を直接呼び、事情を確認した上で承認可否を判断してください。
            </b>
          </div>
        )}
        <div
          style={{
            marginTop: 10,
            fontSize: 11,
            color: T.ink3,
            lineHeight: 1.6,
          }}
        >
          提出期限 = 出発日の属する週の水曜日 23:59 または 出発予定時刻の 48
          時間前、いずれか早い方。
        </div>
      </div>
    </div>
  );
}
