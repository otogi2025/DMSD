# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-05-28 凌晨（跨夜会话 — 主体在 5-27 晚段-3：老师实名账户登录改造 + 砍匿名建議 + codex 5.5 xhigh 审查；起因：itsuki 看到 web 登录页 501 错误 → CC 诊断双服务器分离 → itsuki 顺势拍板老师登录从「共用密码」改成「实名账户列表→选名字→输密码」+ 加教师创建/删除管理页 + 砍残留匿名建議 + 拍板「老师登录跟学生登录没关系」纠正 CC 默认对齐 iOS 路径 +「做完后 codex 审查 5.5 xhigh」。CC 4 commit 落地：`b9f237c` backend（CORS + auth.py teacher_id 形式 + 3 schema + teachers.py 3 新接口）+ `b444aad` frontend（LoginScreen 完整重写 2 屏合一 + TeachersAdminPage 新建 + 砍 anon tab + 3 假数据）+ `1904b18` 5 个设计档案同步 + `aba0659` codex 审查修 3 🔴 阻塞（timedelta import 缺 prior bug / INVITE_ALLOWED_ROLES 给「学習担当」越权 / 没拦最后一个 admin = 系统 lockout）+ 关键 🟡/🟢。剩余 4 项 itsuki 决策 / 大工程进 TODO §🚀-G。AC 价值：模式 1+2+5+6 顶级 × 4。早段 — teacher_web v1.0 凌晨深夜推进收尾会话 + 醒后 backend 自审 9 处修复：itsuki 启动「审查我做的事到底做好了没」+「不要停下来问 / 不需要决策的直接修 / 决策的加 TODO」→ CC 自查 5 维度：alembic migration ✅ / 13 router 注册 ✅ / 61 endpoint 真 import 通过 ✅ / Student.is_demo 字段已加 ✅ / client.js 32 helper 跟 backend 路径 100% 对齐 ✅ / 5 处 index.html 日语注释中文化（中文铁律）/ 全部 9 处真 bug 已在凌晨别会话修完。早些深夜-3 — iOS 全自主审查 + 修 + 收尾会话：itsuki 启动「审查这个 iOS APP 看有什么问题，然后去做去修」+「做完后就直接收尾，不要给我留问题，也不要停下来问我，所有的问题加到 todo 里面」→ CC 5 维度过完 41 文件 / 修 1 处（`MyPageStubs.swift:1404` `c.score!` force unwrap 改 `map ?? _`）/ 2 处架构性问题写 TODO §D（`StayListStubs.swift:475` catch 降级 mock 假数据 / `MyPageStubs.swift:1637` 暴露 `localizedDescription`）/ 所有 demo 后门 + A-XXX bug 标记 + NFC UI + 其他 catch 全部确认 ✅。早些深夜-2 — 跨天会话「2026-05-25 晚段-2 / AC 学习内容清单 v0.1.0 起草」收尾：5-25 晚 itsuki 抛元认知反思「5 端开发但一门语言都没掌握 + 文件认不全」+ 主动要求扩充「专业知识 + 项目底层运转逻辑」→ CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章（工程层改动被 5-26 晚段-4 别会话 commit `3d945a7` 顺手带走）+ 列 4 章扩充大纲（第 9-12 章）等拍板 → itsuki 直接说「收尾」未实装 → 加 TODO §🛠️ §M 6 条悬挂任务 + raw `2026-05-25_AC学习清单起草.md` 4 段深度 AC 素材；模式 5 顶级 × 2。早些 2026-05-27 深夜 — itsuki 让 CC 清 TODO 里「不需要决策 + CC 自己能做 + 不重要」的小活清单 14 件<!-- VERSION_OK --> + project-overview drift 修：6 件本来就闭合 TODO 没刷状态（T1 3 文件已归档 / T2 .DS_Store 删 / T3 临时PDF 目录已不存在 / T7 DESIGN_BRIEF 5-26 已重写 / T8 DEVICE_REGISTRY §6 已是 dorm-1/2 / T9 FC-025-028 已标 ✅ N/A）+ 7 件真做（T4 99_archive README 时间戳 / T6 WEB_DESIGN_LOG §7+§10 路径过时项 / T11 project-overview §6.2 raw 48→55 / T12 SC26 session-wrap §7.5.5「6 项」→「8 项」/ T13 全局环境清单 DMSD Skills 7→8 加 dmsd-startup / T14 WIP 最近会话 10→5 砍 5 条 / T15 §0.1 体量表全刷新 1181→1189）+ 2 件挂起待 itsuki 拍板（T5 backend 表数 13→21 + P0/P1/P2 分级标准 / T10 系统bug专栏 77 条状态字段工作量大）；起因：itsuki 启动「列 TODO 里不重要 CC 自己能做的小活」+ 说「做完后直接收尾，想 commit 就 commit」。早些 2026-05-26（晚段-4 — teacher_web Vite + TypeScript 实装版整体废弃 + Ryō polish 试做被回滚 + 修破工具脚本 demo_server.py 死链改 python http.server + 文档同步 WEB_DESIGN_LOG §12 + DESIGN_BRIEF + v1/README + 物理清 node_modules 81MB + dist + decision_log 加 2 条；起因：itsuki 启动「推进 teacher web」+ 看到 Vite 实装版怒怼「这他妈根本不是我的 web」拍板「垃圾归档用 B」+ frontend-design skill polish 试做整体不喜欢一句「回滚」全退。早些晚段-3 — iOS demo 后门清理（做法 B）+ 字段对齐零漂移 commit `7521bf8`。早些晚段-2 — 全项目中枢机制立项 + DMSD 注册档案 + DMSD CLAUDE.md 加「全项目中枢联动」段；同时合并早段 iOS Bot 1 复查 + 暗夜模式 v2 + 3 上架配置归位 + memory 加铁律「TODO 关条目不要问」入「最近会话」。早段头：启动 SOP 集中化 — 新建 `.claude/skills/dmsd-startup/SKILL.md`（5 件启动必做事）+ 全局 `~/.claude/hooks/session-start-coord-check.sh` 在 DMSD 项目下静默退出 + DMSD CLAUDE.md「会话开始」段简化引用新 skill + 6 项目 CLAUDE.md 加「不主动用英语名词」规则段 + project-overview SKILL.md §0.1 + §1.7 同步 + 本文件「会话开始」铁律改成走 dmsd-startup skill）。5-25 晚段（追加：第三轮升级 — anti-ai-flavor 加第 3 触发词「**翻车**」单字 + 新建 `inbox.md` — itsuki 收尾中途立项自我迭代机制：发现新翻车点 → CC 按 5 字段「原文 / 6 类归类 / 违反铁律 / 根因 / 修正版」记 inbox，未来批量整理合并到 `references/翻车案例库.md`；改 5 文件：新建 `inbox.md` + SKILL.md 加 §7.5 + CLAUDE.md 触发词 2→3 + hook 提醒 + `我的环境.md` + `.html`）。早些（同晚段）：anti-ai-flavor HOW_TO_TALK.md 立项 + 跨 3 项目 session-wrap 加项 11/8 — itsuki 给 16 个翻车原句证据 → 4 根本问题 + 9 类细分 → 5 条总结铁律 → 方案 B 落地：SKILL.md 反面自检 + HOW_TO_TALK.md 正面教学互补 + 2 触发词「说人话」/「单词白名单」+ DMSD/SC26/Tango session-wrap 收尾清单同步加「全局环境清单同步」项 — 全局 6 文件 + DMSD 1 文件 + 2 memory + SC26 1 文件 + Tango 1 文件。早些 5-25（drift 脚本 bug 修 + 全局 `session-coord` 三层保险落地 — DMSD 2 文件 + 全局 4 文件 / 全局 Hooks 4→5；同时补登 5-24 iOS bug 批量修复会话遗漏的收尾）。早些 5-22（**3 会话产出** — ① 早 project-overview §0.1 漂移 957→980 / ② 中 iOS fork 融合归档 commit `46f779c` / ③ 晚 点呼机推进 + 撞海关查扣事件 + 立项 `session-wrap §5.5.15 decision-draft`）。早些 5-21（5-20 凌晨 4 会话审查作战 cron 自动 fire 产出 131 条 findings / 5-21 加系统 bug 专栏 + 第一批修复 8 条）。早些 5-19（project-overview 大改造 + 防漂 C 方案）。<!-- VERSION_OK -->

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

