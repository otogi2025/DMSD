---
name: dmsd-startup
description: DMSD 会话启动 SOP — CC 每次开新会话必读必做的 4 件事（读中枢信箱 / ac-radar 启动检查 / 读 心智模型+WIP / 打勾报告）。集中管理启动逻辑 — 启动该做什么以本文件 §2 为唯一真值，CLAUDE.md / WIP 只写指针不写内容（防两边漂移）。**always-on — 不依赖关键词，每次会话启动 CC 必须主动 Read 本 skill 并按 §2 顺序执行**。
---

# dmsd-startup

> 🔴🔴🔴 **CC 每次开新会话必做 — 加载本 skill 后按 §2 顺序跑 4 件事，跑完逐项打勾报告 itsuki**
>
> **本文件 §2 是启动流程唯一真值** — CLAUDE.md「会话开始」段 / WIP 顶部只允许写「走 dmsd-startup skill」一句指针，不允许复述步骤内容（历史教训：复述过的两处都漂移了，「漂移检测移走」9 天没人同步）。改本文件 → 联动规则 Rule 27 会提醒核对指针处。

## 1. 为什么写这个 skill

启动逻辑散在多处 = 容易漏 + 互相打架。itsuki 2026-05-26 拍板集中到一个 skill。2026-06-11 启动流程大改版：

- **session-coord（多会话协作板）整体停用** — 没用上（信箱零留言 / 占用登记防不住真冲突），防多会话冲突的实际机制是「做完一件事立刻 commit」铁律。原 Step 1 删除
- **中枢信箱并入启动**（原来散在 CLAUDE.md 另一段，违反「集中」初衷）
- **全局说明书（ac-radar / cc-comm-rules）不再每会话读原文** — 省 550+ 行/会话，精华已在全局 CLAUDE.md
- 更早：2026-05-28 拍板 project-overview 漂移检测从启动移除，唯一检测点在收尾（[[session-wrap]] §7.5.1 项 7）

## 2. 启动必做 4 件事（按顺序）

### Step 1 — 读全项目中枢信箱

读 iCloud 中枢的 DMSD 信箱（别项目 CC 给 DMSD 的留言）：

```
~/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/大学入試/全项目中枢/信箱/DMSD_inbox.md
```

- 有新留言（`## 状态: 未读`）→ 报告 itsuki，处理完改状态行「已处理 yyyy-mm-dd」
- 没留言 → 报一句「信箱无新留言」即可

### Step 2 — ac-radar 启动检查

跑：
```bash
python3 ~/.claude/skills/ac-radar/scripts/startup_check.py
```

干嘛：三项检查 — ① AC 关键日程 ≤30 天提醒 ② 状态快照超 7 天没更新提醒 ③ 素材池当月堆超 50 条提醒。每条提醒每天本机只发一次。**脚本永远输出一行状态** — 真空输出 = 脚本坏了，要报告。

向 itsuki 报告：原样转告，不美化不解释。

### Step 3 — 读 项目心智模型.md + WIP.md

读两份（都全文，都短）：

1. **`~/dev/DMSD/00_admin/项目心智模型.md`** —— 系统怎么跑通 + 5 端各自现状 + 绑住 5 端的契约 + 核心不变量 + 当前未决问题。**这是让 AI 开局脑子里就有项目全貌的骨架，每次必读**（专治「开新会话改前端却不知道后端写到哪」）。
2. **`~/dev/DMSD/00_admin/WIP.md`**（全文）

从 WIP 拿到信息：当下焦点 / 最近 5 次会话 / 阻塞项。

TODO 不主动读（itsuki 主动问才读），git status 留到收尾。

### Step 4 — 逐项打勾报告 + 等指令

```
启动完成核对：
✅ Step 1 中枢信箱 —— 无新留言（或：N 条新留言，内容…）
✅ Step 2 AC 雷达 —— [脚本原样输出]
✅ Step 3 心智模型 + WIP —— 系统骨架已读 / 焦点：[一句话]
✅ Step 4 报告完毕，等你指令
```

铁律：
- 每步必须标 ✅（做了）或 ❌（出错 + 错信息），不允许默默跳过
- 报完等 itsuki 说做什么 — 不主动催进度，不主动列 TODO

## 3. 不做的事（明确边界）

