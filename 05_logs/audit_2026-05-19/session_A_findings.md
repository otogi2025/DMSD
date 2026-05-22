# 会话 A findings — 第一档必审（维度 1-5）

生成于：2026-05-20 ~01:03（子代理 A）
项目快照：HEAD = 8e35338，backend = `03_dev/backend/v1/`（注意：不是 `app/`），iOS = `student_ios/v1/TomoshibiApp/`，Android = `student_android/v1/app/`，点呼机 src = `03_dev/rollcall_device/src/`

## 维度 5：NFC 安全（最关键 — 先审）

### [A-001] 🔴 JWT 密钥默认值是 `change-me-in-production` — 没有强制 fail-fast

- **文件**：`03_dev/backend/v1/app/config.py:29`
- **描述**：`jwt_secret: str = "change-me-in-production"`。如果 `.env` 没设 / 设错变量名，整个 JWT 签名链就用这个公开的字符串作密钥，任何人能伪造任意学生 / 教师 token。生产部署如果 ops 漏配 `.env` → 鉴权全废。
- **建议改法**：在 `Settings.__init__` 或 `get_settings()` 里加一段：`if app_env == "production" and jwt_secret in {"change-me-in-production", "", None}: raise RuntimeError(...)`。同时把 `jwt_secret` 改成 `Field(...)` 必填，没默认值，dev 环境靠 `.env` 自动注入。
- **跨会话**：N/A

### [A-002] 🔴 JWT 用 HS256 对称密钥 — 点呼机 / iOS / Android 没法独立验签

- **文件**：`03_dev/backend/v1/app/config.py:30` (`jwt_algorithm: str = "HS256"`) + `security.py:69-72`
- **描述**：HS256 是对称加密，签名密钥 = 验证密钥。点呼机（Pi）要本地验 student token 才能确认 NFC checkin 合法，但 HS256 意味着点呼机也要持有 `jwt_secret` 副本；点呼机硬件被偷 / SD 卡被复制 → 攻击者拿到 secret → 能伪造任意 token。spec / BACKEND_DESIGN_LOG 里 ECDSA 签名是给 NFC 卡 payload 的，跟 JWT 是两套，但 JWT 这层选 HS256 仍然是离线设备场景的高风险。
- **建议改法**：评估迁移到 RS256 / ES256（非对称）— backend 私钥签发，所有 client（iOS / Android / 点呼机）持公钥验证。或者点呼机不验 JWT，全部 checkin 走 backend HTTP API（牺牲离线能力）。当前姿态未拍板时至少在 BACKEND_DESIGN_LOG 标注「HS256 决策依赖于点呼机不本地验 JWT」。
- **跨会话**：@C（如果 C 审 BACKEND_DESIGN_LOG）

### [A-003] 🔴 NFC checkin 没有签名 / nonce 验证

- **文件**：`03_dev/backend/v1/app/routers/rollcall.py:127-191`（`create_checkin`）+ `schemas.py` 对应 `RollCallCheckinIn`
- **描述**：POST `/rollcall/sessions/{id}/checkins` 接收 `card_uid` + `student_id`，没有任何防作弊机制：
  1. 没有 nonce — 任何人拿到一次合法请求体能 replay 无数次
  2. 没有 ECDSA 签名 — 攻击者用 NFC reader 读取目标学生卡 UID（NFC UID 不是 secret，可以远距离读取）后能伪造 checkin
  3. 路径 A 注释「card_uid に対応する学生が見つかりません (P1 実装待ち)」— 当前实现需要 client 同时传 `student_id` + `card_uid`，等于完全放弃了「NFC 卡 = 学生身份证明」这一防线
  4. 调用方是 `get_current_teacher`，意味着「老师代签」是默认路径 — 但 spec / system_features 的核心防御是「学生本人拿自己卡刷」+ 「动态 nonce 刷新」+ 「ECDSA 签名」
- **建议改法**：
  1. 必须挂 `idempotency_key`（已在 schema 里有字段但没强制使用 + 没在 DB 加 unique constraint）
  2. P1 必须实现：`card_uid` 在 `students` 表 / 单独 `nfc_cards` 表里 lookup（移除 `student_id` 路径 A fallback）
  3. spec 拍板的「ST25DV16K 动态 nonce 10 秒刷新」+ 「ECDSA 签名」要立项落到 endpoint 字段（`signature: str` + `nonce: str` + `nonce_issued_at: datetime`），server 端验签 + nonce 有效期 + nonce 唯一性（防 replay）
  4. 紧迫程度：v1.0 NFC 实卡上线**前**必须做。当前 demo 阶段 acceptable 但要在 BACKEND_DESIGN_LOG 加 🚨 红标
- **跨会话**：N/A

### [A-004] 🔴 学生 login 用「学号 + 密码」— 学号是公开信息

