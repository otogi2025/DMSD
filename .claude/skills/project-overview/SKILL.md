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
> **和别的「介绍型」文件分工**（三层不重叠）：`PROJECT_GUIDE.md`（根目录）= 新人 / AI 深入理解整个项目的导览；`00_admin/项目心智模型.md` = AI 开局必读的 1 屏骨架（系统怎么跑通 + 5 端现状）；**本 skill** = 1388 文件逐个的「字典」，想知道某个文件干嘛时查。
>
> **最后更新**：2026-06-10 — §6.2 raw 92→108 / §6.3 dev_log 9→14 / 05_logs 总数 177（find 实数，本会话 iOS 全量审查新增 raw 2 + dev_log 1，其余为并行会话累积）。上一轮：2026-06-05 — 全文件对账校准（1200→1399 真实数，以 HEAD committed 为准）：backend §3 大补（routers 11→26 / tests 5→20 / alembic 9→22 / 总 62→104）+ iOS 67→78 / Android 80→131 / 点呼机 12→36 / 05_logs 92→161 / 99_archive 431→639 + 散件补漏（01_specs / 02_design / 04_ops / 根目录 / skills 标题）。收尾时点含别会话并行提交（test_front_desk 等）。更早记录见 git log。

**最后扫描真值**：2026-06-05 `git ls-tree -r HEAD` 全统计（1399 已提交文件）+ 各组逐组验证 + `bin/check_overview_drift.sh` 校验。下次结构大改时更新本字段。

---

## 0. 摘要

### 0.1 体量（2026-06-05 对账 — `git ls-tree HEAD` 真实统计，1399 个已提交文件；收尾时点，别会话并行提交中可能微动）

| 顶级目录 | 文件数 | 占比 | 主要内容 |
|---|---|---|---|
| `99_archive/` | 639 | 46% | 归档物（5-26 晚段-4 加 `2026-05-26_teacher_web_vite实装作废/` 13 文件 = App.tsx + main.tsx + Shell.tsx + pages × 5 + store/auth.ts + vite_root_index.html + package.json + lock + vite.config.ts + tailwind.config.js + postcss.config.js + tsconfig × 2 — itsuki 拍板 Vite + TS 实装版整体废弃 + 5-26 晚加 `2026-05-26_ios_v1_demo_snapshot/` 42 文件（iOS demo 后门删除前快照） + 5-26 早 3 个 iOS 上架配置归位 + 5-22 加 2026-05-21_pre_fix + 2026-05-22_tomoshibi_appstore_fork 残余 + 5-21 teacher_web/demo 整组 158 文件归档 + 早期 GPT 对话 / throwaway iOS / demo 4-28 / 5-12 深夜大整理 / cloud agent 退役 / 5-02 handoff × 4 等）|
| `03_dev/` | 527 | 38% | 代码 + 设计 LOG（含未 commit iOS `APIErrorPresenter.swift` + `project.pbxproj.bak3_before_apierrorpresenter_register` 2 文件；5-27 早段-2 git mv `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` → 99_archive/2026-04-22_ios_round1_design_brief/；5-26 晚段-4 删除 Vite 实装 13 文件 → 全归档 → teacher_web 回到 Ryō standalone 主线）|
| `05_logs/` | 149 | 11% | raw 68（5-16/19/21/22/22-iOS/24/25/25-AC学习清单/26/26-dmsd-startup/26-vite废弃+polish回滚/27-teacher_web_v1.0_深夜推进/27-ios审查/27-全项目审查/27-anti-ai-flavor双层防御立项/27-整理inbox+8类升级/27-老师实名账户登录/27-ios登录注册大改+审批链进度条/28-ios_codex审查/28-注册页demo空+数字码+设计文档中文化/28-web登录页修复）/ AC_叙事 12 / dev_log / problem_solving / meta + audit_2026-05-19/（_session_prompts + _fixed_1-4 + 3 session findings + _master_issues）+ audit_2026-05-21_codex/ + audit_2026-05-22_codex/（5 类 jsonl + tsv + findings.md + json）|
| `00_admin/` | 25 | 1.8% | 8 顶级 md（5-29 加 项目心智模型.md）+ hooks 子目录 — 5-21 加 `系统bug专栏.md` + `codex_audit_prompt.md`（详见 §1.2）|
| `01_specs/` | 14 | 1.2% | 规格冻结区（含 5 .pages 不可读）|
| `.claude/` | 12 | 0.9% | 8 skill + 1 agent + 2 配置（settings / session-coord.config）— **5-26 加 `dmsd-startup/SKILL.md`**（启动 SOP 集中）/ 5-19 加 `.claude/agents/security-reviewer.md`（详见 §1.7.5）|
| `06_assets/` | 9 | 0.6% | 4 icon + 术语表.html + 学习内容清单.html + bus_schedule + bus_notice 真实样本 + app_screens_2026-06-05_ios/ |
| 根目录 | 8 | 0.6% | CLAUDE / README / CHANGELOG / LICENSE / .gitignore / .graphifyignore / PROJECT_GUIDE / start-teacher-web.command |
| `02_design/` | 4 | 0.3% | system_features + hardware + flow + NFC防代刷_后端立项施工计划 |
| `docs/` | 3 | 0.3% | Matt Pocock 套件 per-repo 配置（agents/{issue-tracker,triage-labels,domain}.md）|
| `bin/` | 3 | 0.3% | sync-check + create_local_dev_symlink + check_overview_drift（5-19 加）|
| `04_ops/` | 3 | 0.2% | MAC_MINI_SETUP + wifi_survey_howto + teacher_web_v1.0_上线部署清单 |
| `.github/` | 2 | 0.1% | workflows/test.yml（GitHub Actions CI 自动跑测试）+ dependabot.yml（依赖漏洞自动监控 — pip/gradle/actions 每周一）|
| **总计** | **1399** | 100% | |

> **占比读法**：归档 `99_archive/` + 代码 `03_dev/` 占 84%。日常开发的「活」文件主要在 `03_dev/`（代码）+ `00_admin/`（管理）+ `01_specs/`（规格）+ `02_design/`（设计）+ `.claude/`（AI 配置）。`99_archive/` 是历史归档区，按子目录粒度维护（见 §7），不逐文件追描述。

### 0.2 状态分布（2026-06-05 近似 — 总 1399）

| 类别 | 估算 | 说明 |
|---|---|---|
| 📦 归档 `99_archive/` | ~639 | 历史物，占 46%，日常不查 |
| ✅ 活跃代码 + 文档 | ~570 | `03_dev/` + `00_admin/` + `01_specs/` + `02_design/` + `.claude/`（含 teacher_web 130 + iOS/Android vendor 字体，第三方资源价值上算 archived）|
| 📝 日志记录 `05_logs/` | ~149 | raw + AC 叙事 + 审查报告，多数写过不改的历史 |
| ❓ 不可读（.pages / .docx / .510Z） | ~24 | 早期手稿，已被 .md 取代（清理需 itsuki 一次性确认，见 §11）|

> 精确逐文件状态需扫全 repo；本表按目录粒度近似。

### 0.3 五条关键发现

1. **第一次了解项目的入口已拆层**：`README.md` 负责 GitHub 门面；`PROJECT_GUIDE.md` 负责新人导览；本 skill 负责文件级地图。

2. **teacher_web 当前主线已明确**：6-05 从 HTML 单文件迁到 **React + TypeScript + Vite**（界面冻结原样搬，吸取 5-26 教训），当前权威源是 `03_dev/teacher_web/v1/src/` 下 React+TS（main/App/Shell/theme/utils/api(client.ts+types.ts)/components 26 .tsx），构建产物 `dist/`。旧 standalone HTML 已归档。

3. **后端 v1 已从 P0 骨架推进到 v1.0 功能补齐阶段**：25 个 router 覆盖全业务线（扣分 / 清扫 / 前台 / 外出 / 事案 / 指导 / 学年更新 / 巴士 / 行事 / WebSocket 等）；**防作弊核心后端仍未写**（§3.7）。

4. **iOS / Android / teacher_web / backend / 点呼机 5 端代码层都已启动**，但成熟度不同：backend 和 iOS 更靠前，Android 真后端接入与测试、点呼机真机模块仍待续。

5. **历史归档和当前主线必须分开读**：`99_archive/`、`05_logs/raw/`、`.pages` / `.docx` / `.510Z` 多数不是新人入口；找当前状态优先看 `WIP.md` + `项目心智模型.md`。

### 0.4 跨组横向洞察（详见 §8）

- **demo ↔ v1 复制策略**（2026-05-06 独立 repo 模式退役后）：backend 选了"重写"（schema 全新）✅；teacher_web 5-26 Vite 试做(重做新界面)被否决后回 standalone HTML，6-05 重新迁 Vite（这次界面冻结原样搬，成功）；iOS / Android 真代码全部在 DMSD 内（曾经的独立 repo + cloud agent 同步三件套已归档到 `99_archive/2026-05-06_cloud_agent_退役/`）。
- **五层 DESIGN_LOG 体系生效**：BACKEND / IOS / ANDROID / WEB 四端 DESIGN_LOG 都活跃且与 system_features.md 同步链清晰；2026-05-08 加点呼机 ROLLCALL_DEVICE_DESIGN_LOG 成第 5 个 — 是 4-29 大整理后的最大资产，5-08 收口。
- **AC 叙事供应充足**：80+ 条 #AC候选 + 6 个 per-version 叙事（v0.3-0.7）+ 4 个 problem_solving 精品版 + 3 个 03_dev/_DESIGN_LOG 工程化叙事 — 数量上远超 AC 自我推荐书所需。

---

## 1. 第 1 组：根目录 + 00_admin（30 文件 — 2026-05-29 加 项目心智模型.md / 2026-05-27 加 PROJECT_GUIDE.md，新人导览入口）

**统计**：✅ 22 / 📦 7 / ⚠️ 3 / ❓ 4

### 1.1 根目录（8 文件已提交）

| 文件 | 作用 | 状态 | 备注 |
|---|---|---|---|
| `.gitignore` | git 忽略规则（Python / Node / Android / IDE / 数据库本地） | ✅ | 当前完整 |
| `CLAUDE.md` | AI 项目指令权威源（每会话必读） | ✅ | 4-30 沟通规则 #6 升级 |
| `CHANGELOG.md` | 18 tag 全程 + 版本号单源真值 | ✅ | 教授会看 |
| `README.md` | 项目对外介绍（4-30 名字 Tomoshibi 定名） | ✅ | 4-29 起 GitHub public |
| `PROJECT_GUIDE.md` | 给第一次了解 / AI 深入理解整个项目的导览 — 项目是什么 / 5 端结构 / 系统怎么跑通 / 核心业务概念 + 规则数字速查 / 数据模型 / 关键决策 + 演化时间线 / AI 协作体系 / 阅读顺序。可单文件外发给无仓库的 AI 当「项目老师」用 | ✅ | 6-10 补外发场景（§4.5 规则数字 / §8.5 时间线 / §15 AI 协作体系）；6-05 扩成深度版 |
| `LICENSE` | All Rights Reserved + AC 后 4 方向评估 | ✅ | 不常改 |
| `.graphifyignore` | graphify 知识图谱忽略规则（防 vendor 字体污染图谱） | ✅ | |
| `start-teacher-web.command` | 双击一键：build Vite dist → 后端 8000 托管 dist 到 /teacher/ → 自动开浏览器 | ✅ | 6-08 中文名改英文名（原 `启动老师网站.command`，itsuki 嫌中文名蠢）；6-05 改成 Vite 版（原起前端 8787 托管 src 旧单文件）；6-08 重建 dev 库补 teacher.is_demo 列 + demo 账号 |

### 1.2 00_admin/AI 协作 + 项目治理（2026-05-22 校准 — 7 顶级 md + hooks 子目录，5-21 加 2 个长期治理文件）

