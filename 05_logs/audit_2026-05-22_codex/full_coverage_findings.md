# Codex Full Coverage Findings — 2026-05-22 全文件覆盖审查

## 总览

- 🔴 阻塞上线：14 条
- 🟡 该修：23 条
- 🟢 优化 / 信息：2 条
- 合计：39 条
- 跟 Claude 重复 / 复核仍存在：13 条
- Claude 漏的 / Codex 独立发现：26 条

本轮只审查和记录问题，没有修改业务代码。  
全文件覆盖证据在 `05_logs/audit_2026-05-22_codex/file_coverage.tsv`。  
本轮机器读取范围是 1003 个文件：957 个已跟踪文件 + 46 个未跟踪文件。  
其中 656 个文本文件按内容扫描，347 个二进制文件按路径、大小、行数占位和 `sha256_16` 指纹登记。  

说明：API 是“应用程序接口”。endpoint 是“端点”。CI 是“持续集成”。JWT 是“JSON Web Token 登录令牌”。Alembic 是“数据库迁移工具”。SQLite 是“轻量数据库”。NFC 是“近场通信”。ECDSA 是“椭圆曲线签名”。nonce 是“一次性随机数”。SDK 是“软件开发工具包”。CVE 是“已知漏洞编号”。npm 是 JavaScript 依赖管理工具。pip-audit 是 Python 依赖漏洞检查工具。

---

## 维度 1 — 全文件覆盖与项目总览

### [Codex-FC-001] 🔴 多个 5-21 核心修复文件仍是未跟踪状态，fresh clone 会丢

- 位置：`00_admin/系统bug专栏.md:1`
- 描述：`git status --short` 显示这些核心文件仍是 `??`：`00_admin/系统bug专栏.md`、`.github/workflows/test.yml`、`03_dev/backend/v1/pyproject.toml`、3 个后端测试文件、2 个 Alembic 迁移、`RollCallAPI.swift`、`bin/check_overview_drift.sh`、`00_admin/hooks/post-edit-format.sh`。如果现在推到 GitHub，别人重新 clone 后会缺少 CI、测试、迁移、系统 bug 总表和 iOS 点呼 API。
- 建议改法：fix 阶段先决定这些文件是否进入正式仓库。要进仓库的统一 `git add`，不该进仓库的写入 `.gitignore` 或归档说明。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-002] 🟡 project-overview 体量表和实际文件数再次漂移

- 位置：`.claude/skills/project-overview/SKILL.md:29`
- 描述：`§0.1` 写“committed 957 + 未 commit 23 = 实际 980”。本轮启动对账也显示总数 980，但目录仍漂移：`03_dev/` 写 395 / 实际 396，`99_archive/` 写 431 / 实际 432，且 `.github/`、`bin/` 等目录依赖未提交文件。
- 建议改法：等本轮审查产物是否纳入项目决定后，再跑 `bash bin/check_overview_drift.sh`，按输出更新 `project-overview/SKILL.md`。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-003] 🟡 严格锁和 skill 仍引用不存在的旧路径

- 位置：`.claude/session-coord.config.json:9`
- 描述：strict lock 仍指向 `01_specs/rollcall/RollCall_Spec_v0.1.md` 和 `dictionary_v0.1_v0.2_v0.3.md`，实际仓库里已经是 `RollCall_Spec.md` 和字典拆分文件。`.claude/skills/new-feature/SKILL.md:84` 和 `.claude/skills/spec-sync/SKILL.md:45` 也还写旧后端路径 `03_dev/backend/app/...`，实际代码在 `03_dev/backend/v1/app/...`。
- 建议改法：把 lock 和 skill 的路径统一到当前 v1 目录。路径类配置建议用脚本跑存在性检查。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-004] 🟡 系统 bug 专栏状态和实际文件不一致

- 位置：`00_admin/系统bug专栏.md:335`
- 描述：C-048 仍写 `.github/workflows/` 不存在；实际 `.github/workflows/test.yml` 已出现但未跟踪。C-049 在 `00_admin/系统bug专栏.md:632` 仍写没有 pytest 配置；实际 `pyproject.toml` 已出现但未跟踪。C-050 在 `00_admin/系统bug专栏.md:637` 仍写没有 rollcall / study / applications 测试；实际测试文件已出现但测试失败。
- 建议改法：把状态改成“已生成，待提交，待验证”。不要把“文件不存在”和“文件存在但失败”混在一起。
- 跟 Claude 关系：[重复 C-048 / C-049 / C-050]，但当前状态仍漂移

