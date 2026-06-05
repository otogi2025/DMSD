# Project Guide — DMSD / Tomoshibi

> **这是什么**：让一个**第一次接触这个项目的人或 AI，从零到深入理解整个 DMSD**的完整导览。先建立正确的地图，再读细节。
>
> **它和别的「介绍型」文件分工**（三层，不重叠）：
> - `00_admin/项目心智模型.md` = AI 每次**开局必读**的 1 屏骨架（短、快），随时知道系统跑通的主线 + 5 端现状。
> - **本文件 `PROJECT_GUIDE.md`** = 想**深入理解整个项目**时读的完整展开版（长、全）。不用每次读，需要时读，隔一段更新一次。心智模型是本文件的浓缩摘要。
> - `.claude/skills/project-overview/SKILL.md` = 1396 个文件逐个的「字典」，想知道**某个具体文件干嘛**时查。
>
> **怎么用**：想**快速了解**→读 §1~§3；想**深入理解**→读全文；想**查某个文件**→去 project-overview。

---

## 1. 项目一句话 + 要解决什么

**DMSD 是一个把宿舍点呼数字化的系统**。`DMSD`（Dormitory Management System Digitalization，宿舍管理系统数字化）是项目/仓库代号；`Tomoshibi`（灯火 / ともしび）是这个系统对外使用的产品名。

**要解决的核心问题**：宿舍现在很多流程靠纸质表和人工确认——晚上点呼、迟到缺席记录、外泊申请、学习出席、纪律扣分、清扫检查、前台宅配。Tomoshibi 把这些连成一套能在真实宿舍跑起来的系统。

**最核心的一件事是「点呼数字化 + 防代刷」**：学生晚上回宿舍，用 NFC（Near Field Communication，近场通信——手机或卡靠近几厘米就能传数据）刷一下完成签到，系统自动记考勤、算扣分。难点是防止「代刷」（让别人替自己签到）。

> **为什么这个项目重要**：它是 itsuki 申请筑波大学情報学群 AC 入試（一种重视过程与动手能力的特别入学考试）的核心叙事项目。所以代码、文档、决策过程都同等重要。

---

## 2. 系统全景：5 个端 + 1 个中枢

系统由 5 个「端」（互相独立、各跑各的程序）组成，全部靠**后端**这个中枢连起来。

| 端 | 是什么 / 谁用 | 代码位置 | 技术栈 | 成熟度 |
|---|---|---|---|---|
| **后端 backend** | 唯一判定者 + 数据库 + 给所有端提供接口 | `03_dev/backend/v1/` | FastAPI（Python 网络框架）+ PostgreSQL（数据库） | 🟢 主干靠前 |
| **学生 iOS** | 学生用的 iPhone App | `03_dev/student_ios/v1/` | Swift + SwiftUI | 🟢 较靠前 |
| **学生 Android** | 学生用的安卓 App | `03_dev/student_android/v1/` | Kotlin + Jetpack Compose | 🟡 偏早 |
| **老师网页 teacher_web** | 老师看座位 / 改判 / 管学生账号 | `03_dev/teacher_web/v1/` | React + TypeScript + Vite | 🟢 较靠前 |
| **点呼机 rollcall_device** | 宿舍门口那台刷卡机 | `03_dev/rollcall_device/` | 树莓派 Pi 3A+ + PN532 读卡模块 | 🟠 早（骨架）|

成熟度图例：🟢 较靠前 / 🟡 中 / 🟠 早 / 🔴 未开工。**注意**：「成熟度」几个月才变一次；「最近做到哪、正在改什么」属于流水进度，看 `00_admin/WIP.md`，本文件不复述。

> **上线姿态**（2026-04-19 拍板）：v1.0 = NFC 卡 + iPhone App + 安卓 App **一次性一起上线**，不分阶段。（早期 4-12 曾设想「先卡后手机」分阶段，已废弃。）

---

## 3. 系统怎么跑通（一条签到主线）

详细流程 + 攻防分析见 `02_design/flow_design.md`。骨架一条线：

