# DMSD 项目进度总览

> **最后更新**: 2026-05-04（章节里程碑大刷新 — itsuki 让 CC 改）
> **当前版本**: 见 `CHANGELOG.md` 顶部（单源真值，见 `00_admin/文档同步点清单.md §1`）
> **版本细粒度**: CHANGELOG 已于 2026-04-17 晚重建，pre-0.1 追认 + 2-02 至今每个实质节点一条 patch
>
> 这是项目的**当前状态快照**。详细的日志、问题解决、决策过程在 `05_logs/` 下。
>
> **2026-05-04 章节里程碑刷新**（CC 直写）：
> - §分阶段策略 加 4-19 G2 决策更新 note（Phase 1/2 已取消，v1.0 完整版直接上线）
> - §纪律规则 修正 ≥9 → ≥8（4-29 itsuki 拍板单源真值，详见 `00_admin/文档同步点清单.md §10`）
> - §阶段 3-7 从「⬜ 未开始」更新为「🔄 进行中」+ 列 v0.4-v0.8 已完成 milestone
> - 加 §项目里程碑（v0.4 - v0.8）— 4 月底到 5 月初的密集推进总览
> - §关键决策记录 加 4-19 / 4-29 / 5-03 / 5-04 新决策

---

## 项目简介

- **项目名**（仓库/开发代号）：**DMSD**（Dormitory Management System Digitalization）
- **系统/产品名**（对外）：**Tomoshibi**（灯火 / ともしび，2026-04-21 定名）

把宿舍的纸质点呼考勤、纪律管理流程数字化,通过 NFC 卡 + 后端服务器 + 手机 App 实现。

- **开发者**: itsuki(一个人,零基础起步)
- **起始时间**: 2026 年 2 月
- **GitHub**: https://github.com/otogi2025/DMSD (私有仓库)

---

## 分阶段策略

> **⚠️ 2026-04-19 G2 决策更新（取消分阶段）**：原计划「Phase 1 = 卡 + 点呼机 / Phase 2 = 手机 App」已废弃。**v1.0 直接 iOS + Android + 卡 一次上线**。理由：4-19 itsuki 拍板「分阶段会让用户体验割裂、维护双套逻辑增本」。
>
> 内部开发节奏仍按 M1→M5 里程碑（兜底：做不完至少 M1+M2 可 demo）。
>
> 详见 `CHANGELOG.md` v0.4 段 + `00_admin/文档同步点清单.md §4`。

### 4-19 之前的旧分阶段（保留作历史记录）

| 阶段 | 内容 | 不需要 |
|------|------|--------|
| ~~Phase 1~~ | ~~NFC 卡 + 后端 + 点呼机(Raspberry Pi)~~ | ~~学生 App~~ |
| ~~Phase 2~~ | ~~加手机 App(iOS + Android)~~ | ~~—~~ |

---

## 系统架构

```
  点呼室入口                          VPS 服务器
┌─────────────┐                  ┌──────────────┐
│ 点呼机 A    │───── WiFi ──────→│              │
│ (树莓派+NFC)│←── 学生名字 ─────│  FastAPI     │
│ + 扬声器    │                  │  + PostgreSQL│
└─────────────┘                  │              │
                                 │              │
┌─────────────┐                  │              │
│ 点呼机 B    │───── WiFi ──────→│              │
│ (树莓派+NFC)│←── 学生名字 ─────│              │
│ + 扬声器    │                  └──────┬───────┘
└─────────────┘                         │ WiFi
                                        ↓
                                 ┌──────────────┐
                                 │ 老师 iPad     │
                                 │ (管理界面)    │
                                 └──────────────┘

Phase 2 追加:
┌─────────────────────────────────┐
│ 学生手机 App (iOS + Android)     │ 直接碰固定 NFC 点签到,或查看自己数据
└─────────────────────────────────┘
```

---

## 核心功能: 点呼系统

### 流程

1. 老师在管理端点击"开始点呼"
2. 学生把 NFC 卡(或 Phase 2 的手机)贴到点呼机
3. 点呼机读到 UID → 发给后端 → 返回学生姓名
4. **点呼机扬声器播报学生姓名**(防作弊关键设计)
5. 老师站在旁边对照人脸
6. 系统自动判定: 准时 / 迟到 / 缺席
7. 老师可以手动改判(需填写理由,系统留审计记录)
8. 到时间未结束 → 系统自动结束并结算

### 纪律规则

