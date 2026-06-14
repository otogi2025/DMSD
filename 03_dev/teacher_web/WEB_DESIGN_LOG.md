# Tomoshibi 教员 Web · 设计决策完整归档

> **作用**：itsuki 提过的所有 Web 设计要求 + Claude Design 产出的所有东西 + [Code-Agent] 补提议的完整归档。防遗忘 / 下次会话快速恢复 context / AC 素材 / 代码 agent 实装时对照 single source of truth。
> **建立**：2026-04-21 by [Code-Agent]
> **最后更新**：2026-05-26（§实装进度速查表大改 + 新 §13 段「2026-05-26 Vite 实装版整体废弃 + Ryō polish 试做被回滚」）。早些：2026-05-21 §实装进度速查表加 A-029 / 2026-05-03 §11.9.1 学生登録コードパネル / 2026-04-22 下午 Round 3 产出交付。

## ⚠️ 实装进度速查表（2026-05-27 改 — 修 5-26 后多处 drift）

> 5-27 醒后会话 itsuki 让 CC 审查「能不能直接上线」时发现本表多处 drift（行数 3 倍漂移 / 路径错 / demo_server.py「死链」状态描述错 / 明文密码状态未刷新）→ 全面校准。

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ 100% | 806 行设计 + 5-03 学生登録コードパネル |
| **当前权威源** | ✅ | **`v1/src/index.html` 24041 行 standalone HTML**（4-21 Round 2 + 4-22 Round 3 + 之后多次 polish 推进累积）+ `v1/src/components/_legacy/*.jsx` 14 JSX 源（accounts / app / applications / discipline / front-desk / live-roll-call / login / outstay-detail-modal / override-modal / pages-records-search-etc / roll-call-landing / select-teacher / shell / theme） |
| **v1/src/ Vite + TS 实装** | ❌ 5-26 整体废弃 | 已归档，不在公开仓库（App.tsx / pages × 5 / store / Shell / package.json / vite.config.ts 等 13 文件）。废弃理由：itsuki 5-26 看到 Vite 实装版后判定其与本人设想的界面完全不符，拍板废弃归档 |
| `api/client.js` + `api/client.ts` | 🟡 保留未用（除 Login） | `client.js`（5-04 后多次扩，含 rollcall / discipline / cleaning / front-desk / announcements 5 类 helper 含 5-27 补的 4 个 announcement helper）+ `client.ts`（416 行 TS 类型版，5-26 归档迁移前留下）— 实装时只有 Login 已真接 backend，其他 15 个 page 全部 `window.*` 假数据 |
| Ryō standalone NFC 实时点呼 demo | 🟡 双入口不一致 | `demo_server.py` 文件**真存在 142 行**（3 端点 /api/server-info / POST /checkin / GET /events/latest）；但启动脚本 `开发模式跑.command` 调 `python3 -m http.server`（demo 端点失效）vs `tomoshibi` CLI 调 `python3 demo_server.py`（demo 端点正常）— **双击 vs CLI 行为不一致** — 需统一到一个入口 |
| AnnouncementsAPI | 🟢 backend 5 端点已实装 + client.js 已暴露 | 5-27 backend 5 endpoint 全注册（list / unread-count / detail / replies / replies/{id}）+ client.js 5-27 补 4 helper（updateAnnouncement / getAnnouncementUnreadCount / postAnnouncementReply / deleteAnnouncementReply）— 缺老师公告**发布页 UI**（A-026 已补 type 但 UI 不在范围）|
| AppStatus 完整性 | 🟡 部分 | `returned` 状态漏（A-017 已修） |
| Application 字段对齐 | 🟡 部分 | reason / stay_locations / meals_skip / flight_* / withdrawn_at / bus_route_id 全缺（A-018 已修） |
| demo/ 归档 | ✅ 已归档 | 14 文件 jsx demo SPA（A-032 已归档） |
| v1/src/index.html A-039 明文密码 `12345678` | ✅ **5-26 commit `b0bed26` 已删** | LoginScreen 改 fetch `${API_BASE}/sessions/teacher` 真后端 + 删 demo 提示行 — 5-26 已闭合（DESIGN_BRIEF §5 已记） |
| **5-27 backend 接入准备状态** | ✅ backend 就绪（frontend 等接入） | 5-27 backend 大批修：spec §11.4 改判扣分联动 + spec §7.5 自动扣分（rollcall late 1.0 / absent 2.0 / study_absent 1.5）+ WebSocket `/api/v1/ws/teacher` 实装（broadcast checkin / override / outstay_new 事件）+ alembic c1d2e3f4 加 demerit/cleaning/front_desk 3 张表 + R4 寮过滤 helper + 8 个新 P0/P1 endpoint（discipline 3 + cleaning 3 + front-desk 3 — 含 2 个 list）。frontend 接入只剩**调用** |
| **直接上线整体评估** | 🔴 **未达成** | UI 90% ✅ / Login 真接 backend 1/16 ✅ / 其他 15 个 page 全部假数据 ⏳ / 3 个 SkeletonTab（帰国 / 帰省 / タクシー）⏳ / WebSocket 重连 banner（spec §11.8）⏳ / demo_server.py 双入口不一致 ⏳ — 详见 TODO §🚀 §N teacher_web 直接上线 backlog |

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
| 2026-04-21 晚 · 20:00 左右 | itsuki 纠正 Q2: "黄色是迟到，等到具体时间还没签到的人自动变黄" + 指明 `RollCall_Spec.md §4.1 §5.3` 权威规则 |
| 2026-04-21 晚 · 稍后 | [Code-Agent] 通过 Anthropic design share link fetch Round 2 handoff bundle（6.3MB gzip → 9.1MB tar）+ 解压 + import 到 `teacher_web/` |
| 2026-04-21 晚 · 命名 | 主会话 [Mac-naming-sync] 系统正式命名 **Tomoshibi（灯火）**，全局 doc 同步 |
| 2026-04-21 晚 · 21:00 | itsuki 给 Q1-Q11 答复 + 要求"不要给选择题，列所有页面 + 功能，我一条条审" |
| 2026-04-21 晚 · 21:05 | [Code-Agent] 列 Round 3 清单（R2.1-R2.5 / II L.1-L.6 / III.A-E / IV SK / V G / VI P / VII GAP）共 ~60 条 |
| 2026-04-21 晚 · 21:10 | itsuki 一次性给 Round 3 完整决策（闲置退回 / 登录重构 / 编辑模式 / 男女寮 / Tomoshibi 命名 + 火焰 logo / 最近点呼可跳 / 趋势图 / 外宿表按实表 / 申请中心 / 全局检索 / 自动警告脚本暂不做）|
| 2026-04-21 晚 · 21:15 | [Code-Agent] 建 Round 3 交接目录（已归档）+ 导入 3 张参考图 + 写 Round 3 Prompt + WEB_DESIGN_LOG + 更新 questions_for_requirements.md |
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
| 2026-04-22 ~ 06-04（多次） | ⚠️ 本时间线在此有断档：4-22 之后到 6-04 的多次推进（backend 接入 / 学習出席页 / 出寮者一覧 / 食数导出按钮 / 学習名簿 等）未逐条入本表，真值见 git log。 |
| 2026-06-05 | **代録（出寮届）表单页** `ProxyApplicationPage`（杭田五-3「教師用は当日入力可」收尾）：老师替学生补录帰省/外泊/帰国届。① 学生选择器走 `proxyCandidates`（GET /applications/proxy-candidates，按寮边界 + 姓名/学号搜）② 申請种类 3 按钮切换 ③ 共有字段（出寮/帰寮 日期·方法·时刻 + 本人連絡先），交通手段下拉选项与 iOS `ApplyStubs` LEAVE/RETURN_TRANSPORTS 一致 ④ 种类别：帰省理由 + 長期休暇 / 外泊·帰国 同行者+行先+宿泊先（必填≥1）/ 帰国 飞机信息 ⑤ 食事栏按学生 `is_overseas` 切换：留学生填食事不要期间（前端展开成 `[{date,meal}]`，照抄 iOS expandMealsSkip）、日本人显示「自己填食事入力表」提示。提交 `createByTeacher` → POST /applications/by-teacher。导航栏「代録」项限代録 5 角色（`DAIROKU_ROLES_FRONT`）可见。`client.js` 加 `proxyCandidates`+`createByTeacher`。验证 check_jsx 16 块 0 错误。| [Mac-Opus 4.8 1M] CC |

