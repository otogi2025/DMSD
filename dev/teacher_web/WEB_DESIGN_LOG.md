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
| 2026-04-21 上午 | [Mac-demo-sprint] 建 demo_4-28/ 需求档 + backend skeleton（`dev/backend/`）|
| 2026-04-21 晚 · 18:09 | [Code-Agent] onboard，写 `teacher_web/DESIGN_BRIEF.md` v1（Claude Design 任务书，4 轮节奏）|
| 2026-04-21 晚 · 稍后 | itsuki："demo 的文件单独放到 demo 文件夹里" → backend + 3 新目录全挪到 `dev/demo_4-28/` |
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
| 2026-04-22 ~ 06-04（多次） | ⚠️ 本时间线在此有断档：4-22 之后到 6-04 的多次推进（backend 接入 / 晩自習出席页 / 出寮者一覧 / 食数导出按钮 / 晩自習名簿 等）未逐条入本表，真值见 git log。 |
| 2026-06-05 | **代録（出寮届）表单页** `ProxyApplicationPage`（杭田五-3「教師用は当日入力可」收尾）：老师替学生补录帰省/外泊/帰国届。① 学生选择器走 `proxyCandidates`（GET /applications/proxy-candidates，按寮边界 + 姓名/学号搜）② 申請种类 3 按钮切换 ③ 共有字段（出寮/帰寮 日期·方法·时刻 + 本人連絡先），交通手段下拉选项与 iOS `ApplyStubs` LEAVE/RETURN_TRANSPORTS 一致 ④ 种类别：帰省理由 + 長期休暇 / 外泊·帰国 同行者+行先+宿泊先（必填≥1）/ 帰国 飞机信息 ⑤ 食事栏按学生 `is_overseas` 切换：留学生填食事不要期间（前端展开成 `[{date,meal}]`，照抄 iOS expandMealsSkip）、日本人显示「自己填食事入力表」提示。提交 `createByTeacher` → POST /applications/by-teacher。导航栏「代録」项限代録 5 角色（`DAIROKU_ROLES_FRONT`）可见。`client.js` 加 `proxyCandidates`+`createByTeacher`。验证 check_jsx 16 块 0 错误。| [Mac-Opus 4.8 1M] CC |
| 2026-06-14 | **公告页 UI 优化**（`InfoPage.tsx`）：① お知らせ展开去重复 —— 展开时头部摘要原地替换为全文（`whiteSpace:pre-wrap`）+ 删展开区冗余全文框，任意时刻只显一份正文（itsuki 反馈「展开后摘要 + 全文重复显示」，原话「后面的内容叠加到前面的内容上面」）② 编辑/新建公告弹窗加大 —— `width` 540→680 + `textarea rows` 6→12 + 外壳改 flex 列 `maxHeight:90vh` + 内容区 `overflowY:auto`（防正文加高把底部按钮顶出小屏）。富文本编辑（字号/粗体细体）itsuki 拍板放后续版本、记 TODO §B。`npm run build` ✓。commit `0fcf5b5`。| [Mac-Opus 4.8 1M] CC |

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
| 左 nav 分组（6-14 追加） | 16 菜单平铺 → **4 组归类**，每组加灰色小标题、高频在上 / 管理项沉底。组划分（具体以 `Shell.tsx` 为真值，下为当前结构）：点呼業務（点呼・点呼記録・出寮者一覧・通知）/ 生活・指導（申請・減点・処分・清掃罰則・事案記録・夜学習出席）/ 情報・発信（お知らせ・バス・コミュニティ管理・フロント業務）/ 管理・設定（学生アカウント管理・学生登録コード・教員アカウント管理・操作履歴）。⚠️『開示申請』已随開示申請機能整删（2026-06-15）、nav 无此项；『晩自習出席→夜学習出席』随用词统一；『代録』不再是独立 nav 项。起因 itsuki 截图反馈「散在一排不美观不直观」。⚠️ §4.2 旧表「7 大类」是 5-26 废弃 Vite 版的笼统旧话、无具体定义，不作数 |
| 菜单可见性（6-14 厘清，单源真值）| **16 项全部对所有登录老师显示**，不按角色 / 职位隐藏任何菜单。敏感功能（教員アカウント管理 / 事案記録 / 操作履歴 等。注：学生登録コード 原在此列，2026-06-14 itsuki 拍板对全权限组 + 演示账号放开、不再被后端拦，已移出 → `design/teacher_permission_v1.md` §5）的增删改由**后端 `require_permission` 按权限组把关**：无权限老师能进页面、但具体操作被后端拦（403）。⚠️ 本档早期多处「某菜单仅 X 権限可見 / role-based nav」（§5.3' 教师管理「仅寮務管理可見」、§7.16 学生登録コード、§4.2 代録限 5 角色 `DAIROKU_ROLES_FRONT` 等）全是「职位退化为纯显示标签」重构**之前**的旧设计，已撤回、不作数 —— 现实以本行为准 |

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

### 5.11 減点・処分 /discipline（旧名 規律・処分，2026-06-15 改名 + 并入「事案記録」标签页）

> 6-15 调整（itsuki 反馈「規律・処分 日语生硬、记录类菜单太多」）：① 菜单名「規律・処分」→「減点・処分」（更贴扣分制实质）；② 原独立菜单「事案記録」并入本页，做成页内标签页（`DisciplinePage` 加 `tab` state："demerit" 減点・処分 /「incidents」事案記録，复用 `IncidentsPage` 组件 `embedded` 模式渲染、隐藏其自带 eyebrow/h1）；侧栏 `incidents` 项 + `App.tsx` case 一并移除；③ 原独立菜单「記録」→「点呼記録」并从「生活・指導」移到「点呼業務」组（它本是点呼出勤历史、非处分）。

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
| /community | 1 tab：リクエスト曲（掲示板 / 忘れ物 / 宅配 / 匿名建議 全已删）| リクエスト曲 数条 |

### 5.15 全局 UX

- 空状态：「まだデータがありません」+ 薄 icon
- 加载中：spinner
- 错误：顶部 red banner +「再試行」
- 承認/却下/削除前 confirm modal（防误操作）
- **面包屑**（topbar 下，深入子页才显示）
- 右下 **「DEMO」amber badge**（prototype 标识）
- Footer 最下: `Tomoshibi v0.1.0-demo`
- 登录页底小字: 同上

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
| Spec 色表权威 | `specs/rollcall/RollCall_Spec.md §4.1` | 5 色 + overlay 黑 |
| Spec 时间窗 | `specs/rollcall/RollCall_Spec.md §5.3` | `window_start / on_time_end / late_end / auto_end_at` |
| Spec 老师时刻表 | `specs/rollcall/RollCall_Spec.md §4.2` | 朝/晚点呼 平日/祝休日 ×普通寮生/部活 |

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

> **⚠ 権威源は `design/system_features.md`**。ここは Web 視点の抜粋 + 実装要件のみ。

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
  - 残り 1 tab：リクエスト曲（掲示板 / 忘れ物 / 宅配 / 匿名建議 全已删 §7.14）
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
2. `DESIGN_BRIEF.md`（已归档 `archive/2026-07-14_公开区过期文件归档/`，历史资料）— 旧的实装状态 + 接口路线 D0-D6 记录，现行真值以本文件为准
3. `v1/README.md` — 怎么打开 / CLI 用法

**当前推进方式**：
- 看效果：双击项目根启动脚本（本地保留不公开，起后端 8000 + 前端 8787 + 自动开浏览器）/ NFC 演示用 `cd v1 && ./tomoshibi start`（仅前端，不起后端）
- 改 UI：编辑 `v1/src/index.html`（standalone HTML，所有 CSS/JS inline）— 改完浏览器 Cmd+R 刷新
- 改 JSX 源后内联：`v1/rebuild.command`（把 `_legacy/*.jsx` 重新内联到 `index.html`）
- 打包单文件 demo：`v1/打包单文件.command`（用 `build_single_file.py` 打包成可携带单 HTML）
- 接真后端：参考 `v1/src/api/client.ts` 已定义的 26 个 endpoint — 内联到 standalone 时需要删 TS 类型导出 + 暴露到 `window.tomoshibiApi` namespace（原详见 DESIGN_BRIEF §6，该文件已归档）

历史归档：原 `round2/` / `round3/` / `handoff/` / `round3_handoff/` 4 个子目录 + Vite + TS 实装版均已归档，不在公开仓库。Round 1-3 历史对话作 AC 素材保留。

---

## 11. v1.0 实装清单（2026-04-30 加）

> **作用**: 给 Web code agent 接手 v1.0 实装的入口章。
> **agent 阅读顺序**（两层结构）:
> 1. **共用层（必读）**: `design/system_features.md` —— 角色 / 数据模型 / §7 14 子节功能矩阵 / R1-R4 / 38 条要件
> 2. **专属层（本档全文）**: 本 LOG §1-§9 = Web 设计决策 + §10 下次会话 quick-start + 本 §11 = 实装层
> 3. **后端 API 契约**: `dev/backend/BACKEND_DESIGN_LOG.md`
> 4. **点呼业務規則**: `specs/rollcall/RollCall_Spec.md`（特に §4 §5 §11）
>
> **決策標記**: ✅ 已定 / 🟡 CC 假设 / ⏳ 待拍板（聚集到 §11.9）

