# 2026-05-14（晚段）— Tango 项目立项 + grill-me 12 题设计讨论 + 跨项目 bootstrap

> 主会话：DMSD 上下文 / Opus 4.7 1M / itsuki 提"做个记单词网站"启动 → grill-me skill 12 题完整设计讨论 → cc-project-template 起 Tango 骨架 → 跨项目 bootstrap → stop 等推进
> 主线：派生 AC 项目立项 → 12 题设计决策树 → itsuki 推翻 CC 4 次 → cc-project-template 治理框架首次实战 → bootstrap 自动化流程踩坑修复

---

## A. 项目立项 — 派生 AC 项目想法

### 背景 / 触发

itsuki 启动后第一句话提议做"基于遗忘曲线的记单词网站"，明确说"也是 AC 素材，我遇到了很多英语单词不会、记不住的问题。然后想出了这个解决办法"。

### 关键判断

itsuki 主动识别"我做 DMSD 时遇到背单词难"= 派生痛点。不是 CC 提议，是 itsuki 主动从 DMSD 准备过程中抽出的副线项目。同时主动想到调 grill-me skill（"我记得我有个 skill 是专门开始讨论一个新的项目"）— 工具复用意识。

### itsuki 原话 ⭐

> "可以做一个记单词网站，利用遗忘曲线，我输入进单词，然后背。网站根据遗忘曲线自动分配哪天要复习哪些内容。"
> "我想最后搭载到我自己的 VPS 上面，这样我在哪里都可以打开网站。"
> "我记得我有个 skill 是专门开始讨论一个新的项目，然后非常详细的讨论的。"

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#問題発見 #自己認識
- 展示：主动识别派生痛点 + 想到"工程能力解决学习问题"思路 + 记得自己设过 grill-me 适合这种讨论 + DMSD/Tango 双叙事维度（为他人 vs 为自己）
- 模式：1（问题→方案）+ 4（DMSD v1 → Tango v2 派生）

#AC候选 #问题发现 #自我认识 #派生项目 #模式1 #模式4

---

## B. grill-me 12 题设计讨论 — 系统化决策树

### 完整 12 题拍板表

| Q | 主题 | 拍板 |
|---|---|---|
| Q1 | 项目独立性 | A — 独立项目 + 独立 VPS + 共享域名 |
| Q2 | 时间盒 | MVP 先 Web → App 后续 → 上 App Store + 推广（itsuki 修正 CC 推荐）|
| Q3 | 算法野心 | B — SM-2 改造 + 后续机器学习 + 真做研究 |
| Q4 | MVP 范围 | 英语 only，日语推后到上 App Store 前 |
| Q5 | 技术栈 | A — FastAPI + Jinja2 + SQLite + Vibe Coded UI |
| Q6 | 单词卡字段 | A — 最小（front + back）|
| Q7 | 多单词本 | B — 多单词本（Quizlet 心智）|
| Q8 | Quizlet 导入格式 | `-` / `,` 用户选 + 强制前后空格 + 切第一次出现 + 预览 + 报告失败行 + 不查重 |
| Q9 | SM-2 评分 | A — Anki 标准翻译（忘了/难/一般/简单）+ 4 档 + Anki 默认倍数 |
| Q10 | 项目名 | Tango（単語罗马字 + 探戈双关）+ displayName Tango暗記 / Tango背词 |
| Q11 | 看板信息层级 | B — 完整 dashboard + 数据库全量记录 review_log |
| Q12 | 研究计划 | 3-4 篇核心论文 + 双语笔记 + 存 GitHub repo `research/` + L1/L2/L3 切分 |

### itsuki 主体性证据

- 12 题全部 itsuki 拍板，CC 只提推荐 + 让 itsuki 选
- itsuki 推翻 CC 4 次（详 §C）
- itsuki 主动提扩展点（"自动识别动名词"v0.2+）
- itsuki 主动 set 算法野心高度（"原创算法证明能力实力"+ 学机器学习神经网络）

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #問題解決 #自己認識
- 展示：系统化决策能力 + 取舍意识 + 主动 push 自己提技术深度
- 模式：6（取舍三角，每题都有取舍）+ 1（问题→方案）