---

## 维度 2 — 测试、CI 与迁移

### [Codex-FC-005] 🔴 后端默认 pytest 现在无法进入测试收集

- 位置：`03_dev/backend/v1/pyproject.toml:15`
- 描述：`filterwarnings` 把 `DeprecationWarning` 当成 error。`03_dev/backend/v1/app/main.py:67` 使用 FastAPI 的 `@app.on_event("startup")`，导入时触发弃用警告。结果是 `.venv/bin/python -m pytest tests -q` 在收集阶段失败。
- 建议改法：改用 FastAPI lifespan，或者把这条特定 warning 精确忽略。然后重新跑默认 pytest，保证不靠命令行临时 `-W ignore` 才能测试。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-006] 🔴 后端忽略 warning 后仍有 2 failed / 8 errors

- 位置：`03_dev/backend/v1/tests/test_rollcall.py:30`
- 描述：`RollCallSession(target_date=...)` 传了模型不存在的字段；实际模型从 `03_dev/backend/v1/app/models.py:520` 开始，没有 `target_date`。`03_dev/backend/v1/tests/test_study.py:29` 使用不存在的 `StudyAttendanceRoster`，实际类名是 `StudyRoster`。同文件 `test_study.py:64` 和 `:81` 用 `date.today()` 提交学習请假，超过 19:40 后会被 `03_dev/backend/v1/app/routers/study.py:364` 拒绝，测试随时间变化。
- 建议改法：测试 fixture 改到当前模型名和当前字段。时间相关测试要固定时钟或用明天日期。
- 跟 Claude 关系：[重复 C-050] 的后续复核；具体失败是 Codex 独立发现

### [Codex-FC-007] 🟡 测试说明写 in-memory，但实际写本地数据库文件

- 位置：`03_dev/backend/v1/tests/conftest.py:1`
- 描述：文件注释写“in-memory SQLite”，但 `03_dev/backend/v1/tests/conftest.py:7` 设置的是 `sqlite:///./test_tomoshibi.db`。这会在工作目录生成本地数据库文件，测试隔离程度和注释不一致。
- 建议改法：要么改成真正的 `sqlite:///:memory:` 并处理连接池，要么把注释改成“文件型测试 SQLite”。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-008] 🟡 CI 设置了 DATABASE_URL，但 Alembic 不读取它

- 位置：`.github/workflows/test.yml:47`
- 描述：CI 里给迁移步骤设置了 `DATABASE_URL=sqlite:///./ci_test.db`。但 `03_dev/backend/v1/alembic/env.py:46` 从 Alembic 配置读 `sqlalchemy.url`，而 `03_dev/backend/v1/alembic.ini:89` 写死 `sqlite:///./tomoshibi_dev.db`。结果 CI 以为在测临时库，实际可能迁移开发库文件。
- 建议改法：在 `env.py` 里优先读取环境变量 `DATABASE_URL`，没有时再用 `alembic.ini`。
- 跟 Claude 关系：[重复 C-048] 的实现复核

### [Codex-FC-009] 🟡 新增唯一约束迁移在 SQLite 下高风险

- 位置：`03_dev/backend/v1/alembic/versions/a8b9c0d1e2f3_add_rce_idempotency_unique.py:28`
- 描述：迁移直接 `op.create_unique_constraint(...)`。SQLite 对 ALTER TABLE 约束支持有限，Alembic 通常需要 `batch_alter_table`。当前 CI 又用 SQLite，所以这条迁移可能在 CI 或本地失败。
- 建议改法：SQLite 分支使用 batch mode，或把 CI 数据库改成 PostgreSQL 服务，和生产目标一致。
- 跟 Claude 关系：[重复 C-048] 的实现复核

---

## 维度 3 — 安全、认证与 NFC 防代刷

### [Codex-FC-010] 🔴 App Store 要求的账号删除仍未真正实现

