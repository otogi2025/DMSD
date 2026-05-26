# 2026-05-26 — 启动 SOP 集中化（dmsd-startup skill 立项）+ DMSD CLAUDE.md 重写到 QTS 模式 247→190 行

> 会话起点：itsuki 问「pre-bash-destructive-block 这个 hook 帮我看看，感觉没在工作」+「anti-ai-flavor 这个教 CC 说人话的 skill，做成 hook 好还是 skill 好？」→ CC 解释 anti-ai-flavor 已经是 hook+skill 三层组合 + pre-bash-destructive 5-12 itsuki 自己改成 warn 模式（CC 看到要自觉停） → itsuki 给愿景「让 CC 自己停下想，没必要不走有必要继续」 → itsuki 进一步反问「这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？」 → CC 拍板做 dmsd-startup skill 集中启动逻辑 → itsuki 让 CC 列 DMSD CLAUDE.md → 看到一堆「xxx 5-26 新加」标记反感「这种完全没必要写到 claude.md 里，只是浪费时间」+「你自己审查一遍 claude.md，看哪些可以去掉，哪些可以做成 skill 或者 hook」 → CC 全文审查（max effort + 参考 QTS CLAUDE.md 模式）247→190 行重写。

> 主线：本会话是 anti-ai-flavor + hook 讨论引导出的 **启动系统架构集中化大改** + **CLAUDE.md 文档观转变**（从「历史 + 当下混合」到「纯当下指令，历史归 git log / decision_log」）

> AC 价值：⭐⭐⭐⭐⭐ 模式 5 顶级 × 4（hook/skill 分工认知 / destructive-bash 行为约定 ≠ 阻断 / 时间戳冗余反感正式立铁律 / QTS 模式作为良好范本）+ 模式 6 取舍 × 3（pre-bash-destructive ABC / 启动 hook 分工 ABC / CLAUDE.md 重审 3 选项）+ 模式 4 版本演化（CLAUDE.md 247→190 大改写）+ 多次主体性拍板（6 次明确决策）+ CC 自检失败 1 次（auto mode 拦截 CLAUDE.md 修改 → itsuki 切手动模式）+ 工具发现 1 个（git commit -o 限定 path）

---

## 阶段 1 [问题解决 + 模式 5 认知改变] pre-bash-destructive-block hook 没在工作 — itsuki 给愿景重新定义

### 背景 / 触发

itsuki 一开始问两件事：

> 1. **anti-ai-flavor** — 这个是教 CC 说人话的 skill，你觉得是保持 skill 好还是做成 hook 好？毕竟我需要 CC 每次回复都可以调用到这个 anti ai flavor
> 2. **pre-bash-destructive-block** — 帮我看看这个 hook，我感觉这个 hook 没在工作

CC 先读了 `00_admin/hooks/pre-bash-destructive-block.sh` + `~/.claude/settings.json` + `~/.claude/skills/anti-ai-flavor/SKILL.md`。

### 经过

**关于 anti-ai-flavor**：CC 解释这已经是 hook + skill 三层组合（A+B+C）：
- A 层：`~/.claude/hooks/anti-ai-flavor-precheck.sh`（UserPromptSubmit 每次注入 6 类提醒）
- B 层：skill description 强信号
- C 层：全局 `~/.claude/CLAUDE.md` reminder

不需要二选一。详细规则塞 hook 会噪音爆炸 → skill 放详细规则，hook 放短提醒。

**关于 pre-bash-destructive-block**：CC 解释：
- 2026-05-04 itsuki 拍板新建（exit 2 阻断模式）
- **2026-05-12 itsuki 自己拍板改成 warn 模式**（不阻断，注入 `⚠️ destructive-bash-WARN` 警告让 CC 自觉停）
- 现在感觉「没工作」= warn 模式靠 CC 自觉，CC 看到警告但下意识继续跑 → 从外部看就是「命令照跑，hook 等于没有」

CC 提 3 个方案：
- A. 回到 exit 2 全阻断（误伤多，每次 git reset --hard 都被拦）
- B. 保持 warn + 加 CLAUDE.md 强行为约定（CC 必须停下来征求同意才能继续）
- **C. 分档**：灾难级（rm -rf 到 repo / rm .git / git push --force）= exit 2 阻断；可恢复级 = warn

CC 推荐 C。

