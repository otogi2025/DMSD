# DMSD（项目）/ Tomoshibi（系统）Demo 4-28 Sprint Plan（总纲）  <!-- VERSION_OK -->

> **命名**（2026-04-21 定名）：项目 = DMSD，系统/产品 = **Tomoshibi（灯火）**。管理员 demo 介绍系统时统一用 "Tomoshibi"。Demo 当天向管理员开场可说"这是我开发的 Tomoshibi（灯火）宿舍点呼系统"。
> **本文作用**: 4-28 管理员 demo 冲刺的**总纲**（时间表 + 决策复盘 + 指针）。具体内容分散到 4 个子档。
> **触发**: 2026-04-21 议题 E 拍板（详见 `05_logs/raw/2026-04-21.md §16:50`）
> **文件夹位置**: `00_admin/demo_4-28/`（本文件夹包含所有 demo 规划档案，不污染 `00_admin/` 根目录）
> **最后更新**: 2026-04-21 深夜（系统命名 Tomoshibi 同步）

---

## 导览：按需要查哪个档

| 你要找的 | 去看 |
|---|---|
| 今天是 D?，做什么 | 本文 §3 时间表 |
| 某个功能怎么做 / API 规格 / 字段定义 | [`scope_tier.md`](./scope_tier.md) Tier 1/2/3 清单 |
| 演示当天台词 + 动作 | [`demo_script.md`](./demo_script.md) |
| ST25DV 替代方案 + iOS Shortcuts 配置 | [`ST25DV_fallback.md`](./ST25DV_fallback.md) |
| 文件夹整体导览 | [`README.md`](./README.md) |

---

## 0. 核心决策复盘（议题 E + scope 扩展 + ST25DV fallback）

### 0.1 Demo 给谁看
**宿舍管理员**。管理员是真实 stakeholder，决定是否采纳系统。

### 0.2 时间
**2026-04-28（周二）**。7 天硬 deadline。

### 0.3 范围（2026-04-21 Tier 分层拍板）
- **Tier 1** 真跑通（demo 脚本里真演）：点呼 + 座位表 + 改判 + 健康 + 请假 + 外宿 + 归国 + 扣分 + 检索
- **Tier 2** UI skeleton（菜单存在 + mock 数据）：扫除 + 巴士 + 活动 + 宿舍互动 5 项 + 快递 + 归县 + 出租车 + 通知中心 + 长期豁免
- **Tier 3** 砍：举报审核算法 / 真删除封禁 / CSV/PDF 导出 / 多点呼机协调 / 时间窗自动结算

详见 [`scope_tier.md`](./scope_tier.md)。

### 0.4 形态
**实机演示**（老师进 itsuki 房间 → iPad + 真点呼机 + iPhone + Xcode 模拟器）。演示台词见 [`demo_script.md`](./demo_script.md)。

### 0.5 硬件
- Pi 3A+ × 1（Amazon 日本 ¥6480，4-22 到，详见 `02_design/hardware_design_v0.1.md §2.1`）
- NTAG215 × 10（Amazon 日本 ¥400，4-22 到）
- PN532 + 杜邦线 + 小喇叭 + 电源 + SD 卡（同上到货）
- **ST25DV16K**（淘宝空运 7-10 天，demo 前到不了）→ **替代方案 A**：NTAG215 静态贴纸 + iOS Shortcuts Automation，详见 [`ST25DV_fallback.md`](./ST25DV_fallback.md)

### 0.6 扣分规则（2026-04-21 拍板）
**暂定数字 + 后端做成可配置阈值**：默认迟到 0.5 / 缺席 1 / 月累计 4 罚扫 / 月累计 8 禁足。Demo 时说明"数字最终和老师商议"。详见 [`scope_tier.md §1.12`](./scope_tier.md)。

### 0.7 iOS 版本
itsuki iPhone iOS 26（最新）→ Shortcuts Automation "不问确认" 完全支持。

---

## 1. Demo 流程脚本摘要

完整台词 + 动作 + 备用应答 见 [`demo_script.md`](./demo_script.md)。

**骨架**（12-15 分钟）：
1. 开场 pitch（30 秒）
2. 介绍 Web 左侧菜单 7 大类（2 分钟）
3. 开始点呼 + iPhone tap + 座位实时响应 + 语音喊名 ⭐（3 分钟）
4. 座位手动改判（2 分钟）
5. 健康状态上报 + 叠加红十字（1.5 分钟）
6. 单次不去点呼申请 + 一键审批（1.5 分钟）
7. 外宿申请提交 + 审批（2 分钟）
8. 扣分累计展示（1.5 分钟）
9. 后台检索（1 分钟）
10. 收尾 + 请管理员反馈（1 分钟）

