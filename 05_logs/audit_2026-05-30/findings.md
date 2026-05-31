# DMSD 全项目审查 findings — 2026-05-30
> 多代理审查产出（主会话编排）。两批 workflow：后端 5 单元 + 客户端/文档 10 单元成功。
> 6 单元卡死未出（ios-apply / ios-foundation / cross-end / spec-internal / design-logs / governance）→ 主会话另行补审。

**总计 175 条**：🔴 critical 12 / 🟠 high 33 / 🟡 medium 63 / ⚪ low 67

类别：bug=逻辑错 / security=安全 / consistency=不一致 / architecture=架构 / test=测试 / doc=文档

---

## 🔴 致命（阻塞上线）（12 条）

### [android-base-01] 注册流程完全没有后端强制要求的 6 位注册码字段
- **严重度**：critical | **类别**：consistency | **单元**：Android·基础层+接后端屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/account/AccountScreen.kt` : 44-58, 87-118
- **问题**：AccountScreen 的 4 步注册（基本情報 / 点呼区分 / 連絡先 / パスワード）里没有任何「注册码 / 登録コード」输入框，FormData 数据类也没有这个字段。但后端 schemas.py:804 明确要求注册时必传 registration_code（6 位数字、min_length=6 max_length=6、pattern ^\d{6}$），且 models.py:882 有 StudentRegistrationCode 表，注释写「学生注册码 App Store 上架对策，2026-05-03 itsuki 拍板」。
- **影响**：一旦 Android 接通后端，注册请求必然因缺 registration_code 字段被后端拒绝，整个注册功能无法工作。这是管理员发码控制谁能注册的核心防滥用机制，缺失等于 Android 端注册防线为零。
- **建议**：在 AccountScreen 增加注册码输入步骤（对齐 iOS 是否已做需确认），FormData 加 registrationCode 字段，提交时随注册请求发给后端校验。

### [android-base-02] 登录任意邮箱+空密码即放行，且会自动登录
- **严重度**：critical | **类别**：security | **单元**：Android·基础层+接后端屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/login/LoginScreen.kt` : 40-58, 153
- **问题**：submit() 只 delay(700) 然后无条件 store.update{ authed=true } 跳 Home，完全没有校验邮箱/密码，也没调任何后端。按钮 enabled 条件只看 email.isNotBlank()，密码可为空。第 53-58 行 LaunchedEffect 还会在 state.user.email 非空且未登录时自动 delay(1500) 调 submit() 直接登录。无失败次数锁定（与已知后端缺口「学生登录无失败锁定」呼应——客户端这边连密码都不发）。
- **影响**：当前任何人输入任意邮箱（甚至默认预填的 haruki@tomoshibi.jp）就能进入主界面。即使后端将来做了校验，客户端这套本地放行+自动登录逻辑也必须整段重写，否则会绕过后端鉴权。
- **建议**：submit 改为调用后端登录接口，凭返回 token 判定成功才置 authed；删除自动登录的 LaunchedEffect 后门；按钮启用条件加上密码非空。

### [android-base-03] NFC 点呼是纯前端模拟，无真实 NFC/nonce/ECDSA，且无法关闭
- **严重度**：critical | **类别**：security | **单元**：Android·基础层+接后端屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/nfc/NfcScreen.kt` : 45-62, 154
- **问题**：goScan() 点「シミュレート」按钮后 delay(1600) 就直接本地写一条 status="ok"、method="nfc" 的点呼记录，没有任何真实 NFC 读取、动态贴纸 nonce 校验、ECDSA 签名，也不发后端。RollCallSheet.kt:165-176 的「NFC をかざす」CTA 同样只本地把 rollState 改 DONE。MainActivity.kt:39-41 真正的 NFC ForegroundDispatch 还只是 TODO 注释。这与已知后端缺口「NFC 防作弊三件套后端完全没实装」对应——客户端侧同样三件套全无，整条防代刷链路两端都空。
- **影响**：点呼防代刷是项目核心卖点（spec 要求动态贴纸+ECDSA+老师监督），现状是按个按钮就算「点呼完了」，学生在任何地方都能伪造出席记录，防作弊价值为零。「シミュレート」按钮在生产构建里仍可见。
- **建议**：实装真实 NFC 读取（onResume 注册 ForegroundDispatch），读贴纸 nonce + 卡 UID，连同 ECDSA 走后端校验；生产构建移除「シミュレート」模拟按钮。当前阶段至少在 spec/TODO 标明这是 demo 桩。

### [androidrest-01] 注册流程完全没有注册码校验，任何人可自建账号并自选房号/宿舍/区分
- **严重度**：critical | **类别**：security | **单元**：Android·其余屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/account/AccountScreen.kt` : 78-118
- **问题**：AccountScreen 是 4 步注册表单（基本情報→点呼区分→連絡先→パスワード），全程没有任何「注册码」（管理员发给学生的一次性激活码）输入框或校验。全项目搜 register_code / 登録コード / invite 等关键词在 Android 代码里 0 命中。学生自己填 性別(决定男寮/女寮) / roomDigit(房号) / cat(一般寮生 vs サッカー部，决定点呼时刻) / isOverseas(决定审批链)，全部无人验证。
- **影响**：spec 明确要求「学生用管理员发的注册码注册」作为身份准入的第一道闸。这里完全缺失，等于任何人都能凭空注册并把自己挂到任意房间/宿舍/点呼区分下，直接破坏了点呼系统的身份边界，是防作弊设计的根本性绕过。
- **建议**：在 Step 1 之前或之中加一个「注册码」输入步骤，注册时把注册码连同表单一起发给 backend 校验，由 backend 根据注册码反查并锁定该学生的宿舍/房号/区分，而不是让学生自填这些边界字段。

### [androidrest-02] 注册收集的密码 pw/pw2 从未保存也未发送，账号创建纯本地假动作
- **严重度**：critical | **类别**：bug | **单元**：Android·其余屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/account/AccountScreen.kt` : 95-118
- **问题**：Step4 收集了 data.pw / data.pw2 并做了一致性校验，但 onNext 完成注册时只 store.update 写了 User(name/email/dorm/room/...) 这些资料字段。User 模型(Models.kt:9-21)里根本没有密码字段，pw 既没存进本地也没发任何网络请求(manifest 连 INTERNET 权限都没有)。所谓「アカウント作成完了」之后直接跳 Welcome→Login，登录其实也是 demo。
- **影响**：整个注册是个假流程：用户以为自己设了密码创建了账号，实际什么都没发生。真接 backend 时这套 UI 完全要重写（密码需要传给后端做哈希），现在的实现给人「已经做完注册了」的错觉，且与后端已知缺口（学生登录无失败锁定）叠加，掩盖了认证链根本没打通的事实。
- **建议**：明确标注此屏为 demo-only；真实装时注册要把 注册码+密码+资料 一起 POST 给 backend，由后端创建账号并返回 token，客户端不应自行 store.update 伪造一个已登录用户。

### [backend-biz-01] ✅已复核 扣分排名接口调用未导入的 dorm_units_for_teacher，必然抛 NameError 崩溃
- **严重度**：critical | **类别**：bug | **单元**：后端·公告/食堂/扣分/清扫/前台/通知
- **位置**：`03_dev/backend/v1/app/routers/discipline.py` : 29, 74
- **问题**：discipline.py 第 74 行 `dorm_units = dorm_units_for_teacher(teacher)` 调用了 R4 寮过滤函数，但文件顶部第 29 行 `from ..deps import get_current_teacher` 只导入了 get_current_teacher，没有导入 dorm_units_for_teacher（对比 cleaning.py 第 26 行是 `from ..deps import dorm_units_for_teacher, get_current_teacher`，正确导入了两个）。Python 运行到第 74 行时找不到这个名字，会抛 NameError。
- **影响**：GET /api/v1/discipline/ranking 这个核心扣分排名接口任何一次调用都会 500 崩溃，老师端 DisciplinePage（扣分页面）完全打不开。这是整个扣分模块的入口，等于扣分排名功能上线即不可用。

### [rollcall-01] NFC 防代刷核心（card_uid↔学生绑定 + nonce + ECDSA 签名）后端完全未实装，路径 A 靠 client 自报 student_id
- **严重度**：critical | **类别**：security | **单元**：后端·点呼与防作弊
- **位置**：`03_dev/backend/v1/app/routers/rollcall.py` : 263-288
- **问题**：spec 把动态 NFC 贴纸（ST25DV16K 每 10 秒刷新 nonce）+ ECDSA 数字签名定为防代刷的核心机制。但在 create_checkin 里，所谓「路径 A：NFC カード UID で学生特定」的分支实际是：if not body.student_id 就报错，然后 student = db.get(models.Student, body.student_id) —— 即真正用来定位学生的是 client 传来的 student_id，card_uid 仅被原样存进 event，没有任何校验。我已核实 models.py 的 Student 表根本没有 card_uid 字段（grep 全文只有 RollCallEvent.card_uid），所以 card_uid 无法反查学生；schemas.RollCallCheckinIn 里没有 nonce / signature 字段（注释明写「v1.1 起追加 nonce + signature」）；security.py 全文只有 JWT+bcrypt，无任何 ECDSA / nonce 校验代码。
- **影响**：防代刷机制在后端零实现。攻击者（或任意持老师 token 的人，甚至同学借到老师设备）可对 /checkins 直接 POST {"student_id": "<任意学生 UUID>", "card_uid": "任意字符串", "path_hint": "A"}，后端不验证这张卡是否真属于该学生、不验证 nonce 是否在 10 秒窗口内、不验证 ECDSA 签名，就把该学生记为 present。代刷（一人帮全宿舍点呼）完全无法阻止——这正是整个系统要解决的头号问题。

### [sysfeat-01] flow_design 把 nonce+ECDSA+设备注册整套防代刷标成定稿，后端零实装
- **严重度**：critical | **类别**：consistency | **单元**：设计文档 vs 代码
- **位置**：`02_design/flow_design.md` : 63-165 (§3 整章)
- **问题**：flow_design §3.1 把路径 B 的核心防御画成端到端 ✅：步骤 9『校验 nonce 是 10 秒内发给 DEV001 的吗 ✅』、步骤 10『用学生注册时存的公钥验 signature ✅』、步骤 12『查绑定：王小明绑了 DEV001 吗 ✅』，§0 状态表把 §3 标『✅ 定稿』。但 grep 后端 app/：没有任何 nonce 端点（flow_design 写的 POST /api/v1/nonce 不存在）、没有 public_key/pubkey 列（models.py / schemas.py 全无）、没有签名校验代码。schemas.py:627 自己注明『B = iPhone tap（v1.1 起追加 nonce + signature）』——即整套签名/nonce 是 v1.1 才做。
- **影响**：这是 spec 宣称的核心防代刷设计（动态贴纸 10 秒 nonce + 签名），文档却标『定稿』给人已落地的错觉。若按此文档判断 v1.0 上线就绪，实际上线时学生手机碰贴纸这条路完全没有任何防伪——复制 URL 即可永久代签，与文档 §3.4『防御生效率近似 100%』的结论相反。
- **建议**：把 flow_design §0 状态表 §3 从『✅ 定稿』改为『⏳ 设计定稿 / 后端未实装（v1.1）』，并在 §3 顶部加 banner 注明 nonce/signature/device 绑定后端均未实装；同步在 system_features §7.4 NFC 签到行明确标 v1.0 实际只走『老师手动 + card_uid（也未实装卡查找）』，路径 B 防伪推迟。

### [ios-auth-01] 房间号双前缀 bug 只修了 SEED 路径，真正送后端的 draft 路径仍坏 → 生产注册必失败
- **严重度**：critical | **类别**：bug | **单元**：iOS·登录注册
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Auth/AuthStubs.swift` : 1021, 1034
- **问题**：5-28 commit 6d945df「修房间号双前缀」只改了 SEED.user.room（第 1021 行：room.first?.isLetter==true 时不补 M/W 前缀），但同一函数第 1034 行 app.registrationDraft.room_no_suffix = room 仍把原始 room（含字母，如 demo 默认 "A5"）直接塞进 draft。AppStore.swift computedRoomNo（第 36-40 行）无条件 prefix = (gender==male)?"M":"W"; return prefix + room_no_suffix，于是 "A5" → "MA5"。后端 accounts.py _validate_room_dorm_match 取 room_no[:1] 期望 "M"/"W"，"MA5" 前缀是 M 看似过关，但 dorm_unit 由 computedDormUnit 从 suffix 第一位推（"A" 不是 "2" → 1 寮），实际房号语义全错；若学生输入纯数字如 "205" 反而正确。真正送后端的字段（draft）和被修复的字段（SEED）是两条独立路径，修复没覆盖提交路径。
- **影响**：非 demo 学生注册时，房号被错误拼接或语义错乱，要么被后端 422 打回卡在 Step5，要么写入错误寮区/房号数据。这是真实上线会 100% 触发的 bug。
- **建议**：把 room_no_suffix 的赋值统一走 computedRoomNo 同款逻辑：若 room 首位已是字母则不再补前缀；或更彻底地让 UI 只收数字 suffix（禁止学生输字母），让前缀完全由 gender 派生。两条路径（SEED + draft）必须用同一个拼接函数，消除分叉。

