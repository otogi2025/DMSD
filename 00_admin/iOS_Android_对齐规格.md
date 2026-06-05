# iOS ↔ Android 对齐规格

> **目的**：把 **Android 学生 App 做得跟 iOS 学生 App 几乎一模一样**（itsuki 2026-06-05 要求「完全一样」）。本文是给另一个会话的施工蓝图。
>
> **真值来源 = iOS**（Swift/SwiftUI，`03_dev/student_ios/v1/TomoshibiApp/`，已基本完工）。本文每一段都是 agent **读 iOS 真实代码**写出来的，不是凭空设计。
>
> **Android 现状** = 早期演示桩（`03_dev/student_android/v1/`，Kotlin/Compose）：只有 UI 桩 + 本地 `MockData.kt` 假数据，**没有任何网络层**（无 retrofit/okhttp/ktor）。所以「对齐」= 照 iOS 把 Android 补成功能 + 外观一致，并从零写网络层接同一个后端。
>
> **配套截图**：`06_assets/app_screens_2026-06-05_ios/`（14 张 iOS 实机界面图，视觉真值；README 里有每张图对应哪个屏）。
>
> **施工顺序建议**：①设计系统（地基）→ ②导航骨架 → ③网络层（API 契约）→ ④登录注册 → ⑤各功能屏。每段末尾有「### Android 对齐要点」直接说 Android 缺什么、做成什么样。
>
> **UI 文案铁律**：所有界面文字保持**日语原文**（跟 iOS 一字不差），别翻译成中文或英文。

---

## 目录

1. 设计系统 / 主题 / 共享组件
2. 导航 / 路由 / 整体骨架
3. 后端 API 契约 + 数据模型
4. 登录 / 注册 / 账号
5. ホーム 主页
6. 申し込み 申请列表 + 新規申請
7. 各申请表单 + 番号再設定
8. マイページ 个人页
9. 減点明細 + 趋势图
10. バス / 宅配 / リクエスト曲 / カレンダー / 通知
11. 点呼 / NFC 扫描 / 状态条

---

I have everything I need. The Android side has tokens/colors/type ported but lacks a unified shared-component library (no central Card/Pill/PrimaryButton/TField/GlassSheet/PageHeader/FlowLayout module — atoms are scattered/inlined per screen). I have enough to write the design-system alignment section accurately.

## 设计系统 / 主题 / 共享组件（iOS↔Android 对齐）

> 真值来源：iOS `Foundation/Theme/TTokens.swift`（设计令牌枚举 `T`）+ `Foundation/Components/`（共享组件）+ `Foundation/LiquidGlass/`（玻璃组件）。本节是整个 App 的地基 —— 所有屏幕的颜色、字号、圆角、间距、卡片、按钮都从这里取。Android 必须先把这套地基补齐，后面照屏做才能「一模一样」。
>
> 配色代号说明：iOS 主题代号叫「涼 Suzu」，主色 teal（青绿）`#1F6B74`。Android 已经把这套色板 port（移植）进 `ui/theme/Color.kt` + `Tokens.kt`，**色值已对齐，不用重抄**；缺的是「统一共享组件库」—— iOS 把 Card / Pill / 按钮 / 输入框 都收进 `Foundation/Components/`，Android 现在是散在各屏内联、没有中央组件文件。

---

### 1. 色板（每个 `T.xxx` 令牌的语义 + 色值）

iOS 在 `TTokens.swift` 里用 `enum T` 集中定义。色值用 `Color(hex: 0xRRGGBB, alpha:)`（自定义扩展，见文件末尾 `extension Color`）。逐条列（hex 是 6 位十六进制颜色码）：

**主色系（teal 青绿）**

| 令牌 | 色值 | 语义 / 用在哪 |
|---|---|---|
| `T.primary` | `#1F6B74` | 主色 teal dark —— 按钮主色、激活 tab、链接、强调文字 |
| `T.primaryDk` | `#0E3840` | 更深的 teal —— 渐变暗端、深背景 |
| `T.accent` | `#5FBEC8` | 亮 teal —— 按钮渐变亮端、点呼按钮中环 |
| `T.accentSoft` | `#A8DCE2` | 浅 teal —— 渐变最亮端、点呼按钮外缘 halo（光晕） |

**中性 / 表面 / 文字层级**

| 令牌 | 色值 | 语义 |
|---|---|---|
| `T.pearl` | `#EFF2F3` | 米白 —— 整个页面画布背景（pageBg）、输入框填充底 |
| `T.paper` | `白 #FFFFFF` | 卡片表面（card surface）|
| `T.ink` | `#0F1E22` | 主文字（接近黑的深青）|
| `T.inkSub` | `#56707A` | 副文字 / 小标题 |
| `T.inkMute` | `#93A4AC` | 更淡文字 / 图标 / placeholder（占位字）|
| `T.inkFaint` | `#C4D0D5` | 最淡灰 —— 禁用态、分隔 |
| `T.hair` | `#0F1E22` @ 8% 透明 | 发丝线（hairline）分隔线 / 边框 |
| `T.hairSoft` | `#0F1E22` @ 4% 透明 | 更淡分隔 / textarea 底 |

**状态色（3 组：警告 / 危险 / 成功，各带 主色+背景+深色 三层）**

| 令牌 | 色值 | 语义 |
|---|---|---|
| `T.warn` | `#D1984A` | 警告主色（琥珀橙）|
| `T.warnBg` | `#FDF4E1` | 警告背景（浅米黄）—— 点呼倒计时 bar 底 |
| `T.warnDeep` | `#7A4A0E` | 警告深色 —— 警告 bar 上的文字 |
| `T.danger` | `#C44848` | 危险主色（红）—— 删除按钮、必填 `*`、错误文字 |
| `T.dangerBg` | `#FDE8E8` | 危险背景（浅粉红）|
| `T.ok` | `#4A9478` | 成功主色（绿）—— 已签到图标 |
| `T.okBg` | `#E3F1EA` | 成功背景（浅绿）—— 已签到 bar 底 |
| `T.okDeep` | `#2C6048` | 成功深色 —— 成功 bar 上的文字 |

**玻璃层（Liquid Glass 降级用，iOS 26 真玻璃走 `.glassEffect()`）**

| 令牌 | 色值 | 语义 |
|---|---|---|
| `T.glassNav` | 白 @ 68% | 导航玻璃降级底 |
| `T.glassBar` | 白 @ 70% | 顶部点呼 bar 玻璃降级底 |
| `T.glassSheet` | 白 @ 85% | 底部弹层玻璃降级底 |
| `T.glassBackdrop` | `#0F1E22` @ 35% | 弹层背后的暗色遮罩 |

**Pill（胶囊小标签）**

| 令牌 | 色值 | 语义 |
|---|---|---|
| `T.pill` | `#1F6B74` @ 8% | 半透明 teal —— 标签底、头像底、选中 chip 底 |
| `T.pillFg` | = `T.primary` | 标签前景文字色 |

**渐变（`LinearGradient` / `RadialGradient`）**

| 令牌 | 定义 | 用在哪 |
|---|---|---|
| `T.amberGrad` | 线性 `#FFE9B5 → #F4C677`，左上→右下 | Home 减点卡 hero（招牌琥珀卡）|
| `T.redGrad` | 线性 `#FDD7D2 → #E88A80` | 红色 hero 卡 |
| `T.greenGrad` | 线性 `#D2EBDA → #8BC6A3` | 绿色 hero 卡 |
| `T.btnGrad` | 线性 `accent → primary`，左上→右下 | 备用按钮渐变 |
| `T.rollBtnGrad` | 径向 `accentSoft → accent → primary`，圆心 (0.35, 0.28)，半径 0→70 | 底部中央 ⭐点呼大圆按钮 |

---

### 2. 字号 / 字重规范

iOS 没有命名 typography 表，是在每个组件里直接写 `.font(.system(size:weight:))`。下面是从所有共享组件里提取的实际数值（Android 照搬成 sp，1pt ≈ 1sp）：

| 角色 | 字号 | 字重 | 取自哪个组件 |
|---|---|---|---|
| 页面标题（PageHeader） | 17 | bold（粗）| `PageHeader` |
| Section 小标题 | 13 | bold + 全大写 + 字间距 1 | `SectionHeader` |
| 主按钮文字 | 16 | bold + 字间距 0.32 | `PrimaryButton` |
| 次按钮文字 | 15 | medium（中）| `GhostButton` |
| 输入框正文 | 15 | regular | `TField` |
| 表单 label | 13 | semibold（半粗）| `Field` |
| 表单 hint / error | 11 | regular | `Field` |
| Pill 标签 | 11 | semibold | `Pill` |
| Radio 标题 | 15 | semibold | `RadioCard` |
| Radio 副文字 | 12 | regular | `RadioCard` |
| Chip 文字 | 12 | semibold | `ChipGroup` |
| 底部 tab 文字 | 10 | semibold | `BottomNav` |
| 底部 tab 图标 | 20 | medium | `BottomNav` |
| 点呼按钮文字「点呼」 | 9 | bold | `BottomNav` |
| 顶部点呼 bar 主文字 | 12 | semibold | `TopRollBar` |
| 顶部点呼 bar 副文字 | 10 | regular | `TopRollBar` |
| Toast 文字 | 13 | medium | `ToastView` |
| 空状态标题 | 14 | semibold | `EmptyState` |
| 空状态图标 | 40 | —— | `EmptyState` |

**字体家族**：iOS 用 `HiraginoSans-W3`（常规）/ `HiraginoSans-W6`（粗）/ `SFMono-Regular`（等宽数字），定义在 `T.fontName` 等常量，但**实际组件全用系统字体 `.system()`，没真正套 Hiragino**。Android 已在 `Type.kt` 用 `FontFamily.SansSerif` 占位 + `TODO: 接入 Noto Sans JP`，等宽数字用 `RobotoMono`。

---

### 3. 圆角 / 间距约定

iOS 在 `T` 里有两个嵌套枚举：

**圆角 `T.Radius`**（单位 pt）

| 名 | 值 | 用在哪 |
|---|---|---|
| `xs` | 8 | 最小圆角 |
| `sm` | 12 | 输入框 TField / textarea |
| `md` | 16 | 卡片 Card 默认、按钮、RadioCard |
| `lg` | 22 | GlassCard 默认 |
| `pill` | 9999 | 胶囊全圆（Capsule）|

**间距 `T.Space`**（单位 pt）

| 名 | 值 |
|---|---|
| `xs` | 4 |
| `sm` | 8 |
| `md` | 12 |
| `lg` | 16 |
| `xl` | 24 |
| `xxl` | 32 |

（注：组件内部很多 padding 是直接写死数字如 14、20、40，不全走 `T.Space`，照搬具体组件的实测值即可。）

---

### 4. 共享组件逐个（外观 + 用法）

每个组件给：iOS 文件、外观规格、文案、用法。Android 要做成中央组件库（建议 `ui/components/` 下补齐对应文件），各屏不再内联重写。

#### 4.1 `Card`（`Components/UIAtoms.swift`）
白卡片容器。`padding` 默认 14、`radius` 默认 16（`T.Radius.md`）、底 `T.paper` 白、**双层阴影**：① `T.ink` @5%，模糊 14，偏移 y=4；② `T.ink` @4%，模糊 2，偏移 y=1。圆角 style `.continuous`（连续圆角，比普通圆角更顺）。
**用法**：包任意内容当卡片。
**Android 对齐**：`Surface` 或 `Box` + `RoundedCornerShape(16.dp)` + `background(paper)` + 两层 `shadow`（Compose 用 `Modifier.shadow` 叠两次或 `graphicsLayer`）。`.continuous` 在 Compose 无原生等价 → 用普通 `RoundedCornerShape` 即可（视觉差极小）。

#### 4.2 `Pill`（`UIAtoms.swift`）
胶囊小标签。字号 11 semibold，内边距 横 10 / 竖 4，`Capsule` 底。5 个色调 `Tone`：
- `neutral` → 字 `inkSub` / 底 `hair`
- `ok` → 字 `okDeep` / 底 `okBg`
- `warn` → 字 `warnDeep` / 底 `warnBg`
- `danger` → 字 `danger` / 底 `dangerBg`
- `accent` → 字 `primary` / 底 `pill`

**Android 对齐**：`@Composable fun Pill(text, tone)`，用 `Box` + `CircleShape`（高度方向全圆 = Capsule）。`Tone` 做成 enum，`when` 映射 fg/bg。

#### 4.3 `Avatar`（`UIAtoms.swift`）
圆形头文字。默认 44pt 直径，圆底 `T.pill`，中央 1 个字母（字号 = 直径 × 0.44 bold，色 `primary`）。
**Android 对齐**：`Box(Modifier.size(44.dp).clip(CircleShape).background(pill))` + 居中 `Text`。

#### 4.4 `SectionHeader`（`UIAtoms.swift`）
区块小标题。左 title（13 bold，色 `inkSub`，**全大写** + 字间距 1），右可选 `right` 视图，中间 `Spacer` 撑开。
**Android 对齐**：`Row` + `Text(..., letterSpacing=1.sp)` + 手动 `.uppercase()`（Compose 无 textCase，需 `text.uppercase()`）。

#### 4.5 `PrimaryButton`（`Components/PrimaryButton.swift`）
**最重要的主按钮**。高 52、圆角 16、字 16 bold + 字间距 0.32、字色白、宽度撑满。可选前置图标。三态背景：
- 正常 → **径向渐变** `accentSoft → accent → primary`（圆心 0.35/0.28，半径 0→260）+ 阴影 `primary` @24% 模糊 14 y=4
- 禁用（`enabled=false`）→ 纯 `T.inkFaint` 灰、无阴影
- 危险（`destructive=true`）→ 纯 `T.danger` 红、无阴影

**Android 对齐**：`Button` 高 `52.dp`，`Modifier.background(Brush.radialGradient(...))`（已在 `Tokens.kt` 的 `rollGrad` 用过类似径向）。禁用态换灰，危险态换红。注意径向渐变的圆心要按比例。

#### 4.6 `GhostButton`（`PrimaryButton.swift`）
次按钮（描边透明）。高 52、圆角 16、字 15 medium 色 `primary`、底透明、边框 `primary` @30% 线宽 1。
**Android 对齐**：`OutlinedButton` 或 `Box` + `border(1.dp, primary.copy(alpha=.3f))`。

#### 4.7 `Field`（`Components/Field.swift`）
表单字段包裹。竖排间距 7：① label 行（13 semibold 色 `inkSub`，`required=true` 时尾随红 `*`）② 内容 slot ③ error（11 红）或 hint（11 `inkMute`，行距 3）二选一。
**Android 对齐**：`Column(verticalArrangement=spacedBy(7.dp))`，label 用 `Row` 拼 `*`，error/hint 条件渲染。

#### 4.8 `TField`（单行输入，`Field.swift`）
高 48、圆角 12（`T.Radius.sm`）、底 `T.pearl`、字 15 色 `ink`、横内边距 14。边框：**未聚焦 `T.hair` 线宽 1，聚焦时 `T.primary` 线宽 1.5**。支持 `secure`（密码遮蔽）+ `keyboard` 类型。
**Android 对齐**：`BasicTextField` 或 `OutlinedTextField` 自定义 colors，高 `48.dp`，焦点态切边框色 + 加粗。密码用 `PasswordVisualTransformation`，键盘用 `keyboardOptions`。Compose 没现成「焦点变边框」要用 `interactionSource.collectIsFocusedAsState()`。

#### 4.9 `TArea`（多行输入，`Field.swift`）
高 = `rows×22 + 20`（默认 4 行）、内边距 8、底 `T.hairSoft`、圆角 12、边框 `T.hair` 线宽 1。空时左上角显示 placeholder（14 色 `inkMute`，内边距 14，不吃点击）。
**Android 对齐**：`BasicTextField(singleLine=false)` + 手动 placeholder overlay（`Box` + 条件 `Text`）。

#### 4.10 `RadioCard`（`UIAtoms.swift`）
单选大卡。横排：左圆形 radio（22pt 圈，选中 `primary` 描边 + 内 10pt 实心点；未选 `inkFaint` 描边）+ 右竖排（title 15 semibold `ink` + 可选 detail 12 `inkSub`）。整卡内边距 14、圆角 16，**选中底 `T.pill` / 未选底 `T.hairSoft`**。整卡可点。
**Android 对齐**：`Row` in clickable `Box`，左用 `Canvas` 或嵌套 `Box` 画圈+点。

#### 4.11 `ChipGroup` + `FlowLayout`（`Features/Apply/ApplyStubs.swift` + `Features/Home/HomeStubs.swift`）
**横向自动换行的胶囊选择组**（多选项排成一行，放不下自动折到下一行）。每个 chip：字 12 semibold，内边距 横 12 / 竖 7，`Capsule` 底。**选中 → 字白 + 底 `primary` + 边 `primary`；未选 → 字 `ink` + 底 `paper` + 边 `hair`**。chip 间距 6（横 6 竖 6）。
`FlowLayout` 是 iOS 16+ `Layout` 协议实现的流式布局：逐个量子视图宽度，当前行放不下就换行累加行高。
**Android 对齐**：Compose 直接有 **`FlowRow`**（`androidx.compose.foundation.layout.FlowRow`），不用自己实现 `Layout`。chip 用 `FilterChip` 自定义颜色，或 `Box` + `CircleShape` + `clickable`。`horizontalArrangement = Arrangement.spacedBy(6.dp)`、`verticalArrangement = spacedBy(6.dp)`。

#### 4.12 `EmptyState`（`UIAtoms.swift`）
空状态占位。竖排间距 10：图标（40pt 色 `inkMute`，默认 SF symbol `tray`）+ title（14 semibold `inkSub`）+ 可选 message（12 `inkMute` 居中）。整体内边距 40。
**Android 对齐**：`Column` 居中，图标换 Material Icons 或自绘。

#### 4.13 `Skeleton`（`UIAtoms.swift`）
加载骨架条。圆角 6，默认高 14，**横向流光动画**：`LinearGradient(hair → hairSoft → hair)` 起止点左右往返，`easeInOut` 1.4 秒无限循环（不反转）。
**Android 对齐**：`Box` + `Brush.linearGradient` + `rememberInfiniteTransition` 动 offset（或 accompanist shimmer）。

#### 4.14 `TToggle`（`UIAtoms.swift`）
iOS 开关。系统 `.switch` 样式，激活色 `T.primary`，隐藏 label。
**Android 对齐**：`Switch(colors = SwitchDefaults.colors(checkedTrackColor = primary))`。

#### 4.15 `Toast`（`Components/Toast.swift`）
底部浮层提示。字 13 medium 白，内边距 横 18 / 竖 12，`Capsule` 底 `T.ink` @88%，距底 100。`从底部滑入 + 淡入`过渡。
**Android 对齐**：自做 `Snackbar` 或 `AnimatedVisibility` + `Box` 底对齐。

#### 4.16 `PageHeader`（`Components/PageHeader.swift`）—— 导航核心
页面头。横排间距 14：左按钮（`level==1` 显示 home 图标 → 点击回首页；`level>=2` 显示返回箭头 → 点击 `router.back()`，按钮 36×36）+ title（17 bold `ink`）+ `Spacer` + 可选 `right`。整体内边距 横 16 / 竖 12。
**长按 0.4 秒左按钮** → 软触感反馈 + 打开面包屑弹层（`app.breadcrumbOpen = true`）。
**Android 对齐**：`Row`，左 `IconButton` 按 level 切图标，长按用 `Modifier.combinedClickable(onLongClick=)` + `HapticFeedback`。

#### 4.17 `BottomNav`（`Components/BottomNav.swift`）—— 底部导航
**胶囊浮动 bar** + 中央凸起点呼按钮。bar 高 62、`Capsule` 底 `paper` @78% + 玻璃（iOS26 `.glassEffect`，旧版 `.ultraThinMaterial`）+ 白 @50% 描边 0.5 + 阴影黑 @15% 模糊 20 y=6。
- 2 个 tab：「申し込み」（信封图标，路由 `.apply`）/「マイページ」（人形图标，路由 `.my`），中间留 80pt 空给点呼按钮
- tab 激活色 `primary` / 未激活 `inkMute`，图标 20 + 文字 10 semibold
- 激活态背后滑动半透明 `primary` @12% capsule（`matchedGeometryEffect` morph）
- **中央点呼按钮**：62pt 圆 + 径向渐变 `T.rollBtnGrad` + 盾牌图标 `shield.checkered`（26 bold 白）+ 下方「点呼」9 bold + 阴影 `primary` @42%。点击 → 中触感 + `app.openSheet(.rollcall)`，整体上移 10pt 凸起。

**Android 对齐**：Android 已有 `BottomTabs.kt`（要核对是否已含中央点呼按钮）。bar 用浮动 `Surface(shape=CircleShape)`，激活态滑动用 `animateDpAsState` 或 `AnimatedContent`。点呼按钮用 `Box` 圆 + `rollGrad`（已在 Tokens 里）+ 盾牌图标。Compose 无 Liquid Glass → 用 `paper @78%` 半透 + 模糊（`Modifier.blur` 或半透叠层）降级，跟 iOS 旧版 fallback 视觉一致即可。

#### 4.18 `TopRollBar`（`Components/TopRollBar.swift`）—— 全局顶部点呼状态条
常驻顶部胶囊 bar，**4 态**（读 `app.rollState`）：

| 态 | 图标 | 主文字 | 副文字 | 前景色 | 底色 |
|---|---|---|---|---|---|
| `idle`（日常） | clock 色 `primary` | 「次の点呼: 21:00」 | 「タップで体調報告 / 欠席申請」 | `ink` | 玻璃 / `glassBar` |
| `active`（点呼中） | dot.circle.fill 红 + 脉冲 | 「点呼中 · あと N分NN秒で遅刻判定」（倒计时） | 「タップで欠席申請 / 体調報告」 | `warnDeep` | `warnBg` |
| `absent`（欠席） | 三角警告白 | 「欠席判定 · 寮監に直接連絡」 | 「寮監室までお越しください」 | 白 | `danger` |
| `done`（已签到） | check.circle.fill 色 `ok` | 「チェックイン済 〈时刻〉 · 〈方式〉」 | 「お疲れさまでした」 | `okDeep` | `okBg` |

横排：图标 + 竖排（主 12 semibold / 副 10）+ `Spacer` + 非 done 态右侧 chevron @50%。内边距 横 14 / 竖 10，`Capsule` 裁切。点击（非 done）→ `app.openSheet(.feedback)`。
**Android 对齐**：Android 已有 `TopRollBar.kt`，要核对是否齐 4 态 + 倒计时格式。脉冲动画用 `rememberInfiniteTransition` 改 alpha/scale。

#### 4.19 玻璃组件（`Foundation/LiquidGlass/`）
- **`GlassCard`**：iOS 26 原生 `.glassEffect()` 包裹，圆角默认 22（`lg`），3 档强度 `regular/clear/strong`（strong = tint `accent`@10%）。旧版降级 `.ultraThinMaterial`。
- **`GlassSheet`**：自研底部半弹层（不用原生 `.sheet`）。顶部拖拽手柄（36×5 胶囊 `inkMute`@30%）+ 内容（横内边距 20 / 底 40）+ 顶部双圆角 28 + 玻璃底。`从底部滑入 + 淡入`。
- **`GlassBackdrop`**：弹层背后全屏遮罩，`T.glassBackdrop`（`#0F1E22`@35%）+ 玻璃模糊，点击关闭。

**Android 对齐**：Compose **没有 Liquid Glass**。统一降级：
- `GlassCard` → `Card` + 半透 `paper` 底（或 `Modifier.blur` + 半透叠层）
- `GlassSheet` → `ModalBottomSheet`（Material3）自定义 `shape = RoundedCornerShape(topStart=28.dp, topEnd=28.dp)` + 拖拽手柄
- `GlassBackdrop` → `ModalBottomSheet` 自带 scrim，或自做 `Box(background(ink@35%))` + `clickable` 关闭

---

### 5. Android 对齐要点（总览 —— 这块缺什么）

**已经有的（不用重做）**：
- ✅ 色板：`ui/theme/Color.kt` 已 1:1 port 全部 iOS 令牌（`SuzuPrimaryLight = 0xFF1F6B74` 等），还多做了一套 **暗色模式**（iOS 没暗色，Android 自补，先以 Light 为准对齐 iOS）。
- ✅ 令牌容器：`ui/theme/Tokens.kt` 用 `SuzuTokens` data class + `LocalSuzuTokens` CompositionLocal（组合本地变量，子树里用 `SuzuT.current.warn` 取色），等价 iOS `enum T`。三个渐变 `btnGrad / amberGrad / rollGrad` 已建。
- ✅ 字体：`ui/theme/Type.kt` 已建 Material3 Typography（占位 `SansSerif` + `RobotoMono` 数字）。

**缺的 / 要补的**：
1. **没有中央共享组件库** —— iOS 的 `Card / Pill / Avatar / PrimaryButton / GhostButton / Field / TField / TArea / RadioCard / EmptyState / Skeleton / SectionHeader / TToggle / Toast / PageHeader` 在 iOS 是 `Foundation/Components/` 一组独立文件，Android 现在散在各屏内联（`grep` 只在 SettingsScreen / MyPageScreen 命中零星 Card 用法）。**要新建 `ui/components/` 下一组 `@Composable` 函数**，把上面 4.1–4.16 全部实现，参数签名照 iOS（如 `Pill(text, tone)` / `PrimaryButton(title, icon, enabled, destructive, onClick)` / `TField(value, onValueChange, placeholder, secure, keyboard)`）。
2. **`Radius` / `Space` 常量缺** —— iOS 有 `T.Radius`（xs8 sm12 md16 lg22 pill9999）+ `T.Space`（4/8/12/16/24/32），Android `Tokens.kt` 只有颜色没有尺寸常量。**补一个 `object SuzuDim { val radiusMd = 16.dp ... }`**，各组件统一引用。
3. **`FlowLayout` 不用自己写** —— iOS 手写了 `Layout` 协议，Android 直接用 Compose 内置 `FlowRow`，间距 6.dp。
4. **玻璃效果统一降级方案** —— Compose 无 Liquid Glass，全部走「半透明 paper + 可选 `Modifier.blur`」，跟 iOS `iOS<26 fallback` 路径对齐（`paper@78%` / `glassSheet@85%` / `glassBackdrop ink@35%`）。`GlassSheet` 推荐用 Material3 `ModalBottomSheet` + 自定义顶圆角 28 + 拖拽手柄。
5. **底部导航 + 顶部点呼条已有桩**（`BottomTabs.kt` / `TopRollBar.kt`），但要核对：BottomNav 中央凸起点呼按钮（径向渐变 + 盾牌图标 + 上移 10dp）是否齐；TopRollBar 是否齐 4 态 + 倒计时文案格式「点呼中 · あと N分NN秒で遅刻判定」。
6. **字体 TODO** —— iOS 名义上 Hiragino 但实跑系统字体；Android 已留 `TODO: 接入 Noto Sans JP`，可暂用 SansSerif，视觉差可接受，等真上线再放字体文件。
7. **阴影对齐** —— iOS `Card` 是双层柔阴影（5% 模糊14 / 4% 模糊2），Compose `Modifier.shadow` 单层 + elevation 体感不同，建议叠两层或用低 elevation + 自绘 ambient 阴影，避免 Material 默认硬阴影把卡片做「重」。

**优先级建议**：先补 `ui/components/` 组件库 + `SuzuDim` 尺寸常量（地基），再逐屏照各屏规格组装。色板已齐是最大利好 —— Android 只要把组件做出来，各屏拼装时颜色自然对得上 iOS。

**相关文件路径**（Android 工程师参照）：
- iOS 真值：`/Users/kurekoduki/dev/DMSD/03_dev/student_ios/v1/TomoshibiApp/Foundation/Theme/TTokens.swift`、`Foundation/Components/*.swift`、`Foundation/LiquidGlass/*.swift`、`Features/Apply/ApplyStubs.swift`（ChipGroup/FlowLayout）、`Features/Home/HomeStubs.swift`（radioChip/FlowLayout）
- Android 现状：`/Users/kurekoduki/dev/DMSD/03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/theme/{Color,Tokens,Type,Theme}.kt`、`ui/components/{BottomTabs,TopRollBar,GlobalScaffold,HomeCards,RollCallSheet}.kt`、`ui/icons/SuzuIcons.kt`

---

I have all the data I need from both the iOS truth and Android current state. I'll now write the navigation alignment spec section.

## 导航 / 路由 / 整体骨架（navigation）

> 真值来源（iOS）：`Root/RootView.swift`、`Root/GlobalOverlays.swift`、`Foundation/Routing/Route.swift`、`Foundation/Routing/RouterStore.swift`、`Foundation/AppState/AppStore.swift`、`Foundation/AppState/SheetKind.swift`、`Foundation/Components/BottomNav.swift`、`Foundation/Components/TopRollBar.swift`、`Foundation/Components/BreadcrumbOverlay.swift`、`Foundation/Components/PageHeader.swift`、`Foundation/Components/Toast.swift`、`Foundation/LiquidGlass/GlassBackdrop.swift`、`Foundation/LiquidGlass/GlassSheet.swift`、`TomoshibiApp.swift`。
> 这块讲的是「整个 App 的骨架」——不讲某一个具体页长什么样，讲的是**有哪些页、怎么从一页跳到另一页、屏幕上下永久挂着的两条栏（顶部点呼状态条 + 底部导航条）、以及盖在所有页之上的弹窗机制**。

---

### 1. 整体架构（一句话）

iOS 的学生 App **不用 iOS 系统自带的 NavigationStack（系统导航栈，自带左上角返回按钮 + 右滑返回手势）**。理由写在 `RouterStore.swift` 注释里：「3 按钮 nav + 中央 action + 长按 breadcrumb 需自控栈」——意思是它要的导航交互（底部 3 个按钮切 tab、底部中央一个圆按钮弹点呼弹窗、长按返回键弹出历史面包屑）系统栈做不了，所以**自己写了一个导航栈管理器**。

这套骨架由 5 个东西拼成：

| 角色 | iOS 文件 | 干嘛 |
|---|---|---|
| `RouterStore` | `Foundation/Routing/RouterStore.swift` | 导航栈管理器。持有「当前页 `current`」+「页栈数组 `stack`」，提供 `go / back / replace / jump` 四个跳转方法 |
| `Route` | `Foundation/Routing/Route.swift` | 一个枚举（enum），把 App 里**每一个页**都列成一个 case（一共 ~60 个 case）。`current` 的类型就是 `Route` |
| `AppStore` | `Foundation/AppState/AppStore.swift` | 全局状态容器。存登录令牌、当前用户、点呼状态、当前打开的弹窗、toast 文本等。**导航相关的部分**只用到 `sheetOpen`（当前弹窗）/ `breadcrumbOpen`（面包屑开关）/ `toast`（提示文本）/ `rollState`（点呼状态，决定顶部栏显不显示） |
| `RootView` | `Root/RootView.swift` | 顶层视图。一个巨大的 `switch router.current`，按当前 `Route` 渲染对应页；同时用 `safeAreaInset` 把顶部点呼条 + 底部导航条永久挂在上下两端 |
| `GlobalOverlays` | `Root/GlobalOverlays.swift` | 全局浮层。盖在所有页之上，负责渲染弹窗（sheet）/ 面包屑 popup / toast |

App 入口 `TomoshibiApp.swift`：在 `WindowGroup` 里挂一个 `RootView`，把 `router`（`RouterStore`）和 `app`（`AppStore`）作为 `@StateObject` 注入，整个 App 共用这两个单例。注意它**强制 `.preferredColorScheme(.light)`**——暗色模式「做了但没实装」，先锁亮色防黑闪。

---

### 2. Route 枚举 — App 全部页清单（~60 个 case）

`Route.swift` 里每个 case = 一个页。带参数的 case（如 `homePackageDetail(id: Int)`）= 详情页，参数是要展示哪条记录的 id。按 spec 分 5 段：

**§0 认证 / 启动（11 个）**
`splash`（启动闪屏）、`onboarding`（介绍轮播）、`registerStep1~5`（注册 5 步：基本信息 / 点呼区分 / 联络方式 / 密码 / 注册码）、`registerDone`（注册完成）、`login`（登录）、`lockout`（登录失败锁定中）、`pwreset`（密码重置说明）。

**§1 Home 主屏 + 子页（14 个）**
`home`（主屏）、`homeAnnouncements`（公告一覧）、`homeAnnouncementDetail(id: String)`（公告详情）、`homeNotifications`（通知中心）、`homePackages`（宅配一覧）、`homePackageDetail(id: Int)`、`homeLost`（落とし物一覧）、`homeLostNew`（投稿）、`homeLostDetail(id: Int)`、`homeMusic`（リクエスト曲一覧）、`homeMusicNew`、`homeMusicDetail(id: Int)`、`homeEvents`（活动一覧）、`homeEventDetail(id: Int)`、`homeBus`（巴士时刻）。

**§2 申し込み（9 个）**
`apply`（申请一覧 = tab root）、`applyNew`（新规申请入口）、`applyForm(kind: String)`（按申请种类分发表单，kind 是申请类型字符串如「外泊」）、`applyPreview(kind: String)`（确认）、`applyDone(kind: String)`（完成）、`applyDetail(id: String)`（申请详情）、`dormEventList`（行事企画一覧）、`studyOnlineList`（在线学习申请一覧）、`fridgeList`（冷蔵庫購入届一覧）、`itemList`（物品所持許可願一覧）。

**§3 マイページ（15 个）**
`my`（マイページ landing = tab root）、`myInfo`（个人信息）、`myInfoEdit`（编辑）、`myRollcall`（点呼履历）、`myRollcallDetail(entryId: String?)`、`myPoints`（减点明细）、`myPointsChart`（图表）、`myDiscipline`（处分履历）、`myHealth`（体调报告履历）、`myClean`（扫除提出履历）、`myPackages`（宅配履历）、`mySettings`（设定）、`myAbout`（关于）、`myStudy`（学习履历）。

**§4 V1 参考系（5 个，老师 38 条需求）**
`stayList`（申请履历一覧）、`stayDetail(id: String)`、`stayEdit(id: String)`（出寮届修改届）、`schedule`（行事予定月历）、`busList`（寮生特别运航便一覧）。

每个 case 还带 5 个**计算属性**（CC 注：computed property = 不存数据、每次读时现算的属性），这些是导航骨架的关键判断逻辑：

- `displayName: String` — 面包屑里显示的日语名（如 `.home → "ホーム"`、`.apply → "申し込み"`）。**全部日语原文逐条列在 `Route.swift` 74-132 行**，Android 照抄。
- `isTabRoot: Bool` — 是不是底部 tab 的根页（只有 `.home / .apply / .my` 为 true）。
- `isApplyBranch: Bool` — 是不是「申し込み」tab 子树（`.apply / .applyNew / .applyForm / .applyPreview / .applyDone / .applyDetail / .dormEventList / .studyOnlineList / .fridgeList / .itemList`）。**底部导航条用它高亮申し込み按钮**。
- `isMyBranch: Bool` — 是不是「マイページ」tab 子树（`.my / .myInfo / ... / .stayList / .stayDetail / .stayEdit / .schedule / .busList` 共 19 个）。**底部导航条用它高亮マイページ按钮**。注意 §4 参考系 5 页归在 my 分支下。
- `hidesBottomNav: Bool` / `hidesTopBar: Bool` — 是否隐藏底部导航条 / 顶部点呼条。**所有 §0 认证流程页（splash / onboarding / register1~5 / registerDone / login / lockout / pwreset）两个都 true**——即登录前不显示上下两条栏。其余页都显示。

---

### 3. RouterStore — 导航栈四个方法

`RouterStore` 持有两个发布属性（`@Published`，CC 注：值一变 UI 自动重渲染）：
- `current: Route` — 当前在哪一页
- `stack: [Route]` — 页栈数组，记录从哪一路点进来的（面包屑靠它）

四个跳转方法：

| 方法 | 干嘛 | 典型用途 |
|---|---|---|
| `go(_ route)` | 把新页**压栈**（`stack.append` + `current = route`） | 点进详情、进下一注册步：`router.go(.homePackageDetail(id: 3))` |
| `back()` | **弹栈**回退一级（栈只剩 1 个时不动） | 返回键 |
| `replace(_ route)` | **清空栈**只放新页（`stack = [route]`） | 切 tab、登录成功跳主页：`router.replace(.home)` |
| `jump(to route)` | 跳到栈里某一级：若该页在栈中则截断栈到那一位，否则等同 `go` | 面包屑里点某一级 |

还有一个计算属性 `breadcrumbChain: [Route]` = 当前页之前的所有层级（`stack.dropLast()`），面包屑面板遍历它来画路径。

**关键交互约定**（Android 必须一致）：
- 切 tab 用 `replace`（不是 `go`）—— 切到 tab 不应该把旧 tab 压栈，否则面包屑会越积越乱。
- 进详情 / 进子页用 `go`。
- 登录成功 / 注册完成 / 启动后判定 → `replace(.home)` 或 `replace(.login)`。

---

### 4. RootView — 骨架渲染 + 两条栏挂载方式

`RootView.body` 是一个 `ZStack`（层叠容器），从下到上三层：

1. **背景**：`Color(.systemBackground)` 铺满。
2. **当前页**：`content(for: router.current)` —— 一个 `@ViewBuilder switch`，把每个 `Route` case 映射到对应的页视图（如 `.home → HomeView()`、`.apply → ApplyListView()`）。**这个 switch 就是「路由表」**，60 个 case 一一对应。
3. **全局浮层**：`GlobalOverlays()`（见 §6）。

**两条永久栏的挂载方式**（这是整个骨架最特殊的一点，Android 要照做）——不是简单地用一个底部 Bar，而是用 SwiftUI 的 `.safeAreaInset` 把它们挂在「当前页」这一层的上下边：

```swift
content(for: router.current)
    .safeAreaInset(edge: .top, spacing: 0) {
        if !router.current.hidesTopBar && app.rollState != .idle {
            TopRollBar() ...   // 顶部点呼状态条
        }
    }
    .safeAreaInset(edge: .bottom, spacing: 0) {
        if !router.current.hidesBottomNav {
            BottomNav() ...    // 底部导航条
        }
    }
```

`safeAreaInset` 的作用：让条**浮在页面上方**，同时**页内的滚动视图会自动避让**（内容不会被条遮住，能滚到底）。这是 iOS 26 Liquid Glass「内容从玻璃条下方穿过」效果的基础。

**两条栏的显示条件（Android 必须逐条对齐）**：
- **顶部点呼条 `TopRollBar`**：`!hidesTopBar`（非认证页）**且** `app.rollState != .idle`。即——点呼状态是 `idle`（日常无点呼）时**完全不显示**，只有 `active`（点呼中）/ `done`（已签到）/ `absent`（欠席判定）才出现。
- **底部导航条 `BottomNav`**：`!hidesBottomNav`（非认证页）就显示。
- **两条栏在弹窗打开时都淡出**：`.opacity(app.sheetOpen == nil ? 1 : 0)` + `.allowsHitTesting(app.sheetOpen == nil)` + `.animation(.easeInOut(duration: 0.2))` —— 即一旦有 sheet 弹出，上下两条栏淡出到透明且不可点（0.2 秒过渡），避免和弹窗争抢点击。

