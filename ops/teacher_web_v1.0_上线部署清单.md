# teacher_web + 后端 v1.0 生产上线部署清单

> ⚠️ **本文件是 2026-06-14 写的上线前计划书，部分内容已被实际部署超越，勿直接照做。**
> - 后端已于 2026-06-18 部署生产、2026-07-22 迁至现服务器，实际以 docker compose 编排（本文件写的是裸机 uvicorn 起法）。
> - 老师网页已于 2026-07-29 部署至 `teacher.tomoshibi.cc`，采用 nginx 直接托管静态文件，非本文件 §2 步骤 6 所列的甲/乙两方案 —— 现状与更新流程见 `ops/teacher_web_生产部署与更新.md`。
> - §1 邮件变量已从 SendGrid 改为 Resend（`RESEND_API_KEY`），§5「NFC 防代刷后端零实装」已于 2026-07-17 实装收口。
>
> 仍然有效的部分：§1 必设环境变量表、§4 已实装的守卫说明。
>
> 起因：teacher_web v1.0 代码已就绪（codex 5 轮复审 0 阻塞），但「能上线」还差 ops（运维）这步 —— 设环境变量 + 建表 + 起服务。后端加了「漏配就拒绝启动」的守卫，本清单把这些步骤列全。
> 适用：后端 `dev/backend/v1`（FastAPI + PostgreSQL）+ 老师网页 `dev/teacher_web/v1`。

## 1. 环境变量（写进 `dev/backend/v1/.env`）

### 必设 —— 不设生产会拒绝启动（config.py 的 fail-fast 守卫）

| 变量 | 值 | 说明 |
|---|---|---|
| `APP_ENV` | `production` | 不设默认 dev；生产必须显式设 |
| `JWT_SECRET` | 32+ 字符强随机串 | 登录令牌签名密钥。用 `openssl rand -hex 32` 生成。弱值/默认/不足 32 字符 → 拒绝启动 |
| `DATABASE_URL` | `postgresql+psycopg://用户:密码@主机:5432/库名` | 生产用 PostgreSQL；填 SQLite → 拒绝启动 |
| `CORS_ORIGINS` | `https://你的老师网页域名` | 允许跨域的真实域名（逗号分隔多个）。含 localhost / `*` / 空 → 拒绝启动 |

### 生产首次 seed（灌初始账号）必设 —— 缺则 seed 拒绝执行

| 变量 | 说明 |
|---|---|
| `ADMIN_INITIAL_PASSWORD` | admin 教师初始密码 |
| `REVIEWER_PASSWORD` | Apple 审核员账号密码（App Store 审核用） |
| `REVIEWER_REGISTRATION_CODE` | 审核员永久注册码 |

### 可选

| 变量 | 说明 |
|---|---|
| `TEACHER_WEB_DIR` | 老师网页静态文件目录（如指向 `dev/teacher_web/v1/src`）。设了后端就在 `/teacher` 挂载 serve 网页（同源部署）；不设则跳过（网页另外单独 serve） |
| `SENDGRID_API_KEY` + `EMAIL_FROM` + `EMAIL_FROM_NAME` | 邮件通知（出寮届审批通知学生等）。不设邮件发不出 |
| `APNS_KEY` / `APNS_KEY_ID` / `APNS_TEAM_ID` / `APNS_BUNDLE_ID` / `FCM_KEY` | 手机推送凭证。**当前 push 只有后端骨架，真投递要 iOS/Android 集成，v1.0 不必设** |

## 2. 部署步骤

```bash
cd dev/backend/v1

# 1. 装依赖（虚拟环境）
.venv/bin/pip install -r requirements.txt   # 或 uv / poetry，按项目实际

# 2. 写 .env（按上面必设清单），确认 APP_ENV=production + DATABASE_URL 指 PostgreSQL

# 3. 建表 —— 跑数据库迁移（alembic 已改成读 DATABASE_URL，会建到生产 PostgreSQL）
.venv/bin/python -m alembic upgrade head

# 4. 灌初始账号（admin + 审核员），需上面 3 个 seed 环境变量
APP_ENV=production .venv/bin/python seed.py

# 5. 起后端服务
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
#   （生产建议挂 gunicorn + uvicorn worker + 反向代理 nginx + HTTPS）

# 6. 老师网页：
#   方案甲 同源 —— 设 TEACHER_WEB_DIR，后端 /teacher 路径 serve（网页里 API_BASE 已是相对 /api/v1）
#   方案乙 分离 —— 网页单独静态托管，改 index.html 的 window.API_BASE 为后端绝对地址 + CORS_ORIGINS 配网页域名
```

## 3. 上线前检查清单

- [ ] `.env` 里 `APP_ENV=production`、`JWT_SECRET` 强随机、`DATABASE_URL` 指 PostgreSQL、`CORS_ORIGINS` 真实域名
- [ ] `ADMIN_INITIAL_PASSWORD` / `REVIEWER_PASSWORD` / `REVIEWER_REGISTRATION_CODE` 已设
- [ ] `alembic upgrade head` 跑通、PostgreSQL 里表都建出来了
- [ ] `seed.py` 跑过、admin 能登录
- [ ] 后端起来后 `GET /healthz` 返 200
- [ ] HTTPS 配好（点呼签到走 NFC URL，必须 HTTPS）
- [ ] 老师网页能打开、能登录、能拉到真数据（不是空白/报错）
- [ ] 数据库定时备份配好

## 4. 已实装的守卫（漏配会主动报错，不会偷偷用弱默认值起服务）

- 生产 `JWT_SECRET` 弱/空/不足 32 字符 → 启动 raise（config.py _validate_production_settings）
- 生产 `CORS_ORIGINS` 含 localhost / `*` / 空 → 启动 raise
- 生产 `DATABASE_URL` 是 SQLite → 启动 raise
- 生产 seed 缺 3 个密钥环境变量 → seed.py raise 拒绝执行（不灌弱密码假数据）
- 启动时大声 log 当前 APP_ENV；检测到 PostgreSQL 却非 production 模式 → WARNING

## 5. 尚未做（不影响核心上线，但要知道）

- **NFC 防代刷后端零实装** —— 见 `design/NFC防代刷_后端立项施工计划.md`。当前点呼签到没有 nonce 校验 + ECDSA 验签 + 卡绑定，真防代刷要单独立项做。
- **push 推送只有后端骨架** —— 真投递要 APNs/FCM 凭证 + iOS/Android 集成。
