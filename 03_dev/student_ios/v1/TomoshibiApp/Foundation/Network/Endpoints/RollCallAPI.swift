// RollCallAPI.swift
// Foundation · Network · Endpoints — 点呼（roll call）相关 endpoint 包装
//
// A-024 (2026-05-21): 之前 iOS 完全没有 RollCall API client；backend 实装的 8 endpoint
// 学生端实际用的是 POST /checkins（路径 B = iPhone tap BTR）。
// 其他 GET endpoint（today/sessions、board、summary）是教师端用，iOS 学生侧不需要。
//
// 字段对齐：跟 backend schemas.py RollCallCheckinIn / RollCallEventOut 对齐
//   - path_hint 是 A-020 新加，client 显式标路径

import Foundation

enum RollCallAPI {
    /// POST /api/v1/rollcall/sessions/:id/checkins — 学生 BTR tap 入口
    ///
    /// 路径 B（iPhone 静态标签）使用：
    ///   - 用户 tap iPhone-BTR 触发 iOS Universal Link
    ///   - app 拿到 nonce（v1.1+ 起 ECDSA 签名）
    ///   - 调本方法提交 checkin
    @MainActor
    static func checkin(
        sessionId: UUID,
        body: RollCallCheckinBody
    ) async throws -> RollCallEventOut {
        let path = "/api/v1/rollcall/sessions/\(sessionId.uuidString.lowercased())/checkins"
        return try await APIClient.shared.post(path: path, body: body)
    }
}

/// POST /api/v1/rollcall/sessions/:id/checkins 请求 body
///
/// 跟 backend RollCallCheckinIn 对齐（schemas.py）。
/// 字段命名：保持 snake_case 跟 backend byte-perfect 对齐（同 NetworkModels.swift 风格）。
struct RollCallCheckinBody: Encodable {
    let card_uid: String? // 路径 A（NFC 卡 UID）；路径 B 时 nil
    let student_id: UUID? // 路径 B / manual 时学生自身 ID
    let idempotency_key: String? // 路径 B 客户端生成 UUID 防重复
    let status_source: String // "auto_nfc" / "manual_checkin"
    let ts_local: Date? // 客户端时刻；nil 由 backend 用 server time
    let path_hint: String? // "A" / "B" / "manual"（A-020 新加）
}

/// POST /api/v1/rollcall/sessions/:id/checkins 响应
///
/// 跟 backend RollCallEventOut 对齐。
struct RollCallEventOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let base_status: String // "present" / "late" / "absent" / "exempt_range"
    let status_source: String // "auto_nfc" / "manual_checkin" / "teacher_override" / "auto_settle"
    let checked_in_at: Date
    let path_type: String? // "A" / "B" / "manual"
}
