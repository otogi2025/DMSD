---
name: version-bump
description: DMSD 版本号 bump 完整流程（5 步 + 7 处联动文件强制同步）。⭐ 主触发 = itsuki 说「迭代 / bump / 发版本 / 打 tag / 升级版本 / 发布 vX.Y.Z」。⭐ CC 有否决权 — 即使 itsuki 说要迭代，CC 读完 §2 决策树后判断不该 bump，可以拒绝。⭐ 版本演变一览必更新 — 历史已踩漂移（v0.6.0 / v0.8.0 都没更新到一览），现在写成铁律强制。包含决策树 / 5 步流程 / 7 处联动 / commit 前缀 / staging 污染防御 / 30 秒判断 / 路线图。
when_to_use: ⭐ 主触发 — itsuki 说「迭代 / bump / 发版本 / 打 tag / 升级版本 / 发布 / release / 升到 v0.X.Y」。次触发 — 改了 01_specs/ 主体 / 字典 / 02_design/system_features.md / 03_dev/ 主体 / pre-commit hook 提醒 "考虑 bump" / 累积 5+ commit 含实质改动 / 会话结束做一致性检查。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Version Bump Skill — DMSD 版本迭代完整流程

> **核心理念**：版本号 bump = **多文件强制同步动作**，不是 "改 CHANGELOG 就完事"。每次 bump **强制更新 7 处联动文件**（不是 SOP 旧版的 6 处 — 因为 v0.6.0 / v0.8.0 漂移让我意识到要加防御）。
>
> **来源**：基于 `00_admin/版本管理SOP.md`（v0.4.0 建立 → v0.7.0 首次全套跑通 → 但 v0.6.0 / v0.8.0 漂移证明 prompt 不够强）+ 2026-05-04 itsuki 4 条新铁律（否决权 / 必更一览 / 全量扫描 / 迭代关键词）→ 整体迁入做成 skill。
>
> **原 SOP 文件位置**：归档到 `99_archive/2026-05-04_版本管理SOP_迁入skill/`。

---

## §0 四条根本性原则（⭐ 2026-05-04 itsuki 拍板）

### 0.1 ⭐⭐⭐ CC 否决权（最重要）

> **「就算我说了迭代，然后他读了这个 skill 他也有权利否定我说不用迭代」** — itsuki 2026-05-04

**铁律**：CC 不是 itsuki 的"按钮执行器"。即使 itsuki 显式说「迭代 / bump / 发版本」，CC **必须先走完 §2 决策树**，根据决策树结果判断：

| 决策树结果 | CC 该做 |
|---|---|
| 命中 §2 任一 bump 触发条件 | ✅ 走 §3 流程，告诉 itsuki "建议 bump 到 vX.Y.Z（理由：...）" |
| 全部不命中（只有 typo / 文档整理 / raw dump / memory）| 🛑 **拒绝 bump**，告诉 itsuki "你说要迭代，但按 §2 决策树本会话改动不触发 bump，建议保持当前版本，理由：..." |
| 模糊 / 边界 case | ⚠️ 列出 itsuki 这次会话改动 + §2 命中分析 → 让 itsuki 拍板 |

**为什么这条最重要**：
- itsuki 自己说了 — **「有时候我自己不能判断要不要迭代，也不知道迭代到什么地步。所以是要由 AI 由 CC 来判断」**
- 防止"想到 bump 就 bump"导致版本号通胀（应是有意义的里程碑）
- 防止 CC 沦为"按钮机器人"，强制 CC 担起判断责任

**否决话术**（CC 拒绝 bump 时用）：
```
你说要迭代，但我读完 §2 决策树后判断本次会话**不该 bump**，理由：
- 本会话改动：[具体列出]
- §2 决策树命中：[第 7-9 条 → 不 bump 类]
- 建议：保持当前版本 vX.Y.Z，先把改动累积到下次会话再决定

要不要我详细讲为什么这次不该 bump？
```

### 0.2 ⭐ 版本演变一览必更新（铁律）

