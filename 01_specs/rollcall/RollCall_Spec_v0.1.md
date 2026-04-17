# RollCall Spec v0.1（点呼仕様）

> **v0.1 初版冻结**：2026-02-12（来源 `.pages` 原稿）
> **v0.2 主体改写**：2026-04-17 晚（双路径并存 / Q1-Q5 决策落地 / 附录 B 漏洞收口）
> **当前文件状态**：spec 主体已对齐 4-17 决策；`.pages` 原稿仅作历史快照保留
> **权威来源**：本 `.md` 是唯一真值，与字典四件套（ENUM/FIELD/ERROR_CODES/DEVICE_REGISTRY）相互引用

---

## 1. 概述

DMSD 点呼系统支持 **双路径并存**：

| 路径 | 触发方式 | 上线节奏 |
|---|---|---|
| **路径 A — NFC 卡** | 学生把卡贴到点呼机的 PN532 读头 | **Phase 1**（先上线，不需要学生 App）|
| **路径 B — iPhone 静态标签** | 学生 iPhone 读点呼机外贴的静态 NFC 标签 | **Phase 2**（追加，与卡共存；Android 方案另议）|

两条路径都遵循同一个业务流程：

1. 老师从管理网站（タブレット）查看座席表，按 **「点呼開始」** 按钮开启点呼场次
2. 学生在时间窗内通过 **路径 A 或路径 B** 触发签到
3. 签到事件由 **服务器** 唯一判定（准时 / 迟到 / 缺席 / 拒绝）
4. 老师管理网站的对应座位颜色实时变化（灰 / 绿 / 黄 / 红 / 黑），通过 WebSocket 推送
5. 老师在场监督（**Phase 1 防代签的关键人防补偿**，详见 §9 + 附录 B.1）

**架构原则（4-15 拍板）**：
- **thin client / thick server**：点呼机只搬运数据（读 NFC + HTTP 发后端 + 听 WebSocket + 播报 + 亮灯），**业务判断全在后端**
- **服务器是唯一判定者**：是否在窗口内 / 准时还是迟到 / 是否结算缺席 —— 全由服务器以 `server_now (JST)` 为准
- **客户端时间不参与判定**，只用于 UI 展示

详细协议契约见 `DEVICE_REGISTRY_v0.1.md` + `ENUM_REGISTRY_v0.1.md` §12-13（`device_type` / `path_type`）。

---

## 2. 座位颜色定义

> **4-17 修订（Q1 A）**：`exempt_range` 从"叠加角标"改为 `base_status`。
> 因为"免"表示"学生当天根本不参与判定"（结构上和 init/present/late/absent 同级），不是"签到了带个标记"。
> 字典见 `ENUM_REGISTRY_v0.1.md` §3-4。

### 2.1 底色（`base_status` — 五选一）

| 颜色 | 状态值 | 含义 |
|------|--------|------|
| 灰 | `init` | 初始（未签到） |
| 绿 | `present` | 准时出席 |
| 黄 | `late` | 迟到出席 |
| 红 | `absent` | 缺席 |
| 绿 | `exempt_range` | 事先申请免点呼（如外泊），不参与判定 |

### 2.2 叠加角标（`overlay_badges` — 可多选）

> overlay 分两类：**纯装饰型**（不改底色） vs **改底色型**（强制 override 底色）。

| 标记 | 状态值 | 类型 | 含义 |
|------|--------|------|------|
| 红十字 | `health_issue` | 纯装饰型 | 健康状态异常（不改底色，永远叠加显示）|
| 申（黑底） | `absence_request_pending` | 改底色型 | 本场不参加申请，待老师处理（强制底色变黑）|

### 2.3 显示规则

- **`health_issue`（红十字）**：永远叠加显示，不改变底色，不参与底色优先级排序
- **`absence_request_pending`（申）**：强制底色变黑，覆盖任何 `base_status`
- 任何 `base_status` 都允许同时叠加 `health_issue`（红十字）
- 当 `absence_request_pending` 存在时仍可同时叠加 `health_issue`（黑底 + 红十字）

### 2.4 底色优先级（从高到低）

1. `absence_request_pending`（黑 — overlay 强制 override）
2. `absent`（红）
3. `late`（黄）
4. `exempt_range`（绿）
5. `present`（绿）
6. `init`（灰）

> 多个 `base_status` 不会同时存在（互斥）。
> 上面的优先级在以下场景适用：
> - 老师手动改判时若曾经 settle 过，需要按优先级决定显示
> - 老师审批"申"为"拒绝"时：移除 `absence_request_pending` → 底色变 `absent`
> - `health_issue` 始终叠加显示，不参与排序

---

## 3. 座位点击弹窗显示项

### 3.1 基本信息
- `student_id`
- `student_name`
- `seat_id`

### 3.2 本场信息
- `session_type`：`morning` / `evening`
- `day_type`：`weekday` / `weekend_holiday`
- `device_id`（本场签到来自哪台点呼机；详见 `DEVICE_REGISTRY_v0.1.md`）
- `path_type`：`A`（卡）/ `B`（iPhone 静态标签）

### 3.3 本场结果信息
- `base_status`（出席状态 — 取值见 ENUM `base_status`）
- `overlay_badges`（叠加角标 — 数组，取值见 ENUM `overlay_badge`）
- `checked_in_at`（签到时间）
- `server_time`（服务器时间）
- `applied_group`（本次判定使用的 `effective_group`，详见 §6.4）
- 健康内容（如有）
- 缺席理由（红色时）
- 申请审批结果（同意 / 拒绝）

### 3.4 手动改判记录（如有）
- `operator_id`
- `operate_at`
- `from_status` → `to_status`
- `reason`（必填）
- `evidence`（可选）

### 3.5 老师可执行的操作
- 设置点呼状态为 **准时**
- 设置点呼状态为 **迟到**
- 设置点呼状态为 **缺席**
- **承认 / 否认** 本场点呼免除申请
- 设置学生的点呼免除期间