### 2026-05-28 web 登录页修复 — 账号砍到1个 + 返回按钮改显眼 by [MacBook-Pro-Sonnet 4.6]

**主题**：compact 续接（前半段 f4a882f 已 commit）。itsuki 第一次实机打开新实名账户登录页，报 2 个 bug：①登录页 9 个账号「密码不知道」→ CC 查出密码是 `seed.py:39 DEV_PASSWORD = "123456"` 明文常量（itsuki 不知道有这个东西）→ 9 个假数据账号砍到 1 个「新股（寮務部長/全权限跨寮）」+ 备份旧数据库 + 重建 dev 库（seed 是幂等的：光改代码不动数据库 = 旧数据还在，必须重建）②密码页「← 別の先生を選ぶ」返回按钮「失灵」→ CC 用截图里「パスワードが違います(残り 2 回)」反推 React 确实活着（逻辑 OK），真因是按钮 fontSize:12+灰色+padding:0 点击区域极小 → 改蓝色背景+padding:8px 可见按钮。commit `01d0654`。AC：模式 2（假设崩→继续→真因）+ 模式 5（seed 隐藏常量 / 数据层 vs 代码层认知）× 2。raw：`05_logs/raw/2026-05-28_web登录页修复.md`

### 2026-05-28 宿舍申請实物表数字化 by [MacBook-Pro-Opus 4.7 1M]

