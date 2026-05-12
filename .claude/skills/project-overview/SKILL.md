---
name: project-overview
description: DMSD 项目所有文件清单 + 每个文件干嘛 + 状态 + AC 价值（630+ 文件全包含）。⭐ 触发：itsuki / CC 想知道「X 文件干嘛 / 项目里有什么 X 类的文件 / 这个目录下有什么 / 找文件」时。新会话开始想了解项目结构也调本 skill。比 file-linkage skill 长（~650 行）— 因为要包含全部文件，触发频率应该低（itsuki 找文件时才用，不是 CC 改文件就用）。
when_to_use: ⭐ 触发 — 「X 文件在哪 / X 文件干嘛 / 项目里有 X 类文件吗 / X 目录下有什么 / 找文件 / 列文件 / 整理某类文件」/ 新会话想了解项目结构 / itsuki 主动 review 项目状态。**不要在 CC 改文件后自动调** — 那是 file-linkage skill 的活。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# DMSD 项目文件总览

> **作用 — 新会话理解项目的「入口文件」**：repo 里每个文件干嘛的、还在用没、什么状态、AC 价值如何 — 一份清单全包含。**新会话开始时读完本文件即可对项目有完整画面**，不需要再去单独看每个文件。
>
> **维护规则（2026-05-04 itsuki 拍板）**：
> 1. CC 每次**创建新文件 / 删除文件 / 大幅改动文件作用** → 当场同步更新本文件对应章节（不再开新审查文件）
> 2. 每次**版本 bump / sprint 收尾** → 整体 review 一次状态分布数字
> 3. **旧的"审查报告"模式已弃用** — 不再生成 `2026-XX-XX_xxx_审查.md` 这种带日期的快照文件
>
> **历史**：原文件 `2026-05-01_全文件审查.md` 由主会话切 7 组 + Explore agent 并行扫描 606 个 git-tracked 文件（venv / __pycache__ / DerivedData 已自动排除）后合成。**5-04 itsuki 拍板**升级为系统级单源真值文件，去掉日期前缀；**5-04 深夜 itsuki 二度拍板**整体迁入 skill 形态（`.claude/skills/project-overview/SKILL.md`）— 因为「不是给我看的，是给 CC 看的」 → skill 形态加载更高效。
>
> **和 `00_admin/文件结构指南.md` 关系**：那份偏「顶级目录骨架 + 权限速查」（静态参考，430 行）；本文件偏「每个文件状态 + 价值评估 + AC top 10」（动态总览，~650 行）。两份分工不同，本 skill 是**新会话首选入口**。
>
> **最后更新**：2026-05-13 早（接力 CC 26 文件大整理校准 — AC 12 文件迁 05_logs/AC_叙事/ §1.4；老文件 6 个归档 99_archive/2026-05-12_深夜大整理/ §1.5；管理文档 6 个散位 §1.5；iOS 2 个改名 _archived_ §5.1；NOT_YET_ALLOWED 错误码补；hooks 5 个 itsuki→kurekoduki + sync-rules 死链修；新增 §1.8 非编号目录说明）。早些更新：2026-05-12 凌晨（CC 自治大整理校准 — iOS Foundation 17→29 文件 / 1861→3512 行；AC 叙事 7→8 个含 v0.3.2；DESIGN_LOG 3→5 层加 Android + 点呼机）；2026-05-06（独立 repo 模式退役）；2026-05-04 深夜（迁入 skill 形态）

**最后扫描真值**：2026-05-13 早 接力 CC 整理后用 Read + Bash 全 repo 真实 ls 验证（含非编号目录 / .gitignore 排除项）。下次大整理时更新本字段。

---

## 0. 摘要

### 0.1 体量

| 顶级目录 | 文件数 | 占比 | 主要内容 |
|---|---|---|---|
| `03_dev/` | 407 | 67% | 代码 + 设计 LOG（teacher_web vendor + 字体占大头） |
| `99_archive/` | 109 | 18% | 归档物（早期 GPT 对话 / throwaway iOS / demo 4-28） |
| `00_admin/` | 33 | 5% | 管理文档 / AC 叙事 / hooks / 术语表 |
| `05_logs/` | 32 | 5% | raw / dev_log / problem_solving / meta |
| `01_specs/` | 13 | 2% | 规格冻结区（含 5 .pages 不可读） |
| `02_design/` | 4 | 0.7% | 硬件 + 流程 + system_features + 巴士时刻 |
| `06_assets/` + `bin/` + 根 | 9 | 1.5% | logo / 真实样本 / 同步脚本 / 顶层 5 |
| **总计** | **606** | 100% | |

### 0.2 状态分布

| 状态 | 数量 | 占比 |
|---|---|---|
| ✅ active（仍在更新或被引用） | ~155 | 26% |
| 📦 archived（任务结束保留作参考） | ~395 | 65%（含 268 vendor 字体） |
| ⚠️ stale（内容过期或冗余复制） | ~25 | 4% |
| ❓ 不可读（.pages / .docx / 二进制 PDF dump） | ~31 | 5% |

> 注：teacher_web 的 268 vendor 字体严格说"在用"（HTML 实际加载），但都是第三方资源，价值上当成 archived 处理。

### 0.3 五条关键发现

1. **`teacher_web/demo/` 和 `teacher_web/v1/` 100% 完全相同**（13 个 jsx + 全部 vendor + 字体的 MD5 全部匹配）。v1 是 4-30 从 demo 整体复制后**没有任何改动**。预期之内（v1.0 启动起点），但启动改动时要小心 git 分叉。

2. **5 个 .pages 原稿** + **2 个 .docx** 都已经被对应的 .md 取代，但原稿没清理。CC 永远读不出内容，留着只占空间。

3. **`progress_overview.md` 和 draft 错位 11 天没合并**（4-20 起草、5-1 仍未合）— 教授看 GitHub 时"做到哪了"的信息陈旧。

4. **后端 v1 P0 已完成 70%**（出寮届 / 食堂 Excel / SendGrid / 认证全跑通），但**点呼 / 学习 / 役职审批**三块路由完全缺，需后续 P1 会话补。

5. **iOS Foundation 层已冻结成熟**（17 文件 1861 行），3 个核心 Feature（Auth/Home/Community 共 5K+ 行）已真实装；Apply / MyPage v2 待 Agent D/E。**整体结构远比 4-28 demo 完成度高**。

### 0.4 跨组横向洞察（详见 §8）

- **demo ↔ v1 复制策略**（2026-05-06 独立 repo 模式退役后）：backend 选了"重写"（schema 全新）✅；teacher_web 选了"复制不动"⏳；iOS / Android 真代码全部在 DMSD 内（曾经的独立 repo + cloud agent 同步三件套已归档到 `99_archive/2026-05-06_cloud_agent_退役/`）。
- **五层 DESIGN_LOG 体系生效**：BACKEND / IOS / ANDROID / WEB 四端 DESIGN_LOG 都活跃且与 system_features.md 同步链清晰；2026-05-08 加点呼机 ROLLCALL_DEVICE_DESIGN_LOG 成第 5 个 — 是 4-29 大整理后的最大资产，5-08 收口。
- **AC 叙事供应充足**：80+ 条 #AC候选 + 6 个 per-version 叙事（v0.3-0.7）+ 4 个 problem_solving 精品版 + 3 个 03_dev/_DESIGN_LOG 工程化叙事 — 数量上远超 AC 自我推荐书所需。

---

## 1. 第 1 组：根目录 + 00_admin（37 文件）

**统计**：✅ 22 / 📦 7 / ⚠️ 3 / ❓ 4

### 1.1 根目录（5 文件）

| 文件 | 作用 | 状态 | 备注 |
|---|---|---|---|
| `.gitignore` | git 忽略规则（Python / Node / Android / IDE / 数据库本地） | ✅ | 当前完整 |
| `CLAUDE.md` | AI 项目指令权威源（每会话必读） | ✅ | 4-30 沟通规则 #6 升级 |
| `CHANGELOG.md` | 18 tag 全程 + 版本号单源真值 | ✅ | 教授会看 |
| `README.md` | 项目对外介绍（4-30 名字 Tomoshibi 定名） | ✅ | 4-29 起 GitHub public |
| `LICENSE` | All Rights Reserved + AC 后 4 方向评估 | ✅ | 不常改 |

### 1.2 00_admin/AI 协作 + 项目治理（7 文件）

| 文件 | 作用 | 状态 |
|---|---|---|
| `文件结构指南.md` | 所有文件清单 + 反向索引 | ✅（轻微滞后，本文已对照补） |
| `文档同步点清单.md` | 单源真值表 / 5 AC 核心问题 / 分阶段策略 | ✅ |
| ~~`版本管理SOP.md`~~ | 2026-05-04 整体迁入 `.claude/skills/version-bump/SKILL.md` | 📦 已归档到 `99_archive/2026-05-04_版本管理SOP_迁入skill/` |
| `版本演变一览.md` | 18 tag 故事线 | ✅ |
| `2026-04-19_项目审查_backlog.md` | 87 条漏洞清单（已大量 close） | 📦 |
| `漏洞_剩余清单_2026-04-21.md` | 28 条剩余精简索引 | ✅ |
| `v0.4.0_S系列spec漏洞优先级分析.md` | 已被"漏洞_剩余清单"吸收 | 📦 可清理 |

### 1.3 00_admin/会话状态（3 文件 — 2026-05-13 progress_draft 归档）

