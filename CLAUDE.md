# DMSD 项目指令（CC 必读）

## 关于 itsuki

- 中国人，日本高中三年级，2026 年 4 月起进入高三
- 完全零基础，没有系统学过编程，所有概念要从零解释
- 目标：筑波大学 情報学群 情報科学類 AC入試（2027 年 4 月入学）
- DMSD 是她的核心 AC 叙事项目

## 语言规则

| 场景 | 语言 |
|---|---|
| 日常对话、解释概念 | 中文 |
| 英文术语、命令参数 | 中文解释含义（如 `git commit` = 提交记录）|
| 日语专业词 | 标注中文意思 |
| AC 自我推荐书 / 志望理由书内容 | 日语 |
| 面试模拟 | 日语 |
| 代码注释 | 中文 |
| Git commit message | 英文（简短）+ 中文正文可选 |

## 项目信息

- **项目名**：DMSD（Dormitory Management System Digitalization）— 开发项目 / 仓库代号 / AC 叙事项目
- **系统/产品名**：**Tomoshibi**（灯火 / ともしび）— 面向用户的系统名，2026-04-21 拍板
  - 使用场景：学生 iOS / Android App 名字、老师 Web 标题、点呼机终端品牌、README / 介绍文案、对管理员/教授的所有表述
  - 保留 DMSD 的场景：项目开发过程、git 历史、spec / commit / 版本号、CLAUDE.md 这类"对 CC 的项目指令"
  - **AC 面试话术**（itsuki 原话定版）："我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。所以取日语名 Tomoshibi（灯火）。"
- 核心：宿舍点呼数字化（NFC 签到 / 自动判定 / 纪律扣分）
- 技术栈（2026-04-20 议题 A/B/C 细化）：
  - iOS（Swift / SwiftUI，**BTR + Universal Link + AASA** 实现"碰一下自动唤 App"）
  - Android（Kotlin，**App Links + assetlinks.json** + 自建 APK 分发，最低支持 **Android 10+**）
  - 后端（FastAPI / Python / PostgreSQL，托管域名 `dmsd.otogi2025.com` 或同类）
  - 点呼机（**Raspberry Pi 3 Model A+ + Python**，I²C 接 **PN532 卡读头** + **ST25DV16K 动态 NFC 贴纸模块**；**2026-04-21 推翻 4-20 Pi 4B 2GB 选型**，原因：thin client 用不上 over-spec + 实际市场价 ¥500 太贵 + Pi 3A+ 双频 WiFi + 3.5mm 音频口内置）
  - NFC 卡（NTAG215 空白卡，学生自贴名字）
- **防御核心**（2026-04-20 议题 A 定稿）：ST25DV16K 每 10 秒刷新一次性 nonce（URL 复制无效）+ ECDSA 签名（私钥存 Keychain/Keystore 硬件级）+ 老师现场监督 + session 幂等
- **账号规则**（2026-04-22 Demo 简化修订，**推翻 4-20 议题 C "入学日面签确认"**；4-20 议题 C 的"不锁定单设备"原则沿用）：
  - **注册**：App 内 4-step 流程（氏名 + 生日 + 性别 + 学生类别 一般/サッカー部 + 邮箱 + 电话 + 密码 ×2 + 头像）→ **即激活**（demo 阶段无老师面签；v1.0 可恢复面签核验）
  - **账号 ID**：系统分配 2 位数字（`00` 保留为 demo seed = リュウ イヒ / 女寮 W101 / 4 分扣分；真实学生 `01` 起自动分配）
  - **登录**：号码 + 密码，**永久保持 session** 直到主动 ログアウト
  - **密码重置**：App 无自助路径，学生必须找宿管，宿管在老师 Web 后台手动重置（⚠ 老师 Web 待加页面，见 `teacher_web/Round4` backlog）
  - **密码锁定升级**：连错 3 次 → 锁 30 秒 + 通报老师 → 解锁后再错 1 次 → 1 分钟 → 5 分 → 30 分 → 1 小时 → **永久锁死**（找宿管）；成功登录 counter 清零
  - **签到**：不锁定单设备；任意已激活设备 + 学生私钥签名即可签到；换机无需老师（学生新机登录自助，旧设备密钥自动作废）
  - **权威源**：`03_dev/student_ios/IOS_DESIGN_LOG.md §3`
