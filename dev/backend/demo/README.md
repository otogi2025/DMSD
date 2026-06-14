# Tomoshibi Backend (Demo Sprint v1) — 项目代号 DMSD

> 宿舍管理员演示用后端。系统对外名 **Tomoshibi**（灯火，2026-04-21 定名）；项目/仓库代号 DMSD。用途：向宿舍管理员现场演示「手机签到 → 后端 → 实时看板」最小闭环，验证核心流程可行性；正式版（`../v1/`）在此基础上重写。
>
> **Demo 版特性**：SQLite（零配置）+ FastAPI + WebSocket 实时推送。部署版后续迁 PostgreSQL。

## 技术栈

- **Python 3.11+**
- **FastAPI** — Web 框架。为什么选它：比 Flask 多出"自动文档 + 数据验证 + async 原生支持"；比 Django 轻；**每个 API 自动生成 Swagger 文档**（老师 Web 联调时不用猜字段）
- **SQLAlchemy** — ORM（对象关系映射）。让 Python 代码操作数据库，不用手写 SQL。Demo 用 SQLite，部署版只改一行就能切 PostgreSQL
- **SQLite**（demo）/ **PostgreSQL**（部署）— 数据库
- **websockets** — 实时推送（老师 Web 实时看到签到事件）
- **uvicorn** — 跑 FastAPI 的服务器

## 文件结构

```
backend/
├── README.md              # 本文件
├── requirements.txt       # Python 依赖清单
├── db_schema.sql          # 数据库表结构参考（SQLAlchemy 实际建表用 models.py）
├── main.py                # FastAPI 主程序（启动点）
├── models.py              # 数据库表定义（SQLAlchemy）
├── database.py            # 数据库连接
├── schemas.py             # Pydantic 数据模型（API 输入输出验证）
├── ws_manager.py          # WebSocket 连接管理
└── dmsd.db                # SQLite 数据库文件（运行后自动生成，已在 .gitignore）
```

## 怎么跑（本地 Mac / Pi 3A+ 都一样）

### 第一次设置

```bash
# 1. 进入 backend 目录
cd dev/backend

# 2. 创建 Python 虚拟环境（避免污染系统 Python）
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate   # Mac/Linux
# Windows: venv\Scripts\activate

# 4. 装依赖
pip install -r requirements.txt
```

### 启动服务

```bash
# 虚拟环境已激活的前提下：
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` = 改代码自动重启（开发期用）
- `--host 0.0.0.0` = 让 Pi / iPhone / iPad 都能访问（不只是 localhost）
- `--port 8000` = 端口号

### 看自动文档

浏览器访问：http://localhost:8000/docs

FastAPI 自动生成的 Swagger UI，可以直接在网页上测试每个 API。

## API 概览

见 `main.py` 或启动后访问 `/docs`。

| Method | Path | 功能 |
|---|---|---|
| POST | `/api/login` | 老师登录 |
| GET | `/api/students` | 学生列表 |
| POST | `/api/checkin` | 签到（手机快捷指令 / 点呼机卡）|
| POST | `/api/roll-call/start` | 开始点呼 |
| POST | `/api/roll-call/end` | 结束点呼 |
| GET | `/api/roll-call/sessions` | 点呼会话列表 |
| GET | `/api/checkins` | 签到记录查询（`?date=YYYY-MM-DD`）|
| POST | `/api/outstay` | 学生提交外宿申请 |
| GET | `/api/outstay` | 外宿列表（老师）|
| PATCH | `/api/outstay/{id}` | 审批外宿 |
| POST | `/api/return-home` | 学生提交归国申请 |
| GET | `/api/return-home` | 归国列表 |
| PATCH | `/api/return-home/{id}` | 审批归国 |
| WS | `/ws/teacher` | 老师 Web 订阅实时签到 / 新申请事件 |

## Demo 数据

启动时会自动建表（SQLAlchemy `create_all`）。可以跑 `seed.py`（TODO）灌测试学生。

## Demo 场景 curl 测试（快捷指令代 App 的原理）

```bash
# 模拟 itsuki 签到（相当于 iOS 快捷指令做的事）
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "method": "shortcut"}'
```

## 后续迁 PostgreSQL

只需改 `database.py` 一行：

```python
# 改前（demo）:
DATABASE_URL = "sqlite:///./dmsd.db"

# 改后（部署）:
DATABASE_URL = "postgresql://user:password@localhost/dmsd"
```

其他代码不用改。