| 文件 | 作用 | 状态 |
|---|---|---|
| ~~`文件结构指南.md`~~ | 所有文件清单 + 反向索引 | 📦 **2026-05-04 已归档到 `99_archive/2026-05-04_文件结构指南_已被项目文件总览取代/`** — 本 skill（project-overview）取代它 |
| `文档同步点清单.md` | 单源真值表 / 5 AC 核心问题 / 分阶段策略 | ✅ |
| ~~`版本管理SOP.md`~~ | 2026-05-04 整体迁入 `.claude/skills/version-bump/SKILL.md` | 📦 已归档到 `99_archive/2026-05-04_版本管理SOP_迁入skill/` |
| ~~`版本演变一览.md`~~ | 18 tag 故事线 | 📦 **5-13 commit 81842f4 已迁到 `05_logs/`**（见 §1.5）|
| `2026-04-19_项目审查_backlog.md` | 87 条漏洞清单（已大量 close） | 📦 |
| ~~`漏洞_剩余清单_2026-04-21.md`~~ | 28 条剩余精简索引 | 📦 **5-13 commit 81842f4 已迁到 `05_logs/`**（见 §1.5）|
| ~~`v0.4.0_S系列spec漏洞优先级分析.md`~~ | 已被"漏洞_剩余清单"吸收 | 📦 **5-13 commit 81842f4 已归档到 `99_archive/2026-05-12_深夜大整理/`**（见 §1.5）|
| `系统bug专栏.md` | **5-21 加** 131 条 v1.0 上线前 bug 集中管理（🔴 阻塞 43 / 🟡 该修 58 / 🟢 优化 30）— 由 5-19~5-21 三子代理审 + 主会话整理产出 / **5-22 加 Codex 第二轮 audit 段**（24 独立发现 + 13 复核 + 2 positive，共 39 条 / `audit_2026-05-22_codex/`）| ✅ |
| `codex_audit_prompt.md` | **5-21 加** Codex 第二轮 audit prompt 模板（27 必读文件 + 17 审查维度 + Claude 漏的 4 类重点）— 给 itsuki 喂 codex 用 | ✅ |

**实际剩余在 `00_admin/` 顶级**（2026-06-10 校准，10 md + `hooks/` 子目录 — progress_overview.md 当日退役移 99_archive）：`文档同步点清单.md` + `2026-04-19_项目审查_backlog.md` + `项目心智模型.md`（§1.3）+ `WIP.md` + `TODO.md` + `TODO_完成归档.md`（TODO 整段完成的段剪切归档，6-10 分层重组时建）+ `系统bug专栏.md` + `codex_audit_prompt.md` + `iOS_Android_对齐规格.md`（iOS↔Android 逐屏对齐规格）+ `iOS_Android对齐_GOAL提示词.md`（对齐会话的 /goal 提示词）+ `hooks/`（§1.6）。另有 `五端对齐_GOAL提示词.md` 未提交、`老师网页Vite迁移_GOAL提示词.md` 工作区已删。

### 1.3 00_admin/会话状态（4 文件 — 2026-05-29 加 项目心智模型 / 2026-05-13 progress_draft 归档）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `项目心智模型.md` | **2026-05-29 加** AI 开局必读骨架 — 系统怎么跑通 + 5 端各自现状 + 绑住 5 端的契约 + 核心不变量 + 当前未决问题 | ✅ | 由 dmsd-startup §2 Step 3 开局自动读 / session-wrap §7.5.1 项 12 收尾更新。不是文件清单（project-overview）/ 不是新人导览（PROJECT_GUIDE）/ 不是版本编年史（CHANGELOG）|
| `WIP.md` | 当下书签 — 记最近 5 次会话做了啥 / 当前焦点 / 多会话占用 / 阻塞项。CC 每次新会话必读全文 | ✅ | 短期记忆，跟 TODO 不重叠 |
| `TODO.md` | 所有未完成事项的完整清单（真值）— 2026-06-10 分层重组：§A v1.0 上线必做 / §B 不挡上线 / §C 长尾存疑 / §D 等拍板 | ✅ | 长期 backlog（待办池），CC 新会话扫顶部 200 行 |
| `TODO_完成归档.md` | **2026-06-10 加** TODO 分层重组时「整段全部完成」的段剪切到这（原文未改）| ✅ | 零散 ✅ 条目仍留 TODO.md 原位当证据 |
| ~~`progress_overview.md`~~ | （已退役 — 长期没人维护必然过期，进度叙事归 CHANGELOG 全版本一览 + PROJECT_GUIDE §8.5 时间线；活待办已提取 TODO §N+）| 📦 | → `99_archive/2026-06-10_progress_overview退役.md`（itsuki 6-10 拍板）|
| ~~`progress_overview_draft_2026-04-20.md`~~ | （已归档 — 4-20 draft 比 5-04 正文还旧）| 📦 | → `99_archive/2026-05-12_深夜大整理/`（5-13 commit 81842f4）|

### 1.4 05_logs/AC_叙事/（12 文件 — **2026-05-13 commit b37d065 从 00_admin/ 迁入**，Q3 拍板）

| 文件（现路径 `05_logs/AC_叙事/`） | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `v0.3.0_AC叙事.md` ~ `v0.8.0_AC叙事.md`（8 个含 v0.3.2）| 每个版本一份 AC 叙事素材 — 这版本做了啥 / 为啥这么做 / 跟 AC 4 维度怎么挂 | ✅ | **5-04 起新规则**：itsuki 自己写，CC 不主动起草。历史 v0.3-v0.8 的 7 个是 CC 起草保持不动 |
| `面试准备_索引.md` | 面试题库索引 — 6 大类 42+ 题（题目占位 / 回答留 iCloud） | ✅ | itsuki 出愿前练习用 |
| `原创设计_语音播报防作弊.md` | 语音播报防代刷的完整设计思路（自动贩卖机灵感 → 代刷观察 → 工程实装） | ✅ | ⭐ AC 最强素材之一 |
| `AC_志望動機_素材.md` | 志望理由书的素材框架 — 8 个核心问题留白等 itsuki 自填 | ⚠️ | 框架完整 / 内容 0/8 |
| `AC_提交_checklist.md` | 出愿前 6 个倒计时 gate（关卡）+ 月度回顾工作流 | ⚠️ | 5-10 起 |
| `Batch3_itsuki手笔素材指引.md` | 4 个已写好可直接粘贴（ready-to-paste）的 draft，等 itsuki 合并 | 📦 | 30-45min 工作量 |

### 1.5 00_admin/v0.4.0 spec draft + 管理文档（**2026-05-13 commit 81842f4 全分散到 7 个目的地**）

| 文件 → 新位置 | 原本干啥用 | 状态 |
|---|---|---|
| `v0.4.0_Device_Contract骨架.md` → `99_archive/2026-05-12_深夜大整理/` | 点呼机 device 跟 backend 通信契约的早期草稿（已融入 BACKEND_DESIGN_LOG） | 📦 已归档 |
| `v0.4.0_S2_S3_字段draft.md` → `99_archive/2026-05-12_深夜大整理/` | S2/S3 spec 段的字段草稿（已融入 FIELD_REGISTRY） | 📦 已归档 |
| `v0.4.0_S系列spec漏洞优先级分析.md` → `99_archive/2026-05-12_深夜大整理/` | S 系列 spec 找出的漏洞排优先级（已被「漏洞_剩余清单」吸收） | 📦 已归档 |
| `T2_iOS归档_dryrun评估.md` → `99_archive/2026-05-12_深夜大整理/` | iOS 归档执行前的试跑评估（已执行） | 📦 已归档 |
| `跨会话_ios_共享决策.md` → `99_archive/2026-05-12_深夜大整理/` | iOS 项目跨多会话同步的临时决策表（5-06 退役独立 repo 模式后失效） | 📦 已归档 |
| `wifi_survey_howto.md` → `04_ops/` | 宿舍 WiFi 信号实地调研的方法说明 | ✅ |
| `MAC_MINI_SETUP.md` → `04_ops/` | Mac mini 部署后端的步骤手册 | ✅ |
| `漏洞_剩余清单_2026-04-21.md` → `05_logs/` | 28 条还没修的 spec 漏洞索引 | ✅ |
| `版本演变一览.md` → `05_logs/` | 18 个 git tag 的故事线（每个 tag 当时做了啥） | ✅ |
| `术语表.html` → `06_assets/` | 180+ 词的可交互术语学习页面（itsuki AC 面试日语准备） | ✅ |
| `create_local_dev_symlink.sh` → `bin/` | VPS 上建本地 dev 软链接的脚本（VPS 已停用 / 脚本保留参考） | ✅ |

### 1.6 00_admin/hooks（12 hook + 1 库 + README = 14 文件 — **2026-05-19 校准 + 加 post-edit-format**）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `install.sh` | 把 `00_admin/hooks/` 注册成 git 的 hooks 目录（`git config core.hooksPath`） | ✅ | 首次 clone repo 后跑一次 / 不跑则后面 hook 不生效 |
| `pre-commit` | git commit 前自动检查 3 件事：版本号一致性 + bump 提醒 + 文件联动 | ✅ | 不通过会拦 commit |
| `post-commit` | git commit 后自动跑 graphify 增量更新代码图谱 | ✅ | 2026-05-11 加 |
| `post-checkout` | git 切分支后自动跑 graphify 重建图谱 | ✅ | 2026-05-11 加 |
| `post-edit-sync-check.sh` | CC 用 Write/Edit 改文件后，自动跑联动检查 + 扫 demo scaffold（demo 临时代码）字眼 | ✅ | 2026-05-04 加 |
| `post-edit-memory-check.sh` | CC 改 memory 目录后，提醒补 MEMORY.md 索引 | ✅ | 2026-05-04 加 / 5-13 修死链（路径 itsuki→kurekoduki）|
| `post-edit-japanese-comment-check.sh` | CC 改代码后，扫日语 hiragana/katakana 注释（中文铁律 — 注释必须中文） | ✅ | 2026-05-04 凌晨加 |
| `post-edit-timestamp-check.sh` | CC 改 WIP/TODO 等声明性文件后，检查「最后更新」时间戳是不是今天 | ✅ | 2026-05-04 凌晨加 |
| `post-edit-version-hardcode-check.sh` | CC 改声明性文件时实时拦版本号硬编码（比 pre-commit 早一步发现） | ✅ | 2026-05-04 凌晨加 |
| `post-edit-project-overview-check.sh` | CC 改任何 DMSD 文件后，提醒同步本 project-overview skill — 防加文件没补 / 删文件没去 / 描述漂移 | ✅ | 2026-05-13 itsuki 怒怼后加 / **2026-05-19 改全项目覆盖**（原白名单漏 routers / Android / Features 等 → 5-19 对账发现 9 处漂移后扩范围） |
| `pre-bash-destructive-block.sh` | CC 跑 Bash 前拦危险命令（`rm -rf` 非临时 / `git push --force` / `git branch -D`） | ✅ warn 模式 | 2026-05-04 加 / 5-12 改 warn 不阻断 |
| `post-edit-format.sh` | CC 改代码后按扩展名分发自动格式化（`.py`→ruff / `.swift`→swiftformat / `.kt`→ktlint / `.ts/.tsx/.js/.jsx/.vue/.css/.scss/.html/.json`→prettier）| ✅ | **2026-05-19 加 — claude-code-setup 推荐器落地 4 件之一** / 工具未装静默 skip / 跟 japanese-comment 并行串行跑会拖 2-4 秒 |
| `lib/sync-rules.sh` | 19 条文件联动规则的代码版 — pre-commit + sync-check.sh 都调它 | ✅ | 5-16 重 grep `^add_rule` 验证 = 19 条真实数 |
| `README.md` | hooks 目录总说明（3 类 hook 全覆盖：git pre-commit + git post-commit/checkout + CC PostToolUse 6 + CC PreToolUse 1） | ✅ | 改 hook 必同步 |

### 1.7 .claude/skills（9 skill — 2026-06-04 加 codex-review）

| skill | 一句话作用 | 触发关键词 | 状态 |
|---|---|---|---|
| `dmsd-startup/` | 会话启动 SOP — §2 5 件必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）+ §4 按需触发的事（找文件查 project-overview / TODO 主动问才读 / WIP vs TODO 铁律 / 文件联动走 file-linkage） | always-on（每次会话启动 CC 主动 Read） | ✅ **2026-05-26 加** |
| `session-wrap/` | 会话收尾流程 — §5.5 共 16 节子流程（全量扫描 / AC dump / 中文总结 / 文件联动 / WIP+TODO 刷新 / git commit / git 状态确认 / 跨 repo / memory 维护 / daily-archive iCloud 备份 §5.5.14 / decision-draft 决策日志草稿起草 §5.5.15）| 收尾 / 整理今天 / 总结今天 | ✅ |
| `version-bump/` | 版本号决策树（CC 有否决权）+ 发版动作 SOP（git tag / CHANGELOG / push） | 迭代 / bump / 发版本 / 发版 | ✅ |
| `file-linkage/` | 文件联动矩阵 — 改 A 必查 B（19 条规则） | 联动 / 改 A 要查 B | ✅ |
| `project-overview/` | 项目所有文件清单 — 每个文件干啥 + 状态（本 skill） | X 文件在哪 / X 文件干嘛 / 找文件 | ✅ |
| `memory-write/` | 写 memory 文件的 SOP（4 类型 / 查重 / 索引同步） | 记一下规则 / 以后这样 / memory 加一条 | ✅ |
| `new-feature/` | 加新功能时 4 端实装模板（spec → backend → iOS → Android）+ 字段对齐自检 | 新功能 X / 加 Y / 实装 Z | ✅ |
| `spec-sync/` | 跨端字段对齐检查 — backend ↔ iOS ↔ Android 字段提取对比 | 跨端检查 / 字段对齐 | ✅ |
| `codex-review/` | codex 审查循环编排 — 派 codex（gpt-5.5 xhigh）只读审本会话改动 → CC 逐条裁决 + 修 → 复审 → 跑到收敛（须带「codex」字样触发）| codex 审查 / 派 codex 审 / codex 挑刺 / codex 找 bug | ✅ **2026-06-04 加** |

