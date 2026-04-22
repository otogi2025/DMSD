# DMSD v0.1 设备字典 — 点呼机设备注册

更新时间：2026-04-22（4-22 修订：`device_active` 语义收窄为"临时停用" + 新增 `device_retired_at` 区分永久注销 — 对应 backlog S12）

## 1. 适用范围

本文件定义点呼机及其相关 NFC 读写设备的字段、注册流程、生命周期。

**所有签到 API 都必须传 `device_id`**，未注册的设备一律返回 `UNKNOWN_DEVICE`。

## 2. 字段定义

详见 `FIELD_REGISTRY_v0.1.md` §2.2 / §2.8。核心字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_id` | UUID 或自定义短码 | ✅ | 设备唯一标识。建议格式 `dorm-{location}-{seq}`（如 `dorm-A-01`） |
| `device_type` | enum | ✅ | `card_reader` / `iphone_tag` / `hybrid` —— 详见 ENUM §12 |
| `device_location` | string | ✅ | 物理位置自由文本（如"寮舍 A 入口" "寮舍 B 入口"等，等现实调研后定） |
| `device_active` | boolean | ✅ | **临时启用/停用**标志（维修 / 故障时 toggle）。false 时所有签到 API 返回 `DEVICE_NOT_ACTIVE` |
| `device_registered_at` | timestamp | ✅ | 注册时间（JST） |
| `device_registered_by` | teacher_id | ✅ | 注册人（管理员） |
| `device_retired_at` | timestamp | ⬜ | **永久注销**时间（**4-22 新增 — S12 修复**：区分临时停用 vs 永久注销）。null = 设备仍在使用 / 非 null = 永久注销日期。注销后 `device_active` 也应置 false |
| `device_notes` | string | ⬜ | 备注（如硬件型号 `RPi 4B 2GB` 等） |

## 3. `device_type` 详解

### 3.1 `card_reader`（路径 A 的卡读头）

- **物理形态**：树莓派（Pi Zero 2 W / Pi 4B 等）+ PN532 NFC 模块 + 扬声器
- **职责**：读 NFC 卡 UID + HTTP 发后端 + 听 WebSocket + 播报 + 亮灯
- 4-15 决策"thin client / thick server"：**不做任何业务判断**

### 3.2 `iphone_tag`（路径 B 的静态 NFC 标签）

- **物理形态**：贴在点呼机外壳上的静态 NFC tag（NTAG21x 等），写入固定的 `device_id`
- **职责**：仅供学生 iPhone 读取拿到 `device_id`，不主动通信
- 学生 iPhone 拿到 `device_id` 后**自己**用 WiFi/4G 发签到请求给后端
- **成本**：~¥2/张

### 3.3 `hybrid`（同台树莓派同时承载 A 和 B）

- **物理形态**：同一台树莓派，上面装 PN532 卡读头（路径 A） + 外贴静态 NFC 标签（路径 B）
- 在 device 表里登记为一条 `hybrid` 记录，对应一个 `device_id`
- ⚠️ **物理布局**（卡读头 vs 静态标签的相对位置）参见 `RollCall_Spec_v0.1.md` 附录 C.4（Q4 待定）

## 4. 注册流程（4-17 默认方案）

> ⚠️ 默认方案是"管理员后台手动注册"。如果 itsuki 有别的想法（如"首次上电自动注册" / "厂家预分配"），告知 CC 修订。

1. 管理员在老师端管理网站打开"设备管理"页
2. 点"添加设备"，填字段（`device_id` / `device_type` / `device_location` / `device_notes`）
3. 系统检查 `device_id` 唯一性
4. 注册成功 → `device_active=true` / `device_registered_at=server_now` / `device_registered_by=操作的 teacher_id`
5. 管理员把 `device_id` 物理标记到设备上（贴标签 / 烧写到 RPi 配置 / 写入 NFC tag）
6. 设备上电 → 用 `device_id` 调签到 API 时后端能识别

## 5. 生命周期

### 5.1 临时停用（启用/停用 toggle）

**场景**：设备故障送修 / 网络临时中断 / 软件升级中 / 运营决定本机暂停几天。

- 老师在后台 toggle `device_active`（true/false），`device_retired_at` 保持 null
- `device_active=false` 时：
  - 路径 A：点呼机仍可工作（它本身只搬运），但后端会拒绝所有 `device_id=X` 的签到，返回 `DEVICE_NOT_ACTIVE`
  - 路径 B：iPhone 读到该 `device_id` 发请求 → 同样返回 `DEVICE_NOT_ACTIVE`
- 所有 `device_active` 变更必须留档（参考 spec §11 改判审计字段）
- 可反复 toggle（故障修好后设 true 恢复）

### 5.2 永久注销（4-22 修订 — S12 修复）

**场景**：设备彻底报废 / 部署位置撤销 / 换为新型号设备（此 device_id 不再启用）。

- 操作：设 `device_retired_at = server_now` + `device_active=false`（两个字段同时变更）
- 注销后**不允许再 toggle `device_active` 回 true**（逻辑由后端校验拦截）
- **不删除 device 记录**：保留历史 `rollcall_event` 可追溯性；老师端历史查询"这条签到来自哪台设备"仍能找到
- 若部署新设备替换：**另发新 `device_id`**，不复用旧 ID（避免历史记录语义混淆）

### 5.3 历史查询时区分两类状态

| 查询场景 | 判据 |
|---|---|
| 设备当前在不在用 | `device_active=true AND device_retired_at IS NULL` |
| 设备是临时故障 / 还是永久注销 | `device_retired_at IS NULL` → 临时（可能还会回来）/ `IS NOT NULL` → 永久注销 |
| 某日的签到属于哪台设备 | 按 `rollcall_event.device_id` 查，不受当前 active/retired 状态影响 |

## 6. 4 台部署（Q3 — 待现实调研后定具体位置）

itsuki Q3 决策：**4 台**点呼机。

候选位置（待问老师 + 现实调研）：

| `device_id`（建议） | `device_location`（候选） | `device_type`（待 Q4 拍板） |
|---------------------|---------------------------|------------------------------|
| `dorm-A-01` | 寮舍 A 入口 | `hybrid`（如果 Q4 决定卡 + iPhone 标签同台共存） |
| `dorm-B-01` | 寮舍 B 入口 | 同上 |
| `dorm-C-01` | 寮舍 C 入口（待定） | 同上 |
| `dorm-D-01` | 寮舍 D 入口（待定） | 同上 |

实际数量与位置以现实调研结果为准（详见 `00_admin/TODO.md` 的"现实世界调研"段）。

## 7. 待补完项目（4-17 立此存照）

- 设备的硬件型号、采购成本、维修流程 → 在 `00_admin/executable_dev_checklist_v0.1.md` 或新建 hardware_checklist 里完善
- 设备故障 / 离线时的降级策略 → 见 `RollCall_Spec_v0.1.md` 附录 B.8（"离线策略"待决）
- WebSocket 协议（点呼机 ↔ 后端）→ 见 `RollCall_Spec_v0.1.md` 附录 B.17

---

**END** — DEVICE_REGISTRY v0.1
