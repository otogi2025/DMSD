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
> **最后更新**：2026-05-04 深夜（迁入 skill 形态）

---

## 0. 摘要

### 0.1 体量

| 顶级目录 | 文件数 | 占比 | 主要内容 |
|---|---|---|---|
| `03_dev/` | 407 | 67% | 代码 + 设计 LOG（teacher_web vendor + 字体占大头） |
| `99_archive/` | 109 | 18% | 归档物（早期 GPT 对话 / throwaway iOS / demo 4-28） |
| `00_admin/` | 32 | 5% | 管理文档 / AC 叙事 / hooks |
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

- **demo ↔ v1 复制策略**：backend 选了"重写"（schema 全新）✅；teacher_web 选了"复制不动"⏳；iOS v1 走独立 repo（refs/ 物理拷贝）— 三种姿态都对，但要明文说清楚。
- **三层 DESIGN_LOG 体系生效**：BACKEND / WEB / IOS 三个 DESIGN_LOG 都活跃且与 system_features.md 同步链清晰，是 4-29 大整理后的最大资产。
- **AC 叙事供应充足**：80+ 条 #AC候选 + 6 个 per-version 叙事（v0.3-0.7）+ 4 个 problem_solving 精品版 + 3 个 03_dev/_DESIGN_LOG 工程化叙事 — 数量上远超 AC 自我推荐书所需。

---

## 1. 第 1 组：根目录 + 00_admin（36 文件）

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

### 1.3 00_admin/会话状态（4 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `WIP.md` | ✅ | 多会话协调枢纽 |
| `TODO.md` | ✅ | 三轨 A/B/C 推进中 |
| `progress_overview.md` | ⚠️ | 内容停在 4-17，**11 天没合 draft** |
| `progress_overview_draft_2026-04-20.md` | 📦 | draft 已就绪等审 |

### 1.4 00_admin/AC 叙事（12 文件，2026-05-04 更新加 v0.8.0）

| 文件 | 状态 | 价值 |
|---|---|---|
| `v0.3.0_AC叙事.md` ~ `v0.8.0_AC叙事.md`（7 个） | ✅ | 完整 7 版本素材链。**5-04 起新规则**：itsuki 自己写不主动起草，历史 v0.3-v0.8 的 7 个是 CC 起草保持不动 |
| `面试准备_索引.md` | ✅ | 6 大类 42+ 题清单（题目占位，回答留 iCloud） |
| `原创设计_语音播报防作弊.md` | ✅ | ⭐ AC 最强素材之一 |
| `AC_志望動機_素材.md` | ⚠️ | 框架完整 / 内容 0/8 留白等 itsuki 自填 |
| `AC_提交_checklist.md` | ⚠️ | 5-10 月 6 个 gate 倒计时 + 月度 review 工作流 |
| `Batch3_itsuki手笔素材指引.md` | 📦 | 4 个 ready-to-paste draft 等 itsuki 合并（30-45min 工作量） |

### 1.5 00_admin/v0.4.0 spec draft + 其他（6 文件）

| 文件 | 状态 | 建议 |
|---|---|---|
| `v0.4.0_Device_Contract骨架.md` | 📦 | 已融入 BACKEND_DESIGN_LOG，参考用 |
| `v0.4.0_S2_S3_字段draft.md` | 📦 | 已融入 FIELD_REGISTRY |
| `T2_iOS归档_dryrun评估.md` | 📦 | 已执行（旧 iOS 已移 99_archive），可清理 |
| `wifi_survey_howto.md` | ✅ | 等 itsuki 实地调研 |
| `跨会话_ios_共享决策.md` | ⚠️ | 注明"短期 TODO 用"，已融入 system_features 和独立 iOS repo，**可清理** |
| `create_local_dev_symlink.sh` | ✅ | VPS 已停用但脚本保留参考 |

