# 当前工作状态 (Work In Progress)

> **这个文件是给 Claude Code 看的。**
>
> - **会话开始时**: 先读这个文件,知道"做到哪了、谁在做什么、哪些文件我不能碰"
> - **会话结束前**: 更新这个文件(移任务状态、登记完成、更新时间戳)
> - **多个会话并行时**: 通过这个文件互相协调,避免冲突
>
> 和其他文件的区别:
> - `progress_overview.md` = 长期章节目录(稳定,每次会话结束更新一次)
> - `TODO.md` = itsuki 自己的完整待办清单(所有该做没做的事)
> - 本文件(WIP.md) = 当下的书签 + 多会话协调(谁占用哪些文件,避免冲突)

---

**最后更新**: 2026-04-19 22:00 by [Mac-主会话 (CC-Opus-4.7)] — 文档同步机制 A+B+C 建立
**当前版本**: 见 `CHANGELOG.md` 顶部 · **重大状态**: 4-19 晚 G2 决策（取消分阶段，v1.0 一次上） + 项目审查 backlog 87 条 + 文档同步机制（单源真值 + 同步清单 + pre-commit hook）建立

---

## 🎯 当前焦点

**4-19 G2 决策 + 点呼流程定稿 + 项目审查 backlog 落地** — 架构 / 流程 / 记录规则全部重大更新。

**架构层（4-19 重大转向）**:
- **G2 拍板**: 取消 Phase 1 / Phase 2 分阶段上线；**v1.0 直接 iOS + Android + 卡 完整版一次上线**。开发内部仍按 M1→M5 里程碑顺序（风险兜底：做不完至少 M1+M2 可 demo）。
- **点呼路径**: A 路径（NFC 卡 tap 点呼机 PN532）+ B 路径（iPhone / Android 都走 tap 外贴静态 NFC 贴纸）三路共存；Android **不走 HCE**，保持跨平台一致。
- **核心原则保留**: thin client / thick server；服务器唯一判定者；语音播报防作弊。

**卡生命周期（4-19 定稿）**:
- 空白 NTAG215 + 学生自贴"名字便签"（为毕业回收复用，不贴学号）
- App 内"绑定卡片" → tap 卡 → UID 录入学生账户（自助绑定）
- 没手机学生走"管理员代录"特殊通道
- 丢卡：新卡发 + 新绑定 + 旧 UID 作废（不收钱）
- 毕业：清除卡 UID 绑定（账户保留作历史记录），卡可回收给下一届

**App 账号规则（4-19 定稿）**:
- 注册：姓名 + 生日 + 性别（**不要学号**）
- 一设备一账号；换设备必须老师→管理员后台操作（学生不能自助换机）
- Android 分发：自建网站托管 APK，学生下载

**点呼规则（4-19 定稿）**:
- 三路径（卡 / iPhone / Android）并存，学生随便用
- 每时间窗只能点呼一次（幂等）

**记录体系更新（4-19）**:
- `00_admin/CLAUDE_CODE_记录指南.md §3.4` 新增"记录详细度要求"（5 模块 + 篇幅指引 + 失败模式清单）
- raw 每条目标 500-2000 字（按重要度），不再是 100-300 字的"决策快照"

**仍挂的遗留（下次会话讨论）**:
- iPhone / Android tap 贴纸的技术细节（Background Tag Reading / Android 后台唤 App）
- 一设备一账号的具体实现（设备指纹 / 硬件 ID / 推送 token）
- 风控策略起草（CC 起草 → itsuki review）
- Demo 范围构思（G2 兜底）
- 点呼机硬件零件选型（最后做，等 spec 定）
- 宿舍点呼位置网络情况（itsuki 问老师）

**下一个大动作（v0.3.1 Tier 1，1-3 天）**: **文档同步 + AC readiness 第一步**（详见 `00_admin/2026-04-19_项目审查_backlog.md` Tier 1，87 条漏洞里的 11 条）—— 根目录 README / project_evolution 补 3 次转折 / decision_log 补 3 条 / progress_overview 全面更新 / CLAUDE.md 修过期表述 / 志望動機 #5 占位 / 原创设计 showcase / AI 协作坦诚声明。

