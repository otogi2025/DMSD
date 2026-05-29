---
name: dmsd-startup
description: DMSD 会话启动 SOP — CC 每次开新会话必读必做的 4 件事（多会话协同注册 / ac-radar 启动检查 / 读 WIP / 不主动读 TODO / 报告状态等指令）。集中管理启动逻辑，替代原来散落在 CLAUDE.md「会话开始」段 + 全局 session-start-coord-check 挂钩里的指令。**always-on — 不依赖关键词，每次会话启动 CC 必须主动 Read 本 skill 并按 §2 顺序执行**。
---

# dmsd-startup

> 🔴🔴🔴 **CC 每次开新会话必做 — 加载本 skill 后按 §2 顺序跑 4 件事，跑完逐项打勾报告 itsuki**

## 1. 为什么写这个 skill

之前 DMSD 启动逻辑散在 3 处：
- 全局挂钩 `~/.claude/hooks/session-start-coord-check.sh`（多会话协同检测）
- ac-radar 启动检查
- DMSD `CLAUDE.md` 第 106 行「会话开始: 读 WIP.md」段

散 = 容易漏。itsuki 2026-05-26 拍板集中到一个 skill，挂钩里跟项目相关的部分搬过来，全局挂钩里只跟 DMSD 重复的部分在 DMSD 项目下静默退出。

> **2026-05-28 itsuki 拍板**：project-overview 漂移检测从启动移除 —— 启动不再检测，唯一检测 / 修复点放到收尾（[[session-wrap]] §7.5.1 项 8）。配套停掉 `settings.json` 里的 `check_overview_drift.sh` 启动挂钩。

## 2. 启动必做 4 件事（按顺序）

### Step 1 — 多会话协同（读 + 报告）

注册 / 刷心跳 / 记当前任务 由 `session-coord-auto.sh` hook 自动维护（开窗时 + itsuki 每次发话时后台做，零对话 token）。**CC 不用再手动注册**，只跑一次 scan 读取 + 报告：

```bash
bash ~/.claude/skills/session-coord/scripts/scan.sh "$CLAUDE_CODE_SESSION_ID"
```

干嘛：
- `$CLAUDE_CODE_SESSION_ID` — Claude 给本窗口发的会话编号（环境变量），跟 hook 建的状态目录同名，对得上号
- `scan.sh` — 扫别的窗口在干嘛 + 自己 inbox（信箱）有没有新留言 + 顺手清理超 1 小时的死窗口目录

期待输出：活跃窗口清单 + 自己 inbox（如果有内容）

向 itsuki 报告：活跃会话清单 + 自己 inbox 新消息（没消息说一句没消息）

> 万一 hook 没生效（比如刚改完配置还没重开窗口），scan 照常工作，只是少标「👈 我」那行，不影响报告别的窗口。

完整说明 → `~/.claude/skills/session-coord/SKILL.md` §三（hook 自动 vs CC 手动分工）

### Step 2 — ac-radar 启动检查

跑：
```bash
python3 ~/.claude/skills/ac-radar/scripts/startup_check.py
```

干嘛：检查 AC 入试素材收集状态（距离截止日 / inbox 新条目 / 今天有没有 AC 信号）

期待输出：脚本自己印 AC 雷达状态

向 itsuki 报告：原样转告，不美化不解释

### Step 3 — 读 项目心智模型.md + WIP.md

读两份（都全文，都短）：

1. **`~/dev/DMSD/00_admin/项目心智模型.md`** —— 系统怎么跑通 + 5 端各自现状 + 绑住 5 端的契约 + 核心不变量 + 当前未决问题。**这是让 AI 开局脑子里就有项目全貌的骨架，每次必读**（专治「开新会话改前端却不知道后端写到哪」）。
2. **`~/dev/DMSD/00_admin/WIP.md`**（全文）

从 WIP 拿到信息：
- 当前版本号（顶部「**当前版本**: vX.Y.Z」）
- 当下焦点（§ 🎯 当前焦点）
- 最近 5 次会话（§ 最近会话）
- 多会话占用（§ 多会话占用，避免跟别的会话撞文件）
- 阻塞项（§ 阻塞项）

注意：WIP 顶部「会话开始: CC 读 ... + TODO.md 顶部 200 行 + git status」是旧版指令（跟 CLAUDE.md 新指令冲突）。按本 skill 做 — TODO 不主动读，git status 留到收尾。

### Step 4 — 逐项打勾报告 + 等指令

跑完 Step 1-3 后，**逐项打勾**汇报（itsuki 一眼看到每件事都做了）：

```
启动完成核对：
✅ Step 1 多会话协同 —— 活跃会话 N 个 / inbox 新消息 X 条
✅ Step 2 AC 雷达 —— [脚本原样输出]
✅ Step 3 心智模型 + WIP —— 系统骨架已读 / 当前 vX.Y.Z / 焦点：[一句话]
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
| DMSD 项目挂钩 `bin/check_overview_drift.sh` | project-overview 漂移检测 | **2026-05-28 起不在启动跑** — 移到收尾（[[session-wrap]] §7.5.1 项 8）。启动挂钩已从 `settings.json` 停掉，脚本本身保留可单独用 / 收尾调用 |
| `~/.claude/skills/ac-radar/SKILL.md` | AC 入试素材实时捕获 | **本 skill Step 3 跑它的 startup_check.py** — ac-radar 自己的运行时（信号命中 / 收尾 flush）不受本 skill 影响 |
| `~/.claude/skills/session-coord/SKILL.md` | 多会话协同板的完整 SOP | **本 skill Step 1 调用它的 register/scan 脚本** — session-coord 自己的其他 SOP（写 inbox / 释放占用 / handoff）按它自己的触发走 |
| `.claude/skills/session-wrap/SKILL.md` | 会话收尾 SOP | **互补** — 启动用本 skill，收尾用 session-wrap |

## 6. CC 行为约定（always-on）

加载本 skill 后：

1. **每次新会话第一个回合** — 按 §2 顺序跑 4 件事
2. **不依赖关键词触发** — 不等 itsuki 说「启动」才做
3. **跑出错** — 报告 itsuki 哪步出错 + 错信息，不擅自跳过
4. **不主动声明自己在用本 skill** — itsuki 看汇报内容就行，不用「我现在在跑 dmsd-startup skill」这种客套

## 版本

- v0.3.0 / 2026-05-29 / Step 3 从「读 WIP」扩成「读 项目心智模型.md + WIP」—— 配合新建 `00_admin/项目心智模型.md`（AI 开局必读骨架：系统怎么跑 + 5 端现状 + 契约 + 不变量 + 未决问题），解决「开新会话 AI 不知道别的端写到哪」。收尾侧更新由 [[session-wrap]] §7.5.1 项 12 负责。
- v0.2.0 / 2026-05-28 / itsuki 拍板 3 改：① project-overview 漂移检测从启动移除（移到收尾 [[session-wrap]] §7.5.1 项 8）+ 停 `settings.json` 启动挂钩；② 启动从 5 件事砍到 4 件事；③ Step 4 报告改逐项打勾格式（每步标 ✅ / ❌）
- v0.1.0 / 2026-05-26 / 初版 — itsuki 拍板集中启动逻辑，从 CLAUDE.md 第 106-111 行 +  全局 `session-start-coord-check.sh` 挂钩 + DMSD `bin/check_overview_drift.sh` 调用 抽出来。配套：全局 coord-check 挂钩改成 DMSD 下静默，DMSD CLAUDE.md 会话开始段简化成「启动走 dmsd-startup skill」
