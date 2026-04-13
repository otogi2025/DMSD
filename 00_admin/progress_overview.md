# DMSD 项目进度总览

> **最后更新**: 2026-04-13
> **当前版本**: v0.2.0(见 `CHANGELOG.md`)
>
> 这是项目的**当前状态快照**。详细的日志、问题解决、决策过程在 `05_logs_ac/` 下。

---

## 项目简介

**DMSD**(Dormitory Management System Digitalization)— 宿舍管理系统电子化

把宿舍的纸质点呼考勤、纪律管理流程数字化,通过 NFC 卡 + 后端服务器 + 手机 App 实现。

- **开发者**: itsuki(一个人,零基础起步)
- **起始时间**: 2026 年 2 月
- **GitHub**: https://github.com/otogi2025/DMSD (私有仓库)

---

## 分阶段策略(2026-04-12 决定)

| 阶段 | 内容 | 不需要 |
|------|------|--------|
| **Phase 1** | NFC 卡 + 后端 + 点呼机(Raspberry Pi) | 学生 App |
| **Phase 2** | 加手机 App(iOS + Android) | — |

Phase 2 不替换 Phase 1,两种方式共存。没智能手机的学生继续用卡。

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
- 月累计 ≥ 9.0 → 下月禁足

### 防作弊核心: 语音播报

点呼机读卡后自动播报学生姓名,老师人眼对照。把"机器识别身份"和"老师人眼识别"实时配对,攻击者必须本人到场(详见 `05_logs_ac/decision_log.md`)。

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
- [x] 更新 `executable_dev_checklist_v0.1.md`

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

### 阶段 3: 后端开发 ⬜ 未开始

- [ ] VPS 安装 PostgreSQL
- [ ] FastAPI 项目骨架搭建
- [ ] 数据库建表与迁移
- [ ] 登录与权限系统
- [ ] 点呼核心 API(开始/签到/结束)
- [ ] 改判与审计日志
- [ ] 健康上报、不点呼申请
- [ ] 扣分系统与纪律报表

### 阶段 4: 点呼机设备开发 ⬜ 未开始(Phase 1 关键)

- [ ] 采购 Raspberry Pi + PN532 NFC 模块 + 扬声器
- [ ] Raspberry Pi 系统安装与配置
- [ ] NFC 读卡 Python 代码(nfcpy)
- [ ] HTTP 通信后端
- [ ] 语音播报(pyttsx3)
- [ ] 外壳 + 贴墙安装

### 阶段 5: 老师端 Web/iPad 界面 ⬜ 未开始

### 阶段 6: iOS 学生 App ⬜ Phase 2

### 阶段 7: Android 学生 App ⬜ Phase 2

### 阶段 8: 部署与试运行 ⬜ 未开始

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

详细前因后果见 `05_logs_ac/decision_log.md`。

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

---

## 问题解决记录(索引)

详细记录在 `05_logs_ac/problem_solving/`。

| 日期 | 问题 | 类型 |
|------|------|-----|
| 2026-03-10 | tar 打包报错 "no files or directories specified" | 命令行 |
| 2026-03-10 | scp 传文件缺少目标路径 | 命令行 |
| 2026-03-11 | Python NameError(变量未定义) | 编程 |
| 2026-03-11 | Python 布尔值必须大写 True/False | 编程 |
| 2026-04-10 | Git pull 失败: NFC vs NFD 跨平台编码差异 | Git/跨平台 |

---

## 开发环境

- **学校 iPad** → SSH 到 VPS(~/DMSD)→ Claude Code(学习、写后端、写文档)
- **家里 Mac** → 本地(~/dev/DMSD)Claude Code + Xcode(iOS 开发)+ VS Code(Python 练习)
- 通过 GitHub 同步代码

---

## 当前待办

### 优先(短期)

- [ ] 填 4-10 dev_log 的 4 个【】占位符
- [ ] 填 reflection_2026-04-10 的 5 个【】占位符
- [ ] 回答 `05_logs_ac/raw/项目起源_真实观察.md` 里的 AC 起源问题
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
- [ ] 和真人讨论项目(填 `05_logs_ac/interview_log/`)
- [ ] 月度回顾(每月最后一周,填 `05_logs_ac/monthly_review/`)

---

## 仓库结构地图

```
DMSD/
├── CHANGELOG.md                     版本变更记录
├── CLAUDE.md                        Claude Code 项目指令
├── 00_admin/                        项目管理
│   ├── progress_overview.md         ← 本文件
│   └── executable_dev_checklist_v0.1.md
├── 01_specs/                        规格文档(v0.1 冻结)
│   ├── API_CONVENTIONS_v0.1.md
│   ├── API_Contract_v0.1.pages
│   ├── IA_UI_v0.1.pages
│   ├── v0.1完整计划.pdf
│   └── rollcall/
│       ├── RollCall_Spec_v0.1.pages
│       ├── FIELD_REGISTRY_v0.1.md
│       ├── ENUM_REGISTRY_v0.1.md
│       ├── ERROR_CODES_v0.1.md
│       └── v0.1_冻结决策.md
├── 03_dev/                          代码(待开始)
│   └── Student/DMSDStudentApp(iOS)/  早期 throwaway 代码,将重写
├── 05_logs_ac/                      AC 入試记录
│   ├── AC考试记录指南.md
│   ├── decision_log.md
│   ├── ai_协作记录.md
│   ├── raw/                         原始未润色素材
│   ├── dev_log/                     润色后的日志
│   ├── problem_solving/             问题解决
│   ├── interview_log/               访谈记录(空)
│   ├── monthly_review/              月度回顾(空)
│   └── reflection_*.md              反思
└── 99_archive/                      归档
```
