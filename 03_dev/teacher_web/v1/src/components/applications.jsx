// /applications landing + outstay detail modal (digitised from real form).
//
// ⭐ 外泊申請の提出期限ルール (2026-04-22 itsuki 拍板):
//   出発日の属する週の水曜日 23:59 / 出発予定時刻の 48 時間前、いずれか早い方。
//   期限後の申請は受付不可 → iOS App でも送信ブロック、寮監との直接面談必要。
//   老師 Web 側では "期限超過" badge + modal でアラート表示。

function parseJst(s) {
  // 受け入れる形: 'YYYY-MM-DD HH:MM' or 'MM-DD HH:MM'（その場合は 2026 年扱い）
  const full = (s && s.length <= 11) ? '2026-' + s : s;
  return full ? new Date(full.replace(' ', 'T') + ':00+09:00') : null;
}

function outstayDeadline(departStr) {
  const depart = parseJst(departStr);
  if (!depart) return null;
  // (a) 出発 48h 前
  const h48 = new Date(depart.getTime() - 48 * 3600 * 1000);
  // (b) 出発日の属する週の水曜 23:59（週始 = 月曜の ISO 方式）
  const wed = new Date(depart);
  const dow = wed.getDay(); // 0=日, 1=月, ..., 3=水, ..., 6=土
  const isoDow = dow === 0 ? 6 : dow - 1; // 0=月
  const delta = 2 - isoDow; // 水曜までの差
  wed.setDate(wed.getDate() + delta);
  wed.setHours(23, 59, 59, 999);
  return wed < h48 ? wed : h48;
}

function isLateSubmission(departStr, submittedStr) {
  const deadline = outstayDeadline(departStr);
  const submitted = parseJst(submittedStr);
  if (!deadline || !submitted) return false;
  return submitted > deadline;
}

function formatJst(d) {
  if (!d) return '—';
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const jaDow = ['日','月','火','水','木','金','土'][d.getDay()];
  return `${y}-${m}-${day}（${jaDow}） ${hh}:${mm}`;
}

function ApplicationsPage({ onOpen }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('outstay');
  const [sub, setSub] = React.useState('pending');

  const outstayPending = (window.OUTSTAY_APPS || []).filter(a => a.state === 'pending').length;
  const tabs = [
    { k: 'outstay', label: '外泊', badge: outstayPending },
    { k: 'return',  label: '帰国', badge: 1 },
    { k: 'home',    label: '帰省', badge: 0 },
    { k: 'taxi',    label: 'タクシー', badge: 1 },
  ];

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>申請 &gt; {tabs.find(t=>t.k===tab).label}</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: '4px 0 18px', letterSpacing: -0.3 }}>申請センター</h1>

      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${T.line}`, marginBottom: 18 }}>
        {tabs.map(t => (
          <button key={t.k} onClick={() => setTab(t.k)} style={{
            padding: '10px 18px', background: 'transparent', border: 'none',
            borderBottom: tab === t.k ? `2px solid ${T.cobalt}` : '2px solid transparent',
            color: tab === t.k ? T.cobaltDeep : T.ink3, fontWeight: tab === t.k ? 700 : 500,
            fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1, position: 'relative',
          }}>
            {t.label}
            {t.badge > 0 && <span style={{ marginLeft: 6, fontSize: 10, background: T.danger, color: '#fff', padding: '1px 6px', borderRadius: 8, fontWeight: 700 }}>{t.badge}</span>}
          </button>
        ))}
      </div>

      {tab === 'outstay' && <OutstayRuleBanner />}

      {tab === 'outstay' ? (
        <OutstayList sub={sub} setSub={setSub} onOpen={onOpen} />
      ) : (
        <SkeletonTabBody tab={tabs.find(t => t.k === tab).label} />
      )}
    </div>
  );
}

function OutstayRuleBanner() {
  const T = window.RYO;
  const [open, setOpen] = React.useState(true);
  if (!open) {
    return (
      <button onClick={() => setOpen(true)} style={{ padding: '7px 14px', background: 'transparent', color: T.ink3, border: `1px dashed ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 11, cursor: 'pointer', marginBottom: 14 }}>📅 外泊申請の提出期限ルールを表示</button>
    );
  }
  return (
    <div style={{ padding: '12px 16px', background: T.cobaltSoft, color: T.cobaltDeep, border: `1px solid ${T.infoBorder}`, borderRadius: 10, fontSize: 12, lineHeight: 1.7, marginBottom: 14, display: 'flex', gap: 12, alignItems: 'flex-start' }}>
      <span style={{ fontSize: 16 }}>📅</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>外泊申請 提出期限ルール</div>
        <div>提出期限 = <b>出発日の属する週の水曜日 23:59</b> または <b>出発予定時刻の 48 時間前</b>、<b>いずれか早い方</b>。</div>
        <div style={{ marginTop: 3 }}>期限後は iOS App から送信できません。やむを得ない事情がある場合は、<b>必ず生徒本人が寮監室に来て直接相談</b>してください。</div>
      </div>
      <button onClick={() => setOpen(false)} style={{ background: 'transparent', border: 'none', color: T.cobaltDeep, cursor: 'pointer', fontSize: 14, padding: 0 }}>×</button>
    </div>
  );
}

