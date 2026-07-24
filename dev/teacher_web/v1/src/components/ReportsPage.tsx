import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { ContentReportOut } from "../api/types";

// 投稿通報一覧（App Store 审核指南 1.2 UGC 治理 — itsuki 2026-07-20 拍板 A 方案）。
// 学生在 app 里通報的互见投稿（「リクエスト曲」/「お知らせ返信」/「落とし物」）在这里集中处理：
// 「投稿を削除」= 删投稿 + 自动标对应通報为处理完；「対応済みにする」= 判定无问题只标处理完。

const TYPE_LABELS: Record<ContentReportOut["content_type"], string> = {
  song: "リクエスト曲",
  announcement_reply: "お知らせ返信",
  lost_found: "落とし物",
};

// 后端 created_at 是带 +09:00 的 JST 墙钟字符串，直接截取展示（照 AuditLogPage 做法）。
function fmtJa(iso: string): string {
  if (!iso) return "";
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
  return m ? `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}` : iso;
}

export function ReportsPage({ authToken }: { authToken: string | null }) {
  const T = RYO;
  const [items, setItems] = React.useState<ContentReportOut[]>([]);
  const [statusFilter, setStatusFilter] = React.useState<
    "open" | "handled" | "all"
  >("open");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [busyId, setBusyId] = React.useState<string | null>(null);
  // 递增请求号 — 快速切换过滤器时旧响应不得覆盖新列表（照 AuditLogPage requestIdRef 做法）
  const requestIdRef = React.useRef(0);

  const load = React.useCallback(() => {
    if (!authToken) return;
    const requestId = ++requestIdRef.current;
    setLoading(true);
    setError(null);
    api
      .listContentReports(
        statusFilter === "all" ? null : statusFilter,
        authToken,
      )
      .then((res) => {
        // 仅最新请求写 state — 迟到的旧过滤响应丢弃
        if (requestId !== requestIdRef.current) return;
        setItems(res);
      })
      .catch(() => {
        if (requestId !== requestIdRef.current) return;
        setError("通報一覧の取得に失敗しました。");
      })
      .finally(() => {
        if (requestId === requestIdRef.current) setLoading(false);
      });
  }, [authToken, statusFilter]);

  React.useEffect(() => {
    load();
  }, [load]);

  // 「対応済みにする」— 只标通報处理完，不动投稿本体。
  const markHandled = (r: ContentReportOut) => {
    if (!authToken) return;
    setBusyId(r.id);
    api
      .handleContentReport(r.id, authToken)
      .then(() => load())
      .catch(() => setError("操作に失敗しました。"))
      .finally(() => setBusyId(null));
  };

  // 「投稿を削除」— 删投稿本体（学生 app 一览立即消失），随后自动标通報处理完。
  // 失败时不刷新一覧（load 开头会清 error，刷新会把错误红字抹掉）。
  const deleteContent = async (r: ContentReportOut) => {
    if (!authToken) return;
    if (
      !confirm("この投稿を削除しますか？寮生のアプリからも非表示になります。")
    )
      return;
    setBusyId(r.id);
    try {
      try {
        if (r.content_type === "song") {
          await api.deleteSongRequest(r.content_id, authToken);
        } else if (r.content_type === "lost_found") {
          await api.deleteLostFoundPost(r.content_id, authToken);
        } else if (r.content_parent_id) {
          await api.deleteAnnouncementReply(
            r.content_parent_id,
            r.content_id,
            authToken,
          );
        } else {
          throw new Error("parent missing");
        }
      } catch (e: any) {
        // 投稿可能已被删（404）→ 不拦流程，照样把通報标处理完
        if (!e || e.status !== 404) throw e;
      }
      try {
        await api.handleContentReport(r.id, authToken);
      } catch (e: any) {
        // 通報已被别的老师标过（409）不算失败
        if (!e || e.status !== 409) throw e;
      }
      load();
    } catch {
      setError("削除に失敗しました。");
    } finally {
      setBusyId(null);
    }
  };

  const filterBtn = (key: "open" | "handled" | "all", label: string) => (
    <button
      key={key}
      onClick={() => setStatusFilter(key)}
      style={{
        padding: "6px 14px",
        borderRadius: 8,
        border: `1px solid ${statusFilter === key ? T.cobalt : T.line}`,
        background: statusFilter === key ? T.cobaltSoft : "transparent",
        color: statusFilter === key ? T.cobalt : T.ink2,
        fontSize: 13,
        fontWeight: 600,
        cursor: "pointer",
        fontFamily: T.font,
      }}
    >
      {label}
    </button>
  );

  return (
    <div style={{ padding: "24px 28px", fontFamily: T.font, color: T.ink }}>
      <div style={{ fontSize: 19, fontWeight: 800, marginBottom: 4 }}>
        投稿の通報
      </div>
      <div style={{ fontSize: 12.5, color: T.ink3, marginBottom: 16 }}>
        寮生から通報された投稿（リクエスト曲・お知らせ返信・落とし物）を確認し、削除または対応済みにします。
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {filterBtn("open", "未対応")}
        {filterBtn("handled", "対応済み")}
        {filterBtn("all", "すべて")}
      </div>

      {error && (
        <div style={{ color: T.danger, fontSize: 13, marginBottom: 12 }}>
          {error}
        </div>
      )}
      {loading && (
        <div style={{ color: T.ink3, fontSize: 13, marginBottom: 12 }}>
          読み込み中...
        </div>
      )}
      {!loading && items.length === 0 && (
        <div style={{ color: T.ink3, fontSize: 14, padding: "28px 0" }}>
          {statusFilter === "open"
            ? "未対応の通報はありません。"
            : "通報はありません。"}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {items.map((r) => (
          <div
            key={r.id}
            style={{
              border: `1px solid ${T.line}`,
              borderRadius: 12,
              padding: "14px 16px",
              background: T.surface,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 6,
              }}
            >
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: 999,
                  background: T.cobaltSoft,
                  color: T.cobalt,
                }}
              >
                {TYPE_LABELS[r.content_type]}
              </span>
              <span style={{ fontSize: 12, color: T.ink3 }}>
                {fmtJa(r.created_at)}
              </span>
              {r.status === "handled" && (
                <span style={{ fontSize: 11, fontWeight: 700, color: T.ink3 }}>
                  対応済み
                </span>
              )}
            </div>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
              {r.content_preview ?? "（投稿は既に削除されています）"}
            </div>
            {r.reason && (
              <div style={{ fontSize: 12.5, color: T.ink2, marginBottom: 8 }}>
                通報理由：{r.reason}
              </div>
            )}
            {r.status === "open" && (
              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <button
                  onClick={() => deleteContent(r)}
                  disabled={busyId === r.id}
                  style={{
                    padding: "6px 14px",
                    borderRadius: 8,
                    border: `1px solid ${T.danger}`,
                    background: "transparent",
                    color: T.danger,
                    fontSize: 12.5,
                    fontWeight: 700,
                    cursor: "pointer",
                    fontFamily: T.font,
                  }}
                >
                  投稿を削除
                </button>
                <button
                  onClick={() => markHandled(r)}
                  disabled={busyId === r.id}
                  style={{
                    padding: "6px 14px",
                    borderRadius: 8,
                    border: `1px solid ${T.line}`,
                    background: "transparent",
                    color: T.ink2,
                    fontSize: 12.5,
                    fontWeight: 600,
                    cursor: "pointer",
                    fontFamily: T.font,
                  }}
                >
                  問題なし（対応済みにする）
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
