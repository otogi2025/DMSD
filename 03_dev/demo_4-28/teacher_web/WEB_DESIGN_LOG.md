# Tomoshibi 教员 Web · 设计决策完整归档

> **作用**：itsuki 提过的所有 Web 设计要求 + Claude Design 产出的所有东西 + [Code-Agent] 补提议的完整归档。防遗忘 / 下次会话快速恢复 context / AC 素材 / 代码 agent 实装时对照 single source of truth。
> **建立**：2026-04-21 by [Code-Agent]
> **最后更新**：2026-04-22 下午（Round 3 产出交付 + 解包 + 组件重命名）

---

## 1. 时间线（按发生顺序）

| 时刻 | 事件 |
|---|---|
| 2026-04-21 上午 | [Mac-demo-sprint] 建 demo_4-28/ 需求档 + backend skeleton（`03_dev/backend/`）|
| 2026-04-21 晚 · 18:09 | [Code-Agent] onboard，写 `teacher_web/DESIGN_BRIEF.md` v1（Claude Design 任务书，4 轮节奏）|
| 2026-04-21 晚 · 稍后 | itsuki："demo 的文件单独放到 demo 文件夹里" → backend + 3 新目录全挪到 `03_dev/demo_4-28/` |
| 2026-04-21 晚 · 19:30 UTC 前 | itsuki 在 Claude Design 跑完 Round 1（3 variations）+ Round 2（login + dashboard + live + override modal）|
| 2026-04-21 晚 · 19:38 | itsuki 发 Round 2 截图 "这个版本我很满意，就按照这个版本来" |
| 2026-04-21 晚 · 19:42 | itsuki 发之前的 dmsd-demo-2026-04-15 原型截图（4×6 号室网格 + デモコンソール），提议座位表改房间号网格 |
| 2026-04-21 晚 · 20:00 左右 | itsuki 纠正 Q2: "黄色是迟到，等到具体时间还没签到的人自动变黄" + 指明 `RollCall_Spec_v0.1.md §4.1 §5.3` 权威规则 |
| 2026-04-21 晚 · 稍后 | [Code-Agent] 通过 Anthropic design share link fetch Round 2 handoff bundle（6.3MB gzip → 9.1MB tar）+ 解压 + import 到 `teacher_web/` |
| 2026-04-21 晚 · 命名 | 主会话 [Mac-naming-sync] 系统正式命名 **Tomoshibi（灯火）**，全局 doc 同步 |
| 2026-04-21 晚 · 21:00 | itsuki 给 Q1-Q11 答复 + 要求"不要给选择题，列所有页面 + 功能，我一条条审" |
| 2026-04-21 晚 · 21:05 | [Code-Agent] 列 Round 3 清单（R2.1-R2.5 / II L.1-L.6 / III.A-E / IV SK / V G / VI P / VII GAP）共 ~60 条 |
| 2026-04-21 晚 · 21:10 | itsuki 一次性给 Round 3 完整决策（闲置退回 / 登录重构 / 编辑模式 / 男女寮 / Tomoshibi 命名 + 火焰 logo / 最近点呼可跳 / 趋势图 / 外宿表按实表 / 申请中心 / 全局检索 / 自动警告脚本暂不做）|
| 2026-04-21 晚 · 21:15 | [Code-Agent] 建 `round3_handoff/` + 导入 3 张参考图 + 写 Round 3 Prompt + WEB_DESIGN_LOG + 更新 questions_for_requirements.md |
| 2026-04-22 下午 · 16:25 | itsuki 给出 Claude Design Round 3 成品 `Tomoshibi_Prototype_v3__Standalone_.html`（9.4MB，self-unpacking bundle）|
| 2026-04-22 下午 · 16:28 | [Code-Agent] 导入到 `round3/Tomoshibi_Prototype_v3.html`（standalone 可直接浏览器打开）+ 用 Python 脚本解包 manifest（146 个资源）→ 重命名 JS 为 12 个 component + 3 个 vendor + 1 icon + 130 fonts，产出可编辑版 `round3/src/`（index.html + components/ + vendor/ + assets/ + _assets/ fonts）|
| 2026-04-22 下午 · 17:35 | itsuki 双击 `src/index.html` 全空白 → 诊断：`file://` 协议下 `integrity+crossorigin` 让 React/Babel 被 CORS block + `text/babel` script 靠 fetch 拉 .jsx 跨源受阻。Fix：删 integrity/crossorigin 属性 + 加 `round3/开发模式跑.command`（`python3 -m http.server 8787` 一键启动脚本 + 自动开浏览器）|
| 2026-04-22 夜 · 19:40 | itsuki 「NFC URL card 太繁琐 + 要 CLI 式启动」→ (a) `NfcQuickUrlCard` 大瘦身（DEMO badge / 长标题 / 使い方+前提+テスト 3 段说明 / テスト送信 button / IP 详述 / 折叠 button 全砍）→ 保留 3 元素：番号 select + URL 黑框 + コピー button 1 行紧凑（高度 ~45px）(b) 写 `round3/tomoshibi` bash CLI（ANSI 彩色 banner + subcommand `start` / `stop` / `status` / `ip` / `rebuild` / `pack` / `help`）— demo 当天 `./tomoshibi` 开启比双击 .command 更"pro"|
| 2026-04-22 夜 · 19:10 | itsuki 拍板 **外泊申请提交期限规则**：出発日の属する週の水曜日 23:59 OR 出発 48h 前、早い方。実装：`applications.jsx` に `outstayDeadline()` helper（当週水曜 vs 48h、Math.min 相当）+ `isLateSubmission()` + `DeadlineBadge` 列 + 顶部 banner + seed データを 2 late / 2 期限内 に調整。`outstay-detail-modal.jsx` に新 `DeadlineSection`（期限 vs 実提出の可視化 + 期限超過時「⚠ 面談必須」赤アラート）。iOS 側でも期限後送信をブロックするよう IOS_DESIGN_LOG に記載。|
| 2026-04-22 夜 · 19:00 | **IP 自动检测 card** in `roll-call-landing.jsx`（`NfcQuickUrlCard`）: fetch `/api/server-info` → 显示 Mac 当前热点/Wi-Fi IP + 番号 select + 一键复制 URL + テスト送信 button。`demo_server.py` 加 `/api/server-info` 端点（UDP socket trick 拿 outbound IP，热点环境下精确）。这样 itsuki demo 不用手动查 IP，URL 直接可复制粘贴到 iPhone 快捷指令 |
| 2026-04-22 晚 · 18:45 | **itsuki 拍板：点呼機（Pi 3A+）购买不及 → 银行卡 + iPhone 快捷指令 代替模式**。实装：(a) `round3/demo_server.py` 扩展 Python HTTP server（静态文件 + `POST /checkin?no=XX` + `GET /events/latest` + CORS + seq 去重 + 局域网 IP 自动检测输出）(b) `live-roll-call.jsx` 加 polling useEffect 每秒 fetch `/events/latest` + seq 变化触发 simCheckin + `SpeechSynthesisUtterance` 日语 TTS 读名 + 顶部 `NfcIndicator` 徽章 3 态（待機中/受信 OK/エラー） (c) `开发模式跑.command` 改调 `demo_server.py` (d) `NFC_DEMO_SETUP.md` 详细教程（iPhone NFC Automation 绑银行卡 → POST 局域网 IP + 故障排查 + 演示台本 + AC 话术） · flow: iPhone 碰卡 → 快捷指令 POST → Python server 记录 → Web 1s poll 检测 → リュウ イヒ 座位变绿 + スピーカー「リュウイヒ」|
| 2026-04-22 晚 · 18:35 | itsuki 对 iOS 設計档：「要在 Web 加学生アカウント管理页面」（iOS §9.2 之前 pending，现在直接做到 Round 3）。新加 `components/accounts.jsx`（AccountsPage + AccountDetailModal）+ `theme.jsx` 加 `window.ACCOUNTS` seed 24 人（00 = リュウ イヒ · 01-23 = 其他学生）+ Shell nav 加「学生アカウント管理」+ app.jsx route · 功能：番号/氏名/部屋/メール/電話/最終ログイン/状態（正常/失败N回/ロック中）列表 + 搜索 + 过滤（全員/男寮/女寮/ロック中）+ 4 stat card（総アカウント/今月新規/ロック中/次の新規番号）· 详情 modal 2 tab：プロフィール（基本情報 read-only + 編集可能 邮箱/电话/部屋 + パスワード初期化 + ロック解除）/ アクティビティ履歴（点呼/申请/扣分/体調/登录失败时间线）|
| 2026-04-22 下午 · 18:11 | 日语自然度全量扫描（itsuki native 视角）→ 修 10+ 处中文残留（名単→リスト / 距X→Xまで残り / 本月当月→今月 / 改判→手動調整 / 晚→晩 / push→プッシュ通知 / 部活早朝→部活生 / 自分で入力→記入 / 軍歌斉唱 删掉 等）+ **单文件打包脚本**：`build_single_file.py` + `打包单文件.command` 产出 `Tomoshibi_v3_single.html` 32MB（U 盘一文件走）|
| 2026-04-22 下午 · 17:55 | 白屏 2 连事件：Round 1 file:// CORS（Babel fetch .jsx 被 block + integrity 属性导致 CORS）→ 做 `rebuild.command` 把 jsx 内联到 index.html + 删 integrity/crossorigin 属性；Round 2 男寮 12→13 人后 records.jsx statuses hardcode 12 项数组越界 → RecStatusBadge crash 白屏 → `i % statuses.length` + fallback 修复 |
| 2026-04-22 下午 · 17:40 | itsuki 4 项调整：(1) `申請センター` 詳細列被挤没 → 列宽 80px→100px + 整行可点 hover 变色（applications.jsx）(2) **リュウ イヒ 女子寮 W101 → 男子寮 M101 as itsuki demo binding 迁移**（theme.jsx ROSTER_MEN 前插 + ROSTER_WOMEN 去掉，变 13男/11女；OUTSTAY_APPS + COMMUNITY_POSTS + cleaning mock 的 room W101→M101 同步迁移；佐藤 M101→M102、高橋 M102→M103 级联）(3) 让 リュウ イヒ 进清扫罚则名单：discipline.jsx demerit 数组 [0] 改成 `late=5 absent=2 → total=4.5`（清扫线 ≥4、禁足 ≥8） (4) 名前検索空格 normalize 修复：shell topbar suggestions 动态从 `window.ROSTER_ALL` 生成 + `normalize(s)=replace(/\s+/g,'').toLowerCase()` 比对；SearchPage 同逻辑 + 担当寮优先 → 全寮 fallback + 跨寮 warn banner |
| 2026-04-22 下午 · 17:00 | itsuki 走查 Round 3 发现 3 个文案问题 + 要求重做 コミュニティ 页 + 审 bug。[Code-Agent] 修复：`申請中心 → 申請センター`（applications.jsx）· `寮コミュニティ → コミュニティ管理`（shell.jsx nav + pages.jsx h1）· **CommunityPage 大改**（卡片 + 头像 + 点赞/评论 + 老师管理按钮 删除/ピン留め/通報解除 + 4 个统计卡片 + 3 个过滤器 + 5 tab 真实 seed 21 条学生投稿含通报样本）· **InfoPage お知らせ投稿 button**（右上 + ComposeNoticeModal 标题+本文）· 审出 7 bug 全修（override 却下/既読 死按钮 · discipline+notifications+records 里 hardcoded 男寮人名 → dynamic 按 teacher.dorm · shell 顶栏 2026-04-21 硬编码日期 → live clock · roll-call landing 日期 → 动态 · applications 外泊 badge 3 → 实际 pending count） |

