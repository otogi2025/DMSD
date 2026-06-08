# iOS 接线 — /goal 完成条件 + 详细规格

> 本会话压缩后用 `/goal` 自动迭代实装 iOS 接线。`/goal` 是 Claude Code 命令：设一个「完成条件」后，本会话一轮接一轮自己干，每轮由小模型（Haiku）检查条件达没达成，达成才停。**不是交给另一个 AI，是本会话自己跑。**
> ⚠️ 检查的小模型**只看对话里亮出来的内容、不自己跑命令读文件** → 完成条件必须是对话输出能证明的（编译结果、`git log`），不能写「接好了」这种没法验证的话。
> 后端那半已做完（commit `d815995`，未 push）；本规格里的后端路径 / 字段 / iOS 模式 / 文件位置 / 假数据字段，都逐个 grep + Read 真代码核实过。行号截至写稿，以 grep symbol 名为准。用完移 `99_archive/`。

---

## ▶ 复制下面整段，粘到 `/goal ` 后面回车

```
先 Read 本文件 00_admin/handoff/iOS接线_GOAL提示词.md 的「详细规格」全段再动手。按它把 iOS 学生 app（工作目录 03_dev/student_ios/v1/TomoshibiApp/）8 类界面的生产分支(#else)从读假数据 SEED.* / 假 toast 改成调真后端：①扫除历史 ②个人信息修改 ③体调欠席其他 ④点歌 ⑤遗失物 ⑥修繕来訪代理 ⑦点呼历史 ⑧减点明细。每轮挑还没做完的功能往下做，做完一个 commit 一个（显式列文件名、不 push、不打 tag、不写 Co-Authored-By）。

判定完成必须在对话里贴出这三样真实输出（不是复述「成功」，是贴原始输出行）：
(1) cd 03_dev/student_ios/v1 && xcodegen generate 后，xcodebuild -scheme TomoshibiApp -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build 输出 ** BUILD SUCCEEDED **；
(2) xcodebuild -scheme TomoshibiAppDemo（同 destination）也输出 ** BUILD SUCCEEDED **；
(3) git log --oneline -12 显示 8 个功能各有对应 commit。

硬约束（违反算没做完）：保留所有 #if DEMO 假数据分支不删；不碰 Android；代码注释中文、UI 字符串日语；只改详细规格里列出的 iOS 文件，不动后端、不改 project.yml（新文件靠 xcodegen 目录 glob 自动收）；commit 前 git diff --cached 核对、别卷入别会话改动。

刹车：连续 3 轮卡在同一个编译错误修不掉，或累计跑满 30 轮，就停下、报告卡在哪个功能 / 什么编译错，不再继续，把控制权还给我。
```

> 这段约 1200 字（`/goal` 上限 4000，没超）。刹车的「30 轮」嫌多可自己调小。要无人值守得同时开 auto mode（自动模式，负责一轮内自动批准工具调用）。

---

# 详细规格（/goal 跑起来后本会话照这个实装）

## 0. 一句话任务 · 工作目录

- **你的活**：把 iOS 学生 app 里 8 类界面的**生产分支**（`#else`）从「读假数据 `SEED.*` / 提交只弹假 toast」改成「调真后端」。
- **演示分支**（`#if DEMO`）的假数据**原样保留**——itsuki 拍板：假数据是演示版讲叙事用的，不删，只是切到生产版时不干扰。
- **不碰 Android**。
- **工作目录**：`03_dev/student_ios/v1/TomoshibiApp/`（仓库根 `~/dev/DMSD`）。

---

## 1. 背景（必读，别跳）

- 后端「iOS 缺的这 6+1 个功能」已全部实装 + 测试 + commit（提交号 `d815995`，全套 353 passed，**未 push**）。后端路由已在 `app/main.py` 注册完（`songs` / `lost_found` / `misc_requests` / `cleaning` / `rollcall` reports / `student_profile` 都在）。
- 「两端对齐」= 后端做完 + iOS 接上。你做的是 iOS 这半。
- iOS 工程靠两个 scheme（构建方案）分演示 / 生产：
  - **演示版** scheme `TomoshibiAppDemo` → 编译时定义 `DEMO` 宏 → 走 `#if DEMO` 分支 → 全假数据。
  - **正式版** scheme `TomoshibiApp` → 不定义 `DEMO` → 走 `#else` 分支 → 连真后端。
  - 两个 scheme 编译后都必须 `** BUILD SUCCEEDED **`。