> **历史漂移证据**：2026-05-04 审视发现 — **v0.6.0（4-29 close）+ v0.8.0（5-02 close）都没更新到 `00_admin/版本演变一览.md`**。SOP §4 第 3 行写了"必改"但实战漂移。所以做 skill 时要明确铁律。

**铁律**：**每次 bump 必须更新 `00_admin/版本演变一览.md`**，不能跳过。如果 CC 走 §3 流程时漏了这一步，**视为 bump 失败**，必须回头补。

**怎么写一览段**：
- 标题格式：`## vX.Y.Z — 一句话主题（YYYY-MM-DD close）`
- 内容：3-5 个子段（新建文件 / 关键决策 / 元规则修订 / 基建 / AC 素材 等）
- 长度：~50-100 行（参考 v0.3.1 / v0.4.0 / v0.5.0 / v0.7.0 既有段）
- 重点：**面向不熟悉项目的读者写**（AC 提交时教授 / 访客）— 每条具体说"变化了什么 + 为什么变"

**待补的历史欠债**（CC 主动识别，等 itsuki 拍板补不补）：
- v0.6.0 段（老师 4-29 LINE 38 条受领 + RollCall_Spec 5 处时序修订 + system_features 中文骨架大重写）
- v0.8.0 段（三端代码层全启动）

### 0.3 ⭐ 全量扫描迭代相关文件（不偷懒）

> **「记得看一下我有哪些文件是跟迭代有关的。找不到的话就有项目文件总览。但是有些新文件没有包括，所以你也不要偷懒」** — itsuki 2026-05-04

**铁律**：CC 在执行 bump 时，**不能只看本 skill 的 §4 联动清单就 ok**。每次 bump 前必须额外做：

1. **grep 全 repo `<!-- VERSION_OK -->`** — 确认所有"豁免硬编码版本号"的位置都还有效
2. **检查 `.claude/skills/project-overview/SKILL.md`** 有没有新增"跟迭代相关"的文件（比如新的 AC 叙事文档、版本相关分析文件）
3. **检查 `00_admin/文档同步点清单.md §1`** — 单源真值规则有没有变
4. **看自上次 bump 以来 git log** — 有没有新文件写了 `<!-- VERSION_OK -->` 但 §4 清单没收录

如果发现新增"应该联动 bump 但 §4 清单没列"的文件 → **当场更新本 skill 的 §4**（这是 §11 SOP 自维护规则的应用）。

### 0.4 当前版本单一真值

**`CHANGELOG.md` 顶部第一条 `## [vX.Y.Z] - YYYY-MM-DD`** = 当前版本。

特殊情况：
- `## [vX.Y.Z-wip]` = 该版本"在路上"还没 close（**需要决定何时关闭**）
- `## [vX.Y.Z]` = 已 close，但 git tag 可能还没打

**二级源**（同步副本）：`WIP.md` 头部第一行 + `git tag` 列表。三处不一致 → 以 CHANGELOG 顶部为准。

---

## §1 5 秒速查卡（最关键 5 行）

1. **当前版本** = `CHANGELOG.md` 顶部第一条（也同步在 `WIP.md` 头部）
2. **改 spec 主体 / 字典 / 02_design / 03_dev 大块** → 必读 §2 决策树
3. **决定 bump** → 跑 §3 五步 + 对照 §4 联动文件清单（**必改 7 处**）
4. **commit 前缀对照表** → §5
5. **协作模型**（CC 自动 commit / itsuki 主导 push + bump + AC 叙事 / CC 执行 tag）→ 详见 session-wrap skill §5.5.7

---

## §2 决策树：这次改动该 bump 吗？

按从上到下顺序判断，命中第一条就停：