#AC候选 #模式6 #模式1 #技术判断 #grill-me #决策树

---

## C. itsuki 推翻 CC 4 次 — 主体性强证据

### 推翻 1（Q2 时间盒）— "跟 DMSD 平行做 + 上 App Store + 推广"

CC 推荐 A 极简 MVP（1-2 周）。itsuki 推翻选升级版："跟 DMSD 平行做 + 上 App Store + 推广"。CC 当下 raise 3 个根本冲突：

1. 时间盒物理不可能（5 件事塞 3 个月）
2. 网站 ≠ iOS app（要做 2 个产品工作量翻倍）
3. 推广 ≠ AC 准备资源（吃时间不直接产 AC）

itsuki 听完修正路线：**MVP 先 Web → App 后续 → 上 App Store + 推广** — 不放弃但分顺序。

### 推翻 2（Q8 分隔符）— "手机用户没 Tab 键"

CC 给分隔符选项包含"空格"和"Tab"（按 Quizlet 默认）。itsuki 推翻：

> "用户自己选。不要说 tab 了，手机用户怎么 tab？"

⭐⭐⭐⭐⭐ CC 一直在桌面端思维 — itsuki 一眼戳穿"移动端没 Tab 键"。CC 后续把"移动端优先"作为 MVP 隐含设计原则。

### 推翻 3（看板范围）— "vibe coding 不能按手工搓估时"

CC 因为时间盒紧推 A+ 极简看板。itsuki 选 B 完整 dashboard + 拍板：

> "别拿手工搓需要花的时间来评估现代 vibe coding 所需要花的时间"

⭐⭐⭐⭐⭐ **CC 估时方式根本错** — CC 一直按"手工搓"估 MVP 2-2.5 周，按 vibe coding 实际 3-5 天。CC 全面修订时间盒认知。本认知**影响后续所有项目工作量估算**。

### 推翻 4（域名策略）— "独立项目就独立域名"

CC 默认假设 Tango 共享 DMSD 域名（永久）。itsuki 修正：

> "域名暂时只有一个，如果这个项目独立的话，我肯定会专门去租或者买域名"

CC implication：代码不绑死域名 → 用环境变量。Tango v1.0 后会迁专属域名。

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #自己認識 #分歧
- 展示：主体性 5/5 + 跨设备思考（移动端）+ 用工具方式跟时代（vibe coding ≠ 手工）+ 长期视野（域名独立买）
- 模式：5 主线（每次推翻都是 itsuki 用自己框架修正 CC）+ 2 假设崩（CC 多次假设崩 → itsuki 真因）

#AC候选 #模式5 #模式2 #分歧 #推翻

---

## D. 算法野心 + 研究计划 — "先研究后实现"路径

### itsuki 原话 ⭐

> "我选择 SM2 改造版，加自己的创新参数。先上线这个，再做个性化机器学习。我要学会机器学习，神经网络。然后我也会做研究，我要做详细的研究计划。比如说读一些论文，读一些书，尽可能的做到极限。"
> "我先把这个领域研究了。有了自己的想法，明白了，然后再去做出自己新的算法。"

### CC 当下教 unknown unknowns — 闭门造车反向证据

CC 一上来抛"原创算法陷阱"教学：

> "教授看你的'原创算法'，第一件事是查：你有没有读过这个领域的现有研究？如果不知道前人做了什么就发明算法 → 结论：'这个学生不会做研究'。"

教间隔重复算法历史 30 秒速读：Ebbinghaus 1885 → Leitner 1972 → SM-2 1985 → FSRS 2023+。

### 3 层切分（CC 提案 + itsuki 接受）

CC 看到 itsuki 想"3 个月学完机器学习 + 神经网络"raise 第二次时间盒冲突，propose 3 层切分：

