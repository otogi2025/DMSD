// LostFoundAPI.swift
// Foundation · Network · Endpoints — 遗失物（UI「遺失物」）endpoint 包装
//
// 后端路由 app/routers/lost_found.py（prefix /api/v1/lost-found）：
//   POST  /api/v1/lost-found              投稿（found 拾得物 / lost 遗失物）
//   GET   /api/v1/lost-found?status=      一览（新→旧；status=open/resolved，不传=全部）
//   PATCH /api/v1/lost-found/{id}/resolve 标为已解决（仅投稿者本人；非本人 403 / 已 resolved 409）

import Foundation

/// POST /api/v1/lost-found 请求 body（对齐后端 LostFoundCreateIn）。
struct LostFoundBody: Encodable {
    let post_type: String // "found"（拾得物）| "lost"（遗失物）
    let item_name: String
    let description: String?
    let location: String?
}

/// 遗失物投稿（对齐后端 LostFoundOut）。
struct LostFoundOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let post_type: String // "found" | "lost"
    let item_name: String
    let description: String?
    let location: String?
    let status: String // "open" | "resolved"
    let created_at: Date // 卡片日期 label 用，格式化展示
    let resolved_at: Date?
}

enum LostFoundAPI {
    /// 遗失物投稿。
    @MainActor
    static func create(_ body: LostFoundBody) async throws -> LostFoundOut {
        return try await APIClient.shared.post(path: "/api/v1/lost-found", body: body)
    }

    /// 遗失物一览（后端按新→旧返回；不传 status = 全部）。
    @MainActor
    static func list() async throws -> [LostFoundOut] {
        return try await APIClient.shared.get(path: "/api/v1/lost-found")
    }

    /// 标为已解决（仅投稿者本人）。APIClient 无 PATCH 便利方法 → 调底层泛型 request（无 body）。
    @MainActor
    static func resolve(id: UUID) async throws -> LostFoundOut {
        return try await APIClient.shared.request(
            method: "PATCH",
            path: "/api/v1/lost-found/\(id.uuidString.lowercased())/resolve",
            body: nil as String?
        )
    }
}
