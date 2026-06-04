# 决策变更记录

> 记录项目的版本级/方向性重大决策。
> 单文件追加式,最新的决策放最上面。
> 面试前快速调取决策脉络用。

---

## 格式模板

```markdown
## YYYY-MM-DD — [决策简述]

**之前的决策**: ...
**新的决策**: ...
**为什么改**:
1. ...
2. ...
**这个改动影响了什么**: ...
**事后回看**(几个月后补填): 这个决定对吗?
```

---

## 决策记录(倒序)

## 2026-06-04 — 会话协作机制三项调整：启动维持 skill / 心智模型与 WIP 分工 / codex 审查做成 skill

**之前的决策**:
- 启动 SOP 靠 `dmsd-startup` skill（CC 每次开会话自觉加载），曾考虑改成开窗自动跑的 hook。
- `00_admin/项目心智模型.md` §4 与 `WIP.md` 都在维护「5 端现状」，两处重叠且 §4 长期过期。
- 「派 codex gpt-5.5 xhigh 审查」是高频手动工作流，没有专属 skill。

**新的决策**:
1. 启动**维持 skill 不上 hook** —— 只要 itsuki 记得每次说「启动」，skill 功能等价于 hook，差别只是「靠人记得」vs「机器强制」。
2. 心智模型 §4 **只标成熟度档位 + 一句话定位**，细节进度归 WIP；当前焦点留 WIP。两文件按「慢变量（架构骨架）vs 快变量（流水账）」分工。
3. 新建 `codex-review` skill 固定审查循环（gpt-5.5 xhigh 只读审本会话改动 → CC 逐条裁决+修 → 复审 → 跑到收敛 / 不带「codex」字样不触发）。

**为什么改**:
1. itsuki 自己想通「机制兜底优于自律」铁律针对的是 CC 反复忘，触发权收回自己手里后不适用 → 不必为省一句「启动」上 hook。
2. 把变化频率不同的东西分开放：快变量混进慢变量文件会导致反复改动、易误改、且 §4 那种细节进度必然过期。砍重叠同时治好漂移。
3. codex 自报不可信 / 前提可能错 / 沙箱编译不了 iOS —— 把「CC 当审查的审查者」沉淀成可复用流程，比每次口头交代更可靠。

**这个改动影响了什么**:
- `00_admin/项目心智模型.md`（§4 重构 + §7 维护说明）+ `.claude/skills/session-wrap/SKILL.md`（项 12 对齐）+ 新建 `.claude/skills/codex-review/SKILL.md` + `CLAUDE.md` skill 表 + project-overview 清单。
- 以后心智模型 §4 只在「某端成熟度跳档」时更新，普通进度只动 WIP。

**相关**: `05_logs/raw/2026-06-04.md`（深度 AC 素材 + 模式 5 顶级 ×2 / 模式 6 ×3 / 模式 2）

**事后回看**(几个月后补填):

## 2026-06-02 — ST25DV 架构反转：手机从「读」贴纸改「写」贴纸

**之前的决策**: 路径 B（手机签到）= 点呼机每 10 秒往 ST25DV16K 写一个带 nonce（一次性随机码）的签到 URL，学生手机**读**贴纸拿 URL → 唤起 App → ECDSA（椭圆曲线签名）签名 → POST。防代刷靠「nonce 10 秒失效（防 URL 复制远程代签）+ 手机私钥签名（防伪造）」。

**新的决策**: 反过来 —— 学生手机 App 把身份数据**写**进 ST25DV 的 Mailbox（邮箱缓存），点呼机（树莓派）被动收、I²C 读走、发后端。点呼机不再刷 nonce。

**为什么改**:
1. itsuki 找 AI（Gemini）补点呼机硬件原理课，学着学着自己发现旧方案有矛盾（「我也不记得为什么之前要不断往 ST25DV 写数据」），回到第一性原理重想
2. 反转后学生手机只做近距离 NFC 写、**彻底不需要网络**（飞行模式可签到），解决「学生流量卡/没网」痛点
3. 系统复杂度减半：砍掉「点呼机每 10 秒向后端拿 nonce + 拼 URL + 写 EEPROM」整套动态逻辑
4. 顺带消灭 5-28 Codex「ST25DV 每 10 秒擦写、116 天磨穿」伪问题 —— 新方案手机写的是 Mailbox（临时缓存，不耗 EEPROM 擦写寿命）

**这个改动影响了什么**:
- 硬件真值 `hardware_design.md §2.3` 已改（本条配套，同 commit）
- **防代刷其实简化了（CC 初判「断链/三缺口」被 itsuki 当场纠正 — 详 raw 2026-06-02 §9）**：手机不联网、只有点呼机跟后端通信 → 旧 nonce+URL（防手机远程 POST）在新架构不需要了，攻击面变小。代刷只剩「到现场」一条路 → 靠「播报 + 老师看脸」防（4-12 既定）+ v2.0 人脸自动化。
- 真正要做（跟反转无关、本来就要做）：点呼机↔后端 HTTPS 加密 + 点呼机设备密钥认证
- 实体卡 UID 克隆是老问题（NTAG424 DNA 已在 TODO）
- 连带文件待简化（非紧急）：`flow_design.md` / `NFC防代刷_后端立项施工计划.md` / `system_features.md` / `ROLLCALL_DEVICE_DESIGN_LOG.md`
- 暂不升版本号（代码未实装）

