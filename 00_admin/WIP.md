# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-08（**iOS 上架冲刺跨日大会话** — 5-07 启动「上线 App Store」目标 → backend production 部署 GCP VPS + DNS + GH Pages + Apple Dev Portal/ASC + Xcode 编译，卡 Validate Version empty 待修；早些更新:点呼机当第 5 端 + 联动机制 18 条规则升级）

> **本文件 = Claude Code 的「当下书签 + 多会话协调」清单。短小为美。**
>
> **职责分工（重要 — 别再重叠）**:
>
> | 文件 | 内容 | 给谁看 |
> |---|---|---|
> | **WIP.md（本文件）** | 当下书签 + 最近 5 次会话 1-2 行总结 + 多会话占用 + 阻塞项 | CC（每次会话开始读全文）|
> | **TODO.md** | **所有未完成事项的完整 backlog**（真值）| itsuki + CC（每次会话开始扫顶部 200 行）|
> | **progress_overview.md** | 长期章节目录（稳定，每次 close 版本时更新）| itsuki + 教授读 |
> | **CHANGELOG.md** | 已发布版本编年史 | 全部读者 |
> | **commit history** | 每次改动的细节 | git log 可查 |
>
> **铁律**：未完成的事**只写在 TODO.md**。本文件**绝不**复述 TODO 的内容。
>
> - **会话开始**: CC 读本文件全文 + `TODO.md` 顶部 200 行 + `git status`
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.8.0 <!-- VERSION_OK -->
**版本 bump 流程**: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权 — 即使 itsuki 说要 bump 但 §2 决策树不命中可以拒绝）

---

## 🎯 当前焦点

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 三端代码层启动完毕，下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-08 凌晨 by [新Mac-Opus 4.7 1M-主会话 reviewer_demo重做]

**主题**：⭐⭐⭐⭐⭐ reviewer demo 方案 review 戳穿 5 bug → itsuki 拍板「修干净再提交」→ 完整重做（v1.0.1 全提前 v1.0.0） <!-- VERSION_OK -->

- **23:30 启动**：itsuki 提「做不做老师 iOS 登录」 → CC 反对老师 iOS（用户量不对等 + 已有 teacher_web）→ itsuki 改「老师下载 app + 体验内容 + 永久注册码」
- **23:45 CC 警告 3 bug**：永久码跟 §7.16 「5 分钟 TTL」铁律冲突 / 上架决策防线被钻洞 / DB 数据污染 → 给 3 替代方案 → itsuki 拍板「demo 账号 + 老师卡在验证码 = 演示注册码门」
- **23:50 itsuki paste VPS CC 已实装方案**：060199/Reviewer-2026/999999 永久码塞 prod DB → 让主 CC 「检查 bug」
- **00:00 review 戳穿 5 bug**：(1) `999999` 4 年永久后门（refresh 一刀切作废 + 6 个 9 太规则） (2) admin 默认密码 `ChangeMe-2026-05` 进 git 历史污点 (3) reviewer 凭证一眼是 demo (4) fork seed 偏离主项目 (5) CC 没让 itsuki 拍板具体值
- **00:15 itsuki 拍板 ⭐⭐⭐**：「**接下来的修复我会全部在这个会话里进行，在修好之前我不会推进别的了**」 → v1.0.1 修理项**全部提前 v1.0.0**，质量优先于发版速度 <!-- VERSION_OK -->
- **01:00-04:30 完整重做（11 文件 / 42 pass）**：
  - schema migration `f6a7b8c9d0e1`（students.is_demo + student_registration_codes.is_reviewer + 内置 UPDATE 把 fork 旧 999999 行自动 invalidate）
  - admin_registration_code.py 3 处改（refresh + current 加 is_reviewer 过滤 + _generate_code 范围 [0,999998] reserved 999999）
  - rollcall.py + applications.py 加 is_demo 过滤（关键判断：accounts 学号查重 / auth.login **不能** 加过滤，否则 reviewer 不能 login）
  - seed.py 重写 `APP_ENV=dev|production` 双模式 + admin 密码移到 env
  - 新 `tests/test_demo_reviewer.py` 5 个 case，**42 passed**（37 原有 + 5 新）
  - 文档同步：system_features §7.20 新章 + §7.16 例外 / BACKEND_DESIGN_LOG §5.x.4 / IOS_DESIGN_LOG §3.16 / TODO §🐛 ledger
  - VPS 部署清单 + Reviewer Notes 双语文案（绝不写注册码）写到 `05_logs/raw/2026-05-08_vps_deploy_steps.md`

