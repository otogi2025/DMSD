// OutingsAPI.swift
// Foundation · Network · Endpoints — 外出申请（当天回寮、单一老师确认）endpoint 包装
//
// 后端路由 app/routers/outings.py（prefix /api/v1/outings）：
//   POST   /api/v1/outings                 提出
//   GET    /api/v1/outings/mine            我的一览（最近优先）
//   GET    /api/v1/outings/{id}            详情
//   PATCH  /api/v1/outings/{id}/withdraw   撤回（仅 pending 状态）
//
// 跟出寮届（applications）的区别：不过夜 / 没有多级审查 / 一名老师点「確認」即可。
// 模型（OutingOut / OutingCreateBody）就近放本文件 —— NetworkModels.swift 不在本会话可改文件；
// 复用 NetworkModels 的 StudentBrief。

import Foundation

/// POST /outings 请求体（对齐后端 schemas.OutingCreateIn）。
/// 日期 / 时刻保 String（同 NetworkModels 日期方针：date "yyyy-MM-dd" / time "HH:mm[:ss]"）。
struct OutingCreateBody: Encodable {
    let outing_date: String // "2026-06-05"（必填）
    let destination: String? // 去向
    let leave_time: String? // 外出时刻 "HH:mm"
    let return_time: String? // 回寮预定时刻（同一天）
    let taxi_reservation_time: String? // 出租车预约时刻；nil = 不预约
    let reason: String?
}

/// 外出申请查询返回（对齐后端 schemas.OutingOut）。
struct OutingOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let student: StudentBrief?
    let outing_date: String // date → String
    let destination: String?
    let leave_time: String? // time → String
    let return_time: String?
    let taxi_reservation_time: String?
    let reason: String?
    let status: String // "pending" | "approved" | "withdrawn"
    // 这几个时刻保 String：仅用于外出申请列表 / 详情的纯展示，不参与计算，直接显示后端原文。
    // （后端已统一输出带 +09:00 日本时间 —— database.py 的 TZDateTime，dev/prod 一致。）
    let submitted_at: String
    let withdrawn_at: String?
    let confirmed_by_teacher_id: UUID?
    let confirmed_by_name: String? // 确认老师的姓名（学生侧显示「確認 · ○○ 先生」）
    let confirmed_at: String?
}

enum OutingsAPI {
    /// 外出申请提出。
    @MainActor
    static func create(_ body: OutingCreateBody) async throws -> OutingOut {
        return try await APIClient.shared.post(path: "/api/v1/outings", body: body)
    }

    /// 我的外出申请一览（最近优先）。
    @MainActor
    static func listMine() async throws -> [OutingOut] {
        return try await APIClient.shared.get(path: "/api/v1/outings/mine")
    }

    /// 外出申请详情。
    @MainActor
    static func detail(id: UUID) async throws -> OutingOut {
        return try await APIClient.shared.get(path: "/api/v1/outings/\(id.uuidString.lowercased())")
    }

    /// 撤回自己 pending 的外出申请。
    /// APIClient 没有 PATCH 便利方法、且 APIClient.swift 不在本簇可改文件 →
    /// 直接调底层泛型 request（撤回无 body、传 nil）。
    @MainActor
    static func withdraw(id: UUID) async throws -> OutingOut {
        return try await APIClient.shared.request(
            method: "PATCH",
            path: "/api/v1/outings/\(id.uuidString.lowercased())/withdraw",
            body: nil as String?
        )
    }
}