---

### 5. 顶部点呼状态条 + 底部导航条（两个核心组件）

#### 5.1 TopRollBar（顶部点呼状态条）— `Foundation/Components/TopRollBar.swift`

一条胶囊形（Capsule）横条，左图标 + 两行文字 + 右箭头。**按 `app.rollState` 四态变色变文案**：

| 状态 | 图标 | 主文案（日语原文） | 副文案 | 背景色 |
|---|---|---|---|---|
| `idle` | `clock`（teal 色） | （此态整条不显示，见 §4） | — | 玻璃透明 `glassBar` |
| `active` | `dot.circle.fill`（红色，脉冲动画） | `点呼中 · あと N分NN秒で遅刻判定`（倒计时由 `rollCountdownSec` 算：分 = 秒/60，秒 = 秒%60） | `タップで欠席申請 / 体調報告` | 暖色 `warnBg`（`0xFDF4E1`） |
| `absent` | `exclamationmark.triangle.fill`（白） | `欠席判定 · 寮監に直接連絡` | `寮監室までお越しください` | 红 `danger` |
| `done` | `checkmark.circle.fill`（绿） | `チェックイン済 {时刻} · {判定}`（时刻 = `checkinAt`，判定 = `checkinKind` 如「時間内」） | `お疲れさまでした` | 绿 `okBg`（`0xE3F1EA`） |

交互：整条可点（`contentShape(Capsule())`）。`rollState != .done` 时点击 → `app.openSheet(.feedback)`（弹出「体调报告 / 欠席申请 / 其他」3 选 1 弹窗）；`done` 态不可点、右箭头隐藏。

#### 5.2 BottomNav（底部导航条）— `Foundation/Components/BottomNav.swift`

一条胶囊形浮条，结构是 **「左 tab — 中间 80pt 空隙 — 右 tab」+ 一个凸起的圆形中央按钮浮在空隙上方**（`ZStack` 叠，中央按钮 `.offset(y: -10)` 上移凸出）：

- **左 tab「申し込み」**：图标 `envelope.fill`，文字 `申し込み`，高亮判定 `router.current.isApplyBranch`，点击 `router.replace(.apply)`。
- **右 tab「マイページ」**：图标 `person.fill`，文字 `マイページ`，高亮判定 `router.current.isMyBranch`，点击 `router.replace(.my)`。
- **中央圆形按钮「点呼」**：62×62 圆形，径向渐变背景 `rollBtnGrad`（teal），白色盾牌图标 `shield.checkered`，下方小字 `点呼`。点击触发**中等强度触感反馈**（`UIImpactFeedbackGenerator(.medium)`）+ `app.openSheet(.rollcall)`（弹点呼弹窗）。

外形：高 62pt、胶囊形、半透明纸色背景 `paper.opacity(0.78)`、白色 0.5pt 描边、`black.opacity(0.15)` 阴影。

高亮规则：active tab 文字/图标用 `primary`（teal）色，非 active 用 `inkMute`（灰）。iOS 26 上 active tab 背后有一个半透明 teal 胶囊滑动 morph（`matchedGeometryEffect`）；iOS < 26 退化成纯 tint。

**注意**：底部只有「申し込み / マイページ」两个 tab 按钮 + 中央「点呼」按钮——`home`**不在底部导航条里**（首屏从 splash → home，home 本身没有底部 tab 高亮，靠中央按钮 + 顶部条 + 页内入口导航）。这点 Android 别画成 3 个文字 tab。

---

### 6. GlobalOverlays — 全局弹窗机制（sheet / 面包屑 / toast）

`GlobalOverlays.swift` 是盖在所有页之上的 `ZStack`，三种浮层各自独立判断显隐：

#### 6.1 Sheet（半屏弹窗）

由 `app.sheetOpen: SheetKind?` 驱动（nil = 无弹窗）。一旦非 nil：
1. 先铺一层 `GlassBackdrop`（`GlassBackdrop.swift`）—— 全屏暗化遮罩（`0x0F1E22` 35% 透明）+ 毛玻璃模糊，点遮罩 → `app.closeSheet()`。
2. 再 `switch kind` 渲染对应弹窗内容。

`SheetKind` 枚举（`SheetKind.swift`）9 种弹窗：
- `rollcall` — 中央点呼按钮弹的点呼弹窗
- `feedback` — 顶部条点出来的「3 选 1」弹窗（体调 / 欠席 / 其他）
- `health` — 体调问题报告
- `absence` — 今回欠席申请
- `other` — 其他问题
- `logout` — 登出确认
- `studyCheckin` — 学习 NFC 2 次签到弹窗
- `songReport(songId: Int)` — リクエスト曲通报弹窗
- `renewStudentNo` — 番号再设定弹窗

弹窗内容用自研 `GlassSheet`（`GlassSheet.swift`）——**不用系统 `.sheet()`**（理由注释：系统 sheet 背景不可改 + 长按吃事件）。`GlassSheet` 是底部半屏面板：顶部一个灰色拖拽手柄（36×5 胶囊）+ 内容；上两角圆角 28pt；iOS 26 用 `glassEffect`、以下用 `glassSheet`（白 85%）纯色；从底部滑入（`.move(edge: .bottom)`）。

`AppStore` 提供 `openSheet(kind)` / `closeSheet()`，都带 spring 动画（`response: 0.34, dampingFraction: 0.82`）。

#### 6.2 面包屑 popup（BreadcrumbOverlay）

由 `app.breadcrumbOpen: Bool` 驱动。模仿 **iOS Safari「长按返回键弹历史」**：不是居中大弹窗，而是**贴在左上角返回键正下方的小卡片**（`width: 240`，origin 在 `leading: 12 / top: safeArea+50`）。

触发方式：每个子页头部 `PageHeader`（`PageHeader.swift`）左上角那个返回/Home 键，**长按 0.4 秒**（`LongPressGesture(minimumDuration: 0.4)`）+ 轻触感反馈 → `app.breadcrumbOpen = true`。

面包屑内容：第一行永远是「`ホームへ戻る`」（点 → `router.replace(.home)`），下面遍历 `router.breadcrumbChain`（栈里 current 之前的层级），每行显示 `route.displayName`（日语名），点 → `router.jump(to: route)`。背景透明遮罩（几乎全透 `opacity(0.0001)`，点外侧关闭）。

#### 6.3 Toast（底部提示条）

由 `app.toast: String?` 驱动。`Toast.swift`：底部居中胶囊条（`ink.opacity(0.88)` 深色背景、白字、距底 100pt），从底部滑入。`AppStore.showToast(text)` 显示后 **2.2 秒自动清空**。

#### 6.4 PageHeader（每个子页的头部）— 导航规则核心

`PageHeader.swift` 是所有非 tab-root 子页统一头部：左键 + 标题 + 可选右键。左键按 `level` 分两态：
- `level == 1`（L1 页）：显示 Home 图标，点 → `router.replace(.home)`。
- `level >= 2`（L2+ 页）：显示返回箭头，点 → `router.back()`。
- **任意 level 长按 0.4s → 弹面包屑**（见 6.2）。

---

### 7. 页面层级树（进入路径）

```
splash（启动）
 ├─ 有令牌 → replace(home)
 └─ 无令牌 → replace(login)
            login ─ 新規登録 → go(registerStep1) → go(step2) → go(step3) → go(step4) → go(step5) → replace(registerDone) → replace(home)
            login ─ 失败 → go(lockout) ─ 倒计时完 → replace(login)

home（主屏，无底部 tab 高亮）
 ├─ 公告 → go(homeAnnouncements) → go(homeAnnouncementDetail)
 ├─ 通知铃铛 → go(homeNotifications)
 ├─ Community 入口 → go(homePackages/homeLost/homeMusic/homeEvents/homeBus) → 各自 detail/new
 │
[底部导航条]
 ├─ 申し込み tab → replace(apply)
 │   apply ─ FAB → go(applyNew) → 选 kind → go(applyForm(kind)) → go(applyPreview(kind)) → go(applyDone(kind))
 │   apply ─ 列表项 → go(applyDetail(id))
 │   apply ─ 各类一覧 → go(dormEventList / studyOnlineList / fridgeList / itemList)
 ├─ 中央「点呼」按钮 → openSheet(rollcall)   ※ 不切页，弹窗
 └─ マイページ tab → replace(my)
     my → go(myInfo → myInfoEdit / myRollcall → myRollcallDetail / myPoints → myPointsChart /
            myDiscipline / myHealth / myClean / myPackages / mySettings / myAbout / myStudy /
            stayList → stayDetail → stayEdit / schedule / busList)
```

---

### Android 对齐要点

**Android 现状盘点（已 Read 确认）**：Android 已经有一套桩骨架，但和 iOS 偏差大，需要重做对齐：
- `nav/Routes.kt`：用 `sealed class Route` 列了**只 22 个 route**（iOS 是 ~60 个），且把 home/applications/nfc/notifications/mypage 设计成「core 5 tab」——**和 iOS 不一致**（iOS 底部只有 2 个 tab 按钮 + 1 个中央点呼按钮，home 不是 tab，notifications 是 home 子页不是 tab）。
- `nav/NavGraph.kt`：用 Jetpack Navigation Compose 的 `NavHost` + `composable(path)` —— 即用了 Android 系统导航栈。iOS 是**自研栈**。
- 已有 `ui/components/BottomTabs.kt`(184 行) / `GlobalScaffold.kt`(54 行) / `TopRollBar.kt` 桩，但都是早期演示版、无真实状态驱动。
- 全部 22 屏只有本地 `MockData.kt` 假数据，**无任何网络层**。

**要做成什么样（逐条）**：

1. **Route 改造成 ~60 个，对齐 iOS 全清单**。Android 用 `sealed class Route` 是对的方向（iOS 也是 enum/带参数）。带参数的页（detail）用 `data class`（Android 已有 `ApplicationDetail(id)` / `NotifDetail(id)` 范式，照此扩展到 `homePackageDetail / applyDetail / stayDetail` 等全部 detail）。**每个 Route 加 `displayName` 属性**，日语值逐字照抄 iOS `Route.swift` 74-132 行（面包屑要用）。再加 `isApplyBranch` / `isMyBranch` / `hidesBottomNav` / `hidesTopBar` / `isTabRoot` 五个判断属性，case 归类和 iOS 完全一致（特别注意 §4 stay/schedule/bus 5 页归在 myBranch）。

2. **要不要用 Jetpack Navigation Compose？建议放弃，改自研栈对齐 iOS**。理由同 iOS：底部 3 按钮 + 中央 action 弹窗 + 长按返回弹面包屑，系统 NavHost 的返回栈和 BottomNavigation 模型套不进来（尤其面包屑跳任意一级 = `popBackStack(route, inclusive)` 行为不自然）。做法：写一个 `RouterStore`（用 `class RouterStore { var current by mutableStateOf<Route>(...); val stack = mutableStateListOf<Route>() }`），实现 `go / back / replace / jump(to)` 四方法 + `breadcrumbChain` 计算属性，语义和 iOS `RouterStore.swift` 一对一。把 `RouterStore` 和 `AppStore` 用 `CompositionLocal` 或 hoisted state 注入到整个 Compose 树（对应 iOS 的 `@EnvironmentObject`）。

3. **RootView 改成「`when(router.current)` 单点路由表 + 上下两条栏挂载」**。Compose 做法：最外层 `Box`（对应 iOS ZStack）三层——背景 / 当前页 / GlobalOverlays。当前页用 `Scaffold` 或手动布局，把 TopRollBar / BottomNav 放在 `topBar` / `bottomBar`，或者用 `Modifier.windowInsetsPadding` + 手动叠放让内容滚动避让（对应 iOS `safeAreaInset`）。**显示条件逐条对齐**：TopRollBar 仅当 `!current.hidesTopBar && appStore.rollState != Idle`；BottomNav 仅当 `!current.hidesBottomNav`；两条栏在 `appStore.sheetOpen != null` 时 `alpha` 动画淡出到 0 + 不可点（用 `Modifier.alpha()` + `pointerInput` 拦截，`animateFloatAsState` 0.2 秒）。

4. **BottomNav 画成「2 文字 tab + 中央凸起圆按钮」，不是 Material 的 3-tab BottomNavigation**。结构：`Box` 里放一条胶囊 `Row`（左「申し込み」envelope 图标 / 中间 80dp `Spacer` / 右「マイページ」person 图标），再叠一个中央圆形 `IconButton`（62dp 圆、teal 径向渐变、白盾牌图标 `shield`、下方小字「点呼」、`offset(y = -10.dp)` 凸起）。胶囊外形：高 62dp、`Color.White.copy(alpha=0.78f)` 背景、`RoundedCornerShape(50)`、0.5dp 白描边、阴影。高亮：左按钮亮判定 `current.isApplyBranch`、右按钮 `current.isMyBranch`，亮色用 teal `0xFF1F6B74`、灰用 inkMute。点击：左 `router.replace(Apply)`、右 `router.replace(My)`、中央 `haptic(medium)` + `appStore.openSheet(Rollcall)`。

5. **TopRollBar 4 态照抄文案 + 配色**。Compose：一条 `RoundedCornerShape(50)` 胶囊 `Row`，左图标 + 两行 `Text` + 右 chevron。`when(appStore.rollState)` 切图标/主副文案/背景色，**日语主副文案逐字照抄 iOS TopRollBar.swift 59-80 行**（`active` 的倒计时格式 `点呼中 · あと %d分%02d秒で遅刻判定`、`done` 的 `チェックイン済 {checkinAt} · {checkinKind}` 等）。背景色对齐 token：active=`0xFFFDF4E1` / absent=danger 红 / done=`0xFFE3F1EA`。整条 `clickable`，非 done 态点击 → `appStore.openSheet(Feedback)`。

6. **全局弹窗机制三件套（sheet / 面包屑 / toast）独立实装，不用 Material 自带**：
   - **Sheet**：`appStore.sheetOpen: SheetKind?` 驱动（`SheetKind` 改成 Kotlin sealed class，9 种照抄含 `SongReport(songId)` 带参）。非 null 时先铺 `Box` 全屏遮罩（`Color(0xFF0F1E22).copy(alpha=0.35f)` + 模糊，`clickable` 关闭），再 `when(kind)` 渲染内容。内容用**自研底部半屏面板**（顶部拖拽手柄 36×5dp + 上两角 28dp 圆角 + 从底滑入 `AnimatedVisibility(slideInVertically)`）——**别用 Material `ModalBottomSheet`**（iOS 特意避开系统 sheet，Android 同理保持外观一致 + 避免手势冲突）。`openSheet/closeSheet` 带 spring 动画。
   - **面包屑**：`appStore.breadcrumbOpen: Boolean` 驱动。**贴左上角返回键下方的 240dp 小卡片**（不是居中 Dialog），首行「`ホームへ戻る`」+ 遍历 `router.breadcrumbChain` 显示各级 `displayName`。触发：子页头部返回键 `combinedClickable(onLongClick = { appStore.breadcrumbOpen = true })`（长按 ~400ms + `HapticFeedback`）。点某级 → `router.jump(to)`。外侧透明遮罩点击关闭。
   - **Toast**：`appStore.toast: String?` 驱动，底部居中深色胶囊（距底 100dp），`showToast()` 后 2.2 秒 `delay` 自动清。**别用 Android 系统 Toast**（外观/位置不可控）。

7. **PageHeader（子页头部）统一组件**：左键 + 标题 + 可选右键。`level == 1` 显 Home 图标点击 `router.replace(Home)`、`level >= 2` 显返回箭头点击 `router.back()`，任意 level `onLongClick` 弹面包屑。所有非 tab-root 子页都用它。

8. **启动 + 登录跳转逻辑对齐**：SplashScreen 停留 2.2 秒后——有令牌 `router.replace(Home)`、无令牌 `router.replace(Login)`（不再强制走 onboarding，对齐 iOS 2026-05-07 决策）。登录成功 / 注册完成 → `replace(Home)`；切 tab 一律 `replace`、进详情/子页一律 `go`。

9. **强制亮色**：对齐 iOS 当前 `.preferredColorScheme(.light)`——Android 主题先锁 light（`Theme` 不跟随系统 dark），暗色模式同样「做了未实装」。

**Android 工程师验收自检**：① 底部只有 2 个文字 tab + 1 个中央点呼圆按钮（不是 3 tab）② 顶部点呼条只在 rollState 非 idle 时出现、4 态文案/配色逐字对 ③ 长按返回键弹面包屑、贴左上角 ④ 弹窗打开时上下两条栏 0.2 秒淡出不可点 ⑤ 全部 ~60 个 Route 都能到达、detail 带 id 参数 ⑥ 切 tab=replace / 进详情=go / 返回=back。

---

I have everything I need. I've read all network layer files: APIClient, APIError, APIErrorPresenter, NetworkModels, KeychainService, ApplyKindMapper, and all 7 endpoint files (Auth, Applications, ApplicationsCreateBodies, Study, Bus, DormLife, Events, RollCall). Now I'll write the complete API contract section.

## 后端 API 契约 + 数据模型（Android 网络层从零搭建蓝图）

> 本节是 Android 从零写网络层（目前 Android 完全没有网络层，只有 `MockData.kt` 本地假数据）的**唯一真值蓝图**。iOS 已基于这套契约跑通（Swift 的 `Foundation/Network/`），Android 必须调**一模一样的端点、对一模一样的字段**。所有字段命名是 `snake_case`（蛇形小写，单词间下划线连接，后端 Python 的命名习惯），Android 用 Kotlin 数据类时要么把属性名也写成蛇形，要么用 Moshi 的 `@Json(name="...")` / kotlinx.serialization 的 `@SerialName("...")` 把 Kotlin 驼峰名映射到蛇形线缆名。

---

### ① base url（服务器根地址）+ 全局请求约定

iOS 来源：`APIClient.swift`。

| 项 | 值 |
|---|---|
| DEBUG（开发，连本机）base url | `http://localhost:8000` |
| RELEASE（上架，连生产服务器）base url | `https://api.tomoshibi.cc` |
| 环境变量覆盖 | iOS 读 `TOMOSHIBI_API_URL`，有就用它顶替默认 |
| 请求超时 | 15 秒（`timeoutIntervalForRequest = 15`） |
| 所有路径前缀 | `/api/v1/...`（注意：base url 不含 `/api/v1`，端点路径自带） |

**全局请求头（每个请求都加）**：

- `Content-Type: application/json`（JSON 请求体时）；上传文件时是 `multipart/form-data; boundary=...`。
- `Authorization: Bearer <token>` —— 登录成功后拿到 `access_token`（一段 JWT 字符串，JWT = JSON Web Token，服务器签发的登录凭证），之后**所有请求都带上**。token 为空（未登录）时不加这个头。

**token 持久化**（iOS 用 Keychain，见 `KeychainService.swift`）：

- iOS 把 token 存进 Keychain（苹果系统加密存储），不存明文 `UserDefaults`，理由是 token 是机密、设备越狱后明文存储能直接被读。
- service 标识 `jp.tomoshibi.cc`，account 标识 `student.jwt`。
- 三个操作：`save(token)` 登录成功后存、`load()` app 启动时读（实现自动登录）、`delete()` 登出或收到 401 时清。

---

### ② 通用响应解码 + 状态码处理（Android 必须照搬这套口径）

iOS 来源：`APIClient.swift` 的 `decodeResponse` + `APIError.swift` + `APIErrorPresenter.swift`。

**状态码分支**（这是 Android 网络层的核心逻辑，错一个就会到处误报失败）：

| HTTP 状态码 | iOS 处理 | Android 要做成 |
|---|---|---|
| 200–299（成功） | 正常 JSON 解码成目标模型 | 同样解码 |
| 204 No Content / body 为空 | **不走 JSON 解码**，直接当成功返回空对象 | 必须特判：部分 DELETE 接口返回 204 空 body，强行 JSON 解码会失败 → 误报删除失败 |
| 401 | 抛 `unauthorized`（需重新登录） | 抛对应异常，UI 提示重新登录、清 token |
| 422（输入校验错） | 抛 `unprocessable(后端的错误 message)` | 抽取后端 message 原样显示给用户 |
| 其他（5xx 等） | 抛 `server(状态码, message)` | 同样带状态码 + message |

**422 / 错误响应里怎么抽 message**（后端有两种错误体形态，两种都要试着解）：

1. 形态 A（FastAPI 自带校验错）：`{"detail": "字符串"}`
2. 形态 B（后端自己 raise 的）：`{"detail": {"code": "...", "message": "..."}}`

iOS 先试形态 B（信息量更大，message 是后端写好的日语提示），失败再退到形态 A。Android 要写一个同样的 `extractMessage`：先尝试把 `detail` 当对象解（取里面的 `message`），失败再当字符串解。422 时若两种都抽不到，iOS 用兜底文案「`入力エラー`」（输入错误）。

**错误类型（iOS `APIError` 枚举，Android 建一个对应的 sealed class）**：

| iOS case | 含义 | 用户提示文案（日语原文，UI 直接显示） |
|---|---|---|
| `network(Error)` | 通信失败（Wi-Fi 断等） | 「通信エラーが発生しました。電波を確認してください。」 |
| `decode(Error)` | JSON 解析失败 | 「データの読み込みに失敗しました。」 |
| `unauthorized` | 401，需重新登录 | 「ログインが必要です。再度ログインしてください。」 |
| `unprocessable(msg)` | 422，输入错 | 直接显示后端返回的 `msg`（后端写好的日语提示） |
| `server(code, msg)` | 5xx 等 | 「サーバーエラー（コード: \(code)）。時間をおいて再度お試しください。」 |
| `unknown` | 兜底 | 各调用点自定义 fallback 文案 |

> Android 实现提示：iOS 有个 `APIErrorPresenter.userMessage(for:fallback:)`，把任意异常转成上面这些日语提示字符串，多个界面共用。Android 也应建一个等价的 `ApiErrorPresenter` 单一来源，避免每个屏幕各写一份 catch 文案导致漂移。

**日期解码（关键坑，Android 一定要处理）**：

- 后端返回的 datetime（带时分时区的完整时刻，如 `2026-05-03T18:00:00.123456+09:00`）默认**带微秒（小数秒）**。
- iOS 的全局解码器配了一个自定义日期策略 `decodeISO8601Date`：先用「带小数秒」的 ISO8601 格式试，失败再退到「不带小数秒」的，两种都不行才抛错。
- Android 同样要兼容这两种，否则后端发带微秒的时间会让整段 JSON 解码失败（iOS 历史 bug 编号 IX-003）。
- **三类时间字段的处理方针**（NetworkModels.swift 头部注明，Android 必须一致）：
  - `yyyy-MM-dd` 纯日期（如 `leave_date`、`target_date`、`event_date`）→ **保留成字符串**，不解成日期对象（裸日期没时分时区，强行 ISO8601 解会失败）。
  - `HH:mm:ss` 纯时刻（如 `leave_time`、`taxi_reservation_time`）→ **保留成字符串**。
  - `YYYY-MM-DDTHH:mm:ssZ` 完整 datetime（如 `submitted_at`、`schedule_at`、`flight_dep_at`）→ 解成日期对象（Kotlin 用 `Instant` / `OffsetDateTime`）。

---

### ③ 端点全清单（方法 + 路径 + 用途 + 请求体 + 响应）

> 学生 App 实际会调的所有端点。每个 iOS 端点包装成一个 enum（命名空间），Android 可以建对应的 Retrofit interface 或 Ktor 函数。

#### 认证 + 账号（`AuthAPI.swift`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| POST | `/api/v1/sessions/student` | 学生登录 | `StudentLoginRequest`（`student_no`、`password`） | `TokenOut` |
| POST | `/api/v1/accounts` | 学生新规注册（必带教师生成的 6 位注册码） | `StudentAccountCreateBody` | `StudentAccountCreateResponse`（201） |
| DELETE | `/api/v1/accounts/me` | 删除自己账号（App Store 强制要求） | 无 | 204 No Content |
| GET | `/api/v1/students/me` | 当前登录学生基本信息 | 无 | `StudentMeOut` |
| POST | `/api/v1/students/me/renew-number` | 番号再设定（学年更新、自选学年/组/出席番号） | `RenewBody`（`grade_code`、`class_code`、`seat_no`） | `StudentMeOut` |
| GET | `/api/v1/discipline/me/summary` | 当月扣分汇总 | 无 | `MyDisciplineSummaryOut` |

#### 老师公告（`AuthAPI.swift` 里的 `AnnouncementsAPI`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| GET | `/api/v1/announcements` | 公告列表（按学生 scope 自动过滤、新→旧） | 无 | `AnnouncementListResponse` |
| GET | `/api/v1/announcements/unread-count` | 主页未读数 badge | 无 | `AnnouncementUnreadCount` |
| GET | `/api/v1/announcements/{id}` | 公告详情 + 回复（访问时自动标已读） | 无 | `AnnouncementDetail` |
| POST | `/api/v1/announcements/{id}/replies` | 学生发回复 | `ReplyBody`（`body`） | `AnnouncementReplyOut` |
| DELETE | `/api/v1/announcements/{aid}/replies/{rid}` | 删自己发的回复 | 无 | 204 |

#### 出寮届（`ApplicationsAPI.swift` + `ApplicationsCreateBodies.swift`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| POST | `/api/v1/applications` | 提交出寮届（帰省/外泊/帰国之一） | `KisheiCreateBody` / `GaihakuCreateBody` / `KikokuCreateBody`（后端按 `kind` 字段 dispatch） | `ApplicationOut` |
| GET | `/api/v1/applications/mine` | 我的申请一览（最近优先） | 无 | `[ApplicationOut]` |
| GET | `/api/v1/applications/{id}` | 申请详细（含承认 chain 全部 step） | 无 | `ApplicationOut` |
| PUT | `/api/v1/applications/{id}` | 修改届（pending/approved_partial/returned 时可改） | `ApplicationUpdateBody`（全字段 Optional） | `ApplicationOut` |
| GET | `/api/v1/applications/{id}/audit` | 改动履历 | 无 | `[AuditLogOut]` |

> **路径 id 大小写注意**：iOS 调详细/修改/audit 时把 UUID 转成**小写**（`.uuidString.lowercased()`）拼进路径。Android 也要小写，避免后端大小写敏感时 404。

#### 学習（晚自习，`StudyAPI.swift`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| POST | `/api/v1/study/absence-requests` | 学習欠席届提交 | `AbsenceRequestBody`（`target_date`、`period`、`reason`） | `StudyAbsenceRequestOut` |
| GET | `/api/v1/study/absence-requests/me/summary` | 当月请假次数 | 无 | `MyAbsenceSummaryOut`（`month`、`count`） |
| POST | `/api/v1/study/online-requests` | 学習オンライン申請提交 | `OnlineRequestBody` | `StudyOnlineRequestOut` |
| GET | `/api/v1/study/online-requests/mine` | 我的在线学习申请列表 | 无 | `[StudyOnlineRequestOut]` |
| POST | `/api/v1/study/online-requests/{id}/contract` | 上传契約書（合同照片/PDF） | multipart 文件（字段名 `file`） | `StudyOnlineRequestOut` |

#### 宿舍生活类申請（`DormLifeAPI.swift`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| POST | `/api/v1/dorm-life/event-proposals` | 寮生行事企画申請书提交 | `EventProposalBody` | `DormEventProposalOut` |
| GET | `/api/v1/dorm-life/event-proposals/mine` | 我的行事企画列表 | 无 | `[DormEventProposalOut]` |
| POST | `/api/v1/dorm-life/fridge-purchases` | 冷蔵庫購入届提交 | `FridgePurchaseBody` | `FridgePurchaseRequestOut` |
| GET | `/api/v1/dorm-life/fridge-purchases/mine` | 我的冷蔵庫購入届列表 | 无 | `[FridgePurchaseRequestOut]` |
| POST | `/api/v1/dorm-life/item-possessions` | 物品所持許可願提交 | `ItemPossessionBody` | `ItemPossessionRequestOut` |
| GET | `/api/v1/dorm-life/item-possessions/mine` | 我的物品所持願列表 | 无 | `[ItemPossessionRequestOut]` |

#### 巴士便 + 行事预定 + 点呼（`BusAPI.swift` / `EventsAPI.swift` / `RollCallAPI.swift`）

| 方法 | 路径 | 用途 | 请求体 | 响应 |
|---|---|---|---|---|
| GET | `/api/v1/bus/routes` | 巴士便列表（可带 `?kind=daily_commute` / `?kind=dorm_special` 过滤） | 无（query 参数 `kind` 可选） | `BusRouteListOut`（取 `.items`） |
| GET | `/api/v1/events` | 行事予定列表（可带 `?from_date=&to_date=` 范围过滤，纯日期 `yyyy-MM-dd`） | 无（query 参数 `from_date` / `to_date` 可选） | `EventListOut`（取 `.items`） |
| POST | `/api/v1/rollcall/sessions/{id}/checkins` | 学生 NFC tap 点呼提交（路径 B = iPhone tap 静态标签） | `RollCallCheckinBody` | `RollCallEventOut` |

> Bus / Events 的列表响应是 `{"items": [...]}` 包装，iOS 解包后只返回数组。Android 同样：解 wrapper 取 `items`。

---

### ④ 所有数据模型字段（snake_case，Android Kotlin 数据类逐字段对齐）

> 标注 `?` 的是可空（Optional / nullable）。Kotlin 里写成可空类型 `Type?`。**漏接一个非空字段会让整段 JSON 解码失败**（iOS 历史 bug：`bus_route_id` 漏接导致整个申请详情 decode 崩，编号 FC-020），所以即使界面不显示也要在数据类里保留。

#### 登录 / 注册响应

**`TokenOut`**（登录成功响应；后端蛇形 → Kotlin 字段）：
- `access_token: String` —— JWT 令牌
- `token_type: String` —— 固定 `"bearer"`
- `expires_in: Int` —— 过期秒数

**`StudentAccountCreateBody`**（注册请求体，POST `/accounts`）：

| 字段 | 类型 | 说明 / 约束（与后端 `StudentAccountCreateIn` 对齐） |
|---|---|---|
| `name` | String | 氏名，1–100 字，必填非空 |
| `name_kana` | String? | 氏名假名，≤100 字 |
| `birthday` | String? | `yyyy-MM-dd`，没填传 null |
| `gender` | String | `"male"` 或 `"female"` |
| `grade_code` | String | 恰好 2 位数字 `^\d{2}$` |
| `class_code` | String | 恰好 2 位数字 |
| `seat_no` | String | 恰好 2 位数字 |
| `category` | String | `"一般寮生"` 等 |
| `room_no` | String | `"M101"` / `"W205"`，3–8 字 |
| `dorm_unit` | Int | 只能是 `1` / `2` / `4`（男寮 1·2、女寮 4，没有 3） |
| `is_overseas` | Bool | 是否海外生 |
| `email` | String? | ≤200 字 |
| `phone` | String? | ≤32 字 |
| `password` | String | 6–128 字 |
| `registration_code` | String | 恰好 6 位数字（教师生成、5 分钟有效） |

> **客户端表单校验（Android 必须照搬）**：iOS 在 `StudentAccountCreateBody.validate()` 里做了完整本地校验（非空 / 长度上下限 / 固定格式），返回 nil = 通过，否则返回一条日语错误文案。这是为了在发请求前就拦住明显错误，避免白白吃 422。Android 应写一个等价的本地校验函数，错误文案逐条照抄（如「`氏名を入力してください`」「`部屋番号は 3 文字以上で入力してください`」「`登録コードは 6 桁の数字で入力してください`」「`パスワードは 6〜128 文字で入力してください`」等，全部见下方文案表）。

**`StudentAccountCreateResponse`**（注册成功 201）：
- `access_token: String`、`token_type: String`、`expires_in: Int`、`student: StudentBrief`

#### 学生信息

**`StudentMeOut`**（GET `/students/me`）：
- `id: String`、`student_no: String`、`name: String`、`name_kana: String?`、`grade_code: String`、`class_code: String`、`seat_no: String`、`gender: String`、`category: String`、`room_no: String`、`dorm_unit: Int`、`is_overseas: Bool`、`email: String?`、`phone: String?`、`avatar_url: String?`、`status: String`、`needs_renewal: Bool?`（学年更新「待更新」标记 → true 时主页显示「更新番号」按钮，可空兜底防分阶段部署解码崩）
- 注：后端还会发 `registered_at`，iOS 不接（解码默认跳过多余字段，Android 也无视即可）

**`StudentBrief`**（申请详情里嵌入的学生简易信息）：
- `id: UUID`、`student_no: String`、`name: String`、`dorm_unit: Int`、`is_overseas: Bool`、`room_no: String`

**`MyDisciplineSummaryOut`**（当月扣分汇总）：
- `month: String`、`total_points: Double`、`late_count: Int`、`absent_count: Int`

> Android 注意：`total_points` 是浮点数（`Double`），扣分可能是 0.5 这种半分，别写成 Int。

#### 出寮届

**`ApplicationOut`**（申请详情 / 列表元素，最复杂，字段最多）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | |
| `student_id` | UUID | |
| `student` | StudentBrief? | 列表里可能 null，详情里有 |
| `kind` | String | `"帰省"` / `"外泊"` / `"帰国"`（日文原文，后端直接发日文） |
| `reason` | String? | 申请理由 |
| `contact_phone` | String? | 联系电话 |
| `meal_note` | String? | 餐食备注 |
| `companion` | String? | 同行人（仅外泊/帰国） |
| `dest_cities` | String? | 目的地城市（仅外泊/帰国） |
| `receipt_submitted` | Bool? | |
| `is_long_vacation` | Bool? | 是否长假 |
| `leave_date` | String | `"2026-05-03"`（纯日期保字符串） |
| `leave_method` | String | 出发方式 |
| `leave_time` | String | `"19:40:00"`（纯时刻保字符串） |
| `return_date` | String | |
| `return_method` | String | |
| `return_time` | String | |
| `taxi_reservation_time` | String? | 出租车预约时刻 `"HH:MM:SS"`，null = 不预约 |
| `stay_locations` | [[String: AnyJSON]]? | 滞在先列表（仅外泊/帰国），松散 JSON |
| `meals_skip` | [[String: AnyJSON]]? | 食堂跳过的餐（仅外泊/帰国），松散 JSON |
| `flight_dep_air` | String? | 出发空港（仅帰国） |
| `flight_dep_at` | Date? | 出发时刻 datetime（仅帰国） |
| `flight_arr_air` | String? | 到达空港（仅帰国） |
| `flight_arr_at` | Date? | 到达时刻 datetime（仅帰国） |
| `bus_route_id` | UUID? | 关联巴士便（界面不显示但必须接，否则解码崩） |
| `submitted_at` | Date | 提交时刻 datetime |
| `status` | String | `"pending"` / `"approved_partial"` / `"approved"` / `"rejected"` / `"withdrawn"` / `"returned"` |
| `withdrawn_at` | Date? | |
| `approval_chain` | [ApprovalStepOut] | 承认链（每个役职一步） |

**`ApprovalStepOut`**（承认链的一步）：
- `approver_role: String`（`"担任"` / `"寮務課長"` / `"管理係"` 等）、`decision: String?`（`"approve"` / `"reject"` / null=未决）、`decided_at: Date?`、`comment: String?`、`approver_id: UUID?`

**`AuditLogOut`**（改动履历）：
- `id: UUID`、`actor_type: String`（`"student"` / `"teacher"`）、`actor_id: UUID?`、`action: String`（`"application.submit"` / `"application.approve"` / `"application.amend"` 等）、`payload: [String: AnyJSON]?`、`created_at: Date`

**提交请求体（按 kind 分 3 个，`kind` 字段硬编码日文）**：

- `KisheiCreateBody`（帰省，最简）：`kind="帰省"` + `reason?`、`contact_phone?`、`meal_note?`、`is_long_vacation: Bool`、`leave_date`、`leave_method`、`leave_time`、`return_date`、`return_method`、`return_time`、`taxi_reservation_time?`
- `GaihakuCreateBody`（外泊）：在帰省基础上去掉 `is_long_vacation`，加 `companion?`、`dest_cities?`、`stay_locations: [StayLocationBody]`（至少 1 件，后端校验）、`meals_skip: [MealSkipBody]`（0 件以上）
- `KikokuCreateBody`（帰国）：在外泊基础上加 `flight_dep_air: String`、`flight_dep_at: String`（ISO8601 datetime 字符串如 `"2026-05-03T18:00:00+09:00"`）、`flight_arr_air: String`、`flight_arr_at: String`

**子模型**：
- `StayLocationBody`：`kind: String`（`"ホテル"` / `"親戚宅"` / `"自宅"` 等）、`name: String`、`address: String?`、`phone: String?`
- `MealSkipBody`：`date: String`（`"2026-05-03"`）、`meal: String`（`"朝食"` / `"昼食"` / `"夕食"`）

**`ApplicationUpdateBody`**（PUT 修改届，全字段可空，只传改了的）：
- 字段同提交体，全部 Optional + 默认 null。**额外多一个** `amend_reason: String?`（修改理由，后端只写进 audit 履历给老师看，不覆盖 `reason`）。
- 后端用 `model_dump(exclude_none=True)`：只更新非 null 字段。Android 序列化时**必须排除 null 字段**（别把没改的字段当 null 发上去），否则会误清空。kotlinx.serialization 用 `encodeDefaults = false`，Moshi 默认就跳 null。
- 修改届提交后后端会把承认链全员重置为 pending。
- 注：出租车预约目前是 create-only（仅新建时填），修改届不改 taxi（待办 N-004）。

#### 学習

**`StudyAbsenceRequestOut`**（欠席届响应）：
- `id: UUID`、`student_id: UUID`、`target_date: String`（`"2026-05-03"`）、`period: String`（`"first_half"` / `"second_half"` / `"full"`）、`reason: String`、`submitted_at: Date`、`status: String`（`"pending"` / `"approved"` / `"rejected"`）、`decided_by: UUID?`、`decided_at: Date?`、`comment: String?`
- 请求体 `AbsenceRequestBody`：`target_date`、`period`、`reason`（必填 1–2000 字）

**`StudyOnlineRequestOut`**（在线学习申请响应）：
- `id: UUID`、`student_id: UUID`、`reason: String`、`period_from: String`、`period_to: String`、`weekly_schedule: [String: [[String: String]]]`（周课表，嵌套结构：键是星期，值是该天若干时段，每时段是一组键值对）、`contract_ref: String?`、`contract_file_name: String?`、`contract_mime: String?`、`contract_size: Int?`（这三个契約書文件信息非 null 表示已上传，**不含服务器物理路径**——安全考量，看文件内容要另调 GET `.../contract`）、`submitted_at: Date`、`status: String`（`"pending"` / `"approved"` / `"rejected"` / `"revoked"`）、`decided_by: UUID?`、`decided_at: Date?`、`comment: String?`
- 请求体 `OnlineRequestBody`：`reason`、`period_from`、`period_to`、`weekly_schedule`、`contract_ref?`

