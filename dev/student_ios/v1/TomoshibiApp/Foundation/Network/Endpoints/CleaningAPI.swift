// CleaningAPI.swift
// Foundation · Network · Endpoints — 罚扫（罰則清掃）提出履历 endpoint 包装
//
// 后端路由 app/routers/cleaning.py（prefix /api/v1/cleaning）：
//   GET /api/v1/cleaning/me   学生查自己的罚扫安排 + 检查结果（按计划时刻倒序）
// 老师端的 GET /cleaning / POST /cleaning / POST /{id}/inspect 学生 app 不用，本文件只包 /me。
// 模型就近放本文件，复用现有网络底座（APIClient）。

import Foundation

/// GET /cleaning/me 返回的单条罚扫安排（对齐后端 schemas.CleaningAssignmentOut）。
/// 改动 1：scheduled_date(date) → scheduled_at(datetime)，iOS 直接解成 Date
///         （全局 JSONDecoder 已配 .custom(decodeISO8601Date)，三分支都能解，无需自写 formatter）。
/// 改动 2：area 仍 String，但后端已去枚举校验（老师自由文本），iOS 侧本就当任意文本展示，无需改。
/// 学生侧只展示 area / scheduled_at / status / failure_reason —— 其余字段 Decodable 默认忽略，减少解码面。
struct CleaningAssignmentOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let area: String // 清扫地点（老师自由文本，如「廊下 2F」「玄関まわり」）
    let scheduled_at: Date // 罚扫预定时刻（带时区 datetime，JST 显示）
    let status: String // "assigned" | "done" | "passed" | "failed" | "skipped"
    let failure_reason: String? // 却下（failed）理由
}

enum CleaningAPI {
    /// 我的罚扫提出履历（按计划时刻倒序，后端排好）。
    @MainActor
    static func listMine() async throws -> [CleaningAssignmentOut] {
        try await APIClient.shared.get(path: "/api/v1/cleaning/me")
    }
}

/// 主页「下次罚扫」小卡展示用（演示/正式归一）。
/// AppStore.nextCleaning 计算后给 HomeStubs 的 nextCleaningCard 渲染。
struct NextCleaningInfo: Equatable {
    let dateText: String // "5月20日"
    let timeText: String // "19時00分"（与 AppStore.jstHour 的 H時mm分 口径一致）
    let area: String // "廊下 2F"
}
