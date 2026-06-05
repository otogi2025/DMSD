# Android 网络层 ↔ 后端 schemas.py 逐项对照

> **产出时间**：2026-06-05
> **对照双方**：对齐规格第 3 章「后端 API 契约」（= Android 网络层要照建的蓝图，源自 iOS）↔ 后端真值 `03_dev/backend/v1/app/schemas.py` + `app/routers/*.py`（实际路由路径）。
> **为什么这么对**：Android 现在网络层=零，要照规格从零建。规格源自 iOS、iOS 调的就是这个后端。所以核「规格 vs 后端」= 确认照规格建出来就跟后端对齐。
> **结论先行**：30 个学生端端点**路径全部一致**；字段**全部 snake_case 一致**；发现 **1 个真矛盾（密码长度）** + 2 处仅命名不同字段相同 + 几处 Optional/默认值细节。

---

## 一、端点路径逐项对照（规格 vs 后端实际路由）

| 用途 | 规格声称路径 | 后端实际（前缀+装饰器） | 响应 model | 路径一致 |
|---|---|---|---|---|
| 学生登录 | POST /api/v1/sessions/student | `auth.py` /api/v1/sessions + POST /student | TokenOut | ✅ |
| 学生注册 | POST /api/v1/accounts | `accounts.py` /api/v1/accounts + POST "" | StudentAccountCreateOut(201) | ✅ |
| 删自己账号 | DELETE /api/v1/accounts/me | `accounts.py` + DELETE /me | 204 | ✅ |
| 当前学生信息 | GET /api/v1/students/me | `student_profile.py` /api/v1 + GET /students/me | **StudentProfileBasic** | ✅ |
| 番号再设定 | POST /api/v1/students/me/renew-number | + POST /students/me/renew-number | StudentProfileBasic | ✅ |
| 当月扣分汇总 | GET /api/v1/discipline/me/summary | `discipline.py` /api/v1/discipline + GET /me/summary | MyDisciplineSummaryOut | ✅ |
| 公告列表 | GET /api/v1/announcements | `announcements.py` + GET "" | AnnouncementListOut | ✅ |
| 未读数 badge | GET /api/v1/announcements/unread-count | + GET /unread-count | AnnouncementUnreadCountOut | ✅ |
| 公告详情 | GET /api/v1/announcements/{id} | + GET /{announcement_id} | AnnouncementDetailOut | ✅ |
| 发回复 | POST /api/v1/announcements/{id}/replies | + POST /{id}/replies | AnnouncementReplyOut | ✅ |
| 删回复 | DELETE /announcements/{aid}/replies/{rid} | + DELETE | 204 | ✅ |
| 出寮届提交 | POST /api/v1/applications | `applications.py` + POST "" | ApplicationOut | ✅ |
| 我的申请一览 | GET /api/v1/applications/mine | + GET /mine | [ApplicationOut] | ✅ |
| 申请详情 | GET /api/v1/applications/{id} | + GET /{application_id} | ApplicationOut | ✅ |
| 修改届 | PUT /api/v1/applications/{id} | + PUT /{application_id} | ApplicationOut | ✅ |
| 改动履历 | GET /api/v1/applications/{id}/audit | + GET /{id}/audit | [AuditLogOut] | ✅ |
| 学習欠席届提交 | POST /api/v1/study/absence-requests | `study.py` /api/v1/study + POST /absence-requests | StudyAbsenceRequestOut | ✅ |
| 当月请假次数 | GET /study/absence-requests/me/summary | + GET /absence-requests/me/summary | MyAbsenceSummaryOut | ✅ |
| 在线学习提交 | POST /api/v1/study/online-requests | `study_online.py` /api/v1/study/online-requests + POST "" | StudyOnlineRequestOut | ✅ |
| 我的在线学习 | GET /study/online-requests/mine | + GET /mine | [StudyOnlineRequestOut] | ✅ |
| 契約書上传 | POST /study/online-requests/{id}/contract | + POST (multipart) | StudyOnlineRequestOut | ✅ |
| 行事企画提交 | POST /dorm-life/event-proposals | `dorm_life.py` /api/v1/dorm-life + POST | DormEventProposalOut | ✅ |
| 我的行事企画 | GET /dorm-life/event-proposals/mine | + GET /event-proposals/mine | [DormEventProposalOut] | ✅ |
| 冷蔵庫提交 | POST /dorm-life/fridge-purchases | + POST | FridgePurchaseRequestOut | ✅ |
| 我的冷蔵庫 | GET /dorm-life/fridge-purchases/mine | + GET .../mine | [FridgePurchaseRequestOut] | ✅ |
| 物品所持提交 | POST /dorm-life/item-possessions | + POST | ItemPossessionRequestOut | ✅ |
| 我的物品所持 | GET /dorm-life/item-possessions/mine | + GET .../mine | [ItemPossessionRequestOut] | ✅ |
| 巴士便列表 | GET /api/v1/bus/routes | `bus_routes.py` /api/v1/bus/routes + GET "" | BusRouteListOut | ✅ |
| 行事予定列表 | GET /api/v1/events | `events.py` /api/v1/events + GET "" | **DormEventListOut** | ✅ |
| 点呼 NFC 提交 | POST /rollcall/sessions/{id}/checkins | `rollcall.py` /api/v1/rollcall + POST /sessions/{id}/checkins | RollCallEventOut | ✅ |