- **demo 宏与网络底座现状**（你照抄这些，别重造）：
  - `Foundation/Network/APIClient.swift`：`APIClient.shared`（`@MainActor` 单例）。`DEBUG`（Xcode Run）打 `http://localhost:8000`，`RELEASE`（Archive）打 `https://api.tomoshibi.cc`。已配好 token 自动加 `Authorization: Bearer`、ISO8601 健壮日期解码、422/401/2xx 状态码处理。
  - 登录态 / 当前用户已就绪：`AppStore.shared`（`@MainActor`、`ObservableObject`、`@Published`）里 `authToken`、`currentUser: User?`、`displayUser`（真用户 ?? `SEED.user` 占位）、`loadMe()` 登录/启动时拉 `GET /students/me`。

---

## 2. 后端契约（全部 prefix `/api/v1`，学生用学生 token，已核实路径）

### 2.1 扫除提出履历
- `GET /cleaning/me` → `[CleaningAssignmentOut]`（学生查自己，按计划日倒序）
- `CleaningAssignmentOut`：`id`(UUID), `student_id`(UUID), `area`(str), `scheduled_date`(date "yyyy-MM-dd"), `status`("assigned"|"done"|"passed"|"failed"|"skipped"), `assigned_by_teacher_id`?(UUID), `assigned_at`(datetime), `done_at`?, `inspected_by_teacher_id`?(UUID), `inspected_at`?, `failure_reason`?(str), `demerit_event_id`?(UUID)

### 2.2 个人信息修改
- `GET /students/me` → 身份信息（iOS 已有 `StudentsAPI.me()` 在用，返回 `StudentMeOut`）
- `PATCH /students/me` body `{email?, phone?, avatar_url?, room_no?}`（**只传要改的字段，PATCH 语义**）→ `StudentProfileBasic`
  - `room_no` 后端校验前缀与本人寮一致（男寮 `M***` / 女寮 `W***`），跨性别寮返 **422 `INVALID_ROOM_FORMAT`**；`email` 撞别人返 **422 `EMAIL_TAKEN`**。两种 422 的日语提示后端已给，iOS 的 `APIError.unprocessable(msg)` 会原样带出来，直接弹给学生即可。
- `StudentProfileBasic` 字段比 `StudentMeOut` 多一个 `registered_at`，其余同。**解码可直接复用 `StudentMeOut`**（Swift `Decodable` 默认忽略多余字段）。

### 2.3 体调报告 / 当次缺席 / 其他问题（点呼三弹窗）
- `POST /rollcall/reports` body `{kind:"health"|"absence"|"other", body:str(1~2000), session_id?:UUID}` → `RollCallReportOut`(201)
- `GET /rollcall/reports/mine` → `[RollCallReportOut]`
- `RollCallReportOut`：`id`(UUID), `student_id`(UUID), `session_id`?(UUID), `kind`, `body`, `created_at`, `resolved_at`?, `resolved_by_teacher_id`?(UUID)
- （老师端 `GET /rollcall/reports` + `PATCH /reports/{id}/resolve` 学生 app 不用）

### 2.4 点歌（最小版）
- `POST /songs` body `{song_title:str, artist?, note?}` → `SongRequestOut`(201)（`dorm_unit` 后端按登录学生的寮自动取）
- `GET /songs?dorm=1|2|4`（不传 = 全部）→ `[SongRequestOut]`（投稿顺序新→旧）
- `SongRequestOut`：`id`(UUID), `student_id`(UUID), `dorm_unit`(int), `song_title`, `artist`?, `note`?, `created_at`
- 通报 / 封禁 / 投票是 v1.1，**最小版只做投稿 + 一览**。

### 2.5 遗失物社区投稿
- `POST /lost-found` body `{post_type:"found"|"lost", item_name:str, description?, location?}` → `LostFoundOut`(201)
- `GET /lost-found?status=open|resolved`（不传 = 全部）→ `[LostFoundOut]`
- `PATCH /lost-found/{id}/resolve`（投稿者本人；非本人 403；已 resolved 409）→ `LostFoundOut`
- `LostFoundOut`：`id`(UUID), `student_id`(UUID), `post_type`("found"|"lost"), `item_name`, `description`?, `location`?, `status`("open"|"resolved"), `created_at`, `resolved_at`?

