# DMSD v0.1 错误码字典

更新时间：2026-04-22（4-22 修订：§1.3 `UNREGISTERED_UID` 描述修正 补 S4 遗漏面 + §3 加 `ok=true` 字段约定 S19 修复）

## 1. 全局最小集合（固定）

### 1.1 通用错误
- `UNAUTHORIZED`
- `FORBIDDEN`
- `INVALID_INPUT`
- `NOT_FOUND`

### 1.2 点呼场次相关
- `SESSION_NOT_RUNNING`（session 不在 running 状态：还没开始 或 已结束）
- `ALREADY_RUNNING`（session 已经在 running，重复开始无效）
- `NO_ROLLCALL_FOR_TODAY`（**4-17 新增** — 时间窗表无对应组合，不创建 session）
- `TIMEOUT`（已过迟到截止时刻仍想签到）
- `NOT_YET_ALLOWED`（**5-12 补 — 4-29 决策遗漏面修复** — `RollCall_Spec.md §5.4 + §5.6 + 附录 A.4` 共 3 处引用但 ERROR_CODES 漏列。老师手动按"开始"但当前时刻早于 `on_time_end - 5min`（即未到老师允许手动开始窗口）→ 后端拒绝并返回此码。HTTP 状态 409 Conflict）

### 1.3 签到请求相关
- `DUPLICATE_REQUEST`（同一 `student_id` 在同一 session 已签到，重复请求）
- `UNKNOWN_CARD`（**4-17 新增** — 路径 A：卡的 UID 没绑定到任何学生）
- `UNREGISTERED_UID`（**4-17 新增 / 4-22 修订描述 — S4 遗漏面补齐** — 路径 A：UID 在 `card_uid` 表里**有记录**但 `card_active=false`，或绑定的学生 `student_status != 'active'`。和 `UNKNOWN_CARD` 区分见 `RollCall_Spec.md §7 边界`）
- `UNKNOWN_DEVICE`（**4-17 新增** — 路径 B：iPhone 发的 `device_id` 没在 device 表里）
- `DEVICE_NOT_ACTIVE`（**4-17 新增** — `device_id` 存在但 `device_active=false`）
- `INVALID_SIGNATURE`（**4-17 新增** — 路径 B：签名校验失败）

## 2. 前端文案映射（固定）

### 2.1 通用
- `UNAUTHORIZED` -> `登录已失效，请重新登录`
- `FORBIDDEN` -> `你没有该操作权限`
- `INVALID_INPUT` -> `提交内容有误，请检查后重试`
- `NOT_FOUND` -> `数据不存在或已被删除`

### 2.2 点呼场次
- `SESSION_NOT_RUNNING` -> `点呼还没开始 或 已结束`
- `ALREADY_RUNNING` -> `点呼已在进行中`
- `NO_ROLLCALL_FOR_TODAY` -> `今天没有点呼安排`
- `TIMEOUT` -> `点呼已截止`
- `NOT_YET_ALLOWED` -> `还没到可以开始点呼的时间`

### 2.3 签到请求
- `DUPLICATE_REQUEST` -> `已签到，请勿重复`
- `UNKNOWN_CARD` -> `这张卡没有登记，请联系管理员`
- `UNREGISTERED_UID` -> `卡未启用`
- `UNKNOWN_DEVICE` -> `点呼机未注册`
- `DEVICE_NOT_ACTIVE` -> `点呼机已停用`
- `INVALID_SIGNATURE` -> `签名验证失败，请重新尝试`

兜底文案：
- 未知错误码 -> `系统繁忙，请稍后重试`

## 3. 使用规则
- 业务错误必须返回上述 code。
- 接口失败时格式必须为：

```json
{ "ok": false, "error": { "code": "TIMEOUT", "message": "..." } }
```

- **`ok=true` 时 `error` 字段**（**4-22 新增 — S19 修复**）：接口成功时响应 body **不包含** `error` 字段（不是写成 `"error": null`）。即：

```json
{ "ok": true, "data": { ... } }
```

- 理由：保持成功 / 失败两种响应的字段集完全互斥，前端反序列化时用 `ok` 分派；前端代码不需要同时处理 `error === null` 和 `error === undefined` 两种情况。和 `API_CONVENTIONS.md §1` 的"响应信封"约定对齐。

## 4. 4-17 修订记录

- 移除候选 `NOT_STARTED` / `ENDED` —— 这两个语义都被 `SESSION_NOT_RUNNING` 覆盖（不在 `running` = 还没开始 或 已结束）
- 新增上述路径 A / 路径 B 相关错误码（针对 `RollCall_Spec.md` 附录 B.3 / B.4 / B.10 的 device 建模缺口）
- 文案分组重新整理（原版本是平铺，现按通用 / 场次 / 签到分组）
- 原 `DUPLICATE_REQUEST` 文案 "已提交过，请勿重复提交" 改为 "已签到，请勿重复"（更贴合点呼场景）
