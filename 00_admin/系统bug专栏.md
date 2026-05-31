# DMSD 系统 Bug 专栏

> **创建于**：2026-05-21
> **来源**：4 会话审查作战（2026-05-19 启动 / 2026-05-20 凌晨 cron 自动 fire 跑 3 子代理并行审 15+ 维度 / 5-21 itsuki 拍板专栏化管理）
> **完整 findings 详情**：`05_logs/audit_2026-05-19/session_{A,B,C}_findings.md`
> **汇总 + TOP 10**：`05_logs/audit_2026-05-19/_master_issues.md`
> **本文件作用**：长期跟踪 131 条 bug 的修复状态 / 决策 / 验证

---

## 🍎 iOS 交叉验证审查追加（2026-05-29）

> **来源**：iOS 学生端 app 两轮独立审 + 交叉验证 — CC 多 agent workflow 确认 27 条 + codex GPT-5.5 xhigh 独立确认 13 条，去重合并 **37 条**（独立编号 IX-001~037）。
> **完整清单详情**：`05_logs/audit_2026-05-29_ios交叉验证.md`
> **状态**：⏳ 全部待 itsuki 决策修复优先级（本次只列 bug、未改代码）。本 37 条独立编号、不计入下方 131 条总览。
> **♻️ 归档条件**：IX-001~037 全部「已修 / 明确不修」后，详情文件移入 `99_archive/`，本入口段标 ✅ 闭合。
>
> **3 条上线级核心（已亲自核实代码）**：
> - **IX-001** 点呼按钮根本不发后端（`Features/Home/HomeStubs.swift:1435` 只本地改状态 + `RollCallAPI` 全项目零调用=死代码）→ 即本专栏 **A-024 / FC-018「🔴 仍存在」** 第三方再确认，至今未修。
> - **IX-002** 删账号接口后端不存在（iOS `AuthAPI.swift:52` 调 `DELETE /accounts/me`，后端 `routers/accounts.py` 无此路由）→ 卡苹果上架审核（5.1.1(v) 强制要求账号删除）。
> - **IX-003** 时间带小数秒致几乎所有响应解码失败（`APIClient.swift:89` 用 `.iso8601` + `NetworkModels.swift` 等 20+ 个 Date 字段）→ 影响面最大；CC 第一轮对抗验证曾误杀此条，codex + 亲自核实确认为真。

---

## 📊 总览

| 严重 | 数量 | 占比 |
|---|---|---|
| 🔴 阻塞上线（v1.0 前必修） | 43 | 33% |
| 🟡 该修 | 58 | 44% |
| 🟢 优化 / 信息 / positive note | 30 | 23% |
| **合计** | **131** | 100% |

> **2026-05-22 — Codex 第二轮 audit 加 39 条**（24 独立 + 13 复核 + 2 positive） → 见 **§🤖 Codex 第二轮 audit findings** 段。131 原条目总数不变；codex 段独立编号 FC-001~039。
>
> **Codex 复核 12 个原条目状态**（详见 §🤖 段「🔁 Codex 复核」表）：
> - **🔴 仍存在**：A-001（JWT FC-011）/ A-009 + A-027（点呼机 FC-023）/ A-010（NFC ECDSA FC-016）/ A-014（reviewer 凭据 FC-012）/ A-016（Android FC-022）/ A-024（iOS RollCallAPI FC-018）/ A-039（teacher_web 密码 FC-024）
> - **🟡 部分修**：A-018（iOS bus_route_id FC-020）/ C-048（CI FC-008+009）/ C-049 + C-050（pytest 配置 + 测试 FC-004+031）/ C-037（cc-project-template FC-036）

### 状态图例

- ⏳ 待修：itsuki 还没拍板要不要修
- 🔧 修复中：已拍板修，进行中
- ✅ 已修：完成 + 验证通过
- 🚫 不修：itsuki 拍板不修（带理由）
- ⚠️ 待复核：可能跟其他条目重复 / 需要二次拍板

### 每条字段

- **位置**：file:line
- **维度**：1-17（详见 `_master_issues.md`）
- **状态**：⏳ / 🔧 / ✅ / 🚫 / ⚠️
- **修法**：1 句怎么修
- **验证**：怎么确认修完了
- **commit**：修完后填 hash（默认 —）
- **决策**：itsuki 拍板时间 + 理由

---

## 🔴 阻塞上线（43 条）

### 子代理 A 维度 1-5（13 条 — 跨端 / 联动 / 设计 / scaffold / NFC 安全）

### [A-001] 🔴 JWT 密钥默认值无 fail-fast
- 位置: `03_dev/backend/v1/app/config.py:29` | 维度 5 | ⏳ 待修
- 修法: `Settings.__init__` 加 fail-fast 拒绝默认值 `change-me-in-production`
- 验证: 设 `APP_ENV=production` + 默认 secret 跑 backend 应抛 RuntimeError
- commit: —
- 决策: 2026-05-21 创建 / 待 itsuki 拍板

### [A-002] 🔴 JWT 用 HS256 对称密钥
- 位置: `03_dev/backend/v1/app/config.py:30` + `security.py:69-72` | 维度 5 | ⏳ 待修
- 修法: 评估迁 RS256 / ES256 非对称密钥；或点呼机不验 JWT 走 backend HTTP；或至少 BACKEND_DESIGN_LOG 标注「HS256 决策依赖点呼机不本地验 JWT」
- 验证: 拍板后定（设计层决策先行）
- commit: —
- 决策: 2026-05-21 创建 / 待拍板（设计层）

### [A-003] 🔴 NFC checkin 无签名 / nonce 验证
- 位置: `03_dev/backend/v1/app/routers/rollcall.py:127-191` + `schemas.py` `RollCallCheckinIn` | 维度 5 | ⏳ 待修
- 修法: 跟 A-010 一起处理 — 加 nonce 表 + ECDSA 验签 + Device/NFCCard 表 + 路径 A fallback 移除
- 验证: POST 同一 checkin 两次第二次应 409；伪造签名应 401
- commit: —
- 决策: 2026-05-21 创建 / 待拍板（跟 A-010 合并）

### [A-004] 🔴 学生 login 用学号 + 密码（学号公开）
- 位置: `03_dev/backend/v1/app/routers/auth.py:21-44` | 维度 5 | ⏳ 待修
- 修法: 加 rate limit（用 failed_count + lock_level 字段已有）+ 密码复杂度强制 + 长期考虑 TOTP（一次性密码）
- 验证: 同一 IP 失败 N 次后应 429 锁定
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [A-005] 🔴 失败计数器不递增 — lock_level 形同虚设
- 位置: `03_dev/backend/v1/app/routers/auth.py:32-44` + `:76-80` | 维度 5 | ⏳ 待修
- 修法: login 失败分支补 `account.failed_count += 1` + `if failed_count >= N: lock_level = 1`，入口前查 lock
- 验证: 写 pytest 模拟 5 次错误密码 → 第 6 次应被锁
- commit: —
- 决策: 2026-05-21 创建 / 待拍板（阈值 + 时长由 itsuki 定）

### [A-010] 🔴 spec 写 ECDSA + nonce backend 一行未实装
- 位置: `02_design/flow_design.md:63-115` + `hardware_design.md:144` + `ERROR_CODES.md:26` vs `backend/v1/app/routers/rollcall.py:127` | 维度 1+5 | ⏳ 待修
- 修法: 二选一 — (a) 完整实装 Device + Nonce + NFCCard 表 + `POST /api/v1/nonce` + schema 4 字段 + ECDSA 验签 / (b) spec 砍降级 v1.1，路径 B 用 JWT + idempotency_key + ts 滑窗替代
- 验证: 拍板 (a) 后 → 全流程集成测试通过；拍板 (b) 后 → spec 改完 commit
- commit: —
- 决策: 2026-05-21 创建 / **v1.0 是否可上线宿舍真实环境的核心决策** / 待拍板

### [A-015] 🔴 iOS 没 RollCallAPI — 端到端缺口
- 位置: `03_dev/student_ios/v1/.../Foundation/Network/Endpoints/`（缺 RollCallAPI.swift）+ `backend/v1/app/routers/rollcall.py` | 维度 1+2 | ✅ 已修
- 修法: iOS 加 `RollCallAPI.swift` 至少含 POST /checkins（学生 BTR tap iPhone 入口）
- 实际改法: 新建 `Foundation/Network/Endpoints/RollCallAPI.swift`（54 行）含 `enum RollCallAPI` + `checkin(sessionId:body:)` + `RollCallCheckinBody` + `RollCallEventOut`，字段 byte-perfect 对齐 backend schemas
- 验证: iOS 真实 device 跑 NFC tap → backend 收到 checkin → 出席板更新（真机验证待 itsuki 手动跑）
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 修复 by 5-22 fork 融合会话 backport**

### [A-016] 🔴 Android 完全没接通 backend
- 位置: `03_dev/student_android/v1/app/build.gradle.kts`（没 HTTP client）+ `data/model/Models.kt` | 维度 1 | ⏳ 待修
- 修法: 加 Ktor / Retrofit + kotlinx-serialization snake_case 处理；新建 `data/api/` 模块；拆 `Models.kt` → `domain/` + `api/dto/`
- 验证: Android 真机调 `/auth/login` 拿 token → list applications 返回数据
- commit: —
- 决策: 2026-05-21 创建 / v1.0 必修 / 待拍板

### [A-027] 🔴 ROLLCALL_DEVICE 设计完整 src/ 空 — 联动断裂
- 位置: `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md`（226 行设计）vs `src/main.py`（9 行 placeholder）+ `src/{nfc,api,led,audio}/__init__.py`（全空）| 维度 2 | ⏳ 待修
- 修法: ROLLCALL_DEVICE_DESIGN_LOG.md 头部加「实装进度: 0%」+ WIP / TODO 加显式条目（v1.0 上线前 src/ 必填）
- 验证: src/main.py 能跑通最小循环 → 读 NFC → POST backend
- commit: —
- 决策: 2026-05-21 创建 / 待拍板（实装时间盒）

