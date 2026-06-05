---
name: file-linkage
description: DMSD 文件联动矩阵 — 改 A 必查 B 的完整规则表（23 条联动规则 + 反向索引 + 检查命令）。⭐ 触发：CC 改文件后想确认联动 / itsuki 说「联动检查 / 我改了 X 要查什么 / 改 A 要不要改 B」/ 改了任何 backend models / spec / system_features / Route 等"高联动文件"。短小专一（~200 行）— 比 project-overview skill 短，给频繁触发设计。
when_to_use: ⭐ 触发 — 「联动 / 联动检查 / 我改了 X 要查什么 / 改 A 要改 B 吗 / sync-check」/ CC 自己刚改了 backend models / spec 主体 / system_features / Route.swift / iOS Foundation 组件 / hooks 时主动确认。配套 PostToolUse hook 自动跑 sync-rules.sh — hook 是确定性快查，本 skill 是 LLM 可读详细版。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# File Linkage Skill — DMSD 文件联动矩阵

> **核心理念**：DMSD 是高度联动项目（5 端代码 + 多层文档：iOS / Android / 后端 / teacher_web / 点呼机），改 A 文件**必查 B 文件**否则会漂移。本 skill 是「改 A 必查 B」规则的人类可读总表。
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

## §1 联动矩阵（23 条规则）

> **编号说明**（消除困惑）：规则按历史顺序编号、有跳号 —— 没有 Rule 6（早期删过留的空号）,Rule 10-13 是一个条目涵盖 4 条 ios-foundation 组件规则。所以下面编号最高到 **Rule 24**,但实际 `add_rule` 共 **23 条**（以 `sync-rules.sh` 实际条数为准,别被最大编号误导）。

### Rule 1: backend-models（must）

**触发**：`03_dev/backend/v1/app/models.py`（SQLAlchemy ORM 模型）

**必查联动**（至少改 1 个）：
- `03_dev/backend/v1/app/schemas.py` — Pydantic schema 字段对齐
- `03_dev/backend/v1/alembic/versions/*.py` — 数据库 migration
- `03_dev/backend/v1/app/routers/*.py` — API 路由实现
- `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift` — iOS 字段对齐
- `03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/model/Models.kt` — Android 字段对齐（2026-06-03 补 — 原来只提醒 iOS，漏了 Android 同性质文件）

**为什么**：ORM model 是数据真值。schema 定义 API 输入输出形状，migration 让数据库跟上 model，routers 用 schema 暴露 API，iOS / Android 两个客户端都要 decode 同样字段 — 任一漂移就崩。Android 现在还是假数据没接后端，但趁早挂联动，免得接后端时才发现字段早已各漂各的。

> ⚠️ **must 是「或」语义**（§0：必查清单里至少改 1 个就放行）。所以改了 `models.py` 只改 Android、不改 iOS / schema / migration 也会通过 — 规则只是「提醒核对下游」,不保证每个都改到。iOS + Android 字段要各自核对,别只动一端就当过关（codex 2026-06-03 审查提醒）。

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
- `03_dev/student_android/ANDROID_DESIGN_LOG.md`
- `03_dev/teacher_web/WEB_DESIGN_LOG.md`
- `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md`

**为什么**：共用层 system_features 改了 → 5 端 *_DESIGN_LOG.md 引用通常至少 1 个端会受影响（实装侧要跟着改）。

---

### Rule 4: ios-route（must）

