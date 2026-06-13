// APIError.swift
// Foundation · Network — API 错误类型

import Foundation

enum APIError: Error, LocalizedError {
    case network(Error) // 通信错误（Wi-Fi 断连等）
    case decode(Error) // JSON 解析失败
    case unauthorized // 401 — 需要重新登录
    case unprocessable(String) // 422 — 输入错误（服务器返回的消息）
    case server(Int, String) // 5xx 等意外错误
    case unknown

    var errorDescription: String? {
        switch self {
        case .network: return "通信エラーが発生しました。電波を確認してください"
        case .decode: return "データの読み込みに失敗しました"
        case .unauthorized: return "ログインが必要です"
        case let .unprocessable(msg): return msg
        case let .server(code, msg): return "サーバーエラー (\(code)): \(msg)"
        case .unknown: return "不明なエラー"
        }
    }
}
