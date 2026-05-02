// KeychainService.swift
// Foundation · Network — JWT トークンを iOS Keychain 永続化する小さい wrapper
//
// 为什么用 Keychain 不用 UserDefaults:
//   - JWT トークン是机密、UserDefaults 是明文 plist、设备越狱后能直接读
//   - Keychain 是苹果系统加密的 secure storage、即使 backup 也加密
//   - kSecAttrAccessibleAfterFirstUnlock = 设备首次解锁后可访问
//     （锁屏后 background 也能用、但不解锁就不能读）
//
// 使い方:
//   KeychainService.save(token: "eyJ...")    // login 成功后
//   let saved = KeychainService.load()         // app 起動時
//   KeychainService.delete()                   // logout / 401

import Foundation
import Security

enum KeychainService {

    // service / account 用 unique 标识区分多个 keychain item
    private static let service = "jp.tomoshibi.app"
    private static let account = "student.jwt"

    /// トークン保存（既存ありなら上書き）
    static func save(token: String) {
        guard let data = token.data(using: .utf8) else { return }

        // 先删除既存（idempotent — 重複 save しても OK）
        let delQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(delQuery as CFDictionary)

        // 添加新 item
        let addQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock,
        ]
        SecItemAdd(addQuery as CFDictionary, nil)
    }

    /// トークン読み込み（存在しない時 nil）
    static func load() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess, let data = item as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    /// トークン削除（logout / 401 受け取った時）
    static func delete() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(query as CFDictionary)
    }
}
