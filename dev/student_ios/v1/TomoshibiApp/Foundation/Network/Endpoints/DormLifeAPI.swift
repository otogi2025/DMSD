// DormLifeAPI.swift
// Foundation · Network · Endpoints — 宿舍生活类申請 endpoint 包装

import Foundation

enum DormLifeAPI {
    struct EventProposalBody: Encodable {
        let team_name: String?
        let title: String
        let held_at: String
        let place: String
        let expected_count: Int
        let target: String
        let purpose: String
        let content: String
        let risk_solution: String
        let expected_cost: String
        let note: String?
    }

    struct FridgePurchaseBody: Encodable {
        let contact_phone: String
        let contact_wechat: String?
        let product: String
    }

    struct ItemPossessionBody: Encodable {
        let room_no: String
        let item: String
        let reason: String
        let guardian_name: String
    }

    @MainActor
    static func submitEventProposal(body: EventProposalBody) async throws -> DormEventProposalOut {
        return try await APIClient.shared.post(path: "/api/v1/dorm-life/event-proposals", body: body)
    }

    @MainActor
    static func listMyEventProposals() async throws -> [DormEventProposalOut] {
        return try await APIClient.shared.get(path: "/api/v1/dorm-life/event-proposals/mine")
    }

    /// 行事企画 再提出（仅 result == "resubmit" 的企画可重提，成功后 result 回 pending）。
    /// body 与 create 同（EventProposalBody 全字段）。失败 409 = CANNOT_RESUBMIT（状态不允许）。
    @MainActor
    static func resubmitEventProposal(id: UUID, body: EventProposalBody) async throws -> DormEventProposalOut {
        let path = "/api/v1/dorm-life/event-proposals/\(id.uuidString.lowercased())/resubmit"
        return try await APIClient.shared.post(path: path, body: body)
    }

    @MainActor
    static func submitFridgePurchase(body: FridgePurchaseBody) async throws -> FridgePurchaseRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/dorm-life/fridge-purchases", body: body)
    }

    @MainActor
    static func listMyFridgePurchases() async throws -> [FridgePurchaseRequestOut] {
        return try await APIClient.shared.get(path: "/api/v1/dorm-life/fridge-purchases/mine")
    }

    @MainActor
    static func submitItemPossession(body: ItemPossessionBody) async throws -> ItemPossessionRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/dorm-life/item-possessions", body: body)
    }

    @MainActor
    static func listMyItemPossessions() async throws -> [ItemPossessionRequestOut] {
        return try await APIClient.shared.get(path: "/api/v1/dorm-life/item-possessions/mine")
    }
}