**新规则上线**：
- 上架前底线：reviewer 永久码必须有 `is_reviewer=True` schema flag 跟普通 5 分钟 TTL 码并存（spec §7.16 例外条款）
- memory 加 `feedback_cc_picks_value_must_announce_window.md` — CC 自挑值时必须 explicit 告知 + 给打断窗口
- 拍板：「修干净再提交」优先于「冲提交后再修」 — itsuki 引入的 engineering 时间盒新铁律

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2（假设崩→继续→真因，3 层叠加）+ 模式 5（多次：trade-off 语言陷阱 / 修干净拍板 / fork 复发 single source / CC 拍板边界）+ 模式 6（取舍三角 demo 账号方案）+ 多 AI 协作 audit。详见 `05_logs/raw/2026-05-08_reviewer_demo重做.md`

**残**：上架后操作（admin 密码改强密码 + 删 VPS 旧 060199 学生）/ Mac fork 4 部署文件合回主项目（v1.0.1）/ commit + push + VPS 部署待执行 <!-- VERSION_OK -->

### 2026-05-07 → 2026-05-08 by [Mac-主会话 跨日]

**主题**：⭐⭐⭐⭐⭐ **上线 iOS 到 App Store 冲刺**（v0.8.0 期间，提前 G2 决策） <!-- VERSION_OK -->— backend production 部署 GCP VPS + DNS + GH Pages + Apple Dev Portal/ASC/Xcode Archive 全过，卡 Validate Version empty 待修

- **5-07 启动**：itsuki 拍板「公开 App Store + 现在就推」（激进路径，提前 4-19 G2 决策的「v1.0 三端齐发」） <!-- VERSION_OK -->→ CC plan mode 设计完整路径
- **5-07 4 次反转**：itsuki 反 plan 决策（物理 fork 双份 + fork 放 DMSD 外 + NFC 完整保留 + 不声明私域）→ iOS+backend 全 fork 到 `~/dev/Tomoshibi-AppStore/`（DMSD 外，不污染 git）
- **5-07 fork 改动**：project.yml 11 处 / APIClient #if DEBUG / PrivacyInfo.xcprivacy / .entitlements（NFC + Push + Time Sensitive）/ 账号删除（Apple 5.1.1(v) iOS+backend 双端）/ SplashView 启动跳转（双端同步主项目）/ backend seed.py / VPS 部署套件（Dockerfile/docker-compose/Caddyfile/DEPLOY.md）/ METADATA.md / privacy_policy.md
- **5-07 教学失职被纠正**：CC 让 itsuki 勾 NFC 没解释 Capability 是什么 → itsuki 怒怼「我需要你的解释 你不能偷懒」→ TODO 加「教学类 Skill」
- **5-07 撞名**：Tomoshibi 占了 → `Tomoshibi · 灯火` 救场（Bundle ID 没占继续用 com.itsuki.tomoshibi）
- **5-07 VPS 启动**：itsuki 选 GCP $300 trial（不 Vultr）+ asia-northeast1-c e2-small Tokyo + SSH 公钥认证（cat 重用现有 key + GCP metadata）
- **5-08 backend 部署**：VPS CC 找到 3 个隐藏 bug（alembic env.py 不读 DATABASE_URL / docker-compose 不传 APP_ENV → create_all 绕过 alembic / migration 用 SQLite-only batch_alter_table 撞 Postgres 外键）→ Mac fork 同步 4 处修复 + TODO §🐛 v1 backend bug fix
- **5-08 OOM**：e2-small 2GB OOM kill → swap + worker 4→2
- **5-08 GH Pages**：CC 用 gh CLI API 启用绕过手动点 → 双 URL HTTP/2 200
- **5-08 Xcode 链式踩坑**：iOS 26→18 降级 supportsImagePlayground iOS 18.1+ only → 删 → Archive 成功 → Validate CFBundleShortVersionString empty → fork yml 改 MARKETING_VERSION + itsuki Xcode General 直接填 Version/Build
- **5-08 reviewer demo 5 反思**：itsuki 让另一 CC 会话 review → CC 自我反思（不甩锅 VPS CC，责任在我设计）→ TODO §C 跟踪 5 个真问题

