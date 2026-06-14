import React from "react";
import { RYO } from "../theme";

// 源 index.html 24086-24960（pages-records-search-etc 块）。
// 界面原样搬：JSX 结构 + 所有内联 style 一字不改，仅把作用域引用从 window.RYO 改成 import 的 RYO。
//
// ⚠️ 类型说明：本组件访问 teacher.dorm（字符串 "men"/"women"）+ teacher.name，
// 这是旧单文件里的 teacher 形状，跟 ../api/types 的 TeacherProfile（assigned_dorm: number | null，无 dorm 字段）不一致。
// 为了「界面 + 逻辑 100% 冻结」不改 JSX，这里给 props 用按源实际用法推出的 inline 类型，
// 不强行套 TeacherProfile（否则 teacher.dorm 会 tsc 报错）。迁移收口时需把 teacher 形状对齐统一。

// 掲示板/リクエスト曲 投稿的本地 UI 形状（posts 初始为空数组、无后端接线，字段按 JSX 访问推出）
type CommunityPost = {
  id: string | number;
  cat: string; // "board" | "song"
  author?: string;
  room?: string;
  date?: string;
  time?: string;
  title?: string;
  body?: string;
  likes?: number;
  comments?: number;
  pinned?: boolean;
  deleted?: boolean;
  timeSlot?: string; // "morning" | "evening"
  songStatus?: string; // "pending" | "approved" | "rejected"
  decidedAt?: string;
  decidedBy?: string;
};

