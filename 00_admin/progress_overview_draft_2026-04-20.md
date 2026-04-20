# DMSD 项目进度总览 — CC 起草 draft（2026-04-20）

> **这是什么**：CC 按 backlog D7-D13 起草的 `progress_overview.md` v0.3.1 更新版。**按 CLAUDE.md "progress_overview 起草不直写" 规则，不直接改正文。**
>
> **给 itsuki 的行动**：
> 1. 读下面内容（**关键改动有 `<!-- CC 起草 4-20 -->` 注释，可搜这个关键词快速定位**）
> 2. 同意 → 用本文件内容**替换** `00_admin/progress_overview.md`（最简单：`mv progress_overview_draft_2026-04-20.md progress_overview.md`，或手动复制粘贴）
> 3. 不同意某处 → 告诉 CC 具体哪条要回改
> 4. 合并后 backlog 里 D7 / D8 / D9 / D10 / D12 / D13 打 ✅（D11 需要 itsuki 核实 reflection 文件占位符数量后再打 ✅）
>
> **本 draft 覆盖的 backlog 条目**：D7 / D8 / D9 / D10 / D11（部分）/ D12 / D13
>
> **不覆盖（留给 itsuki 手动处理）**：
> - D1 / D2 / D3 / D4 是手笔区 → 见 `Batch3_itsuki手笔素材指引.md`
> - D5（死引用修复）—— CC 起的新版里已删除那条死引用，itsuki 审时确认

---

下面是 CC 起草的**完整 progress_overview.md 新版正文**。审核无误后整体替换原文件（本文件上面的说明段不保留）。

---

# DMSD 项目进度总览

> **最后更新**: 2026-04-20（v0.3.1 更新） <!-- CC 起草 4-20：原"2026-04-17 晚（头部版本号于 2026-04-19 改为指针）"。改为当前版本说明 + 去掉已不需要的版本号迁移脚注 -->
> **当前版本**: 见 `CHANGELOG.md` 顶部（单源真值，见 `00_admin/文档同步点清单.md §1`）
> **版本细粒度**: CHANGELOG 于 2026-04-17 晚重建，pre-0.1 追认 + 2-02 至今每个实质节点一条 patch（4-19 / 4-20 持续细粒度化）
>
> 这是项目的**当前状态快照**。详细日志、问题解决、决策过程在 `05_logs/` 下。**AC 素材已迁 iCloud**（不在 git）。

---

## 项目简介

**DMSD**（Dormitory Management System Digitalization）— 宿舍管理系统电子化

把宿舍的纸质点呼考勤、纪律管理流程数字化，通过 NFC 卡 + 服务器 + 手机 App（iOS + Android）+ 墙上专用点呼机实现。

- **开发者**: itsuki（一个人，零基础起步）
- **起始时间**: 2026 年 2 月
- **GitHub**: https://github.com/otogi2025/DMSD（私有仓库）
- **升学目标**: 筑波大学 情報学群 情報科学類 AC 入試（2027 年 4 月入学）

---

## 上线姿态（2026-04-19 G2 决策） <!-- CC 起草 4-20：整章替换原"分阶段策略（2026-04-12 决定）"。G2 决策后原 Phase 1/Phase 2 分阶段已取消 -->

**v1.0 直接一次上线**：NFC 卡 + iOS + Android 三路径同时部署。**不再做"先上卡再上 App"的分阶段**。

- **三路径并存**：
  - A 路径：NFC 卡 tap 点呼机（PN532 读头）
  - B 路径：iPhone tap 外贴 NFC 动态贴纸（ST25DV16K，2026-04-20 决定）
  - B 路径：Android tap 同一贴纸（不走 HCE，跨平台一致）
- **没智能手机的学生继续用卡** —— 无人被排除
- **开发节奏**：内部按 M1→M5 里程碑推进。兜底规则：做不完至少 M1+M2 可 demo

---

## 系统架构