**认知闭环（AC 素材）**: 2026-04-12「语音播报设计」条已写「手机可借朋友、都绕不开代签 → 攻击者必须本人到场 = 技术+人组合」→ 4-20 加 nonce+ECDSA 技术防 → 6-02 反转后技术防部分断链、防代刷又回到「人看脸」这条线 + v2.0 用人脸识别把「看脸」自动化。绕一圈印证最初判断：纯技术验证不了「人」，最终要靠生物特征。

**事后回看**(几个月后补填): —

---

## 2026-05-31 — IX-008 iOS 当前用户接后端：currentUser + displayUser + SEED.user 安全网（不逐改 73 处）

**之前的决策**: iOS 各页 73 处直接读写死的演示假用户 `SEED.user`（リュウ イヒ / A5 / 4.5分）。
**新的决策**: AppStore 加 `currentUser`（登录拉 `GET /students/me` 填）+ 计算属性 `displayUser = currentUser ?? SEED.user`；loadMe 同时把真实用户**写回全局 SEED.user 当安全网**，覆盖 ~60 处没法用 app 的站点（@State 默认值 / mock / 静态 helper）；登出复位 demoUserSeed 防残留。只把高可见站点（HomeStubs）转 displayUser。
**为什么改 / 选这个**:
1. 调研发现 `User` 结构混了身份+统计+flag 三类，`/me`（StudentProfileBasic）只给身份 → 「73 处一把换 displayUser」不成立（@State 默认值用不了 app、统计字段 /me 没有）。
2. 纯全局突变（只改 SEED.user）有 app 重启时序 + 不响应式刷新问题；纯 displayUser 要逐改 73 处且 @State/mock 改不了。→ 取中间：displayUser（响应式，高可见处）+ SEED.user 安全网（长尾兜底）。
3. 符合代码里已写的 `isAuthenticated` 门控设计意图（登录后真实 / 否则占位）。
**这个改动影响了什么**:
- 统计字段（points/迟到/欠席）/me 给不了 → 真人先显 0（itsuki：4.5 是 demo 数据），扣分接入 = IX-008b
- isStudyTarget 默认 false（itsuki：老师后台手动设的才是学習対象）+ UI 入口不隐藏 + 详情页显「学習対象外です」
- 后端 StudentProfileBasic 加 category（/me 给 iOS）+ 新 GET /students/me
- 残留风险：SEED.user 全局突变 = demo-scaffold 式做法，语义略混；登出已复位。IX-008 的 Codex 独立审查因额度耗尽待补
**相关**: `05_logs/raw/2026-05-31_ios接后端_IX004收敛+IX008用户资料.md` §3（设计决策 + 模式6）
**事后回看**(几个月后补填):

## 2026-05-27 — teacher_web 老师登录方式：共用密码 → 实名账户（列表 → 选名字 → 输密码）

**之前的决策**（demo 期遗留，与 4-30 §3.4 拍板矛盾）: web 实装 = 共用账户「tomoshibi」+ 共用密码 + 登录后 SelectTeacherScreen 中间页选「今日担当者」。所有老师共享 1 个密码。但 backend `Teacher` model 4-30 之前就已经是「每老师独立 login_id / password_hash / failed_count / locked_until」结构 — web 端 UX 简化造成的实装漂移。

**新的决策**: 实名账户登录方式。LoginScreen 2 屏合一：
1. 屏 1 = 调 `GET /teachers/public`（无认证、只返 id+name+assigned_dorm+last_login_at）列男寮/女寮老师卡片
2. 屏 2 = 选中老师后输该老师密码 → POST `/sessions/teacher` 用 `teacher_id` (UUID) + password
3. 砍 SelectTeacherScreen 中间页（实名账户登录后身份已确定）
4. 新建 TeachersAdminPage（Shell nav 加「教員アカウント管理」入口，仅寮务管理 3 角色可见），支持创建（name + login_id + email + 初始 password + role + 担当寮）+ 删除（自删拦截 + 最后一个寮务管理角色拦截 LAST_ADMIN）