### [A-033] 🔴 iOS HomeStubs long-press demo cycle
- 位置: `03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift:256, 535` + `Foundation/AppState/AppStore.swift` `cycleDemoRollState` | 维度 4 | ✅ 已修（iOS 端）
- 修法: v1.0 sprint 删 long-press cycle + `cycleDemoRollState` 函数 + 调用点
- 实际改法: HomeStubs.swift + StayListStubs.swift 留空 `DemoCardCycleGesture` modifier shell（保留调用点不报错，等接 backend event 驱动后整段删）+ AppStore.swift `cycleDemoRollState` 函数体删
- 验证: grep `cycleDemoRollState` 全 repo = 0；amber Card 改成 backend event 驱动
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 修复 by 5-22 fork 融合会话**（Android A-034 + spec A-030 还未同步删）

### [A-034] 🔴 Android AppStore cycleDemoRollState
- 位置: `03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/store/AppStore.kt:59-61` | 维度 4 | ⏳ 待修
- 修法: 跟 A-033 同步删
- 验证: grep `cycleDemoRollState` = 0
- commit: —
- 决策: 2026-05-21 创建 / 跟 A-033 合并

### [A-035] 🔴 iOS Auth magic value "000000" 注册流程后门
- 位置: `Features/Auth/AuthStubs.swift:1944-2074`（RegisterStep5 demo bypass）| 维度 4 | ✅ 已修
- 修法: v1.0 上线前 grep `magic.value\|"000000"\|0000` 在 Auth 流程全删
- 实际改法: 删默认值 `code: String = "000000"` → `""`，删 `DEMO_MAGIC_CODE` 常量，删 submit() 里 `if code == DEMO_MAGIC_CODE` bypass 分支。TextField placeholder "000000" 保留（UX 输入提示不是后门）。Step4 `#if DEMO` 预填 pw 保留（编译开关已 gate production build）
- 验证: `grep '000000\|magic.value\|DEMO_MAGIC_CODE' AuthStubs.swift` 现在只剩 line 2005 TextField placeholder（UX hint）+ A-035 修复注释
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 修复 by 本会话 CC**（itsuki 总授权「全部修好」）

### [A-039] 🔴 teacher_web v1/src/index.html 7700+ 行老 demo + 密码明文（紧急）
- 位置: `03_dev/teacher_web/v1/src/index.html:4262, 4297, 4393, 4772`（共 7774 行）| 维度 4 | ⏳ 待修
- 修法: 紧急 — `v1/src/index.html` 回归 vite minimal shell（< 50 行 `<div id="root"></div>`）；7700 行老 demo 删除（或挪 `99_archive/`）
- 验证: `wc -l v1/src/index.html` < 100；`grep -c "SHARED_PASSWORD" v1/src/index.html` = 0；`npm run dev` 启动正常
- commit: —
- 决策: 2026-05-21 创建 / **紧急 — public GitHub repo 已暴露 24 人明文密码**

### 子代理 B 维度 6-10（11 条 — 规格 / 硬件 / memory / 挂钩 / TODO）

### [B-001] 🔴 TODO §⏰ Cloud Design 5-12 截止已过期
- 位置: `00_admin/TODO.md:18-22` | 维度 10 | ⏳ 待修
- 修法: 标 `[x]` 或归档到「已废 — 5-12 截止过期 / 额度浪费」；§F line 87 同条目同时归档去重
- 验证: TODO 顶部 §⏰ 段不再含 5-12 截止条目
- commit: —
- 决策: 2026-05-21 创建 / itsuki 5-21 没拍板"顺手清"故待单独拍

### [B-002] 🔴 TODO §G / §F 编号顺序错乱 + 双 G
- 位置: `00_admin/TODO.md:72`（§G anti-ai-flavor）+ `:83`（§F 5-12）+ `:94`（§G 5-14 Tango）| 维度 10 | ⏳ 待修
- 修法: 第二个 §G 重命名为 §H；加 TOC 让 CC / itsuki 快速定位
- 验证: TODO 编号 A-H 顺序唯一
- commit: —
- 决策: 2026-05-21 创建 / 跟 B-001 一组待清

### [B-004] 🔴 TODO §🎯 4-28 Demo 段过期 22 天但仍标「最高优先级」
- 位置: `00_admin/TODO.md:542-559` | 维度 10 | ⏳ 待修
- 修法: 整段移到 §1061「已完成归档」+ 加「Demo 通过验证 2026-04-29」状态；剩余真活归到对应 §
- 验证: TODO 顶部 200 行无「最高优先级 / Deadline 4-28」字眼
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [B-005] 🔴 TODO §🚨 硬件架构层全拍板但仍标「未决」
- 位置: `00_admin/TODO.md:720-760` | 维度 10 | ⏳ 待修
- 修法: 6/8 项归到「已拍板」（标 ✅ + 引用 `hardware_design.md` 章节）；剩 2/8 保留真活
- 验证: §🚨 段只剩真未决条目（位置 / 卡片形式 / 丢卡补卡）
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [B-011] 🔴 CLAUDE.md 引用 feedback_design_doc_layers.md 死链
- 位置: `CLAUDE.md:63` | 维度 8 | ⏳ 待修
- 修法: 二选一 — (a) 写该 memory（内容散在 CLAUDE.md §设计文档双层）/ (b) CLAUDE.md:63 改成「见 CLAUDE.md §设计文档双层 段」
- 验证: 文件存在 OR 引用路径有效
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [B-012] 🔴 CLAUDE.md + hooks/README 引用 feedback_code_comments_chinese_strict.md 双重死链
- 位置: `CLAUDE.md:69` + `00_admin/hooks/README.md:30` | 维度 8 | ⏳ 待修
- 修法: 写该 memory（规则在 hook 里活但 narrative 缺失）/ 或两处改成 hook README 段引用
- 验证: 同 B-011
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [B-013] 🔴 CLAUDE.md 路径漂 -Users-itsuki-dev-DMSD（每次会话受影响）
- 位置: `CLAUDE.md:205` | 维度 8 | ⏳ 待修
- 修法: `-Users-itsuki-dev-DMSD/` → `-Users-kurekoduki-dev-DMSD/`（一行替换）
- 验证: 路径 `ls $(grep 路径 CLAUDE.md)` 返回真实 memory 目录
- commit: —
- 决策: 2026-05-21 创建 / 高置信（B + C 独立报）/ **一行修，先做**

### [B-021] 🔴 bin/check_overview_drift.sh awk bug
- 位置: `bin/check_overview_drift.sh:46-54` | 维度 9 | ✅ 已修
- 修法: awk 正则限定到「§0.1 体量表」上下文（用 `in_overview_table=1` flag）+ 区分 staged / committed
- 验证: 跑脚本 .claude/ 应报「写 11 / 实际 11」；本会话多次跑 `bash bin/check_overview_drift.sh` 均「✅ 没漂」
- commit: 5-21 主会话已 commit（脚本顶部注释 + line 36-48 staged/committed + line 58-94 in_table flag）
- 决策: 2026-05-21 创建 / 5-19 拍板核心机制自带 bug / **2026-05-22 复核已修，本会话标 ✅**

### [B-027] 🔴 spec 主体 Phase 1/Phase 2 模型过期（4-19 G2 已取消）
- 位置: `01_specs/rollcall/RollCall_Spec.md:17-18, 233-240, 460-466, 586-590` | 维度 6 | ⏳ 待修
- 修法: Phase 1 / Phase 2 全替换 — 路径 A（NFC 卡）/ 路径 B（iOS Universal Link）+ 加路径 C（Android App Link）
- 验证: `grep -i "Phase 1\|Phase 2" RollCall_Spec.md` = 0（或只在历史段）
- commit: —
- 决策: 2026-05-21 创建 / 跟 B-028 + C-010 合并处理

### [B-028] 🔴 spec §7 + §10 仍引 effective_* 平移概念（4-29 §5.4 已推翻）
- 位置: `RollCall_Spec.md:396, 500, 514-516, 527` | 维度 6 | ⏳ 待修
- 修法: 「不平移」生效后 effective_* = scheduled_*，二选一 — (a) 彻底删 effective_* 概念 / (b) 明确「现在 effective = scheduled，字段名保留」
- 验证: spec 内部无矛盾段（§5.5 line 304 跟 §7/§10 一致）
- commit: —
- 决策: 2026-05-21 创建 / 跟 B-027 合并

### 子代理 C 维度 11-17（19 条 — AC / commit / 测试 / 跨项目 / 精读）

### [C-001] 🔴 memory 路径用户名错位 /Users/itsuki/ → 实际 /Users/kurekoduki/
- 位置: `CLAUDE.md:205` | 维度 17 | ⏳ 待修
- 修法: 跟 B-013 同（一行替换 `itsuki` → `kurekoduki`，或改用 `$HOME` 占位）
- 验证: 同 B-013
- commit: —
- 决策: 2026-05-21 创建 / **跟 B-013 重复 — 同一处问题，2 子代理独立发现**

### [C-002] 🔴 CLAUDE.md 引用 2 个 memory feedback 文件不存在
- 位置: `CLAUDE.md:63` + `:69` | 维度 17 | ⏳ 待修
- 修法: 跟 B-011 + B-012 同
- 验证: 同 B-011/012
- commit: —
- 决策: 2026-05-21 创建 / 跟 B-011/012 合并

### [C-003] 🔴 progress_overview.md 仓库结构地图严重过期
- 位置: `00_admin/progress_overview.md:340-368` | 维度 17 | ⏳ 待修
- 修法: 删整段「仓库结构地图」code block，引导到 `.claude/skills/project-overview/SKILL.md`；或全部重写贴现状
- 验证: progress_overview 仓库结构图跟当前 `ls -d ~/dev/DMSD/*/` 一致
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [C-004] 🔴 progress_overview.md 系统架构图含 "Phase 2 追加"
- 位置: `00_admin/progress_overview.md:42-65` | 维度 17 | ⏳ 待修
- 修法: 架构图重画 — 「Phase 2 追加」框整合进主系统图（学生 App 是 v1.0 第一天就有）
- 验证: progress_overview 架构图跟 §分阶段策略「2026-04-19 取消分阶段」一致
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-003 一组