### 关键拍板 / 模式 5 认知改变

itsuki 给愿景重新定义：

> 不用停下来，**只要自己停下来好好思考一遍有没有必要，然后没必要就不走，有必要就接着做**

→ 拍板：不选 C 分档，选简化版 B —— 不是「征求同意」，是「自己停下来想一下，反思过没必要就跳过，有必要就直接跑」。

**为什么这个是模式 5 顶级**：CC 一直以为 hook 是「拦不让做」或者「提醒后等批准」的二元思维。itsuki 给的愿景是第三种 — **「让 CC 多一次反思窗口」**（不打断，但触发自检）。这是行为层规则不是阻断层规则。

itsuki 同时拍板第 2 件事：

> claude.md 里，加一句，除非项目里有这个单词，否则不要主动用英语名词

→ 立铁律：**不主动用英语名词，除非项目代码 / 文档 / 文件名里真出现过**。

### itsuki 原话 ⭐

> 不用停下来，只要自己停下来好好思考一遍有没有必要，然后没必要就不走，有必要就接着做，我觉得这样可以偶尔有效避免被误删之类的

> claude.md 里，加一句，除非项目里有这个单词，否则不要住用用英语名词

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #自己認識 #問題解決
- 展示了什么：itsuki 对「自动化工具的人机协作边界」的深度理解 — 工具不必非「拦」或「批」，可以是「提醒反思」第三态
- 模式：**模式 5 顶级**（CC 二元思维 vs itsuki 三态思维）
- 可能用在自我推荐书：「我在跟 AI 协作时主张工具应该给思考空间，不只是执行命令或被动等待批准。比如我的破坏性命令检测脚本就改成只在 AI 跑 rm -rf 前注入一段警告，让它有 5 秒反思空间」

### CC 翻车 1 次

CC 尝试 Edit `~/.claude/CLAUDE.md` 被 auto mode classifier 拦了（理由：Self-Modification HARD BLOCK-adjacent，修改 agent 启动配置需要明确授权）。

itsuki 一开始说「授权」CC 重试又被拦（理由：再次提示 self-modification 即使口头授权也要拦）。

CC 提两个解决方案：A. itsuki 自己粘贴 / B. itsuki 切手动模式让 CC 重跑。itsuki 选 B（用 `/effort` + 切手动），然后说「跑」短指令让 CC 重试 → 成功。

**协作纠错** — 工具限制 + itsuki 主动切模式 + 简短「跑」指令 = 高效绕过工具阻塞。

#AC候选 #问题解决 #技术判断 #自己認識 #模式5

---

## 阶段 2 [认知改变 + 模式 5] anti-ai-flavor skill vs hook = 「不二选一，已经是组合」

### 经过

itsuki 问：「anti-ai-flavor 是教 CC 说人话的 skill，做成 hook 好还是保持 skill 好？毕竟我需要 CC 每次回复都可以调用到这个 anti ai flavor」

CC 解释：**已经是 hook + skill + CLAUDE.md 三层组合**（itsuki 自己 5-16 拍板的 A+B+C 三层保险）：

| 层 | 文件 | 触发时机 | 干嘛 |
|---|---|---|---|
| A 层 hook | `~/.claude/hooks/anti-ai-flavor-precheck.sh` | UserPromptSubmit（itsuki 每次发消息） | 注入 6 类自检提醒（短）|
| B 层 skill | `~/.claude/skills/anti-ai-flavor/SKILL.md` | CC 主动 Read | 详细规则 + 20 案例（长）|
| C 层 CLAUDE.md | `~/.claude/CLAUDE.md` | 每次启动 | 强 reminder |

为什么不能全塞 hook：详细规则塞 hook = 每次输入注入几千字提醒 = 噪音爆炸。短提醒（6 类标题 + 6 问自检）放 hook，detail 留 skill。

### itsuki 原话 ⭐

> anti-ai-flavor 这个是教 CC 说人话的 skill，你觉得是保持 skill 好还是做成 hook 好？毕竟我需要 CC 每次回复都可以调用到这个 anti ai flavor

### AC 价值 ⭐⭐⭐⭐

