# Briefing for Code Agent — DMSD（项目）/ Tomoshibi（系统）Demo 4-28 Sprint  <!-- VERSION_OK -->

> **读者**：新开的代码实现会话（负责前端 / 后端 / iOS / 点呼机代码）
> **发件人**：需求/文档会话 [Mac-demo-sprint]
> **目的**：让你在 5 分钟内知道自己是谁、要做什么、读哪些文件、交付标准

---

## 🔖 命名（2026-04-21 定名，代码/UI/文案全部遵守）

| 概念 | 名字 | 使用场景 |
|---|---|---|
| **项目 / 仓库 / 开发代号** | **DMSD** | commit message / git / spec / 内部开发文档 |
| **系统 / 产品 / 对用户文案** | **Tomoshibi**（灯火 / ともしび）| App title / Web title / `<title>` 标签 / 登录欢迎语 / README 给用户看的部分 / FastAPI app title / Swift App name / 代码里 UI 字符串 |

**铁律**：
- iOS App 的 `CFBundleDisplayName` = `Tomoshibi`（不是 DMSD）
- FastAPI `FastAPI(title="Tomoshibi API")`（不是 DMSD API）
- Web `<title>Tomoshibi 老师管理台</title>`（不是 DMSD）
- Python / Swift / JS 里 UI 字符串（按钮 / 标题 / 欢迎语）一律 Tomoshibi
- 模块名 / 类名 / 包名 / 变量名可以用 `dmsd` 前缀（内部代号），UI 展示层一律 Tomoshibi
- 数据库 / 配置 / 日志里的应用名：`tomoshibi`（lowercase）

**AC 叙事一句**（万一管理员或教授问为什么叫 Tomoshibi）：
> "我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。"

---

## 1. 你是谁

你是 DMSD 项目 **Demo 4-28 Sprint 的代码实现 agent**，负责把需求文档里的 Tier 1 功能变成 **Tomoshibi** 系统的可运行代码。

- **使命**：把需求文档里的 Tier 1 功能变成能跑的代码，让 2026-04-28 的管理员 demo 成功
- **Deadline**：**2026-04-28**（7 天，今天 2026-04-21 是 D1，demo 是 D8）
- **用户**：itsuki（中国人，日本高三，零基础，目标筑波大学 AC 入試）
- **评估标准**：Demo Day 管理员看完点头 → 系统被采纳 → 这是最硬的 AC 素材

## 2. 第一件事：读这 8 个文件（按顺序）

**30 分钟内读完**，建立完整上下文。

1. `CLAUDE.md`（项目总规则，对话语言 / 代码注释 / 命名 / commit 规则）
2. `00_admin/WIP.md`（当前工作状态 + 文件边界 + 会话协调规则）
3. `00_admin/demo_4-28/README.md`（文件夹导览）
4. `00_admin/demo_4-28/sprint.md`（7 天时间表 + 决策复盘 + 风险清单）
5. **`00_admin/demo_4-28/scope_tier.md`**（⭐ 最重要，你的需求来源：每个功能含 API 规格 / 字段 / 页面路径 / demo 动作）
6. `00_admin/demo_4-28/demo_script.md`（Demo 当天演示台词，你写的代码要确保每一步真跑通）
7. `00_admin/demo_4-28/ST25DV_fallback.md`（硬件 fallback：NTAG215 + iOS Shortcuts Automation 代 ST25DV16K）
8. `02_design/hardware_design.md`（硬件规格：Pi 3A+ / NTAG215 / PN532）
9. `03_dev/backend/README.md`（backend skeleton 已建，怎么跑）

## 3. 你的职责边界

### 你负责的文件（可自由 Write/Edit/新建）

- `03_dev/backend/` — 后端 FastAPI（已有 skeleton，继续加端点 / 表 / 业务逻辑）
- `03_dev/teacher_web/`（待建）— 老师 Web 前端
- `03_dev/Student_iOS_new/`（待建）— 新 iOS App（旧 iOS 代码是 throwaway，别用）
- `03_dev/device/`（待建）— Pi 3A+ 点呼机 Python 程序

### 你不能改的文件（只读）

- `00_admin/demo_4-28/*`（需求档，需求变动必须通过 itsuki 走需求会话更新）
- `01_specs/*`（spec 冻结）
- `00_admin/v0.4.0_*.md`（主会话 [Mac-主会话] 负责）
- `00_admin/2026-04-19_项目审查_backlog.md`（主会话负责）
- `CLAUDE.md`（改动走 itsuki）
- `05_logs/raw/*`（由 itsuki 和 [Mac-demo-sprint] 维护）
- `02_design/*`（设计文档由需求会话维护，硬件/流程变动不是代码能决定的）

### 可以协作更新