| 文件 | 状态 | 备注 |
|---|---|---|
| `WIP.md` | ✅ | 多会话协调枢纽 |
| `TODO.md` | ✅ | 三轨 A/B/C 推进中 |
| `progress_overview.md` | ⚠️ | 5-04 正文已更新到 v0.8 但 5-12 又过期 8 天 |
| ~~`progress_overview_draft_2026-04-20.md`~~ | 📦 已归档 → `99_archive/2026-05-12_深夜大整理/`（2026-05-13 commit 81842f4 — draft 反向过时：4-20 draft < 5-04 正文） |

### 1.4 05_logs/AC_叙事/（12 文件 — **2026-05-13 commit b37d065 从 00_admin/ 迁入**，Q3 拍板）

| 文件（现路径 `05_logs/AC_叙事/`） | 状态 | 价值 |
|---|---|---|
| `v0.3.0_AC叙事.md` ~ `v0.8.0_AC叙事.md`（8 个含 v0.3.2） | ✅ | 完整 8 版本素材链。**5-04 起新规则**：itsuki 自己写不主动起草，历史 v0.3-v0.8 的 7 个是 CC 起草保持不动 |
| `面试准备_索引.md` | ✅ | 6 大类 42+ 题清单（题目占位，回答留 iCloud） |
| `原创设计_语音播报防作弊.md` | ✅ | ⭐ AC 最强素材之一 |
| `AC_志望動機_素材.md` | ⚠️ | 框架完整 / 内容 0/8 留白等 itsuki 自填 |
| `AC_提交_checklist.md` | ⚠️ | 5-10 月 6 个 gate 倒计时 + 月度 review 工作流 |
| `Batch3_itsuki手笔素材指引.md` | 📦 | 4 个 ready-to-paste draft 等 itsuki 合并（30-45min 工作量） |

### 1.5 00_admin/v0.4.0 spec draft + 管理文档（**2026-05-13 commit 81842f4 全分散到 7 个目的地**）

| 文件 → 新位置 | 状态 | 备注 |
|---|---|---|
| `v0.4.0_Device_Contract骨架.md` → `99_archive/2026-05-12_深夜大整理/` | 📦 已归档 | 已融入 BACKEND_DESIGN_LOG |
| `v0.4.0_S2_S3_字段draft.md` → `99_archive/2026-05-12_深夜大整理/` | 📦 已归档 | 已融入 FIELD_REGISTRY |
| `v0.4.0_S系列spec漏洞优先级分析.md` → `99_archive/2026-05-12_深夜大整理/` | 📦 已归档 | 已被「漏洞_剩余清单」吸收 |
| `T2_iOS归档_dryrun评估.md` → `99_archive/2026-05-12_深夜大整理/` | 📦 已归档 | 已执行 |
| `跨会话_ios_共享决策.md` → `99_archive/2026-05-12_深夜大整理/` | 📦 已归档 | 5-06 退役独立 repo 后失效 |
| `wifi_survey_howto.md` → `04_ops/` | ✅ | 等 itsuki 实地调研 |
| `MAC_MINI_SETUP.md` → `04_ops/` | ✅ | Mac mini 部署 SOP（previously 漏列）|
| `漏洞_剩余清单_2026-04-21.md` → `05_logs/` | ✅ | 28 条剩余漏洞索引（previously 在 §1.2）|
| `版本演变一览.md` → `05_logs/` | ✅ | 18 tag 故事线（previously 在 §1.2）|
| `术语表.html` → `06_assets/` | ✅ | itsuki AC 面试准备 — 180+ 词术语学习工具 |
| `create_local_dev_symlink.sh` → `bin/` | ✅ | VPS 已停用但脚本保留参考 |

### 1.6 00_admin/hooks（10 hook + 1 库 + README — **2026-05-13 校准**）

| 文件 | 状态 | 备注 |
|---|---|---|
| `install.sh` | ✅ | 首次 clone 后跑一次（`git config core.hooksPath`）|
| `pre-commit` | ✅ | git commit 前 3 件事：版本号一致性 + bump 提醒 + 联动检查 |
| `post-commit` | ✅ | git post-commit — graphify AST 增量重建（**2026-05-11 加**）|
| `post-checkout` | ✅ | git post-checkout — graphify 切分支后重建（**2026-05-11 加**）|
| `post-edit-sync-check.sh` | ✅ | CC PostToolUse — 联动检查 + demo scaffold 字眼检测（2026-05-04 加）|
| `post-edit-memory-check.sh` | ✅ | CC PostToolUse — memory dir 改完提醒补 MEMORY.md 索引（2026-05-04 加 / **2026-05-13 hardcode 路径 itsuki→kurekoduki 修复 hook 复活**）|
| `post-edit-japanese-comment-check.sh` | ✅ | CC PostToolUse — 代码注释日语 hiragana/katakana 扫描（中文铁律，2026-05-04 凌晨加）|
| `post-edit-timestamp-check.sh` | ✅ | CC PostToolUse — 声明性文件「最后更新」时间戳是否同步今天（2026-05-04 凌晨加）|
| `post-edit-version-hardcode-check.sh` | ✅ | CC PostToolUse — 版本号硬编码实时拦（比 pre-commit 早一步，2026-05-04 凌晨加）|
| `post-edit-project-overview-check.sh` | ✅ | CC PostToolUse — **project-overview SKILL.md 同步检查**（**2026-05-13 itsuki 怒怼后加** — 改结构相关文件 → 提醒同步 project-overview / 防"加文件没补 / 删文件没去 / 描述漂移"）|
| `pre-bash-destructive-block.sh` | ✅ warn 模式 | CC PreToolUse — 拦 rm -rf 非临时 / git push --force / git branch -D（2026-05-04 加 / **2026-05-12 改 warn 模式不阻断**）|
| `lib/sync-rules.sh` | ✅ | **21 条**联动规则代码化（**2026-05-08 从 13→18 加 6 条反向 Rule 14-19；2026-05-13 audit 验证为实际 21 条 add_rule** — 5-08 后又加 3 条 / CLAUDE.md 仍写"17 条"待校准）+ demo-scaffold-detect 函数 + `00_admin/版本管理SOP.md` 引用 **2026-05-13 改 version-bump skill**（commit 859693e）|
| `README.md` | ✅ | hooks 总说明（git pre-commit + git post-commit/checkout + **CC PostToolUse 6** + CC PreToolUse 1 = **3 类**全覆盖）|

### 1.7 .claude/skills（7 skill）

| skill | 状态 | 触发 / 用途 |
|---|---|---|
| `session-wrap/` | ✅ | 「收尾 / 整理今天」AC 素材全量扫描 dump + git 状态收尾确认（§5.5.9）|
| `version-bump/` | ✅ | 「迭代 / bump / 发版本 / 发版」版本决策树（CC 有否决权）+ §13 发版动作 SOP |
| `file-linkage/` | ✅ | 「联动 / 改 A 要查 B」联动矩阵 13 条 |
| `project-overview/` | ✅ | 本 skill — 文件总览（itsuki 找文件时调）|
| `memory-write/` | ✅ | 「记一下规则 / 以后这样」memory 写入 SOP（2026-05-04 加）|
| `new-feature/` | ✅ | 「新功能 X / 加 Y」4 端实装模板 + 字段对齐自检（2026-05-04 加）|
| `spec-sync/` | ✅ | 「跨端检查 / 字段对齐」字段提取对比 — 大改后 / v1.0 前用一次（2026-05-04 加）|

> **2026-05-04 调整记录**：原计划 10 skill，itsuki 反问后砍 3：
> - `session-start` 删（内容并入 `session-wrap §5.5.9` 收尾段；启动只读 WIP）
> - `demo-clean` 删（一次性任务做 skill 频次太低；改成 `lib/sync-rules.sh` demo-scaffold-detect 自动检测 + `system_features.md` 末尾清单）
> - `release-checklist` 删（合并到 `version-bump §13`；本来就串联，分两个 skill 反而割裂）

---

### 1.8 主目录非编号目录 + 隐藏文件（**2026-05-13 itsuki 反馈后新增**）

> **背景**：itsuki 5-13 反映"docs 没编号为啥在主目录"。本节列清楚所有非编号目录 / 隐藏文件 — 为啥它们不归编号目录 + 哪些进 git / 哪些 .gitignore 排除。

#### 1.8.1 进 git 的非编号目录（3 个）

| 目录 | 文件数 | 为啥不编号 | 备注 |
|---|---|---|---|
| `.claude/` | 23 | Claude Code 配置 — 跨项目共享惯例（`.claude/skills/` / `.claude/settings.json` / `.claude/scheduled_tasks.lock`）| `.claude/sessions/` + `.claude/settings.local.json` .gitignore 排除 |
| `bin/` | 2 | 可执行脚本 — Unix 惯例 | `bin/sync-check.sh`（联动检查工具）+ `bin/create_local_dev_symlink.sh`（5-13 从 00_admin/ 迁入）|
| `docs/` | 3 | **外部 skill 适配配置 — Matt Pocock 套件读这里**：`docs/agents/{issue-tracker,triage-labels,domain}.md`（详见 `CLAUDE.md §Agent skills`）| ⚠️ **不是 itsuki 看的文档**（DMSD 自己的文档全在编号目录 00-99）— 给外部 skill 读 |

#### 1.8.2 .gitignore 排除的非编号目录（git 看不到 / GitHub 看不到 / 教授看不到）

