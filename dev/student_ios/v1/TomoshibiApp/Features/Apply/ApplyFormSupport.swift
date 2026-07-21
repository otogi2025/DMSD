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
        // 固定 JST 时区+日历：非 JST 设备（留学生回国 UTC+8 等）也按日本时间显示/存储。
        // 否则用户选的钟面时间存成设备时区的绝对时刻，combineDateAndTimeISO 用东京日历提取会偏（codex 审出）。
        .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo")!)
        .environment(\.calendar, ApplyFormDate.tokyoCalendar)
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
            // 固定 JST 时区+日历（同 ApplyDateField）：非 JST 设备也按日本时间，否则时刻偏移（codex 审出）。
            .environment(\.timeZone, TimeZone(identifier: "Asia/Tokyo")!)
            .environment(\.calendar, ApplyFormDate.tokyoCalendar)
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

    /// 今天 0 点（JST 日历锚定）—— 行事企画「実施日時」的最早可选日，避免裸 Date() 随设备时区漂
    static var today: Date {
        tokyoCalendar.startOfDay(for: Date())
    }

    /// 明天 0 点（JST 日历锚定）
    static var tomorrow: Date {
        let cal = tokyoCalendar
        return cal.date(byAdding: .day, value: 1, to: today) ?? today
    }

    static var threeDaysLater: Date {
        let cal = tokyoCalendar
        let today0 = cal.startOfDay(for: Date())
        return cal.date(byAdding: .day, value: 3, to: today0) ?? today0
    }

    /// 解析「HH:mm」为 JST 时刻。
    /// ios#13: 解析失败不再静默吞掉 —— DEBUG/断言打信号；调用方仍拿 Date（当前全传写死合法串）。
    /// 返回 Date（非 Date?）：调用方当前全传写死合法串；原 StayForm.parseHM 已删、口径统一到本函数。
    static func parseHM(_ s: String) -> Date {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // 固定 JST：DatePicker 已固定东京时区，初值字符串也按 JST 解读，否则偏移
        if let d = f.date(from: s) { return d }
        assertionFailure("ApplyFormDate.parseHM 解析失败: \(s)")
        #if DEBUG
            print("[ApplyFormDate.parseHM] 解析失败: \(s)，回退当前时刻")
        #endif
        return Date()
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
        f.timeZone = TimeZone(identifier: "Asia/Tokyo") // 固定 JST，与 DatePicker / parseHM 一致
        return f.string(from: d)
    }

    static func combineDateAndTimeISO(date: Date, time: Date) -> String {
        // 固定 JST（Asia/Tokyo）合成日期时刻，输出带 +09:00 偏移量的 ISO8601 字符串。
        // 原实现用 Calendar.current（设备时区），非 JST 设备（如留学生回国把手机时区改成 UTC+8）
        // 合成的时刻会偏移，提交给后端的 held_at 因此不准确。
        // formatYMD / StayForm 等同文件其他方法已固定 Asia/Tokyo，本函数对齐同一口径。
        let cal = tokyoCalendar
        let d = cal.dateComponents([.year, .month, .day], from: date)
        let t = cal.dateComponents([.hour, .minute], from: time)
        var c = DateComponents()
        c.year = d.year
        c.month = d.month
        c.day = d.day
        c.hour = t.hour
        c.minute = t.minute
        c.second = 0
        c.timeZone = TimeZone(identifier: "Asia/Tokyo")
        let combined = cal.date(from: c) ?? date

        // ISO8601DateFormatter 默认输出 UTC（Z 后缀），此处改用带时区偏移的格式化器
        // 明确保留 +09:00，让后端收到的字符串时区可读、调试清晰。
        let fmt = ISO8601DateFormatter()
        fmt.timeZone = TimeZone(identifier: "Asia/Tokyo") ?? .current
        fmt.formatOptions = [.withInternetDateTime]
        return fmt.string(from: combined)
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
