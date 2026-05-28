// NetworkModels.swift
// Foundation · Network — backend 响应的 Decodable 模型
//
// 跟 SeedModels.swift（mock fixture）分离。Network = wire format（线缆数据格式），Seed = UI mock。
// 跟 backend Pydantic schema（03_dev/backend/v1/app/schemas.py）byte-perfect 对齐。
//
// 日期方针：
//   - "yyyy-MM-dd" 的 date 类型 → 保 String（JSONDecoder.iso8601 单独 date 会被弾く）
//   - "HH:mm:ss" 的 time 类型 → 保 String
//   - "YYYY-MM-DDTHH:mm:ssZ" 的 datetime 类型 → Date（APIClient 已配 .iso8601）

import Foundation

// MARK: - 学生

/// 申请里嵌入的学生简易信息（GET /applications/:id 响应内）
struct StudentBrief: Decodable, Hashable {
    let id: UUID
    let student_no: String
    let name: String
    let dorm_unit: Int
    let is_overseas: Bool
    let room_no: String
}

// MARK: - 申请

/// 承认 chain 的 1 步（每个役职的决定状态）
struct ApprovalStepOut: Decodable, Hashable {
    let approver_role: String // "担任" / "寮務課長" / "管理係" / 等
    let decision: String? // "approve" | "reject" | nil（未决）
    let decided_at: Date? // ISO 8601 datetime（未决时 nil）
    let comment: String?
    let approver_id: UUID?
}

/// 出寮届详细（POST /applications / GET /applications/:id 响应）
///
/// 按 kind 分字段：
///   - 帰省: stay_locations / meals_skip / flight_* 全 nil
///   - 外泊: stay_locations / meals_skip 有值，flight_* 全 nil
///   - 帰国: 全字段都有值
struct ApplicationOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let student: StudentBrief?

    let kind: String // "帰省" | "外泊" | "帰国"
    let reason: String?
    let contact_phone: String?
    let meal_note: String?
    let companion: String?
    let dest_cities: String?
    let receipt_submitted: Bool?
    let is_long_vacation: Bool?

    // 日期、时刻：backend 用 date / time 类型 → 保 String
    let leave_date: String // "2026-05-03"
    let leave_method: String
    let leave_time: String // "19:40:00"
    let return_date: String
    let return_method: String
    let return_time: String

    // 仅外泊 / 帰国
    let stay_locations: [[String: AnyJSON]]?
    let meals_skip: [[String: AnyJSON]]?

    // 仅帰国
    let flight_dep_air: String?
    let flight_dep_at: Date?
    let flight_arr_air: String?
    let flight_arr_at: Date?

    /// FC-020 (2026-05-24): backend schemas.py:187 ApplicationOut.bus_route_id 一直在，iOS 漏接
    /// 不显示也要保留以免 backend 发出时 decode 整段 fail
    let bus_route_id: UUID?

    let submitted_at: Date
    let status: String // "pending" | "approved_partial" | "approved" | "rejected" | "withdrawn" | "returned"
    let withdrawn_at: Date?
    let approval_chain: [ApprovalStepOut]
}

/// 改动履历 entry（GET /applications/:id/audit）
struct AuditLogOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let actor_type: String // "student" | "teacher"
    let actor_id: UUID?
    let action: String // "application.submit" | "application.approve" | "application.amend" 等
    let payload: [String: AnyJSON]?
    let created_at: Date
}

// MARK: - 学習（晚自习）

/// 学習欠席届（POST /study/absence-requests 响应）
struct StudyAbsenceRequestOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let target_date: String // "2026-05-03"
    let period: String // "first_half" | "second_half" | "full"
    let reason: String
    let submitted_at: Date
    let status: String // "pending" | "approved" | "rejected"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
}

/// 学習オンライン申請（POST /study/online-requests 响应）
struct StudyOnlineRequestOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let reason: String
    let period_from: String
    let period_to: String
    let weekly_schedule: [String: [[String: String]]]
    let contract_ref: String?
    let submitted_at: Date
    let status: String // "pending" | "approved" | "rejected" | "revoked"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
}

// MARK: - 宿舍生活类申請

/// 寮生行事企画申請書（POST /dorm-life/event-proposals 响应）
struct DormEventProposalOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let proposer_id: UUID
    let team_name: String?
    let title: String
    let held_at: Date
    let place: String
    let expected_count: Int
    let target: String
    let purpose: String
    let content: String
    let risk_solution: String
    let expected_cost: String
    let note: String?
    let submitted_at: Date
    let result: String // "pending" | "approved" | "approved_conditional" | "resubmit" | "rejected"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
}

/// 冷蔵庫購入届（POST /dorm-life/fridge-purchases 响应）
struct FridgePurchaseRequestOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let contact_phone: String
    let contact_wechat: String?
    let product: String // "A" | "B"
    let submitted_at: Date
    let delivered_sign: String?
    let status: String // "pending" | "ordered" | "delivered" | "rejected"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
}

