# Tomoshibi 学生 Android App · 设计决策完整归档

> **作用**：Android 端実装方针 / Compose 翻译规则 / 21 屏 route registry / Phase 计划。同 iOS 侧 `student_ios/IOS_DESIGN_LOG.md` 等价档。
> **建立**：2026-05-02 by [Mac-mini]
> **路线**：CC 主导，从 Claude Design 出的 standalone HTML 蓝图（22 屏全接通可交互 React App）**逐屏对译** Kotlin + Jetpack Compose。**不**派 sub agent / 不走 Claude Design 二次出工程。
>
> ⚠️ **单 repo 模式**（2026-05-06 退役独立 repo）：Android 代码直接在 `dev/student_android/v1/`，跟 backend / iOS / Web 全在 DMSD 单 repo 里。

## ⚠️ 实装进度速查表（2026-07-20 对齐马拉松后刷新）

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ 100% | 含 route registry（孤儿页清理后见 §16） |
| Compose UI | ✅ 全屏对齐 iOS 生产版 | 见 §16 对齐马拉松（233 条差距清零） |
| HTTP client | ✅ | `ApiClient`（HttpURLConnection + kotlinx.serialization，{ok,data} 信封 / multipart / 二进制下载 / 加密令牌存储） |
| 字段对齐 backend | ✅ | `@SerialName` snake_case 对齐；端点路径逐条对照 iOS |
| 未接线残留 | ⏳ 3 项等拍板 | FCM 推送注册 / demo 构建变体 / AI要約·头像（Apple Intelligence 专属） |

---

## 1. 时间线

| 时刻 | 事件 |
|---|---|
| 2026-05-02 14:00 | itsuki 拍板 v1.0 直接 iOS + Android 双端上线（不分阶段）|
| 2026-05-02 16:55 | itsuki 给 Claude Design standalone HTML 路径，提议"逐屏对译 + CC 主导，不派 sub agent" |
| 2026-05-02 17:08 | 路线变更确认 — Claude Design handoff 路线已废，原 `round1_handoff/` 目录已归档（不在公开仓库）|
| 2026-05-02 17:14 | itsuki 用 Claude Design "Handoff to Claude Code" 导出完整包（22 屏 React 源码 + iOS 参考材料），CC fetch + 解压到 `/tmp/tomoshibi_handoff/dmsd-android/`（**注意**：临时位置，不在 git）|
| 2026-05-02 17:25 | itsuki 拍板 "一个会话解决所有问题" — CC 校准 scope: 冲到 context 极限或装机闭环跑通为止；目标 framework + 4-6 核心屏，剩余进 backlog |

---

## 2. 技术栈 + 工程结构

### 2.1 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言 | **Kotlin** | Google 官方推荐（2019 起替代 Java），新项目业界 ≈ 100% Kotlin |
| UI 框架 | **Jetpack Compose** | 声明式 UI，跟 SwiftUI 概念一一对应 |
| Material 版本 | **Material 3**（M3）| 当前 Android 官方设计系统（替代 M2）|
| 最低 SDK | **API 26**（Android 8.0, 2017）| Compose 最低支持 21，但 26 起 NfcAdapter 稳定 + 占当前市场 ≈ 96% |
| 编译 SDK | **API 35**（Android 15）| 跟随最新 stable |
| Navigation | **Jetpack Navigation Compose** | 标准做法，支持 deep link / back stack |
| 持久化 | **DataStore (Preferences)** | 替代旧 SharedPreferences，对应 React 的 localStorage |
| 字体 | Noto Sans JP（CJK 渲染必须）| 对应 iOS Hiragino Sans |
| 字体（数字）| Roboto Mono | 对应 iOS SF Mono — 减点 4.5 / 时间 09:20 等 |
| NFC | `android.nfc.NfcAdapter` + ForegroundDispatch | NFC 写在 Activity 而非 Composable，详见 §6 |
| 日期时间 | `kotlinx-datetime` | 跨平台、不依赖 java.time API level |
| 依赖注入 | 暂不引入 Hilt/Koin | v1.0 屏幕数 21 屏，手动 DI 够用 |
| 网络 | Ktor Client | 后端 API 调用（v1.1+，v1.0 mock 数据）|
| JSON | kotlinx.serialization | 标准做法 |

### 2.2 包结构

