# 会话 C findings — 第三档长尾 + 精读（维度 11-17）

生成于：2026-05-20 ~01:03（子代理 C）

> 状态：✅ 已完成（共 50 条 findings — 🔴 19 / 🟡 19 / 🟢 12）
>
> 维度覆盖：17 精读 + 12 commit + 11 AC 时间线 + 13 AC 漏抓 + 14 跨项目 + 15 CVE + 16 测试

---

## 维度 17：逐字精读

### [C-001] 🔴 memory 路径用户名错位（/Users/itsuki/ → 实际是 /Users/kurekoduki/）

- **文件**：CLAUDE.md:205
- **描述**：CLAUDE.md 写 `~/.claude/projects/-Users-itsuki-dev-DMSD/memory/MEMORY.md` 但实际机器上是 `/Users/kurekoduki/`。检查 `/Users/kurekoduki/.claude/projects/` 下确实有 `-Users-kurekoduki-dev-DMSD` 目录而 **没有** `-Users-itsuki-dev-DMSD`。CC 按 CLAUDE.md 跟着读会 404。
- **建议改法**：`/Users/itsuki/` → `/Users/kurekoduki/`，或者改成相对引用 `项目 memory dir/MEMORY.md`。最稳是用 `$HOME` 占位。
- **严重程度**：🔴（CC 直接读不到 feedback 索引，影响每次会话规则加载）

### [C-002] 🔴 CLAUDE.md 引用 2 个 memory feedback 文件不存在

- **文件**：CLAUDE.md:63 + CLAUDE.md:69
- **描述**：
  - 第 63 行 `判断标准 / 反模式: memory feedback_design_doc_layers.md`
  - 第 69 行 `中文铁律 ... memory feedback_code_comments_chinese_strict.md`
  - 在 `/Users/kurekoduki/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/` 找不到这两个文件。
- **建议改法**：要么补齐这两个 memory 文件，要么把 CLAUDE.md 里的「memory ...」改成内联说明或指向真存在的文件。
- **严重程度**：🔴（CLAUDE.md 是 CC 必读，引用死链是规则失效）

### [C-003] 🔴 progress_overview.md 仓库结构地图严重过期

- **文件**：00_admin/progress_overview.md:340-368
- **描述**：仓库结构图列的还是 4-12 之前的结构：
  - 列了 `00_admin/executable_dev_checklist.md`，但 TODO.md 顶部说该文件 4-17 已归档到 99_archive/
  - 列了 `03_dev/Student/DMSDStudentApp(iOS)/` 早期 throwaway 代码 — 早就改成 `03_dev/student_ios/` 结构
  - 没列 `02_design/` 整个目录、`03_dev/backend/`、`03_dev/teacher_web/`、`03_dev/student_android/`、`03_dev/rollcall_device/`、`04_ops/`、`06_assets/`、`07_release/`、`docs/agents/`、`.claude/`、`bin/`、`graphify-out/` 等绝大多数目录
- **建议改法**：删整段「仓库结构地图」code block，引导到 `.claude/skills/project-overview/SKILL.md` 看真值（或全部重写贴近现状）。
- **严重程度**：🔴（progress_overview 是给「itsuki + 教授读」的快照文件，过期图给招生官看会减分）

### [C-004] 🔴 progress_overview.md 系统架构图仍含 "Phase 2 追加"

- **文件**：00_admin/progress_overview.md:42-65
- **描述**：架构图末尾还有
  ```
  Phase 2 追加:
  ┌─────────────────────────────────┐
  │ 学生手机 App (iOS + Android)     │
  └─────────────────────────────────┘
  ```
  但同一文件顶部 §分阶段策略 已经明确「**2026-04-19 G2 决策更新（取消分阶段）**」+「v1.0 直接 iOS + Android + 卡 一次上线」。同一文件内自相矛盾。
- **建议改法**：把架构图重画 — 把「Phase 2 追加」框直接整合进主系统图（学生 App 是 v1.0 第一天就有的端，不是后续追加）。
- **严重程度**：🔴（自相矛盾，给教授读时直接出洋相）

### [C-005] 🔴 progress_overview.md §阶段 4 状态过期（点呼机说"未开始"但 ROLLCALL_DEVICE_DESIGN_LOG 已建）

- **文件**：00_admin/progress_overview.md:169
- **描述**：第 169 行 `### 阶段 4: 点呼机设备开发 ⬜ 未开始` 但：
  - `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md` 已建（226 行，2026-05-08 起）
  - `02_design/hardware_design.md` 已在 5-08 把所有占位升 ✅ 定稿
  - new-feature skill 5-10 已把 4 端→5 端，加点呼机 step 5
  - CHANGELOG / WIP 里早就出现「点呼机软件层」字眼
- **建议改法**：阶段 4 改成「🔄 进行中（设计层完成，硬件采购 / Pi 上手编程 未开始）」+ 加列已完成项（hardware_design 定稿 / ROLLCALL_DEVICE_DESIGN_LOG 建立）。
- **严重程度**：🔴（进度状态完全不准，给教授读时叙事不连贯）

### [C-006] 🔴 progress_overview.md §阶段 6 / §阶段 7 还在「v0.8 推进」当前版本是 v0.8.0