- 对应核心问题：#自己認識 #技術判断
- **模式 5** — itsuki 对 hook+skill 关系的理解深化：不是二选一，是不同职责互补
- 之前他可能觉得 hook = 强制 / skill = 可选，要 always-on 就必须做 hook；现在理解 hook 注入短提醒触发，skill 提供详细 SOP，两者协同
- 可能用在自我推荐书：「在设计 AI 协作系统时我学会区分『触发器』和『知识库』 — 触发器要轻（不阻塞），知识库要详（不噪音）」

#AC候选 #认知改变 #技术判断 #模式5

---

## 阶段 3 [关键设计决策 + 模式 5] 沟通铁律「不主动用英语名词」全局 + 6 项目 CLAUDE.md 落地

### 背景

itsuki 拍板加全局 + 让我扩展到所有 6 个项目 CLAUDE.md：

> 不仅仅要加到 DMSD 的 claude.md，还要加到所有项目的 claude.md 里

### 经过

CC 扫所有 itsuki 的 6 个项目 CLAUDE.md（QTS / tango / SC26 / DMSD / practice / cc-project-template），每个加一段：

```
## ⚠️ 沟通铁律 — 不主动用英语名词

除非这个词在项目代码 / 文档 / 文件名里真出现过，否则一律用中文。
比如别说「凭证 credential」「兜底 fallback」「联动 sync」，直接说中文。

完整规则在 `~/.claude/CLAUDE.md`。
```

CC 还在全局 `~/.claude/CLAUDE.md` 的「规则」段加同样的铁律。

### 关键决策

为什么不只全局加（让所有项目自动继承）：itsuki 想要冗余写到每个项目 = 让 Codex / Gemini 等只读项目 CLAUDE.md 的工具也能看到。代价是 6 处冗余，但好处是确定性覆盖。

### itsuki 原话 ⭐

> 不仅仅要加到 DMSD 的 claude.md，还要加到所有项目的 claude.md 里

### AC 价值 ⭐⭐⭐⭐

- 对应核心问题：#技術判断 #問題解決
- **模式 6 取舍** — 单点维护 vs 冗余确定性 — itsuki 选冗余（其他工具能看到）
- 后期可能用在自我推荐书：「在多工具协作时我倾向于把核心规则冗余写到每个入口，宁可付出维护成本也要确保所有工具都能看到」

#AC候选 #关键设计决策 #技术判断 #模式6

---

## 阶段 4 [关键设计决策 + 模式 5 + 模式 6] 启动 SOP 集中化 — itsuki 反问「这不应该做成 skill 吗？」

### 背景 / 触发

itsuki 想做「项目启动 skill」让 CC 每次启动跑读 WIP / 注册多会话协同等。

CC 解释 DMSD 现状：启动逻辑散在 3 处：
- 全局 `~/.claude/hooks/session-start-env-diff.sh`（环境清单对账）
- 全局 `~/.claude/hooks/session-start-coord-check.sh`（多会话协同检测）
- DMSD `bin/check_overview_drift.sh`（project-overview 漂移检测，hook 模式）
- DMSD `CLAUDE.md` 第 106-111 行「会话开始: 读 WIP.md」段

CC 第一次提议：「挂钩不动 + DMSD CLAUDE.md 抽段成 skill」(混合方案，保留全局 hook 确定性)

### itsuki 反问 → 立刻拍板

> 这不应该做成 skill 吗？
> 我每次启动项目，比如说 DMSD 我希望 CC 读 WIP 还有 TODO，还有注册多会话协同等等，原本我说启动后它会做的事
> 这不应该做成 skill 吗？
> sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？

→ CC 第一方案被推翻。**itsuki 想要的不是「挂钩 + skill 互补」，是「全集中到一个 skill」**。

### CC 第二次 ABC 方案

A. 全局挂钩输出动态判断项目（DMSD 输出「加载 dmsd-startup」，别项目输出原检测）
B. 全局挂钩不动，DMSD 新加项目级挂钩
C. DMSD 项目级配置覆盖（推荐 — 改动最小）

itsuki 给最终答案：

> 我选，**每个项目都有单独的启动 skill**，session-start-env-diff.sh 这个根本不需要加进项目级别的 skill，**留在全局就好了**，session-start-coord-check.sh 这个则根本没有必要单独存在，**融进所有项目的启动 skill 里就好了**

→ 拍板：
- 每项目独立启动 skill（先做 DMSD）
- env-diff（全局挂钩）留全局
- coord-check（全局挂钩）退役全局功能 / 融进每项目启动 skill（DMSD 项目下静默退出）