### 2.6 修繕 / 来訪者 / 代理受取
- `POST /misc-requests` body `{kind:"repair"|"guest"|"proxy_receipt", subject:str, detail?, target_date?:date}` → `MiscRequestOut`(201)
- `GET /misc-requests/mine` → `[MiscRequestOut]`
- `PATCH /misc-requests/{id}/withdraw`（本人，仅 pending；非本人 403 / 非 pending 409）→ `MiscRequestOut`
- `MiscRequestOut`：`id`(UUID), `student_id`(UUID), `kind`, `subject`, `detail`?, `target_date`?(date), `status`("pending"|"confirmed"|"withdrawn"), `created_at`, `confirmed_by_teacher_id`?(UUID), `confirmed_at`?, `withdrawn_at`?
- （老师端 `GET /misc-requests` + `PATCH /{id}/confirm` 学生 app 不用）

### 2.7 点呼历史 + 减点明细（后端本就有，不用新建后端）
- `GET /students/{student_id}/profile`（学生本人可查自己；要先拿到自己 UUID，见 §3.4）→ `StudentProfileOut`，取其中两块：
  - `rollcall_events[]`：`{id, session_id, session_type("morning"|"evening"), base_status, status_source, checked_in_at}`
  - `demerit_events[]`：`{id, source_type, points, reason, month("yyyy-MM"), created_at}`
- 各块默认最近 20 条（`?limit=` 可调，最大 100）。
- 当月合计扣分另有 `DisciplineAPI.mySummary().total_points`，`loadMe()` 已拉进 `currentUser.points` → 「今月合計」生产版已经是真数据，不用改。

---

## 3. iOS 既有模式（照抄这些真样板，别另起炉灶）

### 3.1 endpoint 包装（`Foundation/Network/Endpoints/*.swift`）
风格：`enum XxxAPI` + `@MainActor static func`，请求体 / 响应模型就近放同文件，字段 `snake_case` 跟后端 byte-perfect 对齐，复用 `NetworkModels.swift` 的 `StudentBrief`。
- **日期方针**：`date`("yyyy-MM-dd") 与「只展示不计算的 datetime」→ **保 `String`**；需要参与逻辑 / 排序的 `datetime` → `Date`（`APIClient` 已配健壮解码）。
- **PATCH 无 body** 用底层 `request`（`APIClient` 没有 PATCH 便利方法）。

真样板（`OutingsAPI.swift`，照这个写）：
```swift
struct OutingOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let student: StudentBrief?
    let outing_date: String   // date → String
    let status: String        // "pending" | "approved" | "withdrawn"
    let submitted_at: String  // datetime 只展示 → String
    // …
}

enum OutingsAPI {
    @MainActor static func create(_ body: OutingCreateBody) async throws -> OutingOut {
        try await APIClient.shared.post(path: "/api/v1/outings", body: body)
    }
    @MainActor static func listMine() async throws -> [OutingOut] {
        try await APIClient.shared.get(path: "/api/v1/outings/mine")
    }
    // PATCH 无 body：
    @MainActor static func withdraw(id: UUID) async throws -> OutingOut {
        try await APIClient.shared.request(
            method: "PATCH",
            path: "/api/v1/outings/\(id.uuidString.lowercased())/withdraw",
            body: nil as String?
        )
    }
}
```

### 3.2 AppStore 状态 + 拉取函数（`Foundation/AppState/AppStore.swift`）
每个数据源加一个 `@Published var xxx` + 一个 `loadXxx() async`，**带令牌守卫**（登出 / 切用户不写回旧用户数据）+ 失败静默。真样板（`loadMyPackages`）：
```swift
@Published var packages: [FrontDeskItemBrief] = []

@MainActor
func loadMyPackages() async {
    let tokenAtStart = authToken
    do {
        let items: [FrontDeskItemBrief] = try await APIClient.shared.get(path: "/api/v1/front-desk/mine")
        guard authToken == tokenAtStart else { return }   // await 后确认还是同一登录
        packages = items
    } catch {
        // 拉失败不阻塞其他源，静默，下次再试
    }
}
```