**v0.3.0 → v0.3.1 → v0.4.0 → v0.5.0 → v0.6.0 路线图**见 backlog Part 5。

---

## 🔄 进行中的任务

*(无进行中任务。会话结束，下次开会话时再认领。)*

---

## ✅ 最近完成(24-48 小时内)

### 2026-04-19 晚（点呼流程 + 卡生命周期 + 记录规则 + 项目审查 backlog）

- **[Mac-主会话]** **点呼流程重新拍板**：会话开场 itsuki "之前的决定全砍了，从 0 开始"；CC 连续跳步 3 次（默认双路径架构 / 没读 spec 推 C5 / 又跳硬件）每次被纠正；最终确立"先流程后硬件"方法论
- **[Mac-主会话]** **G2 决策** — 取消 Phase 1/Phase 2 分阶段上线；v1.0 一次全上（iOS + Android + 卡）；开发内部保留 M1→M5 里程碑
- **[Mac-主会话]** **NFC 卡完整生命周期定稿** — F1 修订（空白 NTAG215 + 学生自贴名字）/ App 内 tap 绑定 / 没手机学生管理员代录 / 丢卡不收钱 / 毕业清 UID 绑定保留账户 / 卡可回收复用
- **[Mac-主会话]** **App 账号规则定稿** — 姓名+生日+性别（不要学号）/ 一设备一账号 / 换机走管理员
- **[Mac-主会话]** **Android 路线拍板** — tap 贴纸（不走 HCE）+ APK 自建网站分发
- **[Mac-主会话]** **三路径 + 时间窗幂等规则定稿**
- **[Mac-主会话]** **记录指南 §3.4 新增** — 记录详细度要求（5 模块 / 篇幅指引表 / 失败模式清单）。触发点：itsuki 反馈"简略的 raw 等于没记录"
- **[Mac-主会话]** **`05_logs/raw/2026-04-19.md`** — 12 条碎片 / 11 条 #AC候选 / ~700 行（经 2 轮重写，按新 §3.4 标准展开）
- **[Mac-主会话]** **`00_admin/2026-04-19_项目审查_backlog.md` 落地** — 87 条漏洞清单（D30 + S20 + A13 + T13 + L11）+ Tier 0-4 版本路线图 v0.3.1 → v0.6.0（**本会话没动清理，Tier 0/1 归入 v0.3.1 下次会话**）
- **[Mac-主会话]** **memory 治理** — 新建 raw_log_depth feedback 后撤回（理由：not git-tracked / 不跨机器同步），规则 merge 进 `CLAUDE_CODE_记录指南.md §3.4`；顺手修 MEMORY.md 3 条过期（v1.0 iOS only → iOS+Android / v1.0 frozen → v0.1 frozen / VPS 不再推进 DMSD）
- **[Mac-主会话]** **文档同步机制 A+B+C 建立** — itsuki 从 spec 文件名 v0.1 vs 内容 v0.2 不同步（raw 20:45）发现根因"多源必然漂移"，拍板全做 A+B+C。**A 单源真值**：新建 `00_admin/文档同步点清单.md`（§1 版本号 / §2 目录结构 / §3 5 核心问题 / §4 分阶段 / §5 时间戳 / §6 Release Checklist / §7 Onboarding Checklist）。**B 会话结束前扫描**：CLAUDE.md 新增"文档一致性规则"节（单源真值表 + 声明性文件清单 + 会话结束前 CC 必做 3 项）。**C pre-commit hook**：`00_admin/hooks/pre-commit` + `install.sh` + `README.md`（首次 clone 后跑 install.sh 设 `core.hooksPath`；hook 拦截声明性文件里的硬编码版本号，支持 `<!-- VERSION_OK -->` 豁免）。配套改动：CLAUDE.md / WIP / TODO 去硬编码版本号 + 反映 G2 决策；backlog D22/D23/D25/L11 打 ✅ + 加元条目 M1；AC 素材记入 `raw/2026-04-19.md §21:30`

