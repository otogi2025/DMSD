# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-11（术语表 HTML 学习工具建立 — 180+ 词 / 16 段 / 交互式 + 5-11 MD→HTML 混层方案首个落地试水 + 砍 5-08 点呼机条目保 5 条上限）。早些更新: 2026-05-10 晚（skills 批量装上线）/ 2026-05-10（ac-radar 上线）

> **本文件 = Claude Code 的「当下书签 + 多会话协调」清单。短小为美。**
>
> **职责分工（重要 — 别再重叠）**:
>
> | 文件 | 内容 | 给谁看 |
> |---|---|---|
> | **WIP.md（本文件）** | 当下书签 + 最近 5 次会话 1-2 行总结 + 多会话占用 + 阻塞项 | CC（每次会话开始读全文）|
> | **TODO.md** | **所有未完成事项的完整 backlog**（真值）| itsuki + CC（每次会话开始扫顶部 200 行）|
> | **progress_overview.md** | 长期章节目录（稳定，每次 close 版本时更新）| itsuki + 教授读 |
> | **CHANGELOG.md** | 已发布版本编年史 | 全部读者 |
> | **commit history** | 每次改动的细节 | git log 可查 |
>
> **铁律**：未完成的事**只写在 TODO.md**。本文件**绝不**复述 TODO 的内容。
>
> - **会话开始**: CC 读本文件全文 + `TODO.md` 顶部 200 行 + `git status`
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.8.0 <!-- VERSION_OK -->
**版本 bump 流程**: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权 — 即使 itsuki 说要 bump 但 §2 决策树不命中可以拒绝）

---

## 🎯 当前焦点

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 三端代码层启动完毕，下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-11 by [新Mac-Opus 4.7 1M-主会话 术语表]

**主题**：⭐⭐⭐ 术语表 HTML 学习工具建立 — 5-11 MD→HTML 混层方案首个落地试水 + itsuki 元认知拍板「英文认得 vs 日语会说」分层 + CC 第 1 版静态字典被推翻重写交互式工具 + CC 漏 project-overview 同步被 itsuki 当场抓

- **元认知拍板**：itsuki 区分**英语 = passive recognition（认得）/ 日语 = active production（说出来）**两个学习目标 — "我又没说我要背读法，我就认得出来就好了。日语的话我必须要说出来。" 避免双语都要"会说"的低效路径
- **第 1 版被推翻**：CC 默认建静态字典（130 词 / 9 段），itsuki 一句反问"思考最高效让我达成目标的方式" → CC 反思字典 ≠ 学习工具 → 重写交互式版（180+ 词 / 16 段 / JS 渲染 / localStorage 进度 / 5 条认知科学原则）
- **5 条认知科学原则嵌入工具**：主动回忆 / 间隔重复 / 检索练习 / 交错学习 / 输出>输入 — 顶部展开框 + 测试模式（日语模糊点击揭晓）/ 4 状态标记 / 🎲 随机考我 5 张 / 实时进度面板
- **3 轮迭代覆盖**：v1 130 词 → v2 加 4 段（项目特有/宿舍日语/流程/概念） → v3 加 3 段 ~55 词（后端文件 21 / iOS 文件 29 / UI 代码常见词 20）— 第 3 轮是 itsuki 说"代码文件夹英语单词没背过别忘了"触发
- **CC 漏 project-overview 同步被抓**：CLAUDE.md L86 铁律「新建文件 → project-overview/SKILL.md 同步」CC 没主动跑，itsuki 反问 → CC 承认 + 补 3 处编辑 + 自我反思「下次不等你问」
- **itsuki 验证规则源头**：CC 引用「CLAUDE.md 铁律」时 itsuki 立刻问"是 CLAUDE 还是 skill 要求的" → CC grep 证明真在 L86 → 双层元层验证（执行层 + 规则层）
- **CC 主动修 ID 撞车 bug**：第 1 版 archive / tag 两个 ID 跨分类撞车会污染 mastery 状态 → 重命名 xcode-archive / nfc-tag / git-tag

