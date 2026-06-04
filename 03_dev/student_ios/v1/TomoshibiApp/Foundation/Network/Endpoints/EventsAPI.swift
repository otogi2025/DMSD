// EventsAPI.swift
// Foundation · Network · Endpoints — 行事预定（日历「行事予定」页）endpoint 包装
//
// 对应后端 spec §7.5（routers/events.py）:
//   GET /api/v1/events?from_date=&to_date=   — 列日期范围内行事（学生 + 老师都可看）
//
// from_date / to_date 都是可选的「年-月-日」纯日期字符串（"2026-04-01"）。
// 不传 = 后端返回全部行事；传了 = 只返回 event_date 落在 [from_date, to_date] 内的行事。
// 后端返回 { "items": [...] } 包装，这里解包成数组返回（仿 BusAPI.listRoutes）。

import Foundation

enum EventsAPI {
    /// 列行事予定。fromDate / toDate 传 nil = 不加该过滤条件。
    /// 字符串格式必须是后端能解析的纯日期 "yyyy-MM-dd"（由调用方按显示范围算好传入）。
    @MainActor
    static func listEvents(fromDate: String? = nil, toDate: String? = nil) async throws -> [EventOut] {
        var query: [String] = []
        if let fromDate {
            query.append("from_date=\(fromDate)")
        }
        if let toDate {
            query.append("to_date=\(toDate)")
        }
        var path = "/api/v1/events"
        if !query.isEmpty {
            path += "?" + query.joined(separator: "&")
        }
        let out: EventListOut = try await APIClient.shared.get(path: path)
        return out.items
    }
}
