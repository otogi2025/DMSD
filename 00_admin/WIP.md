# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-11 跨 23 点（CC-2 reviewer 后门修复上线主线收官 — 详见 `raw/2026-05-11_reviewer后门修复上线.md §F.1-F.8`）。早些更新: 2026-05-11 更晚（graphify + 沟通问题大爆发，详见 `raw/2026-05-11.md §D + §E`）/ 2026-05-11 晚（§C session-coord）/ 2026-05-11（§B HTML/MD + §A 术语表）/ 2026-05-10 晚（skills 批量装）

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

> **⭐ 沟通规则 cc-comm-rules 已上线（5-11 晚）— 新会话必读 →** `05_logs/raw/2026-05-11.md §E + §F`
> 5-11 晚 itsuki 3 次怒怼 CC 沟通失职 → 拍板「Skill 主 + Hook 辅」方案 → 已实装上线。
> **完整 skill**：`~/.claude/skills/cc-comm-rules/SKILL.md`（5 个规则 + always-on 永远在线）。
> **配套 3 个 hook**：在 `~/.claude/hooks/`（拦 memory / 怒怼词检测 / 环境清单 diff）。
> **新会话开场必须**：(1) 读 cc-comm-rules SKILL.md / (2) 按 5 个规则执行 / (3) 看 §F 测试结果。
> **试用 1-2 周看效果** → 详见 TODO §🛠️ A。

> **⏰ 2026-05-12 截止** — Cloud Design 40 额度。
> 5-13 凌晨刷新，不用就浪费。
> 跟 cici 讨论怎么用 → 见 `TODO.md §⏰`。
> 若明天 itsuki 没主动提：CC 启动读到此条须主动报告。

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 三端代码层启动完毕，下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-11 跨 23 点 by [新Mac-Opus 4.7 1M-CC2 reviewer 后门修复上线]

**主题**：⭐⭐⭐⭐⭐ 5-08「修干净再提交」拍板后 3 天的 reviewer 后门修复主线 5-11 晚收官 — 主项目 push GitHub + Mac→VPS 精细 rsync + alembic upgrade + SQL 重发凭证 + 验证全绿 + session-coord 多会话首测通过

- **会话身份**：session-coord 真实多会话首测中的 CC-2 角色（主会话 Opus47-1M-主 设计的双会话验证），跑通 register / scan / 公告 / 心跳 全链路
- **session-coord bug 自动收敛**：register.sh L81 + scan.sh L63 中文全角标点 + `set -u` → unbound variable，主会话 + CC-2 独立诊断同方案 = bug 客观存在不是偶发
- **戳穿 reviewer 后门三层分裂**：itsuki 问「修好了吗」→ git log 查到主项目 commit 852563c 已修 + 11 commit 没 push + Mac fork 缺 migration 文件 + VPS 上跑的可能还是 buggy → itsuki 拍板「让 VPS CC 修」
- **diff 戳穿"fork = 主项目"假设**：alembic/env.py + b2c3d4e5f6a7 是 VPS / fork 改过主项目没改；f6a7b8c9d0e1 migration 只在主项目；seed.py fork 是 buggy 后门源 / 主项目是双模式修过版 → 设计精细 rsync 避免破坏 VPS 修过的部分
- **跨机器协作分工**：Mac CC push GitHub + 写 VPS CC 提示词（Step A-F + 5 红线）；VPS CC 跑 Step A-F；itsuki 拍 SQL 红线节点
- **VPS CC 反向识破 Mac CC 任务描述偏差**：expires_at 2099 vs 2030 / "App Reviewer" vs "Reviewer 2026" — Mac CC 凭印象抄 TODO ledger，VPS CC 直接读主项目 seed.py 拿真值 + 停下问 itsuki = 收敛
- **VPS CC Step F 全绿**：alembic head=f6a7b8c9d0e1 / 旧 999999 invalidated + is_reviewer=f / 新 999999 reviewer 码 / 旧 060199 标 is_demo / curl 200 / api healthy
- **itsuki 怒怼"你到底在说什么呀"**：5-11 晚 graphify 会话刚立 `feedback_no_dense_jargon_strings`，当晚 reviewer 修复 CC 又踩 → memory 不解决当下问题，CC 元层翻车