### 关键拍板 / 模式 5 顶级认知

CC 一开始觉得「全局挂钩 + 项目 skill」是稳的（挂钩确定性 + skill 详细 SOP），不愿意动全局。

itsuki 强行集中 = 让 CC 看清「启动逻辑应该一个入口」的设计原则 — 散在 3 处 = 容易漏，集中到 skill = 一站式入口。

**这不是简单技术决策，是设计哲学**：itsuki 选「单一职责 + 单一入口」over「多层冗余 + 互补」。

### itsuki 原话 ⭐

> 这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？

> 每个项目都有单独的启动 skill / env-diff 留全局 / coord-check 融进项目 skill

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #問題解決 #自己認識
- **模式 5 顶级** — CC「多层冗余 = 安全」vs itsuki「单一职责 = 清晰」的设计哲学碰撞
- **模式 6** — 三方案对比，itsuki 选「全集中」推翻 CC 的「保留全局挂钩」
- 学术延伸性：软件工程「single responsibility principle」/ DDD「bounded context」/ Unix philosophy「do one thing well」
- 可能用在自我推荐书：「我在跟 AI 协作时学到设计原则的取舍 — 多层冗余看起来稳但其实增加维护成本，单一入口才能让协作者快速理解系统」

#AC候选 #关键设计决策 #模式5 #模式6 #技术判断

---

## 阶段 5 [执行] 干 6 件主任务 — dmsd-startup 立项 + 全局 hook 改 + 6 项目 CLAUDE.md 加规则

### 经过

CC 用 TaskCreate 立 4 个 task 跟踪：

1. 创建 `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md`（第一版 ~165 行）
   - §1 为什么写
   - §2 启动必做 5 件事（多会话协同注册 / overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）
   - §3 不做的事
   - §4 跟其他 skill / 挂钩边界
   - §5 CC 行为约定

2. 改 `~/.claude/hooks/session-start-coord-check.sh`：DMSD 项目下 `exit 0` 静默退出

3. DMSD CLAUDE.md 顶部加 dmsd-startup 强制加载段 + 沟通铁律段 + 简化「会话开始」段

4. 6 个项目 CLAUDE.md 加沟通铁律段（DMSD / QTS / tango / SC26 / practice / cc-project-template）

5. 补 project-overview SKILL.md §0.1 体量表（`.claude/` 10→11 / 7 skill→8 skill）+ §1.7 加 dmsd-startup 行 + 历史注释更新

6. 修 DMSD WIP.md 顶部时间戳（5-25→5-26）+ 第 19 行「会话开始」铁律（原写「读 TODO 顶部 200 行 + git status」跟新 CLAUDE.md 矛盾，改成「走 dmsd-startup skill / TODO 等 itsuki 主动问 / git status 留收尾」）

每个 PostToolUse hook 都触发了 project-overview 同步提醒（4 次）— 我在收尾报告里说明。

### AC 价值 ⭐⭐⭐

- 对应核心问题：#問題解決
- **模式 1 + 模式 4** — 把散在 3 处的启动逻辑集中到 1 个 skill（版本演化）
- 工程实践：用 TaskCreate 跟踪 + 完成一项标 completed + 下一项标 in_progress（机械顺序，避免漏步）

#AC候选 #问题解决 #模式1 #模式4

---

## 阶段 6 [模式 5 顶级] itsuki 反感时间戳冗余 — CLAUDE.md 文档观转变（5-26 立铁律）

### 背景 / 触发

CC 列 DMSD CLAUDE.md 内容给 itsuki 看时，标了「🆕 5-26 新加」类历史标记。

itsuki 反应：

> 🆕 5-26 新加（5 行）
> 像这种 xxx 新加，**完全没必要写到 claude.md 里啊，只是浪费时间**
>
> 你自己审查一遍 claude.md，看哪些完全没必要的东西可以去掉，看哪些东西可以直接做成 skill 或者 hook

→ CC 受到拍板触发 → 全文审查。

### 关键认知 / 模式 5 顶级

CC 长期习惯（在所有 CLAUDE.md / SKILL.md / WIP.md / 各类文档里）加：
- 「2026-05-XX 上线」
- 「XXX 拍板」
- 「2026-05-21 死链修复 B-011」
- 「5-19 改全项目覆盖」