export function CommunityPage({
  teacher,
}: {
  teacher: { dorm?: string; name?: string } | null;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("song");
  const [posts, setPosts] = React.useState<CommunityPost[]>([]); // A6/codex: 掲示板 无后端，去假数据空状态
  const [filter, setFilter] = React.useState("all");
  const [slotFilter, setSlotFilter] = React.useState("all"); // song tab 専用: all / morning / evening

  const [songFilter, setSongFilter] = React.useState("pending"); // song tab 専用: pending / approved / rejected / all
  const [dormFilter, setDormFilter] = React.useState(
    teacher && teacher.dorm ? teacher.dorm : "men",
  ); // song tab 専用: men / women / all（默认是负责的寮）
  const dormOf = (p: CommunityPost) =>
    p && p.room && p.room.charAt(0) === "M" ? "men" : "women";

  const handleDelete = (id: string | number) => {
    if (confirm("この投稿を削除しますか？学生のアプリからも非表示になります。"))
      setPosts(posts.map((p) => (p.id === id ? { ...p, deleted: true } : p)));
  };
  const handlePin = (id: string | number) =>
    setPosts(posts.map((p) => (p.id === id ? { ...p, pinned: !p.pinned } : p)));
  const handleSongDecision = (id: string | number, decision: string) =>
    setPosts(
      posts.map((p) =>
        p.id === id
          ? {
              ...p,
              songStatus: decision,
              decidedAt: new Date().toTimeString().slice(0, 5),
              decidedBy: teacher ? `${teacher.name} 先生` : "担当 先生",
            }
          : p,
      ),
    );

  const catPosts = posts.filter((p) => p.cat === tab && !p.deleted);
  let visible = catPosts;
  if (filter === "pinned") visible = catPosts.filter((p) => p.pinned);
  if (tab === "song" && slotFilter !== "all")
    visible = visible.filter((p) => p.timeSlot === slotFilter);
  if (tab === "song" && songFilter !== "all") {
    visible = visible.filter((p) => (p.songStatus || "pending") === songFilter);
  }
  if (tab === "song" && dormFilter !== "all") {
    visible = visible.filter((p) => dormOf(p) === dormFilter);
  }

  // リクエスト曲 按 古い順（投稿顺、升序）= 放送队列顺。置顶在上部。其他 tab 照旧 置顶在上部 + 降序。
  if (tab === "song") {
    visible = [...visible].sort((a, b) => {
      const pinDiff = (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0);
      if (pinDiff !== 0) return pinDiff;
      const aKey = `${a.date} ${a.time || ""}`;
      const bKey = `${b.date} ${b.time || ""}`;
      return aKey.localeCompare(bKey); // 升序 = 古い順 = 队列顺
    });
  } else {
    visible = [...visible].sort(
      (a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0),
    );
  }

  // 给已承認的队列分配序号 #n（按 寮 × 朝/晩 的组合各自 古い順 = 提交顺）
  const approvedOrder: Record<string | number, number> = {};
  ["men", "women"].forEach((d) => {
    ["morning", "evening"].forEach((slot) => {
      posts
        .filter(
          (p) =>
            p.cat === "song" &&
            !p.deleted &&
            p.songStatus === "approved" &&
            p.timeSlot === slot &&
            dormOf(p) === d,
        )
        .sort((a, b) =>
          `${a.date} ${a.time || ""}`.localeCompare(
            `${b.date} ${b.time || ""}`,
          ),
        )
        .forEach((p, i) => {
          approvedOrder[p.id] = i + 1;
        });
    });
  });

  const stats = {
    total: posts.filter((p) => !p.deleted).length,
    today: posts.filter((p) => !p.deleted && p.date === "04-22").length,
    deleted: posts.filter((p) => p.deleted).length,
  };

  const tabs: [string, string, string][] = [
    ["song", "リクエスト曲", "寮内 BGM リクエスト · 提出順に再生"],
    // itsuki 拍板删「掲示板」残留 tab — system_features §7.14（4-29 已拍板砍学生留言板 + 社区整体），保留「リクエスト曲」（点歌）
    // 「匿名建議」tab 此前已砍
  ];

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 600,
        }}
      >
        コミュニティ管理
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
          margin: "4px 0 20px",
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>
          コミュニティ管理
        </h1>
        <div style={{ fontSize: 11, color: T.ink3 }}>
          担当寮：
          <b style={{ color: T.ink }}>
            {teacher && teacher.dorm === "men" ? "男子寮" : "女子寮"}
          </b>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 12,
          marginBottom: 20,
        }}
      >
        <StatCard
          label="総投稿"
          value={stats.total}
          note="アクティブ"
          color={T.ink}
        />
        <StatCard
          label="本日投稿"
          value={stats.today}
          note="04-22"
          color={T.cobalt}
        />
        <StatCard
          label="削除済み"
          value={stats.deleted}
          note="今月累計"
          color={T.ink3}
        />
      </div>

      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          marginBottom: 14,
          flexWrap: "wrap",
        }}
      >
        {tabs.map(([k, l]) => {
          const count = posts.filter((p) => p.cat === k && !p.deleted).length;
          return (
            <button
              key={k}
              onClick={() => {
                setTab(k);
                setFilter("all");
              }}
              style={{
                padding: "10px 16px",
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
                position: "relative",
              }}
            >
              {l}{" "}
              <span style={{ color: T.ink3, fontSize: 11, fontWeight: 500 }}>
                ({count})
              </span>
            </button>
          );
        })}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 14,
          fontSize: 12,
          color: T.ink2,
          flexWrap: "wrap",
        }}
      >
        <span style={{ color: T.ink3 }}>
          {tabs.find((t) => t[0] === tab)![2]} ·
        </span>
        {[
          ["all", "全て"],
          ["pinned", "ピン留め"],
        ].map(([k, l]) => (
          <button
            key={k}
            onClick={() => setFilter(k)}
            style={{
              padding: "4px 10px",
              background: filter === k ? T.cobaltSoft : T.surface,
              color: filter === k ? T.cobaltDeep : T.ink3,
              border: `1px solid ${filter === k ? T.cobalt : T.lineStrong}`,
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
        {tab === "song" && (
          <>
            <span style={{ color: T.ink3, marginLeft: 6 }}>寮 ·</span>
            {[
              ["men", "男子寮"],
              ["women", "女子寮"],
              ["all", "両方"],
            ].map(([k, l]) => {
              const n = posts.filter(
                (p) =>
                  p.cat === "song" &&
                  !p.deleted &&
                  (k === "all" || dormOf(p) === k),
              ).length;
              return (
                <button
                  key={k}
                  onClick={() => setDormFilter(k)}
                  style={{
                    padding: "4px 10px",
                    background: dormFilter === k ? T.cobaltSoft : T.surface,
                    color: dormFilter === k ? T.cobaltDeep : T.ink3,
                    border: `1px solid ${dormFilter === k ? T.cobalt : T.lineStrong}`,
                    borderRadius: 999,
                    fontFamily: "inherit",
                    fontSize: 11,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  {l}{" "}
                  <span style={{ fontFamily: T.mono, opacity: 0.7 }}>{n}</span>
                </button>
              );
            })}
            <span style={{ color: T.ink3, marginLeft: 6 }}>放送枠 ·</span>
            {[
              ["all", "両方"],
              ["morning", "朝 ☀"],
              ["evening", "晩 🌙"],
            ].map(([k, l]) => (
              <button
                key={k}
                onClick={() => setSlotFilter(k)}
                style={{
                  padding: "4px 10px",
                  background: slotFilter === k ? T.cobaltSoft : T.surface,
                  color: slotFilter === k ? T.cobaltDeep : T.ink3,
                  border: `1px solid ${slotFilter === k ? T.cobalt : T.lineStrong}`,
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
            <span style={{ color: T.ink3, marginLeft: 6 }}>審査 ·</span>
            {[
              ["pending", "未対応"],
              ["approved", "承認"],
              ["rejected", "拒否"],
              ["all", "全て"],
            ].map(([k, l]) => {
              const n = posts.filter(
                (p) =>
                  p.cat === "song" &&
                  !p.deleted &&
                  (k === "all" || (p.songStatus || "pending") === k),
              ).length;
              return (
                <button
                  key={k}
                  onClick={() => setSongFilter(k)}
                  style={{
                    padding: "4px 10px",
                    background: songFilter === k ? T.cobaltSoft : T.surface,
                    color: songFilter === k ? T.cobaltDeep : T.ink3,
                    border: `1px solid ${songFilter === k ? T.cobalt : T.lineStrong}`,
                    borderRadius: 999,
                    fontFamily: "inherit",
                    fontSize: 11,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  {l}{" "}
                  <span style={{ fontFamily: T.mono, opacity: 0.7 }}>{n}</span>
                </button>
              );
            })}
          </>
        )}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
          gap: 12,
        }}
      >
        {visible.map((p) => (
          <PostCard
            key={p.id}
            post={p}
            onDelete={handleDelete}
            onPin={handlePin}
            onSongDecision={handleSongDecision}
            queueNo={approvedOrder[p.id]}
          />
        ))}
        {visible.length === 0 && (
          <div
            style={{
              gridColumn: "1 / -1",
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
              background: T.surface,
              border: `1px dashed ${T.lineStrong}`,
              borderRadius: 12,
            }}
          >
            このカテゴリーに投稿はありません
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  note,
  color,
  onClick,
}: {
  label: string;
  value: number;
  note: string;
  color: string;
  onClick?: (() => void) | null;
}) {
  const T = RYO;
  return (
    <div
      onClick={onClick || undefined}
      style={{
        padding: "14px 16px",
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 10,
        cursor: onClick ? "pointer" : "default",
        transition: "border-color .15s",
      }}
    >
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.5,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 26,
          fontWeight: 700,
          color,
          fontFamily: T.mono,
          margin: "4px 0",
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: 11, color: T.ink3 }}>{note}</div>
    </div>
  );
}

function PostCard({
  post,
  onDelete,
  onPin,
  onSongDecision,
  queueNo,
}: {
  post: CommunityPost;
  onDelete: (id: string | number) => void;
  onPin: (id: string | number) => void;
  onSongDecision: (id: string | number, decision: string) => void;
  queueNo?: number;
}) {
  const T = RYO;
  // 5-27 砍 anon tab — cat 已无 "anon" 值，isAnon 逻辑全删
  const isSong = post.cat === "song";
  const avatarColor = hashColor(post.author || "A", T);
  const initial = (post.author || "").charAt(0) || "・";
  const slotLabel =
    isSong && post.timeSlot === "morning"
      ? "朝 ☀"
      : isSong && post.timeSlot === "evening"
        ? "晩 🌙"
        : null;
  const songStatus = isSong ? post.songStatus || "pending" : null;
  const statusMap: Record<
    string,
    { label: string; fg: string; bg: string; bd: string }
  > = {
    pending: {
      label: "未対応",
      fg: T.warn,
      bg: T.warnSoft,
      bd: T.warnBorder,
    },
    approved: { label: "承認", fg: T.ok, bg: T.okSoft, bd: T.okBorder },
    rejected: {
      label: "拒否",
      fg: T.danger,
      bg: T.dangerSoft,
      bd: T.dangerBorder,
    },
  };
  const st = songStatus && statusMap[songStatus];
  const borderColor = post.pinned
    ? T.cobalt
    : songStatus === "approved"
      ? T.okBorder
      : songStatus === "rejected"
        ? T.dangerBorder
        : T.line;
  return (
    <div
      style={{
        padding: 14,
        background: T.surface,
        border: `1px solid ${borderColor}`,
        borderRadius: 12,
        display: "flex",
        flexDirection: "column",
        gap: 10,
        boxShadow: post.pinned ? T.shadow1 : "none",
        opacity: songStatus === "rejected" ? 0.7 : 1,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        {isSong && songStatus === "approved" && queueNo && (
          <div
            title={`放送キュー #${queueNo}`}
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: T.okSoft,
              color: T.ok,
              border: `1.5px solid ${T.okBorder}`,
              fontWeight: 700,
              fontSize: 14,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
              fontFamily: T.mono,
            }}
          >
            #{queueNo}
          </div>
        )}
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: avatarColor,
            color: "#fff",
            fontWeight: 700,
            fontSize: 14,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {initial}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: T.ink }}>
            {post.author}
            {post.room && (
              <span
                style={{
                  color: T.ink3,
                  fontWeight: 500,
                  marginLeft: 6,
                  fontSize: 11,
                }}
              >
                · {post.room}
              </span>
            )}
          </div>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              fontFamily: T.mono,
              marginTop: 2,
            }}
          >
            {post.date} {post.time}
          </div>
        </div>
        <div
          style={{
            display: "flex",
            gap: 4,
            alignItems: "center",
            flexWrap: "wrap",
            justifyContent: "flex-end",
          }}
        >
          {slotLabel && (
            <span
              style={{
                fontSize: 10,
                color: T.cobaltDeep,
                background: T.cobaltSoft,
                padding: "2px 7px",
                borderRadius: 4,
                fontWeight: 700,
                border: `1px solid ${T.cobalt}33`,
                whiteSpace: "nowrap",
              }}
            >
              {slotLabel}
            </span>
          )}
          {st && (
            <span
              style={{
                fontSize: 10,
                color: st.fg,
                background: st.bg,
                padding: "2px 7px",
                borderRadius: 4,
                fontWeight: 700,
                border: `1px solid ${st.bd}`,
                whiteSpace: "nowrap",
              }}
            >
              {st.label}
            </span>
          )}
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
        </div>
      </div>

      {post.title && (
        <div style={{ fontSize: 14, fontWeight: 700, color: T.ink }}>
          {post.title}
        </div>
      )}
      {post.body && (
        <div
          style={{
            fontSize: 13,
            lineHeight: 1.6,
            color: T.ink2,
            whiteSpace: "pre-wrap",
          }}
        >
          {post.body}
        </div>
      )}
      {isSong && post.decidedBy && (
        <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>
          {songStatus === "approved" ? "承認" : "拒否"}：{post.decidedBy} ·{" "}
          {post.decidedAt}
        </div>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          paddingTop: 6,
          borderTop: `1px solid ${T.line}`,
          fontSize: 11,
          color: T.ink3,
          flexWrap: "wrap",
        }}
      >
        <span>♥ {post.likes || 0}</span>
        <span>💬 {post.comments || 0}</span>
        <div style={{ flex: 1 }} />
        {isSong && songStatus === "pending" && (
          <>
            <button
              onClick={() =>
                onSongDecision && onSongDecision(post.id, "rejected")
              }
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
              拒否
            </button>
            <button
              onClick={() =>
                onSongDecision && onSongDecision(post.id, "approved")
              }
              style={{
                padding: "4px 10px",
                background: T.ok,
                color: "#fff",
                border: `1px solid ${T.ok}`,
                borderRadius: 6,
                fontFamily: "inherit",
                fontSize: 11,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              承認
            </button>
          </>
        )}
        {isSong && songStatus !== "pending" && (
          <button
            onClick={() => onSongDecision && onSongDecision(post.id, "pending")}
            style={{
              padding: "4px 10px",
              background: T.surface,
              color: T.ink3,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 6,
              fontFamily: "inherit",
              fontSize: 11,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            審査取消
          </button>
        )}
        <button
          onClick={() => onPin(post.id)}
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
          onClick={() => onDelete(post.id)}
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
    </div>
  );
}

// 头像底色：把作者名 hash 成调色板里的一个固定颜色（私有助手，仅 PostCard 用，旧块本地定义，shared/utils/theme 里没有）
function hashColor(s: string, T: typeof RYO) {
  const palette = [
    T.cobalt,
    T.ok,
    T.warn,
    T.danger,
    "#7e57c2",
    "#0097a7",
    "#d84315",
    "#5d4037",
  ];
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return palette[h % palette.length];
}

function Row({ date, msg }: { date: string; msg: string }) {
  const T = RYO;
  return (
    <div
      style={{
        display: "flex",
        gap: 14,
        padding: "12px 14px",
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 10,
        marginBottom: 8,
        fontSize: 13,
      }}
    >
      <span style={{ fontFamily: T.mono, color: T.ink3, minWidth: 100 }}>
        {date}
      </span>
      <span>{msg}</span>
    </div>
  );
}
