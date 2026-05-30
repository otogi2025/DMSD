# teacher_web 老师网页 + 后端 — v1.0 上线审查报告

> 来源：多 agent 并行审查 workflow（8 维度 + 对抗性复核，65 个 agent，约 15 分钟）
> 运行 ID：wf_7416e10c-d2e ｜ 原始发现 56 条 → 确认 49 条 ｜ 误报剔除 7 条
> 生成时间：2026-05-30

## 一句话

确认 **49** 个真问题：致命级 6、重要级 21、次要级 22。另有盲区补充（见文末）。

---

## 🔴 致命级（blocker — 不修不能上线）

### [FE-1] 账号管理页 100% 假数据，且后端根本没有对应端点（无法接）

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:23007-23060 (AccountsPage) + 03_dev/backend/v1/app/routers/accounts.py:78`
- **现象/证据**：AccountsPage 第 23009 行 `const [accounts, setAccounts] = React.useState(window.ACCOUNTS)` 直接用写死的假学生名单。三个动作 handleSave（改资料）/ handlePasswordReset（重置密码）/ handleUnlock（解锁）全是本地 `setAccounts(...)` 改 React state，没有一句调后端。其中密码重置用 `Math.random().toString(36)` 在浏览器里随机生成一个临时密码、弹个提示就完了，什么都没存。后端 accounts.py 全文件只有一个端点 `POST /accounts`（学生自己注册用），完全没有「老师列出账号 / 改资料 / 重置密码 / 解锁」的端点。client.js 里也根本没有 accounts 相关的 helper。
- **影响**：老师在账号管理页做的任何操作（改学生信息、重置忘记密码的学生、解锁被锁账号）都是假的——刷新页面就消失，密码也根本没改。学生密码忘了 / 账号被锁这种真实运维场景在 v1.0 完全无法处理。这不是「前端没接」而是「后端这块功能整个不存在」，工作量是要从后端建表/写端点开始，不是接一下就行。
- **建议**：确认账号管理是否是 v1.0 必需功能。如果是：后端 accounts.py 要补「GET 列表 / PATCH 改资料 / POST 重置密码 / POST 解锁」四个端点 + 权限校验，client.js 补对应 helper，前端再接。如果 v1.0 不做：把账号管理入口从老师网页导航里隐藏，别让老师点进去对着假数据做无效操作。
- **复核结论**：confirmed

### [FE-2] 前台宅配/忘れ物页：发了后端请求但渲染时把结果丢了，照样显示假数据

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:18080-18647 (FrontDeskPage)`
- **现象/证据**：FrontDeskPage 第 18084 行声明了 `const [backendItems, setBackendItems] = React.useState(null)`，第 18088 行真调了 `tomoshibiApi.listFrontDesk(authToken)` 把后端数据存进 backendItems。但全文件搜 `backendItems` 只出现这一处声明、之后再没被读过——渲染用的是第 18105/18108 行写死的 `window.FRONT_DELIVERIES` / `window.FRONT_LOST_ITEMS`。而且老师的三个操作 markPicked（标记已领）/ addDelivery（登记新宅配）/ deleteDelivery（删除）全是本地 React state 改，没调 createFrontDesk / pickupFrontDesk / notifyFrontDesk（这三个 helper 在 client.js 里定义了但属于死代码，从没被调用）。
- **影响**：宅配/忘れ物是 4-29 老师 38 条需求里的功能。现在页面看着像在工作（甚至偷偷请求了后端），实际显示的全是假数据，老师登记的宅配、点的「已领取」刷新就没了，也不会真的给学生发通知。比纯假数据更坑——因为它「看起来接了」，容易让人误以为能用。
- **建议**：把渲染数据源从 window.FRONT_DELIVERIES 改成 backendItems（适配字段后），三个写操作改成调 createFrontDesk / pickupFrontDesk / notifyFrontDesk 并在成功后 refetch。这是「helper 都现成、只差接」的活，比 FE-1 简单。
- **复核结论**：confirmed