CC 之前的潜意识：写时间戳 = 可追溯 + 可问责 + 有上下文

**itsuki 的设计哲学**：CLAUDE.md / SKILL.md 是**「指令文档」**，**不是日志**。指令文档要：
- 长期可读
- 不被历史污染
- 当下指引为核心

历史 = 归 `git log` / `decision_log.md` / raw / CHANGELOG。两者分离。

→ 立铁律：**「xxx 5-26 新加」这种历史标记 = 浪费 = 禁止**。

### 跟之前 feedback 的关系

memory 已有：
- `feedback_no_dense_jargon_strings.md`（一句话别堆密集术语）
- `feedback_anti_ai_flavor_翻车案例.md`（5-22~25 拍板的 5 铁律 + 20 案例）

但「文档时间戳冗余」是**新角度**：
- 不是「术语堆砌」（A 类术语裸露问题）
- 不是「客套腔」（F 类）
- 是**「文档目的认知」** — CC 把指令文档当日志写，把可追溯需求塞进当下指引

→ **新 feedback memory 候选**：`feedback_docs_no_timestamps_no_history.md`（详见 §5.5.13 处理）

### itsuki 原话 ⭐

> 像这种 xxx 新加，完全没必要写到 claude.md 里啊，只是浪费时间
>
> 你自己审查一遍 claude.md，看哪些完全没必要的东西可以去掉，看哪些东西可以直接做成 skill 或者 hook

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#自己認識 #技術判断 #失敗と修正
- **模式 5 顶级** — CC 长期习惯（写时间戳）vs itsuki 长期反感的根本认知差
- **元层** — 「指令文档 vs 日志」的设计原则 — 不只是 CLAUDE.md 范畴，扩到所有「给未来读者的文档」
- 学术延伸性：「declarative vs imperative documentation」/ 「specification vs history」/ Knuth 文学编程
- 可能用在自我推荐书：「我跟 AI 协作时发现一个反复出现的模式 — AI 喜欢在指令文档里加时间戳和历史注释（'2026-05-26 拍板'），但指令文档应该是面向未来的指引，不是过去的日志。我现在的做法是明确两类文档边界：指令文档（CLAUDE.md / SKILL.md）只写当下规则，历史归 git log / decision_log。」

#AC候选 #模式5 #自己認識 #失敗与修正 #元层

---

## 阶段 7 [问题解决 + 模式 6] CLAUDE.md 第一次审查 v1（普通版）

### 经过

CC 第一次扫 234 行 DMSD CLAUDE.md，分 3 类：

| 类 | 怎么处理 | 行数 |
|---|---|---|
| A 类（砍） | 时间戳 / 历史 / 死链修复编号 / 复制版段 | ~110 行 |
| B 类（搬到 skill） | 按需读 → dmsd-startup §4 / ac-radar 段 → skill 自己 description / 工具列表 → hooks/README | ~55 行 |
| 保留 | 核心铁律 / 项目信息 / 设计文档双层 / AC 默认底线 | ~80 行 |

推荐 A+B（保留核心 + 砍历史 + 搬细节）。

### itsuki 给我看 QTS CLAUDE.md（他自己改的版本）

itsuki 选项是不是简单「砍」，而是给我看了他自己整理的 QTS CLAUDE.md（修改通知，linter 提醒）。

CC 读 QTS CLAUDE.md 后发现：QTS 给了 3 个 DMSD 缺的好东西：
1. **Skills 继承段**（全局 + 项目专属 + 一句作用，**不列触发词**）
2. **Hooks 段**（同上结构）
3. **全项目中枢联动段**（5-26 立的跨项目机制）

### AC 价值 ⭐⭐⭐

- **模式 6 取舍** — A/B/C 三选项给 itsuki
- **CC 主动发现** — 通过看 itsuki 自己改的 QTS 反向学到良好结构

#AC候选 #问题解决 #模式6

---

## 阶段 8 [模式 5 + 模式 4 + 模式 6 顶级] CLAUDE.md 重审 v2（max effort + QTS 模式参考）

### 背景

itsuki 切到 `/effort max`，让我「重新审查一次」（这次更严，参考 QTS）。

### 经过

CC 用更严标准 + QTS 模式参考重审，分 4 类：