- 迟到: +0.5 分
- 缺席: +1.0 分
- 月累计 ≥ 4.0 → 下月罚扫
- 月累计 ≥ 8.0 → 下月禁足

> 2026-04-29 itsuki 拍板把禁足阈值从 ≥9 改为 ≥8（含等于）。单源真值见 `00_admin/文档同步点清单.md §10` + `01_specs/rollcall/v0.1_冻结决策.md §1`。

### 防作弊核心: 语音播报

点呼机读卡后自动播报学生姓名,老师人眼对照。把"机器识别身份"和"老师人眼识别"实时配对,攻击者必须本人到场(详见 `05_logs/decision_log.md`)。

---

## 整体进度

### 阶段 0: 规格设计 ✅ 已完成(2026-02 月)

- [x] 确定项目范围和功能边界
- [x] 编写点呼规格书(RollCall_Spec_v0.1)
- [x] 定义 API 约定、枚举字典、字段字典、错误码
- [x] 编写 8 条验收测试场景
- [x] 编写可执行开发清单
- [x] v0.1 规格冻结(2026-02-12)

### 阶段 0.5: 架构决策 ✅ 已完成(2026-04-12)

- [x] NFC vs 二维码技术选型
- [x] 卡 vs 手机架构 → 分阶段策略
- [x] 点呼机硬件方案: Raspberry Pi + PN532
- [x] 语音播报防作弊设计
- [x] 更新 `executable_dev_checklist.md`

### 阶段 0.6: 版本管理与记录体系 ✅ 已完成(2026-04-13)

- [x] SemVer 语义化版本规范确立
- [x] 所有 spec 文件 v1.0 → v0.1 重命名
- [x] 建立 `CHANGELOG.md`
- [x] 建立 AC 记录体系(raw/ + polished/ + 双日期 + decision_log + interview_log + monthly_review)
- [x] 版本管理实践指南(移至 iCloud 通用指南)

### 阶段 1: 项目搭建 ✅ 已完成(2026-03-10)

- [x] Mac 本地建立项目目录
- [x] 学会 Git 基础(init, add, commit, push, pull, status, log)
- [x] 创建 GitHub 私有仓库并推送代码
- [x] VPS 上克隆项目并配置 Git
- [x] 建立 Mac ↔ GitHub ↔ VPS 的同步流程

### 阶段 2: 编程学习 🔄 进行中

- [x] Python 第 1 天: 变量、数据类型(str/int/float/bool)、print、if/elif/else
- [ ] Python 第 2 天: for 循环、列表(list)
- [ ] Python 第 3 天: while 循环、字典(dict)
- [ ] Python 第 4 天: 函数(function)
- [ ] Python 第 5 天: 类(class)
- [ ] Swift 基础学习
- [ ] SwiftUI 基础学习

### 阶段 3: 后端开发 🔄 进行中（v0.7 - v0.8 大量推进）

- [x] FastAPI 项目骨架搭建（v0.7）
- [x] SQLite + Alembic migration 框架（v0.7-v0.8）
- [x] 数据库建表（students / accounts / teachers / applications / approvals / audit_log / study_* / rollcall_* / teacher_invitations）
- [x] 登录与权限系统（JWT + Keychain 持久化）
- [x] 出寮届 API（create / list / detail / update / approve / reject / audit log）
- [x] 学習出席 API（attendees / checkin / finalize / absence-request / decision）
- [x] 点呼 API（rollcall.py — sessions / checkin / events / board / summary）
- [x] 教师管理 API（invitation / register）
- [x] **学生注册码 API**（admin/registration-code/{current,refresh,history} + POST /accounts 校验）— 2026-05-04 加，App Store 上架对策（v1.0）
- [x] **老师公告 API**（announcements 列表/详情/未读数/回复发删 + 老师投稿/编辑/软删）— 2026-05-04 加（v1.0）
- [x] 邮件通知（SendGrid 框架）
- [x] 食堂 Excel 导出
- [x] pytest 测试套件（37 case 全 pass — 含 12 注册码 + 6 公告新测试）
- [ ] 扣分系统 cron job（自动月结算）
- [ ] PostgreSQL 切换（v1.0 上线前从 SQLite 迁移）
- [ ] 部署到 VPS（uvicorn + nginx + systemd）

### 阶段 4: 点呼机设备开发 ⬜ 未开始