---

## 2. 系统命名（2026-04-21 定版）

- **项目代号 / repo / git 历史**：DMSD（Dormitory Management System Digitalization）
- **系统对外名 / 用户看到的品牌**：**Tomoshibi**（灯火 / ともしび）
- **使用场景对照**：
  - Web UI 标题 / iOS App 名 / README / 对管理员・教授文案：**Tomoshibi**
  - spec 文档 / commit msg / 内部 variable 名（`window.RYO` 等）：DMSD 或 Tomoshibi 都可
  - Shell 左上 wordmark "DMSD" → "Tomoshibi"，下面"寮管理システム"不动
- **App icon**：`01_tomoshibi_icon.png`（已归档；火焰 + 中心黄球，"灯火"视觉）替换原 ◇ 菱形
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

### 4.1 Round 2 handoff bundle（已归档，不在公开仓库）

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

> **⚠️ 2026-05-27 itsuki 拍板 — 本节 §5.1 / §5.2 / §5.3 旧方案已被废除**（共用密码 + 选老师 + 登录前编辑老师卡片）。新方案见 §5.1' / §5.2' / §5.3'。废除理由：
> - §3.4 拍板「每个老师独立账号密码（R3）」+「前台不允许自助注册任何教师账号」— 共用密码 + 登录前匿名编辑卡片**直接违反**这两条
> - itsuki 5-27 重申「老师密码不共用 / 每老师独立账户 / 新宿管来了从已登录的教师管理页加，离职从那里删」

### 5.1' 登录 flow（2026-05-27 拍板 — 实名账户版）

| 项 | 决策 | 出处 |
|---|---|---|
| 第 1 屏 = 直接列老师卡片 | 不再先输共用密码 — 进 web 就调 `GET /api/v1/teachers/public`（无认证、只返 `id + name + dorm + last_login_mins`，不返 `login_id / role / email`）| itsuki 2026-05-27 |
| 第 2 屏 = 选中老师后输密码 | 点卡片 → 显示「{name} 先生」+ 密码 input + 登录按钮（POST `/api/v1/sessions/teacher` 用屏 1 拿到的 `teacher_id` UUID + 输入密码 — 不暴露 `login_id` 给前端，防爬虫枚举攻击）| 同上 |
| 共用账号 `tomoshibi` + 共用密码 | **废除** — backend `Teacher.login_id` 字段保留（用于后端识别个人），但前端登录 UX **完全无视该字段**（用户感知层面 = 选名字 + 输密码） | 同上 |
| 失败处理 | 同老师密码 3 次失败 → backend `Teacher.locked_until` 锁 30 秒（已实装、不动）| 现有 |
| 登录后跳转 | 直接进 Shell 主界面（不再有「选今日担当者」中间页 — §5.2' 砍）| itsuki 2026-05-27 |

### 5.2' ~~老师选择页 `/login/select-teacher`~~ — 砍

旧设计的「登录后选今日担当者」中间页砍。理由：
- 旧方案 = 共用密码下匿名进 Shell，所以需要「中间页让大家声明今天是谁」；新方案 = 每人独立账号，登录后**身份已确定**，不需要中间页
- 「今日担当者」概念用 Shell 左下「当前登录教员」badge 替代（已有）

### 5.3' 教师账号管理（搬到 Shell 内的「教师管理」页 — 登录后才能用）

| 项 | 决策 |
|---|---|
| 入口 | Shell nav 加「教师管理」项（仅「寮務管理」权限教师可见，§3.4） |
| 列表 | 全教师 row 列表（name + role + dorm + 状态 + 最終ログイン），调 `GET /api/v1/teachers`（需登录） |
| 创建新教师 | 右上「新規教員を追加」按钮 → modal（name + login_id + dorm + 初始密码） → `POST /api/v1/teachers`（已登录教师 + 寮務管理权限）|
| 删除教师 | 每行「削除」按钮 → 确认对话框 → `DELETE /api/v1/teachers/{id}` |
| 旧「登录前编辑模式」（floating FAB + 卡片右上 X + AddCard） | **砍** — 违反 §3.4「前台不允许自助注册任何教师账号」|
| 邀请码流程（`POST /teachers/invitations` + `/teachers/register`）| 保留 backend 接口、但 v1.0 web 不实装 UI（v1.1 候补 — 「新教师远程注册」场景才需要邀请码；v1.0 用「现场添加」简化版即可）|

#### 5-28 实机 bug 修复（commit `01d0654`）

| bug | 根因 | 修法 |
|---|---|---|
| 登录页显示 9 个老师账号 | `seed.py` `DEV_TEACHERS` 原有 9 个假数据老师 → 备份 + 重建数据库 + 只保留「新股」1 个 | `seed.py:70-78` `DEV_TEACHERS` 砍到 1 个；旧 DB 备份 `.bak` + 重跑 seed |
| 屏 2 返回按钮「消失」/ 点不中 | 按钮样式 `fontSize:12 + padding:0 + color:T.ink3 + background:transparent` → 点击区域只有约 12px 高、颜色极浅，itsuki 看不见也点不中 | 改为 `background:T.cobaltSoft + color:T.cobalt + borderRadius:6 + padding:"8px 12px"` — 按钮变成淡蓝背景可见控件 |

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
| 左 nav 分组（6-14 追加） | 16 菜单平铺 → **4 组归类**，每组加灰色小标题、高频在上 / 管理项沉底。组划分：点呼業務（点呼・代録・出寮者一覧・通知）/ 生活・指導（申請・規律・処分・学習出席・記録・事案記録）/ 情報・発信（お知らせ・バス・コミュニティ管理・フロント業務）/ 管理・設定（学生アカウント管理・学生登録コード・教員アカウント管理・開示申請）。起因 itsuki 截图反馈「散在一排不美观不直观」。⚠️ §4.2 旧表「7 大类」是 5-26 废弃 Vite 版的笼统旧话、无具体定义，不作数 |
| 菜单可见性（6-14 厘清，单源真值）| **16 项全部对所有登录老师显示**，不按角色 / 职位隐藏任何菜单。敏感功能（教員アカウント管理 / 学生登録コード / 事案記録 / 開示申請 等）的增删改由**后端 `require_permission` 按权限组把关**：无权限老师能进页面、但具体操作被后端拦（403）。⚠️ 本档早期多处「某菜单仅 X 権限可見 / role-based nav」（§5.3' 教师管理「仅寮務管理可見」、§7.16 学生登録コード、§4.2 代録限 5 角色 `DAIROKU_ROLES_FRONT` 等）全是「职位退化为纯显示标签」重构**之前**的旧设计，已撤回、不作数 —— 现实以本行为准 |

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