```
app/src/main/java/jp/tomoshibi/android/
├── MainActivity.kt              ← Activity entry, NFC ForegroundDispatch, setContent { TomoshibiApp() }
├── TomoshibiApp.kt              ← Top-level composable: ThemeProvider + NavHost
├── ui/
│   ├── theme/
│   │   ├── Color.kt             ← Suzu Light/Dark palette (35 色)
│   │   ├── Type.kt              ← Material 3 Typography + Noto Sans JP + Roboto Mono
│   │   ├── Tokens.kt            ← SuzuTokens data class + LocalSuzuTokens CompositionLocal
│   │   └── Theme.kt             ← TomoshibiTheme composable wrap
│   ├── components/              ← 共用 Composable（AmberCard, RollCallButton, BottomTabs, ...）
│   ├── icons/
│   │   └── SuzuIcons.kt         ← 32 个 ImageVector（对应 React tokens.jsx Ic 组件）
│   └── screens/                 ← 21 屏 1:1 对应 React 组件
│       ├── splash/SplashScreen.kt
│       ├── onboarding/OnboardingScreen.kt
│       ├── account/AccountScreen.kt
│       ├── welcome/WelcomeScreen.kt
│       ├── login/LoginScreen.kt
│       ├── home/HomeScreen.kt
│       ├── notifications/NotificationsScreen.kt
│       ├── notifications/NotificationDetailScreen.kt
│       ├── applications/ApplicationsScreen.kt
│       ├── applications/ApplyNewScreen.kt
│       ├── applications/ApplicationDetailScreen.kt
│       ├── nfc/NfcScreen.kt
│       ├── deduction/DeductionScreen.kt
│       ├── rollcall/RollCallScreen.kt
│       ├── mypage/MyPageScreen.kt
│       ├── mypage/SettingsScreen.kt
│       ├── community/MusicScreen.kt
│       ├── community/StudyScreen.kt
│       ├── community/LostFoundScreen.kt
│       ├── community/ScheduleScreen.kt
│       ├── community/BusScreen.kt
│       └── community/DeliveryScreen.kt
├── data/
│   ├── store/AppStore.kt        ← DataStore wrapper, replaces React StoreProvider
│   ├── model/                   ← Application / Notification / Deduction / etc data classes
│   └── seed/MockData.kt         ← 对应 React tokens.jsx DATA + app-shell.jsx DEFAULT_STATE
└── nav/
    ├── Routes.kt                ← sealed class Route — 22 个 route case (1 splash + 21 screens)
    └── NavGraph.kt              ← NavHost composable, 注册所有 route
```

### 2.3 命名规范

| 来源（React） | 目标（Compose） | 例 |
|---|---|---|
| `function HomeScreen()` | `@Composable fun HomeScreen()` | 屏幕 |
| `function AmberCard()` | `@Composable fun AmberCard()` | 共用组件 |
| `function Ic({name})` | `Icon(imageVector = SuzuIcons.Bell, ...)` | iconlibrary |
| `useState()` | `remember { mutableStateOf() }` | 组件级 state |
| `useStore() / Context` | `LocalAppStore.current` (CompositionLocal) | 全局 state |
| `useRouter().push('home')` | `navController.navigate(Route.Home.path)` | 导航 |

### 2.4 包名 + applicationId

- **package**: `jp.tomoshibi.android`
- **applicationId**: `jp.tomoshibi.android`
- 对应 iOS bundle id: `jp.tomoshibi.ios`（iOS repo 是否一致后续核对）

---

## 3. React → Compose 翻译规则速查

| React 概念 | Compose 等价 | 备注 |
|---|---|---|
| `function Cmp({prop1, prop2})` | `@Composable fun Cmp(prop1: T, prop2: T)` | 函数 props |
| `useState(init)` | `remember { mutableStateOf(init) }` | 组件级 |
| `useEffect(fn, [dep])` | `LaunchedEffect(dep) { fn() }` | 副作用 |
| `useMemo(fn, [dep])` | `remember(dep) { fn() }` | 派生值 |
| `useContext(Ctx)` | `LocalCtx.current` | CompositionLocal |
| `<Ctx.Provider value=v>` | `CompositionLocalProvider(LocalCtx provides v)` | provide |
| `<div style={{display:flex,flexDirection:row}}>` | `Row(Modifier...)` | 横排 |
| `<div style={{display:flex,flexDirection:column}}>` | `Column(Modifier...)` | 纵排 |
| `<div style={{...}}>` 裸 | `Box(Modifier...)` | 单子 |
| inline style `{padding:16}` | `Modifier.padding(16.dp)` | 边距 |
| `borderRadius: 12` | `Modifier.clip(RoundedCornerShape(12.dp))` | 圆角 |
| `background: '#xxx'` | `Modifier.background(Color(0xFFxxx))` | 背景 |
| `linear-gradient(135deg, A 0%, B 100%)` | `Brush.linearGradient(listOf(A, B))` | 渐变 |
| `radial-gradient(circle ...)` | `Brush.radialGradient(...)` | 径向渐变 |
| `onClick={fn}` | `Modifier.clickable { fn() }` | 点击 |
| `localStorage.setItem` | `dataStore.edit { it[KEY] = value }` | 持久化 |
| `setTimeout(fn, ms)` | `LaunchedEffect(Unit) { delay(ms); fn() }` | 延迟 |
| `<svg>...<path d="..."/></svg>` | `ImageVector.Builder { addPath(...) }` 或 `Icon(painterResource(R.drawable.xxx))` | icon |
| Animation `@keyframes pulse` | `rememberInfiniteTransition().animateFloat(...)` | 循环动画 |
| `localStorage` 持久化 state | DataStore + ViewModel + StateFlow | 状态 |

