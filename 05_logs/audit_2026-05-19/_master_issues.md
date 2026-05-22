# DMSD 审查作战 — 总问题清单

> **生成于**：2026-05-20 ~01:30 日本时间（cron 自动 fire / 主会话汇总）
> **来源**：3 子代理并行审 15+ 维度
> **状态**：✅ 审查完成（未修任何文件，等 itsuki 拍板每条修不修）

---

## 📊 数据总览

| 子代理 | 维度 | 🔴 | 🟡 | 🟢 | 总 |
|---|---|---|---|---|---|
| A | 1-5 跨端 / 联动 / 设计 / scaffold / NFC 安全 | 13 | 22 | 5 | 40 |
| B | 6-10 规格 / 硬件 / memory / 挂钩 / TODO | 11 | 17 | 13 | 41 |
| C | 11-17 AC / commit / 测试 / 跨项目 / 精读 | 19 | 19 | 12 | 50 |
| **合计** | **15+ 维度** | **43** | **58** | **30** | **131** |

---

## 🚨 TOP 10 必修（v1.0 上线前 — 按风险 + 修法成本）

### 1. 🔴🔴🔴 teacher_web 老师密码全员明文 — public GitHub repo 已暴露

- **报告**：A-039 + A-032
- **文件**：`03_dev/teacher_web/v1/src/index.html:4262` `window.SHARED_PASSWORD='12345678'` + `:4297` `window.ACCOUNTS = [24 人明文]` + `:4393` 登录页显示密码 + `:4772` `DEMO` badge
- **现状**：本应该是 vite 入口 shell（< 50 行），实际填了 7774 行老 demo HTML
- **影响**：public repo 暴露所有老师账户明文（最紧急）
- **修法**：紧急清掉 7700 行老 demo，回归 vite minimal shell

### 2. 🔴 CLAUDE.md 路径用户名错位 — 每次会话都受影响

- **报告**：B-013 + C-001（2 子代理独立发现）
- **文件**：`CLAUDE.md:205` 写 `~/.claude/projects/-Users-itsuki-dev-DMSD/`
- **应该**：`-Users-kurekoduki-dev-DMSD/`
- **影响**：CC 每次会话启动按这路径找 memory 都 404
- **修法**：一行替换 `itsuki` → `kurekoduki`

### 3. 🔴 backend NFC 防代刷一行未实装 — v1.0 上线最大隐患

- **报告**：A-010 + A-028
- **文件**：`02_design/flow_design.md:63-115`（spec 写了 ECDSA + 10 秒 nonce）vs `03_dev/backend/v1/app/routers/rollcall.py:127`（完全没实装）
- **现状**：backend 没 nonce 表 / 没 Device 表 / 没 NFCCard 表 / `POST /api/v1/nonce` endpoint 不存在 / `RollCallCheckinIn` schema 没 signature 字段
- **影响**：v1.0 NFC 真实卡上线 = 所有 checkin 走无验证路径 = 任何人能伪造 checkin
- **修法**：二选一 —— (a) 完整实装 ECDSA + nonce + 3 张表（Device / Nonce / NFCCard） / (b) spec 砍降级到 v1.1

### 4. 🔴 backend auth 5 处漏洞集中爆发

- **报告**：A-001 至 A-005
- **文件**：`03_dev/backend/v1/app/config.py:29-30` + `app/routers/auth.py:32-44`
- **5 条**：
  - JWT 密钥默认值 `change-me-in-production` 无 fail-fast（ops 漏配 .env 直接玩完）
  - HS256 对称密钥（点呼机被盗 = 整套垮）
  - NFC checkin 无签名 / nonce 验证
  - 学生 login 用学号 + 密码（学号公开 = 蛮力破解可行）
  - 失败计数器 `failed_count` 不递增（brute force 0 代价）
- **修法**：v1.0 上线前必修，详见 session_A_findings.md A-001~A-005

### 5. 🔴 README + progress_overview + 状态文档严重过期 — 招生官读出洋相

- **报告**：C-003 至 C-009 + C-022
- **文件**：`README.md:23-37` 写「截至 2026-04-29（v0.5.0）/ 后端 — 还没开始」+ `progress_overview.md` 仓库结构图 + 系统架构图含「Phase 2 追加」自相矛盾
- **实际**：5-19 已 v0.8.0 + backend 1134 行 + 三端代码层启动 + 5-08 硬件全定稿
- **影响**：public GitHub repo 首屏招生官读 = 项目静止 17 天的假象（AC 出愿期 8-9 月）
- **修法**：README + progress_overview + system_features 顶部时间戳 + 状态段一次刷新

### 6. 🔴 Phase 1/2 模型 + effective_* 概念在 spec 多处过期 — 3 子代理共同发现

- **报告**：B-027 + B-028 + C-010 + C-011 + C-012
- **文件**：`01_specs/rollcall/RollCall_Spec.md:17-18, 26, 182, 233, 460, 466, 586` + `system_features.md:47-75` + 5 端 `*_DESIGN_LOG.md` 多处
- **现状**：4-19 G2 决策取消分阶段 / 4-29 拍板不平移 / 5-06 退役独立 repo 仍未传播到 spec + design log
- **影响**：5 端实装的对齐基准跟最高决策矛盾
- **修法**：spec 主体 + 5 端 DESIGN_LOG + system_features 一次性刷新

### 7. 🔴 Android 完全没接通 backend — 100% 脱节

