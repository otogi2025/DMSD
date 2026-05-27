# DMSD 项目指令（CC 必读）

## ⚠️ 沟通铁律 — 不主动用英语名词

除非这个词在项目代码 / 文档 / 文件名里真出现过，否则一律用中文。比如别说「凭证 credential」「兜底 fallback」「联动 sync」，直接说中文。

**不要默认认为 itsuki 认识项目里的各种名词和英语单词**。哪怕这个词在项目里真出现过，CC 第一次提到它时也要带一句解释「这是什么 / 在哪出现 / 干嘛用的」。例如说「`models.py`」要补一句「这是 backend 后端的数据库表定义文件」；说「FC-024」要补一句「这是系统 bug 专栏里的编号，指 teacher_web 明文密码漏洞」。itsuki 是零基础 + 项目体量 1193 文件 + 5 端联动，记不住所有代号 / 缩写 / 文件名 / 角色名。

完整规则在 `~/.claude/CLAUDE.md`。

## ⭐⭐⭐ dmsd-startup 强制加载

每次会话启动 **第一件事** 先 Read `.claude/skills/dmsd-startup/SKILL.md`，按 §2 顺序跑 5 件启动必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）。

不依赖关键词触发 — 每次新会话第一个回合 CC 必须主动加载本 skill。

## 关于 itsuki

中国留学生，日本高中三年级
完全零基础，所有概念从零解释
目标：筑波大学 情報学群 情報科学類 AC 入試，2027-04 入学
**DMSD 是核心 AC 叙事项目**（Tango / QTS 是派生项目）

## 项目核心

- **项目代号**：DMSD（Dormitory Management System Digitalization）
- **系统名**：Tomoshibi（灯火 / ともしび）— 用户面向
- **核心**：宿舍点呼数字化 + NFC 防代刷
- **技术栈**：iOS Swift+SwiftUI / Android Kotlin+Compose / 后端 FastAPI+PostgreSQL / 点呼机 Pi 3A+ + PN532 + ST25DV16K / NFC 卡 NTAG215
- **上线姿态**：v1.0 一次上线 iOS + Android + 卡，不分阶段 <!-- VERSION_OK -->
- **当前版本**：见 `CHANGELOG.md` 顶部
- **GitHub**：`otogi2025/DMSD` public（单一 repo，iOS+Android+Web+后端 全在 DMSD 内）

设计 / 防御 / 扣分 / 采购 / 硬件 / 流程详情：`02_design/` + `01_specs/` + `.claude/skills/project-overview/SKILL.md`

## 目录结构

| 目录 | 干嘛 |
|---|---|
| `00_admin/` | WIP / TODO / 项目文件总览 / 文档同步点清单 / hooks |
| `01_specs/` | 规格文档 — rollcall/ 字典 + 主体 |
| `02_design/` | 设计文档 — hardware / flow / system_features 等 |
| `03_dev/` | 代码 — backend / teacher_web / student_ios / student_android / rollcall_device（点呼机）|
| `04_ops/` | 运维 |
| `05_logs/` | 开发 log — raw / dev_log / problem_solving / decision_log / learning_path / project_evolution |
| `06_assets/` | 参考材料 / 真实样本 |
| `07_release/` | 发布物 |
| `99_archive/` | 早期归档 |
| `bin/` | 脚本 |
| `docs/agents/` | 外部 skill 配置（Matt Pocock 套件）|

完整文件级清单 + 状态 + AC 价值：`.claude/skills/project-overview/SKILL.md`

## 设计文档双层

| 层 | 文件 |
|---|---|
| 共用层（≥2 端涉及） | `02_design/system_features.md` |
| iOS 専属 | `03_dev/student_ios/IOS_DESIGN_LOG.md` |
| Android 専属 | `03_dev/student_android/ANDROID_DESIGN_LOG.md` |
| Web 専属 | `03_dev/teacher_web/WEB_DESIGN_LOG.md` |
| 后端 専属 | `03_dev/backend/BACKEND_DESIGN_LOG.md` |
| 点呼机 専属 | `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` |
| 物理硬件层 | `02_design/hardware_design.md`（板子选型 / 模块选型 / BOM）|

## 文档一致性

- 单源真值表 + pre-commit hook：`00_admin/文档同步点清单.md`
- 版本号 bump 流程：`.claude/skills/version-bump/SKILL.md`（CC 有否决权）
- 中文铁律：代码注释 + 内部文档 100% 中文 / UI 字符串保持日语（hook 实时扫描）
- 文件联动详见：`.claude/skills/file-linkage/SKILL.md`