| 目录 | 用途 | 来源 |
|---|---|---|
| `.git/` | git 内部 | 永远 |
| `.beads/` | graphify hook install 残留（hook 已 copy 到 `00_admin/hooks/`，详见 `hooks/README.md ⚠️` 段）| 2026-05-11 graphify install |
| `.scratch/` | Matt Pocock `to-prd` 中间产物（PRD 进 TODO.md 后即弃）| Matt Pocock skill |
| `graphify-out/` | graphify 知识图谱产物（82M+ 临时文件）| 5-11 install graphify |
| `.swiftpm/` / `.venv/` / `node_modules/` / `__pycache__/` 等 | 语言生态自动建 | 各语言工具链 |
| `**/.DS_Store` | macOS 元数据 | macOS Finder |

#### 1.8.3 主目录顶层文件（6 项）

| 文件 | 用途 |
|---|---|
| `CHANGELOG.md` | 版本号单源真值（教授会看）|
| `CLAUDE.md` | AI 项目指令权威源（每会话必读）|
| `README.md` | 项目对外介绍（GitHub public，教授会看）|
| `LICENSE` | All Rights Reserved + AC 后 4 方向评估 |
| `.gitignore` | git 忽略规则（含上面所有 .gitignore 排除项）|
| `.graphifyignore` | graphify 忽略规则（防 vendor 字体污染图谱）|

#### 1.8.4 关键 takeaway（itsuki 关注的）

1. **"我 ls 看到非编号目录乱"真相** = 物理文件存在但大部分 .gitignore 排除（`.beads/ / .scratch/ / graphify-out/ / .DS_Store / .venv/`）→ git 看不到 / GitHub 看不到 / 教授看不到
2. **真进 git 的非编号目录只有 3 个**：`.claude/`（CC 配置）/ `bin/`（脚本）/ `docs/`（外部 skill 配置）— 都是工具类，按惯例不编号
3. **docs/ 不是 itsuki 看的** — DMSD 自己的文档全在编号目录（00-99），docs/ 是给 Matt Pocock skill 读的

---

## 2. 第 2 组：01_specs + 02_design（17 文件）

**统计**：✅ 11 / 📦 0 / ⚠️ 1 / ❓ 5（全是 .pages）

### 2.1 01_specs/ 顶级（5 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `v0.1完整计划.pdf` | ✅ | PDF 可读，10 部规划完整 |
| `API_Contract_v0.1.pages` | ❓ | 已被 `API_CONVENTIONS.md` 取代 |
| `API_CONVENTIONS.md` | ✅ | 4-22 修订 8 处（URL 路由 / HTTP 动词 / 错误码） |
| `IA_UI_v0.1.pages` | ❓ | 已被 `v0.1完整计划.pdf §3` + `system_features.md §7` 覆盖 |
| `Overview_of_Features_v0.1.pages` | ❓ | 已被 `system_features.md`（4-30 重写 357→830 行）取代 |

### 2.2 01_specs/rollcall/（7 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `RollCall_Spec.md` | ✅ | v0.3.0 主体，4-29 修订 5 处（§4.2 / §5.2 / §5.4 / §5.5 / §5.6） |
| `RollCall_Spec_v0.1.pages` | ❓ | 已被 .md 替代，无价值 |
| `ENUM_REGISTRY.md` | ✅ | 15 种枚举 |
| `FIELD_REGISTRY.md` | ✅ | 字段 + 禁止字段（4-22 增补） |
| `DEVICE_REGISTRY.md` | ✅ | device_retired_at 永久注销字段 |
| `ERROR_CODES.md` | ✅ | 12 个错误码（与 API_CONVENTIONS 对齐） |
| `DMSDv0.1验收脚本.pages` | ❓ | 不知是否与 PDF §1.2 完全相同，需 itsuki 决定 |
| `v0.1_冻结决策.md` | ⚠️ | 4-29 阈值再冻结后 ~10 处文档已修，但本文角色（备份 vs 历史快照）需明确 |

### 2.3 02_design/（3 文件 — 2026-05-08 bus_schedule_real.md 挪到 06_assets/）

| 文件 | 状态 | 备注 |
|---|---|---|
| `system_features.md` | ✅ | ⭐ 5 端共用真値（iOS / Android / 后端 / teacher_web / 点呼机），4-30 轨道 ABC 同日完成（覆盖老师 38 条） |
| `hardware_design.md` | ✅ | Pi 3A+ 选型 + 砍 Pi 4B 论证（AC 素材）— 跟 03_dev/rollcall_device/ 软件层互补 |
| `flow_design.md` | ✅ | 路径 A 卡 / 路径 B iOS / 路径 B Android |

---

## 3. 第 3 组：03_dev/backend（35 文件）

**统计**：✅ 22（v1）+ 11（demo 锁定也算 active 算 archive 看法）+ ⚠️ 1 + ❓ 1
**核心**：v1 P0 完成约 70%；demo 11 文件锁定无修改

### 3.1 backend 顶层 + demo（13 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `backend/README.md` | ✅ | demo/v1 分工说明 |
| `backend/BACKEND_DESIGN_LOG.md` | ✅ | ⭐ 12 章设计权威源（D1-D12 决策清单） |
| `backend/demo/`（10 文件）| 📦 | 4-28 demo skeleton，全部锁定不动；`db_schema.sql` 价值最低（v1 改用 SQLAlchemy declarative） |

### 3.2 backend/v1/ 配置层（5 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `.env.example` | ✅ | 35 个环境变量（DB / JWT / SendGrid / CORS） |
| `requirements.txt` | ✅ | 14 个依赖（含 sendgrid / openpyxl / pytest / psycopg） |
| `README.md` | ✅ | 5 步启动 + 烟雾测试 |
| `seed.py` | ✅ | 教师 8 角色 + 班主任 + 学生 2 人（含留学生） |
| `.gitignore` | ✅ | 保护 .env / venv |

### 3.3 backend/v1/app/ 核心（9 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` / `database.py` / `deps.py` / `security.py` / `main.py` / `config.py` | ✅ | 范式标准 |
| `models.py` | ⚠️ | 13 张表已建（含 P1/P2 的 RollCallSession / RollCallEvent / StudyCheckin），但**对应 router 缺**；建议在 docstring 标 P0/P1/P2 |
| `schemas.py` | ✅ | discriminated union 实装 |

### 3.4 backend/v1/app/routers/（**11 文件 — 2026-05-13 audit 补 6 漏**）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` | ✅ | 空包声明 |
| `auth.py` | ✅ | P0 完整（学生 + 教师 + JWT） |
| `applications.py` | ⚠️ | **P0 70%** — 学生提交/邮件/履历/详情 ✅，**缺 #10-#13 役职审批 endpoint** |
| `meals.py` | ✅ | P0 完整（JSON + Excel openpyxl） |
| `notifications.py` | ✅ | SendGrid 烟雾测试 |
| `accounts.py` | ✅ | 5-04 启 — 学生注册（POST /accounts）+ 密码重置 / DELETE /accounts/me 待补（Apple 5.1.1(v)）|
| `admin_registration_code.py` | ✅ | 5-03 启 — POST /refresh + GET /current + GET /history（注册码门禁）|
| `announcements.py` | ✅ | 5-03 启 — 老师公告 9 endpoints（list / detail / replies / reads）|
| `rollcall.py` | ⚠️ | **5-12 04:55 commit 96f86eb 已挂载** — 但 NFC card_uid 防作弊核心未真接（rollcall.py:145-153 暫定，深度审查 P0）|
| `study.py` | ⚠️ | **5-12 04:55 commit 96f86eb 已挂载** — 学習 NFC 3 tap 状态机 + 欠席届 + 出席统计 |
| `teachers.py` | ✅ | 教师管理 + 邀请 token（5-03 启）|

### 3.5 backend/v1/app/services/（4 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` / `meals.py` | ✅ | meals.py P0 完整 |
| `approval_chain.py` | ⚠️ | 外泊 chain 证据确定 ✅；**帰省 / 帰国 chain 是 PROVISIONAL 暫定值**（待 itsuki 老师见面补 4 张实物表） |
| `email.py` | ⚠️ | 90% 完整，**缺 retry 3 次循环**（设计要求） |

### 3.6 backend/v1/tests/（**5 文件 — 2026-05-13 audit 校准**）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` + `conftest.py` | ✅ | 标准 fixture |
| `test_smoke.py` | ✅ | 17 个 test case — P0 关键路径 |
| `test_announcements.py` | ✅ | 公告 endpoint test（5-03 + 启）|
| `test_demo_reviewer.py` | ✅ | reviewer demo 账号 test（5-08 拍板）|
| `test_registration_code.py` | ✅ | 注册码 5-03 启 — 测 /refresh / /current / /history |

**实际 42 test case** — 覆盖率 35-45%（远低于 BACKEND_DESIGN_LOG §8 要求 70% — 5-12 深度审查 P1 发现）。

### 3.7 v1 P0 缺块清单（**2026-05-13 audit 校准 — #2 #3 已完成**）

需后续 P1 会话补：
1. `routers/applications.py` 加 `POST /{id}/approvals`（#10-#13 役职审批）+ `DELETE /{id}`（D3 撤回）
2. ~~新建 `routers/rollcall.py`~~ → ✅ **5-12 commit 96f86eb 已挂载**（但 NFC card_uid 防作弊核心未真接 — 见 §3.4 ⚠️ + 深度审查 P0）
3. ~~新建 `routers/study.py`~~ → ✅ **5-12 commit 96f86eb 已挂载**
4. `services/email.py` 补 retry 3 次
5. **`routers/accounts.py` 加 DELETE /accounts/me**（5-13 audit 新发现 — Apple 5.1.1(v) 强制要求 / BACKEND_DESIGN_LOG §5.1.6 已 spec）
6. **NFC card_uid 全栈实装**（5-13 audit / backend codex full audit 重点）— Student.card_uid 字段 + cards 表 + alembic migration + UNIQUE INDEX + admin_cards.py 路由