- **报告**：A-016 + A-024
- **文件**：`03_dev/student_android/v1/app/build.gradle.kts`（没 Retrofit / OkHttp / Ktor 任何 HTTP client）+ `data/model/Models.kt`（mock 字段 camelCase）
- **影响**：你可能误以为 Android 已经接通，**实际不是**
- **修法**：v1.0 上线前加 Ktor / Retrofit + 拆 `domain/`（业务模型）+ `api/dto/`（snake_case DTO）+ 真接 backend endpoint

### 8. 🔴 decision_log + project_evolution 严重过时 — AC 面试用直接出洋相

- **报告**：C-028 + C-029
- **文件**：`05_logs/decision_log.md` 停 2026-04-15 / `project_evolution.md` 停 2026-04-13
- **缺**：4-19 G2 / 4-21 Tomoshibi 命名 + Pi 3A+ / 4-29 38 条规则 / 4-29 管理员同意 / 5-02 三端启动 / 5-08 硬件定稿 / 5-11 沟通规则 / 5-19 防漂 C 方案 等 15+ 条
- **影响**：AC 面试招生官读决策脉络 = 4-15 之后全黑
- **修法**：itsuki 自己补 15+ 条决策（CC 起草 draft 等粘贴 — 不直写）

### 9. 🔴 memory feedback 2 个文件死链 + `bin/check_overview_drift.sh` awk bug

- **报告**：B-011 + B-012 + C-002（死链）+ B-021（awk bug）
- **死链 1**：`CLAUDE.md:63` 引用 `feedback_design_doc_layers.md`（不存在）
- **死链 2**：`CLAUDE.md:69` 引用 `feedback_code_comments_chinese_strict.md`（不存在）
- **awk bug**：`bin/check_overview_drift.sh:46-54` awk 正则匹配过宽，抓 §1.8.1（23 行表格）而非 §0.1（体量表 9）→ 每次会话启动报伪差异
- **修法**：补 2 个 memory + 改 awk 正则限定 §0.1 上下文

### 10. 🔴 CI 缺位 + 核心业务无测试

- **报告**：C-048 + C-050
- **文件**：`.github/workflows/` 不存在 / `03_dev/backend/v1/tests/` 只有 smoke + registration + announcements + demo_reviewer（37 case）
- **缺**：rollcall / study / applications / teachers / auth 核心业务**无专用测试文件**
- **修法**：补 test_rollcall.py / test_study.py / test_applications.py 各 ~150-200 行 + 加 `.github/workflows/test.yml` 跑 pytest

---

## 🔗 跨子代理高置信项（多个独立发现 = 高可信）

| 主题 | A | B | C | 置信度 |
|---|---|---|---|---|
| CLAUDE.md 路径漂 | — | B-013 | C-001 | 高（2 独立发现）|
| memory feedback 死链 | — | B-011/B-012 | C-002 | 高 |
| Phase 1/2 过期 | — | B-027/B-028 | C-010 | 高（跨 5+ 文件）|
| 5-06 独立 repo 退役未传播 | — | — | C-011/C-012 | C 独家但跨 3 文件 |
| 跨项目 DMSD 残留 | — | — | C-035/036/037 | C 独家，共 63 处 |
| Phase 1/2 多文件 | — | B-027/028 | C-010/011/012/013 | 高 |

---

## 📋 完整 🔴 阻塞清单（按子代理）

### A 子代理 🔴（13 条）

A-001~005 backend auth 5 处漏洞 / A-010 ECDSA spec vs 实装 / A-015 iOS 没 RollCallAPI / A-016 Android 没接通 backend / A-027 ROLLCALL_DEVICE 设计 vs 空 src / A-033 iOS demo long-press / A-034 Android demo cycle / A-035 iOS Auth magic 000000 / A-039 teacher_web 7700 行 demo + 密码明文

### B 子代理 🔴（11 条）

B-001 TODO Cloud Design 已过期 / B-002 TODO §G / §F 编号重复 / B-004 TODO Demo 4-28 段已过期 / B-005 TODO 硬件已拍板但标未决 / B-011/012 CLAUDE.md memory 死链 / B-013 CLAUDE.md 路径漂 / B-021 check_overview_drift awk bug / B-027/028 spec Phase 1/2 + effective_* 过期

### C 子代理 🔴（19 条）

C-001/002 memory 路径错 + 死链 / C-003~009 README + progress_overview 全面过期（7 条）/ C-010 RollCall_Spec Phase 1/2 / C-011 system_features 独立 repo / C-012 ANDROID/IOS DESIGN_LOG 独立 repo / C-013 flow_design Pi 4B 错（实际 Pi 3A+）/ C-016 文件结构指南死链 4 处 / C-028/029 AC 时间线停滞 / C-036/037 跨项目残留 / C-048 没 CI

---

## 🟡 🟢 完整清单

详见各子代理 findings 文件（同目录）：

- `session_A_findings.md` — 22 🟡 + 5 🟢
- `session_B_findings.md` — 17 🟡 + 13 🟢
- `session_C_findings.md` — 19 🟡 + 12 🟢

---

## 📌 备注

- 总数 131 条不代表 131 个独立 bug — 部分跨子代理重复（约 8-10 条重叠）
- 严重程度依子代理自评，最终修复优先级由 itsuki 拍板
- 子代理报告里有完整 `file:line` + 建议改法 + 跨会话引用
- 本会话执行约束：**等 itsuki 拍板每条修不修**，不擅自动手

## ⏭️ 等 itsuki 拍板

- TOP 10 哪几个立刻修？我（主会话）来动手
- 剩余 121 条要不要分批过？还是只过 🔴 43 条？
- 修复完是不是一起 commit / 分多 commit / 不 commit 等下次会话？
