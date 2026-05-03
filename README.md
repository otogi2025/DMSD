<p align="center">
  <img src="06_assets/icons/tomoshibi_app_icon_256.png" alt="Tomoshibi 灯火" width="160" height="160" />
</p>

# DMSD → Tomoshibi（灯火）

> **项目名（仓库/开发代号）**：DMSD — Dormitory Management System Digitalization
> **系统/产品名（对外）**：**Tomoshibi**（灯火 / ともしび）
>
> 把我们宿舍的纸质点呼流程数字化。
>
> **当前版本**：见 [`CHANGELOG.md`](./CHANGELOG.md)（单源真值）
> **状态**：规格 + 前端框架已搭建（iOS prototype / Web Round 3），后端 + 生产实装为下阶段
> **作者**：itsuki（伊月）— 零基础起步，边学边做

---

## 这是什么

我住的宿舍每天都要点呼，现在用的是纸质签到表。这种方式慢、容易漏。

Tomoshibi 用 NFC 卡 + 服务器 + 手机 App + 墙上的专用小设备（点呼机）把这整个流程数字化。

---

## 做到哪了

**截至 2026-04-29**（v0.5.0）：

- ✅ 规格文档 v0.1 冻结（2026-02-12）
- ✅ 字典体系（枚举 / 字段 / 错误码 / 设备注册）成型
- ✅ 硬件架构决策（Raspberry Pi + PN532 NFC + 扬声器）
- ✅ 双路径架构：NFC 卡 + 手机 App 同时支持，没智能手机的学生不被排除
- ✅ 反作弊机制：动态 NFC 贴纸（ST25DV16K，每 10 秒刷新一次性 nonce，防 URL 复制）+ 语音播报
- ✅ 系统正式命名 **Tomoshibi（灯火）**（2026-04-21）
- ✅ Spec S 系列闭合（v0.4.0，2026-04-22）
- ✅ 老师 Web prototype Round 3（12 组件 + 学生账号管理 + 座席表 + 改判 + カレンダー + リクエスト曲）
- ✅ 学生 iOS prototype Round 1（73 画面 Phase A+B HTML，3 按钮 nav + Home omnibus + 中央点呼 sheet）
- ✅ Demo 4-28 sprint 跑通（纯软件，iPhone 碰 NFC → 后端 → iPad 座位变绿 + 日语播报）
- ✅ 跨会话同步机制 A+B+C（多 AI agent 并行协作的真值同步规则）
- ✅ 版本管理 SOP 建立（`00_admin/版本管理SOP.md`，解决"9 天没 bump"的迭代问题）
- ✅ 完整版本变更记录（见 `CHANGELOG.md`，v0.0.1 → v0.5.0 共 14 个版本）
- ⬜ 后端 + 生产代码 —— 还没开始。iOS Swift / Android Kotlin / FastAPI 后端 实装从 v0.6 起步

**为什么这个顺序**：我是零基础高一时开始想这个项目，花了大量时间先把"这个系统到底要长什么样"写清楚 → 再用 prototype 把交互跑通 → 最后才上生产实装。我认为这个顺序是对的（下面"AI 协作"一段会再讲一次）。Demo 4-28 是给宿舍管理员看的软件 prototype，反馈是基本同意采纳，接下来进入生产实装阶段。

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
| 学生 App | iOS（Swift / SwiftUI）+ Android（Kotlin / Java） |
| 老师 Web | 待定（iPad 上用浏览器打开的管理界面） |
| 后端 | FastAPI / Python + PostgreSQL |
| 点呼机 | Raspberry Pi + PN532 NFC + 扬声器 + Python |
| NFC 卡 | NTAG215（空白卡批量采购） |
| 版本 / 协作 | Git + GitHub |

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