- [ ] 采购 Raspberry Pi 4B 2GB × 4（已拍板，¥1200 RMB，等管理员采纳后扩容）
- [ ] 采购动态 NFC 贴纸 ST25DV16K × 4（¥25 × 4 = ¥100 RMB，10 秒 nonce 刷新）
- [ ] Raspberry Pi 系统安装与配置
- [ ] NFC 读卡 Python 代码（I²C PN532）
- [ ] ECDSA 签名校验
- [ ] HTTP 通信后端 + session 幂等
- [ ] 语音播报（pyttsx3）
- [ ] 外壳 + 贴墙安装

### 阶段 5: 老师端 Web/iPad 界面 🔄 进行中

- [x] teacher_web v1 启动（TS + Vite + Zustand，5 page 起手）— v0.8
- [x] Demo 接真后端（demo_server.py 加 /api/v1/ 代理 + JWT 真实认证）
- [x] 学習管理全屏会话（StudyLanding + LiveStudySession + 3-tap NFC + 相位条）
- [x] iPad 点呼 live-roll-call.jsx（Demo 4-28 用过）
- [ ] 学生注册码生成面板（v1.0 待实装，spec §7.16.5）
- [ ] 老师公告投稿 / 编辑 / 删除 / 回复管理面板（v1.0 待实装，spec §7.15.7）
- [ ] 出寮届审批 chain（pending list + approve/reject + 评论）
- [ ] 出寮者一覧 PC 端（事務室 + 1·2 寮 / 4 寮 分别表示，§7.8 + R4）
- [ ] 学生指导履历 / 事案录入（§7.9）
- [ ] 学生个人数据汇总 view（§7.10）

### 阶段 6: iOS 学生 App 🔄 进行中（v0.8 推进）

- [x] iOS 网络层完整建设（APIClient + KeychainService + Endpoints/ + NetworkModels）
- [x] AppStore 切真后端（login + applications + study）
- [x] iOS↔backend 字段对齐（F1-F5 + Q1 7 处失配修复）
- [x] 5 大功能屏完整体（Auth / Home / Apply / MyPage / Schedule / StayList / Bus / Study / NfcScan / RollCallSheet）
- [x] **注册码 RegisterStep5**（POST /accounts wire 通 + RegistrationDraft 累积 Step1-4 真字段）— 2026-05-04 加（v1.0）
- [x] **老师公告 列表/详情/回复 view**（最小可工作版）— 2026-05-04 加（v1.0）
- [x] Apple Image Playground 集成（注册时 AI 头像生成，iOS 18.2+）
- [ ] AI 摘要（Foundation Models, iOS 26）— v1.1
- [ ] 翻译（Translation framework, iOS 17.4+）— v1.1
- [ ] Push 通知（APNs）— v1.1

### 阶段 7: Android 学生 App 🔄 进行中（v0.8 bootstrap）

- [x] Compose 工程框架从零搭建（21 个 .kt + 10 屏 UI）— v0.8
- [x] 独立 repo `otogi2025/Tomoshibi-Android` public
- [x] 实装方针拍板：CC 主导逐屏对译 Compose（不派 sub agent）
- [ ] 注册码 RegisterStep5 镜像 iOS（v1.0 待实装）
- [ ] 老师公告 列表/详情/回复 view（v1.0 待实装）
- [ ] Push 通知（FCM）— v1.1

### 阶段 8: 部署与试运行 ⬜ 未开始

- [ ] PostgreSQL 部署到 VPS
- [ ] FastAPI uvicorn + nginx + systemd
- [ ] iOS App Store 上架（Apple Developer Program 已付，99 USD/年）
- [ ] Android Google Play 上架
- [ ] 点呼机 4 台部署到宿舍
- [ ] keystore 备份（本地 Mac + 后端服务器加密 + 纸质密码）

---

## 项目里程碑（v0.4 - v0.8）

> 4 月底到 5 月初的密集推进总览。详细 commit 历史 → `git log` / `CHANGELOG.md`。

