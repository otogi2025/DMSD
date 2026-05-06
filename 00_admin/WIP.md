# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-06（独立 repo 模式退役 — iOS + Android 全合并回 DMSD + GitHub 双独立 repo 删除 + 4 元数据 + sync 脚本归档 + 5 文档同步更新）

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

### 2026-05-06 by [新Mac-Opus 4.7 1M-主会话]

**主题**：⭐⭐⭐ 独立 repo 模式退役 — iOS / Android 全合并回 DMSD + GitHub 双独立 repo 删除

- **背景**：itsuki 在新 Mac（kurekoduki）拉 Mac mini 5-06 push 的 46 commit + v0.8.0 tag → 看到 CC 报告里「iOS 独立 repo」表述 → 问 CC 实情 → 拍板「全部合回 DMSD，github repo 删了，给教授看不能太难看」 <!-- VERSION_OK -->
- **iOS 合并**：DMSD 16578 行 vs Tomoshibi-iOS 5347 行（4-23 后没 push），DMSD 已是 single source，无逆同步
- **Android 合并**：rsync `/tmp/check-android` → `03_dev/student_android/v1/`（85 文件 / 6945 行 Kotlin / 1MB）
- **归档** `99_archive/2026-05-06_cloud_agent_退役/`：4 元数据（STATUS / SHARED_DECISIONS / SESSION_CHANGELOG / REMOTE_AGENT_GUIDE）+ `sync-ios-refs.sh` + iOS / Android 完整 git log + README
- **5 声明性文件改**：CLAUDE.md / 文档同步点清单 / file-linkage SKILL / project-overview SKILL（§0.4 / §5.2 / §5.6 / §6.5 / §8.1 / §9.6 / §10 / §13）/ sync-rules.sh
- **GitHub repo 删**：`otogi2025/Tomoshibi-iOS` + `Tomoshibi-Android`（不可逆，git log 已存档）

**新规则上线**：
- 独立 repo 模式退役 — iOS+Android+Web+后端 全在 DMSD 单一 repo
- CC 收到「现状是什么」类问题时，先 grep/find 实地验证再用 SKILL.md 补充（这次 CC 答歪触发的 lesson）

**AC 价值**：⭐⭐⭐ — 「设计在约束下成立 → 约束变化方案跟着变」13 天试错周期（4-23 → 5-06）；项目文件总览 SKILL §8.1 + AC top 10 #9 都重写为「试错 + 退役迭代」叙事。详见 `05_logs/raw/2026-05-06.md`

**hook 实战拦截**：`pre-bash-destructive-block.sh`（5-04 凌晨加）拦了 `rm -rf 03_dev/student_android/v1/round1_handoff/` — CC 改用 rsync 跳过，让 .DS_Store 垃圾留着（git 看不到不影响）

**残**：~~版本 bump 决策~~ ✅ itsuki 否决「这算个屁的升级，就移动了下结构而已」（raw §7 dump）/ ~~push~~ ✅ commit `1f55643` + `f050c30` 已 push origin main / round1_handoff/ 里 7 个 .DS_Store 垃圾还在（可手动 Finder 删） <!-- VERSION_OK -->

### 2026-05-04 晚 by [Mac-iOS bug 修复 Opus 4.7]

**主题**：⭐⭐⭐⭐ iOS 5 个 bug 修复（2 个真机生产 bug + 1 次 CC 失职被 itsuki 戳穿 + 删 8 处蠢 placeholder）