> ⚠️ **所有手动操作必须填写理由（`reason`），并作为审计记录保存到服务器。**

---

## 4. 点呼时刻表

### 4.1 学生侧时刻表（"几点必须到"）

#### 早点呼（morning）

| 日期类型 | 普通寮生 | 足球部 |
|----------|----------|--------|
| 平日（weekday） | 7:40 | 7:20 |
| 祝休日（weekend_holiday） | 8:50 | 7:20 |

#### 晚点呼（evening）

| 日期类型 | 普通寮生 | 足球部 |
|----------|----------|--------|
| 平日（weekday） | 22:00 | 22:00 |
| 祝休日（weekend_holiday） | 20:00 | 20:00 |

### 4.2 老师侧时刻表（"几点按开始钮 / 几点起算迟到"）

#### 早点呼（morning）

| 日期类型 | 对象 | 开始按钮 | 准时截止 |
|----------|------|----------|----------|
| 平日 | 普通寮生 | 7:37 | 7:40:00 |
| 平日 | 足球部 | 7:17 | 7:20:00 |
| 祝休日 | 普通寮生 | 8:47 | 8:50:00 |
| 祝休日 | 足球部 | 7:17 | 7:20:00 |

#### 晚点呼（evening）

| 日期类型 | 对象 | 开始按钮 | 准时截止 |
|----------|------|----------|----------|
| 平日 | 普通寮生 | 21:57 | 22:00:00 |
| 平日 | 足球部 | 21:57 | 22:00:00 |
| 祝休日 | 普通寮生 | 19:57 | 20:00:00 |
| 祝休日 | 足球部 | 19:57 | 20:00:00 |

> 老师在 **「准时截止」前 3 分钟** 按下「点呼開始」按钮，学生才能开始签到。
> 在「准时截止」之前签到 = 准时（绿）；之后 = 迟到（黄）。

---

## 5. 系统逻辑

### 5.1 签到信号流（路径 A vs 路径 B）

> **共同前提**：服务器是唯一判定者；client/iPhone/卡的本地时间均不参与判定；`device_id` 必须先在 `DEVICE_REGISTRY` 注册。

#### 5.1.1 路径 A — NFC 卡（Phase 1 主推）

```
学生卡 ──贴近──> 点呼机 PN532 读头
                 │
                 ├─ 1. 读到卡 UID
                 ├─ 2. POST /api/v1/checkin
                 │     {device_id, uid, ts_local}     ← 仅搬运，无判定
                 ▼
              后端
                 │
                 ├─ 3. 校验：device_active / UID 绑定 / session running / 时间窗
                 ├─ 4. 判定：present/late/duplicate/timeout/...
                 ├─ 5. 写 attendance_event (append-only)
                 ├─ 6. WS 推送 → 老师端座位点亮
                 ▼
              返回点呼机：
                 ├─ 成功 → 学生姓名 + 状态 → 点呼机播报"张三 准时" + 绿灯
                 └─ 失败 → 错误码 → 点呼机红灯 + 失败声音
```

#### 5.1.2 路径 B — iPhone 静态标签（Phase 2 追加，与路径 A 共存）

```
学生 iPhone ──贴近──> 点呼机外贴静态 NFC 标签
                       │
                       ├─ 1. iPhone Core NFC 读到 device_id
                       ▼
                    iPhone App
                       │
                       ├─ 2. App 取一次性 nonce（预取池或在线获取）
                       ├─ 3. 用本机私钥 ECDSA 签名 (session_id || device_id || nonce || ...)
                       ├─ 4. POST /api/v1/checkin (WiFi/4G 自己发，不经过点呼机)
                       │     {student_id, device_id, ts_local, signature, nonce, idempotency_key}
                       ▼
                    后端
                       │
                       ├─ 5. 校验：签名 / nonce / device_active / session running / 时间窗
                       ├─ 6. 判定：present/late/...
                       ├─ 7. 写 attendance_event
                       ├─ 8. WS 推送 → 老师端座位点亮
                       └─ 9. WS 推回点呼机 → 播报"张三 准时" + 绿灯
                       ▼
                    iPhone App 收到响应 → 本地展示结果
```

**关键差异**：
- 路径 A 的 device 是 **主动通信节点**（带 PN532 + 树莓派），device_id 写在配置里
- 路径 B 的 device 是 **被动 NFC 标签**，仅供 iPhone 读取拿 device_id；iPhone 自己发后端
- 同一台树莓派可同时承载 A 卡读头 + B 静态标签 → `device_type = hybrid`（详见 `DEVICE_REGISTRY_v0.1.md` §3.3）

#### 5.1.3 防代签（Phase 1 关键人防补偿）

NFC 卡固有弱点：卡可被转交。技术不能完全防代签 → **必须靠老师在场监督**：
- 老师站在点呼机旁边，目视学生本人碰卡
- 听点呼机播报姓名 → 对照人脸（"张三 准时" + 看到张三本人）
- spec 把这条作为 Phase 1 的 **硬约束** 写入，不是建议（详见附录 B.1）

Phase 2 路径 B 通过 device 绑定 + 签名 + 单设备策略缓解（但仍无法 100% 防"借手机"）。

### 5.2 开始与结束流程

1. 老师到点呼室，在管理网站按 **「点呼開始」** 按钮 → 学生才能开始签到
2. 学生比老师先到也无法签到（按钮没按 = 系统返回 `SESSION_NOT_RUNNING`）
3. 老师按 **「点呼終了」** 按钮 → 仍未签到的学生座位变红（`absent`）

### 5.3 时间窗结构（写死规则）

每场点呼有 4 个关键时刻：

```
window_start  →  on_time_end  →  late_end  →  auto_end_at
（开始可签到）   （准时截止）    （迟到截止）   （系统兜底自动结束）
```

约束：

- `window_start < on_time_end < late_end ≤ auto_end_at`
- `late_end = on_time_end + 1 秒`
- `auto_end_at = on_time_end + X 分钟`（X 待最终确定，详见附录 A.3）

