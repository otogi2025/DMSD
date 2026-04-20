# Changelog

> **最后更新**: 2026-04-20（v0.3.1 发布 — AC readiness 文档层 + 文档同步机制 + backlog 10 ✅ / 11 ⏳）
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

## [0.3.0] - 2026-04-17 晚（spec 主体 rewrite）

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

## [0.2.0] - 2026-04-17 晚

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
