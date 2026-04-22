# DMSD（项目）/ Tomoshibi（系统）Demo 4-28 档案夹  <!-- VERSION_OK -->

> 2026-04-28 宿舍管理员 demo 的全部规划档案。
>
> **命名**（2026-04-21 定名）：项目 = **DMSD** / 系统（给管理员看的产品）= **Tomoshibi（灯火）**。Demo 给管理员演示的系统自我介绍时用 "Tomoshibi"。
> **建立**: 2026-04-21 议题 E 拍板 + scope 扩展 + ST25DV 供货延迟三事件触发
> **权威来源**: 本文件夹 = demo 相关决策、需求、脚本、替代方案的唯一真值
> **非目录**: 不包含代码（代码在 `03_dev/backend/` / `03_dev/device/` / `03_dev/teacher_web/` / `03_dev/Student_iOS_new/`）

---

## 档案目录

| 文件 | 谁读 | 何时读 | 内容 |
|---|---|---|---|
| [sprint.md](./sprint.md) | itsuki + CC | 起点 / 每天开工 | **总纲**：7 天时间表 + 决策复盘 + 架构 + 风险清单 + 指向各子档的指针 |
| [scope_tier.md](./scope_tier.md) | itsuki + 代码 agent | 开工前 / 每个功能开写前 | **Tier 1 真跑 / Tier 2 UI skeleton / Tier 3 post-demo** 完整分层清单。含每项 API 规格 + 字段 + 页面路径 + demo 动作 |
| [ST25DV_fallback.md](./ST25DV_fallback.md) | itsuki | D2-D3 | NFC 替代方案（2026-04-22 简化为 itsuki 自有 NFC 卡 + iOS Shortcuts Automation）+ 配置步骤 + 现场叙事 |
| [demo_script.md](./demo_script.md) | itsuki | D7 彩排 + D8 Demo Day | 现场演示完整台词 + 动作 + 时机 + 管理员可能追问的备用应答 + Tier A 8 问 |
| **[questions_for_admin.md](./questions_for_admin.md)** 🆕 | itsuki | **Demo Day §10 收尾时** | **35 个要问宿舍管理员的问题** 按 Tier A ⭐ 必问 / Tier B 追问 / Tier C 书面跟进 分层 + 每题话术 + 答复模板 |
| **[wifi_survey_howto.md](./wifi_survey_howto.md)** 🆕 | itsuki | **Demo 后 30 分钟** | Wi-Fi 实地测试手册：许可话术 + 5 步测法（信号 / 客户端隔离 / 速度 / 网段）+ 记录模板 |
| [questions_for_requirements.md](./questions_for_requirements.md) | Code-Agent + CC | 代码 agent 开工 | 代码 agent 问需求会话的内部对齐（和管理员无关，不要混淆）|

## 读法建议

**itsuki 每次开工前**：`sprint.md §3 今天是 D?` → 对应 Day 的任务 → 涉及 Tier 1 功能 → 翻 `scope_tier.md` 查规格

**代码 agent 接到任务时**（主会话 / 另开子 agent）：`scope_tier.md` 找对应功能的 API 规格和字段 → 写代码。不用读其他文件

**彩排 / Demo Day**：`demo_script.md` 走一遍 + `questions_for_admin.md §Tier A` 口袋小抄 + `wifi_survey_howto.md §1` 许可话术准备

## 关键分工

- 本会话（[Mac-demo-sprint]）：**只负责需求/文档/清单**，不写代码
- 代码实现由其他 agent 负责（前端 / 后端 / iOS / Pi 点呼机）
- 代码 agent 读 `scope_tier.md` 作为需求来源 → 产出对应代码 → 回到这里更新"完成度"
