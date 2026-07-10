# dev/backend/

后端代码的总目录。**demo/ 锁定不动 / v1/ 是 v1.0 正式版开发位置**。

## 目录

| 目录 | 用途 | 状态 |
|---|---|---|
| `demo/` | 管理员演示用的 FastAPI（FastAPI + SQLAlchemy + SQLite + WebSocket）| **锁定** — demo 已通过管理员认可，反复给管理员看用，**不再改动** |
| `v1/` | v1.0 正式版后端（FastAPI + SQLAlchemy + Alembic；本地开发 SQLite，生产 PostgreSQL）| **实装中** — 实装进度以 `BACKEND_DESIGN_LOG.md` 顶部「实装进度速查表」为真值；路由清单以 `v1/app/routers/` 目录为准，迁移链以 `v1/alembic/versions/` 为准（本表不硬编码数字）|

## 规则（2026-04-29 itsuki 拍板）

> 「demo 的文件单独放在一个文件夹里，然后具体可以用到正式版的东西就复制一份就好了，demo 的文件不要动」

- demo/ 内容：demo sprint 期间一次性产物（含 demo seed 数据 / 简化的认证 / 内存管理 WebSocket / SQLite）
- v1/ 内容：上线版后端，需要满足 v1.0 全部功能（账号体系 / 出寮届 / 学习 / 点呼 / 行事 / 食堂 Excel 导出 / 教师指导历 / 事案录入 等），本地开发 SQLite / 生产 PostgreSQL 双轨，权威源 `design/system_features.md`

## 启动 demo

```bash
cd dev/backend/demo   # 注意：是 demo/ 子目录，不是 backend/ 根
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

demo/README.md 属锁定内容，其中「怎么跑」一节写的 `cd dev/backend` 是拆目录前的旧路径 — 以上面这段为准（demo 代码和 requirements.txt 都在 `dev/backend/demo/` 下）。其余说明详见 `demo/README.md`。
