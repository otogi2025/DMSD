---
name: new-feature
description: DMSD 新功能 5 端实装模板 — spec → backend → iOS → Android → 点呼机 TODO 顺序 / 每端最小必改文件清单 / 字段对齐自检 / 完成后 sync-check。⭐ 解决 CC 永远漏端 / 字段不对齐两大失职。DMSD 是 5 端联动项目（backend / iOS / Android / teacher_web / rollcall_device 点呼机）+ spec + 文档，新功能必须每端考虑。
when_to_use: ⭐ 触发 — itsuki 说「新功能 X / 加 Y 功能 / 实装 Z / 做 W / 加个 N」/ 当前任务是从零做一个完整 user-facing 功能（不是改 bug / 重构 / 文档调整）。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# New Feature Skill — DMSD 5 端实装模板

> **核心理念**：DMSD 一个新功能 = spec + backend + iOS + Android + 点呼机 + 文档**多端联动**。CC 默认只做 itsuki 直接说的那端，**剩下端一定漏**。本 skill 让 CC 做完一端就主动问下一端，做完所有涉及端 + 字段对齐自检 + sync-check 才算完事。
>
> **2026-05-08 更新**：itsuki 拍板把点呼机当第 5 端，跟 backend / iOS / Android / teacher_web 4 端对称管理。当前点呼机骨架阶段（代码 0 行），D1-D6 决策待拍板 + 配件到货后开始实装 — 新功能涉及点呼机时先记 TODO。
>
> **2026-05-04 时点状态**：iOS 在前面跑，backend 还没真上线，Android 还没起。所以实战流程是 **spec → iOS demo → 后续 backend 真上线时补字段对齐**。本 skill 写的是**完整理想流程**，做不到的端记 TODO。

---

## §0 5 端实装顺序（不可跳序）

```
Step 1: spec 段（先写规格，再实装 — 不能反过来）
  └─ 02_design/system_features.md 加章节
  └─ 各端 *_DESIGN_LOG.md 引用 / 补端专属设计

Step 2: backend 段（后端先于客户端 — 客户端依赖后端 API）
  └─ models.py + schemas.py + routers/*.py + alembic 迁移

Step 3: iOS 段（v1.0 主推 iOS）
  └─ NetworkModels.swift + Endpoints/*API.swift + View

Step 4: Android 段（v1.0 同步上线，但当前 demo 阶段先记 TODO）
  └─ entity + retrofit interface + Compose screen / 或 TODO

Step 5: 点呼机端（rollcall_device — 涉及 NFC 点呼 / LED 状态 / 日语播报时必看）
  └─ src/{nfc,led,audio,api}/*.py + ROLLCALL_DEVICE_DESIGN_LOG.md / 当前骨架阶段先记 TODO

Step 6: 字段对齐自检 + sync-check.sh + commit
```

**例外**：itsuki 明确说「这次只做 spec」/「这次只做 iOS demo」→ 跳后续步骤但**必须报告漏的端 + 加 TODO**。

**端涉及判断**：不是所有功能都涉及全 5 端。判断规则：
- 学生 App 内功能（申请 / 公告 / 个人页）→ backend + iOS + Android（3 端）
- 老师 / 舍监后台功能 → backend + teacher_web（暂未在本 skill 详写）
- 物理点呼相关（卡片 / NFC / 现场播报 / 状态灯）→ backend + rollcall_device（+ iOS/Android 显示）
- 跨域功能（如「老师推送公告 → 学生收到」）→ 全 5 端

---

## §1 Step 1: Spec 段

### 1.1 写 system_features.md

`02_design/system_features.md` 是「≥2 端涉及」的共用层。新功能默认要加章节。

最小必填：
- 功能名 + 一句话描述
- 用户视角的流程（who do what when how）
- 涉及哪些端（iOS / Android / Backend / 点呼机）
- 关键数据字段（草稿，正式定义在 backend models）
- 边界 case（错误 / 重试 / 离线）

### 1.2 各端 DESIGN_LOG 引用

如果功能有端专属设计（比如 iOS 需要某个特殊动画 / 后端需要特殊队列处理）→ 在对应 `*_DESIGN_LOG.md` 加章节，并从 system_features.md 引用过去。

判断标准（详见 memory `feedback_design_doc_layers.md`）：
- ≥2 端共用 → system_features.md
- 某端专属 → 端的 DESIGN_LOG.md

### 1.3 反例

❌ 跳过 spec 直接写 iOS 代码 → 流程没想清楚，做到一半推翻
❌ spec 只写 iOS 视角不提 backend → backend 实装时缺字段
❌ system_features.md 写了端专属细节 → 应该下沉到端的 DESIGN_LOG