- **上线姿态**（2026-04-19 G2 决策）：**v1.0 直接 iOS + Android + 卡 完整版一次上线**；取消原 Phase 1 / Phase 2 分阶段
- **开发节奏**：内部按 M1→M5 里程碑推进（兜底：做不完至少 M1+M2 可 demo）
- **4-28 管理员 demo 冲刺**（2026-04-21 议题 E 拍板 + scope 扩展 + **2026-04-22 砍硬件**）：宿舍管理员决定是否采纳系统 → 7 天冲刺（4-21 → 4-28）→ 范围 **Tier 分层**：Tier 1 真跑（点呼 / 座位表 / 改判 / 健康 / 请假 / 外宿 / 归国 / 扣分 / 检索）+ Tier 2 UI skeleton（扫除 / 巴士 / 活动 / 宿舍互动 5 项 / 快递 / 归县 / 出租车 / 通知中心 / 长期豁免）+ Tier 3 砍。**4-22 重大调整**：砍 Pi 点呼机硬件 → demo 纯软件跑（itsuki iPhone 碰自有 NFC 卡 → 后端 → iPad 座位变绿 + iPad Safari Web Speech API 日语播报 / fallback Mac `say -v Kyoko`）。**扣分规则**暂定（迟到 0.5 / 缺席 1 / 月 4 罚扫 / 月 8 禁足），后端做成 `discipline_config` 可配置表，上线前和老师商议。**权威源**：`00_admin/demo_4-28/`（文件夹，含 README.md / sprint.md / scope_tier.md / ST25DV_fallback.md / demo_script.md / **questions_for_admin.md** / **wifi_survey_howto.md**）。**分工**：本会话 [Mac-demo-sprint] 只做需求/文档/清单，代码实现交其他 agent
- **采购策略**（2026-04-22 二次修订）：**Demo 阶段 0 采购**（推翻 4-21 的"Demo 1 台 ¥12380"计划，砍硬件调试风险）→ 管理员采纳后扩容 3 台（淘宝，¥1345 RMB）。上线版硬件选型（Pi 3A+）保留在 `02_design/hardware_design.md §2.1`。详见 `02_design/hardware_design.md §4` + `00_admin/demo_4-28/scope_tier.md §0.1`
- 规格：`01_specs/` 初版冻结于 2026-02-12；后续修订进度见 `CHANGELOG.md`
- **硬件 + 流程权威源**：`02_design/hardware_design.md` + `02_design/flow_design.md`（2026-04-20 建立）
- 版本：SemVer。**当前版本见 `CHANGELOG.md` 顶部**（单源真值，见下方"文档一致性规则"节）
- **版本号 bump 时必须触发 AC 记录**（对应核心问题 #3 重大决策）
- **keystore（Android App 签名证书）备份**（议题 B 定稿）：本地 Mac 主拷贝 + 后端服务器加密备份（跨人传承）+ 纸质密码笔记本（毕业交接转交）+ 年度校验。**不存 iCloud**（个人账号不可传承）

## 目录结构

> **完整文件级清单 + 每个文件的作用 + 权限速查表 + 反向索引** 见 `00_admin/文件结构指南.md`（2026-04-21 建立，新建/改/删/挪文件时同步更新）。以下是顶级骨架。