### 5.8A 点呼机离线 → 老师手动接管 ✅（2026-06-04 itsuki 拍板）

点呼机掉线时，老师网页（teacher_web，老师在 iPad 上用的网页）要让老师顶上，自己逐个点学生状态：

1. **告警来源**（两种）：
   - 点呼机单独掉线 → 后端推 `device_offline` 事件（见 `BACKEND_DESIGN_LOG.md §5.8`）→ 网页顶部弹红色告警条「点呼機がオフラインです（设备 X）」。
   - 老师平板自己也跟后端断了 → 网页本地检测自己那条 WebSocket 断 → 显示「サーバーと接続が切れています」。
2. **老师确认**：告警条带「確認」按钮。老师点确认 = 进入「手動点呼モード」（手动点呼模式）。
3. **手动接管**：手动模式下，座席表（座位实时表）每个学生可直接点状态，复用已有的 `override-modal.jsx`（手動調整弹窗，老师手动选学生的出勤状态）。老师对照本人 + 纸质名单逐个判。
4. **恢复**：后端推 `device_online` → 告警条变绿「点呼機が復帰しました」→ 老师可退出手动模式。补传数据合并规则见 `BACKEND_DESIGN_LOG.md §5.8`（默认老师手动优先）。

> 界面不用新做 —— 复用 `override-modal.jsx`，只加「离线告警条 + 手动模式开关」两块 UI。

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
| /community | 4 tabs：掲示板 / リクエスト曲 / 忘れ物 / 宅配（5-27 砍「匿名建議」§7.14）| 各 3-5 条 |

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

> **2026-05-27 更新**：原 round2/ + round3/ + handoff/ + round3_handoff/ 4 个子目录全部塌缩归档、不在公开仓库（详见 §12 Vite 废弃 + DESIGN_BRIEF §2 文件清单）。原资源路径已迁到归档目录或塌缩到 `v1/src/components/_legacy/` + `v1/src/assets/`。

| 资源 | 路径 | 备注 |
|---|---|---|
| 当前权威源（standalone） | `v1/src/index.html` | 7700+ 行 inline 全部 CSS/JS/字体 |
| JSX 组件源（14 个） | `v1/src/components/_legacy/*.jsx` | 原 round2/ + round3/ 塌缩后命名（误导但已实际是 Ryō 主源） |
| 后端对接代码 | `v1/src/api/client.ts` | 416 行 26 endpoint — 保留未用，未来 Ryō 接真后端复用 |
| 火焰 logo | `v1/src/assets/tomoshibi-icon.png` | 原 round3 交接图 01_tomoshibi_icon.png（已归档） |
| Claude Design 历史对话 | 已归档，不在公开仓库 | itsuki ↔ Claude Design Round 1-3 完整迭代 — AC ⭐ |
| Spec 色表权威 | `01_specs/rollcall/RollCall_Spec.md §4.1` | 5 色 + overlay 黑 |
| Spec 时间窗 | `01_specs/rollcall/RollCall_Spec.md §5.3` | `window_start / on_time_end / late_end / auto_end_at` |
| Spec 老师时刻表 | `01_specs/rollcall/RollCall_Spec.md §4.2` | 朝/晚点呼 平日/祝休日 ×普通寮生/部活 |

---

## 8. Itsuki 原话精选（AC 叙事素材）

> "这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"

> "实时点呼界面，我希望是单独一个界面，因为按点呼开始后老师就直接只看实际座位表了。学生表才是主角。"（Round 1 → Round 2 的关键迭代）

> "黄色是迟到，等到了具体时间还没签到的人，就自动变成黄色"（纠正 [Code-Agent] 误解 Q2）

> "我的 demo 是把目之所及的功能全做出来对吧"（Demo 标准定义）

> "demo 的文件单独放到 demo 文件夹里，不要污染主项目"（工程卫生）

> "以上的我的选择仅供参考，你不要给我选择，你把要做的页面一个一个列出来，我一个一个给你我的意见"（协作模式：propose + audit，不要 A/B/C 给我选）

---

## 8.5 2026-04-23 追加決定（学号体系 + 房间号 + 改动履歴 + コミュニティ拆分）

> **⚠ 権威源は `02_design/system_features.md`**。ここは Web 視点の抜粋 + 実装要件のみ。

### 8.5.1 学号体系 6 桁化（`accounts.jsx` + `theme.jsx` 大改）

- `window.ACCOUNTS` seed に `grade_code` / `class_code` / `seat_no` 3 フィールド追加、`student_no` は computed（例 `060218`）
- `no` フィールド（旧 `00`-`23`）は deprecated、移行期間のみ並存
- リュウ イヒ: `no='00'` → `student_no='060218'`（grade=06 高 3 / class=02 B / seat=18）
- accounts.jsx テーブル: `番号` 列 → `学号` 列に改名、6 桁で表示
- 详细 modal「プロフィール」tab: 学年 / 組 / 番号 個別表示 + read-only（学生編集可、老师は履歴で確認）

### 8.5.2 学生改动履歴 連携（accounts.jsx アクティビティ履歴 tab 拡充）

- 現状の活动履歴 mock（登录/申请/点呼）に **学号変更 / 房间号変更 / メール変更 / 電話変更 / アバター変更 / パスワード変更事実** を追加
- `buildActivityMock(a)` 拡張: `actor: 'self'|'teacher'|'system'` + `field` + `old_value`/`new_value` entries
- 表示例: 「2026-04-05 08:12 · 自己 · 房間号 M101 → M205 に変更」

### 8.5.3 房间号 一括分配ページ（新 nav、v1.1 未来、Round 4 backlog）

- 新ページ `components/room-assignment.jsx`（未作成）
- 左右 pane: 左 = 学生 list（フィルタ: 寮 / 学年 / 未割当） / 右 = 部屋 grid（M101-M1XX / W101-W1XX）
- drag & drop で割当 → 保存 button → 後端一括 push → 学生 App 自動更新
- Demo 4-28 では対象外、Round 4 backlog 入り

### 8.5.4 コミュニティ管理 拆分（pages-records-search-etc.jsx CommunityPage 縮小）