> **契約書上传是两步**：先 POST 申请拿到 `id`，再 POST `/online-requests/{id}/contract` 把文件 multipart 上传。Android 实现 multipart：字段名 `file`，带 `filename` 和 `Content-Type`（mime 类型）。iOS 还做了文件名安全处理（去掉换行符 `\r` `\n` 和双引号 `"`，否则会破坏 multipart 结构）——Android 也要清理文件名。

#### 宿舍生活类申請

**`DormEventProposalOut`**（行事企画响应）：
- `id: UUID`、`proposer_id: UUID`、`team_name: String?`、`title: String`、`held_at: Date`、`place: String`、`expected_count: Int`、`target: String`、`purpose: String`、`content: String`、`risk_solution: String`、`expected_cost: String`、`note: String?`、`submitted_at: Date`、`result: String`（`"pending"` / `"approved"` / `"approved_conditional"` / `"resubmit"` / `"rejected"`，注意这里叫 `result` 不是 `status`）、`decided_by: UUID?`、`decided_at: Date?`、`comment: String?`
- 请求体 `EventProposalBody`：`team_name?`、`title`、`held_at`（datetime 字符串）、`place`、`expected_count: Int`、`target`、`purpose`、`content`、`risk_solution`、`expected_cost`、`note?`

**`FridgePurchaseRequestOut`**（冷蔵庫購入届响应）：
- `id: UUID`、`student_id: UUID`、`contact_phone: String`、`contact_wechat: String?`、`product: String`（`"A"` / `"B"`）、`submitted_at: Date`、`delivered_sign: String?`、`status: String`（`"pending"` / `"ordered"` / `"delivered"` / `"rejected"`）、`decided_by: UUID?`、`decided_at: Date?`、`comment: String?`
- 请求体 `FridgePurchaseBody`：`contact_phone`、`contact_wechat?`、`product`

**`ItemPossessionRequestOut`**（物品所持願响应）：
- `id: UUID`、`student_id: UUID`、`room_no: String`、`item: String`、`reason: String`、`guardian_name: String`、`submitted_at: Date`、`status: String`（`"pending"` / `"approved"` / `"rejected"`）、`decided_by: UUID?`、`decided_at: Date?`、`comment: String?`
- 请求体 `ItemPossessionBody`：`room_no`、`item`、`reason`、`guardian_name`

#### 巴士便 / 行事预定

**`BusRouteOut`**（巴士便单条）：
- `id: UUID`、`kind: String`（`"daily_commute"`=平日上下学班车 / `"dorm_special"`=寮生特別運行）、`name: String`、`direction: String`、`schedule_at: Date`（出发时刻，完整 datetime，前端拆成日期+时分显示）、`arrival_at: Date?`（到达时刻，空港便等才有）、`visible_to: String`（`"all"` / `"dorm_only"` / `"men"` / `"women"`）、`note: String?`、`deprecated: Bool`、`created_by_teacher_id: UUID`、`created_at: Date`、`updated_at: Date?`
- 列表包装 `BusRouteListOut`：`items: [BusRouteOut]`

**`EventOut`**（行事预定单条）：
- `id: UUID`、`title: String`、`category: String`（后端枚举：`"学校行事"` / `"寮行事"` / `"外部"` / `"その他"`）、`event_date: String`（`"2026-04-23"`，纯日期保字符串，别解成日期对象否则崩）、`start_at: Date?`（开始时刻，带时分时区可空）、`end_at: Date?`、`description: String?`、`created_by_teacher_id: UUID`、`created_at: Date`、`updated_at: Date?`
- 列表包装 `EventListOut`：`items: [EventOut]`

#### 老师公告

**`AnnouncementBrief`**（列表项，注意这组用驼峰字段名 + `CodingKeys` 映射蛇形线缆名）：

| Kotlin 字段 | 线缆名（JSON key） | 类型 |
|---|---|---|
| id | `id` | UUID |
| title | `title` | String |
| bodySummary | `body_summary` | String |
| scope | `scope` | String（`"all"` / `"male"` / `"female"`） |
| authorTeacherId | `author_teacher_id` | UUID |
| authorTeacherName | `author_teacher_name` | String |
| createdAt | `created_at` | Date |
| updatedAt | `updated_at` | Date |
| isRead | `is_read` | Bool |
| replyCount | `reply_count` | Int |

**`AnnouncementListResponse`**：`items: [AnnouncementBrief]`

**`AnnouncementDetail`**（详情）：`id`、`title`、`body`（全文）、`scope`、`author_teacher_id`、`author_teacher_name`、`created_at`、`updated_at`、`replies: [AnnouncementReplyOut]`

**`AnnouncementReplyOut`**（回复条目）：`id`、`author_kind`（`"student"` / `"teacher"`）、`author_id`、`author_name`、`body`、`created_at`

**`AnnouncementUnreadCount`**：`unread_count: Int`（线缆名蛇形）

#### 点呼

**`RollCallCheckinBody`**（提交请求体）：
- `card_uid: String?`（路径 A = NFC 卡 UID；路径 B 时 null）、`student_id: UUID?`（路径 B / manual 时学生自身 ID）、`idempotency_key: String?`（路径 B 客户端生成 UUID 防重复提交）、`status_source: String`（`"auto_nfc"` / `"manual_checkin"`）、`ts_local: Date?`（客户端时刻，null 时后端用服务器时间）、`path_hint: String?`（`"A"` / `"B"` / `"manual"`）

**`RollCallEventOut`**（提交响应）：
- `id: UUID`、`student_id: UUID`、`base_status: String`（`"present"` / `"late"` / `"absent"` / `"exempt_range"`）、`status_source: String`（`"auto_nfc"` / `"manual_checkin"` / `"teacher_override"` / `"auto_settle"`）、`checked_in_at: Date`、`path_type: String?`（`"A"` / `"B"` / `"manual"`）

> 说明：学生端实际只用 POST checkins（路径 B = iPhone tap 静态标签）。后端其他 GET 点呼端点（today/sessions、board、summary）是教师端用，学生 Android 不用接。

#### kind 编码映射（`ApplyKindMapper.swift`）

iOS 内部用英文 enum 管理申请类型，只在 API 收发时转成日文。Android 若同样用内部英文枚举，要建同样的映射：

| iOS 内部码 | 后端日文（API 的 `kind` 字段值） |
|---|---|
| `stay` | `外泊` |
| `holiday` | `帰省` |
| `returncountry` | `帰国` |
| `study_absence` | `学習欠席` |

> 不过出寮届提交体（`KisheiCreateBody` 等）的 `kind` 字段是**直接硬编码日文**（`"帰省"`/`"外泊"`/`"帰国"`），不经映射；映射器主要用于 iOS 内部状态管理。Android 实现时直接发日文 `kind` 即可，避免出错。

---

### ⑤ 关键日语文案（注册表单本地校验错误，UI 直接显示）

来自 `StudentAccountCreateBody.validate()`，Android 校验函数逐条照抄：

- 氏名空 →「`氏名を入力してください`」
- 氏名超 100 →「`氏名は 100 文字以内で入力してください`」
- 氏名假名超 100 →「`氏名カナは 100 文字以内で入力してください`」
- 性别未选 →「`性別を選択してください`」
- 学年非 2 位数字 →「`学年は 2 桁の数字で入力してください`」
- 班级非 2 位数字 →「`クラスは 2 桁の数字で入力してください`」
- 座席非 2 位数字 →「`座席番号は 2 桁の数字で入力してください`」
- 部屋番号 <3 字 →「`部屋番号は 3 文字以上で入力してください`」
- 部屋番号 >8 字 →「`部屋番号は 8 文字以内で入力してください`」
- 寮号非法 →「`寮号が不正です`」
- 邮箱超 200 →「`メールアドレスは 200 文字以内で入力してください`」
- 电话超 32 →「`電話番号は 32 文字以内で入力してください`」
- 密码不在 6–128 →「`パスワードは 6〜128 文字で入力してください`」
- 注册码非 6 位数字 →「`登録コードは 6 桁の数字で入力してください`」

---

### ### Android 对齐要点

Android 目前**完全没有网络层**（只有 `MockData.kt` 本地假数据），整套要从零建。建议结构对照 iOS 的 `Foundation/Network/` 一一映射：

1. **HTTP 客户端单例**（对应 `APIClient.swift`）：
   - 用 Retrofit + OkHttp（Android 主流）或 Ktor Client。base url 按构建类型切：debug `http://localhost:8000`、release `https://api.tomoshibi.cc`（用 `BuildConfig` 区分），允许环境变量/构建参数覆盖。
   - OkHttp 加一个 Interceptor（拦截器，统一给每个请求加头），自动注入 `Authorization: Bearer <token>`（token 非空时）。
   - 超时设 15 秒。
   - 序列化器选 Moshi 或 kotlinx.serialization。**关键配置**：(a) 解码时忽略响应里多出来的未知字段（后端会发 iOS 不接的 `registered_at` 等）；(b) 编码请求体时**跳过 null 字段**（修改届 `ApplicationUpdateBody` 必须，否则误清空）。

2. **日期适配器**（对应 `decodeISO8601Date`）：写一个自定义日期反序列化器，先试带小数秒的 ISO8601 格式、失败退到不带小数秒的。datetime 解成 `Instant`/`OffsetDateTime`；纯日期（`yyyy-MM-dd`）和纯时刻（`HH:mm:ss`）字段**全部保留成 `String`**，别解成日期类型。

3. **状态码 + 错误处理**（对应 `APIError` + `decodeResponse`）：
   - 建一个 `sealed class ApiError`：`Network` / `Decode` / `Unauthorized` / `Unprocessable(msg)` / `Server(code, msg)` / `Unknown`。
   - 204 / 空 body 特判当成功（DELETE 接口）。
   - 401 → 抛 `Unauthorized` + 触发清 token、跳登录。
   - 422 → 用 `extractMessage` 抽后端 message（两种错误体形态都试）→ 抛 `Unprocessable(msg)`。
   - 建一个 `ApiErrorPresenter`（对应 `APIErrorPresenter.swift`）把异常转成日语提示文案，全 App 共用，文案逐条照抄上面表格。

4. **token 持久化**（对应 `KeychainService.swift`）：Android 用 EncryptedSharedPreferences（Jetpack Security 加密的偏好存储，等价于 iOS Keychain 的安全存储角色），别用明文 SharedPreferences。三操作 `save` / `load` / `delete`，app 启动 `load` 实现自动登录。

5. **端点包装**（对应 `Endpoints/*.swift`）：每组功能一个 Retrofit interface 或一组挂起函数（`AuthApi` / `ApplicationsApi` / `StudyApi` / `DormLifeApi` / `BusApi` / `EventsApi` / `RollCallApi` / `AnnouncementsApi` / `StudentsApi` / `DisciplineApi`），方法签名、路径、请求/响应类型全部照上面的端点清单。路径里的 UUID 转**小写**再拼。

6. **数据模型**（对应 `NetworkModels.swift` + 各请求体）：每个 `struct` 建对应 Kotlin `data class`，字段命名 + 可空性 + 类型逐字段对齐。`AnyJSON` 那种松散 JSON 字段（`stay_locations` / `meals_skip` / audit `payload`）用 `Map<String, Any?>` 或自定义薄 wrapper 接。**所有非空字段一个都不能漏**，否则整段解码失败。

7. **multipart 文件上传**（对应 `APIClient.upload`）：契約書上传用 OkHttp 的 `MultipartBody`，字段名 `file`，带 filename 和 mime 的 `Content-Type`。文件名先清理掉 `\r` `\n` `"`。

8. **本地表单校验**（对应 `validate()`）：注册表单在发请求前做完整本地校验，错误文案照抄 ⑤ 节日语原文。

---

I now have full coverage of the auth/registration area. Writing the alignment spec.

## 一、登录 / 注册 / 账号 模块（auth-registration）

> 真值来源（iOS）：`Features/Auth/AuthStubs.swift`（2163 行，登录+注册全部 10 个画面）、`Foundation/AppState/AppStore.swift`（令牌持久化 / 注册累积器 / 锁定升级 / loadMe）、`Foundation/Network/Endpoints/AuthAPI.swift`（登录 / 注册 / 删号 端点）、`Foundation/Network/KeychainService.swift`（令牌加密存储）、`Foundation/Routing/RouterStore.swift` + `Route.swift`（自管导航栈）。
> 共享组件真值：`Foundation/Components/Field.swift`（`Field` / `TField` / `TArea`）、`PrimaryButton.swift`（`PrimaryButton` / `GhostButton`）、`UIAtoms.swift`（`Avatar`）。
> 颜色统一走 `T.*` token（`Foundation/Theme/TTokens.swift`），版本号走 `AppVersionTag.full`。
> **「DEMO」= 演示版独立编译开关**（Swift 的 `#if DEMO`）。Android 要做出等价的「演示版 vs 生产版」双行为，建议用 `BuildConfig.DEMO`（Gradle 的 `buildConfigField "boolean"`）做 build variant，不要把演示后门硬编码进生产 APK（itsuki 5-28 拍板，否则是安全漏洞）。

---

### 1. 画面一覧（10 屏，全部在 Auth 模块）

| # | 屏名（iOS struct） | Route case | 干嘛 |
|---|---|---|---|
| 1 | `SplashView` | `.splash` | 火焰 logo 闪屏，2.2 秒后按有无令牌分流 |
| 2 | `OnboardingView` | `.onboarding` | 3 页横滑引导（当前启动流程已不强制经过，但屏要做出来）|
| 3 | `RegisterStep1View` | `.registerStep1` | 基本情報：头像 / 氏名 / 性别 / 学生区分 / 生年月日 / 学年 / 组 / 出席番号 / 部屋番号 + 账号番号预览 |
| 4 | `RegisterStep2View` | `.registerStep2` | 点呼区分（一般寮生 / サッカー部 二选一卡片）|
| 5 | `RegisterStep3View` | `.registerStep3` | 連絡先：メール + 電話 |
| 6 | `RegisterStep4View` | `.registerStep4` | パスワード設定（密码 × 2 + 不可自助改密警告）|
| 7 | `RegisterStep5View` | `.registerStep5` | 認証コード（教师生成 6 桁数字，提交时调后端建号）|
| 8 | `RegisterDoneView` | `.registerDone` | 注册成功（绿勾动画 + 账号番号大字展示）|
| 9 | `LoginView` | `.login` | 登录（番号 / メール 两 tab + 演示 magic 登录）|
| 10 | `LockoutView` | `.lockout` | 锁定页（倒计时 + 锁定升级提示 + 永久锁分支）|
| 11 | `PwResetView` | `.pwreset` | 找回密码说明（App 内不能改、引导找寮監）— 当前登录页入口已隐藏，但屏保留 |

弹窗（非独立屏）：账号删除有 2 个系统 `alert`（在 `MyPage/MyPageStubs.swift` 的 `MySettingsView`，删号入口归本模块管）：① 删除确认 alert ②删除失败 alert。

---

### 2. 各屏布局结构（从上到下）

#### 2.1 SplashView（闪屏）
- **背景**：竖直渐变，白 → `0xF4F7F8`（极浅灰），全屏。
- **居中纵向布局**：`Spacer` → 白色圆角方卡（168×168，圆角 32，双层阴影）内嵌火焰图 `TomoshibiFlame`（120×120，`scaledToFit`）→ 间距 36 → 文案块：`Tomoshibi · 灯火`（18sp bold，字距 2.2，色 `T.primaryDk`）+ 版本号 `AppVersionTag.full`（11sp 等宽，色 `T.inkMute`）→ `Spacer` × 2（卡片整体偏上 42% 位置）。
- **动画**：进入时整块 `opacity` 0→1，`easeIn` 0.6 秒。
- **停留**：2.2 秒（`2_200_000_000` 纳秒）后分流。

#### 2.2 OnboardingView（引导）
- **顶部右上**：`スキップ` 文字按钮（14sp medium，色 `T.inkSub`）。
- **中部**：横滑分页（`TabView .page`，不显示系统圆点），3 张 slide，每张 = 圆角 36 渐变方块（240×240，左上→右下渐变 + 阴影）内嵌一个 SF Symbol 图标（120sp）→ 间距 44 → 标题（28sp bold，`T.ink`）→ 副标题（15sp，`T.inkSub`）。
- **底部**：自绘指示点（当前点 24×8 圆角胶囊色 `T.primary`，其余 8×8 色 `T.inkFaint`，间距 8，切换 `easeInOut` 0.2 秒动画）→ `PrimaryButton`（非末页文案`次へ`/末页`始める`）。
- **3 张 slide 内容**（图标 + 渐变需照抄）：
  - slide1 图标 `wave.3.right.circle.fill`，标题`タッチで点呼`，副`NFC にかざすだけ`，渐变 `0xE8F4F6→0xA8DCE2`，图标色 `T.primary`
  - slide2 图标 `square.and.pencil.circle.fill`，标题`申請はアプリで`，副`外泊・帰省・タクシー`，渐变 `0xFDF4E1→0xFFE9B5`，图标色 `T.warnDeep`
  - slide3 图标 `sparkles`，标题`寮生活をひとつに`，副`バス・活動・荷物`，渐变 `0xE3F1EA→0x8BC6A3`，图标色 `T.okDeep`

#### 2.3 注册 5 步通用骨架
每个注册屏都是：`RegisterHeader`（顶部）→ `RegisterProgress`（进度条）→ `ScrollView`（表单主体）→ footer（底部按钮）。背景 `T.paper`。
- **`RegisterHeader`**：高 48，左侧自绘返回箭头（按钮 36×36，点击 `router.back()`）+ 居中标题（17sp bold，`T.ink`）+ 右侧 36×36 占位（让标题真居中）。
- **`RegisterProgress`**：上行 = 左`アカウント作成`（13sp semibold，`T.inkSub`）+ 右`N / 5`（12sp 等宽，`T.inkMute`）；下行 = 进度条（底槽色 `T.hair` 高 4，填充 = `T.accent→T.primary` 横向渐变，宽 = 总宽 × step/5，`easeInOut` 0.4 秒动画）。横向 padding 24。
- **footer 两种**：
  - `footerSingle`（仅 Step1 用）：顶部 0.5pt 分隔线 + 单个 `PrimaryButton`（`次へ`，`enabled=canNext`）。
  - `footerDouble`（Step2-5 用）：分隔线 + 一行两按钮（左 `GhostButtonFull` 描边款`戻る` + 右 `PrimaryButton`），间距 10。

#### 2.4 RegisterStep1View（基本情報，最复杂屏）
`ScrollView` 内纵向（间距 18，横 padding 24），8 个 `Field` 区块 + 1 个账号预览：
1. **アバター**：水平排列。左 = 64×64 圆形头像（默认 = `Avatar(letter:)`，字母圆头像；有 AI 生成 URL 时显示图片）。右 = 纵向 3 按钮：`写真を選択`（浅灰填充描边，38 高）/ `デフォルトを使う`（青色淡填充，semibold）/ `AI で生成`（仅 `supportsImagePlayground=true` 时显示 — 当前硬编码 `false`，Android 直接不做这个按钮）。
2. **氏名**（`Field` required，hint `日本人は漢字、留学生はカタカナで入力してください`）：`TField`。
3. **性別**（required，hint `性別により自動的に男寮 / 女寮に配属されます`）：两个内联 radio chip `男` / `女`（选中 = `T.primary` 淡填充 + `T.primary` 1.5pt 描边 + 文字加粗变青）。
4. **学生区分**（required）：两 chip `一般生`(`false`) / `留学生`(`true`)，同 radio 样式。
5. **生年月日**（required）：内联滚轮日期选择器（日语 locale `ja_JP`，高 160，上限今天，灰底圆角框）。
6. **学年**（required）：一行 6 个等宽 chip `中1 中2 中3 高1 高2 高3`（选中 = `T.primary` 实心填充 + 白字加粗）。
7. **組**（required）：两 chip `A組` / `B組`。
8. **出席番号**（required）：数字键盘 `TField`。
9. **部屋番号**（required）：`TField`，实时过滤（只留字母数字、转大写、最多 4 桁）。
10. **アカウント番号 プレビュー**：浅青底圆角框，左`アカウント番号`标签 + 右 6 桁大字（22sp bold 等宽 `T.primary`，字距 2），随上面输入实时变化。

**账号番号算法**（必须照抄）：6 桁 = 学年码(2) + 组码(2) + 出席番号(2)。
- 学年码：中1=`01` 中2=`02` 中3=`03` 高1=`04` 高2=`05` 高3=`06`，未选=`00`。
- 组码：A=`01` B=`02`，未选=`00`。
- 出席番号：`String.format("%02d", n)`，n 取 0–99（`max(0,min(99,…))`）。
- 例：高3 + B + 18 → `060218`。

**canNext 放行条件**（8 字段全满足才能下一步）：氏名非空 + 性别∈{male,female} + 学年非空 + 组非空 + 出席番号 ∈ 1–99 + 部屋番号非空。

#### 2.5 RegisterStep2View（点呼区分）
`ScrollView` 内：标题 `あなたの点呼区分`（15sp bold）→ 2 张可选大卡片（`catCard`）。每卡：左上区分名（16sp bold）+ 右上 22×22 自绘 radio 标记（选中 = 6pt 厚 `T.primary` 圆环 + 中心白圆点；未选 = 1.5pt `T.inkFaint` 细圆环）→ 下方时刻明细（12.5sp，`T.inkSub`）。选中卡 = `T.primary` 1.5pt 描边 + 极淡青底 + 阴影。
- 卡1 `一般寮生`，明细`平日: 朝 7:40 / 晩 22:00  ·  土日: 朝 8:50 / 晩 20:00`，值 `regular`
- 卡2 `サッカー部`，明细`平日: 朝 7:10 / 晩 22:00  ·  土日: 朝 7:10 / 晩 20:00`，值 `soccer`
- 提交时把 UI 值映射成日语后端串：`soccer→サッカー部`，其余→`一般寮生`。
- 注意：日文用「晩」不是「晚」（照抄）。

#### 2.6 RegisterStep3View（連絡先）
两个 `Field`（间距 18）：
- **メールアドレス**（required，hint `学校のメールアドレスでも、ご自身のメールアドレスでも登録できます。認証メールは送信されません（将来のパスワードリセット時の確認用です）`）：邮箱键盘 `TField`，placeholder `example@email.com`。
- **電話番号**（required，hint `寮監があなたに連絡する場合に使います`）：电话键盘 `TField`，placeholder `090-1234-5678`。
- footer 下一步条件：邮箱与电话都非空。

#### 2.7 RegisterStep4View（パスワード設定）
- **琥珀色警告条**（顶部）：左 24×24 橙圆内白色 `!` + 右纵向（标题`ご注意ください` 12.5sp bold 色 `T.warnDeep` + 正文`パスワードは自分では変更できません。変更には寮監への連絡が必要です。入力時は慎重にお願いします。`）。底 `T.warnBg`，描边 `T.warn` 25% 透明。
- **パスワード**（required，hint `8 文字以上`）：`TField secure=true`。
- **パスワード（確認）**（required）：`secure`，不一致时下方红字 `パスワードが一致しません`。
- canSubmit：两密码都非空且相等。footer 下一步文案 `次へ`，跳 Step5。

#### 2.8 RegisterStep5View（認証コード）
- 琥珀警告条（同 Step4 样式），正文`教員から発行された 6 桁の認証コードを入力してください。コードは発行から 5 分以内のみ有効です。`
- 6 桁数字大字输入：上方标签`認証コード（6 桁）`（13sp semibold）+ 居中超大输入框（28sp heavy 等宽，字距 8，数字键盘，placeholder `000000`，实时过滤只留数字、最多 6 位、输入变动清错误）。
- 错误条：`errorMsg` 非空时显示红字红底圆角框（文案来自后端 422）。
- footer：`戻る` + `アカウント作成完了`（加载中变`送信中…`，`enabled = canSubmit && !isLoading`，canSubmit = 恰好 6 位数字）。

#### 2.9 RegisterDoneView（注册完成）
全屏居中：`Spacer` → 100×100 绿色渐变圆（`0x8BC6A3→0x4A9478` + 绿阴影）内白色对勾（`CheckIcon`，放大 2.4 倍）→ 欢迎文`ようこそ、{姓名} さん`（22sp bold）→ 副`アカウントが作成されました`（13sp `T.inkSub`）→ 账号面板（青色渐变 `0xE8F4F6→0xA8DCE2` 圆角 20）：小标题`あなたのアカウント番号`（11sp bold 字距 2 大写 `T.primaryDk`）+ 6 桁大字（44sp heavy 等宽 `T.primaryDk`，自动缩放单行）+ 说明`次回からはこの 6 桁番号\nまたはメールアドレスと\nパスワードでログインしてください` → `Spacer` → `始める` 按钮（跳 `.home`）。
- **动画**：绿勾 `scaleEffect` 0.2→1 + `opacity` 0→1，`spring(response:0.4, damping:0.7)`。
- 进入时调 `app.resetRegistrationDraft()` 清注册累积器。

#### 2.10 LoginView（登录）
- **背景**：竖直渐变 `T.pearl→0xE4EBEC`。
- 顶部留白 40 → 居中标题块（`Tomoshibi` 28sp bold `T.primaryDk` 字距 1.12 + `灯火 · ログイン` 12sp `T.inkMute` 字距 1）→ 间距 36。
- **mode tab**（2 段切换）：容器底 `T.pill` 圆角 12 padding 3，两 tab `番号` / `メール`（激活 = `T.paper` 底 + `T.primary` 字 + 阴影；非激活 = 透明 + `T.inkSub`），各高 40。
- **字段区**：番号 mode 显示`アカウント番号`（数字键盘 `TField`，20sp 等宽字距 2）；メール mode 显示`メールアドレス`（邮箱键盘）。下方恒显`パスワード`（`secure`）。
- **登录按钮**：`PrimaryButton`，文案 `ログイン`（加载中 `ログイン中…`），`disabled(isLoading)`。
- **底部链接行**：左`新規登録`（跳 `.registerStep1`）。右侧`パスワードを忘れた`入口在 v1.0 上架版**已隐藏**（避免 Apple 死按钮 reject），Android 也不要做这个链接。
- 演示版预填：番号 `060217`、邮箱 `demo@example.com`、密码 `12345678`；生产版三者全空。

#### 2.11 LockoutView（锁定）
全屏居中：100×100 红圆（`T.dangerBg`）内 `LockIcon`（放大 1.6 倍，色 `T.danger`）→ 标题（非永久`ログインに失敗しました` / 永久`アカウントがロックされました`，20sp bold）。
- **非永久分支**：MM:SS 倒计时大字（48sp bold 等宽 `T.danger`）+ 说明`セキュリティのため、しばらくログインできません。` + 琥珀提示框（当前阶段 `現在 N 回目のロック（{label}）` + 若有下一阶段 `次回失敗で {next} ロックに上がります`）。倒计时归零 → `router.replace(.login)`。
- **永久分支**（失败 ≥6 次）：显示`永久`大字 + `試行回数の上限を超えました。\n寮監にご連絡ください。`，不计时。

#### 2.12 PwResetView（找回密码说明）
`RegisterHeader` 标题`パスワードをリセット` → 正文`パスワードのリセットは App 内では行えません。寮監に直接お声がけください。寮監がシステム後台で手動でリセットします。`（15sp，行距宽）→ 信息框（极淡青底圆角，左 `ℹ` + 文`リセット後、新しいパスワードが寮監から伝えられます`）→ 底部 `戻る` 按钮（跳 `.login`）。
（当前登录页入口隐藏 = 用户走不到这屏，但屏要做出来备用。）

#### 2.13 账号删除（在设置页 `MySettingsView` 末尾，归本模块）
- **入口 section**：小标题`アカウント` → 红色行`アカウントを削除`（删除中`削除中…`，14sp semibold 红字，右 `chevron.right`）→ 下方灰字`削除すると元に戻せません。`
- **确认 alert**：标题`アカウントを削除しますか？`，按钮`キャンセル`(cancel) / `削除する`(destructive)，正文`削除すると元に戻せません。点呼履歴・申請履歴・プロフィール情報がすべて閲覧できなくなります。`
- **失败 alert**：标题`削除に失敗しました`，`OK` 关闭。
- 删除成功 → `app.authToken = nil`（触发清 Keychain + 登出复位）→ `router.replace(.login)`。

---

### 3. 用到的共享组件

| 组件 | iOS 文件 | 本模块怎么用 |
|---|---|---|
| `Field` | `Field.swift` | 注册全部表单字段的 label+hint+error+required(*) 包裹 |
| `TField` | `Field.swift` | 单行输入：高 48 / 圆角 12 / 底 `T.pearl` / 描边聚焦变 `T.primary`；支持 `secure` / `keyboard` |
| `PrimaryButton` | `PrimaryButton.swift` | 高 52 / 圆角 16 / 径向青渐变 / `enabled=false` 时变 `T.inkFaint` 灰 |
| `GhostButtonFull` | `AuthStubs.swift`(私有) | `戻る` 描边款全宽按钮（52 高，圆角 16，`T.hair` 描边）|
| `Avatar` | `UIAtoms.swift` | Step1 字母圆头像 + RegisterDone 不用 |
| 自绘图标 | `AuthStubs.swift`(私有) | `CheckIcon`/`LockIcon`/`BackChevronIcon`/`PhoneTapIcon`/`MailIcon`/`CalendarIcon`/`FlameShape` — Canvas 画的，Android 用 `Canvas` 或矢量资源等价复刻 |
| `RegisterHeader`/`RegisterProgress` | `AuthStubs.swift`(私有) | 注册屏通用头 + 进度条 |

本模块**不用** GlassSheet / FlowLayout / BottomNav（登录注册流没有底部 tab，没有玻璃 sheet）。

---

### 4. 导航（怎么进 / 返回 / tab）

iOS 用自管栈 `RouterStore`（不用系统 NavigationStack），三个核心方法：
- `go(route)` = 入栈（前进，可 `back()` 回退）。
- `replace(route)` = 清栈只留这一个（跳 tab 根 / 登录 / 主页用，回不去）。
- `back()` = 出栈一级（`RegisterHeader` 返回箭头调它）。

本模块导航链：
```
splash ──令牌存在──▶ home
       └─无令牌────▶ login
login ──新規登録──▶ registerStep1 ─▶ Step2 ─▶ Step3 ─▶ Step4 ─▶ Step5 ─▶(replace) registerDone ─▶(replace) home
login ──登录成功──▶(replace) home
login ──401失败──▶(go) lockout ──倒计时到0──▶(replace) login
注册各步返回箭头：router.back() 回上一步（栈回退）
onboarding ──スキップ/始める──▶ registerStep1
删号成功 ──▶(replace) login
```
- 跨步前进用 `router.go(.registerStepN)`（保留栈方便 `戻る`）；Step5→Done 和 Done→home 用 `replace`（不让用户回到注册流）。

**Android 现状**：`MockData.kt` 桩 + Compose 只有 UI，没有这套自管栈。Android 建议用 `NavController`（Jetpack Navigation Compose）或一个等价的 `RouterViewModel` 持有 `mutableStateListOf<Route>` 栈，实现 `go/replace/back/jump`。Route 用 `sealed class`（对应 iOS 的 `enum Route`，含带参 case 如 `RegisterStepN` 无参、`homeAnnouncementDetail(id)` 带参）。注册流必须能 `back` 回上一步、`replace` 到 done/home。

---

### 5. 数据源（调哪个 API / 读哪个 mock）

| 动作 | iOS 端点 / 方法 | 请求 | 响应 |
|---|---|---|---|
| 学生登录 | `AuthAPI.loginStudent` → `POST /api/v1/sessions/student` | `{student_no, password}` | `TokenOut{access_token, token_type, expires_in}` |
| 学生注册建号 | `AccountsAPI.createAccount` → `POST /api/v1/accounts` | `StudentAccountCreateBody`（见下）| `StudentAccountCreateResponse{access_token, token_type, expires_in, student}` |
| 删除账号 | `AccountsAPI.deleteMyAccount` → `DELETE /api/v1/accounts/me` | 无 | 204 No Content |
| 拉当前学生 | `StudentsAPI.me` → `GET /api/v1/students/me` | 无（身份取自令牌）| `StudentMeOut`（身份字段）|
| 当月扣分汇总 | `DisciplineAPI.mySummary` → `GET /api/v1/discipline/me/summary` | 无 | `{month, total_points, late_count, absent_count}` |

**`StudentAccountCreateBody` 字段**（与后端 `StudentAccountCreateIn` 一对一，含校验上下限，Android 必须照抄字段名 + 校验）：
```
name(必填,≤100) name_kana(可空,≤100) birthday("yyyy-MM-dd"可空)
gender("male"|"female") grade_code(^\d{2}$) class_code(^\d{2}$) seat_no(^\d{2}$)
category("一般寮生"等日语串) room_no(3–8字符,如"M101") dorm_unit(1|2|4) is_overseas(Bool)
email(可空,≤200) phone(可空,≤32) password(6–128) registration_code(^\d{6}$)
```
- **`room_no` 前缀规则（关键，曾出 MM101 回归 bug）**：输入框只让填裸房号（如`101`/`A5`）。拼前缀只在 `RegistrationDraft.computedRoomNo` 一处做：房号首位已是字母（`A5`）→ 不加前缀；纯数字（`101`）→ 男`M`女`W` → `M101`。前缀绝不能加两次。
- **`dorm_unit` 推导**：女生恒 4；男生房号首位是`2`→2 寮，否则 1 寮。
- 注册发请求前先跑客户端 `validate()`（返回 nil=OK，否则日语错误串），校验不过直接抛 422、不发请求。

**演示版（DEMO）数据**：iOS 用 `SEED.user`（`Foundation/Seed/`）当假人；登录 magic `060217`/`12345678` 跳过 API 直进主页；注册 Step5 认证码预填`000000`、提交跳过后端直接进 done。Android 对应读 `MockData.kt` 假人，演示分支同样跳过网络。

---

### Android 对齐要点

**Android 当前 = 只有 UI 桩 + `MockData.kt` 假数据，没有任何网络层、没有令牌持久化、没有锁定升级、没有注册累积器。要从零补齐下面全部。**

**A. 网络层（最大缺口，先建）**
- 建一个 `AuthApi` / `AccountsApi` / `StudentsApi`（Retrofit interface 或等价），端点路径 / 请求体字段 / 响应字段严格照上面表抄。请求体字段名用 snake_case（`student_no` / `grade_code` / `room_no` / `registration_code`），别用 camelCase。
- 响应 JSON key 是 snake_case，Kotlin data class 用 `@SerializedName`（Gson）或 `@Json(name=...)`（Moshi）映射成 camelCase 属性。`TokenOut`/`StudentAccountCreateResponse` 都含 `access_token`/`token_type`/`expires_in`。
- 统一的 `APIError` 分类要对齐 iOS：`unauthorized`(401) / `unprocessable(msg)`(422，把后端日语 message 抽出来) / `network`。登录 401→锁定，422→toast 后端文案。

**B. 令牌持久化 + 自动登录（对应 KeychainService + AppStore.init）**
- iOS 把 JWT 存 iOS Keychain（加密）。Android 等价 = `EncryptedSharedPreferences`（Jetpack Security，AES 加密）存 token，**不要用明文 SharedPreferences**（理由同 iOS：明文易被 root 设备读）。service/account 标识可用固定 key `student.jwt`。
- 过期时刻（`expires_at` = 现在 + `expires_in` 秒）单独存普通 prefs（过期时刻不是机密）。
- App 启动时（`Application.onCreate` 或根 ViewModel init）：读 token → 若过期则删 token + 删过期记录 → 走登录页；未过期则恢复 token + 拉 `/students/me`（`loadMe`）。
- `authToken` 用 `MutableStateFlow<String?>`，设值时同步：写/删 EncryptedPrefs + 给 Retrofit 的 `Authorization: Bearer` 拦截器更新 + token 变 null 时清 currentUser/needsRenewal/复位 mock 假人/清公告缓存（对齐 iOS didSet 的全套清理）。
- 提供 `setAuthToken(token, expiresIn)`（存过期时刻 + 设 token）和直接 `authToken = null`（登出/删号用）。

**C. 注册累积器（对应 RegistrationDraft）**
- 建 `RegistrationDraft` data class（字段名照抄 §5 的 body + `room_no_suffix` 裸房号）放在一个跨 5 步共享的 ViewModel（`RegisterViewModel`，scope 到注册 nav graph，别每步各一个 VM）。
- 每步 onNext 把本步 `@State` 写进 draft；Step5 提交时用 draft 拼 body 调 `createAccount`。
- 把 `computedRoomNo`（M/W 前缀单点拼接逻辑）、`computedDormUnit`（寮号推导）、`birthdayString`（用 `Locale.US` + 公历格式化成 `yyyy-MM-dd`，防和历把年份写错）做成 draft 的派生属性，照抄 iOS 逻辑。
- 注册成功后 `resetRegistrationDraft()` 清空。

**D. 账号番号实时预览（Step1）**
- 把学年码/组码/出席番号映射表照抄（中1=01…高3=06，A=01 B=02，出席`%02d`）。用 Compose `derivedStateOf` 或 `remember(grade, classSuffix, seatNo)` 算 `computedAccount`，随输入实时刷新预览大字。
- `canNext` 8 字段校验照抄，控制底部按钮 enabled。

**E. 锁定升级（对应 AppStore 的 loginFailCount + lockoutDurations）**
- 阶梯照抄：失败 1=30 秒 / 2=1 分 / 3=5 分 / 4=30 分 / 5=1 时间 / 6+=永久。秒数数组 `[30,60,300,1800,3600]`，第 6 次起 `currentLockoutSeconds=null`=永久。
- `currentLockoutLabel` / `nextLockoutLabel` 日语标签照抄（`30 秒`/`1 分`/`5 分`/`30 分`/`1 時間`/`永久`）。
- `recordLoginFailure()`(+1) / `resetLoginFailures()`(归 0，登录成功调)。`loginFailCount` 用 StateFlow，LockoutView 据此渲染倒计时 vs 永久。
- 倒计时用协程 `while(sec>0){ delay(1000); sec-- }`（别用 iOS Timer 的直译），归零 `router.replace(login)`。

**F. 演示版双行为（对应 #if DEMO）**
- 用 `BuildConfig.DEMO`（Gradle build variant）替代 `#if DEMO`。演示 build：预填值（登录 `060217`/`demo@example.com`/`12345678`、注册各步预填、认证码 `000000`）+ magic 登录跳过 API + Step5 提交跳过后端直进 done。
- **生产 build 绝不能含这些后门分支**（itsuki 5-28 拍板：演示后门进生产 = 安全漏洞）。用 `if (BuildConfig.DEMO) { … }` 包住所有演示分支，确保 release variant 编译时整段不进 APK。

