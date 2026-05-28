// StudyAPI.swift
// Foundation · Network · Endpoints — 学習（晚自习）相关 endpoint 包装
//
// 学生侧能用的:
//   - POST /api/v1/study/absence-requests   学習欠席届 提交
//
// 不在这里的（教师侧 endpoint、学生不会调）:
//   - 教师批准 / 拒否 学習欠席届
//   - 学習出席 NFC tap 提交（backend 待实装）

import Foundation

enum StudyAPI {

    /// POST /api/v1/study/absence-requests 用的请求 body
    struct AbsenceRequestBody: Encodable {
        let target_date: String     // "2026-05-03"
        let period: String          // "first_half" | "second_half" | "full"
        let reason: String          // 申请理由（必填、1-2000 字）
    }

    /// POST /api/v1/study/online-requests 用的请求 body
    struct OnlineRequestBody: Encodable {
        let reason: String
        let period_from: String
        let period_to: String
        let weekly_schedule: [String: [[String: String]]]
        let contract_ref: String?
    }

    /// 学習欠席届提交
    /// - Throws:
    ///   - APIError.unprocessable — 同日重复提交、target_date 范围超过等
    ///   - APIError.unauthorized — 401 → 重新登录
    @MainActor
    static func submitAbsenceRequest(targetDate: String, period: String, reason: String) async throws -> StudyAbsenceRequestOut {
        let body = AbsenceRequestBody(target_date: targetDate, period: period, reason: reason)
        return try await APIClient.shared.post(path: "/api/v1/study/absence-requests", body: body)
    }

    /// 学習オンライン申請 提交
    @MainActor
    static func submitOnlineRequest(body: OnlineRequestBody) async throws -> StudyOnlineRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/study/online-requests", body: body)
    }

    /// 学習オンライン申請 我的列表
    @MainActor
    static func listMyOnlineRequests() async throws -> [StudyOnlineRequestOut] {
        return try await APIClient.shared.get(path: "/api/v1/study/online-requests/mine")
    }
}
