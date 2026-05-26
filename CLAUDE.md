# DMSD 项目指令（CC 必读）

## ⚠️ 沟通铁律 — 不主动用英语名词（2026-05-26 拍板，全局规则）

除非这个词在项目代码 / 文档 / 文件名里真出现过，否则一律用中文。比如别说「凭证 credential」「兜底 fallback」「联动 sync」，直接说中文。

完整规则在 `~/.claude/CLAUDE.md`。

## ⭐⭐⭐ dmsd-startup 强制加载（2026-05-26 上线 — 集中启动逻辑）

每次会话启动时，**第一件事**先 Read `.claude/skills/dmsd-startup/SKILL.md`，按 §2 顺序跑 5 件启动必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）。

不依赖关键词触发 — 每次新会话第一个回合 CC 必须主动加载本 skill。

历史：以前启动逻辑散在 CLAUDE.md「会话开始」段 + 全局 `session-start-coord-check.sh` 挂钩 + DMSD `bin/check_overview_drift.sh` 调用，2026-05-26 itsuki 拍板集中到一个 skill。配套：全局 coord-check 挂钩在 DMSD 项目下静默退出，本 CLAUDE.md「会话开始」段简化成「走 dmsd-startup skill」。

## ⭐ ac-radar 强制加载（2026-05-10 上线）

每次会话启动时，**先 Read** `~/.claude/skills/ac-radar/SKILL.md`，按那里的「CC 行为约定」（§14）执行。这是为了让 AC 素材捕获不依赖 description 语义匹配（会漏）。

启动时跑一次：

```bash
python3 ~/.claude/skills/ac-radar/scripts/startup_check.py
```

脚本输出按原样转告 itsuki，不美化、不解释。

### 跟 session-wrap 的分工（重要）

- **实时阶段**：信号命中 → ac-radar 双写 inbox + DMSD raw 的 `## AC 信号 (HH:MM)` 段（轻量 tag）
- **收尾阶段**：itsuki 说「收尾」→ ac-radar flush 模式仅补**中央 inbox** + session-wrap 跑 §5.5 全流程（含 §5.5.1 深度 AC dump 到 raw）
- 完整分工矩阵 → `~/.claude/skills/ac-radar/SKILL.md` §13

**session-wrap 不动** —— 它继续做工程层 + 深度 AC dump，ac-radar 只补「实时短 tag + 跨项目 inbox」。两者并行不互调。

## 关于 itsuki

中国留学生，日本高中三年级
完全零基础，所有概念从零解释
目标: 筑波大学 情報学群 情報科学類 AC入試，2027-04 入学
DMSD 是他的核心 AC 叙事项目

## 项目信息

项目名: DMSD
系统名: Tomoshibi
核心: 宿舍点呼数字化 + NFC 防代刷
技术栈: iOS Swift+SwiftUI / Android Kotlin+Compose / 后端 FastAPI+PostgreSQL / 点呼机 Pi 3A+ + PN532 + ST25DV16K / NFC 卡 NTAG215
上线姿态: v1.0 一次上线 iOS + Android + 卡，不分阶段 <!-- VERSION_OK -->
当前版本: 见 CHANGELOG.md 顶部
GitHub: otogi2025/DMSD public（单一 repo — 2026-05-06 退役独立 repo 模式，iOS+Android+Web+后端 全在 DMSD 内）
设计 / 防御 / 扣分 / 采购 / 硬件 / 流程 详情: 02_design/ + 01_specs/ + .claude/skills/project-overview/SKILL.md

## 目录结构

00_admin/   WIP / TODO / 项目文件总览 / 文档同步点清单 / hooks（版本 bump 流程 → `.claude/skills/version-bump/`）
01_specs/   规格文档 — rollcall/ 字典+主体
02_design/  设计文档 — hardware / flow / system_features 等
03_dev/     代码 — backend / teacher_web / student_ios / student_android / rollcall_device（点呼机）
04_ops/     运维
05_logs/    开发 log — raw / dev_log / problem_solving / decision_log / learning_path / project_evolution
06_assets/  07_release/  99_archive/  bin/   参考材料 / 发布物 / 早期归档 / 脚本
docs/agents/  外部 skill 配置（Matt Pocock）— issue-tracker / triage-labels / domain 映射

完整文件级清单 + 状态 + AC 价值: .claude/skills/project-overview/SKILL.md

