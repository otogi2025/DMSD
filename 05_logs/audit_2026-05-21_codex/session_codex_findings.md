# Codex Findings — 2026-05-21 独立第二轮审查

## 总览

- 🔴 阻塞上线：11 条
- 🟡 该修：14 条
- 🟢 优化 / 信息：1 条
- 跟 Claude 重复：14 条（标 [重复 A-001 等]）
- Claude 漏的 / Codex 独立发现：12 条

本轮是独立第二轮审查。  
我只审查并记录问题，没有修改业务代码。  

说明：API 是“应用程序接口”，endpoint 是“端点”，CI 是“持续集成”，JWT 是“JSON Web Token 登录令牌”，Alembic 是“数据库迁移工具”，SQLite 是“轻量数据库”，NFC 是“近场通信”，ECDSA 是“椭圆曲线签名”，nonce 是“一次性随机数”。

---

## 维度 1 — project-overview 清单漂移

### [Codex-001] 🟡 project-overview 体量表和实际文件数已经再次漂移

- 位置：`.claude/skills/project-overview/SKILL.md:29`
- 描述：`§0.1` 仍写总文件数 957，但本轮运行 `bin/check_overview_drift.sh` 得到“写 957 / committed 957 + 未 commit 21 = 实际 978”。顶级目录也漂移：`03_dev/` 写 546、实际 395；`99_archive/` 写 273、实际 432；`.github/` 实际 1 但表里没有。这个文件是 Claude 的项目总览入口，数字漂移会让后续审查误判项目规模和文件归属。
- 建议改法：先决定是否把当前未提交文件纳入项目事实；再更新 `§0.1` 顶级目录表、`§1` 分组表和对应小节。建议把 `bin/check_overview_drift.sh` 输出贴进修复记录，避免只手改数字。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-002] 🟡 project-overview 的后端测试和迁移清单没有跟上 5-21 新文件

- 位置：`.claude/skills/project-overview/SKILL.md:345`
- 描述：后端测试小节仍写 5 个测试文件、42 个测试用例，但实际 `03_dev/backend/v1/tests/` 已有 9 个文件。Alembic 数据库迁移工具小节从 `.claude/skills/project-overview/SKILL.md:358` 开始，仍列 6 个版本脚本，漏了 `a8b9c0d1e2f3_add_rce_idempotency_unique.py`。`.github/workflows/test.yml` 也已出现，但 `§0.1` 没有 `.github/` 目录。
- 建议改法：按实际文件重新生成后端测试清单、迁移清单和 CI 持续集成清单。测试用例数量不要手估，建议用 `pytest --collect-only` 或同等命令得到。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-003] 🟡 联动规则数量在三个地方互相不一致

- 位置：`.claude/skills/project-overview/SKILL.md:160`
- 描述：project-overview 写 `sync-rules.sh` 有 19 条规则；`.claude/skills/file-linkage/SKILL.md:3` 的描述仍写 17 条；同文件 `.claude/skills/file-linkage/SKILL.md:31` 又写 18 条。实际 `00_admin/hooks/lib/sync-rules.sh` 里 `add_rule` 数量是 18。联动矩阵是“改 A 必查 B”的源头，数量不一致会让 itsuki 不知道哪一份是真值。
- 建议改法：把真值定为 `00_admin/hooks/lib/sync-rules.sh` 的实际规则数。同步改 project-overview、file-linkage frontmatter、file-linkage 正文和 hooks README。
- 跟 Claude 关系：[重复 C-017]，但当前仍未完全收敛

### [Codex-004] 🟡 系统 bug 专栏没有反映 5-21 已生成的修复文件

- 位置：`00_admin/系统bug专栏.md:335`
- 描述：C-048 仍写 `.github/workflows/` 不存在并标 ⏳，但实际已有 `.github/workflows/test.yml`。C-049 在 `00_admin/系统bug专栏.md:632` 仍写无 pytest 配置，但实际 `03_dev/backend/v1/pyproject.toml` 已有 pytest 配置。C-050 在 `00_admin/系统bug专栏.md:637` 仍写没有 rollcall / study / applications 测试，但实际已有相关测试文件。这个专栏是 131 条问题的总看板，状态漂移会让后续修复重复劳动。
- 建议改法：逐条复核 5-21 产生的新文件，把“已实装但未验证”的条目标成“待验证”，不要继续标“未修”。同时保留本轮仍发现的缺口，例如迁移脚本在 SQLite 下可能失败。
- 跟 Claude 关系：Claude 漏 — 独立发现

---

## 维度 2 — 配置、安全和种子数据

### [Codex-005] 🔴 `.env.example` 里的 JWT 示例值能绕过生产启动检查

