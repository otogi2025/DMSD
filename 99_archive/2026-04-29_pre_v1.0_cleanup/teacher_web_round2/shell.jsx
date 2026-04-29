// Shell — left nav (Ryo) + topbar + content slot.
// Used on /roll-call landing and everywhere nav is visible.
// /roll-call/live (fullscreen live seat grid) does NOT use this shell.

function Shell({ user, active, onNav, children, sessionActive, onLogout }) {
  const T = window.RYO;
  const NAV = [
    ['roll-call', '点呼', null, true],
    ['notifications', '通知', 7],
    ['discipline', '規律・処分', null],
    ['applications', '申請', 3],
    ['cleaning', '清掃確認', null],
    ['info', 'お知らせ・バス', null],
    ['community', '寮コミュニティ', null],
  ];

  return (
    <div style={{
      minHeight: '100vh', background: T.paper, color: T.ink, fontFamily: T.font,
      display: 'flex',
    }}>
      <aside style={{
        width: 232, flexShrink: 0, background: T.surface, borderRight: `1px solid ${T.line}`,
        display: 'flex', flexDirection: 'column', position: 'sticky', top: 0, height: '100vh',
      }}>
        <div style={{ padding: '20px 20px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 30, height: 30, borderRadius: 8, background: T.ink, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700 }}>◇</div>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>Tomoshibi</div>
              <div style={{ fontSize: 10, color: T.ink3, marginTop: 1 }}>灯火 · 寮管理システム</div>
            </div>
          </div>
        </div>
        <div style={{ height: 1, background: T.line }} />
        <nav style={{ padding: '10px 10px', flex: 1 }}>
          {NAV.map(([id, label, badge]) => {
            const isActive = id === active;
            return (
              <button key={id} onClick={() => onNav && onNav(id)}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  width: '100%', padding: '9px 12px', marginBottom: 2,
                  background: isActive ? T.cobaltSoft : 'transparent',
                  color: isActive ? T.cobaltDeep : T.ink2,
                  fontFamily: 'inherit', fontSize: 13.5,
                  fontWeight: isActive ? 600 : 500,
                  border: 'none', borderRadius: 8, cursor: 'pointer', textAlign: 'left',
                }}>
                <span>{label}</span>
                {badge != null && <span style={{
                  fontSize: 11, background: isActive ? T.cobalt : T.lineStrong, color: '#fff',
                  padding: '1px 8px', borderRadius: 10, fontWeight: 600, fontVariantNumeric: 'tabular-nums',
                }}>{badge}</span>}
              </button>
            );
          })}
        </nav>
        <div style={{ padding: '14px 20px', borderTop: `1px solid ${T.line}`, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: 16, background: T.cobaltSoft, color: T.cobaltDeep, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13 }}>
            {(user && user.name && user.name.charAt(0)) || '田'}
          </div>
          <div style={{ fontSize: 12, flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user ? user.name : '田中 先生'}</div>
            <div style={{ color: T.ink3, fontSize: 11 }}>{user ? user.dorm : '第一寮'}</div>
          </div>
          <button onClick={onLogout} title="ログアウト / アカウント切替"
            style={{ border: 'none', background: 'transparent', color: T.ink3, cursor: 'pointer', padding: 6, borderRadius: 6, fontSize: 11 }}>切替</button>
        </div>
      </aside>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <header style={{
          height: 56, borderBottom: `1px solid ${T.line}`, background: T.surface,
          display: 'flex', alignItems: 'center', padding: '0 24px', gap: 16,
          position: 'sticky', top: 0, zIndex: 5,
        }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: T.ink }}>
            {active === 'roll-call' && '点呼'}
            {active === 'notifications' && '通知'}
            {active === 'discipline' && '規律・処分'}
            {active === 'applications' && '申請'}
            {active === 'cleaning' && '清掃確認'}
            {active === 'info' && 'お知らせ・バス'}
            {active === 'community' && '寮コミュニティ'}
          </div>
          <div style={{ flex: 1 }} />
          {sessionActive && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8, padding: '5px 12px',
              background: T.okSoft, color: T.ok, borderRadius: 999, fontSize: 12, fontWeight: 600,
              border: `1px solid ${T.okBorder}`,
            }}>
              <span style={{ width: 8, height: 8, borderRadius: 4, background: T.ok, boxShadow: `0 0 0 4px ${T.okSoft}` }} />
              点呼実施中
            </div>
          )}
          <div style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono }}>
            2026-04-21（火） 19:38
          </div>
        </header>
        <div style={{ flex: 1, overflow: 'auto' }}>{children}</div>
      </div>
    </div>
  );
}

window.Shell = Shell;
