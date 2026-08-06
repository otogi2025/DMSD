import React from "react";
import { RYO, S, type RyoTokens } from "../theme";
import { api } from "../api/client";
import type {
  FrontDeskItem,
  FrontDeskCreateIn,
  TeacherProfile,
} from "../api/types";
import { canManage, C_FRONTDESK } from "../api/permissions";
import {
  ModalShell,
  ModalField,
  ModalFooter,
  StudentPicker,
  type PickerStudent,
} from "./shared";

// 源 index.html 17884-18885（front-desk 块）。界面原样搬，仅作用域引用方式改造。
// 前台业务页——从社区拆出的宅配通知 + 失物登记

// 撰写弹窗回调要提交的内容（部屋番号/発見場所 可空；宅配带收件学生 student_id）
type ComposeBody = {
  description: string;
  location: string | null;
  student_id?: string | null;
  item_count?: number; // 宅配件数（2026-06-14）；失物不传、后端默认 1
};

/** 失物是否超 1 月未返却（长期保管）：expires_at 日期早于今日 JST，且未受取/未处分 */
function isArchivedLost(l: FrontDeskItem, todayIso: string): boolean {
  const expDate = (l.expires_at || "").slice(0, 10);
  if (!expDate || expDate >= todayIso) return false;
  return (
    l.status === "pending" || l.status === "notified" || l.status === "expired"
  );
}

