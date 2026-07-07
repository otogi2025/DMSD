# 备份与恢复演练 SOP

> 覆盖两件事：§1 数据库定时备份（现状没有，本文件给出落地方案）；§2 恢复演练（备份从没被恢复验证过 —— **没做过恢复演练的备份只是一个愿望**）。
> 现状：唯一的备份形态是部署前手动 pg_dump（部署 SOP 的回滚点），非常态化；最近一次备份 5.8K —— 数据极小的现在正是把演练跑熟的零成本窗口。

## 0. 目标值

| 指标 | 含义 | 目标 |
|---|---|---|
| RPO（最多丢多少数据） | 灾难时刻回溯到最近一份可用备份的间隔 | 24 小时（每日备份）。点呼数据一晚一波，即使丢当晚也有纸质名单/老师改判可重建，24h 可接受 |
| RTO（恢复要多久） | 从决定恢复到服务可用的耗时 | 首次演练实测后定，初期目标 ≤ 60 分钟 |

## 1. 定时备份方案（待部署）

三层：**每日服务器本机备份（保留 14 天）→ 每周下载到 Mac（异地）→ 备份成功心跳监控**。

### 1.1 备份脚本

放服务器 `~/bin/db-backup.sh`（部署目录外，避免被 rsync 覆盖）：

```
#!/bin/sh
# Tomoshibi 数据库每日备份：pg_dump → gzip → 保留 14 天 → 成功后发心跳
set -eu
BACKUP_DIR="$HOME/backups"
STAMP=$(date +%Y%m%d-%H%M)
mkdir -p "$BACKUP_DIR"

cd "$HOME/tomoshibi-backend"
# -T：cron 环境没有终端，不加会失败
docker compose exec -T postgres pg_dump -U tomoshibi tomoshibi \
  | gzip > "$BACKUP_DIR/db-daily-$STAMP.sql.gz"

# 空文件守卫：备份产物小于 1KB 视为失败（连表结构都不足 1KB）
[ "$(stat -c%s "$BACKUP_DIR/db-daily-$STAMP.sql.gz")" -ge 1024 ]

# 清理 14 天前的旧备份
find "$BACKUP_DIR" -name 'db-daily-*.sql.gz' -mtime +14 -delete

# 成功心跳（healthchecks.io，见监控清单 P0-3；URL 配好后取消注释）
# curl -fsS -m 10 --retry 3 <healthchecks心跳URL> > /dev/null
```

### 1.2 crontab

**先 `timedatectl` 确认服务器时区再定时刻**（云主机常见默认 UTC）。目标是 JST 凌晨 3 点半（点呼后、日常低峰）：服务器为 UTC 时写 `30 18 * * *`，为 JST 时写 `30 3 * * *`。

```
crontab -e
# 加一行（UTC 服务器示例）：
30 18 * * * /home/<用户>/bin/db-backup.sh >> /home/<用户>/backups/backup.log 2>&1
```

### 1.3 异地副本（每周）

服务器和它的磁盘是同一个故障域（实例被误删/账号出问题时本机备份一起消失），每周把最新一份拉到 Mac：

```
# Mac 侧执行（目录沿用部署备份惯例）
scp <生产服务器>:~/backups/$(ssh <生产服务器> 'ls -t ~/backups/db-daily-*.sql.gz | head -1 | xargs basename') \
    ~/Downloads/tomoshibi-prod-backup-weekly/
```

真实数据进入系统（第二波）后，此步升级为每周固定日的例行动作并考虑自动化；当前阶段手动即可。

### 1.4 部署检查单（一次性）

- [ ] `timedatectl` 确认时区 → 定 cron 时刻
- [ ] 脚本放置 + `chmod +x` + 手动跑一次成功（产物 ≥1KB，能 `gunzip -t` 通过）
- [ ] crontab 生效，次日确认自动产物存在
- [ ] healthchecks.io 心跳接上（监控清单 P0-3），故意断一次验证告警
- [ ] `.env` / `Caddyfile` / `docker-compose.yml` 三个配置文件当前版本在 Mac 已有副本（部署 SOP 的 Phase 2 产物即可，配置不常变不进每日 cron）

> 部署是改生产动作，按惯例须 itsuki 明示后执行（可交给部署会话随下次部署一并做）。

## 2. 恢复演练 SOP

**目的**：证明「备份 → 可用的库」这条路真的走得通，并实测 RTO。方式沿用部署 SOP 的 migtest 惯例（服务器上一次性库），全程不碰生产库 `tomoshibi`。

1. **选备份**：`ls -t ~/backups/db-daily-*.sql.gz | head -1`（演练用最新一份；也可故意挑最旧的一份验证保留期内都可用）。开始计时。
2. **建一次性库**（名字固定 `migtest`，绝不用生产库名）：
   ```
   cd ~/tomoshibi-backend
   docker compose exec -T postgres createdb -U tomoshibi migtest
   ```
3. **恢复**：
   ```
   gunzip -c ~/backups/db-daily-<日期>.sql.gz \
     | docker compose exec -T postgres psql -q -U tomoshibi -d migtest
   ```
   观察有无报错输出；有错即演练失败，记录错误全文。
4. **验证清单**（全过才算恢复成功）：
   ```
   docker compose exec -T postgres psql -U tomoshibi -d migtest -c \
     "SELECT (SELECT count(*) FROM students)  AS students,
             (SELECT count(*) FROM teachers)  AS teachers,
             (SELECT version_num FROM alembic_version) AS migration;"
   ```
   - [ ] 三个值都能查出（表结构完整、迁移版本在）
   - [ ] students / teachers 行数与生产当前值一致（生产侧同款查询对 `tomoshibi` 库跑一遍对照）
   - [ ] migration 版本与生产一致
   - [ ] 抽查一张业务表内容非空且字段可读（如 `SELECT id, created_at FROM announcements LIMIT 3;`）
5. **停止计时** —— 这就是本次实测 RTO（真实灾难时还要加上「切换应用指向」的时间，做估算时加 10 分钟余量）。
6. **记录**：按 §3 模板写入演练记录。
7. **清理**：
   ```
   docker compose exec -T postgres dropdb -U tomoshibi migtest
   ```
   （敲这条前默念一遍库名是 migtest。）

## 3. 演练记录模板

追加记录在本文件末尾 §5，一次一行：

| 日期 | 用的备份 | 结果 | 实测恢复耗时 | 行数核对 | 问题与改进 |
|---|---|---|---|---|---|
| | | 成功/失败 | | 一致/不一致 | |

## 4. 频率

- 真宿舍上线前：**至少完整跑通一次**（上线门槛，不可跳过）。
- 常态：每学期一次 + 备份方案变更后一次。
- 每日备份的自动验证由脚本的空文件守卫 + 心跳监控兜底，演练管的是「恢复」这半边。

## 5. 演练记录

（尚无记录 —— 首次演练后从这里开始填。）

## 6. 与部署备份的关系

部署前的手动 pg_dump（部署 SOP Phase 2，作为回滚点）**继续照旧**，与本文件的每日定时备份互不替代：部署备份钉住「部署前一刻」的状态，每日备份保证平时任意一天挂掉最多丢 24 小时。回滚操作路径见故障手册 S10。
