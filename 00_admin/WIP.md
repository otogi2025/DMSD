# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-14 晚段（**Tango 项目立项** + grill-me 12 题完整设计讨论 + cc-project-template 治理框架首次实战 + 跨项目 bootstrap — 详见 `raw/2026-05-14_Tango立项+bootstrap.md`）。同日早段: 沟通规则 v0.5.0 根本方向再调整 + 4 次连续元层翻车 + hook 推全局（详见 `raw/2026-05-14.md`）。再早: 2026-05-13（v0.4.0 + v0.4.1 + §7.5 自查清单 + TODO §🛠️ E + F）/ 2026-05-12（修补类批量 + cc-comm-rules 加严 + destructive bash hook block→warn）<!-- VERSION_OK -->

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
> - **会话开始**: CC 读本文件全文 + `TODO.md` 顶部 200 行 + `git status`
> - **会话结束**: CC 更新「最近会话」+「多会话占用」；新增的 backlog **写到 TODO.md** 不写这里

---

**当前版本**: v0.8.0 <!-- VERSION_OK -->
**版本 bump 流程**: `.claude/skills/version-bump/SKILL.md`（itsuki 说「迭代/bump/发版本/打 tag」自动触发；CC 有否决权 — 即使 itsuki 说要 bump 但 §2 决策树不命中可以拒绝）

---

## 🎯 当前焦点

> **⭐⭐⭐ 沟通规则 cc-comm-rules v0.5.0 根本方向再调整（5-14 拍板）** — 新会话必读 → `05_logs/raw/2026-05-14.md` <!-- VERSION_OK -->
> v0.1-v0.4「约束 CC 输出」思路全部作废。新方向：CC 用英语词自由 + **收尾时全量加到 `06_assets/术语表.html`**（itsuki 当 AC 面试日语学习材料）。<!-- VERSION_OK -->
> **删的**：`pre-write-memory-block.sh` hook（itsuki 原话「我从来没有说过要拦截持久记忆」）。
> **新的**：`pre-bash-destructive-block.sh` 推全局 `~/.claude/hooks/`（原 DMSD 项目级保留）— 8 个原 pattern 不变，warn 模式不变，覆盖范围扩到所有项目。
> **备份**：5-14 改的 3 处旧版存 `~/.claude/_archive_2026-05-14/`（含 README 回滚命令）。
> **未来 propose**：把 `~/.claude/` 做成 git 仓库（永久解决全局配置无历史问题）— 等 itsuki 拍板。

> **⏰ Cloud Design 5-12 额度已过期** — 5-14 检查时已浪费。下次额度重置时间未知。

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 三端代码层启动完毕，下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

### 2026-05-14（晚段）by [新Mac-Opus 4.7 1M-Tango立项+bootstrap]

**主题**：⭐⭐⭐⭐⭐ itsuki 提"做记单词网站" → grill-me 12 题完整设计讨论 → cc-project-template 治理框架首次实战 → 跨项目 bootstrap 起 Tango 项目骨架（`~/dev/tango/`）→ stop 等推进

**关键拍板**：Tango = DMSD 派生 AC 项目（"为自己解决英语单词记不住痛点"，跟 DMSD"为他人"双叙事维度并列）/ MVP 先 Web → App 后续 → 上 App Store + 推广（itsuki 推翻 CC 4 次后修正路线）/ 算法 B 路径（SM-2 改造 → 机器学习版 → 神经网络）3 层切分 L1/L2/L3 / 技术栈跟 DMSD 后端同（FastAPI + Jinja2 + SQLite）+ 移动端优先 + 域名暂共享 DMSD 后续独立买

**Tango bootstrap 完成**：cp `cc-project-template` → 替换 5 占位符（13 文件）→ Tango 专属 CLAUDE.md（参考 DMSD）→ 项目宪章 v0.0.0（含 12 题讨论结果 + 15 task）→ git init + 2 commit (`addbfde` + `0467ed6`) → hook 装好 + pre-commit 2 次拦截后修复成功（验证治理跨项目复用）→ TODO 加 9 条 G1-G9 治理 TODO（边开发边清 6 skill 共 197 处 DMSD 残留）<!-- VERSION_OK -->

**itsuki 推翻 CC 4 次**（主体性 5/5）：(1) 时间盒选升级版（不接受极简 MVP）/ (2) 手机用户没 Tab 键（戳穿 CC 桌面端思维）/ (3) vibe coding 不能按手工搓估时（CC 估时根本错）/ (4) 域名独立项目独立买（不绑 DMSD 永久）

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**：派生痛点识别 → 工程解法
- **模式 4** × 2：DMSD（v1 核心）→ Tango（v2 派生）双叙事 / cc-project-template 治理 v1.0 → 5-14 首次实战 <!-- VERSION_OK -->
- **模式 5** × 多：4 次推翻 + 6 次 CC 主动诊断 unknown unknowns（闭门造车反向证据 / App Store 撞车预警 / 分隔符陷阱 / vibe coding 边界 / DMSD 残留治理策略 / 跨项目脏改反模式）+ cc-comm-rules v0.5.0 实战触发 1 次（master vs main "不理解" hook 拦下） <!-- VERSION_OK -->
- **模式 6** × 多：12 题每题取舍 + 算法 3 层切分 + MVP 范围日语推后等
- **学术延伸性**：认知科学（Ebbinghaus 遗忘曲线）→ 间隔重复算法（SM-2）→ 机器学习（FSRS）→ 神经网络 → 个人记忆模型 — 完整学习路径跟情報学群直接挂钩