---

## 4. 21 屏 Route Registry

来源：`Tomoshibi App.html` line 110-134 SCREENS object。

| # | React 名 | Compose route | 业务流 | 优先级 |
|---|---|---|---|---|
| 0 | SplashScreen | Route.Splash | auth | P1 |
| 1 | OnboardingScreen | Route.Onboarding | auth | P1 |
| 2 | AccountScreen | Route.Account | auth | P1 |
| 3 | WelcomeScreen | Route.Welcome | auth | P1 |
| 4 | LoginScreen | Route.Login | auth | P1 |
| 5 | HomeScreen | Route.Home | core | P1 |
| 6 | NotificationsScreen | Route.Notifications | core | P3 |
| 7 | NotificationDetailScreen | Route.NotifDetail | core | P3 |
| 8 | ApplicationsScreen | Route.Applications | core | P2 |
| 9 | ApplyNewScreen | Route.ApplyNew | core | P2 |
| 10 | ApplicationDetailScreen | Route.AppDetail | core | P2 |
| 11 | NFCScreen | Route.Nfc | core | P1 |
| 12 | DeductionScreen | Route.Deduction | core | P3 |
| 13 | RollCallScreen | Route.RollCall | core | P3 |
| 14 | MyPageScreen | Route.MyPage | core | P2 |
| 15 | SettingsScreen | Route.Settings | core | P3 |
| 16 | MusicScreen | Route.Music | community | P4 |
| 17 | StudyScreen | Route.Study | community | P4 |
| 18 | LostFoundScreen | Route.LostFound | community | P4 |
| 19 | ScheduleScreen | Route.Schedule | community | P4 |
| 20 | BusScreen | Route.Bus | community | P4 |
| 21 | DeliveryScreen | Route.Delivery | community | P4 |

---

## 5. Phase 计划

| Phase | 内容 | 预估 | Commit | 完成判定 |
|---|---|---|---|---|
| **P0**（本会话）| Android Studio 装机 + 工程脚手架 + Theme（Color/Type/Tokens/Theme.kt）+ ANDROID_DESIGN_LOG.md | 2-3 hr | 1-2 commit | emulator run 显示 Suzu pearl 背景空屏 |
| **P1**（本会话或第 2 会话）| App shell（NavGraph + DataStore + AppDevice frame + BottomTabs + Toast）+ auth flow（Splash + Onboarding 3 + Account 4 + Welcome + Login） | 4-5 hr | 2-3 commit | 新用户注册流程 emulator 跑通 |
| **P2** | Home omnibus（amber Card + Community 入口 + 顶部点呼 bar）+ NFC 三态屏 | 3-4 hr | 1-2 commit | 进入 Home 看到完整布局 + NFC 演示动画 |
| **P3** | 申请流（Applications + ApplyNew + Detail）+ Notifications + NotifDetail | 3-4 hr | 1-2 commit | 申请提交 → 列表出现 → 详情查看跑通 |
| **P4** | MyPage + Settings + Deduction + RollCall 历史 | 2-3 hr | 1 commit | 个人页跑通 |
| **P5** | Community 7 屏（Music / Study / LostFound / Schedule / Feedback / Bus / Delivery） | 4-6 hr | 1-2 commit | 社区功能跑通 |
| **P6** | NFC 真实硬件接入（NfcAdapter ForegroundDispatch）+ 后端 API 接入（替换 mock）+ FCM 通知 | TBD | TBD | 接 backend |

**总计预估 18-25 小时实际编码** — v1.0 上线前还要加测试 / 适配 / debug 时间。

---

## 6. 关键 Android 平台特性 vs iOS

### 6.1 NFC

