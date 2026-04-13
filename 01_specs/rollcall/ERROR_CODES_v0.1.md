# DMSD v0.1 错误码字典

更新时间：2026-02-12

## 1. 全局最小集合（固定）
- `UNAUTHORIZED`
- `FORBIDDEN`
- `INVALID_INPUT`
- `NOT_FOUND`
- `SESSION_NOT_RUNNING`
- `TIMEOUT`
- `DUPLICATE_REQUEST`
- `ALREADY_RUNNING`

## 2. 前端文案映射（固定）
- `TIMEOUT` -> `点呼已截止`
- `SESSION_NOT_RUNNING` -> `老师还没开始点呼`
- `DUPLICATE_REQUEST` -> `已提交过，请勿重复提交`
- `UNAUTHORIZED` -> `登录已失效，请重新登录`
- `FORBIDDEN` -> `你没有该操作权限`
- `INVALID_INPUT` -> `提交内容有误，请检查后重试`
- `NOT_FOUND` -> `数据不存在或已被删除`
- `ALREADY_RUNNING` -> `点呼已在进行中`

兜底文案：
- 未知错误码 -> `系统繁忙，请稍后重试`

## 3. 使用规则
- 业务错误必须返回上述 code。
- 接口失败时格式必须为：
```json
{ "ok": false, "error": { "code": "TIMEOUT", "message": "..." } }
```
