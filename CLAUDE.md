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
- 技术栈：iOS（Swift / SwiftUI）+ 后端（FastAPI / Python / PostgreSQL）
- 分阶段：Phase 1 NFC 卡 + 后端（无手机 App）；Phase 2 iOS + Android
- 规格：`01_specs/` v0.2 已于 2026-04-12 更新
- 版本：SemVer，当前 v0.2.0，见 `CHANGELOG.md`
- **版本号 bump 时必须触发 AC 记录**（对应核心问题 #3 重大决策）

## 目录结构

```
DMSD/
├── 00_admin/
│   ├── WIP.md                         # 书签级，每次会话头尾读写
│   ├── progress_overview.md           # 章节级，CC 起草由 itsuki 确认
│   └── CLAUDE_CODE_记录指南.md         # AC 记录操作手册（仅格式需要时读）
├── 01_specs/                          # 规格文档，v0.2 冻结
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

**iCloud（CC 不访问）**：`筑波大学 AC入試 準備/` 下的 `AC素材_候选/` `AC素材_成品/` 是 AC 记录第 2、3 层，itsuki 在 Mac 上手动搬运。

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

| 路径 | CC 权限 |
|---|---|
| `05_logs/raw/YYYY-MM-DD.md`（第 1 层 CC dump）| 读写 |
| `05_logs/` 其他子项（dev_log / problem_solving / decision_log.md / learning_path.md / project_evolution.md）| itsuki 自己写的日志。CC 可读可引用，改动前先告知 |
| `00_admin/CLAUDE_CODE_记录指南.md` | 只读 |
| `00_admin/WIP.md` | 读写 |
| `00_admin/progress_overview.md` | 起草（不直写）|
| iCloud `AC素材_候选/` `AC素材_成品/`（第 2、3 层）| 不访问 |

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
- CC 只打 `#AC候选` 标签，不替 itsuki 判断升不升级到第 2 层
- 不擅自在 iCloud AC 素材目录写任何东西
- 发现 itsuki 把 AC 私密反思直接写进 `05_logs/` 某个会被推 GitHub 的文件时，提醒她（Private repo 短期无风险，但长期应挪 iCloud）

## 元规则

itsuki 是主角，CC 辅助。CC 越提醒越少、她越来越能自己识别 —— 这本身是成长轨迹。

## 会话结束

1. 刷新当日 `05_logs/raw/YYYY-MM-DD.md` 顶部目录（读操作手册 §8）
2. 列出今天 dump 了哪些碎片给 itsuki 确认
3. 直接更新 `WIP.md`（完成任务 → 最近完成，新认领任务 → 进行中）
4. 起草 `progress_overview.md` 更新草稿，等 itsuki 确认后保存
5. 月末最后一次会话：提醒做月度回顾（挑 `#AC候选` + 写 `monthly_review/YYYY-MM.md` 到 iCloud）

**不做**：长篇会话总结 / 直接写进 iCloud AC 目录。

---

**END** — CC 把本文作为每次会话必读上下文。