### 11.1 P0 范围 + 角色 → 路由対応

#### P0 角色 → 必有功能

| 角色 | 設備 | P0 必有 |
|---|---|---|
| 寮務部長 / 寮務課長 | 〇 個人 PC（職員室）| 出寮届 一覧 + 承认（#10）+ コメント（#13） |
| 国際交流部長 / 国際交流課長 | 〇 個人 PC | 同上（仅留学生 外泊/帰国 chain） |
| **寮監** | **★ 寮管室 iPad** | 朝/夜点呼（#16-#19）+ 改判（一本道 R2） |
| **学習担当** | **★ 寮管室 iPad** | 晩自習出席（#14-#15）+ 自動判定修正（#20） |
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
- **iPad ★ 例外**: 点呼 session active 中 / 晩自習 active 中 (19:40-21:45) 不触发
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
| **W6** | iPad ★ 自动退出 active 中例外 | ✅ **両方 active 中例外**（点呼・晩自習中は退出 timer 停止） |
| **W7** | RYO theme tokens 直接復用 | ✅ **復用**（demo 安定 + AC 叙事「同じデザイン言語で全システム」） |
| **W8** | 外泊届 modal layout | ✅ **縦 1 列 cards**（iPad 縦持ち + 5 行 chain で縦のほうが自然） |
| **W9** | **外泊届承认 chain 实物表対応**（2026-04-30 D4 から）| ⏳ 役职 cards を `student.is_overseas` + `application.kind` で動的生成（一般 = 3 行 / 留学生 = 5 行）。「担任」cards = `student.homeroom_teacher_id` 解决（backend D11 待）|

### 11.9.1 学生登録コードパネル（2026-05-03 itsuki 拍板）

**⚠ 権威源は `design/system_features.md §7.16`。本節は教師 Web 側の UI 実装仕様のみ。**

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

**itsuki 看完整体不喜欢** → 一句话「回滚」→ `git checkout dev/teacher_web/v1/src/index.html` 全部退回 4-21 原版。

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

**方式 B CLI（仅 NFC 演示）**：`cd dev/teacher_web/v1 && ./tomoshibi start`（+ `stop` / `status` / `help`）— 只起前端不起后端，走登录用方式 A

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

### 16.3 工程结构（当前权威源 `dev/teacher_web/v1/`）

- **入口**：根 `index.html`（14 行，引 `/src/main.tsx`）→ `src/main.tsx`（挂载 + 引 fonts.css/styles.css）→ `src/App.tsx`（鉴权状态 + 路由 switch）→ `src/Shell.tsx`（侧栏 16 菜单 / 4 组归类・全教師表示 + 顶栏）
- **公共层**：`src/theme.ts`（RYO 配色 + 常量 + dormLabel + `API_BASE="/api/v1"`）/ `src/utils.ts`（4 个 JST 日本时间助手）/ `src/api/types.ts`（50+ 后端类型，对齐 `backend/app/schemas.py`）/ `src/api/client.ts`（60+ 接口方法）/ `src/components/shared.tsx`（ConfirmModal/DormBadge/ModalShell/ModalField/ModalFooter/StateBadge）
- **页面/弹窗**：`src/components/` 26 个 `.tsx`（22 页 + 3 弹窗 OverrideModal/OutstayDetailModal/StudentProfileModal + shared）
- **资源**：`src/_assets/`（fonts.css 引用的 .woff2 字体）+ `src/assets/tomoshibi-icon.png`
- **配置**：`package.json`（build = `tsc --noEmit && vite build`）/ `vite.config.ts`（`base:"./"` + proxy /api→8000 + `resolve.extensions` .ts 优先）/ `tsconfig.json`
- **迁移映射**：`window.RYO`→`import { RYO } from theme`；`window.tomoshibiApi`→`import { api } from api/client`；`window.XxxPage`→各组件 import；旧 `client.js`(IIFE 挂 window) 拆成 `client.ts`(有 export) + `types.ts`(类型)；`React.useState` 原样保留；JSX + 内联 style 逐字搬；注释改中文，UI 字符串保持日语

### 16.4 验证（chrome 客观实测 + 后端测试）

- `npm run build`：0 报错（tsc 0 + vite build，产物 index js 414KB / css 398KB + 字体）
- chrome 自动化：登录跑通（选老师卡片→输密码→进 app）；17 菜单页全渲染无崩溃；27 个接口请求全 200；控制台 0 报错；代録搜学生(田中 太郎)、点呼板(対象 2 名)、晩自習出席(名簿 2 人)、出寮者一覧、审批(申請) 全部真数据通
- 后端 311 测试全过

### 16.5 托管 + 归档

- 项目根启动脚本（本地保留不公开）改成 build dist → 后端用 `TEACHER_WEB_DIR=dist` 托管到 `/teacher/` 路径（同源，前端用相对 `/api/v1` 连后端）
- 旧物已归档（不在公开仓库）：旧 `src/index.html`(29629 行源) + `api/client.js`(旧 IIFE) + `vendor/`(浏览器版 react+babel) + 打包脚本 + 33MB 旧自包含产物（双击可看旧版界面做对比）

### 16.6 已知遗留（itsuki 决策）

`RollCallLanding`（点呼默认页）的统计卡 + 趋势图 + 最近セッション表是从旧 `index.html` 原样照搬的硬编码 demo 数据（页面带「DEMO」标记）。忠实迁移保留了它，是否接真后端待 itsuki 拍（属 demo scaffold 范畴）。

### 16.7 剩余

itsuki 双击项目根启动脚本肉眼签收界面跟旧版一致 → 确认后 push（CC 不自动 push）。完整施工记录见 `Vite迁移_施工清单.md` §8（已归档 `archive/2026-07-14_公开区过期文件归档/`）。

## 17. 选学生统一组件 StudentPicker + 宅配件数改造 — 2026-06-15

> 起因：itsuki 2026-06-14 截图反馈フロント業務「宅配通知を追加」弹窗选学生不好用，提出「选学生做成可复用组件、别处也统一用」。同会话 brainstorming 出设计、6-15 实装。

### 17.1 共用组件 StudentPicker（`shared.tsx`）

原来「挑学生」三处各写各的：前台快递自写搜索单选 / 事件记录 `StudentMultiSelect` 多选 / 扣分页根本没有主动搜学生入口（只能从排行榜点）。本次抽一个 `StudentPicker`：

- `mode="single" | "multi"`：单选点一行即选定收起、显示「姓名（部屋号 · 学籍番号）」；多选勾选累加 chip。
- `searchApi: (q, token) => Promise<PickerStudent[]>`：搜索函数由调用方传入 → 适配三个权限不同的后端接口，组件不绑死。**用 ref 存 searchApi**，effect 不依赖它，避免调用方传内联箭头函数每次重渲染触发重拉。
- `autoOpen`：放 modal 里时设 true → 打开即展开列表（itsuki「打开弹窗就直接列出学生，滚动着点，懒得打字；想筛再打字」）。空查询也拉一页（后端返前 ~20 条）。
- 就地展开面板（非 `position:absolute` 浮层），避免被表单 modal 的 overflow 裁掉（沿用原 StudentMultiSelect 的做法）。

### 17.2 三处接入

| 处 | mode | searchApi | 备注 |
|---|---|---|---|
| 前台快递 `DeliveryComposeModal` | single | `searchFrontDeskStudents`（`C_FRONTDESK`）| 见 17.3 |
| 事件记录 `IncidentsPage` | multi | `listStudents`（`C_STUDENT_ACCOUNT`）| 删本地 `StudentMultiSelect`，回填只有 id+name 时 room_no/student_no 填空串占位（chip 只显示 name）|
| 扣分页 `DisciplinePage`（新入口）| single | `searchDemeritStudents`（`C_DEMERIT`）| 见 17.4 |

### 17.3 宅配弹窗改造（`FrontDeskPage`）

- 受取人 → `StudentPicker(single, autoOpen)`。
- 件数 → 步进器（−/数字/＋，下限 1）选 `item_count`，不再靠 description 写「ヤマト 1件」。
- 部屋番号 → 选学生后自动带出其 `room_no`、只读展示。
- 备注 → 改可选（去掉原「配送業者」字段）。
- 列表行 description 列改成显示「N件 + 可选备注」（件数移出 description 后板上仍可见）。

### 17.4 扣分页新入口（`DisciplinePage`）

