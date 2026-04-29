// Login — centered form. Demo creds: teacher / 1234
// Keeps Ryo's subtle shadow + radius language.

function LoginScreen({ onLogin }) {
  const T = window.RYO;
  const [u, setU] = React.useState('teacher');
  const [p, setP] = React.useState('');
  const [err, setErr] = React.useState('');

  const submit = (e) => {
    e.preventDefault();
    if (u === 'teacher' && p === '1234') onLogin({ name: '田中 先生', dorm: '第一寮' });
    else setErr('ユーザー名またはパスワードが正しくありません。');
  };

  return (
    <div style={{
      minHeight: '100vh', background: T.paper, color: T.ink, fontFamily: T.font,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div style={{ width: 420 }}>
        {/* Brand lockup */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28, justifyContent: 'center' }}>
          <div style={{ width: 42, height: 42, borderRadius: 10, background: T.ink, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, fontWeight: 700 }}>◇</div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: 2 }}>Tomoshibi</div>
            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 1, marginTop: 1 }}>灯火 · 寮管理システム</div>
          </div>
        </div>

        <form onSubmit={submit} style={{
          background: T.surface, border: `1px solid ${T.line}`, borderRadius: 14,
          padding: '28px 28px 24px', boxShadow: T.shadow2,
        }}>
          <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 4 }}>ログイン</div>
          <div style={{ fontSize: 12, color: T.ink3, marginBottom: 22 }}>教職員アカウントでサインインしてください。</div>

          <Field label="ユーザー名" value={u} onChange={setU} autoFocus />
          <Field label="パスワード" type="password" value={p} onChange={(v) => { setP(v); setErr(''); }} />

          {err && (
            <div style={{
              marginTop: 4, marginBottom: 12, padding: '8px 12px', fontSize: 12,
              background: T.dangerSoft, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 8,
            }}>{err}</div>
          )}

          <button type="submit" style={{
            width: '100%', marginTop: 6, padding: '11px 16px', background: T.cobalt, color: '#fff',
            border: 'none', borderRadius: 10, fontFamily: 'inherit', fontSize: 14, fontWeight: 600, cursor: 'pointer',
          }}>サインイン</button>

          <div style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${T.line}`, display: 'flex', justifyContent: 'space-between', fontSize: 11, color: T.ink3 }}>
            <span>担当舎監ごとに個別アカウント</span>
            <span style={{ fontFamily: T.mono }}>v0.4 · demo</span>
          </div>
        </form>

        <div style={{ fontSize: 11, color: T.ink3, textAlign: 'center', marginTop: 14, fontFamily: T.mono }}>
          demo: teacher / 1234
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', autoFocus }) {
  const T = window.RYO;
  return (
    <label style={{ display: 'block', marginBottom: 12 }}>
      <div style={{ fontSize: 11, color: T.ink2, marginBottom: 6, fontWeight: 600 }}>{label}</div>
      <input type={type} value={value} autoFocus={autoFocus} onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%', padding: '10px 12px', background: T.surface, border: `1px solid ${T.lineStrong}`,
          borderRadius: 8, fontFamily: 'inherit', fontSize: 14, color: T.ink, outline: 'none', boxSizing: 'border-box',
        }} />
    </label>
  );
}

window.LoginScreen = LoginScreen;