- **文件**：00_admin/progress_overview.md:193-213
- **描述**：阶段 6/7 列了「v0.8 推进 / v0.8 bootstrap」字眼，但实际 v0.8.0 早 5-02 close，5-03 起又加了注册码 + 公告 + 文件联动工具（progress_overview 第 236 行表说 v0.8 之后 pending bump）。状态行没刷新到 5-19 的现状。
- **建议改法**：阶段 6/7 状态说明刷新为「v0.8 + 之后未 bump 段」+ 列 5-04/5-08/5-11/5-14/5-19 的关键产出 milestone。
- **严重程度**：🔴（进度快照过时 15 天，给招生官读会减分）

### [C-007] 🔴 README.md 状态文本严重过期（4-29 v0.5.0 写法 vs 当前 v0.8.0 已 close）

- **文件**：README.md:23-37
- **描述**：README "做到哪了" 段标头是 `截至 2026-04-29（v0.5.0）` + 列「⬜ 后端 + 生产代码 — 还没开始。iOS Swift / Android Kotlin / FastAPI 后端 实装从 v0.6 起步」。但实际：
  - 当前已 v0.8.0 + 后续多次推进未 bump（注册码 / 公告 / 文件联动）
  - 后端早已实装（BACKEND_DESIGN_LOG 1134 行 / Alembic / 8 router / 37 pytest 全 pass）
  - iOS Swift 早就网络层完整 + 字段对齐 + 实装中
  - Android Compose 也早就 bootstrap + 10 屏
- **建议改法**：README 顶部「状态」+「做到哪了」段重写到 5-19 现状。或者明确把 README 标注「这是 4-29 时点 snapshot，最新见 CHANGELOG / WIP / progress_overview」+ 加 5-19 现状段。
- **严重程度**：🔴（README 是 public repo 首屏，4-29 文本说"后端还没开始"跟实际严重不符 — 招生官读 GitHub 时第一眼看的就是这）

### [C-008] 🔴 README.md 技术栈表「老师 Web 待定」过期

- **文件**：README.md:69-71
- **描述**：README 技术栈表第 70 行写 `老师 Web | 待定（iPad 上用浏览器打开的管理界面）`。但 teacher_web v1 早就拍板 TS + Vite + Zustand，已实装 5 page + demo 接真后端。
- **建议改法**：「老师 Web」行改成「TypeScript + Vite + Zustand（已实装 5 page，2026-05-02 v0.8 起）」。
- **严重程度**：🔴（public repo 技术栈表错给招生官减分）

### [C-009] 🔴 README.md 没标系统真实状态（管理员同意采纳 / Demo 4-28 已完成 / 5 月密集推进）

- **文件**：README.md:23-37
- **描述**：README 当前完全没提：
  - Demo 4-28 已跑通
  - 管理员 4-29 已口头同意采纳
  - 5-02 三端代码层全启动
  - 注册码 + 公告 + 5 端架构（点呼机加进来后是 5 端不是 4 端）
- **建议改法**：补一段「项目近期里程碑」串 4-28 demo → 4-29 管理员同意 → 5-02 三端启动 → 5-08 硬件定稿 → 5-19 文件治理大改造。
- **严重程度**：🔴（叙事缺这段 = 看 README 的人不知道项目有多接近上线）

### [C-010] 🔴 RollCall_Spec.md 仍以 Phase 1 / Phase 2 为主叙事（已被 4-19 G2 取消）

- **文件**：01_specs/rollcall/RollCall_Spec.md:17-18, 26, 182, 203, 233, 460, 466, 586-590, 653-665, 678-679, 693, 706
- **描述**：spec §1 概述就把「Phase 1 NFC 卡 / Phase 2 iPhone」作为路径上线节奏写进表，正文 §5.1.1/5.1.2/5.1.3 + §6 角色表 + 附录 B 通篇引用 Phase 1/2。但 4-19 G2 决策已**取消分阶段**（v1.0 一次性上线 iOS + Android + 卡）。spec 是 source of truth 但跟主决策矛盾。
- **建议改法**：
  1. §1 概述改写：「双路径并存」保留，但去掉「Phase 1 / Phase 2」节奏列，改成「双路径同时 v1.0 上线」
  2. 全文搜「Phase 1」「Phase 2」→ 改成「路径 A（NFC 卡）/ 路径 B（iPhone）」或「v1.0 / v1.1」
  3. 附录 B.1 防代签段保留（人防补偿仍生效），但去掉「Phase 1 / Phase 2 时序」描述
- **严重程度**：🔴（spec 主体跟项目最高决策矛盾，且属业务规则文档不能含糊）

### [C-011] 🔴 system_features.md 引用废弃独立 repo Tomoshibi-iOS / TomoshibiiOSApp

- **文件**：02_design/system_features.md:47, 59, 61, 67, 70, 75
- **描述**：system_features.md 多处引用：
  - line 47: `iOS 在 ~/dev/TomoshibiiOSApp/(独立 repo otogi2025/Tomoshibi-iOS,cloud agent 并走)`
  - line 59-75: 跨 repo 同步规则（`bin/sync-ios-refs.sh` / `Tomoshibi-iOS/refs/` 等）
  
  但 CLAUDE.md:38 明确「2026-05-06 退役独立 repo 模式，iOS+Android+Web+后端 全在 DMSD 内」。system_features.md 还按独立 repo 写规则。
- **建议改法**：5-06 退役那段同步规则全删（§跨 repo 同步 / 物理复制 / 反向同步），改成「iOS 直接在 `03_dev/student_ios/v1/`，单 repo 同源」。
- **严重程度**：🔴（5 端协作 + cloud agent 还按废规则跑会有真实风险）

### [C-012] 🔴 ANDROID_DESIGN_LOG.md / IOS_DESIGN_LOG.md 也还残留独立 repo 引用

