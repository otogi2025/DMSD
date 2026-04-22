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
  { id: 't1', name: '田中 健一', dorm: 'men',   lastLoginMins: 12, initial: '田' },
  { id: 't2', name: '佐々木 陽一', dorm: 'men',   lastLoginMins: 240, initial: '佐' },
  { id: 't3', name: '鈴木 美咲', dorm: 'women', lastLoginMins: 38, initial: '鈴' },
  { id: 't4', name: '山田 花子', dorm: 'women', lastLoginMins: null, initial: '山' }, // 初回
];

// ⭐ Roster — 13 men (M101-M113) + 11 women (W102-W112)
// リュウ イヒ (S001, 男性寮 M101) = itsuki demo binding
// 2026-04-22 itsuki 決定：男子寮へ移動（demo で男寮担任視点で自分が見える）
window.ROSTER_MEN = [
  ['M101','S001','リュウ イヒ'],
  ['M102','S101','佐藤 健太'], ['M103','S102','高橋 翔'],
  ['M104','S103','渡辺 隼人'], ['M105','S104','中村 大樹'],
  ['M106','S105','吉田 蓮'],   ['M107','S106','山口 健'],
  ['M108','S107','松本 翔太'], ['M109','S108','斎藤 晴'],
  ['M110','S109','阿部 悠真'], ['M111','S110','木村 拓哉'],
  ['M112','S111','山崎 航'],   ['M113','S112','佐々木 颯'],
];
window.ROSTER_WOMEN = [
  ['W102','S002','田中 美咲'],
  ['W103','S003','山本 綾'],     ['W104','S004','小林 美優'],
  ['W105','S005','加藤 陽菜'],   ['W106','S006','山田 千夏'],
  ['W107','S007','井上 結衣'],   ['W108','S008','清水 花音'],
  ['W109','S009','林 美奈'],     ['W110','S010','池田 咲希'],
  ['W111','S011','橋本 紗羅'],   ['W112','S012','鈴木 涼'],
];
window.ROSTER_ALL = [...window.ROSTER_MEN.map(r => [...r, 'men']), ...window.ROSTER_WOMEN.map(r => [...r, 'women'])];