- **文件**：`03_dev/backend/v1/app/routers/auth.py:21-44`
- **描述**：学生用「学号 + 密码」登录。学号是 grade+class+seat（6 位数字）组合，宿舍 / 班级里所有人都知道彼此学号，等于把「用户名」变成公开信息。一旦密码弱（学生没养成强密码习惯），蛮力破解可行。错误信息 `"学号 or 密码が違います"` 不区分（这一点做对了 — 不泄露学号是否存在）。
- **建议改法**：
  1. 加 rate limit（已经有 `failed_count` + `lock_level` 字段但当前 code 没看到 lockout 逻辑 — 第 63 行 `account.failed_count = 0` 是登录成功重置，但失败时**没看到** `failed_count += 1` 这段）
  2. 密码复杂度强制 — 现在 schema 看不到 `min_length` / `pattern`，需要确认
  3. 长期：考虑「学号 + 个人独立 PIN（注册时设的）+ TOTP」三因子。当前 1.0 不强求但 BACKEND_DESIGN_LOG 要标注风险
- **跨会话**：N/A

### [A-005] 🔴 失败计数器没递增 — lock_level 形同虚设

- **文件**：`03_dev/backend/v1/app/routers/auth.py:32-44` + `auth.py:76-80`
- **描述**：学生 / 教师登录失败时直接 raise HTTPException，**完全没有** `account.failed_count += 1` / `lock_level` 更新逻辑。models.py 里有 `failed_count` / `lock_level` 字段（待确认 — 下文读），但 router 不写。等于 brute-force 无任何代价。
- **建议改法**：在 login 失败分支补 `account.failed_count += 1` + `if failed_count >= N: lock_level = 1`，并在登录入口前查 `if lock_level >= X and last_login_at < now - timedelta(minutes=15): raise LOCKED`。需要 spec 拍板锁定阈值 + 时长。
- **跨会话**：N/A

### [A-006] 🟡 教师 login 没指数退避 / IP 锁

- **文件**：`03_dev/backend/v1/app/routers/auth.py:71-104`
- **描述**：教师端 login 同样没有失败计数。教师权限更高（能改判 / 发邀请码 / 解除 NFC 绑定），一旦被蛮力破解危害大于学生。同 A-005，但严重度更高。
- **建议改法**：同 A-005，且阈值更严（3 次失败立锁 30 分钟）。
- **跨会话**：N/A

### [A-007] 🟡 CORS 默认开发地址，没看到 production override 校验

- **文件**：`03_dev/backend/v1/app/config.py:40` (`cors_origins: str = "http://localhost:5173,http://localhost:3000"`)
- **描述**：默认是 dev 地址，但 production 部署如果忘配 `.env CORS_ORIGINS`，浏览器会拒绝所有教师 web 请求 — 这是 deploy-time fail-loud（好事）。**但** 如果有人配成 `cors_origins=*`，没有任何校验阻止。
- **建议改法**：`get_settings` 里加 `if app_env=="production" and "*" in cors_origin_list: raise`。低优先，标 🟡。
- **跨会话**：N/A

### [A-008] 🟡 SQLite 默认 DB — production 风险

- **文件**：`03_dev/backend/v1/app/config.py:26` (`database_url: str = "sqlite:///./tomoshibi_dev.db"`)
- **描述**：默认 SQLite，没有强制 production 用 PostgreSQL 的检查。CLAUDE.md 说 production 用 PostgreSQL，但 config 没拦。同 A-001 思路，需要 `if app_env=="production" and is_sqlite: raise`。
- **建议改法**：加 fail-fast。
- **跨会话**：N/A

### [A-009] 🟡 点呼机 src 全是空骨架 — 5 端联动当前不可能跑通

- **文件**：`03_dev/rollcall_device/src/main.py:1-9` + `src/nfc/__init__.py`（空文件） + `src/api/__init__.py`（空文件） + `src/led/` + `src/audio/`
- **描述**：点呼机源码是 placeholder。NFC 写卡 / nonce 生成 / 签名验证逻辑**全部未实装**。这不是「漏洞」是「缺口」，但既然 spec 已经写了 ECDSA + nonce 防御，工程上没有任何代码意味着 backend 那边收到的所有 NFC checkin 都跑「无验证路径」(A-003)。
- **建议改法**：要么把 backend NFC checkin endpoint 标 `disabled until v1.0` 关掉，要么把 spec 的 ECDSA / nonce 部分降级到 v1.1（cards demo 用纯 UID + idempotency_key）— itsuki 拍板。
- **跨会话**：N/A

### [A-010] 🔴 spec 写了 ECDSA + nonce 防代刷 / 防 replay，backend 一行未实装