### 3.3 界面双分支（计算属性 + Display 视图模型 + `.task`）
**金标准样板**（`MyPackagesView`，照抄结构）：
```swift
struct MyPackagesView: View {
    @EnvironmentObject var app: AppStore

    /// 演示=SEED 假数据 / 生产=后端真数据，靠 #if DEMO 守卫，两边归一成同一个 Display 型
    private var rows: [PackageDisplay] {
        #if DEMO
            return SEED.packages.map(PackageDisplay.init(demo:))
        #else
            return app.packages.map(PackageDisplay.init(brief:))
        #endif
    }

    var body: some View {
        // …用 rows 渲染，跟原来一模一样的布局…
        .task {
            #if !DEMO
                await app.loadMyPackages()
            #endif
        }
    }
}
```
要点：**用一个 `Display` 视图模型（两个 init：`init(demo:)` 接 SEED 型 / `init(brief:)` 或 `init(real:)` 接后端型）把演示与生产两种数据归一**，UI 渲染只认 Display。这样 demo 的日语状态值（如 "通過"）和后端英语枚举（如 "passed"）在 init 里各自翻译成同一套展示字段，UI 一份代码。

### 3.4 提交按钮 + 自己 UUID
- 提交（saveAndLog / 投稿 / 申请）：真样板 `saveAndLog` 用 `app.showToast("保存しました")` + `router.back()`。改成：`#if DEMO` 维持现有假 toast；`#else` 包 `Task { try await XxxAPI.create(...); app.showToast(...); router.back() }`，`catch` 里 `app.showToast(错误信息)`（422 的日语提示由 `APIError.unprocessable` 带出）。
- **自己的学生 UUID**（功能 2 不需要，功能 7/8 需要）：`StudentMeOut.id` 是 `String`（UUID 字符串），`loadMe()` 里已经有 `me` 对象。在 `AppStore` 加 `@Published var myStudentId: String?`，在 `loadMe()` 成功分支补一行 `myStudentId = me.id`（登出 `didSet` 里随 `currentUser = nil` 一起清 `myStudentId = nil`）。功能 7/8 的拉取用它拼 `GET /students/\(myStudentId)/profile`。

---

## 4. 8 个界面逐个（文件 · symbol · 当前数据源 · 后端 · 映射）

> SEED 假数据模型定义全在 `Foundation/Seed/SeedModels.swift`，下面已附字段。

### ① 扫除历史 — `Features/MyPage/MyPageStubs.swift` · `struct MyCleanView`（~1606）
- 当前：`ForEach(SEED.cleaning)` 渲染。`CleaningRecord{date, range, status("通過"|"退回"), score:Int?, rejected:Bool, comment:String?}`
- 后端：§2.1 `GET /cleaning/me` → `[CleaningAssignmentOut]`
- 映射（Display 双 init）：`range←area` / `date←scheduled_date` / 状态显示 `passed→通過`、`failed→退回`、`done→提出済`、`assigned→未提出`、`skipped→免除` / `rejected ← (status=="failed")` / `comment ← failure_reason`。后端没有分数 → 生产版 Pill 只显状态文字（不显「· N点」）。
- 新建 `CleaningAPI.swift`；`AppStore` 加 `@Published var cleaningHistory: [CleaningAssignmentOut]` + `loadCleaningHistory()`；`MyCleanView` 改计算属性 rows + `.task`。

### ② 个人信息修改 — `Features/MyPage/MyPageStubs.swift` · `struct MyInfoEditView` 的 `saveAndLog()`（~895）
- 当前：只改 `app.currentUser` + `SEED.user` + 假 toast。
- 后端：§2.2 `PATCH /students/me`。
- 做法：在 `AuthAPI.swift` 的 `enum StudentsAPI` 里加 `updateMe(_ body:)`（仿同文件的 `me()`），请求体 `StudentSelfUpdateBody{email:String?, phone:String?, avatar_url:String?, room_no:String?}`（全 Optional，**只填用户实际改了的字段**），响应解码复用 `StudentMeOut`。`saveAndLog`：`#if DEMO` 保持现状；`#else` 包 `Task`，调 `updateMe`，成功后用现成的 `mapMeToUser`（私有 → 可让 `updateMe` 后直接复用 `loadMe` 思路，或在 saveAndLog 里把返回的 `StudentMeOut` 字段写回 `currentUser`/`SEED.user`）+ `showToast` + `back`；`catch APIError.unprocessable(let m)` → `showToast(m)`（撞 email / 房号格式错的日语提示）。

