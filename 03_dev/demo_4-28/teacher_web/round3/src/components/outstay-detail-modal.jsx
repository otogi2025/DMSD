// Outstay application detail modal — digitised from 02_gaihaku_form_reference.jpeg.

function OutstayDetailModal({ app, onClose, onAction }) {
  const T = window.RYO;
  const [confirm, setConfirm] = React.useState(null);

  const Section = ({ title, children }) => (
    <div style={{ marginBottom: 18 }}>
      <div style={{ fontSize: 10, color: T.ink3, letterSpacing: 2, fontWeight: 700, marginBottom: 8, paddingBottom: 4, borderBottom: `1px solid ${T.line}` }}>§ {title}</div>
      {children}
    </div>
  );
  const F = ({ label, children, mono }) => (
    <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: 10, fontSize: 13, padding: '5px 0' }}>
      <div style={{ color: T.ink3, fontSize: 12 }}>{label}</div>
      <div style={{ color: T.ink, fontFamily: mono ? T.mono : 'inherit' }}>{children}</div>
    </div>
  );

  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(20,23,31,.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, fontFamily: T.font, padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ width: 820, maxHeight: '94vh', overflow: 'auto', background: T.surface, borderRadius: 14, boxShadow: T.shadowModal, color: T.ink }}>
        <div style={{ padding: '22px 28px 18px', borderBottom: `1px solid ${T.line}`, background: T.surfaceAlt, borderRadius: '14px 14px 0 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 700 }}>申請 &gt; 外泊 &gt; {app.applicant} の申請</div>
            <div style={{ flex: 1 }} />
            <window.StateBadge s={app.state} />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginTop: 8 }}>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3 }}>外泊許可願</div>
            <div style={{ fontSize: 12, fontFamily: T.mono, color: T.ink3 }}>{app.id} · 提出 {app.submitted}</div>
          </div>
        </div>

        <div style={{ padding: '22px 28px' }}>
          <Section title="申請者本人">
            <F label="氏名">{app.applicant}</F>
            <F label="学年・組">{app.grade}</F>
            <F label="部屋">{app.room} · {window.dormLabel(app.dorm)}</F>
            <F label="本人連絡先" mono>{app.phone}</F>
          </Section>

          <Section title="同行者">
            <F label="氏名">{app.companion.name}</F>
            <F label="連絡先" mono>{app.companion.phone}</F>
          </Section>

          <Section title="外泊日時">
            <F label="出発予定日時" mono>{app.depart}</F>
            <F label="帰舎予定日時" mono>{app.return_}</F>
          </Section>

          <Section title="移動手段">
            <F label="行き">{app.methodGo}{app.flightNo && ` (${app.flightNo})`}</F>
            <F label="帰り">{app.methodBack}</F>
            {app.specialTransport.on && <F label="寮生特別運行">該当 · {app.specialTransport.from} 〜 {app.specialTransport.to}</F>}
          </Section>

          <Section title="宿泊先">
            <F label="分類">{app.lodging.type}</F>
            <F label="名称">{app.lodging.name}</F>
            <F label="住所">{app.lodging.address}</F>
            <F label="行先都市">{app.lodging.city}</F>
          </Section>

          <Section title="食事">
            <F label="朝 / 昼 / 夕" mono>{app.meals.breakfast} / {app.meals.lunch} / {app.meals.dinner}</F>
            <F label="自分で記入可">{app.meals.selfInput ? '✓ 許可（食数の自由記入可）' : '—'}</F>
          </Section>

          <Section title="外泊の理由">
            <div style={{ background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 8, padding: '10px 12px', fontSize: 13, lineHeight: 1.7 }}>{app.reason}</div>
          </Section>

          {app.note && (
            <Section title="備考">
              <div style={{ background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 8, padding: '10px 12px', fontSize: 13, lineHeight: 1.7 }}>{app.note}</div>
            </Section>
          )}

          <Section title="保護者許可">
            <F label="確認">{app.parentOk.confirmed ? '✓ 確認済' : '未確認'}</F>
            <F label="保護者電話" mono>{app.parentOk.phone}</F>
          </Section>

          <Section title="承認ワークフロー">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
              {app.approvals.map((a, i) => {
                const map = { pending: [T.ink3, T.surfaceAlt, T.line, '—'], approved: [T.ok, T.okSoft, T.okBorder, '✓ 承認済'], rejected: [T.danger, T.dangerSoft, T.dangerBorder, '✗ 却下'], question: [T.warn, T.warnSoft, T.warnBorder, '? 質問あり'] }[a.state];
                return (
                  <div key={i} style={{ padding: '10px 12px', background: map[1], border: `1px solid ${map[2]}`, borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: 10, color: T.ink3, fontWeight: 600, letterSpacing: 1 }}>{a.role}</div>
                    <div style={{ fontSize: 13, fontWeight: 600, marginTop: 2 }}>{a.name}</div>
                    <div style={{ fontSize: 11, color: map[0], fontWeight: 700, marginTop: 4 }}>{map[3]}</div>
                  </div>
                );
              })}
            </div>
          </Section>
        </div>

        <div style={{ padding: '14px 28px', borderTop: `1px solid ${T.line}`, background: T.surfaceAlt, display: 'flex', gap: 8, borderRadius: '0 0 14px 14px' }}>
          <button onClick={onClose} style={{ padding: '10px 18px', background: 'transparent', color: T.ink, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>閉じる</button>
          <div style={{ flex: 1 }} />
          <button onClick={() => setConfirm({ action: 'question', label: '質問あり（保留）' })} style={{ padding: '10px 18px', background: 'transparent', color: T.warn, border: `1px solid ${T.warnBorder}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>質問あり（保留）</button>
          <button onClick={() => setConfirm({ action: 'rejected', label: '却下' })} style={{ padding: '10px 18px', background: 'transparent', color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>却下</button>
          <button onClick={() => setConfirm({ action: 'approved', label: '承認' })} style={{ padding: '10px 20px', background: T.cobalt, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>承認</button>
        </div>
      </div>

      {confirm && (
        <window.ConfirmModal title={`${app.applicant} の外泊申請を${confirm.label}しますか？`}
          desc="承認・却下・保留いずれの場合も、学生には iOS App に push 通知が送信されます。"
          danger={confirm.action === 'rejected'} confirmLabel={confirm.label}
          onCancel={() => setConfirm(null)}
          onConfirm={() => { onAction(confirm.action); setConfirm(null); }} />
      )}
    </div>
  );
}

window.OutstayDetailModal = OutstayDetailModal;
