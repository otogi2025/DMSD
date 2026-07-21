// GlassCard.swift
// ⭐ Foundation · Liquid Glass 内容容器
//
// 最低支持 iOS 16.0（project.yml deploymentTarget，itsuki 2026-06-05 拍板）。
// iOS 26+ 走原生 `.glassEffect()`；iOS 16.0〜25.x 走 `.ultraThinMaterial` fallback（活代码，不能删）。

import SwiftUI

/// Liquid Glass 内容容器（iOS 26+ 原生 glass；更早系统用材质兜底）
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
            // iOS 26+ 原生 Liquid Glass
            switch intensity {
            case .regular:
                Color.clear.glassEffect(.regular, in: .rect(cornerRadius: radius))
            case .clear:
                Color.clear.glassEffect(.clear, in: .rect(cornerRadius: radius))
            case .strong:
                Color.clear.glassEffect(.regular.tint(T.accent.opacity(0.1)), in: .rect(cornerRadius: radius))
            }
        } else {
            // iOS 16.0〜25.x 活代码：最低部署目标是 16，真机会走这里，勿当死代码删
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