**为什么改**:
1. 修违反 §3.4 已拍板（4-30）的漏洞 — 「役职・寮監・寮務部教师 = 每人单独账号密码 R3」+「前台不允许自助注册任何教师账号 / 必须先用已存在的教师账号登录 → 后台加 / 删」。demo 期共用密码方案直接违反这两条
2. 实物事实优先 — 真实学校就是每老师 1 个账号 1 个密码。「新宿管来了就加，离职就删」是学校实际人事流程。共用密码 ≠ 学校真实
3. itsuki 拍板「老师登录跟学生登录没关系」— 不要从 iOS 学生流程对齐复用。老师 vs 学生是 2 个独立的设计空间（用户群 / 验证方式 / 登录入口 / 设备共用度都不同）
4. 安全性 — 共用密码 = 单点泄漏全员失守 / 共用账号没 audit log（不知道哪个老师操作的）。实名账户 = 个人责任 + 操作可追溯

**这个改动影响了什么**:
- backend `teachers.py` 加 3 个接口（GET /public 无认证 / POST 创建 / DELETE 删除）+ 引入 `TEACHER_ADMIN_ROLES = {寮務部長, 寮務課長, 寮監}`（不含学習担当）
- backend `auth.py` POST /sessions/teacher 支持 `teacher_id` (UUID) 或 `login_id` 登录（前者新增、后者 backward-compat）
- backend `schemas.py` 加 `TeacherPublicOut` / `TeacherCreateIn` + 改 `TeacherLoginIn`
- frontend `index.html` LoginScreen 完整重写 + 砍 SelectTeacherScreen 中间页 + 新建 TeachersAdminPage + Shell nav 按角色过滤
- frontend `client.js` 加 3 个 helper（listTeachersPublic / createTeacher / deleteTeacher）+ teacherLogin 改 body 形式
- 5 个设计档案同步：`system_features §3.4` 加 Web 登录 UX 段 / `BACKEND_DESIGN_LOG §5.1.2b` 加 4 接口表 / `WEB_DESIGN_LOG §5.1 / 5.2 / 5.3` 旧版标废除 + 加 §5.1' / 5.2' / 5.3' 新版 / `DESIGN_BRIEF` /login 行拆 2 + 加 /teachers-admin 行 / `propose §4` 砍 anonymous_suggestion / anonymous（连带「砍匿名建議」决策）
- 安全设计：CC 主动选「GET /teachers/public 只返 id (UUID) 不返 login_id」防爬虫枚举攻击 — codex 后期肯定
- 旧 select-teacher route 砍 + auto-logout 30 分钟超时改回 login（不是 select-teacher）+ Shell 「切替」按钮 = logout

**相关**:
- `05_logs/raw/2026-05-27_老师实名账户登录.md`（7 节详细叙事 + AC 模式 1+2+5+6 顶级素材）
- `system_features.md §3.4`（4-30 拍板的原则、5-27 加 Web 登录 UX 段）
- commit `b9f237c`（backend）+ `b444aad`（frontend）+ `1904b18`（设计档案）+ `aba0659`（codex 审查修）
- codex 5.5 xhigh 审查发现 3 🔴 阻塞 bug（timedelta import 缺 / 「学習担当」越权 / 没拦最后一个 admin）— 全修，剩余 4 项 itsuki 决策 / 大工程进 TODO §🚀-G

**事后回看**(几个月后补填):

---

## 2026-05-27 — 砍 /community 页「匿名建議」tab + 3 条假数据 + propose 字段方案残留

**之前的决策**(2026-04-29): system_features §7.14 itsuki 拍板砍「学生掲示板 + 社区功能整体 + 匿名建議 + 学生→帖子通报」4 项，留「リクエスト曲」。

**新的决策**: 5-27 itsuki 一句「匿名功能要删了」+ 选「A 砍匿名建議 tab 保留其他」→ 清理 web + propose 残留：
- `index.html` `/community` tabs 数组砍 `["anon", "匿名建議", ...]`
- `index.html` PostCard 组件 `isAnon` 逻辑全删
- `index.html` 3 条 anon 假帖子（C030/C031/C032）删
- `01_specs/teacher_web_v1.0_backend_models_propose.md §4` CommunityPost board_type 砍 `anonymous_suggestion` / author_type 砍 `anonymous` / §4.3 砍「匿名 author_id 怎么处理」决策项

**为什么改**:
1. 4-29 拍板砍后，web 代码 + CC 5-27 凌晨写的 propose 草案都有残留 — CC 没去查 spec 已经拍板砍了什么。itsuki 5-27 一句话指出残留
2. 实质 = 修「CC 凌晨没查 spec 就提议字段方案」的漂移，不是新决策

**这个改动影响了什么**:
- web `/community` 页从 5 tabs（掲示板 / リクエスト曲 / 忘れ物 / 匿名建議 / 宅配）变 4 tabs
- propose 文档 §4 字段方案精简

**相关**:
- `02_design/system_features.md §7.14`（2026-04-29 原拍板）
- `05_logs/raw/2026-05-27_老师实名账户登录.md` 第 2 节
- commit `b444aad`（web 砍）+ `1904b18`（propose 文档清）

**事后回看**(几个月后补填):

---

## 2026-05-26 — teacher_web Vite + TypeScript 实装版整体废弃，回归 Ryō standalone 主线