排行榜上方加「＋ 任意の学生に手動加算」按钮 → 新 `ManualDemeritSearchModal`（StudentPicker single + 减点数 + 理由 一弹窗）。**保留排行榜行的「手動加算」旧入口不动**。新接口 `searchDemeritStudents` 走 `C_DEMERIT` 权限：能扣分的寮監 / 寮務未必有前台权限，复用 front-desk 搜学生接口会把他们锁在外面（详见 BACKEND_DESIGN_LOG 2026-06-15 条 + 后端 §5 约束2）。

### 17.5 验证

`npm run build`（`tsc --noEmit && vite build`）通过。后端段见 BACKEND_DESIGN_LOG 2026-06-15。iOS item_count 显示见 IOS_DESIGN_LOG。

---

## 18. バス拆成独立左栏 + 加便表单简化（2026-06-15，commit `e886e8c`）

> itsuki 截图反馈：「お知らせ・行事カレンダー这两个和バス要分开，巴士独立出来放到左边一栏」+「便名不需要、種類也不需要」+「学生 iOS 右上角看这个 bus 干嘛的，加便时能写、带示例」。

### 18.1 导航拆分（`Shell.tsx`）

- 「情報・発信」组里 `["info","お知らせ・バス"]` 拆成 `["info","お知らせ"]` + 新增 `["bus","バス時刻表"]`（紧跟其后、独立成左栏一项）。`pageLabel` 同步：`info` 改「お知らせ」、加 `bus`「バス時刻表」。

### 18.2 页面拆分（`InfoPage.tsx` / `App.tsx`）

- `InfoPage` 去掉「バス時刻表」tab + 大标题改「お知らせ」，只剩 公告 / 行事カレンダー 两 tab。
- `BusSchedulePanel` 改 `export`，新增导出的 `BusPage`（包一层标题「バス時刻表」+ 28px padding 与 InfoPage 一致）。`App.tsx` 加 `case "bus" → <BusPage>`。

### 18.3 加便表单改造（`BusRouteModal`）

- 去掉「種別」「便名」两栏（后端默认补全，见 BACKEND_DESIGN_LOG 2026-06-15）；`BusRouteFormData` / `toBusRouteCreateIn` 不再传 `kind`/`name`，`valid` 去掉 `name.trim()`。
- 新增「用途・説明（学生に表示）」textarea，带示例 placeholder「例：GW の外泊・帰省・買い物に使える臨時便です。」→ 提交进 `purpose`。学生 iOS 端日期头右上角每天显示一条（见 IOS_DESIGN_LOG）。
- `types.ts`：`BusRoute` 加 `purpose`；`BusRouteCreateIn` 的 `kind`/`name` 改可选 + 加 `purpose`。

### 18.4 验证

`npm run build` 通过。⚠️ 与并发会话（班车 notify_students + 清扫罚扫）共用工作区，全程显式 pathspec / `git add -p` 提交，零污染。

---

## 19. 清掃罰則ページ 重做（2026-06-15，commit `743dfd2`）

罚扫功能 6-10 删除后 2026-06-15 itsuki 拍板重做（推翻删除，详见 `logs/decisions/decision_log.md` 同日）。老师网页段恢复 + 改造：

### 19.1 CleaningPage 恢复 + 改造（`components/CleaningPage.tsx`）

- 恢复旧页骨架：顶栏「清掃確認」+「＋ 清掃を割り当て」+ 错误横幅 + 三列卡片网格 + 承認/却下 + 却下理由 modal。
- 改造 3 处对齐重做设计：① 地点 7 选 1 下拉 → **自由文本 input**（老师手输）② 日期 `type="date"` → **`type="datetime-local"`**（精确到点，提交 `new Date(when).toISOString()`）③ 选学生裸 UUID input → 复用 `shared.tsx` 的 `StudentPicker` 单选（searchApi = `searchDemeritStudents`）。
- 前端拦「不能选过去时间」（后端 422 兜底）；卡片 `fmtCleaningWhen` 显示「M月D日 H時mm分」。
- list 口径：`api.listCleaning(token)` **无参**，拉后端所有未审核（assigned/done）安排、按 scheduled_at 升序；副标题「未完了の清掃割り当て一覧」。

### 19.2 DisciplinePage 恢复罚扫名单/列/规则（`components/DisciplinePage.tsx`）

- 恢复「清掃罰則リスト」名单区段：过滤 `is_cleaning_threshold && !is_curfew_threshold`（≥8 分只进禁足名单、不重复标罚扫，对齐「到 8 分不再标罚扫」）。
- 排行表加「清掃まで残り」列（6→7 列网格）+ 减点合计着色 ≥4 红/≥3 黄。
- 规则卡加「清掃罰則の適用 月累計 ≥4 点」徽章。

### 19.3 导航 + 路由 + 接口

- `Shell.tsx`：NAV「生活・指導」组挨 discipline 后加 `["cleaning","清掃罰則"]` + pageLabel。
- `App.tsx`：import `CleaningPage` + switch `case "cleaning"`。
- `api/types.ts`：恢复 `CleaningItem`/`CleaningCreateIn`/`CleaningInspectIn`（scheduled_at:string + area:string）；`DemeritSourceType` 加 `cleaning_failed`；`DisciplineRankingEntry` 加 `is_cleaning_threshold`、`DisciplineRankingOut` 加 `cleaning_threshold_count`。
- `api/client.ts`：恢复 `listCleaning`(无参)/`createCleaning`/`inspectCleaning`。

### 19.4 验证

`npm run build` 通过（tsc 0 错 + vite build）。主会话独立复验。

## 20. 投稿通知開関「学生に通知する」（2026-06-15，§7.13.1，commit `0ebd178`）

老师投稿/编辑 公告 / 巴士便 / 行事カレンダー 时勾「学生に通知する」(notify_students) → 该条进学生 app 通知中心 + 推送(stub)。

### 20.1 改动（`InfoPage.tsx` + `api/types.ts`）
- `types.ts`：`AnnouncementCreateIn` / `EventCreateIn` / `BusRouteCreateIn` 各加 `notify_students?: boolean`（可选，后端缺省 false）。create/update 函数直接转发 body，无需改 `client.ts`。
- 四个投稿弹窗各加「学生に通知する（アプリの通知センターに表示）」勾选框 + 数据流接线：
  - `ComposeNoticeModal`（公告新建）默认勾上(true)；底部「投稿後アプリに通知」固定文案改成**只在勾选时显示**（不勾不该再说"会推送"）。
  - `EditNoticeModal`（公告编辑）默认不勾(false)。
  - `EventComposeModal`（行事，单弹窗 `initial?` 区分）默认 `!initial`，经 `toEventCreateIn` 传。
  - `BusRouteModal`（巴士，`initial` 区分）默认 `!initial`，经 `toBusRouteCreateIn` 传。
- **默认值规则**：新建默认勾 / 编辑默认不勾（改错字不该惊动全员，老师想重新通知再手动勾）。

### 20.2 验证
`npm run build` 通过（tsc 0 错 + vite）。主会话独立核对 4 弹窗 state / 勾选框 / onSubmit 签名 / 提交传值 + 2 映射函数 + 2 数据流 handler 全接上 `notify_students`。

端别：后端 BACKEND_DESIGN_LOG 改订履历 2026-06-15 / iOS IOS_DESIGN_LOG §26。

---

## 21. 操作履歴ページ（操作记录审计）+ 默认页统一为点呼（2026-06-16）

itsuki 2026-06-16 拍板：老师网页要能查看老师做过的操作历史（带精确日期时间 + 做了什么操作）。后端用中间件自动埋点 + 只读端点（详见 `BACKEND_DESIGN_LOG.md §3.7.1`），网页加一个「操作履歴」页展示。

### 21.1 操作履歴ページ `AuditLogPage.tsx`（新建）
- 表格列：日時 / 操作者 / 操作 / 対象 / 詳細（可展开看完整 payload）。
- 「もっと見る」按钮翻页（后端 limit/offset 分页）。
- 无权限时（后端返 403）显示「権限がありません」。
- `action` 键（后端存的「METHOD + 归一化路径」，如 `POST discipline/manual`）经前端映射成日语操作名（如「減点を追加」）；映射未命中则回退显示原始 `action` 字符串。

### 21.2 导航项「操作履歴」（仅管理角色显示）
- `Shell.tsx`：「管理・設定」导航组加「操作履歴」菜单项。该项**仅管理角色可见**（新增 `canViewAuditLog` 属性，由 `App.tsx` 计算后传入），与后端 `C_AUDIT_LOG` 权限组对齐。
  - 这是 §5.5 「16 项全部对所有登录老师显示」规则的一个例外 —— 因为操作履历审计簇对「一般宿管+晚自习」「申請承認専用」两组取 ✕（不可见），故菜单层面也按权限隐藏，而非"全显 + 后端拦"。详见 `design/teacher_permission_v1.md §5` 第 17 簇。