### 2026-04-17 晚（spec 修订 3-commit 全部完成）

- **[Mac-主会话]** **v0.3.0**（commit `2ef7ff7`，已 push + tag）— spec 主体 rewrite：§1 双路径并存 / §5.1 双路径信号流 / §11.3 改判时限矩阵 / §11.4 改判扣分联动 / 附录 C 4 台协调 / 附录 D 25 项收口清单。spec 681→958 行（+277）。收口附录 ✅ 13 项 / 🔄 10 项
- **[Mac-主会话]** **v0.2.0**（commit `48e9b38`，已 push + tag）— 字典三件套全改（base_status 重命名 / overlay 分两类 / +5 ENUM 枚举 / +6 FIELD 字段 / +5 ERROR_CODES）+ DEVICE_REGISTRY 新建 + 6 项 🟢 清理（删 .trash_* / 归档 Folder Structure / Overview.docx → 99_archive/ / .gitignore 删 3 条 / 99_archive/README.md / 目录架构.md 删除）+ CHANGELOG 细粒度重建（pre-0.1 追认 6 条 + 2-02 至今每节点一条）+ 元文档单源化（CLAUDE.md ↔ CLAUDE_CODE_记录指南.md，1563→1362 行）
- **[Mac-主会话]** **v0.1.1**（commit `8706fed`，已 push）— CHANGELOG revert v0.2.0→v0.1.1 + CLAUDE.md 措辞修正 + raw 18:00 dump + WIP 启动 spec 修订 3-commit 计划

### 2026-04-17 上午

- **[Mac-主会话]** 把 `RollCall_Spec_v0.1.pages` 数字化为 Markdown（`01_specs/rollcall/RollCall_Spec_v0.1.md`），顺便反向审查 spec 漏洞 7+18=**25 项**（附录 A + B，5 项 🔴 为 Phase 1 阻塞项）
- **[Mac-主会话]** **iCloud AC 目录结构大重构**：两个冗余 "筑波大学 AC入試 準備" 合并；按编号分类（00_指南 / 01_官网资料 / 02_分析与调研 / 03_素材_候选 / 04_素材_成品 / 05_产出 / 99_archive）；扁平版过期文件进 `99_archive/_deprecated_4-14扁平版snapshot/`（建议 4-24 前眼检后删）
- **[Mac-主会话]** **AC 素材第 2 层首次批量填充**：CC 经 itsuki 明确授权，从 `05_logs/raw/` 5 个历史文件挑出 10 条候选 + 候选索引，搬进 iCloud `03_素材_候选/`（常规流程仍是 itsuki 月度做）
- **[Mac-主会话]** **CC 权限边界更新**（`DMSD/CLAUDE.md`）：CC 可读 iCloud AC 目录；写 03/04 需当场授权；永不写 05_产出
- **[Mac-主会话]** **AC 入试记录指南 v3.0 → v3.1**：§1 目录图、§11 起步清单修订为当前真实状态（版本号 bump = AC 记录触发）
- **[Mac-主会话]** 清理 `iCloud/04_Dev/Projects/AC_DMSD/` 老镜像：提取 8 个早期 .pages/.pdf 到 `99_archive/早期手写材料/`，镜像壳标 `_deprecated_AC_DMSD_旧镜像_至2026-04-24`

### 2026-04-15

- **[Mac-主会话]** 重新打开 A(RPi)/B(ESP32) 全维度对比,确认方向 A;推翻 4-12 "已决定 RPi" 的伪决策
- **[Mac-主会话]** 确立核心架构原则:"点呼机只搬运数据,业务判断全在后端"(由 itsuki 主动提出,反驳 AI 的过度配置建议)
- **[Mac-主会话]** 识别 iOS 平台第三方 App 无 NFC HCE / Secure Element 权限的根本限制;学习 Apple Pay 背后机制
- **[Mac-主会话]** 推翻 "手机发 UID 和卡统一" 的初期设计,重设 Phase 2 为双路径共存(卡走 RFID,iPhone 读静态贴纸 + 自己联网发后端,后端 WS 推回点呼机播报)
- **[Mac-主会话]** 发现 spec gap:v0.1 spec 完全没写点呼机契约,记入项目债