---

## 2. 系统命名（2026-04-21 定版）

- **项目代号 / repo / git 历史**：DMSD（Dormitory Management System Digitalization）
- **系统对外名 / 用户看到的品牌**：**Tomoshibi**（灯火 / ともしび）
- **使用场景对照**：
  - Web UI 标题 / iOS App 名 / README / 对管理员・教授文案：**Tomoshibi**
  - spec 文档 / commit msg / 内部 variable 名（`window.RYO` 等）：DMSD 或 Tomoshibi 都可
  - Shell 左上 wordmark "DMSD" → "Tomoshibi"，下面"寮管理システム"不动
- **App icon**：`round3_handoff/01_tomoshibi_icon.png`（火焰 + 中心黄球，"灯火"视觉）替换原 ◇ 菱形
- **AC 面试话术（itsuki 原话定版）**："我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"

---

## 3. Design System "Ryō（涼）" 完整 tokens（Round 1 itsuki 从 3 variations 中选定）

摘自 `round2/theme.jsx`（以下为 Claude Design 产出的正式色值）：

```js
// Paper / surface / line
paper:        '#f4f5f7'
surface:      '#ffffff'
surfaceAlt:   '#f9fafb'
line:         '#e3e5eb'
lineStrong:   '#cdd0d8'

// Text
ink:          '#14171f'  // 正文
ink2:         '#3a404d'  // 次要
ink3:         '#6a6f7d'  // 三级
muted:        '#9ea3ae'

// Brand accent (cobalt blue)
cobalt:       '#2b4d8c'
cobaltDeep:   '#1c3567'
cobaltSoft:   '#e5ebf5'

// Semantic
ok (green):   '#2f7a55' | soft '#dfefe5' | border '#b7d7c4'
danger (red): '#b33a3a' | soft '#f3dcdc' | border '#e3b3b3'
info (cobalt alias): '#2b4d8c' | soft '#dde4f1' | border '#bdcae1'
warn (amber): '#a56b1e' | soft '#f2e3cb'
graySoft:     '#ebedf1' | grayBorder '#d5d8df'

// Round 3 新增（待 Claude Design 实装）
late (amber): '#c69320' | soft '#f5e7c2' | border '#e5c98a'   // propose
// OR 复用 warn，由 Claude Design 选

// Fonts
font:  '"Noto Sans JP","Hiragino Kaku Gothic ProN",-apple-system,BlinkMacSystemFont,sans-serif'
mono:  '"JetBrains Mono","SF Mono",ui-monospace,Menlo,monospace'

// Shadows
shadow1:      '0 1px 2px rgba(20,23,31,.04)'
shadow2:      '0 4px 16px rgba(20,23,31,.08), 0 1px 2px rgba(20,23,31,.04)'
shadowModal:  '0 24px 64px rgba(20,23,31,.28), 0 2px 8px rgba(20,23,31,.12)'
```