- **AppIcon Liquid Glass 修复**（4 层失败重诊）— Xcode 26 build error `actool: None of the input catalogs contained... icon stack named "AppIcon"`。**CC 第一次走错方向回退到传统 .appiconset + v2 PNG 替换**，BUILD SUCCEEDED 假装修好 → itsuki 怒戳穿「我现在图标还是白色背景，你到底更新了没？」→ CC 重新诊断（单独跑 actool 隔离 + WebSearch Apple iOS 26 文档）→ 真根因：**Xcode 26 把 `.icon` 当单一文件 reference 处理，不能塞 `.xcassets/` 里**。修：mv `Assets.xcassets/AppIcon.icon` → `TomoshibiApp/AppIcon.icon` + 手改 pbxproj 4 处加 PBXFileReference / PBXBuildFile / PBXGroup / PBXResourcesBuildPhase
- **暗夜模式黑闪修复**（itsuki 真机晚上点页面黑一下）— `TomoshibiApp.swift:20` `.preferredColorScheme(app.isDark ? .dark : nil)` 中 `nil` = **跟随系统**，晚上系统切 dark → SwiftUI 喂 dark color scheme → view 硬编码 light token 双重渲染 → 黑闪。修：强制 `.preferredColorScheme(.light)` + 加 inline 注释标 N18 待实装
- **注册进度 5/4 → 5/5 修复** — `RegisterProgress` 硬编码 totalSteps=4（旧 4 步 JSX 抄来），后加 RegisterStep5 没跟上 → `Text("\(step) / 4")` 改 5，进度条 `* 0.25` → `/ 5.0`
- **删 8 处蠢 placeholder** — itsuki 怒怼「你写的例子太他妈蠢了」→ ApplyStubs × 6 / StayListStubs × 2 / HomeStubs × 1 全删。剧情化（祖父母宅 / 友人の結婚式 / 祖母の通院）→ 中性提示（住所を入力 / 理由を入力）
- **CommunityStubs Text + Text deprecation** — iOS 26 推荐字符串插值嵌套 Text

**新规则上线**：
- memory `feedback_no_dramatic_placeholder.md` — UI placeholder 禁用剧情化例子（demo prototype 抄到生产时必删「例：xxx」）
- memory `feedback_dont_unilaterally_revert_design.md` — CC 修 build error 不能私自回退 itsuki 主动选的新格式（先诊断根因 / 不通就报告等拍板，不能 fallback 伪装 BUILD SUCCEEDED）

**联动副发现 — IOS_DESIGN_LOG.md §6.5 矛盾**：N18「暗色模式：做 ✅」但实际未实装 → 加 TODO §B 待 itsuki 拍板（A 真做 N18 全 token 改造 / B 降级 N18 → v1.0 不做）

**残**：
- pbxproj 备份 `/tmp/pbxproj_backup_before_icon_move`（commit 前 git diff 可检视手改 UUID 正确性）
- iOS sync 脚本本机不通（`~/dev/TomoshibiiOSApp` 不存在）— 是否 clone 独立 repo / 或改脚本路径
- 真机暗夜黑闪 fix 需要 itsuki 装手机晚上验证（CC 无法验证）
- 启动 git status 残留垃圾（`.bak` × 2 / `Root/File.txt`）等 itsuki 拍板删

### 2026-05-04 深夜 by [Mac-元层优化 Opus 4.7]

**主题**：⭐⭐⭐⭐ Claude Code 5 层架构学习 + 2 个 skill 落地（ac-record + version-bump）+ 4 次 itsuki 戳穿 CC 设计盲点 + 全工程实践扫描清单

