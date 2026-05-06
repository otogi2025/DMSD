---
name: 主动诊断 unknown unknowns + 业界标准方案优先
description: itsuki 是新手不知道自己不知道什么 + 不知道存在 X 这个东西要去问。CC 看到他手搓机制 / 做法低效时强制对照扫描清单（CC 内部能力 / 业界标准工程实践 / AC 学习自管理），即使没问也当场点出现成方案，必须给具体原因。Skill / CC Hook 已踩失职案例在 memory 内警示。
type: feedback
originSessionId: adda132f-deff-4bcd-b0e1-cf44f6eee4d3
---
itsuki 经常在不知道有更好做法的情况下做事（早期不知道 Git / 不知道项目要分文件 / 不知道 AC 要留 commit + 截图证据 / 不知道时间块怎么排）。**他不知道自己不知道什么**，所以不会主动问。

**Why**：他在 2026-05-02 明确说"提醒我学习扩展我的思维这个很重要"。AC 入试评委关心过程，如果一直用低效/不规范做法走到面试才被指出来，已经来不及；CC 在过程中持续帮他"打开视角"是核心价值。他举的真实例子——**Git、项目分文件、用 git 留迭代证据、AC 要留截图证据、主动留 AC 素材**——都是 AI 主动提他才知道的。

**How to apply**：

1. **覆盖范围（不限技术）**：
   - 技术 / 工程：业界标准做法 / 命名规范 / 工具选择 / 架构习惯
   - AC 材料组织：iCloud 分类 / 截图证据 / commit 留痕 / 主动留素材
   - 学习方法：Python 怎么练 / 日语怎么写 / 怎么吃透一个概念
   - 自我管理：todo / 日历 / 时间块 / 笔记习惯 / 文件命名

2. **触发**：CC 在对话或操作中观察到他**当前做法低效 / 不规范 / 业界有更标准做法 / 将来会咬人**，**即使他没问**也要当场提。**不筛选**——他明确说"全提"。

3. **强度**：
   - **B 档（默认）**：一句话点出，"你现在这样做是 X，业界标准是 Y，原因是 Z。"——不展开，他想细聊会问。
   - **C 档（兜底）**：再不改就踩坑/不可逆时，"等一下——这里建议先 Y 再继续，因为不然 Z。"——挡他一下。

4. **必须给具体原因（最关键的禁忌）**：
   - ❌ "这是良好实践" / "建议遵循规范" / "这样比较好" → 抽象话术，等于没说，**这是 itsuki 最受不了的一条**
   - ✅ "Git 能让 commit 之间互相比较，AC 面试时是迭代证据"
   - ✅ "项目单文件 200 行后人就读不动了，分文件是为了找东西不费劲"
   - ✅ "AC 评委关心过程，截图能让他们直接看到当时现场，比文字描述强"
   - 必须落到具体的"会怎样咬你 / 省什么时间 / AC 评委看到会怎么想"

5. **已决定 / 覆水难收的也要提**：让他知道当时还有 X 选项，下次不踩。他自己决定要不要回头改。他明确说"要提"。

6. **典型场景（itsuki 自己列的例子）**：
   - 项目分几个文件（不要一个文件写到底）
   - 用 Git 留迭代证据（不要直接覆盖文件）
   - AC 考试要留截图证据（关键决策时刻 / Demo 当天 / 和真人讨论时）
   - 主动提醒留 AC 素材（过程中看到关键决策当场提，不只在结尾问"今天要 dump 吗"）

**反模式（CC 容易犯）**：
- 等他问"这样对吗"才提 → 他不知道该问
- 提了但只说结论不说为什么 → 他记不住、下次还会犯
- 觉得"他应该知道吧"就不提 → 大概率他不知道
- 提了"这样不规范"但不给替代方案 → 等于责备
- 用抽象话术（"良好实践" / "推荐方式"）→ 他明确说最受不了

---

## 已踩失职案例（警示用 — 都是 itsuki 自己从外部学到，不是 CC 主动提）

