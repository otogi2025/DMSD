# Remote Agent Guide · Tomoshibi iOS · v2 HTML-fidelity Rewrite

> **你是从 Anthropic cloud 启动的 routine agent**。工程在 GitHub `otogi2025/Tomoshibi-iOS`。你的任务：**按 Phase B HTML 1:1 pixel-level fidelity** 重写某 feature 的 Swift。之前 v1 pass 的 agent（A/B/C）自由发挥过度 — **不满足要求，需要重做**。
> **当前 baseline commit**: `8bcf856` (master)
> **你的产出**: Push 到 branch `feature/<agent>-v2` → open PR → itsuki 审后 merge

---

## 0. 你的 feature id + prompt 指派

看 Anthropic 下发的 prompt 开头会标 `Agent: A / B / C / D / E`。对应任务:

| Agent | Feature | JSX 源 (refs/phaseB_src/) | 目标文件 | 分支 |
|---|---|---|---|---|
| **A** | Auth 10 页 | c13988a3__SplashPage_OnboardingPage_RegisterDonePage.js | TomoshibiApp/Features/Auth/AuthStubs.swift | feature/auth-v2 |
| **B** | Home 6-8 页 + 5 sheets | 364061ea__HomePage_RollcallSheet_FeedbackSheet.js | TomoshibiApp/Features/Home/HomeStubs.swift | feature/home-v2 |
| **C** | Community 17-18 页 | 33f0266b__NotificationsPage_PackagesPage_PackageDetailPage.js | TomoshibiApp/Features/Community/CommunityStubs.swift | feature/community-v2 |
| **D** | Apply 13 页 · StayForm 最复杂 | 100ba570__ApplyListPage_ApplyNewPage_ApplyFormPage.js | TomoshibiApp/Features/Apply/ApplyStubs.swift | feature/apply-v2 |
| **E** | MyPage 14 页 + LogoutSheet | e38fcebf__LogoutSheet.js | TomoshibiApp/Features/MyPage/MyPageStubs.swift | feature/mypage-v2 |

共通源（所有 agent 需读）:
- `refs/phaseB_src/c281cafa__module.js` — T tokens 权威 + SEED data
- `refs/phaseB_src/8b866e02__RouterProvider_AppProvider_BreadcrumbPopup.js` — 原子组件 + Icons 全量 SVG path
- `refs/Tomoshibi_iOS_PhaseB_v2.html` — 视觉 source of truth（你可以双击跑，如果 cloud env 不支持就读 HTML inline CSS）
- `refs/IOS_DESIGN_LOG.md` — iOS 専属设计决策（Q1-8 + N1-20 + §3.9 学号 6 桁 + §3.10 房间号 + §3.11 改动履歴）
- **`refs/system_features_v0.1.md`** ⭐ **iOS + Web + 後端 共用機能マトリクス（single source of truth）** — 新機能を扱う前に必ず読み、実装後に DMSD 側の同ファイルへ逆同期する（itsuki 経由）
- `refs/跨会话_ios_共享决策.md` — iOS-Swift-CC ↔ Web-CC 短期協作スナップショット（実装 TODO ビュー）

---

## 1. Fidelity 铁律（v2 核心差异 vs v1）

### 1.1 文字 / 数字逐字对照

**不要润色，不要 smarten、不要改句式**。从 JSX 里 `<span>...</span>` 里拿原文，直抄到 Swift `Text("...")`。

示例：
- JSX: `<div>あと <b>{mm}</b>分 {ss}秒で遅刻判定</div>` → Swift: `Text("あと ") + Text("\(mm)").bold() + Text("分 \(ss)秒で遅刻判定")`（保留"分"前的全角空格 / "秒"后的正文）
- JSX: `'平日: 朝 7:00 / 晚 21:00'` — 注意已在 v2 HTML 里改为 `晩`。**用 `晩` 不用 `晚`**（v2 HTML 的中文残留已修）

### 1.2 数值严格对照 JSX inline style

JSX `style={{ fontSize: 13, fontWeight: 500, lineHeight: 1.6 }}` → Swift `.font(.system(size: 13, weight: .medium))`

**不要**:
- 四舍五入（13pt 不要变 14pt 因为"iOS 习惯"）
- 重新拟定 spacing（原 `gap: 12` 不要改 16）
- 换 color hex（原 `#1f6b74` 不要用 Color.accentColor 或 SF Pro default）

### 1.3 Icon 全部自绘 Path（不用 SF Symbols）

Phase B 所有 icon 是 inline SVG stroke-based 定义在 `8b866e02__...js` 的 `Ic` object。