// ⭐ Accounts — iOS 設計 §3.2 と整合。番号 00 = リュウ イヒ（demo seed 本体、itsuki 本人）、01-23 = 他の寮生
// フィールド: no, sid（学籍番号）, name, birthday, gender, category, room, dorm,
//            email, phone, registeredAt, lastLoginAt, locked, failedLoginCount
window.ACCOUNTS = [
  { no: '00', sid: 'S001', name: 'リュウ イヒ', birthday: '2006-10-14', gender: 'female', category: '一般寮生', room: 'M101', dorm: 'men',   email: 'ryu.ihi@tomoshibi.local',   phone: '090-0000-0000', registeredAt: '2026-02-10', lastLoginAt: '2026-04-22 18:05', locked: false, failedLoginCount: 0 },
  { no: '01', sid: 'S101', name: '佐藤 健太', birthday: '2008-03-22', gender: 'male',   category: 'サッカー部', room: 'M102', dorm: 'men',   email: 'sato.kenta@tomoshibi.local', phone: '090-1234-5678', registeredAt: '2026-03-05', lastLoginAt: '2026-04-22 19:12', locked: false, failedLoginCount: 0 },
  { no: '02', sid: 'S102', name: '高橋 翔',   birthday: '2007-09-05', gender: 'male',   category: '一般寮生', room: 'M103', dorm: 'men',   email: 'takahashi.sho@tomoshibi.local', phone: '090-9876-5432', registeredAt: '2026-03-05', lastLoginAt: '2026-04-22 18:30', locked: false, failedLoginCount: 0 },
  { no: '03', sid: 'S103', name: '渡辺 隼人', birthday: '2008-01-15', gender: 'male',   category: 'サッカー部', room: 'M104', dorm: 'men',   email: 'watanabe.h@tomoshibi.local',   phone: '090-2345-6789', registeredAt: '2026-03-07', lastLoginAt: '2026-04-21 20:10', locked: false, failedLoginCount: 0 },
  { no: '04', sid: 'S104', name: '中村 大樹', birthday: '2007-11-28', gender: 'male',   category: '一般寮生', room: 'M105', dorm: 'men',   email: 'nakamura.t@tomoshibi.local',   phone: '090-3456-7890', registeredAt: '2026-03-07', lastLoginAt: '2026-04-22 17:45', locked: false, failedLoginCount: 0 },
  { no: '05', sid: 'S105', name: '吉田 蓮',   birthday: '2008-05-03', gender: 'male',   category: 'サッカー部', room: 'M106', dorm: 'men',   email: 'yoshida.ren@tomoshibi.local',  phone: '090-4567-8901', registeredAt: '2026-03-08', lastLoginAt: '2026-04-22 18:00', locked: false, failedLoginCount: 1 },
  { no: '06', sid: 'S106', name: '山口 健',   birthday: '2008-07-19', gender: 'male',   category: '一般寮生', room: 'M107', dorm: 'men',   email: 'yamaguchi.k@tomoshibi.local',  phone: '090-5678-9012', registeredAt: '2026-03-10', lastLoginAt: '2026-04-20 22:15', locked: false, failedLoginCount: 0 },
  { no: '07', sid: 'S107', name: '松本 翔太', birthday: '2007-12-02', gender: 'male',   category: '一般寮生', room: 'M108', dorm: 'men',   email: 'matsumoto.s@tomoshibi.local',  phone: '090-6789-0123', registeredAt: '2026-03-10', lastLoginAt: '2026-04-22 19:30', locked: false, failedLoginCount: 0 },
  { no: '08', sid: 'S108', name: '斎藤 晴',   birthday: '2008-02-11', gender: 'male',   category: 'サッカー部', room: 'M109', dorm: 'men',   email: 'saito.haru@tomoshibi.local',   phone: '090-7890-1234', registeredAt: '2026-03-12', lastLoginAt: '2026-04-22 19:00', locked: true,  failedLoginCount: 3 },
  { no: '09', sid: 'S109', name: '阿部 悠真', birthday: '2007-10-08', gender: 'male',   category: '一般寮生', room: 'M110', dorm: 'men',   email: 'abe.yuma@tomoshibi.local',     phone: '090-8901-2345', registeredAt: '2026-03-12', lastLoginAt: '2026-04-22 17:00', locked: false, failedLoginCount: 0 },
  { no: '10', sid: 'S110', name: '木村 拓哉', birthday: '2008-04-17', gender: 'male',   category: '一般寮生', room: 'M111', dorm: 'men',   email: 'kimura.t@tomoshibi.local',     phone: '090-9012-3456', registeredAt: '2026-03-15', lastLoginAt: '2026-04-22 18:20', locked: false, failedLoginCount: 0 },
  { no: '11', sid: 'S111', name: '山崎 航',   birthday: '2008-06-25', gender: 'male',   category: 'サッカー部', room: 'M112', dorm: 'men',   email: 'yamazaki.w@tomoshibi.local',   phone: '090-0123-4567', registeredAt: '2026-03-15', lastLoginAt: '2026-04-22 18:40', locked: false, failedLoginCount: 0 },
  { no: '12', sid: 'S112', name: '佐々木 颯', birthday: '2007-08-30', gender: 'male',   category: '一般寮生', room: 'M113', dorm: 'men',   email: 'sasaki.hayate@tomoshibi.local', phone: '090-1111-2222', registeredAt: '2026-03-16', lastLoginAt: '2026-04-22 19:05', locked: false, failedLoginCount: 0 },
  { no: '13', sid: 'S002', name: '田中 美咲', birthday: '2007-05-14', gender: 'female', category: '一般寮生', room: 'W102', dorm: 'women', email: 'tanaka.misaki@tomoshibi.local', phone: '080-2222-3333', registeredAt: '2026-03-05', lastLoginAt: '2026-04-22 18:12', locked: false, failedLoginCount: 0 },
  { no: '14', sid: 'S003', name: '山本 綾',   birthday: '2007-09-21', gender: 'female', category: '一般寮生', room: 'W103', dorm: 'women', email: 'yamamoto.aya@tomoshibi.local',  phone: '080-3333-4444', registeredAt: '2026-03-06', lastLoginAt: '2026-04-22 17:50', locked: false, failedLoginCount: 0 },
  { no: '15', sid: 'S004', name: '小林 美優', birthday: '2008-01-04', gender: 'female', category: '一般寮生', room: 'W104', dorm: 'women', email: 'kobayashi.m@tomoshibi.local',   phone: '080-4444-5555', registeredAt: '2026-03-08', lastLoginAt: '2026-04-22 19:20', locked: false, failedLoginCount: 0 },
  { no: '16', sid: 'S005', name: '加藤 陽菜', birthday: '2008-03-11', gender: 'female', category: '一般寮生', room: 'W105', dorm: 'women', email: 'kato.hina@tomoshibi.local',     phone: '080-5555-6666', registeredAt: '2026-03-08', lastLoginAt: '2026-04-21 21:00', locked: false, failedLoginCount: 0 },
  { no: '17', sid: 'S006', name: '山田 千夏', birthday: '2007-07-07', gender: 'female', category: '一般寮生', room: 'W106', dorm: 'women', email: 'yamada.chinatsu@tomoshibi.local', phone: '080-6666-7777', registeredAt: '2026-03-10', lastLoginAt: '2026-04-22 18:00', locked: false, failedLoginCount: 0 },
  { no: '18', sid: 'S007', name: '井上 結衣', birthday: '2008-05-19', gender: 'female', category: '一般寮生', room: 'W107', dorm: 'women', email: 'inoue.yui@tomoshibi.local',     phone: '080-7777-8888', registeredAt: '2026-03-11', lastLoginAt: '2026-04-22 19:45', locked: false, failedLoginCount: 2 },
  { no: '19', sid: 'S008', name: '清水 花音', birthday: '2008-08-02', gender: 'female', category: '一般寮生', room: 'W108', dorm: 'women', email: 'shimizu.kanon@tomoshibi.local',  phone: '080-8888-9999', registeredAt: '2026-03-13', lastLoginAt: '2026-04-22 18:35', locked: false, failedLoginCount: 0 },
  { no: '20', sid: 'S009', name: '林 美奈',   birthday: '2007-11-16', gender: 'female', category: '一般寮生', room: 'W109', dorm: 'women', email: 'hayashi.mina@tomoshibi.local',  phone: '080-9999-0000', registeredAt: '2026-03-13', lastLoginAt: '2026-04-20 23:30', locked: false, failedLoginCount: 0 },
  { no: '21', sid: 'S010', name: '池田 咲希', birthday: '2008-02-28', gender: 'female', category: '一般寮生', room: 'W110', dorm: 'women', email: 'ikeda.saki@tomoshibi.local',    phone: '080-0000-1111', registeredAt: '2026-03-15', lastLoginAt: '2026-04-22 18:50', locked: false, failedLoginCount: 0 },
  { no: '22', sid: 'S011', name: '橋本 紗羅', birthday: '2007-12-23', gender: 'female', category: '一般寮生', room: 'W111', dorm: 'women', email: 'hashimoto.sara@tomoshibi.local', phone: '080-1111-2223', registeredAt: '2026-03-15', lastLoginAt: '2026-04-22 17:35', locked: false, failedLoginCount: 0 },
  { no: '23', sid: 'S012', name: '鈴木 涼',   birthday: '2008-06-08', gender: 'female', category: '一般寮生', room: 'W112', dorm: 'women', email: 'suzuki.ryo@tomoshibi.local',    phone: '080-2222-3334', registeredAt: '2026-03-16', lastLoginAt: '2026-04-22 19:10', locked: false, failedLoginCount: 0 },
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
