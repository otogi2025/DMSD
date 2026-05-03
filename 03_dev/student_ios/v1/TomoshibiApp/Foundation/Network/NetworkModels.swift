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
    let approver_role: String              // "担任" / "寮務課長" / "管理係" / 等
    let decision: String?                   // "approve" | "reject" | nil（未决）
    let decided_at: Date?                   // ISO 8601 datetime（未决时 nil）
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

    let kind: String                        // "帰省" | "外泊" | "帰国"
    let reason: String?

    // 日期、时刻：backend 用 date / time 类型 → 保 String
    let leave_date: String                  // "2026-05-03"
    let leave_method: String
    let leave_time: String                  // "19:40:00"
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

    let submitted_at: Date
    let status: String                      // "pending" | "approved_partial" | "approved" | "rejected" | "withdrawn" | "returned"
    let withdrawn_at: Date?
    let approval_chain: [ApprovalStepOut]
}

/// 改动履历 entry（GET /applications/:id/audit）
struct AuditLogOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let actor_type: String                  // "student" | "teacher"
    let actor_id: UUID?
    let action: String                      // "application.submit" | "application.approve" | "application.amend" 等
    let payload: [String: AnyJSON]?
    let created_at: Date
}

// MARK: - 学習（晚自习）

/// 学習欠席届（POST /study/absence-requests 响应）
struct StudyAbsenceRequestOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let target_date: String                 // "2026-05-03"
    let period: String                      // "first_half" | "second_half" | "full"
    let reason: String
    let submitted_at: Date
    let status: String                      // "pending" | "approved" | "rejected"
    let decided_by: UUID?
    let decided_at: Date?
    let comment: String?
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