- 位置：`03_dev/backend/v1/.env.example:17`
- 描述：示例值是 `change-me-in-production-32-bytes-minimum-please-rotate-on-deploy`。`03_dev/backend/v1/app/config.py:18` 的禁用列表没有包含这个完整字符串，而它又超过 32 字节，所以如果部署者直接复制 `.env.example`，`APP_ENV=prod` 下的检查可能通过。结果是生产环境使用公开写在仓库里的登录令牌密钥。
- 建议改法：把 `.env.example` 里的 JWT 示例改成明显不可用于生产的短占位，例如 `CHANGE_ME`；同时把当前完整示例值加入 `_FORBIDDEN_JWT_SECRETS`。生产环境应要求部署者手动设置随机强密钥。
- 跟 Claude 关系：[重复 A-001]，但 5-21 修复仍不完整

### [Codex-006] 🔴 生产 seed 仍保留公开默认管理员密码和审核员注册码

- 位置：`03_dev/backend/v1/seed.py:307`
- 描述：生产 seed 里 `PROD_REVIEWER_PASSWORD` 默认值仍是公开字符串，`PROD_REVIEWER_REGISTRATION_CODE` 默认值仍是 `999999`，`ADMIN_INITIAL_PASSWORD` 在 `03_dev/backend/v1/seed.py:333` 还有默认值。更严重的是 `03_dev/backend/v1/seed.py:421` 会把审核员密码和注册码写进日志。只要生产 seed 被误跑，就会产生公开凭据。
- 建议改法：生产模式缺少 `ADMIN_INITIAL_PASSWORD`、`REVIEWER_PASSWORD`、`REVIEWER_REGISTRATION_CODE` 时应直接失败。日志里不要输出任何密码或注册码，只输出“是否已配置”。
- 跟 Claude 关系：[重复 A-014]，但当前风险仍存在

### [Codex-007] 🔴 老师登录锁定路径会因为缺少 `timedelta` 导入而崩溃

- 位置：`03_dev/backend/v1/app/routers/auth.py:14`
- 描述：文件只从 `datetime` 导入了 `datetime, timezone`，但失败登录路径在 `03_dev/backend/v1/app/routers/auth.py:109` 使用 `timedelta(minutes=LOCK_MINUTES)`。老师连续输错密码触发锁定时，会从业务错误变成 Python 的 `NameError` 运行时报错。
- 建议改法：补 `from datetime import datetime, timedelta, timezone`，并加一个测试：同一老师连续失败 3 次后返回锁定错误，而不是 500。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-008] 🟡 `.gitignore` 没覆盖若干敏感文件和本地生成文件

- 位置：`.gitignore:29`
- 描述：当前只忽略 `.env`、`.env.local`、`.env.*.local`，以及 Android 的 `*.jks`、`*.keystore`。还没有覆盖常见密钥和本地状态：`*.pem`、`*.key`、`*.p12`、`*.mobileprovision`、`secrets/`、`.claude/worktrees/`、`.claude/scheduled_tasks.lock`、`*.tsbuildinfo`。实际工作区里已经出现 `.claude/worktrees/` 和 `.claude/scheduled_tasks.lock`，teacher web 的 `tsconfig.tsbuildinfo` 也被纳入了项目清单。
- 建议改法：补充这些忽略规则。对已经被 Git 追踪的缓存文件，需要单独从索引移除；这个动作应在 fix 阶段做，不在 audit 阶段做。
- 跟 Claude 关系：Claude 漏 — 独立发现

---

## 维度 3 — 后端端点、迁移和测试

### [Codex-009] 🔴 点呼开始时间在 00-04 分时会触发 `ValueError`

- 位置：`03_dev/backend/v1/app/routers/rollcall.py:99`
- 描述：代码用 `scheduled_window_start_at.minute - 5` 直接改 `minute`。如果点呼开始时间是 08:00、08:01、08:02、08:03 或 08:04，`replace(minute=-5)` 这类值会触发 `ValueError: minute must be in 0..59`。这会让合法的早晨整点点呼无法签到。
- 建议改法：用 `timedelta(minutes=5)` 做时间减法，例如 `scheduled_window_start_at - timedelta(minutes=5)`。再加一个开始时间为整点的测试。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-010] 🔴 学生点呼签到端点实际要求老师 token

