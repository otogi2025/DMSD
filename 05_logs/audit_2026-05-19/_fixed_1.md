# Fix-Bot 1 修复报告 — 03_dev/ 代码层

生成于：2026-05-21（itsuki 拍板「全都修好派 subagent 上」）

## 已修

### A 子代理范围（backend / iOS / Android / teacher_web / 点呼机 代码层）

| ID | 严重 | 文件 | 改了什么 |
|---|---|---|---|
| A-006 | 🟡 | `03_dev/backend/v1/app/routers/auth.py` | 教师 login 失败 counter 递增 + 3 次锁 30 分（用现有 teacher.failed_count / teacher.locked_until 字段） |
| A-007 | 🟡 | `03_dev/backend/v1/app/config.py` | `_validate_production_settings()` 加 CORS production 不允许 `*` 通配符 fail-fast |
| A-008 | 🟡 | `03_dev/backend/v1/app/config.py` | `_validate_production_settings()` 加 SQLite production 禁止 fail-fast |
| A-009 | 🟡 | `03_dev/rollcall_device/src/main.py` | docstring 顶部加「实装进度: 0% — placeholder」+ 链接 ROLLCALL_DEVICE_DESIGN_LOG / hardware_design |
| A-011 | 🟡 | `03_dev/backend/v1/app/models.py` + `routers/rollcall.py` + `alembic/versions/a8b9c0d1e2f3_add_rce_idempotency_unique.py` | RollCallEvent 加 UniqueConstraint(session_id, idempotency_key) + router 改先查 key 命中（新 alembic migration） |
| A-012 | 🟡 | `03_dev/backend/v1/app/schemas.py` + `routers/teachers.py` | TeacherRegisterIn 加 confirmation_email 字段 + register 校验跟 invitation.target_email lowercase 严格对比 |
| A-013 | 🟡 | `03_dev/backend/v1/app/routers/applications.py` | `/pending-for-me` 移到 `/{application_id}` 之前（FastAPI 路由顺序 bug） |
| A-014 | 🟢 | `03_dev/backend/v1/seed.py` | reviewer 密码 + 注册码改从 env 读（REVIEWER_PASSWORD / REVIEWER_REGISTRATION_CODE），fallback 时 log.warning |
| A-017 | 🟡 | `03_dev/teacher_web/v1/src/api/client.ts` | AppStatus union 加 `"returned"` |
| A-018 | 🟡 | `03_dev/teacher_web/v1/src/api/client.ts` | Application 接口补齐 reason / stay_locations / meals_skip / flight_* / withdrawn_at / bus_route_id 全字段 + 加 StayLocation / MealSkip 类型 |
| A-019 | 🟡 | `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift` | StudentAccountCreateBody 加 `validate()` 方法镜像 backend max length（name/name_kana/email/phone/room_no/password） |
| A-020 | 🟡 | `03_dev/backend/v1/app/schemas.py` + `routers/rollcall.py` | RollCallCheckinIn 加 `path_hint: Optional[Literal["A","B","manual"]]` + router 校验 path_hint=A 必须有 card_uid / B 必须有 idempotency_key |
| A-023 | 🟡 | `03_dev/backend/BACKEND_DESIGN_LOG.md` | 头部加「字段隐私分级」附注（is_demo / password_hash / failed_count backend-only） |
| A-024 | 🟡 | `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/RollCallAPI.swift` | 新建 RollCallAPI enum + RollCallCheckinBody + RollCallEventOut 跟 backend 对齐（path_hint 已含） |
| A-026 | 🟡 | `03_dev/teacher_web/v1/src/api/client.ts` | 加 AnnouncementBrief / Detail / Reply / CreateIn 类型 + listAnnouncements / getAnnouncement / createAnnouncement / deleteAnnouncement 4 个 API client（UI 发布页 v1.1 实装） |
| A-027 | 🔴 | `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` | 头部加「实装进度速查表」明示设计 ✅ 100% / src ⏳ 0% / 硬件采购 ⏳ 0% / 端到端 ⏳ 0% |
| A-029 | 🟡 | 5 端 *_DESIGN_LOG.md | iOS / Android / Web / Backend / ROLLCALL_DEVICE 都加「实装进度速查表」section |
| A-030 | 🟡 | iOS HomeStubs.swift + AppStore.swift / Android AppStore.kt | iOS DemoCardCycleGesture 改成 no-op（保留 modifier 调用点）+ cycleDemoRollState() 函数本体删；Android cycleDemoRollState() 删（无调用方） |
| A-032 | 🟡 | `03_dev/teacher_web/demo/` → `99_archive/2026-05-21_teacher_web_demo_archived/demo/` | 整目录 git mv 归档 + 加 README.md 说明背景 / 归档理由 / 复活方法 |
| A-033 | 🔴 | iOS `HomeStubs.swift` + `AppStore.swift` | cycleDemoRollState() 完整删；DemoCardCycleGesture 改成 no-op（A-030 一并修） |
| A-034 | 🔴 | Android `AppStore.kt` | cycleDemoRollState() 整段删（A-030 一并修） |
| A-036 | 🟡 | iOS `AppStore.swift` | 加 `isAuthenticated: Bool { authToken != nil }` gate；后续 view 用此 gate 决定回退 SEED.user 还是显示「— 」（A-037 已在 StayList 用） |
| A-037 | 🟡 | iOS `Features/StayList/StayListStubs.swift` | load() 切回 `try await ApplicationsAPI.listMine()` + `.toStayApplication()`；未登录态用 StayListMock 兜底（isAuthenticated gate） |
| A-038 | 🟡 | iOS `Foundation/AppState/AppStore.swift` | init() 删 `seedDemoAnnouncements()` 调用 + 整段函数体（141 行）删 |

