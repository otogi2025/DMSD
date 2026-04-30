// Tomoshibi (灯火) Round 3 theme — extends Ryo tokens from Round 2.
// Adds: late state, timing constants, 12M/12F roster, shared app constants.

window.RYO = {
  paper: '#f4f5f7', surface: '#ffffff', surfaceAlt: '#f9fafb',
  line: '#e3e5eb', lineStrong: '#cdd0d8',
  ink: '#14171f', ink2: '#3a404d', ink3: '#6a6f7d', muted: '#9ea3ae',
  cobalt: '#2b4d8c', cobaltDeep: '#1c3567', cobaltSoft: '#e5ebf5',
  // statuses
  ok: '#2f7a55', okSoft: '#dfefe5', okBorder: '#b7d7c4',
  late: '#b8871f', lateSoft: '#f6e8c4', lateBorder: '#e5c98a',   // ⭐ NEW
  danger: '#b33a3a', dangerSoft: '#f3dcdc', dangerBorder: '#e3b3b3',
  info: '#2b4d8c', infoSoft: '#dde4f1', infoBorder: '#bdcae1',
  warn: '#a56b1e', warnSoft: '#f2e3cb', warnBorder: '#e6c98f',
  graySoft: '#ebedf1', grayBorder: '#d5d8df',
  // women-dorm soft accent (for dorm badge)
  femaleAccent: '#a4478e', femaleSoft: '#f3e2ee',
  maleAccent: '#3a6a8f', maleSoft: '#dfeaf3',
  font: '"Noto Sans JP","Hiragino Kaku Gothic ProN",-apple-system,BlinkMacSystemFont,sans-serif',
  mono: '"JetBrains Mono","SF Mono",ui-monospace,Menlo,monospace',
  shadow1: '0 1px 2px rgba(20,23,31,.04)',
  shadow2: '0 4px 16px rgba(20,23,31,.08), 0 1px 2px rgba(20,23,31,.04)',
  shadowModal: '0 24px 64px rgba(20,23,31,.28), 0 2px 8px rgba(20,23,31,.12)',
};

// ⭐ App constants
// DEMO: 動作確認用に短縮する場合はここを変える
window.TIMEOUT_MS = 30 * 60 * 1000;      // 30 min — auto return to /login/select-teacher
window.TIMEOUT_WARN_MS = 25 * 60 * 1000; // 25 min — show "あと 5 分" toast
window.LATE_THRESHOLD_SEC = 180;         // 3 min — late auto transition
window.SHARED_PASSWORD = '12345678';
window.APP_VERSION = 'v0.1.0-demo';

// ⭐ Teachers (initial)
window.TEACHERS = [
  { id: 't1', name: '新股',   dorm: 'men',   lastLoginMins: 12,  initial: '新' },
  { id: 't2', name: '小林',   dorm: 'men',   lastLoginMins: 240, initial: '小' },
  { id: 't5', name: '難波',   dorm: 'men',   lastLoginMins: null, initial: '難' },
  { id: 't3', name: '鈴木 美咲', dorm: 'women', lastLoginMins: 38,  initial: '鈴' },
  { id: 't4', name: '山田 花子', dorm: 'women', lastLoginMins: null, initial: '山' }, // 初回
];

// ⭐ Roster — 4 men + 3 women（2026-04-24 デモ用に最小構成へ削減）
// リュウ イヒ (S001, 男性寮 M101) = itsuki demo binding
// 2026-04-22 itsuki 決定：男子寮へ移動（demo で男寮担任視点で自分が見える）
// 2026-04-24 itsuki 削減：男寮 リュウ/田中 隼人/ゴテンウ/ヨウシエン、女寮 リシンさん/ソンキゼン/ゴキンウ のみ残す
window.ROSTER_MEN = [
  ['M101','S001','リュウ イヒ'],
  ['M104','S103','田中 隼人'],
  ['M114','S113','ゴテンウ'],
  ['M115','S114','ヨウシエン'],
];
window.ROSTER_WOMEN = [
  ['W113','S013','リシンさん'],
  ['W114','S014','ソンキゼン'],
  ['W115','S015','ゴキンウ'],
];
window.ROSTER_ALL = [...window.ROSTER_MEN.map(r => [...r, 'men']), ...window.ROSTER_WOMEN.map(r => [...r, 'women'])];

