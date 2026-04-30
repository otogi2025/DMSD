// Front Desk page — 宅配通知 + 忘れ物（2026-04-24 追加、コミュニティから拆分）

function FrontDeskPage({ teacher }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('delivery');
  const [deliveries, setDeliveries] = React.useState(window.FRONT_DELIVERIES);
  const [lostItems, setLostItems] = React.useState(window.FRONT_LOST_ITEMS);
  const [filter, setFilter] = React.useState('all');
  const [composing, setComposing] = React.useState(false);

  const markPicked = (id) => setDeliveries(deliveries.map(d => d.id === id ? { ...d, picked: true, pickedAt: formatNow() } : d));
  const deleteDelivery = (id) => { if (confirm('この宅配通知を削除しますか？')) setDeliveries(deliveries.filter(d => d.id !== id)); };
  const addDelivery = (data) => { setDeliveries([{ ...data, id: 'D' + Date.now(), date: todayShort(), time: nowHHMM(), picked: false }, ...deliveries]); setComposing(false); };

  const returnLost = (id) => setLostItems(lostItems.map(l => l.id === id ? { ...l, status: 'returned', returnedAt: formatNow() } : l));
  const archiveLost = (id) => setLostItems(lostItems.map(l => l.id === id ? { ...l, status: 'archived' } : l));
  const addLost = (data) => { setLostItems([{ ...data, id: 'L' + Date.now(), date: todayShort(), status: 'open' }, ...lostItems]); setComposing(false); };

  const delFiltered = deliveries.filter(d => filter === 'all' ? true : filter === 'unpicked' ? !d.picked : d.picked);
  const lostFiltered = lostItems.filter(l => filter === 'all' ? true : filter === 'open' ? l.status === 'open' : filter === 'returned' ? l.status === 'returned' : l.status === 'archived');

  const stats = tab === 'delivery' ? {
    total: deliveries.length,
    unpicked: deliveries.filter(d => !d.picked).length,
    today: deliveries.filter(d => d.date === todayShort()).length,
    picked: deliveries.filter(d => d.picked).length,
  } : {
    total: lostItems.length,
    open: lostItems.filter(l => l.status === 'open').length,
    returned: lostItems.filter(l => l.status === 'returned').length,
    archived: lostItems.filter(l => l.status === 'archived').length,
  };

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>フロント業務</div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, margin: '4px 0 6px' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>フロント業務</h1>
        <button onClick={() => setComposing(true)} style={{ padding: '8px 16px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer', boxShadow: T.shadow1 }}>＋ {tab === 'delivery' ? '宅配通知を追加' : '忘れ物を登録'}</button>
      </div>
      <div style={{ fontSize: 12, color: T.ink3, marginBottom: 18 }}>寮監前台受付の代行記録 — 宅配便の到着通知と、館内で見つかった忘れ物の管理。</div>

      {/* stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        {tab === 'delivery' ? (
          <>
            <FdStat label="累計" value={stats.total} note="全受付" color={T.ink} />
            <FdStat label="未受取" value={stats.unpicked} note="要対応" color={T.warn} onClick={stats.unpicked > 0 ? () => setFilter('unpicked') : null} />
            <FdStat label="本日受付" value={stats.today} note={todayShort()} color={T.cobalt} />
            <FdStat label="受取済" value={stats.picked} note="完了" color={T.ok} />
          </>
        ) : (
          <>
            <FdStat label="累計" value={stats.total} note="全登録" color={T.ink} />
            <FdStat label="未返却" value={stats.open} note="持主探索中" color={T.warn} onClick={stats.open > 0 ? () => setFilter('open') : null} />
            <FdStat label="返却済" value={stats.returned} note="持主判明" color={T.ok} />
            <FdStat label="保管庫行" value={stats.archived} note="1ヶ月経過" color={T.ink3} />
          </>
        )}
      </div>

      {/* tabs */}
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${T.line}`, marginBottom: 14 }}>
        {[['delivery', '宅配通知', deliveries.length], ['lost', '忘れ物', lostItems.length]].map(([k, l, n]) => (
          <button key={k} onClick={() => { setTab(k); setFilter('all'); }} style={{ padding: '10px 16px', background: 'transparent', border: 'none', borderBottom: tab === k ? `2px solid ${T.cobalt}` : '2px solid transparent', color: tab === k ? T.cobaltDeep : T.ink3, fontWeight: tab === k ? 700 : 500, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1 }}>
            {l} <span style={{ color: T.ink3, fontSize: 11, fontWeight: 500 }}>({n})</span>
          </button>
        ))}
      </div>

      {/* filter chips */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, fontSize: 12, color: T.ink2 }}>
        {tab === 'delivery' ? (
          [['all', '全て'], ['unpicked', '未受取'], ['picked', '受取済']].map(([k, l]) => (
            <button key={k} onClick={() => setFilter(k)} style={chipStyle(T, filter === k)}>{l}</button>
          ))
        ) : (
          [['all', '全て'], ['open', '未返却'], ['returned', '返却済'], ['archived', '保管庫']].map(([k, l]) => (
            <button key={k} onClick={() => setFilter(k)} style={chipStyle(T, filter === k)}>{l}</button>
          ))
        )}
      </div>

      {/* list */}
      {tab === 'delivery' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {delFiltered.length === 0 && <EmptyRow T={T} />}
          {delFiltered.map(d => <DeliveryRow key={d.id} d={d} T={T} onPick={markPicked} onDelete={deleteDelivery} />)}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {lostFiltered.length === 0 && <EmptyRow T={T} />}
          {lostFiltered.map(l => <LostItemRow key={l.id} l={l} T={T} onReturn={returnLost} onArchive={archiveLost} />)}
        </div>
      )}

      {composing && tab === 'delivery' && <DeliveryComposeModal T={T} onClose={() => setComposing(false)} onSubmit={addDelivery} />}
      {composing && tab === 'lost' && <LostItemComposeModal T={T} onClose={() => setComposing(false)} onSubmit={addLost} />}
    </div>
  );
}

function FdStat({ label, value, note, color, onClick }) {
  const T = window.RYO;
  return (
    <div onClick={onClick || undefined} style={{ padding: '14px 16px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, cursor: onClick ? 'pointer' : 'default' }}>
      <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, color, fontFamily: T.mono, margin: '4px 0' }}>{value}</div>
      <div style={{ fontSize: 11, color: T.ink3 }}>{note}</div>
    </div>
  );
}

function DeliveryRow({ d, T, onPick, onDelete }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', background: T.surface, border: `1px solid ${d.picked ? T.line : T.warnBorder}`, borderRadius: 10 }}>
      <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 4, background: d.picked ? T.okSoft : T.warnSoft, color: d.picked ? T.ok : T.warn, border: `1px solid ${d.picked ? T.okBorder : T.warnBorder}`, letterSpacing: .5, whiteSpace: 'nowrap', minWidth: 68, textAlign: 'center' }}>
        {d.picked ? '受取済' : '未受取'}
      </span>
      <span style={{ fontFamily: T.mono, fontSize: 12, color: T.ink3, minWidth: 95 }}>{d.date} {d.time}</span>
      <span style={{ fontSize: 13, fontWeight: 600, minWidth: 120 }}>{d.student}</span>
      <span style={{ fontFamily: T.mono, fontSize: 11, color: T.ink3, minWidth: 50 }}>{d.room}</span>
      <span style={{ fontSize: 12, color: T.ink2, flex: 1 }}>{d.carrier} · {d.count} 件{d.memo && ` · ${d.memo}`}</span>
      {d.picked && d.pickedAt && <span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>{d.pickedAt} 受取</span>}
      {!d.picked && <button onClick={() => onPick(d.id)} style={actionBtn(T, 'ok')}>受取済に</button>}
      <button onClick={() => onDelete(d.id)} style={actionBtn(T, 'danger')}>削除</button>
    </div>
  );
}

function LostItemRow({ l, T, onReturn, onArchive }) {
  const statusMap = { open: [T.warn, T.warnSoft, T.warnBorder, '未返却'], returned: [T.ok, T.okSoft, T.okBorder, '返却済'], archived: [T.ink3, T.surfaceAlt, T.line, '保管庫'] };
  const [col, bg, bd, lbl] = statusMap[l.status];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', background: T.surface, border: `1px solid ${bd}`, borderRadius: 10 }}>
      <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 4, background: bg, color: col, border: `1px solid ${bd}`, letterSpacing: .5, whiteSpace: 'nowrap', minWidth: 68, textAlign: 'center' }}>{lbl}</span>
      <span style={{ fontFamily: T.mono, fontSize: 12, color: T.ink3, minWidth: 55 }}>{l.date}</span>
      <span style={{ fontSize: 13, fontWeight: 600, minWidth: 150 }}>{l.title}</span>
      <span style={{ fontSize: 12, color: T.ink3, minWidth: 100 }}>発見場所: {l.foundAt}</span>
      <span style={{ fontSize: 12, color: T.ink2, flex: 1 }}>{l.memo}</span>
      {l.status === 'returned' && l.returnedAt && <span style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>{l.returnedAt} 返却</span>}
      {l.status === 'open' && <>
        <button onClick={() => onReturn(l.id)} style={actionBtn(T, 'ok')}>返却済に</button>
        <button onClick={() => onArchive(l.id)} style={actionBtn(T, 'ghost')}>保管庫へ</button>
      </>}
    </div>
  );
}

function DeliveryComposeModal({ T, onClose, onSubmit }) {
  const [student, setStudent] = React.useState('');
  const [room, setRoom] = React.useState('');
  const [carrier, setCarrier] = React.useState('ヤマト運輸');
  const [count, setCount] = React.useState('1');
  const [memo, setMemo] = React.useState('');
  const studentOptions = window.ROSTER_ALL || [];

  const handleStudentChange = (name) => {
    setStudent(name);
    const match = studentOptions.find(([, , n]) => n === name);
    if (match) setRoom(match[0]);
  };

  return (
    <ModalShell T={T} title="宅配通知を追加" onClose={onClose}>
      <Field T={T} label="受取人">
        <input list="roster-list" value={student} onChange={e => handleStudentChange(e.target.value)} placeholder="学生名を入力または選択" style={inputStyle(T)} />
        <datalist id="roster-list">
          {studentOptions.map(([r, id, n]) => <option key={id} value={n}>{r}号室</option>)}
        </datalist>
      </Field>
      <Field T={T} label="部屋番号"><input value={room} onChange={e => setRoom(e.target.value)} placeholder="M101 / W113 等" style={inputStyle(T)} /></Field>
      <Field T={T} label="配送業者">
        <select value={carrier} onChange={e => setCarrier(e.target.value)} style={inputStyle(T)}>
          {['ヤマト運輸', '佐川急便', '日本郵便', 'Amazon', '福山通運', 'その他'].map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </Field>
      <Field T={T} label="件数"><input type="number" min="1" value={count} onChange={e => setCount(e.target.value)} style={inputStyle(T)} /></Field>
      <Field T={T} label="備考"><input value={memo} onChange={e => setMemo(e.target.value)} placeholder="例：冷蔵必要 / 大型" style={inputStyle(T)} /></Field>
      <ModalFooter T={T} onClose={onClose} onSubmit={() => student.trim() && onSubmit({ student: student.trim(), room: room.trim() || '—', carrier, count: parseInt(count, 10) || 1, memo: memo.trim() })} disabled={!student.trim()} />
    </ModalShell>
  );
}

function LostItemComposeModal({ T, onClose, onSubmit }) {
  const [title, setTitle] = React.useState('');
  const [foundAt, setFoundAt] = React.useState('');
  const [memo, setMemo] = React.useState('');
  return (
    <ModalShell T={T} title="忘れ物を登録" onClose={onClose}>
      <Field T={T} label="物品名"><input value={title} onChange={e => setTitle(e.target.value)} placeholder="例：黒の折り畳み傘" style={inputStyle(T)} /></Field>
      <Field T={T} label="発見場所"><input value={foundAt} onChange={e => setFoundAt(e.target.value)} placeholder="玄関 / 食堂 / 風呂場 / ロビー 等" style={inputStyle(T)} /></Field>
      <Field T={T} label="特徴・備考"><textarea value={memo} onChange={e => setMemo(e.target.value)} rows={3} placeholder="色・サイズ・拾った人等" style={{ ...inputStyle(T), resize: 'vertical', lineHeight: 1.5 }} /></Field>
      <ModalFooter T={T} onClose={onClose} onSubmit={() => title.trim() && onSubmit({ title: title.trim(), foundAt: foundAt.trim() || '—', memo: memo.trim() })} disabled={!title.trim()} />
    </ModalShell>
  );
}

// Shared modal atoms
function ModalShell({ T, title, onClose, children }) {
  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(20,23,31,0.55)', zIndex: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: T.surface, borderRadius: 14, width: 540, maxWidth: '100%', boxShadow: T.shadowModal, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: `1px solid ${T.line}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: 15, fontWeight: 700 }}>{title}</div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', fontSize: 20, color: T.ink3, cursor: 'pointer' }}>×</button>
        </div>
        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>{children}</div>
      </div>
    </div>
  );
}
function Field({ T, label, children }) {
  return (
    <div>
      <div style={{ fontSize: 11, color: T.ink3, fontWeight: 600, letterSpacing: 1, marginBottom: 6 }}>{label}</div>
      {children}
    </div>
  );
}
function ModalFooter({ T, onClose, onSubmit, disabled }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 6 }}>
      <button onClick={onClose} style={{ padding: '8px 16px', background: T.surface, color: T.ink2, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>キャンセル</button>
      <button onClick={onSubmit} disabled={disabled} style={{ padding: '8px 16px', background: disabled ? T.line : T.cobalt, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: disabled ? 'not-allowed' : 'pointer' }}>登録</button>
    </div>
  );
}
function EmptyRow({ T }) {
  return <div style={{ padding: 36, textAlign: 'center', color: T.ink3, fontSize: 13, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 10 }}>該当する項目はありません</div>;
}

