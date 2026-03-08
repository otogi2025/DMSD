import SwiftUI

struct RollCallHistoryHomeView: View {
    @ObservedObject var store: RollCallHistoryStore

    var body: some View {
        NavigationView {
            StateContainerView(state: store.state) {
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        if let overview = store.overview {
                            ScoreSummaryCard(data: overview)
                            StatusLegendView()
                            MonthCalendarView(data: overview)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 14)
                    .padding(.bottom, 120)
                }
            }
            .navigationTitle("点呼历史")
            .navigationBarTitleDisplayMode(.inline)
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

private struct ScoreSummaryCard: View {
    let data: StudentHistoryOverviewData

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 4) {
                Text(totalPointsText)
                    .font(.system(size: 38, weight: .bold))
                    .foregroundColor(.primary)

                Text("累计扣分")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            }

            Divider()

            VStack(alignment: .leading, spacing: 8) {
                thresholdLine(
                    title: "罚扫",
                    remaining: data.remainingToCleaning
                )

                thresholdLine(
                    title: "禁足",
                    remaining: data.remainingToConfinement
                )

                if let nextCleaningAt = data.nextCleaningAt {
                    infoLine(title: "下次罚扫", value: DateTextFormatter.shortDate(nextCleaningAt))
                }

                if let confinementUntil = data.confinementUntil {
                    infoLine(title: "禁足到", value: DateTextFormatter.dateTime(confinementUntil))
                }
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard(cornerRadius: 20)
    }

    private var totalPointsText: String {
        let points = data.totalPoints
        if points.truncatingRemainder(dividingBy: 1) == 0 {
            return String(Int(points))
        }
        return String(format: "%.1f", points)
    }

    private func thresholdLine(title: String, remaining: RemainingThreshold) -> some View {
        (
            Text("\(title)：还差 ") +
            Text("迟到 \(remaining.late) 次").fontWeight(.semibold) +
            Text("，") +
            Text("缺席 \(remaining.absent) 次").fontWeight(.semibold)
        )
        .font(.system(size: 14, weight: .regular))
        .foregroundColor(.primary)
    }

    private func infoLine(title: String, value: String) -> some View {
        HStack(spacing: 6) {
            Text("\(title)：")
                .font(.system(size: 14, weight: .regular))
                .foregroundColor(.secondary)
            Text(value)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.primary)
        }
    }
}

private struct StatusLegendView: View {
    var body: some View {
        HStack(spacing: 16) {
            legendItem(color: .green, text: "正常点呼")
            legendItem(color: .yellow, text: "迟到")
            legendItem(color: .red, text: "缺席")
        }
        .padding(.vertical, 4)
    }

    private func legendItem(color: Color, text: String) -> some View {
        HStack(spacing: 7) {
            Capsule()
                .fill(color)
                .frame(width: 24, height: 4)

            Text(text)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
    }
}

private struct MonthCalendarView: View {
    let data: StudentHistoryOverviewData

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 8), count: 7)
    private let weekTitles = ["日", "一", "二", "三", "四", "五", "六"]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(monthTitle)
                .font(.system(size: 31, weight: .bold))
                .foregroundColor(.primary)

            HStack(spacing: 8) {
                ForEach(weekTitles, id: \.self) { title in
                    Text(title)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity)
                }
            }

            LazyVGrid(columns: columns, spacing: 8) {
                ForEach(dayCells.indices, id: \.self) { index in
                    if let date = dayCells[index] {
                        DayStatusCell(
                            date: date,
                            status: status(for: date),
                            isToday: Calendar.current.isDateInToday(date)
                        )
                    } else {
                        Color.clear
                            .frame(height: 58)
                    }
                }
            }
        }
        .padding(14)
        .glassCard(cornerRadius: 20)
    }

    private var monthTitle: String {
        guard let monthDate else { return data.month }
        return DateTextFormatter.monthTitle(monthDate)
    }

    private var dayCells: [Date?] {
        guard let monthDate else { return [] }

        let calendar = Calendar(identifier: .gregorian)
        let dayRange = calendar.range(of: .day, in: .month, for: monthDate) ?? 1..<1
        let firstDay = calendar.date(from: calendar.dateComponents([.year, .month], from: monthDate)) ?? monthDate
        let firstWeekday = calendar.component(.weekday, from: firstDay)

        var cells: [Date?] = Array(repeating: nil, count: max(0, firstWeekday - 1))

        for day in dayRange {
            if let date = calendar.date(byAdding: .day, value: day - 1, to: firstDay) {
                cells.append(date)
            }
        }

        return cells
    }

    private var monthDate: Date? {
        DateTextFormatter.monthDate(data.month)
    }

    private func status(for date: Date) -> HistoryCalendarDayStatus {
        let key = DateTextFormatter.dayKey(date)
        if let item = data.days.first(where: { $0.date == key }) {
            return item
        }
        return HistoryCalendarDayStatus(date: key, amStatus: .none, pmStatus: .none)
    }
}

