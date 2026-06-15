// StudentNotificationsAPI.swift
// Foundation · Network · Endpoints — 学生通知中心 feed endpoint 包装
//
// 对应后端 spec §7.13.1（routers/student_notifications.py）:
//   GET  /api/v1/student/notifications        — 拉当前学生的通知 feed
//                                               （老师投稿时勾了「学生に通知する」的 公告/巴士/行事，
//                                                按学生可见范围聚合，时系列 desc）
//   POST /api/v1/student/notifications/read    — 标记一条通知已读（幂等，返回 204）
//
// 公告已读复用 announcement_reads（与公告详情已读同源）；巴士/行事用 student_notification_reads。

import Foundation

enum StudentNotificationsAPI {
    /// 拉学生通知 feed（items + 未読数）。
    @MainActor
    static func feed() async throws -> StudentNotificationFeedOut {
        try await APIClient.shared.get(path: "/api/v1/student/notifications")
    }

    /// 标记一条通知已读。后端返回 204 No Content → 用 postNoContent。
    /// kind ∈ {"announcement","bus","event"}；refId = 该条对应实体的 id。
    @MainActor
    static func markRead(kind: String, refId: UUID) async throws {
        struct Body: Encodable {
            let kind: String
            let ref_id: String
        }
        try await APIClient.shared.postNoContent(
            path: "/api/v1/student/notifications/read",
            body: Body(kind: kind, ref_id: refId.uuidString)
        )
    }
}