| 项 | iOS | Android |
|---|---|---|
| API | CoreNFC `NFCNDEFReaderSession` | `android.nfc.NfcAdapter` |
| 位置 | 任意 SwiftUI view 触发 | **必须** 在 Activity 用 ForegroundDispatch |
| 后台读取 | 不支持（必须用户主动启动 session）| 支持（NDEF intent filter）|
| 实装策略 | （iOS 已实装）| MainActivity 持有 NfcAdapter，通过 SharedFlow 推 Composable；Composable 用 collectAsState 消费 |

### 6.2 系统返回

| 项 | iOS | Android |
|---|---|---|
| 默认手势 | 屏幕左缘右滑 | 系统手势条 / 软返回键 |
| Compose 处理 | （iOS 自动）| `BackHandler { navController.popBackStack() }` 显式注册 |

### 6.3 状态栏 / 导航栏

| 项 | iOS | Android |
|---|---|---|
| 状态栏色 | UIKit appearance | `WindowCompat.setDecorFitsSystemWindows + WindowInsets` |
| 沉浸式 | safe area | `Modifier.systemBarsPadding()` / `WindowInsets.systemBars` |

### 6.4 字体

iOS 系统自带 Hiragino Sans。Android 必须 bundle Noto Sans JP（约 4MB）到 `res/font/`，否则 Android 默认 Roboto 不渲染日文。

---

## 7. Mock 数据策略

P1-P5 全部用 mock — 来源 `tokens.jsx DATA` + `app-shell.jsx DEFAULT_STATE`。

`data/seed/MockData.kt` 包含：
- 学生用户 リュウイヒ（060218 / 高3B組 18番 / 男寮 M101）
- 5 条 application（外泊审査中 / その他要修正 / 帰省承認済 / 外出承認済 / 早帰承認済）
- 5 条 notification
- 7 条 deduction（4.5 点合计）
- 3 条 musicRequest（Lemon 22 票）
- 3 条 lostFound

P6 接 backend 时换成 Ktor Client + Repository pattern。

---

## 8. 待决清单（不阻塞 P1）

> ⭐ **2026-06-09 itsuki 拍板分发方式：不上 Google Play、不办谷歌开发者账号** —— 改打签名 APK（安卓安装包文件）上传到后端 VPS、学生自己下载安装。**理由：有中国留学生的手机用不了 Google Play**。所以「Google Play 上架 / 商店审核 / 商店隐私表单 / 谷歌账号」全部不需要；但 keystore 仍要（打可安装 APK 必须 release 签名）。
> ⚠️ 连带影响：FCM（谷歌推送）依赖手机装了 Google Play 服务 → **中国留学生手机收不到 FCM 推送**，Android 推送方案 v1.1 要另想。

- [ ] 字体 license 确认（Noto Sans JP — Apache 2.0，OK 可商用 / 可 bundle）
- [ ] applicationId 是否最终 `jp.tomoshibi.android`（APK 自托管不强制商店唯一性，定了好管理）
- [ ] keystore 创建 + 密码管理流程（**APK 自托管仍需 release 签名才能装**；密码管理沿用项目既定方案 — 本地 Mac + 后端服务器加密 + 纸质密码 + 年度校验）
- [ ] **APK 自托管落地**：后端放一个 APK 下载入口（页面/链接）+ 引导用户开「允许安装未知来源」+ 想清版本更新怎么提示用户重下
- [ ] Android 真机调试 — 当前 emulator 不支持 NFC，最终需要 1 台 Android 真机（itsuki 决策时再讨论）
- [ ] ~~FCM Sender ID + Server Key~~ → 见上：FCM 对中国留学生手机不可达，Android 推送 v1.1 另议

---

## 9. 单 repo 同步

⚠️ **2026-05-06 退役独立 repo** — Android 代码直接在 `dev/student_android/v1/`，跟 backend / iOS / Web 全在 DMSD 单 repo 里。原跨 repo 同步规则（跨 repo 物理 copy 等）已废。

## 10. 出租车预约「タクシー予約」— 待 Android 接后端时实装（2026-06-03）

itsuki 2026-06-03 拍板出租车预约功能（4 端）。iOS / 老师网页 / 后端已实装（后端 `applications.taxi_reservation_time`）。

**Android 本次未做**，理由：Android 现在是 Compose 骨架、申请表单（`ApplyNewScreen.kt`）未接后端、本地无法 gradle 编译验证 → 加 `Switch` UI 占位有 import 风险又测不了，价值低于风险。