private extension View {
    func glassCard(cornerRadius: CGFloat) -> some View {
        self
            .background(
                .regularMaterial,
                in: RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(.white.opacity(0.78), lineWidth: 1)
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [.white.opacity(0.42), .clear],
                            startPoint: .top,
                            endPoint: .center
                        )
                    )
                    .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            )
            .shadow(color: .black.opacity(0.06), radius: 12, x: 0, y: 5)
    }
}

private struct DayStatusCell: View {
    let date: Date
    let status: HistoryCalendarDayStatus
    let isToday: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("\(Calendar.current.component(.day, from: date))")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.primary)
                .padding(.horizontal, 7)
                .padding(.vertical, 2)
                .background(isToday ? Color.blue.opacity(0.2) : Color.clear)
                .clipShape(Capsule())

            VStack(alignment: .leading, spacing: 3) {
                Capsule()
                    .fill(color(for: status.amStatus))
                    .frame(width: 20, height: 4)

                Capsule()
                    .fill(color(for: status.pmStatus))
                    .frame(width: 20, height: 4)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, minHeight: 58, alignment: .topLeading)
    }

    private func color(for slotStatus: AttendanceSlotStatus) -> Color {
        switch slotStatus {
        case .normal:
            return .green
        case .late:
            return .yellow
        case .absent:
            return .red
        case .none:
            return Color.gray.opacity(0.28)
        }
    }
}

private enum DateTextFormatter {
    private static let inputDateTimeFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds, .withColonSeparatorInTimeZone]
        return formatter
    }()

    private static let fallbackInputDateTimeFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withColonSeparatorInTimeZone]
        return formatter
    }()

    private static let shortDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.dateFormat = "yyyy年MM月dd日"
        return formatter
    }()

    private static let dateTimeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.dateFormat = "yyyy年MM月dd日 HH:mm"
        return formatter
    }()

    private static let monthFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()

    private static let monthTitleFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.dateFormat = "M月"
        return formatter
    }()

    private static let dayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 9 * 3600)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()

    static func shortDate(_ iso: String) -> String {
        guard let date = parseISODate(iso) else { return iso }
        return shortDateFormatter.string(from: date)
    }

    static func dateTime(_ iso: String) -> String {
        guard let date = parseISODate(iso) else { return iso }
        return dateTimeFormatter.string(from: date)
    }

    static func monthDate(_ month: String) -> Date? {
        monthFormatter.date(from: "\(month)-01")
    }

    static func monthTitle(_ date: Date) -> String {
        monthTitleFormatter.string(from: date)
    }

    static func dayKey(_ date: Date) -> String {
        dayFormatter.string(from: date)
    }

    private static func parseISODate(_ iso: String) -> Date? {
        if let date = inputDateTimeFormatter.date(from: iso) {
            return date
        }
        return fallbackInputDateTimeFormatter.date(from: iso)
    }
}

#Preview {
    let store = RollCallHistoryStore()
    store.state = .content
    store.overview = StudentHistoryOverviewData(
        month: "2026-02",
        totalPoints: 5,
        remainingToCleaning: RemainingThreshold(late: 8, absent: 4),
        remainingToConfinement: RemainingThreshold(late: 16, absent: 8),
        nextCleaningAt: nil,
        confinementUntil: nil,
        days: [
            HistoryCalendarDayStatus(date: "2026-02-11", amStatus: .late, pmStatus: .normal),
            HistoryCalendarDayStatus(date: "2026-02-12", amStatus: .absent, pmStatus: .none)
        ]
    )

    return RollCallHistoryHomeView(store: store)
}