- 位置：`02_design/system_features.md:1063`
- 描述：共用设计要求 iOS 有账号删除入口，后端有 `DELETE /api/v1/accounts/me`，并把 `students.status` 改成 `deleted`。后端设计也在 `03_dev/backend/BACKEND_DESIGN_LOG.md:666` 写了同一件事。但实际 `03_dev/backend/v1/app/routers/accounts.py:78` 只有 `POST /accounts`，没有 `DELETE`。模型约束 `03_dev/backend/v1/app/models.py:84` 也没有允许 `deleted` 状态。iOS 设计在 `03_dev/student_ios/IOS_DESIGN_LOG.md:331` 写了 UI 和 API 调用，但 `AuthAPI.swift:34` 只有 `createAccount`。
- 建议改法：后端先加软删除 endpoint、状态约束和测试。iOS 再接 `AccountsAPI.deleteMyAccount()` 和设置页入口。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-011] 🔴 `.env.example` 的 JWT 示例值能绕过生产检查

- 位置：`03_dev/backend/v1/.env.example:17`
- 描述：示例值是 `change-me-in-production-32-bytes-minimum-please-rotate-on-deploy`。生产检查的禁用列表在 `03_dev/backend/v1/app/config.py:19`，但只禁了短字符串 `change-me-in-production`。因为示例值超过 32 字符，直接复制 `.env.example` 可能通过生产校验。
- 建议改法：把完整示例值加入禁用列表。`.env.example` 可以写成明显不能启动生产的短占位。
- 跟 Claude 关系：[重复 A-001]，当前仍未修完整

### [Codex-FC-012] 🔴 生产 seed 仍保留公开 fallback 凭据，并把秘密写进日志

- 位置：`03_dev/backend/v1/seed.py:307`
- 描述：`REVIEWER_PASSWORD` 默认是公开字符串，`REVIEWER_REGISTRATION_CODE` 默认是 `999999`，`ADMIN_INITIAL_PASSWORD` 默认是 `ChangeMe-2026-05`。更严重的是 `03_dev/backend/v1/seed.py:421` 会把 reviewer 密码写进日志。
- 建议改法：生产 seed 缺少这些环境变量时直接失败。日志只写“已配置 / 未配置”，不要打印秘密本身。
- 跟 Claude 关系：[重复 A-014]，当前仍未修完整

### [Codex-FC-013] 🔴 老师登录锁定路径会因为缺少 `timedelta` 导入而 500

- 位置：`03_dev/backend/v1/app/routers/auth.py:14`
- 描述：文件只导入了 `datetime, timezone`，但 `03_dev/backend/v1/app/routers/auth.py:109` 用了 `timedelta(...)`。老师连续输错密码触发锁定时，会抛 `NameError`，不是返回正常锁定错误。
- 建议改法：补 `timedelta` 导入，并加“连续失败 3 次触发锁定”的测试。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-014] 🔴 学生点呼 check-in endpoint 现在要求老师 token

- 位置：`03_dev/backend/v1/app/routers/rollcall.py:151`
- 描述：`POST /rollcall/sessions/{session_id}/checkins` 是 NFC / iPhone tap 用的签到端点，但函数依赖在 `03_dev/backend/v1/app/routers/rollcall.py:160` 是 `get_current_teacher`。iOS 的 `RollCallAPI.swift:14` 注释说这是学生 BTR tap 入口。学生 token 会被后端拒绝。
- 建议改法：按路径拆分权限。老师手动签到走 teacher endpoint，学生 NFC / tap 签到走 student endpoint，并在后端校验学生身份、设备、时间窗和防重放字段。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-015] 🔴 点呼开始前 5 分钟判断在整点附近会崩溃

- 位置：`03_dev/backend/v1/app/routers/rollcall.py:99`
- 描述：代码用 `replace(minute=session.scheduled_window_start_at.minute - 5)`。如果开始时间是 `21:00` 到 `21:04`，minute 会变成负数，Python 会抛异常。后面再 `max(0, window_minus5.minute)` 已经来不及。
- 建议改法：用 `scheduled_window_start_at - timedelta(minutes=5)`，不要手改 minute 字段。
- 跟 Claude 关系：[重复 A-? / 5-19 已记录的 minute-5 bug]，Codex 复核仍存在