### 5.4 老师"提前开始"与窗口平移

如果老师在 `scheduled_window_start` 之前点击开始：

- `started_at = server_now`
- `started_source = teacher`
- 整个窗口 **整体平移**（保持时长不变）：

```
effective_window_start = started_at
effective_on_time_end  = started_at + (scheduled_on_time_end  - scheduled_window_start)
effective_late_end     = started_at + (scheduled_late_end     - scheduled_window_start)
effective_auto_end_at  = started_at + (scheduled_auto_end_at  - scheduled_window_start)
```

判定时使用 `effective_*`，不使用 `scheduled_*`。

> ⚠️ 此规则会导致老师提前开始时，准时截止时间也提前。是否符合实际意图？详见附录 A.4。

### 5.5 自动开始 / 自动结束（系统兜底）

**自动开始**

到达 `scheduled_window_start` 时，老师仍未按开始 → 系统自动开始：

- `started_at = scheduled_window_start`
- `started_source = system`（取值见 ENUM `session_event_source`）

如果系统已自动开始后老师再按 **「点呼開始」** → 返回 `ALREADY_RUNNING`，不变更状态。

**自动结束**

到达 `effective_auto_end_at` 时，老师仍未按结束 → 系统自动结束并结算：

- `ended_at = effective_auto_end_at`
- `ended_source = system`

> 老师端在到点前的提醒由前端自行实现，但即使老师没注意到，系统兜底也会触发。

---

## 6. 选择规则与适用对象

### 6.1 `day_type` 计算（优先级写死）

1. 当前日期命中 **节假日表** → `weekend_holiday`
2. 否则当前是 **周六/周日** → `weekend_holiday`
3. 否则 → `weekday`

> 节假日表由老师后台维护。所有日期/时间判断使用 **JST**。

### 6.2 `student_group`（学生分组）

| 值 | 含义 |
|----|------|
| `normal` | 普通寮生 |
| `soccer` | 足球部 |
| `unknown` | 未分类 / 资料缺失 |

- 学生注册时可自选，但 **以老师端学生档案为准**
- 老师可在后台修改，所有变更必须留档
- 档案缺失 → `raw_student_group = unknown`
- `unknown` 按 `normal` 计算，并在老师端显示「未分类」标记提醒补齐

### 6.3 `schedule_mode`（本场点呼模式）

| 值 | 含义 |
|----|------|
| `split` | 分组点呼（普通走普通时间窗，足球走足球时间窗） |
| `merged_normal` | 合并到普通（全员按普通时间窗判定） |

### 6.4 `effective_group`（本场实际用于算时间窗的分组）

```
若 schedule_mode == merged_normal  →  effective_group = normal
若 schedule_mode == split          →  effective_group = raw_student_group
若 effective_group == unknown      →  按 normal 计算
```

### 6.5 时间窗查找

- 用三元组 `(session_type, day_type, effective_group)` 查时间窗表
- 得到该场的 `window_start` / `on_time_end` / `late_end` / `auto_end_at`

### 6.6 约束

- 时间窗表必须覆盖所有组合，否则视为配置错误，阻止开始（返回 `no_rollcall_for_today`）
- `schedule_mode` 只能在本场开始前设置；`started_at` 写入后锁定
- 修改 `schedule_mode` 必须留档

> 如果制度上 **足球部在祝休日没有早点呼**，可标注该组合不创建 morning session。
> 即使如此，建议保留 soccer 行作为 split 模式备用。

---

## 7. 判定逻辑

判定时间 `t` = **服务器收到签到请求的时间**（JST）。
判定时使用 `effective_*`（已考虑老师提前开始的窗口平移）。

| 判定 | 条件 |
|------|------|
| `present`（绿） | `effective_window_start ≤ t ≤ effective_on_time_end` |
| `late`（黄） | `effective_on_time_end < t ≤ effective_late_end` |
| `absent`（红） | 到结算时刻仍未签到（见第 8 节） |

### 边界情况

> 所有错误码定义见 `ERROR_CODES_v0.1.md`。

- **`t > effective_late_end` 的签到**：返回 `TIMEOUT`，不改变座位结果，最终由结算置为缺席
- **`started_at` 之前 / `ended_at` 之后的签到**：返回 `SESSION_NOT_RUNNING`（统一覆盖"还没开始"和"已结束"两种情况）
- **重复签到**（同一 `student_id` 在同一 session 内已签到）：返回 `DUPLICATE_REQUEST`，silently ignore（不变更状态、不重复播报，但记 audit log）
- **未注册卡 / 陌生 UID**（路径 A）：返回 `UNKNOWN_CARD`，点呼机红灯 + 失败声音 + 不播报姓名
- **卡未启用**（路径 A，UID 在表里但 `device_active=false` 或学生离寮）：返回 `UNREGISTERED_UID`
- **未注册设备**（路径 B，iPhone 发的 `device_id` 不在 device 表里）：返回 `UNKNOWN_DEVICE`
- **设备已停用**：返回 `DEVICE_NOT_ACTIVE`
- **签名校验失败**（路径 B）：返回 `INVALID_SIGNATURE`
- **配置缺失**（时间窗表无对应 `(session_type, day_type, effective_group)` 组合）：返回 `NO_ROLLCALL_FOR_TODAY`，阻止 session 创建

---

## 8. 结算规则

### 8.1 结算时刻

```
settle_at = min(ended_at, effective_auto_end_at)
```

到达 `settle_at` 时：

> **将仍为 `init` 且 `base_status ≠ exempt_range` 且不存在 `absence_request_pending` overlay 的座位，置为 `absent`。**

### 8.2 `exempt_range` 的结算（4-17 修订：`exempt_range` 现为 `base_status`，不是 overlay）