| # | 改动类型 | 应该 |
|---|---|---|
| 1 | 改了 `01_specs/rollcall/RollCall_Spec*.md` 业务规则主体（不只是 typo） | **Minor** bump |
| 2 | 改了字典（FIELD / ENUM / ERROR / DEVICE / API_CONVENTIONS）的实质内容（加字段 / 改语义 / 加枚举） | **Minor** bump |
| 3 | 新建 `02_design/` 设计文档（>100 行） | **Minor** bump |
| 4 | `03_dev/` prototype 大幅扩展（如新增页面 / 新增账号管理 / 业务规则改写）| **Minor** bump |
| 5 | 改了 CLAUDE.md 元规则 / 加新章节 / 新决策机制 | **Patch** bump |
| 6 | 命名 / 品牌变更（如 4-21 Tomoshibi）| **Patch** bump |
| 7 | 修 typo / 改格式 / 调排版 / 整理文档 | **不 bump** |
| 8 | raw log dump / AC 叙事 / 反思记录 / memory 更新 | **不 bump** |
| 9 | hooks / .gitignore / scripts 调整 | **不 bump** |

### 0.x 阶段的特殊规则

- **0.x 不严格区分 Major / Minor**：破坏性改动也用 Minor（按 SemVer 0.x 约定）
- **1.0.0 = 系统在宿舍正式上线**

### 累积判断（重要）

**单次 commit 不 bump 不代表永远不 bump**。如果累积 5+ commit 都属"不 bump"但触达 Minor / Patch 阈值，会话结束时就该 bump 了。

例：4-22 → 4-29 demo-4-28 sprint 期间每次 commit 都是 `feat(demo-4-28):`，单看每条只是 prototype 扩展，但累积起来是巨大的 Minor 范围扩展 → 应在 4-29 close 为 v0.5.0。

---

## §3 Bump 五步流程（按顺序执行）

### 步骤 1：决定版本号

- 看 CHANGELOG 顶部当前是什么 → 套 §2 决策树 → 算出新版本号
- 如果有累积的 `[X.Y.Z-wip]` 段 → 决定是 close 它还是新开
- ⭐ **CC 否决权检查**：这次 bump 是 itsuki 主动说"迭代"还是 CC 自己判断的？
  - itsuki 主动说但 §2 决策树不命中 → 走 §0.1 否决话术
  - CC 自己判断 → 给 itsuki 看决策树命中位置 + 等他确认

### 步骤 2：更新 CHANGELOG.md

- 新版本条目放最上面（倒序）
- 必含：日期 + "为什么 bump" 说明 + Added / Changed / Fixed / Notes 分类
- 头部 "最后更新" 时间戳同步刷新
- 参考 v0.3.2 / v0.7.0 段的写法

### 步骤 3：同步 §4 联动文件（**必改 7 处**）

见 §4 表格，逐项过。**§4 第 3 项「版本演变一览」是 §0.2 铁律 — 不能跳过**。

### 步骤 4：commit

- message 首行：`release(vX.Y.Z): 一句话总结`
- message 主体：分点列 why + what + scope
- 不写 `Co-Authored-By` trailer（DMSD 项目规则）
- 不要 `--no-verify` 跳过 hook
- 用 HEREDOC 传 message（中文换行才正确）

### 步骤 5：打 tag（**等 itsuki 明示**）

- `git tag -a vX.Y.Z -m "release(vX.Y.Z): 一句话"`
- `git push origin vX.Y.Z`（仅当 itsuki 明说 push）
- **CC 不能自动打 tag** — 这是发布动作，必须 itsuki 拍板

---

## §4 Bump 时联动文件清单（**必改 7 处**）

> ⭐ 比旧 SOP 多一处（第 7 项）— 因为 itsuki 拍板要求"全量扫描"，发现 `.claude/skills/project-overview/SKILL.md` 也是迭代联动点（新建 AC 叙事文档时要更新总览）。

