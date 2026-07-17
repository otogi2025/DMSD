# DMSD 全项目错误码字典

更新时间：2026-07-17（**7-17 全面改版 — itsuki 拍板「错误码字典全统一、放规格文件夹」**：原 v0.1 点呼域字典（15 码）扩为**全项目字典**，后端实际发码全量登记（改版日脚本盘点 107 码 / 311 处发码点，后端双会话审查 2-中-4/5/6 收口）。路径保留 `specs/rollcall/`——引用面 12+ 文件含挂钩脚本，搬家断链成本大于收益；自本版起本文件覆盖全部业务域，不限点呼）

## 1. 使用规则

- 业务错误必须返回本字典登记的 code；**后端新增错误码时必须同步登记本表**（spec-dict-chain 联动）。
- 响应格式（与 `API_CONVENTIONS.md §1` 响应信封一致）：
  - 失败：`{ "ok": false, "error": { "code": "...", "message": "..." } }`
  - 成功：`{ "ok": true, "data": { ... } }` — **不含 `error` 字段**（4-22 S19：成功/失败字段集互斥，前端用 `ok` 分派）
- `message` 为日语、即用户可见文案的默认值。前端可按 code 覆盖本地化文案；未覆盖的码直接显示 message；未知码显示通用兜底文案。原 v0.1「中文文案映射表」废止（当时 UI 未定型；现 UI 语言 = 日语，message 即文案）。
- HTTP 状态码语义对照 `API_CONVENTIONS.md §8`。同一 code 固定一个状态码。

## 2. 通用 / 横切（鉴权 · 权限 · 演示隔离 · 账号状态）

| code | HTTP | 语义 |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | 未登录 / 令牌无效 / 凭证错误（登录失败也用它——不区分「账号不存在」，防枚举） |
| `FORBIDDEN` | 403 | 已登录但无此操作权限（权限组不足 / 身份类别不符） |
| `FORBIDDEN_ROLE` | 403 | 缺特定功能簇权限（如指导履历閲覧） |
| `FORBIDDEN_DORM` | 403 | 寮边界：担当寮外学生不可操作（7-17 拍板「分角色跨寮」后实装随之调整，见 `design/teacher_permission_v1.md §13`） |
| `DEMO_READONLY` | 403 | 演示账号不可执行该写操作 |
| `DEMO_FORBIDDEN` | 403 | 演示账号不可执行该操作（横切闸） |
| `ACCOUNT_INACTIVE` | 403 | 账号已停用 |
| `ACCOUNT_EXPIRED` | 403 | 临时账号已过有效期 |
| `ACCOUNT_LOCKED` | 423 | 登录连续失败锁定中（老师 3 次/30 分、学生 5 次/15 分） |
| `NOT_FOUND` | 404 | 资源不存在 / 已删除（通用兜底 404） |
| `STUDENT_NOT_FOUND` | 404 | 指定学生不存在 |
| `INVALID_INPUT` | 422 | 输入不合法（通用兜底 422） |
| `MISSING_IDENTIFIER` | 422 | 请求缺必需标识（如 teacher_id / login_id 二选一都没传） |

## 3. 老师账号管理 · 邀请（teachers.py / admin_accounts.py）

| code | HTTP | 语义 |
|---|---|---|
| `DUPLICATE` | 409 | login_id 或 email 已存在 |
| `DUPLICATE_LOGIN_ID` | 409 | login ID 已被使用 |
| `EMAIL_MISMATCH` | 403 | 确认邮箱与邀请对象不一致 |
| `INVALID_TOKEN` | 404 | 邀请令牌无效 |
| `TOKEN_EXPIRED` | 410 | 邀请令牌已过期 |
| `TOKEN_USED` | 409 | 邀请令牌已被使用 |
| `CANNOT_DELETE_SELF` | 400 | 不能删除自己的账号 |
| `LAST_ADMIN` | 400 | 最后一名寮务管理权限教师不可删（防系统锁死） |
| `INVALID_ROLE` | 422 | 职位标签不合法 |
| `INVALID_PERMISSION_GROUP` | 422 | 权限组不合法 |
| `ACCOUNT_NOT_FOUND` | 404 | 指定账号未登记 |