```
  点呼室入口                          VPS 服务器
┌─────────────┐                  ┌──────────────┐
│ 点呼机 ×4   │───── WiFi ──────→│              │
│ (Pi 4B 2GB  │←── 学生名字 ─────│  FastAPI     │
│  + PN532    │                  │  + PostgreSQL│
│  + ST25DV   │                  │              │
│  + 扬声器)  │                  └──────┬───────┘
└─────────────┘                         │ WiFi
                                        ↓
                                 ┌──────────────┐
                                 │ 老师 iPad     │
                                 │ (Web 管理界面)│
                                 └──────────────┘
                                        │
                                        ↓
                                 ┌─────────────────────────────┐
                                 │ 学生手机（iOS + Android）    │
                                 │ tap 贴纸自动唤 App 签到      │
                                 │ BTR + Universal Link + AASA │
                                 └─────────────────────────────┘
```

<!-- CC 起草 4-20：原图只画"点呼机 A/B"两台 + 老师 iPad + Phase 2 学生手机。改为反映 4-20 决策：4 台点呼机 / Pi 4B 2GB + PN532 + ST25DV 动态贴纸 / iOS+Android 同时在架构里 -->

---

## 核心功能: 点呼系统

### 流程

1. 老师在管理端点击"开始点呼"
2. 学生的操作三选一：
   - **卡路径**：把 NFC 卡贴到点呼机
   - **iPhone 路径**：掏出手机碰一下贴纸（BTR 自动唤 DMSD App）
   - **Android 路径**：同上（系统级 NFC 意图触发 App）
3. 点呼机/App 读到身份 → 发后端 → 后端唯一判定（准时/迟到/缺席）
4. **点呼机扬声器播报学生姓名**（防作弊关键设计）
5. 老师站在旁边对照人脸
6. 老师可以手动改判（需填写理由，系统留审计记录）
7. 到时间未结束 → 系统自动结束并结算

### 纪律规则

- 迟到: +0.5 分
- 缺席: +1.0 分
- 月累计 ≥ 4.0 → 下月罚扫
- 月累计 ≥ 9.0 → 下月禁足

### 防作弊核心: 语音播报

见 [`00_admin/原创设计_语音播报防作弊.md`](./原创设计_语音播报防作弊.md)（2026-04-20 新建 showcase）。 <!-- CC 起草 4-20：原文没有链接，现有 showcase 文档了，直接指 -->

### 防作弊补充（2026-04-20）: 动态 NFC 贴纸 <!-- CC 起草 4-20：新章 -->

路径 B 的 NFC 贴纸使用 ST25DV16K（I²C 可动态写入），点呼机每 10 秒刷新贴纸里的 URL（含一次性 nonce），防止学生复制 URL 在宿舍房间"隔空签到"。详见 `05_logs/raw/2026-04-20.md §16:00`。

---

## 整体进度

### 阶段 0: 规格设计 ✅ 已完成（2026-02 月）

- [x] 确定项目范围和功能边界
- [x] 编写点呼规格书（RollCall_Spec v0.1）
- [x] 定义 API 约定、枚举字典、字段字典、错误码
- [x] 编写 8 条验收测试场景
- [x] 编写可执行开发清单（已归档至 `99_archive/`）
- [x] v0.1 规格冻结（2026-02-12）

### 阶段 0.5: 架构决策 ✅ 已完成（2026-04-12 / 4-15 / 4-17 / 4-19 / 4-20 多次迭代） <!-- CC 起草 4-20：原"2026-04-12 完成"过于简单，现在是多次迭代 -->

