// AuthAPI.swift
// Foundation · Network · Endpoints — 认证相关 endpoint 包装
//
// 包 backend 的 /api/v1/sessions/* endpoint。
// 学生注册（4 step）backend 还没实装（F6），暂不在这里。

import Foundation

enum AuthAPI {

    // MARK: - 学生登录

    /// POST /api/v1/sessions/student 用的请求 body
    struct StudentLoginRequest: Encodable {
        let student_no: String  // "060218" 6 桁
        let password: String
    }

    /// 学生登录。成功返 TokenOut（access_token + token_type + expires_in）
    /// - Throws:
    ///   - APIError.unauthorized — 学号 / 密码错（401）
    ///   - APIError.unprocessable — 学号格式错等（422）
    ///   - APIError.network — 通信失败
    @MainActor
    static func loginStudent(studentNo: String, password: String) async throws -> TokenOut {
        let body = StudentLoginRequest(student_no: studentNo, password: password)
        return try await APIClient.shared.post(path: "/api/v1/sessions/student", body: body)
    }
}