- **文件**：
  - 03_dev/student_android/ANDROID_DESIGN_LOG.md:6, 246, 247
  - 03_dev/student_ios/IOS_DESIGN_LOG.md:583
- **描述**：
  - ANDROID:6 `独立 repo：Tomoshibi-Android（GitHub），本地 ~/dev/TomoshibiAndroidApp/`
  - ANDROID:246-247 `Tomoshibi-Android repo 侧 refs/ 目录是物理 copy，禁止直接编辑` / `sync 脚本`
  - IOS:583 `跨 repo: Swift 实装在 ~/dev/TomoshibiiOSApp/（GitHub otogi2025/Tomoshibi-iOS）...bin/sync-ios-refs.sh 物理复制到 Tomoshibi-iOS/refs/`
  
  全部跟 CLAUDE.md:38 "2026-05-06 退役独立 repo 模式" 矛盾。
- **建议改法**：3 处全删 / 重写，统一改为「单 repo `~/dev/DMSD/03_dev/student_{ios,android}/v1/`」。
- **严重程度**：🔴（5-06 退役后规则没落地到 design log，工程层会按废规则跑）

### [C-013] 🔴 flow_design.md ASCII 图标错点呼机 Pi 4B（已 4-21 推翻为 Pi 3A+）

- **文件**：02_design/flow_design.md:71
- **描述**：flow_design.md 第 71 行 ASCII 图块写 `点呼机 (Pi 4B 2GB) ──Python 循环──> 后端`。但 hardware_design.md 4-21 已推翻 Pi 4B → 改 Pi 3A+，且 hardware_design.md §0 章节状态表+ CLAUDE.md:35 技术栈都明确是 Pi 3A+。
- **建议改法**：flow_design.md:71 `Pi 4B 2GB` → `Pi 3A+`。
- **严重程度**：🔴（硬件型号是上线关键，跨文档型号漂移最伤）

### [C-014] 🟡 CLAUDE.md / WIP.md / new-feature skill 「端数」混乱（4 端 vs 5 端 vs 三端）

- **文件**：
  - CLAUDE.md:79 「**5 端** *_DESIGN_LOG.md 引用要更新」
  - CLAUDE.md:173 表 `new-feature` 行写「**4 端**实装模板（spec→backend→iOS→Android）」
  - CLAUDE.md:195 「**5 端** monorepo + 共用层」
  - WIP.md:42 「**三端**代码层启动完毕」
  - WIP.md:43 「老师公告 **4 端**实装（iOS + Android + Web + Backend）」
  - WIP.md:44 「学生注册码 v1.0 实装（**4 端** spec...）」
  - CHANGELOG.md:3 / :20 / :38 多次「三端代码层」
- **描述**：项目实际是 5 端（iOS + Android + Web + Backend + 点呼机）— new-feature skill 5-10 也升级了 4→5 端。但多文件还在用 4 端或三端措辞。
- **建议改法**：
  - CLAUDE.md:173 改 `5 端实装模板（spec→backend→iOS→Android→点呼机）`
  - WIP.md:42 改「五端代码层启动完毕」或直接列各端状态
  - WIP.md:43-44 「4 端实装」改「5 端实装」（注册码 / 公告功能上点呼机层涉及吗？如不涉及就保留 4 端但显式说「不含点呼机」）
  - CHANGELOG.md:3/20/38 「三端」 → 「三端 app + 后端 + 点呼机」或就保留「三端 app + 后端」+ 说明点呼机层在 v0.9 / v1.0 路线
- **严重程度**：🟡（不影响代码运行但导致团队 / 招生官读时概念漂）

### [C-015] 🟡 WIP.md 「关键文件边界」表错路径 03_dev/device/

- **文件**：00_admin/WIP.md:264
- **描述**：表里 `| `03_dev/device/` | 设备会话（Pi）|` 但实际目录是 `03_dev/rollcall_device/`（`03_dev/device/` 不存在）。
- **建议改法**：`03_dev/device/` → `03_dev/rollcall_device/`
- **严重程度**：🟡（多会话占用如果按 device/ 列会出错路径）

### [C-016] 🔴 文档同步点清单 / WIP / TODO 引用「文件结构指南.md」但已归档

- **文件**：
  - 00_admin/文档同步点清单.md:68, 72-75
  - 00_admin/WIP.md:280
  - 00_admin/TODO.md:311, 661
- **描述**：4 处文件引用 `00_admin/文件结构指南.md` 作为「文件级清单 + 反向索引」的唯一真值。但实际文件已 5-04 归档到 `99_archive/2026-05-04_文件结构指南_已被项目文件总览取代/`，被 `.claude/skills/project-overview/SKILL.md` 取代。
- **建议改法**：
  - 文档同步点清单 §2 改为「文件级清单 ... 单一真值 = `.claude/skills/project-overview/SKILL.md`」
  - WIP.md:280 第 6 项「文件地图」`+ 00_admin/文件结构指南.md` 改为 `+ .claude/skills/project-overview/SKILL.md`
  - TODO.md:311 改成 project-overview / TODO.md:661 删该条（无效任务）
- **严重程度**：🔴（4 处死链 + 引用废文件 = CC 按规则跑会读 99_archive 里的过期文件）

### [C-017] 🟡 hooks/README.md §A 段误写「13 联动规则 + demo-scaffold-detect」（实际 18 条）