### [SEC-3] 扣分排名端点的寮过滤因漏 import dorm_units_for_teacher 必然崩溃 500

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/app/routers/discipline.py:74`
- **现象/证据**：GET /api/v1/discipline/ranking 第 74 行调用 `dorm_units = dorm_units_for_teacher(teacher)` 做 R4 寮过滤（男寮老师只能看 1+2 寮、女寮老师只能看 4 寮、跨寮役职看全部）。但 discipline.py 第 29 行只 import 了 `from ..deps import get_current_teacher`，没 import `dorm_units_for_teacher`。python 实测确认模块里没有这个名字。意味着任何老师调扣分排名都必崩 500——这不是边界情况，是主路径。BACKEND_DESIGN_LOG.md 第 1166 行写了「5-27 ... discipline / cleaning router 改用 .in_() 修过滤 bug」，但 discipline 这个 import 没补上（cleaning.py 第 26 行补对了：`from ..deps import dorm_units_for_teacher, get_current_teacher`）。
- **影响**：扣分排名页（DisciplinePage）是老师网页核心功能之一，一打开就 500 全挂，等于这个功能完全不可用。更隐蔽的安全含义：如果上线前为了「让它能跑」而草率删掉这行过滤，就会变成所有老师都能看全寮学生扣分（越权看别寮数据），违反 §3.4 + R4 的寮隔离硬约束。
- **建议**：把 discipline.py 第 29 行改成 `from ..deps import dorm_units_for_teacher, get_current_teacher`。建议上线前对每个老师可访问端点都跑一次真实 HTTP 调用冒烟测试（design log 里的『uvicorn 启动 + 49 端点注册』只验证了路由挂上了，没验证每个端点跑起来不崩——这正是这 3 个 bug 全漏网的原因）。
- **复核结论**：confirmed

### [BL-2] 点呼手动开始接口在窗口分钟数小于 5 时直接 500 崩溃

- **维度**：后端业务逻辑正确性
- **位置**：`03_dev/backend/v1/app/routers/rollcall.py:168-175 (start_session 的 -5min 检查)`
- **现象/证据**：第169-171行 `session.scheduled_window_start_at.replace(minute=session.scheduled_window_start_at.minute - 5)`。我实际跑了一遍：当窗口开始时刻分钟数 < 5（比如 21:00、21:03），`minute - 5` 算出 -5/-2，datetime.replace 抛 ValueError「minute must be in 0..59」，FastAPI 返 500。点呼时刻通常就是整点/半点（19:00、21:00），几乎必然命中。即便分钟 ≥ 5 不崩，replace 也只在同一小时内减，21:00 应该是 20:55 却根本算不出来，跨小时边界逻辑也是错的。
- **影响**：老师按「开始点呼」按钮在最常见的整点场景下直接报错，点呼根本开不了。这是点呼这个核心功能的入口，崩了整个流程瘫痪，是硬上线阻断。
- **建议**：用 timedelta 做时间减法：`window_minus5 = session.scheduled_window_start_at - timedelta(minutes=5)`，再 `if now < window_minus5: raise 409`。删掉 replace(minute=...) 这种手算分钟的写法。
- **复核结论**：confirmed

### [BL-3] 自动结算把外宿/免点呼学生误判缺席并扣 2 点

- **维度**：后端业务逻辑正确性
- **位置**：`03_dev/backend/v1/app/routers/rollcall.py:642-689 (_settle_absent) + 全项目无 session 创建/exempt 预置`
- **现象/证据**：RollCall_Spec §8.1/§8.2 要求：结算时只把仍为 init、且 base_status≠exempt_range、且无 absence_request_pending 的座位置 absent；外宿学生应在 session 创建时就被预置成 exempt_range。但 _settle_absent 只用 `checked_ids`（present/late/exempt_range 的 event）排除，没签到的全部一律 absent + 扣 2 点。问题根源：grep 全项目 `RollCallSession(` 只在 seed.py 和测试里出现，model 注释写「cron で自動生成」但根本没有 cron/scheduler，也没有任何地方把外宿学生预置 exempt_range event。所以外泊/帰省/帰国期间的学生在结算时一律被打成缺席并扣分。
- **影响**：出寮届承认通过、人合法不在宿舍的学生，点呼结算时被自动判缺席 + 扣 2 点。这是直接冤枉学生、错算规律扣分的脏数据，且无人工触发就会发生。规律扣分关系到清扫/门限处分，错扣后果严重。
- **建议**：两件事：(1) 实装 session 自动创建（cron 或启动任务），创建时按出寮届 approved + 期间内的学生预置 exempt_range event；(2) _settle_absent 在置 absent 前，排除当天有 approved 出寮届覆盖该日期的学生（参考 study.py:96-105 的 outstay_ids 写法），与 study 端对齐。
- **复核结论**：confirmed

### [EP-1] 推送通知通道（push）后端完全没实装，§7.13 里所有发给学生的 push 通知全部发不出去

- **维度**：设计要求 vs 实装差距
- **位置**：`03_dev/backend/v1/app/routers/applications.py:527 + 03_dev/backend/BACKEND_DESIGN_LOG.md:153`
- **现象/证据**：全后端搜不到任何推送实现（grep apns/APNs/fcm/FCM/device_token/push_notification/send_push 全部为空），也没有 channel='push' 的写入处。BACKEND_DESIGN_LOG.md 第 153 行白纸黑字写「后端必须实现 2 通道：notifications.email_send() + notifications.push_send()」，但只有邮件通道做了。applications.py 的承认/拒否处理（decide 函数，第 509-529 行）做完后只写了 AuditLog 就 commit 返回，没给学生发任何通知——而 system_features.md §7.13 明确要求「役职 承认/不承认 → 学生 = push + in-app」，BACKEND_DESIGN_LOG.md 第 866 行也写「整体 status 变 final 时给学生发 push」。
- **影响**：学生提交外泊/帰省/帰国申请后，老师批了或拒了，学生在 App 里收不到任何通知，只能自己反复刷新看状态——这违背 §7.13 设计要求，也破坏整个审批闭环的可用性。同理 §7.15 公告 push、§7.16 学习相关 push、巴士/学号变更 push 全部失效。push 是 spec 里学生侧通知的主手段（R1 只规定老师侧用邮件），缺了等于学生侧通知系统整体没上线。
- **建议**：上线前必须实装 push_send() 通道（APNs 给 iOS / FCM 给 Android），至少把「承认结果→学生」这条最关键的接上。若实在来不及，需 itsuki 明确把 push 降级为 v1.1 并在 spec §7.13 标注「v1.0 学生侧只有 in-app 轮询、无 push」，同时确认学生 App 端有轮询兜底能看到状态变化，否则审批闭环不可用。注意 §7.15.11 已经把公告 push 标成 v1.1，但承认结果 push 没有任何「降级到 v1.1」的记录，属于真缺口。
- **复核结论**：confirmed

## 🟠 重要级（major — 影响核心体验/功能）

### [EP-1] WebSocket 实时推送路径少了 /api/v1 前缀，前端永远连不上后端

- **维度**：前后端端点对齐
- **位置**：`03_dev/teacher_web/v1/src/api/client.js:260-269 vs 03_dev/backend/v1/app/routers/ws.py:27,30`
- **现象/证据**：后端 ws.py 第 27 行把路由前缀写成 prefix="/api/v1/ws"，第 30 行 @router.websocket("/teacher")，合起来真实地址是 /api/v1/ws/teacher。但前端 client.js 的 openTeacherWS 函数（第 260-269 行）拼地址时：相对路径分支拼出 ws://主机/ws/teacher（第 267 行），绝对路径分支用 .replace(/\/api\/v1$/,"/ws/teacher") 把 /api/v1 整段替换掉，拼出 ws://localhost:8000/ws/teacher（第 264 行）—— 两个分支都丢了 /api/v1 这一段。WEB_DESIGN_LOG.md 第 23 行也写明后端实装的是 /api/v1/ws/teacher，DESIGN_BRIEF.md §D3 第 110 行却写成 new WebSocket('/ws/teacher')，前端是照着写错的 DESIGN_BRIEF 来的。
- **影响**：老师网页的实时功能全部失效：点呼进行中座席表不会自动变绿（要靠刷新）、新出寮届的待审计数不会实时弹出。前端有 8 次指数退避重连（1s/2s/4s…30s），8 次全打到一个 404 地址后放弃，控制台一直报错。v1.0 老师端的核心卖点之一就是「实时看学生归寮」，这条断了体验大打折扣。
- **建议**：把 client.js openTeacherWS 里两个分支的目标路径都改成带 /api/v1，即 /api/v1/ws/teacher。绝对路径分支别用 replace 砍掉 /api/v1，改成在 base 后面接 /ws/teacher；相对路径分支拼成 ${proto}//${location.host}/api/v1/ws/teacher。顺手把 DESIGN_BRIEF.md §D3 第 110 行的 /ws/teacher 也更正，避免下次又照错文档抄。
- **复核结论**：confirmed

### [FE-3] 清扫确认页：同样发了后端请求却不渲染，且页面挂着「開発中」标签

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:19961-20100 (CleaningPage)`
- **现象/证据**：CleaningPage 第 19964 行声明 backendItems、第 19971 行真调 `tomoshibiApi.listCleaning(authToken, isoDate)` 存进去，但跟前台页一样——backendItems 之后再没被读，渲染用的是第 20035 行附近写死的三张卡 `[['リシンさん','W113','04-21'], ...]`。页面标题旁边还挂着黄色「開発中」徽章（第 20007 行）。审查照片的 inspectCleaning helper 在 client.js 里是死代码，从没被调用。
- **影响**：清扫确认（审查学生打扫照片、判合格/不合格）功能上看着有页面、偷偷请求了后端，但显示的是写死的三个假学生，老师没法真审查。不过清扫不在「点呼/外泊/学習/扣分」四大核心价值里，自己也挂着開発中标签，所以不算 blocker。
- **建议**：若 v1.0 要上清扫：渲染改读 backendItems，审查动作接 inspectCleaning，去掉「開発中」标签。若不上：保留「開発中」标签即可，但建议明确写进 DESIGN_BRIEF 的 v1.0 不做范围，避免上线时老师误用。
- **复核结论**：confirmed

### [FE-4] 记录搜索页：拉了 7 天点呼历史但不用，渲染写死的状态数组

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:19113-19419 (RecordsPage)`
- **现象/证据**：RecordsPage 第 19120 行声明 `backendHistory`、第 19124 行真调 `tomoshibiApi.rollcallSessionsHistory(authToken)` 存进去，但同样——backendHistory 之后再没被读（awk 扫 19113-19420 只命中声明那一行）。渲染用的是第 19143 行起写死的 `statuses = ['ok','ok','ok','late',...]` 和 methods 数组 + window.ROSTER 假名单。
- **影响**：点呼记录回溯（老师查过去某天某学生是出席/迟到/缺席）显示的是固定 12 个写死状态，跟真实历史无关。这是合规追溯用的功能，给假数据等于不可用。但属于查询类非实时操作，能靠别的方式绕（直接查后端 / 数据库），不卡核心点呼，定 major。
- **建议**：渲染改读 backendHistory（rollcallSessionsHistory 已返回真数据），把写死的 statuses/methods/roster 替换成后端历史记录的字段映射。helper 现成，只差接。
- **复核结论**：confirmed

### [FE-5] 掲示板/点歌/通知/搜索/点呼着陆统计 用假名单且后端无对应功能

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:21536 (CommunityPage) / 19784 (NotificationsPage) / 19419 (SearchPage) / 12075 (RollCallLanding)`
- **现象/证据**：CommunityPage（コミュニティ管理，含掲示板 + リクエスト曲点歌 + 忘れ物 + 宅配 tab）第 21539 行 `useState(window.COMMUNITY_POSTS)` 全假数据，handleDelete/handlePin/handleResolve/handleSongDecision 全是本地 state 改，没任何后端调用；后端 routers 目录里没有 community / song / board 任何 router。NotificationsPage（第 19786 行）和 SearchPage（第 19427 行）都用写死的 window.ROSTER_MEN/WOMEN 拼假数据。RollCallLanding 着陆页第 12086 行用 window.ROSTER 假名单算「対象 N 名」统计。注意 spec §7.14 已拍板「砍掉学生掲示板」，但 CommunityPage 至今还在导航里（index.html:11536 `['community','コミュニティ管理']` + 25049 `case 'community'`）渲染假数据。
- **影响**：这几个页面要么是后端整个不存在（掲示板/点歌——而且掲示板按规格本该砍掉却还留着）、要么用假名单（通知/搜索/着陆页统计）。搜索学生、看通知、着陆页学生人数这些会被老师当真信息看，给假数据有误导风险。掲示板没删干净违反了 spec §7.14 的拍板决定。
- **建议**：(1) 掲示板既已拍板砍，CommunityPage 整个从导航和路由删掉，别留着渲染假数据。(2) 点歌（リクエスト曲）若 v1.0 要保留需补后端，否则同样隐藏。(3) 通知/搜索/着陆页统计要接真名单——但这依赖一个能列学生的端点（目前后端没有，跟 FE-1 同根问题）。
- **复核结论**：confirmed

### [FE-7] client.js 定义 45 个接口里 16 个是从未被调用的死代码（多为写操作）

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/api/client.js（全文件）`
- **现象/证据**：把 index.html 折成单行精确比对：client.js 定义 45 个 helper，只有 29 个真被调用。16 个定义了从没被调用：createCleaning / inspectCleaning（清扫写）、createFrontDesk / notifyFrontDesk / pickupFrontDesk（前台写）、createManualDemerit / revokeDemerit（扣分手动加/撤销）、createInvitation（教师邀请）、updateAnnouncement / deleteAnnouncement / postAnnouncementReply / deleteAnnouncementReply（公告改/删/回复）、getAnnouncement（公告详情）、getApplication / getAuditLog（申请详情/审计日志）、getAnnouncementUnreadCount（未读数）。规律很明显：列表读取（list*）大多接了，但写操作和详情几乎全没接。
- **影响**：这 16 个死代码暴露了一个系统性缺口：后端能力（写/改/删/详情）大多已具备且 helper 都写好了，但前端组件根本没接上去。具体后果：扣分页只能看不能手动加/撤销分；公告只能发不能改/删/回复；申请只能看列表不能看详情和审计履历；前台/清扫的所有写操作都断。这些不是单点 bug 而是「写回链路普遍缺失」，是 v1.0 接入度的核心短板。
- **建议**：以这 16 个死 helper 为清单，逐个排查对应组件是否该接、该接的接上。建议先接扣分（createManualDemerit/revokeDemerit）和公告写操作（这俩对应的页面已经在用 backend 读），属于补完即可用；前台/清扫见 FE-2/FE-3。client.ts 那套 416 行类型版从没被加载，也建议确认是否还需要保留以免误导。
- **复核结论**：confirmed

### [FE-8] 扣分页只接了读排名，手动加分/撤销分没接（只能看不能操作）

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:17566-17640 (DisciplinePage)`
- **现象/证据**：DisciplinePage 第 17580 行真调 `tomoshibiApi.getDisciplineRanking(authToken, month)` 拉后端扣分排名（5-27 接的），失败才回退到 mock。但后端有的 createManualDemerit（老师手动给学生加扣分）和 revokeDemerit（撤销某条扣分）这两个 helper 在 client.js 里是死代码，DisciplinePage 没接。另外注意第 17608 行附近 backend 排名只返聚合 total_points，late/absent 拆分被写死成 0（`late: 0, absent: 0`），UI 上迟到/缺席分项恒为 0。
- **影响**：扣分是四大核心价值之一。现在老师能看到学生扣分排名（真数据），但没法手动加扣分（比如学生违纪老师当场记一笔）或撤销误判的扣分——这俩是扣分管理的关键写操作。而且 UI 上迟到/缺席的分项明细恒显示 0，老师看不出扣分构成。
- **建议**：DisciplinePage 补接 createManualDemerit / revokeDemerit（helper 现成）。后端扣分排名若需要返回 late/absent 拆分，要在 schema 里补字段再让前端读，否则把分项列去掉别显示恒 0 误导老师。
- **复核结论**：confirmed

### [SEC-1] 删最后一个管理员的「防系统锁死」保护因漏 import func 会直接崩溃 500

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/app/routers/teachers.py:284`
- **现象/证据**：delete_teacher 删教师时，第 282-290 行有一段「删最后一个寮务管理角色就拦下来（防系统 lockout 没人能管理教师）」的保护，里面调用 `func.count(models.Teacher.id)` 来数还剩几个管理员。但本文件顶部只 import 了 `from sqlalchemy import select`（第 15 行），从来没 import `func`。我用 python 实测确认：`app.routers.teachers` 模块里根本没有 `func` 这个名字（resolves_in_module=False）。意思是只要删的目标是「寮務部長/寮務課長/寮監」这类管理角色，代码跑到第 284 行就抛 NameError，FastAPI 返回 500。
- **影响**：这条保护是专门防「把最后一个管理员删掉 → 谁都登不进去管理系统 = 系统永久锁死」的。现在它一执行就崩溃：要么删管理员永远失败（管理员根本删不掉，运维受阻），要么——更糟——如果上线时改成捕获异常或顺序变了，保护就静默失效，真有人误删最后一个管理员系统就锁死。这是 BACKEND_DESIGN_LOG.md 第 1166 行明确写了「5-27 codex 审查 #3 删最后一个寮务管理角色拦截」要做的安全功能，但实际没跑通。
- **建议**：在 teachers.py 第 15 行改成 `from sqlalchemy import func, select`。改完务必加一个集成测试：只剩 1 个寮務部長时调 DELETE /teachers/{id} 必须返 400 LAST_ADMIN（现在 70 个测试一条都没覆盖这个路径，所以 bug 漏网）。
- **复核结论**：confirmed

### [SEC-2] 教师创建的并发去重保护因漏 import IntegrityError 会二次崩溃

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/app/routers/teachers.py:244`
- **现象/证据**：create_teacher 创建新教师时，第 242-253 行用 `try: db.commit() except IntegrityError:` 来兜并发情况下两个请求同时建同一个 login_id/email 的撞车（唯一约束冲突），本意是回滚后返回友好的 409。但本文件没 import `IntegrityError`（正常应是 `from sqlalchemy.exc import IntegrityError`），python 实测确认模块里没有这个名字。一旦真的发生 commit 撞车，except 子句自己抛 NameError → 500，原始数据库错误也没被正确处理。
- **影响**：教师账号是高权限对象，创建是 admin 操作。正常情况下前面的预查能挡掉大部分重复，所以平时不触发；但并发场景（两个 admin 同时建同名账号）会让 server 抛 500 且事务状态不干净，可能导致后续请求连带报错。属于「写了防御代码但防御本身是坏的」，比没写还危险（给人安全的错觉）。
- **建议**：在 teachers.py 顶部加 `from sqlalchemy.exc import IntegrityError`。同样建议补一个并发/重复 login_id 的测试覆盖这条 except 分支。
- **复核结论**：confirmed

### [SEC-4] 公开 repo 的 seed.py 写死了审核员注册码/密码的 fallback 默认值

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/seed.py:250-258`
- **现象/证据**：seed.py 是 git 跟踪文件（git ls-files 确认），而仓库是 public（otogi2025/DMSD）。第 250-258 行：审核员密码 fallback 是 `"Tomoshibi-Reviewer-2026!"`、审核员永久注册码 fallback 是 `"999999"`，都明文写在代码里。虽然第 250、256 行用 `os.environ.get(..., 默认值)` 做成「env 没设就用这个默认」，且 seed_prod 第 264-273 行有 log.warning 提醒上线必设 env，但这只是警告，不阻断。审核员注册码 is_reviewer=True 是永久有效、老师面板看不到、refresh 也不作废的后门级凭证（spec §7.16 例外条款）。
- **影响**：任何人看公开 repo 就知道：如果运维忘了设 REVIEWER_PASSWORD / REVIEWER_REGISTRATION_CODE 这两个 env，审核员账号密码就是 `Tomoshibi-Reviewer-2026!`、永久注册码就是 `999999`，可以拿这个永久码注册一个真学生账号混进系统。fallback 默认值 + 仅 warning 不阻断 = 一次运维疏忽就变后门。这跟 config.py 对 JWT 密钥/CORS/SQLite 做的 production fail-fast 硬拦（不合规直接 RuntimeError 拒启）形成对比——同样级别的敏感凭证却只 warn 不拦。
- **建议**：把 seed_prod 改成：APP_ENV=production 时如果 REVIEWER_PASSWORD / REVIEWER_REGISTRATION_CODE / ADMIN_INITIAL_PASSWORD 任一是 fallback 默认值，直接 raise RuntimeError 拒绝 seed（跟 config.py 的 _validate_production_settings 一致的硬拦风格），而不是只打 warning。或者干脆不给 fallback，env 没设就报错。
- **复核结论**：confirmed

### [BL-5] 今日点呼列表缺日期上界，返回所有未来 session

- **维度**：后端业务逻辑正确性
- **位置**：`03_dev/backend/v1/app/routers/rollcall.py:63-93 (today_sessions)`
- **现象/证据**：第70-81行 stmt 只有 `scheduled_window_start_at >= 当天0点` 一个条件，没有 `<= 当天23:59` 上界。对比下面 list_sessions_history（第124-129行）就有 from/to 双边界。结果是「今日 session」接口会把今天往后所有日期的 session 全都返回。
- **影响**：老师端「今日点呼」面板会混入未来日期的 session，老师可能误开未来的点呼，或座席板显示错误日期的数据，运行期日常困扰。
- **建议**：给 today_sessions 加上界条件 `scheduled_window_start_at < 次日0点`（或 <= 当天23:59:59），与 list_sessions_history 的边界写法对齐。
- **复核结论**：uncertain

### [BL-6] 手动扣分的月度归属用 UTC 计算，跨月凌晨会归错月

- **维度**：后端业务逻辑正确性
- **位置**：`03_dev/backend/v1/app/routers/discipline.py:137-144 (create_manual_demerit)`
- **现象/证据**：第137行 `now = datetime.now(timezone.utc)`，第144行 `month=now.strftime('%Y-%m')`。我验证：JST 6月1日早8点 = UTC 5月31日23点，UTC 算出 month='2026-05'，而排名查询 get_ranking 是按 month 字符串聚合的。点呼/study 端算 month 都用 JST（rollcall.py:340 用 scheduled_window_start_at 的 JST、study.py:369 用 today JST），唯独手动扣分用 UTC，月初/月末凌晨的手动扣分会被归到上个月，排名 + 阈值统计漏算。
- **影响**：月度规律排名是清扫(4点)/门限(8点)处分的依据。手动扣分归错月 → 当月排名漏掉这笔分、上月排名多算，阈值触发判断跟着错，可能错放/错罚学生。
- **建议**：create_manual_demerit 改用 JST 计算 month：复用一个 `_now_jst()` 工具（study/rollcall 已有），`month = now_jst.strftime('%Y-%m')`，全后端 month 归属口径统一成 JST。
- **复核结论**：confirmed

### [EP-3] 公告的编辑/删除/返信管理（§7.15.7）后端做了、前端有按钮但没接线

- **维度**：设计要求 vs 实装差距
- **位置**：`03_dev/backend/v1/app/routers/announcements.py:411/454/379（后端齐全）vs 03_dev/teacher_web/v1/src/index.html（updateAnnouncement/deleteAnnouncement/reply 调用次数 = 0）`
- **现象/证据**：后端 announcements.py 端点完整：PATCH /{id}（编辑，第 411 行）、DELETE /{id}（删除，第 454 行）、POST /{id}/replies（第 379 行）、DELETE replies 都有。client.js 也定义了 updateAnnouncement/deleteAnnouncement/postAnnouncementReply/deleteAnnouncementReply 这些 helper。但前端 index.html 里 grep updateAnnouncement/deleteAnnouncement/postAnnouncementReply/getAnnouncementUnreadCount 全是 0 次调用——前端只接了 listAnnouncements（第 20115 行）+ createAnnouncement（第 20151 行）。前端虽有「編集」按钮（第 20974 行）和编辑 modal（第 21180 行），但点了不会调后端更新。system_features.md §7.15.7 明确要求老师 Web 端「投稿/編集/削除/返信管理」四件齐全。
- **影响**：老师发了公告后改不了、删不了、管不了学生的返信——§7.15.7 要求的「編集/削除/返信管理」三项不可用。公告是 itsuki 拍板「重要性点呼の次（M1 必達）」的功能，管理能力缺失影响实际运营（发错字没法改、过期公告没法删）。属于「后端做了前端没接」类型。
- **建议**：前端把已有的「編集」按钮接到 updateAnnouncement helper、加删除按钮接 deleteAnnouncement、返信管理接 postAnnouncementReply/deleteAnnouncementReply。后端和 client.js helper 都现成，只需在 index.html 公告页补 4 处调用。这是低成本高价值的补线。
- **复核结论**：confirmed

### [EP-5] teacher_web 三处 demo scaffold（demo_server.py + index.html LAN IP 自动检测块）还没删，是上线前必清项

- **维度**：设计要求 vs 实装差距
- **位置**：`03_dev/teacher_web/v1/demo_server.py（仍存在 142 行）+ 03_dev/teacher_web/v1/src/index.html:12453/12507（/api/server-info 调用）`
- **现象/证据**：system_features.md 末尾「v1.0 上线前必删 demo scaffold 清单」§Teacher Web 列了 4 条，其中第 1 条 demo_server.py（内存模拟后端 + 银行卡 NFC POST 接口）和第 3 条 index.html line ~4895-4931 LAN IP 自动检测 UI 块，要求上线前删掉。实测：demo_server.py 文件还在（ls 确认 5302 字节）；index.html 第 12453 行还有「demo_server.py の /api/server-info から LAN IP を自動取得」的 fetch 调用 + 第 12507 行「demo_server.py から自動検出」的 UI title。这些都是必删清单里登记但还没删的项。
- **影响**：demo_server.py 是内存模拟后端、绕过真认证，留在生产路径里有混淆和误连风险；LAN IP 自动检测 UI 块是 demo 期间为了 iPad 找 Mac IP 用的，生产环境不需要还会暴露内网信息。spec 明确说不删「→ 变安全漏洞或 demo 数据混入生产」。
- **建议**：上线前按 system_features.md §「v1.0 上线前必删 demo scaffold 清单」逐条执行：删 demo_server.py 整个文件、删 index.html 第 12447-12510 附近的 LAN IP 自动检测块、删 demo/ 目录。删完跑 spec 给的全 repo 扫描命令 grep -rn 'DEMO-ONLY' 03_dev/ 确认清空。
- **复核结论**：confirmed

### [EP-6] 行事予定完整日历（§7.5）+ 巴士管理（§7.6）后端没端点、前端只有 mock UI

- **维度**：设计要求 vs 实装差距
- **位置**：`system_features.md §7.5/§7.6 vs 后端无 events.py/bus.py（确认文件不存在）+ 前端 EventCalendar/BusSchedule 仅 mock`
- **现象/证据**：后端 routers 目录里没有 events.py、没有 bus.py（ls + grep 确认两文件不存在），main.py 注册的 router 里也没有 events/bus。spec §7.5 要求 GET/POST/PATCH/DELETE /events（行事予定加改删，老师 Web 编辑 modal），§7.6 要求 GET/POST/PATCH/DELETE /bus/routes（巴士录入编辑）。前端 index.html 有 EventCalendar/BusSchedule 等 UI 组件（grep 命中 6 处）但都是 window.* mock 数据，没接任何后端。WEB_DESIGN_LOG.md 第 816 行把「巴士編集 #11 / 行事編集 #12」列在清单里，但 §11.3 第 578 行把 info/community 等页标为「P0 不動（P3 範囲）」。
- **影响**：行事日历和巴士是老师 38 条要件 #9/#11/#12 + Q8/Q9，spec 标 V1。但 WEB_DESIGN_LOG §11.3 已把这些页归到 P3（P0 范围外），说明是有意识地往后排。后端零端点 + 前端纯 mock，等于完全没做。影响功能完整度但不阻塞核心点呼/审批闭环。
- **建议**：确认 itsuki 对 §7.5/§7.6 的上线优先级。若 v1.0 不做（按 P3 定位），在 system_features.md §7.5/§7.6 的 Demo/V1 列把「(V1)」改标注为「(V1.1)」或加一句「v1.0 后送」，让 spec 和实装对得上账。若要做，需后端新建 events/bus 两个 router + 模型 + 前端接线，工作量较大。
- **复核结论**：confirmed

### [EP-7] 指导履历/事案录入/学生个人档案（§7.9/§7.10）+ リクエスト曲通报封禁（§7.11）前后端大面积缺失

- **维度**：设计要求 vs 实装差距
- **位置**：`system_features.md §7.9/§7.10/§7.11 vs 后端无 guidance/incident/disclosure/songs 端点 + 前端无指導履歴/StudentDetail 页`
- **现象/证据**：后端 grep guidance/incident/disclosure/students/{id}/profile 端点全部 0 命中（无 §7.9 指导履历录入、§7.10 学生 aggregated 档案、开示申请决定等端点）；songs/song_reports/リクエスト曲 后端模型和 router 完全不存在（grep 0 命中）。前端 index.html grep「指導履歴/StudentDetail/事案/IncidentPage/guidance」0 命中（这些页面不存在）；リクエスト曲前端 UI 有 54 处命中（CommunityPage 里有），但全是 mock，对应的后端通报/封禁/ban_level 一行没有。spec §7.9-§7.11 这些都标 V1，但 §7.11 的通报封禁逻辑（5/10/15 件自动封禁 + cron 解除 + ban_level）后端完全空白。
- **影响**：指导履历/事案/学生档案是老师 38 条要件 #31/#32/#33，リクエスト曲通报是 itsuki 5-01 拍板「留」的功能。但 WEB_DESIGN_LOG §11.3 把这些归到 P3/P2 范围外，属于有意识往后排。前后端都没做。不阻塞核心闭环，但 spec 标 V1 与实装为零之间存在明显对不上账。
- **建议**：这几块工作量大（指导履历涉及开示申请决定流程、リクエスト曲涉及通报阈值 + cron 封禁），建议 itsuki 明确划到 v1.1，并在 system_features.md §7.9/§7.10/§7.11 把 Demo/V1 标记改为 v1.1，避免 spec 写 V1 但实装零导致上线验收时大面积「未达标」误判。若 v1.0 必做需单独排期。
- **复核结论**：confirmed

### [EP-8] 学号一括进级/班级变更/转校生录入（§4.2）后端没看到对应端点，spec 标 V1

- **维度**：设计要求 vs 实装差距
- **位置**：`system_features.md §4.2 vs 03_dev/backend/v1/app/routers/accounts.py（无 grade bump / 学号变更端点）`
- **现象/证据**：system_features.md §4.2 学号生命周期要求老师 Web 能做「全员进级（grade_code +1 一括更新）」「班级编成变更单件 patch」「转校生录入」，且 §7.13 通知矩阵有「学号变更（老师改）→ 学生 push」。但 accounts.py 里 grep grade/bump/进级 只看到注册时的学号查重（第 91-117 行），没有进级一括更新或学号 patch 的端点。前端也没有对应页面。
- **影响**：学号进级是每年 4 月的运维操作，spec §4.2 明确放在 v1.0（区别于房间号一括分配明确标 v1.1）。缺失意味着到明年 4 月老师无法在系统里给全寮升级学号。不阻塞首次上线（上线时学号是注册时定的），但属于 spec 标 V1 而实装缺失。
- **建议**：确认进级功能的上线时机——首次上线（假设在学年中）可能用不到，但 spec 标 V1。建议要么补一个老师 Web 一括进级端点 + 页面，要么在 spec §4.2 明确标注「进级功能 v1.0 后送、明年 4 月前补」。同时 §7.13「学号变更→学生 push」也依赖 EP-1 的 push 通道。
- **复核结论**：confirmed

### [DEMO-1] 老师网页 ShortcutsDemoCard（局域网 IP / iPhone 快捷指令 URL 卡）生产环境也会显示，未受 demo 开关保护

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/teacher_web/v1/src/index.html:12436 + 12441-12545`
- **现象/证据**：system_features.md §上线前必删清单 Teacher Web 第 3 条要求「删整段 — production 不需要查 LAN IP」。但 index.html 第 12436 行 `<ShortcutsDemoCard />` 是无条件渲染的（不像 DemoConsole 那样包在 `window.DEMO_MODE &&` 里）。组件第 12454-12463 行调 `fetch('/api/server-info')`（demo_server.py 专属端点）自动探测局域网 IP，第 12471 行拼出 `http://${host}/checkin?no=${no}` 的明文点呼后门 URL 显示给老师看，番号取自 `window.DEMO_SEED_NO`（060218，itsuki 本人）和 `window.ACCOUNTS` 假数据。
- **影响**：v1.0 上线后老师在点呼着陆页会看到一张「ショートカット URL」卡片，内容是局域网内网 IP + 一个无需登录就能 POST 打卡的 checkin 后门地址。一是泄漏服务器内网地址，二是把「任何人构造这个 URL 就能伪造打卡」的攻击路径直接显示给用户，三是显示 itsuki 本人的演示番号造成困惑。这是明确登记在必删清单里、却还没删的项。
- **建议**：删掉第 12436 行的 `<ShortcutsDemoCard />` 渲染调用和第 12441-12545 行整个组件定义；或者至少像 DemoConsole 一样用 `window.DEMO_MODE && <ShortcutsDemoCard />` 包起来，让它只在 URL 带 ?demo=1 时出现。推荐直接删（这个卡片只服务于 iPhone 快捷指令演示，生产用真 NFC 点呼机，不需要它）。
- **复核结论**：confirmed

### [FAKE-1] 账号管理页（AccountsPage）纯靠 window.ACCOUNTS 假数据，没有任何真后端调用，密码重置/解锁是空操作

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/teacher_web/v1/src/index.html:23009（AccountsPage 组件）+ DESIGN_BRIEF.md:88`
- **现象/证据**：第 23009 行 `const [accounts, setAccounts] = React.useState(window.ACCOUNTS)` —— 账号列表初始值就是 7 条假学生（リュウ イヒ 等，第 10112 行起定义，含假邮箱 ryu.ihi@tomoshibi.local、假电话 090-0000-0000）。在 client.js 的 40 个端点里根本没有「列学生 / 重置密码 / 解锁账号」对应的 API，整个 AccountsPage 没出现一次 `tomoshibiApi`。DESIGN_BRIEF.md 第 88 行自己承认「学生 list / state — 当前用 window.ROSTER/ACCOUNTS 假数据」。
- **影响**：账号管理是 iOS 学生改密码的唯一通道（注释自己写「iOS App 内不可改密码，本画面是唯一自改经路」）。它现在显示的全是假学生，老师点「重置密码 / 解锁」是改假数据，关页面就没了，真学生账号永远改不了。这是核心管理功能完全没接后端，不是小瑕疵。
- **建议**：v1.0 上线前必须给 AccountsPage 接真后端：backend 需要补「GET 学生列表 / POST 重置密码 / POST 解锁」端点（当前 client.js 和 backend routers 都没有），前端把 useState 初始值从 window.ACCOUNTS 改成真 API fetch。在没接通前这页不能开放给老师用。
- **复核结论**：confirmed

### [SEED-2] seed.py 默认 APP_ENV=dev，生产误跑会灌入密码统一为 123456 的假学生假老师

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/backend/v1/seed.py:39 + 380`
- **现象/证据**：第 39 行 `DEV_PASSWORD = '123456'`，第 81-118 行 seed_dev 把假学生（リュウ イヒ / 田中 太郎）和假老师（shingu 新股）全部用这个密码的 hash 灌进 DB。第 380 行 `env = os.environ.get('APP_ENV', 'dev').lower()` —— 默认值是 dev。也就是说在生产服务器上只要忘了写 `APP_ENV=production` 就直接 `python -m seed`，灌的是弱密码 123456 的假数据，而不是 production 最小数据。
- **影响**：生产数据库被弱密码 123456 的假账号污染，这些账号能用 123456 真登录系统（密码是真 hash），等于开了人尽皆知的弱密码后门 + 假学生混进真名册。default 取 dev 这个设计让一次手滑就能造成生产事故，属于上线前必须堵死的隐患。
- **建议**：把第 380 行默认值改成安全侧：要么默认 production，要么 env 没显式设成 dev/production 就直接 raise 报错拒绝跑（fail-fast），不允许「啥都没设就默默灌 dev 假数据」。同时在 seed_dev 顶部加一道 `if env != 'dev': raise` 的二次保险。
- **复核结论**：confirmed

### [RUN-1] APP_ENV 默认 dev — ops 漏配生产会静默降级、绕过所有上线校验和迁移

- **维度**：后端可运行性实跑验证（硬证据）
- **位置**：`03_dev/backend/v1/app/config.py:37 + app/main.py:55-58 + app/config.py:78`
- **现象/证据**：实跑确认：`Settings.model_fields['app_env'].default` 输出 `dev`（config.py:37 写 `app_env: Literal[...] = "dev"`）。main.py 生命周期里写 `if settings.app_env == "dev": create_all()`——也就是只要不是显式 production 就会用 create_all() 直接建表（create_all 是 SQLAlchemy 的「按模型一把建全部表」函数，绕过 alembic 迁移）。同时 config.py:78 的生产校验函数开头是 `if s.app_env != "production": return`——不是 production 就直接放行不校验。我实测把 APP_ENV 设成 production 时确实抛错拦住了 SQLite（输出「Production 环境不允许 SQLite」），但默认 dev 时这层保护一个都不会触发。
- **影响**：上线那天 ops（负责部署的人）如果忘了在服务器 .env 里写 APP_ENV=production，后端会以 dev 模式起来：① 用 create_all() 建表而不是跑 alembic 迁移，schema 来源不受版本控制；② 弱 JWT 密钥 / SQLite / 通配符 CORS 这三道上线红线全部静默放行不报错。属于「fail-open」——配错了不会炸、反而偷偷用不安全的默认值跑起来，比直接报错更危险。这是部署配置层隐患，不是代码 bug，但直接关系 v1.0 上线安全。
- **建议**：把生产校验从「app_env != production 就跳过」改成「app_env 不在 {dev} 白名单 或 未显式设置就当 production 严格校验」，即默认收紧而非默认放行；或在部署文档/启动脚本里把 APP_ENV=production 设为必填项并在 CI/部署检查里硬性校验。最稳的做法是 main.py 启动时若检测到生产特征（非 SQLite 的 DATABASE_URL）却 app_env=dev，直接 raise 拒绝启动。
- **复核结论**：confirmed

### [EP-1] API_BASE 写死 http://localhost:8000，生产部署会全盘失效

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/src/index.html:10041`
- **现象/证据**：第 10041 行硬编码 window.API_BASE = "http://localhost:8000/api/v1";（前端调后端的根地址写死成本机 8000 端口）。但 client.js 第 39 行的逻辑是「window.API_BASE 没设才用 /api/v1」——既然 index.html 已经把它设成绝对地址 localhost:8000，同源部署的 /api/v1 永远不会生效。DESIGN_BRIEF.md 第 125 行明确写的生产路径是「iPad Safari 打开 http://{Mac IP}:8000/teacher_web/ → 经 FastAPI StaticFiles 挂载」，那种同源部署下应该用相对地址 /api/v1，而不是 localhost:8000（iPad 上 localhost 指向 iPad 自己，根本连不到 Mac 后端）。
- **影响**：v1.0 真正部署给老师在 iPad 上用时，所有接口请求都会打到 iPad 本机的 localhost:8000（不存在的地址），整个网页除了静态画面外全部连不上后端——登录都做不到。当前这个值只对「老师本人在 Mac 上本地 dev 调试」有效。
- **建议**：上线前把第 10041 行改回相对地址 window.API_BASE = "/api/v1";（同源 StaticFiles 部署时浏览器会自动拼成 http://{Mac IP}:8000/api/v1）。本地 dev 想连 8000 时改成由 URL 参数或单独 dev 配置控制，不要把 dev 值留在生产文件里。
- **复核结论**：confirmed

## 🟡 次要级（minor — 该修但不阻断上线）

### [EP-2] 退出登录调的 DELETE /sessions/current 后端没有这个端点，每次必 404

- **维度**：前后端端点对齐
- **位置**：`03_dev/teacher_web/v1/src/index.html:24643 vs 03_dev/backend/v1/app/routers/auth.py:24,31,83`
- **现象/证据**：前端 index.html 第 24643 行退出登录时用原始 fetch 直接调 await fetch(`${window.API_BASE}/sessions/current`, {method:"DELETE"})，注释写「Task #15 W5 拍板: backend revoke」。但后端 auth.py（前缀 /api/v1/sessions，第 24 行）只定义了两个端点：POST /student（第 31 行）和 POST /teacher（第 83 行），没有任何 DELETE，也没有 /current。整个后端 grep 不到 sessions/current。
- **影响**：退出登录时这个 DELETE 请求每次都返回 404。前端用 try/catch 包住了所以界面照样退出（本地清掉 token），表面看不出问题——但后端那一侧的「注销 token」动作从来没真正发生。后端用的是无状态 JWT，本来就没有撤销机制，加上这个 404，意味着用户「退出登录」后旧 token 在过期前理论上仍然有效。对一个管理学生数据的系统是安全隐患。
- **建议**：两个方向二选一：A. 后端在 auth.py 真补一个 DELETE /api/v1/sessions/current（配合一张 token 黑名单表或缩短 token 有效期）实现真注销；B. 如果 v1.0 决定接受「无状态 JWT 不做服务端注销」，就把前端这次 fetch 删掉、注释里「backend revoke」的承诺也撤掉，避免误导。无论哪种都要让代码和「W5 拍板」一致。
- **复核结论**：confirmed

### [EP-3] 点呼历史的 from 查询参数后端变量名是 from_，导致 from 永远不生效

- **维度**：前后端端点对齐
- **位置**：`03_dev/teacher_web/v1/src/api/client.js:136-142 vs 03_dev/backend/v1/app/routers/rollcall.py:102-104`
- **现象/证据**：前端 client.js rollcallSessionsHistory（第 136-142 行）把日期拼成 ?from=YYYY-MM-DD&to=YYYY-MM-DD。后端 rollcall.py 历史端点 GET /sessions（第 102-104 行）的函数签名是 def list_sessions_history(from_: Optional[date] = None, to: ...)。FastAPI 不会自动去掉变量名结尾的下划线，也没给它加 Query(alias="from")，所以这个参数对外暴露的查询名就是 from_，不是 from。前端发的 from= 绑不到 from_ 上，会被忽略落到默认值。
- **影响**：老师在记录页选「起始日期」筛点呼历史时，from 这个条件实际不起作用——后端永远走默认「过去 7 天」逻辑（rollcall.py 第 116-119 行）。to 参数名一致所以正常。结果就是不管老师怎么选起始日，列表都只给最近 7 天。功能上是静默的错（不报错但筛错），影响不大但确实是 bug。目前前端调用处（index.html:19125）只传 token 不传日期，所以暂时没暴露，但只要将来接上日期选择器就会踩到。
- **建议**：后端 rollcall.py 第 104 行把 from_: Optional[date] = None 改成 from_: Optional[date] = Query(None, alias="from")（从 fastapi 导入 Query），让对外查询名变回 from，跟前端和文档 §rollcall/sessions?from=&to= 对齐。
- **复核结论**：confirmed

### [EP-4] 生产 index.html 里残留演示专用的 /api/server-info 原始 fetch

- **维度**：前后端端点对齐
- **位置**：`03_dev/teacher_web/v1/src/index.html:12455,12841`
- **现象/证据**：index.html 第 12455 行和第 12841 行各有一处 fetch("/api/server-info", {cache:"no-store"})，第 12453 行注释写「demo_server.py 的 /api/server-info から LAN IP 自动取得」。这个地址既不是 /api/v1 前缀，后端 v1（main.py + routers）和 demo 目录里也都 grep 不到 server-info——它只存在于演示用的 demo_server.py。用途是给演示二维码组件自动填本机局域网 IP。
- **影响**：这两处是演示遗留代码混进了权威源 index.html。在 v1.0 生产部署下这个请求会 404，但都包了 .catch(()=>{}) 并有手动输入兜底，所以不会让界面崩。不算上线阻断，但属于「演示脚手架没清干净」——和项目 memory 里『demo scaffolds 必须 v1.0 前删』的纪律相符，应纳入上线前清理清单核对。
- **建议**：确认这两处所在的二维码/账号展示组件是不是 v1.0 老师端真要保留的功能。若是演示专用，连同组件一起删；若要保留并需要自动填 IP，把端点改到 v1 后端真实路径或干脆只留手动输入。同时跟 system_features.md 末尾的『v1.0 上线前必删 demo 清单』对账登记。
- **复核结论**：confirmed

### [FE-9] 外泊承認没传审批意见、详情走假数据、保留(hold)操作对后端无效

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:25118-25165 (App decide 调用) + 17023 (OutstayDetailModal)`
- **现象/证据**：外泊承認主线是真接的（第 25141 行 pendingForMe + 第 25132 行 decide）。但第 25136 行调 decide 时第三个参数 comment 传的是 `undefined`，老师填的审批意见没传给后端。第 25118 行注释自己写明「a='pending'(保留) は backend decide には無いので skip (UI のみ閉じる)」——老师点「保留」只是关弹窗，后端状态没变。另外申请详情 modal（OutstayDetailModal）依赖 getApplication / getAuditLog，这俩是死代码（FE-7），所以详情和审批履历展示的是 demo 数据不是后端真详情。
- **影响**：外泊承認核心动作（批准/拒绝）能用，但三个边角：审批意见丢失、保留操作是假的、详情页非真数据。审批意见丢失在合规上有点影响（拒绝理由没存档），保留按钮点了没用会让老师困惑。属于核心流程的细节瑕疵，不卡上线。
- **建议**：decide 把老师填的 comment 真传过去；「保留」按钮要么对接后端对应状态、要么直接从 UI 去掉避免误导；详情 modal 接 getApplication/getAuditLog 展示后端真详情和审批履历。
- **复核结论**：uncertain

### [FE-10] API_BASE 写死 localhost + 残留 demo_server 的 LAN-IP / events 轮询块

- **维度**：前端真接入度（假数据 vs 真接口）
- **位置**：`03_dev/teacher_web/v1/src/index.html:10041 (API_BASE) / 12453-12455 / 12841 / 13012`
- **现象/证据**：第 10041 行 `window.API_BASE = 'http://localhost:8000/api/v1'` 写死指向本机 localhost——部署到真服务器/局域网时老师电脑访问不到后端。另外第 12453-12455、12841 行还在 fetch demo_server.py 的 `/api/server-info`（自动检测局域网 IP），第 13012 行还在每秒轮询 `/events/latest`——这些正是 spec §1665「v1.0 上线前必删 demo 清单」里第 2、3 条点名要删的 demo 块（system_features.md:1702 写明「删整段 — production 不需要查 LAN IP」），至今没删。
- **影响**：API_BASE 写死 localhost 意味着这个网页只能在跑着后端的同一台机器上用，真实部署（老师各自电脑连宿舍服务器）直接连不上后端，全部 fallback 到假数据。残留的 demo server-info / events 轮询块在生产环境会一直请求不存在的端点报错刷控制台。这俩都是规格已明确登记要删/要改但漏了的上线阻塞项。
- **建议**：API_BASE 改成相对路径 `/api/v1`（client.js 第 38 行其实已有 `|| '/api/v1'` 兜底，把 10041 行的 localhost 硬编码删掉即可走相对路径），由部署的反向代理转发后端。按 spec §1665 清单删掉 server-info（12453/12841）和 events/latest 轮询（13012）这两个 demo 块。
- **复核结论**：confirmed

### [SEC-5] JWT 无服务端吊销机制 — token 签发后 24 小时内无法主动失效

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/app/security.py:39 + app/deps.py:76`
- **现象/证据**：JWT 有效期 24 小时（config.py 第 47 行 jwt_access_expire_min=1440），HS256 无状态签名。全代码搜不到任何 jti（token 唯一 id）/ blacklist / denylist / 吊销表（grep 无命中）。好的一面：deps.py 的 get_current_teacher（第 94-99 行）每次请求都重新 `db.get` 读教师并检查 `status != 'active'`，所以把教师停用（status 改非 active）或删除能即时挡住——这点做得对。坏的一面：单纯「改密码」或「角色降权后想强制对方重登」没有任何机制能让已签发的 token 立即作废，只能等 24h 自然过期；而且 token 一旦泄露（比如审核员 token），在过期前无法吊销。
- **影响**：高权限教师 token（能改判扣分、发注册码、删教师）如果泄露或设备丢失，最长 24 小时内仍然有效且无法主动踢下线。对宿舍这种规模风险可接受，但属于上线时该知道的安全边界。注意：靠 status='active' 检查已经覆盖了「停用账号即时生效」这个最重要的场景，所以不是 blocker。
- **建议**：v1.0 可接受现状（status 检查已兜住停用场景），但建议：(1) 在 BACKEND_DESIGN_LOG 明确记一句「token 无吊销、靠 status 兜停用、密码改了不强制重登」作为已知边界；(2) 把 24h 有效期考虑缩短（比如 8h）降低泄露窗口；(3) v1.1 如要真吊销，加 token jti + 一张 revoked 表或在 Teacher 上加 token_valid_after 时间戳。
- **复核结论**：confirmed

### [SEC-6] GET /teachers/public 无认证暴露全体教师姓名+寮+最后登录时间

- **维度**：后端认证与权限安全
- **位置**：`03_dev/backend/v1/app/routers/teachers.py:191`
- **现象/证据**：GET /teachers/public 无任何认证（list_teachers_public 第 192 行只有 db 依赖，没有 get_current_*），任意匿名调用者能拿到全部 active 教师的 id（UUID）+ name（真实姓名）+ assigned_dorm + last_login_at。schema TeacherPublicOut（schemas.py 第 728-738 行）确实刻意不返 login_id/email/role/status（防爬虫枚举登录名爆破），这点是对的。但仍然把「在职教职员真实姓名名单 + 各自最后登录时间戳」暴露给整个互联网。这是 5-27 拍板的实名登录方式刻意设计（登录页第一屏要显示老师卡片列表）。
- **影响**：属于轻度信息泄露：攻击者能拿到职员实名通讯录 + 谁今天上没上线的活动规律，可用于社工/钓鱼定位。但拿不到登录名/密码/角色，不能直接越权，宿舍场景风险有限。是「设计取舍」不是「实现 bug」，所以只列 minor 供 itsuki 知情决策。
- **建议**：如果接受『登录页就是要给学生/家长看老师卡片』这个产品决策，可保留现状，但建议至少去掉 last_login_at（最后登录时间对匿名访客没有产品价值，纯泄露作息）。如果想更稳，可加一道极轻的限流或要求一个固定的客户端标识，挡住批量爬虫。
- **复核结论**：confirmed

### [BL-9] study 出席判定边界把恰好 19:40 整判为迟到，与一本道阈值定义可能不符

- **维度**：后端业务逻辑正确性
- **位置**：`03_dev/backend/v1/app/routers/study.py:270 (create_checkin) 对照 today_attendees:208-227`
- **现象/证据**：第270行 `determined_status = 'present' if checked_at < study_start else 'late'`，study_start = 19:40。即恰好 19:40:00 签到判 late。点呼端 create_checkin（rollcall.py:316）用的是 `now <= scheduled_on_time_end` 判 present（含等号）。两端对「边界时刻算不算准时」的口径不一致（study 用 <，点呼用 <=）。spec §7.3 未明确 19:40 整点归属。
- **影响**：恰好卡点签到的学生在 study 被判迟到、在点呼会被判准时，两端体验不一致，且 study 边界从严可能误扣 1.5 点。属小概率边界但会引发学生争议。
- **建议**：与 itsuki 确认 19:40 整点该算准时还是迟到，统一 study 与点呼两端的边界比较符号（建议都用 <=，整点算准时），并在 spec §7.3 写明边界归属。
- **复核结论**：confirmed

### [EP-2] 食堂食数 Excel 导出（§7.7）后端做完了但前端完全没接，老师没法用

- **维度**：设计要求 vs 实装差距
- **位置**：`03_dev/backend/v1/app/routers/meals.py:67（后端有）vs 03_dev/teacher_web/v1/src/api/client.js（无 meals helper）`
- **现象/证据**：后端 meals.py 第 67 行有真实的 GET /api/v1/meals/export，用 openpyxl 生成真 .xlsx 流返回，完成度高。但前端接口层 client.js 里没有任何 meals 相关 helper（grep client.js 的 helper 列表里没有 meals/export/食数）。前端 index.html 里搜「meals」7 处全是 applications 页里的 mock 字段（如 meals: {breakfast:1,lunch:2}，第 16899/16933 行），没有任何「食堂食数页」或「Excel 导出按钮」调用后端。system_features.md §7.7 要求老师 Web「按钮按下 → .xlsx 下载」，WEB_DESIGN_LOG.md 第 810 行把它列在 v1.0 实装清单里（「食堂食数 → 寮務 ダウンロード Excel button #7」）。
- **影响**：食堂食数导出是老师 4-29 提的 38 条要件之一（#7/Q7），spec 标 V1 且 WEB_DESIGN_LOG 列入 v1.0 范围。后端能力齐全但前端没入口，等于这个功能对老师不可见、不可用。食堂 iPad 也没法显示。属于「只做了后端没前端」类型缺口。
- **建议**：前端补一个 MealsPage（食数页），在 client.js 加 mealsCalc / mealsExport 两个 helper（对应后端 calc + export），导出按钮触发浏览器下载 .xlsx。工作量不大（后端已就绪，只需前端一个页面 + 2 个 helper）。若决定推迟则需在 spec §7.7 和 WEB_DESIGN_LOG §11 明确标 v1.1。
- **复核结论**：confirmed

### [EP-4] 寮監事務室 出寮者一覧（§7.8 R4 必读约束相关）前端完全没有页面

- **维度**：设计要求 vs 实装差距
- **位置**：`system_features.md §7.8 + WEB_DESIGN_LOG.md:809（要求 v1.0）vs 03_dev/teacher_web/v1/src/index.html（DormOutStay/出寮者一覧 搜索结果 = 0）`
- **现象/证据**：前端 index.html 里 grep「DormOutStay / 出寮者一覧 / 出寮者」全部 0 命中——这个页面根本不存在。后端也没有专门的 GET /apply/active?dorm= 出寮者一覧端点（applications router 里没有按 dorm 过滤的「当前在外学生一览」端点）。但 system_features.md §7.8 把它列为 V1 功能（寮監事務室 PC 用、要能打印、1·2 寮和 4 寮分开显示——直接关联 R4 硬约束），WEB_DESIGN_LOG.md 第 809 行也明确写在 v1.0 实装清单里（「● 寮監事務室 出寮者一覧 PC #22-#27 — 印刷可能 + 編集不可 + 1·2/4 寮分離」）。
- **影响**：出寮者一覧是老师 38 条要件 #22-#27、寮監事務室 PC 的核心功能，且直接体现 R4「1·2 寮 vs 4 寮分别表示」硬约束。前后端都没做，等于寮監在事務室没法确认当前哪些学生在外、没法打印。属于「spec 要求但完全没做」类型。考虑到它被 WEB_DESIGN_LOG 明确列入 v1.0，缺失影响上线完整度。
- **建议**：确认这是否真的 v1.0 必做（WEB_DESIGN_LOG §11 列了，但 §11.3 把很多页标 P3 范围）。若必做：后端加一个 GET 当前承认通过且在外期间内的学生一览（按 dorm_unit 过滤），前端加只读的出寮者一覧页 + window.print()。若决定 v1.1：在 spec §7.8 和 WEB_DESIGN_LOG 把它从 v1.0 清单移到 v1.1 并标注，避免「列了 v1.0 却没做」的对不上账。
- **复核结论**：confirmed

### [DEMO-2] 实时点呼座位板的 /events/latest 轮询循环每秒打 demo 后端，生产环境会持续 404 且座位变色靠假数据驱动

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/teacher_web/v1/src/index.html:12989-13044（LiveRollCall 组件内）`
- **现象/证据**：system_features.md §上线前必删清单没单列这条，但它跟第 1/3 条同源（都是 demo_server.py 的端点消费方）。第 12992 行的 `React.useEffect` 无条件起一个轮询（不受 `window.DEMO_MODE` 保护），第 13012 行 `fetch('/events/latest')`（demo_server.py 专属端点）每秒拉一次，第 13024 行用 `window.ACCOUNTS` 假数据 `.find(a => a.no === ev.no)` 把番号映射成学生再让座位变色 + 日语朗读。与此同时第 24514 行 App() 还另开了真正的 WebSocket（`openTeacherWS`）走 `/ws/teacher` 更新同一份 students 状态——也就是说真假两条点呼通道并存。
- **影响**：生产环境真后端（FastAPI）没有 /events/latest 这个端点，这个 effect 会每秒 fetch 一次拿到 404（控制台噪音、白白耗网络）。更糟的是它和真 WebSocket 通道并存：万一 demo_server.py 真被部署、或前端误连到它，座位颜色会被假 ACCOUNTS 数据驱动，跟真后端 WebSocket 推的真实打卡打架，造成座位状态错乱。这是 demo 通道没拆干净的隐患。
- **建议**：删掉第 12989-13044 行整个 /events/latest 轮询 effect（真实时点呼已经由第 24514 行的 WebSocket 通道接管）。如果想保留给 demo，必须用 `if (!window.DEMO_MODE) return;` 在 effect 顶部短路，并确认 demo_server.py 不进生产部署。
- **复核结论**：confirmed

### [DEMO-3] demo_server.py（内存模拟后端 + 无认证 /checkin 后门 + 局域网 IP 探测）整文件仍在仓库并被 tomoshibi CLI 当默认启动器

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/teacher_web/v1/demo_server.py:1-143 + 03_dev/teacher_web/v1/tomoshibi:108`
- **现象/证据**：system_features.md §上线前必删清单 Teacher Web 第 1 条写「整个文件 = 内存模拟后端 + /api/server-info（LAN IP 自动检测）+ 银行卡 NFC POST 接口，全删」。文件还在（142 行）。demo_server.py 第 76-96 行 `do_POST` 处理 `/checkin?no=XX`：没有任何认证，谁都能 POST 进一条打卡事件；第 50-59 行 `_lan_ip()` 探测内网 IP；第 101 行 CORS `Access-Control-Allow-Origin: *` 全放开。`tomoshibi` CLI 第 108 行 `exec python3 demo_server.py` 把它当 start 的默认动作。git ls-files 确认 demo_server.py 已提交进 public 仓库。
- **影响**：这是一个完全无认证、CORS 全开、带内网 IP 探测和伪造打卡接口的后端，被登记为「必删」却还在，而且是 CLI 一键启动的默认。只要它被误当成生产启动方式（CLI 名字叫 tomoshibi、看起来像正经启动器），就等于上线了一个谁都能伪造打卡、绕过所有权限的后门服务。即使不部署，它在公开仓库里也是给攻击者的现成攻击脚本说明书。
- **建议**：上线前删掉 demo_server.py，或挪进明确的 demo/ 隔离目录并在 tomoshibi CLI 里改掉默认 start 行为（改成静态 http.server 或指向真后端）。当前根目录的「启动老师网站.command」其实已经用 `python3 -m http.server` 起前端（不是 demo_server.py），说明 demo_server.py 已经名存实亡，可以放心删。
- **复核结论**：confirmed

### [SEED-1] backend/v1/seed.py 的 dev 种子函数漏导入 ZoneInfo，运行到点呼 session 时直接崩（NameError）

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/backend/v1/seed.py:24 + 176`
- **现象/证据**：第 176 行 `datetime.now(ZoneInfo('Asia/Tokyo'))` 用到了 `ZoneInfo`，但全文件 import 只有第 24 行 `from datetime import date, datetime, timezone, timedelta`，没有 `from zoneinfo import ZoneInfo`。我用 AST 解析确认 import 进来的名字里没有 ZoneInfo，结论是 seed_dev 跑到第 176 行必抛 `NameError: name 'ZoneInfo' is not defined`。而且第 174 行还定义了 `JST = timezone(...)` 但下面没用它（本意应该是用 JST 而不是 ZoneInfo）。
- **影响**：dev 种子（灌测试学生/老师/点呼场次）会在建点呼场次那一步崩溃，前面的学生和老师虽然已 commit、但点呼 session 灌不进去，开发环境数据不完整。这不直接挡生产上线，但说明 seed.py 没被真正跑通验证过，降低对整个 seed 流程的信任度（包括 production 分支）。
- **建议**：在第 24 行下面加 `from zoneinfo import ZoneInfo`，或者干脆把第 176 行 `ZoneInfo('Asia/Tokyo')` 改成已定义的 `JST`（第 174 行那个 timezone 对象），二选一。改完真跑一遍 `APP_ENV=dev python -m seed` 确认不报错。
- **复核结论**：confirmed

### [SEC-1] 公开仓库 _legacy 旧 JSX 副本里残留明文共用密码 12345678（虽不被 index.html 加载）

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/teacher_web/v1/src/components/_legacy/theme.jsx:31 + login.jsx:21,75`
- **现象/证据**：`_legacy/theme.jsx` 第 31 行 `window.SHARED_PASSWORD = '12345678';`，`_legacy/login.jsx` 第 21 行用它做老师登录校验、第 75 行直接把 `demo: tomoshibi / {window.SHARED_PASSWORD}` 显示在登录页。这就是 FC-024 当年的明文共用密码漏洞。好消息：grep 确认 index.html（权威源）已不加载 _legacy（FC-024 已在主文件修复，第 10036 行有删除注释）。坏消息：git ls-files 确认这些 _legacy 文件都已提交进 public 仓库（otogi2025/DMSD 是公开的）。
- **影响**：因为 index.html 不加载 _legacy，所以这不是运行时漏洞（生产跑不到这段）。但密码 12345678 明晃晃躺在公开仓库的历史副本里，任何看仓库的人都能看到这是项目曾用过的共用密码模式；若该密码在某处仍被沿用就是真泄漏。属于「该清理的死代码 + 轻度信息泄漏」。
- **建议**：上线前把 _legacy/theme.jsx 第 31 行的明文密码删掉或改成占位（如 `window.SHARED_PASSWORD = '';`），登录用的 _legacy/login.jsx 已经被 index.html 内联版取代，整个 _legacy 目录可以考虑移到 99_archive 归档（它只是设计源副本，不参与运行）。
- **复核结论**：confirmed

### [SEC-2] seed.py 的 production 兜底密码 / reviewer 注册码 / 真实邮箱写死在公开仓库（有 env 覆盖 + warn 缓解）

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/backend/v1/seed.py:226,251,257,276`
- **现象/证据**：第 226 行 admin 邮箱写死 `otogi2025@gmail.com`（itsuki 真实邮箱）；第 251 行 reviewer 密码 fallback `Tomoshibi-Reviewer-2026!`；第 257 行 reviewer 注册码 fallback `999999`；第 276 行 admin 初始密码 fallback `ChangeMe-2026-05`。这些都在 public 仓库可见。缓解措施做得不错：第 250/256/276 行都从 env 变量优先读，第 264-281 行 seed_prod 跑时若用的是 fallback 会打 warning 提醒上线前必设 env。
- **影响**：因为有 env 覆盖 + warn，正常上线流程（设好 env）下不会用这些 fallback，所以不是 blocker。但只要 ops 漏设一个 env，对应的弱密码/已知注册码就静默生效——而 999999 注释自己写「public repo 已知」。真实邮箱写死也是轻度隐私泄漏。
- **建议**：把这几个 fallback 默认值的危险度再降一档：reviewer/admin 密码和注册码的 env 没设时，production 分支直接 raise 拒绝跑（跟 config.py 的 fail-fast 风格一致），不要只 warn 然后继续灌。真实邮箱建议也改成从 env 读或用占位邮箱。
- **复核结论**：confirmed

### [DEMO-4] backend/demo/（含明文密码 teacher/1234 + 假 token + 无认证 checkin）与 v1 共存，未列入任何上线删除清单

- **维度**：demo 残留 + 上线前必删项 + 假数据
- **位置**：`03_dev/backend/demo/main.py:50,55-58,120 + system_features.md §上线前必删清单`
- **现象/证据**：demo/main.py 第 50 行 `DEMO_TEACHER = {'username': 'teacher', 'password': '1234'}` 明文，第 55-58 行登录成功返回假 token `'demo-token-' + 时间戳`，第 120 行 `/api/checkin` 无认证。seed 也是裸名字假学生（itsuki/張三/李四…）。我确认 backend/v1/app 不 import backend/demo（grep 为空，两套不交叉），且 demo/.gitignore 正确排除了 *.db（不会提交假库）。但 system_features.md 必删清单只点名了 teacher_web/demo/（第 4 条），没提 backend/demo/。
- **影响**：按任务约定 demo/ 的问题不算 v1.0 缺口，且它跟 v1 物理隔离、不被引用，所以是 minor。但它跟 teacher_web/demo/ 一样属于「演示版残留代码」，必删清单里漏登记 backend/demo/ 是个一致性疏漏——清理时容易漏掉它，留在公开仓库里同样是一份「明文密码 + 无认证打卡」的攻击说明书。
- **建议**：在 system_features.md 必删清单的 Backend/Teacher Web 部分补登一条 backend/demo/ 整目录（跟 teacher_web/demo/ 同处理：上线前整个归档或删除）。它本身代码不用动（demo 用、已隔离），只是要纳入清理清单别漏。
- **复核结论**：confirmed

### [EP-2] README 自相矛盾且严重失实（demo_server.py 状态/行数/路径全错）

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/README.md:26,28,47`
- **现象/证据**：README 第 47 行写「demo_server.py 不存在」+「当前 ./tomoshibi start 跑 python3 -m http.server 只做静态」——但 demo_server.py 文件真实存在（142 行，5302 字节），且 tomoshibi CLI 第 108 行实际是 exec python3 demo_server.py（不是 http.server）。第 26 行写「index.html 单文件 7700+ 行」——真实 25211 行（差 3 倍多）。第 28 行写 JSX 源在 src/_legacy/——真实路径是 src/components/_legacy/。同一个 2026-05-28 17:33 的提交里 DESIGN_BRIEF.md 已经把这些都校准对了（第 7/28/34 行），唯独 README 没跟着改。
- **影响**：README 是「下次想看怎么打开」的第一手说明文档。零基础的 itsuki 照着错信息走会困惑：以为 demo 点呼功能失效（其实正常）、以为文件只有 7700 行（实际 25211）。同一提交里 DESIGN_BRIEF 对了 README 错了 = 文档之间互相打架，谁是真值说不清。
- **建议**：按 DESIGN_BRIEF.md 第 7/28/34 行的已校准内容同步修 README：demo_server.py 改成「存在、142 行、tomoshibi start 跑它」、行数改 25211、JSX 路径改 src/components/_legacy/。
- **复核结论**：confirmed

### [ZH-1] index.html 约 31 行英文代码注释，违反「注释 100% 中文」铁律

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/src/index.html:9984,9985,11482,11483 等约 31 处`
- **现象/证据**：用 grep 统计 index.html 里纯英文（不含中日文字）的 // 注释行约 31 行，例如第 9984 行「// Tomoshibi (灯火) Round 3 theme — extends Ryo tokens from Round 2.」、第 11482 行「// Shell — left nav + topbar with global search + WS indicator + logout.」、第 13789 行「// Override modal — extended with pending leave request...」、第 19002 行「// Seed data」等。项目 CLAUDE.md 规定「代码注释 + 内部文档 100% 中文 / UI 字符串保持日语」。注意：UI 显示文案确认是日语（如「完了」「教員を追加」「氏名」），这条只针对注释。
- **影响**：违反项目中文铁律，但属代码注释不影响运行也不影响上线功能。项目自己装了 post-edit-japanese-comment-check.sh 钩子扫日语注释，但英文注释没被这个机制拦住。对零基础的 itsuki 来说英文注释也比中文难读。
- **建议**：低优先级。上线不阻断，可在某次顺手维护时把这 31 行英文注释翻成中文。也可考虑让现有注释检查钩子顺带扫纯英文注释。
- **复核结论**：confirmed

### [ZH-2] _legacy 旧版 jsx 约 29 行英文注释（已脱节归档文件）

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/src/components/_legacy/*.jsx 约 29 处`
- **现象/证据**：_legacy/ 下 14 个 jsx 共约 29 行纯英文 // 注释，如 theme.jsx「// Adds: late state, timing constants...」、shell.jsx「// Shell — left nav + topbar...」、app.jsx「// App root — router, state, auto-logout timer, demo toast.」、accounts.jsx「// mock activity」「// newest first」。这些文件是 2026-04-30 的旧版，已不被 index.html 加载（grep 确认无任何地方 import _legacy）。
- **影响**：同样违反中文铁律，但这是已脱节的历史归档副本（EP-3 已说明它跟 index.html 脱节），不参与运行、不影响上线。修不修都不影响 v1.0。
- **建议**：最低优先级。如果按 EP-3 把 _legacy 定性为纯历史归档，这些英文注释可以不管；真要清理就翻译或干脆删掉这批不再用的源副本。
- **复核结论**：confirmed

### [EP-4] index.css 是废弃的 Vite 残留（含 CDN 字体引入 + Tailwind 指令），但根本没被加载

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/src/index.css:1-5`
- **现象/证据**：index.css 第 1 行 @import url("https://fonts.googleapis.com/css2?family=Noto+Sans+JP...")（从 Google CDN 在线拉字体），第 3-5 行是 @tailwind base/components/utilities（需要 Tailwind 编译器才能展开的指令）。但 grep 确认 index.html 没有任何 <link> 或引用指向 index.css——它根本不会被加载。这是已废弃 Vite 工程时代的遗留文件，DESIGN_BRIEF/WEB_DESIGN_LOG 仍把它列在「保留」清单里。
- **影响**：对当前 standalone 单文件加载没有任何实际影响（index.css 不被加载，所以它的 CDN 字体引入和 Tailwind 指令都不会执行——真正的字体是 index.html 里内联的本地 woff2）。隐患在于「文档说保留它」会让人误以为它还有用；万一未来有人把它 <link> 进 index.html，就会引入一个离线打不开的 CDN 依赖 + 一堆没编译的无效 Tailwind 原始指令。
- **建议**：确认 index.css 已无用后从 src/ 删掉（或移到归档），并从 DESIGN_BRIEF/WEB_DESIGN_LOG 的「保留」清单里移除，避免误导。本身不阻断上线。
- **复核结论**：confirmed

### [EP-5] DESIGN_BRIEF 承诺的离线备份文件 standalone-offline-backup.html 从未创建

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/DESIGN_BRIEF.md:126`
- **现象/证据**：DESIGN_BRIEF.md 第 126 行写「CDN 断（Google Fonts / unpkg React 不可达）：改打开 standalone-offline-backup.html —— 8.4MB 完全内嵌，无外部依赖」。但在整个 teacher_web 目录下 find 查找 *offline* / *backup* 没有任何文件——这个声称的离线兜底文件根本不存在。
- **影响**：文档承诺了一个离线兜底方案但东西没做。好消息是：经核查 index.html 本身已经是完全本地化的（React/Babel/字体全是本地副本，无实际 CDN 加载），所以离线打开本来就没问题，这个备份文件其实不必要。问题只是文档写了不存在的东西，会让人去找一个找不到的文件。
- **建议**：既然 index.html 已经离线可用，删掉 DESIGN_BRIEF 第 126 行那段关于 standalone-offline-backup.html 的描述（或改成「index.html 本身已全本地内嵌、离线可直接打开」）。不阻断上线。
- **复核结论**：confirmed

### [EP-6] head 残留两行 Google Fonts preconnect 预连接（无害但与离线声明不一致）

- **维度**：前端可加载性 + 中文铁律一致性
- **位置**：`03_dev/teacher_web/v1/src/index.html:11-12`
- **现象/证据**：index.html 第 11-12 行有 <link rel="preconnect" href="https://fonts.googleapis.com"> 和 fonts.gstatic.com。preconnect 只是「提前跟这个域名握手」的性能优化提示，不实际下载任何字体（真正的字体是 head 里内联的 520 处本地 _assets/*.woff2 引用，已验证）。
- **影响**：完全不影响离线加载——preconnect 失败浏览器静默忽略，页面照常渲染本地字体。唯一影响是：联网时浏览器会徒劳地去跟 Google 域名握手一下（轻微无意义的网络动作），且跟「无外部依赖」的设计目标字面上不符。
- **建议**：纯洁癖级别。删掉这两行 preconnect 即可彻底无外部域名痕迹。不删也完全不影响上线。
- **复核结论**：confirmed

---

## 完整性批判 — 盲区补充

Confirmed: `broadcast` ignores `assigned_dorm` entirely ("当前广播全部" = broadcasts to all). A female-dorm teacher receives live check-in events for male-dorm students over WS — a multi-dorm isolation leak the 8 dimensions didn't catch (the list only covers REST endpoint filtering, not the WS channel). I have enough. Here are the blind spots.

---

以下是清单**没覆盖到**的新盲区。我已逐条 Read 源码核对，没编造。

**RUN-N1 没有任何生产部署制品（Docker / systemd / nginx / gunicorn 全缺）** — blocker｜整个仓库（`find` 全空，`04_ops/` 只有 `MAC_MINI_SETUP.md` + `wifi_survey_howto.md`）｜后端只有 `uvicorn app.main:app --reload` 这种开发跑法（写在 `app/main.py` 顶部注释里），没有任何「怎么在真机器上把服务长期跑起来、崩了自动重启、开机自启」的东西。老师网页要在宿舍天天用，电脑一重启服务就没了，没人会手动敲命令。建议：补一个 systemd service 文件（让服务开机自启 + 崩溃自动拉起）或 Docker 容器配置，写进 `04_ops/`。

**RUN-N2 全链路没有 HTTPS，登录密码和令牌明文过网** — blocker｜`app/main.py:121`（uvicorn 裸 http）+ `client.js:266`（前端只是「如果当前是 https 就用 wss」，自己不提供 https）｜老师登录走 `POST /sessions/teacher`，密码在请求体里；登录后拿到的 JWT（令牌，相当于通行证）每次请求都带。没有 HTTPS（加密传输）的话，同一个 Wi-Fi 下任何人都能抓到老师密码和令牌，直接冒充老师改判 / 发邀请码。宿舍 Wi-Fi 是共享网络，这是硬伤。建议：上线前必须在前面架一层带证书的反向代理（nginx + Let's Encrypt 免费证书），所有流量走 https/wss。

**RUN-N3 teacher_web 没有「生产怎么 serve」的方案，只有 demo 的 `python3 -m http.server`** — blocker｜`03_dev/teacher_web/v1/tomoshibi:108`（`exec python3 demo_server.py`）+ `README.md:7,14`｜启动老师网页的唯一办法是跑 demo 脚本或双击 `.command` 起 `http.server`（一个零安全、零并发、专给本机调试用的 Python 内置小服务器）。它不支持 HTTPS、不能扛多人同时访问、进程一关就没。这跟 RUN-N1/N2 是一套问题但针对前端：前端也没有生产托管方案。建议：前端静态文件交给跟后端同一个 nginx 托管（同源还顺带解决 CORS 跨域问题）。

**SEC-N1 登录返回的令牌 24 小时就硬过期，没有续期端点，老师每天被强制重登** — major｜`config.py:47-48`（定义了 `jwt_access_expire_min=1440` 和 `jwt_refresh_expire_min=43200`）+ `routers/auth.py`（全文没有 `/sessions/refresh` 端点，我搜过确认不存在）｜`.env.example:24` 里煞有介事地配了「刷新令牌 30 天」，但后端根本没有「拿旧令牌换新令牌」的接口，也没签发刷新令牌。结果：那个 30 天配置是死的，老师每过 24 小时令牌一过期就被踢回登录页，正在做的点呼 / 改判操作直接 401 失败。日常使用体验断点。建议：要么补一个刷新端点，要么把过期时间调长并明确告知「每天要重登一次」是预期行为。

**SEC-N2 WebSocket 实时点呼板对所有老师无差别广播，女寮老师能收到男寮学生的实时签到** — major｜`app/ws_manager.py:71` `broadcast()`（遍历 `self._conns` 全推，完全没看 `assigned_dorm`）+ 该文件第 13 行作者自己注释「每个连接带 teacher_id（供未来按 dorm 过滤 — 当前广播全部）」｜连接时明明记录了每个老师的 `assigned_dorm`（负责哪个寮），但广播时无视它。这是 R4 寮隔离约束（老师只能看自己负责寮的学生）在 WebSocket 通道上的漏洞——REST 接口那 8 个维度审到了寮过滤，但实时推送通道没人审。男女寮学生信息互相泄露。建议：`broadcast` 按事件里的 `dorm_unit` 跟连接的 `assigned_dorm` 比对，只推匹配的老师。

**LOGIC-N1 学习室出席（study）实时推送完全没接，老师盯的是不会自动刷新的死页面** — major｜`app/routers/study.py`（全文 0 处 `broadcast` 调用，我 grep 确认；只有 `rollcall.py` 和 `applications.py` 调了 `_ws.manager`）｜点呼（rollcall）签到会触发 WebSocket 推送，但学习室出席（study/checkins）一个推送都没有。老师在「今日学習出席」页等学生刷卡，画面不会自己变——除非手动刷新整页。这是功能性断点，清单里只提了「rollcall 的 WS 前缀错」，没人注意到 study 压根没接 WS。建议：study 的 `create_checkin` 也调 `broadcast_sync` 推一个 study 出席事件。

**LOGIC-N2 `broadcast_sync` 在同步路由里大概率根本发不出去（事件循环陷阱）** — major｜`app/ws_manager.py:86-99`（`asyncio.get_event_loop()` + `loop.is_running()`）｜后端用的是同步路由（`def` 不是 `async def`），FastAPI 会把这种路由丢到独立线程池里跑。那个线程里**没有运行中的事件循环**，所以 `asyncio.get_event_loop()` 在 Python 3.11（你的环境实测 3.11.5）会走到 `except RuntimeError` 分支被「静默跳过」——日志只 debug 一句就没了。意思是点呼签到的实时推送很可能压根没真发出去，但代码看起来「调了广播」，排查时极难发现。这跟清单里「WS 少了 /api/v1 前缀连不上」是两个独立问题：就算前缀修了、连上了，服务端这边也推不出来。建议：用 `diagnose` skill 真起服务 + 真连一个 WS 客户端验证签到事件能不能收到，别只看代码。

**LOGIC-N3 出寮届邮件通知发给「审批链上的老师」，不发给学生家长，且学生 email 字段允许为空** — major｜`models.py:65`（`Student.email` 是 `Optional`，可为 NULL）+ `email.py:156`（收件人为空时记 `"chain 上の役职に email 登録なし"`）｜出寮届（学生申请离开宿舍）的通知收件人是审批链上的教师邮箱，不是家长/学生本人。而教师 email 没登记就整封邮件发不出去（只在 `notification_log` 记一条 failed，业务不报错继续走）。上线时如果 seed 进来的老师没填 email，所有出寮届审批通知会静默丢失，老师以为没人申请。建议：上线前确认每个有审批权的老师都填了真实可收邮件的 email，并加一个「审批链上无人有 email」的显式告警，而不是埋在日志里。

**SEC-N3 全后端没有任何接口限流（仅教师登录有 3 次锁定，其余裸奔）** — major｜`routers/auth.py:27`（只有教师登录做了失败计数锁定）+ `requirements.txt`（无 slowapi 等限流库）｜除了教师登录失败锁 30 分钟，其他所有接口——学生登录、注册码刷新、公告发布、改判——都没有速率限制。学生登录接口可被无限次暴力试密码（学生端没有锁定逻辑，我在 `login_student` 里确认没有失败计数）。公开网络上线后，学生账号能被批量爆破。建议：至少给学生登录和注册码相关接口加基础限流。

**RUN-N4 生产数据库从空库到可用没有「初始化跑通」的闭环文档** — major｜`alembic/versions/`（有 10 个迁移文件）+ `seed.py:261` `seed_prod`（只灌 1 个 admin 老师 + 1 个 reviewer 学生）｜迁移脚本和生产 seed 都在，但缺一份「在生产 Postgres 上：先 `alembic upgrade head` 建表 → 再 `APP_ENV=production python -m seed` 灌初始管理员 → 然后怎么把全校真实学生名簿导进去」的连贯操作清单。`seed_prod` 只造一个管理员，真实几百个学生的名簿从哪来、怎么批量导入，全项目没看到入口（清单里 SPEC 维度提的「学号一括进级」是另一回事）。结果：服务能起来，但库里没有真实学生，老师登录后点呼板是空的——这是「老师登录后拿不到学生名单」的根因之一。建议：写一份生产初始化 runbook，并明确真实学生名簿的导入方式。

**LOGIC-N4 `study.py` 自己重写了一套寮过滤逻辑，没复用公共的 `dorm_units_for_teacher`** — minor｜`routers/study.py:137-147`（内联 `if teacher.assigned_dorm == 1: ...`）对比 `deps.py:24` 的公共函数 `dorm_units_for_teacher`｜寮过滤这种安全相关逻辑有两份实现，一份在公共函数、一份在 study 里手抄。哪天规则变了（比如新增寮号）改了公共函数忘了改 study，study 的寮隔离就会悄悄错位。这是隐患不是当前 bug，但属于「多寮隔离」维度没人提的复制粘贴风险。建议：study 改成调用 `dorm_units_for_teacher`，消灭第二份实现。

**SEC-N4 CORS 配置 `allow_credentials=True` + 通配方法/头，生产校验只拦 origin 通配但放过这个组合** — minor｜`app/main.py:79-81`（`allow_credentials=True` 配 `allow_methods=["*"]` + `allow_headers=["*"]`）｜生产校验（`config.py:94`）只检查 origin 不含 `*`，但 methods/headers 全通配 + 允许携带凭证的组合本身偏宽松。origin 白名单对了就不算严重漏洞，列为 minor 提醒。建议：生产把 methods/headers 也收敛到实际用到的几个。

**说明**：以上是站在「真上线给老师天天用」角度补的盲区，跟你给的清单不重复。最该先处理的是 RUN-N1/N2/N3（部署 + HTTPS + 前端托管）——这三条不解决，系统连「能在宿舍长期跑起来且不泄露密码」都做不到，比清单里任何单个功能缺口都更卡上线。

---

## 被判为误报、已剔除的 7 条

- **[FE-6] 3 个申请 tab（帰国/帰省/タクシー）仍是「開発中」空壳** — 剔除理由：误报,被代码直接证伪。

核对位置 03_dev/teacher_web/v1/src/index.html 的 ApplicationsPage 组件(16361 行起)和 tab 渲染区(16475-16499 行):

1. 原报说「帰国/帰省/タクシー三个 tab 全走 SkeletonTabBody 空壳,只有外泊真接后端」——事实相反。实际渲染:
   - outstay(外泊,16475-16482 行)→ OutstayList 组件 + outstayApps
   - return(帰国,16483-16490 行)→ OutstayList 组件 + returnApps
   - home(帰省,16491-16498 行)→ OutstayList 组件 + homeApps
   - taxi(タクシー,16499 行)→ 唯一一个走 SkeletonTabBody 空壳
   外泊/帰国/帰省三个 tab 全部接了后端真数据:16367-16378 行调 _adaptBackendAppsByKind(backendApplications, "外泊"/"帰国"/"帰省") 从后端 pendingForMe 返回的 Application[] 里按 kind 分别过滤。三个 tab 复用同一个真列表组件 OutstayList(16575 行定义),有 pending/approved/rejected/question/all 子筛选、点击 onOpen(a) 开详情(16680 行)、详情里有「承認/却下」按钮(index.html 13954/13970 行)和保存反映逻辑。功能跟外泊完全一致。

2. 唯一空壳 taxi 是设计决策,不是遗漏。后端数据模型 03_dev/backend/v1/app/models.py:209 写死 APPLICATION_KINDS = ("帰省", "外泊", "帰国"),:284 加了 CheckConstraint("kind IN ('帰省','外泊','帰国')");schemas.py:182 的 discriminated union 也只有这三种 Literal。后端根本没有 タクシー(出租车)这个申请类型。index.html:16323 注释明确:「taxi は backend kind に無いので Skeleton 占位のまま (システム外、Round 4 議題)」。

3. 因此原报「影响」段的断流推断也不成立:学生 iOS 端无法提交出租车申请(后端不接受该 kind),所以不存在「学生提交了没人处理」。

补充(不改变 refuted 判定):帰国/帰省复用 OutstayList 时,外泊专属的提交期限规则横幅 OutstayRuleBanner 只在 outstay tab 显示(16470-16471 行,注释「帰国/帰省はルール異なる」);各 kind 详情里的专属字段(外泊滞在先 / 帰国航班)是否在 return/home tab 正确渲染我没逐字段核对。但这属于字段渲染细节,跟原报主张的「整 tab 是空壳」完全两回事,不支撑 FE-6。

结论:原报把「1 个 tab 是占位(且对应后端类型不存在)」夸大成「3 个 tab 是空壳」,核心证据失实,corrected_severity 给 none。
- **[BL-1] 出寮届承认链完全不校验顺序，任何角色可越级抢先批/拒** — 剔除理由：代码现状描述属实但结论错误，判定为误报。

【代码核对属实部分】decide_approval（applications.py:476-483）确实只按 `r.approver_role == teacher.role and r.decision is None` 找待审行，不看 chain_order、不检查前序是否已批；build_chain（approval_chain.py:149-159）确实给每行写 chain_order=idx。这两点原报说的没错。

【但前提（spec 要求逐级顺序审批）不成立】我通读了 spec §7.2.2（02_design/system_features.md:361-388）、§7.2.6（440-454）、schema、models.py、tests，全项目没有任何一处写「承认链必须逐级、必须等前一级批完才能批下一级」。相反证据全部指向「并行审批」设计：
1. §7.2.2 第384行「提交时给上述役职发邮件」+ collect_recipients（approval_chain.py:166-184）一次性收集 chain 上所有役职的邮件 → 提交那一刻所有役职同时收到通知各自批，不是「上一级批完才通知下一级」。
2. chain_order 的真实用途在 §7.2.6 和 models.py:280 `order_by="ApplicationApproval.chain_order"` 里有明确定义：它是 UI 进度条显示顺序 / DB 行排序 / 邮件接收顺序用的。§7.2.6 第452行「顺序无关——无论 approve 时间顺序如何，进度只往右填」恰恰反过来证明设计有意允许任意时间顺序批。原报把这个 UI/排序字段误读成「强制逐级审批的业务契约」。

【核心影响论断被代码直接推翻】原报说「校長/管理係越级先批 = 放行外出 = 审批形同虚设」。但 _recompute_application_status（applications.py:532-542）逻辑是：任一 approve → approved_partial，**全员 approve 才** approved，任一 reject → rejected。也就是说哪怕校長抢先批了，只要担任还没批，整体 status 仍是 approved_partial（未放行）。真正放行（status=approved）的闸门要求 chain 全员都同意——这道安全闸门没有失效。「越级抢批就放行」的灾难场景不存在。

【旁证】§7.2.4 修改届「Chain 重置规则」（systen_features.md:421-424）：学生改字段后 chain 全员回到未批、已批役职重新看。这也是并行模型的特征（严格逐级模型只需从改动点往后重走）。

结论：原报把 UI/邮件/排序用的 chain_order 误当成「强制逐级审批」业务规则，且忽略了「全员 approve 才生效」这道实际闸门。任何役职可在别人之前批自己那一栏是设计意图（spec 顺序无关 + 全员同时收邮件），不是 bug。不影响上线，corrected_severity 给 none。
- **[BL-4] 教师改判取错「原始状态」，二次改判/旧 event 改判时扣分联动算错** — 剔除理由：我逐行核对了 rollcall.py:561-627（patch_event）+ 491-555（_OVERRIDE_DEMERIT_MAP 和 _apply_override_demerit）+ 365-428（board 接口）+ schemas.py:644-674 + 前端 index.html:24688-24895 + client.js:146。原报 BL-4 的两个核心指控都站不住。

【指控A「对旧行 PATCH 取历史值」— 业务流程不可达】board 接口（rollcall.py:385-419）对每个学生只挑「最新一行 event」（按 checked_in_at 比大小，第393-397行），第419行返回 last_event_id=最新行的 id。schemas.py:653 把它暴露成 last_event_id 字段。前端 index.html:24688-24690 注释写明「该学生最新 RollCallEvent.id — OverrideModal 调 PATCH 用」，lastEventId=e.last_event_id；第24871-24872行 patchRollcallEvent(target.lastEventId,...) 传的就是这个最新行 id。所以正常 UI 流程下老师 PATCH 的永远是最新一行，patch_event 第574行 old_status=event.base_status 取到的就是当前状态，不是历史值。原报设想的「老师对一条旧 auto event 发 PATCH」在前端根本拿不到旧行 id，只有绕过前端直接拼 API 才可达。

【指控B「连续改判/重复撤销」— 被代码里的过滤条件直接证伪】这是原报最具体的指控，原文「late→present 已撤销过一次，再 PATCH 旧行又会触发一次 -0.5 revoke」。但撤销分支（rollcall.py:540-555）的查询第546行带了 revoked_at.is_(None) 过滤——只捞「尚未撤销」的扣分行。一条扣分被撤销过后 revoked_at 已非空，第二次查询结果为空列表，第552行 for 循环空转，不会重复 -0.5。撤销操作天然幂等。我反复推演了 late→present 连续改判数据流，确认重复撤销不会发生。原报这个最有杀伤力的例子是错的。

【唯一残留的真实隐患（降级到 minor）】正 delta 加扣分支（第528-539行）每次都无条件 db.add 一行新 DemeritEvent，没有像撤销分支那样的幂等保护。理论上若同一对 (from,to) 被重复触发会重复加扣。但触发它需要：(1) 绕过前端直接对旧行拼 API（业务流程不可达）；(2) 还要过第607行 old_status != new_status 这道拦截。属「API 层缺幂等防护」的健壮性隐患，不是原报描述的「正常改判联动算错、规律分数据失真」的功能 bug。另外我确认 tests/test_rollcall.py 完全没有 patch_event/override/改判扣分联动的测试用例（只有第68行测了 checkin），这块零测试覆盖是真实的次要缺口。

综合：原报核心机制描述（重复撤销 + 正常流程取历史值）被代码证伪，major 评级明显偏高。保留「加扣分支无幂等 + 整块零测试」这个真实但低危、需异常 API 调用才触发的残留，定为 minor。
- **[BL-7] 结算/finalize 可重复触发导致重复扣分（无幂等/重判保护）** — 剔除理由：我打开两处源码逐行核对，原报告的两条核心证据都不成立，"误触两次按钮就重复扣分"的主断言被证伪。

【点呼侧 rollcall.py】end_session（189-215 行）入口第 196 行就拦 `if session.session_status != "running"`，不是 running 就返回 409 SESSION_NOT_RUNNING。第一次 end 成功时，第 206 行把 `session.session_status` 改成 "ended"，紧接着第 212 行调 `_settle_absent`（缺席学生写 absent event + 2 点 DemeritEvent），第 213 行一次 `db.commit()` 把"状态变 ended"和"扣分"一起提交。所以第二次再调 end_session，session_status 已是 "ended"，被 196 行直接挡住，根本走不到 _settle_absent。原报告说"只挡 != running，走过一次会再跑一遍"是错的——走过一次后状态恰恰就不再是 running 了。状态机已经天然保证每个 session 只 settle 一次。

【学习侧 study.py】bulk_finalize（299-388 行）确实没有"今日已 finalize"标记，老师能重复按。但我核对了重判逻辑 346-381 行：to_absent 只在两种情况追加——记录不存在（c is None，351 行）或记录存在且 `c.status == "init"`（362 行）。第一遍把缺席学生标成 absent 并 commit（383 行）后，第二遍是独立请求重新查 existing_map（339-344 行能读到第一遍提交的数据），这些学生 status 已是 "absent"——既不满足 c is None，也不满足 c.status == "init"，不进 to_absent，于是 370-381 行的 DemeritEvent 循环对它们不再扣分。原报告说"对仍 init/缺记录的学生再写 absent + 再加 1.5 点"——对第一遍已处理的学生，第二遍他们是 absent 不是 init，不会重扣。另外 StudyCheckin 有唯一约束 uq_sc_date (student_id, target_date)（models.py:561），数据库层也堵死了重复 absent 行。

【残留隐患】DemeritEvent 表本身确无唯一约束（models.py:1046-1053），重复防护全靠应用层 status 状态机；理论上高并发竞态（两请求在对方 commit 前都读到旧状态）下仍有极小重判可能，且代码缺显式幂等护栏（如"同 session/同日同 source 已存在则跳过"）。但这是边缘并发场景，原报告完全没论证并发、举的是"误触两次"的串行场景，而串行场景下两条路径都不会重复扣分。原 major（误触必重扣）评级失实，降为 minor。
- **[BL-8] 出寮届修改后旧承认行被物理删除，审批历史与已批意见丢失** — 剔除理由：证据本身属实（applications.py:393-394 确实 `for row in app.approvals: db.delete(row)` 物理删全部承认行再 build_chain 重建），但原报告把这个「设计行为」误判成了「bug」，方向恰好反了。

依据一（核心）：规格 02_design/system_features.md §7.2.4「Chain 重置规则(2026-04-30 後續 拍板「已批役职重新看」)」白纸黑字写：「修改后 → chain 全员回到未批状态(已批的役职要重新看一次)」「邮件通知触发：chain 上还没批的 + 已批的 都重新发」，理由是「学生改了字段后,已批的役职可能不同意新内容,必须重新确认」。§7.2.5 功能矩阵第 436 行也列「Chain 重置 + 邮件再送 → 后端 hook on PUT (V1)」。§1553 决策日志同样把「chain 重置」记为 4-30 第二轮拍板内容。代码删行重建（approval_chain.py build_chain 生成的新行 decision=None / decided_at=None / comment=None）正是实现「全员回到未批状态」。所以删除已批决策不是缺陷，就是规格明确要求的目的。原报告说「已审批进度被清空 = 缺陷」恰好说反了——清空就是设计意图。

依据二（评论 comment）：ApplicationApproval 确有 comment 字段（models.py:332），删行后旧评论确实没了，这点技术属实。但 spec §7.2.4 全文没有任何「修改届时保留已批老师评论」的要求。既然链是「全员重新看一次」，旧评论针对的是被改前的旧内容，按设计本就该作废重写。所以「评论丢失」不构成 spec 违反。

依据三（AuditLog）：spec §7.2.4「Audit log 可见性」明确 entry 形式只要求「谁 + 何时 + 改了哪个字段 + 旧值/新值」——是字段变更记录，不是审批决策记录。代码第 404-413 行确实写了 application.update 的 AuditLog（payload={"updated_fields": ...}）。spec 从没要求「把被作废的旧决策快照存进 audit」，原报告说的「无 AuditLog 记录被删了哪些决策」是它自行加码的需求，不是规格缺口。

依据四：原报告称「与 spec『老师后台看得到修改记录』相悖」也是理解反了——spec 要的「修改记录」= 学生改了哪些字段（已由 application.update AuditLog 满足），不是「保留旧审批决策」。

综上，BL-8 把规格定义的正确行为当成了缺陷，属于误报。（旁注：唯一沾边的真问题是 audit payload 只记字段名、没记旧值/新值，跟 spec §7.2.4「旧值/新值」要求有差距，但那是另一条独立 finding，不是 BL-8 所述的「删了哪些决策」，不影响本条 refuted 判定。）
- **[BL-10] study 一本道结算对外宿/欠席控除未按学生在册 dorm/term 一致性校验** — 剔除理由：我打开 /Users/kurekoduki/dev/DMSD/03_dev/backend/v1/app/routers/study.py:299-365 和 models.py 逐行核对，结论是这条基本属于误报（代码本身是正确的，原报也承认不会误扣，但它把这段说成"性能隐患/口径不统一"的批评站不住脚）。

核对到的事实：
1. 证据描述的代码现象属实：roster_ids 确实按 academic_term 取（study.py:310-317）；outstay_exempt 确实查全表 approved 且 leave_date<=today<=return_date 的出寮届（出寮届=请假/外宿/回国申请），没按 roster 学生收窄（study.py:328-336）；最后确实是 `if sid in exempt_ids: continue` 求交（study.py:347-348），所以不会误扣。这部分我确认无误。

但原报对这个现象的"定性"有三处错误，导致整条判断不成立：

第一，"无界查询 / 全表扫描"是错的。我在 models.py:290 看到 Application 表建了索引 idx_app_status_date，建在 (status, leave_date) 两列上。outstay_exempt 的查询条件正好是 `status == "approved"` 加 `leave_date <= today`，正好能用上这个索引（数据库按 status 等值 + leave_date 范围走索引）。所以根本不是"全表扫描""无界查询"，原报的核心技术论据不成立。

第二，"应该按 term（学期）对齐"在语义上是错的。我看了 Application 模型整段（models.py:220-291），它压根没有 academic_term 字段——出寮届天然是用 leave_date / return_date 这对日期表达有效期的，一张请假单跨学期很正常。出寮届免扣的含义是"今天这个学生人不在宿舍，所以学习不该算他欠席"，这跟学期无关。硬要求它跟按学期取的 roster"口径对齐"，本身就是误解了这两张表不同的设计意图。

第三，紧挨着的承认欠席届 exempt（study.py:320-327，查 StudyAbsenceRequest 当天 approved）同样没按 roster 收窄。说明作者一贯就是"先算出全量豁免集合，再跟 roster 求交"这个写法，不是 outstay 这一处特有的疏漏。原报只挑 outstay 一处批评，没看到这是统一的设计模式。

另外"混入大量非 roster 学生"被夸大了：豁免集合的实际行数 = 今天有出寮届/欠席届的学生数，这是一天请假人数级别的很小子集，不是"大量"；而且 roster 本来就包含全体中学生 + 部分高中生，请假的人多半本来也在 roster 里，收窄能省的几乎可忽略。

综上：代码功能完全正确（求交兜住），性能批评的核心证据（全表扫描/无界查询）因为有现成索引而不成立，语义批评（应按 term 对齐）因为 Application 模型本就不含 term 而不成立。这最多是一个极轻微的"理论上可以加 .where(student_id.in_(roster_ids)) 收窄"的代码风格建议，远够不上一个真实缺陷。
- **[EP-3] tomoshibi rebuild 命令读的源文件不存在，一跑就崩** — 剔除理由：我把 03_dev/teacher_web/v1 整个 src + tomoshibi 脚本复制到 /tmp 临时目录，实跑了 `./tomoshibi rebuild`：退出码 0，输出「✓ 18 components · 1019 KB」，生成的 index.html 跟原文件逐字节相同（diff 显示 IDENTICAL，25211 行不变）。原报「一跑就崩 / 直接报错 FileNotFoundError」是错的——根本没抛异常。

原因我也查清了。rebuild 第 161 行的折叠正则要求内联块以「\n</script>」结尾（换行后紧跟顶格的 </script>），但 index.html 里每个收尾标签都缩进成「    </script>」（前面 4 个空格）。所以第 161 行正则在整文件命中 0 次（我用 re.findall 验证：单行前缀 `data-source="components/..."` 能命中 15 次，但带 `\n.*?\n</script>` 的完整折叠命中 0 次；逐字打印 theme.jsx 收尾处证实是 `};\n    </script>`）。因为没有任何块被折叠成中间形态 `src="components/..."`，第 166 行那段唯一会去读 `src/components/X.jsx`（即原报说的缺失文件代码路径）的正则也命中 0 次，inline() 函数根本不执行。结论：这命令是个静默空操作（什么都没干），不是崩溃。

原报的几个事实观察本身属实：src/components/ 下确实只有 _legacy/ 子目录，没有顶层 components/*.jsx；index.html 里 18 个 data-source 引用 vs _legacy/ 只有 14 个 jsx，多出的 4 个（registration-code-panel / study-attendance-page / teachers-admin-page / roll-call-summary）确实只内联存在、没源副本。但这些只能支撑「这套 改 jsx → rebuild 内联 工作流已脱节」这个温和结论，不能支撑「一跑就崩」这个核心断言——真实失效模式是「rebuild 啥也不干」（死工具），不是报错。

更关键：tomoshibi 脚本第 3、22 行自己标明是「demo CLI · v0.1.0-demo」，不是 v1.0 生产路径；README 第 26、40 行也写明 index.html 单文件是设计权威、靠手改。所以对 v1.0 上线就绪度的影响基本为零，最多算「过时的 demo 开发辅助脚本 + README 路径写错（写成 src/_legacy/ 实际是 src/components/_legacy/）」这种小瑕疵。