**残（下次跟进）**：
- Tango GitHub repo `otogi2025/tango` 未建 / 未 push（commit `addbfde` + `0467ed6` 等 itsuki 拍板 push）
- Tango 切新会话开始 Phase 1（读 Ebbinghaus + Wozniak 论文 + 笔记 → MVP 实装）
- 6 个 Tango skill 共 197 处 DMSD 残留 → G1-G9 治理 TODO 边开发边清
- 术语表归档 Tango 新词（grill-me / vibe coding / SM-2 / FSRS / Ebbinghaus / Wozniak / Anki / Quizlet 等大批领域词）推到 Tango Phase 1 实装时按对应类目入（不挤 ⑰ 协作类）

详细 raw：`05_logs/raw/2026-05-14_Tango立项+bootstrap.md`

### 2026-05-14（早段）by [新Mac-Opus 4.7 1M-沟通规则 v0.5.0 + hook 推全局] <!-- VERSION_OK -->

**主题**：⭐⭐⭐⭐⭐ 沟通规则 v0.5.0 根本方向再调整 — 5 次迭代后换思路（约束 CC 输出 → 系统化归档术语表）+ 4 次连续元层翻车 + 状态快照 14 天后刷新 + destructive bash hook 推全局 <!-- VERSION_OK -->

- **起因**：itsuki 启动问"状态快照是什么" → CC 解释完顺势报告 5-13 残留时又蹦英语单词（sub agent / classifier / audit / git mv / HTML / draft 等）→ itsuki 怒怼"我记得有 skill + hook 就是为了拦你"
- ⭐⭐⭐⭐⭐ **沟通规则 v0.5.0 根本方向反转**：v0.1-v0.4 都是"约束 CC 当下输出"（执行率低 / CC 漂 / itsuki 还看不懂）→ itsuki 跳出循环拍板换思路 — **不约束 CC 当下，系统化归档到术语表当 AC 学习材料**。同步删 `pre-write-memory-block.sh` hook（itsuki 原话「没说过要拦截持久记忆」）<!-- VERSION_OK -->
- ⭐⭐⭐⭐⭐ **4 次连续元层翻车**：
  1. 蹦英语单词（v0.4.1 拍板第二天就漂）<!-- VERSION_OK -->
  2. 把工作甩回 itsuki（"你审 + 搬段 + 改日期"被怒怼"你他妈自己做"）
  3. propose A/B/C 复杂术语（"Bash pattern" / "PreToolUse" / "Write 工具" / "old_string"）让 itsuki 拍板 — 被怒怼"我他妈 ABC 三个都没看懂"
  4. 矫枉过正用甲乙丙 — 违反 DMSD memory `feedback_use_english_letters.md`「只用 A/B/C，禁用甲乙丙」 — 被怒怼"我不是听不懂 ABC 三个字母"
- ⭐⭐⭐⭐⭐ **毁灭性动作自检 + 备份**：CC 跑了 `rm 单文件` + Write 全文重写 + Edit 改全局 settings.json — 都不在 destructive bash hook 拦截范围（hook 只拦 Bash `rm -rf` 等 8 pattern，不拦 Write/Edit 工具）。`~/.claude/` 不在 git 仓库 → 不可 revert。itsuki 拍板 A：备份 3 处旧版到 `~/.claude/_archive_2026-05-14/`
- ⭐⭐⭐⭐⭐ **hook 推全局**：itsuki 拍板"最简方案" — 把 DMSD 项目级 `pre-bash-destructive-block.sh` `cp` 到 `~/.claude/hooks/` + 注册到全局 settings.json。8 个原 pattern 不变，warn 模式不变，覆盖范围扩到所有项目。CC 之前 propose 的 A/B/C 全部"加新东西"被推翻
- ⭐⭐⭐⭐⭐ **状态快照 14 天后刷新**：4-30 → 5-14。CC 直接写 iCloud（按 itsuki 拍板"你直接添加 + 跟我写的区分开"），用 🤖 emoji 标记 CC 起草段。当前焦点段 5 行 + 最近重大变化段 6 个新日期段

