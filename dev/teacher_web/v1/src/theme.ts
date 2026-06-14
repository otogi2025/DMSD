// 老师网站主题 token —— 从旧 index.html 的 theme.jsx 块原样搬（window.RYO + 全局常量 + dormLabel）
// 界面冻结铁律：配色值一字不改。

// Ryō 配色板（Round 3，扩展自 Round 2 tokens）
export const RYO = {
  paper: "#f4f5f7",
  surface: "#ffffff",
  surfaceAlt: "#f9fafb",
  line: "#e3e5eb",
  lineStrong: "#cdd0d8",
  ink: "#14171f",
  ink2: "#3a404d",
  ink3: "#6a6f7d",
  muted: "#9ea3ae",
  cobalt: "#2b4d8c",
  cobaltDeep: "#1c3567",
  cobaltSoft: "#e5ebf5",
  // statuses
  ok: "#2f7a55",
  okSoft: "#dfefe5",
  okBorder: "#b7d7c4",
  late: "#b8871f",
  lateSoft: "#f6e8c4",
  lateBorder: "#e5c98a",
  danger: "#b33a3a",
  dangerSoft: "#f3dcdc",
  dangerBorder: "#e3b3b3",
  info: "#2b4d8c",
  infoSoft: "#dde4f1",
  infoBorder: "#bdcae1",
  warn: "#a56b1e",
  warnSoft: "#f2e3cb",
  warnBorder: "#e6c98f",
  graySoft: "#ebedf1",
  grayBorder: "#d5d8df",
  // women-dorm soft accent (for dorm badge)
  femaleAccent: "#a4478e",
  femaleSoft: "#f3e2ee",
  maleAccent: "#3a6a8f",
  maleSoft: "#dfeaf3",
  font: '"Noto Sans JP","Hiragino Kaku Gothic ProN",-apple-system,BlinkMacSystemFont,sans-serif',
  mono: '"JetBrains Mono","SF Mono",ui-monospace,Menlo,monospace',
  shadow1: "0 1px 2px rgba(20,23,31,.04)",
  shadow2: "0 4px 16px rgba(20,23,31,.08), 0 1px 2px rgba(20,23,31,.04)",
  shadowModal: "0 24px 64px rgba(20,23,31,.28), 0 2px 8px rgba(20,23,31,.12)",
} as const;

export type RyoTokens = typeof RYO;

// 寮标签转换: dorm 字段（"men"/"women"，由后端 assigned_dorm 派生 4→women/其他→men）→ 日语显示名「男子寮」「女子寮」
export function dormLabel(d: string): string {
  return d === "men" ? "男子寮" : "女子寮";
}

// App 全局常量
export const TIMEOUT_MS = 30 * 60 * 1000; // 30 分 — 无操作自动回登录页
export const TIMEOUT_WARN_MS = 25 * 60 * 1000; // 25 分 — 显示「あと 5 分」提示
export const LATE_THRESHOLD_SEC = 180; // 3 分 — 迟到自动转换阈值
export const API_BASE = "/api/v1"; // 同 origin 部署 + dev 走 vite proxy
export const APP_VERSION = "v0.23.0";
