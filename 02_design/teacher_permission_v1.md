# 老师权限分级系统 设计文档 v1

> 本文件是「老师端权限」的单源真值。2026-06-11 itsuki 拍板定稿，取代 `system_features.md` §3.4 旧权限模型（「按职责勾选」朝点呼/夜点呼/学習担当…）。旧模型作废。
>
> 决策脉络见 `05_logs/decisions/decision_log.md`（2026-06-11 条）。

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
| 13 | 注册码管理 | M | M | M | M | **V** |
| 14 | 事案记录 | M | M | M | M | **V** |
| 15 | 指导履历 | M | M | M | M | **V** |
| 16 | 老师账号管理 | M | M | **V** | **V** | **V** |

注：
- 第 16 行老师账号管理对受限三组只给查看权（含登录账号名 `login_id`），itsuki 2026-06-11 拍板（理由：登录页方案 B 本就公开展示所有老师卡片，名字职位半公开）。
- 第 14/15 行事案·指导履历对申請承認専用给查看权，itsuki 2026-06-11 拍板（一视同仁，不因隐私另设限）。
- 「寮过滤」（男/女寮可见范围 `assigned_dorm`）与本权限模型**正交叠加**，不变：本表决定「能不能用某功能」，`dorm_units_for_teacher` 决定「该功能里能看到哪些寮的学生」。

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

---

## 7. op 账号机制（安全铁律）

- 账号名固定 `op`，`is_demo=False`，`assigned_dorm=NULL`（跨寮看全部）。
- **密码绝不写进代码 / 仓库 / 迁移 / seed 任何文件**。itsuki 自己保管明文。
- 后端建 op 账号时从**环境变量** `OP_PASSWORD` 读取，仅在部署机的环境里设置。环境变量缺失时不建 op 账号（不设缺省值）。
- 仓库内任何位置都不得出现该密码字符串（实装后用 `grep` 自查零命中）。

---

## 8. 登录页（方案 B）

一页全显所有老师卡片，点卡片进入登录。UI 实装细节归 `03_dev/teacher_web/WEB_DESIGN_LOG.md`。

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
- 鉴权机制现状 + 本设计落地记录见 `03_dev/backend/BACKEND_DESIGN_LOG.md §3.8`（2026-06-11 实装）。

## 11. 实装落地（2026-06-11）

后端 + 老师网页两端已实装（commit `78ea32f` 后端核心 / `49139d5` 端到端 + 网页）：

- **后端**：`app/permissions.py`（§5 矩阵单源真值 PRESET + ROLE_DEFAULT_GROUP 向后兼容回退）；`Teacher.permission_group` 列 + 迁移 `f1a2b3c4d5e6`；`deps.require_permission(簇,级别)` 闸取代 17 个簇路由里所有裸 `get_current_teacher` / `require_teacher_roles`；op 账号经 `OP_PASSWORD` 环境变量注入（明文绝不入仓库）。pytest 371 passed / 0 failed。
- **老师网页**：建账号弹窗加权限组选择器；`src/api/permissions.ts` 前端矩阵镜像（仅 UI 显隐用，非安全边界）。`npm run build` 退出码 0。
- **§6 端点映射实装注记**：代録（`applications.py` by-teacher）与 proxy-candidates 因 §6 未列进 cluster-2 管理动作清单，挂 `require_permission` 的同时保留了 `_DAIROKU_ROLES` 职责域规则；`teachers.py delete_teacher` 保留 `TEACHER_ADMIN_ROLES`（防删最后一个管理员）。这两处职位域规则是否也纯按权限组判，待 itsuki 拍板。
- **未接线**：「按权限组隐藏/置灰功能入口」的导航联动 —— 前端矩阵已备好，具体 UX 待 itsuki 拍板（不擅自改冻结的 web 界面）。
