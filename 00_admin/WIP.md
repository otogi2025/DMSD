# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-06-04（**AC 升学素材体系大重构** — 旧四级流水线「人工精选」闸门空转 + 两校各存一份 → 重构成「两校共用原始池」：建 `大学入試/00_原始素材池_两校共用/` 迁 75 素材 + 两校侧重组 `03_按X口味提炼/04_产出/99_证据截图` + 改 6 脚本指向新池 + iCloud 根建统一归档区 `99_归档/`；同会话早段 iOS 黑屏诊断 / 外部 AI 评估 / 统一两个根目录都已归档；详见最近会话顶条）；早些 2026-06-04（**项目协作机制讨论** — 启动维持 skill 不上 hook / 心智模型 §4 砍掉跟 WIP 的重叠（只标成熟度档位）/ 新建 `codex-review` skill；详见「最近会话」顶条）；早些 2026-06-03（**版本号回溯规范化** — 把 5-11~6-02 一个多月的 236 commit 按语义化版本（SemVer）一次性补了 6 个版本标签 v0.8.1~v0.12.0 + CHANGELOG 6 个条目，当前版本从 v0.8.0 升到 v0.12.0；历史标签全保留不动 / 未改代码 / 未 push；详见 raw 2026-06-03）；早些 2026-06-02（**IX-034 请假计数接后端 `e0c150c` + 过夜无人值守 GOAL 设计**——详见最近会话顶条；早些 2026-05-31 **teacher_web v1.0 全实装 + codex 5 轮复审收敛** — itsuki `/goal`「老师网页做到能直接上线 v1.0」超长自主会话八波施工：摸底(4 并行 agent)→修 7 后端 bug+网页接 13 死接口→建学生账号管理→删 demo+生产配置→**6 大模块全建**(行事予定/巴士/指導履歴/事案/个人档案聚合/一括进级 + push 骨架，各后端建表迁移接口测试 + 网页 UI)→W8 自审 30+ 问题→**codex 独立复审 5 轮到它自己说「0 blocker 0 major 可上线」**(寮边界系统性补齐是第 4 轮挖出)。后端 193 测试 / 前端 check_jsx 0 错。收尾写 NFC 防代刷立项 + 上线部署清单。24 commit **未 push**。AC 模式 2+5+6 + 教训「独立验证 agent 自报」。详见 raw `2026-05-31_teacher_web_v1.0全实装+codex5轮收敛.md`）；早些 2026-05-30（session-coord 多窗口协作板改 hook 后台自动维护 — 详见「最近会话」顶条 + `raw/2026-05-29_session-coord自动化.md`）；早些 2026-05-29（项目心智模型机制建立 — 新建 `00_admin/项目心智模型.md` AI 开局必读骨架 + 挂进 dmsd-startup/session-wrap，详见「最近会话」顶条 + `raw/2026-05-29_项目心智模型机制.md`）；早些 2026-05-28（点呼机采购清单 HTML 会话 — itsuki「做个 HTML 含购买清单+点呼机信息 / 我发的链接你确认了吗 / 图片塞进去可折叠」→ CC 用 WebFetch 逐个抓 itsuki 发的采购链接核对，揪出截图看不出的坑：风扇链接 `B0DYV31FJZ` 是 12V（Pi 只有 5V 转不动）+ 喇叭链接 Apqfw 和截图 HONKYOB 对不上 + 蓝 LED 漏链接 + 杜邦线买重 + PN532 链接 500 抓不到。做 `03_dev/rollcall_device/点呼机采购清单.html`（6 块：目的与效果/机器组成原理/下单前提醒/采购清单带可点链接/接线速查/16 截图折叠区）+ 16 截图复制进 `采购截图/` + project-overview §5.8 点呼机 11→12 文件 + TODO §R 加「🔥 下单前必确认」8 条高优先。AC：主体性 + 交叉验证「不假设链接=需求」，早段 116 天伪问题的正面版）；早些 2026-05-28（iOS 申請界面实装会话 — itsuki「接着做 iOS app 实装 → 派 codex gpt-5.5 xhigh 干活 / CC 规划+审查」。两轮 codex：① 出寮届扩展 + 帰国届校長链修 + 4 新申请界面（在线学习/行事企画/冷蔵庫/物品所持）+ 网络层 ② 补 3 个「我的提交列表」。CC 审查不盲信 codex 自报：codex 沙箱跑不了 iOS 真编译只能语法解析 → CC 独立 `xcodebuild` 抓到 2 个 codex 查不出的 `Field` 参数顺序错 + 修。后又修演示版回归：codex 跑 `xcodegen generate` 擦掉了手动配的 Demo 编译配置 → CC 写进 `project.yml`（Debug/Release/Demo + 独立 bundle id 区分正式/演示 + DEMO 开关 + 2 scheme）永久 regen-safe；itsuki 演示需求：房间号 A5 + 注册第五步认证码预填「000000」用 `#if DEMO` 包（顺带解决 A-035 生产后门）。正式版+演示版都 `BUILD SUCCEEDED`，演示版装模拟器跑起来验证（启动页 v1.0.0-demo + 登录预填）。未做：6 新界面逐屏运行点查（无模拟器点击工具）留 itsuki 手走。改 8 文件+新建 4 文件+配置 2 文件，**未 commit/push**。AC 模式 2 + 多 AI 协作顶级）；早些 2026-05-28（点呼机硬件采购夜会话 — itsuki「今晚把点呼机硬件全买好」→ CC 发现 5-22 海关查扣后日本本地选型还是「待选型」占位 → itsuki 给 5-19 调研 4 家分工清单 + 拍板方案 A 首单 1 台 → CC 回填 `hardware_design.md` §5.1'/§4.2'/§4.6/§0；CC 调 Codex GPT-5.5 xhigh 审查报「ST25DV 每 10 秒写 EEPROM → 116 天磨穿」当致命问题，CC 原样转 itsuki → itsuki 一句常识推翻：点呼非 24h 全天刷，只在时间窗（120~360 次/天）→ 寿命 7-22 年，116 天伪问题（Codex 前提错，CC 转述没审前提=失职）→ 写给第二个 AI 提示词把坑写进去防再犯，第二 AI 确认 + 补官方手册引用；逐件核对截图选型 13 件 + 教练答零基础问题；决策 ST25DV ×4/风扇 5V/喇叭 USB/转接线 SparkFun Qwiic 套件；产出 hardware_design 回填 + TODO §R 学习任务 + 新建 `rollcall_device/点呼机接线说明.md` + project-overview §5.8 + 2 份外部 AI 审查提示词）；早些 2026-05-28（申請表后端实装会话 — itsuki 拍板「申请表规范改动全落实 → 派 codex gpt-5.5 思考等级 xhigh 干活 / CC 写详细提示词负责规划 / codex 改完 CC 审查」。CC 写 6 节自包含提示词 → codex 后台 workspace-write 实装后端（`applications` 加 6 实物字段 + `approver_role`/`teachers.role`/`CROSS_DORM_ROLES` 加「校長」+ `approval_chain.py` 4 处链修正 + 新表 `study_online_requests` + 4 张生活申请表 dorm_event/schedule/fridge/item + 新路由 study_online.py/dorm_life.py + alembic `d2e3f4a5b6c7`）→ CC 审查不盲信：逐个 diff 8 个越界文件诊断为「测试套件早坏（引用不存在的 `StudyAttendanceRoster`）+ `pyproject.toml` 弃用即报错策略」逼的、非乱改 / 独立重跑确认 70 测试通过 / 临时配置造真正空库复验 10 个迁移全链路 upgrade-downgrade 通过。commit `c6ccee0`（17 文件 +1325/-67）。itsuki 拍板：校長保留 A「实物有校长就要校长」+ iPhone 进 TODO §T 标「下一步立刻做」+ 安卓/老师网页暂不走 + 开发库不 stamp。AC 模式 2+6 顶级。早段（跨夜会话 — 主体在 5-27 晚段-3：老师实名账户登录改造 + 砍匿名建議 + codex 5.5 xhigh 审查；起因：itsuki 看到 web 登录页 501 错误 → CC 诊断双服务器分离 → itsuki 顺势拍板老师登录从「共用密码」改成「实名账户列表→选名字→输密码」+ 加教师创建/删除管理页 + 砍残留匿名建議 + 拍板「老师登录跟学生登录没关系」纠正 CC 默认对齐 iOS 路径 +「做完后 codex 审查 5.5 xhigh」。CC 4 commit 落地：`b9f237c` backend（CORS + auth.py teacher_id 形式 + 3 schema + teachers.py 3 新接口）+ `b444aad` frontend（LoginScreen 完整重写 2 屏合一 + TeachersAdminPage 新建 + 砍 anon tab + 3 假数据）+ `1904b18` 5 个设计档案同步 + `aba0659` codex 审查修 3 🔴 阻塞（timedelta import 缺 prior bug / INVITE_ALLOWED_ROLES 给「学習担当」越权 / 没拦最后一个 admin = 系统 lockout）+ 关键 🟡/🟢。剩余 4 项 itsuki 决策 / 大工程进 TODO §🚀-G。AC 价值：模式 1+2+5+6 顶级 × 4。早段 — teacher_web v1.0 凌晨深夜推进收尾会话 + 醒后 backend 自审 9 处修复：itsuki 启动「审查我做的事到底做好了没」+「不要停下来问 / 不需要决策的直接修 / 决策的加 TODO」→ CC 自查 5 维度：alembic migration ✅ / 13 router 注册 ✅ / 61 endpoint 真 import 通过 ✅ / Student.is_demo 字段已加 ✅ / client.js 32 helper 跟 backend 路径 100% 对齐 ✅ / 5 处 index.html 日语注释中文化（中文铁律）/ 全部 9 处真 bug 已在凌晨别会话修完。早些深夜-3 — iOS 全自主审查 + 修 + 收尾会话：itsuki 启动「审查这个 iOS APP 看有什么问题，然后去做去修」+「做完后就直接收尾，不要给我留问题，也不要停下来问我，所有的问题加到 todo 里面」→ CC 5 维度过完 41 文件 / 修 1 处（`MyPageStubs.swift:1404` `c.score!` force unwrap 改 `map ?? _`）/ 2 处架构性问题写 TODO §D（`StayListStubs.swift:475` catch 降级 mock 假数据 / `MyPageStubs.swift:1637` 暴露 `localizedDescription`）/ 所有 demo 后门 + A-XXX bug 标记 + NFC UI + 其他 catch 全部确认 ✅。早些深夜-2 — 跨天会话「2026-05-25 晚段-2 / AC 学习内容清单 v0.1.0 起草」收尾：5-25 晚 itsuki 抛元认知反思「5 端开发但一门语言都没掌握 + 文件认不全」+ 主动要求扩充「专业知识 + 项目底层运转逻辑」→ CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章（工程层改动被 5-26 晚段-4 别会话 commit `3d945a7` 顺手带走）+ 列 4 章扩充大纲（第 9-12 章）等拍板 → itsuki 直接说「收尾」未实装 → 加 TODO §🛠️ §M 6 条悬挂任务 + raw `2026-05-25_AC学习清单起草.md` 4 段深度 AC 素材；模式 5 顶级 × 2。早些 2026-05-27 深夜 — itsuki 让 CC 清 TODO 里「不需要决策 + CC 自己能做 + 不重要」的小活清单 14 件<!-- VERSION_OK --> + project-overview drift 修：6 件本来就闭合 TODO 没刷状态（T1 3 文件已归档 / T2 .DS_Store 删 / T3 临时PDF 目录已不存在 / T7 DESIGN_BRIEF 5-26 已重写 / T8 DEVICE_REGISTRY §6 已是 dorm-1/2 / T9 FC-025-028 已标 ✅ N/A）+ 7 件真做（T4 99_archive README 时间戳 / T6 WEB_DESIGN_LOG §7+§10 路径过时项 / T11 project-overview §6.2 raw 48→55 / T12 SC26 session-wrap §7.5.5「6 项」→「8 项」/ T13 全局环境清单 DMSD Skills 7→8 加 dmsd-startup / T14 WIP 最近会话 10→5 砍 5 条 / T15 §0.1 体量表全刷新 1181→1189）+ 2 件挂起待 itsuki 拍板（T5 backend 表数 13→21 + P0/P1/P2 分级标准 / T10 系统bug专栏 77 条状态字段工作量大）；起因：itsuki 启动「列 TODO 里不重要 CC 自己能做的小活」+ 说「做完后直接收尾，想 commit 就 commit」。早些 2026-05-26（晚段-4 — teacher_web Vite + TypeScript 实装版整体废弃 + Ryō polish 试做被回滚 + 修破工具脚本 demo_server.py 死链改 python http.server + 文档同步 WEB_DESIGN_LOG §12 + DESIGN_BRIEF + v1/README + 物理清 node_modules 81MB + dist + decision_log 加 2 条；起因：itsuki 启动「推进 teacher web」+ 看到 Vite 实装版怒怼「这他妈根本不是我的 web」拍板「垃圾归档用 B」+ frontend-design skill polish 试做整体不喜欢一句「回滚」全退。早些晚段-3 — iOS demo 后门清理（做法 B）+ 字段对齐零漂移 commit `7521bf8`。早些晚段-2 — 全项目中枢机制立项 + DMSD 注册档案 + DMSD CLAUDE.md 加「全项目中枢联动」段；同时合并早段 iOS Bot 1 复查 + 暗夜模式 v2 + 3 上架配置归位 + memory 加铁律「TODO 关条目不要问」入「最近会话」。早段头：启动 SOP 集中化 — 新建 `.claude/skills/dmsd-startup/SKILL.md`（5 件启动必做事）+ 全局 `~/.claude/hooks/session-start-coord-check.sh` 在 DMSD 项目下静默退出 + DMSD CLAUDE.md「会话开始」段简化引用新 skill + 6 项目 CLAUDE.md 加「不主动用英语名词」规则段 + project-overview SKILL.md §0.1 + §1.7 同步 + 本文件「会话开始」铁律改成走 dmsd-startup skill）。5-25 晚段（追加：第三轮升级 — anti-ai-flavor 加第 3 触发词「**翻车**」单字 + 新建 `inbox.md` — itsuki 收尾中途立项自我迭代机制：发现新翻车点 → CC 按 5 字段「原文 / 6 类归类 / 违反铁律 / 根因 / 修正版」记 inbox，未来批量整理合并到 `references/翻车案例库.md`；改 5 文件：新建 `inbox.md` + SKILL.md 加 §7.5 + CLAUDE.md 触发词 2→3 + hook 提醒 + `我的环境.md` + `.html`）。早些（同晚段）：anti-ai-flavor HOW_TO_TALK.md 立项 + 跨 3 项目 session-wrap 加项 11/8 — itsuki 给 16 个翻车原句证据 → 4 根本问题 + 9 类细分 → 5 条总结铁律 → 方案 B 落地：SKILL.md 反面自检 + HOW_TO_TALK.md 正面教学互补 + 2 触发词「说人话」/「单词白名单」+ DMSD/SC26/Tango session-wrap 收尾清单同步加「全局环境清单同步」项 — 全局 6 文件 + DMSD 1 文件 + 2 memory + SC26 1 文件 + Tango 1 文件。早些 5-25（drift 脚本 bug 修 + 全局 `session-coord` 三层保险落地 — DMSD 2 文件 + 全局 4 文件 / 全局 Hooks 4→5；同时补登 5-24 iOS bug 批量修复会话遗漏的收尾）。早些 5-22（**3 会话产出** — ① 早 project-overview §0.1 漂移 957→980 / ② 中 iOS fork 融合归档 commit `46f779c` / ③ 晚 点呼机推进 + 撞海关查扣事件 + 立项 `session-wrap §5.5.15 decision-draft`）。早些 5-21（5-20 凌晨 4 会话审查作战 cron 自动 fire 产出 131 条 findings / 5-21 加系统 bug 专栏 + 第一批修复 8 条）。早些 5-19（project-overview 大改造 + 防漂 C 方案）。<!-- VERSION_OK -->

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