- 位置：`03_dev/backend/v1/app/routers/rollcall.py:156`
- 描述：`POST /api/v1/rollcall/sessions/{session_id}/checkins` 的依赖是 `Depends(get_current_teacher)`。`03_dev/backend/v1/app/deps.py:53` 的 `get_current_teacher` 会拒绝学生 JWT 登录令牌。可是 iOS 新增的 `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/RollCallAPI.swift:14` 明确把它当成学生点呼签到端点。结果是学生 App 调用会得到 403。
- 建议改法：拆成学生签到端点和设备签到端点，或让同一端点按 token 类型分支校验。不要让学生端依赖老师权限。
- 跟 Claude 关系：[重复 A-015 / A-024 / A-010]，但本轮定位到具体权限不匹配

### [Codex-011] 🔴 iOS 仍然只做本地模拟点呼，没有真正调用后端签到

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift:1430`
- 描述：`simulate()` 仍然只是等待后调用 `app.recordCheckin()`。`03_dev/student_ios/v1/TomoshibiApp/Foundation/AppStore.swift:321` 也写着当前是 mock，后续才接后端。虽然新增了 `RollCallAPI.swift`，但代码搜索没有发现任何 View 调用它。也就是说点呼主路径仍然没有真实联网。
- 建议改法：把 NFC 近场通信触发后的签到流程接到 `RollCallAPI.checkin`。失败时展示后端错误码，成功时用后端返回状态更新 UI，而不是本地直接写“已点呼”。
- 跟 Claude 关系：[重复 A-015 / A-024]，当前只是部分补文件，未接入流程

### [Codex-012] 🟡 新增的 iOS RollCallAPI 没进当前 Xcode 工程文件

- 位置：`03_dev/student_ios/v1/TomoshibiApp.xcodeproj/project.pbxproj:252`
- 描述：当前 Xcode 工程的 `Endpoints` group 只列了 `ApplicationsAPI.swift`、`AuthAPI.swift`、`StudyAPI.swift` 和 `ApplicationsCreateBodies.swift`，没有 `RollCallAPI.swift`。虽然 `project.yml` 可能通过 XcodeGen 重新生成工程，但如果直接打开现有 `.xcodeproj`，新增文件不会编译进 App。
- 建议改法：要么运行 XcodeGen 并提交更新后的 `.xcodeproj`，要么明确项目规范要求只用 `project.yml` 生成工程。修复后需要确认 `RollCallAPI.swift` 出现在 build phase 里。
- 跟 Claude 关系：[重复 A-015]，但本轮定位到工程文件未同步

### [Codex-013] 🟡 `ts_local` 的日期编码在 iOS 和后端之间不一致

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/APIClient.swift:67`
- 描述：`APIClient` 用默认 `JSONEncoder()` 编码请求体。Swift 的默认 `Date` 编码是数字时间，不是 ISO 8601 字符串。`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/RollCallAPI.swift:39` 的 `ts_local` 是 `Date?`，后端 `03_dev/backend/v1/app/schemas.py:414` 接收 `datetime`。如果未来 iOS 传非空 `ts_local`，后端可能解析失败或语义不一致。
- 建议改法：请求编码器也设置 `.iso8601`，或者这个字段改成后端统一生成，不让客户端传。选择后同步 iOS 模型、后端 schema 和 RollCall 规格。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-014] 🔴 CI 里的 Alembic 迁移数据库变量不会被 `env.py` 使用

- 位置：`03_dev/backend/v1/alembic/env.py:15`
- 描述：CI 持续集成文件 `.github/workflows/test.yml:47` 设置了 `DATABASE_URL=sqlite:///./ci_test.db`，但 Alembic 的 `env.py` 没读取这个环境变量。`03_dev/backend/v1/alembic.ini:89` 仍是 `sqlite:///./tomoshibi_dev.db`。这会让 CI 自以为在测临时库，实际可能操作开发库路径。
- 建议改法：在 `env.py` 中读取 `DATABASE_URL`，存在时覆盖 `sqlalchemy.url`。CI 里再检查迁移生成的数据库文件名，确认不是 `tomoshibi_dev.db`。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-015] 🔴 新的唯一约束迁移在 SQLite CI 下可能失败

- 位置：`03_dev/backend/v1/alembic/versions/a8b9c0d1e2f3_add_rce_idempotency_unique.py:25`
- 描述：迁移脚本直接调用 `op.create_unique_constraint(...)`。SQLite 不支持直接 `ALTER TABLE ADD CONSTRAINT`。CI 文件 `.github/workflows/test.yml:47` 使用 SQLite 跑 `alembic upgrade head`，所以这个迁移很可能在 CI 中失败。模型里的 `03_dev/backend/v1/app/models.py:636` 虽然有唯一约束，但 `create_all` 测试通过不代表迁移通过。
- 建议改法：对 SQLite 使用 `op.batch_alter_table("rollcall_events")`，或在迁移里按数据库方言分支处理。补一个只跑迁移、不调用 `create_all` 的 CI 检查。
- 跟 Claude 关系：[重复 A-011]，但 5-21 新迁移仍有缺口