- `App.tsx`：路由 `audit-log` → `AuditLogPage`；`canViewAuditLog` 计算 = `permission_group` 优先（∈ {op, 寮管理者, 一般宿管}），为空时按职位回退（∈ {校長, 寮務部長, 寮務課長, 管理係, 寮務一般教師}）。
- `api/client.ts` 加 `getAuditLogs()`；`api/types.ts` 加 `AuditLogEntry` / `AuditLogListOut`。

### 21.3 登录后默认页统一为「点呼」（同一需求附带改动）
- `App.tsx` 的 `_roleHomePage` 改成永远返回 `"roll-call"` —— itsuki 拍板登录后默认页统一为「点呼」。
- 原逻辑按角色分流（管理角色 → 申請 / 学習担当 → 晩自習 / 其他 → 点呼），现取消分流、所有老师登录后一律落到点呼页。

端别：后端 BACKEND_DESIGN_LOG 改订履历 2026-06-16 / 权限矩阵 `design/teacher_permission_v1.md §5` 第 17 簇 + §12。

## 22. v1.1 候补死代码登记（2026-06-17 itsuki 拍板「留着+登记」，全量审查 C87）

> v1.0 用户**进不去**、但 v1.1 真要用的骨架。itsuki 拍板**保留不删**，在此登记以免日后审查/他人误当死代码清理。

- **C87 `SelectTeacherScreen.tsx`（整文件约 675 行，当前不可达）** — `App.tsx` 已注释「保留作 v1.1 候补」。它是 v1.1「老师单独给某学生发私信 / 选老师」类功能的界面骨架，v1.0 无任何入口导航到它。**有意保留，非死代码漏删**。确认 v1.1 不用了再删。

> 另：C42 出寮届「差戻」按钮（`OutstayDetailModal.tsx` + `client.ts returnApplication` + `App.tsx onReturn` 接线）由 2026-06-17 并发会话实装（混在其 teacher_web 审查批 commit 中），后端端点见 `BACKEND_DESIGN_LOG.md` 同日履历。

---

## 23. 版本号联动注入 + 系统管理者登录入口（2026-06-18）

### 23.1 版本号不再写死，构建时从 CHANGELOG 注入

登录页脚 `Tomoshibi vX.Y.Z` 原来读 `theme.ts` 里写死的 `APP_VERSION`，每次发版要手动改、结果漂到 v0.23.0（项目已 v0.24.8）。改成机制联动：

- `vite.config.ts` 加 `readAppVersion()` —— 构建 / 启 dev server 时读仓库根 `CHANGELOG.md` 顶部第一条 `## [vX.Y.Z]`，通过 `define` 注入全局常量 `__APP_VERSION__`（类型声明在 `src/vite-env.d.ts`）。
- `theme.ts` 的 `APP_VERSION = __APP_VERSION__`，不再写死。
- 效果：版本号永远跟着 CHANGELOG（单源真值）走，发版重新构建网页即自动同步，杜绝漂移。version-bump 清单第 8 项里 teacher_web 这一处已从「手动同步」转为「自动注入」。

### 23.2 「システム管理者ログイン」单独入口（op 不上墙）

`LoginScreen.tsx` 登录页按 4 个权限组分栏（寮管理者 / 一般宿管 / 一般宿管+夜学習 / 申請承認専用），op 运维账号**不上墙**。新增页脚低调入口「システム管理者ログイン」→ 切到手动登录屏，输 `login_id` + 密码登录（后端 `POST /sessions/teacher` 早已支持 `login_id`，无需改后端）。成功后用返回的老师档案现搭 `PickedTeacher` 交给 App 顶层。配套后端把 op 从 `GET /teachers/public` 列表剔除（见 `BACKEND_DESIGN_LOG`），op 的姓名 / 最后登录时间不再半公开泄露。

---

## 24. 登录选寮 + 临时账户（2026-06-18）

itsuki 截图反馈 + brainstorm 拍板（设计决策见 `decision_log` 2026-06-18）。

### 24.1 登录页改动（`LoginScreen.tsx`）

- **卡片去男/女寮徽章** —— 寮不再绑账户，改登录时选。
- **手动入口文案** `システム管理者ログイン` → **`ログイン`**（itsuki 要求，方便代班老师登临时账户）。
- **密码界面加「今夜の担当」男/女寮选择器**（新 `DormPicker` 子组件）：
  - 点卡片登录：选中老师非「申請承認専用」组才显示，必选才能登录（`cardNeedsDorm`）。承認组不显示（看全部）。
  - 走「ログイン」手动登录：登录前不知权限组，**一律显示且必选**；op / 承認账号后端忽略此选择、仍看全部。
- 选的寮经 `api.teacherLogin({ selected_dorm })` 发后端，写进令牌驱动寮过滤（后端 `dorm_units_for_teacher`，见 `BACKEND_DESIGN_LOG`）。

### 24.2 临时账户（`TeachersAdminPage.tsx`）

教員アカウント管理页加「臨時アカウントを追加」按钮（与「新規教員を追加」并列），复用创建弹窗的 `mode="temp"` 模式：
- 表单：氏名 + ログイン ID + メール + 初期パスワード + 功能组（4 选 1，复用 `SELECTABLE_GROUPS`）+ **有効期限**（预设档 今日中 / 3·7·30 日 + 「日時を指定」自定义 `datetime-local`）。临时模式隐藏「担当寮」（登录时现选）。
- 提交把时限算成 `expires_at` ISO 字符串走 `createTeacher`。
- 列表行：临时账户名字后带「臨時」徽章（过期标「期限切れ」红）、担当寮列改显「〜MM/DD HH:mm」到期时刻、过期行文字标红。
- 管理员手动填 ID+密码后口头/微信告诉代班老师，对方走登录页「ログイン」入口登录。

---

## 25. コミュニティ管理页冷冻（2026-07-06）

决策清算会话拍板（决策见 `decision_log_全部` 2026-07-06 决策 7）。该页整页未接后端（社区 + 点歌），挂在活菜单上构成「空头承诺」（6-23 全量审查 TW-003/005）。三选项（排期实装 / 砍掉删码 / 冷冻）itsuki 选冷冻：

- `Shell.tsx` 情報・発信组摘除「コミュニティ管理」菜单项（原位置留注释说明冷冻原因与复活方式）。
- App.tsx 路由、`CommunityPage.tsx` 组件、后端 songs 路由与表**全部保留原样**，版本归属以后定；复活时恢复菜单一行即可。
- 学生 iOS 侧 Community 占位壳（`CommunityStubs.swift`）不在本次范围，未动。

commit `f66b812`，`npm run build` 通过。

---

## 全接口响应信封 {ok,data} 解码接入（2026-07-17，commit `1766b64`，派 cursor grok4.5 施工 + 主会话审查复验）

后端所有成功响应改包一层 `{ok:true,data:...}`、失败响应统一 `{ok:false,error:{code,message,detail}}`（详见 `dev/backend/BACKEND_DESIGN_LOG.md` 同日条 + 契约真值 `specs/API_CONVENTIONS.md` §1）。网页侧只改 `src/api/client.ts` 的 `request<T>`：

- 成功路径：`res.json()` 后判定 `payload.ok===true && "data" in payload` 就解包返回 `payload.data`，否则原样返回（向后兼容尚未信封化的旧路径，虽然本批四端已全改）。
- 失败路径：新信封的校验错误在 `error.detail.errors` 数组；旧形态（`detail` 本身是数组 / `{detail:{code,message}}`）仍识别，取首条 `msg` 显示人话提示（延续 TW-015 那条「别把数组下标当字段拷给老师看」的教训）。

验证：`npm run build` 通过（主会话独立重跑核对，非仅信自报）。无已知 latent。

---

## 适老化设计审查落地：左栏任务型重组 + 小修 6 件（2026-07-17，6 commit）

背景：itsuki 发起「设计逻辑 + 适老化」审查（主用户 = 年长宿舍管理员），对报告 6 项建议拍板（决策记录见 `logs/decisions/decision_log_全部.md` 2026-07-17 条）。本节记实装部分：

