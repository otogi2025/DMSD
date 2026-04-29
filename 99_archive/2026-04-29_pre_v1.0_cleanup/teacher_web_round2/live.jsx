// /roll-call/live — FULLSCREEN seat grid. No left nav. 学生が主役.
// Hierarchy per user: 氏名 largest, 部屋番号 smaller meta, 学籍番号 smallest mono.
// Status by background tint + subtle left accent bar. Badges never override main color.

function LiveRollCall({ sessionName, startedAt, students, onEnd, onOverride, onReset }) {
  const T = window.RYO;
  const [now, setNow] = React.useState(Date.now());
  React.useEffect(() => { const id = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(id); }, []);
  const elapsed = Math.max(0, Math.floor((now - startedAt) / 1000));
  const hh = String(Math.floor(elapsed / 3600)).padStart(2, '0');
  const mm = String(Math.floor(elapsed / 60) % 60).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');

  const cnt = students.reduce((a, s) => { a[s.status] = (a[s.status] || 0) + 1; return a; }, {});
  const done = (cnt.ok || 0) + (cnt.absent || 0) + (cnt.exempt || 0);
  const total = students.length;

  return (
    <div style={{
      minHeight: '100vh', background: T.paper, color: T.ink, fontFamily: T.font,
      display: 'flex', flexDirection: 'column',
    }}>
      {/* Minimal header bar — no nav, session info + end button */}
      <header style={{
        background: T.surface, borderBottom: `1px solid ${T.line}`,
        padding: '14px 28px', display: 'grid', gridTemplateColumns: 'auto 1fr auto', alignItems: 'center', gap: 20,
        boxShadow: T.shadow1,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: T.ink, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700 }}>◇</div>
          <div>
            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>LIVE SESSION</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 1 }}>{sessionName}　<span style={{ color: T.ink3, fontSize: 13, fontWeight: 500 }}>2026-04-21（火）</span></div>
          </div>
        </div>

        {/* Center: big metrics */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 36 }}>
          <Metric label="進捗" value={`${done}`} sub={`/ ${total}`} color={T.ink} />
          <Metric label="時間内" value={String(cnt.ok || 0)} color={T.ok} />
          <Metric label="欠席" value={String(cnt.absent || 0)} color={T.danger} />
          <Metric label="免除" value={String(cnt.exempt || 0)} color={T.info} />
          <Metric label="未点呼" value={String(cnt.unknown || 0)} color={T.ink3} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>経過時間</div>
            <div style={{ fontSize: 22, fontFamily: T.mono, fontWeight: 700, letterSpacing: 1, color: T.ink, fontFeatureSettings: '"tnum"' }}>
              {hh}:{mm}:{ss}
            </div>
          </div>
          <button onClick={onEnd} style={{
            padding: '11px 22px', background: T.danger, color: '#fff', border: 'none',
            borderRadius: 10, fontFamily: 'inherit', fontSize: 14, fontWeight: 700, cursor: 'pointer',
          }}>点呼を終了</button>
        </div>
      </header>

      {/* Legend strip */}
      <div style={{
        padding: '10px 28px', background: T.surfaceAlt, borderBottom: `1px solid ${T.line}`,
        display: 'flex', alignItems: 'center', gap: 20, fontSize: 12, color: T.ink2,
      }}>
        <span style={{ fontSize: 11, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>凡例</span>
        <Legend color={T.ok} label="時間内" />
        <Legend color={T.danger} label="欠席" />
        <Legend color={T.info} label="免除" />
        <Legend color={T.muted} label="未点呼" />
        <span style={{ width: 1, height: 16, background: T.line }} />
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Badge c={T.danger}>＋</Badge> 体調報告
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Badge c={T.warn}>?</Badge> 欠席届 審査中
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Badge c={T.ink2}>M</Badge> 手動調整
        </span>
        <div style={{ flex: 1 }} />
        <button onClick={onReset} style={{
          padding: '5px 12px', background: 'transparent', color: T.ink3,
          border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, cursor: 'pointer',
        }}>demo: データをリセット</button>
      </div>

      {/* SEAT GRID — 6 cols like user reference */}
      <div style={{ flex: 1, padding: '20px 28px 32px' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12,
        }}>
          {students.map(s => <SeatCard key={s.id} s={s} onClick={() => onOverride(s)} />)}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, sub, color }) {
  const T = window.RYO;
  return (
    <div style={{ textAlign: 'center', minWidth: 60 }}>
      <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 3, marginTop: 2 }}>
        <span style={{ fontSize: 22, fontFamily: T.mono, fontWeight: 700, color, fontFeatureSettings: '"tnum"' }}>{value}</span>
        {sub && <span style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono }}>{sub}</span>}
      </div>
    </div>
  );
}
function Legend({ color, label }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <span style={{ width: 10, height: 10, borderRadius: 3, background: color }} />
      {label}
    </span>
  );
}
function Badge({ c, children }) {
  return <span style={{
    fontSize: 9, fontWeight: 700, color: '#fff', background: c,
    width: 15, height: 15, borderRadius: 8, display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
  }}>{children}</span>;
}

