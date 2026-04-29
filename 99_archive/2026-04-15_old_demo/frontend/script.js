// ========================================
// 配置(演示前必改)
// ========================================
// 如果前端和后端在同一台 Mac 上跑, 用 'localhost'
// 如果要让 iPhone 通过 NFC 触发, 换成 Mac 的局域网 IP (例如 '192.168.1.5')
// 查询 Mac IP: 终端运行 `ifconfig | grep "inet "`
const MAC_IP = 'localhost';
const PORT = 8000;
// ========================================

const API_BASE = `http://${MAC_IP}:${PORT}`;
const POLL_INTERVAL_MS = 1000;

// 已经见过的 student_id（用来判断新刷卡事件，防止重复触发动画/语音）
const seenIds = new Set();

// 学生花名册（GET /students 拿到后缓存在这里）
let roster = [];

// DOM 快捷引用
const $grid = document.getElementById('room-grid');
const $connStatus = document.getElementById('conn-status');
const $attendance = document.getElementById('attendance');
const $apiBase = document.getElementById('api-base');
const $toastArea = document.getElementById('toast-area');
const $btnReset = document.getElementById('btn-reset');

// ========================================
// 页面启动入口
// ========================================
// 页面加载完成后：显示 API 地址，拉花名册，开始轮询，绑定按钮
async function init() {
  $apiBase.textContent = API_BASE;

  await loadRoster();

  // 绑定重置按钮
  $btnReset.addEventListener('click', resetAll);

  // 绑定两个模拟刷卡按钮（footer 里的 data-sim 属性）
  document.querySelectorAll('[data-sim]').forEach((btn) => {
    btn.addEventListener('click', () => simulateCheckin(btn.dataset.sim));
  });

  // 启动轮询
  setInterval(poll, POLL_INTERVAL_MS);
  poll();  // 立刻跑一次，不等第一秒
}

// ========================================
// 拉取花名册并构建房间网格
// ========================================
async function loadRoster() {
  try {
    const res = await fetch(`${API_BASE}/students`);
    if (!res.ok) throw new Error('students fetch failed');
    const data = await res.json();
    roster = data.students || [];
    setConnected(true);
    buildGrid(roster);
  } catch (err) {
    // 后端没起来时：画一个本地占位花名册（24 人 × 24 间单人房）
    console.warn('无法连接后端，使用占位花名册：', err);
    setConnected(false);
    roster = buildPlaceholderRoster();
    buildGrid(roster);
  }
}

// 根据花名册在页面渲染 24 个房间格子（一人一室）
function buildGrid(students) {
  $grid.innerHTML = '';

  // 按 seat_no（房间号）数值升序排序，101 < 102 < ... < 406
  const sorted = [...students].sort(
    (a, b) => Number(a.seat_no) - Number(b.seat_no)
  );

  sorted.forEach((student) => {
    const cell = document.createElement('div');
    cell.className = 'room-cell';
    cell.id = `seat-${student.student_id}`;  // 用 student_id 定位
    cell.innerHTML = `
      <div class="room-no">${student.seat_no}号室</div>
      <div class="student-id">${student.student_id}</div>
      <div class="student-name">${student.name}</div>
    `;
    $grid.appendChild(cell);
  });
}

// ========================================
// 轮询后端 /events，处理新到的刷卡
// ========================================
async function poll() {
  try {
    const res = await fetch(`${API_BASE}/events`);
    if (!res.ok) throw new Error('events fetch failed');
    const data = await res.json();
    setConnected(true);

    const checkedIn = data.checked_in || [];
    checkedIn.forEach((entry) => {
      if (!seenIds.has(entry.student_id)) {
        seenIds.add(entry.student_id);
        markSeatChecked(entry);
        speak(entry.name);
        showToast(entry);
      }
    });

    updateAttendance();
  } catch (err) {
    setConnected(false);
  }
}