### [Codex-016] 🔴 账号删除规格存在，但后端没有实现 `DELETE /accounts/me`

- 位置：`03_dev/backend/BACKEND_DESIGN_LOG.md:666`
- 描述：后端设计日志明确写了 Apple App Store Review Guideline 5.1.1(v) 需要 `DELETE /api/v1/accounts/me`，并在 `03_dev/backend/BACKEND_DESIGN_LOG.md:695` 指向 `app/routers/accounts.py:delete_my_account`。实际 `03_dev/backend/v1/app/routers/accounts.py:78` 只有 `POST /accounts` 创建账号，没有删除端点。这个缺口会影响 iOS 上架审查。
- 建议改法：实现 `DELETE /api/v1/accounts/me`，做软删除、写审计日志，并补 iOS 调用和后端测试。
- 跟 Claude 关系：Claude 漏 — 独立发现

---

## 维度 4 — 跨端字段和 Optional 一致性

### [Codex-017] 🟡 Web 的 `StayLocation` 字段仍和后端 schema 不一致

- 位置：`03_dev/teacher_web/v1/src/api/client.ts:220`
- 描述：Web 端类型写的是 `{ date, location, contact }`。后端 `03_dev/backend/v1/app/schemas.py:29` 的 `StayLocation` 是 `{ kind, name, address?, phone? }`。这会让外泊申请详情或提交数据在 Web 和后端之间对不上。
- 建议改法：以 `schemas.py` 为准同步 Web 类型。然后检查申请创建、详情展示和测试 fixture 里是否还残留旧字段名。
- 跟 Claude 关系：[重复 A-018]，当前字段仍未对齐

### [Codex-018] 🟡 iOS `ApplicationOut` 少了后端和 Web 已有的 `bus_route_id`

