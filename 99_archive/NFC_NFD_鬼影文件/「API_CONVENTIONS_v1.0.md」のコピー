# DMSD v1.0 API 全局约定

更新时间：2026-02-12

## 1. 统一响应包裹格式（强制）
- 成功：
```json
{ "ok": true, "data": { } }
```
- 失败：
```json
{ "ok": false, "error": { "code": "INVALID_INPUT", "message": "...", "detail": {} } }
```
- 禁止在 `data` 内再次嵌套 `ok` 字段。

## 2. 鉴权与角色（最小可跑）
- Header：`Authorization: Bearer <token>`
- 学生 token 只允许访问 `/student/*`
- 老师 token 只允许访问 `/teacher/*`

## 3. 本地开发联调方案（第 16 条，已拍板）
- 采用 `/auth/dev_login`（仅开发环境可用）。
- 生产环境必须关闭该接口。
- `dev_login` 返回固定测试账号 token，最少包含：
  - `student_demo`
  - `teacher_demo`

## 4. 时间基准
- 所有判定一律基于 `server_now (JST)`。
- 前端只展示倒计时，不参与业务判定。

## 5. scheduled 与 effective 规则
- 两者都存在时，一律使用 `effective_*_at`。
- `scheduled_*` 仅用于配置展示与回溯。

## 6. 倒计时公式（唯一）
- `remaining_seconds = max(0, effective_late_end_at - server_now)`
- 禁止使用 `ended_at` 参与倒计时计算。

## 7. settle 规则（唯一）
- `settle_at = min(ended_at, effective_auto_end_at)`
- 结算时将 `init -> absent`
- 排除：
  - `exempt_range`
  - `absence_request_pending`
- 结算后：`session_status = ended`
- 老师改判必须填写 `override_reason` 并写审计日志。
