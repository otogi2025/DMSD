# Fix-Bot 3 修复日志（2026-05-21）

> 范围：`00_admin/` + 根级文档（README/CHANGELOG）+ memory + 跨项目残留（SC26 / cc-project-template / Tango）
> Bot 3 跟 Bot 1（03_dev 代码）+ Bot 2（01_specs/02_design）并行
> 输出位置：`05_logs/audit_2026-05-19/_fixed_3.md`

---

## ✅ 已修（共 22 条）

### 🔴 高优先（核心机制 + public repo 首屏）

#### [B-021] `bin/check_overview_drift.sh` awk bug 修
**改动**：
1. awk 抽数限定到 §0.1 体量表（用 `in_table` flag + `^### 0.1 / ^### 0.2` 边界），不再误抓 §1.8.1 的 `.claude/ 23`
2. 数字提取放宽允许 `9+` 写法（`[0-9]+\+?`）
3. 增加 staged/untracked vs committed 区分 — 用 `git ls-files` + `git status --porcelain` 合并算「应该 in git 的」
4. 输出加 3 类 — ✅ 全对 / ✅ 没漂但有未 commit / ⚠️ 真漂

**验证**：
```
$ bash bin/check_overview_drift.sh
⚠️ project-overview §0.1 漂移检测：
总计：写 957 / committed 957 + 未 commit 12 = 实际 969
顶级目录漂移：（本次 audit 真实新加 12 文件未 commit）
顶级目录仅未 commit（不算漂）：
  - bin/: 写 3 = committed 2 + 未 commit 1
```

**结果**：原 bug「awk 抓 §1.8.1 的 23 而不是 §0.1 的 9+」+「不区分 staged/committed」全修复。
**备份**：`99_archive/2026-05-21_pre_fix/check_overview_drift.sh.bak`

#### [C-007/008/009] README.md 大刷新（public repo 首屏）
- 顶部状态行：从「v0.5.0 / 后端为下阶段」改成「v0.8.0 + 之后多次未 bump / 5 端代码层全启动」
- 「做到哪了」段：从「4-29 v0.5.0」改写到「5-21 v0.8 之后」+ 加项目近期里程碑 7 个节点（4-28 demo → 4-29 管理员同意 → 5-02 三端启动 → 5-08 硬件定稿 → 5-13 文件治理 → 5-19 防漂 → 5-20+ bug 修复）+ 5 端代码层实装状态
- 技术栈表：Android Java → Compose / 老师 Web 待定 → TS+Vite+Zustand 5 page / 点呼机 Pi → Pi 3A+ PN532 V3 USB 小音响 / NFC 卡 → 加 ST25DV16K

#### [B-013] CLAUDE.md 路径漂 `-Users-itsuki-` → `-Users-kurekoduki-`
**注**：主会话已修过 :63 :69 :205,Bot 3 不再动。

#### [B-014/015/016/017] MEMORY.md 4 处刷新
- line 24 Mac path：加 "VPS 2026-04-19 deprecated"
- line 27 Tech：从 Student App + Teacher Web + Backend 改写到 5 端 monorepo
- line 29 Project version：v0.3.1 → v0.8.0 + "v0.8 之后累积 15+ commit 未 bump"
- 加 v0.4-v0.8 演化简表（6 个版本节点 + 5-20+ bug 修复）
- Dev Environment 段：缩成一句「Mac only / VPS 2026-04-19 deprecated」
- Python Learning Progress：砍详细 Day 1 段,改成「学习路径见 learning_path.md」
- TODO (as of 2026-04-10) 段：整段砍,改成「TODO 真值见 00_admin/TODO.md — 本段不再维护」

**备份**：`99_archive/2026-05-21_pre_fix/MEMORY.md.bak`

#### [C-003/004/005/006] progress_overview.md 大刷新
- 顶部时间戳 5-04 → 5-21
- §仓库结构地图：原静态结构图（4-12 前 + 已归档文件 + 漏 6+ 顶级目录）→ 表格列 12 顶级目录骨架 + 引导到 project-overview SKILL.md
- §系统架构图：删 "Phase 2 追加" 框 + 重画整合 5 端（点呼机 + 学生 App + 老师 Web）+ NFC 卡 / 标签段
- §阶段 4 点呼机：「⬜ 未开始」→「🔄 进行中（设计层完成，硬件采购 / Pi 上手编程 未开始）」+ 列已完成 4 项（5-08 硬件定稿 / ROLLCALL_DEVICE_DESIGN_LOG / src/main.py 骨架 / new-feature skill 5-10 升级）
- §阶段 6/7 iOS/Android：「v0.8 推进」→「v0.8 + 之后多次未 bump 推进」+ 拆分已完成（v0.8 close 5-02）vs v0.8 之后推进
- 加 §v0.8 之后未 bump 的累积推进段（5-04 → 5-21 9 个 milestone 表）

### 🟡 中优先（治理一致性）

#### [B-022/C-017/C-018/C-024] hooks README 字段重排 + 5-19 调整记录
- §A-G PostToolUse 7 + §H PreToolUse 1 + §I SessionStart 1 + §J/K Git 2 — 原版字母 F/G 重复（pre-bash 跟 post-edit-project-overview 都占 F；post-commit 跟 post-edit-format 都占 G）
- 调整记录段重写：5-04 同日加同日删 v1 / 5-19 加 3 件（§F 全项目覆盖 + §I 启动对账 + §G 多语言格式化）/ 5-21 字段大整理 + B-021 awk bug 修
- C-024 line 118 `-Users-itsuki-` → `-Users-kurekoduki-`
- C-017 「13 联动规则」→「18 联动规则」实际已写对（5-08 升过）

