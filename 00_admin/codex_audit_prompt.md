# Codex 用 — DMSD 项目全量审查 prompt

> **用法**：itsuki 把下面 `<prompt>` 内的全部内容复制粘贴给 codex（OpenAI 的 GPT-5 命令行工具 / chat 入口）。
> **创建于**：2026-05-21（4 会话审查作战后，itsuki 想让 codex 独立第二轮）
> **跟 Claude 第一轮的关系**：Claude 已派 3 子代理审过 131 条 findings（见 `00_admin/系统bug专栏.md`），codex 这次是**独立第二轮** — 补漏 / 复核 / 找 Claude 漏的

---

<prompt>

# 任务：DMSD 项目全量审查（独立第二轮）

## 你是谁

OpenAI Codex（OpenAI 的代码 / 推理工具），被 itsuki 派来对 DMSD 项目做完整审查。

之前 Claude（Anthropic 的 AI）已派 3 个子代理审过一轮（131 条 findings 记录在 `00_admin/系统bug专栏.md`）。**你是独立第二轮** — 补漏 / 复核 / 找 Claude 漏的。

## itsuki 背景

- 中国留学生 / 日本高三 / **零编程基础**
- 升学目标：筑波大学 情報学群 情報科学類 AC 入試（2027-04 入学，出愿期 2026-08~09）
- DMSD 是 itsuki 的核心 AC 叙事项目，public GitHub repo（otogi2025/DMSD）
- **沟通用中文** — 英文 / 缩写 / 简写第一次出现必须带中文翻译

## DMSD 项目背景

- **项目名（仓库代号）**：DMSD（Dormitory Management System Digitalization — 宿舍管理系统数字化）
- **系统名（对外）**：Tomoshibi（灯火 / ともしび）
- **核心**：宿舍点呼数字化 + NFC（近场通信）防代刷
- **5 端**：
  - iOS Swift + SwiftUI（苹果手机原生 App）
  - Android Kotlin + Compose（安卓原生 App）
  - 老师 Web TypeScript + Vite + Zustand（老师管理界面）
  - 后端 FastAPI + PostgreSQL（Python 异步 Web 框架 + 关系数据库）
  - 点呼机 Raspberry Pi 3A+ + PN532 NFC reader + ST25DV16K 卡（树莓派 3A+ + 近场通信读卡器 + 动态 NFC 贴纸）
- **v1.0 上线姿态**：iOS + Android + NFC 卡 一次上线（4-19 G2 决策取消分阶段）
- **当前版本**：见 `CHANGELOG.md` 顶部（v0.8.0 + 之后多次未 bump 推进）

## 项目根

```
/Users/kurekoduki/dev/DMSD/
```

## 项目结构

```
00_admin/         管理文档（WIP / TODO / progress_overview / 文档同步点清单 / hooks / 系统bug专栏）
01_specs/         规格文档（rollcall/ 字典 + 主体）
02_design/        设计文档（hardware / flow / system_features）
03_dev/           5 端代码（backend / teacher_web / student_ios / student_android / rollcall_device）
04_ops/           运维
05_logs/          开发 log（raw / decision_log / project_evolution / learning_path / audit_*/）
06_assets/        参考材料
07_release/       发布物
99_archive/       早期归档（已废文件）
bin/              脚本（含启动对账 / 联动检查）
.claude/          Claude Code 配置（settings / skills / agents / sessions）
```

## 必读文件清单（按顺序读）

### 顶层指令 + 状态

1. `CLAUDE.md` — 项目顶层指令（含联动矩阵 17 条 / 5 端结构 / 沟通规则 / AC 叙事铁律）
2. `00_admin/WIP.md` — 当下书签 + 最近 5 会话 + 多会话占用
3. `00_admin/TODO.md` — 完整未完成 backlog（顶部含 §🐞 系统 Bug 专栏入口 + §🆕 v1.0 后新功能候选）
4. **`00_admin/系统bug专栏.md`** — **Claude 第一轮找到的 131 条 bug**（你跟这个对照，每条标「重复 / 独立发现 / Claude 漏」）
5. `00_admin/progress_overview.md` — 阶段进度快照（给 itsuki + 教授读）
6. `CHANGELOG.md` — 版本变更编年史
7. `README.md` — public GitHub repo 首屏

### Claude 维护的项目总览（重点扫漂移）

8. **`.claude/skills/project-overview/SKILL.md`** — **DMSD 项目所有文件清单 + 每个文件干嘛 + 状态（650+ 行）**

**重点扫这个文件的漂移**：
- SKILL.md 列的文件 实际不存在（死链）？
- 实际存在但 SKILL.md 没列（孤儿文件）？
- SKILL.md §0.1 体量表数字（写 X / 实际 Y）漂移？跑 `git ls-files | wc -l` 验证
- SKILL.md 每个文件描述跟实际内容是否匹配？

⚠️ Claude 第一轮没逐条对照 `ls -R` 验证 SKILL.md — 这是 Claude 可能漏的最大点。

### 规格 + 字典 + 设计