### B 子代理范围

| ID | 严重 | 文件 | 改了什么 |
|---|---|---|---|
| B-035 | 🟡 | `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` §2 | 改成「单一真值 = hardware_design.md §2.4.1」+ GPIO 表对齐 hardware（加 LED 白 = GPIO 23） |

### C 子代理范围

| ID | 严重 | 文件 | 改了什么 |
|---|---|---|---|
| C-012 | 🔴 | iOS `IOS_DESIGN_LOG.md:583` + Android `ANDROID_DESIGN_LOG.md:6` & §9 | 清独立 repo 引用（5-06 退役）；iOS line 583 改「单 repo 在 03_dev/student_ios/v1/」；Android 顶部独立 repo 标注换成「2026-05-06 退役独立 repo」；§9「跨 repo 同步」整段改成「单 repo 同步」+ 说明原规则已废 |
| C-039 | 🟡 | `03_dev/backend/v1/requirements.txt` | python-jose 升 `>=3.4.0`（修 CVE-2024-33663 algorithm confusion + CVE-2024-33664 JWT bomb） |
| C-040 | 🟡 | grep 验证 | backend 代码 + seed.py 全 grep — passlib 引用 0 处，无 runtime 错风险（注释正确） |
| C-042 | 🟡 | `03_dev/backend/demo/requirements.txt` | 6 个依赖 `==` → `>=` 跟 v1/ 风格统一 |
| C-044 | 🟡 | `03_dev/student_ios/IOS_DESIGN_LOG.md` 进度速查表 | 加注「依赖管理 ✅ N/A」— iOS xcodeproj 内 XCRemoteSwiftPackageReference grep 为空，无外部 SPM 依赖，不需要 Package.resolved |
| C-048 | 🔴 | `.github/workflows/test.yml`（新建） | GitHub Actions 跑 pytest — Python 3.12 + alembic upgrade head sanity check + pytest tests/ -v；触发条件 push/PR 改动 backend/v1/** |
| C-049 | 🟡 | `03_dev/backend/v1/pyproject.toml`（新建） | `[tool.pytest.ini_options]` 配 testpaths / python_files / asyncio_mode auto / DeprecationWarning 升 error（pydantic / fastapi 忽略） |
| C-050 | 🟡 | `03_dev/backend/v1/tests/test_rollcall.py` + `test_study.py` + `test_applications.py`（新建 3 文件，共约 470 行） | rollcall：checkin 创建 / idempotency / path_hint A/B 校验 / board demo 过滤 / session lifecycle；study：today/attendees / absence-request 创建+承认+一览 / checkin / cancel-today 权限；applications：create kisei / list mine / **pending-for-me 路由顺序 regression test**（关键 — 防 A-013 复发）/ get by id / audit log |

## 待 itsuki 拍板（unfix）

无 — 范围内全跑完。

## 跳过（不在范围）

主会话保留：
- A-001 / A-002 / A-003 / A-004 / A-005（backend auth 设计层 — JWT secret 默认值 / HS256→RS256 / NFC 签名 / 学生 login / 学生失败锁）
- A-010 / A-028（NFC ECDSA 实装 — v1.0 决策性，需要 itsuki 拍板 v1.0 是「完整实装」or「降级 v1.1」）
- A-035（iOS Auth magic 000000 — itsuki 拍板才能改注册 flow）
- A-039（teacher_web v1/src/index.html 7700 行旧 demo — 需要先备份 + 验证 vite 配置）

Bot 2 范围：01_specs/ + 02_design/ + system_features.md 全跳过（部分进度速查表用 design log 单端层，没动 system_features.md）。

Bot 3 范围：00_admin/ + README.md + CHANGELOG.md + memory/ + ~/dev/SC26 + ~/dev/cc-project-template + ~/dev/tango 全跳过。

主会话刚修过的具体行未动。

## 总计

- 已修：33 条（A 维度 23 / B 维度 1 / C 维度 9）
- 待拍板：0 条
- 跳过：6 条（主会话保留）+ 不在范围的全部其他

涉及文件数：22 个 + 5 个新建（A-011 alembic migration + A-024 RollCallAPI.swift + C-048 .github/workflows/test.yml + C-049 pyproject.toml + 99_archive README + 3 个 tests/test_*.py + A-032 teacher_web/demo/ 整目录归档）

### 关键问题 3 条

1. **A-027 / A-029 实装进度速查表落地** — 5 端 *_DESIGN_LOG 全加进度速查表，让招生官 / agent / itsuki 自己读时立刻看到「设计完了 vs 代码完了」分层真值，防再被 BACKEND_DESIGN_LOG 1134 行设计误导成「都做完了」。
2. **A-011 idempotency 完整修** — model UniqueConstraint + alembic migration + router 先查 key 命中三层都改齐，防 client 用同 key 重试时产生 race condition。还配套写 regression test (`test_rollcall.py::TestCheckin::test_idempotency_same_key_returns_existing`)。
3. **A-013 路由顺序 + regression test** — `/pending-for-me` 移到 `/{application_id}` 之前修了主 bug；同时在 `test_applications.py::TestPendingForMe::test_pending_for_me_route_resolves_correctly` 加显式 regression test，防未来重排路由时 bug 复发。

### 项目结构 hook 提醒未处理

所有「project-overview 漂移检测」hook 提醒全部跳过 — `.claude/skills/project-overview/SKILL.md` 是 Bot 3 范围（按 itsuki 拍板「Bot 1 / Bot 2 / Bot 3 不跨范围」执行）。Bot 3 完整跑完会一次性补这些路径引用。

中文铁律 hook 提醒：日语注释告警全部是已有代码（不是本次新加的），跳过修正以避免越权改原 code。
