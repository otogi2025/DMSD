import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { NotificationItem } from "../api/types";

// 通知中心（UI「通知センター」）— 阶段1（itsuki 2026-06-13）。
// 2 张卡用现成接口算真数字（待审申请 / 警告人数）；最近通知流来自后端
// GET /notifications/feed（取时扫现有事件同步）；点一条标记已读 +「すべて既読にする」按钮。
// 通報卡已删（通報功能 2026-06-13 彻底删除）。

// 当月 YYYY-MM（JST，给扣分 ranking 接口）— web#102：不用浏览器本地 getFullYear/getMonth
function currentMonth(): string {
  const parts = new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
  }).formatToParts(new Date());
  const y = parts.find((p) => p.type === "year")?.value ?? "";
  const m = parts.find((p) => p.type === "month")?.value ?? "";
  return `${y}-${m}`;
}

// event_at（ISO）→ JST 本地化时刻 — web#101
function formatTime(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("ja-JP", {
    timeZone: "Asia/Tokyo",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// category → 标签 + 颜色
function categoryMeta(category: string, T: typeof RYO) {
  switch (category) {
    case "application":
      return { label: "申請", color: T.cobalt };
    case "demerit":
      return { label: "減点", color: T.danger };
    case "rollcall_report":
      return { label: "点呼報告", color: T.warn };
    // 阶段2 新增 8 类申请来源
    case "outing":
      return { label: "外出", color: T.cobalt };
    case "study_absence":
      return { label: "夜学習欠席", color: T.cobalt };
    case "study_online":
      return { label: "オンライン学習", color: T.cobalt };
    case "dorm_event":
      return { label: "行事企画", color: T.cobalt };
    case "fridge":
      return { label: "冷蔵庫", color: T.ink2 };
    case "item":
      return { label: "物品所持", color: T.ink2 };
    case "demerit_alert":
      return { label: "減点警告", color: T.warn };
    case "misc":
      return { label: "雑項", color: T.ink2 };
    default:
      return { label: "通知", color: T.ink3 };
  }
}

// category → 点击通知跳转的目标页。
// 老师网页有对应审查页的才跳；其余（外出 / 行事企画 / 冰箱 / 物品 / 杂项）
// 当前没有审查页 → 不跳、仅标已读。
const NAV_TARGET: Record<string, string> = {
  application: "applications",
  demerit: "discipline",
  demerit_alert: "discipline",
  rollcall_report: "records",
  study_absence: "study",
  study_online: "study",
};

export function NotificationsPage({
  onNav,
  authToken,
}: {
  // web#103：删死 prop teacher（组件全程未用；App.tsx 传入处由主控统一删）
  onNav: (view: string) => void;
  authToken: string;
}) {
  const T = RYO;
  const [items, setItems] = React.useState<NotificationItem[]>([]);
  const [unread, setUnread] = React.useState(0);
  const [pendingCount, setPendingCount] = React.useState<number | null>(null);
  const [warningCount, setWarningCount] = React.useState<number | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const loadFeed = React.useCallback(() => {
    if (!authToken) return;
    setLoading(true);
    api
      .notificationFeed(authToken)
      .then((res) => {
        setItems(res.items || []);
        setUnread(res.unread_count || 0);
        setError(null);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "通知の取得に失敗しました");
        setLoading(false);
      });
  }, [authToken]);

  React.useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  // 2 张卡的真实数字（用现成接口，不经通知表）
  React.useEffect(() => {
    if (!authToken) return;
    api
      .pendingForMe(authToken)
      .then((list) => setPendingCount((list || []).length))
      .catch(() => setPendingCount(null));
    api
      .getDisciplineRanking(authToken, currentMonth())
      .then((r) => setWarningCount(r.curfew_threshold_count ?? 0))
      .catch(() => setWarningCount(null));
  }, [authToken]);

  const markRead = (n: NotificationItem) => {
    if (n.is_read) return;
    // 乐观更新 — 先本地标已读，失败靠重拉回滚
    setItems((list) =>
      list.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)),
    );
    setUnread((u) => Math.max(0, u - 1));
    api
      .markNotificationRead(n.id, authToken)
      .then((res) => setUnread(res.unread_count))
      .catch(() => loadFeed());
  };

  const markAllRead = () => {
    if (unread === 0) return;
    setItems((list) => list.map((x) => ({ ...x, is_read: true })));
    setUnread(0);
    api
      .markAllNotificationsRead(authToken)
      .then((res) => setUnread(res.unread_count))
      .catch(() => loadFeed());
  };

  // 点一条通知：先标已读，再按 category 跳到对应审查页（没有对应页的类型只标已读）
  const handleClick = (n: NotificationItem) => {
    markRead(n); // markRead 内部已判 is_read，已读不会重复请求
    const target = NAV_TARGET[n.category];
    if (target) onNav(target);
  };

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
        通知
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 18px",
          letterSpacing: -0.3,
        }}
      >
        通知センター
      </h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <NotifCard
          n={pendingCount == null ? "—" : pendingCount}
          label="審査待ち申請"
          color={T.cobalt}
          onClick={() => onNav("applications")}
        />
        <NotifCard
          n={warningCount == null ? "—" : warningCount}
          label="警告リスト"
          color={T.warn}
          onClick={() => onNav("discipline")}
        />
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 10,
        }}
      >
        <div
          style={{
            fontSize: 12,
            color: T.ink3,
            letterSpacing: 1.5,
            fontWeight: 700,
          }}
        >
          最近の通知
          {unread > 0 && (
            <span
              style={{
                marginLeft: 8,
                fontSize: 11,
                background: T.danger,
                color: "#fff",
                padding: "1px 8px",
                borderRadius: 10,
                fontWeight: 700,
              }}
            >
              未読 {unread}
            </span>
          )}
        </div>
        <button
          onClick={markAllRead}
          disabled={unread === 0}
          style={{
            padding: "5px 12px",
            background: "transparent",
            color: unread === 0 ? T.ink3 : T.cobalt,
            border: `1px solid ${unread === 0 ? T.line : T.cobalt}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            fontWeight: 600,
            cursor: unread === 0 ? "default" : "pointer",
          }}
        >
          すべて既読にする
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: "10px 14px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            color: T.danger,
            fontSize: 13,
            marginBottom: 12,
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {loading && items.length === 0 ? (
        <div
          style={{
            background: T.surface,
            border: `1px dashed ${T.lineStrong}`,
            borderRadius: 12,
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
          }}
        >
          読み込み中…
        </div>
      ) : items.length === 0 ? (
        <div
          style={{
            background: T.surface,
            border: `1px dashed ${T.lineStrong}`,
            borderRadius: 12,
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
          }}
        >
          通知はありません
        </div>
      ) : (
        <div
          style={{
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
            overflow: "hidden",
            boxShadow: T.shadow1,
          }}
        >
          {items.map((n, i) => {
            const meta = categoryMeta(n.category, T);
            return (
              <div
                key={n.id}
                onClick={() => handleClick(n)}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 12,
                  padding: "12px 16px",
                  borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                  background: n.is_read ? "transparent" : T.cobaltSoft,
                  cursor:
                    !n.is_read || NAV_TARGET[n.category]
                      ? "pointer"
                      : "default",
                }}
              >
                {/* 未读小圆点 */}
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: 4,
                    marginTop: 5,
                    flexShrink: 0,
                    background: n.is_read ? "transparent" : T.cobalt,
                  }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      marginBottom: 2,
                    }}
                  >
                    <span
                      style={{
                        fontSize: 10,
                        color: meta.color,
                        background: T.surfaceAlt,
                        border: `1px solid ${T.lineStrong}`,
                        padding: "1px 7px",
                        borderRadius: 4,
                        fontWeight: 700,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {meta.label}
                    </span>
                    <span
                      style={{
                        fontSize: 13,
                        fontWeight: n.is_read ? 500 : 700,
                        color: T.ink,
                      }}
                    >
                      {n.title}
                    </span>
                  </div>
                  <div style={{ fontSize: 12.5, color: T.ink2 }}>{n.body}</div>
                </div>
                <span
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    fontFamily: T.mono,
                    whiteSpace: "nowrap",
                    flexShrink: 0,
                  }}
                >
                  {formatTime(n.event_at)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function NotifCard({
  n,
  label,
  color,
  onClick,
}: {
  n: number | string;
  label: string;
  color: string;
  onClick: () => void;
}) {
  const T = RYO;
  return (
    <button
      onClick={onClick}
      style={{
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        padding: "18px 20px",
        boxShadow: T.shadow1,
        textAlign: "left",
        fontFamily: "inherit",
        cursor: "pointer",
      }}
    >
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          fontFamily: T.mono,
          color,
        }}
      >
        {n}
      </div>
      <div style={{ fontSize: 12, color: T.ink2, marginTop: 2 }}>{label}</div>
      <div
        style={{
          fontSize: 11,
          color: T.cobalt,
          fontWeight: 600,
          marginTop: 8,
        }}
      >
        開く →
      </div>
    </button>
  );
}