---

## 4. 第 4 组：03_dev/teacher_web（314 文件，46 真代码 + 268 vendor）

**统计**：✅ 17 / 📦 25 / ⚠️ 2 + 268 vendor / ❓ 2
**核心发现**：**demo 和 v1 100% 完全相同**（v1 是 4-30 整体复制后未改动，符合预期"复制起点"策略）

### 4.1 顶层（2 文件）

| 文件 | 状态 |
|---|---|
| `DESIGN_BRIEF.md` | ✅ — Round 2/3 handoff + 实装跟踪 |
| `WEB_DESIGN_LOG.md` | ✅ — ⭐ 完整设计决策归档（18 项时间线 + Tomoshibi 命名 + Ryo 涼配色） |

### 4.2 demo/（159 文件 = 8 根 + 15 src + 134 vendor / 字体 / icon + 2 同名子）

| 文件类 | 状态 | 备注 |
|---|---|---|
| `Tomoshibi_v3_single.html`（32MB 单文件）| 📦 | demo day U 盘携带用，v1 不需要 → **可删** |
| `build_single_file.py` / `rebuild.command` / `打包单文件.command` | 📦 | 单文件打包链，v1 改 server-render 后过期 → **可删** |
| `demo_server.py` | 📦 | mock 后端（/checkin / /events/latest / /api/server-info），v1 改真 FastAPI；架构思路保留参考 |
| `tomoshibi`（无后缀 CLI） | 📦 | 7 子命令的 bash 工具，质量高；v1 架构改了过期 |
| `开发模式跑.command` | 📦 | demo 一键启动 |
| `NFC_DEMO_SETUP.md` | 📦 | demo day 现场说明书（iPhone Shortcuts NFC 流程），AC 素材 |
| `src/index.html` | ✅ | 主入口（HTML + 字体 CSS + inline jsx + React/Babel CDN） |
| `src/components/*.jsx`（14 文件）| ✅ | 13 真组件 + theme + accounts；理解架构的核心 |
| `src/{vendor,_assets,assets}/`（134 文件）| 📦 | React + Babel + Noto Sans JP / JetBrains Mono 130 woff2 + 1 icon = 9.9MB |

### 4.3 v1/（155 文件 = 7 根 + 14 src + 134 vendor）

| 文件 | 状态 | 备注 |
|---|---|---|
| `README.md` | ⚠️ | 启动条件清单（4-29 写）但还没启动；v1.0 开工前要 review |
| 其他全部 7+14+134 | ⚠️ | **MD5 100% 与 demo 相同**，未做任何改动 |

**v1.0 启动建议清单**（按顺序）：
1. 删 demo 复用的 build/single-file 脚本（v1 不用）
2. 改 `theme.jsx`：删 ACCOUNTS / TEACHERS / ROSTER seed 改 fetch API
3. 改 `shell.jsx`：5 角色不同菜单（NAV 数组 role-based filter）
4. 改 `login.jsx`：删 teacher/1234 硬编码改真认证
5. 改 `live-roll-call.jsx`：/events/latest poll 换 WebSocket
6. 改 `app.jsx`：state 初始化改 fetch API
7. 补充 Tier 1 剩余页面（外泊 / 帰省 / 帰国 / records / search / 健康申报 / 请假流程）

---

## 5. 第 5 组：03_dev/student_ios + student_android + rollcall_device + LATEST.md（54 + 56 + 8 文件）

**统计**：✅ 31 / 📦 4 / ⚠️ 6 / ❓/⏳ 13
**核心发现**：Foundation 层已冻结成熟（17 文件 1861 行）；3 个 Feature 已真实装；Apply / MyPage 待 Agent D/E

### 5.1 顶层 + demo（8 文件）

| 文件 | 状态 |
|---|---|
| `03_dev/LATEST.md` | ✅ — 最新原型位置指针 |
| `student_ios/README.md` | ✅ — 目录说明 |
| `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` | 📦 — **2026-05-13 commit 81842f4 已从 DESIGN_BRIEF.md 改名**（IOS_DESIGN_LOG 全覆盖）|
| `student_ios/IOS_DESIGN_LOG.md` | ✅ — ⭐ §1-11 完整决策权威源 |
| `demo/.gitignore` | ✅ |
| `demo/QA_Round1_PhaseB.md` | ✅ — Claude Design Phase B 静态扫描报告 |
| `demo/_archived_Round2_Prompt_draft.md` | 📦 — **2026-05-13 commit 81842f4 已从 Round2_Prompt_C3.md 改名**（C3 已 resolve）|
| `demo/Tomoshibi_iOS_PhaseB_v2.html` | 📦 — Phase B 完整原型（锁定不动） |

### 5.2 v1/ 顶层管理（3 文件 — 2026-05-06 退役 cloud agent 模式后精简）

| 文件 | 状态 | 备注 |
|---|---|---|
| `.gitignore` / `README.md` / `project.yml`（xcodegen）/ `BUILD.md` | ✅ | 常规 |

> **2026-05-06 归档**：STATUS / SHARED_DECISIONS / SESSION_CHANGELOG / REMOTE_AGENT_GUIDE 4 个 cloud agent 元数据文件已 git mv 到 `99_archive/2026-05-06_cloud_agent_退役/`（独立 repo 模式退役 — itsuki 决定不用 cloud agent，保留这 4 文件无意义）。

### 5.3 v1/TASKS/（3 文件）

`TASK_C_COMMUNITY.md` / `TASK_D_APPLY.md` / `TASK_E_MYPAGE.md` 都 ✅ — Agent dispatch 任务卡。和 IOS_DESIGN_LOG 分工：LOG 是设计决策权威，TASK 是实装 checklist，零重合。

### 5.4 v1/Xcode 项目结构 + Assets（7 文件）

`project.pbxproj`（27KB 机器生成）+ `contents.xcworkspacedata` + 5 个 Assets.xcassets 元数据/icon = ✅。**STATUS.md 提到 Assets 暂因 SDK 冲突移除**，需要 4-23 后澄清现状。

### 5.5 v1/Features/（8 个 *Stubs.swift）

| 文件 | 行数 | 真实状态 |
|---|---|---|
| `Auth/AuthStubs.swift` | 1661 | ✅ **完成**（10 个 Auth view 真实装，1:1 JSX fidelity） |
| `Home/HomeStubs.swift` | 1705 | ✅ **完成**（6 页 Home + 4-state RollcallSheet money shot 动画） |
| `Community/CommunityStubs.swift` | 1820 | ✅ **完成**（18 view 必做 8 + stub 10） |
| `Apply/ApplyStubs.swift` | 1785 | ⏳ 文件存在但状态不明，**待 Agent D v2** |
| `MyPage/MyPageStubs.swift` | 1521 | ⏳ Landing 实装，其余 13 页 stub，**待 Agent E v2** |
| `Schedule/ScheduleStubs.swift` | 338 | ❌ 纯 stub，已并入 Home Community → **可删** |
| `StayList/StayListStubs.swift` | 748 | ❌ 纯 stub，已并入 Apply → **可删或 redirect** |
| `BusList/BusListStubs.swift` | 330 | ❌ 纯 stub，已并入 Community Bus card → **可删** |

### 5.6 v1/Foundation/（17 文件）+ Root/（3 文件）

全部 ✅ frozen — AppState 2 / Components 12 / LiquidGlass 3 / Routing 2 / Seed 2 / Theme 1 + RootView + GlobalOverlays + TomoshibiApp 入口。1861 行专业级代码。

### 5.7 03_dev/student_android/（Android 第 4 端,2026-05-06 合并回 DMSD,~56 文件）

> **背景**：2026-05-02 itsuki 拍板 v1.0 直接 iOS + Android 双端上线,Android 用 Kotlin + Jetpack Compose + Material 3 从 Claude Design 22 屏 standalone HTML 逐屏对译。原独立 repo `Tomoshibi-Android` 5-06 退役合并回 DMSD（详见 §8.1 退役 cloud agent 模式）。

| 文件类 | 数 | 状态 | 备注 |
|---|---|---|---|
| `ANDROID_DESIGN_LOG.md` | 1 | ✅ | ⭐ 完整设计权威源 — 2026-05-02 建,22 屏 route registry + Compose 翻译规则 + Phase 计划 |
| `v1/` Gradle 配置（7 文件）| 7 | ✅ | `build.gradle.kts` × 2 + `settings.gradle.kts` + `gradle.properties` + `libs.versions.toml` + wrapper 配置 |
| `v1/app/AndroidManifest.xml` + `res/`（8 文件）| 9 | ✅ | manifest + drawable + values × 3 + xml × 2 + mipmap × 2 |
| `v1/app/.../{TomoshibiApp,MainActivity}.kt` | 2 | ✅ | 应用入口（@HiltAndroidApp / @AndroidEntryPoint）|
| `v1/app/.../nav/`（Routes + NavGraph）| 2 | ✅ | 22 屏路由声明（对称 iOS Route.swift + RootView.swift）|
| `v1/app/.../data/`（store + seed + model）| 3 | ✅ | AppStore（CompositionLocal 全局状态）+ MockData seed + Models domain types |
| `v1/app/.../ui/components/`（5 文件）| 5 | ✅ | TopRollBar / GlobalScaffold / BottomTabs / RollCallSheet / HomeCards |
| `v1/app/.../ui/theme/`（4 文件）| 4 | ✅ | Color / Theme / Tokens / Type — Material 3 主题层 |
| `v1/app/.../ui/icons/SuzuIcons.kt` | 1 | ✅ | Tomoshibi 自定义图标 |
| `v1/app/.../ui/screens/`（22 屏）| 22 | ✅ | splash / welcome / onboarding / login / home / rollcall / applications × 3（list / detail / new）/ mypage × 2 / nfc / deduction / account / community × 7（schedule / bus / delivery / feedback / lostfound / music / study）/ notifications × 2 |
| `v1/app/src/{androidTest,test}/`（2 文件）| 2 | ✅ | ExampleInstrumentedTest + ExampleUnitTest（脚手架,未真实装）|

