# teacher_web v1.0 施工进度（活文档 — 压缩后读这个接着干）

> 这是 itsuki 2026-05-30 下达「teacher_web 做到 v1.0 能上线」任务的**进度协调文件**。
> CC 上下文压缩（compact）后**先读本文件**恢复状态再继续。每完成一步就更新本文件。
> 配套：分析见 `teacher_web_v1.0_上线施工计划_2026-05-30.md`；审查见 `audit_2026-05-30_teacher_web后端_v1上线审查.md`。

## 目标 + 关键决策

- 目标：老师网页 teacher_web + 后端做到直接上线 v1.0；网页↔后端↔iOS 接口对齐能互传；自审到 0 bug 再让 codex 复审。
- **iOS 当对齐标准，只读不改**（itsuki 明确「iOS 不用管，只管网页」）。
- **6 大模块 + push 全本期做**（itsuki 2026-05-30 拍板「6 大模块全本期做」）。
- git 分工：CC 可自主 commit（不 push、不写 Co-Authored-By）；每波做完即 commit。
- 上下文：到 ~400k 靠 compact 压缩，靠本文件保信息。

## 关键事实（架构 / 验证）

- 网页源头 = `03_dev/teacher_web/v1/src/index.html`（巨型单文件，浏览器 babel 现编译，无 npm 构建）。`src/components/_legacy/` 是废弃旧源，不用。
- 接口封装 `src/api/client.js`，对象 = `window.tomoshibiApi`，页面用 `window.tomoshibiApi.fn(...)` 调。
- **网页验证**：`cd 03_dev/teacher_web/v1 && node check_jsx.js`（要 0 错误）+ `node --check src/api/client.js`。
- 后端 `03_dev/backend/v1`（FastAPI + SQLAlchemy + Alembic + pytest）。**后端验证**：`pytest`（基线已到 95 passed）。models 在 `app/models.py`，schema 在 `app/schemas.py`，路由 `app/routers/`，注册在 `app/main.py`。
- iOS 契约：JSON 全 snake_case；列表响应用 `{items:[...]}` 包装（如 AnnouncementListOut/StudentAccountListOut）；错误 `{detail:...}`。
- **有并行会话**在动同 repo（改了 applications.py / .gitignore / WEB_DESIGN_LOG / 建了 05_logs/audit_2026-05-30/findings.md）。提交时**只 stage 自己改的文件**，别扫别人的。
- 共享文件冲突防御：models.py / schemas.py / main.py / index.html 都是共享单文件 → 改它们的活**必须串行**，禁止并行 agent 同时改。

## 已完成（已 commit）

| 波 | 内容 | commit | 验证 |
|---|---|---|---|
| W1 | 后端 7 崩溃/逻辑 bug（漏 import 500 ×3 / 窗口<5 崩 / 外宿误扣 / 缺日期上界 / UTC 归错月） | d9e65f1 | 95 测试 |
| W2 | 三边对齐（WebSocket 路径补 /api/v1；核实公告/错误/出寮届字段已对齐 iOS） | d9e65f1 | 读码核实 |
| W3 | 网页接已有后端 13 死接口（扣分/前台/清扫/公告/出寮届写操作 + 修 3 丢渲染 bug） | d9e65f1 | check_jsx + 字段核对 |
| W5 | 学生账号管理后端（GET /students、POST /accounts/{id}/password-reset、unlock）+ 网页账号页/搜索页接入 | 7f638a5 | 25 新测试 |
| W6后端 | seed 密钥 fail-fast（SEC-4）+ 启动环境守卫（RUN-1） | 29d6c3f | 95 测试 |
| W6网页 | 删 demo（ShortcutsDemoCard/DemoConsole/poll）+ 语音移植 WebSocket + API_BASE→/api/v1 + 删 demo_server.py | 4c2578f | check_jsx 0 错 |

## 待做

### W6b — ROSTER 假名单重接真后端（小，明确）
- `window.ROSTER_*` 还被 5 处用：全局搜索(shell)、点呼着陆(roll-call-landing)、记录页(RecordsPage) → 改用 `listStudents` 后端；LiveRollCall 的 `seedStudents` 回退删掉靠 rollcallBoard；通知页 NotificationsPage 用 roster 造假名 → 见 W7。
- 全解决后删 `window.ROSTER_*` / `seedStudents` / `window.TEACHERS` / 其它死数据数组（ACCOUNTS/OUTSTAY_APPS/FRONT_*/NOTICE_POSTS）定义。
- 还有 LiveRollCall 里 `showConsole` state + `simCheckin` 死代码待清。

### W7 — 6 大模块 + push：✅ 后端全做完（4 组 commit，153 测试，迁移链验证），⏳ 网页 UI 待做