- [x] NFC vs 二维码技术选型
- [x] 卡 vs 手机架构 → 原分阶段策略（4-12）
- [x] 点呼机硬件方案：Raspberry Pi + PN532
- [x] 语音播报防作弊设计
- [x] 核心架构原则"点呼机只搬运，业务判断全在后端"（4-15 thin client / thick server）
- [x] Phase 2 双路径重设（4-15，iPhone 不走 HCE，读点呼机外贴标签）
- [x] spec 主体 rewrite + Q1-Q5 硬决策 + 字典三件套重构（4-17）
- [x] **G2 决策：取消分阶段，v1.0 一次上**（4-19）
- [x] NFC 卡完整生命周期 + App 账号规则 + Android 路线（4-19）
- [x] iPhone tap 贴纸技术细节 BTR + Universal Link + AASA（4-20）
- [x] URL 复制漏洞 → 动态 NFC 贴纸 ST25DV16K（4-20）
- [x] Pi 4B 2GB × 4 台确认（4-20）

### 阶段 0.6: 版本管理与记录体系 ✅ 已完成（2026-04-13 / 4-17 / 4-19 迭代） <!-- CC 起草 4-20：backlog D7 —— 原"已完成 2026-04-13" 漏了后续 -->

- [x] SemVer 语义化版本规范确立（4-13）
- [x] 所有 spec 文件 v1.0 → v0.1 重命名（4-13）
- [x] 建立 `CHANGELOG.md`（4-13）
- [x] AC 记录体系 v3（raw + polished + 双日期 + decision_log + interview_log + monthly_review，4-13）
- [x] 版本管理实践指南移至 iCloud 通用指南（4-13）
- [x] **CHANGELOG 细粒度化 + pre-0.1 追认 6 条**（4-17）
- [x] **文档同步机制 A+B+C**（单源真值清单 + CLAUDE.md 一致性规则节 + pre-commit hook，4-19）
- [x] **项目审查 backlog 87 条 + Tier 0-4 版本路线图**（4-19）

### 阶段 1: 项目搭建 ✅ 已完成（2026-03-10）

- [x] Mac 本地建立项目目录
- [x] 学会 Git 基础（init, add, commit, push, pull, status, log）
- [x] 创建 GitHub 私有仓库并推送代码
- [x] VPS 上克隆项目并配置 Git
- [x] 建立 Mac ↔ GitHub 的同步流程 <!-- CC 起草 4-20：memory 说 VPS 已停用 DMSD，去掉 VPS 字样 -->

### 阶段 2: 编程学习 🔄 Python Day 2+ 延后 <!-- CC 起草 4-20：backlog D3 —— 原"进行中"不准确。Python Day 1 在 3-11 学的，到 4-20 = 40 天没动。坦诚说"延后"更真实 -->

- [x] Python 第 1 天: 变量、数据类型（str/int/float/bool）、print、if/elif/else（2026-03-11）
- [ ] **Python Day 2+ 主动延后** —— 3-11 到 4-20 期间优先把 spec 和架构做完整。理由：没有真实工程需求时单独学 Python 驱动力不够（4-10 回归日认知）；等 Batch 1 架构完全定稿后（约 M1 开工前）再续学
- [ ] Swift 基础学习（iOS App 开工前）
- [ ] SwiftUI 基础学习
- [ ] Kotlin / Android 基础学习（Android App 开工前）

### 阶段 3: 后端开发 ⬜ 未开始（对应 M2-M3）

- [ ] VPS 安装 PostgreSQL
- [ ] FastAPI 项目骨架搭建
- [ ] 数据库建表与迁移（从 `FIELD_REGISTRY` 直接转）
- [ ] 登录与权限系统
- [ ] 点呼核心 API（开始/签到/结束）
- [ ] 改判与审计日志
- [ ] 健康上报、不点呼申请
- [ ] 扣分系统与纪律报表

### 阶段 4: 点呼机设备开发 ⬜ 未开始（对应 M2） <!-- CC 起草 4-20：原"Phase 1 关键" 改为 M2，因为 G2 取消 Phase 分层 -->

