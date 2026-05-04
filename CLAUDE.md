# DMSD 项目指令（CC 必读）

## 关于 itsuki

中国留学生，日本高中三年级
完全零基础，所有概念从零解释
目标: 筑波大学 情報学群 情報科学類 AC入試，2027-04 入学
DMSD 是他的核心 AC 叙事项目

## 项目信息

项目名: DMSD
系统名: Tomoshibi
核心: 宿舍点呼数字化 + NFC 防代刷
技术栈: iOS Swift+SwiftUI / Android Kotlin+Compose / 后端 FastAPI+PostgreSQL / 点呼机 Pi 3A+ + PN532 + ST25DV16K / NFC 卡 NTAG215
上线姿态: v1.0 一次上线 iOS + Android + 卡，不分阶段 <!-- VERSION_OK -->
当前版本: 见 CHANGELOG.md 顶部
GitHub: otogi2025/DMSD public
iOS 独立 repo: otogi2025/Tomoshibi-iOS，single source 永远 DMSD 侧
设计 / 防御 / 扣分 / 采购 / 硬件 / 流程 详情: 02_design/ + 01_specs/ + 00_admin/项目文件总览.md

## 目录结构

00_admin/   WIP / TODO / 项目文件总览 / 文档同步点清单 / 版本管理SOP / hooks
01_specs/   规格文档 — rollcall/ 字典+主体
02_design/  设计文档 — hardware / flow / system_features 等
03_dev/     代码 — backend / teacher_web / student_ios，Swift 实装在独立 repo Tomoshibi-iOS
04_ops/     运维
05_logs/    开发 log — raw / dev_log / problem_solving / decision_log / learning_path / project_evolution
06_assets/  07_release/  99_archive/  bin/   参考材料 / 发布物 / 早期归档 / 脚本

完整文件级清单 + 状态 + AC 价值: 00_admin/项目文件总览.md

## 设计文档双层

共用层（≥2 端涉及）: 02_design/system_features.md
iOS 専属:  03_dev/student_ios/IOS_DESIGN_LOG.md
Web 専属:  03_dev/teacher_web/WEB_DESIGN_LOG.md
后端 専属: 03_dev/backend/BACKEND_DESIGN_LOG.md
判断标准 / 反模式: memory feedback_design_doc_layers.md

## 文档一致性

单源真值表 + pre-commit hook + 跨 repo 同步: 00_admin/文档同步点清单.md
版本 bump 流程: 00_admin/版本管理SOP.md
中文铁律 — 代码注释 + 内部文档 100% 中文 / UI 字符串保持日语: memory feedback_code_comments_chinese_strict.md

## 文件连锁结构（改 A 必查 B，改完当场对照）