**待办**：Android 接后端时，`ApplyNewScreen.kt` 出寮届表单**照 iOS 2026-06-04 新交互做**（见 `IOS_DESIGN_LOG.md §14.17`）—— **出寮方法选了「タクシー」就当场露出时刻选择器**，不做独立开关、不为帰寮加预约（后端 `taxi_reservation_time` 只一个字段、只管出寮），提交带 `taxi_reservation_time`、详情页显示，跟 iOS `StayForm` 对齐。

---

## 11. 特別運行便一覧：只显示特別便 + 删通学便筛选 + 運航→運行（2026-06-13，与 iOS 对齐，commit `79f702c`）

itsuki 看 iOS 班车页反馈三点，拍板 iOS + Android + 共用规格全同步。Android `BusListScreen.kt` 照 iOS `BusListView` 同改：

- **只显示寮生特別運行便**：`visible` 过滤改成只留 `kind == "dorm_special"`，平日通学便（`daily_commute`）不再显示（页脚弱字已注明「※ 通常日のスクールバスは別途ご確認ください」= 普通校车另查）。
- **删类型筛选条**：原「すべて」「特別便」「通学便」3 颗 `FilterPill` 胶囊 + `filter` state + `FilterPill` 组件定义 +`clickable` 孤儿 import 全删，只保留「空港送迎便のみ」开关。
- **徽章全称**：`kindLabel()` 的 `dorm_special` 显示从「特別便」→「特別運行便」，`BusRow` 的 Pill tone 比对同步改。
- **汉字 運航→運行**：标题 `PageHeader`、空状态「運行便はありません」、`Routes.kt` / `Models.kt` / `MockData.kt`（含 2 处公告假数据 UI 串）——「運航」专指船 / 飞机、巴士的标准日语是「運行」，itsuki 反馈用的就是「運行」，全项目统一。
- **验证**：`./gradlew assembleDebug` BUILD SUCCESSFUL。
- 共用规格 `system_features.md §7.6.2` 同步更新（只显示特別運行便 / 删类型 filter）。iOS 侧见 `IOS_DESIGN_LOG.md §19`。

## 12. 全量审查修复批：中文漏出→日语 + 晩自習→夜学習 全端对齐 + 死代码清理（2026-06-17，commit `040e8b8`）

本会话全项目审查的 Android 修复（详见 `archive/2026-07-14_admin报告群归档/2026-06-17_全量审查报告.md`）：

- **中文漏进日语 UI**（要上架、扎眼）：`StayEditScreen` / `StayDetailScreen`「修改/身份情報/役职」→「変更/個人情報/役職」，与 iOS `StayListStubs` 对齐；`StayDetailScreen` auditColor `contains("修改")` 同步改「変更」否则履历着色失效。
- **晩自習/晚自习→夜学習 全端对齐**（しおり 官方用词，itsuki 6-16 拍板、iOS+teacher_web 先改、本批 Android 补齐）：用户可见串全改（ApplicationsScreen / MyStudyScreen / MyPageScreen / MySettingsScreen / StudyAbsenceForm / StudyCheckinSheet / Models.kt StudyTap START·END label）；英文 key + MockData.name 不动。
- **对齐**：`ApiClient` Json 补 `explicitNulls = false`；`MyDisciplineSummaryOut` 补 `needs_cleaning`、`BusRouteOut` 补 `purpose`（与后端+iOS 对齐）。
- **bug/死代码**：`ApplyNewScreen` 来訪者/代理受取补必填字段+canSubmit、48時間期限只对有出寮日类型显示、删 `APPLY_KINDS_7`；删孤儿屏 `SettingsScreen`/`community/StudyScreen`（含 NavGraph/Routes）；删 `ApplyKindMapper`；`LoginScreen` 写死 `v0.12.0`→`BuildConfig.VERSION_NAME`。
- **未动（待 itsuki）**：`NfcScreen`/`RollCallSheet` v1.0 不可达双轨；`GenericApplyPreview/Done` 不可达死路径。见 TODO §A 2026-06-17 段。
- **验证**：`./gradlew assembleDebug` BUILD SUCCESSFUL。

## 13. v1.1 候补死代码登记 + C42/C43 学生端实装（2026-06-17）

### 13.1 v1.1 候补死代码登记（itsuki 拍板「留着+登记」，全量审查 C36-39 + Android 代理发现）

> v1.0 用户**进不去**、但 v1.1 真要用的骨架。itsuki 拍板**保留不删**，在此登记以免日后误当 bug / 死代码清理。

