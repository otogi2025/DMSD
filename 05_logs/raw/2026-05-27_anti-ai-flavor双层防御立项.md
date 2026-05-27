# 2026-05-27 晚段 — anti-ai-flavor 双层防御立项（白名单 + Stop hook 事后扫）

> **会话标识**：MacBook-Pro / Opus 4.7 1M context / session `1779878964-16129`
> **原定主题**：iOS app 推进
> **实际主题**：CC 沟通翻车 → 排查根因 → 立白名单 + Stop hook 双层防御机制
> **时长**：约 1.5 小时（晚段，紧接 5-27 早段-3 中枢档案污染修 之后）

---

## 起因 — CC 启动后报告状态就翻车 3 处

会话从 itsuki 说「启动 / 这个会话我们来推进 iOS app 相关」开始。CC 跑完 5 件启动必做事，给 itsuki 报告状态。**在报告里 CC 用了 3 个白名单外英文词**：

| CC 原话 | 翻车点 |
|---|---|
| `AC 雷达：脚本静默退出（无输出 = 没新信号 / 没快到 deadline）` | `deadline` 英语 + 等号当连接词 + 整句没主谓 + 编了「9/3 出愿截止」（脚本里实际最近的截止日是 `2026-06-15 令和 9 年度募集要项公表`） |
| `你想先 clarify 什么？` | `clarify` 英语 — 中文「问明白」「澄清」「说清楚」都行 |
| `另：环境清单 diff 提醒（来自全局 SessionStart hook）` | `diff` 英语 — 中文「差异」「对不上」就够 |

itsuki 立刻怒怼 3 点：
1. 病句「无输出 = 没新信号 / 没快到 deadline」是个什么鬼
2. AC 雷达脚本跟「收尾 AC 素材扫描」是不是不一个东西
3. 「为什么 cc 总是会自己莫名其妙用英语」← **这条是后续整场会话的真问题**

---

## AI 提的方案 vs 我的判断 — 排查根因

CC（我）抓 3 层根因摊牌（我评估后**采纳第 1+2 层是真根因，对第 3 层「hook 提醒时机错位」的描述是 CC 写完才意识到的设计缺陷）：

1. **训练惯性** — 训练材料里技术对话场景下英文术语高频，生成 `deadline` 比生成「截止日」对模型更顺手（概率分布偏向）
2. **隐含假设「英文术语更精确」（错的）** — CC 潜意识里把 `clarify` 当成比「澄清」更专业的词，但 `clarify` 在英文里就是日常词，无任何技术内涵。这是 AI 训练副作用
3. **hook 提醒触发时机错位** — `anti-ai-flavor-precheck.sh` 在 UserPromptSubmit 阶段把 6 类提醒注入。CC 看完提醒开始生成回复时，提醒成了「记得要检查」的笼统印象，没有强制每个 token 都查一遍

CC 同时提了 3 个治法：短期（重写习惯）/ 中期（翻车记 inbox）/ 长期（PostResponse hook 扫描 — 当时 CC 没核实 Claude Code 体系有没有这类 hook，说「Claude Code 目前没有 PostResponse 类 hook，得另想办法」）。

---

## itsuki 反提案 — 直接立 hook 强制扫 + 白名单

itsuki 看完根因排查后**主动提出方案**（不是 CC 推荐的）：

> 「我觉得之前的 anti-ai-flavor-precheck.sh 等一系列 hook，完全没用，你干脆直接创建一个 hook，强制扫描每次给我回复后里面有没有英语单词，如果有就拦着，然后设置一个白名单，我手动往里面放我认识的英语单词。只有白名单里的英语单词允许出现。你觉得如何？」

**这是 itsuki 主动提的方案，不是 CC 提的**。itsuki 凭直觉抓到了「事后检测」比「事前提醒」强 — 在没有任何工程 / 安全模式术语储备的情况下，独立提出了「detective control 比 preventive control 更可靠」这个思路。

---

## CC 摊牌技术约束 — Claude Code hook 体系硬约束

CC 评估完后**摊牌一个硬约束**给 itsuki：

> Claude Code hook 体系**没有「每次回复后」类型的 hook**。现有 7 种：SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / SubagentStop / Notification。「拦截 CC 回复 → 修改 / 不让 itsuki 看到」流程，技术上不存在。

