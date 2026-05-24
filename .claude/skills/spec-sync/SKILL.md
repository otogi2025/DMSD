---
name: spec-sync
description: DMSD 跨端字段对齐自动检查 — 比 file-linkage 深一层。file-linkage = 提醒去查；spec-sync = 真扫并报告差异。提取 backend models/schemas + iOS NetworkModels + Android entity 字段对比，列出不对齐项（命名漂移 / Optional 不一致 / 缺字段 / 类型错）。
when_to_use: ⭐ 触发 — itsuki 说「跨端检查 / 字段对齐 / spec 同步 / 端对齐 / API 对齐」/ 改完 backend models.py / schemas.py 后想确认所有客户端跟得上 / 集成测试报「Decoding error」类型问题怀疑字段漂移 / 上线前最后一道字段一致性检查。**当前阶段**：backend 还没真上线，本 skill 价值是在 backend 上线后立刻跑（demo 阶段可以记 TODO 跳过）。
allowed-tools: Read, Bash, Grep, Glob
---

# Spec Sync Skill — 跨端字段对齐自动检查

> **核心理念**：DMSD 字段对齐是最大 bug 来源。手动 grep 对比累 + 易漏。本 skill 是**字段提取 + 对比 + 报告差异**的 SOP，让 CC 一次扫完报告所有不对齐项。
>
> **跟 file-linkage 区别**：
> - `file-linkage` = 改 A 提醒去查 B（轻量提醒，不真扫）
> - `spec-sync` = 真扫 backend / iOS / Android，逐字段对比报告差异
>
> 调用本 skill = 主动跑深度检查，调用频次低但每次跑都是真活。

---

## §0 主流程（5 步）

```
Step 1: 列要对比的实体（哪些 model / 哪些功能）
Step 2: 提取 backend 字段（models.py SQLAlchemy + schemas.py Pydantic）
Step 3: 提取 iOS 字段（NetworkModels.swift Codable struct）
Step 4: 提取 Android 字段（entity / DTO / Retrofit）
Step 5: 4 端字段表对比 → 报告差异
```

---

## §1 Step 1: 列要对比的实体

询问 itsuki 或主动判断对比哪些：

```
A. 全量扫描（找出所有共享实体）— 慢，但全
B. 单个实体（itsuki 指定，比如「对齐 Student」）— 快
C. 改动驱动（git diff 看 backend models 改了啥，只对比改动相关）— 平衡
```

默认走 **C 改动驱动** — 跑这个：

```bash
git log -1 --name-only -- 03_dev/backend/v1/app/models.py 03_dev/backend/v1/app/schemas.py
git diff HEAD~1 -- 03_dev/backend/v1/app/models.py 03_dev/backend/v1/app/schemas.py
```

提取出本次改动涉及的 model 名（`class Student`、`class CheckIn` 等）。

---

## §2 Step 2: 提取 backend 字段

### 2.1 SQLAlchemy models

```bash
# 提取 class X 段
awk '/^class Student/,/^class [A-Z]/' 03_dev/backend/v1/app/models.py
```

或更精确的提取（如果安装了 ast 工具）：

```bash
python3 -c "
import ast, sys
tree = ast.parse(open('03_dev/backend/v1/app/models.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Student':
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                print(f'{item.target.id}: {ast.unparse(item.annotation)}')
"
```

输出：
```
id: int
student_number: str
name: str
created_at: datetime
```

### 2.2 Pydantic schemas

```bash
awk '/^class Student/,/^class [A-Z]/' 03_dev/backend/v1/app/schemas.py
```

注意：schemas 通常分 Request / Response / Base，要全提取。

### 2.3 整理成表

```
backend.models.Student     |  backend.schemas.StudentResponse
─────────────────────────────────────────────────────────────
id: int                    |  id: int
student_number: str        |  student_number: str
name: str                  |  name: str
created_at: datetime       |  created_at: datetime
                          |  is_active: bool      ← schemas 多一个，确认是 computed
```

---

## §3 Step 3: 提取 iOS 字段

### 3.1 NetworkModels.swift

```bash
awk '/^struct Student/,/^}$/' \
  03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift
```

或：

```bash
grep -A 20 "struct Student" \
  03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift
```

### 3.2 检查 CodingKeys

Swift Codable 需要 CodingKeys 把 `studentNumber` 映射到 `student_number`。**必看**：

