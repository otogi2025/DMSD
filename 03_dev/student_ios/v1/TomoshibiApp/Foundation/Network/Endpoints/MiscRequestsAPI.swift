// MiscRequestsAPI.swift
// Foundation · Network · Endpoints — 杂项申请（修繕 / 来訪者 / 代理受取）endpoint 包装
//
// 后端路由 app/routers/misc_requests.py（prefix /api/v1/misc-requests）：
//   POST  /api/v1/misc-requests              提出（kind: repair 修繕 / guest 来訪者 / proxy_receipt 代理受取）
//   GET   /api/v1/misc-requests/mine         我的一览（学生 app 暂无一览页，未用）
//   PATCH /api/v1/misc-requests/{id}/withdraw 撤回（暂无入口，未用）
//
// 学生 app 当前只用提出 —— iOS 三类申请走 GenericApplyForm（kind: repair / guest / parcel）。
// 其中 iOS「parcel」(UI「代理受取 · 不在時の荷物代理受取」) 对应后端 proxy_receipt。

import Foundation

/// POST /api/v1/misc-requests 请求 body（对齐后端 MiscRequestCreateIn）。
struct MiscRequestBody: Encodable {
    let kind: String // "repair" | "guest" | "proxy_receipt"
    let subject: String
    let detail: String?
    let target_date: String? // date "yyyy-MM-dd"；无则 nil
}

/// 杂项申请（对齐后端 MiscRequestOut）。学生提出后只看是否成功，不渲染返回值。
struct MiscRequestOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let kind: String
    let subject: String
    let detail: String?
    let target_date: String? // date → String
    let status: String // "pending" | "confirmed" | "withdrawn"
    let created_at: Date
}

enum MiscRequestsAPI {
    /// 杂项申请提出。
    @MainActor
    static func create(_ body: MiscRequestBody) async throws -> MiscRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/misc-requests", body: body)
    }
}