export function FrontDeskPage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile | null;
  authToken: string | null;
}) {
  const T = RYO;
  // 权限：C_FRONTDESK 簇里「申請承認専用」组只有 VIEW，后端 routers/front_desk.py 的
  // 追加/通知/受取均 require_permission(C_FRONTDESK, MANAGE)。无 MANAGE 时隐藏写按钮，
  // 避免点了必被 403（与 AccountsPage/InfoPage 同款门控）。
  const canWrite = !!teacher && canManage(teacher, C_FRONTDESK);
  const [tab, setTab] = React.useState<"delivery" | "lost">("delivery");
  const [items, setItems] = React.useState<FrontDeskItem[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [refreshing, setRefreshing] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [filter, setFilter] = React.useState("all");
  const [composing, setComposing] = React.useState(false);
  // 进行中的通知/受取请求 id，防连点触发后端 409
  const [pendingActionIds, setPendingActionIds] = React.useState<Set<string>>(
    () => new Set(),
  );
  const itemsRef = React.useRef(items);
  itemsRef.current = items;

  const loadItems = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    // 首载（或列表仍空）才盖「読み込み中」；后续静默刷新不卸掉列表
    if (itemsRef.current.length === 0) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    setFetchError(null);
    api
      .listFrontDesk(authToken)
      .then((data) => {
        if (!cancelled) setItems(Array.isArray(data) ? data : []);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[FrontDeskPage] listFrontDesk 失败", e);
        setFetchError(e.message || "データ取得に失敗しました");
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
          setRefreshing(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  React.useEffect(() => {
    return loadItems();
  }, [loadItems]);

  // 复审：同步 ref 守卫防双击（React state 异步，两个近乎同时的点击读同一旧快照各发一次
  // → 后端 409 / 状态打架）；pendingActionIds state 仅供渲染按钮 disabled。参照 TeachersAdminPage deletingRef。
  const pendingActionRef = React.useRef<Set<string>>(new Set());

  const handleNotify = (id: string) => {
    if (!authToken || pendingActionRef.current.has(id)) return;
    pendingActionRef.current.add(id);
    setPendingActionIds((prev) => new Set(prev).add(id));
    api
      .notifyFrontDesk(id, authToken)
      .then(() => loadItems())
      .catch((e) =>
        alert("通知処理に失敗しました：" + (e.message || JSON.stringify(e))),
      )
      .finally(() => {
        pendingActionRef.current.delete(id);
        setPendingActionIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      });
  };

  const handlePickup = (id: string) => {
    if (!authToken || pendingActionRef.current.has(id)) return;
    pendingActionRef.current.add(id);
    setPendingActionIds((prev) => new Set(prev).add(id));
    api
      .pickupFrontDesk(id, authToken)
      .then(() => loadItems())
      .catch((e) =>
        alert("受取処理に失敗しました：" + (e.message || JSON.stringify(e))),
      )
      .finally(() => {
        pendingActionRef.current.delete(id);
        setPendingActionIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      });
  };

  // location 空时按原逻辑提交 null（后端接受 null）；FrontDeskCreateIn.location 类型为 string?，故此处 cast
  const addItem = (
    body: ComposeBody & { kind: "delivery" | "lost_and_found" },
  ) => {
    if (!authToken) return;
    api
      .createFrontDesk(body as unknown as FrontDeskCreateIn, authToken)
      .then(() => {
        setComposing(false);
        loadItems();
      })
      .catch((e) =>
        alert("登録に失敗しました：" + (e.message || JSON.stringify(e))),
      );
  };

  // 「本日」按日本时区算 —— 后端时间统一是 +09:00 日本时间；用 UTC 会在日本凌晨 00-09 时算成昨天。
  // sv-SE 区域设置输出 ISO 格式 "YYYY-MM-DD"。
  const todayIso = new Date().toLocaleDateString("sv-SE", {
    timeZone: "Asia/Tokyo",
  });

  // 一次遍历累加统计 + 筛选，包进 useMemo 避免无关 state 变更时重算
  const { deliveries, lostItems, delFiltered, lostFiltered, stats } =
    React.useMemo(() => {
      const deliveries: FrontDeskItem[] = [];
      const lostItems: FrontDeskItem[] = [];
      const delAcc = { total: 0, unpicked: 0, today: 0, picked: 0 };
      const lostAcc = { total: 0, open: 0, returned: 0, archived: 0 };

      for (const i of items) {
        if (i.kind === "delivery") {
          deliveries.push(i);
          delAcc.total++;
          if (i.status === "pending" || i.status === "notified")
            delAcc.unpicked++;
          if ((i.created_at || "").startsWith(todayIso)) delAcc.today++;
          if (i.status === "picked_up") delAcc.picked++;
        } else if (i.kind === "lost_and_found") {
          lostItems.push(i);
          lostAcc.total++;
          if (i.status === "pending" || i.status === "notified") lostAcc.open++;
          if (i.status === "picked_up") lostAcc.returned++;
          if (isArchivedLost(i, todayIso)) lostAcc.archived++;
        }
      }

      // 未受取/未返却 = 显式 pending || notified（TW-060）。原来用 `!= picked_up`，会把将来
      // 可能出现的 expired / discarded 终态也算成「要対応」，误导老师。现阶段后端无这两个终态，
      // 属潜伏 bug，先按语义显式化兜住。
      const delFiltered = deliveries.filter((d) =>
        filter === "all"
          ? true
          : filter === "unpicked"
            ? d.status === "pending" || d.status === "notified"
            : d.status === "picked_up",
      );
      const lostFiltered = lostItems.filter((l) =>
        filter === "all"
          ? true
          : filter === "open"
            ? l.status === "pending" || l.status === "notified"
            : filter === "archived"
              ? isArchivedLost(l, todayIso)
              : l.status === "picked_up",
      );

      return {
        deliveries,
        lostItems,
        delFiltered,
        lostFiltered,
        stats: (tab === "delivery" ? delAcc : lostAcc) as Record<
          string,
          number
        >,
      };
    }, [items, tab, filter, todayIso]);

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
        フロント業務
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
          margin: "4px 0 6px",
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>
          フロント業務
        </h1>
        {canWrite && (
          <button
            onClick={() => setComposing(true)}
            className="t-btn"
            style={{
              ...S.btnPrimary,
              padding: "8px 16px",
            }}
          >
            ＋ {tab === "delivery" ? "宅配通知を追加" : "忘れ物を登録"}
          </button>
        )}
      </div>
      <div style={{ fontSize: 12, color: T.ink3, marginBottom: 18 }}>
        寮の受付窓口での代行記録です。宅配便の到着通知と、館内で見つかった忘れ物を管理します。
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

      {/* 统计卡片 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          marginBottom: 20,
        }}
      >
        {tab === "delivery" ? (
          <>
            <FdStat
              label="累計"
              value={stats.total}
              note="全受付"
              color={T.ink}
            />
            <FdStat
              label="未受取"
              value={stats.unpicked}
              note="要対応"
              color={T.warn}
              onClick={stats.unpicked > 0 ? () => setFilter("unpicked") : null}
            />
            <FdStat
              label="本日受付"
              value={stats.today}
              note={todayShort(todayIso)}
              color={T.cobalt}
            />
            <FdStat
              label="受取済"
              value={stats.picked}
              note="完了"
              color={T.ok}
            />
          </>
        ) : (
          <>
            <FdStat
              label="累計"
              value={stats.total}
              note="全登録"
              color={T.ink}
            />
            <FdStat
              label="未返却"
              value={stats.open}
              note="持主探索中"
              color={T.warn}
              onClick={stats.open > 0 ? () => setFilter("open") : null}
            />
            <FdStat
              label="返却済"
              value={stats.returned}
              note="持主判明"
              color={T.ok}
            />
            <FdStat
              label="長期保管"
              value={stats.archived}
              note="1ヶ月経過"
              color={T.ink3}
              onClick={stats.archived > 0 ? () => setFilter("archived") : null}
            />
          </>
        )}
      </div>

      {/* 标签页 */}
      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          marginBottom: 14,
        }}
      >
        {(
          [
            ["delivery", "宅配通知", deliveries.length],
            ["lost", "忘れ物", lostItems.length],
          ] as [string, string, number][]
        ).map(([k, l, n]) => (
          <button
            key={k}
            onClick={() => {
              setTab(k as "delivery" | "lost");
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
            }}
          >
            {l}{" "}
            <span style={{ color: T.ink3, fontSize: 11, fontWeight: 500 }}>
              ({n})
            </span>
          </button>
        ))}
      </div>

      {/* 筛选标签 */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 14,
          fontSize: 12,
          color: T.ink2,
        }}
      >
        {tab === "delivery"
          ? (
              [
                ["all", "全て"],
                ["unpicked", "未受取"],
                ["picked", "受取済"],
              ] as [string, string][]
            ).map(([k, l]) => (
              <button
                key={k}
                onClick={() => setFilter(k)}
                className="t-btn"
                style={chipStyle(T, filter === k)}
              >
                {l}
              </button>
            ))
          : (
              [
                ["all", "全て"],
                ["open", "未返却"],
                ["returned", "返却済"],
                ["archived", "長期保管"],
              ] as [string, string][]
            ).map(([k, l]) => (
              <button
                key={k}
                onClick={() => setFilter(k)}
                className="t-btn"
                style={chipStyle(T, filter === k)}
              >
                {l}
              </button>
            ))}
        {refreshing && (
          <span style={{ marginLeft: 8, fontSize: 11, color: T.ink3 }}>
            更新中…
          </span>
        )}
      </div>

      {/* 加载中（仅首载） */}
      {loading && (
        <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
          読み込み中…
        </div>
      )}

      {/* 列表——刷新时不卸掉 */}
      {!loading &&
        (tab === "delivery" ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {delFiltered.length === 0 && <EmptyRow T={T} />}
            {delFiltered.map((d, i) => (
              <DeliveryRow
                key={d.id}
                d={d}
                T={T}
                canWrite={canWrite}
                pending={pendingActionIds.has(d.id)}
                onNotify={handleNotify}
                onPickup={handlePickup}
                index={i}
              />
            ))}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {lostFiltered.length === 0 && <EmptyRow T={T} />}
            {lostFiltered.map((l, i) => (
              <LostItemRow
                key={l.id}
                l={l}
                T={T}
                canWrite={canWrite}
                pending={pendingActionIds.has(l.id)}
                onPickup={handlePickup}
                index={i}
              />
            ))}
          </div>
        ))}

      {composing && tab === "delivery" && (
        <DeliveryComposeModal
          T={T}
          authToken={authToken}
          onClose={() => setComposing(false)}
          onSubmit={(body) => addItem({ ...body, kind: "delivery" })}
        />
      )}
      {composing && tab === "lost" && (
        <LostItemComposeModal
          T={T}
          onClose={() => setComposing(false)}
          onSubmit={(body) => addItem({ ...body, kind: "lost_and_found" })}
        />
      )}
    </div>
  );
}

