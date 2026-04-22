// /login — shared-password login for teaching staff.
// Fields: アカウント ID (固定 'tomoshibi') + shared password.
// 3 failures → 30s lock.

function LoginScreen({ onLogin }) {
  const T = window.RYO;
  const [u, setU] = React.useState('tomoshibi');
  const [p, setP] = React.useState('');
  const [fails, setFails] = React.useState(0);
  const [lockUntil, setLockUntil] = React.useState(0);
  const [err, setErr] = React.useState('');
  const [now, setNow] = React.useState(Date.now());

  React.useEffect(() => { const id = setInterval(() => setNow(Date.now()), 500); return () => clearInterval(id); }, []);
  const locked = now < lockUntil;
  const lockLeft = Math.max(0, Math.ceil((lockUntil - now) / 1000));

  const submit = (e) => {
    e.preventDefault();
    if (locked) return;
    if (u.trim() === 'tomoshibi' && p === window.SHARED_PASSWORD) {
      setFails(0); setErr(''); onLogin();
    } else {
      const n = fails + 1; setFails(n);
      if (n >= 3) { setLockUntil(Date.now() + 30000); setErr('3 回失敗しました。30 秒間ロックされます。'); setFails(0); }
      else { setErr(`パスワードが違います (残り ${3 - n} 回)`); }
      setP('');
    }
  };

  return (
    <div style={{
      minHeight: '100vh', background: T.paper, color: T.ink, fontFamily: T.font,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div style={{ width: 440 }}>
        {/* Brand lockup */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 32, justifyContent: 'center' }}>
          <img src={window.__resources.tomoshibiIcon} alt="Tomoshibi" style={{ width: 56, height: 56, borderRadius: 14, boxShadow: T.shadow1 }} />
          <div>
            <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 1, color: T.ink }}>Tomoshibi</div>
            <div style={{ fontSize: 12, color: T.ink3, letterSpacing: 1.5, marginTop: 2 }}>灯火 · 寮管理システム</div>
          </div>
        </div>

        <form onSubmit={submit} style={{
          background: T.surface, border: `1px solid ${T.line}`, borderRadius: 14,
          padding: '28px 28px 24px', boxShadow: T.shadow2,
        }}>
          <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 4 }}>ログイン</div>
          <div style={{ fontSize: 12, color: T.ink3, marginBottom: 22 }}>教職員共用アカウントでサインインしてください。</div>

          <LField label="アカウント ID" value={u} onChange={setU} autoFocus disabled={locked} />
          <LField label="パスワード (共用)" type="password" value={p} onChange={(v) => { setP(v); setErr(''); }} disabled={locked} />

          {err && !locked && (
            <div style={{ marginTop: 2, marginBottom: 12, padding: '8px 12px', fontSize: 12,
              background: T.dangerSoft, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 8 }}>{err}</div>
          )}
          {locked && (
            <div style={{ marginTop: 2, marginBottom: 12, padding: '10px 12px', fontSize: 12,
              background: T.warnSoft, color: T.warn, border: `1px solid ${T.warnBorder}`, borderRadius: 8,
              fontFamily: T.mono }}>🔒 ロック中 · あと {lockLeft} 秒</div>
          )}

          <button type="submit" disabled={locked} style={{
            width: '100%', marginTop: 6, padding: '12px 16px',
            background: locked ? T.lineStrong : T.cobalt, color: '#fff',
            border: 'none', borderRadius: 10, fontFamily: 'inherit', fontSize: 14, fontWeight: 600,
            cursor: locked ? 'not-allowed' : 'pointer',
          }}>ログイン</button>

          <div style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${T.line}`, fontSize: 11, color: T.ink3, lineHeight: 1.6 }}>
            <div>次の画面で「本日の担当者」を選択します。</div>
            <div style={{ fontFamily: T.mono, marginTop: 4 }}>demo: tomoshibi / {window.SHARED_PASSWORD}</div>
          </div>
        </form>

        <div style={{ fontSize: 11, color: T.ink3, textAlign: 'center', marginTop: 14 }}>
          Tomoshibi {window.APP_VERSION} · 2026 AC 入試プロジェクト成果物
        </div>
      </div>
    </div>
  );
}

function LField({ label, value, onChange, type = 'text', autoFocus, disabled }) {
  const T = window.RYO;
  return (
    <label style={{ display: 'block', marginBottom: 14 }}>
      <div style={{ fontSize: 11, color: T.ink2, marginBottom: 6, fontWeight: 600, letterSpacing: .5 }}>{label}</div>
      <input type={type} value={value} autoFocus={autoFocus} disabled={disabled} onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%', padding: '11px 12px', background: disabled ? T.surfaceAlt : T.surface,
          border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit',
          fontSize: 14, color: T.ink, outline: 'none', boxSizing: 'border-box',
        }} />
    </label>
  );
}

window.LoginScreen = LoginScreen;