**新规则上线**：
- 沟通规则 `cc-comm-rules` v0.5.0（`~/.claude/skills/`）— 规则 2.3 根本反转 + 规则 3.2 删 hook 配套改软规则 + 规则 5 删翻译自检 <!-- VERSION_OK -->
- 全局 `pre-bash-destructive-block.sh` hook + 注册（`~/.claude/`）
- 全局归档目录 `~/.claude/_archive_2026-05-14/`（含 4 文件 + README）
- 术语表 ⑰ CC / 工作流协作分类（23 个新词条 — 16 主轮 + 7 收尾补漏）
- 状态快照「最后更新」铁律：CC 改完同时更新顶部日期 + 用 🤖 标记 CC 起草段

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 元规则演化**：沟通规则 v0.1 → v0.5 五次迭代（4 天）— "约束输出 → 系统化归档" 的思维进化（不打补丁换思路）<!-- VERSION_OK -->
- **模式 5 元层翻车** × 4：(1) 蹦英语词 (2) 甩工作 (3) 抽象术语 (4) 矫枉过正违反 memory
- **模式 6 取舍** × 4：约束 vs 归档 / 拦死 vs 提醒 / 备份 vs 接受 vs git init / itsuki 改 vs CC 直接写
- **模式 2 假设崩** × 2：hook 该拦今天的 `rm` / 改字母系统能解决"没看懂"
- **主体性 5/5**：itsuki 5 次主动拍板（v0.5.0 / 不准甩工作 / A 备份 / hook 推全局 / 不用甲乙丙）<!-- VERSION_OK -->
- **学术延伸性**：「约束输出 → 归档」= 系统设计哲学（拒绝越来越复杂的约束机制，改用归档让用户事后查）— AC 面试可挂"工程学方法论 / 软件设计原则"

**残（下次跟进）**：
- itsuki 未来要不要做 `~/.claude/` git init（永久解决全局配置无历史问题）
- 3 个怒怼根源仍未拦：`rm 单文件` / Write 重写 / Edit 改全局配置 — 当前 hook 推全局也不拦，等未来 itsuki 主动加 pattern
- 本会话所有改动 commit（DMSD 仅 `06_assets/术语表.html` 1 文件 modified；全局改动在 `~/.claude/` 不入 git；iCloud 状态快照不入 git）
- 状态快照里 🤖 起草段 itsuki 后续可挑选重要的搬进正文 / 改写

### 2026-05-13 by [新Mac-Opus 4.7 1M-接力CC-深度审查整理]

**主题**：⭐⭐⭐⭐⭐ 5-12 凌晨深度审查接力 + 5-13 早 itsuki 怒怼后真整理 + project-overview 同步 hook 上线

5-13 早 itsuki 醒来怒怼"没真整理 / project-overview 漂移 / 我看不到的地方也乱" → CC 当下立刻干 → **7 个 commit 累计**：

- `859693e` 9 文件死链 + NOT_YET_ALLOWED 致命缺口修
- `b37d065` 12 AC 文件 git mv → `05_logs/AC_叙事/`（Q3 拍板）
- `81842f4` 14 文件 git mv（6 管理 + 6 归档 + 2 iOS 改名 `_archived_`）
- `eaeeefe` 新 hook `post-edit-project-overview-check.sh` + project-overview SKILL.md 10+ 处校准 + §1.8 非编号目录新章节
- `6f9650e` HTML 总结加 5-13 中午段
- `(待 commit)` project-overview audit 校准 6 处（§3.4 backend routers 5→11 / §3.6 tests 3→5 / §3.7 P0 删 rollcall+study 已建 / §1.6 sync-rules 18→21 + PostToolUse 5→6 / 末尾时间戳）

**新 hook 上线**：`00_admin/hooks/post-edit-project-overview-check.sh` — CC 改结构相关文件后自动 grep project-overview 看是否同步 → 3 级提醒。**防再漂移**。

**4 sub agent 起草 draft 在 `/tmp/`**：decision_log 29 条 / learning_path 15 条 / project_evolution 5 转折 / system_features §8 补丁 — itsuki 红线 等粘贴。

**sub agent af04d326 audit 报告**：18 条 Edit 建议 — 本 session 做了 6 条，剩 12 条留下次 CC。完整 `/tmp/project_overview_audit.md`。

**AC 价值** ⭐⭐⭐⭐⭐：
- 模式 5：itsuki 怒怼"我看不到"驱动 hook 上线 — passive 提醒永远跟 active 同步（"机制 > 自律"原则验证）
- 模式 6：sub agent audit 发现 SKILL.md 自己漂移（讽刺地漏列刚加的 hook）— 元层面 self-reference 漂移
- 工程纪律：怒怼后立刻 stop + 不绕 classifier + 用 `!` prefix 让 itsuki 自己跑

**残（下次 CC 跟进）**：
- 全 read 600+ 文件审 project-overview 描述准不准 — 单会话 3M tokens 不够（要 6-11 sub agent 分批）
- project-overview 18 条 audit 剩 12 条（§0.1 体量重算 / §4.3 teacher_web v1 整段重写 / §5.5 iOS Feature 8 行数字 / §6.2 raw 36→41 / §7 99_archive 漏 7+ 子目录等）
- 2 SKILL.md classifier 拦（file-linkage 17→18 / memory-write itsuki path）— itsuki 自己 sed
- 4 sub agent draft 粘贴