## 4. 学生注册 · 学生账号（accounts.py / admin_accounts.py / student_profile.py / admin_registration_code.py / student_promote.py）

| code | HTTP | 语义 |
|---|---|---|
| `INVALID_REGISTRATION_CODE` | 422 | 注册码不正 / 过期 / 已失效（`system_features §7.16`） |
| `STUDENT_NO_TAKEN` | 422 | 学号重复 |
| `EMAIL_TAKEN` | 422 | 邮箱重复 |
| `INVALID_ROOM_FORMAT` | 422 | 房间号与 dorm_unit / 性别不整合（`system_features §5.1.5`） |
| `CODE_GEN_FAILED` | 500 | 注册码生成失败（服务器侧异常） |
| `STUDENT_NOT_ACTIVE` | 409 | 仅在籍（active）学生可做此变更 |
| `RENEWAL_NOT_OPEN` | 409 | 当前不在学年更新对象期 |

## 5. 点呼（rollcall.py）

| code | HTTP | 语义 |
|---|---|---|
| `SESSION_NOT_RUNNING` | 409 | 场次不在 running：还没开始 或 已结束（含结束后的补传签到——2026-07-17 拍板②后原 TIMEOUT 场景归此码） |
| `ALREADY_RUNNING` | 409 | 场次已在进行中，重复开始无效 |
| `ALREADY_ENDED` | 409 | 场次已结束（重复结束无效） |
| `NOT_YET_ALLOWED` | 409 | 早于「准时截止 − 5 分」按开始（`RollCall_Spec §5.4`） |
| `SESSION_EXPIRED` | 409 | 已过预定自动结束时刻的场次不可再开始 |
| `SESSION_NOT_FOUND` | 404 | 点呼场次不存在 |
| `NO_OP_OVERRIDE` | 409 | 改判目标状态与当前相同（空操作） |
| `REPORT_NOT_FOUND` | 404 | 点呼异常报告不存在 |
| `ALREADY_RESOLVED` | 409 | 已处理完毕（点呼异常报告 / 遗失物两域共用同名码，message 各自） |
| `PATH_HINT_MISMATCH` | 422 | path_hint 与携带字段不匹配（A 必须有 card_uid 等） |
| `NO_ROLLCALL_FOR_TODAY` | — | **spec 预定、代码未发**：时间窗配置缺失时阻止建场（`RollCall_Spec §6.6`）；场次自动创建（rollcall_scheduler）落地时实装确认 |

> 点呼**重复签到不发错误码**：命中既有事件直接 200 返回 `duplicate=true`（静默幂等，设备不重复播报——`Device_Contract §4.1`）。`DUPLICATE_REQUEST` 码现仅晚自习欠席届在用（§7）。

## 6. 点呼机设备 · 卡（devices.py / device_auth.py / deps.py — `Device_Contract.md`）

| code | HTTP | 语义 |
|---|---|---|
| `UNKNOWN_CARD` | 422 | 卡 UID 无任何绑定记录（新卡 / 外部卡） |
| `UNREGISTERED_UID` | 422 | UID 有记录但卡已停用 或 学生非 active |
| `UNKNOWN_DEVICE` | 404 | device_id 未注册 |
| `DEVICE_NOT_ACTIVE` | 403 | 设备已停用 |
| `DEVICE_RETIRED` | 409 | 设备已永久注销，不可再有效化 |
| `DEVICE_ALREADY_EXISTS` | 409 | device_id 已存在（注册冲突） |
| `CARD_ALREADY_BOUND` | 409 | 卡已绑定在其他有效学生上 |
| `INVALID_SIGNATURE` | 401 | 设备认证 / 签名校验失败 |

## 7. 出寮届 · 审批（applications.py；`APPROVAL_ALREADY_DECIDED` 为审批类通用码，dorm_life / study / study_online 共用）

