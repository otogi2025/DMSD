# Tomoshibi Backend · 设计 + v1.0 实装档案

> **作用**: backend（后端 = 服务器代码）agent 接手 v1.0 实装的入口文件。对称 iOS 的 `IOS_DESIGN_LOG.md` 和 Web 的 `WEB_DESIGN_LOG.md` —— 每个端各一个档案。
> **建立**: 2026-04-30 by [Mac-轨道C-CC]
> **范围**: **P0 only**（出寮届 #1-9 / #10-13 + 点呼・学習 iPad #14-20 + 邮件通知 R1）。P1/P2/P3 后续会话续写。

## ⚠️ 实装进度速查表（2026-05-21 A-029 加）

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ 100% | 1134 行设计 + Alembic / 8 router 完整 |
| Routers | ✅ ~90% | rollcall / study / accounts / admin_registration_code / teachers / applications / auth / meals / notifications / announcements 全实装 |
| NFC ECDSA / nonce | ⏳ 0% | spec 写了 + ROLLCALL_DEVICE 设计了，**backend 一行未实装**（A-010 主会话保留） |
| JWT 安全 | 🟡 部分 | HS256 + change-me 默认值（A-001/A-002 主会话保留）；production fail-fast 已加（A-007/A-008） |
| 失败锁定 | 🟡 部分 | 教师锁已加 3 次 / 30 分（A-006 已修）；学生锁待主会话拍板阈值（A-005） |
| 路由顺序 | ✅ 已修 | `/pending-for-me` 移到 `/{application_id}` 之前（A-013） |
| Idempotency | ✅ 已修 | RollCallEvent (session_id, idempotency_key) UniqueConstraint + alembic migration（A-011） |
| 教师注册 | ✅ 已修 | confirmation_email 必填 + invitation.target_email 严格对比（A-012） |
| Reviewer 凭证 | ✅ 已修 | 999999 + 密码移 env，fallback 时 warn（A-014） |
| Tests | 🟡 部分 | 37 case 全 pass；rollcall / study / applications 专用测试缺（C-050 已修） |
| 扣分值 / 改判重算 | ✅ 已修 | 迟到/缺席 0.5/1.0（system_features §862 冻结值，旧 1.0/2.0 是 drift）；改判 `_apply_override_demerit` 改「按当前状态重算」修多步改判少扣 bug（itsuki 5-31 + Codex 5.5 审）|
| 注册码 TTL / 关闭 | ✅ 已修 | 自动失效 5→30 分 + 新增 `POST /admin/registration-code/close` 手动关闭（itsuki 5-31；「一次性」需求拒绝）|
| 密码下限 | ✅ 已修 | 设密码处（老师注册 / 学生建号）6→8 位；登录处不卡长度（保护错误密码锁定测试）（itsuki 5-31）|
| 邮件发送 | 🟡 dev | SendGrid（2025 春取消永久免费）→ Resend（永久免费 3000 封/月）迁移完成（6-05）；无密钥时 dev 模式跳过不真发，itsuki 注册 resend.com 拿密钥填 .env 即真发；urllib POST 无第三方依赖；带 3 单元测试（test_email_resend.py）|

### 字段隐私分级（2026-05-21 A-023 加）

某些 backend 字段不应向 client 暴露，避免泄露内部信息。原则：
- **backend-only**：`is_demo` / `is_reviewer` / `password_hash` / `failed_count` / `locked_until` / 内部 `created_at` audit 等 — 不进任何 client schema
- **教师 client 可见**：`role` / `assigned_dorm` / `name` 等
- **学生 client 可见**：自己的 `student_no` / `dorm_unit` / `room_no` / `name`；不可见其他学生信息
- iOS `StudentBrief` / teacher_web `StudentBrief` 字段集要按本分级裁剪（当前已正确 — `is_demo` 没暴露）
>
> **agent 阅读顺序**（两层结构）:
> 1. **共用层（必读）**: `02_design/system_features.md` —— 角色 / 数据模型 / §7 14 子节功能矩阵 / R1-R4 硬约束 / 38 条要件
> 2. **专属层（本文）**: 后端实装层 —— DB schema SQL / API 形状 / 错误码 / 测试 / 部署 / 待拍板
>
> **其他权威源**:
> - `01_specs/rollcall/RollCall_Spec.md` —— 点呼业务规则（§4 时刻表 / §5 流程 / §11 改判）
> - 老师 38 条反馈 backlog（原文 + Q1-Q12 + R1-R4 完整记录）—— 内部管理记录，不在公开仓库
>
> **下游**:
> - `03_dev/backend/demo/` —— 演示版实装（FastAPI + SQLAlchemy + SQLite + WebSocket 玩具版），**只搬"已验证可行"的部分**，不直接复用
> - `03_dev/backend/v1/` —— v1.0 实装位置（未着手）

---

## 0. 文档使用方法

- code agent 接手时 → 从 §1 读到 §3 拿到全局，再按 §5 的模块顺序逐个实装
- itsuki 来 review 时 → 直接跳 §10「待 itsuki 拍板」拍决策；其余部分都是 CC 已经做的合理假设
- 决策标记:
  - ✅ **已定** = 上游真值或老师/itsuki 明示
  - 🟡 **CC 假设** = code agent 可直接按此实装，但 itsuki 有否决权
  - ⏳ **待拍板** = 必须 itsuki 决定才能动手（聚集到 §10）

---

## 1. 技术栈与启动条件

### 1.1 技术栈（✅ 已定）

| 层 | 选型 | 出处 |
|---|---|---|
| 言語 | **Python 3.11+** | demo 已用 / itsuki 学习路径 |
| Web framework | **FastAPI** | demo 已用 |
| ORM | **SQLAlchemy 2.x（async）** | demo 已用 |
| DB | **PostgreSQL 16+**（demo 用 SQLite，v1 升 PG）| `system_features.md` |
| migration | **Alembic** | 🟡 CC 推荐（FastAPI 标配） |
| 认证 | **JWT (HS256) + refresh token** | 🟡 CC 推荐（详见 §5.1） |
| WebSocket | FastAPI 内置 + Redis pub/sub（v1 多机时）| demo 用了内存 manager，v1 加 Redis |
| 邮件 | **SendGrid API** | ⏳ §10-D1 待拍板 |
| 时区 | 全部 JST（`Asia/Tokyo`），DB 存 UTC `TIMESTAMPTZ`，业务层转 JST | RollCall_Spec §9 |
| 测试 | pytest + httpx AsyncClient | 🟡 CC 推荐 |

### 1.2 启动前提（✅ 已定）

- `02_design/system_features.md` §7 14 子节已定稿（4-29 close）
- `RollCall_Spec.md` 5 处时序修订已定稿（4-29）
- 老师 12 个 Q 已答 11 个（Q12 杭田 UI 矛盾不影响后端实装）
- 项目仓库 GitHub `otogi2025/DMSD`（4-29 起 public）

### 1.3 起点（✅ 已定）

**从 `demo/` 复制 + 重写**:

| demo 资产 | v1 处置 |
|---|---|
| `demo/main.py` 路由组织方式 | 参考结构，**不直接复制**（v1 要拆 router） |
| `demo/models.py` SQLAlchemy 模型 | **重写** — schema 大改（applications / study / teachers 全新表） |
| `demo/db_schema.sql` | **废弃** — v1 用 Alembic migration 生成 |
| `demo/ws_manager.py` 内存 WS broker | 参考 + 改 Redis 版（多机 / 4 台 iPad 协调） |
| `demo/seed.py` | 参考 seed 数据形状，**v1 用真名单导入** |
| NFC `POST /checkin?no=XX` 端点 | 路径 A 的简化版可保留作 demo 兜底（NFC quick URL Card） |

---

## 2. P0 范围（本文档覆盖）

### 2.1 P0 = 老师 38 条里的核心闭环

| 编号 | 模块 | 受益角色 | 说明 |
|---|---|---|---|
| **#1-#9** | 学生 出寮届提交 | 学生 | 帰省 / 外泊 / 帰国 3 种 |
| **#10-#13** | 役职 出寮届承认 | 役职（4 人） | 寮務部長 / 寮務課長 / 国際交流部長 / 国際交流課長 |
| **#14-#20** | 寮監・学習担当 点呼/学習 | 寮監 / 学習担当 | iPad ★ 一本道 UX（R2） |
| **R1** | 邮件通知 | 役职 / 学習担当 | 出寮届 提交时 / 学習欠席届 提交时 |

### 2.2 P0 范围外（后续会话）

| 范围 | 移到 |
|---|---|
| #7 食堂 食数计算 / Excel 导出 | P1 |
| #8 寮生特别运航便 一覧 | P2 |
| #9 行事予定表示 | P2 |
| #11 役职 巴士編集 / #12 行事編集 | P2 |
| #22-#27 寮監事務室 出寮者一覧 ● PC | P1 |
| #28-#33 寮務部教师 学生管理 / 指導履歴 / 事案 | P2 |
| #37 リクエスト曲（音乐） | P3 |
| 旧 demo NFC 快捷指令 → iOS BTR 升级 | P1 |
| 罚则 自動アラート / 風控 | M3+ |

---

## 3. 全局约束与横切关注点（✅ 已定）

> **R1-R4 概念定义** = `system_features.md §2`。本节 = 在 backend 实装层的**具体体现**（SQL 约束 / API 默认值 / 通道选择等代码层的事）。

### 3.1 R4 — dorm_unit 分流（必须贯穿）

**所有 entity 涉及"按寮分别处理"时**，必须有 `dorm_unit ∈ {1, 2, 4}` 字段（小写 SMALLINT），并通过 CHECK 强制与 `gender` 一致：

```sql
CHECK (
  (gender = 'male'   AND dorm_unit IN (1, 2)) OR
  (gender = 'female' AND dorm_unit = 4)
)
```

**点呼 session** = **2 个并行**（`dorm_unit IN (1,2)` 合同 / `dorm_unit = 4` 独立）— 不是 1 个 session 切 2 段。

**API filter 约定**:
- `?dorm=1+2` 或 `?dorm=men` → 1·2 寮合并
- `?dorm=4` 或 `?dorm=women` → 4 寮
- 不传 → 按当前登录教师的 `assigned_dorm` 自动 filter（详见 §5.1.4）

### 3.2 R1 — 邮件 vs Push 通知分流

| 场景 | 手段 |
|---|---|
| 出寮届 提交 → 役职 | **email**（必须） |
| 学習欠席届 提交 → 学習担当 | **email**（必须） |
| 役职 承认/拒否 → 学生 | **email**（必须）— 杭田 2026-06-04 訂正：原定 push，改为邮件，因「提出したことが残る」（推送会被划掉忘记） |
| 学号変更 → 老师（误输入检测） | **email**（必须） |
| 巴士时刻 / お知らせ 投稿 → 学生 | push + in-app |

后端必须实现 **2 通道**: `notifications.email_send()` + `notifications.push_send()`。任一通道失败 → retry 3 次 → 失败记 `notification_log` + 告警（不阻塞业务流程）。

> **2026-06-04 实装**：审批终态（approved / rejected）给提出者本人发邮件已落地 —— `services/email.py` 的 `render_application_decided` + `send_application_decided`（template_key=`application_decided`），由 `routers/applications.py` 的 `decide_approval` 在 `_recompute_application_status` 后、状态变终态时调用。学生本人无 email 登录则记 failed 不阻塞业务。push 通道（`services/push.py`）仍为死代码、符合杭田「不要推送」。

### 3.3 R2 — 老龄寮監 一本道 UX

