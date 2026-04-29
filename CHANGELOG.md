# Changelog

> **最后更新**: 2026-04-29（**v0.4.0 + v0.5.0 双 minor 闭合** — 4-21 至 4-29 9 天累积一次性 close；文件名 `_v0.1` 去后缀；**版本管理 SOP 建立**解决"不会迭代"问题，详见 `00_admin/版本管理SOP.md`）
>
> 版本号规则：[语义化版本 (SemVer)](https://semver.org/) — 主版本号.次版本号.修订号
>
> **本项目约定**：
> - `v0.x.y` = 开发阶段，`0.x` 本意就是"不稳定，什么都能改"
> - `v1.0.0` = 系统在宿舍正式上线运行（对外第一次兼容性承诺）
> - spec 实质内容未变的版本 bump = patch（`0.0.y` / `0.x.y`），只有"新范围进来"才 minor bump
>
> **pre-0.1 的追认**：下方 `0.0.x` 系列是在 2026-04-17 回溯 chat log 后补标的。
> 原始迭代发生在 ChatGPT 对话里，未进入 git（见 `05_logs/raw/2025-12_NFC系统早期设计对话.md` 节选）。
> 打这些标签的目的：让"讨论了十几种方案才写第一版文档"这件事有可追溯的证据链。
>
> **2026-04-20 更新**：10 个 pre-0.1 annotated tag（`v0.0.1` - `v0.0.10`）已追认打在 initial commit `3baa168` 上，每个 tag message 里写了对应版本的核心内容 + 指向 CHANGELOG / raw 的指针。`git tag -l | sort -V` 可以看到完整版本历史。

---

## [0.5.0] - 2026-04-29（Demo 4-28 sprint 落地 + 跨会话同步机制 + 学号 6 桁体系）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：本版本完成 demo-4-28 sprint 全套（D1-D2-D3 + demo-day fix + web 收尾），属于 03_dev/ prototype 大幅扩展（条件 4 minor 触发）+ 学号 6 桁体系是业务规则改动（条件 1 minor 触发）+ 跨会话同步规则 A+B+C 是新决策机制（条件 5 patch 触发，叠加上面 = minor）。
>
> **6 commit 归入本版本**：`d517cef` / `78aa611` / `57bc394` / `da959ef` / `0c8362c` / `9aedd36`（4-22 18:31 → 4-29 13:06）。
>
> **首次执行版本管理 SOP** — 本版本 close 是 SOP 建立后的第一次实践，CHANGELOG / WIP 头部 / 版本演变一览 / vX.Y.Z_AC叙事 / raw 当日 dump / git tag 6 处联动同步。

### Added — Demo 4-28 sprint 全面落地

**Web Round 3 完整 prototype**（`03_dev/teacher_web/round3/`）:
- 12 组件 + 3 vendor + 130 字体（base64 inline）+ 32 MB single-file U 盘版
- 学生アカウント管理页面（`accounts.jsx` + ACCOUNTS seed 24 人 + Shell nav + modal 2 tab）
- login / dashboard / live 座席表 / override modal / roll-call landing
- カレンダー仿 iOS（月グリッド + 选择日列表 + ＋追加 modal 复用 ModalShell）
- リクエスト曲管理（男女寮分け + 提出順 + 承認/拒否 workflow + #番号 寮×朝/晩 4 組合別自動採番）
- 主页ショートカット URL 自动检测 LAN IP（demo_server.py /api/server-info + manual fallback）
- 男寮新教员（新股 / 小林 / 難波 + 姓后先生统一）+ applications.jsx 承認 workflow

**iOS Round 1 落盘**（`03_dev/student_ios/`）:
- `IOS_DESIGN_LOG.md`（303 行，决策归档）+ `Round1_Prompt.md`（878 行，73 画面 Phase A+B 一次出）+ 4 参考图
- 3 按钮 nav + Home omnibus + 中央点呼 sheet（iOS 26 Liquid Glass）+ 注册 4-step + 锁定升级 5 阶段 + 长按 breadcrumb
- Phase B v2 HTML（Tomoshibi_iOS_PhaseB_v2.html，QA 修 C1+C2）
- 推翻 Xcode 壳方案 → Demo 当天 Safari 直开（itsuki 拍板，CC 30 行 SwiftUI 工程废弃）

**学号 6 桁体系**（D3 拍板）:
- 学年 × 組 × 番号、中高一貫 6 年制、A=01/B=02
- リュウ イヒ demo seed: 00 → **060218**（高3 B 18）
- DEMO_SEED_NO=060218 单源 + sid-based 判定 + accounts.jsx 番号列 70→130px

**跨会话同步机制 A+B+C**（D3 建立）:
- `02_design/system_features.md` 新建 = iOS+Web+後端共用真值（"単一真値"）
- `bin/sync-ios-refs.sh` 建立（DMSD → Tomoshibi-iOS/refs/ 物理コピー）
- CLAUDE.md §跨 repo 同步规则（明文 ルール）
- 解决问题：Tomoshibi iOS Swift 实装在独立 repo（cloud agent 取不到 DMSD），需物理 copy

**点呼机软件代替方案**（4-22 砍 Pi 后）:
- `demo_server.py` + polling TTS（iPad Safari Web Speech API 日语播报 / fallback Mac `say -v Kyoko`）
- iPhone Shortcuts + itsuki 自有 NFC 卡触发签到
- `./tomoshibi` CLI 启动整套

**学生改动履歴（监查 log）规格**（D3）:
- 学号 / 房间号 / 邮箱 / 电话 / 密码事实全记录
- 老师 Web アクティビティ履歴 tab + 学生 App 変更履歴

**房间号管理**（D3）:
- 注册时学生手入力 + v1.1 老师 Web 一括分配 drag & drop + 学生 App 自動受信

**コミュニティ 拆分**（D3）:
- 通報保留 / 宅配+忘れ物 フロント業務へ / リクエスト曲 古い順 + 寮内 BGM

**巴士实公告 + 系統**（D3）:
- 实公告 2026-03-22 保管 → `06_assets/real_samples/bus_notice_2026-03-22_特別運行便.md`
- 規格入 system_features.md §6.6（閲覧 / CRUD / 乗車名簿）

**新建文档**:
- `00_admin/demo_4-28/demo_script.md`（286 行 demo 流程脚本）
- `00_admin/demo_4-28/questions_for_requirements.md`（181 行问题队列）
- `00_admin/demo_4-28/scope_tier.md`（384 行 Tier 1/2/3 范围分层）
- `00_admin/文件结构指南.md`（366 行，全 repo 文件级清单 + 权限 + 反向索引）
- `02_design/system_features.md`（共用功能真值）
- `02_design/teacher_requirements.md`（老师需求文档）

### Changed — 03_dev 物理重构 + 业务规则修订

- **03_dev 物理重构**（D3）: `demo_4-28/` 嵌套解除 → `03_dev/{backend, teacher_web, student_ios, device}/` 平置化 + 27 MD 文件 path 引用更新 + `03_dev/LATEST.md` 新建（最新 HTML 索引）
- **HTML build 顺序明文化**: jsx 改 → `rebuild.command` → `build_single_file.py` 三段
- **CLAUDE.md §账号规则 patch v3**（推翻 4-20 议题 C "入学日面签确认"）: App 内 4-step 注册即激活 + 锁定升级 5 阶段 + 账号 ID 分配（00 demo seed / 01+ 真实）+ 密码重置走宿管后台
- **demo-day fix**（4-29）: リュウ イヒ 060218 対齐 / 部活合宿→外宿 / 宿監→寮監 / 巴士平日登校便 寮発→岡山駅西口発 7:30 / roster 削减 4 男+3 女 + ghost student 全清扫 5 名 5 房间号 / 全页面 maxWidth 砍 9 容器 → iPad/Mac 浏览器自适应

### Fixed — Demo crash + 文案细修

- **crash bug 修 2 处**: startSession seeded[8] / NotificationsPage roster[3]（hardcoded index 不防御短 roster）
- **白屏 debug 2 次**: file:// CORS（integrity/crossorigin strip）+ Round 2 数组越界（roster 13 人但 statuses 12 项 → `i % len`）
- **日语 native 文案审查**: 名単→リスト / 距 X まで→X まで残り / 晚→晩 / スプレッドシート×入力→食数の自由記入可 / 名前搜索 normalize 去空格 等约 12+ 处中文残留修正
- **细部文案 4 件**（4-29）: 匿名建議 自販機 / 記録 Shortcut→スマホ / override 閾値超で入寮→定刻に間に合わず / 期限後→期限内
- **デフォルト中文回答漂移** 自我观察 → memory `feedback_default_chinese_response.md` 新建（多次纠正"做日语 UI 时 CC 整段日语漂移"）

### Added — 4-29 close 时一并完成（v0.5.0 范围内）

**版本管理 SOP 建立**（解决 "4-21 → 4-29 9 天没 bump" 问题）:
- `00_admin/版本管理SOP.md` 新建（运行手册 — 当前版本 / 决策树 / 5 步 bump 流程 / 联动文件清单 / commit 前缀 / 多会话协调 / 30 秒判断 / 12 节）
- 和 iCloud `00_通用指南/版本管理实践指南.md`（教科书）明文分工
- **让 Claude 必读 SOP 的 4 层机制**：
  1. CLAUDE.md inline "版本号操作核心 5 条" + 触发条件清单
  2. WIP.md 头部第一行 `**当前版本**: vX.Y.Z`（带 VERSION_OK 豁免）
  3. pre-commit hook 检测 `01_specs/` / `02_design/` 改动 → "考虑 bump" 提醒（非阻塞）
  4. CLAUDE.md §会话结束 加第 4 项 "版本 bump 判断"（30 秒决策树）

**文件名 `_v0.1` 去后缀**（按 iCloud 版本管理实践指南 §5）:
- 11 个文件 git mv（+ 1 个 mv 处理 untracked）：API_CONVENTIONS / DEVICE_REGISTRY / ENUM_REGISTRY / ERROR_CODES / FIELD_REGISTRY / RollCall_Spec / flow_design / hardware_design / system_features / teacher_requirements
- 36 个活跃文档 perl 批量替换引用（保留 5 类历史快照例外：raw/* / vX.Y.Z_AC叙事 / progress_overview_draft / Batch3 / 99_archive）
- `v0.1_冻结决策.md` 保留（合法历史快照命名）

**v0.4.0 + v0.5.0 双 minor close**（4-29）:
- CHANGELOG 头部 + [0.4.0] 段 + [0.5.0] 段（一次性 close 4-21 至 4-29 9 天累积 15 commit）
- `00_admin/v0.4.0_AC叙事.md` + `00_admin/v0.5.0_AC叙事.md`（按 v0.3.0 模板 6 节）
- `00_admin/版本演变一览.md` 加 v0.4.0 + v0.5.0 段 + 路线表更新
- `00_admin/文档同步点清单.md §9` 文件名版本号规则
- `00_admin/文件结构指南.md` 加 SOP / 02_design 新文件 / AC 叙事

### Notes

- **本版本仍是 demo prototype 阶段**（Web HTML + iOS HTML + ./tomoshibi CLI），不是生产代码。`v1.0.0 = 系统在宿舍正式上线`目标不变
- **Demo 4-28 当天**（2026-04-28）by itsuki 实际执行结果 → 见 `05_logs/raw/2026-04-28*.md`（如有）/ `00_admin/demo_4-28/post_mortem.md`（如有）
- **跨会话改動履歴**: Tomoshibi-iOS 側 `STATUS.md` + `REMOTE_AGENT_GUIDE.md` 设 "最近の改动 log" section
- **AC 素材新增**: `raw/2026-04-22_iOS前端设计_Round1.md` + `raw/2026-04-23.md`（10 section + AC 候补 🌟 5 件）+ `raw/2026-04-24.md` + `raw/2026-04-29.md`（10 section + AC 候补 ⭐ 5 件）
- **本版本是项目第一个 "stakeholder-facing" 版本** — v0.5.0 AC 叙事文件指出这是 AC 叙事核心素材的特殊地位
- **首次执行版本管理 SOP** — close 流程跑了 SOP §3 五步 + §4 联动 6 处（CHANGELOG / WIP 头部 / 版本演变一览 / vX.Y.Z_AC叙事 / raw / git tag 等 itsuki 拍板）

---

## [0.4.0] - 2026-04-22 17:00（系统正式命名 Tomoshibi + S 系列 spec 闭合 + Device_Contract 骨架）

> **为什么 minor bump**（对照版本管理 SOP §2 决策树）：S 系列 spec 漏洞批量闭合（S1/S2/S3/S4/S7/S9/S10/S11/S12/S13/S14/S16/S19/S20）= 改了字典 + spec 主体（条件 1+2 minor 触发）+ Device_Contract 骨架是新设计层（条件 3 minor 触发）+ Tomoshibi 命名是 patch 但叠加上面归入 minor。
>
> **9 commit 归入本版本**：`2e49878` / `9d1cecf` / `eeb39d2` / `c8e05ea` / `b77b12a` / `71ffb38` / `d02ba18` / `00e5aab` / `8a9d226`（4-20 22:53 → 4-22 17:00）。
>
> **历史回顾**: 本版本 4-21 时标 `[0.4.0-wip]` 启动，但拖了 9 天没 close（直到 4-29 SOP 建立后回头追认 close）。教训：wip 状态有 deadline，不能拖。

### Naming — 系统正式命名 **Tomoshibi**（灯火 / ともしび）

**决策**（4-21 拍板）：
- **项目名**（repo / 开发代号 / AC 叙事项目名）保留 **DMSD**（Dormitory Management System Digitalization）
- **系统/产品名**（面向用户、学生 App、老师 Web、点呼机终端品牌、对管理员/教授文案）定名 **Tomoshibi**

**理由**（itsuki 定版 AC 面试话术）：
> "我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"

### Added — spec 实质改动

**字典扩**（`01_specs/rollcall/` 多文件）:
- `ENUM_REGISTRY` 新增 enum 值（修 S1/S2/S3 字典缺）
- `FIELD_REGISTRY` 新增字段（card_uid / student_status 等，修 S2/S3/S4）+ 禁止字段溯源（修 S20）
- `ERROR_CODES` 响应约定（修 S19/S20）
- `API_CONVENTIONS` 48 → 240 行扩写（URL / 动词 / 幂等 / 分页 / 日期 / 命名 / 状态码 / error.detail，修 S13）

**v0.4.0 开工启动**（4-21 上午）:
- `00_admin/v0.4.0_S2_S3_字段draft.md`（S2 card_uid 完整定义 + S3 student_status 4 取值 ENUM + 配套生命周期字段）
- `00_admin/v0.4.0_Device_Contract骨架.md`（210 行，9 节骨架 + OQ1-9 Open Questions：mTLS / nonce+HMAC / HTTP 超时 / device 注册 / 心跳 / 降级策略 / 固件更新 / LED 语义 / path_type 扩展）

**4-19 项目审查 backlog 剩余抽取**:
- `00_admin/漏洞_剩余清单_2026-04-21.md`（38 条分 D / S / T-L 三段 + 权限标签）
- 解决"backlog 87 条体量太大下次会话不知从哪开始"问题

**版本演变一览升级**:
- `00_admin/版本演变一览.md` 详细版（每个变化单独一句话解释，覆盖 18 tag + 补 v0.1.0 - v0.1.3 四个遗漏 tag）

**memory**:
- `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/project_naming_tomoshibi.md`（跨会话 memory）

### Changed — 全局系统名同步 + spec 主体修补

- `CLAUDE.md §项目信息` 第一行区分项目名 vs 系统名 + AC 话术定稿
- `README.md` 标题改 "DMSD → Tomoshibi（灯火）"，新增"为什么叫 Tomoshibi"段
- 所有面向用户 / 面向教授的文档（spec / design / demo_4-28 材料 / AC 叙事 / backlog / 面试准备索引）同步更新 Tomoshibi
- spec 主体 `RollCall_Spec` §7 + §10.2 修漏洞（S1/S4/S7/S10）
- 项目 / 仓库 / git 历史 / commit 上下文继续用 DMSD
- 早期 throwaway iOS 代码（`03_dev/Student/DMSDStudentApp*`）不改（本就是待归档产物）

### Fixed — backlog 收口

- ✅ S1 / S2 / S3 / S4 / S7 / S9 / S10 / S11 / S12 / S13 / S14 / S16 / S19 / S20（14 条 spec 漏洞批量闭合）
- ✅ L10（FIELD_REGISTRY 禁止字段溯源）
- ✅ D21（CHANGELOG v0.2.0 / v0.3.0 header 加 HH:MM 时间戳精化）

### Notes

- **不含代码 / 不动 spec 主体大改**（仍是 spec-only 项目状态）
- **Device_Contract** 仍是骨架阶段，9 个 OQ 等 itsuki 拍板（部分留 v0.5.0+ 解决）
- **Tomoshibi 命名落地** 跨 30+ 文件同步，但 git 历史 / spec 文件名 / 项目代号继续 DMSD（双层不冲突）
- **首次跨会话并行下半天**: [Mac-主会话] 修 spec + [Mac-另一会话] 议 Tomoshibi 命名，commit 分工不冲突

---

## [0.3.2] - 2026-04-20 深夜（v0.3.1 post 持续推进 + 议题 D 结论 + 架构决策推翻 4-19 部分）

> **为什么 patch bump**（对照版本管理指南 §2 / §3 + CHANGELOG 自身约定 "spec 实质内容未变 = patch"）：
> 1. `RollCall_Spec_v0.1.md` 主体**没改一行** —— 所有新决策落在 `02_design/`（新文档层）+ `CLAUDE.md`（元规则 / 项目信息）+ `raw/`（AC 素材），spec 主体留给 v0.4.0 闭环
> 2. 和同日早些的 v0.3.1 patch 判断**保持一致性**（v0.3.1 新建 10+ 文档文件也是 patch）
> 3. 保留 v0.4.0 名额给原 roadmap `spec 层闭环 + Device_Contract + S1-S7 修复`
>
> **两会话并行协调成果**：今日 DMSD 仓库有两个并行 CC 会话 —— `[Mac-主会话]`（8 commit，持续推 backlog）+ `[Mac-议题讨论会话]`（1 commit `d8be72b`，推 5 议题 A-E）。通过 commit 分工 + 不覆盖对方文件协调。两会话未冲突。

### Added — 12 个新建文件

**设计文档层**（`02_design/`）:
- `02_design/flow_design_v0.1.md`（324 行）— 签到端到端流程 + 攻击路径 + 防御机制
- `02_design/hardware_design_v0.1.md`（260 行）— 硬件选型 + 采购清单 + keystore 备份方案

**AC readiness / 面试准备**:
- `00_admin/AC_提交_checklist.md` — 5-10 月每月 gate + 技术/AC 叙事双线 + 滑动条件降级
- `00_admin/面试准备_索引.md` — 6 大类 42+ 题目 + 素材指针 + 教授追问模板
- `00_admin/v0.3.0_AC叙事.md` — CLAUDE.md "版本 bump 触发 AC 记录" 首次落地 + 未来模板

**基建 / 评估文档**:
- `LICENSE` — All Rights Reserved + AC 后 4 方向评估表
- `00_admin/T2_iOS归档_dryrun评估.md` — 3 方案对比 + 推荐 A + 完整执行命令（不执行，待授权）
- `00_admin/v0.4.0_S系列spec漏洞优先级分析.md` — 20 条 S 分 MVP(7)/Nice-to-have(8)/Defer(5) + Week 1-3 节奏 + 总估 15-20 小时

**AC 素材 / 读者导航**:
- `05_logs/raw/2026-04-20.md`（958 行）— 下午议题讨论会话 AC 素材，14 条 / 10 #AC候选
- `05_logs/raw/2026-04-20_v0.3.1发布执行.md` — 本主会话 AC 素材，4 条 #AC候选
- `05_logs/raw/README.md` — 给教授/访客的 raw/ 目录导航
- `05_logs/dev_log/2026-04-10_空白期反思_索引.md` — 指向 iCloud 反思原文（不泄露私密）

### Changed — 元规则 / 基建修订

**CLAUDE.md**（两会话各自改一次）:
- §项目信息 技术栈细化（BTR / App Links / Pi 4B 2GB / ST25DV16K / Android 10+）+ 防御核心 + 硬件流程权威源指针
- §项目信息 **推翻 4-19 G2 "一设备一账号"决策** → 改为"任意设备签名 + 入学日老师扫码面签确认"（下午议题 C 新决策）
- §项目信息 keystore 备份方案定稿（Mac + 服务器加密压缩包 + 纸质密码 + 不存 iCloud）
- §目录结构 `02_design/` 加注释
- §对话规则 **新增第 5 条 "讨论=产出，不等会话结束"**（itsuki 元规则 + memory `feedback_discuss_means_produce` 新建）

**记录指南**:
- `CLAUDE_CODE_记录指南.md §2` 去 `date` 命令冗余（改为读 env prompt `currentDate`）
- `CLAUDE_CODE_记录指南.md §12` raw 命名规则改为 3 步判断决策树（D26 + L6）

**基建**:
- `.gitignore` 从 18 行扩到 ~80 行（Python/Node/Android/IDE/日志/OS/SQLite/.claude 本地设置）
- `00_admin/create_local_dev_symlink.sh` 加 26 行头部注释 + 两层自检（Mac vs VPS 场景判别）
- `00_admin/TODO.md` 新增 4 条（宿舍综合官网 / keystore 备份 / 异常行为检测 v0.6.0+ 推迟 / 毕业交接包 2028-01）
- `CHANGELOG.md` 头部加 2026-04-20 pre-0.1 tag 追认说明

### Fixed — 架构决策推翻 + backlog 收口 14 条 ✅

**推翻 4-19 G2 两条**:
- "一设备一账号" → 取消（议题 C，改老师面签）
- "Phase 2 静态 NFC 贴纸" → 升级动态 ST25DV16K（议题 B，URL 复制漏洞）

**backlog 打 ✅（本版本 14 条）**:
- A2（志望動機占位）/ A4（commit 消息动机坦诚在 README）/ A5（raw/README）/ A6（AC 提交 checklist）/ A9（空白期反思锚点）/ A11（AI 协作声明在 README）/ A12（v0.3.0 AC 叙事模板）/ A13（面试准备索引）
- L1 超额（10 个 pre-0.1 annotated tag）/ L6（raw 命名决策树）
- T4（.gitignore 扩充）/ T6（LICENSE）/ T8（symlink 脚本注释+自检）/ T10（payload.json PII 检查无敏感）/ T13（.claude/settings.local.json 未 tracked）
- D26（记录指南 §2 date 去冗余）

**新增 backlog ⏳ 1 条**：T2 iOS 归档 dry-run 评估完成，待 itsuki 授权执行

**标过期 🟰 1 条**：T9 Mac↔VPS 同步协议（VPS 已停用）

**新增 backlog M2 元条目**：版本管理指南 §5 / §7 / §12 iCloud 更新建议

### Notes

- **不含代码 / 不动 spec 主体** — 仍是 spec-only 项目状态
- **backlog 总进度**：✅ 25 / ⏳ 12 / 🟰 1 / 剩 49（从 v0.3.1 的 11 ✅ 升到 25 ✅）
- **git tag 追认**：本版本区间内补了 10 个 pre-0.1 annotated tag（`v0.0.1` - `v0.0.10`）指向 initial commit，完整版本历史可用 `git tag | sort -V` 查看
- **10 commit 归入本版本**：
  - `f36d10b` / `8fac003` / `d7e587e` / `85e3b21`（[Mac-主会话] v0.3.1 发布后的持续 patch）
  - `d8be72b`（[Mac-议题讨论会话] 议题 D/E 补）
  - `ca16614`（WIP 锚 v0.3.2 方向）
- **议题 E 遗留**（Demo 范围）2026-04-21 itsuki fact-check 筑波官网时间表后拍板
- **下一步 v0.4.0 minor** = 原 roadmap scope：Device_Contract + 字典补字段（S2/S3）+ spec 主体漏洞 S1/S4/S7 修复 + 其他 Nice-to-have

---

## [0.3.1] - 2026-04-20（AC readiness 文档层同步 + 文档同步机制 A+B+C）

> **为什么 patch bump**：本版本是"修正已有内容到事实一致 + 补必要的外观文档"，不新增 spec 范围。按版本管理指南 §2 / §3 属于 Patch 语义（"攒了一批小修复准备发布"）。
>
> **scope**：闭合 backlog Tier 1 Batch 1（4 项 ✅）+ Batch 2/3 draft（CC 起草待 itsuki 合并，4 项 ⏳）+ M1 文档同步机制（4-19 建立）+ A2 志望動機占位。项目审查 backlog 87 条里累计处理 10 条 ✅ + 11 条 ⏳。
>
> **路径**：v0.3.0（2026-04-17 spec 主体 rewrite）→ v0.3.1（文档同步 + AC 门面） → v0.3.2（itsuki 手笔区补完）→ v0.4.0（spec 层闭环 + Device_Contract）

### Added — 新建文件

- `README.md`（根目录，103 行）：项目门面。段落：是什么 / 为什么做 / 做到哪了 / 目录导航（推荐阅读顺序）/ 技术栈（反映 4-19 G2 决策）/ 关于 AI 协作（A11 内嵌声明）/ 升学目标（坦诚 AC 动机）
- `00_admin/原创设计_语音播报防作弊.md`（135 行）：核心原创设计 showcase。按"起点观察（宿舍代刷）→ 四步推导 → 替代方案对比 → 设计本质 → 面试原话 → 证据链"结构。第一人称叙事，不是 spec 风格
- `00_admin/AC_志望動機_素材.md`：A2 占位框架（8 个必答子问题 Q1-Q8 + 辅助素材收集清单 + 填写顺序建议 + 更新触发信号）。内容留白由 itsuki 自己填
- `00_admin/文档同步点清单.md`（M1，4-19）：版本号 / 目录结构 / 5 核心问题 / 分阶段策略的单源真值清单 + Release / Onboarding Checklist
- `00_admin/2026-04-19_项目审查_backlog.md`（4-19）：87 条漏洞 + Tier 0-4 版本路线图
- `00_admin/hooks/pre-commit` + `install.sh` + `README.md`（M1，4-19）：声明性文件版本号硬编码拦截机制
- `00_admin/progress_overview_draft_2026-04-20.md`（⏳ Batch 2a draft，待 itsuki 审合并后删）
- `00_admin/Batch3_itsuki手笔素材指引.md`（⏳ Batch 3 辅助，9 条 decision + 5 次 project_evolution 转折 + Python/PostgreSQL 补答 draft，待 itsuki 粘贴后删）

### Changed — 文档同步

- `CLAUDE.md` §项目信息 整段重写（去硬编码版本号 + 反映 4-19 G2 决策"v1.0 一次上，取消 Phase 1/Phase 2"）
- `CLAUDE.md` 新增 §文档一致性规则 章节（单源真值表 + 声明性文件清单 + 会话结束前 CC 必做 3 项 + hook 安装指令）
- `CLAUDE.md` §会话结束 扩展到 7 步 + 增加"git 后要讲 commit 内容不讲 git 工具"的前提规则（含 ❌/✅ 对比）
- `TODO.md` 头部版本号改指针 + 3 条过期 🟢 TODO 打 ✅（D14 / D15 / D16）
- `WIP.md` 多次更新（头部时间戳 4-19 → 4-20 / 最近完成 4-19 段 + 4-20 段 / 更新日志 append 6 条）
- `CHANGELOG.md` 头部加"最后更新"时间戳（D20）

### Fixed — backlog 处理（10 条 ✅ + 11 条 ⏳）

- ✅ D19 / D20 / D22 / D23 / D24 / D25 / L11 / A1 / A2 / A3 / A11
- ⏳ D1 / D2 / D3 / D4 / D7 / D8 / D9 / D10 / D11 / D12 / D13（CC 起 draft 就绪，等 itsuki 手动合并，见 Batch3 素材指引 + progress_overview draft）

### Notes

- **本版本不含代码改动**（项目仍 spec-only）
- **未 push 到 origin**：所有 commit 都在 local。itsuki 说"push" 时再推
- **raw/2026-04-20.md**（今日下午另一会话定稿 BTR + ST25DV + Pi 2GB 的 5 条 AC 素材）不在本版本 commit 里，留 itsuki 或下次会话处理
- **v0.3.2 预期 scope**：itsuki 手动合并 Batch 2 / Batch 3 draft → decision_log / project_evolution / learning_path / progress_overview 正文更新到位 → 闭合剩余 11 条 ⏳
- **M2 新增**（指南待更新）：版本管理指南 iCloud §5 / §7 / §12 与实际脱节，详见 backlog §3.6 M2，等 itsuki 手动改

---

## [0.3.0] - 2026-04-17 晚 18:53（spec 主体 rewrite）

> **为什么 minor bump**：v0.2.0 完成了字典三件套 + DEVICE_REGISTRY 的"定义层"。本版本完成"业务规则层"——把新字典实际写进 spec 主体，并新增 3 块业务规则（双路径信号流 / 4 台协调 / 改判时限+扣分联动）。是 v0.2.0 承诺的实现完成。

### Added — spec 主体新增章节
- **§1 双路径并存**：路径 A（NFC 卡 / Phase 1） + 路径 B（iPhone 静态标签 / Phase 2）双路径定义 + thin client 架构原则
- **§5.1 双路径签到信号流**：路径 A / 路径 B 的端到端流程图 + §5.1.3 防代签人防补偿
- **§9 系统组件职责** rewrite：thin client / thick server 落地到 7 个组件分工 + 引用 DEVICE_REGISTRY
- **§11.3 改判时限矩阵**（角色 × 时间）：解决附录 B.9 涉及金钱/处分字段的时间窗
- **§11.4 改判与扣分联动表**：6 种状态转换的自动 ledger 规则
- **附录 C — 4 台点呼机协调规则**（C.1-C.5）：学生归属 / session 边界 / 重复碰处理 / 物理布局候选 / 学生 → session 归属
- **附录 D — v0.2 收口清单**：附录 A/B 共 25 项的 ✅/🟡/🔄 状态盘点

### Changed — spec 主体对齐字典
- §1 概述移除"App 触碰"假设（A.1 ✅ 收口）
- §2.1 base_status 表：`exempt_range` 从 overlay 改为 base（Q1 落地）
- §2.2 overlay_badges：分两类（纯装饰型 / 改底色型）
- §2.4 底色优先级：`exempt_range` 进入排序
- §3.2 弹窗信息：`本场来自的点位（A 或 B）` → `device_id` + `path_type`（B.16 ✅ 收口）
- §5 重排：原 5.1-5.4 → 5.2-5.5，新插 5.1 双路径信号流
- §7 边界：`NOT_STARTED` / `ENDED` → 统一 `SESSION_NOT_RUNNING`；新增 5 个错误码引用
- §8.2 / §8.3：`EXEMPT_RANGE` 不再是 overlay
- §10 数据模型：rollcall_event 新增 `device_id` / `path_type` / `applied_group` / `idempotency_key`
- 所有大写状态值（`INIT/PRESENT/LATE/ABSENT/EXEMPT_RANGE`）改为小写以匹配 ENUM_REGISTRY 规则

### Notes
- 附录 A/B 仍开放项（约 9 项 🔄）留给 itsuki 拍板或 v0.4 / v0.5 继续
- spec 现 958 行，比 v0.2.0 时增加 ~280 行（新增 3 块规则 + 附录 C/D + 信号流图）
- `.pages` 原稿继续保留为历史快照，本 `.md` 是唯一真值

---

## [0.2.0] - 2026-04-17 晚 18:22

> **为什么 minor bump**：字典三件套全部重写 + `DEVICE_REGISTRY` 新建 = spec 实质改动，触达 SemVer minor 阈值。原计划的 v0.1.4（纯元工作）因此次 commit 合并了字典改动被合并到 v0.2.0 一并发布。

### Added — spec 实质变动
- `01_specs/rollcall/DEVICE_REGISTRY_v0.1.md` 新建：`device_type` 三类 / 4 台候选位置 / 注册流程 / 生命周期
- `ENUM_REGISTRY` 新增：`session_event_source` / `device_type` / `path_type` / `day_type` / `student_group` / `schedule_mode`
- `FIELD_REGISTRY` 新增：`device_id` / `started_source` / `ended_source` / `device_*` 6 字段
- `ERROR_CODES` 新增：`UNKNOWN_CARD` / `UNKNOWN_DEVICE` / `DEVICE_NOT_ACTIVE` / `NO_ROLLCALL_FOR_TODAY` / `INVALID_SIGNATURE`
- spec 附录 B.9 扩写"修改时间窗矩阵"（角色×时间，月结冻结）
- spec 附录 A.2 明确"当前假设：足球部祝休日训练导致时间与平日相同 + 待 itsuki 最终确认"

### Changed — spec 实质变动
- `ENUM_REGISTRY.base_status` 重命名（原 `background_status`）+ overlay 分两类（badge / range）
- `ERROR_CODES` 按通用/场次/签到分组 + 移除 `NOT_STARTED`/`ENDED`（用 `SESSION_NOT_RUNNING` 替代）
- `FIELD_REGISTRY` 废弃 `background_status`
- spec 附录 B.11 从 🟢 升 🟡（Phase 1 无 App 时申请流程的根本问题记入 spec 主体）

### Added — 元工作
- CHANGELOG 细粒度重建：pre-0.1 追认 6 条（2025-12 ChatGPT 方案级迭代）+ 2-02 至今每实质节点一条
- `99_archive/README.md`：10 项归档条目 + 归档原则 + 清理 SLA
- `raw/2026-04-17.md`：全项目审查（16 处文档/字典内部冲突 + 5 个外人视角担忧）+ 版本号方法论修正 + 早期 chat log 整合 + 9 项重要不紧急问题方案 + 2025-12 对话日期锁定（2025-12-19 23:11 JST）+ project_evolution 起点章节草稿

### Changed — 元工作（单源化 / 反冗余）
- `CLAUDE.md`：权限表 / 目录结构改为唯一真值源
- `CLAUDE_CODE_记录指南.md`：大幅简化，5 核心问题 / 目录边界都改为"见 CLAUDE.md"；新增 `[方法论决策]` 标签
- 元文档行数：1563 → 1362（省 201 行）

### Changed — 清理（6 项 🟢）
- 删 `05_logs/.trash_dev_log/` / `.trash_problem_solving/` / `.trash_raw/` 三个空目录
- `00_admin/Folder Structure Overview.pages` → `99_archive/2026-03-08_Folder_Structure_Overview.pages`
- `01_specs/Overview/*.docx`（2 个 Word 原稿）→ `99_archive/01_specs_Overview_原稿/`
- `.gitignore` 删 3 条过期规则（`99_archive/2025-12_早期GPT对话/` 已 tracked；`99_archive/05_logs_ac_v2归档/` 与 `全量日志/` 已不存在）
- `99_archive/2025-12_早期GPT对话/` 三个 JSON 文件正式入 git
- `00_admin/executable_dev_checklist_v0.1.md` → `99_archive/2026-04-12_executable_dev_checklist_v0.1.md`（功能被 TODO.md 吸收）
- `00_admin/目录架构.md` 删除（CLAUDE.md §目录结构是权威源；git 历史可恢复）

### Notes
- spec 主体 rewrite（§1 双路径 / §2 Q1 / §5 / §7 / §9 / §10 / 附录 C）仍未落地 → 留给 v0.2.1 或 v0.3.0
- 本 commit 由两个 CC 会话并行工作的合流产物（无文件冲突，字典与清理零重叠）

---

## [0.1.3] - 2026-04-17 上午

### Added
- `01_specs/rollcall/RollCall_Spec_v0.1.md`：把 .pages 原稿数字化为 Markdown，附录 A（7 项整理时发现的问题）+ 附录 B（18 项深度审查发现的 spec 漏洞，共 25 项）
- iCloud AC 素材第 2 层首次批量填充：10 条候选 + 候选索引
- iCloud AC 目录结构重构（扁平版与嵌套版合并，按编号分类）
- AC 入试记录指南 v3.0 → v3.1（§1 目录图、§11 起步清单修订）
- `DMSD/CLAUDE.md` iCloud 权限子表（CC 可读 iCloud AC 目录；写 03/04 需当场授权；永不写 05_产出）

### Changed
- spec 源权威性从 `.pages`（二进制，Git 无法 diff）过渡到 `.md`（可追溯）
- 修正 RollCall spec 中若干日文打字错误（おす→押す、人ってから→入ってから 等）
- spec §2 颜色优先级统一为详细版（两套写法合并）

### Notes
- 本版本是 **spec 可追溯化** 的里程碑：从此 spec 修改每一次都能被 git 看见
- spec 主体（§1 "App 触碰" 与 Phase 1 "卡触碰" 脱节）未重写 → 留给 v0.2.0

---

## [0.1.2] - 2026-04-15

### Added
- 核心架构原则：**thin client / thick server**（点呼机只搬运数据，业务判断全在后端，由 itsuki 主动提出反驳 AI 的过度配置）
- Phase 2 双路径架构：卡（RFID）+ iPhone（读点呼机外贴静态 NFC 标签 → 自己联网发后端 → WS 推回点呼机播报），不走 HCE
- iOS 第三方 App 无 Secure Element / HCE 权限的根本限制认知（Apple Pay 背后是 SE + 一次性 token）
- RPi vs ESP32 全维度重开对比 → 确认方向 A（Raspberry Pi），推翻 4-12 "已决定 RPi" 的伪决策

### Changed
- 点呼机硬件配置降级：Pi 4B 4GB → Pi Zero 2 W / Pi 4B 2GB 候选（职责最简化 → 配置需求最小化）
- 点呼机代码估计 < 100 行 Python（极简化）

### Notes
- 本版本是 **架构原则层** 的升级，spec 文件未改 → patch
- 发现 spec gap：v0.1 spec 完全没写点呼机契约（记入项目债）
- Android 版 Phase 2 方案未细化（HCE 机制与 iOS 不同，记入项目债）

---

## [0.1.1] - 2026-04-13

> **注**：本版本原标记为 0.2.0，但内容实质上仅为 **命名与元数据整理**（spec 文件实质内容未变），按 SemVer 规范应为 patch 而非 minor bump。2026-04-17 审查时更正。

### Added
- `CHANGELOG.md` 版本记录文件
- 版本管理实践指南（放在 iCloud `00_通用指南/`）
- AC 入試 三层记录体系（raw / 候选 / 成品）
- `00_admin/WIP.md` 多会话协调文档
- `00_admin/CLAUDE_CODE_记录指南.md` CC 操作手册

### Changed
- spec 文件命名统一：所有文件从 "v1.0" 重命名为 "v0.1"
- 更新 `00_admin/executable_dev_checklist_v0.1.md`：点呼主闭环增加硬件架构和分阶段说明
- 更新 `CLAUDE.md`：反映分阶段策略和版本管理

### Notes
- 本版本是 **命名与元数据整理**，spec 文件实质内容无变化
- 4-12 的设计决策（NFC 硬件 / 分阶段 / 播报防作弊 / NFC vs 二维码）未写入 spec，记录在 `05_logs/decision_log.md`
- commit hash: `3b01345` / `e637034` / `e346dca` / `43c73ec` / `91a4294` / `d89b435` / `666faf8`

---

## [0.1.0] - 2026-02-12

### Added
- 规格文档冻结：`ENUM_REGISTRY` / `FIELD_REGISTRY` / `API_CONVENTIONS` / `ERROR_CODES`
- `RollCall_Spec` 点呼行为规格（.pages 原稿）
- `v0.1_冻结决策.md`：纪律阈值（迟到 0.5 / 缺席 1.0 / 月 ≥4 罚扫 / ≥9 禁足）+ session 状态机 + 规则优先级
- 8 条验收场景
- 可执行开发清单

### Notes
- 这是项目的 **第一个正式版本基线**
- 原始文件名使用 "v1.0"，已在 0.1.1 中统一重命名为 "v0.1"
- 冻结的是 **规则与数据模型**，未冻结硬件架构 / 点呼机契约 / API 详细 schema（留给后续版本）

---

## [0.0.10] - 2026-02-08

### Added
- 学生分类（普通寮生 / 足球部 / 未分类）与点呼场次合并思路

### Notes
- 为 v0.1.0 冻结做准备的倒数第二稿
- 来源：`05_logs/dev_log/2026-02-08_学生分类和点呼合并.md`

---

## [0.0.9] - 2026-02-04

### Changed
- 全体計画改善（全体规划迭代）

### Notes
- 来源：`05_logs/dev_log/2026-02-04_全体計画の改善.md`

---

## [0.0.8] - 2026-02-03

### Added
- 点呼规格大纲（第一版成文的点呼业务规则）

### Notes
- 来源：`05_logs/dev_log/2026-02-03_点呼规格大纲完成.md`
- 这是 spec 的前身

---

## [0.0.7] - 2026-02-02

### Added
- 项目目录结构与命名规划初稿

### Notes
- 来源：`05_logs/dev_log/2026-02-02_目录结构和命名规划.md`
- 进入 git 时代前夕的工程基础

---

## [0.0.6] - ~2025-12（追认，日期不精确）

> **pre-0.1 追认**：以下版本记录的是 2025-12 ChatGPT 对话里的方案级迭代。原始记录见 `05_logs/raw/2025-12_NFC系统早期设计对话.md`。日期是大致估计，不是精确 tag 时间。

### Added
- **v2.1 加固版**：Android 碎片化对策（enableReaderMode 前台模式 + NDEF 纯文本避免系统抢占）
- ECDSA 签名格式强制统一（DER base64），避免 iOS/Android 验签不兼容
- nonce 预取池（解决弱网下 challenge→submit 的逻辑悖论）
- 内网服务发现：路由器静态 DHCP + 内网 DNS + App 内置管理员改 Base URL 入口
- 内网 HTTPS 策略：校内自建 CA 或证书 Pinning，不用"自签 + 忽略"
- 复用监控服务器的 I/O 争抢对策：PostgreSQL 数据目录必须与监控录像分盘
- PostgreSQL 备份策略：每日 pg_dump 加密 + 双地点落地
- 物理瓶颈修正：同一教室贴 2-3 个 NFC 标签并行读取，避免门口堵死
- 无 NFC 学生兜底：老师手动签到 + 临时设备登记

### Notes
- 这是 pre-0.1 最成熟的方案；之后的 v0.0.7（2-02 目录规划）开始才落纸进 git 体系

---

## [0.0.5] - ~2025-12（追认）

### Added
- **v2.1 方案**：去掉 FaceID（iPhone / Android 统一）；身份证明改为"账号登录 + 设备私钥签名"
- 后端选型：Python + FastAPI + PostgreSQL + WebSocket
- 部署方向：宿舍内网本地服务器（复用现有"监控服务器"跑该系统，尽量低成本）
- Android 支持：Android Keystore 生成 P-256 私钥（hardware-backed 优先，不强制 StrongBox）

### Removed
- FaceID / 生物识别依赖（统一 iOS + Android 不对生物识别做要求）

### Notes
- 去 FaceID 后，"防代刷"靠老师现场监督 + 单设备绑定 + 换机审批 + nonce/验签，**不靠纯技术**
- 开始明确"内网 + 不一定要公网 IP + 预算极低"的现实约束

---

## [0.0.4] - ~2025-12（追认）

### Added
- **v2 综合方案**：
  - 安全闭环：设备密钥（iOS Secure Enclave / CryptoKit）+ P-256 ECDSA + 一次性 nonce + 服务端 session 时间窗
  - 可选强化：Apple App Attest（防伪造 App/脚本）
  - 扫除拍照：水印 + 照片 hash + 设备签名证明（非单纯水印）
  - 数据模型：事件溯源（append-only）+ 状态投影（seat_status_snapshot）
  - 状态机：present / late / absent / invalid / manual_override + 规则优先级
  - 运维可靠性：学生端本地队列 + 重试 + 幂等 key；老师端 WS 断线重连 + 全量快照校准

### Notes
- v2 是第一个"可交付级"综合方案，但还依赖 FaceID（后在 v0.0.5 被去除）

---

## [0.0.3] - ~2025-12（追认）

### Added
- 学习 NXP NTAG 424 DNA 的 **SDM/SUN 动态认证机制**
- 认知："每次触碰 tap-unique"→ 后端用 AES key 验证 CMAC + 防重放计数器
- 理解"复制 tag 数据 ≠ 能伪造签到，关键是服务端验的是什么"

### Changed
- 点位防复制方案从"普通静态 tag"升级为"安全标签"候选

### Notes
- 这是关键认知突破：从"静态 ID 不能当凭证"到"需要动态认证机制"

---

## [0.0.2] - ~2025-12（追认）

### Added
- 方案改为 **iPhone 读固定点位 NFC tag**（Core NFC 原生能力）
- 服务端 session 时间窗 + 挑战/签名 + 设备绑定的基础安全模型

### Removed
- HCE 手机当卡方案（iOS 第三方 App 无 HCE 权限，Apple 只对 EEA 开放且有授权条件）

### Notes
- 第一个重大方案推翻。认知：iPhone 不能被"自制读卡器"读作卡；只能反过来让手机读标签

---

## [0.0.1] - ~2025-12（追认）

### Added
- **最初设想**：学生手机当 NFC 卡，碰一碰教室里的读卡机完成签到（灵感来自日本 NFC 自动贩卖机）
- 最初业务方案：钥匙贴二维码 = 学生信息，一人一设备绑定，老师 iPad 座位表实时亮灯
- 扣分处分规则雏形（迟到 0.5 / 缺席 1.0 / ≥4 罚扫 / ≥8 禁足）
- 扫除拍照审核 + 加分抵扣设想

### Notes
- 这是项目的起点方案，**多处被后续迭代推翻**（HCE 不可行、钥匙二维码是隐私雷、单纯水印防伪不足）
- 但业务形态（固定时间 / 固定教室 / 固定座位 / 碰一下签到 / 老师 iPad 实时亮）**从头到尾保留至今**
- 证据：`05_logs/raw/2025-12_NFC系统早期设计对话.md` 早期段落