**5-11 跨会话联动**：早些会话已在 TODO.md 加 §📄「MD → HTML 改造候选清单」拍板混层方案（CC 协作文件保 MD / 人最终读的文件候选 HTML，不强制双写）— 本次术语表.html 是首个落地试水 + TODO 自带「查 HTML skill」元任务等启动

**新规则上线**：
- 文件格式分层（CC 协作 vs 人最终读者）— TODO §📄 已建候选清单 + pandoc 临时渲染策略（要看 HTML 让 CC 渲染到 /tmp/ 永不入 git）
- itsuki 跟 CC 协作的**双层元验证模式** — 不只检查 CC 是否执行规则，还检查 CC 引用的规则真伪

**AC 价值**：⭐⭐⭐ — 模式 5 × 3（英/日认知分层 / 漏同步纠正 / 规则源头验证）+ 模式 2 × 1（CC 第 1 版假设崩→重写）+ 模式 6 × 2（HTML vs MD / 单独背 vs 项目语境化）。详见 `05_logs/raw/2026-05-11.md` 6 条素材深度 dump

**残**：术语表后续 itsuki 用一周后反馈是否真用得起来 / TODO §📄 候选清单 A 元任务（查 HTML skill）+ B 7+ 个候选 HTML 改造文件 / 多 commit 未 push 等 itsuki 拍板统一策略 / 本次 TODO.md modify 是早些会话的 §📄 加段（不是本会话改的，跟本会话 commit 一起带走还是分开等 itsuki 拍板）

### 2026-05-10 晚 by [新Mac-Opus 4.7-主会话 skills 批量装]

**主题**：⭐⭐ 装 15 个 skill（Matt Pocock 6 + Patina 2 + Anthropic 官方 skill-creator + chrome-devtools-mcp 6 子 skill）+ DMSD 外部 skill 体系建立（docs/agents/ 配置层 + CLAUDE.md ## Agent skills 段 + 文档同步点清单 §13）

- **9 skill 调研**：CC WebSearch + WebFetch 5 次整理 3 个来源 — Matt Pocock npx / Anthropic /plugin / Patina curl。/grill-me / TDD / write-a-prd / prd-to-issues 实际名字 to-prd / to-issues / Browser-use 已激活 / Agent-browser 真名 chrome-devtools-mcp（CC 之前给的名字不准 — 自己承认错误后替换）
- **`/setup-matt-pocock-skills` 拍板 B（核心架构决策）⭐⭐⭐**：CC 探索 DMSD 现状发现 Matt Pocock 默认布局（GitHub Issues / docs/adr/ / CONTEXT.md / docs/agents/ 字母目录）跟 DMSD 现有体系（00_admin/TODO.md / 05_logs/decision_log.md / 02_design/system_features.md + 5 端 DESIGN_LOG / 00-99 数字目录）完全错位 → 给 3 选项 → itsuki 选 B「让 skill 服从 DMSD 不双轨」
- **6 处改动落地**：新建 docs/agents/{issue-tracker,triage-labels,domain}.md（prose 映射）+ CLAUDE.md 加 `## Agent skills` 段 + §目录结构 加 docs/agents/ 一行 + 00_admin/文档同步点清单.md 加 §13 + .gitignore 加 .scratch/
- **superpowers 误装 + 卸载**：itsuki 跑 /plugin 装的是 superpowers（第三方 obra）不是 skill-creator（Anthropic 官方）。CC 主动点 superpowers 跟 Matt Pocock 套件 4 处功能重叠（TDD / debug / brainstorming / 写新 skill） + 关键词撞车风险 → itsuki 拍板留 Matt Pocock 卸 superpowers
- **CC 帮删 superpowers manifest**：Edit installed_plugins.json（成功）+ rm -rf cache 被 DMSD pre-bash-destructive-block.sh hook 拦（hook 不认 ~/.claude/plugins/cache/ 是临时路径，要 itsuki 明确授权 — 反映 hook 体系在外部目录上正确触发拦截）→ 让 itsuki 自跑 rm 路径
- **AC 出愿写作 skill**：patina（devswha — AI 写作模式检测中/英/日/韩）= 日语志望理由书核心工具 + patina-max（best-of-N 但要 codex/gemini CLI 才完整发挥）

