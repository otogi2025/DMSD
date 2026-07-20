// CommunityStubs.swift · Community feature · v2 HTML-fidelity rewrite
// Agent C v2 · 14 struct（宿舍墙 WallView 3 struct + 旧日历 EventsView 已删，见 IOS_DESIGN_LOG §14.14）· 对等 JSX 源 33f0266b__NotificationsPage_PackagesPage_PackageDetailPage.js
// Fidelity 铁律：JSX 原文直抄、数值对照 style、Icon 全 Foundation Ic、颜色 T tokens / colorFromHex()
// v2 HTML 修正：UI 文字与界面日语对齐（快递/点歌等）+ C1 中文残留已修

import SwiftUI

// MARK: - Color hex String helper（SEED.lost[i].color 是 "#3b82f6" 字符串）

private func colorFromHex(_ hex: String) -> Color {
    var h = hex.trimmingCharacters(in: .whitespaces)
    if h.hasPrefix("#") { h.removeFirst() }
    var v: UInt64 = 0
    Scanner(string: h).scanHexInt64(&v)
    return Color(
        red: Double((v >> 16) & 0xFF) / 255,
        green: Double((v >> 8) & 0xFF) / 255,
        blue: Double(v & 0xFF) / 255
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

/// 2-tab segmented（待領 / 領済 · 列表 / 日历）
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

/// 右上 "+" icon 按钮（Lost / Music 顶部）
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
    @EnvironmentObject var app: AppStore
    @State private var filter: String = "すべて"
    /// 4-30 加「学習」(R1 例外的 push 通知种类)
    private let filters = ["すべて", "申請", "減点", "夜学習", "宅配", "活動", "リクエスト曲"]

    private var filtered: [NotificationItem] {
        // 数据源 = AppStore.allNotifications（push 模拟通知 + SEED.notifications）
        if filter == "すべて" { return app.allNotifications }
        return app.allNotifications.filter { $0.type == filter }
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
                            // NET-02: feed 拉取失败时显失败态，不再静默显「通知はありません」假空态
                            switch app.notificationsState {
                            case .loading:
                                // 加载中显骨架，避免冷启动那一两秒闪「通知はありません」假空态（codex 复审 minor）
                                VStack(spacing: 8) { Skeleton(height: 72); Skeleton(height: 72); Skeleton(height: 72) }
                            case let .failed(msg):
                                EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: msg)
                            default:
                                EmptyState(icon: "bell", title: "通知はありません")
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        // IX-009：进入通知中心时拉真公告（生产构建的通知源）；演示构建此调用是空操作。
        .task { await app.refreshNotificationSources() }
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
        // §7.13.1：点后端 feed 来源通知（kind/refId 非 nil）→ 标已读；push/宅配/SEED 无 kind 不响应。
        .contentShape(Rectangle())
        .onTapGesture {
            guard let kind = n.kind, let refId = n.refId, n.unread else { return }
            Task { await app.markStudentNotificationRead(kind: kind, refId: refId) }
        }
    }

    /// 对等 JSX: n.type==='減点'?'warn':n.type==='申請'?'ok':'accent'
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

// MARK: - 包裹展示模型（统一 demo 假数据 与 生产真后端两个数据源）

/// 宅配卡片 / 详情共用的展示模型。
/// - 演示构建(#if DEMO)：由 `SEED.packages`（静态假数据 PackageItem）映射
/// - 生产构建：由 `AppStore.packages`（GET /api/v1/front-desk/mine 真后端 FrontDeskItemBrief）映射
/// 两个数据源在 UI 层收敛成一个类型，PackagesView / MyPackagesView / PackageDetailView 都只认它，
/// 假数据靠 `#if DEMO` 守卫 → 生产构建绝不显示假包裹。
struct PackageDisplay: Identifiable {
    let id: String // 演示=PackageItem.id(Int) 转字符串 / 生产=FrontDeskItem UUID 字符串
    let title: String // 演示=配送業者 / 生产=包裹说明(description)
    let dateLabel: String // 到着日（卡片副标题）
    let arrivedLabel: String // 详情「到着」行文案
    let tracking: String? // 追跡番号（仅演示有，后端无此字段）
    let location: String? // 保管場所（后端 location）
    let itemCount: Int // 宅配件数（后端 item_count；演示默认 1）
    let isWaiting: Bool // true=待取（状态 pending/notified）/ false=已取（picked_up 等终态）
    let statusLabel: String // 详情「状態」行用：精确到 5 状态（picked_up/expired/discarded 各自文案，不一律「受取済」）
    var statusText: String {
        isWaiting ? "受取待ち" : "受取済"
    }
}

/// 后端 5 状态 → 学生侧展示文案（codex 审查 major #2：expired/discarded 不能一律显示「受取済」）。
private func packageStatusLabel(_ backendStatus: String) -> String {
    switch backendStatus {
    case "pending", "notified": return "受取待ち"
    case "picked_up": return "受取済"
    case "expired": return "期限切れ"
    case "discarded": return "処分済"
    default: return backendStatus
    }
}

private let pkgDateFmt: DateFormatter = {
    let f = DateFormatter()
    f.locale = Locale(identifier: "ja_JP")
    f.timeZone = TimeZone(identifier: "Asia/Tokyo")
    f.dateFormat = "yyyy-MM-dd"
    return f
}()

private let pkgArrivedFmt: DateFormatter = {
    let f = DateFormatter()
    f.locale = Locale(identifier: "ja_JP")
    f.timeZone = TimeZone(identifier: "Asia/Tokyo")
    f.dateFormat = "yyyy-MM-dd HH:mm"
    return f
}()

extension PackageDisplay {
    /// 演示构建：从 SEED 假数据映射。
    init(demo p: PackageItem) {
        self.init(
            id: String(p.id),
            title: p.from,
            dateLabel: p.date,
            arrivedLabel: "\(p.date) 14:22",
            tracking: p.tracking,
            location: "寮務室前棚 A-3",
            itemCount: 1, // 演示假数据无件数字段，占位 1
            isWaiting: p.status == "受取待ち",
            statusLabel: p.status // 演示数据状态本就是日语「受取待ち / 受取済」
        )
    }

    /// 生产构建：从后端 FrontDeskItemBrief 映射（status pending/notified 视为待取、其余视为已取）。
    init(brief b: AppStore.FrontDeskItemBrief) {
        self.init(
            id: b.id.uuidString,
            // 备注可空（6-14 起宅配备注改可选）→ 空时用件数当主标题，保证卡片有意义
            title: b.description.isEmpty ? "荷物\(b.itemCount)件" : b.description,
            dateLabel: pkgDateFmt.string(from: b.createdAt),
            arrivedLabel: pkgArrivedFmt.string(from: b.notifiedAt ?? b.createdAt),
            tracking: nil,
            location: b.location,
            itemCount: b.itemCount,
            isWaiting: b.status == "pending" || b.status == "notified",
            statusLabel: packageStatusLabel(b.status)
        )
    }
}

// MARK: - §2 PackagesView · 宅配（v2 修正：快递 → 宅配）

struct PackagesView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var tab: PkgTab = .wait

    enum PkgTab: Hashable { case wait, done }

    /// 全部包裹（演示=SEED 假数据 / 生产=后端真数据，靠 #if DEMO 守卫）。
    private var allRows: [PackageDisplay] {
        #if DEMO
            return SEED.packages.map(PackageDisplay.init(demo:))
        #else
            return app.packages.map(PackageDisplay.init(brief:))
        #endif
    }

    private var waitCount: Int {
        allRows.filter { $0.isWaiting }.count
    }

    private var doneCount: Int {
        allRows.filter { !$0.isWaiting }.count
    }

    private var list: [PackageDisplay] {
        allRows.filter { tab == .wait ? $0.isWaiting : !$0.isWaiting }
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "宅配", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // SegTabs · marginBottom 14
                    SegTabs(selection: $tab, items: [
                        (.wait, "受取待ち · \(waitCount)"),
                        (.done, "受取済 · \(doneCount)"),
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
                            // NET-01: 网络/解码失败时显失败态，不再静默显「荷物はありません」假空态
                            switch app.packagesState {
                            case .loading:
                                // 加载中显骨架，避免冷启动那一两秒闪「荷物はありません」假空态（codex 复审 minor）
                                VStack(spacing: 10) { Skeleton(height: 72); Skeleton(height: 72) }
                            case let .failed(msg):
                                EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: msg)
                            default:
                                EmptyState(icon: "shippingbox", title: tab == .wait ? "受取待ちの荷物はありません" : "受取済の荷物はありません")
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task {
            // 生产构建：进页拉真后端包裹（演示构建用 SEED，不拉）
            #if !DEMO
                await app.loadMyPackages()
            #endif
        }
    }

    private func pkgCard(_ p: PackageDisplay) -> some View {
        Button { router.go(.homePackageDetail(id: p.id)) } label: {
            Card(padding: 14) {
                // HStack alignItems:'center' gap:12
                HStack(alignment: .center, spacing: 12) {
                    // JSX 用 emoji 📦 fontSize:28 · 保留（Fidelity：不自作主张换 SF Symbol）
                    Text("📦")
                        .font(.system(size: 28))
                    VStack(alignment: .leading, spacing: 2) {
                        Text(p.title)
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                        // date + tracking · fontFamily:T.mono fontSize:11 color:T.inkMute
                        Text("\(p.dateLabel)\(p.tracking.map { " · \($0)" } ?? "")")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundStyle(T.inkMute)
                    }
                    Spacer()
                    // 待領 only：受取 button · height 36 padding '0 16' fontSize 13
                    if p.isWaiting {
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
    let id: String
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// 演示=按 SEED 的 Int id（转字符串）匹配 / 生产=按后端 UUID 字符串匹配，靠 #if DEMO 守卫。
    private var item: PackageDisplay? {
        #if DEMO
            return SEED.packages.first(where: { String($0.id) == id }).map(PackageDisplay.init(demo:))
        #else
            return app.packages.first(where: { $0.id.uuidString.caseInsensitiveCompare(id) == .orderedSame }).map(PackageDisplay.init(brief:))
        #endif
    }

    /// 详情 meta 行：演示沿用 JSX 4 行（含追踪号等门面字段）；
    /// 生产只列后端真有的字段（说明 / 到达 / 状态 / 保管位置），不假造后端没有的配送商、追踪号。
    private func rows(_ p: PackageDisplay) -> [(String, String)] {
        #if DEMO
            return [
                ("配送業者", p.title),
                ("到着時刻", p.arrivedLabel),
                ("追跡番号", p.tracking ?? "―"),
                ("保管場所", p.location ?? "―"),
            ]
        #else
            var r: [(String, String)] = [
                ("内容", p.title),
                ("件数", "\(p.itemCount)件"),
                ("到着", p.arrivedLabel),
                ("状態", p.statusLabel),
            ]
            if let loc = p.location, !loc.isEmpty {
                r.append(("保管場所", loc))
            }
            return r
        #endif
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
                        // 受取確認：仅演示构建。生产无学生自助确认端点（取走由老师标记 / NFC 取走是 v1.1+），
                        // 不放假按钮误导学生。
                        #if DEMO
                            PrimaryButton(title: "受取確認") {
                                app.showToast("受取完了しました")
                                router.back()
                            }
                            .padding(.horizontal, 20)
                            .padding(.top, 20)
                        #endif
                    } else {
                        EmptyState(icon: "shippingbox", title: "荷物が見つかりません")
                    }
                    Spacer().frame(height: 24)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task {
            // 生产构建：深进详情时若包裹缓存还空（冷启动 / 直达），补拉一次
            #if !DEMO
                if app.packages.isEmpty { await app.loadMyPackages() }
            #endif
        }
    }
}

#Preview {
    PackageDetailView(id: "1")
        .environmentObject(RouterStore(initial: .homePackageDetail(id: "1")))
        .environmentObject(AppStore())
}

// MARK: - §4 LostView · 遺失物

/// 遗失物卡片视图模型 —— 演示（SEED.lost）/ 生产（LostFoundOut）归一成同一套展示字段。
struct LostDisplay: Identifiable {
    let id: String // 演示=LostItem.id(Int)→String / 生产=UUID 字符串
    let title: String // 演示=title / 生产=item_name
    let place: String // 演示=place / 生产=location
    let date: String // 卡片日期 label（演示=date / 生产=created_at 格式化）
    let detail: String? // 详情描述（生产=description / 演示=nil，详情页演示用固定文案）
    let colorHex: String // 卡片渐变色（演示=color / 生产=固定色，后端无装饰色字段）
    let isResolved: Bool // 生产 status==resolved（已解决）
    let ownerId: String? // 投稿者 UUID（生产=student_id，用于「本人才能解决」判断；演示=nil）
}

private let lostDateFmt: DateFormatter = {
    let f = DateFormatter()
    f.locale = Locale(identifier: "ja_JP")
    f.timeZone = TimeZone(identifier: "Asia/Tokyo")
    f.dateFormat = "MM-dd"
    return f
}()

extension LostDisplay {
    /// 演示构建：从 SEED.lost 映射。
    init(demo l: LostItem) {
        self.init(
            id: String(l.id), title: l.title, place: l.place, date: l.date,
            detail: nil, colorHex: l.color, isResolved: false, ownerId: nil
        )
    }

    /// 生产构建：从后端 LostFoundOut 映射（固定渐变色）。
    init(real l: LostFoundOut) {
        self.init(
            id: l.id.uuidString, title: l.item_name, place: l.location ?? "—",
            date: lostDateFmt.string(from: l.created_at), detail: l.description,
            colorHex: "#7c3aed", isResolved: l.status == "resolved",
            ownerId: l.student_id.uuidString
        )
    }
}

struct LostView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore
    @State private var search: String = ""

    /// 全部遗失物（演示=SEED 假数据 / 生产=后端真数据，靠 #if DEMO 守卫，归一成 LostDisplay）。
    private var allRows: [LostDisplay] {
        #if DEMO
            return SEED.lost.map(LostDisplay.init(demo:))
        #else
            return app.lostFound.map(LostDisplay.init(real:))
        #endif
    }

    /// IX-030 修复：按搜索词过滤：标题 / 拾得场所 / 日期任一命中即保留，大小写不敏感。
    /// 搜索词为空时返回全部。
    private var filteredLost: [LostDisplay] {
        let q = search.trimmingCharacters(in: .whitespacesAndNewlines)
        if q.isEmpty { return allRows }
        return allRows.filter {
            $0.title.localizedCaseInsensitiveContains(q)
                || $0.place.localizedCaseInsensitiveContains(q)
                || $0.date.localizedCaseInsensitiveContains(q)
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 遺失物只有寮監可投稿 → 学生端右上无 + 按钮（仅浏览）
            PageHeader(title: "遺失物", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // 提示：请将拾得物交给寮監
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
                        TextField("検索…", text: $search)
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
                    // 三态（ios④ 上线缺口）：原来直接铺 grid、无加载/失败/空态 → 网断时一片空白被当成「没有遗失物」。
                    // 演示版 lostFoundState 恒 .idle 走 default。
                    if allRows.isEmpty {
                        switch app.lostFoundState {
                        case .loading:
                            ProgressView().frame(maxWidth: .infinity).padding(.top, 40)
                        case let .failed(msg):
                            EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: msg)
                                .frame(maxWidth: .infinity).padding(.top, 20)
                        default:
                            EmptyState(icon: "magnifyingglass", title: "落とし物はありません")
                                .frame(maxWidth: .infinity).padding(.top, 20)
                        }
                    } else if filteredLost.isEmpty {
                        // 有数据但搜索词无匹配
                        EmptyState(icon: "magnifyingglass", title: "見つかりません")
                            .frame(maxWidth: .infinity).padding(.top, 20)
                    } else {
                        LazyVGrid(columns: cols, spacing: 10) {
                            // IX-030 修复：数据源改用按搜索词过滤后的 filteredLost（原来直接铺 SEED.lost）
                            ForEach(filteredLost) { l in
                                lostCell(l)
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.bottom, 24)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task {
            #if !DEMO
                await app.loadLostFound()
            #endif
        }
    }

    private func lostCell(_ l: LostDisplay) -> some View {
        // 对等 JSX: aspectRatio 1 · gradient `${color}aa → ${color}44`
        Button { router.go(.homeLostDetail(id: l.id)) } label: {
            VStack(alignment: .leading, spacing: 0) {
                ZStack {
                    LinearGradient(
                        colors: [
                            colorFromHex(l.colorHex).opacity(2.0 / 3.0), // aa ≈ 0.67
                            colorFromHex(l.colorHex).opacity(0.27), // 44 ≈ 0.27
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
    @State private var postType: String = "found" // 種別 默认「拾得物」(found)
    @State private var itemName: String = ""
    @State private var place: String = ""
    @State private var feature: String = ""
    @State private var isSubmitting = false

    /// 品名必填（后端 item_name 必填）。
    private var canSubmit: Bool {
        !itemName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

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

                    // 種別选择（「拾得物」found /「落とし物」lost）—— 后端 post_type 必填。
                    Field(label: "種別", required: true) {
                        HStack(spacing: 8) {
                            typeChip(title: "拾得物", value: "found")
                            typeChip(title: "落とし物", value: "lost")
                        }
                    }
                    .padding(.bottom, 18)

                    Field(label: "品名", required: true) {
                        TField(text: $itemName, placeholder: "傘 / 鍵 / 財布 …")
                    }
                    .padding(.bottom, 18)

                    Field(label: "場所", required: true) {
                        TField(text: $place, placeholder: "玄関 / 廊下 / …")
                    }
                    .padding(.bottom, 18)

                    Field(label: "特徴", required: true) {
                        TArea(text: $feature, placeholder: "色・大きさ・目印", rows: 3)
                    }
                    .padding(.bottom, 18)

                    // 原有「拾得日時」栏写死过去日期「2026-04-22 15:00」、且不参与提交（submit 不读它），
                    // 是 JSX 直译演示残留。生产页不应显示写死的过去日期，已删整栏。
                    // 若日后要真实拾得日時，应改成日期选择器并加入 LostFoundBody 传后端。

                    PrimaryButton(title: "投稿する", enabled: canSubmit && !isSubmitting) {
                        submit()
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

    /// 種別选择 chip。
    private func typeChip(title: String, value: String) -> some View {
        let selected = postType == value
        return Button { postType = value } label: {
            Text(title)
                .font(.system(size: 14, weight: selected ? .bold : .medium))
                .foregroundStyle(selected ? T.primary : T.ink)
                .padding(.horizontal, 16).padding(.vertical, 10)
                .background {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(selected ? T.primary.opacity(0.06) : T.pearl)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(selected ? T.primary : T.hair, lineWidth: selected ? 1.5 : 1)
                }
        }
        .buttonStyle(.plain)
    }

    /// 投稿提交 —— 演示版假 toast / 生产版 POST /lost-found。
    private func submit() {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        #if DEMO
            app.showToast("投稿しました")
            Task {
                try? await Task.sleep(nanoseconds: 500_000_000)
                await MainActor.run {
                    isSubmitting = false
                    router.go(.homeLost)
                }
            }
        #else
            let loc = place.trimmingCharacters(in: .whitespacesAndNewlines)
            let desc = feature.trimmingCharacters(in: .whitespacesAndNewlines)
            let body = LostFoundBody(
                post_type: postType,
                item_name: itemName.trimmingCharacters(in: .whitespacesAndNewlines),
                description: desc.isEmpty ? nil : desc,
                location: loc.isEmpty ? nil : loc
            )
            let tokenAtStart = app.authToken
            Task {
                defer { isSubmitting = false }
                do {
                    _ = try await LostFoundAPI.create(body)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话刷新 / 弹 toast
                    await app.loadLostFound() // 投稿后刷新一览
                    guard app.authToken == tokenAtStart else { return } // loadLostFound 也有 await → 二次确认再 toast/导航
                    app.showToast("投稿しました")
                    router.go(.homeLost)
                } catch {
                    app.showToast("投稿に失敗しました")
                }
            }
        #endif
    }
}

#Preview {
    LostNewView()
        .environmentObject(RouterStore(initial: .homeLostNew))
        .environmentObject(AppStore())
}

// MARK: - §6 LostDetailView · 遺失物詳細

/// 投稿通報按钮（App Store 审核指南 1.2 UGC 治理 — itsuki 2026-07-20 拍板 A 方案）。
/// 详情页右下角的小按钮：点击 → 确认弹窗 → POST /api/v1/reports → toast 反馈。
/// 演示版只弹 toast（SEED 假数据无 UUID）；生产版真调后端。
struct ReportFlagButton: View {
    let contentType: String // "song" / "announcement_reply" / "lost_found"
    let contentId: String
    @EnvironmentObject var app: AppStore
    @State private var confirming = false

    var body: some View {
        Button {
            confirming = true
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "exclamationmark.bubble")
                    .font(.system(size: 12))
                Text("通報する")
                    .font(.system(size: 12))
            }
            .foregroundStyle(T.inkMute)
        }
        .frame(maxWidth: .infinity, alignment: .trailing)
        .confirmationDialog(
            "この投稿を通報しますか？",
            isPresented: $confirming,
            titleVisibility: .visible
        ) {
            Button("通報する", role: .destructive) { submit() }
            Button("キャンセル", role: .cancel) {}
        } message: {
            Text("不適切な内容として寮の教職員に報告します。")
        }
    }

    private func submit() {
        #if DEMO
            app.showToast("通報しました")
        #else
            guard let uuid = UUID(uuidString: contentId) else {
                // 理论上只有演示假数据混进生产路径才会走到 — 静默吞掉会让用户以为通報成功
                app.showToast("通報に失敗しました")
                return
            }
            Task {
                do {
                    _ = try await ReportsAPI.report(contentType: contentType, contentId: uuid)
                    app.showToast("通報しました。ご協力ありがとうございます")
                } catch {
                    app.showToast("通報に失敗しました")
                }
            }
        #endif
    }
}

struct LostDetailView: View {
    let id: String
    @EnvironmentObject var app: AppStore
    @State private var resolving = false

    /// 演示=按 id 从 SEED 查 / 生产=从后端缓存按 UUID 查，归一成 LostDisplay。
    private var item: LostDisplay? {
        #if DEMO
            return SEED.lost.first(where: { String($0.id) == id }).map(LostDisplay.init(demo:))
        #else
            return app.lostFound.first(where: { $0.id.uuidString.caseInsensitiveCompare(id) == .orderedSame }).map(LostDisplay.init(real:))
        #endif
    }

    /// 详情描述：演示用固定文案（SEED 无此字段）/ 生产显真 description。
    private var detailText: String {
        #if DEMO
            return "玄関付近で拾いました。黒色の折りたたみ傘で、持ち手に小さな白い傷があります。お心当たりのある方はご連絡ください。"
        #else
            return item?.detail ?? "（説明はありません）"
        #endif
    }

    /// 本人投稿且未解决 → 显示「解决」按钮（后端 PATCH resolve 仅投稿者本人可调）。
    /// 大小写不敏感比对 —— ownerId 来自 Swift UUID.uuidString(大写)，myStudentId 来自后端 /me 的 id(小写)。
    private var canResolve: Bool {
        guard let l = item, !l.isResolved,
              let owner = l.ownerId, let me = app.myStudentId else { return false }
        return owner.caseInsensitiveCompare(me) == .orderedSame
    }

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
                                    colorFromHex(l.colorHex).opacity(2.0 / 3.0),
                                    colorFromHex(l.colorHex).opacity(0.27),
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
                                if l.isResolved {
                                    Pill(text: "解決済み", tone: .ok)
                                }
                            }
                            .padding(.bottom, 14)
                            Text(detailText)
                                .font(.system(size: 14))
                                .foregroundStyle(T.inkSub)
                                .lineSpacing(4) // lineHeight 1.7
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.bottom, 20)
                            #if DEMO
                                // 演示版保留「私のものです」claim（联系投稿者是 v1.1，无后端接口）。
                                PrimaryButton(title: "私のものです") {
                                    app.showToast("投稿者に通知しました")
                                }
                            #else
                                // 生产版：仅投稿者本人、未解决时显「解决」按钮 → PATCH /lost-found/{id}/resolve。
                                if canResolve {
                                    PrimaryButton(title: "解決済みにする", enabled: !resolving) {
                                        resolve(l)
                                    }
                                }
                            #endif
                            ReportFlagButton(contentType: "lost_found", contentId: l.id)
                                .padding(.top, 14)
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
        .task {
            #if !DEMO
                // 深链直接进详情时缓存可能为空 → 拉一次一览兜底。
                if app.lostFound.isEmpty { await app.loadLostFound() }
            #endif
        }
    }

    /// 标为已解决（仅生产）。
    private func resolve(_ l: LostDisplay) {
        #if !DEMO
            guard let uuid = UUID(uuidString: l.id) else { return }
            resolving = true
            let tokenAtStart = app.authToken
            Task {
                defer { resolving = false } // 任何 return（含下方 guard 提前返回）都复位按钮，否则永久禁用
                do {
                    _ = try await LostFoundAPI.resolve(id: uuid)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话刷新 / 弹 toast
                    await app.loadLostFound()
                    guard app.authToken == tokenAtStart else { return } // loadLostFound 也有 await → 二次确认再 toast
                    app.showToast("解決済みにしました")
                } catch {
                    app.showToast("操作に失敗しました")
                }
            }
        #endif
    }
}

#Preview {
    LostDetailView(id: "1")
        .environmentObject(RouterStore(initial: .homeLostDetail(id: "1")))
        .environmentObject(AppStore())
}

// MARK: - §7 MusicView · リクエスト曲（system_features §7.11 — 2026-05-01 拍板）

//
// 変更点:
// - 排序：投稿顺（新→旧 = id 降序）。赞成/反对废止。

/// 点歌卡片视图模型 —— 演示（SEED.songs）/ 生产（SongRequestOut）归一成同一套展示字段。
struct SongDisplay: Identifiable {
    let id: String // 演示=SongItem.id(Int)→String / 生产=UUID 字符串
    let title: String
    let artist: String
    let by: String // 投稿者名（演示有 / 生产后端无此字段 → 空）
    let note: String? // 投稿理由（生产=note / 演示=nil，详情页演示用固定文案）

    /// 卡片副标题：生产无投稿者 → 只显艺术家。
    var metaLine: String {
        by.isEmpty ? artist : "\(artist) · \(by)"
    }
}

extension SongDisplay {
    /// 演示构建：从 SEED.songs 映射。
    init(demo s: SongItem) {
        self.init(id: String(s.id), title: s.title, artist: s.artist, by: s.by, note: nil)
    }

    /// 生产构建：从后端 SongRequestOut 映射（无投稿者 / 无票数）。
    init(real s: SongRequestOut) {
        self.init(
            id: s.id.uuidString, title: s.song_title, artist: s.artist ?? "", by: "", note: s.note
        )
    }
}

struct MusicView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// 演示=SEED 假数据(新→旧) / 生产=后端真数据(后端已新→旧)，靠 #if DEMO 守卫，归一成 SongDisplay。
    private var rows: [SongDisplay] {
        #if DEMO
            return SEED.songs.sorted { $0.id > $1.id }.map(SongDisplay.init(demo:))
        #else
            return app.songRequests.map(SongDisplay.init(real:))
        #endif
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(
                title: "リクエスト曲",
                level: 2,
                right: AnyView(HeaderPlusButton { router.go(.homeMusicNew) })
            )
            ScrollView {
                VStack(spacing: 0) {
                    VStack(spacing: 8) {
                        ForEach(rows) { s in
                            songCard(s: s)
                        }
                        if rows.isEmpty {
                            // 三态（ios④ 上线缺口）：演示 idle 走 default；生产区分 加载中 / 失败 / 真没数据
                            switch app.songsState {
                            case .loading:
                                ProgressView().frame(maxWidth: .infinity).padding(.vertical, 16)
                            case let .failed(msg):
                                EmptyState(icon: "exclamationmark.triangle", title: "読み込みに失敗しました", message: msg)
                            default:
                                EmptyState(icon: "music.note", title: "リクエストされた曲はまだありません")
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.top, 4)
                .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task {
            #if !DEMO
                await app.loadSongs()
            #endif
        }
    }

    private func songCard(s: SongDisplay) -> some View {
        Card(padding: 14) {
            HStack(alignment: .center, spacing: 12) {
                // 44x44 渐变专辑封面（点击进详情）
                Button { router.go(.homeMusicDetail(id: s.id)) } label: {
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
                }
                .buttonStyle(.plain)

                // title + meta · flex 1（点击进详情）
                Button { router.go(.homeMusicDetail(id: s.id)) } label: {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(s.title)
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(T.ink)
                            .lineLimit(1)
                            .truncationMode(.tail)
                        Text(s.metaLine)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                            .lineLimit(1)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
        }
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
    @State private var isSubmitting = false

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

                    // IX-021 修复：曲名 / 艺术家 两个字段标了必填（红星号），
                    // 投稿按钮要在两者都非空时才可点。
                    // trimmingCharacters 去掉首尾空白，防止只输空格也算非空。
                    let canSubmitSong = !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                        && !artist.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                    PrimaryButton(title: "投稿する", enabled: canSubmitSong && !isSubmitting) {
                        submit()
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

    /// 点歌投稿提交 —— 演示版假 toast / 生产版 POST /songs（后端按本人寮自动取 dorm）。
    private func submit() {
        // 防连点：提交在途再点直接忽略，避免重复提交
        guard !isSubmitting else { return }
        isSubmitting = true
        #if DEMO
            app.showToast("投稿しました")
            Task {
                try? await Task.sleep(nanoseconds: 500_000_000)
                await MainActor.run {
                    isSubmitting = false
                    router.go(.homeMusic)
                }
            }
        #else
            // Apple Music URL 是演示版的「自動取得」占位，后端无 url 字段 → 生产只传曲名 / 艺术家 / 投稿理由。
            let trimmedNote = reason.trimmingCharacters(in: .whitespacesAndNewlines)
            let body = SongRequestBody(
                song_title: title.trimmingCharacters(in: .whitespacesAndNewlines),
                artist: artist.trimmingCharacters(in: .whitespacesAndNewlines),
                note: trimmedNote.isEmpty ? nil : trimmedNote
            )
            let tokenAtStart = app.authToken
            Task {
                defer { isSubmitting = false }
                do {
                    _ = try await SongsAPI.create(body)
                    guard app.authToken == tokenAtStart else { return } // 切账号 / 登出后不在新会话刷新 / 弹 toast
                    await app.loadSongs() // 投稿后刷新一览
                    guard app.authToken == tokenAtStart else { return } // loadSongs 也有 await → 二次确认再 toast/导航
                    app.showToast("投稿しました")
                    router.go(.homeMusic)
                } catch {
                    app.showToast("投稿に失敗しました")
                }
            }
        #endif
    }
}

#Preview {
    MusicNewView()
        .environmentObject(RouterStore(initial: .homeMusicNew))
        .environmentObject(AppStore())
}

// MARK: - §9 MusicDetailView · 曲詳細

struct MusicDetailView: View {
    let id: String
    @EnvironmentObject var app: AppStore

    /// 演示=按 id 从 SEED 查(查不到 fallback 第一首) / 生产=从后端缓存按 UUID 查，归一成 SongDisplay。
    private var song: SongDisplay? {
        #if DEMO
            let item = SEED.songs.first(where: { String($0.id) == id }) ?? SEED.songs.first
            return item.map(SongDisplay.init(demo:))
        #else
            return app.songRequests.first(where: { $0.id.uuidString.caseInsensitiveCompare(id) == .orderedSame }).map(SongDisplay.init(real:))
        #endif
    }

    /// 副标题：演示显「artist · 投稿 投稿者」/ 生产无投稿者 → 只显 artist。
    private var metaText: String {
        guard let s = song else { return "" }
        #if DEMO
            return "\(s.artist) · 投稿 \(s.by)"
        #else
            return s.artist
        #endif
    }

    /// 投稿理由：演示用固定文案（SEED 无此字段）/ 生产显真 note。
    private var reasonText: String {
        #if DEMO
            return "朝の支度時間に聴きたい、明るい気持ちになれる曲です。"
        #else
            return song?.note ?? "（理由は未記入です）"
        #endif
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "曲詳細", level: 2)
            ScrollView {
                if song == nil {
                    // 生产深链指向不存在的曲 → 空状态（对齐 LostDetailView，codex 复审 minor-2）
                    EmptyState(icon: "music.note", title: "見つかりません")
                        .padding(.top, 40)
                } else {
                    VStack(spacing: 0) {
                        // 160x160 rounded album · gradient · centered
                        ZStack {
                            LinearGradient(
                                colors: [T.accentSoft, T.accent],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                            Ic.music(82).foregroundStyle(.white)
                        }
                        .frame(width: 160, height: 160)
                        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                        .shadow(color: T.primary.opacity(0.25), radius: 20, x: 0, y: 12)
                        .padding(.bottom, 20)

                        Text(song?.title ?? "—")
                            .font(.system(size: 22, weight: .heavy))
                            .foregroundStyle(T.ink)
                            .padding(.bottom, 6)

                        Text(metaText)
                            .font(.system(size: 14))
                            .foregroundStyle(T.inkSub)
                            .padding(.bottom, 24)

                        Card(padding: 16) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("投稿理由")
                                    .font(.system(size: 12))
                                    .foregroundStyle(T.inkSub)
                                Text(reasonText)
                                    .font(.system(size: 14))
                                    .foregroundStyle(T.ink)
                                    .lineSpacing(3)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                        .padding(.bottom, 12)

                        if let s = song {
                            ReportFlagButton(contentType: "song", contentId: s.id)
                                .padding(.bottom, 18)
                        }
                    }
                    .padding(20)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task {
            #if !DEMO
                // 深链直接进详情时缓存可能为空 → 拉一次一览兜底。
                if app.songRequests.isEmpty { await app.loadSongs() }
            #endif
        }
    }
}

#Preview {
    MusicDetailView(id: "1")
        .environmentObject(RouterStore(initial: .homeMusicDetail(id: "1")))
        .environmentObject(AppStore())
}

// MARK: - §14 EventDetailView · 活動詳細

struct EventDetailView: View {
    let id: Int
    @EnvironmentObject var app: AppStore

    /// id 是 list index（Events 用 idx 作 id）· fallback 0
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
                                colors: [Color(hex: 0xE8F4F6), Color(hex: 0xA8DCE2)],
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

                    // desc card · 正文只显 event.desc（原 JSX 给所有活动写死追加「新入生の自己紹介…」后缀，
                    // 对防灾演练/考试等任意活动都不合理，已删）
                    Card(padding: 16) {
                        Text(event.desc)
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
