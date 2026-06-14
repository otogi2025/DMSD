# Tomoshibi Backend — 日本 VPS 部署 SOP

> **前提**：itsuki 已经租到日本 VPS（推荐 Sakura / Conoha / Vultr Tokyo）+ 买好域名（如 tomoshibi.cc）。
>
> **目标**：跑出公网可访问的 `https://api.tomoshibi.cc`，给 iOS app 上架版用。

---

## 0. VPS 推荐 + 大致价格（2026-05 时点）

| 服务商 | 最便宜套餐 | 月费 | 备注 |
|---|---|---|---|
| Vultr Tokyo | 1 vCPU / 1 GB / 25 GB SSD | $6/月 | 推荐 — 5 分钟创建、付按月 |
| Sakura VPS（さくらの VPS） | 1 vCPU / 1 GB / 25 GB SSD | ¥1,098/月 | 日本本土公司、稳定性高 |
| Conoha VPS | 1 vCPU / 1 GB / 100 GB SSD | ¥968/月 | 日本本土、容量大 |
| 自分の Mac mini を VPS 化 | — | 0 | ⚠️ 不推荐：宅 IP 不稳定 + 端口转发麻烦 + Apple 审核期间断电就 reject |

**推荐选 Vultr Tokyo 或 Sakura VPS** — 跑 docker compose（FastAPI + Postgres + Caddy）够。

---

## 1. VPS 初始化（开机后第一件事）

SSH 到 VPS（itsuki 自己机器）：
```bash
ssh root@VPS公网IP
```

### 1.1 创建非 root 用户 + 装基础工具
```bash
# 创建 deploy 用户（不用 root 跑应用，安全惯例）
adduser deploy
usermod -aG sudo deploy

# 装基础工具
apt-get update && apt-get install -y \
    docker.io docker-compose-plugin \
    git curl ufw fail2ban

# 让 deploy 用户能跑 docker
usermod -aG docker deploy
```

### 1.2 防火墙 + SSH 加固
```bash
# 只开 22 (SSH) / 80 (HTTP) / 443 (HTTPS)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# fail2ban 默认 SSH 防暴力破解（开箱即用）
systemctl enable --now fail2ban
```

### 1.3 切到 deploy 用户
```bash
su - deploy
```

---

## 2. 域名 DNS 解析

在域名注册商面板（Cloudflare / Namecheap / Route 53 / Sakura DNS 等）：

```
A 记录:  api.tomoshibi.cc  →  VPS 公网 IP
```

⚠️ **DNS 解析等候 1-24 小时生效**。验证：
```bash
dig +short api.tomoshibi.cc
# 预期返回 VPS 公网 IP
```

---

## 3. 拉代码 + 配环境变量

```bash
# 在 VPS deploy 用户家目录
cd ~

# Tomoshibi-AppStore fork 没在 GitHub 上 → itsuki 用 rsync / scp 从 Mac 推到 VPS
# Mac 端跑：
#   rsync -avz --exclude='.venv' --exclude='__pycache__' \
#     ~/dev/Tomoshibi-AppStore/backend/ deploy@VPS_IP:~/tomoshibi-backend/
# 或者先 git init + push 到 GitHub 私库（itsuki 后续决定）

cd ~/tomoshibi-backend

# 配环境变量
cp .env.example .env
nano .env

# 必改的字段：
# - POSTGRES_PASSWORD = openssl rand -base64 24 生成的强密码
# - JWT_SECRET = openssl rand -hex 32 生成的 64 hex 字符
# - CORS_ORIGINS = https://api.tomoshibi.cc（Apple 审核期保持只一条；teacher_web 上线后加）

# 生成强值用的命令：
openssl rand -base64 24   # POSTGRES_PASSWORD 用
openssl rand -hex 32      # JWT_SECRET 用
```

### 改 Caddyfile 域名

打开 `Caddyfile`，把 `api.tomoshibi.cc` 替换成 itsuki 实际买的域名。

---

## 4. 启动 stack

```bash
# 第一次启动（拉镜像 + build api 镜像 + 启动）
docker compose up -d --build

# 看日志确认启动正常
docker compose logs -f api
# 预期：Uvicorn running on http://0.0.0.0:8000
# Ctrl+C 退出 log 流（不停 service）

docker compose logs -f caddy
# 预期：obtained certificate from Let's Encrypt
# 如果看到 "challenge failed" → 检查 DNS 是否指向 VPS / 80 端口是否开
```

