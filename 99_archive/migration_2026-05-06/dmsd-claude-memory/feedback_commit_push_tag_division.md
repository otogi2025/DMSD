---
name: commit/push/tag 协作分工（2026-05-04 itsuki 拍板）
description: CC 自动 commit 本地不 push；push 等 itsuki 明示「推到 X commit」；bump itsuki 拍板版本号 → CC 执行 tag + push；CHANGELOG CC 起草事实清单，AC 叙事 itsuki 自己写
type: feedback
originSessionId: 0d45fc2f-1340-456c-aee4-c005e59a14dc
---
DMSD 项目的 git 治理协作分工（2026-05-04 拍板）：

## 谁做什么

| 谁做 | 做什么 |
|---|---|
| **CC 自动** | commit 本地（不 push）/ raw/ 详细 dump / 起草 CHANGELOG 段（事实清单技术性）/ 主动提 bump 时机（SOP §10 4 问 hit 就提议）|
| **itsuki 主导** | push 时机（「推到 X commit 为止」）/ bump 决定（patch / minor / major）/ **AC 叙事整个文档**（自己写，CC 等他来问才辅助，不主动起草）|
| **CC 执行** | itsuki 点头后 → 打 tag + commit CHANGELOG 文件 + push 一气呵成 |

## CHANGELOG vs AC 叙事 关键差别

| 类型 | 内容 | 谁写 |
|---|---|---|
| **CHANGELOG** | 事实清单（"v0.9.0 加了 X / 改了 Y / 修了 Z"，时间 + 文件 + commit hash）| **CC 起草** |
| **AC 叙事**（`v0.X.Y_AC叙事.md`）| itsuki 的故事（"为什么做、学到了什么、推翻过什么、面试时怎么讲"）| **itsuki 自己写**，CC 辅助不起草 |

## CC 自动 commit 时的规范

- commit message 详细：首行 `feat/fix/chore: 简述`，空行后主体分点列 **why + what**
- 不写 `Co-Authored-By` trailer（memory `feedback_commit_style.md`）
- 用 HEREDOC 传 message 保中文换行；pre-commit hook 自动跑
- **本地 commit 后不 push**（push 等 itsuki 明示）
- **别会话的未提交改动**（`git status` 里别人的 WIP）→ **不打包**，留给那个会话或 itsuki 自己处理
- 涉及凭证 / 密码 / 私密内容 → 先问 itsuki
- 改了 `CLAUDE.md` / 系统设计 / 规则类文件 → commit 完主动告知"我推了 X 规则上去"

## Why

itsuki 2026-05-04 经历了一次完整的拍板反复：
1. 第一次想要"全自动 commit + push + tag"（"免得每次都要开口"）
2. CC 提醒 unknown unknowns —— GitHub repo 是 public，自动 push 后 git log 永久保留所有改动；commit 和 tag 是两件不同的事
3. itsuki 撤回授权（"我还是不接受了"）
4. CC 重新提议「commit 自动 / push 等明示 / tag 跑 SOP」
5. itsuki 接受 + 进一步说"AC 叙事 / CHANGELOG / bump 决定 / 时机 你都可以帮我做"
6. CC 提醒"AC 叙事里「面试原话」节我代不了你"
7. itsuki 重申最终立场："我最主要的还是需要你的辅助。我自己整理我自己阅读，AI 辅助我把稿子写好，把故事写好" —— **CC 是档案员 + 写手助理，不是代笔**
8. 最终分工：CC 主导技术执行（commit / CHANGELOG / tag 执行），itsuki 主导叙事（push 决定 / bump 决定 / AC 叙事写作）

## How to apply

- 会话结束时有 CC 自己的改动 → 直接 commit（按规范）+ 三段式总结，**不 push**
- itsuki 说"看本地有哪些 commit" → 跑 `git log --oneline origin/main..HEAD`
- itsuki 说"推到 X commit" → `git push origin <hash>:main`
- itsuki 说"撤销最近 N 个 commit" → `git reset --soft HEAD~N`（默认 soft 保留改动）
- 看到 spec / 02_design / 03_dev 主体改动 → 跑 SOP §10 4 问，命中任一 → 主动提议 bump
- itsuki 拍板 bump 后 → CC 写 CHANGELOG 段 + 不写 AC 叙事 + 打 tag + push（一气呵成）
- 看到自己快要起草 `v0.X.Y_AC叙事.md` → 停下，提醒 itsuki "AC 叙事是你自己写"

## 历史文件处理

`v0.3.0` ~ `v0.8.0` 的 6 个 `v0.X.Y_AC叙事.md` 都是 CC 起草的（旧分工），**保持不动**（历史快照）。新规则**从下一次 bump 起生效**。
