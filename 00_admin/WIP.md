# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-22（**3 会话产出** — ① 早 `1779447495-6286` 修 project-overview §0.1 漂移 957→980 + 加 `系统bug专栏.md` / `codex_audit_prompt.md` 引用 + B2 Fix-Bot 4 `effective_*` 已完成确认 + F1 清 5-14 过期警告标记 / ② 中 `1779447279-2548` iOS fork 融合归档 + 5 文件 backport + commit `46f779c` / ③ 晚 `1779447985-17762` 点呼机推进 → 撞 5-12~16 海关查扣事件 → itsuki 拍板撤回中国海运改日本本地买 + 立项 `session-wrap §5.5.15 decision-draft` 收尾子节 — CC 永不直写 `decision_log.md` 正文只起草草稿 / 改 8 文件）。早些 5-21（5-20 凌晨 4 会话审查作战 cron 自动 fire 产出 131 条 findings / 5-21 加系统 bug 专栏 + 第一批修复 8 条）。早些 5-19（project-overview 文件介绍大改造 + 9 处漂移对账修复 + 防漂 C 方案落地 / 详见 `raw/2026-05-19.md`）。早些 5-16 下午（跨项目 CC 完整性审计 + 大修）。<!-- VERSION_OK -->

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

**当前版本之后的阶段**（版本号见 `CHANGELOG.md` 顶部） — 5 端代码层启动完毕（iOS + Android + Web + Backend + 点呼机），下一步重点：
1. 老师公告 4 端实装（iOS + Android + Web + Backend — 不含点呼机）— spec 已落 `system_features.md §7.15`
2. 学生注册码 v1.0 实装（4 端 spec 已就位 2026-05-03 上午别会话 — 不含点呼机）
3. 文档欠债：`progress_overview.md` 章节级里程碑刷新（4-17 之后没动）

→ 完整 backlog 看 `TODO.md`。

---

## 📜 最近会话（最多保留 5 条，老的删 — 详细历史看 commit log + raw/）

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

### 2026-05-16（下午 16:30-18:30）by [新Mac-Opus 4.7 1M-跨项目优化]

**主题**：⭐⭐⭐⭐⭐ itsuki 主动质疑「3 项目 + 默认目录 CC 是否完整工作」→ 派 codex 审计 → 4 拍板 + 大修 → CC 自检发现 4 问题 → 全部落地 + 修 macOS bash 3.2 heredoc 中文乱码 bug

**关键拍板**（itsuki 5 次明确决策）：
- **Tango B 案**（保留 6 skill 骨架重写适配单端 web）
- **SC26 轻修**（删过期 version-bump / new-feature 引用 + 复检残留）
- **cc-project-template D 案**（清成真通用模板 — 197 处 DMSD 残留全清成占位符 / 通用骨架）
- **全局 hook session-wrap-checklist-remind.sh 改读 cwd**（DMSD 8 项 / SC26 6 项 / Tango **6 项单 web 版** — 之前硬编码三套混合输出）
- **修 hook 中文乱码**（之前判断不修 →「也去检查一下」后改主意「现在修」）

**实际改动统计**：
| 项目 | 文件数 | 谁做的 |
|---|---|---|
| Tango | 8 改动 + 1 新建根 CLAUDE.md | codex 6 + 我修 v0.5→v0.6 |
| SC26 | 2 改动 | codex 改 CLAUDE.md + 我改 hooks/README |
| cc-project-template | 12 改动 | 我全做（hook 头注释 / PROJECT_DIR 默认值 / MEMORY_DIR 动态算 / pre-commit / README / 起新项目）|
| 全局 hook | 1 重写（含 v2.1 bug 修） | 我全做 |

**bash 3.2 heredoc bug 根因 + 修法**：
- 现象：hook 输出 `「��` 乱码（紧贴右全角标点的变量末字节 + 全角字符首字节合并解析）
- 试 `export LANG=en_US.UTF-8` → 没用（跟 locale 无关）
- 真因：macOS 默认 bash 3.2 heredoc parser bug
- 修法：所有「$VAR」改成 [$VAR]（半角方括号）/ 或 「 $VAR 」加空格

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 1**（派生痛点）：核心项目 OK ≠ 副项目能跑，主动审一遍不等翻车
- **模式 2** × 3：codex sandbox 报告字段误判（git status 是真值）/ locale 假设崩 / 紧贴全角标点假设验证 ✅
- **模式 6** × 4：同会话 4 个相反策略（Tango 保留 vs 模板清通用 — 按上下文判断不一刀切）
- **debug 元规则**：假设崩 → 换另一个假设，不固执；改 production 前先写最小测试用例
- **主体性 5/5**：5 次明确拍板，每次都给理由
- **学术延伸性**：软件工程「通用 vs 专用」「right tool for the job」「DRY 反例」+ debug 方法论 — AC 面试都能挂

**残（下次跟进）**：
- 4 项目改动**未 commit** — 待 itsuki 审核 + 决定 commit message
- 全局 hook 不在 git 仓库（`~/.claude/` 没 init）— 永久 propose 把 `~/.claude/` 做成 git 仓库
- Tango 3 处 skill 引用「DMSD raw 共用」**保留**（A 案 — Tango 立项 3 天没真开发，Phase 2 真开发时再建 Tango 自己 raw）
- codex 顺手修了 SC26 CLAUDE.md「在日 6 年 → 2 年 9 个月」fact 错（保留）

**详细 raw**：`05_logs/raw/2026-05-16.md`

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
- ~~WIP 已 8 条超 "最多 5 条" 上限~~ ✅ **2026-05-22 已清** — 5-19 收尾砍 5-14 早段沟通规则 v0.5.0 段，当前正好 5 条（5-19 / 5-16 / 5-14 晚段-2 / 5-14 中午 / 5-14 晚段）<!-- VERSION_OK -->

详细 raw：`05_logs/raw/2026-05-14.md` §K（4 段素材 + §L 工程动作清单）

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