**G. 视觉一致性**
- 颜色全走 Android 侧的 `T.*` 等价 token（若 Android 还没建主题 token 表，要先建一份镜像 `TTokens.swift` 的 Compose `object T`，色值十六进制照抄如 `T.primary`/`T.primaryDk`/`T.pearl`/`T.paper`/`T.hair`/`T.warn`/`T.warnBg`/`T.warnDeep`/`T.danger`/`T.dangerBg`/`T.inkSub`/`T.inkMute`/`T.inkFaint`/`T.accent`/`T.okDeep`/`T.pill`）。
- 自绘图标（火焰/对勾/锁/返回箭头）用 Compose `Canvas` 复刻 iOS 的 path，或导出成 `VectorDrawable`。SF Symbols（onboarding 的 `wave.3.right.circle.fill` 等）Android 没有，需换成等价 Material 图标或自绘矢量。
- `PrimaryButton` 的径向青渐变（`Brush.radialGradient`）/ 52 高 / 圆角 16 / disabled 变灰、`TField` 的聚焦描边变青、`Field` 的 label+required 红星+hint/error 切换，都要做成 Compose 可复用 `@Composable`，对齐 iOS 像素规格。
- 日语 UI 文案逐字照抄本文档「」内原文（含`晩`不是`晚`、半角空格、`·` 分隔符），不要改写不要翻译。
- 版本号走统一常量（对应 `AppVersionTag.full`，Android 用 `BuildConfig.VERSION_NAME` + DEMO 后缀），当前 `v0.12.0` / 演示版 `v0.12.0-demo`。

---

I have everything needed to write a complete, build-faithful spec. Producing the Markdown section now.

---

## ホーム主页（Home / HomeView）

> iOS 真值文件：`03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift`（`HomeView` + `LifeTab` 部分，第 128～1157 行）。配套数据：`Foundation/Seed/SEED.swift`、`Foundation/Seed/SeedModels.swift`。配色：`Foundation/Theme/TTokens.swift`。对应截图 01 / 06。
>
> 本节只覆盖**主页本体**：问候行、減点 amber 卡（含点呼三态切换 + 学習模式）、5 张生活卡（次のバス便 / 宅配便 / 今週の活動 / リクエスト曲 / 遺失物）、学年更新横幅。各卡点击后跳转的「下级页面」（包裹一覧、巴士一覧、活動一覧 等）不在本节展开，只标出跳转目标。点呼弹窗 `RollcallSheet`、学習签到弹窗 `StudyCheckinSheet` 等弹窗归别的对齐节。

### 0. 配色与共享原子（Android 先建好这些再做卡片）

iOS 用 `T.*` 设计令牌（在 `TTokens.swift`），Android 要在 Compose 主题里建同名常量。本节要用到的颜色（十六进制）：

| 令牌名 | 十六进制 | 干嘛用 |
|---|---|---|
| `primary` | `#1F6B74` | 主色（深青）— 巴士图标 / 横幅按钮 / 强调字 |
| `accent` | `#5FBEC8` | 亮青 — 活動卡图标底 |
| `pearl` | `#EFF2F3` | 页面整体背景（米白） |
| `paper` | `#FFFFFF` | 卡片白底 |
| `ink` | `#0F1E22` | 主文字（近黑） |
| `inkSub` | `#56707A` | 副标题灰 |
| `inkMute` | `#93A4AC` | 更淡的灰（次要信息 / 箭头） |
| `inkFaint` | `#C4D0D5` | 最浅灰（遺失物色块兜底） |
| `hair` | `#0F1E22` @ 8% 透明 | 卡片 0.5pt 描边 |
| `danger` | `#C44848` | 红 — 未读 badge / 快递红 |
| `dangerBg` | `#FDE8E8` | 快递图标淡红底 |
| `warnBg` / `warnDeep` | `#FDF4E1` / `#7A4A0E` | 点呼 pill 暖色 |
| `okBg` / `okDeep` | `#E3F1EA` / `#2C6048` | 「時間内」绿 pill |

amber 减点卡专用色（写死在 `HomeStubs.swift`，不是令牌）：

- 减点卡文字深褐 `deepBrown = #5C3410`
- amber 渐变（左上→右下）：`#FFEFC2` → `#F4C677`(55%) → `#D99F3E`(100%)
- 红渐变（欠席态）：`#FFD6D0` → `#EF6A58`(55%) → `#C83B29`(100%)
- 进度条填充渐变：`#D99F3E` → `#B07A28`

**两个共享原子组件**（Android 建成可复用 Composable）：

1. **`HomeCard`**（5 张生活卡都用它）：白底，圆角 **18dp**，内边距 **14dp**，0.5pt `hair` 描边，双层阴影（`ink` 4% / 半径 2 / y偏移 1；`ink` 5% / 半径 14 / y偏移 4）。可整卡点击。Compose 用 `Card` + `Modifier.clickable`，圆角必须 18dp（不是 16）。
2. **`Ic.chevR(size)`**：右箭头 `›`（`chevron.right`），出现在每张卡右端，颜色 `inkMute`。Android 用 `Icons.Default.ChevronRight` 或矢量图。

### 1. 画面一覧

主页只有**一个滚动页面**（竖向 `ScrollView`），从上到下：

1. 问候行 greetingRow（含右上角铃铛按钮）
2. 学年更新「待更新」横幅 renewBanner（**条件显示** — 仅 `needsRenewal == true` 时出现）
3. 減点 amber 卡 pointsCard（内部按状态三态/学習模式切换内容）
4. LifeTab：5 张生活卡（バス / 宅配便 / 活動 / リクエスト曲 / 遺失物）竖向排列

页面整体背景色 `pearl`(`#EFF2F3`)。所有横向内边距：问候行左右 **20dp**，其余区块左右 **16dp**。

### 2. 布局结构（从上到下逐块）

#### 2.1 问候行 greetingRow

横向 `Row`，左文字 + 右铃铛，中间 `Spacer` 撑开。整块上内边距 14dp、下 6dp，左右 20dp。

- **左侧**（竖排两行，行距 3dp）：
  - 第 1 行问候：`「おかえり、{用户名} さん」`（意为「欢迎回来，XX 同学」）。字号 20、加粗、字距 0.2。用户名取 `displayUser.name`，演示数据是 `「リュウ イヒ」`，所以整句是 `「おかえり、リュウ イヒ さん」`。
  - 第 2 行日期：JST（日本时间）今天，格式 `「yyyy 年 M 月 d 日（曜日）」`，比如 `「2026 年 6 月 5 日（金）」`。字号 12、颜色 `inkMute`。**注意**：这是运行时实时生成的当天日期（`DateFormatter` locale=ja_JP, timeZone=Asia/Tokyo），不是写死字符串。
- **右侧铃铛按钮**：44×44 方块，圆角 14dp，白底 `paper`，0.5pt `hair` 描边，同 `HomeCard` 的双层阴影。中间放铃铛图标（`bell`，尺寸 22，色 `ink`）。
  - **未读 badge**：当未读数 `unread > 0` 时，右上角叠一个红色胶囊。最小宽 16、高 16，左右内边距 4，圆角胶囊，红底 `danger`，白字数字（字号 10、加粗、等宽字体 monospaced），外加 1.5pt 白色描边，相对方块右上偏移（x −4 / y +4）。
  - 点击 → 跳转通知页 `homeNotifications`。
  - 未读数 = `app.unreadNotificationCount`（含真公告 + push mock）。

#### 2.2 学年更新「待更新」横幅 renewBanner（条件显示）

仅当 `app.needsRenewal == true` 时显示，夹在问候行与减点卡之间，左右内边距 16dp、上 6dp。整条可点击 → 打开「学籍番号更新」弹窗（iOS 是 `app.openSheet(.renewStudentNo)`）。

横向 `Row`：

- 左图标：`person.text.rectangle`（人像证件图），字号 18、半粗，色 `primary`。
- 中间竖排两行（行距 2）：
  - 主文案 `「学籍番号の更新が必要です」`（意为「需要更新学籍号」），字号 14、加粗、色 `ink`。
  - 副文案 `「新学年の 学年・組・出席番号 を設定してください」`（意为「请设置新学年的 年级・班级・出席号」），字号 12、色 `inkMute`。
- `Spacer` 撑开。
- 右侧按钮：文字 `「更新」`，白字（字号 13、加粗），左右内边距 14、上下 8，胶囊形 `primary` 底。

整条容器：内边距 14，圆角 16dp，底色 `primary` @ 6% 透明，外加 1pt `primary` @ 30% 描边。

**Android 现状**：`needsRenewal` 状态 + 这个横幅 + 跳转弹窗全部缺失，要新建。

#### 2.3 減点 amber 卡 pointsCard（核心卡，含多态）

这是主页最复杂的卡。容器：圆角 **22dp**，内边距「左右 22 / 上下 20」，amber 渐变底，外加一圈金色阴影（`#D4A547` @ 24% / 半径 20 / y偏移 6）。右上角叠一个白色径向渐变装饰圆斑（半径 60、整体 120×120，偏移到卡右上，被卡圆角裁掉一半）。

卡内容**按状态三选一**（iOS 用 `app.rollState` + `app.studyState` 判断），优先级从高到低：

**(A) 学習模式**（仅「学習対象学生」+ 学習状态为 upcoming/active 时 — DEMO-ONLY，v1.0 会删，Android 可暂缓或一并做）
**(B) idle 态（默认）= 今月の減点 hero** ← **这是截图 01 / 06 的主形态，Android 优先做这个**
**(C) 点呼进行中/遅刻/欠席/完了 hero**（active/late/absent/done — 点呼那段动态，归点呼对齐节，本节只交代布局骨架）

##### (B) idle 态 — 今月の減点 hero（重点做）

整块可点击 → 跳转 `myPoints`（我的扣分明细页）。竖排，文字色统一 `deepBrown`(`#5C3410`)：

1. **顶行**（横向，下边距 6）：
   - 左标题 `「今月の減点」`（意为「本月扣分」），字号 11、加粗、**全大写处理 + 字距 1.98**（letterSpacing 拉很开），色 `deepBrown` @ 80%。
   - 右 pill：idle 态文字固定 `「来月より清掃対象」`（意为「下月起列入清扫对象」）。字号 11.5、加粗、字距 0.22，左右内边距 10、上下 3，胶囊形，底色白 @ 45%，字色 `deepBrown`。
2. **大数字行**（横向基线对齐，下边距 12）：
   - 大数字 = `displayUser.points` 保留 1 位小数，演示值 **`4.5`**。字号 **56**、超粗（heavy）、等宽字体、字距 −1.12。
   - 紧跟单位 `「点」`，字号 16、半粗、色 `deepBrown` @ 75%。
3. **进度条 progressRow**（关键，见下）。
4. **底行**（横向，上边距 12）：
   - 左侧统计：`「遅刻 {N} 回 · 欠席 {M} 回」`（意为「迟到 N 次 · 缺席 M 次」），其中 N=`displayUser.lateCount`（演示 **5**）、M=`displayUser.absentCount`（演示 **2**）。整行字号 12、色 `deepBrown` @ 85%；两个数字本身用等宽加粗字号 12。
   - 右侧 `「詳細」` + 右箭头 `›`（字号 12 加粗 / 箭头 14），色 `deepBrown`。

**进度条 progressRow 细节**（截图能看到的横条）：

- 轨道：高 8、圆角 4、底色白 @ 40%，占满卡宽。
- 填充：从左起，宽度 = `(points / 8) × 轨道宽`（演示 4.5/8 ≈ 56%），高 8、圆角 4，填充渐变 `#D99F3E → #B07A28`（左→右）。
- 两根阈值竖线（色 `deepBrown` @ 40%，宽 2、高 12）：一根在 50% 处（4 点），一根在 100% 处（8 点）。
- 轨道下方一行刻度标签（字号 10、等宽、`deepBrown` @ 70%）：左 `「0」`、中 `「4 · 清掃」`（意为「4 点 · 清扫」）、右 `「8 · 外出禁止」`（意为「8 点 · 禁止外出」），三者用 `Spacer` 两端对齐。

##### (C) 点呼进行中 hero（布局骨架，动态细节归点呼节）

当 `rollState ≠ idle` 时整卡换成点呼形态，竖排三段：

- **Row 1**：小号「今月の減点 · {N} 点 · 詳細›」一行（可点 → `myPoints`）。
- **Row 2 heroStatus**：大状态块，按子态显示：
  - active 倒计时：标题 `「点呼中 · 残り」`、大字 `mm:ss`（字号 44 超粗等宽）、副文 `「NFC にタッチでチェックイン」`。
  - active 超时：大字 `「遅刻」`（红 `danger`）、副文 `「欠席申請または体調報告で救済可能」`。
  - done：标题=签到时刻（如 `「21:02」`）、大字 `「時間内」`（绿 `#2C6048`）、副文 `「今回の点呼は完了しました」`。
  - absent：整卡变红渐变，文字转白系；大字 `「欠席」`、副文 `「寮監室まで直接お越しください」`。
- **Row 3 操作按钮**：
  - 非欠席态：两个并排白底半透按钮 `「欠席申請」`（开 absence 弹窗）+ `「体調報告」`（开 health 弹窗）。
  - 欠席态：单个白底红字按钮 `「寮監に連絡」`（点了弹 toast `「寮監：田中先生（内線 101）へ直接ご連絡ください」`）。

##### (A) 学習模式 hero（DEMO-ONLY，可后做）

仅学習対象学生 + 学習状态 upcoming/active 时显示：upcoming 显示学習迟到倒计时大字（mm:ss）+ 节次提示 `「前半節 19:40〜20:40 ／ 後半節 20:45〜21:45」` + `「請假」`入口；active 显示「開始/終了」两点 NFC 签到进度 + `「NFC で签到」`/`「請假」`按钮，两次都签到完显示 `「本日の学習出席は完了しました」`。

#### 2.4 LifeTab — 5 张生活卡

竖向 `Column`，卡间距 10dp。顺序固定：バス → 宅配便 → 活動 → リクエスト曲 → 遺失物。每张都是 `HomeCard`（白底圆角 18dp）。

##### ① 次のバス便（巴士卡）

横向 `Row`，间距 12：

- 左图标块：44×44，圆角 12dp，底色 `primary` @ 7% 透明，中间巴士图标 `Ic.bus(22)` 色 `primary`。
- 中间竖排（行距 2）：
  - 数据源逻辑：iOS 调 `LifeTab.upcomingBus` 计算属性 → 扫 `SEED.busSchedule`，先找「今天且时刻晚于现在」的第一班；找不到再找「未来最近一天」的第一班。
  - **若是今天的班**：第 1 行 `「次のバス便」`（意为「下一班巴士」），字号 13、色 `inkSub`；第 2 行大时刻（如 `「07:30」`，字号 22、加粗、等宽、色 `ink`）+ 同行 `「· {route}」`（如 `「· 高校棟 → 岡山駅西口」`，字号 12、色 `inkMute`、单行截断）。
  - **若是未来日的班**：第 1 行改 `「次回運行」`（意为「下次运行」）；时刻后跟 `「· M/D(曜日)」`（如 `「· 4/29(水)」`）；再下一行单独显示 route 文字（字号 11、色 `inkMute`）。
  - **若无任何班**：第 1 行 `「次のバス便」`、第 2 行 `「予定なし」`（意为「无预定」，字号 14、色 `inkMute`）。
- 右端箭头 `›`（16，色 `inkMute`）。
- 整卡点击 → 跳转 `busList`（带筛选的巴士一覧 `BusListView`，**不是**旧的 `homeBus`）。

`BusLine` 字段：`time` / `route` / `seats` / `next`。`BusDaySchedule` 字段：`date` / `weekday` / `label` / `notice?` / `lines: [BusLine]`。

##### ② 宅配便（快递卡）

横向 `Row`，间距 12：

- 左图标块：44×44，圆角 12dp，底色 `dangerBg`(`#FDE8E8`)，中间包裹图标 `Ic.package(22)` 色 `danger`。
  - **待領 badge**：当待领数 `pendingPkg > 0` 时右上角叠红圆，20×20、圆角 10、红底 `danger`、白字（字号 11 加粗等宽）、2pt 白描边，偏移 x +4 / y −4。
  - `pendingPkg` = `SEED.packages` 里 `status == "待領"` 的条数（演示数据里只有 id=1 是「待領」→ **1 件**）。
- 中间竖排（行距 2）：
  - 主行 `「宅配便 · {N} 件未受取」`（意为「快递 · N 件未领取」），演示 `「宅配便 · 1 件未受取」`，字号 15、加粗、色 `ink`。
  - 副行 `「本日到着」`（意为「今日到达」），字号 12、色 `inkSub`。
- 右端箭头 `›`。
- 整卡点击 → 跳转 `homePackages`（包裹一覧）。

`PackageItem` 字段：`id` / `date` / `from` / `status`(待領|領済) / `tracking?`。

##### ③ 今週の活動（活動卡，带内嵌列表）

竖排，行距 10：

- **头行**（横向）：
  - 左 32×32 图标块，圆角 10dp，底色 `accent` @ 13% 透明，中间日历图标 `Ic.calendar(18)` 色 `primary`。
  - 标题 `「今週の活動 · {N} 件」`（意为「本周活动 · N 件」），N=`SEED.events.count`（演示数据共 14 条），字号 14、加粗、色 `ink`。
  - `Spacer` + 右端箭头 `›`。
- **内嵌列表**：取 `SEED.events` 前 **2** 条，每条一行（上下内边距 6）：
  - 左 `MM-DD`（把日期 `2026-04-05` 去掉前 5 字符 → `04-05`），字号 11、等宽、色 `inkMute`、固定宽 50。
  - 中标题 `event.title`（如 `「留4アクティビティ」`），字号 13、色 `ink`。
  - `Spacer` + 右时刻 `event.time`（如 `「08:30」`），字号 11、色 `inkMute`。
- 整卡点击 → 跳转 `homeEvents`（活動一覧）。

`EventItem` 字段：`date` / `time` / `title` / `place` / `desc`。前 2 条演示数据：`04-05 留4アクティビティ 08:30`、`04-07 帰寮日 15:33`。

##### ④ リクエスト曲（点歌卡）

横向 `Row`，间距 12：

- 左图标块：44×44，圆角 12dp，**紫色渐变底**（左上→右下 `#A78BFA → #7C3AED`），中间音符图标 `Ic.music(22)` 色白。
- 中间竖排（行距 2）：
  - 主行 `「リクエスト曲 · {N} 件」`（意为「点歌 · N 件」），N=`SEED.songs.count`（演示 8 条），字号 14、加粗、色 `ink`。
  - 副行 = 排第一的歌 `「{title} · {artist}」`（演示 `「Lemon · 米津玄師」`，取 `SEED.songs.first`），字号 12、色 `inkSub`、单行截断。若无歌则显示 `「まだ投稿がありません」`（意为「还没有投稿」，色 `inkMute`）。
- 右端箭头 `›`。
- 整卡点击 → 跳转 `homeMusic`（点歌一覧）。

`SongItem` 字段：`id` / `title` / `artist` / `by` / `up` / `down`。

##### ⑤ 遺失物（失物卡，3 列方格）

竖排，行距 10：

- **头行**（横向）：标题 `「遺失物 · 最新」`（意为「失物 · 最新」），字号 14、加粗、色 `ink`；`Spacer` + 右端箭头 `›`。
- **3 列网格**（`LazyVGrid` 3 等分列、列间距 8、行间距 8）：取 `SEED.lost` 前 **3** 条，每条一个正方形方块 `lostTile`：
  - 方块：1:1 正方形，圆角 10dp，底色 = 该物品 `color`（hex）@ 13% 透明，上叠一层 135° 线性渐变（同色 40% → 13%），外加 0.5pt `hair` 描边。
  - 左下角标题文字 = `title` 前 **8** 字符，字号 10、半粗、白字、带黑色阴影（便于浅底上可读），内边距 8。
  - 演示前 3 条：`「青い折りたたみ傘」`(蓝 `#3b82f6`)、`「黒の鍵」`(黑 `#1f2937`)、`「赤のペンケース」`(红 `#ef4444`)。
- 整卡点击 → 跳转 `homeLost`（失物一覧）。

`LostItem` 字段：`id` / `title` / `place` / `date` / `color`(hex)。Android 解析 hex 字符串成 Color 时要处理 `#` 前缀。

### 3. 用到的共享组件汇总

| 组件 | iOS 名 | Android 要做成 |
|---|---|---|
| 生活卡白卡 | `HomeCard`（圆角 18 / pad 14 / 双阴影 / 可点击） | 复用 `Card` 封装的 Composable |
| 减点卡 | `pointsCard`（圆角 22 / amber 渐变 / 三态） | 自定义 Composable，渐变用 `Brush.linearGradient` |
| pill 胶囊标签 | `NotifPill` / 内联 `Capsule` | `Box` + `RoundedCornerShape(50%)` |
| 右箭头 | `Ic.chevR` | `Icons.ChevronRight` |
| 图标 | `Ic.bell / bus / package / calendar / music`(22 或 18) | Material Icons 或矢量资源 |
| 进度条 | `progressRow`（轨道 + 填充 + 2 阈值线 + 刻度） | 自定义 `Canvas` 或 `Box` 叠层 |

### 4. 关键文案（日语原文逐条）

- `「おかえり、{name} さん」` — 问候（XX 同学，欢迎回来）
- 日期 `「yyyy 年 M 月 d 日（E）」` — JST 当天，运行时生成
- `「学籍番号の更新が必要です」` / `「新学年の 学年・組・出席番号 を設定してください」` / `「更新」` — 学年更新横幅
- `「今月の減点」` / `「点」` / `「来月より清掃対象」` — 减点卡（idle）
- `「遅刻 {N} 回 · 欠席 {M} 回」` / `「詳細」` — 减点卡底行
- 进度条刻度：`「0」` `「4 · 清掃」` `「8 · 外出禁止」`
- 点呼态：`「点呼中 · 残り」` `「NFC にタッチでチェックイン」` `「遅刻」` `「欠席申請または体調報告で救済可能」` `「時間内」` `「今回の点呼は完了しました」` `「欠席」` `「寮監室まで直接お越しください」` `「欠席申請」` `「体調報告」` `「寮監に連絡」` `「寮監：田中先生（内線 101）へ直接ご連絡ください」`
- 巴士卡：`「次のバス便」` / `「次回運行」` / `「予定なし」`
- 快递卡：`「宅配便 · {N} 件未受取」` / `「本日到着」`
- 活動卡：`「今週の活動 · {N} 件」`
- 点歌卡：`「リクエスト曲 · {N} 件」` / `「まだ投稿がありません」`
- 失物卡：`「遺失物 · 最新」`

### 5. 导航（怎么进 / 跳哪）

- 主页本身是底部导航 BottomNav 第一个 tab「ホーム」，App 启动默认落在这里。
- 顶部 TopRollBar / 底部 BottomNav 由全局 `GlobalOverlays` 挂，主页自身**不重挂**（Android 同理：导航栏放在 Scaffold 外层，主页只管内容滚动区）。
- 跳转目标（iOS Route 枚举值，在 `Foundation/Routing/Route.swift`）：
  - 铃铛 → `homeNotifications`
  - 减点卡（idle 整卡 / 点呼态 Row1 / 底行詳細）→ `myPoints`
  - 学年横幅 → 弹窗 `renewStudentNo`
  - バス卡 → `busList`
  - 宅配便卡 → `homePackages`
  - 活動卡 → `homeEvents`
  - 点歌卡 → `homeMusic`
  - 失物卡 → `homeLost`
  - 点呼态按钮 → 弹窗 `absence` / `health`；学習 → 弹窗 `studyCheckin` 或 `applyForm(kind: "studyAbsence")`

### 6. 数据源（mock）

主页所有数据都来自本地 mock，**没有网络层**（生产态会改读后端，但当前 iOS 演示态也是读 SEED + AppStore 内存状态）：

- 用户信息：`app.displayUser`（演示落到 `SEED.demoUserSeed` → `「リュウ イヒ」` / 男寮 A5 / `points 4.5` / `lateCount 5` / `absentCount 2` / `isStudyTarget true`）。
- 未读数：`app.unreadNotificationCount`。
- 学年横幅开关：`app.needsRenewal`（默认 false）。
- 点呼/学習状态：`app.rollState`（idle/active/absent/done）、`app.studyState`（upcoming/active 等）、倒计时 `app.rollCountdownSec` / `app.studyCountdownSec`、`app.studyTaps`。
- 巴士：`SEED.busSchedule`（5 天的特别运行表，`LifeTab.upcomingBus` 实时挑下一班）。
- 快递：`SEED.packages`（4 条，1 条待領）。
- 活動：`SEED.events`（14 条，主页取前 2）。
- 点歌：`SEED.songs`（8 条，主页取第 1 首预览）。
- 失物：`SEED.lost`（6 条，主页取前 3）。

### Android 对齐要点

Android 现状（`03_dev/student_android/v1/`）= 早期演示桩，只有 Compose UI 桩 + 本地 `MockData.kt`，**没有网络层**，主页跟 iOS 差距很大。要补成跟 iOS 一致，按下面做：

1. **建数据模型 + 种子数据**：在 Kotlin 侧建 `User` / `BusLine` / `BusDaySchedule`(字段 `date/weekday/label/notice?/lines`) / `PackageItem`(`status` 待領|領済) / `EventItem` / `SongItem`(`up/down`) / `LostItem`(`color` hex) 数据类，字段名与值**逐一照抄** `SEED.swift`（用户 `「リュウ イヒ」`/男寮/A5/points 4.5/late 5/absent 2；巴士 5 天；快递 4 条；活動 14 条；点歌 8 条；失物 6 条）。这是主页能显示正确数字（4.5 / 5 / 2 / 1 件 / 14 件 / 8 件）的前提，不补这些卡片就是空的。

2. **建主题令牌**：把上面第 0 节的颜色表搬进 `Color.kt` / `Theme.kt`，命名对齐 iOS（primary/accent/pearl/paper/ink/inkSub/inkMute/hair/danger/dangerBg/warnBg/okBg 等），减点卡的 amber 渐变三色 + 深褐 `#5C3410` 也单独定义。

3. **建两个核心 Composable**：
   - `HomeCard(onClick)` — 白底圆角 **18.dp**、`padding(14.dp)`、`border(0.5.dp, hair)`、阴影。注意 Compose `Card` 默认圆角不是 18，要显式 `RoundedCornerShape(18.dp)`。
   - `pointsCard` — 圆角 22.dp，`Brush.linearGradient` 画 amber 渐变，右上角白色径向渐变装饰圆斑用 `Brush.radialGradient` + `Modifier.clip`。

4. **减点卡先只做 idle 态**：点呼三态 + 学習模式是 DEMO-ONLY（v1.0 会删），可以先把 idle 态（`今月の減点` 大数字 4.5 + 进度条 + `遅刻 5 回 · 欠席 2 回` + 詳細）做对，这是截图 01/06 的主形态。进度条用 `Box` 叠层或 `Canvas`：底轨白 40% → 填充渐变宽 `points/8` → 两根阈值竖线（50%、100%）→ 下方三段刻度 `0` / `4 · 清掃` / `8 · 外出禁止`。

5. **巴士卡的「挑下一班」逻辑**要照搬：用 `LocalDate.now()`（时区 Asia/Tokyo）扫 `busSchedule`，先找今天且 `time > 现在时刻` 的第一班 → 标题 `次のバス便` + `time · route`；否则找未来最近一天第一班 → 标题 `次回運行` + `time · M/D(曜日)`；都没有 → `予定なし`。别写死成 `07:30`。

6. **快递 badge 数**要由 `packages.count { it.status == "待領" }` 算出来（演示=1），不要写死。badge 是红圆 20×20、2dp 白描边、偏移到图标右上。

7. **活動/点歌/失物的「截断取前 N 条」**：活動取 `events.take(2)`、失物取 `lost.take(3)`、点歌取 `songs.first()`。日期 `04-05` 由 `date.drop(5)` 得到；失物标题取 `title.take(8)`；hex 颜色字符串解析成 `Color` 要处理 `#` 前缀（iOS 有 `Color(hexString:)` 兜底，Android 自己写 `parseColor`）。

8. **导航**：用 Navigation-Compose 建对应路由（busList / homePackages / homeEvents / homeMusic / homeLost / homeNotifications / myPoints）+ 学年更新/absence/health/studyCheckin 等弹窗。整卡 `Modifier.clickable` 跳对应目的地，跳转目标名对齐 iOS Route 枚举。

9. **学年横幅条件渲染**：`if (needsRenewal) { RenewBanner() }`，默认 `needsRenewal=false` 不显示（与 iOS 一致）。

10. **铃铛未读 badge**：未读数 > 0 才显示红胶囊，数字 + 1.5dp 白描边，偏移到铃铛方块右上。

---

I now have a complete picture of both iOS (target) and Android (current). I have everything needed to write the alignment spec. Let me also quickly confirm the iOS `Ic` icon SF Symbol names map and the SuzuIcons availability on Android isn't critical — I'll describe icon requirements generically since Android uses a letter placeholder now. I have enough detail.

Here is my section:

## 申し込み（申请列表 + 新規申請选择）— iOS↔Android 对齐规格

> iOS 真值文件：`03_dev/student_ios/v1/TomoshibiApp/Features/Apply/ApplyStubs.swift`（列表 §2.1 行 60-275 / 新規申請宫格 §2.2 行 281-345）。对应截图 08（申请列表）/ 09 + 10（新規申請宫格）。
> Android 现状文件：`03_dev/student_android/v1/app/src/main/java/jp/tomoshibi/android/ui/screens/applications/ApplicationsScreen.kt`（列表 + 宫格全在一个文件里）。
> 共享设计令牌（颜色/圆角/间距）来自 iOS `Foundation/Theme/TTokens.swift`，Android 对应 `ui/theme/SuzuT`。下文凡引用 `T.xxx` 都给出十六进制色值，方便 Android 工程师核对 `SuzuT` 里的同名字段。

---

### 一、画面一覧（本块涉及 2 屏 + 1 弹层）

| 编号 | iOS View | 路由 | 说明 |
|---|---|---|---|
| 屏 1 | `ApplyListView` | `.apply`（底栏 tab 之一） | 申请列表，4 个筛选 tab + 申请卡列表 + 右下「＋」悬浮按钮 |
| 屏 2 | `ApplyNewView` | `.applyNew` | 新規申請种类选择，2 列宫格，12 种类型 |

注意一个关键差异：**iOS 的「新規申請」是一个独立全屏页（`ApplyNewView`），从列表右下「＋」按钮 `router.go(.applyNew)` 进入。Android 现状把它做成了底部弹出抽屉（`ModalBottomSheet`）**。要对齐 iOS 就得改成独立全屏页（见下「Android 对齐要点」）。

---

### 二、屏 1 · ApplyListView 布局结构（从上到下）

整体是一个 `ZStack(alignment: .bottomTrailing)`：底层是列表内容，叠加层是右下角悬浮按钮。背景色 `T.pearl`（`#EFF2F3` 灰白）。

**① 顶部页头 `PageHeader(title: "申し込み", level: 1)`**
- `level: 1` 表示这是一级页：左侧显示「家」图标（`Ic.home()`），点击 `router.replace(.home)` 回首页（不是返回箭头）。
- 标题文字「申し込み」字号 17、粗体（`.bold`）、色 `T.ink`（`#0F1E22` 近黑）。
- 页头内边距：左右 16、上下 12。
- 长按 0.4 秒「家」图标会弹面包屑导航（`app.breadcrumbOpen`）——这是全局 PageHeader 行为，列表页继承。

**② 筛选 tab 行（横向胶囊 pill）** — 一个横向 `ScrollView`，4 个 tab：

| key | 标签（日语原文） | 命中逻辑 |
|---|---|---|
| `all` | 「すべて」（全部） | 全部显示 |
| `pending` | 「審査中」（审查中） | `status == "pending"` |
| `approved` | 「承認済」（已批准） | `status == "approved"` **或** `"approved_partial"`（一部承認也归这） |
| `draft` | 「下書き」（草稿） | `status == "draft"` |

- 每个 tab 是胶囊（`Capsule`）：字号 12.5、半粗体（`.semibold`）、左右内边距 14、上下 7。
- 选中态：文字白色，背景 `T.primary`（`#1F6B74` 深 teal 青）。
- 未选中态：文字 `T.primary`，背景 `T.pill`（`#1F6B74` 8% 透明度的淡青）。
- tab 行下方留白 14。

**③ 三种状态分支**（互斥，按顺序判断）：
- **加载中**（`loading`）：居中转圈 `ProgressView()`，内边距 40。
- **加载失败**（`loadError != nil`）：居中竖排 → 「⚠️」字号 40 + 错误文案（色 `T.inkSub` `#56707A`，居中）+ 「再読み込み」（重新加载）按钮（色 `T.primary`，半粗体）。点按钮重新 `load()`。
- **空列表**（`filtered.isEmpty`）：居中竖排 → 「📋」字号 40 + 「申請はありません」（无申请，字号 14 粗体 `T.inkSub`）+ 「下の＋ボタンから新規作成できます」（可从下方＋按钮新建，字号 12 色 `T.inkMute` `#93A4AC`）。
- **有数据**：竖排卡片列表，卡间距 10，每张是一个 `ApplicationRow`。

列表整体左右内边距 16，底部留白 120（给悬浮按钮让位）。

**④ 申请卡 `ApplicationRow`** — 用共享 `Card(padding: 14)` 组件包裹，内部上下两区，中间一条 0.5pt 细分隔线（`T.hair` `#0F1E22` 8% 透明）。

上区（一个 `HStack`，间距 12）：
- **左侧图标方块**：40×40，圆角 10，背景 `T.pill`（淡青）。里面放该申请类型对应的 SF Symbol 图标（色 `T.primary`，字号 17）。图标按申请类型取（见下第六节类型表的 `icon` 列）。
- **中间竖排**（间距 3）：
  - 第一行 `HStack`（间距 8）：类型名（如「外泊」，字号 14 粗体 `T.ink`）+ 状态徽章 `Pill`。
  - 第二行：摘要文字 `item.summary`（字号 12，色 `T.inkSub`）。例：「東京 · 2 泊 3 日」。
- 右侧 `Spacer` 把内容顶左。
- 上区底部留白 8。

下区（一个 `HStack`，顶部留白 8 + 顶部细线）：
- 左侧日期 `item.date`（字号 11，**等宽字体** `.monospaced`，色 `T.inkMute`）。
- 右侧 `Spacer`。

整张卡点击 → `router.go(.applyDetail(id: item.id))` 进申请详情。

**⑤ 状态徽章 `Pill`**（共享组件 `Foundation/Components/UIAtoms.swift`）— 文字 + 胶囊底，字号 11 半粗体，左右内边距 10、上下 4。状态 → 标签 + 配色映射（iOS `statusPair` 函数，行 43-54）：

| status（后端值） | 标签（日语） | Pill.Tone | 文字色 | 底色 |
|---|---|---|---|---|
| `draft` | 「下書き」 | `.neutral` | `T.inkSub` `#56707A` | `T.hair`（近黑 8%） |
| `pending` | 「審査中」 | `.warn` | `T.warnDeep` `#7A4A0E` | `T.warnBg` `#FDF4E1` |
| `approved` | 「承認済」 | `.ok` | `T.okDeep` `#2C6048` | `T.okBg` `#E3F1EA` |
| `approved_partial` | 「一部承認」（部分批准） | `.ok` | 同上 | 同上 |
| `rejected` | 「差戻」（驳回） | `.danger` | `T.danger` `#C44848` | `T.dangerBg` `#FDE8E8` |
| `returned` | 「要修正」（需修改） | `.danger` | 同上 | 同上 |
| `withdrawn` | 「取消済」（已取消） | `.neutral` | 同 `draft` | 同 `draft` |
| 其他未知值 | 原样显示 | `.neutral` | 同 `draft` | 同 `draft` |

**⑥ 右下悬浮按钮 FAB**（叠在 ZStack 右下）：
- 尺寸 56×56，**圆角 18 的圆角方形**（不是正圆 `RoundedRectangle(cornerRadius: 18)`），背景 `T.primary`（深青），带阴影（青色 35% 透明，模糊半径 12，y 偏移 8）。
- 里面是「＋」图标 `Ic.plus(24)`，白色。
- 距右 18、距底 96（避开底部导航栏）。
- 点击 → `router.go(.applyNew)` 进新規申請页。

---

### 三、屏 2 · ApplyNewView 布局结构（新規申請种类选择）

竖排 `VStack`，背景 `T.pearl`。

**① 页头 `PageHeader(title: "新規申請", level: 2)`** — `level: 2` 表示二级页：左侧是**返回箭头**（`Ic.back()`），点击 `router.back()` 返回列表。标题「新規申請」。

**② 说明文字**「申請の種類を選択してください」（请选择申请种类）— 字号 13，色 `T.inkSub`，左内边距 4，下留白 14。

**③ 2 列宫格 `LazyVGrid`**（2 列等宽 `.flexible()`，列间距 10、行间距 10）：12 个类型，每个是一个按钮卡，点击 → `router.go(.applyForm(kind: t.k))` 进对应申请表单。

每个宫格卡用 `Card(padding: 16)`，内部居中竖排：
- **图标方块**：52×52，圆角 14，背景 `T.pill`（淡青）。图标 SF Symbol（色 `T.primary`，字号 22）。下留白 10。
- **类型名**：字号 14 粗体 `T.ink`。下留白 3。
- **副标题描述**：字号 11，色 `T.inkMute`，行距 2，居中多行。

宫格区左右内边距 16、顶 4、底 24。

---

### 四、12 种申请类型完整表（iOS `APPLY_TYPES`，行 22-35）⭐ 这是对齐核心

**每个类型必须有：英文 key（路由用，传给 `applyForm(kind:)`）+ 日语名 + SF Symbol 图标 + 日语副标题。** Android 现状只有 10 个、key 用的是日语、还缺图标。完整 12 个如下，顺序也要一致：

| 顺序 | key（英文，路由用） | 名（日语） | 副标题（日语原文逐字） | iOS SF Symbol 图标 |
|---|---|---|---|---|
| 1 | `outing` | 「外出」 | 「当日帰寮の外出」 | `calendar` |
| 2 | `stay` | 「外泊」 | 「寮外での宿泊」 | `house` |
| 3 | `holiday` | 「帰省」 | 「実家帰省・長期休暇」 | `house.lodge`（带烟囱的小屋） |
| 4 | `returncountry` | 「帰国」 | 「一時帰国（航空機利用）」 | `airplane` |
| 5 | `repair` | 「修繕」 | 「部屋・設備の修繕依頼」 | `wrench.and.screwdriver`（扳手+螺丝刀） |
| 6 | `parcel` | 「代理受取」 | 「不在時の荷物代理受取」 | `shippingbox`（快递箱） |
| 7 | `guest` | 「来訪者」 | 「家族・友人の来訪」 | `person.2`（两个人） |
| 8 | `studyAbsence` | 「学習欠席」 | 「晚自习の欠席届（前半・後半・両方）」 | `book.closed`（合上的书） |
| 9 | `studyOnline` | 「オンライン学習」 | 「自室でのオンライン学習」 | `laptopcomputer`（笔记本电脑） |
| 10 | `event` | 「行事企画」 | 「寮内イベントの企画申請」 | `sparkles`（闪光） |
| 11 | `fridge` | 「冷蔵庫購入」 | 「指定冷蔵庫の購入届」 | `snowflake`（雪花） |
| 12 | `item` | 「物品所持」 | 「持込物品の許可願」 | `shippingbox`（快递箱，与 parcel 同图标） |

