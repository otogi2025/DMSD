import React from "react";
import { RYO, type RyoTokens } from "../theme";
import { api } from "../api/client";
import type {
  TeacherProfile,
  FrontDeskItem,
  FrontDeskCreateIn,
} from "../api/types";
import { ModalShell, ModalField, ModalFooter } from "./shared";

// 源 index.html 17884-18885（front-desk 块）。界面原样搬，仅作用域引用方式改造。
// フロント業務页 —— 宅配通知 + 忘れ物（コミュニティから拆分）

// 撰写弹窗回调要提交的内容（部屋番号/発見場所 可空）
type ComposeBody = { description: string; location: string | null };

export function FrontDeskPage({
  teacher: _teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string | null;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState<"delivery" | "lost">("delivery");
  const [items, setItems] = React.useState<FrontDeskItem[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [filter, setFilter] = React.useState("all");
  const [composing, setComposing] = React.useState(false);

  const loadItems = React.useCallback(() => {
    if (!authToken) return;
    let cancelled = false;
    setLoading(true);
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
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  React.useEffect(() => {
    return loadItems();
  }, [loadItems]);

  // 后端 status → 表示用 boolean
  // delivery: pending/notified = 未受取、picked_up = 受取済
  // lost_and_found: pending/notified = open、picked_up = returned
  const deliveries = items.filter((i) => i.kind === "delivery");
  const lostItems = items.filter((i) => i.kind === "lost_and_found");

  const handleNotify = (id: string) => {
    if (!authToken) return;
    api
      .notifyFrontDesk(id, authToken)
      .then(() => loadItems())
      .catch((e) =>
        alert("通知処理に失敗しました：" + (e.message || JSON.stringify(e))),
      );
  };

  const handlePickup = (id: string) => {
    if (!authToken) return;
    api
      .pickupFrontDesk(id, authToken)
      .then(() => loadItems())
      .catch((e) =>
        alert("受取処理に失敗しました：" + (e.message || JSON.stringify(e))),
      );
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

  const delFiltered = deliveries.filter((d) =>
    filter === "all"
      ? true
      : filter === "unpicked"
        ? d.status !== "picked_up"
        : d.status === "picked_up",
  );
  const lostFiltered = lostItems.filter((l) =>
    filter === "all"
      ? true
      : filter === "open"
        ? l.status !== "picked_up"
        : l.status === "picked_up",
  );

  const todayIso = new Date().toISOString().slice(0, 10);
  // 两个标签页统计字段不同 —— 用 Record 统一类型，避免联合后各字段变 number|undefined
  const stats: Record<string, number> =
    tab === "delivery"
      ? {
          total: deliveries.length,
          unpicked: deliveries.filter((d) => d.status !== "picked_up").length,
          today: deliveries.filter((d) =>
            (d.created_at || "").startsWith(todayIso),
          ).length,
          picked: deliveries.filter((d) => d.status === "picked_up").length,
        }
      : {
          total: lostItems.length,
          open: lostItems.filter((l) => l.status !== "picked_up").length,
          returned: lostItems.filter((l) => l.status === "picked_up").length,
          archived: 0,
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
          ＋ {tab === "delivery" ? "宅配通知を追加" : "忘れ物を登録"}
        </button>
      </div>
      <div style={{ fontSize: 12, color: T.ink3, marginBottom: 18 }}>
        寮の受付窓口での代行記録です。宅配便の到着通知と、館内で見つかった忘れ物を管理します。
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
              note={todayShort()}
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
              ] as [string, string][]
            ).map(([k, l]) => (
              <button
                key={k}
                onClick={() => setFilter(k)}
                style={chipStyle(T, filter === k)}
              >
                {l}
              </button>
            ))}
      </div>

      {/* 加载中 */}
      {loading && (
        <div style={{ padding: 24, color: T.ink3, fontSize: 13 }}>
          読み込み中…
        </div>
      )}

      {/* 列表 */}
      {!loading &&
        (tab === "delivery" ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {delFiltered.length === 0 && <EmptyRow T={T} />}
            {delFiltered.map((d) => (
              <DeliveryRow
                key={d.id}
                d={d}
                T={T}
                onNotify={handleNotify}
                onPickup={handlePickup}
              />
            ))}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {lostFiltered.length === 0 && <EmptyRow T={T} />}
            {lostFiltered.map((l) => (
              <LostItemRow key={l.id} l={l} T={T} onPickup={handlePickup} />
            ))}
          </div>
        ))}

      {composing && tab === "delivery" && (
        <DeliveryComposeModal
          T={T}
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
      style={{
        padding: "14px 16px",
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 10,
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
  onNotify,
  onPickup,
}: {
  d: FrontDeskItem;
  T: RyoTokens;
  onNotify: (id: string) => void;
  onPickup: (id: string) => void;
}) {
  const isPicked = d.status === "picked_up";
  const isNotified = d.status === "notified";
  const dateStr = d.created_at
    ? d.created_at.slice(5, 16).replace("T", " ")
    : "—";
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "12px 16px",
        background: T.surface,
        border: `1px solid ${isPicked ? T.line : T.warnBorder}`,
        borderRadius: 10,
      }}
    >
      <span
        style={{
          fontSize: 10,
          fontWeight: 700,
          padding: "3px 8px",
          borderRadius: 4,
          background: isPicked ? T.okSoft : isNotified ? "#fffbe6" : T.warnSoft,
          color: isPicked ? T.ok : isNotified ? "#b58c00" : T.warn,
          border: `1px solid ${isPicked ? T.okBorder : T.warnBorder}`,
          letterSpacing: 0.5,
          whiteSpace: "nowrap",
          minWidth: 68,
          textAlign: "center",
        }}
      >
        {isPicked ? "受取済" : isNotified ? "通知済" : "未受取"}
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
      <span style={{ fontSize: 12, color: T.ink2, flex: 1 }}>
        {d.description}
      </span>
      {isPicked && d.picked_up_at && (
        <span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>
          {d.picked_up_at.slice(5, 16).replace("T", " ")} 受取
        </span>
      )}
      {!isPicked && !isNotified && (
        <button onClick={() => onNotify(d.id)} style={actionBtn(T, "ghost")}>
          通知済に
        </button>
      )}
      {!isPicked && (
        <button onClick={() => onPickup(d.id)} style={actionBtn(T, "ok")}>
          受取済に
        </button>
      )}
    </div>
  );
}

// LostItemRow —— 对齐后端 FrontDeskItemOut
// status: "pending"|"notified" → 未返却 / "picked_up" → 返却済
function LostItemRow({
  l,
  T,
  onPickup,
}: {
  l: FrontDeskItem;
  T: RyoTokens;
  onPickup: (id: string) => void;
}) {
  const isReturned = l.status === "picked_up";
  const col = isReturned ? T.ok : T.warn;
  const bg = isReturned ? T.okSoft : T.warnSoft;
  const bd = isReturned ? T.okBorder : T.warnBorder;
  const lbl = isReturned ? "返却済" : "未返却";
  const dateStr = l.created_at ? l.created_at.slice(5, 10) : "—";
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "12px 16px",
        background: T.surface,
        border: `1px solid ${bd}`,
        borderRadius: 10,
      }}
    >
      <span
        style={{
          fontSize: 10,
          fontWeight: 700,
          padding: "3px 8px",
          borderRadius: 4,
          background: bg,
          color: col,
          border: `1px solid ${bd}`,
          letterSpacing: 0.5,
          whiteSpace: "nowrap",
          minWidth: 68,
          textAlign: "center",
        }}
      >
        {lbl}
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
      {!isReturned && (
        <button onClick={() => onPickup(l.id)} style={actionBtn(T, "ok")}>
          返却済に
        </button>
      )}
    </div>
  );
}

