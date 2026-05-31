# 2026-05-31 findings 全量修复 + 多 AI 每阶段 Codex 审 + 翻车反思

> 主题：itsuki 要求把 findings.md 全 175 条修好，定工作流「每阶段 commit → Codex 5.5 xhigh 审 → 处理反馈 → 下一阶段」。本会话修了角色名/隐私/Android 小 bug/后端小 bug/实时广播架构等多批，过程中踩坑翻车并立教训。

---

## [方法] 多 AI 三层 + 每阶段 Codex 审的修复流水线

### 背景 / 触发
itsuki 设 ultracode + 「全修好 findings 175 条」+「每阶段做完派 Codex 挑刺」。

### 经过 / 关键判断
- 先用 17 单元核实 workflow 把 175 条逐条核对**当前**代码状态（不信旧 findings 描述）——发现 status 自动标签噪音大（子代理把大工程误标已修），逐条读 evidence 才靠谱。
- 按「能直接改的小 bug / 几周大工程 / 需 itsuki 决策」三层分。小 bug 我亲自改 + 验证，大工程归 /goal 不重复，决策项摊给 itsuki。
- 每批改完 commit + 派 Codex（gpt-5.5 / xhigh）静态审。**Codex 抓到两个我自己没发现的真问题**：① 我把生产管理员邮箱当 demo 假数据误清（admin 收不到邮件）；② study.py 用 logging 但漏 import（pytest 没触发那分支所以没暴露）。

### AC 价值
模式 4（多 AI 交叉验证，不盲信单点）+ 模式 6（流程机制：把「人审」固化成每阶段 Codex gate）。可挂「我设计了核实→改→Codex 审→修反馈的流水线，让两个 AI 互相证伪，自己做最终把关」的工程判断力。

---

## [认知改变 / 翻车] 「验证过了」的假象比不验证更危险

### 背景 / 触发
修后端批后我写 commit「193 全过」，实际是 11 passed / 182 error，且坏代码已 commit。

### 经过 / 根因
- 根因 1：`pytest | tail` 的 exit code 是 tail 的（恒 0），我把后台通知的 exit 0 当 pytest 通过。
- 根因 2：连踩两次「ruff 删分两步加的 import」——分两步改（先加 import 后加用法），ruff 在中间把没被用的 import 当垃圾删，导致运行时 NameError。main.py 那次直接让 app 启动崩、182 测试全挂。
- 处理：补回 import、真读「193 passed」结果行核实、新 commit 诚实记录翻车（坏 commit + 假 message 留历史作为失误记录）、立 memory 防第三次。

### itsuki 原话 ⭐
「要确认修得正确，不要像之前一样莫名其妙冒出一个一般教师出来一样。」

### AC 价值
模式 5（认知改变：自动化工具链里「以为验证过」是最隐蔽的失败模式——CI 绿、exit 0、commit 成功全是假信号，必须看到真实断言数字）+ 模式 2（假设崩了：从「193 全过」到发现 182 error，不甩锅继续追根因）。诚实记录自己的失误本身是 AC 叙事的真实性证据。

---

## [事实] 环境与并发约束
- 本机只有 iOS Xcode 能编译；Android 没装 SDK 不能 gradle 编译（只能 Codex 静态审兜底）；后端能 pytest。
- 全程有别的会话并行改 iOS，靠「commit 只 add 自己的文件」防互相覆盖（呼应 feedback_parallel_sessions_overwrite_risk）。
