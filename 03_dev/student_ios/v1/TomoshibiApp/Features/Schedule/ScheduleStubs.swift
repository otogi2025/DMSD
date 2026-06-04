// ScheduleStubs.swift · 行事预定 月历（日历「行事予定」页）
// ⭐ 会话 C · 老師 38 条 #9「行事予定の表示（参考用）」+ Q9「現有日历不够要加强」
//
// API 对接（杭田 2026-06-04 需求「一・行事予定表示」）:
//   GET /api/v1/events?from_date=&to_date=   → ScheduleView   (system_features §7.5)
//   后端 routers/events.py 已实装，学生 + 老师都可看。
//
// 三态加载（仿 BusListView.load，见同工程 BusListStubs.swift）:
//   - 未登录       → 回退 SEED.events（开发态 / Apple 审核员没真账号也能看效果）
//   - 已登录       → 拉真后端，把 EventOut 映射成 UI 用的 EventItem
//   - 已登录但失败  → 不喂假数据（清空 + 报错）；401 清登录态
//
// 跟既存 demo 用的 EventsView（CommunityStubs.swift）的区别:
//   - demo EventsView: 只硬编码了 4 月 / 5 月
//   - 本 ScheduleView: 从数据源（真后端或 SEED 兜底）自动算出月份范围 → 可滚到任意月
//   - 详情页 EventDetailView 按 SEED 下标取数 → 只在「用 SEED 兜底」时才跳详情（见 onTapEvent）

import SwiftUI