**30 个端点路径 100% 一致。** 仅 2 处响应类名规格起的别名与后端不同（不影响线缆字段）：
- 规格叫 `StudentMeOut` → 后端实际 `StudentProfileBasic`
- 规格叫 `EventOut`/`EventListOut` → 后端实际 `DormEventOut`/`DormEventListOut`

---

## 二、关键数据模型字段对照（snake_case 逐字段）

### TokenOut（登录响应）✅
`access_token: str` / `token_type: "bearer"` / `expires_in: int` — 规格一致。

### StudentAccountCreateIn（注册请求体）⚠️ 1 处矛盾
| 字段 | 后端 schemas.py | 规格 | 一致 |
|---|---|---|---|
| name | str 1–100 必填 | 同 | ✅ |
| name_kana | str? ≤100 | 同 | ✅ |
| birthday | date?（yyyy-MM-dd） | 同 | ✅ |
| gender | "male"/"female" | 同 | ✅ |
| grade_code/class_code/seat_no | str 恰好 2 位数字 | 同 | ✅ |
| category | str 默认"一般寮生" | 同 | ✅ |
| room_no | str 3–8 字 | 同 | ✅ |
| dorm_unit | **Literal[1,2,4]** | 同（无 3） | ✅ |
| is_overseas | bool 默认 false | 同 | ✅ |
| email | EmailStr? ≤200 | 同 | ✅ |
| phone | str? ≤32 | 同 | ✅ |
| **password** | **str min_length=8** max 128 | 规格/iOS 本地校验写 **6–128** | ⚠️ **矛盾** |
| registration_code | str 恰好 6 位数字 | 同 | ✅ |

> ⚠️ **真矛盾**：后端要求密码 ≥8 位，但 iOS 本地校验（规格 ⑤ 节文案「パスワードは 6〜128 文字」）放行 6–7 位。后果：用户输 6–7 位密码，iOS/Android 本地校验过、后端 422 拒。这是 **iOS 也有的潜在 bug**。本对齐任务按「对齐 iOS」要求暂保留 6–128（文案一字不差），但**标记给 itsuki 决定**：要不要把三端 + 后端统一成 8–128。

### StudentProfileBasic（GET /students/me，规格叫 StudentMeOut）✅
后端字段：`id, student_no, name, name_kana?, grade_code, class_code, seat_no, gender, category, room_no, dorm_unit, is_overseas, email?, phone?, avatar_url?, status, registered_at, needs_renewal(默认false)`
- 与规格字段**全一致**。规格说 iOS 不接 `registered_at`（多余字段跳过，Android 同样无视即可）。
- `needs_renewal`：后端非可空默认 false；规格建议 Android 接成可空带默认（防分阶段部署解码崩），照规格做。

