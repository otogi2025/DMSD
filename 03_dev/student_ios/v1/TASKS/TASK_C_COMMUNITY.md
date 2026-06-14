# TASK C · Community (Home 子页 18 页) · SwiftUI 实装

> **Dispatch**: Agent tool · subagent_type=`general-purpose`
> **工程**: `03_dev/student_ios/v1/TomoshibiApp/Features/Community/CommunityStubs.swift`
> **翻译源**: `phaseB_src/33f0266b__NotificationsPage_PackagesPage_PackageDetailPage.js`（demo 阶段 JSX 源，已归档、不在仓库）

## 产物

**Replace** `CommunityStubs.swift` 全部内容（18 struct + 1 CommunityStub 工具），保留文件名（xcodegen auto-include）。

## 18 Views · 分 2 档（优先级）

### ⭐ 必做 8 核心页

1. **NotificationsView** — ScrollView · filter pill row (全て / 申請 / 減点 / 宅配 / 活動 / リクエスト曲) · Card × SEED.notifications (5 件) · 每条 type icon + title + time + body + 红点 unread
2. **PackagesView** — 2-tab (待領 / 領済) · Card list · 每 card status pill + date + from + 「確認受取」button (待領 only)
3. **PackageDetailView** — 从 SEED.packages.first(where: {$0.id == id}) 拿 item · date/from/tracking/status + 「受取完了」button → toast
4. **BusView** — 若 SEED.busNotice.active → amber banner · 3 便 list · next=true 的 green border + 「次の便」pill
5. **EventsView** — segmented picker (list / calendar) · list: 3 件 event card · calendar: SwiftUI LazyVGrid 模拟日历 (仅当月，有 event 的日子标点)
6. **EventDetailView** — 大标题 + date/time/place/desc Card · 「iPhone カレンダーに追加」PrimaryButton → toast "カレンダーに追加しました"
7. **WallView** — 5 posts · Card · Avatar(letter: first char of author) + author/time + text + heart/bubble/flag row · FAB "+" → `.homeWallNew`
8. **MusicView** — 8 songs ranked · Card: #idx + title/artist + by/up/down · up/down button toggle · FAB "+" → `.homeMusicNew`

### 💤 余 10 页 · 简 stub（PageHeader + EmptyState + `Spacer()`）

LostView / LostNewView / LostDetailView / MusicNewView / MusicDetailView / WallNewView / WallDetailView / SuggestView / SuggestFeedView

```swift
struct LostView: View {
    var body: some View {
        VStack {
            PageHeader(title: "落とし物", level: 2)
            EmptyState(icon: "tray", title: "落とし物", message: "(D3 実装予定)")
            Spacer()
        }
        .background(T.pearl)
    }
}
```

## Foundation API

读 `03_dev/student_ios/v1/TomoshibiApp/Foundation/` 全部文件熟悉。关键:

- `@EnvironmentObject var router: RouterStore` · `router.go(.xxx)` / `router.back()`
- `@EnvironmentObject var app: AppStore` · `app.showToast("...")` / `app.openSheet(.kind)`
- `SEED.notifications / .packages / .buses / .busNotice / .events / .lost / .songs / .wall / .suggestions`
- `PageHeader(title:, level: 2/3, right: AnyView?)` · 含长按 0.4s breadcrumb
- `Card(padding:, radius:) { content }` · paper bg + shadow
- `Pill(text:, tone: .neutral/.ok/.warn/.danger/.accent)`
- `Avatar(letter:, size:)` · cobalt soft 圆
- `Ic.bell/package/bus/calendar/heart/comment/music/plus/chevR/up/down/flag/search/x/close` 全齐
- `PrimaryButton(title:, icon:, enabled:, destructive:, action:)` / `GhostButton`
- `EmptyState(icon:, title:, message:?)`
- T tokens: T.primary / T.ink / T.inkSub / T.inkMute / T.warnBg/warnDeep / T.okBg/okDeep / T.pill / T.paper / T.pearl / T.hair / T.danger / T.Radius.sm/md/lg

## ⚠️ Color hex String 处理

`SEED.lost[i].color` 是 "#3b82f6" 这种 String · T.swift 里只有 `Color(hex: UInt32)`。文件内部加 private helper:

```swift
private func colorFromHex(_ hex: String) -> Color {
    var h = hex.trimmingCharacters(in: .whitespaces)
    if h.hasPrefix("#") { h.removeFirst() }
    var v: UInt64 = 0; Scanner(string: h).scanHexInt64(&v)
    return Color(red: Double((v >> 16) & 0xff)/255, green: Double((v >> 8) & 0xff)/255, blue: Double(v & 0xff)/255)
}
```

## 产出要求

1. Replace `CommunityStubs.swift` · 18 struct · 600-900 行
2. 每 struct `#Preview { XxxView().environmentObject(RouterStore()).environmentObject(AppStore()) }`
3. Build verify: `cd 03_dev/student_ios/v1 && xcodegen generate && xcodebuild -project TomoshibiApp.xcodeproj -scheme TomoshibiApp -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -configuration Debug build 2>&1 | grep -E "error:|BUILD"` → `** BUILD SUCCEEDED **`
4. 完成 report（完成 page 清单 + build 状态 + 偏差）

## 不要做

- ❌ 改 Foundation/ · Route.swift · project.yml · Assets.xcassets · 其他 feature folder
- ❌ git commit（parent 批量）