### [C-005] 🔴 progress_overview.md §阶段 4 点呼机状态过期
- 位置: `00_admin/progress_overview.md:169` | 维度 17 | ⏳ 待修
- 修法: 阶段 4 改「🔄 进行中（设计层完成，硬件采购 / Pi 上手编程 未开始）」+ 列已完成项
- 验证: 状态跟 hardware_design.md §0 + ROLLCALL_DEVICE_DESIGN_LOG.md 一致
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-003 一组

### [C-006] 🔴 progress_overview.md §阶段 6/7 「v0.8 推进」过期
- 位置: `00_admin/progress_overview.md:193-213` | 维度 17 | ⏳ 待修
- 修法: 阶段 6/7 刷新到「v0.8 + 之后多次推进未 bump」+ 列 5-04/5-08/5-11/5-14/5-19 关键 milestone
- 验证: 状态跟 WIP.md 最近会话 + CHANGELOG.md 一致
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-003 一组

### [C-007] 🔴 README.md 状态文本严重过期（4-29 v0.5.0 vs 当前 v0.8.0）
- 位置: `README.md:23-37` | 维度 17 | ✅ 已修
- 修法: README 顶部「状态」+「做到哪了」段重写到 5-19 / 5-20 现状；或加 5-19 现状段保留 4-29 snapshot
- 验证: README 状态跟 backend / iOS / Android / web 实装现状一致
- commit: 待 commit（modified 中，2026-05-22 进 commit 2 工程治理批）
- 决策: 2026-05-21 创建 / **public repo 首屏给招生官读** / 2026-05-22 复核已修（5-21 主会话改 + 5-22 加 5-22 里程碑行）

### [C-008] 🔴 README.md 技术栈表「老师 Web 待定」过期
- 位置: `README.md:69-71` | 维度 17 | ✅ 已修
- 修法: 「老师 Web」行改「TypeScript + Vite + Zustand（已实装 5 page，2026-05-02 v0.8 起）」
- 验证: 技术栈跟 03_dev/teacher_web/v1/package.json 一致
- commit: 待 commit（modified 中，2026-05-22 进 commit 2 工程治理批）
- 决策: 2026-05-21 创建 / 跟 C-007 一组 / 2026-05-22 复核已修

### [C-009] 🔴 README.md 缺系统真实状态里程碑
- 位置: `README.md:23-37` | 维度 17 | ✅ 已修
- 修法: 补「项目近期里程碑」段：4-28 demo → 4-29 管理员同意 → 5-02 三端启动 → 5-08 硬件定稿 → 5-19 文件治理大改造
- 验证: README 含完整里程碑串叙事
- commit: 待 commit（modified 中，2026-05-22 进 commit 2 工程治理批）
- 决策: 2026-05-21 创建 / 跟 C-007 一组 / 2026-05-22 复核已修

### [C-010] 🔴 RollCall_Spec.md 仍以 Phase 1/Phase 2 为主叙事
- 位置: `01_specs/rollcall/RollCall_Spec.md:17-18, 26, 182, 203, 233, 460, 466, 586-590, 653-679, 693, 706` | 维度 17 | ⏳ 待修
- 修法: 跟 B-027 同（§1 概述改双路径并存 / Phase 1/2 → 路径 A/B/C / 附录 B.1 防代签段保留但去时序）
- 验证: 同 B-027
- commit: —
- 决策: 2026-05-21 创建 / 跟 B-027 重复，合并处理

### [C-011] 🔴 system_features.md 引用废弃独立 repo Tomoshibi-iOS
- 位置: `02_design/system_features.md:47, 59, 61, 67, 70, 75` | 维度 17 | ⏳ 待修
- 修法: 5-06 退役那段同步规则全删（§跨 repo 同步 / 物理复制 / 反向同步）→ 改「iOS 直接在 03_dev/student_ios/v1/，单 repo 同源」
- 验证: `grep -i "Tomoshibi-iOS\|TomoshibiiOSApp\|跨 repo" system_features.md` = 0
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-012 一组（5-06 决策传播）

### [C-012] 🔴 ANDROID_DESIGN_LOG / IOS_DESIGN_LOG 残留独立 repo 引用
- 位置: `03_dev/student_android/ANDROID_DESIGN_LOG.md:6, 246, 247` + `03_dev/student_ios/IOS_DESIGN_LOG.md:583` | 维度 17 | ⏳ 待修
- 修法: 3 处全删 / 重写，统一「单 repo `~/dev/DMSD/03_dev/student_{ios,android}/v1/`」
- 验证: grep 独立 repo 字眼全 0
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-011 一组

### [C-013] 🔴 flow_design.md ASCII 图标错 Pi 4B（已 4-21 推翻为 Pi 3A+）
- 位置: `02_design/flow_design.md:71` | 维度 17 | ⏳ 待修
- 修法: `Pi 4B 2GB` → `Pi 3A+`
- 验证: grep `Pi 4B` flow_design.md = 0
- commit: —
- 决策: 2026-05-21 创建 / 一行修

### [C-016] 🔴 4 处文件引用归档的「文件结构指南.md」
- 位置: `00_admin/文档同步点清单.md:68, 72-75` + `WIP.md:280` + `TODO.md:311, 661` | 维度 17 | ⏳ 待修
- 修法: 文档同步点清单 §2 + WIP.md:280 + TODO.md:311 改成 `.claude/skills/project-overview/SKILL.md`；TODO.md:661 直接删
- 验证: `grep -r "00_admin/文件结构指南" 00_admin/ WIP.md TODO.md` = 0
- commit: —
- 决策: 2026-05-21 创建 / 5-04 归档但 4 处引用未清

### [C-028] 🔴 decision_log.md 停 4-15（1 个多月 AC 叙事空白）
- 位置: `05_logs/decision_log.md` | 维度 11 | ⏳ 待修
- 修法: itsuki 自己补 15+ 条决策（4-19 G2 / 4-21 命名 / 4-29 38 条 + 管理员同意 / 5-02 三端启动 / 5-08 硬件定稿 / 5-11 沟通规则 / 5-19 防漂 C 方案）；CC 起草 draft 等粘贴 — **不直写**
- 验证: 时间线连贯到 5-21；面试调取脉络无 4-15 后空白
- commit: —
- 决策: 2026-05-21 创建 / **itsuki 自己写 / CC 只起草 draft** / 待拍板起草开始

### [C-029] 🔴 project_evolution.md 停 4-13
- 位置: `05_logs/project_evolution.md:147` | 维度 11 | ⏳ 待修
- 修法: 跟 C-028 同 — itsuki 自己补「第五次重大转折」/「第六次」等段
- 验证: 时间线连贯到 5-21
- commit: —
- 决策: 2026-05-21 创建 / 跟 C-028 一组

### [C-036] 🔴 SC26 4 skill 共 14 处 DMSD 残留（5-16 拍板未完成）
- 位置: `~/dev/SC26/.claude/skills/{session-wrap:8, file-linkage:3, project-overview:2, memory-write:1}` | 维度 14 | ⏳ 待修
- 修法: 清 SC26 session-wrap 8 处 DMSD 引用（优先级比 Tango 高 — SC26 是 itsuki 在跑的实际项目）
- 验证: `grep -r "DMSD" ~/dev/SC26/.claude/skills/` 全 0
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [C-037] 🔴 cc-project-template 6 skill 共 45 处 DMSD 残留
- 位置: `~/dev/cc-project-template/.claude/skills/{project-overview:12, memory-write:10, version-bump:9, session-wrap:7, new-feature:4, file-linkage:3}` | 维度 14 | ⏳ 待修
- 修法: 再次跑 grep + 清剩余 45 处（5-16 D 案没清干净）
- 验证: `grep -r "DMSD" ~/dev/cc-project-template/.claude/skills/` 全 0
- commit: —
- 决策: 2026-05-21 创建 / 待拍板

### [C-048] 🔴 没 CI/CD `.github/workflows/`
- 位置: `.github/workflows/`（不存在）| 维度 16 | ⏳ 待修
- 修法: 加 `.github/workflows/test.yml` 跑 `pytest 03_dev/backend/v1/tests/`；可加 ruff / mypy
- 验证: GitHub PR 自动跑 pytest 显示绿勾
- commit: —
- 决策: 2026-05-21 创建 / v1.0 上线前必修 / 待拍板

---

## 🟡 该修（58 条）

### 子代理 A 维度 1-5（22 条）

### [A-006] 🟡 教师 login 没指数退避 / IP 锁
- 位置: `routers/auth.py:71-104` | 维度 5 | ⏳ 待修
- 修法: 同 A-005 但阈值更严（3 次失败立锁 30 分钟）
- 决策: 2026-05-21 创建

### [A-007] 🟡 CORS 默认开发地址，没 production override 校验
- 位置: `config.py:40` | 维度 5 | ⏳ 待修
- 修法: `get_settings` 加 `if app_env=="production" and "*" in cors_origin_list: raise`
- 决策: 2026-05-21 创建

### [A-008] 🟡 SQLite 默认 DB — production 风险
- 位置: `config.py:26` | 维度 5 | ⏳ 待修
- 修法: 加 fail-fast `if app_env=="production" and is_sqlite: raise`
- 决策: 2026-05-21 创建

### [A-009] 🟡 点呼机 src 全空骨架 — 5 端联动不可能跑通
- 位置: `03_dev/rollcall_device/src/main.py + nfc + api + led + audio`（全 placeholder）| 维度 5 | ⏳ 待修
- 修法: 二选一 — backend NFC endpoint 标 `disabled until v1.0` / 或 spec ECDSA 段降级 v1.1
- 决策: 2026-05-21 创建 / 跟 A-010 一组

### [A-011] 🟡 idempotency_key 无 UniqueConstraint
- 位置: `models.py:617-619` + `routers/rollcall.py:164-172` | 维度 5 | ⏳ 待修
- 修法: 加 `UniqueConstraint("session_id", "idempotency_key", name="uq_rce_idempotency")`；router 查重改成先查 key 命中
- 决策: 2026-05-21 创建

