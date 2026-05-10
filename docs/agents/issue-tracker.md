# Issue tracker: DMSD Custom Layout

DMSD 不用 GitHub Issues。issue / backlog 全部走 `00_admin/TODO.md` 单文件。

## Conventions

- **单文件**：所有未完成事项在 `00_admin/TODO.md`（66KB+），按 section 分类
- **section 命名**：emoji + 主题（例 `§🛰️ 点呼机` / `§🐛 v1 backend bug fix` / `§🛠️ Meta` / `§C reviewer demo 跟踪`）
- **状态符号**：`⏳` 进行中 / `✅` 已完成 / `🔴` 阻塞 / `❌` 否决
- **新 issue**：append 到对应 section 末尾，不新建文件、不开 GitHub Issue

## When a skill says "publish to the issue tracker"

Append 到 `00_admin/TODO.md` 对应 section。section 不存在则新建（emoji + 主题）插到合适位置。提交前给 itsuki 看一眼。

## When a skill says "fetch the relevant ticket"

读 `00_admin/TODO.md`。itsuki 通常会指明 section（如 "§🐛 v1 backend bug fix 那条"）或直接 paste 内容。

## PRD 例外

`to-prd` skill 写 PRD 时，PRD 详细文档放 `.scratch/<feature>/PRD.md`（中间产物，已 .gitignore）。PRD 拆出的实装 issue 仍 append 到 `00_admin/TODO.md`。

分工：
- `to-prd` → `.scratch/<feature>/PRD.md`（详细设计文档，本地中间产物）
- `to-issues` → `00_admin/TODO.md` 对应 section（实装单，进 git）
