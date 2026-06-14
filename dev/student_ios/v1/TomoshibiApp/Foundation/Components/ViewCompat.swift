//  iOS 16 兼容辅助。
//  最低支持降到 iOS 16（itsuki 2026-06-05 拍板）后，把只有 iOS 17+ 才有的 API
//  包成跨版本工具，老系统退化、新系统照常，既不报错也不留 deprecation 警告。

import SwiftUI

extension View {
    /// onChange 跨版本封装（纯触发版 — 不关心新旧值）。
    /// - iOS 17+：用新版双参数 `onChange(of:) { _, _ in }`
    /// - iOS 16：用老版单参数 `onChange(of:) { _ in }`
    @ViewBuilder
    func onChangeCompat<V: Equatable>(
        of value: V,
        perform action: @escaping () -> Void
    ) -> some View {
        if #available(iOS 17.0, *) {
            onChange(of: value) { _, _ in action() }
        } else {
            onChange(of: value) { _ in action() }
        }
    }

    /// onChange 跨版本封装（带新值版 — 闭包收到变化后的新值）。
    /// - iOS 17+：新版双参数取 newValue
    /// - iOS 16：老版单参数本身就是 newValue
    @ViewBuilder
    func onChangeCompat<V: Equatable>(
        of value: V,
        perform action: @escaping (V) -> Void
    ) -> some View {
        if #available(iOS 17.0, *) {
            onChange(of: value) { _, newValue in action(newValue) }
        } else {
            onChange(of: value) { newValue in action(newValue) }
        }
    }
}