| # | 文件 | 改什么 | 谁改 | 优先级 |
|---|---|---|---|---|
| 1 | `CHANGELOG.md` | 顶部新条目 + 头部"最后更新"时间戳 | CC | 🔴 必 |
| 2 | `00_admin/WIP.md` | 头部第一行 `**当前版本**: vX.Y.Z` | CC | 🔴 必 |
| 3 | `00_admin/版本演变一览.md` | 加新版本一句话 + 详细段（按既有格式） | CC | 🔴 **必（§0.2 铁律）** |
| 4 | `00_admin/vX.Y.Z_AC叙事.md` | 新建（5-04 起 itsuki 自写；CC 不主动起草，等 itsuki 来问才辅助） | itsuki | 🔴 必（itsuki 侧）|
| 5 | `05_logs/raw/YYYY-MM-DD.md` | dump 一条 #AC候选 标 "版本号 bump = 重大决策"（按 session-wrap skill）| CC | 🔴 必 |
| 6 | `git tag` | 打 tag（**等 itsuki 明示**）| itsuki / CC 经授权 | 🟠 半必 |
| 7 | `.claude/skills/project-overview/SKILL.md` | 如果新建了 vX.Y.Z_AC叙事.md → §1.4 加新条目 + 计数 | CC | 🟠 半必（条件触发）|

### 可选联动（按情况）

- iCloud `00_通用指南/版本管理实践指南.md §12` 项目规划表 — itsuki 同步（CC 不写 iCloud）
- `00_admin/TODO.md` — 如果 bump 影响 TODO 排期
- `00_admin/progress_overview.md` — 如果是章节级里程碑

### 全量扫描清单（§0.3 铁律 — 每次 bump 前跑）

```bash
# 1. 找所有"硬编码版本号豁免"位置 → 看有没有过期
grep -rn "VERSION_OK\|<!-- VERSION" /Users/kurekoduki/dev/DMSD/ --include="*.md" | grep -v 99_archive

# 2. 看自上次 bump 以来新建的文件（可能是新联动点）
git log --diff-filter=A --name-only $(git tag --sort=-v:refname | head -1)..HEAD | grep -v 99_archive | grep -v 05_logs/raw

# 3. 检查项目文件总览有没有新增"跟迭代相关"的文件
grep -i "version\|版本\|bump\|tag" /Users/kurekoduki/dev/DMSD/.claude/skills/project-overview/SKILL.md
```

发现新增联动点 → 当场更新本 §4（不要绕开）。

---

## §5 Conventional Commits 速查（commit 前缀）

| 前缀 | 含义 | 版本影响 | 例 |
|---|---|---|---|
| `feat:` | 新功能 | **Minor 候选** | `feat(spec): 新增 device_id 字段` |
| `fix:` | 修 bug | **Patch 候选** | `fix(spec): API_CONVENTIONS S13 闭合` |
| `docs:` | 只改文档 | 不 bump | `docs: 更新 README` |
| `chore:` | 杂事 | 不 bump | `chore: .gitignore 扩充` |
| `refactor:` | 重构 | 不 bump | `refactor: 03_dev 目录扁平化` |
| `style:` | 格式 | 不 bump | `style: typo 修正` |
| `test:` | 测试 | 不 bump | `test: 加点呼测试` |
| `feat!:` | 破坏性新功能 | Major（1.0 后）| `feat!: 重写认证` |
| `release(vX.Y.Z):` | 发布版本（DMSD 自定义）| 跟随 vX.Y.Z | `release(v0.5.0): demo sprint 收尾` |

---

## §6 多会话协调

### 谁有权 bump

- **bump 是 `[Mac-主会话]` 的特权**（一次只能一个会话改 CHANGELOG）
- 其他会话发现累积到阈值 → 在 WIP.md "进行中"段提醒 itsuki "建议 bump 到 vX.Y.Z"
- 不要两个会话同时改 CHANGELOG.md（git conflict 不好处理）

### -wip 状态的协调

- `[X.Y.Z-wip]` 标在 CHANGELOG 顶部期间，多会话可以一起往里堆 commit
- 但 close（去掉 `-wip`）+ 打 tag = `[Mac-主会话]` 一个人做

### ⚠️ Staging area 污染防御（2026-04-29 实战教训）