// ========================================
// 把对应房间格子标绿（触发 CSS 过渡 + 脉冲）
// ========================================
function markSeatChecked(entry) {
  const cell = document.getElementById(`seat-${entry.student_id}`);
  if (cell) cell.classList.add('checked');
}

// ========================================
// 更新顶部总出席计数
// ========================================
function updateAttendance() {
  $attendance.textContent = `出席 ${seenIds.size} / 24`;
}

// ========================================
// 日语 TTS 语音播报（只念名字）
// ========================================
function speak(text) {
  if (!('speechSynthesis' in window)) return;  // 浏览器不支持就静默
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'ja-JP';
  utter.rate = 0.95;
  speechSynthesis.speak(utter);
}

// ========================================
// 右下角 Toast 通知（3 秒后自动消失）
// ========================================
function showToast(entry) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<strong>${entry.name}</strong>さん (${entry.seat_no}号室)`;
  $toastArea.appendChild(toast);
  // 3 秒后从 DOM 移除
  setTimeout(() => toast.remove(), 3000);
}

// ========================================
// 连接状态芯片
// ========================================
function setConnected(ok) {
  if (ok) {
    $connStatus.textContent = '🟢 サーバー接続済み';
    $connStatus.classList.remove('disconnected');
    $connStatus.classList.add('connected');
  } else {
    $connStatus.textContent = '🔴 サーバー未接続';
    $connStatus.classList.remove('connected');
    $connStatus.classList.add('disconnected');
  }
}

// ========================================
// 重置：清空后端事件 + 清空前端状态
// ========================================
async function resetAll() {
  if (!confirm('点呼状態をすべてリセットしますか？')) return;
  try {
    await fetch(`${API_BASE}/reset`, { method: 'POST' });
  } catch (err) {
    console.warn('后端重置失败（也许后端没起来）：', err);
  }
  // 无论后端是否成功，前端都清空显示
  seenIds.clear();
  document.querySelectorAll('.room-cell.checked').forEach((el) => el.classList.remove('checked'));
  $toastArea.innerHTML = '';
  updateAttendance();
}

// ========================================
// 手动模拟刷卡（footer 按钮调用）
// ========================================
async function simulateCheckin(studentId) {
  try {
    await fetch(`${API_BASE}/checkin?student_id=${studentId}`, { method: 'POST' });
    // 不在这里直接触发动画，让 poll() 循环自然发现，流程一致
  } catch (err) {
    alert('模拟刷卡失败：后端可能没起来');
    console.error(err);
  }
}

// ========================================
// 后端没起来时的占位花名册（24 人 × 24 间单人房）
// ========================================
function buildPlaceholderRoster() {
  // 顺序严格对齐任务中给的 24 条数据：S001 → S024，房间号 101-406
  const data = [
    ['S001', 'リュウイヒ', '101'],
    ['S002', '佐藤健太', '102'],
    ['S003', '鈴木涼', '103'],
    ['S004', '高橋翔', '104'],
    ['S005', '田中美咲', '105'],
    ['S006', '渡辺隼人', '106'],
    ['S007', '山本綾', '201'],
    ['S008', '中村大樹', '202'],
    ['S009', '小林美優', '203'],
    ['S010', '加藤陽菜', '204'],
    ['S011', '吉田蓮', '205'],
    ['S012', '山田千夏', '206'],
    ['S013', '佐々木葵', '301'],
    ['S014', '山口健', '302'],
    ['S015', '松本翔太', '303'],
    ['S016', '井上結衣', '304'],
    ['S017', '斎藤晴', '305'],
    ['S018', '清水花音', '306'],
    ['S019', '林美奈', '401'],
    ['S020', '池田咲希', '402'],
    ['S021', '橋本紗羅', '403'],
    ['S022', '阿部悠真', '404'],
    ['S023', '木村拓哉', '405'],
    ['S024', '山崎航', '406'],
  ];
  return data.map(([student_id, name, seat_no]) => ({
    student_id,
    name,
    seat_no,
  }));
}

// 启动
init();
