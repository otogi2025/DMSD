# 老师 Web — 设计 & 实装状态

> **系统名**：**Tomoshibi**（灯火，2026-04-21 定名）。UI 里的品牌字符串一律 `Tomoshibi`，不用 DMSD。
> **建立**：2026-04-21 by [Code-Agent]（原为 Claude Design 任务书 v1）
> **2026-04-21 晚更新**：Round 2 Claude Design 产出已落盘本目录，itsuki 拍板"就按这个版本来"。
> **2026-05-26 大调整**：Vite + TypeScript 实装版（5-02 立项）废弃归档到 `99_archive/2026-05-26_teacher_web_vite实装作废/`。回到 Ryō standalone 主线。当天跑过一次 `frontend-design` skill polish（米白和纸 / 朱色 / 明朝体）但 itsuki 不喜欢已回滚 — 设计层面回到 4-21 Round 2 原版。
> **权威源**：`v1/src/index.html`（**24041 行** standalone — 5-27 校准，原文档写 7700+ 已严重过时）+ `v1/src/components/_legacy/*.jsx`（14 个 JSX 组件源 — accounts / app / applications / discipline / front-desk / live-roll-call / login / outstay-detail-modal / override-modal / pages-records-search-etc / roll-call-landing / select-teacher / shell / theme — 原文档写 `v1/src/_legacy/` 路径错，实际是 `components/_legacy/`）

---

## 1. 当前状态

Claude Design（claude.ai/design）产出的 Round 2 原型已 handoff + 落盘。itsuki 2026-04-21 晚在 Claude Design 里点了 "Save as standalone HTML: DMSD Round 2 Prototype.html" → 生成 handoff bundle（6.3MB gzip → 9.1MB tar）→ [Code-Agent] 通过 Anthropic 设计分享链接 fetch + 解压 + 导入本目录。

**当前设计方向**：Variation C "涼 (Ryō)" — 近黑 `#14171f` + コバルト `#2b4d8c` accent + Noto Sans JP + 稍圆 8-12px + 极薄 shadow，近 monoxer / modern SaaS but 克制。完整 tokens 见 `v1/src/index.html` 里 inline 的 `window.RYO` 对象（line ~4235） + `v1/src/_legacy/theme.jsx`（源副本）。

**2026-05-26 polish 尝试** — 当天跑过 `frontend-design` skill 提了「Quiet Luxury Japanese Editorial」方向（米白和纸 + 朱色 + 明朝体 + 纹理），itsuki 看完不喜欢已回滚。Polish 内容跟方向论证看 commit 历史 + 5-26 raw log。

## 2. 本目录文件清单（2026-05-27 校准 — 修 5-26 后多处 drift）

```
teacher_web/
├── DESIGN_BRIEF.md                  # 本文件
├── WEB_DESIGN_LOG.md                # Web 専属设计 log
└── v1/                              # 实装目录（standalone HTML + Ryō polish）
    ├── 开发模式跑.command            # 双击 → 起 `python3 -m http.server 8787` + 自动开浏览器（demo_server.py 端点失效）
    ├── tomoshibi                    # CLI（./tomoshibi start | stop | status | rebuild | pack）— start 走 `python3 demo_server.py`（demo_server.py 端点正常）⚠️ 跟 `开发模式跑.command` 不一致
    ├── demo_server.py               # ⭐ 5-27 校准发现真存在 142 行（之前文档写「死链」错）— 3 端点 /api/server-info + POST /checkin + GET /events/latest（iPhone 快捷指令 NFC demo 用）
    ├── 打包单文件.command            # 双击 → 用 build_single_file.py 打包成 demo 携带单文件
    ├── build_single_file.py         # 把 src/index.html + 所有 assets/vendor inline 成单文件
    ├── rebuild.command              # 双击 → 把 components/_legacy/*.jsx 重新内联到 index.html
    ├── README.md                    # v1 实装说明 + 怎么打开
    └── src/
        ├── index.html               # ⭐ Ryō standalone 主入口（**24041 行** — 5-27 校准）
        ├── index.css                # 极简 CSS（大部分样式 inline 在 React 组件里）
        ├── components/
        │   └── _legacy/             # ⭐ 14 个 JSX 组件源（accounts / app / applications / discipline / front-desk / live-roll-call / login / outstay-detail-modal / override-modal / pages-records-search-etc / roll-call-landing / select-teacher / shell / theme）— 5-27 校准发现实际位置是 `components/_legacy/`，原文档写 `_legacy/` 错
        ├── _assets/                 # Noto Sans JP + JetBrains Mono 字体 woff2 本地副本
        ├── assets/                  # tomoshibi-icon.png
        ├── vendor/                  # React 18 + Babel 本地副本（standalone 用）
        └── api/
            ├── client.js            # ⭐ 5-04 后多次扩 — rollcall / discipline / cleaning / front-desk / announcements 5 类 helper（5-27 补 4 个 announcement helper）
            └── client.ts            # 416 行 TS 类型版（5-26 Vite 归档前留下，保留未用）
```

