import React from "react";
import { RYO, S } from "../theme";
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
  TeacherProfile,
} from "../api/types";
import { canManage, C_DEMERIT } from "../api/permissions";

// /cleaning — 清扫确认：未完了の清掃割り当て一覧 + 割り当て modal + 却下理由 modal。
// 旧版（71d9200）原样恢复，套 3 处改动：
//   改动1：担当日（date）→ 日時（datetime-local），提交转 ISO8601。
//   改动2：担当エリア 7 选 1 枚举 → 自由文本 input。
//   改动3：学生 ID 裸输入 → StudentPicker 单选（searchDemeritStudents）。
// list 口径：后端不带参数，直接拉所有未审核（assigned/done）的安排，按 scheduled_at 升序。

// 清扫输入框样式 — 套 S.input，保留原 padding / 边框强度
function modalInputStyle(T: RyoTokens): React.CSSProperties {
  return {
    ...S.input,
    width: "100%",
    padding: "9px 12px",
    border: `1px solid ${T.lineStrong}`,
    boxSizing: "border-box",
  };
}

// scheduled_at（ISO8601）→「M月D日 H時mm分」，显示锁 JST、不依赖浏览器时区（全链路 JST 契约）。
function fmtCleaningWhen(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const parts = new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(d);
  const g = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  return `${g("month")}月${g("day")}日 ${g("hour")}時${g("minute")}分`;
}