- session 创建时，由后台根据"免点呼范围表"把符合条件的学生 `base_status` 直接初始化为 `exempt_range`
- 这些座位 **不参与缺席结算**
- 即使到 `settle_at` 也不会被置为 `absent`
- 座位显示保持 **`exempt_range`（绿色）**
- 本场统计单列 `exempt_count`
- `exempt_range` 不计入 `present` / `late` / `absent` / `init`

### 8.3 `absence_request_pending`（申）的结算

- 带有 `absence_request_pending` overlay 的座位 **不自动置为 `absent`**
- 座位显示保持 **黑底**（overlay 强制 override base_status）
- 本场统计单列 `pending_request_count`
- `pending_request` 不计入 `present` / `late` / `absent` / `init` / `exempt_range`
- 老师审批后才落最终结果：
  - **同意** → 移除 `absence_request_pending` overlay → `base_status` 变为 **`exempt_range`（绿色）**
  - **拒绝** → 移除 `absence_request_pending` overlay → `base_status` 变为 **`absent`（红色）**，按制度扣分

---

## 9. 系统组件职责（thin client / thick server）

> **核心原则（4-15 拍板）**：点呼机只搬运数据，业务判断全在后端。改规则只改后端一处；设备越蠢越安全。

| 组件 | 负责 | 不负责 |
|------|------|--------|
| **学生 iPhone App**（路径 B / Phase 2）| Core NFC 读静态标签拿 `device_id`；本机 P-256 ECDSA 签名；POST 发后端；展示结果与错误提示 | 颜色判定；最终结算；时间窗判定 |
| **老师端管理页面**（iPad）| 开始/结束点呼（按按钮触发 session_event）；查看座位颜色与统计；手动改判（reason 必填）；处理「申」审批；Device 注册管理 | 判定逻辑；自动结算逻辑 |
| **点呼机：路径 A `card_reader`** | 读 NFC 卡 UID；HTTP 发后端；听 WebSocket；播报姓名/状态；亮灯 | 不保存学生身份；不查表；不判定准时/迟到 |
| **点呼机：路径 B `iphone_tag`**（被动标签）| 把 `device_id` 暴露给 iPhone 读取 | 不通信；不参与流程 |
| **点呼机：路径 A+B `hybrid`**（同台树莓派）| 同时承载卡读头（A）+ 静态标签（B）；卡通信由 PN532 负责，iPhone 通信不经过点呼机 | 同上 |
| **服务器** | **唯一判定者**：session 是否 running / 时间窗内 / 准时/迟到 / 缺席<br>**唯一结算者**：到 `settle_at` 把符合条件的座位置为 `absent`<br>**唯一信息源**：老师端实时状态由服务器 WebSocket 推送<br>**Device 守门人**：所有 `device_id` 必须先在 `DEVICE_REGISTRY` 注册并 `device_active=true` | — |
| **老师本人（人防）** | Phase 1 防代签的关键：站点呼机旁监督；听播报对照人脸；异常时立即手动改判 | （非系统职责，但是 Phase 1 的硬约束）|

### 时间基准

- 判定时间使用 **服务器收到请求的时间** `server_now`
- 时区固定为 **JST**
- 客户端时间 **不参与判定**，只用于 UI 展示

### Device 注册

详见 `DEVICE_REGISTRY_v0.1.md`：
- 所有签到 API 必须传 `device_id`
- 未注册 → `UNKNOWN_DEVICE`；已停用 → `DEVICE_NOT_ACTIVE`
- Q3 决策：**部署 4 台**（具体位置 + 物理布局 Q4 待定）

---

## 10. 数据模型与字段（关键补充）

> 完整字段定义见 `FIELD_REGISTRY_v0.1.md`。本节只列 spec 主体相关的关键字段。

### 10.1 `rollcall_session`（点呼场次）

| 字段 | 类型 | 说明 |
|---|---|---|
| `session_id` | UUID | 主键 |
| `session_type` | enum | `morning` / `evening` |
| `session_status` | enum | `draft` / `running` / `ended` |
| `schedule_mode` | enum | `split` / `merged_normal`；默认 `split` |
| `started_at` | timestamp | 实际开始时间（JST）|
| `started_source` | enum | `teacher` / `system`（取值见 ENUM `session_event_source`）|
| `ended_at` | timestamp | 实际结束时间 |
| `ended_source` | enum | 同 `started_source` |
| `scheduled_window_start_at` 等 4 个 | timestamp | 计划时间窗 |
| `effective_window_start_at` 等 4 个 | timestamp | 老师提前开始后平移过的实际判定区间（必须保存）|
| `settle_at` | timestamp | `min(ended_at, effective_auto_end_at)` |

### 10.2 `rollcall_event`（签到事件 — append-only）

| 字段 | 类型 | 说明 |
|---|---|---|
| `event_id` | UUID | 主键 |
| `session_id` | FK | 关联场次 |
| `student_id` | FK | 学生 |
| `device_id` | FK | 来自哪台点呼机（详见 `DEVICE_REGISTRY_v0.1.md`）|
| `path_type` | enum | `A`（卡）/ `B`（iPhone 静态标签）|
| `base_status` | enum | 判定结果 |
| `status_source` | enum | `auto_nfc` / `auto_settle` / `manual_checkin` / `teacher_override` |
| `applied_group` | enum | 本次判定使用的 `effective_group`（`normal` / `soccer`），用来解释"足球部当天合并点呼为什么按普通时间窗算" |
| `checked_in_at` | timestamp | 服务器接收时间 = 判定时间 |
| `idempotency_key` | string | 客户端生成 UUID，防重提 |

### 10.3 `device`（设备表）

详见 `DEVICE_REGISTRY_v0.1.md`。spec 主体只引用 `device_id` 与 `device_active` 两个字段。

### 10.4 字段一致性约束

- `base_status` 取值必须来自 `ENUM_REGISTRY` §3
- `overlay_badges` 数组元素必须来自 `ENUM_REGISTRY` §4
- 所有错误码必须来自 `ERROR_CODES_v0.1.md`
- 判定使用 `effective_*`，结算使用 `effective_auto_end_at`，查表使用 `(session_type, day_type, effective_group)`