**新规则上线**：
- 待写 memory：`feedback_cc_reference_source_of_truth_not_summary.md` — CC 给别的 CC 写提示词时必须引用源码 source of truth，不凭印象抄 ledger / 摘要 / WIP
- WIP §当前焦点 顶部加「⏰ 2026-05-12 截止 Cloud Design 40 额度」紧急条目
- TODO §⏰ 时间敏感 新 section（Cloud Design 5-13 凌晨刷新）

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2 × 2（itsuki「修好了」假设崩 + diff 戳穿 fork=主项目 假设）+ 模式 5 × 3（commit-push-deploy 三层分离 / source-of-truth vs 印象 / CC 元层翻车 memory 失效）+ 模式 6 × 2（精细 rsync 取舍 / 跨机器协作分工）+ 主线收官（5-08 拍板 public safety 真正动机 + 时间盒承诺兑现）。详见 `05_logs/raw/2026-05-11_reviewer后门修复上线.md`（§F.1-F.8）

**残**：
- VPS 端 4 项遗留：env.py + b2c3d4e5f6a7 反向同步回主项目主分支（不是 fork）/ reseed_reviewer.sql 留 VPS 当证据 / app.bak.20260511_123608 备份 1-2 天后删 / Apple Reviewer Notes 用新凭证（注册码原文不写）
- iOS 上架冲刺 A.1-A.11 步骤等 itsuki 坐到 Xcode 前继续（卡点已修通过 fork project.yml MARKETING_VERSION）
- 本会话改动等 commit（raw 1 新文件 + WIP/TODO 编辑）

### 2026-05-11 更晚 by [新Mac-Opus 4.7 1M-主会话 graphify]

**主题**：⭐⭐⭐⭐⭐ graphify 知识图谱工具上线全套（装 / 全量跑 / 发现 vendor 污染 + archive 漂移 + .beads 副作用 / 修复 / hook 装 / always-on 配 / **沟通问题大爆发**）

- **graphify v0.7.13 装上线** <!-- VERSION_OK -->：itsuki 给 GitHub URL → 读 README → 反问"API vs 订阅余额"→ CC 查 skill 源码确认走 CC subagent 不接 API → itsuki 拍板"装" + "趁余额重置 18 分钟内全量跑"
- **DMSD 全量跑**：573 文件 / 240 万字 / 13 chunk subagent 并行 / 6 分钟 → 9729 nodes / 26803 edges / 377 communities
- **vendor 污染发现**：god nodes 前 10 全是 React/Babel 压缩函数 `As() error() K() i()`（来自 iOS demo + teacher_web demo 的 vendor 目录 + phaseB_src）→ itsuki 反问"你到底在说啥" → CC 重新校准用零基础语言解释 → 写 `.graphifyignore` 排除（**待 `/graphify --update` 重跑才生效，目前图谱还是脏的**）
- **archive 漂移意外发现**：`99_archive/compose-drafts/HomeScreen.kt` 还在 import 活的 `GlobalScaffold` → itsuki 拍板不修
- **.beads 副作用抓获**：`graphify hook install` 偷改 git `core.hooksPath` 到 `.beads/hooks/` 覆盖 DMSD 原 `00_admin/hooks/` → 立刻验证 + 修复（copy hook 到主目录 + hooksPath 改回 + `.gitignore` 加 `.beads/`）
- **`graphify claude install` 装 always-on**：DMSD CLAUDE.md 加 graphify 段 + `.claude/settings.json` 加 PreToolUse hook → CC 以后每次工具调用前提醒读 `GRAPH_REPORT.md`
- **DMSD Hooks 7 → 10**：加 post-commit / post-checkout（graphify AST 自动重建）+ PreToolUse always-on
- **⭐⭐⭐⭐⭐ 沟通问题大爆发**：itsuki 3 次怒怼 — (1) "句子太密 5 个未知数堆一句话" (2) "真问题是你没把做的事写出来 + 字太省略 + 英文不翻译" (3) "你他妈跟我讨论方案了吗 / 单方面立 4 习惯不算讨论" → CC 写 feedback memory `feedback_no_dense_jargon_strings.md` 但 itsuki 明确说 **memory 不解决当下问题**。沟通方案**讨论尚未真正发生**（CC 抛了 3 观察 + 1 选项，itsuki 没回应直接让收尾）→ 详见 `raw/2026-05-11.md §E`（给新会话必读）