iOS Swift view 改（视觉 / 流程 / 字段） → 03_dev/student_ios/IOS_DESIGN_LOG.md 对应章节 + 02_design/system_features.md（≥2 端涉及时）
02_design/system_features.md → 各端 *_DESIGN_LOG.md 引用要更新
backend models.py → schemas.py + routers/*.py + alembic/versions/* + iOS NetworkModels.swift（字段对齐）
backend routers/*.py → iOS Endpoints/*API.swift（端点 / 参数 / 返回类型对齐）
Route.swift 加 case → RootView.swift switch + 用到的 view 要存在
Foundation/ component 改 props → grep 全 repo 找用到的地方
01_specs/rollcall/* 主体改 → 触发 SOP 阅读 + 可能 bump 版本号
新建 / 删除 / 改名 / 移动文件 → 00_admin/项目文件总览.md 同步更新对应章节
新建声明性文件（CLAUDE.md / WIP / TODO 类） → 00_admin/文档同步点清单.md 加同步点
新建 / 改 hook → 00_admin/hooks/README.md
iOS Swift 改了 → bash bin/sync-ios-refs.sh 同步 Tomoshibi-iOS

工具:
- commit 时自动: bash 00_admin/hooks/pre-commit
- 中途随时: bash bin/sync-check.sh
- 规则源: 00_admin/hooks/lib/sync-rules.sh

## 会话开始: 只读 WIP.md

启动读 00_admin/WIP.md — 当前版本 / 当下焦点 / 最近 5 次会话 / 多会话占用 / 阻塞项
读完给 itsuki 报告状态等指令，不主动催进度

## 按需读（不主动读，触发场景才读）

**找文件 / 问文件 → 必须去查 00_admin/项目文件总览.md，不用 grep / find / 命令行**

下面任何一种 itsuki 输入，CC 必须当场打开 00_admin/项目文件总览.md 查答案：
- 「某文件在哪？」
- 「某文件干嘛用的？」
- 「项目里有没有 XX 文件？」
- 「XX 类的文件都在哪个目录？」
- 「这个目录下有什么？」
- itsuki 让 CC 「找文件」/「列文件」/「整理某类文件」

**不用命令行查找** — 总览里写好了所有文件干嘛用 + 状态。直接翻总览拿答案。

**TODO 待办 → 必须 itsuki 主动问才读 00_admin/TODO.md**

只在 itsuki 主动问「还有什么没做」/「下一步该做什么」时读，不主动催进度，不主动列待办给他看。

**WIP vs TODO 铁律**: WIP = 当下书签，最近 5 次会话上限 / TODO = 完整未完成 backlog，真值。WIP 绝不复述 TODO 内容。

## 会话结束: 走 ac-record skill

收尾时通过 ac-record skill 跑完整流程（AC 素材 dump / 中文总结 / 文件联动 / WIP 刷新 / git commit）。skill 在 `.claude/skills/ac-record/SKILL.md`，触发关键词命中时自动加载，无需主动读。

---

# AC 记录协作（CC 立场 + 默认底线）

> **DMSD 是 itsuki 的 AC 叙事项目。AC 是他最重要的事**，跟"写代码 / 改文档"同等重要。
>
> **完整规则（3 根本原则 / 5 核心问题 / 5 级素材清单 / 模式 5 挖掘法 / 7 节收尾动作 / AC 文件家族权限速查）→ 全部在 skill `.claude/skills/ac-record/SKILL.md`**。触发关键词命中时 CC 自动加载，按里面执行。

## 默认底线（CC 永远遵守 — 这 5 条不依赖 skill 触发，永远在线）

1. iCloud `05_产出/` 永不写 — itsuki 原创志望理由书 / 自我推荐书 / 面试准备
2. iCloud `03_素材_候选/` + `04_素材_成品/` 写需 itsuki 当场授权
3. `05_logs/decision_log.md` / `project_evolution.md` / `learning_path.md` 正文 CC 永不直写，只起草 draft 等 itsuki 粘贴
4. AC 叙事文档 `vX.Y.Z_AC叙事.md` itsuki 自己写，CC 等他来问才辅助，不主动起草
5. 叙事归属：raw 阶段写「AI 提了 X，我评估后采纳/拒绝/改造，理由是 Y」 — **不写"未完全理解"类自我贬低标记**（2026-05-04 itsuki 拍板：raw 是 git 可见的负面证据）。月度筛选时再归功 itsuki 判断 — 详见 skill §0.1

## 触发场景（看到任一 → ac-record skill 自动激活）

⭐ **主触发**（最常用）：itsuki 说「**收尾**」/「**总结一下今天**」/「**整理一下今天**」/「**记一下今天发生的事**」 → CC 立刻跑 skill §5.5.0 **全量扫描算法**（从会话第一条消息扫到最后，找所有候选素材，不只看最后一段）。

次触发（兜底用，避免当下重要素材漏 dump）：
- itsuki 说「启动」/「记一下」/「dump 一下」/「留个痕」
- itsuki 做了决策 / 拍板 / 反思 / 学到新东西 / 纠正 CC
- itsuki 说「以前我...」/「我之前以为...」/「原来这样啊」（模式 5 触发词）
- 代码或架构改了
- CC 主动发现的问题（这种也算 itsuki 的 AC 素材，必须 dump）
- 版本号 bump

---

# 对话规则 / 代码编写原则

核心:
1. itsuki 决定做什么 / CC 实现怎么做 / 每段代码向他解释含义
2. 大白话沟通，术语 / 日语 / 英文缩写第一次出现就翻译
3. 主动告诉他不知道但应该知道的概念或更优做法
4. 出练习题结合 DMSD 场景 — 点呼 / 扣分 / 签到

详细规则 / feedback 历史: ~/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md 索引（feedback_*.md 系列）