## 设计文档双层

共用层（≥2 端涉及）: 02_design/system_features.md
iOS 専属:     03_dev/student_ios/IOS_DESIGN_LOG.md
Android 専属: 03_dev/student_android/ANDROID_DESIGN_LOG.md
Web 専属:     03_dev/teacher_web/WEB_DESIGN_LOG.md
后端 専属:    03_dev/backend/BACKEND_DESIGN_LOG.md
点呼机 専属:  03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md
物理硬件层:   02_design/hardware_design.md（板子选型 / 模块选型 / BOM — 跟点呼机软件层互补）
判断标准 / 反模式: 见本节上方 5 端 + 共用层 + 物理硬件层 划分（原 memory 文件已并入本章 — 2026-05-21 死链修复 B-011）

## 文档一致性

单源真值表 + pre-commit hook: 00_admin/文档同步点清单.md
版本 bump 流程: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权）
中文铁律 — 代码注释 + 内部文档 100% 中文 / UI 字符串保持日语（规则在 `00_admin/hooks/post-edit-japanese-comment-check.sh` 里活，2026-05-03 itsuki 拍板 — 2026-05-21 死链修复 B-012/C-002）

## 文件连锁结构（改 A 必查 B，改完当场对照）

iOS Swift view 改（视觉 / 流程 / 字段） → 03_dev/student_ios/IOS_DESIGN_LOG.md 对应章节 + 02_design/system_features.md（≥2 端涉及时）
Android UI 改（视觉 / 流程 / 字段） → 03_dev/student_android/ANDROID_DESIGN_LOG.md + 02_design/system_features.md（≥2 端涉及时）
backend 业务代码改（routers / services） → 03_dev/backend/BACKEND_DESIGN_LOG.md + 02_design/system_features.md（≥2 端涉及时）
teacher_web 业务代码改 → 03_dev/teacher_web/WEB_DESIGN_LOG.md + 02_design/system_features.md（≥2 端涉及时）
点呼机 src 业务代码改 → 03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md + 02_design/system_features.md（≥2 端涉及时）
任一端 *_DESIGN_LOG.md 改 → 多端涉及时 02_design/system_features.md 也要更新（共用层真值）
02_design/system_features.md → 5 端 *_DESIGN_LOG.md 引用要更新
02_design/hardware_design.md → 03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md（接线 / GPIO / 模块选型联动）
backend models.py → schemas.py + routers/*.py + alembic/versions/* + iOS NetworkModels.swift（字段对齐）
backend routers/*.py → iOS Endpoints/*API.swift（端点 / 参数 / 返回类型对齐）
Route.swift 加 case → RootView.swift switch + 用到的 view 要存在
Foundation/ component 改 props → grep 全 repo 找用到的地方
01_specs/rollcall/* 主体改 → 触发 SOP 阅读 + 可能 bump 版本号
新建 / 删除 / 改名 / 移动文件 → .claude/skills/project-overview/SKILL.md 同步更新对应章节
新建声明性文件（CLAUDE.md / WIP / TODO 类） → 00_admin/文档同步点清单.md 加同步点
新建 / 改 hook → 00_admin/hooks/README.md

详细联动矩阵 / 反向索引: `.claude/skills/file-linkage/SKILL.md`（itsuki 说"联动检查 / 我改了 X 要查什么"自动触发）

工具（7 PostToolUse + 1 PreToolUse + 1 SessionStart + git pre-commit）:
- 实时联动检查 + demo scaffold 字眼检测（Write/Edit 后）: `post-edit-sync-check.sh`
- memory 索引检查（Write/Edit memory dir 后）: `post-edit-memory-check.sh`
- 中文铁律 / 日语注释扫描（Write/Edit 代码文件后）: `post-edit-japanese-comment-check.sh`
- 声明性文件时间戳检查（Write/Edit WIP/TODO/progress 后）: `post-edit-timestamp-check.sh`
- 版本号硬编码实时拦（Write/Edit 声明性文件后）: `post-edit-version-hardcode-check.sh`
- **project-overview 同步检查（Write/Edit 任何 DMSD 文件后 — 2026-05-19 改全项目覆盖）**: `post-edit-project-overview-check.sh`
- **多语言代码自动格式化（Write/Edit 代码文件后 — 2026-05-19 加）**: `post-edit-format.sh`（`.py`→ruff / `.swift`→swiftformat / `.kt`→ktlint / `.ts/.tsx/.js/.jsx/.vue/.css/.scss/.html/.json`→prettier，工具未装静默 skip）
- 破坏性 Bash 命令拦截（Bash 调用前）: `pre-bash-destructive-block.sh`（rm -rf 非临时 / git reset --hard / git push --force / git branch -D 等）
- **project-overview 启动对账（每次会话启动 — 2026-05-19 加）**: `bin/check_overview_drift.sh` — 跑 git ls-files 跟 project-overview §0.1 体量表对比，漂了立刻报
- commit 时: bash 00_admin/hooks/pre-commit
- 中途随时: bash bin/sync-check.sh / bash bin/check_overview_drift.sh
- 规则源: 00_admin/hooks/lib/sync-rules.sh

## 会话开始: 走 dmsd-startup skill

启动 SOP 完整版在 `.claude/skills/dmsd-startup/SKILL.md`，按 §2 顺序跑 5 件事：

1. 多会话协同注册（register + scan）
2. project-overview 漂移检测（`bin/check_overview_drift.sh`）
3. ac-radar startup_check
4. 读 WIP（拿当前版本 / 焦点 / 最近 5 次会话 / 多会话占用 / 阻塞项）
5. 报告状态等指令 — 不主动催进度，不主动列 TODO

git 仓库状态确认（git status / 残留 / 未 push / stash） → **会话结尾时**走 session-wrap skill §5.5.9，**不在启动时跑**。

## 按需读（不主动读，触发场景才读）

**找文件 / 问文件 → 必须去查 .claude/skills/project-overview/SKILL.md，不用 grep / find / 命令行**

下面任何一种 itsuki 输入，CC 必须当场打开 .claude/skills/project-overview/SKILL.md 查答案：
- 「某文件在哪？」
- 「某文件干嘛用的？」
- 「项目里有没有 XX 文件？」
- 「XX 类的文件都在哪个目录？」
- 「这个目录下有什么？」
- itsuki 让 CC 「找文件」/「列文件」/「整理某类文件」

**不用命令行查找** — 总览里写好了所有文件干嘛用 + 状态。直接翻总览拿答案。

**TODO 待办 → 必须 itsuki 主动问才读 00_admin/TODO.md**

只在 itsuki 主动问「还有什么没做」/「下一步该做什么」时读，不主动催进度，不主动列待办给他看。

**WIP vs TODO 铁律**: WIP = 当下书签，最近 5 次会话上限 / TODO = 完整未完成 backlog，真值。WIP 绝不复述 TODO 内容。

## 会话结束: 走 session-wrap skill

收尾时通过 session-wrap skill 跑完整流程（AC 素材 dump / 中文总结 / 文件联动 / WIP 刷新 / git commit）。skill 在 `.claude/skills/session-wrap/SKILL.md`，触发关键词命中时自动加载，无需主动读。

---

# AC 记录协作（CC 立场 + 默认底线）

> **DMSD 是 itsuki 的 AC 叙事项目。AC 是他最重要的事**，跟"写代码 / 改文档"同等重要。
>
> **完整规则（3 根本原则 / 5 核心问题 / 5 级素材清单 / 模式 5 挖掘法 / 7 节收尾动作 / AC 文件家族权限速查）→ 全部在 skill `.claude/skills/session-wrap/SKILL.md`**。触发关键词命中时 CC 自动加载，按里面执行。

## 默认底线（CC 永远遵守 — 这 5 条不依赖 skill 触发，永远在线）

1. iCloud `05_产出/` 永不写 — itsuki 原创志望理由书 / 自我推荐书 / 面试准备
2. iCloud `03_素材_候选/` + `04_素材_成品/` 写需 itsuki 当场授权
3. `05_logs/decision_log.md` / `project_evolution.md` / `learning_path.md` 正文 CC 永不直写，只起草 draft 等 itsuki 粘贴
4. AC 叙事文档 `vX.Y.Z_AC叙事.md` itsuki 自己写，CC 等他来问才辅助，不主动起草
5. 叙事归属：raw 阶段写「AI 提了 X，我评估后采纳/拒绝/改造，理由是 Y」 — **不写"未完全理解"类自我贬低标记**（2026-05-04 itsuki 拍板：raw 是 git 可见的负面证据）。月度筛选时再归功 itsuki 判断 — 详见 skill §0.1

## 触发场景（看到任一 → session-wrap skill 自动激活）

⭐ **主触发**（最常用）：itsuki 说「**收尾**」/「**总结一下今天**」/「**整理一下今天**」/「**记一下今天发生的事**」 → CC 立刻跑 skill §5.5.0 **全量扫描算法**（从会话第一条消息扫到最后，找所有候选素材，不只看最后一段）。

次触发（兜底用，避免当下重要素材漏 dump）：
- itsuki 说「启动」/「记一下」/「dump 一下」/「留个痕」
- itsuki 做了决策 / 拍板 / 反思 / 学到新东西 / 纠正 CC
- itsuki 说「以前我...」/「我之前以为...」/「原来这样啊」（模式 5 触发词）
- 代码或架构改了
- CC 主动发现的问题（这种也算 itsuki 的 AC 素材，必须 dump）
- 版本号 bump

---

# Skills 触发速查（关键词命中 → CC 自动加载对应 skill）

| skill | 触发关键词 | 干嘛 |
|---|---|---|
| session-wrap | 收尾 / 整理今天 / 总结今天 / 记一下今天 | AC 素材全量扫描 dump + git 状态收尾确认（§5.5.9）|
| version-bump | 迭代 / bump / 发版本 / 打 tag / 发版 / release / 推上去 | 版本决策树（CC 有否决权）+ §13 发版动作 SOP |
| new-feature | 新功能 X / 加 Y / 实装 Z / 做 W | 5 端实装模板（spec→backend→iOS→Android→点呼机）|
| spec-sync | 跨端检查 / 字段对齐 / 端对齐 / API 对齐 | backend↔iOS↔Android 字段提取对比 |
| memory-write | 记一下规则 / 以后这样 / memory 加一条 / 不要再... | memory 写入 SOP（4 类型 / 查重 / 索引）|
| file-linkage | 联动 / 改 A 要查 B / 我改了 X 要查什么 | 联动矩阵（CC 改高联动文件后调）|
| project-overview | X 文件在哪 / 项目里有 X 类文件吗 / 找文件 | 项目文件总览 |

---

## Agent skills（外部 skill 配置入口 — Matt Pocock 套件）

外部 skill（grill-me / tdd / to-prd / to-issues / diagnose / setup-matt-pocock-skills）的 per-repo 配置。详细配置 → `docs/agents/`。

### Issue tracker

DMSD 用 `00_admin/TODO.md` 单文件（不是 GitHub Issues）。详见 `docs/agents/issue-tracker.md`。

### Triage labels

5 个默认 label（`needs-triage` / `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`），DMSD 暂未启用，留作模板。详见 `docs/agents/triage-labels.md`。

### Domain docs

Multi-context — 5 端 monorepo + 共用层 + 物理硬件层 + 决策日志（替代 docs/adr/）。`CLAUDE.md` 仍是 single source；`docs/agents/domain.md` 是给 skill 读的快照。

# 对话规则 / 代码编写原则

核心:
1. itsuki 决定做什么 / CC 实现怎么做 / 每段代码向他解释含义
2. 大白话沟通，术语 / 日语 / 英文缩写第一次出现就翻译
3. 主动告诉他不知道但应该知道的概念或更优做法
4. 出练习题结合 DMSD 场景 — 点呼 / 扣分 / 签到

详细规则 / feedback 历史: ~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md 索引（feedback_*.md 系列）

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 全项目中枢联动 (2026-05-26 起)

中枢位置: `/Users/kurekoduki/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/大学入試/全项目中枢/`

itsuki 名下 4 个项目 (大学入試 / DMSD / Tango / QTS) 互通的中央协同板。CC 实例之间不能直接调用，通过中枢里的文件传信。

- **会话启动时**: 来中枢读 `信箱/DMSD_inbox.md`，有新留言报告 itsuki
- **会话收尾时**: 来中枢更新 `项目档案/DMSD.md` 的「现状一句话」+「最后更新日期」
- **想留言给别项目**: 写到 `信箱/<对方>_inbox.md` (对方 = 大学入試 / Tango / QTS)
- **想知道别项目在干嘛**: 读 `项目档案/<对方>.md` 或 `_中央板.md`

完整机制说明 → 中枢 `CLAUDE.md`
