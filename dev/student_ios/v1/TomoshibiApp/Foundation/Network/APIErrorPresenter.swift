// APIErrorPresenter.swift
// Foundation · Network — 把 APIError 转成日语用户提示的统一 helper
//
// 用途：StayList / MyPage / 申請詳細 等多处 catch 分支需要给用户看日语提示，
// 之前每处 catch 都手写一份 switch，文案散乱。本 helper 统一文案 + .unprocessable
// 走 backend 真错误 message + 其他 case 给固定友好提示。

import Foundation

@MainActor
enum APIErrorPresenter {
    /// 把 APIError 转成日语用户提示
    /// - Parameters:
    ///   - error: catch 拿到的 Error（非 APIError 也接受，走 fallback）
    ///   - fallback: 非 APIError 或 .unknown 时显示的文案（每个调用点按场景写）
    /// - Returns: 日语用户提示字符串
    static func userMessage(for error: Error, fallback: String) -> String {
        guard let api = error as? APIError else { return fallback }
        switch api {
        case .unauthorized:
            return "ログインが必要です。再度ログインしてください。"
        case .network:
            return "通信エラーが発生しました。電波を確認してください。"
        case let .server(code, _):
            return "サーバーエラー（コード \(code)）。時間をおいて再度お試しください。"
        case let .unprocessable(msg):
            // backend 返的具体校验错误 message（422 时是 backend 写好的日语提示）直接显示
            return msg
        case .decode:
            return "データの読み込みに失敗しました。"
        case .unknown:
            return fallback
        }
    }
}