**事件**：4-29 [Mac-VersionMgmt-CC] commit `0e9fbb7` 时，staging area 已含**另一会话 stage 但未 commit** 的 `D 02_design/teacher_requirements.md`（删除）。当前会话 `git add 00_admin/WIP.md` 后 commit，把别人 stage 的删除**一起 push 出去**，导致 GitHub 上 main 误删该文件 6 分钟。

**为什么 hook 没拦下**：pre-commit hook 只检查"声明性文件硬编码版本号"，不验证 staged files 是否符合本次会话意图。

**铁律**：
- **commit 前必须 `git status` 逐项核对 staged 内容**
- 看到不是本会话改的文件出现在 staged area → **`git restore --staged <file>`** 取消 stage（不动工作树）
- 不要假设 "我没改的就不会被 commit"（错的，staging area 可能被另一会话污染）

**实操话术**（CC 在 commit 前必跑）：
```
git status --short
# 逐行问："这一行是本会话产出吗？" 不是的 → git restore --staged
```

**为什么会话间 staging 污染？** Mac 上多个 CC 会话共用同一个 git index（`.git/index` 文件），任何会话 git mv / git add / git rm 都改这个共享 index。所以 staged area 不属于"本会话"。

---

## §7 何时不 bump（错觉清单）

- ❌ 一天写了 50 个 commit ≠ 一天打 50 个 tag
- ❌ 改了 5 个 typo ≠ 5 次 patch bump（攒到下次 minor 一起 close）
- ❌ raw log dump 不 bump（这是记录，不是产品改动）
- ❌ memory 更新 不 bump
- ❌ TODO / WIP 内部协调 不 bump
- ❌ AC 叙事 / 反思 不 bump
- ❌ hooks / scripts 不 bump
- ❌ pre-commit 提示"考虑 bump"不等于"必须 bump" — 它只是提醒，最终判断回归 §2 决策树
- ❌ **itsuki 说"迭代"也不等于必须 bump** — §0.1 否决权适用

---

## §8 历史教训（DMSD 踩过的）

| 时间 | 教训 | 解法 |
|---|---|---|
| 2026-02-12 | 文件名写 v1.0 但项目还没代码 | 0.x 阶段不要用 1.x 文件名 |
| 2026-04-13 | 命名整理 bump 到 v0.2.0（应该是 patch v0.1.1）| 命名 ≠ 实质改动 |
| 2026-04-17 | 文件名 _v0.1 但项目实质 v0.2.0 | 文件名不带版本号（2026-04-29 已修正）|
| 2026-04-19 | CLAUDE.md / WIP / TODO 残留过期版本号 | 单源真值 + pre-commit hook + 文档同步点清单 |
| 2026-04-21 → 04-29 | bump 到 [0.4.0-wip] 后拖 9 天没 close + 累积 15 commit | SOP 建立 + WIP 头部加版本行 + hook 提醒 |
| **2026-05-02 / 04-29** | **v0.6.0 + v0.8.0 close 但版本演变一览没更新** | **本 skill §0.2 铁律 + 把 SOP 做成 skill 强制** |

---

## §8.5 版本路线图（0.7 → 1.0 预测，2026-04-30 起草）<!-- VERSION_OK -->

> **目的**：让未来 agent 不要"看 v0.7.0 完成后下一步该做什么"还要重新猜。这是 itsuki 4-30 拍板的业务推进顺序，版本号跟着业务里程碑走。<!-- VERSION_OK -->
>
> **前提**（itsuki 2026-04-30 明示）：
> - **iOS / Web 前端** = round3 demo 代码"改改就能用"（接真后端 + 删 demo 脚手架，**不是从 0 写**）
> - **Android 前端 + 后端** = 完全没开始（**从 0 写**）

### 路线图

