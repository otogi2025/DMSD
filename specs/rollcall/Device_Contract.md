# Device_Contract — 点呼机 ↔ 后端 接口契约

> **版本**：v1.0 草案（2026-07-17 起草，依 7-17 拍板「点呼功能真实装」启动；骨架前身 = 2026-04-21 Device_Contract 骨架，已归档）
> **上游文件**：`RollCall_Spec.md` §5/§7/§9/附录 C ｜ `DEVICE_REGISTRY.md` ｜ `design/flow_design.md` §3/§6 ｜ `specs/v1.1_范围冻结决策.md` §2.3 ｜ `specs/API_CONVENTIONS.md`
> **定位**：点呼机（device）与后端（server）之间**所有交互协议**的唯一真值；同时定义 ST25DV Mailbox 载荷格式（手机写入端与点呼机读取端共用 §7）。
> **不定义**：点呼机内部硬件接线（→ `design/hardware_design.md`）；学生端 / 老师端 App 契约（→ `API_CONVENTIONS.md` 等）。
> **状态标记**：正文均为实装契约；标 ⏳ 的条目为实装采用的默认值，仍待 itsuki 最终确认（汇总见 §11）。

---

## 1. 适用范围与术语

- **device（点呼机）**：Raspberry Pi 3A+ + PN532 读头 + ST25DV16K 邮箱标签的边缘设备，`device_type = card_reader / iphone_tag / hybrid`（ENUM §12）。
- **server（后端）**：FastAPI 后端，唯一判定者。
- 点呼机是**受信任边缘设备**：唯一职责扩展 = 为签到事件盖 NTP 校准时间戳 `swipe_time`（`flow_design.md §1.2`）。除此之外遵守 thin client 原则（RollCall_Spec §9）：不判定、不查表、不保存业务真值。
- 响应一律走 `{ok,data}` / `{ok,error}` 信封（API_CONVENTIONS §1，中间件自动包裹，本文示例只写 `data` 内部）。

## 2. 设备身份与认证（v1.1 冻结 §2.3 落地）

### 2.1 密钥体系

- 每台点呼机持有一对 **Ed25519 密钥**：私钥存设备本地文件（权限 0600，路径见 §10），公钥存后端 `rollcall_devices` 表。
- 后端不保存私钥；私钥不出设备。设备报废 / 疑似泄露 → 管理员停用该设备（`device_active=false`），重新 enroll 换新钥。

### 2.2 设备登记与激活（enroll）

1. 管理员（老师权限组 op）调 `POST /api/v1/devices` 创建设备记录：`{device_id, device_type, device_location, device_notes?}`。响应返回**一次性激活码 `enroll_code`**（明文仅此一次；后端只存其哈希）。
2. 部署者把 `device_id` + `enroll_code` 写进设备 `config.json`（§10）。
3. 设备首次启动：本地生成 Ed25519 密钥对 → `POST /api/v1/devices/{device_id}/enroll`，body `{enroll_code, public_key}`（公钥 = base64 原始 32 字节）。
4. 后端校验 enroll_code 哈希匹配且未使用 → 存公钥、记 `enrolled_at`、作废激活码。重复 enroll → `INVALID_INPUT`（重新激活须管理员先调 `POST /api/v1/devices/{device_id}/reset-enroll` 重发激活码，旧公钥即刻作废）。

### 2.3 令牌换取（token）

- `POST /api/v1/devices/{device_id}/token`，body：

```json
{ "ts": "2026-07-17T21:55:00+09:00", "nonce": "随机 16 字节的 hex", "signature": "base64(Ed25519 签名)" }
```

- 签名串（UTF-8 逐字拼接）：`"{device_id}\n{ts}\n{nonce}"`。
- 后端校验：设备存在且 `device_active=true` 且已 enroll → 验签 → `|server_now − ts| ≤ 600 秒` → nonce 24 小时内未用过（防重放）。
- 通过 → 返回 `{access_token, expires_at}`：JWT，`role="device"`，`sub=device_id`，有效期 **12 小时**。设备在剩余寿命过半时主动换新。
- 失败错误码：`UNKNOWN_DEVICE` / `DEVICE_NOT_ACTIVE` / `INVALID_SIGNATURE`（含 ts 过期、nonce 重放，`error.detail.reason` 细分）。