- **学概念**：CC 5 层架构（CLAUDE.md / Skills / Hooks / Subagents / Plugins）+ MCP / Agent Teams 外挂；连续 4 次戳穿 CC「派多个 subagent 叫 Teams」表述夸大 → CC 校准到 L1/L2/L3 真实分级；CrewAI 简介；第一性原理筛 5 层 → Plugins ❌ Skills 🟡 Hooks 🔴 Subagents 🟠
- **戳 CC coach 失职**：CC 之前没主动提 Skill / CC Hook 这两个现成方案 → 我手搓了山寨版 CLAUDE.md 触发词机制 + git pre-commit；元认知金句「这种事情没有体验，别人提醒我也不会知道」拍板
- **memory 升级**：`feedback_proactive_diagnose_unknown_unknowns.md` 加 case study（Skill / CC Hook 失职 + Git 反证）+ 3 层扫描清单（CC 内部能力 / 业界标准工程实践 / AC 学习自管理）
- **🆕 ac-record skill** — itsuki 重写 v4 → CC 审视 → 整体迁入 `.claude/skills/ac-record/SKILL.md`；旧 `00_admin/CLAUDE_CODE_记录指南.md` git rm；后续 itsuki 4 次戳穿 CC：1) 指针文件多余 2) 未完全理解自我贬低 3) 关键词触发不实用 → CC 改为「**收尾全量扫描**」主流程
- **🆕 version-bump skill** — `00_admin/版本管理SOP.md` 整体迁入 `.claude/skills/version-bump/SKILL.md`（531 行），归档到 `99_archive/2026-05-04_版本管理SOP_迁入skill/`；加 4 条 itsuki 拍板新铁律：⭐ **CC 否决权**（itsuki 说要 bump CC 也能拒绝）/ ⭐ **版本演变一览必更新**（实战发现 v0.6.0 + v0.8.0 都没更新）/ ⭐ **全量扫描**（不偷懒）/ ⭐ 加「迭代」关键词
- **CLAUDE.md 同步**：4 处指针改向 ac-record skill / SOP 引用全改向 version-bump skill / 5 硬底线第 5 条改为「raw 写"AI 提了 X，我评估后采纳"」（冲突 1 折中）；第 5 条二改去掉「未完全理解明标」（itsuki 拒绝）
- **TODO 闭合 + 加 unknown unknowns 工程实践体检清单**：5 项 🔴 推荐试（GitHub Actions / Linter / Type checker / FastAPI /docs / .env）+ 4 项 🟠 延后（Issues / Sentry / Docker / structlog）+ 学习路径 5 步

**新规则上线**：
- AC 协作权威源换地方 — `.claude/skills/ac-record/SKILL.md`（按需触发不占主上下文）
- 版本 bump 权威源换地方 — `.claude/skills/version-bump/SKILL.md`（CC 有否决权 + 版本演变一览必更新）
- CC 看到 itsuki 手搓机制 → 强制对照扫描清单，主动提现成方案
- raw dump 叙事策略：写「AI 提了 X，我评估后采纳/拒绝/改造」（不写"未完全理解"自我贬低标记）
- ac-record 主要工作模式：itsuki 说"收尾" → CC 全量扫描会话上下文（不依赖关键词命中）

**版本演变一览历史欠债**（CC 主动识别，等 itsuki 拍板补不补）：
- v0.6.0 段（4-29 close）— 没写
- v0.8.0 段（5-02 close）— 没写
- → 下次 bump 时 version-bump skill §0.2 铁律会强制补这部分

**残**：itsuki 授权 CC 自主完成 — 2 个 skill ✅ 已做完。后续待 itsuki：1) 测试 ac-record 收尾全量扫描 2) 测试 version-bump 否决权（说"迭代"看 CC 是否会拒绝）3) unknown unknowns 体检清单 🔴 5 项 4) Hook 改造（日语注释拦截 + sync-check on Stop）5) progress_overview 章节里程碑刷新 6) 版本演变一览补 v0.6.0 / v0.8.0 段

### 2026-05-04 晚 by [Mac-治理 Opus 4.7]

**主题**：⭐⭐⭐ DMSD 文档治理大整顿 — CLAUDE.md 71% 瘦身 / 性别身份更正 / 单源真值确立

- **CLAUDE.md 419 → 120 行**（瘦身 71%）— AC 协作整块挪到 `00_admin/CLAUDE_CODE_记录指南.md`（升级为 AC 协作单一权威源 §0-§13）；对话规则细节挪 memory 索引指针；删 markdown 表格分隔符 / `**bold**` / 历史注释 / 解释性括号
- **5-01 全文件审查升级为系统级入口**：`git mv 2026-05-01_全文件审查.md → 项目文件总览.md`，去日期前缀 + 加维护铁律（CC 创建/删除/大改文件作用 → 当场同步更新，不再开新审查报告文件）
- **CLAUDE_CODE_记录指南.md 升级为 AC 协作单一权威源**：§0 加 3 根本性原则 / §7 完整 5 核心问题（不再指针）/ §8 升级 7 节详细收尾动作 / §13 加 AC 文件家族 CC 权限速查
- **CLAUDE.md 加规则**：找文件 / 问文件 → 必须翻项目文件总览不用 `grep`/`find`；TODO 必须 itsuki 主动问才读不主动催进度
- **性别身份更正**：itsuki 是男生不是女生 — sed 批量替换全 DMSD 仓库 markdown（172 处）+ memory 文件夹（102 处）= 274 处「她」→「他」；99_archive/ 历史快照不动；新建 `user_gender_male.md` memory + MEMORY.md 顶部 ⚡警告
- **`00_admin/文件结构指南.md` 归档**到 `99_archive/2026-05-04_文件结构指南_已被项目文件总览取代/`（已被项目文件总览取代）
- **TODO.md 538 → 660 行**：旧 backlog（4-19 87 条）+ 全文件审查（5-01 606 文件）所有未结余项展开搬到一个 §（A.1-A.5 + B + C + D + E + F + G）— 5 个分散文件改作历史快照
- **4-19 backlog 5-04 同步打勾 6 条**：T2 / T7 / T12 / S15 / D17 / D18 — 实际已闭合但忘了打勾
- **memory 加 4 条**：`feedback_no_cli_jargon.md` / `user_gender_male.md` / MEMORY.md 索引更新

