---
name: Recover lost timestamps via mtime + embedded JSON timestamp cross-verification
description: When "what date was this written?" is needed for files/artifacts with no explicit date, cross-check filesystem mtime against any embedded timestamps (JSON created_at, EXIF, API response payloads) — if both agree within seconds, date is trustworthy
type: feedback
originSessionId: 5b42bac5-7936-42ff-a68b-ee631b704e40
---
# 用 filesystem mtime + 嵌入式 JSON timestamp 交叉验证恢复日期

## The rule

When itsuki (or AC narrative) needs to date an artifact whose explicit date was never written down:

1. Check filesystem **mtime** (`ls -la` or `stat`) — note it may be creation of the container, not content
2. Look for any **embedded timestamps** inside the payload:
   - JSON: `created_at` / `timestamp` fields (usually Unix epoch seconds)
   - HTTP response archives: `date` header
   - EXIF: photo capture time
   - Email `.eml`: `Date:` header
3. Convert both to the same timezone (here: JST = UTC+9)
4. **If both agree within seconds/minutes → date is trustworthy** (the two sources are independent — filesystem is local OS, JSON is from the originating server)
5. If they disagree → flag the discrepancy, don't silently pick one

## Why

Used 2026-04-17 (raw log 18:35). itsuki needed to backdate `project_evolution.md` 起点章节 — the 2025-12 ChatGPT conversation archive files had no "written on" metadata. CC found:

- filesystem mtime: `Dec 19 23:11` for payload.json + prompt.txt
- inside `resp.json`: `created_at: 1766153493` → UTC `2025-12-19 14:11:33` → **JST 2025-12-19 23:11**

The two sources matched to the minute — date became safe to cite in AC narrative: "2025-12-19 23:11 JST, 和 GPT-5 Pro 长谈宿舍点呼系统".

This matters because AC评委 will ask "when was this idea first formed?" and "I don't remember exactly" is a weaker answer than "2025-12-19 23:11 — backed by two independent timestamp sources".

## How to apply

- **Any time itsuki says "我不记得具体是哪天"** about a project milestone, first try this technique before accepting the vague date. The file probably knows even if she doesn't.
- **Especially for**: `99_archive/` contents, screenshot files, downloaded API responses, screenshots of chat conversations with visible UTC timestamps, commit hashes that reference external events.
- **One-liner Unix epoch conversion**: `date -r 1766153493` (BSD/macOS) or `date -d @1766153493` (Linux) shows local time; add `-u` for UTC.
- **Be honest about limits**: mtime can be corrupted by `cp` / sync / migration. Always prefer embedded timestamps as primary; use mtime as corroborating only.
- If only mtime is available and no embedded timestamp exists, say so explicitly (don't claim forensic certainty from a single source).

## Don't violate by

- Citing a date in AC material (志望理由书 / 自我推荐书 / project_evolution.md) without verification if forensics are possible
- Using mtime alone when the embedded source exists — the embedded source wins
- Forgetting timezone conversion (UTC → JST is +9 hours; ignore at your peril)