**详细 raw**: `05_logs/raw/2026-05-13_接力CC续做.md`

### 2026-05-12 by [新Mac-Opus 4.7 1M-修补批量+规则加严]

**主题**：⭐⭐⭐⭐ itsuki 让 CC 把修补类任务全跑（周额度刷新前消耗 token）→ 12 任务并行 + 5 agent → 真改 4 文件 + 9 份报告 → **沟通规则翻车 → itsuki 二次怒怼 → cc-comm-rules 规则 2.3 当下加严 + 加规则 6**

- **起因**：周额度刷新前 itsuki 让列「消耗 token 不需决策可做完」任务 → CC 列 14 项 6 组 → itsuki 选「修补类全做」
- **12 任务并行**：5 agent（spec-sync / file-linkage / graphify / CC 自治简报 / HTML skill 调研）+ 主线 7（环境清单 HTML + project-overview SKILL + memory 体检 + commit 0c71d6b 审查 + AC inbox 盘点 + pandoc blocked + 5-11 raw AC 检查）
- **真改 4 文件**：`~/.claude/我的环境.html` + `.md`（日期 + 5-12 历史段）/ `project-overview/SKILL.md` §6.2 raw 清单 16→36 文件 / destructive bash hook + README
- **destructive bash hook 改造（block→warn）**：itsuki 拍板「太严，提醒 CC 思考一下，别拦死」→ `exit 2` 改成 `exit 0` + JSON additionalContext / dry-run 测通过 / 文件名保留避免多处联动 / `00_admin/hooks/README.md §F` 同步
- **沟通规则翻车 + 二次怒怼**：CC 跑报告时大量英文术语没翻（`exit 0` / `stderr` / `dry-run` / `Pydantic schema` / `god nodes` 等）→ itsuki 怒怼"我没看到任何效果" → CC 承认 + 提"下回合开始改" → **itsuki 二次怒怼"不用说首次出现，每次都要"** → CC 当下改 `~/.claude/skills/cc-comm-rules/SKILL.md` §2.3
- **加规则 6**：itsuki 拍板"我一次输入多任务时 CC 要先总结让我确认" → CC 加规则 6 + 自己应用一次（总结这条要求）+ bump 到 v0.3.0 <!-- VERSION_OK -->

**新规则上线**：
- `cc-comm-rules` v0.3.0 — 规则 2.3 加严（每次出现都翻译，不是首次）+ 加规则 6（多任务输入先总结） <!-- VERSION_OK -->
- `pre-bash-destructive-block.sh` warn 模式（block→warn 改造）

**AC 价值** ⭐⭐⭐⭐⭐ — 模式 5 元规则验证 × 3（itsuki 验证 5-11 规则真做到没 / CC 一次怒怼后又踩 memory 反模式 / itsuki 二次怒怼让 CC 当下改 skill 文本不靠 memory）+ 模式 2 假设崩 × 1（"昨天讲过的不用再翻"被推翻）+ 模式 6 取舍 × 1（翻译密度 vs 回复简洁度，选密度）+ **规则演化进化论证据**（v1 5-11 → v2 5-12 加严 → v3 5-12 加规则 6，1 天内 3 次迭代）。详见 `05_logs/raw/2026-05-12_修补批量+comm规则加严.md`

**残**：
- 7 个待 itsuki 拍板的事（详上面 raw §F / 含 Cloud Design 5-13 刷新 / 整理脚本跑不跑 / iOS Rule 1+2 漂移修 / vendor 清 / MEMORY 主体刷 / AC inbox 5-12 补 / file-linkage 标题 18→17）
- 本会话所有改动等 commit（3 modified + 1 新 raw log + WIP 自己。全局文件 `~/.claude/` 下的不入 DMSD git）
- 另一会话 untracked 3 文件（深度审查批 1 / 接力进度 / 执行计划）不动，让那条线自己 commit

**5-13 凌晨延续**（跨夜段，3 个关键产出）：
- 沟通规则文件迭代 v0.3.0 → v0.4.0（根本方向调整：概念强制中文 + 技术事实保留英文，废 v0.1-v0.3 "英文+括号翻译" 方向）→ v0.4.1（修正 DMSD / Tomoshibi 归类为专有名词保留英文）<!-- VERSION_OK -->
- 加 §7.5「收尾完成强制自查清单」到 session-wrap 文件 — 解决"CC 收尾默默跳过 N/A"系统性问题。8 项逐条核对表强制每次收尾必给（✅ / ⏸ + 显式理由 / ❌ + 解决方案）
- TODO 加 §🛠️ E + F（沟通规则后续 4 条 + 5-12 收尾残留 6 条）
- 3 次提交：`b9ae594` raw §I / `9c0398f` TODO §E+F / 本回合 WIP + session-wrap §7.5（待提交）
- 详见 `raw/2026-05-12_修补批量+comm规则加严.md §I`

