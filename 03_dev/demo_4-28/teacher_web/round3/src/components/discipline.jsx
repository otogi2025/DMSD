// /discipline — rules card + rankings + cleaning/ban lists + warnings + future-alert preview.

function DisciplinePage({ teacher, onNav }) {
  const T = window.RYO;
  const dorm = teacher.dorm;
  const roster = dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;

  // Mock demerit data per student (index 0 = リュウ イヒ in 男子寮 — 清掃罰則ライン超え)
  const data = roster.map(([room, id, name], i) => {
    const late = [5,1,2,0,3,0,1,6,0,2,1,0][i % 12];
    const absent = [2,0,0,0,1,0,0,1,0,0,0,0][i % 12];
    const total = late * 0.5 + absent * 1.0;
    return { room, id, name, late, absent, total };
  }).sort((a, b) => b.total - a.total);

  const cleaningList = data.filter(d => d.total >= 4);
  const banList = data.filter(d => d.total >= 8);
  const warnList = data.filter(d => d.total >= 3 && d.total < 4);

  return (
    <div style={{ padding: '28px 32px 48px', maxWidth: 1280 }}>
      <div style={{ fontSize: 11, color: T.ink3, letterSpacing: 2, fontWeight: 600 }}>規律・処分</div>
      <h1 style={{ fontSize: 24, fontWeight: 700, margin: '4px 0 6px', letterSpacing: -0.3 }}>規律・処分</h1>
      <div style={{ color: T.ink2, fontSize: 13, marginBottom: 22 }}>{window.dormLabel(dorm)} · 2026 年 4 月</div>

      {/* Rules card */}
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, padding: '18px 22px', boxShadow: T.shadow1, marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <div style={{ fontSize: 14, fontWeight: 700 }}>現在の減点ルール（運用前、先生と調整可）</div>
          <div style={{ flex: 1 }} />
          <button style={{ padding: '5px 12px', background: 'transparent', color: T.ink3, border: `1px solid ${T.lineStrong}`, borderRadius: 6, fontFamily: 'inherit', fontSize: 11, cursor: 'pointer' }}>値を変更 (管理者のみ)</button>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <RulePill label="遅刻" value="0.5 点" color={T.late} />
          <RulePill label="欠席" value="1.0 点" color={T.danger} />
          <RulePill label="清掃罰則 発動" value="月累計 ≥ 4 点" color={T.warn} />
          <RulePill label="外出禁止 発動" value="月累計 ≥ 8 点" color={T.danger} />
        </div>
      </div>

      <SectionH n="1" title="今月全員ランキング" />
      <div style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', boxShadow: T.shadow1, marginBottom: 24 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '60px 1fr 90px 90px 90px 90px 120px 130px', background: T.surfaceAlt, fontSize: 11, color: T.ink2, fontWeight: 600, letterSpacing: 1, borderBottom: `1px solid ${T.line}` }}>
          {['順位', '学生', '部屋', '減点合計', '遅刻回数', '欠席回数', '清掃まで残り', '外出禁止まで残り'].map(h => <div key={h} style={{ padding: '10px 12px' }}>{h}</div>)}
        </div>
        {data.map((d, i) => (
          <div key={d.id} style={{ display: 'grid', gridTemplateColumns: '60px 1fr 90px 90px 90px 90px 120px 130px', borderTop: i > 0 ? `1px solid ${T.line}` : 'none', fontSize: 12.5, alignItems: 'center' }}>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: i < 3 ? T.danger : T.ink3, fontWeight: 700 }}>#{i + 1}</div>
            <div style={{ padding: '9px 12px', fontWeight: 600 }}>{d.name}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.ink3 }}>{d.room}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, fontWeight: 700, color: d.total >= 4 ? T.danger : d.total >= 3 ? T.warn : T.ink }}>{d.total.toFixed(1)}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.late }}>{d.late}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.danger }}>{d.absent}</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.ink3 }}>{Math.max(0, 4 - d.total).toFixed(1)} 点</div>
            <div style={{ padding: '9px 12px', fontFamily: T.mono, color: T.ink3 }}>{Math.max(0, 8 - d.total).toFixed(1)} 点</div>
          </div>
        ))}
      </div>

      <SectionH n="2" title="清掃罰則リスト (来月対象)" note={`${cleaningList.length} 名`} />
      <StudentCardRow list={cleaningList} color={T.warn} label="今月減点" empty="該当なし" />

      <SectionH n="3" title="外出禁止リスト (来月対象)" note={`${banList.length} 名`} />
      <StudentCardRow list={banList} color={T.danger} label="今月減点" empty="該当なし" />

      <SectionH n="4" title="警告リスト (閾値近接)" note={`${warnList.length} 名`} />
      <StudentCardRow list={warnList} color={T.warn} label="今月減点" empty="該当なし" />

      {/* Future alert preview */}
      <div style={{ marginTop: 30, background: T.surface, border: `1px dashed ${T.lineStrong}`, borderRadius: 12, padding: '18px 20px', opacity: 0.85 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: T.ink3 }}>自動アラート</div>
          <span style={{ fontSize: 10, fontWeight: 700, color: T.warn, background: T.warnSoft, padding: '2px 8px', borderRadius: 4, letterSpacing: 1 }}>開発中</span>
        </div>
        <div style={{ fontSize: 12, color: T.ink3, lineHeight: 1.7, marginBottom: 10 }}>
          将来、後端サーバーに常駐スクリプトを設置し、特定学生の遅刻・欠席が一定数に達した時点で自動的に宿監へアラート短評を生成する予定です。現 demo 版では手動確認のみ。
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {data.slice(0, 2).map((d, i) => (
            <div key={d.id} style={{ padding: '8px 12px', background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 6, fontSize: 12, color: T.ink3 }}>{d.name} · 今月遅刻 {d.late} 回 · {i === 0 ? '要面談' : '継続観察'}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RulePill({ label, value, color }) {
  const T = window.RYO;
  return (
    <div style={{ background: T.surfaceAlt, border: `1px solid ${T.line}`, borderRadius: 999, padding: '6px 14px', display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
      <span style={{ color: T.ink3 }}>{label}</span>
      <span style={{ fontFamily: window.RYO.mono, fontWeight: 700, color }}>{value}</span>
    </div>
  );
}

function SectionH({ n, title, note }) {
  const T = window.RYO;
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, margin: '6px 0 10px' }}>
      <span style={{ fontSize: 11, fontWeight: 700, color: T.ink3, letterSpacing: 1, fontFamily: T.mono }}>§{n}</span>
      <span style={{ fontSize: 15, fontWeight: 700 }}>{title}</span>
      {note && <span style={{ fontSize: 11, color: T.ink3 }}>{note}</span>}
    </div>
  );
}

function StudentCardRow({ list, color, label, empty }) {
  const T = window.RYO;
  if (!list.length) return <div style={{ padding: '14px 16px', background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, fontSize: 12, color: T.ink3, marginBottom: 18 }}>{empty}</div>;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 18 }}>
      {list.map(d => (
        <div key={d.id} style={{ background: T.surface, border: `1px solid ${T.line}`, borderRadius: 10, padding: '12px 14px', boxShadow: T.shadow1 }}>
          <div style={{ fontSize: 15, fontWeight: 700 }}>{d.name}</div>
          <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono, marginTop: 2 }}>{d.room} · {d.id}</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginTop: 8 }}>
            <span style={{ fontSize: 10, color: T.ink3 }}>{label}</span>
            <span style={{ fontSize: 18, fontWeight: 700, fontFamily: T.mono, color }}>{d.total.toFixed(1)}</span>
            <span style={{ fontSize: 10, color: T.ink3 }}>点</span>
          </div>
          <div style={{ fontSize: 10, color: T.ink3, marginTop: 4 }}>遅刻 {d.late} / 欠席 {d.absent}</div>
        </div>
      ))}
    </div>
  );
}

window.DisciplinePage = DisciplinePage;
