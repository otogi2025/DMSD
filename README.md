<p align="center">
  <img src="06_assets/icons/tomoshibi_app_icon_256.png" alt="Tomoshibi 灯火" width="160" height="160" />
</p>

# DMSD → Tomoshibi（灯火）

> **项目名（仓库/开发代号）**：DMSD — Dormitory Management System Digitalization
> **系统/产品名（对外）**：**Tomoshibi**（灯火 / ともしび）
>
> 把我们宿舍的纸质点呼流程数字化。
>
> **当前版本**：见 [`CHANGELOG.md`](./CHANGELOG.md)（单源真值，v0.8.0 + 之后多次未 bump 推进）
> **状态**：5 端代码层全启动 — iOS Swift / Android Compose / Teacher Web TS / FastAPI 后端 / 点呼机 Pi 3A+ 骨架，硬件采购 + Pi 上手编程 阶段
> **作者**：itsuki（伊月）— 零基础起步，边学边做

---

## 这是什么

我住的宿舍每天都要点呼，现在用的是纸质签到表。这种方式慢、容易漏。

Tomoshibi 用 NFC 卡 + 服务器 + 手机 App + 墙上的专用小设备（点呼机）把这整个流程数字化。

---

## 做到哪了

**截至 2026-05-21**（v0.8.0 close + 之后多次未 bump 推进）：

**项目近期里程碑**（详见 `CHANGELOG.md` + `00_admin/progress_overview.md`）：

- 2026-04-28 — Demo 跑通（iPhone NFC → 后端 → iPad 座位变绿 + 日语播报）
- 2026-04-29 — **宿舍管理员当面口头同意采纳系统** + GitHub repo 首次 public
- 2026-04-30 — spec 主体 38 条 R1-R4 + 8 分阈值拍板入 system_features
- 2026-05-02 — **5 端代码层全启动**（v0.8.0 close）：iOS 网络层 / Android Compose bootstrap / teacher_web v1 TS+Vite / backend rollcall+study+teachers routers / iOS↔backend 字段对齐 F1-F5+Q1
- 2026-05-08 — **硬件全定稿**：Pi 3A+ + PN532 V3 + ST25DV16K + LED 模块 + 01Studio USB 小音响
- 2026-05-13 — 文件大整理 + project-overview skill 建立（630+ 文件清单单源真值）
- 2026-05-19 — project-overview 大改造（9 处漂移修 + §0.1 体量重算 957 文件）+ 防漂 C 方案（hook 全覆盖 + 启动对账）
- 2026-05-20+ — 131 条 bug findings 4 会话并行修复
- 2026-05-22 — project-overview §0.1 再校准 957→980（5-21 demo 158 文件归档落地）+ Fix-Bot 4 effective_* 字段彻底删完成 + Codex 第二轮全文件覆盖 audit（39 条 / 24 独立 + 13 复核 + 2 positive）

**5 端代码层实装状态**（截至 5-21）：

- ✅ **规格层**：RollCall_Spec.md（~1000 行）+ 字典三件套（枚举 / 字段 / 错误码 / 设备注册）+ system_features.md 830 行（4-30 大重写）
- ✅ **后端 FastAPI**：1134 行 BACKEND_DESIGN_LOG + 8 router（auth / rollcall / study / accounts / admin_registration_code / teachers / applications / meals / notifications）+ Alembic migration 框架 + 37 case pytest 全 pass
- ✅ **iOS Swift/SwiftUI**：Foundation 层 17 文件 1861 行（网络 / Keychain / Route / AppStore）+ 3 个核心 Feature（Auth / Home / Community 5K+ 行）实装中
- ✅ **Android Kotlin/Compose**：22 屏（Login/Home/Apply/MyPage/Settings/Schedule/Bus/Study/Music/Notifications/NfcScreen 等）+ MainActivity / NavGraph / AppStore / MockData / Theme
- ✅ **Teacher Web TS+Vite+Zustand**：5 page + demo 接真后端 + 学習管理全屏会话
- 🔄 **点呼机 Pi 3A+**：硬件全定稿（5-08）+ ROLLCALL_DEVICE_DESIGN_LOG 226 行 + src/main.py 骨架；硬件采购 + Pi 上手编程 未开始
- ✅ **工程治理**：跨会话同步机制 A+B+C / 版本管理 SOP（迁 `.claude/skills/version-bump/` skill 形态）/ 18 条联动规则 + 11 hook / 7 项目 skill / project-overview 单源真值