**新规则上线**：
- iOS+backend 物理 fork 模式（ad hoc 上架冲刺，不污染主项目 git）
- 教学类 Skill 待做（TODO §🛠️ Meta）
- 主项目 v1 backend 3 bug + reviewer demo 5 缺陷（TODO §🐛 + §C）

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 5（认知改变）× 多 + 模式 2（假设崩→真因 × 3 alembic）+ 模式 6（取舍 × plan 6 决策）+ CC 自我反思（不甩锅）。详见 `05_logs/raw/2026-05-07.md` + `2026-05-08_ios_上架冲刺.md`

**残**：当前卡 Xcode Validate（Version/Build 修后重 Archive）/ 截图 / ASC 元数据 / Submit / push 等 itsuki 明示 / `06_assets/icons/Tomoshibi icon.icon/{Assets/tomoshibi_flame 2.png, icon.json}` 被删（git status 显示，不知是不是 itsuki 自己手动）等拍板 restore 还是接受 / iOS+backend fork 在 DMSD 外不在 git 范围

### 2026-05-08 by [新Mac-Opus 4.7 1M-主会话]

**主题**：⭐⭐⭐ 点呼机当第 5 端 + 联动机制 12→18 条规则升级 + 11 配件型号定型(itsuki 已下单)

- **配件查证**:itsuki 发淘宝 10 张截图,要求**上网查证**不接受 CC 凭直觉判断;CC 用 WebSearch 跑 4 个并行查询验证 Pi 3A+ 接口 / PN532 接 Pi / ST25DV16K I2C / 音频组合,11 件能组装 ✅,识别 3 个真坑(ST25DV16K 没官方 Python 库 1-2 周学习成本 / PN532 在 Pi 上 I2C 不稳推荐 SPI / Pi 3A+ 单 USB 限制)
- **架构方案讨论**:itsuki 用直觉心智模型挑战 02_design 现状,被 CC 解释「设计文档双层」是 itsuki 自己以前拍板的(CLAUDE.md L33-39);CC 第 1 轮答错说「Android 缺 DESIGN_LOG」被 itsuki 当场质疑,grep 验证后承认错误 + 解释清楚双层模式;**拍板方案 A**(维持现状双层 + 加点呼机)
- **联动机制升级**:itsuki 主动发现现有 12 条规则只覆盖「设计→代码」+「数据层字段对齐」,**缺反向「代码→设计」5 端对称**;拍板加 6 条新规则 Rule 14-19(action 模式) + Rule 3 system-features 必查列表加 ANDROID + ROLLCALL_DEVICE
- **8 步全量执行**:点呼机骨架(8 文件)+ sync-rules.sh 12→18 条 + file-linkage SKILL 同步 + CLAUDE.md 双层 3→5 端 + 文档同步点清单 §11 表 + project-overview §5.7(顺手补 student_android)/ §5.8(点呼机)/ §13.1 反向规则 + hooks/README + hardware_design §2.2/§2.4/§2.5 占位回填 + bus_schedule_real.md 挪 06_assets/ + TODO.md 加 §🛰️ 点呼机 backlog
- **新规则实战触发**:跑 sync-check.sh,Rule 14(ios-business-design)+ Rule 19(design-log-to-system-features)各触发一次,验证反向规则真能用 ✅