> **2026-05-04 调整记录**：原计划 10 skill，itsuki 反问后砍 3：
> - ~~`session-start` 删（内容并入 `session-wrap §5.5.9` 收尾段；启动只读 WIP）~~ — **2026-05-26 恢复**，改名 `dmsd-startup/`，集中启动逻辑（原全局 `session-start-coord-check.sh` 挂钩 + `bin/check_overview_drift.sh` 调用 + CLAUDE.md「会话开始」段）
> - `demo-clean` 删（一次性任务做 skill 频次太低；改成 `lib/sync-rules.sh` demo-scaffold-detect 自动检测 + `system_features.md` 末尾清单）
> - `release-checklist` 删（合并到 `version-bump §13`；本来就串联，分两个 skill 反而割裂）

### 1.7.4 .claude/ 配置文件（2 个 — **2026-05-22 补漏列**）

| 文件 | 一句话作用 | 状态 |
|---|---|---|
| `settings.json` | Claude Code DMSD 项目级配置 — 注册 hooks（SessionStart 跑 check_overview_drift / PostToolUse 跑 sync-check + format / UserPromptSubmit 跑 anti-ai-flavor 提醒 / 等）| ✅ |
| `session-coord.config.json` | session-coord skill 协作板配置 — 列哪些文件 strict_lock（CLAUDE.md / CHANGELOG / spec 主体 + 字典 4 件）/ advisory_lock（WIP / TODO / 5 DESIGN_LOG / system_features / 文档同步点清单）。**2026-05-22 修 FC-003**：原锁清单引用已废文件名 `RollCall_Spec_v0.1.md` + `dictionary_v0.1_v0.2_v0.3.md`，改成 `RollCall_Spec.md` + 4 个字典文件真名 | ✅ |

### 1.7.5 .claude/agents（1 subagent — **2026-05-19 新建**）

DMSD 项目级 subagent（子代理 — CC 派出去做独立任务的小弟）。

| agent | 一句话作用 | 触发场景 | 状态 |
|---|---|---|---|
| `security-reviewer.md` | DMSD 专用安全审查 — 鉴权 / 输入验证 / 密钥管理 / 权限提升 / 防作弊（NFC nonce / ECDSA / 学生注册码 / 老师权限边界）+ OWASP Top 10 通用清单。只审不改 — 出报告由主 CC 改 | itsuki 说「安全审查 X / 审一下 auth.py / 漏洞扫描 / 上线前过一遍」/ 改完鉴权 / 密钥 / NFC 验签相关代码 / v1.0 上线前最后 gate | ✅ |

**2026-05-19 新建背景**：itsuki 跑 claude-code-setup 推荐器后拍板的 4 件落地之一（同批：context7 MCP / GitHub MCP / 全局已装 / `post-edit-format.sh` hook）。**项目级**专属理由：DMSD 防作弊机制（NFC ST25DV16K + 10 秒 nonce + ECDSA + 学生注册码 + 老师班级隔离）有特定上下文，通用 reviewer 抓不准。Tango 后端真需要时再写一个全局通用版（不复用 DMSD 版）。

### 1.7.6 全局配置改动一览（**2026-05-19 同日装的全局基础设施 — 不在 DMSD 项目内但 DMSD 用得到**）

> 本节列**不在 DMSD 项目内**但跟 DMSD 工作流相关的全局改动 — 为了让未来的 CC 会话 / itsuki 知道这些存在。物理位置全在 `~/.claude/` 或 `~/.claude.json`，git 不跟踪。

| 改动 | 物理位置 | 干啥 | DMSD 用途 |
|---|---|---|---|
| **context7 MCP server** | `~/.claude.json` 用户级 mcpServers | 实时拉开源库（FastAPI / SwiftUI / Kotlin / Tailwind）最新文档 | 5 端不同栈，CC 查最新 API 写法不靠训练数据 |
| **GitHub MCP server** | `~/.claude.json` 用户级 mcpServers + PAT 凭证 | CC 通过 MCP 管 issues / PR / actions / releases | 跨项目都用得到（DMSD / Tango / SC26 都在 otogi2025 GitHub 账号）/ DMSD 当前用 TODO.md 不用 GitHub Issues，主要是未来 PR 流程时用 |
| **docx / xlsx / pptx / pdf** | `~/.claude/skills/{docx,xlsx,pptx,pdf}/` | Anthropic 官方 4 个文档生成 skill — 创建 / 读取 / 编辑 Word / Excel / PowerPoint / PDF | AC 出愿 PDF 备用（itsuki 当前用 Pages.app，留作未来需要时直接可用） |
| **多语言格式化工具** | `/opt/homebrew/bin/{ruff,swiftformat,ktlint}` + `~/.npm-global/bin/prettier` | 系统装的工具 — 给 `post-edit-format.sh` hook 调用 | 4 端都用得到 |

> **跨项目可见性**：context7 + GitHub MCP + 4 个 doc skill 是**全局**配置，Tango / SC26 等其他项目的 CC 会话也能用。但 `security-reviewer` + `post-edit-format.sh` 是 **DMSD 项目级**，只在 DMSD 内生效。

---

### 1.8 主目录非编号目录 + 隐藏文件（**2026-05-13 itsuki 反馈后新增**）

> **背景**：itsuki 5-13 反映"docs 没编号为啥在主目录"。本节列清楚所有非编号目录 / 隐藏文件 — 为啥它们不归编号目录 + 哪些进 git / 哪些 .gitignore 排除。

#### 1.8.1 进 git 的非编号目录（3 个）

| 目录 | 文件数 | 为啥不编号 | 备注 |
|---|---|---|---|
| `.claude/` | 23 | Claude Code 配置 — 跨项目共享惯例（`.claude/skills/` / `.claude/settings.json` / `.claude/scheduled_tasks.lock`）| `.claude/sessions/` + `.claude/settings.local.json` .gitignore 排除 |
| `bin/` | 3 | 可执行脚本 — Unix 惯例 | `bin/sync-check.sh`（联动检查工具）+ `bin/create_local_dev_symlink.sh`（5-13 从 00_admin/ 迁入）+ `bin/check_overview_drift.sh`（5-19 加 — project-overview 启动对账） |
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

#### 1.8.3 主目录顶层文件（7 项）

| 文件 | 用途 |
|---|---|
| `CHANGELOG.md` | 版本号单源真值（教授会看）|
| `CLAUDE.md` | AI 项目指令权威源（每会话必读）|
| `README.md` | 项目对外介绍（GitHub public，教授会看）|
| `PROJECT_GUIDE.md` | 新人导览入口（第一次了解项目先读这里）|
| `LICENSE` | All Rights Reserved + AC 后 4 方向评估 |
| `.gitignore` | git 忽略规则（含上面所有 .gitignore 排除项）|
| `.graphifyignore` | graphify 忽略规则（防 vendor 字体污染图谱）|

#### 1.8.4 关键 takeaway（itsuki 关注的）

1. **"我 ls 看到非编号目录乱"真相** = 物理文件存在但大部分 .gitignore 排除（`.beads/ / .scratch/ / graphify-out/ / .DS_Store / .venv/`）→ git 看不到 / GitHub 看不到 / 教授看不到
2. **真进 git 的非编号目录只有 3 个**：`.claude/`（CC 配置）/ `bin/`（脚本）/ `docs/`（外部 skill 配置）— 都是工具类，按惯例不编号
3. **docs/ 不是 itsuki 看的** — DMSD 自己的文档全在编号目录（00-99），docs/ 是给 Matt Pocock skill 读的

---

## 2. 第 2 组：01_specs + 02_design（17 文件 — 6-09：+3 范围冻结规格 +1 v1.0 验收脚本、-5 早期 .pages 全归档到 99_archive）

**统计**：✅ 17 / ⚠️ 1 / ❓ 0（早期 .pages 已全部归档）

### 2.1 01_specs/ 顶级（7 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `v0.1完整计划.pdf` | v0.1 版本的 10 部完整规划（项目顶层蓝图） | ✅ | PDF 可读 / AC 答辩用 |
| `API_CONVENTIONS.md` | backend API 的命名规范 + 错误码体系（URL 路由 / HTTP 动词 / 错误码） | ✅ | 通用约定有效；§2/§8 URL 命名已跟实际代码漂移 |
| `teacher_web_v1.0_backend_models_propose.md` | teacher_web v1.0 要的后端数据模型提案 — discipline/cleaning/front_desk 三表字段 | ⚠️ | 一次性提案、内容已实装；候选归档 |
| `v1.0_范围冻结决策.md` | ⭐ 产品 v1.0 范围冻结 — 纳入功能 / 范围决策 / 排除项 / 验收 / 各端任务 | ✅ | 6-09 itsuki 拍板三波切分后定稿 |
| `v1.0_验收脚本.md` | v1.0 上线前人工验收测试用例集（替代失效的 v0.1 验收脚本）| ✅ | 6-09 重写 |
| `v1.1_范围冻结决策.md` | 产品 v1.1 范围冻结 — 点呼签到 + 卡 + 点呼终端 + 防作弊（硬件就绪触发）| ✅ | 6-09 定范围，硬件就绪启动 |
| `v1.2_范围冻结决策.md` | 产品 v1.2+ 候选池 — 紧急警报 / 暗色 / 在线学习 / 出租车 Android / FCM（非冻结，待拍板升格）| ✅ | 6-09 归集 |

### 2.2 01_specs/rollcall/（6 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `RollCall_Spec.md` | 点呼系统的核心规格文档（v0.3.0 主体）— 所有点呼相关规则的权威源 | ✅ | 4-29 修订 5 处（§4.2 / §5.2 / §5.4 / §5.5 / §5.6） |
| `ENUM_REGISTRY.md` | 点呼相关 15 种枚举值定义（出席状态 / 役职 / 申请类型等） | ✅ | 跨端字段对齐参考 |
| `FIELD_REGISTRY.md` | 点呼相关字段统一登记表 + 禁止使用的字段名单 | ✅ | 4-22 增补 |
| `DEVICE_REGISTRY.md` | 点呼机设备字段登记（含 `device_retired_at` 永久注销字段） | ✅ | backend models 对齐参考 |
| `ERROR_CODES.md` | backend 返回客户端的 12 个错误码定义 | ✅ | 与 API_CONVENTIONS 对齐 |
| `v0.1_冻结决策.md` | v0.1 阶段冻结时拍板的决策快照 | ⚠️ | 4-29 阈值再冻结后 ~10 处文档已修 / 本文角色（备份 vs 历史快照）需明确 |

### 2.3 02_design/（4 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `system_features.md` | ⭐ 5 端（iOS / Android / 后端 / teacher_web / 点呼机）共用的功能规格真值 | ✅ | 4-30 轨道 ABC 同日完成（覆盖老师 38 条反馈） |
| `hardware_design.md` | 点呼机硬件选型 + 接线设计（Pi 3A+ 选型 + 砍 Pi 4B 的论证） | ✅ | 跟 `03_dev/rollcall_device/` 软件层互补 / AC 素材 |
| `flow_design.md` | 学生点呼的 3 种流程图（路径 A 刷卡 / 路径 B iOS 自助 / 路径 B Android 自助） | ✅ | 视觉流程图参考 |
| `NFC防代刷_后端立项施工计划.md` | NFC 防代刷后端实装的立项施工计划 — 对应「全项目最大未完成块」防作弊核心后端 | ✅ | 设备注册校验 + 卡→学生映射 + 传输安全 |

---

## 3. 第 3 组：03_dev/backend（104 文件 — 2026-06-05 校准 62→104）

