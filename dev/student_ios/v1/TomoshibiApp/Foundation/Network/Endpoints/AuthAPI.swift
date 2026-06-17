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
        let student_no: String // 6 桁学号 "060218"
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

    /// DELETE /api/v1/accounts/me — App Store 5.1.1(v) 强制要求的账号删除接口。
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

// MARK: - 当前登录学生（GET /students/me，IX-008，替换 SEED.user 假数据）

/// GET /students/me 响应 — 后端 StudentProfileBasic（学生基本信息）。
/// 只含身份字段；统计（扣分/迟到/欠席）+ 夜学習対象 flag 不在这接口。
struct StudentMeOut: Decodable {
    let id: String
    let student_no: String
    let name: String
    let name_kana: String?
    let grade_code: String
    let class_code: String
    let seat_no: String
    let gender: String
    let category: String
    let room_no: String
    let dorm_unit: Int
    let is_overseas: Bool
    let email: String?
    let phone: String?
    let avatar_url: String?
    let status: String
    /// 学年更新「待更新」标记 — true 时主页顶部显示「更新番号」按钮（spec §4.2）。
    /// Optional 兜底：分阶段部署时若后端未发该字段，避免整个 /me 解码失败。
    let needs_renewal: Bool?
    // registered_at 解码时忽略（Decodable 默认跳过多余字段）
}

/// PATCH /students/me 请求体（对齐后端 StudentSelfUpdate）。
/// 全 Optional —— Swift 合成 Encodable 对 nil Optional 走 encodeIfPresent 自动省略，
/// 故只编码用户实际改了的字段，实现 PATCH「只传要改的」语义。
struct StudentSelfUpdateBody: Encodable {
    let email: String?
    let phone: String?
    let avatar_url: String?
    let room_no: String?
}

enum StudentsAPI {
    /// GET /students/me — 当前登录学生的基本信息。
    /// 仿 teachers/me；后端从令牌取学生，无需传 id。
    @MainActor
    static func me() async throws -> StudentMeOut {
        try await APIClient.shared.get(path: "/api/v1/students/me")
    }

    /// PATCH /students/me — 学生自改联系方式 / 房号（只传非 nil 字段）。
    /// - 撞别人邮箱 → 422 EMAIL_TAKEN；房号前缀跟本人寮不符（男 M*** / 女 W***）→ 422 INVALID_ROOM_FORMAT。
    ///   两种 422 的日语提示由 APIError.unprocessable 原样带出，直接弹给学生。
    /// - 响应是后端 StudentProfileBasic（比 StudentMeOut 多 registered_at）；
    ///   Decodable 默认忽略多余字段 → 直接复用 StudentMeOut 解码。
    /// - APIClient 无 PATCH 便利方法 → 调底层泛型 request（同 OutingsAPI.withdraw 做法）。
    @MainActor
    static func updateMe(_ body: StudentSelfUpdateBody) async throws -> StudentMeOut {
        try await APIClient.shared.request(
            method: "PATCH",
            path: "/api/v1/students/me",
            body: body
        )
    }
}

// MARK: - 番号再設定（学年更新 / 学生自设番号，spec §4.2 — 2026-06-05）

enum StudentRenewalAPI {
    /// POST /api/v1/students/me/renew-number 请求 body — 身份从登录令牌取，不含 student_id。
    struct RenewBody: Encodable {
        let grade_code: String
        let class_code: String
        let seat_no: String
    }

    /// 学生自设番号 — 选新的 学年 / 组 / 出席番号。
    /// 撞号时后端返 422 → APIError.unprocessable(日语提示)，原样弹给学生。
    /// 未开闸（needs_renewal=false）时后端返 409 RENEWAL_NOT_OPEN → 落 APIError.server(409, 日语 msg)，
    ///   msg 仍可经 extractMessage 取出原样展示；正常 UI 只在 needs_renewal=true 时露出本入口，409 属边缘态。
    /// 成功返回更新后的 StudentMeOut（新 student_no + needs_renewal=false）。
    @MainActor
    static func renewNumber(
        gradeCode: String, classCode: String, seatNo: String
    ) async throws -> StudentMeOut {
        let body = RenewBody(
            grade_code: gradeCode, class_code: classCode, seat_no: seatNo
        )
        return try await APIClient.shared.post(
            path: "/api/v1/students/me/renew-number", body: body
        )
    }
}

// MARK: - 当月扣分汇总（GET /discipline/me/summary，IX-008b）

/// GET /discipline/me/summary 响应 — 当前学生当月扣分统计。
/// 与后端 MyDisciplineSummaryOut 对齐：当月总扣分 + 点呼迟到 / 欠席次数。
struct MyDisciplineSummaryOut: Decodable {
    let month: String
    let total_points: Double
    let late_count: Int
    let absent_count: Int
    /// 改动3：罚扫对象 flag — 后端实时算 total_points >= CLEANING_THRESHOLD(4.0)。
    /// 声明成 Bool? + 用处 `?? (total_points >= 4)` 兜底：防后端字段名敲定前 / 旧后端没返该字段时整段 summary 解码失败。
    let needs_cleaning: Bool?
}

enum DisciplineAPI {
    /// GET /discipline/me/summary — 当前登录学生当月扣分汇总（总分 / 迟到 / 欠席）。
    @MainActor
    static func mySummary() async throws -> MyDisciplineSummaryOut {
        try await APIClient.shared.get(path: "/api/v1/discipline/me/summary")
    }
}
