---
name: When recording issues, default to TODO not just raw log
description: "要解决的问题/issues to solve" 属于待办性质,默认进 TODO.md,不能只 dump 到 raw log
type: feedback
originSessionId: 50a11731-8c8b-49c4-9d39-c562adc08708
---
When itsuki asks to record "问题清单 / 要解决的问题 / issues to solve / 待修订事项" — default to **adding to `00_admin/TODO.md`** as actionable checkbox items, NOT just to `05_logs/raw/YYYY-MM-DD.md`.

**Why**:
- raw log = 历史事件性记录("今天发现了 X")
- TODO = 可执行待办("X 需要解决")
- "要解决的问题" 天然属于待办性质 → 主目标是 TODO
- 2026-04-17 spec 审查时 itsuki 纠正过 CC:CC 把 25 项 spec 漏洞只 dump 到 raw,漏掉了 TODO。原话:"你记录到 todo 啊,我让你记待办事项里"

**How to apply**:
- 当请求里出现 "问题/issues" + 待办语义(要解决 / 要做 / 待办 / 修订) → **默认 TODO 是主目标**
- raw 仍可以并行记(事件叙事 + #AC候选 标签),但 TODO 是必做
- 不确定时主动确认:「raw + TODO 都记?还是只 TODO?」
- 反过来:itsuki 说"记一下今天的事 / dump 一下" 这种纯叙事语义时,默认 raw,不用进 TODO
