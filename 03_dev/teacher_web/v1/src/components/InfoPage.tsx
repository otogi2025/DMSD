import React from "react";
import { RYO } from "../theme";
import type { RyoTokens } from "../theme";
import { api } from "../api/client";
import { ModalShell, ModalField, ModalFooter } from "./shared";
import type {
  TeacherProfile,
  AnnouncementBrief,
  AnnouncementDetail,
  AnnouncementScope,
  EventItem,
  BusRoute,
} from "../api/types";

// 源 index.html 21369-24084（pages-records-search-etc 块）。界面原样搬：
// JSX 结构 + 内联 style 一字不改，仅作用域引用方式改写
// （window.RYO→RYO / window.tomoshibiApi→api / window.ModalShell 等→shared / window.modalInputStyle→本地副本）。
// 本文件含主组件 InfoPage + 9 个私有子组件（公告 / 行事日历 / 巴士），其余主组件不在此。

// 输入框样式（源 front-desk 块 inputStyle / window.modalInputStyle 的本地副本）。
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

// 公告一覧の UI 内部形式（adaptList の戻り値）。
interface NoticeRow {
  date: string;
  title: string;
  body: string;
  author: string;
  author_id: string;
  scope: AnnouncementScope;
  reply_count: number;
  _id: string;
}

// 行事一覧の UI 内部形式（adapt の戻り値）。
interface EventRow {
  _id: string;
  date: string;
  time: string | null;
  title: string;
  category: string;
  description: string;
  start_at: string | null;
  end_at: string | null;
}

// 行事 modal の編集対象 / 提交 payload。
interface EventFormData {
  title: string;
  category: string;
  event_date: string;
  start_at: string | null;
  end_at: string | null;
  description: string | null;
}

// 巴士 modal の提交 payload。
interface BusRouteFormData {
  kind: string;
  name: string;
  direction: string;
  schedule_at: string | null;
  arrival_at: string | null;
  visible_to: string;
  note: string | null;
}

// 巴士告知ボードの行事項目（バックエンド非依存のローカル形式）。
interface BusEventItem {
  time: string;
  action: string;
  location?: string;
  memo?: string;
}

interface BusEventData {
  date: string;
  name: string;
  audience?: string;
  items: BusEventItem[];
}

// 巴士告知ボードの投稿（バックエンド非依存のローカル形式）。
interface BusPost {
  title: string;
  category: string;
  posted_on: string;
  posted_by: string;
  effective_from: string;
  effective_until: string | null;
  body: string;
  pinned: boolean;
  events: BusEventData[];
}

