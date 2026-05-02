# iOS 实装 Inventory（给 Claude Design 当索引）

> 31 个 .swift 源文件 + 全 Route + 全数据模型摘要。详细看 `iOS_source_pack/` 文件夹。

## 文件结构

```
TomoshibiApp/
├── TomoshibiApp.swift            ← @main entry
├── Foundation/
│   ├── AppState/
│   │   ├── AppStore.swift        ← @MainActor ObservableObject ⭐ 核心
│   │   └── SheetKind.swift       ← enum SheetKind（8 种 sheet）
│   ├── Components/               ← 共通 UI 原子（Card / Field / TField / Pill / etc）
│   │   ├── BottomNav.swift       ← 底部 nav（3 button + 中央点呼）+ Liquid Glass morph
│   │   ├── BreadcrumbOverlay.swift
│   │   ├── Field.swift / PrimaryButton.swift / Toast.swift / TopRollBar.swift / etc
│   │   └── Icons/Ic.swift        ← icon library
│   ├── LiquidGlass/              ← GlassBackdrop / GlassCard / GlassSheet
│   ├── Routing/
│   │   ├── Route.swift           ← enum Route（32+ cases）⭐
│   │   └── RouterStore.swift     ← stack-based router
│   ├── Seed/
│   │   ├── SEED.swift            ← demo fixture data
│   │   └── SeedModels.swift      ← 18 数据 struct ⭐
│   └── Theme/
│       └── TTokens.swift         ← Design tokens + AppVersionTag
├── Features/
│   ├── Auth/AuthStubs.swift              ← 10 views (Splash / Onboarding / Register x 5 / Login / Lockout / PwReset)
│   ├── Home/HomeStubs.swift              ← Home + LifeTab + RollcallSheet + StudyCheckinSheet + Feedback/Health/Absence/OtherSheet
│   ├── Apply/ApplyStubs.swift            ← ApplyList + ApplyNew + StayForm + StudyAbsenceForm + GenericApplyForm + ApplyPreview/Done/Detail
│   ├── StayList/StayListStubs.swift      ← StayList + StayDetail + 履歴 tab + StayEditForm（修改届）
│   ├── MyPage/MyPageStubs.swift          ← MyLanding + 12 子画面 + MyStudy + LogoutSheet
│   ├── Community/CommunityStubs.swift    ← Notifications + Packages + Lost + Music + SongReportSheet + Wall + Events + Bus + Suggest
│   ├── Schedule/ScheduleStubs.swift      ← 行事予定 月历
│   └── BusList/BusListStubs.swift        ← 特別運航便 一覧
└── Root/
    ├── RootView.swift            ← Switch over Route + safeAreaInset 挂 TopRollBar / BottomNav
    └── GlobalOverlays.swift      ← Sheet dispatch + Breadcrumb + Toast
```

## Route 全列表（32 cases — 一字不差对齐 Android sealed class）

```swift
enum Route: Hashable {
    // §0 認証 / 起動
    case splash, onboarding
    case registerStep1, registerStep2, registerStep3, registerStep4, registerDone
    case login, lockout, pwreset

    // §1 Home
    case home

    // §1.4 Home 子页 Community
    case homeNotifications, homePackages, homePackageDetail(id: Int)
    case homeLost, homeLostNew, homeLostDetail(id: Int)
    case homeMusic, homeMusicNew, homeMusicDetail(id: Int)
    case homeWall, homeWallNew, homeWallDetail(id: Int)
    case homeEvents, homeEventDetail(id: Int)
    case homeBus, homeSuggest, homeSuggestFeed

    // §2 申し込み
    case apply, applyNew, applyForm(kind: String), applyPreview(kind: String)
    case applyDone(kind: String), applyDetail(id: String)

    // §3 マイページ
    case my, myInfo, myInfoEdit
    case myRollcall, myRollcallDetail
    case myPoints, myPointsChart
    case myDiscipline, myHealth, myClean, myPackages
    case mySettings, myAbout, myStudy

    // §4 V1 リファレンス系
    case stayList, stayDetail(id: String), stayEdit(id: String)
    case schedule, busList
}
```