**主题**：itsuki 提供宿舍真实纸质申请表「届け類.pdf」9 种扫描件 → 要求读懂 + 派 codex 双读对比 + 写进设计规范 + 实装（三步走）。CC 读 10 页 = 9 种表（帰省通常/長期 / 外泊日本人/留学生 / 学習欠席 / 行事企画 / 日課変更 / 冷蔵庫 / 物品所持）。codex（gpt-5.5）独立读图 3 次调用失败逐个修（参数贪婪吞提示词 → stdin / 目录信任 → skip / 只读沙箱）后双读核对**高度一致**。写进 `system_features.md` §7.2（出寮届補完）+ §7.3.5（补漏掉的在线学习申请类型）+ §7.21（新增 4 种全新表单）+ §8（数据模型 + 4 新表）+ IOS_DESIGN_LOG §14（别会话 commit 0ccd19d 带走）。itsuki 拍板 6 待决点：①日本人外泊含寮務部長（4人）②留学生帰省跟实物走（4人无国際交流部長）③帰国届有独立表「様式3-1 留学生・長期休暇」抬头**校長**→approver_role 加校長第7值 ④学習欠席一人审查 ⑤晚自习开始 19:40（实物 19:30 作废）⑥4 种新表都进 v1.0。实装 backlog 进 TODO §T。AC：需求工程（真实凭证驱动设计）+ 多 AI 交叉验证 + 发现现有设计缺口（学習欠席届只做半截）。本会话 commit：system_features + TODO（待 commit）。

### 2026-05-28 简报 + 注册页 demo 默认空 + 数字码 bug 修 + IOS_DESIGN_LOG 部分中文化 by [MacBook-Pro-Opus 4.7 1M]

**主题**：compact 续接。简报启动检查 → 注册页学年/组/出席号/房间号 4 字段 demo 也默认空（itsuki 要演示账号番号随输入实时变化）→ codex 审查发现数字码真 bug（iOS 送中文「高3」但后端 `schemas.py` 要 `^\d{2}$` 数字码，真实学生注册必被打回）→ 修（含出席号 ≤99 上限 + 提交转 gradeCode/classCode/补零 seat_no）→ IOS_DESIGN_LOG §1/§3/§5 日语→中文（界面字符串保留）+ §11 技术区约 180 行加 TODO §S → commit `0ccd19d`。drift 修（05_logs 114→116）被别会话 `f4a882f` 顺手 commit。AC：不盲信 codex 误报（核实 SeedModels.swift 证伪第 4 点）+ itsuki 理解码 vs 显示分离 + UX 演示设计。

### 2026-05-27 晚段-4 / 跨夜 5-28 凌晨 by [MacBook-Pro-Opus 4.7 1M / iOS 登录注册大改 + AC 素材分级机制 + 申请履歴进度条]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动后报告 iOS 登录页 5 处 UI 问题 + 担心非 demo 模式注册会真写他个人信息到后端 → CC 改 6 处 + 派 codex 5.5 高档位审查 → codex 报 3 个真问题（gender / grade-classSuffix / birth 默认值数据污染）→ **itsuki 主动延伸顶级 AC 素材**：「正常代码里怎么会默认帮忙选好了性别和年龄」+「平均年龄选中位数 = 人性化设计」+「AC 素材主动提报权重更高，分级储存免得被淹没」→ CC 建 `_priority_itsuki主动提报/` 子目录 + memory 加铁律 + 修 4 处代码（中位数 picker 默认 2011-01-01 / canNext 加性别学年组别检查 / classCode 空映射改 00 / gender 默认空）→ 申请履歴 chip 链改进度横线 + 无名节点（同步 IOS_DESIGN_LOG + system_features §7.2.6 新章）→ 修 pbxproj 4 处加 APIErrorPresenter 文件注册（别会话遗留）→ 教 Edit Scheme 走到 Build Configuration

