// 老师网站主题 token —— 从旧 index.html 的 theme.jsx 块原样搬（window.RYO + 全局常量 + dormLabel）
// 2026-08-06 视觉改造：配色源改为学生端 iOS App 的 TTokens.swift（青绿＋白），
// 旧「界面冻结铁律：配色值一字不改」已由项目负责人当面解除。

// Ryō 配色板（2026-08-06 对齐 iOS TTokens）
export const RYO = {
  paper: "#EFF2F3",
  surface: "#ffffff",
  surfaceAlt: "#F7FAFA",
  line: "#E2EAEC",
  lineStrong: "#C4D0D5",
  ink: "#0F1E22",
  ink2: "#2E4A52",
  ink3: "#56707A",
  muted: "#93A4AC",
  cobalt: "#1F6B74",
  cobaltDeep: "#0E3840",
  cobaltSoft: "#E3F1F3",
  // statuses
  ok: "#4A9478",
  okSoft: "#E3F1EA",
  okBorder: "#BCDCCB",
  late: "#D1984A",
  lateSoft: "#FDF4E1",
  lateBorder: "#EFDCB2",
  danger: "#C44848",
  dangerSoft: "#FDE8E8",
  dangerBorder: "#F2C7C7",
  info: "#1F6B74",
  infoSoft: "#E3F1F3",
  infoBorder: "#BCDDE1",
  warn: "#A9762C",
  warnSoft: "#FDF4E1",
  warnBorder: "#EFDCB2",
  graySoft: "#ECF1F2",
  grayBorder: "#D2DDDF",
  // women-dorm soft accent (for dorm badge)
  femaleAccent: "#9C5590",
  femaleSoft: "#F5E7F2",
  maleAccent: "#35707F",
  maleSoft: "#DFEEF1",
  font: '"Noto Sans JP","Hiragino Kaku Gothic ProN",-apple-system,BlinkMacSystemFont,sans-serif',
  mono: '"JetBrains Mono","SF Mono",ui-monospace,Menlo,monospace',
  shadow1: "0 1px 2px rgba(15,30,34,.05)",
  shadow2: "0 6px 20px rgba(15,30,34,.07), 0 1px 3px rgba(15,30,34,.04)",
  shadowModal: "0 24px 64px rgba(15,30,34,.22), 0 2px 8px rgba(15,30,34,.10)",

  // ── 新增：青绿强调色（源 iOS TTokens accent / accentSoft）
  accent: "#5FBEC8", // 亮青 — 渐变亮端、图标块、进度条
  accentSoft: "#A8DCE2", // 浅青 — 渐变中段、hover 底色
  accentPale: "#E8F6F7", // 极浅青 — 大面积浅底

  // ── 新增：渐变（照抄字符串，不要自己调角度）
  gradPrimary: "linear-gradient(135deg, #5FBEC8 0%, #1F6B74 100%)", // 主按钮 / 侧栏选中项
  gradPrimarySoft: "linear-gradient(135deg, #E8F6F7 0%, #DCF0F2 100%)", // 浅色信息卡
  gradPage: "linear-gradient(160deg, #F2F7F8 0%, #EFF4F5 45%, #EAF3F4 100%)", // 页面底
  gradOk: "linear-gradient(135deg, #7FC4A6 0%, #4A9478 100%)",
  gradWarn: "linear-gradient(135deg, #E9BE85 0%, #D1984A 100%)",
  gradDanger: "linear-gradient(135deg, #E08585 0%, #C44848 100%)",

  // ── 新增：玻璃质感
  glassBg: "rgba(255,255,255,.72)",
  glassBorder: "rgba(255,255,255,.86)",
  glassBlur: "blur(20px)",

  // ── 新增：卡片阴影两态
  shadowCard: "0 4px 16px rgba(15,30,34,.06), 0 1px 3px rgba(15,30,34,.04)",
  shadowCardHover:
    "0 12px 32px rgba(15,30,34,.10), 0 2px 6px rgba(15,30,34,.05)",
  shadowBtn: "0 2px 8px rgba(31,107,116,.24)",

  // ── 新增：统一过渡曲线
  ease: "all .22s cubic-bezier(.4,0,.2,1)",
} as const;

export type RyoTokens = typeof RYO;

