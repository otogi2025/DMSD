// OutingsAPI.swift
// Foundation · Network · Endpoints — 外出申请（当天回寮、单一老师事后确认）endpoint 包装
//
// 后端路由 app/routers/outings.py（prefix /api/v1/outings）：
//   POST   /api/v1/outings                 提出
//   GET    /api/v1/outings/mine            我的一览（最近优先）
//   GET    /api/v1/outings/{id}            详情
//   PATCH  /api/v1/outings/{id}/withdraw   撤回（仅 pending 状态）
//
// 跟出寮届（applications）的区别：不过夜 / 没有多级审查 / 一名老师处理即可。
//
// itsuki 2026-07-22 拍板 — 语义从「事前审批制」改成「事后确认制」（只影响外出，出寮届不动）：
//   - 学生提交后立刻生效可以出门，不用等老师同意；老师点「確認」= 留记录，不是放行开关
//   - 老师仍可「却下」（现实中很少用）：只发通知 + 留记录，不要求学生立刻回寮
//   - 当月扣分 ≥8 分（外出禁止 / 禁足）的学生提交时被后端挡住（422 · code=OUTING_BANNED）
// 模型（OutingOut / OutingCreateBody）就近放本文件 —— NetworkModels.swift 不在本会话可改文件；
// 复用 NetworkModels 的 StudentBrief。

import Foundation

/// POST /outings 请求体（对齐后端 schemas.OutingCreateIn）。
/// 日期 / 时刻保 String（同 NetworkModels 日期方针：date "yyyy-MM-dd" / time "HH:mm[:ss]"）。
struct OutingCreateBody: Encodable {
    let outing_date: String // "2026-06-05"（必填）
    let destination: String? // 去向
    let leave_time: String? // 外出时刻 "HH:mm"
    let return_time: String? // 回寮预定时刻（同一天）
    let taxi_reservation_time: String? // 出租车预约时刻；nil = 不预约
    let reason: String?
}

/// 外出申请查询返回（对齐后端 schemas.OutingOut）。
struct OutingOut: Decodable, Hashable, Identifiable {
    let id: UUID
    let student_id: UUID
    let student: StudentBrief?
    let outing_date: String // date → String
    let destination: String?
    let leave_time: String? // time → String
    let return_time: String?
    let taxi_reservation_time: String?
    let reason: String?
    let status: String // "pending" | "approved" | "rejected" | "withdrawn"
    // DC-01: 保留裸 String（与后端四值 Literal 一致、解码不会因新值崩溃）。显示侧 outingStatusPair 已对未知值
    // 兜底成「不明な状態」，撤回 / 进度处用精确 == 比较 —— 后端将来新增 status 值都不会被误显成已知状态。
    // datetime 用 Date —— 对齐后端 schemas.OutingOut（submitted_at/withdrawn_at/confirmed_at 均 datetime）
    // 与 NetworkModels 其它 datetime 字段同口径；后端统一输出带 +09:00 日本时间（TZDateTime），
    // APIClient 全局 JSONDecoder 配 .custom(decodeISO8601Date) 直接解码（带/不带小数秒都兼容）。
    let submitted_at: Date
    let withdrawn_at: Date?
    // confirmed_by_* / confirmed_at 是「処理した先生 / 処理時刻」——
    // status=approved 时是确认者、status=rejected 时是却下者（事后确认制起共用同一组字段）。
    // 显示文案必须按 status 分支（approved →「確認 · ○○ 先生」/ rejected →「却下 · ○○ 先生」），不能一律写「確認」。
    let confirmed_by_teacher_id: UUID?
    let confirmed_by_name: String? // 处理老师的姓名
    let confirmed_at: Date?
    /// 却下理由 —— 只在 status=rejected 时可能有值（老师没填理由时仍是 nil）。
    let reject_reason: String?
}

enum OutingsAPI {
    /// 外出申请提出。
    @MainActor
    static func create(_ body: OutingCreateBody) async throws -> OutingOut {
        return try await APIClient.shared.post(path: "/api/v1/outings", body: body)
    }

    /// 我的外出申请一览（最近优先）。
    @MainActor
    static func listMine() async throws -> [OutingOut] {
        return try await APIClient.shared.get(path: "/api/v1/outings/mine")
    }

    /// 外出申请详情。
    @MainActor
    static func detail(id: UUID) async throws -> OutingOut {
        return try await APIClient.shared.get(path: "/api/v1/outings/\(id.uuidString.lowercased())")
    }

    /// 撤回自己 pending 的外出申请。
    /// APIClient 没有 PATCH 便利方法、且 APIClient.swift 不在本簇可改文件 →
    /// 直接调底层泛型 request（撤回无 body、传 nil）。
    @MainActor
    static func withdraw(id: UUID) async throws -> OutingOut {
        return try await APIClient.shared.request(
            method: "PATCH",
            path: "/api/v1/outings/\(id.uuidString.lowercased())/withdraw",
            body: nil as String?
        )
    }
}
