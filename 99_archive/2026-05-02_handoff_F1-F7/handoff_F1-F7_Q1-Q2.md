# Backend ↔ iOS 字段对齐 handoff（F1-F7 + Q1-Q2）

> **本文件用途**：新开 CC 会话时，先 `cat` 这个文件，里面有处理 7 条字段失配 + 2 条 schema 决策需要的全部背景。不需要上次会话上下文。
>
> **来源**：2026-05-01 早上 [Mac-主会话] 三个 Explore subagent 并行扫 `03_dev/backend/v1/` + `03_dev/student_ios/v1/` Swift + `03_dev/teacher_web/v1/` 后交叉对齐得出。原始 dump 在 `05_logs/raw/2026-05-01.md §3-§5`。
>
> **作成日**：2026-05-02 by [Mac-主会话]
>
> **本会话不做的事**：本文件仅整理问题 + 推荐方案 + 待 itsuki 拍板的决策；不动代码。代码改动留给新会话执行。

---

## 0. 给新会话 CC 的开场白

你好。这个任务是 **iOS 学生 App ↔ FastAPI 后端 字段契约对齐**（contract alignment — 翻译: 让前端发送 JSON 跟后端期望 schema 一致）。

**背景一句话**：
- iOS Swift 实装在 `03_dev/student_ios/v1/TomoshibiApp/`（已经写完 UI + mock 数据，0 行 URLSession 网络调用）
- FastAPI 实装在 `03_dev/backend/v1/app/`（已经起了 19 个 endpoint + Pydantic schema + ORM + JWT 认证）
- 两边各自先各干各的，今天开始对齐

**你需要做**：
1. 读完本文件 §1-§3（7 条 F + 2 条 Q + 2 条原则）
2. 跟 itsuki 确认 Q1+Q2 的拍板（如已拍则跳过）
3. 实施 §4 的执行清单（按顺序，每完成一条 commit）

**关键限制**（CLAUDE.md 已写，不重复）：
- 中文回答、解释每个概念
- 不私自 push / tag
- commit 不写 `Co-Authored-By`，message 详细
- itsuki 是零基础高中生，每段代码解释含义

---

## 1. F1-F7 字段失配清单（7 条 🔴 阻塞）

### F1 · `apply kind` 值不一致

**现状**：
- iOS（`Foundation/Routing/Route.swift` + `ApplyStubs.swift`）：枚举值 `stay / holiday / returncountry / study_absence`（snake_case 英文 — 翻译: 单词间用下划线连接的英文命名风格）
- backend（`app/schemas/application.py`）：Literal 字符串 `"外泊" / "帰省" / "帰国" / "学習欠席"`（日语原文）
- teacher_web（`v1/src/...`）：跟 backend 一致，用日语

**为什么会这样**：iOS 写得早，开发者图方便用英文 enum；backend 后写时按 spec §7.2 + 实物表 evidence 直接用日语。

**推荐方案**：**iOS 加映射层**（5 行 dict）
```swift
// 在 APIClient.swift 里加
static let kindToBackend: [String: String] = [
    "stay":          "外泊",
    "holiday":       "帰省",
    "returncountry": "帰国",
    "study_absence": "学習欠席",
]
```
请求出去前 lookup 转换，response 进来时反向转换。

**为什么 iOS 改而不是 backend 改**：日语是 spec 主语言（system_features.md 全日语 + 老师 web UI 全日语），改 backend 等于把整个数据库 enum 列重写 + 影响 teacher_web，成本大 5 倍。

**改动量**：~10 行（一个 dict + 两个转换函数）
**影响文件**：iOS 新建 `APIClient.swift`（F7 一起做）

---

### F2 · `stay_locations` 形状不一致

**现状**：
- iOS（`StayForm` form）：扁平字符串数组 `["1丁目 友達宅", "2丁目 喫茶店"]`
- backend（`app/schemas/application.py`）：对象数组 `[{kind: str, name: str, address: str?, phone: str?}]`

**为什么会这样**：iOS form 表单只收一行 text，backend 设计时考虑多场所要带地址电话方便老师联系。

**推荐方案**：**iOS form 改成对象**
- 现在 iOS 已经有 4 个独立字段（場所 / 住所 / 電話 / 種別 — 翻译: 场所/地址/电话/种别），但提交时被 join 成单字符串，改回对象数组就行
- 多场所支持留 v1.1（M3 之后），v1.0 先发单场所对象 `[{kind, name, address, phone}]`