- ~~**通報機能は保留**（itsuki 2026-04-23 拍板）~~ → **通報機能は彻底削除**（itsuki 2026-06-13 拍板：点歌举报+封禁系统从未真正实装，5 端 + 规格全删，点歌本体保留）
- **リクエスト曲**: ラベル「館内 BGM」→「寮内 BGM」修正 + **排序を古い順に変更**（現状時刻降順 → 古い順）+ 朝/晩 chip filter（iOS 側で字段追加後に有効化、字段追加は itsuki 拍板待ち）
- **宅配通知 + 忘れ物 を CommunityPage から撤去** → 移設先は itsuki 拍板待ち（案 1: 新 nav「フロント業務」 / 案 2: 既存「通知」ページ内 tab）
  - 残り 2 tab: 掲示板 / リクエスト曲（5-27「匿名建議」も砍 §7.14）
  - Shell nav に新規項目追加（案 1 採用時）or 既存 InfoPage に tab 追加（案 2 採用時）

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
- [ ] **(a) コミュニティ 宅配通知 + 忘れ物 移設先**: 新 nav「フロント業務」 / 「通知」内 tab どちらに（2026-04-23 §8.5.4 pending）
- [ ] **(b) リクエスト曲 朝/晩 字段**: iOS 側追加 → Web 側 filter 有効化 する？（2026-04-23 §8.5.4 pending、itsuki 「3 古い順」回答済だが朝晩字段未明示）
- [ ] **(c) 学号変更に老师承認要否**: 学生自由変更 + 履歴（現方針） vs 学生申請 → 老师承認（§8.5.2 pending）

---

## 10. 下次会话 quick-start

> **2026-05-27 重写**：Round 2/3 时代结束。当前权威源 = `v1/src/index.html` standalone。Vite + TS 实装版 5-26 整体废弃归档（详见 §12）。

**代码 agent / 未来自己回来继续工作**，优先读这 3 个档：

1. **本文件（WEB_DESIGN_LOG.md）** — 设计决策全归档 + §12 5-26 Vite 废弃 + polish 回滚事实记录
2. `DESIGN_BRIEF.md` — 当前实装状态 + 真接口对接路线 D0-D6 + v1.0 关卡清单
3. `v1/README.md` — 怎么打开 / CLI 用法

**当前推进方式**：
- 看效果：双击项目根启动脚本（本地保留不公开，起后端 8000 + 前端 8787 + 自动开浏览器）/ NFC 演示用 `cd v1 && ./tomoshibi start`（仅前端，不起后端）
- 改 UI：编辑 `v1/src/index.html`（standalone HTML，所有 CSS/JS inline）— 改完浏览器 Cmd+R 刷新
- 改 JSX 源后内联：`v1/rebuild.command`（把 `_legacy/*.jsx` 重新内联到 `index.html`）
- 打包单文件 demo：`v1/打包单文件.command`（用 `build_single_file.py` 打包成可携带单 HTML）
- 接真后端：参考 `v1/src/api/client.ts` 已定义的 26 个 endpoint — 内联到 standalone 时需要删 TS 类型导出 + 暴露到 `window.tomoshibiApi` namespace（详见 DESIGN_BRIEF §6）

历史归档：原 `round2/` / `round3/` / `handoff/` / `round3_handoff/` 4 个子目录 + Vite + TS 实装版均已归档，不在公开仓库。Round 1-3 历史对话作 AC 素材保留。

---

## 11. v1.0 实装清单（2026-04-30 加）

> **作用**: 给 Web code agent 接手 v1.0 实装的入口章。
> **agent 阅读顺序**（两层结构）:
> 1. **共用层（必读）**: `02_design/system_features.md` —— 角色 / 数据模型 / §7 14 子节功能矩阵 / R1-R4 / 38 条要件
> 2. **专属层（本档全文）**: 本 LOG §1-§9 = Web 设计决策 + §10 下次会话 quick-start + 本 §11 = 实装层
> 3. **后端 API 契约**: `03_dev/backend/BACKEND_DESIGN_LOG.md`
> 4. **点呼业務規則**: `01_specs/rollcall/RollCall_Spec.md`（特に §4 §5 §11）
>
> **決策標記**: ✅ 已定 / 🟡 CC 假设 / ⏳ 待拍板（聚集到 §11.9）

### 11.1 P0 范围 + 角色 → 路由対応

#### P0 角色 → 必有功能

| 角色 | 設備 | P0 必有 |
|---|---|---|
| 寮務部長 / 寮務課長 | 〇 個人 PC（職員室）| 出寮届 一覧 + 承认（#10）+ コメント（#13） |
| 国際交流部長 / 国際交流課長 | 〇 個人 PC | 同上（仅留学生 外泊/帰国 chain） |
| **寮監** | **★ 寮管室 iPad** | 朝/夜点呼（#16-#19）+ 改判（一本道 R2） |
| **学習担当** | **★ 寮管室 iPad** | 学習出席（#14-#15）+ 自動判定修正（#20） |
| 寮務一般教師 | 〇 個人 PC | （P0 範囲外） |

#### P0 路由

```
/login/teacher                    教师 login（學生 login は iOS App、Web では `/login/student` 備用）
/                                 自動分流（按 role 重定向）
/applications                     役职: 待承認一覧
  /applications/:id               詳細 modal
/study                            ★ iPad 学習担当: 当日出席列表（一本道）
  /study/finalize                 ★ 一本道結束 button（19:55 等）
/rollcall                         ★ iPad 寮監: 当天 session 选择
  /rollcall/sessions/:id          ★ 座席表 live + 改判 modal
  /rollcall/sessions/:id/summary  ★ 「点呼総結」中層頁（RollCall_Spec §5.6）
/logout
```

#### Role → home 重定向

- 寮監 / 学習担当 → 当天有 running session → `/rollcall/sessions/:id` 直跳；無 → `/study`（19:00-19:40）/ `/rollcall`（点呼前）/ landing
- 役职 4 人 → `/applications`
- 寮務一般教師 → P0 範囲外（landing「P0 未対応」）

### 11.2 技术栈（demo R3 → v1 升级）

| 層 | demo (R3) | v1 |
|---|---|---|
| Build | Babel standalone in-browser | **Vite + React 18** |
| ファイル | `.jsx` | `.tsx` (TypeScript) |
| 状態 | `window.X` global | **Zustand**（軽量） |
| Routing | hash-based 自製 | **React Router v6** |
| API | demo_server.py + polling | v1 backend (`/api/v1/*`) + polling + WebSocket |
| 様式 | inline style + theme.jsx | **CSS Modules** + theme tokens 復用（**Ryō 配色保留**） |
| icons | inline SVG | `lucide-react` |

> **🟡 CC 推奨**: TS + Zustand + Vite 升级。理由: demo 已証明 R3 設計可行、v1 加权限 / 真后端复杂度上来 → TS 防 bug 価値大。⏳ §11.9-W1 待拍板。
> **iPad Safari 互換性**: Vite 打包時 target = `safari14`（iPadOS Safari 17 已遠超）。

### 11.3 起点（demo/ → v1/ 復制）