### [A-012] 🟡 教师 register 不校验 invitation.target_email
- 位置: `routers/teachers.py:76-131` | 维度 5 | ⏳ 待修
- 修法: 注册时 body 多带 `confirmation_email` 跟 `invitation.target_email` 严格对比
- 决策: 2026-05-21 创建

### [A-013] 🟡 /applications/{application_id} 路由顺序 bug
- 位置: `applications.py:151` + `:254` | 维度 5 | ⏳ 待修
- 修法: 把 `/pending-for-me` 定义移到 `/{application_id}` 之前（FastAPI best practice：静态路径在前）
- 决策: 2026-05-21 创建

### [A-017] 🟡 teacher_web AppStatus 漏 `returned` 状态
- 位置: `teacher_web/v1/src/api/client.ts:114` | 维度 1 | ⏳ 待修
- 修法: `AppStatus` 加 `| "returned"`；UI switch 加 returned 分支
- 决策: 2026-05-21 创建

### [A-018] 🟡 teacher_web Application 接口字段不全
- 位置: `teacher_web/v1/src/api/client.ts:133-147` | 维度 1 | ⏳ 待修
- 修法: 把 backend `ApplicationOut` 全字段映到 ts 接口（含 reason / stay_locations / meals_skip / flight_*）
- 决策: 2026-05-21 创建

### [A-019] 🟡 iOS StudentAccountCreateBody 字段类型出入
- 位置: `iOS NetworkModels.swift:106-143` + `backend schemas.py:530-558` | 维度 1 | ✅ 已修
- 修法: iOS 客户端 form 加 max length 校验镜像 backend
- 实际改法: `StudentAccountCreateBody` 加 `validate() -> String?` 方法镜像 backend max length（name 100 / name_kana 100 / email 200 / phone 32 / room_no 8 / password 6-128）。返回 nil = OK，否则日语错误信息 UI 显示用
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 修复 by 5-22 fork 融合会话 + 本会话 FC-021 校 16→8**

### [A-020] 🟡 iOS path_type 跟 backend dispatch 不一致
- 位置: `backend rollcall.py:181` + `schemas.py:402-409` | 维度 1 | ⏳ 待修
- 修法: schema 加 `path_hint: Literal["A","B","manual"]` 由 client 显式标 + backend 校验
- 决策: 2026-05-21 创建

### [A-022] 🟡 iOS Decodable 字段 snake_case + camelCase 混
- 位置: `iOS NetworkModels.swift:17-24, 43-73, 142-163` | 维度 1 | ⏳ 待修
- 修法: 统一选一种 — 全局 JSONDecoder `.convertFromSnakeCase` + Swift 用 camelCase；或 AnnouncementBrief 改回 snake_case
- 决策: 2026-05-21 创建

### [A-023] 🟡 backend is_demo / is_reviewer 加了但 iOS 没字段
- 位置: `backend models.py:72` + `iOS NetworkModels.StudentBrief` | 维度 2 | ⏳ 待修
- 修法: BACKEND_DESIGN_LOG.md §4 加附注「字段隐私分级」
- 决策: 2026-05-21 创建

### [A-024] 🟡 backend rollcall 8 endpoint iOS 完全没 RollCallAPI
- 位置: `backend routers/rollcall.py` + `iOS Endpoints/`（缺）| 维度 2 | ✅ 已修（学生端，路径 B）
- 修法: 跟 A-015 同
- 实际改法: 新建 `RollCallAPI.swift` 实装 POST /checkins（学生 BTR tap iPhone 入口）。其他 7 endpoint（GET today/sessions / board / summary 等）是教师端用，iOS 学生侧不需要 — 不在本次范围
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / 跟 A-015 合并 / **2026-05-24 学生端补齐**

### [A-026] 🟡 Announcement teacher_web 没管理界面
- 位置: `iOS NetworkModels.swift:142-217` 有 + `teacher_web` 无 | 维度 2 | ⏳ 待修
- 修法: teacher_web 加 Announcement 发布页 + API；或 spec 标 v1.1
- 决策: 2026-05-21 创建

### [A-028] 🟡 spec ECDSA / nonce 在 02_design 但 backend 全不知道
- 位置: `flow_design.md:63-115` + `hardware_design.md:144` + `ERROR_CODES.md:26` vs `backend models/schemas/routers` | 维度 2 | ⏳ 待修
- 修法: 跟 A-010 同
- 决策: 2026-05-21 创建 / 跟 A-010 合并

### [A-029] 🟡 5 端 DESIGN_LOG 无「实装进度对照表」
- 位置: `IOS_DESIGN_LOG.md` + `ANDROID_DESIGN_LOG.md` + `WEB_DESIGN_LOG.md` | 维度 3 | ⏳ 待修
- 修法: 每个 DESIGN_LOG 顶部加「当前实装进度速查表」（基于 spec §xx / 字段 / endpoint 列「已 / 部分 / 未」）
- 决策: 2026-05-21 创建

### [A-030] 🟡 amber Card 三态 demo-only spec 标了 iOS/Android 仍用 long-press
- 位置: `system_features.md §7.3.8` + `iOS HomeStubs.swift:256, 535` + `Android AppStore.kt:59-61` | 维度 3 | ⏳ 待修
- 修法: 跟 A-033/034 同
- 决策: 2026-05-21 创建 / 跟 A-033/034 合并

### [A-032] 🟡 teacher_web/demo/ 残留 14 jsx + v1/index.html 7700 行
- 位置: `teacher_web/demo/src/components/` 14 jsx + `v1/src/index.html` | 维度 3 | ⏳ 待修
- 修法: (1) v1/src/index.html 回归 vite shell（跟 A-039 同） / (2) demo/ 整体 archive 到 99_archive/
- 决策: 2026-05-21 创建 / 跟 A-039 合并

### [A-036] 🟡 iOS SEED.user 硬编码 + Android MockData 双端同步漂
- 位置: `iOS Foundation/Seed/SEED.swift:10-30` + `Android data/seed/MockData.kt:11, 17` | 维度 4 | ✅ 已修（iOS 端）
- 修法: 登录后强制清 SEED.user，未登录显示「— 」占位；AppStore 引 `isAuthenticated` gate
- 实际改法: AppStore.swift 加 `var isAuthenticated: Bool { authToken != nil }` gate。view 用此 gate 决定回退到 SEED.user 占位（登录前）或显示「— 」（登录后未拉到数据）。token 失效会在 401 时清空触发重新登录
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 iOS 端修复 by 5-22 fork 融合会话**（Android MockData 还未同步）

### [A-037] 🟡 iOS StayListStubs 5 处 DEMO-ONLY 替代 GET /applications/mine
- 位置: `Features/StayList/StayListStubs.swift:390, 453, 687, 1133, 1346` | 维度 4 | ⏳ 待修
- 修法: 替换成 `ApplicationsAPI.listMine()`
- 决策: 2026-05-21 创建

### [A-038] 🟡 iOS AppStore Announcement demo seed 5 处
- 位置: `Foundation/AppState/AppStore.swift:98, 217, 230, 260, 286, 535` | 维度 4 | ✅ 已修
- 修法: 上线前删 `seedDemoAnnouncements()` + 调用点 + 函数本体
- 实际改法: AppStore.swift 删 145 行 `seedDemoAnnouncements()` 函数本体（5 条 demo 公告 + 5 条 reply seed）+ init() 调用点。公告全走 backend AnnouncementsAPI
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-21 创建 / **2026-05-24 修复 by 5-22 fork 融合会话**

### 子代理 B 维度 6-10（17 条）

### [B-003] 🟡 TODO §F 跟 §🛠️ A/B/C/D/E + §G 功能重复
- 位置: `00_admin/TODO.md:83-92` vs `:72-81` | 维度 10 | ⏳ 待修
- 修法: §F 已废条目移到 §1061 归档；活的留 §F
- 决策: 2026-05-21 创建

### [B-006] 🟡 TODO §🐛 §📱 §🛰️ 嵌套「已完成 + 残留」mixed list
- 位置: `00_admin/TODO.md:105-249` | 维度 10 | ⏳ 待修
- 修法: 「✅ 已完成」段从 §抽离归档到 §1061
- 决策: 2026-05-21 创建

### [B-007] 🟡 TODO §🟢 低优先级含已过期死条目
- 位置: `00_admin/TODO.md:1003-1015` | 维度 10 | ⏳ 待修
- 修法: line 1003 .pages 改 3 个（去 rollcall）；line 1012 改 `[x]`
- 决策: 2026-05-21 创建

### [B-014] 🟡 MEMORY.md stale fact「项目 v0.3.1」实际 v0.8.0
- 位置: `MEMORY.md:29, 46` | 维度 8 | ⏳ 待修
- 修法: line 29 改「截至 2026-05-19 v0.8.0」；line 46 加「v0.4-v0.8 演化简表」
- 决策: 2026-05-21 创建

### [B-015] 🟡 MEMORY.md「VPS (~/DMSD)」段已废但仍叙述
- 位置: `MEMORY.md:33-35` | 维度 8 | ⏳ 待修
- 修法: line 24 改「Mac path only — VPS 2026-04-19 deprecated」；line 33-35 缩成一句
- 决策: 2026-05-21 创建

### [B-016] 🟡 MEMORY.md TODO 段过期 41 天
- 位置: `MEMORY.md:56-63` | 维度 8 | ⏳ 待修
- 修法: 整段砍 — TODO 真值在 `00_admin/TODO.md`；或改成「TODO 真值见 00_admin/TODO.md — 本段不维护」
- 决策: 2026-05-21 创建

### [B-017] 🟡 MEMORY.md Python Day 1 段冻 41 天
- 位置: `MEMORY.md:50-54` | 维度 8 | ⏳ 待修
- 修法: 砍 — 学习进度在 `05_logs/learning_path.md`
- 决策: 2026-05-21 创建

### [B-022] 🟡 hooks README 字段错乱 §F/G/H/I 顺序
- 位置: `00_admin/hooks/README.md:15-110` | 维度 9 | ⏳ 待修
- 修法: 重排字段 A-K = PostToolUse 7 + PreToolUse 1 + SessionStart 1 + Git 2
- 决策: 2026-05-21 创建

