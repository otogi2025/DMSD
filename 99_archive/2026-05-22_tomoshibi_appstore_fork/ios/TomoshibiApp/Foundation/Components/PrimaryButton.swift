// PrimaryButton.swift · GhostButton.swift
// ⭐ Foundation · 基础按钮组件

import SwiftUI

/// 主操作按钮 · 对等 JSX PrimaryBtn
/// JSX 规格: height 52 · radius 16 · fontSize 16 · fontWeight 700 · letterSpacing 0.02em
///           bg radial-gradient(circle at 35% 28%, #a8e0e6 0%, #5fbec8 40%, #1f6b74 100%)
///           shadow 0 4px 14px rgba(31,107,116,0.24)
struct PrimaryButton: View {
    let title: String
    var icon: String? = nil
    var enabled: Bool = true
    var destructive: Bool = false
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if let icon { Image(systemName: icon) }
                Text(title)
                    .font(.system(size: 16, weight: .bold))
                    .kerning(0.32)
            }
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 52)
            .background {
                if destructive {
                    RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous)
                        .fill(T.danger)
                } else if !enabled {
                    RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous)
                        .fill(T.inkFaint)
                } else {
                    RadialGradient(
                        colors: [T.accentSoft, T.accent, T.primary],
                        center: UnitPoint(x: 0.35, y: 0.28),
                        startRadius: 0,
                        endRadius: 260
                    )
                    .clipShape(RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous))
                }
            }
            .shadow(
                color: (enabled && !destructive) ? T.primary.opacity(0.24) : .clear,
                radius: 14, x: 0, y: 4
            )
            .contentShape(RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous))
        }
        .buttonStyle(.plain)
        .disabled(!enabled)
    }
}

/// 次操作按钮（描边透明）
struct GhostButton: View {
    let title: String
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 15, weight: .medium))
                .foregroundStyle(T.primary)
                .frame(maxWidth: .infinity)
                .frame(height: 52)
                .background {
                    RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous)
                        .stroke(T.primary.opacity(0.3), lineWidth: 1)
                }
                .contentShape(RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}
