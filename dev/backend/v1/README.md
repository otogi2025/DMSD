# dev/backend/v1/

Tomoshibi v1.0 正式版后端 — FastAPI + SQLAlchemy 2.x + Alembic。本地开发用 SQLite（`tomoshibi_dev.db`），生产用 PostgreSQL（docker-compose）。

---

## 当前状态

实装进度以 `../BACKEND_DESIGN_LOG.md` 顶部「实装进度速查表」为真值，本文件不复述数字（历史证明硬编码必漂移）。

- 端点总表：看 `openapi_snapshot.json`，或启动后访问 `http://localhost:8000/docs`
- 路由清单：以 `app/routers/` 目录为准（认证 / 申请 / 点呼 / 学习 / 扣分 / 清扫 / 前台 / 指导 / 事案 / 通知 / WebSocket 等）
- 数据库迁移链：以 `alembic/versions/` 目录为准
- 测试清单：以 `tests/` 目录为准

---

## 启动（本地开发）

```bash
cd dev/backend/v1

# 虚拟环境 + 依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 配置
cp .env.example .env

# 数据库迁移（切分支 / 拉新代码后必跑 — 存量库表结构落后时接口会 500）
.venv/bin/alembic upgrade head

# 开发用假数据投入
python -m seed

# 启动服务
python -m app.main
# → http://localhost:8000/docs 查看 OpenAPI UI
```

---

## 测试

```bash
cd dev/backend/v1
.venv/bin/python -m pytest        # 全量约 3 分钟
```

必须用项目自带虚拟环境（系统 Python 未装 fastapi，裸跑 `pytest` 必失败）。测试用独立测试库自动重建，不碰开发库。覆盖面以 `tests/` 目录下各测试文件为准（点呼 / 权限矩阵 / 演示隔离 / 迁移回归等）。

---

## 邮件服务（Resend）

邮件发送实现在 `app/services/email.py`，走 Resend HTTP API。

- `.env` 中 `RESEND_API_KEY` 留空 = 开发模式，只记日志不真发邮件
- 填入真实密钥（`re_` 开头）= 实际发送
- SendGrid 已弃用（`config.py` 中 `sendgrid_api_key` 仅为兼容旧 `.env` 保留，不再使用）

---

## 目录骨架

只画一层骨架，文件级清单以目录本身为准：

```
v1/
├── app/
│   ├── main.py                  # FastAPI 入口（lifespan + 路由注册 + 库结构自检）
│   ├── config.py                # 设置（BaseSettings）
│   ├── database.py              # SQLAlchemy engine + Session
│   ├── deps.py                  # 依赖注入（当前学生 / 当前教师）
│   ├── security.py              # JWT + bcrypt
│   ├── models.py                # ORM 表定义
│   ├── schemas.py               # Pydantic v2 输入输出模型
│   ├── permissions.py           # 教师权限分级
│   ├── audit.py                 # 审计日志
│   ├── ratelimit.py             # 限流
│   ├── ws_manager.py            # WebSocket 连接管理
│   ├── routers/                 # 各功能路由（清单以本目录为准）
│   └── services/                # 领域服务（审批链 / 邮件 / 食数 / 推送 / 学生受众）
├── tests/                       # pytest 测试（清单以本目录为准）
├── alembic/                     # 数据库迁移链（versions/ 为准）
├── seed.py                      # 开发用假数据投入
├── Dockerfile / docker-compose.yml / Caddyfile / DEPLOY.md   # 生产部署四件套
├── openapi_snapshot.json        # 端点快照
├── requirements.txt / pyproject.toml / .env.example
└── README.md
```

---

## 相关文档

- 后端设计权威源：`../BACKEND_DESIGN_LOG.md`（含实装进度速查表）
- 共用功能设计：`design/system_features.md`
- 生产部署流程：`DEPLOY.md`
- demo 版（管理员演示用，锁定不改）：`../demo/`