---

## 11. 老师端手动操作 — 留档硬规则

### 11.1 每次操作必须记录的字段

- `operator_id`
- `operate_at`（服务器时间 JST）
- `operation_type`
- target：`session_id` + `seat_id` 或 `student_id` 或 `request_id`
- `from_status` → `to_status`
- `reason`（必填）
- `evidence`（可选）

### 11.2 硬规则

- `reason` 为空 → **不允许提交**
- 记录 **只追加，不允许修改**

### 11.3 改判时限矩阵（4-17 新增 — 收口附录 B.9）

涉及金钱/处分的字段必须有时间窗约束。规则：**角色 × 时间** 的二维矩阵。

| 字段类型 | 可改时限 | 角色 | 留痕要求 |
|---|---|---|---|
| 备注 / 改判理由（非状态字段）| 无限制 | 所有老师 | 修改历史 |
| 出勤状态改判 | ≤ 7 天 且 当月月结前 | 所有老师 | 必填 reason |
| 出勤状态改判 | 8-30 天 | 仅舍监 | 必填 reason + 舍监签字 |
| 出勤状态改判 | > 30 天 | **只读** | 走「追溯申请」独立流程（v0.3 设计）|
| 已发处分名单对应的 session | 原则只读 | — | 若必改需撤销处分通知 + 重新发放 |
| 纪律分（月汇总产出后）| 只读 | — | 修正只能下月补扣 / 补还 |

### 11.4 改判与扣分联动（4-17 新增 — 收口附录 B.9）

| 改判方向 | 自动扣分动作 | ledger 记录 |
|---|---|---|
| `present` → `late` | 自动 +0.5 分 | `type=adjust_late` |
| `present` → `absent` | 自动 +1.0 分 | `type=adjust_absent` |
| `late` → `present` | 自动 -0.5 分（回退）| `type=reverse_late` |
| `late` → `absent` | 自动 +0.5 分（差值）| `type=adjust_absent` |
| `absent` → `present` | 自动 -1.0 分（回退）| `type=reverse_absent` |
| `absent` → `late` | 自动 -0.5 分（差值）| `type=adjust_late` |
| 任意 → `exempt_range` | 之前自动加的分全回退 | `type=reverse_*` |

> 老师改判 = 改 status；扣分自动跟随；不允许"只改状态不改分"或"只改分不改状态"（避免审计断链）。
> 所有 ledger 条目都关联 `override_at` + `override_by` + `reason`。

---

## 附录 A — 整理时发现的问题（待 itsuki 确认）

> 这些问题在整理 `.pages` 原稿到 Markdown 的过程中发现，列出来供后续修订参考。

### A.1 Phase 1 与 spec 的脱节

- 本 spec 假设 **学生用手机 App 触碰点呼机** 签到（即 Phase 2 路径 B）
- 但 4-12 决定的 **Phase 1** 是 **NFC 卡 + 点呼机直读**，没有手机 App
- Phase 1 上线时的「签到方式」与 spec 描述不一致 → v0.2 spec 补完时需要解决（参见 WIP 中"补点呼机契约 spec"任务）

### A.2 早点呼祝休日 — 足球部时间（当前假设：故意如此，待 itsuki 最终确认）

- 平日：足球部 7:20，普通 7:40 ✅
- 祝休日：足球部 7:20，普通 8:50 ⚠️
- **当前假设**：故意如此 —— 足球部祝休日有训练，所以早点呼时间与平日相同（7:20）
- **依据**：日本高中足球部常见安排（祝休日上午训练/比赛）
- **⏳ 待 itsuki 最终确认**：
  - 确认"故意如此" → 把本段 "A.2" 升级为 spec 主体 §4.1 的一条说明，移出附录
  - 发现其实是"手滑"/"足球部祝休日无早点呼" → 改成 "祝休日 soccer 不安排 morning session"（并调整 §6.5 时间窗表）

### A.3 时间窗 X 分钟未定值

- `auto_end_at = on_time_end + X 分钟`
- **X 的具体值还没定**（候选：5 / 10 / 15 / 30）
- 这个值决定了：老师忘记按结束钮时，系统多久兜底结算

### A.4 老师"提前开始"窗口平移规则可能反直觉

当前规则：老师提前按开始钮 → 整个窗口（含准时截止）一起前移。

举例：晚点呼平日，scheduled `window_start = 21:57`、`on_time_end = 22:00`。
若老师 21:50 按下开始钮：

```
effective_window_start = 21:50
effective_on_time_end  = 21:50 + 3min = 21:53
```

→ 学生在 21:54 签到 = LATE（即使原计划 22:00 才迟到）

**疑问**：这是不是老师想要的？如果老师"提前开始"只是为了让学生能更早签到，但准时截止仍按 22:00 算，那就不该平移 `on_time_end`。
建议确认实际场景。

### A.5 已修正的日文打字错误

CC 在整理时已修正以下打字错（如原稿是有意这么写，请告知，可恢复）：

| 原文 | 修正为 |
|------|--------|
| `おす` | `押す` |
| `２２：００人ってから遅刻になる` | `22:00 入ってから遅刻になる` |
| `チェックインした生徒とまだ来てない生徒が欠席になる` | `チェックインしてない生徒` |

### A.6 颜色优先级有两套写法（已合并）

原稿前后出现两处优先级定义，**顺序不同**：

- 前段：`1.免  2.申  3.赤  4.黄  5.緑`
- 后段：`申(黑) 免(绿) ABSENT(红) LATE(黄) PRESENT(绿) INIT(灰)`

CC 整理时采用 **后段（详细版）**，因为它包含 `INIT` 且与 8.3 节"申"逻辑一致（申待处理 = 黑色 = 最高优先级）。
请确认是否正确，如有冲突请指正。

### A.7 「点呼机外贴 NFC 标签」的位置概念

第 9 节里写「点呼机（NFC）负责提供 `reader_id` 或 `tag_id` 让手机碰一下触发签到」。

