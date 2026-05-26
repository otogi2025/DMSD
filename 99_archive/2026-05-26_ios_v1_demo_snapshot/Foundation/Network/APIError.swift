// APIError.swift
// Foundation · Network — API エラー型

import Foundation

enum APIError: Error, LocalizedError {
    case network(Error)          // 通信エラー (Wi-Fi 切断など)
    case decode(Error)           // JSON パース失敗
    case unauthorized            // 401 — 再ログイン必要
    case unprocessable(String)   // 422 — 入力エラー (サーバからのメッセージ)
    case server(Int, String)     // 5xx など予期しないエラー
    case unknown

    var errorDescription: String? {
        switch self {
        case .network: return "通信エラーが発生しました。電波を確認してください"
        case .decode: return "データの読み込みに失敗しました"
        case .unauthorized: return "ログインが必要です"
        case .unprocessable(let msg): return msg
        case .server(let code, let msg): return "サーバーエラー (\(code)): \(msg)"
        case .unknown: return "不明なエラー"
        }
    }
}