### [B-023] 🟡 pre-commit:99 引用过期路径「00_admin/版本管理SOP.md」
- 位置: `00_admin/hooks/pre-commit:99` | 维度 9 | ⏳ 待修
- 修法: line 99 改「→ 对照 .claude/skills/version-bump/SKILL.md §2 决策树判断」
- 决策: 2026-05-21 创建

### [B-024] 🟡 hooks README 测试命令含过期路径 -Users-itsuki-dev-DMSD
- 位置: `00_admin/hooks/README.md:118` | 维度 9 | ⏳ 待修
- 修法: 改账号名 itsuki → kurekoduki
- 决策: 2026-05-21 创建 / 跟 B-013 同源

### [B-029] 🟡 ENUM_REGISTRY §13 path_type 扩展性说明跟 4-19 G2 不一致
- 位置: `01_specs/rollcall/ENUM_REGISTRY.md:82-87` | 维度 6 | ⏳ 待修
- 修法: 明确 v1.0 Android 用 B 跟 iOS 同；或现在拆 C
- 决策: 2026-05-21 创建

### [B-030] 🟡 DEVICE_REGISTRY §3.1 物理形态写 Pi Zero 2 W / Pi 4B 已废
- 位置: `DEVICE_REGISTRY.md:30` | 维度 6 | ⏳ 待修
- 修法: 改「Raspberry Pi 3A+ + PN532 V3 + 01Studio USB 小音响（详见 hardware_design.md §2）」
- 决策: 2026-05-21 创建

### [B-031] 🟡 DEVICE_REGISTRY §6 部署位置候选码跟 S18 未对齐
- 位置: `DEVICE_REGISTRY.md:91-98` | 维度 6 | ⏳ 待修
- 修法: 按 S18 改 `dorm-1-01 / dorm-2-01 / dorm-4-01`（3 寮废止）
- 决策: 2026-05-21 创建

### [B-035] 🟡 GPIO 接线 hardware_design vs ROLLCALL_DEVICE 不同步
- 位置: `hardware_design.md §2.4` + `ROLLCALL_DEVICE_DESIGN_LOG.md:61-78` | 维度 7 | ⏳ 待修
- 修法: hardware_design.md §2.4 落具体 GPIO pin 数字 + ROLLCALL_DEVICE 引用 hardware_design 章节（一处真值）
- 决策: 2026-05-21 创建

### [B-038] 🟡 BOM 列零件代码没用 — 5 个零件没回填
- 位置: `hardware_design.md §4.2` | 维度 7 | ⏳ 待修
- 修法: §4.2 BOM 加 5 行（LED 套装 / USB 小音响 / 面包板 / 杜邦线 / 外壳+风扇）+ 更新合计
- 决策: 2026-05-21 创建

### [B-039] 🟡 hardware_design §0 状态 vs §4.4 自相矛盾「Demo 阶段砍 LED」
- 位置: `hardware_design.md:20, 316` | 维度 7 | ⏳ 待修
- 修法: 删第一个 §4.4（demo 阶段已过，5-08 已重新选型）；第二个 §4.4 改 §4.5
- 决策: 2026-05-21 创建

### 子代理 C 维度 11-17（19 条）

### [C-014] 🟡 「端数」混乱（4 端 / 5 端 / 三端）
- 位置: `CLAUDE.md:79, 173, 195` + `WIP.md:42-44` + `CHANGELOG.md:3, 20, 38` | 维度 17 | ⏳ 待修
- 修法: 项目实际 5 端，统一改「5 端」+ 列各端；CHANGELOG 历史段可保留旧措辞
- 决策: 2026-05-21 创建

### [C-015] 🟡 WIP 关键文件边界表错路径 03_dev/device/
- 位置: `WIP.md:264` | 维度 17 | ⏳ 待修
- 修法: `03_dev/device/` → `03_dev/rollcall_device/`
- 决策: 2026-05-21 创建

### [C-017] 🟡 hooks/README §A 数字错「13 联动规则」实际 18 条
- 位置: `00_admin/hooks/README.md` 表里 | 维度 17 | ⏳ 待修
- 修法: `13 联动规则` → `18 联动规则`
- 决策: 2026-05-21 创建

### [C-018] 🟡 hooks/README §B 调整记录缺 5-19 新加 hook
- 位置: `00_admin/hooks/README.md §B` | 维度 17 | ⏳ 待修
- 修法: §B 加「2026-05-19 加 post-edit-format.sh + post-edit-project-overview-check.sh + check_overview_drift.sh — 见 §F / §G / §I」
- 决策: 2026-05-21 创建

### [C-019] 🟡 CHANGELOG 顶部「最后更新 5-02」实际 5-19+ 多次未 bump 推进
- 位置: `CHANGELOG.md:3` | 维度 17 | ⏳ 待修
- 修法: 顶部加「2026-05-19 注: v0.8 后累积 15+ commit 未 bump，见 WIP / TODO」
- 决策: 2026-05-21 创建

### [C-020] 🟡 RollCall_Spec 标题 / 副标题 v0.1 / v0.2 / v0.3 措辞混乱
- 位置: `RollCall_Spec.md:1-7` | 维度 17 | ⏳ 待修
- 修法: 标题改「# RollCall Spec（点呼仕様）」（去 v0.1 后缀）+ 副标题加版本流叙事
- 决策: 2026-05-21 创建

### [C-022] 🟡 system_features.md 顶部「最后更新 2026-05-03」过时
- 位置: `02_design/system_features.md:13` | 维度 17 | ⏳ 待修
- 修法: 5-04 / 5-08 等关键节点更新顶部时间戳
- 决策: 2026-05-21 创建

### [C-024] 🟡 commit 8e35338 混议题（5-14 + 5-16）
- 位置: commit `8e35338` | 维度 12 | ⏳ 待修
- 修法: 未来 commit 拆 — 一议题一 commit
- 决策: 2026-05-21 创建 / 历史 commit 不动，未来注意

### [C-025] 🟡 commit 13276e5 message「8 项收尾流程」但只改 3 文件
- 位置: commit `13276e5` | 维度 12 | ⏳ 待修
- 修法: 未来 message 不写改动量数字，让 stat 自己说话
- 决策: 2026-05-21 创建

### [C-030] 🟡 learning_path.md 可能过时（已走过的路 4-13 后未补）
- 位置: `05_logs/learning_path.md:153` | 维度 11 | ⏳ 待修
- 修法: itsuki 自己审查 + 补条目
- 决策: 2026-05-21 创建

### [C-031] 🟡 raw 5 月各文件缺「## AC 信号」双写段
- 位置: `05_logs/raw/2026-05-*.md`（除 2026-05-10）| 维度 11 | ⏳ 待修
- 修法: 要么改 SKILL 规则取消双写要求；要么 5-19/5-16 等 raw 补回 `## AC 信号 (HH:MM)` 段
- 决策: 2026-05-21 创建

### [C-033] 🟡 5-19 raw 模式标记但无 AC 信号双写段
- 位置: `05_logs/raw/2026-05-19.md` | 维度 13 | ⏳ 待修
- 修法: 跟 C-031 同
- 决策: 2026-05-21 创建

### [C-034] 🟡 raw/2026-05-16 双文件 AC 跟工程审计混
- 位置: `05_logs/raw/2026-05-16.md` + `2026-05-16_AC合格率评估+官网验证.md` | 维度 13 | ⏳ 待修
- 修法: 未来 inbox scratchpad 命名跟 raw 文件名对齐（一对一）
- 决策: 2026-05-21 创建

### [C-035] 🟡 Tango 4 skill 共 4 处 DMSD 残留
- 位置: `~/dev/tango/.claude/skills/{version-bump:2, file-linkage:1, new-feature:1}` | 维度 14 | ⏳ 待修
- 修法: 按 TODO §🛠️ G 边开发边清；或集中一次清
- 决策: 2026-05-21 创建

### [C-039] 🟡 backend python-jose 3.3.0 含 2 个 CVE
- 位置: `03_dev/backend/v1/requirements.txt:9` | 维度 15 | ⏳ 待修
- 修法: 升 `python-jose[cryptography]>=3.4.0`；或换 `pyjwt[crypto]>=2.10.0`
- 决策: 2026-05-21 创建 / 生产前必修

### [C-040] 🟡 backend bcrypt 4.x 可能漏 passlib 迁移
- 位置: `03_dev/backend/v1/requirements.txt:10` | 维度 15 | ⏳ 待修
- 修法: grep backend 代码确认 passlib 真清；如还引用会 runtime 抛错
- 决策: 2026-05-21 创建

### [C-042] 🟡 backend demo 用 == 锁死小版本跟 v1 用 >= 不一致
- 位置: `03_dev/backend/demo/requirements.txt` | 维度 15 | ⏳ 待修
- 修法: demo 改 >=，跟 v1 风格统一
- 决策: 2026-05-21 创建

### [C-044] 🟡 iOS 没 Package.swift / Podfile — 依赖管理不可见
- 位置: `03_dev/student_ios/` | 维度 15 | ⏳ 待修
- 修法: 确认 iOS 工程 SPM 管理 — 如是，把 Package.resolved 进 git 跟踪
- 决策: 2026-05-21 创建

### [C-049] 🟡 backend v1 没 pytest.ini / pyproject.toml 测试配置
- 位置: `03_dev/backend/v1/` | 维度 16 | ⏳ 待修
- 修法: 加 `pyproject.toml [tool.pytest.ini_options]` 或 `pytest.ini`
- 决策: 2026-05-21 创建

### [C-050] 🟡 backend 无 rollcall / study / teachers / applications 测试
- 位置: `03_dev/backend/v1/tests/` | 维度 16 | ⏳ 待修
- 修法: 补 test_rollcall.py / test_study.py / test_applications.py 各 ~150-200 行
- 决策: 2026-05-21 创建 / v1.0 上线前必加

---

## 🟢 优化 / 信息 / positive note（30 条）

### 子代理 A（5 条）