### [ios-home-01] 点呼弹窗 NFC 按钮是演示后门：按一下必成功，不读真 NFC、不校验防代刷
- **严重度**：critical | **类别**：security | **单元**：iOS·首页+点呼弹窗
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` : 1430-1446
- **问题**：RollcallSheet 的 simulate() 是「NFC をかざす」按钮（第 1250 行触发）的唯一处理逻辑。它只 sleep 0.5 秒就无条件 app.recordCheckin() 跳到 success 态，期间没有任何真实 NFC 读取、没有校验动态贴纸 nonce、没有卡 UID 绑定、没有 ECDSA 签名验证。fail（失败）态虽然写了完整 UI（failView, 1378 行），但 simulate() 里根本没有走向 fail 的分支——它永远成功。函数名直接就叫 simulate（模拟）。
- **影响**：这是整个系统核心防代刷设计的正面突破口。spec 要求点呼靠手机碰点呼机 + 10 秒刷新 nonce + ECDSA 签名 + 卡 UID 绑定防代刷，但客户端这一侧任何人只要打开 App 点一下按钮就能在本地判定为「時間内チェックイン（按时签到）」，完全不需要人在点呼机旁边、不需要 NFC、不需要本人。配合后端三件套也完全没实装（已知背景），代刷防御链路上下两端全空。这是会上线的真系统，等于点呼形同虚设。
- **建议**：v1.0 前必须用真 CoreNFC 读取 + 把读到的 nonce/卡 UID/签名发后端校验替换掉 simulate()，成功/失败由后端响应决定（失败走已有的 failView）。当前阶段至少在代码里明确标注这是 demo-only 桩、列入上线前必删/必换清单（参照 memory project_demo_scaffolds_to_remove_before_v1.md），并把它和后端三件套缺口在同一条 TODO 里对齐。

### [iosmypage-01] 删账号按钮调用的后端接口不存在，点击必然失败
- **严重度**：critical | **类别**：bug | **单元**：iOS·个人页
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` : 1632
- **问题**：删账号流程 performDelete() 调 AccountsAPI.deleteMyAccount()，该方法在 AuthAPI.swift:53 发 DELETE /api/v1/accounts/me。但后端 03_dev/backend/v1/app/routers/ 里全文搜 @router.delete 只有 teachers.py（删老师）/ announcements.py（删公告、删回复）三处，没有任何 accounts 的 DELETE 路由。学生点「アカウントを削除」→ 后端返 404/405 → 永远走到 catch 弹「削除に失敗しました」。
- **影响**：App Store 5.1.1(v) 强制要求的账号删除功能完全不可用。审核时苹果会实测这个按钮，删不掉号 = 直接拒审，iOS 上不了架。
- **建议**：后端补 DELETE /api/v1/accounts/me 路由（鉴权取当前学生 → 软删或硬删 student + 级联 token 失效）。在补完前，这个按钮要么藏起来（#if DEMO），要么明确标记为已知缺口写进 TODO。

### [teacherweb-01] 学生账户管理页整页是写死假数据，零后端对接
- **严重度**：critical | **类别**：bug | **单元**：老师网页
- **位置**：`03_dev/teacher_web/v1/src/index.html` : 23007-23051
- **问题**：AccountsPage（学生アカウント管理 = 学生账户管理页）的数据来源是 `React.useState(window.ACCOUNTS)`，而 window.ACCOUNTS 是第 10112 行写死的 7 个假学生（リュウ イヒ、电话 090-0000-0000、邮箱 @tomoshibi.local 等 demo seed）。页面上的「保存修改」handleSave（23038）、「重置密码」handlePasswordReset（23048，用 Math.random 生成临时密码）、锁定/解锁，全都只 setAccounts 改本地 state，没有任何一处调 window.tomoshibiApi 把改动发给后端。client.js 里也根本没有学生账户 CRUD 的接口。
- **影响**：生产上线后，老师在这个页面做的所有学生账户操作（改资料、重置密码、锁定账户）都是假的——刷新页面就全没了，后端数据库纹丝不动。老师会误以为已经锁定了某个违规学生或重置了密码，实际完全没生效，属于功能性彻底失效，且会误导真实管理决策。
- **建议**：上线前要么给 AccountsPage 接真实的后端学生账户接口（client.js 需新增对应端点），要么明确把整页标成「未实装 / demo 专用」并在生产模式（无 ?demo）下禁止进入，不能让它伪装成可用功能。

---

## 🟠 高危（33 条）

### [android-base-04] 整个 app 无网络层，全部数据是 MockData 假数据
- **严重度**：high | **类别**：architecture | **单元**：Android·基础层+接后端屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/store/AppStore.kt` : 31-67
- **问题**：全树 grep 不到任何 HTTP 客户端（retrofit/okhttp/ktor/URLConnection）。AppStore 只把 AppState 整体 JSON 存进本地 DataStore（tomoshibi-app-state-v1），首次或解析失败一律回落 MockData.INITIAL_STATE。MockData.kt:6 自己注释「v1.0 demo 用，P6 接 backend 时换成真实 Repository」。Home/申请/通知/减点/点呼履历等所有屏读的都是本地 state + MockData 常量（如 HomeScreen.kt:87 DEFAULT_BUS、:97 DEFAULT_DELIVERY 直接读静态常量）。
- **影响**：「v1.0 一次上线」目标下，Android 端实际离能用差一整个数据层：申请提交、点呼上报、减点/通知拉取都没连后端，多设备/换机数据不同步，老师那边也看不到学生真实操作。
- **建议**：补 Repository + 网络层（统一 base URL 配置、登录 token、各业务接口），把 MockData 降级为仅离线占位；明确标注当前为原型阶段避免被当成已上线功能。

### [android-base-05] MockData/FormData 硬编码真实姓名邮箱电话
- **严重度**：high | **类别**：security | **单元**：Android·基础层+接后端屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/data/seed/MockData.kt` : 10-21
- **问题**：DEFAULT_USER 把真实邮箱 otogi2025@gmail.com、电话 090-9482-8905、姓名 リュウイヒ、房间 M101、学号 060218 写死进种子数据。AccountScreen.kt:44-58 的 FormData 默认值同样预填同一套真实邮箱和电话。仓库已 public（otogi2025/DMSD）。
- **影响**：本人真实邮箱和手机号随源码公开在 GitHub，属于个人信息泄露；将来真上线时这些 demo 默认值若没清掉，新用户注册界面会预填别人的私人信息。
- **建议**：种子/默认值改用明显的占位数据（如 example@example.com、000-0000-0000、テスト太郎），真实个人信息不入库。