function FdStat({
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
      className={onClick ? "t-card" : undefined}
      style={{
        ...S.card,
        padding: "14px 16px",
        cursor: onClick ? "pointer" : "default",
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

// DeliveryRow —— 对齐后端 FrontDeskItemOut
// d.status: "pending" | "notified" | "picked_up"
// d.description: 说明文（配送公司・件数等以字符串填入）
// d.location: 房间号等
// d.created_at: ISO 字符串
function DeliveryRow({
  d,
  T,
  canWrite,
  pending,
  onNotify,
  onPickup,
  index = 0,
}: {
  d: FrontDeskItem;
  T: RyoTokens;
  canWrite: boolean;
  pending: boolean;
  onNotify: (id: string) => void;
  onPickup: (id: string) => void;
  index?: number;
}) {
  const isPicked = d.status === "picked_up";
  const isNotified = d.status === "notified";
  // expired（显示「期限切れ」）/ discarded（显示「処分済」）是终态 —— v1.0 暂无代码会置成这俩，
  // 但防御性处理：终态显示对应标签且不再显示「通知済に」「受取済に」操作按钮（点了后端会拒绝）。
  const isClosed =
    isPicked || d.status === "expired" || d.status === "discarded";
  const statusLabel = isPicked
    ? "受取済"
    : d.status === "expired"
      ? "期限切れ"
      : d.status === "discarded"
        ? "処分済"
        : isNotified
          ? "通知済"
          : "未受取";
  const dateStr = d.created_at
    ? d.created_at.slice(5, 16).replace("T", " ")
    : "—";
  return (
    <div
      className="t-fade-up"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "12px 16px",
        ...S.card,
        border: `1px solid ${isClosed ? T.line : T.warnBorder}`,
        opacity: pending ? 0.7 : 1,
        ...(index < 12 ? { animationDelay: `${index * 40}ms` } : null),
      }}
    >
      <span
        style={{
          ...S.pill,
          fontSize: 10,
          fontWeight: 700,
          padding: "3px 8px",
          background: isPicked
            ? T.okSoft
            : isNotified
              ? T.lateSoft
              : isClosed
                ? T.surfaceAlt
                : T.warnSoft,
          color: isPicked
            ? T.ok
            : isNotified
              ? T.warn
              : isClosed
                ? T.ink3
                : T.warn,
          border: `1px solid ${isPicked ? T.okBorder : isClosed ? T.line : T.warnBorder}`,
          letterSpacing: 0.5,
          whiteSpace: "nowrap",
          minWidth: 68,
          textAlign: "center",
          justifyContent: "center",
        }}
      >
        {statusLabel}
      </span>
      <span
        style={{
          fontFamily: T.mono,
          fontSize: 12,
          color: T.ink3,
          minWidth: 95,
        }}
      >
        {dateStr}
      </span>
      <span
        style={{
          fontFamily: T.mono,
          fontSize: 11,
          color: T.ink3,
          minWidth: 50,
        }}
      >
        {d.location || "—"}
      </span>
      <span
        style={{
          fontSize: 12,
          color: T.ink2,
          flex: 1,
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span style={{ fontWeight: 700, color: T.ink }}>{d.item_count}件</span>
        {d.description && (
          <span style={{ color: T.ink3 }}>{d.description}</span>
        )}
      </span>
      {isPicked && d.picked_up_at && (
        <span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>
          {d.picked_up_at.slice(5, 16).replace("T", " ")} 受取
        </span>
      )}
      {canWrite && !isClosed && !isNotified && (
        <button
          disabled={pending}
          onClick={() => onNotify(d.id)}
          className="t-btn"
          style={{
            ...S.btnGhost,
            padding: "5px 12px",
            fontSize: 11,
            color: T.ink3,
            cursor: pending ? "not-allowed" : "pointer",
            opacity: pending ? 0.5 : 1,
            whiteSpace: "nowrap",
          }}
        >
          通知済に
        </button>
      )}
      {canWrite && !isClosed && (
        <button
          disabled={pending}
          onClick={() => onPickup(d.id)}
          className="t-btn"
          style={{
            ...S.btnPrimary,
            padding: "5px 12px",
            fontSize: 11,
            cursor: pending ? "not-allowed" : "pointer",
            opacity: pending ? 0.5 : 1,
            whiteSpace: "nowrap",
          }}
        >
          受取済に
        </button>
      )}
    </div>
  );
}

// LostItemRow —— 对齐后端 FrontDeskItemOut
// status: "pending"|"notified" → 未返却 / "picked_up" → 返却済
// expired / discarded 同 DeliveryRow 作终态防御
function LostItemRow({
  l,
  T,
  canWrite,
  pending,
  onPickup,
  index = 0,
}: {
  l: FrontDeskItem;
  T: RyoTokens;
  canWrite: boolean;
  pending: boolean;
  onPickup: (id: string) => void;
  index?: number;
}) {
  const isReturned = l.status === "picked_up";
  const isClosed =
    isReturned || l.status === "expired" || l.status === "discarded";
  const statusLabel = isReturned
    ? "返却済"
    : l.status === "expired"
      ? "期限切れ"
      : l.status === "discarded"
        ? "処分済"
        : "未返却";
  const col = isReturned ? T.ok : isClosed ? T.ink3 : T.warn;
  const bg = isReturned ? T.okSoft : isClosed ? T.surfaceAlt : T.warnSoft;
  const bd = isReturned ? T.okBorder : isClosed ? T.line : T.warnBorder;
  const dateStr = l.created_at ? l.created_at.slice(5, 10) : "—";
  return (
    <div
      className="t-fade-up"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "12px 16px",
        ...S.card,
        border: `1px solid ${bd}`,
        opacity: pending ? 0.7 : 1,
        ...(index < 12 ? { animationDelay: `${index * 40}ms` } : null),
      }}
    >
      <span
        style={{
          ...S.pill,
          fontSize: 10,
          fontWeight: 700,
          padding: "3px 8px",
          background: bg,
          color: col,
          border: `1px solid ${bd}`,
          letterSpacing: 0.5,
          whiteSpace: "nowrap",
          minWidth: 68,
          textAlign: "center",
          justifyContent: "center",
        }}
      >
        {statusLabel}
      </span>
      <span
        style={{
          fontFamily: T.mono,
          fontSize: 12,
          color: T.ink3,
          minWidth: 55,
        }}
      >
        {dateStr}
      </span>
      {l.location && (
        <span style={{ fontSize: 12, color: T.ink3, minWidth: 100 }}>
          発見場所：{l.location}
        </span>
      )}
      <span style={{ fontSize: 12, color: T.ink2, flex: 1 }}>
        {l.description}
      </span>
      {isReturned && l.picked_up_at && (
        <span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>
          {l.picked_up_at.slice(5, 16).replace("T", " ")} 返却
        </span>
      )}
      {canWrite && !isClosed && (
        <button
          disabled={pending}
          onClick={() => onPickup(l.id)}
          className="t-btn"
          style={{
            ...S.btnPrimary,
            padding: "5px 12px",
            fontSize: 11,
            cursor: pending ? "not-allowed" : "pointer",
            opacity: pending ? 0.5 : 1,
            whiteSpace: "nowrap",
          }}
        >
          返却済に
        </button>
      )}
    </div>
  );
}

// DeliveryComposeModal —— 对齐后端 FrontDeskItemCreateIn
// 提交: { kind:"delivery", student_id, description(任意备注), location(=房号), item_count }
// 2026-06-14 选学生统一 + 快递改造：
//   - 受取人 → 共用 StudentPicker（single），打开即列表、滚动点选、想筛再打字
//   - 件数 → 步进器选数字（item_count），不再靠 description 里写「ヤマト 1件」
//   - 部屋番号 → 选学生后自动带出其 room_no、只读
//   - 備考 → 改可选（去掉原「配送業者」字段）
function DeliveryComposeModal({
  T,
  authToken,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  authToken: string | null;
  onClose: () => void;
  onSubmit: (body: ComposeBody) => void;
}) {
  const [selected, setSelected] = React.useState<PickerStudent[]>([]);
  const [itemCount, setItemCount] = React.useState(1);
  const [note, setNote] = React.useState(""); // 備考（任意）
  const student = selected[0] || null;
  const disabled = !student;
  const atMax = itemCount >= 999;

  const stepBtn: React.CSSProperties = {
    width: 36,
    height: 36,
    border: `1px solid ${T.lineStrong}`,
    background: T.surface,
    color: T.ink,
    fontSize: 18,
    fontWeight: 700,
    lineHeight: 1,
    cursor: "pointer",
    transition: T.ease,
  };

  return (
    <ModalShell T={T} title="宅配通知を追加" onClose={onClose}>
      <ModalField T={T} label="受取人（必須）">
        <StudentPicker
          mode="single"
          autoOpen
          searchApi={(q, token) => api.searchFrontDeskStudents(q, token)}
          selected={selected}
          onChange={setSelected}
          authToken={authToken || ""}
          placeholder="氏名 / 学籍番号で検索（クリックで一覧）"
        />
      </ModalField>
      <ModalField T={T} label="件数">
        <div style={{ display: "flex", alignItems: "center" }}>
          <button
            type="button"
            className="t-btn"
            onClick={() => setItemCount((n) => Math.max(1, n - 1))}
            style={{ ...stepBtn, borderRadius: "10px 0 0 10px" }}
          >
            −
          </button>
          <div
            style={{
              minWidth: 48,
              height: 36,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderTop: `1px solid ${T.lineStrong}`,
              borderBottom: `1px solid ${T.lineStrong}`,
              background: T.surfaceAlt,
              fontSize: 15,
              fontWeight: 700,
              color: T.ink,
            }}
          >
            {itemCount}
          </div>
          <button
            type="button"
            disabled={atMax}
            className="t-btn"
            onClick={() => setItemCount((n) => Math.min(999, n + 1))}
            style={{
              ...stepBtn,
              borderRadius: "0 10px 10px 0",
              opacity: atMax ? 0.4 : 1,
              cursor: atMax ? "not-allowed" : "pointer",
            }}
          >
            ＋
          </button>
          <span style={{ marginLeft: 10, fontSize: 13, color: T.ink3 }}>
            件
          </span>
          {atMax && (
            <span style={{ marginLeft: 8, fontSize: 11, color: T.ink3 }}>
              （上限 999）
            </span>
          )}
        </div>
      </ModalField>
      <ModalField T={T} label="部屋番号（受取人から自動）">
        <div
          style={{
            padding: "9px 12px",
            border: `1px solid ${T.line}`,
            borderRadius: 10,
            background: T.surfaceAlt,
            fontSize: 13,
            color: student ? T.ink : T.ink3,
          }}
        >
          {student ? student.room_no : "寮生を選択すると自動入力されます"}
        </div>
      </ModalField>
      <ModalField T={T} label="備考（任意）">
        <input
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="例: 冷蔵・大型 等（任意）"
          className="t-input"
          style={inputStyle(T)}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={() =>
          !disabled &&
          student &&
          onSubmit({
            description: note.trim(),
            location: student.room_no,
            student_id: student.id,
            item_count: itemCount,
          })
        }
        disabled={disabled}
      />
    </ModalShell>
  );
}

// LostItemComposeModal —— 对齐后端 FrontDeskItemCreateIn
// 提交: { kind:"lost_and_found", description, location }
function LostItemComposeModal({
  T,
  onClose,
  onSubmit,
}: {
  T: RyoTokens;
  onClose: () => void;
  onSubmit: (body: ComposeBody) => void;
}) {
  const [description, setDescription] = React.useState("");
  const [location, setLocation] = React.useState("");
  const disabled = !description.trim();
  return (
    <ModalShell T={T} title="忘れ物を登録" onClose={onClose}>
      <ModalField T={T} label="物品名・特徴">
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="例：ピンクの水筒（サーモス）"
          className="t-input"
          style={inputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="発見場所">
        <input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="玄関 / 廊下 / 風呂場 / 共用キッチン 等"
          className="t-input"
          style={inputStyle(T)}
        />
      </ModalField>
      <ModalFooter
        T={T}
        onClose={onClose}
        onSubmit={() =>
          !disabled &&
          onSubmit({
            description: description.trim(),
            location: location.trim() || null,
          })
        }
        disabled={disabled}
      />
    </ModalShell>
  );
}

function EmptyRow({ T }: { T: RyoTokens }) {
  return (
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
      該当する項目はありません
    </div>
  );
}

// 样式助手
function chipStyle(T: RyoTokens, on: boolean): React.CSSProperties {
  return {
    ...S.pill,
    padding: "4px 10px",
    fontSize: 11,
    background: on ? T.cobaltSoft : T.surface,
    color: on ? T.cobaltDeep : T.ink3,
    border: `1px solid ${on ? T.cobalt : T.lineStrong}`,
    fontFamily: "inherit",
    fontWeight: 600,
    cursor: "pointer",
    transition: T.ease,
  };
}
function inputStyle(T: RyoTokens): React.CSSProperties {
  return {
    ...S.input,
    width: "100%",
    padding: "9px 12px",
    border: `1px solid ${T.lineStrong}`,
    boxSizing: "border-box",
  };
}

// 日期助手 —— 从 JST 的 todayIso（YYYY-MM-DD）截取 MM-DD，与「本日受付」计数同源
function todayShort(todayIso: string): string {
  return todayIso.slice(5);
}
