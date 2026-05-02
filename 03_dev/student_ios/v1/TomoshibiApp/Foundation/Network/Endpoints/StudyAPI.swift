// StudyAPI.swift
// Foundation · Network · Endpoints — 学習（晚自习）相关 endpoint 包装
//
// 学生侧能用的:
//   - POST /api/v1/study/absence-requests   学習欠席届 提交
//
// 不在这里的（教師侧 endpoint、学生不会调）:
//   - 教師批准 / 拒否 学習欠席届
//   - 学習出席 NFC tap 提交（backend 待实装）

import Foundation

enum StudyAPI {

    /// POST /api/v1/study/absence-requests 用的请求 body
    struct AbsenceRequestBody: Encodable {
        let target_date: String     // "2026-05-03"
        let reason: String          // 申请理由（必填、1-2000 文字）
    }

    /// 学習欠席届提交
    /// - Throws:
    ///   - APIError.unprocessable — 同日重复提交、target_date 范围超过等
    ///   - APIError.unauthorized — 401 → 重新登录
    @MainActor
    static func submitAbsenceRequest(targetDate: String, reason: String) async throws -> StudyAbsenceRequestOut {
        let body = AbsenceRequestBody(target_date: targetDate, reason: reason)
        return try await APIClient.shared.post(path: "/api/v1/study/absence-requests", body: body)
    }
}