// The signature seat card. Hierarchy:
//   氏名       : 24px bold  (dominant — 学生が主役)
//   部屋番号   : 11px mono  (meta, top-left)
//   学籍番号   : 10px mono  (meta, top-left, dimmer)
//   時刻/理由  : 11px mono  (bottom-left, status-colored)
function SeatCard({ s, onClick }) {
  const T = window.RYO;
  const map = {
    ok:      { fg: T.ok,      bg: T.okSoft,      bd: T.okBorder },
    absent:  { fg: T.danger,  bg: T.dangerSoft,  bd: T.dangerBorder },
    exempt:  { fg: T.info,    bg: T.infoSoft,    bd: T.infoBorder },
    unknown: { fg: T.ink3,    bg: T.surface,     bd: T.lineStrong },
  }[s.status];

  const statusText = s.status === 'ok' ? s.checkinAt
    : s.status === 'absent' ? '欠席'
    : s.status === 'exempt' ? (s.exemptReason || '免除')
    : (s.pending ? '審査中' : '未点呼');

  return (
    <button onClick={onClick} style={{
      position: 'relative', background: map.bg, border: `1px solid ${map.bd}`,
      borderLeft: `4px solid ${map.fg}`, borderRadius: 10, padding: '12px 16px 14px',
      boxShadow: T.shadow1, cursor: 'pointer', fontFamily: T.font,
      textAlign: 'left', minHeight: 106, transition: 'transform .12s, box-shadow .12s',
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
    }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = T.shadow2; e.currentTarget.style.transform = 'translateY(-1px)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = T.shadow1; e.currentTarget.style.transform = 'translateY(0)'; }}
    >
      {/* Top row: meta (small) + overlay badges */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
        <div>
          <div style={{ fontSize: 11, fontFamily: T.mono, color: T.ink2, fontWeight: 600, letterSpacing: 0.3 }}>{s.room}号室</div>
          <div style={{ fontSize: 10, fontFamily: T.mono, color: T.ink3, marginTop: 1 }}>{s.id}</div>
        </div>
        <div style={{ display: 'flex', gap: 3 }}>
          {s.health && <Badge c={T.danger}>＋</Badge>}
          {s.pending && <Badge c={T.warn}>?</Badge>}
          {s.override && <Badge c={T.ink2}>M</Badge>}
        </div>
      </div>

      {/* Hero: student name */}
      <div style={{
        fontSize: 24, fontWeight: 700, color: T.ink, lineHeight: 1.15,
        letterSpacing: -0.4, marginTop: 6,
      }}>{s.name}</div>

      {/* Status line */}
      <div style={{
        fontSize: 11, fontFamily: T.mono, color: map.fg, fontWeight: 600,
        marginTop: 6, letterSpacing: 0.3,
      }}>{statusText}</div>
    </button>
  );
}

window.LiveRollCall = LiveRollCall;
window.SeatCard = SeatCard;
