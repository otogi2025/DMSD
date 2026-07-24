import React from "react";
import { RYO, dormLabel } from "../theme";
import { api } from "../api/client";
import type { StudentAccountListItem } from "../api/types";

// 源 index.html 20425-20810（pages-records-search-etc 块）。界面原样搬，仅作用域引用方式改写。
export function SearchPage({
  query,
  authToken,
}: {
  query: string;
  authToken: string;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("student");
  const [q, setQ] = React.useState(query || "");
  // C11: 已在检索页时从顶栏再次检索，page 不变、组件不重挂，useState 初值不会重跑，
  // 内部 q 会停在旧值导致二次检索静默失效。同步 query prop → 内部 q。
  React.useEffect(() => {
    setQ(query || "");
  }, [query]);
  // 后端检索结果 — null=未检索 / []=0 件 / [...]
  const [results, setResults] = React.useState<StudentAccountListItem[] | null>(
    null,
  );
  const [searching, setSearching] = React.useState(false);
  const [searchError, setSearchError] = React.useState<string | null>(null);

  // web#39：防抖 + cancelled 守卫，防快打字慢请求覆盖新结果 / 卸载后 setState
  React.useEffect(() => {
    if (!q.trim()) {
      setResults(null);
      setSearching(false);
      setSearchError(null);
      return;
    }
    if (!authToken) return;
    let cancelled = false;
    setSearching(true);
    setSearchError(null);
    const timer = setTimeout(() => {
      api
        .listStudents({ q: q.trim() }, authToken)
        .then((res) => {
          if (cancelled) return;
          setResults(res.items || []);
          setSearching(false);
        })
        .catch((e) => {
          if (cancelled) return;
          setSearchError(e.message || "検索に失敗しました");
          setSearching(false);
        });
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [q, authToken]);

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
        検索 {q && `> ${q}`}
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 18px",
          letterSpacing: -0.3,
        }}
      >
        検索結果
      </h1>

      <div
        style={{
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.line}`,
          marginBottom: 20,
        }}
      >
        {[
          ["student", "学生から"],
          ["date", "日付から"],
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

      {tab === "student" ? (
        <>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="氏名・学籍番号で検索"
            style={{
              width: "100%",
              padding: "11px 14px",
              background: T.surface,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 14,
              outline: "none",
              boxSizing: "border-box",
              marginBottom: 20,
            }}
          />
          {searchError && (
            <div
              style={{
                padding: "10px 14px",
                background: T.dangerSoft,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 8,
                fontSize: 12,
                color: T.danger,
                marginBottom: 14,
              }}
            >
              ⚠️ {searchError}
            </div>
          )}
          {searching && (
            <div
              style={{
                padding: 24,
                textAlign: "center",
                color: T.ink3,
                fontSize: 13,
              }}
            >
              検索中…
            </div>
          )}
          {!searching && results && results.length > 0 && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              {results.map((s) => (
                <StudentDossier
                  key={s.id}
                  room={s.room_no}
                  id={s.student_no}
                  name={s.name}
                  dorm={s.dorm_unit === 4 ? "women" : "men"}
                />
              ))}
            </div>
          )}
          {!searching && results !== null && results.length === 0 && (
            <EmptyState msg={`「${q}」に一致する学生はいません`} />
          )}
          {!searching && results === null && (
            <EmptyState msg="氏名・学籍番号を入力してください" />
          )}
        </>
      ) : (
        <DateSearchBody />
      )}
    </div>
  );
}

function StudentDossier({
  room,
  id,
  name,
  dorm,
}: {
  room: string;
  id: string;
  name: string;
  dorm: string;
}) {
  const T = RYO;
  const [open, setOpen] = React.useState<Record<string, boolean>>({
    rollcall: true,
    demerit: true,
    health: false,
    leave: false,
    apps: false,
    other: false,
  });
  const Block = ({
    k,
    title,
    badge,
    children,
  }: {
    k: string;
    title: string;
    badge?: string;
    children: React.ReactNode;
  }) => (
    <div
      style={{
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        marginBottom: 10,
        boxShadow: T.shadow1,
      }}
    >
      <button
        onClick={() => setOpen((o) => ({ ...o, [k]: !o[k] }))}
        style={{
          display: "flex",
          width: "100%",
          alignItems: "center",
          padding: "14px 18px",
          background: "transparent",
          border: "none",
          fontFamily: "inherit",
          cursor: "pointer",
        }}
      >
        <span style={{ fontSize: 15, fontWeight: 700, color: T.ink }}>
          {title}
        </span>
        {badge && (
          <span style={{ marginLeft: 8, fontSize: 11, color: T.ink3 }}>
            {badge}
          </span>
        )}
        <div style={{ flex: 1 }} />
        <span style={{ color: T.ink3, fontSize: 13 }}>
          {open[k] ? "▾" : "▸"}
        </span>
      </button>
      {open[k] && (
        <div
          style={{
            padding: "0 18px 16px",
            fontSize: 13,
            color: T.ink2,
            lineHeight: 1.7,
          }}
        >
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div>
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 22px",
          boxShadow: T.shadow1,
          marginBottom: 16,
          display: "flex",
          alignItems: "center",
          gap: 18,
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: 28,
            background: T.cobaltSoft,
            color: T.cobaltDeep,
            fontSize: 22,
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {name.charAt(0)}
        </div>
        <div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{name}</div>
          <div
            style={{
              fontSize: 12,
              color: T.ink3,
              fontFamily: T.mono,
              marginTop: 2,
            }}
          >
            {room} · {id} · {dormLabel(dorm)}
          </div>
        </div>
      </div>

      {/* 履歴区块统一「データ未接続」占位（审查 web#7）：原来六个区块全是硬编码
          假数据（点呼 18/2/0、減点 1.0 点、04-21 外泊申請等），头部却是真实检索
          结果——生产环境对真实学生展示捏造的点呼/减点历史，老师会据此误判学生。
          学生档案聚合接口做出来之前只显示诚实占位，不显示编造内容 */}
      <Block k="rollcall" title="点呼履歴">
        データ未接続（今後のバージョンで対応予定）
      </Block>
      <Block k="demerit" title="減点明細">
        データ未接続（今後のバージョンで対応予定）
      </Block>
      <Block k="health" title="体調報告履歴">
        データ未接続（今後のバージョンで対応予定）
      </Block>
      <Block k="leave" title="欠席届履歴">
        データ未接続（今後のバージョンで対応予定）
      </Block>
      <Block k="apps" title="申請履歴">
        データ未接続（今後のバージョンで対応予定）
      </Block>
      <Block k="other" title="清掃・活動・宅配 等">
        データ未接続（今後のバージョンで対応予定）
      </Block>
    </div>
  );
}

function DateSearchBody() {
  const T = RYO;
  // web#40：日期默认用 JST 今天（Asia/Tokyo，sv-SE→YYYY-MM-DD，与本批其它日期修复同口径）；
  // 聚合接口未接前诚实标「準備中」，不展示假统计
  const todayStr = new Date().toLocaleDateString("sv-SE", {
    timeZone: "Asia/Tokyo",
  });
  const [date, setDate] = React.useState(todayStr);

  return (
    <div>
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        style={{
          padding: "11px 14px",
          border: `1px solid ${T.lineStrong}`,
          borderRadius: 10,
          fontFamily: T.mono,
          fontSize: 14,
          marginBottom: 18,
        }}
      />
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 22px",
          boxShadow: T.shadow1,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
          {date} 全寮集計
        </div>
        <div
          style={{
            padding: "28px 12px",
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
            lineHeight: 1.7,
            border: `1px dashed ${T.lineStrong}`,
            borderRadius: 8,
          }}
        >
          準備中
          <div style={{ fontSize: 11, marginTop: 6, color: T.muted }}>
            日付集計 API 接続後に表示されます
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ msg }: { msg: string }) {
  const T = RYO;
  return (
    <div
      style={{
        padding: 60,
        textAlign: "center",
        color: T.ink3,
        fontSize: 13,
        background: T.surface,
        border: `1px dashed ${T.lineStrong}`,
        borderRadius: 12,
      }}
    >
      {msg}
    </div>
  );
}