- **文件**：00_admin/hooks/README.md:第 11-15 行表 / §A 段
- **描述**：README 顶部讲「3 类 hook」介绍时 §A `post-edit-sync-check.sh` 段写 **18 条联动规则**（正确），但后面表里 `lib/sync-rules.sh` 行写「13 联动规则 + demo-scaffold-detect」（过时，2026-05-08 已升 18 条）。同文件内部数字不一致。
- **建议改法**：表里 `13 联动规则` → `18 联动规则`
- **严重程度**：🟡（内部数字不一致影响 trust，但功能仍能跑）

### [C-018] 🟡 hooks/README.md 缺 §B 调整记录段提到 hook G (post-edit-format)

- **文件**：00_admin/hooks/README.md
- **描述**：README 已经在 §F (project-overview check) §G (format) §I (check_overview_drift.sh) 介绍了新 hook（5-13 / 5-19 加），但「§B 砍 hook 的调整记录」段只写了 5-04 深夜砍 4 项决策，没补 5-19 新加 hook 的设计依据 / 砍权衡。
- **建议改法**：在 §B 调整记录加一行「2026-05-19 加 post-edit-format.sh + post-edit-project-overview-check.sh + check_overview_drift.sh — 见 §F / §G / §I」。
- **严重程度**：🟡（不影响运行，但调整记录不全 = AC 叙事缺一段）

### [C-019] 🟡 CHANGELOG.md 顶部「最后更新」日期 2026-05-02，但实际现在 5-19/5-20 + 多次未 bump 推进

- **文件**：CHANGELOG.md:3
- **描述**：CHANGELOG 顶部最后更新写 2026-05-02 晚 v0.8.0 close。但 5-03 起又有注册码 + 公告 + 5-04 文件联动工具 + 5-08 硬件 + 5-10/5-11/5-13/5-14/5-16/5-19 多次会话推进 — 这些没 bump 但日期戳应该更新一句「v0.8 之后多次推进未 bump，见 WIP + progress_overview」。
- **建议改法**：CHANGELOG.md 顶部加一句 `> **2026-05-19 注**: v0.8 之后累积 15+ commit 实质推进，未到 bump 触发线，详见 WIP / TODO。下个版本 bump 触发线在 ...`
- **严重程度**：🟡（CHANGELOG 是「最后更新 5-02」让招生官以为项目静止 17 天）

### [C-020] 🟡 RollCall_Spec.md 顶部「v0.1 初版冻结」+「v0.2 主体改写」措辞混乱

- **文件**：01_specs/rollcall/RollCall_Spec.md:1-7
- **描述**：spec 标题写 `# RollCall Spec v0.1（点呼仕様）`，副标题说 `v0.1 初版冻结 2026-02-12 / v0.2 主体改写 2026-04-17 / 当前文件状态: spec 主体已对齐 4-17 决策`。这导致：
  - 标题写 v0.1 但内容已 v0.2 — 是 v0.1 还是 v0.2？
  - memory MEMORY.md 也说「v0.3.0 主体 rewrite both completed 2026-04-17」— 第 3 个版本号
  - TODO.md 也说「filename still RollCall_Spec_v0.1.md (去后缀 scheduled for v0.4.0 / T3)」
- **建议改法**：把标题改成 `# RollCall Spec（点呼仕様）`（去 v0.1 后缀因为内容是滚动的），副标题改成 `> 版本流: v0.1 (2026-02-12 初版) → v0.2 (2026-04-17 主体改写) → 当前 = spec 主体 + 4-17 决策 + 4-29 38 条增量`。
- **严重程度**：🟡（命名混乱给读者增加心智成本，但 spec 内容本身仍可信）

### [C-021] 🟢 README.md 提到「v0.4.0 - v0.5.0 共 14 个版本」可能不准

- **文件**：README.md:37
- **描述**：README 写「完整版本变更记录（见 `CHANGELOG.md`，v0.0.1 → v0.5.0 共 14 个版本）」。当前已到 v0.8.0，14 个版本数字也基于 v0.5.0 时点统计 — 现在应该是更多。
- **建议改法**：改成「完整版本变更记录见 `CHANGELOG.md`」去掉具体数字（避免再漂）。
- **严重程度**：🟢（数字过时但意思清晰）

### [C-022] 🟡 system_features.md 顶部「最后更新 2026-05-03」过时

- **文件**：02_design/system_features.md:13
- **描述**：第 13 行写「最后更新: 2026-05-03(itsuki 拍板「学生注册码」§7.16...)」。但 5-04 起又有大量改动（注册码 iOS / Android 实装 / 老师公告 / 字段对齐等），文件本身应该更新过但顶部时间戳没刷。
- **建议改法**：5-04 / 5-08 等关键节点更新顶部时间戳。
- **严重程度**：🟡（时间戳过时影响信任度）

### [C-023] 🟢 ROLLCALL_DEVICE_DESIGN_LOG.md / hardware_design.md 时间线一致性 OK

- **文件**：03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md + 02_design/hardware_design.md
- **描述**：两文件交叉引用 5-08 同日定稿 — hardware_design §2.4 上下游链接到 ROLLCALL_DEVICE_DESIGN_LOG（5-08 建），互相对齐。这是好例子（其他文件可参考）。
- **建议改法**：无（保留作样板）
- **严重程度**：🟢（这条只是参考好例子，不是问题）

---

## 维度 12：commit vs 实际改动

### [C-024] 🟡 commit 8e35338 混议题（5-14 + 5-16）