### [androidrest-03] FeedbackScreen 用字符串拼接构造 JSON，存在注入与转义破坏风险
- **严重度**：high | **类别**：security | **单元**：Android·其余屏
- **位置**：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/community/FeedbackScreen.kt` : 167
- **问题**：提交反馈时手写拼 JSON："""{"category":"${category}","mood":"${mood}","text":"${text.replace("\"", "'")}"}"""。只把双引号替换成单引号，没处理反斜杠 \ / 换行 / 控制字符，用户输入含 \ 或换行就会生成非法 JSON；将来这串直接发给 backend 时是典型的注入面。
- **影响**：现在存本地 List<String> 还只是脏数据，一旦 P6 接 backend（注释 line 33 写明计划这么做）原样把这串当 JSON 发出，轻则后端解析失败丢数据，重则被构造特殊输入注入额外字段。
- **建议**：改用 kotlinx.serialization 把一个 data class 序列化成 JSON，不要手拼字符串。

### [applchain-01] 审批接口 decide_approval 缺寮(宿舍)边界校验 — 跨寮越权审批
- **严重度**：high | **类别**：security | **单元**：后端·申请与审批链
- **位置**：`03_dev/backend/v1/app/routers/applications.py` : 457-529
- **问题**：POST /applications/{id}/approvals 只用 get_current_teacher 拿到老师，然后凭 teacher.role 匹配 pending 的审批行就允许 approve/reject，完全没有调用 _teacher_can_view 或 dorm_units_for_teacher 做寮过滤。对比同文件 GET /{id}（行 263-268 用 _teacher_can_view 校验担当寮）和 list_pending_for_me（行 214-225 对非跨寮役职加 dorm_unit 过滤），唯独真正产生写操作的审批接口没有这层校验。
- **影响**：举例：男寮(dorm_unit 1/2)的某个『寮務課長』之外的、被分配到女寮(assigned_dorm=4)的同役职老师，只要该役职出现在审批链里，就能审批男寮学生的外泊/帰省申请。虽然『寮務課長/寮務部長』等本就是跨寮役职，但担任(homeroom)这一环也可能被任意担任老师抢审（见 applchain-03），且 R4 寮隔离在写路径上完全失效。这是真实越权(IDOR 类)漏洞。

### [applchain-02] 担任(homeroom)审批环没校验是不是该学生的真正担任 — 任意担任老师可冒充审批
- **严重度**：high | **类别**：security | **单元**：后端·申请与审批链
- **位置**：`03_dev/backend/v1/app/routers/applications.py` : 476-512
- **问题**：审批链里『担任』这一环是 per-学生的（approval_chain.resolve_homeroom_teacher 按学生班级从 class_teacher_assignment 表解析出唯一担任）。但 decide_approval 判断谁能审『担任』环只看 teacher.role == '担任'，不校验这个老师是不是这个学生班级的担任。任何 role 为『担任』的老师（全校所有班主任）都能审批任意学生的『担任』审批行。
- **影响**：A 班担任可以替 B 班学生的申请盖『担任』章。担任本应是申请审批链里最贴近学生、最该专属的一环，现在变成全校班主任通用，破坏了审批链的责任归属与防代审设计。

### [auth-account-01] ✅已复核 teachers.py 缺 IntegrityError 与 func 两个 import，创建/删除老师必崩
- **严重度**：high | **类别**：bug | **单元**：后端·鉴权与账号
- **位置**：`03_dev/backend/v1/app/routers/teachers.py` : 244, 284
- **问题**：create_teacher 在第 244 行用 `except IntegrityError:` 捕获并发冲突，delete_teacher 在第 284 行用 `func.count(...)` 统计剩余管理员；但文件顶部 import 区（9-21 行）只 import 了 `from sqlalchemy import select`，既没有 `from sqlalchemy.exc import IntegrityError`，也没有 `from sqlalchemy import func`。这两个名字在运行时都未定义。
- **影响**：创建新教师时一旦走到并发冲突分支会抛 NameError（500 而不是友好 409）；删除任何「寮务管理」角色教师时，只要走到 LAST_ADMIN 拦截分支就一定 NameError 崩溃（500），删除管理员功能直接不可用。这是上线即触发的运行时 bug。

### [auth-account-03] ✅已复核 学生登录无失败计数与账号锁定，6 位密码可被无限暴力破解
- **严重度**：high | **类别**：security | **单元**：后端·鉴权与账号
- **位置**：`03_dev/backend/v1/app/routers/auth.py` : 31-80
- **问题**：login_student 在密码错误时直接 raise 401（第 50-56 行），从不递增任何失败计数，也从不设置锁定；只有在登录成功后才把 `account.failed_count = 0 / account.lock_level = 0`（第 74-75 行）。而 Account 模型明明有 `failed_count` / `locked_until` / `lock_level` 三个字段（models.py 197-199 行）专门为锁定准备。对比 login_teacher（83-154 行）实现了完整的失败计数+30 分钟锁定，学生端的锁定逻辑完全没接。学生密码 schema 只要求 min_length=6（schemas.py 第 50 行），很多学生会用纯 6 位数字。
- **影响**：攻击者拿到任意学号（学号是 grade+class+seat 6 位，极易枚举——见 auth-account-05），可对该学生账号无限次试密码。配合弱密码（6 位数字仅百万组合）几小时内可爆破。点呼系统里学生账号能提交外泊申请、看公告等，被盗号影响真实业务。

### [auth-account-04] 学生注册码非一次性，5 分钟窗口内可被任意多人重复注册
- **严重度**：high | **类别**：security | **单元**：后端·鉴权与账号
- **位置**：`03_dev/backend/v1/app/routers/accounts.py` : 48-75, 162-173
- **问题**：_validate_registration_code 只校验码存在、未作废、未过期（54-62 行），校验通过后 create_account 不把该码标记为已使用（invalidated_at 始终不被设置），只写了一条 audit log（162-172 行）。StudentRegistrationCode 模型也没有 used_count / max_uses / single_use 类字段（models.py 882-907 行只有 invalidated_at / is_reviewer）。spec 字典里 registration_code 的核心规则之一应是单次有效，代码却让它在 5 分钟 TTL 内可被无限次复用。
- **影响**：老师在现场报一次注册码给一个学生，这个 6 位码在 5 分钟内被旁边的人看到/截图后，任何人都能用它注册任意数量的账号（只要学号不撞）。配合 6 位纯数字码可枚举（auth-account-05），等于注册闸门基本失效，可批量灌假账号。

### [auth-account-06] ✅已复核 缺 DELETE /accounts/me，违反 Apple 5.1.1(v) 账号删除强制要求
- **严重度**：high | **类别**：consistency | **单元**：后端·鉴权与账号
- **位置**：`03_dev/backend/v1/app/routers/accounts.py` : 24-193
- **问题**：accounts.py 只实现了 POST /accounts（新规注册），全后端 grep DELETE 端点只在 teachers.py 和 announcements.py 命中，没有任何让学生删除自己账号的端点。Apple App Store 审核指南 5.1.1(v) 明确要求：允许用户在 App 内创建账号的应用，必须提供应用内删除账号的能力。本项目 v1.0 要上 iOS。
- **影响**：iOS 上架审核大概率被拒（5.1.1(v) 是硬性条款，且这个 App 本身就强制注册）。同时学生没有任何途径自助注销账号，属合规缺口。

### [models-entry-01] StudentAccountCreateIn 允许 dorm_unit=3，但 DB CHECK 只接受 1/2/4，会在落库时抛 500
- **严重度**：high | **类别**：bug | **单元**：后端·数据模型与入口
- **位置**：`03_dev/backend/v1/app/schemas.py` : 798
- **问题**：学生新规注册输入 schema `StudentAccountCreateIn` 对 dorm_unit 的校验是 `dorm_unit: int = Field(..., ge=1, le=4)`，意思是「1 到 4 之间的整数都通过」，所以 3 也能通过 Pydantic 校验。但 models.py 里 Student 表的 CHECK 约束 `ck_students_dorm_unit` 只允许 `dorm_unit IN (1, 2, 4)`（models.py:88）。dorm_unit（宿舍栋号）实际只有 1/2 男寮、4 女寮，没有 3。accounts.py 的 `_validate_room_dorm_match` 只校验房号前缀和 gender，对 dorm_unit=3 不拦（它的 expected_prefix 逻辑是 `dorm_unit in (1,2)` 否则一律当 W/female，dorm_unit=3 会被归到 female 分支但不会因 dorm_unit 本身报错）。
- **影响**：客户端若传 dorm_unit=3（手滑或恶意构造），会绕过输入层校验，到 INSERT 时被 DB CHECK 拒绝，抛出未捕获的 IntegrityError → 返回 500 而不是友好的 422/400。生产环境 PostgreSQL 同样会拒。属于输入校验与 DB 约束不一致。

### [migtest-01] 测试用 create_all 建表完全不跑 alembic 迁移，迁移脚本零验证
- **严重度**：high | **类别**：test | **单元**：后端·迁移与测试
- **位置**：`03_dev/backend/v1/tests/conftest.py` : 30-31
- **问题**：_engine fixture 用 Base.metadata.drop_all/create_all（第 30-31 行）直接从 models.py 当前定义建表，从不执行 alembic upgrade。意味着 10 个迁移脚本里的 batch_alter_table(recreate='always')、downgrade、op.execute、CHECK 约束变更等逻辑从未被任何测试跑过。
- **影响**：迁移本身的 bug（如 SQLite batch recreate 时丢列数据、downgrade 写错、迁移与 models 漂移）在 CI 里完全无法暴露。生产部署跑的是 alembic（与测试路径不同），等于上线路径无测试覆盖。
- **建议**：增加一个集成测试：建空 SQLite，跑 alembic upgrade head，再 alembic downgrade base，断言不报错；并对比迁移建出的 schema 与 metadata.create_all 的 schema 是否一致。

### [migtest-02] DATABASE_URL 用 setdefault + .env 生效，测试可能跑在真实库上并被清空
- **严重度**：high | **类别**：bug | **单元**：后端·迁移与测试
- **位置**：`03_dev/backend/v1/tests/conftest.py` : 7
- **问题**：conftest 第 7 行 os.environ.setdefault('DATABASE_URL', 'sqlite:///./test_tomoshibi.db')，setdefault 只在变量未设时生效。config.py 第 30 行 Settings 又配了 env_file='.env'。若开发机已 export DATABASE_URL 或 .env 指向 tomoshibi_dev.db，测试会连真实库，而 _truncate_tables fixture（第 41-46 行）每个用例前 delete 所有表的全部行。
- **影响**：在某些环境下跑 pytest 会清空开发/生产数据库的全部数据，属于数据破坏风险。
- **建议**：改用 os.environ['DATABASE_URL']=... 强制覆盖（不用 setdefault），或显式在 get_settings 里对 APP_ENV=test 锁定到独立测试库，并在 fixture 里加断言确认连的是 test 库才允许 truncate。

### [migtest-04] 审批链 approve/reject 与学生修改届核心写路径声称覆盖但实际没测
- **严重度**：high | **类别**：test | **单元**：后端·迁移与测试
- **位置**：`03_dev/backend/v1/tests/test_applications.py` : 8-9
- **问题**：文件 docstring（第 8-9 行）声称覆盖 POST /applications/:id/approvals（教师承认/拒绝）和 PUT /applications/:id（学生修改届 chain 重置），但整个文件里没有任何针对这两个端点的测试，只有创建/查询/列表/audit。审批是整个出寮流程最核心的状态机动作。
- **影响**：承认链推进、partial→approved 跃迁、拒绝、修改后 chain 重置这些最关键且最易出 bug 的写逻辑零测试保护，回归风险高。
- **建议**：补审批链测试：教师按顺序 approve 推进 chain_order、非当前环节教师 approve 被拒、reject 后状态、学生 PUT 修改后 approvals 是否正确重置。

### [backend-biz-02] 清扫查看/创建/审核全程缺 R4 寮边界校验，男寮老师可操作女寮学生
- **严重度**：high | **类别**：security | **单元**：后端·公告/食堂/扣分/清扫/前台/通知
- **位置**：`03_dev/backend/v1/app/routers/cleaning.py` : 63-94, 97-159
- **问题**：create_cleaning（第 63 行）和 inspect_cleaning（第 97 行）只校验了 teacher.role 在 _ADMIN_ROLES 里，没有校验目标学生是否属于该老师管辖的寮（dorm_units_for_teacher）。list_cleaning（第 37 行）做了 R4 过滤，但创建和审核两个写操作完全没做。一个 assigned_dorm=1（男寮）的寮監，能给 dorm_unit=4（女寮）的学生分配清扫、审核清扫不通过并自动加扣分。
- **影响**：破坏 spec R4 寮隔离边界。男寮管理员可越权给女寮学生加扣分（清扫不通过自动 +2.5 分，见第 144-153 行），可能影响该学生是否触发 4 分清扫阈值/8 分禁足阈值，属于跨边界数据操纵。

### [backend-biz-03] 前台条目查看/登记/操作全程缺 R4 寮边界校验
- **严重度**：high | **类别**：security | **单元**：后端·公告/食堂/扣分/清扫/前台/通知
- **位置**：`03_dev/backend/v1/app/routers/front_desk.py` : 40-58, 61-101, 104-137, 140-173
- **问题**：front_desk.py 四个端点（list_items / create_item / notify_item / mark_picked_up）都只检查 role 不检查寮边界。list_items（第 40 行）列全部条目不按老师所辖寮过滤；create_item 可给任意寮学生登记宅配；notify/picked-up 可对任意条目操作。整个文件没有 import 也没有调用 dorm_units_for_teacher。
- **影响**：宅配 / 失物条目里含学生 student_id 与个人信息（description / location），男寮老师能看到并操作女寮学生的宅配/失物条目，违反 R4 寮隔离。虽然敏感度低于扣分，但仍是越权信息访问。

### [rollcall-02] WebSocket broadcast 把全校学生姓名+房号推给每个连接老师，无视寮（dorm）隔离边界
- **严重度**：high | **类别**：security | **单元**：后端·点呼与防作弊
- **位置**：`03_dev/backend/v1/app/ws_manager.py` : 71-84
- **问题**：ws_manager.broadcast 对 self._conns 里所有连接无条件 send_json(event)，而 rollcall.py 的 create_checkin（349-359）/ patch_event（616-625）广播的 event 里带 student_id、name、room_no、status。_TeacherConn 虽然存了 assigned_dorm（line 34），但 broadcast 完全没用它过滤。代码注释自己也承认「当前广播全部」（ws_manager.py line 13）。对比 board / today_sessions / study 等 HTTP endpoint 都老老实实按 assigned_dorm 做了寮过滤，唯独实时推送这条没做。
- **影响**：横向越权数据泄漏：男寮老师（assigned_dorm=1）会实时收到女寮（dorm_unit=4）学生的姓名、房号、出席状态推送，反之亦然；不该跨寮的老师拿到了别寮全部学生的隐私与点呼动态。违反 spec 的班级/宿舍隔离边界设计。

### [rollcall-03] checkin / patch_event 缺少「目标学生是否属于本老师管辖寮」的越权校验
- **严重度**：high | **类别**：security | **单元**：后端·点呼与防作弊
- **位置**：`03_dev/backend/v1/app/routers/rollcall.py` : 226-288, 561-610
- **问题**：create_checkin 只校验 session 存在且 running、student 存在，没有校验该 student 的 dorm_unit 是否在该老师 assigned_dorm 允许范围内，也没校验 session 的 dorm_unit_set 是否在老师可见范围。patch_event（改判）同理：任何 get_current_teacher 通过的老师都能对任意 event_id 改判、触发扣分增减，没有寮过滤、没有 require_teacher_roles 角色限制。board/summary/list 都做了寮过滤，唯独写操作（checkin/override）没做。
- **影响**：纵向/横向越权：男寮老师可给女寮学生写出席记录或改判其点呼状态（连带自动扣分/撤销扣分），影响别寮学生的纪律分。攻击面比只读更严重，因为是写操作且联动 DemeritEvent。

### [sysfeat-02] flow_design 描述学生 App 直接 POST 签到，但后端签到端点强制要老师登录
- **严重度**：high | **类别**：consistency | **单元**：设计文档 vs 代码
- **位置**：`02_design/flow_design.md` : 96-119
- **问题**：flow_design §3.1 步骤 7-8 写『App 用本机 Keychain 私钥做 ECDSA 签名 → POST /api/v1/checkin {student_id, signature...}』，即学生手机自己向后端提交签到。但实际后端 rollcall.py:230 的 create_checkin 依赖 `get_current_teacher`——必须老师 token 才能调，学生身份调不通。且真实路径是 POST /api/v1/rollcall/sessions/{id}/checkins，与文档写的 /api/v1/checkin 不同。
- **影响**：文档描绘的『学生 tap→App 自动 POST』签到模型与实装架构根本不同（实装是老师设备/点呼机持票调用）。按文档去对接客户端会得到 401，且学生端无法独立完成签到这一核心交互的真值缺失，影响 iOS/Android/点呼机三端对接判断。
- **建议**：在 flow_design §3.1 标注当前实装的签到端点是 /api/v1/rollcall/sessions/{id}/checkins 且需要点呼机/老师凭证调用；澄清 v1.0 的调用者是点呼机（Pi）而非学生 App 直接 POST，或确认未来要不要给学生端开放签到端点（涉及鉴权设计）。

### [sysfeat-03] flow_design §1.2 称 device_id 必须在 DEVICE_REGISTRY 注册，但后端无此表
- **严重度**：high | **类别**：consistency | **单元**：设计文档 vs 代码
- **位置**：`02_design/flow_design.md` : 43
- **问题**：flow_design §1.2 共同前提写『每个 device_id 必须在 DEVICE_REGISTRY 注册后才能签到』，§8.1 还定义了 UNKNOWN_DEVICE 错误码。但 models.py 没有任何 device/DEVICE_REGISTRY 表；device_id 仅作为 RollCallEvent 上一个 Optional[uuid] 列存在（models.py:802），无外键、无校验、签到流程从不读它。
- **影响**：『设备必须注册才能签到』这条前提在后端完全不成立，UNKNOWN_DEVICE 永远不会触发。任何未注册点呼机/伪造 device_id 都能签到（只要满足其它条件），与文档安全前提相悖。
- **建议**：要么后端补 device 注册表 + 签到时校验 device_id，要么把 flow_design §1.2 这条前提与 §8.1 UNKNOWN_DEVICE 标为『⏳ 未实装』，避免审查者误以为已有设备白名单防御。

### [ios-auth-02] 客户端做登录失败锁定升级，但后端已知无失败锁定 → 锁定纯前端形同虚设
- **严重度**：high | **类别**：security | **单元**：iOS·登录注册
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Auth/AuthStubs.swift` : 1739-1742, 1773-1887
- **问题**：tryLogin 捕获 APIError.unauthorized 后调 app.recordLoginFailure() + 跳 LockoutView，AppStore 维护 loginFailCount → 30s/1分/5分/.../永久 的本地倒计时。但已知后端没有登录失败锁定。锁定状态只存在 iOS 内存（loginFailCount 是 @Published Int，没持久化），杀进程重启即清零；攻击者直接打后端 /api/v1/sessions/student 接口绕过 App 即可无限暴力破解。LockoutView 的 30s 倒计时结束只是 router.replace(.login)，不阻止任何真实请求。
- **影响**：登录限速/锁定是安全装饰，无实际防爆破能力。学号是 6 桁数字（10^6 空间）+ 无后端限速 = 可被脚本短时间撞库。AC 叙事里把这当防作弊亮点会被面试官一问就破。
- **建议**：锁定必须由后端实装（按学号/IP 计失败次数 + 返回 429/锁定标志），iOS 只展示后端下发的锁定状态。当前前端逻辑可保留做 UX 提示，但要在 spec/文档明确标注「真实限速在后端，前端仅展示」，并把后端限速列入 TODO。

