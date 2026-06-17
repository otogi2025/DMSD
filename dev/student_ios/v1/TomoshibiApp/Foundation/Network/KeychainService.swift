// KeychainService.swift
// Foundation · Network — JWT token 持久化到 iOS Keychain 的小 wrapper
//
// 为什么用 Keychain 不用 UserDefaults：
//   - JWT token 是机密、UserDefaults 是明文 plist、设备越狱后能直接读
//   - Keychain 是苹果系统加密的安全存储区
//   - kSecAttrAccessibleWhenUnlockedThisDeviceOnly = 仅设备处于解锁态时可访问
//     （锁屏后即不可读，比 AfterFirstUnlock 更严，token 不在后台锁屏态暴露）
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

        // 匹配用的 query（class + service + account 唯一定位这条）
        let baseQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        // 要写入 / 更新的内容
        let attributes: [String: Any] = [
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        ]

        // codex: 原来先 SecItemDelete 再 SecItemAdd，万一 Add 失败、旧 token 已被删，
        // 持久化里就没 token 了、但内存 authToken 还显示已登录，自动登录直接坏掉。
        // 改成先 SecItemUpdate（旧值在成功覆盖前不动），只有这条还不存在才 Add。
        let updateStatus = SecItemUpdate(baseQuery as CFDictionary, attributes as CFDictionary)
        let status: OSStatus
        if updateStatus == errSecItemNotFound {
            var addQuery = baseQuery
            attributes.forEach { addQuery[$0.key] = $0.value }
            status = SecItemAdd(addQuery as CFDictionary, nil)
        } else {
            status = updateStatus
        }

        // SecItemAdd/Update 的返回状态码以前被丢弃 → 写失败时静默返回，
        // app 重启读不到 token、自动登录失效且无从定位（IX-037）。
        // 清单 #9 + 漏洞E：原来 DEBUG 下 assertionFailure 会中断运行 —— 但 Keychain 写失败多是环境性
        // （模拟器 keychain 偶发不可用 / 首次解锁前不可写 / entitlement 缺 keychain-access-group），
        // 不是代码逻辑 bug，硬断言把外部存储失败伪装成代码崩溃、还打断 Preview / 单测。
        // 降级为可观测日志，且只在 DEBUG 输出（Release 不写日志，避免 OSStatus 进系统日志）。
        if status != errSecSuccess {
            #if DEBUG
                let detail = SecCopyErrorMessageString(status, nil) as String? ?? ""
                print("KeychainService.save 失败：OSStatus=\(status) \(detail)")
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