- [x] 硬件型号敲定：Pi 4B 2GB × 4 台 + PN532 + ST25DV16K × 4 + 扬声器（4-20）
- [ ] 采购（itsuki 中国跨境下单）
- [ ] Raspberry Pi 系统安装与配置
- [ ] NFC 读卡 Python 代码（nfcpy）
- [ ] HTTP 通信后端
- [ ] WebSocket 接收后端推送
- [ ] ST25DV16K I²C 动态写入（nonce 10 秒刷新）
- [ ] 语音播报（pyttsx3）
- [ ] 外壳 + 贴墙安装

### 阶段 5: 老师端 Web/iPad 界面 ⬜ 未开始（对应 M3-M4）

### 阶段 6: 学生 App ⬜ 未开始（对应 M4，iOS + Android 同步） <!-- CC 起草 4-20：原"iOS 学生 App Phase 2" + "Android 学生 App Phase 2"。G2 后改为 M4 一并做 -->

- iOS 走 Swift / SwiftUI / Core NFC / Universal Link
- Android 走 Kotlin（Java 作为备选）/ NFC 贴纸 Intent / 自建网站分发 APK

### 阶段 7: 部署与试运行 ⬜ 未开始（对应 M5）

---

## 技术学习时间线 <!-- CC 起草 4-20：backlog D8 补 4-15/4-17/4-19/4-20 -->

| 日期 | 学了什么 | 关键收获 |
|------|---------|---------|
| 2026-02 月 | 项目规格设计 | 学会如何定义系统需求、冻结范围、写规格文档 |
| 2026-03-10 | Git 基础 | 理解版本控制的意义，建立多设备同步流程 |
| 2026-03-11 | Python 变量、数据类型、条件判断 | 第一次写代码并运行 |
| 2026-03-11 | 前端/后端/API/数据库概念 | 理解整个系统的通信架构 |
| 2026-04-10 | NFC 与 NFD（Unicode normalization） | 跨平台开发的隐藏坑 |
| 2026-04-12 | NFC 原理（电磁感应 + 13.56MHz + UID） | NFC 不是黑科技，是高中物理的应用 |
| 2026-04-12 | iOS Core NFC 框架 + SwiftUI 基础 | 读卡核心逻辑 ~60 行 Swift |
| 2026-04-12 | Python nfcpy + pyttsx3 | Raspberry Pi 设备端代码 ~20 行 |
| 2026-04-13 | SemVer 语义化版本规范 | 版本号是给"发布"用的，不是每次 commit |
| **2026-04-15** | **thin client / thick server 原则** | **从反驳 AI 过度配置推导出的架构原则** |
| **2026-04-15** | **iOS 平台 SE / HCE 限制** | **第三方 App 不能伪装 NFC 卡，决定双路径架构** |
| **2026-04-17** | **字典三件套 + 单源真值** | **数据一致性从设计层保证，不靠纪律** |
| **2026-04-19** | **文档同步三件套（单源 + 清单 + hook）** | **把"多源漂移"这种系统病用工程手段根治** |
| **2026-04-20** | **iOS BTR + Universal Link + AASA** | **学生碰一下不用开 App = 7 步变 2 步** |
| **2026-04-20** | **静态 URL 攻击面 + 动态 NFC 标签 ST25DV** | **"知道 URL ≠ 到场"，静态凭证不能当身份证明** |

---

## 关键决策记录（索引） <!-- CC 起草 4-20：backlog D9 补 4-15/4-17/4-19/4-20 -->

详细前因后果见 `05_logs/decision_log.md`。