现有 Foundation `Ic.swift` 用 SF Symbols wrap — **对于你 feature 中的 icon，如果视觉 diff 大，请在你 feature folder 新建 `CustomIcons.swift`** 并用 SwiftUI `Path` 重绘，不用 Foundation 的 SF Symbols fallback。

SF Symbols 可接受 only if：
- icon 极简（叉 / 加号 / 圆点）SF Symbols 的 `xmark` / `plus` / `circle.fill` 视觉差异 < 10%
- 其他一律自绘

**自绘 SwiftUI Path 模板**（参考 JSX `Ic.bell`）:
```swift
struct BellIcon: View {
    var size: CGFloat = 22
    var body: some View {
        Canvas { ctx, s in
            var p = Path()
            // JSX: <path d="M6 17V11a6 6 0 1 1 12 0v6l1.5 2h-15L6 17Z"/>
            p.move(to: CGPoint(x: 6, y: 17))
            p.addLine(to: CGPoint(x: 6, y: 11))
            p.addArc(...)  // 按 JSX d 属性 直译
            // stroke, not fill
            ctx.stroke(p, with: .color(.primary), lineWidth: 1.6)
        }
        .frame(width: size, height: size)
    }
}
```

或用 `SwiftUI Path` + `.stroke` on Shape。

### 1.4 颜色严格对照 `c281cafa T 对象`

T tokens 原值全在 `refs/phaseB_src/c281cafa__module.js` 的 `const T = {...}`。Foundation/Theme/TTokens.swift 已尽力对照，若某个颜色不一致请在你 feature 里用 hex literal 精确覆盖（**不要改 Foundation**）。

### 1.5 动画 timing 对照 CSS keyframes

JSX 的 `@keyframes slideUp { from{transform:translateY(30%)opacity:0} to{transform:translateY(0)opacity:1} }` + CSS `animation: slideUp 0.34s ease-out` → Swift:
```swift
.offset(y: show ? 0 : (30 * geo.size.height / 100))
.opacity(show ? 1 : 0)
.animation(.easeOut(duration: 0.34), value: show)
```

常见 keyframes:
- `fadeIn 0.2s` → `.easeIn(duration: 0.2)`
- `zoom 0.22s` → `.scaleEffect(show ? 1 : 0.8).opacity(...)` + `.easeOut(0.22)`
- `slideUp 0.34s` → 见上
- `pulse 1.4s` → `.opacity(pulseOn ? 0.3 : 0.8)` + `.easeInOut(duration: 0.7).repeatForever(autoreverses: true)`

### 1.6 Layout 对照 CSS flexbox / grid

JSX `<div style={{display:'flex', gap:10, padding:'14px 16px'}}>` → Swift:
```swift
HStack(spacing: 10) {
    ...
}
.padding(.horizontal, 16).padding(.vertical, 14)
```

`gap: X` = `spacing: X`；`padding: 'A B'` = `.padding(.vertical, A).padding(.horizontal, B)`

### 1.7 圆角对照 `border-radius`

CSS `border-radius: 22px` → Swift `.clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))`

T.Radius: xs=8 / sm=12 / md=16 / lg=22 / pill=9999 — 可直接用常量。

### 1.8 禁止做的自由发挥

- ❌ "这里加个 chevron 图标更 iOS 化" — **不加**
- ❌ "文案改成敬体更自然" — **不改**
- ❌ "用 NavigationStack 代替 hash router" — **不用**
- ❌ "按钮改 primary tint 而不是 gradient" — **不改**
- ❌ "Sheet 改成 native `.sheet()`" — **不改**
- ❌ "字体改 .title / .body SwiftUI 语义字体" — **不改，用 .system(size: N, weight: W)**

---

## 2. Foundation API（**不要改 Foundation**，只消费）

所有 Foundation 代码位于 `TomoshibiApp/Foundation/`。**冻结**。

你只能消费：

### 2.1 State
```swift
@EnvironmentObject var router: RouterStore   // go(_:) back() replace(_:) jump(to:)
@EnvironmentObject var app: AppStore          // openSheet(_:) closeSheet() showToast(_:) simulateCheckin()
// app: rollState (RollState) / sheetOpen (SheetKind?) / breadcrumbOpen (Bool) / toast (String?) / isDark (@AppStorage) / rollCountdownSec / checkinAt / checkinKind
```

### 2.2 Route (enum)
32 case 详细见 `TomoshibiApp/Foundation/Routing/Route.swift` · 不新增不改 case

