import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { AuditLogEntry } from "../api/types";

// 操作履历审计（操作记录页）— 老师写操作全量自动记，本页只读展示。
// 后端按权限组 C_AUDIT_LOG 把关：非管理角色 GET 会 403（本页显示「権限がありません」）。
// action 是后端中间件存的 "METHOD 归一化路径"，下面 ACTION_LABELS 映射成日语。

const PAGE_SIZE = 50;

// "METHOD 归一化路径" → 日语操作名。未命中则回退显示原始 action。
const ACTION_LABELS: Record<string, string> = {
  "POST notifications/read-all": "通知を既読化",
  "POST discipline/manual": "減点を追加",
  "POST discipline/{id}/revoke": "減点を取消",
  "POST applications/{id}/approvals": "申請を承認・却下",
  "POST applications/by-teacher": "代理で出寮届を登録",
  "PUT applications/{id}": "出寮届を修正",
  "PATCH outings/{id}/confirm": "外出を確認",
  "POST announcements": "お知らせを投稿",
  "PATCH announcements/{id}": "お知らせを編集",
  "DELETE announcements/{id}": "お知らせを削除",
  "POST announcements/{id}/archive": "お知らせをアーカイブ",
  "POST cleaning": "清掃罰則を割当",
  "POST cleaning/{id}/inspect": "清掃を検査",
  "POST events": "行事を作成",
  "PATCH events/{id}": "行事を編集",
  "DELETE events/{id}": "行事を削除",
  "POST bus-routes": "バス路線を追加",
  "PATCH bus-routes/{id}": "バス路線を編集",
  "DELETE bus-routes/{id}": "バス路線を削除",
  "POST front-desk": "フロント預り物を登録",
  "POST front-desk/{id}/notify": "受取通知を送信",
  "POST front-desk/{id}/picked-up": "受取済みを記録",
  "POST teachers": "教員を追加",
  "DELETE teachers/{id}": "教員を削除",
  "POST incidents": "事案を記録",
  "PATCH incidents/{id}": "事案を編集",
  "DELETE incidents/{id}": "事案を削除",
  "POST guidance": "指導履歴を記録",
  "POST study/roster": "夜学習対象を追加",
  "POST study/checkins/bulk-finalize": "夜学習を一括終了",
  "POST rollcall/sessions/{id}/start": "点呼を開始",
  "POST rollcall/sessions/{id}/end": "点呼を終了",
  "PATCH rollcall/events/{id}": "点呼判定を変更",
  "POST students/renewal-start": "学年更新を開始",
  "PATCH reports/{id}": "通報を対応済みに変更",
  "DELETE songs/{id}": "リクエスト曲を削除",
  "DELETE lost-found/{id}": "落とし物投稿を削除",
};

function actionLabel(action: string): string {
  return ACTION_LABELS[action] || action;
}

// 后端发的 created_at 是带 +09:00 的 JST 墙钟字符串，直接截取展示（不经 Date 避免本地时区漂移）。
function fmtJa(iso: string): string {
  if (!iso) return "";
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/);
  return m ? `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}` : iso;
}

