# 版本管理 SOP（运行手册）

> **这是给 Claude Code 看的运行手册**（不是教科书）。每次会话遇到 spec / 字典 / 02_design / 03_dev 改动时**必读 §2 §3 §4**。
>
> **和 iCloud 版本管理实践指南.md 的分工**：
> - **iCloud 版本管理实践指南**（教科书）— 讲 SemVer 理论 / 业界标准 / DMSD 长期路线图 / 历史教训。读者 = itsuki 学习时看。
> - **本 SOP**（运行手册）— 讲"这次改动该不该 bump / bump 时改哪些文件 / 完整命令"。读者 = **每个 Claude 会话**。
>
> 类比：iCloud 那份是数学课本，本 SOP 是考试时的"公式速查卡"。
>
> **最后更新**：2026-04-29（首版建立 — 解决"4-21 → 4-29 9 天累积没 bump"问题）
>
> **触发本 SOP 阅读的情景**：
> - 即将 commit `feat:` / `fix:` 前缀 → 读 §2 §3
> - 改了 `01_specs/` 主体 / 字典 / `02_design/system_features.md` → 读 §2 §3 §4
> - itsuki 说"打 tag" / "bump" / "迭代版本" → 读 §3 §4
> - 会话结束做 §一致性检查 → 读 §10 30 秒判断
> - 用户问"现在版本是多少" → 读 §1

---

## § 0 — 5 秒速查卡（最关键 5 行）

1. **当前版本** = `CHANGELOG.md` 顶部第一条 `## [vX.Y.Z]`（也同步在 `WIP.md` 头部）
2. **改 spec 主体 / 字典 / 02_design / 03_dev 大块** → 必读 §2 决策树
3. **决定 bump** → 跑 §3 五步 + 对照 §4 联动文件清单（必改 6 处）
4. **commit 前缀对照表** → §5（feat=minor 候选 / fix=patch 候选 / docs+chore=不 bump）
5. **协作模型**（CC 自动 commit / itsuki 主导 push + bump + AC 叙事 / CC 执行 tag）→ 单源真值在 `.claude/skills/ac-record/SKILL.md §5.5.7`

---

## § 1 — 当前版本怎么知道

### 单一真值

**`CHANGELOG.md` 顶部第一条 `## [vX.Y.Z] - YYYY-MM-DD`** = 当前版本。

特殊情况：
- `## [vX.Y.Z-wip]` = 该版本"在路上"还没 close（**需要决定何时关闭**）
- `## [vX.Y.Z]` = 已 close，但 git tag 可能还没打

### 二级源（同步副本，bump 时一起改）

- `WIP.md` 头部第一行 `**当前版本**: vX.Y.Z`（带 `<!-- VERSION_OK -->` 豁免，bump 时人工同步）
- `git tag` 列表（`git tag -l | sort -V`）

> **如果三处不一致**：以 CHANGELOG 顶部为准，立即修正其他两处（属于 §一致性漂移 bug）。

---

## § 2 — 决策树：这次改动该 bump 吗？

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
- **1.0.0 = 系统在宿舍正式上线**（详见 iCloud 版本管理实践指南 §1）

### 累积判断（重要）

**单次 commit 不 bump 不代表永远不 bump**。如果累积 5+ commit 都属"不 bump"但触达 Minor / Patch 阈值，会话结束时就该 bump 了。

例：4-22 → 4-29 demo-4-28 sprint 期间每次 commit 都是 `feat(demo-4-28):`，单看每条只是 prototype 扩展，但累积起来是巨大的 Minor 范围扩展 → 应在 4-29 close 为 v0.5.0。

---

## § 3 — Bump 五步流程（按顺序执行）

### 步骤 1：决定版本号

- 看 CHANGELOG 顶部当前是什么 → 套 §2 决策树 → 算出新版本号
- 如果有累积的 `[X.Y.Z-wip]` 段 → 决定是 close 它还是新开

### 步骤 2：更新 CHANGELOG.md

- 新版本条目放最上面（倒序）
- 必含：日期 + "为什么 bump" 说明 + Added / Changed / Fixed / Notes 分类
- 头部 "最后更新" 时间戳同步刷新
- 参考 v0.3.2 / v0.3.1 段的写法

### 步骤 3：同步 §4 联动文件（**必改 6 处**）

见 §4 表格，逐项过。

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

## § 4 — Bump 时联动文件清单（**必改 6 处**）

| # | 文件 | 改什么 | 谁改 |
|---|---|---|---|
| 1 | `CHANGELOG.md` | 顶部新条目 + 头部"最后更新"时间戳 | CC |
| 2 | `00_admin/WIP.md` | 头部第一行 `**当前版本**: vX.Y.Z` | CC |
| 3 | `00_admin/版本演变一览.md` | 加新版本一句话 + 详细段（按既有格式）| CC |
| 4 | `00_admin/vX.Y.Z_AC叙事.md` | 新建（按 v0.3.0 / v0.3.2 模板 6 节）| CC 起草 → itsuki 审 |
| 5 | `05_logs/raw/YYYY-MM-DD.md` | dump 一条 #AC候选 标 "版本号 bump = 重大决策"（CLAUDE.md 规定）| CC |
| 6 | `git tag` | 打 tag（**等 itsuki 明示**）| itsuki / CC 经授权 |

