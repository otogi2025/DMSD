# Tomoshibi iOS v1 — Build 双版本说明

源码 1 份，**编译 2 个版本**：

| 版本 | 用途 | 含 demo hack | 数据来源 |
|---|---|---|---|
| **Production**（默认） | 真上线给学生用 | ❌ 无 | 接 backend 后由真数据驱动；接通前用 SEED.user 等 fixture 占位 |
| **Demo**（含 `DEMO` flag） | 发给老师 / Claude Design / AC 演示 | ✅ 有 | SEED + amber Card 长按循环 + Push trigger 4 button + LoginView magic password 等 |

差异通过 Swift `#if DEMO ... #endif` 编译时切换 — production binary 完全不含 demo 代码（反编译也看不到）。

两个版本各有自己的 **scheme**，已在 `project.yml` 里定义好：`TomoshibiApp` = 生产；`TomoshibiAppDemo` = 演示（run config = Demo，自带 `DEMO` flag）。**不要再手动加 `SWIFT_ACTIVE_COMPILATION_CONDITIONS` —— 直接选对应 scheme 即可。**

## 命令行 build

### Production（scheme `TomoshibiApp`）

```bash
cd dev/student_ios/v1
xcodebuild \
  -project TomoshibiApp.xcodeproj \
  -scheme TomoshibiApp \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  build
```

### Demo（scheme `TomoshibiAppDemo`）

```bash
cd dev/student_ios/v1
xcodebuild \
  -project TomoshibiApp.xcodeproj \
  -scheme TomoshibiAppDemo \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  build
```

`TomoshibiAppDemo` scheme 的 run config = Demo、已经带上 `DEMO` flag，命令行无需再传 `SWIFT_ACTIVE_COMPILATION_CONDITIONS`。

## Xcode GUI 操作

顶部 scheme 切换器直接选：

- **TomoshibiApp** = production（无 demo 代码）
- **TomoshibiAppDemo** = demo（含 SEED + demo hack）

两个 scheme 都已在 `project.yml` 定义（xcodegen 生成工程时自动建好），不需要再手动建 Build Configuration 或 scheme。

> ⚠️ 在 Xcode 里手动改的工程配置（新建 config / scheme / build setting / bundle id）必须写回 `project.yml`，否则 xcodegen 重新生成 pbxproj 时会被擦掉。两版能否并存装在 Simulator（各自 bundle id / product name）也由 `project.yml` 的 Demo config 决定。

## 验证 demo 代码确实被排除

Production binary 应该不含「Demo · 」字样：

```bash
xcodebuild -project TomoshibiApp.xcodeproj -scheme TomoshibiApp \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -derivedDataPath ./build-prod build

# 检查 binary 里没有 "Demo · " 字符串
strings build-prod/Build/Products/Debug-iphonesimulator/TomoshibiApp.app/TomoshibiApp \
  | grep -i "demo" | head
```

如果 production 走出 `Demo ·` 前缀字样 → 说明有处 #if DEMO 漏圈、按 grep 结果定位修。

## 已圈进 #if DEMO 的代码清单

| 位置 | 内容 |
|---|---|
| `Foundation/AppState/AppStore.swift` | `cycleDemoRollState()` / `cycleDemoStudyState()` / 4 个 `simulateXxx()` push trigger / `changeLog "高2→高3"` seed / `studyHistory.demoSeed` / `studyLeaveCountThisMonth` 初值 3 |
| `Features/Home/HomeStubs.swift` | `DemoCardCycleGesture` modifier（amber Card 长按循环 5 态状态） |
| `Features/MyPage/MyPageStubs.swift` | `pushDemoSection` + `pushDemoRow`（MySettings 底部「⚠️ Push 通知 デモ」section） |
| `Features/Auth/AuthStubs.swift` | LoginView default `acc / email / pw` 预填 / RegisterStep4 default `pw / pw2` 预填 / `tryLogin()` 严格判定（demo magic `00 / demo1234`） |
| `Foundation/Theme/TTokens.swift` | `AppVersionTag.full` —— 从 `Bundle.main` 的 `CFBundleShortVersionString`（见 `project.yml` 的 `CFBundleShortVersionString`）动态读取，**不写死版本号**；demo 版自动加 `-demo` 后缀 |

## 待接 backend 的 stub 标记

代码中 `TODO[backend]:` 注释指明哪里需要换成真 API：
- `recordCheckin()` → `POST /checkins`
- `submit()` (StayForm) → `POST /applications`
- `submitStudyLeave()` → `POST /study/leave`
- `recordStudyTap()` → `POST /study/checkins`
- `reportSong()` → `POST /songs/:id/reports`
- `recordLoginFailure()` / `tryLogin()` → `POST /sessions`
- `handleIncomingPush()` → APNs delegate 接进来调

接 backend 时 grep `TODO\[backend\]` 拉清单。