**改动量**：~15 行（form submit handler 改 + APIClient 调用改）
**影响文件**：`Features/Apply/ApplyStubs.swift` StayForm submit + `APIClient.swift`

---

### F3 · `meals_skip` 形状不一致

**现状**：
- iOS（`StayForm.swift`）：对象数组 `[{date: "2026-05-01", meal: "朝食"}, {date: "2026-05-01", meal: "夕食"}]`
- backend（`app/schemas/application.py`）：`list[datetime]` ISO 8601 时间戳 — 翻译: 国际标准日期格式 `"2026-05-01T07:00:00"`

**为什么会这样**：backend 写时把"哪天哪顿不吃"压缩成单个 datetime（朝食 → 7:00 / 昼食 → 12:00 / 夕食 → 18:00），iOS 写时按 spec §7.7 食堂 Excel 输出格式（日期 + 食事种类两列）。

**推荐方案**：**backend 改成对象数组**
```python
# app/schemas/application.py
class MealSkipEntry(BaseModel):
    date: date  # 2026-05-01
    meal: Literal["朝食", "昼食", "夕食"]

# StayApplicationCreate
meals_skip: list[MealSkipEntry] = []
```

**为什么 backend 改而不是 iOS 改**：
- spec §7.7 食堂 Excel 输出本来就要"日期+食事種類"两个独立列
- backend `app/services/meals.py` 现在压成 datetime 后又要拆开做 Excel，多此一举
- iOS form UI 已经按"哪天哪顿"3×N 网格选，砍了 UX 退步

**改动量**：~20 行（schema 改 + ORM JSON 字段改 + meals.py 服务层改）
**影响文件**：`app/schemas/application.py` + `app/models/application.py` + `app/services/meals.py`

---

### F4 · iOS 多发 `student_id`，backend 拒绝

**现状**：
- iOS（推测）：POST body 里塞了 `"student_id": 123`
- backend（`app/api/applications.py`）：用 JWT token 自动取 `current_user.id`，body 里多发会被 Pydantic `model_config = {"extra": "forbid"}` 拒绝（422）

**为什么会这样**：iOS 没有 JWT 概念时写的，习惯把 user_id 一起发。

**推荐方案**：**iOS 砍掉 student_id 字段**（1 行删除 / 一开始 APIClient 设计就不要有）

**为什么**：JWT token（JSON Web Token — 翻译: 一种登录后获得的"通行证"，每次请求自动带上，后端从中读出"你是谁"）是 backend 唯一信任的 user_id 来源。iOS 自报 student_id 等于伪造身份，后端必拒。

**改动量**：~3 行（确保 APIClient body builder 不放 student_id）
**影响文件**：`APIClient.swift`（建立时就不要放）

---

### F5 · iOS 必填 `reason`，backend schema 没收

**现状**：
- iOS（每种申请 form 都有）：`reason: String` 必填字段「申請理由」
- backend（`app/schemas/application.py`）：所有 ApplicationCreate Pydantic schema 都没有 `reason` 字段

**为什么会这样**：backend 写时按实物表（外泊届）evidence 拆字段，实物表上确实没"理由"独立列；但 iOS UX 设计时考虑老师审批要看理由，加了。

**推荐方案**：**backend 加 `reason` 字段**（可选 → 必填渐进）

```python
# app/schemas/application.py — 共通基类
class ApplicationCreateBase(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
    # 其他字段...
```

**为什么 backend 加而不是 iOS 砍**：
- 修改届流程（spec §7.2.4-5）：学生提交修改届时**必须**写「修改の理由」，老师才能判断改是否合理 — reason 是修改届的必备字段
- 审计 log（auditLog）也要存「为什么改 / 为什么申请」
- 砍了的话老师 web UI 里申请详情页没"理由"列，UX 退步

**改动量**：~15 行（schema 加 + ORM 列加 + Alembic migration — 翻译: 数据库表结构升级脚本 — 加一列）
**影响文件**：`app/schemas/application.py` + `app/models/application.py` + 新 alembic migration

---

### F6 · 注册 endpoint backend 没实装

**现状**：
- iOS（`Features/Auth/AuthStubs.swift`）：4-step 注册 UI 已写完，`tryRegister()` 函数是 stub（mock 后直接进 home）
- backend（`app/api/auth.py`）：只有 `/auth/login`，**没有** `/auth/register/step1` 等端点
- spec（D10 设计）：纸面有完整设计，2026-04-30 落地到 `BACKEND_DESIGN_LOG.md` §3，但 0 行代码

**为什么会这样**：4-30 backend 起手版优先做了 P0 起手（schema / 申请提交 / 邮件 / 食堂 Excel），注册留给后续。