function OutstayList({ sub, setSub, onOpen }) {
  const T = window.RYO;
  const apps = window.OUTSTAY_APPS;
  const subs = ['pending', 'approved', 'rejected', 'question', 'all'];
  const subLabels = { pending: '審査待ち', approved: '承認済', rejected: '却下', question: '質問あり', all: '全て' };
  const filtered = sub === 'all' ? apps : apps.filter(a => a.state === sub);

  return (
    <>
      <div style={{ display: 'flex', gap: 6, marginBottom: 14, alignItems: 'center' }}>
        {subs.map(s => (
          <button key={s} onClick={() => setSub(s)} style={{
            padding: '5px 12px', background: sub === s ? T.cobalt : T.surface,
            color: sub === s ? '#fff' : T.ink2, border: `1px solid ${sub === s ? T.cobalt : T.lineStrong}`,
            borderRadius: 999, fontFamily: 'inherit', fontSize: 12, fontWeight: 600, cursor: 'pointer',
          }}>{subLabels[s]}</button>
        ))}
        <div style={{ flex: 1 }} />
        <button onClick={() => alert('Demo 版未対応')} style={{ padding: '6px 12px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 12, cursor: 'pointer' }}>CSV 出力</button>
      </div>

      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '140px 70px 80px 140px 140px 90px 120px 110px 90px 80px', background: T.surfaceAlt, color: T.ink2, fontSize: 11, fontWeight: 600, letterSpacing: 1, borderBottom: `1px solid ${T.line}` }}>
          {['申請者', '部屋', '担当寮', '出発日時', '帰舎予定', '行先', '提出時刻', '期限', '状態', '操作'].map(h => <div key={h} style={{ padding: '10px 12px' }}>{h}</div>)}
        </div>
        {filtered.map((a, i) => (
          <div key={a.id} onClick={() => onOpen(a)} style={{ display: 'grid', gridTemplateColumns: '140px 70px 80px 140px 140px 90px 120px 110px 90px 80px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 12, alignItems: 'center', cursor: 'pointer', transition: 'background .1s' }}
               onMouseEnter={e => e.currentTarget.style.background = T.surfaceAlt}
               onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
            <div style={{ padding: '10px 12px', fontWeight: 600 }}>{a.applicant}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono }}>{a.room}</div>
            <div style={{ padding: '10px 12px' }}><window.DormBadge dorm={a.dorm} /></div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, color: T.ink2 }}>{a.depart}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, color: T.ink2 }}>{a.return_}</div>
            <div style={{ padding: '10px 12px' }}>{a.city}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, color: T.ink3 }}>{a.submitted}</div>
            <div style={{ padding: '10px 12px' }}><DeadlineBadge depart={a.depart} submitted={a.submitted} /></div>
            <div style={{ padding: '10px 12px' }}><StateBadge s={a.state} /></div>
            <div style={{ padding: '10px 12px', color: T.cobalt, fontSize: 12, fontWeight: 700, textAlign: 'left' }}>詳細 →</div>
          </div>
        ))}
        {filtered.length === 0 && <div style={{ padding: 40, textAlign: 'center', color: T.ink3, fontSize: 13 }}>まだデータがありません</div>}
      </div>
    </>
  );
}

