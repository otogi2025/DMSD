# 2026-04-10 会话总结（结构化版）

> 这是一份**结构化索引**，配合同目录下的 `2026-04-10_回归日.md`（叙事版）一起使用。
> 叙事版讲"故事"，索引版讲"清单"。两者不重复，各有用途。

---

## 一、高层概览

今天是**停滞一个月后的回归日**。主线任务不是"写代码"，而是"**重新校准工作方式**"。

### 三件大事
1. **环境切换**：VPS → Mac 本地作为主力开发环境
2. **方法论修正**：从"先学完再做"转向"边学边做 + AI 辅助"
3. **建立长效机制**：规则、记忆、文件结构，今天全部沉淀

**产出**：0 行 DMSD 代码，但规则、记忆、反思、问题解决日志、dev_log 全都沉淀下来。

---

## 二、7 个关键决定

| # | 决定 | 理由 | 存在哪 |
|---|------|------|--------|
| 1 | 不补写过去的 dev_log | 补写 = 伪造，AC 看真实过程 | `memory/feedback_dev_log_discipline.md` |
| 2 | 旧 iOS/SwiftUI 代码作废 | 早期试水质量不够 | `memory/feedback_ios_early_code.md` |
| 3 | 主战场切到 Mac 本地 | Xcode 只能 Mac 用 | 全流程验证过 |
| 4 | 学习方法改为"边学边做" | 传统路径在 AI 时代过时 | 待写进 `learning_path.md` |
| 5 | 遵守反 vibe-coding 三铁律 | 防止沦为 AI 代笔 | 待写进 `learning_path.md` |
| 6 | commit 不加 Co-Authored-By | 保持 commit history 干净 | `memory/feedback_commit_style.md` |
| 7 | 暂不租新 VPS | 开发阶段 Mac 够用 | 心里默认 |

---

## 三、知识清单

### Git
commit / HEAD / behind/ahead / fast-forward / diverged / rebase / stash / git rebase --skip / git ls-tree -r / git pull --rebase

### Unicode & 跨平台
同一字符多种字节表示 / NFC（组合形式，macOS git 默认）/ NFD（分解形式，Linux 默认）/ APFS 文件系统 / 跨平台路径账本错配

### 系统 & 命令行
scp（+ 必须从目标方拉不能从源方推）/ mkdir -p / mv / .gitignore / localhost / 127.0.0.1

### 概念
vibe coding（Karpathy 2025/02）/ 边学边做 vs vibe coding / authorization scope（授权范围）/ setup cost vs running cost / metacognition（元认知）/ code laundering（代码走私）

---

## 四、文件产出清单

### ✅ 已入 Git
| 文件 | 位置 | 备注 |
|-----|------|------|
| 反思草稿 | `05_logs_ac/reflection_2026-04-10_一个月的空白.md` | **`【】` 占位符待填** |
| Python 学习日志 | `05_logs_ac/dmsd_app_ideas.md` | 2026-03-12 的学习记录 |
| 学习过程证据 | `05_logs_ac/证据/` 3 张 PNG | 学 Python 时的截图 |
| NFC/NFD 问题日志 | `05_logs_ac/problem_solving/2026-04-10_NFC_NFD_git_pull_failure.md` | Mac 上已写，待 commit |
| 早期 GPT 对话归档 | `99_archive/2025-12_早期GPT对话/` | 已被 .gitignore 忽略 |
| 回归日 dev_log | `05_logs_ac/dev_log/2026-04-10_回归日.md` | 叙事版 |
| 本份会话总结 | `05_logs_ac/dev_log/2026-04-10_session_summary.md` | 索引版（就是这份） |

### 🧠 Claude Code 长期记忆（不进 Git，两端分别保存）
| 文件 | 内容 |
|-----|------|
| `MEMORY.md` | 项目基本信息（已更新 iOS+Android 澄清） |
| `project_structure.md` | 项目结构细节 |
| `physical_environment.md` | 物理环境 |
| `feedback_ios_early_code.md` | 旧 iOS 作废规则 |
| `feedback_dev_log_discipline.md` | dev_log 当天写规则 |
| `feedback_commit_style.md` | commit 不加 trailer 规则（仅 Mac）|

---

## 五、Git 同步状态（截至会话结束）

| 端 | 状态 |
|-----|------|
| **Mac** | 已 push，领先 2 commit 已同步到 GitHub |
| **GitHub** | 最新版本 |
| **VPS** | 已 pull 同步，与 GitHub 对齐 |