> 注意：副标题第 8 项「晚自习」里的「晚」是中文汉字（iOS 源码原样如此，照抄，不要改成日语「夜」）。
> 列表卡上区的「类型图标 + 类型名」也用同一张 `APPLY_TYPES` 表查（iOS `applyType(item.type)` 行 37-39，按 key 匹配，匹配不到取第 0 个 `outing`）。

---

### 五、关键文案汇总（日语原文，照抄）

- 页头标题：「申し込み」（列表）/「新規申請」（种类选择）
- tab：「すべて」「審査中」「承認済」「下書き」
- 空列表：「申請はありません」「下の＋ボタンから新規作成できます」
- 加载失败重试按钮：「再読み込み」
- 种类选择说明：「申請の種類を選択してください」
- 状态徽章：「下書き」「審査中」「承認済」「一部承認」「差戻」「要修正」「取消済」
- 12 类型名 + 副标题：见上表

---

### 六、导航

- 进列表：底部导航栏 tab「申し込み」→ `.apply`。
- 列表 →「＋」FAB → `.applyNew`（新規申請页）。
- 新規申請页 → 点某个类型宫格 → `.applyForm(kind: key)`（对应表单，本块不含表单内部）。
- 新規申請页 → 返回箭头 → `router.back()` 回列表。
- 列表 → 点某张申请卡 → `.applyDetail(id:)`（申请详情，本块不含）。

---

### 七、数据源

iOS 列表数据走条件编译（`#if DEMO`，行 104-127）：
- **演示版**（`#if DEMO`）：读 `SEED.applications`（`Foundation/Seed/SEED.swift` 行 97-101），3 条假数据：
  - `{id:"a1", type:"stay", status:"pending", date:"2026-04-20", summary:"東京 · 2 泊 3 日"}`
  - `{id:"a3", type:"holiday", status:"approved", date:"2026-04-15", summary:"茨城 · 帰省"}`
  - `{id:"a4", type:"outing", status:"approved", date:"2026-04-02", summary:"駅前 · タクシー予約"}`
- **生产版**：调 `ApplicationsAPI.listMine()` → 拿后端 `ApplicationOut` 列表 → 经 `mapToItem`（行 93-101）转成 `ApplicationItem`。转换里 `summary` 拼成「{kind}・{leave_date}〜{return_date}」，`type` 经 `ApplyKindMapper.decode(o.kind)` 把后端日语 kind 转回英文 key。
- 拉数据失败若是 401 未授权（`APIError.unauthorized`）→ 清登录态 `app.authToken = nil` + 跳登录页 `router.replace(.login)`；其他错误 → 显示错误文案 + 重试按钮。
- `hasLoaded` 标记防止切 tab / 重进页面重复拉取（`.task { if !hasLoaded { await load() } }`）。

`ApplicationItem` 模型（`Foundation/Seed/SeedModels.swift` 行 93-99）：`id: String` / `type: String`（英文 key）/ `status: String`（后端状态值）/ `date: String` / `summary: String`。

新規申請宫格本身无数据源 —— 12 个类型是写死的 `APPLY_TYPES` 常量。

---

### Android 对齐要点

Android 现状（`ApplicationsScreen.kt`）骨架对了（列表 + 4 tab + 右下渐变 FAB），但跟 iOS 有 6 处明显不一致，要逐一改：

**1. 类型表彻底重做（最重要）。** 现状 `APPLY_KINDS`（行 225-236）只有 10 个、key 用日语（如 `KindMeta("外出", ...)`）、还混进了 iOS 没有的「早帰」「学習」「その他」，且缺了「学習欠席」「オンライン学習」「行事企画」「冷蔵庫購入」「物品所持」「代理受取」「来訪者」等多个。要替换成上面第四节那张 12 行表，**key 改成英文**（`outing`/`stay`/`holiday`/`returncountry`/`repair`/`parcel`/`guest`/`studyAbsence`/`studyOnline`/`event`/`fridge`/`item`），顺序、名、副标题逐字照抄。Compose 数据类建议：
```kotlin
data class ApplyKindMeta(val key: String, val name: String, val sub: String, val icon: ImageVector)
```
导航传 key 用英文：`navController.navigate(Route.ApplyForm.withKind(meta.key))`（注意现状传的是日语 `k.key`，下游表单分派得按英文 key 判断，跟 iOS `ApplyFormDispatcher` 一致）。

**2. 宫格图标：现状用「类型名首字」占位**（行 270-274 `k.name.firstOrNull()`），必须换成真图标。iOS 用 SF Symbol，Android 要找视觉等价的 Material 图标或自绘 `SuzuIcons`：`calendar`→`Icons.Outlined.CalendarMonth`、`house`/`house.lodge`→`Icons.Outlined.Home`/`Cottage`、`airplane`→`Flight`、`wrench.and.screwdriver`→`Build`、`shippingbox`→`Inventory2`、`person.2`→`Group`、`book.closed`→`MenuBook`、`laptopcomputer`→`Laptop`、`sparkles`→`AutoAwesome`、`snowflake`→`AcUnit`。图标方块：宫格 52dp 圆角 14dp 背景 `tokens.pill`，图标色 `tokens.primary` 22sp；列表卡 40dp 圆角 10dp 同色。

**3. 新規申請改成独立全屏页，不是 ModalBottomSheet。** 现状（行 207-222）点 FAB 弹底部抽屉 `ModalBottomSheet` 放宫格 —— iOS 是 `router.go(.applyNew)` 跳一个**独立全屏页** `ApplyNewView`（带 `level:2` 返回箭头页头 +「申請の種類を選択してください」说明 + 2 列 `LazyVGrid`）。要把宫格搬进一个新的全屏 Composable（项目里已有 `ApplyNewScreen.kt` 文件，把宫格逻辑挪过去），FAB 改成 `navController.navigate(Route.ApplyNew.path)`。页头用二级页头组件（左返回箭头），背景 `tokens.pearl`。

**4. 列表卡布局对齐。** 现状卡（行 137-174）缺三样东西：
- **缺左侧类型图标方块**（40dp 圆角 10 背景 pill + 类型图标）。现状直接把类型名做成小 pill 标签了，要改成「图标方块 + 类型名(14sp 粗体) + 状态 Pill」横排。
- **缺底部日期区**：iOS 下区有一条细分隔线 + 等宽字体日期（11sp monospace 色 `inkMute`）。现状把 `#id` 放右上角了，要去掉，改成底部放 `item.date`（等宽）。
- 摘要文字：iOS 用单一 `summary` 字段（12sp `inkSub`）。现状拼的是 `dest` + `from〜to`，要么改后端模型对齐 `summary`，要么本地拼成「{kind}・{leave_date}〜{return_date}」跟 iOS `mapToItem` 一致。

**5. 选中 tab 配色对齐。** 现状选中态背景用 `tokens.ink`（近黑）、文字 `tokens.pearl`（行 107、114）—— iOS 选中态背景是 `T.primary`（深青 `#1F6B74`）、文字纯白。未选中态 iOS 背景 `T.pill`（淡青）、文字 `T.primary`，现状是 `paper` 白底 + `hair` 描边 + `inkSub` 字。两处都改成 iOS 配色。tab 标签文字本身（すべて/審査中/承認済/下書き）已对，不用动。

**6. FAB 形状。** 现状是正圆 `CircleShape`（行 192）—— iOS 是**圆角 18 的圆角方形**（`RoundedRectangle(cornerRadius: 18)`）。Android 改 `RoundedCornerShape(18.dp)`。尺寸 56dp、背景 `tokens.btnGrad`（已对）、白色＋图标 26dp（已对）、距右 18dp 距底 96dp（现状 end=20 bottom=20，要调成贴 iOS、并避开底部导航栏）。

**7. 数据源 / 网络层（Android 当前完全缺）。** Android 现状只读本地 `MockData`（`state.applications`），没有任何网络层，也没有 `loading`/`loadError`/`hasLoaded` 三态。要补：
- 进页面拉 `GET /applications/mine`（对应 iOS `ApplicationsAPI.listMine()`），返回后端 `ApplicationOut` 列表，映射成本地列表项（`type` 经 kind 解码器把后端日语 kind 转英文 key、`summary` 拼「{kind}・{leave_date}〜{return_date}」）。
- 三态 UI：加载中转圈；失败显示「⚠️」+ 错误文案 +「再読み込み」重试按钮；空列表显示「📋」+「申請はありません」+「下の＋ボタンから新規作成できます」（现状空态文案是「該当する申請はありません」，要换成 iOS 这两句）。
- 401 未授权 → 清登录态跳登录页，跟 iOS 一致。
- 演示版（Android 若有 BuildConfig.DEMO 开关）走本地种子，种子内容对齐上面 `SEED.applications` 那 3 条。

**8. 状态徽章 `ApplicationStatusPill`（行 295-315）补全。** 现状只有 4 个枚举（PENDING/APPROVED/RETURNED/REJECTED），iOS `statusPair` 有 7 种 + 兜底。要补 `draft`(「下書き」neutral)、`approved_partial`(「一部承認」ok)、`withdrawn`(「取消済」neutral)，且把 `rejected` 标签从「却下」改成「差戻」、配色按第二节第⑤表对齐（neutral 用 `hair` 底 + `inkSub` 字）。同时「承認済」tab 命中逻辑要同时收 `APPROVED` 和 `APPROVED_PARTIAL`（现状只收 APPROVED）。「下書き」tab 现状写死 `false`（行 54），生产接后端后要真按 `status == draft` 过滤。

**共享组件映射速查**（iOS → Android）：`Card`→圆角 14dp 白底卡（`tokens.paper` + 阴影，现状已用）；`Pill`→`ApplicationStatusPill`；`PageHeader level:1`→home 图标页头 / `level:2`→返回箭头页头；`Ic.plus`→`SuzuIcons.Plus`；`LazyVGrid 2 列`→现状用 `chunked(2)` 手搓 Row（可保留，或换 `LazyVerticalGrid(GridCells.Fixed(2))`）。颜色令牌 `SuzuT` 字段名与 iOS `T` 同名（primary/pearl/paper/ink/inkSub/inkMute/inkFaint/hair/pill/warnBg/warnDeep/okBg/okDeep/danger/dangerBg/btnGrad），直接一一对应，色值见上文。

---

I now have everything needed. Let me write the aligned specification section as pure Markdown.

## application-forms（各申請表单）

> iOS 真值文件：`Features/Apply/ApplyStubs.swift`（列表 / 新規 / 分派 / StayForm / StudyAbsenceForm / GenericApplyForm / 确认 / 完成 / 详情）、`Features/Apply/DormLifeForms.swift`（行事企画 / 冷蔵庫購入 / 物品所持）、`Features/Apply/StudyOnlineForm.swift`（オンライン学習）、`Features/Apply/ApplyFormSupport.swift`（表单共用小组件）、`Foundation/Components/ContractFilePicker.swift`（契約書文件选择）、`Features/Home/HomeStubs.swift` 内 `RenewStudentNoSheet`（番号再設定弹窗）。
> 关键缩写一次性翻译：`#if DEMO` = 编译时分支，DEMO 构建走假数据 / 生产构建走真后端；`@State` = SwiftUI 里组件自己持有的可变状态；`Binding` = 双向绑定（子组件能改父组件的值）；`POST /applications` = 向后端「提交一条申请」的网络请求。

---

### 0. 全局：12 种申請类型 + 分派表

iOS 在 `ApplyStubs.swift` 顶部硬编码一张 `APPLY_TYPES` 表（12 条），每条 4 个字段：`k`（内部代号）/ `name`（日语显示名）/ `icon`（SF Symbol 图标名）/ `desc`（一行说明）。Android 要原样照搬这 12 条（图标用 Material 等价图标或自带矢量图都行，名字 + 说明逐字照抄）：

| k（代号） | name | icon（iOS SF Symbol） | desc |
|---|---|---|---|
| `outing` | 「外出」 | calendar | 「当日帰寮の外出」 |
| `stay` | 「外泊」 | house | 「寮外での宿泊」 |
| `holiday` | 「帰省」 | house.lodge | 「実家帰省・長期休暇」 |
| `returncountry` | 「帰国」 | airplane | 「一時帰国（航空機利用）」 |
| `repair` | 「修繕」 | wrench.and.screwdriver | 「部屋・設備の修繕依頼」 |
| `parcel` | 「代理受取」 | shippingbox | 「不在時の荷物代理受取」 |
| `guest` | 「来訪者」 | person.2 | 「家族・友人の来訪」 |
| `studyAbsence` | 「学習欠席」 | book.closed | 「晚自习の欠席届（前半・後半・両方）」 |
| `studyOnline` | 「オンライン学習」 | laptopcomputer | 「自室でのオンライン学習」 |
| `event` | 「行事企画」 | sparkles | 「寮内イベントの企画申請」 |
| `fridge` | 「冷蔵庫購入」 | snowflake | 「指定冷蔵庫の購入届」 |
| `item` | 「物品所持」 | shippingbox | 「持込物品の許可願」 |

**分派逻辑**（`ApplyFormDispatcher`，按选中的 `kind` 决定打开哪个表单）：

- `stay` / `holiday` / `returncountry` → **StayForm**（三种共用一个表单，内部按 kind 动态显隐区块）
- `studyAbsence` → **StudyAbsenceForm**
- `studyOnline` → **StudyOnlineForm**
- `event` → **DormEventProposalForm**
- `fridge` → **FridgePurchaseForm**
- `item` → **ItemPossessionForm**
- 其余（`outing` / `repair` / `parcel` / `guest` / `return`）→ **GenericApplyForm**（纯演示桩，未接后端，提交只跳确认页）

#### Android 对齐要点（全局）

- Android 现状只有本地 `MockData.kt` 假数据 + UI 桩，没有这套 12 类表 + 分派。要新建一个 `ApplyType` 数据类（4 字段）+ 一个常量列表 `APPLY_TYPES`，以及一个 `ApplyFormDispatcher` 可组合函数（`@Composable`），用 `when(kind)` 分派到 6 个表单 Composable + 1 个通用桩。
- 导航：用 Jetpack Navigation Compose，路由参数带 `kind: String`。每个表单页是一个独立 destination。
- DEMO / 生产分支：Android 用 `BuildConfig.DEBUG` 或自建 `BuildConfig.DEMO` flag 对应 iOS 的 `#if DEMO`。

---

### 1. 表单组件（共享原子，Android 必须先建这一层）

所有申請表单都建在同一套小组件上。Android 要先把这套组件做出来，否则每个表单都要重复写样式。

| iOS 组件 | 文件 | 作用 | 关键样式 |
|---|---|---|---|
| `Field` | `Field.swift` | 标签 + 内容 + 提示/错误的包裹器 | 标签 13sp/600/色 `T.inkSub`；`required=true` 时标签后跟红色「*」；下方 `hint`（11sp 灰）或 `error`（11sp 红）二选一 |
| `TField` | `Field.swift` | 单行输入框 | 高 48、圆角 12、内边距水平 14、字号 15、底色 `T.pearl`、边框 `T.hair`，聚焦时边框变 `T.primary` 且加粗到 1.5。支持 `keyboard`（`.phonePad` 电话键盘 / `.numberPad` 数字键盘）、`secure`（密码） |
| `TArea` | `Field.swift` | 多行文本框 | 高 = `rows × 22 + 20`、圆角 12、底色 `T.hairSoft`、边框 `T.hair`；空时左上显示 placeholder（14sp 灰） |
| `ApplyDateField` | `ApplyFormSupport.swift` | 日期选择器 | 紧凑式 DatePicker，locale 固定 `ja_JP`，可传 `minDate` 限制最早可选日；高 42、圆角 10、底 `T.paper`、边 `T.hair` |
| `ApplyTimeField` | `ApplyFormSupport.swift` | 时刻选择器（时:分） | 同上，只显示时分 |
| `ApplyFormSectionLabel` | `ApplyFormSupport.swift` | 区块编号标签 | 圆形 22×22 蓝底白字编号 + 14sp/700 区块名 |
| `ChipGroup` | `ApplyStubs.swift` | 单选「药丸」按钮组（横向自动换行） | 选项用 `FlowLayout` 排，选中项蓝底白字、未选白底深字+灰边，胶囊形 |
| `FlowLayout` | `ApplyStubs.swift` / `HomeStubs.swift` | 子项横排满了自动换行的布局 | iOS 用 `Layout` 协议实现；Android 用 `FlowRow`（accompanist 或 Compose 1.4+ 自带）直接替代 |
| `RadioCard` | `UIAtoms.swift` | 单选卡片（带圆形单选钮 + 标题 + 可选副标题） | 圆形选钮（选中蓝）+ 标题 15sp/600 + `detail` 12sp 灰；选中底 `T.pill`、未选底 `T.hairSoft`，整卡可点 |
| `PrimaryButton` | `PrimaryButton.swift` | 主操作按钮 | 高 52、圆角 16、字 16/700、白字；启用时径向渐变蓝（`T.accentSoft→T.accent→T.primary`）+ 阴影；禁用时填 `T.inkFaint` 灰 |
| `SectionLabel`（StayForm 私有） | `ApplyStubs.swift` | 同 `ApplyFormSectionLabel`，但编号背景是圆角 6 方块不是圆形 | 22×22 圆角方块蓝底白字 13sp/700 |
| `InfoRow`（StayForm 私有） | `ApplyStubs.swift` | 只读信息行（左标签固定宽 88 + 右值） | 行高内边距水平 16 垂直 12，非首行顶部 0.5 细线分隔 |

另有底部「提出する」按钮的两个变体：
- StayForm / GenericApplyForm 用 **双按钮行**：左「下書き保存」（白底描边灰字）+ 右「提出する / 次へ · 確認」（蓝底白字，`canSubmit=false` 时变灰禁用）。
- DormLifeForms 用私有函数 `submitButton(title:canSubmit:action:)`：单个 52 高蓝底白字按钮，禁用变灰。

#### Android 对齐要点（组件层）

- 先在 Android 建一个 `forms/` 组件包，逐个对应：`AppField`、`AppTextField`、`AppTextArea`、`AppDateField`、`AppTimeField`、`SectionLabel`、`ChipGroup`、`RadioCard`、`PrimaryButton`。
- `TField`：Compose 用 `OutlinedTextField` 或自绘 `BasicTextField` + `Box`，高度固定 48.dp，聚焦态用 `interactionSource.collectIsFocusedAsState()` 切边框色。`keyboard` 映射到 `KeyboardOptions(keyboardType = KeyboardType.Phone / Number)`。
- `TArea`：`BasicTextField` 多行，高度 `rows*22 + 20`.dp，空时叠一层 placeholder。
- `ApplyDateField` / `ApplyTimeField`：Compose 没有内嵌紧凑 DatePicker，需点击弹 `DatePickerDialog` / `TimePickerDialog`，框里显示已选值文本（日期格式 `yyyy-MM-dd` 用日语 locale，时刻 `HH:mm`）。`minDate` 用 `selectableDates` 限制。**时区固定 `Asia/Tokyo`**（见第 7 节，不能用设备本地时区，否则提交日期会偏一天）。
- `ChipGroup`：`FlowRow` + 每个 chip 是带状态色的 `Surface`/`Box`，点了回调改选中值。
- `RadioCard`：`Row` + 自绘圆形选钮 + 文本列，整行 `clickable`。
- `PrimaryButton`：`Button` 自定背景，启用态用 `Brush.radialGradient`，禁用态灰底。

---

### 2. StayForm —— 出寮届（外泊 / 帰省 / 帰国 三合一，最复杂）

这是整个申請模块最重要的表单，三种 kind 共用，按 kind 累积显隐区块。页面标题 = `"<类型名>申請"`（如「外泊申請」）。

#### 2.1 画面结构（从上到下）

1. **kind 提示横幅**（黄色背景，圆角 12）—— 按 kind 三选一：
   - 帰省：「⏰ 帰省申請は毎週水曜日 18:00 が締切です」
   - 帰国：「✈️ 帰国申請は航空券確定後に提出してください」
   - 外泊：「📝 外泊申請は出発 3 日前までに提出してください」
2. **Header 卡**（淡蓝底+蓝边）：左图标方块（类型 icon，蓝底白字）+「<类型名>許可願」+ 副标题「朝日塾中等教育学校 国際交流部寮」。
3. **§1 申請者本人**（只读 InfoRow 列表，6 行）：
   - 「学号」= 6 桁学号；「氏名」；「学年・組」= 「N年X組  M番」；「寮・部屋」；「区分」（一般寮生 / 留学生）；「携帯電話」。
   - 卡下方灰字注记：「※ ログイン中のアカウントで提出されます。他の生徒の代理提出はできません。」
4. **§2 連絡先・届の区分**（卡）：
   - `Field`「本人連絡先（携帯電話）」→ TField，placeholder「090-0000-0000」，电话键盘。
   - **仅帰省**：`Field`「帰省届の区分」→ ChipGroup，选项 `["通常時用", "長期休暇用"]`（绑定到布尔 `isLongVacation`）。
5. **§3 出寮**（卡）：
   - 「出寮日」：DateField（minDate=明天）+ TimeField 并排；下方灰字「※ 出寮日は明日以降のみ選択できます」。
   - 「帰省方法」（帰省时）/「出寮方法」（其余）：ChipGroup，选项 `["西口1便","西口2便","金川1便","金川2便","寮生特別運行","JR","自家用車","タクシー","教員","その他"]`；下方有「寮生特別運行の時刻表を見る」链接按钮（跳巴士时刻表页）。
   - **连动**：出寮方法选了「タクシー」→ 当场露出「タクシー希望時刻」TimeField。
6. **§4 帰寮**（卡）：
   - 「帰寮日」：DateField（minDate=出寮日）+ TimeField 并排。
   - 「帰寮方法」：ChipGroup，选项 `["西口登校便","金川登校便","寮生特別運行","JR","自家用車","タクシー","教員","その他"]`；下方同样有「寮生特別運行の時刻表を見る」链接。
7. **§5 同行者・行先・外泊地点**（**仅 外泊 / 帰国**）（卡）：
   - `Field`「同行者」→ TField，placeholder「同行者がいる場合は入力」。
   - **仅 外泊（帰国隐藏）**：`Field`「行先（都市名）」→ TField，placeholder「例：東京 / 大阪 / ソウル」。
   - 「宿泊先」：可增删的住所输入行列表（每行 TField placeholder「宿泊先住所」+ 行数>1 时右侧红色减号删除按钮）；底部「地点を追加」蓝色加号按钮；灰字「※ 複数の地点に滞在する場合はすべて入力してください」。
8. **§6 寮食堂 食事申告**（**仅 外泊 / 帰国**）（卡）—— 分两种用户：
   - **留学生**（`isOverseas=true`）：开关「食事不要期間を申告する」；开关开时显示「不要 開始」（DateField minDate=出寮日 + 餐次 ChipGroup `["朝食","昼食","夕食"]`）+「不要 終了」（DateField minDate=开始日 + 餐次 ChipGroup）；灰字「※ 上記期間（開始の食事から終了の食事まで）の寮食堂を不要とします」；再加一个「食事備考」TArea（placeholder「例：8月10日朝食まで必要、8月20日夕食から必要」，3 行）。
   - **日本人**（`isOverseas=false`）：不显示开关，只显示文本「食事は食事入力表でご記入ください」+ 灰字「※ 日本人生徒の食事変更は学校指定の食事入力表で扱います。」。
9. **§7 飛行機**（**仅 帰国**）（卡）：
   - `Field`「出発空港」(required) → TField placeholder「出発空港名」。
   - 「出発時刻」→ TimeField。
   - `Field`「到着空港」(required) → TField placeholder「到着空港名」。
   - 「到着時刻」→ TimeField。
10. **§8 理由**（全 kind 共通，**区块编号动态**：帰国=8 / 外泊=7 / 帰省=5）：标签「帰省の理由」/「帰国の理由」/「外泊の理由」三选一；TArea placeholder「理由を入力してください」，3 行。
11. **底部双按钮行**：「下書き保存」（点了弹 toast「下書き保存しました」，纯演示不存）+「提出する」（`canSubmit` 控制启用）。
12. 底部居中灰字：「提出後は担当の先生へメールで承認依頼が送信されます。」

#### 2.2 字段累积（哪种 kind 显示哪些区块）

- **帰省**：§1 §2(含届区分) §3 §4 §8。
- **外泊**：帰省的全部 + §5(同行者/行先/宿泊先) + §6(食事)。
- **帰国**：外泊的全部，但 §5 隐藏「行先」，加 §7(飛行機)。

#### 2.3 提交可否（canSubmit）与校验

- `reason` 非空。
- `帰寮日+帰寮時刻` 必须晚于 `出寮日+出寮時刻`（合成完整时间后比较，防同日时刻倒挂）。
- 外泊/帰国：宿泊先至少 1 行非空（trim 后）。
- 帰国：出発空港 + 到着空港都非空。
- 食事不要期間展开后若为空数组（如起「夕食」终「朝食」同一天），弹 toast「食事不要期間が空です。開始・終了の食事の順序をご確認ください」并阻止提交。

#### 2.4 数据源 / 提交（生产接真后端）

提交走 `POST /api/v1/applications`，按 kind 用 3 个不同的请求体（字段名 snake_case，跟后端逐字对齐，见 `ApplicationsCreateBodies.swift`）：

- **帰省** → `KisheiCreateBody`：`kind="帰省"`, `reason`, `contact_phone`, `meal_note`, `is_long_vacation`, `leave_date`, `leave_method`, `leave_time`(「HH:mm:ss」), `return_date/method/time`, `taxi_reservation_time`(「HH:mm:ss」或 null)。
- **外泊** → `GaihakuCreateBody`：帰省全部字段去掉 `is_long_vacation`，加 `companion`, `dest_cities`, `stay_locations`(对象数组 `{kind,name,address,phone}`，至少 1 件), `meals_skip`(数组 `{date,meal}`)。
- **帰国** → `KikokuCreateBody`：外泊全部 + `flight_dep_air`, `flight_dep_at`(ISO 带 +09:00), `flight_arr_air`, `flight_arr_at`。

提交格式细节：
- 时刻发后端要补「:00」秒（如「18:00」→「18:00:00」）。
- `stay_locations`：UI 只填地址，所以每条 `kind="その他"`、`name` 和 `address` 都填地址、`phone=null`。
- `meals_skip`：把「起始日+起始餐」到「结束日+结束餐」按 `["朝食","昼食","夕食"]` 顺序逐顿展开成数组（日本人不发；留学生且开关关闭也不发）。
- 航班时刻：TimeField 只有时分，要跟对应日期合成（出发跟出寮日 / 到着跟帰寮日），输出带 +09:00 的 ISO 字符串。
- 成功 → toast「<类型名>申請を提出しました」→ 跳完成页 `applyDone(kind)`；422 错误原样弹后端日语消息；401 清登录态跳登录页；网络错弹「通信エラーが発生しました。電波を確認してください」。

本人信息预填：进页面（`onAppear`）+ 真实用户晚到时（`currentUser` 变化）把本人电话预填进「本人連絡先」框，只填一次（`didPrefillContact` 守卫），允许学生改。生产构建只在拿到真实用户后填，演示构建直接用 SEED 假人电话。

#### Android 对齐要点（StayForm）

- Android 现在完全没有这个表单。要建 `StayFormScreen(kind: String)`，用一个 `ViewModel` 持有所有状态（出寮/帰寮日时、方法、宿泊先列表、食事申告、航班、理由、本人电话等），用 `derivedStateOf` 算 `canSubmit`。
- 三 kind 显隐：用 `if (needPlaces) {...}` / `if (needSkipMeal) {...}` / `if (needFlight) {...}` 在 Composable 里直接条件渲染，跟 iOS 一致。
- 宿泊先增删列表：用稳定 id（`UUID` 或自增）当 `key`，`LazyColumn`/普通 `Column` + `remember { mutableStateListOf<StayPlace>() }`，**不要用数组下标当 key**（删中间行会串内容，iOS 这里踩过 IX-032 坑）。OnlineForm 的时段列表同理。
- 本人信息只读区：从登录态用户对象读，做成只读 `Row` 列表。
- 提交：Android 需新建网络层（Retrofit/Ktor），`POST /api/v1/applications`，按 kind 序列化 3 种请求体。字段名 snake_case 必须 byte-perfect 对齐后端，可用 `@SerializedName` / `kotlinx.serialization @SerialName`。
- 错误处理映射 iOS：422→弹后端消息、401→清 token 跳登录、网络→固定日语提示。
- 食事展开、航班 ISO 合成、时刻补「:00」这些纯逻辑直接照 iOS 翻译成 Kotlin。

---

### 3. StudyAbsenceForm —— 学習欠席届（晚自习请假）

页面标题「学習欠席届」。结构（从上到下，整页一个 ScrollView，间距 16）：

1. **§1 欠席する日付**：DatePicker（紧凑），可选范围 = 今日 ～ 14 日后；框圆角 10、底 `T.paper`、边 `T.hair`。
2. **§2 欠席する範囲**：3 个单选行（圆圈选中变实心勾 `checkmark.circle.fill`，未选 `circle`），选中行淡蓝底+蓝边：
   - 「前半節（19:40〜20:40）」（值 `first`，发后端 `first_half`）
   - 「後半節（20:45〜21:45）」（值 `second`，发后端 `second_half`）
   - 「両方」（值 `both`，发后端 `full`）
3. **§3 理由（必須）**：TextEditor 多行（最小高 120），空时 placeholder「欠席する理由を入力してください」。
4. **提出する** 按钮（胶囊形蓝底白字，48 高）。

**提交**：理由 trim 后非空才允许（否则 toast「理由を入力してください」）。调 `app.submitStudyLeave(targetDate:reason:range:)`，`targetDate` 格式「yyyy-MM-dd」（JST），`range` 用 `wireValue`（first_half/second_half/full）。成功跳 `applyDone(kind:"studyAbsence")`；422 弹后端消息（如同日重复提交 / 超 14 日范围）；401 清 token；网络错固定日语提示。

#### Android 对齐要点

- 建 `StudyAbsenceFormScreen`。范围用 enum `StudyLeaveRange { FIRST, SECOND, BOTH }`，各带 `label`（日语）+ `wireValue`（first_half/second_half/full）。
- 日期范围限制：`DatePickerDialog` 的 `selectableDates` 限今日～+14 天。
- 单选行：自绘 `RadioButton` 行，选中态换图标 + 背景色。

---

### 4. StudyOnlineForm —— オンライン学習申請（带文件上传 + 周课表）

页面标题「オンライン学習申請」。结构：

1. **「提出済み一覧」** 跳转按钮（淡底胶囊，跳 `studyOnlineList`）。
2. **黄色提示横幅**：图标 + 「オンライン学習開始の 3 日前までに提出してください」。
3. **§1 期間**（卡）：
   - `Field`「開始日」(required, hint「オンライン学習開始の 3 日前までに提出してください」) → ApplyDateField，minDate = 3 天后（JST 日历）。
   - `Field`「終了日」(required) → ApplyDateField，minDate = 開始日。
4. **§2 曜日・時間**（卡）：周一～周五（「月」「火」「水」「木」「金」）每天一块：
   - 标题「<曜日>曜日」+ 右侧蓝加号「+」按钮（加一个时段）。
   - 无时段时显示灰字「申請なし」。
   - 有时段时每行：起 TimeField「〜」终 TimeField + 红减号删除（默认时段 19:40〜21:00）。
5. **§3 契約書**（卡）：
   - `Field`「契約書ファイル」(hint「契約書の写真または PDF を添付してください（任意）」) → **ContractFilePicker**（见第 5 节）。
   - `Field`「補足説明」(hint「契約書の内容・受講証明・リンクなど（任意）」) → TArea placeholder「契約書や受講証明の内容・リンクを入力」，3 行。
6. **§4 理由**：`Field`「理由」(required) → TArea placeholder「オンライン学習を希望する理由を入力してください」，4 行。
7. **提出する** 按钮（提交中显示「提出中…」并禁用，防连点）。

**canSubmit**：理由非空 + 終了日≥開始日 + 至少有一个时段 + 所有时段 end>start。

**提交**（两步）：先 `StudyAPI.submitOnlineRequest(body)`（`OnlineRequestBody`：`reason`, `period_from`(yyyy-MM-dd), `period_to`, `weekly_schedule`(字典 `{曜日: [{start,end}]}` 时刻为「HH:mm」), `contract_ref`)；若选了契約書文件，建好申请后第二步 `StudyAPI.uploadOnlineContract(requestId,fileData,fileName,mimeType)` 上传文件。文件上传失败不回退申请，弹「申請は提出されましたが契約書の添付に失敗しました」仍跳完成页。成功 toast「オンライン学習申請を提出しました」→ 完成页。

#### Android 对齐要点

- 建 `StudyOnlineFormScreen`。周课表用 `Map<String, SnapshotStateList<ScheduleSlot>>`，每个 slot 带稳定 id。
- 两步提交（建申请→传文件）照 iOS 逻辑。`weekly_schedule` 是 `Map<String, List<Map<String,String>>>`，序列化时注意键是日语单字。
- 文件上传用 `multipart/form-data`（Retrofit `@Multipart` + `@Part MultipartBody.Part`）。

---

### 5. ContractFilePicker —— 契約書文件选择（图片/PDF）

`StudyOnlineForm` 的 §3 用。组件状态 = 一个可空 `PickedContract`（含 `data`/`fileName`/`mime`）。

- 未选文件时：虚线描边按钮，回形针图标 +「契約書を添付」（蓝字，44 高）。
- 点了从底部弹**三选项菜单**（标题「契約書を追加」）：
  - 「写真を撮る」（拍照，相机不可用时不显示此项）
  - 「アルバムから選ぶ」（相册）
  - 「ファイルを選ぶ」（选 PDF/图片文件）
  - 「キャンセル」
- 已选文件时：横行卡（淡底 `T.pill`），左文件类型图标（PDF=`doc.fill` / 图片=`photo.fill`）+ 文件名 + 大小文本 + 右侧灰色「×」删除按钮。
- 错误时下方红字（如「画像の読み込みに失敗しました」「ファイルの読み込みに失敗しました」「対応していないファイル形式です」「ファイルが大きすぎます（10 MB 以下にしてください）」）。

**处理逻辑**：所有图片（含 HEIC）统一转 JPEG（最长边缩到 2400、压缩质量 0.8），PDF 原样；客户端先拦 >10 MB（后端也会拦，这里给即时反馈）。

#### Android 对齐要点

- 用 `ActivityResultContracts`：`TakePicture`（拍照）/ `PickVisualMedia`（相册图片）/ `GetContent` 或 `OpenDocument`（选 PDF/图片）。底部三选项用 `ModalBottomSheet`。
- HEIC→JPEG：Android 拍照/选图后用 `BitmapFactory` 解码 + 缩放（最长边 2400）+ `compress(JPEG, 80)`，PDF 原样读字节。客户端拦 10MB。
- `PickedContract` 数据类 = `data: ByteArray` + `fileName: String` + `mime: String`（"image/jpeg" / "application/pdf"）。

---

### 6. GenericApplyForm —— 通用桩表单（outing / repair / parcel / guest / return）

这是**纯演示桩**，未接后端，提交只跳确认页 `applyPreview(kind)`。标题「<类型名>申請」。结构按 kind 动态：

- **Header 卡**（淡蓝底蓝边）：类型 icon + name + desc。
- 条件字段（按 kind 显隐）：
  - 行き先（outing/stay/holiday，required，placeholder「行き先を入力」）
  - 来訪者氏名（guest，required，placeholder「来訪者氏名を入力」）
  - 荷物の概要（parcel，required，placeholder「配送業者・個数」）
  - 日付 / 開始日 / 終了日（DateField，非 repair/parcel/outing 显示）
  - 帰寮予定時刻（TimeField，非含终止日且非 repair/parcel/outing）
  - 交通手段（ChipGroup `["電車","バス","車","徒歩","その他"]`，默认「電車」）
  - **タクシー予約**（仅 outing）：开关「タクシーを予約する」+ 开时显 TimeField
  - **修繕专属**：「場所」(required) 4 个 RadioCard「自室」「共用スペース」「水回り」「その他」；「写真」虚线框「写真を追加（任意）」（桩，不真上传）
  - 「不具合の内容」（repair）/「理由・詳細」(required，TArea，placeholder repair=「状態を具体的に」/ 其他=「申請の理由を具体的に」)
  - 連絡先（非 repair/parcel，hint「緊急時用」，电话键盘）
  - **保証人**（stay/holiday）：「保証人連絡先」TField「保護者電話番号」+ 黄底确认勾选框「外泊・帰省は保証人の同意が必要です。上記の保証人に連絡済み／同意を得ていることを確認します。」
- 底部双按钮：「下書き保存」+「次へ · 確認」。

#### Android 对齐要点

- 这是桩，可低优先级，但为了「跟 iOS 一模一样」也要做。建 `GenericApplyFormScreen(kind)`，按 kind 用 `when`/`if` 显隐字段，提交只导航到确认页，不发网络。

---

### 7. 日期/时区处理（全表单必须一致）

iOS 用 `ApplyFormDate` / `StayForm` 的静态方法，**关键：所有日期格式化固定 `Asia/Tokyo` 时区**（`formatYMD` / `parseYMD` 都固定 JST），否则非日本时区设备提交的「出寮日 / period_from」会偏一天（这是踩过的 IX-034 / Codex 6-03 坑）。

- 日期串「yyyy-MM-dd」（JST）；时刻串「HH:mm」（发后端补「:00」秒）。
- 「3 日后」「明天」也按 JST 日历算（`tokyoCalendar`），不随设备时区漂。
- 航班 datetime 输出带 +09:00 的 ISO 8601（不是 UTC 的 Z）。

#### Android 对齐要点

- Kotlin 用 `java.time` + `ZoneId.of("Asia/Tokyo")`。格式化器 `DateTimeFormatter.ofPattern("yyyy-MM-dd")` / `"HH:mm"` 都绑 JST。日期选择器的 minDate（明天 / 3 日后）也按 JST 算。航班用 `OffsetDateTime` 带 +09:00 输出。

---

### 8. RenewStudentNoSheet —— 番号再設定弹窗（学籍番号自设）

不在 Apply 模块，在 `Home/HomeStubs.swift`，学年更新后让学生自设新番号。用 **GlassSheet**（毛玻璃底部弹窗）包裹。结构：

1. 标题「学籍番号の再設定」（20sp/heavy）。
2. 说明灰字「新学年の 学年・組・出席番号 を選んでください。学籍番号は自動で計算されます。」。
3. **学年**（必填，label 后红「*」）：`FlowLayout` 6 个 `radioChip`（选中蓝字+淡蓝底+蓝边）：
   - 「中1」(01)「中2」(02)「中3」(03)「高1」(04)「高2」(05)「高3」(06)
4. **組**（必填）：2 个 radioChip「A組」(01)「B組」(02)。
5. **出席番号**（必填）：TField，placeholder「例: 18」，数字键盘，只留数字最多 2 位。
6. **实时预览**：学年/组/番号三段齐了（番号 1～99）显示「新しい学籍番号: <学年码><组码><两位番号>」（蓝字）。
7. **更新する** PrimaryButton（提交中「送信中…」，`canSubmit` 控制启用）。