**这条 UX 约束在 backend API 设计上的体现**:
- 寮監使用的 endpoint **不能要求"先选条件再查"** — API 默认值要能直接返回当天该寮的现状
- 例: `GET /study/today/attendees` 不传任何 query param → 自动返回「当天 + 当前教师寮 + 当前学習対象寮生 - 今日学習欠席届承认者 - 今日出寮届承认者」的 ready-to-render list
- 寮監 iPad UI 不会传 filter / sort / pagination → API 设计不要把 paging 做成必传

### 3.4 时间 / 时区

- 入站 timestamp **接受 ISO 8601 with TZ**，无 TZ 时按 JST 解释
- 出站 timestamp **统一 ISO 8601 + `+09:00`** 后缀
- DB column 全 `TIMESTAMPTZ`
- 业务判定（迟到 / 出寮日 = 明天起 / 学習欠席届截止）一律 **服务器 JST 时刻**，不信任客户端

### 3.5 幂等 / 重复防护

- POST 创建类 endpoint 接受 `Idempotency-Key` header（UUID v4）
- 同一 `Idempotency-Key` 24h 内返回首次结果
- DB 唯一索引（如 `application_approvals(application_id, approver_role)`）作第二道防线

### 3.6 错误响应统一格式

```json
{
  "error": {
    "code": "STRING_CODE",       // 大写 snake_case，对应 ERROR_CODES.md
    "message": "人话日语",         // 学生面向 = 日语
    "details": { ... }            // 可选 — field validation 时含字段级错误
  }
}
```

### 3.7 Audit log（审计日志）

**必须 audit 的操作**:
- 役职 承认 / 拒否 出寮届
- 教師 改判 点呼 status（reason 必填，参 RollCall_Spec §11）
- 教師 修改 学生 学号 / 房间号
- 学生 自己修改 学号 / 房间号 / 邮箱 / 电话 / 头像
- 密码错误失败 / 锁定 / 解锁
- 教师密码 reset 操作

audit log 表 = `audit_logs(id, actor_type, actor_id, action, target_type, target_id, payload, created_at)`，**append-only**（不允许 UPDATE/DELETE，DB 触发器拦）。

---

### 3.8 教师权限分级（teacher_permission_v1 实装落地，2026-06-11）

单源真值 = `02_design/teacher_permission_v1.md`（旧「按职责勾选」模型作废）。后端落地：

- **模型**：`Teacher.permission_group`（5 值枚举或 NULL + CheckConstraint）；迁移 `f1a2b3c4d5e6` 加列 + 按职位回填。职位 `role` 退化为纯显示标签、不参与鉴权。
- **矩阵**：`app/permissions.py` PRESET（5 权限组 × 16 功能簇 → MANAGE / VIEW / NONE，严格照设计 §5）+ `ROLE_DEFAULT_GROUP`（NULL 组按职位回退的向后兼容 shim，生产账号显式配组后不触发）。
- **闸**：`deps.require_permission(功能簇, 级别)` 取代裸 `get_current_teacher` / `require_teacher_roles`；17 个簇路由的老师端点全改挂（管理动作 M / 查看动作 V），拒绝时 `detail.code="FORBIDDEN_ROLE"`（沿用旧码）。
- **正交关系**：寮过滤（`dorm_units_for_teacher`）/ 演示隔离（`assert_not_demo_teacher` / `demo_scope_for_teacher`）/ 审批链 角色逻辑 与权限闸正交叠加，全部保留不变。
- **op 账号**：`seed.py` 从环境变量 `OP_PASSWORD` 注入，明文绝不入仓库 / 迁移（缺失则跳过建账号）。
- **两处保留的职位域规则**（待 itsuki 决定是否也纯按权限组判）：① `applications.py` 代録 / proxy-candidates 仍叠加 `_DAIROKU_ROLES`（§6 未把它们列进 cluster-2 管理动作清单）；② `teachers.py delete_teacher` 仍用 `TEACHER_ADMIN_ROLES` 防删最后一个管理员。
- **codex 复审（2026-06-11，gpt-5.5 xhigh 只读）**：0 阻塞 / 5 重大 / 2 次要 / 1 建议。CC 逐条独立核实，itsuki 拍板后修了 4 条（F3 保持现状）：
  - **F2 renewal-start 漏迁**：`student_promote.py` 由 `require_teacher_roles(*_ADMIN_ROLES)` 改挂 `require_permission(C_STUDENT_ACCOUNT, MANAGE)`（§6 把 renewal 列为 cluster 12 管理动作）。
  - **F1 寮边界**：codex 报 14 端点「被放大」，CC 核实只有 `admin_accounts` 的 `/students`(list) / `password-reset` / `unlock` 3 个是本次真放大的（改动前 ADMIN_ROLES 3 职位 → 改动后所有 M 组含分寮老师、且无寮过滤）；其余 11 个是改动前就有的既有问题（裸 `get_current_teacher` 或已含分寮角色，本次没放大、部分还收窄）。修法：list 查询加寮过滤、password-reset/unlock 加 `_assert_student_in_dorm`（403 FORBIDDEN_DORM，与同文件 renew_seat 一致）。既有 11 端点另记 TODO 安全加固。
  - **F4 删管理员按职位计数**：`teachers.py delete_teacher` 由数 `TEACHER_ADMIN_ROLES`(职位) 改为按 `effective_group` 对 `C_TEACHER_ACCOUNT` 是否达 MANAGE 计数（`_has_teacher_account_admin`）。顺带修正旧逻辑的真 bug：旧集合错含寮監（实为 V）、漏了校長（实为 M）。
  - **F5 学習担当 回退映射**：`permissions.py` + 迁移回填把 `学習担当` 从 `申請承認専用`(晚自习只读) 改成 `一般宿管+晚自习`(itsuki 确认其负责晚自习管理)。
  - **F3（保持现状）**：建账号允许 permission_group=NULL→职位回退是故意留的安全网，itsuki 拍板不强制必填。
  - 次要/建议（F6 前端导航按职位显隐 / F7 共享端点 / F8 代録职位）记入内部 TODO 跟踪。

---

## 4. 数据模型 — P0 范围

> **真值**: `system_features.md §8`。本节 = **P0 实装版**（补 §8 没写的字段 + 加索引 / 约束）。

### 4.1 `students` (✅ 已定 — 来源 system_features §8.1)

```sql
CREATE TABLE students (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  grade_code      VARCHAR(2) NOT NULL,                      -- '01'..'06'
  class_code      VARCHAR(2) NOT NULL,                      -- '01' (A) | '02' (B)
  seat_no         VARCHAR(2) NOT NULL,                      -- '01'..'99'
  student_no      VARCHAR(6) GENERATED ALWAYS AS (grade_code || class_code || seat_no) STORED UNIQUE,
  name            TEXT NOT NULL,
  name_kana       TEXT,
  birthday        DATE,
  gender          TEXT NOT NULL CHECK (gender IN ('male','female')),
  category        TEXT NOT NULL DEFAULT '一般寮生',
  room_no         VARCHAR(8) NOT NULL,                      -- 'M101' / 'W203'
  dorm_unit       SMALLINT NOT NULL CHECK (dorm_unit IN (1,2,4)),
  is_overseas     BOOLEAN NOT NULL DEFAULT FALSE,           -- 留学生 flag (Q11)
  email           TEXT,
  phone           TEXT,
  avatar_url      TEXT,
  registered_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  status          TEXT NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active','locked','graduated','transferred','paused')),
  CHECK (
    (gender = 'male'   AND dorm_unit IN (1,2)) OR
    (gender = 'female' AND dorm_unit = 4)
  )
);
CREATE INDEX idx_students_dorm ON students (dorm_unit, status);
CREATE INDEX idx_students_no ON students (student_no);
```

### 4.2 `accounts` (✅ 已定)

```sql
CREATE TABLE accounts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      UUID NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
  password_hash   TEXT NOT NULL,                            -- bcrypt cost 12
  failed_count    SMALLINT NOT NULL DEFAULT 0,
  locked_until    TIMESTAMPTZ,                              -- NULL = unlocked
  lock_level      SMALLINT NOT NULL DEFAULT 0,              -- 0..6 (升级阶段，6 = 永久锁)
  last_login_at   TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

锁定升级表（IOS_DESIGN_LOG §3.6 真值）:

| lock_level | 触发 | 锁定时长 | 老师通报 |
|---|---|---|---|
| 0 | (正常) | — | — |
| 1 | 连续 3 次错 | 30 秒 | ✅ |
| 2 | 解锁后再错 1 次 | 1 分钟 | ✅ |
| 3 | 同上 | 5 分钟 | ✅ |
| 4 | 同上 | 30 分钟 | ✅ |
| 5 | 同上 | 1 小时 | ✅ |
| 6 | 同上 | **永久** → 「宿監に連絡してください」 | ✅ |

### 4.3 `teachers` + `class_teacher_assignment` (✅ 已定 — R3 + D11 + D12)

```sql
CREATE TABLE teachers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  login_id        VARCHAR(32) NOT NULL UNIQUE,              -- 教师独自 ID
  name            TEXT NOT NULL,
  email           TEXT NOT NULL UNIQUE,
  password_hash   TEXT NOT NULL,
  role            TEXT NOT NULL CHECK (role IN (
    '寮務部長','寮務課長','国際交流部長','国際交流課長','管理係',
    '寮監','学習担当','寮務一般教師'
  )),
  -- 注: 4-30 D12 → 加「管理係」单独 role（实物表必有审批人）
  -- 注: 4-30 itsuki 補正 → 「国際交流課長」役职は存在する（外泊届表に印欄が無いだけ、帰国届等 他届で関与する可能性）→ ENUM 保留
  -- 注: 「担任」不在本 ENUM — 通过下面 class_teacher_assignment 表关联（D11 拍板）
  assigned_dorm   SMALLINT CHECK (assigned_dorm IS NULL OR assigned_dorm IN (1, 2, 4)),
  -- NULL = 跨寮（如 寮務部長）/ 1 = 男寮（暗指 1+2 合同）/ 4 = 女寮（D2 拍板方案 A）
  failed_count    SMALLINT NOT NULL DEFAULT 0,
  locked_until    TIMESTAMPTZ,
  last_login_at   TIMESTAMPTZ,
  status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','disabled')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- D11 拍板（2026-04-30）— 担任は teachers.role に入れず、本表で紐付け