**触发**：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Routing/Route.swift`

**必查联动**：
- `03_dev/student_ios/v1/TomoshibiApp/Root/RootView.swift`

**为什么**：Route 加 case → RootView.swift switch 必须补对应分支，否则 Swift 编译失败（exhaustive switch）。

---

### Rule 5: spec-body（action）

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

### Rule 14: ios-business-design（action — 反向规则,2026-05-08 加）

**触发**：`03_dev/student_ios/v1/TomoshibiApp/Features/**/*.swift`（业务代码）

**必做动作**：判断是否同步 `IOS_DESIGN_LOG.md`,多端涉及时 `system_features.md` 也要更新。

**为什么**：业务代码改 = 实装行为变了,设计文档可能漂移。typo / 重命名 / 重构内部不需要同步,改 UI / 流程 / 字段才需要 — `action` 模式温和提醒不强制。

---

### Rule 15: android-business-design（action — 反向规则,2026-05-08 加）

**触发**：`03_dev/student_android/**/(ui|features)/**/*.kt`

**必做动作**：判断是否同步 `ANDROID_DESIGN_LOG.md` + `system_features.md`。

---

### Rule 16: backend-business-design（action — 反向规则,2026-05-08 加）

**触发**：`03_dev/backend/v1/app/(routers|services)/**/*.py`

**必做动作**：判断是否同步 `BACKEND_DESIGN_LOG.md` + `system_features.md`。

**注**：与 Rule 1 / Rule 2 互补 — Rule 1/2 是「字段对齐」（must）,本规则是「设计文档同步」（action）。

---

### Rule 17: web-business-design（action — 反向规则,2026-05-08 加 / 2026-06-03 两次修 trigger）

**触发**（精确平铺这三类活代码）：
- `03_dev/teacher_web/v1/src/index.html`
- `03_dev/teacher_web/v1/src/index.css`
- `03_dev/teacher_web/v1/src/api/*.js`

**必做动作**：判断是否同步 `WEB_DESIGN_LOG.md` + `system_features.md`。

**为什么这样写 trigger**：老师网页早从 Vite + TypeScript 方案废弃,回到单文件 `index.html` + `index.css` + `api/client.js`（不编译 TS）。① 第一次修（解决旧 trigger 只认 `.ts` 认不出活代码 `.js`/`.html`、反而盯着废弃的 `client.ts`）。② 第二次修（codex 审查发现：第一次改宽成 `src/**/*.{js,html,...}` 会误报 `vendor/`(react/babel 第三方库) 的 `.js`、又漏了 `index.css`）→ 收窄成精确平铺这三类,刻意排除 `vendor/` / `_assets/`(字体) / `assets/`(图标) / 废弃的 `client.ts`。

---

### Rule 18: rollcall-device-business-design（action — 第 5 端,2026-05-08 加）

**触发**：`03_dev/rollcall_device/src/**/*.py`

**必做动作**：判断是否同步 `ROLLCALL_DEVICE_DESIGN_LOG.md` + `system_features.md`。

---

### Rule 19: design-log-to-system-features（action — 反向规则,2026-05-08 加）

**触发**：任一端 `*_DESIGN_LOG.md`(BACKEND / IOS / ANDROID / WEB / ROLLCALL_DEVICE)

**必做动作**：多端涉及时,`02_design/system_features.md`（共用层真值）也要更新。

**为什么**：与 Rule 3 反向 — Rule 3 是「共用→各端」,Rule 19 是「各端→共用」。某端 DESIGN_LOG 加新功能描述,如果其他端也涉及,共用层应吸收上去。

---

### Rule 20: rollcall-arch-chain（action — 点呼机架构链,2026-06-03 加）

**触发**（下面 4 个文件任一改）：
- `02_design/hardware_design.md` — 点呼机硬件选型
- `02_design/flow_design.md` — 签到流程图 + 攻防分析
- `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` — 点呼机软件设计
- `00_admin/项目心智模型.md` — AI 开局必读骨架

**必做动作**：核对其余三个是否漂移 — 这 4 个文件是同一条「点呼机怎么读写 NFC」的链,改一个其余常跟着改。

**为什么**：2026-06-02 改 `hardware_design.md` 把手机从「读 NFC 贴纸」反转成「写 NFC 贴纸」,但旧联动系统没提醒去改另外三个 → `flow_design.md` 还画着旧的 nonce 每 10 秒刷新流程、`ROLLCALL_DEVICE_DESIGN_LOG.md` 和 `项目心智模型.md` 留了旧架构,互相矛盾。补这条 action 规则把整条链锁在一起。用 action（每次触发都无条件提醒）而非 must,因为 must 是「这 4 个至少改 1 个就放行」,正好会漏掉「只改 1 个、其余该跟没跟」的情形。

---

### Rule 21: backend-routers-web（action — 2026-06-03 加）

**触发**：`03_dev/backend/v1/app/routers/*.py`（后端 API 路由）

**必做动作**：核对老师网页 `03_dev/teacher_web/v1/src/api/client.js`（约 65 处直连后端接口路径）是否要跟改。

**为什么**：Rule 2 backend-routers（must）已提醒查 iOS Endpoints,但老师网页 `client.js` 同样直连后端路由,过去无任何规则覆盖（后端接口一改网页可能整片崩没人知道）。单独用 action 而不并进 Rule 2 的 must —— iOS 和 web 是两个独立客户端,后端路由改了两个都可能要改,而 must 是「列表里至少改 1 个就放行」,会被 iOS 的改动满足、漏掉 web。

---

### Rule 22: spec-dict-chain（action — spec 字典链,2026-06-03 加）

**触发**（下面 5 个文件任一改）：
- `01_specs/rollcall/FIELD_REGISTRY.md` — 字段字典（唯一命名）
- `01_specs/rollcall/ENUM_REGISTRY.md` — 枚举字典（唯一取值）
- `01_specs/rollcall/ERROR_CODES.md` — 错误码字典
- `01_specs/rollcall/DEVICE_REGISTRY.md` — 设备字典
- `01_specs/rollcall/RollCall_Spec.md` — 点呼规格主体

**必做动作**：核对其余几个是否漂移 + 后端 `schemas.py`/`models.py` 实装的字段枚举是否要跟改。

**为什么**：跟点呼机架构链同性质的真实链。主体 `RollCall_Spec.md` §8 自声明「与字典四件套相互引用」,正文多处显式引用字典为权威（如 `base_status` 取值必须来自 ENUM_REGISTRY）。改字典一个字段名 / 枚举值,主体引用和后端实装都可能对不上。action 模式（同点呼机链理由：must 会漏「只改字典、主体和后端没跟」）。

---

### Rule 23: version-number-chain（action — 版本号链,2026-06-03 加 / 2026-06-05 加版本演变一览）

**触发**：`CHANGELOG.md`（仓库根）/ `00_admin/WIP.md` / `05_logs/版本演变一览.md`

**必做动作**：核对三处是否同步 ——
- **`CHANGELOG.md` = 版本号唯一真值**（改文件版本时以它为准）
- `00_admin/WIP.md` 头部「当前版本」= 二级源（版本号要跟 CHANGELOG 一致）
- `05_logs/版本演变一览.md` = 面向 AC 教授的详细叙事版（**改 CHANGELOG 必连带改这里**：加新版本的总表行 + 详细段，因为这是 AC 素材）

**为什么**：`文档同步点清单.md §1` 定义版本号单一真值 = `CHANGELOG.md`。改 CHANGELOG = 迭代版本，必须同步：① WIP 头部版本号 ② 版本演变一览。后者是 itsuki 2026-06-05 拍板补的绑定 —— 原话「迭代版本要改 changelog，改了 changelog 就该改版本演变一览，这两个文件要绑在一起，版本演变一览要包含详细的内容，因为是素材」。过去 Rule 23 只绑 CHANGELOG↔WIP、漏了版本演变一览，6-05 补齐。完整 bump 流程见 version-bump skill。

---

### Rule 24: sync-rules-self（must — 联动系统自身同步,2026-06-03 加）

**触发**：`00_admin/hooks/lib/sync-rules.sh`（联动规则真值代码）

**必查联动**：
- `.claude/skills/file-linkage/SKILL.md`（本文件 — 给人读的规则表）

**为什么**：规则代码和本文件必须同步（hook 按代码跑、人按本表查,两边漂了联动系统就半失效）。讽刺的是过去没规则保护这层：`sync-rules.sh` 在 `hooks/lib/` 子目录下,而 Rule 8「hooks」trigger 是 `^00_admin/hooks/[^/]+$` 只匹配 hooks/ 一层、够不到 `lib/` 里的它。codex 2026-06-03 审查揪出,补这条 must 强制同步。

---

## §2 反向索引（按目标文件查谁改了它要联动）

> CC 想知道「改了 schemas.py 是因为什么 trigger?」时反向查。

| 目标文件 | 谁改了它要联动来 |
|---|---|
| `schemas.py` | Rule 1 (models.py 改) |
| `alembic/versions/*` | Rule 1 (models.py 改) |
| `routers/*` | Rule 1 (models.py 改) |
| `NetworkModels.swift` | Rule 1 (models.py 改) |
| `Models.kt`（Android 数据模型） | Rule 1 (models.py 改) |
| `Endpoints/*API.swift` | Rule 2 (routers 改) |
| `teacher_web src/api/client.js` | Rule 21 (后端 routers 改) |
| `BACKEND_DESIGN_LOG.md` | Rule 3 (system_features 改) + Rule 16 (backend 业务代码改) |
| `IOS_DESIGN_LOG.md` | Rule 3 (system_features 改) + Rule 14 (iOS Features 改) |
| `ANDROID_DESIGN_LOG.md` | Rule 3 (system_features 改) + Rule 15 (Android ui/features 改) |
| `WEB_DESIGN_LOG.md` | Rule 3 (system_features 改) + Rule 17 (teacher_web 业务代码改) |
| `ROLLCALL_DEVICE_DESIGN_LOG.md` | Rule 3 (system_features 改) + Rule 18 (点呼机 src/ 改) + Rule 20 (点呼机架构链任一改) |
| `hardware_design.md` | Rule 20 (点呼机架构链任一改) |
| `flow_design.md` | Rule 20 (点呼机架构链任一改) |
| `项目心智模型.md` | Rule 20 (点呼机架构链任一改) |
| `01_specs/rollcall 字典四件套 + RollCall_Spec.md` | Rule 22 (spec 字典链任一改) |
| `CHANGELOG.md` | Rule 23 (WIP.md / 版本演变一览 版本号改) |
| `WIP.md`（版本号部分） | Rule 23 (CHANGELOG.md 改) |
| `05_logs/版本演变一览.md` | Rule 23 (CHANGELOG.md 改 — 必连带加总表行+详细段) |
| `system_features.md` | Rule 19 (任一端 *_DESIGN_LOG 改) |
| `RootView.swift` | Rule 4 (Route.swift 改) |
| `hooks/README.md` | Rule 8 (hooks/* 改) |
| `CLAUDE.md` | Rule 9 (bin/*.sh 改) |
| `文档同步点清单.md` | Rule 9 (bin/*.sh 改) |
| `file-linkage/SKILL.md`（本表） | Rule 24 (sync-rules.sh 改) |

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
- 2026-05-08 itsuki 拍板：（1）点呼机当第 5 端建 03_dev/rollcall_device/ + ROLLCALL_DEVICE_DESIGN_LOG.md（2）补 6 条反向规则 Rule 14-19 — 业务代码改时温和提醒同步 *_DESIGN_LOG.md / system_features.md（3）Rule 3 system-features 必查列表加 ANDROID + ROLLCALL_DEVICE。规则总数 12 → 18。
- 2026-06-03 补漏：6-02 改 hardware_design.md 把手机「读 NFC 贴纸」反转成「写 NFC 贴纸」,旧联动系统漏提醒 → flow_design.md / ROLLCALL_DEVICE_DESIGN_LOG.md / 项目心智模型.md 留旧架构互相矛盾。补 Rule 20 rollcall-arch-chain（action）把这 4 个文件锁成同一条链 + 首次把 项目心智模型.md（5-29 新建时漏挂联动）纳入。规则总数 18 → 19。
- 2026-06-03（同日续）：itsuki「让所有文件互相联动 + 找别的有问题的文件」→ CC 论证「1256 文件全连 = 提醒太多反而没人看」否决全连,改派子代理系统审查联动盲点,独立验证(揪出子代理 2 处数字/范围不准:iOS Endpoints 数、字典是四件套不是三件套)后补 4 类真盲点,改 2 条 + 新增 3 条规则：① 修 Rule 17 trigger（teacher_web 活代码 index.html/client.js 过去零联动保护,规则盯着废弃的 .ts）+ 新增 Rule 21（后端路由改提醒查 client.js 的 65 处接口调用）② Rule 1 加 Android Models.kt（原只提醒 iOS 漏 Android 字段对齐）③ 新增 Rule 22 spec 字典链 ④ 新增 Rule 23 版本号链 CHANGELOG↔WIP。规则总数 19 → 22。盲点 5（iOS Endpoints 对接缺口,非规则 bug）/ 6（Android trigger 路径偏窄,影响小）暂不补。
- 2026-06-03（codex 审查后修）：派 codex GPT-5.5 xhigh 只读复审上面 22 条。codex 7 项发现,CC 独立核验(逮到 codex 建议的 vendor 排除写法 `(?!...)` 负向先行在 ERE 里不支持、照抄会坏)后分三档处理 ——【修】① Rule 17 trigger 第一版改宽会误报 vendor 第三方库 + 漏 index.css → 收窄成精确平铺 `index.html`/`index.css`/`api/*.js` ② Rule 1 文案「两端都要」改成说清 must 是「或」语义 ③ §1 加编号说明(消除 22/23 困惑)；【补】④ 新增 Rule 24 sync-rules-self(must) — codex 揪出联动系统自身盲点:规则代码 sync-rules.sh 在 hooks/lib/ 下、Rule 8 hooks 够不到,改了规则人读版无提醒；【报告暂不修】_check_demo_scaffold 返回值反转(真 bug 但牵涉退出码语义) / Rule 6 design-doc 引用的 teacher_requirements.md 已不存在(死路径) / must 列表路径无 `^…$` 锚定。规则总数 22 → 23。