**推荐方案**：**backend 优先实装 4 step register 端点**

需要的端点（按 D10 设计）：
1. `POST /auth/register/step1` — 6 桁学号 + 姓名 + 生日 + 性别 → 校验学号格式 + 返回 step_token（一次性 — 翻译: 用过就废的临时 token）
2. `POST /auth/register/step2` — step_token + 邮箱 → 发邮箱验证码
3. `POST /auth/register/step3` — step_token + 邮箱验证码 → 验证通过返回新 step_token
4. `POST /auth/register/step4` — step_token + 房间号 + 密码 → 创建 student 记录 + 自动 login 返回 access_token

**改动量**：~200 行（API + service + schema + 邮件验证码 service + 测试）
**影响文件**：`app/api/auth.py`（扩展）+ `app/services/register.py`（新建）+ `app/schemas/auth.py`（扩展）+ `tests/test_register.py`（新建）

---

### F7 · iOS 完全没接 `URLSession`

**现状**：iOS 全部 mock seed 数据，0 行 `URLSession` / `URLRequest` / `JSONDecoder`。

**推荐方案**：**iOS 建 `APIClient` 层**

```
03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/
├── APIClient.swift        ← 单例 + base URL + JWT header 注入
├── APIError.swift         ← enum APIError（network / decode / 401 / 422 / 500）
├── Endpoints/
│   ├── AuthAPI.swift      ← login / register/step1-4
│   ├── ApplicationsAPI.swift  ← submit / list / detail / amendment
│   ├── RollcallAPI.swift  ← checkin / today
│   ├── StudyAPI.swift     ← tap / today / monthly
│   └── ProfileAPI.swift   ← me / update
└── Mappers/
    └── ApplyKindMapper.swift  ← F1 的 dict
```

base URL：开发期 `http://localhost:8000`（本机），真机时换成 LAN IP；生产 `https://api.tomoshibi.school`（暂定）。

JWT 注入：login 成功后 access_token 存 `KeychainService`（不是 UserDefaults，因为 token 是机密 — 翻译: 苹果 iOS 系统的安全存储区，比 UserDefaults 更安全），每次请求自动加 `Authorization: Bearer <token>` header。

错误处理：401 自动跳 LoginView，422 弹 toast「入力に誤りがあります」，500 弹 toast「サーバーエラー」。

**改动量**：~250 行（client base + 5 endpoint module + Keychain wrapper + error mapper）
**影响文件**：新建上述 8 个 swift 文件

---

## 2. Q1 + Q2 待 itsuki 拍板的决策

### Q1 · status 枚举对齐怎么办

**iOS 现状**：6 态 `draft / pending / approved / rejected / returned / cancelled`
**backend 现状**：5 态 `draft / pending / approved / rejected / withdrawn`

**3 个分歧 + CC 推荐**：

| # | iOS 名 | backend 名 | 含义 | CC 推荐 |
|---|---|---|---|---|
| a | `cancelled` | `withdrawn` | 学生主动撤回申请 | **统一用 `withdrawn`**（更国际化、英文母语者一看就懂、AC 面试讲也好） |
| b | `returned` | （无） | 老师退回让学生改 | **保留并加进 backend**（spec §7.2.4 修改届流程依赖，砍了流程崩） |
| c | `draft` | `draft`（实际不存）| 学生本地草稿 | **iOS 保留 / backend 砍**（草稿在 App 本地存就行，没提交就没数据库记录） |

**最终对齐枚举**（5 态 server-side）：
```python
class ApplicationStatus(str, Enum):
    pending = "pending"      # 提交后 chain 审批中
    approved = "approved"    # chain 全通过
    rejected = "rejected"    # 任一节点拒绝
    returned = "returned"    # 退回学生修改
    withdrawn = "withdrawn"  # 学生主动撤回
```

iOS client-side 多一个 `draft` 态（本地未提交）。

**itsuki 待决**：以上 3 条推荐 OK 不 OK？

---

### Q2 · `reason` 字段归到哪

**3 选 1**：

| 选项 | 内容 | 优 | 劣 |
|---|---|---|---|
| A | **backend 加 `reason` 字段** | 修改届 / 审计 / 老师审批 UI 全有"理由"列；干净 | backend 改 schema + migration + ORM + 测试 ~15 行 |
| B | iOS 砍 `reason` 字段 | iOS 改 1 行 | UX 退步 / 修改届流程实现不了 / 老师审批盲判 |
| C | 塞到 `leave_method` 末尾 hack | 不动 schema | 数据脏 / 解析麻烦 / 永远拆不出来 |