| demo 組件 | v1 処置 |
|---|---|
| `theme.jsx` | tokens（color / font / shadow）復制、`window.ROSTER` / `ACCOUNTS` 等 mock seed 削除 |
| `shell.jsx` | **大改** — R3 教師独自 login / role-based nav / logout button |
| `login.jsx` | **重写** — demo 共有密码 → 教師 login_id + password |
| `live-roll-call.jsx` | 5 色座席表 + 凡例 保留、**改后端连接** + R4 dorm filter |
| `override-modal.jsx` | layout 保留、加 §11 时限矩阵 |
| `applications.jsx` + `outstay-detail-modal.jsx` | **大改** — 4 段審認 → **4 役职並行**（chain ロジック変更）|
| `accounts.jsx` | P2 学生管理参考、P0 不重写 |
| `discipline.jsx` / `pages-records-search-etc.jsx` / `cleaning.jsx` / `info.jsx` / `community.jsx` | P0 不動（P3 範囲） |

### 11.4 全局约束（实装层 — R2 概念定義は system_features §2）

#### R2 — iPad ★ 一本道 在 Web 实装上的体现

iPad ★ 路由（`/study` / `/rollcall/*`）**禁止**:
- dropdown / select 多選項（除非"開始 / 結束"等価 button）
- 多 tab 切替（同一頁面只有一個 main view）
- 折叠的隠し機能（手指難按 / 老人不会発見）
- 多 step フォーム（提交前 confirm 例外）

iPad ★ 路由 **必須**:
- 主操作 button ≥ 80px 高 / 文字 ≥ 24pt
- 名前 list 文字 ≥ 18pt
- 状態 color 明確（緑/黄/赤 + 文字 label、不只靠 color）
- 「次に何をすれば」必ず文字明示
- ログアウト button → 双重 confirm

〇 路由（PC 用）不受 R2 限制。

#### R4 — dorm 分離

教師 JWT 含 `assigned_dorm`。前端:
- iPad ★ 路由不显示 dorm switcher（自動按 assigned_dorm）
- 役职 〇 路由可显示 dorm filter（默认全件、跨寮役职 4 人 = 全件）

#### 自動退出（沿用 demo R3 §5.4）

- 30 分钟无操作 → `/logout`
- 25 分时 toast「あと 5 分で退出します」+「継続」
- **iPad ★ 例外**: 点呼 session active 中 / 学習 active 中 (19:40-21:45) 不触发
- demo `TIMEOUT_MS` constant 保留 + `// DEMO 用短縮` 注释

#### ローディング / エラー / 空状態

沿用 demo R3 全局 UX:
- 空状態:「まだデータがありません」+ 薄 icon
- 加载中: spinner
- 错误: 顶 red banner +「再試行」
- 削除/拒否前 confirm modal

### 11.5 状態管理 + 認証

#### Login flow

```
/login/teacher (login_id + password)
  → POST /api/v1/sessions/teacher
  → on success: 拉 teacher info（role + assigned_dorm + name）
  → 按 role 重定向（§11.1）
  → JWT 存 sessionStorage（不 localStorage — F5 恢复、关 Safari 必清登录）
```

> **🟡 CC 假设**: sessionStorage 不 localStorage。理由 = iPad 共用前提下、关 Safari 必清防忘 logout。
> **⏳ §11.9-W3**: 学生 + 教师 login 同 `/login` vs 分两路？CC 推奨 = **分两路**（`/login/student` + `/login/teacher`、学生主入口は iOS App、Web 学生 login は備用）。

#### Token 管理

- access_token 24h → 失效時自動 refresh
- 401 全局 interceptor → `/login/teacher`
- React Router guard: 未登录路由強制 `/login/teacher`

#### Zustand store

```ts
// auth store
{ teacher: { id, name, role, assigned_dorm }, accessToken, refreshToken }

// rollcall store (active session 時)
{ sessionId, board: { studentId → status }, ws: WebSocket }

// applications store
{ pendingForMe: [...], filter: { status } }
```

### 11.6 路由 → API 調用映射

> UI layout / sections / 列名 / state machine は本档 §5（Round 3 完整設計決策）が真値。本節 = **どの route がどの backend API を叩くか** の対応表のみ。

| Route | API（参 BACKEND_DESIGN_LOG §5）|
|---|---|
| `/login/teacher` | `POST /api/v1/sessions/teacher` |
| `/applications` | `GET /api/v1/applications/pending-for-me` + `GET /api/v1/applications` + Q params (filter) |
| `/applications/:id` | `GET /api/v1/applications/:id`; `POST /api/v1/applications/:id/approvals`; `POST /api/v1/applications/:id/comments` |
| `/study` | `GET /api/v1/study/today/attendees`; `POST /api/v1/study/checkins`; `PATCH /api/v1/study/checkins/:id`; `POST /api/v1/study/checkins/bulk-finalize`; `WS /ws/study/{date}` |
| `/rollcall` | `GET /api/v1/rollcall/today/sessions` |
| `/rollcall/sessions/:id` | `GET .../board`; `POST .../start`; `POST .../end`; `POST .../checkins`; `PATCH /api/v1/rollcall/events/:id`; `WS /ws/rollcall/{session_id}` |
| `/rollcall/sessions/:id/summary` | `GET /api/v1/rollcall/sessions/:id/summary` |
| `/logout` | `DELETE /api/v1/sessions/current` |

### 11.7 共通 Component（demo R3 から升级）

- `<Shell>` — 教師独自 login / 全教師に全メニュー表示（旧 role-based filter は撤回）/ 担当寮 badge / logout button / Tomoshibi logo / dynamic browser title
- `<DormSwitch>` — PC 上方 dropdown（assigned_dorm IS NULL の役职のみ表示 / 操作）
- `<ApprovalChain>` — 4 役职行 cards 組件
- `<SeatGrid>` — demo `live-roll-call.jsx` 沿用 + R4 dorm 自動 filter
- `<ConfirmModal>` — iPad ★ 大 button 大文字版（R2 一本道用）

### 11.8 テスト + ビルド

#### テスト

- Vitest + React Testing Library
- 必須 case:
  - 役职が自分のロール行のみ操作可
  - 留学生 + 外泊届 → 4 役职 chain 全表示 / 非留学生 → 2 役职
  - iPad ★ R2 抽查: `/study` 不存在 dropdown / active session 中 idle 不退出
  - R4: 男寮教師 login → 4 寮学生不見える
  - 改判 reason 空 → button disabled
  - WebSocket disconnect → 「再接続中」banner
- E2E (Playwright): 「役职 login → 承認 → 学生通知 → ログアウト」一周

#### ビルド / 部署

- `pnpm build` → `dist/` static
- nginx 配信 + `/api` → backend reverse proxy
- iPad Safari (iPadOS 17+) 動作確認必須
- ENV: `VITE_API_BASE_URL` / `VITE_WS_BASE_URL`

### 11.9 待 itsuki 拍板（P0 阻塞）

> **2026-04-30 進捗**：W1-W8 全部拍板。**残** = W9（实物表対応の動的 chain UI — backend D11 担任データモデル待ち）。

