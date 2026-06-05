import React from "react";
import { RYO } from "../theme";
import type { RyoTokens } from "../theme";
import { api } from "../api/client";
import { ModalShell, ModalField, ModalFooter } from "./shared";
import type {
  CleaningItem,
  CleaningCreateIn,
  CleaningInspectIn,
} from "../api/types";

// 源 index.html 20944-21367（pages-records-search-etc 块）。界面原样搬，仅
// window.RYO→RYO / window.tomoshibiApi→api / window.ModalShell|ModalField|ModalFooter→从 ./shared import /
// window.modalInputStyle→本文件本地副本 modalInputStyle / 日语注释翻成中文。
// /cleaning — 清扫确认：当天清扫分配一览 + 割り当て modal + 却下理由 modal。

// 清扫输入框样式（源 front-desk 块 inputStyle / window.modalInputStyle 的本地副本）
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

export function CleaningPage({ authToken }: { authToken: string }) {
  const T = RYO;
  const today = new Date();
  const isoDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  const [items, setItems] = React.useState<CleaningItem[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [composing, setComposing] = React.useState(false);
  // 却下 modal: 选中的清扫记录
  const [rejectTarget, setRejectTarget] = React.useState<CleaningItem | null>(
    null,
  );

  const loadItems = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    setLoading(true);
    setFetchError(null);
    api
      .listCleaning(authToken, isoDate)
      .then((data) => {
        if (!cancelled) setItems(Array.isArray(data) ? data : []);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[CleaningPage] listCleaning 失败", e);
        setFetchError(e.message || "データ取得に失敗しました");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken, isoDate]);

  React.useEffect(() => {
    return loadItems();
  }, [loadItems]);

  const handleInspect = (
    id: string,
    result: "passed" | "failed",
    failure_reason?: string,
  ) => {
    const body: CleaningInspectIn = { result };
    if (result === "failed" && failure_reason)
      body.failure_reason = failure_reason;
    api
      .inspectCleaning(id, body, authToken)
      .then(() => {
        setRejectTarget(null);
        loadItems();
      })
      .catch((e) =>
        alert("審査に失敗しました：" + (e.message || JSON.stringify(e))),
      );
  };

  const handleCreate = (body: CleaningCreateIn) => {
    api
      .createCleaning(body, authToken)
      .then(() => {
        setComposing(false);
        loadItems();
      })
      .catch((e) =>
        alert("登録に失敗しました：" + (e.message || JSON.stringify(e))),
      );
  };

  const statusColors: Record<string, [string, string, string, string]> = {
    assigned: [T.warn, T.warnSoft, T.warnBorder, "未審査"],
    done: [T.cobalt, "#e8f0ff", "#b3c9f7", "完了報告済"],
    passed: [T.ok, T.okSoft, T.okBorder, "承認済"],
    failed: [T.danger, "#fff0f0", "#f5c6cb", "却下"],
    skipped: [T.ink3, T.surfaceAlt, T.line, "免除"],
  };

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 6,
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>清掃確認</h1>
        <button
          onClick={() => setComposing(true)}
          style={{
            marginLeft: "auto",
            padding: "8px 16px",
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
          ＋ 清掃を割り当て
        </button>
      </div>
      <div style={{ color: T.ink3, fontSize: 13, marginBottom: 20 }}>
        {isoDate} の清掃割り当て一覧
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
            onClick={loadItems}
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

      {loading && (
        <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
          読み込み中…
        </div>
      )}

      {!loading && !fetchError && items.length === 0 && (
        <div
          style={{
            padding: 36,
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            background: T.surface,
            border: `1px dashed ${T.lineStrong}`,
            borderRadius: 10,
          }}
        >
          まだデータがありません
        </div>
      )}

      {!loading && items.length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 14,
          }}
        >
          {items.map((item) => {
            const [col, bg, bd, lbl] =
              statusColors[item.status] || statusColors.assigned;
            const canInspect =
              item.status === "assigned" || item.status === "done";
            return (
              <div
                key={item.id}
                style={{
                  background: T.surface,
                  border: `1px solid ${T.line}`,
                  borderRadius: 12,
                  padding: 14,
                  boxShadow: T.shadow1,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 10,
                  }}
                >
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 4,
                      background: bg,
                      color: col,
                      border: `1px solid ${bd}`,
                      letterSpacing: 0.5,
                    }}
                  >
                    {lbl}
                  </span>
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 700,
                      color: T.cobaltDeep,
                      marginLeft: "auto",
                    }}
                  >
                    {item.area}
                  </span>
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    fontFamily: T.mono,
                    marginBottom: 4,
                  }}
                >
                  学生ID：{String(item.student_id).slice(0, 8)}…
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    fontFamily: T.mono,
                    marginBottom: 10,
                  }}
                >
                  担当日：{item.scheduled_date}
                </div>
                {item.failure_reason && (
                  <div
                    style={{
                      fontSize: 11,
                      color: T.danger,
                      marginBottom: 8,
                    }}
                  >
                    却下理由：{item.failure_reason}
                  </div>
                )}
                {canInspect && (
                  <div style={{ display: "flex", gap: 6 }}>
                    <button
                      onClick={() => handleInspect(item.id, "passed")}
                      style={{
                        flex: 1,
                        padding: "7px",
                        background: T.cobalt,
                        color: "#fff",
                        border: "none",
                        borderRadius: 6,
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: "pointer",
                        fontFamily: "inherit",
                      }}
                    >
                      承認
                    </button>
                    <button
                      onClick={() => setRejectTarget(item)}
                      style={{
                        flex: 1,
                        padding: "7px",
                        background: "transparent",
                        color: T.danger,
                        border: `1px solid ${T.dangerBorder}`,
                        borderRadius: 6,
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: "pointer",
                        fontFamily: "inherit",
                      }}
                    >
                      却下
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* 清扫分配 modal */}
      {composing && (
        <CleaningCreateModal
          T={T}
          isoDate={isoDate}
          onClose={() => setComposing(false)}
          onSubmit={handleCreate}
        />
      )}

      {/* 却下理由输入 modal */}
      {rejectTarget && (
        <CleaningRejectModal
          T={T}
          item={rejectTarget}
          onClose={() => setRejectTarget(null)}
          onSubmit={(reason) =>
            handleInspect(rejectTarget.id, "failed", reason)
          }
        />
      )}
    </div>
  );
}