| 版本 | 里程碑 | 工作量 | 关键依赖 |
|---|---|---|---|
| **v0.7.0** | 设计层 39 条 + REQUIREMENTS brief 完成 | 三轨 A/B/C（4-30 close）| - | <!-- VERSION_OK -->
| **v0.8.0** | 后端实装（从 0 写）+ 数据库 schema 落地 | 大 — 后端是其他三端的地基 | — | <!-- VERSION_OK -->
| **v0.9.0** | Android 前端实装（从 0 写）| 大 — 整个 App 框架要搭 | 后端 done | <!-- VERSION_OK -->
| **v0.10.0** | iOS + Web 从 demo 升级到生产版 | 中 — 接真后端 + 删 demo-only 脚手架 | 后端 done | <!-- VERSION_OK -->
| **v1.0.0** | 三端 + 后端联调 + 真上线 | 联调 + 测试 | 0.8 / 0.9 / 0.10 全 done | <!-- VERSION_OK -->

### 关键依赖关系

```
后端（v0.8.0）<!-- VERSION_OK -->
    ↓ 必须先有，否则没"真"数据
    ├→ Android（v0.9.0 从 0 写）<!-- VERSION_OK -->
    └→ iOS / Web（v0.10.0 从 demo 升级）<!-- VERSION_OK -->

→ 三端齐 + 后端齐 = v1.0.0 <!-- VERSION_OK -->
```

**没后端 → iOS / Web 现有 demo 也升级不了**（demo 用客户端假数据，不是真 API）。所以**后端是最大瓶颈**。

### 风险点

| # | 风险 | 缓解 |
|---|---|---|
| 1 | iOS / Web 的 demo-only 脚手架必须 v1.0 前删干净 | memory `feedback_demo_scaffolds_to_remove_before_v1.md` 已记。**不删 = 学生能自己伪造点呼状态 = 安全漏洞**。v0.10.0 时一并清理 | <!-- VERSION_OK -->
| 2 | Android NFC HCE（Host Card Emulation = 手机假装自己是 NFC 卡）API 跟 iOS 完全两套 | v0.9.0 工作量可能比 iOS / Web 加起来还大，预留缓冲 | <!-- VERSION_OK -->

### 路线图维护规则

- 这是"预测"，不是"承诺"。每完成一个版本号 → 回头修正下一个版本号的工作量预估和这一节
- 顺序可能调：比如 Android NFC HCE 卡住 → 可能 v0.9 / v0.10 顺序换 <!-- VERSION_OK -->
- **v1.0 = "在真宿舍跑给学生用"是死的目标**，0.8 / 0.9 / 0.10 是活的中间过程 <!-- VERSION_OK -->
- 改本节不触发 bump（按 §11 SOP 维护规则属 doc 改动）

---

## §9 文件名版本号规则（2026-04-29 拍板）

### 新规则

- **新建文件**：**不要在文件名里写版本号**。版本由 git tag + CHANGELOG 管理
- 例：`02_design/system_features.md` ✅，不要 `02_design/system_features_v0.1.md` ❌

### 例外（保留版本号的合法情况）

- 历史快照命名：`v0.1_冻结决策.md` — 是 "v0.1 那刻冻结的决策" 的快照
- AC 叙事：`vX.Y.Z_AC叙事.md` — 是 "vX.Y.Z bump 那刻" 的 AC 记录
- 版本相关分析：`v0.4.0_S系列spec漏洞优先级分析.md` — 是 "为 v0.4.0 准备的输入"

---

## §10 30 秒判断（会话结束前必跑）

会话结束前，跑这 4 问：

1. **本会话改了 spec 主体 / 字典 / 02_design / 03_dev 主体吗？** → 没改：跳过；改了：去 §2
2. **CHANGELOG 顶部是 `[X.Y.Z-wip]` 吗？** → 是：考虑这次会话产出能不能 close 它
3. **累积自上次 tag 已经多少 commit 了？** → 5+ + 包含实质改动：建议 bump
4. **itsuki 这次会话有"今天结束"信号吗？**（如 "明天再做" / "晚安" / "结束会话"）→ 有 + 上 3 项任一命中：**主动询问 itsuki 是否 bump**

固定话术：

```
本次会话累积改动：[列改了哪些 spec / design / 03_dev]
按 §2 决策树判断 → 建议 bump 到 vX.Y.Z（理由：...）
是否 bump？或者保持 [X.Y.Z-wip] 等下次会话再 close？
```