**配件型号定型**(itsuki 已淘宝下单,~¥425 RMB):
- PN532 V3 红板 ¥26.7 / LED 模块套装 ¥10.9 / 01Studio USB 小音响 ¥29 / Pi 3A+ 透明壳 + 风扇盖 + 风扇 ¥24 / SYB-170 面包板 + 杜邦线 ¥3.57(本次新定型 ~¥94)
- 加上之前 Pi 3A+ ¥239 + ST25DV × 2 ¥47 + 电源 ¥13 + NTAG215 × 50 ¥31.9

**新规则上线**:
- 联动机制覆盖度从「设计→代码 + 数据字段」扩到「+ 代码→设计 5 端反向 + 端→共用层」
- 5 端对称结构:backend / iOS / Android / teacher_web / **rollcall_device**(2026-05-08 加)+ 物理硬件层(02_design/hardware_design.md)
- ROLLCALL_DEVICE_DESIGN_LOG 等 itsuki 拍板 D1-D6(NFC 库 / ST25DV 驱动 / TTS / SPI vs I2C / WebSocket / 设备认证)+ 配件到货后开始实装

**AC 价值**:⭐⭐⭐ — 模式 5(认知改变)× 3 处 + 模式 6(取舍三角)× 2 处 + 模式 4(v1→v2 演化)× 1 处。主线 = itsuki 用 CC 协作把"工程治理"从"有 hook"升级到"有 hook + 覆盖度审计"。详见 `05_logs/raw/2026-05-08.md`

**残**:~~版本 bump 决策~~ ✅ itsuki 否决「暂时不用 bump」/ 配件等到货 / D1-D6 拍板待 itsuki / push 等 itsuki 明示

### 2026-05-06 by [新Mac-Opus 4.7 1M-主会话]

**主题**：⭐⭐⭐ 独立 repo 模式退役 — iOS / Android 全合并回 DMSD + GitHub 双独立 repo 删除

- **背景**：itsuki 在新 Mac（kurekoduki）拉 Mac mini 5-06 push 的 46 commit + v0.8.0 tag → 看到 CC 报告里「iOS 独立 repo」表述 → 问 CC 实情 → 拍板「全部合回 DMSD，github repo 删了，给教授看不能太难看」 <!-- VERSION_OK -->
- **iOS 合并**：DMSD 16578 行 vs Tomoshibi-iOS 5347 行（4-23 后没 push），DMSD 已是 single source，无逆同步
- **Android 合并**：rsync `/tmp/check-android` → `03_dev/student_android/v1/`（85 文件 / 6945 行 Kotlin / 1MB）
- **归档** `99_archive/2026-05-06_cloud_agent_退役/`：4 元数据（STATUS / SHARED_DECISIONS / SESSION_CHANGELOG / REMOTE_AGENT_GUIDE）+ `sync-ios-refs.sh` + iOS / Android 完整 git log + README
- **5 声明性文件改**：CLAUDE.md / 文档同步点清单 / file-linkage SKILL / project-overview SKILL（§0.4 / §5.2 / §5.6 / §6.5 / §8.1 / §9.6 / §10 / §13）/ sync-rules.sh
- **GitHub repo 删**：`otogi2025/Tomoshibi-iOS` + `Tomoshibi-Android`（不可逆，git log 已存档）

**新规则上线**：
- 独立 repo 模式退役 — iOS+Android+Web+后端 全在 DMSD 单一 repo
- CC 收到「现状是什么」类问题时，先 grep/find 实地验证再用 SKILL.md 补充（这次 CC 答歪触发的 lesson）