### 可选联动（按情况）

- iCloud `00_通用指南/版本管理实践指南.md §12` 项目规划表 — itsuki 同步（CC 不写 iCloud）
- `00_admin/TODO.md` — 如果 bump 影响 TODO 排期
- `00_admin/progress_overview.md` — 如果是章节级里程碑

---

## § 5 — Conventional Commits 速查（commit 前缀）

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

## § 6 — 多会话协调

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

## § 7 — 何时不 bump（错觉清单）

- ❌ 一天写了 50 个 commit ≠ 一天打 50 个 tag
- ❌ 改了 5 个 typo ≠ 5 次 patch bump（攒到下次 minor 一起 close）
- ❌ raw log dump 不 bump（这是记录，不是产品改动）
- ❌ memory 更新 不 bump
- ❌ TODO / WIP 内部协调 不 bump
- ❌ AC 叙事 / 反思 不 bump
- ❌ hooks / scripts 不 bump
- ❌ pre-commit 提示"考虑 bump"不等于"必须 bump" — 它只是提醒，最终判断回归 §2 决策树

---

## § 8 — 历史教训（DMSD 踩过的）

| 时间 | 教训 | 解法 |
|---|---|---|
| 2026-02-12 | 文件名写 v1.0 但项目还没代码 | 0.x 阶段不要用 1.x 文件名 |
| 2026-04-13 | 命名整理 bump 到 v0.2.0（应该是 patch v0.1.1）| 命名 ≠ 实质改动 |
| 2026-04-17 | 文件名 _v0.1 但项目实质 v0.2.0 | 文件名不带版本号（2026-04-29 已修正）|
| 2026-04-19 | CLAUDE.md / WIP / TODO 残留过期版本号 | 单源真值 + pre-commit hook + 文档同步点清单 |
| 2026-04-21 → 04-29 | bump 到 [0.4.0-wip] 后拖 9 天没 close + 累积 15 commit | 本 SOP 建立 + WIP 头部加版本行 + hook 提醒 |

---

## § 8.5 — 版本路线图（0.7 → 1.0 预测，2026-04-30 起草） <!-- VERSION_OK -->

> **目的**：让未来 agent 不要"看 v0.7.0 完成后下一步该做什么"还要重新猜。这是 itsuki 4-30 拍板的业务推进顺序，版本号跟着业务里程碑走。 <!-- VERSION_OK -->
>
> **前提**（itsuki 2026-04-30 明示）：
> - **iOS / Web 前端** = round3 demo 代码"改改就能用"（接真后端 + 删 demo 脚手架，**不是从 0 写**）
> - **Android 前端 + 后端** = 完全没开始（**从 0 写**）

### 路线图

| 版本 | 里程碑 | 工作量 | 关键依赖 |
|---|---|---|---|
| **v0.7.0** | 设计层 39 条 + REQUIREMENTS brief 完成 | 三轨 A/B/C 当前推进中（4-30）| 等 C 收尾 | <!-- VERSION_OK -->
| **v0.8.0** | 后端实装（从 0 写）+ 数据库 schema 落地 | 大 — 后端是其他三端的地基 | — | <!-- VERSION_OK -->
| **v0.9.0** | Android 前端实装（从 0 写）| 大 — 整个 App 框架要搭 | 后端 done | <!-- VERSION_OK -->
| **v0.10.0** | iOS + Web 从 demo 升级到生产版 | 中 — 接真后端 + 删 demo-only 脚手架 | 后端 done | <!-- VERSION_OK -->
| **v1.0.0** | 三端 + 后端联调 + 真上线 | 联调 + 测试 | 0.8 / 0.9 / 0.10 全 done | <!-- VERSION_OK -->

### 关键依赖关系

```
后端（v0.8.0）  <!-- VERSION_OK -->
    ↓ 必须先有，否则没"真"数据
    ├→ Android（v0.9.0 从 0 写）  <!-- VERSION_OK -->
    └→ iOS / Web（v0.10.0 从 demo 升级）  <!-- VERSION_OK -->

→ 三端齐 + 后端齐 = v1.0.0  <!-- VERSION_OK -->
```

**没后端 → iOS / Web 现有 demo 也升级不了**（demo 用客户端假数据，不是真 API）。所以**后端是最大瓶颈**。

### 风险点

