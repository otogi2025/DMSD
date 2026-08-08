# 老师网页 teacher_web 生产部署与更新

> 记录 `teacher.tomoshibi.cc` 的实际部署形态与日常更新流程。
> 与 `teacher_web_v1.0_上线部署清单.md` 的区别：那份是上线前的准备清单（后端环境变量、seed、守卫），本文件是**已部署系统的现状与运维操作**。

## 1. 部署形态

| 项 | 值 |
|---|---|
| 访问地址 | `https://teacher.tomoshibi.cc` |
| 静态文件路径 | 生产服务器 `/var/www/teacher/` |
| 托管方式 | nginx 直接托管静态文件，不经过后端容器 |
| 接口转发 | `/api/` 与 `/ws/` 由 nginx 反代至 `127.0.0.1:8000`（后端 api 容器） |
| nginx 站点配置 | `/etc/nginx/sites-available/teacher.tomoshibi.cc` |
| 构建产物来源 | `dev/teacher_web/v1/dist/`（`npm run build` 输出） |
| 部署日 | 2026-07-29 |

前端 `src/theme.ts` 中 `API_BASE = "/api/v1"` 为相对路径，故网页与接口对浏览器而言同源，不产生跨域请求 —— 后端 `CORS_ORIGINS` 无需为本站点追加条目。

## 2. 架构决策：为何不使用后端容器托管

后端 `app/main.py` 支持通过环境变量 `TEACHER_WEB_DIR` 将 `dist/` 挂载到 `/teacher` 路径（`StaticFiles`），本地开发脚本 `start-teacher-web.command` 即采用该方式。生产部署未采用，理由如下：

1. **避免重启生产后端。** 该方案需修改 `docker-compose.yml`（增加卷挂载与环境变量）并重建 api 容器。生产后端同时服务已上架的 iOS 客户端，重启会造成短暂不可用。nginx 方案对后端容器零改动。
2. **独立域名需要独立站点配置。** 若走后端托管，访问路径为 `api.tomoshibi.cc/teacher/`；使用独立域名 `teacher.tomoshibi.cc` 本就需要新建 nginx 站点，在该站点内直接托管静态文件不增加复杂度。
3. **静态文件分发效率。** nginx 分发静态资源优于 FastAPI 的 `StaticFiles`，且可对带内容哈希的 `assets/` 目录设置长期缓存。

`TEACHER_WEB_DIR` 机制保留不变，本地开发仍在使用。

## 3. 日常更新流程

网页代码变更后，在 Mac 仓库执行：

```bash
cd dev/teacher_web/v1
npm run build
rsync -az --delete dist/ <生产服务器>:/var/www/teacher/
```

（`<生产服务器>` 的登录地址与用户名见本地文档，按仓库惯例不写入公开目录。）

`--delete` 保证服务器端与本地 `dist/` 完全一致，清除上一版遗留的哈希文件。无需重启 nginx 或后端容器 —— 静态文件即时生效。

浏览器可能因缓存仍加载旧版：`index.html` 不带哈希，但引用的 `assets/` 文件名含内容哈希，构建后文件名改变，强制刷新（Cmd+Shift+R）即可确认。

### 3.1 更新前备份与回滚

`rsync --delete` 会清掉服务器端旧文件，出问题无法就地撤销。故 rsync 之前先在服务器上整目录复制一份：

```bash
cp -a /var/www/teacher /var/www/teacher.bak_<日期>
```

回滚（把上一版换回来，静态文件即时生效，无需重载 nginx）：

```bash
rm -rf /var/www/teacher && mv /var/www/teacher.bak_<日期> /var/www/teacher
```

备份目录约 6 MB，确认新版稳定后删除即可。也可从 Git 回滚：切到旧 commit 重新 `npm run build` 再 rsync —— 但那要求旧 commit 的依赖仍能装上，直接留目录副本更稳。

### 3.2 部署前必须确认后端是否同步

本站与后端分开部署，前端传新版不会带上任何后端改动。若本次前端改动调用了后端新接口，而生产后端仍是旧版，网页会在运行时报错。部署前核对：

```bash
git log <上次部署的 tag 或 commit>..HEAD --oneline -- dev/backend
git diff <上次部署的 tag 或 commit>..HEAD -- dev/teacher_web/v1/src/api/
```

后端无代码改动、且前端 `src/api/` 无改动时，单独部署前端才是安全的。否则须先按 `.claude/skills/deploy-backend/SKILL.md` 部署后端。

## 4. HTTPS 证书

由 Let's Encrypt 签发，certbot 管理，已配置自动续期（systemd timer）。首次签发日 2026-07-29，有效期至 2026-10-27。

在生产服务器上手动检查续期状态：

```bash
certbot certificates
```

## 5. 故障排查

| 症状 | 检查项 |
|---|---|
| 网页 404 / 空白 | 服务器 `/var/www/teacher/index.html` 是否存在；`rsync` 是否成功 |
| 网页能开但登录报错 | `curl https://teacher.tomoshibi.cc/api/v1/teachers/public` 是否返回 `{"ok":true,...}`；否则查后端容器 `docker ps` 状态 |
| 502 Bad Gateway | 后端 api 容器未运行或未监听 `127.0.0.1:8000` |
| 座位看板不实时刷新 | WebSocket 未连通，检查 nginx 站点 `location /ws/` 的 `Upgrade` / `Connection` 头 |
| 证书过期告警 | `certbot renew --dry-run` 验证续期链路 |

nginx 配置变更后必须先验证再重载（在生产服务器上执行）：

```bash
nginx -t && systemctl reload nginx
```

## 6. 关联文档

- 后端生产部署 SOP：`.claude/skills/deploy-backend/SKILL.md`（本地）
- 生产故障对应手册：`ops/生产故障对应手册.md`
- 监控告警清单：`ops/监控告警清单.md`
- 老师网页设计日志：`dev/teacher_web/WEB_DESIGN_LOG.md`
