# 03_dev/backend/v1/

**v1.0 正式版后端 — 未开始**。

## 启动条件

v1.0 后端开发需要先完成：
- [ ] `02_design/system_features.md` 重写（以老师 38 条需求 + Q1-12 答案 + R1-R4 硬约束 + itsuki 4 条砍/留 为锚）
- [ ] 老师 12 个 Q 全部答复（部分已收到 4-29，部分还要再问）
- [ ] 数据库 schema 设计（从 SQLite → PostgreSQL，覆盖 v1.0 全功能）
- [ ] 认证体系实装（教师每人单独账号 / R3）

## 起点

从 `../demo/` 复制需要的代码（demo 已经验证了 NFC + WebSocket + 座位表实时更新流程），但需要重写：
- seed → 真实数据导入
- SQLite → PostgreSQL
- demo 简化认证 → 完整账号体系
- 邮件通知（R1）
- 角色权限（5 角色）