| 不做的 | 理由 | 什么时候做 |
|---|---|---|
| 读 `00_admin/TODO.md` | itsuki 不想被 CC 催进度 | 只在 itsuki 主动问「下一步做什么」/「还有什么没做」才读 |
| 跑 `git status` | 启动时跑会噪音 + 容易引导 CC 想 commit | 会话结束走 [[session-wrap]] §5.5.9 |
| 读 `CHANGELOG.md` | 它是给全部读者看的版本编年史，CC 启动不需要 | 版本 bump 时由 [[version-bump]] skill 处理 |
| 读 ac-radar / cc-comm-rules 完整 SKILL.md | 精华已在全局 CLAUDE.md，每会话重读 550+ 行纯烧上下文 | 信号命中要写素材 / itsuki 怒怼沟通问题时按需读 |
| 扫 `00_admin/handoff/` 交接件 | 交接件 itsuki 都当场用；归档责任在被交接的 AI（干完活自己移 99_archive，规则在 handoff/README.md + 交接词模板末尾）| 不扫 |
| 检测装的工具 vs 环境清单 | 全局挂钩 `~/.claude/hooks/session-start-env-diff.sh` 在管 | 挂钩自动跑，CC 看到输出再反应 |
| session-coord 协作板注册 / 扫描 | 2026-06-11 itsuki 拍板整体停用 | 不做（想恢复见 `~/.claude/skills/session-coord/SKILL.md` 顶部停用说明）|

## 4. 按需触发的事（itsuki 输入命中哪些场景 → CC 做什么）

启动后不主动做，但 itsuki 输入命中这些场景时 CC 必须立刻反应：

### 4.1 找文件 / 问文件 → 必须查 `.claude/skills/project-overview/SKILL.md`

不用 grep / find / 命令行。总览里写好了所有文件干嘛用 + 状态，直接翻总览拿答案。

itsuki 任一种输入触发：

- 「某文件在哪？」
- 「某文件干嘛用的？」
- 「项目里有没有 XX 文件？」
- 「XX 类的文件都在哪个目录？」
- 「这个目录下有什么？」
- 「找文件」/「列文件」/「整理某类文件」

### 4.2 TODO 待办 → 必须 itsuki 主动问才读 `00_admin/TODO.md`

只在 itsuki 主动问下面这类问题时才读：

- 「还有什么没做？」
- 「下一步该做什么？」
- 「TODO 还剩什么？」

**不主动催进度，不主动列待办给 itsuki 看**。

### 4.3 WIP vs TODO 铁律

- **WIP** = 当下书签，最近 5 次会话上限
- **TODO** = 完整未完成 backlog，真值
- **WIP 绝不复述 TODO 内容**

### 4.4 文件联动 → 走 `.claude/skills/file-linkage/SKILL.md`

CC 改完高联动文件（backend models.py / spec 主体 / system_features.md / Route.swift 等）后自动加载 file-linkage skill 查反向索引，确认下游文件都同步了。

联动规则 + 反向索引 + 检查命令 → `.claude/skills/file-linkage/SKILL.md`（条数以 `sync-rules.sh` 为真值）。

---

## 5. 跟其他 skill / 挂钩边界

| 谁 | 干嘛 | 跟本 skill 的关系 |
|---|---|---|
| 全局挂钩 `session-start-env-diff.sh` | 对账实际装的工具 vs 环境清单 | **互补** — 挂钩自动跑，本 skill 不重复，CC 看到挂钩输出再反应 |
| DMSD 项目挂钩 `bin/check_overview_drift.sh` | project-overview 漂移检测 | **不在启动跑** — 唯一检测点在收尾（[[session-wrap]] §7.5.1 项 7）。脚本保留可单独用 |
| `~/.claude/skills/ac-radar/SKILL.md` | AC 入试素材实时捕获 | **本 skill Step 2 只跑它的 startup_check.py** — SKILL 原文按需读；ac-radar 自己的运行时（信号命中 / 收尾 flush）不受本 skill 影响 |
| ~~`~/.claude/skills/session-coord/SKILL.md`~~ | 多会话协作板 | **2026-06-11 整体停用** — 挂钩摘除 + 启动步骤删除，脚本保留可恢复（见其顶部停用说明）|
| `.claude/skills/session-wrap/SKILL.md` | 会话收尾 SOP | **互补** — 启动用本 skill，收尾用 session-wrap |

## 6. CC 行为约定（always-on）

加载本 skill 后：

1. **每次新会话第一个回合** — 按 §2 顺序跑 4 件事
2. **不依赖关键词触发** — 不等 itsuki 说「启动」才做
3. **跑出错** — 报告 itsuki 哪步出错 + 错信息，不擅自跳过
4. **不主动声明自己在用本 skill** — itsuki 看汇报内容就行，不用「我现在在跑 dmsd-startup skill」这种客套

## 版本

- v0.4.0 / 2026-06-11 / 启动流程大改版 — ① session-coord 停用、原 Step 1 删除 ② 中枢信箱并入为新 Step 1（原散在 CLAUDE.md）③ ac-radar / cc-comm-rules 不再每会话读原文 ④ 立「本文件 §2 = 唯一真值，别处只写指针」+ 联动 Rule 27 兜底 ⑤ startup_check.py 加永远在的状态行
- v0.3.0 / 2026-05-29 / Step 3 从「读 WIP」扩成「读 项目心智模型.md + WIP」
- v0.2.0 / 2026-05-28 / 漂移检测移到收尾；5 件事砍到 4 件；报告改逐项打勾
- v0.1.0 / 2026-05-26 / 初版 — itsuki 拍板集中启动逻辑
