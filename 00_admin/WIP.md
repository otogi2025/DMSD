# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-27（早段 — teacher_web v1.0 凌晨深夜推进收尾会话 + 醒后 backend 自审 9 处修复：itsuki 启动「审查我做的事到底做好了没」+「不要停下来问 / 不需要决策的直接修 / 决策的加 TODO」→ CC 自查 5 维度：alembic migration ✅ / 13 router 注册 ✅ / 61 endpoint 真 import 通过 ✅ / Student.is_demo 字段已加 ✅ / client.js 32 helper 跟 backend 路径 100% 对齐 ✅ / 5 处 index.html 日语注释中文化（中文铁律）/ 全部 9 处真 bug 已在凌晨别会话修完。早些深夜-3 — iOS 全自主审查 + 修 + 收尾会话：itsuki 启动「审查这个 iOS APP 看有什么问题，然后去做去修」+「做完后就直接收尾，不要给我留问题，也不要停下来问我，所有的问题加到 todo 里面」→ CC 5 维度过完 41 文件 / 修 1 处（`MyPageStubs.swift:1404` `c.score!` force unwrap 改 `map ?? _`）/ 2 处架构性问题写 TODO §D（`StayListStubs.swift:475` catch 降级 mock 假数据 / `MyPageStubs.swift:1637` 暴露 `localizedDescription`）/ 所有 demo 后门 + A-XXX bug 标记 + NFC UI + 其他 catch 全部确认 ✅。早些深夜-2 — 跨天会话「2026-05-25 晚段-2 / AC 学习内容清单 v0.1.0 起草」收尾：5-25 晚 itsuki 抛元认知反思「5 端开发但一门语言都没掌握 + 文件认不全」+ 主动要求扩充「专业知识 + 项目底层运转逻辑」→ CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章（工程层改动被 5-26 晚段-4 别会话 commit `3d945a7` 顺手带走）+ 列 4 章扩充大纲（第 9-12 章）等拍板 → itsuki 直接说「收尾」未实装 → 加 TODO §🛠️ §M 6 条悬挂任务 + raw `2026-05-25_AC学习清单起草.md` 4 段深度 AC 素材；模式 5 顶级 × 2。早些 2026-05-27 深夜 — itsuki 让 CC 清 TODO 里「不需要决策 + CC 自己能做 + 不重要」的小活清单 14 件<!-- VERSION_OK --> + project-overview drift 修：6 件本来就闭合 TODO 没刷状态（T1 3 文件已归档 / T2 .DS_Store 删 / T3 临时PDF 目录已不存在 / T7 DESIGN_BRIEF 5-26 已重写 / T8 DEVICE_REGISTRY §6 已是 dorm-1/2 / T9 FC-025-028 已标 ✅ N/A）+ 7 件真做（T4 99_archive README 时间戳 / T6 WEB_DESIGN_LOG §7+§10 路径过时项 / T11 project-overview §6.2 raw 48→55 / T12 SC26 session-wrap §7.5.5「6 项」→「8 项」/ T13 全局环境清单 DMSD Skills 7→8 加 dmsd-startup / T14 WIP 最近会话 10→5 砍 5 条 / T15 §0.1 体量表全刷新 1181→1189）+ 2 件挂起待 itsuki 拍板（T5 backend 表数 13→21 + P0/P1/P2 分级标准 / T10 系统bug专栏 77 条状态字段工作量大）；起因：itsuki 启动「列 TODO 里不重要 CC 自己能做的小活」+ 说「做完后直接收尾，想 commit 就 commit」。早些 2026-05-26（晚段-4 — teacher_web Vite + TypeScript 实装版整体废弃 + Ryō polish 试做被回滚 + 修破工具脚本 demo_server.py 死链改 python http.server + 文档同步 WEB_DESIGN_LOG §12 + DESIGN_BRIEF + v1/README + 物理清 node_modules 81MB + dist + decision_log 加 2 条；起因：itsuki 启动「推进 teacher web」+ 看到 Vite 实装版怒怼「这他妈根本不是我的 web」拍板「垃圾归档用 B」+ frontend-design skill polish 试做整体不喜欢一句「回滚」全退。早些晚段-3 — iOS demo 后门清理（做法 B）+ 字段对齐零漂移 commit `7521bf8`。早些晚段-2 — 全项目中枢机制立项 + DMSD 注册档案 + DMSD CLAUDE.md 加「全项目中枢联动」段；同时合并早段 iOS Bot 1 复查 + 暗夜模式 v2 + 3 上架配置归位 + memory 加铁律「TODO 关条目不要问」入「最近会话」。早段头：启动 SOP 集中化 — 新建 `.claude/skills/dmsd-startup/SKILL.md`（5 件启动必做事）+ 全局 `~/.claude/hooks/session-start-coord-check.sh` 在 DMSD 项目下静默退出 + DMSD CLAUDE.md「会话开始」段简化引用新 skill + 6 项目 CLAUDE.md 加「不主动用英语名词」规则段 + project-overview SKILL.md §0.1 + §1.7 同步 + 本文件「会话开始」铁律改成走 dmsd-startup skill）。5-25 晚段（追加：第三轮升级 — anti-ai-flavor 加第 3 触发词「**翻车**」单字 + 新建 `inbox.md` — itsuki 收尾中途立项自我迭代机制：发现新翻车点 → CC 按 5 字段「原文 / 6 类归类 / 违反铁律 / 根因 / 修正版」记 inbox，未来批量整理合并到 `references/翻车案例库.md`；改 5 文件：新建 `inbox.md` + SKILL.md 加 §7.5 + CLAUDE.md 触发词 2→3 + hook 提醒 + `我的环境.md` + `.html`）。早些（同晚段）：anti-ai-flavor HOW_TO_TALK.md 立项 + 跨 3 项目 session-wrap 加项 11/8 — itsuki 给 16 个翻车原句证据 → 4 根本问题 + 9 类细分 → 5 条总结铁律 → 方案 B 落地：SKILL.md 反面自检 + HOW_TO_TALK.md 正面教学互补 + 2 触发词「说人话」/「单词白名单」+ DMSD/SC26/Tango session-wrap 收尾清单同步加「全局环境清单同步」项 — 全局 6 文件 + DMSD 1 文件 + 2 memory + SC26 1 文件 + Tango 1 文件。早些 5-25（drift 脚本 bug 修 + 全局 `session-coord` 三层保险落地 — DMSD 2 文件 + 全局 4 文件 / 全局 Hooks 4→5；同时补登 5-24 iOS bug 批量修复会话遗漏的收尾）。早些 5-22（**3 会话产出** — ① 早 project-overview §0.1 漂移 957→980 / ② 中 iOS fork 融合归档 commit `46f779c` / ③ 晚 点呼机推进 + 撞海关查扣事件 + 立项 `session-wrap §5.5.15 decision-draft`）。早些 5-21（5-20 凌晨 4 会话审查作战 cron 自动 fire 产出 131 条 findings / 5-21 加系统 bug 专栏 + 第一批修复 8 条）。早些 5-19（project-overview 大改造 + 防漂 C 方案）。<!-- VERSION_OK -->

> **本文件 = Claude Code 的「当下书签 + 多会话协调」清单。短小为美。**
>
> **职责分工（重要 — 别再重叠）**:
>
> | 文件 | 内容 | 给谁看 |
> |---|---|---|
> | **WIP.md（本文件）** | 当下书签 + 最近 5 次会话 1-2 行总结 + 多会话占用 + 阻塞项 | CC（每次会话开始读全文）|
> | **TODO.md** | **所有未完成事项的完整 backlog**（真值）| itsuki + CC（每次会话开始扫顶部 200 行）|
> | **progress_overview.md** | 长期章节目录（稳定，每次 close 版本时更新）| itsuki + 教授读 |
> | **CHANGELOG.md** | 已发布版本编年史 | 全部读者 |
> | **commit history** | 每次改动的细节 | git log 可查 |
>
> **铁律**：未完成的事**只写在 TODO.md**。本文件**绝不**复述 TODO 的内容。
>
> - **会话开始**: CC 走 `.claude/skills/dmsd-startup/SKILL.md` §2 — 5 件必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）。**TODO + git status 启动不主动跑**（TODO 等 itsuki 主动问，git status 留收尾 §5.5.9）
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.8.0 <!-- VERSION_OK -->
**版本 bump 流程**: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权 — 即使 itsuki 说要 bump 但 §2 决策树不命中可以拒绝）

---

## 🎯 当前焦点

> **⭐⭐⭐ 沟通规则 cc-comm-rules v0.6.0（5-14 晚撤回 v0.5.0）** — 新会话必读 → `raw/2026-05-14.md §K` + 全局挂钩 `~/.claude/skills/cc-comm-rules/SKILL.md` <!-- VERSION_OK -->
> **v0.6.0 撤回 v0.5.0「英文自由用」** — 回归 v0.4.1「概念术语强制中文 + 技术事实保留英文」+ 新加 §2.3.1「术语后必带中文效果描述」。起因：v0.5.0 早段拍板当晚实测翻车（must 模式 / action 模式 / modified / 残 / 误判拒答 看不懂）。术语表 180+ 词条**保留**作 AC 学习材料，但 v0.6.0 后**不再自动加词**。<!-- VERSION_OK -->
> **配套新挂钩**：`anti-ai-flavor` 全局挂钩（CC 说话别像 AI、像真人聊天 — 气质层）— 6 类痛点 A-F（A 缺上下文 / B 复杂条件句 / C 网络黑话 / D 术语裸露 / E 字面化 / F 客套腔）按反感程度排序，always-on。详见 `~/.claude/skills/anti-ai-flavor/SKILL.md`<!-- VERSION_OK -->
> v0.1-v0.4「约束 CC 输出」思路全部作废。<!-- VERSION_OK -->
> **删的**：`pre-write-memory-block.sh` hook（itsuki 原话「我从来没有说过要拦截持久记忆」）。
> **新的**：`pre-bash-destructive-block.sh` 推全局 `~/.claude/hooks/`（原 DMSD 项目级保留）— 8 个原 pattern 不变，warn 模式不变，覆盖范围扩到所有项目。
> **备份**：5-14 改的 3 处旧版存 `~/.claude/_archive_2026-05-14/`（含 README 回滚命令）。
> **未来 propose**：把 `~/.claude/` 做成 git 仓库（永久解决全局配置无历史问题）— 等 itsuki 拍板。

> **⏰ Cloud Design 5-12 额度已过期** — 5-14 检查时已浪费。下次额度重置时间未知。

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 5 端代码层启动完毕（iOS + Android + Web + Backend + 点呼机），下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend — 不含点呼机）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话 — 不含点呼机）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-27 晚段-2 by [MacBook-Pro-Opus 4.7 1M / 整理 inbox 第一次实战 + anti-ai-flavor 6 类升 8 类]

**主题**：⭐⭐⭐⭐⭐ itsuki「启动」→ CC 跑 dmsd-startup 5 件事 → 4 件小事自决（drift 修 / scan.sh 命令补 SESSION_ID / 环境清单 hook 同步 / DMSD CLAUDE.md 加新沟通铁律「不要默认认识英语单词」）→ CC 翻车 5 词全裸（untracked/working tree/commit/repo/propose）itsuki 怒怼「你还是给我用英语单词了啊」→ 写 inbox #006 → itsuki「整理 inbox」第一次实战触发（5-25 立 inbox 机制后第一次批量整理）→ 合并 inbox #001-#007 到案例库 v1.1 #21-#27 + 加根本问题 5「自指失败」+ 类 J/K + 触发词 2→4 → itsuki「升级」→ 6 类升 8 类全链路 7 文件联动改（SKILL.md / hook / 全局 CLAUDE.md / DMSD CLAUDE.md / HOW_TO_TALK.md / 案例库 / inbox）→ itsuki「project-overview 漂移修好了更新状态」→ CC 当场翻 H 类「编造数据」车（漏算 03_dev -1 按记忆假设只 2 目录涉及）→ 补改后 drift ✅ 1194 → itsuki「做」commit → 别会话已 commit `a8c4837` + `26dc4ca` 全吞 → itsuki「收尾」+「继续不要再停」

