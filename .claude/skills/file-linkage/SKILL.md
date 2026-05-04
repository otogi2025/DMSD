---
name: file-linkage
description: DMSD 文件联动矩阵 — 改 A 必查 B 的完整规则表（13 条联动规则 + 反向索引 + 检查命令）。⭐ 触发：CC 改文件后想确认联动 / itsuki 说「联动检查 / 我改了 X 要查什么 / 改 A 要不要改 B」/ 改了任何 backend models / spec / system_features / Route 等"高联动文件"。短小专一（~150 行）— 比 project-overview skill 短，给频繁触发设计。
when_to_use: ⭐ 触发 — 「联动 / 联动检查 / 我改了 X 要查什么 / 改 A 要改 B 吗 / sync-check」/ CC 自己刚改了 backend models / spec 主体 / system_features / Route.swift / iOS Foundation 组件 / hooks 时主动确认。配套 PostToolUse hook 自动跑 sync-rules.sh — hook 是确定性快查，本 skill 是 LLM 可读详细版。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# File Linkage Skill — DMSD 文件联动矩阵

> **核心理念**：DMSD 是高度联动项目（5 端代码 + 多层文档），改 A 文件**必查 B 文件**否则会漂移。本 skill 是「改 A 必查 B」规则的人类可读总表。
>
> **配套机制**：
> - `00_admin/hooks/lib/sync-rules.sh` — 同样规则的代码化版（hook 自动跑）
> - `bin/sync-check.sh` — 中途手动跑同步检查
> - `.claude/settings.json` PostToolUse hook — CC 调 Write/Edit 后自动跑 sync-rules.sh
> - **本 skill** — itsuki / CC 主动查"我改了 X 要联动什么"时加载

---

## §0 联动规则模型

每条规则两个模式：

| 模式 | 含义 | hook 行为 |
|---|---|---|
| **must** | 改了 trigger → **必须**改 must 列表里至少 1 个文件 | hook 报警告 |
| **action** | 改了 trigger → **必须执行**某个动作（不是改其他文件） | hook 报提醒 |

---

## §1 联动矩阵（13 条规则）

### Rule 1: backend-models（must）

**触发**：`03_dev/backend/v1/app/models.py`（SQLAlchemy ORM 模型）

