# Tomoshibi 设计 Tokens（Android Compose 实装时直接 1:1 用）

> 直接从 iOS `Foundation/Theme/TTokens.swift` 抽出。Android Compose 用 `MaterialTheme.colorScheme` extension + `androidx.compose.ui.graphics.Color`。

## 主题名 / 主色

- 主题名: **涼 Suzu**
- 主色: `#1f6b74` (teal dark)

## Color Tokens

| 名 | Hex | 用途 |
|---|---|---|
| `primary` | `#1f6b74` | teal dark — 主色 |
| `primaryDk` | `#0e3840` | teal 极深 — wordmark / 强调 |
| `primarySoft` | `#7fb0b6` | teal 中淡 |
| `accent` | `#7eb1b8` | accent — 装饰 / chart |
| `accentSoft` | `#bcd9dc` | accent 淡 |
| `paper` | `#ffffff` | card / sheet 背景 |
| `pearl` | `#eff2f3` | 页面背景 |
| `ink` | `#0f1e22` | 主要文字 |
| `inkSub` | `#465d62` | 次要文字 |
| `inkMute` | `#6b8086` | 注释 / 时间戳 |
| `inkFaint` | `#a3b2b6` | 占位 / disabled |
| `hair` | `#d6dee0` | 0.5pt border line |
| `hairSoft` | `#eaf0f1` | 极淡 line / divider |
| `pill` | `#e8eef0` | 标签 chip 浅底 |
| `pillFg` | `#3d5a60` | pill 文字 |
| `warn` | `#d99f3e` | amber 警告 |
| `warnDeep` | `#5c3410` | 警告深棕（amber Card 文字色）|
| `warnBg` | `#fdf4e1` | 警告浅底 |
| `ok` | `#4a9478` | 绿 — 通过 / 时间内 |
| `okDeep` | `#2c6048` | 绿深 — pill 文字 |
| `okBg` | `#e3f1ea` | 绿浅底 |
| `danger` | `#c44848` | 红 — 危险 / 缺席 / rejected |
| `dangerBg` | `#fbe8e6` | 红浅底 |

### Color 渐变（关键）

- **rollBtnGrad** (中央点呼按钮 / NFC button): radial / linear `[#7eb1b8 → #1f6b74]`
- **amber Card**（扣分卡）`linear-gradient(topLeading → bottomTrailing)`:
  ```
  stop 0:    #ffefc2
  stop 0.55: #f4c677
  stop 1:    #d99f3e
  ```
- **amber Card 欠席态**（红渐变）:
  ```
  stop 0:    #ffd6d0
  stop 0.55: #ef6a58
  stop 1:    #c83b29
  ```
- **MyPoints chart bar**: `[#f4c677 → warn]`
- **MusicView 紫 icon bg**: `[#a78bfa → #7c3aed]`
- **success circle**: `[#8bc6a3 → #4a9478]`
- **fail circle**: `[#e88a80 → #c44848]`

## Typography

iOS 用 SF Pro，Android 用 **Roboto**（Material 3 默认）+ **Noto Sans JP**（日本語）。

字号映射（iOS pt = Android sp）:

| iOS 用途 | size | weight | letterSpacing |
|---|---|---|---|
| Header 17 | 17pt | 700 | — |
| Section title 12 | 12pt | 700 (kerning 1.2) | 1.2 |
| Body 14 | 14pt | 400 | — |
| Body bold 14 | 14pt | 700 | — |
| Sub 12.5 | 12.5pt | 400 | — |
| Caption 11 | 11pt | 400 | — |
| Caption mono 11 | 11pt | 700 monospaced | — |
| Hero number 56 | 56pt | 800 monospaced | -1.12 |
| Hero label 11 | 11pt | 700 | 1.98 (uppercase) |
| Wordmark 28-40 | 28-40pt | 800 | 0.04em |

数字 / 时刻 / 学号 / 减点全用 **monospaced**（Android 用 `JetBrains Mono` 或 Roboto Mono）。

## Radius

| token | px | 用途 |
|---|---|---|
| `Radius.xs` | 8 | small chip |
| `Radius.sm` | 12 | input field / pill |
| `Radius.md` | 14 | dialog / sheet |
| `Radius.lg` | 18 | Card（HomeCard）|
| `Radius.xl` | 22 | amber Card / 大 hero |
| `Capsule` | (height/2) | 标签 pill / button |

## Spacing

| token | px |
|---|---|
| 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32, 40 |

iOS 默认 padding: Card pad=14 / Section gap=18 / Page horizontal=20

## Shadow

```
soft:  color(ink, 0.04), radius 2,  y 1
big:   color(ink, 0.05), radius 14, y 4
amber: color(#d4a547, 0.24), radius 20, y 6
glow:  color(primary, 0.32), radius 18, y 6  (按钮 hover/active)
```

## Liquid Glass → Material 3

iOS 26 `.glassEffect(.regular, in: capsule)` 在 Android 不存在。映射:

- BottomNav glass capsule → `Surface(shape = CircleShape, color = paper.copy(alpha=0.78), shadowElevation = 6.dp)` + 半透明 + blur
- amber Card 半透明白覆盖层（active glass）→ `Box.background(primary.copy(alpha=0.12), CapsuleShape)` + 用 `AnimatedContent` / `Crossfade` 实现 morph
- Sheet 背景模糊 → `BackdropFilter` (Compose 1.7+) 或 `Modifier.blur(...)`
- Liquid Glass shimmer 效果 — 不强求，用 Material 3 standard 即可

## Icon Set

- iOS 用 SF Symbols + 自定义 Path
- Android 用 **Material Icons** (`androidx.compose.material.icons.filled.*` / `outlined.*`)
- 罕见 icon（house.lodge / iphone.radiowaves / shield.checkered）→ 自定义 `ImageVector`

| iOS | Android Material |
|---|---|
| `house.fill` | `Home` |
| `house.lodge` | `Cabin` 或自定义 |
| `airplane` | `Flight` |
| `envelope.fill` | `Email` |
| `person.fill` | `Person` |
| `bell` | `Notifications` |
| `shippingbox` | `Inventory2` |
| `music.note` | `MusicNote` |
| `bus` | `DirectionsBus` |
| `calendar` | `CalendarMonth` |
| `iphone.radiowaves.left.and.right` | 自定义 ImageVector |
| `shield.checkered` | `Shield` (filled) |
| `bubble.left` | `ChatBubble` |
| `lock` | `Lock` |
| `flag` | `Flag` |

## Dark Mode

iOS 已实装 `@AppStorage isDark`。Android 跟系统切（`isSystemInDarkTheme()` + `MaterialTheme.colorScheme`），保留用户在 MySettings 强制覆盖的开关。