### 2.4 日常调用

- 一切设备侧请求带 `Authorization: Bearer <device JWT>`。
- `role="device"` 的令牌**只能**调用本文 §4-§5 列出的设备端点；调其他端点 → `FORBIDDEN`。老师 / 学生令牌也不能调设备专属端点（`/devices/me/*`）。

## 3. 判定时间基准（API_CONVENTIONS §4 点呼机波条款落地）

- 设备签到（§4.1）判定时刻 = 请求携带的 **`swipe_time`**（设备 NTP 校准、学生接触机器那一刻）。
- 信任边界：`swipe_time > server_now + 30 秒`（未来时刻）→ 后端以 `server_now` 代之并写审计（时钟异常不奖励）；`swipe_time` 早于 `server_now`（离线补传常态）→ 照用。
- 非设备来源的签到（老师代签端点）维持 `server_now` 判定，不受本文影响。

## 4. HTTP 契约（设备侧端点）

### 4.1 `POST /api/v1/rollcall/device-checkins`（核心签到入口）

设备不感知 session：后端由学生归属（dorm_unit）解析**当前 running 的场次**。无 running 场次 → `SESSION_NOT_RUNNING`。

请求 body：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path_type` | `"A"` / `"B"` | ✅ | ENUM §13 |
| `card_uid` | string | 路径 A ✅ | NTAG215 UID，14 位 hex 小写（7 字节） |
| `student_id` | UUID | 路径 B ✅ | 来自 Mailbox 载荷（§7） |
| `idempotency_key` | UUID | 路径 B ✅ | 来自 Mailbox 载荷（§7）；路径 A 不传（后端按「同生同场次仅一条」去重） |
| `swipe_time` | timestamp | ✅ | ISO 8601 +09:00，设备盖章 |

处理流程（后端）：

1. 解析学生：路径 A 用 `card_uid` 查卡绑定表（无记录 → `UNKNOWN_CARD`；有记录但卡停用或学生非 `active` → `UNREGISTERED_UID`）；路径 B 直接用 `student_id`（无此人或非 `active` → `UNREGISTERED_UID`）。演示学生（`is_demo`）按 `UNREGISTERED_UID` 处理，不进真实考勤。
2. 找该生 dorm 所属、`session_status=running` 的场次；无 → `SESSION_NOT_RUNNING`。
3. 幂等：该生该场次已有签到 → 返回 200，`duplicate=true`，携带既存结果（设备**不重复播报**，绿灯即可）；`idempotency_key` 命中同理。
4. 按 `swipe_time` 判定（RollCall_Spec §7 完整语义）：`≤ scheduled_on_time_end_at` → `present`；`≤ scheduled_late_end_at` → `late`；**之后 → `TIMEOUT`（不写出席事件）**。
5. 写 `rollcall_event`（append-only，`device_id` = 调用设备，`status_source=auto_nfc`）→ 扣分联动 → WebSocket 推老师端。

响应 `data`：

```json
{
  "student_id": "…", "student_number": "10023", "student_name": "山田太郎",
  "base_status": "present", "session_id": "…", "duplicate": false,
  "led": "green", "audio_file": "10023.wav", "broadcast_text": "山田太郎"
}
```

`led` 取值 `green / yellow / red`（成功=绿；`late`=绿——迟到与否学生侧不区分显示，老师端可见；错误场景见 §9）。

### 4.2 `GET /api/v1/devices/me/roster`（离线兜底名单）

返回 `{generated_at, students: [{student_id, student_number, name, card_uids: []}]}`——仅 `active` 且非演示学生。用途：断网时本地校验放行（flow_design §6 拍板）+ 播报文件名映射。设备每日启动时拉取 + 收到 `roster_updated` 推送时拉取。**设备本地只落磁盘一份加密无关的最小缓存，毕业 / 退寮学生随刷新自然消失。**

### 4.3 音频同步

- `GET /api/v1/devices/me/audio-manifest` → `{files: [{name: "10023.wav", sha256, size}]}`
- `GET /api/v1/devices/me/audio/{file}` → 音频原文件（`audio/wav`）。
- 后端音频目录由运维放置（后端预生成方案，ROLLCALL_DEVICE_DESIGN_LOG §10-D3 拍板）；本波提供存取通道，生成管线另行处理。设备对照 manifest 差量下载至本地缓存；缺文件时播报降级为通用提示音（§9）。

### 4.4 `POST /api/v1/devices/me/heartbeat`

body `{fw_version}` → 后端记 `last_seen_at`。WS 心跳（§5）正常时可不调；作为 WS 不可用时的兜底通道。

## 5. WebSocket 契约

- URL：`wss://<server>/api/v1/ws/device?token=<device JWT>`（与老师通道 `/ws/teacher` 并列、互不相通）。
- 消息统一 `{"type": "...", "data": {...}}`。