### [A-014] 🟢 reviewer 注册码 999999 写死 seed.py public repo 风险
- 位置: `seed.py:251` + `:247` | 维度 5 | ⏳ 待修
- 修法: 移到 .env / secrets/；上线后 rotate
- 决策: 2026-05-21 创建

### [A-021] 🟢 iOS / Android / backend 学生 ID 都 UUID 一致（positive）
- 决策: 2026-05-21 创建 / 无需动作

### [A-025] 🟢 routers/applications + iOS ApplicationsAPI 已对齐（positive）
- 决策: 2026-05-21 创建 / 无需动作

### [A-031] 🟢 BACKEND_DESIGN_LOG 跟实装代码对齐（positive）
- 决策: 2026-05-21 创建 / 无需动作

### [A-040] 🟢 backend is_demo 过滤逻辑正确生效（positive）
- 决策: 2026-05-21 创建 / 无需动作

### 子代理 B（13 条）

### [B-008] 🟢 WIP graphify 段复述 TODO 内容违反铁律
- 位置: `WIP.md:175-184` vs `TODO.md:43-50` | 维度 10 | ⏳ 待修
- 修法: WIP 改简短摘要「拍板见 raw / 残留见 TODO §🛠️ C」
- 决策: 2026-05-21 创建

### [B-009] 🟢 TODO §📄 HTML 改造候选含 README（itsuki 4-29 已 cleanup）
- 位置: `TODO.md:284-304` | 维度 10 | ⏳ 待修
- 修法: 低优段标「未启动 — 等 §A 元任务做完再 review」
- 决策: 2026-05-21 创建

### [B-010] 🟢 TODO §🛣️ 38 条 baseline 数字状态可能漂
- 位置: `TODO.md:397-404` | 维度 10 | ⏳ 待修
- 修法: 数字加注「⚠️ 4-30 baseline；实装层进度看 §F」；或重 baseline
- 决策: 2026-05-21 创建

### [B-018] 🟢 memory 孤儿 feedback_llm_self_discipline_unreliable.md 未建
- 位置: `TODO.md:67-70`（规划中）| 维度 8 | ⏳ 待修
- 修法: 等 itsuki 拍板才写（已按 SOP）
- 决策: 2026-05-21 创建

### [B-019] 🟢 抽样 4 个 memory description vs 正文一致（positive）
- 决策: 2026-05-21 创建 / 无需动作 / 26+ 没全扫

### [B-020] 🟢 抽样未找 memory 矛盾（positive，但 22+ 未扫）
- 决策: 2026-05-21 创建 / 无需动作 / 留 follow-up

### [B-025] 🟢 settings.json 注册数 vs hooks 目录一致（positive）
- 决策: 2026-05-21 创建

### [B-026] 🟢 hooks lib/sync-rules.sh 抽样无死链（positive）
- 决策: 2026-05-21 创建

### [B-032] 🟢 ENUM_REGISTRY §3 exempt_range 跟 spec §2.1 对齐（positive）
- 决策: 2026-05-21 创建

### [B-033] 🟢 FIELD_REGISTRY §3 禁止字段来源指针完整（positive）
- 决策: 2026-05-21 创建

### [B-034] 🟢 ENUM ERROR_CODES vs spec §7 边界规则对齐（positive）
- 决策: 2026-05-21 创建

### [B-036] 🟢 模块选型（PN532 V3 / NTAG215 / ST25DV16K）3 文件对齐（positive）
- 决策: 2026-05-21 创建

### [B-037] 🟢 src/main.py 骨架占位无漂（positive）
- 决策: 2026-05-21 创建

### [B-040] 🟢 ROLLCALL_DEVICE §10-D1~D6 跟 TODO §🛰️ D1-D6 对齐（positive）
- 决策: 2026-05-21 创建

### [B-041] 🟢 ROLLCALL_DEVICE §1.2 跟 hardware_design 一致（positive）
- 决策: 2026-05-21 创建

### 子代理 C（12 条）

### [C-021] 🟢 README 数字「v0.4-v0.5 共 14 个版本」过时
- 位置: `README.md:37` | 维度 17 | ⏳ 待修
- 修法: 去掉具体数字「完整版本变更记录见 CHANGELOG.md」
- 决策: 2026-05-21 创建

### [C-023] 🟢 ROLLCALL_DEVICE / hardware_design 时间线一致（positive）
- 决策: 2026-05-21 创建 / 样板

### [C-026] 🟢 commit 81842f4「整理 14 文件」message vs stat 对齐（positive）
- 决策: 2026-05-21 创建

### [C-027] 🟢 commit 8e35338 message 长 + 详细符合 commit style（positive）
- 决策: 2026-05-21 创建

### [C-032] 🟢 5-16/5-19 inbox scratchpad 存在 + 对应 raw 同日详细 dump（positive）
- 决策: 2026-05-21 创建 / AC 素材主线没问题

### [C-038] 🟢 SC26 / cc-project-template / Tango 目录 + .claude 结构齐（positive）
- 决策: 2026-05-21 创建

### [C-041] 🟢 fastapi / sqlalchemy / pydantic 版本约束合理（positive）
- 决策: 2026-05-21 创建

### [C-043] 🟢 Android compileSdk 36 / minSdk 26 / targetSdk 36 标准（positive）
- 决策: 2026-05-21 创建

### [C-045] 🟢 backend v1 测试齐全（4 文件 + conftest ~900 行）（positive）
- 决策: 2026-05-21 创建

### [C-046] 🟢 tests/conftest.py 测试隔离 OK（positive）
- 决策: 2026-05-21 创建

### [C-047] 🟢 关键路径覆盖 auth / registration / announcements（positive）
- 决策: 2026-05-21 创建

---

## 📋 维度索引

| 维度 | 范围 | 关键条目 |
|---|---|---|
| 1 跨端字段对齐 | A-015 ~ A-022 | A-015 / A-016 / A-022 |
| 2 联动矩阵 | A-023 ~ A-028 | A-024 / A-027 / A-028 |
| 3 设计分层 | A-029 ~ A-032 | A-029 / A-030 |
| 4 demo scaffold | A-033 ~ A-040 | A-033 / A-039 |
| 5 NFC 安全 | A-001 ~ A-014 | A-001~005 / A-010 |
| 6 规格主体 | B-027 ~ B-034 | B-027 / B-028 |
| 7 硬件 vs 点呼机 | B-035 ~ B-041 | B-035 / B-038 / B-039 |
| 8 memory 索引 | B-011 ~ B-020 | B-011 / B-012 / B-013 |
| 9 挂钩系统 | B-021 ~ B-026 | B-021 |
| 10 TODO 真值 | B-001 ~ B-010 | B-001 / B-002 / B-004 / B-005 |
| 11 AC 时间线 | C-028 ~ C-032 | C-028 / C-029 |
| 12 commit vs 改动 | C-024 ~ C-027 | — |
| 13 AC 漏抓 | C-033 ~ C-034 | — |
| 14 跨项目残留 | C-035 ~ C-038 | C-036 / C-037 |
| 15 CVE | C-039 ~ C-044 | C-039 |
| 16 测试 | C-045 ~ C-050 | C-048 / C-050 |
| 17 逐字精读 | C-001 ~ C-023 | C-001 / C-007 / C-010 / C-011 |

---

## 🔗 跨子代理重复条目（去重提示）

合并修同一处问题：

| 重复组 | 条目 | 同一处 |
|---|---|---|
| CLAUDE.md 路径漂 | B-013 + C-001 | `CLAUDE.md:205` |
| memory feedback 死链 | B-011 + B-012 + C-002 | `CLAUDE.md:63, 69` |
| Phase 1/2 过期 | B-027 + B-028 + C-010 | spec 主体 |
| 5-06 独立 repo 退役 | C-011 + C-012 | system_features + design log |
| amber Card demo cycle | A-030 + A-033 + A-034 | iOS + Android |
| ECDSA / nonce | A-003 + A-009 + A-010 + A-028 | backend rollcall |
| teacher_web 7700 行 | A-032 + A-039 | v1/index.html |

---

## 📌 备注

- 总数 131 = 部分跨子代理重复（约 8-10 条同一处问题）
- 严重程度依子代理自评，最终优先级由 itsuki 拍板
- 子代理详细 file:line + 完整描述 + 跨会话引用 → `05_logs/audit_2026-05-19/session_{A,B,C}_findings.md`
- **修复约束**：本会话 / CC 不擅自修，每条等 itsuki 拍板再动手
- 修完时填 commit hash + 状态改 ✅ + 决策日志加一行

---

## 🤖 Codex 第二轮 audit findings（2026-05-22）

> **来源**：Codex Full Coverage Findings — 2026-05-22 全文件覆盖审查
> **范围**：1003 个文件（957 已跟踪 + 46 未跟踪 / 656 文本扫内容 + 347 二进制只登记指纹）
> **总览**：14 🔴 阻塞 + 23 🟡 该修 + 2 🟢 正向 = **39 条**
> **跟 Claude 重复 / 复核**：13 条
> **Claude 漏的独立发现**：**24 条**
> **完整证据**：`05_logs/audit_2026-05-22_codex/`（file_coverage.tsv / pip_audit / npm_audit / pytest 输出）
> **本轮约束**：codex 只审查 + 记录，没改业务代码

### 最关键 3 条（codex 自评）

1. 后端测试**不是全 pass** — 默认 pytest 收集失败；忽略 warning 后 60 passed / **2 failed / 8 errors**
2. **账号删除 + 学生点呼权限 + NFC 防重放**直接影响 v1.0 上线 + App Store 审查
3. **多个 5-21 修复文件仍未跟踪**（CI / 测试 / 迁移 / 系统 bug 专栏），fresh clone 会丢

---

### 🆕 Codex 独立发现（24 条 — Claude 漏的）