- **C36-39 `NfcScreen` / `RollCallSheet` 点呼入口双轨** — v1.0 安卓学生端无点呼入口（点呼在点呼机硬件 + 后端），这套是 v1.1 手机点呼候补的不可达骨架。**有意保留，非 bug**。
- **`GenericApplyPreview` / `Done` 不可达死路径** — `stage="preview"` 当前流程从不设置，预览/完成态走不到。保留作通用申请预览的 v1.1 候补。

### 13.2 C42/C43 出寮届撤回 + 差戻重提 + 行事企画重提（commit `f131ade`）

对接后端新端点（详见 `BACKEND_DESIGN_LOG.md` 2026-06-17 履历），与 iOS 语义对齐：`ApiClient.postNoBody` + `ApplicationsAPI.withdraw` + `DormLifeAPI.resubmitEventProposal`；`StayDetailScreen` 加「取消（撤回）」红按钮 + `returned` 态编辑按钮改「修正して再提出」；`DormEventListScreen` 在 `result=='resubmit'` 显老师评语 + 「再提出」按钮 + 补 `approved_conditional`/`resubmit` 状态徽章。`gradlew assembleDebug` BUILD SUCCESSFUL。注：`StayEditScreen` 重提编辑屏仍是既有 mock（历史 TODO）；行事重提暂用现有内容原样重提（无独立详情屏，与 iOS 一致）。

## 14. C2 测试批：data/ 纯逻辑层新建 + 点呼履历 JST 锁定（2026-07-13，commit `881aa52`）

C 组质量体系 C2 清单 Android #13-20 落地。新建 `data/` 下三个纯逻辑文件（无 Android 依赖、JVM 可单测）：

- `data/rollcall/RollStateMachine.kt` — 点呼时间窗判定，逐行移植 iOS `decideRollState`。⚠️ **尚无 UI 调用点**（Android 点呼屏仍走 mock）——是接真后端批次的预置基线，测试与 iOS 用同一组窗口数值钉双端判定一致，勿当已生效功能。
- `data/account/RoomCoding.kt` — 房号前缀/寮名（从 AccountScreen 等价抽取）+ `validateRoomDormMatch`（对齐后端口径，未接线）。⚠️ **实测查出真双端差异**：房号「A5」iOS 原样保留（IX-014），Android 现行拼成「MA5」双前缀 → 已用测试锁定现状 + TODO 挂等拍板条，本批不擅改注册行为。
- `data/format/JstDate.kt` — 点呼履历时刻格式化，时区从「跟随设备」改锁死 Asia/Tokyo（**本批唯一真实行为变更**，主会话签收：对齐全链路 JST 契约与 iOS，真实用户设备本就 JST 显示不变）。

界面层等价接线：AccountScreen 房号/寮名委托 RoomCoding；ApplicationStatusPill 徽章文案抽 `applicationStatusLabel` 纯函数；RollCallScreen 履历时刻改用 JstDate。`AppStore.appJson` private→internal 供 token 往返测试测真身。测试 6 文件 30 条（含 auto_end 边界回落 IDLE / 多场次顺序无关）。验证：`testDebugUnitTest` 全绿 + `assembleDebug` BUILD SUCCESSFUL。未 push。

---

## 全接口响应信封 {ok,data} 解码接入（2026-07-17，commit `37bfd4b`，派 cursor grok4.5 施工 + 主会话审查复验）

后端所有成功响应改包一层 `{ok:true,data:...}`、失败响应统一 `{ok:false,error:{code,message,detail}}`（详见 `dev/backend/BACKEND_DESIGN_LOG.md` 同日条 + 契约真值 `specs/API_CONVENTIONS.md` §1）。Android 侧只改 `data/network/ApiClient.kt`：

- `decode<T>` 先按 `ApiEnvelope<T>{ok,data}` 解外壳，`envelope.ok` 为假时抛 `ApiError.Decode`（不该走到这——成功状态码走这条路径），否则取 `envelope.data as T`。
- `extractDetail`（对齐 iOS `DetailError`）加第 1 优先形态 `error.message`，旧形态 `detail` 字符串/对象仍兼容。

验证：`./gradlew assembleDebug` BUILD SUCCESSFUL（主会话独立重新编译核对，非仅信自报；实际路径 `dev/student_android/v1/`，非施工提示词写的 `dev/student_android/`，按现状改）。无已知 latent。

## 15. 邮箱登录接通（2026-07-19，与 iOS / 后端对齐）

后端 `POST /api/v1/sessions/student` 已支持 `student_no` / `email` 二选一；iOS 同日恢复「メール」tab 并接通。Android 侧：

