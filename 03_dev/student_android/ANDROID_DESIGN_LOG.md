# Tomoshibi 学生 Android App · 设计决策完整归档

> **作用**：Android 端実装方针 / Compose 翻译规则 / 22 屏 route registry / Phase 计划。同 iOS 侧 `student_ios/IOS_DESIGN_LOG.md` 等价档。
> **建立**：2026-05-02 by [Mac-mini]
> **路线**：CC 主导，从 Claude Design 出的 standalone HTML 蓝图（22 屏全接通可交互 React App）**逐屏对译** Kotlin + Jetpack Compose。**不**派 sub agent / 不走 Claude Design 二次出工程。
>
> ⚠️ **单 repo 模式**（2026-05-06 退役独立 repo）：Android 代码直接在 `03_dev/student_android/v1/`，跟 backend / iOS / Web 全在 DMSD 单 repo 里。

## ⚠️ 实装进度速查表（2026-05-21 A-029 加）

| 层 | 进度 | 说明 |
|---|---|---|
| 设计文档（本文） | ✅ 100% | 253 行设计，含 22 屏 route registry |
| Compose UI | 🟡 部分 | 10+ 屏已对译；Auth / Application / RollCall 主 flow 可走 |
| HTTP client | ⏳ 0% | **无 Retrofit / Ktor / OkHttp** — 全本地 mock（A-016 待主会话拍板）|
| 字段对齐 backend | ⏳ 0% | `Models.kt` 全 camelCase 跟 backend snake_case 完全脱节（A-016） |
| amber Card 三态 demo | 🟡 待删 | long-press cycleDemoRollState 残留（A-034 已修） |

---

## 1. 时间线

| 时刻 | 事件 |
|---|---|
| 2026-05-02 14:00 | itsuki 拍板 v1.0 直接 iOS + Android 双端上线（不分阶段）|
| 2026-05-02 16:55 | itsuki 给 Claude Design standalone HTML 路径，提议"逐屏对译 + CC 主导，不派 sub agent" |
| 2026-05-02 17:08 | 路线变更确认 — 归档原 `student_android/v1/round1_handoff/`（Claude Design handoff 路线已废，见 `99_archive/2026-05-02_android_handoff_route_archived/`）|
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
| 依赖注入 | 暂不引入 Hilt/Koin | v1.0 屏幕数 22 屏，手动 DI 够用 |
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
│   └── screens/                 ← 22 屏 1:1 对应 React 组件
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
│       ├── community/FeedbackScreen.kt
│       ├── community/BusScreen.kt
│       └── community/DeliveryScreen.kt
├── data/
│   ├── store/AppStore.kt        ← DataStore wrapper, replaces React StoreProvider
│   ├── model/                   ← Application / Notification / Deduction / etc data classes
│   └── seed/MockData.kt         ← 对应 React tokens.jsx DATA + app-shell.jsx DEFAULT_STATE
└── nav/
    ├── Routes.kt                ← sealed class Route — 23 个 route case (1 splash + 22 screens)
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

## 4. 22 屏 Route Registry

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
| 20 | FeedbackScreen | Route.Feedback | community | P4 |
| 21 | BusScreen | Route.Bus | community | P4 |
| 22 | DeliveryScreen | Route.Delivery | community | P4 |

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

- [ ] 字体 license 确认（Noto Sans JP — Apache 2.0，OK 可商用 / 可 bundle）
- [ ] applicationId 是否最终 `jp.tomoshibi.android`（vs `jp.tomoshibi.tomoshibi` / `dev.tomoshibi.android` 等）
- [ ] keystore 创建 + 密码管理流程（参照 CLAUDE.md "本地 Mac + 后端服务器加密 + 纸质密码 + 年度校验"）
- [ ] Android 真机调试 — 当前 emulator 不支持 NFC，最终需要 1 台 Android 真机（itsuki 决策时再讨论）
- [ ] FCM Sender ID + Server Key（接 backend 时填）

---

## 9. 单 repo 同步

⚠️ **2026-05-06 退役独立 repo** — Android 代码直接在 `03_dev/student_android/v1/`，跟 backend / iOS / Web 全在 DMSD 单 repo 里。原跨 repo 同步规则（`bin/sync-android-refs.sh` / 跨 repo 物理 copy 等）已废 — 2026-05-21 C-012 清理。

**TODO**: 写 `bin/sync-android-refs.sh`（P0 后期或 P1 初期建立）。

---

**END** — 本档随实装进展持续更新。