## 会话开始 — 走 dmsd-startup skill

启动 SOP 完整版在 `.claude/skills/dmsd-startup/SKILL.md`。

## 会话结束 — 走 session-wrap skill

收尾 SOP 完整版在 `.claude/skills/session-wrap/SKILL.md`，触发关键词「收尾 / 整理今天 / 总结今天 / 记一下今天」自动加载。

git 状态确认（git status / 残留 / 未 push / stash）→ **会话结尾时**走 session-wrap §5.5.9，不在启动时跑。

---

# AC 记录协作（DMSD 特有 — always-on）

> **DMSD 是 itsuki 的核心 AC 叙事项目**。AC 是他最重要的事，跟「写代码 / 改文档」同等重要。

## 默认底线（5 条铁律 — 不依赖 skill 触发）

1. iCloud `05_产出/` 永不写 — itsuki 原创志望理由书 / 自我推荐书 / 面试准备
2. iCloud `03_素材_候选/` + `04_素材_成品/` 写需 itsuki 当场授权
3. `05_logs/decision_log.md` / `project_evolution.md` / `learning_path.md` **CC 直接 Edit 写**（记录类，不让 itsuki 做粘贴手活 — 详见 memory `feedback_no_handoff_work_back_to_itsuki.md`）；AC 叙事文档 + iCloud 仍归 itsuki
4. AC 叙事文档 `vX.Y.Z_AC叙事.md` itsuki 自己写，CC 等他来问才辅助，不主动起草
5. 叙事归属：raw 阶段写「AI 提了 X，我评估后采纳/拒绝/改造，理由是 Y」 — **不写"未完全理解"类自我贬低标记**

完整 AC 规则（3 根本原则 / 5 核心问题 / 5 级素材清单 / 模式 5 挖掘法 / 7 节收尾动作 / AC 文件家族权限速查）→ 全部在 `.claude/skills/session-wrap/SKILL.md`。

---

## Skills 继承

### 全局自动继承（`~/.claude/skills/` + plugin）

| skill | 干嘛 |
|---|---|
| **ac-radar** | 实时 AC 入试素材捕获（写中央 inbox + DMSD raw 段）|
| **anti-ai-flavor** | 反 AI 味（每次回复前 8 类自检 + 5 铁律 — 5-27 从 6 类升 8 类加 G 自指失败 + H 编造数据）|
| **cc-comm-rules** | 跟 itsuki 沟通的强制规则 |
| **session-coord** | 多终端会话协作板（防文件冲突）|
| **patina / patina-max** | 去 AI 味重写（AC 叙事文档慎用 patina-max — 违反默认底线第 4 条）|
| **diagnose** | 调试硬 bug 流程 |
| **tdd** | 测试驱动开发 |
| **grill-me** | 拷问设计 |
| **graphify** | 代码知识图谱（`graphify-out/GRAPH_REPORT.md`，改完代码跑 `graphify update .`）|
| **docx / xlsx / pptx / pdf** | 4 个文档生成 skill（AC 出愿 PDF 备用）|

### DMSD 项目专属（`.claude/skills/`）

| skill | 触发 | 干嘛 |
|---|---|---|
| **dmsd-startup** | always-on 启动时 | 5 件启动必做事 |
| **session-wrap** | 收尾 / 整理今天 / 总结今天 / 记一下今天 | AC 素材全量扫描 dump + git 状态确认 |
| **version-bump** | 迭代 / bump / 发版本 / 打 tag / 发版 / release | 版本决策树（CC 有否决权）+ 发版 SOP |
| **new-feature** | 新功能 X / 加 Y / 实装 Z / 做 W | 5 端实装模板（spec→backend→iOS→Android→点呼机）|
| **spec-sync** | 跨端检查 / 字段对齐 / API 对齐 | backend↔iOS↔Android 字段提取对比 |
| **file-linkage** | 联动 / 改 A 要查 B / 我改了 X 要查什么 | 文件联动矩阵（17 条规则 + 反向索引）|
| **project-overview** | X 文件在哪 / 项目里有 X 类文件吗 / 找文件 | 项目所有文件清单 + 状态 + AC 价值 |
| **memory-write** | 记一下规则 / 以后这样 / memory 加一条 | memory 写入 SOP（4 类型 / 查重 / 索引）|

## Hooks 继承

### 全局自动继承（`~/.claude/hooks/`，注册在 `~/.claude/settings.json`）