**当前版本**: v0.12.0 <!-- VERSION_OK -->（2026-06-03 回溯把 5-11~6-02 的 236 commit 按 SemVer 补了 6 个版本标签 v0.8.1~v0.12.0，详见 CHANGELOG 顶部）
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

### 2026-06-04 AC 升学素材体系大重构 — 两校共用原始池 by [Opus 4.8 1M]

- 起因：itsuki 连环追问暴露旧 AC 素材体系设计缺陷（radar inbox 跟素材候选职责重叠 / 「人工精选」闸门从没运转 / 要同时申请筑波+庆应需素材通用）。
- itsuki 核心洞察：原始素材两校通用、分叉在产出端（= 单一数据源多视图，他自己悟出来的）。
- 做了（7 步全程只移不删，旧物归档）：iCloud 根建统一归档区 `99_归档/` + 共用池 `大学入試/00_原始素材池_两校共用/`；迁 75 原始素材进池；筑波 `04_素材_成品`（_v2归档31个）整体归档；两校侧重组成 `03_按X口味提炼/04_产出/99_证据截图`；改 6 脚本指向新池（append_to_scratchpad / daily-archive / session-start 重写 / startup_check / pre-write-protected 重写护新 04_产出 区 / ac-radar SKILL.md）；2 README + 验证全绿。
- 同会话早段：iOS 动画黑屏诊断归档 / 外部 AI 项目评估两段归档（审前提标 SFC≠筑波等 5 处不能照抄）/ 统一两个 AC 根目录（AC/→大学入試/ 移 19 文件 + 改脚本 + 修 memory 路径错）。
- AC：模式 5（元认知，顶级）+ 系统架构设计（单一数据源多视图）。新建 memory `project_ac_material_system_two_school_pool`。raw `2026-06-04.md`。