**Round 1 未选中的 variations**（Claude Design 产出，保留为 alternative 方向）：
- **A. 静 (Sei)** — ネイビー #1f3763 + 朱 #a8302a。ヒラギノ角ゴ ProN。normal density。"公文書" 堅実 感。
- **B. 密 (Mitsu)** — チャコール #2a2a24 + 苔緑 #4e6b3f。游ゴシック + IBM Plex Mono。compact density。高密度デスク感。

---

## 4. Claude Design 产出归档（已导入 repo）

### 4.0 Round 3 产出（`teacher_web/round3/`，2026-04-22 交付）⭐

**权威源**：`round3/Tomoshibi_Prototype_v3.html`（9.4MB，self-unpacking standalone bundle，可直接双击打开）

**可编辑版**：`round3/src/`（146 个资源解包 + JS 重命名为人类可读文件名）

```
round3/
├── Tomoshibi_Prototype_v3.html   ← ⭐ 标准交付 · 单文件可跑（demo 用这个）
└── src/                           ← 解包 + 重命名，用来读代码 / 后续二次开发
    ├── index.html                 ← 主入口（template）
    ├── components/                ← 12 个 React 组件（.jsx，未编译）
    │   ├── app.jsx                    ← Router + auto-logout timer
    │   ├── theme.jsx                  ← RYO tokens + late state + 12M/12F roster
    │   ├── shell.jsx                  ← 左 nav + topbar + 全局検索 + WS indicator
    │   ├── login.jsx                  ← 共有 ID + password + 3 次 lock
    │   ├── select-teacher.jsx         ← 男女寮 2 列 + 编辑模式
    │   ├── roll-call-landing.jsx      ← Dashboard + 7-day trend chart
    │   ├── live-roll-call.jsx         ← 座席表 + late + 倒计时 + デモコンソール
    │   ├── override-modal.jsx         ← 手動調整 + pending leave + health report
    │   ├── applications.jsx           ← /applications 4-tab landing
    │   ├── outstay-detail-modal.jsx   ← 外泊 4 段審認 modal
    │   ├── discipline.jsx             ← 規律処分 + 警告 + §7.5.1 自動アラート preview
    │   └── pages-records-search-etc.jsx ← records/search/notifications/cleaning/info/community 6 合 1
    ├── vendor/                    ← React 18 dev + ReactDOM + Babel standalone
    ├── assets/                    ← tomoshibi-icon.png
    └── _assets/                   ← 130 个 woff2 字体（Noto Sans JP / JetBrains Mono）
```

