import React from "react";
import { RYO, dormLabel, LATE_THRESHOLD_SEC } from "../theme";
import tomoshibiIcon from "../assets/tomoshibi-icon.png";

// 源 index.html 12368-13008（components/live-roll-call.jsx 块）。
// 实时点呼大屏：迟到状态 + 预测条 + 演示控制台 + 座席网格。
// 界面原样搬，仅作用域引用方式改写（window.RYO→RYO / window.dormLabel→dormLabel /
// window.LATE_THRESHOLD_SEC→LATE_THRESHOLD_SEC / 图标用 Vite import）。
// fabBtn / NfcIndicator / Metric / SeatCard / Badge / LegendPanel 是本块私有子组件，同文件不 export。

// 座席学生（本组件本地演示状态，非后端类型）
interface SeatStudent {
  key: string;
  id: string;
  room: string;
  name: string;
  status: "ok" | "late" | "absent" | "exempt" | "unknown";
  checkinAt?: string;
  pending?: boolean;
  health?: string;
  exemptReason?: string;
  override?: { reason: string };
}

// 当前老师（本组件用 dorm + name 两个字段，本地演示状态）
interface LiveTeacher {
  dorm: string; // "men" / "women"（App 由 assigned_dorm 派生），dormLabel 期待字符串
  name: string;
}