// Style helpers
function chipStyle(T, on) {
  return { padding: '4px 10px', background: on ? T.cobaltSoft : T.surface, color: on ? T.cobaltDeep : T.ink3, border: `1px solid ${on ? T.cobalt : T.lineStrong}`, borderRadius: 999, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer' };
}
function actionBtn(T, kind) {
  const map = { ok: [T.ok, T.okBorder], danger: [T.danger, T.dangerBorder], ghost: [T.ink3, T.lineStrong] };
  const [col, bd] = map[kind];
  return { padding: '5px 12px', background: T.surface, color: col, border: `1px solid ${bd}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' };
}
function inputStyle(T) {
  return { width: '100%', padding: '9px 12px', border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontSize: 13, fontFamily: 'inherit', boxSizing: 'border-box', background: T.surface, color: T.ink };
}

// Date helpers
function todayShort() {
  const d = new Date();
  return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function nowHHMM() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}
function formatNow() { return `${todayShort()} ${nowHHMM()}`; }

// Seed data
window.FRONT_DELIVERIES = [
  { id: 'D001', student: 'リュウ イヒ', room: 'M101', carrier: 'ヤマト運輸', count: 1, memo: '', date: '04-22', time: '14:30', picked: false },
  { id: 'D002', student: '田中 隼人', room: 'M104', carrier: '佐川急便', count: 2, memo: '', date: '04-22', time: '11:15', picked: false },
  { id: 'D003', student: 'リシンさん', room: 'W113', carrier: 'Amazon', count: 1, memo: '', date: '04-21', time: '18:20', picked: true, pickedAt: '04-21 19:30' },
  { id: 'D004', student: 'ゴテンウ', room: 'M114', carrier: '日本郵便', count: 1, memo: '書留', date: '04-20', time: '10:05', picked: true, pickedAt: '04-20 18:22' },
  { id: 'D005', student: 'ソンキゼン', room: 'W114', carrier: 'ヤマト運輸', count: 3, memo: '冷蔵', date: '04-19', time: '09:30', picked: true, pickedAt: '04-19 19:10' },
];

window.FRONT_LOST_ITEMS = [
  { id: 'L001', title: 'ピンクの水筒', foundAt: '食堂', memo: 'サーモス製、ステッカー付き', date: '04-22', status: 'open' },
  { id: 'L002', title: '黒の折り畳み傘', foundAt: '玄関', memo: '傘袋なし', date: '04-21', status: 'open' },
  { id: 'L003', title: 'ワイヤレスイヤホン（AirPods）', foundAt: '風呂場付近', memo: 'ケースにシール有り', date: '04-19', status: 'returned', returnedAt: '04-20 08:30' },
  { id: 'L004', title: '青色ボールペン', foundAt: 'ロビー', memo: '', date: '03-15', status: 'archived' },
];

window.FrontDeskPage = FrontDeskPage;
// 共有 modal helper（pages-records-search-etc の BusPostComposeModal / 他から使用）
window.ModalShell = ModalShell;
window.ModalField = Field;
window.ModalFooter = ModalFooter;
window.modalInputStyle = inputStyle;
