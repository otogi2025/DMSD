# TASK E · MyPage (マイページ 14 页) · SwiftUI 实装

> **Dispatch**: Agent tool · subagent_type=`general-purpose`
> **工程**: `~/dev/TomoshibiiOSApp/TomoshibiApp/Features/MyPage/MyPageStubs.swift`
> **翻译源**: `/Users/kurekoduki/dev/DMSD/03_dev/demo_4-28/Student_iOS_new/designs/phaseB_src/e38fcebf__LogoutSheet.js`

## 产物

**Replace** `MyPageStubs.swift` 全部内容。14 个 View + LogoutSheet。保留文件名。

**⚠️ 注意**: MyLandingView **已有基础实装**（显示 profile card + menu list），可在此基础扩展或重写。LogoutSheet 也已实装，保留或扩展。

## 14 Views · 分 2 档

### ⭐ 必做 7 核心页

1. **MyLandingView** (L1) — 顶部 profile card (Avatar 大 + 氏名 + 番号) · 2 Pill (男寮 M101 + 一般寮生) · 10 入口 menu list · 底部 ログアウト button → `app.openSheet(.logout)`
2. **MyInfoView** (L2) — 全 read-only 个人情報 list: 氏名 / 生年月日 / 年齢 / 性别 / 番号 / 寮・部屋 / 区分 / メール / 電話 · 底部 info box 「情報を変更する場合は、寮監にご連絡ください」
3. **MyRollcallView** (L2) — 月 filter (4 月 / 3 月 / 2 月) · SEED.rollcall list · group by date · 每行: date/session/state Pill/method icon
4. **MyPointsView** (L2) — 顶部 amber gradient card (今月合計 4.5 点 大字) · 进度条 (0/4/8 threshold marker) · SEED.points list · 每行 date/session+kind/+val · 底部 info box 「現在のルール: 遅刻 0.5 / 欠席 1.0 · 月 4 点清掃罰則 · 月 8 点外出禁止」
5. **MyPointsChartView** (L3) ⭐ — SwiftUI `Canvas` 或 `Path` 手画 12 月折线图 · mock data: [0.5, 1.0, 2.0, 0.5, 1.5, 0, 1.0, 2.5, 0.5, 1.0, 2.0, 4.5] · gridline + threshold line (4 / 8) · 当前月 dot highlight
6. **MySettingsView** (L2) — Toggle list: 点呼リマインダー / 申請結果 / 宅配到着 / 活動リマインダー / 減点警告 · 下段暗色模式 `@AppStorage("isDark")` toggle (用 TToggle)
7. **MyAboutView** (L2) — Tomoshibi wordmark + 版本 `v0.1.0-demo` + AC 署名 block (引用 IOS_DESIGN_LOG §Tomoshibi 命名 AC 叙事 "这个系统守护的是'灯火'——毎晩学生が無事に帰宅し、部屋に灯りが灯ること。")

### 💤 余 6 页 · 简 stub 但有 list view

MyRollcallDetail / MyDiscipline / MyHealth / MyClean / MyPackages / LogoutSheet

- **MyRollcallDetail**: 空 stub
- **MyDiscipline**: EmptyState "処分歴はまだありません"
- **MyHealth**: SEED.health 2 件 list (date / sym / temp / note) · 简单 Card list
- **MyClean**: SEED.cleaning 2 件 list (date / range / status / score)
- **MyPackages**: SEED.packages 4 件 list (重用 Community 的 PackageDetail pattern)
- **LogoutSheet**: 保留已实装（确认 modal + ログアウト/キャンセル 按钮）

## Foundation API

- `Route`: `.my / .myInfo / .myRollcall / .myRollcallDetail / .myPoints / .myPointsChart / .myDiscipline / .myHealth / .myClean / .myPackages / .mySettings / .myAbout`
- `SEED`:
  - `.user: User` (account="00" / name="リュウ イヒ" / nameKana / birth="2006-10-14" / age=19 / gender="女" / dorm="男寮" / room="M101" / category="一般寮生" / email / phone / avatar="リ" / points=4.5 / lateCount=5 / absentCount=2)
  - `.points: [PointRecord]` (7 件 · date/session/kind/val)
  - `.rollcall: [RollcallEntry]` (34 件 · date/session/state/method)
  - `.health: [HealthRecord]` (2 件 · date/sym/temp/note)
  - `.cleaning: [CleaningRecord]` (2 件 · date/range/status/score/rejected/comment)
  - `.packages: [PackageItem]` (4 件)
- `AppStore`: `openSheet(.logout)` / `showToast` / `isDark` (`@AppStorage`)
- `RouterStore.replace(.login)` (ログアウト 后)
- `PageHeader(title:, level: 1/2/3, right:?)` — **MyLanding 用 level 1**（显示 Home icon）
- `Avatar(letter:, size:)` / `Card / Pill / PrimaryButton / GhostButton / Ic.chevR/chevD/x / TToggle` / `EmptyState`
- T tokens · 全套（尤其 T.amberGrad / T.Radius.lg）

## MyPointsChart SwiftUI Canvas 模板

```swift
struct MyPointsChartView: View {
    let data: [Double] = [0.5, 1.0, 2.0, 0.5, 1.5, 0, 1.0, 2.5, 0.5, 1.0, 2.0, 4.5]
    let months = ["5","6","7","8","9","10","11","12","1","2","3","4"]
    var body: some View {
        VStack {
            PageHeader(title: "減点推移", level: 3)
            GeometryReader { geo in
                Canvas { ctx, size in
                    let maxVal: Double = 10
                    let pad: CGFloat = 20
                    let w = size.width - pad*2
                    let h = size.height - pad*2
                    // Threshold lines (4 / 8)
                    for threshold in [4.0, 8.0] {
                        let y = pad + h * (1 - threshold/maxVal)
                        var p = Path()
                        p.move(to: CGPoint(x: pad, y: y))
                        p.addLine(to: CGPoint(x: pad + w, y: y))
                        ctx.stroke(p, with: .color(.orange.opacity(0.3)), style: StrokeStyle(lineWidth: 1, dash: [4]))
                    }
                    // Data line
                    var path = Path()
                    for (i, v) in data.enumerated() {
                        let x = pad + w * CGFloat(i) / CGFloat(data.count - 1)
                        let y = pad + h * CGFloat(1 - v / maxVal)
                        if i == 0 { path.move(to: CGPoint(x: x, y: y)) }
                        else { path.addLine(to: CGPoint(x: x, y: y)) }
                    }
                    ctx.stroke(path, with: .color(Color(red: 0.12, green: 0.42, blue: 0.45)), lineWidth: 2)
                    // Dots
                    for (i, v) in data.enumerated() {
                        let x = pad + w * CGFloat(i) / CGFloat(data.count - 1)
                        let y = pad + h * CGFloat(1 - v / maxVal)
                        let dot = Path(ellipseIn: CGRect(x: x-3, y: y-3, width: 6, height: 6))
                        ctx.fill(dot, with: .color(Color(red: 0.12, green: 0.42, blue: 0.45)))
                    }
                }
                .frame(height: 240)
            }
            Spacer()
        }
    }
}
```

## 产出要求

1. Replace MyPageStubs.swift · 14 struct + LogoutSheet · 800-1200 行
2. 每 struct `#Preview`
3. Build pass `** BUILD SUCCEEDED **`
4. 完成 report

## 不要做

- ❌ 改 Foundation/ · Route.swift · 其他 feature folder
- ❌ git commit
