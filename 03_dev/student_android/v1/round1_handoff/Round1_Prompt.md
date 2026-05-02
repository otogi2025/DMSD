# Tomoshibi Android v1 — Round 1 Prompt（給 Claude Design）

> ## ⚠️ 最重要的约束 — 一开始就读
>
> **直接用 Kotlin + Jetpack Compose 写**。
>
> **禁止用 HTML / CSS / JS / React / Flutter / KMM / 任何中间语言**。最终产物要在 Android Studio 里直接打开能编译，跑在 Android 真机或 emulator 上。
>
> 不出 HTML mockup、不出 Figma 链接、**直接 .kt 文件 + Compose Preview**。Phase A 的 3 variations 也是 Compose Preview screenshot 而不是 HTML。

> **任务**：把已经做好的 iOS 完整版（Swift / SwiftUI）**1:1 复刻**到 Android（Kotlin / Jetpack Compose），目标 = 学生用 Android 手机能跑同样的功能 + 同样的设计语言。

## 你（Claude Design）要做什么

输出一个**可直接打开的 Android Studio 工程**（目录结构 + Gradle 文件 + 全 Kotlin 源码 + Compose UI），跑出来的 demo 和 iOS 完整版**功能等价 + 视觉等价**。Phase A 先出 3 variations 让 itsuki 选风格细节，Phase B 一次出 30+ Activity / Composable 全画面。

## 项目背景（重要）

**Tomoshibi**（灯火 / ともしび）是日本宿舍点呼数字化系统。学生用手机 NFC 签到，老师 iPad 实时看出席。这是 itsuki（中国留日高中生）申请筑波大学 AC 入試的核心叙事项目。

- **iOS 已完成**：31 个 .swift / 12 大 Feature 模块 / Production + Demo 双版本
- **Backend 已起手**：FastAPI / SQLAlchemy / SendGrid 邮件 / 出寮届 chain 承认
- **现在开工 Android**：Kotlin + Compose Material 3，复刻 iOS demo 版（含演示 hack 让老师看效果）

## 平台映射

| iOS（已完成） | Android（你要做） |
|---|---|
| Swift 6.0 | Kotlin 2.0+ |
| SwiftUI | Jetpack Compose |
| `@StateObject AppStore` | `viewModel<AppStore>()` (Hilt or Koin) |
| `@EnvironmentObject` | `CompositionLocal` 或 ViewModel 注入 |
| `@Published` | `MutableStateFlow` / `mutableStateOf` |
| iOS 26 Liquid Glass `.glassEffect()` | Material 3 `Surface` + 半透明 + `BlurTransform` |
| Core NFC | `android.nfc.NfcAdapter` (NDEF) |
| APNs push | FCM (Firebase Cloud Messaging) |
| `TabView` / 自製 BottomNav | `NavigationBar` + `NavHost` |
| `.sheet` | `ModalBottomSheet` |
| SF Symbols | Material Icons + 自定义 vector |
| 日本語 ja_JP | 同 |

iOS 的 Liquid Glass morph 在 Android 用 `Material 3` `Surface` + 半透明 capsule + `AnimatedContent` / `Crossfade` 模拟即可。Material You 风格保留，但**调色 / 字体 token 对齐 iOS**（见 `Design_Tokens.md`）。

## 双版本机制（必做）

iOS 用 `#if DEMO` 编译时切换 production / demo。Android 用 **Build Variant**：
- `productFlavors { production { ... } demo { ... } }`
- `BuildConfig.DEMO_BUILD: Boolean` 在 Kotlin 用 `if (BuildConfig.DEMO_BUILD) { ... }` 圈 demo 代码
- 两个 flavor 不同 `applicationId`（`com.itsuki.tomoshibi` / `com.itsuki.tomoshibi.demo`）+ 不同 app name 让两版能并存装 Android 手机

## 功能范围（**全部** 必做 — 不许砍）

### §1 認証 / 起動

- Splash（炎 logo 动画）
- Onboarding 3 页轮播（タッチで点呼 / 申請も簡単 / 灯火を絶やさない）
- 注册 5 step：基本情报（含留学生 chip）→ 点呼区分（一般 / サッカー部）→ 連絡先 → パスワード → Done
- Login（番号モード / メールモード 2 tab + 密码 + lockout 升级 30s→1m→5m→30m→1h→永久）
- LockoutView（动态阶段 + 倒计时 + 「次回失敗で N」提示）
- PwResetView（"寮監に连络" placeholder）

