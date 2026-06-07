// CleaningAPI.swift
// Foundation · Network · Endpoints — 掃除（清扫）提出履历 endpoint 包装
//
// 后端路由 app/routers/cleaning.py（prefix /api/v1/cleaning）：
//   GET /api/v1/cleaning/me   学生查自己的清扫分配 + 检查结果（按计划日倒序）
//
// 老师端的 GET /cleaning（全部）/ POST /cleaning（分配）/ POST /{id}/inspect（检查）
// 学生 app 不用，本文件只包 /me。
// 模型就近放本文件，复用现有网络底座（APIClient）。

import Foundation

/// GET /cleaning/me 返回的单条清扫分配（对齐后端 schemas.CleaningAssignmentOut）。
/// 学生侧只展示 area / scheduled_date / status / failure_reason，故只解这几个字段 ——
/// 其余（各 datetime / teacher_id / demerit_event_id）Decodable 默认忽略，减少解码面。
struct CleaningAssignmentOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let area: String // 清扫区域（如「廊下 2F」）
    let scheduled_date: String // date "yyyy-MM-dd" → String（纯展示，同日期方针）
    let status: String // "assigned" | "done" | "passed" | "failed" | "skipped"
    let failure_reason: String? // 退回（failed）理由
}

enum CleaningAPI {
    /// 我的清扫提出履历（按计划日倒序）。
    @MainActor
    static func listMine() async throws -> [CleaningAssignmentOut] {
        return try await APIClient.shared.get(path: "/api/v1/cleaning/me")
    }
}
