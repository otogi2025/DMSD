---
name: codex-review
description: DMSD 专属「codex 审查循环」— itsuki 说「codex 审查」时，CC 派 codex（另一家 AI 编码代理，模型 gpt-5.5 + 思考等级 xhigh 顶格）只读审查本会话改动 → CC 逐条裁决 + 修 → 复审 → 收敛 → 收尾。固定最高强度 + 不盲信 codex + CC 自己验证。⭐ 触发：itsuki 说「codex 审查 / 调用 codex 审查 / 派 codex 审 / 派 codex gpt-5.5 xhigh 审 / codex 挑刺 / codex 找 bug / codex 找漏洞 / 让 codex 审一下 / codex 过一遍」。不带「codex」字样的审查请求不触发（避免跟安全审查 / 普通代码审查撞车）。
when_to_use: ⭐ 触发 — itsuki 说的话里**带「codex」三个字** + 审查意图（审查 / 挑刺 / 找 bug / 找漏洞 / 审一下 / 过一遍）。不带「codex」字样 → 不触发本 skill。本 skill 是给 CC 看的编排说明书 — codex 本身只能通过 codex:codex-rescue 子代理调，那个子代理只转发一次任务、不做编排，所以「审 → 修 → 复审 → 收敛」的循环由主会话 CC 编排。
allowed-tools: Agent, Bash, Read, Edit, Grep, Glob
---

# Codex 审查循环 Skill — DMSD 专属

> **一句话**：itsuki 说「codex 审查」→ CC 把**本会话改动**喂给 codex（gpt-5.5 / xhigh 最高思考等级）做**只读**审查 → codex 挑刺 → CC **逐条裁决**（真问题修 / 误报驳回）→ 修完 **CC 自己验证** → 把「上轮提了啥 + 我怎么改的 + 验证结果」喂回 codex 复审 → **跑到收敛**（codex 说 0 阻塞 0 重大）→ 收尾。

## 1. 为什么有这个 skill（背景 — itsuki 多次踩坑换来的）

codex 是 itsuki 反复用的「第二双眼睛」，但它有三个真实坑（全是历史教训，见各 memory）：

- **自报不可信**：codex 常声称「修好了」其实只修一半 / 漏 import / 改错了真正的路径。pytest 绿 ≠ 逻辑对。（`feedback_verify_agent_self_reports`）
- **前提可能是错的**：codex 算术对、但前提错（「116 天磨穿」按 7×24 全天刷算，实际点呼只在时间窗）。原样转给 itsuki = 失职。（`feedback_relay_ai_output_audit_premises`）
- **沙箱编译不了 iOS**：codex 只能语法解析，跑不了真 `xcodebuild`，iOS 改动必须 CC 自己真编译。（`feedback_codex_ios_build_verification`）

所以这套流程的灵魂不是「codex 说啥我做啥」，而是 **CC 当审查的审查者**。

## 2. 模型与强度（已查实，写死）

- itsuki 的 codex 配置文件 `~/.codex/config.toml` 默认就是 `model = "gpt-5.5"` + `model_reasoning_effort = "xhigh"`。**默认调用就是 5.5 + 顶格思考**。
- 调用时仍**显式带 `--effort xhigh`** 双保险（防某次默认被改）。
- **首轮先做「一字测试」**：派一个只含一个字的任务，确认 codex 启动横幅真打出 `reasoning effort: xhigh`，证明顶格思考生效了，再喂正式审查任务。（itsuki 历史习惯）

## 3. 完整流程（CC 按这 7 步做，每步必做）

### Step 0 — 确认审查范围

- **默认范围 = 本次会话的改动**（itsuki 2026-06-04 拍板）。
- 开跑前先 `git status` + `git diff --stat`，**列出本会话改了哪些文件给 itsuki 看一眼**，让他能当场纠正范围（万一他只想审其中一部分）。

### Step 1 — 准备喂给 codex 的完整上下文（上下文不全 = codex 瞎审）

每次派 codex 前，prompt 里必须打包齐这些（itsuki 铁律「上下文要完整」）：

1. **改了什么**：具体文件 + 每个文件改动的意图（不是只贴 diff，要讲为什么改）。
2. **背景**：这是 DMSD 的哪一块（5 端里哪个端 / 哪个功能），相关的项目契约 / 约束（从 `01_specs/API_CONVENTIONS.md` + `00_admin/项目心智模型.md` 取）。
3. **明确要求只读**：prompt 里写清「**review only, do NOT edit any file**（只审查，不要改任何文件）」。修由 CC 做，不让 codex 自己动手（否则跟 CC 的修撞车 + itsuki 失去「自己判断」环节）。
4. **要求结构化输出**：每条发现给「问题描述 / 严重度（阻塞 blocker / 重大 major / 次要 minor / 建议）/ 文件位置 / 修复建议」。

### Step 2 — 调 codex

通过 **Agent 工具**派 `codex:codex-rescue` 子代理：

