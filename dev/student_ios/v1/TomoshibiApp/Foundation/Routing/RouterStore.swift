// RouterStore.swift
// ⭐ Foundation · Hash-based navigation + stack（对等 phaseB_src 8b866e02 RouterProvider）
// 不用 NavigationStack — 3 按钮 nav + 中央 action + 长按 breadcrumb 需自控栈

import Combine
import Foundation

@MainActor
final class RouterStore: ObservableObject {
    @Published private(set) var current: Route
    @Published private(set) var stack: [Route]

    /// 「介绍页看过没」标记在手机本地小仓库（UserDefaults）里的键名 —— OnboardingView 的 @AppStorage 共用同一个键
    static let onboardingSeenKey = "hasSeenOnboarding"

    /// app 打开时的第一个页面。
    /// 原来先放 2.2 秒启动闪屏（.splash）再由它判断跳哪 —— 2026-07-22 itsuki 拍板「太丑也没必要」，
    /// 闪屏整个删掉，判断挪到这里，打开 app 直接落在该去的页面上。
    ///
    /// 演示版（Demo scheme）：永远从介绍页开始 —— itsuki 拿它给人演示，每次打开都要能完整走一遍新用户流程。
    /// 正式版：已登录 → 主页；没登录且本机没看过介绍 → 介绍页；否则 → 登录页（跟原闪屏里的判断一模一样）。
    static func launchRoute() -> Route {
        #if DEMO
            return .onboarding
        #else
            if AppStore.shared.authToken != nil { return .home }
            if !UserDefaults.standard.bool(forKey: onboardingSeenKey) { return .onboarding }
            return .login
        #endif
    }

    init(initial: Route = RouterStore.launchRoute()) {
        current = initial
        stack = [initial]
    }

    /// 推入新 route
    func go(_ route: Route) {
        stack.append(route)
        current = route
    }

    /// 回退一级（若为单元素则不动，feature view 自行决定如何处理）
    func back() {
        guard stack.count > 1 else { return }
        stack.removeLast()
        current = stack.last ?? .home
    }

    /// 替换栈（跳到 tab root 用）
    func replace(_ route: Route) {
        stack = [route]
        current = route
    }

    /// 从 breadcrumb 跳到指定层级 —— 按栈中的实际索引截断。
    /// breadcrumbChain == stack.dropLast()，所以面包屑第 idx 项就是 stack[idx]。
    /// 原 jump(to:) 用 firstIndex(of:) 值查找，栈里有重复 Route（如两条路径都进过 .myInfo）
    /// 时会截到第一个、跳错层级；改成按 idx 截断，免疫重复。
    func jump(toIndex idx: Int) {
        guard idx >= 0, idx < stack.count else { return }
        stack = Array(stack.prefix(idx + 1))
        current = stack[idx]
    }

    /// Breadcrumb 显示用：返回 current 之前的层级（不含 current 自己）
    var breadcrumbChain: [Route] {
        guard stack.count > 1 else { return [] }
        return Array(stack.dropLast())
    }
}