每个 case 有 `displayName: String` (Breadcrumb 用) + `isTabRoot` / `isApplyBranch` / `isMyBranch` / `hidesBottomNav` / `hidesTopBar`。

## SheetKind 全列表（8 + 1 associated）

```swift
enum SheetKind: Hashable {
    case rollcall                   // NFC 点呼 sheet（4 态）
    case feedback                   // 3 选 1（健康 / 欠席 / その他）
    case health                     // 体調報告 form
    case absence                    // 当回欠席 form
    case other                      // その他問題 form
    case logout                     // 注销确认
    case studyCheckin               // 学習 NFC 3 次碰 sheet
    case songReport(songId: Int)    // リクエスト曲 投诉 sheet
}
```

## 18 Data Models（SeedModels.swift）

```swift
struct User { account, name, nameKana, birth, age, gender, dorm, room,
               category, email, phone, avatar, points, lateCount, absentCount,
               grade, classSuffix, seatNo, isStudyTarget, isOverseas }

struct PointRecord { date, session, kind, val }
struct RollcallEntry { date, session, state, method }
struct HealthRecord { date, sym, temp, note }
struct CleaningRecord { date, range, status, score, rejected, comment }
struct PackageItem { id, date, from, status, tracking }
struct NotificationItem { id, type, title, time, body, unread }
struct ApplicationItem { id, type, status, date, summary }
struct BusLine { time, route, seats, next }
struct BusDaySchedule { date, weekday, label, notice, lines }
struct EventItem { date, time, title, place, desc }
struct LostItem { id, title, place, date, color }
struct SongItem { id, title, artist, by, up, down }    // up/down 字段保留但 5-01 后不再展示
struct WallPost { id, author, time, text, likes, comments }
struct SuggestItem { id, q, a, date }
struct ChangeLogEntry { id, at, field, label, before, after }
struct StudyHistoryEntry { id, date, tapKind, tapLabel, timeHM, note }
struct AuditLogEntry { id, at, action, actor, detail }
struct StayApplication { id, kind, status, leaveDate, returnDate, summary,
                         destination, leaveMethod, returnMethod, chain, submittedAt, auditLog }
struct ApprovalStep { role, approverName, decision, decidedAt, comment }
```

## AppStore（核心 ObservableObject）— 关键 @Published

```swift
// 点呼
@Published var rollState: RollState = .idle
@Published var rollCountdownSec: Int = 180
@Published var checkinAt: String?
@Published var checkinKind: String?

// 学習
@Published var studyState: StudyState = .idle
@Published var studyCountdownSec: Int = 600
@Published var studyLeaveCountThisMonth: Int    // demo seed=3 / production=0
@Published var studyTaps: Set<StudyTap> = []
@Published var studyHistory: [StudyHistoryEntry]    // demo seed 6 件 / production []

// リクエスト曲
@Published var songReportCounts: [Int: Int] = [:]
@Published var myReportTotal: Int = 0
@Published var songBanLevel: Int = 0
@Published var songBanUntil: Date?

// 锁定升级
@Published var loginFailCount: Int = 0
static let lockoutDurations: [Int] = [30, 60, 300, 1800, 3600]

// Push 通知
@Published var pushNotifications: [NotificationItem] = []

// 변更履历
@Published var changeLog: [ChangeLogEntry]

// UI state
@Published var sheetOpen: SheetKind?
@Published var breadcrumbOpen: Bool = false
@Published var toast: String?
@AppStorage("isDark") var isDark: Bool = false
```

## 关键方法