| # | 风险 | 缓解 |
|---|---|---|
| 1 | iOS / Web 的 demo-only 脚手架必须 v1.0 前删干净 | memory `feedback_demo_scaffolds_to_remove_before_v1.md` 已记。**不删 = 学生能自己伪造点呼状态 = 安全漏洞**。v0.10.0 时一并清理 | <!-- VERSION_OK -->
| 2 | #21 老龄寮監（年纪大的宿舍老师）iPad UI 不在 B / C 范围 | 仍 ❌ baseline，要单独议题，可能 v0.7.x patch 内补 |
| 3 | #30 教师当天代录出寮届 | 同上，仍 ❌ baseline |
| 4 | Android NFC HCE（Host Card Emulation = 手机假装自己是 NFC 卡）API 跟 iOS 完全两套 | v0.9.0 工作量可能比 iOS / Web 加起来还大，预留缓冲 | <!-- VERSION_OK -->

### 路线图维护规则

- 这是"预测"，不是"承诺"。每完成一个版本号 → 回头修正下一个版本号的工作量预估和这一节
- 顺序可能调：比如 Android NFC HCE 卡住 → 可能 v0.9 / v0.10 顺序换 <!-- VERSION_OK -->
- **v1.0 = "在真宿舍跑给学生用"是死的目标**，0.8 / 0.9 / 0.10 是活的中间过程 <!-- VERSION_OK -->
- 改本节不触发 bump（按 §11 SOP 维护规则属 doc 改动）

---

## § 9 — 文件名版本号规则（2026-04-29 拍板）

### 新规则

- **新建文件**：**不要在文件名里写版本号**。版本由 git tag + CHANGELOG 管理
- 例：`02_design/system_features.md` ✅，不要 `02_design/system_features_v0.1.md` ❌

### 历史文件已 2026-04-29 重命名

| 旧文件名 | 新文件名 |
|---|---|
| `01_specs/API_CONVENTIONS_v0.1.md` | `01_specs/API_CONVENTIONS.md` |
| `01_specs/rollcall/DEVICE_REGISTRY_v0.1.md` | `01_specs/rollcall/DEVICE_REGISTRY.md` |
| `01_specs/rollcall/ENUM_REGISTRY_v0.1.md` | `01_specs/rollcall/ENUM_REGISTRY.md` |
| `01_specs/rollcall/ERROR_CODES_v0.1.md` | `01_specs/rollcall/ERROR_CODES.md` |
| `01_specs/rollcall/FIELD_REGISTRY_v0.1.md` | `01_specs/rollcall/FIELD_REGISTRY.md` |
| `01_specs/rollcall/RollCall_Spec_v0.1.md` | `01_specs/rollcall/RollCall_Spec.md` |
| `01_specs/rollcall/v0.1_冻结决策.md` | `01_specs/rollcall/v0.1_冻结决策.md`（保留 — 是历史快照命名，非状态声明）|
| `02_design/flow_design_v0.1.md` | `02_design/flow_design.md` |
| `02_design/hardware_design_v0.1.md` | `02_design/hardware_design.md` |
| `02_design/system_features_v0.1.md` | `02_design/system_features.md` |
| `02_design/teacher_requirements_v0.1.md` | `02_design/teacher_requirements.md` |

### 例外（保留版本号的合法情况）

- 历史快照命名：`v0.1_冻结决策.md` — 是 "v0.1 那刻冻结的决策" 的快照
- AC 叙事：`vX.Y.Z_AC叙事.md` — 是 "vX.Y.Z bump 那刻" 的 AC 记录
- 版本相关分析：`v0.4.0_S系列spec漏洞优先级分析.md` — 是 "为 v0.4.0 准备的输入"

---

## § 10 — 30 秒判断（会话结束前必跑）

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

## § 11 — SOP 维护规则

| 改 SOP 什么 | 是否 bump |
|---|---|
| §4 联动清单加新文件 | 不 bump（属 patch 级 doc 改动） |
| §2 决策树加新场景 | 不 bump |
| 新建 § 章节 | Patch |
| SOP 整体重构 | 不 bump |

**SOP 自身的更新触发**：
- 发现现实和 SOP 不一致 → 改 SOP 而不是绕开
- 出现新文件 / 新文件类型 → 加进 §4
- itsuki 推翻 SOP 某条规则 → 改 SOP 同时记到 raw log

---

## § 12 — 给新 Claude 会话的 Onboarding

新会话读 CLAUDE.md / WIP.md 后，遇到下列任一情景立即来读本 SOP：

| 情景 | 读哪节 |
|---|---|
| 用户问"现在版本是多少" | §1 |
| 用户问"下一个版本是什么" / "v0.X 之后做什么" | §8.5 |
| 即将 commit `feat:` / `fix:` 前缀 | §2 §5 |
| 改了 `01_specs/` 主体或字典 | §2 §3 §4 |
| 改了 `02_design/system_features.md` | §2 §3 §4 |
| 用户说 "bump" / "打 tag" / "迭代版本" | §3 §4 |
| pre-commit hook 输出"考虑 bump" 提醒 | §2 |
| 会话结束做一致性检查 | §10 |
| 不确定何时 bump | §0 速查卡 |

---

**END** — 版本管理 SOP