### ApplicationOut（出寮届，字段最多）✅
后端字段与规格逐字段一致：`id, student_id, student?, kind(帰省/外泊/帰国), leave_date, leave_method, leave_time, return_date, return_method, return_time, contact_phone?, meal_note?, stay_locations?, meals_skip?, companion?, dest_cities?, receipt_submitted, reason?, is_long_vacation, flight_dep_air?, flight_dep_at?, flight_arr_air?, flight_arr_at?, taxi_reservation_time?, bus_route_id?, submitted_at, status, withdrawn_at?, approval_chain[]`
- 细节：`receipt_submitted` / `is_long_vacation` 后端是 `bool` 带默认（规格写 Bool?）。Android 接成带默认 false 的 Bool 即可，无碍。
- 三种提交体 `KisheiCreateIn`/`GaihakuCreateIn`/`KikokuCreateIn` 字段与规格一致；后端用 `discriminator="kind"` 按日文 kind 分派 → Android 直接发日文 kind。
- `ApplicationUpdateIn`：全字段 Optional + 多 `amend_reason` ✅，与规格一致；Android 序列化**必须跳 null**（否则误清空）。

### StudyAbsenceRequestOut / StudyOnlineRequestOut ✅
- 欠席：`id, student_id, target_date, period(first_half/second_half/full), reason, submitted_at, status, decided_by?, decided_at?, comment?` ✅
- 在线学习：`id, student_id, reason, period_from, period_to, weekly_schedule(dict), contract_ref?, contract_file_name?, contract_mime?, contract_size?, submitted_at, status, decided_by?, decided_at?, comment?` ✅（不含服务器物理路径，安全）

### DormEventProposalOut / FridgePurchaseRequestOut / ItemPossessionRequestOut ✅
三个生活申请响应字段与规格逐字段一致。注意：行事企画的状态字段叫 `result`（不是 status），值 pending/approved/approved_conditional/resubmit/rejected ✅。

### BusRouteOut / DormEventOut（行事予定）✅
- 巴士：`id, kind(daily_commute/dorm_special), name, direction, schedule_at, arrival_at?, visible_to, note?, deprecated, created_by_teacher_id, created_at, updated_at?` ✅，列表包 `{items:[...]}`
- 行事予定（DormEventOut，规格叫 EventOut）：`id, title, category, event_date(纯日期保字符串), start_at?, end_at?, description?, created_by_teacher_id, created_at, updated_at?` ✅，列表包 `{items:[...]}`

### Announcement 组 ✅
- `AnnouncementBrief`：`id, title, body_summary, scope(all/male/female), author_teacher_id, author_teacher_name, created_at, updated_at, is_read, reply_count` ✅
- `AnnouncementDetailOut`：+ `body` 全文 + `replies[]` ✅
- `AnnouncementReplyOut`：`id, author_kind(student/teacher), author_id, author_name, body, created_at` ✅
- `AnnouncementUnreadCountOut`：`unread_count` ✅

### RollCallCheckinIn / RollCallEventOut ✅
- 请求体：`card_uid?, student_id?, idempotency_key?, status_source(默认auto_nfc), ts_local?, path_hint?(A/B/manual)` ✅
- 响应：`id, student_id, base_status, status_source, checked_in_at, path_type?` ✅
- ⚠️ 真实 NFC 签到链路依赖**防作弊核心后端（未写）**：nonce / ECDSA 签名 / 设备注册 / 卡→学生映射。Android 侧点呼只能先做 UI，真实联网签到**记 TODO**。

### MyDisciplineSummaryOut / MyAbsenceSummaryOut ✅
- 扣分汇总：`month, total_points(float！可能 0.5), late_count, absent_count` ✅
- 请假汇总：`month, count` ✅

---

## 三、对照结论 + 给 itsuki 的待决项

1. ✅ **30 端点路径全一致、字段全 snake_case 一致** —— 照规格第 3 章建 Android 网络层 = 跟后端对齐，蓝图可信。
2. ⚠️ **密码长度矛盾**（后端 8 / iOS 6）—— 待 itsuki 决定是否统一成 8。本次按对齐 iOS 暂保留 6。
3. 📝 **防作弊核心后端未写** —— 点呼真实签到链路 Android 只做 UI，联网部分记 TODO。
4. 细节（Optional/默认值）已在各模型注明，Android 数据类按「漏接非空字段会整段解码崩」原则，所有字段一个不漏 + 可空字段写 `Type?`。