**新接口清单（前端 UI 要接的，全 snake_case，list 用 {items} 或聚合结构）**：
- 行事予定：`GET/POST/PATCH/DELETE /api/v1/events`（增删改限寮務管理）
- 巴士：`GET /api/v1/bus/routes`(+`/{id}`)、`POST/PATCH/DELETE`（DELETE 软停用）
- 指導履歴：`POST/GET /api/v1/students/{id}/guidance`、`POST /api/v1/students/{id}/guidance/disclosure-request`(学生)、`GET /api/v1/guidance/disclosure-requests`、`POST /api/v1/guidance/disclosure-requests/{id}/decision`
- 事案：`POST/GET /api/v1/incidents`、`GET/PATCH/DELETE /api/v1/incidents/{id}`
- 个人档案：`GET /api/v1/students/{id}/profile`（聚合 出寮届/学習/点呼/指導/扣分）
- 一括进级：`POST /api/v1/students/bulk-promote`（body 带 dry_run，默认 true 预览）
- push：`POST /api/v1/notifications/device-token`（学生端，teacher_web 不接）

**网页 UI 待做**（全在 index.html，串行；client.js 加对应函数）：
- 行事予定 + 巴士 → CommunityPage（现用假 bus seed）改造成真后端日历 + 巴士管理
- 指導履歴 + 事案 + 个人档案 → 新页/在学生详情里（账号页或搜索结果点学生 → profile）
- 一括进级 → 账号管理页加「一括进级」按钮（先 dry_run 预览再确认）
- push 无 teacher_web UI（学生 App 的活）

### W8 — 自审 + codex 复审到 0 bug
- 多 agent 多维自审（对齐/崩溃/逻辑/安全/生产配置/三边一致）→ 修。
- 把并行会话 `05_logs/audit_2026-05-30/findings.md` 里**后端 + teacher_web 相关**条目挑出来一起修（Android/iOS 的不管）。
- codex（GPT-5.5 xhigh，能真起 Python 后端跑测试）独立复审 → 修。两轮 0 新 blocker/major 收敛。

### W8 追加发现（部署 bug，待修）
- **alembic 不读 DATABASE_URL**：`alembic/env.py:46` 用 `config.get_main_option("sqlalchemy.url")`，读的是 `alembic.ini:89` 写死的 `sqlite:///./tomoshibi_dev.db`。生产 PostgreSQL 部署时 `alembic upgrade head` 会指错库。修：env.py 改成优先读 DATABASE_URL 环境变量。
- 验证迁移链方法（dev 库 create_all 没跑过迁移）：`cd 03_dev/backend/v1; sed "s#sqlite:///./tomoshibi_dev.db#sqlite:///TMPDB#" alembic.ini > _t.ini; APP_ENV=dev .venv/bin/python -m alembic -c _t.ini upgrade head`（临时 ini 必须放后端目录，否则 script_location 相对路径找不到）。

## 进展日志
- W7 第1组 ✅ 行事予定(dorm_events)+巴士(bus_routes) 后端：迁移 e3f4a5b6c7d8 验证空库建 29 表 / 20 新测试 / 115 passed / commit 完成。
- 后端 python = `03_dev/backend/v1/.venv/bin/python`；pytest 基线现 115。

## 进展日志（续）
- 后端 4 组全 ✅ commit（行事/巴士、指導/事案、档案/进级、push），153 测试，迁移链验证 6 新表。
- 前端 FE1 ✅ 行事予定+巴士 接真后端（CommunityPage，listEvents/listBusRoutes，check_jsx 0 错），**未 commit**。
- 前端 FE2 ✅ 个人档案 Modal(6tab)+事案録入页(加 nav)+指導録入，11 client.js 函数，check_jsx 0 错，**未 commit**。缺口：开示申请审查 UI 没建（函数就绪）。

## 待做（前端 + 收尾）
1. FE3：一括进级 UI（账号页，dry_run 预览再确认）+ 开示申请审查 UI（补 FE2 缺口）
2. FE4 / W6b：ROSTER 假名单重接 — 全局搜索(shell 11568)/点呼着陆(12086)/记录页(19451) 改用 listStudents；LiveRollCall 删 seedStudents 回退靠 rollcallBoard；NotificationsPage(20144) 假名 + COMMUNITY_POSTS 处理
3. 统一假数据清理（我用脚本）：删 window.ROSTER_*/TEACHERS/ACCOUNTS/OUTSTAY_APPS/FRONT_*/NOTICE_POSTS/COMMUNITY_POSTS/seedStudents/showConsole/simCheckin 死代码（确认无引用后）
4. commit 前端各组
5. **W8 审查**：多 agent 自审（三边对齐/崩溃/逻辑/安全/生产配置）+ 挑 findings.md 后端/teacher_web 条目 + 修 alembic 不读 DATABASE_URL 部署 bug → codex 复审 → 0 bug 收敛
