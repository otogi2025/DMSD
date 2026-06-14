// TomoshibiApp.swift
// ⭐ App entry · Foundation agent owns this file (Frozen after D1)
//
// 依据 03_dev/student_ios/IOS_DESIGN_LOG.md
// 架构: @main App → RootView with @StateObject router + app
// 全局 overlays (sheet / breadcrumb / toast) 挂在 RootView 内部 ZStack

import SwiftUI
import UIKit
import UserNotifications

@main
struct TomoshibiApp: App {
    // APNs（苹果推送）回调只能走 UIKit 的 AppDelegate —— SwiftUI 纯 App 生命周期没有，
    // 用 @UIApplicationDelegateAdaptor 桥接。
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @StateObject private var router = RouterStore()
    /// 用单例 —— AppDelegate 的 push 回调要写进界面读的同一个 AppStore（IX-009）。
    @StateObject private var app = AppStore.shared

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(router)
                .environmentObject(app)
                // ⚠️ N18（IOS_DESIGN_LOG §6.5）= 暗色模式「做」但未实装。
                // 暂强制 light，避免系统 dark → SwiftUI 反色 + 黑闪。N18 实装时改回 `.preferredColorScheme(app.isDark ? .dark : nil)`
                .preferredColorScheme(.light)
        }
    }
}

/// APNs（苹果推送）回调处理（IX-009）。
/// 职责：① 请求推送权限 ② 注册成功拿 deviceToken → 上报后端 ③ 收到 push → 进通知列表。
/// ⚠️ 真机收推送还需 itsuki 在 Apple Developer 后台申请 APNs 证书(.p8) 配后端；
///    entitlements 的 aps-environment 已就绪，不用改 project.yml。
final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    func application(
        _: UIApplication,
        didFinishLaunchingWithOptions _: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        #if !DEMO
            // 演示构建不弹推送权限、不连 APNs。
            Task { await Self.requestPushAuthorization() }
        #endif
        return true
    }

    /// 请求推送权限 → 同意才向 APNs 注册（苹果审核要求：必须可被用户拒绝）。
    @MainActor
    private static func requestPushAuthorization() async {
        let center = UNUserNotificationCenter.current()
        do {
            let granted = try await center.requestAuthorization(options: [.alert, .badge, .sound])
            guard granted else { return } // 用户拒绝 → 不注册
            UIApplication.shared.registerForRemoteNotifications()
        } catch {
            // 权限请求失败静默 —— 下次启动再试。
        }
    }

    /// APNs 注册成功 → deviceToken（Data）转 hex 字符串上报后端。
    func application(
        _: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let hex = deviceToken.map { String(format: "%02x", $0) }.joined()
        Task { await AppStore.shared.registerDeviceToken(hex) }
    }

    /// APNs 注册失败（无证书 / 无网络 / 模拟器未登录 Apple ID 等）—— 打日志、不崩。
    func application(
        _: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        #if DEBUG
            print("[APNs] 远程通知注册失败：\(error.localizedDescription)")
        #endif
    }

    /// app 在前台时收到 push —— 仍弹横幅 + 进通知列表。
    /// nonisolated：UNUserNotificationCenterDelegate 回调非主线程隔离，内部用 Task @MainActor 切回。
    nonisolated func userNotificationCenter(
        _: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        handleIncoming(notification)
        completionHandler([.banner, .badge, .sound])
    }

    /// 用户点击 push 打开 app。
    nonisolated func userNotificationCenter(
        _: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        handleIncoming(response.notification)
        completionHandler()
    }

    /// 把 APNs payload 转成通知卡插进列表。
    /// payload 的 userInfo 可带 "type"（"申請" / "減点" / "宅配" 等），缺省按「お知らせ」。
    private nonisolated func handleIncoming(_ notification: UNNotification) {
        let content = notification.request.content
        // 在 nonisolated 上下文先取出 Sendable 的 String 字段 —— 不要把非 Sendable 的
        // content 整个捕获进 @MainActor Task（否则触发 sending data race 编译错误）。
        let type = (content.userInfo["type"] as? String) ?? "お知らせ"
        let title = content.title
        let body = content.body
        Task { @MainActor in
            AppStore.shared.handleIncomingPush(type: type, title: title, body: body)
        }
    }
}
