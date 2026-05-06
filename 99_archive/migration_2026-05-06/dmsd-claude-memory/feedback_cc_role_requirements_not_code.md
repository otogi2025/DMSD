---
name: CC 主职责 = 需求/文档/清单，代码交代码 agent
description: itsuki 2026-04-21 明示 DMSD demo sprint 阶段 CC 不主动写代码实现，代码任务分配给其他 agent；CC 职责聚焦需求文档、待办清单、设计层文档、决策记录
type: feedback
originSessionId: 3bad5eac-da87-4cc6-b236-903c55f4c04d
---
**itsuki 原话**（2026-04-21 晚）：
> "像前端后端代码之类的，这些任务我会分配到别的 agent 去做，你不要管，你只需要把需求和待办清单列出来就好了"

**背景**：
- DMSD 进入 4-28 demo sprint 冲刺阶段（7 天完成管理员 demo）
- itsuki 决定用多 agent 分工：CC 负责需求/文档，代码 agent 负责实现
- 这是新的协作模式，之前 CC 倾向"既讲需求又写代码"

## CC 在本阶段的产出标准

**该做**：
- 需求文档（scope / Tier 分层 / API 规格 / 字段定义 / 页面路径 / demo 动作）
- 待办清单（TaskCreate 按模块细分 + 优先级）
- 设计层文档（CLAUDE.md / hardware_design / flow_design）
- 决策记录（raw log / sprint plan 历史留痕）
- 演示台词（demo_script）
- 配置步骤指南（iOS Shortcuts / 硬件烧 SD 等需要 itsuki 手动做的步骤）

**不该做**：
- 主动写新的前端代码（HTML/JS/React）
- 主动写新的后端业务代码（FastAPI 端点 / SQL 迁移脚本）
- 主动写 iOS Swift 代码
- 主动写 Pi 点呼机 Python 代码

**豁免（已在边界上的）**：
- 已建的 backend skeleton（models / schemas / ws_manager / 基础 API）= "需求落地的最小样板"，可保留，代码 agent 接着做
- 明确 itsuki 口头同意时（"你来写"）

## 需求文档要达到的质量

关键标准：**代码 agent 读完能直接开工，不用回头问 CC**。

每个功能项必须有：
- 页面路径 / 菜单位置
- 后端 API 规格（method + path + body + response）
- 字段定义（每个字段类型、约束、默认值）
- 幂等 / 去重策略
- WS / 实时推送事件（如有）
- UI 要求（用词精准，例如"3 个 tab" / "点击弹 modal" / "学生名字大字加粗"）
- Demo 时的动作（谁点哪里 / 期望响应是什么）

## 如何应用

**Why**：
1. 多 agent 协作效率 > 单 agent 揽全活，尤其是 7 天 deadline
2. CC 写代码深度不够（前端 UI 美学 / iOS Swift 细节 / Pi 硬件驱动），代码 agent 可能更专精
3. itsuki 要学的是"怎么设计系统 + 怎么管理工程"，不是"怎么让 CC 替他写代码"—— 分工模式下 itsuki 看到完整需求文档，学产品思维

**How**：
- 每次 itsuki 提出功能变动，先更新需求文档（`scope_tier.md` / `sprint.md`），而不是直接写代码
- 提到"代码 agent"任务时，用 TaskCreate 建待办但 owner 不是自己
- 代码相关疑问主动指向代码 agent 会话，不自己答（例如"这个 API 怎么实现"→ "我已经在 scope_tier.md §X.X 写了规格，代码 agent 读规格实现"）

## 不适用场景

- DMSD 非 demo sprint 阶段（比如 spec 修订阶段 / backlog 清理阶段），CC 仍做之前的工作模式
- itsuki 明确说"这个你来写"（明示豁免）
- 极小片段（单个 SQL 查询 / 一个 utility function 的 3 行）需要立即说明原理时
- backend skeleton 这类"搭骨架 + 讲解"性质的产出（教学价值 > 实现价值）

## 配合的 memory

- `feedback_discuss_means_produce.md` — 讨论 = 产出。本条规则不冲突：CC 的"产出"从"代码"变为"需求文档 + 清单"
- `feedback_be_a_coach_not_executor.md` — 本条进一步强化"coach"定位