```
学生刷卡（路径 A） 或 手机碰一下点呼机（路径 B）
  → 卡：点呼机的 PN532 模块读卡的 UID（卡的唯一编号）
    手机：App 把身份数据「写」进点呼机里 ST25DV 芯片的邮箱缓存（手机全程不联网）
  → 点呼机给数据盖一个 NTP 校准过的时间戳 swipe_time（= 接触机器那一刻的准确时间）
  → 点呼机自己 POST 到后端的签到接口（是点呼机连后端，不是手机连后端）
  → 后端校验：是注册学生吗? 设备注册了吗? 在点呼时间窗内吗?（按 swipe_time 判）
  → 写一条 attendance 记录（只追加、不改旧记录）
  → 后端通过 WebSocket（一种服务器能主动推消息给客户端的长连接）实时推送：
       老师网页上这个学生的座位变绿 + 点呼机播报学生全名 + 亮绿灯
```

**三条签到路径并存**：① NFC 卡贴点呼机 ② iPhone 写 ST25DV 邮箱 ③ Android 写同一张 ST25DV。

**关键架构反转（2026-06-02）**：手机从原来的「读点呼机贴纸拿 URL 再联网上报」，改成「直接写进点呼机的邮箱缓存、自己完全不联网」。好处：学生没流量/没网也能签到（飞行模式都行）；系统复杂度减半。

---

## 4. 核心业务概念（理解项目的钥匙）

这几个概念是读懂整个系统的前提。具体规则的权威源是 `01_specs/rollcall/RollCall_Spec.md` + `02_design/system_features.md`，这里只讲「是什么」。

- **点呼（roll call）**：宿舍每天固定时段确认学生在不在。数字化后 = 刷 NFC 签到 + 系统按时间窗自动判「准时 / 迟到 / 缺席」。
- **扣分（規律点 / demerit）**：违纪（迟到、缺席、清扫不合格等）累计扣分，到阈值触发处分。阈值等具体数字见 spec。对应表 `DemeritEvent`，路由 `discipline.py`。
- **申请审批链（approval chain）**：学生提的申请（外泊 / 帰省 / 帰国 等）要按申请类型经过指定的几位老师依次审批。逻辑在 `services/approval_chain.py`，对应表 `Application` + `ApplicationApproval`。
- **学習（study）**：被列为「学習対象」的学生要在学習区刷卡签到、缺席要交欠席届、也能申请在线学习。对应表 `StudyRoster` / `StudyCheckin` / `StudyAbsenceRequest` / `StudyOnlineRequest`。
- **角色权限**：老师不是一种，分寮務部長 / 寮務課長 / 寮監 / 学習担当 / 一般教師 / 管理係 等，不同角色能看 / 能改的范围不同（比如只有寮务管理几个角色能管学生账号）。学生只能访问自己的数据。
- **防代刷（anti-cheat）**：系统的灵魂。核心认知是「**任何打卡技术只能验证设备，验证不了人**」——卡能让朋友带、手机能借、二维码能截图。所以最终防线是**点呼机现场播报姓名 + 老师看脸**，技术（NFC 近场 4cm + 现场到场）只是把「必须本人到场」这件事坐实。
- **学年更新（renewal）**：每年 4 月老师点一次「学年更新开始」=给非毕业年级学生打更新标记 + 发通知，学生自己确认。对应路由 `student_promote.py`。

---

## 5. 把 5 端绑在一起的契约（改任何端都要遵守）

全部细节见 `01_specs/API_CONVENTIONS.md`。最关键 4 条：

1. **响应格式**：成功返回 `{ok:true, data:{}}`；失败返回 `{ok:false, error:{code,message,detail}}`。成功没有 error 字段，失败没有 data 字段——两者互斥。
2. **鉴权**：请求头带 `Authorization: Bearer <token>`（token = 登录后拿到的身份令牌）。学生 token 只能访问学生接口，老师 token 只能访问老师接口。
3. **URL 命名**：⚠️ 还没最终拍板（API_CONVENTIONS §8.2 / 编号 L8 是未决项）。临时统一用方案 A：`/api/v1/<角色>/<资源>`。新代码按 A 写。
4. **时间 + 命名**：全链路用 JST（日本时间）。判定时间基准 = 点呼机打的 `swipe_time`（NTP 校准，受信任的边缘设备，不算普通客户端）；普通客户端（手机 / 老师网页）的本地时间不参与判定。字段名一律小写蛇形（`student_id`，不要写成 `studentId`）。

