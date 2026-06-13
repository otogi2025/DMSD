// APIClient.swift
// Foundation · Network — HTTP 单例
//
// 使用方法:
//   let client = APIClient.shared
//   client.token = "eyJ..."          // login 成功后设置
//   let out: TokenOut = try await client.post("/api/v1/auth/login", body: body)

import Foundation

// MARK: - 配置

// 上架版：DEBUG（Xcode Run）→ localhost / RELEASE（Archive 上架）→ VPS 生产
#if DEBUG
    private let DEFAULT_BASE_URL = "http://localhost:8000"
#else
    private let DEFAULT_BASE_URL = "https://api.tomoshibi.cc"
#endif

// MARK: - 响应类型

struct TokenOut: Decodable {
    let accessToken: String
    let tokenType: String
    let expiresIn: Int

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
    }
}

// MARK: - APIClient

@MainActor
final class APIClient {
    static let shared = APIClient()

    /// login 成功后设置，后续所有请求都会附加 Authorization: Bearer <token>
    var token: String?

    private let baseURL: String
    private let session: URLSession

    private init() {
        baseURL = ProcessInfo.processInfo.environment["TOMOSHIBI_API_URL"] ?? DEFAULT_BASE_URL
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 15
        session = URLSession(configuration: config)
    }

    // MARK: - 通用请求

    func request<Req: Encodable, Res: Decodable>(
        method: String,
        path: String,
        body: Req? = nil as String?
    ) async throws -> Res {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.unknown
        }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let tok = token {
            req.setValue("Bearer \(tok)", forHTTPHeaderField: "Authorization")
        }
        if let body {
            req.httpBody = try JSONEncoder().encode(body)
        }

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: req)
        } catch {
            throw APIError.network(error)
        }

        return try decodeResponse(data: data, response: response)
    }

    /// 共用响应解析 — request（JSON）和 upload（multipart）走同一套状态码 / 解码口径。
    private func decodeResponse<Res: Decodable>(data: Data, response: URLResponse) throws -> Res {
        guard let http = response as? HTTPURLResponse else {
            throw APIError.unknown
        }

        switch http.statusCode {
        case 200 ... 299:
            // 204 No Content（成功但无 body）或 body 为空时，不走 JSON 解码，直接当成功
            // backend 部分 DELETE 接口返回 204，空 body 解码会失败 → 防止误报失败
            if http.statusCode == 204 || data.isEmpty {
                if let empty = EmptyResponse() as? Res {
                    return empty
                }
                // 期望非 EmptyResponse 类型却收到空 body 时才报错
                throw APIError.decode(EmptyBodyError())
            }
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .custom(decodeISO8601Date)
                return try decoder.decode(Res.self, from: data)
            } catch {
                throw APIError.decode(error)
            }
        case 401:
            throw APIError.unauthorized
        case 422:
            let msg = DetailError.extractMessage(from: data) ?? "入力エラー"
            throw APIError.unprocessable(msg)
        default:
            let msg = DetailError.extractMessage(from: data) ?? ""
            throw APIError.server(http.statusCode, msg)
        }
    }

    // MARK: - 便捷包装

    func get<Res: Decodable>(path: String) async throws -> Res {
        try await request(method: "GET", path: path, body: nil as String?)
    }

    func post<Req: Encodable, Res: Decodable>(path: String, body: Req) async throws -> Res {
        try await request(method: "POST", path: path, body: body)
    }

    func put<Req: Encodable, Res: Decodable>(path: String, body: Req) async throws -> Res {
        try await request(method: "PUT", path: path, body: body)
    }

    func delete(path: String) async throws {
        let _: EmptyResponse = try await request(method: "DELETE", path: path, body: nil as String?)
    }

    // MARK: - multipart 文件上传

    /// multipart/form-data 单文件上传（契約書照片 / PDF）。
    /// 手搓 multipart body：边界 + Content-Disposition + 文件字节。响应解析与 request 同口径。
    func upload<Res: Decodable>(
        path: String,
        fileData: Data,
        fileName: String,
        mimeType: String,
        fieldName: String = "file"
    ) async throws -> Res {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.unknown
        }
        let boundary = "Boundary-\(UUID().uuidString)"
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue(
            "multipart/form-data; boundary=\(boundary)",
            forHTTPHeaderField: "Content-Type"
        )
        if let tok = token {
            req.setValue("Bearer \(tok)", forHTTPHeaderField: "Authorization")
        }

        // 文件名直接拼进 Content-Disposition 头 → 含换行 / 引号会破坏 multipart 结构，
        // 先去掉 CR / LF / 双引号（用户选的 PDF 文件名理论上可含这些）
        let safeName = fileName
            .replacingOccurrences(of: "\r", with: "")
            .replacingOccurrences(of: "\n", with: "")
            .replacingOccurrences(of: "\"", with: "")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append(
            "Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(safeName)\"\r\n"
                .data(using: .utf8)!
        )
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        req.httpBody = body

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: req)
        } catch {
            throw APIError.network(error)
        }

        return try decodeResponse(data: data, response: response)
    }
}

