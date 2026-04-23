import Foundation

enum APIErrorCode: String, Codable {
    case unauthorized = "UNAUTHORIZED"
    case forbidden = "FORBIDDEN"
    case invalidInput = "INVALID_INPUT"
    case notFound = "NOT_FOUND"
    case sessionNotRunning = "SESSION_NOT_RUNNING"
    case timeout = "TIMEOUT"
    case duplicateRequest = "DUPLICATE_REQUEST"
    case alreadyRunning = "ALREADY_RUNNING"
    case unknown = "UNKNOWN"
}

enum APIErrorMessageMap {
    static func message(for code: APIErrorCode) -> String {
        switch code {
        case .timeout:
            return "点呼已截止"
        case .sessionNotRunning:
            return "老师还没开始点呼"
        case .duplicateRequest:
            return "已提交过，请勿重复提交"
        case .unauthorized:
            return "登录已失效，请重新登录"
        case .forbidden:
            return "你没有该操作权限"
        case .invalidInput:
            return "提交内容有误，请检查后重试"
        case .notFound:
            return "数据不存在或已被删除"
        case .alreadyRunning:
            return "点呼已在进行中"
        case .unknown:
            return "系统繁忙，请稍后重试"
        }
    }

    static func message(for rawCode: String?) -> String {
        guard let rawCode, let code = APIErrorCode(rawValue: rawCode) else {
            return message(for: .unknown)
        }
        return message(for: code)
    }
}
