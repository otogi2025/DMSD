// BottomNav.swift · 3 tab + 中央 ⭐点呼 action button
// iOS 26 Liquid Glass morph 効果 (itsuki 2026-05-01 反馈):
//   選択中 tab に高光ガラスが乗り、別 tab を tap すると capsule がスーッと滑って morph する。
//   `GlassEffectContainer` + `glassEffectID` + `.interactive()` で実現。
//   iOS < 26 は legacy fallback（ガラス無し、active 単純 tint）。

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

            // 中央 ⭐点呼 action button · 凸起浮在 bar 上方
            centerButton
                .offset(y: -10)
        }
    }

    // MARK: - iOS 26 Liquid Glass morph 版

    @available(iOS 26.0, *)
    private var liquidGlassBar: some View {
        // GlassEffectContainer 内部の glassEffectID が同じ glass は、
        // active 切替時に「滑って morph する」アニメーションを行う。
        GlassEffectContainer(spacing: 0) {
            ZStack {
                // (1) active glass capsule — active tab の背後に 1 個だけ出現
                HStack(spacing: 0) {
                    glassSlot(visible: router.current.isApplyBranch)
                    Spacer().frame(width: 80)
                    glassSlot(visible: router.current.isMyBranch)
                }
                .padding(.horizontal, 12)
                .frame(height: 62)

                // (2) tab buttons (前景)
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
            }
        }
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

    /// active glass capsule slot — 表示時のみ Capsule が glass + ID を持ち、
    /// 反対側 slot から「滑り込む」morph を起こす。
    @available(iOS 26.0, *)
    @ViewBuilder
    private func glassSlot(visible: Bool) -> some View {
        if visible {
            Capsule(style: .continuous)
                .fill(Color.clear)
                .glassEffect(
                    .regular.tint(T.primary.opacity(0.22)).interactive(),
                    in: Capsule(style: .continuous)
                )
                .glassEffectID("active-nav", in: glassNS)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding(.vertical, 6)
        } else {
            Color.clear.frame(maxWidth: .infinity)
        }
    }

    // MARK: - iOS < 26 fallback

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

    /// nav tab — VStack を Button label に置きつつ、hit 領域を bar 全体（高さ 62pt）に拡大。
    /// 旧コードは VStack 自然高さ（≈40pt）しか hit せず、上下 10pt の空白がタップ漏れして
    /// 背面の ScrollView に貫通していた（itsuki 2026-05-01 報告）。
    /// `.frame(maxHeight: .infinity)` + `.contentShape(Rectangle())` で row 全域を hit 化。
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