### 1.6 00_admin/hooks（6 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `install.sh` | ✅ | 首次 clone 后跑一次（`git config core.hooksPath`）|
| `pre-commit` | ✅ | git commit 前 3 件事：版本号一致性 + bump 提醒 + 联动检查 |
| `post-edit-sync-check.sh` | ✅ | CC PostToolUse hook — Write/Edit 后跑 sync-rules 联动检查（2026-05-04 加）|
| `post-edit-memory-check.sh` | ✅ | CC PostToolUse hook — memory dir 改完提醒补 MEMORY.md 索引（2026-05-04 加）|
| `session-start-check.sh` | ✅ | CC SessionStart hook — 会话起自动跑轻量状态扫描（2026-05-04 加）|
| `lib/sync-rules.sh` | ✅ | 13 条联动规则代码化（pre-commit + post-edit-sync 共享）|
| `README.md` | ✅ | hooks 总说明（git + CC 两类全覆盖）|

### 1.7 .claude/skills（10 skill）

| skill | 状态 | 触发 / 用途 |
|---|---|---|
| `ac-record/` | ✅ | 「收尾 / 整理今天」AC 素材全量扫描 dump |
| `version-bump/` | ✅ | 「迭代 / bump / 发版本」版本决策树（CC 有否决权）|
| `file-linkage/` | ✅ | 「联动 / 改 A 要查 B」联动矩阵 13 条 |
| `project-overview/` | ✅ | 本 skill — 文件总览（itsuki 找文件时调）|
| `session-start/` | ✅ | 「启动 / 早上好 / 我回来了」7 步状态扫描（2026-05-04 加）|
| `memory-write/` | ✅ | 「记一下规则 / 以后这样」memory 写入 SOP（2026-05-04 加）|
| `new-feature/` | ✅ | 「新功能 X / 加 Y」4 端实装模板（2026-05-04 加）|
| `demo-clean/` | ✅ | 「v1.0 准备 / 删 demo」demo scaffold 清理（2026-05-04 加）|
| `spec-sync/` | ✅ | 「跨端检查 / 字段对齐」字段提取对比（2026-05-04 加）|
| `release-checklist/` | ✅ | 「发版 / 打 tag / release」发版动作 SOP（2026-05-04 加）|

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

### 2.3 02_design/（4 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `system_features.md` | ✅ | ⭐ iOS+Web+后端共用真値，4-30 轨道 ABC 同日完成（覆盖老师 38 条） |
| `hardware_design.md` | ✅ | Pi 3A+ 选型 + 砍 Pi 4B 论证（AC 素材） |
| `flow_design.md` | ✅ | 路径 A 卡 / 路径 B iOS / 路径 B Android |
| `bus_schedule_real.md` | ✅ | 实际巴士时刻表（参考材料），可考虑挪 04_ops/ |

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

### 3.4 backend/v1/app/routers/（5 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` | ✅ | 空包声明 |
| `auth.py` | ✅ | P0 完整（学生 + 教师 + JWT） |
| `applications.py` | ⚠️ | **P0 70%** — 学生提交/邮件/履历/详情 ✅，**缺 #10-#13 役职审批 endpoint** |
| `meals.py` | ✅ | P0 完整（JSON + Excel openpyxl） |
| `notifications.py` | ✅ | SendGrid 烟雾测试 |

### 3.5 backend/v1/app/services/（4 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `__init__.py` / `meals.py` | ✅ | meals.py P0 完整 |
| `approval_chain.py` | ⚠️ | 外泊 chain 证据确定 ✅；**帰省 / 帰国 chain 是 PROVISIONAL 暫定值**（待 itsuki 老师见面补 4 张实物表） |
| `email.py` | ⚠️ | 90% 完整，**缺 retry 3 次循环**（设计要求） |

### 3.6 backend/v1/tests/（3 文件）

`__init__.py` + `conftest.py` + `test_smoke.py` 都 ✅，17 个 test case 覆盖 P0 关键路径 70%。

### 3.7 v1 P0 缺块清单