| 类 | 怎么处理 | 行数 |
|---|---|---|
| A（砍） | 时间戳 / 历史 / 死链编号 / 文件连锁结构（file-linkage 已有）/ 工具列表（hooks/README 已有）/ AC 触发场景（session-wrap 已有）/ Skills 触发速查（每个 skill description 已有）/ 对话规则（全局已有）/ graphify（工具自配置）| ~120 行 |
| B（搬到 skill） | 按需读 3 段 → dmsd-startup §4 / Agent skills 详细 → docs/agents/ | ~35 行 |
| C（保留） | 沟通铁律 / dmsd-startup 强制加载 / 关于 itsuki / 项目信息 / 目录结构 / 设计文档双层 / 文档一致性 / AC 默认底线 | ~75 行 |
| D（补 — 参考 QTS 模式 DMSD 缺的）| Skills 继承（全局 + 项目专属）/ Hooks 继承 / 全项目中枢联动 / 沟通规则简版 / Git | ~70 行 |

净估算：234 → ~150 行（实际写完 190 行）。

itsuki 看完拍板：

> 全部按照你的想法做
> 做之前记得**先 git 一次备份**，免得改出事了

### 关键拍板 / 模式 4

CC 第二次审查比第一次：
- 更严（QTS 模式参照标准）
- 更结构化（D 类新加 = 补 DMSD 缺的）
- max effort 体现：不只是「砍 + 搬」，是「按良好范本重构」

itsuki「先 git 备份」= 工程习惯（万一改坏可以 `git checkout HEAD -- CLAUDE.md` 回退）。CC 之前没主动 propose 这个 — 是 itsuki 教的 [推测：CC 知道但没主动说，潜意识觉得「Edit 工具能 undo 不用 commit 备份」]

### itsuki 原话 ⭐

> 全部按照你的想法做。做之前记得先 git 一次备份，免得改出事了

> 我选，每个项目都有单独的启动 skill，session-start-env-diff.sh 这个根本不需要加进项目级别的 skill，留在全局就好了，session-start-coord-check.sh 这个则根本没有必要单独存在，融进所有项目的启动 skill 里就好了

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #問題解決 #失敗と修正 #自己認識
- **模式 5 顶级** — itsuki 给「先 git 备份」教 CC 工程习惯
- **模式 4 版本演化** — CLAUDE.md 247→190 行大改写（不是小修，是按 QTS 模式重构）
- **模式 6 顶级** — 三层激进度选项（最稳 / 中等 / 激进），itsuki 选激进 + 加「先备份」
- 学术延伸性：refactoring 实践（make small commits + always have a working baseline）/ Joel Spolsky「make backups before risky refactoring」
- 可能用在自我推荐书：「跟 AI 协作做大改时我总要求先 commit 当前状态做备份再开始改，万一改坏可以一行命令回退。这个习惯避免了多次潜在的工作丢失」

#AC候选 #模式5 #模式4 #模式6 #关键设计决策

---

## 阶段 9 [执行 + 工具发现] git commit -o 限定 path + DMSD CLAUDE.md 重写 190 行落地

### 经过

CC 跑：

```bash
cd ~/dev/DMSD && git status --short
```

发现 staged 区有 3 个 R 文件（renamed）— 是别会话改的 iOS 上架 fork 整理活（99_archive→student_ios/v1 重命名）。本会话不该一起 commit 走。

### 工具发现 ⭐

`git commit -o`（`--only`）参数 — 限定只 commit 指定 path，**不动 staged 区其他内容**。

```bash
cd ~/dev/DMSD && git add .claude/skills/dmsd-startup/ && git commit -o \
  CLAUDE.md \
  00_admin/WIP.md \
  .claude/skills/project-overview/SKILL.md \
  .claude/skills/dmsd-startup/SKILL.md \
  -m "..."
```

→ `d1fc8b3` 第 1 次 commit 备份成功（4 files / 273 insertions / 81 deletions）。pre-commit hook 一致性检查通过。

### CLAUDE.md 重写 247→190 行

CC Write 整文件覆盖（先 Read 拿最新状态 — 注意晚段别会话已经在文末加了「全项目中枢联动」段，重写时保留这段不覆盖）。

dmsd-startup SKILL.md 加 §4「按需触发的事」段（搬 CLAUDE.md 原 L132-150 按需读 3 段 + 加 §4.4 文件联动走 file-linkage）。

