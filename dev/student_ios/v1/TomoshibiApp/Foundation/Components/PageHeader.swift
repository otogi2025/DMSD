// PageHeader.swift · L1 Home icon / L2+ back · 长按 0.4s → breadcrumb
// ⭐ Foundation · 导航规则核心

import SwiftUI

struct PageHeader: View {
    let title: String
    var level: Int = 2          // 1 = L1 (显示 Home icon), 2+ = 返回箭头
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

    @ViewBuilder
    private var leftButton: some View {
        Button {
            if level == 1 {
                router.replace(.home)
            } else {
                router.back()
            }
        } label: {
            Group {
                if level == 1 {
                    Ic.home()
                } else {
                    Ic.back()
                }
            }
            .foregroundStyle(T.ink)
            .frame(width: 36, height: 36)
        }
        .simultaneousGesture(
            LongPressGesture(minimumDuration: 0.4)
                .onEnded { _ in
                    let fb = UIImpactFeedbackGenerator(style: .soft)
                    fb.impactOccurred()
                    app.breadcrumbOpen = true
                }
        )
    }
}
