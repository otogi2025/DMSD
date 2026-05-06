---
name: No Co-Authored-By trailer in DMSD commits
description: DMSD repo commit history should stay clean Chinese-only; never append Co-Authored-By trailer even though every commit involves AI collaboration
type: feedback
originSessionId: ede75598-18bc-41d0-919c-b0a5fc13b079
---
When committing to the DMSD repo, do NOT append the `Co-Authored-By: Claude ...` trailer to commit messages, even though every commit involves AI collaboration.

**Why:** Confirmed by itsuki on 2026-04-10. (1) DMSD is a solo learning project, not team collaboration — there is no co-author to credit in the team-PR sense. (2) Every commit has AI involvement, so trailers carry zero signal — they only add noise. (3) AC入試 reviewers reading the commit history benefit more from clean short Chinese subject lines than from English trailer text. (4) AI collaboration transparency is intentionally documented in higher-context places (dev_logs, reflections, future `05_logs_ac/project_evolution.md`) where it can be explained, not buried in commit metadata.

**How to apply:**
- Match the existing repo style: short Chinese subject line, no body, no trailer.
- Existing examples to mirror: "项目统一命名DMSD" / "初始提交:所有项目文件" / "归档早期 GPT 对话三件套到 99_archive" / "添加 Python 学习日志和过程证据截图".
- This applies only to the DMSD repo. For other projects with different conventions, fall back to default trailer behavior unless told otherwise.
- If a future commit covers something AI-specific that itsuki wants to call out, do it via a one-line dev_log entry instead of via the commit trailer.