**关键拍板**（itsuki 6 次）：
- 「报错原因修一下 + 全做」（4 件小事自决授权）
- 「commit 你自己看着做」（commit 颗粒度自决）
- 「整理 inbox」（5-25 立的批量整理触发词第一次实战）
- 「升级」（6 类升 8 类全链路 — CC 提的 J/K 升级到主体的提议被采纳）
- 「project-overview 漂移 你修好了的话记得更新状态」（drift 闭环验证 + 状态字段更新要求）
- 「继续啊，不要再停了」（收尾别太碎，加速）

**实际改动**（DMSD 3 + 全局 5 + iCloud 中枢 1 + DMSD raw 新 + 筑波 inbox 信号 7 + iCloud 会话总结新 = 12 文件）：
| 类别 | 文件 |
|---|---|
| DMSD repo | `.claude/skills/dmsd-startup/SKILL.md`（scan.sh 命令补 SESSION_ID）/ `.claude/skills/project-overview/SKILL.md`（§0.1 1189→1194 两轮 + 加 raw 主题词）/ `CLAUDE.md`（沟通铁律加新句 + 3 处 6→8 联动）|
| 全局 改 | `anti-ai-flavor/SKILL.md` v0.3.0（加 G+H 整段 + §4 6→8 + 边界 + 版本）<!-- VERSION_OK --> / `anti-ai-flavor-precheck.sh`（注入 6→8 + 6 问→8 问）/ `~/.claude/CLAUDE.md` 5 处 / `HOW_TO_TALK.md` / `references/翻车案例库.md` v1.0→v1.1（§一 #21-#27 + §三 根本问题 5 + §四 J+K + §九 触发词 2→4）<!-- VERSION_OK --> / `inbox.md`（#006 + 整理后清空 + 归档 + 7 条物理保留）/ `~/.claude/我的环境.html`（§3 Hooks 5→6 + 加 hook 行 + skill 段 6→8） |
| iCloud 中枢 改 | `项目档案/DMSD.md`（现状一句话 + 更新日志加本会话） |
| DMSD raw 新 | `05_logs/raw/2026-05-27_整理inbox+8类升级.md`（6 阶段 + 工程动作 + AC 价值） |
| 筑波 inbox 改 | `06_radar_inbox/ac_scratchpad_2026-05-27.md` 加信号 7 |
| iCloud 会话总结 新 | `03_素材_候选/会话总结/2026-05-27_MacBook-Pro_430f9ad0_总结.md`（详细日记式 7 阶段）|

**AC 价值** ⭐⭐⭐⭐⭐：模式 4 主体性升级链（5-25 立 inbox → 5-27 整理实战 → 抽 G+H → 升 SKILL.md 6→8 → 全链路 7 处改） + 模式 5 自指失败顶级 × 2 实战验证（CC 立完铁律下一秒翻车两次都被当场抓 — 阶段 2 + 阶段 5） + 模式 2 假设崩（跨目录 git mv source -1） + 模式 6 取舍（inbox 整理策略） + 模式 7 机制完备性（5-16 三层保险 + 5-25 inbox 自我迭代 + 5-27 早段-3 中枢档案铁律 + 5-21 daily-archive 4 层全跑通）

**残（下次跟进）**：
- daily-archive 脚本 cp 路径树「升学/AC/筑波大学.../03_素材_候选/」跟 ac-radar 写的「升学/大学入試/筑波大学.../06_radar_inbox/」**不同** — 同项目两套目录树，要不要统一？记 TODO
- anti-ai-flavor inbox.md 「已整理归档」7 条物理保留 — 下次整理时按案例库 §九「整理 inbox」SOP 把它们再往下挪
- G+H 新模式要不要更新 memory `feedback_anti_ai_flavor_翻车案例.md` 指向案例库 v1.1
- 5 处 `~/.claude/` 改动不在 git 跟踪 — 「~/.claude/ 做成 git 仓库」propose 5-14 / 5-26 立未拍板
- WIP「最近会话」累积 9 条远超 5 上限 — 等下次大砍

详细 raw：`05_logs/raw/2026-05-27_整理inbox+8类升级.md`

### 2026-05-27 晚段-1 by [MacBook-Pro-Opus 4.7 1M / anti-ai-flavor 双层防御立项]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动「推进 iOS app」→ CC 报告状态翻车 3 处（`deadline` / `clarify` / `diff` 英语裸露 + 病句 + 编造数据 9/3 出愿截止）→ itsuki 怒怼追问根因「为什么 CC 总是会自己莫名其妙用英语」→ CC 摊牌 3 层根因 + Claude Code hook 体系无 PostResponse 类硬约束 → **itsuki 主动提反方案**「立 hook 强制扫 + 白名单，命中就拦着」（独立提出 detective control 思路，没有任何工程 / 安全模式术语储备）→ CC 给 A/B/C 三方案 → itsuki 拍板 A+B + 白名单 6 类 + 4 模糊地带词「全收」→ 工程实装 3 新文件 + 2 改文件全在 `~/.claude/` 全局目录（iOS 原主题一行没碰）

**关键拍板**（itsuki 4 次明确决策 + 沟通纠正 4 次）：
- 「为什么 cc 总是会自己莫名其妙用英语 / 排查原因」（追问根因，不要表面修补）
- **「立 hook 强制扫 + 白名单 — 只有白名单里的英文允许出现 / 你觉得如何？」**（**itsuki 主动提方向** — 不是 CC 推荐）
- **「A+B」**（听完 CC 摊牌技术约束后接受 + 选近似方案）
- **「Claude / CC / hook / skill / commit / bug 这些都放进去」**（白名单模糊地带全收 — 最大化减少误报噪音的直觉判断）

**实际改动**（全局 7 + DMSD 4 + iCloud 1 = 12 件）：
| 类别 | 文件 | 改动 |
|---|---|---|
| 全局 新建 | `~/.claude/skills/anti-ai-flavor/whitelist.md` | 53 词白名单 7 类 + 怎么加词 SOP |
| 全局 新建 | `~/.claude/hooks/stop-scan-english-words.sh` + `.py` | Stop hook Bash 入口 + 真扫描脚本（读 transcript JSONL 找最后 assistant msg → 正则扫英文词 → 去白名单 → 命中追加 inbox） |
| 全局 改 | `~/.claude/hooks/anti-ai-flavor-precheck.sh` | 末尾加白名单注入段。同期 itsuki 自己改了 6 类 → 8 类（加 G 自指失败 + H 编造数据）+ 6 问 → 8 问 |
| 全局 改 | `~/.claude/settings.json` | 注册 Stop hook 到 `Stop` 钩位（10s timeout） |
| 全局 改 | `~/.claude/我的环境.html` | §3 全局 Hooks 6 → 8 |
| 全局 改 | `~/.claude/skills/anti-ai-flavor/inbox.md` | 加 #007 翻车（5 字段 — 3 处叠加 deadline / clarify / diff） |
| 全局 改 | `~/.claude/skills/anti-ai-flavor/SKILL.md` + `~/.claude/CLAUDE.md` | itsuki 自己改 — 8 类升级 + 触发词 2→3 |
| DMSD 新建 | `05_logs/raw/2026-05-27_anti-ai-flavor双层防御立项.md` | 完整素材 dump |
| DMSD 改 | `.claude/skills/project-overview/SKILL.md` | §0.1 体量表 1192→1193 + 05_logs 111→112 + raw 描述 / §6.2 raw 57→60（顺手修历史漂移） |
| DMSD 改 | `00_admin/TODO.md` | §🛠️ 加 §P 新段 5 条 + 顶部「最后更新」追加 |
| DMSD 新建 | memory `feedback_mechanism_over_self_discipline.md` | 沟通问题 itsuki 偏好工程化解法不接受 CC 自律承诺 |
| iCloud 改 | `06_radar_inbox/ac_scratchpad_2026-05-27.md` | 信号 6 双写（双写铁律落地）+ 总结段 5→6 信号 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 4 主体性最强级** — itsuki **自己提的方向**（独立提出 detective control 比 preventive control 强）+ 摊牌技术约束后立刻接受 + 拍板 A+B + 白名单全收。前所未有的「itsuki 提方案 CC 接受技术约束」颗粒度
- **模式 5 自指失败连锁** ⭐⭐⭐⭐⭐ — CC 在排查「为什么用英语」时又翻车 3 处。讨论沟通问题时表演了沟通问题本身
- **模式 7 机制完备性** ⭐⭐⭐⭐ — 三层保险范式之上新加第 4 层 detective control（事后检测）— 之前 3 层全是 preventive control（预防）
- **模式 6 取舍** — A/B/C 三方案 + 摊牌 PostResponse hook 不存在 + 白名单边界词「全收」
- **跨学科延伸 ⭐⭐⭐⭐**：preventive vs detective control（医疗 / 工程安全 / 网络安全 / 软件可靠性工程）/ 训练惯性 vs 用户偏好的协同进化 / hook 体系的钩位设计

**残（已入 TODO §🛠️ §P 5 条）**：iOS 推进延后 / 环境清单 md↔html 同步 / Stop hook 首次实战观察 / 翻车案例库 v1.1 核对 / 5 铁律没升 8 类

详细 raw：`05_logs/raw/2026-05-27_anti-ai-flavor双层防御立项.md`

### 2026-05-27 早段-3 by [MacBook-Pro-Opus 4.7 1M / 中枢档案污染排查 + 修 + 立铁律 + 立 hook]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动后查 WIP / 跑启动 SOP → 看到别会话写中枢 `项目档案/DMSD.md` 末尾「更新日志」段混入「模式 5 顶级 / AC 价值 ⭐⭐⭐⭐⭐」等 AC 评分 → 当场质疑「ac 素材给我写到哪去了 / 我不知道在我发现这个问题之前还有多少失误 / 帮我排查 / 让他们呆在该呆的地方 / 修好 skill 和 hook」→ CC 排查 3 中枢档案污染（DMSD.md / Tango.md / QTS.md）+ 1 个漏写（5-27 三段会话 AC 素材没进筑波 `06_radar_inbox/`）+ 立 3 层防御（中枢 CLAUDE.md 加铁律 / session-wrap SKILL.md §5.5.1.A 加去向表 + 强制双写 / 新建全局 PostToolUse hook 扫 AC 关键词）+ 翻车 4 处记 anti-ai-flavor inbox.md #002-#005

**关键拍板**（itsuki 3 次明确决策 + 协作模式 1 次纠正）：
- **「修 / 排查 / 让他们呆在该呆的地方 / 修好 skill 和 hook」**（最强自治授权 — 包括立 hook 这种长期防御层）
- **「修完后直接收尾」**（协作授权颗粒度顶级 — 跟 5-27 早段-2 / 凌晨 `/goal` 一脉相承）
- **「以下都是问题... 这句话就是个病句 / 这句话也看不懂 / 记得更新说人话 skill 的素材」**（沟通纠正 — 当场指出 4 处 CC 翻车并要求记 inbox）