**已归档（2026-05-26 Vite 实装版废弃）**：`99_archive/2026-05-26_teacher_web_vite实装作废/`
- App.tsx / main.tsx / Shell.tsx / pages/ / store/ / vite_root_index.html / package.json + lock / vite.config.ts / tailwind.config.js / postcss.config.js / tsconfig*

## 3. 已实装范围（UI 完成度 ~90%）

权威源 `v1/src/index.html`（standalone HTML，inline 16 个组件源），JSX 源在 `v1/src/components/_legacy/`（14 个 `.jsx`）。

| 区域 | 文件（_legacy/）| UI 状态 | 真接口 |
|---|---|---|---|
| `/login` 共用密码登录 | `login.jsx` LoginScreen | ✅ 5-26 含 3 失败 30s 锁定逻辑 + submitting state | ✅ FC-024 修复后 POST `${API_BASE}/sessions/teacher` 真后端认证 |
| `/login/select-teacher` 选当值老师 | `select-teacher.jsx` | ✅ 含编辑模式（删 + 加老师 + 男女寮分类）| ⏳ 当前从 `window.TEACHERS` 假数据读 |
| Shell（左 nav + topbar）| `shell.jsx` | ✅ 含全局搜索 + WS 指示器 + logout + 切换老师 + 恢复 Live | — |
| `/roll-call` 点呼着陆 | `roll-call-landing.jsx` | ✅ 含 7 天趋势图 + 4 session 类型 + NFC 快速 URL 卡 | ⏳ |
| `/roll-call/live` 实时座席 | `live-roll-call.jsx` | ✅ 含 late 5 色 + 预测条 + demo console + 12 学生 grid + 健康 🏥 overlay + 请假 ❔ overlay | ⏳ |
| 手動調整 modal | `override-modal.jsx` | ✅ 含 pending leave / health report / 调整履歴扩展 | ⏳ |
| `/applications` 申请中心 | `applications.jsx` + `outstay-detail-modal.jsx` | ✅ 外泊完整（list + rule banner + detail modal + 5 sub-tab + 期限计算 + isLateSubmission）/ ⏳ 帰国 / 帰省 / タクシー 3 个 SkeletonTab 占位 | ⏳ |
| `/discipline` 扣分排名 | `discipline.jsx` | ✅ 含 RulePill + 排名 + 罚扫 + 禁足 + 警告リスト + future-alert preview | ⏳ |
| `/records` `/search` `/notifications` | `pages-records-search-etc.jsx` | ✅ 签到历史按日筛 + 按学生/日期搜索 + 通知聚合 | ⏳ |
| `/cleaning` 清掃 | inline CleaningPage | ✅ | ⏳ |
| `/info` 寮内通知 + 行事 | inline InfoPage + EventCalendar + EventComposeModal + ComposeNoticeModal | ✅ | ⏳ |
| `/community` 寮掲示板 + リクエスト曲 | inline CommunityPage | ✅ 含 hashColor / pin / resolve / 匿名建議 | ⏳ 老师公告 client（client.ts）尚未接入 |
| `/front-desk` 宅配 + 忘れ物 | `front-desk.jsx` | ✅ 含 4 数字卡 + DeliveryRow + NotifCard | ⏳ |
| `/accounts` 账号管理 | `accounts.jsx` + AccountDetailModal | ✅ 含详情 modal + 密码重置 + 解锁 + activity mock | ⏳ |
| バス時刻 | inline BusSchedulePanel + BusPostCard + BusEventBlock + BusPostComposeModal | ✅ | ⏳ |

**5-26 大调整后已解决项**：
- ✅ late 黄色 + 迟到阈值已加（`theme.jsx` `late: '#b8871f'` + `window.LATE_THRESHOLD_SEC = 180`）→ 原 §5「Spec 对齐项」作废
- ✅ FC-024 明文密码 `12345678` 已删（commit `b0bed26`）→ LoginScreen 改 fetch backend 真认证

## 4. 未实装范围（v1.0 上线前剩余）

**UI 维度真实剩余 — 3 个 SkeletonTab**（applications.jsx 内）：

- `/applications/return` 帰国 申请 — 当前 SkeletonTabBody，待补 List + Detail + 承認（仿 OutstayList 模式）
- `/applications/home` 帰省 同上
- `/applications/taxi` タクシー 同上

加 itsuki TODO §🛠️ §L「未来设计层 polish 候选方向」4 条（可选，不阻塞上线）。

**真后端接入维度全部待做**（除 Login 5-26 修 FC-024 时已接）：

- 学生 list / state — 当前用 `window.ROSTER_MEN/WOMEN/ALL/ACCOUNTS` 假数据
- 点呼 session — 当前用 React state 不持久化
- 外泊申请 list / 承認 — 当前用 `window.OUTSTAY_APPS` 假数据
- 扣分 / 申请 / 公告 / 宅配 / 账号 等 page 全部待接 `api/client.ts` 已定义的 26 个端点