```
DMSD/
├── 00_admin/
│   ├── WIP.md                         # 书签级，每次会话头尾读写
│   ├── TODO.md                        # itsuki 维护的全部待办 + 4-29 老师反馈 38 条 backlog
│   ├── 文件结构指南.md                 # ⭐ 文件级清单 + 作用 + 权限（每次找不到文件先查这里）
│   ├── 文档同步点清单.md               # 单源真值表 + release/onboarding checklist
│   ├── 版本管理SOP.md                  # ⭐ 运行手册 — 决策树 / bump 5 步 / commit 前缀（CC 改 spec 必读）
│   ├── progress_overview.md           # 章节级，CC 起草由 itsuki 确认
│   ├── CLAUDE_CODE_记录指南.md         # AC 记录操作手册（仅格式需要时读）
│   ├── demo_4-28/                     # 4-28 管理员 demo 需求档（sprint / scope_tier / demo_script / questions / wifi_survey）
│   ├── hooks/                         # pre-commit hook 三件套（拦硬编码版本号）
│   └── vX.Y.Z_AC叙事.md                # 每次 minor bump 后写的 AC 素材卡
├── 01_specs/                          # 规格文档（rollcall/ 字典+主体，文件名不带版本号）
├── 02_design/                         # 设计文档（hardware_design + flow_design + system_features 等，硬件+流程+共用功能权威源）
├── 03_dev/                            # 代码（backend / teacher_web / student_ios — Swift 实装在独立 repo Tomoshibi-iOS）
├── 04_ops/
├── 05_logs/                           # DMSD 开发 log
│   ├── raw/                           # CC 每日 dump YYYY-MM-DD.md（+ 历史主题文件）
│   ├── dev_log/                       # 开发日志（itsuki 自己写）
│   ├── problem_solving/
│   ├── decision_log.md                # itsuki 手写索引（CC 不写）
│   ├── learning_path.md
│   └── project_evolution.md
│   # AC 纯素材（reflection/ weekly_review/ monthly_review/ interview_log/
│   # ai_协作记录.md dmsd_app_ideas.md 证据/ ac_入試准备/）已移 iCloud，不在 git
├── 06_assets/                         # real_samples/（实公告等参考材料）
├── 07_release/
├── 99_archive/                        # 2025-12 早期 GPT 对话等
├── bin/                               # sync-ios-refs.sh 等脚本
├── CHANGELOG.md
└── CLAUDE.md                          # 本文件
```

**iCloud 路径**：`iCloud/02_学习与知识/升学/AC/筑波大学 AC入試 準備/`（结构见本文件"AC 记录协作"节）。

## 文档一致性规则（2026-04-19 加）

> **背景**：2026-04-19 itsuki 发现"迭代了几个版本但多个文件还写过期版本号"。根本原因 = "同一信息多处存储 → 必然漂移"。解法 = 单源真值 + 同步清单 + pre-commit hook 三件套。

### 单源真值（Single Source of Truth）

| 共享概念 | 权威源 | 其他文件怎么引用 |
|---|---|---|
| **最新 HTML プロトタイプ 位置**（iOS / Web）| **`03_dev/LATEST.md`** | "见 `03_dev/LATEST.md`" |
| 版本号 | `CHANGELOG.md` 顶部 + `WIP.md` 头部 | "当前版本见 `CHANGELOG.md`" |
| **版本 bump 操作流程** | **`00_admin/版本管理SOP.md`** | "见 SOP §X" |
| 顶级目录结构 | 本文件 §目录结构 | "见 CLAUDE.md §目录结构" |
| **文件级清单 + 作用 + 权限** | **`00_admin/文件结构指南.md`** | "见 `00_admin/文件结构指南.md`" |
| 5 AC 核心问题 | 本文件 §5 个 AC 核心问题 | "见 CLAUDE.md §5 个 AC 核心问题" |
| 分阶段策略 | `CHANGELOG.md` + `RollCall_Spec_*.md §1` | 用指针 |
| **iOS + Web + 後端 共用功能**（账号 / 申請 / 通知 / コミュニティ / 規律）| **`02_design/system_features.md`** | "见 system_features.md §X" |
| iOS 専属設計（視覚 / flow / Phase）| `03_dev/student_ios/IOS_DESIGN_LOG.md` | 専属項目のみ / 共用機能は system_features に |
| Web 専属設計（Ryō tokens / 老师動線）| `03_dev/teacher_web/WEB_DESIGN_LOG.md` | 同上 |