**radioChip** 是这个弹窗私有的单选药丸：14sp（选中加粗）、内边距水平 16 垂直 10、圆角 12、选中淡蓝底蓝边、未选 `T.pearl` 底灰边。

**提交**：番号补成 2 位（如 `5`→`05`），调 `app.submitRenewStudentNo(gradeCode:classCode:seatNo:)`。撞号后端返 422 → 原样弹日语提示，留在弹窗让学生改；成功后关弹窗（成功 toast 在 store 内部弹），顶部「番号再設定」按钮消失。

#### Android 对齐要点

- 用 `ModalBottomSheet` + 毛玻璃/半透明背景对应 `GlassSheet`。
- 学年/组用 `FlowRow` + 自绘单选药丸。出席番号 `TextField` 数字键盘 + `filter { it.isDigit() }.take(2)`。
- 实时预览拼串：`"$gradeCode$classCode${seat.padStart(2,'0')}"`。
- 提交后 422 弹后端消息留窗、成功关窗刷新登录态（清 `needsRenewal` 让顶部入口消失）。

---

### 9. 确认页 / 完成页 / 详情页（GenericApplyForm 链路 + 完成页通用）

- **ApplyPreviewView**（确认页，桩）：标题「申請内容の確認」。蓝底信息条「ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。」+ 一张只读键值卡（按 kind 列不同行，含写死的演示值如「申請番号 A-TEMP」）+ 底部「戻る」+「提出する」。提交弹 toast「申請を提出しました」延迟跳完成页。
- **ApplyDoneView**（完成页，所有真表单提交成功都跳这）：居中渐变圆角勾标 + 大标题「申請を提出しました」+「<类型名>申請を受け付けました。\n審査完了時に通知でお知らせします。」+ 信息卡「予想審査時間 1〜2 時間」+「一覧へ」按钮（回申請列表）。
- **ApplyDetailView**（详情页）：出寮届系走真后端 `StayDetailView`，其余演示桩走 3 步进度时间线（提出→審査→完了；外出特殊为 2 步 提出→先生の確認待ち/確認）。

#### Android 对齐要点

- 完成页 `ApplyDoneScreen(kind)` 是所有真表单共用，优先做。确认页/详情页跟 iOS 一样按 demo 桩 vs 真后端分流。完成页文案逐字照抄。

---

I now have all the data I need. Producing the alignment spec.

## マイページ（個人页 / MyPage）

> iOS 真值源：`03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift`（2342 行，13 个 View + 1 弹窗）。数据源 `Foundation/Seed/SEED.swift` + `Foundation/Seed/SeedModels.swift`（演示假数据 `SEED`）。本块覆盖个人页全部画面，**减点折线图（`MyPointsChartView` 的 `chartCanvas`）由另一份对齐稿负责，本稿仅列出它的入口与外壳**。对应截图 11 / 12。

「個人页」= マイページ，底部导航第 4 个 tab（首页 / 申請 / 外泊一覧 / マイページ）。它本身是一个 L1 着陆页（`MyLandingView`），底下挂 12 个 L2/L3 子页 + 1 个登出弹窗。

---

### 0. 共享主题 token（Android 必须先建一份对照表）

iOS 全局色板在 `Foundation/Theme/TTokens.swift`（代号 `T`）。Android 在 Compose 里建一个等价的 `object T { ... }` 或 `Color` 常量集，所有个人页颜色都引用它，**不许散落写 hex**：

| iOS token | hex | 用途 |
|---|---|---|
| `T.primary` | `#1F6B74`（深青绿 teal） | 主色：图标 / 强调文字 / 进度条 |
| `T.primaryDk` | `#0E3840` | 更深青绿：info box 文字 / 关于页大字 |
| `T.accent` | `#5FBEC8` | 亮青绿：Pill accent 色 |
| `T.pearl` | `#EFF2F3` | 页面背景（米白）|
| `T.paper` | `#FFFFFF` | 卡片背景（纯白）|
| `T.ink` | `#0F1E22` | 主文字（近黑）|
| `T.inkSub` | `#56707A` | 副标题 / 标签文字 |
| `T.inkMute` | `#93A4AC` | 弱化文字 / 日期 |
| `T.inkFaint` | `#C4D0D5` | 浅灰：列表箭头 |
| `T.hair` | `#0F1E22` @ 8% 透明 | 分隔线 / 卡片描边 |
| `T.pill` | `#1F6B74` @ 8% 透明 | 灰底 pill / 规则盒底色 |
| `T.warn` | `#D1984A` | 警告橙：遅刻 |
| `T.warnBg` | `#FDF4E1` | 警告底色 |
| `T.warnDeep` | `#7A4A0E` | 深警告色 |
| `T.danger` | `#C44848` | 危险红：欠席 / 退回 / 登出 |
| `T.dangerBg` | `#FDE8E8` | 危险底色 |
| `T.ok` | `#4A9478` | 通过绿：時間内 |
| `T.okBg` | `#E3F1EA` | 通过底色 |
| `T.okDeep` | `#2C6048` | 深绿 |

圆角：`Radius.sm = 12` / `md = 16` / `lg = 22` / 卡片普遍 `18`。卡片阴影 iOS 用两层（`opacity 0.04 radius 2 y1` + `opacity 0.05 radius 14 y4`）—— Android 用 `Modifier.shadow(elevation = 2.dp ... )` 近似即可，不必逐像素抠。

---

### 1. 画面一覧（13 屏 + 1 弹窗）

| # | iOS View | 画面标题（PageHeader） | 层级 | 进入方式 |
|---|---|---|---|---|
| 1 | `MyLandingView` | 「マイページ」 | L1（左上 Home 图标，点回首页） | 底部 tab |
| 2 | `MyInfoView` | 「個人情報」 | L2（左上返回箭头） | 履歴格子「個人情報」 |
| — | `MyInfoEditView` | 「連絡先・部屋編集」 | L3 | 个人情报页内「学年・組…を編集」按钮 |
| 3 | `MyRollcallView` | 「点呼履歴」 | L2 | 「今月の点呼」卡 |
| 4 | `MyRollcallDetailView` | 「点呼セッション詳細」 | L2 | 点呼履歴里某一行 |
| 5 | `MyPointsView` | 「減点明細」 | L2 | 「減点明細」卡 / 格子无（卡进入） |
| 6 | `MyPointsChartView` | 「減点グラフ」 | L2 | 减点明细页右上「グラフ →」**（图表本体另稿）** |
| 7 | `MyDisciplineView` | 「処分履歴」 | L2 | 履歴格子「処分履歴」 |
| 8 | `MyHealthView` | 「体調報告履歴」 | L2 | 履歴格子「体調報告履歴」 |
| 9 | `MyCleanView` | 「掃除提出履歴」 | L2 | 履歴格子「掃除提出履歴」 |
| 10 | `MyPackagesView` | 「荷物受取履歴」 | L2 | 履歴格子「荷物受取履歴」 |
| — | `MyStudyView` | 「学習履歴」 | L2 | 「学習ステータス」卡 |
| 11 | `MySettingsView` | 「通知設定」 | L2 | 设置列表「通知設定」 |
| 12 | `MyAboutView` | 「Tomoshibi について」 | L2 | 设置列表「Tomoshibi について」 |
| 13 | `LogoutSheet` | （弹窗，无 header） | 弹窗 | 设置列表「ログアウト」 |

「申請履歴」格子例外：它不进个人页内的子屏，而是路由到外部「外泊一覧」屏（`Route.stayList`），那屏归别人对齐。

---

### 2. `MyLandingView`（L1 着陆页）— 个人页主屏，对应截图 11

页面整体：`PageHeader(title:"マイページ", level:1)` 固定在顶，下面是一个 `ScrollView`，背景 `T.pearl`。滚动区从上到下 6 块，每块左右 padding 16：

#### 2.1 头像档案卡（profileSection）

一张 `Card(padding: 18)`，内部水平排列：
- 左：圆形头像 `Avatar(letter: 用户头像字, size: 56)`。头像 = 用户名首字（演示假数据是「リ」），圆形纯色底（`T.primary` 系），白字居中，字号 = 直径 × 0.44。
- 右：竖排 4 行，间距 4
  1. 姓名：`name`，18pt heavy（演示假数据「リュウ イヒ」）
  2. 一行账号：小字「アカウント 」(11pt, `T.inkMute`) + 账号 `account`（11pt bold 等宽字体 monospaced，演示假数据「060218」）
  3. 两个 Pill 横排，间距 6：第一个 `accent` 色 = 「{寮} {房间}」（演示「男寮 A5」）；第二个 `neutral` 灰色 = `category`（演示「一般寮生」）
- 最右：`Spacer`

> **共享组件 `Pill`**：iOS `Pill(text:tone:)`，tone ∈ {neutral, ok, warn, danger, accent}，胶囊形，11pt semibold。Android 做成 `@Composable fun Pill(text, tone)` —— accent 用青绿底白字，neutral 用灰底深字。
> **共享组件 `Avatar`**：iOS `Avatar(letter:size:)`。Android 做成 `Box` 内 `Text` 居中 + `CircleShape` 背景。

#### 2.2 行事予定卡（scheduleCard）

整张卡可点（点了去 `Route.schedule` 日程屏）。卡片背景白 + 阴影 + `T.hair` 0.5 描边，圆角 18，内 padding 16：
- 头部一行：左 40×40 圆角方块（`T.primary` 10% 底）内放日历图标 `Ic.calendar(20)` 青绿色；中间「行事予定」15pt heavy；右侧「すべて見る」11pt + 右箭头 `Ic.chevR(12)`，都青绿色
- 列表（最多 3 条，今日含之后最近的活动；演示版「今日」固定 `2026-04-23`，生产版取东京时区今日）：
  - 空时显示「当面の予定はありません」12pt `inkMute`
  - 有时每条 `scheduleRow`：左 40 宽竖块（上「{月}月」10pt 青绿 / 下「{日}」18pt heavy rounded）+ 1pt 竖线 `T.hair` 高 32 + 右竖排（标题 13.5pt bold 单行 / 场所 11pt `inkSub` 单行，场所空则不显）。条目间 0.5pt `T.hair` 横分隔线
  - 演示数据近期取 `SEED.events`（如「誕生日会 / カフェテリア」「避難訓練 / 寮玄関前集合」「茶道部体験 / 和室」等）

#### 2.3 主要状态卡群（3 张竖排，间距 10）— 截图 11 主体

3 张卡共用同一个外壳：白底 + 双层阴影 + 0.5pt `T.hair` 描边 + 圆角 18 + 内 padding 16，整卡可点。左侧 48×48 圆角方块放 emoji，右侧竖排文字，最右 `Spacer`。

**A. 学習ステータス卡**（`studyStatusCard`，点去 `Route.myStudy`）
- 方块底色 `T.primary` 10%，emoji「📚」22pt
- 右：第 1 行「学習ステータス」12pt semibold `inkSub`；第 2 行状态文字 16pt heavy（4 种：`.idle`→「対象外（今日）」/ `.upcoming`→「開始まで M:SS」倒计时 / `.active`→「進行中」/ `.done`→「本日完了 ✅」）；第 3 行「履歴を見る →」11pt 青绿
- **入口始终显示**：即使该生非晚自习对象也显示这张卡，点进去由 `MyStudyView` 自己显示「学習対象外です」

**B. 今月の点呼卡**（`rollcallStatusCard`，点去 `Route.myRollcall`）
- 方块底色 `T.okBg`，emoji「📋」22pt
- 右：第 1 行「今月の点呼」；第 2 行三个统计块横排（间距 12），每块 = 数字（17pt heavy 等宽）+ 小标签（10.5pt）：「{n} 時間内」绿 / 「{n} 遅刻」橙 / 「{n} 欠席」红；第 3 行「詳細を見る →」
- 统计口径：只数当月记录。演示版固定「2026-04」前缀过滤 `SEED.rollcall`（34 条里 04 月全部），生产版取系统当前年月

**C. 減点明細卡**（`pointsStatusCard`，点去 `Route.myPoints`）
- 方块底色按分数档变（`< 4`→`okBg` / `4–7.9`→`warnBg` / `≥ 8`→`dangerBg`），emoji「📉」22pt
- 右：第 1 行「減点明細」；第 2 行 = 分数（22pt heavy 等宽，颜色按档：绿/橙/红）+「点」12pt + Pill（档位标签：`<4`→「良好」ok / `4–7.9`→「罰掃 注意」warn / `≥8`→「禁足」danger）；第 3 行「詳細を見る →」
- 演示分数 `SEED.user.points = 4.5` → 橙色 + 「罰掃 注意」

#### 2.4 履歴 section header

一行小标题「履歴」11pt heavy `inkSub`，字距 0.6，左 padding 22，下 8。

#### 2.5 履歴宫格（gridSection）— 6 格 2 列

`LazyVGrid` 2 列（Android `LazyVerticalGrid` 或固定 2 列的 Row+weight），格距 10。每格 = 一张白底圆角 16 卡（双层阴影 + 0.5pt 描边），`minHeight 80`，内 padding 14：
- 左上：38×38 圆角方块（`T.primary` 10% 底）放系统线条图标 17pt 青绿
- 底部：标签 13.5pt bold
- 右上角可挂红色徽标 Pill（仅「荷物受取履歴」有，数字 = 待領包裹数；演示有 1 个待領 → 显「1」红底胶囊）

6 格固定顺序与目标路由：

| 标签 | iOS 图标(SF Symbol) | Android 等价图标 | 路由 |
|---|---|---|---|
| 「個人情報」 | `person.text.rectangle` | Icons.Filled.Badge / ContactPage | `myInfo` |
| 「処分履歴」 | `exclamationmark.triangle` | Warning | `myDiscipline` |
| 「体調報告履歴」 | `cross.case` | MedicalServices / HealthAndSafety | `myHealth` |
| 「申請履歴」 | `doc.text` | Description | `stayList`（外部屏） |
| 「掃除提出履歴」 | `sparkles` | AutoAwesome / CleaningServices | `myClean` |
| 「荷物受取履歴」 | `shippingbox` | Inventory2 | `myPackages`（带徽标） |

> SF Symbol 是苹果系统图标名，Android 没有同名，按「Android 等价图标」列挑视觉接近的 Material 图标即可，外观一致比图标 ID 一致重要。

#### 2.6 设置列表（settingsSection）

一张 `Card(padding: 0)`，竖排 3 行，行间细分隔线：
1. 「通知設定」+ 右箭头 → `Route.mySettings`
2. 「Tomoshibi について」+ 右箭头 → `Route.myAbout`
3. 「ログアウト」无箭头，文字红色（`T.danger`）→ 打开 `LogoutSheet` 弹窗

每行 14.5pt medium，左右 padding 18，上下 16。

> 历史去重提示（Android 跟着删，别重新加回来）：以前这里还有「行事予定」「特別運航便」两个入口，已分别搬到本页顶部日程卡 / 首页巴士卡。

---

### 3. `MyInfoView`（個人情報，L2）

`PageHeader("個人情報", level:2)` + `ScrollView`，左右 padding 20。

**A. 信息表卡**：`Card(padding:0)`，10 行键值，行间细分隔线。左列标签固定宽 120（13pt `inkSub`），右列值（13.5pt medium `ink`）。10 行：

| 标签 | 值（演示假数据） |
|---|---|
| 氏名 | リュウ イヒ |
| フリガナ | りゅう いひ |
| 生年月日 | 2006-10-14 (19 歳) |
| 性別 | 男 |
| アカウント番号 | 060218 |
| 学年・組・番号 | 高3 B組 18番 |
| 寮・部屋 | 男寮 A5 |
| 区分 | 一般寮生 |
| メール | demo@example.com |
| 電話 | 090-0000-0000 |

**B. 編集按钮**：青绿 8% 底圆角 12，高 44，居中「✎ 学年・組・番号・部屋を編集」14pt semibold 青绿 → `Route.myInfoEdit`。

**C. 変更履歴**（仅当有改动历史时显示）：小标题「変更履歴」+ `Card`，每条 = 上行（字段标签青绿 12pt + 右侧时间戳 `yyyy-MM-dd HH:mm` 11pt）+ 下行（旧值带删除线 → 「→」→ 新值 bold）。

**D. info box**：青绿 4% 底 + 13% 描边圆角 12，「ℹ 氏名・生年月日・性別・メール・電話などの変更は、寮監にご連絡ください。」12.5pt `primaryDk`。

#### `MyInfoEditView`（連絡先・部屋編集，L3）

`PageHeader("連絡先・部屋編集", level:3)`。底部固定一个 `PrimaryButton("保存する")`（仅三字段都非空才可点）。滚动区：
- **read-only 头**：小标题「変更不可（先生に依頼）」+ `Card`，两行（「学号」+ 值 + 锁图标 / 「氏名」+ 值 + 锁图标）。学号、姓名学生不可改（老师专改）
- **部屋番号**字段：`Field` 内左侧固定显示寮前缀方块（青绿 8% 底，`M`=男寮 / `W`=女寮 / `A`=A 寮，从原房号继承）+ `TField`（数字键盘，只留数字、最多 3 位）
- **メール**字段：`TField`（邮箱键盘）
- **電話**字段：`TField`（电话键盘）
- help box：「ℹ 学号・姓名・生年月日・性別の変更は寮監にご連絡ください。」「変更履歴は次の画面で確認できます。」
- 保存逻辑：拼回前缀 + 数字 = 新房号，逐字段追加到变更履歴，弹 toast「保存しました」后返回

> **共享组件**：`Field`（标签 + required 红星 + hint + 内容槽）、`TField`（单行输入框，带 `keyboard` 类型）、`PrimaryButton`（主按钮，`enabled` 控制可点，`destructive` 控制红色）。Android 各做一个等价 `@Composable`。

---

### 4. `MyRollcallView`（点呼履歴，L2）

`PageHeader("点呼履歴", level:2)` + `ScrollView`，左右 padding 16。

- **月份筛选胶囊**：横排 3 个 `["4月","3月","2月"]`，选中 = 青绿底白字，未选 = `T.pill` 灰底青绿字，12pt semibold，胶囊形（左右 padding 14、上下 6）。点哪个就按那月前缀过滤 `SEED.rollcall`
- **按日期分组列表**：每组 = 日期小标题（11pt 等宽 `inkMute`）+ `Card(padding:0)` 内若干行，行间细分隔线。每行 `rollcallRow` 可点 → `Route.myRollcallDetail(entryId: r.id)`：
  - 左：场次 `朝点呼/晩点呼`（60 宽，13pt semibold）
  - Pill：状态（時間内→ok绿 / 遅刻→warn橙 / 欠席→danger红）
  - 右：方式（11pt 等宽 `inkMute`，演示「NFC」或欠席时「―」）+ 右箭头
- 数据 `SEED.rollcall`：演示从 2026-04-05 到 04-21 每天「朝/晩」两条，特殊日标记遅刻/欠席（如 04-21 朝遅刻、04-20 晩欠席）

### 5. `MyRollcallDetailView`（点呼セッション詳細，L2）

`PageHeader("点呼セッション詳細", level:2)`。按被点那条记录渲染（不是写死）：
- **主卡** `Card(padding:18)`：标题「{date} {场次}」16pt bold 等宽青绿 + 「セッション ID: RC-{纯数字日期}-{AM/PM}」12pt `inkMute` + 一个 2 列网格键值：
  - 固定「状態」「方式」两项；状態文字：遅刻→「遅刻 0.5 点」/ 欠席→「欠席 1.0 点」/ 時間内→「時間内」
  - 「開始時刻」「締切時刻」：朝场「07:00:00 / 07:10:00」，晚场「21:00:00 / 21:10:00」
  - 仅遅刻时多两项：「チェックイン 07:12:34」「遅れ +2分34秒」
- **info box**：青绿 4% 底，「ℹ 改判はされていません」12pt

### 6. `MyPointsView`（減点明細，L2）

`PageHeader("減点明細", level:2, right: グラフ→按钮)` —— 右上「グラフ →」12pt bold 青绿 → `Route.myPointsChart`。滚动区左右 padding 20：
- **琥珀渐变总分卡**：圆角 20，渐变底（左上 `#FFEFC2` → 右下 `#F4C677`），内「今月合計」12pt bold 字距 1.7 大写（深棕 `#5C3410` 80%）+ 大数字（48pt heavy 等宽，`#5C3410`，演示「4.5」）+「点」14pt
- **进度条**：0→8 满刻度。灰底胶囊 + 渐变填充（`#F4C677`→warn）填到 `points/8`；4 处橙竖标、8 处红竖标。下方刻度行「0」「4 清掃罰則」（warnDeep）「8 外出禁止」（danger）
- **明细列表** `Card(padding:0)`：逐条 `SEED.points`（演示 7 条），行 = 日期（80 宽等宽 `inkMute`）+「{场次} · {种类}」+ 右侧「+{值}」（≥1→danger红 / <1→warnDeep）。演示如「2026-04-05 / 朝点呼 · 遅刻 / +0.5」
- **规则盒**（`T.pill` 灰底圆角 12）：「現在のルール: 遅刻 0.5 点 / 欠席 1.0 点」+「月累計 4 点で清掃罰則 · 月累計 8 点で外出禁止」12pt `inkSub`

### 6b. `MyPointsChartView`（減点グラフ，L2）— 外壳

`PageHeader("減点グラフ", level:2)`。一张 `Card(padding:20)`：小标题「過去 12 ヶ月」+ **折线图画布（高 200，本体另稿对齐）** + 图例（橙线「清掃罰則閾値」/ 红线「外出禁止閾値」）。Android 这屏的 header / 卡 / 标题 / 图例照本节做，中间 canvas 等图表对齐稿。演示数据 `[0,0,1,0,0.5,1,0,2,0,1,2,4.5]`，月份标签 `5~4`。

### 7. `MyDisciplineView`（処分履歴，L2）

空状态屏：居中「✨」48pt + 「処分歴はまだありません」14pt semibold `inkSub`，padding 40。演示永远空。

### 8. `MyHealthView`（体調報告履歴，L2）

竖排卡列表（间距 10），逐条 `SEED.health`（演示 2 条）。每条 `Card(padding:14)`：
- 上行：左「{症状}」14pt bold + 体温（有则「{温度}°C」13pt semibold 等宽红色） / 右「{date}」11pt 等宽 `inkMute`
- 下行：备注（非空时，12.5pt `inkSub`）
- 演示：「頭痛 37.2°C / 2026-04-14 / 午後ずっと頭が重い」、「腹痛（无温度）/ 2026-04-03」

### 9. `MyCleanView`（掃除提出履歴，L2）

竖排卡列表，逐条 `SEED.cleaning`（演示 2 条）。每条 `Card(padding:14)`：
- 上行：左竖排「{范围}」14pt bold +「{date}」11pt 等宽 / 右 Pill：有分数显「{状态} · {分}点」，无则只「{状态}」；通過→ok绿 / 退回→danger红
- 退回时多一块红色评语盒（`dangerBg` 底圆角 8）：评语文字红色
- 演示：「部屋 / 2026-04-19 / 通過 · 5点」、「共用エリア / 2026-04-05 / 退回」+ 评语「床が汚れている」

### 10. `MyPackagesView`（荷物受取履歴，L2）

竖排卡列表，逐条 `SEED.packages`（演示 4 条），整卡可点 → `Route.homePackageDetail(id:)`。每条 `Card(padding:14)`：
- 左「📦」28pt + 竖排（「{寄件方}」14pt bold /「{date}」11pt 等宽）+ `Spacer` + 右 Pill（待領→warn橙 / 領済→neutral灰）
- 演示：「宅配便 / 2026-04-22 / 待領」、「佐川 / 領済」、「ヤマト / 領済」、「郵便局 / 領済」

### 10b. `MyStudyView`（学習履歴，L2）

入口 = 着陆页学習卡。`PageHeader("学習履歴", level:2)`：
- **非晚自习对象**（`isStudyTarget == false`）：居中「📚」44pt +「学習対象外です」17pt heavy +「あなたは現在、晩学習（夜間学習）の対象ではありません。\n学習担当の先生が対象に指定すると、ここに出席状況が表示されます。」
- **是对象**：4 块竖排（间距 14）
  - 月度 summary 卡：「今月の学習出席」+ 右上「対象/対象外」胶囊；下方 3 个 statBox（出席 ok / 遅刻 warn / 異常 danger），每块大数字 24pt 等宽 + 「回」，灰底圆角 12
  - 当月欠席届卡：圆形「📝」+「今月の学習欠席届」+ 大数字「{n} 回」（>3 标红 + 右侧「超過」红胶囊）
  - 出席タップ履歴卡：标题「出席タップ履歴」+ 右「{n} 件」；空则「✨ 履歴はまだありません」；有则按日期分组的日块（每天判定齐全→「時間内」绿胶囊 / 齐全且迟到→「遅刻」黄胶囊 / 不齐→「未完」红胶囊；下列各打卡时刻 + tap 标签 + 备注）
  - help box：「ℹ 学習出席は NFC を 1 日 2 回タップ」「学習開始 (19:40) ／ 学習終了 (21:45)。2 回揃わない場合は異常扱いとなり、学習担当の先生が手動で判定します。」

### 11. `MySettingsView`（通知設定，L2）— 对应截图 12

`PageHeader("通知設定", level:2)`，滚动区竖排间距 14：
- **通知开关卡** `Card(padding:0)`，5 行带开关 `TToggle`（默认全开），行间分隔线：「点呼リマインダー」「申請結果」「荷物到着」「活動リマインダー」「減点警告」
- **ダークモード卡**：单行 + 系统 `Toggle`（绑 `app.isDark`），青绿 tint
- **（演示版限定）Push 通知 デモ段**：标题「⚠️ Push 通知 デモ」+「この section は demo 版限定です（production では非表示）。」+ 4 行带「🔔」铃铛 + 「送信」的触发行：「学習欠席届 → 承認」「学習欠席届 → 不承認」「学習対象に追加された」「外泊届（修改届）が再承認された」。**这段只在演示构建里（`#if DEMO`）显示，生产版不编译进去——Android 用对应的 BuildConfig.DEBUG 或 demo flavor 包住，上线版必须不可见**
- **账号删除段**（App Store 强制要求，Android 也保留）：小标题「アカウント」+ `Card` 内红色「アカウントを削除」行 + 右箭头 + 下方「削除すると元に戻せません。」。点击弹确认框：标题「アカウントを削除しますか？」/ 正文「削除すると元に戻せません。点呼履歴・申請履歴・プロフィール情報がすべて閲覧できなくなります。」/ 按钮「キャンセル」「削除する」（红）。删除成功清登录态跳登录页，失败弹「削除に失敗しました」

> **共享组件 `TToggle`**：自定义开关（绑 `Binding<Bool>`）。Android 用 `Switch` 包一层统一样式即可。

### 12. `MyAboutView`（Tomoshibi について，L2）

`PageHeader("Tomoshibi について", level:2)`，居中布局：
- **字标块**：「Tomoshibi」40pt heavy 深青绿 + 「灯 火」14pt semibold 大字距青绿 + 版本号（`AppVersionTag.full`，11pt 等宽 `inkMute`）。Android 用 `BuildConfig.VERSION_NAME` 或一个统一版本常量
- **AC 署名卡**（白底圆角 18 卡）：
  - 「Tomoshibi は、日本の寮での点呼と生活管理を一体化したシステムです。」
  - 「「日本で留学する私にとって、寮は異国の第二の家。このシステムが守るのは『灯火』—— 毎晩学生が無事に帰宅し、部屋に灯りが灯ること。だから日本語名を Tomoshibi（灯火）にしました。」」
  - 分隔线后：「2026 年 AC 入試プロジェクト成果物」「— リュウ イヒ」

### 13. `LogoutSheet`（登出弹窗）

从设置列表「ログアウト」打开，底部弹出玻璃质感半屏（iOS `GlassSheet`，Android 用 `ModalBottomSheet` + 半透明模糊背景）：
- 标题「ログアウトしますか？」20pt heavy
- 正文「次回起動時はアカウント番号と\nパスワードが必要です」13pt 居中
- 两个竖排按钮：`PrimaryButton("ログアウト", destructive: true)`（红）→ 清登录态跳登录页 + `GhostButton("キャンセル")`（描边）→ 关弹窗

> **共享组件 `GlassSheet`**：从底部升起的毛玻璃面板，带 `onClose`（点遮罩 / 拖下关）。`GhostButton`：透明描边按钮。

---

### 导航总则（Android 必须复刻）

- **L1 头**左上是 Home 图标，点回首页（`router.replace(.home)`）；**L2/L3 头**左上是返回箭头，点 `router.back()`。长按头部 0.4 秒触发面包屑（`breadcrumbOpen`）。Android 用 `NavController` / 自建路由栈实现「back / replace」，并给头部图标加 `combinedClickable` 长按。
- 个人页所有「卡 / 行 / 格子」点击都靠一个统一路由枚举跳转（iOS `Route` + `router.go(...)`）。Android 建一个 sealed class 路由 + 类似 `RouterStore` 的状态机，**别用碎片化的 startActivity**，要跟 iOS 一样单 Activity 内栈式切屏。

---

### Android 对齐要点（汇总）

Android 现状（`03_dev/student_android/v1/`）= 纯 UI 桩 + 本地 `MockData.kt`，**没有任何网络层**，个人页要从近乎零搭。要补的：

1. **数据源**：先照 `SeedModels.swift` 14 个结构 + `SEED.swift` 假数据，在 Kotlin 建等价 `data class`（`User / PointRecord / RollcallEntry / HealthRecord / CleaningRecord / PackageItem / EventItem / StudyHistoryEntry`）+ 一个 `Seed` object 装演示假数据（数值逐字照抄上文，尤其 `points=4.5 / lateCount=5 / absentCount=2 / room="A5" / account="060218" / name="リュウ イヒ"`）。生产版接后端时再换数据层，但 UI 先用假数据跑通。
2. **共享组件**：先把 `Pill / Avatar / Card / PageHeader / PrimaryButton / GhostButton / GlassSheet / Field / TField / TToggle / Ic（图标集）` 在 Compose 里各做一个，外观对齐第 0 节色板。这些组件首页 / 申請 / 外泊一覧都复用，先建好一劳永逸。
3. **着陆页结构**：`Scaffold` + 顶 `PageHeader(level=1)` + `LazyColumn`，按 2.1→2.6 六块顺序铺。状态卡群 3 张、履歴 6 格 `LazyVerticalGrid(2 列)`、设置 3 行。
4. **状态联动**：学習卡的 4 态文字、点呼卡当月统计、減点卡分数档位（颜色 + Pill 标签）、包裹徽标数，都要做成根据数据动态算的（不要写死），跟 iOS 一致。
5. **演示版隔离**：`MySettingsView` 的「Push 通知 デモ」段、`SEED` 的假通知，iOS 用 `#if DEMO` 编译隔离。Android 用 `BuildConfig.DEBUG` 或 demo 产品风味（flavor）包住，**上线包必须不可见**（否则变安全漏洞）。
6. **文案逐字照抄**：上文所有「」括起来的日语原文必须一字不差进 Kotlin 字符串资源（建议放 `strings.xml` 用日语 locale），UI 文案保持日语，不许翻成中文 / 英文。
7. **图标差异**：SF Symbol 名在 Android 不存在，按上文宫格表「Android 等价图标」列挑 Material 图标，视觉接近优先。
8. **减点折线图（`MyPointsChartView` 的 canvas 本体）不在本稿**，由另一份对齐稿给 Compose `Canvas` 画法，本稿只交付该屏的 header + 卡外壳 + 图例。

---

I have everything I need. Writing the aligned spec section now.

## 減点明細 + 趋势图（discipline）

> 来源真值：iOS `03_dev/student_ios/v1/TomoshibiApp/Features/MyPage/MyPageStubs.swift`（減点明細页 `MyPointsView` 行 1161–1345 / 趋势图页 `MyPointsChartView` 行 1347–1495 / 入口卡 `pointsStatusCard` 行 395–436）+ 种子数据 `Foundation/Seed/SEED.swift`（`SEED.points` 7 件，`SEED.user.points = 4.5`）+ 模型 `Foundation/Seed/SeedModels.swift`（`PointRecord`）。颜色取自 `Foundation/Theme/TTokens.swift`（下文统称「色板 T」，是 iOS 的全局配色常量集合，Android 要照抄同样的十六进制色值）。
>
> 「減点」= 扣分；这套界面是「学生看自己这个月被扣了多少纪律分、每一笔怎么来的、离两条处罚红线还有多远」。两条红线：累计 4 分 → 清掃罰則（罚扫除），累计 8 分 → 外出禁止（禁足）。

### 一、画面一覧（这块有几个屏）

| 序号 | iOS 屏名 / 路由 | 层级 | 中文说明 | 怎么进 |
|---|---|---|---|---|
| 入口卡 | `pointsStatusCard`（在 MyPage 着陆页里，不是独立屏） | — | 「減点明細」状态卡，显示当前合計分 + 等级徽章 | MyPage 着陆页常驻 |
| 05-A | `MyPointsView` / 路由 `.myPoints` | L2（带返回箭头） | 減点明細主页：大数字 + 进度条 + 明细列表 + 规则脚注 | 点入口卡 / 也可从 Home 的点数卡进 |
| 05-B | `MyPointsChartView` / 路由 `.myPointsChart` | L2 | 減点グラフ趋势图：过去 12 个月折线图 | 05-A 标题栏右上「グラフ →」按钮进 |

对应截图 **05**。没有弹窗 / 没有底部弹层（GlassSheet），全部是普通页面 + 返回箭头。

### 二、入口卡 `pointsStatusCard`（着陆页里的一张卡，行 395–436）

横向卡片，整张可点（点了进 05-A）。从左到右：

1. **左侧图标块**：48×48 圆角方块（圆角 12），底色按等级变（见下），中间放 emoji「📉」（下降折线图，22pt）。
2. **右侧文字区**（纵向，间距 4）：
   - 第一行小标题「減点明細」（12pt 半粗，色 `T.inkSub` 副标题灰）。
   - 第二行（基线对齐，间距 6）：大数字 = 当前分（22pt 超粗等宽字体，颜色按等级）+「点」字（12pt 灰）+ 一个 **Pill 徽章**（小圆角标签）。
   - 第三行「詳細を見る →」（11pt 半粗，主题色 `T.primary` 青）。

**等级判定逻辑**（按当前总分 `pts`，三档，行 399–403）：

| 条件 | 数字颜色 | 图标块底色 | 徽章文案 | 徽章色调 |
|---|---|---|---|---|
| `pts >= 8` | `T.danger` 红 | `T.dangerBg` 浅红 | 「禁足」 | danger |
| `4 <= pts < 8` | `T.warn` 橙 | `T.warnBg` 浅黄 | 「罰掃 注意」 | warn |
| `pts < 4` | `T.ok` 绿 | `T.okBg` 浅绿 | 「良好」 | ok |

demo 数据 4.5 分 → 落在中档，数字橙色、底色浅黄、徽章「罰掃 注意」。

### 三、05-A 減点明細主页 `MyPointsView`（行 1161–1345）

整页 = 顶部 PageHeader + 下面 ScrollView。从上到下：

**(1) PageHeader（页头，行 1173–1186）**
- 标题「減点明細」，level=2（带返回箭头，点了 `router.back()`）。
- 右上角放一个文字按钮「グラフ →」（12pt 粗，主题色青），点了 `router.go(.myPointsChart)` 进 05-B 趋势图。

**(2) 今月合計大数字卡（琥珀渐变，行 1190–1217）**
- 一张大圆角卡（圆角 20），背景是**线性渐变**：从左上 `#FFEFC2`（浅黄）到右下 `#F4C677`（金黄）。
- 内容纵向左对齐，间距 4：
  - 小标题「今月合計」（12pt 粗，字距 kerning 1.7，全大写化 textCase，颜色 `#5C3410`（深棕）透明度 0.8）。
  - 大数字行（底基线对齐，间距 6）：分数 = `String(format:"%.1f", SEED.user.points)`（**48pt 超粗等宽字体**，深棕 `#5C3410`）+「点」字（14pt，深棕透明度 0.7）。
- demo 显示「4.5 点」。
- 卡片内边距：水平 22 / 垂直 20；卡下方留白 16。

**(3) 进度条 `progressBar`（0 → 8，带 4/8 阈值刻度，行 1288–1338）**
- 逻辑：最大值 `maxVal = 8`，当前值 `v = min(points, 8)`，比例 `ratio = v / 8`。
- 结构（用 GeometryReader 拿到容器实际宽度 `W`）：
  - **底轨**：Capsule（胶囊圆角条），填 `T.hair`（极浅灰），高 8。
  - **进度填充**：Capsule，线性渐变从左 `#F4C677` 到右 `T.warn`(`#D1984A`)，宽 = `W × ratio`，高 8，左对齐。
  - **阈值刻度 4**：一根竖线 Rectangle（宽 2 高 14），填 `T.warn` 橙，横向偏移到 `W × (4/8) − 1`（即正中间）。
  - **阈值刻度 8**：一根竖线（宽 2 高 14），填 `T.danger` 红，贴最右（偏移 `W − 2`）。
- 进度条下方一行三段文字标签（左中右用 Spacer 撑开）：
  - 左「0」（10pt 等宽，`T.inkMute` 灰）
  - 中「4 清掃罰則」（10pt，`T.warnDeep`(`#7A4A0E`) 深棕）
  - 右「8 外出禁止」（10pt，`T.danger` 红）
- 进度条整体下方留白 16。

**(4) 扣分明细列表卡（行 1224–1234）**
- 一张 Card（padding=0，即卡内不留边，靠每行自己撑），纵向堆 `SEED.points` 每条记录，**条目之间夹一根 Divider 分隔线**（填 `T.hair`；第 0 条上方不画）。
- 每行 `pointRow`（行 1268–1286），横向，从左到右：
  - **日期**（`p.date`，12pt 等宽，`T.inkMute` 灰，固定宽 80 左对齐）。例「2026-04-05」。
  - **「场次 · 类型」**（`"\(p.session) · \(p.kind)"`，13pt，`T.ink` 主墨色）。例「朝点呼 · 遅刻」。
  - Spacer 撑开。
  - **加分值**（`String(format:"+%.1f", p.val)`，14pt 粗等宽）。颜色规则：**`val >= 1` 用 `T.danger` 红，否则用 `T.warnDeep` 深棕**（即欠席 +1.0 红、遅刻 +0.5 棕）。
  - 每行内边距：水平 16 / 垂直 14。
- 列表卡下方留白 14。

**SEED.points 7 条 demo 数据**（`SEED.swift` 行 34–42，Android 要原样照抄）：

| date | session | kind | val |
|---|---|---|---|
| 2026-04-05 | 朝点呼 | 遅刻 | 0.5 |
| 2026-04-07 | 朝点呼 | 遅刻 | 0.5 |
| 2026-04-12 | 朝点呼 | 遅刻 | 0.5 |
| 2026-04-15 | 晩点呼 | 欠席 | 1.0 |
| 2026-04-18 | 朝点呼 | 遅刻 | 0.5 |
| 2026-04-20 | 晩点呼 | 欠席 | 1.0 |
| 2026-04-21 | 朝点呼 | 遅刻 | 0.5 |