**实际改动**（DMSD 1 改 + iCloud 中枢 4 改 / 新建 + 全局 3 新建 / 改 + raw 1 已有 = 9 文件）：
| 类别 | 文件 | 改动 |
|---|---|---|
| DMSD 改 | `.claude/skills/session-wrap/SKILL.md` | §5.5.1 加 4 个子节 — 5.5.1.A AC 素材去向表 / 5.5.1.B 强制双写铁律 / 5.5.1.C 学习过程为核心 / 5.5.1.D 反模式 |
| iCloud 中枢 改 | `项目档案/DMSD.md` | 砍 line 19 现状一句话 / line 50 更新日志 / line 51 更新日志 里的 AC 模式分析 + 评分 |
| iCloud 中枢 改 | `项目档案/Tango.md` | 砍「模式 4 v1→v2 演进 AC 证据」「AC 出愿研究方法证据」「AC 研究方法素材」3 处 |
| iCloud 中枢 改 | `项目档案/QTS.md` | 砍 line 8-16 itsuki 拍板段 / line 41-50 关联度评估 + AC 价值点 + 风险 2 大段 |
| iCloud 中枢 改 | `CLAUDE.md` | 末尾加「中枢档案铁律」段 — 只写工程事实 / AC 分析归别处 / AC 内容种类对照表 / 反模式 |
| iCloud 新建 | `06_radar_inbox/ac_scratchpad_2026-05-27.md` | 补 5-27 三段会话 + 早段-3 AC 信号 5 条（之前漏写） |
| 全局 新建 | `~/.claude/hooks/post-edit-zhongshu-ac-pollution-check.sh` | PostToolUse hook — 扫中枢 项目档案/*.md 写入时是否含 AC 评分关键词，warn 模式不阻断 |
| 全局 改 | `~/.claude/settings.json` | 注册 PostToolUse Write\|Edit matcher 调上面 hook |
| 全局 改 | `~/.claude/skills/anti-ai-flavor/inbox.md` | 加翻车 #002-#005 — 4 条本会话翻车（PostToolUse 术语 / AC 素材去向矩阵病句 / 强制调 ac-radar flush 病句 / 引用注脚装腔）|

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 自指失败 顶级** — CC 在写「AC 信号扫描器」给筑波 AC 用的中央 inbox 时，自己漏写中央 inbox；CC 在维护「跨项目协同板」时，把 AC 素材污染了协同板。讨论问题时表演了问题本身。
- **模式 7 机制完备性** — 立 3 层防御（铁律 / 双写规则 / hook 扫描），不是 ad hoc 修一次而是「按已建立的机制范式补全」（参考 ac-radar / cc-comm-rules / session-coord 三层保险模式）。
- **模式 6 取舍** — 哪些「AC tag」算污染哪些算注脚 — decision_log 末尾「相关：raw」算注脚不算污染（边界判断 — false positive 3 处）。
- **协作纠错 × 4** — itsuki 当场质疑（污染）+ 让 CC 自查（还有多少失误）+ 让 CC 立规则防再犯（修 skill / hook）+ 沟通纠正（4 处病句立刻指出）。
- **学术延伸**：documentation hygiene / separation of concerns / detective control vs preventive control（hook 是检测控制，铁律是预防控制）/ AI alignment 协作层。AC 面试可挂「文档系统设计 + 协同 AI 时的清洁度维护」。

**残（下次跟进 — 全部已入 TODO §🛠️ §O）**：
- anti-ai-flavor inbox 累计 5 条，到 itsuki 之前定的「3-5 条后写整理 inbox SOP」阈值 → 下次会话或 itsuki 主动喊「整理 inbox」时合并到 `references/翻车案例库.md`
- 中枢 3 档案铁律落地 — 各项目 CLAUDE.md（Tango / QTS / 父项目 大学入試 CLAUDE.md）要不要加指针让各项目 CC 知道这条铁律
- 全局 `~/.claude/` 不在 git → settings.json + hook 新建无历史记录（5-14 + 5-26 已立 propose「~/.claude/ 做成 git 仓库」未拍板）

详细 raw：本会话主题以「修工具 + 立规则」为主，AC 素材直接进 `06_radar_inbox/ac_scratchpad_2026-05-27.md`，DMSD raw 不另写

### 2026-05-27 早段-2 by [MacBook-Pro-Opus 4.7 1M / 全项目审查 + Vite 决策漂移 6 处修]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动「全项目审查 — 每个文件 / 文件关联 / 关联 skill / 内容审查 / project-overview 检查全跑一遍」+ 强调「主目录无编号文件分析 / 各文件夹莫名其妙的文件 / 不要偷懒 / 扫整个项目所有文件 / 收尾不要给我留问题 / 所有问题加 TODO / 我可以直接关闭会话」→ CC 一次过扫 1189 文件 + grep 决策关键词 + 比对 SKILL.md §0.1 + 读关键文件 → 直接修 6 处 Vite 决策漂移 + 物理清 7 个 .DS_Store + git mv `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` → 99_archive + TODO §🛠️ §N 加 8 条 backlog

**关键拍板**（itsuki 3 次明确决策 + 协作模式 3 次校准）：
- **「做完直接收尾 + 不要停下来问我」**（协作授权颗粒度顶级 — CC 工程层 + memory 规则托底的全部自决，跟 5-14「不要把 CC 该做的事甩回 itsuki」+ 5-26「TODO 关条目不要问」一脉相承）
- **「v1.0 上线目标可能是旧的，比如网站决策文档」**（举例驱动 — itsuki 不知道具体哪里，让 CC 全扫找出来）
- **「不要偷懒 / 扫整个项目所有文件 / 各种问题 / 我要强调非常多遍」**（强度强调 — CC 必须全量执行非 sample 抽查）

**实际改动**（DMSD 8 文件改 + 1 git mv + 1 新 raw + 7 .DS_Store 物理删 = 17 件）：
| 类别 | 文件 |
|---|---|
| 改（4 处「当前状态」漂移修） | `README.md` × 2 行（48 + 74）/ `03_dev/LATEST.md` 行 13 / `00_admin/progress_overview.md` 行 75 ASCII 图 |
| 改（其他漂移修） | `03_dev/teacher_web/WEB_DESIGN_LOG.md` §11.9 W1 行 ✅ → ❌ + `03_dev/teacher_web/v1/src/api/client.ts` 行 3 注释 |
| 改（同步） | `00_admin/TODO.md` 加 §🛠️ §N 8 条 + 时间戳 / `.claude/skills/project-overview/SKILL.md` §0.1 raw 57→58 + §6.2 加 2 条新 raw entry |
| git mv | `99_archive/2026-04-22_ios_round1_design_brief/DESIGN_BRIEF_Round1_context.md` ← `student_ios/_archived_DESIGN_BRIEF_Round1_context.md` |
| 物理删 | 7 个 .DS_Store（主目录 + 7 子目录） |
| 新建 | `05_logs/raw/2026-05-27_全项目审查.md`（9 段 + AC 价值 + 工程动作汇总） |

**核心结论**（给下次 CC 启动看）：
- **主目录 6 个无编号文件**（CLAUDE.md / README.md / CHANGELOG.md / LICENSE / .gitignore / .graphifyignore）全部符合开源项目约定 — itsuki 担心的「主目录无编号文件可能不该在那」**结论是没问题**
- **真问题在 teacher_web Vite 决策漂移** — 5-26 已废弃但 4 处「当前状态」描述还写 TS+Vite+Zustand（已全修）
- **`progress_overview.md` 4-17 后没动 + v0.8 之后累积 28+ commit 未 bump** → 入 TODO §N 第 6 + 7 条

**残（下次跟进 — 全部已入 TODO §🛠️ §N）**：99_archive 散件归档 / 01_specs 4 个 .pages 归档 / 4-19 backlog 物理归档 / 跑 `graphify update .` / `backend/demo/` 处置 / progress_overview 大改 / 是否 bump v0.9 / 「决策状态扫描 hook」长期 propose

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 顶级** — itsuki 三度「不要偷懒 / 扫所有文件 / 不要给我留问题」 → CC 协作模式升级（全量扫 + 自决修 + 修不了塞 TODO）
- **模式 2 假设崩** — itsuki 担心主目录无编号文件 → 调查发现全部符合约定，真问题在 Vite 决策漂移
- **模式 7 机制完备性** — 文档同步机制当前只覆盖「文件存在 / 版本号 / 体量」3 类，「决策状态描述」类没机制 → TODO §N 第 8 条立项扫描 hook propose
- **模式 6 取舍** — 自决修 vs 塞 TODO 边界（工程动作 + 文档校准类自决 / 命名 + 归档结构 + bump + 长期 propose 类塞 TODO）

详细 raw：`05_logs/raw/2026-05-27_全项目审查.md`

### 2026-05-27 凌晨~早段 by [MacBook-Pro-Opus 4.7 1M / teacher_web v1.0 深夜推进 + 醒后 backend 审查 9 处修复]

**主题**：⭐⭐⭐⭐⭐ 跨 6+ 小时拼接会话 — 5-26 23:30 itsuki 启动「teacher_web 实现目标 + 进度简报」→ 设 `/goal` v1.0 完整体 → 5-27 00:00 拍板「不 push 57 commit 到 GitHub / 继续到撞墙」「严格按 4 份规划文档对齐 / 不要偷懒」「GOAL 模式一直做 / 不再做决策 / 我去睡了」 → CC 单边推进凌晨 31 commit（5 个 P0 必做 + 13/16 page 真接 backend + alembic c1d2e3f4 + WebSocket /ws/teacher + spec §11.4 改判扣分 + spec §7.5 自动扣分）→ 5-27 早 itsuki 醒后「审查到底有没有做好 / 不需要决策的直接修 / 决策的加 TODO 跳过 / 收尾后直接关会话」→ CC 自查 5 维度全过 + 5 处日语注释中文化收尾。**93 commit ahead of origin / 全部 9 处真 bug 已修完 / alembic head = c1d2e3f4 / 61 endpoint 真 import 通过**

**关键拍板**（itsuki 6 次）：
- 「不 push 57 commit / 继续到撞墙」（放弃 cloud agent 接力机制）
- 「严格按 4 份规划文档对齐」（system_features / RollCall_Spec / DESIGN_BRIEF / WEB_DESIGN_LOG）
- 「GOAL 模式一直做 / 我去睡了 / 不再做决策」（替默认决策最强授权）
- 「卡 bug 收尾就好别停了」（v1.0 production 验收超单会话边界）
- 醒后「审查到底好没好 / 不需要决策的直接修 / 决策的加 TODO 跳过」（self-audit + 自主修复授权）
- 「不要给我留问题 / 不要停下来问 / 收尾后直接关会话」（最终收尾授权）

**实际改动**（93 commit ahead / 凌晨 31 commit + 醒后审查 8 commit + 中文铁律收尾 5 处）：
| 类别 | 文件 |
|---|---|
| backend 新 model | `models.py` 加 `DemeritEvent` / `CleaningAssignment` / `FrontDeskItem` 3 张表 + Float import + `Student.is_demo` 字段 |
| backend 新 router | `routers/discipline.py` + `cleaning.py` + `front_desk.py` 各 3-4 endpoint + `main.py` 注册 |
| backend FC-027 | `announcements.py` list/detail 用 `get_current_principal` 同时接受 student/teacher token |
| backend R4 helper | `deps.py` 加 `get_current_principal` + `dorm_units_for_teacher`（CROSS_DORM_ROLES 4 类 → None / 男寮 → [1,2] / 女寮 → [4]）|
| backend 自动扣分 | `rollcall.py` settle late=1.0 / absent=2.0 自动加 `DemeritEvent` + `study.py` absent=1.5 自动加 |
| backend 改判扣分 | `rollcall.py` PATCH /events/{id} 实装 spec §11.4 12 类 transition + `_OVERRIDE_DEMERIT_MAP` + `_apply_override_demerit` |
| backend WebSocket | 新建 `ws_manager.py` + `routers/ws.py` + main 注册 + 4 处 broadcast（rollcall checkin / override / applications create）|
| backend alembic | 新建 `c1d2e3f4_add_demerit_cleaning_frontdesk.py` migration（含 CHECK / FK / index）|
| teacher_web 新组件 | `src/index.html` 加 RollCallSummary（spec §5.6 4 区块）+ RegistrationCodePanel（§11.9.1）+ StudyAttendancePage（§7.3 + iOS 对齐）|
| teacher_web App() 改造 | authToken + sessionStorage 还原 + 401 全局拦截 + WebSocket /ws/teacher + 役职別 home 重定向 + 13 page 接 backend |
| teacher_web client.js | 内联 `client.ts → client.js` 35 个 endpoint helper + setOnUnauthorized + openTeacherWS 工厂 |
| teacher_web FC-024 | 删 `window.SHARED_PASSWORD = '12345678'` 明文密码 + LoginScreen 改 backend 真实认证 + DEMO_MODE URL gate（`?demo=1`）+ APP_VERSION 动态 |
| 中文铁律收尾 | `src/index.html` 5 处日语注释中文化（FC-024 / DEMO scaffold / LoginScreen err msg / WS demo / Task #13 RollCallSummary docstring）|
| 文档同步 | `BACKEND_DESIGN_LOG.md` 加 5-27 9 处修复入档 / `系统bug专栏.md` FC-025/26/27/28 标 N/A / `WEB_DESIGN_LOG.md` + `DESIGN_BRIEF.md` + `v1/README.md` 同步真实状态 / 新建 `01_specs/teacher_web_v1.0_backend_models_propose.md` 229 行 |
| raw | 新建 `05_logs/raw/2026-05-27_teacher_web_v1.0_深夜推进.md` 200+ 行 9 章（含 §9 审查作战）|

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 4 主体性最强级** — itsuki 设 `/goal` + 「我去睡了 / 不再做决策」 = CC 单边推进 6+ 小时 31 commit 替默认决策（前所未有的授权颗粒度）
- **模式 5 元认知** — 5-27 早 itsuki 「审查到底有没有做好」 = 主动质疑 CC 工作质量（不盲信）→ CC 自查 9 处真 bug 落地
- **模式 6 取舍** — 「严格按 4 份规划文档对齐 / 不要偷懒」 vs CC 偷懒倾向（不读完 spec 直接写代码）
- **协作纠错 × 3** — 「不 push 到 GitHub」「不模糊界限」「不要给我留问题」3 次明确边界
- **学术延伸**：「自主代理边界」 + 「production 验收硬约束 vs 单会话工程量」 + 「self-audit 是协作信任的核心」 + AC 面试可挂「跟 AI 协作时何时给最大授权 + 何时严格审查」

**残（已加 TODO）**：
- production DB 跑 `alembic upgrade head` 应用 c1d2e3f4（开发环境已 upgrade ✅）
- 3 个 page 等 backend P2 endpoint：NotificationsPage / AccountsPage / CommunityPage
- backend P2 工作待 itsuki 字段决策：CommunityPost + Notice 字段（匿名 author_id / Notice vs Announcement 合并）
- 93 commit 未 push origin/main — itsuki 拍板「不 push」执行中
- `01_specs/teacher_web_v1.0_backend_models_propose.md` 229 行 propose 等 itsuki review

详细 raw：`05_logs/raw/2026-05-27_teacher_web_v1.0_深夜推进.md`（9 章 + 审查作战段）

### 2026-05-26 晚段-4 by [MacBook-Pro-Opus 4.7 1M / teacher_web Vite 废弃 + Ryō polish 回滚]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动「推进 teacher web 开发 + 问有没有前端 skill」→ CC 报告 frontend-design skill → itsuki 选「调 skill 优化设计」→ CC 起 Vite dev server → itsuki 看到屏幕怒怼「这他妈根本不是我的 web 啊」→ CC 调查发现 v1/ 两套并存（5-02 Vite + TS 实装版 + 4-21 Ryō standalone 老 demo）→ itsuki 拍板「Vite 实装版垃圾归档，用 B」→ CC 归档 13 文件 + 物理删 node_modules 81MB + dist + 修破工具脚本（demo_server.py 死链 → python http.server）→ CC 跑 frontend-design skill 给 Ryō polish（米白和纸 / 朱色 sharp accent / 明朝体 Shippori Mincho B1 / 和纸 SVG 噪点 / shadow 加深 / 4 处关键 UI 用新 token）→ itsuki 看完整体不喜欢一句「回滚」→ git checkout index.html 全退 + 同步改 README / DESIGN_BRIEF 写「polish 试过被回滚」事实记录

**关键拍板**（itsuki 7 次明确决策）：
- 调 frontend-design skill 优化设计
- 「先告诉我我现在怎么看 teacher web」 + 「一般开发者怎么变改边做」（学习需求 — 三窗口工作流 + HMR 教学）
- **「Vite 实装版就是个垃圾，给我归档，用 B」**（推翻 5-02 立项决定 — 5 端代码层 v0.8 里 teacher_web 这一端从 v0.8 回退到 v0.3 阶段）
- **「看你」**（协作授权颗粒度 — 工程层 CC 自定）
- 「之前的垃圾 web 不要再污染我的项目文件了，归档」（工程洁癖 — 不只 gitignore，物理删）
- 「试一下，全改完后我看看效果」（接受 polish 试做）
- **「回滚」**（主观品味驱动拒绝 AI 设计建议）

**实际改动**（DMSD 5 改 + 1 删 + 13 归档 + 1 新 raw + 2 新 decision + 1 新 WEB_DESIGN_LOG §12 = 23+ 文件）：
| 类别 | 文件 |
|---|---|
| 归档 Vite 实装 13 文件 → `99_archive/2026-05-26_teacher_web_vite实装作废/` | App.tsx / main.tsx / pages/×5 / Shell.tsx / store/auth.ts / vite_root_index.html / package.json / lock / vite.config.ts / tailwind.config.js / postcss.config.js / tsconfig.json / tsconfig.tsbuildinfo |
| 物理删 | node_modules（81MB）+ dist |
| 改 | `v1/src/index.html`（polish → 回滚）/ `v1/开发模式跑.command`（修死链）/ `v1/tomoshibi` CLI（同上）/ `v1/README.md`（重写）/ `teacher_web/DESIGN_BRIEF.md`（删 round2/ 段 + 加 _legacy/ 位置） |
| 新建 | `05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md`（深度 AC 素材） |
| 改 | `05_logs/decision_log.md`（加 2 条 — Vite 废弃 + polish 回滚）/ `WEB_DESIGN_LOG.md`（§实装进度速查表大改 + 加 §12 新段） |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 3 失败→吸取教训 顶级** — 5-02 立项 Vite 实装 → 5-26 推翻整体废弃。约 1 个月间隔 + 5 端 v0.8 启动里 1 端整体作废 = 罕见大事件
- **模式 5 顶级 × 2** — 前端开发流程学习（不知 HMR / 三窗口工作流 → CC 教 → 现在懂跨端反馈速度差异）+ 文档诚实记录哲学
- **模式 6 取舍 × 多** — A/B/C/D 范围选项 / polish 8 处改动 vs 回滚 / 归档范围 5 类决策 / 物理删 vs 留
- **协作纠错 × 3** — CC 没核对启动了哪套被怒怼 / CC 假设 round2/ 存在 → 调查塌缩真相 / CC polish 试做 → itsuki 拒绝（最大）
- **主体性 ⭐⭐⭐⭐⭐**：7 次明确拍板 + 推翻自己 5-02 立项 + 拒绝 AI 设计建议
- **学术延伸性**：Sunk cost fallacy 反例 / 用户体验驱动 vs 技术先进性 / 设计审美主观性 + 可回滚工程方法 / 跨技术栈反馈循环长度对比 / 协作信任设计（提前承诺降低试验门槛）/ 文档诚实记录历史 / AC 面试可挂「跟 AI 协作时何时采纳何时拒绝」

**残（下次跟进，已入 TODO §🛠️ L）**：
- `demo_server.py` 写一份 — 恢复 NFC iPhone 快捷指令实时点呼 demo
- 系统bug专栏 FC-025/26/27/28 全部 N/A（Vite 字段对齐已 N/A — Vite 整体废了）
- 未来设计层 polish 候选方向（单页改造 / 字体单独换 / 找 itsuki 喜欢的参照系）

详细 raw：`05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md`

### 2026-05-26 晚段-3 by [MacBook-Pro-Opus 4.7 1M / iOS demo 后门清理（做法 B）+ 字段对齐零漂移]

**主题**：⭐⭐⭐⭐⭐ itsuki 拍板「推进 iOS — A demo 后门 + B 字段对齐 一起做 / 先备份 demo 快照 / 主推进只走干净 app」→ CC 提议 A/B/C 三种 demo 删除策略 → itsuki 选 B「保留 `#if DEMO` 包好的代码」→ 落地 5 处裸 demo fallback 删 + 全量字段比对零漂移 + anti-ai-flavor inbox.md 首次实战触发（CC 翻车「Task # / SEED.user / 做法 B」内部代号）

**关键拍板**（itsuki 5 次明确决策）：A+B 一起做 + 备份策略 + 做法 B（B 选 vs A 全删 vs C 不做）+ 「说人话 + 翻车 + skill 迭代」3 触发词连击 + 收尾 commit 自决权

**实际改动**（5 文件 + 1 全局 + raw 5-26 阶段 10）：
| 文件 | 改动 |
|---|---|
| `AppStore.swift` | 5 处裸 demo fallback 删（computedRoomNo M205 / createAccount 7 字段 / 公告 3 处 catch 分支构造伪数据）|
| `99_archive/2026-05-26_ios_v1_demo_snapshot/` | 新建 — iOS 主项目完整复制 41 swift + README / 1.1M |
| `TODO.md` | 关 line 248 漂移条目 + 重写 line 1010 demo-only 清单 iOS 进度 6/6 + SEED 延期理由 |
| `project-overview SKILL.md §0.1` | 99_archive 552→594 / 总计 1127→1169（anticipate 未 commit 42）|
| `~/.claude/skills/anti-ai-flavor/inbox.md` | 翻车 #001（首次实战）— 5 字段分析 CC 用内部代号沟通失职 |
| `raw/2026-05-26.md §阶段 10` | 完整 dump |
| 中枢 `项目档案/DMSD.md` | 现状一句话补 5-26 三段进度 + 更新日志加晚段条目 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 2（假设崩）** × 3：CC 假设「字段严重漂移」崩（零漂移）/ 假设「SEED 改后端拉是必做」崩（132 处引用 + 数周架构重构）/ 假设「itsuki 跟 CC 同步内部代号」崩
- **模式 5（自指失败）** ⭐⭐⭐ — CC 在讲反 AI 味的回复里大量用术语裸露，讨论问题时表演了问题本身
- **模式 6（取舍）** × 4：A/B/C demo 策略 / SEED 整文件包 vs 不包 / commit 范围 / Task 完成范围解读
- **模式 7（机制完备性）** — anti-ai-flavor inbox 首次实战跑通（5-25 立项 → 5-26 真触发）
- **学术延伸**：条件编译（`#if DEMO`）vs 依赖注入 vs 独立 fork vs feature flag 4 种 demo 策略对比 / iOS 演示型架构 → 生产化 = 数周架构重构（technical debt 案例）

**残（下次跟进）**：
- SEED.swift 整文件包 `#if DEMO` 延期到 backend 上线后做
- working tree 累积大堆改动（teacher_web vite 作废 + IOS_DESIGN_LOG / decision_log / CLAUDE.md 等 itsuki / 别会话改的）— CC 不擅自 commit，只 commit 本次清楚做的工作

详细 raw：`05_logs/raw/2026-05-26.md §阶段 10`

### 2026-05-26 晚段-2 by [MacBook-Pro-Opus 4.7 1M / 启动 SOP 集中化 + DMSD CLAUDE.md 247→190 重写]

**主题**：⭐⭐⭐⭐⭐ 4 件大事 — (1) `pre-bash-destructive-block` hook 行为约定立项（CC 看到 WARN 自己停下想，没必要不走 / 有必要继续 / 灾难级才问 itsuki）(2) 沟通铁律「不主动用英语名词」全局 + 6 项目 CLAUDE.md 落地（除非项目代码 / 文档 / 文件名真出现过否则一律中文）(3) 启动 SOP 集中化 — `dmsd-startup` skill 立项（§2 5 件必做事 + §4 按需触发段）+ 全局 `session-start-coord-check.sh` 在 DMSD 项目下静默退出 (4) DMSD CLAUDE.md 247→190 行重写到 QTS 模式（A 砍 120 + B 搬 35 + D 补 70 — Skills 继承段 / Hooks 继承段 / 全项目中枢联动 / 沟通规则简版 / Git）+ CLAUDE.md 文档观转变（时间戳冗余禁止）

**关键拍板**（itsuki 6 次明确决策）：
- destructive-bash 行为约定：「不用停下来，只要自己停下来好好思考一遍有没有必要，然后没必要就不走，有必要就接着做」
- 沟通铁律：「除非这个词在项目代码 / 文档 / 文件名里真出现过，否则一律用中文」
- 启动 skill 集中化：「这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？」→「每项目独立启动 skill / env-diff 留全局 / coord-check 融进项目 skill」
- 时间戳冗余禁止：「像这种 xxx 新加，完全没必要写到 claude.md 里啊，只是浪费时间」
- CLAUDE.md 重写到 QTS 模式：「全部按照你的想法做。做之前记得先 git 一次备份」
- auto mode 拦截 `~/.claude/CLAUDE.md` 修改 → itsuki 切手动模式 + 「跑」短指令

**实际改动**（DMSD 7 + 全局 2 + 6 项目 CLAUDE.md + 新主题 raw = 16 文件 / 2 commit）：
| 文件 | 改动 | commit |
|---|---|---|
| `~/.claude/CLAUDE.md` | 加沟通铁律段 + destructive-bash 行为约定段 | ⚠️ 全局非 git repo 无备份 |
| `~/.claude/hooks/session-start-coord-check.sh` | DMSD 项目下 `exit 0` 静默退出 | ⚠️ 同上 |
| `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md` | 新建（200+ 行）— §2 5 件 + §3 不做 + §4 按需触发 + §5/§6 边界与行为约定 | `d1fc8b3` + `d608846` |
| `~/dev/DMSD/CLAUDE.md` | 第 1 次加 2 段 → 第 2 次重写 247→190 QTS 模式 | `d1fc8b3` + `d608846` |
| `~/dev/DMSD/00_admin/WIP.md` | 顶部时间戳 + 第 19 行启动铁律改成走 dmsd-startup（修「TODO 200 行 + git status」旧冲突）+ 本条目 | `d1fc8b3` + 本会话末 |
| `~/dev/DMSD/.claude/skills/project-overview/SKILL.md` | §0.1 + §1.7 加 dmsd-startup + §1.7 描述加 §4 + §6.2 加 5-26 两个 raw 行 | `d1fc8b3` + `d608846` + 本会话末 |
| `~/dev/DMSD/00_admin/TODO.md` | §🛠️ K 新段 5 条（启动 SOP 集中化残留）+ 顶部时间戳 | 本会话末 |
| `~/dev/{QTS,tango,SC26,practice,cc-project-template}/CLAUDE.md` | 各自加沟通铁律段（顶部）| 各 repo 自管 |
| `~/dev/DMSD/05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` | 新建 600+ 行主题 raw（10 阶段 + 工程动作汇总 + AC 价值评分）| 本会话末 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 顶级 × 4** — hook/skill 二选一 vs 互补认知 / destructive-bash WARN 不是阻断是行为约定 / 时间戳冗余反感正式立铁律 / QTS 模式作为良好范本（CC 学 itsuki 整理）
- **模式 6 取舍 × 3** — pre-bash-destructive ABC / 启动 hook 分工 ABC / CLAUDE.md 重审 3 选项（最稳/中等/激进）
- **模式 4 版本演化** — CLAUDE.md 247→190 大改写到 QTS 模式
- **协作纠错 × 2** — auto mode 拦截 → 切手动 + 「跑」短指令 / 「先 git 备份」工程习惯被 itsuki 教 → CC 立即照做
- **CC 主动发现** — 审查 CLAUDE.md 分 A/B/C/D 4 类（itsuki 没明说要这种分类）
- **工具发现** — `git commit -o` 限定 path 不动 staged 区
- **学术延伸性** — single responsibility principle / Unix philosophy / declarative vs imperative documentation / actor model（CC 实例间共享文件传信）

**残（下次跟进 — 全部已入 TODO §🛠️ K）**：
- 全局环境清单 `~/.claude/我的环境.md` 没同步（dmsd-startup 新建 + 全局 hook 改 + 全局 CLAUDE.md 改）
- `~/.claude/` 做成 git 仓库 propose（5-14 立 / 5-26 强化）
- 其他 5 项目独立启动 skill 都没做
- sync-check 警告 `bin/check_overview_drift.sh` 联动文件未改（别会话遗留）
- WIP「最近会话」段已 8 条超过 5 条上限（itsuki 决定删哪条）

详细 raw：`05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md`

### 2026-05-26 by [MacBook-Pro-Opus 4.7 1M / iOS Bot 1 复查 + 全项目中枢注册]

**主题**：⭐⭐⭐⭐ 两次会话 — 早段 iOS Bot 1 误删功能复查（全量 diff fork vs 主项目 v1 证实没遗留误删 + 撤暗夜模式 v2 + 3 上架配置归位 03_dev/student_ios/v1/TomoshibiApp/ + memory 加铁律「TODO 关条目不要问 itsuki」+ CC「说人话」触发 2 次）；晚段 itsuki 介绍 5-26 新建「全项目中枢」机制（iCloud / 大学入試 / 全项目中枢/ 下 4 项目互通板 — 大学入試 / DMSD / Tango / QTS）→ DMSD CC 注册档案（档案状态 ⏳→✅ + 补现状一句话 + 跟其他项目关系 + 加 DMSD CLAUDE.md「全项目中枢联动」段）

**关键拍板**（itsuki 7+ 次明确决策）：
- 早段：推 iOS / 选 A Bot 1 复查 / **「TODO 关条目不要问，做完就该 CC 自己删」**（怒怼立铁律入 memory）/ 3 上架配置文件归位到 iOS 主目录 / 暗夜模式撤回 v2 再做 / A+B 立项后撤回（看工作量评估）
- 晚段：4 步注册任务（读中枢 CLAUDE.md / 改 项目档案/DMSD.md / 扫 信箱/DMSD_inbox.md / 改 DMSD CLAUDE.md 加联动段）

**实际改动**（DMSD 8 + 全局 1 memory + iCloud 中枢 1 + 本 raw 新增段 = 11）：
| 文件 | 改动 |
|---|---|
| `05_logs/raw/2026-05-26.md` | 新建（早段 8 阶段 + 工程动作汇总）+ 追加阶段 9（全项目中枢注册）|
| `00_admin/TODO.md` | 关 4 条（Bot 1 编译 / §D5 复查 / N18 / 3 空壳屏）|
| `03_dev/student_ios/IOS_DESIGN_LOG.md` | §6.5 + §8.2 N18「做」→「v2 再做」|
| `03_dev/student_ios/v1/TomoshibiApp/{AppIcon-1024.png, PrivacyInfo.xcprivacy, TomoshibiApp.entitlements}` | git mv 从 99_archive 归位 |
| `CLAUDE.md` | 末尾加「全项目中枢联动 (2026-05-26 起)」段 |
| `.claude/skills/project-overview/SKILL.md` | §0.1 体量 1124→1127 + 03_dev 396→399 + 99_archive 555→552 + 05_logs 104→105 |
| memory `feedback_no_handoff_work_back_to_itsuki.md` | 加 5-26 案例 + 新铁律「TODO 关条目不要问」|
| iCloud 中枢 `项目档案/DMSD.md` | 注册 ⏳→✅ + 补现状一句话 / 跟其他项目关系 / 基础信息漏字段 / 删注册任务段 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 顶级**（早段 TODO 怒怼）— 同根反复犯（feedback memory 5-14「不要甩工作回 itsuki」5-26 再翻车） → 升级新具体场景铁律
- **模式 4 机制扩展**（晚段中枢）— 从「项目内多会话协同（session-coord）」升级到「跨项目协同（全项目中枢）」
- **模式 5 元认知**（早段 Bot 1）— 5-22 担心遗留误删 → 5-26 主动复查证实
- **模式 6 取舍** × 多 — A+B 立项→看工作量撤回 / 3 文件归属判断 / 中枢挂大学入試 vs ~/dev/ / git mv 保留 blame
- **模式 2 假设崩** — CC diff HomeStubs `EmptyView` 一瞬错读 → 完整读上下文修正
- **协作纠错** × 3 — TODO 不要问 / 说人话 × 2（anti-ai-flavor 实战机制跑通）
- **学术延伸性**：分布式系统「actor model」类比（CC = 独立 actor / 共享文件 mailbox 传信）/ 多 agent 协同设计

**残（下次跟进）**：
- 老师公告 A+B（Android + 教师 Web）+ 学生注册码 C+D 留下次
- WIP §当前焦点 #1+#2 描述要改准（标明剩 Android + Web 不含 iOS — iOS + backend 已装）
- 中枢机制首次实战 — Tango / QTS 还要各自跑注册流程
- 中枢「信箱」未来跨项目留言试用 — 没用过不知道有没有 CC 忘看 inbox 的失败模式
- DMSD CLAUDE.md「中枢联动」段是否要补 hook（启动强制读 inbox）— 等观察几次实战
- 本次 + 5-24 + 5-25 累积改动未 commit — 等 itsuki 拍板 commit 顺序
- AC 中央 inbox `~/Library/.../02_ac_workspace/06_radar_inbox/` 路径不存在 — ac-radar inbox 实际路径要查

详细 raw：`05_logs/raw/2026-05-26.md`（10 阶段 + 工程动作汇总 + 阶段 9 追加段）

### 2026-05-27 深夜-3 by [MacBook-Pro-Opus 4.7 1M / iOS 全自主审查 + 修 + 收尾]

**主题**：⭐⭐ itsuki 启动「审查这个 iOS APP 看有什么问题，然后去做去修」+ 紧接「做完后就直接收尾，不要给我留问题，也不要停下来问我，所有的问题加到 todo 里面」充分授权 → CC 5 维度系统过 41 文件（demo 后门残留 / A-XXX bug 标记 / catch 错误处理 / Force unwrap / NFC 实装）→ 修 1 处 + 写 2 条 TODO + 全自主收尾不问。

**关键拍板**（itsuki 2 次）：「直接做去修」（明确授权直接修不只审查）/「做完后就直接收尾」+「所有问题加到 todo」+「我可以直接关闭这个会话」（最强自治授权 — CC 自己拍板每项归类「直接修」vs「TODO 延期」vs「跳过」）

**审查结论 5 维度**：
- demo 后门残留 ✅ 3 处 `demo1234` 全已包 `#if DEMO`（5-26 做法 B 落地干净）
- A-XXX bug 标记 ✅ 8 个全已修（A-019/020/024/030/033/035/036/037/038）
- catch 错误处理 — 7 处 5 正确 / 2 有问题（写 TODO）
- Force unwrap — `MyPageStubs.swift:1404` `c.score!` 改 `map ?? _`
- NFC 实装 ✅ UI 19 处日语完整 / backend 联动 4 处 `TODO[backend]` 是合法待办

**实际改动**：`Features/MyPage/MyPageStubs.swift` 1 行 + `TODO.md §D` 加 2 条 + 本 WIP 段 + project-overview §0.1/§6.2 raw 56→57 + 新建 raw `2026-05-27_ios_审查会话.md`

**TODO 加项**（→ TODO §D 工程债务延后修）：
- `StayListStubs.swift:475` catch 降级 mock 假数据 — 修法：区分 `APIError.unauthorized` 走 mock / 其他错误显示提示
- `MyPageStubs.swift:1637` catch 暴露 `error.localizedDescription` — 修法：区分错误类型显示日语友好提示

**AC 价值** ⭐⭐ — 模式 6（工程审查能力）+ 模式 4（决策边界 — CC 自主拍板每项归类）

详细 raw：`05_logs/raw/2026-05-27_ios_审查会话.md`

### 2026-05-25 晚段-2 by [MacBook-Pro-Opus 4.7 1M / AC 学习内容清单 v0.1.0 起草（跨 5-27 收尾）] <!-- VERSION_OK -->

**主题**：⭐⭐⭐⭐⭐ itsuki 元认知瞬间「我现在 DMSD 都 5 端开发了，但实际上我一门编程语言都没掌握 ... 我现在连自己项目的文件都认不全」→ 让 CC 读 iCloud `02_分析与调研/AC入試制度総覧_2027.html` 了解 AC 评分 3 点（关心 / 能力 / 表达）+ 时间窗（6/15 R9 募集要项公表 / 9/3 出愿截止 / 11/2 合格）→ CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章（项目熟悉 / 通用基础 / Python / Swift / Kotlin / TypeScript / 硬件 / AC 直接相关 / 推荐顺序）+ project-overview SKILL.md 同步 3 处 → itsuki 看完不满深度主动要求「不仅有 DMSD 内容，还包括各种专业类知识 + 项目底层运转逻辑」→ CC 列 4 章新增大纲（第 9 章项目底层运转 / 第 10 章计算机科学基础（情報科学類 1-2 年级共通课预习）/ 第 11 章信息安全深度 CTF 方向 / 第 12 章软件工程）等 itsuki 拍板 → itsuki 直接说「收尾」→ 4 章扩充未实装到 HTML 变悬挂任务，加 TODO §🛠️ §M 6 条<!-- VERSION_OK -->

**关键拍板**（itsuki 4 次）：元认知声明「5 端但一门语言都没掌握 + 文件认不全」(模式 5 顶级) / 让 CC 先读 AC 制度再设计学习清单（工程顺序 — CC 默认会跳过）/「不是说计划，就把要学的内容列出来」（清单 ≠ 时间表）/ 主动扩充 9 章 → 13 章（推翻 CC 第一版范围）

**实际改动**（已被 5-26 晚段-4 别会话 commit `3d945a7` 顺手带走）：新建 `06_assets/学习内容清单.html` v0.1.0（9 章 / 815 行 / 61KB / 跟 iCloud AC 制度総覧 HTML 同风格配蓝色区分） + project-overview SKILL.md §1.5 + §6.5 + 总计 3 处<!-- VERSION_OK -->

**5-27 深夜收尾产出**：新建 `05_logs/raw/2026-05-25_AC学习清单起草.md`（4 段深度 AC 素材 / 模式 5 顶级 × 2 + 模式 6 + 模式 4） + TODO §🛠️ §M 6 条 + 本 WIP 段 + project-overview §1.5/§6.2 raw 55→56 / 108→109

**AC 价值** ⭐⭐⭐⭐⭐ — 模式 5 二阶元认知（项目跑起来 ≠ 自己掌握）+ 主动引入「情報科学類 1-2 年级共通课预习」高价值 AC 方向 + 主体性顶级（推翻 + 扩充）

详细 raw：`05_logs/raw/2026-05-25_AC学习清单起草.md`

### 2026-05-25 晚段 by [MacBook-Pro-Opus 4.7 1M / anti-ai-flavor HOW_TO_TALK 立项 + 跨 3 项目 session-wrap 同步]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动「这个会话我们来讨论 claude 不说人话的问题」→ 一口气扔 16 个翻车原句证据 → CC 抽出 4 根本问题 + 9 类细分 → 当场 CC 又翻车 4 次 → 5 条总结铁律拍板 → 看别的 AI 复盘材料抽出第 5 根本问题「抽象规则要变具体模板」→ 方案 B 落地（HOW_TO_TALK.md 跟 SKILL.md 反面自检互补）→ hook 升级注入正面 6 问 → DMSD/SC26/Tango 三个项目 session-wrap 收尾清单同步加项 11/8/8「全局环境清单同步」

**关键拍板**（itsuki 11 次）：风格 1 故事化 默认 / 风格 D 直问 简单 yes/no / 5 条总结铁律 / 2 触发词「说人话」+「单词白名单」/ 方案 A 一键重写 + 方案 C 6 类清单搬全局 / 不加方案 B 自动追加自检行 / 不加"每段问懂了吗" / 方案 B 独立文件不独立 skill / hook 加 HOW_TO_TALK 指针 + 6 问 / 应用到全局 = SC26+Tango 同步加 / 加到收尾 skill 不靠 PostToolUse hook

**实际改动**（10+ 文件）：详见 `05_logs/raw/2026-05-25.md` 晚段 §阶段 6 清单

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 顶级 × 5** — CC 当场翻车 4 次 + 写"规则要变模板"时自己又用抽象代号（讨论问题时表演了问题本身 — 自指失败 self-referential failure）
- **模式 6 取舍** — A/B/C 方案对比 itsuki 戳穿 A 让现有 skill 鸡肋 → 改推 B（SOLID 单一职责）
- **模式 7 机制完备性** — 跨 3 项目同步加同样项（一致性原则）
- **方法论级转折** — 「抽象规则」→「具体模板」架构观转变
- **协作教学** — itsuki 扮演"老师改作业"，给精心修改版 vs CC 原版对比驱动方法论提取

**追加：第三轮升级**（同晚段稍后，收尾过程中 itsuki 抛新需求）：
- 起因：itsuki「我需要我的说人话 skill 可以不断迭代更新 — 发现新问题 → CC 记到 skill 文件 + 做分析」
- 拍板 3 决定：触发词 =「**翻车**」单字 / 先扔 `inbox.md`（推荐）/ 5 字段全填（原文 / 6 类归类 / 违反铁律 / 根因 / 修正版）
- 改 5 文件：① 新建 `~/.claude/skills/anti-ai-flavor/inbox.md` ② SKILL.md 加 §7.5「3 个动作触发词」段 ③ CLAUDE.md 触发词 2→3 ④ hook 提醒 2→3 ⑤ `~/.claude/我的环境.md` + `.html` 同步
- 「翻车」单字触发细则：itsuki 单独说「翻车」二字才触发，长句里出现「翻车」当普通词处理
- AC 价值：元层立项（让 skill 能自我迭代，比单纯加规则高一层）+ propose 流程示例（CC 没自作主张设计触发词，用 AskUserQuestion 问 3 决定，候选都用 itsuki 嘴里出过的话）

**残（下次跟进）**：
- SC26 §7.5.5 line 720 旧漂移（5-16 留下来的「6 项」实际 8 项）
- Tango 未来装 §7.5 强制清单段
- CC 自治进化机制 propose（itsuki 提了未拍板）
- 触发词「单词白名单」首次触发后 CC 建 `whitelist.md`
- 触发词「说人话」首次实战测试 — 还没真的用过
- 触发词「翻车」首次实战测试 — 等下次 CC 翻车 itsuki 喊一声看机制能不能跑通
- inbox 累到 3-5 条后写「整理 inbox」SOP（批量合并到案例库的流程）
- DMSD + SC26 + Tango 全部改动未 commit

详细 raw：`05_logs/raw/2026-05-25.md`（晚段 §阶段 1-7 + 7 条 AC 候选段 + 第三轮升级追加段）

> **2026-05-27 收尾砍 5 条**（让 5-26 晚段-4 + 5-26 晚段-3 + 5-26 晚段-2 + 5-26 早段 + 5-25 晚段 维持 5 条上限）：5-25 早段（drift 修 + session-coord 三层保险） / 5-24（iOS bug 批量修复） / 5-22 晚段（点呼机推进 + decision-draft） / 5-22 早段（iOS fork 融合） / 5-19（project-overview 系统化改造） — 详细历史看 commit log + `raw/2026-05-{19,22,22_iOS_fork融合,24,25}.md`<!-- VERSION_OK -->

<!-- 5-25 早段（drift 修 + session-coord 三层保险） by [MacBook-Pro-Opus 4.7 1M] — 砍于 2026-05-27 收尾。详见 raw/2026-05-25.md。
### 2026-05-25 早段 by [MacBook-Pro-Opus 4.7 1M / drift 修 + session-coord 三层保险]

**主题**：⭐⭐⭐⭐ itsuki 启动 → CC 报告 drift hook 3 个目录漂 → itsuki 说「修好」→ CC 调查发现根因是脚本 bug 不是数据漂（`git ls-files` 中文文件名怪行为 + 脚本 `sort -u` vs `sort | uniq -c` 口径打架）→ 修 2 文件 → itsuki 抛新话题「session-coord 启动不主动加载，要全局生效」→ CC 诊断缺 A+B 层保险（对比 ac-radar / cc-comm-rules 已有三层）→ 补 4 个全局文件 → 收尾时被 hook 戳穿 `~/.claude/我的环境.html` 漏同步 → 现场补回

**关键拍板**（itsuki 6 次明确决策）：
- **「修好」drift**（执行式拍板 — CC 自己定怎么修）
- **「顺手修了」git ls-files 重复 path**（itsuki 期待治根，CC 调查后发现不是 git 真重复改主意只修脚本侧）
- **「不管 DMSD 还是别的项目，启动都注册 session-coord」**（全局适用，不做项目专用）
- **「skill description 语义触发不可靠 → 需要 A+B+C 三层」**（机制完备性原则）
- **「html 漏同步要补」**（detective control 硬拦截 — session-wrap §7.5 env-diff 提醒触发）
- **「收尾」**（启动 8 项流程）

**实际改动**（DMSD 2 + 全局 4 = 6 文件 + 1 新 raw）：
| 文件 | 改动 |
|---|---|
| `bin/check_overview_drift.sh` | 删一处 `sort -u` 统一口径修脚本 bug |
| `.claude/skills/project-overview/SKILL.md §0.1` | 时间戳 5-24→5-25 / 总计 1122→1124 / `05_logs/` 102→104 / raw 列表 +5-24+5-25 |
| `~/.claude/hooks/session-start-coord-check.sh` | **新建** — SessionStart hook 检测项目协作板状态 |
| `~/.claude/settings.json` | SessionStart 数组 +1 注册（10s timeout）|
| `~/.claude/CLAUDE.md` | 加 `## session-coord 强制加载` 段（参考 ac-radar / cc-comm-rules 写法）|
| `~/.claude/我的环境.md` + `.html` | hook 表 +1 行 / 末尾 5-25 历史日志条目 / 页脚日期 5-22→5-25 |
| `05_logs/raw/2026-05-25.md` | **新建** raw — 5 候选 AC 素材段 |
| `00_admin/TODO.md` | +2 段（§📊 project-overview 历史欠债 + §🐚 shell 工具链 quirk）|

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**（派生痛点）：CC 改完主动跑脚本验证「✅ 没漂」不假设改完就对
- **模式 2**（假设崩）× 2：CC 假设「git index 真重复」崩（grep -c 验证只 1 份）/ 脚本作者假设「ls-files 不会重复」崩
- **模式 5**（元认知）× 2：CC 没字面执行「修好」直接改数字，主动调查根因 / CC 同会话内自己漏 html 同步被 hook 戳穿（机制证明自己价值）
- **模式 6**（取舍）× 3：修脚本 vs 改数字 vs git rm --cached / A 单层 vs A+B+C 三层 / 项目专用 vs 全局适用
- **模式 7**（机制完备性）⭐：itsuki 类比 ac-radar / cc-comm-rules 三层保险结构诊断 session-coord 缺 A+B 层 — 不是「ad hoc 加 hook」是「按已建立的机制范式补全」
- **协作纠错** × 1：itsuki 隐性期待「顺手修 git 状态」CC 调查后改主意只修脚本（announce + 给打断窗口）
- **主体性 6/6**：6 次明确拍板都给理由
- **学术延伸性**：「root cause vs symptom」/「Unicode 规范化 NFC/NFD」/「shell 工具链跨平台 quirk」/「机制完备性原则」/「detective control 比 preventive control 更可靠」— AC 面试可挂「跟 AI 协作的工具链设计」

**残（下次跟进）**：
- 本会话全部改动 + 昨晚 5-24 遗留改动**未 commit** — 等 itsuki 拍板 commit 顺序（建议 3 个 commit：5-24 iOS bug 修 / 5-25 drift 修 / 5-25 全局 session-coord 三层保险 ~/.claude/ 不在 DMSD git）
- §6.2 raw 章节标题「48 文件」历史漂（已记 TODO §📊）
- 全局 `~/.claude/` 改动不在 git 仓库 — itsuki 之前提过「~/.claude/ 做成 git 仓库」永久 propose 还没拍板

详细 raw：`05_logs/raw/2026-05-25.md`

### 2026-05-24 by [MacBook-Pro-Opus 4.7 1M / iOS bug 批量修复 — 补登 5-25]

**主题**：⭐⭐⭐⭐ itsuki 启动「修复 iOS 代码问题」→ working tree 既有 6 条 iOS bug 修复 + 新修 3 条（A-035 RegisterStep5 万能密码后门删 / FC-020 ApplicationOut 补 bus_route_id / FC-021 room_no 长度 iOS 16 vs backend 8）= 9 条 iOS bug 落地。**会话当晚未跑收尾** — 5 改 + 1 新建 raw 全挂 working tree 未 commit，本次 5-25 收尾补登条目。

**关键拍板**（itsuki 5 次）：
- **「不用我决定的，全部都修好」** — 协作授权颗粒度拍板（CC 工程层 + memory 规则托底的事不要甩回 itsuki 决定）
- **「他妈的，到底是什么东西啊？」** — 沟通失职诊断（CC 报错术语裸露）
- **「不要再停下来」** — 工作节奏拍板（执行模式 vs 讨论模式）
- xcodebuild destination 误报 exit 0 → CC 自查发现 iOS 26.5 模拟器未装 → 报告 itsuki + 切 destination
- SourceKit 10 个 diagnostic 是误报 → 信任 xcodebuild 真编译结果

**AC 价值** ⭐⭐⭐⭐：
- **模式 5** × 3：协作边界 / SourceKit vs xcodebuild 信任源 / 沟通失职反讽（CC 帮 itsuki 修代码 bug 同时自己报错术语裸露）
- **模式 1**：A-035 magic value 后门删 — 派生痛点（demo scaffold 留到生产 = 安全漏洞）
- **模式 2** × 2：room_no 长度跨端不一致 / xcodebuild destination 配置假设崩
- **主体性 5/5**：每次拍板都给具体边界

**残**：commit 留给 5-25 一起处理（详见 5-25 条目 §残）

详细 raw：`05_logs/raw/2026-05-24.md`

### 2026-05-22（晚段 20:30-21:30+）by [MacBook-Pro-Opus 4.7 1M / 1779447985-17762-点呼机推进 + decision-draft]

**主题**：⭐⭐⭐⭐⭐ 会话以「点呼机推进」为主题启动 → itsuki 抛 5-12~16 中国海关查扣事件（项目内 raw + decision_log 全 0 命中 — 之前未留痕）→ itsuki 拍板撤回中国海运渠道改日本本地买（理由：避免再查扣 + 本地买配件坏了维护方便）+ 同步立项 `session-wrap §5.5.15 decision-draft` 收尾子节（itsuki 反问「我不是有 ac-radar 了吗」+ 拍板「直接放收尾流程里作子节，不做独立 SKILL.md」）+ CC 失职 2 次（提议写 decision_log 但没主动提更新 `我的环境.html` / 闭门造车设计触发词 itsuki 戳穿「我一个都不会说」）

**关键拍板**（itsuki 7 次明确决策）：
- **撤回中国海运 → 日本本地买**（双理由：避免查扣 + 长期维护）
- **decision_log 专门做一 skill — 多方位收集素材**（CC 提议「删」被反向升级）
- **A 窄做**（决策日志写入助手 — 起草草稿不直写正文）
- **「我不是有 ac-radar 了吗」**（戳穿 CC 重复造轮子）
- **「直接放收尾流程里作子节，不做独立 SKILL.md」**（架构重定）
- **「我一个都不会说」**（戳穿 CC 闭门造车设计触发词）
- **「如果我不说你会写吗？」**（戳穿 CC 漏更新 `我的环境.html` 全局规则）

**实际改动**（8 文件）：
| 文件 | 改动 |
|---|---|
| `05_logs/raw/2026-05-22.md` | 新建 — 深度抓海关事件 + 方向反转 + 模式 1+2+6 三维度拆解 + 主体性 5/5 评分 |
| iCloud `06_radar_inbox/ac_scratchpad_2026-05-22.md` | AC 雷达短标签写入（跨项目可见）|
| `00_admin/TODO.md` | §🛰️ 点呼机段：原 11 件淘宝清单 + 2 任务作废 / 加 6 条新待办（重新选型 + 渠道调研 + 预算重估 + 硬件文档更新 + 点呼机设计文档更新 + 拆寄教训）|
| `.claude/skills/session-wrap/SKILL.md` | 加 §5.5.15 decision-draft 子节（识别 6 类重大决策 / 草稿格式 / CC 永不直写铁律 / 跟 ac-radar + §5.5.1 AC dump 分工 / 含 5-22 海关事件实测例子）+ §5.5 标题「8 节→16 节」|
| `~/.claude/我的环境.md` | 顶部时间戳 + DMSD Skills 表 session-wrap 行 + 末尾历史日志 5-22 条目 |
| `~/.claude/我的环境.html` | 同上 3 处 + 页脚日期 |
| `02_design/hardware_design.md` | 顶部时间戳 + §0 状态表 §5 行 + §5 整段重写（5.1 标 ❌ + 加 5.1' 新方向 + 5.2「假设崩」表）|
| `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md §1.2` | 加 5-22 banner + 原配件标 🔴 撤回 + 加日本重新选型行 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**（派生痛点 → 工程解法）：省运费 → 单点故障 → 一两件触发查扣 → 全部连带损失 → 反向推「拆寄 + 本地买」方案
- **模式 2**（假设崩）× 2：4-20 写「ST25DV16K 通用电子元件无出口限制」5-22 真值翻车 / CC 提议「写 decision_log 草稿」被 itsuki 反向升级
- **模式 5**（元认知）× 3：CC 失职 2 次主动承认 / itsuki 推翻 CC「删」改「升级成能力模块」/ CC 闭门造车设计触发词 itsuki 戳穿
- **模式 6**（取舍）× 多：长期维护视角 vs 单次成本 / 决策日志做独立 SKILL vs 收尾子节 / 触发词靠 itsuki 喊 vs 收尾自动扫
- **协作纠错** × 3：itsuki 戳穿 CC 重复造轮子 / CC 闭门造车 / CC 漏更新清单
- **主体性 5/5**：7 次明确拍板，3 次戳穿 CC，1 次主动标记 AC 素材
- **学术延伸性**：供应链风险管理 / 单点故障设计 / 鸡蛋别放一个篮子（diversification 原则） — AC 面试挂「系统设计的风险分散」

**残（下次跟进）**：
- 日本本地硬件重新选型 — 6 类 × 6 渠道（Amazon.jp / 秋月電子 / スイッチサイエンス / 千石電商 / Yahoo Auction / メルカリ）→ 下次会话开始
- 点呼机 `ROLLCALL_DEVICE_DESIGN_LOG.md §10` D1-D6 待 itsuki 拍板（不依赖硬件实物，可并行）
- 点呼机 mock 写代码 — 不依赖 Pi 实物
- 后端 ECDSA 验签实装 — 切别会话推进
- 本次 decision-draft 子节首次产出的「5-22 海关方向反转」草稿在 SKILL.md §5.5.15 例段，等 itsuki 粘到 `05_logs/decision_log.md` 顶部
- 多个 project-overview 描述准确性 hook 提醒挂起（8 文件改动产生），收尾时统一过 §0.1 体量表 + 对应章节描述

详细 raw：`05_logs/raw/2026-05-22.md`

### 2026-05-22 by [MacBook-Pro-Opus 4.7 / 1779447279-2548-iOS fork 融合]

**主题**：⭐⭐⭐⭐⭐ itsuki 拍板「不冲刺上架先把 v1.0 做完再上架」→ 5-08 上架冲刺的 fork（`~/dev/Tomoshibi-AppStore/`）归档进 `99_archive/2026-05-22_tomoshibi_appstore_fork/` + backport 5 个 iOS 文件到主项目 + xcodebuild 编译验证戳穿「Bot 1 闯祸 30+ 编译错误」是 SourceKit 单文件索引误报 + commit `46f779c` 落地 + 2 次沟通规则触发（「看不懂」+「他妈的不要再停下来」）

**关键拍板**（itsuki 5 次明确决策）：
- **不冲刺上架** — 路线撤回，先做完 v1.0 全功能再启动上架
- **A'**（fork 归档 + 反向 patch 修正版）— 不是「全抄 fork」也不是「保留主项目」，而是逐文件归类
- **原目录归档** — 不只搬到 archive，原 `~/dev/Tomoshibi-AppStore/` 也删
- **commit 起草后落地** — 用 CC 起草的 message
- **「除非又重大决策 否则他妈的不要再停下来了」** — 校准 CC 工作节奏（执行模式 vs 讨论模式）

**实际改动**：5 个 iOS 文件 + 1 个 DESIGN_LOG + 新增 1.7 MB 归档目录。详细对照表见 raw。

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5** × 3：路线撤回 / xcodebuild 戳穿误报真相 / 沟通规则实战
- **模式 2** × 2：itsuki 假设「fork 更新」崩 + CC 假设「全抄 fork」崩 → diff 工具识破
- **模式 6** × 2：A/B/C 取舍 + 9 个文件归类（备份赢 / 主项目赢 / 部分各赢）
- **模式 4**：session-coord v0.1.0（5-11）→ 5-22 第 2 次实战发现协议层限制 <!-- VERSION_OK -->
- **主体性 5/5**：5 次明确拍板，含 1 次路线撤回 + 1 次 CC 节奏校准
- **学术延伸性**：iOS 工程认知（SourceKit vs xcodebuild）+ App Store 审核条款（5.1.1(v)）+ fork 分裂工程反模式

**残（下次跟进）**：
- commit `46f779c` 未 push（按全局铁律等 itsuki 明示）
- project-overview SKILL.md 3 个 Foundation 文件未列（独立任务）
- 「Bot 1 还可能误删了别的功能」需要复查 — 本次只确认了 MyPage 账号删除被误删
- system_features.md 「v1.0 上线前必删 demo scaffold 清单」是否要加密码框 `#if DEMO` 条目

详细 raw：`05_logs/raw/2026-05-22_iOS_fork融合.md`

### 2026-05-19 by [新Mac-Opus 4.7 1M-project-overview 系统化改造]

**主题**：⭐⭐⭐⭐⭐ project-overview 文件介绍大改造（itsuki 拍板「一眼看明白」/ 27 段表全改）+ 9 处文件数漂移对账修复 + 防漂 C 方案落地（hook 全覆盖 + 启动对账脚本双层保险）+ 元层翻车 itsuki「我看不懂了」沟通问题 hook 触发

**关键拍板**（itsuki 5 次明确决策）：
- **B 边读边改**（跳过 CC propose 仪式，直接全改）
- **全部修**（5 大 + 4 小 = 9 处漂移）
- **C 方案 + hook 覆盖整个项目**（不是扩白名单 — 是全 DMSD 覆盖）
- **加 CLAUDE.md**（提一句新机制让新会话知道）
- **简单介绍**（不要再介绍得我看不懂了 — 沟通问题 hook 触发）

**实际改动**：
| 文件 | 改动 |
|---|---|
| `.claude/skills/project-overview/SKILL.md` | 909→949 行 / 27 段表全部加「一句话作用」列 / 9 处漂移修 / 加 §3.6.5 alembic + §4.3 重写 |
| `00_admin/hooks/post-edit-project-overview-check.sh` | 重写全覆盖版（删白名单逻辑）|
| `bin/check_overview_drift.sh` | 新建启动对账脚本（注册 SessionStart）|
| `.claude/settings.json` | 加 SessionStart hook 注册 |
| `00_admin/hooks/README.md` | 加 §I SessionStart 段 + §F v2 说明 |
| `CLAUDE.md` | hooks 工具列表加 2 行新机制（粗体标 5-19）|

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**（派生痛点）× 2：改造完主动对账 / 修完主动诊断「为啥漂」
- **模式 2**（假设崩）× 2：CC 以为 hook 白名单够 / 以为「文件名在 = OK」
- **模式 5**（元认知）× 3：诊断时引用 §7.5.4 反讽自己 / 自指验证机制 / 黑话翻车
- **模式 6**（取舍）× 2：itsuki 选「覆盖整个项目」比 CC 提议的「扩白名单」更激进 / 选 C 不选单层
- **主体性 5/5**：5 次明确拍板
- **学术延伸性**：软件工程「白名单 vs 全覆盖」/ 机制设计反模式（依赖自觉）/ 错误处理哲学（升级到机制层）— AC 面试可挂

**残（下次跟进）**：
- 对账脚本 bug — `.claude/` 写 9 实际 9，但脚本说「写 23 / 实际 9」（awk 取到了 §1.8.1 的 23 而非 §0.1 的 9）→ 记 TODO 修脚本
- bin/ 数 3 vs 2 — 因为 `check_overview_drift.sh` 未 commit（commit 后会对上）
- §10 AC top 10 第 10 项「版本管理SOP」路径已迁但表没改
- §11 itsuki 待决定列表 8 条状态复核
- 本会话所有改动未 commit — 等 itsuki 拍板

详细 raw：`05_logs/raw/2026-05-19.md`
-->

> **2026-05-25 收尾砍 2 条**（让 5-25 drift+session-coord + 5-24 iOS bug 补登 + 5-22 晚 点呼机+decision-draft + 5-22 早 iOS fork + 5-19 project-overview 改造 维持 5 条上限）：
> - 砍 5-16 跨项目优化（codex 审 + cc-project-template 通用化 + bash 3.2 heredoc bug 修）— 详见 `raw/2026-05-16.md`
> - 砍 5-14 晚段-2 anti-ai-flavor 立项 + cc-comm-rules v0.6.0 撤回 — 详见 `raw/2026-05-14.md` §K<!-- VERSION_OK -->

> **2026-05-22 晚收尾砍 5-14 中午 graphify 复盘 + 5-14 晚段 Tango 立项 2 条**（让 5-22 晚 点呼机推进+decision-draft + 5-22 早 iOS fork 融合 + 5-19 project-overview 改造 + 5-16 跨项目优化 + 5-14 晚段-2 anti-ai-flavor 维持 5 条上限）— 详细历史看 commit log + `raw/2026-05-14.md` + `raw/2026-05-14_Tango立项+bootstrap.md` <!-- VERSION_OK -->

> **2026-05-19 收尾砍 5-14 早段沟通规则 v0.5.0 段** — 详细历史看 commit log + `raw/2026-05-14.md` <!-- VERSION_OK -->

> **2026-05-16 下午砍 5-13 接力 audit 段**（让 5-16 跨项目优化 + 5-14 晚段-2 anti-ai-flavor + 5-14 中午 graphify + 5-14 晚段 Tango 立项 + 5-14 早段 沟通规则 v0.5.0 维持 5 条上限）— 详细历史看 commit log + `raw/2026-05-13_接力CC续做.md` <!-- VERSION_OK -->

> **2026-05-16 上午砍 5 条**（让 5-13 接力 audit + 5-14 早段沟通规则 v0.5.0 + 5-14 中午 graphify 复盘 + 5-14 晚段 Tango 立项 + 5-14 晚段-2 anti-ai-flavor 立项 维持 5 条上限）：砍 5-12 修补批量+规则加严 / 5-11 跨 23 点 CC2 reviewer 后门修复上线 / 5-11 更晚 graphify / 5-11 晚 session-coord / 5-11 术语表 — 详细历史看 commit log + raw <!-- VERSION_OK -->

> **2026-05-12 砍 5-10 晚 skills 批量装条目**（让 5-12 修补批量+规则加严 + 5-11 跨 23 点 reviewer 后门修复上线 + 5-11 更晚 graphify + 5-11 晚 session-coord + 5-11 术语表 维持 5 条上限） — 详见 `raw/2026-05-10_skills批量装.md`

> **2026-05-11 跨 23 点砍 2 条**（让 CC-2 reviewer 后门修复上线 + graphify + session-coord + 术语表 + 5-10 晚 skills 批量装 维持 5 条上限）：
> - 砍 5-10 ac-radar 上线条目 — 详见 `raw/2026-05-10.md`
> - 砍 5-08 凌晨 reviewer_demo 重做条目 — 详见 `raw/2026-05-08_reviewer_demo重做.md`（本次 CC-2 会话 §F.7 已 reference 它作为主线前提）
>
> 早些砍除：**2026-05-04 深夜砍 5 条** + **5-06 砍 5-03 晚** + **5-08 砍 5-04 上午** + **5-08 凌晨砍 5-04 主体/晚/深夜 3 条** + **5-10 砍 5-04 晚 iOS bug** + **5-10 晚砍 5-06 独立 repo 退役** + **5-11 砍 5-08 点呼机** + **5-11 晚砍 5-07→5-08 iOS 上架冲刺跨日** — 详细历史看 `git log` + `05_logs/raw/2026-05-0{2,3,4,6,7,8}.md`

---

## 🤝 多会话占用（避免冲突）

*当前无并行会话占用任何文件。*

> 如启动多会话并行：在此列出谁正在改哪些文件 + 开始时间，其他会话避让。改完登记完成移走。

---

## 🚧 阻塞项

*当前无阻塞项。*

> 阻塞项 = 等 itsuki 答复才能推进的硬卡点（如 Q1/Q2 字段对齐拍板）。无阻塞时本节为空。

---

## 🔒 多会话协调规则

### 会话标识（建议命名）

`[设备-主题]` 格式：`[Mac-主会话]` / `[Mac-mini-Opus 4.7]` / `[Mac-后端]` / `[Mac-iOS]` / `[Mac-Android]` / `[Mac-Web]` / `[Code-Agent]`。

### 避免冲突的硬规则

1. 每个「占用」任务必须标出涉及文件 / 目录
2. 其他会话不能动正在被占用的文件
3. **共享文件**（`CLAUDE.md` / `WIP.md` / `progress_overview.md` / `CHANGELOG.md` / `TODO.md`）：一次只能一个会话改，改完立刻 commit + push
4. 改 `WIP.md` 本身：先 pull，改完立刻 push
5. git conflict：停下来问 itsuki，不自己猜合并

### 关键文件边界

| 目录 | 归谁管 |
|------|-------|
| `03_dev/backend/` | 后端会话 |
| `03_dev/student_ios/` | iOS 会话 |
| `03_dev/teacher_web/` | Web 会话 |
| `03_dev/rollcall_device/` | 点呼机会话（Pi）|
| `01_specs/` | 一次只允许一个会话改（规格冻结区）|
| `00_admin/` | 主会话管理 |
| `05_logs/raw/` | 各会话写自己今天的，文件名不撞 |

---

## 📝 给新会话的上下文（关键信息）

读完 `CLAUDE.md` + 本文件 + `TODO.md` 顶部应该知道：

1. **当前版本**：见上方 + `CHANGELOG.md` 顶部
2. **上线姿态**（4-19 G2 决策）：取消分阶段；v1.0 直接 iOS + Android + 卡 一次上线
3. **防作弊核心**：动态 NFC 贴纸 ST25DV16K（10 秒 nonce）+ ECDSA 签名 + 老师监督 + 语音播报（原创设计 → `05_logs/decision_log.md`）
4. **版本体系**：0.x.x = 开发中，1.0.0 = 宿舍正式上线
5. **记录体系**：CC 侧 `00_admin/CLAUDE_CODE_记录指南.md`；总章 `AC入试记录指南_v3.md` 在 iCloud（CC 不读）
6. **文件地图**：`CLAUDE.md §目录结构` + `.claude/skills/project-overview/SKILL.md`（5-04 起替代已归档的 `00_admin/文件结构指南.md`）
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策他拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04 上午** — 加 2026-05-04 会话条目（A+B 文件联动工具建设）
- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- **2026-05-10** — 加 ac-radar 上线条目（共 6 条超 5 条上限）→ 砍 5-04 晚 iOS bug 修复条目（详见 raw/2026-05-04_iOS_bug修复.md）
- 更早历史 — 见 `git log -- 00_admin/WIP.md`
