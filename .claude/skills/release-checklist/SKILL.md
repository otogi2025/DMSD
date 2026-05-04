---
name: release-checklist
description: DMSD 发版动作 SOP — 跟 version-bump 配合但不重复。version-bump = 决策树（要不要 bump / bump 哪一位）；release-checklist = 决定 bump 之后的动作清单（CHANGELOG 更新 / tag 打 / push / 跨 repo 同步 / GitHub Release / 公告 / 监控 / 回滚预案）。
when_to_use: ⭐ 触发 — itsuki 说「发版 / 打 tag / release / 推上去 / 发布 v0.X.Y / 跨 repo 同步」/ version-bump skill 走完决策树确定要 bump 后立刻调本 skill / v1.0 demo-clean 跑完后立刻调。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Release Checklist Skill — 发版动作 SOP

> **核心理念**：version-bump skill 解决「**要不要 bump**」的决策；本 skill 解决「**bump 决定后做什么**」的动作。两个 skill 串联：version-bump → release-checklist。
>
> **场景**：itsuki 说「发版 v0.4.0」→ CC 走 version-bump 确认 bump 合理 → 走本 skill 把所有发版动作做完。

---

## §0 主流程（按时序 5 阶段）

```
T-7 天: 发版前长准备（如果是 minor / major bump）
T-1 天: 发版前最后检查
T 当天: 发版动作
T+1 天: 发版后监控
T+N 天: 回滚预案（如出问题）
```

**patch 版本**（如 v0.3.1 → v0.3.2）：跳 T-7，T-1 简化，直接走 T 当天。
**minor 版本**（如 v0.3.x → v0.4.0）：全跑。
**major 版本**（如 v0.x.y → v1.0.0）：全跑 + 多一道 demo-clean skill。

---

## §1 T-7 天: 长准备（minor / major）

- [ ] 跟 itsuki 确认本次发版 scope（哪些 feature / fix 进 / 不进）
- [ ] 确认 demo 环境（如果有外部演示日期）
- [ ] **major 版本必跑**：`demo-clean` skill 全套
- [ ] 写 release notes 草稿（CHANGELOG.md 顶部新建段，标 [Unreleased]）
- [ ] 跑全套测试（iOS Xcode + backend pytest）确认基线 green

---

## §2 T-1 天: 最后检查

- [ ] git status 工作树干净（无未 commit 改动）
- [ ] git log origin/main..HEAD 看本地未 push commit（理想：0，所有该进版本的都已 push）
- [ ] CHANGELOG.md 顶部 [Unreleased] 段 → 改成正式版本号 + 日期
- [ ] **同步点清单全过一遍**：`00_admin/文档同步点清单.md` 列的 11 项全检
- [ ] WIP.md / TODO.md / progress_overview.md 最近更新对齐
- [ ] **跑** `bash bin/sync-check.sh` → 0 警告
- [ ] **跑** `bash 00_admin/hooks/pre-commit` 手动模拟 → 0 阻塞

---

## §3 T 当天: 发版动作（核心 8 步）

### 3.1 最终 CHANGELOG

```bash
# 编辑 CHANGELOG.md 顶部
# - 把 [Unreleased] 改成 [vX.Y.Z] - YYYY-MM-DD
# - 检查 Added / Changed / Fixed / Removed 段完整
```

```bash
git add CHANGELOG.md
git commit -m "chore(release): vX.Y.Z"
```

### 3.2 打 tag

**铁律**（memory `feedback_commit_push_tag_division.md`）：CC 起草命令，**等 itsuki 拍板**才真跑。

```bash
# annotated tag（不要 lightweight tag）
git tag -a vX.Y.Z -m "Release vX.Y.Z

主要变化:
- ...
- ...

详见 CHANGELOG.md"
```

确认：
```bash
git tag --list | tail -3
git show vX.Y.Z --stat | head -20
```

### 3.3 push commit + tag

⚠️ **push 是 itsuki 拍板动作** — CC 起草命令等指令。

```bash
git push origin main
git push origin vX.Y.Z
```

### 3.4 跨 repo 同步（iOS）

DMSD 的 iOS 代码 single source 是 DMSD 仓库，独立 repo `otogi2025/Tomoshibi-iOS` 是镜像。

```bash
bash bin/sync-ios-refs.sh
cd ../Tomoshibi-iOS  # 或对应路径
git status            # 确认同步进来的改动
git tag -a vX.Y.Z -m "..." && git push --follow-tags origin main
cd -
```

