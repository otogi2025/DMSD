// BreadcrumbOverlay.swift · 长按返回弹出的多级导航 popup

import SwiftUI

struct BreadcrumbOverlay: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    var body: some View {
        ZStack {
            // 半透明背景
            Color.black.opacity(0.35)
                .ignoresSafeArea()
                .onTapGesture { close() }

            // Popup
            VStack(alignment: .leading, spacing: 0) {
                Text("ナビゲーション履歴")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(T.inkMute)
                    .padding(.horizontal, 16).padding(.top, 14)

                // Home 快捷
                Button {
                    router.replace(.home)
                    close()
                } label: {
                    HStack(spacing: 10) {
                        Ic.home(18)
                        Text("ホームへ戻る").font(.system(size: 15, weight: .medium))
                        Spacer()
                    }
                    .padding(.horizontal, 16).padding(.vertical, 14)
                    .foregroundStyle(T.ink)
                }
                .buttonStyle(.plain)

                Divider().padding(.horizontal, 16)

                // 栈内路径
                ForEach(Array(router.breadcrumbChain.enumerated()), id: \.offset) { idx, route in
                    Button {
                        router.jump(to: route)
                        close()
                    } label: {
                        HStack(spacing: 10) {
                            Text("\(idx + 1).")
                                .font(.system(size: 12, design: .monospaced))
                                .foregroundStyle(T.inkMute)
                            Text(route.displayName)
                                .font(.system(size: 15))
                            Spacer()
                            Ic.chevR(14)
                        }
                        .padding(.horizontal, 16).padding(.vertical, 12)
                        .foregroundStyle(T.ink)
                    }
                    .buttonStyle(.plain)
                }

                // 取消
                Button {
                    close()
                } label: {
                    Text("キャンセル")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(T.inkSub)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.plain)
                .background(T.hairSoft)
            }
            .frame(maxWidth: 320)
            .background {
                RoundedRectangle(cornerRadius: T.Radius.lg, style: .continuous)
                    .fill(T.paper)
                    .shadow(color: T.ink.opacity(0.2), radius: 24, y: 8)
            }
            .clipShape(RoundedRectangle(cornerRadius: T.Radius.lg, style: .continuous))
            .padding(24)
            .transition(.scale(scale: 0.9).combined(with: .opacity))
        }
    }

    private func close() {
        withAnimation(.spring(response: 0.28, dampingFraction: 0.85)) {
            app.breadcrumbOpen = false
        }
    }
}