| code | HTTP | 语义 |
|---|---|---|
| `APPROVAL_ALREADY_DECIDED` | 409 | 该审批人已决定过（并行会签下重复批） |
| `APPROVAL_NOT_REQUIRED` | 403 | 该职位不是本届的承认者 |
| `NOT_HOMEROOM_TEACHER` | 403 | 不是该学生的担任（班主任） |
| `APPLICATION_FINALIZED` | 409 | 届已确定 / 取消，不可再操作 |
| `APPLICATION_RETURNED` | 409 | 届在差戻し（退回）中，等学生再提出 |
| `CANNOT_MODIFY` | 409 | 已承认 / 拒绝的届不可修正 |
| `CANNOT_RETURN` | 409 | 仅审査中的届可差戻 |
| `CANNOT_WITHDRAW` | 409 | 已承认 / 拒绝 / 取消的届不可撤回 |
| `AMEND_REASON_REQUIRED` | 422 | 修正必须填理由 |
| `NO_CHANGES` | 422 | 修正内容为空 |
| `LEAVE_DATE_NOT_FUTURE` | 422 | 出寮日必须明日以降（学生提交；教師代録当日可） |
| `LEAVE_DATE_PAST` | 422 | 出寮日必须本日以降 |
| `RETURN_BEFORE_LEAVE` | 422 | 帰寮日早于出寮日 |
| `RETURN_TIME_BEFORE_LEAVE` | 422 | 同日时帰寮时刻早于出寮时刻 |

## 8. 外出（outings.py）

| code | HTTP | 语义 |
|---|---|---|
| `OUTING_DATE_PAST` | 422 | 外出日必须本日以降 |
| `OUTING_NOT_PENDING` | 409 | 不是確認待ち状态的外出申请 |

## 9. 晚自习 · 在线学习（study.py / study_online.py）

| code | HTTP | 语义 |
|---|---|---|
| `ALREADY_CHECKED_IN` | 409 | 当日已有出席记录 |
| `ALREADY_IN_ROSTER` | 409 | 已在晚自习名簿中 |
| `NOT_IN_ROSTER` | 404 | 不在晚自习名簿中 |
| `DUPLICATE_REQUEST` | 409 | 当日欠席届已提交过 |
| `LATE_SUBMISSION` | 422 | 已过欠席届截止（晚自习开始前） |
| `PAST_DATE` | 422 | 不可对过去日期提交欠席届 |
| `TARGET_DATE_FUTURE` | 422 | 不可结算未来日期 |
| `TARGET_DATE_TOO_OLD` | 422 | 不可结算 30 天前的日期 |
| `FINALIZE_CONFLICT` | 409 | 结算并发冲突，请重试 |
| `ALREADY_DECIDED` | 409 | 已审査完毕的申请不可变更 |
| `CANNOT_REVOKE` | 409 | 仅已许可的申请可取消 |
| `ONLINE_REQUEST_OVERLAP` | 409 | 同期间的在线学习申请已存在 |
| `ONLINE_REQUEST_TOO_LATE` | 422 | 在线学习申请须开始 3 日前提出 |
| `EMPTY_FILE` | 422 | 上传文件为空 |
| `FILE_MISSING` | 404 | 契約書文件不存在 |
| `FILE_TOO_LARGE` | 422 | 上传文件超限 |
| `UNSUPPORTED_FILE_TYPE` | 422 | 契約書仅收 JPEG / PNG / HEIC / PDF |
| `STORAGE_ERROR` | 500 | 文件保存失败（服务器侧） |

## 10. 扣分 · 处分（discipline.py；`EVENT_NOT_FOUND` 与行事域共用同名码）

| code | HTTP | 语义 |
|---|---|---|
| `EVENT_NOT_FOUND` | 404 | 扣分事件不存在（行事域同名码 = 行事不存在，message 各自） |
| `ALREADY_REVOKED` | 409 | 扣分事件已撤销 |
| `INVALID_MONTH` | 422 | month 须为 YYYY-MM 格式 |

## 11. 前台 · 宿舍生活 · 清扫 · 杂项申请（front_desk.py / dorm_life.py / cleaning.py / misc_requests.py）

