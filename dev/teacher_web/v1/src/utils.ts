// 跨页共用的 JST(日本标准时间) 工具函数 —— 从旧 index.html applications 块原样搬。
// 出寮届「48 小时前 / 当周周三 23:59 取早」的提出期限计算 + 日本时间解析/格式化。

// 解析日本时间字符串。接受多种形态：
//  - 后端 ISO datetime（带 Z 或 ±HH:MM 时区，如 submitted_at "2026-06-05T08:30:00Z"）→ 直接按其时区解析
//  - 后端 'YYYY-MM-DD HH:MM:SS'（leave_date+leave_time 拼接，无时区）→ 当作 JST(+09:00)
//  - 旧 demo 'YYYY-MM-DD HH:MM' / 'MM-DD HH:MM'（分精度，后者按 2026 年处理）→ 补秒后当作 JST
// 旧实现无条件追加 ":00+09:00"，对带秒/带 Z 的真实后端数据会产出 Invalid Date（期限徽章因此恒为「期限内」）。
export function parseJst(s: string | null | undefined): Date | null {
  if (!s) return null;
  // 已带时区信息（ISO 带 Z 或 ±HH:MM）→ 原样解析，不要再拼 JST
  if (/[zZ]$/.test(s) || /[+-]\d\d:?\d\d$/.test(s)) {
    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
  }
  // 无时区：可能是 'YYYY-MM-DD ...' 或旧的 'MM-DD HH:MM'（≤11 字符补年份）
  let full = s.length <= 11 ? "2026-" + s : s;
  full = full.replace(" ", "T");
  // 仅到分（HH:MM）时补秒，避免 "T17:30+09:00" 这类非法串
  if (/T\d\d:\d\d$/.test(full)) full += ":00";
  const d = new Date(full + "+09:00");
  return isNaN(d.getTime()) ? null : d;
}

// 出寮届提出期限 = (a)出发 48 小时前 与 (b)出发日所在周的周三 23:59 取较早者。
export function outstayDeadline(departStr: string): Date | null {
  const depart = parseJst(departStr);
  if (!depart) return null;
  // (a) 出发 48 小时前
  const h48 = new Date(depart.getTime() - 48 * 3600 * 1000);
  // (b) 出发日所在周的周三 23:59（周始 = 周一的 ISO 方式）
  const wed = new Date(depart);
  const dow = wed.getDay(); // 0=日, 1=月, ..., 3=水, ..., 6=土
  const isoDow = dow === 0 ? 6 : dow - 1; // 0=周一
  const delta = 2 - isoDow; // 到周三的差
  wed.setDate(wed.getDate() + delta);
  wed.setHours(23, 59, 59, 999);
  return wed < h48 ? wed : h48;
}

// 是否逾期提出（提出时刻晚于期限）。
export function isLateSubmission(
  departStr: string,
  submittedStr: string,
): boolean {
  const deadline = outstayDeadline(departStr);
  const submitted = parseJst(submittedStr);
  if (!deadline || !submitted) return false;
  return submitted > deadline;
}

// 格式化日本时间 → "2026-06-05（金） 17:30"。
export function formatJst(d: Date | null): string {
  if (!d) return "—";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const jaDow = ["日", "月", "火", "水", "木", "金", "土"][d.getDay()];
  return `${y}-${m}-${day}（${jaDow}） ${hh}:${mm}`;
}

// 旧 index.html 里 window.formatJstDeadline 是 formatJst 的别名。
export const formatJstDeadline = formatJst;