- **左栏重组（决策 2，commit `c7e91af`，独立 commit 可 `git revert` 一步回档，itsuki 肉眼验收前不算定稿）**：`Shell.tsx` NAV_GROUPS 从 4 组「系统功能分类」（点呼業務/生活・指導/情報・発信/管理・設定）改 3 组「宿管任务分类」——「今晩の業務」（点呼/夜学習出席/出寮者一覧/申請/通知，每晚必用置顶）/「記録を見る」（点呼記録/減点・処分/清掃罰則）/「管理・設定」（お知らせ/バス時刻表/フロント業務/学生アカウント管理/学生登録コード/教員アカウント管理/操作履歴）。页面本身与路由不动。
- **登录页 3 件（决策 4①②④，commit `40ec56e`）**：`LoginScreen.tsx` ① 寮未选时登录按钮下加「担当の寮を選んでください」提示（原本按钮灰着零解释）② 两处密码框加「表示/隠す」明文切换（盲打 + 3 次锁 30 分钟对年长用户过苛），返回时复位为遮蔽 ④ 底部 op 入口裸链接「ログイン」改「管理者ログイン」。
- **英文标签去除（决策 4③，commit `208ba21`）**：`RollCallLanding.tsx` 开始卡片眉头「SESSION」改「点呼セッション」。同 commit 把 Stat 假数据注释里的「待 itsuki 决策」更新为拍板结果（见下）。注：`LiveRollCall.tsx` 还有一处「LIVE SESSION」不在本次拍板范围，未动。
- **面包屑用词统一（决策 4⑤，commit `d1cca18`）**：`RecordsPage.tsx` 眉头「記録」→「点呼記録」；`StudyAttendancePage.tsx` 眉头首段「夜学習担当」→「夜学習出席」，消除同物两名。
- **空状态指引（决策 4⑥，commit `b755ee8`）**：`StudyAttendancePage.tsx` 出席表 0 名时在「対象学生がいません」下补「名簿管理から対象学生を登録してください」+「名簿管理へ →」跳转按钮（页内切到名簿管理视图）。
- **字号上调（决策 4⑦，commit `9de8322`）**：`Shell.tsx` 左栏导航项 13.5px→15px、组标题 11px→12px。
- **未实装、有拍板归属的**：决策 5 仪表盘双轨数据（demo 账户假数据 / 真账户真数据）待后端统计接口，`RollCallLanding.tsx` 注释已改记拍板结果；决策 3 登录选人页改排列 = itsuki 否决维持现状；决策 6 一页 A4 速查 = 改版验收后写。

验证：每 commit 前后 `npm run build`（tsc + Vite）全过。同日深夜浏览器实走验证完成 — 隔离环境（HEAD 干净工作树 + 8001 端口独立后端，绕开点呼机会话施工现场）实测：新左栏三组渲染正确、登录页①②④与空状态⑥逐一实操生效、信封解码登录链路通；补跑走查同场完成（剩余 10 页 + 一般宿管/申請承認専用低权限视角 + WCAG AA 对比度扫描全过，唯一擦线 = 登录页「習」图标字 4.37:1），新发现 6 条记 `admin/TODO.md` §B 走查小节，12 张截图在 `.scratch/走查截图2026-07-17/`。itsuki 肉眼验收待其本人过目截图。

---

## 2026-07-20 — 「投稿の通報」一覧页（App Store UGC 治理，itsuki 拍板 A 方案）

新组件 `ReportsPage.tsx`，导航挂「管理・設定」组（「バス時刻表」和「フロント業務」之间）。学生 app 通報的互见投稿（「リクエスト曲」「お知らせ返信」「落とし物」）集中处理：未対応/対応済み/すべて筛选；「投稿を削除」按类型分流（song/lost-found 直删、公告回复用 content_parent_id 拼两段路径删）→ 目标已删 404 容忍 → 自动标通報 handled（他师已标 409 容忍）；「問題なし」只标处理完不动投稿。`client.ts` 加 4 函数、`types.ts` 加 `ContentReportOut`、操作履历页 3 个新操作名映射。样式循 RYO token（cobalt 主色 / danger 红），不动冻结的 CommunityPage。每步 `npm run build` 绿。commit `38ca410`。

---

## 2026-07-21 — 审查 S2：老师网页高危 8 条修复（五端 568 条修复计划第 2 场）

三方辩论（Fable 5 主裁 + Opus 4.8 xhigh + grok-4.5-high-fast）两轮定案后 Fable 亲手修，四家终审收口。commit `cab8aeb`（前端）+ `a7357b5`（配套后端摘要字段）。

- **web#0**：`endSession` 末尾恒真 if/else 两分支都弹「保存されました」，把 catch 里的失败警告覆盖掉——加 `endFailed` 门闩，失败时保留警告不弹成功。
- **web#1**：空闲超时登出原来不清点呼 session/学生列表/NFC 计数（对比 401 回调和 logout 都清），再登录会假显「点呼実施中」——补清三项；并让 `startSession` 识别 `ALREADY_RUNNING`（409）直接拉 board 重进 live，否则超时后老师被挡在进行中的场次外面。不调 `rollcallEnd`：结算交给后端调度器（`scheduled_auto_end_at` 非空已核实），前端不替不在场的老师提前记欠席。
- **web#2**：未展开公告直接点「編集」原来用后端 80 字摘要当编辑初始值，保存即把完整正文永久覆盖成摘要——改为缓存未命中先拉全文，拉不到不开弹层，拉取中防连点。
- **web#3**：清扫卡片只显 UUID 前 8 位认不出人——后端 `CleaningAssignmentOut` 加 `student_name/student_no/room_no`（Optional，学生 /me 自查保持 null），前端主显「姓名（房号）+ 学籍番号」。
- **web#4 止血**（条目留 S3 契约族）：删 3 分钟本地「自動遅刻転換」和「遅刻判定開始」倒计时横幅——大屏把未刷卡学生标「遅刻」而后端结算记「欠席」，属对老师说谎；未刷卡保持「未点呼」，横幅改中性经过时间。
- **web#5**：`OverrideModal` 的「承認/却下」是假交互（`approveLeave` 从不调审批接口）且文案假称会推送通知——整块改只读展示 + 指路申请页；`approveLeave` 六处引用一次删齐；顺带消 web#32 硬编码假时间 '19:22'；badge「欠席届」改「申請」（pending 实为外泊申请，来自 WS `outstay_new`）。
- **web#6**：欠席届 inbox 原来只有理由/状態/提出時刻三列信息、拉全历史——表改 7 列补「学生/対象日/期間」（姓名走后端摘要，辩论中 roster/today 前端解析两案都被否——roster 懒加载常空）；拉取改「status=pending 全量 + 対象日=今天」两路各自容错按 id 去重（只拉今天会漏「提前请明天假」；「今天」用后端 `target_date` JST 口径不用浏览器时区）。
- **web#7**：学生检索档案六个区块（点呼 18/2/0、減点 1.0 点、04-21 外泊申請等）全是硬编码假数据、头部却是真实检索结果——生产环境对真实学生展示捏造历史。全部换「データ未接続」诚实占位；同模式的 web#16（账户详情假活动页）属 medium 留 S9。

验证：`npm run build` + `npx tsc --noEmit` 零错误；`approveLeave`/'19:22' 全库 grep 零残留；后端全量 pytest 637 passed。

终审补丁（`d5fba97`）：四家终审两条共同保留意见落地——`theme.ts` 死常量 `LATE_THRESHOLD_SEC` 删除（止血后无引用，注释「迟到自动转换阈值」会误导后来人）+ `ALREADY_RUNNING` 重进场次时经过时间改用后端真实 `started_at`（原来从重进瞬间起算，「経過」显示是错的）。

**审查S3 web#4 契约收口**（2026-07-21）：S2 已止血本地伪 late 转换，本场 `LiveRollCall.tsx` 仅更新过时注释——前端不再本地按阈值判 late（全看后端 board status），说明四端点呼状态语义一致（present/ok=按时 / late=遅刻 / absent=欠席 / exempt=免除 / 未签到=未点呼，无兜底积极态）。web#4 补勾（S2 遗留的契约族条目本场收口）。commit `7ad051f`。

## 2026-07-21 — 审查 S9：老师网页 medium 35 条修复（五端 568 条修复计划第 9 场）

双票复审（grok + opus 背对背只读审）收敛后落地。分组：

**诚实性（假数据/假成功止血）**：web#9 差戻无后端数据不再假报「送信済み」（改诚实提示「デモデータのため保存されません」）；web#16 账户活动页删写死点呼假条目、只留 last_login_at 真登录 + 「未実装（サンプル表示）」横幅；web#17 房号编辑端点未落地、改只读 +「保存未対応」标注（撤掉点了必失败的假保存按钮 + 随之孤儿化的 EditField 组件）；web#40 日期检索删假统计（点呼 23/24 等）改「準備中」占位；web#31 調整履歴假时刻「19:35」改真时刻/「—」；web#33 登录删本地假锁「残り N 回」、真锁只认后端 423。

**逻辑/竞态**：web#8 失败 toast 加 error 红色（原非 ok 一律黄 warn；复审补上 web#9 差戻失败 toast 也改红）；web#11 空闲 25 分警告标志改 ref、活动时复位（原一旦弹过不再弹）；web#12 改判成功回写 lastEventId（原同生二次改判仍走 POST）；web#15 学生列表搜索加 300ms 防抖 + 共享请求号守卫（**复审 grok 抓出**：手动刷新路径原无守卫、与搜索变更交错会盖旧结果——补 reqId 让最后发起者胜）；web#18/23/24 日期一律走 JST（Asia/Tokyo，原 UTC/本地时区日界差一天）；web#21 操作记录加请求号防旧响应覆盖；web#27/28/29 公告详情失败态与加载态分离 + 翻月同步 selected；web#34 登录 403 按 code 给日语说明；web#37/38 代録食事不要期間仅外泊/帰国 + resetForm 防串号；web#39 检索防抖 + cancelled 守卫。