完整同步点清单 + Release Checklist + Onboarding Checklist → `00_admin/文档同步点清单.md`。

### 声明性文件（不允许硬编码版本号 — pre-commit hook 会拦）

- `CLAUDE.md`（本文件）
- `00_admin/WIP.md`
- `00_admin/TODO.md`
- `00_admin/progress_overview.md`

豁免：行末加 `<!-- VERSION_OK -->` 注释。详见 `00_admin/hooks/README.md`。

### 版本号操作核心 5 条（2026-04-29 加 — 解决"4-21 → 4-29 9 天没 bump"问题）

> **运行手册全文**: `00_admin/版本管理SOP.md`（CC 触发条件见 SOP §0 §12）。**理论 / 历史教训** 在 iCloud `00_通用指南/版本管理实践指南.md`（CC 一般不读）。

1. **当前版本** = `CHANGELOG.md` 顶部第一条 + `00_admin/WIP.md` 头部"当前版本"行（双源同步，bump 时一起改）
2. **改了 spec 主体 / 字典 / 02_design / 03_dev 主体后** → 必读 SOP §2 决策树（每条改动都判一次）
3. **decide bump** → 跑 SOP §3 五步 + 对照 SOP §4 联动文件清单（**必改 6 处**：CHANGELOG / WIP 头部 / 版本演变一览 / vX.Y.Z_AC叙事 / raw 当日 dump / git tag）
4. **commit 前缀** = SOP §5 速查表（feat=Minor 候选 / fix=Patch 候选 / docs+chore+refactor=不 bump）
5. **打 tag = 发布动作** → CC **不能自动**打 tag，必须 itsuki 明示

> **触发本 SOP 阅读的情景**（命中任一 → 立即读 SOP 对应节）：
> - 即将 commit `feat:` / `fix:` 前缀 → SOP §2 §5
> - 改了 `01_specs/` 主体或 `02_design/system_features.md` → SOP §2 §3 §4
> - itsuki 说 "bump" / "打 tag" / "迭代版本" → SOP §3 §4
> - 用户问"现在版本是多少" → SOP §1
> - pre-commit hook 输出 "考虑 bump" 提醒 → SOP §2

### 会话结束前一致性检查（CC 必做）

每次会话结束前：

1. **pre-commit 检查预演**：跑 `bash 00_admin/hooks/pre-commit`（不需要真 commit 就能看结果），有 ❌ 就提示 itsuki
2. **时间戳新鲜度扫描**：过去 7 天 commit 改过但文件头"最后更新"没动的文件 → 提醒 itsuki
3. **同步点发现**：本次会话新建了声明性文件 → 提醒 itsuki 加入 `00_admin/文档同步点清单.md`
4. **版本 bump 判断**（2026-04-29 加 — 跑 `00_admin/版本管理SOP.md §10` 30 秒 4 问）：本会话改了 spec / design / 03_dev 主体？CHANGELOG 顶部还停在 `[X.Y.Z-wip]`？累积 5+ commit 包含实质改动？itsuki 有"今天结束"信号？任一命中 → 主动询问 itsuki 是否 bump（用 SOP §10 固定话术）

### 跨 repo 同步规则（2026-04-23 加 — iOS Swift 実装は独立 repo）

**問題**: Tomoshibi iOS App の Swift 実装は独立 repo `otogi2025/Tomoshibi-iOS`（`~/dev/TomoshibiiOSApp/`）。Anthropic cloud agent が並走するため、cloud 環境からは DMSD repo を取得不可 → iOS 側から参照する設計文書は `Tomoshibi-iOS/refs/` に **物理コピー**で配置する必要がある。

