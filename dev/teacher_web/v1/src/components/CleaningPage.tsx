import React from "react";
import { RYO } from "../theme";
import type { RyoTokens } from "../theme";
import { api } from "../api/client";
import {
  ModalShell,
  ModalField,
  ModalFooter,
  StudentPicker,
  type PickerStudent,
} from "./shared";
import type {
  CleaningItem,
  CleaningCreateIn,
  CleaningInspectIn,
} from "../api/types";

// /cleaning — 清扫确认：未完了の清掃割り当て一覧 + 割り当て modal + 却下理由 modal。
// 旧版（71d9200）原样恢复，套 3 处改动：
//   改动1：担当日（date）→ 日時（datetime-local），提交转 ISO8601。
//   改动2：担当エリア 7 选 1 枚举 → 自由文本 input。
//   改动3：学生 ID 裸输入 → StudentPicker 单选（searchDemeritStudents）。
// list 口径：后端不带参数，直接拉所有未审核（assigned/done）的安排，按 scheduled_at 升序。

// 清扫输入框样式（源 front-desk 块 inputStyle 的本地副本）
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

// scheduled_at（ISO8601）→「M月D日 H時mm分」。后端带时区，new Date 按本地(JST)显示。
function fmtCleaningWhen(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return `${d.getMonth() + 1}月${d.getDate()}日 ${d.getHours()}時${String(d.getMinutes()).padStart(2, "0")}分`;
}

export function CleaningPage({ authToken }: { authToken: string }) {
  const T = RYO;

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
      .listCleaning(authToken)
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
  }, [authToken]);

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
        未完了の清掃割り当て一覧
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
                  日時：{fmtCleaningWhen(item.scheduled_at)}
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
          authToken={authToken}
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

// datetime-local 默认值：当前时刻 + 1 小时，截到分钟，格式 YYYY-MM-DDTHH:mm
function defaultDatetimeLocal(): string {
  const d = new Date(Date.now() + 60 * 60 * 1000);
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}

// 清扫分配作成 modal —— body → { student_id, area, scheduled_at }
function CleaningCreateModal({
  T,
  authToken,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  authToken: string;
  onClose: () => void;
  onSubmit: (body: CleaningCreateIn) => void;
}) {
  const [selected, setSelected] = React.useState<PickerStudent[]>([]);
  const [area, setArea] = React.useState(""); // 改动2：自由文本，不再是枚举
  // 改动1：日期+时间。datetime-local 的默认值给「现在的下一个整点」做提示
  const [when, setWhen] = React.useState(() => defaultDatetimeLocal());
  const student = selected[0] || null;
  // 不能排到已过去时间（前端先拦一道，后端再兜底）
  const isPast = !!when && new Date(when).getTime() < Date.now();
  const disabled = !student || !area.trim() || !when || isPast;

  return (
    <ModalShell T={T} title="清掃を割り当て" onClose={onClose}>
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
      <ModalField T={T} label="担当エリア（自由入力）">
        <input
          value={area}
          onChange={(e) => setArea(e.target.value)}
          placeholder="例：1階トイレ / 共用キッチン / 玄関前"
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="日時">
        <input
          type="datetime-local"
          value={when}
          onChange={(e) => setWhen(e.target.value)}
          style={modalInputStyle(T)}
        />
        {isPast && (
          <div style={{ fontSize: 11, color: T.danger, marginTop: 6 }}>
            過去の日時は指定できません
          </div>
        )}
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={() =>
          !disabled &&
          onSubmit({
            student_id: student!.id,
            area: area.trim(),
            // datetime-local 是「无时区本地时刻」字符串（YYYY-MM-DDTHH:mm）。
            // new Date(localStr) 按浏览器本地时区解析 → toISOString() 转 UTC 的 ISO8601。
            // 老师机器时区 = JST，后端按带时区 datetime 收，对齐 scheduled_at。
            scheduled_at: new Date(when).toISOString(),
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
