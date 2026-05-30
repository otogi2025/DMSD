# 老师网页 teacher_web → v1.0 上线施工计划

> 目标（itsuki 2026-05-30 下达）：把老师网页 + 后端做到能直接上线 v1.0 的水平。修掉审查的 49 个问题、补齐功能、让 网页 ↔ 后端 ↔ iOS 三边接口对齐能互传信息。做完自审到没 bug，再让 codex 复审，有问题继续修。iOS 当对齐标准，不改 iOS 代码。
>
> 配套审查报告：`05_logs/audit_2026-05-30_teacher_web后端_v1上线审查.md`（49 条确认问题）
> 本计划基于 4 个盘点子任务（后端 / 网页 / iOS 契约 / v1.0 功能要求）2026-05-30 的真实读码结果。

---

## §0 一句话现状

**后端几乎做完了，网页大部分还在用假数据。** 真正的工作量是「把网页接上已有后端 + 修 bug + 补几个真缺的后端 + 删 demo 脚手架」，不是「从零写后端」。

- 后端：16 个路由文件、约 80 个接口全部真实装，10 个数据库迁移脚本，无空桩。
- 网页：`index.html` 单文件 25211 行，17 个页面里只有登录页真接后端，其余多数「真接口 + 假数据备用」或纯假数据。`client.js` 定义 33 个接口函数，**15 个从没被调用**（写操作没接上）。
- iOS：学生 App 的接口约定清晰，snake_case 命名，是后端 + 网页要对齐的标准答案。

---

## §1 现状盘点速查

### 1.1 后端（`03_dev/backend/v1/app/`）— 强

| 路由文件 | 接口数 | 状态 |
|---|---|---|
| auth / accounts / admin_registration_code | 2/1/3 | ✅ 登录 + 注册码全实装 |
| applications（出寮届） | 7 | ✅ 提交/审批/审计全实装；**无 comments 评论接口**（D-05 要） |
| announcements（公告） | 8 | ✅ 列表/详情/发/编辑/删/回复全实装 |
| rollcall（点呼） | 8 | ✅ 开始/结束/签到/board/summary/改判全实装 |
| study（学習） | 8 + 4 | ✅ 出席/欠席届/在线学习全实装 |
| discipline（扣分） | 3 | ✅ 排名/手动/撤销 |
| cleaning / front_desk / dorm_life | 3/4/16 | ✅ 全实装 |
| teachers / meals / notifications | 7/2/1 | ✅ 老师管理 + 食数 Excel + 邮件测试 |
| ws（WebSocket 实时） | 1 | ✅ `/api/v1/ws/teacher`（签到/改判/新届 3 种推送） |

**后端真缺的（无任何接口）**：见 §3.2。

### 1.2 网页（`03_dev/teacher_web/v1/src/`）— 弱

| 页面 | 数据来源 | 待办 |
|---|---|---|
| 登录 / 选老师 | ✅ 真后端 | 已接好 |
| 教师管理 TeachersAdminPage | ✅ 真后端 | 已接好 |
| 点呼 LiveRollCall | 真后端 + 1 秒 poll demo_server | 改走 WebSocket、删 poll |
| 出寮届 ApplicationsPage | 真接口 + 假数据备用 | 删假数据备用、补帰国/帰省/タクシー三个空 tab |
| 学習 StudyAttendancePage | 真接口 + "開発中" 标签 | 删标签、删 demo 限制 |
| 扣分 DisciplinePage | 只读排名 + 内联假数据 | 接手动加分/撤销（client.js 死代码已有） |
| 前台 FrontDeskPage | 只读 + 假数据备用 | 接通知/取走（死代码已有） |
| 清扫 CleaningPage | 只读 + 假数据备用 | 接新建/审核（死代码已有） |
| 公告 InfoPage | 真接口 + 假数据备用 | 接编辑/删除/回复（死代码已有） |
| 记录 RecordsPage | 真接口 + 假数据备用 | 删假数据备用 |
| **搜索 SearchPage** | 纯假数据（本地 roster） | 接真学生检索（需后端？见 §3） |
| **通知 NotificationsPage** | 纯假数据（内联 3 条） | 定义来源（= 公告？还是独立？） |
| **社区 CommunityPage** | 纯假数据（巴士 seed） | = 巴士模块（§3.2 大模块） |
| **账号 AccountsPage** | 纯假数据 window.ACCOUNTS | **后端真缺**（§3.2），密码重置/解锁是空操作 |

