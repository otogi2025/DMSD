// GlassCard.swift
// ⭐ Foundation · iOS 26 原生 Liquid Glass wrapper
//
// 依据 itsuki 2026-04-22 Q2 决策: 必须用 iOS 26 `.glassEffect()`，不降级
// Xcode 26 + iOS 26 SDK 完整支持

import SwiftUI

/// Liquid Glass 内容容器（iOS 26 原生）
struct GlassCard<Content: View>: View {
    var radius: CGFloat = T.Radius.lg
    var intensity: GlassIntensity = .regular
    @ViewBuilder var content: () -> Content

    var body: some View {
        content()
            .background {
                glassBackground
            }
            .clipShape(RoundedRectangle(cornerRadius: radius, style: .continuous))
    }

    @ViewBuilder
    private var glassBackground: some View {
        if #available(iOS 26.0, *) {
            // iOS 26 原生 Liquid Glass
            switch intensity {
            case .regular:
                Color.clear.glassEffect(.regular, in: .rect(cornerRadius: radius))
            case .clear:
                Color.clear.glassEffect(.clear, in: .rect(cornerRadius: radius))
            case .strong:
                Color.clear.glassEffect(.regular.tint(T.accent.opacity(0.1)), in: .rect(cornerRadius: radius))
            }
        } else {
            // iOS 25- fallback (不应命中，deploymentTarget 26)
            RoundedRectangle(cornerRadius: radius, style: .continuous)
                .fill(.ultraThinMaterial)
        }
    }
}

enum GlassIntensity {
    case regular
    case clear
    case strong
}