### §2 Home

- Greeting + bell badge（unread）
- Amber Card 三态:
  - 平时 = 扣分点数 + progress bar + 月度遅刻/欠席统计
  - 点呼中 = 倒计时 + 欠席申請 / 体調報告 双 button
  - 学習 mode = 学習迟到倒计时 + 請假 button → 切到 active 显示 NFC 3 dot 进度
- LifeTab 6 cards: バス / 宅配 / 今週の活動 / リクエスト曲 / 遺失物 / 匿名建議

### §3 Sheets（关键 — 中央点呼按钮 + Feedback 入口）

- **RollcallSheet** 4 态: idle（NFC 待机 + pulse 动画）→ scanning（0.5s spinner）→ success（绿勾 + 时刻）→ fail（红 ✗ + 重试）
- **StudyCheckinSheet** 4 态（同上风格 + 显示 N/3 学習開始のタップ + 受付時間窗口）
- **FeedbackSheet** 3 选 1（体調 / 欠席 / その他）
- **HealthSheet**（症状 chip + 体温 + 補足）
- **AbsenceSheet**（理由）
- **OtherSheet**（分類 + 内容）
- **SongReportSheet**（リクエスト曲投诉 4 理由 + 自由文）
- **LogoutSheet**（确认）

### §4 申し込み（出寮届 + 7 类申请）

- ApplyListView 一覧 + filter（すべて / 審査中 / 承認済 / 下書き）
- ApplyNewView 8 grid (帰省 / 外泊 / 帰国 / 学習欠席 / その他 等)
- StayForm（**出寮届 = 帰省 / 外泊 / 帰国 三种 kind 字段累积**）
  - 帰省: 出寮日 / 帰省方法 / 出寮時刻 / 帰寮日 / 帰寮方法 / 帰寮時刻 / 理由
  - 外泊: 帰省字段 + 外泊地点（多个）+ 食事不要期間（开始 / 結束）
  - 帰国: 外泊字段 + 出発空港 / 出発時刻 / 到着空港 / 到着時刻
- StudyAbsenceForm（範囲 select 前半 / 後半 / 両方 + 理由）
- GenericApplyForm（其他 4 种轻量表单）
- ApplyPreview / ApplyDone

### §5 申請履歴 + 修改届（system_features §7.2.4-5）

- StayListView（一覧 + filter + chain dot row 摘要）
- StayDetailView（詳細 + 承認の流れ timeline + 履歴 tab segmented）
  - 承認の流れ = 5 役职竖向 timeline（圈 + 状态 pill + 担当者名 + 决定时刻 + 评论）
  - chain rule: 一般外泊 = 担任 + 寮務課長 + 管理係（3 行）/ 留学生 = 担任 + 国際交流部長 + 寮務課長 + 寮務部長 + 管理係（5 行）
  - **修改届ボタン**: status ∈ {pending, returned} 时显示「修改届を提出」
  - 提交后承認の流れ全员重置回 pending + auditLog append
- StayEditForm（身份字段 read-only + 出寮日 / 帰寮日 / 移动方法 chip / 宿泊先 / **修改の理由**必填）

### §6 マイページ（10+ 子画面）

- MyLanding 9 grid blocks（個人情報 / 点呼履歴 / 減点明細 / 処分履歴 / 体調報告履歴 / 申請履歴 / 掃除提出履歴 / 荷物受取履歴 / 学習履歴 仅 isStudyTarget）+ 下部設定 list
- MyInfo（学号/姓名 read-only + 寮 / 部屋 / 区分 / メール / 電話 + 変更履歴 timeline）
- MyInfoEditView（**spec §6**: 学号/姓名 read-only 锁、邮箱/电话/房间号可改）
- MyRollcall（月度 filter + group by 日期 + state pill）
- MyRollcallDetail（kv pair grid + ℹ 改判 banner）
- MyPoints（amber 总和 card + progress 0/4/8 阈值 + 列表 + 规则注解）
- MyPointsChart（12 ヶ月 Canvas 折线图 + threshold dashed 线）
- MyDiscipline（空状态「処分歴はまだありません」+ ✨ emoji）
- MyHealth（体调记录列表 + 症状 + 体温 + 备注）
- MyClean（掃除提出 + 通过/退回 pill + 退回理由）
- MyPackages（宅配 + 状態 pill）
- **MyStudy**（system_features §7.3.10 — isStudyTarget 限定）:
  - 今月 stats（出席 / 遅刻 / 異常 3 box）
  - 当月学習欠席届 計数（>3 显示「超過」红 pill）
  - 出席タップ 履歴 group by 日付（3 件揃 = 「時間内」绿 / <3 = 「未完」红）
  - help info box
