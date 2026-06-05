import React from "react";
import { RYO, dormLabel } from "../theme";
import { api } from "../api/client";
import type { TeacherProfile, StudentAccountListItem } from "../api/types";

// 源 index.html 20425-20810（pages-records-search-etc 块）。界面原样搬，仅作用域引用方式改写。
export function SearchPage({
  teacher,
  query,
  authToken,
}: {
  teacher: TeacherProfile;
  query: string;
  authToken: string;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("student");
  const [q, setQ] = React.useState(query || "");
  // 后端检索结果 — null=未检索 / []=0 件 / [...]
  const [results, setResults] = React.useState<StudentAccountListItem[] | null>(
    null,
  );
  const [searching, setSearching] = React.useState(false);
  const [searchError, setSearchError] = React.useState<string | null>(null);

  // q 每次变化都走后端检索（空白则不检索）
  React.useEffect(() => {
    if (!q.trim()) {
      setResults(null);
      return;
    }
    if (!authToken) return;
    setSearching(true);
    setSearchError(null);
    api
      .listStudents({ q: q.trim() }, authToken)
      .then((res) => {
        setResults(res.items || []);
        setSearching(false);
      })
      .catch((e) => {
        setSearchError(e.message || "検索に失敗しました");
        setSearching(false);
      });
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
            placeholder="氏名・学籍番号で検索（後端検索）"
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
                  dorm={String(s.dorm_unit)}
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

      <Block k="rollcall" title="点呼履歴" badge="月別サマリー">
        4 月: 時間内 18 / 遅刻 2 / 欠席 0 · 3 月: 時間内 31 / 遅刻 0 / 欠席 0
      </Block>
      <Block k="demerit" title="減点明細" badge="累計 1.0 点">
        04-17 遅刻 0.5 点 · 04-09 遅刻 0.5 点
      </Block>
      <Block k="health" title="体調報告履歴">
        提出記録なし
      </Block>
      <Block k="leave" title="欠席届履歴">
        提出記録なし
      </Block>
      <Block k="apps" title="申請履歴">
        04-21 外泊申請 (審査待ち) · 03-15 外泊申請 (承認済)
      </Block>
      <Block k="other" title="清掃・活動・宅配 等">
        清掃 4 月実施 6 回 · 宅配受取 2 件
      </Block>
    </div>
  );
}

function DateSearchBody() {
  const T = RYO;
  return (
    <div>
      <input
        type="date"
        defaultValue="2026-04-21"
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
          2026-04-21 全寮集計
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 14,
          }}
        >
          {[
            ["点呼", "23/24"],
            ["欠席", "1"],
            ["体調異常", "1"],
            ["申請処理", "3"],
          ].map(([l, v], i) => (
            <div key={i}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  letterSpacing: 1.2,
                  fontWeight: 600,
                }}
              >
                {l}
              </div>
              <div
                style={{
                  fontSize: 26,
                  fontWeight: 700,
                  fontFamily: T.mono,
                  marginTop: 4,
                }}
              >
                {v}
              </div>
            </div>
          ))}
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