**为什么这个顺序**：我是零基础高一时开始想这个项目，花了大量时间先把"这个系统到底要长什么样"写清楚 → 再用 prototype 把交互跑通 → 接 4-28 demo 拿管理员反馈 → 5-02 起 5 端代码层并发推进。我认为这个顺序是对的（下面"AI 协作"一段会再讲一次）。

---

## 目录导航（推荐阅读顺序）

| 顺序 | 文件 | 看什么 |
|---|---|---|
| 1 | [`CHANGELOG.md`](./CHANGELOG.md) | 项目版本变更历史（含 pre-0.1 追认） |
| 2 | [`01_specs/rollcall/RollCall_Spec.md`](./01_specs/rollcall/RollCall_Spec.md) | 点呼系统完整规格（~1000 行，业务 + API） |
| 3 | [`05_logs/decision_log.md`](./05_logs/decision_log.md) | 每个重要决策的"之前 → 现在 → 为什么" |
| 4 | [`05_logs/project_evolution.md`](./05_logs/project_evolution.md) | 项目整体如何从"想法"演变到"可动手蓝图" |
| 5 | [`05_logs/learning_path.md`](./05_logs/learning_path.md) | 我作为零基础学习者的学习路径 |
| 6 | [`00_admin/progress_overview.md`](./00_admin/progress_overview.md) | 阶段进度快照（章节级） |

---

## 技术栈

| 部分 | 技术 |
|---|---|
| 学生 App | iOS（Swift / SwiftUI）+ Android（Kotlin / Compose） |
| 老师 Web | TypeScript + Vite + Zustand（已实装 5 page，2026-05-02 v0.8 起） |
| 后端 | FastAPI / Python + PostgreSQL + Alembic |
| 点呼机 | Raspberry Pi 3A+ + PN532 V3 NFC + 01Studio USB 小音响 + Python |
| NFC 卡 / 标签 | NTAG215（学生卡）+ ST25DV16K（动态标签，每 10 秒刷新 nonce） |
| 版本 / 协作 | Git + GitHub + Claude Code |

**上线姿态**（2026-04-19 决定）：v1.0 **一次性**上线三种使用方式（卡 / iPhone / Android），不做"先上卡再上 App"的分阶段。开发内部按 M1→M5 里程碑推进，兜底是"做不完至少 M1+M2 可以 demo"。

---

## 关于 AI 协作（诚实声明）

**我在整个项目过程中使用了 Claude Code 作为搭档**（AI 家教 + 代码助手 + 写作辅助）。这对我不是秘密，我写这一段就是想把这件事说清楚。

具体做法：

- **我决定"做什么"，AI 帮我实现"怎么做"**，每段代码我都必须能解释给别人听
- **AI 不是听话的执行者，是"有原则的教练"** —— 我希望它质疑我、打断我、在我漏看的地方提醒我
- **所有重大决策最终由我拍板**，包括主动**反驳 AI 的过度建议**（例如 2026-04-15 我反对 AI 推荐的高配 Raspberry Pi，转而选更便宜的低配款 + "thin client / thick server" 架构原则）

如果你想看我怎么和 AI 协作的具体证据，可以读：

- [`CLAUDE.md`](./CLAUDE.md) —— 我给 AI 的项目指令
- `05_logs/decision_log.md` 2026-04-15 条 —— 反驳 AI 过度配置
- [`00_admin/2026-04-19_项目审查_backlog.md`](./00_admin/2026-04-19_项目审查_backlog.md) —— AI 对项目做的深度审查 + 我的取舍判断

我相信"成熟地使用 AI"本身也是现代软件工程的一部分，不需要遮掩。

---

## 联系 / 其他

- **开发者**：itsuki（otogi2025@gmail.com）
- **GitHub**：https://github.com/otogi2025/DMSD
- **项目起始**：2026-02
- **升学目标**：筑波大学 情報学群 情報科学類 AC 入試（2027 年 4 月入学）—— DMSD 也是我 AC 入試 的核心叙事项目。这个动机我不回避：**"真诚解决真问题"和"把解决过程作为升学叙事"本来就不冲突**。
