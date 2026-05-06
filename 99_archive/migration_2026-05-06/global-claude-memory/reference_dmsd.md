---
name: DMSD 项目位置 + 専属 memory
description: DMSD 项目相关工作要去 ~/dev/DMSD 开 CC，那个目录有独立的 CLAUDE.md 和 memory
type: reference
originSessionId: 697f58e9-cd2d-44f3-91f2-67764162b91c
---
DMSD 是 itsuki 核心 AC 项目，在 `~/dev/DMSD`。要做 DMSD 相关工作（写代码 / 改设计文档 / 跑 backend / 写 AC log），**应该 `cd ~/dev/DMSD && claude` 开新会话**，而不是在通用目录里搞。

**为什么**：
- DMSD 仓库根有 `CLAUDE.md`（详细的项目指令 / 语言规则 / 文档同步规则 / 版本管理 SOP）
- DMSD 専属 memory 在 `~/.claude/projects/-Users-itsuki-dev-DMSD/memory/`（28+ 个文件，包含项目历史 / itsuki 反馈 / 决策记录）
- 这些都只在 cwd = `~/dev/DMSD` 时被 CC 自动加载

**通用目录**（cwd = `/Users/itsuki`，本 memory 所在）适合做：
- Mac 系统管理 / 装工具 / 配 shell
- 学校事务 / 非 DMSD 学习
- 跨项目的杂事

**关联仓库**：iOS Swift 实装在独立 repo `~/dev/TomoshibiiOSApp/`（GitHub `otogi2025/Tomoshibi-iOS`），不过它是 DMSD 的物理 copy，single source 永远是 DMSD 侧。

**iCloud AC 目录**：`~/Library/Mobile Documents/com~apple~CloudDocs/02_学习与知识/升学/AC/筑波大学 AC入試 準備/`（CC 默认只读，`05_产出/` 永不写）。
