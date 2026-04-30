// BottomNav.swift · 3 tab + 中央 ⭐点呼 action button
// 圆角胶囊浮动液态玻璃 · 对等 Image #36 HTML 设计 · 直接 .glassEffect modifier

import SwiftUI

struct BottomNav: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    var body: some View {
        ZStack {
            // 胶囊形液态玻璃 bar（中央留空给 center button 凸起）
            HStack(spacing: 0) {
                navTab(icon: "envelope.fill", label: "申し込み",
                       active: router.current.isApplyBranch,
                       action: { router.replace(.apply) })

                // 中央空位（占位，center button 用 overlay 放）
                Spacer().frame(width: 80)

                navTab(icon: "person.fill", label: "マイページ",
                       active: router.current.isMyBranch,
                       action: { router.replace(.my) })
            }
            .padding(.horizontal, 12)
            .frame(height: 62)
            .modifier(BottomNavGlass())
            .overlay(
                Capsule(style: .continuous)
                    .stroke(Color.white.opacity(0.5), lineWidth: 0.5)
            )
            .shadow(color: .black.opacity(0.15), radius: 20, x: 0, y: 6)

            // 中央 ⭐点呼 action button · 凸起浮在 bar 上方
            centerButton
                .offset(y: -10)
        }
    }

    private func navTab(icon: String, label: String, active: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                Text(label)
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(active ? T.primary : T.inkMute)
            .frame(maxWidth: .infinity)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    private var centerButton: some View {
        Button {
            let fb = UIImpactFeedbackGenerator(style: .medium)
            fb.impactOccurred()
            app.openSheet(.rollcall)
        } label: {
            VStack(spacing: 2) {
                ZStack {
                    Circle()
                        .fill(T.rollBtnGrad)
                        .frame(width: 62, height: 62)
                        .shadow(color: T.primary.opacity(0.42), radius: 10, y: 6)
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 26, weight: .bold))
                        .foregroundStyle(.white)
                }
                Text("点呼")
                    .font(.system(size: 9, weight: .bold))
                    .foregroundStyle(T.primary)
            }
        }
        .buttonStyle(.plain)
    }
}

// 直接 .glassEffect 修饰器（iOS 26） + fallback
private struct BottomNavGlass: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 26.0, *) {
            content
                .glassEffect(.regular, in: .capsule)
        } else {
            content
                .background(.ultraThinMaterial, in: Capsule(style: .continuous))
        }
    }
}
