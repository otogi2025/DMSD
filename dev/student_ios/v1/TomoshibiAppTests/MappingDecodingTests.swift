// MappingDecodingTests.swift
// 映射与解码 单测（C2 #9-12）
//
// #9  ApplyKindMapper 出寮届 3 kind 正映射（iOS 代码 ↔ backend 日语一一对应；studyAbsence 不在本表）
// #10 未知 kind 走默认分支不崩（后端先行加新申请类时旧版 App 不崩）
// #11 MyRollCallTodaySession 解码：my_status / my_checked_in_at 为 null → 解码成功、可选字段 nil
// #12 关键日期字段 ISO8601 解析（含 JST 时区）→ Date 值精确
//
// #11/#12 直接复用生产解码路径：JSONDecoder + .custom(decodeISO8601Date)
// （decodeISO8601Date 是 APIClient.swift 里的解码函数，测生产真身、不拷副本 → 防测试与生产漂移）。

import Foundation
import Testing
@testable import TomoshibiApp

struct MappingDecodingTests {
    // MARK: - #9 ApplyKindMapper 全 kind 正映射

    @Test("#9 3 个出寮届 kind iOS 代码 ↔ backend 日语一一对应且可往返")
    func applyKindMapperRoundTrips() {
        // 仅 ApplicationsAPI 出寮届三种；studyAbsence 走 StudyAPI，不在本表（ios#102）
        let pairs: [(ios: String, backend: String)] = [
            ("stay", "外泊"),
            ("holiday", "帰省"),
            ("returncountry", "帰国"),
        ]
        for p in pairs {
            #expect(ApplyKindMapper.encode(p.ios) == p.backend) // iOS → backend
            #expect(ApplyKindMapper.decode(p.backend) == p.ios) // backend → iOS
            #expect(ApplyKindMapper.decode(ApplyKindMapper.encode(p.ios)) == p.ios) // 往返回到自身
        }
        // 映射表本身不缺项（后端新增 kind 忘了补 iOS 侧时这里会红）
        #expect(ApplyKindMapper.toBackend.count == 3)
        #expect(ApplyKindMapper.fromBackend.count == 3)
    }

    // MARK: - #10 未知 kind 不崩（走默认分支原样返回）

    @Test("#10 未知 kind 原样透传、不崩（后端先加新申请类，旧版 App 不崩）")
    func unknownKindPassesThrough() {
        #expect(ApplyKindMapper.encode("brandNewKind") == "brandNewKind")
        #expect(ApplyKindMapper.decode("将来の新申請") == "将来の新申請")
        // 空串也走默认分支、不崩
        #expect(ApplyKindMapper.encode("") == "")
        #expect(ApplyKindMapper.decode("") == "")
    }

    // MARK: - #11 MyRollCallTodaySession null 字段解码

    /// 生产同款 JSONDecoder：日期用 .custom(decodeISO8601Date) 策略解码。
    private func makeDecoder() -> JSONDecoder {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .custom(decodeISO8601Date)
        return d
    }

    @Test("#11 my_status / my_checked_in_at 为 null → 解码成功且两字段 nil，非可选日期正常解出")
    func decodeSessionWithNullOptionalFields() throws {
        let json = """
        {
          "session_id": "11111111-1111-1111-1111-111111111111",
          "session_type": "evening",
          "day_type": "weekday",
          "session_status": "running",
          "scheduled_window_start_at": "2026-07-13T21:00:00+09:00",
          "scheduled_on_time_end_at": "2026-07-13T21:10:00+09:00",
          "scheduled_late_end_at": "2026-07-13T21:15:00+09:00",
          "scheduled_auto_end_at": "2026-07-13T21:30:00+09:00",
          "my_status": null,
          "my_checked_in_at": null
        }
        """.data(using: .utf8)!
        let s = try makeDecoder().decode(MyRollCallTodaySession.self, from: json)
        #expect(s.my_status == nil)
        #expect(s.my_checked_in_at == nil)
        #expect(s.session_type == "evening")
        // 非可选日期真被解出（若日期策略挂了这里会抛，不会走到这）
        #expect(within(s.scheduled_window_start_at, utc(2026, 7, 13, 12, 0, 0)))
    }

