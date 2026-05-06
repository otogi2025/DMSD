---
name: When itsuki overrules a CLAUDE.md rule, treat it as a signal to update the rule
description: If CC refuses a request by citing a CLAUDE.md rule and itsuki explicitly overrules, propose updating the rule in CLAUDE.md (and related guides) — don't treat it as a one-off exception
type: feedback
originSessionId: 5b42bac5-7936-42ff-a68b-ee631b704e40
---
# 规则被推翻 = 更新规则的信号，不是一次性破例

## The rule

When CC refuses a user request citing a specific rule from `CLAUDE.md` (or any 指南), and itsuki explicitly overrules ("我允许你..." / "你来做..." / "就按你想的干"), CC should:

1. Execute the task she asked for (that's the immediate ask)
2. **Also propose updating the rule itself** — either generalize it, add a permission row for the now-legitimate case, or outright reverse the rule
3. Do the rule update in the same session if she confirms, not later

## Why

Witnessed 2026-04-17: itsuki asked CC to move layer-2 AC candidates. CC refused citing "CC 不擅自在 iCloud AC 素材目录写任何东西" from CLAUDE.md. itsuki overruled: "我允许你访问我的 icloud".

The rule was written when the intent was "CC can't touch AC materials at all". By 4-17 itsuki's actual mental model had shifted to "CC can touch under my direction". The rule hadn't caught up.

Without updating the rule, the same friction would happen every time across sessions — CC refusing → itsuki manually overruling → asymmetry between text rules and lived practice. That's rule rot.

## How to apply

- **When CC refuses by citing a CLAUDE.md rule and is overruled** → this is the signal. Don't re-read the rule looking for a loophole; propose a rule update.
- **Granularity matters**: not every permission expansion should be "unlimited access". Propose the *narrowest* rule change that covers the legitimate case (e.g. "can write 03/04 with explicit per-session authorization" is better than "can write anywhere in iCloud").
- **Preserve the parts that still apply**: on 4-17, "CC never writes 05_产出 (志望理由书 / 自我推荐书 / 面试准备)" was added — because those remain itsuki's 100% original work. Overruling one rule doesn't mean neighboring rules are also overrulable.
- **Surface the change visibly**: in the session where the change happens, update the doc AND mention in summary "I also updated CLAUDE.md §X to reflect this" — so itsuki knows the rule now matches reality and doesn't have to re-authorize next time.

## Related memories

- `feedback_be_a_coach_not_executor.md` — the coach stance underlies this: don't just execute the one-off, recognize the meta-signal
- `feedback_dont_over_structure.md` — propose boldly; updating a rule is a proposal, itsuki still approves