**Single Source of Truth は常に DMSD 側**。`Tomoshibi-iOS/refs/` は複製品（直接編集禁止）。

**同期対象ファイル**（DMSD → Tomoshibi-iOS/refs/）:
- `02_design/system_features.md`
- `03_dev/student_ios/IOS_DESIGN_LOG.md`
- `03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB_v2.html`
- `03_dev/student_ios/designs/phaseB_src/`
- `03_dev/student_ios/designs/QA_Round1_PhaseB.md`

**同期方法**: DMSD 内の `bin/sync-ios-refs.sh` を実行 → 物理コピー → Tomoshibi-iOS 側で `git status` 確認 → itsuki が手動 commit（自動 push しない）。

**CC 必須動作**:

| 状況 | アクション |
|---|---|
| iOS 機能 / 設計を改動した（DMSD 側 LOG 更新済）| 会話末尾に `bash bin/sync-ios-refs.sh` を走らせる + itsuki に Tomoshibi-iOS 側 commit を促す |
| Swift コードで機能挙動を変えた（Tomoshibi-iOS 側）| `STATUS.md` 更新 + itsuki に通知 → 「DMSD 側 `IOS_DESIGN_LOG.md` + `system_features.md` への逆同期が必要」と明示 |
| 新機能を iOS で設計した | 先に DMSD 側 `system_features.md` + `IOS_DESIGN_LOG.md` を更新 → sync script → Tomoshibi-iOS 側で実装 |

**跨会话改动履歴**: Tomoshibi-iOS 側の `STATUS.md` + `REMOTE_AGENT_GUIDE.md` に "最近の改动 log" section を設ける。どの agent がどの feature に何を変えたか時系列記録 → 別 agent が拾える。

### pre-commit hook 安装

每个 clone 本 repo 的机器首次跑一次（Mac / VPS 各跑）：

    bash 00_admin/hooks/install.sh

详见 `00_admin/hooks/README.md`。

## 开发环境

- **家 Mac** → 本地（`~/dev/DMSD`）→ CC + Xcode + VS Code（iOS 开发）— **当前唯一开发环境**
- ~~学校 iPad → SSH 到 VPS（`~/DMSD`）~~ — **2026-04-19 已停用 for DMSD**（itsuki 决策，VPS 仍可用于学习/通用，但 DMSD 工作集中在 Mac）
- GitHub（`otogi2025/DMSD`）= 唯一远端真值；2026-04-29 起 **public**（之前 private）
- 独立 repo：Tomoshibi-iOS（`~/dev/TomoshibiiOSApp/`，GitHub `otogi2025/Tomoshibi-iOS`）— Swift 实装，与 DMSD 通过 `bin/sync-ios-refs.sh` 物理 copy 同步设计文档

## 对话规则

1. 每一步都要解释"为什么做"和"在干什么"
2. 主动告诉 itsuki 不知道但应该知道的概念（她不知道自己不知道什么）
3. 不假设 itsuki 有任何先验知识（变量 / API / HTTP / 数据库都要解释）
4. 出练习题尽量结合 DMSD 场景（点呼、扣分、签到）
5. **讨论 = 产出，不等会话结束**（2026-04-20 itsuki 新规则）— 每轮讨论完拍板重大决策后**立即**检查是否要更新 CLAUDE.md / `02_design/` 等权威文档，**当场改**，不攒到会话结束的 5 步流程里。触发点：议题切换前、推翻旧决策后、产生新技术栈/新规则时。详见 memory `feedback_discuss_means_produce.md`。itsuki 原话："我跟你讨论，最终目的是让你产出，以后别忘了记得加到 CLAUDE.md 里"

## 代码编写原则