**CC 推荐 A**（backend 加）— B/C 都伤害产品。

**itsuki 待决**：选 A 吗？

---

## 3. 两条原则

### 原则 1 · 单源真值（CLAUDE.md §文档一致性规则）
所有共用规则（≥2 端涉及）的权威源是 **`02_design/system_features.md`**，不是 iOS 代码也不是 backend 代码。改完字段后**同步**更新 `system_features.md` + 各端 `*_DESIGN_LOG.md`。

### 原则 2 · 不动 teacher_web
teacher_web 由别 agent / 别会话维护，本任务**不碰** `03_dev/teacher_web/`。如果改 backend schema 影响了 teacher_web，列出影响清单 dump 给 itsuki，等她协调。

---

## 4. 执行顺序建议

按依赖顺序，每完成一条 commit 一次：

| 顺位 | 任务 | 依赖 | 改动量 |
|---|---|---|---|
| **1** | Q1+Q2 拍板 → 落地到 `system_features.md` §7.2 | — | ~30 行文档 |
| **2** | F5 backend 加 `reason` 字段 + Alembic migration | Q2 | ~15 行 |
| **3** | F3 backend 改 `meals_skip` 形状 + `meals.py` 调整 + Alembic migration | — | ~20 行 |
| **4** | Q1 backend status enum 改（5 态 → `withdrawn` rename + 加 `returned`）+ Alembic migration | Q1 | ~10 行 |
| **5** | F6 backend 实装 register 4 step | — | ~200 行 + 测试 |
| **6** | F7 iOS 建 `APIClient` 层（含 KeychainService）| — | ~250 行 |
| **7** | F1 iOS `ApplyKindMapper` + 集成到 APIClient | F7 | ~10 行 |
| **8** | F4 iOS APIClient body builder 不发 student_id | F7 | ~3 行 |
| **9** | F2 iOS StayForm submit handler 改对象数组 | F7 | ~15 行 |
| **10** | iOS 各 endpoint 实接（替换 mock）+ 联调测试 | F1-F9 | ~150 行 |

**预估总工时**：5-8 小时（一个会话能搞完，分两次会话也行）。

**关键里程碑**：
- 完成 1-5 = backend 完整可联调
- 完成 6-9 = iOS 网络层就位
- 完成 10 = 全栈打通 → 真机测试

---

## 5. 关键参考文件路径

| 用途 | 路径 |
|---|---|
| 规则真值 | `02_design/system_features.md` §7.2（出寮届）+ §7.7（食堂）|
| backend ORM + schema | `03_dev/backend/v1/app/models/` + `app/schemas/` |
| backend API | `03_dev/backend/v1/app/api/` |
| backend 设计 LOG | `03_dev/backend/v1/BACKEND_DESIGN_LOG.md` |
| backend Alembic 用法 | `03_dev/backend/v1/alembic/` + `alembic.ini` |
| backend 测试 | `03_dev/backend/v1/tests/` |
| iOS 全部 swift | `03_dev/student_ios/v1/TomoshibiApp/` |
| iOS 当前数据模型 | `Foundation/Seed/SeedModels.swift`（18 struct）|
| iOS 设计 LOG | `03_dev/student_ios/IOS_DESIGN_LOG.md` |
| 5-01 原始失配 dump | `05_logs/raw/2026-05-01.md` §3-§5 |

---

## 6. 不要碰的文件

- `03_dev/teacher_web/v1/*` — 别会话主写区
- `03_dev/student_ios/v1/TomoshibiApp/` 里**已经写好的 UI 层**（`Features/*` 的 SwiftUI View）— 只动数据流（Network 层 + AppStore.recordCheckin 等方法体），不改 View
- `01_specs/` — 规格冻结源，要改先问 itsuki
- 任何 git tag / push — itsuki 明示前不动

---

## 7. 完成后必做

1. 跑 pytest（backend）+ xcodebuild（iOS）— 都绿
2. 真机联调（iOS Simulator + backend `uvicorn` 起着）— 至少跑通 login + 提交一份外泊届
3. 更新 `system_features.md` + `BACKEND_DESIGN_LOG.md` + `IOS_DESIGN_LOG.md`
4. 更新 `CHANGELOG.md` 顶部（按 SOP 决定 patch / minor）
5. commit + 给 itsuki 三段式中文总结（原来 / 问题 / 改成）

---

**END** — 把这个文件 cat 一下当背景，然后开干。