### ③ 体调 / 欠席 / 其他 — `Features/Home/HomeStubs.swift` · `HealthSheet`（~1949）/ `AbsenceSheet`（~2040）/ `OtherSheet`（~2085）
- 当前：提交假 toast。三个是**提交表单**，不读 SEED 列表。
- 后端：§2.3 `POST /rollcall/reports`，`kind` 分别 `health` / `absence` / `other`。
- 做法：新建 `RollCallReportsAPI.swift`（或加进现有 `RollCallAPI.swift`）：`create(kind:body:sessionId:)`。三个 sheet 的提交：`#if DEMO` 假 toast / `#else` 把各 sheet 收集的文本拼成 `body`（你读三个 sheet 看它们各收集啥字段）、`kind` 各对应、`session_id` 传当前点呼 session（`AppStore` 里若有当前 session 就带，没有传 `nil`）。

### ④ 点歌 — `Features/Community/CommunityStubs.swift` · `MusicView`（~795）/ `MusicNewView`（~925）/ `MusicDetailView`（~1022）
- 当前：`SEED.songs.sorted{ $0.id > $1.id }`。`SongItem{id:Int, title, artist, by, up:Int, down:Int}`
- 后端：§2.4。`SongRequestOut` 无 `by`/`up`/`down`（投票 v1.1）→ 列表 / 详情只显 `song_title` / `artist` / `note`，投票 UI 在生产版隐藏或去掉（演示版保留）。
- 映射：real `id` 是 UUID、demo `id` 是 Int → Display 用 `String` 归一 id。`MusicView` rows 双分支 + `.task` 拉 `GET /songs`；`MusicNewView` 提交 `POST /songs`；`MusicDetailView` 按 id 查。

### ⑤ 遗失物 — `Features/Community/CommunityStubs.swift` · `LostView`（~499）/ `LostNewView`（~633）/ `LostDetailView`（~716）
- 当前：`SEED.lost{id:Int, title, place, date, color(hex)}`，`LostView` 有搜索过滤 `filteredLost`（IX-030 修复，**必须保留**搜索逻辑）。
- 后端：§2.5。
- 映射：`title←item_name` / `place←location` / `date←created_at`（格式化展示）。`color` 是演示版专属装饰，生产版可给固定色。生产版对 `app.lostFound` 套同样的搜索过滤。
- `LostNewView` 看表单当前有没有区分 found/lost，没有就加个选择（默认 `found`）。`LostDetailView` 加「解决」按钮（仅本人，调 `PATCH /{id}/resolve`）。
- 新建 `LostFoundAPI.swift`；`AppStore` 加 `@Published var lostFound: [LostFoundOut]` + `loadLostFound()`。

### ⑥ 修繕 / 来訪 / 代理 — `Features/Apply/ApplyStubs.swift` · `GenericApplyForm`（~1564）+ `ApplyPreviewView`（~1932）
- 当前：这三类申请走 `GenericApplyForm`，提交假 toast。`ApplyPreviewView` 是提交前确认页。
- 后端：§2.6，`kind` 分别 `repair` / `guest` / `proxy_receipt`。
- 做法：新建 `MiscRequestsAPI.swift`；读 `GenericApplyForm` 看它怎么区分这三类 kind、收集 `subject`/`detail`/`target_date`；只接这三类，**别动 `GenericApplyForm` 处理的其他 kind**（不在本任务范围）。提交 `#else` → `POST /misc-requests`。

### ⑦ 点呼历史 — `Features/MyPage/MyPageStubs.swift` · `MyRollcallView`（~927）/ `MyRollcallDetailView`（~1051）
- 当前：`SEED.rollcall{date, session, state("時間内"|"遅刻"|"欠席"), method("NFC"|"―")}`；RootView 按 id 从 `SEED.rollcall` 查记录传给 detail。
- 后端：§2.7 `rollcall_events[]`。
- 映射：`date←checked_in_at`（取 yyyy-MM-dd）/ `session←session_type`（`morning→朝点呼` / `evening→晩点呼`）/ `state←base_status`（`present→時間内` / `late→遅刻` / `absent→欠席` / `exempt_range→免除`）/ `method←status_source`（`auto_nfc→NFC`，其余→`―`）。
- 拉取：见 §3.4 自己 UUID。详情页 RootView 传 id 的查表逻辑改成从 `app` 缓存查。

