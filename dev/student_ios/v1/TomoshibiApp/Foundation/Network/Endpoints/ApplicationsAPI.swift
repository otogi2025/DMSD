// ApplicationsAPI.swift
// Foundation · Network · Endpoints — 出寮届相关 endpoint 包装
//
// 包 backend 的 /api/v1/applications/* endpoint（学生侧能用的部分）：
//   - POST /applications              create
//   - GET  /applications/mine          listMine
//   - GET  /applications/:id           detail
//   - PUT  /applications/:id           update（修改届）
//   - POST /applications/:id/withdraw  withdraw（撤回）
//   - GET  /applications/:id/audit     audit（改动履历）

import Foundation

enum ApplicationsAPI {
    /// 出寮届提交。body 是 KisheiCreateBody / GaihakuCreateBody / KikokuCreateBody 之一。
    /// backend 按 `kind` 字段 dispatch 到对应 Pydantic schema（discriminated union）。
    @MainActor
    static func create<Body: Encodable>(_ body: Body) async throws -> ApplicationOut {
        return try await APIClient.shared.post(path: "/api/v1/applications", body: body)
    }

    /// 我的申请一览（最近优先）
    @MainActor
    static func listMine() async throws -> [ApplicationOut] {
        return try await APIClient.shared.get(path: "/api/v1/applications/mine")
    }

    /// 申请详细（含承认 chain 全部 step）
    @MainActor
    static func detail(id: UUID) async throws -> ApplicationOut {
        let path = "/api/v1/applications/\(id.uuidString.lowercased())"
        return try await APIClient.shared.get(path: path)
    }

    /// 修改届（pending / approved_partial / returned 状态时可改）
    /// body 全字段 Optional。backend 收到后 chain 全员重置为 pending。
    @MainActor
    static func update(id: UUID, body: ApplicationUpdateBody) async throws -> ApplicationOut {
        let path = "/api/v1/applications/\(id.uuidString.lowercased())"
        return try await APIClient.shared.put(path: path, body: body)
    }

    /// 撤回出寮届（仅 pending / approved_partial / returned 状态可撤回，成功后 status 变 withdrawn）。
    /// 无 body。失败 409 = CANNOT_WITHDRAW（状态不允许）。
    @MainActor
    static func withdraw(id: UUID) async throws -> ApplicationOut {
        let path = "/api/v1/applications/\(id.uuidString.lowercased())/withdraw"
        // 撤回无请求体 —— 传 nil（同 OutingsAPI.withdraw 的写法，APIClient.post 要求 Encodable，String? 满足）
        return try await APIClient.shared.post(path: path, body: nil as String?)
    }

    /// 改动履历（提出 / 修改届 / 役职决定 全部按时序记录）
    @MainActor
    static func audit(id: UUID) async throws -> [AuditLogOut] {
        let path = "/api/v1/applications/\(id.uuidString.lowercased())/audit"
        return try await APIClient.shared.get(path: path)
    }
}