    @Test("#11 两可选字段整个缺席（key 不存在）也当 nil，不抛")
    func decodeSessionWithOmittedOptionalKeys() throws {
        let json = """
        {
          "session_id": "22222222-2222-2222-2222-222222222222",
          "session_type": "morning",
          "day_type": "weekday",
          "session_status": "draft",
          "scheduled_window_start_at": "2026-07-13T07:00:00+09:00",
          "scheduled_on_time_end_at": "2026-07-13T07:10:00+09:00",
          "scheduled_late_end_at": "2026-07-13T07:15:00+09:00",
          "scheduled_auto_end_at": "2026-07-13T07:30:00+09:00"
        }
        """.data(using: .utf8)!
        let s = try makeDecoder().decode(MyRollCallTodaySession.self, from: json)
        #expect(s.my_status == nil)
        #expect(s.my_checked_in_at == nil)
        #expect(s.session_type == "morning")
    }

    @Test("#11 两可选字段有值时也能解（present + 签到时刻）")
    func decodeSessionWithPresentOptionalFields() throws {
        let json = """
        {
          "session_id": "33333333-3333-3333-3333-333333333333",
          "session_type": "evening",
          "day_type": "weekday",
          "session_status": "running",
          "scheduled_window_start_at": "2026-07-13T21:00:00+09:00",
          "scheduled_on_time_end_at": "2026-07-13T21:10:00+09:00",
          "scheduled_late_end_at": "2026-07-13T21:15:00+09:00",
          "scheduled_auto_end_at": "2026-07-13T21:30:00+09:00",
          "my_status": "present",
          "my_checked_in_at": "2026-07-13T21:05:00+09:00"
        }
        """.data(using: .utf8)!
        let s = try makeDecoder().decode(MyRollCallTodaySession.self, from: json)
        #expect(s.my_status == "present")
        #expect(s.my_checked_in_at != nil)
        if let at = s.my_checked_in_at {
            #expect(within(at, utc(2026, 7, 13, 12, 5, 0))) // 21:05 JST == 12:05 UTC
        }
    }

    // MARK: - #12 ISO8601 JST 时区解析精确性

    @Test("#12 JST +09:00 与等价 Z 串解到同一绝对时刻，且与独立算出的 UTC 参照一致")
    func iso8601JstOffsetHonored() throws {
        // 参照点由 Calendar(UTC) 独立算出（不经 ISO8601DateFormatter）→ 真正的交叉校验
        let reference = utc(2026, 7, 13, 12, 0, 0)
        let json = """
        ["2026-07-13T21:00:00+09:00","2026-07-13T12:00:00Z"]
        """.data(using: .utf8)!
        let dates = try makeDecoder().decode([Date].self, from: json)
        #expect(dates.count == 2)
        // 21:00 JST 必须 == 12:00 UTC（+09:00 偏移被正确减去，不是当成本地/UTC 裸时间）
        #expect(within(dates[0], reference))
        #expect(within(dates[1], reference))
        #expect(within(dates[0], dates[1]))
    }

    @Test("#12 带小数秒（微秒）的 JST 串解析精确到亚秒")
    func iso8601FractionalSecondsParsed() throws {
        let json = """
        ["2026-07-13T21:00:00.500+09:00"]
        """.data(using: .utf8)!
        let dates = try makeDecoder().decode([Date].self, from: json)
        // 12:00:00.500 UTC → 比整点参照晚 0.5 秒（小数秒分支真的解了、没被丢弃）
        #expect(abs(dates[0].timeIntervalSince(utc(2026, 7, 13, 12, 0, 0)) - 0.5) < 0.001)
    }

    @Test("#12 无时区裸时间按 UTC 兜底解析（dev SQLite 无 Z 的历史场景）")
    func iso8601NaiveTreatedAsUTC() throws {
        let json = """
        ["2026-07-13T12:00:00"]
        """.data(using: .utf8)!
        let dates = try makeDecoder().decode([Date].self, from: json)
        // 无 Z / 无偏移 → 兜底按 UTC 解（恢复 DateTime(timezone=True) 本意）
        #expect(within(dates[0], utc(2026, 7, 13, 12, 0, 0)))
    }

    // MARK: - 测试辅助

    /// 由 UTC 日历部件独立构造 Date（不经 ISO8601DateFormatter），供绝对时刻交叉校验。
    private func utc(_ y: Int, _ mo: Int, _ d: Int, _ h: Int, _ mi: Int, _ s: Int) -> Date {
        var comps = DateComponents()
        comps.year = y; comps.month = mo; comps.day = d
        comps.hour = h; comps.minute = mi; comps.second = s
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "UTC")!
        return cal.date(from: comps)!
    }

    /// Date 近似相等（容 0.5ms 浮点误差）。
    private func within(_ a: Date, _ b: Date, _ tol: TimeInterval = 0.0005) -> Bool {
        abs(a.timeIntervalSince(b)) <= tol
    }
}