9. `01_specs/rollcall/RollCall_Spec.md` — 点呼系统主规格（~1000 行）
10. `01_specs/rollcall/ENUM_REGISTRY.md` / `FIELD_REGISTRY.md` / `ERROR_CODES.md` / `DEVICE_REGISTRY.md` — 字典三件套（枚举 / 字段 / 错误码 / 设备）
11. `02_design/system_features.md` — ≥2 端共用层真值（5 端引用基础）
12. `02_design/flow_design.md` — 端到端流程图
13. `02_design/hardware_design.md` — 物理硬件层（Pi 选型 / 模块 / BOM / 接线 / GPIO）

### 5 端设计 + 代码

14. `03_dev/student_ios/IOS_DESIGN_LOG.md` + `v1/TomoshibiApp/`（iOS Swift+SwiftUI 代码）
15. `03_dev/student_android/ANDROID_DESIGN_LOG.md` + `v1/app/`（Android Kotlin+Compose 代码）
16. `03_dev/teacher_web/WEB_DESIGN_LOG.md` + `v1/src/`（老师 Web TypeScript+Vite 代码）
17. `03_dev/backend/BACKEND_DESIGN_LOG.md` + `v1/app/`（后端 FastAPI 代码）+ `v1/alembic/`（数据库迁移）+ `v1/tests/`（测试）
18. `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` + `src/`（点呼机软件层 — 大部分还是 placeholder）

### AC 叙事 + 历史

19. `05_logs/decision_log.md` / `project_evolution.md` / `learning_path.md` — AC 叙事三件套（**注意**：这些是 itsuki 自己写的，CC / codex **不直写** — 只起草 draft 等 itsuki 粘贴）
20. `05_logs/raw/*.md` — 每日开发原始日志
21. **`05_logs/audit_2026-05-19/`** — **Claude 第一轮 audit 全套结果**：
    - `session_A_findings.md` / `session_B_findings.md` / `session_C_findings.md` — 3 子代理各自 findings
    - `_master_issues.md` — 主会话汇总 + TOP 10
    - `_fixed_1.md` / `_fixed_2.md` / `_fixed_3.md` — 3 子代理修了什么

### 配置 + 工具 + memory

22. `.claude/settings.json` — Claude Code 钩子（hook — 事件触发的脚本）注册
23. `00_admin/hooks/README.md` + `00_admin/hooks/*.sh` — 项目级钩子
24. `00_admin/hooks/lib/sync-rules.sh` — 联动规则源
25. `bin/check_overview_drift.sh` + `bin/sync-check.sh` — 启动对账 + 联动检查脚本
26. `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/MEMORY.md` — Claude 持久记忆索引
27. `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_*.md` + `project_*.md` — itsuki 拍板规则归档

## 审查维度（17 维 — 跟 Claude 3 子代理一样）

### 第一档（必审）
1. **跨端字段对齐** — backend `models.py` / `schemas.py` vs iOS `NetworkModels.swift` vs Android entity vs Web TypeScript types
2. **联动矩阵全过** — `CLAUDE.md` §文件连锁结构 列的 17 条「改 A 必查 B」规则
3. **设计文档分层一致** — `system_features.md`（共用层）vs 5 端 `*_DESIGN_LOG.md` 引用
4. **demo scaffold（demo 用脚手架代码）清单 vs 实际代码** — `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/project_demo_scaffolds_to_remove_before_v1.md`
5. **NFC 安全审查** — ECDSA（椭圆曲线签名）/ nonce（一次性随机数防 replay 重放）/ 学生注册码后门 / 鉴权漏洞 / 输入验证

### 第二档（该审）
6. **规格主体一致性** — RollCall_Spec.md vs 字典三件套术语对齐
7. **物理硬件 vs 点呼机软件** — `hardware_design.md` vs `ROLLCALL_DEVICE_DESIGN_LOG.md` vs `src/`
8. **memory 索引完整性** — MEMORY.md 索引 vs 实际 feedback / project 文件
9. **挂钩系统审查** — `00_admin/hooks/*.sh` + `.claude/settings.json` 注册 + `bin/*.sh`
10. **TODO.md 真值审查** — 已完成项还挂 / 跟 WIP 重叠 / 过期项

### 第三档（长尾 + 精读）
11. **AC 叙事时间线** — decision_log / project_evolution / learning_path 时间一致
12. **commit history vs 实际改动** — git log message vs git show diff 抽样比对
13. **AC 素材漏抓** — raw/ 模式标记 vs 中央 inbox 双写段
14. **跨项目残留** — `~/dev/SC26/.claude/skills/` + `~/dev/cc-project-template/.claude/skills/` + `~/dev/Tango/.claude/skills/` 含 DMSD 字眼
15. **依赖 CVE（已知漏洞编号 — Common Vulnerabilities and Exposures）** — Python `requirements.txt` / iOS `Package.swift` / Android `build.gradle`
16. **后端测试** — `03_dev/backend/v1/tests/` 覆盖 + `.github/workflows/` CI（持续集成）配置
17. **逐字精读** — 所有声明性文件（CLAUDE.md / WIP / TODO / progress_overview / README / CHANGELOG / spec / DESIGN_LOG）笔误 / 错字 / 引用失效 / 数字日期版本号自相矛盾