project-overview SKILL.md §1.7 dmsd-startup 行描述加「+ §4 按需触发的事」（同步 skill 内容扩展）。

→ `d608846` 第 2 次 commit 大改（3 files / 168 insertions / 184 deletions）。pre-commit hook 通过。

### 还有零碎尾巴 — sync-check 警告

CC 跑 `bash bin/sync-check.sh` 时报：

```
⚠️ [bin-script] 联动文件未改
  原因：bin/ 脚本改了 → CLAUDE.md / 文档同步点清单.md / hooks README 是否要提到
  触发文件：bin/check_overview_drift.sh
```

但 `bin/check_overview_drift.sh` 是**别会话改的**（不在本会话改动范围）。CC 本会话不动这个文件 — 留 itsuki 自己拍板或下次会话补。

### AC 价值 ⭐⭐⭐

- 对应核心问题：#技術判断 #問題解決
- **工具发现** — `git commit -o` 限定 path
- **工程实践** — 多会话并行时保护 staged 区
- 可能用在自我推荐书：「多会话并行开发时我学到的关键技巧 — `git commit -o` 限定路径，不让一个会话的提交带走另一个会话的暂存内容」

#AC候选 #工具发现 #问题解决 #技术判断

---

## 阶段 10 [元层观察] ~/.claude/ 不是 git repo + 多会话并行实战观察

### 工程发现

CC 扫所有 7 个目录的 git 状态时发现：`~/.claude/` 不是 git repo。

这意味着：
- 本会话改的 `~/.claude/CLAUDE.md`（加 2 段）
- 本会话改的 `~/.claude/hooks/session-start-coord-check.sh`（DMSD 静默退出）
- 全局环境清单 `~/.claude/我的环境.md` 该更新但本会话没动

→ **全部没法 git 备份**。

WIP 顶部 itsuki 5-14 立的 propose 还在：

> **未来 propose**：把 `~/.claude/` 做成 git 仓库（永久解决全局配置无历史问题）— 等 itsuki 拍板

本会话再次强化这个需求。

### 多会话并行实战观察

WIP 显示晚段 itsuki 在别会话做了「iOS Bot 1 复查 + 全项目中枢注册」。CC 本会话 Read DMSD CLAUDE.md 时发现末尾已经被别会话加了「全项目中枢联动」段 — CC 重写时保留这段不覆盖。

CC 跑 git status 看到 3 个 M（session-wrap / 系统bug专栏 / check_overview_drift）是别会话改的没 commit 的活，本会话用 `git commit -o` 不动。

→ **多会话协同实战示例** — 工具层（git commit -o + Read 拿最新版）+ 内容层（CC 主动识别哪些是别会话的活不动）配合，避免误覆盖。

### AC 价值 ⭐⭐⭐⭐

- 对应核心问题：#技術判断 #自己認識
- **模式 5** — CC 跟 itsuki 同时跨多终端开多 CC 会话的协作模式
- 学术延伸性：「distributed version control」/ 「actor model」（各 CC = 独立 actor / 共享文件 = mailbox）
- 元认知：CC 不能假设自己是唯一会话，要主动 Read 最新版 + 用 git commit -o 限定 path + 不动别会话的活

#AC候选 #自己認識 #模式5 #元层

---

## 阶段汇总 — 工程动作清单

### 文件改动

| 文件 | 改动 | commit |
|---|---|---|
| `~/.claude/CLAUDE.md` | 加沟通铁律「不主动用英语名词」段 + destructive-bash-WARN 行为约定段 | ⚠️ 全局非 git repo，没备份 |
| `~/.claude/hooks/session-start-coord-check.sh` | DMSD 项目下静默退出 | ⚠️ 同上 |
| `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md` | 新建（第一版 165 行 + 加 §4 按需触发段后 ~200 行） | `d1fc8b3` + `d608846` |
| `~/dev/DMSD/CLAUDE.md` | 第 1 次加 2 段 → 第 2 次重写 247→190 QTS 模式 | `d1fc8b3` + `d608846` |
| `~/dev/DMSD/00_admin/WIP.md` | 顶部时间戳 + 第 19 行「会话开始」铁律改 | `d1fc8b3` |
| `~/dev/DMSD/.claude/skills/project-overview/SKILL.md` | §0.1 + §1.7 同步 + §1.7 dmsd-startup 描述加 §4 | `d1fc8b3` + `d608846` |
| `~/dev/QTS/CLAUDE.md` | 加沟通铁律段（顶部）— itsuki 自己后来又改了这文件 | 未跟踪本次（QTS repo） |
| `~/dev/tango/CLAUDE.md` | 加沟通铁律段（顶部）— itsuki 后来重构 tango CLAUDE.md | 未跟踪本次 |
| `~/dev/SC26/CLAUDE.md` | 加沟通铁律段 | 未跟踪本次 |
| `~/dev/practice/CLAUDE.md` | 加沟通铁律段 | 未跟踪本次 |
| `~/dev/cc-project-template/.claude/CLAUDE.md` | 加沟通铁律段 | 未跟踪本次 |