### 2026-06-04 项目协作机制讨论 — 启动 skill/hook + 心智模型/WIP 职责 + 建 codex-review skill by [Opus 4.8 1M]

- 起因：itsuki 主动反思自己搭的协作机制，连问启动要不要改 hook / WIP 和心智模型是否冗余 / 把「派 codex 审查」做成 skill。
- ① 启动维持 skill 不上 hook（itsuki 自己想通：只要记得说「启动」，skill 就能代替 hook 全部功能；「机制兜底优于自律」铁律针对 CC 反复忘，触发权收回自己手里就不适用）。
- ② 心智模型 vs WIP 砍重叠：心智模型 §4 四列→两列（只标成熟度档位 + 一句话定位，细节进度归 WIP，防作弊大缺口单独强调），治好「§4 老过期漂移」。session-wrap 项 12 同步改成「只在成熟度跳档才更新 §4」。当前焦点留 WIP。
- ③ 新建 `codex-review` skill（派 codex gpt-5.5 xhigh 只读审本会话改动 → CC 逐条裁决+修 → 复审 → 跑到收敛；不带「codex」字样不触发）+ 登记 CLAUDE.md / project-overview。
- AC：模式 5（认知，顶级 ×2）+ 模式 6（取舍 ×3）+ 模式 2（把不盲信 codex 制度化）。raw `2026-06-04.md`。