**新规则上线**：
- 外部工具进入项目时的**归化原则** — 不让项目迁就工具，让工具服从项目（docs/agents/ 体系实战 — CLAUDE.md 仍 single source / docs/agents/*.md 是给 skill 读的快照）
- 文档同步点清单 §13 加「外部 skill 配置」同步点

**AC 价值**：⭐⭐ — 模式 5「skill 装哪儿分层架构理解」（通用工具底层 vs per-repo 配置层）+ 模式 6 × 2（设计决策双轨拒绝 + skill 重叠取舍）+ 工程纪律（先装完再统一 commit 拒绝 git add . 一锅端）。详见 `05_logs/raw/2026-05-10_skills批量装.md`（6 条素材深度 dump）+ 中央 inbox 4 条短 tag

**残**：本次 setup 6 处改动 + 5-08 跨日残（.claude/skills/new-feature/SKILL.md / 06_assets/icons 2 个 icon 删）混着 + 6 commit 未 push 等 itsuki 拍板统一 commit 策略 / superpowers cache 5MB 留着无害等 itsuki 自跑 `rm -rf ~/.claude/plugins/cache/claude-plugins-official/superpowers` 清 / 重启 CC 让当前会话残留的 superpowers 14 子 skill 真正下线

### 2026-05-10 by [Cowork-Opus 4.7-主会话 ac-radar 上线]

**主题**：⭐⭐⭐ 设计并落地全局 `ac-radar` Skill —— 跨 CC 项目的 AC 素材实时捕获层；DMSD/CLAUDE.md 加 ac-radar 钩子；**session-wrap 不动**

- **诉求来源**：itsuki 现有 AC 素材完全靠手动整理 + DMSD session-wrap 收尾扫描，副项目（交易系统等）里 CC 不知道 AC 存在 → 素材会漏。要做一个跨项目的实时雷达
- **设计迭代 5 轮**：从「16 文件理论完美」→ 「按 YAGNI + progressive disclosure 砍到 5 文件」（itsuki 追问「为什么需要这十几份文件 / 这是 skill 启动后会去读吗」推动）
- **Skill 名定 `ac-radar`**（雷达隐喻：一直开扫，发现信号就标）+ **inbox 定 `06_radar_inbox/`**（itsuki 选数字编号连贯方案，不要 CC 提的 90_）
- **核心架构 3 层**：实时打 tag（中央 inbox + DMSD 双写）→ 用户挑（03_素材_候选）→ 用户写（05_产出）。**ac-radar 永远只动最左边**
- **关键拍板**：「直接让 ac-radar 被收尾这个关键词调用，session-wrap 跑它自己的收尾」 → 两个 Skill 并行不互调
- **CC 自决不动 session-wrap**（读了 760 行后判断破坏现成体系不值得）→ 改成"实时层 ac-radar + 收尾层 session-wrap §5.5.1"互补分工
- **5 文件落地**（在 iCloud workspace `_skill_draft_ac-radar/`）：SKILL.md（15 节）/ scripts/ × 3（find_ac_root / startup_check / append_to_scratchpad）/ INSTALL.md
- **DMSD/CLAUDE.md 加段**：⭐ ac-radar 强制加载 + 跟 session-wrap 的分工说明（让下次会话 CC 必读 ac-radar）

**新规则上线**：
- AC 素材层从「session-wrap 独家」升级到「ac-radar 实时 + session-wrap 收尾深度」双层互补
- DMSD raw 文件结构变了 —— 同时含 `## AC 信号 (HH:MM)` 段（ac-radar 写）+ `## HH:MM [类型]` 段（session-wrap §5.5.1 写），互补不冲突
- **session-wrap 完全不动**（CC 自决保护现有体系）

**AC 价值**：⭐⭐⭐ — 模式 5 × 2（progressive disclosure 机制理解 / 两个 skill 并行不互调的设计直觉）+ 模式 6 × 2（inbox 命名取舍 / ~/.claude/ 保护带来的草稿+cp 路线）。详见 `05_logs/raw/2026-05-10.md`

**残**：
- itsuki 还没跑 cp 命令装 ac-radar（INSTALL.md §1 给了一行）
- 全局激活段（~/.claude/CLAUDE.md）还没贴 → 副项目不激活
- 副项目（交易系统等）的 CLAUDE.md 也建议加 ac-radar 钩子段（按需）
- 截止日期表 2026-06-15 募集要项公表后要更新 startup_check.py

### 2026-05-08 凌晨 by [新Mac-Opus 4.7 1M-主会话 reviewer_demo重做]

**主题**：⭐⭐⭐⭐⭐ reviewer demo 方案 review 戳穿 5 bug → itsuki 拍板「修干净再提交」→ 完整重做（v1.0.1 全提前 v1.0.0） <!-- VERSION_OK -->

- **23:30 启动**：itsuki 提「做不做老师 iOS 登录」 → CC 反对老师 iOS（用户量不对等 + 已有 teacher_web）→ itsuki 改「老师下载 app + 体验内容 + 永久注册码」
- **23:45 CC 警告 3 bug**：永久码跟 §7.16 「5 分钟 TTL」铁律冲突 / 上架决策防线被钻洞 / DB 数据污染 → 给 3 替代方案 → itsuki 拍板「demo 账号 + 老师卡在验证码 = 演示注册码门」
- **23:50 itsuki paste VPS CC 已实装方案**：060199/Reviewer-2026/999999 永久码塞 prod DB → 让主 CC 「检查 bug」
- **00:00 review 戳穿 5 bug**：(1) `999999` 4 年永久后门（refresh 一刀切作废 + 6 个 9 太规则） (2) admin 默认密码 `ChangeMe-2026-05` 进 git 历史污点 (3) reviewer 凭证一眼是 demo (4) fork seed 偏离主项目 (5) CC 没让 itsuki 拍板具体值
- **00:15 itsuki 拍板 ⭐⭐⭐**：「**接下来的修复我会全部在这个会话里进行，在修好之前我不会推进别的了**」 → v1.0.1 修理项**全部提前 v1.0.0**，质量优先于发版速度 <!-- VERSION_OK -->
- **01:00-04:30 完整重做（11 文件 / 42 pass）**：
  - schema migration `f6a7b8c9d0e1`（students.is_demo + student_registration_codes.is_reviewer + 内置 UPDATE 把 fork 旧 999999 行自动 invalidate）
  - admin_registration_code.py 3 处改（refresh + current 加 is_reviewer 过滤 + _generate_code 范围 [0,999998] reserved 999999）
  - rollcall.py + applications.py 加 is_demo 过滤（关键判断：accounts 学号查重 / auth.login **不能** 加过滤，否则 reviewer 不能 login）
  - seed.py 重写 `APP_ENV=dev|production` 双模式 + admin 密码移到 env
  - 新 `tests/test_demo_reviewer.py` 5 个 case，**42 passed**（37 原有 + 5 新）
  - 文档同步：system_features §7.20 新章 + §7.16 例外 / BACKEND_DESIGN_LOG §5.x.4 / IOS_DESIGN_LOG §3.16 / TODO §🐛 ledger
  - VPS 部署清单 + Reviewer Notes 双语文案（绝不写注册码）写到 `05_logs/raw/2026-05-08_vps_deploy_steps.md`

**新规则上线**：
- 上架前底线：reviewer 永久码必须有 `is_reviewer=True` schema flag 跟普通 5 分钟 TTL 码并存（spec §7.16 例外条款）
- memory 加 `feedback_cc_picks_value_must_announce_window.md` — CC 自挑值时必须 explicit 告知 + 给打断窗口
- 拍板：「修干净再提交」优先于「冲提交后再修」 — itsuki 引入的 engineering 时间盒新铁律

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2（假设崩→继续→真因，3 层叠加）+ 模式 5（多次：trade-off 语言陷阱 / 修干净拍板 / fork 复发 single source / CC 拍板边界）+ 模式 6（取舍三角 demo 账号方案）+ 多 AI 协作 audit。详见 `05_logs/raw/2026-05-08_reviewer_demo重做.md`

**残**：上架后操作（admin 密码改强密码 + 删 VPS 旧 060199 学生）/ Mac fork 4 部署文件合回主项目（v1.0.1）/ commit + push + VPS 部署待执行 <!-- VERSION_OK -->

### 2026-05-07 → 2026-05-08 by [Mac-主会话 跨日]

**主题**：⭐⭐⭐⭐⭐ **上线 iOS 到 App Store 冲刺**（v0.8.0 期间，提前 G2 决策） <!-- VERSION_OK -->— backend production 部署 GCP VPS + DNS + GH Pages + Apple Dev Portal/ASC/Xcode Archive 全过，卡 Validate Version empty 待修

- **5-07 启动**：itsuki 拍板「公开 App Store + 现在就推」（激进路径，提前 4-19 G2 决策的「v1.0 三端齐发」） <!-- VERSION_OK -->→ CC plan mode 设计完整路径
- **5-07 4 次反转**：itsuki 反 plan 决策（物理 fork 双份 + fork 放 DMSD 外 + NFC 完整保留 + 不声明私域）→ iOS+backend 全 fork 到 `~/dev/Tomoshibi-AppStore/`（DMSD 外，不污染 git）
- **5-07 fork 改动**：project.yml 11 处 / APIClient #if DEBUG / PrivacyInfo.xcprivacy / .entitlements（NFC + Push + Time Sensitive）/ 账号删除（Apple 5.1.1(v) iOS+backend 双端）/ SplashView 启动跳转（双端同步主项目）/ backend seed.py / VPS 部署套件（Dockerfile/docker-compose/Caddyfile/DEPLOY.md）/ METADATA.md / privacy_policy.md
- **5-07 教学失职被纠正**：CC 让 itsuki 勾 NFC 没解释 Capability 是什么 → itsuki 怒怼「我需要你的解释 你不能偷懒」→ TODO 加「教学类 Skill」
- **5-07 撞名**：Tomoshibi 占了 → `Tomoshibi · 灯火` 救场（Bundle ID 没占继续用 com.itsuki.tomoshibi）
- **5-07 VPS 启动**：itsuki 选 GCP $300 trial（不 Vultr）+ asia-northeast1-c e2-small Tokyo + SSH 公钥认证（cat 重用现有 key + GCP metadata）
- **5-08 backend 部署**：VPS CC 找到 3 个隐藏 bug（alembic env.py 不读 DATABASE_URL / docker-compose 不传 APP_ENV → create_all 绕过 alembic / migration 用 SQLite-only batch_alter_table 撞 Postgres 外键）→ Mac fork 同步 4 处修复 + TODO §🐛 v1 backend bug fix
- **5-08 OOM**：e2-small 2GB OOM kill → swap + worker 4→2
- **5-08 GH Pages**：CC 用 gh CLI API 启用绕过手动点 → 双 URL HTTP/2 200
- **5-08 Xcode 链式踩坑**：iOS 26→18 降级 supportsImagePlayground iOS 18.1+ only → 删 → Archive 成功 → Validate CFBundleShortVersionString empty → fork yml 改 MARKETING_VERSION + itsuki Xcode General 直接填 Version/Build
- **5-08 reviewer demo 5 反思**：itsuki 让另一 CC 会话 review → CC 自我反思（不甩锅 VPS CC，责任在我设计）→ TODO §C 跟踪 5 个真问题

**新规则上线**：
- iOS+backend 物理 fork 模式（ad hoc 上架冲刺，不污染主项目 git）
- 教学类 Skill 待做（TODO §🛠️ Meta）
- 主项目 v1 backend 3 bug + reviewer demo 5 缺陷（TODO §🐛 + §C）

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 5（认知改变）× 多 + 模式 2（假设崩→真因 × 3 alembic）+ 模式 6（取舍 × plan 6 决策）+ CC 自我反思（不甩锅）。详见 `05_logs/raw/2026-05-07.md` + `2026-05-08_ios_上架冲刺.md`

**残**：当前卡 Xcode Validate（Version/Build 修后重 Archive）/ 截图 / ASC 元数据 / Submit / push 等 itsuki 明示 / `06_assets/icons/Tomoshibi icon.icon/{Assets/tomoshibi_flame 2.png, icon.json}` 被删（git status 显示，不知是不是 itsuki 自己手动）等拍板 restore 还是接受 / iOS+backend fork 在 DMSD 外不在 git 范围

> **2026-05-04 深夜砍掉 5 条老条目** + **2026-05-06 砍掉 5-03 晚条目（协作模型升级）** + **2026-05-08 砍掉 5-04 上午小条目（已合并到 5-04 主条目）** + **2026-05-08 凌晨砍掉 5-04 主体 / 5-04 晚治理 / 5-04 深夜元层优化 3 条** + **2026-05-10 上午砍掉 5-04 晚 iOS bug 修复条目** + **2026-05-10 晚砍掉 5-06 独立 repo 退役条目** + **2026-05-11 砍掉 5-08 点呼机条目（让 5-11 术语表 + 5-10 晚 skills + 5-10 ac-radar + 5-08 reviewer_demo + 5-07→5-08 跨日 5 条上限；详见 `05_logs/raw/2026-05-08.md`）** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4,6,7,8}.md`

---

## 🤝 多会话占用（避免冲突）

*当前无并行会话占用任何文件。*

> 如启动多会话并行：在此列出谁正在改哪些文件 + 开始时间，其他会话避让。改完登记完成移走。

---

## 🚧 阻塞项

*当前无阻塞项。*

> 阻塞项 = 等 itsuki 答复才能推进的硬卡点（如 Q1/Q2 字段对齐拍板）。无阻塞时本节为空。

---

## 🔒 多会话协调规则

### 会话标识（建议命名）

`[设备-主题]` 格式：`[Mac-主会话]` / `[Mac-mini-Opus 4.7]` / `[Mac-后端]` / `[Mac-iOS]` / `[Mac-Android]` / `[Mac-Web]` / `[Code-Agent]`。

### 避免冲突的硬规则

1. 每个「占用」任务必须标出涉及文件 / 目录
2. 其他会话不能动正在被占用的文件
3. **共享文件**（`CLAUDE.md` / `WIP.md` / `progress_overview.md` / `CHANGELOG.md` / `TODO.md`）：一次只能一个会话改，改完立刻 commit + push
4. 改 `WIP.md` 本身：先 pull，改完立刻 push
5. git conflict：停下来问 itsuki，不自己猜合并

### 关键文件边界

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | Web 会话 |
| `03_dev/device/` | 设备会话（Pi）|
| `01_specs/` | 一次只允许一个会话改（规格冻结区）|
| `00_admin/` | 主会话管理 |
| `05_logs/raw/` | 各会话写自己今天的，文件名不撞 |

---

## 📝 给新会话的上下文（关键信息）

读完 `CLAUDE.md` + 本文件 + `TODO.md` 顶部应该知道：

1. **当前版本**：见上方 + `CHANGELOG.md` 顶部
2. **上线姿态**（4-19 G2 决策）：取消分阶段；v1.0 直接 iOS + Android + 卡 一次上线
3. **防作弊核心**：动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ ECDSA 签名 + 老师监督 + 语音播报（原创设计 → `05_logs/decision_log.md`）
4. **版本体系**：0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**：CC 侧 `00_admin/CLAUDE_CODE_记录指南.md`；总章 `AC入试记录指南_v3.md` 在 iCloud（CC 不读）
6. **文件地图**：`CLAUDE.md §目录结构` + `00_admin/文件结构指南.md`
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策他拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04 上午** — 加 2026-05-04 会话条目（A+B 文件联动工具建设）
- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- **2026-05-10** — 加 ac-radar 上线条目（共 6 条超 5 条上限）→ 砍 5-04 晚 iOS bug 修复条目（详见 raw/2026-05-04_iOS_bug修复.md）
- 更早历史 — 见 `git log -- 00_admin/WIP.md`
