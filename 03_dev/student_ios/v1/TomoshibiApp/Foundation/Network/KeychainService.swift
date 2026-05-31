// KeychainService.swift
// Foundation · Network — JWT token 持久化到 iOS Keychain 的小 wrapper
//
// 为什么用 Keychain 不用 UserDefaults：
//   - JWT token 是机密、UserDefaults 是明文 plist、设备越狱后能直接读
//   - Keychain 是苹果系统加密的安全存储区
//   - kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly = 设备首次解锁后可访问
//     （锁屏后 background 也能用、但不解锁就不能读）
//     ThisDeviceOnly = 不进 iCloud/iTunes 备份、不随备份迁移到别的设备
//     （防代刷场景：登录态不该被带到另一台设备）
//
// 怎么用：
//   KeychainService.save(token: "eyJ...")    // 登录成功后
//   let saved = KeychainService.load()         // app 启动时
//   KeychainService.delete()                   // 登出 / 401

import Foundation
import Security

enum KeychainService {
    // service / account 用唯一标识区分多个 keychain item
    private static let service = "jp.tomoshibi.cc"
    private static let account = "student.jwt"

    /// token 保存（已存在就覆盖）
    static func save(token: String) {
        guard let data = token.data(using: .utf8) else { return }

        // 先删既存（idempotent — 重复 save 也 OK）
        let delQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(delQuery as CFDictionary)

        // 加新 item
        let addQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
        ]
        // SecItemAdd 的返回状态码以前被丢弃 → 写失败时静默返回，
        // app 重启读不到 token、自动登录失效且无从定位（IX-037）。
        // 现在检查状态码：非 errSecSuccess 就打日志，DEBUG 下直接断言暴露。
        let status = SecItemAdd(addQuery as CFDictionary, nil)
        if status != errSecSuccess {
            print("KeychainService.save 失败：OSStatus=\(status)")
            #if DEBUG
                assertionFailure("Keychain token 保存失败 OSStatus=\(status)")
            #endif
        }
    }

    /// token 读取（不存在时 nil）
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

    /// token 删除（登出 / 收到 401 时）
    static func delete() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(query as CFDictionary)
    }
}