**新规则上线**：
- 全局 CLI 工具 `graphify`（`uv tool install graphifyy`）+ DMSD CLAUDE.md graphify always-on 段 + `.claude/settings.json` PreToolUse hook + DMSD Hooks 10 个
- `.graphifyignore` 配置文件（DMSD 根目录，排 vendor）
- `.beads/` 漂移注意点（`00_admin/hooks/README.md ⚠️ 段`）
- 个人能力清单 `~/.claude/我的环境.html` 加 graphify 用法速查 + hook 全套 + .beads 警告
- feedback memory `feedback_no_dense_jargon_strings.md`（MEMORY.md 索引 line 95 ⭐）
- ✅ **沟通方案 Skill + Hook 混合已落地** — 新 skill `cc-comm-rules`（`~/.claude/skills/`）+ 3 个 hook（`~/.claude/hooks/`）+ `~/.claude/CLAUDE.md` 加强制加载段 + `~/.claude/settings.json` 注册 hook。dry-run 测试 5/5 通过。详见 `raw/2026-05-11.md §F`

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2 × 2（vendor 污染假设崩 + CC 以为问题是密度真问题是没说清做了啥）/ 模式 5 × 3（工程 ignore 文件普适性 + 第三方工具配置污染防御 + CC 元层翻车）/ 模式 6 × 2（archive 漂移取舍 + memory vs 当下讨论的取舍）/ 工程发现 × 2（vendor 污染 + .beads 副作用）。详见 `raw/2026-05-11.md §D + §E`

**残**：
- ✅ **沟通方案已落地** → 试用 1-2 周 + 看效果（详见 TODO §🛠️ A）
- vendor 污染配置写了但**还没重跑**：`/graphify --update` 待 itsuki 拍板（详见 TODO §🛠️ C）
- `~/.claude/我的环境.html` 还没同步 cc-comm-rules + 3 hook（详见 TODO §🛠️ B）
- 本会话所有改动（cc-comm-rules + 3 hook + raw §F + TODO §🛠️）一起待 commit
- 11+ commits 未 push 等 itsuki 拍板（详见 TODO §🛠️ D）

### 2026-05-11 晚 by [新Mac-Opus 4.7 1M-主会话 session-coord]

**主题**：⭐⭐⭐⭐ session-coord 多 CC 会话协作板 skill 从零到上线 + 真实多会话首测通过 + 顺手能力清单 HTML 化（5-11 MD→HTML 分层方案晚段实战）

- **诉求**：itsuki 直接喊 `/skill-creator:skill-creator` + 明确"多 CC 会话互相协同、互相做不同内容、不冲突" + 强制要求"上网搜，好好搜好好了解，不要偷懒"
- **2 个并行 agent 研究**：claude-code-guide（官方 Agent Teams + worktree + hooks）+ general-purpose（mclaude 7 层 + claude-squad / Tmux-Orchestrator + Matt Pocock skill 教学）
- **3 件大事**：Agent Teams 是 AI 自治不适合 itsuki（人是 leader） / mclaude 锁+心跳+handoff 3 件套可借鉴 / 行业共识 worktree 隔离>协商
- **itsuki 当场否决 CC 越级"5 Q 拍板"做法**：CC 直接抛术语让拍板 → itsuki 怒怼"心跳是什么？worktree 突然蹦出来？锁粒度是新单词？你完全没解释就让我拍" → CC 重写每个术语类比+演示+才让拍
- **itsuki 拍板"升级为协作板"**：CC 之前偏防冲突（锁+心跳），itsuki "我对 Skill 最大需求是每个 Session 互相知道对方、知道在做什么、互相搭配工作" → skill 抽象层升级（status.md / _board.md / inbox.md 三机制加）
- **关键设计拍板**：文件级锁 / 30s 心跳 / 3min stale / 装全局多项目共享 / 配置不存在 CC 主动问 init / **不用 Agent Teams**（AI 自治） / **不用 worktree**（高频改共享文件场景不对口） / **不直装 mclaude**（本土化）
- **9 scripts + SKILL.md + README.md + README.html + DMSD config 模板 落地**（draft 在 `.scratch/`，全局装 `~/.claude/skills/session-coord/`）
- **bug 修 2 处**：`$SESSION_ID（` / `$TASK（` bash 变量名+中文标点 unbound — 主会话 + 真实开的 CC-2 独立诊断同方案 = **收敛验证**
- **真实多会话首测通过**：主会话 + CC-2 互看 / inbox 互发 / 三档锁 / stale 释放 全 work
- **CC 自我反思**：自己以"cleanup"名义 `mv .claude/sessions/` 把 CC-2 状态搬走 = 设计 skill 的人最容易绕过自己 skill（模式 5）
- **能力清单 HTML 化**：itsuki 主动提"所有 skill / hook / CLAUDE.md 列表做成 HTML" → 补全 `~/.claude/我的环境.md`（13 全局 skills / 5 Plugin / 5 MCP / 7 DMSD skills / 7 DMSD hooks）+ 生成 `~/.claude/我的环境.html`
- **机制澄清**："CC 是回合制工具不会自动跟别的会话互动" — itsuki 接受根本限制，选"先正常用一段时间再加 hook"渐进路径

