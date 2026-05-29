# 2026-05-29 session-coord 协作板改 hook 自动维护

## 22:30 [认知改变][问题解决][技术判断] itsuki 自己发现协作板机制缺陷 → CC 诊断真因 → 改 hook 自动

### 背景 / 触发

itsuki 启动会话后问「session-coord 这个 skill 你知道是做什么用吗」，CC 读 SKILL.md 解释后，itsuki 直接抛出他自己观察到的三个缺陷：

> "我觉得这个 session coord 不是很有作用，帮我优化一些。比如说，我最开始启动了这个会话，然后让启动的时候它就会注册这个。它会写它会做什么，但是后续我需要它做别的事，它就不会更新它继续做什么了。然后别的会话也不知道它正在做什么，它应该是不会实时更新。然后也不知道实时更新会不会太消耗 token 了，我也不太知道。"

这是 **itsuki 自己发现问题**（模式 2 的起点 + 问题发现能力）—— 不是 CC 提的，是他用了之后自己察觉「注册完就不更新、别的窗口看不到、怕费 token」。

### 经过

1. CC 没有直接动手，先读了所有脚本（register / scan / status / claim / end）确认 itsuki 说的对不对 → 结论：**全对**。
2. CC 诊断出根本原因：这套机制设计上「能」实时更新（有 status.sh / 每回合 scan 的设计），但更新全靠 CC 每回合自觉跑脚本，而 CC 不自觉 → 「当前任务」永远停在注册时那句话 → 整套等于摆设。
3. CC 指出这正好撞在 itsuki 之前立的一条铁律上（memory `feedback_mechanism_over_self_discipline.md`）：同类问题反复犯就别靠「以后注意」，要立 hook 机制兜底。
4. CC 用 AskUserQuestion 问了两个关键问题（决定方案 ROI）：itsuki 答「几乎每天多窗口并行」+「防撞车和知道对方在干嘛两个都想要」。
5. CC 派 claude-code-guide 子代理查证 hook 输入规格（关键技术前提），确认：hook 能从后台拿到 session_id（整个会话不变）、prompt 原文、cwd；且 hook 不往 stdout 打字就零对话 token。
6. CC 实测发现环境变量 `CLAUDE_CODE_SESSION_ID` = 当前窗口会话编号，跟 hook stdin 的 session_id 同值 → 身份证天然统一。

### 关键判断 / 学到的东西

**最终方案**：把「维护协作板」从靠 CC 自觉跑脚本，整个搬到 hook 后台自动做。
- 新建 `session-coord-auto.sh` + `lib/session_coord_auto.py`（挂 SessionStart + UserPromptSubmit）：开窗自动注册 / 每次发话刷心跳 + 把 itsuki 那句话存成「当前任务」。
- 改 register.sh（认环境变量 + 幂等）/ scan.sh（死窗口瘦身 + 自动清理超 1 小时旧记录）。

**取舍三角（模式 6）**：实时性 vs token 成本 vs 可靠性。
- 旧方案靠 CC 自觉 = 可靠性差（CC 记不住）→ 实时性=0。
- 「每回合都跑脚本」= 实时但费对话 token + 仍靠自觉。
- 选定方案：实时性归 hook（后台写文件、零对话 token、不靠自觉），读取归按需（只启动 + itsuki 主动问时才读）→ 三个目标同时满足。

**itsuki 学到的新概念（模式 5 — unknown unknowns）**：
1. hook 不只是「会话开始弹个提醒」，它能在后台拿到用户输入原文、会话编号、当前目录，自动做事。
2. hook 输出到屏幕才占 token，只写文件不打字 = 零对话 token。这是「实时更新会不会费 token」这个顾虑的答案。
3. 环境变量是程序之间传值的一种方式（CLAUDE_CODE_SESSION_ID）。

### itsuki 原话 ⭐

> "我觉得这个 session coord 不是很有作用，帮我优化一些。"
> "后续我需要它做别的事，它就不会更新它继续做什么了。"
> "也不知道实时更新会不会太消耗 token 了，我也不太知道。所以我现在不太了解我这个，所以我需要你来帮助我了解，然后帮助我优化。"

### AC 价值 ⭐

- 对应核心问题：#1 問題発見（自己用了之后发现机制缺陷）/ #2 技術判断（取舍三角）/ #3 問題解決 / #5 自己認識（通过 AI 理解 hook / token / 环境变量）
- 展示能力：① itsuki 主动发现工具缺陷（不是被动接受现成方案）② 对 AI 给的方案先要求「帮我了解再优化」= 不盲目让 AI 改 ③ 提出「会不会费 token」= 成本意识。
- 模式：2（itsuki 直觉「没用」→ CC 验证确实没用、找出真因）+ 5（hook / token / 环境变量认知）+ 6（取舍三角）。
- 可能用在自我推荐书：「我如何用 AI 协作改进自己搭的工具」主线。

### 后续 / 未解决

- hook 真实触发（开窗 / 发话自动跑）还没在真流程验证过，只用假数据模拟测通。需要 itsuki 重开新窗口确认。
- 全局 `~/.claude/` 的 9 个改动文件不在 git 仓库（无法 commit），只有 DMSD 内 dmsd-startup/SKILL.md 能提交。

#AC候选 #认知改变 #问题解决 #技术判断 #DMSD