```swift
// Toast / Sheet
func showToast(_ text: String)
func openSheet(_ kind: SheetKind) / func closeSheet()

// 点呼
func recordCheckin()           // NFC tap 成功后调（TODO: 接 POST /checkins）
func tickCountdown()
#if DEMO func cycleDemoRollState() #endif    // 长按 amber Card 循环 5 态

// 学習
func recordStudyTap() -> StudyTap?         // NFC 1 回 tap 记录 + 推到 history
func tickStudyCountdown()
func submitStudyLeave(reason:range:)        // 提交 + 月度 >3 提醒文案
#if DEMO func cycleDemoStudyState() #endif

// 投诉
func reportSong(songId:reason:freeText:)    // 5/10/15 自动 escalate ban_level

// 锁定
func recordLoginFailure() / func resetLoginFailures()
var currentLockoutSeconds: Int? / var currentLockoutLabel: String / var nextLockoutLabel: String?

// 通知
func handleIncomingPush(type:title:body:)   // APNs delegate 接进来调（Android 用 FCM service）
var allNotifications / var unreadNotificationCount

// 변更履历
func appendChange(field:label:before:after:)

#if DEMO
func simulateStudyLeaveApproved/Rejected/RosterAdded/AmendmentRebatch    // MySettings 4 push trigger
#endif
```

## 状态枚举

```swift
enum RollState     { idle / active / absent / done }
enum StudyState    { idle / upcoming / active / done }
enum StudyTap      { start / mid / end }
enum StudyAttendance { idle / none / progressing / green / yellow / red / abnormal / excused }
enum StudyLeaveRange { first / second / both }
enum SongReportReason { noisy / taste / lyrics / other }

// StayList
enum ApplicationKind   { stay = "外泊" / holiday = "帰省" / return = "帰国" / other = "その他" }
enum ApplicationStatus { draft / pending / approved / rejected / returned / cancelled }
enum ApprovalRole      { homeroom = "担任" / dormHead = "寮務部長" / dormChief = "寮務課長"
                         / intlHead = "国際交流部長" / intlChief = "国際交流課長" / management = "管理係" }
enum ApprovalDecision  { pending / approved / rejected }
```

## 关键业务规则

### 出寮届 chain（system_features §7.2.2）

```
外泊（一般寮生）= 担任 → 寮務課長 → 管理係                  // 3 行
外泊（留学生）  = 担任 → 国際交流部長 → 寮務課長 → 寮務部長 → 管理係  // 5 行
帰省 / 帰国     = 暫定同 chain（实物表 evidence 待ち）
```

### 修改届（system_features §7.2.4-5）

- 提交条件: status ∈ {pending, returned}
- 提交后: chain 全员 reset to pending + auditLog append + status = pending
- 身份字段（学号 / 姓名 / 留学生 flag / 性別）read-only

### 学習 NFC 3 次碰（system_features §7.3.3-6）

```
19:35-19:40  start tap     — 学習開始
20:40-20:50  mid tap       — 中場確認
21:40-21:50  end tap       — 学習終了

3 揃 = 緑（時間内）
2 揃缺 mid = 異常（老师手动判）
1 揃 = 進行中
0 揃 + done = 缺席
不一致パターン → 異常 標記 → 老师手动判
```

### リクエスト曲 投诉（system_features §7.11.2 — 2026-05-01 拍板）

```
投稿順排序（不是赞踩）
通報理由: うるさい / 曲調 / 歌詞 / その他
累積通報 5 件 → 1 ヶ月 投稿禁止
       10 件 → 3 ヶ月 投稿禁止
       15 件 → 永久 投稿禁止
通報 7 件以上 → 老师 Web「⚠ 通報多数」badge（学生侧不显示）
```

### 锁定升级（CLAUDE.md §App 账号规则）

```
失败 1 → 30 秒
失败 2 → 1 分
失败 3 → 5 分
失败 4 → 30 分
失败 5 → 1 时间
失败 6+ → 永久（寮監解除）
```