- `00_admin/WIP.md` §进行中的任务 — **你登记自己的进度**（加自己的 agent 名字 + 认领文件 + 进度）
- `00_admin/demo_4-28/questions_for_requirements.md`（新建，如有需求疑问往里写 → itsuki 看到后同步到需求会话修正）
- `CHANGELOG.md` — demo 后评估版本号 bump 时更新（本 sprint 期间不打 tag）

## 4. 技术栈（已定，别改）

| 组件 | 技术 | 依据 |
|---|---|---|
| 后端 | **FastAPI + SQLAlchemy + SQLite**（demo）/ PostgreSQL（上线）+ WebSocket | 已有 skeleton `03_dev/backend/` |
| 老师 Web | **HTML + Vanilla JS + WebSocket client**（不用 React，7 天来不及学）| 零基础 + deadline |
| iOS App | **Swift + SwiftUI + URLSession**（Xcode 模拟器，不实机）| scope 限定 |
| iOS tap | **iOS Shortcuts Automation**（itsuki 手动配，你不实现）| fallback 方案 |
| 点呼机 | **Python + adafruit-circuitpython-pn532**（I²C 读卡）+ **pyttsx3**（本地 TTS）| Pi 3A+ 硬件 |
| 点呼机 OS | **Raspberry Pi OS Lite**（不装桌面，省 RAM）| Pi 3A+ 512MB RAM 硬约束 |

## 5. 7 天时间表（从 `sprint.md §3` 拷贝，细节看原档）

| Day | 日期 | 你要产出的代码 |
|---|---|---|
| D1 | 4-21 今天晚 | 已完成 backend skeleton |
| D2 | 4-22 周三 | Pi 烧 SD + 连 WiFi + SSH（itsuki 做，你给文档步骤）/ 后端本地跑通 + curl 测 `/api/checkin` |
| D3 | 4-23 周四 | Pi Python 主程序：PN532 读 UID + POST 签到 / iOS Shortcuts 配置 itsuki 手动 / **端到端第一次跑通** |
| D4 | 4-24 周五 | Pi TTS 语音喊名 / 老师 Web 登录 + 主框架 + **实时座位表（颜色渲染）** + 左侧菜单 7 大类导航 |
| D5 | 4-25 周六 | **座位改判** + **健康上报** + **请假申请** Tier 1（3 项真跑）+ Tier 2 一批（扫除/巴士/活动/匿名建议 skeleton）|
| D6 | 4-26 周日 | **外宿 + 归国 + 扣分 + 检索** Tier 1（4 项）+ Tier 2 另一批（遗失物/宿舍墙/点歌/快递/归县/出租车/通知中心/长期豁免 skeleton）|
| D7 | 4-27 周一 | 彩排 3 遍 + bug 修 + 预警名单 skeleton |
| D8 | 4-28 Demo Day | 待命（现场可能要紧急修 bug）|

## 6. Tier 策略（最关键）

**Tier 1 = 真跑通**（demo 脚本里真演，不能假）：
- 登录 / 点呼会话 / 实时座位表 / NFC 签到 / 语音喊名 / 座位改判 / 健康上报 / 请假 + 审批 / 外宿 + 审批 / 归国 + 审批 / 扣分展示 / 后台检索
- 每项 API + 字段 + UI 要求 → 见 `scope_tier.md §1`

**Tier 2 = UI skeleton**（能点开不真跑）：
- 扫除 / 巴士 / 活动 / 匿名建议 / 遗失物 / 宿舍墙 / 点歌 / 快递 / 归县 / 出租车 / 通知中心 / 长期豁免 / 预警 / 导出
- 实现策略：前端统一用 `SkeletonPage` 组件（标题 + 说明文字 + 3 条 mock 数据 + "开发中"标签）
- 每项估时 ≤ 0.3 天 → 见 `scope_tier.md §2`

**Tier 3 = 完全不做**（demo 当天不出现）：
- 真举报审核算法 / 真删除封禁 / CSV/PDF 真导出 / 多机协调 / 时间窗自动结算 / APNs 推送
- → 见 `scope_tier.md §3`

## 7. 关键约束（踩过坑的 / 必须知道的）

### 7.1 ST25DV16K 不用等

- 淘宝空运来不及，用 **NTAG215 静态贴纸 + iOS Shortcuts Automation**
- iOS 端不需要你写 NFC 读卡代码（iOS Shortcuts 直接 POST 调你的 `/api/checkin`）
- 你只要确保 `/api/checkin` 能被 POST JSON `{"student_id": 1, "method": "shortcut"}` 正常响应

### 7.2 iOS App 只在 Xcode 模拟器演示

- 不需要 Apple Developer 账号、不需要实机部署、不需要签名
- App 只做 6 屏：签到 / 健康上报 / 请假 / 外宿 / 归国 / 扣分查看
- URL 可以写 Mac 局域网 IP（例如 `http://192.168.1.100:8000`），demo 当天手动改

### 7.3 网络配置