**关键拍板**（itsuki 11+ 次）：
- 「demo 模式需要预填」+「移动进 demo 模式不就好了？」（推翻 CC 第一版改法）
- 「你用 codex 5.5 xhigh 审查」（主动调度第三方代理审查）
- 「这些问题都是 ac 素材哈」（主动识别 AC 价值）
- 「正常代码里怎么会默认帮忙选好了性别和年龄」（原则铁律）
- **「平均年龄选中位数 = 人性化设计」**（顶级延伸，模式 5 ⭐⭐⭐⭐⭐）
- **「主动提报权重 > CC 自查，建分级机制」**（顶级元元层，模式 7 ⭐⭐⭐⭐⭐）
- 「役职名 chip 太丑改进度横线 + 节点」+「无论同意顺序都是往右变化」（设计推翻）
- 「同步改 5 端设计文档」（机制完备性）

**实际改动**（DMSD 6 文件 + iCloud AC inbox 3 文件 + memory 2 文件 = 11 文件）：
| 类别 | 文件 |
|---|---|
| iOS 改 | `AuthStubs.swift` 11 处（DEMO 包预填 10 + UI 文案 / 行为 / 热区 5 + canNext 加 3 字段必填）/ `StayListStubs.swift` chainDots 重写（chip 链 → 进度横线 + 节点）|
| iOS 项目结构 | `project.pbxproj` 4 处加 APIErrorPresenter 文件注册（别会话遗留 bug）+ `project.pbxproj.bak3` 备份留 |
| 设计同步 | `IOS_DESIGN_LOG.md §11.9 I11` 补 2026-05-28 进度条样式拍板段 + `system_features.md §7.2.6` 新章「承认 chain UI 显示规则（5 端通用）」|
| iCloud AC inbox | 新建 `_priority_itsuki主动提报/` 子目录 + `README.md` 分级规则 + `2026-05-27_ios注册默认值人性化设计.md` 第一条主动提报素材 + `ac_scratchpad_2026-05-27.md` 加信号 9 |
| DMSD raw | `05_logs/raw/2026-05-27_ios登录注册大改+审批链进度条.md` 8 节详细叙事 |
| memory | 新加 `feedback_ac_priority_tier_itsuki_initiated.md` + `MEMORY.md` 索引 |
| project-overview | §0.1 总计 1197 → 1198 + 05_logs 113 → 114 + §6.2 raw 61 → 62 |

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 5 顶级 × 2** — 「中位数默认 = 人性化设计」+「AC 素材分级机制」两条都是 itsuki 主动延伸出来的，不是 CC 教的
- **模式 6 取舍 × 2** — A/B/C 三层默认值选择（偷懒 / 强制必选 / 中位数）+ chip 链 vs 进度条 + 节点
- **模式 7 机制完备性** — 物理隔离 priority 子目录防被低权重素材淹没
- **协作三层模型** — Claude（工程层）+ codex（数据正确性层）+ itsuki（用户体验+设计哲学层）三方分工
- **学术延伸**：HCI Defaults theory / Median-of-population default / Type-driven UX design / Information architecture / AI 协作伦理

**残（下次跟进）**：
- itsuki 还没跑通 Edit Scheme → Build Configuration → Demo（卡在第 2 步操作教学，CC 重写后等 itsuki 试）
- SourceKit 报 SplashView 段 cannot find type — 索引坏，需重启 Xcode + Clean Build Folder
- 申请履歴新 UI 视觉验证 — 等 itsuki 跑通 demo 模式后看效果
- 老师 Web / Android 端审批链 UI 实装（system_features §7.2.6 标 ⏳）
- 工作树 ?? 3 个 untracked：`APIErrorPresenter.swift`（别会话新建）/ `PROJECT_GUIDE.md`（itsuki 自己加）/ `project.pbxproj.bak3` 备份 — 看 itsuki 决定哪些 stage

详细 raw：`05_logs/raw/2026-05-27_ios登录注册大改+审批链进度条.md`

### 2026-05-28 凌晨 by [MacBook-Pro-Opus 4.7 1M / iOS catch 修 + StayDetail 切真 API + codex 审查全装]

