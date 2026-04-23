import Foundation

enum SessionType: String, Codable {
    case morning
    case evening
}

enum SessionStatus: String, Codable {
    case draft
    case running
    case ended
}

enum BaseStatus: String, Codable {
    case initial = "init"
    case present
    case late
    case absent
    case exemptRange = "exempt_range"
}

enum OverlayBadge: String, Codable {
    case healthIssue = "health_issue"
    case absenceRequestPending = "absence_request_pending"
}

enum StatusSource: String, Codable {
    case autoNFC = "auto_nfc"
    case autoSettle = "auto_settle"
    case manualCheckin = "manual_checkin"
    case teacherOverride = "teacher_override"
}

struct StudentHomeData: Codable {
    let sessionId: String
    let sessionType: SessionType
    let sessionStatus: SessionStatus
    let serverNow: String
    let effectiveWindowStartAt: String?
    let effectiveOnTimeEndAt: String?
    let effectiveLateEndAt: String?
    let effectiveAutoEndAt: String?
    let remainingSeconds: Int
    let baseStatus: BaseStatus
    let overlayBadges: [OverlayBadge]
    let statusSource: StatusSource
}

struct HistoryDayItem: Codable {
    let date: String
    let calendarStatus: String
}

struct HistoryAnomalyItem: Codable {
    let date: String
    let reason: String
}

struct StudentHistoryMonthData: Codable {
    let month: String
    let dayItems: [HistoryDayItem]
    let anomalyItems: [HistoryAnomalyItem]
}