-- 理由: (1) 一人の教師が同時に複数の学年・組を担任する可能性 (2) 学年度更替時に audit 履歴必要
CREATE TABLE class_teacher_assignment (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id         UUID NOT NULL REFERENCES teachers(id),
  grade_code         VARCHAR(2) NOT NULL,                   -- '01'..'06' (中1〜高3)
  class_code         VARCHAR(2) NOT NULL,                   -- '01' (A) | '02' (B)
  academic_year      INTEGER NOT NULL,                      -- 2026, 2027 ...
  is_homeroom        BOOLEAN NOT NULL DEFAULT TRUE,         -- 担任 (TRUE) / 副担任 (FALSE)
  effective_from     DATE NOT NULL,
  effective_to       DATE,                                  -- NULL = 现役
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (grade_code, class_code, academic_year, is_homeroom, effective_from)
);
CREATE INDEX idx_cta_teacher ON class_teacher_assignment (teacher_id) WHERE effective_to IS NULL;
CREATE INDEX idx_cta_class ON class_teacher_assignment (grade_code, class_code, academic_year) WHERE effective_to IS NULL;
```

**API 取「学生 X の担任」**: `SELECT teacher_id FROM class_teacher_assignment WHERE grade_code = student.grade_code AND class_code = student.class_code AND academic_year = current_year() AND is_homeroom = TRUE AND effective_to IS NULL LIMIT 1`

### 4.4 `applications` (出寮届) — system_features §8.2 扩充

```sql
CREATE TABLE applications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      UUID NOT NULL REFERENCES students(id),
  kind            TEXT NOT NULL CHECK (kind IN ('帰省','外泊','帰国')),
  -- 共通字段
  leave_date      DATE NOT NULL,                            -- 出寮日 (#3 明天起)
  leave_method    TEXT NOT NULL,                            -- 帰省方法（自由 + 巴士选择 §4.7）
  leave_time      TIME NOT NULL,
  return_date     DATE NOT NULL,
  return_method   TEXT NOT NULL,
  return_time     TIME NOT NULL,
  -- 外泊/帰国 only
  stay_locations  JSONB,                                    -- [{address, name, kind}, ...] 复数可
  meals_skip_from TIMESTAMPTZ,                              -- 食事不要 from (#38 from/to 明确)
  meals_skip_to   TIMESTAMPTZ,
  -- 帰国 only
  flight_dep_air  TEXT,
  flight_dep_at   TIMESTAMPTZ,
  flight_arr_air  TEXT,
  flight_arr_at   TIMESTAMPTZ,
  -- 巴士关联（§4.7 P2 实装）
  bus_route_id    UUID,                                     -- FK 后续加
  -- 状态
  submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','approved_partial','approved','rejected','withdrawn')),
  -- 元
  withdrawn_at    TIMESTAMPTZ,                              -- 学生撤回（如允许）⏳ §10-D3
  CHECK (leave_date >= (CURRENT_DATE + INTERVAL '1 day'))   -- #3 出寮日 = 明天起
);
CREATE INDEX idx_app_student ON applications (student_id, status);
CREATE INDEX idx_app_status_date ON applications (status, leave_date);
```

> **`#3 出寮日 = 明天起` 的 CHECK 约束**: PostgreSQL 不允许在 CHECK 里用 `CURRENT_DATE`（非 immutable），实际应做成 trigger or 应用层校验。CC 假设 = **应用层校验 + DB 留 trigger 兜底**。code agent 实装时必加 trigger BEFORE INSERT。
> **教師当日録入豁免（#30）**: 教師から POST 时可传 `bypass_future_check=true`（仅 `寮務一般教師` 以上 role 接受），跳过 leave_date >= tomorrow 校验。

### 4.5 `application_approvals` (✅ 已定 §8.2)

```sql
CREATE TABLE application_approvals (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id  UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  approver_role   TEXT NOT NULL CHECK (approver_role IN (
    '担任','寮務部長','寮務課長','国際交流部長','国際交流課長','管理係'
  )),
  -- 4-30 实物表 evidence: 外泊届の chain 図には 担任 + 寮務課長 + 管理係（一般）/ + 国際交流部長 + 寮務部長（留学生）が必有
  -- 「国際交流課長」は外泊届チェーンには印欄無いが、帰国届等の他届で関与する可能性 → ENUM 保留（実物表入手後 chain 生成ロジックで条件分岐）
  approver_id     UUID REFERENCES teachers(id),             -- NULL = 还没承认
  decided_at      TIMESTAMPTZ,
  decision        TEXT CHECK (decision IN ('approve','reject')),
  comment         TEXT,                                     -- #13 给提交者显示的评论
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (application_id, approver_role)
);
```

**承认者リスト生成规则（业务层 — 2026-04-30 实物表 evidence 為準）**:
- **外泊（非留学生）** → 担任 + 寮務課長 + 管理係 = 3 行
- **外泊（留学生 `is_overseas=true`）** → 担任 + 国際交流部長 + 寮務課長 + 寮務部長 + 管理係 = 5 行
- **帰省** → ⏳ 实物表 evidence 缺（暫定 = 担任 + 寮務課長 + 管理係、外泊と同チェーン仮置き、本人確認まで保留）
- **帰国** → ⏳ 同上（暫定 = 留学生 5 行 / 非留学生 3 行、外泊と同パターン仮置き）

担任の解决: 该学生の `class_teacher_assignment` 表からひいた `teacher_id` を `application_approvals` 行作成時に staff_id として確定（学生提出時刻の現役担任）

**整体 status 派生规则**（`applications.status` trigger 自动更新）:
- 任一行 `decision='reject'` → 整体 `rejected`
- 全部行 `decision='approve'` → 整体 `approved`
- 部分行 `approve` 且无 `reject` → `approved_partial`
- 都为 NULL → `pending`

### 4.6 `study_roster` / `study_absence_requests` / `study_checkins` (✅ 已定 §8.3)

```sql
CREATE TABLE study_roster (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      UUID NOT NULL REFERENCES students(id),
  academic_term   TEXT NOT NULL,                            -- '2026-spring' / '2026-fall'
  added_by        UUID REFERENCES teachers(id),             -- NULL = system (中学全员自动)
  added_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  removed_at      TIMESTAMPTZ,                              -- 期末后 reset
  UNIQUE (student_id, academic_term)
);

CREATE TABLE study_absence_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      UUID NOT NULL REFERENCES students(id),
  target_date     DATE NOT NULL,
  reason          TEXT NOT NULL,
  submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','approved','rejected')),
  decided_by      UUID REFERENCES teachers(id),
  decided_at      TIMESTAMPTZ,
  comment         TEXT,
  -- 截止: 19:40 当日开始前
  CHECK (submitted_at::time < TIME '19:40' OR submitted_at::date < target_date)
);
CREATE INDEX idx_sar_date_status ON study_absence_requests (target_date, status);

CREATE TABLE study_checkins (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      UUID NOT NULL REFERENCES students(id),
  target_date     DATE NOT NULL,
  checked_at      TIMESTAMPTZ,                              -- NULL = absent
  status          TEXT NOT NULL DEFAULT 'init'
                  CHECK (status IN ('init','present','late','absent','exempt')),
  recorded_by     UUID REFERENCES teachers(id),             -- 学習担当
  overridden_by   UUID REFERENCES teachers(id),             -- 后续修正
  override_reason TEXT,
  UNIQUE (student_id, target_date)
);
CREATE INDEX idx_sc_date_status ON study_checkins (target_date, status);
```

### 4.7 `rollcall_sessions` / `rollcall_events` (RollCall_Spec §10)

```sql
CREATE TABLE rollcall_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dorm_unit_set   SMALLINT[] NOT NULL,                      -- {1,2} 或 {4} (R4)
  session_type    TEXT NOT NULL CHECK (session_type IN ('morning','evening')),
  schedule_mode   TEXT NOT NULL DEFAULT 'split'
                  CHECK (schedule_mode IN ('split','merged_normal')),
  day_type        TEXT NOT NULL CHECK (day_type IN ('weekday','weekend_holiday')),
  session_status  TEXT NOT NULL DEFAULT 'draft'
                  CHECK (session_status IN ('draft','running','ended')),
  started_at      TIMESTAMPTZ,
  started_source  TEXT CHECK (started_source IN ('teacher','system')),
  started_by      UUID REFERENCES teachers(id),
  ended_at        TIMESTAMPTZ,
  ended_source    TEXT CHECK (ended_source IN ('teacher','system')),
  ended_by        UUID REFERENCES teachers(id),
  -- 4 个时刻（schedule + effective）
  scheduled_window_start_at  TIMESTAMPTZ NOT NULL,
  scheduled_on_time_end_at   TIMESTAMPTZ NOT NULL,
  scheduled_late_end_at      TIMESTAMPTZ NOT NULL,
  scheduled_auto_end_at      TIMESTAMPTZ NOT NULL,
  settle_at       TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rollcall_events (                              -- append-only
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      UUID NOT NULL REFERENCES rollcall_sessions(id),
  student_id      UUID NOT NULL REFERENCES students(id),
  device_id       UUID,                                     -- FK 加（后续加 devices 表）
  path_type       TEXT CHECK (path_type IN ('A','B','manual')),
  base_status     TEXT NOT NULL CHECK (base_status IN ('init','present','late','absent','exempt_range')),
  status_source   TEXT NOT NULL CHECK (status_source IN (
    'auto_nfc','auto_settle','manual_checkin','teacher_override'
  )),
  -- 2026-05-21 (A-022 b1): applied_group 字段已删除
  -- 窗口永远固定 (RollCall_Spec §5.4)，分组直接走 student 当前 group (§6.4)
  checked_in_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  idempotency_key TEXT,                                     -- 路径 B only
  card_uid        TEXT,                                     -- 路径 A
  reason          TEXT                                      -- override 时必填
);
CREATE UNIQUE INDEX uq_rce_path_b ON rollcall_events (session_id, idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE UNIQUE INDEX uq_rce_path_a ON rollcall_events (
  session_id, card_uid, date_trunc('second', checked_in_at)
) WHERE card_uid IS NOT NULL;                               -- RollCall_Spec §10.2 路径 A 幂等
```

> **session 创建**（RollCall_Spec 附录 C.5）: 系统 cron 每天按时刻表自动创建（`scheduled_window_start_at - 5min`），覆盖男寮 morning + evening + 女寮 morning + evening = **每天 4 个 session**（schedule_mode = split 时足球部+普通寮生 2 组各自 session — 详见 RollCall_Spec §6.4，分组直接走 student 当前 `student_group`）。

### 4.8 `notifications` / `notification_log`

```sql
CREATE TABLE notification_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel         TEXT NOT NULL CHECK (channel IN ('email','push','in_app')),
  template_key    TEXT NOT NULL,                            -- 'application_submitted' 等
  target_type     TEXT NOT NULL CHECK (target_type IN ('student','teacher','role')),
  target_id       UUID,                                     -- target_type=role 时为 NULL，target_role 列入 payload
  payload         JSONB NOT NULL,
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','sent','failed','retrying')),
  attempts        SMALLINT NOT NULL DEFAULT 0,
  last_error      TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at         TIMESTAMPTZ
);
CREATE INDEX idx_notif_status ON notification_log (status, created_at) WHERE status IN ('pending','retrying');
```

### 4.9 `audit_logs`

```sql
CREATE TABLE audit_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_type      TEXT NOT NULL CHECK (actor_type IN ('student','teacher','system')),
  actor_id        UUID,                                     -- system 时 NULL
  action          TEXT NOT NULL,                            -- 'application.approve' 等 dot-notation
  target_type     TEXT NOT NULL,
  target_id       UUID NOT NULL,
  payload         JSONB,
  ip_address      INET,
  user_agent      TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_target ON audit_logs (target_type, target_id, created_at);
CREATE INDEX idx_audit_actor ON audit_logs (actor_type, actor_id, created_at);
-- DB 触发器: 拒绝 UPDATE/DELETE
```

### 4.10 `student_registration_codes`（2026-05-03 itsuki 拍板、App Store 公開対策）

**⚠ 権威源は `02_design/system_features.md §7.16`。本節は schema 詳細のみ。**

```sql
CREATE TABLE student_registration_codes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code            VARCHAR(6) NOT NULL,                      -- 6 桁数字 '000000'-'999999'
  created_by      UUID NOT NULL REFERENCES teachers(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at      TIMESTAMPTZ NOT NULL,                     -- created_at + 5 分
  invalidated_at  TIMESTAMPTZ,                              -- 新コード生成で旧を即無効化
  CONSTRAINT code_format CHECK (code ~ '^[0-9]{6}$')
);

-- 同時有効コードはシステム全体で 1 個のみ（unique partial index）
CREATE UNIQUE INDEX uniq_active_code
  ON student_registration_codes ((1))
  WHERE invalidated_at IS NULL AND expires_at > now();

-- 検証 query で頻出する条件 (active + 未 expire) 高速化
CREATE INDEX idx_active_codes
  ON student_registration_codes (code)
  WHERE invalidated_at IS NULL;
```

**生成 logic（`POST /admin/registration-code/refresh`）**:
1. Tx 開始
2. `UPDATE student_registration_codes SET invalidated_at = now() WHERE invalidated_at IS NULL` — 既存有効コードを即無効化
3. 新規 code 生成（6 桁 random、衝突時は `ON CONFLICT` で再生成）
4. `INSERT INTO student_registration_codes (code, created_by, expires_at) VALUES (?, ?, now() + interval '5 minutes')`
5. Tx commit
6. audit_log: `action='registration_code.refresh'`, `actor=teacher_id`, `target=new_code_id`, `payload={old_code_id, new_code}`

**検証 logic（`POST /accounts` 内）**:
```sql
SELECT id FROM student_registration_codes
WHERE code = :input
  AND invalidated_at IS NULL
  AND expires_at > now()
LIMIT 1;
```
hit なし → `INVALID_REGISTRATION_CODE` (422)。hit あり → 通過 + audit_log: `action='registration_code.use'`, `actor=null`, `target=code_id`, `payload={student_no}`。

> ⚠️ **コードは「使用」しても無効化しない**（再利用可、集団登録対応 §7.16.6）。expires_at 経過 or 教師再生成で初めて失効。

---

## 5. API 列表 — P0

> URL 前缀 = `/api/v1/`。OpenAPI spec 由 FastAPI 自动生成（`/docs`）。

### 5.1 認証（学生 + 教师）

#### 5.1.1 `POST /sessions/student` — 学生 login

req:
```json
{ "student_no": "060218", "password": "..." }
```

res 200:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 86400,
  "student": { "id": "...", "name": "リュウイヒ", "dorm_unit": 1, "is_overseas": true, ... }
}
```

err:
- `INVALID_CREDENTIALS` (401) — 含 `failed_count` / 距下次锁定还差几次
- `ACCOUNT_LOCKED` (423) — 含 `locked_until` / `lock_level`
- `ACCOUNT_INACTIVE` (403) — `status != 'active'`

锁定判定（IOS_DESIGN_LOG §3.6）:
- 连续 3 次错 → `lock_level=1, locked_until=now+30s` + 触发 `notification_log` (target_role=寮監)
- 解锁后再错 1 次 → `lock_level += 1`，时长按表升级
- 成功登录 → `failed_count=0, lock_level=0`

> **⏳ §10-D5**: 「成功登录后 lock_level 是否清零」？CC 假设 = **是**（=「正常使用 1 次后过去的连错记录失效」）。否则 lock_level=5 的学生登一次就锁很久，反人类。

#### 5.1.2 `POST /sessions/teacher` — 教师 login

req:
```json
{ "login_id": "...", "password": "..." }
```

res 200 = 学生类似 + `teacher: { ..., role: '寮務部長', assigned_dorm: null }`

#### 5.1.2b 教师账户管理 endpoints（2026-05-27 实名账户登录方式拍板に伴う追加）

| URL | 認証 | 用途 |
|---|---|---|
| `GET /teachers/public` | **無認証** | 登录页第 1 屏列表 — 只返 `id + name + assigned_dorm + last_login_at`（不暴露 login_id / email / role / status，防爬虫枚举攻击）|
| `GET /teachers` | 寮務部長 / 寮務課長 / 寮監 | 既存（dump 全字段、登录後の教师管理页用）|
| `POST /teachers` | 寮務部長 / 寮務課長 / 寮監 / 学習担当 | 直接创建教师（v1.0 简化：name + login_id + email + password + role + assigned_dorm。同时存在邀请码流程 `POST /teachers/invitations` + `POST /teachers/register`，v1.0 web 不实装 UI、v1.1 候补）|
| `DELETE /teachers/{id}` | 同上 | 删除教师（自分自身は削除不可 — 400 `CANNOT_DELETE_SELF`）|

关連: §3.4「前台不允许自助注册任何教师账号 / 必须先用已存在的教师账号登录 → 加 / 删」拍板，UX 設計は `03_dev/teacher_web/WEB_DESIGN_LOG.md §5.1' / 5.3'`。

#### 5.1.3 `POST /sessions/refresh` / `DELETE /sessions/current`

token 续期 / 退出（学生 + 教师共通）。

#### 5.1.4 `assigned_dorm` JWT claim

教师 JWT payload 必含 `assigned_dorm`，所有 dorm-scoped API 默认按此 filter（除非教师 role ∈ {寮務部長, 寮務課長, 国際交流部長, 国際交流課長} = 跨寮，可显式传 `?dorm=...`）。

#### 5.1.5 `POST /accounts` — 学生新規登録（2026-05-03 拍板で `registration_code` 必須化）

req:
```json
{
  "name": "リュウイヒ",
  "name_kana": "リュウイヒ",
  "birthday": "2006-10-14",
  "gender": "female",
  "grade_code": "06",
  "class_code": "02",
  "seat_no": "18",
  "category": "一般寮生",
  "room_no": "W101",
  "is_overseas": true,
  "email": "...",
  "phone": "...",
  "password": "...",
  "registration_code": "483271"     // ⭐ 2026-05-03 追加（§4.10 + system_features §7.16）
}
```

処理 flow:
1. `registration_code` 検証（§4.10 検証 logic）→ fail 時 `INVALID_REGISTRATION_CODE` (422)
2. `student_no = grade_code || class_code || seat_no` 生成、既存学生と衝突 check（重複時 `STUDENT_NO_TAKEN` 422）
3. `room_no` regex 校验（§5.0 dorm_unit ↔ prefix 一致性 — `INVALID_ROOM_FORMAT` 422）
4. Tx で `students` + `accounts` 同時 insert
5. registration_code 使用 audit_log 記録（§4.10）
6. 永続 JWT 発行（学生 login 同等 = `expires_in: 86400`）+ session 永久保持（IOS_DESIGN_LOG §3.5）

res 201:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 86400,
  "student": { "id": "...", "student_no": "060218", "name": "リュウイヒ", ... }
}
```