- itsuki 决定"做什么"，CC 实现"怎么做"
- 每段代码都要向她解释含义，确保她能理解
- 她需要能在 AC 面试时解释每个模块的功能和设计原因
- CC 写出 itsuki 当时不完全理解的代码时，停下来讲清楚，记 `[分歧]` B 类（见下 AC 记录）

## 会话开始：WIP.md 必读

每次会话第一件事：读 `00_admin/WIP.md`。

- 了解当前做到哪、有哪些进行中任务、哪些文件被其他会话认领
- 遵守 WIP 里的"文件边界"规则，避免多会话冲突

`WIP.md` CC 可直接写（书签级，开销低）。
`progress_overview.md` CC 只起草，由 itsuki 确认后保存。

---

# AC 记录协作（v3 三层体系）

## 权威文档

- 本节 = CC 日常操作的全部需求，大部分会话不需要读操作手册
- 操作手册 `00_admin/CLAUDE_CODE_记录指南.md` 只在需要 dump 格式（§3.3 模板）时才读
- itsuki 侧完整章程 `AC入试记录指南_v3.md` 在 iCloud，CC 不读

## 目录边界

### DMSD 仓库内

| 路径 | CC 权限 |
|---|---|
| `05_logs/raw/YYYY-MM-DD.md`（第 1 层 CC dump）| 读写 |
| `05_logs/` 其他子项（dev_log / problem_solving / decision_log.md / learning_path.md / project_evolution.md）| itsuki 自己写的日志。CC 可读可引用，**改动前必须先告知** |
| `00_admin/CLAUDE_CODE_记录指南.md` | 只读 |
| `00_admin/WIP.md` | 读写 |
| `00_admin/progress_overview.md` | 起草（不直写）|

### iCloud AC 目录（2026-04-17 起 CC 可访问，有边界）

iCloud 根路径：`iCloud/02_学习与知识/升学/AC/筑波大学 AC入試 準備/`

| 路径 | CC 权限 |
|---|---|
| `00_指南/` | 读（`AC入试记录指南_v3.md` / 文件结构图）|
| `01_官网资料/` | 读 |
| `02_分析与调研/` | 读 |
| `03_素材_候选/`（第 2 层）| 默认不写；itsuki **当场明确授权**后可写。升级第 2 层的筛选判断权在 itsuki |
| `04_素材_成品/`（第 3 层）| 默认不写；itsuki **当场明确授权**后可写 |
| `05_产出/`（志望理由书 / 自我推荐书 / 面试准备）| **永不写**——这是 itsuki 的原创作品，AI 不参与起草 |
| `99_archive/` | 读；可写到 `99_archive/` 的新子目录（归档用途）|
| `状态快照.md` | 读；改动前先告知 itsuki |

## 触发清单（CC 每次回复前心里过一遍）

刚才这轮对话里 itsuki 是否出现下列任一条？出现就**当场问她要不要记**，不要等她主动说：

- [ ] 做了决策（选 A 不选 B，哪怕很小）
- [ ] 新想法 / 反思 / 怀疑（包括对方向的动摇）
- [ ] 遇到问题、bug、不理解的概念
- [ ] 学到新东西（语法 / API / 工具 / 概念）
- [ ] 代码、架构、文件结构发生改变
- [ ] **档案体系 / 文件管理规范 / 目录结构分层 等元思考决策**（itsuki 想"以后怎么管这一堆文件 / 怎么不让档案漂"时 → 触发**方法论级详细记录**，~1500 字，AC 价值高）
- [ ] 和真人做了访谈或讨论
- [ ] 和 CC 意见不一致 / itsuki 纠正了 CC
- [ ] CC 写出 itsuki 当时不完全理解的代码
- [ ] 版本号 bump（SemVer 任何位变化）

**固定话术**：

```
刚才〇〇值得记。我现在追加到 05_logs/raw/YYYY-MM-DD.md 好吗？
归类：[标签] / 对应 AC 核心问题 #X
```

同意 → 读操作手册 §3.3 获取格式 → append。
不同意 → 继续对话，不纠缠。