**必查联动**（至少改 1 个）：
- `03_dev/backend/v1/app/schemas.py` — Pydantic schema 字段对齐
- `03_dev/backend/v1/alembic/versions/*.py` — 数据库 migration
- `03_dev/backend/v1/app/routers/*.py` — API 路由实现
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift` — iOS 字段对齐

**为什么**：ORM model 是数据真值。schema 定义 API 输入输出形状，migration 让数据库跟上 model，routers 用 schema 暴露 API，iOS 客户端要 decode 同样字段 — 任一漂移就崩。

---

### Rule 2: backend-routers（must）

**触发**：`03_dev/backend/v1/app/routers/*.py`

**必查联动**：
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/*.swift`

**为什么**：后端 API 端点变了 → iOS 客户端 Endpoints/*API.swift 必须改对应 URL / 参数 / 返回类型。

---

### Rule 3: system-features（must）

**触发**：`02_design/system_features.md`（共用设计层）

**必查联动**（至少改 1 个）：
- `03_dev/backend/BACKEND_DESIGN_LOG.md`
- `03_dev/student_ios/IOS_DESIGN_LOG.md`
- `03_dev/teacher_web/WEB_DESIGN_LOG.md`

**为什么**：共用层 system_features 改了 → 各端 *_DESIGN_LOG.md 引用通常至少 1 个端会受影响（实装侧要跟着改）。

---

### Rule 4: ios-route（must）

**触发**：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Routing/Route.swift`

**必查联动**：
- `03_dev/student_ios/v1/TomoshibiApp/Root/RootView.swift`

**为什么**：Route 加 case → RootView.swift switch 必须补对应分支，否则 Swift 编译失败（exhaustive switch）。

---

### Rule 5: ios-hook（action）

**触发**：`03_dev/student_ios/v1/TomoshibiApp/**/*.swift`（任何 iOS Swift 文件）

**必做动作**：
```bash
bash bin/sync-ios-refs.sh
```
同步到独立 Tomoshibi-iOS repo。

**为什么**：iOS Swift 在 DMSD 主 repo + Tomoshibi-iOS repo 双存（iOS 独立 repo 是 single source 在 DMSD 侧的镜像），改了主 repo 必须 sync。

---

### Rule 6: spec-body（action）

**触发**：`01_specs/**/*.md`

**必做动作**：触发 version-bump skill §10 4 问，可能要 bump 版本号。

**为什么**：spec 主体改 = 业务规则改 = §2 决策树第 1-2 条 minor bump 候选。

---

### Rule 7: design-doc（action）

**触发**：`02_design/{flow_design,hardware_design,teacher_requirements}.md`

**必做动作**：触发 version-bump skill §2 决策树，**Minor 候选**。

---

### Rule 8: hooks（must）

**触发**：`00_admin/hooks/*`（任何 hook 文件）

**必查联动**：
- `00_admin/hooks/README.md`

**为什么**：hooks 改了 → README 必须同步说明（除非改的就是 README 自己）。

---

### Rule 9: bin-script（must）

**触发**：`bin/*.sh`（任何 bin 脚本）

**必查联动**（至少改 1 个）：
- `CLAUDE.md`（如果脚本被 CLAUDE.md 提及）
- `00_admin/文档同步点清单.md`
- `00_admin/hooks/README.md`

**为什么**：bin/ 脚本改了 → CLAUDE.md / 文档同步点清单 / hooks README 是否要提到（新脚本 / 用法变化）。

---

### Rule 10-13: ios-foundation 组件（action × 4）

**触发**：
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/*Pill*.swift`
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/*Card*.swift`
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/*Avatar*.swift`
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/*GlassSheet*.swift`

**必做动作**：
```bash
grep -rn "ComponentName" 03_dev/student_ios/v1/TomoshibiApp/Features/
```
找全 caller，避免 props 改了导致编译失败。

**为什么**：Foundation 组件被多个 Features 调用，props 改了不查 caller → 编译失败。

---

### 辅助规则: new-declarative

**触发**：新建 `CLAUDE.md` 或 `00_admin/*.md`（除已登记常规文件）

**必做动作**：考虑加入 `00_admin/文档同步点清单.md` 让 hook 保护它。

---

## §2 反向索引（按目标文件查谁改了它要联动）

> CC 想知道「改了 schemas.py 是因为什么 trigger?」时反向查。

| 目标文件 | 谁改了它要联动来 |
|---|---|
| `schemas.py` | Rule 1 (models.py 改) |
| `alembic/versions/*` | Rule 1 (models.py 改) |
| `routers/*` | Rule 1 (models.py 改) |
| `NetworkModels.swift` | Rule 1 (models.py 改) |
| `Endpoints/*API.swift` | Rule 2 (routers 改) |
| `BACKEND_DESIGN_LOG.md` | Rule 3 (system_features 改) |
| `IOS_DESIGN_LOG.md` | Rule 3 (system_features 改) |
| `WEB_DESIGN_LOG.md` | Rule 3 (system_features 改) |
| `RootView.swift` | Rule 4 (Route.swift 改) |
| `hooks/README.md` | Rule 8 (hooks/* 改) |
| `CLAUDE.md` | Rule 9 (bin/*.sh 改) |
| `文档同步点清单.md` | Rule 9 (bin/*.sh 改) |

---

## §3 操作命令

### 中途手动检查（itsuki 主动跑 / CC 调用）

```bash
bash bin/sync-check.sh
```

输出：每条触发规则一段警告（含中文 reason + 缺失文件列表）。

### 改了某个文件想看是否触发联动

```bash
bash bin/sync-check.sh <file_path>
```

### Commit 时自动跑（git pre-commit hook）

无需手动调用，`00_admin/hooks/pre-commit` 会自动跑。

### CC 调 Write/Edit 后自动跑（CC PostToolUse hook，2026-05-04 itsuki 拍板新加）

无需手动调用，`.claude/settings.json` 配置 + `00_admin/hooks/post-edit-sync-check.sh` 自动触发。**比 git pre-commit 早一步**。

---

## §4 维护规则

### 加新规则

1. 编辑 `00_admin/hooks/lib/sync-rules.sh` — 加 `add_rule` 调用
2. 同步本 skill 加新 Rule 段
3. 更新 §2 反向索引
4. （可选）更新 `00_admin/hooks/README.md`

### 加新 trigger 文件类型

需要修改 `add_rule` 第 2 个参数（ERE 正则）— 注意避免嵌套捕获组（详见 sync-rules.sh 顶部注释）。

---

## §5 跟其他机制的协同

| 机制 | 角色 | 何时跑 |
|---|---|---|
| **本 skill** | LLM 可读详细版 | itsuki 显式查 / CC 主动确认 |
| `sync-rules.sh` | 代码化规则源 | 所有 hook / 工具的真值 |
| `bin/sync-check.sh` | 中途手动检查工具 | itsuki 跑 / CC 调用 |
| `00_admin/hooks/pre-commit` | git commit 时自动 | commit 触发 |
| `.claude/settings.json` PostToolUse | CC 调 Write/Edit 时自动 | **每次工具调用后** |

**协同原则**：
- 代码化规则（`sync-rules.sh`）是真值
- 本 skill 内容必须跟 sync-rules.sh 同步（改了一边要改另一边）
- hook 报警告 → CC 看输出 → 必要时调本 skill 详细查

---

## §6 历史

- 2026-05-04 itsuki 拍板：A+B 文件联动工具方案（pre-commit + sync-check.sh + sync-rules.sh）
- 2026-05-04 深夜 itsuki 拍板：本 skill 形态化 + CC PostToolUse hook 实时拦截