> 真正的字段级对齐（后端 ↔ iOS ↔ Android 哪个字段叫什么、是否可空），用 `spec-sync` skill 真扫真比，本文件不复述。

---

## 6. 不能违反的核心不变量（设计铁律）

改任何端，下面这些都不能破（来源 `flow_design.md` + `decision_log.md`）：

1. **后端是唯一判定者**——所有「准时 / 迟到 / 缺席 / 扣分」判定逻辑全在后端，手机和老师网页本地不算数。例外：时间戳由点呼机打 `swipe_time`（NTP 校准、受信任边缘设备）。
2. **点呼机只搬运数据，不做业务判断**（thin client / 瘦客户端）——点呼机只做读 NFC、发 HTTP、收 WebSocket、播报亮灯 4 件事。设备越「蠢」越安全，改规则只改后端一处。
3. **幂等（idempotent）**——同一次签到重复提交只记一次（卡用复合唯一索引，手机用幂等键 idempotency_key）。
4. **老师入学日面签**——整个账号体系唯一的真人身份验证锚点；日常签到靠现场老师目视监督兜底。
5. **防代刷最终靠人**——技术（NFC 近场 + 现场播报）把人逼到必须本人到场，最后一道是老师看脸（v2.0 计划用人脸识别把「看脸」自动化）。
6. **一次性上线**——v1.0 = iOS + Android + 卡一起上线，不分阶段。

> ⚠️ **全项目最大的未完成块**：防作弊核心的**后端部分一行都没写**——还缺设备注册校验、卡→学生映射（`Student.card_uid` + cards 表 + 唯一索引）、点呼机↔后端传输安全（加密 + 设备密钥）。当前签到接口暂用老师令牌鉴权、手动传 `student_id`。这是 v1.0 上线最大隐患。施工计划见 `02_design/NFC防代刷_后端立项施工计划.md`。

---

## 7. 数据模型骨架（后端 34 张表，按业务域分组）

权威定义在 `03_dev/backend/v1/app/models.py`（1468 行）。按业务域看一眼有哪些表，能快速建立「系统记录了什么」的画面：

| 业务域 | 表 | 管什么 |
|---|---|---|
| **身份 / 账号** | `Student` `Teacher` `Account` `ClassTeacherAssignment` `TeacherInvitation` `StudentRegistrationCode` | 学生 / 老师档案、学生登录账号、班主任分配、教师邀请、学生注册码 |
| **点呼 / 出席** | `RollCallSession` `RollCallEvent` `DeviceToken` | 点呼场次、每次刷卡记录、推送令牌 |
| **申请类** | `Application` `ApplicationApproval` `Outing` `DormEventProposal` `DormScheduleChange` `FridgePurchaseRequest` `ItemPossessionRequest` | 外泊/帰省/帰国 申请 + 审批、当天外出、寮行事企画、寮日课变更、冷蔵庫購入、物品所持 |
| **学習** | `StudyRoster` `StudyCheckin` `StudyAbsenceRequest` `StudyOnlineRequest` | 学習対象名册、学習签到、欠席届、在线学习申请 |
| **纪律 / 指导** | `DemeritEvent` `CleaningAssignment` `GuidanceRecord` `GuidanceDisclosureRequest` `IncidentRecord` | 扣分、清扫分配、指导记录、指导开示申请、事案记录 |
| **生活信息** | `Announcement` `AnnouncementRead` `AnnouncementReply` `FrontDeskItem` `DormEvent` `BusRoute` | 公告 + 已读 + 回复、前台宅配/失物、行事予定、巴士时刻表 |
| **系统** | `NotificationLog` `AuditLog` | 通知发送记录、操作审计日志 |

这 34 张表对应后端 25 个路由（`app/routers/`，逐个见 project-overview §3.4）和各客户端的界面。

---