err:
- `INVALID_REGISTRATION_CODE` (422) — コード不正 / expire / 無効化済
- `STUDENT_NO_TAKEN` (422) — 学号重複（IOS_DESIGN_LOG §3.9.2 重複チェック失敗）
- `INVALID_ROOM_FORMAT` (422) — 房间号 prefix が dorm_unit / gender と不整合
- `EMAIL_TAKEN` (422)

#### 5.1.6 `DELETE /accounts/me` — 学生账号删除（2026-05-07 拍板，Apple 5.1.1(v) 强制）

**用途**：Apple App Store Review Guideline 5.1.1(v) 自 2022-06 起强制要求 app 内有账号删除入口（不能只让用户邮件联系）。未实装会被审核 reject。详细 spec: `system_features.md §7.18`。

**req**：
```
DELETE /api/v1/accounts/me
Authorization: Bearer <学生 JWT>
（body 无）
```

**res**：`204 No Content`（body 无）

**处理流程**：
1. `Depends(deps.get_current_student)` 验 JWT + 取 student row
2. `student.status = 'deleted'`（软删除，不物理 DELETE）
3. 写 `AuditLog`：`actor_type='student'`、`action='account.delete_self'`、`target_id=student.id`、`payload={student_no, name}`
4. `db.commit()` → 返回 204

**软删除理由**：
- 物理删除会破坏关联的点呼出席审计、申请历史（`applications.student_id` FK）— 寮务审计要求
- `students.status='deleted'` 后 `get_current_student` dep 自动返回 `ACCOUNT_INACTIVE` → 后续登录 + 任何 API 调用都被拒绝
- 物理删除于 1 年后由 cron job 执行（隐私政策第 5 条）

**err**：
- `INVALID_CREDENTIALS` (401) — token 无效 / 已删除
- `ACCOUNT_INACTIVE` (403) — 已经是 deleted 状态（重复调用幂等）

**关联文件**：
- `app/routers/accounts.py:delete_my_account`
- iOS：`Features/MyPage/MyPageStubs.swift` MySettingsView accountDeletionSection（IOS_DESIGN_LOG §3.14）
- iOS API client：`Foundation/Network/Endpoints/AuthAPI.swift` `AccountsAPI.deleteMyAccount()`

### 5.x 教師 admin — 学生登録コード（2026-05-03 拍板、§4.10 + system_features §7.16）

> アクセス権限 = `teacher` JWT + 「寮務管理」権限（§3.4 教師権限モデル）。他 role は 403。

#### 5.x.1 `GET /admin/registration-code/current`

現在有効なコードを返す。教師 Web パネル mount 時 + 30 秒 polling。

res 200（有効コードあり）:
```json
{
  "code": "483271",
  "created_at": "2026-04-15T09:32:14+09:00",
  "expires_at": "2026-04-15T09:37:14+09:00",
  "created_by": { "id": "...", "name": "田中 寮務課長" }
}
```

res 200（有効コードなし — 全 expire / 未生成）:
```json
{ "code": null }
```

#### 5.x.2 `POST /admin/registration-code/refresh`

新規コード生成。既存有効コードは即無効化（§4.10 logic）。

req: `{}`（body 空）

res 201 = `GET /current` と同形式（新コード）

err:
- `RATE_LIMITED` (429) — 直前 10 秒以内に同教師が呼んだ場合（連打防止 / system_features §7.16.8）

#### 5.x.3 `GET /admin/registration-code/history?limit=50` ⏳ v1.1

過去のコード履歴一覧（教師 Web v1.1 履歴 tab 用）。v1.0 範囲外。

#### 5.x.4 Reviewer 永久码例外条款（2026-05-08 itsuki 拍板）

权威 spec: `system_features.md §7.20` + §7.16 例外条款。

**Schema 改动**（migration `f6a7b8c9d0e1_add_demo_reviewer_flags`）：
- `students.is_demo: bool DEFAULT false` + `idx_students_is_demo` 索引
- `student_registration_codes.is_reviewer: bool DEFAULT false` + `idx_src_is_reviewer` 复合索引

**`/refresh` 行为变更**：
- `UPDATE WHERE invalidated_at IS NULL` → `UPDATE WHERE invalidated_at IS NULL AND is_reviewer = false`
- 即：reviewer 码不被普通 refresh 作废（permission/business 层共存）

**`/current` 行为变更**：
- `SELECT WHERE invalidated_at IS NULL AND expires_at > now()` → 加 `AND is_reviewer = false`
- 即：老师面板只看主体码，看不到 reviewer 码 → 防泄漏

**`_generate_code` 范围变更**：
- `random.randint(0, 999999)` → `random.randint(0, 999998)`
- 即：`"999999"` reserved 给 reviewer 码，普通 refresh 永不生成此值

**`POST /accounts` 不变**：
- `_validate_registration_code` 逻辑维持 — 只看 `invalidated_at IS NULL AND expires_at > now()`，不区分 is_reviewer
- 即：reviewer 码也是合法注册码，可用于 RegisterStep5（仅老师演示用）

**Admin 学生列表过滤**（`is_demo=False` 默认过滤）：
- `rollcall.session_board` (`GET /rollcall/sessions/:id/board`) — 出席板
- `rollcall._settle_absent` — 缺席结算
- `applications.list_pending_for_me` (`GET /applications/pending-for-me`) — 老师待审申请
- 注：`accounts.create_account` 学号/email 查重 + `auth.login` 不加过滤（必须能登录 + 防重复创建）

**测试覆盖**（`tests/test_demo_reviewer.py`）：
- `test_reviewer_code_not_invalidated_by_refresh`
- `test_reviewer_code_can_register_account`
- `test_reviewer_code_not_visible_in_current`
- `test_demo_student_excluded_from_session_board`
- `test_generate_code_never_returns_999999`

### 5.2 学生 — 出寮届（#1-#9）

#### 5.2.1 `POST /applications` — 提交（#1 #2 #3 #4）