需后续 P1 会话补：
1. `routers/applications.py` 加 `POST /{id}/approvals`（#10-#13 役职审批）+ `DELETE /{id}`（D3 撤回）
2. 新建 `routers/rollcall.py`（#14-#20 点呼 iPad）
3. 新建 `routers/study.py`（#16-#20 学习担当）
4. `services/email.py` 补 retry 3 次

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

## 5. 第 5 组：03_dev/student_ios + LATEST.md（54 文件）

**统计**：✅ 31 / 📦 4 / ⚠️ 6 / ❓/⏳ 13
**核心发现**：Foundation 层已冻结成熟（17 文件 1861 行）；3 个 Feature 已真实装；Apply / MyPage 待 Agent D/E

### 5.1 顶层 + demo（8 文件）

| 文件 | 状态 |
|---|---|
| `03_dev/LATEST.md` | ✅ — 最新原型位置指针 |
| `student_ios/README.md` | ✅ — 目录说明 |
| `student_ios/DESIGN_BRIEF.md` | ⚠️ — **已被 IOS_DESIGN_LOG 全覆盖**，建议改名 `_archived_DESIGN_BRIEF_Round1_context.md` |
| `student_ios/IOS_DESIGN_LOG.md` | ✅ — ⭐ §1-11 完整决策权威源 |
| `demo/.gitignore` | ✅ |
| `demo/QA_Round1_PhaseB.md` | ✅ — Claude Design Phase B 静态扫描报告 |
| `demo/Round2_Prompt_C3.md` | ⚠️ — C3 决策已 resolve，**可改名 `_archived_`** |
| `demo/Tomoshibi_iOS_PhaseB_v2.html` | 📦 — Phase B 完整原型（锁定不动） |

### 5.2 v1/ 顶层管理（7 文件）

| 文件 | 状态 | 备注 |
|---|---|---|
| `.gitignore` / `README.md` / `project.yml`（xcodegen） | ✅ | 常规 |
| `STATUS.md` | ✅ | 短期 session 快照（每天换） |
| `SHARED_DECISIONS.md` | ✅ | 6 行指针（指向 DMSD 主） |
| `SESSION_CHANGELOG.md` | ✅ | 详细历史变动日志 |
| `REMOTE_AGENT_GUIDE.md` | ✅ | ⭐ Cloud routine agent 执行手册（430 行 spec） |

> **职责重叠隐患**：STATUS（短期 snapshot）vs SESSION_CHANGELOG（详细历史）vs SHARED_DECISIONS（仅指针），文档头注释建议明确区分。

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

全部 ✅ frozen — AppState 2 / Components 12 / LiquidGlass 3 / Routing 2 / Seed 2 / Theme 1 + RootView + GlobalOverlays + TomoshibiApp 入口。1861 行专业级代码。**REMOTE_AGENT_GUIDE 明令禁改**。

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

### 6.2 05_logs/raw/（16 文件）

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
| `bin/sync-ios-refs.sh` | ✅ — DMSD → Tomoshibi-iOS/refs/ 单向同步 |

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

### 8.1 demo ↔ v1 三种姿态对照

| 模块 | 策略 | 现状 | 评估 |
|---|---|---|---|
| **backend** | "重写 + 参考" | demo 锁定不动；v1 schema 全新（UUID + TIMESTAMPTZ + CHECK 约束）；ws_manager / models 思路参考 | ✅ 正确 |
| **teacher_web** | "复制起点 + 待改" | demo / v1 100% MD5 相同（4-30 整体复制后未动） | ⏳ 等开工 |
| **student_ios** | "独立 repo + refs/ 物理拷贝" | DMSD 设计真值 + Tomoshibi-iOS Swift 实装；`bin/sync-ios-refs.sh` 单向同步 | ✅ 正确 |

三种都对，但要明文写在 `00_admin/文档同步点清单.md` 里说清楚（避免下个会话困惑）。

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

### 9.1 P0 立即可做（CC 可独立 / 1 小时内）

