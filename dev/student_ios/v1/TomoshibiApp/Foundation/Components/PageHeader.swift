// PageHeader.swift · L1 Home icon / L2+ back · 长按 0.4s → breadcrumb
// ⭐ Foundation · 导航规则核心

import SwiftUI

struct PageHeader: View {
    let title: String
    var level: Int = 2 // 1 = L1 (显示 Home icon), 2+ = 返回箭头
    var right: AnyView? = nil

    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    var body: some View {
        HStack(spacing: 14) {
            leftButton
            Text(title)
                .font(.system(size: 17, weight: .bold))
                .foregroundStyle(T.ink)
            Spacer()
            if let right { right }
        }
        .padding(.horizontal, 16).padding(.vertical, 12)
    }

    private var leftButton: some View {
        // 原来用 Button + .simultaneousGesture(LongPress)：长按时 Button 的 tap 在松手时
        // 仍会触发 → 既弹面包屑又执行返回（导航双触发，B8）。改用 .onTapGesture +
        // .onLongPressGesture 挂同一视图 —— SwiftUI 里这两者互斥：长按超过时长只触发长按、
        // 不再触发 tap；快按只触发 tap。彻底消除双触发。
        Group {
            if level == 1 {
                Ic.home()
            } else {
                Ic.back()
            }
        }
        .foregroundStyle(T.ink)
        .frame(width: 36, height: 36)
        .contentShape(Rectangle())
        .onTapGesture {
            if level == 1 {
                router.replace(.home)
            } else {
                router.back()
            }
        }
        .onLongPressGesture(minimumDuration: 0.4) {
            let fb = UIImpactFeedbackGenerator(style: .soft)
            fb.impactOccurred()
            app.breadcrumbOpen = true
        }
        .accessibilityAddTraits(.isButton)
        .accessibilityLabel(level == 1 ? "ホーム" : "戻る")
    }
}