**解包流程**（供以后 Round 4+ 复用）：
1. HTML 里有 3 个 script block：`__bundler/manifest`（base64+gzip）、`__bundler/template`（整页骨架，UUID 替换）、`__bundler/ext_resources`（id→uuid 映射）
2. 用 Python 脚本遍历 manifest，base64 解码 + gzip 解压 → 写到 `_assets/{uuid}.{ext}`
3. 从每个 JS 文件头部的 `// ComponentName —` 注释识别组件名，重命名到 `components/`
4. 把 `index.html` 里的 `_assets/UUID` 替换成新路径
5. `window.__resources` 在 standalone 里是动态注入的，解包后需手动在 `<head>` 加 `<script>window.__resources={tomoshibiIcon:"assets/tomoshibi-icon.png"}</script>`（已加）

**Round 3 新增的 Round 2 没有的东西**：
- `components/theme.jsx` — 加了 `late` token (#c69320) + `warnStart`/`onTimeEnd`/`lateEnd` 时间窗口常量 + 12M+12F 男女寮 ROSTER
- `components/select-teacher.jsx` — 新页面，男女寮 2 列 + 编辑模式（红 X + "+追加"）
- `components/applications.jsx` + `outstay-detail-modal.jsx` — 外泊 4 段審認（担任 → 寮務課長 → 管理課長 → 国際交流部長 杉原大輔）
- `components/discipline.jsx` — 规律处分 + §7.5.1 amber card「自動アラート（開発中）」
- `components/pages-records-search-etc.jsx` — /records + /search + 4 个 Tier 2 skeleton 页合一
- `components/roll-call-landing.jsx` — 加了 7-day 迟到/欠席 bar chart
- `components/live-roll-call.jsx` — 加了 late 黄 + 3-min 迟到倒计时 + デモコンソール NFC sim + 凡例

### 4.1 Round 2 handoff bundle（`teacher_web/` 根目录）

| 文件 | 作用 |
|---|---|
| `index.html` (7KB) | 主入口，引用 `round2/*.jsx` + CDN React/Babel/Noto |
| `round2/theme.jsx` (1.9KB) | Ryo tokens + 24 学生 ROSTER（demo seed） |
| `round2/login.jsx` (3.8KB) | ログイン（teacher/1234 硬编码） |
| `round2/shell.jsx` (5.4KB) | 左 nav（7 大类）+ topbar |
| `round2/roll-call-landing.jsx` (5.9KB) | 点呼ダッシュボード |
| `round2/live.jsx` (9KB) | フルスクリーン座席表（24 人 6 列 grid，姓名大字 24-28px） |
| `round2/override-modal.jsx` (7.1KB) | 手動調整（4 radio + 理由 + 欠席届同時承認 checkbox） |
| `standalone-offline-backup.html` (8.4MB) | 完全内嵌版（demo 断网兜底） |
| `handoff/chat1.md` | itsuki ↔ Claude Design Round 1-2 完整对话（⭐ AC 素材） |
| `handoff/README.md` | Claude Design 给 coding agent 的 handoff 指引 |
| `handoff/design-system-round1.html` | Round 1 3 variations 比较页 |
| `handoff/uploads/` | itsuki 上传给 Claude Design 的截图（旧 prototype） |

### 4.2 Round 2 已实装的页面（pixel fidelity 的源）

| 页面 | 状态 | Round 3 改动 |
|---|---|---|
| /login | ✅ 2 field form | ⚠️ 登录后跳转改到 /login/select-teacher，不是直接主界面 |
| /roll-call ダッシュボード | ✅ session 选择 + 开始钮 + 4 统计 + 最近 session | ⚠️ 最近 session 加详细跳转 + 新加迟到/欠席趋势图 |
| /roll-call/live 座席表 | ✅ 24 人 6 列 + 4 状态 + 3 badge | ⚠️ 加 late 黄 + 男女寮分离 + 初始全灰 + 迟到倒计时 + 凡例 + デモコンソール |
| 手動調整 modal | ✅ | ⚠️ expand 显示体調/欠席届/改判履歴 |
| Shell（左 nav 7 大类 + topbar） | ✅ | ⚠️ Logo 换 Tomoshibi + 全局检索 + WS 状态 + 担当寮 badge + ログアウト button |

---

## 5. Round 3 完整设计决策

### 5.1 登录 flow（Q6 B 扩展）

| 项 | 决策 | 出处 |
|---|---|---|
| /login 输入字段 | **账号 ID + 密码** 2 个 field（Round 2 layout 不变，只改跳转目标） | itsuki 2026-04-21 |
| 账号 | 占位值 "tomoshibi"（全寮宿監共用）| [Code-Agent] propose |
| 密码 | 所有老师共用一个 | itsuki |
| 失败处理 | 显示"パスワードが違います (残り X 回)"，3 次失败锁 30 秒 | [Code-Agent] propose |
| 登录后跳转 | 不是主界面 → `/login/select-teacher` 老师选择页 | itsuki |

### 5.2 老师选择页 `/login/select-teacher`

| 项 | 决策 |
|---|---|
| 布局 | **左右两列**，左 = 男性寮 / 右 = 女性寮 |
| 列 header | 「男性寮」「女性寮」(带小图标) |
| 教员卡片样式 | **长方形 + 圆角（12-16px）+ 较大（~280×88px iPad 友好）** |
| 卡片内容 | 头像（头文字 1 字 cobaltSoft）+ 氏名大（16-18px bold）+「{n 分前にログイン} / 本日未ログイン / 初回」 |
| 上次选过的老师 | 右上角「前回」小 tag + 浅色强调框 |
| demo seed | 男寮：田中 健一 / 佐々木 陽一；女寮：鈴木 美咲 / 山田 花子（4 人）|
| 选卡片 | 进 Shell 主界面，左下显示当前教员 + 担当寮 badge |

### 5.3 编辑模式（⭐ itsuki 明确要求）

| 项 | 决策 |
|---|---|
| 入口 | 右下角「編集」floating button（圆形 + 笔 icon，ink 底 white icon）|
| 激活后 | 每张卡右上出现 **红圆 + 黑 X**（pop-in animation） |
| + 追加 card | 每列末尾出现虚线 dashed card + 大 plus + 「教員を追加」|
| 编辑模式退出 | 右下 FAB 变「完了」按钮 |
| 删除 confirm | 点 X 弹 modal「{氏名} 先生のアカウントを削除しますか？」+「削除」(danger) / 「キャンセル」|
| 删除后 | Toast「{氏名} 先生を削除しました」 |
| 追加 form | 氏名 input（必須）+ ふりがな input（optional，[Code-Agent] propose）+ 担当寮自动判定（左/右 column 上下文）|

### 5.4 切替 / 自动退出（itsuki 给了详细权衡表）

| 项 | 决策 | 细节 |
|---|---|---|
| 明示切替 | Shell 左下「切替」→ /login/select-teacher（密码状态保留） | itsuki |
| ログアウト | Shell 右上新加 button → /login（密码清） | [Code-Agent] propose |
| 闲置自动退回 | **30 分钟** 无操作 → /login/select-teacher（密码保留） | itsuki 选定 30 分 |
| 操作定义 | click / scroll / keypress / mousemove 任一 | [Code-Agent] |
| 例外 | **点呼 session active 中不触发** | itsuki（"演示到一半被踢出太尴尬"） |
| 5 分预警 | 25 分钟时右上 toast「あと 5 分で教員選択に戻ります」+「継続」button | itsuki |
| 密码彻底退出 | 不做时间自动；只物理关浏览器 / 手动「ログアウト」 | itsuki（选"或者根本不做" path） |
| Demo 临时调短 | `TIMEOUT_MS` constant 置顶 + 注释「// DEMO 用短縮はここ」，demo 当天改 180000 (3 分) | itsuki（演给管理员看这个功能）|

### 5.5 Shell 调整

| 项 | 决策 |
|---|---|
| 左上 logo | ◇ 菱形 → `01_tomoshibi_icon.png` 火焰图 + "DMSD" → "Tomoshibi" + "寮管理システム" 保持 |
| Browser tab title | `Tomoshibi · {当前页}` dynamic |
| Topbar 中央 | **全局检索 input**，placeholder「学生名・部屋番号・日付で検索...」+ 左内侧虫眼鏡 + 右内侧 `⌘K` hint。Enter 跳 `/search?q=` |
| Topbar 右侧 | 点呼実施中 badge（按可跳 live）+ **WS 接続状态** dot + 日時 + **ログアウト** button（新）|
| 左下 教员信息 | 阿凡达 + 氏名 + **担当寮 badge**（男寮/女寮色分）+「切替」+ **「当番中 / 非番」indicator** |

### 5.6 点呼 Dashboard（/roll-call）改动

| 项 | 决策 |
|---|---|
| ROSTER 男女分离 | 24 人分 男 12 / 女 12，每学生加 `dorm` field，部屋号 M101-M112 / W101-W112 |
| リュウ イヒ | 保留在 W101（女寮），demo 当日绑 itsuki iPhone |
| 最近 session 列表 | 每条加「詳細」button → /records?date=X&session_id=Y |
| ⭐ 迟到/欠席趋势图 | 新加卡片，4 统计下 + 最近 session 上。**Bar chart 7 日** 2 系列（黄=遅刻 / 红=欠席）。bar click 跳 /records?date=X |
| 对象选择 | session 下拉扩展：朝点呼·普通寮生 / 朝点呼·部活早朝 / 晩点呼·普通寮生 / 晩点呼·部活早朝（spec §4.2）|

### 5.7 点呼 Live 座席表

| 项 | 决策 | 出处 |
|---|---|---|
| ⭐ late 黄色 | 补 Round 2 漏掉的第 5 色。`LATE_THRESHOLD_SEC = 180`（3 分），session 开始 3 分钟后未签自动 unknown→late；过点后签到仍 late | spec §4.1 §5.3 + itsuki 纠正 |
| 迟到倒计时 | 顶部「あと X 分で遅刻判定開始」/「遅刻判定中」小字切换 | [Code-Agent] |
| 初始状态 | **全员灰色 unknown**，不预 seed checkin（真 iPhone tap 才变色）| itsuki |
| 当前寮筛选 | 只显示担当寮的 12 人 | itsuki "男女寮分离" |
| Badge expand | 🏥 体調 / ? 欠席届 / M 手動调整（改判履历 click）| [Code-Agent] |
| 凡例 (legend) | 右下 expandable，5 色 + 4 badge 说明 | [Code-Agent] |
| ⭐ デモコンソール | 下部 expandable panel，「NFC 読み取り失敗時のシミュレーションボタン」群，12 人模拟按钮 | itsuki 旧 prototype feature 复活 |
| デモ reset button | Round 2 已有，保留 | - |

### 5.8 override-modal 扩展

- 4 radio + 理由 textarea + 欠席届同時承認 checkbox（Round 2 已有）
- ⭐ expand 学生 pending 欠席届（理由 + 提出时刻 + 大「承認」「却下」按钮）
- ⭐ expand 体調報告（症状 + 補足 + 「既読」button）
- ⭐ expand 改判履历（如果此座已改过）

### 5.9 申請中心 /applications

| 项 | 决策 |
|---|---|
| landing 4 tabs | **外泊（demo 完整）** / 帰国（skeleton）/ 帰省（skeleton）/ タクシー（skeleton）|
| tab badge | pending 数小圆标 |
| 列表 sub-filter | 審査待ち / 承認済 / 却下 / 質問あり / 全て |
| 列表列 | 申請者 / 部屋 / 担当寮 / 出発日時 / 帰舎予定 / 行先 / 提出時刻 / 状態 badge / 「詳細」|
| 右上按钮 | 「CSV 出力」skeleton（toast「Demo 版未対応」）|

### 5.10 外泊詳細 modal（⭐ 按 Image #6 实体表完整数字化）

所有字段 itsuki 明确要求和实体表对齐：

- § 申請者本人：氏名 / 中・高 / 学年 / 組 / 本人連絡先（携帯 or WeChat 等）
- § 同行者：氏名 / 連絡先
- § 外泊日時：出発予定日時 / 帰舎予定日時
- § 移動手段（ラジオ）：
  - 行き：西口バス便 / 金川バス便 / JR / 自家用車 / タクシー / 教員送迎 / 飛行機 + 便番号
  - 帰り：同上
- § 寮生特別運行（条件付 checkbox + 期間）
- § 宿泊先（自宅以外）：日本人宅 / 留学生宅 / ホテル / その他 radio + 名称 + 住所 + 行先都市
- § 食事：朝/昼/夕 自食回数 number × 3 + 「自分で食事入力可」checkbox
- § 外泊の理由 textarea
- § 備考 textarea
- § 保護者許可 checkbox + 保護者電話
- § 承認 workflow 4 段階 card（担任 → 寮務課長 → 管理課長 → 国際交流部長 杉原 大輔。demo 可简化到 1 段）
- § Action buttons（⭐ 3 button 横並び）：「承認」/「却下」/「質問あり」
- § 承認後追記：承認者 + 承認時刻
- § 承認後 toast「学生に通知しました」

### 5.11 規律・処分 /discipline

完整实装（§7.1-7.6）：

- 7.1 顶部 ルール表示 card（現在 `discipline_config` 4 值 + 「値変更 skeleton」）
- 7.2 §1 本月全員ランキング table（月 + 寮 filter，列 sort）
- 7.3 §2 清掃罰則名单 cards
- 7.4 §3 外出禁止名单 cards
- 7.5 §4 警告リスト（連続超標）
- 7.5.1 ⭐ **自動アラート予告 card（UI 预约 only，demo 不启用 logic）** — 说明"将来后端脚本自动生成经常迟到/缺席短评"。对应 §6.1 backlog
- 7.6 学生 card click → 详情 modal（当月 timeline + 累計推移 + 「長期免除設定」skeleton）

### 5.12 記録 /records

- date picker + session dropdown
- Table: 学生 / 部屋 / session / チェックイン時刻 / 状態 / 方式（卡 / Shortcut / 手動）/ 改判者
- 右上「CSV 出力」/「印刷 · PDF 保存」skeleton
- 空状态 handling

### 5.13 検索 /search

- URL `/search?q=` 对接 Shell 全局搜索
- 2 tabs：**「学生から」** / **「日付から」**
- 「学生から」结果: **6 block 折叠** card：点呼 / 减点 / 体調 / 欠席届 / **申請全 type 統合（外泊 + 帰国 + 帰省 + タクシー）** / その他
- 「日付から」结果: 当日全寮汇总（签到统计 / 缺席名单 / 健康异常 / 申请处理）

### 5.14 Tier 2 skeleton landing

| 页面 | tab 结构 | mock |
|---|---|---|
| /notifications | 半真（Q7 A）4 数字 card + 最近通知 feed | 3/2/1/4 |
| /cleaning | 单页 | 扫除审核 3 条 |
| /info | 3 tabs：お知らせ / 行事 / バス | 各 3 条 |
| /community | 5 tabs：掲示板 / リクエスト曲 / 忘れ物 / 匿名建議 / 宅配 | 各 3-5 条 |

### 5.15 全局 UX

- 空状态：「まだデータがありません」+ 薄 icon
- 加载中：spinner
- 错误：顶部 red banner +「再試行」
- 承認/却下/削除前 confirm modal（防误操作）
- **面包屑**（topbar 下，深入子页才显示）
- 右下 **「DEMO」amber badge**（prototype 标识）
- Footer 最下: `Tomoshibi v0.1.0-demo · 2026 AC 入試プロジェクト成果物`
- 登录页底小字: 同上（管理员知道是学生作品）

---

## 6. 暂不做但记下（itsuki 2026-04-21 "帮我记着"）

### 6.1 ⭐ 后端自动迟到/欠席警告短评脚本

- **功能**：后端常驻 script 监测每个学生累计的 遅刻・欠席 次数，达到阈值时自动生成"经常迟到 / 经常缺席"之类短评，推送到教员 Web 专用栏目
- **Round 3 UI 预留占位**：`/discipline` §7.5.1 amber badge card「自動アラート（開発中）」+ 2 条 mock alert 灰显
- **阈值**：与 `discipline_config` 联动，上线前和老师商议
- **推送方式**：教员 Web 页面 banner + （可选）push 通知
- **后端实装方案**：FastAPI scheduled task (apscheduler) 或独立 worker 进程
- **关联 feature**：規律・処分 / 通知中心 / 学生 iOS App 本人向け警告
- **实装时机**：demo 采纳后第一批 post-demo feature
- **persisted location**：`00_admin/demo_4-28/questions_for_requirements.md §N4.5`

### 6.2 男女寮数据库分离（后端）

- itsuki 原话："男寮和女寮分别进入两个不同的数据库"
- demo 实装简化：单 SQLite + `dorm` field filter（前端按担当寮切换 query param）
- 将来 v1.0：真的物理分两个 PostgreSQL schema/db，敏感数据隔离

### 6.3 打印支持（/records "印刷 · PDF 保存"）

- demo 用 `window.print()` 浏览器原生，不排版优化
- 将来 v1.0：专用 print stylesheet + PDF export server-side

### 6.4 CSV 出力（各 table）

- demo skeleton button，click 弹 toast「Demo 版未対応」
- 将来 v1.0：后端 /api/export/csv endpoint

---

## 7. 参考资料索引

| 资源 | 路径 | 备注 |
|---|---|---|
| Round 2 源码 | `03_dev/demo_4-28/teacher_web/round2/*.jsx` | Claude Design 产出 |
| Round 2 offline bundle | `03_dev/demo_4-28/teacher_web/standalone-offline-backup.html` | 8.4MB，demo 网断兜底 |
| Round 2 chat | `03_dev/demo_4-28/teacher_web/handoff/chat1.md` | itsuki ↔ Claude Design 对话，AC ⭐ |
| Round 3 prompt | `03_dev/demo_4-28/teacher_web/round3_handoff/Round3_Prompt.md` | 待贴 Claude Design |
| Round 3 图 1 火焰 logo | `round3_handoff/01_tomoshibi_icon.png` | 新 icon |
| Round 3 图 2 外泊表 | `round3_handoff/02_gaihaku_form_reference.jpeg` | 实表数字化参考 |
| Round 3 图 3 改前 header | `round3_handoff/03_current_header_before.png` | "改之前什么样" 给 Claude Design 看 |
| Spec 色表权威 | `01_specs/rollcall/RollCall_Spec_v0.1.md §4.1` | 5 色 + overlay 黑 |
| Spec 时间窗 | `01_specs/rollcall/RollCall_Spec_v0.1.md §5.3` | `window_start / on_time_end / late_end / auto_end_at` |
| Spec 老师时刻表 | `01_specs/rollcall/RollCall_Spec_v0.1.md §4.2` | 朝/晚点呼 平日/祝休日 ×普通寮生/部活 |

---

## 8. Itsuki 原话精选（AC 叙事素材）

> "这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"

> "实时点呼界面，我希望是单独一个界面，因为按点呼开始后老师就直接只看实际座位表了。学生表才是主角。"（Round 1 → Round 2 的关键迭代）

> "黄色是迟到，等到了具体时间还没签到的人，就自动变成黄色"（纠正 [Code-Agent] 误解 Q2）

> "我的 demo 是把目之所及的功能全做出来对吧"（Demo 标准定义）

> "demo 的文件单独放到 demo 文件夹里，不要污染主项目"（工程卫生）

> "以上的我的选择仅供参考，你不要给我选择，你把要做的页面一个一个列出来，我一个一个给你我的意见"（协作模式：propose + audit，不要 A/B/C 给我选）

---

## 9. 待拍板 / 开放项

> **2026-04-22 Round 3 产出后刷新**

- [ ] **Round 3 视觉 walkthrough**（itsuki 下次会话做）：10 页全走一遍 / 配色 / 字号 / badge / 迟到倒计时 / 男女寮分配是否合理 / 外泊 modal 4 段审认布局是否像实体表
- [ ] Q2 确认（spec §4.1 §5.3）：late 黄 #c69320 + 3-min 窗口已进 `theme.jsx`，live grid 有 late 色块 → itsuki 视觉确认即可关掉
- [ ] 账号 ID 文字："tomoshibi" 占位是否 OK？或者换别的？（`login.jsx` 改 1 行即可）
- [ ] 4 段階承認 workflow demo 里几段？（当前 `outstay-detail-modal.jsx` 做的是完整 4 段 UI，demo 只需要 itsuki 按第 1 段"担任"承認即可）
- [ ] 男女寮 12 人分配（`theme.jsx` `window.ROSTER`）如果名字 vs 性别分错了，直接改 array（Round 3 已生成，改起来 O(1)）
- [ ] Tomoshibi 火焰图配色 vs Ryo cobalt 整体协调度（浏览器打开看一下）
- [ ] 自动警告短评脚本在 `/discipline §7.5.1` 的 "（開発中）" 文案是否合适（demo 时管理员会看到）

---

## 10. 下次会话 quick-start

**代码 agent / 未来自己回来继续工作**，优先读这 3 个档：

1. **本文件（WEB_DESIGN_LOG.md）** — 设计决策全归档
2. `DESIGN_BRIEF.md` — 当前实装状态 + Round 3 还没做的 list
3. `round3_handoff/Round3_Prompt.md` — Claude Design 的 Round 3 输入

**Round 3 已交付（2026-04-22）→ 下一步**：
- Demo 直接跑：`open round3/Tomoshibi_Prototype_v3.html`（单文件，离线可跑）
- 要改代码：编辑 `round3/src/components/*.jsx` → `open round3/src/index.html`
- 要接后端（FastAPI + WebSocket）：`app.jsx` 里 seed 数据替换成 `fetch('/api/...')` + `new WebSocket('ws://...')`
- Round 2 的 `round2/` 子目录 + 根目录 `index.html` 已过时，**不要再改**；作为历史引用保留

跳过 `DESIGN_BRIEF.md §附录` 和 `handoff/chat1.md` 除非需要 Round 1-2 历史 context。

---

**END** — 本档随 Web 设计新决策累积更新。下次重大变动时加一条"时间线"记录 + 对应 section。