- MySettings（5 通知 toggle + ダークモード + **demo 版底部 push trigger 4 button**）
- MyAbout（Tomoshibi wordmark + 灯火 + 版本号 + AC 叙事段）

### §7 Community（Home 子页）

- NotificationsView（filter pills + group by 类型 + dot 未读）
- PackagesView（待領 / 領済 segmented）+ PackageDetail
- LostView（投稿 + filter）+ LostNew + LostDetail
- **MusicView**（system_features §7.11 — 2026-05-01 拍板）:
  - **投稿順排序**（不是赞踩 ranking）
  - hint banner「気になる曲があれば、通報ボタンから先生にお伝えできます。」
  - row 上有「⚠ 通報」button → 弹 SongReportSheet
- MusicNewView（投稿表单 + **封禁中显示红色 banner**）
- MusicDetailView（**砍赞踩** → 「この曲を通報する」big button）
- WallView + WallNew + WallDetail（寮ウォール — 现存功能保留）
- EventsView + EventDetail（活動 list / calendar segmented）
- BusView（バス時刻表 日別 group）
- SuggestView + SuggestFeedView（匿名建議 + 回応一覧）

### §8 V1 リファレンス系

- ScheduleView（行事予定 月历 任意月对应 + 日选 + 多 dot）
- BusListView（特別運航便 + BusKind filter tab + 空港 only switch + 日别 group）

### §9 サービス・状態管理

复刻 iOS `AppStore.kt` 的 ViewModel：
- `rollState` / `studyState` / `studyTaps` / `studyAttendance` / `nextStudyTap`
- `recordCheckin()` / `recordStudyTap()` / `submitStudyLeave()`
- `loginFailCount` / `lockoutDurations` / `recordLoginFailure()` / `resetLoginFailures()`
- `songReportCounts` / `songBanLevel` / `reportSong()` / `canPostSong`
- `pushNotifications` / `handleIncomingPush()` / `unreadNotificationCount`
- `changeLog` + `appendChange()`
- `#if DEMO` 包裹 demo: `cycleDemoRollState` / `cycleDemoStudyState` / 4 个 `simulateXxx` push trigger / amber Card 长按手势
- demo 版预填: changeLog "高2→高3" seed / studyHistory 6 件 demoSeed / studyLeaveCountThisMonth = 3 / Login default acc=00 email=otogi2025 pw=demo1234

### §10 Routing

复刻 `Route.swift` 的 sealed class（Kotlin 用 sealed class + `NavHost`）— 32 + cases。所有 case 名 / displayName 1:1 对应。

### §11 SheetKind

复刻 `SheetKind` 8 种 sheet（rollcall / feedback / health / absence / other / logout / studyCheckin / songReport(songId)）— Kotlin 也用 sealed class。

## 设计语言

- **主题名**: 涼 Suzu
- **主色**: `#1f6b74` teal dark
- 颜色 / 字体 / spacing tokens 全清单 → 见 `Design_Tokens.md`
- 视觉风格: iOS 26 Liquid Glass + 涼しい和風（細い hair line / 薄い影 / 大きなラジアス）
- Android 用 Material 3 但调色 + 字体 + 圆角对齐 iOS（不是 default Material You）

## 资料文件

- `Design_Tokens.md` — 颜色 / 字体 / 圆角 / 间距 / 阴影
- `iOS_Inventory.md` — 31 .swift 文件清单 + 数据模型 + 路由全列表 + AppStore state shape
- `iOS_source_pack/` — 28 个关键 .swift 文件（参考实装）
- `spec_excerpts/system_features.md` — 共用规则全文（账号 / 出寮届 / 学習 / 投诉 / 通知 / 数据模型）
- `spec_excerpts/IOS_DESIGN_LOG.md` — iOS 設計決策（多步注册 / 锁定升级 / 等）
- `screenshots/` — 关键页面 iOS 截图（itsuki 自己截）

## 输出格式

### Phase A（先出）

不出全部 Activity，先做 **3 个 variations** 给 itsuki 选风格细节:
- Variation 1: Material 3 默认（标准 Material You 风）
- Variation 2: 强对齐 iOS（圆角 18 / 細 hair / 薄影 / Material 3 配色 但忽略 Material You dynamic color）
- Variation 3: Material Expressive（Android 16 新风格 + 大胆字号 + 强动画）