- `anti-ai-flavor-precheck.sh` — UserPromptSubmit 注入 8 类反面提醒（5-27 升级）
- `pre-bash-destructive-block.sh` — 拦 `rm -rf` / `git reset --hard` / `git push --force` 类危险命令（warn 模式，不阻断）
- `session-start-env-diff.sh` — SessionStart 对账实际装的工具 vs `~/.claude/我的环境.html`
- `session-start-coord-check.sh` — SessionStart 多终端协作板提醒（**DMSD 项目下静默退出**，由 dmsd-startup §2 接管）

### DMSD 项目专属（`00_admin/hooks/` + `bin/`）

7 PostToolUse + 1 PreToolUse + 1 SessionStart + git pre-commit。完整说明：`00_admin/hooks/README.md`。

| hook | 触发 | 干嘛 |
|---|---|---|
| `post-edit-sync-check.sh` | Write/Edit 后 | 实时联动检查 + demo scaffold 字眼检测 |
| `post-edit-memory-check.sh` | Write/Edit memory 目录后 | memory 索引检查 |
| `post-edit-japanese-comment-check.sh` | Write/Edit 代码文件后 | 日语注释扫描（违反中文铁律就提醒）|
| `post-edit-timestamp-check.sh` | Write/Edit WIP/TODO/progress 后 | 时间戳过期检查 |
| `post-edit-version-hardcode-check.sh` | Write/Edit 声明性文件后 | 硬编码版本号 `vX.Y.Z` 实时拦 |
| `post-edit-project-overview-check.sh` | Write/Edit 任何 DMSD 文件后 | project-overview 同步提醒 |
| `post-edit-format.sh` | Write/Edit 代码文件后 | 多语言自动格式化（ruff / swiftformat / ktlint / prettier）|
| `bin/check_overview_drift.sh` | SessionStart | project-overview §0.1 体量表跟 git ls-files 对账（dmsd-startup §2 也调）|
| `00_admin/hooks/pre-commit` | git commit 时 | 一致性检查 |

## 全项目中枢联动

中枢位置：`~/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/大学入試/全项目中枢/`

itsuki 名下 4 个项目（大学入試 / DMSD / Tango / QTS）互通的中央协同板。CC 实例之间不能直接调用（每个 CC 独立进程），靠中枢文件传信。

- **会话启动时**：来中枢读 `信箱/DMSD_inbox.md`，有新留言报告 itsuki
- **会话收尾时**：来中枢更新 `项目档案/DMSD.md` 的「现状一句话」+「最后更新日期」
- **想留言给别项目**：写到 `信箱/<对方>_inbox.md`（对方 = 大学入試 / Tango / QTS）
- **想知道别项目在干嘛**：读 `项目档案/<对方>.md` 或 `_中央板.md`

完整机制说明 → 中枢 `CLAUDE.md`

## 沟通规则（继承 `~/.claude/CLAUDE.md` 简版）

- **中文回答**
- 英文 / 日语 / 缩写第一次出现必翻译 + 一句解释
- 不假设任何先验知识
- 教练身份 — 解释「为什么」「是什么」，不只是「怎么做」
- anti-ai-flavor 8 类自检（A 术语裸露 / B 缺上下文 / C 复杂条件句 / D 网络黑话 / E 字面化执行 / F 客套腔 / G 自指失败 / H 编造数据）+ 5 铁律（起因 / 改哪+这是啥 / 改的内容 / 每对象解释 / 下一步推荐）
- 主动诊断 — 看到 itsuki 做法低效就当场点出，给具体原因
- 提选项用 A/B/C，不用甲乙丙
- 触发词「说人话」= 重写上一条 / 「单词白名单」= 列英文词让 itsuki 选 / 「翻车」= 记 inbox 做 5 字段分析
- 出练习题结合 DMSD 场景 — 点呼 / 扣分 / 签到

## Git

- 不写 `Co-Authored-By` trailer
- 不自动 push / tag
- 敏感文件（.env / API key / 账号密码）绝不 commit
- commit 前 pre-commit hook 自动跑一致性检查

## Agent skills（外部 Matt Pocock 套件）

外部 skill（grill-me / tdd / to-prd / to-issues / diagnose）的 per-repo 配置在 `docs/agents/`。DMSD 用 `00_admin/TODO.md` 单文件当 issue tracker（不是 GitHub Issues）。

详细 feedback 历史：`~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md` 索引（feedback_*.md 系列）