**主题**：⭐⭐⭐⭐⭐ itsuki 启动「推进 iOS 全做」→ CC 扫现状区分真活 vs 已完成（注册码 iOS ✅ / 公告 iOS ✅ 无活）→ 修 TODO §D 2 处 catch + 切回 5-03 漂移的 StayDetail 真 API → itsuki「调用 codex 审查」→ codex 第一次卡住 + itsuki「还没好——」→ CC 诊断 + 重试简化版 → codex 3/5 报告 → CC 识破误判（`$0` 闭包简写被 codex 误读为 `/bin/zsh`）→ itsuki「全都做」→ 实装 6 项（新建 helper + 401 清 token + audit 容错 + 拆 guard + MyPage helper + 文档同步）+ TODO §D + §E 两条 iOS fork 过期项闭合（5-22 归档时实际已同步主项目，悬挂 6 天）

**关键拍板**（itsuki 4 次 + 协作纠错 1 次）：
- **「今晚全做」** — 4 个候选方向全做的强授权
- **「他妈的 graphify 是什么？」** — 协作纠错顶级（CC 用了未解释术语违反「不要默认认识英语单词」铁律 + 全局 CLAUDE.md 5-27 加的 8 类自检第 1 类「术语裸露」+ 第 2 类「缺上下文」）
- **「调用 codex 审查一边」** — 多 AI 协作触发
- **「A」** — codex 卡住后选「重开简化版」（3 选项 A/B/C）
- **「全都做」** — 接受 codex 真建议 5 项（剔除 1 个误判后）

**实际改动**（DMSD 6 件 + 工具产物 2 件）：
| 类别 | 文件 |
|---|---|
| 新建 | `03_dev/student_ios/v1/TomoshibiApp/Foundation/Network/APIErrorPresenter.swift`（39 行 — `APIError` 6 case 转日语提示统一 helper）|
| 改 iOS | `Features/StayList/StayListStubs.swift` — `loadList` 401 改清 `app.authToken = nil` 触发跳登录页 + `StayDetailView.load()` 拆 guard（未登录 vs 非 UUID 分开 toast）+ `audit` 单独 try 容错 + 4 catch 走 helper |
| 改 iOS | `Features/MyPage/MyPageStubs.swift` — 删账号 catch 9 行 switch → 1 行 helper 调用 |
| 改 文档 | `IOS_DESIGN_LOG.md` — §速查表 5 项 🟡 → ✅ + §11.9 I11 → ✅ + 最后更新日改 |
| 改 TODO | `00_admin/TODO.md` — §D 463 + §E 477 两条 iOS fork 过期项闭合（5-22 已归档实际同步完成，悬挂 6 天）|
| 新建 raw | `05_logs/raw/2026-05-28_ios_codex审查会话.md` — 8 段详细 dump + 工程汇总 + AC 价值 ⭐⭐⭐⭐⭐ |
| 新建 inbox | iCloud `06_radar_inbox/ac_scratchpad_2026-05-28.md` — 4 信号顶级评分 |
| 重建 | `graphify-out/graph.json` + `GRAPH_REPORT.md` — 17487 节点 / 35753 边 / 677 文件 |
| 工具产物（未 commit） | `project.pbxproj`（hook 自动注册 helper +4 行）+ `.bak3_before_apierrorpresenter_register` 备份（不 commit）|

**AC 价值** ⭐⭐⭐⭐⭐：
- **模式 2 假设崩 顶级 × 2** — codex 一定成功（卡住假设崩）+ CC 不能 verify codex 输出（CC 验证发现误判假设崩）→ 都没放弃 → 重试 + 验证 + 落地
- **模式 4 v1→v2 演化 顶级** — 错误处理 4 步演化（原始降级 mock → 切回真 API → codex 审查发现风险 → 抽 helper + 401 清 token + audit 容错）
- **模式 5 认知改变 顶级** — itsuki「graphify 是什么」+「见过 ≠ 知道意思」元认知（hook 提示过 ≠ itsuki 认识）
- **模式 6 取舍 × 多** — codex 卡住 3 选项 / 401 mock 取舍 / audit 致命非致命 / helper 抽象边界
- **协作纠错** × 1 顶级 — itsuki 当场质疑 CC 沟通失职
- **方法论级别** — AI 协作真实形态（不盲信 / fallback / 验证 / 提示词精简）+ 信息边界诚实（CC 主动加注「没真验证 backend，只看了 iOS 注释」）

**残（下次跟进）**：
- iOS 真没活了 — 学習出席 / rollcall NFC 真接等 backend / Xcode Archive 上架冲刺等 itsuki 操作
- WIP 8 条超上限 — 等 itsuki 拍板砍 3 条
- working tree 别会话遗留改动（hardware_design / system_features / Auth / README / PROJECT_GUIDE / 5-27 别会话 raw / pbxproj scheme）— 等别会话自己 commit

详细 raw：`05_logs/raw/2026-05-28_ios_codex审查会话.md`

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
