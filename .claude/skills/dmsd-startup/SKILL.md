---
name: dmsd-startup
description: DMSD 会话启动 SOP — CC 每次开新会话必读必做的 5 件事（多会话协同注册 / project-overview 漂移检测 / 读 WIP / 不主动读 TODO / 报告状态等指令）。集中管理启动逻辑，替代原来散落在 CLAUDE.md「会话开始」段 + 全局 session-start-coord-check 挂钩里的指令。**always-on — 不依赖关键词，每次会话启动 CC 必须主动 Read 本 skill 并按 §2 顺序执行**。
---

# dmsd-startup

> 🔴🔴🔴 **CC 每次开新会话必做 — 加载本 skill 后按 §2 顺序跑 5 件事，跑完报告 itsuki**

## 1. 为什么写这个 skill

之前 DMSD 启动逻辑散在 3 处：
- 全局挂钩 `~/.claude/hooks/session-start-coord-check.sh`（多会话协同检测）
- DMSD 项目挂钩 `bin/check_overview_drift.sh`（project-overview 漂移检测）
- DMSD `CLAUDE.md` 第 106 行「会话开始: 读 WIP.md」段

散 = 容易漏。itsuki 2026-05-26 拍板集中到一个 skill，挂钩里跟项目相关的部分搬过来，全局挂钩里只跟 DMSD 重复的部分在 DMSD 项目下静默退出。

## 2. 启动必做 5 件事（按顺序）

### Step 1 — 多会话协同注册

跑：
```bash
bash ~/.claude/skills/session-coord/scripts/register.sh $(hostname -s) "<本会话主题，CC 自己拟一句>"
bash ~/.claude/skills/session-coord/scripts/scan.sh
```

干嘛：
- `register.sh` — 把本会话登记到 `~/dev/DMSD/.claude/sessions/_board.md` 协作板，让别的同时开的 CC 会话知道你存在
- `scan.sh` — 扫别的会话在干嘛 + 自己 inbox 有没有新留言

期待输出：协作板内容 + 自己 inbox（如果有内容）

向 itsuki 报告：活跃会话清单 + 自己 inbox 新消息（没消息说一句没消息）

完整说明 → `~/.claude/skills/session-coord/SKILL.md`

### Step 2 — project-overview 漂移检测

跑：
```bash
bash ~/dev/DMSD/bin/check_overview_drift.sh
```

干嘛：跑 `git ls-files` 数实际文件数，跟 `.claude/skills/project-overview/SKILL.md` §0.1 体量表对比，文件数对不上 = 漂移

期待输出：
- 没漂 — 脚本静默 / 输出「无漂移」
- 漂了 — 列出哪些目录写了 N 实际 M

向 itsuki 报告：原样转告脚本输出，不美化不解释。提一句「→ 漂了 = Edit `.claude/skills/project-overview/SKILL.md` §0.1 体量表 + 对应章节」让 itsuki 决定要不要现在修

### Step 3 — ac-radar 启动检查

跑：
```bash
python3 ~/.claude/skills/ac-radar/scripts/startup_check.py
```

干嘛：检查 AC 入试素材收集状态（距离截止日 / inbox 新条目 / 今天有没有 AC 信号）

期待输出：脚本自己印 AC 雷达状态

向 itsuki 报告：原样转告，不美化不解释

### Step 4 — 读 WIP.md

读：`~/dev/DMSD/00_admin/WIP.md`（全文）

拿到信息：
- 当前版本号（顶部「**当前版本**: vX.Y.Z」）
- 当下焦点（§ 🎯 当前焦点）
- 最近 5 次会话（§ 最近会话）
- 多会话占用（§ 多会话占用，避免跟别的会话撞文件）
- 阻塞项（§ 阻塞项）

注意：WIP 顶部「会话开始: CC 读 ... + TODO.md 顶部 200 行 + git status」是旧版指令（跟 CLAUDE.md 新指令冲突）。按本 skill 做 — TODO 不主动读，git status 留到收尾。

