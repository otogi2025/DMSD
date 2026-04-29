// Roll-call landing + 7-day trend chart + session picker (4 types).

function RollCallLanding({ teacher, onStart, lastEnded, onNav, trend }) {
  const T = window.RYO;
  const [name, setName] = React.useState('晩点呼 · 普通寮生');
  const students = teacher.dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  const today = new Date();
  const todayLabel = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}（${['日','月','火','水','木','金','土'][today.getDay()]}）`;

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: -0.3 }}>点呼ダッシュボード</h1>
        <span style={{ fontSize: 12, color: T.ink3 }}>{todayLabel}</span>
      </div>
      <div style={{ color: T.ink2, fontSize: 13, marginBottom: 22 }}>対象 {students.length} 名 · {window.dormLabel(teacher.dorm)} · 舎監 {teacher.name} 先生</div>

      {/* Start card */}
      <div style={{
        background: T.surface, border: `1px solid ${T.line}`, borderRadius: 14,
        padding: '22px 24px', boxShadow: T.shadow1, marginBottom: 20,
        display: 'grid', gridTemplateColumns: '1fr auto', gap: 24, alignItems: 'center',
      }}>
        <div>
          <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>SESSION</div>
          <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>新しい点呼を開始</div>
          <div style={{ color: T.ink2, fontSize: 13, marginTop: 4 }}>「開始」を押すと {students.length} 名の座席表に切り替わります。</div>
          <div style={{ marginTop: 14, display: 'flex', gap: 10, alignItems: 'center' }}>
            <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600 }}>対象</label>
            <select value={name} onChange={e => setName(e.target.value)} style={{ padding: '7px 10px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, color: T.ink, outline: 'none' }}>
              <option>晩点呼 · 普通寮生</option>
              <option>晩点呼 · 部活生</option>
              <option>朝点呼 · 普通寮生</option>
              <option>朝点呼 · 部活生</option>
            </select>
          </div>
        </div>
        <button onClick={() => onStart(name)} style={{
          padding: '16px 36px', background: T.cobalt, color: '#fff', border: 'none',
          borderRadius: 12, fontFamily: 'inherit', fontSize: 16, fontWeight: 700, cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(43,77,140,.28)',
        }}>点呼を開始 →</button>
      </div>

      {/* Day stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <Stat label="本日実施" value="1" suffix="/ 2" note="朝点呼 完了" onClick={() => onNav('records')} />
        <Stat label="欠席者" value="2" color={T.danger} note="昨日は 1 名" onClick={() => onNav('records')} />
        <Stat label="審査待ち申請" value="3" color={T.cobalt} note="外泊 2 · 免除 1" onClick={() => onNav('applications')} />
        <Stat label="警告リスト" value="4" color={T.warn} note="今月累計" onClick={() => onNav('discipline')} />
      </div>

      {/* ⭐ Trend chart */}
      <TrendChart trend={trend} onBarClick={(d) => onNav('records', { date: d })} />

      {/* Recent sessions */}
      <div style={{ fontSize: 12, letterSpacing: 1.5, color: T.ink3, fontWeight: 700, textTransform: 'uppercase', marginBottom: 10, marginTop: 22 }}>最近のセッション</div>
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '110px 1fr 110px 110px 110px 90px', background: T.surfaceAlt, color: T.ink2, fontSize: 11, fontWeight: 600, letterSpacing: 1, borderBottom: `1px solid ${T.line}` }}>
          {['日付', '名称', '開始', '終了', '出席率', ''].map(h => <div key={h} style={{ padding: '10px 14px' }}>{h}</div>)}
        </div>
        {[
          lastEnded && ['2026-04-21', lastEnded.name, lastEnded.start, lastEnded.end, lastEnded.rate, '詳細'],
          ['2026-04-21', '朝点呼 · 普通寮生', '07:00', '07:08', '12/12', '詳細'],
          ['2026-04-20', '晩点呼 · 普通寮生', '19:30', '19:37', '11/12', '詳細'],
          ['2026-04-20', '朝点呼 · 普通寮生', '07:00', '07:09', '12/12', '詳細'],
        ].filter(Boolean).map(([d, n, s, e, r, a], i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 110px 110px 110px 90px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 13 }}>
            <div style={{ padding: '10px 14px', fontFamily: T.mono, color: T.ink3 }}>{d}</div>
            <div style={{ padding: '10px 14px', fontWeight: 500 }}>{n}</div>
            <div style={{ padding: '10px 14px', fontFamily: T.mono, color: T.ink2 }}>{s}</div>
            <div style={{ padding: '10px 14px', fontFamily: T.mono, color: T.ink2 }}>{e}</div>
            <div style={{ padding: '10px 14px', fontFamily: T.mono, fontWeight: 600 }}>{r}</div>
            <button onClick={() => onNav('records', { date: d })} style={{ padding: '10px 14px', color: T.cobalt, fontSize: 12, fontWeight: 600, cursor: 'pointer', background: 'transparent', border: 'none', fontFamily: 'inherit', textAlign: 'left' }}>{a} →</button>
          </div>
        ))}
      </div>

      {/* ⭐ 手机デモ用・iOS ショートカット貼り付け URL */}
      <ShortcutsDemoCard />
    </div>
  );
}

function ShortcutsDemoCard() {
  const T = window.RYO;
  const LS_KEY = 'tomoshibi.demo.host';
  const [host, setHost] = React.useState(() => localStorage.getItem(LS_KEY) || '192.168.1.100:8080');
  const [auto, setAuto] = React.useState(false); // true = サーバーが自動検出した IP
  const [no, setNo] = React.useState(window.DEMO_SEED_NO || ((window.ACCOUNTS || [{}])[0].no || ''));
  const [copied, setCopied] = React.useState(false);

  // demo_server.py の /api/server-info から LAN IP を自動取得（失敗時は手動入力にフォールバック）
  React.useEffect(() => {
    fetch('/api/server-info', { cache: 'no-store' })
      .then(r => r.ok ? r.json() : null)
      .then(info => {
        if (info && info.primary && info.port) {
          setHost(`${info.primary}:${info.port}`);
          setAuto(true);
        }
      })
      .catch(() => {});
  }, []);

  React.useEffect(() => { if (!auto) localStorage.setItem(LS_KEY, host); }, [host, auto]);

  const accounts = window.ACCOUNTS || [];
  const url = `http://${host}/checkin?no=${no}`;

  const copy = async () => {
    try { await navigator.clipboard.writeText(url); }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = url; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div style={{
      marginTop: 20, background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10,
      padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap',
    }}>
      <span style={{ fontSize: 11, color: T.ink3, fontWeight: 600 }}>📱 ショートカット URL</span>
      {auto ? (
        <span title="demo_server.py から自動検出" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '5px 10px', background: T.okSoft, color: T.ok, border: `1px solid ${T.okBorder}`, borderRadius: 6, fontFamily: T.mono, fontSize: 11, fontWeight: 600 }}>
          <span style={{ width: 6, height: 6, borderRadius: 3, background: T.ok }} />{host}
        </span>
      ) : (
        <input value={host} onChange={e => setHost(e.target.value)} placeholder="192.168.1.100:8080"
          style={{ width: 160, padding: '5px 8px', background: T.surfaceAlt, color: T.ink, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: T.mono, fontSize: 11, outline: 'none' }} />
      )}
      <select value={no} onChange={e => setNo(e.target.value)}
        style={{ padding: '5px 8px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, color: T.ink, outline: 'none' }}>
        {accounts.map(a => <option key={a.no} value={a.no}>{a.no} · {a.name}</option>)}
      </select>
      <div style={{ flex: 1, minWidth: 200, padding: '5px 10px', background: T.surfaceAlt, color: T.ink, border: `1px solid ${T.line}`, borderRadius: 6, fontFamily: T.mono, fontSize: 11, whiteSpace: 'nowrap', overflow: 'auto', userSelect: 'all' }}>{url}</div>
      <button onClick={copy} style={{
        padding: '5px 14px', background: copied ? T.ok : T.cobalt, color: '#fff',
        border: 'none', borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer', minWidth: 64,
      }}>{copied ? '✓' : 'コピー'}</button>
    </div>
  );
}