### 2026-05-11 跨 23 点 by [新Mac-Opus 4.7 1M-CC2 reviewer 后门修复上线]

**主题**：⭐⭐⭐⭐⭐ 5-08「修干净再提交」拍板后 3 天的 reviewer 后门修复主线 5-11 晚收官 — 主项目 push GitHub + Mac→VPS 精细 rsync + alembic upgrade + SQL 重发凭证 + 验证全绿 + session-coord 多会话首测通过

- **会话身份**：session-coord 真实多会话首测中的 CC-2 角色（主会话 Opus47-1M-主 设计的双会话验证），跑通 register / scan / 公告 / 心跳 全链路
- **session-coord bug 自动收敛**：register.sh L81 + scan.sh L63 中文全角标点 + `set -u` → unbound variable，主会话 + CC-2 独立诊断同方案 = bug 客观存在不是偶发
- **戳穿 reviewer 后门三层分裂**：itsuki 问「修好了吗」→ git log 查到主项目 commit 852563c 已修 + 11 commit 没 push + Mac fork 缺 migration 文件 + VPS 上跑的可能还是 buggy → itsuki 拍板「让 VPS CC 修」
- **diff 戳穿"fork = 主项目"假设**：alembic/env.py + b2c3d4e5f6a7 是 VPS / fork 改过主项目没改；f6a7b8c9d0e1 migration 只在主项目；seed.py fork 是 buggy 后门源 / 主项目是双模式修过版 → 设计精细 rsync 避免破坏 VPS 修过的部分
- **跨机器协作分工**：Mac CC push GitHub + 写 VPS CC 提示词（Step A-F + 5 红线）；VPS CC 跑 Step A-F；itsuki 拍 SQL 红线节点
- **VPS CC 反向识破 Mac CC 任务描述偏差**：expires_at 2099 vs 2030 / "App Reviewer" vs "Reviewer 2026" — Mac CC 凭印象抄 TODO ledger，VPS CC 直接读主项目 seed.py 拿真值 + 停下问 itsuki = 收敛
- **VPS CC Step F 全绿**：alembic head=f6a7b8c9d0e1 / 旧 999999 invalidated + is_reviewer=f / 新 999999 reviewer 码 / 旧 060199 标 is_demo / curl 200 / api healthy
- **itsuki 怒怼"你到底在说什么呀"**：5-11 晚 graphify 会话刚立 `feedback_no_dense_jargon_strings`，当晚 reviewer 修复 CC 又踩 → memory 不解决当下问题，CC 元层翻车

**新规则上线**：
- 待写 memory：`feedback_cc_reference_source_of_truth_not_summary.md` — CC 给别的 CC 写提示词时必须引用源码 source of truth，不凭印象抄 ledger / 摘要 / WIP
- WIP §当前焦点 顶部加「⏰ 2026-05-12 截止 Cloud Design 40 额度」紧急条目
- TODO §⏰ 时间敏感 新 section（Cloud Design 5-13 凌晨刷新）

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2 × 2（itsuki「修好了」假设崩 + diff 戳穿 fork=主项目 假设）+ 模式 5 × 3（commit-push-deploy 三层分离 / source-of-truth vs 印象 / CC 元层翻车 memory 失效）+ 模式 6 × 2（精细 rsync 取舍 / 跨机器协作分工）+ 主线收官（5-08 拍板 public safety 真正动机 + 时间盒承诺兑现）。详见 `05_logs/raw/2026-05-11_reviewer后门修复上线.md`（§F.1-F.8）

**残**：
- VPS 端 4 项遗留：env.py + b2c3d4e5f6a7 反向同步回主项目主分支（不是 fork）/ reseed_reviewer.sql 留 VPS 当证据 / app.bak.20260511_123608 备份 1-2 天后删 / Apple Reviewer Notes 用新凭证（注册码原文不写）
- iOS 上架冲刺 A.1-A.11 步骤等 itsuki 坐到 Xcode 前继续（卡点已修通过 fork project.yml MARKETING_VERSION）
- 本会话改动等 commit（raw 1 新文件 + WIP/TODO 编辑）

### 2026-05-11 更晚 by [新Mac-Opus 4.7 1M-主会话 graphify]

**主题**：⭐⭐⭐⭐⭐ graphify 知识图谱工具上线全套（装 / 全量跑 / 发现 vendor 污染 + archive 漂移 + .beads 副作用 / 修复 / hook 装 / always-on 配 / **沟通问题大爆发**）

