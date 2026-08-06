import React from "react";
import { RYO, S } from "../theme";
import type { RyoTokens } from "../theme";
import { api } from "../api/client";
import { canManage, C_EVENT, C_BUS } from "../api/permissions";
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
// 视觉改造：展开 S.input，保留原 padding / 描边强度。
function modalInputStyle(T: RyoTokens): React.CSSProperties {
  return {
    ...S.input,
    width: "100%",
    padding: "9px 12px",
    border: `1px solid ${T.lineStrong}`,
    boxSizing: "border-box",
  };
}

// 公告列表的 UI 内部结构（adaptList 的返回值）。
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

// 行事列表的 UI 内部结构（adapt 的返回值）。
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

// 行事 modal 的编辑对象 / 提交 payload。
interface EventFormData {
  title: string;
  category: string;
  event_date: string;
  start_at: string | null;
  end_at: string | null;
  description: string | null;
  notify_students: boolean;
}

// 巴士 modal 的提交 payload。6-15: kind/name 不再由表单收集（后端默认补全）。
interface BusRouteFormData {
  direction: string;
  schedule_at: string | null;
  arrival_at: string | null;
  visible_to: string;
  note: string | null;
  purpose: string | null;
  notify_students: boolean;
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
  // web#28: 详情拉取失败标记 { [id]: 错误文案 }，与「読み込み中」区分
  const [detailError, setDetailError] = React.useState<Record<string, string>>(
    {},
  );
  // 返信入力: { [id]: string }
  const [replyInput, setReplyInput] = React.useState<Record<string, string>>(
    {},
  );
  // 返信提交中: { [id]: true } — 锁定进行中的返信，防止重复投稿
  const [replySubmitting, setReplySubmitting] = React.useState<
    Record<string, boolean>
  >({});
  // setState 是异步的，按住回车的连发可能赶在重渲染前穿过 state 守卫——ref 当场生效，作同步锁
  const replySubmittingRef = React.useRef<Record<string, boolean>>({});
  // 編集対象: null | { id, title, body, scope }
  const [editTarget, setEditTarget] = React.useState<{
    id: string;
    title: string;
    body: string;
    scope: AnnouncementScope;
  } | null>(null);
  // 正在为編集拉全文的公告 id（防连点：拉取中忽略再次点击）
  const [editLoading, setEditLoading] = React.useState<string | null>(null);

  // ── 編集打开（先保证有全文）──
  // 列表项 body 是后端截 80 字的摘要（_summarize），直接当编辑初始值保存会把
  // 完整正文永久覆盖成摘要（审查 web#2 数据丢失）。缓存未命中就先拉详情，
  // 拉不到不开弹层
  const handleEditOpen = async (p: NoticeRow) => {
    if (editLoading) return;
    const cached = detailCache[p._id];
    if (cached) {
      setEditTarget({
        id: p._id,
        title: p.title,
        body: cached.body,
        scope: p.scope,
      });
      return;
    }
    if (!authToken) return;
    setEditLoading(p._id);
    try {
      const det = await api.getAnnouncement(p._id, authToken);
      setDetailCache((c) => ({ ...c, [p._id]: det }));
      setEditTarget({
        id: p._id,
        title: p.title,
        body: det.body,
        scope: p.scope,
      });
    } catch (e) {
      alert(
        "お知らせの内容を取得できませんでした。編集を開けません：" +
          ((e as Error).message || JSON.stringify(e)),
      );
    } finally {
      setEditLoading(null);
    }
  };

