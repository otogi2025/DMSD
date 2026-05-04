---
name: session-start
description: DMSD 会话启动 7 步检查 SOP — WIP / git 残留 / 未 push / stash / 多会话占用 / 当前版本 / 报告模板。⭐ 比 CLAUDE.md「读 WIP」一条规则深得多。touched 实战 CC 经常漏的 6 个失职点：多会话占用判断 / git 残留文件 / branch 没切回来 / 未 push commit / stash 挂的活 / 工作树污染。
when_to_use: ⭐ 触发 — itsuki 说「启动 / 开始 / 早上好 / 我回来了 / 继续 / 干活」/ 新会话第一条消息（即使 itsuki 没明示「启动」也跑）/ CC 注意到 git status 一堆 ?? 文件想确认状态时主动调。
allowed-tools: Read, Bash, Grep, Glob
---

# Session Start Skill — 会话启动 SOP

> **核心理念**：DMSD 是多设备多会话项目（Mac 主会话 / Mac 另开会话 / iPad SSH VPS 旧时代 / 不同 worktree）。**启动不只是读 WIP — 是要在 30 秒内确认当前 repo 是不是一个干净已知的状态**，不然 CC 接着干活会覆盖别会话的成果。
>
> **2026-05-04 itsuki 痛点**：CLAUDE.md 只写「读 WIP.md」太轻量，CC 启动经常漏多会话占用 / git 残留 / 未 push 等关键状态。

---

## §0 7 步主流程（必跑全跑，不能跳）

```
Step 1: 读 00_admin/WIP.md → 当前版本 / 当下焦点 / 最近 5 次会话 / 多会话占用 / 阻塞
Step 2: git status → 工作树污染 / 残留文件 / branch
Step 3: git log origin/main..HEAD → 未 push commit 数量
Step 4: git stash list → 是否有挂着的活
Step 5: 多会话占用诊断（§3 算法）
Step 6: 读 CHANGELOG.md 顶部 → 确认 WIP 版本号是否一致
Step 7: 用 §2 模板报告状态 + 等 itsuki 指令（不主动催进度 / 不主动列 TODO）
```

---

## §1 每步详细做法

### Step 1: 读 WIP

```bash
cat 00_admin/WIP.md
```

提取这 5 项：
- 当前版本（顶部 / "当前版本 see CHANGELOG.md 顶部"）
- 当下焦点（"## 当下焦点" 段）
- 最近 5 次会话条目
- 多会话占用声明（"## 多会话占用" 段，可能写"Mac 主会话"或"无"）
- 阻塞项（"## 阻塞" 段）

**铁律**：WIP = 当下书签（≤5 次会话），不复述 TODO 内容。如果 WIP 显得过长，警告 itsuki 该精简。

### Step 2: git status

```bash
git status
```

