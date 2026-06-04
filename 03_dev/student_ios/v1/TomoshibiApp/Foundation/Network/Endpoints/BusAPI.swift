// BusAPI.swift
// Foundation · Network · Endpoints — 巴士便（寮生特別運行 / 平日上下学班车）endpoint 包装
//
// 对应后端 spec §7.6:
//   GET /api/v1/bus/routes            — 列巴士便（学生 + 老师都可看）
//   GET /api/v1/bus/routes?kind=...   — 按种类过滤（daily_commute / dorm_special）

import Foundation

enum BusAPI {
    /// 列巴士便。kind 传 nil = 全部；传 "dorm_special" / "daily_commute" = 只看该种类。
    /// 后端返回 { "items": [...] } 包装，这里解包成数组返回。
    @MainActor
    static func listRoutes(kind: String? = nil) async throws -> [BusRouteOut] {
        var path = "/api/v1/bus/routes"
        if let kind {
            path += "?kind=\(kind)"
        }
        let out: BusRouteListOut = try await APIClient.shared.get(path: path)
        return out.items
    }
}