| # | 任务 | 来源 | 工作量 |
|---|---|---|---|
| 1 | 删 `跨会话_ios_共享决策.md`（已过期）或加注 `_archived_` 前缀 | §1.5 | 1 min |
| 2 | 删 `00_admin/v0.4.0_S系列spec漏洞优先级分析.md`（已被吸收）| §1.2 | 1 min |
| 3 | 改名 `student_ios/DESIGN_BRIEF.md` → `_archived_DESIGN_BRIEF_Round1_context.md`（IOS_DESIGN_LOG 已全覆盖） | §5.1 | 1 min |
| 4 | 改名 `student_ios/demo/Round2_Prompt_C3.md` → `_archived_Round2_Prompt_draft.md`（C3 已 resolve） | §5.1 | 1 min |
| 5 | 删 `99_archive/2026-04-15_old_demo/.DS_Store`（误进 git） | §7 | 1 min |
| 6 | 在 `models.py` 表 docstring 标 P0 / P1 / P2 | §3.3 | 10 min |
| 7 | 更新 `文件结构指南.md`：补 v0.6.0/v0.7.0 AC 叙事文件 + 新增 raw 日志 + cross-session iOS 决策的归宿 | 跨多组 | 20 min |
| 8 | 更新 `99_archive/README.md` 时间戳 + 鬼影文件解决说明 | §7.5 | 5 min |

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
| 33 | 跨会话管理文件（STATUS / SHARED_DECISIONS / SESSION_CHANGELOG / REMOTE_AGENT_GUIDE）头注释明确职责 |

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
| 9 | `bin/sync-ios-refs.sh` + 跨 repo 同步规则 | #3 | 多 agent 协作的工程解（source of truth + 单向 sync） |
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
| `02_design/system_features.md`（共用层）| 各端 `*_DESIGN_LOG.md` 引用是否要更新（至少 1 个端通常受影响）| 共用层规则改了，专属层引用过期 → 实装跟设计漂移 |
| iOS `Foundation/Routing/Route.swift` 加 case | (1) `Root/RootView.swift` switch 必须补对应分支  (2) 用到的 view 要存在 | 编译失败 |
| iOS `Foundation/<Pill\|Card\|Avatar\|GlassSheet>*.swift` 组件 props | grep 全 repo 找 caller，逐个对齐新 props | caller 编译失败 |
| `01_specs/*.md` 主体 | 触发版本管理 SOP §10 4 问 → 可能要 bump 版本号 | 版本号跟实质改动脱节 |
| `00_admin/hooks/*` | `00_admin/hooks/README.md` 同步说明（除非改的就是 README 自己）| 新机器 clone 后照旧 README 跑 → 配置错 |
| `bin/*.sh` 脚本 | (1) `CLAUDE.md` 单源真值速查表  (2) `00_admin/文档同步点清单.md`  (3) `00_admin/hooks/README.md`（任 1）| CC 不知道有这个脚本、用旧办法做事 |
| 新建 `CLAUDE.md` / `00_admin/*.md` 声明性文件 | (1) `00_admin/文档同步点清单.md` 加入 §1 让 hook 保护它  (2) **本文件**（项目文件总览）加入对应章节 | 新文件没 hook 保护 → 版本号漂移 / 新会话不知道有这个文件 |
| iOS Swift 任意 .swift 改 | 改完跑 `bash bin/sync-ios-refs.sh` 同步到 Tomoshibi-iOS repo | DMSD 跟独立 repo 漂移 |
| 新建 / 改名 / 删除文件 | 同步更新**本文件**（项目文件总览）对应章节 + 顶级目录变化时改 `CLAUDE.md §目录结构` | 新会话 / CC 看不到 / 找不到文件 |

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

**本文最后更新**：2026-05-04（加 §13 文件联动指南，2026-05-04 itsuki 拍板）。早些更新：2026-05-01（首次创建 7 组并行扫描 606 文件合成）