---

## 2. 老师 Web 功能清单摘要

**Tier 1 真跑**（11 项）+ **Tier 2 UI skeleton**（15 项）+ **Tier 3 砍**。完整规格、API、字段、页面路径 见 [`scope_tier.md`](./scope_tier.md)。

左侧菜单 7 大类（对应 itsuki 给的需求 §11）：
1. 点呼（+ 实时座位表 + 改判 + 健康 + 请假）
2. 通知中心（聚合待办）
3. 纪律处分（扣分展示）
4. 申请中心（外宿 / 归国 / 归县 / 出租车）
5. 扫除审核
6. 公告 / 活动 / 巴士
7. 宿舍互动治理（宿舍墙 / 点歌 / 遗失物 / 匿名建议 / 快递）

---

## 3. 7 天时间表（按 Tier 1 + Tier 2 并行）

**重要**：Day 数字从 "今天 2026-04-21 下午起算 = D1"。代码实现由其他 agent 负责（本会话只做需求/文档/清单）。

| Day | 日期 | Tier 1 主线（真跑）| Tier 2 穿插（skeleton）| 里程碑 |
|---|---|---|---|---|
| **D1** | 4-21 今晚 | ✅ 文档层（sprint / scope_tier / ST25DV_fallback / demo_script / backend skeleton / hardware_design 修订）| - | 规划完成 |
| **D2** | 4-22 周三 | 硬件到 → Pi 3A+ 烧 SD / 连 WiFi / SSH 打通；后端签到 API 本地测通 | - | 硬件上电 |
| **D3** | 4-23 周四 | 点呼机 NFC 驱动（PN532 I²C 读 UID）；iOS Shortcuts Automation 配置；端到端第一次跑通"iPhone tap → 后端 → iPad 显示"| - | 核心链路通 |
| **D4** | 4-24 周五 | Pi TTS 语音喊名；老师 Web 登录 + 主框架 + **实时座位表（颜色渲染）** | Web 左侧菜单 7 大类导航就位 | Web 骨架 |
| **D5** | 4-25 周六（全天）| **座位手动改判** + **健康状态上报**（App + Web 叠加红十字）+ **单次不去点呼申请** + 一键审批 | Tier 2 一批：扫除 / 巴士 / 活动 / 匿名建议（4 个页面 skeleton）| 点呼核心完整 |
| **D6** | 4-26 周日（全天）| **外宿 + 归国**（iOS Xcode form + Web 审批）+ **扣分展示**（学生端 + 老师端排名，含 discipline_config 可配置表）+ **后台检索**（按学生 / 按日期）| Tier 2 另一批：遗失物 / 宿舍墙 / 点歌 / 快递 / 归县 / 出租车 / 通知中心 / 长期豁免（8 个页面 skeleton） | 功能面完整 |
| **D7** | 4-27 周一 | **彩排 3 遍** + bug 修 + demo 脚本定稿 | Tier 2 扫尾 + 连续超标预警 skeleton | 彩排通过 |
| **D8** | **4-28 周二 🎯** | **Demo Day**（按 demo_script.md 走）| - | 管理员反馈入袋 |

---

## 4. 技术架构（MVP 简化版）

```
┌─────────────────┐         ┌───────────────────────────────┐
│  itsuki iPhone  │ ──────> │   后端 FastAPI (Python)       │ <──┐
│  (NFC tap +     │  POST   │   - SQLite (demo)             │    │
│   Shortcuts     │         │   - WebSocket broadcast       │    │
│   Automation)   │         │   - discipline_config 可配置  │    │
└─────────────────┘         └───────────────────────────────┘    │
                                  │                 ▲             │
                                  │ WS push         │ POST 签到   │
                                  │                 │             │
                        ┌─────────▼────────┐   ┌────┴──────────┐ │
                        │  老师 Web (iPad) │   │ Pi 3A+ 点呼机 │ │
                        │  - HTML + JS     │   │ - Python      │ │
                        │  - WS client     │   │ - PN532 NFC   │ │
                        │  - 实时座位表    │   │ - pyttsx3 TTS │ │
                        └──────────────────┘   └───────────────┘ │
                                                                  │
                        ┌──────────────────┐                      │
                        │ iOS App (Xcode)  │──POST 申请 / 健康────┘
                        │  - SwiftUI form  │
                        └──────────────────┘
```