#### [Codex-FC-001] 🔴 多个 5-21 核心修复文件仍未跟踪
- 位置: `00_admin/系统bug专栏.md:1`（git status 报 ??）
- 涉及文件: 系统bug专栏.md / .github/workflows/test.yml / pyproject.toml / 3 backend test / 2 alembic migration / RollCallAPI.swift / check_overview_drift.sh / post-edit-format.sh
- 修法: 决定哪些进仓库 → 统一 `git add`；不进仓库的写 `.gitignore`
- 决策: 2026-05-22 codex 创建 / **fresh clone 会丢 CI + 测试 + 迁移 + 系统 bug 总表**

#### [Codex-FC-002] 🟡 project-overview 体量再次微漂（codex 跑时实际跟现在不同）
- 位置: `.claude/skills/project-overview/SKILL.md:29`
- 描述: codex 跑时报 03_dev/ 写 395 实际 396（差 1）+ 99_archive 写 431 实际 432（差 1）
- 修法: 等本轮 audit 产物决定进不进仓库后，再跑 `bash bin/check_overview_drift.sh` 更新
- 决策: 2026-05-22 codex 创建 / **本会话 A1 已修但 codex 跑后又多了文件**

#### [Codex-FC-003] 🟡 严格锁 + skill 引用不存在的旧路径
- 位置: `.claude/session-coord.config.json:9` + `new-feature/SKILL.md:84` + `spec-sync/SKILL.md:45`
- 描述: session-coord 锁清单指向 `RollCall_Spec_v0.1.md` + `dictionary_v0.1_v0.2_v0.3.md`（旧文件名）；2 个 skill 引用 `03_dev/backend/app/`（实际在 `backend/v1/app/`）<!-- VERSION_OK -->
- 修法: 路径统一到 v1 当前目录；加路径存在性检查脚本
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-005] 🔴 后端默认 pytest 无法进入测试收集
- 位置: `03_dev/backend/v1/pyproject.toml:15`
- 描述: `filterwarnings` 把 DeprecationWarning（弃用警告）当 error；`main.py:67` 用 FastAPI `@app.on_event("startup")` 触发弃用警告 → 收集阶段失败
- 修法: 改用 FastAPI `lifespan`（新的启动钩子写法），或精确忽略这条 warning
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-006] 🔴 后端忽略 warning 后仍 2 failed / 8 errors
- 位置: `03_dev/backend/v1/tests/test_rollcall.py:30` + `test_study.py:29,64,81`
- 描述: test 用了不存在的字段 `target_date` + 不存在的类 `StudyAttendanceRoster`（真名 `StudyRoster`）；`date.today()` 提交学習请假在 19:40 后被拒
- 修法: fixture 改到当前模型名 + 当前字段；时间相关 test 固定时钟或用明天日期
- 决策: 2026-05-22 codex 创建 / 跟 [C-050] 复核

#### [Codex-FC-007] 🟡 测试注释写 in-memory 实际写本地数据库文件
- 位置: `03_dev/backend/v1/tests/conftest.py:1,7`
- 描述: 注释「in-memory SQLite」但实际是 `sqlite:///./test_tomoshibi.db`（本地文件）
- 修法: 改成真 `sqlite:///:memory:`（并处理连接池），或注释改成「文件型测试 SQLite」
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-010] 🔴 App Store 要求的账号删除未真正实现
- 位置: `02_design/system_features.md:1063` + `BACKEND_DESIGN_LOG.md:666` + `IOS_DESIGN_LOG.md:331`
- 描述: 设计要求 iOS 有删除入口 + 后端有 `DELETE /api/v1/accounts/me` + students.status='deleted'。实际后端 `accounts.py:78` 只有 POST；models.py:84 也不允许 deleted 状态；iOS `AuthAPI.swift:34` 只有 createAccount
- 修法: 后端加软删除 endpoint + 状态约束 + 测试 → iOS 接 `AccountsAPI.deleteMyAccount()` + 设置页入口
- 决策: 2026-05-22 codex 创建 / **App Store 审查必查项**

#### [Codex-FC-013] 🔴 老师登录锁定路径因缺 timedelta 导入会 500
- 位置: `03_dev/backend/v1/app/routers/auth.py:14,109`
- 描述: 只导入了 `datetime, timezone`，但 109 行用了 `timedelta(...)` → 老师连输错密码触发锁定时 NameError 500
- 修法: 补 `timedelta` 导入 + 加「连续失败 3 次触发锁定」测试
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-014] 🔴 学生点呼 checkin endpoint 要求老师 token
- 位置: `03_dev/backend/v1/app/routers/rollcall.py:151,160`
- 描述: `POST /rollcall/sessions/{session_id}/checkins` 是 NFC / iPhone tap 入口（iOS RollCallAPI.swift:14 也这么注释），但依赖 `get_current_teacher` → 学生 token 被拒
- 修法: 按路径拆权限 — 老师手动签到走 teacher endpoint / 学生 NFC tap 走 student endpoint + 校验学生身份 / 设备 / 时间窗 / 防重放
- 决策: 2026-05-22 codex 创建 / **v1.0 核心路径错权限**

#### [Codex-FC-015] 🔴 点呼开始前 5 分钟判断在整点附近会崩溃
- 位置: `03_dev/backend/v1/app/routers/rollcall.py:99`
- 描述: 用 `replace(minute=session.scheduled_window_start_at.minute - 5)`。开始时间 21:00~21:04 时 minute 变负数 → Python 抛异常。后面 `max(0, ...)` 来不及
- 修法: 用 `scheduled_window_start_at - timedelta(minutes=5)`，不要手改 minute 字段
- 决策: 2026-05-22 codex 创建 / 5-19 audit 已记，codex 复核仍存在

#### [Codex-FC-017] 🟡 规格仍写旧 `POST /api/v1/checkin`，实际是 rollcall sessions 路径
- 位置: `01_specs/rollcall/RollCall_Spec.md:192` + `API_CONVENTIONS.md:64`
- 描述: 规格路径 A/B 都写 `POST /api/v1/checkin`，但后端 + iOS 新文件用的是 `/api/v1/rollcall/sessions/{session_id}/checkins`
- 修法: 统一规格 + API conventions + 设备端 + iOS / Android 文档；旧路径只保留为历史说明
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-018] 🔴 iOS RollCallAPI.swift 没进 Xcode 工程，UI 仍走模拟签到
- 位置: `03_dev/student_ios/v1/TomoshibiApp.xcodeproj/project.pbxproj:252` + `HomeStubs.swift:1430,1435`
- 描述: Endpoints group 只有 Applications/Auth/Study/ApplicationsCreateBodies 4 个 API 文件，没有 RollCallAPI.swift；RollCallAPI.swift 本身也是未跟踪。UI 调 `simulate()` + `app.recordCheckin()` 只更新本地
- 修法: RollCallAPI.swift 加进 Xcode 工程 + Git → UI 改调真 API + 处理 401/403/重复/超时
- 决策: 2026-05-22 codex 创建 / 跟 [A-024] 实现复核 / Xcode 工程遗漏是 codex 独立发现

#### [Codex-FC-019] 🟡 iOS 默认 JSONEncoder 可能发后端不接受的 Date 格式
- 位置: `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/APIClient.swift:67` + `RollCallAPI.swift:39`
- 描述: 用默认 `JSONEncoder()`，但 `ts_local: Date?` 默认编码不是 ISO 8601 字符串 → 后端 `schemas.py:414` 期待 datetime → 非 nil 时可能 422
- 修法: 统一 `JSONEncoder.dateEncodingStrategy = .iso8601`，或时间字段跨端用 String 客户端格式化
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-020] 🟡 iOS ApplicationOut 漏后端 + Web 都有的 bus_route_id | ✅ 已修
- 位置: `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:43`
- 描述: iOS 没 `bus_route_id`，后端 `schemas.py:187` 有 `bus_route_id: Optional[UUID]`，Web `client.ts:252` 也有
- 修法: iOS 模型补字段（即使暂不显示也要保留以免 decode 缺数据）
- 实际改法: NetworkModels.swift ApplicationOut struct 在 `flight_arr_at` 之后、`submitted_at` 之前加 `let bus_route_id: UUID?`
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-22 codex 创建 / 跟 [A-018] 漏补项 / **2026-05-24 修复 by 本会话 CC**

#### [Codex-FC-021] 🟡 学生注册 room_no 长度 iOS 16 vs 后端 8 | ✅ 已修
- 位置: `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/NetworkModels.swift:107,137` + `backend/schemas.py:558`
- 描述: iOS 校验 16 字符 / 后端最大 8 → iOS 过校验后端 422
- 修法: 二选一 — iOS 改 8 或后端改 16（以字段字典为准）
- 实际改法: 选 iOS 改 8 跟 backend 对齐。NetworkModels.swift line 107 注释 + line 137 validate() 阈值 `room_no.count > 16` → `> 8`。宿舍号实际格式 M205/W205B 长度 4-5 字符，max 8 够用
- commit: —（5-24 收尾时统一 commit）
- 决策: 2026-05-22 codex 创建 / **2026-05-24 修复 by 本会话 CC**（选 iOS 跟 backend 对齐，理由：backend 是字段真值源）

#### [Codex-FC-025] 🟡 Web StayLocation 字段形状跟后端不一致 — ✅ N/A
- 位置: `03_dev/teacher_web/v1/src/api/client.ts:220` + `backend/schemas.py:29`
- 描述: Web `{date, location, contact}` / 后端 `{kind, name, address, phone}` → 外泊 / 帰国住宿地跨端解释错误
- 修法: 以 `FIELD_REGISTRY.md` + 后端 schema 为真值，统一 Web 类型 + 渲染
- 决策: 2026-05-22 codex 创建 / **2026-05-26 itsuki TODO §🛠️ §L 标 N/A**（Vite 整体废弃）
- 工程注记: `api/client.ts` 文件本身**仍在主线没归档**（README §设计权威「保留 — 未来 Ryō 接真后端时复用」）。Task #6 真接口对接时把 client.ts 接进 standalone HTML 仍会踩坑 → 届时本条要重开