// 清扫分配作成 modal
// body → { student_id, area, scheduled_date }
const CLEANING_AREAS: CleaningCreateIn["area"][] = [
  "浴室",
  "廊下",
  "トイレ",
  "共用キッチン",
  "階段",
  "玄関",
  "その他",
];

function CleaningCreateModal({
  T,
  isoDate,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  isoDate: string;
  onClose: () => void;
  onSubmit: (body: CleaningCreateIn) => void;
}) {
  const [studentId, setStudentId] = React.useState("");
  const [area, setArea] = React.useState<CleaningCreateIn["area"]>(
    CLEANING_AREAS[0],
  );
  const [date, setDate] = React.useState(isoDate);
  const disabled = !studentId.trim();
  return (
    <ModalShell T={T} title="清掃を割り当て" onClose={onClose}>
      <ModalField T={T} label="学生ID">
        <input
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="担当エリア">
        <select
          value={area}
          onChange={(e) => setArea(e.target.value as CleaningCreateIn["area"])}
          style={modalInputStyle(T)}
        >
          {CLEANING_AREAS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </ModalField>
      <ModalField T={T} label="担当日">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={() =>
          !disabled &&
          onSubmit({
            student_id: studentId.trim(),
            area,
            scheduled_date: date,
          })
        }
        disabled={disabled}
      />
    </ModalShell>
  );
}

// 却下理由输入 modal
function CleaningRejectModal({
  T,
  item,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  item: CleaningItem;
  onClose: () => void;
  onSubmit: (reason: string) => void;
}) {
  const [reason, setReason] = React.useState("");
  const disabled = !reason.trim();
  return (
    <ModalShell T={T} title={`却下：${item.area}`} onClose={onClose}>
      <ModalField T={T} label="却下理由（必須）">
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={3}
          placeholder="例：清掃が不十分でした"
          style={{
            ...modalInputStyle(T),
            resize: "vertical",
            lineHeight: 1.5,
          }}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={() => !disabled && onSubmit(reason.trim())}
        disabled={disabled}
      />
    </ModalShell>
  );
}
