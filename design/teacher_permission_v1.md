# 老师权限分级系统 设计文档 v1

> 本文件是「老师端权限」的单源真值，取代 `system_features.md` §3.4 旧权限模型（「按职责勾选」朝点呼/夜点呼/学習担当…）。旧模型作废。

---

## 1. 背景与目标

### 1.1 现状（改造前）

- `teachers.role` 字段存职位（9 个枚举值），`app/deps.py` 的 `require_teacher_roles(...)` 按职位硬拦。
- 但绝大多数老师端点只挂 `get_current_teacher`（登录即全能），**仅** 学生账号管理 / 注册码管理 / 老师账号管理 / 在线学习审批挂了职位闸。
- 即：现在权限几乎没有按职位细分，且凡是挂了的，都是「权限 = 职位」死绑。

### 1.2 问题

老师按班次轮值，同一人不同时段在男寮 / 女寮、有时多人同管。把权限绑死在固定职位上不符合现实（典型反例：`assigned_dorm=1` 的男寮老师走到女寮调不出女寮名单）。

### 1.3 目标

- **职位退化为纯显示标签**，不决定任何权限。
- 权限改为 **「权限组 + 按功能两级开关」** 模型：账号创建时指定一个权限组，权限组决定该账号每个功能的权限级别。

---

## 2. 核心概念

| 概念 | 含义 |
|---|---|
| **职位标签** | 9 个职位（校長 / 寮務部長 …），纯显示用，不参与鉴权 |
| **权限组** | 5 个预设组，账号创建时二选一指定，决定该账号的功能权限集 |
| **功能权限（两级）** | 每个功能簇对每个权限组取三态之一：**管理（M）**=可增删改、且蕴含查看 ／ **查看（V）**=只读 ／ **无（✕）**=完全不可见 |

> 关键设计原则（itsuki 2026-06-11）：**哪怕某权限组对某功能没有管理权，也至少给查看权**——宿管交接班需互相看到对方记录的内容。所以三态里 ✕（完全不可见）在本设计中极少用到。

---

## 3. 五个权限组

| 权限组 | 账号性质 | 简介 |
|---|---|---|
| **op** | 全权限·非个人 | 系统最高权限运维账号。账号名固定 `op`，不属于任何一位老师私有。密码由 itsuki 自存、经环境变量注入（见 §7） |
| **寮管理者** | 全权限·个人 | 寮务负责人个人账号，权限等同全权限 |
| **一般宿管** | 受限 | 日常运营全能，不含晚自习/学习管理 |
| **一般宿管+晚自习** | 受限 | 一般宿管 + 晚自习出席/学习管理 |
| **申請承認専用** | 受限 | 以审批为核心 + 部分公共信息管理；其余功能降级为只读 |

---

## 4. 九个职位标签（仅显示）

```
校長 / 寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長 / 管理係 / 寮監 / 学習担当 / 寮務一般教師
```

账号创建时除选权限组外，还选一个职位标签，仅用于界面展示（如登录卡片、列表）。

---

## 5. 权限矩阵（单源真值）

**M** = 管理（增删改 + 查看） ／ **V** = 仅查看 ／ **✕** = 不可见

| # | 功能簇 | op | 寮管理者 | 一般宿管 | +晚自习 | 申請承認専用 |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | 点呼运营 | M | M | M | M | **V** |
| 2 | 申请审批（含在线学习审批） | M | M | M | M | M |
| 3 | 扣分管理 | M | M | M | M | **V** |
| 4 | 前台·宅配 | M | M | M | M | **V** |
| 5 | 公告 | M | M | M | M | M |
| 6 | 巴士路线 | M | M | M | M | M |
| 7 | 行事·活动 | M | M | M | M | M |
| 8 | 遗失物 | M | M | M | M | M |
| 9 | 点歌 | M | M | M | M | M |
| 10 | 食数计算·导出 | M | M | M | M | M |
| 11 | 晚自习出席记录 | M | M | **V** | M | **V** |
| 12 | 学生账号管理 | M | M | M | M | **V** |
| 13 | 注册码管理 | M | M | M | M | M |
| 14 | 事案记录 | M | M | M | M | **V** |
| 15 | 指导履历 | M | M | M | M | **V** |
| 16 | 老师账号管理 | M | M | **V** | **V** | **V** |
| 17 | 操作履历审计 | M | M | **V** | **✕** | **✕** |

