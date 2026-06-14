# dev/backend/

后端代码的总目录。**demo/ 锁定不动 / v1/ 是 v1.0 正式版开发位置**。

## 目录

| 目录 | 用途 | 状态 |
|---|---|---|
| `demo/` | 4-28 管理员 demo 用的 FastAPI（FastAPI + SQLAlchemy + SQLite + WebSocket）| ⚠️ **锁定** — demo 已通过老师认可，反复给老师看用，**不再改动** |
| `v1/` | v1.0 正式版后端（FastAPI / PostgreSQL）| 🔄 **实装中**（2026-05-12 校准）— 8 个 router 已挂载（auth/applications/accounts/admin_registration_code/announcements/study/rollcall/teachers）+ 6 个 alembic migration。部分 P1/P2 待续：NFC 防作弊 card_uid 全栈实装 / WebSocket + Redis / refresh_token rotation / DELETE /accounts/me / 整点 session minute-5 bug |

## 规则（2026-04-29 itsuki 拍板）

> 「demo 的文件单独放在一个文件夹里，然后具体可以用到正式版的东西就复制一份就好了，demo 的文件不要动」

- demo/ 内容：4-28 demo sprint 期间一次性产物（含 demo seed 数据 / 简化的认证 / 内存管理 WebSocket / SQLite）
- v1/ 内容：上线版后端，需要满足 v1.0 全部功能（账号体系 / 出寮届 / 学习 / 点呼 / 行事 / 食堂 Excel 导出 / 教师指导历 / 事案录入 等），数据库 PostgreSQL，权威源 `design/system_features.md`

## 启动 demo

```bash
cd dev/backend/demo
# 详见 demo/README.md
```