### ⑧ 减点明细 — `Features/MyPage/MyPageStubs.swift` · `MyPointsView`（~1176）/ `MyPointsChartView`（~1362）
- 当前：`SEED.points{date, session, kind("遅刻"|"欠席"), val:Double}` 明细 + `SEED.user.points`(4.5) 合计。
- 后端：§2.7 `demerit_events[]`。「今月合計」用 `app.displayUser.points`（已是 `DisciplineAPI.mySummary` 真数据，生产版**已对，不用改**）。
- 映射：明细行 `date←created_at` / `val←points` / 标签 `←reason`（或 `source_type`）。图表 `MyPointsChartView` 数据同源。
- **功能 ⑦⑧ 共用一个 profile 接口** → 合成一个 `loadMyProfile()`：一次 `GET /students/{id}/profile` 同时填 `@Published var myRollcallEvents` + `@Published var myDemeritEvents` 两块。

---

## 5. 文件清单

**新建**（放 `Foundation/Network/Endpoints/` 下，`project.yml` sources 是目录 glob，`xcodegen` 后自动进工程）：
- `CleaningAPI.swift`（功能①）
- `RollCallReportsAPI.swift`（功能③）
- `SongsAPI.swift`（功能④）
- `LostFoundAPI.swift`（功能⑤）
- `MiscRequestsAPI.swift`（功能⑥）
- `StudentProfileAPI.swift`（功能⑦⑧：`StudentProfileOut` + 嵌套 `rollcall_events` / `demerit_events` 模型 + `profile(id:limit:)`）

**改**：
- `Foundation/Network/Endpoints/AuthAPI.swift`（功能②：`StudentsAPI.updateMe` + `StudentSelfUpdateBody`）
- `Foundation/AppState/AppStore.swift`（各 `@Published` 状态 + `loadXxx()` + `loadMe()` 补 `myStudentId = me.id` + 登出清 `myStudentId`）
- `Features/MyPage/MyPageStubs.swift`（功能①②⑦⑧）
- `Features/Home/HomeStubs.swift`（功能③）
- `Features/Community/CommunityStubs.swift`（功能④⑤）
- `Features/Apply/ApplyStubs.swift`（功能⑥）

> `project.yml` 不用改（目录 glob 自动收新文件），跑一次 `xcodegen generate` 即可。

---

## 6. 工程操作 + 验证（必做，自己跑真编译，别只凭「我改对了」）

```bash
cd 03_dev/student_ios/v1
xcodegen generate
# 正式版（走 #else 真后端）
xcodebuild -scheme TomoshibiApp     -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build
# 演示版（走 #if DEMO 假数据）
xcodebuild -scheme TomoshibiAppDemo -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build
```
- 两个 scheme 都要看到 `** BUILD SUCCEEDED **`。
- 可**全部改完再一次** `xcodegen` + 双 scheme 编译（省时间），有编译错再逐个修。

---

## 7. 红线

- demo 假数据 `#if DEMO` 守卫**保留**，别删。
- 代码注释 **100% 中文**；UI 字符串保持**日语**；注释里引用日语 UI 词用「」。
- **不动 Android**。
- iOS 字段以 §2 为准（跟后端 `schemas.py` 对齐），别自己编字段名。
- 点歌的**通报 / 封禁 / 投票不做**（v1.1）。
- commit 用**显式 pathspec 列文件名**（zsh 不拆未引用变量），commit 前 `git diff --cached` 核对，别卷入别会话改动。`git add` 别用 `-A`。
- 改 Swift / Python 加 `import` 必须**同一次**带上用到它的代码（ruff / 编译器会把「加了没用」的当问题）。
- **不要 `git push`、不要打 tag**（itsuki 明确才做）。commit 不写 `Co-Authored-By`。

---

## 8. 完成定义

8 类界面的生产版（`#else`）接真后端、演示版（`#if DEMO`）仍跑假数据；正式版 + 演示版**双 scheme `BUILD SUCCEEDED`**；按功能逐个 commit（未 push）。