// ⭐ Accounts — iOS 設計 §3.2 と整合。番号 00 = リュウ イヒ（demo seed 本体、itsuki 本人）、01-23 = 他の寮生
// フィールド: no, sid（学籍番号）, name, birthday, gender, category, room, dorm,
//            email, phone, registeredAt, lastLoginAt, locked, failedLoginCount
// 番号 6 桁 = 学年(2) + 組(2) + 番号(2)。学年: 中1=01〜高3=06、組: A=01 / B=02、番号: 01-99。
// 全員 高3（学年 06）、リュウ イヒ = 高3 B 18号 = 060218（itsuki 本人, demo seed · iOS SEED と一致）。
window.DEMO_SEED_NO = '060218';
window.ACCOUNTS = [
  { no: '060218', sid: 'S001', name: 'リュウ イヒ', birthday: '2006-10-14', gender: 'male',   category: '一般寮生', room: 'M101', dorm: 'men',   email: 'ryu.ihi@tomoshibi.local',   phone: '090-0000-0000', registeredAt: '2026-02-10', lastLoginAt: '2026-04-22 18:05', locked: false, failedLoginCount: 0 },
  { no: '060103', sid: 'S103', name: '田中 隼人', birthday: '2008-01-15', gender: 'male',   category: 'サッカー部', room: 'M104', dorm: 'men',   email: 'tanaka.hayato@tomoshibi.local', phone: '090-2345-6789', registeredAt: '2026-03-07', lastLoginAt: '2026-04-21 20:10', locked: false, failedLoginCount: 0 },
  { no: '060112', sid: 'S113', name: 'ゴテンウ',  birthday: '2007-04-18', gender: 'male',   category: '一般寮生', room: 'M114', dorm: 'men',   email: 'go.tenu@tomoshibi.local',       phone: '090-3333-4444', registeredAt: '2026-04-10', lastLoginAt: '2026-04-23 19:30', locked: false, failedLoginCount: 0 },
  { no: '060225', sid: 'S114', name: 'ヨウシエン', birthday: '2008-08-25', gender: 'male',   category: '一般寮生', room: 'M115', dorm: 'men',   email: 'you.shien@tomoshibi.local',     phone: '090-5555-6666', registeredAt: '2026-04-10', lastLoginAt: '2026-04-23 20:15', locked: false, failedLoginCount: 0 },
  { no: '060108', sid: 'S013', name: 'リシンさん', birthday: '2006-11-30', gender: 'female', category: '一般寮生', room: 'W113', dorm: 'women', email: 'ri.shinsan@tomoshibi.local',    phone: '080-3333-4445', registeredAt: '2026-04-10', lastLoginAt: '2026-04-23 19:00', locked: false, failedLoginCount: 0 },
  { no: '060214', sid: 'S014', name: 'ソンキゼン', birthday: '2009-02-07', gender: 'female', category: '一般寮生', room: 'W114', dorm: 'women', email: 'son.kizen@tomoshibi.local',     phone: '080-5555-6667', registeredAt: '2026-04-10', lastLoginAt: '2026-04-23 18:40', locked: false, failedLoginCount: 0 },
  { no: '060121', sid: 'S015', name: 'ゴキンウ',   birthday: '2007-06-13', gender: 'female', category: '一般寮生', room: 'W115', dorm: 'women', email: 'go.kinu@tomoshibi.local',       phone: '080-7777-8889', registeredAt: '2026-04-10', lastLoginAt: '2026-04-23 21:05', locked: false, failedLoginCount: 0 },
];

// Helpers
window.dormLabel = (d) => d === 'men' ? '男性寮' : '女性寮';
window.seedStudents = (dorm) => {
  const src = dorm === 'men' ? window.ROSTER_MEN : window.ROSTER_WOMEN;
  return src.map(([room, id, name]) => ({
    key: id, id, room, name, dorm, status: 'unknown',
    checkinAt: null, health: null, pending: null, override: null, exemptReason: null,
  }));
};