## 8. 关键决策与「为什么」（精选）

完整决策脉络在 `05_logs/decision_log.md`。下面是理解项目最该知道的几条——它们也是 AC 叙事的核心：

1. **NFC 而不是二维码**（4-12）：二维码能截图发给不在场的人；NFC 的 4cm 距离从根本上消除这个漏洞。点呼的本质是「确认人在场」。
2. **语音播报防作弊**（4-12，最强叙事）：发现任何打卡系统都验证不了「人」，于是用「播报姓名 + 老师看脸」让代刷者必须本人到场。
3. **点呼机用树莓派不用 iPad**（4-12）：iPad 太贵（约 5 万日元）且不适合固定上墙；树莓派约 1.3 万日元、跑 Python（和后端同语言）、能练动手能力。
4. **点呼机只搬运数据**（4-15）：发现 spec 里根本没写过点呼机职责，AI 就会自由加配。定下「业务判断全在后端」后，硬件需求大幅降级。
5. **双路径、不强求协议统一**（4-15）：iOS 平台限制——第三方 App 不能伪装 NFC 卡发任意 UID。于是卡走一条路、手机走另一条路，实现同样体验。
6. **架构反转：手机改「写」不「读」**（6-02）：itsuki 自己补硬件原理课时发现旧方案矛盾，回到第一性原理重想，让手机彻底不联网、复杂度减半。
7. **老师网页迁 React + Vite，界面 100% 冻结**（6-05）：撤掉「零基础维护难」这个伪约束（有 AI 辅助维护）后，选业界标准的 Vite 正规工程；铁律是界面逐页原样搬，吸取上一次「重做新界面被否决」的教训。

---

## 9. 当前真实状态（看这里别看版本号）

版本号在 `CHANGELOG.md` 顶部，但**判断「现在做到哪」不要只看版本号**——很多推进没来得及 bump 版本。看当前状态的权威来源：

1. `00_admin/WIP.md` —— 最近几次会话做了什么 + 当前焦点 + 阻塞项（短期记忆，每次会话必读）。
2. `00_admin/项目心智模型.md` —— 5 端成熟度档位 + 系统骨架（慢变量）。
3. `00_admin/progress_overview.md` —— 给教授看的长期里程碑（对外页面）。

一句话现状：5 端代码层都已启动；后端 + iOS + 老师网页更靠前，Android 屏已铺开但真后端接入待续，点呼机仍是骨架 + 硬件采购阶段；**防作弊核心后端是最大未完成块**。

---

## 10. 第一次该按什么顺序读

| 顺序 | 文件 | 目的 |
|---|---|---|
| 1 | `README.md` | 先知道项目是什么、当前主线 |
| 2 | **本文件 `PROJECT_GUIDE.md`** | 建立完整地图（你正在读）|
| 3 | `00_admin/项目心智模型.md` | 1 屏速记系统怎么跑通 + 5 端现状 |
| 4 | `02_design/system_features.md` | 5 端共用功能规格 |
| 5 | `01_specs/rollcall/RollCall_Spec.md` | 点呼系统的业务规则 |
| 6 | `05_logs/decision_log.md` | 关键决策为什么这样定 |
| 7 | `05_logs/project_evolution.md` | 项目从想法到系统的演化 |
| 8 | `.claude/skills/project-overview/SKILL.md` | 查某个文件 / 目录具体干什么 |

**不要从 `05_logs/raw/` 开始读**——那是原始会话记录，信息密度高，且包含后来被推翻的方案。

---

## 11. 目录怎么理解

| 目录 | 读法 |
|---|---|
| `00_admin/` | 项目管理区。WIP、TODO、进度、心智模型、hook、审查 prompt。 |
| `01_specs/` | 规格区。规则、字段、错误码、点呼系统真值。 |
| `02_design/` | 跨端设计区。系统功能、硬件、流程图。 |
| `03_dev/` | 代码区。Backend / iOS / Android / Teacher Web / 点呼机。 |
| `04_ops/` | 运维区。部署、WiFi 调研等实地操作说明。 |
| `05_logs/` | 记录区。决策、学习、演化、raw 原始记录、审查报告。 |
| `06_assets/` | 素材区。图标、术语表、学习清单、真实班车样本。 |
| `99_archive/` | 历史归档区。不要当当前主线。 |
| `.claude/` | AI 协作配置和项目 skills。给 Claude Code / Codex 读。 |
| `bin/` | 本地工具脚本。 |
| `docs/` | 外部 agent skills 的配置，不是项目正文文档。 |

