<p align="center">
  <img src="dev/student_ios/v1/TomoshibiApp/AppIcon-1024.png" alt="Tomoshibi 灯火" width="160" height="160" />
</p>

# DMSD → Tomoshibi（灯火）

> **仓库 / 开发代号**：DMSD — Dormitory Management System Digitalization
> **产品名**：Tomoshibi（灯火 / ともしび）
> **一句话**：把宿舍纸质点呼、纪律管理、申请流程数字化。
> **当前版本**：见 [`CHANGELOG.md`](./CHANGELOG.md)（版本号单源真值）
> **当前状态**：5 端代码层全启动，v1.0 完整体推进中。
> **作者**：itsuki（伊月）

---

## 第一次读这个项目

如果你是第一次打开这个仓库，建议按这个顺序读：

1. [`design/system_features.md`](./design/system_features.md) — 5 端共用功能规格，系统整体能力一览。
2. [`specs/rollcall/RollCall_Spec.md`](./specs/rollcall/RollCall_Spec.md) — 点呼系统完整业务规格。
3. [`dev/`](./dev/) — 5 端源代码，每个端目录下有自己的 README。

`README.md` 是仓库门面，`design/` 与 `specs/` 是理解系统设计的入口。

---

## 这是什么

我住的宿舍每天都要点呼，现在用的是纸质签到表。这种方式慢、容易漏，也很难和纪律分数、外泊申请、学习出席记录连起来。

Tomoshibi 用 NFC 卡、学生手机 App、老师 Web、后端服务器和入口处的专用点呼机，把这个流程数字化。

核心目标不是“做一个 App”，而是把宿舍管理里每天重复、容易出错的流程，变成一套可以实际运行的系统。

---

## 做到哪了

**截至 2026-06-15**：

- 2026-04-28：Demo 跑通（iPhone NFC → 后端 → iPad 座位变绿 + 日语播报）。
- 2026-04-29：宿舍管理员当面口头同意采纳系统，GitHub repo 首次 public。
- 2026-04-30：老师反馈 38 条吸收进 `system_features.md`。
- 2026-05-02：v0.8.0 close，iOS / Android / Teacher Web / Backend / 点呼机 5 端代码层全启动。
- 2026-05-08：点呼机硬件方案定稿（Pi 3A+ + PN532 V3 + ST25DV16K + USB 小音响）。
- 2026-05-19：project-overview 大改造，建立文件级总览和防漂机制。
- 2026-05-20 到 05-22：多轮审查和 bug findings 修复。
- 2026-05-26：Teacher Web 的 Vite + TypeScript 实装版被整体废弃，回到 Ryō 风格 standalone HTML 主线。
- 2026-05-27：Teacher Web v1.0 深夜推进，后端新增 discipline / cleaning / front desk / WebSocket 等能力；同日完成 iOS 审查、全项目审查、project-overview 再校准。
- 2026-05-28：宿舍申请表后端全链路（5 张新表 + 校長审批链）+ iOS 6 个申请界面实装 + 点呼机硬件采购定稿。
- 2026-05-30：Teacher Web v1.0 完整施工 6 大模块（行事予定 / 巴士时刻表 / 指導履歴 / 事案 / 个人档案聚合 / 学号一括进级）。
- 2026-05-31：iOS 多功能从假数据接真后端（IX 系列）+ 后端 findings 全面修复，Codex 多轮复审（后端测试 193 → 220 全过）。
- 2026-06-03：版本号回溯规范化 — 把 5-11 到 6-02 的 236 个 commit 按语义化版本补了 6 个版本标签（v0.8.1 ~ v0.12.0）。
- 2026-06-03：出租车予約功能 4 端实装（v0.13.0）。
- 2026-06-04：杭田老师 6-04 需求大批 + 外出申請 + オンライン学習契約書（v0.14.0）。
- 2026-06-05：老师网页从 standalone HTML 迁到 React + TypeScript + Vite（界面冻结原样搬）+ Android 对齐 iOS + 学年更新完成（v0.15.0）。
- 2026-06-09 ~ 06-11：版本号体系按语义化版本（SemVer）规范化（回溯补标 + 插空细分）；iOS 体验功能批次（介绍页重做 / 公告 AI 翻译·要約 / 首页接真数据）+ iOS 首批单元测试（点呼时间窗状态机）。
- 2026-06-12 ~ 06-13：iOS 公告原地翻译（Apple Intelligence）+ 老师权限分级 + 公告 is_demo 演示隔离 + 后端 schema 落后自检。
- 2026-06-14：iOS 上线前全量审查（日语自然度 / bug / 漏洞 / 前后端对齐，Tier1–3 修复，当前版本 v0.23.10）。
- 2026-06-13 ~ 06-15：公开仓库治理 — 白名单 .gitignore（只公开软件本体）+ 顶层目录去数字编号前缀（9 目录改名 + 全引用同步）+ 仓库门面整理。