- **文件**：`02_design/flow_design.md:63-115`（路径 B-iOS 完整流程）+ `02_design/hardware_design.md:144`（"上线版本保持 ST25DV16K 动态 nonce 方案不变（nonce 每 10 秒刷新防代签）"）+ `01_specs/rollcall/ERROR_CODES.md:26`（`INVALID_SIGNATURE` 错误码）+ `03_dev/backend/v1/app/routers/rollcall.py:127-191`（实装）
- **描述**：设计文档（flow_design 第 95-100 行）明文要求：
  - app 用 iOS Keychain 私钥做 ECDSA 签名 `signature = sign(student_id || device_id || nonce || ts)`
  - 提交字段 `{ student_id, device_id, nonce, signature, ... }`
  - 后端 §107 行 "校验 nonce 有效性：是 10 秒内发给 DEV001 的吗?"

  现状：
  - `RollCallCheckinIn` schema（schemas.py:402-409）只有 `card_uid` / `student_id` / `idempotency_key` / `status_source` / `ts_local`，**没有** `device_id` / `nonce` / `signature` 字段
  - `create_checkin` 实装（rollcall.py:127）完全没有 nonce 表 / 签名验证 / device_id 校验
  - `models.py` 没有 `nonces` 表 / `devices` 表 / 学生 NFC 卡公钥表
  - `POST /api/v1/nonce` endpoint（flow_design §70 行所述）**不存在**
- **建议改法**：v1.0 上线前必做以下其一：
  1. **完整实装**：加 `Device` / `Nonce` / `NFCCard` 三张表 + `POST /api/v1/nonce` endpoint + `RollCallCheckinIn` 加 4 字段 + 后端 ECDSA 验签逻辑（用 `cryptography.hazmat.primitives.asymmetric.ec`）
  2. **降级 v1.0 上线**：spec 砍掉 ECDSA / nonce，路径 B 用「JWT + idempotency_key + ts 滑窗（±60s）」替代；明确标 v1.1 升级 — itsuki 拍板
- **跨会话**：N/A — 这条直接影响 v1.0 是否可上线宿舍真实环境

### [A-011] 🟡 idempotency_key 没有 UniqueConstraint — 同 key 重复 POST 不安全

- **文件**：`03_dev/backend/v1/app/models.py:617-619`（RollCallEvent.idempotency_key 字段定义） + `routers/rollcall.py:164-172`（去重逻辑）
- **描述**：`idempotency_key` 字段是 Text 没有 unique index。当前去重靠 router 第 165-171 行的 query (同 session_id + 同 student_id + same status_source 找 existing)，**不查 idempotency_key**。这意味着：
  - client 用同一个 idempotency_key 重试，后端不能凭 key 直接拒绝重复 — 真正去重的是 session_id + student_id + status_source 组合
  - 如果 client 在两个 session 间隔切换时复用 key，可能产生「同 key 多 student / 同 key 多 session」绑定
  - idempotency_key 设计本意就是 client 防重复提交，这里没正确实现
- **建议改法**：加 `UniqueConstraint("session_id", "idempotency_key", name="uq_rce_idempotency")`；router 查重改成「先查 idempotency_key 命中 → 直接返已存事件」。spec / BACKEND_DESIGN_LOG 同步更新。
- **跨会话**：N/A

### [A-012] 🟡 教师 register endpoint 不校验 invitation.target_email — 任何拿到 token 的人都能注册

- **文件**：`03_dev/backend/v1/app/routers/teachers.py:76-131`
- **描述**：`POST /teachers/register` 只检查 token 是否存在 / 是否过期 / 是否已用。**没有校验**当前注册请求的来源跟 `invitation.target_email` 是否对得上。等于 token 被中间人拿到（邮件被转发 / 截图 / Slack 转发）→ 任何人都能注册成此教师。最后第 117 行 `email=invitation.target_email` 是从 invitation 取的（好），但 login_id / password 是注册者自由选的（坏）。
- **建议改法**：注册时要求 `body` 多带 `confirmation_email` 字段，跟 `invitation.target_email` 严格对比；或者改成「邀请链接 → 跳学校邮箱验证页 → 验证通过才能注册」两步法。短期权宜：在 schema 加 `target_email_confirm` 必填字段。
- **跨会话**：N/A

### [A-013] 🟡 `/applications/{application_id}` 路由顺序 bug — `/pending-for-me` 被吃掉

- **文件**：`03_dev/backend/v1/app/routers/applications.py:151`（`{application_id}`） + `applications.py:254`（`/pending-for-me`）
- **描述**：FastAPI 按路由**注册顺序**匹配。`@router.get("/{application_id}")` 在第 151 行，`@router.get("/pending-for-me")` 在第 254 行 — `/applications/pending-for-me` 请求会先撞到 `{application_id}` 路径，FastAPI 会尝试把 `"pending-for-me"` 解析成 UUID → 422 错误，**而不是**走到 `/pending-for-me` 实装。
- **验证方式**：跑后端，`curl -H "Authorization: Bearer <teacher_token>" http://localhost:8000/api/v1/applications/pending-for-me` 看返回。
- **建议改法**：把 `/pending-for-me` 定义移到 `/{application_id}` 之**前**。同样的 PUT/audit 子路径也应该挪。FastAPI 文档 best practice：静态路径在前、动态路径在后。
- **跨会话**：N/A