### 3.5 GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - <一句话标题>" \
  --notes "$(awk '/^## \[vX.Y.Z\]/,/^## \[v/{print}' CHANGELOG.md | head -n -1)"
```

或手动：访问 https://github.com/otogi2025/DMSD/releases/new 填表。

### 3.6 文档同步点 final check

跑一遍 `00_admin/文档同步点清单.md` Release Checklist 段（如果那里有 release 专用清单）。

### 3.7 WIP / TODO 收尾

- [ ] WIP.md 最近会话条目加一条「vX.Y.Z 发版完成」
- [ ] TODO.md 把已发版功能从 backlog 划掉
- [ ] `00_admin/hooks/pre-commit` 重跑确认 hook 不抓硬编码版本号

### 3.8 通知 / 公告（如需要）

major / minor 版本如果有外部用户：
- iOS 用户：TestFlight 推送 build
- Android 用户：（v1.0 时）
- 演示：通知宿舍管理员
- AC 素材：dump 到 `05_logs/raw/<date>.md` 标 5 级里程碑

---

## §4 T+1 天: 发版后监控

- [ ] crash log（iOS Sentry / 手动收集）
- [ ] backend 日志报错率
- [ ] 用户反馈（如有渠道）
- [ ] performance metrics（如有）

如果有问题 → 决定 hotfix（patch bump）/ 回滚。

---

## §5 T+N 天: 回滚预案

如果发版后炸：

### 5.1 客户端炸（iOS）
- 快速 hotfix → 走 patch bump 流程（vX.Y.Z+1）
- 严重时：从 TestFlight 撤掉 build，让用户用上一版

### 5.2 backend 炸
- `git revert vX.Y.Z` 上一个 commit / 回退部署
- alembic downgrade（如果有数据库 schema 变化）
- 通知客户端用户

### 5.3 完全撤回 release
```bash
# 删 GitHub Release（不删 tag）
gh release delete vX.Y.Z

# 删 tag（local + remote）— 慎用
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
```

⚠️ **删 tag 是不可逆操作** — itsuki 必须明确拍板。

---

## §6 反模式

### ❌ 反模式 1: CC 主动跑 git push
违反 commit/push/tag 协作分工 — push / tag / 删 tag 全部 itsuki 拍板。
**正确**：CC 起草命令等指令。

### ❌ 反模式 2: tag 用 lightweight（git tag X 没 -a）
**后果**：没 metadata，看不出谁打的 / 什么时候 / 为什么。
**正确**：`git tag -a vX.Y.Z -m "..."` annotated tag。

### ❌ 反模式 3: 跳 CHANGELOG 直接打 tag
**后果**：发版后回头补 CHANGELOG，可能漏 commit。
**正确**：先 CHANGELOG 段成型 → 一个 chore(release) commit → 再 tag。

### ❌ 反模式 4: 漏跨 repo 同步
**后果**：DMSD 仓库 vX.Y.Z 出了，但 Tomoshibi-iOS 还停在 vX.Y.Z-1，公开 iOS repo 误导。
**正确**：bin/sync-ios-refs.sh + Tomoshibi-iOS 也打同步 tag。

### ❌ 反模式 5: 漏 hooks 验证
**后果**：发版后下次 commit hook 才发现版本号不一致。
**正确**：发版当天 §2 §3.7 都跑 hook 验证。

### ❌ 反模式 6: minor / major 跳 demo-clean
**后果**：v1.0 上线带着 demo bypass = 安全漏洞。
**正确**：major 版本（任何上 v1.0.0 或 v2.0.0 等）必先跑 demo-clean skill。

---

## §7 配套 skill / 文件

- `.claude/skills/version-bump/SKILL.md` — bump 决策（前置）
- `.claude/skills/demo-clean/SKILL.md` — major 版本前置必跑
- `.claude/skills/file-linkage/SKILL.md` — 联动检查
- `00_admin/文档同步点清单.md` — 同步点完整列表
- `00_admin/hooks/pre-commit` + `bin/sync-check.sh` — 发版前必跑
- `CHANGELOG.md` — 版本号 single source
- `bin/sync-ios-refs.sh` — 跨 repo 同步
- memory `feedback_commit_push_tag_division.md` — push/tag 协作分工铁律

---

**最后更新**：2026-05-04 itsuki 拍板新建（version-bump 决策完后的动作 SOP）