当前重点：

| 端 | 状态 |
|---|---|
| 规格层 | `system_features.md` + `RollCall_Spec.md` + 字段/枚举/错误码字典仍是业务真值。 |
| Backend | FastAPI + PostgreSQL + Alembic。27 router（REST + WebSocket）覆盖点呼 / 申请 / 公告 / 指导 / 事案 / 前台 等业务域。 |
| iOS | SwiftUI 项目在 `dev/student_ios/v1/`；学生端主要功能已接真后端，完成多轮上线前审查（日语自然度 / bug / 漏洞 / 前后端对齐）+ 首批单元测试。 |
| Android | Kotlin + Compose 项目已建，视觉层覆盖主要学生端屏幕；真后端接入和测试仍待推进。 |
| Teacher Web | React + TypeScript + Vite（Ryō 风格界面冻结搬迁），权威源 `dev/teacher_web/v1/src/`。 |
| 点呼机 | 硬件方案和 Python 骨架已建，真实 Pi 上手和 NFC/LED/audio/API 模块实装仍在后续。 |
| 工程治理 | WIP / TODO / project-overview / hooks / skills 协作防漂体系；公开仓库白名单 + 目录规范化。 |

---

## 技术栈

| 部分 | 技术 |
|---|---|
| 学生 App | iOS（Swift / SwiftUI）+ Android（Kotlin / Jetpack Compose） |
| 老师 Web | React + TypeScript + Vite（Ryō 风格界面，iPad 浏览器使用） |
| 后端 | FastAPI / Python + PostgreSQL + Alembic |
| 点呼机 | Raspberry Pi 3A+ + PN532 V3 NFC + 01Studio USB 小音响 + Python |
| NFC 卡 / 标签 | NTAG215（学生卡）+ ST25DV16K（入口动态标签，每 10 秒刷新 nonce） |
| 协作 / 版本 | Git + GitHub + Claude Code |

---

## 推荐阅读顺序

| 顺序 | 文件 | 看什么 |
|---|---|---|
| 1 | [`design/system_features.md`](./design/system_features.md) | 5 端共用功能规格真值。 |
| 2 | [`specs/rollcall/RollCall_Spec.md`](./specs/rollcall/RollCall_Spec.md) | 点呼系统完整业务规格。 |
| 3 | [`design/`](./design/) | 硬件 / 流程 / 权限等设计文档。 |
| 4 | [`dev/`](./dev/) | 5 端源代码，各端目录下有自己的 README。 |
| 5 | [`CHANGELOG.md`](./CHANGELOG.md) | 版本演变和里程碑。 |

---

## 关于 AI 协作

我在整个项目过程中使用 Claude Code 作为开发搭档：AI 负责帮助发现盲点、解释技术、实现代码、整理记录，重大决策由我拍板。

之所以保留这一声明，是因为这个项目本身也是一次个人开发者与 AI 协作完成真实工程的实践。完整的决策与演化记录保留在本地开发日志中。

---

## 联系 / 其他

- **开发者**：itsuki（otogi2025@gmail.com）
- **GitHub**：https://github.com/otogi2025/DMSD
- **项目起始**：2025-12（NFC 方案早期设计讨论；Git 历史自 2026-03）