### [A-014] 🟢 reviewer 注册码 "999999" 写死在 seed.py — 公开 repo 风险

- **文件**：`03_dev/backend/v1/seed.py:251` (`PROD_REVIEWER_REGISTRATION_CODE = "999999"`) + `seed.py:247` (`PROD_REVIEWER_PASSWORD = "Tomoshibi-Reviewer-2026!"`)
- **描述**：DMSD repo 是 public。任何人 clone 后能直接拿到 reviewer 永久注册码 + 密码。code 6 桁 + 永久有效（`is_reviewer=True` 不过期）意味着上线后这是稳定后门。
- **建议改法**：把 reviewer 凭证移到 `.env` / `secrets/`（gitignored）。production seed 启动时从环境变量读取。最坏情况能容忍（Apple reviewer 用完审核就完），但应该 v1.0 上线后立刻 rotate。
- **跨会话**：N/A

---

## 维度 1：跨端字段对齐

### [A-015] 🔴 iOS `StudentBrief` 跟 backend 一致 — 但 iOS 完全不调 rollcall API（端到端缺口）

- **文件**：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/*` 全无 `RollCall*API.swift` + `backend/v1/app/routers/rollcall.py:127`（实装存在）
- **描述**：backend `rollcall.py` 实装了 8 个 endpoint（today/sessions、start、end、checkins、board、summary、events PATCH 等），但 iOS / Android **都没有任何 RollCall API client** — iOS 只 Auth/Applications/Study/Announcements，Android 完全无 HTTP client（见 A-016）。这意味着即使 backend rollcall 实装了，student app 那边「学生用 NFC tap」流程**完全没接通**。
- **建议改法**：iOS 加 `RollCallAPI.swift`（至少 POST /checkins 给学生 tap iPhone-BTR 入口）；Android 同上 + 加 HTTP client（见 A-016）。或者明确 spec：rollcall 接 client 是 v1.0 必做、还是 v1.1 推迟。
- **跨会话**：N/A

### [A-016] 🔴 Android 完全没有 HTTP client — 跟 backend 100% 脱节

- **文件**：`03_dev/student_android/v1/app/build.gradle.kts`（没有 retrofit / okhttp / ktor 任何 HTTP 库）+ `data/model/Models.kt`（全是本地 mock 字段名 camelCase）
- **描述**：Android 项目 `dependencies` 只有 Compose + DataStore + kotlinx.serialization，**没有任何 HTTP client**。`Models.kt` 里的 `User / Application / RollCall / Deduction` 等字段是给 React app-shell.jsx 本地 mock 用的（如 `studentNo / gradeClass / phone` 直接默认 "060218 / 高3B組 18番 / 090-9482-8905"），跟 backend `StudentBrief`（`student_no / dorm_unit / room_no` snake_case）字段名 + 命名风格都不一致。等于 Android 端是「demo only」状态。
- **建议改法**：v1.0 上线前必须：
  1. 加 Ktor / Retrofit + kotlinx-serialization 处理 snake_case ↔ camelCase
  2. 新建 `data/api/` 子模块，类比 iOS 的 `Endpoints/`
  3. 把 `Models.kt` 拆成 `domain/`（业务模型 camelCase）+ `api/dto/`（跟 backend 对齐的 snake_case DTO）
  4. 进度条上明确：Android 当前 = "UI prototype + DataStore 持久化"，**不是** "iOS 同等功能" — itsuki 可能误以为 Android 已经接通
- **跨会话**：N/A

### [A-017] 🟡 teacher_web `AppStatus` 漏了 `returned` 状态

- **文件**：`03_dev/teacher_web/v1/src/api/client.ts:114` (`AppStatus = "pending" | "approved_partial" | "approved" | "rejected" | "withdrawn"`)
- **描述**：backend `schemas.py:189-191` 的 `ApplicationOut.status` 包含 6 值：`pending / approved_partial / approved / rejected / withdrawn / returned`。teacher_web 的 type union 漏了 `returned`（spec §7.2.4-5 老师退回学生修改）。TypeScript 收到 `returned` 时不会报错（运行期 type 是字符串），但 UI 渲染时 switch 不到这个 case 会漏显示「退回中」状态。
- **建议改法**：`AppStatus` 加 `| "returned"`。检查 UI（Applications.tsx）的 switch / lookup 加 returned 分支。
- **跨会话**：N/A

### [A-018] 🟡 teacher_web `Application` 接口字段不全 — reason / stay_locations / meals_skip / flight_* 全缺

- **文件**：`03_dev/teacher_web/v1/src/api/client.ts:133-147`
- **描述**：teacher_web `Application` 接口只有 7 个共通字段（kind / leave_*/return_*/submitted_at/status/chain），**没有** `reason / stay_locations / meals_skip / flight_dep_air / flight_dep_at / flight_arr_air / flight_arr_at / withdrawn_at / bus_route_id`。这些字段对老师审批是关键（外泊届里学生写的滞在先、留学生 帰国届 的飞机信息），但 web TypeScript 类型层把它们藏起来了。如果 web `Applications.tsx` 用 `app.reason` 会编译报错。
- **建议改法**：把 backend `ApplicationOut` 全字段映到 ts 接口（Optional 处理 `null`），照 iOS NetworkModels.swift:43-73 那样做齐。
- **跨会话**：N/A