export function InfoPage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("notice");
  // 真データのみ — 初期値は空配列（NOTICE_POSTS 假数据を初期値にしない）
  const [posts, setPosts] = React.useState<NoticeRow[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [composing, setComposing] = React.useState(false);
  // 詳細展開中の公告 id (null = 全部閉じ)
  const [openId, setOpenId] = React.useState<string | null>(null);
  // 詳細キャッシュ: { [id]: AnnouncementDetail }
  const [detailCache, setDetailCache] = React.useState<
    Record<string, AnnouncementDetail>
  >({});
  // 返信入力: { [id]: string }
  const [replyInput, setReplyInput] = React.useState<Record<string, string>>(
    {},
  );
  // 編集対象: null | { id, title, body, scope }
  const [editTarget, setEditTarget] = React.useState<{
    id: string;
    title: string;
    body: string;
    scope: AnnouncementScope;
  } | null>(null);

  // ── 一覧 adapt ──
  const adaptList = (data: { items?: AnnouncementBrief[] }): NoticeRow[] => {
    const items = (data && data.items) || [];
    return items.map((a) => {
      const d = new Date(a.created_at);
      return {
        date: `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`,
        title: a.title,
        body: a.body_summary,
        author: a.author_teacher_name,
        author_id: a.author_teacher_id,
        scope: a.scope,
        reply_count: a.reply_count || 0,
        _id: a.id,
      };
    });
  };

  // ── 一覧 fetch ──
  const loadList = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    setLoading(true);
    setFetchError(null);
    api
      .listAnnouncements(authToken)
      .then((data) => {
        if (cancelled) return;
        setPosts(adaptList(data));
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[InfoPage] listAnnouncements 失败", e);
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
    return loadList();
  }, [loadList]);

  // ── 詳細 fetch (展開時) ──
  const openDetail = (id: string) => {
    setOpenId((prev) => (prev === id ? null : id));
    if (!detailCache[id] && authToken) {
      api
        .getAnnouncement(id, authToken)
        .then((det) => setDetailCache((c) => ({ ...c, [id]: det })))
        .catch((e) => console.warn("[InfoPage] getAnnouncement 失败", e));
    }
  };

  // ── 新規投稿 ──
  const handlePost = async (input: {
    title: string;
    body: string;
    scope: AnnouncementScope;
  }) => {
    if (!authToken) throw new Error("未登录");
    await api.createAnnouncement(
      { title: input.title, body: input.body, scope: input.scope },
      authToken,
    );
    const data = await api.listAnnouncements(authToken);
    setPosts(adaptList(data));
    setComposing(false);
  };

  // ── 編集保存 ──
  const handleUpdate = async (
    id: string,
    input: { title: string; body: string; scope: AnnouncementScope },
  ) => {
    if (!authToken) return;
    await api.updateAnnouncement(
      id,
      {
        title: input.title,
        body: input.body,
        scope: input.scope,
      },
      authToken,
    );
    // 詳細キャッシュ削除 + 一覧再取得
    setDetailCache((c) => {
      const n = { ...c };
      delete n[id];
      return n;
    });
    setEditTarget(null);
    loadList();
  };

  // ── 削除 ──
  const handleDelete = async (id: string) => {
    if (!authToken) return;
    if (!confirm("この公告を削除しますか？")) return;
    try {
      await api.deleteAnnouncement(id, authToken);
      setPosts((prev) => prev.filter((p) => p._id !== id));
      if (openId === id) setOpenId(null);
    } catch (e) {
      alert(
        "削除に失敗しました：" + ((e as Error).message || JSON.stringify(e)),
      );
    }
  };

  // ── 返信投稿 ──
  const handleReply = async (announcementId: string) => {
    const body = (replyInput[announcementId] || "").trim();
    if (!body || !authToken) return;
    try {
      await api.postAnnouncementReply(announcementId, { body }, authToken);
      setReplyInput((r) => ({ ...r, [announcementId]: "" }));
      // 詳細キャッシュ更新
      const det = await api.getAnnouncement(announcementId, authToken);
      setDetailCache((c) => ({ ...c, [announcementId]: det }));
    } catch (e) {
      alert(
        "返信に失敗しました：" + ((e as Error).message || JSON.stringify(e)),
      );
    }
  };

  // ── 返信削除 ──
  const handleDeleteReply = async (announcementId: string, replyId: string) => {
    if (!authToken) return;
    try {
      await api.deleteAnnouncementReply(announcementId, replyId, authToken);
      const det = await api.getAnnouncement(announcementId, authToken);
      setDetailCache((c) => ({ ...c, [announcementId]: det }));
    } catch (e) {
      alert(
        "返信の削除に失敗しました：" +
          ((e as Error).message || JSON.stringify(e)),
      );
    }
  };

  const scopeLabel: Record<string, string> = {
    all: "全寮生",
    male: "男子寮",
    female: "女子寮",
  };

  return (
    <div style={{ padding: "28px 32px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>お知らせ・バス</h1>
        {tab === "notice" && (
          <button
            onClick={() => setComposing(true)}
            style={{
              padding: "8px 16px",
              background: T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: T.shadow1,
            }}
          >
            ＋ 新規お知らせ投稿
          </button>
        )}
      </div>
      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          margin: "18px 0",
        }}
      >
        {[
          ["notice", "お知らせ"],
          ["event", "行事カレンダー"],
          ["bus", "バス時刻表"],
        ].map(([k, l]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            style={{
              padding: "10px 18px",
              background: "transparent",
              border: "none",
              borderBottom:
                tab === k ? `2px solid ${T.cobalt}` : "2px solid transparent",
              color: tab === k ? T.cobaltDeep : T.ink3,
              fontWeight: tab === k ? 700 : 500,
              fontFamily: "inherit",
              fontSize: 13,
              cursor: "pointer",
              marginBottom: -1,
            }}
          >
            {l}
          </button>
        ))}
      </div>

      {tab === "notice" && (
        <div>
          {/* エラーバナー */}
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
                onClick={loadList}
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
          {!loading && !fetchError && posts.length === 0 && (
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

          {posts.map((p) => {
            const isOpen = openId === p._id;
            const det = detailCache[p._id];
            return (
              <div
                key={p._id}
                style={{
                  background: T.surface,
                  border: `1px solid ${T.line}`,
                  borderRadius: 10,
                  marginBottom: 10,
                  fontSize: 13,
                  overflow: "hidden",
                }}
              >
                {/* カードヘッダー — クリックで展開 */}
                <div
                  onClick={() => openDetail(p._id)}
                  style={{ padding: "14px 16px", cursor: "pointer" }}
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
                        fontFamily: T.mono,
                        color: T.ink3,
                        fontSize: 11,
                      }}
                    >
                      {p.date}
                    </span>
                    <span style={{ color: T.ink3, fontSize: 11 }}>
                      · {p.author}
                    </span>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "1px 6px",
                        borderRadius: 4,
                        background: T.cobaltSoft,
                        color: T.cobaltDeep,
                        border: `1px solid ${T.infoBorder}`,
                      }}
                    >
                      {scopeLabel[p.scope] || p.scope}
                    </span>
                    {p.reply_count > 0 && (
                      <span style={{ fontSize: 11, color: T.ink3 }}>
                        💬 {p.reply_count}
                      </span>
                    )}
                    <div style={{ flex: 1 }} />
                    {/* 編集ボタン（自分が投稿者の場合のみ — authProfile id チェックは省略し常時表示） */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const d = detailCache[p._id];
                        setEditTarget({
                          id: p._id,
                          title: p.title,
                          body: d ? d.body : p.body || "",
                          scope: p.scope,
                        });
                      }}
                      style={{
                        padding: "3px 8px",
                        background: T.surface,
                        color: T.ink2,
                        border: `1px solid ${T.lineStrong}`,
                        borderRadius: 5,
                        fontFamily: "inherit",
                        fontSize: 11,
                        cursor: "pointer",
                      }}
                    >
                      編集
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(p._id);
                      }}
                      style={{
                        padding: "3px 8px",
                        background: T.surface,
                        color: T.danger,
                        border: `1px solid ${T.dangerBorder}`,
                        borderRadius: 5,
                        fontFamily: "inherit",
                        fontSize: 11,
                        cursor: "pointer",
                      }}
                    >
                      削除
                    </button>
                    <span style={{ fontSize: 12, color: T.ink3 }}>
                      {isOpen ? "▲" : "▼"}
                    </span>
                  </div>
                  <div
                    style={{
                      fontWeight: 700,
                      fontSize: 14,
                      marginBottom: 4,
                    }}
                  >
                    {p.title}
                  </div>
                  {p.body && (
                    <div
                      style={{
                        color: T.ink2,
                        fontSize: 12,
                        lineHeight: 1.6,
                      }}
                    >
                      {p.body}
                    </div>
                  )}
                </div>

                {/* 展開時: 全文 + 返信 */}
                {isOpen && (
                  <div
                    style={{
                      padding: "0 16px 16px",
                      borderTop: `1px solid ${T.line}`,
                      background: T.surfaceAlt,
                    }}
                  >
                    {det ? (
                      <>
                        {det.body && det.body !== p.body && (
                          <div
                            style={{
                              margin: "12px 0",
                              padding: "10px 12px",
                              background: T.surface,
                              border: `1px solid ${T.line}`,
                              borderRadius: 8,
                              fontSize: 13,
                              lineHeight: 1.7,
                              whiteSpace: "pre-wrap",
                            }}
                          >
                            {det.body}
                          </div>
                        )}
                        {/* 返信一覧 */}
                        <div style={{ marginTop: 12 }}>
                          <div
                            style={{
                              fontSize: 11,
                              color: T.ink3,
                              fontWeight: 600,
                              letterSpacing: 1,
                              marginBottom: 8,
                            }}
                          >
                            返信 {det.replies ? det.replies.length : 0}件
                          </div>
                          {det.replies &&
                            det.replies.map((r) => (
                              <div
                                key={r.id}
                                style={{
                                  display: "flex",
                                  gap: 10,
                                  alignItems: "flex-start",
                                  padding: "8px 10px",
                                  background: T.surface,
                                  border: `1px solid ${T.line}`,
                                  borderRadius: 7,
                                  marginBottom: 6,
                                  fontSize: 12,
                                }}
                              >
                                <div style={{ flex: 1 }}>
                                  <span
                                    style={{
                                      fontWeight: 700,
                                      color: T.cobaltDeep,
                                    }}
                                  >
                                    {r.author_name}
                                  </span>
                                  <span
                                    style={{
                                      color: T.ink3,
                                      marginLeft: 8,
                                      fontFamily: T.mono,
                                      fontSize: 11,
                                    }}
                                  >
                                    {new Date(r.created_at).toLocaleString(
                                      "ja-JP",
                                    )}
                                  </span>
                                  <div
                                    style={{
                                      marginTop: 4,
                                      color: T.ink2,
                                      lineHeight: 1.6,
                                    }}
                                  >
                                    {r.body}
                                  </div>
                                </div>
                                <button
                                  onClick={() => handleDeleteReply(p._id, r.id)}
                                  style={{
                                    padding: "2px 7px",
                                    background: "transparent",
                                    color: T.danger,
                                    border: `1px solid ${T.dangerBorder}`,
                                    borderRadius: 4,
                                    fontFamily: "inherit",
                                    fontSize: 11,
                                    cursor: "pointer",
                                    flexShrink: 0,
                                  }}
                                >
                                  削除
                                </button>
                              </div>
                            ))}
                        </div>
                        {/* 返信入力 */}
                        <div
                          style={{
                            display: "flex",
                            gap: 8,
                            marginTop: 10,
                          }}
                        >
                          <input
                            value={replyInput[p._id] || ""}
                            onChange={(e) =>
                              setReplyInput((r) => ({
                                ...r,
                                [p._id]: e.target.value,
                              }))
                            }
                            onKeyDown={(e) =>
                              e.key === "Enter" &&
                              !e.shiftKey &&
                              handleReply(p._id)
                            }
                            placeholder="返信を入力… (Enter で送信)"
                            style={{
                              flex: 1,
                              padding: "8px 10px",
                              border: `1px solid ${T.lineStrong}`,
                              borderRadius: 7,
                              fontSize: 12,
                              fontFamily: "inherit",
                            }}
                          />
                          <button
                            onClick={() => handleReply(p._id)}
                            disabled={!(replyInput[p._id] || "").trim()}
                            style={{
                              padding: "8px 14px",
                              background: (replyInput[p._id] || "").trim()
                                ? T.cobalt
                                : T.line,
                              color: "#fff",
                              border: "none",
                              borderRadius: 7,
                              fontFamily: "inherit",
                              fontSize: 12,
                              fontWeight: 700,
                              cursor: (replyInput[p._id] || "").trim()
                                ? "pointer"
                                : "not-allowed",
                            }}
                          >
                            送信
                          </button>
                        </div>
                      </>
                    ) : (
                      <div
                        style={{
                          padding: "12px 0",
                          color: T.ink3,
                          fontSize: 12,
                        }}
                      >
                        読み込み中…
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
      {tab === "event" && (
        <EventCalendar teacher={teacher} authToken={authToken} />
      )}
      {tab === "bus" && (
        <BusSchedulePanel teacher={teacher} authToken={authToken} />
      )}
      {composing && (
        <ComposeNoticeModal
          onClose={() => setComposing(false)}
          onSubmit={handlePost}
        />
      )}
      {/* 編集 modal — ComposeNoticeModal を初期値付きで流用 */}
      {editTarget && (
        <EditNoticeModal
          initial={editTarget}
          onClose={() => setEditTarget(null)}
          onSubmit={(input) => handleUpdate(editTarget.id, input)}
        />
      )}
    </div>
  );
}

// 公告編集 modal — ComposeNoticeModal と同構造、初期値あり版
function EditNoticeModal({
  initial,
  onClose,
  onSubmit,
}: {
  initial: { title: string; body: string; scope: AnnouncementScope };
  onClose: () => void;
  onSubmit: (input: {
    title: string;
    body: string;
    scope: AnnouncementScope;
  }) => Promise<void>;
}) {
  const T = RYO;
  const [title, setTitle] = React.useState(initial.title || "");
  const [body, setBody] = React.useState(initial.body || "");
  const [scope, setScope] = React.useState<AnnouncementScope>(
    initial.scope || "all",
  );
  const [submitting, setSubmitting] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState("");
  const handleSubmit = async () => {
    if (!title.trim() || submitting) return;
    setSubmitting(true);
    setErrorMsg("");
    try {
      await onSubmit({ title: title.trim(), body: body.trim(), scope });
    } catch (e) {
      setErrorMsg((e as Error)?.message || "保存に失敗しました");
      setSubmitting(false);
    }
  };
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
          <div style={{ fontSize: 15, fontWeight: 700 }}>お知らせを編集</div>
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
              タイトル
            </div>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontSize: 14,
                fontFamily: "inherit",
                boxSizing: "border-box",
              }}
            />
          </div>
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
              本文
            </div>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={6}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontSize: 13,
                fontFamily: "inherit",
                boxSizing: "border-box",
                resize: "vertical",
                lineHeight: 1.6,
              }}
            />
          </div>
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
              配信対象
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {[
                { k: "all", label: "全寮生" },
                { k: "male", label: "男子寮のみ" },
                { k: "female", label: "女子寮のみ" },
              ].map((o) => (
                <button
                  key={o.k}
                  onClick={() => setScope(o.k as AnnouncementScope)}
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: scope === o.k ? T.cobalt : T.surface,
                    color: scope === o.k ? "#fff" : T.ink2,
                    border: `1px solid ${scope === o.k ? T.cobalt : T.lineStrong}`,
                    borderRadius: 8,
                    fontSize: 12,
                    fontWeight: 600,
                    fontFamily: "inherit",
                    cursor: "pointer",
                  }}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>
          {errorMsg && (
            <div
              style={{
                padding: "8px 12px",
                background: T.dangerSoft,
                color: T.danger,
                border: `1px solid ${T.danger}`,
                borderRadius: 8,
                fontSize: 12,
              }}
            >
              {errorMsg}
            </div>
          )}
        </div>
        <div
          style={{
            padding: "12px 20px",
            background: T.surfaceAlt,
            borderTop: `1px solid ${T.line}`,
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          }}
        >
          <button
            onClick={onClose}
            disabled={submitting}
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
            onClick={handleSubmit}
            disabled={!title.trim() || submitting}
            style={{
              padding: "8px 16px",
              background: !title.trim() || submitting ? T.line : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: !title.trim() || submitting ? "not-allowed" : "pointer",
            }}
          >
            {submitting ? "保存中..." : "保存"}
          </button>
        </div>
      </div>
    </div>
  );
}

// 行事カレンダー — 真后端数据版（5-30 改造）
// 后端字段: id / title / category / event_date / start_at? / end_at? / description?
// 权限：寮務部長 / 寮務課長 / 管理係 才显示增删改按钮
function EventCalendar({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  const EDIT_ROLES = ["寮務部長", "寮務課長", "管理係"];
  const canEdit = EDIT_ROLES.includes((teacher && teacher.role) || "");

  const today = new Date();
  const fmt = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const todayKey = fmt(today);
  const [cursor, setCursor] = React.useState(
    new Date(today.getFullYear(), today.getMonth(), 1),
  );
  const [selected, setSelected] = React.useState(todayKey);
  const [composing, setComposing] = React.useState(false);
  // 编辑目标：null | 行事对象
  const [editTarget, setEditTarget] = React.useState<EventRow | null>(null);
  // 从后端拉取的行事列表
  const [list, setList] = React.useState<EventRow[]>([]);
  const [loadingEvt, setLoadingEvt] = React.useState(false);
  const [evtError, setEvtError] = React.useState<string | null>(null);

  // 后端字段 → UI 内部格式适配
  // event_date: "YYYY-MM-DD", start_at: ISO datetime | null
  const adapt = (item: EventItem): EventRow => ({
    _id: item.id,
    date: item.event_date,
    time: item.start_at
      ? item.start_at.slice(11, 16) // "HH:MM"
      : null,
    title: item.title,
    category: item.category,
    description: item.description || "",
    start_at: item.start_at,
    end_at: item.end_at,
  });

  // 拉取当前月前后各1个月范围的行事（保证翻月不闪）
  const loadEvents = React.useCallback(() => {
    if (!authToken) return;
    const y = cursor.getFullYear();
    const m = cursor.getMonth();
    const from = `${y}-${String(m + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(y, m + 1, 0).getDate();
    const to = `${y}-${String(m + 1).padStart(2, "0")}-${lastDay}`;
    setLoadingEvt(true);
    setEvtError(null);
    api
      .listEvents(authToken, from, to)
      .then((data) => setList((data.items || []).map(adapt)))
      .catch((e) => setEvtError(e.message || "行事の取得に失敗しました"))
      .finally(() => setLoadingEvt(false));
  }, [authToken, cursor]);

  React.useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const y = cursor.getFullYear();
  const m = cursor.getMonth();
  const firstDow = new Date(y, m, 1).getDay();
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDow; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  const eventsByDate = list.reduce(
    (acc, e) => {
      (acc[e.date] = acc[e.date] || []).push(e);
      return acc;
    },
    {} as Record<string, EventRow[]>,
  );
  const dayKey = (d: number) =>
    `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  const selEvents = (eventsByDate[selected] || [])
    .slice()
    .sort((a, b) => (a.time || "99:99").localeCompare(b.time || "99:99"));
  const selDate = new Date(selected + "T00:00:00");
  const selJa = `${selDate.getMonth() + 1}月${selDate.getDate()}日（${["日", "月", "火", "水", "木", "金", "土"][selDate.getDay()]}）`;
  const monthJa = `${y}年${m + 1}月`;

  const dowLabels = ["日", "月", "火", "水", "木", "金", "土"];
  const navMonth = (delta: number) => setCursor(new Date(y, m + delta, 1));

  // 新增：提交到后端后刷新列表
  const handleCreate = async (formData: EventFormData) => {
    if (!authToken) return;
    await api.createEvent(toEventCreateIn(formData), authToken);
    setComposing(false);
    setSelected(formData.event_date);
    loadEvents();
  };

  // 编辑：提交到后端后刷新
  const handleUpdate = async (id: string, formData: EventFormData) => {
    if (!authToken) return;
    await api.updateEvent(id, toEventCreateIn(formData), authToken);
    setEditTarget(null);
    loadEvents();
  };

  // 删除：后端物理删除
  const handleDelete = async (id: string) => {
    if (!authToken) return;
    if (!confirm("この行事を削除しますか？")) return;
    try {
      await api.deleteEvent(id, authToken);
      loadEvents();
    } catch (e) {
      alert(
        "削除に失敗しました：" + ((e as Error).message || JSON.stringify(e)),
      );
    }
  };

  // EventFormData（null 許容）→ EventCreateIn（undefined 許容）に変換。
  const toEventCreateIn = (fd: EventFormData) => ({
    title: fd.title,
    category: fd.category,
    event_date: fd.event_date,
    start_at: fd.start_at ?? undefined,
    end_at: fd.end_at ?? undefined,
    description: fd.description ?? undefined,
  });

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(420px, 1.3fr) 1fr",
        gap: 20,
        alignItems: "start",
      }}
    >
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 20px",
          boxShadow: T.shadow1,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 14,
          }}
        >
          <button
            onClick={() => navMonth(-1)}
            title="前月"
            style={{
              width: 32,
              height: 32,
              border: `1px solid ${T.line}`,
              background: T.surface,
              borderRadius: 8,
              cursor: "pointer",
              fontSize: 14,
              color: T.ink2,
              fontFamily: "inherit",
            }}
          >
            ‹
          </button>
          <div
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: T.ink,
              fontFamily: T.font,
            }}
          >
            {monthJa}
          </div>
          <button
            onClick={() => navMonth(1)}
            title="次月"
            style={{
              width: 32,
              height: 32,
              border: `1px solid ${T.line}`,
              background: T.surface,
              borderRadius: 8,
              cursor: "pointer",
              fontSize: 14,
              color: T.ink2,
              fontFamily: "inherit",
            }}
          >
            ›
          </button>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            gap: 4,
            marginBottom: 6,
          }}
        >
          {dowLabels.map((d, i) => (
            <div
              key={d}
              style={{
                textAlign: "center",
                fontSize: 11,
                fontWeight: 600,
                color: i === 0 ? T.danger : i === 6 ? T.cobalt : T.ink3,
                padding: "6px 0",
              }}
            >
              {d}
            </div>
          ))}
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            gap: 4,
          }}
        >
          {cells.map((d, i) => {
            if (d == null)
              return <div key={i} style={{ aspectRatio: "1 / 1" }} />;
            const k = dayKey(d);
            const has = (eventsByDate[k] || []).length > 0;
            const isSel = k === selected;
            const isToday = k === todayKey;
            const dow = (firstDow + d - 1) % 7;
            const baseColor =
              dow === 0 ? T.danger : dow === 6 ? T.cobalt : T.ink;
            return (
              <button
                key={i}
                onClick={() => setSelected(k)}
                style={{
                  aspectRatio: "1 / 1",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 3,
                  padding: 0,
                  fontFamily: "inherit",
                  background: isSel
                    ? T.cobalt
                    : isToday
                      ? T.cobaltSoft
                      : "transparent",
                  color: isSel ? "#fff" : baseColor,
                  border: isSel
                    ? `1px solid ${T.cobalt}`
                    : `1px solid transparent`,
                  borderRadius: 8,
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: isSel || isToday ? 700 : 500,
                  position: "relative",
                }}
              >
                <span>{d}</span>
                {has && (
                  <span
                    style={{
                      width: 5,
                      height: 5,
                      borderRadius: 3,
                      background: isSel ? "#fff" : T.cobalt,
                    }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        {/* 加载/错误状态 */}
        {loadingEvt && (
          <div style={{ padding: 16, color: T.ink3, fontSize: 13 }}>
            読み込み中…
          </div>
        )}
        {evtError && (
          <div
            style={{
              padding: "8px 12px",
              background: "#fff0f0",
              border: "1px solid #f5c6cb",
              borderRadius: 8,
              color: T.danger,
              fontSize: 12,
              marginBottom: 10,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span style={{ flex: 1 }}>{evtError}</span>
            <button
              onClick={loadEvents}
              style={{
                padding: "3px 10px",
                background: "transparent",
                color: T.danger,
                border: "1px solid #f5c6cb",
                borderRadius: 6,
                fontFamily: "inherit",
                fontSize: 11,
                cursor: "pointer",
              }}
            >
              再試行
            </button>
          </div>
        )}
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: 10,
            marginBottom: 12,
          }}
        >
          <div style={{ fontSize: 20, fontWeight: 700, color: T.ink }}>
            {selJa}
          </div>
          <div style={{ flex: 1 }} />
          <span
            style={{
              fontSize: 11,
              color: T.ink3,
              background: T.surfaceAlt,
              border: `1px solid ${T.line}`,
              padding: "3px 9px",
              borderRadius: 999,
              fontFamily: T.mono,
            }}
          >
            {selEvents.length}件
          </span>
          {canEdit && (
            <button
              onClick={() => setComposing(true)}
              style={{
                padding: "5px 12px",
                background: T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 6,
                fontFamily: "inherit",
                fontSize: 11,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              ＋ 追加
            </button>
          )}
        </div>
        {selEvents.length === 0 && !loadingEvt ? (
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
            この日に予定はありません
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {selEvents.map((e) => (
              <div
                key={e._id}
                style={{
                  padding: "12px 14px",
                  background: T.surface,
                  border: `1px solid ${T.line}`,
                  borderRadius: 10,
                  boxShadow: T.shadow1,
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
                      fontFamily: T.mono,
                      color: T.cobaltDeep,
                      fontWeight: 700,
                      fontSize: 14,
                      minWidth: 52,
                    }}
                  >
                    {e.time || "終日"}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 700,
                        color: T.ink,
                      }}
                    >
                      {e.title}
                    </div>
                    <div
                      style={{
                        fontSize: 11,
                        color: T.ink3,
                        marginTop: 2,
                      }}
                    >
                      {e.category}
                    </div>
                    {e.description && (
                      <div
                        style={{
                          fontSize: 12,
                          color: T.ink2,
                          marginTop: 4,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {e.description}
                      </div>
                    )}
                  </div>
                  {canEdit && (
                    <div style={{ display: "flex", gap: 4 }}>
                      <button
                        onClick={() => setEditTarget(e)}
                        style={{
                          padding: "3px 9px",
                          background: T.surface,
                          color: T.ink2,
                          border: `1px solid ${T.lineStrong}`,
                          borderRadius: 6,
                          fontFamily: "inherit",
                          fontSize: 11,
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        編集
                      </button>
                      <button
                        onClick={() => handleDelete(e._id)}
                        style={{
                          padding: "3px 9px",
                          background: T.surface,
                          color: T.danger,
                          border: `1px solid ${T.dangerBorder}`,
                          borderRadius: 6,
                          fontFamily: "inherit",
                          fontSize: 11,
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        削除
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {composing && (
        <EventComposeModal
          initialDate={selected}
          onClose={() => setComposing(false)}
          onSubmit={handleCreate}
        />
      )}
      {editTarget && (
        <EventComposeModal
          initialDate={editTarget.date}
          initial={editTarget}
          onClose={() => setEditTarget(null)}
          onSubmit={(fd) => handleUpdate(editTarget._id, fd)}
        />
      )}
    </div>
  );
}

// 行事追加/編集 modal — 后端字段版（5-30 改造）
// onSubmit 收到 { title, category, event_date, start_at?, end_at?, description? }
function EventComposeModal({
  initialDate,
  initial,
  onClose,
  onSubmit,
}: {
  initialDate: string;
  initial?: EventRow;
  onClose: () => void;
  onSubmit: (fd: EventFormData) => Promise<void>;
}) {
  const T = RYO;
  const Shell = ModalShell;
  const Field = ModalField;
  const Footer = ModalFooter;
  const inputStyle = modalInputStyle(T);
  const isEdit = !!initial;

  // start_at/end_at 是 ISO datetime，UI 分拆为日期 + 时刻
  const toTimeStr = (iso: string | null) => (iso ? iso.slice(11, 16) : "");

  const [date, setDate] = React.useState(initial ? initial.date : initialDate);
  const [time, setTime] = React.useState(
    initial ? toTimeStr(initial.start_at) : "",
  );
  const [endTime, setEndTime] = React.useState(
    initial ? toTimeStr(initial.end_at) : "",
  );
  const [title, setTitle] = React.useState(initial ? initial.title : "");
  const [category, setCategory] = React.useState(
    initial ? initial.category : "学校行事",
  );
  const [description, setDescription] = React.useState(
    initial ? initial.description : "",
  );
  const [submitting, setSubmitting] = React.useState(false);
  const [errMsg, setErrMsg] = React.useState("");

  // 把 YYYY-MM-DD + HH:MM 拼成 ISO datetime（带 T，后端接受）
  const toIso = (dateStr: string, timeStr: string) =>
    dateStr && timeStr ? `${dateStr}T${timeStr}:00` : null;

  const valid = title.trim() && date;

  const submit = async () => {
    if (!valid || submitting) return;
    setSubmitting(true);
    setErrMsg("");
    try {
      await onSubmit({
        title: title.trim(),
        category,
        event_date: date,
        start_at: toIso(date, time),
        end_at: toIso(date, endTime),
        description: description.trim() || null,
      });
    } catch (e) {
      setErrMsg((e as Error).message || "保存に失敗しました");
      setSubmitting(false);
    }
  };

  return (
    <Shell T={T} title={isEdit ? "行事を編集" : "行事を追加"} onClose={onClose}>
      <Field T={T} label="日付 *">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          style={inputStyle}
        />
      </Field>
      <Field T={T} label="カテゴリー *">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={inputStyle}
        >
          {["学校行事", "寮行事", "外部", "その他"].map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </Field>
      <Field T={T} label="タイトル *">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例：避難訓練"
          style={inputStyle}
        />
      </Field>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
        }}
      >
        <Field T={T} label="開始時刻（任意）">
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="終了時刻（任意）">
          <input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            style={inputStyle}
          />
        </Field>
      </div>
      <Field T={T} label="詳細（任意）">
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          placeholder="例：グラウンド集合、雨天は体育館"
          style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }}
        />
      </Field>
      {errMsg && (
        <div
          style={{
            padding: "8px 12px",
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            fontSize: 12,
          }}
        >
          {errMsg}
        </div>
      )}
      <Footer
        T={T}
        onClose={onClose}
        onSubmit={submit}
        disabled={!valid || submitting}
      />
    </Shell>
  );
}

// 巴士时刻表面板 — 真后端数据版（5-30 改造）
// 后端字段: id / kind / name / direction / schedule_at / arrival_at? / visible_to / note? / deprecated
// 权限：寮務部長 / 寮務課長 / 管理係 才显示增删改
function BusSchedulePanel({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  const EDIT_ROLES = ["寮務部長", "寮務課長", "管理係"];
  const canEdit = EDIT_ROLES.includes((teacher && teacher.role) || "");

  const [routes, setRoutes] = React.useState<BusRoute[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  // null | 'new' | route对象
  const [composing, setComposing] = React.useState<false | "new" | BusRoute>(
    false,
  );
  // all / daily_commute / dorm_special
  const [kindFilter, setKindFilter] = React.useState("all");

  // visible_to 显示标签
  const visibleLabel: Record<string, string> = {
    all: "全員",
    dorm_only: "寮生のみ",
    men: "男子寮",
    women: "女子寮",
  };

  const loadRoutes = React.useCallback(() => {
    if (!authToken) return;
    setLoading(true);
    setLoadError(null);
    api
      .listBusRoutes(authToken)
      .then((data) => setRoutes(data.items || []))
      .catch((e) => setLoadError(e.message || "バス便の取得に失敗しました"))
      .finally(() => setLoading(false));
  }, [authToken]);

  React.useEffect(() => {
    loadRoutes();
  }, [loadRoutes]);

  // 按 kind 过滤
  const filtered =
    kindFilter === "all" ? routes : routes.filter((r) => r.kind === kindFilter);

  // 按 kind 分组
  const commute = filtered.filter((r) => r.kind === "daily_commute");
  const special = filtered.filter((r) => r.kind === "dorm_special");

  // 软停用（DELETE → deprecated=true）
  const handleDeprecate = async (id: string) => {
    if (!authToken) return;
    if (!confirm("このバス便を運休にしますか？（非表示になります）")) return;
    try {
      await api.deleteBusRoute(id, authToken);
      loadRoutes();
    } catch (e) {
      alert(
        "運休に失敗しました：" + ((e as Error).message || JSON.stringify(e)),
      );
    }
  };

  const handleCreate = async (formData: BusRouteFormData) => {
    if (!authToken) return;
    await api.createBusRoute(toBusRouteCreateIn(formData), authToken);
    setComposing(false);
    loadRoutes();
  };

  const handleUpdate = async (id: string, formData: BusRouteFormData) => {
    if (!authToken) return;
    await api.updateBusRoute(id, toBusRouteCreateIn(formData), authToken);
    setComposing(false);
    loadRoutes();
  };

  // BusRouteFormData（null 許容）→ BusRouteCreateIn（undefined 許容）に変換。
  const toBusRouteCreateIn = (fd: BusRouteFormData) => ({
    kind: fd.kind,
    name: fd.name,
    direction: fd.direction,
    schedule_at: fd.schedule_at ?? "",
    arrival_at: fd.arrival_at ?? undefined,
    visible_to: fd.visible_to,
    note: fd.note ?? undefined,
  });

  // 时刻格式化：ISO → HH:MM
  const fmtTime = (iso: string | null) => (iso ? iso.slice(11, 16) : "—");

  const RouteRow = ({ r }: { r: BusRoute }) => (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "56px 1fr auto auto",
        alignItems: "center",
        gap: 10,
        padding: "10px 14px",
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 8,
        marginBottom: 6,
      }}
    >
      <span
        style={{
          fontFamily: T.mono,
          color: T.cobaltDeep,
          fontWeight: 700,
          fontSize: 14,
        }}
      >
        {fmtTime(r.schedule_at)}
      </span>
      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.ink }}>
          {r.name}
        </div>
        <div style={{ fontSize: 11, color: T.ink3, marginTop: 2 }}>
          {r.direction}
          {r.arrival_at ? ` → ${fmtTime(r.arrival_at)} 着` : ""}
          {" · "}
          {visibleLabel[r.visible_to] || r.visible_to}
        </div>
        {r.note && (
          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              marginTop: 3,
              fontStyle: "italic",
            }}
          >
            {r.note}
          </div>
        )}
      </div>
      {canEdit && (
        <>
          <button
            onClick={() => setComposing(r)}
            style={{
              padding: "3px 9px",
              background: T.surface,
              color: T.ink2,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 6,
              fontFamily: "inherit",
              fontSize: 11,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            編集
          </button>
          <button
            onClick={() => handleDeprecate(r.id)}
            style={{
              padding: "3px 9px",
              background: T.surface,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 6,
              fontFamily: "inherit",
              fontSize: 11,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            運休
          </button>
        </>
      )}
    </div>
  );

  const Section = ({ title, items }: { title: string; items: BusRoute[] }) =>
    items.length === 0 ? null : (
      <div style={{ marginBottom: 20 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            color: T.ink3,
            letterSpacing: 1,
            marginBottom: 8,
          }}
        >
          {title}
        </div>
        {items.map((r) => (
          <RouteRow key={r.id} r={r} />
        ))}
      </div>
    );

  return (
    <div>
      {/* ヘッダー */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 14,
          gap: 10,
          flexWrap: "wrap",
        }}
      >
        {/* kind フィルター */}
        <div style={{ display: "flex", gap: 6 }}>
          {[
            ["all", "すべて"],
            ["daily_commute", "平日通学便"],
            ["dorm_special", "寮特殊便"],
          ].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setKindFilter(k)}
              style={{
                padding: "5px 12px",
                background: kindFilter === k ? T.cobaltSoft : T.surface,
                color: kindFilter === k ? T.cobaltDeep : T.ink3,
                border: `1px solid ${kindFilter === k ? T.cobalt : T.lineStrong}`,
                borderRadius: 999,
                fontFamily: "inherit",
                fontSize: 11,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {l}
            </button>
          ))}
        </div>
        {canEdit && (
          <button
            onClick={() => setComposing("new")}
            style={{
              padding: "7px 14px",
              background: T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: T.shadow1,
              whiteSpace: "nowrap",
            }}
          >
            ＋ バス便を追加
          </button>
        )}
      </div>

      {/* エラー / ローディング */}
      {loading && (
        <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
          読み込み中…
        </div>
      )}
      {loadError && (
        <div
          style={{
            padding: "8px 12px",
            background: "#fff0f0",
            border: "1px solid #f5c6cb",
            borderRadius: 8,
            color: T.danger,
            fontSize: 12,
            marginBottom: 10,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span style={{ flex: 1 }}>{loadError}</span>
          <button
            onClick={loadRoutes}
            style={{
              padding: "3px 10px",
              background: "transparent",
              color: T.danger,
              border: "1px solid #f5c6cb",
              borderRadius: 6,
              fontFamily: "inherit",
              fontSize: 11,
              cursor: "pointer",
            }}
          >
            再試行
          </button>
        </div>
      )}

      {/* リスト */}
      {!loading && !loadError && filtered.length === 0 && (
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
          バス便はまだ登録されていません
        </div>
      )}
      <Section title="平日通学便" items={commute} />
      <Section title="寮特殊便" items={special} />

      {/* 追加/編集 modal */}
      {composing && (
        <BusRouteModal
          T={T}
          initial={composing === "new" ? null : composing}
          onClose={() => setComposing(false)}
          onSubmit={
            composing === "new"
              ? handleCreate
              : (fd) => handleUpdate((composing as BusRoute).id, fd)
          }
        />
      )}
    </div>
  );
}

// 巴士便 追加/編集 modal
function BusRouteModal({
  T,
  initial,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  initial: BusRoute | null;
  onClose: () => void;
  onSubmit: (fd: BusRouteFormData) => Promise<void>;
}) {
  const Shell = ModalShell;
  const Field = ModalField;
  const Footer = ModalFooter;
  const inputStyle = modalInputStyle(T);
  const isEdit = !!initial;

  const toDateStr = (iso: string | null) => (iso ? iso.slice(0, 10) : "");
  const toTimeStr = (iso: string | null) => (iso ? iso.slice(11, 16) : "");

  const [kind, setKind] = React.useState<string>(
    initial ? initial.kind : "daily_commute",
  );
  const [name, setName] = React.useState(initial ? initial.name : "");
  const [direction, setDirection] = React.useState(
    initial ? initial.direction : "",
  );
  // schedule_at / arrival_at は ISO datetime。UI では日付 + 時刻に分割
  const [schedDate, setSchedDate] = React.useState(
    initial ? toDateStr(initial.schedule_at) : "",
  );
  const [schedTime, setSchedTime] = React.useState(
    initial ? toTimeStr(initial.schedule_at) : "",
  );
  const [arrDate, setArrDate] = React.useState(
    initial ? toDateStr(initial.arrival_at) : "",
  );
  const [arrTime, setArrTime] = React.useState(
    initial ? toTimeStr(initial.arrival_at) : "",
  );
  const [visibleTo, setVisibleTo] = React.useState(
    initial ? initial.visible_to : "all",
  );
  const [note, setNote] = React.useState(initial ? initial.note || "" : "");
  const [submitting, setSubmitting] = React.useState(false);
  const [errMsg, setErrMsg] = React.useState("");

  const toIso = (d: string, t: string) => (d && t ? `${d}T${t}:00` : null);
  const valid = name.trim() && direction.trim() && schedDate && schedTime;

  const submit = async () => {
    if (!valid || submitting) return;
    setSubmitting(true);
    setErrMsg("");
    try {
      await onSubmit({
        kind,
        name: name.trim(),
        direction: direction.trim(),
        schedule_at: toIso(schedDate, schedTime),
        arrival_at: toIso(arrDate, arrTime),
        visible_to: visibleTo,
        note: note.trim() || null,
      });
    } catch (e) {
      setErrMsg((e as Error).message || "保存に失敗しました");
      setSubmitting(false);
    }
  };

  return (
    <Shell
      T={T}
      title={isEdit ? "バス便を編集" : "バス便を追加"}
      onClose={onClose}
    >
      <Field T={T} label="種別 *">
        <select
          value={kind}
          onChange={(e) => setKind(e.target.value)}
          style={inputStyle}
        >
          <option value="daily_commute">平日通学便</option>
          <option value="dorm_special">寮特殊便</option>
        </select>
      </Field>
      <Field T={T} label="便名 *">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="例：登校便"
          style={inputStyle}
        />
      </Field>
      <Field T={T} label="方向（区間）*">
        <input
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          placeholder="例：岡山駅西口 → 高校棟"
          style={inputStyle}
        />
      </Field>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
        }}
      >
        <Field T={T} label="出発日 *">
          <input
            type="date"
            value={schedDate}
            onChange={(e) => setSchedDate(e.target.value)}
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="出発時刻 *">
          <input
            type="time"
            value={schedTime}
            onChange={(e) => setSchedTime(e.target.value)}
            style={inputStyle}
          />
        </Field>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
        }}
      >
        <Field T={T} label="到着日（任意）">
          <input
            type="date"
            value={arrDate}
            onChange={(e) => setArrDate(e.target.value)}
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="到着時刻（任意）">
          <input
            type="time"
            value={arrTime}
            onChange={(e) => setArrTime(e.target.value)}
            style={inputStyle}
          />
        </Field>
      </div>
      <Field T={T} label="対象">
        <select
          value={visibleTo}
          onChange={(e) => setVisibleTo(e.target.value)}
          style={inputStyle}
        >
          <option value="all">全員</option>
          <option value="dorm_only">寮生のみ</option>
          <option value="men">男子寮</option>
          <option value="women">女子寮</option>
        </select>
      </Field>
      <Field T={T} label="備考（任意）">
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          placeholder="例：部活対応 / 雨天中止"
          style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }}
        />
      </Field>
      {errMsg && (
        <div
          style={{
            padding: "8px 12px",
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            fontSize: 12,
          }}
        >
          {errMsg}
        </div>
      )}
      <Footer
        T={T}
        onClose={onClose}
        onSubmit={submit}
        disabled={!valid || submitting}
      />
    </Shell>
  );
}

function BusPostCard({
  post,
  T,
  open,
  onToggle,
  onEditPost,
  onDeletePost,
  onPin,
}: {
  post: BusPost;
  T: RyoTokens;
  open: boolean;
  onToggle: () => void;
  onEditPost: () => void;
  onDeletePost: () => void;
  onPin: () => void;
}) {
  return (
    <div
      style={{
        background: T.surface,
        border: `1px solid ${post.pinned ? T.cobalt : T.line}`,
        borderRadius: 10,
        marginBottom: 10,
        overflow: "hidden",
        boxShadow: post.pinned ? T.shadow1 : "none",
      }}
    >
      <div
        onClick={onToggle}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "12px 14px",
          cursor: "pointer",
        }}
      >
        <span
          style={{
            fontSize: 14,
            color: T.ink3,
            fontFamily: T.mono,
            width: 14,
            textAlign: "center",
          }}
        >
          {open ? "▼" : "▶"}
        </span>
        {post.pinned && (
          <span
            style={{
              fontSize: 10,
              color: "#fff",
              background: T.cobalt,
              padding: "2px 6px",
              borderRadius: 4,
              fontWeight: 700,
              letterSpacing: 1,
            }}
          >
            PIN
          </span>
        )}
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            padding: "2px 8px",
            borderRadius: 4,
            background:
              post.category === "特別運行便" ? T.cobaltSoft : T.surfaceAlt,
            color: post.category === "特別運行便" ? T.cobaltDeep : T.ink2,
            border: `1px solid ${post.category === "特別運行便" ? T.cobalt : T.line}`,
            whiteSpace: "nowrap",
          }}
        >
          {post.category}
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: T.ink,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {post.title}
          </div>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              fontFamily: T.mono,
              marginTop: 2,
            }}
          >
            {post.posted_on} · {post.posted_by} · {post.effective_from}
            {post.effective_until
              ? ` 〜 ${post.effective_until}`
              : " 〜 継続中"}{" "}
            · {post.events.length} 件
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onPin();
          }}
          style={{
            padding: "4px 10px",
            background: post.pinned ? T.cobaltSoft : T.surface,
            color: post.pinned ? T.cobaltDeep : T.ink3,
            border: `1px solid ${post.pinned ? T.cobalt : T.lineStrong}`,
            borderRadius: 6,
            fontFamily: "inherit",
            fontSize: 11,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {post.pinned ? "ピン解除" : "ピン留め"}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEditPost();
          }}
          style={{
            padding: "4px 10px",
            background: T.surface,
            color: T.ink2,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 6,
            fontFamily: "inherit",
            fontSize: 11,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          編集
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDeletePost();
          }}
          style={{
            padding: "4px 10px",
            background: T.surface,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 6,
            fontFamily: "inherit",
            fontSize: 11,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          削除
        </button>
      </div>
      {open && (
        <div
          style={{
            padding: "4px 14px 14px",
            borderTop: `1px solid ${T.line}`,
            background: T.surfaceAlt,
          }}
        >
          {post.body && (
            <div
              style={{
                padding: "10px 12px",
                margin: "10px 0",
                background: T.surface,
                border: `1px solid ${T.line}`,
                borderRadius: 8,
                fontSize: 12,
                lineHeight: 1.7,
                color: T.ink2,
                whiteSpace: "pre-wrap",
              }}
            >
              {post.body}
            </div>
          )}
          {post.events.length === 0 && (
            <div
              style={{
                padding: 20,
                textAlign: "center",
                color: T.ink3,
                fontSize: 12,
              }}
            >
              行事がまだ登録されていません
            </div>
          )}
          {post.events.map((ev, i) => (
            <BusEventBlock key={i} ev={ev} T={T} />
          ))}
        </div>
      )}
    </div>
  );
}

function BusEventBlock({ ev, T }: { ev: BusEventData; T: RyoTokens }) {
  return (
    <div
      style={{
        margin: "10px 0",
        padding: 12,
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 8,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 8,
          paddingBottom: 8,
          borderBottom: `1px solid ${T.line}`,
        }}
      >
        <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            padding: "3px 8px",
            background: T.cobaltSoft,
            color: T.cobaltDeep,
            borderRadius: 4,
            fontFamily: T.mono,
            letterSpacing: 0.5,
          }}
        >
          {ev.date}
        </span>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.ink, flex: 1 }}>
          {ev.name}
        </div>
        {ev.audience && (
          <div
            style={{
              fontSize: 10,
              color: T.ink3,
              maxWidth: 280,
              textAlign: "right",
              lineHeight: 1.4,
            }}
          >
            対象: {ev.audience}
          </div>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {ev.items.map((it, j) => (
          <div
            key={j}
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 12,
              fontSize: 12,
              padding: "5px 0",
              borderBottom:
                j < ev.items.length - 1 ? `1px dashed ${T.line}` : "none",
            }}
          >
            <span
              style={{
                fontFamily: T.mono,
                color: T.cobalt,
                fontWeight: 700,
                minWidth: 48,
              }}
            >
              {it.time}
            </span>
            <span style={{ color: T.ink, flex: 1, fontWeight: 500 }}>
              {it.action}
            </span>
            {it.location && (
              <span
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  minWidth: 68,
                  textAlign: "right",
                }}
              >
                {it.location}
              </span>
            )}
            {it.memo && (
              <span
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  flex: 2,
                  textAlign: "left",
                  fontStyle: "italic",
                }}
              >
                {it.memo}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function BusPostComposeModal({
  T,
  initial,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  initial?: BusPost | null;
  onClose: () => void;
  onSubmit: (post: {
    title: string;
    category: string;
    posted_on: string;
    posted_by: string;
    effective_from: string;
    effective_until: string | null;
    body: string;
  }) => void;
}) {
  const MS = ModalShell;
  const MField = ModalField;
  const MFooter = ModalFooter;
  const inputS = modalInputStyle;
  const [title, setTitle] = React.useState(initial ? initial.title : "");
  const [category, setCategory] = React.useState(
    initial ? initial.category : "特別運行便",
  );
  const [postedOn, setPostedOn] = React.useState(
    initial ? initial.posted_on : new Date().toISOString().slice(0, 10),
  );
  const [postedBy, setPostedBy] = React.useState(
    initial ? initial.posted_by : "国際交流部",
  );
  const [effectiveFrom, setEffectiveFrom] = React.useState(
    initial ? initial.effective_from : "",
  );
  const [effectiveUntil, setEffectiveUntil] = React.useState(
    initial ? initial.effective_until || "" : "",
  );
  const [body, setBody] = React.useState(initial ? initial.body : "");
  return (
    <MS
      T={T}
      title={initial ? "告知を編集" : "新規告知を作成"}
      onClose={onClose}
    >
      <MField T={T} label="タイトル">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例：特別運行便に関するお知らせ"
          style={inputS(T)}
        />
      </MField>
      <MField T={T} label="カテゴリー">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={inputS(T)}
        >
          {["特別運行便", "定期便", "イベント", "臨時"].map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </MField>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
        }}
      >
        <MField T={T} label="掲載日">
          <input
            type="date"
            value={postedOn}
            onChange={(e) => setPostedOn(e.target.value)}
            style={inputS(T)}
          />
        </MField>
        <MField T={T} label="発信元">
          <input
            value={postedBy}
            onChange={(e) => setPostedBy(e.target.value)}
            style={inputS(T)}
          />
        </MField>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
        }}
      >
        <MField T={T} label="有効 開始日">
          <input
            type="date"
            value={effectiveFrom}
            onChange={(e) => setEffectiveFrom(e.target.value)}
            style={inputS(T)}
          />
        </MField>
        <MField T={T} label="有効 終了日 (空欄 = 継続中)">
          <input
            type="date"
            value={effectiveUntil}
            onChange={(e) => setEffectiveUntil(e.target.value)}
            style={inputS(T)}
          />
        </MField>
      </div>
      <MField T={T} label="本文（前文 / 注意事項）">
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={5}
          placeholder="学校休業日等に..."
          style={{ ...inputS(T), resize: "vertical", lineHeight: 1.6 }}
        />
      </MField>
      <div style={{ fontSize: 11, color: T.ink3, padding: "6px 0" }}>
        ※ 行事（日付ごとの時刻表）は告知作成後、詳細画面から追加できます（demo
        段階では行事追加 UI は簡略化）。
      </div>
      <MFooter
        T={T}
        onClose={onClose}
        onSubmit={() =>
          title.trim() &&
          onSubmit({
            title: title.trim(),
            category,
            posted_on: postedOn,
            posted_by: postedBy.trim(),
            effective_from: effectiveFrom,
            effective_until: effectiveUntil || null,
            body: body.trim(),
          })
        }
        disabled={!title.trim()}
      />
    </MS>
  );
}

function ComposeNoticeModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (input: {
    title: string;
    body: string;
    scope: AnnouncementScope;
  }) => Promise<void>;
}) {
  const T = RYO;
  const [title, setTitle] = React.useState("");
  const [body, setBody] = React.useState("");
  // 5-27: 配送 scope — backend AnnouncementCreateIn.scope: "all" | "male" | "female"
  const [scope, setScope] = React.useState<AnnouncementScope>("all");
  const [submitting, setSubmitting] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState("");
  const handleSubmit = async () => {
    if (!title.trim() || submitting) return;
    setSubmitting(true);
    setErrorMsg("");
    try {
      await onSubmit({
        title: title.trim(),
        body: body.trim(),
        scope,
      });
    } catch (e) {
      setErrorMsg(
        (e as Error)?.message ||
          "お知らせの送信に失敗しました。サーバーに接続できないか、権限が不足している可能性があります。しばらくしてから再度お試しください。",
      );
      setSubmitting(false);
    }
  };
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
          <div style={{ fontSize: 15, fontWeight: 700 }}>新規お知らせ投稿</div>
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
              タイトル
            </div>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="例：今週金曜の清掃検査について"
              style={{
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontSize: 14,
                fontFamily: "inherit",
                boxSizing: "border-box",
              }}
            />
          </div>
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
              本文
            </div>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="詳細をここに記入..."
              rows={6}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontSize: 13,
                fontFamily: "inherit",
                boxSizing: "border-box",
                resize: "vertical",
                lineHeight: 1.6,
              }}
            />
          </div>
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
              配信対象
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {[
                { k: "all", label: "全寮生" },
                { k: "male", label: "男子寮のみ" },
                { k: "female", label: "女子寮のみ" },
              ].map((o) => (
                <button
                  key={o.k}
                  onClick={() => setScope(o.k as AnnouncementScope)}
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: scope === o.k ? T.cobalt : T.surface,
                    color: scope === o.k ? "#fff" : T.ink2,
                    border: `1px solid ${scope === o.k ? T.cobalt : T.lineStrong}`,
                    borderRadius: 8,
                    fontSize: 12,
                    fontWeight: 600,
                    fontFamily: "inherit",
                    cursor: "pointer",
                  }}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>
          {errorMsg && (
            <div
              style={{
                padding: "8px 12px",
                background: T.dangerSoft,
                color: T.danger,
                border: `1px solid ${T.danger}`,
                borderRadius: 8,
                fontSize: 12,
              }}
            >
              {errorMsg}
            </div>
          )}
          <div style={{ fontSize: 11, color: T.ink3 }}>
            投稿後、対象寮生の iOS・Android アプリにプッシュ通知が送信されます。
          </div>
        </div>
        <div
          style={{
            padding: "12px 20px",
            background: T.surfaceAlt,
            borderTop: `1px solid ${T.line}`,
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          }}
        >
          <button
            onClick={onClose}
            disabled={submitting}
            style={{
              padding: "8px 16px",
              background: T.surface,
              color: T.ink2,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: submitting ? "not-allowed" : "pointer",
            }}
          >
            キャンセル
          </button>
          <button
            onClick={handleSubmit}
            disabled={!title.trim() || submitting}
            style={{
              padding: "8px 16px",
              background: !title.trim() || submitting ? T.line : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: !title.trim() || submitting ? "not-allowed" : "pointer",
            }}
          >
            {submitting ? "送信中..." : "投稿"}
          </button>
        </div>
      </div>
    </div>
  );
}
