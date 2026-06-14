// 跨页共用的 JST(日本标准时间) 工具函数 —— 从旧 index.html applications 块原样搬。
// 出寮届「48 小时前 / 当周周三 23:59 取早」的提出期限计算 + 日本时间解析/格式化。

// 解析日本时间字符串。接受 'YYYY-MM-DD HH:MM' 或 'MM-DD HH:MM'（后者按 2026 年处理）。
export function parseJst(s: string | null | undefined): Date | null {
  const full = s && s.length <= 11 ? "2026-" + s : s;
  return full ? new Date(full.replace(" ", "T") + ":00+09:00") : null;
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
