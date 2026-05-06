---
name: Iteration evidence must live in Git-trackable media (.md + frequent commits), not .pages / chat transcripts / binary containers
description: When itsuki discusses design or iterates on a doc, push her toward opening a plain .md file and committing early/often — binary formats (.pages / .docx) and chat transcripts (ChatGPT / Claude app) are AC-invisible black boxes
type: feedback
originSessionId: 5b42bac5-7936-42ff-a68b-ee631b704e40
---
# 迭代痕迹必须住在 Git 可追踪的媒介里

## The rule

When itsuki is about to iterate on a design, spec, or thinking:

- **Push her to open a plain `.md` file early** — even three rough lines on Day 1 beats a polished `.pages` on Day 30.
- **Every substantive change = a commit**, with a message saying what changed and why ("新增方案 D" / "推翻方案 A，理由 Y"). Frequency matters more than commit-message quality.
- `.pages`, `.docx`, and chat-app transcripts (ChatGPT / Claude app) are **AC-invisible black boxes**. Git sees "file changed" but can't diff; an AI conversation isn't even in Git. 100 revisions inside such containers = 0 revisions of evidence to a reviewer.

## Why

Learned 2026-04-17 (raw log 17:57 + 18:09). itsuki's `RollCall_Spec_v0.1.pages` had been revised ~100 times between 2026-03-08 and 2026-04-17, but git log showed one monolithic file with no internal diff history. Worse: the *earliest* ~15 design iterations from 2025-12 lived entirely in ChatGPT transcripts — no Pages, no Git, nothing.

AC入試 reviewers explicitly value "what you considered and rejected" — i.e., the rejected paths. If the rejection isn't recorded in a diffable medium with timestamps, it effectively didn't happen from their standpoint, regardless of how many hours of thinking actually went in.

The same day she had to manually reconstruct 2025-12 dates by timestamp forensics (see `feedback_timestamp_forensics_mtime_plus_json.md`) — a tax paid because the discussion never entered Git in the first place.

## How to apply

- **When a new design idea enters conversation**: ask "should we open an `.md` for this now?" before she writes it anywhere else.
- **When she says she's "thinking about X for a while"**: proactively suggest a scratch file, even if contents are rough. "粗糙三行笔记 > 完美的 pages 文件" is the principle.
- **When she iterates on an existing `.md`**: nudge toward a commit after each substantive session, not batched weekly.
- **When she references something from a chat (ChatGPT / Claude app)**: flag that the content is currently invisible to Git and suggest copying the salient bits into `05_logs/raw/` as a dump or into a decision file.
- **`.pages` is fine for producing pretty PDFs to hand to a teacher**, but never as the editing canvas. Edit in `.md`, export to `.pages`/PDF only for delivery.
- This applies to **new projects after DMSD too** — the AI Pair that sees itsuki open a new project should proactively push "open an `.md` Day 1" before anything else.

## Don't violate by

- Letting her do a 30-minute design discussion without proposing a dump
- Accepting `.pages` as a "working" format ("改完再 export 成 .md" is *not* acceptable — edit *in* `.md`)
- Treating chat transcripts as sufficient record; they must be exported/dumped into `raw/` to count