**核心发现**：
- 22 屏目标 ✅ 全部到位（design 蓝图与代码 1:1）
- 包名 `jp.tomoshibi.android` — Tomoshibi 命名跟 iOS / 后端一致
- 跟 iOS 的对应：`screens/` ≈ iOS `Features/Stubs.swift`,`components/` ≈ `Foundation/`,`nav/` ≈ `Foundation/Routing/`
- **真后端接入未做** — 当前是 MockData seed,backend v1 上线后改 fetch API（同 iOS,见 §3.7 backend P0 缺块）

**与 system_features.md / spec 的对齐状态**：
- ⏳ 未做 spec-sync 跨端字段对齐检查（spec-sync skill 价值在 backend 上线后跑）
- 22 屏 vs system_features §7 14 子节功能矩阵 — 视觉层覆盖 ✅,业务规则层（扣分阈值 / 时间窗 / 役职链）待 backend 接通后实战验证

### 5.8 03_dev/rollcall_device/（点呼机第 5 端,2026-05-08 建骨架,~8 文件）

> **背景**：2026-05-08 itsuki 拍板「点呼机当第 5 端」(对称 backend / iOS / Android / teacher_web 4 端模式) — 跑在 Raspberry Pi 3A+ 上的 Python 程序,读 NTAG215 学生卡 + 写 ST25DV16K 动态贴纸 + LED 反馈 + 日语播报。物理硬件层在 `02_design/hardware_design.md`,本目录是软件层。

| 文件 | 状态 | 备注 |
|---|---|---|
| `README.md` | ✅ 骨架 | 目录说明 + 上下游 + 启动指引 |
| `ROLLCALL_DEVICE_DESIGN_LOG.md` | ✅ 骨架（11 章纲）| ⭐ 软件设计权威源 — §1 技术栈 / §2 GPIO 接线 / §3 主循环 / §4 模块 / §5 systemd / §8 已知坑 / §10 待 itsuki 拍板 6 个 D1-D6 |
| `requirements.txt` | ✅ 骨架（注释列依赖待选）| Adafruit-PN532 / smbus2 / gpiozero / httpx 等候选 |
| `src/main.py` | ⏳ 占位 | 实装时填主循环（IDLE → SUBMITTING → SUCCESS / FAIL → IDLE 状态机）|
| `src/{nfc,audio,led,api}/__init__.py` | ⏳ 占位 | 4 个空模块包 — 实装时分别写 PN532 / TTS / LED / 后端客户端 |
| `config/.gitkeep` + `docs/.gitkeep` | ⏳ 占位 | systemd unit / 部署 SOP / 接线图 待写 |

**v1.0 实装顺序建议**（按 ROLLCALL_DEVICE_DESIGN_LOG §10 拍板后）：
1. itsuki 拍板 D1-D6（NFC 库 / ST25DV 驱动方案 / TTS 方案 / SPI 还是 I2C / WebSocket 还是 HTTP / 设备认证）
2. Pi 装系统 + SSH + 配件实物到货
3. 写 nfc/pn532.py（读 NTAG215 卡 UID）
4. 写 led/led.py（GPIO 状态机）
5. 写 api/client.py（调 backend POST /checkin）
6. 串起 main.py 主循环
7. 写 nfc/st25dv.py（自写 I2C 驱动 — 1-2 周学习成本）
8. 写 audio/player.py
9. 写 systemd unit + 开机自启
10. 部署到真宿舍点呼

---

## 6. 第 6 组：05_logs + 06_assets + bin（36 文件）

**统计**：✅ 24 / 📦 2 / ⚠️ 10
**核心发现**：raw 04-12 ~ 04-30 高频产出（13 份）；80+ 条 #AC候选；4 篇 problem_solving 全集中于 4-10/4-15

### 6.1 05_logs/ 根级 meta（3 文件）

| 文件 | 状态 | AC 核心问题映射 |
|---|---|---|
| `decision_log.md` | ✅ | 6 条版本级决策（最后更新 4-20，"事后回看"占位待补） |
| `learning_path.md` | ✅ | 学习哲学 + 已走的路（最后更新 4-13，**4-10 后新学的 NFC/Swift/硬件未追记**） |
| `project_evolution.md` | ✅ | 4 次重大转折（最后更新 4-13，待补"第五次转折"= demo 完成情况） |

### 6.2 05_logs/raw/（36 文件，2026-05-12 校准）

| 文件 | AC 候选密度 | 备注 |
|---|---|---|
| `README.md` | — | raw 目录说明 ✅ |
| `2025-12_NFC系统早期设计对话.md`（3100 行）| ⭐⭐ | 项目起源原始素材 |
| `2026-04-12_NFC架构讨论.md` | ⭐⭐ | 播报防作弊原创设计 |
| `2026-04-13_版本管理和AC工作流.md` | ⭐⭐ | 版本号纠错 + 记录方法论 |
| `2026-04-15_NFC硬件+Phase2架构讨论.md` | ⭐⭐⭐ | **#AC候选量最密集**（推翻+重论证+双路径） |
| `2026-04-17.md` | ⭐⭐ | 25 项 spec 漏洞 + Q1-Q5 拍板 + v0.3.0 |
| `2026-04-19.md` | ⭐⭐⭐ | 方法论级（取消分阶段 + 文档同步机制 A+B+C） |
| `2026-04-20.md` + `2026-04-20_v0.3.1发布执行.md` | ⭐⭐ | URL 漏洞 + ST25DV 动态贴纸 + 进度如实汇报 |
| `2026-04-21.md` | ⭐⭐⭐ | **Tomoshibi 命名** + Pi 3A+ 反直觉决策 |
| `2026-04-22.md` + `2026-04-22_iOS前端设计_Round1.md` | ⭐⭐ | 4-tab 推翻 + 73 页清单 + Round 3 解包 |
| `2026-04-23.md` | ⭐⭐⭐ | 学号 6 桁 + 跨会话同步规则 A+B+C + 巧合收束 |
| `2026-04-24.md` / `2026-04-29.md` / `2026-04-30.md` | ⏳ | 老师反馈受领 + 三轨 ABC 落地 + 学習 NFC 化 |
| `2026-05-01.md` / `2026-05-02.md` / `2026-05-03.md` | ⭐⭐ | 5 月初 v0.4-v0.6 推进（公告 4 端 / 注册码 spec） |
| `2026-05-04.md` + `2026-05-04_iOS_bug修复.md` | ⭐⭐ | WIP/TODO 分工拍板 + iOS bug 修复 |
| `2026-05-06.md` | ⭐⭐⭐ | **独立 repo 退役** — 5 端全合并回 DMSD monorepo |
| `2026-05-07.md` | ⭐⭐ | iOS 上架冲刺启动 + 教学 skill 拍板 |
| `2026-05-08.md` + `2026-05-08_ios_上架冲刺.md` + `2026-05-08_reviewer_demo重做.md` + `2026-05-08_vps_deploy_steps.md` | ⭐⭐⭐ | GCP VPS 部署 + Apple Reviewer demo 5 bug 修干净 + 点呼机第 5 端拍板 |
| `2026-05-10.md` | ⭐⭐ | 15 skill 批量装 + ac-radar 上线 |
| `2026-05-11.md` + `2026-05-11_reviewer后门修复上线.md` | ⭐⭐⭐⭐⭐ | 术语表 HTML / session-coord / graphify / **沟通问题大爆发**（cc-comm-rules 立 skill）/ reviewer 后门修复跨机器协作 |
| `2026-05-11_深夜大整理.md` + `2026-05-12_深夜大整理_总结报告.md` + `_AC价值汇总.md` + `_问题清单_codex修复SOP.md` + `_codex_auto_修复.md` + `_压缩后接力指引.md` | ⭐⭐⭐⭐ | CC 自治模式跨夜大整理（5-11 23:30 → 5-12 04:57）— 38 条 AC 素材 + 11 区域 codex 修复 SOP + 整理脚本 `/tmp/cleanup_2026-05-12.sh` |

### 6.3 05_logs/dev_log/（9 文件）

| 文件 | 状态 |
|---|---|
| 2026-02 月 4 个（早期规格设计） | 📦 历史快照 |
| `2026-04-10_空白期反思_索引.md` | ✅ — 1 个月空白期的 in-repo 锚点（正文在 iCloud） |
| `2026-04-10_回归日.md` + `2026-04-10_session_summary.md` | ✅ |
| `2026-04-12_NFC方案设计日.md` | ✅ |
| `2026-04-15_[NFC][MULTI]_硬件重开与Phase2架构.md` | ✅ |

> **断更现象**：02-08 → 04-10 共 66 天无 dev_log。已由 `空白期反思_索引` 解释。

### 6.4 05_logs/problem_solving/（4 文件）

全部 ✅ — 4-10 NFC/NFD git pull 失败 / 4-15 AI 过度配置诊断 / 4-15 iOS 限制下双路径重构 / 4-15 spec gap 发现。**全集中 4-10/4-15**，4-15 后无新增。