- **文件**：commit `8e35338` (2026-05-16 13:40)
- **描述**：commit message 是「5-14 晚段-2 anti-ai-flavor 立项 + 5-16 工程边角清理」混 2 天 2 个不相关的议题。改动文件：TODO + WIP + raw/2026-05-14.md + 术语表.html — 涉及 4 个文件但 2 个不同议题混在一起。理想应该分 2 commit。
- **建议改法**：未来 commit 拆 — 一个议题一 commit，不混 2 天的事。
- **严重程度**：🟡（影响 git log 可读性 + git bisect 时不易回滚单议题）

### [C-025] 🟡 commit 13276e5 message 说"8 项收尾流程"但只改 3 文件

- **文件**：commit `13276e5` (2026-05-13)
- **描述**：commit message 「docs(skill+wip+raw): 5-13 接力 session 收尾 — audit 校准 + 8 项收尾流程」暗示有「8 项」工程动作落地，但 stat 显示只改了 3 文件（project-overview SKILL.md + WIP.md + raw）。「8 项收尾流程」要么是 raw 内 dump 内容（OK），要么 message 表述夸大改动量。
- **建议改法**：未来 message 不写改动量数字（让 stat 自己说话），或者写清楚「8 项」是文档化 vs 实装。
- **严重程度**：🟡（轻微 — message 不算错，只是「8 项」让读者预期是 8 个真实改动）

### [C-026] 🟢 commit 81842f4 "整理 14 文件" message 准 — file 改名都对得上

- **文件**：commit `81842f4` (2026-05-13)
- **描述**：message 「chore: 整理 14 文件 — 管理文档归位 + 老文件归档 + iOS 改名」+ stat 显示 14 files changed 真的对应 14 个 rename / archive 操作。是 commit message vs 改动对齐的好例子。
- **严重程度**：🟢（好例子，无需改）

### [C-027] 🟢 commit 8 e35338 message 长 + 详细，符合项目 commit style

- **文件**：commit `8e35338`
- **描述**：commit body 写得详细，分 5-14 段 + 5-16 段，详细描述每个文件改了什么，符合项目「不写 Co-Authored-By + 中文 commit + 详细 body」style。除「混议题」外，message 质量 OK。
- **严重程度**：🟢（好例子）

---

## 维度 11：AC 叙事时间线连贯

### [C-028] 🔴 decision_log.md 严重过时 — 停在 4-15 没记录 4-19 G2 / 4-29 反馈 / 5-03 注册码 / 5-08 硬件 / 5-11 沟通规则等大决策

- **文件**：05_logs/decision_log.md
- **描述**：decision_log.md 最新一条决策是 2026-04-15「Phase 2 架构 + 点呼机大脑选 RPi」+ 4-13 版本号体系重置。但项目 4 月底以来 1 个多月的重大决策**全没记录**：
  - 4-19 **G2 决策（取消分阶段）** — progress_overview / CHANGELOG / RollCall_Spec 都提到但 decision_log 没条目
  - 4-21 **Tomoshibi 命名 + Pi 4B → Pi 3A+ 推翻** — 也没条目
  - 4-29 **老师 38 条 / R1-R4 / 8 分阈值** — 重要决策但没条目
  - 4-29 **管理员同意采纳 + GitHub public** — 重要里程碑没条目
  - 5-02 / 5-03 **注册码 / 公告 / 三端代码层启动** — 没条目
  - 5-08 **硬件全定稿（PN532 V3 / LED / 喇叭 / 外壳）** — 没条目
  - 5-11 **cc-comm-rules / graphify / 沟通规则演化** — 没条目
  - 5-19 **project-overview 大改造 + 防漂 C 方案** — 没条目
  
  decision_log 自己说「面试前快速调取决策脉络用」— 现在面试用直接出洋相。
- **建议改法**：itsuki 主动补 4-15 之后的 ~12-15 条重大决策。CC 不能直写但可起草 draft 等粘贴。
- **严重程度**：🔴（AC 核心叙事文档严重过时 — 面试时招生官读决策脉络 = 4-15 之后空白）

### [C-029] 🔴 project_evolution.md 也停在「现在的状态(2026-04-13)」

- **文件**：05_logs/project_evolution.md:147
- **描述**：项目演变文档同样停在 4-13 (`## 现在的状态(2026-04-13)`)。4-13 之后 1 个多月的演变全无（4-19 G2 / 4-29 老师反馈 / 5-02 三端启动 / 5-08 硬件定稿 / 5-11+ 沟通规则演化）。
- **建议改法**：itsuki 补 4-13 之后的「第五次重大转折」/ 「第六次」等段。
- **严重程度**：🔴（同 C-028，AC 叙事文档严重过时）

### [C-030] 🟡 learning_path.md「即将要学(计划)」可能也过时

- **文件**：05_logs/learning_path.md:153
- **描述**：learning_path 一共 300 行，结构按时间倒序 + 计划。需要 itsuki 自己审查「已走过的路」段是否包含 4-13 之后的实际学习（Swift / Kotlin / FastAPI / Alembic / Pi 硬件 / Compose 等）。
- **建议改法**：itsuki 自己审查 + 补条目。
- **严重程度**：🟡（不一定过时，但需要 itsuki 复核）

### [C-031] 🟡 raw/2026-05-19.md 缺「## AC 信号」段（5 月各 raw 文件都缺）

