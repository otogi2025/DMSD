# W8 审查 findings（4 分身并行审查产出，2026-05-30）

> 审查范围：teacher_web + 后端 v1.0 上线就绪。下面按「修复优先级」归类。压缩后接着修读这个。

## A 类 — 我 W7 新代码引入的 bug（必修）

| # | 严重 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| A1 | blocker | 前端 index.html 23801/20859/21505 | `teacher.role` 永远 undefined（真角色在 authProfile.role）→ 一括进级/行事/巴士 增删改按钮**永不显示** | 登录时把 role 塞进 teacher，或组件读 authProfile.role |
| A2 | blocker | schemas.py:1179 | `BusRouteListOut` 混入硬编码 `message="アカウントのロックを解除しました。"` | 删该字段 |
| A3 | blocker | student_promote.py:97 | `int(s.grade_code)` 无防护，脏数据→500 | try/except 或查询过滤 grade_code IN ('01'..'06') |
| A4 | blocker | 前端 DisclosureRequestsPage 26879 | 显示 item.student_no 但后端只返 student_id→空白 | 后端 schema 补 student_no(join)，前端改用 |
| A5 | major | 前端 12125 | listStudents({dorm_unit: teacher.dorm}) 传字符串，后端要 int→过滤失效 | 转 int 或用 authProfile.assigned_dorm |
| A6 | major | 前端 CommunityPage 22713 | posts 用 window.COMMUNITY_POSTS 假数据，无后端 | 标占位/明确无后端 |
| A7 | major | 前端 IncidentsPage 26183 | involved_student_ids 无 UUID 校验→422 | 提交前校验或学生联想选择 |
| A8 | minor | events.py:53/bus_routes.py:51 | GET 用 get_current_teacher，spec 说学生可看 | 改 get_current_principal（低优先，无学生客户端） |
| A9 | minor | bus_routes.py PATCH | 软删可被 PATCH 改回 | 加校验 |
| A10 | minor | guidance.py | 学生开示申请无 audit / list 无 limit / pending 去重竞争 | 补 audit+limit |
| A11 | minor | events.py:33 死代码 / promote 无格式校验 / device_tokens token 非唯一索引 | 清理+唯一索引 |
| A12 | minor | CommunityPage 22815 stats.today 硬编码"04-22" / AccountsPage 重复注册 / toast 定位 | 动态日期+去重 |

## B 类 — 审查翻出的既有上线阻塞（真问题，v1.0 需要）

| # | 严重 | 位置 | 问题 | 修法 |
|---|---|---|---|---|
| B1 | blocker | auth.py 无 DELETE /sessions/current | logout→404，JWT 服务端无法吊销 | 后端加端点 |
| B2 | blocker | accounts.py 无 DELETE /accounts/me | App Store 5.1.1(v) 强制，iOS 调它→404 上架被拒 | 后端加 DELETE /accounts/me |
| B3 | blocker | alembic/env.py:46 | 不读 DATABASE_URL，生产 PostgreSQL 建表失败（叠加 create_all 只 dev）→ 生产无法初始化 | env.py 优先读 os.environ DATABASE_URL |
| B4 | blocker | config.py:56 CORS | 只 localhost，生产校验不拦 | 生产校验加 localhost→error |
| B5 | major | main.py 无 StaticFiles | teacher_web 生产 serving 方案未定 | 选同 origin mount StaticFiles 或跨 origin |
| B6 | major安全 | auth.py 学生登录 | 失败计数不递增，可无限爆破（A-005） | 失败分支递增+锁定 |
| B7 | major安全 | accounts.py 注册码 | invalidated_at 只查不设，可重复注册 | 用后标记已用 |
| B8 | major隐私 | 多端缺 R4 寮边界 | applications decide/cleaning/front_desk/rollcall/ws 不校验学生属本老师寮→跨寮越权+全校信息推所有老师 | 各处加 assigned_dorm 校验 |
| B9 | major | index.html 假数据残留 | ROSTER_*/ACCOUNTS/DEMO_SEED_NO/seedStudents 仍下发（泄露编号规则） | 统一删 |
| B10 | minor | schemas.py:798 | StudentAccountCreateIn.dorm_unit 允许 3，DB 只 1/2/4 | 改 Literal[1,2,4] |

## C 类 — 超范围 / 单独决策（不在本次修复）

- **NFC 防代刷三件套**（card_uid↔学生 + nonce + ECDSA）后端零实装（rollcall-01/FC-014/sysfeat-01/02/03）。学生端 NFC 签到核心，大功能 + 需 itsuki 拍板，不在 teacher_web v1.0 范围，需单独立项。
- iOS/Android 客户端 findings — 不在范围。
- client.ts 与 client.js 漂移死代码 — 低优先。

## 已确认本会话已修复（findings.md 交叉验证）
discipline/teachers 漏 import ✅ / rollcall minute 崩 ✅ / auth timedelta ✅ / API_BASE 明文 ✅ / AccountsPage 假数据 ✅ / 静默 demo 降级 ✅ / JWT_SECRET fail-fast ✅

## 修复顺序
Fix1 后端 A 类 → Fix2 后端 B 安全(B1/B2/B6/B7/B10) → Fix3 后端 B8 寮边界 → Fix4 生产配置(B3/B4/B5) → Fix5 前端 A 类 → Fix6 假数据清理(B9) → 复跑 pytest+check_jsx → codex 复审