**之前的决策**(2026-05-02): 5 端代码层 v0.8 启动时立项 teacher_web Vite + TypeScript + Zustand + React 18 实装版 — 入口 `App.tsx` + 4 标签页（Applications / Study / RollCall / Teachers）+ Shell 导航壳 + `api/client.ts` 6 大模块对接 backend。共用 design system（Ryō / Cobalt / Noto Sans JP）从 4-21 Round 2 demo 继承。
**新的决策**:
1. **Vite 实装版整体废弃** — 13 个文件 `git mv` 归档到 `99_archive/2026-05-26_teacher_web_vite实装作废/`（App.tsx / main.tsx / Shell.tsx / pages/ × 5 / store/ / vite_root_index.html / Vite 构建配置 × 7）
2. **回归 Ryō standalone 主线** — `v1/src/index.html`（7774 行 standalone HTML，4-21 Claude Design Round 2 产出）成为唯一权威源
3. **保留 `api/client.ts`** — 后端真接口对接代码留着等未来 Ryō 接真后端时复用
4. **保留 `_legacy/*.jsx`** — 14 个 JSX 组件源（命名误导，实际是 Ryō 主源，不是 legacy）
5. **退 Vite 改 Python 内建静态服务器** — `开发模式跑.command` + `tomoshibi` CLI 都改用 `python3 -m http.server 8787`
6. **物理删 `node_modules`（81 MB）+ `dist`** — gitignored 但占磁盘
**为什么改**:
1. itsuki 5-26 启动 Vite dev server 看到屏幕后第一反应「这他妈根本不是我的 web 啊」— 他心里的「teacher_web」 = 4-21 Ryō prototype（深色蓝调 + 24 学生座席表 + 实时点呼仪表盘），但 Vite 实装版是 5-02 起做的另一套（4 标签页登录后台）
2. itsuki 拍板原话「Vite 实装版就是个垃圾，给我归档，用 B」— B = Ryō prototype
3. 不为 1 个月 Vite 实装工作感情用事（sunk cost fallacy 反例） — 用户体验驱动 > 技术先进性
4. Ryō standalone 是 itsuki 当初真正认可 + 实际给宿舍管理员看过的版本（2026-04-28 demo 4-28 sprint）— 而 Vite 实装版从来没演示过
**这个改动影响了什么**:
- 5 端代码层 v0.8 共同启动里 teacher_web 这一端从 v0.8 状态**回退到 v0.3 阶段**（Ryō standalone prototype）
- `00_admin/系统bug专栏.md` FC-025/26/27/28（Vite 字段对齐相关 4 条）全部 N/A，因为 Vite 整体废了
- `00_admin/TODO.md` 多处 Vite 引用要更新（line 106 A-039 / line 883 ✅ S15 / line 1023 mock state）
- `03_dev/teacher_web/WEB_DESIGN_LOG.md` 加本次会话条目（5-02→5-26 演化 + 当前权威源调整）
- `03_dev/teacher_web/DESIGN_BRIEF.md` 重写 §1+§2（删 round2/ 段 / 加 _legacy/ 实际位置）
- `03_dev/teacher_web/v1/README.md` 重写（加「怎么打开」+ 技术栈段）
- NFC iPhone 快捷指令实时点呼 demo 失效（脚本一直引用不存在的 `demo_server.py`，本次会话改用静态服务器后实时点呼断了，要恢复需要写 `demo_server.py`，独立任务）
- 老师 Web 离 v1.0 实装真前端距离重新拉大 — Ryō 是 mock 数据 prototype，要接真后端要重做 fetch 层
**相关**: `05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md`（深度 AC 素材 + 模式 3/5 顶级 + 主体性 ⭐⭐⭐⭐⭐）
**事后回看**(几个月后补填):

---

## 2026-05-26 — Ryō 设计 polish 尝试做完被 itsuki 整体回滚

**之前的决策**(2026-04-21): 4-21 Claude Design Round 2 拍板 Variation C 「涼 (Ryō)」 — 近黑 `#14171f` + コバルト `#2b4d8c` accent + Noto Sans JP + 圆角 8-12px + 极薄 shadow，近 monoxer / modern SaaS but 克制。itsuki 当晚原话「就按这个版本来」。
**新的决策**: 设计层面**仍回 4-21 原 Ryō**，本次 polish 全部回滚。
**为什么改**:
1. itsuki 选了 A（Ryō 框架内 polish）→ CC 跑 frontend-design skill 提了「Quiet Luxury Japanese Editorial（克制日式编辑感）」方向 — 米白和纸 `#f3efe8` + 朱色 sharp accent `#c43d2d` + 明朝体 display Shippori Mincho B1 + SVG 噪点纹理 + shadow 加深 + logo / 主按钮 / Stat 数字 4 处用新 token
2. itsuki 看完浏览器效果后整体不喜欢 — 主观品味驱动判断，没说具体哪里不行
3. 一句话「回滚」→ `git checkout 03_dev/teacher_web/v1/src/index.html` 全部退回
**这个改动影响了什么**:
- `v1/src/index.html` 退回 4-21 原版（冷灰白 + Cobalt + Noto Sans JP）
- `v1/README.md` 和 `teacher_web/DESIGN_BRIEF.md` 里的「polish 完成」段同步改成「试过被回滚」事实记录（不抹历史）
- AC 素材层面是金贵证据 — itsuki 拒绝 AI 设计建议 = 直接证据「不是被 AI 牵着走」
- 工程方法层面验证 CC「all-in-one-file + 提前承诺可回滚」设计 — 让 itsuki 敢试 + 不喜欢一行退回
- 未来再试 polish 候选方向：单页改造 / 字体单独换 / 找 itsuki 喜欢的具体参照系 web
**相关**: `05_logs/raw/2026-05-26_teacher_web_vite废弃+polish回滚.md`（模式 5 / 6 / 协作纠错 ⭐ 顶级素材）
**事后回看**(几个月后补填):