```swift
struct Student: Codable {
    let id: Int
    let studentNumber: String
    let name: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case studentNumber = "student_number"
        case name
        case createdAt = "created_at"
    }
}
```

如果**没有 CodingKeys** 或某字段漏了 → 字段会解码失败。

---

## §4 Step 4: 提取 Android 字段（当前阶段：跳）

Android 还没起。本步当前跳过，但报告 itsuki：「Android 端待实装，对齐检查留 TODO」。

未来 Android 实装后：

```bash
# Kotlin data class
grep -A 15 "data class Student" 03_dev/android/app/src/main/java/.../entity/Student.kt
```

注意 `@SerializedName` 注解（Gson）/ `@Json(name="...")` 注解（Moshi）— 跟 iOS CodingKeys 同理。

---

## §5 Step 5: 对比报告

### 5.1 标准报告格式

```
🔍 字段对齐检查报告 — Student

✅ 对齐字段（4/5）
  - id: int / Int
  - student_number / studentNumber (CodingKeys ✅)
  - name: str / String
  - created_at / createdAt (CodingKeys ✅, dateDecodingStrategy 需为 .iso8601)

⚠️ 不对齐字段（1）
  - is_active: bool (backend) / 缺 (iOS)
    → backend schemas 有，iOS NetworkModels 没。
    → 决策：iOS 需要 / 不需要这个字段？
    → 如需要：iOS 加 `let isActive: Bool` + CodingKeys + 用到的 view 加显示
    → 如不需要：backend 是否真需要返回？或加 `exclude_unset` 过滤

❌ 类型不一致（0）

⚠️ Optional 不一致检查
  - backend `name: str` (非 nullable) / iOS `let name: String` ✅ 一致
  - backend `email: Optional[str]` / iOS `let email: String?` ✅ 一致

📋 Android：跳过（端未实装，TODO 记录）
```

### 5.2 决策建议

每个差异都给出修复建议（不是 CC 自动改 — 等 itsuki 决策方向）：

| 差异类型 | 建议 |
|---|---|
| backend 多字段 | iOS 加 / backend 改 `exclude_unset` |
| iOS 多字段 | iOS 删 / backend 加（取决于谁是 source of truth） |
| 类型不一致 | 决定权威端，另一端跟 |
| Optional 不一致 | 看业务语义（这字段真的可空吗？） |
| CodingKeys 缺失 | iOS 必加 |

---

## §6 反模式

### ❌ 反模式 1: 只看 schemas 不看 models
schemas 是接口层，models 是数据库层。两者也可能漂移（schemas 加了字段但 models 没加 → 接口返回 None）。**两层都要扫**。

### ❌ 反模式 2: 不查 CodingKeys 直接说 iOS 字段对齐
iOS 有 `studentNumber` 字段，backend 有 `student_number` — 不是自动对应的，**必须看 CodingKeys**。

### ❌ 反模式 3: 不查 dateDecodingStrategy
backend 返回 ISO 8601 字符串，iOS Date 默认期望 timestamp。**JSONDecoder 必须 `.iso8601`**。

### ❌ 反模式 4: 报告里只列「不对齐」不给修复建议
itsuki 看了不知道怎么改，要回头问。一次到位给方案。

### ❌ 反模式 5: 跑完不更新 IOS_DESIGN_LOG / BACKEND_DESIGN_LOG
对齐报告跑完直接被忘 → 同样的差异下次又出现。**报告里关键差异要 dump 到对应 DESIGN_LOG**。

---

## §7 配套文件 / skill

- `.claude/skills/file-linkage/SKILL.md` — 联动提醒（轻量）
- `.claude/skills/new-feature/SKILL.md` — 新功能 4 端实装时 §5 字段对齐自检（手动版）
- `00_admin/hooks/post-edit-sync-check.sh` — 改 models 后 hook 提醒「考虑跑 spec-sync」
- `bin/sync-check.sh` — 通用同步检查（不深入字段层）

---

## §8 未来增强（v1.0 后再做）

- 写一个 `bin/spec-sync.py` 把字段提取 + 对比自动化
- CI 集成（GitHub Actions 跑 spec-sync，PR 不对齐拒绝合并）
- 引入 OpenAPI schema 作为 single source（backend 自动生成 → iOS / Android 自动生成 client）

当前是手动 SOP，未来工程化。

---

**最后更新**：2026-05-04 itsuki 拍板新建（backend 上线后立刻用 — 当前 demo 阶段记 TODO）
