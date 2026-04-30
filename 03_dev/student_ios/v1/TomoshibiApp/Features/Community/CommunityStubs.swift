// CommunityStubs.swift · Community feature · v2 HTML-fidelity rewrite
// Agent C v2 · 18 struct · 对等 JSX 源 33f0266b__NotificationsPage_PackagesPage_PackageDetailPage.js
// Fidelity 铁律：JSX 原文直抄、数值对照 style、Icon 全 Foundation Ic、颜色 T tokens / colorFromHex()
// v2 HTML 修正：快递 → 宅配 · 宿舍墙 → 寮ウォール · 点歌 → リクエスト曲（C1 中文残留已修）

import SwiftUI

// MARK: - Color hex String helper（SEED.lost[i].color 是 "#3b82f6" 字符串）

private func colorFromHex(_ hex: String) -> Color {
    var h = hex.trimmingCharacters(in: .whitespaces)
    if h.hasPrefix("#") { h.removeFirst() }
    var v: UInt64 = 0
    Scanner(string: h).scanHexInt64(&v)
    return Color(
        red: Double((v >> 16) & 0xff) / 255,
        green: Double((v >> 8) & 0xff) / 255,
        blue: Double(v & 0xff) / 255
    )
}

// MARK: - 共用小工具（private · 不外泄 Feature 边界）

/// 顶部 filter pill row 的单颗
private struct FilterPill: View {
    let text: String
    let active: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            Text(text)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(active ? .white : T.primary)
                .padding(.horizontal, 14)
                .padding(.vertical, 6)
                .background(
                    Capsule().fill(active ? T.primary : T.pill)
                )
        }
        .buttonStyle(.plain)
    }
}

/// 2-tab segmented（待領 / 領済 · リスト / カレンダー）
/// 对等 JSX: `gridTemplateColumns:'1fr 1fr', gap:4, padding:4, background:T.pill, borderRadius:12`
private struct SegTabs<Value: Hashable>: View {
    @Binding var selection: Value
    let items: [(Value, String)]