---

## 2026-05-26 — 指令文档不写时间戳 / 历史标记 + DMSD CLAUDE.md 247→190 行重写到 QTS 模式

**之前的决策**(隐性 / 长期): CC 在 CLAUDE.md / SKILL.md / 文档同步点等指令文档里习惯加「2026-05-XX 拍板 / 上线 / 新加 / B-XXX 死链修复」类时间戳 / 历史标记 — 以为是「可追溯 + 有上下文」，itsuki 反复看到反感累积
**新的决策**:
1. **铁律立项**：指令文档（CLAUDE.md / SKILL.md / `.claude/agents/*.md` / `docs/agents/*.md`）正文不写时间戳 / 历史标记 — 历史归 git log / `05_logs/decision_log.md` / raw / CHANGELOG
2. **写到 memory**：新建 `~/.claude/projects/-Users-kurekoduki-dev-DMSD/memory/feedback_no_timestamps_in_instruction_docs.md`（跨会话坚持）
3. **DMSD CLAUDE.md 重写**：247→190 行（A 砍 120 行历史/复制版段 + B 搬 35 行到 dmsd-startup §4 + D 补 70 行参考 QTS 模式 — Skills 继承段 / Hooks 继承段 / 全项目中枢联动 / 沟通规则简版 / Git 段）
4. WIP 顶部「最后更新」+「最近会话」段时间戳是例外（协调用，本来就是日志性质）
**为什么改**:
1. itsuki 5-26 列 DMSD CLAUDE.md 内容时看到「🆕 5-26 新加（5 行）」标记，反应：「像这种 xxx 新加，**完全没必要写到 claude.md 里啊，只是浪费时间**」
2. 设计哲学（itsuki 隐性长期，5-26 第一次明示）：指令文档 ≠ 日志 — 指令文档是当下指引（长期可读 / 不被历史污染），历史归专门的日志文件
3. QTS CLAUDE.md（itsuki 自己整理的）给 DMSD 缺的良好模式：Skills 继承段 / Hooks 继承段 / 全项目中枢联动段（结构清晰 / 不混历史）
4. CC 长期翻车（写时间戳 = 潜意识把指令当日志用） — 累积 → itsuki 正式拍板立铁律
**这个改动影响了什么**:
- DMSD CLAUDE.md 247→190 行（砍 57 行 + 加 QTS 模式新段）
- DMSD CLAUDE.md 增加 Skills 继承段 + Hooks 继承段 + 全项目中枢联动段 + 沟通规则简版 + Git 段
- 6 个项目 CLAUDE.md 顶部加沟通铁律段「不主动用英语名词」
- dmsd-startup SKILL.md §4 新增「按需触发的事」段（搬 CLAUDE.md L132-150 原内容）
- project-overview SKILL.md §1.7 dmsd-startup 描述加「+ §4 按需触发的事」
- memory 新增 `feedback_no_timestamps_in_instruction_docs.md`
- 未来所有 CLAUDE.md / SKILL.md 改动都按此铁律 — 不加时间戳尾巴 / 历史段 / bug 编号
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 6-9
**事后回看**(几个月后补填):

---

## 2026-05-26 — 启动 SOP 集中化 — dmsd-startup skill 立项 + 全局 coord-check 退役（DMSD 项目下静默）

