# DMSD v0.1 字段字典（唯一命名）

更新时间：2026-02-12

## 1. 强制规则
- 同一概念只允许一个字段名。
- IA 与 API 必须逐字段一致。
- 禁止同义字段并存（例如：`my_status` 与 `my_base_status`）。

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

### 2.3 场次与时间
- `session_type`
- `session_status`
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
- `base_status`
- `overlay_badges`
- `status_source`
- `status_reason`

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

## 3. 禁止字段（示例）
- `my_status`
- `my_base_status`
- `seat_status`
- `state`

说明：
- 历史文档里出现的旧字段视为废弃，不得进入新代码。
