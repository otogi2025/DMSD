// /records, /search, /notifications, /cleaning, /info, /community pages.

function RecordsPage({ teacher, params, onNav }) {
  const T = window.RYO;
  const date = params && params.date || '2026-04-21';
  const roster = teacher.dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  const statuses = ['ok','ok','ok','late','ok','absent','ok','ok','exempt','ok','ok','ok'];
  const methods  = ['NFC卡','NFC卡','スマホ','手動','NFC卡','—','NFC卡','NFC卡','—','NFC卡','NFC卡','スマホ'];
  const times    = ['19:30','19:31','19:31','19:34','19:32','—','19:33','19:31','—','19:32','19:30','19:31'];
  const rows = roster.map(([room, id, name], i) => {
    const k = i % statuses.length;
    return { room, id, name, session: '晩点呼 · 普通寮生', time: times[k], status: statuses[k], method: methods[k], overrider: k === 3 ? `${teacher.name} 先生` : '—' };
  });

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>記録</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: '4px 0 18px', letterSpacing: -0.3 }}>点呼記録</h1>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 16 }}>
        <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600 }}>日付</label>
        <input type="date" defaultValue={date} style={{ padding: '7px 10px', border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: T.mono, fontSize: 13 }} />
        <label style={{ fontSize: 11, color: T.ink2, fontWeight: 600, marginLeft: 10 }}>セッション</label>
        <select style={{ padding: '7px 10px', border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13 }}>
          <option>晩点呼 · 普通寮生</option><option>朝点呼 · 普通寮生</option>
        </select>
        <div style={{ flex: 1 }} />
        <button onClick={() => alert('Demo 版未対応')} style={{ padding: '6px 12px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 12, cursor: 'pointer' }}>CSV 出力</button>
        <button onClick={() => window.print()} style={{ padding: '6px 12px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 12, cursor: 'pointer' }}>印刷 · PDF 保存</button>
      </div>

      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 190px 110px 100px 100px 140px', background: T.surfaceAlt, fontSize: 11, color: T.ink2, fontWeight: 600, letterSpacing: 1, borderBottom: `1px solid ${T.line}` }}>
          {['学生','部屋','セッション','チェックイン','状態','方式','手動調整者'].map(h => <div key={h} style={{ padding: '10px 12px' }}>{h}</div>)}
        </div>
        {rows.map((r, i) => (
          <div key={r.id} style={{ display: 'grid', gridTemplateColumns: '1fr 90px 190px 110px 100px 100px 140px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 12.5, alignItems: 'center' }}>
            <div style={{ padding: '9px 12px', fontWeight: 600 }}>{r.name}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.ink3 }}>{r.room}</div>
            <div style={{ padding: '9px 12px' }}>{r.session}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.ink2 }}>{r.time}</div>
            <div style={{ padding: '9px 12px' }}><window.RecStatusBadge s={r.status} /></div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>{r.method}</div>
            <div style={{ padding: '9px 12px', fontSize: 11, color: r.overrider === '—' ? T.ink3 : T.cobaltDeep }}>{r.overrider}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

window.RecStatusBadge = function({ s }) {
  const T = window.RYO;
  const map = { ok: [T.ok, T.okSoft, '時間内'], late: [T.late, T.lateSoft, '遅刻'], absent: [T.danger, T.dangerSoft, '欠席'], exempt: [T.info, T.infoSoft, '免除'] }[s] || [T.ink3, T.surfaceAlt, '—'];
  return <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: map[1], color: map[0] }}>{map[2]}</span>;
};

function SearchPage({ teacher, query }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('student');
  const [q, setQ] = React.useState(query || '');
  const normalize = (s) => (s || '').replace(/\s+/g, '').toLowerCase();
  const qn = normalize(q);
  // 担当寮優先で検索、見つからなければ全体からも探す
  const ownRoster = teacher.dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  const ownMatch = qn ? ownRoster.find(([room, id, name]) => normalize(`${name}${room}${id}`).includes(qn)) : null;
  const allMatch = !ownMatch && qn ? (window.ROSTER_ALL || []).find(([room, id, name]) => normalize(`${name}${room}${id}`).includes(qn)) : null;
  const match = ownMatch || allMatch;
  const matchDorm = ownMatch ? teacher.dorm : (allMatch ? allMatch[3] : teacher.dorm);
  const crossDorm = allMatch && !ownMatch;

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>検索 {q && `> ${q}`}</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: '4px 0 18px', letterSpacing: -0.3 }}>検索結果</h1>

      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${T.line}`, marginBottom: 20 }}>
        {[['student', '学生から'], ['date', '日付から']].map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)} style={{ padding: '10px 18px', background: 'transparent', border: 'none', borderBottom: tab === k ? `2px solid ${T.cobalt}` : '2px solid transparent', color: tab === k ? T.cobaltDeep : T.ink3, fontWeight: tab === k ? 700 : 500, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1 }}>{l}</button>
        ))}
      </div>

      {tab === 'student' ? (
        <>
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="氏名・部屋・学籍番号で検索（スペース無視）"
            style={{ width: '100%', padding: '11px 14px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 10, fontFamily: 'inherit', fontSize: 14, outline: 'none', boxSizing: 'border-box', marginBottom: 20 }} />
          {crossDorm && (
            <div style={{ padding: '10px 14px', background: T.warnSoft, border: `1px solid ${T.warnBorder}`, borderRadius: 8, fontSize: 12, color: T.warn, marginBottom: 14 }}>
              担当外の寮の学生が見つかりました · {window.dormLabel(matchDorm)}（閲覧のみ）
            </div>
          )}
          {match ? <StudentDossier room={match[0]} id={match[1]} name={match[2]} dorm={matchDorm} /> : <EmptyState msg={q ? `「${q}」に一致する学生はいません` : '学生名・部屋番号・学籍番号を入力してください'} />}
        </>
      ) : (
        <DateSearchBody />
      )}
    </div>
  );
}

function StudentDossier({ room, id, name, dorm }) {
  const T = window.RYO;
  const [open, setOpen] = React.useState({ rollcall: true, demerit: true, health: false, leave: false, apps: false, other: false });
  const Block = ({ k, title, badge, children }) => (
    <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, marginBottom: 10, boxShadow: T.shadow1 }}>
      <button onClick={() => setOpen(o => ({ ...o, [k]: !o[k] }))} style={{ display: 'flex', width: '100%', alignItems: 'center', padding: '14px 18px', background: 'transparent', border: 'none', fontFamily: 'inherit', cursor: 'pointer' }}>
        <span style={{ fontSize: 15, fontWeight: 700, color: T.ink }}>{title}</span>
        {badge && <span style={{ marginLeft: 8, fontSize: 11, color: T.ink3 }}>{badge}</span>}
        <div style={{ flex: 1 }} />
        <span style={{ color: T.ink3, fontSize: 13 }}>{open[k] ? '▾' : '▸'}</span>
      </button>
      {open[k] && <div style={{ padding: '0 18px 16px', fontSize: 13, color: T.ink2, lineHeight: 1.7 }}>{children}</div>}
    </div>
  );

  return (
    <div>
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 22px', boxShadow: T.shadow1, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 18 }}>
        <div style={{ width: 56, height: 56, borderRadius: 28, background: T.cobaltSoft, color: T.cobaltDeep, fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{name.charAt(0)}</div>
        <div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{name}</div>
          <div style={{ fontSize: 12, color: T.ink3, fontFamily: T.mono, marginTop: 2 }}>{room} · {id} · {window.dormLabel(dorm)}</div>
        </div>
      </div>

      <Block k="rollcall" title="点呼履歴" badge="月別サマリー">
        4 月: 時間内 18 / 遅刻 2 / 欠席 0 · 3 月: 時間内 31 / 遅刻 0 / 欠席 0
      </Block>
      <Block k="demerit" title="減点明細" badge="累計 1.0 点">
        04-17 遅刻 0.5 点 · 04-09 遅刻 0.5 点
      </Block>
      <Block k="health" title="体調報告履歴">提出記録なし</Block>
      <Block k="leave" title="欠席届履歴">提出記録なし</Block>
      <Block k="apps" title="申請履歴">04-21 外泊申請 (審査待ち) · 03-15 外泊申請 (承認済)</Block>
      <Block k="other" title="清掃・活動・宅配 等">清掃 4 月実施 6 回 · 宅配受取 2 件</Block>
    </div>
  );
}

function DateSearchBody() {
  const T = window.RYO;
  return (
    <div>
      <input type="date" defaultValue="2026-04-21" style={{ padding: '11px 14px', border: `1px solid ${T.lineStrong}`, borderRadius: 10, fontFamily: T.mono, fontSize: 14, marginBottom: 18 }} />
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 22px', boxShadow: T.shadow1 }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>2026-04-21 全寮集計</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
          {[['点呼', '23/24'], ['欠席', '1'], ['体調異常', '1'], ['申請処理', '3']].map(([l, v], i) => (
            <div key={i}>
              <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 1.2, fontWeight: 600 }}>{l}</div>
              <div style={{ fontSize: 26, fontWeight: 700, fontFamily: T.mono, marginTop: 4 }}>{v}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ msg }) {
  const T = window.RYO;
  return <div style={{ padding: 60, textAlign: 'center', color: T.ink3, fontSize: 13, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 12 }}>{msg}</div>;
}

function NotificationsPage({ teacher, onNav }) {
  const T = window.RYO;
  const roster = teacher && teacher.dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  const pick = (i) => (roster[i % roster.length] || roster[0])[2];
  const sample1 = pick(0);
  const sample2 = pick(3);
  const sample3 = pick(1);
  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>通知</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: '4px 0 18px', letterSpacing: -0.3 }}>通知中心</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        <NotifCard n="3" label="審査待ち申請" color={T.cobalt} onClick={() => onNav('applications')} />
        <NotifCard n="2" label="清掃審査" color={T.warn} onClick={() => onNav('cleaning')} />
        <NotifCard n="1" label="通報" color={T.danger} onClick={() => onNav('community')} />
        <NotifCard n="4" label="警告リスト" color={T.warn} onClick={() => onNav('discipline')} />
      </div>
      <div style={{ fontSize: 12, color: T.ink3, letterSpacing: 1.5, fontWeight: 700, marginBottom: 10 }}>最近の通知</div>
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1 }}>
        {[
          ['19:22', `${sample1} さんが外泊申請を提出しました`, T.cobalt],
          ['19:20', '清掃写真 2 件 審査待ち', T.warn],
          ['18:45', `${sample2} さんの遅刻が今月 5 回に達しました`, T.warn],
          ['14:10', `${sample3} さんの外泊申請が担任により承認されました`, T.ok],
          ['08:30', '朝点呼 完了 (12/12 時間内)', T.ok],
        ].map(([t, msg, c], i) => (
          <div key={i} style={{ display: 'flex', gap: 12, padding: '12px 16px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 13 }}>
            <span style={{ width: 8, height: 8, background: c, borderRadius: 4, marginTop: 6, flexShrink: 0 }} />
            <span style={{ flex: 1 }}>{msg}</span>
            <span style={{ fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>{t}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function NotifCard({ n, label, color, onClick }) {
  const T = window.RYO;
  return (
    <button onClick={onClick} style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 20px', boxShadow: T.shadow1, textAlign: 'left', fontFamily: 'inherit', cursor: 'pointer' }}>
      <div style={{ fontSize: 32, fontWeight: 700, fontFamily: T.mono, color }}>{n}</div>
      <div style={{ fontSize: 12, color: T.ink2, marginTop: 2 }}>{label}</div>
      <div style={{ fontSize: 11, color: T.cobalt, fontWeight: 600, marginTop: 8 }}>開く →</div>
    </button>
  );
}

// Skeleton pages
function CleaningPage() {
  const T = window.RYO;
  return (
    <div style={{ padding: '28px 32px' }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>清掃確認 <span style={{ fontSize: 11, fontWeight: 700, color: T.warn, background: T.warnSoft, padding: '2px 8px', borderRadius: 4, letterSpacing: 1, marginLeft: 8, verticalAlign: 3 }}>開発中</span></h1>
      <div style={{ color: T.ink3, fontSize: 13, marginTop: 4, marginBottom: 20 }}>学生清掃写真の審査</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {[['リシンさん', 'W113', '04-21'], ['ソンキゼン', 'W114', '04-20'], ['ゴキンウ', 'W115', '04-20']].map(([n, r, d], i) => (
          <div key={i} style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: 12, boxShadow: T.shadow1 }}>
            <div style={{ height: 140, background: T.surfaceAlt, border: `1px dashed ${T.lineStrong}`, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: T.ink3, fontSize: 12 }}>写真プレビュー</div>
            <div style={{ marginTop: 10, fontSize: 14, fontWeight: 600 }}>{n}</div>
            <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>{r} · {d}</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
              <button style={{ flex: 1, padding: '7px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>承認</button>
              <button style={{ flex: 1, padding: '7px', background: 'transparent', color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>却下</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function InfoPage({ teacher }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('notice');
  const [posts, setPosts] = React.useState(window.NOTICE_POSTS);
  const [composing, setComposing] = React.useState(false);

  const handlePost = (title, body) => {
    const now = new Date();
    const date = `${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
    setPosts([{ date, title, body, author: teacher && teacher.name || '新股 先生', pinned: false }, ...posts]);
    setComposing(false);
  };

  return (
    <div style={{ padding: '28px 32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>お知らせ・バス</h1>
        {tab === 'notice' && (
          <button onClick={() => setComposing(true)} style={{ padding: '8px 16px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer', boxShadow: T.shadow1 }}>＋ 新規お知らせ投稿</button>
        )}
      </div>
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${T.line}`, margin: '18px 0' }}>
        {[['notice', 'お知らせ'], ['event', '行事カレンダー'], ['bus', 'バス時刻表']].map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)} style={{ padding: '10px 18px', background: 'transparent', border: 'none', borderBottom: tab === k ? `2px solid ${T.cobalt}` : '2px solid transparent', color: tab === k ? T.cobaltDeep : T.ink3, fontWeight: tab === k ? 700 : 500, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1 }}>{l}</button>
        ))}
      </div>
      {tab === 'notice' && (
        <div>
          {posts.map((p, i) => (
            <div key={i} style={{ padding: '14px 16px', background: T.surface, border: `1px solid ${p.pinned ? T.cobalt : T.line}`, borderRadius: 10, marginBottom: 10, fontSize: 13 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                {p.pinned && <span style={{ fontSize: 10, color: '#fff', background: T.cobalt, padding: '2px 6px', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>PIN</span>}
                <span style={{ fontFamily: T.mono, color: T.ink3, fontSize: 11 }}>{p.date}</span>
                <span style={{ color: T.ink3, fontSize: 11 }}>· {p.author}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{p.title}</div>
              {p.body && <div style={{ color: T.ink2, fontSize: 12, lineHeight: 1.6 }}>{p.body}</div>}
            </div>
          ))}
        </div>
      )}
      {tab === 'event' && <EventCalendar events={window.CALENDAR_EVENTS || []} teacher={teacher} />}
      {tab === 'bus' && <BusSchedulePanel teacher={teacher} />}
      {composing && <ComposeNoticeModal onClose={() => setComposing(false)} onSubmit={handlePost} />}
    </div>
  );
}

// バス時刻表 管理 — 2026-04-24 新規。実運用サンプル = 06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md
// 行事カレンダー（iOS と同型レイアウト：月グリッド + 選択日イベントリスト）
function EventCalendar({ events, teacher }) {
  const T = window.RYO;
  const today = new Date();
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  const todayKey = fmt(today);
  const [cursor, setCursor] = React.useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selected, setSelected] = React.useState(todayKey);
  const [composing, setComposing] = React.useState(false);
  const [list, setList] = React.useState(events);

  const y = cursor.getFullYear();
  const m = cursor.getMonth();
  const firstDow = new Date(y, m, 1).getDay();
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < firstDow; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  const eventsByDate = list.reduce((acc, e) => { (acc[e.date] = acc[e.date] || []).push(e); return acc; }, {});
  const dayKey = (d) => `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
  const selEvents = (eventsByDate[selected] || []).slice().sort((a, b) => (a.time || '99:99').localeCompare(b.time || '99:99'));
  const selDate = new Date(selected + 'T00:00:00');
  const selJa = `${selDate.getMonth()+1} 月 ${selDate.getDate()} 日（${['日','月','火','水','木','金','土'][selDate.getDay()]}）`;
  const monthJa = `${y} 年 ${m+1} 月`;

  const dowLabels = ['日','月','火','水','木','金','土'];
  const navMonth = (delta) => setCursor(new Date(y, m + delta, 1));

  const addEvent = (e) => { setList([...list, e].sort((a,b) => a.date.localeCompare(b.date))); setComposing(false); setSelected(e.date); };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(420px, 1.3fr) 1fr', gap: 20, alignItems: 'start' }}>
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 20px', boxShadow: T.shadow1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <button onClick={() => navMonth(-1)} title="前月" style={{ width: 32, height: 32, border: `1px solid ${T.line}`, background: T.surface, borderRadius: 8, cursor: 'pointer', fontSize: 14, color: T.ink2, fontFamily: 'inherit' }}>‹</button>
          <div style={{ fontSize: 16, fontWeight: 700, color: T.ink, fontFamily: T.font }}>{monthJa}</div>
          <button onClick={() => navMonth(1)} title="次月" style={{ width: 32, height: 32, border: `1px solid ${T.line}`, background: T.surface, borderRadius: 8, cursor: 'pointer', fontSize: 14, color: T.ink2, fontFamily: 'inherit' }}>›</button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 6 }}>
          {dowLabels.map((d, i) => (
            <div key={d} style={{ textAlign: 'center', fontSize: 11, fontWeight: 600, color: i === 0 ? T.danger : i === 6 ? T.cobalt : T.ink3, padding: '6px 0' }}>{d}</div>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
          {cells.map((d, i) => {
            if (d == null) return <div key={i} style={{ aspectRatio: '1 / 1' }} />;
            const k = dayKey(d);
            const has = (eventsByDate[k] || []).length > 0;
            const isSel = k === selected;
            const isToday = k === todayKey;
            const dow = (firstDow + d - 1) % 7;
            const baseColor = dow === 0 ? T.danger : dow === 6 ? T.cobalt : T.ink;
            return (
              <button key={i} onClick={() => setSelected(k)} style={{
                aspectRatio: '1 / 1', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                gap: 3, padding: 0, fontFamily: 'inherit',
                background: isSel ? T.cobalt : (isToday ? T.cobaltSoft : 'transparent'),
                color: isSel ? '#fff' : baseColor,
                border: isSel ? `1px solid ${T.cobalt}` : `1px solid transparent`,
                borderRadius: 8, cursor: 'pointer', fontSize: 14, fontWeight: isSel || isToday ? 700 : 500,
                position: 'relative',
              }}>
                <span>{d}</span>
                {has && <span style={{ width: 5, height: 5, borderRadius: 3, background: isSel ? '#fff' : T.cobalt }} />}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 12 }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: T.ink }}>{selJa}</div>
          <div style={{ flex: 1 }} />
          <span style={{ fontSize: 11, color: T.ink3, background: T.surfaceAlt, border: `1px solid ${T.line}`, padding: '3px 9px', borderRadius: 999, fontFamily: T.mono }}>{selEvents.length} 件</span>
          <button onClick={() => setComposing(true)} style={{ padding: '5px 12px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}>＋ 追加</button>
        </div>
        {selEvents.length === 0 ? (
          <div style={{ padding: 36, textAlign: 'center', color: T.ink3, fontSize: 13, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 12 }}>この日に予定はありません</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {selEvents.map((e, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '70px 1fr', gap: 12, padding: '12px 14px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, boxShadow: T.shadow1 }}>
                <div style={{ fontFamily: T.mono, color: T.cobaltDeep, fontWeight: 700, fontSize: 14 }}>{e.time || '終日'}</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: T.ink }}>{e.title}</div>
                  {e.location && <div style={{ fontSize: 12, color: T.ink3, marginTop: 2 }}>📍 {e.location}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {composing && <EventComposeModal initialDate={selected} onClose={() => setComposing(false)} onSubmit={addEvent} />}
    </div>
  );
}

function EventComposeModal({ initialDate, onClose, onSubmit }) {
  const T = window.RYO;
  const [date, setDate] = React.useState(initialDate);
  const [time, setTime] = React.useState('');
  const [title, setTitle] = React.useState('');
  const [location, setLocation] = React.useState('');
  const Shell = window.ModalShell;
  const Field = window.ModalField;
  const Footer = window.ModalFooter;
  const inputStyle = window.modalInputStyle(T);

  const submit = () => {
    if (!title.trim() || !date) return;
    onSubmit({ date, time: time || null, title: title.trim(), location: location.trim() || '—' });
  };
  const valid = title.trim() && date;

  return (
    <Shell T={T} title="行事を追加" onClose={onClose}>
      <Field T={T} label="日付 *">
        <input type="date" value={date} onChange={e => setDate(e.target.value)} style={inputStyle} />
      </Field>
      <Field T={T} label="時刻（任意 · 空欄なら終日）">
        <input type="time" value={time} onChange={e => setTime(e.target.value)} style={inputStyle} />
      </Field>
      <Field T={T} label="タイトル *">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="例：避難訓練" style={inputStyle} />
      </Field>
      <Field T={T} label="場所">
        <input value={location} onChange={e => setLocation(e.target.value)} placeholder="例：グラウンド" style={inputStyle} />
      </Field>
      <Footer T={T} onClose={onClose} onSubmit={submit} disabled={!valid} />
    </Shell>
  );
}

function BusSchedulePanel({ teacher }) {
  const T = window.RYO;
  const [posts, setPosts] = React.useState(window.BUS_POSTS);
  const [openPost, setOpenPost] = React.useState(() => (window.BUS_POSTS[0] || {}).id || null);
  const [editing, setEditing] = React.useState(null); // null | 'new' | postId | { postId, eventIdx } | { postId, eventIdx, itemIdx }

  const togglePost = (id) => setOpenPost(openPost === id ? null : id);
  const deletePost = (id) => { if (confirm('この告知を削除しますか？')) setPosts(posts.filter(p => p.id !== id)); };
  const togglePin = (id) => setPosts(posts.map(p => p.id === id ? { ...p, pinned: !p.pinned } : p));
  const savePost = (data) => {
    if (editing === 'new') {
      setPosts([{ ...data, id: 'BP' + Date.now(), events: [], pinned: false }, ...posts]);
    } else {
      setPosts(posts.map(p => p.id === editing ? { ...p, ...data } : p));
    }
    setEditing(null);
  };

  const sorted = [...posts].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, gap: 10 }}>
        <div style={{ fontSize: 12, color: T.ink3 }}>特別運行便・定期便の告知管理。各告知 → 日付ごとの行事 → 時刻行の 3 階層。</div>
        <button onClick={() => setEditing('new')} style={{ padding: '7px 14px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 12, fontWeight: 700, cursor: 'pointer', boxShadow: T.shadow1, whiteSpace: 'nowrap' }}>＋ 新規告知</button>
      </div>

      {sorted.map(post => (
        <BusPostCard key={post.id} post={post} T={T} open={openPost === post.id} onToggle={() => togglePost(post.id)}
          onEditPost={() => setEditing(post.id)} onDeletePost={() => deletePost(post.id)} onPin={() => togglePin(post.id)} />
      ))}

      {sorted.length === 0 && <div style={{ padding: 36, textAlign: 'center', color: T.ink3, fontSize: 13, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 10 }}>告知はまだありません。「＋ 新規告知」から追加してください。</div>}

      {editing && <BusPostComposeModal T={T} initial={editing === 'new' ? null : posts.find(p => p.id === editing)} onClose={() => setEditing(null)} onSubmit={savePost} />}
    </div>
  );
}

function BusPostCard({ post, T, open, onToggle, onEditPost, onDeletePost, onPin }) {
  return (
    <div style={{ background: T.surface, border: `1px solid ${post.pinned ? T.cobalt : T.line}`, borderRadius: 10, marginBottom: 10, overflow: 'hidden', boxShadow: post.pinned ? T.shadow1 : 'none' }}>
      <div onClick={onToggle} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', cursor: 'pointer' }}>
        <span style={{ fontSize: 14, color: T.ink3, fontFamily: T.mono, width: 14, textAlign: 'center' }}>{open ? '▼' : '▶'}</span>
        {post.pinned && <span style={{ fontSize: 10, color: '#fff', background: T.cobalt, padding: '2px 6px', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>PIN</span>}
        <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: post.category === '特別運行便' ? T.cobaltSoft : T.surfaceAlt, color: post.category === '特別運行便' ? T.cobaltDeep : T.ink2, border: `1px solid ${post.category === '特別運行便' ? T.cobalt : T.line}`, whiteSpace: 'nowrap' }}>{post.category}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: T.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{post.title}</div>
          <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, marginTop: 2 }}>
            {post.posted_on} · {post.posted_by} · {post.effective_from}{post.effective_until ? ` 〜 ${post.effective_until}` : ' 〜 継続中'} · {post.events.length} 件
          </div>
        </div>
        <button onClick={(e) => { e.stopPropagation(); onPin(); }} style={{ padding: '4px 10px', background: post.pinned ? T.cobaltSoft : T.surface, color: post.pinned ? T.cobaltDeep : T.ink3, border: `1px solid ${post.pinned ? T.cobalt : T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{post.pinned ? 'ピン解除' : 'ピン留め'}</button>
        <button onClick={(e) => { e.stopPropagation(); onEditPost(); }} style={{ padding: '4px 10px', background: T.surface, color: T.ink2, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>編集</button>
        <button onClick={(e) => { e.stopPropagation(); onDeletePost(); }} style={{ padding: '4px 10px', background: T.surface, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>削除</button>
      </div>
      {open && (
        <div style={{ padding: '4px 14px 14px', borderTop: `1px solid ${T.line}`, background: T.surfaceAlt }}>
          {post.body && <div style={{ padding: '10px 12px', margin: '10px 0', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 8, fontSize: 12, lineHeight: 1.7, color: T.ink2, whiteSpace: 'pre-wrap' }}>{post.body}</div>}
          {post.events.length === 0 && <div style={{ padding: 20, textAlign: 'center', color: T.ink3, fontSize: 12 }}>行事がまだ登録されていません</div>}
          {post.events.map((ev, i) => <BusEventBlock key={i} ev={ev} T={T} />)}
        </div>
      )}
    </div>
  );
}

function BusEventBlock({ ev, T }) {
  return (
    <div style={{ margin: '10px 0', padding: 12, background: T.surface, border: `1px solid ${T.line}`, borderRadius: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, paddingBottom: 8, borderBottom: `1px solid ${T.line}` }}>
        <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', background: T.cobaltSoft, color: T.cobaltDeep, borderRadius: 4, fontFamily: T.mono, letterSpacing: .5 }}>{ev.date}</span>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.ink, flex: 1 }}>{ev.name}</div>
        {ev.audience && <div style={{ fontSize: 10, color: T.ink3, maxWidth: 280, textAlign: 'right', lineHeight: 1.4 }}>対象: {ev.audience}</div>}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {ev.items.map((it, j) => (
          <div key={j} style={{ display: 'flex', alignItems: 'baseline', gap: 12, fontSize: 12, padding: '5px 0', borderBottom: j < ev.items.length - 1 ? `1px dashed ${T.line}` : 'none' }}>
            <span style={{ fontFamily: T.mono, color: T.cobalt, fontWeight: 700, minWidth: 48 }}>{it.time}</span>
            <span style={{ color: T.ink, flex: 1, fontWeight: 500 }}>{it.action}</span>
            {it.location && <span style={{ fontSize: 11, color: T.ink3, minWidth: 68, textAlign: 'right' }}>{it.location}</span>}
            {it.memo && <span style={{ fontSize: 11, color: T.ink3, flex: 2, textAlign: 'left', fontStyle: 'italic' }}>{it.memo}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function BusPostComposeModal({ T, initial, onClose, onSubmit }) {
  const MS = window.ModalShell;
  const MField = window.ModalField;
  const MFooter = window.ModalFooter;
  const inputS = window.modalInputStyle;
  const [title, setTitle] = React.useState(initial ? initial.title : '');
  const [category, setCategory] = React.useState(initial ? initial.category : '特別運行便');
  const [postedOn, setPostedOn] = React.useState(initial ? initial.posted_on : new Date().toISOString().slice(0, 10));
  const [postedBy, setPostedBy] = React.useState(initial ? initial.posted_by : '国際交流部');
  const [effectiveFrom, setEffectiveFrom] = React.useState(initial ? initial.effective_from : '');
  const [effectiveUntil, setEffectiveUntil] = React.useState(initial ? (initial.effective_until || '') : '');
  const [body, setBody] = React.useState(initial ? initial.body : '');
  return (
    <MS T={T} title={initial ? '告知を編集' : '新規告知を作成'} onClose={onClose}>
      <MField T={T} label="タイトル"><input value={title} onChange={e => setTitle(e.target.value)} placeholder="例：特別運行便に関するお知らせ" style={inputS(T)} /></MField>
      <MField T={T} label="カテゴリー">
        <select value={category} onChange={e => setCategory(e.target.value)} style={inputS(T)}>
          {['特別運行便', '定期便', 'イベント', '臨時'].map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </MField>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <MField T={T} label="掲載日"><input type="date" value={postedOn} onChange={e => setPostedOn(e.target.value)} style={inputS(T)} /></MField>
        <MField T={T} label="発信元"><input value={postedBy} onChange={e => setPostedBy(e.target.value)} style={inputS(T)} /></MField>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <MField T={T} label="有効 開始日"><input type="date" value={effectiveFrom} onChange={e => setEffectiveFrom(e.target.value)} style={inputS(T)} /></MField>
        <MField T={T} label="有効 終了日 (空欄 = 継続中)"><input type="date" value={effectiveUntil} onChange={e => setEffectiveUntil(e.target.value)} style={inputS(T)} /></MField>
      </div>
      <MField T={T} label="本文（前文 / 注意事項）"><textarea value={body} onChange={e => setBody(e.target.value)} rows={5} placeholder="学校休業日等に..." style={{ ...inputS(T), resize: 'vertical', lineHeight: 1.6 }} /></MField>
      <div style={{ fontSize: 11, color: T.ink3, padding: '6px 0' }}>※ 行事（日付ごとの時刻表）は告知作成後、詳細画面から追加できます（demo 段階では行事追加 UI は簡略化）。</div>
      <MFooter T={T} onClose={onClose} onSubmit={() => title.trim() && onSubmit({ title: title.trim(), category, posted_on: postedOn, posted_by: postedBy.trim(), effective_from: effectiveFrom, effective_until: effectiveUntil || null, body: body.trim() })} disabled={!title.trim()} />
    </MS>
  );
}

function ComposeNoticeModal({ onClose, onSubmit }) {
  const T = window.RYO;
  const [title, setTitle] = React.useState('');
  const [body, setBody] = React.useState('');
  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(20,23,31,0.55)', zIndex: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: T.surface, borderRadius: 14, width: 540, maxWidth: '100%', boxShadow: T.shadowModal, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: `1px solid ${T.line}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: 15, fontWeight: 700 }}>新規お知らせ投稿</div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', fontSize: 20, color: T.ink3, cursor: 'pointer' }}>×</button>
        </div>
        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <div style={{ fontSize: 11, color: T.ink3, fontWeight: 600, letterSpacing: 1, marginBottom: 6 }}>タイトル</div>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="例：今週金曜の清掃検査について" style={{ width: '100%', padding: '10px 12px', border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontSize: 14, fontFamily: 'inherit', boxSizing: 'border-box' }} />
          </div>
          <div>
            <div style={{ fontSize: 11, color: T.ink3, fontWeight: 600, letterSpacing: 1, marginBottom: 6 }}>本文</div>
            <textarea value={body} onChange={e => setBody(e.target.value)} placeholder="詳細をここに記入..." rows={6} style={{ width: '100%', padding: '10px 12px', border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontSize: 13, fontFamily: 'inherit', boxSizing: 'border-box', resize: 'vertical', lineHeight: 1.6 }} />
          </div>
          <div style={{ fontSize: 11, color: T.ink3 }}>投稿後、学生の iOS App に push 通知が送信されます。</div>
        </div>
        <div style={{ padding: '12px 20px', background: T.surfaceAlt, borderTop: `1px solid ${T.line}`, display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button onClick={onClose} style={{ padding: '8px 16px', background: T.surface, color: T.ink2, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>キャンセル</button>
          <button onClick={() => title.trim() && onSubmit(title.trim(), body.trim())} disabled={!title.trim()} style={{ padding: '8px 16px', background: title.trim() ? T.cobalt : T.line, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: title.trim() ? 'pointer' : 'not-allowed' }}>投稿</button>
        </div>
      </div>
    </div>
  );
}

function CommunityPage({ teacher }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('board');
  const [posts, setPosts] = React.useState(window.COMMUNITY_POSTS);
  const [filter, setFilter] = React.useState('all');
  const [slotFilter, setSlotFilter] = React.useState('all'); // song tab 専用: all / morning / evening

  const [songFilter, setSongFilter] = React.useState('pending'); // song tab 専用: pending / approved / rejected / all
  const [dormFilter, setDormFilter] = React.useState(teacher && teacher.dorm ? teacher.dorm : 'men'); // song tab 専用: men / women / all（既定は担当寮）
  const dormOf = (p) => (p && p.room && p.room.charAt(0) === 'M') ? 'men' : 'women';

  const handleDelete = (id) => { if (confirm('この投稿を削除しますか？学生のアプリからも非表示になります。')) setPosts(posts.map(p => p.id === id ? { ...p, deleted: true } : p)); };
  const handlePin = (id) => setPosts(posts.map(p => p.id === id ? { ...p, pinned: !p.pinned } : p));
  const handleResolve = (id) => setPosts(posts.map(p => p.id === id ? { ...p, flagCount: 0, resolved: true } : p));
  const handleSongDecision = (id, decision) => setPosts(posts.map(p => p.id === id ? {
    ...p,
    songStatus: decision,
    decidedAt: new Date().toTimeString().slice(0, 5),
    decidedBy: teacher ? `${teacher.name} 先生` : '担当 先生',
  } : p));

  const catPosts = posts.filter(p => p.cat === tab && !p.deleted);
  let visible = catPosts;
  if (filter === 'flagged') visible = catPosts.filter(p => p.flagCount > 0 && !p.resolved);
  if (filter === 'pinned') visible = catPosts.filter(p => p.pinned);
  if (tab === 'song' && slotFilter !== 'all') visible = visible.filter(p => p.timeSlot === slotFilter);
  if (tab === 'song' && songFilter !== 'all') {
    visible = visible.filter(p => (p.songStatus || 'pending') === songFilter);
  }
  if (tab === 'song' && dormFilter !== 'all') {
    visible = visible.filter(p => dormOf(p) === dormFilter);
  }

  // リクエスト曲は 古い順（投稿順、昇順）= 放送キュー順。ピン留め上部。その他 tab は 従来通り ピン留め上部 + 降順。
  if (tab === 'song') {
    visible = [...visible].sort((a, b) => {
      const pinDiff = (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0);
      if (pinDiff !== 0) return pinDiff;
      const aKey = `${a.date} ${a.time || ''}`;
      const bKey = `${b.date} ${b.time || ''}`;
      return aKey.localeCompare(bKey); // 昇順 = 古い順 = キュー順
    });
  } else {
    visible = [...visible].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));
  }

  // 承認済みキューの順番 #n を割り当て（寮 × 朝/晩 の組合せごとに古い順 = 提出順）
  const approvedOrder = {};
  ['men', 'women'].forEach(d => {
    ['morning', 'evening'].forEach(slot => {
      posts.filter(p => p.cat === 'song' && !p.deleted && p.songStatus === 'approved' && p.timeSlot === slot && dormOf(p) === d)
        .sort((a, b) => `${a.date} ${a.time || ''}`.localeCompare(`${b.date} ${b.time || ''}`))
        .forEach((p, i) => { approvedOrder[p.id] = i + 1; });
    });
  });

  const stats = {
    total: posts.filter(p => !p.deleted).length,
    today: posts.filter(p => !p.deleted && p.date === '04-22').length,
    flagged: posts.filter(p => p.flagCount > 0 && !p.resolved && !p.deleted).length,
    deleted: posts.filter(p => p.deleted).length,
  };

  const tabs = [
    ['board', '掲示板', '学生からの一般投稿'],
    ['song', 'リクエスト曲', '寮内 BGM リクエスト · 提出順に再生'],
    ['anon', '匿名建議', '匿名で寮運営への意見'],
  ];

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>コミュニティ管理</div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, margin: '4px 0 20px' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>コミュニティ管理</h1>
        <div style={{ fontSize: 11, color: T.ink3 }}>担当寮：<b style={{ color: T.ink }}>{teacher && teacher.dorm === 'men' ? '男子寮' : '女子寮'}</b></div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <StatCard label="総投稿" value={stats.total} note="アクティブ" color={T.ink} />
        <StatCard label="本日投稿" value={stats.today} note="04-22" color={T.cobalt} />
        <StatCard label="通報中" value={stats.flagged} note="要確認" color={T.danger} onClick={stats.flagged > 0 ? () => setFilter('flagged') : null} />
        <StatCard label="削除済み" value={stats.deleted} note="今月累計" color={T.ink3} />
      </div>

      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${T.line}`, marginBottom: 14, flexWrap: 'wrap' }}>
        {tabs.map(([k, l, desc]) => {
          const count = posts.filter(p => p.cat === k && !p.deleted).length;
          const flagged = posts.filter(p => p.cat === k && !p.deleted && p.flagCount > 0 && !p.resolved).length;
          return (
            <button key={k} onClick={() => { setTab(k); setFilter('all'); }} style={{ padding: '10px 16px', background: 'transparent', border: 'none', borderBottom: tab === k ? `2px solid ${T.cobalt}` : '2px solid transparent', color: tab === k ? T.cobaltDeep : T.ink3, fontWeight: tab === k ? 700 : 500, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1, position: 'relative' }}>
              {l} <span style={{ color: T.ink3, fontSize: 11, fontWeight: 500 }}>({count})</span>
              {flagged > 0 && <span style={{ marginLeft: 6, fontSize: 10, background: T.danger, color: '#fff', padding: '1px 5px', borderRadius: 8, fontWeight: 700 }}>{flagged}</span>}
            </button>
          );
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, fontSize: 12, color: T.ink2, flexWrap: 'wrap' }}>
        <span style={{ color: T.ink3 }}>{tabs.find(t => t[0] === tab)[2]} ·</span>
        {[['all', '全て'], ['flagged', '通報あり'], ['pinned', 'ピン留め']].map(([k, l]) => (
          <button key={k} onClick={() => setFilter(k)} style={{ padding: '4px 10px', background: filter === k ? T.cobaltSoft : T.surface, color: filter === k ? T.cobaltDeep : T.ink3, border: `1px solid ${filter === k ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{l}</button>
        ))}
        {tab === 'song' && (
          <>
            <span style={{ color: T.ink3, marginLeft: 6 }}>寮 ·</span>
            {[['men', '男寮'], ['women', '女寮'], ['all', '両方']].map(([k, l]) => {
              const n = posts.filter(p => p.cat === 'song' && !p.deleted && (k === 'all' || dormOf(p) === k)).length;
              return (
                <button key={k} onClick={() => setDormFilter(k)} style={{ padding: '4px 10px', background: dormFilter === k ? T.cobaltSoft : T.surface, color: dormFilter === k ? T.cobaltDeep : T.ink3, border: `1px solid ${dormFilter === k ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{l} <span style={{ fontFamily: T.mono, opacity: 0.7 }}>{n}</span></button>
              );
            })}
            <span style={{ color: T.ink3, marginLeft: 6 }}>放送枠 ·</span>
            {[['all', '両方'], ['morning', '朝 ☀'], ['evening', '晩 🌙']].map(([k, l]) => (
              <button key={k} onClick={() => setSlotFilter(k)} style={{ padding: '4px 10px', background: slotFilter === k ? T.cobaltSoft : T.surface, color: slotFilter === k ? T.cobaltDeep : T.ink3, border: `1px solid ${slotFilter === k ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{l}</button>
            ))}
            <span style={{ color: T.ink3, marginLeft: 6 }}>審査 ·</span>
            {[['pending', '未対応'], ['approved', '承認'], ['rejected', '拒否'], ['all', '全て']].map(([k, l]) => {
              const n = posts.filter(p => p.cat === 'song' && !p.deleted && (k === 'all' || (p.songStatus || 'pending') === k)).length;
              return (
                <button key={k} onClick={() => setSongFilter(k)} style={{ padding: '4px 10px', background: songFilter === k ? T.cobaltSoft : T.surface, color: songFilter === k ? T.cobaltDeep : T.ink3, border: `1px solid ${songFilter === k ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{l} <span style={{ fontFamily: T.mono, opacity: 0.7 }}>{n}</span></button>
              );
            })}
          </>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 12 }}>
        {visible.map(p => <PostCard key={p.id} post={p} onDelete={handleDelete} onPin={handlePin} onResolve={handleResolve} onSongDecision={handleSongDecision} queueNo={approvedOrder[p.id]} />)}
        {visible.length === 0 && <div style={{ gridColumn: '1 / -1', padding: 40, textAlign: 'center', color: T.ink3, fontSize: 13, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 12 }}>このカテゴリーに投稿はありません</div>}
      </div>
    </div>
  );
}

function StatCard({ label, value, note, color, onClick }) {
  const T = window.RYO;
  return (
    <div onClick={onClick || undefined} style={{ padding: '14px 16px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, cursor: onClick ? 'pointer' : 'default', transition: 'border-color .15s' }}>
      <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, color, fontFamily: T.mono, margin: '4px 0' }}>{value}</div>
      <div style={{ fontSize: 11, color: T.ink3 }}>{note}</div>
    </div>
  );
}

function PostCard({ post, onDelete, onPin, onResolve, onSongDecision, queueNo }) {
  const T = window.RYO;
  const isAnon = post.cat === 'anon';
  const isSong = post.cat === 'song';
  const avatarColor = hashColor(post.author || 'A', T);
  const initial = isAnon ? '？' : (post.author || '').charAt(0) || '・';
  const slotLabel = isSong && post.timeSlot === 'morning' ? '朝 ☀' : isSong && post.timeSlot === 'evening' ? '晩 🌙' : null;
  const songStatus = isSong ? (post.songStatus || 'pending') : null;
  const statusMap = {
    pending:  { label: '未対応', fg: T.warn,   bg: T.warnSoft,   bd: T.warnBorder },
    approved: { label: '承認',   fg: T.ok,     bg: T.okSoft,     bd: T.okBorder },
    rejected: { label: '拒否',   fg: T.danger, bg: T.dangerSoft, bd: T.dangerBorder },
  };
  const st = songStatus && statusMap[songStatus];
  const borderColor = post.pinned ? T.cobalt
    : post.flagCount > 0 && !post.resolved ? T.danger
    : songStatus === 'approved' ? T.okBorder
    : songStatus === 'rejected' ? T.dangerBorder
    : T.line;
  return (
    <div style={{ padding: 14, background: T.surface, border: `1px solid ${borderColor}`, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 10, boxShadow: post.pinned ? T.shadow1 : 'none', opacity: songStatus === 'rejected' ? 0.7 : 1 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        {isSong && songStatus === 'approved' && queueNo && (
          <div title={`放送キュー #${queueNo}`} style={{ width: 36, height: 36, borderRadius: '50%', background: T.okSoft, color: T.ok, border: `1.5px solid ${T.okBorder}`, fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontFamily: T.mono }}>#{queueNo}</div>
        )}
        <div style={{ width: 36, height: 36, borderRadius: '50%', background: avatarColor, color: '#fff', fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{initial}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: T.ink }}>{isAnon ? '匿名' : post.author}{post.room && !isAnon && <span style={{ color: T.ink3, fontWeight: 500, marginLeft: 6, fontSize: 11 }}>· {post.room}</span>}</div>
          <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, marginTop: 2 }}>{post.date} {post.time}</div>
        </div>
        <div style={{ display: 'flex', gap: 4, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          {slotLabel && <span style={{ fontSize: 10, color: T.cobaltDeep, background: T.cobaltSoft, padding: '2px 7px', borderRadius: 4, fontWeight: 700, border: `1px solid ${T.cobalt}33`, whiteSpace: 'nowrap' }}>{slotLabel}</span>}
          {st && <span style={{ fontSize: 10, color: st.fg, background: st.bg, padding: '2px 7px', borderRadius: 4, fontWeight: 700, border: `1px solid ${st.bd}`, whiteSpace: 'nowrap' }}>{st.label}</span>}
          {post.pinned && <span style={{ fontSize: 10, color: '#fff', background: T.cobalt, padding: '2px 6px', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>PIN</span>}
          {post.flagCount > 0 && !post.resolved && <span style={{ fontSize: 10, color: T.danger, background: T.dangerSoft, padding: '2px 6px', borderRadius: 4, fontWeight: 700, border: `1px solid ${T.dangerBorder}` }}>通報 {post.flagCount}</span>}
        </div>
      </div>

      {post.title && <div style={{ fontSize: 14, fontWeight: 700, color: T.ink }}>{post.title}</div>}
      {post.body && <div style={{ fontSize: 13, lineHeight: 1.6, color: T.ink2, whiteSpace: 'pre-wrap' }}>{post.body}</div>}
      {isSong && post.decidedBy && (
        <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>{songStatus === 'approved' ? '承認' : '拒否'}：{post.decidedBy} · {post.decidedAt}</div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 6, borderTop: `1px solid ${T.line}`, fontSize: 11, color: T.ink3, flexWrap: 'wrap' }}>
        <span>♥ {post.likes || 0}</span>
        <span>💬 {post.comments || 0}</span>
        <div style={{ flex: 1 }} />
        {isSong && songStatus === 'pending' && (
          <>
            <button onClick={() => onSongDecision && onSongDecision(post.id, 'rejected')} style={{ padding: '4px 10px', background: T.surface, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>拒否</button>
            <button onClick={() => onSongDecision && onSongDecision(post.id, 'approved')} style={{ padding: '4px 10px', background: T.ok, color: '#fff', border: `1px solid ${T.ok}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}>承認</button>
          </>
        )}
        {isSong && songStatus !== 'pending' && (
          <button onClick={() => onSongDecision && onSongDecision(post.id, 'pending')} style={{ padding: '4px 10px', background: T.surface, color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>審査取消</button>
        )}
        {post.flagCount > 0 && !post.resolved && <button onClick={() => onResolve(post.id)} style={{ padding: '4px 10px', background: T.surface, color: T.ok, border: `1px solid ${T.okBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>通報解除</button>}
        <button onClick={() => onPin(post.id)} style={{ padding: '4px 10px', background: post.pinned ? T.cobaltSoft : T.surface, color: post.pinned ? T.cobaltDeep : T.ink3, border: `1px solid ${post.pinned ? T.cobalt : T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{post.pinned ? 'ピン解除' : 'ピン留め'}</button>
        <button onClick={() => onDelete(post.id)} style={{ padding: '4px 10px', background: T.surface, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>削除</button>
      </div>
    </div>
  );
}

function hashColor(s, T) {
  const palette = [T.cobalt, T.ok, T.warn, T.danger, '#7e57c2', '#0097a7', '#d84315', '#5d4037'];
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return palette[h % palette.length];
}

function Row({ date, msg }) {
  const T = window.RYO;
  return (
    <div style={{ display: 'flex', gap: 14, padding: '12px 14px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, marginBottom: 8, fontSize: 13 }}>
      <span style={{ fontFamily: T.mono, color: T.ink3, minWidth: 100 }}>{date}</span>
      <span>{msg}</span>
    </div>
  );
}

// Seed data: notice posts + community posts
window.NOTICE_POSTS = [
  { date: '04-21', title: '春期中間試験 実施要項について', body: '5/13〜5/17 に春期中間試験を実施します。試験期間中は静粛期間となり、消灯時刻は 22:30 に繰上げとなります。', author: '新股 先生', pinned: true },
  { date: '04-20', title: '寮内清掃チェック 実施日変更', body: '今週金曜日の清掃検査は土曜日 10:00 に延期となりました。', author: '中村 美和 先生', pinned: false },
  { date: '04-18', title: '避難訓練 4/25 実施予定', body: '全寮生対象。当日 14:00 集合・点呼後、速やかにグラウンドへ避難してください。', author: '山本 先生', pinned: false },
];

window.COMMUNITY_POSTS = [
  { id: 'C001', cat: 'board', author: 'リュウ イヒ', room: 'M101', date: '04-22', time: '08:14', body: '明日の朝食、卵焼きリクエストです 🍳 みんなで食堂のメニュー会議しませんか？', likes: 12, comments: 4, pinned: true, flagCount: 0 },
  { id: 'C002', cat: 'board', author: 'リシンさん', room: 'W113', date: '04-22', time: '07:50', body: '今日の避難訓練、女子寮は何時集合でしたっけ？', likes: 3, comments: 2, flagCount: 0 },
  { id: 'C003', cat: 'board', author: '田中 隼人', room: 'M104', date: '04-21', time: '22:10', body: '22 時消灯のはずなのに隣の部屋うるさいです。誰か静かにさせてください。', likes: 1, comments: 0, flagCount: 2 },
  { id: 'C004', cat: 'board', author: 'ゴテンウ', room: 'M114', date: '04-21', time: '18:45', body: 'Wi-Fi が不安定です。運営に報告しました。復旧は明日とのこと。', likes: 8, comments: 1, flagCount: 0 },
  { id: 'C005', cat: 'board', author: 'ソンキゼン', room: 'W114', date: '04-20', time: '20:00', body: '寮の門限って何時までですか？新入生なのでまだ把握してなくて…', likes: 2, comments: 5, flagCount: 0 },

  // リクエスト曲（寮内 BGM）— 古い順で表示。各投稿に timeSlot: 'morning'（朝）/ 'evening'（晩）。
  { id: 'C010', cat: 'song', author: 'ゴテンウ', room: 'M114', date: '04-20', time: '21:45', title: '夜に駆ける / YOASOBI', body: '', timeSlot: 'evening', songStatus: 'approved', decidedBy: '新股 先生', decidedAt: '22:10', likes: 11, comments: 3, flagCount: 0 },
  { id: 'C011', cat: 'song', author: '田中 隼人', room: 'M104', date: '04-20', time: '22:00', title: 'Pretender / Official髭男dism', body: '', timeSlot: 'evening', songStatus: 'approved', decidedBy: '新股 先生', decidedAt: '22:12', likes: 7, comments: 2, flagCount: 0 },
  { id: 'C012', cat: 'song', author: 'ソンキゼン', room: 'W114', date: '04-21', time: '18:40', title: '青と夏 / Mrs. Green Apple', body: '', timeSlot: 'evening', songStatus: 'pending', likes: 4, comments: 0, flagCount: 0 },
  { id: 'C013', cat: 'song', author: 'リシンさん', room: 'W113', date: '04-21', time: '19:15', title: 'ハナウタ / Kenshi Yonezu', body: '夜の BGM におすすめ。', timeSlot: 'evening', songStatus: 'pending', likes: 6, comments: 0, flagCount: 0 },
  { id: 'C014', cat: 'song', author: 'リュウ イヒ', room: 'M101', date: '04-22', time: '07:30', title: '春日和 / Aimer', body: '朝の放送で流してほしいです。気分が上がります。', timeSlot: 'morning', songStatus: 'pending', likes: 9, comments: 1, flagCount: 0 },
  { id: 'C015', cat: 'song', author: '田中 隼人', room: 'M104', date: '04-19', time: '23:10', title: '残酷な天使のテーゼ / 高橋洋子', body: '深夜テンションで申請。', timeSlot: 'evening', songStatus: 'rejected', decidedBy: '新股 先生', decidedAt: '23:20', likes: 2, comments: 4, flagCount: 0 },

  { id: 'C030', cat: 'anon', author: '匿名', date: '04-22', time: '03:20', body: '自販機にミネラルウォーターをもう少し増やしてほしいです。よく売り切れてます。', likes: 15, comments: 8, flagCount: 0 },
  { id: 'C031', cat: 'anon', author: '匿名', date: '04-20', time: '23:50', body: '食堂のメニュー、もう少し多様化してほしいです。外国人留学生向けの選択肢が少ない。', likes: 22, comments: 12, flagCount: 0 },
  { id: 'C032', cat: 'anon', author: '匿名', date: '04-18', time: '14:00', body: 'Wi-Fi の速度を改善してほしい。', likes: 9, comments: 3, flagCount: 0 },
];

// 行事カレンダー seed — iOS 側と同型データ。date は YYYY-MM-DD。
window.CALENDAR_EVENTS = [
  { date: '2026-04-23', time: '18:00', title: '新入生歓迎会',     location: '食堂' },
  { date: '2026-04-25', time: '14:00', title: '避難訓練',         location: 'グラウンド' },
  { date: '2026-04-28', time: '09:00', title: 'デモ日',           location: '寮玄関' },
  { date: '2026-05-03', time: null,    title: 'GW 始め',          location: '—' },
  { date: '2026-05-13', time: '08:30', title: '春期中間試験 開始', location: '高校棟' },
  { date: '2026-05-17', time: '15:00', title: '春期中間試験 終了', location: '高校棟' },
];

// バス告知 seed — 2026-03-22 特別運行便（実公告ベース、詳細は 06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md）
window.BUS_POSTS = [
  {
    id: 'BP001',
    category: '特別運行便',
    title: '特別運行便に関するお知らせ',
    posted_on: '2026-03-22',
    posted_by: '国際交流部・技師',
    effective_from: '2026-04-01',
    effective_until: null,
    pinned: true,
    body: '学校休業日等に、寮生やボランティア等に取り組む通学生は、特別運航便(無料スクールバス)に乗車して構いません。寮生は乗車名簿に事前にチェックをつけて下さい。バス乗車時は、挨拶等の礼儀作法に気をつけてください。\n\n＊集中して学習やスポーツに取り組む時間と自由なオフタイムのメリハリをつけ、節約しながら休日は思いっ切りリフレッシュしてほしいので、特別運航便を案内しますが、技師(運転士)から悪い報告を受けた場合は該当者の乗車を一定期間拒否することがあり得ます。\n\n＊乗車簿を寮監が確認後、多すぎる場合は乗車便調整を行う場合があります。\n\n＊長期間の帰省・一時帰国等のタイミングは、情勢変化によって変更があり得ます。',
    events: [
      { date: '2026-04-05', name: '留4アクティビティ', audience: '4月生及び4月生をサポートする意志・日本語力・英語力を有する者のみ乗車・参加 → 参加希望者は高野まで', items: [
        { time: '08:30', action: 'お花見弁当受取り', location: '食堂', memo: '女子寮・渡邊へ（15 食 +α）' },
        { time: '08:50', action: '朝点呼', location: '', memo: '渡邊・ジェニファー' },
        { time: '09:10', action: '日本語プレイスメントテスト', location: '', memo: '' },
        { time: '10:10', action: '英語プレイスメントテスト', location: '', memo: '' },
        { time: '11:25', action: '留4スクバ乗車', location: '', memo: '' },
        { time: '12:15', action: 'RSK 山陽放送局前下車・徒歩移動', location: 'RSK', memo: '県立図書館紹介' },
        { time: '12:30', action: '岡山城芝生広場で昼食・見学', location: '岡山城', memo: '' },
        { time: '14:00', action: '記念撮影', location: '岡山城', memo: '' },
        { time: '14:15', action: '後楽園散策', location: '後楽園', memo: '' },
        { time: '15:00', action: 'さくらカーニバル 自由散策', location: '河川敷', memo: '各自現金持参' },
        { time: '16:00', action: '後楽園入口集合', location: '後楽園', memo: '' },
        { time: '16:15', action: '丸善岡山シンフォニーホール見学', location: '', memo: '日本語・各科目コーナー中心' },
        { time: '16:45', action: '出口集合', location: '', memo: '' },
        { time: '17:00', action: 'RSK 山陽放送局前乗車', location: 'RSK', memo: 'バスは駐車不可、必ず待つ' },
        { time: '17:45', action: '帰寮', location: '', memo: '' },
      ] },
      { date: '2026-04-07', name: '帰寮日', audience: '', items: [
        { time: '15:33', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
        { time: '18:45', action: '岡山駅西口発（寮行き）', location: '岡山駅西口', memo: '' },
      ] },
      { date: '2026-04-11', name: 'みつ元気プロジェクト・買い物等', audience: '', items: [
        { time: '08:30', action: '西口発', location: '西口', memo: '' },
        { time: '09:20', action: '高校棟バス乗り場発（御津公民館行き）', location: '高校棟', memo: '' },
        { time: '09:45', action: '御津公民館着 → 戦略会議', location: '御津公民館', memo: '' },
        { time: '10:10', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '' },
        { time: '12:00', action: '御津公民館発', location: '御津公民館', memo: '' },
        { time: '12:20', action: '高校棟バス乗り場発（西口行き）', location: '高校棟', memo: '' },
        { time: '13:00', action: '西口着', location: '西口', memo: '' },
        { time: '15:33', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
        { time: '17:02', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
      ] },
      { date: '2026-04-29', name: 'GW 外泊・帰省等、買い物等', audience: '', items: [
        { time: '07:30', action: '高校棟バス乗り場発（岡山駅西口行き）', location: '高校棟', memo: '' },
        { time: '10:10', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '' },
        { time: '15:33', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
        { time: '17:02', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
      ] },
      { date: '2026-05-06', name: 'GW 後帰寮日、買い物等', audience: '', items: [
        { time: '09:20', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '' },
        { time: '10:10', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '' },
        { time: '15:33', action: '金川駅発（寮行き）', location: '金川駅', memo: '' },
        { time: '18:45', action: '岡山駅西口発（寮行き）', location: '岡山駅西口', memo: '' },
      ] },
      { date: '2026-05-23', name: '音楽と青空市（岡山市立御津公民館）', audience: '基本ボランティア用、時間帯等注意', items: [
        { time: '07:30', action: '岡山駅西口発', location: '岡山駅西口', memo: '' },
        { time: '08:15', action: '高校棟発', location: '高校棟', memo: '' },
        { time: '08:35', action: '御津公民館着', location: '御津公民館', memo: '' },
        { time: '16:00', action: '御津公民館発', location: '御津公民館', memo: '' },
        { time: '16:20', action: '高校棟発', location: '高校棟', memo: '' },
        { time: '17:00', action: '岡山駅西口着', location: '岡山駅西口', memo: '' },
      ] },
      { date: '2026-05-31', name: '英検第 1 回一次試験・買い物等', audience: '英検時程に合わせて時程調整予定', items: [
        { time: '06:40', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '級受験者＋買い物等希望者' },
        { time: '09:20', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '買い物等希望者' },
        { time: '11:00', action: '高校棟バス乗り場発（金川駅行き）', location: '高校棟', memo: '英検級受験者＋買い物等希望者' },
        { time: '15:33', action: '金川駅発（寮行き）', location: '金川駅', memo: '買い物等希望者' },
        { time: '17:31', action: '金川駅発（寮行き）', location: '金川駅', memo: '英検級受験者＋買い物等希望者' },
      ] },
    ],
  },
  {
    id: 'BP002',
    category: '定期便',
    title: '平日 通学定期便',
    posted_on: '2026-04-01',
    posted_by: '寮務課',
    effective_from: '2026-04-01',
    effective_until: null,
    pinned: false,
    body: '平日（月〜金）の定期スクールバス運行時刻。長期休業期間は運休。',
    events: [
      { date: '平日', name: '登校便', audience: '全寮生', items: [
        { time: '07:30', action: '岡山駅西口 → 高校棟', location: '岡山駅西口', memo: '毎日 1 便' },
      ] },
      { date: '平日', name: '下校便', audience: '全寮生', items: [
        { time: '17:00', action: '高校棟発 → 寮', location: '高校棟', memo: '' },
        { time: '18:30', action: '高校棟発 → 寮', location: '高校棟', memo: '部活動対応' },
        { time: '21:00', action: '高校棟発 → 寮', location: '高校棟', memo: '自習室閉館後' },
      ] },
    ],
  },
];

window.RecordsPage = RecordsPage;
window.SearchPage = SearchPage;
window.NotificationsPage = NotificationsPage;
window.CleaningPage = CleaningPage;
window.InfoPage = InfoPage;
window.CommunityPage = CommunityPage;