| 日期 | 决策 |
|------|------|
| 2026-02-12 | v0.1 规格冻结 |
| 2026-03-10 | 用 Git + GitHub 管理代码 |
| 2026-03-11 | 练习代码放 `~/dev/practice/`，不放 DMSD |
| 2026-03-11 | 用 Claude Code 辅助开发 |
| 2026-04-10 | 学习方法: 从"先学完再做"改为"边做边学 + AI 辅助" |
| 2026-04-12 | NFC 而非二维码（防作弊） |
| 2026-04-12 | 原分阶段上线策略（已被 4-19 G2 取代） |
| 2026-04-12 | 点呼机 = Raspberry Pi（不是 iPad） |
| 2026-04-12 | **语音播报防作弊设计**（原创） |
| 2026-04-13 | 版本号体系重置 v1.0 → v0.1 |
| **2026-04-15** | **点呼机架构原则: "只搬运数据，业务判断全在后端"** |
| **2026-04-15** | **Phase 2 双路径: iPhone 读静态贴纸，不走 HCE** |
| **2026-04-15** | **点呼机硬件: A(RPi)/B(ESP32) 全维度对比后确认 A** |
| **2026-04-17** | **spec 主体 rewrite + Q1-Q5 硬决策 + 字典三件套** |
| **2026-04-19** | **G2 决策: 取消分阶段，v1.0 一次上**（iOS + Android + 卡） |
| **2026-04-19** | **NFC 卡完整生命周期 + App 账号规则 + 三路径幂等** |
| **2026-04-19** | **文档同步机制 A+B+C**（单源 + 清单 + hook） |
| **2026-04-20** | **iPhone BTR + Universal Link 方案** |
| **2026-04-20** | **动态 NFC 贴纸 ST25DV16K** |
| **2026-04-20** | **Pi 4B 2GB × 4 台确认** |

---

## 问题解决记录（索引） <!-- CC 起草 4-20：backlog D10 补 4-15 三条 -->

详细记录在 `05_logs/problem_solving/`。

| 日期 | 问题 | 类型 |
|------|------|-----|
| 2026-03-10 | tar 打包报错 "no files or directories specified" | 命令行 |
| 2026-03-10 | scp 传文件缺少目标路径 | 命令行 |
| 2026-03-11 | Python NameError（变量未定义） | 编程 |
| 2026-03-11 | Python 布尔值必须大写 True/False | 编程 |
| 2026-04-10 | Git pull 失败: NFC vs NFD 跨平台编码差异 | Git / 跨平台 |
| **2026-04-15** | **AI 过度配置诊断（Pi 4B 4GB ¥541 太贵）** | 协作 |
| **2026-04-15** | **iOS 限制下的 UID 统一模型重构** | 架构 |
| **2026-04-15** | **spec gap 发现（v0.1 完全没写点呼机契约）** | 规格 |
| **2026-04-20** | **静态 URL 可被复制 → 动态 NFC 贴纸** | 安全 |

---

## 开发环境 <!-- CC 起草 4-20：memory 说 VPS 已停用 DMSD，去掉 -->

- **家里 Mac** → 本地（`~/dev/DMSD`）Claude Code + Xcode（iOS 开发）+ VS Code（Python 练习） <!-- 4-19 itsuki 决定不再用 VPS 推 DMSD -->
- 通过 GitHub 同步代码

---

## 当前待办

完整清单见 `00_admin/TODO.md` + `00_admin/2026-04-19_项目审查_backlog.md`。下面是重点。

### 优先（短期 / v0.3.x patch）

- [ ] 填 iCloud `AC素材_成品/reflection/reflection_2026-04-10_一个月的空白.md` 的占位符 <!-- CC 起草 4-20：backlog D11 —— 原文说"5 个"，TODO 说"4 个"。实际数字需 itsuki 打开 iCloud 文件核实后更新 -->
- [ ] 回答 iCloud `AC素材_成品/ac_入試准备/项目起源_真实观察.md` 的 AC 起源问题
- [ ] `decision_log.md` 补 4-17 Q1-Q5 / 字典重构 / spec rewrite / 4-19 G2 / 4-20 BTR + ST25DV + Pi 2GB
- [ ] `project_evolution.md` 补 4-15 / 4-17 / 4-19 / 4-20 四次重大转折
- [ ] `learning_path.md` 补 PostgreSQL 选型回答 + Python Day 2 坦诚说"延后"

### 中期（v0.4.0 minor）

