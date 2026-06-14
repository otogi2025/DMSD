import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { Application, StudentBrief } from "../api/types";

// 源 index.html 20037-20423（pages-records-search-etc 块）。界面原样搬。
// 出寮者一覧（2026-06-04 杭田需求「四」）— 纯只读页。
// 拉 GET /applications/active（当天在出寮期间内、已承认的届），按寮分两块表显示。
// 編集不可 / 削除不可 — 防误删；老师只能看 + 印刷 + 更新（重新拉取）。
export function ActiveLeavesPage({ authToken }: { authToken: string }) {
  const T = RYO;
  // 日期选择器初值 = 今天（YYYY-MM-DD，本地时区）
  const todayStr = () => {
    const d = new Date();
    const p = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  };
  const [date, setDate] = React.useState(todayStr());
  // 三态：null=加载中 / Error 对象=拉取失败 / 数组=真值（可空数组 = 0 件）
  const [rows, setRows] = React.useState<Application[] | null>(null);
  const [error, setError] = React.useState<{ message?: string } | null>(null);
  // 每次「更新」时 +1 触发重新拉取
  const [reloadTick, setReloadTick] = React.useState(0);

  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    setRows(null);
    setError(null);
    api
      .activeLeaves(authToken, date)
      .then((data) => {
        if (!cancelled) setRows(Array.isArray(data) ? data : []);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[ActiveLeavesPage] activeLeaves 失敗", e);
        setError(e || { message: "取得に失敗しました" });
      });
    return () => {
      cancelled = true;
    };
  }, [authToken, date, reloadTick]);

  // 拼「行先」字符串：外泊先（stay_locations）或帰国都市（dest_cities），都没有就「—」。
  // stay_locations 是 dict 数组（含 name 等），dest_cities 可能是逗号分隔字符串，两种都兼容。
  const formatDestination = (app: Application) => {
    const locs = app.stay_locations;
    if (Array.isArray(locs) && locs.length > 0) {
      return locs
        .map((l) => (l && (l.name || l.kind)) || "")
        .filter(Boolean)
        .join("、");
    }
    const cities = app.dest_cities;
    if (Array.isArray(cities) && cities.length > 0) {
      return cities.filter(Boolean).join("、");
    }
    if (typeof cities === "string" && cities.trim()) {
      return cities.trim();
    }
    return "—";
  };

  // 一条届 = 表格一行
  const renderRow = (app: Application, i: number) => {
    const st: Partial<StudentBrief> = app.student || {};
    return (
      <div
        key={app.id || i}
        style={{
          display: "grid",
          gridTemplateColumns: "1.2fr 80px 70px 1.1fr 1.1fr 1.4fr",
          borderTop: i > 0 ? `1px solid ${T.line}` : "none",
          fontSize: 12.5,
          alignItems: "center",
        }}
      >
        <div style={{ padding: "9px 12px", fontWeight: 600 }}>
          {st.name || "—"}
        </div>
        <div
          style={{
            padding: "9px 12px",
            fontFamily: T.mono,
            color: T.ink2,
          }}
        >
          {st.room_no || "—"}
        </div>
        <div style={{ padding: "9px 12px", color: T.ink2 }}>
          {app.kind || "—"}
        </div>
        <div
          style={{
            padding: "9px 12px",
            fontFamily: T.mono,
            color: T.ink2,
            fontSize: 12,
          }}
        >
          {app.leave_date || "—"}{" "}
          {app.leave_time ? String(app.leave_time).slice(0, 5) : ""}
        </div>
        <div
          style={{
            padding: "9px 12px",
            fontFamily: T.mono,
            color: T.ink2,
            fontSize: 12,
          }}
        >
          {app.return_date || "—"}{" "}
          {app.return_time ? String(app.return_time).slice(0, 5) : ""}
        </div>
        <div style={{ padding: "9px 12px", color: T.ink2 }}>
          {formatDestination(app)}
        </div>
      </div>
    );
  };

  // 每个寮单位画一块（表格）
  const renderBlock = (title: string, blockRows: Application[]) => (
    <div style={{ marginBottom: 24 }}>
      <div
        style={{
          fontSize: 13,
          fontWeight: 700,
          color: T.ink,
          marginBottom: 8,
        }}
      >
        {title}
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: T.ink3,
            marginLeft: 8,
          }}
        >
          {blockRows.length} 名
        </span>
      </div>
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: T.shadow1,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 80px 70px 1.1fr 1.1fr 1.4fr",
            background: T.surfaceAlt,
            fontSize: 11,
            color: T.ink2,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {["氏名", "部屋", "種類", "出寮", "帰寮", "行先"].map((h) => (
            <div key={h} style={{ padding: "10px 12px" }}>
              {h}
            </div>
          ))}
        </div>
        {blockRows.length === 0 ? (
          <div
            style={{
              padding: "20px 12px",
              textAlign: "center",
              color: T.ink3,
              fontSize: 12.5,
            }}
          >
            該当者なし
          </div>
        ) : (
          blockRows.map((app, i) => renderRow(app, i))
        )}
      </div>
    </div>
  );

  // 按寮分组：「1・2寮（男寮）」= dorm_unit ∈ {1,2}，「4寮（女寮）」= dorm_unit === 4
  const menRows = Array.isArray(rows)
    ? rows.filter((a) => {
        const u = a.student && a.student.dorm_unit;
        return u === 1 || u === 2;
      })
    : [];
  const womenRows = Array.isArray(rows)
    ? rows.filter((a) => a.student && a.student.dorm_unit === 4)
    : [];

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
        記録
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 6px",
          letterSpacing: -0.3,
        }}
      >
        出寮者一覧
      </h1>
      <div style={{ fontSize: 12.5, color: T.ink3, marginBottom: 18 }}>
        指定日に出寮中（承認済み）の寮生一覧です。閲覧専用・編集不可。「更新」で最新の届を再取得します。
      </div>

      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600 }}>
          日付
        </label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          style={{
            padding: "7px 10px",
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: T.mono,
            fontSize: 13,
          }}
        />
        <button
          onClick={() => setReloadTick((t) => t + 1)}
          style={{
            padding: "6px 12px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          更新
        </button>
        <div style={{ flex: 1 }} />
        <button
          onClick={() => window.print()}
          style={{
            padding: "6px 12px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          印刷・PDF 保存
        </button>
        <button
          onClick={async () => {
            // 食堂用食数表导出：今天 ~ +31 天（食数来自将来的外泊/帰国届的食事不要期间）
            const pad = (n: number) => String(n).padStart(2, "0");
            const fmt = (d: Date) =>
              `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
            const start = new Date();
            const end = new Date();
            end.setDate(end.getDate() + 31);
            try {
              await api.downloadMealsExport(fmt(start), fmt(end), authToken);
            } catch (e) {
              window.alert(
                `食数表の取得に失敗しました (${(e && (e as { status?: number }).status) || "network"})`,
              );
            }
          }}
          style={{
            padding: "6px 12px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          食数表（今後1ヶ月）出力
        </button>
      </div>

      {error !== null ? (
        <div
          style={{
            padding: "32px 0",
            textAlign: "center",
            color: T.danger,
            fontSize: 13,
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 12,
          }}
        >
          出寮者一覧の取得に失敗しました
          {error && error.message ? `（${error.message}）` : ""}
        </div>
      ) : rows === null ? (
        <div
          style={{
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
          }}
        >
          {authToken ? "読み込み中…" : "ログインしてください"}
        </div>
      ) : rows.length === 0 ? (
        <div
          style={{
            padding: "32px 0",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
          }}
        >
          この日に出寮中の寮生はいません
        </div>
      ) : (
        <>
          {renderBlock("一寮・二寮（男子寮）", menRows)}
          {renderBlock("四寮（女子寮）", womenRows)}
        </>
      )}
    </div>
  );
}

// 私有子组件 — 点呼状态徽章（源块里紧邻 ActiveLeavesPage 的 window.RecStatusBadge）。
// 不 export，仅同文件复用。
function RecStatusBadge({ s }: { s: string }) {
  const T = RYO;
  const map = (
    {
      ok: [T.ok, T.okSoft, "時間内"],
      late: [T.late, T.lateSoft, "遅刻"],
      absent: [T.danger, T.dangerSoft, "欠席"],
      exempt: [T.info, T.infoSoft, "免除"],
    } as Record<string, [string, string, string]>
  )[s] || [T.ink3, T.surfaceAlt, "—"];
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: "2px 8px",
        borderRadius: 4,
        background: map[1],
        color: map[0],
      }}
    >
      {map[2]}
    </span>
  );
}