**其它对齐**：web#14 点呼建议日期动态 JST（原写死 04-22/21）；web#19 名单兜底「その他・未分類」不静默丢行；web#20 期限徽章仅外泊 tab；web#22 拉取失败文案与空数据区分；web#25 guidance_records 空值兜底防白屏；web#26/36 竞态守卫 + 错误态重试；web#41 ModalFooter 按钮文案可覆盖（設定/却下）。web#30/#32/#121 现码已修（前序阶段收口，本场核实确认非漏项）。

验证：`npm run build` 零错误。commit 见 git log（S9 场）。

## 2026-07-22 — 审查 S11：老师网页 low 95 条修复（五端 568 条修复计划第 11 场）

8 代理并行只读分类 97 候选 = 95 LIVE / 2 已修 / 0 moot。grok 7 批文件不相交并行下笔 89 条（含从组件定义删死 prop）+ grok 批8 串行做 App.tsx（自身 6 条 + 死 prop 调用方删除 + web#45 假 trend 跨 App/RollCallLanding + web#51 Shell 徽章接线）+ 主控自补 web#109（types.ts 加 is_long_vacation 去 as 断言）。修 93 条，defer 2（web#114 studentCount>1000 理论上限需改 client.ts / web#120 LField-AdminField 去重需新共享模块）。

**分组**：JST 时区（formatJst +9h 平移 getUTC*、formatTime/currentMonth/month/started_at/decidedAt/todayShort/expandMealsSkip 改 Intl Asia/Tokyo，弃浏览器本地 getMonth/getDate）；React 竞态守卫（loadEvents/fetchIncidents/loadItems/copyToast/StudentPicker 加 cancelled/请求号/AbortController）；防双击 in-flight；假数据止血（App.tsx 假 trend 删→RollCallLanding「準備中」占位、FrontDeskPage archived 用 expires_at 真算、DisciplinePage late/absent 恒 0 噪音删）；死 prop（7 组件 + App.tsx 调用方两侧删 teacher/onNav/authToken/dorm）；死码/死分支；日语 UI（LIVE SESSION→リアルタイム点呼、exempt→免除、老師→教師、flow/step→日语等）+ 注释日→中 + 过时职位名单注释→按 canManage/权限组。

**双票对抗复审（grok+opus 背对背只读）异构互补**：opus 抓出 grok 漏的 2 重大（均在 web#51 侧栏「申請」徽章）——W1 `pendingAppsCount` 按 `status==="pending"` 收窄漏掉 `approved_partial`（多级审批链前序批过、仍等本人批的件也算待我审）→改 `backendApplications.length`；W2 web#51 删 Shell 60s 轮询后 App 未补→徽章丢自动刷新，App 加 60s interval 重拉。grok 抓出：ProxyApplicationPage todayStr 本地时区→JST、InfoPage 日历基准日 new Date()→JST、FrontDesk 双击守卫 state→同步 ref、StudentPicker 首开 250ms 闪空态→loadedOnceRef、formatTime 加 hour12:false。次要 defer：IncidentsPage/StudyAttendance 双击守卫用 state（opus 判 disabled 已兜、可接受）。

验证：`npm run build` ✓ built（多轮）。commit `3d72243`（本体）+ `29f0320`（复审）。

## 2026-07-22 — 外出申请「確認 / 却下」页新建（事后确认制老师端，commit `e63c7e4`）

itsuki 拍板外出申请改事后确认制：学生提交即生效可出门，老师这边的操作**只是事后留记录**，不是放行开关。老师端此前完全没有外出页面（后端接口 6-04 就有了，网页一直空着，`admin/TODO.md` 挂了两条），本次一次做全。

**新文件 `OutingsPage.tsx`（793 行）**：列表 + 三态页签筛选（確認待ち / 確認済 / 却下済）+ 详情弹窗 + 确认按钮 + 却下（带理由输入框，理由可以留空）。风格照现有页面：纯 inline style + `theme.ts` 的 `T` 令牌，不引 Tailwind。

**接线 4 处**：`api/client.ts` 加 5 个方法（`outingsForMe` / `outingsPendingForMe` / `getOuting` / `confirmOuting` / `rejectOuting`）；`api/types.ts` 加 `OutingStatus` / `OutingOut`；`App.tsx` 加 `case "outings"`；`Shell.tsx` 左栏加入口；`NotificationsPage.tsx` 的 `NAV_TARGET` 把 outing 类通知指到本页。

**后端要新开一个接口才做得成**：原有的 `pending-for-me` 把 `status == "pending"` 写死在查询里，只出待处理的、看不到历史 —— 三态筛选根本查不出「確認済」和「却下済」。所以后端同批加了 `GET /outings/for-me?status=`，跟 `pending-for-me` 共用同一套演示数据隔离 + R4 寮边界过滤逻辑（见 `BACKEND_DESIGN_LOG.md` §7.7）。

**并发安全靠后端**：确认 / 却下都走后端 `_transition_outing` 的原子条件更新，两个老师同时点同一条时后一个拿 409 `OUTING_NOT_PENDING`，前端照常显示错误即可，不用自己做锁。

验证：`npm run build` 通过（主会话自己跑，不采信子代理自报）。

**当日追加第 4 个页签「取消済」（commit `fc77dd3`，itsuki 拍板 A）**：初版只做了 `pending`/`approved`/`rejected` 三个页签，学生自己撤回的件老师端完全点不进去 —— 页面本身其实是 withdrawn-aware 的（状态徽章「取消済」、详情弹窗「取消時刻」初版就写好了），后端 `for-me` 也支持这个筛选值，唯独少一个页签。顺手把空状态文案从三层嵌套三元表达式改成直接复用 `FILTERS` 里的页签名拼串（以后再加页签不用改那处）。后端补了 `test_for_me_withdrawn_filter` —— 这个页签是 `status=withdrawn` 这个筛选值的第一个真实使用方。

**跨端对齐**：学生端同日改文案（iOS `IOS_DESIGN_LOG.md` §41 / Android `ANDROID_DESIGN_LOG.md` §18）。共用层语义 → `design/system_features.md` §7.2.7。

**上线前审查的收尾修复（commit `553581b`，grok4.5 只读审查发现）**：详情弹窗底部对所有非 `pending` 状态一律写「この申請は既に処理済みです」。但 `withdrawn` 是学生自己按了「取りやめる」，老师根本没经手 —— 从「取消済」页签点进去看到「已处理」，会让老师以为是自己或同事操作过的。改成按状态分流：`withdrawn` 显示「この外出は学生本人が取りやめました」，`approved`/`rejected` 才叫処理済み。同批给 `AuditLogPage.tsx` 的 `ACTION_LABELS` 补上 `PATCH outings/{id}/reject` → 「外出を却下」—— 初版只映射了 confirm，却下记录在操作履历里只显示原始接口路径。

## 2026-07-24 — 申請ページに「オンライン学習」審査 tab 追加（在线学习申请老师审批入口）

grok-4.5 三方对齐审查（前端调用 ↔ 仓库后端 ↔ 洛杉矶线上后端）发现：后端在线学习申请的老师审批接口（`GET /study/online-requests` 待审列表 + `POST /{id}/decision` 承認/却下）早已实装，但老师网页从未接线 —— 学生提交在线学习申请后老师端无处审批（此前只有学生档案弹窗能看状态 + 下合同）。itsuki 拍板：漏做的 bug，接上。

**落点定在申請ページ而非夜学習ページ**：审批权限是 `C_APPROVAL`（申請承認専用，后端 `permissions.py` 注释明写「含在线学习审批」），跟外泊/帰国/帰省同组；夜学習ページ要 `C_STUDY` 权限，放那里负责审批的老师可能进不去。故在 `ApplicationsPage.tsx` 加第 5 个 tab「オンライン学習」（初版误判要放夜学習ページ，查权限体系后纠正）。

**自给自足 tab（不走 backendApplications 统一流）**：在线学习申请数据结构独立（period_from/to、weekly_schedule、契約書），套不进外泊的 `_adaptBackendAppsByKind`。新 tab 自己调 `api.onlineRequests("pending")` 拉列表 + `decideOnlineRequest` 承認/却下，审批后 refetch（端点只回 pending，处理完即从列表消失）；badge 显示待审数。收件箱表格样式照夜学習ページの欠席届一覧。为此给 `ApplicationsPage` 加 `authToken` prop（`App.tsx` 透传）——该页原本纯展示、数据由 App 拉好传入，在线学习是首个自拉自审的 tab。

**后端同批补学生摘要**：`GET /study/online-requests` 原来只回 `student_id`（UUID），老师认不出「谁申请」就得点承認/却下（与 7-21 审查 S2 给欠席届/清扫补 `student_name` 同一动机，当时漏了在线学习，本次补齐）。详见 `BACKEND_DESIGN_LOG.md` 同日条。

验证：`npm run build` ✓ built 803ms（主会话自跑）。

