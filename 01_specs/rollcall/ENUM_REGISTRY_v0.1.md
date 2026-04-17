# DMSD v0.1 枚举字典（唯一取值）

更新时间：2026-04-17（4-17 修订基于 itsuki Q1-Q5 拍板，详见 `RollCall_Spec_v0.1.md` 附录 C）

## 1. session_type
- `morning`
- `evening`

## 2. session_status
- `draft`
- `running`
- `ended`

## 3. base_status

> **4-17 修订（Q1 A）**：原叫 `background_status`，统一为 `base_status`（与 `FIELD_REGISTRY_v0.1.md` 一致）。
> `exempt_range` 归 base（不是 overlay），表示"学生当天根本不参与判定"，不是"签到了带个标记"。

- `init`
- `present`
- `late`
- `absent`
- `exempt_range`

## 4. overlay_badge

> **4-17 修订**：overlay 分两类。
> - **纯装饰型**：只叠加图标，不改底色，不参与底色优先级
> - **改底色型**：会强制 override 底色

- `health_issue`（**纯装饰型** — 红十字叠加，不改底色）
- `absence_request_pending`（**改底色型** — 强制底色为黑）

## 5. status_source

> **用途**：`rollcall_event`（签到事件）的来源。**不是** session 开始/结束的来源（那个用 §8 `session_event_source`）。

- `auto_nfc`
- `auto_settle`
- `manual_checkin`
- `teacher_override`

## 6. calendar_status
- `normal`
- `late`
- `absent`
- `overridden`
- `exempt`

## 7. no_show_request_status
- `pending`
- `approved`
- `rejected`

## 8. session_event_source（4-17 新增）

> **用途**：`rollcall_session.started_source` / `rollcall_session.ended_source`。
> 表示 session 的开始 / 结束事件由谁触发。

- `teacher`（老师手动按按钮）
- `system`（系统兜底自动触发，如到达 `scheduled_window_start` / `effective_auto_end_at`）

## 9. day_type（4-17 新增 — 原本只在 spec 主体出现，现写入字典）
- `weekday`
- `weekend_holiday`

## 10. student_group（4-17 新增 — 同上）
- `normal`
- `soccer`
- `unknown`

## 11. schedule_mode（4-17 新增 — 同上）
- `split`
- `merged_normal`

## 12. device_type（4-17 新增 — 来自 `DEVICE_REGISTRY_v0.1.md`）

- `card_reader`（路径 A 的卡读头：PN532 + 树莓派）
- `iphone_tag`（路径 B 的静态 NFC 标签：用于 iPhone 读取 `device_id`）
- `hybrid`（同台树莓派同时承载路径 A 卡读头 + 路径 B 静态标签）

## 13. path_type（4-17 新增 — 来自 `rollcall_event`）

- `A`（卡路径：卡 → 点呼机 PN532 → 后端）
- `B`（iPhone 路径：iPhone 读静态标签 → iPhone 自己发后端）

## 14. 大小写与拼写规则
- 全部采用小写蛇形或小写单词。
- 枚举值必须逐字匹配，不允许别名。
- 前后端代码直接拷贝本文件取值，禁止二次命名。