- **graphify v0.7.13 装上线** <!-- VERSION_OK -->：itsuki 给 GitHub URL → 读 README → 反问"API vs 订阅余额"→ CC 查 skill 源码确认走 CC subagent 不接 API → itsuki 拍板"装" + "趁余额重置 18 分钟内全量跑"
- **DMSD 全量跑**：573 文件 / 240 万字 / 13 chunk subagent 并行 / 6 分钟 → 9729 nodes / 26803 edges / 377 communities
- **vendor 污染发现**：god nodes 前 10 全是 React/Babel 压缩函数 `As() error() K() i()`（来自 iOS demo + teacher_web demo 的 vendor 目录 + phaseB_src）→ itsuki 反问"你到底在说啥" → CC 重新校准用零基础语言解释 → 写 `.graphifyignore` 排除（**待 `/graphify --update` 重跑才生效，目前图谱还是脏的**）
- **archive 漂移意外发现**：`99_archive/compose-drafts/HomeScreen.kt` 还在 import 活的 `GlobalScaffold` → itsuki 拍板不修
- **.beads 副作用抓获**：`graphify hook install` 偷改 git `core.hooksPath` 到 `.beads/hooks/` 覆盖 DMSD 原 `00_admin/hooks/` → 立刻验证 + 修复（copy hook 到主目录 + hooksPath 改回 + `.gitignore` 加 `.beads/`）
- **`graphify claude install` 装 always-on**：DMSD CLAUDE.md 加 graphify 段 + `.claude/settings.json` 加 PreToolUse hook → CC 以后每次工具调用前提醒读 `GRAPH_REPORT.md`
- **DMSD Hooks 7 → 10**：加 post-commit / post-checkout（graphify AST 自动重建）+ PreToolUse always-on
- **⭐⭐⭐⭐⭐ 沟通问题大爆发**：itsuki 3 次怒怼 — (1) "句子太密 5 个未知数堆一句话" (2) "真问题是你没把做的事写出来 + 字太省略 + 英文不翻译" (3) "你他妈跟我讨论方案了吗 / 单方面立 4 习惯不算讨论" → CC 写 feedback memory `feedback_no_dense_jargon_strings.md` 但 itsuki 明确说 **memory 不解决当下问题**。沟通方案**讨论尚未真正发生**（CC 抛了 3 观察 + 1 选项，itsuki 没回应直接让收尾）→ 详见 `raw/2026-05-11.md §E`（给新会话必读）

**新规则上线**：
- 全局 CLI 工具 `graphify`（`uv tool install graphifyy`）+ DMSD CLAUDE.md graphify always-on 段 + `.claude/settings.json` PreToolUse hook + DMSD Hooks 10 个
- `.graphifyignore` 配置文件（DMSD 根目录，排 vendor）
- `.beads/` 漂移注意点（`00_admin/hooks/README.md ⚠️ 段`）
- 个人能力清单 `~/.claude/我的环境.html` 加 graphify 用法速查 + hook 全套 + .beads 警告
- feedback memory `feedback_no_dense_jargon_strings.md`（MEMORY.md 索引 line 95 ⭐）
- ✅ **沟通方案 Skill + Hook 混合已落地** — 新 skill `cc-comm-rules`（`~/.claude/skills/`）+ 3 个 hook（`~/.claude/hooks/`）+ `~/.claude/CLAUDE.md` 加强制加载段 + `~/.claude/settings.json` 注册 hook。dry-run 测试 5/5 通过。详见 `raw/2026-05-11.md §F`

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 2 × 2（vendor 污染假设崩 + CC 以为问题是密度真问题是没说清做了啥）/ 模式 5 × 3（工程 ignore 文件普适性 + 第三方工具配置污染防御 + CC 元层翻车）/ 模式 6 × 2（archive 漂移取舍 + memory vs 当下讨论的取舍）/ 工程发现 × 2（vendor 污染 + .beads 副作用）。详见 `raw/2026-05-11.md §D + §E`

**残**：
- ✅ **沟通方案已落地** → 试用 1-2 周 + 看效果（详见 TODO §🛠️ A）
- vendor 污染配置写了但**还没重跑**：`/graphify --update` 待 itsuki 拍板（详见 TODO §🛠️ C）
- `~/.claude/我的环境.html` 还没同步 cc-comm-rules + 3 hook（详见 TODO §🛠️ B）
- 本会话所有改动（cc-comm-rules + 3 hook + raw §F + TODO §🛠️）一起待 commit
- 11+ commits 未 push 等 itsuki 拍板（详见 TODO §🛠️ D）

### 2026-05-11 晚 by [新Mac-Opus 4.7 1M-主会话 session-coord]

**主题**：⭐⭐⭐⭐ session-coord 多 CC 会话协作板 skill 从零到上线 + 真实多会话首测通过 + 顺手能力清单 HTML 化（5-11 MD→HTML 分层方案晚段实战）