---

## §2 Step 2: Backend 段

### 2.1 最小必改文件清单

```
03_dev/backend/app/models.py            ← SQLAlchemy ORM 表结构
03_dev/backend/app/schemas.py           ← Pydantic 请求/响应 schema
03_dev/backend/app/routers/<feature>.py ← API 路由
03_dev/backend/alembic/versions/*.py    ← 数据库迁移（必生成新版本）
03_dev/backend/app/main.py              ← 注册新 router（如果是新文件）
03_dev/backend/BACKEND_DESIGN_LOG.md    ← 端专属设计（如果有）
```

### 2.2 实装顺序

```
1. models.py 加表 / 字段
2. alembic revision --autogenerate -m "add X" → 生成迁移
3. schemas.py 加 Request / Response
4. routers/<feature>.py 加 endpoint（用 schemas）
5. main.py include_router
```

### 2.3 检查清单

- [ ] models 字段类型跟 spec 描述一致
- [ ] schemas 字段名跟 models 一致（or alias）
- [ ] alembic 迁移可以 upgrade + downgrade
- [ ] router 的 path / method 跟 iOS 后续要用的一致
- [ ] 错误返回用 HTTPException + 标准 error code

---

## §3 Step 3: iOS 段

### 3.1 最小必改文件清单（基于现有 iOS 结构）

```
03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift
  ← Codable struct 跟 backend schemas 对齐

03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/<X>API.swift
  ← API client 调用

03_dev/student_ios/v1/TomoshibiApp/Features/<X>/<X>View.swift
  ← SwiftUI view（新建或改）

03_dev/student_ios/v1/TomoshibiApp/Foundation/AppState/AppStore.swift
  ← 如果功能涉及全局 state

03_dev/student_ios/v1/TomoshibiApp/Root/Route.swift + RootView.swift
  ← 如果加新页面 case + switch

03_dev/student_ios/IOS_DESIGN_LOG.md
  ← 视觉 / 流程 / 字段设计（必加章节）
```

### 3.2 实装顺序

```
1. IOS_DESIGN_LOG.md 加章节（先想清楚 UI / 状态 / 边界）
2. NetworkModels.swift 加 Codable struct（对齐 backend schemas）
3. Endpoints/<X>API.swift 加调用方法
4. Features/<X>/<X>View.swift 实装 view
5. 如果新页面 → Route.swift case + RootView.swift switch
6. 在 Xcode 跑 build 确认编译通过
```

### 3.3 检查清单

- [ ] NetworkModels 字段名跟 backend schemas 完全一致（**snake_case ↔ camelCase 用 CodingKeys**）
- [ ] 新 view 在 Xcode 真机 / 模拟器跑通
- [ ] Route + RootView 联动改完
- [ ] **bin/sync-ios-refs.sh 跑过**（同步到 Tomoshibi-iOS repo）

---

## §4 Step 4: Android 段（当前 demo 阶段：记 TODO）

Android 还没实装基础架构。现在的做法：

1. **`00_admin/TODO.md` 加一条**：「Android 端实装 X 功能（spec 见 system_features §X）」
2. 不写 Android 代码（避免半成品堆积）
3. 报告 itsuki：「Android 端记了 TODO，等基础架构起来后回来做」

未来 Android 实装时（不是当前任务）：
- entity / DTO 对齐 backend schemas
- Retrofit interface 对齐 routers
- Compose screen / ViewModel

---

## §4.5 Step 5: 点呼机端 rollcall_device（当前骨架阶段：记 TODO）

> **2026-05-08 itsuki 拍板**：点呼机当第 5 端，跟 backend / iOS / Android / teacher_web 对称管理。当前骨架阶段（代码 0 行），D1-D6 决策待拍板 + 11 件配件到货后开始实装。

**新功能涉及点呼机的判断**：功能跟物理 NFC 卡 / LED 状态灯 / 日语语音播报 / 现场点呼相关 → 涉及；纯 App 内功能（申请 / 公告 / 个人页）→ 不涉及。

**当前做法**（骨架阶段）：

1. **`00_admin/TODO.md` §🛰️ 点呼机第 5 端 backlog 加一条**：「rollcall_device 端实装 X 功能（spec 见 system_features §X）」
2. **`03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` 加章节**（设计先行，代码等 D1-D6 + 配件）
3. 不写点呼机代码（避免在 D1-D6 决策没定 / 硬件没到时写废代码）
4. 报告 itsuki：「点呼机端记了 TODO + 加了 DESIGN_LOG 章节，等 D1-D6 拍板 + 配件到货后回来做」