### 2026-06-03 演示版逐屏打磨 + 出租车预约 4 端功能 by [Opus 4.8 1M]

- 起因：itsuki 实机逐屏看 iOS 演示版揪问题（假数据自相矛盾 / 表单不符真实纸质表 / 页面切换黑屏），逐条改；后授权全自主做完出租车功能 + codex 审 + 收尾，期间不打断。
- 演示打磨：通知 / 主页去 Amazon + 活动改誕生日会 / カフェテリア + 删早帰 / その他申请类型 + 删 4 处界面假 ID + 删 2 条矛盾假数据（早帰点进去显示成帰国届）+ 页面切换黑屏修复（`RootView` 去 opacity transition）。
- 出寮届表单对齐两张真实纸质表（様式3-1 帰国 / 様式3-2 外泊）：交通方法拆出寮 / 帰寮两串不同选项 + 删飞机（走帰国飞机段单独填）+「教員送迎」→「教員」+ 加寮生特別運行 + 滞在先→宿泊先 + 帰国隐藏「行先（都市名）」。
- **出租车预约 4 端新功能**：后端 `applications.taxi_reservation_time`（Time/nullable）+ migration `a7b8c9d0e1f2` + iOS `StayForm` 提交+详情+外出 UI 桩 + 老师网页预留的「タクシー」tab 实装（badge 防漏看）。Android 记 TODO（骨架未接后端、无法 gradle 验证）。前后端对齐。
- codex 5.5 xhigh 审查：1 阻塞（migration 编号撞既有 events，换 `a7b8c9d0e1f2` + `alembic heads` 验证）+ 3 建议（帰国教师详情误显行先都市 / 修改届 taxi 名义改 create-only / tab sub 共享）全修。验证：后端 223 测试 / iOS 双 scheme BUILD SUCCEEDED / check_jsx 0 错。
- AC：模式 2（codex 审出真 bug→CC 独立核实→修 + CC 自己编译 exit code 陷阱自纠）+ 5（真实凭证驱动表单设计）+ 6（判断后端不用改 / Android 取舍）。raw `2026-06-03_演示打磨+出租车功能.md`。