**之前的决策**(2026-05-25 + 早些): DMSD 启动逻辑散在 3 处 — 全局 `~/.claude/hooks/session-start-coord-check.sh`（多会话协同检测） + 全局 `~/.claude/hooks/session-start-env-diff.sh`（环境清单对账）+ DMSD `bin/check_overview_drift.sh`（project-overview 漂移检测，SessionStart hook）+ DMSD `CLAUDE.md` 第 106-111 行「会话开始: 读 WIP.md」段
**新的决策**:
1. DMSD 新建 `~/dev/DMSD/.claude/skills/dmsd-startup/SKILL.md` — §2 5 件启动必做事（多会话协同注册 / project-overview 漂移检测 / ac-radar startup_check / 读 WIP / 报告状态）+ §4 按需触发的事（找文件 / TODO / WIP-TODO 铁律 / 文件联动）
2. 全局 `session-start-coord-check.sh` 在 DMSD 项目下 `exit 0` 静默退出 — 由 dmsd-startup §2 Step 1 接管
3. 全局 `session-start-env-diff.sh` 不动 — 留全局自动跑（覆盖所有项目）
4. 每个项目以后独立做自己的启动 skill（QTS / tango / SC26 等先不做，按需后续）
**为什么改**:
1. itsuki 反问「这不应该做成 skill 吗？sesion start env diff 和 start coor 不都是应该集合到启动 skill 里吗？」— CC 第一方案「挂钩不动 + skill 抽段」被推翻，itsuki 想要的不是「挂钩 + skill 互补」是「全集中到一个 skill」
2. 散在 3 处 = 容易漏，集中到 skill = 一站式入口 + CC 启动后读一次拿到完整 SOP
3. 设计哲学：单一职责 + 单一入口 over 多层冗余 + 互补
4. env-diff 留全局是因为它是「跨项目通用对账」（全局工具差异），不属于「项目特定启动逻辑」 — 职责本来就在全局层
**这个改动影响了什么**:
- DMSD `.claude/skills/` 多 1 个 skill（7→8）
- DMSD CLAUDE.md 顶部加「⭐⭐⭐ dmsd-startup 强制加载」段（5 行核心 + 简化的会话开始段）
- `~/.claude/hooks/session-start-coord-check.sh` DMSD 项目下静默退出
- 未来其他 5 项目（QTS / tango / SC26 / practice / cc-project-template）都要做自己的启动 skill
- 长期：每项目启动 skill 内容会因项目差异而不同（DMSD 有 5 端联动 / QTS 有 DECISIONS.md / tango 单端 web 等）
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 4-5
**事后回看**(几个月后补填):

---

## 2026-05-26 — destructive-bash 行为约定立项（CC 看到 WARN 自己停下想，不阻断不批准）

**之前的决策**(2026-05-12): `pre-bash-destructive-block.sh` 从 exit 2 阻断改成 warn 模式（注入 ⚠️ destructive-bash-WARN 文字提醒，不阻断命令）
**新的决策**: 在全局 `~/.claude/CLAUDE.md` 加 CC 行为约定段。CC 看到 WARN 后：(1) 自己停下来想一遍这命令真有必要吗 (2) 没必要 → 不跑 + 跟 itsuki 说一句「本来要跑 X 反思后跳过」(3) 有必要 → 直接跑不专门征求同意 (4) 灾难级（rm -rf 到 repo / rm .git / git push --force 到 main）即使有必要也要先确认
**为什么改**:
1. 5-12 改成 warn 后 itsuki 感觉「hook 没在工作」— warn 模式靠 CC 自觉，CC 看到警告但下意识继续跑命令 → 从外部看就是「命令照跑 / hook 等于没」
2. CC 提 A 全阻断 / B 加规则 / C 灾难级分档 + 可恢复级 warn 三方案 — itsuki 选 B 简化版「不要分档，不要征求同意，只要让 CC 多一次反思窗口」
3. 这不是技术决策是设计哲学 — 工具不必非「拦」或「批」，可以是「提醒反思」第三态
**这个改动影响了什么**:
- 全局 `~/.claude/CLAUDE.md` 加 `## destructive-bash-WARN 看到之后怎么办` 段（5 行行为约定）
- `pre-bash-destructive-block.sh` 脚本本体不变（已经是 warn 模式 + 8 个 pattern）
- 沟通规则隐性立铁律 — 工具警告不是用来阻断 CC，是用来给 CC 反思空间
**相关**: `05_logs/raw/2026-05-26_dmsd-startup+CLAUDE.md大改.md` 阶段 1
**事后回看**(几个月后补填):

---

## 2026-05-22 — 撤回中国海运渠道，改日本本地买点呼机配件