注：
- 第 16 行老师账号管理对受限三组只给查看权（含登录账号名 `login_id`），itsuki 2026-06-11 拍板（理由：登录页方案 B 本就公开展示所有老师卡片，名字职位半公开）。
- 第 14/15 行事案·指导履历对申請承認専用给查看权，itsuki 2026-06-11 拍板（一视同仁，不因隐私另设限）。
- 第 13 行注册码管理对申請承認専用从 V 升 M（5 组全 M），并同时取消演示账号禁令（删除 `admin_registration_code.py` 中 4 处 `assert_not_demo_teacher`）：所有权限组 + 演示账号均可完整使用（生成 / 关闭 / 查看 / 历史）。itsuki 2026-06-14 拍板。该决定回退了 2026-06-08 commit `49176ff` 为注册码加的演示隔离闸 —— itsuki 在知情演示老师可用真码注册真实学生（`is_demo=False`）、污染真实点呼库的前提下，以演示便利为由选择放开。详见 decision_log。
- 第 16 行老师账号管理**矩阵不动**（仍 op/寮管理者 MANAGE、其余三组 VIEW），但 2026-06-15 itsuki 拍板**取消演示账号禁令**（删除 `teachers.py` 中 4 处 `assert_not_demo_teacher`：招待発行 / 列老师 / 建老师 / 删老师）：演示账号现可列真实老师目录、且若在 MANAGE 组可增删真实老师账号。同样回退 6-08 commit `49176ff` 的演示隔离闸 —— itsuki 知情（演示账号可枚举真实老师 `login_id`/`email`、可操作真实人事）以演示便利为由放开。详见 decision_log。
- 「寮过滤」（老师按 `assigned_dorm` 只能看/操作本寮学生）**已取消**（2026-06-14 落地，见 §11.2）：所有老师可查看/操作所有学生，「能不能用某功能」仅由本表（权限组）决定，不再叠加寮限制。`dorm_units_for_teacher` 现恒返回全寮 `[1,2,4]`。注：男女寮**分开显示**（R4 显示规则 — 出寮者一覧按 1·2 寮 / 4 寮 分组）是另一回事，与访问权限无关、保留不变。
- 第 17 行操作履历审计（2026-06-16 新增）是本表唯一**只读**的功能簇：无任何角色可在该页产生写操作（页面只展示历史，记录由中间件自动落库），故矩阵最高也只到 M=管理而非真有"增删改"动作，对管理角色而言 M 与 V 等效。本簇也是少数用到 ✕（完全不可见）的一行——「一般宿管+晚自习」（寮監·学習担当）与「申請承認専用」（国際交流）看不到操作记录页，仅管理角色（op / 寮管理者 / 一般宿管）可查阅。理由：操作审计是管理职能，一线宿管无需也不宜查看全体老师的操作流水。

---

## 6. 功能簇 ↔ 后端端点映射

> 实装时以代码实际扫描为准，逐端点核对。下表为定稿时（2026-06-11）的对应关系。

