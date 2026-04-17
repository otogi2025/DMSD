# DMSD v0.1 字段字典（唯一命名）

更新时间：2026-04-17（4-17 修订基于 itsuki Q1-Q5 拍板，详见 `RollCall_Spec_v0.1.md` 附录 C）

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

## 3. 禁止字段（示例）
- `my_status`
- `my_base_status`
- `seat_status`
- `state`
- `background_status`（**4-17 废弃** — 统一为 `base_status`）

说明：
- 历史文档里出现的旧字段视为废弃，不得进入新代码。