**新规则上线**：
- 启动只读 WIP（不再读 TODO 顶部 / 项目文件总览）
- 项目文件总览 = 找文件唯一入口（替代 grep / find / 命令行）
- 记录指南 = AC 协作唯一权威源（CC 收尾 / 触发场景去读）
- 不再开新「2026-XX-XX_xxx_审查.md」分散文件，未结余项一律写 TODO

**残**：~~待 itsuki 拍板「她」→「他」批量~~（已 sed 全做）/ ~~文件结构指南归档~~（已做）/ progress_overview.md 章节里程碑刷新（4-17 后没动）/ Batch3 itsuki 自粘 11 条历史欠债

### 2026-05-04 by [Mac-mini-Opus 4.7]

**主题**：⭐⭐⭐ 1 个会话推 4 commit — A+B 工具 + backend 双新功能 + iOS 双新功能 + 注释规则强化

4 commit 一气呵成：
- `c3be94d` feat(study): 5-03 残留学習欠席 period 字段贯通（backend + iOS）
- `ce90715` chore(hooks): A+B 文件联动工具（pre-commit 加内容检查 + bin/sync-check.sh 中途查 + sync-rules.sh 13 条规则代码化）
- `3a6c585` feat(backend): 学生注册码 + 老师公告 backend 完整实装 + CLAUDE.md 加重「代码注释只用中文」铁律（itsuki 第二次强调被骂 → 强化规则 box + memory 加 incident）
- `3b19bc4` feat(ios): 注册码 RegisterStep5（POST /accounts wire 通）+ 老师公告 列表/详情/回复 view（最小可工作版）

**新工具习惯化**：会话中跑 `bash bin/sync-check.sh` 即可见联动漏改；commit 前 pre-commit 自动跑同样规则。

**iOS 实装策略**：avoid .pbxproj 大改 → 新 enum/view 全 inline 到现有 .swift（AccountsAPI / AnnouncementsAPI → AuthAPI.swift；公告 view → HomeStubs.swift）。v1.0 上线前可拆 file。

**xcodebuild 验证**：iPhone 17 simulator BUILD SUCCEEDED。
**pytest**：37 passed（含 12 注册码 + 6 公告新测试）。

**残**：Android 注册码 + 公告 4 端实装（独立 repo `~/dev/TomoshibiAndroidApp/`）/ teacher_web 注册码生成面板 + 公告投稿面板 / progress_overview.md 章节刷新 / iOS RegistrationDraft 累积（让 Step1-4 字段真到 backend，目前是 hardcoded demo 字段 + 真注册码）

### 2026-05-04 上午 by [Mac-mini-Opus 4.7]

**主题**：⭐ A+B 文件联动工具建设 — 把 §3 文件关联追踪表代码化 + 加自动检查

- **背景**：itsuki 启动会话提"每次改动/决定立刻同步文档" → 诊断现有机制只能 70-80% 联动 → 拍板 A+B 方案
- 已合并到上面"2026-05-04"主条目（同会话延续）

> **2026-05-04 深夜砍掉 5 条老条目** + **2026-05-06 砍掉 5-03 晚条目（协作模型升级）** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4}.md`

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
- 更早历史 — 见 `git log -- 00_admin/WIP.md`
