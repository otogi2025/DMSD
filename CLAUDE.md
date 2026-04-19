# DMSD 项目指令（CC 必读）

## 关于 itsuki

- 中国人，日本高中三年级，2026 年 4 月起进入高三
- 完全零基础，没有系统学过编程，所有概念要从零解释
- 目标：筑波大学 情報学群 情報科学類 AC入試（2027 年 4 月入学）
- DMSD 是她的核心 AC 叙事项目

## 语言规则

| 场景 | 语言 |
|---|---|
| 日常对话、解释概念 | 中文 |
| 英文术语、命令参数 | 中文解释含义（如 `git commit` = 提交记录）|
| 日语专业词 | 标注中文意思 |
| AC 自我推荐书 / 志望理由书内容 | 日语 |
| 面试模拟 | 日语 |
| 代码注释 | 中文 |
| Git commit message | 英文（简短）+ 中文正文可选 |

## 项目信息

- DMSD（Dormitory Management System Digitalization）宿舍管理系统电子化
- 核心：宿舍点呼数字化（NFC 签到 / 自动判定 / 纪律扣分）
- 技术栈：iOS（Swift / SwiftUI）+ Android（Kotlin，走 NFC 贴纸方案 + 自建 APK 分发）+ 后端（FastAPI / Python / PostgreSQL）+ RPi 点呼机（Python）+ NFC 卡（NTAG215）
- **上线姿态**（2026-04-19 G2 决策）：**v1.0 直接 iOS + Android + 卡 完整版一次上线**；取消原 Phase 1 / Phase 2 分阶段
- **开发节奏**：内部按 M1→M5 里程碑推进（兜底：做不完至少 M1+M2 可 demo）
- 规格：`01_specs/` 初版冻结于 2026-02-12；后续修订进度见 `CHANGELOG.md`
- 版本：SemVer。**当前版本见 `CHANGELOG.md` 顶部**（单源真值，见下方"文档一致性规则"节）
- **版本号 bump 时必须触发 AC 记录**（对应核心问题 #3 重大决策）

## 目录结构

```
DMSD/
├── 00_admin/
│   ├── WIP.md                         # 书签级，每次会话头尾读写
│   ├── progress_overview.md           # 章节级，CC 起草由 itsuki 确认
│   └── CLAUDE_CODE_记录指南.md         # AC 记录操作手册（仅格式需要时读）
├── 01_specs/                          # 规格文档，v0.1 冻结，v0.2 修订中
├── 02_design/
├── 03_dev/                            # 代码（backend / Student-iOS / …）
├── 04_ops/
├── 05_logs/                           # DMSD 开发 log
│   ├── raw/                           # CC 每日 dump YYYY-MM-DD.md（+ 历史主题文件）
│   ├── dev_log/                       # 开发日志（itsuki 自己写）
│   ├── problem_solving/
│   ├── decision_log.md                # itsuki 手写索引（CC 不写）
│   ├── learning_path.md
│   └── project_evolution.md
│   # AC 纯素材（reflection/ weekly_review/ monthly_review/ interview_log/
│   # ai_协作记录.md dmsd_app_ideas.md 证据/ ac_入試准备/）已移 iCloud，不在 git
├── 06_assets/
├── 07_release/
├── 99_archive/                        # 2025-12 早期 GPT 对话等
├── CHANGELOG.md
└── CLAUDE.md                          # 本文件
```

**iCloud 路径**：`iCloud/02_学习与知识/升学/AC/筑波大学 AC入試 準備/`（结构见本文件"AC 记录协作"节）。

## 文档一致性规则（2026-04-19 加）

> **背景**：2026-04-19 itsuki 发现"迭代了几个版本但多个文件还写过期版本号"。根本原因 = "同一信息多处存储 → 必然漂移"。解法 = 单源真值 + 同步清单 + pre-commit hook 三件套。

### 单源真值（Single Source of Truth）

| 共享概念 | 权威源 | 其他文件怎么引用 |
|---|---|---|
| 版本号 | `CHANGELOG.md` 顶部 | "当前版本见 `CHANGELOG.md`" |
| 目录结构 | 本文件 §目录结构 | "见 CLAUDE.md §目录结构" |
| 5 AC 核心问题 | 本文件 §5 个 AC 核心问题 | "见 CLAUDE.md §5 个 AC 核心问题" |
| 分阶段策略 | `CHANGELOG.md` + `RollCall_Spec_*.md §1` | 用指针 |