## 2026-07-24 — ロゴアイコン差し替え（単層フレーム → iOS 定制アプリアイコン完成形の静止画）

ログイン画面 / 教員選択画面 / ヘッダー / 点呼大画面の 4 箇所で参照する `src/assets/tomoshibi-icon.png` は、iOS の `AppIcon.icon` パッケージから背景を剥がした「炎」レイヤー単体だった。背景の実塗り渐変を欠くため、縮小表示すると細い水滴のように見えていた。

**差し替え内容**：iOS `AppIcon.icon/icon.json` の確定レシピ（下端 P3(0.46938, 0.80883, 0.87681) の青緑 → 上端 P3(0.85196, 0.95747, 0.96783) の淡青白への垂直渐変、上部 30% は最明色を保持し以降下端へ補間 + 炎レイヤーを拡大して視覚中央へ配置 + 角丸 squircle マスク）を PIL（Python 画像ライブラリ）で 1024×1024 の完成形静止画に合成し置換。P3 → sRGB 変換は線形空間でのマトリクス変換（ガンマ復号 → M 行列 → ガンマ符号化）。

**制約**：iOS のシステムが実時間で描画する液態ガラス（光沢 / 質感）動效は静止画では再現不可。本差し替えは静止画としての還元であり、動效なし。合成スクリプトはセッションの一時ディレクトリ（scratchpad）に置き、リポジトリには入れない。

itsuki 拍板：角丸版（A 案）採用。参照 4 箇所は同一アセットを import しているため一括反映。

検証：`npm run build` ✓ built 769ms（主会話自跑）。

## 2026-07-24 — 点呼「学生からの報告」処理ページ新設（RollCallReportsPage）

grok-4.5 三方对齐审查发现的第 2 处漏接线：学生在点呼时上报的问题（`POST /rollcall/reports`，iOS 点呼界面三个弹窗 = 体調不良 / 当日欠席 / その他）后端早已实装老师侧查看接口（`GET /rollcall/reports` 列表 + `PATCH /rollcall/reports/{id}/resolve` 标记対応済），但老师网页从未接线 —— 学生上报后老师端无处处理。itsuki 拍板「交给你」，接上。

**独立中层页（不进侧边栏）**：新建 `RollCallReportsPage.tsx`，从点呼着陆页（`RollCallLanding`）入口进、点「戻る」回点呼首页，仿 `RollCallSummary` 的中层页模式，不占主导航。着陆页在当日统计卡下方加一条「学生からの報告」入口横条（`onNav("rollcall-reports")`）；`App.tsx` 加 `case "rollcall-reports"`。默认只看未対応、可切「すべて」看历史；表格样式照在线学习收件箱。403 → 提示需「点呼」权限，409（别的老师已先处理）→ 静默 refetch 让它从未対応列表消失。

**后端同批补学生摘要**：`GET /rollcall/reports` 原来只回 `student_id`（UUID），老师认不出「谁上报」。给 `RollCallReportOut` 加 `student_name/student_no/room_no`（`Optional=None`，学生自查 `/reports/mine` 保持 None、老师端点 join Student 填充），旧客户端不受影响。详见 `BACKEND_DESIGN_LOG.md` 同日条。

検証：`npm run build` ✓ built 770ms（主会話自跑）。

## 2026-07-24 — 全面体检修复战役（中危 26 条 + 用语拍板 2 项全量修复）

前置：同日 46 代理全面体检确认高危 1（令牌有效期——itsuki 显式接受不改）+ 中危 27（C21 剔除后实修 26）+ 低危 62。itsuki 拍板中危全修，清单与逐条 commit 对照见 `admin/handoff/teacherweb修复作战_交接_2026-07-24.md`（本地，完成后归档）。修复分五族：

1. **时区族**：所有 `toLocaleString`/`toLocaleTimeString` 显式钉 `timeZone: "Asia/Tokyo"`——服务器/浏览器时区不同时显示漂移；WS 刷卡实时事件与 board 快照抽共用 `_isoToJstHms` 归一口径。
2. **权限门控族**：7 个页面对无 MANAGE 权限的组（主要是「申請承認専用」）隐藏写按钮，对齐后端 `require_permission` 边界——此前按钮可见、点了才 403。
3. **并发/竞态族**：双击双发（setState 异步守卫被穿透 → ref 同步锁）、迟到轮询覆盖新码（请求代次守卫 + bump 时序）、手動加算「排行榜未到时预填 0 提交清零真实扣分」（区分未知与真实 0，未知禁提交）。
4. **WS 鉴权（C20）**：老师 WS 握手不再把 1 年期 JWT 放 query 参数（会落访问日志长期驻留），改为 `POST /sessions/ws-ticket` 换 60 秒 TTL 短时票据。票据为无状态 JWT、无单次消费机制——权衡理由记录于 `ws.py` 校验处。
5. **用语族**：老师界面「学生」→「寮生」（69 处，贴しおり官方称呼）、「代録」→「代理提出」（13 处）、「清掃罰則」→「罰則清掃」词序、帰舎→帰寮、舎監・宿監→寮監、削除確認の「公告」→「お知らせ」。「減点・処分」体系称呼拍板保持不改。

修后三方复审（opus 47 代理 + grok 异构 + 主会话亲验）确认 4 项半修/漏网并当场补修；遗留低危入 `admin/TODO.md`。検証：`tsc --noEmit` 0 错 + `npm run build` 绿 + 后端全量 pytest 绿。

## 2026-08-01 — 上线前审查：3 阻断 + 10 高危全量修复（接生产前最后一关）

前置：三家 AI 背对背审查（Opus 5 四片 / cursor grok-4.5-high 两片 / codex gpt-5.6-sol 全量），去重 33 条。上线口径与既往几场不同——这次是真宿管老师、真高中生数据、跟已上架的 iOS 学生端联动，所以 itsuki 拍板「3 条阻断 + 10 条高危全修」，中低危 20 条入 `admin/TODO.md`。commit `6379d5f`..`17052b9` 共 9 个；生产 nginx 改动不在仓库内（见下）。

**上线致命族（会误伤真实学生数据）**

- **C1**：点呼下拉框 4 个选项里有两个「部活生」，但 `App.tsx` 的 `wantType` 只看名字含不含「朝」，「部活生」被完全忽略——选它启动的是**全寮点呼**，结束时给全寮上百人各记欠席扣 1.0 分。后端 `models.py` 的 `ck` 约束本就只允许 morning/evening，前端却给了第三种语义。删掉两个假选项（部活生单独点呼若现实中真需要，是要改数据库约束+排程器+结算的新功能，已入 TODO）。
- **H5**：手动设定当月合计点的弹窗，预填的是**页面加载那一刻**排行榜快照里的分数，而后端算差值用的是**提交那一刻**现查的分数。老师页面开着不动的几分钟里，晚点呼记欠席、清扫不合格各自自动扣分，老师只改理由点确认 → 后端算出负 delta，**那些自动处罚被静默撤销**，界面还提示设定成功。后端行锁只保护几毫秒的事务，管不了弹窗停在屏幕上的几分钟。两个入口（排行榜行 + 搜学生弹窗）都改为打开时重拉、提交前再核对、失败不回落旧快照（显示错误 + 再試行）、请求带世代号防竞态。
- **C3（后端）**：老师网页时刻输入框发的是无时区串，`database.py` 的 TZDateTime 规则「无时区一律当 UTC」→ 全部行事/巴士时刻偏 +9 小时。改后端而非前端（itsuki 拍板），详见 `BACKEND_DESIGN_LOG.md` 同日条。

**实时链路族（点呼看板从 7-29 上线至今全灰）**

- **C2**：前端连 `wss://teacher.tomoshibi.cc/api/v1/ws/teacher`，落进生产 nginx 的 `location /api/`，那段没有 `Upgrade` / `Connection` 两行 → 握手失败。配置里写对的 `location /ws/` 前端根本不连。新增 `location /api/v1/ws/` 段（nginx 前缀最长优先，自动赢过 `/api/`，不用调顺序），现有 `/ws/` 段保留未动。**这个文件在生产服务器上、不在仓库里**：`/etc/nginx/sites-available/teacher.tomoshibi.cc`，改前备份 `.bak_20260801_ws`。实测证据：同一个握手 curl，reload 前 404（nginx 没当 WebSocket 转发）→ reload 后 403（后端路由收到握手了，只是测试票据是假的）。
- **H10**：Shell 里那条 WebSocket 断线横幅在点呼大屏上是死代码——`App.tsx` 的 `if (liveMode && session)` 分支直接返回 `LiveRollCall`，整个绕过 Shell。而大屏恰恰最依赖实时推送。C2 那个故障持续期间，大屏界面零迹象。`LiveRollCall` 加 `wsStatus` prop 自己渲染一条（字号/圆点比 Shell 那条大一档，大屏离老师远），文案指向「座席を再取得」按钮给老师可执行的下一步。
- **H11**：原来的顺序是「拉快照 → 建连接」，中间空档里学生刷的卡两头都收不到（快照查时还没刷、WS 还没连上推不过来）→ 座席永远停在未点呼；断线重连同理。改为 `onStatus` 收到 `connected`（首连 + 每次重连）触发静默重拉，请求世代号防慢响应覆盖新响应。**配套新增 `_mergeBoardSnapshot`**：board 接口不返回 `pending`/`override`/`health`/`exemptReason`（映射里恒 null），直接覆盖会把 WS 推来的外宿申请徽章、他端调整理由抹掉；且快照请求飞行的几百毫秒里 WS 刚推到的签到，快照是入库前的旧值。合并规则=状态以服务器为准，但快照说 unknown 而本地已有签到时刻时保留本地。`resetLive`（「座席を再取得」按钮）也改走合并——原来老师每按一次就抹一次 WS 累积的徽章。