扫这 4 类污染：
- ` M` 已修改未 staged 的文件（多吗？是不是别会话改的？）
- `??` untracked 文件（是不是 .bak / .pbxproj.bak / .DS_Store 这种残留垃圾）
- `A ` staged 文件（itsuki 上次会话忘 commit？）
- 当前 branch（应该在 main，如果在 feature/* 要明确指出）

**典型残留垃圾清单**（看到必报告，等 itsuki 决定是否删）：
- `*.pbxproj.bak`、`*.pbxproj.bak2` — Xcode 自动生成
- `.DS_Store` — macOS 系统文件
- `*.psd`、`*.icon/icon.json` — 图标 / 设计源文件可能本来就该 untracked
- `Root/File.txt` 这种明显占位文件

### Step 3: 未 push commit

```bash
git log --oneline origin/main..HEAD
```

报告未 push commit 数量 + 列每条 hash + 一句话。**按 commit/push 协作分工**（memory `feedback_commit_push_tag_division.md`）：CC 不主动 push，等 itsuki 拍板。

### Step 4: git stash

```bash
git stash list
```

如果有 stash → 报告 stash 数量 + 内容简要（itsuki 可能忘了挂的活）。

### Step 5: 多会话占用诊断

走 §3 算法。

### Step 6: 当前版本一致性

```bash
head -5 CHANGELOG.md
```

对比 WIP.md 写的版本号 → 是否一致。如果 WIP 写了具体版本号（不是「见 CHANGELOG」指针）→ 警告 itsuki（违反 single source of truth）。

### Step 7: 用模板报告状态

走 §2 模板。

---

## §2 报告模板（标准格式）

```
🌅 启动状态报告

**当前版本**：v0.3.1（CHANGELOG 顶部）
**当下焦点**：[从 WIP §当下焦点 提取一句]
**最近会话**：[列最近 1-2 个会话简要，不全列 5 个]

**Git 状态**：
- branch: main ✅ / 别 branch ⚠️
- 已修改未 staged: N 个文件（[列名字 / 摘 3 个]）
- untracked: N 个（[残留垃圾列出来 / 正常文件不列]）
- 未 push commit: N 条（最新 [hash] [一句话]）
- stash: 无 / N 条

**多会话占用**：[Mac 主会话 / 其他设备 / 无 — 来自 §3 诊断]

**疑似遗留 / 需确认**：
- [污染项 1，问 itsuki 删还是保留]
- [污染项 2]

→ 请告诉我接下来做什么。
```

**铁律**：
- 不主动催进度（"还有 X 没做"等 itsuki 主动问）
- 不主动列 TODO（TODO 是 itsuki 主动问才读）
- 不主动建议下一步（除非 itsuki 问）

---

## §3 多会话占用诊断算法

> **背景**：itsuki 可能在 Mac 开了 2 个 Claude Code 会话（一个主，一个改 iOS）。如果当前会话不知道另一个会话的存在 → 直接覆盖别会话的修改 = 灾难。

### 信号 A: WIP §多会话占用 段写了什么

```bash
grep -A 5 "## 多会话占用" 00_admin/WIP.md
```

如果显式写了「Mac 另一会话改 iOS」→ **当场报告 itsuki 这个声明，问是否仍占用**。

### 信号 B: 工作树有意外修改

如果 `git status` 显示了**今天没动过的文件**也被修改 → 大概率是别会话改的。

```bash
git status --short | head -20
git log --oneline -5 --since="2 hours ago"
```

对比：working tree 改了 X 文件，但近 2 小时没有相关 commit → 说明别会话在改但还没 commit。

### 信号 C: 文件 mtime 与会话起始时间冲突

```bash
find 03_dev/ -newer 00_admin/WIP.md -type f 2>/dev/null | head -10
```

如果有文件 mtime 比 WIP.md 新（WIP 应该是上次会话最后更新的） → 别会话在动文件。

### 报告

```
⚠️ 多会话占用嫌疑

WIP 声明: [文本 / 无]
工作树异常: [描述哪些文件被改但没 commit]
最新 mtime: [03_dev/student_ios/.../X.swift @ 14:32]

→ 请确认：现在是否有别的 Claude Code 会话在改 iOS / backend / 文档？
   如果有 → 我等它 commit 完再开干。
   如果没 → 可能是上次会话残留，告诉我怎么处理（discard / commit / stash）。
```

---

## §4 反模式（CC 启动经常漏的 6 个失职点）

### ❌ 反模式 1: 只读 WIP 不查 git status
**后果**：WIP 是 itsuki 上次手动写的快照，不反映当下工作树。漏掉今天早上 itsuki 自己改的 / 别会话改的。

### ❌ 反模式 2: 看到一堆 ?? 文件直接忽略
**后果**：里面可能藏着 itsuki 重要的设计文件（.psd 源 / icon.json 配置）也可能是该删的垃圾（.pbxproj.bak）。**必须每个 ?? 都问清楚或归类**。

### ❌ 反模式 3: 不检查未 push commit
**后果**：itsuki 以为已经 push 了，但本地 7 个 commit 没 push。CC 启动时主动报这个，他可能立刻让推。

### ❌ 反模式 4: 不检查 stash
**后果**：上周 stash 的活完全忘了，新功能做完又 stash pop 出来冲突。

### ❌ 反模式 5: 不主动诊断多会话
**后果**：覆盖别会话的修改。**这是 itsuki 最痛的失职** — 历史多次发生（详见 raw 日志）。

### ❌ 反模式 6: 启动就主动催进度 / 列 TODO
**后果**：违反 CLAUDE.md「不主动催」规则。itsuki 自己有节奏，CC 等问才答。

---

## §5 配套文件

- `00_admin/WIP.md` — 当下书签（启动主读源）
- `00_admin/TODO.md` — 完整 backlog（**只在 itsuki 主动问才读**）
- `CHANGELOG.md` — 版本号 single source
- `00_admin/hooks/post-edit-sync-check.sh` — 改文件自动跑联动检查（不是启动跑，是 CC 改文件时跑）

---

## §6 触发关键词速查

| itsuki 说 | 必跑 |
|---|---|
| 「启动」 | ✅ 全 7 步 |
| 「早上好 / 我回来了 / 继续 / 干活」 | ✅ 全 7 步 |
| 新会话第一条消息 | ✅ 全 7 步（即使没明示） |
| 「现在状态如何 / repo 怎么样」 | ✅ 全 7 步 |
| 「读 WIP」 | 🔵 只读 WIP（用户明确缩窄范围） |

---

**最后更新**：2026-05-04 itsuki 拍板新建（戳穿 CC 启动失职 → 主流程化）
