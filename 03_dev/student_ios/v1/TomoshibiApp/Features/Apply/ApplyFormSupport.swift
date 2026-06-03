// ApplyFormSupport.swift
// Features · Apply — 新增申請表单共用的小组件

import SwiftUI

struct ApplyFormSectionLabel: View {
    let n: String
    let label: String

    var body: some View {
        HStack(spacing: 8) {
            Text(n)
                .font(.system(size: 11, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 22, height: 22)
                .background(Circle().fill(T.primary))
            Text(label)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(T.ink)
            Spacer()
        }
        .padding(.bottom, 8)
    }
}

struct ApplyDateField: View {
    @Binding var date: Date
    var minDate: Date? = nil

    var body: some View {
        Group {
            if let minDate {
                DatePicker("", selection: $date, in: minDate..., displayedComponents: .date)
            } else {
                DatePicker("", selection: $date, displayedComponents: .date)
            }
        }
        .labelsHidden()
        .datePickerStyle(.compact)
        .environment(\.locale, Locale(identifier: "ja_JP"))
        .frame(maxWidth: .infinity, minHeight: 42)
        .padding(.horizontal, 8)
        .background {
            RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.paper)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(T.hair, lineWidth: 1)
        }
    }
}

struct ApplyTimeField: View {
    @Binding var date: Date

    var body: some View {
        DatePicker("", selection: $date, displayedComponents: .hourAndMinute)
            .labelsHidden()
            .datePickerStyle(.compact)
            .environment(\.locale, Locale(identifier: "ja_JP"))
            .frame(maxWidth: .infinity, minHeight: 42)
            .padding(.horizontal, 8)
            .background {
                RoundedRectangle(cornerRadius: 10, style: .continuous).fill(T.paper)
            }
            .overlay {
                RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(T.hair, lineWidth: 1)
            }
    }
}

enum ApplyFormDate {
    /// JST 固定日历 —— 让「今天 / N 天后」按日本时间算，不随设备时区漂（跟 formatYMD 固定 JST 配套，Codex 6-03 审出）
    static var tokyoCalendar: Calendar {
        var c = Calendar(identifier: .gregorian)
        c.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
        return c
    }

    static var threeDaysLater: Date {
        let cal = tokyoCalendar
        let today0 = cal.startOfDay(for: Date())
        return cal.date(byAdding: .day, value: 3, to: today0) ?? today0
    }

    static func parseHM(_ s: String) -> Date {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.date(from: s) ?? Date()
    }

    static func formatYMD(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // 固定 JST：否则非 JST 设备 period_from/to 口径偏一天（跟 ApplyStubs.formatYMD / StayList 编辑页一致）
        return f.string(from: d)
    }

    static func formatHM(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.string(from: d)
    }

    static func combineDateAndTimeISO(date: Date, time: Date) -> String {
        let cal = Calendar.current
        let d = cal.dateComponents([.year, .month, .day], from: date)
        let t = cal.dateComponents([.hour, .minute], from: time)
        var c = DateComponents()
        c.year = d.year
        c.month = d.month
        c.day = d.day
        c.hour = t.hour
        c.minute = t.minute
        c.second = 0
        let combined = cal.date(from: c) ?? date
        return ISO8601DateFormatter().string(from: combined)
    }

    static func displayDateTime(_ d: Date) -> String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo")
        return f.string(from: d)
    }

    static func nilIfBlank(_ s: String) -> String? {
        let trimmed = s.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }
}