完整同步点清单 + Release Checklist + Onboarding Checklist → `00_admin/文档同步点清单.md`。

### 声明性文件（不允许硬编码版本号 — pre-commit hook 会拦）

- `CLAUDE.md`（本文件）
- `00_admin/WIP.md`
- `00_admin/TODO.md`
- `00_admin/progress_overview.md`

豁免：行末加 `<!-- VERSION_OK -->` 注释。详见 `00_admin/hooks/README.md`。

### 会话结束前一致性检查（CC 必做）

每次会话结束前：

1. **pre-commit 检查预演**：跑 `bash 00_admin/hooks/pre-commit`（不需要真 commit 就能看结果），有 ❌ 就提示 itsuki
2. **时间戳新鲜度扫描**：过去 7 天 commit 改过但文件头"最后更新"没动的文件 → 提醒 itsuki
3. **同步点发现**：本次会话新建了声明性文件 → 提醒 itsuki 加入 `00_admin/文档同步点清单.md`

### pre-commit hook 安装

每个 clone 本 repo 的机器首次跑一次（Mac / VPS 各跑）：

    bash 00_admin/hooks/install.sh

详见 `00_admin/hooks/README.md`。

## 开发环境

- 学校 iPad → SSH 到 VPS（`~/DMSD`）→ CC（后端、文档、学习）
- 家 Mac → 本地（`~/dev/DMSD`）→ CC + Xcode + VS Code（iOS 开发）
- 通过 GitHub 同步（Private repo）

## 对话规则

1. 每一步都要解释"为什么做"和"在干什么"
2. 主动告诉 itsuki 不知道但应该知道的概念（她不知道自己不知道什么）
3. 不假设 itsuki 有任何先验知识（变量 / API / HTTP / 数据库都要解释）
4. 出练习题尽量结合 DMSD 场景（点呼、扣分、签到）

## 代码编写原则

- itsuki 决定"做什么"，CC 实现"怎么做"
- 每段代码都要向她解释含义，确保她能理解
- 她需要能在 AC 面试时解释每个模块的功能和设计原因
- CC 写出 itsuki 当时不完全理解的代码时，停下来讲清楚，记 `[分歧]` B 类（见下 AC 记录）

## 会话开始：WIP.md 必读

每次会话第一件事：读 `00_admin/WIP.md`。

- 了解当前做到哪、有哪些进行中任务、哪些文件被其他会话认领
- 遵守 WIP 里的"文件边界"规则，避免多会话冲突

`WIP.md` CC 可直接写（书签级，开销低）。
`progress_overview.md` CC 只起草，由 itsuki 确认后保存。

---

# AC 记录协作（v3 三层体系）

## 权威文档

- 本节 = CC 日常操作的全部需求，大部分会话不需要读操作手册
- 操作手册 `00_admin/CLAUDE_CODE_记录指南.md` 只在需要 dump 格式（§3.3 模板）时才读
- itsuki 侧完整章程 `AC入试记录指南_v3.md` 在 iCloud，CC 不读

## 目录边界

### DMSD 仓库内

| 路径 | CC 权限 |
|---|---|
| `05_logs/raw/YYYY-MM-DD.md`（第 1 层 CC dump）| 读写 |
| `05_logs/` 其他子项（dev_log / problem_solving / decision_log.md / learning_path.md / project_evolution.md）| itsuki 自己写的日志。CC 可读可引用，**改动前必须先告知** |
| `00_admin/CLAUDE_CODE_记录指南.md` | 只读 |
| `00_admin/WIP.md` | 读写 |
| `00_admin/progress_overview.md` | 起草（不直写）|

### iCloud AC 目录（2026-04-17 起 CC 可访问，有边界）

iCloud 根路径：`iCloud/02_学习与知识/升学/AC/筑波大学 AC入試 準備/`

| 路径 | CC 权限 |
|---|---|
| `00_指南/` | 读（`AC入试记录指南_v3.md` / 文件结构图）|
| `01_官网资料/` | 读 |
| `02_分析与调研/` | 读 |
| `03_素材_候选/`（第 2 层）| 默认不写；itsuki **当场明确授权**后可写。升级第 2 层的筛选判断权在 itsuki |
| `04_素材_成品/`（第 3 层）| 默认不写；itsuki **当场明确授权**后可写 |
| `05_产出/`（志望理由书 / 自我推荐书 / 面试准备）| **永不写**——这是 itsuki 的原创作品，AI 不参与起草 |
| `99_archive/` | 读；可写到 `99_archive/` 的新子目录（归档用途）|
| `状态快照.md` | 读；改动前先告知 itsuki |

