// GlassSheet.swift · bottom sheet with Liquid Glass panel
// 不用 SwiftUI 原生 .sheet()（自带背景不可改 + 长按吃事件）
// ⭐ Foundation · 自研 half-sheet

import SwiftUI

struct GlassSheet<Content: View>: View {
    /// 面板内关闭回调（拖动手柄下拉触发）。
    /// 点遮罩关闭由 GlobalOverlays 的 GlassBackdrop 负责，本参数只管面板自身手势，两边不互相替代。
    var onClose: () -> Void = {}
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(spacing: 0) {
            Spacer()
            VStack(spacing: 0) {
                // 拖动手柄：下拉超过阈值 → onClose（与 Backdrop 点遮罩关闭职责分工）
                Capsule()
                    .fill(T.inkMute.opacity(0.3))
                    .frame(width: 36, height: 5)
                    .padding(.top, 10).padding(.bottom, 8)
                    .contentShape(Rectangle())
                    .gesture(
                        DragGesture(minimumDistance: 8)
                            .onEnded { value in
                                if value.translation.height > 40 {
                                    onClose()
                                }
                            }
                    )

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