### [A-019] 🟡 iOS `StudentAccountCreateBody` 跟 backend `StudentAccountCreateIn` 字段类型有出入（birthday）

- **文件**：`iOS NetworkModels.swift:106-121` + `backend schemas.py:530-547`
- **描述**：iOS `birthday: String?`（"yyyy-MM-dd"），backend `birthday: Optional[date]`。这个组合是 OK 的（Pydantic 能从字符串解析），但 iOS 没有 `nameKana / phone` 长度限制（schema 没要求 max_length）；backend `name_kana` Optional 最大 100，`phone` 最大 32。当前 iOS 端没做客户端预校验，可能造成 422 错误后端才拦。
- **建议改法**：iOS 客户端 form 加 max length 校验镜像 backend。低优先。
- **跨会话**：N/A

### [A-020] 🟡 iOS `path_type` 跟 backend 用法不一致 — backend 写入用 "A/B/manual"，schema 没限制；rollcall.py:181 行为可疑

- **文件**：`03_dev/backend/v1/app/routers/rollcall.py:181` (`path_type="A" if body.card_uid else ("B" if body.idempotency_key else "manual")`) + `schemas.py:402-409` (`RollCallCheckinIn` 没有 `path_type` 字段)
- **描述**：第 181 行判断逻辑：有 card_uid → A、有 idempotency_key（但没 card_uid）→ B、否则 manual。但 schema 第 408 行 `idempotency_key` 是 Optional 任何路径都能传。如果 client（iOS BTR 路径 B）传了 `card_uid` + `idempotency_key` 都有的情况，backend 会标 A（应该是 B）；如果老师手动签到（路径 manual），client 没传 idempotency_key 也没 card_uid，标 manual（对）。这个 dispatch 用「字段是否存在」推断路径，比较脆弱。
- **建议改法**：schema 加 `path_hint: Literal["A", "B", "manual"]` 由 client 显式标，backend 校验「path_hint=A 必须有 card_uid，path_hint=B 必须有 idempotency_key + nonce + signature」。
- **跨会话**：N/A

### [A-021] 🟢 iOS / Android / backend 学生 ID 都用 UUID — 命名一致（无问题）

- **文件**：3 端 student id 都用 UUID — 这条作为 positive note。

### [A-022] 🟡 iOS Decodable 字段用 snake_case 直接 — 没 CodingKeys 转 camelCase

- **文件**：`03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:17-24` (StudentBrief) + `:43-73` (ApplicationOut) 等多个
- **描述**：iOS Swift 风格通常 camelCase，但这里 `student_no / dorm_unit / is_overseas / leave_date / approval_chain` 等字段都保持 snake_case（即跟 backend 一致）。Swift API design guideline 推荐 camelCase，但跨端对齐时为了 byte-perfect 选了 snake_case。代价是 iOS SwiftUI view 里 `student.student_no` 看起来不 Swift-y。
  - 注：后期加的 `AnnouncementBrief / AnnouncementDetail` 改用了 CodingKeys + camelCase（NetworkModels.swift:142-163）— **两种风格混在同一文件里**，未来会有 confusion。
- **建议改法**：统一选一种。建议：用 `.convertFromSnakeCase` 设全局 JSONDecoder.keyDecodingStrategy 一次性处理，所有 Swift 类型用 camelCase；或者把 `AnnouncementBrief` 改回 snake_case 跟前面对齐。
- **跨会话**：N/A

---

## 维度 2：联动矩阵全过

### [A-023] 🟡 backend models.py 增了 `is_demo` / `is_reviewer` 但 iOS NetworkModels.StudentBrief 没字段

