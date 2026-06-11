# DMSD 项目指令（CC 必读）

## ⚠️ 沟通铁律 — 不主动用英语名词

除非这个词在项目代码 / 文档 / 文件名里真出现过，否则一律用中文。比如别说「凭证 credential」「兜底 fallback」「联动 sync」，直接说中文。

**不要默认认为 itsuki 认识项目里的各种名词和英语单词**。哪怕这个词在项目里真出现过，CC 第一次提到它时也要带一句解释「这是什么 / 在哪出现 / 干嘛用的」。例如说「`models.py`」要补一句「这是 backend 后端的数据库表定义文件」；说「FC-024」要补一句「这是系统 bug 专栏里的编号，指 teacher_web 明文密码漏洞」。itsuki 是零基础 + 项目体量 1400+ 文件 + 5 端联动，记不住所有代号 / 缩写 / 文件名 / 角色名。

完整规则在 `~/.claude/CLAUDE.md`。

## ⭐⭐⭐ dmsd-startup 强制加载

每次会话启动 **第一件事** 先 Read `.claude/skills/dmsd-startup/SKILL.md`，按 §2 顺序执行。**步骤内容以 skill §2 为唯一真值，本文件不复述**（历史上复述过的两处都漂移了 — 联动 Rule 27 兜底）。

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
| `00_admin/` | WIP / TODO / 项目文件总览 / 文档同步点清单 / hooks / `handoff/`（AI 会话间交接件，用完移 99_archive，见 `00_admin/handoff/README.md`）|
| `01_specs/` | 规格文档 — rollcall/ 字典 + 主体 |
| `02_design/` | 设计文档 — hardware / flow / system_features 等 |
| `03_dev/` | 代码 — backend / teacher_web / student_ios / student_android / rollcall_device（点呼机）|
| `04_ops/` | 运维 |
| `05_logs/` | 开发 log — dev_log / problem_solving / decisions/（决策日志双文件）/ learning_path / project_evolution。**raw（AC 素材详细叙事）已迁 iCloud 素材池**（路径见 session-wrap skill §3.1），仓库 `05_logs/raw/` 只剩指路牌 README |
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

## 各端构建 / 测试防坑（实测验证过，CC 跑命令前先看）

- **项目根目录没有任何技术栈配置文件** — 5 端各自埋在 `03_dev/<端>/v1/` 下，在根目录跑 `pytest` / `npm test` 必失败。先 cd 进对应端再跑。
- **后端测试必须用项目自带虚拟环境** — 系统 Python 没装 fastapi，裸跑 `pytest` 必败。正确：`cd 03_dev/backend/v1 && .venv/bin/python -m pytest`（全量约 3 分钟）。
- **iOS 演示版直接用 `TomoshibiAppDemo` scheme 构建** — 不要按 BUILD.md 老办法手动加 `SWIFT_ACTIVE_COMPILATION_CONDITIONS`。正式版 scheme 是 `TomoshibiApp`，destination 用 `iPhone 17 Pro` 模拟器。
- **Xcode 里手动改的工程配置必须写进 `project.yml`** — xcodegen 重新生成 pbxproj 时会把手动配置全部擦掉。
- **改完哪端，必须跑哪端的验证再报完成** — 后端 → pytest 全绿（中途可只跑改动相关的测试文件，收尾前全量）；iOS → 双 scheme 都 BUILD SUCCEEDED；Android → `./gradlew assembleDebug`；老师网页 → `npm run build`。编译 / 测试是机器跑的、对话里只占几行字，跳过它 = 没验证就报完成。
- **Write/Edit 代码后 hook 会自动格式化**（ruff / swiftformat / ktlint / prettier 分语言接管）— 副作用：加 import 必须同一次改动带上用法，分两步加的话 ruff 当场删掉「还没被用到」的 import。

## 会话结束 — 走 session-wrap skill

收尾 SOP 完整版在 `.claude/skills/session-wrap/SKILL.md`，触发关键词「收尾 / 整理今天 / 总结今天 / 记一下今天」自动加载。

git 状态确认（git status / 残留 / 未 push / stash）→ **会话结尾时**走 session-wrap §5.5.9，不在启动时跑。

---

# AC 记录协作（DMSD 特有 — always-on）

> **DMSD 是 itsuki 的核心 AC 叙事项目**。AC 是他最重要的事，跟「写代码 / 改文档」同等重要。

## 默认底线（5 条铁律 — 不依赖 skill 触发）

1. iCloud `05_产出/` 永不写 — itsuki 原创志望理由书 / 自我推荐书 / 面试准备
2. iCloud `03_素材_候选/` + `04_素材_成品/` 写需 itsuki 当场授权
3. `05_logs/decisions/decision_log.md` / `project_evolution.md` / `learning_path.md` **CC 直接 Edit 写**（记录类，不让 itsuki 做粘贴手活 — 详见 memory `feedback_no_handoff_work_back_to_itsuki.md`）；AC 叙事文档 + iCloud 仍归 itsuki
4. AC 叙事文档 `vX.Y.Z_AC叙事.md` itsuki 自己写，CC 等他来问才辅助，不主动起草
5. 叙事归属：raw 阶段写「AI 提了 X，我评估后采纳/拒绝/改造，理由是 Y」 — **不写"未完全理解"类自我贬低标记**