**AC 价值**：⭐⭐⭐ — 「设计在约束下成立 → 约束变化方案跟着变」13 天试错周期（4-23 → 5-06）；项目文件总览 SKILL §8.1 + AC top 10 #9 都重写为「试错 + 退役迭代」叙事。详见 `05_logs/raw/2026-05-06.md`

**hook 实战拦截**：`pre-bash-destructive-block.sh`（5-04 凌晨加）拦了 `rm -rf 03_dev/student_android/v1/round1_handoff/` — CC 改用 rsync 跳过，让 .DS_Store 垃圾留着（git 看不到不影响）

**残**：~~版本 bump 决策~~ ✅ itsuki 否决「这算个屁的升级，就移动了下结构而已」（raw §7 dump）/ ~~push~~ ✅ commit `1f55643` + `f050c30` 已 push origin main / round1_handoff/ 里 7 个 .DS_Store 垃圾还在（可手动 Finder 删） <!-- VERSION_OK -->

### 2026-05-04 晚 by [Mac-iOS bug 修复 Opus 4.7]

**主题**：⭐⭐⭐⭐ iOS 5 个 bug 修复（2 个真机生产 bug + 1 次 CC 失职被 itsuki 戳穿 + 删 8 处蠢 placeholder）

- **AppIcon Liquid Glass 修复**（4 层失败重诊）— Xcode 26 build error `actool: None of the input catalogs contained... icon stack named "AppIcon"`。**CC 第一次走错方向回退到传统 .appiconset + v2 PNG 替换**，BUILD SUCCEEDED 假装修好 → itsuki 怒戳穿「我现在图标还是白色背景，你到底更新了没？」→ CC 重新诊断（单独跑 actool 隔离 + WebSearch Apple iOS 26 文档）→ 真根因：**Xcode 26 把 `.icon` 当单一文件 reference 处理，不能塞 `.xcassets/` 里**。修：mv `Assets.xcassets/AppIcon.icon` → `TomoshibiApp/AppIcon.icon` + 手改 pbxproj 4 处加 PBXFileReference / PBXBuildFile / PBXGroup / PBXResourcesBuildPhase
- **暗夜模式黑闪修复**（itsuki 真机晚上点页面黑一下）— `TomoshibiApp.swift:20` `.preferredColorScheme(app.isDark ? .dark : nil)` 中 `nil` = **跟随系统**，晚上系统切 dark → SwiftUI 喂 dark color scheme → view 硬编码 light token 双重渲染 → 黑闪。修：强制 `.preferredColorScheme(.light)` + 加 inline 注释标 N18 待实装
- **注册进度 5/4 → 5/5 修复** — `RegisterProgress` 硬编码 totalSteps=4（旧 4 步 JSX 抄来），后加 RegisterStep5 没跟上 → `Text("\(step) / 4")` 改 5，进度条 `* 0.25` → `/ 5.0`
- **删 8 处蠢 placeholder** — itsuki 怒怼「你写的例子太他妈蠢了」→ ApplyStubs × 6 / StayListStubs × 2 / HomeStubs × 1 全删。剧情化（祖父母宅 / 友人の結婚式 / 祖母の通院）→ 中性提示（住所を入力 / 理由を入力）
- **CommunityStubs Text + Text deprecation** — iOS 26 推荐字符串插值嵌套 Text

**新规则上线**：
- memory `feedback_no_dramatic_placeholder.md` — UI placeholder 禁用剧情化例子（demo prototype 抄到生产时必删「例：xxx」）
- memory `feedback_dont_unilaterally_revert_design.md` — CC 修 build error 不能私自回退 itsuki 主动选的新格式（先诊断根因 / 不通就报告等拍板，不能 fallback 伪装 BUILD SUCCEEDED）