## ⭐ 重点 — Claude 第一轮可能漏的（你重点扫）

1. **`project-overview/SKILL.md` 自身漂移** — 列项目所有文件清单 + 状态。Claude 第一轮**没逐条对照 `ls -R` 验证**。请你重点扫：
   - SKILL.md 列的文件 实际不存在（死链）？
   - 实际存在但 SKILL.md 没列（孤儿）？
   - §0.1 体量表数字漂移？
   - 每个文件描述准吗？

2. **代码层细节漏检**：
   - backend `routers/*.py` 全部 endpoint（HTTP 端点）是否在 spec 里有对应？
   - iOS `Features/*/Views.swift` 每个 view 是否在 IOS_DESIGN_LOG 引用？
   - alembic（数据库迁移工具）迁移文件序号是否单调递增 / 无冲突？

3. **跨端 Optional 一致性** — Claude 第一轮没深扫：
   - backend `Optional[X]` Python 字段
   - iOS `X?` Swift 字段
   - Android `X?` Kotlin 字段
   - Web `X | undefined` TypeScript 字段
   - 4 端 Optional 含义对齐吗？

4. **配置文件完整性**：
   - `pyproject.toml` / `package.json` / `requirements.txt` 依赖管理文件
   - `.gitignore` 是否漏了敏感文件（.env / *.pem / secrets/）
   - `.env.example` 是否完整覆盖 production 必填环境变量

## 输出

写到 `/Users/kurekoduki/dev/DMSD/05_logs/audit_2026-05-21_codex/session_codex_findings.md`（目录不存在自己 mkdir 建）

格式：

```markdown
# Codex Findings — 2026-05-21 独立第二轮审查

## 总览

- 🔴 阻塞上线：N 条
- 🟡 该修：M 条
- 🟢 优化 / 信息：K 条
- 跟 Claude 重复：X 条（标 [重复 A-001 等]）
- Claude 漏的 / Codex 独立发现：Y 条

## 维度 N — <维度名>

### [Codex-001] 🔴 标题简短

- 位置：`相对路径:行号`
- 描述：发现的具体问题
- 建议改法：怎么修
- 跟 Claude 关系：N/A | 「重复 A-001」| 「Claude 漏 — 独立发现」
```

## 硬约束

1. **只审 + 列问题，不改文件**（itsuki 拍板「audit 不是 fix」铁律）
2. 每条问题：`file:line` + 描述 + 建议改法 + 严重程度（🔴 阻塞上线 / 🟡 该修 / 🟢 优化）
3. **跨文件关联是重点** — 找「A 改了 B 没跟上」
4. **不删 / 不 commit / 不 push**
5. **每条标 Claude 关系**（重复 / 漏 / 独立）

## 沟通规则（itsuki 拍板）

- 用**中文**输出
- 英文 / 缩写 / 简写第一次出现带中文翻译（NFC → 近场通信 / ECDSA → 椭圆曲线签名 / nonce → 一次性随机数 / endpoint → 端点 / alembic → 数据库迁移工具）
- 不用网络黑话（「兜底 / 锁死 / 收窄 / 拿捏」等）
- itsuki 是零基础高中生，每个概念从零解释
- 一句话只表达一个意思（不堆密集术语）

## 完成定义

1. 写完 `session_codex_findings.md`（按格式）
2. 给 itsuki **中文**报告：总数 / 严重程度分布 / 跟 Claude 重复 / 独立发现 / 最关键 3 条

开始。

</prompt>

---

## 给 itsuki 的使用说明

1. **复制 `<prompt>` 和 `</prompt>` 之间的全部内容**
2. **粘贴到 codex（命令行 / chat 入口）**
3. **codex 跑完后**：
   - 检查 `05_logs/audit_2026-05-21_codex/session_codex_findings.md` 是否生成
   - 看 codex 的中文报告（总数 + 严重分布 + 关键发现）
   - 跟 Claude 第一轮 131 条对照（重复 / 独立 / 漏）
   - 真正独立发现的 → 加进 `00_admin/系统bug专栏.md` 总清单

## 如果 codex 跑出问题

- **codex 不读某些文件**（如 sandbox 限制）→ itsuki 手动 `cat 文件 | codex` 喂数据
- **codex 输出英文** → 提醒「用中文 + 第一次出现的英文带翻译」
- **codex 误判**（如 5-16 跨项目审计时 codex sandbox 报告字段误判）→ 跟 Claude 第一轮交叉验证

## 跟 Claude 第一轮的关键差异

| 项 | Claude 3 子代理 | Codex 独立第二轮 |
|---|---|---|
| 输出位置 | `audit_2026-05-19/` | `audit_2026-05-21_codex/` |
| 维度 | 17 维（A/B/C 分工） | 17 维（一个 codex 包揽） |
| 重点 | 第一遍扫 | **重点补漏 + 复核** |
| 跟谁对照 | 自己跑 | 跟 Claude 131 条对照 |