| 层 | 时间 | 内容 |
|---|---|---|
| L1 | 现在 → 2026-08 出愿 | 读 2-3 篇论文 + 实装 SM-2 改造 + 真实数据验证 |
| L2 | 2026-08 → 11 面试 | 扩展阅读 + 机器学习入门 |
| L3 | 入学后 → 大学期间 | 神经网络 + 个人记忆模型 |

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #自己認識
- 展示：研究态度（不闭门造车）+ "先研究后实现"方法论 + 学术延伸性极强（认知科学 → 算法 → 机器学习 → 神经网络）
- 模式：4（v1→v2 演化）+ 6（取舍 — 不一次到 C 分 3 层）

#AC候选 #模式4 #模式6 #研究态度 #算法

---

## E. cc-project-template 治理框架首次实战 — 元层 v1→v2

### 背景

itsuki 让 Tango 独立到 `~/dev/`。CC 没记忆这套底层结构，调 Explore agent 找。Agent 报告：`~/dev/cc-project-template/`（26 文件骨架）+ `~/.claude/项目治理框架.md`（6 原则 / ABC 分类 / SOP / 反模式）— itsuki 2026-05-10 跟 CC 一起设计的跨项目治理 v1.0。

### Tango 是这套治理框架的**首次实战**

5-10 起稿 v1.0 + v1.1 反模式补丁 → 5-14 Tango 立项当天就用上。**治理本身就是 AC 素材**（治理框架 §1.5「元层治理」）。

### 工程动作 + 踩坑

CC 跨项目操作 `~/dev/tango/`：

**Bootstrap 主流程**：

1. `cp -r ~/dev/cc-project-template ~/dev/tango`
2. `mv .git /tmp/cc-template-old-git-*` 清模板 git
3. perl 替换 5 占位符跨 13 文件
4. sed 删 CLAUDE.md bootstrap 段
5. perl YYYY-MM-DD → 2026-05-14
6. Write 重写 README.md / 项目宪章 v0.0.0
7. git init + 首次 commit `addbfde`
8. ac-radar startup_check 跑无紧急提醒

**后续扩展**：

- git rm 起新项目.md（模板 SOP，Tango 不带）
- git branch -m main（DMSD 一致）
- sed 改 install.sh "DMSD" → "tango"
- sed 改 sync-rules.sh 扩展名白名单 → `py|html|js|css`
- 跑 install.sh → `git core.hooksPath = 00_admin/hooks`
- Write 重写 `.claude/CLAUDE.md` Tango 专属版
- Write 重写 TODO.md（15 个 T + 9 条 G 治理）
- Edit WIP.md 修 hook 拦截 → commit `0467ed6`

### Bootstrap 踩坑 + 修

**坑 1 — bash for word splitting 失败**：

```bash
for f in $FILES; do perl ... "$f"; done   # ❌ perl 拿整个 $FILES 当一个文件
```

修：改单 perl 多文件 args 一行命令处理多文件。

**坑 2 — pre-commit hook 拦截 commit 2 次**（治理系统真在工作）：

- WIP.md L11 `v0.1.0（项目刚起，骨架阶段）` 违反单源真值 → 改成"见 CHANGELOG.md 顶部"
- WIP.md L26 `项目宪章 v0.0.0` 误检版本号 → 行尾加 `<!-- VERSION_OK -->`

**这两次拦截验证了治理系统跨项目复用** — DMSD 设的 hook 在 Tango 同样起作用 + 防 itsuki 默认踩"硬编码版本号"反模式。

### AC 价值 ⭐⭐⭐⭐⭐

- 对应核心问题：#技術判断 #自己認識 #問題解決
- 展示：治理框架复用 + 跨项目工程纪律 + bootstrap 自动化首次实战发现 2 个坑都被治理工具兜底
- 模式：4（治理 v1→v2 演化）+ 5（治理系统实战暴露反模式 + 修复）

#AC候选 #模式4 #模式5 #治理 #cc-project-template

---

## F. CC 沟通问题 hook 触发 — 实战

### 背景