**诚实性族（界面对老师说谎，S9 web#9/#40 同族的漏网）**

- **H12**：点呼首页 4 张统计卡是硬编码假数字（本日実施 1/2、欠席 2、審査待ち 3、警告 4）+ 假历史行（日期停在 2026-04-20/21），无 demo/真账号分支，真宿管老师登录第一眼看到的就是编的。改「準備中」占位，与同页趋势图（S11 web#45 已改）一致。接真统计接口是后端新功能，入 TODO。
- **H6**：弹窗说「差戻理由は寮生へメールで通知されます」、成功提示说「メール通知送信済み」，但后端 `return_application` 只改状态+写审计，一封邮件都不发。本次只改文案说实话（学生在 app 的申请履历里看退回理由）；后端补发退回邮件要写模板+测发信，上线前不引入新风险，入 TODO。
- **H7**：`approved_partial`（审批链中段承認）也无条件显示「メール通知送信済み」，但后端只在 `status in ("approved","rejected")` 才发信。审批链 4~5 人，前几位每点一次界面都说已通知。改为接住 `decide` 返回的 status 分支文案：中段说「次の承認者の審査待ち（寮生への通知は最終決定後）」，仅终态写已通知。

**权限 / 边界族**

- **H4（后端）**：`incidents.py` 是唯一没有寮过滤的 router，男寮当值老师能读女生事案全文和真名。详见 `BACKEND_DESIGN_LOG.md` 同日条。
- **H9**：登录时选的当班寮后端认（`deps.py` 按令牌 `selected_dorm` 算可见范围），前端却丢了、页面一律用老师档案里固定的 `assigned_dorm`——代班老师（档案男寮、今晚选女寮）看到错性别徽章，查人数时前端按男寮问、后端按女寮答，交集为空返回 0。`LoginScreen` 的 `onLogin` 加第 4 参把选择传出来，`App` 算 `activeDorm` 写进 teacher 状态 + sessionStorage（F5 刷新后仍是当班寮），档案固有寮另存 `profile_dorm`。顺带：`RollCallLanding` 原来传单一寮编号查人数，但后端规定选 1 或 2 可见范围都是 `[1,2]`，「対象 N 名」少算二寮——改成不传条件、交给后端按令牌算。**这条不是「寮边界分角色 A 方案」**（那件归第二波，未动 `deps.py`）。

**流程断点族**

- **H13**：通知中心「点呼報告」类通知跳到 `records`（查历史场次），应跳 `rollcall-reports`（处理学生上报的页）。同时通知已被标已读 → 上报可能永远没人处理。一行改跳转目标。
- **H8**：`OutstayDetailModal` 的承認/却下/差戻 三个按钮没有 in-flight 锁（全文件 grep `acting|busy|submitting|disabled` 输出为空），慢网双击 → 第二次撞 409、界面报保存失败但第一次已成功已发邮件；更糟的是先承認再差戻，两次都合法通过。加 `acting` 锁 + 处理中文案 + 禁用态样式，抄同片已做对的 `OutingsPage` / `StudyAttendancePage` / `ApplicationsPage`。

検証：每条修完 `npm run build` 绿；后端改动由主会话**串行**重跑全量 pytest 663 passed / 1 skipped（子代理并行跑会抢同一份 `test_tomoshibi.db`，出一堆假失败——本场踩到过，判定标准是等并发结束后单独重跑）。

### 第二轮复审：上述修复自身的 6 处缺陷（commit `015284b` / `20fd36a` / `663eb0c` / `8c7c334`）

13 条修完后按流程派 codex gpt-5.6-sol 只读复审，报 0 阻断 / 3 高 / 3 中，主会话逐条读代码核实后**六条全部属实**——其中三条（F3 / F5 / F6）是本轮新写的代码自己引入的，可见「修完即上线」这一步不能省。

- **F1（上线致命）**：`selected_dorm` 进了登录令牌、REST 接口按它算可见范围，但 `POST /sessions/ws-ticket` 换 WebSocket 短时票据时把它丢了，`ws.py` 回落读老师档案里固定的 `assigned_dorm`。后果比 H9 更重——H9 是前端显示错，这条是**服务器按错寮裁广播**：代班老师大屏显示已连接，一条当班寮签到都收不到，反而收到本不该看的另一个寮。修法是 `auth.py` 把 `teacher._selected_dorm` 透传进票据、`ws.py` 读出后走 `deps.dorm_units_for_teacher()` 算可见寮列表，再折回 `ws_manager` 认识的单一寮值（`[1,2,4]`→None 不限制 / `[1,2]`→1 / `[4]`→4）。折回而不是把列表塞进 `_TeacherConn`，是为了不动 ws_manager 字段和 6 个既有广播过滤测试，上线前把改动面锁死在两个文件内；复用 deps 口径顺带修好了 op / 申請承認専用 组走 WS 时按档案寮被误裁的既有问题。**这是「后端有 5 处自己解 JWT 不走 deps 的鉴权入口，改鉴权规则必须逐个覆盖」这条教训的第三次翻车**（前两次：临时账户过期未覆盖 WS、7-18 设备令牌世代校验未覆盖 WS）。详见 `BACKEND_DESIGN_LOG.md` 同日条。
- **F2**：H5 把「打开时的旧快照」换成「提交前现查」，但现查到 POST 到达之间仍有几百毫秒窗口，自动扣分落在其中照样被静默抵消。纯前端补不上——判断和写入必须在同一把锁内。请求体新增可选 `expected_current_points`，后端在行锁内、算 delta 前比对，不一致返回 409 `POINTS_CHANGED` 且一行不写。字段可选，iOS / Android 老客户端行为不变。
- **F3**：H8 加的 in-flight 锁存在弹窗自己的 state 里，请求还在飞时点遮罩或「閉じる」，组件卸载、锁随之消失；待审列表要等第一笔请求返回才刷新，老师能立刻从旧列表重开同一份申请点相反的操作。两笔请求都到后端、后端只让一笔成功，但后返回的失败提示会盖掉先返回的成功提示，老师从界面判断不出最终状态。改为遮罩与关闭按钮统一走 `closeIfIdle()`，处理中不响应。**加锁时只想到「按钮不能连点」，没想到「组件不能被卸载」**——组件级 state 做的锁，其生命周期就是它的作用域上限。
- **F4**：搜学生弹窗在提交飞行中还能换选另一个学生，学生 id 是提交那一刻现取的，分会记到后换的人头上。改为点击瞬间快照 id / 姓名，并在提交期间锁住选人控件。
- **F5**：H11 的静默补拉失败时只写了一行 `console.warn`，注释理由是「连接横幅已经在提示了」——但走到这一步连接状态已是 `connected`、那条横幅根本不渲染。结果断线期间的签到补不回来、屏幕上零异常迹象。新增 `boardSyncFailed` 标记与配套横幅，指向「座席を再取得」。**教训：写「已有别处提示」这类理由时必须验证那个提示在当前状态下真的可见。**
- **F6**：H11 的 `_mergeBoardSnapshot` 对 `pending` / `override` / `health` / `exemptReason` 一律 `old.X ?? f.X`，而这四个字段 board 接口压根不返回，本地一旦挂上就永远清不掉——申请在别的终端批完了，座席仍挂「審査中」，老师按几次刷新都消不掉。这是两难不是纯 bug：改成不保留又会抹掉 WS 刚推来的。折中为合并函数加 `keepLocalMeta` 参数，后台静默补拉保留、老师主动「座席を再取得」以服务器为准清一遍。根治是让 board 接口返回这四个字段（后端新工作，入 `admin/TODO.md`），届时该参数可删。

検証：`npx tsc --noEmit` 0 错 / `npm run build` 绿 / F1 补 4 条 WS 票据回归测试、F2 补 3 条乐观锁测试。两组新测试都做过**反向验证**——把被测代码换回修复前版本重跑，该红的如期变红，确认不是恒绿摆设。

---

**END** — 本档随 Web 设计新决策累积更新。下次重大变动时加一条"时间线"记录 + 对应 section。
