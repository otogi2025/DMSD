// RouterStore.swift
// ⭐ Foundation · Hash-based navigation + stack（对等 phaseB_src 8b866e02 RouterProvider）
// 不用 NavigationStack — 3 按钮 nav + 中央 action + 长按 breadcrumb 需自控栈

import Combine
import Foundation

@MainActor
final class RouterStore: ObservableObject {
    @Published private(set) var current: Route
    @Published private(set) var stack: [Route]

    init(initial: Route = .splash) {
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