### 2.3 SEED (enum)
14 集合见 `TomoshibiApp/Foundation/Seed/SEED.swift` · **数据已对齐 Web Round 3**：M101 / 男寮 / 4.5 分 / 迟到 5 · 欠席 2

### 2.4 Components (struct)
`TomoshibiApp/Foundation/Components/`: PrimaryButton / GhostButton / Field / TField / TArea / RadioCard<V> / Avatar / Card / Pill / SectionHeader / TToggle / EmptyState / Skeleton / PageHeader / TopRollBar / BottomNav / BreadcrumbOverlay / IOSStatusBar / Toast

`TomoshibiApp/Foundation/LiquidGlass/`: GlassCard / GlassSheet / GlassBackdrop

`TomoshibiApp/Foundation/Components/Icons/Ic.swift` · 23 SF Symbols wrap — **fidelity 高时不用这个，自绘 Path**

### 2.5 T Tokens
`TomoshibiApp/Foundation/Theme/TTokens.swift` · 见 c281cafa 的 T 对象 Swift 化

---

## 3. 产出 workflow (Routine 必做步骤)

### Step 1: Clone + Branch
```bash
cd /tmp
git clone https://github.com/otogi2025/Tomoshibi-iOS.git
cd Tomoshibi-iOS
git checkout -b feature/<agent>-v2   # e.g. feature/auth-v2
```

### Step 2: 读全部 refs
- `refs/REMOTE_AGENT_GUIDE.md` (本档) — 读完整
- `refs/phaseB_src/<你的对应 JS>` — 逐段读，记住 JSX 组件名 + style + state
- `refs/phaseB_src/c281cafa__module.js` — T tokens + SEED
- `refs/phaseB_src/8b866e02__...js` — 原子组件 + Ic SVG paths
- `refs/IOS_DESIGN_LOG.md` §2-§6 — 架构决策
- `refs/QA_Round1_PhaseB.md` — 已知 bug 修正（C1 中文残留 / C2 数据对齐 / C3 申请类型 8 种接受）

### Step 3: 读现有 Foundation（不改）
```
TomoshibiApp/Foundation/**/*.swift
```
熟悉可用 API。

### Step 4: 读现有 stub（v1，你要替换它）
```
TomoshibiApp/Features/<你的 feature>/[Feature]Stubs.swift
```
v1 是 filler，不是 baseline — 你要**按 JSX 1:1 重写**，不要基于 v1 "improve"。

### Step 5: 写 Swift · 按 Fidelity 铁律

替换 `[Feature]Stubs.swift` 内部所有 struct。每个 struct:
- 遵循 §1 Fidelity 铁律
- 添加 `#Preview { XxxView().environmentObject(RouterStore()).environmentObject(AppStore()) }`
- 用 private inline helper struct（如自绘 icon / SectionLabel / InfoRow / ChipGroup）避免污染其他 feature

### Step 6: Build 验证（**必须通过**）

```bash
cd ~/dev/TomoshibiiOSApp   # 实际 routine env 里是 /tmp/Tomoshibi-iOS
# 如果 routine 有 Xcode:
xcodegen generate
xcodebuild -project TomoshibiApp.xcodeproj -scheme TomoshibiApp \
  -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
  -configuration Debug build 2>&1 | grep -E "error:|BUILD"

# 如果 routine 无 Xcode (Linux container):
# 先用 swift CLI 做 lint:
swift -frontend -parse TomoshibiApp/Features/<your>/*.swift 2>&1 | head -50
# 或确认语法对即可 push（itsuki 起来会实际 xcodebuild）
```

若 routine env 无 Xcode：跳过 xcodebuild，改为 `swift -parse` 语法检查 + 人肉 review 你代码 3 次。

### Step 7: Commit + Push + PR

```bash
git add -A
git commit -m "feat(<agent>-v2): HTML-fidelity rewrite of <Feature> per REMOTE_AGENT_GUIDE"
git push -u origin feature/<agent>-v2
gh pr create --title "<Agent> v2 · <Feature> HTML-fidelity rewrite" \
             --body "..." \
             --base master --head feature/<agent>-v2
```

PR body 应列：
- 完成 views + 行数
- build 状态
- 与 v1 的主要视觉 diff
- 已知偏差 / TODO

---

## 4. Agent 特定清单

### Agent A · Auth (10 views)
1. SplashView — fadeIn 1.8s → `router.replace(.onboarding)`
2. OnboardingView — 3 屏 TabView
3. RegisterStep1-4 — 4 step form + progress 25/50/75/100
4. RegisterDoneView — ✅ zoom + 显「あなたのアカウント番号: **00**」
5. LoginView — 2 tab（番号 / メール）· 00 seed 魔法 · 3 次错锁
6. LockoutView — MM:SS 倒计时 · 升级 hint
7. PwResetView — 静态说明

