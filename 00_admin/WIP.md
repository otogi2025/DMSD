# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-11 更晚（graphify 上线全套 + 沟通问题大爆发 — 详见 `raw/2026-05-11.md §D + §E`，§E 为给新会话必读的沟通问题诊断）。早些更新: 2026-05-11 晚（§C session-coord skill）/ 2026-05-11（§B HTML/MD 分层方案 + §A 术语表）/ 2026-05-10 晚（skills 批量装）/ 2026-05-10（ac-radar 上线）

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

> **⭐ 沟通问题大爆发（5-11 晚）— 新会话必读 →** `05_logs/raw/2026-05-11.md §E`
> itsuki 5-11 晚 3 次怒怼 CC 沟通失职：(1) 句子太密 5 未知数堆一句 / (2) 没把做的事写出来 + 字太省略 + 英文不翻译 / (3) 单方面立 4 习惯不算讨论。
> Root cause 已诊断（CC 没把"做了什么"写清楚 + 用英文不翻译 + 状态混淆 + 单方面立规矩不讨论）。
> **解决方案讨论尚未真正发生** — CC 抛了 3 个观察 + 1 个 A/B/C/D 选项，itsuki 没回应直接让收尾。**新会话开场必须读 §E 接上**。

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
- **沟通方案讨论中尚未拍板**

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2 × 2（vendor 污染假设崩 + CC 以为问题是密度真问题是没说清做了啥）/ 模式 5 × 3（工程 ignore 文件普适性 + 第三方工具配置污染防御 + CC 元层翻车）/ 模式 6 × 2（archive 漂移取舍 + memory vs 当下讨论的取舍）/ 工程发现 × 2（vendor 污染 + .beads 副作用）。详见 `raw/2026-05-11.md §D + §E`

**残**：
- **沟通方案讨论未完** → 新会话继续，必读 `raw/2026-05-11.md §E`
- vendor 污染配置写了但**还没重跑**：`/graphify --update` 待 itsuki 拍板
- 本会话所有改动 + 5-11 晚 session-coord 改动一起待 commit
- WIP/TODO/CLAUDE.md modified 但非本会话改的 — 需要 itsuki 拍板（可能是别的会话）

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

> **2026-05-04 深夜砍 5 条老条目** + **2026-05-06 砍 5-03 晚条目** + **2026-05-08 砍 5-04 上午** + **2026-05-08 凌晨砍 5-04 主体/晚/深夜 3 条** + **2026-05-10 砍 5-04 晚 iOS bug 条目** + **2026-05-10 晚砍 5-06 独立 repo 退役条目** + **2026-05-11 砍 5-08 点呼机条目** + **2026-05-11 晚砍 5-07→5-08 iOS 上架冲刺跨日条目（让 5-11 晚 session-coord + 5-11 术语表 + 5-10 晚 skills + 5-10 ac-radar + 5-08 reviewer_demo 5 条上限；详见 `raw/2026-05-07.md` + `2026-05-08_ios_上架冲刺.md`）** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4,6,7,8}.md`

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