| 方向 | type | data | 用途 |
|---|---|---|---|
| server → device | `session_started` | `{session_id, session_type, scheduled_on_time_end_at, scheduled_late_end_at}` | 场次开始（老师手动或系统兜底）→ 设备进入受理状态提示 |
| server → device | `session_ended` | `{session_id}` | 场次结束 |
| server → device | `roster_updated` | `{}` | 通知重拉 §4.2 |
| server → device | `audio_updated` | `{}` | 通知重拉 §4.3 |
| device → server | `heartbeat` | `{ts, fw_version}` | 每 30 秒 ⏳；server 90 秒未收 → 标记离线（记 `last_seen_at`，老师端离线告警属 teacher_web 波，本波不做 UI） |

- 断线重连：指数退避，初始 1 秒、上限 60 秒。设备一切核心功能（读卡→POST）**不依赖 WS 存活**。

## 6. 离线降级与补传（flow_design §6 + ROLLCALL_DEVICE_DESIGN_LOG §6.1 拍板落地）

1. `POST` 失败（网络 / 5xx）→ 事件写入本地 SQLite 队列（含完整请求体，`swipe_time` 为原始盖章值）。
2. 现场即时反馈走本地 roster（§4.2）：UID / student_id 命中 → 绿灯 + 播报（缓存音频）放行；未命中 → 红灯拒绝。
3. 网络恢复 → 按队列顺序补传，成功即出队；`duplicate=true` 同样视为成功。
4. 后端对补传事件按 `swipe_time` 正常判定（§3）。**冲突规则（老师优先）**：
   - 该生该场次已有 `teacher_override` 事件 → 丢弃补传（响应 `duplicate=true` + `superseded_by_teacher=true`，记审计）。
   - 已被结算置 `absent`（`auto_settle`）且补传 `swipe_time` 在窗内 → 采纳补传，追加事件覆盖结果并回退结算扣分（append-only，审计可溯）。
   - `swipe_time` 超过 `scheduled_late_end_at` → `TIMEOUT`，出队不重试（记设备本地日志）。

## 7. ST25DV Mailbox 载荷格式（路径 B：手机 → 点呼机，双端共用）

| 偏移 | 长度 | 内容 |
|---|---|---|
| 0 | 1 | 格式版本 = `0x01` |
| 1 | 1 | 签到类型：`0x01` = 点呼 / `0x02` = 晚自习（v1.1） |
| 2 | 16 | `student_id` UUID 原始 16 字节（RFC 4122 字节序） |
| 18 | 16 | `idempotency_key` UUID 原始 16 字节（App 每次写入前新生成） |

- 总长恒 **34 字节**。点呼机读取后校验「长度 = 34 且版本 = 0x01」，不符即丢弃（记日志、不上报）。
- 预留：未来 v1.1 可选 ECDSA 签名 → 升版本号 `0x02` 追加字段，双端同步升级（v1.1 冻结 §2.4）。
- 写入端（iOS `ST25DVWriter.swift` / Android 同型）与读取端（`rollcall_device/src/nfc/st25dv.py`）必须逐字节对齐本表。

