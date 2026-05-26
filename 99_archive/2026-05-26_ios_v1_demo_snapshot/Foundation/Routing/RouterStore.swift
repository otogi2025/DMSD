// RouterStore.swift
// ⭐ Foundation · Hash-based navigation + stack（对等 phaseB_src 8b866e02 RouterProvider）
// 不用 NavigationStack — 3 按钮 nav + 中央 action + 长按 breadcrumb 需自控栈

import Foundation
import Combine

@MainActor
final class RouterStore: ObservableObject {
    @Published private(set) var current: Route
    @Published private(set) var stack: [Route]

    init(initial: Route = .splash) {
        self.current = initial
        self.stack = [initial]
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

    /// 从 breadcrumb 跳到某一级（若 route 在栈中则截断到该位置）
    func jump(to route: Route) {
        if let idx = stack.firstIndex(of: route) {
            stack = Array(stack.prefix(idx + 1))
            current = route
        } else {
            go(route)
        }
    }

    /// Breadcrumb 显示用：返回 current 之前的层级（不含 current 自己）
    var breadcrumbChain: [Route] {
        guard stack.count > 1 else { return [] }
        return Array(stack.dropLast())
    }
}