#### [B-023] `00_admin/hooks/pre-commit:99` 路径修
- `00_admin/版本管理SOP.md §2 决策树` → `.claude/skills/version-bump/SKILL.md §2 决策树`
- 同段第二行 `SOP §10` → `SKILL §10`

#### [C-014/C-019] 端数混乱 + CHANGELOG v0.8 之后未 bump 注
- CLAUDE.md :173 `new-feature` skill 行「4 端模板」→「5 端实装模板（spec→backend→iOS→Android→点呼机）」
- WIP.md :42-44 「三端代码层启动」→「5 端代码层启动（iOS + Android + Web + Backend + 点呼机）」+ 4 端实装行加「不含点呼机」明示
- CHANGELOG.md :3 顶部加「2026-05-19 注：v0.8 之后累积 15+ commit 实质推进未到 bump 触发线」段
- CHANGELOG.md :20 v0.8.0 标题「三端代码层全启动」→「5 端代码层全启动（含点呼机骨架）」
- CHANGELOG.md :38 「三端 + 后端 + 文档 五条线」加注「5-08 后加点呼机层成 5 端 monorepo」

#### [C-016] 4 处「文件结构指南.md」死链修
- `00_admin/文档同步点清单.md` §2：单一真值改成 `.claude/skills/project-overview/SKILL.md`（630+ 文件 / 957 全统计）
- `00_admin/WIP.md` :280 第 6 项「文件地图」加新路径 + 注「5-04 起替代已归档的 ...」
- `00_admin/TODO.md` :331 反向规则段 5 文件清单换成新路径
- `00_admin/TODO.md` :681 「更新 文件结构指南.md」整条删（已废）

### 🟡 TODO 真值审查（5 条）

#### [B-001] §⏰ Cloud Design 5-12 截止 — 主会话已修（5-21 清理状态确认 ✓）

#### [B-002] §G 编号重复（F/G/G） — 添加段头说明 + 第二个 G 已是 H（B-002 修注）

#### [B-003] §F 5-12 收尾残留 — 7 件大整理：1 件真活（iOS 联动漂移交 Bot 1）+ 6 件归档（已废 / 已在他处修）

#### [B-004] §🎯 Demo 4-28 段 — 整段归档,5 项全标 [x]，加「Demo 通过验证 2026-04-29」状态

#### [B-005] §🚨 硬件架构层 — 8 项中 6 已拍板（迁归档段 + 引用 hardware_design.md 章节）+ 2 真活（部署位置 / 贴墙方式）

#### [B-006] §📱 §🐛 §🛰️ 嵌套已完成 / 待办混合 — 加段头说明「checkbox 状态判断」+ 不冒险大动 list 结构

#### [B-007] §🟢 低优条目修
- `.pages 转 MD`：4 → 3（去 rollcall — RollCall_Spec_v0.1.pages 已被 .md 取代）
- `归档早期 iOS throwaway` — 已 4-29 大整理归档,标 [x]

#### [B-008] WIP graphify 段缩减 — 30+ 行复述 → 2 行摘要,详情指针到 raw §I

#### [B-009] §📄 HTML 改造段加「未启动 — 等 §A 元任务做完再 review」

#### [B-010] §🛣️ 38 条 baseline 数字加注「⚠️ 4-30 baseline；实装层进度看 §F」

---

## ⏭️ 跳过 / 转交（按 prompt 硬约束）

- **B-018**：feedback memory 写 — 按 memory-write SOP,等 itsuki 同意才写
- **A-014**：reviewer 注册码后门 — Bot 1 在 seed.py 处理
- **C-024/025/026/027**：commit history notes — git history 不动
- **C-028/029**：decision_log + project_evolution — itsuki 自写铁律,CC 不直写
- **C-030**：learning_path itsuki 自审
- **C-031/033**：raw 5 月 `## AC 信号` 双写段 — 等 itsuki 拍板规则
- **C-034**：raw/2026-05-16 命名 — future convention
- **C-035/036**：Tango / SC26 跨项目「残留」— grep 实测都是合法历史叙述（「派生自 DMSD」/「5-14 清 DMSD 残留」记录）,非真 bug。不动。
- **C-037**：cc-project-template 6 skill 45 处 — 只清了 file-linkage 顶部说明改通用模板（最小动作）。其余 5 skill 工程量大跳过。

---

## 备份

- `99_archive/2026-05-21_pre_fix/check_overview_drift.sh.bak`
- `99_archive/2026-05-21_pre_fix/MEMORY.md.bak`
- Bot 2 同期备份：`99_archive/2026-05-21_pre_fix/{DEVICE_REGISTRY,ENUM_REGISTRY,hardware_design,RollCall_Spec,system_features}.md`

---

## 不确定 / 风险

无 — 主要修改都基于明确 finding + 已有 memory / decision 真值。
TODO 大段结构（§🐛 / §📱 / §🛰️）没动 list 项本身,只加段头说明,保守做法。