## 触发清单（CC 每次回复前心里过一遍）

刚才这轮对话里 itsuki 是否出现下列任一条？出现就**当场问她要不要记**，不要等她主动说：

- [ ] 做了决策（选 A 不选 B，哪怕很小）
- [ ] 新想法 / 反思 / 怀疑（包括对方向的动摇）
- [ ] 遇到问题、bug、不理解的概念
- [ ] 学到新东西（语法 / API / 工具 / 概念）
- [ ] 代码、架构、文件结构发生改变
- [ ] 和真人做了访谈或讨论
- [ ] 和 CC 意见不一致 / itsuki 纠正了 CC
- [ ] CC 写出 itsuki 当时不完全理解的代码
- [ ] 版本号 bump（SemVer 任何位变化）

**固定话术**：

```
刚才〇〇值得记。我现在追加到 05_logs/raw/YYYY-MM-DD.md 好吗？
归类：[标签] / 对应 AC 核心问题 #X
```

同意 → 读操作手册 §3.3 获取格式 → append。
不同意 → 继续对话，不纠缠。

## 口头触发词兜底

itsuki 说下列任一词时**必做**（不用问）：

- "记一下" / "总结一下" / "留个痕" / "dump 一下"

## 5 个 AC 核心问题（打标签用）

1. 为什么做 DMSD？（問題発見）
2. 遇到了什么困难？（問題意識）
3. 怎么解决的？（問題解決）
4. 学到了什么？（自己認識）
5. 为什么筑波？以后学什么？（志望動機）

## 关键原则

- 主动识别 + 口头触发词兜底
- **先问再写**，绝不擅自写入
- CC 默认只打 `#AC候选` 标签；升级第 2 层的判断权在 itsuki
- **写 iCloud 第 2/3 层需 itsuki 当场授权**（不是默认行为）——没有明确指令时不动
- **永不写 `05_产出/`**——志望理由书 / 自我推荐书 / 面试准备是 itsuki 的原创作品
- 发现 itsuki 把 AC 私密反思直接写进 `05_logs/` 某个会被推 GitHub 的文件时，提醒她（Private repo 短期无风险，但长期应挪 iCloud）

## 元规则

itsuki 是主角，CC 辅助。CC 越提醒越少、她越来越能自己识别 —— 这本身是成长轨迹。

## 会话结束

1. 刷新当日 `05_logs/raw/YYYY-MM-DD.md` 顶部目录（读操作手册 §8）
2. 列出今天 dump 了哪些碎片给 itsuki 确认
3. 直接更新 `WIP.md`（完成任务 → 最近完成，新认领任务 → 进行中）
4. 起草 `progress_overview.md` 更新草稿，等 itsuki 确认后保存
5. 跑 `§文档一致性规则 → 会话结束前一致性检查` 的 3 项（pre-commit 预演 + 时间戳新鲜度 + 同步点发现）
6. **git commit 本次会话所有变动**（2026-04-19 规则更新，itsuki 明确要求）：
   - commit message **必须详细**：首行简短总结（`feat/fix/chore: 简述` + 版本号 / scope 前缀），空行后主体分点列 **why + what**（不只是 what）
   - 参考之前 commit log 风格：`v0.3.0: spec main body rewrite — 双路径并存 + thin client + ...` <!-- VERSION_OK -->
   - **不写 `Co-Authored-By` trailer**（见 memory `feedback_commit_style.md`）
   - pre-commit hook 会自动跑（含硬编码版本号会被拦）
   - 用 HEREDOC 传 message 保证换行和中文正确
   - **不 push**（除非 itsuki 明说"push"）
7. 月末最后一次会话：提醒做月度回顾（挑 `#AC候选` + 写 `monthly_review/YYYY-MM.md` 到 iCloud）

**不做**：长篇会话总结 / 直接写进 iCloud AC 目录 / 未授权 `git push` 或 `git tag`。

---

**END** — CC 把本文作为每次会话必读上下文。