---

## 5. 风险清单

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| ST25DV16K 到货晚于 4-27 | 高 | 中 | 已有方案 A（NTAG215 + iOS Shortcuts），见 [`ST25DV_fallback.md`](./ST25DV_fallback.md) |
| Pi 3A+ 512MB RAM 吃紧 | 低 | 中 | Raspbian Lite（不装桌面）+ 不跑浏览器 |
| PN532 驱动调不通 | 中 | 高 | 备 2 个库（adafruit / Pi-Py532），限 D3 内解决 |
| WebSocket 连不通 iPad | 中 | 高 | Fallback：前端 3 秒轮询 `/api/checkins/latest` |
| itsuki 学 Swift 来不及 | 高 | 低 | iOS App 只做 6 屏；代码 agent 代写；itsuki 理解后 demo 时能讲 |
| Shortcuts Automation 不触发 | 低 | 中 | 备方案 B（桌面 Shortcut 按钮） |
| Demo 当天网络故障 | 低 | 高 | Mac 开热点 + 本地跑后端 |
| Tier 2 skeleton 来不及 | 中 | 低 | D7 删减到 5-6 个 skeleton 也可接受（管理员感受打 80 分）|

---

## 6. AC 素材预埋点

完整清单见 [`scope_tier.md §5`](./scope_tier.md) 和 [`ST25DV_fallback.md §9`](./ST25DV_fallback.md)。

D2-D8 每天预期产生的 AC 素材：

| Day | 预期素材 | 核心问题 |
|---|---|---|
| D1 | Scope 扩展 + Tier 分层 / ST25DV fallback 决策 / 扣分可配置思路 | #3 #4 |
| D2 | 第一次 SSH 到 Pi / 第一次 curl 调 API 成功 | #4 |
| D3 | I²C 调试踩坑 / iOS Shortcuts 配置细节 | #3 #4 |
| D4 | 为什么不用 React（deadline vs 学习曲线的工程取舍）| #3 #4 |
| D5 | WebSocket 实时推送 vs 轮询（学"推模式"）| #4 |
| D6 | Swift 零基础 3 天做 6 屏的最小闭环 | #4 |
| D7 | 彩排 3 遍发现 N 个 bug + 修法 | #3 #4 |
| **D8** | **管理员反馈 — 无论 + / - 都是最硬的 AC 素材** 🌟 | #1 #2 #3 #4 #5 |

---

## 7. 与 v0.4.0 主线的协调

- 本 sprint 不打 git tag（demo 后评估 → 纳入 v0.5.0 或 v0.4.x patch）
- `[Mac-主会话]` 的 v0.4.0 S2/S3 字段 + Device_Contract 骨架：
  - S2 `card_uid` 字段定义 → demo 的 `students.card_uid` 直接用
  - Device_Contract OQ1-9 → demo 不部署多台，可 defer 到 demo 后
- 两会话不冲突：demo sprint 做 `03_dev/` 代码（交给代码 agent）+ `00_admin/demo_4-28/` 档案（本会话）；主会话做 `01_specs/` + `00_admin/v0.4.0_*.md`

---

## 8. 分工（2026-04-21 itsuki 明示）

| 谁 | 做什么 |
|---|---|
| **本会话 [Mac-demo-sprint]**（CC）| 需求 / 文档 / 清单（本文件夹所有档案）+ 文档同步更新（CLAUDE.md / WIP / raw log / hardware_design / TODO）|
| **其他 agent**（前端 / 后端 / iOS / 点呼机）| 真正的代码实现。读 [`scope_tier.md`](./scope_tier.md) 作为需求来源 |
| **itsuki** | 硬件采购 / Shortcuts 配置 / 彩排 / Demo Day / 管理员反馈记录 |

---

## 9. 下次更新触发

- itsuki 补 Tier 1 漏掉的 / Tier 2 升级真跑的项 → [`scope_tier.md §5`](./scope_tier.md) + 本文 §3 时间表
- Amazon / 淘宝下单确认 → `02_design/hardware_design_v0.1.md §4.1`
- 每日进展 → 本文 §3
- 风险发生 → 本文 §5 + 对应子档

---

**END of Sprint Plan v2（Tier 分层 + ST25DV fallback）**