## 8. 场次可用性前提

设备契约假定后端满足 RollCall_Spec 附录 C.5 + §5.5：每日场次由系统按时刻表自动创建、到点兜底自动开始 / 自动结束。设备自身不创建、不查询场次表——收到 `SESSION_NOT_RUNNING` 即黄灯等待（§9）。

## 9. 错误码 → 设备现场行为对照

| 后端响应 | LED | 声音 | 播报 |
|---|---|---|---|
| 成功 `present` / `late` | 绿 | 成功音 | 学生全名（`audio_file` 命中本地缓存；缺失 → 通用确认音）⏳ 迟到是否加播提示音待定 |
| 成功 `duplicate=true` | 绿 | 静默 | 无（spec §7：重复签到不重复播报） |
| `UNKNOWN_CARD` | 红 | 失败音 | 无（陌生卡不播身份） |
| `UNREGISTERED_UID` | 红 | 失败音 | 无 |
| `SESSION_NOT_RUNNING` | 黄 | 短提示音 | 无（「点呼未开始」等待态，区别于失败——RollCall_Spec 附录 B.7） |
| `TIMEOUT` | 红 | 失败音 | 无（已过迟到截止） |
| 网络失败（进离线队列） | 绿（roster 命中）/ 红（未命中） | 对应音 | roster 命中则播报 |
| 鉴权类（`UNKNOWN_DEVICE` 等） | 白灯闪烁 | 静默 | 无（设备自身问题，记日志重试令牌） |

## 10. 设备配置（`config.json`）

```json
{
  "device_id": "dorm-1-01",
  "enroll_code": "首启激活后自动清除",
  "server_url": "https://api.tomoshibi.cc",
  "ws_url": "wss://api.tomoshibi.cc",
  "key_path": "/var/lib/tomoshibi/device_key",
  "data_dir": "/var/lib/tomoshibi",
  "gpio": { "led_red": 17, "led_green": 27, "led_blue": 22, "led_white": 23, "st25dv_gpo": 24 },
  "audio_output": "plughw:1,0"
}
```

GPIO 编号与 `design/hardware_design.md §2.4` / `点呼机接线说明.md` 对齐（LED 低电平点亮）；`st25dv_gpo = 24` ⏳ 接线说明中该引脚原为待定，实装取 GPIO24，硬件联调时如改动同步三处。

## 11. 待 itsuki 确认项汇总（实装已取默认值，改动只调配置 / 单点代码）

| # | 条目 | 实装默认 | 出处 |
|---|---|---|---|
| 1 | 心跳间隔 / 离线判定 | 30 秒 / 90 秒 | §5 |
| 2 | ST25DV GPO 引脚 | GPIO24 | §10 |
| 3 | 场次 `auto_end` 的 X 分钟 | 15 分钟 | RollCall_Spec 附录 A.3（候选 5/10/15/30） |
| 4 | 节假日表来源 | 本波按周六日判定，内閣府 CSV 预填待拍板 | RollCall_Spec 附录 B.13 |
| 5 | 迟到时的现场提示音差异 | 与准时同（仅老师端可见） | §9 |
| 6 | 设备管理 / 绑卡的老师网页 UI | 本波仅 API，UI 归 teacher_web 波 | §2.2 / 卡管理端点 |

## 12. 联动文件

`RollCall_Spec.md`（§5/§7/§9/附录 B.17-B.18 由本文收口）｜ `DEVICE_REGISTRY.md` §7 ｜ `ERROR_CODES.md` ｜ `API_CONVENTIONS.md` §16 ｜ `design/flow_design.md` §3/§6 ｜ `dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` ｜ `dev/backend/v1/`（devices / cards / rollcall 路由）｜ iOS `ST25DVWriter.swift` ｜ Android 同型（后续波）

---

**END** — Device_Contract v1.0 草案