### 2026-06-03 文件联动系统盲点补全 + codex 审查 by [Opus 4.8 1M]

- 起因：补一条点呼机架构链联动规则（6-02 漂移事故的漏）后，itsuki 让「优化所有文件互联 + 找别的有问题的文件」→ CC 否决「1256 文件全连 = 噪音淹没信号 / 告警疲劳」，改精准补真实盲点。
- 产出：联动规则 19 → 23 条。补 4 类盲点（老师网页活代码 index.html/client.js 裸奔 / 后端字段漏提醒 Android / spec 字典链 / 版本号链）+ codex GPT-5.5 xhigh 审查后修 2 处 + 新增 Rule 24（联动系统自身同步）。改 `00_admin/hooks/lib/sync-rules.sh`（规则真值）+ `.claude/skills/file-linkage/SKILL.md`（人读版）。
- 独立验证两层 AI：子代理逮到 2 处数字不准、codex 逮到 1 处错误修法（建议 ERE 不支持的 `(?!...)` 负向先行）。codex 揪的 3 个预先存在问题（demo 函数返回值反转 / Rule 6 死路径 / must 路径无锚定）记 `TODO.md` §🛠️ D1-D3。
- AC：模式 2（AI 方案崩→核验→真做）+ 模式 6（取舍）。raw `2026-06-03_文件联动盲点补全.md`。

### 2026-06-03 版本号回溯规范化 — 236 commit 补 6 个版本标签 + 三端版本号统一 by [Opus 4.8 1M]

- ✅ **回溯补 6 个版本标签 v0.8.1~v0.12.0**（时间对齐各段末端 commit）+ CHANGELOG 6 条目 + WIP 当前版本 v0.8.0→v0.12.0（commit `48e7c97`）。判断：每段有真新功能=次版本号 / 纯修复或开发工具链=修订号。<!-- VERSION_OK -->
- ✅ **三端客户端版本号统一 0.12.0**（commit `e91e768`）：iOS project.yml + TTokens（rc/demo）+ Android versionName + 老师网页 APP_VERSION 全部统一。<!-- VERSION_OK -->
- 🔧 **index.html / README 版本号改动留工作树**（跟并行会话改动叠着，等 itsuki 整理文件一起 commit + push）。本会话发现另一窗口在并行改 iOS/点呼机/file-linkage。
- AC：模式 5（itsuki 学 SemVer 主/次/修订号规则 + commit 数≠版本号 + 否决 v10.0/重写历史）+ 不盲信 AI（itsuki「修了很多 bug 先确认」逼 CC 用数据验证定性）。详见 raw `2026-06-03_版本号回溯规范化.md`。<!-- VERSION_OK -->