**统计**：v1 92（routers 26 + services 5 + tests 20 + alembic 22 + app 核心 9 + 配置 ~10）+ demo 10 锁定 + 顶层 2（README + BACKEND_DESIGN_LOG）= 104
**核心**：v1 功能大幅扩张 — 6-05 已有 25 router / 19 test / 18 迁移；扣分 / 清扫 / 前台 / 外出 / 事案 / 指导 / 学年更新等 §7 全业务线后端已实装。**防作弊核心后端仍未写**（见 §3.7）

### 3.1 backend 顶层 + demo（13 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `backend/README.md` | backend 目录总说明 — demo 跟 v1 怎么分工 | ✅ | 新会话看 backend 时先读 |
| `backend/BACKEND_DESIGN_LOG.md` | ⭐ backend 的 12 章设计决策权威源（D1-D12 所有拍板理由） | ✅ | 改 backend 业务代码前必查 |
| `backend/demo/`（10 文件）| 4-28 demo day 现场跑的 backend 骨架代码 | 📦 | 全部锁定不动 / `db_schema.sql` 价值最低（v1 改用 SQLAlchemy declarative ORM） |

### 3.2 backend/v1/ 配置层（5 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `.env.example` | 环境变量模板（35 个 — DB 连接 / JWT 密钥 / SendGrid 邮件 / CORS 跨域）| ✅ | 部署时 copy 成 .env 填真值 |
| `requirements.txt` | Python 依赖清单（14 个包 — sendgrid 邮件 / openpyxl Excel 读写 / pytest 测试 / psycopg PostgreSQL 驱动）| ✅ | `pip install -r requirements.txt` |
| `README.md` | backend v1 启动手册（5 步启动 + 烟雾测试） | ✅ | 新机器部署看这个 |
| `seed.py` | 数据库初始化脚本 — 灌种子数据（教师 8 角色 + 班主任 + 学生 2 人含留学生）| ✅ | 空库启动后跑一次 |
| `.gitignore` | git 忽略规则（保护 .env 密钥不进 git / 排除 venv 虚拟环境） | ✅ | 防泄漏关键文件 |

### 3.3 backend/v1/app/ 核心（9 文件 — app 顶级，不含 routers/services 子目录）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `__init__.py` | Python 包声明（让 app/ 成 Python 包） | ✅ | 范式标准 |
| `database.py` | 数据库连接 + session 管理（SQLAlchemy 引擎初始化） | ✅ | 范式标准 |
| `deps.py` | FastAPI 依赖注入（含 5-27 加的 `dorm_units_for_teacher` R4 helper — 男寮 = unit 1+2 / 女寮 = unit 4 / 跨寮 4 类 = None） | ✅ | 范式标准 |
| `security.py` | JWT 令牌生成 + 密码哈希 + 认证中间件 | ✅ | 范式标准 |
| `main.py` | FastAPI 应用入口 — 注册路由 + 中间件 + 启动 hook | ✅ | uvicorn 启动这个 |
| `config.py` | 配置加载（读 .env → Pydantic Settings） | ✅ | 范式标准 |
| `models.py` | 数据库 20+ 张表的 ORM 定义（含 5-27 加的 DemeritEvent / FrontDeskItem 等 P1/P2 表；CleaningAssignment 6-10 随清扫功能删） | ⚠️ | 对应 router 部分缺 / 建议在 docstring 标 P0/P1/P2 优先级 |
| `schemas.py` | API 请求/响应的 Pydantic 数据校验定义（含 discriminated union — 按字段值分流校验）| ✅ | iOS / Android 字段对齐参考 |
| `ws_manager.py` | **2026-05-27 加** — WebSocket 老师端连接管理单例（TeacherConnectionManager / asyncio.Lock / broadcast_sync 同步触发） | ✅ | 单进程 in-memory v1.0 / 多进程后期换 Redis pub/sub |

### 3.4 backend/v1/app/routers/（26 文件 = __init__ + 25 router — 2026-06-05 校准 11→26）

> 按业务线分组。⚠️ = 有未完成块。

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `__init__.py` | Python 包声明 | ✅ | 空文件 |
| `auth.py` | 登录认证 — 学生 + 教师登录 / JWT 令牌签发 | ✅ | P0 |
| `accounts.py` | 学生账号自助（注册 / 密码重置） | ✅ | 缺 DELETE /accounts/me（Apple 5.1.1(v) 强制） |
| `admin_accounts.py` | 学生账号 admin 端 — 寮务管理角色管账号 | ✅ | 6 月新增 |
| `admin_registration_code.py` | 管理员发学生注册码（刷新 / 查当前 / 查历史） | ✅ | |
| `teachers.py` | 教师管理（CRUD + 邀请 token 发放） | ✅ | |
| `rollcall.py` | 点呼 NFC 刷卡 — 学生刷卡后记出席 | ⚠️ | 防作弊核心未真接（暂用老师令牌 + 手传 student_id） |
| `study.py` | 学習担当 NFC — 学習区 3 tap 状态机 + 欠席届 + 出席统计 | ⚠️ | 5-12 挂载 |
| `study_online.py` | 在线学习申请 — 学生提交 / 老师审批取消 | ✅ | 6 月新增 |
| `applications.py` | 外泊 / 帰省 / 帰国 申请（提交 / 邮件 / 履历 / 详情） | ⚠️ | 缺 #10-#13 役职审批 endpoint |
| `outings.py` | 当天回寮短时外出（单一老师确认）— 6 接口 | ✅ | 6-04 建 + R4 寮边界 + 19 测试 |
| `dorm_life.py` | 宿舍生活类申请 4 种 — 行事企画 / 日课变更 / 冷蔵庫購入 / 物品所持 | ✅ | 6 月新增 |
| `discipline.py` | 扣分 / 規律処分 — 月排名 + 阈值标记 + 手动加扣分 | ✅ | 5-27 加（DisciplinePage 接后端核心） |
| ~~`cleaning.py`~~ | 🚫 清扫功能全 5 端删除（itsuki 2026-06-10 拍板）— 文件 + cleaning_assignment 表 + 4 点罚扫已删 | — | 5-27 加 / 6-10 删 |
| `front_desk.py` | 前台 — 宅配 + 失物招领登记 / 通知学生 | ✅ | 5-27 加 |
| `guidance.py` | 指导履历录入 + 学生开示申请 | ✅ | 6 月新增（§7.9/§7.10） |
| `incidents.py` | 事案录入 — 老师录 / 查 / 编辑 | ✅ | 6 月新增（§7.9） |
| `student_profile.py` | 学生档案聚合页 — 一次返回各维度履历 | ✅ | 老师全看 / 学生只看自己 |
| `student_promote.py` | 学年更新「开闸」— 老师每年 4 月点一次发通知 | ✅ | 6-05 学生自设方案（§4.2） |
| `announcements.py` | 老师公告（list / detail / replies / reads 9 endpoint） | ✅ | |
| `meals.py` | 食堂用餐统计 — JSON 或 Excel（openpyxl） | ✅ | P0 |
| `events.py` | 行事予定 — 列 / 新建 / 编辑 / 删（老师 + 学生可看） | ✅ | 6 月新增 |
| `bus_routes.py` | 巴士时刻表 — 老师都可看 / 役职可改 | ✅ | 6 月新增（§7.6） |
| `notifications.py` | 推送通知 — 走 SendGrid 邮件 | ✅ | |
| `device_tokens.py` | 设备推送令牌 — App 启动注册本机令牌（幂等） | ✅ | 6 月新增（§7.13） |
| `ws.py` | WebSocket — 老师端实时事件流（点呼 / 申请推送 → LiveRollCall 实时刷座席） | ✅ | 6 月新增 |

### 3.5 backend/v1/app/services/（5 文件 — 6-05 加 push.py）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `__init__.py` | Python 包声明 | ✅ | 空文件 |
| `meals.py` | 食堂用餐业务逻辑（router 之外的纯业务函数） | ✅ | P0 完整 |
| `approval_chain.py` | 申请审批链业务逻辑 — 按申请类型决定要哪几个老师审 | ⚠️ | 外泊 chain 已确定 / 帰省 + 帰国 chain 是暫定值（待 itsuki 见老师补 4 张实物表） |
| `email.py` | 发邮件业务逻辑（包 SendGrid SDK） | ⚠️ | 90% 完整 / 缺 retry 3 次循环（设计要求） |
| `push.py` | 推送通知业务逻辑（设备令牌 → 推送） | ✅ | 配 `device_tokens.py` 路由 |

### 3.6 backend/v1/tests/（20 文件 — 2026-06-05 校准 5→20）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `__init__.py` | Python 包声明 | ✅ | 空文件 |
| `conftest.py` | pytest 公共 fixture（DB 测试库 / test client 等） | ✅ | 范式标准 |
| `test_smoke.py` | P0 关键路径冒烟测试 — 17 个测试用例 | ✅ | 跑这个验主流程 |
| `test_announcements.py` | 公告 API 的测试 | ✅ | 5-03 启 |
| `test_demo_reviewer.py` | Apple 审核员 demo 账号的测试 | ✅ | 5-08 拍板 |
| `test_registration_code.py` | 注册码 API 测试（/refresh / /current / /history） | ✅ | 5-03 启 |
| `test_admin_accounts.py` | admin 端学生账号管理测试 | ✅ | |
| `test_applications.py` | 外泊 / 帰省 / 帰国 申请测试 | ✅ | |
| `test_outings.py` | 外出申请 + R4 寮边界测试（19 用例） | ✅ | 6-04 |
| `test_study.py` | 学習担当 NFC 状态机测试 | ✅ | |
| `test_study_online.py` | 在线学习申请审批测试 | ✅ | |
| `test_rollcall.py` | 点呼刷卡记出席测试 | ✅ | |
| `test_events_and_bus.py` | 行事予定 + 巴士时刻表测试 | ✅ | |
| `test_guidance_and_incidents.py` | 指导履历 + 事案录入测试 | ✅ | |
| `test_student_profile_and_promote.py` | 学生档案聚合 + 学年更新测试 | ✅ | |
| `test_push.py` | 推送通知 + 设备令牌测试 | ✅ | |
| `test_email_resend.py` | 邮件重发测试 | ✅ | |
| `test_dorm_boundary_fixes.py` | 寮边界判定回归测试（IX-014 类 bug 防回归） | ✅ | |
| `test_security_fixes.py` | 安全修复回归测试 | ✅ | |
| `test_front_desk.py` | 前台（宅配 / 失物）测试 | ✅ | 6-05 别会话加 |

> 测试文件从 5 涨到 19，覆盖 6 月新增的全部业务线。具体 test case 数 + 覆盖率需跑 `pytest` 实测（BACKEND_DESIGN_LOG §8 目标 70%）。

### 3.6.5 backend/v1/alembic/（22 文件 = 4 框架 + 18 迁移脚本 — 2026-06-05 校准 9→22）

