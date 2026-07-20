// ReportsAPI.swift
// Foundation · Network · Endpoints — 投稿通報 endpoint 包装
//
// 后端路由 app/routers/reports.py（prefix /api/v1/reports）：
//   POST /api/v1/reports   学生通報一条互见投稿（点歌 / 公告回复 / 遗失物）
//
// App Store 审核指南 1.2 UGC 治理（itsuki 2026-07-20 拍板 A 方案）：
// 学生按「通報」→ 老师在通報一覧确认 → 删投稿或标处理完。
// 老师侧接口（GET / PATCH）是老师网页用的，学生 app 只封装 POST。

import Foundation

/// POST /api/v1/reports 请求 body（对齐后端 ContentReportCreateIn）。
struct ContentReportBody: Encodable {
    let content_type: String // "song" / "announcement_reply" / "lost_found"
    let content_id: UUID
    let reason: String?
}

/// 通報结果（对齐后端 ContentReportOut 的最小子集 — app 只要确认成功，不展示详情）。
struct ContentReportOut: Decodable {
    let id: UUID
    let status: String // "open" / "handled"
}

enum ReportsAPI {
    /// 通報一条投稿。重复通報同一投稿后端幂等返回既有记录（同样走 201）。
    @MainActor
    static func report(contentType: String, contentId: UUID, reason: String? = nil) async throws -> ContentReportOut {
        return try await APIClient.shared.post(
            path: "/api/v1/reports",
            body: ContentReportBody(content_type: contentType, content_id: contentId, reason: reason)
        )
    }
}