| 版本 | 日期 | 主题 | 重点产出 |
|---|---|---|---|
| **v0.4 - v0.5** | 2026-04-17 → 04-29 | RollCall spec 重写 + 项目审查 + 文档体系建立 | RollCall_Spec v0.2 字典三件套 + v0.3 主体重写 / 项目审查 backlog 87 条 / 单源真值 + 同步点清单 + pre-commit hook 三件套 |
| **v0.6** | 2026-04-29 | 老师反馈 38 条受领 + 系统功能大重写 | 老师 LINE 38 条要件清单 + R1-R4 硬约束 / system_features.md 中文骨架大重写 / Demo 4-28 给宿舍管理员演示 + 4-29 口头同意采纳 |
| **v0.7** | 2026-04-30 | 三轨 A+B+C 同日完成 38 条消化 | A 状态盘点 / B §9 拍板 / C 实装 brief 起草（backend / iOS / Web 各端 REQUIREMENTS / DESIGN_LOG）+ 帰省実物表 evidence 入手 |
| **v0.8** | 2026-05-02 | 三端代码层全启动 | Android Compose bootstrap（21 .kt + 10 屏）/ iOS 网络层完整建设 + AppStore 切真后端 / teacher_web v1 TS+Vite+Zustand 升级 + 5 page / backend rollcall+study+teachers routers + Alembic / iOS↔backend 字段对齐 F1-F5+Q1 |
| **v0.8 之后**（pending bump）| 2026-05-03 → 05-04 | 注册码 + 公告 + 文件联动工具 | App Store 上架对策（学生注册码 6 桁 5 分钟有效）/ 老师公告功能（4 端，backend + iOS 完成）/ A+B 文件联动工具（pre-commit + sync-check.sh + 13 条规则代码化）/ 中文铁律加重（被骂 3 次后扩到规范文档）|

---

## 技术学习时间线

| 日期 | 学了什么 | 关键收获 |
|------|---------|---------|
| 2026-02 月 | 项目规格设计 | 学会如何定义系统需求、冻结范围、写规格文档 |
| 2026-03-10 | Git 基础 | 理解版本控制的意义,建立多设备同步流程 |
| 2026-03-11 | Python 变量、数据类型、条件判断 | 第一次写代码并运行 |
| 2026-03-11 | 前端/后端/API/数据库概念 | 理解整个系统的通信架构 |
| 2026-04-10 | NFC 与 NFD(Unicode normalization) | 跨平台开发的隐藏坑,错误信息可能是误导 |
| 2026-04-12 | NFC 原理(电磁感应 + 13.56MHz + UID) | NFC 不是黑科技,是高中物理的应用 |
| 2026-04-12 | iOS Core NFC 框架 + SwiftUI 基础 | 读卡核心逻辑 ~60 行 Swift |
| 2026-04-12 | Python nfcpy + pyttsx3 | Raspberry Pi 设备端代码 ~20 行 |
| 2026-04-13 | SemVer 语义化版本规范 | 版本号是给"发布"用的,不是每次 commit |

---

## 关键决策记录(索引)

详细前因后果见 `05_logs/decision_log.md`。

| 日期 | 决策 |
|------|------|
| 2026-02-12 | v0.1 规格冻结 |
| 2026-03-10 | 用 Git + GitHub 管理代码 |
| 2026-03-11 | 练习代码放 ~/dev/practice/,不放 DMSD |
| 2026-03-11 | 用 Claude Code 辅助开发 |
| 2026-04-12 | NFC 而非二维码(防作弊) |
| 2026-04-12 | 分阶段上线(Phase 1 卡 + Phase 2 App) |
| 2026-04-12 | 点呼机 = Raspberry Pi(不是 iPad) |
| 2026-04-12 | 语音播报防作弊设计 |
| 2026-04-13 | 版本号体系重置 v1.0 → v0.1 |
| 2026-04-19 | **G2 决策：取消分阶段，v1.0 直接 iOS + Android + 卡 一次上线** |
| 2026-04-19 | 单源真值 + 同步点清单 + pre-commit hook 三件套确立（防止文档版本号漂移）|
| 2026-04-20 | 动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ Pi 4B 2GB × 4 采购拍板 |
| 2026-04-21 | 系统 / 产品名定为 **Tomoshibi**（灯火 / ともしび）|
| 2026-04-28 | Demo 4-28 给宿舍管理员演示（NFC → 后端 → iPad 座位变绿 + 语音播报）|
| 2026-04-29 | 管理员口头同意采纳系统；GitHub repo 首次 public |
| 2026-04-29 | 老师 LINE 反馈 38 条要件 + R1-R4 硬约束（邮件通知 / 老龄 UX 一本道 / 教师单独账号 / 1·2 寮 4 寮分别表示）|
| 2026-04-29 | 禁足阈值 ≥9 → ≥8 单源真值统一 |
| 2026-05-02 | Android 实装方针拍板：CC 主导逐屏对译 Compose（不派 sub agent）|
| 2026-05-03 | **学生注册码拍板**（教师生成 6 桁数字、5 分钟有效）— App Store 上架对策 |
| 2026-05-03 | **老师公告功能拍板**（Classroom 风、scope=all/male/female、学生回复全员互见）|
| 2026-05-03 | Apple Intelligence on-device AI 路线统一（Image Playground 头像 / Foundation Models 摘要 / Translation framework）|
| 2026-05-04 | A+B 文件联动工具拍板（pre-commit 内容检查 + bin/sync-check.sh 中途随时查）|
| 2026-05-04 | 中文铁律强化（覆盖范围扩到规范文档、被骂 3 次）|