- Demo 当天 Mac 开 WiFi 热点 → Pi / iPad / iPhone 都连这个热点
- 所有 API URL 用 Mac 局域网 IP，**不要硬编码**；后端 + 前端 + iOS + Pi 都做成配置
- 建议：backend 读环境变量 / 前端从 URL 参数 / iOS 从 Info.plist / Pi 从 `.env` 文件

### 7.4 pre-commit hook

- `00_admin/hooks/pre-commit` 会拦截声明性文件里的硬编码版本号
- 你写的代码文件（`.py` `.js` `.swift`）**不受影响**
- 但如果你碰 `.md` / `CLAUDE.md` / `WIP.md` / `TODO.md` 要注意

### 7.5 iOS 旧代码

- `03_dev/Student/` 里的旧 iOS 代码是 **throwaway**（4-10 前产物），别用
- 新项目从零建：`03_dev/Student_iOS_new/`

### 7.6 扣分规则可配置

- 默认值：迟到 0.5 / 缺席 1 / 月累计 4 罚扫 / 月累计 8 禁足
- **不要硬编码**到 Python / SQL
- 建 `discipline_config` 表 `(key, value)` 存这些阈值，API `GET/PATCH /api/config/discipline`
- Demo 时前端直接从后端读

### 7.7 itsuki 是零基础

- 代码注释用**中文**
- 复杂逻辑（WebSocket / ECDSA / I²C）要在 commit message 或代码注释里**解释为什么这么写**
- itsuki 看你代码时可能问"这一行什么意思"，要能用中文回答到一句话讲清

## 8. 交付 / 回报机制

### 每日结束

1. 更新 `00_admin/WIP.md` §进行中的任务 → 登记自己的进度
2. 跑一次 `bash 00_admin/hooks/pre-commit`（预演）
3. `git add` + `git commit`（commit message 中文主体，不带 Co-Authored-By trailer）
4. **不 push**（除非 itsuki 明说）

### 有需求疑问

**不要自己猜**。写到 `00_admin/demo_4-28/questions_for_requirements.md`（没有就新建）：
```markdown
## [时间] 疑问类型

**背景**：...
**具体问题**：...
**我的倾向**：A / B
**等 itsuki 回复**：
```

itsuki 看到后会同步到需求会话更新需求档。

### commit message 风格

参考 `git log` 里的历史 commit：
```
feat(backend): 加 /api/checkin WebSocket 广播

- 新增 ws_manager.broadcast 方法，推送 checkin 事件
- 前端订阅 /ws/teacher，实时更新座位表
- 覆盖 scope_tier.md §1.4 核心需求
```

**不写 Co-Authored-By trailer**（见 memory `feedback_commit_style.md`）。

## 9. 分工再次明确

| 谁 | 做什么 |
|---|---|
| **你（代码 agent）** | 前端 / 后端 / iOS / Pi 所有代码 |
| **需求会话 [Mac-demo-sprint]** | 需求文档（scope_tier / sprint / demo_script / ST25DV_fallback）+ 设计层文档 |
| **主会话 [Mac-主会话]** | v0.4.0 spec 字典 + Device_Contract（和 demo 无关）|
| **itsuki** | 采购 / iOS Shortcuts 配置 / 彩排 / Demo Day / 反馈 |

## 10. 紧急情况 fallback

如果 Dx 超时 / 卡住：

| 情况 | 应对 |
|---|---|
| 某 Tier 1 功能来不及 | 降级到 Tier 2（skeleton + mock）+ demo 时说"这部分真实数据流等下周"|
| WebSocket 整个跑不通 | Fallback 到前端 3 秒轮询 `/api/checkins/latest` |
| PN532 驱动无法调通 | Pi 程序暂时模拟（定时发固定 UID 到后端），demo 时用 iPhone tap 掩盖 |
| iOS 模拟器跑不通 | 改在老师 Web 里加"模拟学生提交外宿"按钮 |
| Pi 3A+ 硬件故障 | 点呼机降级为 Mac 本地的小 Python 脚本（Demo 时 Mac 代点呼机）|

关键原则：**demo 成功 > 代码完美**。能用变通方案保流程连贯 > 硬怼坚持完美实现。

## 11. Demo Day（4-28）当天

- 你（代码 agent）可能需要**现场待命**（修临时 bug / 网络切换 / 紧急 fallback）
- 所有设备（Mac / Pi / iPad / iPhone）demo 前 30 分钟已就位 + 测过链路
- 演示流程见 `demo_script.md`，每一步都要有对应代码支撑

## 12. 读完这份 briefing 后的第一个动作

1. 读完 §2 列出的 8 个文件
2. 登记进 WIP.md：`[Code-Agent] 接管 Demo 4-28 sprint 代码实现，4-22 开工 D2`
3. 给 itsuki 回复："briefing 读完，我起 D2 开工计划，有 3 个需求疑问要对齐"（如果有疑问）

---

**祝 demo 顺利。**

— 需求会话 [Mac-demo-sprint]，2026-04-21