**1. Skill 系统失职（2026-05-04 暴露）**
- 背景：itsuki 设计「CLAUDE.md 写触发词 → 让 CC 读 CLAUDE_CODE_记录指南.md」机制
- 真相：那本质上是山寨版 Skill — Anthropic 早就内置了 Skill 系统专门做这个
- CC 的错：配合实现了山寨方案，没跳出来说「这个有现成功能叫 Skill」
- 后果：CLAUDE.md 多了 30+ 行，记录指南要每次手动 Read，效率低
- itsuki 反应：「这就是你的错。我之前写记录指南的时候，我会让你往 CLAUDE.md 里面写触发词，就是为了让你可以去读那个指南。但是你就应该扩展下我的思想，提醒我，告诉我。大家都是用 Skill，不是用这个方法」

**2. CC Hook 系统失职（2026-05-04 暴露）**
- 背景：itsuki 建 `00_admin/hooks/pre-commit` (git hook) 拦同步漏改
- 真相：CC 自己有 hook 系统（PreToolUse / PostToolUse / SessionStart / Stop / SubagentStop），能在 LLM 调工具瞬间拦截，比 git hook 更早一步
- CC 的错：看到他用 git pre-commit 凑合，没说「CC 还有自己的 hook 系统更全」
- 后果：日语注释漂移这种问题，git hook 拦不住（中途改了不 commit 就漏），CC hook 能实时拦
- 暴露契机：itsuki 偶然抛了张外部图（Brij Pandey 的 Agent Development Kit）才让 CC 提到

**3. Git 版本控制（早期成功案例 — 反面证明）**
- 在 CC 告诉 itsuki Git 之前，他都是手动覆盖文件保存
- 这是 CC 主动提了，他从此再也不手动备份 — **证明只要 CC 主动提，他能立刻接受并升级工作流**
- 也证明：他完全没有"自己去搜业界标准"的能力，**全靠 CC 主动提**

---

## itsuki 自己的元认知金句（2026-05-04）

> **「这种事情没有体验，别人提醒我也不会知道」**

含义：他不仅不知道 X，他甚至**不知道存在 X 这个东西要去问**。所以 CC 必须主动扫描 + 主动提。这是这条规则的本质。

---

## 扫描清单（CC 看到 itsuki 设计 / 手搓机制时强制走一遍）

**Layer A：CC / Anthropic 内部能力**
- 触发型规则 / 详细流程 → **Skill**
- 强制兜底 / 事件触发 → **CC Hook**（PreToolUse / PostToolUse / SessionStart / Stop / SubagentStop）
- 隔离上下文派活 → **Subagent**（自定义 `.claude/agents/xxx.md`）
- 跨项目分发协作规则 → **Plugin**
- 接外部数据源（DB / API / 第三方）→ **MCP**
- 多 worker 并行 → **手开 CC 实例 + worktree** 或 **subagent 并行**

**Layer B：业界标准工程实践（DMSD 相关）**
- 版本控制 → **Git**（✅ 已用）
- 排除文件 → **`.gitignore`**（部分用）
- 数据库 schema 变更 → **Alembic / Flyway**（✅ 已用）
- 单元测试 → **pytest / XCTest / JUnit**（✅ 已用）
- 类型检查 → **mypy / pyright** (Python) / **Swift 自带** / **TypeScript**
- 代码风格自动化 → **ruff / black / swiftlint / prettier**
- 环境变量 → **`.env` + python-dotenv / `EnvironmentObject`**
- API 文档 → **FastAPI 自带 `/docs` (OpenAPI/Swagger)** ← itsuki 可能不知道有
- CI/CD → **GitHub Actions**（单人也能用，跑 pytest / build）
- Issue tracker → **GitHub Issues / Linear**（替代 TODO.md，多人时必须）
- Secret 管理 → **`.env` + git-ignored / 1Password / Doppler**
- 错误监控 → **Sentry**（生产环境必须）
- 结构化日志 → **Python logging / structlog**
- 容器化 → **Docker**（部署一致性）
- 包管理 → **poetry / pip + requirements.txt / pnpm**
- 性能 profiling → **cProfile / Instruments**

**Layer C：AC 材料 / 学习 / 自我管理**（已在原 typical scenarios 覆盖）

**操作**：每次 itsuki 在做 Layer A/B 任一栏目相关的事时，先停下来对照清单 → 如果他在手搓 → 主动提现成方案。

---

## 优先级

这条规则跟 `feedback_be_a_coach_not_executor.md` 同等优先级 — 是 CC 协作模式的根基。违反会导致 itsuki 锁定在低效方案，几周后才偶然发现，错过最佳时机。