## 口头触发词兜底

itsuki 说下列任一词时**必做**（不用问）：

- "记一下" / "总结一下" / "留个痕" / "dump 一下"

## 5 个 AC 核心问题（打标签用）

1. 为什么做 DMSD？（問題発見）
2. 遇到了什么困难？（問題意識）
3. 怎么解决的？（問題解決）
4. 学到了什么？（自己認識）
5. 为什么筑波？以后学什么？（志望動機）

## 关键原则

- 主动识别 + 口头触发词兜底
- **先问再写**，绝不擅自写入
- CC 默认只打 `#AC候选` 标签；升级第 2 层的判断权在 itsuki
- **写 iCloud 第 2/3 层需 itsuki 当场授权**（不是默认行为）——没有明确指令时不动
- **永不写 `05_产出/`**——志望理由书 / 自我推荐书 / 面试准备是 itsuki 的原创作品
- 发现 itsuki 把 AC 私密反思直接写进 `05_logs/` 某个会被推 GitHub 的文件时，提醒她（Private repo 短期无风险，但长期应挪 iCloud）

## 元规则

itsuki 是主角，CC 辅助。CC 越提醒越少、她越来越能自己识别 —— 这本身是成长轨迹。

## 会话结束

1. 刷新当日 `05_logs/raw/YYYY-MM-DD.md` 顶部目录（读操作手册 §8）
2. 列出今天 dump 了哪些碎片给 itsuki 确认
3. 直接更新 `WIP.md`（完成任务 → 最近完成，新认领任务 → 进行中）
4. 起草 `progress_overview.md` 更新草稿，等 itsuki 确认后保存
5. 跑 `§文档一致性规则 → 会话结束前一致性检查` 的 3 项（pre-commit 预演 + 时间戳新鲜度 + 同步点发现）
6. **git commit 本次会话所有变动**（2026-04-19 规则更新，itsuki 明确要求）：

   > **前提（4-19 22:30 / 22:45 纠正）**：**`git` 命令跑完后要给 itsuki 一段中文人话总结"这次 commit 做了什么"** —— 不是讲 `git add` / `git commit` / HEREDOC 这些工具怎么用，是告诉她本次 commit **实际改了什么 / 覆盖了哪些 backlog 条目 / 下一步是什么**。只贴 git 命令输出不够。
   >
   > 例子对比：
   > - ❌ 错（讲工具）："`git add` 是把文件放进 staging area，`git commit` 把 staging 做成快照"
   > - ✅ 对（讲内容）："本次 commit `1557cef` 锁定了 G2 决策 + 87 条 backlog + A+B+C 同步机制，覆盖漏洞 D22/D23/D24/D25/L11，下一步 v0.3.1 Tier 1 剩余项（README / 志望動機占位 / 原创设计 showcase）"
   >
   > 只有 itsuki 主动问 "这个命令是什么意思"时才讲工具。默认讲内容。

   - commit message **必须详细**：首行简短总结（`feat/fix/chore: 简述` + 版本号 / scope 前缀），空行后主体分点列 **why + what**（不只是 what）
   - 参考之前 commit log 风格：`v0.3.0: spec main body rewrite — 双路径并存 + thin client + ...` <!-- VERSION_OK -->
   - **不写 `Co-Authored-By` trailer**（见 memory `feedback_commit_style.md`）
   - pre-commit hook 会自动跑（含硬编码版本号会被拦）
   - 用 HEREDOC 传 message 保证换行和中文正确
   - **不 push**（除非 itsuki 明说"push"）
7. 月末最后一次会话：提醒做月度回顾（挑 `#AC候选` + 写 `monthly_review/YYYY-MM.md` 到 iCloud）

**不做**：长篇会话总结 / 直接写进 iCloud AC 目录 / 未授权 `git push` 或 `git tag`。

---

**END** — CC 把本文作为每次会话必读上下文。
