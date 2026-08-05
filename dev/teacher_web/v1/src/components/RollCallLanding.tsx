import React from "react";
import { RYO, dormLabel } from "../theme";
import { api } from "../api/client";
import type { StudentAccountListOut } from "../api/types";
import { teacherLabel } from "../utils";

// 源 index.html 11940-12361（components/roll-call-landing.jsx 块）。
// 界面 100% 冻结，仅做作用域引用替换：window.RYO→RYO / window.tomoshibiApi→api / window.dormLabel→dormLabel。
// 点呼着陆页 + 统计/趋势图/最近点呼三块双轨（demo 演示数据 / 真账户「準備中」）+ 点呼类型选择（朝/夜 2 种）。
//
// 【双轨规则 —— itsuki 7-17 决策 5，8-02 实装】
// 「本日の統計」「遅刻・欠席トレンド」「最近の点呼」这三块没有对应的后端统计端点，数据只能是假的。
// 但假数据不该一刀切删掉：演示账号（App Store 审核员 / 给管理员看的 demo）需要看到
// 有内容的界面，真宿管老师则一个假数字都不能看到。所以按 teacher.is_demo 分轨：
//   is_demo === true  → 显示演示数据（统计卡和最近点呼表格直接内联在 JSX 里，
//                       趋势图数据见下面的 demoTrend）
//   否则（含取不到）  → 显示「準備中」占位
// 真接口做出来之后，真账户这一侧换成真数据，演示侧保持不变。
// ⚠️ 别再把演示数据整块删掉改成占位 —— 8-01 上线前审查干过一次，等于推翻 7-17 的决定。

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
  teacher: {
    name: string;
    assigned_dorm: number | null;
    dorm: string;
    // 演示账号标志（可空 = 旧会话存储恢复的老师对象可能没有，按 false 处理）
    is_demo?: boolean;
  };
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
  // 是不是演示账号 —— 决定「本日の統計」和「最近の点呼」显示演示数据还是「準備中」。
  // 取不到时按 false（真账户）处理：宁可少显示，也不能让真宿管老师看到编出来的数字。
  const isDemo = teacher.is_demo === true;
  // 演示用的 7 日趋势数据 —— 只在 isDemo 时渲染。
  // 日期按 JST 今天倒推 7 天动态生成，不写死具体日期：写死的话演示账号过几个月看到的
  // 就是一张停在旧月份的图（iOS 演示数据已经踩过这个坑）。数值固定，保证演示画面每次一样。
  const demoTrend = React.useMemo(() => {
    const counts = [
      { late: 1, absent: 0 },
      { late: 0, absent: 0 },
      { late: 2, absent: 1 },
      { late: 1, absent: 0 },
      { late: 0, absent: 0 },
      { late: 1, absent: 0 },
      { late: 0, absent: 1 },
    ];
    // 以 JST 当天为最后一根柱子，往前推 6 天。用 UTC 毫秒减法避免夏令时/时区跳变。
    const todayJst = new Date().toLocaleDateString("sv-SE", {
      timeZone: "Asia/Tokyo",
    });
    const base = new Date(`${todayJst}T00:00:00Z`).getTime();
    return counts.map((c, i) => ({
      date: new Date(base - (counts.length - 1 - i) * 86400000)
        .toISOString()
        .slice(0, 10),
      ...c,
    }));
  }, []);
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
        {teacherLabel(teacher.name)}
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

      {/* 当日统计（双轨，见文件头注释）：演示账号看 4 张演示卡，真账户看「準備中」*/}
      {isDemo ? (
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
      ) : (
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
      )}

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

      {/* 遅刻・欠席トレンド（双轨，见文件头注释）：演示账号看演示柱状图，真账户看「準備中」。
          web#45 当初把整个图删成占位，等于连演示侧一起砍了 —— 8-02 按双轨规则补回演示侧。*/}
      {isDemo ? (
        <TrendChart
          trend={demoTrend}
          onBarClick={(d) => onNav("records", { date: d })}
        />
      ) : (
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
      )}

      {/* 最近的点呼会话（双轨，见文件头注释）：演示账号看演示表格，真账户看「準備中」。
          注意演示表格第一行是 lastEnded —— 那是本次刚结束的真场次，不是假数据。*/}
      {isDemo ? (
        <>
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
              ["2026-04-21", "朝点呼", "07:00", "07:08", "12/12", "詳細"],
              ["2026-04-20", "夜点呼", "19:30", "19:37", "11/12", "詳細"],
              ["2026-04-20", "朝点呼", "07:00", "07:09", "12/12", "詳細"],
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
                  <div style={{ padding: "10px 14px", fontWeight: 500 }}>
                    {n}
                  </div>
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
        </>
      ) : (
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
      )}
    </div>
  );
}

