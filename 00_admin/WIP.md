# 当前工作状态 (Work In Progress)

> **最后更新**: 2026-06-07（**个人网站 Modal 改版 + 网页风格库 skill**——非 DMSD 核心、属个人站 + 全局 skill 活）：itsuki 让把「灯火」网页风格做成 skill → 对比 `anthropics/skills`（官方范例库）与 `VoltAgent/awesome-design-md`（73 大牌网站 DESIGN.md 合集）→ clone 合集到 `~/dev/awesome-design-md` + 自加 tomoshibi/modal 两份（73→75）+ 做成可调用全局 skill `web-design-styles`（删冗余 `tomoshibi-style` 合并成单一入口）。用 Modal（modal.com 云算力公司）风把 `pj.tomoshibi.cc` 首页重做成「全项目中枢」仪表盘（倒计时 + 4 项目状态 + 6 页面清单 + 慶應「待公布」占位卡 + 立体绿火苗主视觉），多轮推翻（嫌丑去套路 / 去重复逻辑 / 仪表盘当主页 / 扁平图标→立体玻璃火苗）后上线（原灯火版备份 `index.html.bak_pre_modal`）。慶應日期翻遍所有文件确认没有 → 不编、用「待公布」占位。**全是 VPS + 全局 + 独立仓库的活，DMSD 仓库只新增 1 个 raw 日志**。详见 raw `2026-06-07_网页风格库skill与Modal主页.md`，悬挂见 TODO §个人网站。**未 push**。早些 2026-06-06 早（**itsuki 反馈 5 件 → 全实装 + codex 2 轮复审收敛**：时区根治[后端写 UTC/读 +09:00 日本时间，新 `TZDateTime` 类型替 88 字段，推翻通宵 iOS 端「猜时区」治标修法] + iOS 包裹一览页接真后端 + 假数据 `#if DEMO` 守卫 + 老师网页宅配登记必选收件学生 + 前台列表男/女寮过滤 + 外出注释 + 自查修寮監挑学生 403。codex 第 1 轮 4 重大 3 次要 1 建议 → 逐条核实裁决修，第 2 轮 0 阻塞 0 重大收敛。后端 321 passed / iOS 双 scheme 编译过 / 老师网页 tsc 过。**未 push**）。早些 2026-06-06 通宵（**通宵 codex 4 轮对抗复审几个并行会话的混乱改动 → 0 阻塞 0 重大收敛，12 commit 未 push**）。早些 2026-06-05（**项目导览文档分层重构** — itsuki 提出要个让人/AI 深入理解整个项目的文件 → 排查发现 `PROJECT_GUIDE.md` 太简单 + `project-overview` 文件清单大漂移。扩 PROJECT_GUIDE 成深度版（170→约 270 行，加系统怎么跑通/核心业务概念/5 端契约/设计铁律/34 表数据模型/关键决策，定位为项目心智模型的展开详版）+ 全文件对账校准 project-overview 到 HEAD committed 1396（自带脚本 `check_overview_drift.sh` 验证 0 漂移；后端路由 11→26 / 测试 5→19 / 迁移 9→22 / 三端屏数 + 日志归档计数全校准）+ 清过时段（§9/§11/§12 → 指向 TODO）。commit `8193dae`（显式 pathspec 只带这两文件，未 push）。过程逮到暂存区被别会话污染（git ls-files 1388 vs HEAD 1396），改用 git ls-tree HEAD 锚定真值。详见 raw `2026-06-05_项目导览文档分层.md`）；2026-06-05（**代録表单收尾 + 老师网页迁 Vite 决策** — 杭田代録出寮届网页表单从无到有做完：后端新 `GET /applications/proxy-candidates` 搜学生接口(权限对齐代録 5 角色、补 admin 接口只给 3 角色的洞)+ 前端 `ProxyApplicationPage` 表单(字段照抄 iOS)+ 8 测试 + 设计档案三处同步；**三路审查**(CC 自审 + workflow 24 代理 + Codex)修一批 bug(错误提示路径/帰寮时刻只比日期/时区算今天/出租车独立时刻/注释假名等)，3 commit `e77dace`/`f3a846e`/`40de4e3`，pytest 295 全过。itsuki 拍板两件：① 老师网页 HTML 单文件→**React+TS+Vite**(界面 100% 冻结、吸取 5-26「不是我的 web」失败教训，施工清单 `03_dev/teacher_web/Vite迁移_施工清单.md` + GOAL 提示词 `00_admin/老师网页Vite迁移_GOAL提示词.md` 已写、**未开工**等 compact 后执行)② 邮件 SendGrid→**Resend**(永久免费、待 itsuki 注册拿密钥)；详见 raw 2026-06-05 + decision_log 2 条）；早些 2026-06-04（**AC 升学素材体系大重构** — 旧四级流水线「人工精选」闸门空转 + 两校各存一份 → 重构成「两校共用原始池」：建 `大学入試/00_原始素材池_两校共用/` 迁 75 素材 + 两校侧重组 `03_按X口味提炼/04_产出/99_证据截图` + 改 6 脚本指向新池 + iCloud 根建统一归档区 `99_归档/`；同会话早段 iOS 黑屏诊断 / 外部 AI 评估 / 统一两个根目录都已归档；**同会话后段** 再按重要度二次重构成四层（1自动产出/2我挑的/3最重要/4金句）+ 改 4 脚本指向 + CC 全读 8.6 万字会话写 3 总结文件归位；详见最近会话顶条）；早些 2026-06-04（**项目协作机制讨论** — 启动维持 skill 不上 hook / 心智模型 §4 砍掉跟 WIP 的重叠（只标成熟度档位）/ 新建 `codex-review` skill；详见「最近会话」顶条）；早些 2026-06-03（**版本号回溯规范化** — 把 5-11~6-02 一个多月的 236 commit 按语义化版本（SemVer）一次性补了 6 个版本标签 v0.8.1~v0.12.0 + CHANGELOG 6 个条目，当前版本从 v0.8.0 升到 v0.12.0；历史标签全保留不动 / 未改代码 / 未 push；详见 raw 2026-06-03）；早些 2026-06-02（**IX-034 请假计数接后端 `e0c150c` + 过夜无人值守 GOAL 设计**——详见最近会话顶条；早些 2026-05-31 **teacher_web v1.0 全实装 + codex 5 轮复审收敛** — itsuki `/goal`「老师网页做到能直接上线 v1.0」超长自主会话八波施工：摸底(4 并行 agent)→修 7 后端 bug+网页接 13 死接口→建学生账号管理→删 demo+生产配置→**6 大模块全建**(行事予定/巴士/指導履歴/事案/个人档案聚合/一括进级 + push 骨架，各后端建表迁移接口测试 + 网页 UI)→W8 自审 30+ 问题→**codex 独立复审 5 轮到它自己说「0 blocker 0 major 可上线」**(寮边界系统性补齐是第 4 轮挖出)。后端 193 测试 / 前端 check_jsx 0 错。收尾写 NFC 防代刷立项 + 上线部署清单。24 commit **未 push**。AC 模式 2+5+6 + 教训「独立验证 agent 自报」。详见 raw `2026-05-31_teacher_web_v1.0全实装+codex5轮收敛.md`）；早些 2026-05-30（session-coord 多窗口协作板改 hook 后台自动维护 — 详见「最近会话」顶条 + `raw/2026-05-29_session-coord自动化.md`）；早些 2026-05-29（项目心智模型机制建立 — 新建 `00_admin/项目心智模型.md` AI 开局必读骨架 + 挂进 dmsd-startup/session-wrap，详见「最近会话」顶条 + `raw/2026-05-29_项目心智模型机制.md`）；早些 2026-05-28（点呼机采购清单 HTML 会话 — itsuki「做个 HTML 含购买清单+点呼机信息 / 我发的链接你确认了吗 / 图片塞进去可折叠」→ CC 用 WebFetch 逐个抓 itsuki 发的采购链接核对，揪出截图看不出的坑：风扇链接 `B0DYV31FJZ` 是 12V（Pi 只有 5V 转不动）+ 喇叭链接 Apqfw 和截图 HONKYOB 对不上 + 蓝 LED 漏链接 + 杜邦线买重 + PN532 链接 500 抓不到。做 `03_dev/rollcall_device/点呼机采购清单.html`（6 块：目的与效果/机器组成原理/下单前提醒/采购清单带可点链接/接线速查/16 截图折叠区）+ 16 截图复制进 `采购截图/` + project-overview §5.8 点呼机 11→12 文件 + TODO §R 加「🔥 下单前必确认」8 条高优先。AC：主体性 + 交叉验证「不假设链接=需求」，早段 116 天伪问题的正面版）；早些 2026-05-28（iOS 申請界面实装会话 — itsuki「接着做 iOS app 实装 → 派 codex gpt-5.5 xhigh 干活 / CC 规划+审查」。两轮 codex：① 出寮届扩展 + 帰国届校長链修 + 4 新申请界面（在线学习/行事企画/冷蔵庫/物品所持）+ 网络层 ② 补 3 个「我的提交列表」。CC 审查不盲信 codex 自报：codex 沙箱跑不了 iOS 真编译只能语法解析 → CC 独立 `xcodebuild` 抓到 2 个 codex 查不出的 `Field` 参数顺序错 + 修。后又修演示版回归：codex 跑 `xcodegen generate` 擦掉了手动配的 Demo 编译配置 → CC 写进 `project.yml`（Debug/Release/Demo + 独立 bundle id 区分正式/演示 + DEMO 开关 + 2 scheme）永久 regen-safe；itsuki 演示需求：房间号 A5 + 注册第五步认证码预填「000000」用 `#if DEMO` 包（顺带解决 A-035 生产后门）。正式版+演示版都 `BUILD SUCCEEDED`，演示版装模拟器跑起来验证（启动页 v1.0.0-demo + 登录预填）。未做：6 新界面逐屏运行点查（无模拟器点击工具）留 itsuki 手走。改 8 文件+新建 4 文件+配置 2 文件，**未 commit/push**。AC 模式 2 + 多 AI 协作顶级）；早些 2026-05-28（点呼机硬件采购夜会话 — itsuki「今晚把点呼机硬件全买好」→ CC 发现 5-22 海关查扣后日本本地选型还是「待选型」占位 → itsuki 给 5-19 调研 4 家分工清单 + 拍板方案 A 首单 1 台 → CC 回填 `hardware_design.md` §5.1'/§4.2'/§4.6/§0；CC 调 Codex GPT-5.5 xhigh 审查报「ST25DV 每 10 秒写 EEPROM → 116 天磨穿」当致命问题，CC 原样转 itsuki → itsuki 一句常识推翻：点呼非 24h 全天刷，只在时间窗（120~360 次/天）→ 寿命 7-22 年，116 天伪问题（Codex 前提错，CC 转述没审前提=失职）→ 写给第二个 AI 提示词把坑写进去防再犯，第二 AI 确认 + 补官方手册引用；逐件核对截图选型 13 件 + 教练答零基础问题；决策 ST25DV ×4/风扇 5V/喇叭 USB/转接线 SparkFun Qwiic 套件；产出 hardware_design 回填 + TODO §R 学习任务 + 新建 `rollcall_device/点呼机接线说明.md` + project-overview §5.8 + 2 份外部 AI 审查提示词）；早些 2026-05-28（申請表后端实装会话 — itsuki 拍板「申请表规范改动全落实 → 派 codex gpt-5.5 思考等级 xhigh 干活 / CC 写详细提示词负责规划 / codex 改完 CC 审查」。CC 写 6 节自包含提示词 → codex 后台 workspace-write 实装后端（`applications` 加 6 实物字段 + `approver_role`/`teachers.role`/`CROSS_DORM_ROLES` 加「校長」+ `approval_chain.py` 4 处链修正 + 新表 `study_online_requests` + 4 张生活申请表 dorm_event/schedule/fridge/item + 新路由 study_online.py/dorm_life.py + alembic `d2e3f4a5b6c7`）→ CC 审查不盲信：逐个 diff 8 个越界文件诊断为「测试套件早坏（引用不存在的 `StudyAttendanceRoster`）+ `pyproject.toml` 弃用即报错策略」逼的、非乱改 / 独立重跑确认 70 测试通过 / 临时配置造真正空库复验 10 个迁移全链路 upgrade-downgrade 通过。commit `c6ccee0`（17 文件 +1325/-67）。itsuki 拍板：校長保留 A「实物有校长就要校长」+ iPhone 进 TODO §T 标「下一步立刻做」+ 安卓/老师网页暂不走 + 开发库不 stamp。AC 模式 2+6 顶级。早段（跨夜会话 — 主体在 5-27 晚段-3：老师实名账户登录改造 + 砍匿名建議 + codex 5.5 xhigh 审查；起因：itsuki 看到 web 登录页 501 错误 → CC 诊断双服务器分离 → itsuki 顺势拍板老师登录从「共用密码」改成「实名账户列表→选名字→输密码」+ 加教师创建/删除管理页 + 砍残留匿名建議 + 拍板「老师登录跟学生登录没关系」纠正 CC 默认对齐 iOS 路径 +「做完后 codex 审查 5.5 xhigh」。CC 4 commit 落地：`b9f237c` backend（CORS + auth.py teacher_id 形式 + 3 schema + teachers.py 3 新接口）+ `b444aad` frontend（LoginScreen 完整重写 2 屏合一 + TeachersAdminPage 新建 + 砍 anon tab + 3 假数据）+ `1904b18` 5 个设计档案同步 + `aba0659` codex 审查修 3 🔴 阻塞（timedelta import 缺 prior bug / INVITE_ALLOWED_ROLES 给「学習担当」越权 / 没拦最后一个 admin = 系统 lockout）+ 关键 🟡/🟢。剩余 4 项 itsuki 决策 / 大工程进 TODO §🚀-G。AC 价值：模式 1+2+5+6 顶级 × 4。早段 — teacher_web v1.0 凌晨深夜推进收尾会话 + 醒后 backend 自审 9 处修复：itsuki 启动「审查我做的事到底做好了没」+「不要停下来问 / 不需要决策的直接修 / 决策的加 TODO」→ CC 自查 5 维度：alembic migration ✅ / 13 router 注册 ✅ / 61 endpoint 真 import 通过 ✅ / Student.is_demo 字段已加 ✅ / client.js 32 helper 跟 backend 路径 100% 对齐 ✅ / 5 处 index.html 日语注释中文化（中文铁律）/ 全部 9 处真 bug 已在凌晨别会话修完。早些深夜-3 — iOS 全自主审查 + 修 + 收尾会话：itsuki 启动「审查这个 iOS APP 看有什么问题，然后去做去修」+「做完后就直接收尾，不要给我留问题，也不要停下来问我，所有的问题加到 todo 里面」→ CC 5 维度过完 41 文件 / 修 1 处（`MyPageStubs.swift:1404` `c.score!` force unwrap 改 `map ?? _`）/ 2 处架构性问题写 TODO §D（`StayListStubs.swift:475` catch 降级 mock 假数据 / `MyPageStubs.swift:1637` 暴露 `localizedDescription`）/ 所有 demo 后门 + A-XXX bug 标记 + NFC UI + 其他 catch 全部确认 ✅。早些深夜-2 — 跨天会话「2026-05-25 晚段-2 / AC 学习内容清单 v0.1.0 起草」收尾：5-25 晚 itsuki 抛元认知反思「5 端开发但一门语言都没掌握 + 文件认不全」+ 主动要求扩充「专业知识 + 项目底层运转逻辑」→ CC 起草 `06_assets/学习内容清单.html` v0.1.0 9 章（工程层改动被 5-26 晚段-4 别会话 commit `3d945a7` 顺手带走）+ 列 4 章扩充大纲（第 9-12 章）等拍板 → itsuki 直接说「收尾」未实装 → 加 TODO §🛠️ §M 6 条悬挂任务 + raw `2026-05-25_AC学习清单起草.md` 4 段深度 AC 素材；模式 5 顶级 × 2。早些 2026-05-27 深夜 — itsuki 让 CC 清 TODO 里「不需要决策 + CC 自己能做 + 不重要」的小活清单 14 件<!-- VERSION_OK --> + project-overview drift 修：6 件本来就闭合 TODO 没刷状态（T1 3 文件已归档 / T2 .DS_Store 删 / T3 临时PDF 目录已不存在 / T7 DESIGN_BRIEF 5-26 已重写 / T8 DEVICE_REGISTRY §6 已是 dorm-1/2 / T9 FC-025-028 已标 ✅ N/A）+ 7 件真做（T4 99_archive README 时间戳 / T6 WEB_DESIGN_LOG §7+§10 路径过时项 / T11 project-overview §6.2 raw 48→55 / T12 SC26 session-wrap §7.5.5「6 项」→「8 项」/ T13 全局环境清单 DMSD Skills 7→8 加 dmsd-startup / T14 WIP 最近会话 10→5 砍 5 条 / T15 §0.1 体量表全刷新 1181→1189）+ 2 件挂起待 itsuki 拍板（T5 backend 表数 13→21 + P0/P1/P2 分级标准 / T10 系统bug专栏 77 条状态字段工作量大）；起因：itsuki 启动「列 TODO 里不重要 CC 自己能做的小活」+ 说「做完后直接收尾，想 commit 就 commit」。早些 2026-05-26（晚段-4 — teacher_web Vite + TypeScript 实装版整体废弃 + Ryō polish 试做被回滚 + 修破工具脚本 demo_server.py 死链改 python http.server + 文档同步 WEB_DESIGN_LOG §12 + DESIGN_BRIEF + v1/README + 物理清 node_modules 81MB + dist + decision_log 加 2 条；起因：itsuki 启动「推进 teacher web」+ 看到 Vite 实装版怒怼「这他妈根本不是我的 web」拍板「垃圾归档用 B」+ frontend-design skill polish 试做整体不喜欢一句「回滚」全退。早些晚段-3 — iOS demo 后门清理（做法 B）+ 字段对齐零漂移 commit `7521bf8`。早些晚段-2 — 全项目中枢机制立项 + DMSD 注册档案 + DMSD CLAUDE.md 加「全项目中枢联动」段；同时合并早段 iOS Bot 1 复查 + 暗夜模式 v2 + 3 上架配置归位 + memory 加铁律「TODO 关条目不要问」入「最近会话」。早段头：启动 SOP 集中化 — 新建 `.claude/skills/dmsd-startup/SKILL.md`（5 件启动必做事）+ 全局 `~/.claude/hooks/session-start-coord-check.sh` 在 DMSD 项目下静默退出 + DMSD CLAUDE.md「会话开始」段简化引用新 skill + 6 项目 CLAUDE.md 加「不主动用英语名词」规则段 + project-overview SKILL.md §0.1 + §1.7 同步 + 本文件「会话开始」铁律改成走 dmsd-startup skill）。5-25 晚段（追加：第三轮升级 — anti-ai-flavor 加第 3 触发词「**翻车**」单字 + 新建 `inbox.md` — itsuki 收尾中途立项自我迭代机制：发现新翻车点 → CC 按 5 字段「原文 / 6 类归类 / 违反铁律 / 根因 / 修正版」记 inbox，未来批量整理合并到 `references/翻车案例库.md`；改 5 文件：新建 `inbox.md` + SKILL.md 加 §7.5 + CLAUDE.md 触发词 2→3 + hook 提醒 + `我的环境.md` + `.html`）。早些（同晚段）：anti-ai-flavor HOW_TO_TALK.md 立项 + 跨 3 项目 session-wrap 加项 11/8 — itsuki 给 16 个翻车原句证据 → 4 根本问题 + 9 类细分 → 5 条总结铁律 → 方案 B 落地：SKILL.md 反面自检 + HOW_TO_TALK.md 正面教学互补 + 2 触发词「说人话」/「单词白名单」+ DMSD/SC26/Tango session-wrap 收尾清单同步加「全局环境清单同步」项 — 全局 6 文件 + DMSD 1 文件 + 2 memory + SC26 1 文件 + Tango 1 文件。早些 5-25（drift 脚本 bug 修 + 全局 `session-coord` 三层保险落地 — DMSD 2 文件 + 全局 4 文件 / 全局 Hooks 4→5；同时补登 5-24 iOS bug 批量修复会话遗漏的收尾）。早些 5-22（**3 会话产出** — ① 早 project-overview §0.1 漂移 957→980 / ② 中 iOS fork 融合归档 commit `46f779c` / ③ 晚 点呼机推进 + 撞海关查扣事件 + 立项 `session-wrap §5.5.15 decision-draft`）。早些 5-21（5-20 凌晨 4 会话审查作战 cron 自动 fire 产出 131 条 findings / 5-21 加系统 bug 专栏 + 第一批修复 8 条）。早些 5-19（project-overview 大改造 + 防漂 C 方案）。<!-- VERSION_OK -->

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

