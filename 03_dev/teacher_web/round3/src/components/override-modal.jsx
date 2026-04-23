// Override modal — extended with pending leave request / health report / adjustment history.

function OverrideModal({ student, onClose, onSave }) {
  const T = window.RYO;
  const [status, setStatus] = React.useState(student.status === 'unknown' ? 'ok' : student.status);
  const [reason, setReason] = React.useState('');
  const [approveLeave, setApproveLeave] = React.useState(false);
  const needsReason = status !== student.status || student.pending;
  const canSave = !needsReason || reason.trim().length > 0;

  const statuses = [
    { k: 'ok',      label: '時間内', color: T.ok,     soft: T.okSoft,     hint: '対面確認済み' },
    { k: 'late',    label: '遅刻',   color: T.late,   soft: T.lateSoft,   hint: '閾値超で入寮' },
    { k: 'absent',  label: '欠席',   color: T.danger, soft: T.dangerSoft, hint: '未確認のまま終了' },
    { k: 'exempt',  label: '免除',   color: T.info,   soft: T.infoSoft,   hint: '本日は点呼対象外' },
  ];

  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(20,23,31,.48)', backdropFilter: 'blur(2px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, fontFamily: T.font, padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ width: 620, maxHeight: '92vh', overflow: 'auto', background: T.surface, borderRadius: 14, boxShadow: T.shadowModal, color: T.ink }}>
        <div style={{ padding: '20px 24px 16px', borderBottom: `1px solid ${T.line}` }}>
          <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>手動調整</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 4 }}>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3 }}>{student.name}</div>
            <div style={{ fontSize: 12, fontFamily: T.mono, color: T.ink3 }}>{student.room} · {student.id}</div>
          </div>
        </div>

        <div style={{ padding: '18px 24px' }}>
          {/* Pending leave request expand */}
          {student.pending && (
            <div style={{ padding: 14, background: T.warnSoft, border: `1px solid ${T.warnBorder}`, borderRadius: 10, marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: T.warn, fontWeight: 700, letterSpacing: 1, marginBottom: 6 }}>提出された欠席届</div>
              <div style={{ fontSize: 13, color: T.ink, marginBottom: 8 }}>{student.pending.reason}</div>
              <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, marginBottom: 10 }}>提出: {student.pending.submittedAt || '19:22'}</div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => setApproveLeave(true)} style={{ padding: '7px 14px', background: approveLeave ? T.ok : T.surface, color: approveLeave ? '#fff' : T.ok, border: `1px solid ${T.okBorder}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>{approveLeave ? '✓ 承認予定' : '承認'}</button>
                <button onClick={() => setApproveLeave(false)} style={{ padding: '7px 14px', background: 'transparent', color: T.danger, border: `1px solid ${T.dangerBorder}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>却下</button>
              </div>
              <div style={{ fontSize: 10, color: T.ink3, marginTop: 8 }}>※「保存して反映」を押すと承認・却下が確定し、学生に push 通知が送信されます。</div>
            </div>
          )}

          {/* Health expand */}
          {student.health && (
            <div style={{ padding: 14, background: T.dangerSoft, border: `1px solid ${T.dangerBorder}`, borderRadius: 10, marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: T.danger, fontWeight: 700, letterSpacing: 1, marginBottom: 6 }}>体調報告</div>
              <div style={{ fontSize: 13, color: T.ink, marginBottom: 10 }}>{student.health}</div>
              <div style={{ fontSize: 10, color: T.ink3 }}>※「保存して反映」時に既読として記録されます</div>
            </div>
          )}

          {/* Override history */}
          {student.override && (
            <div style={{ padding: 12, background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 10, marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: T.ink3, fontWeight: 700, letterSpacing: 1, marginBottom: 6 }}>調整履歴</div>
              <div style={{ fontSize: 12, color: T.ink2, fontFamily: T.mono }}>{student.override.by} · 19:35</div>
              <div style={{ fontSize: 12, color: T.ink }}>{student.override.reason}</div>
            </div>
          )}

          <div style={{ fontSize: 11, color: T.ink2, letterSpacing: 1.5, fontWeight: 600, marginBottom: 10, textTransform: 'uppercase' }}>状態を選択</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 18 }}>
            {statuses.map(o => (
              <button key={o.k} onClick={() => setStatus(o.k)} style={{
                textAlign: 'left', padding: '11px 14px', borderRadius: 10, cursor: 'pointer',
                background: status === o.k ? o.soft : T.surface,
                border: status === o.k ? `2px solid ${o.color}` : `1px solid ${T.line}`,
                color: T.ink, fontFamily: 'inherit',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ width: 14, height: 14, borderRadius: 8, border: `2px solid ${status === o.k ? o.color : T.lineStrong}`, background: status === o.k ? o.color : 'transparent', boxShadow: status === o.k ? `inset 0 0 0 3px ${T.surface}` : 'none' }} />
                  <span style={{ fontSize: 14, fontWeight: 600, color: status === o.k ? o.color : T.ink }}>{o.label}</span>
                </div>
                <div style={{ fontSize: 11, color: T.ink3, marginTop: 3, marginLeft: 24 }}>{o.hint}</div>
              </button>
            ))}
          </div>

          <div style={{ fontSize: 11, color: T.ink2, letterSpacing: 1.5, fontWeight: 600, marginBottom: 6, textTransform: 'uppercase' }}>
            調整理由 {needsReason && <span style={{ color: T.danger }}>※必須</span>}
          </div>
          <textarea value={reason} onChange={e => setReason(e.target.value)} rows={3}
            placeholder="例：未携帯・対面で確認済み / 保健室で休養中"
            style={{ width: '100%', padding: '10px 12px', background: T.surface, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, color: T.ink, outline: 'none', boxSizing: 'border-box', resize: 'vertical' }} />
          <div style={{ fontSize: 11, color: T.ink3, marginTop: 6, fontFamily: T.mono }}>記録は監査ログに残ります</div>
        </div>

        <div style={{ padding: '14px 24px', borderTop: `1px solid ${T.line}`, background: T.surfaceAlt, display: 'flex', justifyContent: 'flex-end', gap: 8, borderRadius: '0 0 14px 14px' }}>
          <button onClick={onClose} style={{ padding: '9px 18px', background: 'transparent', color: T.ink, border: `1px solid ${T.lineStrong}`, borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>キャンセル</button>
          <button disabled={!canSave} onClick={() => onSave({ status, reason, approveLeave })} style={{ padding: '9px 20px', background: canSave ? T.cobalt : T.lineStrong, color: '#fff', border: 'none', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: canSave ? 'pointer' : 'not-allowed' }}>保存して反映</button>
        </div>
      </div>
    </div>
  );
}

window.OverrideModal = OverrideModal;