| 功能簇 | 后端 router | 管理动作（M 才放行） | 查看动作（V 即放行） |
|---|---|---|---|
| 点呼运营 | `rollcall.py` | sessions/start·end、events/{id} 改、reports/{id}/resolve | sessions·board·summary·reports list |
| 申请审批 | `applications.py` `outings.py` `misc_requests.py` `study_online.py` | {id}/approvals、{id}/confirm、approve、PUT 改 | pending-for-me·active·list·audit |
| 扣分管理 | `discipline.py` | manual 加分、{id}/revoke | ranking |
| 前台·宅配 | `front_desk.py` | create·notify·picked-up | list·students |
| 公告 | `announcements.py` | 发布公告 | 列表 |
| 巴士路线 | `bus_routes.py` | create·patch·delete | list·{id} |
| 行事·活动 | `events.py` | create·patch·delete | list |
| 遗失物 | `lost_found.py` | create·resolve | list |
| 点歌 | `songs.py` | create | list |
| 食数计算·导出 | `meals.py` | export | calc |
| 晚自习出席记录 | `study.py` | checkins 记录 | 名簿查看 |
| 学生账号管理 | `admin_accounts.py` | create·password-reset·renewal | students list·renewal-progress |
| 注册码管理 | `admin_registration_code.py` | refresh·close | current·history |
| 事案记录 | `incidents.py` | create·patch·delete | list·{id} |
| 指导履历 | `guidance.py` | 新建记录 | 查看记录 |
| 老师账号管理 | `teachers.py` | register·create·delete | list·public·me |
| 操作履历审计 | `audit_log.py` | （无写动作）| GET /admin/audit-logs |

注：操作履历审计端点全为只读，无管理动作。`GET /api/v1/admin/audit-logs` 挂 `require_permission(C_AUDIT_LOG, VIEW)`，故对管理三组（op / 寮管理者 / 一般宿管，均 ≥V）放行、对其余两组（✕）拒绝。记录的产生不走任何老师端点，而是由 `audit.py` 的 `AuditLogMiddleware`（ASGI 中间件）拦截全部老师写请求（POST/PUT/PATCH/DELETE）自动落库，详见 `dev/backend/BACKEND_DESIGN_LOG.md`。

---

## 7. op 账号机制（安全铁律）

- 账号名固定 `op`，`is_demo=False`，`assigned_dorm=NULL`（跨寮看全部）。
- **密码绝不写进代码 / 仓库 / 迁移 / seed 任何文件**。itsuki 自己保管明文。
- 后端建 op 账号时从**环境变量** `OP_PASSWORD` 读取，仅在部署机的环境里设置。环境变量缺失时不建 op 账号（不设缺省值）。
- 仓库内任何位置都不得出现该密码字符串（实装后用 `grep` 自查零命中）。

---

## 8. 登录页（方案 B）

一页全显所有老师卡片，点卡片进入登录。UI 实装细节归 `dev/teacher_web/WEB_DESIGN_LOG.md`。

---

## 9. 实装影响（改造范围）

| 端 | 改什么 |
|---|---|
| **后端 models** | `Teacher` 加 `permission_group` 字段（5 值枚举）；5 组对各功能簇的权限级别做成代码内 PRESET 常量（组名 → {功能簇: M/V/✕}），Teacher 只存组名 |
| **后端 deps** | 新增 `require_permission(功能簇, 级别)` 闸，按当前老师的权限组查 PRESET 判定；逐步取代/补充 `require_teacher_roles` |
| **后端各 router** | 每个老师端点挂 `require_permission`（管理动作要 M、查看动作要 V） |
| **后端 seed / 迁移** | 加字段 + 回填现有老师到某组（默认值待定）+ op 账号走环境变量 |
| **老师网页** | 登录页方案 B；建账号弹窗选「权限组 + 职位标签」；按权限组隐藏/置灰功能入口 |
| **iOS / Android** | 学生端，不涉及老师权限，**确认无影响** |

---

## 10. 与旧文档的关系

- 本文件取代 `system_features.md` §3.4 / §3.4 教师权限模型「按职责勾选」（朝点呼/夜点呼/学習担当/寮務/指导履歴/巴士行事 master）——该旧模型作废，`system_features.md` 对应段落已改为指向本文件（2026-06-11）。
- 鉴权机制现状 + 本设计落地记录见 `dev/backend/BACKEND_DESIGN_LOG.md §3.8`（2026-06-11 实装）。