### 6.5 06_assets/ + bin/（4 文件）

| 文件 | 状态 |
|---|---|
| `06_assets/icons/tomoshibi_flame_color.png` + `_mono.png` | ✅ — 4-23 设计 |
| `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md` | ⚠️ — 含**学生实名**，v1.0 公开前需脱敏 |
| `06_assets/bus_schedule_real.md` | ✅ — 学校班车时刻表真值数据（2026-05-08 从 02_design/ 挪入,因为是数据不是设计）— iOS / teacher_web 做班车视图时的 seed data |
| ~~`bin/sync-ios-refs.sh`~~ | 📦 — 2026-05-06 归档到 `99_archive/2026-05-06_cloud_agent_退役/`（独立 repo 模式退役） |

---

## 7. 第 7 组：99_archive（109 文件）

**统计**：📦 96 / ⚠️ 5（NFC 鬼影）/ ❓ 8（.510Z + .pages + .docx 不可读）
**总磁盘**：~21 MB

### 7.1 根级（21 文件）

| 文件 | 状态 | 建议 |
|---|---|---|
| `README.md` | ✅ | 归档导航 |
| 14 × `ファイル - 2026-02-17T*.510Z`（共 6.7MB PDF dump） | ❓ | 内容已整理到 raw/2025-12 — **可删** |
| 5 × `*_原始.pages` / `*_备份版.pages` / `Folder_Structure_Overview.pages` | ❓ | 已被 .md 取代，无版本控制价值 — **可删或保留待 itsuki 决定** |
| `2026-04-12_executable_dev_checklist_v0.1.md` | 📦 | NFC 方案确定后第一份开发清单 |

### 7.2 各专题归档子目录

| 子目录 | 文件数 | AC 价值 | 建议 |
|---|---|---|---|
| `01_specs_Overview_原稿/` 2 个 .docx | 2 | ⭐ | **可删**（已被 .md 取代） |
| `2025-12_早期GPT对话/`（prompt + payload + resp）| 3 | ⭐⭐⭐ | **保留** — 项目起源证据 |
| `2026-03-08_throwaway_ios_swift/` 完整 Xcode 项目 | 35 | ⭐⭐⭐ | **保留** — Phase 0 试错代码（验证 Core NFC + FaceID + Secure Enclave 可行性） |
| `NFC_NFD_鬼影文件/` 5 个`のコピー` | 5 | ⚠️ | **需 itsuki 决定** — 若问题已解决可删；若保留作"问题解决证据"，README 补 1 句 |
| `2026-04-15_old_demo/` Flask demo | 9 | ⭐⭐⭐ | **保留** — 首个可运行原型（3 端点 + iPhone Shortcuts） |
| `2026-04-29_pre_v1.0_cleanup/` 大整理 | 34 | ⭐⭐⭐ | **保留** — 见下 §7.3 |

### 7.3 2026-04-29_pre_v1.0_cleanup/ 详细（34 文件）

| 子分组 | 文件 | 价值 |
|---|---|---|
| `demo_4-28/`（11 文件）| README + sprint + scope_tier + demo_script + ST25DV_fallback + for_code_agent + questions_for_admin + questions_for_requirements + 3 子（round1/round2/round3 handoff）| ⭐⭐⭐ AC 核心 — 完整 7 天 demo sprint 档案 |
| `teacher_web_round2/` 6 jsx | live / login / override-modal / shell / theme / roll-call-landing | ⭐⭐ Round 2 UI skeleton |
| `teacher_web_round3_handoff/` 5 文件 | README + Prompt + 3 张参考画像 | ⭐⭐ Round 3 输入素材 |
| `teacher_web_handoff_round2/` 4 文件 | README + chat1.md + design-system-round1.html + 1 截图 | ⭐⭐ chat1.md AC 素材保留 |
| `student_ios_round1_handoff/` 6 文件 | README + Round1_Prompt + 4 张参考画像 | ⭐⭐ |
| 杂项 5 文件 | Tomoshibi_iOS_PhaseB_v1 / _archived_v1_DESIGN_BRIEF / DEPRECATED handoff / round2 entry HTML / teacher_requirements_v0.5.0_draft | ⭐⭐ 迭代历史 |

---

## 8. 综合横向洞察

### 8.1 demo ↔ v1 复制策略对照（2026-05-06 退役独立 repo 模式后）

| 模块 | 策略 | 现状 |
|---|---|---|
| **backend** | "重写 + 参考" | demo 锁定不动；v1 schema 全新（UUID + TIMESTAMPTZ + CHECK 约束）；ws_manager / models 思路参考 ✅ |
| **teacher_web** | "复制起点 + 待改" | demo / v1 100% MD5 相同（4-30 整体复制后未动）⏳ |
| **student_ios** | DMSD single source | Swift 在 `03_dev/student_ios/v1/TomoshibiApp/`（16578 行），直接 Xcode 改 ✅ |
| **student_android** | DMSD single source | Kotlin 在 `03_dev/student_android/v1/`（6945 行 / 2026-05-06 从 Tomoshibi-Android 合并），直接 Android Studio 改 ✅ |

> **2026-05-06 退役独立 repo 模式**：Tomoshibi-iOS（4-23 起 mirror）+ Tomoshibi-Android（5-02 起 single source）合并回 DMSD。理由 = cloud agent 实际未真用 + 维护成本不抵收益 + 给教授看 GitHub 时多 repo 显乱。详见 `99_archive/2026-05-06_cloud_agent_退役/README.md`。

### 8.2 .pages / .docx / .510Z 不可读文件的命运

repo 里共 **8 个 .pages + 2 个 .docx + 14 个 .510Z = 24 个 CC 不可读文件**：
- 14 个 .510Z 都是早期 GPT 对话 PDF dump，内容已整理到 `raw/2025-12_NFC系统早期设计对话.md`
- 5 个 .pages 在 `01_specs/` 都已被 .md 取代
- 5 个 .pages 在 `99_archive/` 都是早期手稿，已被 .md 抢救
- 2 个 .docx 在 `99_archive/01_specs_Overview_原稿/` 都已被 .md 取代

**统一建议**：除 `01_specs/v0.1完整计划.pdf`（PDF 可读、AC 答辩用）外，其他 24 个全部可清理，节省约 13 MB。但**要 itsuki 一次性确认**（不是 CC 自行清理）。

### 8.3 文档同步漂移现状（4-29 SOP 后）

- ✅ 版本号漂移已解（4-21 hook + 4-29 SOP 双重保护）
- ✅ ≥8.0 阈值漂移已解（4-29 重新冻结后 ~10 处文档已修）
- ⚠️ `progress_overview.md` vs draft 错位 11 天未合
- ⚠️ `learning_path.md` 4-10 后新学未追记（NFC / Core NFC / Swift / 硬件）
- ⚠️ `decision_log.md` 6 条决策"事后回看"占位待补
- ⚠️ `跨会话_ios_共享决策.md` 短期 TODO 文件已过期（iOS 工程独立）

### 8.4 三层 DESIGN_LOG 体系成熟度

4-29 大整理后建立的 BACKEND / WEB / IOS 三层体系：
- 都活跃维护中（4-30 同日全部更新）
- 都和 `system_features.md` 锁定同步关系
- 都有 §11 v1.0 实装清单 section
- 都被 v1/v_demo 子目录共享（不重复 per-module）

这是 4-29 整理的最大资产 — **值得在 AC 叙事 v0.7.0 / v0.8.0 重点展开**（"工程化治理思维"角度）。

---

## 9. 综合行动清单

### 9.1 P0 立即可做（**2026-05-13 commit b37d065 + 81842f4 + 859693e 大部分已 ✅**）

| # | 任务 | 来源 | 状态 |
|---|---|---|---|
| 1 | ~~`跨会话_ios_共享决策.md` 归档~~ → `99_archive/2026-05-12_深夜大整理/` | §1.5 | ✅ 5-13 commit 81842f4 |
| 2 | ~~`v0.4.0_S系列spec漏洞优先级分析.md` 归档~~ | §1.2 | ✅ 5-13 commit 81842f4 |
| 3 | ~~`DESIGN_BRIEF.md` 改名~~ → `_archived_DESIGN_BRIEF_Round1_context.md` | §5.1 | ✅ 5-13 commit 81842f4 |
| 4 | ~~`Round2_Prompt_C3.md` 改名~~ → `_archived_Round2_Prompt_draft.md` | §5.1 | ✅ 5-13 commit 81842f4 |
| 5 | ~~`.DS_Store` 误进 git~~ | §7 | ✅ `.gitignore` 已生效 git 不 track |
| 6 | 在 `models.py` 表 docstring 标 P0 / P1 / P2 | §3.3 | ⏳ 未做 |
| 7 | 更新 `文件结构指南.md`：补 v0.6.0/v0.7.0 AC 叙事文件 + 新增 raw 日志 + cross-session iOS 决策的归宿 | 跨多组 | ⏳ 部分（本 skill 已校准，`文件结构指南.md` 待 itsuki 拍板）|
| 8 | 更新 `99_archive/README.md` 时间戳 + 鬼影文件解决说明 | §7.5 | ⏳ 未做（itsuki 拍板）|
| 9 | **5-13 新增**：4 sub agent draft 待 itsuki 粘贴 → `decision_log` / `learning_path` / `project_evolution` / `system_features §8` | — | ⏳ /tmp/ 待 itsuki |
| 10 | **5-13 新增**：classifier 拦 2 个 skill `sed -i.bak 's\|17 条联动\|18 条\|' .claude/skills/file-linkage/SKILL.md` + `sed -i.bak 's\|/Users/itsuki/\|/Users/kurekoduki/\|g' .claude/skills/memory-write/SKILL.md` | — | ⏳ itsuki 自己 sed |
| 11 | **5-13 新增**：99_archive 100% 重复目录 `2026-05-02_backend_handoff_F1-F7/` vs `2026-05-02_handoff_F1-F7/` itsuki 决定删哪个 | §7 | ⏳ itsuki 拍板 |