- **文件**：`backend models.py:72` (`is_demo: Boolean`) + `iOS NetworkModels.swift:17-24` (StudentBrief 没 `is_demo`)
- **描述**：联动规则「backend models.py → iOS NetworkModels.swift（字段对齐）」违反。backend `Student.is_demo` 是后加的（spec §7.20 reviewer 体验账号），iOS StudentBrief 没暴露 — 这个 OK（iOS 不需要知道自己是不是 demo），但**应该在 BACKEND_DESIGN_LOG.md 显式记**「is_demo 不向客户端暴露」，否则未来加用得到的字段时容易漏一端。
- **建议改法**：BACKEND_DESIGN_LOG.md §4 加附注「字段隐私分级 — 哪些字段 backend-only / 哪些向 client 暴露」。
- **跨会话**：@C（如果 C 审 BACKEND_DESIGN_LOG）

### [A-024] 🟡 routers/rollcall.py 实装 8 endpoint，iOS Endpoints/ 里**完全没** RollCallAPI.swift

- **文件**：`03_dev/backend/v1/app/routers/rollcall.py` (8 endpoint) + `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/Endpoints/`（缺 RollCallAPI.swift）
- **描述**：联动规则「backend routers/*.py → iOS Endpoints/*API.swift」违反。CLAUDE.md 写明「字段对齐 + 端点对齐」。教师 web 已对齐（rollcallTodaySessions / Start / End / Board / Summary），但学生 iOS 端**根本没有**对应文件。
- **建议改法**：iOS 至少加 `RollCallAPI.swift`，含 `POST /api/v1/rollcall/sessions/{id}/checkins`（学生 BTR tap 入口）；其他 GET endpoint iOS 学生用不到。
- **跨会话**：N/A

### [A-025] 🟢 routers/applications.py + iOS ApplicationsAPI 已对齐（含 mine / detail / update / audit）— 联动达成

- 联动 OK 的 positive note。

### [A-026] 🟡 backend Announcement 后加，alembic migration 是 e5f6a7b8c9d0_add_announcements.py 单独一个 — iOS / web 跟得上

- **文件**：`backend alembic/versions/e5f6a7b8c9d0_add_announcements.py` + iOS `NetworkModels.swift:142-217`（AnnouncementBrief/Detail/Reply/UnreadCount） + teacher_web 现在**没有** AnnouncementsAPI
- **描述**：iOS 已对齐 Announcement，teacher_web 没有 announcement 管理界面（老师没法发公告）。spec §7.15 "老师 → 学生 单向通知"，等于 teacher_web 没法走完循环。
- **建议改法**：teacher_web 加 Announcement 发布页 + API。或者 spec 加注「v1.0 公告通过后端 admin 接口手动发，teacher_web v1.1 加 UI」。
- **跨会话**：N/A

### [A-027] 🔴 ROLLCALL_DEVICE_DESIGN_LOG 写了完整设计，src/ 几乎空 — 联动断裂

- **文件**：`03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` (226 行设计) + `src/main.py` (9 行 placeholder) + `src/nfc/__init__.py` (空) + `src/api/__init__.py` (空) + `src/led/__init__.py` (空) + `src/audio/__init__.py` (空)
- **描述**：联动规则「点呼机 src 业务代码改 → ROLLCALL_DEVICE_DESIGN_LOG.md 同步」反过来也成立 — 设计文档说有 §3 主循环 §4 模块设计，但代码全部 placeholder。这是从设计文档单向写下来、还没开始实装的状态。
- **建议改法**：明确标 ROLLCALL_DEVICE_DESIGN_LOG.md 头部「实装进度: 0% — code 全是 placeholder」。CLAUDE.md WIP 或 TODO 加显式条目。
- **跨会话**：N/A

### [A-028] 🟡 spec ECDSA / nonce 写在 02_design/flow_design.md，但 backend models / schemas / routers 完全不知道

- **文件**：`02_design/flow_design.md:63-115` + `02_design/hardware_design.md:144` + `01_specs/rollcall/ERROR_CODES.md:26` + `backend models.py` (无 Device / Nonce / NFCCard 表) + `schemas.py:402` (无 signature 字段)
- **描述**：联动规则「02_design/system_features.md → 5 端 *_DESIGN_LOG.md 引用要更新」+「01_specs/rollcall/* 主体改 → SOP 阅读 + 可能 bump 版本号」失败。flow_design + hardware_design + ERROR_CODES 都标了签名 / nonce，但 backend 完全没体现。详情见 A-010。
- **跨会话**：N/A

---

## 维度 3：设计文档分层一致

### [A-029] 🟡 iOS / Android / Web DESIGN_LOG 都没有「实装进度」对照表 — 哪个 spec 章节哪个 view 实装了不可查

- **文件**：`03_dev/student_ios/IOS_DESIGN_LOG.md`（989 行）+ `student_android/ANDROID_DESIGN_LOG.md`（253 行）+ `teacher_web/WEB_DESIGN_LOG.md`（806 行）
- **描述**：每个 DESIGN_LOG 都有大量决策记录，但**没有**「v1.0 实装范围 vs 推迟到 v1.1」的覆盖矩阵。这导致：
  - itsuki 不知道 Android 实际跟 backend 脱节（见 A-016）
  - 没有标识「本端 NFC 实装 = 0%」之类显式状态
  - 审 spec 时容易认为「设计文档说有 = 代码里有」
- **建议改法**：每个 DESIGN_LOG 顶部加「当前实装进度速查表」section（基于 spec §xx / 字段 / endpoint 列「已 / 部分 / 未」3 态）。低优先但能防漂移。
- **跨会话**：N/A

### [A-030] 🟡 system_features.md §7.3.8 amber Card 三态 demo-only — iOS / Android 都还在用 long-press cycle

- **文件**：`system_features.md` §7.3.8 标记 ⚠️ DEMO-ONLY + `iOS HomeStubs.swift:256,535` (cycleDemoRollState long-press) + `Android AppStore.kt:59-61` (cycleDemoRollState)
- **描述**：spec / memory `project_demo_scaffolds_to_remove_before_v1.md` 第 15 条明确 v1.0 上线前必须删的功能，但 iOS + Android 当前都还在用。**memory 跟代码同步** — memory 不是漂移，是「v1.0 没到」的延期。
- **建议改法**：加 TODO 入 v1.0 sprint：删 long-press cycle + amber Card 三态 + 接 backend event 驱动。CLAUDE.md / WIP 显式登记 v1.0 上线前 GO/NO-GO 检查项。
- **跨会话**：N/A

### [A-031] 🟢 backend BACKEND_DESIGN_LOG 跟实装代码相对齐（registration_code / announcement / rollcall router 都有对应章节）

- positive note。

### [A-032] 🟡 teacher_web/demo/ 仍残留 14 文件 jsx — Web v1 替代品但 demo/ 没归档

- **文件**：`03_dev/teacher_web/demo/src/components/` 14 个 jsx（accounts / applications / discipline / front-desk / live-roll-call / login / outstay-detail-modal / override-modal / pages-records-search-etc / roll-call-landing / select-teacher / shell / theme / app）
- **描述**：teacher_web `v1/src/` 已有真 backend 接通的实装，但 `demo/` 还在原地。memory `project_demo_scaffolds_to_remove_before_v1.md` 第 9-14 条提到的 SHARED_PASSWORD / DEMO_SEED / window.ACCOUNTS 都在 `demo/` 里（不在 v1/）。当前不影响生产，但**长期** demo/ 会随 v1/ 漂移成废弃代码。
- **额外发现**：`teacher_web/v1/src/index.html` 第 4262/4296/4297/4339/4393 行**也**残留 `window.SHARED_PASSWORD='12345678'` / `DEMO_SEED_NO = '060218'` / `window.ACCOUNTS` — 不是 demo/ 里的，是 v1/ 里的 index.html 居然 7774 行（应该 ~10 行 vite html shell），看起来是把整个旧 demo 单页 HTML 拷过来了。
- **建议改法**：
  1. `v1/src/index.html` 应该回归 vite minimal shell（< 50 行）— 删掉 7774 行老 demo HTML
  2. `teacher_web/demo/` 整体 archive 到 `99_archive/`
- **跨会话**：N/A

---

## 维度 4：demo scaffold 清单 vs 实际代码

### [A-033] 🔴 iOS `HomeStubs.swift:256,535` long-press cycleDemoRollState 仍存在 — memory 第 1-2 条命中

- **文件**：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift:256` (⚠️ DEMO-ONLY 三态切换 comment) + `:535` 周边 + `Foundation/AppState/AppStore.swift` (cycleDemoRollState 函数)
- **描述**：memory 清单第 1-2 条「v1.0 必删」— 仍未删。
- **建议改法**：v1.0 sprint 必删。
- **跨会话**：N/A

### [A-034] 🔴 Android `AppStore.kt:59-61` cycleDemoRollState 跟 iOS 同步存在

- **文件**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/store/AppStore.kt:59-61`
- **描述**：跟 A-033 同步，Android 也写了 `// Demo 切换 — 长按 amber Card 触发 4 态轮换（AC demo 杀器）`。
- **建议改法**：v1.0 sprint 同 A-033 一起删。
- **跨会话**：N/A

### [A-035] 🔴 iOS `AuthStubs.swift:1254,1921,2044` 密码预填 + magic value 000000 — 注册流程 demo 后门

- **文件**：
  - `Features/Auth/AuthStubs.swift:1254` （⚠️ DEMO-ONLY-SCAFFOLD 密码预填）
  - `:1921`（默认填 "000000" demo magic value）
  - `:2044`（magic value 跳过 backend 直接 done）
- **描述**：这 3 个标记在注册流程 / 注册码输入 / OTP 类。"000000" 是 magic value 跳后端验证，等于注册时输入 000000 直接通过 — **危险**。memory 清单未列这条（属于 5-03 后新增 scaffold）。
- **建议改法**：v1.0 上线前 grep `magic.value\|"000000"\|0000` 在 Auth 流程全删。
- **跨会话**：N/A

### [A-036] 🟡 iOS `SEED.user` 硬编码 リュウイヒ / 060218 / M101 — 跟 Android `MockData.kt` 双端同步漂

- **文件**：`student_ios/v1/.../Foundation/Seed/SEED.swift:10-30` + `student_android/v1/.../data/seed/MockData.kt:11,17`
- **描述**：iOS + Android 都把 reviewer / demo 学生硬编码进 SEED。背景：未登录态下 demo 数据兜底。后端有 `is_demo` 字段过滤，但 client 启动时本地兜底直接显示 060218。问题：
  - public repo 暴露真实学生 6 桁学号格式 + 房号编码 + 减点数 — 不严重（反正格式公开）
  - **真实问题**：登录后如果 backend 数据没拉回来，client 会回退显示 060218 — 学生看到别人的房号会困惑
- **建议改法**：登录后强制清 SEED.user，未登录显示「— 」占位。AppStore 引入 `var isAuthenticated: Bool` gate。
- **跨会话**：N/A

### [A-037] 🟡 iOS `StayListStubs.swift` 5 处 DEMO-ONLY-SCAFFOLD 纯 mock 替代 GET /applications/mine

- **文件**：`Features/StayList/StayListStubs.swift:390,453,687,1133,1346`
- **描述**：学生 StayList 页（自己的出寮届）当前用 `StayListMock` 替代真 API。memory 清单第 4 / 11 条总览提到 demo seed，**未列**这 5 处 view 级 mock。
- **建议改法**：替换成 `ApplicationsAPI.listMine()`。CLAUDE.md WIP 加显式 sub-task。
- **跨会话**：N/A

### [A-038] 🟡 iOS `AppStore.swift:98,217,230,260,286,535` Announcement demo seed 5 处 — 没 backend 时本地伪造 reply

- **文件**：`Foundation/AppState/AppStore.swift:98,217,230,260,286,535`（注释 ⚠️ DEMO-ONLY-SCAFFOLD）
- **描述**：老师公告 demo seed + seedCache 兜底 + 本地伪造 reply。memory 没列（5-04 后新增）。
- **建议改法**：上线前删 `seedDemoAnnouncements()` + 调用点 + 函数本体。
- **跨会话**：N/A

### [A-039] 🔴 teacher_web v1/src/index.html 残留 7700+ 行旧 demo HTML — `SHARED_PASSWORD='12345678'` + `ACCOUNTS` 全员明文

- **文件**：`03_dev/teacher_web/v1/src/index.html` 7774 行（应该 < 50 行 vite shell）
- **描述**：本应该是 Vite 入口 HTML，被填了 7700+ 行旧 demo SPA 代码。memory 第 9-14 条说在 `teacher_web/round3/src/`，但**实际上**漂到了 `v1/src/index.html` 第 4262 行起 `window.SHARED_PASSWORD='12345678'` + 4297 行 `window.ACCOUNTS = [...]` 24 人明文 + 4393 行 `<div>demo: tomoshibi / {window.SHARED_PASSWORD}</div>` 登录页显示密码 + 4772 行右下角 `DEMO` badge。
- **建议改法**：紧急处理。`v1/src/index.html` 改回 vite 标准模板（10-20 行 `<div id="root"></div>`），把 7700 行老 demo 整段删除（或挪到 `demo/` 也行，反正不能在 v1/ 里）。
- **跨会话**：N/A — 这是 5-12 之后 audit 该 catch 的，可能 5-19 工程边角清理时没扫到。

### [A-040] 🟢 backend `is_demo` 过滤逻辑已正确生效（rollcall.py:211,363 + applications.py:279）

- positive note — 出席板和申请列表都加了 `is_demo.is_(False)` 过滤，reviewer 学生不会污染老师面板。

---

## 总计

- 🔴 阻塞上线：14 条（A-001, A-002, A-003, A-004, A-005, A-010, A-015, A-016, A-027, A-033, A-034, A-035, A-039）
- 🟡 该修：22 条（A-006, A-007, A-008, A-009, A-011, A-012, A-013, A-017, A-018, A-019, A-020, A-022, A-023, A-024, A-026, A-028, A-029, A-030, A-032, A-036, A-037, A-038）
- 🟢 优化 / 信息条：4 条（A-014, A-021, A-025, A-031, A-040 — 注：A-021/25/31/40 为 positive note，A-014 是低优先优化）

实际 🔴 阻塞数 13（去 A-027 算 🟡 — 是「未实装」不是「漏洞」，更严格地说应该跟 itsuki 拍板时定级）。