**之前的决策**(2026-05-08): 11 件配件淘宝集中下单 ¥381 RMB 海运到日本（含 Pi 3A+ / PN532 V3 红板 / ST25DV16K × 2 / NTAG215 × 50 / LED 5 色套装 / USB 小音响 / 面包板 / 杜邦线 / 电源 / 透明壳 + 风扇）
**新的决策**: 被海关查扣的不要了。以后所有点呼机配件改在日本本地买（Amazon.jp / 秋月電子 / スイッチサイエンス / 千石電商 / Yahoo Auction / メルカリ）
**为什么改**:
1. 5-12 到 5-16 之间这批配件走中国海运被海关查扣全没。原因是为省运费打成一个包裹寄出 → 不清楚是哪 1-2 件触发查扣，但所有件连带没收（打包 = 单点故障 / single point of failure）
2. 长期维护视角：日本本地买 = 本地有备件 + 退换货走日本邮政 = 以后某个配件坏了维护方便
3. 风险跟件数非线性 — 一件出事全没。下次拆寄 + 本地买 = 真省，不只是规避海关
**这个改动影响了什么**:
- 原 ¥381 RMB 淘宝清单 + 「下单」「收货清点」2 任务作废
- 预算重估：日本本地价 vs 中国海运价，预计贵 1.5~2 倍但消除海关风险 + 提速到货
- 硬件设计文档 `02_design/hardware_design.md` §2 全部型号 / 价格 / 渠道字段要重写（日本重新选型后）
- 点呼机设计文档 `03_dev/rollcall_device/ROLLCALL_DEVICE_DESIGN_LOG.md §1.2` 加海关事件 + 改日本买
- 未来从中国寄任何件都要拆成 2-3 包分批寄
**相关**: `05_logs/raw/2026-05-22.md`（深度 AC 素材 + 模式 1+2+6 三维度拆解）+ `.claude/skills/session-wrap/SKILL.md §5.5.15`（同日立项 decision-draft 子节 — 第一次实测产出就是这条）
**事后回看**(几个月后补填):

---

## 2026-04-15 — 点呼机架构原则: "只搬运数据,业务判断全在后端"

**之前的决策**: 无(职责边界模糊,spec 里根本没写过点呼机职责)
**新的决策**: 点呼机只做 4 件事 — 读 NFC、发 HTTP、听 WebSocket 接收推送、播报 + 亮灯。**不做任何业务判断**(迟到/缺席/窗口内外,一律后端决定)
**为什么改**:
1. AI 推 Pi 4B 4GB ¥541 RMB,我直觉"太贵",反问"为什么要这么高配置",回到第一性原理
2. 发现 spec 里 grep 点呼机零匹配 — 没有职责声明,AI 就会自由加配
3. 职责最简化 → 配置需求最小化 → Pi Zero 2 W 级别就够用
4. thin client / thick server 是成熟架构原则,改规则时只改后端一处,设备越蠢越安全
**影响**:
- 硬件配置大幅降级(Pi 4B 4GB → Pi Zero 2 W / Pi 4B 2GB 候选)
- 点呼机代码极简化(估计 < 100 行 Python)
- 所有未来"给点呼机加功能"的诱惑都要被这个原则挡回去
**相关**: `problem_solving/2026-04-15_AI过度配置诊断.md`
**事后回看**: (几个月后补填)

---

## 2026-04-15 — Phase 2 架构: iPhone 读静态标签 + 卡共存的双路径,不走 HCE

**之前的决策**(4-12 原始设想): "学生拿手机碰一下点呼机,点呼机收到手机传来的信息" — 默认手机和卡走同一个协议(都发 UID 给点呼机)
**新的决策**: 双路径共存,**协议不强求统一**
- **路径 A(卡)**: 卡 → 点呼机读 UID → HTTP 发后端 → 后端判断 → 返回 → 播报
- **路径 B(iPhone)**: iPhone 读点呼机外贴的**静态** NFC 标签(拿 device_id)→ iPhone 自己用 WiFi/4G 发 `{student_id, device_id, ts, 签名}` 给后端 → 后端判断 → 后端通过 WebSocket 推回点呼机 → 播报
**为什么改**:
1. 我原本的"卡和手机都只发 UID"统一模型撞上 iOS 平台限制 — 第三方 App 不能访问 Secure Element / HCE,**不能伪装 NFC 卡发任意 UID**
2. 追问"自动贩卖机碰一碰怎么做的",挖到 Apple Pay 背后是 SE + 一次性 token,不是普通 App 能碰的基础设施
3. 承认平台差异,用两条不同技术路径实现同样的用户体验,比强求统一协议更现实
**影响**:
- 点呼机外壳要多贴一张静态 NFC 标签(~¥2/张)
- 后端要加 WebSocket 推送机制给点呼机发播报指令
- iPhone App 要实现 Core NFC 读标签 + 签名逻辑
- Android 方案要单独设计(HCE 机制和 iOS 不同),记为项目债
- **Phase 1 卡设计不需要推翻**,Phase 2 是"加",不是"改" — 分阶段策略的复利
**相关**: `problem_solving/2026-04-15_iOS限制下的UID统一模型重构.md`
**事后回看**: (几个月后补填)

---

## 2026-04-15 — 点呼机大脑: 经 A(RPi)/B(ESP32) 全维度重新对比后,确认方向 A

**之前的决策**(4-12 记录的): 点呼机 = Raspberry Pi + PN532 NFC + 扬声器
**新的决策**: 方向仍是 A(Raspberry Pi),**但这次是经过完整 A/B 对比后由 itsuki 主动拍板,不是默认继承 AI 建议**
**为什么改(过程而非结论)**:
1. 4-12 的"已决定 RPi" 是 AI 建议 itsuki 没反对,不是主动决策
2. 今天重开对比:SBC vs MCU 本质差异、离线能力、语音播报、扩展性、AC 叙事
3. 基于 itsuki 的三个判断(宿舍网络稳、不需要屏幕、想练 Python+Linux 这条线),确认 A
4. **具体型号未定** — Pi Zero 2 W (¥100) vs Pi 4B 2GB (¥300) 还在候选,等宿舍网络情况细节再拍
**影响**: 方向没变,但这次是"被论证过的决策"而不是"默认接受的建议"
**事后回看**: (几个月后补填)

