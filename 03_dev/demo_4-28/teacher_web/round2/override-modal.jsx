// Override modal — opens on seat click. 4 radio + reason (required for non-ok).

function OverrideModal({ student, onClose, onSave }) {
  const T = window.RYO;
  const [status, setStatus] = React.useState(student.status === 'unknown' ? 'ok' : student.status);
  const [reason, setReason] = React.useState(student.overrideReason || '');
  const [approveLeave, setApproveLeave] = React.useState(false);
  const needsReason = status !== student.status || student.pending;
  const canSave = !needsReason || reason.trim().length > 0;

  const statuses = [
    { k: 'ok',      label: '時間内', color: T.ok,     soft: T.okSoft,     bd: T.okBorder,     hint: '対面確認済み' },
    { k: 'absent',  label: '欠席',   color: T.danger, soft: T.dangerSoft, bd: T.dangerBorder, hint: '点呼終了時点で未確認' },
    { k: 'exempt',  label: '免除',   color: T.info,   soft: T.infoSoft,   bd: T.infoBorder,   hint: '本日は点呼対象外' },
    { k: 'unknown', label: '未点呼', color: T.ink3,   soft: T.graySoft,   bd: T.grayBorder,   hint: '判定を保留' },
  ];

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, background: 'rgba(20,23,31,.48)', backdropFilter: 'blur(2px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, fontFamily: T.font,
      padding: 20,
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        width: 560, maxHeight: '90vh', overflow: 'auto',
        background: T.surface, borderRadius: 14, boxShadow: T.shadowModal, color: T.ink,
      }}>
        {/* Header */}
        <div style={{ padding: '20px 24px 16px', borderBottom: `1px solid ${T.line}` }}>
          <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>手動調整</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 4 }}>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3 }}>{student.name}</div>
            <div style={{ fontSize: 12, fontFamily: T.mono, color: T.ink3 }}>{student.room}号室 · {student.id}</div>
          </div>
          {(student.health || student.pending) && (
            <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
              {student.health && (
                <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 999, background: T.dangerSoft, color: T.danger, fontWeight: 600, border: `1px solid ${T.dangerBorder}` }}>＋ 体調報告：{student.health}</span>
              )}
              {student.pending && (
                <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 999, background: T.warnSoft, color: T.warn, fontWeight: 600, border: `1px solid ${T.warn}33` }}>? 欠席届 審査中</span>
              )}
            </div>
          )}
        </div>

        {/* Body */}
        <div style={{ padding: '20px 24px' }}>
          <div style={{ fontSize: 11, color: T.ink2, letterSpacing: 1.5, fontWeight: 600, marginBottom: 10, textTransform: 'uppercase' }}>状態を選択</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 20 }}>
            {statuses.map(o => (
              <button key={o.k} onClick={() => setStatus(o.k)} style={{
                textAlign: 'left', padding: '12px 14px', borderRadius: 10, cursor: 'pointer',
                background: status === o.k ? o.soft : T.surface,
                border: status === o.k ? `2px solid ${o.color}` : `1px solid ${T.line}`,
                color: T.ink, fontFamily: 'inherit', position: 'relative',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{
                    width: 16, height: 16, borderRadius: 10, border: `2px solid ${status === o.k ? o.color : T.lineStrong}`,
                    background: status === o.k ? o.color : 'transparent', display: 'inline-block', flexShrink: 0,
                    boxShadow: status === o.k ? `inset 0 0 0 3px ${T.surface}` : 'none',
                  }} />
                  <span style={{ fontSize: 14, fontWeight: 600, color: status === o.k ? o.color : T.ink }}>{o.label}</span>
                </div>
                <div style={{ fontSize: 11, color: T.ink3, marginTop: 4, marginLeft: 26 }}>{o.hint}</div>
              </button>
            ))}
          </div>

          {student.pending && (
            <label style={{
              display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 12px',
              background: T.warnSoft, border: `1px solid ${T.warn}44`, borderRadius: 8, marginBottom: 16, cursor: 'pointer',
            }}>
              <input type="checkbox" checked={approveLeave} onChange={(e) => setApproveLeave(e.target.checked)} style={{ marginTop: 3 }} />
              <div style={{ fontSize: 12 }}>
                <div style={{ fontWeight: 600, color: T.warn }}>欠席届を同時に承認する</div>
                <div style={{ color: T.ink2, marginTop: 2 }}>学生が提出した免除申請を承認し、状態を「免除」として確定します。</div>
              </div>
            </label>
          )}

          <div style={{ fontSize: 11, color: T.ink2, letterSpacing: 1.5, fontWeight: 600, marginBottom: 6, textTransform: 'uppercase' }}>
            調整理由 {needsReason && <span style={{ color: T.danger }}>※必須</span>}
          </div>
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={3}
            placeholder="例：未携帯・対面で確認済み / 保健室で休養中 / 部活遠征で帰寮遅延を事前連絡済み"
            style={{
              width: '100%', padding: '10px 12px', background: T.surface, border: `1px solid ${T.lineStrong}`,
              borderRadius: 8, fontFamily: 'inherit', fontSize: 13, color: T.ink, outline: 'none', boxSizing: 'border-box', resize: 'vertical',
            }} />
          <div style={{ fontSize: 11, color: T.ink3, marginTop: 6, fontFamily: T.mono }}>記録は監査ログに残ります · 舎監：田中 先生</div>
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 24px', borderTop: `1px solid ${T.line}`, background: T.surfaceAlt, display: 'flex', justifyContent: 'flex-end', gap: 8, borderRadius: '0 0 14px 14px' }}>
          <button onClick={onClose} style={{
            padding: '9px 18px', background: 'transparent', color: T.ink, border: `1px solid ${T.lineStrong}`,
            borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer',
          }}>キャンセル</button>
          <button disabled={!canSave} onClick={() => onSave({ status, reason, approveLeave })} style={{
            padding: '9px 20px', background: canSave ? T.cobalt : T.lineStrong, color: '#fff', border: 'none',
            borderRadius: 8, fontFamily: 'inherit', fontSize: 13, fontWeight: 700, cursor: canSave ? 'pointer' : 'not-allowed',
          }}>保存して反映</button>
        </div>
      </div>
    </div>
  );
}

window.OverrideModal = OverrideModal;