- **诉求**：itsuki 直接喊 `/skill-creator:skill-creator` + 明确"多 CC 会话互相协同、互相做不同内容、不冲突" + 强制要求"上网搜，好好搜好好了解，不要偷懒"
- **2 个并行 agent 研究**：claude-code-guide（官方 Agent Teams + worktree + hooks）+ general-purpose（mclaude 7 层 + claude-squad / Tmux-Orchestrator + Matt Pocock skill 教学）
- **3 件大事**：Agent Teams 是 AI 自治不适合 itsuki（人是 leader） / mclaude 锁+心跳+handoff 3 件套可借鉴 / 行业共识 worktree 隔离>协商
- **itsuki 当场否决 CC 越级"5 Q 拍板"做法**：CC 直接抛术语让拍板 → itsuki 怒怼"心跳是什么？worktree 突然蹦出来？锁粒度是新单词？你完全没解释就让我拍" → CC 重写每个术语类比+演示+才让拍
- **itsuki 拍板"升级为协作板"**：CC 之前偏防冲突（锁+心跳），itsuki "我对 Skill 最大需求是每个 Session 互相知道对方、知道在做什么、互相搭配工作" → skill 抽象层升级（status.md / _board.md / inbox.md 三机制加）
- **关键设计拍板**：文件级锁 / 30s 心跳 / 3min stale / 装全局多项目共享 / 配置不存在 CC 主动问 init / **不用 Agent Teams**（AI 自治） / **不用 worktree**（高频改共享文件场景不对口） / **不直装 mclaude**（本土化）
- **9 scripts + SKILL.md + README.md + README.html + DMSD config 模板 落地**（draft 在 `.scratch/`，全局装 `~/.claude/skills/session-coord/`）
- **bug 修 2 处**：`$SESSION_ID（` / `$TASK（` bash 变量名+中文标点 unbound — 主会话 + 真实开的 CC-2 独立诊断同方案 = **收敛验证**
- **真实多会话首测通过**：主会话 + CC-2 互看 / inbox 互发 / 三档锁 / stale 释放 全 work
- **CC 自我反思**：自己以"cleanup"名义 `mv .claude/sessions/` 把 CC-2 状态搬走 = 设计 skill 的人最容易绕过自己 skill（模式 5）
- **能力清单 HTML 化**：itsuki 主动提"所有 skill / hook / CLAUDE.md 列表做成 HTML" → 补全 `~/.claude/我的环境.md`（13 全局 skills / 5 Plugin / 5 MCP / 7 DMSD skills / 7 DMSD hooks）+ 生成 `~/.claude/我的环境.html`
- **机制澄清**："CC 是回合制工具不会自动跟别的会话互动" — itsuki 接受根本限制，选"先正常用一段时间再加 hook"渐进路径

**新规则上线**：
- 全局新 skill `session-coord`（`~/.claude/skills/`）+ DMSD 装配置（`.claude/session-coord.config.json` + `.gitignore` 加 `.claude/sessions/` 和 `graphify-out/`）
- 个人能力清单 `~/.claude/我的环境.{md,html}` 补全 + 5-11 MD→HTML 分层方案晚段实战
- CC 行为铁律重申：先教再决策不越级 / 不绕过自己设计的 skill

**AC 价值**：⭐⭐⭐⭐⭐ — 模式 5 × 多（认知层升级 / 收敛验证识别 / 设计者绕过自己 skill 反模式 / itsuki 内化 MD→HTML 分层）+ 模式 6 × 4（不用 Agent Teams / 不用 worktree / 不直装 mclaude / 渐进 hook）+ 主体性 5/5（主动喊 skill + 强制 CC 研究 + 否决越级 + 升级抽象层 + 启 CC-2 真测 + 选渐进）。详见 `05_logs/raw/2026-05-11.md §C` + AC inbox 5 条

**残**：DMSD 11 commits 未 push 等 itsuki 拍板（含今晚改动）/ `graphify-out/` 82M 已加 .gitignore / superpowers plugin 配置仍 enabled 待 disable / session-coord UserPromptSubmit hook 未来某天看自觉度决定 / 副项目 CLAUDE.md 加 session-coord 钩子段（按需）

### 2026-05-11 by [新Mac-Opus 4.7 1M-主会话 术语表]

**主题**：⭐⭐⭐ 术语表 HTML 学习工具建立 — 5-11 MD→HTML 混层方案首个落地试水 + itsuki 元认知拍板「英文认得 vs 日语会说」分层 + CC 第 1 版静态字典被推翻重写交互式工具 + CC 漏 project-overview 同步被 itsuki 当场抓

