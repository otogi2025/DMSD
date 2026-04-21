# DMSD v0.1 字段字典（唯一命名）

更新时间：2026-04-21（4-21 修订：补 `card_uid` / `student_status` + 配套生命周期字段 — 对应 backlog S2 / S3）

## 1. 强制规则
- 同一概念只允许一个字段名。
- IA 与 API 必须逐字段一致。
- 禁止同义字段并存（例如：`my_status` 与 `my_base_status`，或 `background_status` 与 `base_status`）。

## 2. 核心字段（Canonical）

### 2.1 通用信封字段
- `ok`
- `data`
- `error`
- `code`
- `message`
- `detail`

### 2.2 身份与对象
- `session_id`
- `student_id`
- `teacher_id`
- `seat_no`
- `device_id`（**4-17 新增** — 详见 `DEVICE_REGISTRY_v0.1.md`）
- `card_uid`（**4-21 新增** — 路径 A 核心。NTAG215 UID 7 bytes hex 编码，存为 14 位小写 hex 字符串无分隔符。`UNIQUE` 约束。多对一到 `student_id`（换卡场景：旧 UID 作废记录保留 / 新 UID 绑定同一 `student_id`）。仅路径 A 使用。详见 2.9 卡生命周期 + `RollCall_Spec_v0.1.md §10.2`）

### 2.3 场次与时间
- `session_type`
- `session_status`
- `started_source`（**4-17 新增** — 取值见 ENUM `session_event_source`）
- `ended_source`（**4-17 新增** — 同上）
- `server_now`
- `scheduled_window_start_at`
- `scheduled_on_time_end_at`
- `scheduled_late_end_at`
- `scheduled_auto_end_at`
- `effective_window_start_at`
- `effective_on_time_end_at`
- `effective_late_end_at`
- `effective_auto_end_at`
- `started_at`
- `ended_at`
- `settle_at`
- `remaining_seconds`

### 2.4 点呼状态
- `base_status`（**4-17 修订** — 原 `background_status` 已废弃）
- `overlay_badges`
- `status_source`
- `status_reason`
- `path_type`（**4-17 新增** — 取值见 ENUM `path_type`）
- `applied_group`（**4-17 新增** — 取值同 `effective_group`）

### 2.5 健康与申请
- `health_issue`
- `no_show_request_status`

### 2.6 纪律
- `monthly_points`
- `discipline_action`
- `ledger_items`

### 2.7 改判审计
- `override_reason`
- `override_by`
- `override_at`

### 2.8 设备（**4-17 新增** — 详见 `DEVICE_REGISTRY_v0.1.md`）
- `device_type`（取值见 ENUM `device_type`）
- `device_location`（自由文本，描述设备物理位置如"寮舍 A 入口"）
- `device_active`（boolean，是否启用）
- `device_registered_at`
- `device_registered_by`
- `device_notes`（自由文本，硬件型号等）

### 2.9 卡生命周期（**4-21 新增** — 对应 backlog S2）
- `card_uid`（见 2.2）
- `card_active`（boolean。false = 卡已停用但历史记录保留，不删除 row）
- `card_issued_at`（发卡时间）
- `card_revoked_at`（作废时间；null = 仍在用）
- `card_revoke_reason`（自由文本："挂失补办" / "毕业回收" / "被停用" 等）

**幂等 / 唯一约束**（v0.6.0 migration 阶段落地）：
- `UNIQUE INDEX on (card_uid) WHERE card_revoked_at IS NULL` —— 同一时刻同一 UID 只能绑一个 active 学生
- 作废后 UID 可以重新绑定到新学生（毕业回收场景）

### 2.10 学生生命周期（**4-21 新增** — 对应 backlog S3 + `RollCall_Spec_v0.1.md` 附录 C.5）
- `student_status`（ENUM，取值见 `ENUM_REGISTRY_v0.1.md §14 student_status`）
- `student_status_changed_at`（最近一次变更时间）
- `student_status_changed_by`（操作老师 `teacher_id`）
- `student_status_change_reason`（自由文本）

**业务规则**（对应 spec 附录 C.5）：
- 仅 `active` 学生进入 session 座位表；其他状态保留名单但不计入
- 状态变更必须 audit（四个配套字段缺一不可）
- 毕业 / 转学学生数据永久保留（`student_status = graduated` / `transferred` 但 row 不删）

## 3. 禁止字段（示例）
- `my_status`
- `my_base_status`
- `seat_status`
- `state`
- `background_status`（**4-17 废弃** — 统一为 `base_status`）

说明：
- 历史文档里出现的旧字段视为废弃，不得进入新代码。
