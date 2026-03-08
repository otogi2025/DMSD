import Foundation
import SwiftUI
import Combine

enum AttendanceSlotStatus: String, Codable {
    case normal
    case late
    case absent
    case none
}

struct RemainingThreshold: Codable {
    let late: Int
    let absent: Int
}

struct HistoryCalendarDayStatus: Codable {
    let date: String
    var amStatus: AttendanceSlotStatus
    var pmStatus: AttendanceSlotStatus
}

struct StudentHistoryOverviewData: Codable {
    let month: String
    let totalPoints: Double
    let remainingToCleaning: RemainingThreshold
    let remainingToConfinement: RemainingThreshold
    let nextCleaningAt: String?
    let confinementUntil: String?
    var days: [HistoryCalendarDayStatus]
}

final class RollCallHistoryStore: ObservableObject {
    @Published var state: ScreenState = .loading
    @Published var overview: StudentHistoryOverviewData?

    private var didLoad = false

    func loadIfNeeded() {
        guard !didLoad else { return }
        didLoad = true
        loadOverview()
    }

    func refreshMonthKeepingLocalTodayState() {
        guard let localOverview = overview else {
            loadOverview()
            return
        }

        let localToday = todaySlotStatus(in: localOverview)

        guard
            let envelope: APIEnvelope<StudentHistoryOverviewData> = MockJSONLoader.load(
                "history_overview",
                as: APIEnvelope<StudentHistoryOverviewData>.self
            ),
            envelope.ok,
            var remote = envelope.data
        else {
            return
        }

        if let localToday {
            mergeTodayStatus(into: &remote, today: localToday)
        }

        overview = remote
        state = remote.days.isEmpty ? .empty : .content
    }

    func applyLocalCheckInSuccess() {
        guard var current = overview else { return }

        let sessionType = currentSessionType()
        let today = Self.dayFormatter.string(from: Date())

        if let index = current.days.firstIndex(where: { $0.date == today }) {
            if sessionType == .morning {
                current.days[index].amStatus = .normal
            } else {
                current.days[index].pmStatus = .normal
            }
        } else {
            let newStatus = HistoryCalendarDayStatus(
                date: today,
                amStatus: sessionType == .morning ? .normal : .none,
                pmStatus: sessionType == .evening ? .normal : .none
            )
            current.days.append(newStatus)
        }

        overview = current
        state = .content
    }

    private func loadOverview() {
        state = .loading

        guard
            let envelope: APIEnvelope<StudentHistoryOverviewData> = MockJSONLoader.load(
                "history_overview",
                as: APIEnvelope<StudentHistoryOverviewData>.self
            )
        else {
            state = .error("未找到 history_overview mock 文件")
            return
        }

        if envelope.ok, let data = envelope.data {
            overview = data
            state = data.days.isEmpty ? .empty : .content
            return
        }

        if let message = envelope.error?.message {
            state = .error(message)
        } else {
            state = .empty
        }
    }

    private func currentSessionType() -> SessionType {
        if
            let envelope: APIEnvelope<StudentHomeData> = MockJSONLoader.load(
                "student_home",
                as: APIEnvelope<StudentHomeData>.self
            ),
            let homeData = envelope.data
        {
            return homeData.sessionType
        }

        let hour = Calendar.current.component(.hour, from: Date())
        return hour < 12 ? .morning : .evening
    }

    private func todaySlotStatus(in overview: StudentHistoryOverviewData) -> HistoryCalendarDayStatus? {
        let today = Self.dayFormatter.string(from: Date())
        return overview.days.first(where: { $0.date == today })
    }

    private func mergeTodayStatus(into remote: inout StudentHistoryOverviewData, today: HistoryCalendarDayStatus) {
        if let index = remote.days.firstIndex(where: { $0.date == today.date }) {
            remote.days[index] = today
        } else {
            remote.days.append(today)
        }
    }

    private static let dayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 9 * 3600)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
}
