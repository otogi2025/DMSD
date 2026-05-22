# DMSD v0.1 API 全局约定

更新时间：2026-04-22（4-22 修订：§1 精化 ok=true 字段集 + §8-§15 新增 URL/HTTP 动词/分页/日期/命名/版本号/状态码/error.detail schema 扩写 — 对应 backlog S13 / L8 / S19 对齐）
v0.1 原版 2026-02-12；后续修订见 CHANGELOG + 本文件顶部。

## 1. 统一响应包裹格式（强制）
- 成功：
```json
{ "ok": true, "data": { } }
```
- 失败：
```json
{ "ok": false, "error": { "code": "INVALID_INPUT", "message": "...", "detail": {} } }
```
- **字段集互斥规则**（4-22 明示 — S19 对齐）：`ok=true` 时响应 body **不包含** `error` 字段（不是 `"error": null`）；`ok=false` 时响应 body **不包含** `data` 字段。前端反序列化时严格按 `ok` 分派，不处理 undefined/null 混合态。
- 禁止在 `data` 内再次嵌套 `ok` 字段。
- 详细 error.detail schema 见 §15。

## 2. 鉴权与角色（最小可跑）
- Header：`Authorization: Bearer <token>`
- 学生 token 只允许访问 `/student/*` 下的 endpoint
- 老师 token 只允许访问 `/teacher/*` 下的 endpoint
- token 过期 / 无效 → 返回 `UNAUTHORIZED`
- token 角色不匹配（学生访问 `/teacher/*` 或反之）→ 返回 `FORBIDDEN`
- **URL 前缀统一**见 §8（含 L8 漏洞记录）

## 3. 本地开发联调方案（第 16 条，已拍板）
- 采用 `/auth/dev_login`（仅开发环境可用）。
- 生产环境必须关闭该接口。
- `dev_login` 返回固定测试账号 token，最少包含：
  - `student_demo`
  - `teacher_demo`

## 4. 时间基准
- 所有判定一律基于 `server_now (JST)`。
- 前端只展示倒计时，不参与业务判定。

## 5. 时间窗规则（2026-05-21 b1 决策 — 窗口永远固定）
- 判定 / 结算 / 查表 / 倒计时全部直接用 `scheduled_*_at`。
- 老师提前按开始按钮只改 `started_at` 显示，不改判定窗口。
- 原 `effective_*` 字段族已彻底删除（详见 `rollcall/RollCall_Spec.md §5.4 / §7`）。

## 6. 倒计时公式（唯一）
- `remaining_seconds = max(0, scheduled_late_end_at - server_now)`
- 禁止使用 `ended_at` 参与倒计时计算。

## 7. settle 规则（唯一）
- `settle_at = min(ended_at, scheduled_auto_end_at)`
- 结算时将 `init -> absent`
- 排除：
  - `exempt_range`
  - `absence_request_pending`
- 结算后：`session_status = ended`
- 老师改判必须填写 `override_reason` 并写审计日志。

---

## 8. URL 命名规则（4-22 新增 — S13 + L8）

### 8.1 现状（问题记录）

spec v0.3 里出现两种 URL 前缀风格：
- `/student/*` / `/teacher/*`（本文件 §2 旧写法，按角色分隔）
- `/api/v1/checkin`（RollCall_Spec §5.1 / §5.1.2 / Device_Contract 骨架 §3.1，按版本 + 资源分隔）

**两种不兼容**：一个 endpoint 只能归其中一类。**L8 漏洞未闭合** —— 需要 itsuki 拍板统一。

### 8.2 🔄 待 itsuki 拍板：URL 命名统一方向

| 方案 | 示例 | 优点 | 缺点 |
|---|---|---|---|
| **A（RESTful + 版本前缀 + 角色子前缀）** | `/api/v1/student/me/checkins` / `/api/v1/teacher/sessions/{id}/start` / `/api/v1/device/checkin` | 版本号明确；REST 习惯；路径即角色；新客户端可自主发现 | URL 变长 |
| **B（按角色分前缀 + 版本在 Header）** | `/student/me/checkins` + `X-API-Version: v1` Header / `/teacher/sessions/{id}/start` | URL 简短；本文件 §2 一致；角色清晰 | 版本号藏在 Header 不直观；和 spec §5.1 `/api/v1/*` 不兼容（要改 spec） |
| **C（无角色前缀 + 版本前缀）** | `/api/v1/checkins`（角色由 token 校验）| 最简洁；角色仅靠 Bearer token；和 spec §5.1 最兼容 | 相同 endpoint 学生 / 老师语义不同，易混 |