### 9.2 P1 itsuki 决定后批量执行（节省 ~13 MB）

| # | 任务 | 决定点 |
|---|---|---|
| 9 | 删 14 个 `99_archive/ファイル - *.510Z` PDF dump | 已确认对应 .md 在 raw/2025-12 |
| 10 | 删 5 个 `99_archive/*.pages`（learning_process / progress_log × 2 / 需要学习 / Folder_Structure）| 都已被 .md 抢救 |
| 11 | 删 2 个 `99_archive/01_specs_Overview_原稿/*.docx` | 已被 .md 取代 |
| 12 | 删 4 个 `01_specs/*.pages`（API_Contract / IA_UI / Overview_of_Features / RollCall_Spec_v0.1）| 已被 .md 取代 |
| 13 | 处理 `01_specs/rollcall/DMSDv0.1验收脚本.pages` | 与 PDF §1.2 是否相同？|
| 14 | 处理 `99_archive/NFC_NFD_鬼影文件/` 5 个 | 问题已解决可删；保留则 README 补说明 |

### 9.3 P1 待 itsuki 手笔合并（30-60 分钟单次工作）

| # | 任务 | 文件 |
|---|---|---|
| 15 | 合并 `progress_overview_draft_2026-04-20.md` → `progress_overview.md` | §1.3 |
| 16 | 合并 `Batch3_itsuki手笔素材指引.md` 4 个 draft → decision_log / project_evolution / learning_path | §1.4 |
| 17 | 追记 `learning_path.md` 4-10 后新学（NFC 原理 / Core NFC / Swift / 硬件选型） | §6.1 |
| 18 | 补 `decision_log.md` 6 条"事后回看"（可月度 review 中合并） | §6.1 |

### 9.4 P1 待开发会话补全（后端 P0 缺块）

| # | 任务 |
|---|---|
| 19 | `routers/applications.py` 加 `POST /{id}/approvals`（#10-#13 役职审批） |
| 20 | 新建 `routers/rollcall.py`（#14-#20 点呼 iPad） |
| 21 | 新建 `routers/study.py`（#16-#20 学习担当） |
| 22 | `services/email.py` 补 retry 3 次循环 |

### 9.5 P1 待开发会话推进（teacher_web v1.0 启动）

| # | 任务 |
|---|---|
| 23 | 删 v1/ 复用的 build/single-file 脚本（4 个 .command + .py） |
| 24 | 改 `theme.jsx` seed → fetch API |
| 25 | 改 `shell.jsx` 5 角色不同菜单 |
| 26 | 改 `login.jsx` 真认证 |
| 27 | 改 `live-roll-call.jsx` poll → WebSocket |
| 28 | 补 Tier 1 剩余页面（外泊 / 帰省 / 帰国 / records / search / 健康申报 / 请假流程） |

### 9.6 P1 iOS（待 Agent 派发）

| # | 任务 |
|---|---|
| 29 | Agent D dispatch — Apply v2（StayForm 8 section） |
| 30 | Agent E dispatch — MyPage v2（Landing + Info + Rollcall + Points + PointsChart + Discipline + Settings 14 view） |
| 31 | 决定 Schedule / StayList / BusList 3 个 stub 命运（删 / redirect / 保留） |
| 32 | 澄清 Assets.xcassets SDK 冲突现状 |

### 9.7 P2 一月内（脱敏 + 补 AC 素材）

| # | 任务 |
|---|---|
| 34 | `06_assets/real_samples/bus_notice_*.md` 学生实名脱敏（v1.0 公开前必做） |
| 35 | 提炼 4 篇 problem_solving → iCloud `03_素材_候选/`（CC 协助） |
| 36 | `AC_志望動機_素材.md` Q1-Q8 起草 |
| 37 | 月度 review（5 月底）— 5 月 AC 候选 + monthly_review/2026-05.md |

---

## 10. AC 叙事 top 10 文件（跨全 repo）

按"AC 自我推荐书 + 面试可讲性"排序：

| 排名 | 文件 / 文件群 | 核心问题 | 一句话推介 |
|---|---|---|---|
| 1 | `2025-12_早期GPT対話/` 三件套 | #1 #4 | 项目起源 — 从纸质点呼痛点到 AI 对话定义需求 |
| 2 | `99_archive/2026-03-08_throwaway_ios_swift/` 35 文件 | #3 #4 | Phase 0 试错代码 — 用真实 Swift 验证 Core NFC + FaceID + Secure Enclave |
| 3 | `00_admin/原创设计_语音播报防作弊.md` | #3 | 自动贩卖机灵感 → 代刷观察 → 最简工程方案的完整链 |
| 4 | `05_logs/raw/2026-04-15_NFC硬件+Phase2架构讨论.md` + 4 个 problem_solving | #2 #3 | 推翻 + 重论证 + 双路径方案诞生（最浓密的思维碰撞日） |
| 5 | `99_archive/2026-04-29_pre_v1.0_cleanup/demo_4-28/` 11 文件 | #3 | 7 天 demo sprint 完整需求→设计→交付链 |
| 6 | `02_design/system_features.md` 357→830 行重写 | #3 #4 | 老师 38 条反馈受领 + 共用真值矩阵建立 |
| 7 | `00_admin/v0.7.0_AC叙事.md` 三轨 A/B/C 并行 | #3 #4 | 多会话工程实践 + 信息源选择 lesson |
| 8 | `99_archive/2026-04-15_old_demo/` 9 文件 | #3 | 首个可运行原型（Flask + iPhone Shortcuts + TTS） |
| 9 | `99_archive/2026-05-06_cloud_agent_退役/` 完整归档 | #3 #4 | 多 agent 协作的工程解 → 退役迭代（4-23 拍板 → 5-06 退役 13 天周期，约束变化后的方法论再校准）|
| 10 | `00_admin/版本管理SOP.md` + hooks 三件套 | #4 | 文档治理思维：从漂移发现到机制化解决 |

---

## 11. itsuki 待决定列表

| # | 决定点 | 影响 |
|---|---|---|
| 1 | 24 个不可读文件（.pages / .docx / .510Z）一次性清理? | 节省 ~13 MB / 减少 confused 文件 |
| 2 | NFC_NFD 鬼影文件去留? | 5 文件去留 + README 加 1 句解决方式 |
| 3 | `v0.1_冻结决策.md` 角色定位（备份单源 / 历史快照） | 影响 §文档同步点清单 登记 |
| 4 | `progress_overview_draft_2026-04-20.md` 合并时机 | 教授看 GitHub "做到哪了" 信息新鲜度 |
| 5 | `Batch3_itsuki手笔素材指引.md` 4 个 draft 合并时机 | 30-60 分钟单次工作 |
| 6 | iOS Schedule / StayList / BusList 3 个 stub 命运 | 删 / redirect / 保留 |
| 7 | `bus_notice_*.md` 学生实名脱敏时机 | v1.0 公开前必做 |
| 8 | 是否启动 v1.0 teacher_web 真改造（删 demo 复用脚本 + 真后端 + 5 角色菜单） | v1.0 进度 |

---

## 12. 附：本次审查方法

1. 主会话切 7 组（按目录分组 + vendor 聚合）
2. 7 个 Explore agent 并行扫描，每个 agent 拿到：
   - 项目背景（DMSD / Tomoshibi / 当前 v0.7.0 / 三层 DESIGN_LOG 体系等）
   - 范围内文件清单
   - 输出格式规约（每个文件给作用 / 状态 / 价值 / 建议 4 列）
3. 每个 agent 返回独立 markdown report
4. 主会话合成：精简表格 + 横向洞察 + 综合行动清单 + AC top 10

**精简率**：原 7 个 agent 报告共 ~2500 行 → 本文 ~600 行（保留所有文件清单 + 关键结论 + 跨组洞察，去掉重复列）。

---

## 13. 文件联动指南（一环扣一环 — 2026-05-04 itsuki 拍板加）

> **背景**：2026-05-04 注册码 4 vs 6 位 trade-off 讨论时，CC 数了一下「改一件事会牵动多少文件」 — **9 个文件**：backend models / schemas / router / migration / test / 2 处 spec + iOS NetworkModels / RegisterStep5 view。itsuki 当场拍板「记录到本文件，做改动前先看」+「写到 CLAUDE.md 让以后的 CC 也能看到」（CLAUDE.md §文件连锁结构 已 itsuki 精简重写，指向本节）。
>
> **怎么用本节**：itsuki 或 CC 准备做某个改动前，对照下表查「改 X 必查 Y」，避免漏改某个端 → bug 上线。
>
> **代码源**：本节是 `00_admin/hooks/lib/sync-rules.sh` 的人类可读版。规则代码化之后 pre-commit 会自动检查 + `bash bin/sync-check.sh` 中途随时查。两边内容必须等价。

### 13.1 联动表（改 X → 必查 Y）