// MARK: - 日期解码

/// 兼容「带小数秒」和「不带小数秒」两种后端返回的 ISO8601 时间解码（IX-003）。
///
/// 后端时间默认带微秒（小数秒），系统自带的 .iso8601 不解析小数秒会整段解码失败。
/// 先用支持小数秒的 formatter 试，失败再退回不带小数秒的，两种都不行才抛错。
///
/// formatter 在函数内临时创建（不放全局 / 静态）：ISO8601DateFormatter 非 Sendable，
/// 放全局会触发 Swift 6 并发安全报错；解码不在高频热路径，每次新建开销可忽略。
/// 顶层函数天然不绑主线程，可直接传给 .custom 的 @Sendable 闭包参数。
private func decodeISO8601Date(_ decoder: Decoder) throws -> Date {
    let container = try decoder.singleValueContainer()
    let raw = try container.decode(String.self)

    let withFractional = ISO8601DateFormatter()
    withFractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    if let date = withFractional.date(from: raw) {
        return date
    }

    let noFractional = ISO8601DateFormatter()
    noFractional.formatOptions = [.withInternetDateTime]
    if let date = noFractional.date(from: raw) {
        return date
    }

    // 无时区兜底：开发环境 SQLite 对 DateTime(timezone=True) 弱支持，func.now() 存的是 UTC 裸时间，
    // Pydantic 序列化成 "2026-06-05T14:21:14"（无 Z），上面两个要求带时区的 formatter 都解不出 →
    // 否则整段响应 decode fail（公告 / 申请 / 晚自习 / 点呼等所有 Date 字段都会中，dev 真测确认）。
    // 按 UTC 解释这种裸时间，恢复模型声明 DateTime(timezone=True) 的本意；生产 PostgreSQL 带时区走上面分支。
    let naiveUTC = DateFormatter()
    naiveUTC.locale = Locale(identifier: "en_US_POSIX")
    naiveUTC.timeZone = TimeZone(identifier: "UTC")
    for fmt in ["yyyy-MM-dd'T'HH:mm:ss.SSSSSS", "yyyy-MM-dd'T'HH:mm:ss"] {
        naiveUTC.dateFormat = fmt
        if let date = naiveUTC.date(from: raw) {
            return date
        }
    }

    throw DecodingError.dataCorruptedError(
        in: container,
        debugDescription: "ISO8601 时间格式无法解析: \(raw)"
    )
}

// MARK: - Helper types

/// backend 的错误响应有 2 种形态，两种都要 decode 来抽取提示信息：
///   1. `{"detail": "字符串"}` — FastAPI 自带 validation error
///   2. `{"detail": {"code": "...", "message": "..."}}` — 自家 raise HTTPException(detail={...}) 形式
private enum DetailError {
    static func extractMessage(from data: Data) -> String? {
        // 先试形态 2（自家形式信息量更大）
        struct Nested: Decodable {
            struct Inner: Decodable {
                let code: String?
                let message: String?
            }

            let detail: Inner
        }
        if let nested = try? JSONDecoder().decode(Nested.self, from: data),
           let msg = nested.detail.message, !msg.isEmpty
        {
            return msg
        }
        // 退到形态 1（FastAPI 默认的字符串 detail）
        struct Flat: Decodable { let detail: String }
        if let flat = try? JSONDecoder().decode(Flat.self, from: data),
           !flat.detail.isEmpty
        {
            return flat.detail
        }
        return nil
    }
}

private struct EmptyResponse: Decodable {}

/// 期望有 body 的接口却收到空 body / 204 时抛这个，区别于普通解码失败
private struct EmptyBodyError: Error {}