**当前版本**: v0.15.0 <!-- VERSION_OK -->（2026-06-05 把 6-03/6-04/6-05 三天 80 commit 按天切 3 个 minor v0.13.0~v0.15.0；三端客户端版本号同步 0.15.0，详见 CHANGELOG 顶部）
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

### 2026-06-06 早 itsuki 反馈 5 件 → 实装 + codex 2 轮复审收敛 by [Opus 4.8 1M · ultracode]

- itsuki 看通宵报告后对 5 件提反馈转任务：① 时区（否决通宵 iOS 端「猜世界时」治标修法，要「直接带时区、默认日本时区」）② iOS 包裹一览页假数据 demo 留着但生产别漏 + 后端做完两端对齐 ③ 老师网页宅配登记必选收件学生 ④ 前台列表按男/女寮过滤 ⑤ 外出注释清理。
- **时区根治**：实测挖出真乱源——SQLite 读回丢时区、且不同字段存的时区不一样（点呼按日本时间存 / created_at 按世界时存）。新建 `database.py` 的 `TZDateTime` 类型（写入统一存 UTC、读出统一 +09:00 日本时间），`models.py` 88 字段替换，一处全解。**逮到方法名坑**：第一版写 `process_bind_value`（错），SQLAlchemy 认 `process_bind_param`，名字错会静默不生效（造成「读对写不对」），逐层 debug + 内省 `_has_bind_processor` 定位。
- iOS 包裹一览页/MyPage/履历三处 `#if DEMO` 守卫（生产接 `/front-desk/mine`）+ 新建共用 `PackageDisplay` + 路由 id `Int`→`String`；老师网页宅配 Modal 加学生搜索选择器（必选）；后端前台列表按 `dorm_units_for_teacher` 男女寮过滤。
- **codex 第 1 轮**：4 重大 3 次要 1 建议 → 逐条核实裁决修（auth 学生封锁剥时区差 9 小时是我 TZDateTime 引入的真回归 / iOS 5 状态映射 / 老师网页终态显示 / MyPage badge 假数据 / 日期时区 / 注释）。**CC 自查逮到 codex 没提的真 bug**：寮監登记宅配搜不了学生（403）→ 新增 `GET /front-desk/students` 专用接口。**第 2 轮 0 阻塞 0 重大收敛**。
- 验证：后端 321 passed（+3 新测试）/ iOS 双 scheme BUILD SUCCEEDED / 老师网页 tsc 过。**未 push**。AC：模式 2（多 AI 对抗复审 + 不盲信 + 自查逮 bug）⭐顶级 + 调试纪律（方法名坑实测定位）。raw `2026-06-06.md`。