- `AuthAPI`：拆成 `StudentLoginByNumberRequest` / `StudentLoginByEmailRequest` 两个独立请求体（避免编出 `null` 字段），新增 `loginStudentByEmail`。
- `LoginScreen`：删掉邮箱 tab 死按钮早退；按 tab 调对应 API；邮箱 trim、密码不 trim；401 文案按 tab 分开；debug magic creds 仅番号 tab。
- 注册 Step3 联络先 hint 改为「このメールアドレスはログインにも使えます。確認用のメールは送信されません」（对齐 iOS）。

验证：`./gradlew assembleDebug` BUILD SUCCESSFUL。

---

## 16. Android↔iOS 1:1 对齐马拉松（2026-07-19~20，14 工单 + 对账 + 三方对抗审查，共 17 commit）

目标：Android 全面对齐 iOS 生产版（功能 / 页面 / 设计 / 日语文案逐字）。流程：14 切片差距盘点（233 条）→ 14 个串行工单派 cursor-agent（grok-4.5-high-fast）实装、主会话逐批独立验证（`--rerun-tasks` 强制重跑 + 文案端点色值对照 iOS）→ 覆盖对账（234 条逐条核对）→ 三方对抗审查（Opus 4.8 / Grok 4.5 / Fable 5 四轮跑到收敛）。

### 16.1 工单批次（B01-B14，各一 commit）

| 批 | commit | 内容 |
|---|---|---|
| B01 | 74e0c52 | 网络层扩建：9 端点封装 / EncryptedSharedPreferences 加密令牌存储（读旧→写新→删旧迁移）/ 生产域名 DEBUG 分流 / multipart 上传 + 二进制下载 / ApiErrorPresenter |
| B02 | 1df492e | 会话链路：loadMe 级联（me→扣分→欠席数→未読→通知→今日点呼→罚扫，全程令牌竞态守卫）/ 401 统一清会话 / 令牌过期追踪 |
| B03 | 2b5b793 | 设计系统：GlassSheet / SuzuToast / 底部导航胶囊动画 / 面包屑长按 / 触觉反馈 / 骨架屏 / 双层阴影 / Noto Sans JP（Google Fonts 运行时下载）/ 路由参数类型修正 |
| B04 | 1c2016b | 登录注册：注册接真后端 / 房号字母前缀模型（M/A/W 定寮）/ 锁定页删除（iOS 生产 401 只 toast）/ 介绍页 4 页 / Splash 重做 |
| B05 | bfcb36b | 主页：扣分卡 4 态 / 公告卡接线 / 学年更新横幅接 renew-number / 五卡 + 宅配接真数据 / amber 三段渐变 |
| B06 | a19696b | 通知中心三源聚合（push+feed+包裹）+ markRead + 7 筛选 chip；公告翻訳：ML Kit 端上翻译 4 语言 + 记忆偏好 + 設定页语言区 |
| B07 | e59dd0a | 点呼全链路：ST25DVWriter 真 NFC 邮箱写入（34 字节载荷对齐 Device_Contract §7，帧手拼厂商码标「待硬件联调核实」）/ 场次 ticker 状态机 / 欠席・体調・其他上报接真后端 |
| B08 | 9e2b3bf | 申请中心：五类申请真提交 / 一览合并外出（`outing:` 前缀分流）/ 撤回 / 変更届 / 全屏新規选种页 / withdrawn 独立态 |
| B09 | d448f44 | 申请表单群：行事企画・冷蔵庫・物品所持・夜学習欠席・オンライン夜学習接真后端 / 契約書拍照相册 PDF 上传 / 差戻再提出可编辑 / 完成页统一 |
| B10 | dac7cf3 | 外泊帰省帰国 + 外出：StayForm 真提交 / 操作履歴 audit / stay_locations / 差し戻し文案统一 / 下拉刷新 |
| B11 | 80a91af | 社区：遺失物三屏（本人 resolve）/ 点歌三屏 / 宅配（删自助确认）/ 行事详情 UUID / 路由 Int→String |
| B12 | 034089c | マイページ：真资料 / 罰則清掃履歴新屏 / 体調履歴 / 変更履歴 / 账号删除 DELETE /accounts/me / 減点折线阈值虚线 / 夜学習卡 4 态 / 删重复减点屏 |
| B13 | 84859f0 | 行事月历任意月 + 校车：JST 今天 / 空月历持续显示 / 空港 banner 逐字 / 分组头 purpose |
| B14 | 0f11752 | 清尾：删 6 孤儿页（旧 NFC 模拟 / 旧点呼履历 / 旧巴士 / 旧日历×2 / 夜学習签到弹层）/ MockData 无引用假数据清理 / JstDate 统一 / 日志 gate 进 DEBUG |

