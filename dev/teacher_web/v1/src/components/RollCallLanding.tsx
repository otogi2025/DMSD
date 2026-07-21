import React from "react";
import { RYO, dormLabel } from "../theme";
import { api } from "../api/client";
import type { StudentAccountListOut } from "../api/types";

// 源 index.html 11940-12361（components/roll-call-landing.jsx 块）。
// 界面 100% 冻结，仅做作用域引用替换：window.RYO→RYO / window.tomoshibiApi→api / window.dormLabel→dormLabel。
// 点呼着陆页 + 趋势图占位（web#45 去假数据）+ 点呼类型选择（4 种）。

// 主组件入参类型 —— 从源解构签名推。
// 注意：源里既用 teacher.assigned_dorm 又用 teacher.dorm（源自身字段不一致），界面冻结照搬，故 teacher 类型同时带两者。
export function RollCallLanding({
  teacher,
  onStart,
  lastEnded,
  onNav,
  onShowSummary,
  authToken,
}: {
  teacher: { name: string; assigned_dorm: number | null; dorm: string };
  onStart: (name: string) => void;
  lastEnded:
    | {
        name: string;
        sessionName?: string;
        start: string;
        end: string;
        rate: string;
      }
    | null
    | undefined;
  onNav: (view: string, payload?: { date?: string }) => void;
  onShowSummary?: () => void;
  authToken: string;
}) {
  const T = RYO;
  const [name, setName] = React.useState("夜点呼 · 普通寮生");
  // 从后端取该寮学生人数（替代假名单 window.ROSTER_MEN/WOMEN）
  const [studentCount, setStudentCount] = React.useState<number | null>(null);
  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    // TODO(web#114)：client.listStudents 入参无 limit，后端默认 limit=1000 且
    // res.total === items.length（同被封顶），超 1000 人会截断。本批禁改 client.ts，
    // 真寮规模远低于 1000，暂用 items.length；要修需给 listStudents 加 limit 或真分页/count。
    api
      .listStudents(
        teacher.assigned_dorm ? { dorm_unit: teacher.assigned_dorm } : {},
        authToken,
      )
      .then((res: StudentAccountListOut) => {
        if (!cancelled) setStudentCount((res.items || []).length);
      })
      .catch(() => {
        if (!cancelled) setStudentCount(null);
      });
    return () => {
      cancelled = true;
    };
  }, [teacher.assigned_dorm, authToken]);
  const today = new Date();
  const todayLabel = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}（${["日", "月", "火", "水", "木", "金", "土"][today.getDay()]}）`;

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: 10,
          marginBottom: 4,
        }}
      >
        <h1
          style={{
            fontSize: 24,
            fontWeight: 700,
            margin: 0,
            letterSpacing: -0.3,
          }}
        >
          点呼ダッシュボード
        </h1>
        <span style={{ fontSize: 12, color: T.ink3 }}>{todayLabel}</span>
      </div>
      <div style={{ color: T.ink2, fontSize: 13, marginBottom: 22 }}>
        対象 {studentCount ?? "—"} 名 · {dormLabel(teacher.dorm)} · 舎監{" "}
        {teacher.name} 先生
      </div>

      {/* 学年更新 4 月提醒 —— 每年 4 月，提示从「学生账号管理」开始（spec §4.2）*/}
      {today.getMonth() === 3 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            background: T.warnSoft,
            border: `1px solid ${T.warnBorder}`,
            borderRadius: 12,
            padding: "12px 18px",
            marginBottom: 18,
            fontSize: 13,
          }}
        >
          <span style={{ color: T.warn, fontWeight: 600 }}>
            新学年です。「学生アカウント管理」から学年更新を開始してください。
          </span>
          {onNav && (
            <button
              onClick={() => onNav("accounts")}
              style={{
                padding: "7px 14px",
                background: T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              学生管理へ
            </button>
          )}
        </div>
      )}

      {/* Task #13 spec §5.6: 重新查看刚结束的点呼总结入口 */}
      {lastEnded && onShowSummary && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: T.cobaltSoft,
            border: `1px solid ${T.infoBorder}`,
            borderRadius: 12,
            padding: "12px 18px",
            marginBottom: 18,
            fontSize: 13,
          }}
        >
          <div style={{ color: T.cobaltDeep }}>
            <span style={{ fontWeight: 700 }}>先ほどの点呼：</span>{" "}
            {lastEnded.sessionName || lastEnded.name} · {lastEnded.start} →{" "}
            {lastEnded.end} · 出席率{" "}
            <span style={{ fontFamily: T.mono, fontWeight: 700 }}>
              {lastEnded.rate}
            </span>
          </div>
          <button
            onClick={onShowSummary}
            style={{
              padding: "7px 16px",
              background: T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            集計を見る →
          </button>
        </div>
      )}

      {/* 开始卡片 */}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 14,
          padding: "22px 24px",
          boxShadow: T.shadow1,
          marginBottom: 20,
          display: "grid",
          gridTemplateColumns: "1fr auto",
          gap: 24,
          alignItems: "center",
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              letterSpacing: 2,
              fontWeight: 600,
            }}
          >
            {/* 7-17 适老化拍板③：面向年长日本用户的界面不放裸英文标签 */}
            点呼セッション
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>
            新しい点呼を開始
          </div>
          <div style={{ color: T.ink2, fontSize: 13, marginTop: 4 }}>
            「開始」を押すと {studentCount ?? 0} 名の座席表に切り替わります。
          </div>
          <div
            style={{
              marginTop: 14,
              display: "flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600 }}>
              対象
            </label>
            <select
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{
                padding: "7px 10px",
                background: T.surface,
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                color: T.ink,
                outline: "none",
              }}
            >
              <option>夜点呼 · 普通寮生</option>
              <option>夜点呼 · 部活生</option>
              <option>朝点呼 · 普通寮生</option>
              <option>朝点呼 · 部活生</option>
            </select>
          </div>
        </div>
        <button
          onClick={() => onStart(name)}
          style={{
            padding: "16px 36px",
            background: T.cobalt,
            color: "#fff",
            border: "none",
            borderRadius: 12,
            fontFamily: "inherit",
            fontSize: 16,
            fontWeight: 700,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(43,77,140,.28)",
          }}
        >
          点呼を開始 →
        </button>
      </div>

      {/* 当日统计 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          marginBottom: 20,
        }}
      >
        <Stat
          label="本日実施"
          value="1"
          suffix="/ 2"
          note="朝点呼 完了"
          onClick={() => onNav("records")}
        />
        <Stat
          label="欠席者"
          value="2"
          color={T.danger}
          note="昨日は 1 名"
          onClick={() => onNav("records")}
        />
        <Stat
          label="審査待ち申請"
          value="3"
          color={T.cobalt}
          note="外泊 2 · 免除 1"
          onClick={() => onNav("applications")}
        />
        <Stat
          label="警告リスト"
          value="4"
          color={T.warn}
          note="今月累計"
          onClick={() => onNav("discipline")}
        />
      </div>

      {/* web#45: 无 trend 后端端点 → 假趋势图改为準備中占位 */}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 22px",
          boxShadow: T.shadow1,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
          最近 7 日 遅刻・欠席トレンド
        </div>
        <div style={{ fontSize: 13, color: T.ink3 }}>準備中</div>
      </div>

      {/* 最近的点呼会话 */}
      <div
        style={{
          fontSize: 12,
          letterSpacing: 1.5,
          color: T.ink3,
          fontWeight: 700,
          textTransform: "uppercase",
          marginBottom: 10,
          marginTop: 22,
        }}
      >
        最近の点呼
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
            gridTemplateColumns: "110px 1fr 110px 110px 110px 90px",
            background: T.surfaceAlt,
            color: T.ink2,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {["日付", "名称", "開始", "終了", "出席率", ""].map((h) => (
            <div key={h} style={{ padding: "10px 14px" }}>
              {h}
            </div>
          ))}
        </div>
        {[
          lastEnded && [
            "2026-04-21",
            lastEnded.name,
            lastEnded.start,
            lastEnded.end,
            lastEnded.rate,
            "詳細",
          ],
          [
            "2026-04-21",
            "朝点呼 · 普通寮生",
            "07:00",
            "07:08",
            "12/12",
            "詳細",
          ],
          [
            "2026-04-20",
            "夜点呼 · 普通寮生",
            "19:30",
            "19:37",
            "11/12",
            "詳細",
          ],
          [
            "2026-04-20",
            "朝点呼 · 普通寮生",
            "07:00",
            "07:09",
            "12/12",
            "詳細",
          ],
        ]
          .filter((row): row is string[] => Boolean(row))
          .map(([d, n, s, e, r, a], i) => (
            <div
              key={i}
              style={{
                display: "grid",
                gridTemplateColumns: "110px 1fr 110px 110px 110px 90px",
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                fontSize: 13,
              }}
            >
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  color: T.ink3,
                }}
              >
                {d}
              </div>
              <div style={{ padding: "10px 14px", fontWeight: 500 }}>{n}</div>
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  color: T.ink2,
                }}
              >
                {s}
              </div>
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  color: T.ink2,
                }}
              >
                {e}
              </div>
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  fontWeight: 600,
                }}
              >
                {r}
              </div>
              <button
                onClick={() => onNav("records", { date: d })}
                style={{
                  padding: "10px 14px",
                  color: T.cobalt,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  background: "transparent",
                  border: "none",
                  fontFamily: "inherit",
                  textAlign: "left",
                }}
              >
                {a} →
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}

// 以下 3 个组件 4c2578f「删 demo 脚手架」commit 误删了定义（用法残留），从删之前版本恢复。
// ⚠️ 上面 RollCallLanding 里的 Stat 统计卡 value 仍是硬编码假数据（本日実施 1/2 等），
//    「最近のセッション」表格也是假数据 —— 7-17 itsuki 已拍板（决策 5）：demo 账户显示假数据、
//    真账户接真后端数据（is_demo 双轨），实装待后端统计接口就绪后做。

// 当日统计卡
function Stat({
  label,
  value,
  suffix,
  color,
  note,
  onClick,
}: {
  label: string;
  value: string;
  suffix?: string;
  color?: string;
  note?: string;
  onClick?: () => void;
}) {
  const T = RYO;
  return (
    <button
      onClick={onClick}
      style={{
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        padding: "14px 16px",
        boxShadow: T.shadow1,
        textAlign: "left",
        fontFamily: "inherit",
        cursor: onClick ? "pointer" : "default",
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          letterSpacing: 1.2,
          fontWeight: 600,
          textTransform: "uppercase",
        }}
      >
        {label}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: 6,
          marginTop: 6,
        }}
      >
        <span
          style={{
            fontSize: 30,
            fontWeight: 700,
            color: color || T.ink,
            fontFamily: T.mono,
          }}
        >
          {value}
        </span>
        {suffix && (
          <span style={{ fontSize: 13, color: T.ink3, fontFamily: T.mono }}>
            {suffix}
          </span>
        )}
      </div>
      {note && (
        <div style={{ fontSize: 11, color: T.ink3, marginTop: 4 }}>{note}</div>
      )}
    </button>
  );
}