/// 物品所持許可願（POST /dorm-life/item-possessions 响应）
struct ItemPossessionRequestOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let room_no: String
    let item: String
    let reason: String
    let guardian_name: String
    let submitted_at: Date
    let status: String // "pending" | "approved" | "rejected"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
}

// MARK: - 学生新规注册（POST /accounts，2026-05-04 加）

/// POST /api/v1/accounts 请求 body
/// 跟 backend StudentAccountCreateIn 对齐（schemas.py）
///
/// A-019 (2026-05-21): 字段 max length 镜像 backend，避免 422 才发现
/// FC-021 (2026-05-24): room_no 从 16 改 8 — backend schemas.py:558 是 max_length=8
/// 参考 backend schemas.StudentAccountCreateIn：name 100 / name_kana 100 / email 200 / phone 32 / room_no 8
struct StudentAccountCreateBody: Encodable {
    let name: String
    let name_kana: String?
    let birthday: String? // "yyyy-MM-dd"，没填传 nil
    let gender: String // "male" or "female"
    let grade_code: String // 2 桁
    let class_code: String // 2 桁
    let seat_no: String // 2 桁
    let category: String // "一般寮生" 等
    let room_no: String // "M101" / "W205" 等
    let dorm_unit: Int // 1 / 2 / 4
    let is_overseas: Bool
    let email: String?
    let phone: String?
    let password: String
    let registration_code: String // 6 桁数字（教师生成、5 分钟有效）

    /// A-019: 客户端 form 校验。返回 nil = OK，否则返回错误信息（日语 UI 显示用）
    func validate() -> String? {
        if name.count > 100 { return "氏名は 100 文字以内で入力してください" }
        if let nameKana = name_kana, nameKana.count > 100 {
            return "氏名カナは 100 文字以内で入力してください"
        }
        if let em = email, em.count > 200 {
            return "メールアドレスは 200 文字以内で入力してください"
        }
        if let ph = phone, ph.count > 32 {
            return "電話番号は 32 文字以内で入力してください"
        }
        if room_no.count > 8 { return "部屋番号は 8 文字以内で入力してください" }
        if password.count < 6 || password.count > 128 {
            return "パスワードは 6〜128 文字で入力してください"
        }
        return nil
    }
}

/// POST /api/v1/accounts 响应（成功 201）
/// 跟 backend StudentAccountCreateOut 对齐
struct StudentAccountCreateResponse: Decodable {
    let accessToken: String
    let tokenType: String // "bearer"
    let expiresIn: Int
    let student: StudentBrief

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
        case student
    }
}

// MARK: - 老师公告（2026-05-04 加，spec system_features.md §7.15）

/// 列表 view 用 — 本文摘要 + 已读状态 + 回复数
struct AnnouncementBrief: Decodable, Identifiable, Hashable {
    let id: UUID
    let title: String
    let bodySummary: String
    let scope: String // "all" / "male" / "female"
    let authorTeacherId: UUID
    let authorTeacherName: String
    let createdAt: Date
    let updatedAt: Date
    let isRead: Bool
    let replyCount: Int

    enum CodingKeys: String, CodingKey {
        case id, title, scope
        case bodySummary = "body_summary"
        case authorTeacherId = "author_teacher_id"
        case authorTeacherName = "author_teacher_name"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case isRead = "is_read"
        case replyCount = "reply_count"
    }
}

/// GET /announcements 响应
struct AnnouncementListResponse: Decodable {
    let items: [AnnouncementBrief]
}

/// 回复条目
struct AnnouncementReplyOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let authorKind: String // "student" or "teacher"
    let authorId: UUID
    let authorName: String
    let body: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id, body
        case authorKind = "author_kind"
        case authorId = "author_id"
        case authorName = "author_name"
        case createdAt = "created_at"
    }
}

/// 详情 view — 本文全文 + 回复列表
struct AnnouncementDetail: Decodable, Hashable {
    let id: UUID
    let title: String
    let body: String
    let scope: String
    let authorTeacherId: UUID
    let authorTeacherName: String
    let createdAt: Date
    let updatedAt: Date
    let replies: [AnnouncementReplyOut]

    enum CodingKeys: String, CodingKey {
        case id, title, body, scope, replies
        case authorTeacherId = "author_teacher_id"
        case authorTeacherName = "author_teacher_name"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

/// GET /announcements/unread-count 响应
struct AnnouncementUnreadCount: Decodable {
    let unreadCount: Int

    enum CodingKeys: String, CodingKey {
        case unreadCount = "unread_count"
    }
}

// MARK: - 自由 JSON 字段

/// backend 用 `dict[str, Any]` 返的字段用的薄 Codable wrapper。
/// stay_locations / meals_skip / audit payload 等形状松散的字段在用。
/// 比较用：保留原值字符串化后的内容。
struct AnyJSON: Decodable, Hashable {
    let value: String

    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let s = try? c.decode(String.self) { value = s }
        else if let i = try? c.decode(Int.self) { value = String(i) }
        else if let d = try? c.decode(Double.self) { value = String(d) }
        else if let b = try? c.decode(Bool.self) { value = String(b) }
        else if c.decodeNil() { value = "" }
        else { value = "" }
    }
}