### 2026-04-13

- **[Mac-主会话]** 版本号体系重置 v1.0 → v0.1 (commit `3b01345`)
- **[Mac-主会话]** 建立 AC 入試完整记录体系 (commit `e637034`)
- **[Mac-主会话]** 目录结构整理 + 历史内容抢救 (commit `e346dca`)
- **[Mac-主会话]** 2026-04-12 NFC 方案设计日 dev_log (commit `43c73ec`)
- **[Mac-主会话]** 添加 WIP.md 会话状态文档 + CLAUDE.md 新会话读取指令 (commit `91a4294`)
- **[Mac-主会话]** 建立 ac_入試准备/ 子文件夹 + 提升"边做边学"到方法论层 (commit `d89b435`)
- **[Mac-主会话]** 归档 NFC/NFD 鬼影文件到 99_archive/ (commit `666faf8`)
- **[Mac-主会话]** 保存 2025-12 早期 NFC 系统设计对话为 raw 素材(~3100 行,待后续整理)

### 2026-04-12

- **[Mac-会话]** NFC 架构决策(Raspberry Pi + 分阶段 + 播报防作弊)
- **[Mac-会话]** 更新 executable_dev_checklist_v0.1

### 2026-04-10

- **[Mac-会话]** 解决 NFC/NFD git pull 失败
- **[Mac-会话]** 建立 AI 协作机制 + 一个月空白反思

---

## 📋 开放任务

**完整待办清单已迁移到 `00_admin/TODO.md`**(itsuki 自己维护的主清单)。

本文件只保留 **多会话协调相关** 的任务信息——即:有文件边界冲突风险、需要认领的任务。

查看所有待办 → `00_admin/TODO.md`

### 📌 需要会话认领的任务(有文件边界风险)

*(当前无。将来当多个会话同时开工时,从 TODO.md 拉任务到这里并标注认领者+涉及文件。)*

---

## 🚧 阻塞项

*(当前无阻塞项)*

---

## 🔒 多会话协调规则

### 会话认领流程

1. **开始任务前**: 把任务从 "开放任务" 移到 "进行中",登记认领者和开始时间
2. **做的过程中**: 更新 "已完成" 子列表 + "当前停在"
3. **完成后**: 把任务移到 "最近完成",写上 commit hash(如有)
4. **放弃 / 暂停时**: 把任务写清楚停在哪,移回 "开放任务" 或保留在 "进行中" 标注为暂停

### 会话标识(建议命名)

用 `[设备-主题]` 格式,例如:
- `[Mac-主会话]` — Mac 上的主会话
- `[Mac-后端]` — Mac 上专门做后端的
- `[Mac-设备]` — Mac 上专门做 Raspberry Pi 代码
- `[VPS-后端]` — VPS 上的后端会话
- `[iPad-文档]` — iPad 上做文档整理

### 避免冲突的硬规则

1. **每个"进行中"任务必须标出"涉及的文件/目录"**
2. **其他会话不能动正在被认领的文件**
3. **共享文件**(大家都会改的,如 `CLAUDE.md`, `WIP.md`, `progress_overview.md`, `CHANGELOG.md`): 一次只能有一个会话修改,改完立刻 commit + push
4. **改 `WIP.md` 本身时**: 先 pull,改完立刻 push,避免和其他会话撞
5. **git conflict 了怎么办**: 停下来,先问 itsuki,不要自己猜合并