这与 4-15 讨论的 Phase 2 路径 B 设计 **一致**：
- 点呼机外贴静态 NFC 标签（含 `device_id`）
- 学生 iPhone 读这个标签拿到 `device_id` → 自己用 WiFi/4G 发 `{student_id, device_id, ts, 签名}` 给后端

✅ 这一项不是问题，只是确认 spec 与 4-15 架构是一致的。

---

## 附录 B — 深度审查发现的 spec 漏洞 / 缺失

> CC 在整理后做了一轮深度审查，下面是 **业务规则漏洞** / **未定义场景** / **可能的实现问题**。
> 这些不一定是 bug，但会在实现时变成 bug 或争议点。
> 按优先级排序——🔴 Phase 1 开工前必须解决；🟡 强烈建议；🟢 后续完善。

---

### 🔴 B.1 「代签 / 替考」问题完全没防范（最严重）

**场景**：学生 A 把卡交给舍友 B，B 帮 A 碰卡，A 实际不在。

NFC 卡方案的 **固有弱点**：卡 = 身份。卡可被转交。

4-15 讨论中提到「老师在场」作为人防（技术防不住就靠人）。但 spec 完全没明确这一约束，也没记录这是已知风险。

**建议**：
- 在 spec 里明确「**Phase 1 NFC 卡方案的代签风险靠"老师必须在场监督"补偿**」
- Phase 2 加 iPhone 后能否一定程度缓解（device_id + 学号双绑）需要单独讨论
- 长期：考虑加摄像头 / 人脸识别（但成本、隐私问题大）

---

### 🔴 B.2 多台点呼机的协调未定义

WIP 写明部署 **4 台点呼机**，spec 提到「本场来自点位 A 或 B」，但 **完全没定义**：

- 学生属于哪台机器？（按寮 / 楼层 / 房间分配？）
- 学生碰了非自己分配的机器，算不算？
- 一个 session 是 1 台机器一场，还是 4 台同一场？
- 如果学生先碰 A 再碰 B，怎么处理？

这是 spec 缺失最严重的部分之一。Phase 1 代码开工前必须决定。

---

### 🔴 B.3 重复签到 / 双签的处理未定义

**场景**：学生 A 在 21:58 已成功签到（绿）。21:59 又碰了一下卡。

spec 没说：
- silently ignore？
- 返回 `DUPLICATE_CHECKIN` 错误？
- 更新 `checked_in_at` 为最新时间？

**Phase 1 影响**：用 NFC 卡时学生很容易意外重复碰（手抖、怕没读到再碰一次）。
没有明确策略 → 点呼机会反复播报，体验差。

**建议**：定一条「同一 `student_id` 在同一 session 内的重复签到 → silently ignore（不变更状态、不重复播报，但记日志）」。

---

### 🔴 B.4 未注册卡 / 陌生 UID 的响应未定义

Phase 1 用 NFC 卡时，每张卡的 UID 必须先绑到学生。**未绑定的卡碰一下会怎样？**

spec 没写。需要补：

- 后端响应：`UNKNOWN_CARD` / `UNREGISTERED_UID` 错误码（看 ERROR_CODES 没有这两条）
- 点呼机响应：红灯 + 失败声音 + 不播报姓名
- 老师端：是否记录"陌生卡尝试"事件供审计？（防止有人故意试卡）

---

### 🔴 B.5 学生 → session 的归属未定义

- session 是由谁创建的？（系统按时刻表自动创建？老师手动？）
- 学生属于哪些 session？（每天 morning + evening？还是更复杂？）
- 转学生 / 退寮生 / 新入寮生何时进出 session 范围？

这些是基础数据建模问题，spec 完全没回答。

---

### 🟡 B.6 老师"延后按开始钮"的场景未明确

spec 说：到达 `scheduled_window_start` 仍未开始 → 系统自动开始（`started_source = system`）。

**但**：如果系统已经自动开始（21:57），老师 21:58 才注意到并按了按钮，会发生什么？

**建议**：明确「`started_at` 写入后，再次按开始钮 → 返回 `ALREADY_RUNNING`，不变更状态」。
（ERROR_CODES 里已有 `ALREADY_RUNNING` 错误码，但 spec 没串起来）

---

### 🟡 B.7 「学生比老师先到」的 UX 未定义

第 5.1 节说「先生が点呼開始ボタンを押さないと、チェックインすることができない」。

但 Phase 1 用卡时，学生提前到、碰卡 → 后端返回 `NOT_STARTED`：

- 点呼机灯/声音怎么响应？
- 学生会不会困惑「我是不是没读到？」反复碰？
- 是不是需要专门一种「等待中」的灯/声音区分于「失败」？

Phase 2 用 App 时同理。

---

### 🟡 B.8 离线策略

WIP / TODO 已标注。spec 也没定。

Phase 1 点呼机如果断网：
- 拒绝所有签到（最严格，但学生体验差）
- 缓存到本地，等网恢复后批量上传（友好，但要解决时间戳冲突）
- 触发降级模式（老师手动签）

需要在 Phase 1 开工前定。

---

### 🟡 B.9 改判后的纪律分扣减未闭环 + 修改时间窗

第 11 节说老师可以把 `from_status` → `to_status` 手动改。但：

- 改 `PRESENT` → `ABSENT`：要不要按「缺席 1.0 分」自动扣分？
- 改 `ABSENT` → `PRESENT`：之前自动扣的分要不要回退？
- 还是改判只改状态，扣分由老师另行手动加减？

`v0.1_冻结决策.md` 里只定了阈值，没定改判与扣分的联动规则。

**追加维度（2026-04-17）：修改时间窗**

spec 现在没限制「可改多久前的 session」。但涉及金钱/处分，应该是**角色 × 时间**的二维矩阵：

