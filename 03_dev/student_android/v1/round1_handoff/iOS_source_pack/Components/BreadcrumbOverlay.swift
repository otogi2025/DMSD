// BreadcrumbOverlay.swift · 长按 PageHeader 左ボタン から弹出する小型 popup
//
// iOS Safari の「← 長押しで履歴が出る」UI に準拠（itsuki 2026-05-01 反馈）:
// - 画面中央の大きな modal をやめて、左上の home/back ボタンの真下に貼り付く
// - 半透明 backdrop はほぼ透明（薄い暗化のみ）、tap で閉じる
// - 末尾のキャンセルボタンは廃止（外側 tap で閉じる方が iOS 標準）

import SwiftUI

struct BreadcrumbOverlay: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// PageHeader の左ボタンは padding(.horizontal 16, .vertical 12) + 36×36 の Button
    /// → ボタン中心は (16 + 18, 12 + 18) = (34, 30)、ボタン下端 = 12 + 36 = 48pt
    /// safeArea top inset を加味して popup の origin を leading=12 / top=safeArea+50 に置く
    private let popupLeadingPadding: CGFloat = 12
    private let popupTopPadding: CGFloat = 50

    var body: some View {
        ZStack(alignment: .topLeading) {
            // 透明 backdrop — 外侧 tap 关闭（薄い暗化なし、iOS Safari 風）
            Color.black.opacity(0.0001)
                .ignoresSafeArea()
                .contentShape(Rectangle())
                .onTapGesture { close() }

            popup
                .padding(.leading, popupLeadingPadding)
                .padding(.top, popupTopPadding)
                .transition(
                    .asymmetric(
                        insertion: .scale(scale: 0.85, anchor: .topLeading)
                            .combined(with: .opacity),
                        removal: .opacity
                    )
                )
        }
    }

    private var popup: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Home 快捷
            popupRow(
                icon: AnyView(Ic.home(16)),
                label: "ホームへ戻る",
                showChev: false
            ) {
                router.replace(.home)
                close()
            }

            if !router.breadcrumbChain.isEmpty {
                Divider()
            }

            // 栈内路径（iOS Safari の history list 風）
            ForEach(Array(router.breadcrumbChain.enumerated()), id: \.offset) { idx, route in
                if idx > 0 { Divider() }
                popupRow(
                    icon: AnyView(
                        Image(systemName: "arrow.uturn.backward")
                            .font(.system(size: 13, weight: .medium))
                    ),
                    label: route.displayName,
                    showChev: false
                ) {
                    router.jump(to: route)
                    close()
                }
            }
        }
        .frame(width: 240, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(T.paper)
                .shadow(color: T.ink.opacity(0.18), radius: 18, x: 0, y: 6)
                .shadow(color: T.ink.opacity(0.08), radius: 4,  x: 0, y: 1)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(T.hair, lineWidth: 0.5)
        }
    }

    @ViewBuilder
    private func popupRow(
        icon: AnyView,
        label: String,
        showChev: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                icon
                    .foregroundStyle(T.ink)
                    .frame(width: 18, height: 18)
                Text(label)
                    .font(.system(size: 14.5, weight: .medium))
                    .foregroundStyle(T.ink)
                    .lineLimit(1)
                Spacer(minLength: 0)
                if showChev {
                    Ic.chevR(12).foregroundStyle(T.inkMute)
                }
            }
            .padding(.horizontal, 14).padding(.vertical, 12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    private func close() {
        withAnimation(.spring(response: 0.28, dampingFraction: 0.85)) {
            app.breadcrumbOpen = false
        }
    }
}