### [ios-community-01] 全部 18 屏是静态 SEED 假数据，所有提交动作只弹 toast 不写后端，却被当真功能呈现
- **严重度**：high | **类别**：architecture | **单元**：iOS·社区
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Community/CommunityStubs.swift` : 342-345, 545-551, 617-619, 816-821, 1081-1087, 1772-1778
- **问题**：每个『写』动作都是同一套路：app.showToast("...しました") 然后跳页，没有任何网络请求。例：宅配受取確認(342-345)只弹『受取完了しました』；遗失物投稿(545-551)、点歌投稿(816-821)、寮墙投稿(1081-1087)、遗失物认领『私のものです』(617-619)、匿名建议送信(1772-1778)全部如此。数据源全是 Foundation/Seed/SEED.swift 里写死的静态数组（SEED.packages/lost/songs/wall/suggestions/events）。
- **影响**：公告/遗失物/班车/匿名建议/点歌通报 按 spec 是 v1.0 真上线的用户功能（不是一次性 demo），但现在用户点『投稿』『送信』后屏幕显示成功、数据却根本没存。上线时若忘了接后端，会变成『用户以为提交成功实际丢失』的严重数据问题，且无任何报错提示。
- **建议**：建立『demo 占位 vs 生产功能』清单（已有 memory feedback_ios_early_code / demo_scaffolds_to_remove），逐屏标注哪些 v1.0 必须接后端写接口。每个 showToast 成功提示处加 TODO 注释指向对应后端 API；接后端前这些成功 toast 应改成『后端未接入』占位或禁用按钮。

### [ios-community-02] 匿名建议屏承诺『名字·番号不会被发送』但实际啥都没发送，承诺未经验证
- **严重度**：high | **类别**：security | **单元**：iOS·社区
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Community/CommunityStubs.swift` : 1733, 1772-1778
- **问题**：SuggestView 顶部隐私横幅写死『🔒 投稿は完全匿名です。あなたの名前・番号は送信されません。』(1733)，但送信动作(1772)只是 showToast『送信しました（匿名）』后跳回首页，没有任何真实发送。当未来接后端时，必须保证请求体确实不含学生身份字段——而后端单元已知缺寮越权校验/鉴权缺口，匿名建议如果带着登录 token 发出，后端拿 token 就能反查是谁，『完全匿名』就是假的。
- **影响**：对一个真上线、还专门强调『完全匿名』的功能，一旦接后端时无意中带上身份信息（token / 学号），会直接违背对学生的隐私承诺，可能让学生因吐槽运营被反向定位，属于信任与合规风险。
- **建议**：接后端时为匿名建议设计专门的不带身份的提交通道（或后端明确丢弃身份字段并文档化），并在客户端代码注释里写明『此接口禁止携带 Authorization token』。上线前做一次抓包验证『请求里真的没有学号/姓名/token』再放出这条文案。

### [ios-home-02] 签到成功本地直接造数据：recordCheckin / recordStudyTap 无后端确认即改状态
- **严重度**：high | **类别**：bug | **单元**：iOS·首页+点呼弹窗
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` : 1435, 1771
- **问题**：RollcallSheet.simulate() 调 app.recordCheckin()，StudyCheckinSheet.simulate() 调 app.recordStudyTap()，两处都是本地状态变更，没有等待任何网络请求返回就直接把界面切到「完了（完成）」并弹 toast「チェックイン完了」。整个点呼/学習签到流程没有一次真正打后端接口。成功态展示的时间还用 app.checkinAt ?? "21:02"、kind 用 app.checkinKind ?? "時間内" 这种写死兜底值（1360、1440 行）。
- **影响**：用户会看到「按时签到成功」的绿色完成界面，但服务器上根本没有这条点呼记录（后端也没实装签到接口）。本地状态与服务器真相完全脱节，老师端看不到该学生签到，学生却以为自己签到了——上线后会直接造成「我明明打卡了为什么算我缺席」的纠纷和扣分申诉。
- **建议**：签到成功/失败必须由后端响应驱动：simulate() 改成「调签到 API → 成功才 record + success，失败走 failView」。在后端接口就绪前，这些本地 record 调用应标注为 demo 桩并列入上线前必换清单。

### [ios-home-03] 首页扣分卡演示三态切换 + 学習演示态，已标 v1.0 删但仍在线
- **严重度**：high | **类别**：test | **单元**：iOS·首页+点呼弹窗
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` : 252-269, 293-481
- **问题**：pointsCard 里第 253 行注释「⚠️ DEMO-ONLY 三态切换 (system_features §7.3.8 — v1.0 删)」，第 293 行注释「study content（…⚠️ DEMO-ONLY · v1.0 删）」。这两段（idle/active/study 三态切换 + 整个 studyContent / studyTapsProgress / studyActionButtons 学習演示块）目前都正常编译进 App、对真实用户可见。它们靠的是 app.rollState / app.studyState 这种本地演示状态，不是后端事件驱动。
- **影响**：上线 v1.0 时若忘删，这些演示态会和真实点呼逻辑混在一起：本地 studyState 可被本地切换显示「学習中」hero、学習 3 回 tap 进度全靠本地 recordStudyTap 推进，全是假状态。属于 memory 里明确要求 v1.0 前必删的 demo scaffold（否则变安全漏洞）。
- **建议**：上线前按 system_features §7.3.8 把演示三态切换和 studyContent 整块改为后端事件驱动或删除；当前应在 00_admin/TODO.md 单独立条追踪，避免发版时遗漏。

### [ios-home-11] 学習 NFC 签到同样是演示桩：simulate 必成功，stepTimeWindow 受付时间形同虚设
- **严重度**：high | **类别**：security | **单元**：iOS·首页+点呼弹窗
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` : 1493-1500, 1766-1786
- **问题**：StudyCheckinSheet 的 simulate() 和 RollcallSheet 同样的问题：按「NFC をかざす」无条件成功、本地 recordStudyTap 推进 3 回 tap，没读真 NFC、不校验防代刷。stepTimeWindow（受付時間 19:35〜19:40 等）只是文字展示，代码里完全没有校验「当前是否在受付时间窗口内」，时间外照样能 tap 成功。
- **影响**：学習出席（晚自习 3 次打卡）和点呼一样可被任意伪造：不在学習室、不在受付时间，照样点按钮就显示 3 回完了。学習出席若也关联扣分/管理，这同样是代刷漏洞。属于 §7.3.3 学習签到的演示桩，未做任何防护。
- **建议**：与 ios-home-01 一并处理：改真 NFC + 后端校验（含时间窗口校验由后端判定），失败走 failView；接口就绪前标注 demo 桩并列入上线前必换清单。

### [iosmypage-02] 个人页写死的扣分规则与后端定义冲突（0.5/1.0 vs 1.0/2.0）
- **严重度**：high | **类别**：consistency | **单元**：iOS·个人页
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` : 1031, 879
- **问题**：减点明细页规则栏写「遅刻 0.5 点 / 欠席 1.0 点」（行 1031），点呼详情页也写「遅刻 0.5 点」（行 879）。但后端 models.py:1006 DemeritEvent 的默认分值是 late=1.0 / absent=2.0。两套口径差一倍。SEED.swift 顶部注释（行 3）也说「迟到 5 · 欠席 2」=4.5 分用的是 iOS 的 0.5/1.0 算法，若按后端 1.0/2.0 算同样次数应是 9 分。
- **影响**：上线接后端后，学生 App 上显示的总分、单条扣分值、清扫/禁足阈值触发时机会跟后端真实计算的全部对不上。点呼是这个系统核心，分数错位直接动摇可信度，也可能让学生误判自己是否会被禁足。
- **建议**：先确认哪套是定稿（spec §7.5 / itsuki 5-22 阈值），统一 backend + iOS + Android + teacher_web 四端的迟到/欠席分值。所有扣分规则文案不该 hardcode 在 UI，应由后端下发或集中常量。

### [iosmypage-03] 整个个人页是本地 SEED 假数据，没接后端
- **严重度**：high | **类别**：architecture | **单元**：iOS·个人页
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` : 65, 237, 262, 1015, 1141, 1334, 1388, 1448
- **问题**：点呼统计（行 237 monthRollcallStats 遍历 SEED.rollcall）、扣分总分（行 262 SEED.user.points）、扣分明细（行 1015 SEED.points）、12 月图表（行 1141 写死数组 [0,0,1,...,4.5]）、体调履历（行 1334 SEED.health）、扫除履历（行 1388 SEED.cleaning）、快递（行 1448 SEED.packages）全部读本地 hardcode 数据，没有任何网络请求。SEED.swift 数据是 demo 写死的「リュウ イヒ / A5 / 4.5 点」。
- **影响**：真上线后每个学生看到的都是同一份假数据（同一个名字、同样 4.5 分、同样点呼记录），不是自己的真实数据。这不是个人页，是静态演示页。离生产可用差一整层数据对接。
- **建议**：明确标注这些屏当前是 demo 桩，上线前每屏都要换成后端 GET 接口拉当前学生数据。建议在 TODO.md 按屏列出待接的接口清单（个人信息 / 点呼履历 / 扣分明细 / 体调 / 扫除 / 快递）。

### [iosmypage-04] 「保存する」按钮只改本地 SEED，没调后端，是假持久化
- **严重度**：high | **类别**：bug | **单元**：iOS·个人页
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` : 733
- **问题**：MyInfoEditView 的 saveAndLog()（行 733-747）改房间号/邮箱/电话后，直接写 SEED.user.room/email/phone（行 741-743）并弹「保存しました」toast，全程没有任何网络调用。SEED.user 是 nonisolated(unsafe) static var（SEED.swift:9），改的是全局内存变量。
- **影响**：学生改完信息看到「保存成功」，但数据只存在当前进程内存里，App 一重启就丢，后端永远不知道。学生以为改好了房间号，老师后台看到的还是旧的，点呼归属可能出错。属于会误导用户的假成功。
- **建议**：saveAndLog 必须调后端 PATCH/PUT 个人信息接口，成功后再更新本地 + 弹 toast，失败要走 APIErrorPresenter 报错。后端还需要校验房间号改动（结合已知的『寮越权校验缺失』，学生不该能随便把自己改到别的寮）。