### 2026-06-02 iOS B 类接后端续 — IX-034 请假计数 + 过夜无人值守 GOAL 设计 by [Opus 4.8 1M]

**🔴 进度 + 过夜 GOAL 运行规则在 `05_logs/ios接后端_进度与handoff.md` §7（新会话 / 压缩后先读）。**

- ✅ **IX-034 请假计数按月接后端**（`e0c150c`）：后端 `GET /study/absence-requests/me/summary`（当月 target_date 全状态计数）+ iOS loadMe 拉真实当月数替代内存累加 + 3 测试。后端 220 / iOS 双绿。Codex 5.5 xhigh 审出 4 点待修（跨月仍 +1 / loadMe 令牌竞态 / 测试时区 / formatYMD）→ 留过夜 GOAL 第一件事。
- 🔍 **IX-007 调查揪出前提是假的**：修繕/来訪/代理受取后端零实装（`applications` 表 CHECK 只允许出寮届三种）→ otherDetailBody 生产是死分支 → 走 Option A 降级 DEMO（Option B 真做要拍板，跳过）。
- 🌙 **设计过夜无人值守 GOAL**：itsuki「挂这儿去睡，遇要决策的跳过、做能做的」→ 写 goal 指令 + handoff §7（不准问 / 跳决策记清单 / 不 push / handoff 自管上下文）。
- **待办**：handoff §7.1 IX-034 4 点 → IX-009 通知（聚合公告+审批）→ IX-007 Option A → 5-30 审查 🟡 批。
- AC：审任务前提（代码 CHECK 约束推翻文档描述）+「修好所有问题」拆三层 + 委托 AI 过夜自主跑设计护栏。raw `2026-06-02_iOS接后端_IX-034+过夜GOAL.md`。

### 2026-05-31 iOS 学生端 B 类「演示假数据→真后端」接线（多阶段 + codex 每阶段审）by [Opus 4.8 1M]

**🔴 本会话进度全在 `05_logs/ios接后端_进度与handoff.md`（压缩防丢信息文件 — 新会话 / 压缩后先读它）。**

**主题**：iOS B 类「演示假数据→真后端」。itsuki「全都修好」+「每阶段派 codex gpt-5.5 xhigh 审」+「别停下问自己决定」。**两大块完成**：
- ✅ **IX-004 修改届接后端 — 5 轮 Codex 对抗复审收敛关闭**（`5a8be64`→`0ee5546`→`5b97b45`+文档`a49daf9`）。每轮真挑出问题（阶段3 含越权+滥用2个我没看出的），每条核实再修，测试 1→18 个。后端 pytest 201 / iOS 双 scheme 绿。
- ✅ **IX-008 当前用户接 /me**（`464d42f` /me + `04e5887` category + `b4dea6f` iOS currentUser/displayUser + `97d0180` 登出残留修复）。73 处假用户 → 登录拉 `/me` 真实化（currentUser+displayUser+SEED.user安全网）。后端 209 / iOS 双绿。**Codex 额度被并发会话耗尽（晚11:57重置）→ 我自己自审 + 逮到登出残留 bug 修了**，独立审查待补。
- **待办**（详见 TODO §🔧 + `05_logs/ios接后端_进度与handoff.md`）：IX-008 Codex 补审 / IX-008b 扣分统计接入(真人现显0) / 老师退回(returned)动作未实装 / is_study_target 后端字段。
- AC：多 AI 对抗复审当质量门 + 额度耗尽自己顶上 + 重构前调研拆阶段（模式 2+5+6）。raw `2026-05-31_ios接后端_IX004收敛+IX008用户资料.md`。

### 2026-05-29 session-coord 协作板改 hook 自动维护 by [MacBook-Pro-Opus 4.8 1M]