### 2026-06-06 通宵 codex 4 轮对抗复审几个并行会话的混乱改动 by [Opus 4.8 1M · ultracode]

- itsuki 睡前甩几个并行会话累积的混乱未提交改动（iOS 推送/包裹/外出/契約書 + 后端新端点 + 文档），要 CC 通宵审 + 扣 codex + 修 + 审到 codex 没话说 + 早上一次性列。
- 先建基线（iOS 生产+演示双版本 BUILD SUCCEEDED + 后端 pytest 318）+ 读懂全部未提交改动。CC 自己先挖到**系统性 datetime 解码坑**：dev 用 SQLite，`DateTime(timezone=True)` 读回是无时区裸时间，iOS ISO8601 解码器要带时区 → 公告/申请/晚自习/点呼约 25 个 Date 字段解码整段失败。python + Swift 双实证后，在唯一解码入口 `decodeISO8601Date` 加 UTC 兜底**一处全修**。
- **codex 5 轮（4 实质 + 1 确认）跑到收敛「0 阻塞 0 重大」**。共修：datetime 解码兜底 / 设备令牌切换用户重报 / 并发注册幂等 / 包裹通知 id 防撞 / **冷启动恢复令牌没同步 APIClient**（Swift `init` 内赋值不触发 `didSet`，自写 Swift 实证 + 代码注释原本写反）/ 宅配登记必填收件人 + 空串归一化。
- **不盲信 AI 三处**：codex 说 ruff 删了我的 import → 读真文件证实（自己两步 Edit 又踩 ruff 坑）；codex 说 didSet 不触发 → Swift 实测证实 codex 对；codex 说包裹专属页读 SEED → 核实判定「早先半成品非本批 bug」记 TODO 不盲改。
- 12 commit 全本地**未 push**，全程精确 pathspec、零卷入隔壁活跃会话的 teacher_web tsx。README 顺手刷新到当前版本（去掉原本写死的旧版本号 + 老师网页 Vite 叙述对齐 CHANGELOG）。
- AC：模式 2（多 AI 对抗复审 + 假设验证）⭐顶级 + 验证纪律。raw `2026-06-05.md` 末尾通宵段。

