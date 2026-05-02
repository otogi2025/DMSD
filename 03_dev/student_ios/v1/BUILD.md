# Tomoshibi iOS v1 — Build 双版本说明

源码 1 份，**编译 2 个版本**：

| 版本 | 用途 | 含 demo hack | 数据来源 |
|---|---|---|---|
| **Production**（默认） | 真上线给学生用 | ❌ 无 | 接 backend 后由真数据驱动；接通前用 SEED.user 等 fixture 占位 |
| **Demo**（含 `DEMO` flag） | 发给老师 / Claude Design / AC 演示 | ✅ 有 | SEED + amber Card 长按循环 + Push trigger 4 button + LoginView magic password 等 |

差异通过 Swift `#if DEMO ... #endif` 编译时切换 — production binary 完全不含 demo 代码（反编译也看不到）。

## 命令行 build

### Production（默认无 DEMO flag）

```bash
cd ~/dev/DMSD/03_dev/student_ios/v1
xcodebuild \
  -project TomoshibiApp.xcodeproj \
  -scheme TomoshibiApp \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  build
```

### Demo（加 DEMO flag）

```bash
cd ~/dev/DMSD/03_dev/student_ios/v1
xcodebuild \
  -project TomoshibiApp.xcodeproj \
  -scheme TomoshibiApp \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  SWIFT_ACTIVE_COMPILATION_CONDITIONS="DEBUG DEMO" \
  build
```

关键参数：`SWIFT_ACTIVE_COMPILATION_CONDITIONS="DEBUG DEMO"` — Xcode 默认 Debug build 自带 `DEBUG` flag，所以这里要把 `DEBUG` 也写进去保持原行为，再额外加 `DEMO`。

## Xcode GUI 操作（推荐做法）

为了在 Xcode 里直接切换版本，建议 itsuki 配置一次：

### 方案 A — 加 Build Configuration

1. Xcode → 选 project（顶部蓝图标）→ Info tab → Configurations
2. 点 ＋ → Duplicate "Debug" Configuration → 改名为 `Demo`
3. 选 TomoshibiApp target → Build Settings tab → 搜「Active Compilation Conditions」
4. 找到 `Demo` 那列 → 设置为 `DEBUG DEMO`
5. Product → Scheme → Manage Schemes → 复制 TomoshibiApp scheme → 改名 `TomoshibiAppDemo` → Edit → Run → Build Configuration 选 `Demo`

之后顶部 scheme 切换器选「TomoshibiApp」= production，选「TomoshibiAppDemo」= demo。

### 方案 B — 让两版能并存装在 Simulator 上

如果想同时看到两个版本（不互相覆盖），在 Demo configuration 改：
- `PRODUCT_BUNDLE_IDENTIFIER` = `com.itsuki.tomoshibi.demo`（production = `com.itsuki.tomoshibi`）
- `PRODUCT_NAME` = `Tomoshibi Demo`（production = `Tomoshibi`）

这样 Simulator 上会有「Tomoshibi」+「Tomoshibi Demo」两个 icon。

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
| `Foundation/Theme/TTokens.swift` | `AppVersionTag.full`（demo = `v1.0.0-demo` / production = `v1.0.0-rc`） |

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