struct ScheduleView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore // 判断登录态：已登录拉真后端 / 未登录回退 SEED

    /// 表示中の月（YearMonth）
    @State private var ym: YearMonth = ScheduleView.initialYearMonth()

    /// 選択された日（同じ月の中で nil 不可になったら 1）
    @State private var selectedDay: Int = ScheduleView.initialDay()

    /// 数据源：未登录 = SEED.events 兜底；已登录 = 后端 GET /api/v1/events 映射结果。
    @State private var events: [EventItem] = []
    @State private var isLoading: Bool = false
    @State private var loadError: String? = nil // 已登录拉取失败时的报错（不喂假数据，见 load）
    /// true = 当前数据源是 SEED 兜底（未登录）。决定点击行事行能否跳 SEED 下标制的详情页。
    @State private var usingMock: Bool = false

    private var monthRange: ClosedRange<YearMonth> {
        let all = events.compactMap { YearMonth(from: $0.date) }
        guard let lo = all.min(), let hi = all.max() else {
            // 还没数据（加载中 / 空）时给个含「今天」的安全范围，月份切换按钮不会全灰
            let now = ScheduleView.initialYearMonth()
            return now ... now
        }
        // 确保「今天」所在月一定在范围内（即使该月无行事，也能停在今天那一页）
        let now = ScheduleView.initialYearMonth()
        return min(lo, now) ... max(hi, now)
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "行事予定", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    if isLoading && events.isEmpty {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .padding(.top, 40)
                    } else if let err = loadError, events.isEmpty {
                        EmptyState(
                            icon: "calendar",
                            title: "読み込みに失敗しました",
                            message: err
                        )
                        .frame(maxWidth: .infinity)
                        .padding(.top, 20)
                    } else {
                        calendarCard
                        selectedDaySection
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
        .task { await load() }
    }

    // MARK: 数据加载（已登录拉真后端 / 未登录或失败回退 SEED）

    /// 未登录 → 回退 SEED.events（开发无 backend / Apple 审核员没真账号也能看日历效果）。
    /// 已登录 → GET /api/v1/events 真数据，映射成 EventItem。
    /// 已登录但拉取失败 → 不喂假行事（避免学生照着假日期跑活动 / 误事）：
    ///   401（token 失效）清登录态 + 提示重登；其它错误显示报错 + 空列表。
    /// 一次取够范围（去年初到明年底），月份切换不再二次请求。
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        guard app.isAuthenticated else {
            events = SEED.events
            usingMock = true
            return
        }
        loadError = nil
        let (from, to) = ScheduleView.fetchRange()
        do {
            let raw = try await EventsAPI.listEvents(fromDate: from, toDate: to)
            events = EventMapper.map(raw)
            usingMock = false
        } catch APIError.unauthorized {
            // token 失效：清登录态（令牌已死）+ 明确提示重登。
            // 不留空列表让用户误以为「没有行事」，也不退回 SEED 假数据。
            app.authToken = nil
            loadError = "セッションの有効期限が切れました。再度ログインしてください。"
            events = []
            usingMock = false
        } catch {
            loadError = APIErrorPresenter.userMessage(
                for: error,
                fallback: "行事予定の取得に失敗しました"
            )
            events = []
            usingMock = false
        }
    }

    /// 点击某行事 → 跳详情页。
    /// 详情页 EventDetailView 是按 SEED.events 的下标取数的（历史 demo 实现），
    /// 所以只有「用 SEED 兜底」时跳转才安全；拉了真后端时下标对不上 → 不跳（行内已显示完整信息）。
    private func onTapEvent(_ e: EventItem) {
        guard usingMock, let idx = SEED.events.firstIndex(where: { $0.id == e.id }) else { return }
        router.go(.homeEventDetail(id: idx))
    }

    // MARK: 月切替 + 日グリッド

    private var calendarCard: some View {
        Card(padding: 16) {
            VStack(alignment: .leading, spacing: 14) {
                monthSwitcher
                dayGrid
                if eventsInMonth > 0 {
                    Text("\(ym.month) 月：\(eventsInMonth) 件の予定")
                        .font(.system(size: 11))
                        .foregroundStyle(T.inkMute)
                }
            }
        }
    }

    private var monthSwitcher: some View {
        HStack {
            Button { stepMonth(-1) } label: {
                Ic.chevR(16)
                    .rotationEffect(.degrees(180))
                    .foregroundStyle(canGoBack ? T.ink : T.inkMute)
                    .frame(width: 36, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(!canGoBack)
            Spacer()
            // verbatim 防止 Locale 把 2026 自动加千位分隔符变 "2,026"
            Text(verbatim: "\(ym.year) 年 \(ym.month) 月")
                .font(.system(size: 15, weight: .bold))
                .foregroundStyle(T.ink)
            Spacer()
            Button { stepMonth(1) } label: {
                Ic.chevR(16)
                    .foregroundStyle(canGoForward ? T.ink : T.inkMute)
                    .frame(width: 36, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(!canGoForward)
        }
    }

    private var dayGrid: some View {
        let cols = Array(repeating: GridItem(.flexible(), spacing: 4), count: 7)
        return LazyVGrid(columns: cols, spacing: 4) {
            // 曜日ヘッダ
            ForEach(["日", "月", "火", "水", "木", "金", "土"], id: \.self) { d in
                Text(d)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(weekdayColor(d))
                    .padding(.vertical, 6)
            }
            // 月初前の空白
            ForEach(0 ..< ym.firstWeekdayIndex, id: \.self) { _ in
                Color.clear.aspectRatio(1, contentMode: .fit)
            }
            // 当月の日
            ForEach(1 ... ym.daysInMonth, id: \.self) { day in
                dayCell(day)
            }
        }
    }

    private func dayCell(_ day: Int) -> some View {
        let evs = eventsForDay(day)
        let isToday = ym.equals(today: ScheduleView.today) && day == ScheduleView.today.day
        let isSelected = day == selectedDay
        let bg: Color = isSelected ? T.primary : (isToday ? T.primary.opacity(0.12) : Color.clear)
        let fg: Color = isSelected ? .white : T.ink
        return Button {
            selectedDay = day
        } label: {
            // 数字居中 + 蓝点贴底（避免和数字重叠 — itsuki 2026-05-03 反馈）
            ZStack {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(bg)
                    .overlay {
                        if isToday && !isSelected {
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .stroke(T.primary, lineWidth: 1.5)
                        }
                    }
                Text(verbatim: "\(day)")
                    .font(.system(size: 13, weight: (isSelected || isToday) ? .heavy : .medium, design: .monospaced))
                    .foregroundStyle(fg)
                if !evs.isEmpty && !isSelected {
                    VStack(spacing: 0) {
                        Spacer(minLength: 0)
                        HStack(spacing: 2) {
                            ForEach(0 ..< min(evs.count, 3), id: \.self) { _ in
                                Circle().fill(T.accent).frame(width: 4, height: 4)
                            }
                        }
                        .padding(.bottom, 3)
                    }
                }
            }
            .aspectRatio(1, contentMode: .fit)
            .contentShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    // MARK: 選択日 詳細セクション

    private var selectedDaySection: some View {
        let evs = eventsForDay(selectedDay)
        let weekdayJP = ["日", "月", "火", "水", "木", "金", "土"]
        let weekdayIdx = (ym.firstWeekdayIndex + selectedDay - 1) % 7

        return VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Text("\(ym.month) 月 \(selectedDay) 日")
                    .font(.system(size: 18, weight: .heavy))
                    .foregroundStyle(T.ink)
                Text("（\(weekdayJP[weekdayIdx])）")
                    .font(.system(size: 13))
                    .foregroundStyle(T.inkSub)
                Spacer()
                if !evs.isEmpty {
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
                    Button { onTapEvent(e) } label: {
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
                    if !e.place.isEmpty {
                        HStack(spacing: 4) {
                            Text("📍").font(.system(size: 10))
                            Text(e.place)
                                .font(.system(size: 12))
                                .foregroundStyle(T.inkSub)
                                .lineLimit(1)
                        }
                    }
                }
                Spacer()
                Ic.chevR(14).foregroundStyle(T.inkMute)
            }
        }
    }

    // MARK: ナビゲーション補助

    private var canGoBack: Bool {
        ym > monthRange.lowerBound
    }

    private var canGoForward: Bool {
        ym < monthRange.upperBound
    }

    private func stepMonth(_ delta: Int) {
        let next = ym.advanced(by: delta)
        guard monthRange.contains(next) else { return }
        ym = next
        selectedDay = min(selectedDay, next.daysInMonth)
    }

    private var eventsInMonth: Int {
        events.filter { isInMonth($0.date) }.count
    }

    private func isInMonth(_ s: String) -> Bool {
        guard let other = YearMonth(from: s) else { return false }
        return other == ym
    }

    private func eventsForDay(_ day: Int) -> [EventItem] {
        let dateStr = String(format: "%d-%02d-%02d", ym.year, ym.month, day)
        return events.filter { $0.date == dateStr }
    }

    private func weekdayColor(_ d: String) -> Color {
        switch d {
        case "日": return T.danger
        case "土": return T.primary
        default: return T.inkMute
        }
    }

    // MARK: 「今日」「初期月」的决定

    /// 「今日」判定的基准日。演示版固定在 2026-04-23（跟既存 EventsView 同基准），
    /// 生产版取东京时区的实际今日（过了这天也不会张贴死在 4/23）
    private static var today: (year: Int, month: Int, day: Int) {
        #if DEMO
            return (year: 2026, month: 4, day: 23)
        #else
            var cal = Calendar(identifier: .gregorian)
            cal.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
            let c = cal.dateComponents([.year, .month, .day], from: Date())
            return (year: c.year ?? 2026, month: c.month ?? 4, day: c.day ?? 23)
        #endif
    }

    private static func initialYearMonth() -> YearMonth {
        YearMonth(year: today.year, month: today.month)
    }

    private static func initialDay() -> Int {
        today.day
    }

    /// 一次取够的日期范围：今年 1 月 1 日 到 明年 12 月 31 日。
    /// 覆盖整个学年 + 跨年，月份切换不必二次请求后端。返回 ("yyyy-MM-dd", "yyyy-MM-dd")。
    private static func fetchRange() -> (from: String, to: String) {
        let y = today.year
        return (from: String(format: "%d-01-01", y - 1), to: String(format: "%d-12-31", y + 1))
    }
}

// MARK: - EventMapper（后端 EventOut → UI 用 EventItem 映射）

enum EventMapper {
    /// 把后端行事预定映射成日历 UI 用的 EventItem。
    /// - date：直接用后端的纯日期字符串 event_date（"2026-04-23"）。
    /// - time：有 start_at 就按日本时区格式成 "HH:mm"，没有就空字符串（日历行不显示时刻）。
    /// - place：后端 EventOut 没有「场所」字段，统一留空（详情页里也不会画场所行）。
    /// - desc：用后端 description，空则空串。
    static func map(_ outs: [EventOut]) -> [EventItem] {
        let timeFmt = DateFormatter()
        timeFmt.locale = Locale(identifier: "en_US_POSIX")
        timeFmt.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
        timeFmt.dateFormat = "HH:mm"

        return outs.map { o in
            EventItem(
                date: o.event_date,
                time: o.start_at.map { timeFmt.string(from: $0) } ?? "",
                title: o.title,
                place: "",
                desc: o.description ?? ""
            )
        }
    }
}

// MARK: - YearMonth (year-month + 日数 + 月初曜日 計算)

struct YearMonth: Hashable, Comparable {
    let year: Int
    let month: Int

    init(year: Int, month: Int) {
        self.year = year
        self.month = month
    }

    init?(from dateString: String) {
        // "2026-04-23" → YearMonth(2026, 4)
        let parts = dateString.split(separator: "-")
        guard parts.count >= 2,
              let y = Int(parts[0]),
              let m = Int(parts[1]) else { return nil }
        self.init(year: y, month: m)
    }

    func advanced(by delta: Int) -> YearMonth {
        var totalMonth = year * 12 + (month - 1) + delta
        let newYear = totalMonth >= 0 ? (totalMonth / 12) : ((totalMonth - 11) / 12)
        totalMonth -= newYear * 12
        return YearMonth(year: newYear, month: totalMonth + 1)
    }

    /// 当月の日数
    var daysInMonth: Int {
        var comp = DateComponents()
        comp.year = year
        comp.month = month
        comp.day = 1
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
        guard let d = cal.date(from: comp),
              let r = cal.range(of: .day, in: .month, for: d) else { return 30 }
        return r.count
    }

    /// 月初日が週の何番目か（0 = 日曜）
    var firstWeekdayIndex: Int {
        var comp = DateComponents()
        comp.year = year
        comp.month = month
        comp.day = 1
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
        guard let d = cal.date(from: comp) else { return 0 }
        // Calendar.weekday: 1=Sunday..7=Saturday → index 0..6
        return (cal.component(.weekday, from: d) - 1 + 7) % 7
    }

    func equals(today: (year: Int, month: Int, day: Int)) -> Bool {
        year == today.year && month == today.month
    }

    static func < (lhs: YearMonth, rhs: YearMonth) -> Bool {
        if lhs.year != rhs.year { return lhs.year < rhs.year }
        return lhs.month < rhs.month
    }
}

#Preview {
    ScheduleView()
        .environmentObject(RouterStore(initial: .schedule))
        .environmentObject(AppStore())
}
