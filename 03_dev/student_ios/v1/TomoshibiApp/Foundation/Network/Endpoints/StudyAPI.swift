// StudyAPI.swift
// Foundation · Network · Endpoints — 学習（晚自习）相关 endpoint 包装
//
// 学生侧能用的:
//   - POST /api/v1/study/absence-requests   学習欠席届 提交
//
// 不在这里的（教师侧 endpoint、学生不会调）:
//   - 教师批准 / 拒否 学習欠席届
//   - 学習出席 NFC tap 提交（backend 待实装）

import Foundation

enum StudyAPI {
    /// POST /api/v1/study/absence-requests 用的请求 body
    struct AbsenceRequestBody: Encodable {
        let target_date: String // "2026-05-03"
        let period: String // "first_half" | "second_half" | "full"
        let reason: String // 申请理由（必填、1-2000 字）
    }

    /// POST /api/v1/study/online-requests 用的请求 body
    struct OnlineRequestBody: Encodable {
        let reason: String
        let period_from: String
        let period_to: String
        let weekly_schedule: [String: [[String: String]]]
        let contract_ref: String?
    }

    /// 学習欠席届提交
    /// - Throws:
    ///   - APIError.unprocessable — 同日重复提交、target_date 范围超过等
    ///   - APIError.unauthorized — 401 → 重新登录
    @MainActor
    static func submitAbsenceRequest(targetDate: String, period: String, reason: String) async throws -> StudyAbsenceRequestOut {
        let body = AbsenceRequestBody(target_date: targetDate, period: period, reason: reason)
        return try await APIClient.shared.post(path: "/api/v1/study/absence-requests", body: body)
    }

    /// 学習オンライン申請 提交
    @MainActor
    static func submitOnlineRequest(body: OnlineRequestBody) async throws -> StudyOnlineRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/study/online-requests", body: body)
    }

    /// 学習オンライン申請 我的列表
    @MainActor
    static func listMyOnlineRequests() async throws -> [StudyOnlineRequestOut] {
        return try await APIClient.shared.get(path: "/api/v1/study/online-requests/mine")
    }

    /// 上传在线学习申请的契約書（合同 = 网课报名凭证）照片 / PDF。
    /// multipart/form-data；先提交申请拿到 id，再调本方法把文件传上去。
    /// - Throws:
    ///   - APIError.unprocessable — 类型不符 / 超大 / 空文件
    ///   - APIError.unauthorized — 401 → 重新登录
    @MainActor
    static func uploadOnlineContract(
        requestId: UUID,
        fileData: Data,
        fileName: String,
        mimeType: String
    ) async throws -> StudyOnlineRequestOut {
        return try await APIClient.shared.upload(
            path: "/api/v1/study/online-requests/\(requestId.uuidString)/contract",
            fileData: fileData,
            fileName: fileName,
            mimeType: mimeType
        )
    }

    /// 下载在线学习申请的契約書文件（二进制：图片 / PDF）。
    /// 不走 APIClient.get（那个按 JSON 解码、二进制会失败）；APIClient.swift 不在本簇可改文件，
    /// 这里自建最小请求，base URL / 鉴权（Bearer token）跟 APIClient 保持一致。
    /// - Throws:
    ///   - APIError.unauthorized — 401 → 重新登录
    ///   - APIError.server(404, _) — 没上传过 / 文件丢失
    @MainActor
    static func downloadOnlineContract(requestId: UUID) async throws -> Data {
        let path = "/api/v1/study/online-requests/\(requestId.uuidString)/contract"
        guard let url = URL(string: apiBaseURL + path) else { throw APIError.unknown }
        var req = URLRequest(url: url)
        if let tok = APIClient.shared.token {
            req.setValue("Bearer \(tok)", forHTTPHeaderField: "Authorization")
        }
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.network(error)
        }
        guard let http = response as? HTTPURLResponse else { throw APIError.unknown }
        switch http.statusCode {
        case 200 ... 299:
            return data
        case 401:
            throw APIError.unauthorized
        default:
            throw APIError.server(http.statusCode, "契約書の取得に失敗しました")
        }
    }

    /// APIClient.baseURL 是 private、且 APIClient.swift 不在本簇可改文件 → 下载二进制（非 JSON）
    /// 这里复制同一套 base URL 规则（DEBUG=localhost / RELEASE=本番 + 环境变量覆盖），与 APIClient 保持一致。
    private static var apiBaseURL: String {
        #if DEBUG
            return ProcessInfo.processInfo.environment["TOMOSHIBI_API_URL"] ?? "http://localhost:8000"
        #else
            return ProcessInfo.processInfo.environment["TOMOSHIBI_API_URL"] ?? "https://api.tomoshibi.cc"
        #endif
    }

    /// GET /api/v1/study/absence-requests/me/summary 响应 — 当前学生当月请假次数。
    /// 与后端 MyAbsenceSummaryOut 对齐（IX-034）。
    struct MyAbsenceSummaryOut: Decodable {
        let month: String
        let count: Int
    }

    /// 当月学習欠席届次数 — 当前登录学生（按 target_date 落当月计数，IX-034）。
    /// 登录 / 启动恢复令牌后调，把 studyLeaveCountThisMonth 从纯内存累加换成真实当月数。
    @MainActor
    static func myAbsenceSummary() async throws -> MyAbsenceSummaryOut {
        return try await APIClient.shared.get(path: "/api/v1/study/absence-requests/me/summary")
    }
}