itsuki 回答 5 题拍板时含"我不理解 master 和 main 有什么区别"。`user-prompt-comm-priority.sh` hook 触发 — "不理解"是沟通问题信号词（5-12 加严的规则）。

### CC 当下应对

1. 停下手头其他事
2. 当下解释 master vs main（BLM 改名 + 技术上没区别 + DMSD 用 main）
3. 当下质疑 "SC26 是什么"（itsuki 最后说"专属于 SC26 的 claude.md" — CC 不猜，按 cc-comm-rules 规则 4 当场问）

### itsuki 确认 SC26 是 Tango 笔误（语音输入打错）

### AC 价值 ⭐⭐⭐⭐

- 展示：CC 不猜的工程纪律 + hook 实战拦截有效 + cc-comm-rules v0.5.0（5-14 早上才拍板）当晚就实战触发
- 模式：5 元层（沟通规则系统当日实战验证）

#AC候选 #模式5 #沟通规则 #hook

---

## G. CC 自我认知 — vibe coding 边界

### 关键学到

itsuki 拍板 vibe coding 估时后，CC 当下补一条**诚实 raise**（不顺从）：

> "vibe coding 不是万能：算法逻辑（SM-2 公式）必须人审 / 数据迁移 + schema 变更人要看 / 真实部署调试要登服务器。'AI 起草 + 人深度 review' 才是真正的 vibe coding。不是'AI 写完就上'。"

### AC 价值 ⭐⭐⭐⭐

- 展示：CC 不盲从（be a coach not executor 在工作）+ 不矫枉过正（不否定 vibe coding，只补具体边界）
- 模式：5（认知边界）+ 6（取舍 — vibe coding 用在哪 vs 不用在哪）

#AC候选 #模式5 #模式6 #vibe-coding

---

## H. CC 主动 raise unknown unknowns 列表（本会话累计）

| # | 信号 | 价值 |
|---|---|---|
| 1 | 闭门造车反向证据（Q3）| 教 itsuki "原创算法" ≠ 从零造，要读论文 + 改造 |
| 2 | App Store 撞车预警（Q10）| Tango 名几乎肯定被占，需 displayName 修饰 |
| 3 | 空格 + 减号分隔符陷阱（Q8）| `look forward to` / `well-known` 会被切错 |
| 4 | vibe coding 不万能（看板讨论）| 算法 / schema / 部署必须人审 |
| 5 | DMSD 残留 9 处治理 TODO（bootstrap 后）| 6 个 skill 共 197 处不一次清，边开发边清 |
| 6 | 跨项目脏改反模式 4.7（bootstrap 中）| CC 主动 propose 分工，明示授权才动 |

CC 主动诊断 6 次实例 — `feedback_proactive_diagnose_unknown_unknowns` memory 正向验证。

### AC 价值 ⭐⭐⭐⭐⭐

#AC候选 #模式5 #unknown-unknowns

---

## I. AC 价值汇总

### 模式 5（itsuki 主线 — 认知改变型）

| # | 信号 |
|---|---|
| 1 | 4 次 itsuki 推翻 CC — 每次都是 itsuki 框架修正 CC |
| 2 | 6 次 CC 主动诊断 unknown unknowns |
| 3 | 治理框架 cc-project-template 首次实战 — 元层治理 |
| 4 | bootstrap 治理 hook 2 次拦截 — 系统跨项目复用验证 |
| 5 | cc-comm-rules v0.5.0 当日实战触发 + 修正 |

### 模式 6（取舍）

| # | 取舍 | 路径 |
|---|---|---|
| 1 | MVP 先 Web → App 后续 | 不平行做两端 |
| 2 | 算法 3 层切分 L1/L2/L3 | 不一次到机器学习 |
| 3 | 单词卡字段最小（front+back）| 不堆音标例句词性 |
| 4 | 多单词本 vs 单池子 | Quizlet 心智 + 多本 |
| 5 | 栈跟 DMSD 重合不丢分 | 业务领域才是 AC 核心 |
| 6 | DMSD 残留边开发边清 | 不一次重写 6 个 skill |

### 模式 4（v1→v2 演化）