- **文件**：05_logs/raw/2026-05-19.md（+ 5-11/5-12/5-13/5-14/5-16 全部）
- **描述**：CLAUDE.md «§跟 session-wrap 的分工» 规定「**实时阶段**：信号命中 → ac-radar 双写 inbox + DMSD raw 的 `## AC 信号 (HH:MM)` 段（轻量 tag）」。但 grep `## AC 信号` 在 5 月所有 raw 文件**全为 0**（除 2026-05-10.md 有 4 处）。ac-radar inbox 文件存在 + 写满了 AC scratchpad，但 raw 那一边的双写机制没真跑。
- **建议改法**：要么改 SKILL 规则（取消双写要求），要么 5-19/5-16 等 raw 补回签写入 `## AC 信号 (HH:MM)` 段。
- **严重程度**：🟡（机制设计 vs 执行不一致 — 但因为 inbox 那边有写，AC 素材没真丢）

### [C-032] 🟢 5-16/5-19 inbox scratchpad 文件存在且对应 raw 同日有详细 dump

- **文件**：`{AC_ROOT}/06_radar_inbox/ac_scratchpad_2026-05-19.md` + `2026-05-16.md` + `2026-05-16_AC评估+官网验证.md`
- **描述**：5-14 / 5-16 / 5-19 等 inbox scratchpad 文件存在且有详细模式 tag。AC 素材实际**没有漏抓**，只是没双写到 DMSD raw（见 C-031）。
- **严重程度**：🟢（好情况 — AC 素材主线没问题）

---

## 维度 13：AC 素材漏抓

### [C-033] 🟡 5-19 raw 多个模式标记但 raw 内没有 `## AC 信号 (HH:MM)` 双写段

- **文件**：05_logs/raw/2026-05-19.md
- **描述**：5-19 raw 内文有大量模式标记：
  - L4: `模式 1（派生痛点）× 1 / 模式 2 × 2 / 模式 5 × 3 / 模式 6 × 2`
  - L29: `**模式 5 — itsuki 主体性**`
  - L77: `**模式 5 — CC 元认知**`
  - L96-100: 多处模式标记
  
  但完全没有 `## AC 信号 (HH:MM)` 双写段。inbox scratchpad 那边有写但 raw 这边没双写。这违反 CLAUDE.md 实时阶段规则。
- **建议改法**：要么 itsuki 拍板 raw 不再做双写（更新 CLAUDE.md），要么 CC 在 5-20 收尾时补 5-19 raw 的 `## AC 信号` 段。
- **严重程度**：🟡（规则跟执行不一致，但 AC 素材实际有 dump 在 inbox）

### [C-034] 🟡 raw/2026-05-16.md 双题：AC 合格率评估 + 工程审计 — 但「合格率评估」单独文件，工程审计在主文件，AC 跟项目混

- **文件**：05_logs/raw/2026-05-16.md + 05_logs/raw/2026-05-16_AC合格率评估+官网验证.md
- **描述**：5-16 有 2 个 raw 文件：
  - 主文件「跨项目审计 + 大修」
  - 副文件「AC 合格率评估 + 官网验证」
  
  AC 合格率评估应该跟工程审计分开 — 副文件做了，但 inbox 那边只有一个 scratchpad 不容易分辨。
- **建议改法**：未来 inbox scratchpad 命名跟 raw 文件名对齐（一对一），便于追溯。
- **严重程度**：🟡（轻微 — 文件存在不丢但追溯成本高）

---

## 维度 14：跨项目残留

### [C-035] 🟡 Tango 4 个 skill 仍含 DMSD 字符串残留（5-16 后 4 处）

- **文件**：~/dev/tango/.claude/skills/
- **描述**：grep 计数：
  - version-bump/SKILL.md: 2 处
  - file-linkage/SKILL.md: 1 处
  - new-feature/SKILL.md: 1 处
  
  共 4 处。5-16 拍板「保留 6 skill 骨架重写适配单端 web」但 4 个 skill 内仍有 DMSD 引用未清。TODO §🛠️ G 已记跟进，但还没真清。
- **建议改法**：按 TODO §🛠️ G 边开发边清，或集中一次清完。
- **严重程度**：🟡（已记 TODO + 不影响 Tango 跑，但跨项目残留还在）

### [C-036] 🔴 SC26 4 skill 共 14 处 DMSD 残留 — 大头在 session-wrap (8 处)

- **文件**：~/dev/SC26/.claude/skills/
- **描述**：grep 计数：
  - session-wrap/SKILL.md: 8 处
  - file-linkage/SKILL.md: 3 处
  - project-overview/SKILL.md: 2 处
  - memory-write/SKILL.md: 1 处
  
  共 14 处。5-16 拍板 SC26 「轻修」但 session-wrap 8 处 DMSD 残留没清。SC26 是 itsuki 大学申请项目，跑 session-wrap skill 时会按 DMSD 流程跑（不对）。
- **建议改法**：清 SC26 session-wrap 8 处 DMSD 引用 — 优先级比 Tango 高（SC26 是 itsuki 在跑的实际项目）。
- **严重程度**：🔴（SC26 跑 skill 时 CC 会按 DMSD 流程做 SC26 — 这是 5-16 拍板的修复目标但没做）

### [C-037] 🔴 cc-project-template 6 skill 共 45 处 DMSD 残留（应该是清通用模板的目标）

- **文件**：~/dev/cc-project-template/.claude/skills/
- **描述**：grep 计数：
  - project-overview/SKILL.md: 12 处
  - memory-write/SKILL.md: 10 处
  - version-bump/SKILL.md: 9 处
  - session-wrap/SKILL.md: 7 处
  - new-feature/SKILL.md: 4 处
  - file-linkage/SKILL.md: 3 处
  
  共 45 处。5-16 拍板 cc-project-template「D 案清成真通用模板（197 处 DMSD 残留全清成占位符 / 通用骨架）」+ 实际 12 改动已落地。但 grep 还显示 45 处 DMSD 字符串 — 说明 D 案没真清干净，或者「197 处」原始计数跟现在不一致。