export function CleaningPage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile | null;
  authToken: string;
}) {
  const T = RYO;
  // 权限：清扫罚则归 C_DEMERIT 簇，「申請承認専用」组只有 VIEW，后端清扫写端点均
  // require_permission(C_DEMERIT, MANAGE)。无 MANAGE 时隐藏分配/承认/却下写按钮，
  // 避免点了必被 403（与 AccountsPage/InfoPage 同款门控）。
  const canWrite = !!teacher && canManage(teacher, C_DEMERIT);

  const [items, setItems] = React.useState<CleaningItem[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [composing, setComposing] = React.useState(false);
  // 却下 modal: 选中的清扫记录
  const [rejectTarget, setRejectTarget] = React.useState<CleaningItem | null>(
    null,
  );
  // web#63：请求号守卫 — 直接调用 loadItems 时也能作废旧请求，卸载时 bump 防 setState
  const loadGenRef = React.useRef(0);

  const loadItems = React.useCallback(() => {
    if (!authToken) return;
    const gen = ++loadGenRef.current;
    setLoading(true);
    setFetchError(null);
    api
      .listCleaning(authToken)
      .then((data) => {
        if (gen !== loadGenRef.current) return;
        setItems(Array.isArray(data) ? data : []);
      })
      .catch((e) => {
        if (gen !== loadGenRef.current) return;
        console.warn("[CleaningPage] listCleaning 失败", e);
        setFetchError(e.message || "データ取得に失敗しました");
      })
      .finally(() => {
        if (gen === loadGenRef.current) setLoading(false);
      });
  }, [authToken]);

  React.useEffect(() => {
    loadItems();
    return () => {
      loadGenRef.current++;
    };
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
    done: [T.cobalt, T.cobaltSoft, T.infoBorder, "完了報告済"],
    passed: [T.ok, T.okSoft, T.okBorder, "承認済"],
    failed: [T.danger, T.dangerSoft, T.dangerBorder, "却下"],
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
        {canWrite && (
          <button
            onClick={() => setComposing(true)}
            className="t-btn"
            style={{
              ...S.btnPrimary,
              marginLeft: "auto",
              padding: "8px 16px",
            }}
          >
            ＋ 清掃を割り当て
          </button>
        )}
      </div>
      <div style={{ color: T.ink3, fontSize: 13, marginBottom: 20 }}>
        未完了の清掃割り当て一覧
      </div>

      {/* 错误横幅 */}
      {fetchError && (
        <div
          style={{
            padding: "10px 16px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
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
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "4px 12px",
              fontSize: 12,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
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
            borderRadius: 12,
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
          {items.map((item, i) => {
            const [col, bg, bd, lbl] =
              statusColors[item.status] || statusColors.assigned;
            const canInspect =
              item.status === "assigned" || item.status === "done";
            return (
              <div
                key={item.id}
                className="t-fade-up"
                style={{
                  ...S.card,
                  padding: 14,
                  ...(i < 12 ? { animationDelay: `${i * 40}ms` } : null),
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
                      ...S.pill,
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "2px 8px",
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
                {/* 主信息 = 姓名（房号）— 原来只显 UUID 前 8 位，老师审核时认不出
                    对象是谁（审查 web#3）。后端旧数据无摘要时退回显示短 ID */}
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: T.ink,
                    marginBottom: 4,
                  }}
                >
                  {item.student_name
                    ? `${item.student_name}（${item.room_no || "部屋不明"}）`
                    : `寮生ID：${String(item.student_id).slice(0, 8)}…`}
                </div>
                {item.student_no && (
                  <div
                    style={{
                      fontSize: 11,
                      color: T.ink3,
                      fontFamily: T.mono,
                      marginBottom: 4,
                    }}
                  >
                    学籍番号：{item.student_no}
                  </div>
                )}
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
                {canWrite && canInspect && (
                  <div style={{ display: "flex", gap: 6 }}>
                    <button
                      onClick={() => handleInspect(item.id, "passed")}
                      className="t-btn"
                      style={{
                        ...S.btnPrimary,
                        flex: 1,
                        padding: "7px",
                        fontSize: 12,
                        borderRadius: 8,
                      }}
                    >
                      承認
                    </button>
                    <button
                      onClick={() => setRejectTarget(item)}
                      className="t-btn"
                      style={{
                        ...S.btnGhost,
                        flex: 1,
                        padding: "7px",
                        color: T.danger,
                        border: `1px solid ${T.dangerBorder}`,
                        fontSize: 12,
                        borderRadius: 8,
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

// datetime-local 默认值：当前时刻 + 1 小时，按 JST 生成（YYYY-MM-DDTHH:mm，不依赖浏览器时区）。
// sv-SE 输出 ISO 风格「YYYY-MM-DD HH:mm:ss」(24 时制 00-23)，取前 16 位、空格换 T。
function defaultDatetimeLocal(): string {
  const d = new Date(Date.now() + 60 * 60 * 1000);
  return d
    .toLocaleString("sv-SE", { timeZone: "Asia/Tokyo" })
    .slice(0, 16)
    .replace(" ", "T");
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
  // 改动1：日期+时间。datetime-local 的默认值给「当前时刻 + 1 小时」做提示
  const [when, setWhen] = React.useState(() => defaultDatetimeLocal());
  const student = selected[0] || null;
  // 不能排到已过去时间（前端先拦一道，后端再兜底）。when 是 datetime-local 无时区串，
  // 显式当 JST 解析（+09:00）再比，不依赖浏览器时区（与提交的 scheduled_at 口径一致）。
  const isPast = !!when && new Date(`${when}:00+09:00`).getTime() < Date.now();
  const disabled = !student || !area.trim() || !when || isPast;

  return (
    <ModalShell T={T} title="清掃を割り当て" onClose={onClose}>
      <ModalField T={T} label="寮生（必須）">
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
      <ModalField T={T} label="担当エリア（自由入力・32文字以内）">
        <input
          value={area}
          onChange={(e) => setArea(e.target.value)}
          maxLength={32}
          placeholder="例：1階トイレ / 共用キッチン / 玄関前"
          className="t-input"
          style={modalInputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="日時">
        <input
          type="datetime-local"
          value={when}
          onChange={(e) => setWhen(e.target.value)}
          className="t-input"
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
            // datetime-local 是「无时区本地时刻」串（YYYY-MM-DDTHH:mm）。显式当 JST（+09:00）
            // 解析 → toISOString() 转 UTC 的 ISO8601，不依赖浏览器时区，后端按带时区 datetime 收。
            scheduled_at: new Date(`${when}:00+09:00`).toISOString(),
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
          className="t-input"
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
        submitLabel="却下"
      />
    </ModalShell>
  );
}
