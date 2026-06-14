# DMSD v0.1 枚举字典（唯一取值）

更新时间：2026-04-22（4-22 修订：§13 `path_type` 加扩展性说明 — 对应 backlog S9）

## 1. session_type
- `morning`
- `evening`

## 2. session_status
- `draft`
- `running`
- `ended`

## 3. base_status

> **4-17 修订（Q1 A）**：原叫 `background_status`，统一为 `base_status`（与 `FIELD_REGISTRY.md` 一致）。
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
- `system`（系统兜底自动触发，如到达 `scheduled_window_start_at` / `scheduled_auto_end_at`）

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

## 12. device_type（4-17 新增 — 来自 `DEVICE_REGISTRY.md`）

- `card_reader`（路径 A 的卡读头：PN532 + 树莓派）
- `iphone_tag`（路径 B 的静态 NFC 标签：用于 iPhone 读取 `device_id`）
- `hybrid`（同台树莓派同时承载路径 A 卡读头 + 路径 B 静态标签）

## 13. path_type（4-17 新增 — 来自 `rollcall_event`）

- `A`（卡路径：卡 → 点呼机 PN532 → 后端）
- `B`（手机路径：iPhone / Android 读静态标签 → 手机自己发后端）

> **扩展性说明（2026-05-21 修订 — B-029 修复）**：
> - **v1.0 范围**（2026-04-19 G2 决策）：A/B 两个取值。Android 实现与 iOS 同型（NDEF 读静态标签 + 本机签名 + 自发后端），共用 `path_type=B`。
> - **未来扩展**：如果未来引入 Android HCE 主动上报路径（NFC 主动通信，跟 iOS Core NFC 被动读不同），**新起独立取值 `C`**，不扩展 A/B 语义。保持单字母单义。当前 backlog（TODO §🛠️）暂留 `C` 占位不实装。

## 14. student_status（4-21 新增 — 对应 `RollCall_Spec.md` 附录 C.5）

> **用途**：`student.student_status`。描述学生当前是否参与点呼。

| 取值 | 中文 | 含义 | 是否进入座位表 |
|---|---|---|---|
| `active` | 在寮 | 正常参与点呼 | ✅ |
| `paused` | 长期请假 | 请假期间（病假 / 留学 / 家庭原因），用"免点呼范围"覆盖（spec §8.2） | ❌（名单保留） |
| `transferred` | 转学 | 已转去别的学校 / 寮 | ❌ |
| `graduated` | 毕业退寮 | 毕业后离寮 | ❌ |

**状态转换规则**：
- 新入寮：null → `active`（首个 session 起计算）
- 长期请假：`active` → `paused`（请假期间免点呼）
- 请假结束：`paused` → `active`（回寮当天起恢复）
- 离寮：`active` / `paused` → `transferred` / `graduated`（此后 session 不再计入）
- 任意转换必须 audit：记录 `student_status_changed_at` + `student_status_changed_by` + `student_status_change_reason`（见 `FIELD_REGISTRY.md §2.10`）

**default**：`active`（新学生入寮默认为 active）

## 15. 大小写与拼写规则
- 全部采用小写蛇形或小写单词。
- 枚举值必须逐字匹配，不允许别名。
- 前后端代码直接拷贝本文件取值，禁止二次命名。
