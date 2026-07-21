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
  // (b) 出发日所在周的周三 23:59（JST 固定，不依赖浏览器时区）。
  // 把 UTC 瞬时 +9h 平移到「JST 墙钟」，用 UTC 取值器算星期/设时分，再 -9h 还原成真实瞬时，
  // 这样海外浏览器（非 JST 时区）也算出同一个周三边界（C84）。
  const JST = 9 * 3600 * 1000;
  const wedJst = new Date(depart.getTime() + JST);
  const dow = wedJst.getUTCDay(); // 0=日, 1=月, ..., 3=水, ..., 6=土（JST 墙钟）
  const isoDow = dow === 0 ? 6 : dow - 1; // 0=周一
  const delta = 2 - isoDow; // 到周三的差
  wedJst.setUTCDate(wedJst.getUTCDate() + delta);
  wedJst.setUTCHours(23, 59, 59, 999); // JST 墙钟 23:59
  const wed = new Date(wedJst.getTime() - JST); // 还原成真实 UTC 瞬时
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
// 与 outstayDeadline 同法：+9h 平移到 JST 墙钟，再用 getUTC* 取值，避免浏览器非 JST 时偏一天。
export function formatJst(d: Date | null): string {
  if (!d) return "—";
  const j = new Date(d.getTime() + 9 * 3600 * 1000);
  const y = j.getUTCFullYear();
  const m = String(j.getUTCMonth() + 1).padStart(2, "0");
  const day = String(j.getUTCDate()).padStart(2, "0");
  const hh = String(j.getUTCHours()).padStart(2, "0");
  const mm = String(j.getUTCMinutes()).padStart(2, "0");
  const jaDow = ["日", "月", "火", "水", "木", "金", "土"][j.getUTCDay()];
  return `${y}-${m}-${day}（${jaDow}） ${hh}:${mm}`;
}

// 旧 index.html 里 window.formatJstDeadline 是 formatJst 的别名。
export const formatJstDeadline = formatJst;
