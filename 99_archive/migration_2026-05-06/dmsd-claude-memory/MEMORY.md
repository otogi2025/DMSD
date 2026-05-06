# DMSD Project Memory

## User Profile
- Name: itsuki（汉字: 伊月）— 2026-04-29 主动告知,README 作者行已用「itsuki(伊月)」格式
- Real name (本名): LIU YIFEI — 2026-05-03 from Apple ID account name (Xcode signing); 用于 dev account / 法律文件场合
- Identity: Chinese high school student studying in Japan
- Goal: Apply to University of Tsukuba (筑波大学情報学群) via AC入試
- Dev experience: Complete beginner - explain everything
- Languages: Chinese, Japanese
- GitHub: otogi2025
- Apple Developer: **paid Developer Program member**（已付 99 USD/年，不是免费 Personal Team）— 2026-05-03 confirmed; 后果：真机装 app 不会 7 天过期 / 可注册真机 / 可上 TestFlight + App Store
- Communication: Always in Chinese, explain English terms

## Communication Rules
1. Explain "why" and "what" for every step
2. Explain English terms and command parameters
3. Proactively teach concepts they need to know
4. Remind to log learning moments for AC入試 preparation
5. AC入試 values process over results - problem-solving is material
6. Always communicate in Chinese
7. Aggressively surface "unknown unknowns" - itsuki has no systematic CS/dev education, so proactively explain underlying concepts (e.g. why we use Git, what an API is, how files are organized) whenever relevant, don't assume any prior knowledge

## Project Info
- **Project name**: DMSD (Dormitory Management System Digitalization) — 开发项目/仓库代号
- **System/Product name**: **Tomoshibi**（灯火 / ともしび）— 面向用户的系统名（2026-04-21 拍板）。AC 叙事："我在日本留学，宿舍是我在异国的第二个家。这个系统守护的是'灯火'——每个学生夜晚平安归来、房间亮起一盏灯。" 详见 [naming memory](./project_naming_tomoshibi.md)
- Mac path: ~/dev/DMSD | VPS path: ~/DMSD
- GitHub: https://github.com/otogi2025/DMSD (private)
- Core: Roll call digitalization (NFC check-in, auto attendance, discipline points)
- Tech: Student App (v1.0 ships iOS + Android simultaneously — Swift/SwiftUI + Android Kotlin/Java) + Teacher Web + Backend (FastAPI/Python/PostgreSQL)
- 2026-04-19 G2 decision: no phased launch. v1.0 = cards + iPhone + Android all together. CLAUDE.md "Phase 1 / Phase 2" split is deprecated. Internal dev still follows M1→M5 milestones.
- Specs: RollCall spec v0.1 frozen 2026-02-12. v0.2 字典三件套 + v0.3.0 主体 rewrite both completed 2026-04-17. Filename still RollCall_Spec_v0.1.md (去后缀 scheduled for v0.4.0 / T3). Project overall version: see CHANGELOG.md 顶部 (current v0.3.1 as of 2026-04-20).
- .pages files cannot be read by CC. Only `01_specs/v0.1完整计划.pdf` has a PDF version (duplicate copy in 99_archive/NFC_NFD_鬼影文件/). The other 4 .pages (API_Contract / IA_UI / Overview_of_Features / DMSDv0.1验收脚本) have **no PDF version** — conversion to .md requires itsuki to open Pages.app on Mac and export.

## Dev Environment
- Home Mac → Local Claude Code + Xcode + VS Code — **primary (and as of 2026-04-19, only) dev environment for DMSD**
- VPS (~/DMSD) was previously used via SSH from school iPad for learning/backend/docs. 2026-04-19 itsuki decided to stop pushing DMSD work from VPS.
- GitHub (otogi2025/DMSD, private) is the canonical remote

