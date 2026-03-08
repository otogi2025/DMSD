# DMSD v1.0 枚举字典（唯一取值）

更新时间：2026-02-12

## 1. session_type
- `morning`
- `evening`

## 2. session_status
- `draft`
- `running`
- `ended`

## 3. background_status（对应 base_status）
- `init`
- `present`
- `late`
- `absent`
- `exempt_range`

## 4. overlay_badge
- `health_issue`
- `absence_request_pending`

## 5. status_source
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

## 8. 大小写与拼写规则
- 全部采用小写蛇形或小写单词。
- 枚举值必须逐字匹配，不允许别名。
- 前后端代码直接拷贝本文件取值，禁止二次命名。
