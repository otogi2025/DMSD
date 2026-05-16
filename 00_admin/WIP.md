# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-16 下午 16:30-18:30（跨项目 CC 完整性审计 + 大修 — codex 审计 4 项目 → Tango B 案重写 6 skill / SC26 轻修 / cc-project-template **D 案清成真通用模板**（12 文件改）/ 全局 hook session-wrap-checklist-remind.sh **改读 cwd** + Tango 6 项单 web 版 + 修 macOS bash 3.2 heredoc 中文乱码 bug — 详见 `raw/2026-05-16.md`）。5-16 上午（别会话）：接力 5-14 晚段-2 会话 — 工程边角清理：环境清单 §3+§4+§11 补 dream/anti-ai-flavor-precheck/session-wrap-checklist-remind / WIP 砍 5-11 段 5 条到 5 条上限 / 写 feedback_cc_skips_interview_step.md / 术语表 5-14 早段产物补 commit。5-14 晚段-2: anti-ai-flavor 全局挂钩立项 + cc-comm-rules 同日撤回 v0.5.0 → v0.6.0（`raw/2026-05-14.md §K`）。<!-- VERSION_OK -->

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

> **⭐⭐⭐ 沟通规则 cc-comm-rules v0.6.0（5-14 晚撤回 v0.5.0）** — 新会话必读 → `raw/2026-05-14.md §K` + 全局挂钩 `~/.claude/skills/cc-comm-rules/SKILL.md` <!-- VERSION_OK -->
> **v0.6.0 撤回 v0.5.0「英文自由用」** — 回归 v0.4.1「概念术语强制中文 + 技术事实保留英文」+ 新加 §2.3.1「术语后必带中文效果描述」。起因：v0.5.0 早段拍板当晚实测翻车（must 模式 / action 模式 / modified / 残 / 误判拒答 看不懂）。术语表 180+ 词条**保留**作 AC 学习材料，但 v0.6.0 后**不再自动加词**。<!-- VERSION_OK -->
> **配套新挂钩**：`anti-ai-flavor` 全局挂钩（CC 说话别像 AI、像真人聊天 — 气质层）— 6 类痛点 A-F（A 缺上下文 / B 复杂条件句 / C 网络黑话 / D 术语裸露 / E 字面化 / F 客套腔）按反感程度排序，always-on。详见 `~/.claude/skills/anti-ai-flavor/SKILL.md`<!-- VERSION_OK -->
> v0.1-v0.4「约束 CC 输出」思路全部作废。<!-- VERSION_OK -->
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

### 2026-05-14（晚段-2 20:00-20:37）by [新Mac-Opus 4.7 1M-anti-ai-flavor+cc-comm-rules v0.6.0] <!-- VERSION_OK -->

**主题**：⭐⭐⭐⭐⭐ 新建 `anti-ai-flavor` 全局挂钩（CC 说话别像 AI、像真人聊天）+ cc-comm-rules **同日撤回 v0.5.0「英文自由用」→ v0.6.0**（回归 v0.4.1 + 加 §2.3.1「术语后必带效果描述」）<!-- VERSION_OK -->

**关键拍板**：
- itsuki 给三层权重证据（亲身经历 6 例 > 网络黑话词单 > Opus 4.7 5 维分析），CC 拆出 6 类痛点 A-F 按反感程度排序（A 缺上下文 / B 复杂条件句 / C 网络黑话 / D 术语裸露 / E 字面化执行 / F 传统客套腔）
- itsuki 当场识别 CC 跳 skill-creator interview 第一步 → 怒怼 "我们还没开始讨论呢？你怎么帮我写 skill？" → CC 承认 + 退回 + 主动问 2 个核心问题
- v0.5.0 同日内推翻 — 早段拍板「英文自由用」当晚就发现 D 类痛点（must 模式 / action 模式 / modified / 残 / 误判拒答 看不懂）→ 撤回回归 v0.4.1 + 加 §2.3.1 新规则。术语表 180+ 词条**不删**（作为 AC 日语学习材料价值还在）<!-- VERSION_OK -->
- 触发模式 hybrid — SKILL.md 主体短（always-on 自检）+ 详细 patterns / 黑名单按需读
- itsuki 选 C — 不跑 8 个 subagent 测试直接落地，下次会话观察

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 高分例** — 同日内（12 小时内）对自己拍板的 v0.5.0 做出推翻 + 给出具体翻车证据 + 推翻精度（保留思路里对的部分，只撤回真错的）<!-- VERSION_OK -->
- **协作纠错** — itsuki 当场识别 CC 跳 interview，不等做完才回头
- **证据分层判断力** — 三层权重排序证据（亲身经历 > 网络列举 > 网络分析）= 元方法论
- **元层翻车** — CC 写 anti-ai-flavor 时自己也犯 F 类（强迫执行）+ A 类（缺上下文），反讽性证据比成功案例更说明问题

**残（下次跟进）**：
- anti-ai-flavor 8 个测试用例 subagent 对比未跑（itsuki 选 C 跳过，下次会话真实使用中观察问题）
- 网络黑话黑名单持续补 — 现在一级 7 词 + 二级扩展，下次见新黑话追加 `references/jargon-blacklist.md`
- 术语表.html 已 modified（5-14 早段 v0.5.0 添词的产物）— v0.6.0 后不再自动加词，已有词条保留，要不要 commit 这次 modified itsuki 拍板 <!-- VERSION_OK -->
- `~/.claude/我的环境.html`（清单美化派生版）未重新生成 — itsuki 决定要不要刷
- WIP 已 8 条超 "最多 5 条" 上限 — 下次清理 5-11 段 4 条老条目（详细历史在 commit log + raw）

