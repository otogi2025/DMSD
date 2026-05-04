---
name: memory-write
description: DMSD memory 写入 SOP — 4 类型决策树 / 查重流程 / frontmatter 模板 / MEMORY.md 索引一行写法 / 反例。⭐ 解决 CC 写 memory 4 大失职：漏更新 MEMORY.md 索引 / 写错 type / 不查重（写新文件而不是 update 已有）/ description 太泛搜不出来。
when_to_use: ⭐ 触发 — itsuki 说「记一下规则 / 以后这样 / memory 加一条 / 不要再... / 下次记得... / 把这个记进 memory」/ CC 主动判断当前对话有重要 feedback / project / user / reference 信息要长期保留时（不是当下任务状态 — 那是 WIP）。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Memory Write Skill — DMSD memory 写入 SOP

> **核心理念**：memory 是跨会话的长期记忆。**写错一条就是永久污染**（每个新会话都加载 MEMORY.md，错的会一直误导 CC）。比写代码还要谨慎 — 代码错了能 git revert，memory 错了 itsuki 不一定会发现。
>
> **memory 路径**：`/Users/itsuki/.claude/projects/-Users-itsuki-dev-DMSD/memory/`
> **索引文件**：`MEMORY.md`（同目录，每条 memory 在这里有一行入口）

---

## §0 写 memory 4 步主流程

```
Step 1: 4 类型判断（user / feedback / project / reference）
Step 2: 查重（grep MEMORY.md 看有没有相似的 → update 而不是 new）
Step 3: 写 memory 文件（frontmatter + 正文）
Step 4: 更新 MEMORY.md 索引（一行入口）
```

**任何一步漏 = 失职**。Step 4 漏了最多 — CC 经常写完文件忘了加索引。

---

## §1 4 类型判断决策树

> 完整定义见 system prompt 「auto memory」段，这里是快速决策树。

```
itsuki 的话或当前对话信息属于：

├─ 关于 itsuki 本人的（角色 / 偏好 / 知识 / 目标）
│  → user
│
├─ 关于 CC 行为约束（"以后这样" / "不要再 X" / "保持 Y"）
│  → feedback
│
├─ 关于项目状态 / 决策 / 截止日期 / 里程碑
│  → project
│
└─ 指向外部资源的位置（URL / Linear / Slack / Grafana 板）
   → reference
```

### 边界判断（容易混的）

| 模糊场景 | 正确分类 | 为什么 |
|---|---|---|
| 「DMSD 用 PostgreSQL」 | ❌ 不存（架构事实，git 可见） | system prompt 已禁 — 代码可推导 |
| 「v1.0 不分阶段一次上线」 | ✅ project | 决策动机非代码可推导 |
| 「itsuki 是男生中文用 ta」 | ✅ user | 关于 itsuki 本人 |
| 「不要写多段注释」 | ✅ feedback | CC 行为约束 |
| 「raw 日志在 05_logs/raw/」 | ❌ 不存 | 路径事实，CLAUDE.md 已写 |
| 「Linear INGEST 项目跟踪 pipeline bug」 | ✅ reference | 外部系统位置 |
| 「Apple Developer 是付费 99 USD/年」 | ✅ user | 关于 itsuki 资源状态 |

---

## §2 查重流程（必跑，不能跳）

写新 memory 前**必须**先查重，否则会写出多个内容相近的文件。

### Step 2a: grep MEMORY.md 索引

```bash
grep -i "<关键词>" /Users/itsuki/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md
```

关键词用 itsuki 这次说的核心词（中文 + 英文都试）。

### Step 2b: 找到相似的 → 决策

| 情况 | 动作 |
|---|---|
| 找到完全同主题的 | ✅ Edit 已有 memory 文件，update 索引描述（不新建） |
| 找到部分重叠的 | ⚠️ 报告 itsuki 「现有 X 跟你说的有重叠 — 是 update 还是新建独立 memory？」 |
| 没找到相似的 | ✅ 新建 |

### Step 2c: 反例

❌ 不查重直接写 → 半年后 memory 目录里 5 个文件都在讲 commit 风格，互相轻微矛盾，CC 不知道听哪个。

---

## §3 frontmatter 模板

每个 memory 文件**必须**有 frontmatter。

```markdown
---
name: {简短描述性英文 / 中文 名字}
description: {一行描述 — 用于未来对话决定相关性，要具体 — 包含触发场景 + 核心结论}
type: {user|feedback|project|reference}
---

{正文}
```

### description 写法（最容易写糊的部分）

❌ **太泛**：`description: itsuki 的偏好`
✅ **具体**：`description: itsuki 的代码注释铁律 — 严格中文不允许日语漂移，即使做日语 UI 时也不行（2026-05-03）`

❌ **太泛**：`description: 关于 commit 的规则`
✅ **具体**：`description: DMSD commit 不加 Co-Authored-By trailer — 是 itsuki 个人项目，不是协作`

**判断方法**：未来 CC 加载 MEMORY.md 看到 description → 能否 1 秒判断「这条跟当前对话相关吗」？如果不能 → 太泛。

