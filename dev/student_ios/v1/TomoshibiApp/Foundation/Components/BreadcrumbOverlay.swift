// BreadcrumbOverlay.swift · 长按 PageHeader 左侧按钮时弹出的小型 popup
//
// 仿 iOS Safari「← 长按显示历史」UI（itsuki 2026-05-01 反馈）:
// - 取消屏幕中央的大 modal，改为紧贴左上角 home/back 按钮正下方弹出
// - 半透明遮罩几乎全透明（仅轻微暗化），点外侧关闭
// - 取消末尾的取消按钮（点外侧关闭更符合 iOS 标准）

import SwiftUI

struct BreadcrumbOverlay: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    /// PageHeader 左侧按钮为 padding(.horizontal 16, .vertical 12) + 36×36 的 Button
    /// → 按钮中心在 (16 + 18, 12 + 18) = (34, 30)，按钮下缘 = 12 + 36 = 48pt
    /// 加上 safeArea top inset，popup 原点放在 leading=12 / top=safeArea+50 处
    private let popupLeadingPadding: CGFloat = 12
    private let popupTopPadding: CGFloat = 50

    var body: some View {
        ZStack(alignment: .topLeading) {
            // 透明遮罩 — 点外侧关闭（无暗化，仿 iOS Safari 风格）
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
            // 主页快捷入口
            popupRow(
                icon: AnyView(Ic.home(16)),
                label: "ホームへ戻る"
            ) {
                router.replace(.home)
                close()
            }

            if !router.breadcrumbChain.isEmpty {
                Divider()
            }

            // 栈内路径（仿 iOS Safari 历史列表风格）
            ForEach(Array(router.breadcrumbChain.enumerated()), id: \.offset) { idx, route in
                if idx > 0 { Divider() }
                popupRow(
                    icon: AnyView(
                        Image(systemName: "arrow.uturn.backward")
                            .font(.system(size: 13, weight: .medium))
                    ),
                    label: route.displayName
                ) {
                    router.jump(toIndex: idx)
                    close()
                }
            }
        }
        .frame(width: 240, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(T.paper)
                .shadow(color: T.ink.opacity(0.18), radius: 18, x: 0, y: 6)
                .shadow(color: T.ink.opacity(0.08), radius: 4, x: 0, y: 1)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(T.hair, lineWidth: 0.5)
        }
    }

    private func popupRow(
        icon: AnyView,
        label: String,
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