---

## §11 Skill 自维护规则

| 改 skill 什么 | 是否 bump |
|---|---|
| §4 联动清单加新文件 | 不 bump（属 patch 级 doc 改动） |
| §2 决策树加新场景 | 不 bump |
| 新建 § 章节 | Patch |
| skill 整体重构 | 不 bump |

**skill 自身的更新触发**：
- 发现现实和 skill 不一致 → 改 skill 而不是绕开
- 出现新文件 / 新文件类型 → 加进 §4
- itsuki 推翻 skill 某条规则 → 改 skill 同时记到 raw log

---

## §12 给新 Claude 会话的 Onboarding

新会话遇到下列任一情景立即激活本 skill：

| 情景 | 读哪节 |
|---|---|
| 用户问"现在版本是多少" | §0.4 |
| 用户问"下一个版本是什么" / "v0.X 之后做什么" | §8.5 |
| 即将 commit `feat:` / `fix:` 前缀 | §2 §5 |
| 改了 `01_specs/` 主体或字典 | §2 §3 §4 |
| 改了 `02_design/system_features.md` | §2 §3 §4 |
| **用户说 "迭代" / "bump" / "打 tag" / "升级版本"** | **§0.1（否决权）→ §2 → §3 §4** |
| pre-commit hook 输出"考虑 bump" 提醒 | §2 |
| 会话结束做一致性检查 | §10 |
| 不确定何时 bump | §1 速查卡 |

---

## §13 发版动作（bump 决定后做什么 — 2026-05-04 从 release-checklist skill 合并进来）

> **背景**：原本独立 `release-checklist` skill，itsuki 拍板合并 — 因为 version-bump（决定要不要发）和发版动作（决定后做什么）天然串联，分两个 skill 反而割裂。
>
> **场景串联**：itsuki 说「发版 v0.4.0」 → §0.1 否决权判断 + §2 决策树 → 确认要 bump → §3-§6 改 CHANGELOG / commit → 进入本节做 tag / push / 跨 repo 同步。

### §13.0 主流程（按时序 5 阶段）

```
T-7 天: 长准备（minor / major bump 才做，patch 跳）
T-1 天: 最后检查
T 当天: 发版动作（核心 8 步）
T+1 天: 发版后监控
T+N 天: 回滚预案（如出问题）
```

### §13.1 T-7 天：长准备（minor / major）

- [ ] 跟 itsuki 确认本次发版 scope（哪些 feature / fix 进 / 不进）
- [ ] 确认 demo 环境（如果有外部演示日期）
- [ ] **major 版本（v1.0.0 / v2.0.0 等）**：先按 `02_design/system_features.md` 末尾「v1.0 上线前必删 demo scaffold 清单」逐条清理
- [ ] 写 release notes 草稿（CHANGELOG.md 顶部新建段标 `[Unreleased]`）
- [ ] 跑全套测试（iOS Xcode + backend pytest）确认基线 green

### §13.2 T-1 天：最后检查

- [ ] git status 工作树干净（无未 commit 改动）
- [ ] CHANGELOG.md 顶部 `[Unreleased]` 段 → 改成正式版本号 + 日期
- [ ] 同步点清单 11 项全过：`00_admin/文档同步点清单.md`
- [ ] WIP.md / TODO.md / progress_overview.md 最近更新对齐
- [ ] `bash bin/sync-check.sh` → 0 警告
- [ ] `bash 00_admin/hooks/pre-commit` 手动模拟 → 0 阻塞

### §13.3 T 当天：核心 8 步

#### Step 1: 最终 CHANGELOG

```bash
# 编辑 CHANGELOG.md 顶部
# - 把 [Unreleased] 改成 [vX.Y.Z] - YYYY-MM-DD
# - 检查 Added / Changed / Fixed / Removed 段完整

git add CHANGELOG.md
git commit -m "chore(release): vX.Y.Z"
```

#### Step 2: 打 tag