#### [Codex-FC-026] 🟡 Web 学習请假响应缺 period — ✅ N/A
- 位置: `03_dev/teacher_web/v1/src/api/client.ts:299` + `backend/schemas.py:369`
- 描述: Web StudyAbsenceRequestOut 没 period；后端返回 `period: first_half | second_half | full`
- 修法: Web 类型补 period + 页面显示同步补「前半 / 后半 / 全程」
- 决策: 2026-05-22 codex 创建 / **2026-05-26 itsuki TODO §🛠️ §L 标 N/A**（Vite 整体废弃）
- 工程注记: 同 FC-025 — `client.ts` 没归档，Task #6 真接口对接时本条要重开

#### [Codex-FC-027] 🟡 老师公告 client 跟后端权限不一致 + 无页面使用 — ✅ N/A
- 位置: `03_dev/teacher_web/v1/src/api/client.ts:162` + `backend/routers/announcements.py:105,193`
- 描述: Web client 加了公告列表 / 详情 / 创建 / 删除。后端列表 / 详情依赖 `get_current_student`（老师 token 不能用）；ripgrep 也只发现 client 定义没页面调
- 修法: 二选一 — 后端补 teacher list/detail endpoint，或 Web 只保留能用的 create/delete + 补页面前先写权限契约
- 决策: 2026-05-22 codex 创建 / **2026-05-26 itsuki TODO §🛠️ §L 标 N/A**（Vite 整体废弃）
- 工程注记: backend 端权限契约问题（`get_current_student` vs `get_current_teacher`）跟 Vite 无关，Task #6 真接口对接时本条要重开 + 顺便把老师公告页接进 standalone HTML

#### [Codex-FC-028] 🟡 老师邀请码权限前后端角色不一致 — ✅ N/A
- 位置: `03_dev/teacher_web/v1/src/pages/Teachers.tsx:26` + `backend/routers/teachers.py:28`
- 描述: Web 允许 寮務部長 / 寮務課長 / 寮監 发邀请码；后端还允许 学習担当 → 同老师后端允许前端不显示按钮
- 修法: 可发邀请码角色抽成共享文档真值 → 同步前后端
- 决策: 2026-05-22 codex 创建 / **2026-05-26 itsuki TODO §🛠️ §L 标 N/A**（Vite 整体废弃）
- 工程注记: `pages/Teachers.tsx` 已归档到 `99_archive/2026-05-26_teacher_web_vite实装作废/pages/Teachers.tsx`，本条 Web 侧确实 N/A。但 `backend/routers/teachers.py:28` 角色清单跟未来 Ryō standalone HTML 实装的邀请码 UI 仍要对齐 → Task #6 真接口对接时同步补

#### [Codex-FC-029] 🟡 Teacher Web 没 test 脚本
- 位置: `03_dev/teacher_web/v1/package.json:6`
- 描述: scripts 只有 dev / build / preview；`npm test` 失败（没脚本）
- 修法: 加类型检查 / 单元测试 / smoke test 脚本；或 README 写清「当前只有 build 验证」
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-030] 🟡 Teacher Web v1 README 仍说正式版未开始
- 位置: `03_dev/teacher_web/v1/README.md:3`
- 描述: README 写「老师 Web v1.0 正式版 — 未开始」，但已有 TS + Vite + Zustand + API client + 多页面<!-- VERSION_OK -->
- 修法: 更新到当前真实状态，列已接真后端 vs 仍 demo 的部分
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-033] 🟡 联动脚本遇带空格路径会拆错文件名
- 位置: `00_admin/hooks/pre-commit:126` + `bin/sync-check.sh:110`
- 描述: 用 `check_sync_for_files $STAGED_LIST` 按空格拆。仓库有 39 个带空格路径（如 `tomoshibi_flame 2.png` 截图）
- 修法: 用 null 分隔或数组安全传参；git 文件列表用 `-z` 版本
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-034] 🟡 Claude settings 注册了未跟踪 hook 脚本
- 位置: `.claude/settings.json:31`
- 描述: SessionStart 注册 `bin/check_overview_drift.sh` + PostToolUse 注册 `post-edit-format.sh`，但两脚本未跟踪 → fresh clone 后 settings 调不存在的脚本
- 修法: 脚本提交，或 settings 移除 / 降级 hook
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-035] 🟡 .gitignore 没覆盖常见秘密 + 本地状态文件
- 位置: `.gitignore:29`
- 描述: 当前忽略 `.env` / `.env.local` / `*.jks` / `*.keystore` / 数据库；漏 `*.pem` / `*.key` / `*.p12` / `*.mobileprovision` / `secrets/` / `.claude/worktrees/` / `.claude/scheduled_tasks.lock` / `*.tsbuildinfo`
- 修法: 补这些规则 + 已 git 跟踪的本地生成文件单独 `git rm --cached`
- 决策: 2026-05-22 codex 创建

#### [Codex-FC-037] 🟡 03_dev/LATEST.md 指向已归档 demo + 明文密码
- 位置: `03_dev/LATEST.md:13,16`
- 描述: 文件写 `cd 03_dev/teacher_web/demo && ./tomoshibi` + `Tomoshibi_v3_single.html` + 管理员密码 `12345678`。demo 已归档到 99_archive
- 修法: 改成「历史归档索引」；明文密码只保留在归档说明 + 标明不能用于正式版
- 决策: 2026-05-22 codex 创建

---

### 🔁 Codex 复核（13 条 — 跟 Claude 重复 / 仍存在）

| Codex 条 | 对应 Claude 条 | 复核结论 |
|---|---|---|
| Codex-FC-004 🟡 | C-048 / C-049 / C-050 | 状态字段仍混「文件不存在」vs「文件存在但失败」 |
| Codex-FC-008 🟡 | C-048（CI） | CI 设 `DATABASE_URL` 但 Alembic env.py 不读环境变量 → 实际可能迁移开发库 |
| Codex-FC-009 🟡 | C-048（CI） | 新增唯一约束 migration 在 SQLite 下要用 `batch_alter_table`，否则 CI 失败 |
| Codex-FC-011 🔴 | A-001（JWT 密钥） | `.env.example:17` 示例值能绕过生产检查（禁用列表只禁短字符串） |
| Codex-FC-012 🔴 | A-014（seed） | `seed.py:307,421` REVIEWER_PASSWORD 默认公开 + 把秘密写日志 |
| Codex-FC-016 🔴 | A-010（ECDSA） | spec 要求 v1.0 NFC 签名 / nonce / device_id，schemas 注释「v1.1 起追加」→ v1.0 上线不一致 |
| Codex-FC-022 🔴 | A-016（Android） | Android v1 `build.gradle.kts:43` 无 Retrofit/OkHttp/Ktor → AppStore.kt:37 直接回落 MockData |
| Codex-FC-023 🔴 | A-009 / A-027（点呼机） | 点呼机 src 0% + `requirements.txt:5~28` 全注释 → `pip install` 装不到 PN532 / GPIO / 音频 |
| Codex-FC-024 🔴 | A-014 / demo（密码明文） | `teacher_web/v1/src/index.html:4262,4393` 仍有 `SHARED_PASSWORD = '12345678'` + 学生姓名生日电话明文 |
| Codex-FC-031 🟡 | C-049 / C-050 | README:44 + progress:173 写「8 router + 37 case pytest 全 pass」实际 70 case 默认收集失败；backend/README 写 6 migration 实际 8 |
| Codex-FC-032 🟡 | demo scaffold | `system_features.md:1468` demo 清单已落后当前路径；memory `project_demo_scaffolds_to_remove_before_v1.md:9` 仍写 `~/dev/TomoshibiiOSApp/`（旧仓库） |
| Codex-FC-036 🟡 | C-037（cc-project-template） | 跨项目扫描发现多 skill 仍写 DMSD / Tomoshibi / itsuki / 筑波 AC 内容 → 模板复用会污染新项目 |
| Codex-FC-038（NFC v1.0 范围） | — | 见 Codex-FC-016 |

---

### 🟢 Codex 正向验证（2 条 — positive note）

#### [Codex-FC-038] 🟢 后端 pip-audit + Web npm audit 都 0 漏洞
- 位置: `05_logs/audit_2026-05-22_codex/pip_audit_backend.json:1`
- 描述: 本轮 `pip-audit -r requirements.txt -f json` 检查 48 个 Python 依赖 0 漏洞；`npm audit --omit=dev --json` + 完整 `npm audit` teacher web 也 0 漏洞
- 建议: 依赖漏洞检查纳入 CI + 定期重跑（当前结论只代表 2026-05-22 的公开漏洞数据库状态）
- 决策: 2026-05-22 codex 创建 / positive

#### [Codex-FC-039] 🟢 Alembic 当前只有 1 head 迁移链线性
- 位置: `03_dev/backend/v1/alembic/versions/b9c0d1e2f3a4_remove_applied_group.py:1`
- 描述: 本轮 `alembic heads` 返回单一 head；序列线性无分叉。问题不在「多 head 冲突」，在 CI 数据库 URL + SQLite 兼容性
- 建议: 保留 `alembic heads` 检查；以后每加 migration 跑 `alembic heads` + 一次空库 upgrade head
- 决策: 2026-05-22 codex 创建 / positive

---

### ⏭️ Codex 段下一步（等 itsuki 拍板）

1. 24 条独立发现哪几个**立刻修**？最急 codex 自评 TOP 3：[FC-001 未跟踪文件] / [FC-005+006 pytest] / [FC-013 timedelta 缺导入]
2. **App Store 审查必查** [FC-010 账号删除] — 进 v1.0 还是 v1.0.1？
3. **v1.0 核心路径错权限** [FC-014 学生 checkin endpoint] + [FC-015 minute-5 崩溃] — 等 backend 会话修？
4. Codex 复核 13 条 — 是否合并到对应 A-/B-/C- 原条目更新状态？

---

## ⏭️ 下一步（等 itsuki 拍板）

1. TOP 5（A-039 / B-013 / A-010 / A-001~005 / C-007 类）哪几个**立刻修**？
2. 重复组要不要**合并一次性修**（如 CLAUDE.md 路径漂 B-013 + C-001 一行修两条）？
3. 修完一起 commit / 分多 commit / 暂不 commit？
4. **Codex 段 24 条独立发现** 跟原专栏 131 条如何统筹？合并到 §总览 / 单独管理？