（合计 0.5×5 + 1.0×2 = 4.5，跟大数字 4.5 一致。注意列表里只有 4 月这几笔；大数字直接取 `SEED.user.points = 4.5`，不是从列表 sum 出来的——Android 也别去 sum，直接读用户字段，跟 iOS 一致。）

**(5) 规则脚注卡（行 1236–1258）**
- 一张浅色圆角卡（圆角 12，填 `T.pill`（主题青 8% 透明度的极浅底）），内边距水平 14 / 垂直 12，行间距 3，左对齐占满宽。
- 第一行（横向，间距 4）：「現在のルール:」（12pt 粗，`T.inkSub`）+「遅刻 0.5 点 / 欠席 1.0 点」（12pt 常规，`T.inkSub`）。
- 第二行：「月累計 4 点で清掃罰則 · 月累計 8 点で外出禁止」（12pt，`T.inkSub`，上方留 2）。

整页 ScrollView 内容内边距：水平 20 / 顶 4 / 底 24。页面背景 `T.pearl`（`#EFF2F3` 灰白）。

### 四、05-B 減点グラフ趋势图 `MyPointsChartView`（行 1347–1495）

**(1) PageHeader**：标题「減点グラフ」，level=2（带返回箭头，无右上按钮）。

**(2) 图表卡（Card，padding=20）**，纵向：
- 顶部小标题「過去 12 ヶ月」（12pt，`T.inkSub`，下方留白 14）。
- 中间 **Canvas 折线图**，固定高度 200。
- 底部图例行（横向，居中，两段，间距 16）：
  - 一段：14×2 的橙色小横条（`T.warn`）+「清掃罰則閾値」（11pt，`T.inkSub`）。
  - 一段：14×2 的红色小横条（`T.danger`）+「外出禁止閾値」（11pt，`T.inkSub`）。
  - 图例上方留白 14。

页面背景 `T.pearl`，ScrollView 内边距水平 20 / 顶 4 / 底 24。

**(3) 折线图数据（行 1350–1354，Android 照抄）**
- 12 个月数值 `data = [0, 0, 1, 0, 0.5, 1, 0, 2, 0, 1, 2, 4.5]`（最后一月对齐 `SEED.user.points` 4.5，保持全局一致）。
- 12 个月 X 轴标签 `months = ["5","6","7","8","9","10","11","12","1","2","3","4"]`（注意是从 5 月排到次年 4 月，跨年）。
- 纵轴最大值 `maxVal = 8`。

**(4) Canvas 画法逐笔拆解（行 1406–1494）** —— Android 要 1:1 还原：

坐标系（在 Canvas 实际尺寸 `size.width × size.height` 上算）：
```
left   = 30                       // 左边留 30 给 Y 轴标签
right  = size.width               // 右边到头
top    = 10
bottom = size.height - 20         // 底部留 20 给 X 轴标签
innerW = right - left
innerH = bottom - top
yFor(v) = bottom - innerH * (v / maxVal)          // 值越大 y 越靠上
xFor(i) = left + innerW * i / (data.count - 1)    // 12 个点均分横向
```

绘制顺序（先画的在底层）：
1. **网格线 0/2/4/6/8**：对每个 g∈[0,2,4,6,8]，从 (left, yFor(g)) 到 (right, yFor(g)) 画一条**虚线**（线宽 1，虚线样式 dash [2,3]），颜色 `T.hair`。每条线左侧画 Y 轴数字标签「0」「2」「4」「6」「8」（9pt 等宽，`T.inkMute`），位置 (10, yFor(g))，左对齐锚点。
2. **阈值线 4**（橙）：(left → right) 在 yFor(4) 画虚线，线宽 1，dash [3,2]，颜色 `T.warn`。
3. **阈值线 8**（红）：在 yFor(8) 画虚线，线宽 1，dash [3,2]，颜色 `T.danger`。
4. **数据折线**：把 12 个点 (xFor(i), yFor(v)) 连成一条 Path，线宽 2.5，圆头圆角连接（lineCap/lineJoin round），颜色 `T.primary` 青。
5. **数据点圆点**：每个点画实心圆。**最后一月高亮**（半径 5，颜色 `T.warn` 橙），其余点半径 3.5，颜色 `T.primary` 青。
6. **X 轴标签**：每个点正下方 (xFor(i), size.height - 8) 居中画月份字（9pt 等宽，`T.inkMute`）。

### 五、色板 T 十六进制清单（Android 照抄，行 TTokens.swift 10–44）

| token | hex | 用处 |
|---|---|---|
| `primary` | `#1F6B74` | 折线 / 主按钮 / 点数 |
| `pearl` | `#EFF2F3` | 页面背景 |
| `paper` | `#FFFFFF` | 卡片底 |
| `ink` | `#0F1E22` | 主墨色文字 |
| `inkSub` | `#56707A` | 副标题 |
| `inkMute` | `#93A4AC` | 轴标签 / 日期 |
| `hair` | `#0F1E22` @8% | 分隔线 / 网格线 / 进度底轨 |
| `pill` | `#1F6B74` @8% | 规则脚注卡底 |
| `warn` | `#D1984A` | 阈值 4 / 橙刻度 / 最后点高亮 |
| `warnBg` | `#FDF4E1` | 中档图标块底 |
| `warnDeep` | `#7A4A0E` | 遅刻 +0.5 数值 / 「4 清掃罰則」 |
| `danger` | `#C44848` | 阈值 8 / 欠席 +1.0 数值 / 「8 外出禁止」 |
| `dangerBg` | `#FDE8E8` | 高档图标块底 |
| `ok` | `#4A9478` | 「良好」绿 |
| `okBg` | `#E3F1EA` | 低档图标块底 |
| 琥珀卡渐变 | `#FFEFC2` → `#F4C677`，文字 `#5C3410` | 今月合計大数字卡（硬编码，不在 T 里） |

### 六、导航

- **进 05-A**：MyPage 着陆页点入口卡 / Home 点数卡 `router.go(.myPoints)`。
- **05-A → 05-B**：05-A 页头右上「グラフ →」`router.go(.myPointsChart)`。
- **返回**：两屏都 level=2，左上返回箭头 `router.back()`。
- 这块不在底部 tab（BottomNav）上，是 MyPage 下的深层页。

### 七、数据源

- **当前全是 mock 种子**：`SEED.user.points`（大数字 + 进度条 + 入口卡）、`SEED.points`（明细列表）、`MyPointsChartView` 里写死的 `data`/`months` 数组（趋势图）。
- iOS 本块也尚未接后端（没有对应 API 调用）；趋势图的 12 月数据是纯演示常量。Android 当前阶段**对齐到同样的本地假数据即可**，不需要造网络层（除非「对齐规格」总表另有指示统一接 `/me/points` 类端点；本块 iOS 未接，故 Android 也先不接）。

---

### Android 对齐要点

Android 现状 = 早期演示桩，`student_android/v1/` 里只有 Compose UI 桩 + `MockData.kt` 本地假数据，**没有減点明細页、没有趋势图、没有 Canvas 画图**。要从零补出跟 iOS 一模一样的两屏 + 一张入口卡。

**1. 数据模型 + 假数据（先建）**
```kotlin
data class PointRecord(
    val date: String,     // "2026-04-05"
    val session: String,  // "朝点呼" / "晩点呼"
    val kind: String,     // "遅刻" / "欠席"
    val `val`: Double     // 0.5 / 1.0（val 是 Kotlin 关键字，用反引号或改名 value）
)
```
在 `MockData.kt` 里照抄上面 7 条 `SEED.points` + 用户字段 `points = 4.5`。趋势图的 `data`/`months` 两个数组也照抄到屏内常量。

**2. 入口卡（放进 MyPage 着陆页对应位置）**
- 用 Compose `Card` 或 `Surface` + `Modifier.clickable { nav 到減点明細 }`。
- 左边 48×48 `Box`（`RoundedCornerShape(12.dp)` + 等级底色）放「📉」Text 22sp。
- 右边 `Column`：「減点明細」(12sp `inkSub`) / `Row` 里大数字(22sp `FontWeight.Black` + `FontFamily.Monospace`，等级色) +「点」+ 徽章 / 「詳細を見る →」(11sp `primary`)。
- 等级三档判定写成 `when { pts >= 8 -> …; pts >= 4 -> …; else -> … }`，返回（数字色, 底色, 徽章文案, 徽章色）四元组，照第二节表。徽章用一个小 `Surface(shape = RoundedCornerShape(50))` 或自定义 Pill Composable。

**3. 05-A 減点明細页**
- 顶部用项目已有的页头 Composable（对应 iOS PageHeader：左返回箭头 + 居中标题 + 右 slot）。右 slot 放「グラフ →」`TextButton` 跳 05-B。
- 用 `Column` + `verticalScroll`（对应 iOS ScrollView），水平 padding 20。
- 琥珀大数字卡：`Box`（`RoundedCornerShape(20.dp)` + `Brush.linearGradient(listOf(Color(0xFFFFEFC2), Color(0xFFF4C677)))`），里面「今月合計」(用 `letterSpacing = 1.7.sp` + `.uppercase()`) + 大数字 48sp Black Monospace 深棕。注意 iOS 用 `textCase(.uppercase)`，Compose 要自己 `text.uppercase()`（日文不受影响，但保持等价处理）。
- **进度条用 `Canvas` 画最省事**（也可用 `Box` 叠层）：
  ```kotlin
  Canvas(Modifier.fillMaxWidth().height(14.dp)) {
      val w = size.width
      val barTop = (size.height - 8.dp.toPx()) / 2
      // 底轨
      drawRoundRect(hair, topLeft = Offset(0f, barTop),
          size = Size(w, 8.dp.toPx()), cornerRadius = CornerRadius(4.dp.toPx()))
      // 填充（渐变）
      val ratio = (points.coerceAtMost(8.0) / 8.0).toFloat()
      drawRoundRect(Brush.horizontalGradient(listOf(Color(0xFFF4C677), warn)),
          topLeft = Offset(0f, barTop),
          size = Size(w * ratio, 8.dp.toPx()), cornerRadius = CornerRadius(4.dp.toPx()))
      // 刻度 4（正中）
      drawRect(warn, topLeft = Offset(w * 0.5f - 1, barTop - 3.dp.toPx()),
          size = Size(2f, 14.dp.toPx()))
      // 刻度 8（最右）
      drawRect(danger, topLeft = Offset(w - 2, barTop - 3.dp.toPx()),
          size = Size(2f, 14.dp.toPx()))
  }
  ```
  下方三段标签用 `Row { Text("0"); Spacer(Modifier.weight(1f)); Text("4 清掃罰則"); Spacer(Modifier.weight(1f)); Text("8 外出禁止") }`。
- 明细列表：`Card` 包一个 `Column`，`points.forEachIndexed { i, p -> if (i>0) Divider(color = hair); PointRow(p) }`。`PointRow` 是 `Row`：日期(`Modifier.width(80.dp)`, Monospace inkMute) + 「session · kind」(13sp ink) + `Spacer(Modifier.weight(1f))` + 「+%.1f」用 `String.format("+%.1f", p.value)`，颜色 `if (p.value >= 1) danger else warnDeep`。
- 规则脚注：`Box`（`RoundedCornerShape(12.dp)` + `pill` 底色）里两行 Text，照第三节(5)。

**4. 05-B 趋势图 — Compose Canvas 画法（重点）**

iOS 用 SwiftUI `Canvas`，Android 用 Compose `androidx.compose.foundation.Canvas`，API 形状几乎一一对应。固定高度 200.dp。注意单位：Compose Canvas 里所有坐标是**像素 px**，dp 要 `.dp.toPx()`；但 left/right/top/bottom 这些已经是按 px 算的几何量，直接用 `size.width`/`size.height`（px）就行。

```kotlin
@Composable
fun PointsChart(
    data: List<Double> = listOf(0.0,0.0,1.0,0.0,0.5,1.0,0.0,2.0,0.0,1.0,2.0,4.5),
    months: List<String> = listOf("5","6","7","8","9","10","11","12","1","2","3","4"),
    maxVal: Double = 8.0,
) {
    val textMeasurer = rememberTextMeasurer()  // 画轴标签文字要用
    Canvas(Modifier.fillMaxWidth().height(200.dp)) {
        val left = 30f
        val right = size.width
        val top = 10f
        val bottom = size.height - 20f      // 底部留 20 给 X 标签
        val innerW = right - left
        val innerH = bottom - top
        fun yFor(v: Double) = bottom - innerH * (v / maxVal).toFloat()
        fun xFor(i: Int) = left + innerW * i / (data.size - 1)

        // 1. 网格线 0/2/4/6/8（虚线 dash[2,3]）
        val dash = PathEffect.dashPathEffect(floatArrayOf(2f, 3f))
        listOf(0.0,2.0,4.0,6.0,8.0).forEach { g ->
            val y = yFor(g)
            drawLine(hair, Offset(left, y), Offset(right, y), 1f, pathEffect = dash)
            // Y 标签：drawText(textMeasurer, "${g.toInt()}", topLeft 约 (10, y - 半行高), 9sp Monospace inkMute)
        }
        // 2. 阈值线 4（warn，dash[3,2]）
        drawLine(warn, Offset(left, yFor(4.0)), Offset(right, yFor(4.0)), 1f,
                 pathEffect = PathEffect.dashPathEffect(floatArrayOf(3f, 2f)))
        // 3. 阈值线 8（danger，dash[3,2]）
        drawLine(danger, Offset(left, yFor(8.0)), Offset(right, yFor(8.0)), 1f,
                 pathEffect = PathEffect.dashPathEffect(floatArrayOf(3f, 2f)))
        // 4. 数据折线
        val path = Path()
        data.forEachIndexed { i, v ->
            val pt = Offset(xFor(i), yFor(v))
            if (i == 0) path.moveTo(pt.x, pt.y) else path.lineTo(pt.x, pt.y)
        }
        drawPath(path, primary, style = Stroke(width = 2.5f,
                 cap = StrokeCap.Round, join = StrokeJoin.Round))
        // 5. 圆点（最后一月高亮 r=5 warn，其余 r=3.5 primary）
        data.forEachIndexed { i, v ->
            val isLast = i == data.lastIndex
            drawCircle(if (isLast) warn else primary,
                       radius = if (isLast) 5f else 3.5f,
                       center = Offset(xFor(i), yFor(v)))
        }
        // 6. X 标签：months.forEachIndexed → drawText 居中 (xFor(i), size.height - 8) 9sp Monospace inkMute
    }
}
```

**Compose Canvas 画轴标签文字注意点**（iOS 用 `ctx.draw(Text(...))` 自带锚点对齐，Compose 没有现成锚点）：
- 用 `rememberTextMeasurer()` + `drawText(textMeasurer, str, topLeft, style)`。`drawText` 的 `topLeft` 是文字左上角，不像 iOS 能直接给 `.leading`/`.center` 锚点。要居中（X 轴标签）得先 `textMeasurer.measure(str, style)` 拿到宽度，再 `topLeft = Offset(x - measured.size.width/2, y - measured.size.height/2)` 自己减半。
- 字号 9sp、`FontFamily.Monospace`、颜色 `inkMute`，对齐 iOS 的 9pt monospaced inkMute。
- 也可以退一步：把折线 Canvas 单独画，轴标签用外层 `Box` + 绝对定位的 `Text` 叠上去，避免 `drawText` 的测量麻烦——但**折线 / 网格 / 阈值线 / 圆点必须在同一个 Canvas 里画**，保证坐标系一致。

**5. 颜色常量**：在 Android 主题里建 `object T`（或用项目已有的 `Color.kt`），把第五节那张 hex 表一一对应成 `val warn = Color(0xFFD1984A)` 等（Compose 颜色是 `0xAARRGGBB`，前两位是不透明度 `FF`；`hair`/`pill` 这种带透明度的写 `Color(0x140F1E22)`，`0x14` ≈ 8%）。务必跟 iOS 同值，否则两端配色会肉眼可见地偏。

**6. 易踩的坑**
- 大数字 4.5 直接读用户 `points` 字段，**别去 sum 明细列表**（iOS 就是分开的，列表只 7 条但大数字独立）。
- 进度条刻度 4 在「正中间」是因为 4/8=0.5，不是因为它对齐了第几个数据点——纯比例。
- 趋势图最后一个点 4.5 既是高亮点、又跟大数字 4.5 一致，这是 iOS 故意对齐的，别改成别的值。
- 文案全部保持日语原文，逐条照抄：「減点明細」「今月合計」「点」「現在のルール:」「遅刻 0.5 点 / 欠席 1.0 点」「月累計 4 点で清掃罰則 · 月累計 8 点で外出禁止」「グラフ →」「減点グラフ」「過去 12 ヶ月」「清掃罰則閾値」「外出禁止閾値」「4 清掃罰則」「8 外出禁止」「良好」「罰掃 注意」「禁足」「詳細を見る →」「朝点呼」「晩点呼」「遅刻」「欠席」。

---

I have all the data I need. Android currently has only a `notifications` screen folder + scattered MockData (notifications, events preview, single BusInfo) but no dedicated bus list / package / song / calendar / announcement screens. Now I'll write the alignment spec.

## misc-features（バス / 宅配 / リクエスト曲 / カレンダー / 通知）

> 真值来源：iOS Swift/SwiftUI。本块覆盖 5 组功能 14 个画面。文件位置：
> - 巴士：`Features/BusList/BusListStubs.swift`（`BusListView`，1 屏）+ `Features/Community/CommunityStubs.swift` 内 `BusView`（旧版「バス時刻表」1 屏）
> - 宅配：`Features/Community/CommunityStubs.swift` 内 `PackagesView` / `PackageDetailView`（2 屏）
> - リクエスト曲（点歌）：`Features/Community/CommunityStubs.swift` 内 `MusicView` / `MusicNewView` / `MusicDetailView` / `SongReportSheet`（3 屏 + 1 弹窗）
> - カレンダー / 行事予定：`Features/Schedule/ScheduleStubs.swift`（`ScheduleView`，真后端版日历）+ `Features/Community/CommunityStubs.swift` 内 `EventsView` / `EventDetailView`（演示版日历 + 活动详情）
> - 通知：`Features/Community/CommunityStubs.swift` 内 `NotificationsView`（通知中心）+ `Features/Home/HomeStubs.swift` 内 `AnnouncementListView` / `AnnouncementDetailView`（老师公告一覧 + 详情/回复）
> - LifeTab 入口卡（`HomeStubs.swift` 内 `LifeTab`）也归本块，因为 5 个功能的入口都在那
>
> 共享组件清单（iOS `Foundation/Components`）：`PageHeader`（页头，带返回箭头 + 标题 + 可选右侧按钮）/ `Card`（白底圆角卡，传 padding）/ `Pill`（小圆角标签，tone = neutral/accent/ok/warn）/ `PrimaryButton`（主按钮，可 enabled 控制可点）/ `TField`（单行输入框）/ `TArea`（多行输入框）/ `Field`（带 label + 必填红星 + hint 的表单字段包裹）/ `GlassSheet`（毛玻璃底部弹窗，带 onClose）/ `EmptyState`（空状态：icon + title + message）/ `Ic`（SF Symbol 包装：`Ic.bus` / `Ic.music` / `Ic.calendar` / `Ic.chevR` 右箭头 / `Ic.plus` / `Ic.search` / `Ic.camera` / `Ic.package`）。颜色全走 `T` token（`T.primary` 主色青蓝 / `T.pearl` 页背景浅灰 / `T.paper` 卡白 / `T.pill` 浅灰药丸底 / `T.ink` 主文字 / `T.inkSub` 次文字 / `T.inkMute` 弱文字 / `T.hair` 0.5px 分隔线 / `T.accent` 强调 / `T.warn`/`T.warnBg`/`T.warnDeep` 警告 / `T.danger`/`T.dangerBg` 危险）。
>
> Android 现状（`03_dev/student_android/v1`）：只有 `ui/screens/notifications/` 一个相关目录；`MockData.kt` 里有 `DEFAULT_NOTIFICATIONS`（5 条假通知）、`EVENTS_PREVIEW`（2 条活动预览）+ `EVENTS_THIS_WEEK = 14`、`DEFAULT_BUS`（单条 `BusInfo`，不是完整时刻表）。**没有巴士一覧屏 / 宅配屏 / 点歌屏 / 日历屏 / 公告屏，也没有网络层**。下面每节末尾给「Android 对齐要点」。

---

### 一、バス（巴士）

#### 1.1 画面一覧
- `BusListView` —「特別運航便」一覧（主力，从 Home 巴士卡进）
- `BusView` —「バス時刻表」旧演示版（纯 SEED，无筛选；当前 Home 已不再指向它，但路由 `.homeBus` 仍在；Android 可只做 `BusListView`，旧版略过）

#### 1.2 `BusListView` 布局结构（从上到下）
1. `PageHeader(title: "特別運航便", level: 2)`
2. ScrollView 内容（横边距 16）：
   - **空港送迎案内 banner**：浅色药丸底（`T.pill`）圆角卡，左侧「✈」字符 + 右侧两行文字（标题「空港送迎便について」加粗 + 说明文）
   - **筛选区 filters**：
     - 第一行：横向滚动的 3 颗胶囊 tab —「すべて」/「特別便」/「通学便」。选中 = `T.primary` 填充 + 白字；未选 = `T.pill` 底 + 主色字
     - 第二行：一个 `Toggle` 开关（缩放 0.85）+ 文字「空港送迎便のみ」。开时文字变主色
   - **加载/空/错误三态**：加载中 = 转圈；已登录拉取失败 = `EmptyState(icon:"bus", title:"読み込みに失敗しました", message:错误文)`；筛选后无结果 = `EmptyState(icon:"bus", title:"該当する便はありません", message:"条件を変えてお試しください。")`
   - **日别分组列表**（`grouped`，按日期升序，每组一张圆角卡）：
     - 组头：`月/日`（大号等宽字）+「(曜日)」+ 右侧灰色 purpose 文字。底色 `T.primary.opacity(0.05)`
     - 组内每行（`busRow`）：左侧 36×36 圆角图标块（下一班 = 主色填充白图标，否则浅主色底）；图标空港便用 `airplane` 否则 `bus`；中间 = 大号等宽出发时刻 + `Pill(kind.label)`（"通学便"=neutral / "特別便"=accent）+ 空港便追加 `Pill("空港", accent)`，下一行灰色 direction；右侧 = 若是下一班显示 `Pill("次便", accent)`，下方 seatsLabel 弱字。行间 0.5px 分隔线（左缩进 58）
   - **底部备注**：「※ 通常日のスクールバスは別途ご確認ください。特別便は乗車名簿への事前チェックが必要です。」11px 弱字

#### 1.3 「下一班」判定逻辑（必须照搬）
按日本时区（Asia/Tokyo）取「现在」，格式成 `yyyy-MM-dd HH:mm` 字符串。在**当前筛选后的可见列表**里，第一个满足 `现在 <= "日期 时刻"` 的便高亮为「次便」。不要在数据映射阶段写死 isNext —— 否则切筛选后高亮错位。

#### 1.4 关键文案（日语原文）
页头「特別運航便」；tab「すべて」「特別便」「通学便」；开关「空港送迎便のみ」；banner「空港送迎便について」「帰国届を出す場合は、空港便にチェックを入れて選択してください。」；空态「該当する便はありません」「条件を変えてお試しください。」「読み込みに失敗しました」；行内 Pill「通学便」「特別便」「空港」「次便」；底部「※ 通常日のスクールバスは別途ご確認ください。特別便は乗車名簿への事前チェックが必要です。」；401 报错「セッションの有効期限が切れました。再度ログインしてください。」；通用报错兜底「時刻表の取得に失敗しました」

#### 1.5 导航
进入：Home 的 LifeTab 巴士卡点击 → 路由 `.busList`。返回：`PageHeader` 返回箭头回上一页。无 tab。

#### 1.6 数据源
- 端点：`GET /api/v1/bus/routes`（可加 `?kind=daily_commute|dorm_special` 过滤；iOS `BusAPI.listRoutes`）。响应体 `{ "items": [...] }`，解包成数组。
- 单条 `BusRouteOut` 字段：`id`(UUID) / `kind`(String) / `name` / `direction` / `schedule_at`(完整日期时间) / `arrival_at`(可空) / `visible_to`("all"|"dorm_only"|"men"|"women") / `note`(可空) / `deprecated` / `created_by_teacher_id` / `created_at` / `updated_at`(可空)
- 映射到 UI 模型 `SpecialBusRoute`（拆 `schedule_at` 成日期字符串 `yyyy-MM-dd` + 时分 `HH:mm` + 日语单字曜日；空港便判定 = `direction` 或 `name` 含「空港」二字）。
- **三态加载**：未登录 → 回退本地假数据 `BusListMock.all`（基于 `SEED.busSchedule` 生成）；已登录 → 拉真后端；已登录但失败 → **不喂假时刻表**（学生靠这个赶车，假时间会害人误车），401 清登录态 + 提示重登，其它错误显示报错 + 空列表。
- 假数据 `SEED.busSchedule`（5 个日别组：2026-04-29 / 05-06 / 05-16 / 05-23 / 05-31，每组含 label / notice / 多条 lines，line 字段 = time / route / seats / next）。

#### 1.7 Android 对齐要点
Android 现在只有一个单条 `DEFAULT_BUS = BusInfo("09:20","05/06(水)","高校棟 → 金川駅")`，**完全不够**。要新建：
- `data/model/` 里加 `BusRouteOut`（对齐后端字段，`scheduleAt`/`arrivalAt` 用 `kotlinx.datetime.Instant` 或 `OffsetDateTime`）+ UI 模型 `SpecialBusRoute`（含 `date`/`weekday`/`scheduleAt` 字符串、`isAirport`、`kind` 枚举）。
- `BusKind` 枚举（`DAILY_COMMUTE="daily_commute"` / `DORM_SPECIAL="dorm_special"`，各带 label「通学便」/「特別便」+ Pill tone）。
- 新建 `ui/screens/bus/BusListScreen.kt`（Compose），结构：`Column { PageHeader → 横向 `LazyRow` tab → `Switch` + Text → `LazyColumn` 日别分组 }`。分组用 `groupBy { it.date }` 后按 key 排序，每组用一个圆角 `Card` 包组头 + 多行。
- 「次便」高亮：用 `kotlinx.datetime` 取 Asia/Tokyo 当前，格式同 iOS 拼成可比字符串，`firstOrNull { now <= "${it.date} ${it.scheduleAt}" }?.id` 算出 nextId，行渲染时 `route.id == nextId`。
- 三态：用 `ViewModel` 持 `uiState`（Loading/Error/Content）+ `routes`，`isAuthenticated` 决定走 mock 还是真后端，失败按 iOS 规则不喂假数据。
- 网络层从零搭（Retrofit + Moshi/kotlinx.serialization），端点 `GET bus/routes`，认证 token 放 header。

---

### 二、宅配（包裹）

#### 2.1 画面一覧
- `PackagesView` —「宅配」一覧（待領 / 領済 两 tab）
- `PackageDetailView` —「宅配詳細」

#### 2.2 `PackagesView` 布局
1. `PageHeader(title: "宅配", level: 2)`
2. **2-tab segmented**（`SegTabs`，浅灰底圆角，两格平分；选中格 = 白底加粗）：「待領 · {N}」/「領済 · {N}」（N = 各状态件数）
3. **卡列表**（横边距 16，卡间距 10）：每张 `Card(padding:14)`，横排：左侧 📦 emoji（28px，不换 SF Symbol）+ 中间两行（发货方加粗 + 「日期 · 追跡番号」等宽弱字）+ 右侧仅「待領」状态显示「受取」实心按钮（渐变底 `T.btnGrad`，高 36）
4. 空态：`EmptyState(icon:"shippingbox", title:"なし")`

#### 2.3 `PackageDetailView` 布局
1. `PageHeader(title: "宅配詳細", level: 2)`
2. `Card(padding:20)`：顶部 📦 emoji（56px 居中）+ 下方 4 行 meta 表（每行上边 0.5px 分隔线，左 label 灰 + 右 value 加粗）：
   - 「配送業者」= 发货方 / 「到着時刻」= "日期 14:22" / 「追跡番号」= tracking 或 "―" / 「保管場所」= 写死「寮務室前棚 A-3」
3. `PrimaryButton(title: "受取確認")` → 点了弹 toast「受取完了しました」+ 返回
4. 找不到时：`EmptyState(icon:"shippingbox", title:"宅配が見つかりません")`

#### 2.4 关键文案
「宅配」「宅配詳細」；tab「待領 · N」「領済 · N」；行内按钮「受取」；详情 meta「配送業者」「到着時刻」「追跡番号」「保管場所」「寮務室前棚 A-3」；按钮「受取確認」；toast「受取完了しました」；空态「なし」「宅配が見つかりません」

#### 2.5 导航
进入：LifeTab 宅配卡 → `.homePackages`。一覧每张卡点击 → `.homePackageDetail(id:)`。返回箭头回上层。

#### 2.6 数据源
**目前纯本地假数据 `SEED.packages`**（无真后端端点）。`PackageItem` 字段：`id`(Int) / `date` / `from`(发货方) / `status`("待領"|"領済") / `tracking`(可空)。4 条假数据（JP12345 待領 + 佐川/ヤマト/郵便局 領済）。详情页的「到着時刻 14:22」「保管場所」是写死的演示文字，没在模型里。

#### 2.7 Android 对齐要点
- 模型 `PackageItem(id, date, from, status, tracking)`，`status` 用 enum 或保留字符串「待領」/「領済」（与 iOS 一致，便于过滤）。
- 假数据 `MockData.DEFAULT_PACKAGES`（4 条同 iOS）。
- 新建 `ui/screens/packages/PackagesScreen.kt` + `PackageDetailScreen.kt`。`SegTabs` 用 Compose 自绘（两个等宽 `Box` + `Surface` 选中态），不要用 Material `TabRow`（视觉对不上）。
- 📦 emoji 直接 `Text("📦", fontSize = 28.sp)`，**不要换成 Material Icons**（iOS 注释明确「不自作主张换 SF Symbol」）。
- 详情 meta 4 行的「14:22」「寮務室前棚 A-3」照 iOS 写死。「受取確認」按钮点击弹 Snackbar/Toast 后 `navController.popBackStack()`。

---

### 三、リクエスト曲（点歌）

#### 3.1 画面一覧
- `MusicView` —「リクエスト曲」一覧
- `MusicNewView` —「曲を投稿」表单
- `MusicDetailView` —「曲詳細」
- `SongReportSheet` —「曲を通報する」底部弹窗（毛玻璃）

> 注意：賛成/反対投票 2026-05-01 已废止，现在只有「通報」（举报）动线。

#### 3.2 `MusicView` 布局
1. `PageHeader(title:"リクエスト曲", level:2, right: 右上「+」按钮 HeaderPlusButton)` → 点 + 去投稿
2. **hint banner**（浅主色底 + 主色描边圆角卡）：info 图标 + 「気になる曲があれば、各曲の「⚠ 通報」ボタンから先生にお伝えできます。」
3. **曲卡列表**（按 id 降序 = 新→旧，卡间距 8）：每张 `Card(padding:14)` 横排：
   - 左：44×44 紫渐变方块（`T.accentSoft`→`T.accent`）+ 白色 `Ic.music` 图标（点 → 详情）
   - 中：曲名加粗（1 行省略）+「アーティスト · by号」灰字（点 → 详情）
   - 右：「⚠ 通報」胶囊按钮（`T.warnBg` 底 + `T.warnDeep` 字 + 三角警告图标）→ 点开 `SongReportSheet`

#### 3.3 `MusicNewView` 布局
1. `PageHeader(title:"曲を投稿", level:2)`
2. 若被封禁（`!canPostSong`）顶部显示红色 `banBanner`（octagon 图标 + 封禁说明 + 「通報多数のため、現在リクエスト曲の投稿はできません。詳細は寮監にご相談ください。」）
3. 表单字段（每个用 `Field` 包裹，间距 18）：
   - `Field("Apple Music URL", hint:"曲情報を自動取得します")` + `TField`（placeholder `https://music.apple.com/...`）
   - `Field("曲名", required:true)` + `TField`
   - `Field("アーティスト", required:true)` + `TField`
   - `Field("投稿理由")` + `TArea`（placeholder「この曲を寮で流したい理由」3 行）
4. `PrimaryButton("投稿する")` —— **可点条件 = 未封禁 且 曲名非空 且 艺术家非空**（trim 后判断，只输空格不算）。点了弹 toast「投稿しました」延迟 0.5s 返回一覧

#### 3.4 `MusicDetailView` 布局
1. `PageHeader(title:"曲詳細", level:2)`
2. 160×160 紫渐变大圆角方块 + 白 `Ic.music`（带阴影），居中
3. 曲名（22 heavy）+「アーティスト · 投稿 by号」
4. `Card`「投稿理由」+ 写死文「朝の支度時間に聴きたい、明るい気持ちになれる曲です。」
5. 大「この曲を通報する」按钮（警告色块，高 52）→ 开 `SongReportSheet`
6. 底部「通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。」

#### 3.5 `SongReportSheet`（毛玻璃弹窗）布局
1. `GlassSheet(onClose:)` 包裹，ScrollView，maxHeight 600
2. 标题「曲を通報する」
3. 曲信息小卡（38×38 紫渐变 + 曲名/艺术家）
4. 「通報の理由 *」+ 4 个单选行（radio 自绘圆圈，选中主色）：「うるさい」/「曲調が好みでない / 不快」/「歌詞が不適切」/「その他」
5. 选「その他」时展开「詳細 *」`TArea`（placeholder「通報の理由を具体的にお書きください」）
6. 注意文「※ 通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。\n※ 多数の通報を受けた場合、投稿者の投稿が一定期間制限される場合があります。」
7. `PrimaryButton("通報を送る")` —— 可点条件 = 选了理由 且（若选「その他」则详情非空）。提交调 `reportSong(...)` 后关弹窗

#### 3.6 通报自动封禁逻辑（演示版，照搬）
`reportSong` 累计举报数 `myReportTotal`，阈值升级封禁等级：≥5 → level 1（停 1 个月）/ ≥10 → level 2（停 3 个月）/ ≥15 → level 3（永久）。升级时弹对应 toast：「通報多数のため、1 ヶ月間投稿停止になりました。」/「…3 ヶ月間…」/「…永久に…」；没升级时弹「通報を送信しました。」。`canPostSong` 据等级 + 解封时刻判断；`songBanDescription` 给封禁文案。

#### 3.7 关键文案
页头「リクエスト曲」「曲を投稿」「曲詳細」；hint「気になる曲があれば、各曲の「⚠ 通報」ボタンから先生にお伝えできます。」；行内按钮「通報」；表单 label「Apple Music URL」「曲情報を自動取得します」「曲名」「アーティスト」「投稿理由」「この曲を寮で流したい理由」「投稿する」；封禁 banner「通報多数のため、現在リクエスト曲の投稿はできません。詳細は寮監にご相談ください。」；详情「投稿理由」「朝の支度時間に聴きたい、明るい気持ちになれる曲です。」「この曲を通報する」「通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。」；弹窗「曲を通報する」「通報の理由」「うるさい」「曲調が好みでない / 不快」「歌詞が不適切」「その他」「詳細」「通報の理由を具体的にお書きください」「通報を送る」「※ 通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。」「※ 多数の通報を受けた場合、投稿者の投稿が一定期間制限される場合があります。」；空态「まだ投稿がありません」（Home 卡上）

#### 3.8 导航
进入：LifeTab 点歌卡 → `.homeMusic`。右上 + → `.homeMusicNew`。曲卡左/中 → `.homeMusicDetail(id:)`。通报按钮 → 打开 sheet（`openSheet(.songReport(songId:))`，全局 overlay，不是新页）。返回箭头回上层。

#### 3.9 数据源
**纯本地假数据 `SEED.songs`**（8 条：Lemon/夜に駆ける/Pretender/炎/紅蓮華/マリーゴールド/群青/ミックスナッツ）。`SongItem` 字段：`id`(Int) / `title` / `artist` / `by`(投稿者号，如"00号") / `up` / `down`（up/down 已不显示，废票后保留字段）。封禁状态全在 `AppStore` 内存里（`songBanLevel` / `songBanUntil` / `myReportTotal` / `songReportCounts`），**无真后端**。

#### 3.10 Android 对齐要点
- 模型 `SongItem(id, title, artist, by, up, down)` + `MockData.DEFAULT_SONGS`（8 条同 iOS）。
- `SongReportReason` 枚举（NOISY/TASTE/LYRICS/OTHER，各带日语 label）。
- 封禁状态进 `AppStore`（Android 已有 `data/store/AppStore.kt`）：加 `songBanLevel`/`songBanUntil`/`myReportTotal`/`canPostSong`/`songBanDescription`/`reportSong()`，逻辑照搬阈值 5/10/15。
- 新建 `ui/screens/community/`（或 `music/`）下 `MusicScreen.kt` / `MusicNewScreen.kt` / `MusicDetailScreen.kt`。通报弹窗用 `ModalBottomSheet`（Material3）配毛玻璃背景近似 `GlassSheet`。
- 一覧排序 `sortedByDescending { it.id }`。投稿按钮 `enabled` 三条件照搬（trim 非空）。radio 自绘（`Box` + `Canvas`/`drawCircle`），别用 `RadioButton`（视觉对不上 iOS 的粗描边设计）。

---

### 四、カレンダー / 行事予定

#### 4.1 画面一覧
- `ScheduleView` —「行事予定」月历（**接真后端**，主力，从专用入口进）
- `EventsView` —「カレンダー」月历（演示版，硬编码 4/5 月，从 LifeTab 活动卡进）
- `EventDetailView` —「活動詳細」

> 两个日历视觉几乎一样。差别：`ScheduleView` 数据来自后端、可滚任意月、一天最多画 3 个圆点；`EventsView` 只有 4/5 月切换、一天 1 个圆点。Android 建议**只做 `ScheduleView` 这套**（真后端 + 可滚任意月），`EventsView` 演示版可省。

#### 4.2 `ScheduleView` 布局
1. `PageHeader(title:"行事予定", level:2)`
2. 三态：加载中转圈 / 失败 `EmptyState(icon:"calendar", title:"読み込みに失敗しました", message:错误文)` / 正常显示日历卡 + 选中日详情
3. **日历卡 `calendarCard`**（`Card(padding:16)`）：
   - 月切换头：左箭头（到最早月禁用）+「YYYY 年 M 月」+ 右箭头（到最晚月禁用）。**「2026」必须原样显示，不能被本地化加千位逗号变「2,026」**（iOS 用 `Text(verbatim:)`）
   - 7 列网格：曜日表头「日 月 火 水 木 金 土」（日=红 `T.danger`、土=主色、其余弱字）→ 月初前留空白格 → 当月各天 `dayCell`
   - 当月有行事时底部「{M} 月：{N} 件の予定」弱字
