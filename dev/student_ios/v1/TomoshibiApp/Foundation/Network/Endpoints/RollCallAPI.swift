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
    /// POST /api/v1/rollcall/sessions/:id/checkins
    ///
    /// ⚠️ 架构反转后（2026-06-02 itsuki 拍板，权威 design/flow_design.md §3）学生 app 弃用本方法：
    /// 旧方案（路径 B）= 手机读贴纸拿一次性随机码 nonce → 手机自己 POST 提交 checkin。
    /// 新方案 = 手机不联网，用 CoreNFC 把 student_id 写进墙上 ST25DV Mailbox（见 ST25DVWriter）→
    ///   点呼机读走 → 由点呼机 POST 后端。手机不再直接调本方法。
    /// 保留代码 + 定义（可能给老师代点 / 路径 A 补录用），勿删；学生 app 签到链路已改走 ST25DVWriter。
    @MainActor
    static func checkin(
        sessionId: UUID,
        body: RollCallCheckinBody
    ) async throws -> RollCallEventOut {
        let path = "/api/v1/rollcall/sessions/\(sessionId.uuidString.lowercased())/checkins"
        return try await APIClient.shared.post(path: path, body: body)
    }

    /// GET /api/v1/rollcall/me/today
    ///
    /// 学生查今天自己所属寮的点呼场次 + 自己在每场的签到状态。
    /// iOS 用四个 scheduled_* 时间窗 + 当前时刻真实算出 idle / 进行中倒计时 / 時間内 / 遅刻，
    /// 替代原本地写死的「時間外」「時間内」(R-1/R-2)。空数组 = 本日无我寮点呼。
    @MainActor
    static func myToday() async throws -> [MyRollCallTodaySession] {
        try await APIClient.shared.get(path: "/api/v1/rollcall/me/today")
    }
}

/// GET /api/v1/rollcall/me/today 单条响应（对齐 backend schemas.py MyRollCallTodaySession）。
struct MyRollCallTodaySession: Decodable, Identifiable, Hashable {
    let session_id: UUID
    let session_type: String // morning / evening
    let day_type: String // weekday / weekend_holiday
    let session_status: String // draft / running / ended
    let scheduled_window_start_at: Date
    let scheduled_on_time_end_at: Date
    let scheduled_late_end_at: Date
    let scheduled_auto_end_at: Date
    let my_status: String? // present/late/absent/exempt_range；nil = 还没签到
    let my_checked_in_at: Date?

    var id: UUID {
        session_id
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

// MARK: - 点呼时学生上报（体调不良 / 当次欠席 / 其他问题）— POST /rollcall/reports（功能③）

/// POST /api/v1/rollcall/reports 请求 body（对齐后端 RollCallReportCreateIn）。
struct RollCallReportBody: Encodable {
    let kind: String // "health" | "absence" | "other"
    let body: String // 自由文本 1~2000 字
    let session_id: UUID? // 当前点呼 session；学生端无缓存 → nil（后端 Optional）
}

/// POST /rollcall/reports 响应（对齐后端 RollCallReportOut）。
/// 三个上报弹窗只关心提交成功与否、不渲染返回值，故仅作解码用。
struct RollCallReportOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let session_id: UUID?
    let kind: String
    let body: String
    let created_at: Date
    let resolved_at: Date?
    let resolved_by_teacher_id: UUID?
}

enum RollCallReportsAPI {
    /// 点呼时上报。kind 区分体调（health）/ 当次欠席（absence）/ 其他（other），body 是自由文本。
    @MainActor
    static func create(
        kind: String, body: String, sessionId: UUID? = nil
    ) async throws -> RollCallReportOut {
        let payload = RollCallReportBody(kind: kind, body: body, session_id: sessionId)
        return try await APIClient.shared.post(path: "/api/v1/rollcall/reports", body: payload)
    }

    /// GET /api/v1/rollcall/reports/mine —— 学生查自己提交过的全部上报（后端按时间倒序，含三 kind）。
    /// 「体調報告履歴」只显示 health → 调用方自行 filter kind=="health"（后端不按 kind 过滤）。
    @MainActor
    static func listMine() async throws -> [RollCallReportOut] {
        try await APIClient.shared.get(path: "/api/v1/rollcall/reports/mine")
    }
}