| ID | 決策 | 状态 |
|---|---|---|
| **W1** | ~~demo R3 → v1 升级 TS+Zustand+Vite~~ | ❌ **5-26 整体废弃** — Vite 实装版做到 5-26 被 itsuki 拍板「不是我的 web」归档（详见 §12），回到 Ryō standalone 主线 |
| **W2** | i18n（英 / 中） | ✅ **否**（教师全部日本人） |
| **W3** | login 同路 vs 分两路 | ✅ **分两路**（`/login/student` + `/login/teacher`） |
| **W4** | 役职 dorm filter 範囲 | ✅ **跨寮役职 = 全件 / 寮監・学習担当 = 自寮のみ** |
| **W5** | logout sessionStorage clear vs backend revoke | ✅ **両方**（frontend clear + backend `DELETE /sessions/current`） |
| **W6** | iPad ★ 自动退出 active 中例外 | ✅ **両方 active 中例外**（点呼・学習中は退出 timer 停止） |
| **W7** | RYO theme tokens 直接復用 | ✅ **復用**（demo 安定 + AC 叙事「同じデザイン言語で全システム」） |
| **W8** | 外泊届 modal layout | ✅ **縦 1 列 cards**（iPad 縦持ち + 5 行 chain で縦のほうが自然） |
| **W9** | **外泊届承认 chain 实物表対応**（2026-04-30 D4 から）| ⏳ 役职 cards を `student.is_overseas` + `application.kind` で動的生成（一般 = 3 行 / 留学生 = 5 行）。「担任」cards = `student.homeroom_teacher_id` 解决（backend D11 待）|

### 11.9.1 学生登録コードパネル（2026-05-03 itsuki 拍板）

**⚠ 権威源は `02_design/system_features.md §7.16`。本節は教師 Web 側の UI 実装仕様のみ。**

#### 動機

App Store 上架 = 全人類に配布チャネル開放。**「ダウンロードは公開、登録はゲート」** に分離するために、教師が発行した 6 桁コードを学生が登録最終 step で入れる。

#### ルート

```
/admin/registration-code     ★ 学生登録コード生成パネル（寮務管理権限）
```

寮務管理権限を持つ教師のサイドバー（または「寮務」セクション）にリンク追加：「学生登録コード」。

#### UI レイアウト（v1 React 実装）

縦 1 カラム、3 ブロック：

```
┌─────────────────────────────────────────────┐
│  学生登録コード                               │
│  App Store 公開後の登録ゲート                 │
└─────────────────────────────────────────────┘

┌─── 現在のコード ─────────────────────────────┐
│                                              │
│        4  8  3  2  7  1                      │  ← 6 桁を 32pt mono で大きく表示
│                                              │
│   有効期限まで残り  04:23                     │  ← カウントダウン（秒単位更新）
│                                              │
│   生成者: 田中 寮務課長                        │
│   生成時刻: 2026-04-15 09:32:14              │
│                                              │
│   [ 新しいコードを生成 ]   [ コードをコピー ]  │
└─────────────────────────────────────────────┘

┌─── 使い方 ─────────────────────────────────┐
│  ① ボタンを押すと新しい 6 桁コードが生成され   │
│     ます（前のコードは即座に無効になります）    │
│  ② 学生にコードを伝達（口頭 / 黒板 / LINE）   │
│  ③ 学生は登録 flow の最終 step でコードを入力 │
│  ④ コードは 5 分間有効です                    │
│  ⑤ 集団登録（新入生説明会など）では同じコード  │
│     で複数人が登録できます                    │
└─────────────────────────────────────────────┘
```

#### コンポーネント仕様

- **コード表示**: 32pt mono フォント、3-3 で半角 space（例 `483 271`）、可読性優先
- **カウントダウン**: 残り秒を `mm:ss` 表示、5 分 → 0 秒で自動「期限切れ — 新しいコードを生成してください」赤文字に切替
- **生成ボタン**:
  - 連打防止：押下後 10 秒は disable + spinner
  - 再生成時 confirm modal「現在のコードを無効化して新しいコードを発行します。よろしいですか?」
- **コピーボタン**: clipboard API、押下後「コピーしました」trans toast 1.5 秒
- **権限**: 寮務管理権限を持たない教師がアクセスすると 403 page

#### State 管理（Zustand）

```ts
interface RegistrationCodeStore {
  current: { code: string; expires_at: string; created_by: string; created_at: string } | null;
  fetchCurrent: () => Promise<void>;
  refresh: () => Promise<void>;  // POST /admin/registration-code/refresh
}
```

- マウント時に `GET /admin/registration-code/current` で取得
- 30 秒間隔で再取得 polling（他教師が再生成した場合の検知）
- カウントダウンは `expires_at` から client side で算出

#### 使用シーン

| 場面 | 操作 |
|---|---|
| 入寮シーズン集団登録（30 人） | 教師が説明会開始時に 1 回生成 → プロジェクター / 黒板に表示 → 全員 5 分以内に登録 |
| 個別後日登録 | 学生が連絡 → 教師が後台でボタン押す → LINE / 口頭で伝達 |
| 誤共有（SNS 流出など） | 教師が再生成ボタン → 古いコード即無効 |

#### v1.0 実装スコープ

| 項目 | v1.0 | 後送り |
|---|---|---|
| パネル基本（生成 / 表示 / カウントダウン）| ✅ | — |
| コピー機能 | ✅ | — |
| 権限 gate（寮務管理のみ）| ✅ | — |
| 履歴 tab（過去コード一覧） | — | v1.1 |
| QR コード表示（学生がスキャン） | — | v1.1 |
| 寮単位ごとに別コード（dorm_unit 別）| — | v1.1 |

### 11.10 P1 / P2 / P3

