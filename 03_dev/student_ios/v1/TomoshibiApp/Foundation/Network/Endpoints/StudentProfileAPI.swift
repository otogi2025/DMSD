// StudentProfileAPI.swift
// Foundation · Network · Endpoints — 学生个人 profile 聚合查询 endpoint 包装
//
// 后端路由 app/routers/student_profile.py（prefix /api/v1）：
//   GET /api/v1/students/{id}/profile?limit=  学生本人可查自己（聚合多块，各块默认 20、最大 100）
//
// 学生 app 只取其中两块：点呼事件（功能⑦ 点呼履历）+ 减点事件（功能⑧ 減点明細）。
// 自己的 UUID 从 AppStore.myStudentId 取（loadMe 从 /students/me 的 id 填）。

import Foundation

/// 点呼事件 entry（对齐后端 ProfileRollCallEntry）。
struct ProfileRollCallEntry: Decodable, Identifiable, Hashable {
    let id: UUID
    let session_id: UUID
    let session_type: String // "morning" | "evening"
    let base_status: String // "present" | "late" | "absent" | "exempt_range"
    let status_source: String // "auto_nfc" | ...
    let checked_in_at: Date // 派生展示日期 + 打卡时刻，需参与排序 → Date
}

/// 减点事件 entry（对齐后端 ProfileDemeritEntry）。
struct ProfileDemeritEntry: Decodable, Identifiable, Hashable {
    let id: UUID
    let source_type: String
    let points: Double
    let reason: String
    let month: String // "yyyy-MM"（图表按月聚合用）
    let created_at: Date
}

/// GET /students/{id}/profile 聚合响应 —— 学生 app 只解码用得到的两块，
/// 其余（student / applications / study_checkins / guidance_records / study_online_requests）
/// Decodable 默认忽略，减少解码面。
struct StudentProfileOut: Decodable {
    let rollcall_events: [ProfileRollCallEntry]
    let demerit_events: [ProfileDemeritEntry]
}

enum StudentProfileAPI {
    /// 拉学生本人 profile（点呼事件 + 减点事件）。limit 取上限 100 以覆盖更长历史（图表 12 个月用）。
    @MainActor
    static func profile(studentId: String, limit: Int = 100) async throws -> StudentProfileOut {
        return try await APIClient.shared.get(
            path: "/api/v1/students/\(studentId)/profile?limit=\(limit)"
        )
    }
}