### 2026-06-05 VPS 部署排查 + 个人网站整理 + 仪表盘自动更新 by [Opus 4.8 1M]
- itsuki 要部署后端+网站 → 排查发现两者早在 Google Cloud（`34.85.74.70`）上线 3-4 周（Docker：Caddy+FastAPI+PG），三域名全在线；纠正「VPS 停用」陈旧记忆
- 抢救 4 个部署配置进 git（commit `c91d7e7`）；**提交前逮到 `reseed_reviewer.sql` 含 Apple 审核员明文密码**，拦下没进公开仓库
- 整理 VPS（删旧备份+nginx残留+Docker缓存 846M）；撤 pj.tomoshibi.cc「项目总览」「文件总览」（移 `_offline_pages/`）
- 仪表盘：修 frozen 倒计时 bug（改日本时间实时）+ 数据刷今天 + 建一键生成器 `生成仪表盘.py`
- 后端重新部署 Mac→VPS 方案就绪，itsuki 说「先别动」（app 闲置）；新 3 memory（vps-production / release-status / external-state）
- 详见 raw `2026-06-05_vps部署排查与网站整理.md`

### 2026-06-05 老师网页 Vite 迁移收尾 + 版本号 v0.12.1+v0.13~v0.15 + handoff 文件夹 by [Opus 4.8 1M · ultracode] <!-- VERSION_OK -->（当前版本见 CHANGELOG.md 顶部）