4. **`dayCell`**：正方形格子。选中 = 主色实心 + 白字；今天（非选中）= 浅主色底 + 主色描边；数字等宽，选中/今天加粗。有行事且非选中时，格子底部画 1~3 个 `T.accent` 小圆点（按当天事件数，最多 3）
5. **选中日详情 `selectedDaySection`**：标题「{M} 月 {D} 日（曜日）」+ 右侧「{N} 件」胶囊。无事件 = `Card` 内 `Ic.calendar` + 「予定なし」+「この日の活動はありません」；有事件 = 每条一张 `eventRow`
6. **`eventRow`**：`Card(padding:14)`，左 56pt 宽显示时刻（主色等宽）+ 1px 竖分隔 + 标题加粗 + 「📍 场所」（场所非空才画）+ 右 `Ic.chevR`。点击 → 详情（仅 SEED 兜底态可跳，见下）

#### 4.3 「今天」/ 月份范围逻辑
- 今天基准：演示构建（`#if DEMO`）固定 2026-04-23；生产取 Asia/Tokyo 实际今日。
- 月份范围 = 所有行事的最早月 ~ 最晚月，且强制包含「今天所在月」（即使该月无行事也能停在今天那页）。切月按钮在范围边界禁用。切月时把选中日 clamp 到新月天数（防 5 月 31 日切 4 月显示不存在的 4/31）。

#### 4.4 `EventDetailView` 布局
1. `PageHeader(title:"活動詳細", level:2)`
2. **hero 日期卡**：浅青渐变（`#E8F4F6`→`#A8DCE2`）圆角大卡，居中「2026 · {月}」+ 超大日数（54px heavy 等宽）+「{曜日} · {时刻}」
3. 标题（22 heavy）+「📍 场所」
4. `Card` 描述 = `event.desc` + 写死后缀「。新入生の自己紹介、在学生との交流タイム、軽食とドリンクをご用意します。」
5. `PrimaryButton("iPhone カレンダーに追加")` → toast「カレンダーに追加しました」（**Android 改文案，见对齐要点**）

#### 4.5 关键文案
「行事予定」「カレンダー」「活動詳細」；曜日「日 月 火 水 木 金 土」；「{M} 年 {M} 月」「{M} 月：{N} 件の予定」「{M} 月 {D} 日」「{N} 件」；空态「予定なし」「この日の活動はありません」「読み込みに失敗しました」；详情按钮「iPhone カレンダーに追加」+ toast「カレンダーに追加しました」；描述后缀「新入生の自己紹介、在学生との交流タイム、軽食とドリンクをご用意します。」；401「セッションの有効期限が切れました。再度ログインしてください。」；兜底「行事予定の取得に失敗しました」

#### 4.6 数据源
- 端点：`GET /api/v1/events?from_date=&to_date=`（iOS `EventsAPI.listEvents`）。一次取够范围 = 去年 1/1 ~ 明年 12/31，切月不再二次请求。
- `EventOut` 字段：`id`(UUID) / `title` / `category`(后端枚举「学校行事」「寮行事」「外部」「その他」) / `event_date`(纯日期字符串 "2026-04-23"，**注意不是 Date**，否则 ISO8601 解码失败) / `start_at`(可空，带时分时区) / `end_at`(可空) / `description`(可空) / 创建者等。
- 映射到 UI 模型 `EventItem`：`date`=event_date / `time`=start_at 格式成 "HH:mm"（无则空）/ `title` / `place`=空（后端无场所字段）/ `desc`=description。
- 三态：未登录 → `SEED.events`（14 条假行事，4-05 ~ 5-31，含 time/title/place/desc）；已登录 → 真后端；失败 → 不喂假行事 + 报错，401 清登录态。
- **详情跳转限制**：`EventDetailView` 按 `SEED.events` 下标取数，所以只有「用 SEED 兜底（未登录）」时才允许点击跳详情；拉了真后端时下标对不上，不跳（行内已显示完整信息）。

#### 4.7 Android 对齐要点
- Android 现有 `EVENTS_PREVIEW`（仅 2 条）+ `EVENTS_THIS_WEEK=14` 太薄。要补 `MockData.DEFAULT_EVENTS`（14 条同 iOS `SEED.events`）。
- 模型 `EventOut`（`eventDate` 用 String 别用日期类型，对齐后端纯日期）+ UI 模型 `EventItem(date, time, title, place, desc)`。
- 自写月历 Compose 组件：`LazyVerticalGrid(columns = GridCells.Fixed(7))`，曜日表头 + 空白格（`firstWeekdayIndex` 个）+ 当月天。`firstWeekdayIndex` 和 `daysInMonth` 用 `kotlinx.datetime.LocalDate` 算（注意周日=0 的索引约定，与 iOS Calendar.weekday-1 对齐）。
- 年份显示用纯字符串拼接 `"$year 年 $month 月"`，**绝不能过 `NumberFormat`**（会变「2,026」）。
- 月份范围 + 切月 clamp + 今天基准（DEMO 固定 2026-04-23 / 生产 Asia/Tokyo）逻辑照搬。
- 「iPhone カレンダーに追加」按钮在 Android 上文案改成「カレンダーに追加」或「端末のカレンダーに追加」（不能说 iPhone），实装可接 Android 日历 Intent，最小版先弹 toast「カレンダーに追加しました」。
- 网络层 `GET events?from_date=&to_date=`。

---

### 五、通知（通知中心 + 老师公告）

#### 5.1 画面一覧
- `NotificationsView` —「通知」中心（带 7 种类型筛选）
- `AnnouncementListView` —「お知らせ」老师公告一覧
- `AnnouncementDetailView` —「お知らせ詳細」公告详情 + 回复

> 通知中心（`NotificationsView`）= 聚合视图（push 模拟 + SEED 假通知 / 生产是真公告映射）。公告（`Announcement*`）= 接真后端的老师公告，可回复。两者数据生产环境联动（公告映射成通知卡）。

#### 5.2 `NotificationsView` 布局
1. `PageHeader(title:"通知", level:2)`
2. **筛选 pill 行**（横向滚动）：「すべて」「申請」「減点」「学習」「宅配」「活動」「リクエスト曲」。选中 = 主色填充白字
3. **通知卡列表**（卡间距 8）：每张 `Card(padding:14)` 横排：左侧未读时画 8px 主色实心圆点（已读留空占位）+ 右侧内容（顶行 `Pill(type)` + 右侧时刻弱字；中加粗标题；下正文灰字 1.5 行高）
4. 空态：`EmptyState(icon:"bell", title:"通知はありません")`
5. Pill tone：「減点」=warn /「申請」=ok / 其余=accent

#### 5.3 `AnnouncementListView` 布局
1. 自绘 header（返回箭头 + 「お知らせ」标题）—— 注意这里不是 `PageHeader`
2. 三态：加载转圈 / 错误红字「通信エラーが発生しました」/ 空 `bell.slash` 图标 + 「お知らせはありません」
3. `LazyVStack` 列表，每行 `AnnouncementListCard`：左未读圆点 + 标题（未读加粗）+ 摘要（2 行）+ 底行「老师名 · 相对时间」+ 有回复时右侧气泡图标 + 回复数

#### 5.4 `AnnouncementDetailView` 布局
1. 自绘 header（返回箭头 + 「お知らせ詳細」）
2. 正文区：标题（20 bold）+「老师名 · yyyy/MM/dd HH:mm」+ 正文（行高 4）+ 分隔线 + 「返信 ({N})」+ 回复列表（旧→新，Slack 风 `AnnouncementReplyRow`：作者名 + 教员时加「教員」蓝胶囊徽章 + 时刻 + 回复正文）或「まだ返信はありません」
3. 底部固定**回复输入栏**：圆角多行 `TextField`（placeholder「返信を入力...」，1~4 行）+ 圆形发送按钮（有内容时主色 paperplane 图标，发送中变 ellipsis）
4. 发送失败弹 toast「送信に失敗しました。もう一度お試しください」，**保留输入内容可重试**（不静默吞）

#### 5.5 相对时间格式
< 60 秒「たった今」/ < 1 小时「{N} 分前」/ < 1 天「{N} 時間前」/ 否则「MM/dd」。详情页用完整「yyyy/MM/dd HH:mm」。

#### 5.6 关键文案
「通知」「お知らせ」「お知らせ詳細」；筛选「すべて」「申請」「減点」「学習」「宅配」「活動」「リクエスト曲」；空态「通知はありません」「お知らせはありません」；错误「通信エラーが発生しました」；回复区「返信 (N)」「まだ返信はありません」「返信を入力...」；回复发送失败「送信に失敗しました。もう一度お試しください」；徽章「教員」；相对时间「たった今」「{N} 分前」「{N} 時間前」；通知卡 Pill 类型同筛选标签 + 生产新增「お知らせ」类型

#### 5.7 数据源
- **通知中心 `NotificationsView`**：数据 = `app.allNotifications`。演示构建 = `pushNotifications`（push 接通前为空）+ `SEED.notifications`（5 条假通知，圈在 `#if DEMO` 里，生产物理上没有）；生产构建 = `pushNotifications` + `announcementNotifications`（真公告映射成通知卡，type「お知らせ」，id 用负数避免和 push 正数撞）。`NotificationItem` 字段：`id`(Int) / `type` / `title` / `time` / `body` / `unread`。进页 `.task` 调 `refreshNotificationSources()`（生产拉公告列表 + 未读数）。
- **未读数** `unreadNotificationCount`（驱动 Home 右上角铃铛 badge）：演示 = 所有通知里 unread 计数；生产 = push 未读 + 后端真实公告未读数 `announcementUnreadCount`（登录/启动即拉，不依赖列表是否加载）。
- **公告**：端点 `GET /announcements`（列表）/ `GET /announcements/:id`（详情）/ `POST /announcements/:id/replies`（发回复）。`AnnouncementBrief`（列表项：title/bodySummary/authorTeacherName/createdAt/isRead/replyCount）+ `AnnouncementDetail`（详情：title/body/authorTeacherName/createdAt + `replies: [AnnouncementReplyOut]`）+ `AnnouncementReplyOut`（authorName/authorKind "teacher"|"student"/createdAt/body）。缓存在 `AppStore.announcements` / `announcementDetails[id]`，方法 `loadAnnouncementList()` / `loadAnnouncementDetail(id:)` / `postAnnouncementReply(announcementId:body:)`。

#### 5.8 Android 对齐要点
- Android 已有 `ui/screens/notifications/` + `DEFAULT_NOTIFICATIONS`（5 条，但第 5 条 type 写的是「リクエスト」，iOS 是「リクエスト曲」—— **对齐成「リクエスト曲」**）。补齐筛选标签 7 项 + Pill tone 映射。
- 通知卡未读圆点 / Pill / 时刻 / 标题 / 正文 布局照搬。空态「通知はありません」。
- **公告功能 Android 完全没有，要新建**：`ui/screens/announcements/AnnouncementListScreen.kt` + `AnnouncementDetailScreen.kt`。模型 `AnnouncementBrief` / `AnnouncementDetail` / `AnnouncementReplyOut`（字段对齐后端）。
- `AppStore.kt` 加 `announcements` / `announcementDetails` / `announcementUnreadCount` 状态 + `loadAnnouncementList/Detail/postReply` 方法。通知中心生产态聚合公告（演示态走 mock）。
- 详情页底部回复栏用 `OutlinedTextField` + 圆形 `IconButton`（`Icons.Default.Send`），发送中禁用 + 改图标，失败弹 Snackbar 且保留输入。
- 相对时间 helper 照搬阈值（60 秒 / 1 小时 / 1 天 / MM/dd）。`authorKind == "teacher"` 显示「教員」徽章。
- DEMO vs 生产分支：Kotlin 无 `#if DEMO`，用 `BuildConfig.DEBUG` 或自定义 `BuildConfig` flag 区分「喂 mock 假通知」vs「拉真公告」。
- 网络层补 `GET announcements` / `GET announcements/{id}` / `POST announcements/{id}/replies`。

---

### 六、LifeTab 入口卡（5 个功能的入口聚合）

iOS `LifeTab`（`HomeStubs.swift`）是 Home 里直显的内容区，从上到下 5 张 `HomeCard`：
1. **busCard**：44×44 浅主色底 `Ic.bus` + 「次のバス便 / 次回運行」标签 + 大号时刻 + 路线/日期。点 → `.busList`。数据 = `SEED.busSchedule` 算出的「今日下一班 or 直近未来日首班」。无班次显示「予定なし」。
2. **packageCard**：44×44 危险色底 `Ic.package` + 右上角红色未读数 badge（待領件数）+「宅配便 · {N} 件未受取」+「本日到着」。点 → `.homePackages`。
3. **eventsCard**：32×32 浅强调底 `Ic.calendar` +「今週の活動 · {N} 件」+ 下方 2 条活动预览（日期 MM-DD + 标题 + 时刻）。点 → `.homeEvents`。
4. **musicCard**：44×44 紫渐变（`#A78BFA`→`#7C3AED`）`Ic.music` +「リクエスト曲 · {N} 件」+ top 曲「曲名 · 艺术家」（无则「まだ投稿がありません」）。点 → `.homeMusic`。
5. **lostCard**：「遺失物 · 最新」+ 3 色块网格（遗失物，不属本块，但同在 LifeTab）。

**Android 对齐要点**：Android 已有 `ui/components/HomeCards.kt`，需确认这 5 张卡都在且跳转目标正确（巴士卡跳 `BusListScreen` 不是旧版）。bus 卡的「次のバス便」算法（今日 time > 现在的首班，否则未来日首班）照搬；package 卡红色未读 badge = 待領件数；music 卡紫渐变色值 `#A78BFA`/`#7C3AED` 照搬；events 卡取 `DEFAULT_EVENTS.take(2)` 预览 + 总数。各卡文案「次のバス便」「次回運行」「予定なし」「宅配便 · N 件未受取」「本日到着」「今週の活動 · N 件」「リクエスト曲 · N 件」「まだ投稿がありません」「遺失物 · 最新」照搬。

---

### 附：路由对照（iOS Route → Android 需新增）
`.busList`（特別運航便）/ `.homeBus`（旧版バス時刻，可省）/ `.homePackages` / `.homePackageDetail(id:Int)` / `.homeEvents`（演示日历，可省）/ `.homeEventDetail(id:Int)` / `.homeMusic` / `.homeMusicNew` / `.homeMusicDetail(id:Int)` / `.homeNotifications`（通知中心）/ `.schedule`（行事予定真后端日历）/ `.homeAnnouncements`（公告一覧）/ `.homeAnnouncementDetail(id:String)`。Android `nav/Routes.kt` + `NavGraph.kt` 按此补路由（带参数的用 Navigation Compose 的 `{id}` 路径参数）。`SongReportSheet` 是全局 overlay 弹窗（iOS `openSheet(.songReport(songId:))`），Android 用 `ModalBottomSheet` + 状态触发。

---

I now have complete coverage of the rollcall/NFC/status-bar feature area. Producing the aligned spec section.

## 点呼 / NFC スキャン / 状態条（rollcall-nfc）

> 真值来源（iOS）：`Foundation/Components/TopRollBar.swift`（全 App 顶部状态条）、`Foundation/Components/BottomNav.swift`（中央点呼 FAB）、`Features/Home/HomeStubs.swift`（`RollcallSheet` 行 1165–1491 / `StudyCheckinSheet` 行 1500–1856 / `FeedbackSheet` 行 1863–1940 / amber 卡内点呼 hero 行 282–858）、`Foundation/AppState/AppStore.swift`（`rollState` / `studyState` 状态机 + `recordCheckin()` / `recordStudyTap()`）、`Foundation/AppState/SheetKind.swift`（`RollState` / `SheetKind` 枚举）、`Foundation/Network/Endpoints/RollCallAPI.swift`（真后端端点）、`Foundation/Theme/TTokens.swift`（颜色 token）。对应截图 13。

这块在 iOS 上由 3 个相互独立又联动的部件组成：① 顶部状态条 `TopRollBar`（active/absent/done 时浮在所有页顶部）；② 底部导航中央那颗大圆「点呼」按钮（`BottomNav.centerButton`，任意页常驻）→ 弹 `RollcallSheet` 做 NFC 点呼扫描；③ 学習（晚自习）的 NFC 2 次签到 `StudyCheckinSheet`，从主页 amber 卡（学習対象学生进行中时）的「NFC で签到」按钮进。下面逐部件拆。

---

### ① 顶部状态条 TopRollBar（4 态）

**画面一覧**：不是单独的屏，是一个**胶囊形（Capsule）横条**，挂在 `RootView` 的 `safeAreaInset(edge: .top)` 里。**只在 `rollState != .idle`（即 active / absent / done）时显示**；`idle` 时整条不出现（`RootView.swift` 行 20）。有 sheet 打开时透明度降到 0 且不可点（`opacity / allowsHitTesting`）。

**布局结构**（从左到右，一个 `HStack(spacing: 10)`，内边距 `.padding(.horizontal, 14).padding(.vertical, 10)`，外形 `Capsule`）：
1. **左侧图标**（随状态变 SF Symbol + 颜色）
2. **中间两行文字**（`VStack(alignment: .leading, spacing: 2)`）：第一行 `primaryText`（12pt, semibold），第二行 `secondaryText`（10pt, secondary 灰）
3. **`Spacer()`**
4. **右侧 chevron**（`Ic.chevR()`，半透明 0.5）—— **仅 `done` 态不显示**（done 不可再点）

**整条点击**：`rollState != .done` 时 → `app.openSheet(.feedback)`（打开下面 ④ 的反馈三选一）。done 态点击无反应。

**四态文案 + 配色逐条**（`primaryText` / `secondaryText` / 前景色 `fg` / 背景 `background` / 图标）：

| 态 | 图标(SF Symbol) | 图标色 | primaryText（第一行） | secondaryText（第二行） | 文字前景 fg | 背景 background |
|---|---|---|---|---|---|---|
| **idle** | `clock` | `T.primary`(#1F6B74 teal) | `「次の点呼: 21:00」` | `「タップで体調報告 / 欠席申請」` | `T.ink`(#0F1E22) | iOS26 真 glass / 否则 `T.glassBar`(白 70%) |
| **active** | `dot.circle.fill`（带 pulse 脉冲动画，iOS17+） | `T.danger`(#C44848 红) | `「点呼中 · あと {分}分{秒}秒で遅刻判定」`（如「あと 2分50秒で遅刻判定」，分秒来自 `rollCountdownSec`，`%02d` 补零） | `「タップで欠席申請 / 体調報告」` | `T.warnDeep`(#7A4A0E) | `T.warnBg`(#FDF4E1 浅橙) |
| **absent** | `exclamationmark.triangle.fill` | 白 | `「欠席判定 · 寮監に直接連絡」` | `「寮監室までお越しください」` | 白 | `T.danger`(#C44848 实红) |
| **done** | `checkmark.circle.fill` | `T.ok`(#4A9478 绿) | `「チェックイン済 {时刻} · {判定}」`（如「チェックイン済 21:02 · 時間内」，时刻=`checkinAt`、判定=`checkinKind`） | `「お疲れさまでした」` | `T.okDeep`(#2C6048) | `T.okBg`(#E3F1EA 浅绿) |

active 态倒计时由 `AppStore.rollCountdownSec`（初值 180 秒）驱动，主页 Timer 每秒调 `tickCountdown()` 减 1。done 态由 `recordCheckin()` 触发后 **5 秒自动恢复 idle**（`autoDismissDoneTask`）。

> 注意：amber 卡内部（主页那张大金色卡）也有一套独立的「点呼 hero」显示（`HomeStubs.swift` `rollActiveContent` / `heroStatus` 行 596–714），文案不同（如 active 显「点呼中 · 残り」+ 大号 `{m}:{02d}` 倒计时、absent 显大字「欠席」、done 显「時間内」）。那部分属于「主页 amber 卡」屏，归 Home 那块对齐；这里只负责顶部 `TopRollBar` 状态条本身，但 Android 实现时要知道两者共享同一个 `rollState`。

---

### ② 中央点呼按钮 + RollcallSheet（NFC 点呼扫描弹窗）

**入口**：底部导航条正中那颗**大圆按钮**（`BottomNav.centerButton`，行 128–150）。规格：62×62 圆，填充 `T.rollBtnGrad`（径向渐变 `accentSoft→accent→primary`，圆心偏左上 35%/28%），阴影 `primary` 42% 模糊 10 下移 6；圆内 `shield.checkered` 图标（26pt, bold, 白）；圆下方小字 `「点呼」`（9pt, bold, `T.primary`）。点击触发**中等强度震动反馈**（`UIImpactFeedbackGenerator(style: .medium)`）后 `app.openSheet(.rollcall)`。

**画面一覧**：`RollcallSheet` 是一个底部半弹窗（`GlassSheet`），内部 4 步状态机 `Step { idle, scanning, success, fail }`，每步换一整套内容（`.animation(.easeOut(0.22), value: step)` 过渡）。

**容器（GlassSheet）通用结构**（`GlassSheet.swift`）：底部对齐 → 顶部一个拖动横条（36×5 胶囊，`T.inkMute` 30% 透明，上 10 下 8）→ 内容区 `.padding(.horizontal, 20).padding(.bottom, 40)` → 背景 iOS26 真 glass / 否则 `T.glassSheet`(白 85%)，左右上圆角 28，仅顶部两角圆。进出场 `.move(edge: .bottom) + .opacity`。点弹窗外的暗背景（`GlassBackdrop`）= 关闭。

**Step 1 · idle（扫描准备）布局**（`VStack(alignment: .leading)`，从上到下）：
1. **大标题**（24pt heavy，`kerning -0.24`，行距 6，`T.ink`，下 14）：`「スキャンの準備が\nできました」`（两行）
2. **两步说明**（14pt，`T.inkSub`，下 20）：① `「① 入口の NFC マークにスマホをかざす」` ② `「② 画面が光ったら完了」`
3. **时间外警告横幅**（橙底，`T.warnBg` 填充 + `T.warn` 25% 描边，圆角 12，`T.warnDeep` 文字，内边距 14×10，下 20）：左侧 `⚠` + `「点呼時間外です。点呼開始まで少々お待ちください。」`（12pt，行距 2）
4. **脉冲圆动画**（居中，下 24）：140×140 圆，径向渐变 `T.accent` 25%→5%，2pt `T.accent` 描边，scale 0.94↔1.0 + opacity 0.55↔0.9 循环脉冲（0.7s 往返）；圆内 `iphone.radiowaves.left.and.right`（60pt，`T.primary`）
5. **主按钮**（高 54，圆角 16，填充 `T.rollBtnGrad` 径向渐变，`primary` 32% 阴影，下 10）：`「NFC をかざす」`（16pt bold，`kerning 0.64`，白）→ 调 `simulate()`
6. **取消按钮**（高 48，圆角 16，`T.ink` 6% 浅灰底，`T.inkSub` 文字）：`「キャンセル」`（15pt semibold）→ 关弹窗

**Step 2 · scanning（扫描中，约 0.5 秒）**：居中 `VStack(spacing: 18)`，上下内边距 28：
1. `「スキャン中…」`（22pt bold，`T.ink`）
2. 120×120 旋转环：底环 `T.accent` 30% 描边 3pt，上面 `trim(0~0.3)` 的 `T.primary` 圆弧（圆头），无限匀速旋转（0.9s/圈）；中心 `dot.radiowaves.left.and.right`（44pt，`T.primary`）
3. `「動かないでください」`（13pt，`T.inkSub`）

**Step 3 · success（成功，2 秒后自动关）**：居中 `VStack`，上下 28：
1. 96×96 绿圆（线性渐变 `#8BC6A3→#4A9478` 左上→右下，`#4A9478` 30% 阴影），内 `checkmark`（44pt heavy 白）；进场弹簧 pop-in（scale 0.6→1.0 + 淡入，`spring(0.4, 0.7)`），下 20
2. `「チェックイン完了」`（22pt bold，`T.ink`，下 10）
3. **绿色胶囊 Pill**（`T.okBg` 底，`T.okDeep` 字，内边距 14×6）：`「{checkinAt} · {checkinKind}」`（默认「21:02 · 時間内」，13pt bold）
4. `「お疲れさまでした」`（13pt，`T.inkSub`，上 18）

**Step 4 · fail（失败重试）**：居中 `VStack`：
1. 88×88 红圆（线性渐变 `#E88A80→#C44848`，`T.danger` 30% 阴影），内 `xmark`（40pt heavy 白），下 18
2. `「失敗。もう一度」`（22pt bold，`T.ink`，下 10）
3. `「NFC を読み取れませんでした」`（13pt，`T.inkSub`，下 22）
4. **再试行按钮**（高 54，圆角 16，`T.rollBtnGrad`）：`「再試行」`（16pt bold）→ 回到 idle 步

**流程逻辑（`simulate()`，行 1460）**：点「NFC をかざす」→ 切 scanning → 等 0.5 秒 → 调 `app.recordCheckin()`（写 `checkinAt`=当前 HH:mm、`checkinKind`="時間内"、`rollState`=`.done`）→ 切 success → 再等 2 秒 → `closeSheet()` + Toast `「チェックイン完了 · {时刻}」` → 复位 idle。**取消保护**：弹窗消失时 `scanTask?.cancel()`，且写记录/关窗前都用 `guard app.sheetOpen == .rollcall` 确认当前展示的还是本弹窗（防用户中途开了别的弹窗被误关）。

**共享组件**：`GlassSheet`（半弹窗壳）、`GlassBackdrop`（暗背景）、`Ic.chevR`（右箭头）、`T.*` 颜色 token、`T.rollBtnGrad`（点呼按钮径向渐变）。

---

### ③ 学習 NFC 2 次签到 StudyCheckinSheet

**入口**：主页 amber 卡，当**学習対象学生 + `studyState == .active` + 还有未完成 tap** 时，卡内显示「NFC で签到」按钮（`HomeStubs.swift` `studyActionButtons` 行 472–494，`iphone.radiowaves.left.and.right` 图标 + `「NFC で签到」`，白 70% 底圆角 12）→ `app.openSheet(.studyCheckin)`。

**机制**：一次晚自习要碰 NFC **2 次**——`StudyTap.start`（学習開始，受付 19:35–19:40）和 `.end`（学習終了，受付 21:40–21:50）。**每开一次弹窗只记 1 次 tap**，下次开自动进到下一次（`app.nextStudyTap` 决定当前是第几次）。

**画面一覧**：同样 4 步状态机 `idle / scanning / success / fail`，壳同 `GlassSheet`。

**Step 1 · idle 布局**（`VStack(alignment: .leading)`）：
1. **小标号**（11pt heavy，`kerning 1.8`，大写，`T.primary`，下 6）：`「{N} / 2 回目」`（N=1 或 2，`stepNumber`）
2. **大标题**（24pt heavy，`T.ink`，下 12）：`stepLabel` —— 第 1 次 = `「学習開始のタップ」`，第 2 次 = `「学習終了のタップ」`，全完成 = `「本日完了」`
3. **受付时间 pill**（`T.pill` 底圆角 10，`T.inkSub` 字，内边距 12×8，下 18）：`clock` 图标 + `「受付時間: {窗口}」`（`stepTimeWindow`：start=`「19:35〜19:40」`、end=`「21:40〜21:50」`）
4. **两步说明**（14pt，`T.inkSub`，下 22）：`「① 学習室入口の NFC マークにスマホをかざす」` / `「② 画面が光ったら完了」`
5. **脉冲圆动画**（同 RollcallSheet 那套 140×140，下 24）
6. **主按钮** `「NFC をかざす」`（同 RollcallSheet 规格）→ `simulate()`
7. **取消按钮** `「キャンセル」`（同上）

**Step 2 scanning** 与 RollcallSheet **完全一致**（`「スキャン中…」` + 旋转环 + `「動かないでください」`）。

**Step 3 · success**：96×96 绿圆 + checkmark（同 RollcallSheet）→ 标题 `successTitle`：start 完成=`「開始タップ完了」`、end 完成=`「終了タップ完了」`。下方分两种：
- 还有下一次 tap → `「次は {次のラベル} を {窗口} に」`（如「次は 学習終了 を 21:40〜21:50 に」，13pt，`T.inkSub`）
- 全部完成 → 绿胶囊 Pill：`「{HH:mm} · 本日の学習出席は完了」`（`T.okBg`/`T.okDeep`）

**Step 4 fail** 与 RollcallSheet 一致（`「失敗。もう一度」` / `「NFC を読み取れませんでした」` / `「再試行」`）。

**流程（`simulate()` 行 1805）**：切 scanning → 0.5 秒 → `app.recordStudyTap()`（往 `studyTaps` 集合插入 `nextStudyTap`，并往 `studyHistory` 插一条记录）→ 切 success → 2 秒 → 关窗 + Toast（全完成=`「学習出席完了 · 全 2 回 タップ済み」`，否则=`「{tap名} 完了」`）。同样有 `guard app.sheetOpen == .studyCheckin` 取消保护（IX-011）。

---

### ④ 反馈三选一 FeedbackSheet（点 TopRollBar 进）

点 `TopRollBar`（非 done 态）弹此 sheet。布局（`GlassSheet` 内 `VStack(alignment: .leading)`）：
1. 标题 `「反馈を送る」`（20pt heavy，`T.ink`，下 6）
2. 副标题 `「どの種類の反馈を送りますか？」`（13pt，`T.inkSub`，下 18）
3. **3 个选项卡**（`VStack(spacing: 10)`，每个 `Button`：白 55% 底 + `T.hair` 0.5pt 描边，圆角 16，内边距 16×14；左 emoji 28pt + 中两行文字 + 右 `Ic.chevR(16)` `T.inkMute`）：
   - 🤒 `「体調問題を報告」` / 副 `「発熱・頭痛・その他の症状を先生に通知」` → 开 `.health`（HealthSheet）
   - 📝 `「今回欠席の申請」` / 副 `「今回の点呼を欠席したい理由を申請」` → 开 `.absence`（AbsenceSheet）
   - 💬 `「その他の問題」` / 副 `「遅刻理由・外出中・NFC 不具合など」` → 开 `.other`（OtherSheet）

> HealthSheet / AbsenceSheet / OtherSheet 三个子弹窗（体調報告表单、欠席理由 textarea、その他分類）属表单类，主要归「申请/反馈」那块对齐；这里只需知道它们由 FeedbackSheet 分发。其中 OtherSheet 的分类选项含 `「NFC 不具合」`（NFC 读不到时走这里报障）。

---

### 导航 / 数据源小结

- **顶部状态条**：`RootView.safeAreaInset(.top)` 常驻挂载，`rollState != .idle` 才显示；点它（非 done）→ `.feedback` 弹窗。
- **中央点呼按钮**：`BottomNav` 常驻，点 → `.rollcall` 弹窗。
- **学習签到**：主页 amber 卡（active 态）按钮 → `.studyCheckin` 弹窗。
- **所有弹窗**统一走 `AppStore.sheetOpen: SheetKind?` 单一状态 + `GlobalOverlays.sheetContent(for:)` 分发渲染，`openSheet/closeSheet` 带弹簧动画。
- **数据源（当前 iOS 状态）**：点呼/学習签到目前都是**本地 mock**——`recordCheckin()` / `recordStudyTap()` 只改内存状态、不发网络。真后端端点已在 `RollCallAPI.swift` 备好：`POST /api/v1/rollcall/sessions/{sessionId}/checkins`，请求体 `RollCallCheckinBody`（字段 `card_uid` / `student_id` / `idempotency_key` / `status_source`="auto_nfc" 或 "manual_checkin" / `ts_local` / `path_hint`="A"/"B"/"manual"），响应 `RollCallEventOut`（`base_status`="present"/"late"/"absent"/"exempt_range" 等）。代码注释 TODO 写明：真流程 = NFC tap 拿 tag UID → POST → 后端返回 record → 更新 `rollState/checkinAt/checkinKind`。Android 对齐**先照 iOS 做成 mock 版（同样本地改状态、同样动画），网络层等 iOS 接通后再一起接**。

---

### Android 对齐要点

Android 现状（`03_dev/student_android/v1/`）= 纯 UI 桩 + `MockData.kt`，**没有顶部状态条、没有中央点呼按钮的弹窗、没有任何 NFC 流程、没有网络层**。要从零补出跟 iOS 几乎一样的三个部件。Compose 实现提示：

**A. 顶部状态条 `TopRollBar`（Composable）**
- 用 `Scaffold` 的顶部插槽 或 在根 `Box` 顶部叠一层；**仅当 `rollState != Idle` 时 compose**（iOS idle 不显示）。
- 一个 `Row`（圆角胶囊 = `Modifier.clip(CircleShape)` 或 `RoundedCornerShape(50)`），`horizontalArrangement = spacedBy(10.dp)`，内边距 `padding(horizontal = 14.dp, vertical = 10.dp)`。左 `Icon` + 中 `Column`（两行 `Text`，12sp semibold / 10sp 灰）+ `Spacer(Modifier.weight(1f))` + 右箭头（done 态不画）。
- 状态用 `enum class RollState { Idle, Active, Absent, Done }`（对齐 iOS `RollState`）。四态文案/配色**逐字照上表搬**（日语原文不动）。颜色建在一个 `object T` 里（对齐 `TTokens.swift`）：`primary=0xFF1F6B74`、`danger=0xFFC44848`、`ok=0xFF4A9478`、`warnBg=0xFFFDF4E1`、`warnDeep=0xFF7A4A0E`、`okBg=0xFFE3F1EA`、`okDeep=0xFF2C6048`、`danger 实红做 absent 底`。
- active 的图标脉冲：用 `rememberInfiniteTransition` 做 alpha 或 scale 循环（对齐 iOS `symbolEffect(.pulse)`）。倒计时文案 `「点呼中 · あと %d分%02d秒で遅刻判定」`——Kotlin `String.format("...%d分%02d秒...", min, sec)`。
- 整条 `Modifier.clickable { if (rollState != Done) openSheet(Feedback) }`。

**B. 中央点呼按钮（底部导航 FAB）**
- 底部导航中间一颗 62.dp 圆 `Box`，背景画径向渐变（Compose `Brush.radialGradient(listOf(accentSoft, accent, primary), center = Offset(0.35f, 0.28f) 比例换算)`），`Icon(shield 图标，26.dp 白)`，下方 9sp `「点呼」`。
- 点击先触发震动：`val haptic = LocalHapticFeedback.current; haptic.performHapticFeedback(HapticFeedbackType.LongPress)`（或用 `Vibrator` 系统服务做 medium impact 等效）→ 打开 rollcall 弹窗。

**C. 弹窗体系（GlassSheet 等效）**
- iOS 是自研 `GlassSheet`（底部半弹窗）。Android 用 `ModalBottomSheet`（Material3）或自绘 `Box` 底部对齐 + `AnimatedVisibility(slideInVertically + fadeIn)`。顶部画拖动横条（36×5.dp 圆角），圆角 `RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)`，半透明白底 + 模糊（Android 无原生毛玻璃，退化成 `Color.White.copy(alpha = 0.85f)` 即可，对齐 iOS 非 iOS26 的 fallback）。
- 弹窗状态用一个 `sealed interface SheetKind { Rollcall; Feedback; Health; Absence; Other; StudyCheckin; ... }` + ViewModel 里 `MutableStateFlow<SheetKind?>`，对齐 iOS `AppStore.sheetOpen`。

**D. RollcallSheet / StudyCheckinSheet 状态机**
- 各自一个 `enum class Step { Idle, Scanning, Success, Fail }`，`remember { mutableStateOf(Step.Idle) }`，用 `Crossfade` 或 `AnimatedContent(targetState = step)` 切 4 套内容（对齐 iOS `.animation(easeOut 0.22)`）。
- idle 的脉冲圆：140.dp `Box`，径向渐变填充 + 2.dp 边框圆 + 中心 `Icon`，`rememberInfiniteTransition` 做 scale 0.94↔1.0 / alpha 0.55↔0.9。
- scanning 的旋转环：`drawBehind` 或 `Canvas` 画底环 + `drawArc(startAngle, sweepAngle = 108f /* 0.3圈 */)`，配 `infiniteTransition` 旋转 0→360（0.9s 匀速）。
- success 的 pop-in：`animateFloatAsState`（scale 0.6→1.0 + alpha）配 spring。
- **流程照搬延时数值**：scanning 0.5 秒、success 停 2 秒后自动关。用 `LaunchedEffect` + `delay(500)` / `delay(2000)`，并在 `DisposableEffect`/`onDispose` 取消（对齐 iOS `scanTask.cancel()` + `guard sheetOpen == .rollcall`，防误关）。
- mock 记录：在 ViewModel 写 `recordCheckin()`（设 `checkinAt`=当前 HH:mm、`checkinKind`="時間内"、`rollState=Done`，5 秒后自动回 Idle 用 `viewModelScope.launch { delay(5000); ... }`）和 `recordStudyTap()`（往 `studyTaps: Set<StudyTap>` 加 `nextStudyTap`）。`StudyTap` = `enum { Start, End }`，`nextStudyTap` 逻辑：没 Start 返 Start，没 End 返 End，否则 null。

**E. NFC 实现要点（iOS CoreNFC vs Android NfcAdapter 差异）**
- **当前阶段都是 mock**，按钮点了走假动画，不真碰 NFC——**Android 第一版照 iOS 做 mock 即可，真 NFC 留到后端接通同步做**。下面是真接时的差异提示，先写进文档备查：
  - iOS 用 **CoreNFC**（`NFCNDEFReaderSession` / `NFCTagReaderSession`），权限在 `TomoshibiApp.entitlements` 声明 `com.apple.developer.nfc.readersession.formats = [NDEF, TAG]`；iOS NFC 是「按需开一次会话弹系统扫描 UI」模式（用户主动点才扫）。
  - Android 用 **`NfcAdapter`**（`android.nfc` 包）。两种模式：① **前台调度 Foreground Dispatch**（`enableForegroundDispatch`，App 在前台时优先接收 tag）或 ② **Reader Mode**（`enableReaderMode`，更可控，推荐点「NFC をかざす」后开启）。权限要在 `AndroidManifest.xml` 加 `<uses-permission android:name="android.permission.NFC"/>` + `<uses-feature android:name="android.hardware.nfc"/>`。
  - tag 数据：iOS/Android 都读 NDEF 或裸 tag UID。后端 `RollCallCheckinBody.card_uid` 收的就是卡 UID（路径 A），`path_hint` 标 "A"/"B"/"manual"。Android 接真 NFC 时从 `Tag`/`NdefMessage` 取 UID 填 `card_uid`，其余字段对齐 iOS（`status_source="auto_nfc"`、客户端生成 `idempotency_key` UUID 防重复）。
  - 后端端点照搬：`POST /api/v1/rollcall/sessions/{sessionId}/checkins`，请求/响应字段跟 iOS `RollCallCheckinBody` / `RollCallEventOut` 一对一（Android 用 Retrofit + 同名 snake_case data class）。

**F. 反馈三选一 FeedbackSheet**：照上 ④ 做，3 个选项卡（emoji + 两行文字 + 右箭头），点各自打开 health/absence/other 三个表单弹窗（表单内容归「申请/反馈」那块，这里只做分发框架）。日语文案逐条照搬。

---