---

## 问题解决记录(索引)

详细记录在 `05_logs/problem_solving/`。

| 日期 | 问题 | 类型 |
|------|------|-----|
| 2026-03-10 | tar 打包报错 "no files or directories specified" | 命令行 |
| 2026-03-10 | scp 传文件缺少目标路径 | 命令行 |
| 2026-03-11 | Python NameError(变量未定义) | 编程 |
| 2026-03-11 | Python 布尔值必须大写 True/False | 编程 |
| 2026-04-10 | Git pull 失败: NFC vs NFD 跨平台编码差异 | Git/跨平台 |

---

## 开发环境

> **2026-04-19 更新**：VPS 已停用 for DMSD（itsuki 决定不再从学校 iPad 推进 DMSD 工作）。当前只有家里 Mac 一台主机。

- **家里 Mac**（`~/dev/DMSD`）→ Claude Code + Xcode（iOS 开发）+ VS Code — **当前唯一 dev 环境**
- GitHub `otogi2025/DMSD` = 唯一远端真值，2026-04-29 起 public
- 独立 repo：`otogi2025/Tomoshibi-iOS`（iOS Swift 实装镜像）+ `otogi2025/Tomoshibi-Android`（Android Compose）

---

## 当前待办

### 优先(短期)

- [ ] 填 4-10 dev_log 的 4 个【】占位符
- [ ] 填 reflection_2026-04-10 的 5 个【】占位符（已迁 iCloud `AC素材_成品/reflection/`）
- [ ] 回答 `AC素材_成品/ac_入試准备/项目起源_真实观察.md` 里的 AC 起源问题（已迁 iCloud）
- [ ] 继续 Python 学习(下一个: 循环 + 列表)

### 中期

- [ ] .pages 文件转换为 Markdown(4 个文件)
- [ ] 删除/归档早期 throwaway iOS 代码
- [ ] 学习 Swift/SwiftUI 基础
- [ ] VPS 安装 PostgreSQL
- [ ] 搭建 FastAPI 后端骨架

### 长期

- [ ] 采购 Raspberry Pi + NFC 模块,搭建第一台点呼机原型
- [ ] 建 README.md(开始写代码时)
- [ ] 和真人讨论项目(填 iCloud `AC素材_成品/interview_log/`)
- [ ] 月度回顾(每月最后一周,填 iCloud `AC素材_成品/monthly_review/`)

---

## 仓库结构地图

```
DMSD/
├── CHANGELOG.md                     版本变更记录
├── CLAUDE.md                        Claude Code 项目指令
├── 00_admin/                        项目管理
│   ├── progress_overview.md         ← 本文件
│   └── executable_dev_checklist.md
├── 01_specs/                        规格文档(v0.1 冻结)
│   ├── API_CONVENTIONS.md
│   ├── API_Contract_v0.1.pages
│   ├── IA_UI_v0.1.pages
│   ├── v0.1完整计划.pdf
│   └── rollcall/
│       ├── RollCall_Spec_v0.1.pages
│       ├── FIELD_REGISTRY.md
│       ├── ENUM_REGISTRY.md
│       ├── ERROR_CODES.md
│       └── v0.1_冻结决策.md
├── 03_dev/                          代码(待开始)
│   └── Student/DMSDStudentApp(iOS)/  早期 throwaway 代码,将重写
├── 05_logs/                      DMSD 开发 log（AC 纯素材已迁 iCloud）
│   ├── decision_log.md              itsuki 手写决策索引
│   ├── learning_path.md
│   ├── project_evolution.md
│   ├── raw/                         CC 每日 dump（YYYY-MM-DD.md）
│   ├── dev_log/                     itsuki 自己写的叙述式日志
│   └── problem_solving/             问题解决记录
└── 99_archive/                      归档
```
