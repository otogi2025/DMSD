---
name: 改动/决定确认后立刻同步文档（不等会话结束）
description: itsuki 多次强调，每次改动或决定一旦同意，必须当场更新对应规范文档；CC 必须记得文档单源真值在哪
type: feedback
originSessionId: 1dcd6fcb-c890-4ceb-9ffe-5f0b117c9d58
---
每次 itsuki 提出的任何改动 / 决定，**一旦双方同意**，CC **当场立即**更新对应规范文档；不积攒到会话结束。

**Why:**
- 2026-04-20 已有 `feedback_discuss_means_produce.md`（讨论 = 产出，重大决策当场写 CLAUDE.md / 02_design）
- 2026-05-04 itsuki 又一次主动强调（启动会话开口第二件事）= 信号强：仍然踩坑 / 仍然有"等会话结束统一更新"的倾向
- 不立即更新 → 下次会话 CC 读 spec 看不到这条决定 → 又问一遍 / 又走回头路 / AC 叙事丢证据

**How to apply:**
1. 拍板瞬间：CC 立即开 Edit 改 `02_design/system_features.md`（共用层）/ 各端 `*_DESIGN_LOG.md`（专属层）/ `CLAUDE.md`（规则）
2. 改完之后才继续下一个话题 — **不**说"我等下统一更新" / **不**留 TODO 项"待会改文档"
3. CC **必须记住**单源真值速查表在 `00_admin/文档同步点清单.md`，文件级清单在 `00_admin/文件结构指南.md`
4. 改了某文件 → 对照 CLAUDE.md §会话结束 §3 文件关联追踪表 → 当场补连带必改文件，不留到收尾
5. 适用范围：技术决策 / UI 规则 / 流程 / 角色权限 / 命名 / 阈值 / 任何"以后会被引用"的事实