// ── 样式配方 ── 组件里 style={{...S.card}} 直接展开使用。
// 目的：把「卡片 / 按钮 / 输入框」这类到处重复的内联样式收敛到一处，
// 以后调整视觉只改这里，不用再扫 26 个页面组件。
export const S = {
  // 过渡曲线 — 任何 hover / 状态变化都带上它
  ease: RYO.ease,

  // 卡片：白底 + 16 圆角 + 柔和阴影 + 极淡描边
  card: {
    background: RYO.surface,
    borderRadius: 16,
    border: `1px solid ${RYO.line}`,
    boxShadow: RYO.shadowCard,
    transition: RYO.ease,
  },
  // 卡片（可点击）：hover 抬起。配合 className="t-card" 使用
  cardHoverable: {
    background: RYO.surface,
    borderRadius: 16,
    border: `1px solid ${RYO.line}`,
    boxShadow: RYO.shadowCard,
    transition: RYO.ease,
    cursor: "pointer",
  },
  // 浅色信息卡（提示条 / 空状态）
  cardSoft: {
    background: RYO.gradPrimarySoft,
    borderRadius: 16,
    border: `1px solid ${RYO.infoBorder}`,
    boxShadow: "none",
  },
  // 玻璃面板：顶栏 / 悬浮工具条
  glass: {
    background: RYO.glassBg,
    backdropFilter: RYO.glassBlur,
    WebkitBackdropFilter: RYO.glassBlur,
    border: `1px solid ${RYO.glassBorder}`,
    boxShadow: RYO.shadowCard,
  },

  // 主按钮：渐变底 + 白字
  btnPrimary: {
    background: RYO.gradPrimary,
    color: "#fff",
    border: "none",
    borderRadius: 12,
    padding: "10px 20px",
    fontFamily: "inherit",
    fontSize: 13,
    fontWeight: 700,
    cursor: "pointer",
    boxShadow: RYO.shadowBtn,
    transition: RYO.ease,
  },
  // 次按钮：描边透明底
  btnGhost: {
    background: "transparent",
    color: RYO.ink,
    border: `1px solid ${RYO.lineStrong}`,
    borderRadius: 12,
    padding: "10px 20px",
    fontFamily: "inherit",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
    transition: RYO.ease,
  },
  // 危险按钮
  btnDanger: {
    background: RYO.gradDanger,
    color: "#fff",
    border: "none",
    borderRadius: 12,
    padding: "10px 20px",
    fontFamily: "inherit",
    fontSize: 13,
    fontWeight: 700,
    cursor: "pointer",
    boxShadow: "0 2px 8px rgba(196,72,72,.24)",
    transition: RYO.ease,
  },
  // 小按钮（表格行内操作）
  btnSmall: {
    background: RYO.surface,
    color: RYO.cobalt,
    border: `1px solid ${RYO.cobaltSoft}`,
    borderRadius: 8,
    padding: "5px 12px",
    fontFamily: "inherit",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
    transition: RYO.ease,
  },

  // 胶囊标签
  pill: {
    display: "inline-flex",
    alignItems: "center",
    gap: 4,
    borderRadius: 999,
    padding: "4px 12px",
    fontSize: 12,
    fontWeight: 600,
    border: "1px solid transparent",
  },

  // 输入框
  input: {
    background: RYO.surface,
    border: `1px solid ${RYO.line}`,
    borderRadius: 12,
    padding: "10px 14px",
    fontFamily: "inherit",
    fontSize: 13,
    color: RYO.ink,
    outline: "none",
    transition: RYO.ease,
  },

  // 表格表头
  tableHead: {
    background: RYO.surfaceAlt,
    color: RYO.ink3,
    fontSize: 12,
    fontWeight: 700,
    textAlign: "left" as const,
    padding: "10px 14px",
    borderBottom: `1px solid ${RYO.line}`,
  },

  // 弹窗外壳
  modal: {
    background: RYO.surface,
    borderRadius: 20,
    boxShadow: RYO.shadowModal,
    border: `1px solid ${RYO.glassBorder}`,
  },
  // 弹窗遮罩
  backdrop: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(15,30,34,.42)",
    backdropFilter: "blur(3px)",
    WebkitBackdropFilter: "blur(3px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
} as const;

// 渐变图标块 — 参考设计里统计卡左上角那个彩色圆角方块。
// 用法：<div style={iconTile(RYO.gradPrimary)}>{图标或文字}</div>
export function iconTile(gradient: string, size = 44) {
  return {
    width: size,
    height: size,
    borderRadius: size >= 40 ? 14 : 10,
    background: gradient,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontSize: size >= 40 ? 20 : 15,
    fontWeight: 700,
    flexShrink: 0,
    boxShadow: "0 4px 12px rgba(15,30,34,.12)",
  } as const;
}

// 寮标签转换: dorm 字段（"men"/"women"，由后端 assigned_dorm 派生 4→women/其他→men）→ 日语显示名「男子寮」「女子寮」
export function dormLabel(d: string): string {
  return d === "men" ? "男子寮" : "女子寮";
}

// App 全局常量
export const TIMEOUT_MS = 30 * 60 * 1000; // 30 分 — 无操作自动回登录页
export const TIMEOUT_WARN_MS = 25 * 60 * 1000; // 25 分 — 显示「あと 5 分」提示
export const API_BASE = "/api/v1"; // 同 origin 部署 + dev 走 vite proxy
// 版本号不再写死：由 Vite 构建时从仓库根 CHANGELOG.md 顶部注入（见 vite.config.ts readAppVersion）。
// 全局常量 __APP_VERSION__ 的类型声明在 src/vite-env.d.ts。发版重新构建网页即自动同步，不用手改。
export const APP_VERSION = __APP_VERSION__;