| code | HTTP | 语义 |
|---|---|---|
| `ITEM_NOT_FOUND` | 404 | 前台项目（宅配等）不存在 |
| `WRONG_STATE` | 409 | 当前状态不允许该操作（前台状态机） |
| `NOT_PENDING` | 409 | 仅確認待ち可确认 |
| `CANNOT_DELIVER` | 409 | 仅已注文的申请可引き渡し |
| `CANNOT_RESUBMIT` | 409 | 仅被要求再提出的申请可再提出 |
| `ALREADY_INSPECTED` | 409 | 清扫安排已审核或跳过 |
| `CLEANING_NOT_FOUND` | 404 | 清扫安排不存在 |
| `SCHEDULED_IN_PAST` | 422 | 不可预定过去时刻 |
| `MISSING_REASON` | 400 | 不通过必须填 failure_reason |

## 12. 公告 · 行事 · 巴士 · 食堂 · 点歌 · 遗失物（announcements / events / bus_routes / meals / songs / lost_found）

| code | HTTP | 语义 |
|---|---|---|
| `BUS_ROUTE_NOT_FOUND` | 404 | 巴士便不存在 |
| `INVALID_KIND` | 400 | kind 取值不合法（巴士 / 前台共用参数校验码） |
| `INVALID_VISIBLE_TO` | 400 | visible_to 取值不合法 |
| `INVALID_CATEGORY` | 400 | 分类取值不合法 |
| `INVALID_DATE_RANGE` | 422 | 开始日晚于终了日 |
| `INVALID_TIME_RANGE` | 422 | 开始时刻晚于终了时刻 |
| `INVALID_RANGE` | 422 | 期间指定不合法（to 早于 from） |
| `RANGE_TOO_LARGE` | 422 | 期间超过 1 年上限 |
| `INVALID_STATUS` | 400 | status 取值不合法（open / resolved） |
| `INVALID_DORM` | 400 | dorm 取值必须是 1 / 2 / 4 |

## 13. 指导 · 事案（incidents.py / guidance.py）

| code | HTTP | 语义 |
|---|---|---|
| `INCIDENT_NOT_FOUND` | 404 | 事案不存在 |

## 14. 废止码（历史登记，禁止新代码使用）

| code | 废止时间 | 说明 |
|---|---|---|
| `TIMEOUT` | 2026-07-17 | 拍板②「迟到无截止」随 late_end 概念删除（`RollCall_Spec §5.3` 修订注）；结束后签到归 `SESSION_NOT_RUNNING`。后端已移除 |
| `SESSION_ENDED` | 2026-07-17 | 拍板③「改判无时限」废止「结束后禁改判」闸（`RollCall_Spec §11.3`）。**代码中尚存 1 处**（rollcall.py 改判闸），代码批删除后消失 |
| `UNAUTHORIZED` | 2026-07-17 | 从未被后端使用（审查 2-中-6）——鉴权失败一律 `INVALID_CREDENTIALS`，前端不必映射本码 |
| `OVERRIDE_TIME_LIMIT` | 2026-07-17 | 只存在于设计日志、从未实装；随拍板③时限矩阵废除一并废止 |
| `NOT_STARTED` / `ENDED` | 2026-04-17 | 语义被 `SESSION_NOT_RUNNING` 覆盖（4-17 修订记录保留） |

## 15. 修订记录

- 2026-04-17：移除 `NOT_STARTED` / `ENDED`；新增路径 A / B 设备相关码；文案按域分组。
- 2026-04-22：`UNREGISTERED_UID` 描述修正（S4）；§1 加 `ok=true` 无 `error` 字段约定（S19）。
- 2026-05-12：补 `NOT_YET_ALLOWED`（4-29 决策遗漏面）。
- 2026-07-17：全面改版为全项目字典（本页顶部说明）；废止 `TIMEOUT` / `UNAUTHORIZED` / `OVERRIDE_TIME_LIMIT`，`SESSION_ENDED` 废止预定。