**主题**：itsuki 自己发现多窗口协作板（session-coord）缺陷「注册完不更新 / 别窗口不知道在干嘛 / 怕费 token」→ 要求「先帮我了解再优化」。CC 读全部脚本确认 3 条全对 → 诊断真因「靠 CC 每回合自觉跑脚本，CC 不自觉=摆设」→ 撞 itsuki 旧铁律「机制兜底优于自律」。方案：改 hook 后台自动维护。新建 `~/.claude/hooks/session-coord-auto.sh` + `lib/session_coord_auto.py`（挂 SessionStart+UserPromptSubmit）：开窗自动注册 + 每次发话刷心跳 + 把 itsuki 那句话存「当前任务」，零对话 token；改 register.sh（认 `CLAUDE_CODE_SESSION_ID` + 幂等）/ scan.sh（死窗口瘦身 + 自动清理超 1h）。配套同步 6 文档。已验证 hook 建目录/记任务/scan 对号/瘦身（假数据模拟），**真实触发待 itsuki 重开窗口确认**。全局 9 文件不在 repo 无法 commit，DMSD 内仅 dmsd-startup/SKILL.md + raw commit（`f424f7e`）。AC：模式 2+5+6。raw：`05_logs/raw/2026-05-29_session-coord自动化.md`

### 2026-05-29 扫项目推荐自动化 + 配 Dependabot / 密钥扫描 by [MacBook-Pro-Opus 4.8 1M]

**主题**：itsuki 用 claude-automation-recommender skill 扫 DMSD，要推荐 hooks/skills/MCP/子代理/自动化并配好。CC 实扫现有配置（已很满：8 DMSD skill + 15+ hook + context7/github/chrome-devtools MCP），只推真缺的 3 个，并把「不缺的」诚实列出。itsuki 反复纠正「术语看不懂，说人话」→ CC 重列全 18 候选大白话版（每个一句它干嘛）。建好 **#14 Dependabot**（`.github/dependabot.yml` 监控后端/点呼机 pip + 安卓 gradle + actions 漏洞，每周一）+ **#1 pre-commit 密钥扫描**（造假 SendGrid 密钥实测，拦得住 exit 1）。#7/#9/#10（连本地库/线上库/Sentry）因没服务器、本地库基本空（2 学生）→ CC 判断「现在加没意义/加不了」记 TODO §🔌「上线时配置」等上线提醒。#16 安卓 CI 判不建（代码还早，会天天编译失败红叉）。AC：模式 5（itsuki 学会「数据库本地 vs 服务器」「MCP 是啥」「CI 概念」「Playwright 不操纵电脑只开浏览器」）+ 技术判断（质疑 #7 前提 / 主动要求 #9 提前记防忘）。raw：`05_logs/raw/2026-05-29_扫项目推荐自动化.md` <!-- VERSION_OK -->

### 2026-05-29 项目心智模型机制建立 by [MacBook-Pro-Opus 4.8 1M]

**主题**：itsuki 提元认知问题「AI 开新会话没有整个项目的样子，改前端不知道后端写到哪」→ CC 诊断「不缺文档，缺『对的文档在对的时候被读』」→ A/B/C 方案 itsuki 选 A → 落地：新建 `00_admin/项目心智模型.md`（7 节骨架 / 107 行 / 约 2-3 千 token：项目+5 端 / 系统怎么跑通 / 绑住 5 端的契约 / 5 端各自现状 / 核心不变量 / 未决问题 / 维护说明）+ `dmsd-startup` Step 3 扩成「读心智模型+WIP」开局自动读（v0.3.0）+ `session-wrap` 加「项 12 心智模型同步」收尾自动更（清单 11→12 项 + 修 §7.5.5 老错 8→12）+ project-overview §1.3 加 entry。代码核准后端签到：考勤主干已实装（present/late + 扣分 + WebSocket + 幂等），但防作弊核心（nonce / ECDSA 签名 / device 校验 / 卡→学生映射）后端一行没写 → 确认 TODO A-010「v1.0 上线最大隐患」。过程教训：CC 把 itsuki 模糊「没问题」当成「去查后端吧」+ scope 膨胀（填一行做成审一遍），被纠正当场认错 → memory `feedback_terse_confirm_not_blank_check.md`。**悬挂决策**：要不要给心智模型加启动硬挂钩（100% 保险 vs 现在指令级约 99% 稳，token 花费两者一样）。raw：`05_logs/raw/2026-05-29_项目心智模型机制.md` <!-- VERSION_OK -->

### 2026-05-28 启动 / 收尾流程改造 by [MacBook-Pro-Opus 4.7 1M]

**主题**：itsuki 让 CC 列启动 / 收尾流程 → 拍板改造。启动 skill（dmsd-startup）删 project-overview 漂移检测（移收尾）+ 5 件事砍到 4 件 + Step 4 改逐项打勾；收尾 skill（session-wrap）git 放宽（commit/bump/tag 自主 / push 明示 / reset --hard/rm 确认）+ 新增 §7.6 收尾终判（跑完说「可关 / 不可关」）；停 settings.json 启动漂移 hook；建死引用 memory `feedback_commit_push_tag_division.md`。撞 Claude Code 启动配置系统硬保护（口头授权清不掉 → itsuki 切权限模式）。AC：模式 5（工具安全边界）+ 模式 6（可逆性设计权限）。raw：`05_logs/raw/2026-05-28_启动收尾流程改造.md`