function StateBadge({ s }) {
  const T = window.RYO;
  const map = {
    pending:  [T.warn, T.warnSoft, T.warnBorder, '審査待ち'],
    approved: [T.ok, T.okSoft, T.okBorder, '承認済'],
    rejected: [T.danger, T.dangerSoft, T.dangerBorder, '却下'],
    question: [T.cobalt, T.cobaltSoft, T.infoBorder, '質問あり'],
  }[s];
  return <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: map[1], color: map[0], border: `1px solid ${map[2]}`, letterSpacing: .5, whiteSpace: 'nowrap' }}>{map[3]}</span>;
}

function DeadlineBadge({ depart, submitted }) {
  const T = window.RYO;
  const late = isLateSubmission(depart, submitted);
  const commonStyle = { fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, letterSpacing: .5, whiteSpace: 'nowrap' };
  if (late) return <span title="期限後提出 · 寮監との面談が必要" style={{ ...commonStyle, background: T.dangerSoft, color: T.danger, border: `1px solid ${T.dangerBorder}` }}>⚠ 期限後</span>;
  return <span title="期限内に提出済" style={{ ...commonStyle, background: T.okSoft, color: T.ok, border: `1px solid ${T.okBorder}` }}>✓ 期限内</span>;
}

function SkeletonTabBody({ tab }) {
  const T = window.RYO;
  return (
    <div style={{ padding: '40px 20px', textAlign: 'center', background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 12 }}>
      <div style={{ fontSize: 11, color: T.warn, letterSpacing: 2, fontWeight: 700 }}>開発中</div>
      <div style={{ fontSize: 15, color: T.ink, fontWeight: 600, marginTop: 6 }}>{tab}申請 · 近日実装</div>
      <div style={{ fontSize: 12, color: T.ink3, marginTop: 6 }}>一覧・詳細 modal は「外泊」と同パターンで提供予定。</div>
    </div>
  );
}