- [ ] 新建 `01_specs/rollcall/Device_Contract.md`（点呼机契约 spec）
- [ ] 拍板 spec 附录 D 剩余 🔄 项
- [ ] 修 spec 内部逻辑漏洞（详见 backlog S1-S20）
- [ ] 4 个 `.pages` 转 Markdown
- [ ] `03_dev/Student/DMSDStudentApp(iOS)/` 归档
- [ ] spec 文件去 `_v0.1` 后缀（按版本管理指南 §5 推荐）

### 长期

- [ ] 采购 Pi 4B 2GB × 4 + ST25DV16K × 4 + PN532 + 扬声器
- [ ] 搭建第一台点呼机原型（M2 里程碑）
- [ ] 和真人讨论项目（iCloud `04_素材_成品/interview_log/`）
- [ ] 月度回顾（iCloud `04_素材_成品/monthly_review/`）

---

## 仓库结构地图 <!-- CC 起草 4-20：backlog D12/D13 —— 删 executable_dev_checklist（已归档）、删 目录架构.md（已删除）、加 backlog / 文档同步点清单 / hooks/ / 原创设计 showcase -->

```
DMSD/
├── README.md                           项目门面（2026-04-20 新建）
├── CHANGELOG.md                        版本变更记录（单源真值）
├── CLAUDE.md                           Claude Code 项目指令
├── .gitignore
├── 00_admin/                           项目管理
│   ├── progress_overview.md            ← 本文件
│   ├── WIP.md                          当前工作状态（多会话协调）
│   ├── TODO.md                         itsuki 主待办
│   ├── 文档同步点清单.md                 共享信息单源清单（2026-04-19 新建）
│   ├── 2026-04-19_项目审查_backlog.md   87 条漏洞清单 + Tier 0-4 路线（2026-04-19 新建）
│   ├── 原创设计_语音播报防作弊.md         核心原创设计 showcase（2026-04-20 新建）
│   ├── CLAUDE_CODE_记录指南.md          AC 记录操作手册
│   ├── create_local_dev_symlink.sh
│   └── hooks/                          git 钩子（2026-04-19 新建）
│       ├── pre-commit                  声明性文件版本号硬编码拦截
│       ├── install.sh
│       └── README.md
├── 01_specs/                           规格文档（v0.1 冻结，内容在 v0.3 主体迭代）
│   ├── API_CONVENTIONS_v0.1.md
│   ├── API_Contract_v0.1.pages
│   ├── IA_UI_v0.1.pages
│   ├── Overview_of_Features_v0.1.pages
│   ├── v0.1完整计划.pdf
│   └── rollcall/
│       ├── RollCall_Spec_v0.1.md       spec 主体（v0.3.0 rewrite 后 958 行）
│       ├── RollCall_Spec_v0.1.pages    原稿
│       ├── DMSDv0.1验收脚本.pages
│       ├── FIELD_REGISTRY_v0.1.md
│       ├── ENUM_REGISTRY_v0.1.md
│       ├── ERROR_CODES_v0.1.md
│       ├── DEVICE_REGISTRY_v0.1.md
│       └── v0.1_冻结决策.md
├── 03_dev/                             代码（待开始）
│   └── Student/DMSDStudentApp(iOS)/    早期 throwaway 代码，v0.4.0 前归档
├── 05_logs/                            DMSD 开发 log（AC 纯素材已迁 iCloud）
│   ├── decision_log.md                 itsuki 手写决策索引
│   ├── learning_path.md
│   ├── project_evolution.md
│   ├── raw/                            CC 每日 dump（YYYY-MM-DD.md）
│   ├── dev_log/                        itsuki 自己写的叙述式日志
│   └── problem_solving/                问题解决记录
└── 99_archive/                         归档
    ├── 2025-12_早期GPT对话/
    ├── NFC_NFD_鬼影文件/
    └── 2026-04-12_executable_dev_checklist_v0.1.md
```

---

**END** — progress_overview.md v0.3.1 版
