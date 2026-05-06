# Cloud agent 模式退役归档（2026-05-06）

## 背景

2026-04-23 拍板「iOS Swift 实装独立 repo + Anthropic cloud agent 协作」。配套设计：
- iOS：DMSD（设计真值）+ `Tomoshibi-iOS`（cloud agent 用 mirror）双 repo
- Android（5-02 bootstrap）：直接独立 repo `Tomoshibi-Android`，DMSD 只留设计文档
- 元数据 4 件套（`STATUS.md` / `SHARED_DECISIONS.md` / `SESSION_CHANGELOG.md` / `REMOTE_AGENT_GUIDE.md`）+ 同步脚本（`bin/sync-ios-refs.sh`）

## 退役理由（2026-05-06 itsuki 拍板）

1. **实际使用率低**：Tomoshibi-iOS 自 4-23 后再没 push 过（DMSD 始终 single source）
2. **维护成本不抵收益**：双 repo 同步规则 + 元数据文件 + sync 脚本 = 一整套基础设施，但 itsuki 实际工作流是本地 CC + Xcode + Android Studio，cloud agent 没真用上
3. **GitHub 公开后视觉负担**：DMSD 4-29 起 public，给筑波教授看时多两个 repo 显乱（即使 Tomoshibi-iOS 是 private 教授看不到，Tomoshibi-Android 是 public 教授会看到）
4. **方法论迭代**：4-23 选独立 repo → 5-02 Android 改单 repo → 5-06 全部合回 — 是「试错→反思→再迭代」的工程判断，不是否定原决策

## 这次合并具体做了什么

| # | 动作 | 影响 |
|---|---|---|
| 1 | iOS 合并：检查 `Tomoshibi-iOS` 跟 DMSD 同步状态 → DMSD 16578 行 vs Tomoshibi-iOS 5347 行（4-23 后没动）→ DMSD 已是 single source，无逆同步 | iOS 已就位 |
| 2 | Android 合并：`Tomoshibi-Android` clone 到 `/tmp` → rsync 到 `03_dev/student_android/v1/` | DMSD 内 Android 真代码补齐（85 文件 / 6945 行 Kotlin / 1MB） |
| 3 | 4 个 cloud agent 元数据 git mv 到本目录 | DMSD `03_dev/student_ios/v1/` 干净 |
| 4 | `bin/sync-ios-refs.sh` git mv 到本目录 | 同步脚本退役 |
| 5 | GitHub `otogi2025/Tomoshibi-iOS` + `Tomoshibi-Android` 删除 | 不可逆，但 git log 已存档（见下） |

## 历史证据（archive 内文件）

| 文件 | 内容 |
|---|---|
| `Tomoshibi-iOS-git-log.txt`（121 行）| iOS 独立 repo 全 commit history（2 个 commit：4-22 D1 夜 5347 行 + 4-23 加 refs/） |
| `Tomoshibi-Android-git-log.txt`（566 行）| Android 独立 repo 全 commit history（含 4 feature 分支 + main 的 merge 链） |
| `STATUS.md`（6402 字）| iOS 短期 session 快照 |
| `SHARED_DECISIONS.md`（729 字）| iOS 跨会话决策指针 |
| `SESSION_CHANGELOG.md`（8914 字）| iOS 详细历史变动日志 |
| `REMOTE_AGENT_GUIDE.md`（14350 字）| ⭐ Cloud routine agent 执行手册 — **AC 素材：曾经存在的工程实践证据** |
| `sync-ios-refs.sh`（1838 字）| DMSD → Tomoshibi-iOS/refs/ 单向同步脚本 |

## AC 叙事价值

- **不是失败的方案，是「成本 vs 收益」的工程判断** — 双 repo + 同步三件套是 4-23 真实约束（cloud agent attach 单 repo 限制）下的合理设计
- **5-06 退役是「约束变化后的再迭代」** — itsuki 决定不用 cloud agent 后，原约束消失，方案应跟着变
- **试错周期：13 天**（4-23 → 5-06）— 短周期 = 快速试错快速校准 = 工程素养
- **可关联 AC 核心问题 #3**（怎么解决的）+ **#4**（学到了什么）

## 关联文件（这次合并同步改动）

- `CLAUDE.md` — 删除独立 repo 章节 + 重写文件连锁结构 §iOS sync 一行
- `00_admin/文档同步点清单.md` — 删除跨 repo 同步章节
- `.claude/skills/project-overview/SKILL.md §8.1` — 三种姿态对照表重写
- `05_logs/raw/2026-05-06.md` — 当日决策 dump（AC 候选）

## 找回方法（万一将来想恢复 cloud agent 模式）

1. 本目录 `STATUS.md` / `REMOTE_AGENT_GUIDE.md` 等保留完整内容，可还原
2. iOS / Android git log 完整存档（含每 commit 的 stat）
3. GitHub repo 已删除（不可恢复）— 需重新 push DMSD 内代码到新独立 repo

> 但**不建议恢复** — 试错结论是这套机制对 itsuki 当前工作流性价比低。