### Step 5 — 报告状态等指令

汇报格式（写给 itsuki 看）：

```
1. 多会话协同：[活跃会话 N 个 / inbox 新消息 X 条]
2. project-overview 漂移：[无漂 / 漂了：A 目录 写 X / 实际 Y]
3. AC 雷达：[原样转告脚本输出]
4. WIP 当前焦点：[一句话总结]
5. 等你指令 — 不主动催进度，不主动列 TODO
```

报完等 itsuki 说做什么。

## 3. 不做的事（明确边界）

| 不做的 | 理由 | 什么时候做 |
|---|---|---|
| 读 `00_admin/TODO.md` | itsuki 不想被 CC 催进度 | 只在 itsuki 主动问「下一步做什么」/「还有什么没做」才读 |
| 跑 `git status` | 启动时跑会噪音 + 容易引导 CC 想 commit | 会话结束走 [[session-wrap]] §5.5.9 |
| 读 `progress_overview.md` / `CHANGELOG.md` | 它们是给教授 / 全部读者看的，CC 启动不需要 | 版本 bump 时由 [[version-bump]] skill 处理 |
| 检测装的工具 vs 环境清单 | 全局挂钩 `~/.claude/hooks/session-start-env-diff.sh` 在管 | 挂钩自动跑，CC 看到输出再反应 |

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

完整 17 条联动规则 + 反向索引 + 检查命令 → `.claude/skills/file-linkage/SKILL.md`。

---

## 5. 跟其他 skill / 挂钩边界

| 谁 | 干嘛 | 跟本 skill 的关系 |
|---|---|---|
| 全局挂钩 `session-start-env-diff.sh` | 对账实际装的工具 vs 环境清单 HTML | **互补** — 挂钩自动跑，本 skill 不重复，CC 看到挂钩输出再反应 |
| 全局挂钩 `session-start-coord-check.sh` | 多会话协同检测 | **替代** — 挂钩在 DMSD 项目下静默退出（避免重复），本 skill Step 1 接管 |
| DMSD 项目挂钩 `bin/check_overview_drift.sh` | project-overview 漂移检测 | **本 skill Step 2 主动调用脚本** — 脚本本身保留可单独用 |
| `~/.claude/skills/ac-radar/SKILL.md` | AC 入试素材实时捕获 | **本 skill Step 3 跑它的 startup_check.py** — ac-radar 自己的运行时（信号命中 / 收尾 flush）不受本 skill 影响 |
| `~/.claude/skills/session-coord/SKILL.md` | 多会话协同板的完整 SOP | **本 skill Step 1 调用它的 register/scan 脚本** — session-coord 自己的其他 SOP（写 inbox / 释放占用 / handoff）按它自己的触发走 |
| `.claude/skills/session-wrap/SKILL.md` | 会话收尾 SOP | **互补** — 启动用本 skill，收尾用 session-wrap |

## 6. CC 行为约定（always-on）

加载本 skill 后：

1. **每次新会话第一个回合** — 按 §2 顺序跑 5 件事
2. **不依赖关键词触发** — 不等 itsuki 说「启动」才做
3. **跑出错** — 报告 itsuki 哪步出错 + 错信息，不擅自跳过
4. **不主动声明自己在用本 skill** — itsuki 看汇报内容就行，不用「我现在在跑 dmsd-startup skill」这种客套

## 版本

- v0.1.0 / 2026-05-26 / 初版 — itsuki 拍板集中启动逻辑，从 CLAUDE.md 第 106-111 行 +  全局 `session-start-coord-check.sh` 挂钩 + DMSD `bin/check_overview_drift.sh` 调用 抽出来。配套：全局 coord-check 挂钩改成 DMSD 下静默，DMSD CLAUDE.md 会话开始段简化成「启动走 dmsd-startup skill」