| 字段类型 | 可改时限 | 角色 | 留痕 |
|---|---|---|---|
| 备注 / 改判理由（非状态字段）| 无限制 | 所有老师 | 修改历史 |
| 出勤状态改判 | ≤7 天 且 当月月结前 | 所有老师 | 必填 reason |
| 出勤状态改判 | 8-30 天 | 仅舍监 | 必填 reason + 舍监签字 |
| 出勤状态改判 | >30 天 | **只读** | 走「追溯申请」独立流程 |
| 已发处分名单对应的 session | 原则只读 | — | 若必改需撤销处分通知 + 重新发放 |
| 纪律分（月汇总产出后）| 只读 | — | 修正只能下月补扣/补还 |

v0.2 增补 §11.3。

---

### 🟢 B.10 「免」状态学生意外回来碰卡

**场景**：学生 A 当晚有「免」（事先申请外泊获批准），但 21:30 突然回来了，21:58 碰卡。

spec 没说：
- 允许签到 → 状态变 `PRESENT` 覆盖「免」？
- 忽略碰卡，状态保持「免」？
- 签到成功但状态显示「免 + `PRESENT`」？

宿舍管理常见情况，建议明确。

---

### 🟡 B.11 「申请审批」流程的细节缺失

`ABSENCE_REQUEST_PENDING`（申）→ 老师审批 → 同意/拒绝。但：

- 申请由谁发起？（学生 App 提交？口头告诉老师录入？）
- **Phase 1 没有学生 App —— 申请根本没地方发起**（阻塞项：要定代录入流程或口头报备协议）
- 审批截止时间？（如果老师永远不审批，会一直挂在「申」状态？）
- 学生申请后能否撤回？
- 审批拒绝后是否通知学生？怎么通知？

> 2026-04-17 升 🟡：Phase 1 无 App 的根本问题要在 v0.2 §8.3 补齐，不能"后续完善"。

---

### 🟢 B.12 `schedule_mode` 默认值未定

spec 说 `schedule_mode` 必须在 session 开始前设置，老师可以改。
**默认是什么？** 没说。

建议默认 `split`（分组点呼，符合 v0.1 设计意图）。

---

### 🟢 B.13 节假日表的来源未定

「节假日表由老师后台维护」。但日本祝日是公开数据（内閣府每年发布 CSV）。
全靠老师手动维护 → 容易漏（老师忘记加新一年的祝日 = 全员系统性误判）。

**建议**：每年自动从内閣府数据预填，老师只补「学校特殊休日」（如校内行事日）。

---

### 🟢 B.14 `health_flag` 红十字的生命周期未定

- 谁能加 / 谁能去掉？（学生 App 自己报？老师录入？）
- 加上后什么时候自动清除？（当天 / 一周 / 永久挂）
- 红十字背后存的健康内容字段（弹窗里能看到）由谁写？

---

### 🟢 B.15 `evidence` 字段的格式未定

老师手动操作的留档里有 `evidence`（可选）。但格式没说：
- 文本说明？
- 上传图片（医院证明、请假条照片）？URL 还是 binary？
- 多个证据如何处理？

---

### 🟢 B.16 「本场来自点位 A 或 B」的含义未明

第 3.2 节弹窗显示项里有「本场来自点位 A 或 B」，但「点位 A / B」是什么概念？
- 点呼机的物理位置（4 台机器各一个 ID）？
- 不同的判定逻辑路径（路径 A 卡 / 路径 B iPhone）？

如果是后者，要和第 4 节路径定义对齐。

---

### 🟢 B.17 WebSocket 协议未定义

第 9 节提到老师端实时状态由 WebSocket 推送。但消息格式、心跳、重连策略全没定。

Phase 1 点呼机 → 老师端的播报反馈，Phase 2 学生 App → 老师端的颜色更新都需要这条通道。

技术债，v0.2 spec 补完时一并处理。

---

### 🟢 B.18 幂等键未明确

「幂等」被提到。需要明确幂等键。候选：

- `(student_id, session_id)` —— 简单，但同一 session 重复签到无法区分
- `(student_id, session_id, client_request_id)` —— 客户端生成 UUID，更标准
- `(card_uid, session_id, ts_secondbucket)` —— 用读卡时间桶

影响 Phase 1 点呼机和 Phase 2 App 的重试逻辑。

---

---

## 附录 C — 4 台点呼机协调规则（4-17 新增 — 收口附录 B.2 / B.5 / B.16）

> Q3 拍板：**部署 4 台**。本附录定义"4 台之间如何协调"的硬规则。
> 物理布局（卡读头 vs 静态标签的具体位置）= Q4 待定，详见 `DEVICE_REGISTRY_v0.1.md` §3.3 + §6。

### C.1 学生归属

**默认规则**：学生 **不绑定固定机器**。任何一台 `device_active=true` 的机器都可以用来签到。

理由：
- 寮舍 4 个入口，学生从最近的一个进 → 强制绑定固定机器会造成不必要的拒签
- 防代签靠"老师在场监督"+"播报对照人脸"，不靠"必须用某台机器"

**例外**：如果未来某栋寮舍要单独管理（比如足球部寮 vs 普通寮），可以加 `device_id ↔ student_group` 的可选限制规则。v0.2 暂不实现。

### C.2 一个 session = 全寮一场

**4 台机器同属于 1 个 session**（早点呼一场 + 晚点呼一场 = 每天 2 个 session）。

不是"每台机器一场 = 4 个 session"。原因：
- 学生可能从不同入口回，不应该被分成 4 套座位表
- 老师 iPad 看的是**全寮总座位表**，一个 session 一张表
- 统计、扣分、月汇总都在 session 级别

### C.3 学生先碰 A 再碰 B（同一 session 内）

**第一次碰**：判定为 `present` / `late`，写 `attendance_event`，老师端座位点亮。
**第二次及之后碰**：服务器返回 `DUPLICATE_REQUEST`，silently ignore（不变更状态、不重复播报，但记 audit log）。

老师端弹窗显示**第一次碰的 device_id**（事实证据）；后续重复碰不会覆盖。