完整 AC 规则（3 根本原则 / 5 核心问题 / 5 级素材清单 / 模式 5 挖掘法 / 7 节收尾动作 / AC 文件家族权限速查）→ 全部在 `.claude/skills/session-wrap/SKILL.md`。

---

## Skills 继承

### 全局自动继承（`~/.claude/skills/` + plugin）

全局 skill / hook 清单的真值 = `~/.claude/我的环境.md`，各 skill 靠自己的说明文字自动触发，不在此罗列。DMSD 特有注意事项只有两条：

- **patina / patina-max**（去 AI 味重写）：AC 叙事文档慎用 patina-max — 违反 AC 默认底线第 4 条
- **graphify**（代码知识图谱）：改完代码跑 `graphify update .`，产出在 `graphify-out/GRAPH_REPORT.md`

### DMSD 项目专属（`.claude/skills/`）

| skill | 触发 | 干嘛 |
|---|---|---|
| **dmsd-startup** | always-on 启动时 | 启动必做事（内容以 skill §2 为真值，此处不复述）|
| **session-wrap** | 收尾 / 整理今天 / 总结今天 / 记一下今天 | AC 素材全量扫描 dump + git 状态确认 |
| **version-bump** | 迭代 / bump / 发版本 / 打 tag / 发版 / release | 版本决策树（CC 有否决权）+ 发版 SOP |
| **new-feature** | 新功能 X / 加 Y / 实装 Z / 做 W | 5 端实装模板（spec→backend→iOS→Android→点呼机）|
| **spec-sync** | 跨端检查 / 字段对齐 / API 对齐 | backend↔iOS↔Android 字段提取对比 |
| **file-linkage** | 联动 / 改 A 要查 B / 我改了 X 要查什么 | 文件联动矩阵（条数以 `sync-rules.sh` 为准，不在此硬编码）|
| **project-overview** | X 文件在哪 / 项目里有 X 类文件吗 / 找文件 | 项目所有文件清单 + 状态 + AC 价值 |
| **memory-write** | 记一下规则 / 以后这样 / memory 加一条 | memory 写入 SOP（4 类型 / 查重 / 索引）|
| **codex-review** | codex 审查 / 派 codex 审 / codex 挑刺 / codex 找 bug / 让 codex 审一下（**须带「codex」字样**）| 派 codex（gpt-5.5 xhigh）只读审本会话改动 → CC 逐条裁决 + 修 → 复审 → 跑到收敛 |

## Hooks

hook 注册真值 = `~/.claude/settings.json`（全局）+ `.claude/settings.json`（DMSD 项目）— 本文件不罗列清单，要查看注册表。项目 hook 逐个说明：`00_admin/hooks/README.md`；git pre-commit 在 `00_admin/hooks/pre-commit`。

## 全项目中枢联动

中枢 = itsuki 名下 4 个项目（大学入試 / DMSD / Tango / QTS）互通的中央协同板：`~/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/大学入試/全项目中枢/`。启动读信箱已并入 dmsd-startup、收尾更新档案已并入 session-wrap，不在此复述。想给别项目留言 → 写中枢 `信箱/<对方>_inbox.md`；想看别项目动态 → 读 `项目档案/` 或 `_中央板.md`。完整机制 → 中枢 `CLAUDE.md`。

## 沟通规则

全套继承 `~/.claude/CLAUDE.md`（中文 / 翻译术语 / 零基础 / 教练身份 / 不编造 / A/B/C 选项），不在此重抄。DMSD 补充一条：出练习题结合 DMSD 场景 — 点呼 / 扣分 / 签到。

## Git

- 不写 `Co-Authored-By` trailer
- 不自动 push（本地 commit / bump / tag 可自主 — 见 memory `feedback_commit_push_tag_division.md`）
- 敏感文件（.env / API key / 账号密码）绝不 commit
- commit 前 pre-commit hook 自动跑一致性检查
- ⭐ **做完一件事立刻 commit，不攒到收尾** — 一个功能 / 一个 bug 修复 / 一份文档改动 = 当场一个 commit，用显式文件路径提交（防卷走别会话改动）。理由：① 多会话共用工作区，未提交改动会被别的窗口覆盖（5-30 / 6-04 真事故）② 收尾时多件事混在工作区拆不开、commit 历史回溯不清。收尾时如工作区仍混着多件未提交的事 → 按文件分组拆成多个 commit（`git add -p` / 显式路径），不打包成一个

## Agent skills（外部 Matt Pocock 套件）

外部 skill（grill-me / tdd / to-prd / to-issues / diagnose）的 per-repo 配置在 `docs/agents/`。DMSD 用 `00_admin/TODO.md` 单文件当 issue tracker（不是 GitHub Issues）。

详细 feedback 历史：`~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md` 索引（feedback_*.md 系列）