- **建议改法**：再次跑 grep + 清剩余 45 处。或者用脚本扫 — 因为模板项目应该 0 DMSD 引用。
- **严重程度**：🔴（5-16 拍板的清通用模板目标没完全达成，剩 45 处需要继续清）

### [C-038] 🟢 SC26 / cc-project-template / Tango 目录 + .claude 结构都齐

- **文件**：~/dev/{SC26,cc-project-template,tango}/
- **描述**：3 个项目目录都存在 + 都有 `.claude/skills/` 子目录，结构是正常的（不是空目录或损坏）。
- **严重程度**：🟢（基础结构 OK）

---

## 维度 15：依赖 CVE（已知漏洞）

### [C-039] 🟡 backend v1 用 python-jose >= 3.3.0（有 CVE-2024-33663 + CVE-2024-33664）

- **文件**：03_dev/backend/v1/requirements.txt:9
- **描述**：`python-jose[cryptography]>=3.3.0` — 3.3.0 是 2021 年版本，已知 2 个 CVE：
  - **CVE-2024-33663**: algorithm confusion 漏洞 — 攻击者可以用 HS256 key 跟 ES256 confuse / RS256 跟 HS256 confuse
  - **CVE-2024-33664**: JWT bomb 漏洞 — 解码 JWE token 时无限递归导致 DoS
  
  应该升 3.4.0+ 或换成 `pyjwt`（更主流）。
- **建议改法**：
  - 升 `python-jose[cryptography]>=3.4.0`，或
  - 换成 `pyjwt[crypto]>=2.10.0`（更主流 + 更活跃维护）
- **严重程度**：🟡（生产前必修，但 dev 期间影响小 — backend 还没真 deploy）

### [C-040] 🟡 backend v1 用 bcrypt >= 4.2.0 + 注释说「passlib 不再使用」可能漏迁移

- **文件**：03_dev/backend/v1/requirements.txt:10
- **描述**：`bcrypt>=4.2.0  # 密码哈希 (passlib 不再使用 — bcrypt 4.x 互換性)`。bcrypt 4.x 有跟 passlib 的兼容性问题，注释暗示已从 passlib 迁出。需要验证 backend 代码不再 import passlib。
- **建议改法**：grep backend 代码确认 passlib 真清干净。如果 passlib 还在引用，bcrypt 4.x 会运行时报「__about__」错。
- **严重程度**：🟡（潜在 runtime 错，但只在密码哈希调用时触发）

### [C-041] 🟢 fastapi / sqlalchemy / pydantic 版本约束合理（用 >= 软上限）

- **文件**：03_dev/backend/v1/requirements.txt:4-7
- **描述**：fastapi>=0.115.0 / sqlalchemy>=2.0.30 / pydantic[email]>=2.9.0 都是近期版本（2024 末-2025 初），且用 `>=` 不锁死小版本，pip 升级时能拿安全 patch。
- **严重程度**：🟢（依赖管理合理）

### [C-042] 🟡 backend demo 用 == 锁死小版本，跟 v1 用 >= 不一致

- **文件**：03_dev/backend/demo/requirements.txt
- **描述**：demo 用 `fastapi==0.115.0 / uvicorn==0.32.0 / sqlalchemy==2.0.36 / pydantic==2.9.2 / python-multipart==0.0.17 / websockets==13.1` 全用 `==` 锁死。如果 demo 跟 v1 跑同一个 venv，会冲突；分 venv 时是 OK 的。
- **建议改法**：demo 也改 `>=`，跟 v1 风格统一。
- **严重程度**：🟡（一致性 + 升级 patch 时能自动拿到）

### [C-043] 🟢 Android compileSdk = 36 / minSdk = 26 / targetSdk = 36 是 2025+ 标准

- **文件**：03_dev/student_android/v1/app/build.gradle.kts:8-22
- **描述**：compileSdk = 36 (Android 16) + targetSdk = 36 + minSdk = 26 (Android 8) 是合理选择。`compileSdk { version = release(36) { minorApiLevel = 1 } }` 是新写法。
- **严重程度**：🟢（依赖配置合理）

### [C-044] 🟡 iOS / Swift 没有 Package.swift / Podfile — 依赖管理方式不明

- **文件**：03_dev/student_ios/
- **描述**：grep 找不到 `Package.swift` / `Podfile`。iOS 工程依赖管理可能用 Xcode 内置 SwiftPM（不在 git 跟踪 .xcodeproj 内）或全靠系统库。
- **建议改法**：确认 iOS 工程是否用 SPM 管理 — 如果是，把 Package.resolved 进 git 跟踪。
- **严重程度**：🟡（依赖管理不可见 = 别 dev 机克隆后可能不能直接 build）

---

## 维度 16：后端测试

### [C-045] 🟢 backend v1 测试齐全（4 个 test 文件 + conftest，共 ~900 行测试代码）

- **文件**：03_dev/backend/v1/tests/
- **描述**：tests 目录有 4 个测试文件：
  - test_smoke.py (389 行 — 主烟雾测试)
  - test_registration_code.py (206 行 — 注册码 12 用例)
  - test_demo_reviewer.py (166 行 — reviewer 后门 / demo 流)
  - test_announcements.py (149 行 — 老师公告 6 用例)
  - conftest.py (156 行 — fixtures)
  
  pytest 配置 + in-memory SQLite + JWT secret 固定 + SendGrid 无效（test isolation 做好）。注释里说「37 case 全 pass」+ progress_overview §阶段 3 也确认 37 case 测试套件。