#### P1
- ● 寮監事務室 出寮者一覧 PC（#22-#27）— 印刷可能 + 編集不可 + 1·2/4 寮分離
- 食堂食数 → 寮務 ダウンロード Excel button (#7)
- iOS BTR の路径 B 表示

#### P2
- 寮務部教師 学生 CRUD (#28-#29)
- 学生個人デ ータ aggregated view (#32)
- 巴士編集 (#11) / 行事編集 (#12)
- リクエスト曲管理（demo R3 community 移植 + 男女寮分け + 古い順）
- 全局検索 + 学生個人デ ータ tap-to-jump (#33 杭田弱点 ⭐)
- 指導歴 (#31) / 事案 (#33)
- accounts.jsx 学生管理 page → role-based access

#### P3
- 規律処分 / 罚则アラート（demo R3 既存）
- 月次集計
- お知らせ / 行事 / バス CMS
- 通知中心
- print 専用 stylesheet / PDF export
- CSV 一括出力

---

## 12. 2026-05-26 Vite 实装版整体废弃 + Ryō polish 试做被回滚

### 12.1 背景

5-02 起 v0.8 立项的 Vite + TypeScript + Zustand + React 18 实装版（`v1/src/App.tsx` + 4 标签页 + `Shell.tsx` + `store/` + `api/client.ts`）做到 5-26 约 3-4 周后，itsuki 主动启动会话「推进 teacher web 开发」+ CC 起 Vite dev server → itsuki 看到屏幕第一反应「这他妈根本不是我的 web 啊」→ 拍板「Vite 实装版垃圾归档，用 B（Ryō）」。

**根因**：5-02 起做的 Vite 实装版是「老师后台 4 标签页」结构（Applications / Study / RollCall / Teachers），跟 itsuki 心里的「Ryō 24 学生座席表 + 实时点呼仪表盘」完全不是同一套东西。两套并存在 `v1/` 1 个月，itsuki 没真打开过 Vite 版 → 直到 5-26 启动 dev server 看到才意识到。

### 12.2 归档动作

13 个 Vite 文件 `git mv` 归档（不在公开仓库）：

| 类别 | 文件 |
|---|---|
| React 实装 | `App.tsx` / `main.tsx` / `components/Shell.tsx` / `pages/Applications.tsx` / `pages/Login.tsx` / `pages/RollCall.tsx` / `pages/Study.tsx` / `pages/Teachers.tsx` / `store/auth.ts` |
| Vite 根入口 | `index.html`（→ 归档为 `vite_root_index.html`） |
| 构建配置 | `package.json` / `package-lock.json` / `vite.config.ts` / `tailwind.config.js` / `postcss.config.js` / `tsconfig.json` / `tsconfig.tsbuildinfo` |

物理删（`.gitignore` 忽略）：`node_modules/`（81 MB）+ `dist/`。

**保留**：`api/client.ts`（后端对接代码，未来 Ryō 接真后端复用） + `_legacy/*.jsx` 14 个 JSX 源 + `vendor/` + `_assets/` + `assets/` + `index.css` + `index.html`（Ryō standalone 主体）。

### 12.3 服务器换装

`v1/开发模式跑.command` + `v1/tomoshibi` CLI 都引用不存在的 `demo_server.py`（一直死链）。本次会话改用 `python3 -m http.server 8787 -d src`（Python 内建静态服务器）。

**副作用** — `demo_server.py` 原本提供：
- POST `/checkin?no=XX` — iPhone 快捷指令 → 服务器 → 浏览器实时点呼
- GET `/events/latest` — 浏览器 1 秒 poll
- GET `/api/server-info` — 自动 LAN IP

退到 Python 内建静态服务器后这 3 个端点失效，**NFC 实时点呼 demo 功能失效**。要恢复需要补写 `demo_server.py`（独立任务，TODO 已加）。

### 12.4 Ryō polish 试做 + 回滚

CC 在 itsuki 选 A（Ryō 框架内 polish）后跑 frontend-design skill，提了「Quiet Luxury Japanese Editorial（克制日式编辑感）」方向：

| 改动 | 改的是 |
|---|---|
| 纸面色 `#f4f5f7` → `#f3efe8`（米白和纸） | body 背景 + RYO.paper token |
| 加 `vermillion #c43d2d`（朱赤色 sharp accent） | RYO 新 token |
| 加 display 字体 Shippori Mincho B1（日式明朝） | RYO 新 token + Google Fonts CDN |
| 升级 shadow 0.04 → 0.07 + 模糊变大 | RYO.shadow1/2/Modal |
| 加 SVG 噪点 + 朱+钴双角微渐变 | body::before 伪元素 |
| 主按钮「点呼を開始」换朱色 | inline style |
| logo「Tomoshibi」用 display 字体（登录页 + Shell） | inline style |
| Stat 数字 mono → display + 38px + tabular-nums | inline style |

**itsuki 看完整体不喜欢** → 一句话「回滚」→ `git checkout 03_dev/teacher_web/v1/src/index.html` 全部退回 4-21 原版。

**CC 工程设计 — 提前承诺「可回滚」**：CC polish 前主动跟 itsuki 说「全部改动在 `index.html` 一个文件里，`git checkout` 一行退回」。这个安全网让 itsuki 敢试。

### 12.5 当前权威源（5-26 后）

| 层 | 文件 |
|---|---|
| Ryō standalone 主体 | `v1/src/index.html`（7774 行，含所有 CSS / JS / 字体 inline） |
| JSX 组件源（如要重新 inline） | `v1/src/components/_legacy/*.jsx` 14 个（命名误导，实际是 Ryō 主源） |
| 后端对接代码（保留未用） | `v1/src/api/client.ts`（auth / applications / announcements / teachers / students / rollcall 6 模块） |
| 字体本地副本 | `v1/src/_assets/` Noto Sans JP + JetBrains Mono woff2 |
| React + Babel 本地副本 | `v1/src/vendor/`（standalone HTML 浏览器端编译 JSX 用） |

### 12.6 怎么打开看效果（itsuki 下次想看）

**方式 A 双击（推荐）**：双击项目根启动脚本（本地保留不公开）→ 同时起后端 8000 + 前端 8787 + 自动开浏览器（原 `v1/开发模式跑.command` 只起前端，5-28 归档）

**方式 B CLI（仅 NFC 演示）**：`cd 03_dev/teacher_web/v1 && ./tomoshibi start`（+ `stop` / `status` / `help`）— 只起前端不起后端，走登录用方式 A

**改完 HTML 想看效果**：浏览器手动刷新 Cmd+R（standalone HTML 没 HMR）

### 12.7 未来设计层 polish 候选方向（如果再起意）

- 单页大改造（B 改成具体一页换风格，不动整体）
- 字体单独换不动颜色（risk 最低）
- 找 itsuki 喜欢的具体参照系 web（比 CC 凭 skill 推风格更可靠）
- 跟 itsuki 一起看几个真实日本教育系统 UI（不同风格）后再选方向

## 13. 出租车预约「タクシー予約」tab 实装 — 2026-06-03

itsuki 拍板出租车预约功能，老师端要「能看到 + 主页防漏看提醒」。`ApplicationsPage` 早预留的「タクシー」tab（原 `SkeletonTabBody` 占位）实装成真列表：

- tab body 改用已验证的 `OutstayList` 组件，数据 = 三种出寮届 adapted apps 合并后筛 `_backend.taxi_reservation_time` 非空
- tab badge = 有出租车预约的 pending 数（红点提醒、防老师漏看）
- 申请详情「日時・移動手段」section 加「タクシー予約」字段（`detail.taxi_reservation_time`，无则「予約なし」）
- 数据直接来自后端 `ApplicationOut.taxi_reservation_time`，`client.js` 透传不用改。`check_jsx` 16 块 0 错误

## 14. オンライン学習 契約書（合同）查看 — 2026-06-04

学生在 iOS 上传契約書照片/PDF，老师要能在学生个人档案页看历史合同。
- 学生档案弹窗加「オンライン学習」tab：列学生历史在线学习申请（期间 + 状态 JP 标签），有合同的行显示「契約書を見る」按钮
- `client.js` 加 `downloadOnlineContract(id, token)`：`fetch` 带 token → blob（普通 `<a>` 链接带不了 Authorization 头，故走 fetch + objectURL）；401 调 `_onUnauthorized` 钩子
- 点按钮：先在点击同步时机 `window.open("", "_blank")` 开空窗口（codex 审出 — await 后再 open 会被浏览器弹窗拦截），再把 blob URL 赋给它；被拦则退化当前页跳转；60 秒后 `revokeObjectURL`
- `check_jsx` 16 块 0 错误

---

## 15. 学年更新 / 番号再設定 — 学生アカウント管理页 + 4/1 提醒 — 2026-06-05

学号每年变 → 学生自设番号（推翻 4-30 老师代改，spec §4.2）。老师网页在「学生アカウント管理」页做老师侧（开闸 + 看进度 + 兜底单件改）：
- `client.js`：旧 `promoteStudents`（`/students/bulk-promote`）换成 `startRenewal`（`/students/renewal-start`）+ `renewalProgress`（`GET /students/renewal-progress`）+ `teacherRenewSeat`（`POST /accounts/{id}/renew-seat`）
- 旧「一括進級」按钮 + 整套 promote modal **改造**成「学年更新を開始」开闸：dry_run 预览「通知 N（中1~高2）/ 卒業 M（高3）」→ 确认执行（`handlePromote*` 内部名沿用、行为换成 startRenewal，少改面）
- 学生列表从平铺 `visible.map` 改成**按 学年→A/B 组 分组折叠**（`gradeClassGroups` useMemo + `collapsedGroups`），组标题显示人数 + 「未更新 N」badge
- 顶部进度横幅（`renewalProgress.pending_count > 0` 时显示总未更新数）
- `AccountDetailModal` 加「学籍番号（学年更新の補助）」编辑区：学年/组下拉 + 出席番号输入 → `teacherRenewSeat` 单件改（学生不会操作/填错时兜底），撞号弹后端日语提示
- `RollCallLanding`（点呼默认页）4 月（`getMonth()===3`）顶部显示「新学年です…学年更新を開始してください」提醒横幅 + 跳学生管理按钮
- `check_jsx` 16 块 0 错误。⏳ Android 端待别会话对齐

---

## 16. HTML 单文件 → React + TypeScript + Vite 迁移 — 2026-06-05

老师网页从「单个 ~29600 行 `index.html` + 浏览器内 `babel.min.js` 现场把 JSX 编译成 JS + `react.development.js` 开发版」迁到 **React 18 + TypeScript + Vite** 正规模块化工程。itsuki 6-05 拍板「一步到位上 TypeScript」+ 授权「肉眼签收最后我来，其余你都做」。

### 16.1 为什么迁（撤回两个伪约束）

itsuki 纠正 CC 两个错误前提：① 部署目标是**服务器**（多人访问），不是本地一台电脑；② 别拿「itsuki 零基础维护难」当论据——有 AI 辅助维护，维护能力不进权衡。撤回伪约束后，React+Vite 的业界标准 + 首屏快（打包预编译 vs 浏览器现编译 1.2MB）+ AC 价值占上风。选 Vite 不选 Next.js：内部管理后台不需搜索引擎收录，服务器端渲染卖点用不上。

### 16.2 铁律（吸取 5-26 失败教训，已守住）

5-26 上次 Vite 迁移失败不是技术问题，是产品方向错——重做了一套全新 4 标签管理后台，被 itsuki 否决「这他妈根本不是我的 web」。本次铁律：**界面 100% 冻结，逐页原样搬，一个像素不改外观**；样式保持内联 `style` + Ryō 配色（`window.RYO` 迁成 import 的 `theme.ts`，不用 Tailwind）；全局状态用 React 自带 `useState` + Context（不引 Zustand）。chrome 实测 Ryō 配色 / Noto Sans JP 字体 / 灯火图标跟旧版一致。

### 16.3 工程结构（当前权威源 `03_dev/teacher_web/v1/`）

- **入口**：根 `index.html`（14 行，引 `/src/main.tsx`）→ `src/main.tsx`（挂载 + 引 fonts.css/styles.css）→ `src/App.tsx`（鉴权状态 + 路由 switch）→ `src/Shell.tsx`（侧栏 16 菜单 / 4 组归类・全教師表示 + 顶栏）
- **公共层**：`src/theme.ts`（RYO 配色 + 常量 + dormLabel + `API_BASE="/api/v1"`）/ `src/utils.ts`（4 个 JST 日本时间助手）/ `src/api/types.ts`（50+ 后端类型，对齐 `backend/app/schemas.py`）/ `src/api/client.ts`（60+ 接口方法）/ `src/components/shared.tsx`（ConfirmModal/DormBadge/ModalShell/ModalField/ModalFooter/StateBadge）
- **页面/弹窗**：`src/components/` 26 个 `.tsx`（22 页 + 3 弹窗 OverrideModal/OutstayDetailModal/StudentProfileModal + shared）
- **资源**：`src/_assets/`（fonts.css 引用的 .woff2 字体）+ `src/assets/tomoshibi-icon.png`
- **配置**：`package.json`（build = `tsc --noEmit && vite build`）/ `vite.config.ts`（`base:"./"` + proxy /api→8000 + `resolve.extensions` .ts 优先）/ `tsconfig.json`
- **迁移映射**：`window.RYO`→`import { RYO } from theme`；`window.tomoshibiApi`→`import { api } from api/client`；`window.XxxPage`→各组件 import；旧 `client.js`(IIFE 挂 window) 拆成 `client.ts`(有 export) + `types.ts`(类型)；`React.useState` 原样保留；JSX + 内联 style 逐字搬；注释改中文，UI 字符串保持日语

### 16.4 验证（chrome 客观实测 + 后端测试）

- `npm run build`：0 报错（tsc 0 + vite build，产物 index js 414KB / css 398KB + 字体）
- chrome 自动化：登录跑通（选老师卡片→输密码→进 app）；17 菜单页全渲染无崩溃；27 个接口请求全 200；控制台 0 报错；代録搜学生(田中 太郎)、点呼板(対象 2 名)、学習出席(名簿 2 人)、出寮者一覧、审批(申請) 全部真数据通
- 后端 311 测试全过

### 16.5 托管 + 归档

- 项目根启动脚本（本地保留不公开）改成 build dist → 后端用 `TEACHER_WEB_DIR=dist` 托管到 `/teacher/` 路径（同源，前端用相对 `/api/v1` 连后端）
- 旧物已归档（不在公开仓库）：旧 `src/index.html`(29629 行源) + `api/client.js`(旧 IIFE) + `vendor/`(浏览器版 react+babel) + 打包脚本 + 33MB 旧自包含产物（双击可看旧版界面做对比）

### 16.6 已知遗留（itsuki 决策）

`RollCallLanding`（点呼默认页）的统计卡 + 趋势图 + 最近セッション表是从旧 `index.html` 原样照搬的硬编码 demo 数据（页面带「DEMO」标记）。忠实迁移保留了它，是否接真后端待 itsuki 拍（属 demo scaffold 范畴）。

### 16.7 剩余

itsuki 双击项目根启动脚本肉眼签收界面跟旧版一致 → 确认后 push（CC 不自动 push）。完整施工记录见 `03_dev/teacher_web/Vite迁移_施工清单.md` §8。

---

**END** — 本档随 Web 设计新决策累积更新。下次重大变动时加一条"时间线"记录 + 对应 section。
