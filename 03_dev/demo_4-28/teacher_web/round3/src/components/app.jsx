// App root — router, state, auto-logout timer, demo toast.

function App() {
  const T = window.RYO;
  // route: 'login' | 'select-teacher' | 'app'
  const [route, setRoute] = React.useState('login');
  const [teachers, setTeachers] = React.useState(window.TEACHERS);
  const [teacher, setTeacher] = React.useState(null);
  const [lastTeacherId, setLastTeacherId] = React.useState(null);
  const [page, setPage] = React.useState('roll-call');
  const [pageParams, setPageParams] = React.useState(null);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [toast, setToast] = React.useState(null);

  // Session state
  const [session, setSession] = React.useState(null);     // {name, startedAt}
  const [students, setStudents] = React.useState([]);
  const [liveMode, setLiveMode] = React.useState(false);   // fullscreen live view
  const [lastEnded, setLastEnded] = React.useState(null);
  const [overrideTarget, setOverrideTarget] = React.useState(null);
  const [outstayTarget, setOutstayTarget] = React.useState(null);

  // Trend demo
  const trend = [
    { date: '2026-04-15', late: 1, absent: 0 },
    { date: '2026-04-16', late: 0, absent: 0 },
    { date: '2026-04-17', late: 2, absent: 1 },
    { date: '2026-04-18', late: 1, absent: 0 },
    { date: '2026-04-19', late: 0, absent: 0 },
    { date: '2026-04-20', late: 1, absent: 0 },
    { date: '2026-04-21', late: 0, absent: 1 },
  ];

  // Auto-logout 30min with 25min warning
  const lastActivity = React.useRef(Date.now());
  React.useEffect(() => {
    const bump = () => { lastActivity.current = Date.now(); };
    ['mousemove','keydown','click','touchstart'].forEach(e => window.addEventListener(e, bump));
    return () => ['mousemove','keydown','click','touchstart'].forEach(e => window.removeEventListener(e, bump));
  }, []);
  React.useEffect(() => {
    if (route !== 'app') return;
    let warned = false;
    const id = setInterval(() => {
      const idle = Date.now() - lastActivity.current;
      if (idle > window.TIMEOUT_MS) { setRoute('select-teacher'); setTeacher(null); setLiveMode(false); setToast({ type: 'warn', msg: '操作がないため担当者選択に戻りました' }); }
      else if (!warned && idle > window.TIMEOUT_WARN_MS) { warned = true; setToast({ type: 'warn', msg: 'あと 5 分で担当者選択に戻ります' }); }
    }, 5000);
    return () => clearInterval(id);
  }, [route]);

  React.useEffect(() => { if (toast) { const id = setTimeout(() => setToast(null), 4500); return () => clearTimeout(id); } }, [toast]);

  const loginOk = () => setRoute('select-teacher');
  const pickTeacher = (t) => { setTeacher(t); setLastTeacherId(t.id); setRoute('app'); setPage('roll-call'); setToast({ type: 'ok', msg: `${t.name} 先生でサインインしました · ${window.dormLabel(t.dorm)} 担当` }); };
  const logout = () => { setRoute('login'); setTeacher(null); setLiveMode(false); setSession(null); };

  const startSession = (name) => {
    const seeded = window.seedStudents(teacher.dorm);
    // demo: add a few interesting states
    seeded[0].pending = { reason: '岡山市内で家族と合流、夕食後帰舎予定 · 03-15 承認後再申請', submittedAt: '19:22' };
    seeded[2].health = '発熱 38.1°C、保健室で休養中';
    seeded[8].status = 'exempt'; seeded[8].exemptReason = '部活合宿 04-19〜04-22';
    setStudents(seeded);
    setSession({ name, startedAt: Date.now() });
    setLiveMode(true);
  };
  const endSession = () => {
    const cnt = students.reduce((a, s) => { a[s.status] = (a[s.status] || 0) + 1; return a; }, {});
    const total = students.length;
    const rate = `${(cnt.ok || 0) + (cnt.exempt || 0) + (cnt.late || 0)}/${total}`;
    const d = new Date();
    const t2 = (d) => `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    setLastEnded({ name: session.name, start: t2(new Date(session.startedAt)), end: t2(d), rate });
    setLiveMode(false);
    setSession(null);
    setToast({ type: 'ok', msg: '点呼が保存されました' });
  };
  const openOverride = (s) => setOverrideTarget(s);
  const saveOverride = (patch) => {
    setStudents(list => list.map(s => s.key === overrideTarget.key ? {
      ...s, status: patch.status,
      checkinAt: patch.status === 'ok' ? (s.checkinAt || new Date().toTimeString().slice(0, 8)) : s.checkinAt,
      override: { reason: patch.reason, by: teacher.name + ' 先生' },
      pending: patch.approveLeave ? null : s.pending,
      exemptReason: patch.status === 'exempt' ? (s.exemptReason || patch.reason) : s.exemptReason,
    } : s));
    setOverrideTarget(null);
    setToast({ type: 'ok', msg: '調整が反映されました' });
  };
  const resetLive = () => { setStudents(window.seedStudents(teacher.dorm)); setToast({ type: 'warn', msg: 'セッションをリセットしました' }); };

  const nav = (id, params) => { setPage(id); setPageParams(params || null); if (id !== 'search') setSearchQuery(''); };
  const search = (q) => { setSearchQuery(q); setPage('search'); };

  const onTeacherDelete = (id) => setTeachers(list => list.filter(t => t.id !== id));
  const onTeacherAdd = (data) => setTeachers(list => [...list, { ...data, id: 't' + Date.now(), lastLoginMins: null }]);

  // --- RENDER ---

  if (route === 'login') {
    return <><window.LoginScreen onLogin={loginOk} /><ToastSlot toast={toast} /></>;
  }
  if (route === 'select-teacher') {
    return <><window.SelectTeacherScreen teachers={teachers} lastTeacherId={lastTeacherId}
      onPick={pickTeacher} onDeleteTeacher={onTeacherDelete} onAddTeacher={onTeacherAdd} onLogout={logout} /><ToastSlot toast={toast} /></>;
  }
  // app
  if (liveMode && session) {
    return (
      <>
        <window.LiveRollCall teacher={teacher} sessionName={session.name} startedAt={session.startedAt}
          students={students} setStudents={setStudents} onEnd={endSession}
          onOverride={openOverride} onReset={resetLive} />
        {overrideTarget && <window.OverrideModal student={overrideTarget} onClose={() => setOverrideTarget(null)} onSave={saveOverride} />}
        <ToastSlot toast={toast} />
      </>
    );
  }

  let body;
  switch (page) {
    case 'roll-call':
      body = <window.RollCallLanding teacher={teacher} onStart={startSession} lastEnded={lastEnded} onNav={nav} trend={trend} />; break;
    case 'applications':
      body = <window.ApplicationsPage onOpen={setOutstayTarget} />; break;
    case 'discipline':
      body = <window.DisciplinePage teacher={teacher} onNav={nav} />; break;
    case 'records':
      body = <window.RecordsPage teacher={teacher} params={pageParams} onNav={nav} />; break;
    case 'search':
      body = <window.SearchPage teacher={teacher} query={searchQuery} />; break;
    case 'notifications':
      body = <window.NotificationsPage teacher={teacher} onNav={nav} />; break;
    case 'cleaning':
      body = <window.CleaningPage />; break;
    case 'info':
      body = <window.InfoPage teacher={teacher} />; break;
    case 'community':
      body = <window.CommunityPage teacher={teacher} />; break;
    case 'accounts':
      body = <window.AccountsPage teacher={teacher} />; break;
    default:
      body = <window.RollCallLanding teacher={teacher} onStart={startSession} lastEnded={lastEnded} onNav={nav} trend={trend} />;
  }

  return (
    <>
      <window.Shell teacher={teacher} active={page === 'search' ? 'search' : page} onNav={nav}
        sessionActive={session && !liveMode} onLogout={logout}
        onSwitchTeacher={() => { setRoute('select-teacher'); setTeacher(null); setLiveMode(false); }}
        onSearch={search} onResumeLive={() => session && setLiveMode(true)}>
        {body}
      </window.Shell>
      {outstayTarget && <window.OutstayDetailModal app={outstayTarget} onClose={() => setOutstayTarget(null)}
        onAction={(a) => { setOutstayTarget(null); setToast({ type: 'ok', msg: `申請を${a === 'approved' ? '承認' : a === 'rejected' ? '却下' : '保留'}しました · iOS にプッシュ通知送信済み` }); }} />}
      <ToastSlot toast={toast} />
    </>
  );
}

function ToastSlot({ toast }) {
  const T = window.RYO;
  if (!toast) return null;
  const c = toast.type === 'ok' ? [T.ok, T.okSoft, T.okBorder] : [T.warn, T.warnSoft, T.warnBorder];
  return (
    <div style={{
      position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
      background: c[1], color: c[0], border: `1px solid ${c[2]}`, padding: '10px 18px',
      borderRadius: 999, fontSize: 13, fontWeight: 600, fontFamily: T.font,
      zIndex: 1000, boxShadow: T.shadow2, animation: 'toastIn .3s ease-out',
    }}>{toast.msg}</div>
  );
}

window.App = App;