⚠️ **铁律**（memory `feedback_commit_push_tag_division.md`）：tag 是 itsuki 拍板动作，CC **起草命令等指令**，不主动跑。

```bash
# annotated tag（不要 lightweight tag — 没 metadata）
git tag -a vX.Y.Z -m "Release vX.Y.Z

主要变化:
- ...
- ...

详见 CHANGELOG.md"

# 确认
git tag --list | tail -3
git show vX.Y.Z --stat | head -20
```

#### Step 3: push commit + tag

⚠️ **push 也是 itsuki 拍板动作** — CC 起草命令等指令。

```bash
git push origin main
git push origin vX.Y.Z
```

#### Step 4: 跨 repo 同步（iOS）

DMSD 是 iOS single source；`otogi2025/Tomoshibi-iOS` 是镜像。

```bash
bash bin/sync-ios-refs.sh
cd ../Tomoshibi-iOS  # 或对应路径
git status            # 确认同步进来的改动
git tag -a vX.Y.Z -m "..." && git push --follow-tags origin main
cd -
```

#### Step 5: GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - <一句话标题>" \
  --notes "$(awk '/^## \[vX.Y.Z\]/,/^## \[v/{print}' CHANGELOG.md | head -n -1)"
```

或手动 https://github.com/otogi2025/DMSD/releases/new。

#### Step 6: 文档同步点 final check

跑一遍 `00_admin/文档同步点清单.md` Release Checklist 段。

#### Step 7: WIP / TODO 收尾

- [ ] WIP.md 最近会话条目加「vX.Y.Z 发版完成」
- [ ] TODO.md 把已发版功能从 backlog 划掉
- [ ] `00_admin/hooks/pre-commit` 重跑确认 hook 不抓硬编码版本号

#### Step 8: 通知 / 公告（如需要）

minor / major 如有外部用户：
- iOS 用户：TestFlight 推送 build
- 演示：通知宿舍管理员
- AC 素材：dump 到 `05_logs/raw/<date>.md` 标 5 级里程碑

### §13.4 T+1 天：发版后监控

- [ ] crash log（iOS Sentry / 手动收集）
- [ ] backend 日志报错率
- [ ] 用户反馈（如有渠道）

如有问题 → 决定 hotfix（patch bump）/ 回滚。

### §13.5 T+N 天：回滚预案

#### 客户端炸（iOS）
- 快速 hotfix → 走 patch bump 流程（vX.Y.Z+1）
- 严重时：从 TestFlight 撤掉 build

#### Backend 炸
- `git revert <commit>` 回退部署
- alembic downgrade（如果有数据库 schema 变化）
- 通知客户端用户

#### 完全撤回 release（慎用）

```bash
# 删 GitHub Release（不删 tag）
gh release delete vX.Y.Z

# 删 tag（local + remote）— 不可逆，itsuki 必须明确拍板
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
```

### §13.6 反模式

| ❌ 反模式 | 正确做法 |
|---|---|
| CC 主动 git push | push / tag / 删 tag 全部 itsuki 拍板，CC 起草命令等指令 |
| tag 用 lightweight（git tag X 没 -a） | annotated tag `git tag -a vX.Y.Z -m "..."` |
| 跳 CHANGELOG 直接打 tag | 先 CHANGELOG 段成型 → chore(release) commit → 再 tag |
| 漏跨 repo 同步 | bin/sync-ios-refs.sh + Tomoshibi-iOS 也打同步 tag |
| 漏 hooks 验证 | T-1 § + T 当天 Step 7 都跑 hook 验证 |
| major 跳 demo scaffold 清理 | major 版本必先按 system_features.md 末尾清单清理 |

### §13.7 触发关键词

| itsuki 说 | 走到 |
|---|---|
| 发版 / 打 tag / release / 推上去 / 发布 v0.X.Y | §13.0 主流程 |
| 跨 repo 同步 | §13.3 Step 4 |
| 回滚 / 撤掉 release | §13.5 |

---

**END** — Version Bump Skill