---

## 2026-04-10 — 学习方法: 从"先学完再做"改为"边做边学 + AI 辅助"

**之前的决策**: 按传统路径先把 Python 学完、Swift 学完、数据库学完,再开始做 DMSD
**新的决策**: 边做边学 — 遇到需要什么再学什么,AI 作为即时家教
**为什么改**:
1. 传统路径在 AI 时代过时了 — AI 可以即时解释任何概念,不需要"预先学完"这个前提
2. 没有真实问题驱动的学习,记不住也用不上;有问题驱动就有动力
3. AC 入試 评委更喜欢"带着真实问题边学边做"的故事,比"系统学完后按部就班"强
4. 一个月空白期证明了"先学再做"对我不可行(学着学着就放弃了)

**但识别出一个陷阱**: 纯粹"让 AI 写我不懂的代码" = vibe coding,这是作弊。
**对应的三条铁律**:
- 每行代码能解释
- 先猜后跑(先预测 AI 写的代码会怎么执行,再跑验证)
- 写 dev_log

**这个改动影响了什么**:
- 学习路径: 详见 `learning_path.md`
- AI 协作规则: 详见 `CLAUDE.md` + `feedback_be_a_coach_not_executor`
- 整个项目节奏: 不再"先憋几个月再开始",而是从现在起边做边学

**事后回看**: (几个月后补填)

---

## 2026-04-13 — 版本号体系重置: v1.0 spec → v0.1

**之前的决策**: 2026-02-12 冻结 spec 文件时用了 "v1.0" 命名(11 个文件)
**新的决策**: 所有 spec 文件重命名为 "v0.1";项目版本从 0.x.x 开始;v1.0.0 = 宿舍正式上线
**为什么改**:
1. 学了 SemVer 规范后意识到 "v1.0" 代表"第一次正式发布",连代码都没写不能叫 1.0
2. 趁文件少立刻纠正,以后文件多了改起来成本高
3. 错误的版本号会让所有后续版本的意义都不对
**影响**: 11 个 spec 文件重命名 + 所有交叉引用更新 + 建立 CHANGELOG + 写版本管理指南

---

## 2026-04-12 — 点呼机硬件: 从 iPad 改为 Raspberry Pi

**之前的决策**: (AI 一开始假设)点呼机 = iPad
**新的决策**: 点呼机 = Raspberry Pi + PN532 NFC 模块 + 扬声器,贴墙安装
**为什么改**:
1. iPad 不适合固定在墙上,也太贵(~¥50,000+ 一台)
2. Raspberry Pi 方案 ~¥13,500/台,便宜 80%
3. Raspberry Pi 跑 Python,和后端同一种语言,学习曲线低
4. 自己组装硬件对 AC 入試 展示动手能力 + 成本意识
**影响**: 后端接口设计、设备端代码语言、硬件采购清单

---

## 2026-04-12 — 分阶段上线策略

**之前的决策**: v1.0 一次性包括后端 + iOS 学生 App
**新的决策**:
- Phase 1: NFC 卡 + 后端 + 点呼机 (不需要学生 App,最快上线)
- Phase 2: 加手机 App(iOS + Android),和卡共存
**为什么改**:
1. 用卡可以绕过"学生手机 iOS/Android 不统一"的问题
2. 学校另一位老师在做二维码方案,我需要尽快上线
3. Phase 2 不替换 Phase 1,向后兼容
**影响**: 开发量砍掉近一半,上线速度大幅提升

---

## 2026-04-12 — 点呼防作弊: 语音播报设计

**之前的决策**: 无(设计空白)
**新的决策**: 学生碰卡后系统播报学生姓名,老师对照人脸
**为什么改**:
1. 发现任何打卡系统都有共同弱点:技术只能验证设备,验证不了人
2. 二维码可截图、NFC 卡可让朋友带、手机可借给朋友 — 都绕不开"代签"
3. 播报 + 老师看脸 = 攻击者必须本人到场,技术 + 人的组合
**影响**: 点呼机必须有扬声器,Phase 1 的核心差异化功能

---

## 2026-04-12 — NFC vs 二维码

**之前的决策**: 已决定 NFC,但没明确理由
**新的决策**: 继续 NFC,理由充分化
**为什么改**:
1. 二维码可以截图发给不在场的同学(致命漏洞)
2. 点呼的本质是"确认人在场",不是"确认有人扫了码"
3. NFC 的 4cm 距离限制从根本上消除了这个漏洞
**影响**: 技术选型定稿,写进 dev_log 和 spec