---

## 12. 读代码前先知道的各端主线 + 入口

### Backend（后端）
先读：`03_dev/backend/README.md` → `BACKEND_DESIGN_LOG.md`（设计决策权威源）→ `v1/app/main.py`（应用入口）→ `v1/app/models.py`（34 张表）→ `v1/app/routers/`（25 个路由）。
重点：v1 正式版在 `v1/`，`demo/` 目录锁定不动。

### iOS（学生 iPhone App）
先读：`IOS_DESIGN_LOG.md`（设计决策权威源）→ `v1/README.md` + `v1/BUILD.md`（构建）→ `v1/TomoshibiApp/Foundation/`（基础层：网络 / 路由 / 主题）→ `Features/`（各业务界面）。
重点：当前代码以 `v1/` 为准；旧 README 可能还写独立 repo 时代的信息。

### Android（学生安卓 App）
先读：`ANDROID_DESIGN_LOG.md` → `v1/app/src/main/java/jp/tomoshibi/android/`（`ui/screens/` 57 个屏 + `nav/` 路由 + `data/` 状态与模型）。
重点：屏已铺开（57 个），但真后端接入还在用 MockData 假数据，待续。

### Teacher Web（老师网页）
先读：`WEB_DESIGN_LOG.md` → `DESIGN_BRIEF.md` → `v1/index.html`（Vite 入口）→ `v1/src/`（`App.tsx` 总枢纽 + `Shell.tsx` 外壳 + `components/` 26 个页面/弹窗 + `api/client.ts` 接后端）。
重点：当前主线是 React + TypeScript + Vite（6-05 迁移）；旧的 HTML 单文件版已归档，别当当前路线。

### Rollcall Device（点呼机）
先读：`README.md` → `ROLLCALL_DEVICE_DESIGN_LOG.md`（软件设计权威源）→ `src/main.py`（主循环骨架）→ `点呼机接线说明.md` + `02_design/hardware_design.md`（硬件层）。
重点：仍是骨架 + 硬件采购/接线准备阶段，真机 NFC / LED / 播报模块待实装。

---

## 13. 哪些文件别误读

- `99_archive/`：历史材料，不代表当前主线。
- `05_logs/raw/`：原始会话记录，信息密度高、含被推翻的方案，不适合作为第一印象入口。
- 老师网页里**已归档的 Vite 旧试做**（`99_archive/2026-05-26_teacher_web_vite实装作废/`）和 **HTML 单文件版**（`99_archive/2026-06-05_teacher_web_html单文件版归档/`）：都不是当前主线，当前主线是 `v1/src/` 下的新 Vite 版。
- `.pages` / `.docx` / `.510Z`：多是早期原稿或不可读归档，通常已被 Markdown 文件替代。
- 子目录里的旧 README：有些是历史快照，遇到冲突时以 `WIP.md` / `项目心智模型.md` / `project-overview` 为准。

---

## 14. 给后续维护者的判断原则

1. 看「当前状态」→ 先读 `00_admin/WIP.md` + `项目心智模型.md`。
2. 找某个文件用途 → 读 `.claude/skills/project-overview/SKILL.md`。
3. 改业务规则 → 先查 `02_design/system_features.md` 和对应端的 `*_DESIGN_LOG.md`。
4. 改后端 API → 同步 iOS / Android / 老师网页的请求字段（用 `spec-sync` skill 核对）。
5. 改文件结构、移动文件、新建入口文档 → 同步 `project-overview`（有 hook 提醒）。

---

**最后更新**：2026-06-05（从 170 行导览扩成深度理解版 — 加系统怎么跑通 / 核心业务概念 / 5 端契约 / 设计铁律 / 数据模型骨架 / 关键决策）
