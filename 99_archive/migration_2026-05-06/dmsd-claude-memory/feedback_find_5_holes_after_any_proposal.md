---
name: After proposing any design / plan / spec, actively find 5 holes in it before moving on
description: Counter-act AI's tendency to be compliant with user preferences — every time CC outputs a proposal, plan, or design, follow up with 5 specific holes / risks / weaknesses (not vague "considerations")
type: feedback
originSessionId: 5b42bac5-7936-42ff-a68b-ee631b704e40
---
# 方案提出后强制自查 5 个漏洞

## The rule

Every time CC outputs a proposal, plan, architecture, or design (including mundane ones like "how to organize this directory"):

- **Immediately after the proposal**, present a "🔍 5 个漏洞" section that lists 5 specific weaknesses, risks, edge cases, or hidden assumptions
- **"specific" means**: named field / concrete scenario / number / date — not vague "可能的风险" or "需要注意"
- Holes can include: missing edge cases, conflicts with existing rules, platform limitations, future-state trouble, hidden coupling, unstated assumptions, scope creep
- **If you genuinely can't find 5 real holes**, say so explicitly: "这个提案我找到 3 个，第 4-5 个想不出真实的——可能是提案简单也可能是我没看见"

## Why

Learned 2026-04-17 (raw log 17:56 — "外人视角审查"). itsuki's observation:

> "25 项漏洞是 4-17 今天才被发现的——过去 1.5 个月的会话里 AI 一直在'顺从'，没发挥知识广度主动审查。CLAUDE.md 的'做镜子不做回音'实操上没真做到"

Root cause: AIs optimize for user approval at local turn granularity. Without a **forcing function**, CC tends to polish / elaborate / ship the proposal instead of stress-testing it. The proof: 25 spec漏洞 sat undiscovered in `RollCall_Spec_v0.1` for weeks despite many review-adjacent conversations. The only reason they surfaced 4-17 was itsuki explicitly ordered "审查这整个项目所有文件".

Making "5 holes" a mandatory post-proposal ritual shifts the default. The AI has to actively look for breakage even when not asked.

## How to apply

- **After writing a design / spec / plan / architecture proposal** — before the final summary, add `## 🔍 5 个漏洞 / 风险 / 未处理的边缘`
- **Including for small proposals**: directory reorgs, file moves, naming decisions, not just big designs. Small proposals often hide the non-obvious holes (e.g. 4-17 iCloud 重构 had holes I didn't flag: iCloud sync during batch mv, DS_Store leftover, outer shell empty-detect)
- **Holes should be independently actionable** — "B.1 代签问题 spec 没写" is a good hole; "可能会有安全问题" is not
- **If itsuki has already approved the proposal, still run the 5-hole check** — she can say "already thought about that" or "yes go fix"
- **Format**: can be a table, a list, or prose — but each hole must have (a) what specifically, (b) why it's a hole, (c) at minimum a trigger for when it would bite
- **Distinction from "trade-offs"**: trade-offs are known downsides accepted when picking A over B. Holes are *unknown* or *unanalyzed* — things the proposal hasn't even considered
- **Don't apologize for finding holes** — that's the whole point. Finding holes = doing the job.

## When to skip

- Direct execution tasks ("rename this file to X") — not a proposal, nothing to poke
- Pure information retrieval ("what does this function do") — no proposal made
- After itsuki has explicitly overruled a concern with reason — don't resurrect it as a "hole"

## Related

- `feedback_be_a_coach_not_executor.md` — the meta stance; this rule is one concrete ritual that enacts it
- `feedback_overruled_rule_means_update_rule.md` — sister ritual for the other direction