// 当日统计卡 —— 只在演示账号下渲染（见文件头「双轨规则」）。
// 数值是硬编码演示数据，真账户走「準備中」分支，看不到这个组件。
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

// 一天的迟到 / 缺席条数
type TrendPoint = { date: string; late: number; absent: number };

// 7 日迟到/缺席趋势图 —— 只在演示账号下渲染（真账户走「準備中」占位，见文件头双轨规则）。
// 后端出统计接口后，真账户这一侧改成把真数据传进同一个组件即可，组件本身不用改。
function TrendChart({
  trend,
  onBarClick,
}: {
  trend: TrendPoint[];
  onBarClick: (date: string) => void;
}) {
  const T = RYO;
  const max = Math.max(3, ...trend.map((d) => d.late + d.absent));
  const [hover, setHover] = React.useState<number | null>(null);
  return (
    <div
      style={{
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        padding: "18px 22px",
        boxShadow: T.shadow1,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: 10,
          marginBottom: 14,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700 }}>
          最近 7 日 遅刻・欠席トレンド
        </div>
        <div style={{ fontSize: 11, color: T.ink3 }}>
          バーをクリックで該当日の記録へ
        </div>
        <div style={{ flex: 1 }} />
        <Legend c={T.late} label="遅刻" />
        <Legend c={T.danger} label="欠席" />
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${trend.length}, 1fr)`,
          gap: 10,
          alignItems: "end",
          height: 140,
          position: "relative",
        }}
      >
        {trend.map((d, i) => {
          const total = d.late + d.absent;
          const h = total === 0 ? 6 : (total / max) * 120;
          const lateH = total === 0 ? 0 : (d.late / max) * 120;
          const absH = total === 0 ? 0 : (d.absent / max) * 120;
          return (
            <button
              key={d.date}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onBarClick(d.date)}
              style={{
                background: "transparent",
                border: "none",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "flex-end",
                padding: 0,
                fontFamily: "inherit",
                position: "relative",
                height: "100%",
              }}
            >
              {hover === i && (
                <div
                  style={{
                    position: "absolute",
                    bottom: h + 10,
                    background: T.ink,
                    color: "#fff",
                    fontSize: 11,
                    padding: "5px 9px",
                    borderRadius: 6,
                    whiteSpace: "nowrap",
                    fontFamily: T.mono,
                    zIndex: 2,
                  }}
                >
                  {d.date} · 遅刻 {d.late} / 欠席 {d.absent}
                </div>
              )}
              <div
                style={{
                  width: "72%",
                  maxWidth: 40,
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {d.absent > 0 && (
                  <div
                    style={{
                      height: absH,
                      background: T.danger,
                      borderTopLeftRadius: 3,
                      borderTopRightRadius: 3,
                    }}
                  />
                )}
                {d.late > 0 && (
                  <div
                    style={{
                      height: lateH,
                      background: T.late,
                      borderTopLeftRadius: d.absent === 0 ? 3 : 0,
                      borderTopRightRadius: d.absent === 0 ? 3 : 0,
                    }}
                  />
                )}
                {total === 0 && (
                  <div
                    style={{
                      height: 4,
                      background: T.line,
                      borderRadius: 2,
                    }}
                  />
                )}
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: T.ink3,
                  marginTop: 6,
                  fontFamily: T.mono,
                }}
              >
                {d.date.slice(5)}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// 趋势图图例（色块 + 文字）
function Legend({ c, label }: { c: string; label: string }) {
  const T = RYO;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        fontSize: 11,
        color: T.ink2,
      }}
    >
      <span style={{ width: 10, height: 10, background: c, borderRadius: 2 }} />
      {label}
    </span>
  );
}