### [Codex-FC-016] 🔴 NFC 路径 B 的 ECDSA + nonce 仍只停在规格层

- 位置：`01_specs/rollcall/RollCall_Spec.md:218`
- 描述：规格要求 iOS / Android 路径 B 取 nonce，用 ECDSA 签名并提交 `{student_id, device_id, ts_local, signature, nonce, idempotency_key}`。但后端当前 `RollCallCheckinIn` 在 `03_dev/backend/v1/app/schemas.py:410` 只有 `card_uid`、`student_id`、`idempotency_key`、`ts_local`、`path_hint`，注释还写 v1.1 起追加 nonce + signature。
- 建议改法：如果 v1.0 真要 iOS + Android + NFC 一次上线，nonce / signature / device_id 必须进 v1.0 schema、数据库和校验逻辑。否则要在规格和上线计划中明确降级。
- 跟 Claude 关系：[重复 A-010]，当前仍未落地

---

## 维度 4 — 跨端字段、API 路径与 Optional 对齐

### [Codex-FC-017] 🟡 规格仍写旧 `POST /api/v1/checkin`，实际后端是 rollcall sessions 路径

- 位置：`01_specs/rollcall/RollCall_Spec.md:192`
- 描述：规格在路径 A 和路径 B 都写 `POST /api/v1/checkin`。`01_specs/API_CONVENTIONS.md:64` 也把它列为不兼容旧写法。实际后端和 iOS 新文件用的是 `/api/v1/rollcall/sessions/{session_id}/checkins`。
- 建议改法：统一规格、API conventions、设备端设计和 iOS / Android 文档。旧 `/api/v1/checkin` 只能保留为历史说明，不能继续作为 v1.0 真值。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-018] 🔴 iOS 点呼 API 文件存在但未进入 Xcode 工程，UI 仍走模拟签到

- 位置：`03_dev/student_ios/v1/TomoshibiApp.xcodeproj/project.pbxproj:252`
- 描述：Endpoints group 只有 `ApplicationsAPI.swift`、`AuthAPI.swift`、`StudyAPI.swift`、`ApplicationsCreateBodies.swift`，没有 `RollCallAPI.swift`。同时 `RollCallAPI.swift` 本身还是未跟踪文件。实际签到 UI 在 `03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift:1430` 调 `simulate()`，`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift:1435` 只更新本地 `app.recordCheckin()`。
- 建议改法：把 `RollCallAPI.swift` 加入 Xcode 工程和 Git。UI 层改成调用真实 API，并处理 401 / 403 / 重复签到 / 超时等错误。
- 跟 Claude 关系：[重复 A-024] 的实现复核；Xcode 工程遗漏是 Codex 独立发现

### [Codex-FC-019] 🟡 iOS 默认 JSONEncoder 可能发出后端不接受的 Date 格式

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/APIClient.swift:67`
- 描述：请求 body 用默认 `JSONEncoder()`。`RollCallAPI.swift:39` 里 `ts_local` 是 `Date?`，后端 `03_dev/backend/v1/app/schemas.py:414` 期待 `datetime`。默认 Swift Date 编码通常不是 ISO 8601 字符串，非 nil 时可能 422。
- 建议改法：统一 `JSONEncoder.dateEncodingStrategy = .iso8601`，或把跨端传输时间字段改成 String 并在客户端格式化。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-020] 🟡 iOS `ApplicationOut` 漏了后端和 Web 都有的 `bus_route_id`

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:43`
- 描述：iOS `ApplicationOut` 没有 `bus_route_id`。后端在 `03_dev/backend/v1/app/schemas.py:187` 有 `bus_route_id: Optional[UUID]`，Web 在 `03_dev/teacher_web/v1/src/api/client.ts:252` 有 `bus_route_id`。
- 建议改法：iOS 模型补字段。若 iOS 暂不显示，也要保留字段以免后续 decode 或业务判断缺数据。
- 跟 Claude 关系：[重复 A-018] 的漏补项