### 1.3 iOS 契约要点（不可违反，后端 + 网页对齐它）

- 全部 JSON 字段 **snake_case**（下划线，如 `author_teacher_id`），iOS 用 CodingKeys 映射，后端不能改 camelCase。
- `GET /announcements` 响应必须是 `{"items": [...]}` 包装，不是裸数组（`NetworkModels.swift:270`）。**待核实后端是否已这样返回。**
- `GET /announcements/{id}` 后端自动写已读（副作用），iOS 不发单独已读请求。
- 错误响应两种形态都要支持：`{"detail": "字符串"}` 或 `{"detail": {"code","message"}}`（`APIClient.swift:129`）。**待核实后端实际返回哪种。**
- 出寮届按 `kind`（帰省/外泊/帰国）分校验逻辑。
- 日期 `yyyy-MM-dd` / 时间 `HH:mm:ss` 用 String；datetime 用 ISO 8601。

---

## §2 三边对齐检查项（iOS = 标准）

| # | 对齐项 | 当前状态 | 动作 |
|---|---|---|---|
| AL-1 | WebSocket 路径 | 网页拼成 `/ws/teacher`（丢了 `/api/v1`），后端真实是 `/api/v1/ws/teacher` | 改网页（审查 EP-1） |
| AL-2 | 公告列表响应包装 `{items:[]}` | iOS 要包装，后端待核实 | 核实后端 → 不一致就改后端 |
| AL-3 | 错误响应格式 | iOS 兼容两种，后端待核实统一 | 核实后端 → 统一成 iOS 兼容形态 |
| AL-4 | 字段命名 snake_case | 后端/iOS 一致，网页待核实 | 核实网页解析 key |
| AL-5 | API_BASE 后端地址 | 网页写死 `http://localhost:8000/api/v1` | 改成相对 `/api/v1`（审查 EP-1/RUN-1） |
| AL-6 | 出寮届字段全集 | iOS `ApplicationOut` 28 字段（含 `bus_route_id` 等） | 核实网页 modal 不漏字段、后端返全字段 |

---

## §3 真正的功能缺口

### 3.1 小补丁（后端基本有，网页接上即可）— 在 core 范围内

1. 扣分：手动加分 `createManualDemerit` + 撤销 `revokeDemerit`（死代码，后端有）
2. 改判：`patchRollcallEvent`（死代码，后端有）
3. 清扫：新建 `createCleaning` + 审核 `inspectCleaning`（死代码，后端有）
4. 前台：通知 `notifyFrontDesk` + 取走 `pickupFrontDesk`（死代码，后端有）
5. 公告：编辑 `updateAnnouncement` + 回复 `postAnnouncementReply` + 删回复（死代码，后端有）
6. 出寮届评论 D-05：后端**缺 comments 接口** → 小后端补丁

### 3.2 大模块（后端零接口 + 网页零真 UI）— 需逐个决策 build-now / defer-v1.1

| 模块 | 规格 | 后端 | 网页 | 备注 |
|---|---|---|---|---|
| 学生账号管理（list / 密码重置 / 解锁 / 改学号 / 一括进级） | §7.1 §4.2 | ❌ 无 | 纯假数据 | 密码重置/解锁是**上线必备小后端**；一括进级可延后 |
| 行事予定（学校活动日历，阅览+增改删） | §7.5 | ❌ 无 | 无 | 独立模块，需建表 |
| 巴士时刻表管理 | §7.6 | ❌ 无 | 假 seed | 独立模块，需建表 |
| 指導履歴（学生指导记录 + 开示申请） | §7.9 §7.10 | ❌ 无 | 无 | 独立模块 + 隐私流程 |
| 事案录入（事件记录，富文本+姓名跳转） | §7.9 | ❌ 无 | 无 | 独立模块 |
| 学生个人档案聚合页（出寮/学習/点呼/指导全 tab） | §7.10 | ❌ 无 | 无 | 依赖上面几个 |
| push 推送通知 | §7.13 | ❌ 无（只有邮件） | — | iOS APNs 也是 TODO；R1 规定役职→学生用邮件不是 push，可延后 |
| 出寮者一覧 read-only 打印页 | §7.8 | 可由现有派生 | 无 | 中等 |
| 食堂 iPad 只读 | §7.7 | ✅ 同接口 | 无 | 小 |

---

## §4 审查 49 问题归类

> 详细位置/证据/修法见 `audit_2026-05-30_teacher_web后端_v1上线审查.md` 对应编号。

