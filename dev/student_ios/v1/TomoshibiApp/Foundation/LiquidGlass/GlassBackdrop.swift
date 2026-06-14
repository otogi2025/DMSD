// GlassBackdrop.swift
// ⭐ Foundation · Sheet / Modal 的背景遮罩层（全屏 blur + 暗色 overlay）
// 对等 phaseB_src .glassBackdrop: rgba(15,30,34,0.35)

import SwiftUI

struct GlassBackdrop: View {
    var onTap: () -> Void = {}

    var body: some View {
        Rectangle()
            .fill(T.glassBackdrop)
            .background {
                if #available(iOS 26.0, *) {
                    Color.clear.glassEffect(.clear, in: .rect)
                } else {
                    Rectangle().fill(.ultraThinMaterial)
                }
            }
            .ignoresSafeArea()
            .onTapGesture { onTap() }
            .transition(.opacity)
    }
}