> Alembic = Python 数据库迁移工具，让 schema 变化有版本记录。每次改 `models.py` 字段都要生成一个 versions/*.py 迁移脚本。

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `alembic.ini` | Alembic 配置文件（DB 连接 / 脚本位置） | ✅ | 在 v1/ 顶级不在 alembic/ 子目录 |
| `alembic/env.py` | Alembic 启动入口（连 DB / 注册 models / 跑迁移） | ✅ | 范式标准 |
| `alembic/script.py.mako` | 生成迁移脚本的模板 | ✅ | 范式标准 |
| `alembic/README` | Alembic 默认 README | ✅ | 范式标准 |
| `alembic/versions/7a15771bdc7b_*.py` | 加 study / rollcall / teacher 三张表 | ✅ | 5-12 加 |
| `alembic/versions/b2c3d4e5f6a7_*.py` | 对齐 application schema 字段 | ✅ | |
| `alembic/versions/c3d4e5f6a7b8_*.py` | 加 study absence period（学習欠席届时段） | ✅ | |
| `alembic/versions/d4e5f6a7b8c9_*.py` | 加学生注册码表 | ✅ | 5-03 |
| `alembic/versions/e5f6a7b8c9d0_*.py` | 加公告表 | ✅ | 5-03 |
| `alembic/versions/f6a7b8c9d0e1_*.py` | 加 demo reviewer 标志位（Apple 审核员账号） | ✅ | 5-08 |
| `alembic/versions/e1f2a3b4c5d6_add_outings*.py` | 加 outings 外出申请表（单一老师确认） | ✅ | 6-04 |
| `versions/d2e3f4a5b6c7_add_dorm_application_forms*.py` | 加宿舍生活类申请 4 表 | ✅ | 5-28 |
| `versions/a1b2c3d4e5f6_add_device_tokens*.py` | 加设备推送令牌表 | ✅ | 5-30 |
| `versions/a1b2c3d4e5f6_device_token_unique_index.py` | 设备令牌唯一索引（防重复注册） | ✅ | |
| `versions/e3f4a5b6c7d8_add_events_and_bus_routes*.py` | 加行事予定 + 巴士时刻表 | ✅ | 5-30 |
| `versions/f7a8b9c0d1e2_add_guidance_and_incidents*.py` | 加指导履历 + 事案表 | ✅ | 5-30 |
| `versions/c1d2e3f4a5b6_add_demerit_cleaning_frontdesk.py` | 加扣分 + 清扫 + 前台 3 表 | ✅ | 5-27 |
| `versions/a7b8c9d0e1f2_add_taxi_reservation_time*.py` | 加 taxi 预约时间字段 | ✅ | 6-03 |
| `versions/c9d0e1f2a3b4_add_contract_file_to_study_online*.py` | 在线学习申请加合同文件字段 | ✅ | 6-04 |
| `versions/a8b9c0d1e2f3_add_rce_idempotency_unique.py` | 注册码兑换幂等唯一约束 | ✅ | |
| `versions/b9c0d1e2f3a4_remove_applied_group.py` | 删废弃的 applied_group 字段 | ✅ | |
| `versions/f8a9b0c1d2e3_add_needs_renewal*.py` | 加 needs_renewal 学年更新标记字段 | ✅ | 6-05 |

### 3.7 v1 剩余缺块（2026-06-05 校准）

> 6 月已补：rollcall / study router 挂载 + 扣分 / 清扫 / 前台 / 外出 / 事案 / 指导 / 学年更新 / 巴士 / 行事等全业务线。仍缺：

1. **防作弊核心后端**（全项目最大缺口）— 设备注册校验 + 卡→学生映射（`Student.card_uid` 字段 + cards 表 + UNIQUE 索引 + admin_cards 路由）+ 点呼机↔后端传输安全。当前签到暂用老师令牌 + 手传 `student_id`。施工计划见 `02_design/NFC防代刷_后端立项施工计划.md`。
2. `routers/applications.py` 加役职审批 endpoint（#10-#13）+ 撤回（`DELETE /{id}`）。
3. `routers/accounts.py` 加 `DELETE /accounts/me`（Apple 5.1.1(v) 强制 / BACKEND_DESIGN_LOG §5.1.6 已 spec）。
4. `services/email.py` 补 retry 3 次循环。

---

## 4. 第 4 组：03_dev/teacher_web（177 文件 — 2026-06-05 校准，当前主线 = React + TypeScript + Vite）

**统计**：顶级 2（DESIGN_BRIEF + WEB_DESIGN_LOG）+ v1 175（其中 src/_assets 字体 130）。
**核心状态**：6-05 从「HTML 单文件 + 浏览器内 Babel 编译」**迁到 React 18 + TypeScript + Vite** 正规工程（界面 100% 冻结原样搬，吸取 5-26 失败教训）。chrome 客观实测 17 页全渲染 + 27 接口全 200 + 真数据通；仅剩 itsuki 肉眼签收 + push。旧单文件版归档到 `99_archive/2026-06-05_teacher_web_html单文件版归档/`。注：5-26 那次早期 Vite 试做（重做新界面被否决）归档在 `99_archive/2026-05-26_teacher_web_vite实装作废/`，跟本次是两回事。

### 4.1 顶层（2 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `DESIGN_BRIEF.md` | teacher_web 给设计师的需求简报 + 实装跟踪 | ✅ | Round 2/3 handoff |
| `WEB_DESIGN_LOG.md` | ⭐ teacher_web 设计决策权威源（16 项时间线含 §16 Vite 迁移 + Tomoshibi 命名 + Ryo 涼配色方案） | ✅ | 改 teacher_web 业务代码前必查 |

### 4.2 demo/（已归档）

5-21 teacher_web demo 整组 158 文件已挪到 `99_archive/2026-05-21_teacher_web_demo_archived/`。当前 `03_dev/teacher_web/` 下不再保留 `demo/` 主线目录。

### 4.3 v1/（175 文件 — React + TypeScript + Vite 主线）

> **6-05 校准**：迁到 Vite 正规工程。入口是根 `index.html`(引 /src/main.tsx)；源码全在 `src/` 下 React+TS；构建产物 `dist/` 已 gitignore（不提交，启动脚本现 build）。旧 standalone HTML 运行链(index.html 29629 行 + client.js + vendor + 打包脚本)已整体归档。

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `README.md` | v1 启动说明 | ✅ | 新会话看 teacher_web 先读（⚠️ 可能仍描述旧 standalone 链，待核） |
| `index.html` | Vite 入口（14 行，引 `/src/main.tsx`） | ✅ | 根目录，不是 src 下 |
| `package.json` / `package-lock.json` | 依赖 + 脚本（build = `tsc --noEmit && vite build`） | ✅ | React18 + Vite6 + TS5 |
| `vite.config.ts` | Vite 配置（`base:"./"` + proxy /api→8000 + `resolve.extensions` .ts 优先） | ✅ | |
| `tsconfig.json` | TypeScript 配置 | ✅ | |
| `src/main.tsx` | 挂载入口（render App + 引 fonts.css/styles.css） | ✅ | |
| `src/App.tsx` | 鉴权状态 + 路由 switch（角色门控前的总枢纽） | ✅ | |
| `src/Shell.tsx` | 侧栏 17 菜单 + 角色门控 + 顶栏搜索 | ✅ | |
| `src/theme.ts` | RYO 配色 + 常量 + dormLabel + `API_BASE="/api/v1"` | ✅ | `window.RYO` 迁来 |
| `src/utils.ts` | 4 个 JST 日本时间助手（跨页共用） | ✅ | |
| `src/api/client.ts` | 60+ 接口方法（rollcall/discipline/front_desk/announcements 等；cleaning 6-10 删） | ✅ | 旧 `client.js` 拆来，有 export |
| `src/api/types.ts` | 50+ 后端类型，对齐 `backend/app/schemas.py` | ✅ | |
| `src/components/*.tsx`（26 文件）| 22 页 + 3 弹窗(OverrideModal/OutstayDetailModal/StudentProfileModal) + `shared.tsx`(公共组件) | ✅ | window.XxxPage 迁来 |
| `src/components/RollCallLanding.tsx` | 点呼默认页 | ⚠️ | 统计卡/趋势图/最近セッション是原样搬的硬编码 demo 数据(带「DEMO」标记)，是否接真后端待 itsuki 拍 |
| `src/fonts.css` + `src/styles.css` | 全局字体(@font-face 引 _assets) + 样式 | ✅ | |
| `src/_assets/`（130 .woff2）| Noto Sans JP 等字体文件 | ✅ | fonts.css 引用，Vite 构建打进 dist |
| `src/assets/tomoshibi-icon.png` | 灯火图标 | ✅ | |
| `src/vite-env.d.ts` | Vite 类型声明（.png import 等） | ✅ | |

**当前 v1.0 推进重点**：
1. itsuki 肉眼签收界面跟旧版一致 → push（CC 不自动 push）
2. RollCallLanding 的 demo 数据是否接真后端，待 itsuki 拍
3. README 若仍描述旧 standalone 链需更新
4. 上线前清理其余 demo-only scaffold

---

## 5. 第 5 组：03_dev/student_ios + student_android + rollcall_device + LATEST.md（78 + 131 + 36 + 1 文件 — 2026-06-05 校准）

**统计**：iOS 78（顶层 2 + demo 4 + v1 72）/ Android 131（v1 全 Compose）/ 点呼机 36（软件骨架 12 + 采购截图 24）/ `03_dev/LATEST.md` 1。
**核心发现**：iOS SwiftUI 主线在 `03_dev/student_ios/v1/`，Foundation / Network / Features 结构成型；Android 6 月大幅扩到 57 屏；点呼机仍骨架。三端真后端接入随 backend 推进。

### 5.1 顶层 + demo（8 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `03_dev/LATEST.md` | **2026-05-22 重写**：5 端 HTML プロトタイプ时代历史归档索引（Codex FC-037 修 — 原是「最新 HTML 速查」含明文密码 + 指向已归档 demo）| ✅ | 历史追溯用 / 不能按其路径启 demo |
| `student_ios/README.md` | iOS 目录总说明 | ✅ | 新会话先看 |
| `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` | iOS Round 1 时给设计师的需求简报（已归档） | 📦 | 5-13 commit 81842f4 改名 / IOS_DESIGN_LOG 全覆盖 |
| `student_ios/IOS_DESIGN_LOG.md` | ⭐ iOS 设计决策权威源（§1-11 共 11 章拍板理由） | ✅ | 改 iOS 业务代码前必查 |
| `demo/.gitignore` | demo 目录的 git 忽略规则 | ✅ | 范式标准 |
| `demo/QA_Round1_PhaseB.md` | Claude Design Phase B 静态扫描报告（QA 验收） | ✅ | Round 1 验收记录 |
| `demo/_archived_Round2_Prompt_draft.md` | Round 2 给 Claude Design 的 prompt 草稿（已归档） | 📦 | 5-13 改名 / C3 议题已 resolve |
| `demo/Tomoshibi_iOS_PhaseB_v2.html` | Phase B 时 Claude Design 输出的完整原型 HTML | 📦 | 锁定不动 / demo day 放映用 |

### 5.2 v1/ 顶层管理（3 文件 — 2026-05-06 退役 cloud agent 模式后精简）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `.gitignore` | iOS 目录 git 忽略（DerivedData / xcuserdata 等） | ✅ | 范式标准 |
| `README.md` | iOS v1 目录说明 | ✅ | 范式标准 |
| `project.yml`（xcodegen） | xcodegen 项目生成配置 — 跑 `xcodegen` 生成 .xcodeproj | ✅ | 加文件后要重跑 xcodegen |
| `BUILD.md` | iOS v1 编译运行手册 | ✅ | 新机器构建看这个 |

> **2026-05-06 归档**：STATUS / SHARED_DECISIONS / SESSION_CHANGELOG / REMOTE_AGENT_GUIDE 4 个 cloud agent 元数据文件已 git mv 到 `99_archive/2026-05-06_cloud_agent_退役/`（独立 repo 模式退役 — itsuki 决定不用 cloud agent，保留这 4 文件无意义）。

### 5.3 v1/TASKS/（3 文件）

`TASK_C_COMMUNITY.md` / `TASK_D_APPLY.md` / `TASK_E_MYPAGE.md` 都 ✅ — Agent dispatch 任务卡。和 IOS_DESIGN_LOG 分工：LOG 是设计决策权威，TASK 是实装 checklist，零重合。

### 5.4 v1/Xcode 项目结构 + Assets（7 文件）

`project.pbxproj`（27KB 机器生成）+ `contents.xcworkspacedata` + 5 个 Assets.xcassets 元数据/icon = ✅。**STATUS.md 提到 Assets 暂因 SDK 冲突移除**，需要 4-23 后澄清现状。

### 5.5 v1/Features/（11 文件 — 8 个 *Stubs.swift + Apply 下 3 个真实表单）

| 文件 | 一句话作用 | 行数 | 状态 |
|---|---|---|---|
| `Auth/AuthStubs.swift` | 登录 / 注册 / 找回密码 10 个屏的 SwiftUI 真实装（对照 jsx 1:1 翻译） | 2074 | ✅ 完成 |
| `Home/HomeStubs.swift` | 首页 6 屏 + 点呼弹窗 4 状态动画（RollcallSheet money shot） | 2579 | ✅ 完成 |
| `Community/CommunityStubs.swift` | 社区 18 屏（公告 / 班车 / 失物等）— 必做 8 屏 + stub 10 屏 | 2025 | ✅ 完成 |
| `Apply/ApplyStubs.swift` | 申请相关屏（外泊 / 帰省 / 帰国） | 1920 | ⏳ 待 Agent D v2 |
| `MyPage/MyPageStubs.swift` | 个人页 14 屏（个人信息 / 扣分 / 设置等） | 2016 | ⏳ Landing 实装 / 其余 13 屏 stub / 待 Agent E v2 |
| `Schedule/ScheduleStubs.swift` | 日程屏（已废 — 并入 Home + Community） | 343 | ❌ 可删 |
| `StayList/StayListStubs.swift` | 外泊清单屏（已废 — 并入 Apply） | 1588 | ⏳ 行数翻倍可能不再是纯 stub — 实装前先 review |
| `BusList/BusListStubs.swift` | 班车清单屏（已废 — 并入 Community Bus card） | 330 | ❌ 可删 |
| `Apply/ApplyFormSupport.swift` | 申请表单的共用支撑组件 | — | ✅ |
| `Apply/DormLifeForms.swift` | 宿舍生活类 4 种申请的表单实装（对齐后端 dorm_life） | — | ✅ |
| `Apply/StudyOnlineForm.swift` | 在线学习申请表单实装（对齐后端 study_online） | — | ✅ |

### 5.6 v1/Foundation/（36 文件 — 2026-06-05 校准 29→36，Network 层随后端实装扩张）+ Root/（3 文件）

Foundation 全部 ✅ frozen — AppState / Components / LiquidGlass / Routing / Seed / Theme / Network 等基础层 + RootView + GlobalOverlays + TomoshibiApp 入口。原 17 文件 1861 行已扩到 29 文件（v1 实装中陆续加 NetworkModels / API endpoint / 复用组件等）。

### 5.7 03_dev/student_android/（Android 第 4 端,2026-05-06 合并回 DMSD,131 文件 — 2026-06-05 校准 80→131 Compose 屏大幅扩张）

> **背景**：2026-05-02 itsuki 拍板 v1.0 直接 iOS + Android 双端上线,Android 用 Kotlin + Jetpack Compose + Material 3 从 Claude Design 22 屏 standalone HTML 逐屏对译。原独立 repo `Tomoshibi-Android` 5-06 退役合并回 DMSD（详见 §8.1 退役 cloud agent 模式）。

| 文件类 | 一句话作用 | 数 | 状态 |
|---|---|---|---|
| `ANDROID_DESIGN_LOG.md` | ⭐ Android 设计决策权威源（22 屏 route 登记 + Compose 翻译规则 + Phase 计划） | 1 | ✅ |
| `v1/` Gradle 配置（7 文件）| Android 项目构建配置 — `build.gradle.kts` × 2 + `settings.gradle.kts` + `gradle.properties` + `libs.versions.toml` + wrapper | 7 | ✅ |
| `v1/app/AndroidManifest.xml` + `res/`（8 文件）| Android manifest（应用权限 / 入口）+ 资源目录（drawable / values × 3 / xml × 2 / mipmap × 2） | 9 | ✅ |
| `v1/app/.../{TomoshibiApp,MainActivity}.kt` | 应用入口类（@HiltAndroidApp 注入根 + @AndroidEntryPoint Activity） | 2 | ✅ |
| `v1/app/.../nav/`（Routes + NavGraph）| 22 屏路由声明 + 路由图（对称 iOS 的 Route.swift + RootView.swift） | 2 | ✅ |
| `v1/app/.../data/`（store + seed + model）| 全局状态 store（CompositionLocal）+ MockData 种子数据 + Models 领域类型 | 3 | ✅ |
| `v1/app/.../ui/components/`（5 文件）| 跨屏共用 UI 组件 — TopRollBar / GlobalScaffold / BottomTabs / RollCallSheet / HomeCards | 5 | ✅ |
| `v1/app/.../ui/theme/`（4 文件）| Material 3 主题层 — Color / Theme / Tokens / Type | 4 | ✅ |
| `v1/app/.../ui/icons/SuzuIcons.kt` | Tomoshibi 自定义图标集 | 1 | ✅ |
| `v1/app/.../ui/screens/`（57 文件）| 各业务线屏的 Compose 实装 — applications 16 / community 13 / mypage 12 / login 3 / announcements + notifications 各 2 / home / rollcall / nfc / deduction / account / bus / splash / welcome / onboarding 各 1 | 57 | ✅ |
| `v1/app/src/{androidTest,test}/`（2 文件）| 测试脚手架 — ExampleInstrumentedTest + ExampleUnitTest | 2 | ✅ 未真写测试 |

**核心发现**：
- 屏数从 22 涨到 57（6 月大幅扩展 — 申请类 16 + 社区类 13 + 个人页 12）
- 包名 `jp.tomoshibi.android` — Tomoshibi 命名跟 iOS / 后端一致
- 跟 iOS 的对应：`screens/` ≈ iOS `Features/Stubs.swift`,`components/` ≈ `Foundation/`,`nav/` ≈ `Foundation/Routing/`
- **真后端接入未做** — 当前是 MockData seed,backend v1 上线后改 fetch API（同 iOS,见 §3.7 backend P0 缺块）

**与 system_features.md / spec 的对齐状态**：
- ⏳ 未做 spec-sync 跨端字段对齐检查（spec-sync skill 价值在 backend 上线后跑）
- 22 屏 vs system_features §7 14 子节功能矩阵 — 视觉层覆盖 ✅,业务规则层（扣分阈值 / 时间窗 / 役职链）待 backend 接通后实战验证

### 5.8 03_dev/rollcall_device/（点呼机第 5 端,2026-05-08 建骨架,36 文件 = 软件骨架 12 + 采购截图 24）

> **背景**：2026-05-08 itsuki 拍板「点呼机当第 5 端」(对称 backend / iOS / Android / teacher_web 4 端模式) — 跑在 Raspberry Pi 3A+ 上的 Python 程序,读 NTAG215 学生卡 + 写 ST25DV16K 动态贴纸 + LED 反馈 + 日语播报。物理硬件层在 `02_design/hardware_design.md`,本目录是软件层。

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `README.md` | 点呼机目录总说明 + 上下游关系 + 启动指引 | ✅ 骨架 | 新会话先看 |
| `ROLLCALL_DEVICE_DESIGN_LOG.md` | ⭐ 点呼机软件设计权威源 — 11 章（技术栈 / GPIO 接线 / 主循环 / 模块 / systemd / 已知坑 / 待拍板 D1-D6） | ✅ 骨架（11 章纲）| 改点呼机代码前必查 |
| `requirements.txt` | 点呼机 Python 依赖清单（待选 — Adafruit-PN532 / smbus2 / gpiozero / httpx） | ✅ 骨架 | 注释列出候选 |
| `src/main.py` | 点呼机主循环入口（IDLE → SUBMITTING → SUCCESS / FAIL → IDLE 状态机） | ⏳ 占位 | 实装时填 |
| `src/{nfc,audio,led,api}/__init__.py` | 4 个空模块包占位（NFC 读卡 / TTS 语音 / LED 灯 / 后端 HTTP 客户端） | ⏳ 占位 | 实装时分别写 PN532 / TTS / LED / 后端调用 |
| `config/.gitkeep` + `docs/.gitkeep` | 占位文件让空目录能进 git（systemd unit / 部署手册 / 接线图 待写） | ⏳ 占位 | git 不 track 空目录的解决方案 |
| `点呼机接线说明.md` | 各模块接 Pi 3A+ 的接线方法（PN532 走 SPI / ST25DV 走 I²C / LED GPIO / 风扇 5V / 喇叭 USB + 7 条零基础避坑） | ⏳ 待到货实测 | 2026-05-28 硬件采购会话建 / 配 `02_design/hardware_design.md` |
| `点呼机采购清单.html` | 首台演示机采购清单（按秋月/Switch Science/Amazon 分渠道 + 价格 + 库存状态）+ 点呼机功能 / 模块对应 / 接线速查，浏览器可视化快速查看 | ⏳ 待下单 | 2026-05-28 硬件采购会话建 / 部分线下部分线上 |
| `采购截图/`（24 张 PNG） | 点呼机配件采购截图 — Amazon 购物车 + 秋月电子订单 + 各模块单品 | ✅ | 5-28 硬件采购会话存证 |

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

## 6. 第 6 组：05_logs + 06_assets + bin（161 文件 = 05_logs 149 + 06_assets 9 + bin 3 — 2026-06-05 校准）

**05_logs 177 细分（2026-06-10 实数 find 校准）**：raw 108（每天原始会话记录）+ AC_叙事 12 + dev_log 14 + problem_solving 4 + audit_2026-05-19 13 + audit_2026-05-22_codex 7 + 3 个 meta（decision_log / learning_path / project_evolution）+ 散件 ~9（teacher_web 施工 3 + 各 audit 单件 + 漏洞清单 + 版本演变一览 等）。
**核心发现**：raw 是项目最大原始素材区，AC 候选密度最高的几天见 §6.2 ⭐ 标记。

### 6.1 05_logs/ 根级 meta（3 文件）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `decision_log.md` | 项目级重大决策记录（每条 = 决策 + 理由 + 事后回看） | ✅ | 7 条已记 / 最后 5-22（撤回中国海运改日本本地买）/ "事后回看"占位待补 |
| `learning_path.md` | itsuki 学习哲学 + 已走的路 — AC 自我推荐书素材 | ✅ | 最后 4-13 / 4-10 后新学的 NFC / Swift / 硬件未追记 |
| `project_evolution.md` | 项目重大转折记录（每次 = 转折点 + 起因 + 影响） | ✅ | 4 次已记 / 最后 4-13 / 待补"第 5 次转折" = demo 完成情况 |

### 6.2 05_logs/raw/（108 文件 — 含 README — 2026-06-10 校准 92→108，每天一份原始会话记录，持续增长）

> raw 是项目最大的原始素材区。下表只列 AC 候选密度高（⭐ 多）的关键日，不逐个列全部 91 份 — 找某天记录直接看文件名 `raw/YYYY-MM-DD*.md`。

| 文件 | 这天发生了啥 | AC 候选密度 |
|---|---|---|
| `README.md` | raw 目录总说明 — 怎么写 raw / 命名规则 | — |
| `2025-12_NFC系统早期设计对话.md`（3100 行）| 项目起源原始素材 — 最初跟 GPT 讨论 NFC 方案 | ⭐⭐ |
| `2026-04-12_NFC架构讨论.md` | 语音播报防作弊原创设计的诞生 | ⭐⭐ |
| `2026-04-13_版本管理和AC工作流.md` | 版本号纠错 + AC 记录方法论建立 | ⭐⭐ |
| `2026-04-15_NFC硬件+Phase2架构讨论.md` | AC 候选密度最高的一天 — 推翻 + 重论证 + 双路径方案诞生 | ⭐⭐⭐ |
| `2026-04-17.md` | 25 项 spec 漏洞清理 + Q1-Q5 拍板 + v0.3.0 上线 | ⭐⭐ |
| `2026-04-19.md` | 方法论级 — 取消分阶段 + 文档同步机制 A+B+C 建立 | ⭐⭐⭐ |
| `2026-04-20.md` + `2026-04-20_v0.3.1发布执行.md` | URL 漏洞 + ST25DV 动态贴纸方案 + 进度如实汇报 | ⭐⭐ |
| `2026-04-21.md` | Tomoshibi 命名定 + Pi 3A+ 反直觉决策 | ⭐⭐⭐ |
| `2026-04-22.md` + `2026-04-22_iOS前端设计_Round1.md` | 4-tab 推翻 + 73 页清单 + Round 3 解包 | ⭐⭐ |
| `2026-04-23.md` | 学号 6 桁 + 跨会话同步规则 A+B+C + 巧合收束 | ⭐⭐⭐ |
| `2026-04-24.md` / `2026-04-29.md` / `2026-04-30.md` | 老师反馈受领 + 三轨 ABC 落地 + 学習 NFC 化 | ⏳ |
| `2026-05-01.md` / `2026-05-02.md` / `2026-05-03.md` | 5 月初 v0.4-v0.6 推进（公告 4 端 + 注册码 spec） | ⭐⭐ |
| `2026-05-04.md` + `2026-05-04_iOS_bug修复.md` | WIP/TODO 分工拍板 + iOS bug 修复 | ⭐⭐ |
| `2026-05-06.md` | 独立 repo 退役 — 5 端全合并回 DMSD monorepo | ⭐⭐⭐ |
| `2026-05-07.md` | iOS 上架冲刺启动 + 教学 skill 拍板 | ⭐⭐ |
| `2026-05-08.md` + `2026-05-08_ios_上架冲刺.md` + `2026-05-08_reviewer_demo重做.md` + `2026-05-08_vps_deploy_steps.md` | GCP VPS 部署 + Apple Reviewer demo 5 bug 修干净 + 点呼机第 5 端拍板 | ⭐⭐⭐ |
| `2026-05-10.md` | 15 skill 批量装 + ac-radar 上线 | ⭐⭐ |
| `2026-05-11.md` + `2026-05-11_reviewer后门修复上线.md` | 术语表 HTML 建 / session-coord / graphify / 沟通问题大爆发（cc-comm-rules 立 skill）/ reviewer 后门修复跨机器协作 | ⭐⭐⭐⭐⭐ |
| `2026-05-11_深夜大整理.md` + `2026-05-12_深夜大整理_总结报告.md` + `_AC价值汇总.md` + `_问题清单_codex修复SOP.md` + `_codex_auto_修复.md` + `_压缩后接力指引.md` | CC 自治模式跨夜大整理（5-11 23:30 → 5-12 04:57）— 38 条 AC 素材 + 11 区域 codex 修复 SOP | ⭐⭐⭐⭐ |
| `2026-05-12_深度审查_总结.html` + `_执行计划.md` + `_批1_5端代码整合.md` + `_批2批3整合.md` + `_接力CC进度快照.md` + `_修补批量+comm规则加严.md` | 5-12 接力深度审查 5 端代码 + cc-comm-rules v0.2→v0.3 加严（多任务总结规则 6）+ 修补批量执行 | ⭐⭐⭐⭐ |
| `2026-05-13_接力CC续做.md` | 5-13 早 itsuki 怒怼"没真整理"后 7 commit 真整理 — 9 文件死链修 + 12 AC 文件 git mv + project-overview 同步 hook 上线 | ⭐⭐⭐⭐ |
| `2026-05-14.md` + `2026-05-14_Tango立项+bootstrap.md` | 5-14 三段：早段 cc-comm-rules v0.5.0 沟通规则根本反转 / 中午 graphify 实测复盘 / 晚段 Tango 立项 + grill-me 12 题 / 晚段-2 anti-ai-flavor 立项 + 同日撤回 v0.5.0 → v0.6.0 | ⭐⭐⭐⭐⭐ |
| `2026-05-16.md` | 5-16 跨项目完整性审计 + 4 项目大修（Tango B 案 / SC26 轻修 / cc-project-template D 案清通用 / 全局 hook 改读 cwd / 修 macOS bash 3.2 heredoc 中文乱码 bug） | ⭐⭐⭐⭐⭐ |
| `2026-05-16_AC合格率评估+官网验证.md` | 5-16 AC 入试合格率评估 + 筑波大学官网信息核对 | ⭐⭐⭐ |
| `2026-05-19.md` | 5-19 project-overview 文件介绍大改造 + 9 处漂移对账修复 + 防漂 C 方案落地（hook 全覆盖 + 启动对账脚本）+ 元层翻车 itsuki「我看不懂了」 | ⭐⭐⭐⭐⭐ |
| `2026-05-26.md` | 5-26 早段：iOS Bot 1 误删功能复查（全量 diff fork vs 主项目 v1 证实没遗留误删 + 撤暗夜模式 v2 + 3 上架配置归位）+ memory 加铁律「TODO 关条目不要问」+ 晚段：全项目中枢机制立项 + DMSD 注册档案 | ⭐⭐⭐⭐ |
| `2026-05-26_dmsd-startup+CLAUDE.md大改.md` | 5-26 晚段-2：启动 SOP 集中化（dmsd-startup skill 立项 — 5 件启动必做事 + §4 按需触发段）+ DMSD CLAUDE.md 247→190 行重写（QTS 模式 — Skills 继承 / Hooks 继承 / 全项目中枢联动）+ 沟通铁律「不主动用英语名词」立项全局 + 6 项目 CLAUDE.md 落地 + destructive-bash 行为约定（自己停下想 / 没必要不走 / 灾难级才问）+ CLAUDE.md 文档观转变（时间戳冗余禁止）| ⭐⭐⭐⭐⭐ |
| `2026-05-27_ios_审查会话.md` | 5-27 深夜-3：iOS 全自主审查 + 修 + 收尾会话 — 5 维度过完 41 文件（demo 后门残留 / A-XXX bug 标记 / catch 错误处理 / Force unwrap / NFC 实装），发现 1 处可修（`MyPageStubs.swift:1404` `c.score!` 改 `map ?? _`）+ 2 处架构性延期（`StayListStubs.swift:475` catch 降级 mock 假数据 / `MyPageStubs.swift:1637` 暴露 `localizedDescription`）写 TODO §D | ⭐⭐ |
| `2026-05-27_teacher_web_v1.0_深夜推进.md` | 5-27 凌晨：itsuki 设 `/goal v1.0 完整体上线` 后 CC 自主推 22 commit — teacher_web client.js 接 backend 4 个 page（DisciplinePage / RecordsPage / CleaningPage / FrontDeskPage） + announcements 实装 + LoginScreen 文案 cleanup + backend `discipline.py` / `cleaning.py` / `front_desk.py` 新建 model + router + alembic c1d2e3f4 3 张表 + propose 文档 `01_specs/teacher_web_v1.0_backend_models_propose.md` 等 itsuki 起床拍板 | ⭐⭐⭐⭐ |
| `2026-05-27_全项目审查.md` | 5-27 早段：itsuki 启动「全项目审查 + 不要偷懒」会话 — CC 一次过扫 1189 文件 + grep 决策关键词 + 比对 SKILL.md §0.1 → 直接修 6 处 Vite 决策漂移（README × 2 / LATEST / progress_overview / WEB_DESIGN_LOG / client.ts）+ 物理清 7 个 .DS_Store + git mv `_archived_DESIGN_BRIEF` → 99_archive + TODO §🛠️ §N 加 8 条 backlog（99_archive 散件归档 / .pages 历史归档 / graphify 刷 / backend/demo 处置 / progress_overview 大改 / v0.9 bump 决策 / 决策状态扫描 hook propose） | ⭐⭐⭐⭐⭐ |
| `2026-05-28_web登录页修复.md` | 5-28：itsuki 第一次实机打开实名账户登录页报 2 个 bug — ①9 个账号「密码不知道」→ 查出 seed.py 明文常量 DEV_PASSWORD="123456"（模式 5 认知改变：数据层 vs 代码层分离）→ 砍到 1 个账号「新股」重建 dev 库；②返回按钮「失灵」→ 截图里 401 错误反推 React 活着（逻辑 OK）→ 真因 fontSize:12+灰色+padding:0 点击区域极小 → 改蓝色背景可见按钮（模式 2 假设崩了继续追查） | ⭐⭐⭐⭐ |

### 6.3 05_logs/dev_log/（每日工程简报 + 格式说明 + 历史旧文件）

| 文件 | 这天/这阶段做了啥 | 状态 |
|---|---|---|
| `_README_工程简报格式.md` | dev_log 工程简报格式说明书（2026-06-08 复活时建）— 纯工程事实 + 跟 AC 素材分开铁律 + 模板 | ✅ |
| `YYYY-MM-DD.md`（每日工程简报） | CC 收尾自动生成的纯工程流水账（改了哪些文件 / 修了什么 bug / commit 清单），2026-06-08 复活 | ✅ |
| 2026-02 月 4 个 | 早期规格设计阶段（v0.1 spec 起草） | 📦 历史快照 |
| `2026-04-10_空白期反思_索引.md` | 1 个月空白期的项目内锚点（正文反思在 iCloud） | ✅ |
| `2026-04-10_回归日.md` + `2026-04-10_session_summary.md` | 空白期后回归项目第一天的记录 | ✅ |
| `2026-04-12_NFC方案设计日.md` | NFC 方案敲定那一天 | ✅ |
| `2026-04-15_[NFC][MULTI]_硬件重开与Phase2架构.md` | NFC 硬件重新选型 + Phase 2 架构（多端模式） | ✅ |

> **断更 + 复活**：02-08 → 04-10 共 66 天无 dev_log（已由 `空白期反思_索引` 解释）。4-15 后再次断更，被 AC 素材 raw/ 吸走 → 2026-06-08 itsuki 拍板复活，改成纯工程简报 + CC 收尾自动生成。

### 6.4 05_logs/problem_solving/（4 文件）

全部 ✅ — 4-10 NFC/NFD git pull 失败 / 4-15 AI 过度配置诊断 / 4-15 iOS 限制下双路径重构 / 4-15 spec gap 发现。**全集中 4-10/4-15**，4-15 后无新增。

### 6.5 06_assets/（8 文件 — 2026-05-25 加学习内容清单.html，原 7 → 8）+ bin/（3 文件 — 2026-05-19 加 check_overview_drift.sh）

| 文件 | 一句话作用 | 状态 | 备注 |
|---|---|---|---|
| `06_assets/学习内容清单.html` | itsuki 反向工程自己项目 5 端 + 编程基础 + AC 入試 直接相关知识 — 9 章学习内容清单（不是计划），跟 iCloud `02_分析与调研/AC入試制度総覧_2027.html` 配套 | ✅ | 5-25 起草 v0.1.0 |
| `06_assets/术语表.html` | 180+ 英语词条的可交互学习页面（17 段分类含 ⑰ CC 协作）— itsuki AC 面试日语准备材料 | ✅ | 5-11 加 / 5-13 从 `00_admin/` 迁入 / 5-14 早段加 ⑰ 23 词 |
| `06_assets/icons/tomoshibi_flame_color.psd` | Tomoshibi 火苗 logo 的 Photoshop 设计源文件 | ✅ | 4-23 |
| `06_assets/icons/tomoshibi_flame.png` | Tomoshibi 火苗 logo 的 PNG 渲染版 | ✅ | 4-23 |
| `06_assets/icons/tomoshibi_app_icon_256.png` | App icon v1（iOS / Android 应用图标 256px） | ✅ | v1 版本 |
| `06_assets/icons/tomoshibi_app_icon_v2.png` | App icon v2（5-03 设计迭代后的版本） | ✅ | 5-03 |
| `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md` | 学校班车特别运行通知的真实样本（含学生实名） | ⚠️ | v1.0 公开前需脱敏 |
| `06_assets/bus_schedule_real.md` | 学校班车时刻表真值数据 — iOS / teacher_web 做班车视图时的种子数据 | ✅ | 5-08 从 02_design/ 挪入（数据不是设计） |

**`bin/` 3 文件**（顶级目录非编号目录详见 §1.8.1）：
- `bin/sync-check.sh` ✅ — 联动检查工具（commit 时 pre-commit hook 跑 / 中途随时 `bash bin/sync-check.sh` 手动跑）
- `bin/create_local_dev_symlink.sh` ✅ — VPS 已停用但脚本保留参考（5-13 commit 81842f4 从 `00_admin/` 迁入）
- `bin/check_overview_drift.sh` ✅ — **2026-05-19 加** — project-overview §0.1 体量表跟 git ls-files 真实数对账脚本。注册在 `.claude/settings.json` SessionStart hook 每次会话启动自动跑。itsuki 也可以 `bash bin/check_overview_drift.sh` 手动跑。出处：5-19 对账发现 9 处漂移后 itsuki 拍板 C 方案（hook 全覆盖 + 启动对账）

> ~~`bin/sync-ios-refs.sh`~~ 📦 — 2026-05-06 归档到 `99_archive/2026-05-06_cloud_agent_退役/`（独立 repo 模式退役）

---

## 7. 第 7 组：99_archive（639 文件 — 2026-06-05 校准 431→639，历史归档区，按子目录粒度维护）

> 归档区文件最多（占全项目 46%），但都是「任务结束保留作参考」的历史物，CC 日常很少查具体某个文件。本组只维护**子目录级**结构（§7.2），不逐个文件追描述。找老归档先看 `99_archive/README.md`。

### 7.1 根级（21 文件）

| 文件 | 一句话作用 | 状态 | 建议 |
|---|---|---|---|
| `README.md` | 99_archive 归档导航 — 哪个子目录归档了啥 | ✅ | 找老归档时看 |
| 14 × `ファイル - 2026-02-17T*.510Z`（共 6.7MB PDF dump） | 早期 GPT 对话的 PDF dump | ❓ | 内容已整理到 `raw/2025-12_NFC系统早期设计对话.md` → 可删 |
| 5 × `*_原始.pages` / `*_备份版.pages` / `Folder_Structure_Overview.pages` | 早期 Pages 文档原稿（learning_process / progress_log 等） | ❓ | 已被 .md 取代 / 可删或保留待 itsuki 决定 |
| `2026-04-12_executable_dev_checklist_v0.1.md` | NFC 方案敲定后的第一份开发清单 | 📦 | 历史快照 |

### 7.2 各专题归档子目录（2026-05-16 校准 — 原 6 个 → 现 13 个子目录，5-02 后新增 7 个）

| 子目录 | 归档了啥 | 文件数 | AC 价值 | 建议 |
|---|---|---|---|---|
| `01_specs_Overview_原稿/` | spec Overview 的 .docx 原稿 | 2 | ⭐ | 可删（已被 .md 取代） |
| `2025-12_早期GPT对话/` | 项目起源的 GPT 对话（prompt + payload + response 三件套） | 3 | ⭐⭐⭐ | 保留 — 项目起源证据 |
| `2026-03-08_throwaway_ios_swift/` | Phase 0 试错 Xcode 项目（验证 Core NFC + FaceID + Secure Enclave 可行性） | 35 | ⭐⭐⭐ | 保留 — 试错代码 AC 高价值 |
| `NFC_NFD_鬼影文件/` | macOS NFD 归一化导致 git pull 失败的 5 个`のコピー`鬼影文件 | 5 | ⚠️ | 需 itsuki 决定 — 问题已解决可删 / 保留则 README 补 1 句 |
| `2026-04-15_old_demo/` | 首个可运行原型（Flask + iPhone Shortcuts + TTS） | 9 | ⭐⭐⭐ | 保留 — 首个原型证据 |
| `2026-04-29_pre_v1.0_cleanup/` | v1.0 启动前的大整理归档（demo 4-28 + Round 2/3 handoff） | 34 | ⭐⭐⭐ | 保留 — 见下 §7.3 |
| `2026-05-02_android_handoff_route_archived/` | Android 22 屏 route 早期 handoff 草稿 | 57 | ⭐⭐ | 5-02 加 |
| `2026-05-02_backend_handoff_F1-F7/` | backend 7 区域分批 handoff 文档（F1-F7） | 1 | ⭐⭐ | 5-02 加 / 文件数少疑似只剩索引 |
| `2026-05-02_compose_drafts_archived/` | Android Jetpack Compose 早期组件草稿（含 GlobalScaffold 跨档跟踪） | 38 | ⭐⭐ | 5-02 加 |
| `2026-05-02_handoff_F1-F7/` | 配对 backend handoff 的 frontend handoff 系列 | 1 | ⭐⭐ | 5-02 加 / 跟上面 backend_handoff 重复需 itsuki 决定 |
| `2026-05-03_old_icons_pre_v2/` | App icon v1 设计稿（v2 替换前） | 2 | ⭐ | 5-03 加 |
| `2026-05-04_文件结构指南_已被项目文件总览取代/` | `文件结构指南.md` 整体迁入（本 skill 取代它） | 1 | 📦 | 5-04 加 |
| `2026-05-04_版本管理SOP_迁入skill/` | `版本管理SOP.md` 迁入 `.claude/skills/version-bump/SKILL.md` | 2 | 📦 | 5-04 加 |
| `2026-05-06_cloud_agent_退役/` | 独立 repo 模式退役（4 个 cloud agent 元数据 + iOS / Android 跨 repo 镜像策略） | 8 | ⭐⭐⭐ | 5-06 加 / AC 高价值 |
| `migration_2026-05-06/` | 5-06 monorepo 合并迁移过程记录 | 48 | ⭐⭐ | 5-06 加 |
| `2026-05-12_深夜大整理/` | 5-12 深夜 CC 自治大整理批量归档（5 个 v0.4.0 draft + progress_overview_draft 反向过时 + 跨会话 iOS 决策 + T2 dryrun + Device Contract 骨架 等） | 6 | ⭐⭐⭐ | 5-12 加 |

### 7.3 2026-04-29_pre_v1.0_cleanup/ 详细（34 文件）

| 子分组 | 这子分组装了啥 | 文件清单 | 价值 |
|---|---|---|---|
| `demo_4-28/`（11 文件）| 4-28 demo day 完整 7 天冲刺档案 | README + sprint + scope_tier + demo_script + ST25DV_fallback + for_code_agent + questions_for_admin + questions_for_requirements + 3 子（round1/round2/round3 handoff） | ⭐⭐⭐ AC 核心 |
| `teacher_web_round2/` 6 jsx | Round 2 时 Claude Design 输出的 teacher_web UI 骨架 | live / login / override-modal / shell / theme / roll-call-landing | ⭐⭐ |
| `teacher_web_round3_handoff/` 5 文件 | Round 3 给 Claude Design 的输入素材 | README + Prompt + 3 张参考画像 | ⭐⭐ |
| `teacher_web_handoff_round2/` 4 文件 | Round 2 chat1.md AC 素材 + 设计系统截图 | README + chat1.md + design-system-round1.html + 1 截图 | ⭐⭐ |
| `student_ios_round1_handoff/` 6 文件 | iOS Round 1 给 Claude Design 的 prompt + 参考画像 | README + Round1_Prompt + 4 张参考画像 | ⭐⭐ |
| 杂项 5 文件 | 迭代历史散件（Phase B v1 / 老 DESIGN_BRIEF / DEPRECATED handoff / Round 2 入口 HTML / teacher_requirements v0.5.0 draft） | Tomoshibi_iOS_PhaseB_v1 / _archived_v1_DESIGN_BRIEF / DEPRECATED handoff / round2 entry HTML / teacher_requirements_v0.5.0_draft | ⭐⭐ |

---

## 8. 综合横向洞察

### 8.1 demo ↔ v1 复制策略对照（2026-05-06 退役独立 repo 模式后）

| 模块 | 策略 | 现状 |
|---|---|---|
| **backend** | "重写 + 参考" | demo 锁定不动；v1 schema 全新（UUID + TIMESTAMPTZ + CHECK 约束）；ws_manager / models 思路参考 ✅ |
| **teacher_web** | "界面冻结迁移" | 6-05 从 HTML 单文件迁到 React+TS+Vite，界面 100% 原样搬；旧版归档 ✅ |
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

### 8.4 五层 DESIGN_LOG 体系

五端各有 DESIGN_LOG（各端设计决策的权威源）：BACKEND / IOS / ANDROID / WEB / ROLLCALL_DEVICE。都跟 `02_design/system_features.md`（共用层真值）锁定同步——改某端业务代码前先查对应端 DESIGN_LOG。这套「1 个共用层 + 5 个专属层」的治理是 AC「工程化治理思维」素材。

---

## 9. 任务清单 → 见 `00_admin/TODO.md`

> 原来这里维护 P0/P1/P2 行动清单，2026-06-05 废弃 —— 任务真值统一在 `00_admin/TODO.md`（项目的 issue tracker，按 A 工程 / B 文档 / C AC 素材 三轨分类）。本 skill 只管「文件清单」，不重复维护任务清单（两处会打架）。

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
| 10 | `.claude/skills/version-bump/SKILL.md` + hooks 治理 | #4 | 文档治理思维：从漂移发现到机制化解决 |

---

## 11. 待决定 + 审查历史 → 见 `00_admin/TODO.md` / git log

> 原「itsuki 待决定列表」（不可读文件清理 / 鬼影文件去留 / 学生实名脱敏时机 等）已并入 `00_admin/TODO.md` 统一管理。原「本次审查方法」（2026-05-01 首次 7 组 Explore agent 并行扫描合成）属历史过程，归 git log，不在本 skill 留存。

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

**本文最后更新**：2026-05-19 二改（itsuki 当场对账后拍板「全部修」/ 9 处文件数漂移全修 — §3 backend 35→56 + 加 §3.6.5 alembic / §4 teacher_web 314→333 + 重写 §4.3 / §5 iOS 54→66 + Foundation 17→29 + Features 8 行数全刷 / §5.7 Android 56→80 + 22→23 屏 / §5.8 rollcall_device 8→10 / §1.6 + §2.2 标题数 / §6.2 raw 加 5-16 两文件 / §7.2 9 个子目录文件数填上）。早些 5-19 一改（文件介绍大改造 — 27 段加「一句话作用」列）。早些更新：2026-05-16（3 天漂移大校准 + §14 收尾强制清单）/ 2026-05-13 中午（接力 CC 校准 — 顶部 §0 体量数字 + §1.4/§1.5 26 文件 git mv 路径 + §1.6 hooks 8→11 + §1.8 非编号目录新章节 + §3.4 backend routers 5→11 + §3.6 tests 3→5 + §5.1 iOS 改名 / 基于 sub agent af04d326 audit 报告）/ 2026-05-12 凌晨 CC 自治大整理 / 2026-05-08（§5.7 补 student_android 章节 / §5.8 加点呼机第 5 端骨架 / §13.1 加 6 条反向规则 Rule 14-19）/ 2026-05-04（加 §13 文件联动指南）/ 2026-05-01（首次创建 7 组并行扫描 606 文件合成）

> **2026-05-16 落地 5-13 audit 18 条进度**（itsuki 拍板「检查有没有文件没加进去 / 改了没更新 / 描述不准」全做）：
>
> ✅ **本次已修**：
> - §0.1 体量数字 606 → 957 全行重算（git ls-files 全统计）
> - §1.2 「文件结构指南.md」标已归档（→ `99_archive/2026-05-04_文件结构指南_已被项目文件总览取代/`）+ 4 文件迁出 / 归档标明
> - §1.6 sync-rules.sh 21 → 19（grep `^add_rule` 真实数）
> - §6.2 raw/ 36 → 45（5-12 后新增 9 个补完）
> - §6.5 06_assets/ 4 → 7（漏的术语表.html + 3 app icon）+ bin/ 单独列 2 文件
> - §7.2 99_archive 子目录补 7 个（2026-05-02_* × 4 + 2026-05-03_old_icons + 2026-05-04_文件结构指南 + migration_2026-05-06 + 2026-05-12_深夜大整理）
> - 加 §14「session-wrap 收尾时强制同步本 skill」段（指向 session-wrap §7.5.1 项 8）
> - 顶部「最后更新」+「最后扫描真值」字段刷今天日期
>
> ✅ **2026-05-19 当场对账时已修**：
> - ✅ §4.3 teacher_web v1 整段失效 → 已改成「Vite + TS 重构进行中，174 文件，14 个新顶级 + src 多 26」+ 列出 6 类新文件作用
> - ✅ §5.5 iOS Feature 行数 → 8 个 .swift 文件 wc -l 全刷新（StayList 748→1588 / Home 1705→2579 / MyPage 1521→2016 等）
> - ✅ §5.6 iOS Foundation 17 → 29 文件
> - ✅ §5.7 Android 22 → 23 屏 + 56 → 80 文件
>
> ⏳ **仍未做**：
> - §10 AC top 10 第 10 项「版本管理SOP」路径已迁到 `.claude/skills/version-bump/SKILL.md` — 简单 sed 修
> - §11 itsuki 待决定列表 8 条状态复核（progress_draft / 跨会话 已归档 / 实际 5-13 已大幅清理）— 需要逐条对照当前状态
> - 完整清单：`/tmp/project_overview_audit.md`（5-13 sub agent af04d326 生成）

---

## 14. 收尾时同步本 skill（2026-05-16 itsuki 拍板加）

> **背景**：5-13 itsuki 怒怼"没真整理 + project-overview 漂移 + 我看不到的地方也乱" → 当晚加 hook `00_admin/hooks/post-edit-project-overview-check.sh`（Write/Edit 实时提醒）。但 hook 是 warn 模式 + 误判率高 → CC 容易"看到提醒但跳过"。5-14 → 5-16 期间 3 天累积 9 处漂移（顶部时间戳 / §0.1 体量 / §1.2 文件结构指南 / §6.2 raw / §6.5 06_assets / §7 99_archive / §1.6 sync-rules / 末尾 audit / 加 §14）= hook 兜底不够。
>
> **2026-05-16 itsuki 拍板**：「要保证每次文件和结构做出改动，都会更新 project-overview / 最好加到收尾步骤里」 → **加到 session-wrap `§7.5.1 项 8`** 强制清单。

### 14.1 触发场景（必跑 project-overview 校准）

- 创建新文件（任何编号目录 / 顶级 / hooks / skills 等）
- 删除 / 改名 / 移动文件
- 大幅改文件作用（不是内容编辑，是"这文件干嘛"变了）
- 新加 hook / skill / 联动规则

### 14.2 校准必做的 3 件事

1. **改对应章节**：§1 顶层 / §1.2-1.8 00_admin / §2-7 编号目录 / §10 AC 价值 top
2. **顶部「最后更新」字段刷今天日期**
3. **末尾「真实状态扫描真值」脚注刷今天 git ls-files 全统计**

### 14.3 双层保险机制

| 层 | 工具 | 触发 | 强度 |
|---|---|---|---|
| 实时层 | `post-edit-project-overview-check.sh` hook | Write/Edit 后自动跑 | warn（提醒可跳过）|
| 收尾层 | `session-wrap` §7.5.1 项 8 | itsuki 说「收尾」时强制清单 | 强制（不允许默默跳过）|

### 14.4 状态字段（强制 3 选 1）

- ✅ 改了 — 列改了哪几段
- ⏸ 本会话无结构改动 — 说明改了哪些文件让 itsuki 确认确实只是内容编辑
- ❌ 漏 — 现在补

**3 项目同步**：DMSD（§7.5.1 项 8）+ SC26（§7.5.1 项 6）+ Tango（§5.5 项 6）三个项目 session-wrap 同日同步加。