**后端纯 bug（崩溃/逻辑错，与功能决策无关，最先修）= Wave 1**
- SEC-3 扣分排名漏 `import dorm_units_for_teacher` → 500
- SEC-1 删最后管理员保护漏 `import func` → 500
- SEC-2 老师创建并发去重漏 `import IntegrityError` → 500
- BL-2 点呼手动开始 窗口<5 分钟 → 500
- BL-3 自动结算把外宿/免点呼误判缺席 + 误扣 2 分
- BL-5 今日点呼列表缺日期上界 → 返回未来 session
- BL-6 手动扣分月度归属用 UTC → 跨月凌晨归错月

**生产配置/安全（删脚手架 + 改默认）= Wave 6**
- SEC-4 / SEED-2 / RUN-1：seed.py fallback 密钥 + APP_ENV 默认 dev
- DEMO-1 / EP-5：ShortcutsDemoCard / DemoConsole / demo_server.py / LAN IP

**网页接真后端（消灭假数据）= Wave 3 / 4**
- FE-1 账号管理（后端缺，Wave 5）/ FE-2 宅配失物丢渲染 / FE-3 清扫不渲染 / FE-4 记录搜索写死 / FE-5 多页假名单 / FE-7 15 死代码 / FE-8 扣分只读 / FAKE-1

**三边对齐 = Wave 2**
- EP-1 WebSocket 前缀 / EP-1 API_BASE 写死

**缺失大功能 = Wave 7（决策）**
- EP-6 行事予定+巴士 / EP-7 指導履歴+事案+档案 / EP-8 一括进级 / EP-1 push

---

## §5 施工波次

| 波 | 内容 | 依赖决策 | 风险 |
|---|---|---|---|
| **W1** | 后端纯 bug 7 条（§4 第一组） | 无 | 低，独立 .py 文件 |
| **W2** | 三边对齐 6 项（§2） | 无 | 中，含改后端响应 |
| **W3** | 网页接已有后端（§3.1 第 1-5） | 无 | 中，改 index.html 巨型单文件，**必须串行** |
| **W4** | 4 个纯假数据页（搜索/通知/账号 UI/社区占位） | 部分需决策 | 中 |
| **W5** | 学生账号管理小后端（list/密码重置/解锁）+ 网页接 | 决策：是否本期 | 中，新建接口 + 迁移 |
| **W6** | 删 demo 脚手架 + 生产配置（APP_ENV/API_BASE/seed） | 无 | 低但要全删干净 |
| **W7** | 大模块逐个决策 build-now / defer（§3.2） | **需 itsuki 拍板** | 高，工作量大 |
| **W8** | 自审（多维 review）→ 修 → codex 复审 → 修 → 收敛到 0 bug | 无 | 收尾 |

**index.html 是 25211 行单文件，所有网页改动必须串行做，禁止并行多 agent 同时改（必冲突）。** 后端 .py 改动可并行。

---

## §6 验收闸门

itsuki 定的成果标准：网页 ↔ iOS 功能对齐、后端接口对齐、可互传信息、可直接上线、没 bug。

1. 每波做完：`xcodegen` 不涉及（不碰 iOS）；后端跑 `pytest`（若有测试套件）+ 起服务 smoke test；网页 `npm run build` 通过。
2. W8 自审：多 agent 多维 review（对齐/崩溃/逻辑/安全/生产配置/三边一致），对抗性复核，输出问题清单 → 修到清单空。
3. codex（GPT-5.5 xhigh）独立复审：codex 沙箱能真起 Python 后端跑测试，比审 iOS 那次靠谱。发现问题 → 回到修复循环。
4. 收敛条件：自审 + codex 两轮都 0 新 blocker/major。

---

## §7 范围决策（待 itsuki 拍板，不阻塞 W1-W3）

**推荐：core-first。** 先把每天真用的核心系统（点呼/学習/出寮届/公告/扣分/清扫/前台/账号登录/注册码）做到全真、对齐、0 bug、可上线 —— 这是管理员日常会用的部分。§3.2 的 6 个大模块（行事予定/巴士/指導履歴/事案/个人档案/一括进级/push）逐个决定本期建还是 v1.1，因为它们后端零基础 + 设计细节规格里不全，硬做到「没 bug」需要额外设计决策。

W1（后端纯 bug）+ W2（对齐）+ W3（接已有后端）无论选哪个范围都要做，**先开干，不等决策**。
