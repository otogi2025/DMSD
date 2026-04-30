// 学生アカウント管理ページ — 寮監がパスワード重置・連絡先更新・ロック解除を行う
// iOS App 内ではパスワード変更不可 (iOS DESIGN §3.7) のため、本画面が唯一の自改え経路
// 番号 00 = リュウ イヒ (demo seed)、01 以降 = 真実登録

function AccountsPage({ teacher }) {
  const T = window.RYO;
  const [accounts, setAccounts] = React.useState(window.ACCOUNTS);
  const [query, setQuery] = React.useState('');
  const [dormFilter, setDormFilter] = React.useState('all'); // all / men / women / locked
  const [detailTarget, setDetailTarget] = React.useState(null);
  const [toast, setToast] = React.useState(null);

  const normalize = (s) => (s || '').replace(/\s+/g, '').toLowerCase();
  const qn = normalize(query);

  let visible = accounts.filter(a => {
    if (dormFilter === 'men' && a.dorm !== 'men') return false;
    if (dormFilter === 'women' && a.dorm !== 'women') return false;
    if (dormFilter === 'locked' && !a.locked) return false;
    if (!qn) return true;
    return normalize(`${a.no}${a.name}${a.sid}${a.email}${a.phone}${a.room}`).includes(qn);
  });
  visible = [...visible].sort((a, b) => a.no.localeCompare(b.no));

  const stats = {
    total: accounts.length,
    men: accounts.filter(a => a.dorm === 'men').length,
    women: accounts.filter(a => a.dorm === 'women').length,
    locked: accounts.filter(a => a.locked).length,
    thisMonthNew: accounts.filter(a => a.registeredAt >= '2026-04-01').length,
  };

  const handleSave = (patch) => {
    setAccounts(list => list.map(a => a.no === patch.no ? { ...a, ...patch } : a));
    setToast({ type: 'ok', msg: `番号 ${patch.no} ${patch.name} のアカウントを更新しました` });
    setDetailTarget(null);
  };
  const handlePasswordReset = (no) => {
    const tempPw = Math.random().toString(36).slice(2, 10);
    setAccounts(list => list.map(a => a.no === no ? { ...a, failedLoginCount: 0, locked: false } : a));
    setToast({ type: 'ok', msg: `番号 ${no} · 新しい仮パスワード「${tempPw}」を発行しました（本人に直接伝えてください）` });
  };
  const handleUnlock = (no) => {
    setAccounts(list => list.map(a => a.no === no ? { ...a, locked: false, failedLoginCount: 0 } : a));
    setToast({ type: 'ok', msg: `番号 ${no} のロックを解除しました` });
  };

  React.useEffect(() => { if (toast) { const id = setTimeout(() => setToast(null), 4000); return () => clearTimeout(id); } }, [toast]);

  const DEMO_NO = window.DEMO_SEED_NO; // 060218 = リュウ イヒ
  const nextNoHint = '06????'; // 番号 6 桁: 学年(2)+組(2)+番号(2)。iOS 登録時に学生本人入力

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>学生管理</div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, margin: '4px 0 20px' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>学生アカウント管理</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => alert(`新規登録は iOS App から本人入力（番号 = 学年 2 桁 + 組 2 桁 + 番号 2 桁、例：高 3 B 18 = 060218）。demo 版で老師側追加未対応`)} style={{ padding: '8px 14px', background: 'transparent', color: T.cobalt, border: `1px solid ${T.cobalt}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>＋ 新規追加（iOS から）</button>
          <button onClick={() => alert('CSV 出力 · Demo 版未対応')} style={{ padding: '8px 14px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer' }}>CSV 出力</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <AcctStat label="総アカウント" value={stats.total} note={`男性寮 ${stats.men} · 女性寮 ${stats.women}`} color={T.ink} />
        <AcctStat label="今月新規" value={stats.thisMonthNew} note={stats.thisMonthNew > 0 ? '2026-04' : '無し'} color={T.cobalt} />
        <AcctStat label="ロック中" value={stats.locked} note={stats.locked > 0 ? '要対応' : '異常無し'} color={stats.locked > 0 ? T.danger : T.ok} onClick={stats.locked > 0 ? () => setDormFilter('locked') : null} />
        <AcctStat label="番号フォーマット" value={nextNoHint} note="学年+組+番号 6 桁" color={T.ink3} mono />
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 14, flexWrap: 'wrap' }}>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="番号・氏名・学籍番号・メール・部屋で検索（スペース無視）"
          style={{ flex: 1, minWidth: 280, padding: '10px 14px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 10, fontFamily: 'inherit', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
        <div style={{ display: 'flex', gap: 4, background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 999, padding: 3 }}>
          {[['all', '全員'], ['men', '男性寮'], ['women', '女性寮'], ['locked', 'ロック中']].map(([k, l]) => (
            <button key={k} onClick={() => setDormFilter(k)} style={{ padding: '5px 14px', background: dormFilter === k ? T.cobalt : 'transparent', color: dormFilter === k ? '#fff' : T.ink2, border: 'none', borderRadius: 999, fontFamily: 'inherit', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>{l}</button>
          ))}
        </div>
      </div>

      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '130px 160px 90px 90px 1fr 140px 130px 110px 90px', background: T.surfaceAlt, fontSize: 11, color: T.ink2, fontWeight: 600, letterSpacing: 1, borderBottom: `1px solid ${T.line}` }}>
          {['番号', '氏名', '部屋', '担当寮', 'メールアドレス', '電話番号', '最終ログイン', '状態', ''].map(h => <div key={h} style={{ padding: '10px 12px' }}>{h}</div>)}
        </div>
        {visible.map((a, i) => (
          <div key={a.no} onClick={() => setDetailTarget(a)}
            style={{ display: 'grid', gridTemplateColumns: '130px 160px 90px 90px 1fr 140px 130px 110px 90px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 12.5, alignItems: 'center', cursor: 'pointer', transition: 'background .1s' }}
            onMouseEnter={e => e.currentTarget.style.background = T.surfaceAlt}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, fontWeight: 700, color: a.no === DEMO_NO ? T.cobalt : T.ink2 }}>
              {a.no}{a.no === DEMO_NO && <span style={{ fontSize: 9, marginLeft: 6, padding: '1px 5px', background: T.cobaltSoft, color: T.cobaltDeep, borderRadius: 3, letterSpacing: 1 }}>DEMO</span>}
            </div>
            <div style={{ padding: '10px 12px', fontWeight: 600 }}>{a.name}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, color: T.ink3 }}>{a.room}</div>
            <div style={{ padding: '10px 12px' }}><window.DormBadge dorm={a.dorm} /></div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, fontSize: 11, color: T.ink2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.email}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>{a.phone}</div>
            <div style={{ padding: '10px 12px', fontFamily: T.mono, fontSize: 11, color: T.ink3 }}>{a.lastLoginAt.slice(5)}</div>
            <div style={{ padding: '10px 12px' }}>
              {a.locked
                ? <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: T.dangerSoft, color: T.danger, border: `1px solid ${T.dangerBorder}` }}>🔒 ロック</span>
                : a.failedLoginCount > 0
                  ? <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: T.warnSoft, color: T.warn, border: `1px solid ${T.warnBorder}` }}>失敗 {a.failedLoginCount}</span>
                  : <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4, background: T.okSoft, color: T.ok, border: `1px solid ${T.okBorder}` }}>正常</span>}
            </div>
            <div style={{ padding: '10px 12px', color: T.cobalt, fontSize: 12, fontWeight: 700 }}>詳細 →</div>
          </div>
        ))}
        {visible.length === 0 && <div style={{ padding: 40, textAlign: 'center', color: T.ink3, fontSize: 13 }}>該当するアカウントがありません</div>}
      </div>

      {detailTarget && <AccountDetailModal account={detailTarget} onClose={() => setDetailTarget(null)} onSave={handleSave} onPasswordReset={handlePasswordReset} onUnlock={handleUnlock} />}
      {toast && (
        <div style={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', background: toast.type === 'ok' ? T.okSoft : T.warnSoft, color: toast.type === 'ok' ? T.ok : T.warn, border: `1px solid ${toast.type === 'ok' ? T.okBorder : T.warnBorder}`, padding: '10px 18px', borderRadius: 999, fontSize: 13, fontWeight: 600, zIndex: 1000, boxShadow: T.shadow2, maxWidth: 600 }}>{toast.msg}</div>
      )}
    </div>
  );
}

function AcctStat({ label, value, note, color, onClick, mono }) {
  const T = window.RYO;
  return (
    <div onClick={onClick || undefined} style={{ padding: '14px 16px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, cursor: onClick ? 'pointer' : 'default' }}>
      <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 1.5, fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, color, fontFamily: mono ? T.mono : T.mono, margin: '4px 0' }}>{value}</div>
      <div style={{ fontSize: 11, color: T.ink3 }}>{note}</div>
    </div>
  );
}

function AccountDetailModal({ account, onClose, onSave, onPasswordReset, onUnlock }) {
  const T = window.RYO;
  const [tab, setTab] = React.useState('profile');
  const [email, setEmail] = React.useState(account.email);
  const [phone, setPhone] = React.useState(account.phone);
  const [room, setRoom] = React.useState(account.room);
  const dirty = email !== account.email || phone !== account.phone || room !== account.room;

  const genderLabel = { male: '男性', female: '女性' }[account.gender] || '—';
  const ageYears = (() => {
    const b = new Date(account.birthday);
    const now = new Date('2026-04-22');
    let age = now.getFullYear() - b.getFullYear();
    if (now < new Date(now.getFullYear(), b.getMonth(), b.getDate())) age--;
    return age;
  })();

  // mock activity
  const activities = buildActivityMock(account);

  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(20,23,31,.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, fontFamily: T.font, padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ width: 820, maxHeight: '94vh', overflow: 'auto', background: T.surface, borderRadius: 14, boxShadow: T.shadowModal, color: T.ink }}>
        <div style={{ padding: '20px 28px 16px', borderBottom: `1px solid ${T.line}`, background: T.surfaceAlt, borderRadius: '14px 14px 0 0', display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 56, height: 56, borderRadius: 28, background: T.cobaltSoft, color: T.cobaltDeep, fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{account.name.charAt(0)}</div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontFamily: T.mono, fontSize: 14, color: T.ink3, fontWeight: 700 }}>番号 {account.no}</span>
              {account.no === '00' && <span style={{ fontSize: 10, padding: '2px 8px', background: T.cobalt, color: '#fff', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>DEMO SEED</span>}
              {account.locked && <span style={{ fontSize: 10, padding: '2px 8px', background: T.danger, color: '#fff', borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>🔒 ロック中</span>}
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3, marginTop: 2 }}>{account.name}</div>
            <div style={{ fontSize: 12, color: T.ink3, marginTop: 2 }}>学籍番号 {account.sid} · {account.room} · {window.dormLabel(account.dorm)} · {account.category}</div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', fontSize: 22, color: T.ink3, cursor: 'pointer' }}>×</button>
        </div>

        <div style={{ display: 'flex', gap: 4, padding: '0 28px', borderBottom: `1px solid ${T.line}` }}>
          {[['profile', 'プロフィール・設定'], ['activity', 'アクティビティ履歴']].map(([k, l]) => (
            <button key={k} onClick={() => setTab(k)} style={{ padding: '12px 18px', background: 'transparent', border: 'none', borderBottom: tab === k ? `2px solid ${T.cobalt}` : '2px solid transparent', color: tab === k ? T.cobaltDeep : T.ink3, fontWeight: tab === k ? 700 : 500, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer', marginBottom: -1 }}>{l}</button>
          ))}
        </div>

        {tab === 'profile' && (
          <div style={{ padding: '22px 28px' }}>
            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 700, marginBottom: 10, paddingBottom: 6, borderBottom: `1px solid ${T.line}` }}>§ 基本情報（編集不可 · 登録時に確定）</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 20px', marginBottom: 24 }}>
              <Field label="番号" mono>{account.no}</Field>
              <Field label="学籍番号" mono>{account.sid}</Field>
              <Field label="氏名">{account.name}</Field>
              <Field label="生年月日 · 年齢" mono>{account.birthday} · {ageYears} 歳</Field>
              <Field label="性別">{genderLabel}</Field>
              <Field label="学生類別">{account.category}</Field>
              <Field label="担当寮">{window.dormLabel(account.dorm)}</Field>
              <Field label="登録日" mono>{account.registeredAt}</Field>
            </div>

            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 700, marginBottom: 10, paddingBottom: 6, borderBottom: `1px solid ${T.line}` }}>§ 編集可能項目</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 20px', marginBottom: 24 }}>
              <EditField label="部屋番号" value={room} onChange={setRoom} mono />
              <div />
              <EditField label="メールアドレス" value={email} onChange={setEmail} type="email" />
              <EditField label="電話番号" value={phone} onChange={setPhone} mono />
            </div>

            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 700, marginBottom: 10, paddingBottom: 6, borderBottom: `1px solid ${T.line}` }}>§ パスワード・セキュリティ</div>
            <div style={{ background: T.warnSoft, border: `1px solid ${T.warnBorder}`, borderRadius: 8, padding: '12px 14px', marginBottom: 12, fontSize: 12, color: T.warn, lineHeight: 1.7 }}>
              ⚠️ パスワードは iOS App 内で変更できません。本人がロックされた・忘れた場合は、下のボタンで仮パスワードを発行してください（本人に直接伝達）。
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button onClick={() => { if (confirm(`番号 ${account.no} ${account.name} のパスワードを初期化し、仮パスワードを発行しますか？`)) onPasswordReset(account.no); }}
                style={{ padding: '9px 18px', background: T.warn, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>🔑 パスワード初期化・仮発行</button>
              {account.locked && (
                <button onClick={() => { if (confirm(`番号 ${account.no} のロックを解除しますか？`)) onUnlock(account.no); }}
                  style={{ padding: '9px 18px', background: T.danger, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>🔓 ロック解除</button>
              )}
              <button onClick={() => alert('アカウント無効化 · Demo 版未対応（卒業・退寮時に使用）')} style={{ padding: '9px 18px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, cursor: 'pointer' }}>アカウント無効化</button>
            </div>

            {account.failedLoginCount > 0 && (
              <div style={{ marginTop: 14, padding: '10px 14px', background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 8, fontSize: 12, color: T.ink2 }}>
                <b>ログイン失敗: {account.failedLoginCount} 回</b> · 3 回で 30 秒ロック、以降解除後に再失敗すると自動でロック時間がエスカレート（1 分 → 5 分 → 30 分 → 1 時間 → 永久）
              </div>
            )}
          </div>
        )}

        {tab === 'activity' && (
          <div style={{ padding: '22px 28px' }}>
            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 700, marginBottom: 12 }}>§ この学生の最近のアクティビティ</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {activities.map((act, i) => (
                <div key={i} style={{ display: 'flex', gap: 12, padding: '12px 14px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 14, background: act.color + '1a', color: act.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, flexShrink: 0 }}>{act.icon}</div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: T.ink }}>{act.title}</div>
                    <div style={{ fontSize: 12, color: T.ink2, marginTop: 2 }}>{act.body}</div>
                  </div>
                  <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, whiteSpace: 'nowrap' }}>{act.when}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16, fontSize: 11, color: T.ink3, textAlign: 'center' }}>過去 30 日分表示 · 全履歴は「記録」「規律・処分」「申請センター」で個別に確認できます</div>
          </div>
        )}

        <div style={{ padding: '14px 28px', borderTop: `1px solid ${T.line}`, background: T.surfaceAlt, display: 'flex', justifyContent: 'flex-end', gap: 8, borderRadius: '0 0 14px 14px' }}>
          <button onClick={onClose} style={{ padding: '9px 18px', background: 'transparent', color: T.ink, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>閉じる</button>
          {tab === 'profile' && (
            <button disabled={!dirty} onClick={() => onSave({ no: account.no, name: account.name, email, phone, room })}
              style={{ padding: '9px 20px', background: dirty ? T.cobalt : T.lineStrong, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: dirty ? 'pointer' : 'not-allowed' }}>保存</button>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children, mono }) {
  const T = window.RYO;
  return (
    <div>
      <div style={{ fontSize: 10, color: T.ink3, fontWeight: 600, letterSpacing: 1, marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 13, color: T.ink, fontFamily: mono ? T.mono : 'inherit' }}>{children}</div>
    </div>
  );
}

function EditField({ label, value, onChange, type = 'text', mono }) {
  const T = window.RYO;
  return (
    <div>
      <div style={{ fontSize: 10, color: T.ink3, fontWeight: 600, letterSpacing: 1, marginBottom: 5 }}>{label}</div>
      <input type={type} value={value} onChange={e => onChange(e.target.value)}
        style={{ width: '100%', padding: '8px 10px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: mono ? T.mono : 'inherit', fontSize: 13, color: T.ink, outline: 'none', boxSizing: 'border-box' }} />
    </div>
  );
}

function buildActivityMock(a) {
  // 各番号ごとに少し違うアクティビティを mock（seed dependent）
  const T = window.RYO;
  const base = [
    { icon: '✓', color: T.ok,     title: '点呼チェックイン', body: '晩点呼 · 時間内 · NFC カード', when: '04-22 19:30' },
    { icon: '📋', color: T.cobalt, title: 'ログイン', body: 'iOS App · iPhone 17 Pro', when: a.lastLoginAt.slice(5) },
  ];
  if (a.failedLoginCount > 0) base.push({ icon: '⚠', color: T.warn, title: `ログイン失敗 ${a.failedLoginCount} 回`, body: 'パスワード誤入力 · 自動ロック前の警告', when: '04-22 17:50' });
  if (a.locked) base.push({ icon: '🔒', color: T.danger, title: 'アカウントロック', body: 'ログイン失敗 3 回 · 30 秒ロック → エスカレート', when: '04-22 18:00' });
  if (a.sid === 'S001') { // リュウ イヒ = demo seed (高3 B 18 = 060218)
    base.push(
      { icon: '✗', color: T.danger, title: '欠席', body: '晩点呼 · 未チェックイン · 減点 1.0', when: '04-20 19:35' },
      { icon: '⏰', color: T.late,   title: '遅刻', body: '晩点呼 · 19:34 チェックイン · 減点 0.5', when: '04-12 19:34' },
      { icon: '✗', color: T.danger, title: '欠席', body: '晩点呼 · 未チェックイン · 減点 1.0', when: '04-15 19:38' },
      { icon: '✗', color: T.danger, title: '欠席', body: '晩点呼 · 未チェックイン · 減点 1.0', when: '04-08 19:40' },
      { icon: '⏰', color: T.late,   title: '遅刻', body: '晩点呼 · 19:35 チェックイン · 減点 0.5', when: '04-05 19:35' },
      { icon: '📝', color: T.cobalt, title: '外泊申請 提出', body: '岡山市内 · 2026-04-22 09:15 出発 · 審査待ち', when: '04-21 14:22' },
      { icon: '🎵', color: T.info,   title: 'コミュニティ投稿', body: 'リクエスト曲「春日和 / Aimer」', when: '04-22 07:30' },
    );
  } else if (a.sid === 'S103') { // 田中 隼人
    base.push({ icon: '📝', color: T.cobalt, title: '外泊申請 提出', body: '岡山市内 · 2026-04-25 〜 04-27', when: '04-21 09:10' });
  }
  // newest first
  return base.sort((x, y) => y.when.localeCompare(x.when)).slice(0, 10);
}

window.AccountsPage = AccountsPage;