- DMSD（v1 核心）→ Tango（v2 派生）双 AC 叙事维度
- SM-2 → SM-2 改造 → 机器学习版（算法演化路线）
- cc-project-template v1.0 → 5-14 Tango 首次实战

### 模式 2（假设崩 → 真因）

- "Tab 是合理分隔符"假设崩 — 手机用户没 Tab
- "手工搓估时"假设崩 — vibe coding 时代不同
- "Tango 名字 OK"假设 — App Store 几乎肯定撞车

### 主体性 5/5

itsuki 主动提需求 + 推翻 CC 4 次 + 拍板 12 决策 + 明确 AC 后路线 + 跨项目治理复用

### 学术延伸性

认知科学（Ebbinghaus 遗忘曲线）→ 间隔重复算法（SM-2）→ 机器学习（FSRS）→ 神经网络 → 个人记忆模型 — 完整学习路径跟情報学群方向直接挂钩

---

## J. 工程动作清单

### Tango 项目（跨项目操作）

- ✅ cp 模板 + 清模板 git + 替换 5 占位符（13 文件）+ 删 bootstrap 段 + 改时间戳
- ✅ Write README + 项目宪章 v0.0.0（含 15 task + grill-me 12 题结果）
- ✅ git init + commit `addbfde`
- ✅ ac-radar startup_check 跑了
- ✅ git rm 起新项目.md + branch -m main
- ✅ 改 install.sh + sync-rules.sh DMSD 残留
- ✅ 跑 install.sh → core.hooksPath 装好
- ✅ Write `.claude/CLAUDE.md` Tango 专属版
- ✅ Write TODO（15 个 T + 9 条 G）
- ✅ Edit WIP 修 hook 拦截 → commit `0467ed6`
- ❌ GitHub repo 未建 / 未 push（itsuki 拍板"只做准备不推进"）
- ❌ 6 个 skill 197 处 DMSD 残留未清（边开发边清 G1-G9）

### DMSD 项目（本会话期间）

- 无内文件改动（早上 commit `16dd939` 已含术语表 + 沟通规则 v0.5.0）
- 本次 session-wrap 起草本 raw 文件 → 之后 commit

### 跨范围合规

- 跨项目操作 → itsuki 明示授权"全你来做"
- GitHub push → itsuki 明示"只准备不推进" → 不 push

---

## K. 残留 / 等 itsuki 拍板

1. **Tango GitHub repo `otogi2025/tango`** — 未建 / 未 push（commit `addbfde` + `0467ed6` 等 push 拍板）
2. **Tango 切新会话开始 Phase 1** — itsuki 拍板时机
3. **6 个 Tango skill 197 处 DMSD 残留 → 9 条 G 治理 TODO 边开发边清**
4. **DMSD 20 commit ahead origin/main**（不是本会话产生）— 等 itsuki 拍板 push DMSD

---

## L. 跟 5-14 早上 raw 的关系

5-14 早上 raw `2026-05-14.md` 是**完全独立的主题** — 沟通规则 v0.5.0 根本方向再调整 + 4 次连续元层翻车 + hook 推全局。

本 raw（晚段，Tango 立项）：

- 没有跟早上 raw 重叠
- 主线完全不同（早上=沟通规则元层 / 晚段=新项目立项 + 跨项目 bootstrap）
- 早上 commit `16dd939` 已落地，包括 cc-comm-rules v0.5.0 + 术语表 ⑰ CC 协作 23 词

**联动点**：
- 早上拍板 cc-comm-rules v0.5.0 — 晚段实战触发 1 次（master vs main "不理解" hook 触发）
- 早上加术语表 ⑰ CC / 工作流协作 23 词 — 晚段产生更多新英语词（grill-me / vibe coding / SM-2 / FSRS / Ebbinghaus / Wozniak / Anki / Quizlet / Jinja2 / SQLite 等）待归档

按 v0.5.0 §2.3.2 — 本次会话产生的新英语词归档术语表是本次收尾必做动作（详见 §7.5 自查清单 #1）。