### 关键文件边界(将来会用到)

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/device/` | 设备会话(Raspberry Pi) |
| `03_dev/Student_iOS_new/` | iOS 会话 |
| `03_dev/teacher_web/` | 老师端会话 |
| `01_specs/` | 一次只允许一个会话改(规格冻结区) |
| `00_admin/` | 主会话管理 |
| `05_logs/dev_log/` | 各会话写自己今天的,文件名不撞就好 |
| `05_logs/raw/` | 同上 |

---

## 📝 给新会话的上下文(关键信息)

新会话读完 `CLAUDE.md` 和本文件应该知道:

1. **当前版本**: 见 `CHANGELOG.md` 顶部 — 项目仍在规格和设计阶段，未开始写代码。CHANGELOG 已于 2026-04-17 晚重建为细粒度（pre-0.1 追认 + 2-02 至今每实质节点一条）
2. **上线姿态（4-19 G2 决策）**: 取消 Phase 1 / Phase 2 分阶段；v1.0 直接 iOS + Android + 卡 完整版一次上线。开发内部仍按 M1→M5 里程碑
3. **防作弊核心**: 语音播报（原创设计，详见 `05_logs/decision_log.md`）
4. **版本体系**: 0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**: CC 侧见 `00_admin/CLAUDE_CODE_记录指南.md`；方法论总章（`AC入试记录指南_v3.md`）在 iCloud，CC 不读
6. **文件地图**: 见 `CLAUDE.md §目录结构`（单源真值，见 `00_admin/文档同步点清单.md §2`）
7. **文档一致性**: 声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则` + `00_admin/文档同步点清单.md` + `00_admin/hooks/pre-commit`
8. **itsuki 的偏好**: 给选项用 A/B/C 不用甲乙丙；决策她拍板；不盲从 AI

---

## 🕘 更新日志(本文件自己的)

- 2026-04-13 17:30 — [Mac-主会话] 初次创建 WIP.md
- 2026-04-13 晚 — [Mac-主会话] 开放任务迁移到 `TODO.md`;WIP 聚焦多会话协调;更新当前焦点(NFC 硬件选型中)
- 2026-04-13 深夜 — [Mac-主会话] 补充今天的完成清单(commit 91a4294/d89b435/666faf8 + 2025-12 raw)
- 2026-04-15 晚 — [Mac-主会话] 刷新当前焦点(Phase 1+2 架构敲定,进入硬件收尾+spec 补完阶段);登记 4-15 完成清单;记入两项新项目债(点呼机 spec、Android Phase 2 方案)
- 2026-04-17 18:00 — [Mac-主会话] 启动 RollCall v0.1 spec 修订(3 commit 计划);版本号 v0.3.0 revert 到 v0.1.1 patch（命名整理而已，spec 内容未变）;新增"进行中任务 A"
- 2026-04-17 18:09 — [Mac-主会话] CHANGELOG 细粒度重建：pre-0.1 追认 6 条 2025-12 方案级迭代（HCE→tag→SDM/SUN→v2→v2.1→v2.1加固版，来源 itsuki 贴出的早期 ChatGPT log）+ 2-02 至今每个实质节点一条 patch，当前 = v0.3.0
- 2026-04-17 19:00 — [Mac-主会话] **会话结束**：v0.3.0 spec 主体 rewrite 完成（commit `2ef7ff7`） + v0.2.0/v0.3.0 双 tag 推上 GitHub；任务 A 全结，移到"最近完成"
- 2026-04-19 21:15 — [Mac-主会话] **会话结束**：G2 取消分阶段决策 + NFC 卡生命周期定稿 + Android tap 贴纸路线 + App 账号规则 + 三路径幂等 + 记录指南 §3.4 新增 + raw/2026-04-19.md（12 条 / 11 #AC 候选） + MEMORY.md 过期 3 条修正 + 项目审查 backlog（87 条）落地。**git 暂未 commit/push**（itsuki 有另一个 agent 在改文件，避让）。下次开会话先 commit 这批 + v0.3.1 Tier 1 文档同步开工
- 2026-04-19 22:00 — [Mac-主会话] **文档同步机制 A+B+C 建立**（本次会话）：itsuki 从"版本号漂移"症状识别系统性病根，选最彻底方案。新建 `00_admin/文档同步点清单.md` + `00_admin/hooks/pre-commit` + `install.sh` + `README.md`；CLAUDE.md 加"文档一致性规则"节 + 去硬编码版本号；WIP / TODO 去硬编码。backlog 打 x 4 条 + 加 M1。AC 记录追加 raw §21:30