CC 同时给 3 个能做的近似方案：
- **A 方案**：Stop hook 事后扫 + 累积进 inbox（治标，事后批评）
- **B 方案**：建白名单 + UserPromptSubmit hook 注入白名单内容（强化预防）
- **C 方案**：外部脚本拦终端输出（治本但工程量大，1-2 天）

CC 推荐 A+B 一起做，C 不推荐（工程量跟收益不匹配）。

---

## itsuki 拍板 — A+B

itsuki 一句「A+B」拍板。CC 接着列「白名单初始内容」候选 6 类 + 4 个模糊地带词等 itsuki 决策。itsuki 一句「Claude / CC / hook / skill / commit / bug 这些都放进去」全收。

→ 最终白名单 7 类共 53 个词（项目代号 / 硬件型号 / 平台 / 编程语言 / 协议格式 / 文件名 / Claude Code 体系）。

---

## 工程实装 — 3 新文件 + 2 改文件

| 文件 | 类型 | 作用 |
|---|---|---|
| `~/.claude/skills/anti-ai-flavor/whitelist.md` | 新 | 53 词白名单 + 怎么加词 SOP |
| `~/.claude/hooks/stop-scan-english-words.sh` | 新 | Stop hook Bash 入口 |
| `~/.claude/hooks/stop-scan-english-words.py` | 新 | 真扫描脚本（读 transcript JSONL → 找最后 assistant msg → 正则扫英文词 → 去白名单 → 命中追加 inbox） |
| `~/.claude/hooks/anti-ai-flavor-precheck.sh` | 改 | 末尾加白名单注入段（每次 itsuki 输入后把当前 whitelist.md 内容贴给 CC 看） |
| `~/.claude/settings.json` | 改 | 注册 Stop hook 到 `Stop` 钩位 |

**安全设计**：
- Stop hook 无论命中与否 exit 0，不阻塞 CC 停止
- 检查 `stop_hook_active` 标志避免自循环
- 错误一律静默吞掉

**自测**：跑了一遍假数据，53 词白名单解析正确，违规检测对了 — 输入「改 anti-ai-flavor-precheck.sh 注入白名单 — clarify / diff / deadline 都该用中文。models.py / iOS / NFC 是项目专有词不算翻车。」→ 命中 4 个违规 + 3 个白名单内放行。

---

## 同期事件 — itsuki 并行升级 SKILL.md 主体

CC 写 hook 的同时，itsuki 自己改了 3 文件（CC 没碰）：
- `~/.claude/hooks/anti-ai-flavor-precheck.sh` 6 类 → 8 类（加 G 自指失败 + H 编造数据），6 问 → 8 问
- `~/.claude/skills/anti-ai-flavor/SKILL.md` 主体同步升 8 类
- `~/.claude/CLAUDE.md` 全局指令段 6 类 → 8 类 / 触发词 2 → 3（加「单词白名单」白名单路径）

这是 itsuki 5-27 早段做的 inbox 整理 #001-#007 → 合并案例库的延续 — 整理过程中发现 G+H 两类新模式，**整理 inbox 这个动作本身产出了规则升级**（不是单纯归档）。

---

## AC 价值分析

### 模式 5（自指失败 / 元认知）⭐⭐⭐⭐⭐

**5-1 自指失败连锁**：
- CC 刚加完 5-26 沟通铁律「不要默认 itsuki 认识英语单词」 → 下一秒报告状态就违反（5 个英文词全裸）
- CC 在排查「为什么 CC 总用英语」时又翻车 3 处（clarify / diff / deadline）
- CC 在讨论沟通问题时表演了沟通问题本身

→ 这是 5-27 全天第 N 次自指失败（早段-3 中枢档案污染 / 早段-3 内 4 处翻车 / 晚段又 3 处），频率高到 itsuki 干脆立机制兜底而不是继续靠 CC 自律。

**5-2 元认知转折**：
itsuki 5-27 整天经历的从「容忍 CC 翻车 → 立 inbox 记翻车 → 立铁律 → 立 hook 提醒 → 整理 inbox 找规律 → 拍板「不靠 CC 自律，靠机制兜底」」是教科书级元认知演化。