  // ── 一覧 adapt ──
  const adaptList = (data: { items?: AnnouncementBrief[] }): NoticeRow[] => {
    const items = (data && data.items) || [];
    return items.map((a) => {
      const d = new Date(a.created_at);
      // 卡片日期按 JST 归一，避免非 JST 浏览器跨日显示错日（与 EventCalendar 同源）
      const ymd = d.toLocaleDateString("en-CA", { timeZone: "Asia/Tokyo" });
      return {
        date: ymd.slice(5),
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

  // ── 詳細 fetch（可重试；openDetail / 再試行 共用）──
  const fetchDetail = (id: string) => {
    if (!authToken) return;
    // web#28: 进入加载前清掉该 id 的错误标记
    setDetailError((errs) => {
      const n = { ...errs };
      delete n[id];
      return n;
    });
    api
      .getAnnouncement(id, authToken)
      .then((det) => setDetailCache((c) => ({ ...c, [id]: det })))
      .catch((e) => {
        // web#28: 详情拉取失败写错误标记，展开区展示重试，不再假「読み込み中」
        console.warn("[InfoPage] getAnnouncement 失败", e);
        setDetailError((errs) => ({
          ...errs,
          [id]: (e as Error).message || "詳細の取得に失敗しました",
        }));
      });
  };

  // ── 詳細展開切換 ──
  const openDetail = (id: string) => {
    setOpenId((prev) => (prev === id ? null : id));
    if (!detailCache[id] && authToken) {
      fetchDetail(id);
    }
  };

  // ── 新規投稿 ──
  const handlePost = async (input: {
    title: string;
    body: string;
    scope: AnnouncementScope;
    notify_students: boolean;
  }) => {
    if (!authToken) throw new Error("未登录");
    await api.createAnnouncement(
      {
        title: input.title,
        body: input.body,
        scope: input.scope,
        notify_students: input.notify_students,
      },
      authToken,
    );
    const data = await api.listAnnouncements(authToken);
    setPosts(adaptList(data));
    setComposing(false);
  };

  // ── 編集保存 ──
  const handleUpdate = async (
    id: string,
    input: {
      title: string;
      body: string;
      scope: AnnouncementScope;
      notify_students: boolean;
    },
  ) => {
    if (!authToken) return;
    await api.updateAnnouncement(
      id,
      {
        title: input.title,
        body: input.body,
        scope: input.scope,
        notify_students: input.notify_students,
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
    // web#27: 删缓存后收起展开，否则 openId 仍指向该卡而 det=undefined → 永久「読み込み中」
    setOpenId(null);
    loadList();
  };

  // ── 削除 ──
  const handleDelete = async (id: string) => {
    if (!authToken) return;
    if (!confirm("このお知らせを削除しますか？")) return;
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
    // 提交中守卫：拦截连按回车 / 双击送信导致的重复投稿
    if (!body || !authToken || replySubmittingRef.current[announcementId])
      return;
    replySubmittingRef.current[announcementId] = true;
    setReplySubmitting((s) => ({ ...s, [announcementId]: true }));
    try {
      await api.postAnnouncementReply(announcementId, { body }, authToken);
      setReplyInput((r) => ({ ...r, [announcementId]: "" }));
      // 详情缓存更新 + 卡片 reply_count 与详情同步
      const det = await api.getAnnouncement(announcementId, authToken);
      setDetailCache((c) => ({ ...c, [announcementId]: det }));
      setPosts((prev) =>
        prev.map((p) =>
          p._id === announcementId
            ? { ...p, reply_count: det.replies?.length ?? 0 }
            : p,
        ),
      );
    } catch (e) {
      alert(
        "返信に失敗しました：" + ((e as Error).message || JSON.stringify(e)),
      );
    } finally {
      delete replySubmittingRef.current[announcementId];
      setReplySubmitting((s) => {
        const next = { ...s };
        delete next[announcementId];
        return next;
      });
    }
  };

  // ── 返信削除 ──
  const handleDeleteReply = async (announcementId: string, replyId: string) => {
    if (!authToken) return;
    try {
      await api.deleteAnnouncementReply(announcementId, replyId, authToken);
      const det = await api.getAnnouncement(announcementId, authToken);
      setDetailCache((c) => ({ ...c, [announcementId]: det }));
      setPosts((prev) =>
        prev.map((p) =>
          p._id === announcementId
            ? { ...p, reply_count: det.replies?.length ?? 0 }
            : p,
        ),
      );
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
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>お知らせ</h1>
        {tab === "notice" && (
          <button
            onClick={() => setComposing(true)}
            className="t-btn"
            style={{
              ...S.btnPrimary,
              padding: "8px 16px",
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
                onClick={loadList}
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
          {!loading && !fetchError && posts.length === 0 && (
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

          {posts.map((p, i) => {
            const isOpen = openId === p._id;
            const det = detailCache[p._id];
            return (
              <div
                key={p._id}
                className="t-fade-up"
                style={{
                  ...S.card,
                  marginBottom: 10,
                  fontSize: 13,
                  overflow: "hidden",
                  ...(i < 12 ? { animationDelay: `${i * 40}ms` } : null),
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
                        ...S.pill,
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "1px 6px",
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
                    {/* 編集/削除 只对投稿者本人显示（TW-013）：后端 update/delete 都有
                        author_teacher_id != teacher.id → 403 投稿者本人のみ。原来无条件常显，
                        非作者点了必 403，把老师诱导进注定失败的操作流程。 */}
                    {teacher && p.author_id === teacher.id && (
                      <>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditOpen(p);
                          }}
                          className="t-btn"
                          style={{
                            ...S.btnSmall,
                            padding: "3px 8px",
                            color: T.ink2,
                            border: `1px solid ${T.lineStrong}`,
                            fontSize: 11,
                          }}
                        >
                          編集
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(p._id);
                          }}
                          className="t-btn"
                          style={{
                            ...S.btnSmall,
                            padding: "3px 8px",
                            color: T.danger,
                            border: `1px solid ${T.dangerBorder}`,
                            fontSize: 11,
                          }}
                        >
                          削除
                        </button>
                      </>
                    )}
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
                  {(() => {
                    // 展开时把全文 det.body 原地替换掉摘要 p.body 显示；
                    // 未展开 / 详情还没拉到时仍显示摘要 —— 消除「摘要 + 全文」重复。
                    const showFull = isOpen && det && det.body;
                    const text = showFull ? det.body : p.body;
                    if (!text) return null;
                    return (
                      <div
                        style={{
                          color: T.ink2,
                          fontSize: showFull ? 13 : 12,
                          lineHeight: 1.7,
                          whiteSpace: showFull ? "pre-wrap" : "normal",
                        }}
                      >
                        {text}
                      </div>
                    );
                  })()}
                </div>

                {/* 展开区：只放回复列表 + 回复输入框（全文已在头部原地替换摘要显示）*/}
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
                        {/* 全文已在可折叠头部原地替换摘要显示，这里不再重复展示 */}
                        {/* 返信一覧（回复列表）*/}
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
                                  borderRadius: 10,
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
                                      { timeZone: "Asia/Tokyo" },
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
                                  className="t-btn"
                                  style={{
                                    ...S.btnSmall,
                                    padding: "2px 7px",
                                    background: "transparent",
                                    color: T.danger,
                                    border: `1px solid ${T.dangerBorder}`,
                                    fontSize: 11,
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
                            className="t-input"
                            style={{
                              ...S.input,
                              flex: 1,
                              padding: "8px 10px",
                              border: `1px solid ${T.lineStrong}`,
                              fontSize: 12,
                            }}
                          />
                          <button
                            onClick={() => handleReply(p._id)}
                            disabled={
                              !(replyInput[p._id] || "").trim() ||
                              !!replySubmitting[p._id]
                            }
                            className="t-btn"
                            style={{
                              padding: "8px 14px",
                              background:
                                (replyInput[p._id] || "").trim() &&
                                !replySubmitting[p._id]
                                  ? T.gradPrimary
                                  : T.line,
                              color: "#fff",
                              border: "none",
                              borderRadius: 10,
                              fontFamily: "inherit",
                              fontSize: 12,
                              fontWeight: 700,
                              cursor:
                                (replyInput[p._id] || "").trim() &&
                                !replySubmitting[p._id]
                                  ? "pointer"
                                  : "not-allowed",
                              boxShadow:
                                (replyInput[p._id] || "").trim() &&
                                !replySubmitting[p._id]
                                  ? T.shadowBtn
                                  : "none",
                              transition: T.ease,
                            }}
                          >
                            {replySubmitting[p._id] ? "送信中..." : "送信"}
                          </button>
                        </div>
                      </>
                    ) : detailError[p._id] ? (
                      // web#28: 失败态 — 展示错误 + 再試行，与「読み込み中」区分
                      <div
                        style={{
                          padding: "12px 0",
                          color: T.danger,
                          fontSize: 12,
                        }}
                      >
                        <div style={{ marginBottom: 8 }}>
                          詳細の取得に失敗しました
                          {detailError[p._id]
                            ? `（${detailError[p._id]}）`
                            : ""}
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            fetchDetail(p._id);
                          }}
                          className="t-btn"
                          style={{
                            ...S.btnGhost,
                            padding: "6px 12px",
                            color: T.cobalt,
                            fontSize: 12,
                          }}
                        >
                          再試行
                        </button>
                      </div>
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
      {composing && (
        <ComposeNoticeModal
          onClose={() => setComposing(false)}
          onSubmit={handlePost}
        />
      )}
      {/* 编辑 modal — 共用 NoticeModal，初始值来自 editTarget */}
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

type NoticeSubmitInput = {
  title: string;
  body: string;
  scope: AnnouncementScope;
  notify_students: boolean;
};

// 公告新建/编辑共用 modal（Compose / Edit 只传不同 props）
function NoticeModal({
  heading,
  initial,
  showNotifyCheckbox,
  defaultNotify = false,
  titlePlaceholder,
  bodyPlaceholder,
  submitLabel,
  submittingLabel,
  fallbackError,
  onClose,
  onSubmit,
}: {
  heading: string;
  initial: { title: string; body: string; scope: AnnouncementScope };
  showNotifyCheckbox: boolean;
  defaultNotify?: boolean;
  titlePlaceholder?: string;
  bodyPlaceholder?: string;
  submitLabel: string;
  submittingLabel: string;
  fallbackError: string;
  onClose: () => void;
  onSubmit: (input: NoticeSubmitInput) => Promise<void>;
}) {
  const T = RYO;
  const [title, setTitle] = React.useState(initial.title || "");
  const [body, setBody] = React.useState(initial.body || "");
  const [scope, setScope] = React.useState<AnnouncementScope>(
    initial.scope || "all",
  );
  const [notifyStudents, setNotifyStudents] = React.useState(
    showNotifyCheckbox ? defaultNotify : false,
  );
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
        notify_students: showNotifyCheckbox ? notifyStudents : false,
      });
    } catch (e) {
      setErrorMsg((e as Error)?.message || fallbackError);
      setSubmitting(false);
    }
  };
  return (
    <div
      onClick={onClose}
      style={{
        ...S.backdrop,
        zIndex: 90,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="t-scale-in"
        style={{
          ...S.modal,
          width: 680,
          maxWidth: "100%",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
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
          <div style={{ fontSize: 15, fontWeight: 700 }}>{heading}</div>
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
            overflowY: "auto",
            flex: 1,
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
              placeholder={titlePlaceholder}
              className="t-input"
              style={{
                ...S.input,
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                fontSize: 14,
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
              placeholder={bodyPlaceholder}
              rows={12}
              className="t-input"
              style={{
                ...S.input,
                width: "100%",
                padding: "10px 12px",
                border: `1px solid ${T.lineStrong}`,
                fontSize: 13,
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
                  className="t-btn"
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: scope === o.k ? T.cobalt : T.surface,
                    color: scope === o.k ? "#fff" : T.ink2,
                    border: `1px solid ${scope === o.k ? T.cobalt : T.lineStrong}`,
                    borderRadius: 10,
                    fontSize: 12,
                    fontWeight: 600,
                    fontFamily: "inherit",
                    cursor: "pointer",
                    transition: T.ease,
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
                borderRadius: 10,
                fontSize: 12,
              }}
            >
              {errorMsg}
            </div>
          )}
          {showNotifyCheckbox && (
            <>
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 13,
                  color: T.ink,
                  cursor: "pointer",
                  margin: "4px 0 0",
                }}
              >
                <input
                  type="checkbox"
                  checked={notifyStudents}
                  onChange={(e) => setNotifyStudents(e.target.checked)}
                  style={{ width: 16, height: 16, cursor: "pointer" }}
                />
                寮生に通知する（アプリの通知センターに表示）
              </label>
              {notifyStudents && (
                <div style={{ fontSize: 11, color: T.ink3 }}>
                  投稿後、対象寮生の iOS・Android
                  アプリにプッシュ通知が送信されます。
                </div>
              )}
            </>
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
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "8px 16px",
              cursor: submitting ? "not-allowed" : "pointer",
            }}
          >
            キャンセル
          </button>
          <button
            onClick={handleSubmit}
            disabled={!title.trim() || submitting}
            className="t-btn"
            style={{
              padding: "8px 16px",
              background: !title.trim() || submitting ? T.line : T.gradPrimary,
              color: "#fff",
              border: "none",
              borderRadius: 12,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: !title.trim() || submitting ? "not-allowed" : "pointer",
              boxShadow: !title.trim() || submitting ? "none" : T.shadowBtn,
              transition: T.ease,
            }}
          >
            {submitting ? submittingLabel : submitLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// 公告编辑 modal — 共用 NoticeModal；编辑不显示通知勾选（后端忽略 notify_students）
function EditNoticeModal({
  initial,
  onClose,
  onSubmit,
}: {
  initial: { title: string; body: string; scope: AnnouncementScope };
  onClose: () => void;
  onSubmit: (input: NoticeSubmitInput) => Promise<void>;
}) {
  return (
    <NoticeModal
      heading="お知らせを編集"
      initial={initial}
      showNotifyCheckbox={false}
      submitLabel="保存"
      submittingLabel="保存中..."
      fallbackError="保存に失敗しました"
      onClose={onClose}
      onSubmit={onSubmit}
    />
  );
}

// 行事カレンダー — 真后端数据版（5-30 改造）
// 后端字段: id / title / category / event_date / start_at? / end_at? / description?
// 权限：按 canManage(C_EVENT) 显隐增删改按钮
function EventCalendar({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  // 按权限组判（与后端 events.py require_permission(C_EVENT, MANAGE) 同一真值），不再按
  // 职位白名单。原来用 ["寮務部長","寮務課長","管理係"] 白名单，导致后端授予行事管理权的
  // 其他 role（寮監/学習担当 等）看不到编辑入口（TW-001）。teacher 无 permission_group 时
  // canManage 内部按职位回退。
  const canEdit = canManage(teacher, C_EVENT);

  // 复审：日历基准日用 JST（Asia/Tokyo）——非 JST 浏览器月末/跨日时，初始月与「今日」高亮
  // 及 loadEvents 的 from/to 区间都不再错位（cursor/todayKey 都由此派生）。
  const jstYmd = new Date().toLocaleDateString("en-CA", {
    timeZone: "Asia/Tokyo",
  });
  const [jstY, jstMo, jstD] = jstYmd.split("-").map(Number);
  const today = new Date(jstY, jstMo - 1, jstD);
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

  // 只拉 cursor 所在当前月（from=月初 to=月末）
  const loadEvents = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    const y = cursor.getFullYear();
    const m = cursor.getMonth();
    const from = `${y}-${String(m + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(y, m + 1, 0).getDate();
    const to = `${y}-${String(m + 1).padStart(2, "0")}-${lastDay}`;
    setLoadingEvt(true);
    setEvtError(null);
    api
      .listEvents(authToken, from, to)
      .then((data) => {
        if (cancelled) return;
        setList((data.items || []).map(adapt));
      })
      .catch((e) => {
        if (cancelled) return;
        setEvtError(e.message || "行事の取得に失敗しました");
      })
      .finally(() => {
        if (!cancelled) setLoadingEvt(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken, cursor]);

  React.useEffect(() => {
    return loadEvents();
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
  // web#29: 翻月时 selected 跟随新月，避免右栏仍指旧月日期而 list 已换新月 → 空提示假象
  const navMonth = (delta: number) => {
    const next = new Date(y, m + delta, 1);
    setCursor(next);
    const ny = next.getFullYear();
    const nm = next.getMonth();
    const todayInMonth = today.getFullYear() === ny && today.getMonth() === nm;
    setSelected(
      todayInMonth ? todayKey : `${ny}-${String(nm + 1).padStart(2, "0")}-01`,
    );
  };

  // 新增：提交到后端后刷新列表
  const handleCreate = async (formData: EventFormData) => {
    if (!authToken) return;
    await api.createEvent(toEventCreateIn(formData), authToken);
    setComposing(false);
    setSelected(formData.event_date);
    // web#29: 新建行事若不在当前 cursor 月，先移 cursor 到该月（useEffect 会重拉）；同月则直接 loadEvents
    const [ey, em] = formData.event_date.split("-").map(Number);
    if (ey !== y || em - 1 !== m) {
      setCursor(new Date(ey, em - 1, 1));
    } else {
      loadEvents();
    }
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
    // 空值发 null（不是 undefined）：undefined 会被 JSON.stringify 丢掉、PATCH 请求体里
    // 没这个字段 → 后端 exclude_unset 当「不动」，老师清空可选字段保存后旧值还在（TW-014）。
    // 发 null 让后端 PATCH 落实清空；create 端点对 null 也正常（字段 nullable）。
    start_at: fd.start_at ?? null,
    end_at: fd.end_at ?? null,
    description: fd.description ?? null,
    notify_students: fd.notify_students,
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
          ...S.card,
          padding: "18px 20px",
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
            className="t-btn"
            style={{
              width: 32,
              height: 32,
              border: `1px solid ${T.line}`,
              background: T.surface,
              borderRadius: 10,
              cursor: "pointer",
              fontSize: 14,
              color: T.ink2,
              fontFamily: "inherit",
              transition: T.ease,
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
            className="t-btn"
            style={{
              width: 32,
              height: 32,
              border: `1px solid ${T.line}`,
              background: T.surface,
              borderRadius: 10,
              cursor: "pointer",
              fontSize: 14,
              color: T.ink2,
              fontFamily: "inherit",
              transition: T.ease,
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
                  borderRadius: 10,
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: isSel || isToday ? 700 : 500,
                  position: "relative",
                  transition: T.ease,
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
              background: T.dangerSoft,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 10,
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
              className="t-btn"
              style={{
                ...S.btnGhost,
                padding: "3px 10px",
                fontSize: 11,
                color: T.danger,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 8,
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
              ...S.pill,
              fontSize: 11,
              color: T.ink3,
              background: T.surfaceAlt,
              border: `1px solid ${T.line}`,
              padding: "3px 9px",
              fontFamily: T.mono,
            }}
          >
            {selEvents.length}件
          </span>
          {canEdit && (
            <button
              onClick={() => setComposing(true)}
              className="t-btn"
              style={{
                ...S.btnPrimary,
                padding: "5px 12px",
                fontSize: 11,
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
              borderRadius: 16,
            }}
          >
            この日に予定はありません
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {selEvents.map((e, i) => (
              <div
                key={e._id}
                className="t-fade-up"
                style={{
                  ...S.card,
                  padding: "12px 14px",
                  ...(i < 12 ? { animationDelay: `${i * 40}ms` } : null),
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
                        className="t-btn"
                        style={{
                          ...S.btnSmall,
                          padding: "3px 9px",
                          color: T.ink2,
                          border: `1px solid ${T.lineStrong}`,
                          fontSize: 11,
                        }}
                      >
                        編集
                      </button>
                      <button
                        onClick={() => handleDelete(e._id)}
                        className="t-btn"
                        style={{
                          ...S.btnSmall,
                          padding: "3px 9px",
                          color: T.danger,
                          border: `1px solid ${T.dangerBorder}`,
                          fontSize: 11,
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
  // 新建默认勾选 / 编辑默认不勾（改错字不该惊动全员，要重新通知再手动勾）
  const [notifyStudents, setNotifyStudents] = React.useState(!initial);
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
        notify_students: notifyStudents,
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
          className="t-input"
          style={inputStyle}
        />
      </Field>
      <Field T={T} label="カテゴリー *">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="t-input"
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
          className="t-input"
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
            className="t-input"
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="終了時刻（任意）">
          <input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            className="t-input"
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
          className="t-input"
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
            borderRadius: 10,
            fontSize: 12,
          }}
        >
          {errMsg}
        </div>
      )}
      {/* 通知开关只在「新建」出现 —— 编辑路径后端不碰 notify_students（§7.13.1 修订 2026-06-16），
          显示个无效的勾选框会误导，故编辑时隐藏 */}
      {!initial && (
        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 13,
            color: T.ink,
            cursor: "pointer",
            margin: "4px 0 12px",
          }}
        >
          <input
            type="checkbox"
            checked={notifyStudents}
            onChange={(e) => setNotifyStudents(e.target.checked)}
            style={{ width: 16, height: 16, cursor: "pointer" }}
          />
          寮生に通知する（アプリの通知センターに表示）
        </label>
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

// 巴士时刻表独立页 — 6-15 从「お知らせ・バス」拆出来、单独成左栏一项。
export function BusPage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  return (
    <div style={{ padding: "28px 32px" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>バス時刻表</h1>
      <div style={{ marginTop: 18 }}>
        <BusSchedulePanel teacher={teacher} authToken={authToken} />
      </div>
    </div>
  );
}

// 巴士时刻表面板 — 真后端数据版（5-30 改造）
// 后端字段: id / kind / name / direction / schedule_at / arrival_at? / visible_to / note? / purpose? / deprecated
// 权限：按 canManage(C_BUS) 显隐增删改
export function BusSchedulePanel({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  // 按权限组判（与后端 bus_routes.py require_permission(C_BUS, MANAGE) 同一真值），不再按
  // 职位白名单，让后端授予巴士管理权的所有 role 都能看到编辑入口（TW-001）。
  const canEdit = canManage(teacher, C_BUS);

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
    direction: fd.direction,
    schedule_at: fd.schedule_at ?? "",
    // 同 toEventCreateIn：空值发 null 让编辑可清空（TW-014），undefined 会被 JSON 丢掉。
    arrival_at: fd.arrival_at ?? null,
    visible_to: fd.visible_to,
    note: fd.note ?? null,
    purpose: fd.purpose ?? null,
    notify_students: fd.notify_students,
  });

  // 时刻格式化：ISO → HH:MM
  const fmtTime = (iso: string | null) => (iso ? iso.slice(11, 16) : "—");

  const RouteRow = ({ r, index = 0 }: { r: BusRoute; index?: number }) => (
    <div
      className="t-fade-up"
      style={{
        display: "grid",
        gridTemplateColumns: "56px 1fr auto auto",
        alignItems: "center",
        gap: 10,
        padding: "10px 14px",
        ...S.card,
        marginBottom: 6,
        ...(index < 12 ? { animationDelay: `${index * 40}ms` } : null),
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
            className="t-btn"
            style={{
              ...S.btnSmall,
              padding: "3px 9px",
              color: T.ink2,
              border: `1px solid ${T.lineStrong}`,
              fontSize: 11,
            }}
          >
            編集
          </button>
          <button
            onClick={() => handleDeprecate(r.id)}
            className="t-btn"
            style={{
              ...S.btnSmall,
              padding: "3px 9px",
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              fontSize: 11,
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
        {items.map((r, i) => (
          <RouteRow key={r.id} r={r} index={i} />
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
              className="t-btn"
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
                transition: T.ease,
              }}
            >
              {l}
            </button>
          ))}
        </div>
        {canEdit && (
          <button
            onClick={() => setComposing("new")}
            className="t-btn"
            style={{
              ...S.btnPrimary,
              padding: "7px 14px",
              fontSize: 12,
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
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
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
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "3px 10px",
              fontSize: 11,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
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
            borderRadius: 12,
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

  // 6-15: 表单去掉「種別」「便名」两栏 —— 新便后端默认存 dorm_special、便名用方向回填。
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
  // 「用途・説明」栏 —— 学生 iOS 端右上角展示这趟班车干嘛用的。
  const [purpose, setPurpose] = React.useState(
    initial ? initial.purpose || "" : "",
  );
  // 新建默认勾选 / 编辑默认不勾（改错字不该惊动全员，要重新通知再手动勾）
  const [notifyStudents, setNotifyStudents] = React.useState(!initial);
  const [submitting, setSubmitting] = React.useState(false);
  const [errMsg, setErrMsg] = React.useState("");

  const toIso = (d: string, t: string) => (d && t ? `${d}T${t}:00` : null);
  const valid = direction.trim() && schedDate && schedTime;

  const submit = async () => {
    if (!valid || submitting) return;
    setSubmitting(true);
    setErrMsg("");
    try {
      await onSubmit({
        direction: direction.trim(),
        schedule_at: toIso(schedDate, schedTime),
        arrival_at: toIso(arrDate, arrTime),
        visible_to: visibleTo,
        note: note.trim() || null,
        purpose: purpose.trim() || null,
        notify_students: notifyStudents,
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
      <Field T={T} label="方向（区間）*">
        <input
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          placeholder="例：岡山駅西口 → 高校棟"
          className="t-input"
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
            className="t-input"
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="出発時刻 *">
          <input
            type="time"
            value={schedTime}
            onChange={(e) => setSchedTime(e.target.value)}
            className="t-input"
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
            className="t-input"
            style={inputStyle}
          />
        </Field>
        <Field T={T} label="到着時刻（任意）">
          <input
            type="time"
            value={arrTime}
            onChange={(e) => setArrTime(e.target.value)}
            className="t-input"
            style={inputStyle}
          />
        </Field>
      </div>
      <Field T={T} label="対象">
        <select
          value={visibleTo}
          onChange={(e) => setVisibleTo(e.target.value)}
          className="t-input"
          style={inputStyle}
        >
          <option value="all">全員</option>
          <option value="dorm_only">寮生のみ</option>
          <option value="men">男子寮</option>
          <option value="women">女子寮</option>
        </select>
      </Field>
      <Field T={T} label="用途・説明（寮生に表示）">
        <textarea
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          rows={2}
          placeholder="例：GW の外泊・帰省・買い物に使える臨時便です。"
          className="t-input"
          style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }}
        />
      </Field>
      <Field T={T} label="備考（任意）">
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          placeholder="例：部活対応 / 雨天中止"
          className="t-input"
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
            borderRadius: 10,
            fontSize: 12,
          }}
        >
          {errMsg}
        </div>
      )}
      {/* 通知开关只在「新建」出现 —— 编辑路径后端不碰 notify_students（§7.13.1 修订 2026-06-16），
          显示个无效的勾选框会误导，故编辑时隐藏 */}
      {!initial && (
        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 13,
            color: T.ink,
            cursor: "pointer",
            margin: "4px 0 12px",
          }}
        >
          <input
            type="checkbox"
            checked={notifyStudents}
            onChange={(e) => setNotifyStudents(e.target.checked)}
            style={{ width: 16, height: 16, cursor: "pointer" }}
          />
          寮生に通知する（アプリの通知センターに表示）
        </label>
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

// 公告新建 modal — 共用 NoticeModal；默认勾选通知学生
function ComposeNoticeModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (input: NoticeSubmitInput) => Promise<void>;
}) {
  return (
    <NoticeModal
      heading="新規お知らせ投稿"
      initial={{ title: "", body: "", scope: "all" }}
      showNotifyCheckbox
      defaultNotify
      titlePlaceholder="例：今週金曜の清掃検査について"
      bodyPlaceholder="詳細をここに記入..."
      submitLabel="投稿"
      submittingLabel="送信中..."
      fallbackError="お知らせの送信に失敗しました。サーバーに接続できないか、権限が不足している可能性があります。しばらくしてから再度お試しください。"
      onClose={onClose}
      onSubmit={onSubmit}
    />
  );
}