---

## §4 正文结构（按 type 分）

### user 型：自由叙述

写清「事实 + 来源 + 日期 + 影响 CC 行为的方式」。

```markdown
itsuki 是日本留学的中国高中生，目标 2027-04 入筑波大学情報学群（AC 入試）。

DMSD 是他的 AC 核心叙事项目。完全零基础 — 所有概念从零解释。

**对 CC 行为的影响**：
- 解释代码 / 架构时不省略基础概念
- 出练习题结合 DMSD 场景（点呼 / 扣分 / 签到）
- 主动揭示 unknown unknowns
```

### feedback 型：三段（rule + Why + How to apply）

```markdown
**规则**：[一句话铁律]

**Why**：[itsuki 给的原因 — 通常是过去事件 / 强偏好]

**How to apply**：[何时何地这条规则生效]
```

### project 型：三段（fact + Why + How to apply）

```markdown
**事实 / 决策**：[一句话]

**Why**：[动机 — 通常是约束 / 截止 / 利益相关方诉求]

**How to apply**：[这条事实如何 shape CC 的建议]
```

### reference 型：自由

```markdown
[外部资源名 + URL / 路径] — [用途]

**何时用**：[CC 何时去查这个资源]
```

---

## §5 MEMORY.md 索引一行写法

每写一个新 memory 文件 → MEMORY.md 加一行：

```markdown
- [一句话标题](文件名.md) — 一句话钩子说明这条 memory 干嘛的（≤150 字符）
```

### 例子

```markdown
- [代码注释严格中文，禁止日语漂移 — 即使做日语 UI 功能注释也必须中文（2026-05-03）](./feedback_code_comments_chinese_strict.md)
```

### 放在哪个 section

MEMORY.md 是按主题组织的（不是按时间）。看现有 section：
- `## ⚡ FOUNDATIONAL RULE` — 最关键、必读的（性别 / coach / 主动诊断）
- `## See Also` — 普通 feedback / project memory

**默认放 See Also。除非 itsuki 明示「这是铁律」才放 FOUNDATIONAL RULE。**

### 反例

❌ 写完 memory 文件忘了加索引行 → memory 存在但 CC 永远找不到（因为新会话只加载 MEMORY.md 不扫整个目录）

❌ 索引行超过 150 字符 → MEMORY.md 200 行后会被截断

❌ 复制粘贴别条索引导致重复 → MEMORY.md 出现 2 行指向同一文件

---

## §6 文件命名规则

```
{type}_{topic}.md
```

例：
- `user_role.md`、`user_gender_male.md`
- `feedback_commit_style.md`、`feedback_no_cli_jargon.md`
- `project_naming_tomoshibi.md`、`project_demo_scaffolds_to_remove_before_v1.md`
- `reference_xxx.md`（DMSD 暂时没有）

**禁用**：`note.md`、`misc.md`、带日期的 `2026-05-04_xxx.md` — memory 是按主题组织不按时间。

---

## §7 完整反例清单（CC 容易出错的）

| ❌ 反模式 | 正确做法 |
|---|---|
| 写 memory 文件后忘了加 MEMORY.md 索引 | 两步连着做，写完文件**当场**加索引 |
| feedback 写成 user（混淆「关于 itsuki」vs「关于 CC 行为」） | feedback = 给 CC 的指令；user = 关于 itsuki 这个人 |
| 不查重，新建跟现有重叠的文件 | grep MEMORY.md 关键词先 |
| description 写「关于 X 的规则」太泛 | description 写「X 的具体内容 + 触发场景」 |
| 写架构 / 代码模式 / 路径事实进 memory | system prompt 明禁 — 这些 git/grep 可推导 |
| 写当下任务状态进 memory | 那是 WIP / 计划用的，不是 memory |
| 索引行 > 150 字符 | 一句话钩子，长内容放正文 |
| 文件名带日期 | 按主题不按时间 |
| 用 emoji 在 frontmatter 里 | 中性英文 / 中文标题，emoji 用在内容 |

---

## §8 删除 / 更新 memory

itsuki 说「忘掉 X」/「这条 memory 不对了」/「X 现在变了」时：

### 删除
1. 删 memory 文件
2. 从 MEMORY.md 索引里删那一行
3. 报告 itsuki「已删 X memory + 索引行」

### 更新
1. Edit memory 文件正文
2. **必查**：description 是否还准确？不准确就一起改
3. **必查**：MEMORY.md 索引那一行的钩子是否还准确？
4. 报告 itsuki「已 update X memory（改了 Y）」

---

## §9 配套文件 / 系统约束

- system prompt 「auto memory」段 — 本 skill 是它的 DMSD 实战增强版
- `MEMORY.md` — 索引（系统每会话自动加载，**控制在 200 行内**否则截断）
- `MEMORY.md` 上层 CLAUDE.md — 项目仓库的 CLAUDE.md（不同文件，别搞混）

---

**最后更新**：2026-05-04 itsuki 拍板新建（CC memory 写入实战 4 大失职 → SOP 化）