- 位置：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:43`
- 描述：后端 `03_dev/backend/v1/app/schemas.py:187` 的 `ApplicationOut` 有 `bus_route_id: Optional[int]`，Web `03_dev/teacher_web/v1/src/api/client.ts:252` 也有 `bus_route_id?: number | null`。iOS 的 `ApplicationOut` 没有这个字段。Optional 是“可有可无字段”，但跨端至少要知道它存在，否则 iOS 收到相关申请详情时会丢信息。
- 建议改法：在 iOS `ApplicationOut` 增加 `bus_route_id: Int?`，并确认所有申请类型的字段矩阵。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-019] 🟡 老师 Web 的公告 API 只补了 client，没有补页面和权限路径

- 位置：`03_dev/teacher_web/v1/src/api/client.ts:162`
- 描述：Web client 已有 `announcements.list/detail/create/delete`，但 `src/pages/` 没有公告管理页面。后端 `03_dev/backend/v1/app/routers/announcements.py:105` 的列表端点依赖学生身份，`03_dev/backend/v1/app/routers/announcements.py:193` 的详情端点也依赖学生身份；老师 token 只能走创建和删除。老师 Web 想管理公告时，连列表都取不到。
- 建议改法：补老师侧公告列表 / 详情端点，或调整现有端点权限。再补 Web 页面和路由，让老师能看到自己创建的公告。
- 跟 Claude 关系：[重复 A-026]，当前只是部分补 client

### [Codex-020] 🔴 Android 端仍没有真实后端通信层

- 位置：`03_dev/student_android/v1/app/build.gradle.kts:43`
- 描述：Android 依赖里有 Compose、DataStore 和 serialization，但没有 Retrofit、OkHttp、Ktor 等 HTTP 网络客户端。代码搜索也没有发现真实 API 调用层。v1.0 要求 iOS + Android + NFC 卡一次上线，Android 现在还停在本地状态层。
- 建议改法：先补最小 API client：登录、点呼签到、申请列表。再把现有 Compose 页面从本地状态切到真实 repository。
- 跟 Claude 关系：[重复 A-016]

---

## 维度 5 — 老师 Web 和公开仓库暴露面

### [Codex-021] 🔴 旧老师 Web demo 里的共享密码和账号仍留在 public repo

- 位置：`03_dev/teacher_web/v1/src/index.html:4262`
- 描述：旧 demo 文件仍包含 `window.SHARED_PASSWORD = '12345678'`，并从 `03_dev/teacher_web/v1/src/index.html:4297` 开始列出账号数据，在 `03_dev/teacher_web/v1/src/index.html:4393` 还会显示密码。虽然当前 Vite 入口是 `03_dev/teacher_web/v1/index.html`，但这个旧文件仍在源码目录，public GitHub 仓库会直接暴露这些 demo 凭据。
- 建议改法：把旧 demo 文件移到 `99_archive/`，或删除敏感账号和密码后再保留。`src/_legacy/` 里的同类 demo 密码也要一起处理。
- 跟 Claude 关系：[重复 A-039 / A-032]

### [Codex-022] 🟡 老师邀请权限前后端角色表不一致

- 位置：`03_dev/teacher_web/v1/src/pages/Teachers.tsx:26`
- 描述：Web 端 `canInvite` 只允许 `寮務部長`、`寮務課長`、`寮監`。后端 `03_dev/backend/v1/app/routers/teachers.py:27` 的 `INVITE_ALLOWED_ROLES` 还允许 `学習担当`。如果老师是 `学習担当`，后端允许邀请，但前端不会显示入口。
- 建议改法：确认业务规则。如果 `学習担当` 应该能邀请，就同步 Web；如果不应该，就收紧后端。
- 跟 Claude 关系：Claude 漏 — 独立发现

### [Codex-023] 🟡 旧 API 命名文档仍保留 `/api/v1/checkin`，和实际后端路径不一致

- 位置：`01_specs/API_CONVENTIONS.md:64`
- 描述：API 命名文档仍把 `/api/v1/checkin` 作为 RollCall 例子。主规格 `01_specs/rollcall/RollCall_Spec.md:192` 和 `01_specs/rollcall/RollCall_Spec.md:220` 也写 `POST /api/v1/checkin`。实际后端是 `POST /api/v1/rollcall/sessions/{session_id}/checkins`。对零基础学习者来说，这会直接导致“不知道该调哪个 URL”。
- 建议改法：拍板一个唯一 v1 路径。然后同步 API_CONVENTIONS、RollCall_Spec、iOS/Android/Web client 和后端 router。
- 跟 Claude 关系：[重复 A-010 / B-027]

---

## 维度 6 — hooks、跨项目残留和依赖审计

### [Codex-024] 🟡 hooks README 和实际 `.claude/settings.json` 注册不一致

- 位置：`00_admin/hooks/README.md:19`
- 描述：README 仍写同一个 matcher 下挂 5 条 PostToolUse hook，但 `.claude/settings.json:38` 到 `.claude/settings.json:84` 实际是 7 条。README 在 `00_admin/hooks/README.md:69` 又写 PreToolUse 只有 1 条 H，但 `.claude/settings.json:15` 还有 graphify 搜索提醒 hook。这个文档是新会话理解 hook 行为的入口，少写会让人误判自动检查范围。
- 建议改法：按 `.claude/settings.json` 重新列出 PreToolUse、PostToolUse、SessionStart 三类 hook。把“5 条”改成“7 条”，并补 graphify hook 的说明。
- 跟 Claude 关系：[重复 B-022 / C-018]，但当前 README 仍有新增漂移

### [Codex-025] 🟡 cc-project-template 仍残留大量 DMSD 专属 skill 内容

- 位置：`/Users/kurekoduki/dev/cc-project-template/.claude/skills/memory-write/SKILL.md:3`
- 描述：跨项目模板里仍有 “DMSD memory 写入 SOP”。同目录的 `new-feature/SKILL.md:3`、`session-wrap/SKILL.md:3`、`version-bump/SKILL.md:3`、`project-overview/SKILL.md:1` 也仍是 DMSD/Tomoshibi 专属内容。模板项目如果继续带这些文件，会污染新项目的记忆、功能规划和版本流程。
- 建议改法：把 cc-project-template 里的 DMSD 专属 skill 改成通用模板，或移到 DMSD 仓库专用目录。保留的示例要明确标成 example，不能作为默认规则生效。
- 跟 Claude 关系：[重复 C-037]

### [Codex-026] 🟢 Python 依赖漏洞扫描没有形成可复现检查

- 位置：`03_dev/backend/v1/requirements.txt:10`
- 描述：requirements 注释写 python-jose 已按 C-039 提升到 `>=3.4.0`。本轮本地能跑 `npm audit` 检查老师 Web，结果是 0 个漏洞；但后端环境没有 `pip-audit` 这个 Python 依赖漏洞扫描工具，所以无法用同一套命令复现 Python 依赖 CVE 已清零。CVE 是“公开漏洞编号”。
- 建议改法：在后端开发依赖或 CI 中加入 `pip-audit`，并固定一条命令，例如 `python -m pip_audit -r requirements.txt`。这样以后升级依赖时可以自动检查。
- 跟 Claude 关系：Claude 漏 — 独立发现