- **元认知拍板**：itsuki 区分**英语 = passive recognition（认得）/ 日语 = active production（说出来）**两个学习目标 — "我又没说我要背读法，我就认得出来就好了。日语的话我必须要说出来。" 避免双语都要"会说"的低效路径
- **第 1 版被推翻**：CC 默认建静态字典（130 词 / 9 段），itsuki 一句反问"思考最高效让我达成目标的方式" → CC 反思字典 ≠ 学习工具 → 重写交互式版（180+ 词 / 16 段 / JS 渲染 / localStorage 进度 / 5 条认知科学原则）
- **5 条认知科学原则嵌入工具**：主动回忆 / 间隔重复 / 检索练习 / 交错学习 / 输出>输入 — 顶部展开框 + 测试模式（日语模糊点击揭晓）/ 4 状态标记 / 🎲 随机考我 5 张 / 实时进度面板
- **3 轮迭代覆盖**：v1 130 词 → v2 加 4 段（项目特有/宿舍日语/流程/概念） → v3 加 3 段 ~55 词（后端文件 21 / iOS 文件 29 / UI 代码常见词 20）— 第 3 轮是 itsuki 说"代码文件夹英语单词没背过别忘了"触发
- **CC 漏 project-overview 同步被抓**：CLAUDE.md L86 铁律「新建文件 → project-overview/SKILL.md 同步」CC 没主动跑，itsuki 反问 → CC 承认 + 补 3 处编辑 + 自我反思「下次不等你问」
- **itsuki 验证规则源头**：CC 引用「CLAUDE.md 铁律」时 itsuki 立刻问"是 CLAUDE 还是 skill 要求的" → CC grep 证明真在 L86 → 双层元层验证（执行层 + 规则层）
- **CC 主动修 ID 撞车 bug**：第 1 版 archive / tag 两个 ID 跨分类撞车会污染 mastery 状态 → 重命名 xcode-archive / nfc-tag / git-tag

**5-11 跨会话联动**：早些会话已在 TODO.md 加 §📄「MD → HTML 改造候选清单」拍板混层方案（CC 协作文件保 MD / 人最终读的文件候选 HTML，不强制双写）— 本次术语表.html 是首个落地试水 + TODO 自带「查 HTML skill」元任务等启动

**新规则上线**：
- 文件格式分层（CC 协作 vs 人最终读者）— TODO §📄 已建候选清单 + pandoc 临时渲染策略（要看 HTML 让 CC 渲染到 /tmp/ 永不入 git）
- itsuki 跟 CC 协作的**双层元验证模式** — 不只检查 CC 是否执行规则，还检查 CC 引用的规则真伪

**AC 价值**：⭐⭐⭐ — 模式 5 × 3（英/日认知分层 / 漏同步纠正 / 规则源头验证）+ 模式 2 × 1（CC 第 1 版假设崩→重写）+ 模式 6 × 2（HTML vs MD / 单独背 vs 项目语境化）。详见 `05_logs/raw/2026-05-11.md` 6 条素材深度 dump

**残**：术语表后续 itsuki 用一周后反馈是否真用得起来 / TODO §📄 候选清单 A 元任务（查 HTML skill）+ B 7+ 个候选 HTML 改造文件 / 多 commit 未 push 等 itsuki 拍板统一策略

**§B 早段会话补完（5-11 晚 session-wrap 收尾时记）**：§A raw 17:00 / 18:30 提到的「跨会话拍板混层方案 + TODO §📄 已加」实际就是 §B 本会话本体（不是另一会话）。§B 早段：itsuki 读 Thariq「Why HTML」全文 → CC 拆作者立场（5 用例全是人消费 / 没 DMSD 这种重 MD 协作层）→ itsuki 「就按混层」拍板 → 自己识破双写漂移坑（不等 CC 警告）→ 拍板方案 A「按需 pandoc 临时渲染」→ TODO §📄 落地（A 元任务 + B 13 候选 + C 已有 HTML + D 反向规则）。AC 价值 ⭐⭐⭐ — 模式 5 种子 / 模式 2 假设崩 / 模式 6 取舍 × 2 / 工程纪律「先 review 已有再决定新建」。详见 `raw/2026-05-11.md §B` 5 条 dump（ⓐ-ⓔ）

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
| `03_dev/device/` | 设备会话（Pi）|
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
6. **文件地图**：`CLAUDE.md §目录结构` + `00_admin/文件结构指南.md`
7. **文档一致性**：声明性文件不写硬编码版本号，见 `CLAUDE.md §文档一致性规则`
8. **itsuki 偏好**：选项用 A/B/C 不用甲乙丙 / α β γ；决策他拍板；不盲从 AI

---

## 🕘 本文件自己的更新日志

- **2026-05-04 上午** — 加 2026-05-04 会话条目（A+B 文件联动工具建设）
- **2026-05-04** — 🔧 **大改 by [Mac-mini-Opus 4.7]**：itsuki 指出 WIP 跟 TODO 重叠 → 拍板方案 A → 砍「🔄 进行中的任务」section（218 行，跟 TODO 重叠）+ 砍「✅ 最近完成」长尾历史（170 行，commit history 已记录）+ 头部「最后更新」长串历史压缩到「最近会话」5 条 → 全文 600 → ~160 行；分工规则写明铁律「未完成的事只写在 TODO」；CC 启动流程加「扫 TODO 顶部 200 行」。备份 `/tmp/WIP_backup_2026-05-04.md`
- **2026-05-10** — 加 ac-radar 上线条目（共 6 条超 5 条上限）→ 砍 5-04 晚 iOS bug 修复条目（详见 raw/2026-05-04_iOS_bug修复.md）
- 更早历史 — 见 `git log -- 00_admin/WIP.md`