- **老师网页 Vite 迁移全做完**（compact 后接施工清单 §8）：修后端 dev 库 alembic revision 撞号（`b2c3d4e5f6a7` 重复 → 改 `f8a9b0c1d2e3` + 重建库）→ chrome 客观实测 17 页全渲染 + 27 接口全 200 + 0 报错 + 真数据通 → `启动老师网站.command` 切 build dist + 旧 HTML 单文件版归档 → 收尾 6 文档。后端 311 测试过。**仅剩 itsuki 肉眼签收 + push**。
- **版本号**：6-03~6-05 三天 80 commit 按真实 commit 顺序切 `v0.12.1`(patch 纯修复) + `v0.13.0`/`v0.14.0`/`v0.15.0`(minor)，三端客户端版本号同步 0.15.0，4 个本地 tag。itsuki 借此搞懂语义化版本(SemVer) patch(修订号)概念。 <!-- VERSION_OK -->（历史记录，当前版本见 CHANGELOG.md 顶部）
- **handoff 文件夹机制**：itsuki 拍板交接件不该堆 00_admin 根 → 建 `00_admin/handoff/`(只放活的) + 用完移 99_archive + session-wrap §5.5.9.5 自动清理 + 旧 5 个交接件全归档到 `99_archive/2026-06-05_handoff已完成/`。
- **同步修 3 处旧描述**（防新会话被误导）：teacher_web `README.md` / `DESIGN_BRIEF.md` / 本 WIP 把老师网页从「standalone HTML / 未开工」更新到「Vite 已完成」。
- 全本地未 push（这天累计领先远程 336 commit）。AC：模式 2（撞号假设修正）+ 模式 5（itsuki 学 SemVer + 自悟 handoff 治理结构）+ 方法论（chrome 客观验证）。raw `2026-06-05_teacher_web_vite迁移.md`。