**JSX 特殊点**：
- Register Step2 的 radio card 用 `v:'regular'` / `v:'soccer'` · JSX 里含时刻表 text "平日: 朝 7:00 / **晩** 21:00 · 土日: 朝 8:00 / 晩 21:30"
- Step4 的警示 banner 是 `style={{ background:'#f6e6b0', padding:'12px 14px', borderRadius:10 }}` + ⚠ icon

### Agent B · Home (6-8 views)
- HomeView — ScrollView · greeting + 扣分 amber card + 3 inner tab (生活 / コミュ / 通知)
- RollcallSheet — 4 态 state machine（preparing / scanning / success / fail）· Liquid Glass · slideUp 0.34s · `symbolEffect(.pulse)` 或 Path 手绘脉冲
- FeedbackSheet — 3 选 1 row
- HealthSheet / AbsenceSheet / OtherSheet — form

**JSX 特殊点**：
- Home 扣分 card 的 gradient `linear-gradient(135deg, #ffe9b5 0%, #f4c677 100%)` · 4.5 点是 `<span style={{fontSize:56, fontWeight:800}}>` (**不是 48**)
- Rollcall sheet 的手机插画圆圈直径 120pt + 内 SVG phoneTap icon 大约 60pt

### Agent C · Community (17-18 views)
- Notifications / Packages × 2 / Lost × 3 / Music × 3 / Wall × 3 / Events × 2 / Bus / Suggest × 2
- EventsView 双视图 (list / calendar grid)
- LostView 2 col photo grid (color hex string → Color)

**JSX 特殊点**：
- NotificationsView filter pill row 是 `['すべて','申請','減点','宅配','活動']` — 注意是 `宅配` 不是 `快递`（v2 HTML 已修）
- WallView 每条底部 icon row gap=16 · color=inkMute · heart/comment/flag 三个 + count

### Agent D · Apply (13 views · StayForm 最复杂)
- ApplyList — 4-tab filter · SEED.applications 5 件 · FAB
- ApplyNew — 8 APPLY_TYPES grid
- ApplyFormDispatcher — dispatch kind
- **StayForm** 8 section (见 v1 TASK_D_APPLY.md)
- GenericApplyForm — 6 kind 通用
- ApplyPreview / ApplyDone / ApplyDetail

**JSX 特殊点**：
- APPLY_TYPES 保留 8 种 (outing/stay/holiday/return/repair/parcel/guest/other) — **不要砍到 7**（C3 已定方案 iii）
- StayForm 中的 meal checkbox grid 是 5×3 日期×餐次（JSX line ~200）

### Agent E · MyPage (14 views + LogoutSheet)
- MyLanding — profile card + 10 menu rows + logout button
- MyInfo / MyRollcall (34 件) / MyPoints (amber card + 7 records) / MyPointsChart (**SwiftUI Canvas 折线图**)
- MyDiscipline / MyHealth / MyClean / MyPackages / MySettings / MyAbout
- MyRollcallDetail
- LogoutSheet (已基础实装可保留或增强)

**JSX 特殊点**：
- MyPoints top card gradient `linear-gradient(135deg, #ffefc2 0%, #f4c677 100%)` (与 Home 的 #ffe9b5 不同) · color `#5c3410`
- Chart 可用 Canvas API + Path 手画 threshold 4 / 8 dash line + 12-month line + dots

---

## 5. Routine 结束 criteria

Routine 完成 = 满足以下全部:
- [ ] ≥90% view 按 Fidelity 铁律对照
- [ ] 每个 public struct 有 `#Preview`
- [ ] 语法 / 编译 pass（无 swift compile error）
- [ ] `git push` + `gh pr create` 成功
- [ ] PR body 有完整 report

Routine 失败 = 任一未满足 → 不 push → 写 error report 到日志

---

## 6. itsuki 醒来后 (4am+ JST) 做的事

对 5 个 PR (feature/auth-v2 / feature/home-v2 / feature/community-v2 / feature/apply-v2 / feature/mypage-v2) 逐一 review + merge:
```bash
cd ~/dev/TomoshibiiOSApp
git fetch --all
git checkout master
# 逐 branch review
gh pr list
gh pr view <n> --web   # 看 diff
gh pr merge <n> --squash  # or --merge
```

Merge 完后:
```bash
xcodegen generate
xcodebuild -scheme TomoshibiApp ...
```

应 `** BUILD SUCCEEDED **`。

---

**END of Remote Agent Guide**
