// ScheduleStubs.swift · 行事予定 月历
// ⭐ 会话 C · 老師 38 条 #9「行事予定の表示（参考用）」+ Q9「現有日历不够要加强」
//
// API 対応（B 未到位 → SEED.events 使用）:
//   GET /events?from=&to=    → ScheduleView          (system_features §7.5)
//
// 既存の demo 用 EventsView（CommunityStubs.swift）との違い:
//   - demo EventsView: 4 月 / 5 月 のみハードコード
//   - 本 ScheduleView: SEED.events から自動的に月レンジを算出 → 任意月にスクロール
//   - イベント詳細は既存 EventDetailView を再利用（router.go(.homeEventDetail(id:))）

import SwiftUI

struct ScheduleView: View {
    @EnvironmentObject var router: RouterStore

    /// 表示中の月（YearMonth）
    @State private var ym: YearMonth = ScheduleView.initialYearMonth()

    /// 選択された日（同じ月の中で nil 不可になったら 1）
    @State private var selectedDay: Int = ScheduleView.initialDay()

    private var monthRange: ClosedRange<YearMonth> {
        let all = SEED.events.compactMap { YearMonth(from: $0.date) }
        guard let lo = all.min(), let hi = all.max() else {
            return YearMonth(year: 2026, month: 4)...YearMonth(year: 2026, month: 5)
        }
        return lo...hi
    }

    var body: some View {
        VStack(spacing: 0) {
            PageHeader(title: "行事予定", level: 2)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    calendarCard
                    selectedDaySection
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .padding(.bottom, 28)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(T.pearl.ignoresSafeArea())
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
            ForEach(0..<ym.firstWeekdayIndex, id: \.self) { _ in
                Color.clear.aspectRatio(1, contentMode: .fit)
            }
            // 当月の日
            ForEach(1...ym.daysInMonth, id: \.self) { day in
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
                            ForEach(0..<min(evs.count, 3), id: \.self) { _ in
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

    private var canGoBack: Bool { ym > monthRange.lowerBound }
    private var canGoForward: Bool { ym < monthRange.upperBound }

    private func stepMonth(_ delta: Int) {
        let next = ym.advanced(by: delta)
        guard monthRange.contains(next) else { return }
        ym = next
        selectedDay = min(selectedDay, next.daysInMonth)
    }

    private var eventsInMonth: Int {
        SEED.events.filter { isInMonth($0.date) }.count
    }

    private func isInMonth(_ s: String) -> Bool {
        guard let other = YearMonth(from: s) else { return false }
        return other == ym
    }

    private func eventsForDay(_ day: Int) -> [EventItem] {
        let dateStr = String(format: "%d-%02d-%02d", ym.year, ym.month, day)
        return SEED.events.filter { $0.date == dateStr }
    }

    private func weekdayColor(_ d: String) -> Color {
        switch d {
        case "日": return T.danger
        case "土": return T.primary
        default:   return T.inkMute
        }
    }

    // MARK: 「今日」「初期月」の決定（demo: 2026-04-23 既存 EventsView と同じ基準）

    private static let today = (year: 2026, month: 4, day: 23)

    private static func initialYearMonth() -> YearMonth {
        YearMonth(year: today.year, month: today.month)
    }
    private static func initialDay() -> Int { today.day }
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