- `subagent_type`: `codex:codex-rescue`
- `prompt`: Step 1 打包好的完整审查任务文本，**结尾加路由标志 `--effort xhigh`**。
- model 不用传（config 默认 gpt-5.5）。
- 因为 prompt 写明「review only / read-only」，rescue 子代理不会加可写标志，codex 只读不改。

### Step 3 — 逐条裁决 codex 的发现（这步是灵魂，不能跳）

codex 返回后，**对每一条发现单独判断**，不许整批照单全收：

- **真问题** → 标「采纳」，进 Step 4 修。
- **误报 / 前提错 / 不适用** → 标「驳回」+ **写明理由**。
- **重点审 codex 的前提**：它的判断基于什么假设？假设成立吗？（「116 天磨穿」教训）
- 拿不准的 → 自己 Read 相关代码核实，别猜。

### Step 4 — 修 + CC 自己验证（codex 编译不了，CC 必须真验）

修完采纳的问题后，**CC 自己跑验证**，别只信自己改对了：

- **后端**（`03_dev/backend/v1/`）：跑 `pytest`。⚠️ **别看管道退出码** — pytest 经 `| tail` / `| head` 管道后，退出码是管道末尾命令的，不是 pytest 的。**直接读「N passed」那行数字**。
- **iOS**（`03_dev/student_ios/v1/`）：codex 沙箱跑不了真编译 → **CC 自己 `xcodebuild`**，正式版 + 演示版双 scheme 都要 `BUILD SUCCEEDED`。
- **老师网页**（`03_dev/teacher_web/v1/`）：跑 `check_jsx`（语法检查）。
- **改 Python import 的坑**：ruff（格式化工具）会删「加了但没用到」的 import → 加 import 必须**同一次**带上用到它的代码。（`feedback_ruff_import_and_pytest_exitcode_traps`）

### Step 5 — 增量上下文复审

再派 codex 时，上下文要加这一轮的增量，否则 codex 会重复提同样的问题：

- 上一轮 codex 提了哪几条；
- 每条 CC 怎么处理的（采纳改了什么 / 驳回理由）；
- CC 自己验证的结果（测试通过数 / 编译结果）。

然后回到 Step 2 再跑一轮。

### Step 6 — 收敛判据 + 每轮简报

- **收敛 = codex 报告里明确说「0 个阻塞（blocker）+ 0 个重大（major）问题」**（次要 / 建议项可记 TODO 不强制本轮修）。
- **不设轮次上限**（itsuki 2026-06-04 拍板：跑到收敛为止）。
- **但每轮结束 CC 简报一次**：codex 这轮提了 N 条 / CC 采纳 X 驳回 Y / 验证结果。让 itsuki 随时能喊停，不至于 CC 闷头烧。

### Step 7 — 收敛后收尾

- 报告 itsuki：跑了几轮、最终收敛、改了哪些文件、哪些次要项记了 TODO。
- **留痕（AC 素材）**：每轮 codex 发现 + CC 裁决（采纳/驳回+理由）是「多 AI 对抗复审」叙事素材（itsuki 反复用的模式 2）。收尾时进 iCloud raw 池（路径见 session-wrap §3.1，raw 已不放仓库）。

## 4. 五条红线（违反任一条 = 这套流程白做）

1. **不盲信 codex** — 每条发现 CC 独立裁决，codex 的前提也要审。
2. **codex 只读，修由 CC** — prompt 明写 read-only。
3. **上下文必须完整** — 改了啥 + 为啥 + 项目契约，缺一不可。
4. **修完 CC 自己验证** — pytest 读 passed 数 / iOS 真 xcodebuild / 网页 check_jsx，不信自报。
5. **每轮简报 + 可喊停** — 不设轮次上限但全程透明。

## 5. 跟其他东西的边界

| 谁 | 关系 |
|---|---|
| `codex:codex-rescue` 子代理 | 本 skill Step 2 通过 Agent 工具派它调 codex；它只转发一次、不编排，循环由本 skill（主会话 CC）编排 |
| `codex:setup` skill | 万一 codex 没装好 / 调用失败 → 用它检查 codex CLI 状态 |
| `security-review` / DMSD `security-reviewer` 子代理 | 安全专项审查，跟本 skill 不同（本 skill 是通用挑刺找 bug）；不带「codex」字样的审查请求归它们，不触发本 skill |
| `session-wrap` skill | 收尾时把本次审查的发现 + 裁决 dump 进 raw（AC 素材） |

## 版本

- v0.1.0 / 2026-06-04 / 初版 — itsuki 拍板把高频「派 codex gpt-5.5 xhigh 审查」工作流固定成 skill。范围默认本会话改动 / 不设轮次上限跑到收敛 / 每轮简报可喊停 / 不带「codex」字样不触发。模型强度查实写死（config 默认 gpt-5.5 + xhigh）。5 条红线来自 memory：`feedback_verify_agent_self_reports` / `feedback_relay_ai_output_audit_premises` / `feedback_codex_ios_build_verification` / `feedback_codex_per_stage_review` / `feedback_ruff_import_and_pytest_exitcode_traps`。