## 11. 实装落地（2026-06-11）

后端 + 老师网页两端已实装（commit `78ea32f` 后端核心 / `49139d5` 端到端 + 网页）：

- **后端**：`app/permissions.py`（§5 矩阵单源真值 PRESET + ROLE_DEFAULT_GROUP 向后兼容回退）；`Teacher.permission_group` 列 + 迁移 `f1a2b3c4d5e6`；`deps.require_permission(簇,级别)` 闸取代 17 个簇路由里所有裸 `get_current_teacher` / `require_teacher_roles`；op 账号经 `OP_PASSWORD` 环境变量注入（明文绝不入仓库）。pytest 371 passed / 0 failed。
- **老师网页**：建账号弹窗加权限组选择器；`src/api/permissions.ts` 前端矩阵镜像（仅 UI 显隐用，非安全边界）。`npm run build` 退出码 0。
- **§6 端点映射实装注记**：代録（`applications.py` by-teacher）与 proxy-candidates 因 §6 未列进 cluster-2 管理动作清单，挂 `require_permission` 的同时保留了 `_DAIROKU_ROLES` 职责域规则；`teachers.py delete_teacher` 保留 `TEACHER_ADMIN_ROLES`（防删最后一个管理员）。这两处职位域规则是否也纯按权限组判，待 itsuki 拍板。
- **未接线**：「按权限组隐藏/置灰功能入口」的导航联动 —— 前端矩阵已备好，具体 UX 待 itsuki 拍板（不擅自改冻结的 web 界面）。

## 11.1 第二轮落地（2026-06-13）— 职位彻底退出鉴权

itsuki 2026-06-13 拍板：职位（`teachers.role`）只作显示标签，**一处不参与鉴权**。在前一轮权限分级基础上清掉残留的职位判断：

- **后端**（commit `365f3e7`）：`dorm_life` 4 个审批 decide 端点 `require_teacher_roles(职位)` → `require_permission(C_APPROVAL, MANAGE)`；`applications` 代録 / proxy-candidates 删 `_DAIROKU_ROLES` 职位二次检查（端点已挂权限闸）；`notifications` 通知测试职位闸 → `require_permission(C_ANNOUNCE, MANAGE)`；`meals` 删死代码 `_check_role`；`teachers` 删死代码 `INVITE_ALLOWED_ROLES`；`deps` 删无人使用的 `require_teacher_roles` 闸函数（全后端已无引用）。pytest 371 passed（2 个「非代録职位 403」测试改写为「按权限组放行」新预期）。
- **老师网页**（commit `3382021`）：`Shell` 里 3 个按旧职位列表隐藏的菜单（代録 / 事案記録 / 教員管理）改为无条件显示。**前端不做按权限置灰**——itsuki 拍板「直接全部允许查看」：所有老师都能查看所有功能页，「增删改」限制由后端权限闸按权限组把关（无权限点击被 403 拦）。依据：§5 矩阵里没有任何功能簇对任何组是 ✕（不可见），人人至少有查看权，故菜单层面无需隐藏 / 置灰。
- **审批链**（`approval_chain.py`）：itsuki 2026-06-13 拍板**保留职位驱动**。审批链是「申请路由给谁审」的业务工作流，不是「能不能用功能」的权限闸，职位在此是业务角色而非鉴权，保留不违背「职位不参与鉴权」。
- **寮过滤（R4）**：itsuki 倾向「所有老师可查看所有学生，仅修改受权限限制」，本轮不动、作为独立任务另行处理 → 已于 §11.2 落地。

## 11.2 第三轮落地（2026-06-14）— 寮过滤彻底取消