// Outstay demo data
window.OUTSTAY_APPS = [
  {
    id: 'O-2026-0421-01', applicant: 'リュウ イヒ', room: 'M101', dorm: 'men',
    grade: '中 1 年 1 組', phone: '080-9490-2895',
    companion: { name: 'チャン ユエ', phone: '080-xxxx-xxxx' },
    depart: '2026-04-22 09:15', return_: '2026-04-23 17:00',
    methodGo: '西口バス便', methodBack: 'JR', flightNo: '',
    specialTransport: { on: true, from: '04-22', to: '04-23' },
    lodging: { type: '日本人宅', name: 'ジ・ワンフィス(ゾ) 岡山', address: '岡山市北区野田 1-1-3', city: '岡山' },
    meals: { breakfast: 1, lunch: 2, dinner: 2, selfInput: true },
    reason: '保護者と合流して市内観光・買い物。',
    note: '帰舎は日曜夕方までに確実に戻ります。',
    parentOk: { confirmed: true, phone: '090-xxxx-xxxx' },
    submitted: '04-19 20:10', state: 'pending',
    city: '岡山',
    approvals: [
      { role: '担任', name: '新股 先生', state: 'pending' },
      { role: '寮務課長', name: '—', state: 'pending' },
      { role: '管理課長', name: '—', state: 'pending' },
      { role: '国際交流部長', name: '杉原 先生', state: 'pending' },
    ],
  },
  {
    id: 'O-2026-0421-02', applicant: '田中 隼人', room: 'M104', dorm: 'men',
    grade: '中 2 年 2 組', phone: '080-1234-5678',
    companion: { name: '—', phone: '—' },
    depart: '2026-04-25 15:00', return_: '2026-04-27 18:00',
    methodGo: 'JR', methodBack: 'JR', flightNo: '',
    specialTransport: { on: false },
    lodging: { type: 'ホテル', name: 'ホテルグランヴィア岡山', address: '岡山市北区駅元町 1-5', city: '岡山' },
    meals: { breakfast: 2, lunch: 0, dinner: 2, selfInput: false },
    reason: '家族と合流、祖母の誕生日祝い。',
    note: '',
    parentOk: { confirmed: true, phone: '090-yyyy-yyyy' },
    submitted: '04-21 09:10', state: 'pending',
    city: '岡山',
    approvals: [
      { role: '担任', name: '新股 先生', state: 'approved' },
      { role: '寮務課長', name: '中村 先生', state: 'pending' },
      { role: '管理課長', name: '—', state: 'pending' },
      { role: '国際交流部長', name: '杉原 先生', state: 'pending' },
    ],
  },
  {
    id: 'O-2026-0420-03', applicant: 'リシンさん', room: 'W113', dorm: 'women',
    grade: '中 1 年 2 組', phone: '080-2345-6789',
    companion: { name: '—', phone: '—' },
    depart: '2026-04-19 10:00', return_: '2026-04-20 19:00',
    methodGo: '自家用車', methodBack: '自家用車', flightNo: '',
    specialTransport: { on: false },
    lodging: { type: '自宅', name: '自宅', address: '—', city: '倉敷' },
    meals: { breakfast: 1, lunch: 2, dinner: 1, selfInput: false },
    reason: '法事のため帰省。',
    note: '', parentOk: { confirmed: true, phone: '090-zzzz-zzzz' },
    submitted: '04-15 20:00', state: 'approved',
    city: '倉敷',
    approvals: [
      { role: '担任', name: '新股 先生', state: 'approved' },
      { role: '寮務課長', name: '中村 先生', state: 'approved' },
      { role: '管理課長', name: '山本 先生', state: 'approved' },
      { role: '国際交流部長', name: '杉原 先生', state: 'approved' },
    ],
  },
  {
    id: 'O-2026-0419-04', applicant: 'ゴテンウ', room: 'M114', dorm: 'men',
    grade: '中 2 年 1 組', phone: '080-9876-5432',
    companion: { name: '—', phone: '—' },
    depart: '2026-04-18 18:00', return_: '2026-04-19 21:00',
    methodGo: 'タクシー', methodBack: 'タクシー', flightNo: '',
    specialTransport: { on: false },
    lodging: { type: 'その他', name: '親戚宅', address: '岡山市南区—', city: '岡山' },
    meals: { breakfast: 1, lunch: 1, dinner: 1, selfInput: false },
    reason: '親戚訪問。',
    note: '', parentOk: { confirmed: true, phone: '—' },
    submitted: '04-17 22:15', state: 'question',
    city: '岡山',
    approvals: [
      { role: '担任', name: '新股 先生', state: 'question' },
      { role: '寮務課長', name: '—', state: 'pending' },
      { role: '管理課長', name: '—', state: 'pending' },
      { role: '国際交流部長', name: '杉原 先生', state: 'pending' },
    ],
  },
];

window.ApplicationsPage = ApplicationsPage;
window.StateBadge = StateBadge;
window.DeadlineBadge = DeadlineBadge;
window.outstayDeadline = outstayDeadline;
window.isLateSubmission = isLateSubmission;
window.formatJstDeadline = formatJst;
window.parseJst = parseJst;