**CC 推荐**：**A** —— 路径即角色对新手最友好；和现有 spec §5.1 `/api/v1/*` 最小改动兼容；`X-API-Version` header 对零基础学习者不友好。

**拍板后连带改动**：
- 本文件 §2 改 URL 模板
- RollCall_Spec §5.1 / §5.1.2 示例改
- Device_Contract 骨架 §3 改
- ERROR_CODES 无影响

### 8.3 拍板前的临时规则

在 §8.2 拍板前，新文档 / 代码统一**使用方案 A 书写**（减少后期返工）；历史文档（本文件 §2 / spec §5.1）保留原风格，等一次性统一时再改。

---

## 9. HTTP 动词约定（4-22 新增 — S13）

| 动词 | 语义 | 用例 |
|---|---|---|
| `GET` | 查询资源，**幂等**，**无副作用**（不改服务器状态） | 获取 session 列表 / 学生信息 / 座位表 |
| `POST` | 创建资源 / 执行动作，**不要求幂等**（签到等动作例外，通过 §10 幂等键保证） | 创建 session / 提交签到 / 触发结算 |
| `PUT` | 全量替换资源，**幂等** | 更新学生信息（全字段） |
| `PATCH` | 增量修改资源字段，**幂等**（同 payload 重复发结果一致） | 老师改判 base_status / 修改 session 配置 |
| `DELETE` | 删除资源，**幂等** | 删除 session draft（未 running 前） |

**约束**：
- 不要用 `POST` 做查询（违反 REST 习惯 + 不便缓存）
- 不要用 `GET` 做修改（会被爬虫 / 预加载误触发）
- 签到动作（改判 / 删除）必须同时在后端写 audit log

---

## 10. 幂等键（4-22 新增 — S13 + 和 RollCall_Spec §10.2 对齐）

| 路径 | 幂等键来源 | 说明 |
|---|---|---|
| 路径 A（NFC 卡 → 点呼机） | 后端用 `(card_uid, session_id, ts_secondbucket)` 复合唯一索引去重 | 点呼机是 thin client，不生成 UUID；`ts_secondbucket` = `floor(server_now / 1 秒)`，防止 1 秒内连碰两次都记录 |
| 路径 B（iPhone / Android App） | 客户端生成 UUIDv4 放请求 body `idempotency_key` 字段 | App 可能因网络差而重试，同一 UUID 重试保证幂等 |
| 其他写操作（改判 / 创建 session 等） | 路径同 B：客户端传 `idempotency_key` header（可选） | 非阻塞，缺失时后端按请求正常处理 |

幂等键 TTL：后端至少保留 **24 小时**（足够覆盖当日全部 session + 客户端最大重试窗口）。

---

## 11. 分页约定（4-22 新增 — S13）

### 11.1 请求参数（Query String）

```
GET /api/v1/teacher/sessions?page=1&page_size=20&order_by=started_at&order=desc
```

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `page` | int | 1 | 第几页，从 1 开始（不是 0） |
| `page_size` | int | 20 | 每页几条。上限 100（超过返回 `INVALID_INPUT`） |
| `order_by` | string | `created_at` | 排序字段（白名单，非白名单返回 `INVALID_INPUT`）|
| `order` | enum | `desc` | `asc` / `desc` |

### 11.2 响应格式

```json
{
  "ok": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 143,
      "total_pages": 8
    }
  }
}
```

### 11.3 为什么选 page/page_size 不选 cursor-based

- 简单易懂（零基础初学者友好）
- UI 常需要"跳到第 N 页" + "显示第 X/Y 页"，cursor-based 做不到
- DMSD 业务规模小（1 个寮 ~120 学生 × 每日 2 session × 1 年 = ~87k 行），page/page_size 性能足够
- 如果未来数据规模膨胀（例：多寮联合统计）可升级 cursor-based，但 v1 范围内不需要

---

## 12. 日期时间格式（4-22 新增 — S13）

- 所有时间戳使用 **ISO 8601 带 JST 时区偏移**格式：`2026-04-22T21:30:00+09:00`
- 不使用 UTC（`Z` 结尾）—— 系统全链路 JST，UTC 会产生无谓转换 + 日期边界 bug
- 不使用 UNIX timestamp（数字）—— 可读性差，debug 时需手动转换
- 日期（不含时间）：`2026-04-22`（ISO 8601 date-only）
- 时分（不含日期，如时间窗规格）：`22:00:00`（24 小时制，秒精度）