未来点呼机实装时（不是当前任务）：
- `03_dev/rollcall_device/src/nfc/*.py` — NFC 读卡 / 写动态 NFC（PN532 + ST25DV16K）
- `03_dev/rollcall_device/src/led/*.py` — GPIO 状态灯（蓝/绿/红/白）
- `03_dev/rollcall_device/src/audio/*.py` — 日语 TTS 播报
- `03_dev/rollcall_device/src/api/*.py` — POST /checkin 调 backend
- `03_dev/rollcall_device/src/main.py` — 主循环串起来
- backend `routers/rollcall.py` 端点对齐
- iOS / Android 显示点呼结果端对齐

---

## §5 Step 6: 字段对齐自检

> **DMSD 最大 bug 来源**：backend schemas.py 字段名 ≠ iOS NetworkModels.swift 字段名 → 客户端解码失败。

### 5.1 手动 diff（当前阶段够用）

```bash
# 看 backend X 功能的字段
grep -A 10 "class X" 03_dev/backend/app/schemas.py

# 看 iOS X 功能的字段
grep -A 10 "struct X" 03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift
```

肉眼对比每个字段名 + 类型（注意 snake ↔ camel 转换 / Optional 一致性）。

### 5.2 自动 diff（未来 backend 上线后）

→ 见 `spec-sync` skill（更深的字段提取 + 报告差异自动化）。

### 5.3 常见漂移

| backend | iOS | 是否对齐 |
|---|---|---|
| `student_id: int` | `studentId: Int` | ✅ camelCase 转换 |
| `created_at: datetime` | `createdAt: Date` | ✅ + JSONDecoder dateDecodingStrategy |
| `name: str` | `name: String?` | ❌ Optional 不一致 |
| `status: str` | `status: StatusEnum` | ⚠️ enum 值要枚举完整 |

---

## §6 Step 7: 完成后动作

```bash
# 1. 跑 sync-check 确认联动文件都改了
bash bin/sync-check.sh

# 2. iOS 同步到独立 repo
bash bin/sync-ios-refs.sh

# 3. 看 git status 整体确认
git status

# 4. commit（按 Conventional Commits + 中文 + 不加 Co-Authored-By）
git add <文件们>
git commit -m "feat(<scope>): X 功能 5 端实装"
```

**不主动 push** — 按 commit/push 协作分工 itsuki 拍板。

---

## §7 反模式

### ❌ 反模式 1: 只做 itsuki 字面说的那端
itsuki 说「iOS 加个签到按钮」→ CC 只改 iOS。后端没 endpoint → iOS 跑起来报 404。
**正确**：默认 5 端都考虑（backend / iOS / Android / teacher_web / 点呼机），每端做或记 TODO，做完报告每端状态。

### ❌ 反模式 2: 字段不对齐自检
两端各自写完，跑起来 iOS 解码报错才发现 `created_at` vs `createdAt` 漂移。
**正确**：实装完成时 §5 必跑。

### ❌ 反模式 3: 跳过 spec 直接写代码
头脑里设计写到一半推翻，已经写的代码白扔。
**正确**：先 spec（即使简短）再代码。

### ❌ 反模式 4: 漏更新 DESIGN_LOG
代码改完 IOS_DESIGN_LOG.md / BACKEND_DESIGN_LOG.md 没动 → 文档跟代码漂移。
**正确**：file-linkage skill / hook 兜底，但本 skill §3 §2 已经把 DESIGN_LOG 列入必改清单。

### ❌ 反模式 5: 漏 alembic 迁移
backend models.py 改了但没生成 alembic 迁移 → 数据库 schema 跟 ORM 漂移，部署炸。
**正确**：§2.2 顺序里 alembic 是必做项。

---

## §8 配套文件 / skill

- `02_design/system_features.md` — 共用 spec
- `03_dev/{backend,student_ios,...}/<X>_DESIGN_LOG.md` — 端专属 spec
- `bin/sync-check.sh` / `bin/sync-ios-refs.sh` — 同步脚本
- `.claude/skills/file-linkage/SKILL.md` — 联动规则总表
- `.claude/skills/spec-sync/SKILL.md` — 字段对齐自动化（未来用）
- memory `feedback_design_doc_layers.md` — 共用层 vs 端专属判断

---

**最后更新**：2026-05-09 itsuki 拍板加点呼机为第 5 端（4 端 → 5 端，加 §4.5 / 端涉及判断更新 / commit 例子改 5 端）
**初版**：2026-05-04 itsuki 拍板新建（CC 漏端 / 字段不对齐 → SOP 化）