### [iosmypage-05] 退出登录只跳登录页，没清 token，账号实际没登出
- **严重度**：high | **类别**：security | **单元**：iOS·个人页
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift` : 2071
- **问题**：LogoutSheet 的「ログアウト」按钮（行 2071-2074）只做 app.closeSheet() + router.replace(.login)，跳到登录页，但没有把 app.authToken = nil（对比删账号流程行 1634 是有清 token 的）。弹窗文案还写「次回起動時はアカウント番号とパスワードが必要です」（行 2063 声称下次要重新输密码）。
- **影响**：token 还在 Keychain 里、APIClient 还带着它，等于没真登出：别人拿到这台手机，回退或重进可能直接恢复登录态；下次启动也未必真要求重新输密码，与弹窗承诺不符。共用/丢失设备场景下是账号安全隐患。
- **建议**：登出按钮应跟删账号一样置 app.authToken = nil（触发 didSet 清 Keychain + APIClient），如有后端登出/吊销接口也应调用，再跳登录页。需对照 AppStore.authToken 的 didSet 确认是否已在别处统一处理。

### [ios-staylist-01] StayEditForm 修改届仍是纯 mock 无后端，提交只写本地内存假数据
- **严重度**：high | **类别**：bug | **单元**：iOS·外宿清单+废弃屏
- **位置**：`03_dev/student_ios/v1/TomoshibiApp/Features/StayList/StayListStubs.swift` : 1232-1244, 1445-1462
- **问题**：StayList 的「列表」和「详情」屏（StayListView/StayDetailView）都已在 A-037 切回真 API（ApplicationsAPI.listMine/detail/audit），但「修改届提交」屏 StayEditForm 的 load()（1234 行）和 submitAsync()（1447 行）头部都明确标了 `⚠️ DEMO-ONLY-SCAFFOLD（2026-05-03）：纯 mock，无后端依赖`，submit 只调 `StayListMock.applyAmendment` 改进程内存的假数据数组，根本不发 PUT /applications/:id。登录用户点「修改届を提出」会弹「修改届を提出しました」成功提示，但后端一无所知。
- **影响**：真实学生改外泊届以为提交成功（看到日语成功 toast），实际老师端永远收不到修改、承认 chain 不会重置。这是会上线的生产功能，属于「假成功」严重交互缺陷。同一文件内 list/detail 已接后端、唯独 edit 没接，状态割裂。
- **建议**：上线前必须把 StayEditForm 按头部注释写的 v1.0 计划接 ApplicationsAPI.update（构造 ApplicationUpdateBody + UUID guard + 5 个 catch 分支）。在接通前，至少在 UI 上禁用该入口或挂明显「开发中」标识，避免登录用户误以为已提交。

### [teacherweb-02] 点呼后端一不可达就静默降级到写死假学生，且不受 demo 开关门控
- **严重度**：high | **类别**：bug | **单元**：老师网页
- **位置**：`03_dev/teacher_web/v1/src/index.html` : 24739-24755
- **问题**：startSession 里，只要 backendReachable 为 false 或没找到 session，就走 `window.seedStudents(teacher.dorm)` 直接 seed 7 个写死假学生（リュウ イヒ 等），并 setLiveMode(true) 进入点呼实时界面，toast 只提示一句「demo モードで継続」。这段降级逻辑没有用 window.DEMO_MODE 包起来——也就是生产模式（用户没加 ?demo）下后端临时挂掉时照样会触发。第 24400 行 rollcallTodaySessions 失败时把 backendReachable 直接设 false 也佐证了这一点。
- **影响**：真实上线后若后端临时不可达（网络抖动 / 服务重启），老师点「开始点呼」会看到一份写死的假学生名单还以为在正常点呼查寝，点完的结果一条都不会进后端。点呼是这套系统的核心安全功能，这种静默假降级在生产环境是危险的——会让老师误判某个学生「已点到/已查寝」。
- **建议**：生产模式下后端不可达应该明确报错并阻止进入点呼（红色横幅「后端不可连接，无法点呼」），demo seed 降级只在 window.DEMO_MODE 为真时允许。

### [teacherweb-03] API_BASE 写死成明文 http，上线会明文传输密码和登录令牌
- **严重度**：high | **类别**：security | **单元**：老师网页
- **位置**：`03_dev/teacher_web/v1/src/index.html` : 10041
- **问题**：`window.API_BASE = "http://localhost:8000/api/v1";` 写死成明文 http。老师登录密码（POST /sessions/teacher 的 password）、创建老师时设的初始密码、以及返回的 access_token（JWT 登录令牌）全部通过这个地址走。WebSocket 地址也基于它推导（client.js 263-267），http 会推成明文 ws。
- **影响**：如果上线时忘了改成 https，老师密码、新建老师的初始密码、JWT 令牌都会明文走网络，同一 Wi-Fi 下可被嗅探，进而冒充老师。注释虽提到同源部署时改回 /api/v1，但这是靠人记得手动改，没有任何机制兜底。
- **建议**：生产构建强制走 https/wss；最好把 API_BASE 改成相对路径 /api/v1（同源部署自动跟随页面协议），或在 build_single_file.py 里按构建目标自动注入正确的协议，不依赖人工记忆。

### [teacherweb-04] 登录失败「3 回锁定 30 分」是纯前端假象，刷新即重置
- **严重度**：high | **类别**：security | **单元**：老师网页
- **位置**：`03_dev/teacher_web/v1/src/index.html` : 10309-10318
- **问题**：LoginScreen 用 React state `fails` 计数登录失败次数，到 3 次就显示「3 回失敗しました。30 分間ロックされます」（10313）。但这只是个组件内的内存计数，既没有 setTimeout 真的锁住输入框，也没靠后端——而背景已知后端学生登录就没有失败锁定，老师登录大概率同样没有。刷新页面、重开标签页、或干脆用脚本直接打 POST /sessions/teacher，这个「锁定」完全不存在。
- **影响**：界面给了老师和攻击者一个「有暴力破解防护」的错觉，实际后端可被无限次撞密码。配合 teacherweb-03 的明文传输，老师账户被爆破的风险被低估了。这属于安全感的虚假承诺，比没有提示更危险。
- **建议**：失败锁定必须由后端实装（按 login_id / IP 计失败次数 + 锁定窗口），前端只展示后端返回的 423 锁定状态。在后端没做之前，前端这句「30 分ロックされます」的文案最好别写得这么确定。

---

## 🟡 中等（63 条）

| ID | 类别 | 位置 | 标题 | 影响摘要 |
|---|---|---|---|---|
| android-base-06 | consistency | `AccountScreen.kt:373-378` | 注册区分页 サッカー部 朝点呼时间 7:10 与 spec 的 7:20 不一致 | 学生在注册时看到的点呼时间与实际规则差 10 分钟，可能误导其按 7:10 而非 7:20 理解截止时刻，引发对迟到判定… |
| android-base-07 | bug | `AccountScreen.kt:91, 488` | 密码长度校验下限 6 与界面提示「8 文字以上」矛盾 | 用户被告知需要 8 位，但系统实际接受 6 位，规则不一致；若后端有更严格的密码策略，6-7 位会在接通后端时被拒，造成… |
| android-base-08 | security | `AccountScreen.kt:56-57` | 默认密码硬编码 demo1234 预填且 UI 全程明文 | 若不清理，真上线时大量用户会以同一弱口令 demo1234 注册；即便本人测试，固定弱口令也是不良示范。 |
| android-base-09 | bug | `AppStore.kt:40-46, 53-58` | DataStore 解析失败静默回落 MockData，会悄悄丢用户数据 | 版本升级改了数据模型后，老用户一打开就丢全部本地数据并被填入别人的 demo 数据，且原始数据被覆盖无法恢复；异常被吞掉… |
| androidrest-04 | consistency | `FeedbackScreen.kt:66-68` | 「匿名フィードバック」声称匿名但同 App 携带完整身份，匿名承诺存疑 | 学生基于「匿名」前提说真话（比如投诉寮監），结果后端可定位到本人，承诺与实现不符，可能引发信任危机；AC 叙事里如果讲到… |
| androidrest-05 | bug | `MyPageScreen.kt:51-57` | MyPage 两个 grid 块（体調報告履歴/掃除提出履歴）跳到 Home，是死链 | 用户点「体調報告履歴」「掃除提出履歴」期望看历史，结果被弹回首页，功能形同虚设。当面演示给宿舍管理员时点到这两块会露馅。 |
| androidrest-06 | security | `AccountScreen.kt:54-55` | demo 预填数据里硬编码了 itsuki 真实邮箱和手机号 | 个人隐私信息进了公开仓库的源码，任何人 clone 都能看到。手机号若也是真号风险更大。 |
| androidrest-07 | consistency | `AccountScreen.kt:91` | Step4 提示「8文字以上」但实际校验只要 6 位，文案与逻辑不符 | 密码强度要求口径不一致，既误导用户也说明这块校验是随手写的没对齐。真接 backend 时若后端按 8 位校验，会出现「… |
| androidrest-08 | architecture | `AndroidManifest.xml:1-27` | AndroidManifest 缺 INTERNET / NFC 权限与 NFC feature 声明 | 审查重点问「权限是否过度」——这里相反，是权限严重不足：当前 manifest 状态下 App 根本不可能联网或读 NF… |
| androidrest-09 | test | `BusScreen.kt:31-54` | 全部 community/履历屏使用顶层硬编码 mock 假数据，无任何真实来源 | 都是 demo 占位，本身可接受，但巴士时刻表/行事预定这类一旦真上线就是「显示假信息误导学生」的来源（学生照着假巴士时… |
| applchain-03 | bug | `applications.py:476-543` | 审批链是无门槛并行 + 单人 approve 即推进 approved_partial — 与顺序链语义冲突 | 管理係/校長 可以在担任还没看之前就先 approve（顺序倒置）；若实际业务要求严格顺序（如校長必须最后盖章），现在的… |
| applchain-04 | consistency | `applications.py:532-542` | withdrawn / returned 状态无任何接口可产生 — 死状态 + 注释承诺的撤回功能缺失 | 学生无法撤回已提交的申请（只能改不能撤）；老师无法『差戻（退回要求修改）』。spec §7.2.4 把『要求差戻』列为 … |
| applchain-05 | bug | `applications.py:374-396` | PUT 修改届的 leave_date 未来校验在 setattr 写入之后，且漏掉 return_date>=leave_date 跨字段校验 | 通过修改届可绕过『帰寮日不早于出寮日』的业务约束，产生逻辑上不可能的申请（先回寮再出寮），下游食数计算/点呼免除范围可能… |
| applchain-08 | security | `dorm_life.py:262-297` | dorm-life / study-online 各申请的审批 role 列表与寮(宿舍)边界缺失，且角色集合内部不一致 | 冷蔵庫購入届里『国際交流部長』能审但物品所持/行事企画不能，schedule-change 里又把国際交流部長放进来，看… |
| applchain-11 | bug | `applications.py:180-227` | list_pending_for_me 对担任(homeroom)环没有班级过滤 — 担任老师看到全校待审而非自己班 | 与 applchain-02 同源：担任环的责任归属在『列表展示』层也失守，担任老师面板里塞满别班学生的申请，既是越权可… |
| auth-account-02 | bug | `seed.py:176` | seed.py 使用 ZoneInfo 但未 import，dev seed 直接崩溃 | 运行 `APP_ENV=dev python -m seed` 时跑到点呼 session 投入步骤会 NameErro… |
| auth-account-05 | security | `auth.py:32-41` | 学生登录用学号(grade+class+seat)做标识，可被规律枚举 | 攻击者无需先知道任何人学号，按编码规律遍历几千个组合即可命中所有真实学生账号，再配合无锁定的密码爆破。属于『可预测标识符… |
| auth-account-07 | security | `security.py:39-72` | JWT 用 HS256 对称密钥，无服务端撤销机制，24h 永久有效 | HS256 本身对单体后端可接受（不像多服务需要非对称分发公钥），不算高危。但缺撤销意味着：学生账号被停用(status… |
| auth-account-08 | security | `admin_registration_code.py:34-38` | 注册码与 reviewer 永久码 999999 在 public repo 中已知，且 6 位数字熵过低 | 6 位数字码在『同时只有 1 个有效 + 5 分钟 TTL』下风险可控，但叠加 auth-account-04（非一次性… |
| models-entry-02 | consistency | `schemas.py:597-610` | RollCallSessionOut 响应 schema 漏掉 schedule_mode / settle_at / started_source / ended_source 等模型字段 | teacher_web / iOS / Android 拿不到这些字段，无法在界面上区分点呼来源、是否已结算、是 spl… |
| models-entry-03 | bug | `schemas.py:281-301` | Application 共通字段（leave_method/return_method 等）在 model 层 nullable=False，但 PUT 修改届可单独传任一字段无组合校验 | 学生改届时可提交 return_date 早于 leave_date 的逻辑矛盾数据，绕过创建时的日期校验。后续食堂食数… |
| models-entry-04 | security | `main.py:76-82` | CORS allow_credentials=True 配合 allow_methods/headers=['*']，production 仅靠 origin 列表防线 | 若未来引入基于 cookie 的会话，宽松 CORS + allow_credentials 组合会放大跨站请求伪造风险… |
| migtest-03 | consistency | `models.py:74, 901` | is_demo / is_reviewer 等布尔字段 models 无 server_default 但迁移有，两条建表路径 schema 不一致 | alembic autogenerate 会永远把这些字段报成 server_default diff（噪音，且可能诱导… |
| migtest-05 | test | `test_registration_code.py:78` | test_refresh_invalidates_previous 含永真死断言 'or True' | 两次 refresh 产出相同 code（生成逻辑 bug 或随机碰撞）这种情况不会被这个断言捕获，给人虚假的覆盖感。 |
| migtest-06 | test | `test_study.py:124-125` | 学生自助签到只断言 status<500，等于只测不崩溃没测功能 | 签到逻辑出错（如签到时间窗口判定反了、记错状态）只要不抛 500 就测过，核心功能无实质保护。 |
| migtest-07 | test | `test_rollcall.py:168-180` | test_board_excludes_demo_students 在无 demo 数据下断言恒真，没真正测到过滤 | 给人 demo 过滤被两处测试覆盖的错觉，实际本用例不会因过滤逻辑被破坏而失败。 |
| backend-biz-04 | consistency | `discipline.py:153-185` | 撤销扣分不联动清扫单状态，撤销后清扫记录仍显示「不通过」 | 老师撤销一笔来自清扫的扣分后，扣分排名里分数减回去了，但 CleaningPage 上那条清扫记录仍显示「failed … |
| backend-biz-05 | bug | `email.py:160-175, 202-212` | 邮件发送设计要求 3 次重试，代码只发 1 次（attempts 永远 = 1） | 出寮届提交通知邮件（送给审批老师）一旦遇到 SendGrid 临时网络抖动/限流就直接 failed，不会自动重试，老师… |
| backend-biz-06 | architecture | `discipline.py:43-112` | 扣分排名 ranking 接口缺分页，全员一次性返回 | 一个宿舍几百名学生时一次返回全量数据问题不大，但若学校规模扩大或被恶意高频调用，响应体和内存会线性膨胀。属于设计欠缺而非… |
| rollcall-04 | bug | `rollcall.py:169-175` | start_session 的 -5 分钟校验用 minute 减 5，跨小时/负数会算错或崩溃 | 对开始时刻 minute < 5 的点呼场次，老师点「手動開始」会收到 500 错误，无法开始点呼；其余整点场次也算错 … |
| rollcall-05 | bug | `rollcall.py:293-328` | create_checkin 幂等 fallback 与状态判定有竞态：高并发同一学生可能写入两条 event | 并发或快速重复点呼（NFC 连碰两下）时可能产生重复 event，board/summary 取 latest 虽能去重… |
| rollcall-06 | bug | `ws_manager.py:86-99` | broadcast_sync 依赖已弃用的 asyncio.get_event_loop()，生产 ASGI 环境下可能静默丢失实时事件 | 实时点呼看板在生产环境可能完全不更新（老师碰一下卡但 LiveRollCall 不变色），且因为是静默 debug lo… |
| rollcall-07 | bug | `rollcall.py:561-627` | patch_event 改判前不校验 from_status 与 to_status 是否相同/合法，且任何老师可对已结束 session 的 event 反复改判刷扣分 | 扣分可被反复改判累积，学生纪律分被错误放大；改判无幂等/无终态约束，审计虽有 AuditLog 但数据已脏。 |
| rollcall-08 | security | `study.py:246-293, 394-411` | study create_checkin / patch_checkin / today_attendees 普遍缺 student 寮越权校验，patch_checkin 无角色限制 | 横向越权：任意老师可给非本寮学生写学習出席/改判（连带 study_absent 扣分 1.5 点）。 |
| rollcall-09 | security | `ws.py:30-69` | WebSocket token 走 query param，JWT 会进 Nginx/服务器访问日志，且无连接级心跳超时清理 | JWT 经 URL 泄漏后，24h 内可被重放连 WS 拿到实时点呼数据；半开连接堆积可能导致内存增长与对死连接的无效 … |
| sysfeat-04 | consistency | `flow_design.md:77, 190` | 签到 URL 域名 flow/hardware 用 dmsd.otogi2025.com，system_features 已迁 api.tomoshibi.cc | NDEF 贴纸写入的 URL 域名直接决定 Universal Link / App Links 能否唤起 App。若 … |
| sysfeat-05 | consistency | `system_features.md:1298` | system_features §8.1 student.category 定义为 ENUM 但后端是自由 Text，且サッカー部硬编码可疑 | 文档承诺的枚举约束在 DB 层不存在，任意字符串都能写入 category；前端/统计若假设只有两个值会出错。サッカー部… |
| sysfeat-07 | consistency | `system_features.md:673` | system_features §7.4.2 路径 A card_uid→学生查找标 ✅ demo_server，后端真实装是未完成占位 | 卡路径（路径 A，spec 里学生最主要的 1 步签到方式）在生产后端实质未实装——只能靠老师手动指定 student_… |
| sysfeat-08 | consistency | `flow_design.md:239, 297-301` | flow_design §5.4 称换机欺诈靠『旧密钥自动作废』，但后端无公钥/密钥管理可作废 | 文档把整个账号体系安全性建立在 ECDSA 密钥对管理上并标定稿，实装却毫无密钥概念，意味着 v1.0 实际只有密码登录… |
| ios-auth-03 | consistency | `AuthStubs.swift:900-905, 1034` | room_no_suffix 最长 4 字符 + 后端 room_no min_length=3，纯数字短房号会被后端打回 | 短房号（1-2 位数字）用户走完 5 步才在最后被 422 拒，体验差、错误归因不明确；与后端约束不对齐。 |
| ios-auth-04 | security | `AuthStubs.swift:1399, 167-189` | 密码以明文 String 跨 4 屏存于 @Published registrationDraft，生命周期偏长 | 明文密码在内存停留时间比必要的长，内存 dump / 调试快照可读到。属于纵深防御层面的弱点，非直接可利用漏洞。 |
| ios-community-03 | bug | `CommunityStubs.swift:1206-1216` | 寮墙详情『发送评论』按钮是空动作 Button {}，点了完全无反应 | 用户体验上是明显的坏掉按钮：输入评论点发送啥也不发生，会让人以为 app 卡死。即使是 demo 阶段，空动作按钮也比假… |
| ios-community-04 | consistency | `SeedModels.swift:129-130` | SongItem 仍带 up/down（赞/反对）死字段，spec 已于 2026-05-01 废止赞踩功能 | 死字段+死数据，会误导后续维护者以为还有赞踩逻辑；跨端对齐时（backend / Android）如果有人照着 iOS … |
| ios-community-05 | security | `AppStore.swift:514-542` | reportSong 封禁判定全在客户端：阈值 5/10/15 写死、所有通报都算到『我自己』头上 | 若上线时未把这套逻辑搬到后端，用户重装 app 或清数据就能绕过封禁；通报计数也不真实（只算到自己）。封禁这种带惩罚性质… |
| ios-community-06 | bug | `CommunityStubs.swift:1393-1394, 1452-1454` | EventDetailView 用数组下标当 id，与其他详情屏（按 .id 匹配）规则不一致，顺序一变就错位 | 现在写死数据顺序固定所以碰巧能跑，但接后端动态返回活动列表后，传下标会指向错误的活动详情（点 A 进 B）。也让代码可读… |
| ios-community-07 | bug | `CommunityStubs.swift:873, 1453` | 多处详情屏找不到数据时 fallback 到首条记录，会把『A 的详情』显示成『第一条』 | 传入非法/过期 id 时，用户看到的是『随便一条记录』而不是『没找到』，会误导：比如分享/深链到一首已删除的歌，打开却显… |
| ios-home-04 | bug | `HomeStubs.swift:1438-1444, 1774-1783` | 成功态弹 toast 用 step=.idle 复位，但 sheet 已关闭，存在无意义/竞态收尾 | 边界场景下会出现「我已经手动关了点呼弹窗，过两秒又冒出一条签到成功提示」的诡异体验；虽不崩溃，但在真实点呼这种要求严谨的… |
| ios-home-05 | bug | `HomeStubs.swift:184` | 首页问候日期写死「2026 年 4 月 22 日（火）」假数据 | 上线后任何一天打开 App，首页都显示「2026 年 4 月 22 日（火）」这个过去的固定日期，明显是演示残留，会让用… |
| ios-home-06 | bug | `HomeStubs.swift:505, 520, 523, 562, 722` | 扣分卡分数 / 遅刻欠席次数全部来自写死 SEED，非用户真实数据 | 扣分是这个系统对学生最敏感的数据（8 分外出禁止），首页主卡片却给每个用户都显示同一份写死的 4.5 点 / 遅刻 5 … |
| ios-home-07 | consistency | `HomeStubs.swift:653, 1360, 1440` | 点呼成功展示时间写死兜底「21:02」「時間内」 | 正常情况 recordCheckin 会写入时间所以兜底不常触发，但 21:02 是个写死的演示时刻，万一 checki… |
| ios-home-08 | consistency | `HomeStubs.swift:584` | absent 态「寮監に連絡」按钮把联系人姓名/内线号写死在客户端 | 不同宿舍/不同时段值班管理员不同，写死「田中先生 内線 101」上线后大概率是错的联系人；学生在被判欠席这种紧急场景下拿… |
| ios-home-10 | bug | `HomeStubs.swift:2528-2536` | 公告回复发送失败被静默吞掉，用户无任何提示 | 学生给老师公告发回复，如果请求失败（断网/后端报错），界面看不出任何异常——输入框内容还在但用户不知道没发出去，可能误以… |
| iosmypage-06 | consistency | `SEED.swift:15-17` | SEED demo 数据自相矛盾：女性别却分到男寮 + 头像/性别不一致 | 演示时个人信息页会显示『性别：女 / 男寮 A5』这种矛盾组合，老师或评委一眼能看出数据是拼凑的，降低 demo 可信度… |
| iosmypage-07 | bug | `MyPageStubs.swift:235, 760` | 月度点呼统计未按月份过滤，月份切换 pill 是摆设 | 『今月』统计名不副实（混入了非本月数据）；月份筛选按钮点了没反应，是死交互。接后端后若沿用这个结构，月度汇总会算错，影响… |
| iosmypage-08 | bug | `MyPageStubs.swift:877, 819` | 点呼详情页全是写死的单条假数据，跟列表点进来的项无关 | 学生点任意一天的点呼记录，进去看到的都是同一条假详情，跟实际选的对不上。demo 时翻几条就会穿帮。 |
| iosmypage-09 | consistency | `MyPageStubs.swift:957, 1015` | 扣分总分写死 4.5，与明细 7 条之和不符，且不随明细变化 | 三处分数（总分/明细求和/图表末点）靠手工保持一致，任何一处改了另两处不动就会出现总分跟明细对不上的矛盾，演示时容易被发… |
| ios-staylist-03 | consistency | `StayListStubs.swift:198-199` | StayListMock 留学生标志硬编码 true，注释已过期且与 AppStore 默认 false 矛盾 | 未登录态（mock）下永远按留学生 5 役职 chain 渲染（担任/国際交流部長/寮務課長/寮務部長/管理係），与登录… |
| ios-schedule-04 | bug | `ScheduleStubs.swift:192-193` | ScheduleView 跳事件详情用 firstIndex ?? 0，找不到时静默跳到错误的第一个事件 | 当前 demo 数据下不会触发，但属于隐藏的「打开错事件」类 bug，且 events 一旦接后端就会暴露。用数组 in… |
| teacherweb-05 | consistency | `client.ts:34-187` | client.ts 与实际加载的 client.js 严重漂移，是误导性死代码 | 未来真做 TS 重构、或有人误以为 client.ts 是真值去对照接口契约时，会拿到一份过时且签名错误的接口定义，导致… |
| teacherweb-06 | consistency | `index.html:11524` | 教师管理可访问角色清单三处对不上 | 前端导航按一组角色隐藏、后端按另一组角色判 403，会出现「导航里看不到入口但其实有权限」或反过来的错位。学習担当若后端… |
| teacherweb-07 | bug | `index.html:24451` | 跨寮老师 assigned_dorm 被一律归到男寮列，宿舍隔离展示错乱 | 登录后顶部会给跨寮老师显示错误的「男寮担当」标签；若降级到 demo seed，跨寮老师只能看到男寮假名单看不到女寮，宿… |
| teacherweb-08 | bug | `index.html:16877-17007` | 申請/通知/Outstay 等多处仍用写死 demo 数据，生产真假混杂 | 生产环境若某条申請没成功从后端 adapt，就会回落显示写死的假审批链（新股先生/中村先生这些不存在的老师名字），老师可… |
| teacherweb-09 | security | `client.js:269` | WebSocket 把 JWT 令牌放在 URL 查询串里传 | 令牌出现在 URL 里，可能被反向代理 / 服务器访问日志、浏览器历史记录留存；配合 teacherweb-03 的明文… |

---

## ⚪ 轻微（67 条）

| ID | 类别 | 位置 | 标题 | 影响摘要 |
|---|---|---|---|---|
| android-base-10 | consistency | `MockData.kt:57-65` | 减点 tier 字段语义与数据不符，欠席也标 tier=4 | tier 字段当前没被界面真正使用（减点界面靠 points 累加），属潜在隐患：将来若依赖 tier 做逻辑会取到错误… |
| android-base-11 | consistency | `MyPageScreen.kt:135-141` | MyPage 无注销账户入口，与 iOS 不一致 | 三端功能不一致：iOS 有删号入口、Android 没有。App Store/Google Play 上架对个人账户删除… |
| android-base-12 | bug | `RollCallSheet.kt:104-123, 159-184` | RollCallSheet 警告固定显示「点呼時間外」，与实际可点击扫描矛盾 | 用户看到「现在不在点呼时间」却仍能成功点呼，文案与行为矛盾，且没有任何时间窗校验逻辑（与 spec 的 window_s… |
| androidrest-10 | bug | `AccountScreen.kt:90` | Step3 邮箱校验正则过弱，几乎任何含@的串都通过 | 无效邮箱能注册，将来用于密码重置时收不到邮件（且后端邮件本身已知无重试）。属体验/数据质量问题，非安全要害。 |
| androidrest-11 | consistency | `SettingsScreen.kt:126` | SettingsScreen 版本号硬编码「1.0.0」，与项目实际版本脱节 | 显示的版本号是假的，与真实构建版本无关，误导。也违反项目「不硬编码 vX.Y.Z」的约定。 |
| androidrest-12 | architecture | `ApplicationDetailScreen.kt:148-154` | 撤回/送信等写操作仅改本地 state，缺乏与后端越权校验对应的提交链 | 现阶段是 demo 不暴露越权（因为根本不发请求），但提醒：真接 backend 时这些写操作要带身份并由后端做寮/班级… |
| androidrest-13 | bug | `LostFoundScreen.kt:78-79` | LostFound 新規届出、Deduction グラフ、Settings 隐私政策/利用规约均为空 onClick 死按钮 | 多处可点元素点了没反应，演示时显得半成品。利用规约/隐私政策若上线还空着，应用商店审核（Google Play）通常会因… |
| androidrest-14 | consistency | `AccountScreen.kt:282-288` | 部屋番号自填导致 spec 的房间唯一性/绑定无法保证 | 点呼按房间/座位组织（参见 demo 的 iPad 座位变绿），房号是关键定位字段。自填且不校验唯一性/存在性，真上线会… |
| applchain-06 | bug | `applications.py:375-383` | PUT 修改届对 meals_skip 的 exclude_none + 空列表清空逻辑有歧义，无法显式清空 | 食事不要(免餐)信息在修改届时可能被意外清空或无法清空，影响食堂食数计算(#7 Excel 导出)的准确性。属于边界数据… |
| applchain-07 | bug | `applications.py:46-53` | create/update 的『出寮日=明天起』用 date.today() 而非 JST，跨时区/UTC 环境会判错一天 | 若后端部署在 UTC 时区（云服务器常见），日本时间凌晨 0:00-9:00 之间 date.today() 还停在前一… |
| applchain-09 | bug | `dorm_life.py:277-289` | decide_fridge_purchase 状态机允许 rejected→其他状态以外，但 pending 可直接跳到 approved/ordered 缺约束 | 状态机不是白名单式（只允许 pending→ordered→delivered / pending→rejected），… |
| applchain-10 | security | `dorm_life.py:138-147` | create_schedule_change 用 model_dump() 全量展开入库，无字段白名单 — 潜在过量赋值风险 | 若任一 CreateIn schema 未来不小心加进 status 或 decided_by 字段，学生/老师就能在创… |
| applchain-12 | bug | `applications.py:102-140` | create_application 邮件/WS 广播失败会因未捕获异常导致整个提交回滚（无降级） | 邮件服务抖动时学生无法提交出寮届（核心业务被通知副作用拖垮），与项目『通知失败不阻断业务』的约定不一致。WS 广播失败则… |
| auth-account-09 | security | `auth.py:42-56` | 学号不存在与密码错误的响应耗时不同，存在用户枚举旁路 | 时间侧信道可枚举哪些学号/老师账号已注册。危害低（学号本就可枚举），但配合爆破有辅助价值。属加固项。 |
| auth-account-10 | consistency | `schemas.py:741-750` | TeacherCreateIn 的 email/role 校验弱于 register 流程，role 未在 schema 层约束 | 两条建老师路径的输入校验标准不一致：直接建老师可写入非法 email、含特殊字符的 login_id。危害有限（已登录管… |
| auth-account-11 | bug | `teachers.py:264-279` | delete_teacher 的 teacher_id 为裸 str，传非法 UUID 时 db.get 行为依赖底层不可控 | 上线用 Postgres 后，恶意/误传非 UUID 的 teacher_id 可能触发 500 而非 404，错误处理… |
| models-entry-05 | architecture | `models.py:982-985` | AnnouncementReply.author_id 跨表无外键，仅靠应用层保证，无任何 DB 层完整性约束 | 学生 / 老师被删除或停用时，其历史回复变成悬空引用，列表 join 取名字时可能拿到空或报错。审计 / 数据完整性弱于… |
| models-entry-06 | consistency | `models.py:806-832` | RollCallEvent.base_status CHECK 含 'init'，但注释和 spec 描述的合法值不含 init 的语义对不齐 | 注释和约束不一致会误导后续维护者。若 init 真的能写进 event 表，会出现「有事件记录但状态是未点呼」的脏数据，… |
| models-entry-07 | security | `models.py:396-420` | AuditLog 声称 append-only 但 ORM 层无任何禁止 UPDATE/DELETE 的机制 | 审计日志可被代码逻辑或攻击者篡改/删除，违背审计表「不可抵赖」的初衷。在真实上线、涉及学生扣分/越权操作追溯的系统里，审… |
| models-entry-08 | consistency | `models.py:249-257` | Application.receipt_submitted / is_long_vacation 用 nullable=True + default=False，三态语义混乱 | 类型标注 Mapped[bool] 与 nullable=True 矛盾（标注说非空，DB 允许空）。数据里可能混存 N… |
| models-entry-09 | consistency | `schemas.py:741-750` | TeacherCreateIn 的 email 校验弱（min_length=3 无格式校验），与其他 schema 用 EmailStr 不一致 | 通过该端点能创建 email 为 'a@b'（3 字符）这种非法邮箱的教师账号，破坏数据质量，且后续发邮件通知会失败。密… |
| models-entry-10 | bug | `models.py:882-908` | StudentRegistrationCode 缺乏唯一约束与「同时只有一个有效码」的 DB 层保证 | 并发或逻辑 bug 下可能同时存在多个有效注册码，扩大未授权注册的窗口。注册码是 App Store 上架的防滥用机制，… |
| models-entry-11 | bug | `main.py:55-60` | create_all() 仅在 app_env=='dev' 调，staging 环境既不建表也无 Alembic 保障会启动即失败 | staging 环境部署时若未手动跑 Alembic 迁移，服务启动后第一个 DB 操作报「no such table」… |
| models-entry-12 | bug | `models.py:1025` | Float 类型存扣分点数，浮点累加在阈值判定（4/8 分）边界可能误判 | 浮点累加误差在 4.0 / 8.0 整数阈值边界可能造成扣分阈值判定偏差，学生被错误地判定为达到/未达到清扫或禁足线。概… |
| models-entry-13 | consistency | `models.py:72-91` | Student.is_demo 演示账号标志默认 default=False 落库，依赖每处查询主动过滤，漏过滤即泄漏到生产统计 | 任何新增的学生列表/统计端点若忘记加 is_demo 过滤，演示/审核账号会污染真实数据（出席率、扣分排名、食数计算）。… |
| migtest-08 | security | `f6a7b8c9d0e1_add_demo_reviewer_flags.py:56-60` | 生产迁移里硬编码演示码 999999 清理逻辑 | 迁移文件长期留有演示后门的痕迹；999999 作为 reviewer 保留码的语义散落在迁移、router、测试多处，未… |
| migtest-09 | architecture | `models.py:266` | applications.bus_route_id 是悬空外键引用，无 bus_routes 表 | 字段存在但无对应表也无约束，写入任意 UUID 不会被校验；属于未完成功能的半成品列，易让人误以为巴士功能已落库。 |
| migtest-10 | doc | `conftest.py:1, 6-7` | conftest docstring 称 in-memory SQLite 但实际用文件库，注释与代码不符 | 误导维护者以为测试完全内存隔离；实际落盘的 test_tomoshibi.db 会在工作区残留、可能被旧 schema … |
| backend-biz-07 | bug | `discipline.py:43-67` | ranking 的 month 参数无格式校验，错误格式静默返回空榜单 | 格式错误被静默吞掉，老师看到全员 0 分会以为本月没人扣分，实际是参数格式错。难排查的数据正确性问题。 |
| backend-biz-08 | architecture | `meals.py:67-93` | meals export 用 iter([payload]) 把整份 Excel 一次性塞内存，命名为 StreamingResponse 但并非流式 | 学生/申请规模大时，导出大区间会占用较多内存，但对一个宿舍体量影响有限。属于可接受但需知晓的设计权衡，不是 bug。 |
| backend-biz-09 | security | `meals.py:82-92` | meals export Content-Disposition filename 未转义，文件名注入风险（低） | 当前无实际可利用性（date 类型限定了取值），但若以后改成接受用户自定义文件名前缀，未转义的 header 拼接会变成… |
| backend-biz-10 | bug | `announcements.py:83-101` | _resolve_actor 对缺失/非法 sub 不容错，可能抛未捕获异常 500 | 构造一个签名合法但 payload 缺 sub / sub 格式异常的 token（或自家签发逻辑变更后漏字段），调用回… |
| backend-biz-11 | architecture | `announcements.py:60-66, 256-274` | 公告列表/详情/回复存在 N+1 查询，按回复逐条 db.get 取作者名 | 回复多的热门公告，详情接口查询次数随回复数线性增长，响应变慢。宿舍体量下可接受，但属于可优化点。 |
| backend-biz-12 | consistency | `announcements.py:411-474` | 公告编辑/删除仅限作者本人，寮監/上级无法管理下属公告（已知限制但需确认风险） | 若发公告老师离职或被停用，其错误/过期公告将永久无法修改删除，只能直接改数据库。属于产品决策遗留风险，非代码 bug。 |
| backend-biz-13 | doc | `discipline.py:40, 121` | create_manual_demerit 文档串说含「学習担当」权限，与实际 _ADMIN_ROLES 不符 | 误导后续维护者以为学習担当能手动加扣分，实际会被 403 拒绝。仅文档不一致，不影响运行。 |
| backend-biz-14 | bug | `announcements.py:245` | 公告详情写已读用 db.get(AnnouncementRead, (ann.id, principal.id)) 复合主键顺序需与定义一致 | 当前顺序正确无 bug；但这种「靠声明顺序对齐」的隐式契约脆弱，未来改 model 列序时容易引入查错主键导致重复写已读… |
| rollcall-10 | security | `study.py:476-491` | list_absence_requests 缺寮过滤，学習担当能看全校所有学生的欠席届（含理由明文） | 任意老师可读取全校所有学生的学習欠席届及其理由明文，超出本寮管辖范围，隐私越权。 |
| rollcall-11 | bug | `study.py:586-617` | _notify_absence_submitted 用裸 except: pass 吞掉所有异常，通知失败无任何痕迹 | 学習担当的欠席届通知静默失败时，老师永远不知道有学生提交了欠席届，也无日志可排查。 |
| rollcall-12 | security | `rollcall.py:242, 315-316` | create_checkin 的 ts_local / study checked_at 完全信任 client 传入时间，可伪造 present/late 判定 | client 可传一个窗口内的旧时间把本应 late 的点呼伪造成 present，绕过迟到扣分；也可传未来时间。 |
| rollcall-13 | security | `security.py:69-72` | JWT 算法可被配置成不安全值，decode 未硬锁安全算法清单 | 现状默认安全；仅在配置被误改时存在风险。 |
| sysfeat-06 | doc | `flow_design.md:112` | flow_design §3.1 步骤 14 时间窗硬编码 21:50-22:05，与实装动态 session 窗口不符 | 作为『签到流程唯一真值』文档，把判定窗口写成固定时刻会误导读者以为窗口是 hardcode；且这个数字与 RollCal… |
| sysfeat-09 | consistency | `system_features.md:1119` | 注册码限流：spec §7.16.8 承诺『10 秒最短间隔』，需确认后端 refresh 是否实装 | 若无节流，老师误触/脚本连点 refresh 会高频作废旧码，集团登录时学生频繁拿到失效码；属低危但影响运营体验。 |
| sysfeat-10 | doc | `system_features.md:600` | system_features §7.3.5 类型B注意事项仍留旧时刻19:30，正文已统一19:40 | 晚自习关键时刻（开始/遲刻判定/自动开启）散落多处，后端 cron 与客户端倒计时若各取一处易漂移。属可控的文档清晰度问… |
| sysfeat-11 | consistency | `system_features.md:1067, 1099` | system_features §7.16.5 注册码使用侧 audit log 标 v1.1，与 §7.16.2 第8条『生成/使用全 audit』承诺冲突 | 注册码被谁、何时使用在 v1.0 无审计记录，若出现非授权注册无法追溯使用方；且这与同文档铁律自相矛盾，审查时容易判断错… |
| ios-auth-05 | architecture | `AuthStubs.swift:1659-1668, 1909-1964` | PwResetView（找回密码屏）已成死代码 — 登录页入口已隐藏，无任何路由可达 | 死代码增加维护负担和阅读混淆；文件头清单与实际可达性不符。无功能危害。 |
| ios-auth-06 | consistency | `AuthStubs.swift:1680-1681, 1717-1721` | メール登录模式 UI 可选但点登录直接被拒，是死交互 | 用户被引导用邮箱登录却被拒，文案与实现矛盾，体验割裂。Apple 审核也可能视メール tab 为「无功能控件」。 |
| ios-auth-07 | bug | `AuthStubs.swift:2123, 1525` | createAccount 成功后未 resetLoginFailures，注册流不复位登录失败计数 | 边界场景下锁定段位计算偏高（先失败登录数次→改去注册→注册成功→再登录失败直接进高段锁定）。概率低但逻辑不自洽。 |
| ios-auth-08 | bug | `AuthStubs.swift:766-800` | Image Playground 5.5 秒固定兜底定时器与异步 sheet 结果竞态，loading 状态可能误复位 | 当前不可达无实际影响；未来恢复该功能时埋了 loading 状态与真实进度不同步的 UX bug。 |
| ios-auth-09 | bug | `AuthStubs.swift:101-105` | Splash 自动登录只验 token 存在性，不验有效性 → 过期 token 用户卡 home 后才发现失效 | 过期 token 用户进入 home 后遇到一连串 401，体验差；依赖各页面 401 处理（已知后端/客户端 401 … |
| ios-auth-10 | security | `AuthStubs.swift:1725` | DEMO magic 密码额外接受 "00"，比注释声明的 demo 凭证更宽松 | 仅 demo build 影响，非生产漏洞。但 demo 凭证范围与注释/文档不一致，且过弱。 |
| ios-community-08 | bug | `CommunityStubs.swift:1239-1249, 1275-1292` | EventsView 日历写死只能在 2026 年 4 月/5 月之间切，今天写死 4/23 | demo 阶段没问题，但作为真上线的活动日历功能，到了 2026 年 6 月以后或非 4-5 月就完全不可用，『今天』高… |
| ios-community-09 | doc | `CommunityStubs.swift:294-301, 530, 909, 1114-1117, 1141` | 多个详情/表单屏存在写死的假内容（保管位置、到着时刻、拾得日时、投稿理由、评论） | demo 视觉对齐用，但混在『看起来像真数据』的字段里（尤其宅配的到着时刻 14:22、保管场所 A-3），用户可能当真… |
| ios-community-10 | bug | `CommunityStubs.swift:370, 405, 422-426` | LostView 搜索框 search 状态完全没用于过滤，输入无效果 | 用户在遗失物列表输入关键词搜索却没任何反应，是个明显的『装了搜索框却不工作』的体验缺陷。 |
| ios-community-11 | consistency | `CommunityStubs.swift:374-375, 617-619` | 遗失物认领『私のものです』直接弹『已通知投稿者』，但遗失物声明是寮監专管、无身份核验 | 认领贵重物品（如 SEED 里的『財布 钱包』『黒の鍵 钥匙』）只靠点一下按钮、无身份核验，生产化后存在冒领风险。当前又… |
| ios-community-12 | test | `AppStore.swift:544-550` | resetSongBan 注释自承『未配线』，是没接入口的死方法 | demo 时想演示『封禁后重置体验』却没有入口，封一次就回不去（除非重装）。死方法本身无害但说明点歌封禁 demo 流程… |
| ios-home-09 | test | `HomeStubs.swift:40-47, 266` | DemoCardCycleGesture 已掏空成空壳但仍挂在卡片上（死代码） | 目前是无害空壳（长按后门确实已拆），但留着一个专门为 demo 后门起名的空 modifier 容易误导后续维护者，也给… |
| ios-home-12 | consistency | `HomeStubs.swift:2554-2555` | 公告详情 reply.authorKind 用裸字符串 "teacher" 比较，易与后端字段漂移 | 若后端 authorKind 取值与客户端写死的 "teacher" 不一致，老师的回复不会被标成「教員」、也不高亮，学… |
| iosmypage-10 | bug | `MyPageStubs.swift:1493` | 通知设置开关纯本地 state，自己注释承认不接后端 | 学生关掉某类通知，下次进设置又全部变回开启，设置不生效。属于已知 demo 缺口，但上线前必须接（涉及推送订阅），现状会… |
| iosmypage-11 | consistency | `MyPageStubs.swift:1445` | MyPackagesView 标题混入中文「快递」，与全日语 UI 不一致 | 面向日本用户的界面里冒出中文『快递』，与系统其它处『荷物』不统一，老师/评委一眼能看出是开发期残留，影响完成度观感。 |
| iosmypage-12 | bug | `MyPageStubs.swift:1633` | 删账号成功后只清 token，没退出 MyPage 视图栈/没跳登录 | 若根视图没监听 authToken 切换登录页，删号后用户会停留在已删除账号的个人页，后续操作全部 401，体验混乱。能… |
| ios-schedule-02 | consistency | `ScheduleStubs.swift:ScheduleStubs 全文 / BusListStubs 全文` | 审查任务前提反了：Schedule/BusList 不是废弃屏而是活屏；真正死代码是旧 BusView | 对本次审查无直接代码危害（Schedule/BusList 本身健康），但旧 BusView + .homeBus ro… |
| ios-staylist-05 | bug | `StayListStubs.swift:776-783` | audit 拉取失败被 catch 吞掉只 print，详情页静默显示空履历 | 网络抖动导致 audit 失败时，学生会误以为这条申请没有任何操作历史（实际有，只是没拉到）。属于错误被静默吞掉、状态语… |
| ios-staylist-06 | consistency | `StayListStubs.swift:315-368` | makeSteps 按 status 逆算 chain 进度的 mock 逻辑会造假与真实 chain 不符的中间态 | 未登录预览（含 Apple 审核员看到的）展示的承认进度是编造的，可能与同一条 status 在真实后端的 chain … |
| ios-staylist-07 | consistency | `StayListStubs.swift:1663` | AuditLogOut→Entry 用 actor_type 粗暴把所有教员操作标成学生本人名或泛称「教員」 | 登录后真实履历里，学生本人操作行显示成硬编码 mock 名而非自己名字（轻度信息错误）；教员操作丢失役职信息，老师 38… |
| teacherweb-10 | bug | `index.html:24595-24606` | 登录显示的「先生/担当」用前端选中卡片而非后端真实账户身份 | 正常流程下两者一致影响不大；但如果列表卡片和实际登录账户因数据延迟/缓存对不上，会出现顶部显示 A 老师、实际登录的是 … |
| teacherweb-11 | consistency | `index.html:15246` | 创建老师角色下拉里出现简体中文「教师」，违反 UI 日语铁律 | 如果后端角色枚举里没有「寮務一般教师」这个简体写法，创建会失败或写入一个后端识别不了的角色值，导致该老师权限判断异常。即… |
| teacherweb-12 | security | `demo_server.py:20` | demo_server.py 对所有来源开放 CORS 且无任何鉴权 | 只要它跑在能被访问的网络上，任何人都能 POST /checkin?no=任意号码 伪造点呼事件，浏览器 poll 到就… |

---

## 🔧 主会话手动补充（17 单元未覆盖的配置层）

### [manual-01] 🟠 开发数据库备份未被 git 忽略
- **位置**：`03_dev/backend/v1/tomoshibi_dev.db.bak`
- **问题**：`.gitignore` 挡了 `*.db` 但没挡 `*.db.bak`。该备份含学生数据 + 密码哈希。
- **影响**：一旦误 commit 会进公开 GitHub 仓库 → 数据泄漏。
- **建议**：`.gitignore` 补 `*.db.bak` / `*.bak`，并确认该文件从未进过历史。

### [manual-02] ⚪ .env.example 模板漏 8787 端口（已更正先前误判）
- **位置**：`03_dev/backend/v1/.env.example:35`
- **问题**：模板 `CORS_ORIGINS` 只写 5173,3000，少了老师网页实际用的 8787。注：`config.py:57` 的代码默认值已含 8787，所以直接跑没问题；只有照模板手动配 .env 才会漏。
- **影响**：照模板配置部署时，老师网页(8787)调后端会被浏览器跨域拦截。
- **建议**：`.env.example` 的 CORS_ORIGINS 补上 8787，与 config.py 默认值对齐。

### 已复核确认（主会话亲自读代码）
- `rollcall-01`（NFC 防代刷后端零实装）：代码注释 `rollcall.py:266` 自证「student テーブルに card_uid カラムなし」，nonce/签名「v1.1 起追加」。属实。
- `rollcall-02`（WebSocket 越权广播全校）：`ws_manager.py:71-84` broadcast 无寮过滤，注释第 13 行自承「当前广播全部」。属实。
- `rollcall-06`（同步广播在生产线程池取不到 event loop 静默丢事件）：`ws_manager.py:92-99` 属实。

---

## 🔧 2026-05-30 修复进展 + 交付状态

> 本审查会话与 itsuki 用 `/goal` 启动的「teacher_web v1.0 上线施工」会话**并行**，共享同一 git 工作区。分工：`/goal` 修后端崩溃 bug + 老师网页接后端；本审查会话修 iOS 安全 + 部分后端 + 文档死链。

### ✅ 已修复并固化（commit）
| 发现 | 修复内容 | commit |
|---|---|---|
| auth-account-01 teachers.py 缺 import | 补 func / IntegrityError | d9e65f1（/goal）|
| backend-biz-01 discipline.py 缺 import | 补 dorm_units_for_teacher / ZoneInfo | d9e65f1（/goal）|
| rollcall-04 点呼<5min 开始崩 | 改 timedelta 算窗口 | d9e65f1（/goal）|
| 外宿误扣分 / 今日列表缺上界 / 手动扣分归错月 | /goal 自查补 | d9e65f1（/goal）|
| backend-biz-13 discipline docstring「学習担当」 | 去掉 | d9e65f1 |
| auth-account-02 seed.py 缺 ZoneInfo | 补 import | d9e65f1（审查会话改 /goal 带走）|
| iOS Keychain 令牌可跨设备备份 | 改 ThisDeviceOnly（xcodebuild 验证）| 6cc5c07 |
| iOS 登出不清 token | 加 app.authToken = nil | 6cc5c07 |
| applchain-05 改届缺 return>=leave 校验 | 补跨字段校验 | 6cc5c07 |
| manual-01 db.bak 未被 git 忽略 | .gitignore 加 *.db.bak / *.bak | 6cc5c07 |
| WEB_DESIGN_LOG _legacy 路径死链 | 补 components/ | 6cc5c07 |

### ⚠️ 改过但被并发覆盖 — 待重修
- **models-entry-01** `schemas.py` 允许 dorm_unit=3（DB CHECK 只认 1/2/4 → 落库 500）：本会话加过 field_validator，被 /goal 提交 schemas.py 时覆盖丢失。**需重新加**：`StudentAccountCreateIn` 补 `dorm_unit in (1,2,4)` 校验。

### 🔴 未修 — v1.0 上线 backlog（重大工程 / 实装，非「修 bug」能解决）
- **NFC 防代刷全栈**：card_uid↔学生绑定 + 10秒 nonce + ECDSA 签名 + 点呼机 src/ 实装（后端 rollcall-01 + iOS ios-home-01 + Android NfcScreen + 设计文档 flow_design 全空）
- **Android 整个无网络层** → 接后端要从零写
- **iOS 点呼 / 6 类申请接后端**（RollCallAPI 死代码 + ApplyPreview 假提交）
- **删账号 DELETE /accounts/me**（/goal 的 admin_accounts.py 在做账号管理，可能覆盖此需求）
- **后端写接口寮越权校验**（rollcall / cleaning / front_desk / applications decide_approval / study）
- **学生登录失败锁定 + 注册码一次性**（auth-account-03/04）
- **各端演示假数据替换成真数据**（iOS SEED / Android MockData / 老师网页降级假学生）
- **spec 冻结区文档过期**（DEVICE_REGISTRY 旧型号 RPi 4B / ENUM 缺 manual / RollCall_Spec 路径 C / ERROR_CODES 状态码）— 规格冻结区，需 itsuki 解冻后改
- **progress_overview 严重过期**（VPS 架构图 / GitHub 写成私有 / 独立 repo 残留）— itsuki 维护的对外文档

完整 175 条原始发现见本文件上半部分；误报已剔除（teacherweb-04 后端有真锁定 / ios-community-02 降级）。

---

## 🔧 2026-05-31 续：老师网页 12 条逐条核实 + tw-11 真相

> itsuki + 另一会话逐条核实 teacherweb-01~12，本会话亲自复核 tw-11 / tw-06。

### 核实总账（12 条）
- ✅ 已修 6：tw-01（学生账户页接真后端 7f638a5 / 54ca1ac）/ tw-02（点呼降级假学生已删 4c2578f）/ tw-03（后端地址改相对路径自动跟随 HTTPS）/ tw-07（跨寮老师读后端真身份 a32084c）/ tw-10（顶部身份改后端下发）/ tw-12（demo_server.py 整文件删）
- ⚪ 误报 1：tw-04（老师登录「3 次锁 30 分」）— 后端 login_teacher 有真失败计数 + 30 分锁定，前端非唯一防线
- ❌ 未做 3：tw-09（WebSocket token 走 URL，需后端改鉴权配合，W8 未排）/ tw-05（client.ts 死代码，标低优先推迟）/ tw-11 + tw-06 见下（已修）
- 🟡 有尾巴 1：tw-08（申請 / 通知假数据大部已清，漏 window.FRONT_DELIVERIES / FRONT_LOST_ITEMS 两个死定义没清，前台页已接真后端、不影响功能）

### ✅ tw-11 + tw-06 已修（commit 9a15aba）— 但原始发现的「前提」是错的
- **原发现误判**：tw-11 写「后端角色枚举里没有『寮務一般教师』，选了创建失败 / 写入识别不了的角色」。
- **本会话复核真相**：恰恰相反 — 该角色前端下拉 + 后端 `models.py` 元组 + DB CHECK 约束 + `create_teacher` 的 INVALID_ROLE 校验 + meals / incidents / guidance / student_profile 四个权限组 + 2 个 Alembic 迁移 + 一票测试（主账号 tannin）**全都有**，写法一致（都简体「师」），选了它**能正常创建、有真权限**。真正的问题只是「教师」用了简体，违反日语 UI 用字。
- **itsuki 拍板**：角色保留（给无具体职位但参与管理的老师用，可开多账号备用），权限维持普通寮务等级（食数 / 事案 / 指导 / 学生档案，无建删老师等管理层高权限）不动；仅修正用字。
- **修复**：全链路 25 处代码 + 7 处活跃设计文档「寮務一般教师」→「寮務一般教師」统一，后端 193 测试全过。05_logs 历史日志 + 99_archive 归档保留简体（历史快照不动）。
- **教训**：转述 AI / 工具的审查结论前先审前提（见 memory feedback_relay_ai_output_audit_premises）— 若直接照「删前端选项」修，会砍掉后端真实支持的合法角色。
