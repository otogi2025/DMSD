// /records, /search, /notifications, /cleaning, /info, /community pages.

function RecordsPage({ teacher, params, onNav }) {
  const T = window.RYO;
  const date = params && params.date || '2026-04-21';
  const roster = teacher.dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  const statuses = ['ok','ok','ok','late','ok','absent','ok','ok','exempt','ok','ok','ok'];
  const methods  = ['NFC卡','NFC卡','Shortcut','手動','NFC卡','—','NFC卡','NFC卡','—','NFC卡','NFC卡','Shortcut'];
  const times    = ['19:30','19:31','19:31','19:34','19:32','—','19:33','19:31','—','19:32','19:30','19:31'];
  const rows = roster.map(([room, id, name], i) => {
    const k = i % statuses.length;
    return { room, id, name, session: '晩点呼 · 普通寮生', time: times[k], status: statuses[k], method: methods[k], overrider: k === 3 ? `${teacher.name} 先生` : '—' };
  });

  return (
    <div style={{ padding: '28px 32px 48px', maxWidth: 1280 }}>
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
    <div style={{ padding: '28px 32px 48px', maxWidth: 1180 }}>
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
  const sample1 = roster[0][2];
  const sample2 = roster[3][2];
  const sample3 = roster[1][2];
  return (
    <div style={{ padding: '28px 32px 48px', maxWidth: 1100 }}>
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
        {[['田中 美咲', 'W102', '04-21'], ['山本 綾', 'W103', '04-20'], ['小林 美優', 'W104', '04-20']].map(([n, r, d], i) => (
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
    setPosts([{ date, title, body, author: teacher && teacher.name || '田中 健一 先生', pinned: false }, ...posts]);
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
      {tab === 'event' && (<div>{[['04-25', '避難訓練'], ['04-28', 'デモ日'], ['05-03', 'GW 始め']].map(([d, m], i) => <Row key={i} date={d} msg={m} />)}</div>)}
      {tab === 'bus' && (<div>{[['07:00', '寮 → 学校'], ['12:00', '寮 → 市街'], ['18:00', '市街 → 寮']].map(([d, m], i) => <Row key={i} date={d} msg={m} />)}</div>)}
      {composing && <ComposeNoticeModal onClose={() => setComposing(false)} onSubmit={handlePost} />}
    </div>
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

  const handleDelete = (id) => { if (confirm('この投稿を削除しますか？学生のアプリからも非表示になります。')) setPosts(posts.map(p => p.id === id ? { ...p, deleted: true } : p)); };
  const handlePin = (id) => setPosts(posts.map(p => p.id === id ? { ...p, pinned: !p.pinned } : p));
  const handleResolve = (id) => setPosts(posts.map(p => p.id === id ? { ...p, flagCount: 0, resolved: true } : p));

  const catPosts = posts.filter(p => p.cat === tab && !p.deleted);
  let visible = catPosts;
  if (filter === 'flagged') visible = catPosts.filter(p => p.flagCount > 0 && !p.resolved);
  if (filter === 'pinned') visible = catPosts.filter(p => p.pinned);
  visible = [...visible].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));

  const stats = {
    total: posts.filter(p => !p.deleted).length,
    today: posts.filter(p => !p.deleted && p.date === '04-22').length,
    flagged: posts.filter(p => p.flagCount > 0 && !p.resolved && !p.deleted).length,
    deleted: posts.filter(p => p.deleted).length,
  };

  const tabs = [
    ['board', '掲示板', '学生からの一般投稿'],
    ['song', 'リクエスト曲', '館内 BGM リクエスト'],
    ['lost', '忘れ物', '拾得物・紛失物の共有'],
    ['anon', '匿名建議', '匿名で寮運営への意見'],
    ['delivery', '宅配通知', '宅配到着の自動通知'],
  ];

  return (
    <div style={{ padding: '28px 32px 48px', maxWidth: 1280 }}>
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

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, fontSize: 12, color: T.ink2 }}>
        <span style={{ color: T.ink3 }}>{tabs.find(t => t[0] === tab)[2]} ·</span>
        {[['all', '全て'], ['flagged', '通報あり'], ['pinned', 'ピン留め']].map(([k, l]) => (
          <button key={k} onClick={() => setFilter(k)} style={{ padding: '4px 10px', background: filter === k ? T.cobaltSoft : T.surface, color: filter === k ? T.cobaltDeep : T.ink3, border: `1px solid ${filter === k ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{l}</button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: tab === 'delivery' ? '1fr' : 'repeat(auto-fill, minmax(360px, 1fr))', gap: 12 }}>
        {visible.map(p => <PostCard key={p.id} post={p} onDelete={handleDelete} onPin={handlePin} onResolve={handleResolve} />)}
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

function PostCard({ post, onDelete, onPin, onResolve }) {
  const T = window.RYO;
  const isAnon = post.cat === 'anon';
  const isDelivery = post.cat === 'delivery';
  const avatarColor = hashColor(post.author || 'A', T);
  const initial = isAnon ? '？' : (post.author || '').charAt(0) || '・';
  return (
    <div style={{ padding: 14, background: T.surface, border: `1px solid ${post.pinned ? T.cobalt : post.flagCount > 0 && !post.resolved ? T.danger : T.line}`, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 10, boxShadow: post.pinned ? T.shadow1 : 'none' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: '50%', background: avatarColor, color: '#fff', fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{initial}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: T.ink }}>{isAnon ? '匿名' : post.author}{post.room && !isAnon && <span style={{ color: T.ink3, fontWeight: 500, marginLeft: 6, fontSize: 11 }}>· {post.room}</span>}</div>
          <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, marginTop: 2 }}>{post.date} {post.time}</div>
        </div>
        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          {post.pinned && <span style={{ fontSize: 10, color: '#fff', background: T.cobalt, padding: '2px 6px', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>PIN</span>}
          {post.flagCount > 0 && !post.resolved && <span style={{ fontSize: 10, color: T.danger, background: T.dangerSoft, padding: '2px 6px', borderRadius: 4, fontWeight: 700, border: `1px solid ${T.dangerBorder}` }}>通報 {post.flagCount}</span>}
        </div>
      </div>

      {post.title && <div style={{ fontSize: 14, fontWeight: 700, color: T.ink }}>{post.title}</div>}
      <div style={{ fontSize: 13, lineHeight: 1.6, color: T.ink2, whiteSpace: 'pre-wrap' }}>{post.body}</div>

      {!isDelivery && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, paddingTop: 6, borderTop: `1px solid ${T.line}`, fontSize: 11, color: T.ink3 }}>
          <span>♥ {post.likes || 0}</span>
          <span>💬 {post.comments || 0}</span>
          <div style={{ flex: 1 }} />
          {post.flagCount > 0 && !post.resolved && <button onClick={() => onResolve(post.id)} style={{ padding: '4px 10px', background: T.surface, color: T.ok, border: `1px solid ${T.okBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>通報解除</button>}
          <button onClick={() => onPin(post.id)} style={{ padding: '4px 10px', background: post.pinned ? T.cobaltSoft : T.surface, color: post.pinned ? T.cobaltDeep : T.ink3, border: `1px solid ${post.pinned ? T.cobalt : T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>{post.pinned ? 'ピン解除' : 'ピン留め'}</button>
          <button onClick={() => onDelete(post.id)} style={{ padding: '4px 10px', background: T.surface, color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>削除</button>
        </div>
      )}
      {isDelivery && (
        <div style={{ display: 'flex', gap: 8, paddingTop: 6, borderTop: `1px solid ${T.line}` }}>
          <span style={{ fontSize: 10, color: post.picked ? T.ok : T.warn, background: post.picked ? T.okSoft : T.warnSoft, padding: '3px 8px', borderRadius: 4, fontWeight: 700, border: `1px solid ${post.picked ? T.okBorder : T.warnBorder}` }}>{post.picked ? '受取済' : '未受取'}</span>
        </div>
      )}
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
  { date: '04-21', title: '春期中間試験 実施要項について', body: '5/13〜5/17 に春期中間試験を実施します。試験期間中は静粛期間となり、消灯時刻は 22:30 に繰上げとなります。', author: '田中 健一 先生', pinned: true },
  { date: '04-20', title: '寮内清掃チェック 実施日変更', body: '今週金曜日の清掃検査は土曜日 10:00 に延期となりました。', author: '中村 美和 先生', pinned: false },
  { date: '04-18', title: '避難訓練 4/25 実施予定', body: '全寮生対象。当日 14:00 集合・点呼後、速やかにグラウンドへ避難してください。', author: '山本 先生', pinned: false },
];

window.COMMUNITY_POSTS = [
  { id: 'C001', cat: 'board', author: 'リュウ イヒ', room: 'M101', date: '04-22', time: '08:14', body: '明日の朝食、卵焼きリクエストです 🍳 みんなで食堂のメニュー会議しませんか？', likes: 12, comments: 4, pinned: true, flagCount: 0 },
  { id: 'C002', cat: 'board', author: '田中 美咲', room: 'W102', date: '04-22', time: '07:50', body: '今日の避難訓練、女子寮は何時集合でしたっけ？', likes: 3, comments: 2, flagCount: 0 },
  { id: 'C003', cat: 'board', author: '佐藤 健太', room: 'M102', date: '04-21', time: '22:10', body: '22 時消灯のはずなのに隣の部屋うるさいです。誰か静かにさせてください。', likes: 1, comments: 0, flagCount: 2 },
  { id: 'C004', cat: 'board', author: '高橋 翔', room: 'M103', date: '04-21', time: '18:45', body: 'Wi-Fi が不安定です。運営に報告しました。復旧は明日とのこと。', likes: 8, comments: 1, flagCount: 0 },
  { id: 'C005', cat: 'board', author: '山本 綾', room: 'W103', date: '04-20', time: '20:00', body: '寮の門限って何時までですか？新入生なのでまだ把握してなくて…', likes: 2, comments: 5, flagCount: 0 },

  { id: 'C010', cat: 'song', author: 'リュウ イヒ', room: 'M101', date: '04-22', time: '07:30', title: '春日和 / Aimer', body: '朝の放送で流してほしいです。気分が上がります。', likes: 9, comments: 1, flagCount: 0 },
  { id: 'C011', cat: 'song', author: '田中 美咲', room: 'W102', date: '04-21', time: '19:15', title: 'ハナウタ / Kenshi Yonezu', body: '夜の BGM におすすめ。', likes: 6, comments: 0, flagCount: 0 },
  { id: 'C012', cat: 'song', author: '山本 綾', room: 'W103', date: '04-21', time: '18:40', title: '青と夏 / Mrs. Green Apple', body: '', likes: 4, comments: 0, flagCount: 0 },
  { id: 'C013', cat: 'song', author: '佐藤 健太', room: 'M102', date: '04-20', time: '22:00', title: 'Pretender / Official髭男dism', body: '', likes: 7, comments: 2, flagCount: 0 },
  { id: 'C014', cat: 'song', author: '高橋 翔', room: 'M103', date: '04-20', time: '21:45', title: '夜に駆ける / YOASOBI', body: '', likes: 11, comments: 3, flagCount: 0 },

  { id: 'C020', cat: 'lost', author: 'チャン ユエ', room: 'W104', date: '04-22', time: '09:00', title: 'ピンクの水筒', body: '食堂に置き忘れました。見つけた方は W104 まで…', likes: 0, comments: 1, flagCount: 0 },
  { id: 'C021', cat: 'lost', author: '山本 綾', room: 'W103', date: '04-21', time: '16:20', title: '黒の折り畳み傘', body: '玄関に置いてあったのですが朝には消えてました。', likes: 0, comments: 0, flagCount: 0 },
  { id: 'C022', cat: 'lost', author: '高橋 翔', room: 'M103', date: '04-19', time: '08:00', title: 'ワイヤレスイヤホン（AirPods）', body: '風呂場周辺で紛失。', likes: 0, comments: 2, flagCount: 0 },

  { id: 'C030', cat: 'anon', author: '匿名', date: '04-22', time: '03:20', body: '洗濯機の予約制にしてほしい。いつも順番待ちでつらいです。', likes: 15, comments: 8, flagCount: 0 },
  { id: 'C031', cat: 'anon', author: '匿名', date: '04-20', time: '23:50', body: '食堂のメニュー、もう少し多様化してほしいです。外国人留学生向けの選択肢が少ない。', likes: 22, comments: 12, flagCount: 0 },
  { id: 'C032', cat: 'anon', author: '匿名', date: '04-18', time: '14:00', body: 'Wi-Fi の速度を改善してほしい。', likes: 9, comments: 3, flagCount: 0 },

  { id: 'C040', cat: 'delivery', author: 'リュウ イヒ', room: 'M101', date: '04-22', time: '14:30', body: '荷物 1 件（ヤマト運輸）フロント預かり', picked: false, flagCount: 0 },
  { id: 'C041', cat: 'delivery', author: '佐藤 健太', room: 'M102', date: '04-22', time: '11:15', body: '荷物 2 件（佐川急便）フロント預かり', picked: false, flagCount: 0 },
  { id: 'C042', cat: 'delivery', author: '田中 美咲', room: 'W102', date: '04-21', time: '18:20', body: '荷物 1 件（Amazon）受取済', picked: true, flagCount: 0 },
];

window.RecordsPage = RecordsPage;
window.SearchPage = SearchPage;
window.NotificationsPage = NotificationsPage;
window.CleaningPage = CleaningPage;
window.InfoPage = InfoPage;
window.CommunityPage = CommunityPage;