### C.4 物理布局（Q4 待定 — 4-17 立此存照）

每台树莓派的"卡读头 vs iPhone 标签"相对位置有 3 个候选：

| 布局 | 描述 | 优点 | 缺点 |
|---|---|---|---|
| **A** | 同台树莓派 = `hybrid`（卡读头 + 静态标签贴在外壳上） | 节省机器数；学生不用区分 | 卡和 iPhone 用同一物理点位，碰错概率低但需要清晰指示 |
| **B** | 卡读头 4 台 + 静态标签 4 张分开布置 | 物理隔离清晰 | 需要 8 个点位 |
| **C** | 同台树莓派但卡读头和静态标签分两个面（如正面 + 侧面）| 隔离 + 节省 | 安装稍复杂 |

→ 等现实调研（`00_admin/TODO.md` 的"现实世界调研"段）后定。

### C.5 学生 → session 的归属（收口附录 B.5）

**session 由系统按时刻表自动创建**：
- 每天 morning 1 个 + evening 1 个 = 2 个 session
- 创建时刻：`scheduled_window_start - 5 分钟`（系统兜底，老师可以更早手动开始）
- 如果时间窗表无对应 `(session_type, day_type, effective_group)` 组合 → 不创建该 session，签到返回 `NO_ROLLCALL_FOR_TODAY`

**学生属于哪些 session**：
- 默认：全体在寮学生都属于当天的 morning + evening session
- `student_status` 字段（v0.3 引入）：`active`（在寮）/ `paused`（请假）/ `transferred`（转学）/ `graduated`（退寮）
- 仅 `active` 学生进入 session 的座位表
- 状态变更必须留 audit（包括变更日期、操作老师、原因）

**新入寮 / 转学 / 退寮的边界**：
- 新入寮：`student_status` 设为 `active` 后的第一个 session 起开始计算
- 退寮：`student_status` 改 `transferred` / `graduated` 之后的 session 不再计入
- 中途请假：`paused` 期间用「免点呼范围」覆盖（参见 §8.2）

---

---

## 附录 D — v0.2 主体改写收口清单（2026-04-17 晚）

> 本附录记录 v0.2 主体改写解决了哪些附录 A/B 项，以及哪些仍开放。
> 标 ✅ = 已落地；标 🟡 = 部分解决，剩余开放部分注明；标 🔄 = 留给 v0.3。

### D.1 收口附录 A（整理时发现的问题）

| 项 | 状态 | 落地位置 |
|---|---|---|
| A.1 Phase 1 vs spec 脱节 | ✅ | §1 整体改写为双路径并存 |
| A.2 祝休日足球部时间存疑 | 🟡 | 假设"故意如此"，待 itsuki 最终确认 |
| A.3 X 分钟未定值 | 🔄 | 等 itsuki 拍板（候选 5/10/15/30）|
| A.4 提前开始平移规则反直觉 | 🔄 | 设计意图待 itsuki 确认 |
| A.5 日文打字错误 | ✅ | CC 已修正（此前已落地）|
| A.6 颜色优先级两套写法 | ✅ | 已采用详细版 + Q1 落地 |
| A.7 NFC 标签位置概念 | ✅ | 与 §9 + DEVICE_REGISTRY 一致 |

### D.2 收口附录 B（深度审查发现的 spec 漏洞）

| 项 | 状态 | 落地位置 |
|---|---|---|
| B.1 代签 / 替考 | ✅ | §5.1.3 明确"老师在场监督"为 Phase 1 硬约束 + §9 写入"老师本人"为人防组件 |
| B.2 4 台点呼机协调 | ✅ | 附录 C.1-C.3 |
| B.3 重复签到 | ✅ | §7 边界："silently ignore + DUPLICATE_REQUEST + 记 audit" |
| B.4 未注册卡 / 陌生 UID | ✅ | §7 边界 + `UNKNOWN_CARD` / `UNREGISTERED_UID` / `UNKNOWN_DEVICE` 错误码 |
| B.5 学生 → session 归属 | ✅ | 附录 C.5 |
| B.6 老师延后按开始钮 | ✅ | §5.5（`ALREADY_RUNNING`）|
| B.7 学生比老师先到 UX | 🟡 | §7 边界返回 `SESSION_NOT_RUNNING`；点呼机灯/声音的"等待中"细分 🔄 v0.3 |
| B.8 离线策略 | 🔄 | 需要 itsuki 拍板 |
| B.9 改判扣分 + 修改时间窗 | ✅ | §11.3 + §11.4 |
| B.10 免学生意外回来碰卡 | 🔄 | 需要 itsuki 拍板 |
| B.11 申请审批流程细节 + Phase 1 无 App | 🔄 | 需要 itsuki 决定代录入 / 口头报备协议 |
| B.12 `schedule_mode` 默认值 | ✅ | §10.1 默认 `split` |
| B.13 节假日表来源 | 🔄 | 建议自动从内閣府 CSV 预填，待 itsuki 拍板 |
| B.14 `health_flag` 生命周期 | 🔄 | 待 itsuki 拍板 |
| B.15 `evidence` 字段格式 | 🔄 | 待 itsuki 拍板 |
| B.16 「点位 A 或 B」含义未明 | ✅ | §3.2 改为 `device_id` + `path_type`，含义明确 |
| B.17 WebSocket 协议 | 🔄 | v0.3 写专门的 WebSocket spec |
| B.18 幂等键 | 🟡 | §10.2 引入 `idempotency_key`，具体格式 🔄 v0.3 |

### D.3 v0.2 主体改写后仍开放的项目债

🔄 留给 v0.3 / 实现阶段：
- **设计意图类**（待 itsuki 拍板）：A.2 / A.3 / A.4 / B.8 / B.10 / B.11 / B.13 / B.14 / B.15
- **协议细化类**（v0.3 专项）：B.7 UX / B.17 WebSocket / B.18 幂等键格式

---

**END** — RollCall Spec v0.1（v0.2 主体改写 / 2026-04-17 晚）