**新规则上线**：
- 全局新 skill `session-coord`（`~/.claude/skills/`）+ DMSD 装配置（`.claude/session-coord.config.json` + `.gitignore` 加 `.claude/sessions/` 和 `graphify-out/`）
- 个人能力清单 `~/.claude/我的环境.{md,html}` 补全 + 5-11 MD→HTML 分层方案晚段实战
- CC 行为铁律重申：先教再决策不越级 / 不绕过自己设计的 skill

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 5 × 多（认知层升级 / 收敛验证识别 / 设计者绕过自己 skill 反模式 / itsuki 内化 MD→HTML 分层）+ 模式 6 × 4（不用 Agent Teams / 不用 worktree / 不直装 mclaude / 渐进 hook）+ 主体性 5/5（主动喊 skill + 强制 CC 研究 + 否决越级 + 升级抽象层 + 启 CC-2 真测 + 选渐进）。详见 `05_logs/raw/2026-05-11.md §C` + AC inbox 5 条

**残**：DMSD 11 commits 未 push 等 itsuki 拍板（含今晚改动）/ `graphify-out/` 82M 已加 .gitignore / superpowers plugin 配置仍 enabled 待 disable / session-coord UserPromptSubmit hook 未来某天看自觉度决定 / 副项目 CLAUDE.md 加 session-coord 钩子段（按需）

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

**残**：术语表后续 itsuki 用一周后反馈是否真用得起来 / TODO §📄 候选清单 A 元任务（查 HTML skill）+ B 7+ 个候选 HTML 改造文件 / 多 commit 未 push 等 itsuki 拍板统一策略

**§B 早段会话补完（5-11 晚 session-wrap 收尾时记）**：§A raw 17:00 / 18:30 提到的「跨会话拍板混层方案 + TODO §📄 已加」实际就是 §B 本会话本体（不是另一会话）。§B 早段：itsuki 读 Thariq「Why HTML」全文 → CC 拆作者立场（5 用例全是人消费 / 没 DMSD 这种重 MD 协作层）→ itsuki 「就按混层」拍板 → 自己识破双写漂移坑（不等 CC 警告）→ 拍板方案 A「按需 pandoc 临时渲染」→ TODO §📄 落地（A 元任务 + B 13 候选 + C 已有 HTML + D 反向规则）。AC 价值 ⭐⭐⭐ — 模式 5 种子 / 模式 2 假设崩 / 模式 6 取舍 × 2 / 工程纪律「先 review 已有再决定新建」。详见 `raw/2026-05-11.md §B` 5 条 dump（ⓐ-ⓔ）

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

> **2026-05-11 跨 23 点砍 2 条**（让 CC-2 reviewer 后门修复上线 + graphify + session-coord + 术语表 + 5-10 晚 skills 批量装 维持 5 条上限）：
> - 砍 5-10 ac-radar 上线条目 — 详见 `raw/2026-05-10.md`
> - 砍 5-08 凌晨 reviewer_demo 重做条目 — 详见 `raw/2026-05-08_reviewer_demo重做.md`（本次 CC-2 会话 §F.7 已 reference 它作为主线前提）
>
> 早些砍除：**2026-05-04 深夜砍 5 条** + **5-06 砍 5-03 晚** + **5-08 砍 5-04 上午** + **5-08 凌晨砍 5-04 主体/晚/深夜 3 条** + **5-10 砍 5-04 晚 iOS bug** + **5-10 晚砍 5-06 独立 repo 退役** + **5-11 砍 5-08 点呼机** + **5-11 晚砍 5-07→5-08 iOS 上架冲刺跨日** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4,6,7,8}.md`

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
