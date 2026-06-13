// BottomNav.swift · 3 tab + 中央 ⭐点呼 action button
// iOS 26 Liquid Glass morph 效果 (itsuki 2026-05-01 反馈):
//   选中的 tab 叠加高光玻璃，切换到别的 tab 时 capsule 平滑滑动 morph。
//   通过 `GlassEffectContainer` + `glassEffectID` + `.interactive()` 实现。
//   iOS < 26 使用旧版回退方案（无玻璃效果，active 仅简单 tint）。

import SwiftUI

struct BottomNav: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    @Namespace private var glassNS

    var body: some View {
        ZStack {
            if #available(iOS 26.0, *) {
                liquidGlassBar
            } else {
                legacyBar
            }

            // 中央 ⭐点呼 action button · 凸出悬浮在 bar 上方
            centerButton
                .offset(y: -10)
        }
    }

    // MARK: - iOS 26 Liquid Glass morph 版

    @available(iOS 26.0, *)
    private var liquidGlassBar: some View {
        // 整个 bar 用 .glassEffect 做 Liquid Glass 胶囊。
        // active tab 用 matchedGeometryEffect 让背景半透明 capsule 滑动 morph
        // （iOS 26 .glassEffect API 在 button .background 里会覆盖 icon/label，故不用）。
        HStack(spacing: 0) {
            navTab26(icon: "envelope.fill", label: "申し込み",
                     active: router.current.isApplyBranch,
                     action: { router.replace(.apply) })
            Spacer().frame(width: 80)
            navTab26(icon: "person.fill", label: "マイページ",
                     active: router.current.isMyBranch,
                     action: { router.replace(.my) })
        }
        .padding(.horizontal, 12)
        .frame(height: 62)
        .background(T.paper.opacity(0.78), in: Capsule(style: .continuous))
        .glassEffect(.regular, in: .capsule)
        .overlay(
            Capsule(style: .continuous)
                .stroke(Color.white.opacity(0.5), lineWidth: 0.5)
        )
        .shadow(color: .black.opacity(0.15), radius: 20, x: 0, y: 6)
        .animation(.spring(response: 0.45, dampingFraction: 0.78),
                   value: router.current)
    }

    /// nav tab（iOS 26 版）— active 时在背后绘制一个半透明 primary tint capsule，
    /// 用 matchedGeometryEffect 在切换时让它滑动 morph。
    /// （不使用 .glassEffect + glassEffectID 的原因：iOS 26 glassEffect
    /// 在 button .background 里会遮住 icon + label，导致按钮不可见。）
    @available(iOS 26.0, *)
    private func navTab26(icon: String, label: String, active: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                Text(label)
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(active ? T.primary : T.inkMute)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .contentShape(Rectangle())
            .background {
                if active {
                    Capsule(style: .continuous)
                        .fill(T.primary.opacity(0.12))
                        .padding(.vertical, 6)
                        .matchedGeometryEffect(id: "active-nav", in: glassNS)
                }
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: - iOS < 26 旧版回退

    private var legacyBar: some View {
        HStack(spacing: 0) {
            navTab(icon: "envelope.fill", label: "申し込み",
                   active: router.current.isApplyBranch,
                   action: { router.replace(.apply) })
            Spacer().frame(width: 80)
            navTab(icon: "person.fill", label: "マイページ",
                   active: router.current.isMyBranch,
                   action: { router.replace(.my) })
        }
        .padding(.horizontal, 12)
        .frame(height: 62)
        .background(T.paper.opacity(0.78), in: Capsule(style: .continuous))
        .background(.ultraThinMaterial, in: Capsule(style: .continuous))
        .overlay(
            Capsule(style: .continuous)
                .stroke(Color.white.opacity(0.5), lineWidth: 0.5)
        )
        .shadow(color: .black.opacity(0.15), radius: 20, x: 0, y: 6)
    }

    /// nav tab — 将 VStack 作为 Button label，同时将点击区域扩展到整个 bar（高度 62pt）。
    /// 旧代码仅 VStack 自然高度（≈40pt）可点击，上下各 10pt 空白会漏触
    /// 穿透到背面的 ScrollView（itsuki 2026-05-01 报告）。
    /// 用 `.frame(maxHeight: .infinity)` + `.contentShape(Rectangle())` 将整行全域设为可点击。
    private func navTab(icon: String, label: String, active: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                Text(label)
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(active ? T.primary : T.inkMute)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
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