**三方状态一致**。另外 Mac 工作树上有 5 个"鬼影 untracked"（NFC/NFD 遗留），不影响使用，待后续清理。

---

## 六、待办清单（按紧急度分三层）

### 🔴 今晚（回归日收尾）
- [ ] 填反思文件的 5 个 `【】` 占位符（只有 itsuki 能做）

### 🟡 本周
- [ ] Mac 上 commit `problem_solving/2026-04-10_NFC_NFD_git_pull_failure.md`
- [ ] 创建并写 `05_logs_ac/learning_path.md`
- [ ] 更新 `progress_overview.md`
- [ ] 清理 Mac 的 `~/dmsd_pull_blockers_backup/` 两个备份目录
- [ ] 处理 `01_specs/临时PDF/` 的鬼影 untracked
- [ ] 把旧 iOS 试水代码归档到 `99_archive/早期iOS试水/`

### 🟢 下周起
- [ ] 转 `.pages` 文件为 Markdown
- [ ] 继续 Python Day 2（for 循环 + list）
- [ ] 搭本地开发环境（Python、PostgreSQL、FastAPI、VS Code）
- [ ] 写第一个 FastAPI "Hello World" 接口

---

## 七、AC 入試 金矿：5 个可以在面试里讲的故事

### 🏆 故事 1：方法论的自我修正
**关键句**："我原本打算按传统路径'先学完 Python 再做项目'，但在一次和 AI 的对话里，我意识到这条路径在 AI 时代已经过时。我主动调整为'边学边做'，同时识别出这种方式的陷阱（vibe coding），并为自己定了三条铁律。"
**展示能力**：元认知、自我修正、批判性思考

### 🏆 故事 2：一个月停滞的诚实反思
**关键句**："我在项目中途停了一个月，回来时什么都不记得。我没有伪造回忆，而是写了一份真实的反思，并从这次'失败'中提炼出'dev_log 必须当天写'的个人纪律。"
**展示能力**：诚实、自我反省、从失败中学习

### 🏆 故事 3：NFC/NFD Unicode 规范化 bug
**关键句**："从 Linux 服务器同步项目到 Mac 时，因为一个日文文件名的 Unicode 规范化差异（Linux NFD / macOS git NFC / APFS 文件系统）导致 git pull 卡在死锁。我和 AI 助手通过 4 步调试解开了它。"
**展示能力**：深层技术理解、罕见 bug 诊断、跨平台意识

### 🏆 故事 4：AI 协作的动态授权管理
**关键句**："和 AI 协作不是'会写提示词'这么简单，而是要动态管理授权范围。初始阶段要严（防止乱跑），执行阶段要宽（防止过度谨慎）。我今天主动在两个状态之间切换过。"
**展示能力**：对 AI 时代新型工作方式的深层认知

### 🏆 故事 5："就是一个 git 的事"的直觉判断
**关键句**："当 AI 给我 6 步的复杂流程时，我质疑：'为什么能有这么多步骤？就是一个 git 的事。' AI 诚实承认它过度设计了。这让我意识到：作为用户，我有责任质疑 AI 的建议。"
**展示能力**：独立判断、不迷信 AI、保持用户主体性

---

## 八、给未来自己的几条提醒

### 🕯️ 对话和文件的关系
**对话会消失，文件会留下**。每次聊完有价值的内容要问："**这个值得毕业成文件吗？**" 不毕业就丢了。

### 🕯️ 学习节奏
**不要一次想做 5 件事**。今天做今天该做的一件事，明天再想明天。一个月的停滞已经证明了"什么都计划但什么都不做"的代价。

### 🕯️ AI 协作
**你是主人，AI 是工具**。AI 会过度设计、会过度谨慎、会走神。你的工作是**在这些时候喊停、质疑、授权、纠偏**。

### 🕯️ AC 入試
**今天的质量远超今天的产出**。一个能做出今天这些反思的零基础高中生，已经在展示大学最看重的能力：**自我认知、方法论思考、跨领域学习力**。不要被"没写代码"吓到。

---

**会话结束时间**：2026-04-10 晚
**会话主体**：itsuki × VPS Claude Code × Mac Claude Code（三方协作）
**下一次会话预期**：填完反思后，开始 learning_path.md 或 Python Day 2