    var body: some View {
        HStack(spacing: 4) {
            ForEach(items, id: \.0) { item in
                Button {
                    selection = item.0
                } label: {
                    Text(item.1)
                        .font(.system(size: 13, weight: selection == item.0 ? .bold : .medium))
                        .foregroundStyle(selection == item.0 ? T.ink : T.inkSub)
                        .frame(maxWidth: .infinity)
                        .frame(height: 34)
                        .background(
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .fill(selection == item.0 ? T.paper : Color.clear)
                        )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
        )
    }
}

/// 右上 "+" icon 按钮（Lost / Music / Wall 顶部）
/// 对等 JSX: `width:36, height:36, borderRadius:10, background:T.primary`
private struct HeaderPlusButton: View {
    let action: () -> Void
    var body: some View {
        Button(action: action) {
            Ic.plus(18)
                .foregroundStyle(.white)
                .frame(width: 36, height: 36)
                .background(
                    RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.primary)
                )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - §1 NotificationsView · 通知

struct NotificationsView: View {
    @State private var filter: String = "すべて"
    // 对等 JSX: ['すべて','申請','減点','快递','活動'] → v2 修正 快递 → 宅配；补 リクエスト曲 以对齐 SEED
    private let filters = ["すべて", "申請", "減点", "宅配", "活動", "リクエスト曲"]

    private var filtered: [NotificationItem] {
        if filter == "すべて" { return SEED.notifications }
        return SEED.notifications.filter { $0.type == filter }
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "通知", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Filter pill row · padding '4px 16px 24px' · gap 6 · marginBottom 14
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 6) {
                            ForEach(filters, id: \.self) { f in
                                FilterPill(text: f, active: filter == f) { filter = f }
                            }
                        }
                        .padding(.horizontal, 16)
                    }
                    .padding(.top, 4)
                    .padding(.bottom, 14)

                    // Cards · marginBottom:8 per card
                    VStack(spacing: 8) {
                        ForEach(filtered) { n in
                            notifCard(n)
                        }
                        if filtered.isEmpty {
                            EmptyState(icon: "bell", title: "通知はありません")
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func notifCard(_ n: NotificationItem) -> some View {
        // 对等 JSX Card pad={14} · HStack alignItems:'flex-start' gap:10
        Card(padding: 14) {
            HStack(alignment: .top, spacing: 10) {
                if n.unread {
                    Circle().fill(T.primary)
                        .frame(width: 8, height: 8)
                        .padding(.top, 6)
                } else {
                    Color.clear.frame(width: 8, height: 8)
                }
                VStack(alignment: .leading, spacing: 0) {
                    // gap:8 marginBottom:3
                    HStack(spacing: 8) {
                        Pill(text: n.type, tone: toneFor(n.type))
                        Spacer()
                        Text(n.time)
                            .font(.system(size: 11))
                            .foregroundStyle(T.inkMute)
                    }
                    .padding(.bottom, 3)
                    Text(n.title)
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(T.ink)
                        .padding(.bottom, 2)
                    Text(n.body)
                        .font(.system(size: 12))
                        .foregroundStyle(T.inkSub)
                        .lineSpacing(2) // lineHeight 1.5
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    // 对等 JSX: n.type==='減点'?'warn':n.type==='申請'?'ok':'accent'
    private func toneFor(_ type: String) -> Pill.Tone {
        switch type {
        case "減点": return .warn
        case "申請": return .ok
        default: return .accent
        }
    }
}

#Preview {
    NotificationsView()
        .environmentObject(RouterStore(initial: .homeNotifications))
        .environmentObject(AppStore())
}

// MARK: - §2 PackagesView · 宅配（v2 修正：快递 → 宅配）

struct PackagesView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var tab: PkgTab = .wait

    enum PkgTab: Hashable { case wait, done }

    private var waitCount: Int { SEED.packages.filter { $0.status == "待領" }.count }
    private var doneCount: Int { SEED.packages.filter { $0.status == "領済" }.count }
    private var list: [PackageItem] {
        SEED.packages.filter { tab == .wait ? $0.status == "待領" : $0.status == "領済" }
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "宅配", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // SegTabs · marginBottom 14
                    SegTabs(selection: $tab, items: [
                        (.wait, "待領 · \(waitCount)"),
                        (.done, "領済 · \(doneCount)"),
                    ])
                    .padding(.horizontal, 16)
                    .padding(.top, 4)
                    .padding(.bottom, 14)

                    // Cards · marginBottom 10
                    VStack(spacing: 10) {
                        ForEach(list) { p in
                            pkgCard(p)
                        }
                        if list.isEmpty {
                            EmptyState(icon: "shippingbox", title: "なし")
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func pkgCard(_ p: PackageItem) -> some View {
        Button { router.go(.homePackageDetail(id: p.id)) } label: {
            Card(padding: 14) {
                // HStack alignItems:'center' gap:12
                HStack(alignment: .center, spacing: 12) {
                    // JSX 用 emoji 📦 fontSize:28 · 保留（Fidelity：不自作主张换 SF Symbol）
                    Text("📦")
                        .font(.system(size: 28))
                    VStack(alignment: .leading, spacing: 2) {
                        Text(p.from)
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                        // date + tracking · fontFamily:T.mono fontSize:11 color:T.inkMute
                        Text("\(p.date)\(p.tracking.map { " · \($0)" } ?? "")")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundStyle(T.inkMute)
                    }
                    Spacer()
                    // 待領 only：受取 button · height 36 padding '0 16' fontSize 13
                    if p.status == "待領" {
                        Text("受取")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 16)
                            .frame(height: 36)
                            .background(
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .fill(T.btnGrad)
                            )
                    }
                }
            }
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    PackagesView()
        .environmentObject(RouterStore(initial: .homePackages))
        .environmentObject(AppStore())
}

// MARK: - §3 PackageDetailView · 宅配詳細

struct PackageDetailView: View {
    let id: Int
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    private var item: PackageItem? { SEED.packages.first(where: { $0.id == id }) }

    // JSX 写死 4 行 meta · 用 package item 填充可用字段
    private func rows(_ p: PackageItem) -> [(String, String)] {
        [
            ("配送業者", p.from),
            ("到着時刻", "\(p.date) 14:22"),
            ("追跡番号", p.tracking ?? "―"),
            ("保管場所", "寮務室前棚 A-3"),
        ]
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "宅配詳細", level: 2)
            ScrollView {
                VStack(spacing: 0) {
                    if let p = item {
                        // padding '4px 20px 24px'
                        Card(padding: 20) {
                            VStack(spacing: 0) {
                                // fontSize 56 textAlign center marginBottom 14
                                Text("📦")
                                    .font(.system(size: 56))
                                    .frame(maxWidth: .infinity)
                                    .padding(.bottom, 14)
                                // grid gap 10
                                VStack(spacing: 10) {
                                    ForEach(rows(p), id: \.0) { k, v in
                                        VStack(spacing: 0) {
                                            // borderTop 0.5px T.hair
                                            Rectangle().fill(T.hair).frame(height: 0.5)
                                            HStack {
                                                Text(k)
                                                    .font(.system(size: 13))
                                                    .foregroundStyle(T.inkSub)
                                                Spacer()
                                                Text(v)
                                                    .font(.system(size: 13, weight: .semibold))
                                                    .foregroundStyle(T.ink)
                                            }
                                            .padding(.vertical, 8)
                                        }
                                    }
                                }
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 4)

                        // marginTop 20
                        PrimaryButton(title: "受取確認") {
                            app.showToast("受取完了しました")
                            router.back()
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 20)
                    } else {
                        EmptyState(icon: "shippingbox", title: "宅配が見つかりません")
                    }
                    Spacer().frame(height: 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    PackageDetailView(id: 1)
        .environmentObject(RouterStore(initial: .homePackageDetail(id: 1)))
        .environmentObject(AppStore())
}

// MARK: - §4 LostView · 遺失物

struct LostView: View {
    @EnvironmentObject var router: RouterStore
    @State private var search: String = ""

    var body: some View {
        VStack(spacing: 0) {
            // 遺失物は寮監のみ投稿可能 → 学生側は右上 + ボタンなし（閲覧専用）
            PageHeader(title: "遺失物", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 案内: 寮監に届ける旨
                    HStack(alignment: .top, spacing: 6) {
                        Image(systemName: "info.circle.fill")
                            .font(.system(size: 13))
                            .foregroundStyle(T.primary)
                        Text("拾得物・落とし物は必ず寮監に届けてください。一覧は寮監が管理しています。")
                            .font(.system(size: 12))
                            .foregroundStyle(T.primaryDk)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(T.primary.opacity(0.06))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.primary.opacity(0.15), lineWidth: 1)
                    )
                    .padding(.horizontal, 16)
                    .padding(.top, 4)
                    .padding(.bottom, 10)

                    // 検索 box · padding '10 14' borderRadius 12 background T.pearl
                    HStack(spacing: 10) {
                        Ic.search(18).foregroundStyle(T.inkMute)
                        TextField("検索...", text: $search)
                            .font(.system(size: 14))
                            .foregroundStyle(T.ink)
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pearl)
                    )
                    .padding(.horizontal, 16)
                    .padding(.bottom, 14)

                    // 2-col grid · gap 10
                    let cols = [
                        GridItem(.flexible(), spacing: 10),
                        GridItem(.flexible(), spacing: 10),
                    ]
                    LazyVGrid(columns: cols, spacing: 10) {
                        ForEach(SEED.lost) { l in
                            lostCell(l)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func lostCell(_ l: LostItem) -> some View {
        // 对等 JSX: aspectRatio 1 · gradient `${color}aa → ${color}44`
        Button { router.go(.homeLostDetail(id: l.id)) } label: {
            VStack(alignment: .leading, spacing: 0) {
                ZStack {
                    LinearGradient(
                        colors: [
                            colorFromHex(l.color).opacity(2.0/3.0), // aa ≈ 0.67
                            colorFromHex(l.color).opacity(0.27),    // 44 ≈ 0.27
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    // 32pt emoji + white textShadow
                    Text("🎒")
                        .font(.system(size: 32))
                        .foregroundStyle(.white)
                        .shadow(color: .black.opacity(0.3), radius: 6, x: 0, y: 2)
                }
                .aspectRatio(1, contentMode: .fit)

                VStack(alignment: .leading, spacing: 3) {
                    Text(l.title)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(T.ink)
                        .lineLimit(1)
                    Text("\(l.place) · \(l.date)")
                        .font(.system(size: 10.5))
                        .foregroundStyle(T.inkMute)
                }
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .background(T.paper)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(T.hair, lineWidth: 0.5)
            )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    LostView()
        .environmentObject(RouterStore(initial: .homeLost))
        .environmentObject(AppStore())
}

// MARK: - §5 LostNewView · 遺失物を投稿

struct LostNewView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var place: String = ""
    @State private var feature: String = ""

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "遺失物を投稿", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 画像 field · required
                    Field(label: "画像", required: true) {
                        VStack(spacing: 6) {
                            Ic.camera(28).foregroundStyle(T.primary)
                            Text("写真を追加")
                                .font(.system(size: 13))
                                .foregroundStyle(T.inkSub)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(24)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(style: StrokeStyle(lineWidth: 1.5, dash: [5, 3]))
                                .foregroundStyle(T.inkFaint)
                        )
                    }
                    .padding(.bottom, 18)

                    Field(label: "拾得場所", required: true) {
                        TField(text: $place, placeholder: "ロビー / 食堂 / ...")
                    }
                    .padding(.bottom, 18)

                    Field(label: "特徴", required: true) {
                        TArea(text: $feature, placeholder: "色・大きさ・目印", rows: 3)
                    }
                    .padding(.bottom, 18)

                    // 拾得日時 · 固定文字（JSX 原样）
                    Field(label: "拾得日時") {
                        HStack {
                            Text("2026-04-22 15:00")
                                .font(.system(size: 15))
                                .foregroundStyle(T.ink)
                            Spacer()
                        }
                        .padding(.horizontal, 14)
                        .frame(height: 48)
                        .background(T.pearl)
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(T.hair, lineWidth: 1)
                        )
                    }
                    .padding(.bottom, 18)

                    PrimaryButton(title: "投稿する") {
                        app.showToast("投稿しました")
                        Task {
                            try? await Task.sleep(nanoseconds: 500_000_000)
                            await MainActor.run { router.go(.homeLost) }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    LostNewView()
        .environmentObject(RouterStore(initial: .homeLostNew))
        .environmentObject(AppStore())
}

// MARK: - §6 LostDetailView · 遺失物詳細

struct LostDetailView: View {
    let id: Int
    @EnvironmentObject var app: AppStore

    private var item: LostItem? { SEED.lost.first(where: { $0.id == id }) }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "遺失物詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    if let l = item {
                        // aspectRatio 1.3 · gradient · fontSize 80 emoji
                        ZStack {
                            LinearGradient(
                                colors: [
                                    colorFromHex(l.color).opacity(2.0/3.0),
                                    colorFromHex(l.color).opacity(0.27),
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                            Text("🎒")
                                .font(.system(size: 80))
                                .foregroundStyle(.white)
                        }
                        .aspectRatio(1.3, contentMode: .fit)
                        .frame(maxWidth: .infinity)

                        // padding 20
                        VStack(alignment: .leading, spacing: 0) {
                            Text(l.title)
                                .font(.system(size: 22, weight: .heavy))
                                .foregroundStyle(T.ink)
                                .padding(.bottom, 6)
                            HStack(spacing: 6) {
                                Pill(text: l.place, tone: .accent)
                                Pill(text: l.date, tone: .neutral)
                            }
                            .padding(.bottom, 14)
                            Text("ロビーのソファ付近で拾いました。黒色のコンパクト傘、持ち手に小さな白い傷があります。心当たりのある方はご連絡ください。")
                                .font(.system(size: 14))
                                .foregroundStyle(T.inkSub)
                                .lineSpacing(4) // lineHeight 1.7
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.bottom, 20)
                            PrimaryButton(title: "私のものです") {
                                app.showToast("投稿者に通知しました")
                            }
                        }
                        .padding(20)
                    } else {
                        EmptyState(icon: "magnifyingglass", title: "見つかりません")
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    LostDetailView(id: 1)
        .environmentObject(RouterStore(initial: .homeLostDetail(id: 1)))
        .environmentObject(AppStore())
}

// MARK: - §7 MusicView · リクエスト曲（v2 修正：点歌 → リクエスト曲）

struct MusicView: View {
    @EnvironmentObject var router: RouterStore

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(
                title: "リクエスト曲",
                level: 2,
                right: AnyView(HeaderPlusButton { router.go(.homeMusicNew) })
            )
            ScrollView {
                // marginBottom 8 per card
                VStack(spacing: 8) {
                    ForEach(Array(SEED.songs.enumerated()), id: \.element.id) { idx, s in
                        songCard(idx: idx, s: s)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func songCard(idx: Int, s: SongItem) -> some View {
        Button { router.go(.homeMusicDetail(id: s.id)) } label: {
            Card(padding: 14) {
                // HStack alignItems center gap 12
                HStack(alignment: .center, spacing: 12) {
                    // rank · width 22 · fontSize 16 bold mono · top3 → primary, else inkMute
                    Text("\(idx + 1)")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundStyle(idx < 3 ? T.primary : T.inkMute)
                        .frame(width: 22, alignment: .center)
                    // 44x44 gradient album
                    ZStack {
                        LinearGradient(
                            colors: [T.accentSoft, T.accent],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        Ic.music(22).foregroundStyle(.white)
                    }
                    .frame(width: 44, height: 44)
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    // title + meta · flex 1
                    VStack(alignment: .leading, spacing: 0) {
                        Text(s.title)
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                            .lineLimit(1)
                            .truncationMode(.tail)
                        Text("\(s.artist) · \(s.by)")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                            .lineLimit(1)
                    }
                    Spacer()
                    // votes · VStack gap 3
                    VStack(spacing: 3) {
                        HStack(spacing: 3) {
                            Ic.up(12).foregroundStyle(T.ok)
                            Text("\(s.up)")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundStyle(T.ok)
                        }
                        HStack(spacing: 3) {
                            Ic.down(12).foregroundStyle(T.inkMute)
                            Text("\(s.down)")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundStyle(T.inkMute)
                        }
                    }
                }
            }
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    MusicView()
        .environmentObject(RouterStore(initial: .homeMusic))
        .environmentObject(AppStore())
}

// MARK: - §8 MusicNewView · 曲を投稿

struct MusicNewView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var url: String = ""
    @State private var title: String = ""
    @State private var artist: String = ""
    @State private var reason: String = ""

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "曲を投稿", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Field(label: "Apple Music URL", hint: "曲情報を自動取得します") {
                        TField(text: $url, placeholder: "https://music.apple.com/...")
                    }
                    .padding(.bottom, 18)

                    Field(label: "曲名", required: true) {
                        TField(text: $title)
                    }
                    .padding(.bottom, 18)

                    Field(label: "アーティスト", required: true) {
                        TField(text: $artist)
                    }
                    .padding(.bottom, 18)

                    Field(label: "投稿理由") {
                        TArea(text: $reason, placeholder: "この曲を寮で流したい理由", rows: 3)
                    }
                    .padding(.bottom, 18)

                    PrimaryButton(title: "投稿する") {
                        app.showToast("投稿しました")
                        Task {
                            try? await Task.sleep(nanoseconds: 500_000_000)
                            await MainActor.run { router.go(.homeMusic) }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    MusicNewView()
        .environmentObject(RouterStore(initial: .homeMusicNew))
        .environmentObject(AppStore())
}

// MARK: - §9 MusicDetailView · 曲詳細

struct MusicDetailView: View {
    let id: Int
    @EnvironmentObject var app: AppStore
    @State private var voted: String? = nil  // "up" / "down" / nil

    // JSX 原文 hard-coded Lilac · 我们用 id 找回 SEED song，fallback Lilac
    private var song: SongItem { SEED.songs.first(where: { $0.id == id }) ?? SEED.songs[0] }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "曲詳細", level: 2)
            ScrollView {
                VStack(spacing: 0) {
                    // 160x160 rounded album · gradient · centered
                    ZStack {
                        LinearGradient(
                            colors: [T.accentSoft, T.accent],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        // JSX 写 transform:scale(3.4) on music icon 24 ≈ 82
                        Ic.music(82).foregroundStyle(.white)
                    }
                    .frame(width: 160, height: 160)
                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                    .shadow(color: T.primary.opacity(0.25), radius: 20, x: 0, y: 12)
                    .padding(.bottom, 20)

                    // title textAlign center fontSize 22 heavy
                    Text(song.title)
                        .font(.system(size: 22, weight: .heavy))
                        .foregroundStyle(T.ink)
                        .padding(.bottom, 6)

                    Text("\(song.artist) · 投稿 \(song.by)")
                        .font(.system(size: 14))
                        .foregroundStyle(T.inkSub)
                        .padding(.bottom, 24)

                    // reason card · marginBottom 14
                    Card(padding: 16) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("投稿理由")
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkSub)
                            Text("朝の支度時間に聴きたい、明るい気持ちになれる曲です。")
                                .font(.system(size: 14))
                                .foregroundStyle(T.ink)
                                .lineSpacing(3)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                    .padding(.bottom, 14)

                    // voting buttons · gap 10 · height 52 borderRadius 16
                    HStack(spacing: 10) {
                        voteButton(kind: "up", label: "賛成", iconUp: true)
                        voteButton(kind: "down", label: "反対", iconUp: false)
                    }
                    .padding(.bottom, 18)

                    // report 底部 link
                    Button {
                        app.showToast("報告を送信しました")
                    } label: {
                        HStack(spacing: 4) {
                            Ic.flag(14)
                            Text("報告する")
                                .font(.system(size: 12))
                        }
                        .foregroundStyle(T.inkMute)
                        .frame(maxWidth: .infinity)
                        .padding(10)
                    }
                    .buttonStyle(.plain)
                }
                .padding(20)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    @ViewBuilder
    private func voteButton(kind: String, label: String, iconUp: Bool) -> some View {
        let selected = voted == kind
        let isDanger = kind == "down"
        let borderColor: Color = selected ? (isDanger ? T.danger : T.ok) : T.hair
        let bgColor: Color = selected ? (isDanger ? T.dangerBg : T.okBg) : T.paper
        let fgColor: Color = selected ? (isDanger ? T.danger : T.okDeep) : T.ink
        Button {
            voted = kind
            app.showToast("投票しました")
        } label: {
            HStack(spacing: 8) {
                if iconUp { Ic.up(16) } else { Ic.down(16) }
                Text(label)
                    .font(.system(size: 14, weight: .bold))
            }
            .foregroundStyle(fgColor)
            .frame(maxWidth: .infinity)
            .frame(height: 52)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous).fill(bgColor)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(borderColor, lineWidth: 1.5)
            )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    MusicDetailView(id: 1)
        .environmentObject(RouterStore(initial: .homeMusicDetail(id: 1)))
        .environmentObject(AppStore())
}

// MARK: - §10 WallView · 寮ウォール（v2 修正：宿舍墙 → 寮ウォール）

struct WallView: View {
    @EnvironmentObject var router: RouterStore

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(
                title: "寮ウォール",
                level: 2,
                right: AnyView(HeaderPlusButton { router.go(.homeWallNew) })
            )
            ScrollView {
                // marginBottom 10 per card
                VStack(spacing: 10) {
                    ForEach(SEED.wall) { p in
                        wallCard(p)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func wallCard(_ p: WallPost) -> some View {
        Button { router.go(.homeWallDetail(id: p.id)) } label: {
            Card(padding: 14) {
                VStack(alignment: .leading, spacing: 0) {
                    // author row · marginBottom 8 · gap 10
                    HStack(spacing: 10) {
                        Avatar(letter: String(p.author.prefix(1)), size: 32)
                        VStack(alignment: .leading, spacing: 0) {
                            Text(p.author)
                                .font(.system(size: 13, weight: .bold))
                                .foregroundStyle(T.ink)
                            Text(p.time)
                                .font(.system(size: 11))
                                .foregroundStyle(T.inkMute)
                        }
                        Spacer()
                    }
                    .padding(.bottom, 8)

                    // text · marginBottom 10 · lineHeight 1.6
                    Text(p.text)
                        .font(.system(size: 14))
                        .foregroundStyle(T.ink)
                        .lineSpacing(3)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.bottom, 10)

                    // icon row · gap 18 · color inkSub · last flag marginLeft auto
                    HStack(spacing: 18) {
                        HStack(spacing: 4) {
                            Ic.heart(14)
                            Text("\(p.likes)")
                                .font(.system(size: 12))
                        }
                        HStack(spacing: 4) {
                            Ic.comment(14)
                            Text("\(p.comments)")
                                .font(.system(size: 12))
                        }
                        Spacer()
                        Ic.flag(12)
                    }
                    .foregroundStyle(T.inkSub)
                }
            }
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    WallView()
        .environmentObject(RouterStore(initial: .homeWall))
        .environmentObject(AppStore())
}

// MARK: - §11 WallNewView · 投稿する

struct WallNewView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var content: String = ""

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "投稿する", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Field(label: "内容", required: true) {
                        TArea(text: $content, placeholder: "寮舍の皆に伝えたいこと", rows: 6)
                    }
                    .padding(.bottom, 18)

                    Field(label: "画像（任意）") {
                        VStack(spacing: 6) {
                            Ic.camera(24).foregroundStyle(T.primary)
                            Text("画像を追加")
                                .font(.system(size: 13))
                                .foregroundStyle(T.inkSub)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(20)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(style: StrokeStyle(lineWidth: 1.5, dash: [5, 3]))
                                .foregroundStyle(T.inkFaint)
                        )
                    }
                    .padding(.bottom, 18)

                    PrimaryButton(title: "投稿") {
                        app.showToast("投稿しました")
                        Task {
                            try? await Task.sleep(nanoseconds: 500_000_000)
                            await MainActor.run { router.go(.homeWall) }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    WallNewView()
        .environmentObject(RouterStore(initial: .homeWallNew))
        .environmentObject(AppStore())
}

// MARK: - §12 WallDetailView · 投稿詳細

struct WallDetailView: View {
    let id: Int
    @State private var comment: String = ""

    private var post: WallPost? { SEED.wall.first(where: { $0.id == id }) }

    // JSX hard-coded 2 comments（fidelity）
    private let comments: [(a: String, t: String, w: String)] = [
        (a: "12号", t: "お疲れ様！", w: "3時間前"),
        (a: "05号", t: "飾り付け可愛かった✨", w: "2時間前"),
    ]

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "投稿詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 主 Card · marginBottom 14
                    Card(padding: 16) {
                        VStack(alignment: .leading, spacing: 0) {
                            HStack(spacing: 10) {
                                Avatar(letter: post.map { String($0.author.prefix(1)) } ?? "0", size: 36)
                                VStack(alignment: .leading, spacing: 0) {
                                    Text(post?.author ?? "00号")
                                        .font(.system(size: 14, weight: .bold))
                                        .foregroundStyle(T.ink)
                                    Text(post?.time ?? "5時間前")
                                        .font(.system(size: 11))
                                        .foregroundStyle(T.inkMute)
                                }
                                Spacer()
                            }
                            .padding(.bottom, 10)

                            Text(post?.text ?? "新歓準備お疲れ様でした！みんなで準備した飾り付けも綺麗に仕上がったね。明日の本番がんばろう。")
                                .font(.system(size: 15))
                                .foregroundStyle(T.ink)
                                .lineSpacing(4)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.bottom, 14)

                            // borderTop 0.5 hair · paddingTop 10 · gap 18
                            Rectangle().fill(T.hair).frame(height: 0.5)
                                .padding(.bottom, 10)
                            HStack(spacing: 18) {
                                HStack(spacing: 5) {
                                    Ic.heart(16)
                                    Text("\(post?.likes ?? 15)")
                                        .font(.system(size: 13))
                                }
                                HStack(spacing: 5) {
                                    Ic.comment(16)
                                    Text("\(post?.comments ?? 2)")
                                        .font(.system(size: 13))
                                }
                            }
                            .foregroundStyle(T.inkSub)
                        }
                    }
                    .padding(.bottom, 14)

                    // section label コメント
                    Text("コメント")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(T.inkSub)
                        .kerning(1.2)
                        .textCase(.uppercase)
                        .padding(.horizontal, 4)
                        .padding(.bottom, 8)

                    // comments
                    VStack(spacing: 8) {
                        ForEach(Array(comments.enumerated()), id: \.offset) { _, c in
                            Card(padding: 12) {
                                VStack(alignment: .leading, spacing: 0) {
                                    HStack(spacing: 8) {
                                        Avatar(letter: String(c.a.prefix(1)), size: 24)
                                        Text(c.a)
                                            .font(.system(size: 12, weight: .bold))
                                            .foregroundStyle(T.ink)
                                        Spacer()
                                        Text(c.w)
                                            .font(.system(size: 10))
                                            .foregroundStyle(T.inkMute)
                                    }
                                    .padding(.bottom, 4)
                                    Text(c.t)
                                        .font(.system(size: 13))
                                        .foregroundStyle(T.ink)
                                        .padding(.leading, 32)
                                }
                            }
                        }
                    }
                    .padding(.bottom, 14)

                    // comment input row · marginTop 14 · gap 8
                    HStack(spacing: 8) {
                        TField(text: $comment, placeholder: "コメントを書く...")
                        Button {} label: {
                            Text("→")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundStyle(.white)
                                .frame(width: 48, height: 48)
                                .background(
                                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                                        .fill(T.primary)
                                )
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    WallDetailView(id: 3)
        .environmentObject(RouterStore(initial: .homeWallDetail(id: 3)))
        .environmentObject(AppStore())
}

// MARK: - §13 EventsView · 活動（list / calendar segmented）

struct EventsView: View {
    @EnvironmentObject var router: RouterStore
    @State private var selectedMonth: Int = 4      // 4 月 / 5 月 トグル
    @State private var selectedDay: Int = 23       // 初期選択日（demo: 今日 2026-04-23）

    private let todayMonth = 4
    private let todayDay = 23
    private let year = 2026

    // 2026-04-01 = 水曜日（weekday index 3 · 0=日）
    // 2026-05-01 = 金曜日（weekday index 5）
    private var firstWeekdayOfMonth: Int { selectedMonth == 4 ? 3 : 5 }
    private var daysInMonth: Int { selectedMonth == 4 ? 30 : 31 }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "カレンダー", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    calendarCard
                    selectedDaySection
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    // MARK: — 上半：カレンダー

    private var calendarCard: some View {
        Card(padding: 16) {
            VStack(alignment: .leading, spacing: 14) {
                // 月切替 header
                HStack {
                    Button { selectedMonth = max(4, selectedMonth - 1) } label: {
                        Ic.chevR(16).foregroundStyle(selectedMonth > 4 ? T.ink : T.inkMute)
                            .rotationEffect(.degrees(180))
                            .frame(width: 32, height: 32)
                            .contentShape(Rectangle())
                    }
                    .disabled(selectedMonth <= 4)
                    Spacer()
                    Text(verbatim: "\(year) 年 \(selectedMonth) 月")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(T.ink)
                    Spacer()
                    Button { selectedMonth = min(5, selectedMonth + 1) } label: {
                        Ic.chevR(16).foregroundStyle(selectedMonth < 5 ? T.ink : T.inkMute)
                            .frame(width: 32, height: 32)
                            .contentShape(Rectangle())
                    }
                    .disabled(selectedMonth >= 5)
                }

                let cols = Array(repeating: GridItem(.flexible(), spacing: 4), count: 7)
                LazyVGrid(columns: cols, spacing: 4) {
                    // 曜日ラベル
                    ForEach(["日", "月", "火", "水", "木", "金", "土"], id: \.self) { d in
                        Text(d)
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundStyle(T.inkMute)
                            .padding(.vertical, 6)
                    }
                    // 前の月の空白
                    ForEach(0..<firstWeekdayOfMonth, id: \.self) { _ in
                        Color.clear.aspectRatio(1, contentMode: .fit)
                    }
                    // 当月の日
                    ForEach(1...daysInMonth, id: \.self) { day in
                        dayCell(day)
                    }
                }
            }
        }
    }

    private func dayCell(_ day: Int) -> some View {
        let hasEvent = !eventsForDay(day).isEmpty
        let isToday = selectedMonth == todayMonth && day == todayDay
        let isSelected = day == selectedDay
        let bg: Color = isSelected ? T.primary : (isToday ? T.primary.opacity(0.12) : Color.clear)
        let fg: Color = isSelected ? .white : T.ink
        return Button {
            selectedDay = day
        } label: {
            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(bg)
                    .overlay {
                        if isToday && !isSelected {
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .stroke(T.primary, lineWidth: 1.5)
                        }
                    }
                Text("\(day)")
                    .font(.system(size: 13, weight: (isSelected || isToday) ? .heavy : .medium, design: .monospaced))
                    .foregroundStyle(fg)
                // 有行事时小圆点 · 选中时 hide（已高亮不需要再叠圆点）
                if hasEvent && !isSelected {
                    Circle()
                        .fill(T.accent)
                        .frame(width: 4, height: 4)
                        .offset(y: -3)
                }
            }
            .aspectRatio(1, contentMode: .fit)
            .contentShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    // MARK: — 下半：選択日の行事

    private var selectedDaySection: some View {
        let evs = eventsForDay(selectedDay)
        let weekdayJP = ["日", "月", "火", "水", "木", "金", "土"]
        let weekday = (firstWeekdayOfMonth + selectedDay - 1) % 7

        return VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Text("\(selectedMonth) 月 \(selectedDay) 日")
                    .font(.system(size: 18, weight: .heavy))
                    .foregroundStyle(T.ink)
                Text("（\(weekdayJP[weekday])）")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                Spacer()
                if evs.count > 0 {
                    Text("\(evs.count) 件")
                        .font(.system(size: 11, weight: .bold))
                        .padding(.horizontal, 8).padding(.vertical, 3)
                        .foregroundStyle(T.primary)
                        .background(Capsule().fill(T.primary.opacity(0.1)))
                }
            }
            .padding(.top, 4)

            if evs.isEmpty {
                Card(padding: 24) {
                    VStack(spacing: 8) {
                        Ic.calendar(36).foregroundStyle(T.inkMute)
                        Text("予定なし")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundStyle(T.inkSub)
                        Text("この日の活動はありません")
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkMute)
                    }
                    .frame(maxWidth: .infinity)
                }
            } else {
                ForEach(evs, id: \.id) { e in
                    let idx = SEED.events.firstIndex(where: { $0.id == e.id }) ?? 0
                    Button { router.go(.homeEventDetail(id: idx)) } label: {
                        eventRow(e)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private func eventRow(_ e: EventItem) -> some View {
        Card(padding: 14) {
            HStack(alignment: .center, spacing: 12) {
                VStack(spacing: 2) {
                    Text(e.time)
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundStyle(T.primary)
                }
                .frame(width: 56)
                Rectangle().fill(T.hair).frame(width: 1, height: 38)
                VStack(alignment: .leading, spacing: 3) {
                    Text(e.title)
                        .font(.system(size: 14.5, weight: .bold))
                        .foregroundStyle(T.ink)
                    HStack(spacing: 4) {
                        Text("📍")
                            .font(.system(size: 10))
                        Text(e.place)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                    }
                }
                Spacer()
                Ic.chevR(14).foregroundStyle(T.inkMute)
            }
        }
    }

    // MARK: — 辅助

    private func eventsForDay(_ day: Int) -> [EventItem] {
        let dateStr = String(format: "%d-%02d-%02d", year, selectedMonth, day)
        return SEED.events.filter { $0.date == dateStr }
    }
}

#Preview {
    EventsView()
        .environmentObject(RouterStore(initial: .homeEvents))
        .environmentObject(AppStore())
}

// MARK: - §14 EventDetailView · 活動詳細

struct EventDetailView: View {
    let id: Int
    @EnvironmentObject var app: AppStore

    // id 是 list index（Events 用 idx 作 id）· fallback 0
    private var event: EventItem {
        (id >= 0 && id < SEED.events.count) ? SEED.events[id] : SEED.events[0]
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "活動詳細", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // hero date card · gradient #e8f4f6 → #a8dce2 · borderRadius 20 · padding 28 0
                    VStack(spacing: 0) {
                        Text("2026 · \(monthPart(event.date))")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .kerning(2.4)
                            .foregroundStyle(T.primaryDk.opacity(0.8))
                        Text(dayPart(event.date))
                            .font(.system(size: 54, weight: .heavy, design: .monospaced))
                            .foregroundStyle(T.primaryDk)
                            .padding(.vertical, 6)
                        Text("\(weekdayFor(event.date)) · \(event.time)")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(T.primaryDk)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 28)
                    .background(
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .fill(LinearGradient(
                                colors: [Color(hex: 0xe8f4f6), Color(hex: 0xa8dce2)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                    )
                    .padding(.bottom, 20)

                    // title fontSize 22 heavy · marginBottom 8
                    Text(event.title)
                        .font(.system(size: 22, weight: .heavy))
                        .foregroundStyle(T.ink)
                        .padding(.bottom, 8)

                    // place row · fontSize 13 · marginBottom 18
                    Text("📍 \(event.place)")
                        .font(.system(size: 13))
                        .foregroundStyle(T.inkSub)
                        .padding(.bottom, 18)

                    // desc card · JSX 加了固定后缀
                    Card(padding: 16) {
                        Text("\(event.desc)。新入生の自己紹介、在学生との交流タイム、軽食とドリンクをご用意します。")
                            .font(.system(size: 14))
                            .foregroundStyle(T.ink)
                            .lineSpacing(4)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(.bottom, 18)

                    PrimaryButton(title: "iPhone カレンダーに追加") {
                        app.showToast("カレンダーに追加しました")
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func monthPart(_ s: String) -> String {
        let parts = s.split(separator: "-")
        return parts.count >= 2 ? String(parts[1]) : ""
    }
    private func dayPart(_ s: String) -> String {
        let parts = s.split(separator: "-")
        return parts.count >= 3 ? String(parts[2]) : ""
    }

    private func weekdayFor(_ dateString: String) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "yyyy-MM-dd"
        fmt.locale = Locale(identifier: "ja_JP")
        guard let d = fmt.date(from: dateString) else { return "木曜日" }
        let out = DateFormatter()
        out.locale = Locale(identifier: "ja_JP")
        out.dateFormat = "EEEE"
        return out.string(from: d)
    }
}

#Preview {
    EventDetailView(id: 0)
        .environmentObject(RouterStore(initial: .homeEventDetail(id: 0)))
        .environmentObject(AppStore())
}

// MARK: - §15 BusView · バス時刻表

struct BusView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "バス時刻表", level: 2)
            ScrollView {
                VStack(spacing: 0) {
                    // グローバル通知 banner
                    if SEED.busNotice.active {
                        HStack(alignment: .top, spacing: 4) {
                            (
                                Text("⚠ ")
                                + Text("臨時公告").fontWeight(.bold)
                                + Text(" · \(SEED.busNotice.text)")
                            )
                            .font(.system(size: 12.5))
                            .foregroundStyle(T.warnDeep)
                            .lineSpacing(3)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 12)
                        .background(T.warnBg)
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(T.warn.opacity(0.25), lineWidth: 1)
                        )
                        .padding(.bottom, 16)
                    }

                    // 日別グループ section list
                    VStack(spacing: 14) {
                        ForEach(SEED.busSchedule) { sched in
                            daySection(sched)
                        }
                    }

                    // 備考：通常日バス運行なしの旨
                    Text("※ 上記以外の日はスクールバスの運行はありません。通学生は公共交通機関を利用してください。")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                        .lineSpacing(3)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.top, 18)
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    // MARK: 日別セクション

    private func daySection(_ sched: BusDaySchedule) -> some View {
        VStack(spacing: 0) {
            // header: 月/日 (曜日) + label
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text(monthDayLabel(sched.date))
                    .font(.system(size: 17, weight: .heavy, design: .monospaced))
                    .foregroundStyle(T.primaryDk)
                Text("（\(sched.weekday)）")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                Spacer(minLength: 6)
                Text(sched.label)
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkSub)
                    .lineLimit(1)
                    .truncationMode(.tail)
            }
            .padding(.horizontal, 14).padding(.vertical, 12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(T.primary.opacity(0.05))

            // optional notice
            if let notice = sched.notice {
                HStack(spacing: 4) {
                    Text("ℹ")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(T.warnDeep)
                    Text(notice)
                        .font(.system(size: 11.5))
                        .foregroundStyle(T.warnDeep)
                        .lineSpacing(2)
                }
                .padding(.horizontal, 14).padding(.vertical, 8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(T.warnBg.opacity(0.5))
            }

            // Lines list
            VStack(spacing: 0) {
                ForEach(Array(sched.lines.enumerated()), id: \.offset) { i, line in
                    busRow(line)
                    if i < sched.lines.count - 1 {
                        Rectangle().fill(T.hair).frame(height: 0.5)
                            .padding(.leading, 58)
                    }
                }
            }
            .background(T.paper)
        }
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(T.hair, lineWidth: 0.5)
        )
        .shadow(color: T.ink.opacity(0.05), radius: 10, x: 0, y: 3)
    }

    private func busRow(_ b: BusLine) -> some View {
        HStack(spacing: 12) {
            ZStack {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(b.next ? T.primary : T.primary.opacity(0.08))
                    .frame(width: 36, height: 36)
                Ic.bus(18)
                    .foregroundStyle(b.next ? .white : T.primary)
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(b.time)
                    .font(.system(size: 17, weight: .bold, design: .monospaced))
                    .foregroundStyle(T.ink)
                Text(b.route)
                    .font(.system(size: 11.5))
                    .foregroundStyle(T.inkSub)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 3) {
                if b.next {
                    Pill(text: "次便", tone: .accent)
                }
                Text(b.seats)
                    .font(.system(size: 10.5))
                    .foregroundStyle(T.inkMute)
            }
        }
        .padding(.horizontal, 14).padding(.vertical, 11)
    }

    private func monthDayLabel(_ s: String) -> String {
        // "2026-04-29" → "4/29"
        let p = s.split(separator: "-")
        guard p.count >= 3, let m = Int(p[1]), let d = Int(p[2]) else { return s }
        return "\(m)/\(d)"
    }
}

#Preview {
    BusView()
        .environmentObject(RouterStore(initial: .homeBus))
        .environmentObject(AppStore())
}

// MARK: - §16 SuggestView · 匿名建議

struct SuggestView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var cat: String = ""
    @State private var body_: String = ""

    private let cats = ["食堂", "設備", "運営", "交流", "その他"]

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(
                title: "匿名建議",
                level: 2,
                right: AnyView(
                    Button { router.go(.homeSuggestFeed) } label: {
                        Text("回応一覧")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundStyle(T.primary)
                    }
                    .buttonStyle(.plain)
                )
            )
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // privacy banner · padding '12 14' primary/0a bg primary/22 border
                    HStack(alignment: .top, spacing: 0) {
                        Text("🔒 投稿は完全匿名です。あなたの名前・番号は送信されません。")
                            .font(.system(size: 12))
                            .foregroundStyle(T.primaryDk)
                            .lineSpacing(3)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .background(T.primary.opacity(0.04))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(T.primary.opacity(0.13), lineWidth: 1)
                    )
                    .padding(.bottom, 18)

                    // カテゴリ radio row
                    Field(label: "カテゴリ", required: true) {
                        VStack(alignment: .leading, spacing: 8) {
                            // FlowLayout via HStack wrap — 5 item 应该 fit 一排
                            HStack(spacing: 8) {
                                ForEach(cats.prefix(3), id: \.self) { c in
                                    catChip(c)
                                }
                            }
                            HStack(spacing: 8) {
                                ForEach(cats.suffix(2), id: \.self) { c in
                                    catChip(c)
                                }
                            }
                        }
                    }
                    .padding(.bottom, 18)

                    Field(label: "内容", required: true) {
                        TArea(text: $body_, placeholder: "寮運営へのご意見・ご要望", rows: 6)
                    }
                    .padding(.bottom, 18)

                    PrimaryButton(title: "送信する", enabled: !cat.isEmpty && !body_.isEmpty) {
                        app.showToast("送信しました（匿名）")
                        Task {
                            try? await Task.sleep(nanoseconds: 500_000_000)
                            await MainActor.run { router.go(.home) }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }

    private func catChip(_ c: String) -> some View {
        let sel = cat == c
        return Button {
            cat = c
        } label: {
            Text(c)
                .font(.system(size: 14, weight: sel ? .bold : .medium))
                .foregroundStyle(sel ? T.primary : T.ink)
                .padding(.horizontal, 16)
                .frame(minHeight: 42)
                .background(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(sel ? T.primary.opacity(0.06) : T.pearl)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(sel ? T.primary : T.hair, lineWidth: sel ? 1.5 : 1)
                )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    SuggestView()
        .environmentObject(RouterStore(initial: .homeSuggest))
        .environmentObject(AppStore())
}

// MARK: - §17 SuggestFeedView · 建議回応一覧

struct SuggestFeedView: View {
    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "建議回応一覧", level: 2)
            ScrollView {
                VStack(spacing: 10) {
                    ForEach(SEED.suggestions) { s in
                        Card(padding: 14) {
                            VStack(alignment: .leading, spacing: 0) {
                                // date · fontSize 10.5 mono inkMute · marginBottom 6
                                Text(s.date)
                                    .font(.system(size: 10.5, design: .monospaced))
                                    .foregroundStyle(T.inkMute)
                                    .padding(.bottom, 6)
                                // Q · fontSize 13 bold ink · marginBottom 8
                                Text("Q · \(s.q)")
                                    .font(.system(size: 13, weight: .bold))
                                    .foregroundStyle(T.ink)
                                    .padding(.bottom, 8)
                                // A · padding '10 12' borderRadius 10 primary/0a bg · primaryDk fg fontSize 12.5
                                Text("A · \(s.a)")
                                    .font(.system(size: 12.5))
                                    .foregroundStyle(T.primaryDk)
                                    .lineSpacing(2)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 10)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .background(
                                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                                            .fill(T.primary.opacity(0.04))
                                    )
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
    }
}

#Preview {
    SuggestFeedView()
        .environmentObject(RouterStore(initial: .homeSuggestFeed))
        .environmentObject(AppStore())
}