## Key Dates
- 2026-02-12: RollCall spec v0.1 frozen (originally labeled v1.0 before version reset on 2026-04-13)
- 2026-03-10: Git basics learned, GitHub repo created, project setup complete
- 2026-03-11 → 2026-04-10: ~1 month gap with no work on project
- 2026-04-10: itsuki returned to project after 1-month hiatus
- 2026-04-17: RollCall spec v0.2 主体 rewrite 完成 (commit 2ef7ff7), project version bumped to v0.3.0
- 2026-04-19: G2 decision — cancel phased launch (v1.0 = cards + iPhone + Android simultaneously); VPS deprecated for DMSD; 记录详细度要求 §3.4 added to CLAUDE_CODE_记录指南.md
- 2026-04-19 (same day, later): 文档同步机制 A+B+C 建立 (single source of truth + 同步点清单 + pre-commit hook 拦截硬编码版本号); 项目审查 backlog 87 条落地
- 2026-04-20 (下午 [Mac-另一会话]): iPhone BTR + Universal Link + AASA 拍板; URL 复制漏洞 → 动态 NFC 贴纸 ST25DV16K (¥25 × 4 = ¥100 RMB, nonce 10 秒刷新); Pi 4B 2GB × 4 最终确认 (¥1200 RMB)
- 2026-04-20 (晚 [Mac-主会话]): v0.3.1 tag 发布 (`fb330c2`) — AC readiness 文档层; 持续推 backlog 至 ✅ 累计 25+ / ⏳ 12 / 剩 ~50. 8 commit + 10 pre-0.1 annotated tag 追认 + v0.3.1 tag 都 local 未 push
- 2026-04-28: Demo 4-28 sprint 当天向宿舍管理员演示纯软件 prototype (iPhone NFC → 后端 → iPad 座位变绿 + 日语播报)
- 2026-04-29: **管理员基本同意采纳系统**(itsuki 当面口头反馈,非正式书面),叙事重点从"管理员是否会采纳"转为"做出来给管理员看进度"。同日 GitHub repo 首次 public (https://github.com/otogi2025/DMSD), README 大幅 cleanup (去 Tomoshibi 解释段 / 去代签强调 / 语音播报降级到机制之一非核心设计 / 状态行更新为「前端框架已搭好,后端 + 生产实装为下阶段」)

## Python Learning Progress
- Day 1 (2026-03-11): variables, data types (str/int/float/bool), print, if/elif/else
- Next: for loop, list, then dict and functions
- Practice on Mac in ~/dev/practice/, not in DMSD repo
- Exercises should relate to DMSD when possible (checkin times, penalties, etc.)

## TODO (as of 2026-04-10)
- Continue Python: loop + list + dict + functions
- Write reflection piece on the 1-month gap (AC入試 material) instead of faking old dev_logs
- Convert .pages files to Markdown (13 files in 01_specs/ and 05_logs_ac/)
- Create AC log structure (dev_log/, problem_solving/, learning_path.md, project_evolution.md)
- Learn Swift/SwiftUI basics — iOS will start from scratch (existing code is throwaway)
- Delete or archive existing throwaway Swift/SwiftUI code before starting fresh iOS work
- Start iOS frontend development from clean slate based on 01_specs/

## ⚡ FOUNDATIONAL RULE (read first)
- [⚠️ itsuki 是男生 — 中文代词用男字旁的 ta（2026-05-04 拍板，已 sed 全 repo + memory 替换）](./user_gender_male.md)
- [Be a principled coach, not a compliant executor — itsuki's core expectation for AI collaboration](./feedback_be_a_coach_not_executor.md)
- [主动诊断 unknown unknowns + 业界标准方案优先 — 看到他手搓机制强制扫描 CC 内部能力 / 业界标准 / AC 学习清单，主动提现成方案。Skill / CC Hook 已踩失职案例 in memory](./feedback_proactive_diagnose_unknown_unknowns.md)
- [Project naming — DMSD (project) vs Tomoshibi (system/product), 2026-04-21 定名](./project_naming_tomoshibi.md)
- [iOS + Web 前端大概率真上线（非 demo 一次性）— 新功能要分 demo-only vs 生产版](./project_frontends_headed_to_production.md)
- [Demo-only scaffolds 清单（长按切点呼状态等）必须 v1.0 前删 — 否则变安全漏洞](./project_demo_scaffolds_to_remove_before_v1.md)

## See Also
- [Project structure details](./project_structure.md)
- [Physical environment](./physical_environment.md)
- [Early iOS code is throwaway](./feedback_ios_early_code.md)
- [Dev logs must be same-day](./feedback_dev_log_discipline.md)
- [No Co-Authored-By trailer in DMSD commits](./feedback_commit_style.md)
- [Repo vs Notes boundary — fact (repo) vs narrative/framing (notes), NOT "professor-facing or not"](./feedback_repo_vs_personal_notes.md)
- [Propose boldly, execute only after confirmation — proposing new frameworks is wanted](./feedback_dont_over_structure.md)
- [Issues to solve belong in TODO.md, not just raw log](./feedback_issues_belong_in_todo.md)
- [Overruled rule = update the rule, not one-off exception](./feedback_overruled_rule_means_update_rule.md)
- [Iteration evidence must live in Git-trackable media (.md + commits), not .pages / chat transcripts](./feedback_iteration_evidence_git_trackable.md)
- [Recover lost timestamps via mtime + embedded JSON timestamp cross-verify](./feedback_timestamp_forensics_mtime_plus_json.md)
- [Find 5 specific holes after every proposal — counter AI compliance drift](./feedback_find_5_holes_after_any_proposal.md)
- [选项命名只用 A/B/C，禁用甲乙丙 / α β γ / ①②③](./feedback_use_english_letters.md)
- [讨论的最终目的是产出 — 重大决策当场更新 CLAUDE.md，不等会话结束](./feedback_discuss_means_produce.md)
- [Demo sprint 阶段 CC 只做需求/文档/清单，代码交代码 agent](./feedback_cc_role_requirements_not_code.md)
- [Scope 严格按用户字面说的做，不扩展；用户说"漏洞"就只列漏洞，不加"路径图"/"推进"/"新建"](./feedback_scope_strictly_as_told.md)
- [默认中文回答（不是默认日语）— 做日语 UI 时 CC 容易整段日语漂移，已被多次纠正](./feedback_default_chinese_response.md)
- [代码注释严格中文，禁止日语漂移 — 即使做日语 UI 功能注释也必须中文（2026-05-03）](./feedback_code_comments_chinese_strict.md)
- [审查 = 找漏洞，不是 CC 主动修复 — 收到"排查/找漏洞"指令默认列清单等 itsuki 决定](./feedback_audit_means_find_not_fix.md)
- [找重复文件要读全文不只看标题 — 真问题是"部分章节内容重复"，不是整文件重复](./feedback_audit_read_content_not_just_titles.md)
- [改动总结用"原来/问题/改成"三段式 — 讲内容不讲工具，禁用 "perl N 处" / "git mv N 文件" 这种叙述](./feedback_change_summary_three_part_format.md)
- [用户明确拒绝的事不要再提 — 不要放进 TODO / 留给你做 / open question（杭田 UI 三次没听进去）](./feedback_dont_re_raise_rejected_topics.md)
- [跟 itsuki 沟通必须用大白话 — 内部代号 / 日语 / 英文缩写第一次出现就翻译，对话和文档都适用](./feedback_explain_terms_to_itsuki.md)
- [不要扯命令行黑话 / 路径堆 / 工具语法 — 解释流程时先讲"他要做什么"，命令名最后才出现（2026-05-04）](./feedback_no_cli_jargon.md)
- [WIP.md vs TODO.md 分工铁律 — WIP 是当下书签（短小，最近 5 次会话），TODO 是完整 backlog 真值；CC 启动时两个都读（2026-05-04）](./feedback_wip_todo_split.md)
- [commit/push/tag 协作分工 — CC 自动 commit 本地不 push；push/bump itsuki 拍板；CHANGELOG CC 起草事实清单，AC 叙事 itsuki 自己写（2026-05-04）](./feedback_commit_push_tag_division.md)
- [CC 主动发现的问题 = itsuki 的 AC 素材 — 不仅当场说还要主动 dump raw/，过程算他的（他做了采纳/拒绝/修改判断）（2026-05-04）](./feedback_proactive_record_problem_solving.md)
- [UI placeholder 禁用剧情化例子（祖父母宅 / 友人の結婚式 / 祖母の通院 等）— 用中性字段提示，剧情诱导虚假填写 + 文化预设错位（2026-05-04）](./feedback_no_dramatic_placeholder.md)
- [修 build error 不替 itsuki 撤销设计意图 — Liquid Glass `.icon` build 失败先诊断根因不私自回退到老格式（2026-05-04）](./feedback_dont_unilaterally_revert_design.md)