function Stat({ label, value, suffix, color, note, onClick }) {
  const T = window.RYO;
  return (
    <button onClick={onClick} style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '14px 16px', boxShadow: T.shadow1, textAlign: 'left', fontFamily: 'inherit', cursor: onClick ? 'pointer' : 'default' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 1.2, fontWeight: 600, textTransform: 'uppercase' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 6 }}>
        <span style={{ fontSize: 30, fontWeight: 700, color: color || T.ink, fontFamily: T.mono }}>{value}</span>
        {suffix && <span style={{ fontSize: 13, color: T.ink3, fontFamily: T.mono }}>{suffix}</span>}
      </div>
      {note && <div style={{ fontSize: 11, color: T.ink3, marginTop: 4 }}>{note}</div>}
    </button>
  );
}

function TrendChart({ trend, onBarClick }) {
  const T = window.RYO;
  const max = Math.max(3, ...trend.map(d => d.late + d.absent));
  const [hover, setHover] = React.useState(null);
  return (
    <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 22px', boxShadow: T.shadow1 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 14 }}>
        <div style={{ fontSize: 14, fontWeight: 700 }}>最近 7 日 遅刻・欠席トレンド</div>
        <div style={{ fontSize: 11, color: T.ink3 }}>バーをクリックで該当日の記録へ</div>
        <div style={{ flex: 1 }} />
        <Legend c={T.late} label="遅刻" />
        <Legend c={T.danger} label="欠席" />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${trend.length}, 1fr)`, gap: 10, alignItems: 'end', height: 140, position: 'relative' }}>
        {trend.map((d, i) => {
          const total = d.late + d.absent;
          const h = total === 0 ? 6 : (total / max) * 120;
          const lateH = total === 0 ? 0 : (d.late / max) * 120;
          const absH = total === 0 ? 0 : (d.absent / max) * 120;
          return (
            <button key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}
              onClick={() => onBarClick(d.date)}
              style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', padding: 0, fontFamily: 'inherit', position: 'relative', height: '100%' }}>
              {hover === i && (
                <div style={{ position: 'absolute', bottom: h + 10, background: T.ink, color: '#fff', fontSize: 11, padding: '5px 9px', borderRadius: 6, whiteSpace: 'nowrap', fontFamily: T.mono, zIndex: 2 }}>
                  {d.date} · 遅刻 {d.late} / 欠席 {d.absent}
                </div>
              )}
              <div style={{ width: '72%', maxWidth: 40, display: 'flex', flexDirection: 'column' }}>
                {d.absent > 0 && <div style={{ height: absH, background: T.danger, borderTopLeftRadius: 3, borderTopRightRadius: 3 }} />}
                {d.late > 0 && <div style={{ height: lateH, background: T.late, borderTopLeftRadius: d.absent === 0 ? 3 : 0, borderTopRightRadius: d.absent === 0 ? 3 : 0 }} />}
                {total === 0 && <div style={{ height: 4, background: T.line, borderRadius: 2 }} />}
              </div>
              <div style={{ fontSize: 10, color: T.ink3, marginTop: 6, fontFamily: T.mono }}>{d.date.slice(5)}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Legend({ c, label }) {
  const T = window.RYO;
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 11, color: T.ink2 }}>
    <span style={{ width: 10, height: 10, background: c, borderRadius: 2 }} />{label}
  </span>;
}

function NfcQuickUrlCard() {
  const T = window.RYO;
  const [info, setInfo] = React.useState(null);
  const [no, setNo] = React.useState(window.DEMO_SEED_NO || ((window.ACCOUNTS || [{}])[0].no || ''));
  const [copied, setCopied] = React.useState(false);

  React.useEffect(() => {
    fetch('/api/server-info', { cache: 'no-store' })
      .then(r => r.ok ? r.json() : null)
      .then(setInfo)
      .catch(() => setInfo(null));
  }, []);

  const fullUrl = info ? `http://${info.primary}:${info.port}/checkin?no=${no}` : '';

  const copy = async () => {
    if (!fullUrl) return;
    try { await navigator.clipboard.writeText(fullUrl); }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = fullUrl; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!info) return null;

  return (
    <div style={{
      background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10,
      padding: '10px 14px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10,
    }}>
      <select value={no} onChange={e => setNo(e.target.value)}
        style={{ padding: '6px 10px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 12, color: T.ink, outline: 'none', minWidth: 190 }}>
        {(window.ACCOUNTS || []).map(a => (
          <option key={a.no} value={a.no}>番号 {a.no} · {a.name}</option>
        ))}
      </select>
      <div style={{
        flex: 1, padding: '6px 10px', background: T.surfaceAlt, color: T.ink,
        border: `1px solid ${T.line}`, borderRadius: 6, fontFamily: T.mono, fontSize: 12,
        whiteSpace: 'nowrap', overflow: 'auto', userSelect: 'all',
      }}>{fullUrl}</div>
      <button onClick={copy} style={{
        padding: '6px 14px', background: copied ? T.ok : T.cobalt, color: '#fff',
        border: 'none', borderRadius: 6, fontFamily: 'inherit', fontSize: 12, fontWeight: 600, cursor: 'pointer',
        minWidth: 72,
      }}>{copied ? '✓' : 'コピー'}</button>
    </div>
  );
}

window.RollCallLanding = RollCallLanding;
window.NfcQuickUrlCard = NfcQuickUrlCard;
window.ShortcutsDemoCard = ShortcutsDemoCard;