**联动副发现 — IOS_DESIGN_LOG.md §6.5 矛盾**：N18「暗色模式：做 ✅」但实际未实装 → 加 TODO §B 待 itsuki 拍板（A 真做 N18 全 token 改造 / B 降级 N18 → v1.0 不做）

**残**：
- pbxproj 备份 `/tmp/pbxproj_backup_before_icon_move`（commit 前 git diff 可检视手改 UUID 正确性）
- iOS sync 脚本本机不通（`~/dev/TomoshibiiOSApp` 不存在）— 是否 clone 独立 repo / 或改脚本路径
- 真机暗夜黑闪 fix 需要 itsuki 装手机晚上验证（CC 无法验证）
- 启动 git status 残留垃圾（`.bak` × 2 / `Root/File.txt`）等 itsuki 拍板删

> **2026-05-04 深夜砍掉 5 条老条目** + **2026-05-06 砍掉 5-03 晚条目（协作模型升级）** + **2026-05-08 砍掉 5-04 上午小条目（已合并到 5-04 主条目）** + **2026-05-08 凌晨砍掉 5-04 主体 / 5-04 晚治理 / 5-04 深夜元层优化 3 条（让 5-08 reviewer_demo重做 + 5-07→5-08 跨日 + 5-08 点呼机 + 5-06 + 5-04 iOS bug 5 条上限）** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4,7,8}.md`

---

## 🤝 多会话占用（避免冲突）

*当前无并行会话占用任何文件。*

> 如启动多会话并行：在此列出谁正在改哪些文件 + 开始时间，其他会话避让。改完登记完成移走。

---

## 🚧 阻塞项

*当前无阻塞项。*

> 阻塞项 = 等 itsuki 答复才能推进的硬卡点（如 Q1/Q2 字段对齐拍板）。无阻塞时本节为空。

---

## 🔒 多会话协调规则

### 会话标识（建议命名）

`[设备-主题]` 格式：`[Mac-主会话]` / `[Mac-mini-Opus 4.7]` / `[Mac-后端]` / `[Mac-iOS]` / `[Mac-Android]` / `[Mac-Web]` / `[Code-Agent]`。

### 避免冲突的硬规则

1. 每个「占用」任务必须标出涉及文件 / 目录
2. 其他会话不能动正在被占用的文件
3. **共享文件**（`CLAUDE.md` / `WIP.md` / `progress_overview.md` / `CHANGELOG.md` / `TODO.md`）：一次只能一个会话改，改完立刻 commit + push
4. 改 `WIP.md` 本身：先 pull，改完立刻 push
5. git conflict：停下来问 itsuki，不自己猜合并

### 关键文件边界

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | Web 会话 |
| `03_dev/device/` | 设备会话（Pi）|
| `01_specs/` | 一次只允许一个会话改（规格冻结区）|
| `00_admin/` | 主会话管理 |
| `05_logs/raw/` | 各会话写自己今天的，文件名不撞 |

---

## 📝 给新会话的上下文（关键信息）

读完 `CLAUDE.md` + 本文件 + `TODO.md` 顶部应该知道：

1. **当前版本**：见上方 + `CHANGELOG.md` 顶部
2. **上线姿态**（4-19 G2 决策）：取消分阶段；v1.0 直接 iOS + Android + 卡 一次上线
3. **防作弊核心**：动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ ECDSA 签名 + 老师监督 + 语音播报（原创设计 → `05_logs/decision_log.md`）
4. **版本体系**：0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**：CC 侧 `00_admin/CLAUDE_CODE_记录指南.md`；总章 `AC入试记录指南_v3.md` 在 iCloud（CC 不读）
6. **文件地图**：`CLAUDE.md §目录结构` + `00_admin/文件结构指南.md`
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策他拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04 上午** — 加 2026-05-04 会话条目（A+B 文件联动工具建设）
- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- 更早历史 — 见 `git log -- 00_admin/WIP.md`