## 5. v1.0 上线关卡清单（实时状态）

| 关卡 | 状态 | 备注 |
|---|---|---|
| FC-024 删 index.html 明文密码 `12345678` | ✅ 5-26 commit `b0bed26` | LoginScreen 改 fetch `${API_BASE}/sessions/teacher` 真后端，删 demo 提示行 |
| Spec late 黄色 + 迟到阈值 | ✅ theme.jsx 已加 | `LATE_THRESHOLD_SEC = 180`（3 分钟）|
| FC-025/026/027/028 字段对齐 + 权限契约 | ✅ N/A（itsuki 5-26 TODO §🛠️ §L 拍板）| client.ts 没归档 → Task #6 真接口对接时重新审视 |
| 真接口对接（Login 外）| ⏳ 待做 | 工程量大 — 16 个 page 接 backend；分阶段，先 LiveRollCall + Applications 主线 |
| 3 个 SkeletonTab 补完 | ⏳ 待做 | 帰国 / 帰省 / タクシー — 仿 OutstayList 模式 |
| demo_server.py 补回 NFC 实时点呼 | ⏳ 待做（itsuki TODO §🛠️ §L 第 1 条）| 3 个端点 50 行 — demo 用不是 v1.0 上线必需 |

## 6. 真接口对接路线（D3-D6 — Login 已 D0）

D0 = Login 真后端认证（5-26 FC-024 修复时落地，commit `b0bed26`）。

D3-D6 路线（端点引用 backend FastAPI `app/main.py` + `routers/`）：

1. **D3**：`window.seedStudents()` → `fetch('/api/v1/rollcall/sessions/{id}/board')` + `useEffect`；WebSocket `new WebSocket('/ws/teacher')` 收 `checkin / outstay_new / ...` 事件 `setStudents`；点呼開始 → `POST /api/v1/rollcall/sessions/{id}/start`；終了 → `POST /api/v1/rollcall/sessions/{id}/end`
2. **D4**：override modal 保存 → 当前 backend 没有 `PATCH /api/v1/checkins/{id}/override` 单独端点（待补 / 或走 manual checkin 接口）
3. **D5**：3 个 SkeletonTab 补完（帰国 / 帰省 / タクシー — 仿 OutstayList 模式）
4. **D6**：客户端 events 内嵌 axios 风格 helper / 内联 `api/client.ts` 到 standalone

接入方案：不改 `_legacy/*.jsx` 设计源结构，只把数据源从 `window.ROSTER`/`window.OUTSTAY_APPS` 等常量 → `api/client.ts` 已定义的 fetch 调用。所有 UI 保持 pixel fidelity（handoff README 明确要求 "match visual output"）。

`api/client.ts`（416 行）已定义 26 个 endpoint 接口（auth / applications / study / rollcall / teachers / announcements）— 内联到 standalone HTML 时需要：

(a) 删 TS 类型导出（standalone 不编译）
(b) 改 `import("../store/auth").TeacherProfile` 死链（auth.ts 已归档到 99_archive）— 改成 inline type / 或 `window.TeacherProfile`
(c) 暴露到 `window.tomoshibiApi` namespace

## 7. Demo Day 兜底

- 正常：iPad Safari 打开 `http://{Mac IP}:8000/teacher_web/` → 经 FastAPI StaticFiles 挂载 → 加载 index.html
- CDN 断（Google Fonts / unpkg React 不可达）：改打开 `standalone-offline-backup.html` —— 8.4MB 完全内嵌，无外部依赖

## 8. 日语 UI 术语对照表（Round 2 已用词 + 待 Round 3 扩展）

| 中文 | 日语（Round 2 已用） |
|---|---|
| 点呼 | 点呼 |
| 开始 / 结束 | 開始 / 終了 |
| 准时 / 迟到 / 缺席 / 免点呼 / 未签 | 時間内 / 遅刻（Round 3 待加）/ 欠席 / 免除 / 未点呼 |
| 座位表 | 座席表 |
| 手动改判 | 手動調整 |
| 请假申请 | 欠席届 |
| 外宿 / 归国 / 归县 / 出租车 | 外泊 / 帰国 / 帰省 / タクシー |
| 扣分 | 減点 |
| 罚扫 / 禁足 | 清掃罰則 / 外出禁止 |
| 预警 | 警告リスト |
| 开发中 | 開発中 |
| 切换账号 | 切替（左下）|
| 老师 | 先生（Round 2 用 "田中 先生"）|
| 第 X 寮 | 第一寮（Round 2 mock）|

---

## 附录 · 历史（Round 1-2 任务书原文）

Round 1-2 的 Opening Prompt 已被 Claude Design 消化，原文留在 `handoff/chat1.md` 里（作 AC 素材 —— 展示 itsuki 如何引导 AI 设计师迭代出满意结果）。