每 variation 出 5 关键页 Compose 代码 + Preview 截图：
1. Login
2. Home（amber Card + LifeTab）
3. Apply New（8 grid）
4. StayDetail（chain timeline）
5. MyPage Landing（9 grid）

itsuki 选定后 → Phase B 一次出全部 30+ Composable。

### Phase B（itsuki 选定 variation 后）

完整 Android Studio 工程：
- 目录: `app/src/main/java/com/itsuki/tomoshibi/`（features / foundation / ui）
- `build.gradle.kts`（kotlin 2.0+ / compose 1.7+ / Material 3 / 双 productFlavor / Hilt）
- `app/src/main/AndroidManifest.xml`
- 全 Composable 实装（splash / onboarding / register x 5 / login / lockout / pwreset / home / sheets x 8 / apply x 6 / staylist x 3 / mypage x 13 / community x 13 / schedule / buslist）
- ViewModel（AppStore.kt）+ Repository stub（接 backend 前 mock）
- Demo flavor 含演示 hack（cycle gesture / push trigger / SEED 数据）
- Production flavor 砍 hack
- README.md 含 build + run + 切 flavor 步骤

## 严格约束

0. **直接写 Kotlin + Jetpack Compose**（顶部约束已强调）— 不许 HTML / 不许 React / 不许任何 web 框架中转。最终 deliverable = Android Studio 打开能 build 的 .kt 项目
1. **不砍功能** — 所有 §1-§8 内容必做。如果某 spec 不清楚，记到「Open Questions」让 itsuki 答，不擅自简化
2. **文案 1:1** — 日本語文案逐字照抄 iOS（看 .swift 文件里的字串），不翻译不润色
3. **数据模型对齐** — 18 个 struct（User / ApplicationItem / RollcallEntry / NotificationItem / SongItem / etc）字段名 / 类型 / 含义和 iOS 一致
4. **Route 命名 1:1** — 32 个 case 名一字不差（home / homeNotifications / homePackages / apply / applyNew / applyForm(kind) / my / myInfo / myInfoEdit / stayList / stayDetail(id) / stayEdit(id) / schedule / busList / etc）
5. **demo 版预填值对齐** — Login acc/email/pw 默认值 / studyLeaveCountThisMonth=3 / changeLog seed 等都对齐 iOS demo 版
6. **代码注释用中文**（itsuki 中文 native，看代码用中文容易）
7. **build 工具链固定**：Gradle + Kotlin DSL（`build.gradle.kts`）+ Android Gradle Plugin 8.x+ / Kotlin 2.0+ / Compose Compiler 1.7+ / Material 3 1.3+ / minSdk 24 (Android 7.0) / targetSdk 35 (Android 15) — 不许换成 KMM / Compose Multiplatform / 其他实验工具链

## Open Questions（无清晰答案的让 itsuki 决）

如果做的过程中遇到 iOS spec 不明的，记到一个 `Round1_OpenQuestions.md` 文件，问 itsuki 后再继续。例: NFC 真扫描 vs Mock / 退出注册流程的物理回退手势 / 双版 build 怎么打两个 .apk 的 keystore。

## 起手

**Phase A 起手 = 5 关键页 × 3 variations = 15 个 Composable + 15 个 Preview 截图**。

每个 variation 输出格式 = 真实 .kt 文件代码 + 其下方的 `@Preview` Composable 函数 + 渲染出来的 Preview screenshot 图片（**不是 HTML mockup，不是 Figma**）。

itsuki 看到 3 variations 的 Compose Preview → 选定一个 → 你出 Phase B 全工程。

### Phase A 输出结构示例

```
phaseA/
├── variation1_material3/
│   ├── LoginScreen.kt        ← @Composable + @Preview
│   ├── HomeScreen.kt
│   ├── ApplyNewScreen.kt
│   ├── StayDetailScreen.kt
│   ├── MyPageLandingScreen.kt
│   └── previews/             ← 5 张 Preview 渲染 PNG
├── variation2_ios_aligned/
│   └── ...
└── variation3_material_expressive/
    └── ...
```

---

**重要补充**：iOS 截图见 `screenshots/` 文件夹（itsuki 自己截 15-20 张关键页面给你参考视觉效果）。如果某些页面没有截图，参考 .swift 源码 + spec 描述自己脑补 — Material 3 风格优先合理 + 不能违反 spec。