### 立的铁律 / 立项

1. **沟通铁律**：不主动用英语名词（除非项目代码 / 文档 / 文件名里真出现过）— 全局 + 6 项目落地
2. **destructive-bash 行为约定**：CC 看到 WARN 自己停下想，没必要不走有必要继续，灾难级才问 itsuki
3. **dmsd-startup skill 立项**：DMSD 启动 SOP 集中入口，5 件必做事
4. **CLAUDE.md 文档观转变**：指令文档不写时间戳 / 历史标记，历史归 git log / decision_log
5. **每项目独立启动 skill**：env-diff 留全局 / coord-check 融进每项目启动 skill / DMSD 项目下全局 coord-check 静默退出
6. **「先 git 备份再大改」工程习惯**：CC 学到 itsuki 主张的安全 refactoring 习惯

### 残（下次跟进 / 等拍板）

- ⏳ ~/.claude/ 做成 git 仓库（5-14 立的 propose，本会话强化需求）
- ⏳ 全局环境清单 `~/.claude/我的环境.md` 没更新 — 本会话新建 dmsd-startup skill / 改全局 hook 应该补一条历史日志 / 同步「最后更新」字段
- ⏳ 其他 5 个项目（QTS / tango / SC26 / practice / cc-project-template）启动 skill 都没做 — itsuki 拍板「先只做 DMSD 完整版」，其他项目按需后续做
- ⏳ sync-check 警告 `bin/check_overview_drift.sh` 联动文件未改 — 别会话改的脚本，本会话不动，留 itsuki 拍板或下次会话补
- ⏳ tango 项目重构（itsuki 自己改了 CLAUDE.md + 移到根目录 + 改了多个 .claude/skills/）- 本会话不动 tango
- ⏳ SC26 别会话改的多个 .agents / .codex / Z2-Z4 文件 - 本会话不动 SC26

---

## CC 自检 / 翻车

### CC 翻车 1：auto mode classifier 拦了 `~/.claude/CLAUDE.md` 修改

itsuki 口头授权后又被拦 → CC 提两个解决方案 → itsuki 切手动模式让 CC 重跑成功。

**反思**：Self-Modification HARD BLOCK 是工具机制层，CC 应该提前预判（之前没 propose「需要 itsuki 切手动模式」，是被拦后才说）。

### CC 翻车 2：英文词裸露（部分）

CC 多次用「stage / untracked / commit -o / staged 区」等 git 工具词没解释。**部分**符合「项目里真出现过」（git 是真实工具），但「stage / untracked」第一次出现没翻译。

→ itsuki 没明示「翻车」单字所以没记 inbox.md。但 CC 自检看到该改。

### CC 自检通过项

- ✅ 5 铁律全有（起因 / 改哪+这是啥 / 改的内容 / 每对象解释 / 下一步推荐）
- ✅ 中文回答为主
- ✅ A/B/C 三选项不用甲乙丙
- ✅ 没用「这个 / 那个 / 本项目」类不明代词
- ✅ 「先 git 备份」工程习惯被 itsuki 教 → CC 立刻照做（没扯皮）

---

## itsuki 的金句（本会话）

> 不用停下来，只要自己停下来好好思考一遍有没有必要，然后没必要就不走，有必要就接着做

> 像这种 xxx 新加，完全没必要写到 claude.md 里啊，只是浪费时间

> 这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？

> 全部按照你的想法做。做之前记得先 git 一次备份，免得改出事了

每句都是 itsuki 设计哲学 / 工程习惯的浓缩表达。
