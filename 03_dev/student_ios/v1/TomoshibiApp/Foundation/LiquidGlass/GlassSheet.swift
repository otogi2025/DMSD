// GlassSheet.swift · bottom sheet with Liquid Glass panel
// 不用 SwiftUI 原生 .sheet()（自带背景不可改 + 长按吃事件）
// ⭐ Foundation · 自研 half-sheet

import SwiftUI

struct GlassSheet<Content: View>: View {
    var onClose: () -> Void = {}
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(spacing: 0) {
            Spacer()
            VStack(spacing: 0) {
                // Drag handle
                Capsule()
                    .fill(T.inkMute.opacity(0.3))
                    .frame(width: 36, height: 5)
                    .padding(.top, 10).padding(.bottom, 8)

                content()
                    .padding(.horizontal, 20)
                    .padding(.bottom, 40)
            }
            .frame(maxWidth: .infinity)
            .background {
                if #available(iOS 26.0, *) {
                    Color.clear.glassEffect(.regular, in: .rect(topLeadingRadius: 28, topTrailingRadius: 28))
                } else {
                    UnevenRoundedRectangle(topLeadingRadius: 28, topTrailingRadius: 28, style: .continuous)
                        .fill(T.glassSheet)
                }
            }
            .clipShape(UnevenRoundedRectangle(topLeadingRadius: 28, topTrailingRadius: 28, style: .continuous))
        }
        .ignoresSafeArea(edges: .bottom)
        .transition(.move(edge: .bottom).combined(with: .opacity))
    }
}
