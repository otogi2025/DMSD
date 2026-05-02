// APIClient.swift
// Foundation · Network — HTTP シングルトン
//
// 使い方:
//   let client = APIClient.shared
//   client.token = "eyJ..."          // login 成功後にセット
//   let out: TokenOut = try await client.post("/api/v1/auth/login", body: body)

import Foundation

// MARK: - 設定

/// 開発時は Mac の LAN IP または localhost を使う
/// 本番では TOMOSHIBI_API_URL 環境変数 / Info.plist で上書き
private let DEV_BASE_URL = "http://localhost:8000"

// MARK: - レスポンス型

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

    /// login 後にセット、以降の全リクエストに Authorization: Bearer <token> を付ける
    var token: String?

    private let baseURL: String
    private let session: URLSession

    private init() {
        baseURL = ProcessInfo.processInfo.environment["TOMOSHIBI_API_URL"] ?? DEV_BASE_URL
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 15
        session = URLSession(configuration: config)
    }

    // MARK: - Generic request

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

        guard let http = response as? HTTPURLResponse else {
            throw APIError.unknown
        }

        switch http.statusCode {
        case 200...299:
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
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

    // MARK: - 便利ラッパー

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
}

// MARK: - Helper types

/// backend 的错误响应有 2 种形态，两种都要 decode 来抽取提示信息：
///   1. `{"detail": "字符串"}` — FastAPI 自带 validation error
///   2. `{"detail": {"code": "...", "message": "..."}}` — 自家 raise HTTPException(detail={...}) 形式
private struct DetailError {
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
           let msg = nested.detail.message, !msg.isEmpty {
            return msg
        }
        // 退到形态 1（FastAPI 默认的字符串 detail）
        struct Flat: Decodable { let detail: String }
        if let flat = try? JSONDecoder().decode(Flat.self, from: data),
           !flat.detail.isEmpty {
            return flat.detail
        }
        return nil
    }
}

private struct EmptyResponse: Decodable {}