- **严重程度**：🟢（测试覆盖率合理，符合 backend brief）

### [C-046] 🟢 tests/conftest.py 测试隔离 OK — in-memory SQLite + 环境变量 isolation

- **文件**：03_dev/backend/v1/tests/conftest.py:6-12
- **描述**：conftest.py 顶部 `os.environ.setdefault(...)` 4 行 isolate test env：DATABASE_URL → in-memory SQLite / JWT_SECRET 固定 / SendGrid 关 / APP_ENV=dev。这是合规 pytest practice。
- **严重程度**：🟢（好实践）

### [C-047] 🟢 关键路径覆盖：auth / registration / announcements 全有专用测试

- **文件**：03_dev/backend/v1/tests/
- **描述**：关键 endpoint 都有对应测试文件：
  - 注册码：test_registration_code.py
  - 公告：test_announcements.py
  - smoke：test_smoke.py 应覆盖 auth / health
  - demo/reviewer 后门：test_demo_reviewer.py
- **严重程度**：🟢（关键路径覆盖好）

### [C-048] 🔴 没有 CI/CD `.github/workflows/` 跑 pytest 自动验证

- **文件**：.github/workflows/（不存在）
- **描述**：项目是 GitHub public repo + 上线前要保证 backend tests 全 pass，但 `.github/workflows/` 目录不存在 — pytest 全靠手跑。没 CI 意味着 PR 不能自动 validate。
- **建议改法**：加 `.github/workflows/test.yml` 跑 `pytest 03_dev/backend/v1/tests/`，可加 ruff / mypy。
- **严重程度**：🔴（v1.0 上线前必修 — CI 是 production-grade backend 的基础）

### [C-049] 🟡 backend v1 没有 pytest.ini / pyproject.toml 测试配置

- **文件**：03_dev/backend/v1/
- **描述**：tests/ 目录有但根没有 pytest 配置文件。pytest 默认配置可能找不到 conftest 或定位测试目录有问题。
- **建议改法**：加 `pyproject.toml [tool.pytest.ini_options]` 或 `pytest.ini`，明确 testpaths / asyncio_mode 等。
- **严重程度**：🟡（不影响跑但跨机时可能漂）

### [C-050] 🟡 backend 没有 rollcall / study / teachers / applications endpoint 的测试

- **文件**：03_dev/backend/v1/tests/
- **描述**：CHANGELOG / WIP 都说 backend rollcall + study + teachers + applications 各 routers 已实装，但 tests/ 只有 smoke + registration_code + demo_reviewer + announcements。核心业务（rollcall / study / applications）没有专用测试文件 — 这些是宿舍上线的关键功能。
- **建议改法**：补 test_rollcall.py / test_study.py / test_applications.py 各 ~150-200 行。
- **严重程度**：🟡（业务核心未测，v1.0 上线前必加）

---

## 总计

- 🔴 16 条（C-001, C-002, C-003, C-004, C-005, C-006, C-007, C-008, C-009, C-010, C-011, C-012, C-013, C-016, C-028, C-029, C-036, C-037, C-048）
- 🟡 22 条（C-014, C-015, C-017, C-018, C-019, C-020, C-022, C-024, C-025, C-030, C-031, C-033, C-034, C-035, C-039, C-040, C-042, C-044, C-049, C-050）
- 🟢 12 条（C-021, C-023, C-026, C-027, C-032, C-038, C-041, C-043, C-045, C-046, C-047）

**主题分布**：
- 维度 17 精读（C-001-C-023）：23 条 — 出活最多 ✅
- 维度 12 commit（C-024-C-027）：4 条
- 维度 11 AC 时间线（C-028-C-032）：5 条
- 维度 13 AC 漏抓（C-033-C-034）：2 条
- 维度 14 跨项目（C-035-C-038）：4 条
- 维度 15 CVE（C-039-C-044）：6 条
- 维度 16 测试（C-045-C-050）：6 条

**关键发现**：
1. **AC 叙事文档严重过时**（C-028 / C-029）— decision_log + project_evolution 停在 4-15 / 4-13，1 个多月空白，面试用直接出洋绝。
2. **README + progress_overview + RollCall_Spec 多处自相矛盾**（C-003 至 C-010）— public repo 首屏文档跟项目实际状态严重不符。
3. **5-06 退役独立 repo 决策没落地到 system_features / IOS_DESIGN_LOG / ANDROID_DESIGN_LOG**（C-011 / C-012）— 跨 repo 同步规则废了但 design log 还在按废规则跑。
4. **memory 路径用户名错位**（C-001）+ **2 个 memory feedback 文件死链**（C-002）— CC 每次会话按 CLAUDE.md 跑都 404。
5. **跨项目 197 处 DMSD 残留**（C-036 / C-037）— SC26 14 处 + cc-project-template 45 处，5-16 拍板的清理目标没完全达成。
6. **CI 缺位 + 核心业务无测试**（C-048 / C-050）— v1.0 上线前必修。

**优先级建议**：
1. 立刻修 C-001 / C-002（CLAUDE.md 死链路径错） — 影响每次会话
2. C-003-C-013 一组 — public repo 首屏 + 业务规则文档统一改一遍
3. C-028 / C-029 — itsuki 自己补 AC 叙事缺口（CC 起草 draft 等粘贴）
4. C-036 / C-037 — 清剩余跨项目残留
5. C-048 / C-050 — v1.0 上线前补 CI + 核心 endpoint 测试
