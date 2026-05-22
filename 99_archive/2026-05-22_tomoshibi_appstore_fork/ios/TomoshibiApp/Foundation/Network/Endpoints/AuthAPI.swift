// AuthAPI.swift
// Foundation · Network · Endpoints — 认证相关 endpoint 包装
//
// 包 backend 的 /api/v1/sessions/* endpoint。
// 学生新规注册 POST /api/v1/accounts 的 wrapper 也在本文件（AccountsAPI enum），
// 主题相近（注册 + 登录都是认证流），且避免给 .pbxproj 加单独 file。

import Foundation

enum AuthAPI {

    // MARK: - 学生登录

    /// POST /api/v1/sessions/student 用的请求 body
    struct StudentLoginRequest: Encodable {
        let student_no: String  // 6 桁学号 "060218"
        let password: String
    }

    /// 学生登录。成功返 TokenOut（access_token + token_type + expires_in）
    /// - Throws:
    ///   - APIError.unauthorized — 学号 / 密码错（401）
    ///   - APIError.unprocessable — 学号格式错等（422）
    ///   - APIError.network — 通信失败
    @MainActor
    static func loginStudent(studentNo: String, password: String) async throws -> TokenOut {
        let body = StudentLoginRequest(student_no: studentNo, password: password)
        return try await APIClient.shared.post(path: "/api/v1/sessions/student", body: body)
    }
}

// MARK: - 学生新规注册（POST /accounts，2026-05-04 加，App Store 上架对策）

enum AccountsAPI {

    /// 学生新规注册 — 必须传教师生成的 registration_code（6 桁数字、5 分钟有效）。
    /// 成功 201 → 永久 session JWT + 学生 brief。
    ///
    /// spec: system_features.md §7.16 + BACKEND §5.1.5
    ///
    /// - Throws:
    ///   - APIError.unprocessable（422）— 注册码无效 / 学号重复 / room↔dorm 不对 / email 重复
    ///   - APIError.network — 通信失败
    @MainActor
    static func createAccount(
        body: StudentAccountCreateBody
    ) async throws -> StudentAccountCreateResponse {
        try await APIClient.shared.post(path: "/api/v1/accounts", body: body)
    }

    /// DELETE /api/v1/accounts/me — App Store 5.1.1(v) 强制要求的账号删除端点。
    /// 成功返 204 No Content。调用方收到后把 authToken = nil 触发登出跳转。
    @MainActor
    static func deleteMyAccount() async throws {
        try await APIClient.shared.delete(path: "/api/v1/accounts/me")
    }
}

// MARK: - 老师公告 endpoint（2026-05-04 加，spec §7.15）
//
// 跟 ApplicationsAPI / StudyAPI 一样属于学生面向的功能 endpoint，inline 在本文件
// 是为了避免给 .pbxproj 加新 file。逻辑上独立 — 用 enum AnnouncementsAPI 命名空间隔离。

enum AnnouncementsAPI {

    /// GET /announcements — 列表（按当前学生 scope 自动过滤、新→旧）
    @MainActor
    static func list() async throws -> AnnouncementListResponse {
        try await APIClient.shared.get(path: "/api/v1/announcements")
    }

    /// GET /announcements/unread-count — 主页 badge 用未读数
    @MainActor
    static func unreadCount() async throws -> AnnouncementUnreadCount {
        try await APIClient.shared.get(path: "/api/v1/announcements/unread-count")
    }

    /// GET /announcements/:id — 详情 + 回复（访问时自动写已读）
    @MainActor
    static func detail(id: String) async throws -> AnnouncementDetail {
        try await APIClient.shared.get(path: "/api/v1/announcements/\(id)")
    }

    struct ReplyBody: Encodable {
        let body: String
    }

    /// POST /announcements/:id/replies — 发回复（学生用）
    @MainActor
    static func postReply(
        announcementId: String, body: String
    ) async throws -> AnnouncementReplyOut {
        let req = ReplyBody(body: body)
        return try await APIClient.shared.post(
            path: "/api/v1/announcements/\(announcementId)/replies",
            body: req
        )
    }

    /// DELETE /announcements/:id/replies/:rid — 删自己发的回复
    @MainActor
    static func deleteReply(announcementId: String, replyId: String) async throws {
        try await APIClient.shared.delete(
            path: "/api/v1/announcements/\(announcementId)/replies/\(replyId)"
        )
    }
}
