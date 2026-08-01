import React from "react";
import { RYO, dormLabel } from "../theme";
import { api } from "../api/client";
import type { StudentAccountListOut } from "../api/types";

// 源 index.html 11940-12361（components/roll-call-landing.jsx 块）。
// 界面 100% 冻结，仅做作用域引用替换：window.RYO→RYO / window.tomoshibiApi→api / window.dormLabel→dormLabel。
// 点呼着陆页 + 趋势图/统计/最近点呼占位（去假数据）+ 点呼类型选择（朝/夜 2 种）。

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
  // 选项文字须含「朝」才被 App.tsx startSession 判为 morning；「夜点呼」不含 → evening。
  // 后端只有 morning/evening 两种场次，部活生不是独立场次（勿再加回）。
  const [name, setName] = React.useState("夜点呼");
  // 从后端取可见范围内学生人数（替代假名单 window.ROSTER_MEN/WOMEN）
  const [studentCount, setStudentCount] = React.useState<number | null>(null);
  React.useEffect(() => {
    if (!authToken) return;
    let cancelled = false;
    // 不传 dorm_unit：后端 list_students 已用 dorm_units_for_teacher 按令牌可见范围过滤
    // （选 1/2 寮 → [1,2]；选 4 寮 → [4]）。若传单一 assigned_dorm=1 会漏掉二寮人数。
    // TODO(web#114)：client.listStudents 入参无 limit，后端默认 limit=1000 且
    // res.total === items.length（同被封顶），超 1000 人会截断。本批禁改 client.ts，
    // 真寮规模远低于 1000，暂用 items.length；要修需给 listStudents 加 limit 或真分页/count。
    api
      .listStudents({}, authToken)
      .then((res: StudentAccountListOut) => {
        if (!cancelled) setStudentCount((res.items || []).length);
      })
      .catch(() => {
        if (!cancelled) setStudentCount(null);
      });
    return () => {
      cancelled = true;
    };
  }, [authToken]);
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
        対象 {studentCount ?? "—"} 名 · {dormLabel(teacher.dorm)} · 寮監{" "}
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
            新学年です。「寮生アカウント管理」から学年更新を開始してください。
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
              寮生管理へ
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
              <option>夜点呼</option>
              <option>朝点呼</option>
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

      {/* 当日统计：无统计后端端点 → 假数字改为「準備中」占位（与下方趋势图同款）*/}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 22px",
          boxShadow: T.shadow1,
          marginBottom: 20,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
          本日の統計
        </div>
        <div style={{ fontSize: 13, color: T.ink3 }}>準備中</div>
      </div>

      {/* 学生からの報告 入口 —— 点呼时学生上报的体调/欠席等，老师在这里处理。
          后端 GET /rollcall/reports 早已实装、此前网页无入口（grok 三方对齐审查发现）。 */}
      {onNav && (
        <button
          onClick={() => onNav("rollcall-reports")}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
            padding: "14px 20px",
            marginBottom: 20,
            fontFamily: "inherit",
            cursor: "pointer",
            boxShadow: T.shadow1,
            textAlign: "left",
          }}
        >
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: T.ink }}>
              寮生からの報告
            </div>
            <div style={{ fontSize: 12, color: T.ink3, marginTop: 3 }}>
              点呼時に提出された体調不良・欠席などの報告を確認・対応します
            </div>
          </div>
          <span style={{ color: T.cobalt, fontSize: 14, fontWeight: 700 }}>
            確認する →
          </span>
        </button>
      )}

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

      {/* 最近的点呼会话：无历史列表后端端点 → 假行改为「準備中」占位（与趋势图同款）*/}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "18px 22px",
          boxShadow: T.shadow1,
          marginTop: 22,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
          最近の点呼
        </div>
        <div style={{ fontSize: 13, color: T.ink3 }}>準備中</div>
      </div>
    </div>
  );
}

// 「本日の統計」/「最近の点呼」/「トレンド」均已改为「準備中」占位（无对应统计/历史后端端点）。
// 接真数据需后端新增统计接口后再做；本文件不再放硬编码假数字。