详细 raw：`05_logs/raw/2026-05-14.md` §K（4 段素材 + §L 工程动作清单）

### 2026-05-14（中午）by [新Mac-Opus 4.7 1M-graphify 实测复盘]

**主题**：⭐⭐⭐⭐⭐ graphify 装 3 天闲置 → itsuki 主动质疑实战价值 → CC 第一轮 propose 卸载漏核心用法被 itsuki 校准 → 实读 GRAPH_REPORT.md → 5 机制对比 → 拍板「不卸不用 + 留作 AC 素材」第 4 选项创造

- **起因**：itsuki 启动后问"之前装的那个能省 token + 文件之间连接 + 总结报告的 skill 是什么" → CC 答 graphify → itsuki 反问"这到底有什么用？我怎么感觉完全没用到？"
- ⭐⭐⭐⭐⭐ **CC 第一轮 propose 翻车**：CC 列 graphify vs 5 机制对比倾向卸载（propose B 卸 hook 留 CLI），但漏了 GRAPH_REPORT.md 作为「项目结构总结报告省 token」的核心用法 — itsuki 一句话校准戳穿 CC 视野盲点
- ⭐⭐⭐⭐⭐ **CC 实读真实文件后改口**：CC 实读 1887 行报告，发现报告确实是项目总结（11112 节点 → 465 community），但报告头还是脏的（前 36 个 hub 全是 `Vendor: React/Babel runtime`）+ post-commit hook 只跑 AST 差量不重做 community 聚类 → CC 承认 propose B 方向错（卸 hook 等于把"省 token"机制本身拆了）
- ⭐⭐⭐⭐⭐ **5 机制对比给清晰结论**：CLAUDE.md / WIP / project-overview / file-linkage 4 个现有机制 = 人写的语义信息（精确 + 按需加载 + 更新成本低）/ graphify = 自动抽的 AST 代码结构（糙 + 每次塞 1887 行反而费 token）→ DMSD 真实问题（字段对齐 / 改 A 必改 B / 文件功能）是语义级，AST 解决不了
- ⭐⭐⭐⭐⭐ **itsuki 拍板「不卸不用 + 留作 AC 素材」**：CC 给 5 个具体卸载步骤后，itsuki 没选任何动作选项，自创第 4 个叙事选项 — "我不断尝试新工具，不断学习别人，不断迭代，然后实际使用后，发现还不如原本自己搭建的框架好用"
- ⭐⭐⭐⭐⭐ **跟早段 v0.5.0 同构思维模式**（晚段-2 撤回 v0.5.0 → v0.6.0 是中午之后的事，本次拍板时 v0.5.0 仍生效）：同一天 2 次拍板都用同一元规则 — 「把过程性失败转化为可索引的资产」。早段 = 4 次约束 CC 输出失败后改归档术语表 / 中午 = 工具实验闲置后留作 AC 素材。模式 5 元规则横向迁移（4 小时内 2 次独立应用） <!-- VERSION_OK -->

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**：派生痛点识别 — 看到工具 3 天没用主动质疑（不被动等工具自证）
- **模式 2** × 2：CC 第一轮 propose 卸载假设崩 / CC 以为 graphify 适合 DMSD 假设崩
- **模式 5** × 多：工具选型方法论（装前问代价 / 装后问价值）/ CC 视野盲点被 itsuki 戳穿 / CC 实读真实文件后自主改口 / 通用 vs 专用经典取舍 / 元规则横向迁移
- **模式 6** × 多：卸 vs 留 vs 重跑 → itsuki 跳出框架创造叙事选项 / 通用 vs 专用 / 沉没成本不死扛也不全删
- **主体性 5/5**：主动质疑 / 校准 CC 视野盲点 / 不被 CC 框架限制 / 创造第 4 选项 / 把失败实验转化为 AC 资产
- **学术延伸性**：软件工程经典议题 — 沉没成本 / DRY 原则 / right tool for the job / premature abstraction / 通用 vs 专用 — AC 面试可挂"软件设计方法论 / 工具选型"

**残（下次跟进）**：
- graphify 配置不动（CLAUDE.md 段 / PreToolUse hook / post-commit hook / `graphify-out/` 82MB / 全局 CLI 全保留）
- TODO §🛠️ C「graphify 图谱清洗」+ §🛠️ F「graphify vendor 污染清」标记为"已废 — 5-14 拍板不用"
- 术语表新增 14 词（9 个 ⑰ cc-workflow graphify 协作词 + 5 个 ⑬ concept 软件工程概念）
- 中央 inbox 5 条 AC 信号已 flush
- 本会话改动 commit（`05_logs/raw/2026-05-14.md` §I 段 + `06_assets/术语表.html` 14 新词 + `00_admin/WIP.md` 本身 + `00_admin/TODO.md` 2 条标废）

**详细 raw**：`05_logs/raw/2026-05-14.md §I`（150 行深度 AC dump）

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

> **2026-05-16 砍 5 条**（让 5-13 接力 audit + 5-14 早段沟通规则 v0.5.0 + 5-14 中午 graphify 复盘 + 5-14 晚段 Tango 立项 + 5-14 晚段-2 anti-ai-flavor 立项 维持 5 条上限）：砍 5-12 修补批量+规则加严 / 5-11 跨 23 点 CC2 reviewer 后门修复上线 / 5-11 更晚 graphify / 5-11 晚 session-coord / 5-11 术语表 — 详细历史看 commit log + raw <!-- VERSION_OK -->

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