| 改了什么 | 一环扣一环必查文件 | 不查的后果 |
|---|---|---|
| `backend/v1/app/models.py` ORM 字段 | (1) `schemas.py` Pydantic 校验  (2) `alembic/versions/*.py` migration  (3) `routers/*.py` API 形状  (4) `student_ios/.../NetworkModels.swift` iOS 端字段对齐 | DB 跟代码不一致 / iOS 解析 fail / migration apply 报错 |
| `backend/v1/app/routers/*.py` API 端点 | iOS `Endpoints/*API.swift`（URL / 参数 / 返回类型对齐）| iOS 调到不存在的端点 / 参数错 → 422 |
| `02_design/system_features.md`（共用层）| **5 端** `*_DESIGN_LOG.md` 引用是否要更新（BACKEND / IOS / ANDROID / WEB / ROLLCALL_DEVICE — 至少 1 个通常受影响）| 共用层规则改了，专属层引用过期 → 实装跟设计漂移 |
| `02_design/hardware_design.md`（物理层）| `rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md`（接线 / GPIO / 模块选型联动）| 软硬层割裂 → 软件按旧硬件接线写 |
| **iOS Features 业务 .swift（反向）** | `IOS_DESIGN_LOG.md` + 多端涉及时 `system_features.md` | 设计 → 代码漂移（typo / 重构不用同步,改 UI / 流程 / 字段需要）|
| **Android ui/features 业务 .kt（反向）** | `ANDROID_DESIGN_LOG.md` + 多端涉及时 `system_features.md` | 同上 |
| **backend routers/services 业务 .py（反向）** | `BACKEND_DESIGN_LOG.md` + 多端涉及时 `system_features.md` | 同上 |
| **teacher_web 业务 .{ts,tsx,jsx,vue}（反向）** | `WEB_DESIGN_LOG.md` + 多端涉及时 `system_features.md` | 同上 |
| **rollcall_device/src/*.py（第 5 端反向）** | `ROLLCALL_DEVICE_DESIGN_LOG.md` + 多端涉及时 `system_features.md` | 同上 |
| **任一端 `*_DESIGN_LOG.md`（反向）** | 多端涉及时 `system_features.md`（共用层真值）| 端→共用反方向漂移 |
| iOS `Foundation/Routing/Route.swift` 加 case | (1) `Root/RootView.swift` switch 必须补对应分支  (2) 用到的 view 要存在 | 编译失败 |
| iOS `Foundation/<Pill\|Card\|Avatar\|GlassSheet>*.swift` 组件 props | grep 全 repo 找 caller，逐个对齐新 props | caller 编译失败 |
| `01_specs/*.md` 主体 | 触发版本管理 SOP §10 4 问 → 可能要 bump 版本号 | 版本号跟实质改动脱节 |
| `00_admin/hooks/*` | `00_admin/hooks/README.md` 同步说明（除非改的就是 README 自己）| 新机器 clone 后照旧 README 跑 → 配置错 |
| `bin/*.sh` 脚本 | (1) `CLAUDE.md` 单源真值速查表  (2) `00_admin/文档同步点清单.md`  (3) `00_admin/hooks/README.md`（任 1）| CC 不知道有这个脚本、用旧办法做事 |
| 新建 `CLAUDE.md` / `00_admin/*.md` 声明性文件 | (1) `00_admin/文档同步点清单.md` 加入 §1 让 hook 保护它  (2) **本文件**（项目文件总览）加入对应章节 | 新文件没 hook 保护 → 版本号漂移 / 新会话不知道有这个文件 |
| 新建 / 改名 / 删除文件 | 同步更新**本文件**（项目文件总览）对应章节 + 顶级目录变化时改 `CLAUDE.md §目录结构` | 新会话 / CC 看不到 / 找不到文件 |

> **2026-05-08 加 6 条反向规则**（Rule 14-19）：业务代码 → 自端 *_DESIGN_LOG.md / 共用层 system_features.md。`action` 模式（温和提醒,不强制）— typo / 重命名 / 重构不用同步,改 UI / 流程 / 字段才需要。覆盖 5 端对称（iOS / Android / backend / teacher_web / 点呼机）。规则总数 12 → 18。

### 13.2 实战案例：注册码长度从 6 位改成 4 位（如果将来要改）

> 这是 2026-05-04 当场数出来的「改一件事 = 9 文件」案例。**写在这里让 itsuki 直观感受联动密度**。
>
> （2026-05-04 itsuki 最终决定保 6 位不改 — 但这个案例留作以后类似决策的参考。）

| # | 文件 | 改什么 |
|---|---|---|
| 1 | `backend/v1/app/models.py` `StudentRegistrationCode.__table_args__` | `CheckConstraint("LENGTH(code) = 6")` → `= 4` |
| 2 | `backend/v1/app/schemas.py` `StudentAccountCreateIn.registration_code` + `RegistrationCodeOut.code` | `min_length=6, max_length=6, pattern=r"^\d{6}$"` → 4 / `^\d{4}$` |
| 3 | `backend/v1/app/routers/admin_registration_code.py` `_generate_code()` | `f"{random.randint(0, 999999):06d}"` → `randint(0, 9999):04d` |
| 4 | `backend/v1/alembic/versions/d4e5f6a7b8c9_add_student_registration_codes.py` | `sa.CheckConstraint("LENGTH(code) = 6")` → 4，`sa.String(length=6)` → 4 |
| 5 | `backend/v1/tests/test_registration_code.py` | `assert len(data["code"]) == 6` → 4 |
| 6 | `02_design/system_features.md §7.16.2 规则 1` | "登録コードは数字 6 桁" → 4 桁 |
| 7 | `02_design/system_features.md §7.16.5 功能矩阵` + `BACKEND_DESIGN_LOG.md §4.10` | code 长度描述改 |
| 8 | `student_ios/v1/TomoshibiApp/Features/Auth/AuthStubs.swift` `RegisterStep5View` | `canSubmit: code.count == 6` → 4，`prefix(6)` → 4，placeholder `"000000"` → `"0000"`，banner 文案「6 桁の認証コード」→ 「4 桁」 |
| 9 | `student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift` `StudentAccountCreateBody` 注释 | `// 6 桁数字` → 4 桁 |

→ **9 个文件**。**所以同样的功能性参数，决定时一定要慎重 — 改一次成本不小**。

### 13.3 工具自动化

- **commit 时**：pre-commit hook 自动跑 `00_admin/hooks/lib/sync-rules.sh` 检查 staged 文件联动。warn-only 不阻断。
- **中途随时查**：`bash bin/sync-check.sh`（3 模式：all / --staged / 指定文件）
- **加新规则**：编辑 `00_admin/hooks/lib/sync-rules.sh`（add_rule 一次）+ 同步本节表 + 同步 `CLAUDE.md §文件连锁结构` + 更新 `00_admin/hooks/README.md`
- **完整文档**：`00_admin/文档同步点清单.md §11`

### 13.4 v1.0 上线前必删 demo scaffold 集中清单

> **位置**：`02_design/system_features.md` 末尾「⚠️ v1.0 上线前必删」section（itsuki 上线前必读 system_features，看到清单照着删一次）。
>
> **当前已登记**：iOS 7 处 + Backend 0 处 + Teacher Web 4 处 + 环境配置 2 项。新加 demo scaffold 时必须 (a) 代码加 `// ⚠️ DEMO-ONLY-SCAFFOLD（YYYY-MM-DD）：XX，v1.0 删` 注释  (b) 在 system_features.md 那个 section 登记。
>
> **配套自动扫描**：`grep -rn "DEMO-ONLY" 03_dev/ | grep -v "node_modules\|_legacy\|__pycache__\|\.venv\|DerivedData"` — 上线前跑一次，对照清单全删完。

---

**本文最后更新**：2026-05-13 中午（接力 CC 校准 — 顶部 §0 体量数字 + §1.4/§1.5 26 文件 git mv 路径 + §1.6 hooks 8→11 / sync-rules 18→21 / PostToolUse 5→6 + §1.8 非编号目录新章节 + §3.4 backend routers 5→11 补 6 漏 + §3.6 tests 3→5 + §3.7 P0 删 rollcall/study 已建加 accounts/card_uid + §5.1 iOS 改名 + 末尾时间戳。基于 sub agent af04d326 audit 报告 `/tmp/project_overview_audit.md`）。早些更新：2026-05-12 凌晨 CC 自治大整理 / 2026-05-08（§5.7 补 student_android 章节 — 之前 5-06 合并回 DMSD 漏补;§5.8 加点呼机第 5 端骨架;§13.1 加 6 条反向规则 Rule 14-19;§0.4 五层 DESIGN_LOG;§2.3 / §6.5 同步 bus_schedule 挪位置）/ 2026-05-04（加 §13 文件联动指南）/ 2026-05-01（首次创建 7 组并行扫描 606 文件合成）

> **未做完 — 留给下次 CC**（2026-05-13 audit 18 条 Edit 建议）：
> - §0.1 体量表 7 行数字全过期（606→685 实际）— 要重跑 git ls-files 全统计
> - §4.3 teacher_web v1 整段失效 — 实际已 Vite + TS 重构进行中（35+ 真改造文件 + _legacy/ 隔离）
> - §5.5 iOS Feature 行数 8 行全错（StayList 748→1588 翻倍）
> - §6.2 raw/ 漏 7 个 5-12/5-13 新增（36→41）
> - §7 99_archive 漏 7+ 新建子目录（migration_2026-05-06 / 2026-05-02_* × 4 / 2026-05-12_深夜大整理 等）
> - §10 AC top 10 第 10 项 版本管理SOP 路径已迁
> - §11 itsuki 待决定列表 8 条状态复核（progress_draft / 跨会话 已归档）
> - 完整清单：`/tmp/project_overview_audit.md`