服务器判定时间戳：统一用 `server_now (JST)`（见 §4）。

---

## 13. 字段命名风格（4-22 新增 — S13）

- JSON 字段名 / 数据库字段名：**小写蛇形**（`student_id` / `base_status` / `scheduled_on_time_end_at`）
- 枚举值：**小写蛇形**（`base_status` 取值 `init` / `present` / `late`）
- 禁止 camelCase（`studentId`）或 PascalCase（`StudentID`）
- 见 `FIELD_REGISTRY.md §1 强制规则` + `ENUM_REGISTRY.md §15`

**URL 路径段**：也用小写蛇形（`/api/v1/rollcall_sessions/{id}`），**不使用 hyphen**（避免 `/roll-call-sessions` 和其他文档字段名风格不一致）。

---

## 14. HTTP 状态码映射（4-22 新增 — S13）

| HTTP 状态 | 语义 | 对应 ERROR_CODES |
|---|---|---|
| `200 OK` | 成功（含业务成功 + 业务警告但不失败）| `ok=true` |
| `400 Bad Request` | 客户端输入错误 | `INVALID_INPUT` / `DUPLICATE_REQUEST`（某些场景）|
| `401 Unauthorized` | 无 token / token 无效 / 过期 | `UNAUTHORIZED` |
| `403 Forbidden` | token 有效但无权限 | `FORBIDDEN` |
| `404 Not Found` | 资源不存在 | `NOT_FOUND` |
| `409 Conflict` | 资源状态冲突 | `ALREADY_RUNNING` / `DUPLICATE_REQUEST`（某些场景）/ `SESSION_NOT_RUNNING` |
| `410 Gone` | 资源已永久删除 / 注销 | `DEVICE_NOT_ACTIVE`（设备永久注销时）|
| `422 Unprocessable Entity` | 请求格式正确但语义不合法 | `NO_ROLLCALL_FOR_TODAY` / `INVALID_SIGNATURE` / `UNKNOWN_CARD` / `UNREGISTERED_UID` / `UNKNOWN_DEVICE` / `TIMEOUT` |
| `500 Internal Server Error` | 服务器异常 | 兜底 `系统繁忙，请稍后重试` |

**约束**：
- 业务层逻辑错误（如 `UNKNOWN_CARD`）用 422，不用 500。500 只留给真的异常（数据库连不上 / 代码崩）
- `401` 和 `403` 严格区分：401 = 身份验证失败 / 403 = 身份验证通过但无权限

---

## 15. error.detail Schema（4-22 新增 — S13）

错误响应的 `error.detail` 是**可选**字段，类型为 **JSON Object**（不是 array 或 string）。

### 15.1 标准子字段（约定俗成）

| 子字段 | 类型 | 说明 |
|---|---|---|
| `field` | string | 字段级错误时指明哪个字段（如 `"field": "student_id"`）|
| `reason` | string | 机器可读的细化原因（英文 snake_case，如 `"reason": "value_exceeds_max_length"`）|
| `hint` | string | 给开发者的调试提示（不展示给终端用户）|
| `received` | any | 客户端传入的值（用于 debug，**生产环境需脱敏 PII**）|

### 15.2 示例

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "提交内容有误，请检查后重试",
    "detail": {
      "field": "page_size",
      "reason": "value_exceeds_max",
      "received": 500,
      "hint": "page_size max is 100"
    }
  }
}
```

### 15.3 扩展约束

- `detail` 字段**不强制任何 key**（可为 `{}`）
- 前端只消费 `code` 做分派；`message` 展示给用户；`detail` 仅用于开发 / 客服工具
- **PII**（学生姓名 / 生日 / device_id / card_uid 等）不写进 `detail`（除非脱敏）

---

## 16. v0.2+ 待扩展点（占位）

以下条目尚未规约，**代码开工前必须补**（v0.4.0+ release 前闭环）：

- **rate limiting**（每学生 1 秒最多 N 次签到请求 / 老师每分钟最多 M 次改判）
- **CORS 策略**（学生 App 跨域 / 老师 Web 跨域）
- **HTTPS / TLS 版本要求**（最低 TLS 1.2？mutual TLS？见 Device_Contract 骨架 OQ1）
- **WebSocket 消息格式**（Device_Contract 骨架 §4 + RollCall_Spec 附录 B.17 🔄）
- **审计日志**的字段清单（审计对象 / 操作 / 前后值 / 操作者 / 时间戳 / IP）
- **Webhook / 推送消息**（若有）
- **API 废弃策略**（老版本多久停机）

---

**END** — v0.1 API 约定