export function AuditLogPage({ authToken }: { authToken: string | null }) {
  const T = RYO;
  const [items, setItems] = React.useState<AuditLogEntry[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [forbidden, setForbidden] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [expanded, setExpanded] = React.useState<string | null>(null);
  // 翻页快照边界：首次加载时固定「現在」，后续翻页都带同一 until，
  // 这样翻页期间新增的操作记录不会让 offset 错位（漏/重）。
  const untilRef = React.useRef<string | null>(null);
  // web#21: 递增请求号 — token 变化 / 连点翻页时旧响应不得覆盖 state
  const requestIdRef = React.useRef(0);

  const load = React.useCallback(
    (offset: number) => {
      if (!authToken) return;
      if (offset === 0) untilRef.current = new Date().toISOString();
      const requestId = ++requestIdRef.current;
      setLoading(true);
      setError(null);
      api
        .getAuditLogs(
          { limit: PAGE_SIZE, offset, until: untilRef.current || undefined },
          authToken,
        )
        .then((res) => {
          // web#21: 仅最新请求写 state
          if (requestId !== requestIdRef.current) return;
          setItems((prev) =>
            offset === 0 ? res.items : [...prev, ...res.items],
          );
          setTotal(res.total);
        })
        .catch((e: any) => {
          if (requestId !== requestIdRef.current) return;
          if (e && e.status === 403) setForbidden(true);
          else setError("操作記録の取得に失敗しました。");
        })
        .finally(() => {
          if (requestId === requestIdRef.current) setLoading(false);
        });
    },
    [authToken],
  );

  React.useEffect(() => {
    load(0);
  }, [load]);

  if (forbidden) {
    return (
      <div style={{ padding: 32, color: T.ink2, fontFamily: T.font }}>
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>
          権限がありません
        </div>
        <div style={{ fontSize: 13, color: T.ink3 }}>
          操作記録は管理権限を持つ教員のみ閲覧できます。
        </div>
      </div>
    );
  }

  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "10px 14px",
    fontSize: 12,
    fontWeight: 700,
    color: T.ink2,
    borderBottom: `1px solid ${T.line}`,
    whiteSpace: "nowrap",
  };
  const td: React.CSSProperties = {
    padding: "10px 14px",
    fontSize: 13,
    color: T.ink,
    borderBottom: `1px solid ${T.line}`,
    verticalAlign: "top",
  };

  return (
    <div style={{ padding: 24, fontFamily: T.font }}>
      <div
        style={{ marginBottom: 4, fontSize: 19, fontWeight: 700, color: T.ink }}
      >
        操作履歴
      </div>
      <div style={{ marginBottom: 16, fontSize: 12.5, color: T.ink3 }}>
        教員の操作（登録・編集・削除・承認など）を日時付きで記録しています。全
        {total}件。
      </div>

      {error && (
        <div
          style={{
            padding: "10px 14px",
            marginBottom: 12,
            background: T.dangerSoft,
            color: T.danger,
            borderRadius: 8,
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={th}>日時</th>
              <th style={th}>操作者</th>
              <th style={th}>操作</th>
              <th style={th}>対象</th>
              <th style={{ ...th, textAlign: "right" }}>詳細</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && !loading && (
              <tr>
                <td
                  style={{ ...td, color: T.ink3, textAlign: "center" }}
                  colSpan={5}
                >
                  操作記録はまだありません。
                </td>
              </tr>
            )}
            {items.map((e) => {
              const isOpen = expanded === e.id;
              return (
                <React.Fragment key={e.id}>
                  <tr>
                    <td
                      style={{
                        ...td,
                        fontFamily: T.mono,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {fmtJa(e.created_at)}
                    </td>
                    <td style={{ ...td, whiteSpace: "nowrap" }}>
                      {e.actor_name ? `${e.actor_name} 先生` : "（削除済み）"}
                    </td>
                    <td style={td}>{actionLabel(e.action)}</td>
                    <td style={{ ...td, color: T.ink3, fontSize: 12 }}>
                      {e.target_type || "—"}
                    </td>
                    <td style={{ ...td, textAlign: "right" }}>
                      <button
                        onClick={() => setExpanded(isOpen ? null : e.id)}
                        style={{
                          border: `1px solid ${T.line}`,
                          background: isOpen ? T.cobaltSoft : "transparent",
                          color: isOpen ? T.cobaltDeep : T.ink3,
                          borderRadius: 6,
                          padding: "3px 9px",
                          fontSize: 11,
                          fontFamily: "inherit",
                          cursor: "pointer",
                        }}
                      >
                        {isOpen ? "閉じる" : "詳細"}
                      </button>
                    </td>
                  </tr>
                  {isOpen && (
                    <tr>
                      <td
                        style={{ ...td, background: T.surfaceAlt }}
                        colSpan={5}
                      >
                        <pre
                          style={{
                            margin: 0,
                            fontFamily: T.mono,
                            fontSize: 12,
                            color: T.ink2,
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-all",
                          }}
                        >
                          {JSON.stringify(e.payload ?? {}, null, 2)}
                          {e.ip_address ? `\nIP: ${e.ip_address}` : ""}
                        </pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 14, textAlign: "center" }}>
        {loading && (
          <span style={{ fontSize: 13, color: T.ink3 }}>読み込み中…</span>
        )}
        {!loading && items.length < total && (
          <button
            onClick={() => load(items.length)}
            style={{
              border: `1px solid ${T.lineStrong}`,
              background: T.surface,
              color: T.ink2,
              borderRadius: 8,
              padding: "8px 18px",
              fontSize: 13,
              fontFamily: "inherit",
              cursor: "pointer",
            }}
          >
            もっと見る（残り{total - items.length}件）
          </button>
        )}
      </div>
    </div>
  );
}