### 2026-06-05 学年更新/学生自设番号 五端 + iOS 16 + 对齐文档 + codex 两轮 by [Opus 4.8 1M · ultracode]

- itsuki 实机审 iOS 问「番号年年变，登录不方便？」→ CC 查出**这事 4-30 已拍板「老师改/学生只读」**、跟今天说的相反 → itsuki **当场翻自己旧决定**改成学生自设。CC 主动挖 4 坑（撞号/鸡生蛋/高3毕业/误输）itsuki 逐个拍板。
- 五端实装（Workflow 4 agent 勘察 → 串行）：后端 `needs_renewal` 列+迁移+开闸/自设/进度/单件改+R4（308 测试）+ iOS 顶部横幅+弹窗 + 老师网页 开闸+分组折叠列表+进度+单件改+4/1横幅。**Android 不碰**（itsuki 怒「别动安卓」，归别会话）。
- **iOS 最低支持 26→16**：编译器报错逐个修（symbolEffect/onChange两参数/Canvas Text.foregroundStyle）+ 新建 `ViewCompat.swift`，双 scheme BUILD SUCCEEDED。
- **iOS↔Android 对齐交接**（Workflow 11 agent 读 iOS 真代码）：`00_admin/iOS_Android_对齐规格.md` 3068 行 + `00_admin/iOS_Android对齐_GOAL提示词.md`（itsuki 教 /goal 用法后重写成可测量终态+40 轮刹车）+ `06_assets/app_screens_2026-06-05_ios/` 14 截图清单（PNG 待 itsuki 拖入）。
- **codex 两轮**：① 4 major（R4 缺失）CC 先怀疑前提→查实 codex 对（管理係不在 CROSS_DORM_ROLES）→全采纳修+补 3 测试 ② `dorm_units_for_teacher` 共用函数 fail-open，CC 裁决出范围→记 TODO 给 itsuki 拍。不盲信 AI 双向。
- 10 commit 全本地**未 push**。AC：模式 2（不盲信 AI ⭐顶级）+ 5（翻旧决定 / 学 /goal）+ 6（取舍）。raw `2026-06-05.md` 会话 B。

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