---

## 5. 跑 Migration + Seed

```bash
# 跑 alembic migration（创建所有表）
docker compose exec api alembic upgrade head

# 跑 production seed（创建 admin + reviewer 学生 + reviewer 注册码）
docker compose exec api python -m seed
```

输出会打印：
```
admin login: admin / 密码: ChangeMe-2026-05（上线后立刻在 web 后台改）
reviewer 学号: 060199 / 密码: Reviewer-2026
reviewer 注册码: 999999（2030 过期）
```

⚠️ **把这 3 条凭证记下来** — Apple 提交审核时填到 Reviewer Notes。

---

## 6. 验证

### 6.1 公网可达
```bash
# 从 VPS 内：
curl http://localhost:8000/healthz
# 预期：{"status": "ok"} 或类似

# 从 Mac（关 Wi-Fi、4G 测试）：
curl https://api.tomoshibi.cc/healthz
# 预期：200 + JSON
# 如果失败 → 检查 DNS / 防火墙 / Caddy 日志
```

### 6.2 iOS app 真机连
- iOS app 上架版 Release build 默认连 `https://api.tomoshibi.cc`
- 装到真机 → 用 reviewer 学号 `060199` + 密码 `Reviewer-2026` 登录 → 进 home 即成功

### 6.3 监控（Apple 审核期间必须 100% 在线）
- 注册 [UptimeRobot](https://uptimerobot.com) 免费账号（50 monitors）
- 加 monitor：`https://api.tomoshibi.cc/healthz` 每 5 分钟检查
- 配邮件告警 → 挂了 itsuki 邮箱收通知

---

## 7. 日常运维

```bash
# 看运行状态
docker compose ps

# 重启某服务
docker compose restart api

# 看日志
docker compose logs -f api          # API 日志
docker compose logs -f caddy        # HTTPS / 反代日志
docker compose logs -f postgres     # DB 日志

# 备份 DB（每天定时跑，用 crontab）
docker compose exec postgres pg_dump -U tomoshibi tomoshibi | gzip > ~/backup-$(date +%Y%m%d).sql.gz

# 升级（itsuki 改了代码后从 Mac 推新代码到 VPS 后）
cd ~/tomoshibi-backend
docker compose up -d --build api    # 只重 build api、不动 db / caddy
```

---

## 8. 常见问题

### Caddy 报 "challenge failed"
- DNS 没生效 → `dig +short api.tomoshibi.cc` 看返回 IP 是不是 VPS
- 端口 80 没开 → `ufw status` 检查
- VPS 服务商防火墙（如 Vultr 面板里的 "Firewalls"）也要开 80/443

### Postgres 启动失败
- 看 logs：`docker compose logs postgres`
- 通常是 `POSTGRES_PASSWORD` 没设或包含特殊字符 → 改 .env 用 base64 干净密码

### iOS app 真机连不上 prod URL
- 真机连 4G（不是 Wi-Fi）测 — 排除家庭网络问题
- Safari 打开 `https://api.tomoshibi.cc/docs`（FastAPI 自带 swagger）应该能看到 API 文档

---

## 9. 上架审核期间的注意事项

- **审核期 24-72h 内 backend 必须 100% 在线** — 重启 / 升级 / 维护尽量避开
- **reviewer 凭证泄漏没关系** — 只创建一个 demo 学生 + admin，其他真实数据由 itsuki 上线后通过 web 添
- **审核员 IP 不固定** — 不能 IP 白名单。
- **HTTPS 自签证书会被 Apple 拒** — 必须用 Let's Encrypt（Caddy 自动）

---

## 10. 升级 / 数据迁移到主项目（v1.0 全 dev → prod 时）

当 itsuki 想把这个生产 backend 替换成主项目的（Tomoshibi-AppStore fork 退役）时：
1. 备份生产 DB（pg_dump）
2. 用主项目 backend 镜像替换（重 build）
3. 跑 alembic upgrade head（迁移到主项目最新 schema）
4. 监控异常

但本 plan 范围内**不需要做这事** — 上架版 fork 跑到 v1.0 上架成功后再说。