### 16.2 覆盖对账（commit 920d20a）

4 个并行只读子代理把 14 份差距报告 234 条逐条到代码核实：228 绿；3 条为拍板区故意不修（FCM / demo 变体 / AI要約·头像）；1 条误报（`CheckinType.STUDY` 无调用点与 iOS 一致）；2 条真偏差当场修复——夜学習屏欠席次数接真值 + 履历对齐 iOS 生产空列表、三表单完成页「一覧へ」统一回申请列表根。

### 16.3 三方对抗审查（commit 6cd33f1）

Opus 4.8（high）/ Grok 4.5（high fast）/ Fable 5 主会话，R1 背对背独立审 → R2 互审裁决真错/误报 → R3 挑修复方案的刺 → 终审，三方零互相误报、终审全票通过。确认并修复 10 项：

1. 申請履歴入口改跳对齐版 StayList；申请一览出寮届行详情改走 StayDetail（差戻横幅 + 詳細/履歴 tab + 操作履歴，对齐 iOS 全部出寮详情走 StayDetailView），外出行留原详情
2. `approved_partial` 独立为 APPROVED_PARTIAL（「一部承認」，绿系配色，「承認済」tab 双状态收）——原折叠进 APPROVED 造成与 StayList 自相矛盾
3. 5 个一覧屏（巴士/行事月历/行事企画/冷蔵庫/物品）401 补清会话
4. 点呼 ticker 无变化不落盘 + 令牌同值不重加密（原每秒 AES-GCM 随机 IV 重存 = 每秒真实写盘；已知残留：ACTIVE 受付窗内倒计时秒变仍落盘，窗口数分钟/天）
5. 冷蔵庫/物品完成页 navigate 补清栈；行事企画再提出预填令牌守卫改请求前捕获；外出拉取软失败不拖垮一览；出寮撤回文案「申請を取り消し」

辩论全过程产物：会话 scratchpad `debate/R1~R3+FINAL` 共 10 份文件（临时目录，不入库）。

### 16.4 遗留（等 itsuki 拍板，勿当漏项重报）

① AI要約/アバター（Apple Intelligence 专属，Android 无对应）② demo 构建变体（iOS #if DEMO 双 scheme 的 Android 等价物）③ FCM 推送设备令牌注册（需 Firebase 项目凭证）④ ML Kit 翻译依赖较重，如嫌重可拍板回退。另：夜学習履歴列表两端都等后端 GET /study/attendance/mine。

### 16.5 审查S3 点呼状态契约收口 + Android 高危（2026-07-21）

与 iOS 逐行对齐（同后端契约：absent/exempt_range 事件带 checked_in_at）。

- **判定层（android#1）**：`RollStateMachine` 已签到分支改 `when(myStatus)` 完整映射（与 iOS `decideRollState` 逐行对应），absent→ABSENT 不显时刻、exempt_range→DONE+「免除」不显假时刻、未知→不兜底時間内。补测 2 例。
- **android#4**：`AccountScreen.FormData` 演示 PII 默认值（リュウイヒ/male/M101/demo1234）改空/中性，仅 `BuildConfig.DEBUG` 注入 `demoFormData()`（对齐 LoginScreen），release 空表单。
- **android#0**：删号假删已在 commit 034089c 修复（真调 `AccountsAPI.deleteMyAccount` + token 世代守卫 + clearSession），本场仅核对。
- **展示层收口（终审 fable 抓阻断 + iOS 对端对齐）**：`RollStatusBar`/`TopRollBar` done 态对齐 iOS（exempt 不显畸形「チェックイン済み・免除」、未知态不兜底時間内、big 中性化「記録あり」）；`RollCallSheet.RollSuccessBody` 生产写卡成功（checkinKind=null）显中性「点呼機に送信しました」（ios#44 Android 对端，Android 已接真 NFC 写卡、非模拟）；`MyRollcallScreen` 详情 statusText default 回显不兜底時間内（ios#58 Android 对端）。fable 复核 PASS。

验证：assembleDebug + testDebugUnitTest BUILD SUCCESSFUL。commit `6ba271a` / `c678a59`。

保留意见（fable 复核，留后续场，勿当漏项重报）：① 履歴详情对「免除」记录仍显「チェックイン <结算时刻>」行（iOS/Android 对称，同屏 Pill 已明示「免除」）② 「今月の減点」pill 的 done 分支硬编码「時間内にチェックイン」是死代码（仅 IDLE 态挂载，done 永不渲染）。

---

**END** — 本档随实装进展持续更新。
