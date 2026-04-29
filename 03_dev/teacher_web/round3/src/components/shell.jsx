// Shell — left nav + topbar with global search + WS indicator + logout.
// Used by all pages except /login, /login/select-teacher, /roll-call/live.

function Shell({ teacher, active, onNav, children, sessionActive, onLogout, onSwitchTeacher, onSearch, onResumeLive }) {
  const T = window.RYO;
  const [wsOk, setWsOk] = React.useState(true);
  const [q, setQ] = React.useState('');
  const [focused, setFocused] = React.useState(false);
  const [nowLabel, setNowLabel] = React.useState(() => formatNowJa());

  // Demo: simulate WS blip every 20s
  React.useEffect(() => { const id = setInterval(() => setWsOk(x => Math.random() > 0.05 ? true : x), 8000); return () => clearInterval(id); }, []);
  // Live clock for topbar
  React.useEffect(() => { const id = setInterval(() => setNowLabel(formatNowJa()), 30000); return () => clearInterval(id); }, []);
  // ⌘K focus
  React.useEffect(() => {
    const h = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); document.getElementById('global-search-input')?.focus(); } };
    window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h);
  }, []);

  const NAV = [
    ['roll-call', '点呼'],
    ['notifications', '通知', 7],
    ['discipline', '規律・処分'],
    ['applications', '申請', 3],
    ['records', '記録'],
    ['cleaning', '清掃確認'],
    ['info', 'お知らせ・バス'],
    ['community', 'コミュニティ管理'],
    ['front-desk', 'フロント業務'],
    ['accounts', '学生アカウント管理'],
  ];

  const pageLabel = {
    'roll-call': '点呼', notifications: '通知', discipline: '規律・処分',
    applications: '申請', records: '記録', cleaning: '清掃確認',
    info: 'お知らせ・バス', community: 'コミュニティ管理',
    'front-desk': 'フロント業務',
    accounts: '学生アカウント管理', search: '検索結果',
  }[active] || '';

  const normalize = (s) => (s || '').replace(/\s+/g, '').toLowerCase();
  const qn = normalize(q);
  const studentSuggestions = q.length > 0 ? (window.ROSTER_ALL || []).map(([room, id, name, dorm]) => ({
    label: name, meta: `${room}号室 · ${id}`, kind: 'student',
    hay: normalize(`${name}${room}${id}`),
  })).filter(s => s.hay.includes(qn)) : [];
  const extraSuggestions = q.length > 0 ? [
    { label: '2026-04-22', meta: '点呼記録 · 本日', kind: 'date', hay: '2026-04-22' },
    { label: '2026-04-21', meta: '点呼記録 · 昨日', kind: 'date', hay: '2026-04-21' },
  ].filter(s => s.hay.includes(qn)) : [];
  const suggestions = [...studentSuggestions, ...extraSuggestions].slice(0, 6);

  return (
    <div style={{ minHeight: '100vh', background: T.paper, color: T.ink, fontFamily: T.font, display: 'flex' }}>
      <aside style={{ width: 232, flexShrink: 0, background: T.surface, borderRight: `1px solid ${T.line}`, display: 'flex', flexDirection: 'column', position: 'sticky', top: 0, height: '100vh' }}>
        <div style={{ padding: '18px 20px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <img src={window.__resources.tomoshibiIcon} alt="" style={{ width: 30, height: 30, borderRadius: 8 }} />
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>Tomoshibi</div>
            <div style={{ fontSize: 10, color: T.ink3, marginTop: 1 }}>寮管理システム</div>
          </div>
        </div>
        <div style={{ height: 1, background: T.line }} />
        <nav style={{ padding: '10px 10px', flex: 1, overflowY: 'auto' }}>
          {NAV.map(([id, label, badge]) => {
            const isActive = id === active;
            return (
              <button key={id} onClick={() => onNav && onNav(id)} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                width: '100%', padding: '9px 12px', marginBottom: 2,
                background: isActive ? T.cobaltSoft : 'transparent',
                color: isActive ? T.cobaltDeep : T.ink2,
                fontFamily: 'inherit', fontSize: 13.5, fontWeight: isActive ? 600 : 500,
                border: 'none', borderRadius: 8, cursor: 'pointer', textAlign: 'left',
              }}>
                <span>{label}</span>
                {badge != null && <span style={{ fontSize: 11, background: isActive ? T.cobalt : T.lineStrong, color: '#fff', padding: '1px 8px', borderRadius: 10, fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{badge}</span>}
              </button>
            );
          })}
        </nav>
        <div style={{ padding: '12px 16px', borderTop: `1px solid ${T.line}`, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: 17, background: T.cobaltSoft, color: T.cobaltDeep, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, position: 'relative' }}>
            {teacher ? teacher.initial : '田'}
            <span title="当番中" style={{ position: 'absolute', bottom: -2, right: -2, width: 11, height: 11, borderRadius: 6, background: T.ok, border: '2px solid #fff' }} />
          </div>
          <div style={{ fontSize: 12, flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{teacher ? teacher.name : '—'} 先生</div>
            <div style={{ marginTop: 2 }}>
              <DormBadge dorm={teacher ? teacher.dorm : 'men'} />
            </div>
          </div>
          <button onClick={onSwitchTeacher} title="担当者切替" style={{ border: 'none', background: 'transparent', color: T.ink3, cursor: 'pointer', padding: 6, borderRadius: 6, fontSize: 11 }}>切替</button>
        </div>
      </aside>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <header style={{
          height: 60, borderBottom: `1px solid ${T.line}`, background: T.surface,
          display: 'flex', alignItems: 'center', padding: '0 24px', gap: 16,
          position: 'sticky', top: 0, zIndex: 5,
        }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: T.ink, minWidth: 100 }}>{pageLabel}</div>

          {/* Global search */}
          <div style={{ flex: 1, maxWidth: 520, position: 'relative' }}>
            <div style={{
              display: 'flex', alignItems: 'center', background: T.surfaceAlt, border: `1px solid ${focused ? T.cobalt : T.line}`,
              borderRadius: 10, padding: '0 10px', height: 38, gap: 8, transition: 'border-color .15s',
            }}>
              <span style={{ color: T.ink3, fontSize: 14 }}>🔍</span>
              <input id="global-search-input" value={q} onChange={e => setQ(e.target.value)}
                onFocus={() => setFocused(true)} onBlur={() => setTimeout(() => setFocused(false), 150)}
                onKeyDown={e => { if (e.key === 'Enter' && q.trim()) onSearch(q.trim()); }}
                placeholder="学生名・部屋番号・日付で検索..."
                style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontFamily: 'inherit', fontSize: 13, color: T.ink }} />
              <span style={{ fontFamily: T.mono, fontSize: 10, color: T.ink3, padding: '2px 6px', border: `1px solid ${T.line}`, borderRadius: 4, background: T.surface }}>⌘K</span>
            </div>
            {focused && suggestions.length > 0 && (
              <div style={{ position: 'absolute', top: 44, left: 0, right: 0, background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, boxShadow: T.shadow2, overflow: 'hidden', zIndex: 20 }}>
                {suggestions.map((s, i) => (
                  <div key={i} onMouseDown={() => onSearch(s.label)}
                    style={{ padding: '9px 12px', cursor: 'pointer', fontSize: 13, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: i > 0 ? `1px solid ${T.line}` : 'none' }}>
                    <span>{s.label}</span><span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>{s.meta}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={{ flex: 1 }} />
          {sessionActive && (
            <button onClick={onResumeLive} style={{
              display: 'flex', alignItems: 'center', gap: 8, padding: '5px 12px',
              background: T.okSoft, color: T.ok, borderRadius: 999, fontSize: 12, fontWeight: 600,
              border: `1px solid ${T.okBorder}`, fontFamily: 'inherit', cursor: 'pointer',
            }}>
              <span style={{ width: 8, height: 8, borderRadius: 4, background: T.ok, animation: 'pulse 1.6s infinite' }} />
              点呼実施中
            </button>
          )}
          <div title={wsOk ? 'サーバーに接続中' : '切断 · 再接続中'}
            style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: T.ink3 }}>
            <span style={{ width: 8, height: 8, borderRadius: 4, background: wsOk ? T.ok : T.danger, animation: wsOk ? 'none' : 'pulse 1s infinite' }} />
            <span style={{ fontFamily: T.mono }}>{wsOk ? 'ONLINE' : 'RECONN'}</span>
          </div>
          <div style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono }}>{nowLabel}</div>
          <button onClick={onLogout} style={{
            padding: '6px 10px', background: 'transparent', color: T.ink3,
            border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 11, cursor: 'pointer',
          }}>ログアウト</button>
        </header>
        <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
          {children}
          <div style={{ position: 'fixed', right: 14, bottom: 14, fontSize: 9, fontWeight: 700, color: T.warn, background: T.warnSoft, border: `1px solid ${T.warnBorder}`, padding: '3px 8px', borderRadius: 4, letterSpacing: 2, zIndex: 50, fontFamily: T.mono }}>DEMO</div>
        </div>
      </div>
    </div>
  );
}

function DormBadge({ dorm }) {
  const T = window.RYO;
  const isMen = dorm === 'men';
  return <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 4, letterSpacing: .5,
    background: isMen ? T.maleSoft : T.femaleSoft, color: isMen ? T.maleAccent : T.femaleAccent,
    border: `1px solid ${isMen ? T.maleAccent : T.femaleAccent}33` }}>{isMen ? '男性寮' : '女性寮'}</span>;
}

function formatNowJa() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const jaDay = ['日','月','火','水','木','金','土'][d.getDay()];
  return `${y}-${m}-${day}（${jaDay}） ${hh}:${mm}`;
}

window.Shell = Shell;
window.DormBadge = DormBadge;