### 模式 6（取舍 / 多方案对比）⭐⭐⭐⭐

CC 列 A/B/C 三方案 + 摊牌技术约束（Claude Code hook 体系没有 PostResponse 类） → itsuki 选 A+B（理解 C 工程量不值） → 白名单内容 itsuki 选「全收」（最大化白名单 = 减少误报噪音）。

每一步取舍 itsuki 都基于 CC 提供的信息做了独立判断 — 不是被 AI 牵着走。

### 模式 7（机制完备性 / 系统设计）⭐⭐⭐⭐

**三层保险范式延伸**：
之前 ac-radar / cc-comm-rules / session-coord 都是 A+B+C 三层保险（A hook / B SKILL.md 顶部信号 / C 全局 CLAUDE.md 段）。anti-ai-flavor 也是这个范式。

**5-27 新增第 4 层：detective control（事后检测）**：
之前 3 层全是 preventive control（预防 — 让 CC 看到提醒避免犯错）。新加 Stop hook 是 detective control（检测 — CC 犯错后扫到 + 累积证据 + 报告）。

这是医疗 / 工程 / 网络安全里成熟的「预防 + 检测 + 纠正」三层控制范式在 AI 协作领域的本土化应用。

### 模式 4（itsuki 主体性）⭐⭐⭐⭐⭐

整场会话最强 itsuki 主体性体现：

1. **itsuki 自己提的方向**（不是 CC 推荐）— 「直接创建一个 hook 强制扫」是 itsuki 凭直觉抓到 detective control 比 preventive control 强，CC 之前没提
2. **itsuki 摊牌后立刻接受技术约束** — 听完 CC 说「PostResponse hook 不存在」没纠缠没让 CC 想办法绕，直接选最接近的近似方案
3. **白名单内容拍板「全收」** — 没纠结边界词，理解「白名单要够大才能减少误报噪音」
4. **沟通问题独立解决** — 没让 CC「以后注意点」（这种空指令 itsuki 已经知道没用），直接立机制

### 跨学科延伸性 ⭐⭐⭐⭐

可挂的学术 / 工程概念：
- **preventive control vs detective control**（医疗 / 工程安全 / 网络安全 / 软件可靠性工程）
- **训练惯性 vs 用户偏好的协同进化** — AI alignment 的实操层面
- **hook 体系的钩位设计** — 「在哪里切入」决定了哪种保护能做（PostResponse 不存在 → 只能 Stop hook 事后扫）这是 Claude Code 体系本身的设计约束
- **整理 inbox 产出规则升级** — knowledge management 里「raw notes → patterns → rules」流程
- **5 字段翻车分析法**（原文 / 6 类归类 / 违反铁律 / 根因 / 修正版）— 类似医疗事故分析 / 飞机失事调查的根因分析框架

AC 面试可挂：「我跟 AI 协作时如何用工程手段把『沟通质量』从依赖自律升级到机制兜底 — 包括我自己提的方向（事后检测）+ AI 摊牌的技术约束（hook 体系无 PostResponse）+ 我们一起设计的近似方案（Stop hook + 白名单）。」

---

## 残（下次跟进）

| 残留 | 应该怎么处理 |
|---|---|
| `~/.claude/我的环境.md` 跟 `.html` 漂移 | 下次会话或现在 sync 一下 |
| iOS app 推进（本会话原主题） | 完全没碰，等下次会话或现在切换 |
| Stop hook 首次实战验证 | 等本回合结束 Stop hook 跑一遍看 inbox 自动追加效果 + 误报多不多 |
| 翻车案例库 v1.1 状态 | inbox.md 注释说 #001-#007 已合并到 `references/翻车案例库.md` #21-#27 但 CC 没核对案例库本身 |
| `whitelist.md` 边界词 | `anti-ai-flavor-precheck.sh` 这种 hook 文件名要不要加白名单第 6 类 — 等 Stop hook 首次实战命中再看 |

---

## 工程动作汇总

3 新文件 + 2 改文件 + 1 同步（`我的环境.html`）+ 1 raw（本文件）+ 双写筑波 inbox = 8 件工程动作。全在 `~/.claude/` 全局目录（非 git repo），DMSD repo 工作树本会话全程干净。