### 2026-05-28 点呼机硬件采购 + 「116 天磨穿」伪问题 by [MacBook-Pro-Opus 4.7 1M]

**主题**：itsuki「今晚把点呼机硬件全买好」→ CC 发现 5-22 海关查扣后日本本地选型（`hardware_design.md` §5.1'）还是「待选型」占位 → itsuki 给 5-19 调研的 4 家分工清单（秋月電子/Switch Science/Amazon Japan/ヨドバシ）+ 拍板方案 A 首单 1 台演示机（约 19,800 日元）→ CC 回填 hardware_design 4 处。CC 调 Codex（GPT-5.5 xhigh）审查报「ST25DV 每 10 秒写 EEPROM → 116 天磨穿」当致命问题，CC 原样转 itsuki 建议暂停 → **itsuki 一句常识推翻**：点呼非 24h 全天，只在时间窗刷（120~360 次/天）→ 寿命 7-22 年，116 天伪问题（Codex 算术对但前提错，CC 转述没审前提=失职）→ 写给第二个 AI 的提示词把坑写进去防再犯，第二 AI 确认伪问题 + 补 ST 官方手册引用。逐件核对截图选型（13 件）+ 教练答零基础问题（电阻/LED 多色/焊不焊/USB 喇叭供电）。决策：ST25DV ×4 / 风扇 5V 30×30×10 / 喇叭 USB 型 / 转接线 SparkFun Qwiic 套件 / 不买外壳 + SD 卡（已有）。AC 价值 ⭐⭐⭐⭐⭐：模式 2（AI 权威定量被常识推翻 顶级）+ 模式 4（多 AI 交叉验证）+ 模式 5（元认知立学习任务）+ 模式 3（5-22 海关查扣失败教训）+ 协作纠错（CC 没审 Codex 前提）。raw：`05_logs/raw/2026-05-28_点呼机硬件采购+116天伪问题.md`

### 2026-05-28 web 登录页修复 — 账号砍到1个 + 返回按钮改显眼 by [MacBook-Pro-Sonnet 4.6]

**主题**：compact 续接（前半段 f4a882f 已 commit）。itsuki 第一次实机打开新实名账户登录页，报 2 个 bug：①登录页 9 个账号「密码不知道」→ CC 查出密码是 `seed.py:39 DEV_PASSWORD = "123456"` 明文常量（itsuki 不知道有这个东西）→ 9 个假数据账号砍到 1 个「新股（寮務部長/全权限跨寮）」+ 备份旧数据库 + 重建 dev 库（seed 是幂等的：光改代码不动数据库 = 旧数据还在，必须重建）②密码页「← 別の先生を選ぶ」返回按钮「失灵」→ CC 用截图里「パスワードが違います(残り 2 回)」反推 React 确实活着（逻辑 OK），真因是按钮 fontSize:12+灰色+padding:0 点击区域极小 → 改蓝色背景+padding:8px 可见按钮。commit `01d0654`。AC：模式 2（假设崩→继续→真因）+ 模式 5（seed 隐藏常量 / 数据层 vs 代码层认知）× 2。raw：`05_logs/raw/2026-05-28_web登录页修复.md`

### 2026-05-28 宿舍申請实物表数字化 by [MacBook-Pro-Opus 4.7 1M]

**主题**：itsuki 提供宿舍真实纸质申请表「届け類.pdf」9 种扫描件 → 要求读懂 + 派 codex 双读对比 + 写进设计规范 + 实装（三步走）。CC 读 10 页 = 9 种表（帰省通常/長期 / 外泊日本人/留学生 / 学習欠席 / 行事企画 / 日課変更 / 冷蔵庫 / 物品所持）。codex（gpt-5.5）独立读图 3 次调用失败逐个修（参数贪婪吞提示词 → stdin / 目录信任 → skip / 只读沙箱）后双读核对**高度一致**。写进 `system_features.md` §7.2（出寮届補完）+ §7.3.5（补漏掉的在线学习申请类型）+ §7.21（新增 4 种全新表单）+ §8（数据模型 + 4 新表）+ IOS_DESIGN_LOG §14（别会话 commit 0ccd19d 带走）。itsuki 拍板 6 待决点：①日本人外泊含寮務部長（4人）②留学生帰省跟实物走（4人无国際交流部長）③帰国届有独立表「様式3-1 留学生・長期休暇」抬头**校長**→approver_role 加校長第7值 ④学習欠席一人审查 ⑤晚自习开始 19:40（实物 19:30 作废）⑥4 种新表都进 v1.0。实装 backlog 进 TODO §T。AC：需求工程（真实凭证驱动设计）+ 多 AI 交叉验证 + 发现现有设计缺口（学習欠席届只做半截）。本会话 commit：system_features + TODO（待 commit）。

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