itsuki 2026-06-13 拍板：**取消老师寮过滤**。原话「所有老师都可以看所有学生，因为本来学生信息也都是公开的，只不过不是权限内的人不能修改而已」。即：老师对学生的**查看 + 操作**都不再按男/女寮（`assigned_dorm`）隔开；「能不能改」仅由权限组（§5 矩阵）把关，与寮无关。

- **后端**（commit `d8ddad5`）：`deps.dorm_units_for_teacher` 恒返回全寮 `[1,2,4]`（返全集而非 None，避免无守卫调用点 `.in_(None)` 报错）；`applications._teacher_can_view` → `return True`；删 applications 里 3 处内联寮过滤块。25+ 个调 `dorm_units_for_teacher` 的端点因此自动放开到全寮，逻辑无需逐个改。
- **测试**（commit 见落地批次）：约 35 个寮边界测试改写 —— 原断言「跨寮 403 FORBIDDEN_DORM / 列表排除别寮」改为「跨寮现允许 200/201 / 列表含别寮」。pytest 全量 379 passed / 0 failed。
- **不受影响（刻意保留）**：① 男女寮**分开显示**（R4 显示规则，出寮者一覧分组）；② 学生侧规则 —— 学生只看自己寮的点呼场次（`/rollcall/me/today`）、学生不能把自己房号改成异性寮（房号格式校验）；③ WebSocket 按寮广播；④ 演示/真实数据隔离（`is_demo`，与寮正交）。
- **隐私权衡**：取消后男寮男老师能看到全部女生信息（房间号/出入/事案/扣分）。itsuki 已知悉并拍板接受（理由：学生信息本就对全体老师公开，约束在「改」不在「看」）。
- **`student_profile`**：学生档案查看原按职位（`_GUIDANCE_ROLES`）判，随本轮一并放开到全寮。

## 12. 第 17 功能簇追加（2026-06-16）— 操作履历审计

itsuki 2026-06-16 拍板新增「操作履历审计」功能簇（第 17 簇 `C_AUDIT_LOG`），为老师网页提供「操作履歴」页：可按精确日期时间查看老师做过的写操作。功能簇总数由 16 增至 17。

- **权限矩阵**（已并入 §5 第 17 行）：op=M / 寮管理者=M / 一般宿管=V / 一般宿管+晚自习=✕ / 申請承認専用=✕。即仅管理三组（op / 寮管理者 / 一般宿管 = 寮務部長·寮務課長·管理係）可查阅；寮監·学習担当（一般宿管+晚自习）与国際交流（申請承認専用）不可见。本簇是只读簇，无写动作。
- **后端落地**：`app/permissions.py` 加 `C_AUDIT_LOG` 常量 + PRESET 第 17 行；`app/audit.py` 新增 `AuditLogMiddleware`（ASGI 中间件，拦截全部老师写请求自动落库，请求体脱敏后存 `audit_logs.payload`）；`app/routers/audit_log.py` 新增只读端点 `GET /api/v1/admin/audit-logs`（挂 `require_permission(C_AUDIT_LOG, VIEW)`、按 actor 的 `is_demo` 做演示隔离、支持分页与 actor/时间过滤）；`models.py` 的 `audit_logs` 表 `target_type`/`target_id` 改为可空、`action` 列宽 64→128；迁移 `a9b8c7d6e5f4`（down=`e7e15d3b2e33`）。
- **老师网页落地**：新增 `src/components/AuditLogPage.tsx`（操作履歴页）；`Shell.tsx` 在「管理・設定」导航组加「操作履歴」菜单项，仅管理角色显示（`canViewAuditLog`，由 `App.tsx` 按权限组/职位计算，与后端 `C_AUDIT_LOG` 对齐）。
- 端别实装详情见 `dev/backend/BACKEND_DESIGN_LOG.md` 与 `dev/teacher_web/WEB_DESIGN_LOG.md`。本簇是本表唯一在导航层面按权限隐藏的菜单（其余 16 簇人人至少有查看权、菜单全显），因为其矩阵对两组取 ✕（不可见）。