req（外泊例）:
```json
{
  "kind": "外泊",
  "leave_date": "2026-05-03",     // 必须 >= 明天 (#3)
  "leave_method": "JR + バス",
  "leave_time": "08:00",
  "return_date": "2026-05-05",
  "return_method": "JR",
  "return_time": "20:00",
  "stay_locations": [
    { "kind": "ホテル", "name": "東横イン岡山", "address": "..." }
  ],
  "meals_skip_from": "2026-05-03T08:00:00+09:00",   // (#38 from/to 明确)
  "meals_skip_to":   "2026-05-05T13:00:00+09:00",
  "bus_route_id": null
}
```

约束（业务层校验）:
- (#1) `student_id` = `current_user.id`（不能代别人 — 拒 `FORBIDDEN_PROXY_SUBMIT`）
- (#3) `leave_date >= today + 1`（拒 `LEAVE_DATE_NOT_FUTURE`）
- (#4) 不要的字段不传 / 传 null（API 接受 sparse 对象）
- kind=帰国 时 `flight_*` 必填
- `meals_skip_from < meals_skip_to`

res 201:
```json
{
  "application_id": "...",
  "status": "pending",
  "approval_chain": [
    { "approver_role": "寮務部長", "decision": null },
    { "approver_role": "寮務課長", "decision": null },
    { "approver_role": "国際交流部長", "decision": null },   // 留学生 + 外泊/帰国 时
    { "approver_role": "国際交流課長", "decision": null }
  ],
  "submitted_at": "..."
}
```

副作用:
- (#6 / R1) 给上述 approver_role 的全部教师发 **email** notification（每个 role 可能多人）
- 写 `audit_logs(action='application.submit')`

#### 5.2.2 `GET /applications/mine` — 自己的提交履歴

query: `?status=pending|approved|...&from=&to=`
res: 自分のみ list + `approval_chain` (#5 承认状态显示)

#### 5.2.3 `GET /applications/:id` — 单件詳細

学生只能看自己的；教師按 dorm filter（assigned_dorm 男寮 → 只能看 1·2 寮学生的；跨寮役职 → 全件）

#### 5.2.4 `DELETE /applications/:id` — 撤回

⏳ §10-D3 待拍板（学生能否撤回未承认的届？deadline 内的话允许？）

### 5.3 役职 — 出寮届承认（#10-#13）

#### 5.3.1 `GET /applications/pending-for-me`

返回当前役职 (`current_teacher.role`) 还没决定的 `application_approvals` 行 + 关联 application（按 `application.submitted_at ASC` 排序）。

#### 5.3.2 `POST /applications/:id/approvals` — 承认 / 不承认（#10）

req:
```json
{ "decision": "approve" | "reject", "comment": "（任意）" }
```

约束:
- `current_teacher.role` 必须在 `application_approvals(application_id, approver_role)` 待决行里
- 同一 role 只能决定一次（`UNIQUE (application_id, approver_role)`）

res 200: 更新后 `application.status` + `approval_chain`。
副作用:
- 如果整体 status 变成 final（approved / rejected）→ 给学生发 push（email 不必）
- audit_logs

#### 5.3.3 `POST /applications/:id/comments` — 役职 → 学生评论（#13）

不影响审批结果，只追加评论。**杭田弱点 = 这里**（itsuki 差別化）。

req:
```json
{ "comment": "外泊先の連絡先を追加で教えてください" }
```

副作用: 给学生 push + in_app（不发 email — 不是审批结果）。

### 5.4 学習 — iPad ★ (#14-#20 学習 部分)

**前提**: 当前教师 role ∈ {寮監, 学習担当, 寮務一般教師}。

#### 5.4.1 `GET /study/today/attendees` — 一本道入口（#14）

**R2 一本道关键 endpoint** — 不需任何 query param。

返回:
```json
{
  "target_date": "2026-04-30",
  "study_start_at": "2026-04-30T19:40:00+09:00",
  "expected_attendees": [
    {
      "student_id": "...",
      "student_no": "060218",
      "name": "リュウイヒ",
      "room_no": "M101",
      "dorm_unit": 1,
      "expected_status": "expected",     // expected / exempted_outstay / exempted_absence_request
      "exemption_reason": null,
      "checkin": null                    // 如已签 → { checked_at, status }
    }, ...
  ],
  "exempted_count": { "outstay": 3, "absence_request": 2 },
  "summary": { "expected": 28, "checked_in": 0, "late": 0, "absent": 0 }
}
```

业务规则:
- **当天有效 study_roster**（中学全员 = 自动 + 高中手动）
- **减去** `applications.status='approved'` 且 `target_date ∈ [leave_date, return_date]` 的人 (#14 出寮届控除)
- **减去** `study_absence_requests.status='approved'` 且 `target_date=今日` 的人 (#14 学習欠席届控除)
- 按 `current_teacher.assigned_dorm` filter（R4）
- name 五十音排序

#### 5.4.2 `POST /study/checkins` — 学習出席记录（#15）

req:
```json
{ "student_id": "...", "checked_at": "2026-04-30T19:42:00+09:00" }   // checked_at 默认 now
```

业务:
- `checked_at < 19:40` → `present`
- `checked_at >= 19:40` → `late`
- 19:40 后結束扫过 → 残りは `absent`（自动判定 #20、走 cron）

副作用: WebSocket broadcast → iPad 当前页 badge 更新 + 名前 text 上"✓"。

#### 5.4.3 `POST /study/checkins/bulk-finalize` — 一本道结束按钮（#15）

教师在 19:55 等节点按 iPad 上一个大按钮 → 把当天还未签的人批量 `absent`。

req: `{ "target_date": "2026-04-30" }` (默认 today)
res: `{ "finalized_count": 5, "absent_students": [...] }`

#### 5.4.4 `PATCH /study/checkins/:id` — 手动修正（#20 后续可改）

req: `{ "status": "present", "override_reason": "ノックの音気付かなかった" }`
audit_logs(action='study_checkin.override')

#### 5.4.5 学習欠席届 — 学生侧 `POST /study/absence-requests` / 教师侧 `POST /study/absence-requests/:id/decision`

学生提交 → 学習担当（`role='学習担当'` 教师）email 通知 R1。学習担当 approve/reject。

约束:
- 学生 `submitted_at < 19:40` 当日（拒 `LATE_SUBMISSION`）

### 5.5 点呼 — iPad ★ (#16-#20 点呼 部分)

> 已存在 demo 实装 `POST /checkin?no=XX` (路径 A 简化版) — v1 升级为正式 schema。

#### 5.5.1 `GET /rollcall/today/sessions`

返回当天 4 个 session（男寮 M / 女寮 E + 男寮 M / 男寮 E）的状态。按 `current_teacher.assigned_dorm` filter。

#### 5.5.2 `POST /rollcall/sessions/:id/start` / `POST /rollcall/sessions/:id/end`

老师手动开始 / 结束。规则见 RollCall_Spec §5.4 / §5.5（边界 `NOT_YET_ALLOWED` / `ALREADY_RUNNING` 必现）。

#### 5.5.3 `POST /rollcall/sessions/:id/checkins` — NFC 卡 / 手动签到

req:
```json
{ "card_uid": "04A3B...", "device_id": "...", "ts_local": "..." }
// 或手动: { "student_id": "...", "status_source": "manual_checkin" }
```

判定 RollCall_Spec §7。res 含 base_status。

#### 5.5.4 `GET /rollcall/sessions/:id/board` — 全座位现状（iPad 主屏 polling / WS source）

按 `dorm_unit_set` filter 学生 list + 各人 base_status + overlay_badges。

#### 5.5.5 `GET /rollcall/sessions/:id/summary` — 「点呼総結」中层页 (#5.6 RollCall_Spec)

返回 4 区块:
```json
{
  "absent": [...],
  "late": [...],
  "health_issue": [...],
  "exempted_outstay": [...]
}
```

#### 5.5.6 `PATCH /rollcall/events/:id` — 老师改判（RollCall_Spec §11）

req: `{ "to_status": "late", "reason": "...", "evidence": "..." }`
约束: `reason` 必填；时限矩阵（§11.3）按教师 role + 距 session_started_at 时间检查。
副作用: ledger 自动 +/- 分（§11.4）+ audit_logs。

#### 5.5.7 `GET /rollcall/me/today` — 学生查今日本人点呼（2026-06-11 新增 / R-1+R-2）

学生令牌（`get_current_student`）。返回今天自己所属寮的点呼场次 list（`MyRollCallTodaySession`）：`session_type` / `day_type` / `session_status` + 四个时间窗 `scheduled_window_start_at` / `scheduled_on_time_end_at` / `scheduled_late_end_at` / `scheduled_auto_end_at` + 本人 `my_status`（present/late/absent/exempt_range，nil=未签）+ `my_checked_in_at`。寮过滤 = `student.dorm_unit in session.dorm_unit_set`（Python 侧 filter），join `RollCallEvent` 取本人状态。空数组 = 本日无我寮点呼。
**背景**：补全 iOS 缺口——iOS 原本没有「拉本人点呼时间窗 + 判定」的链路，导致显示链整条写死假数据。iOS 用四时间窗 + 当前时刻真实算 idle / 进行中倒计时 / 時間内 / 遅刻。配套 `student_profile` profile 接口给 `ProfileRollCallEntry` 补 `scheduled_window_start_at` / `scheduled_on_time_end_at`（详情页显真实開始/締切）。

#### 5.5.8 体调上报族 `POST/GET /rollcall/reports*`

点呼时学生上报（功能③）。`POST /rollcall/reports`（`RollCallReportCreateIn`：kind=health/absence/other + 自由文本 body + 可选 session_id）；`GET /rollcall/reports/mine` 学生查本人全部上报（按 created_at 倒序，不按 kind 过滤——iOS「体調報告履歴」自行 filter kind=health，2026-06-11 R-5 接上）；`GET /rollcall/reports` 老师查（R4 寮过滤 + demo 隔离 + only_unresolved）；`PATCH /rollcall/reports/:id/resolve` 老师标记已处理。

### 5.6 通知 (R1)

#### 5.6.1 内部 `notifications.email_send(template_key, target, payload)`

不是 public API，是 service module。templates:
- `application_submitted` (target = role の email list)
- `application_decided` (target = student.email — 可選、デフォルト送らない)
- `study_absence_submitted`
- `student_no_changed` (target = 寮務一般教師 email list)

> **⏳ §10-D1**: 邮件 provider 选型 (SendGrid / AWS SES / SMTP relay)。CC 推荐 = **SendGrid**（无服务器、JP IP、free tier 100/day 足够 demo）。

#### 5.6.2 `POST /notifications/test` (admin only) — 邮件功能测试

dev/staging 用，触发 `email_send` 验证 provider 联通。

### 5.7 WebSocket

`WS /ws/rollcall/:session_id` — 教师 iPad 订阅本场实时变化。message:
```json
{ "type": "checkin", "student_id": "...", "base_status": "present", "checked_in_at": "..." }
```

`WS /ws/study/:date` — 学習出席 iPad 订阅。

> v1 必须用 **Redis pub/sub** 跨进程，不能像 demo 那样内存 dict（4 台 iPad 不同后端进程时会失同步）。

### 5.8 点呼机掉线检测 + 离线告警推送 ✅（2026-06-04 itsuki 拍板）

点呼机自己断网时报不了「我离线了」（连后端都连不上）→ **必须由后端发现**。机制：

1. 点呼机↔后端是 WebSocket 长连接（后端推指令）。这条长连接断开 = 后端立刻知道某台点呼机掉线（`device_id` 标记 `offline`）。
2. 后端通过老师网页的 WebSocket（`/api/v1/ws/teacher`）推一条新事件给该寮所有在线老师：
   ```json
   { "type": "device_offline", "device_id": "...", "dorm_unit": "...", "at": "..." }
   ```
3. 点呼机重连成功 → 后端推 `{ "type": "device_online", "device_id": "...", "at": "..." }` 解除告警。

> 事件类型从原来的 `checkin / override / outstay_new` 扩到再加 `device_offline / device_online` 两个。

**离线期间签到数据怎么合并（2026-06-04 itsuki 拍板：老师手动优先）**：网络恢复后点呼机批量补传的离线签到日志（带 swipe_time），和老师在平板上手动判的状态**可能撞同一个学生**。规则：**老师手动判定优先**（人 > 机器，对齐 spec「老师是唯一改判者」永久硬约束）—— 补传日志里该学生若老师已手动判过，不覆盖，只作为 `card` 方式的参考记录写入 `rollcall_events`（append-only 多写一行，不动老师那行）。

---

## 6. 错误码（P0 范围）

> 完整 ERROR_CODES → 后续单独 spec。下面是 P0 必有。

| code | HTTP | 含义 |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | 学号/密码错 |
| `ACCOUNT_LOCKED` | 423 | 锁定中 |
| `ACCOUNT_INACTIVE` | 403 | status != active |
| `FORBIDDEN_PROXY_SUBMIT` | 403 | (#1) 代别人提交 |
| `FORBIDDEN_DORM` | 403 | 教师跨 assigned_dorm 操作 |
| `LEAVE_DATE_NOT_FUTURE` | 422 | (#3) 出寮日 = 今天或过去 |
| `INVALID_KIND_FIELDS` | 422 | (#2) kind 与字段不匹配 |
| `LATE_SUBMISSION` | 422 | 学習欠席届 19:40 后提交 |
| `APPROVAL_ALREADY_DECIDED` | 409 | role 已决定过 |
| `APPROVAL_NOT_REQUIRED` | 403 | 当前 role 不在该届 chain |
| `SESSION_NOT_RUNNING` | 409 | 点呼 |
| `NOT_YET_ALLOWED` | 409 | 老师早于 -5min 按开始 |
| `ALREADY_RUNNING` | 409 | session 已 running |
| `DUPLICATE_REQUEST` | 200 | (silently ignore + log) |
| `UNKNOWN_CARD` | 422 | UID 全无记录 |
| `UNREGISTERED_UID` | 422 | UID 有记录但 card/student inactive |
| `OVERRIDE_TIME_LIMIT` | 403 | RollCall_Spec §11.3 时限超 |
| `OVERRIDE_REASON_REQUIRED` | 422 | reason 空 |
| `INVALID_REGISTRATION_CODE` | 422 | 注册コード不正 / expire / 無効化済（§4.10 + system_features §7.16）|
| `STUDENT_NO_TAKEN` | 422 | 学号重複（§5.1.5）|
| `INVALID_ROOM_FORMAT` | 422 | 房间号 prefix が dorm_unit / gender と不整合（§5.1.5）|
| `EMAIL_TAKEN` | 422 | メール重複（§5.1.5）|
| `RATE_LIMITED` | 429 | 連打 rate limit（§5.x.2 等）|

---

## 7. 安全 / 权限

### 7.1 認証

- JWT HS256, secret 32+ bytes, env var `JWT_SECRET`
- access_token 24h / refresh_token 30d
- refresh 时刷 access；refresh 用 1 次后失效（rotation）
- logout = revoke refresh_token (Redis blacklist)

### 7.2 認可

- **学生 endpoint** (POST /applications, GET /applications/mine 等) 要 `student` JWT
- **教师 endpoint** 要 `teacher` JWT + role 校验
- role 校验放 FastAPI `Depends(require_role([...]))` decorator
- dorm_unit 校验放业务 service 层（不是 endpoint 层 — 因为有"跨寮役职"）

### 7.3 输入校验

- pydantic v2 model 全部 endpoint 入站
- 日期 / 时间 / UUID strict
- 自由文本字段限长（comment 1000 / reason 500 / textarea 2000）+ HTML escape

### 7.4 速率限制

- `/sessions/*` login endpoint: 5 req/min/IP（防爆破）
- `/applications` 提交: 10 req/min/学生（防大量乱提交）
- 用 Redis sliding window

### 7.5 演示账号真隔离（2026-06-07 itsuki 拍板 — is_demo 横切隔离）

**需求**：演示老师账号登录只看演示数据、真老师看真实数据，上线后互不污染（宿舍演示 / Apple 审核用）。同一套生产网页、靠账号区分。

**机制**：
- `Student.is_demo` + `Teacher.is_demo` 两个对称字段（迁移 `d5e6f7a8b9c0`，teachers 表加列 + 索引）
- `deps.demo_scope_for_teacher(teacher)` 返回 `Student.is_demo.is_(teacher.is_demo)` —— 真老师(False)只看真实学生、演示老师(True)只看演示学生。真老师行为同改造前（硬编码 `is_demo.is_(False)` 提升为依登录者而定，常量值不变）
- 所有老师「读取/返回学生数据的列表查询」where 加此过滤；按 student_id 单点操作的端点加 `student.is_demo != teacher.is_demo → 404` 校验
- 跟 R4 寮过滤（`dorm_units_for_teacher`）正交叠加
- 演示数据 `seed.py` **opt-in**（仅 env `DEMO_TEACHER_PASSWORD` 设置时建演示老师 + 3 演示学生），默认关闭 = 隔离未完整期间生产零风险

**⚠️ is_demo 是横切关注点**（遍布全后端老师→学生数据流，需逐端点加过滤）。已覆盖核心列表 + 多数读取端点。**演示账号 v1.0 启用前必须补完**（重大决策，详情见内部跟踪记录）：
- 写权限越界：演示老师能 start/end 真实点呼 session、对真实学生 finalize 晚自习
- approval_chain 邮件：真实学生申请会通知演示老师（演示老师 role 跨寮的副作用）
- 弱边角：principal 端点（songs / lost_found）+ 单点 detail

### 7.5.1 演示账号默认启用 + 全局端点隔离补齐（2026-06-08 itsuki 拍板 B + 3 轮 codex 复审收敛）

itsuki 拍板把演示账号从 opt-in 默认关改成 **默认启用**（`seed.py` 去开关、密码缺省 `demo123`、dev+prod 都建、开箱即用）。这让上面「v1.0 启用前必补完」的隔离债**立刻到期**——默认开 + 公开密码 demo123（演示老师 login_id=demo 经无认证 `/teachers/public` 全网可见）让「全局端点（表无 is_demo 列、只靠角色门）漏的隔离」从「需先攻破账号」变零成本可达。

补完方式：表无 is_demo 列的全局端点靠 `deps.assert_not_demo_teacher(teacher)` 角色门（演示老师 403），社区列表靠 `principal.is_demo` 双向过滤。3 轮 codex 对抗复审挖 + 修 **11 处全局端点**：
- 注册码读 current/history（提权链根基：演示老师读真实码 → POST /accounts 建真实学生账号绕整套隔离）/ 公告发 post_announcement + 回复 post_reply + 删回复 delete_reply / 行事 events + 巴士 bus_routes 写门 / 测试邮件 notifications send_test / 老师目录 list_teachers → 加 `assert_not_demo_teacher`
- 前台无主失物条目（`front_desk` student_id 空时原守卫被 `if student_id` 跳过）→ else 分支补 403
- 点歌 songs + 遗失物 lost_found 社区列表 → join Student 按 `principal.is_demo` 双向隔离（演示侧/真实侧互不看到对方投稿）
- codex 第 3 轮扫全 25 router 无残余 → **0 阻塞 0 重大收敛**

剩 v1.1 唯一弱边角：announcements 公告**读** list/detail（Announcement 表无 is_demo 列，演示老师能读老师广播、非学生隐私，写侧已全堵）。根治要 Announcement 加 is_demo 列。

验证：`test_demo_teacher.py` 7→20 测试 / 后端全量 373 passed / 网页构建退出码 0。commit `15b0ce5`。

---

## 8. 测试要求

- pytest + pytest-asyncio + httpx.AsyncClient
- 覆盖率目标 >= 70%
- **必有 test 场景**:
  - R1 邮件触发: POST /applications → 验 notification_log 行数（不真发，用 mock）
  - R4 dorm filter: 男寮教师 GET 不到女寮学生
  - #1 代提交防护: A 学生 POST 带 student_id=B → 403
  - #3 出寮日: leave_date=今日 → 422
  - 锁定升级: 连错 3+1+1 次 → lock_level=3, locked_until = now+5min
  - 承认 chain: 留学生外泊 → 4 行；非留学生外泊 → 2 行
  - 点呼 RollCall_Spec §7 全 14 个边界（已有 demo test 可参考）

---

## 9. Migration / 部署

- Alembic migration 单调递增, 不回滚 destructive 变更（drop column 等）
- DB 备份: 每日 pg_dump → S3 (or 等价)
- env: `.env.example` 列全 + `.env` gitignore
- Docker Compose 可启动 (PG + Redis + app + nginx)
- v1 部署目标: itsuki 自有 VPS or 学校 server（⏳ §10-D6）

### 9.1 宿舍本地自组装服务器（2026-06-03 itsuki 讨论中 — 部署形态从 VPS 转向本地）

> **背景**：点呼机架构反转后，签到走「点呼机 ↔ 后端」局域网通讯（WebSocket + HTTP）。itsuki 倾向把后端部署在**宿舍一台 24 小时本地服务器**（学校出钱、自己组装），点呼机走局域网连它，延迟低、不依赖外网。这是对 §10-D6「东京 VPS」方案的演进，**最终部署形态待拍板**（本地 / VPS / 并存）。

**这台服务器承载**：后端 API + 数据库 + 老师网页 + iOS / Android App 接口 + 学生数据 + 图片 + 安卓 APK 下载分发（+ v2.0 人脸识别模型，v1.0 不上）。

**自组装配置（itsuki 拍板，约 8.5-10 万日元，学校经费）**：

| 部件 | 选型 | 说明 |
|---|---|---|
| CPU | Intel i3（12/13 代支持 ECC 的型号）或低功耗 Xeon 至强 | 纯文本后端 + 数据库，算力够用 |
| 主板 | 华擎（ASRock）/ 华硕（ASUS）明确支持 ECC 的型号 | |
| 内存 | 16GB **ECC 内存**（带纠错，自动修运行中的数据位错误，防 24 小时连转死机）| |
| 系统盘 | 480GB 企业级固态硬盘（SSD）| 系统 + 数据库（高频读写）|
| 文件盘 | 1-2TB 企业级机械硬盘（HDD）| 图片 / 公告附件 / APK（冷热数据分离）|
| 电源 | 80PLUS 认证大厂电源（海韵 / 振华）| 24 小时稳定 |
| 网络 | 千兆有线网口，网线直连宿舍路由器 | 局域网延迟 1-2 毫秒 |

**为什么自组装不买品牌整机 / Mini PC**：itsuki 拍板 — 软硬结合是 AC 入试项目竞争力（自己选件 + 组装 + 当售后），含金量高于买成品。

**5 年存储估算**（200 学生）：纯文本约 1GB / 多媒体约 50GB / APK 约 0.5GB → 500GB 级别绰绰有余。

**工程要点**：图片存文件夹、数据库只存路径（别把图片塞进数据库）；机械硬盘选大厂（三星 / 铠侠 / 西数）防 24 小时高频写损坏。

---

## 10. 待 itsuki 拍板（P0 阻塞项 — 实装前必决）

> **2026-04-30 進捗**：D1-D12 **全部拍板**。剩 **evidence 缺口** = 帰省 / 帰国 实物表（4 张：一般 + 留学生 各 2 张），下次见老师时 itsuki 补，内部 TODO 已记。

| ID | 决策 | 状态 | 影响范围 |
|---|---|---|---|
| **D1** | 邮件 provider | ✅ **SendGrid** | §5.6 |
| **D2** | `teachers.assigned_dorm` 编码方案 | ✅ 方案 A（`1` 暗指 1+2、业务层翻 `IN (1,2)` filter）| §4.3 / 全 dorm filter |
| **D3** | 学生能否撤回未承认的出寮届？ | ✅ 能（leave_date 前 24h 之前；后端记 `withdrawn_at`）| §5.2.4 / iOS UI |
| **D4** | **外泊届 / 帰国届 / 帰省届 承认 chain** | ✅ **实物表为准**（2026-04-30）：<br>• 外泊（一般）= **担任 + 寮務課長 + 管理係 = 3 人**<br>• 外泊（留学生）= **担任 + 国際交流部長 + 寮務課長 + 寮務部長 + 管理係 = 5 人**<br>• 帰省 / 帰国 chain = ⏳ 实物表 evidence 待 itsuki 补<br>**老师 4-29 LINE 文字推测被推翻**（漏写「担任」+「管理係」+「国際交流課長」外泊届 chain 上不出现 — 但役职作为存在、帰国届等他届で関与する可能性、ENUM 保留）| §4.5 / approval_chain 生成 |
| **D5** | 学生成功登录后 `lock_level` 清零 | ✅ 是（清 `failed_count` + `lock_level=0`）| §5.1.1 |
| **D6** | v1 部署 target | ⚠️ 2026-06-03 重开：原 ✅ VPS，现 itsuki 倾向宿舍本地自组装服务器（见 §9.1），最终形态待拍板 | §9 / §9.1 |
| **D7** | API 前缀 vs subdomain | ✅ `/api/v1/` 同 host | 全 API |
| **D8** | 高中 学習対象 reset 时点 | ✅ 学習担当手动按按钮 + 一括 add 新学期对象 | §4.6 / §5.4 |
| **D9** | 教师密码 reset 流程 | ✅ 无 self-serve、项目负责老师后台手改（明文一次性、下次登录强制改）| §5.1 |
| **D10** | 学生注册 = 即 active vs 教师承認 pending | ✅ **即 active**（无需老师审批） | §5.1 |
| **D11** | 担任 数据模型 | ✅ **单独表 `class_teacher_assignment`**（学年度更替時の audit 履歴保持 + 1 教師 → N 学年・組 対応）| §4.1 + §4.5 |
| **D12** | 管理係 役职定义 | ✅ **`teachers.role` ENUM 加单独取值 `'管理係'`** — itsuki 判断"不重要"，CC 取最简方案（跟其他役职平级、不细分子类） | §4.3 |

---

## 11. P1 / P2 / P3 — 后续会话续写

> **⚠️ 本文档 P0 完成 + itsuki 拍板 D1-D9 + code agent 起手 P0 实装** 后，下个会话续写 P1。

### P1 (next session)

- 寮監事務室 出寮者一覧 `GET /applications/active?dorm=...` (#22-#27 + R4)
- 食堂食数 `GET /applications/meals/calc?date=` + Excel 导出 (#7 / Q7)
- iOS BTR 替代 demo NFC 快捷指令 → 真路径 B 完整実装 (RollCall_Spec §5.1.2)
- ⏳ 追加 12 个的接口

### P2

- 巴士 master CRUD (#11 / §7.6)
- 行事 master CRUD (#12 / §7.5)
- 寮務部教师 学生 CRUD (#28-#29)
- 指導履歴 (#31)
- 事案录入 (#33 杭田弱点 — 名字 token tap 跳转)
- 学生個人データ aggregated (#32)

### P3

- リクエスト曲（音乐 #37）
- 罚则 自動アラート（discipline_config + cron）
- 風控（异常签到检测）
- 月次集計 / 月結処分
- 毕业交接包

---

## 12. 改订履历

| 日期 | 改订 | 担当 |
|---|---|---|
| 2026-04-30 | P0 初版 — auth + 出寮届 + 学習 + 点呼 + 邮件 + R1-R4 落地 | [Mac-轨道C] CC |
| 2026-05-27 | 5-27 醒后会话 backend 审查 9 处修复入档：(1) `deps.py` 加 `dorm_units_for_teacher` R4 helper（男寮 = unit 1+2 / 女寮 = unit 4 / 跨寮 4 类 = None）+ discipline / cleaning router 改用 `.in_(...)` 修过滤 bug。(2) `announcements.py` 补 `get_current_principal` import 修 NameError。(3) `models.py` 补 `Float` import 修 DemeritEvent NameError。(4) `schemas.py` `DemeritEventOut` 补 `revoked_by_teacher_id` 字段。(5) discipline 权限 5 类 → 4 类收窄对齐 cleaning + front_desk（`{寮監, 寮務部長, 寮務課長, 管理係}`）。(6) alembic c1d2e3f4 加 `demerit_event` + `cleaning_assignment` + `front_desk_item` 3 张表（完整 CHECK / FK / index / down_revision=b9c0d1e2f3a4）。(7) `rollcall.py` PATCH /events 实装 spec §11.4 改判扣分联动 12 类 transition（`_OVERRIDE_DEMERIT_MAP` + `_apply_override_demerit`）。(8) spec §7.5 自动扣分 3 处实装：rollcall late=1.0 / rollcall absent=2.0 / study_absent=1.5（常量 + DemeritEvent 直接 add）。(9) WebSocket `/api/v1/ws/teacher` 实装 — 新建 `ws_manager.py`（TeacherConnectionManager 单例 + asyncio.Lock + broadcast_sync）+ `routers/ws.py`（JWT query param 校验 + role check + teacher status check + WebSocketDisconnect cleanup）+ main.py 注册 + 4 处 broadcast 接入（rollcall create_checkin / rollcall PATCH override / applications create_application；_settle_absent broadcast 留 v1.1）。事件 schema: `{type:"checkin"/"override"/"outstay_new", ...}` 与 frontend `client.js LiveRollCall` 对齐。验证：uvicorn 真启动 → 49 HTTP endpoint + 1 WS endpoint 全注册 / openapi.json 通 / alembic offline SQL 通。8 commits（ddf3880..af8588c）全 local 未 push。| [MacBook-Pro-Opus 4.7 1M] CC |
| 2026-05-28 | 宿舍申请表 5-28 实物规范落库（commit `c6ccee0`，codex gpt-5.5 xhigh 实装 + CC 审查）：(1) `applications` 加 6 实物字段（contact_phone / companion / dest_cities / receipt_submitted / is_long_vacation / meal_note）+ schema / router 读写。(2) `approver_role` + `teachers.role` + `deps.CROSS_DORM_ROLES` 加「校長」（帰国届 様式3-1 最终许可、抬头校長；itsuki 拍板「实物有校长就要校长」）。(3) `approval_chain.py` 按实物校正：外泊日本人 `("寮務課長","寮務部長","管理係")` 4 人 / 帰省日本人+留学生统一 4 人 / 帰国留学生 `("国際交流部長","寮務課長","寮務部長","管理係","校長")` / `PROVISIONAL_CHAINS` 只剩 `("帰国",False)`。(4) 新表 `study_online_requests`（在线学习申请 类型 A）。(5) 新表 4 张 §8.7：`dorm_event_proposals` / `dorm_schedule_changes`（提交者 = teachers）/ `fridge_purchase_requests` / `item_possession_requests`，v1.0 单状态字段 + decided_by 模式（不建多角色链表）。(6) 新路由 `study_online.py` + `dorm_life.py` + main.py 注册。(7) alembic `d2e3f4a5b6c7`（干净空库 10 迁移全链路 upgrade/downgrade 验证通过）。(8) 附带修：历史遗留坏测试（`StudyAttendanceRoster`→`StudyRoster` 等）+ starlette 422 弃用常量 + `on_event`→`lifespan` + SQLite 时区比较 bug（`rollcall.py _as_jst_aware`）+ 旧迁移 `a8b9c0d1e2f3` 改 batch 模式（SQLite 清库升级必须）。验证：70 测试通过（CC 独立重跑）。⚠️ 留待老师确认：日本人帰国实物表是否存在（`("帰国",False)` 暂定）。| [MacBook-Pro-Opus 4.7 1M] CC + codex |
| 2026-05-31 | 修改届（PUT /applications/:id）接 iOS 真后端 + 多轮 Codex 5.5 xhigh 审查收敛（commit `5a8be64` / `0ee5546`）：(1) `ApplicationUpdateIn` 加 `amend_reason` 字段 — 修改理由写进 audit payload、**不覆盖**申请本身的 `reason`。(2) `update_application` 重建审批链后 `app.status = "pending"` 重置（修 approved_partial / returned 改完「链全 pending 但 status 没变」不一致）。(3) `returned`（老师退回）加入可编辑允许列表（spec §7.2.4-5）— ⚠️ **但 `decide_approval` 的 `_recompute_application_status` 目前无产出 `returned` 的路径**（老师「差戻」动作未实装），本次只做前向兼容、留独立 TODO。(4) 只有真改了业务字段才重置链 + 重发邮件（`changed = {k:v for k,v in update_data if getattr(app,k)!=v}`，空 body / 只填 amend_reason / 传相同值 → 422 `NO_CHANGES`，防反复无实质重置已部分承認的链 — 滥用面）；出寮日只在 `leave_date in changed` 时校验（防误拒只改帰寮 / 方法的旧届）。(5) `GET /{id}/audit` 加老师担当寮范围检查 `_teacher_can_view`（修任意老师读任意申请履历越权，越权面因 payload 新含 amend_reason 而扩大）。(6) `changed` 比较加 `_norm` datetime 归一化（请求带时区、SQLite 读回丢时区 → flight 时间同一时刻不被误判成改了；复用 rollcall `_as_jst_aware` 同款）。(7) 改了业务字段但没填修改理由 → 422 `AMEND_REASON_REQUIRED`（iOS 已强制、后端兜底）。测试 +8 `TestUpdateApplication`（no-op 422 / 传相同值 no-op 且已承认行不被清 / 没填理由 422 / audit 越权 403 / 跨寮老师可读 200 / reason 不覆盖 / 链全 pending）。5 轮 Codex 5.5 xhigh 审查（5a8be64 → 0ee5546 → 5b97b45）。验证：pytest 201 passed。| [Mac-Opus 4.8 1M] CC + codex |
| 2026-06-02 | IX-008 第二阶段（Codex 5.5 xhigh + Claude 4 维对抗审查双路独立、结论一致）后端 2 处 + IX-008b 新端点：(1) `deps.py` `get_current_student` / `get_current_teacher` 给 `UUID(payload.get("sub"))` 补 `try/except (TypeError, ValueError)` → 畸形 sub 令牌返 401 不再 500（仿 `get_current_principal` 已有范本、两依赖一致；双审同时指出的依赖一致性缺口）。(2) **IX-008b** 新 `GET /api/v1/discipline/me/summary`（`get_current_student` 鉴权）= 当前学生当月扣分汇总：`MyDisciplineSummaryOut{month, total_points, late_count, absent_count}`，与 `/ranking` 同口径（`month == 当月 YYYY-MM` + 排除 `revoked_at`）；`total_points` = 当月全来源之和、`late/absent` 只数 `rollcall_late` / `rollcall_absent`；扣分按当月算（照系统已有约定，非新拍板）。测试 +4（畸形 sub 401 / 当月限定 / 排除撤销 / 拒老师 403）。验证：pytest 217 passed。iOS 接线（DisciplineAPI + loadMe 填统计）待 iOS 文件腾出再做。⚠️ 撞并发 `git add -A`：IX-008 iOS 5 修复落 `6142ef0`、IX-008b 后端落 `0f84be9`。| [Mac-Opus 4.8 1M] CC + codex |
| 2026-06-02 | **IX-034** 学習欠席届当月计数接后端（commit `e0c150c`）：新 `GET /api/v1/study/absence-requests/me/summary`（`get_current_student` 鉴权）= 当前学生当月请假次数 `MyAbsenceSummaryOut{month, count}`。口径：按 `target_date`（请假针对日）落 JST 当月计数、数全部状态（pending/approved/rejected，学習欠席届无撤销机制 + 唯一约束每人每天最多一条）—— 与 iOS 现有「提交即 +1」行为一致。仿 IX-008b `/discipline/me/summary` 样板。测试 +3（401 / 老师 403 / 当月计数含 rejected 跨月排除）。验证：pytest 220 passed。⚠️ Codex 5.5 xhigh 审出 4 点待修（iOS 侧 submitStudyLeave 跨月仍 +1 + loadMe 令牌竞态；测试时区边界 + formatYMD 未固定 JST）—— 见交接 §7.1，过夜 GOAL 第一件事修。| [Mac-Opus 4.8 1M] CC + codex |

| 2026-06-03 | **出租车预约「タクシー予約」**：`applications` 加 `taxi_reservation_time`（`Time` / nullable，null = 不预约 / 有值 = 想坐车时刻），三种出寮届 + 外出共通。`models.py` 加列 / `schemas.py` 三处（`ApplicationBase`→三 Create 继承 + `ApplicationOut` + `ApplicationUpdateIn`）/ `routers/applications.py`（create app_kwargs 存 + `_to_application_out` 映射；PUT 修改届走 `model_dump`+`setattr` 自动）/ migration `a7b8c9d0e1f2`（down=`b2c3d4e5f6a1`；codex 审出初版编号 `e3f4a5b6c7d8` 撞既有 events 迁移、已换 + `alembic heads` 验证单 head）。自由 `Time` 字段后端不挑值。全套 223 测试绿（+2 taxi：带预约回显 / 不带默认 null）。| [Mac-Opus 4.8 1M] CC + codex |

| 2026-06-04 | **オンライン学習 契約書文件上传**：`StudyOnlineRequest` 加 4 列 `contract_file_path/file_name/mime/size`（migration `c9d0e1f2a3b4`，down=`a7b8c9d0e1f2`）。新端点 `POST /study/online-requests/{id}/contract`（上传，`get_current_student` 鉴权 — 仅本人 + 仅 pending）+ `GET .../{id}/contract`（下载 FileResponse，学生本人 OR 老师受 R4 寮边界）。文件存盘 `upload_dir/contracts/<申请id>.<ext>`，DB 只存路径/名/类型/大小，存盘名用申请 id 防路径穿越；白名单 JPEG/PNG/HEIC/PDF + 10MB 限。`StudyOnlineRequestOut` + 新 `ProfileStudyOnlineEntry` 加文件元数据（不暴露物理路径），`student_profile` 加 `study_online_requests` 子块。codex 5.5 xhigh 审出并修：列表端点 `list_online_requests` 补 R4 寮过滤（防跨寮老师从列表泄露别寮合同文件名）/ 写文件→commit→删旧文件 顺序改原子 / 文件名 `_safe_filename` 去控制字符+限长防 Content-Disposition 注入。测试 +16（含列表寮边界）。验证：pytest 64 passed（study_online 16 + study 13 + applications 20 + 既有未破坏）。⚠️ 暂存用 hunk 过滤避开并发会话的清扫/巴士改动。| [Mac-Opus 4.8] CC + codex |

| 2026-06-04 | **外出申請 単一先生確認**（itsuki 拍板「单独建表」，见 `system_features §7.2.7`）：外出是当天回寮的短时外出，不走出寮届的 7 级审批链，一名老师确认即可。**不塞进 `applications`**（那表为过夜申请设计、回寮字段必填 + 绑审批链，硬塞会污染）→ **新建 `outings` 表**（`student_id` / `outing_date` 单日期 / `destination` / `leave_time` / `return_time` / `taxi_reservation_time` / `reason` / `status` pending·approved·withdrawn / `submitted_at` / `withdrawn_at` / `confirmed_by_teacher_id` 外键→teachers / `confirmed_at`；CHECK + 2 index；migration `e1f2a3b4c5d6`，down=`c9d0e1f2a3b4`，`alembic heads` 验证单 head）。新路由 `outings.py` 6 接口：`POST /outings`（学生提出，外出日今天及以后）/ `GET /outings/mine` / `GET /outings/pending-for-me`（R4 寮过滤）/ `GET /outings/{id}`（学生本人 OR 受 R4 老师）/ `PATCH /outings/{id}/confirm`（**确认者 teacher_id 从登录令牌取、不信任客户端；R4 寮边界 + 只能确认 pending + 重复 409**）/ `PATCH /outings/{id}/withdraw`（学生撤回自己 pending）。`schemas.py` `OutingCreateIn`/`OutingOut`（`confirmed_by_name` 回显确认老师姓名给学生看「確認 · ○○ 先生」）。`main.py` 注册。⚠️ 踩 ruff 坑：先加 import 后加用法被 ruff 当无用导入删，同次补回。测试 +14（提出 / 过去日 422 / 出租车 / 列表 / 待确认 / 详情 / 确认记录令牌身份 / 学生不能确认 403 / 重复 409 / 别寮老师 403 / 撤回 / 已确认不能撤回）。验证：全套 pytest **253 passed**。⏳ iOS 生产版 + 老师网页确认按钮待接。| [Mac-Opus 4.8 1M] CC |

| 2026-06-04~05 | **杭田需求 第一批实装**（无人值守 GOAL 会话，逐条审查后端 + 实装）：(A) `decide_approval` 审批终态（approved/rejected）给提出者本人发邮件 — `email.py` 加 `render/send_application_decided`（template_key=`application_decided`），符合杭田訂正「通知用メール不用 push、提出が残るため」；§3.2 通知矩阵同步（役职承认/拒否→学生 push→邮件）。(B) **出寮者一覧**新只读端点 `GET /applications/active`（事務室 PC 用）— 只返 status=approved 且 leave_date<=指定日<=return_date 的届，R4 寮边界过滤，前端分 1,2寮/4寮；静态路由置于 `/{id}` 前防 UUID 误解析；无编辑端点（防误删）。(H) **代録**新端点 `POST /applications/by-teacher?student_id=`（老师代学生补录帰省/外泊/帰国届）— 限 `_DAIROKU_ROLES` 5 角色 + R4 寮边界 + 放宽到当日（学生侧禁当日）+ 复用学生侧 discriminated union schema（字段全）。(I) `student_profile` 点呼履历 join `RollCallSession` 取 `session_type`，`ProfileRollCallEntry` 加 `session_type` → 前端分朝/夜两份（五-5）。(J) `IncidentRecordOut` 加 `involved_students`（join Student 取 id+name）+ `_to_incident_out` helper，前端事案涉及学生姓名可点跳个人档案（五-6）。(K) `rollcall` `session_board` 预查当日 approved 出寮願 → 无 event 的这些学生 live 板直接标 `exempt_range`（口径同 `_settle_absent`），寮監一眼可见不必等结算（三-3/5）。无新建表 / 无 migration（全是查询 + 既有字段）。测试 +9（应批结果邮件 3 + 出寮者一覧 5 + profile session_type 1 + 事案姓名 1 + 点呼预标 1）。各模块单测绿（applications 28 / profile 20 / incidents 24 / rollcall 16）。iOS 侧 (C) 行事予定 `GET /events` 接真后端（见 IOS_DESIGN_LOG）。⚠️ 与并发会话共用工作区，提交全用显式 pathspec、不 `git add -A`。| [Mac-Opus 4.8 1M] CC |
| 2026-06-05 | **代録 学生选择器后端 + 老师网页表单接上**（杭田五-3「教師用は当日入力可」收尾）：(H 续) 新端点 `GET /applications/proxy-candidates?q=` — 代録表单的学生选择器数据源。**刻意不复用 admin 的 `GET /students`**：那个只给 `ADMIN_ROLES` 3 角色（寮務部長/課長/管理係）还暴露账号锁定信息，而代録允许 5 角色（`_DAIROKU_ROLES`，多寮監+寮務一般教師）→ 权限边界不一致，寮監/一般教師 能代録却拉不到学生。新接口权限对齐代録 5 角色 + R4 寮边界（只搜本人管辖寮）+ 复用 `StudentBrief`（精简字段 学号/姓名/寮/是否留学生/房间，不含管理信息）+ `q` 姓名or学号模糊 + 排 demo + limit 100。无新建 schema / 无 migration。测试 +8（寮務課長列表 / 姓名搜 / 学号搜 / 寮務一般教師可用即权限对齐 / 非寮務系 403 / 学生 token 拒 / 4寮老师搜不到1寮学生 / demo 排除）。验证：applications 模块 36 passed（28+8）。前端 `client.js` 加 `proxyCandidates`+`createByTeacher`，`index.html` 新 `ProxyApplicationPage`（见 WEB_DESIGN_LOG）。| [Mac-Opus 4.8 1M] CC |
| 2026-06-05 | **学年更新 / 学生自设番号**（itsuki 推翻 4-30 老师代改 → 学生自设，spec §4.2）：`students` 加 `needs_renewal` 标记列（migration `b2c3d4e5f6a7`，down=`e1f2a3b4c5d6`，`alembic heads` 单 head）。旧 `bulk-promote` 改造成开闸 `POST /students/renewal-start`（中1~高2 打 `needs_renewal` + 高3 `status=graduated`，dry_run 预览，排除 is_demo）。新 `POST /students/me/renew-number`（学生自设，**身份从 `get_current_student` 令牌取、不信客户端 student_id**；应用层查重 + 并发 `uq_students_no` IntegrityError 兜底，都返 422 STUDENT_NO_TAKEN）/ `GET /students/renewal-progress`（老师看 needs_renewal=true 名单）/ `POST /accounts/{id}/renew-seat`（老师单件改兜底，同款查重）。`StudentAccountListItem`/`StudentProfileBasic` 加 `grade_code/class_code/seat_no/needs_renewal`。测试 TestBulkPromote→TestRenewalStart 重写 + 新增 自设/进度/单件改 + 安全（撞号 422 / 越权 403 / 身份从令牌不信 body student_id）共 16 测试，305 passed。**codex gpt-5.5 xhigh 复审挑出 4 major：renewal-start/progress/renew-seat 漏 R4 寮过滤 + 学生自设漏 `needs_renewal` 开闸检查**。CC 先核实 codex 前提（怀疑 ADMIN_ROLES 全跨寮 → 查 `deps.py` 证实「管理係」**不在** `CROSS_DORM_ROLES`，分寮管理係确实受限）→ codex 正确，全采纳：3 接口加 `dorm_units_for_teacher` 过滤 + 自设加 `needs_renewal=False → 409` + 补 3 测试（未开闸 409 / 分寮管理係改别寮 403 / 进度排除别寮）。全套 **308 passed**。⏳ Android 端待别会话对齐。| [Mac-Opus 4.8 1M] CC + codex |
| 2026-06-13 | **启动自检 schema 落后**（`_warn_if_db_schema_outdated`，commit `caef3ba`）：`main.py` lifespan 在 dev `create_all()` 之后调用 — 比对库当前 alembic 版本 vs `ScriptDirectory.get_heads()`，落后则 `logger.warning` 醒目提示（含 upgrade 命令）。`current=None`（全新 create_all 库）静默不误报。背景：6-13 `GET /teachers/public` 500，根因是本地 dev 库缺 6-12 加的 `teachers.permission_group` 列（alembic 迁移 `f1a2b3c4d5e6` 未跑）。pytest 371 passed 全程保持。| [Mac-Opus 4.8 1M] CC |

---

**END** — code agent 接手时先读 §1-§3 + §10，决策点先和 itsuki 确认完再动手。