### [Codex-FC-021] 🟡 学生注册房间号长度 iOS 和后端不一致

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:107`
- 描述：iOS 注释写 `room_no 16`，校验在 `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:137` 允许 16 字符。后端 `03_dev/backend/v1/app/schemas.py:558` 最大是 8 字符。用户在 iOS 通过校验后，后端仍会返回 422。
- 建议改法：把 iOS 改成 8，或后端改成 16。选哪一个要以字段字典为准。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-022] 🔴 Android v1 没有真实后端通信层

- 位置：`03_dev/student_android/v1/app/build.gradle.kts:43`
- 描述：依赖只有 Compose、DataStore、serialization 等，没有 Retrofit / OkHttp / Ktor 这类 HTTP 客户端。状态层 `03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/store/AppStore.kt:37` 直接回落到 `MockData.INITIAL_STATE`。这和“iOS + Android + NFC 一次上线”不匹配。
- 建议改法：先补最小网络层和认证 token 存储，再接登录、点呼、申请和公告的真实端点。
- 跟 Claude 关系：[重复 A-? Android mock 未接后端]，Codex 复核仍存在

### [Codex-FC-023] 🔴 点呼机软件层仍是 0%，requirements 安装不到任何依赖

- 位置：`03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md:8`
- 描述：设计 log 明确写硬件采购 0%、`src/` 代码 0%、端到端 0%。`03_dev/rollcall_device/src/main.py:4` 写 placeholder。`03_dev/rollcall_device/requirements.txt:5` 到 `:28` 全是注释，所以 `pip install -r requirements.txt` 实际不会安装 PN532、I2C、GPIO、HTTP 或音频依赖。
- 建议改法：把 v1.0 最小路径拆成可运行主循环：读卡、提交后端、LED / 音频反馈、错误重试。requirements 要落到真实包。
- 跟 Claude 关系：[重复 A-009 / A-027]，Codex 复核仍存在

---

## 维度 5 — Teacher Web 与前端残留

### [Codex-FC-024] 🔴 Teacher Web v1 源码里仍有旧 demo 密码和学生账号数据

- 位置：`03_dev/teacher_web/v1/src/index.html:4262`
- 描述：`src/index.html` 仍加载 vendored React / Babel，并写死 `window.SHARED_PASSWORD = '12345678'`、`window.ACCOUNTS`、学生姓名、生日、电话等模拟数据。`03_dev/teacher_web/v1/src/index.html:4393` 还在页面显示 `demo: tomoshibi / {window.SHARED_PASSWORD}`。
- 建议改法：如果这是归档 demo，应移出 `v1/src`。如果 v1 仍会构建它，应删除明文密码和模拟账号，改走真实后端。
- 跟 Claude 关系：[重复 A-014 / demo scaffold 类]，当前仍存在

### [Codex-FC-025] 🟡 Web 的 `StayLocation` 字段形状和后端不一致

- 位置：`03_dev/teacher_web/v1/src/api/client.ts:220`
- 描述：Web 定义是 `{date, location, contact}`。后端 `03_dev/backend/v1/app/schemas.py:29` 定义是 `{kind, name, address, phone}`。外泊 / 帰国申请的住宿地字段会跨端解释错误。
- 建议改法：以 `FIELD_REGISTRY.md` 和后端 schema 为真值，统一 Web 类型和渲染逻辑。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-026] 🟡 Web 的学習请假响应缺少 `period`

- 位置：`03_dev/teacher_web/v1/src/api/client.ts:299`
- 描述：Web `StudyAbsenceRequestOut` 没有 `period`。后端 `03_dev/backend/v1/app/schemas.py:369` 返回 `period: first_half | second_half | full`。老师界面会失去“前半 / 后半 / 全程”的关键信息。
- 建议改法：Web 类型补 `period`，页面显示也要同步补上。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-027] 🟡 老师公告 client 与后端权限不一致，且没有页面使用

- 位置：`03_dev/teacher_web/v1/src/api/client.ts:162`
- 描述：Web client 增加了公告列表 / 详情 / 创建 / 删除。但后端 `03_dev/backend/v1/app/routers/announcements.py:105` 和 `:193` 的列表 / 详情依赖 `get_current_student`，老师 token 不能用。`rg` 也只发现 client 定义，没有页面调用。
- 建议改法：要么后端补 teacher list/detail endpoint，要么 Web 只保留已能用的 create/delete，并补页面前先写权限契约。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-028] 🟡 老师邀请码权限前后端角色不一致

- 位置：`03_dev/teacher_web/v1/src/pages/Teachers.tsx:26`
- 描述：Web 允许 `寮務部長`、`寮務課長`、`寮監` 发邀请码。后端 `03_dev/backend/v1/app/routers/teachers.py:28` 还允许 `学習担当`。同一个老师可能后端允许、前端不显示按钮。
- 建议改法：把可发邀请码的角色抽成共享文档真值，再同步前后端。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-029] 🟡 Teacher Web 没有 test 脚本

- 位置：`03_dev/teacher_web/v1/package.json:6`
- 描述：scripts 只有 `dev`、`build`、`preview`。本轮 `npm run build` 通过，但 `npm test -- --runInBand` 失败，因为没有 test 脚本。
- 建议改法：至少加一个类型检查 / 单元测试 / smoke test 脚本。没有测试也要在 README 写清“当前只有 build 验证”。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-030] 🟡 Teacher Web v1 README 仍说正式版未开始

- 位置：`03_dev/teacher_web/v1/README.md:3`
- 描述：README 写“老师 Web v1.0 正式版 — 未开始”，但实际已有 TypeScript、Vite、Zustand 前端、API client 和多个页面。
- 建议改法：更新 README 到当前真实状态，列出已接真后端和仍是 demo 的部分。
- 跟 Claude 关系：Claude 漏 — 独立发现

---

## 维度 6 — 文档、钩子与项目叙事

### [Codex-FC-031] 🟡 README / progress / backend README 的测试和迁移数字过期

- 位置：`README.md:44`
- 描述：顶层 README 写后端 “8 router + 37 case pytest 全 pass”。`00_admin/progress_overview.md:173` 也写 37 case 全 pass。实际本轮后端收集到 70 个测试；默认 pytest 收集失败；忽略 warning 后是 60 passed / 2 failed / 8 errors。`03_dev/backend/README.md:10` 仍写 6 个 migration，但实际已有 8 个迁移脚本。
- 建议改法：把这些对外可见状态改成真实测试结果。对教授和 GitHub 读者尤其不要写“全 pass”。
- 跟 Claude 关系：[重复 C-049 / C-050] 的文档残留

### [Codex-FC-032] 🟡 demo scaffold 清单已经落后当前路径

- 位置：`02_design/system_features.md:1468`
- 描述：demo 清理清单列了 iOS `AuthStubs` 的 magic code、后端“没有 demo scaffold”、teacher web `03_dev/teacher_web/v1/demo_server.py` 等。但当前后端 `seed.py` 仍有生产 fallback 凭据，teacher web demo 已迁到 `99_archive`，而 `v1/src/index.html` 仍保留旧 demo payload。memory 文件 `/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/project_demo_scaffolds_to_remove_before_v1.md:9` 也还写旧 `~/dev/TomoshibiiOSApp/`。
- 建议改法：重新跑全仓 `DEMO / mock / fallback / SHARED_PASSWORD` 扫描，按当前路径重建 demo scaffold 清单。
- 跟 Claude 关系：[重复 demo scaffold 审查项]，当前清单仍漂移

### [Codex-FC-033] 🟡 联动脚本遇到带空格路径会拆错文件名

- 位置：`00_admin/hooks/pre-commit:126`
- 描述：pre-commit 用 `check_sync_for_files $STAGED_LIST`，`bin/sync-check.sh:110` 用 `check_sync_for_files $CHANGED_FILES`。这会按空格拆分路径。仓库里已有 39 个带空格的路径，例如 iOS 图标 `tomoshibi_flame 2.png` 和截图文件。
- 建议改法：用 null 分隔或数组安全传参。Git 文件列表建议用 `-z` 版本处理。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-034] 🟡 Claude settings 注册了未跟踪 hook 脚本

- 位置：`.claude/settings.json:31`
- 描述：SessionStart 注册 `bin/check_overview_drift.sh`，PostToolUse 注册 `00_admin/hooks/post-edit-format.sh`。但这两个文件当前都是未跟踪。fresh clone 后 settings 会调用不存在的脚本。
- 建议改法：把脚本提交，或者在 settings 里移除 / 降级这些 hook。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-035] 🟡 `.gitignore` 没覆盖常见秘密和本地状态文件

- 位置：`.gitignore:29`
- 描述：当前忽略 `.env`、`.env.local`、Android `*.jks`、`*.keystore` 和数据库文件。但没有覆盖 `*.pem`、`*.key`、`*.p12`、`*.mobileprovision`、`secrets/`、`.claude/worktrees/`、`.claude/scheduled_tasks.lock`、`*.tsbuildinfo`。
- 建议改法：补充这些规则。已经被 Git 跟踪的本地生成文件要单独从索引移除。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-FC-036] 🟡 cc-project-template 里仍残留大量 DMSD 专用 skill

- 位置：`/Users/kurekoduki/dev/cc-project-template/.claude/skills/memory-write/SKILL.md:3`
- 描述：跨项目扫描发现 `cc-project-template` 的多个 skill 仍写 DMSD、Tomoshibi、itsuki、筑波 AC 等项目专用内容。模板项目如果继续被复用，会把 DMSD 规则污染到新项目。
- 建议改法：模板项目只保留通用规则。DMSD 专用内容移回 DMSD 项目或 personal memory。
- 跟 Claude 关系：[重复 C-037]，当前仍存在

### [Codex-FC-037] 🟡 `03_dev/LATEST.md` 仍指向已归档 demo 路径和明文密码

- 位置：`03_dev/LATEST.md:13`
- 描述：文件写 `cd 03_dev/teacher_web/demo && ./tomoshibi`、`03_dev/teacher_web/demo/Tomoshibi_v3_single.html`，并在 `03_dev/LATEST.md:16` 写管理员密码 `12345678`。当前 demo 已归档到 `99_archive/2026-05-21_teacher_web_demo_archived`。
- 建议改法：改成“历史归档索引”，不要作为“最新位置速查”。明文密码只保留在归档说明里，并标明不能用于正式版。
- 跟 Claude 关系：Claude 漏 — 独立发现

---

## 维度 7 — 依赖漏洞与正向验证

### [Codex-FC-038] 🟢 Web 与后端依赖漏洞检查未发现已知 CVE

- 位置：`05_logs/audit_2026-05-22_codex/pip_audit_backend.json:1`
- 描述：本轮 `pip-audit -r 03_dev/backend/v1/requirements.txt -f json` 检查 48 个 Python 依赖，发现 0 个漏洞。此前 `npm audit --omit=dev --json` 和完整 `npm audit --json` 也显示 teacher web 0 个漏洞。
- 建议改法：把依赖漏洞检查纳入 CI，并定期重跑。当前结论只代表 2026-05-22 的公开漏洞数据库状态。
- 跟 Claude 关系：Codex 独立验证

### [Codex-FC-039] 🟢 Alembic 当前只有一个 head，迁移链没有分叉

- 位置：`03_dev/backend/v1/alembic/versions/b9c0d1e2f3a4_remove_applied_group.py:1`
- 描述：本轮 `alembic heads` 返回单一 head `b9c0d1e2f3a4`，迁移序列线性。问题不在“多 head 冲突”，而在 CI 数据库 URL 和 SQLite 兼容性。
- 建议改法：保留这个检查。以后每次新增 migration 后都跑 `alembic heads` 和一次空库 `upgrade head`。
- 跟 Claude 关系：Codex 独立验证

---

## 本轮命令验证摘要

- 全文件覆盖：`file_coverage.tsv` 登记 1003 个文件，读错误为 0。
- 后端测试：默认 pytest 被 `DeprecationWarning` 挡在收集阶段；忽略 warning 后 60 passed / 2 failed / 8 errors。
- Teacher Web：`npm run build` 通过；`npm test` 不存在。
- Android：`./gradlew test --dry-run` 因未配置 Android SDK 路径失败，属于本机环境 / 隐藏依赖问题。
- 依赖漏洞：后端 pip-audit 0 漏洞；teacher web npm audit 0 漏洞。

## 最关键 3 条

1. 后端测试现在不是全 pass，而是默认收集失败，忽略 warning 后仍有 10 个失败 / 错误。  
2. 账号删除、学生点呼权限、NFC 防重放这三条都直接影响 v1.0 上线和 App Store 审查。  
3. 多个 5-21 修复文件仍未跟踪，fresh clone 会丢掉 CI、测试、迁移和系统 bug 总表。  