// DeliveryComposeModal —— 对齐后端 FrontDeskItemCreateIn
// 提交: { kind:"delivery", description, location }
// student_id 任意（v1 以 description 含名字字符串的方式运用）
function DeliveryComposeModal({
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
    <ModalShell T={T} title="宅配通知を追加" onClose={onClose}>
      <ModalField T={T} label="内容（受取人・配送業者・件数等）">
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="例: 田中 隼人 M101 ヤマト運輸 1件"
          style={inputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="部屋番号・場所">
        <input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="M101 / W113 等"
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
          style={inputStyle(T)}
        />
      </ModalField>
      <ModalField T={T} label="発見場所">
        <input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="玄関 / 廊下 / 風呂場 / 共用キッチン 等"
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
        borderRadius: 10,
      }}
    >
      該当する項目はありません
    </div>
  );
}

// 样式助手
function chipStyle(T: RyoTokens, on: boolean): React.CSSProperties {
  return {
    padding: "4px 10px",
    background: on ? T.cobaltSoft : T.surface,
    color: on ? T.cobaltDeep : T.ink3,
    border: `1px solid ${on ? T.cobalt : T.lineStrong}`,
    borderRadius: 999,
    fontFamily: "inherit",
    fontSize: 11,
    fontWeight: 600,
    cursor: "pointer",
  };
}
function actionBtn(
  T: RyoTokens,
  kind: "ok" | "danger" | "ghost",
): React.CSSProperties {
  const map: Record<string, [string, string]> = {
    ok: [T.ok, T.okBorder],
    danger: [T.danger, T.dangerBorder],
    ghost: [T.ink3, T.lineStrong],
  };
  const [col, bd] = map[kind];
  return {
    padding: "5px 12px",
    background: T.surface,
    color: col,
    border: `1px solid ${bd}`,
    borderRadius: 6,
    fontFamily: "inherit",
    fontSize: 11,
    fontWeight: 600,
    cursor: "pointer",
    whiteSpace: "nowrap",
  };
}
function inputStyle(T: RyoTokens): React.CSSProperties {
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

// 日期助手
function todayShort(): string {
  const d = new Date();
  return `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