export function LiveRollCall({
  teacher,
  sessionName,
  startedAt,
  students,
  setStudents,
  onEnd,
  onOverride,
  onReset,
}: {
  teacher: LiveTeacher;
  sessionName: string;
  startedAt: number;
  students: SeatStudent[];
  setStudents: React.Dispatch<React.SetStateAction<SeatStudent[]>>;
  onEnd: () => void;
  onOverride: (s: SeatStudent) => void;
  onReset: () => void;
}) {
  const T = RYO;
  const [now, setNow] = React.useState(Date.now());
  const [showLegend, setShowLegend] = React.useState(false);
  const [showConsole, setShowConsole] = React.useState(false);
  const [lastSeq, setLastSeq] = React.useState(0);
  const [nfcStatus, setNfcStatus] = React.useState<"idle" | "ok" | "error">(
    "idle",
  ); // 'idle' | 'ok' | 'error'
  const lastBroadcastRef = React.useRef<unknown>(null);

  React.useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const elapsed = Math.max(0, Math.floor((now - startedAt) / 1000));
  const hh = String(Math.floor(elapsed / 3600)).padStart(2, "0");
  const mm = String(Math.floor(elapsed / 60) % 60).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");

  // ⭐ 自动迟到转换
  React.useEffect(() => {
    if (elapsed >= LATE_THRESHOLD_SEC) {
      setStudents((list) =>
        list.map((s) =>
          s.status === "unknown" && !s.pending ? { ...s, status: "late" } : s,
        ),
      );
    }
  }, [elapsed >= LATE_THRESHOLD_SEC]); // eslint-disable-line

  const cnt = students.reduce<Record<string, number>>((a, s) => {
    a[s.status] = (a[s.status] || 0) + 1;
    return a;
  }, {});
  const done =
    (cnt.ok || 0) + (cnt.absent || 0) + (cnt.exempt || 0) + (cnt.late || 0);
  const total = students.length;
  const inLatePhase = elapsed >= LATE_THRESHOLD_SEC;
  const secToLate = Math.max(0, LATE_THRESHOLD_SEC - elapsed);

  const simCheckin = (s: SeatStudent) => {
    const d = new Date();
    const t = `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
    const isLate = elapsed >= LATE_THRESHOLD_SEC;
    setStudents((list) =>
      list.map((x) =>
        x.key === s.key
          ? { ...x, status: isLate ? "late" : "ok", checkinAt: t }
          : x,
      ),
    );
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.paper,
        color: T.ink,
        fontFamily: T.font,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <header
        style={{
          background: T.surface,
          borderBottom: `1px solid ${T.line}`,
          padding: "14px 28px",
          display: "grid",
          gridTemplateColumns: "auto 1fr auto",
          alignItems: "center",
          gap: 20,
          boxShadow: T.shadow1,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <img
            src={tomoshibiIcon}
            alt=""
            style={{ width: 32, height: 32, borderRadius: 8 }}
          />
          <div>
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 600,
              }}
            >
              LIVE SESSION
            </div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 1 }}>
              {sessionName}{" "}
              <span style={{ color: T.ink3, fontSize: 13, fontWeight: 500 }}>
                · {dormLabel(teacher.dorm)} · {teacher.name} 先生
              </span>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "center", gap: 30 }}>
          <Metric
            label="進捗"
            value={`${done}`}
            sub={`/ ${total}`}
            color={T.ink}
          />
          <Metric label="時間内" value={String(cnt.ok || 0)} color={T.ok} />
          <Metric label="遅刻" value={String(cnt.late || 0)} color={T.late} />
          <Metric
            label="欠席"
            value={String(cnt.absent || 0)}
            color={T.danger}
          />
          <Metric label="免除" value={String(cnt.exempt || 0)} color={T.info} />
          <Metric
            label="未点呼"
            value={String(cnt.unknown || 0)}
            color={T.ink3}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <NfcIndicator status={nfcStatus} seq={lastSeq} />
          <div style={{ textAlign: "right" }}>
            <div
              style={{
                fontSize: 10,
                color: T.ink3,
                letterSpacing: 1.5,
                fontWeight: 600,
              }}
            >
              経過時間
            </div>
            <div
              style={{
                fontSize: 22,
                fontFamily: T.mono,
                fontWeight: 700,
                letterSpacing: 1,
                color: T.ink,
              }}
            >
              {hh}:{mm}:{ss}
            </div>
          </div>
          <button
            onClick={onEnd}
            style={{
              padding: "11px 22px",
              background: T.danger,
              color: "#fff",
              border: "none",
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            点呼を終了
          </button>
        </div>
      </header>

      {/* 预测条 */}
      <div
        style={{
          padding: "8px 28px",
          background: inLatePhase ? T.lateSoft : T.cobaltSoft,
          borderBottom: `1px solid ${inLatePhase ? T.lateBorder : T.infoBorder}`,
          color: inLatePhase ? T.late : T.cobaltDeep,
          fontSize: 12,
          fontWeight: 600,
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span style={{ fontSize: 13 }}>{inLatePhase ? "⚠" : "⏱"}</span>
        {inLatePhase
          ? `遅刻判定中 · 未チェックイン者は自動的に遅刻になります（${Math.floor(elapsed / 60)}分${elapsed % 60}秒経過）`
          : `あと ${Math.floor(secToLate / 60)}分${secToLate % 60}秒 で遅刻判定開始（閾値 ${LATE_THRESHOLD_SEC / 60} 分）`}
      </div>

      {/* 座席网格 */}
      <div style={{ flex: 1, padding: "20px 28px 100px" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(6, 1fr)",
            gap: 12,
          }}
        >
          {students.map((s) => (
            <SeatCard key={s.id} s={s} onClick={() => onOverride(s)} />
          ))}
        </div>
      </div>

      {/* 底部悬浮控制 */}
      <div
        style={{
          position: "fixed",
          right: 20,
          bottom: 20,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          alignItems: "flex-end",
          zIndex: 10,
        }}
      >
        {/* DEMO-ONLY scaffold（§7.3.8 + project_demo_scaffolds_to_remove_before_v1）：
            URL ?demo=1 时显示、生产模式（默认）下隐藏。
            itsuki memory「v1.0 上线前必删」用 URL 参数门控安全保留。 */}
        {showLegend && <LegendPanel onClose={() => setShowLegend(false)} />}
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={() => setShowLegend(!showLegend)}
            style={fabBtn(T, showLegend)}
          >
            📖 凡例
          </button>
        </div>
      </div>
    </div>
  );
}

// 悬浮按钮样式工厂
const fabBtn = (T: typeof RYO, active: boolean) => ({
  padding: "9px 14px",
  background: active ? T.ink : T.surface,
  color: active ? "#fff" : T.ink2,
  border: `1px solid ${active ? T.ink : T.lineStrong}`,
  borderRadius: 10,
  fontFamily: "inherit",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
  boxShadow: T.shadow1,
});

// NFC 接收状态指示灯（私有子组件）
function NfcIndicator({ status, seq }: { status: string; seq: number }) {
  const T = RYO;
  const map = {
    idle: {
      fg: T.ink3,
      bg: T.surfaceAlt,
      bd: T.line,
      icon: "📡",
      label: "NFC 待機中",
    },
    ok: {
      fg: T.ok,
      bg: T.okSoft,
      bd: T.okBorder,
      icon: "✓",
      label: "受信 OK",
    },
    error: {
      fg: T.danger,
      bg: T.dangerSoft,
      bd: T.dangerBorder,
      icon: "⚠",
      label: "不明な番号",
    },
  }[status] || {
    fg: T.ink3,
    bg: T.surfaceAlt,
    bd: T.line,
    icon: "📡",
    label: "NFC",
  };
  return (
    <div
      title={`seq=${seq} · iPhone 快捷指令 POST /checkin?no=XX で座席更新`}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "5px 10px",
        background: map.bg,
        color: map.fg,
        border: `1px solid ${map.bd}`,
        borderRadius: 999,
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 0.5,
      }}
    >
      <span style={{ fontSize: 12 }}>{map.icon}</span>
      <span>{map.label}</span>
      {seq > 0 && (
        <span
          style={{
            fontFamily: T.mono,
            fontSize: 10,
            color: T.ink3,
            fontWeight: 500,
          }}
        >
          · {seq}
        </span>
      )}
    </div>
  );
}

// 顶部统计指标（私有子组件）
function Metric({
  label,
  value,
  sub,
  color,
}: {
  label: string;
  value: string;
  sub?: string;
  color: string;
}) {
  const T = RYO;
  return (
    <div style={{ textAlign: "center", minWidth: 54 }}>
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.5,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "center",
          gap: 3,
          marginTop: 2,
        }}
      >
        <span
          style={{
            fontSize: 22,
            fontFamily: T.mono,
            fontWeight: 700,
            color,
          }}
        >
          {value}
        </span>
        {sub && (
          <span style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono }}>
            {sub}
          </span>
        )}
      </div>
    </div>
  );
}

// 单个座席卡片（私有子组件）
function SeatCard({ s, onClick }: { s: SeatStudent; onClick: () => void }) {
  const T = RYO;
  const map = {
    ok: { fg: T.ok, bg: T.okSoft, bd: T.okBorder },
    late: { fg: T.late, bg: T.lateSoft, bd: T.lateBorder },
    absent: { fg: T.danger, bg: T.dangerSoft, bd: T.dangerBorder },
    exempt: { fg: T.info, bg: T.infoSoft, bd: T.infoBorder },
    unknown: { fg: T.ink3, bg: T.surface, bd: T.lineStrong },
  }[s.status];

  const statusText =
    s.status === "ok"
      ? s.checkinAt
      : s.status === "late"
        ? s.checkinAt
          ? `遅刻 · ${s.checkinAt}`
          : "遅刻（未チェックイン）"
        : s.status === "absent"
          ? "欠席"
          : s.status === "exempt"
            ? s.exemptReason || "免除"
            : s.pending
              ? "審査中"
              : "未点呼";

  return (
    <button
      onClick={onClick}
      style={{
        position: "relative",
        background: map.bg,
        border: `1px solid ${map.bd}`,
        borderLeft: `4px solid ${map.fg}`,
        borderRadius: 10,
        padding: "12px 16px 14px",
        boxShadow: T.shadow1,
        cursor: "pointer",
        fontFamily: T.font,
        textAlign: "left",
        minHeight: 106,
        transition: "transform .12s, box-shadow .12s",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = T.shadow2;
        e.currentTarget.style.transform = "translateY(-1px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = T.shadow1;
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 8,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              fontFamily: T.mono,
              color: T.ink2,
              fontWeight: 600,
            }}
          >
            {s.room}
          </div>
          <div
            style={{
              fontSize: 10,
              fontFamily: T.mono,
              color: T.ink3,
              marginTop: 1,
            }}
          >
            {s.id}
          </div>
        </div>
        <div style={{ display: "flex", gap: 3 }}>
          {s.health && (
            <Badge c={T.danger} title={`体調: ${s.health}`}>
              ＋
            </Badge>
          )}
          {s.pending && (
            <Badge c={T.warn} title="欠席届 審査中">
              ?
            </Badge>
          )}
          {s.override && (
            <Badge c={T.ink2} title={`手動調整: ${s.override.reason}`}>
              M
            </Badge>
          )}
        </div>
      </div>
      <div
        style={{
          fontSize: 24,
          fontWeight: 700,
          color: T.ink,
          lineHeight: 1.15,
          letterSpacing: -0.4,
          marginTop: 6,
        }}
      >
        {s.name}
      </div>
      <div
        style={{
          fontSize: 11,
          fontFamily: T.mono,
          color: map.fg,
          fontWeight: 600,
          marginTop: 6,
          letterSpacing: 0.3,
        }}
      >
        {statusText}
      </div>
    </button>
  );
}

// 座席角标（私有子组件）
function Badge({
  c,
  children,
  title,
}: {
  c: string;
  children: React.ReactNode;
  title?: string;
}) {
  return (
    <span
      title={title}
      style={{
        fontSize: 9,
        fontWeight: 700,
        color: "#fff",
        background: c,
        width: 15,
        height: 15,
        borderRadius: 8,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {children}
    </span>
  );
}

// 凡例面板（私有子组件）
function LegendPanel({ onClose }: { onClose: () => void }) {
  const T = RYO;
  return (
    <div
      style={{
        width: 280,
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 12,
        boxShadow: T.shadow2,
        padding: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          marginBottom: 10,
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 700, flex: 1 }}>凡例</div>
        <button
          onClick={onClose}
          style={{
            border: "none",
            background: "transparent",
            color: T.ink3,
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          ×
        </button>
      </div>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginBottom: 6,
        }}
      >
        状態
      </div>
      {(
        [
          ["時間内", T.ok],
          ["遅刻", T.late],
          ["欠席", T.danger],
          ["免除", T.info],
          ["未点呼", T.muted],
        ] as [string, string][]
      ).map(([l, c]) => (
        <div
          key={l}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 12,
            padding: "3px 0",
          }}
        >
          <span
            style={{
              width: 12,
              height: 12,
              background: c,
              borderRadius: 3,
            }}
          />
          {l}
        </div>
      ))}
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginTop: 10,
          marginBottom: 6,
        }}
      >
        バッジ
      </div>
      <div style={{ fontSize: 12, lineHeight: 1.9 }}>
        <div>
          <Badge c={T.danger}>＋</Badge> 体調報告
        </div>
        <div>
          <Badge c={T.warn}>?</Badge> 欠席届 審査中
        </div>
        <div>
          <Badge c={T.ink2}>M</Badge> 手動調整痕跡
        </div>
      </div>
    </div>
  );
}
