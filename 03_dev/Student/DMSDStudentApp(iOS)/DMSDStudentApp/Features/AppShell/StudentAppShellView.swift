import SwiftUI
import UIKit

private enum StudentRootTab {
    case applications
    case history
    case me
}

struct StudentAppShellView: View {
    @State private var selectedTab: StudentRootTab = .history
    @State private var showScanSheet = false
    @State private var scanSheetState: RollCallScanSheetState = .scanning
    @State private var toastMessage: String?

    @StateObject private var historyStore = RollCallHistoryStore()
    @StateObject private var scanService = NFCScanService()

    var body: some View {
        ZStack(alignment: .bottom) {
            currentPage
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(LiquidBackdropView())

            StudentBottomBar(
                selectedTab: $selectedTab,
                onTapScan: openScanSheet
            )
        }
        .overlay {
            if showScanSheet {
                RollCallScanOverlay(
                    state: scanSheetState,
                    onCancel: cancelScan
                )
                .transition(.opacity)
            }
        }
        .overlay(alignment: .top) {
            if let toastMessage {
                Text(toastMessage)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(.black.opacity(0.8), in: Capsule())
                    .padding(.top, 10)
                    .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
        .animation(.easeInOut(duration: 0.2), value: showScanSheet)
        .animation(.easeInOut(duration: 0.2), value: toastMessage)
        .onAppear {
            historyStore.loadIfNeeded()
        }
    }

    @ViewBuilder
    private var currentPage: some View {
        switch selectedTab {
        case .applications:
            ApplicationCenterView()
        case .history:
            RollCallHistoryHomeView(store: historyStore)
        case .me:
            MyPageView()
        }
    }

    private func openScanSheet() {
        selectedTab = .history
        scanSheetState = .scanning
        showScanSheet = true
        startScanning()
    }

    private func startScanning() {
        scanSheetState = .scanning

        scanService.start(timeout: 12) { result in
            switch result {
            case .success:
                UINotificationFeedbackGenerator().notificationOccurred(.success)
                historyStore.applyLocalCheckInSuccess()
                historyStore.refreshMonthKeepingLocalTodayState()

                scanSheetState = .success
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
                    closeScanSheet(showToast: true)
                }

            case .failure(let message, let retryable):
                scanSheetState = .error(message)

                if retryable, showScanSheet {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.1) {
                        guard showScanSheet else { return }
                        startScanning()
                    }
                }
            }
        }
    }

    private func cancelScan() {
        scanService.stop()
        closeScanSheet(showToast: false)
    }

    private func closeScanSheet(showToast: Bool) {
        selectedTab = .history
        showScanSheet = false
        scanSheetState = .scanning

        guard showToast else { return }

        toastMessage = "点呼成功"
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            toastMessage = nil
        }
    }
}

private struct StudentBottomBar: View {
    @Binding var selectedTab: StudentRootTab
    let onTapScan: () -> Void

    var body: some View {
        ZStack(alignment: .top) {
            HStack(alignment: .bottom) {
                tabItem(
                    icon: "envelope.fill",
                    title: "申请",
                    isSelected: selectedTab == .applications
                ) {
                    selectedTab = .applications
                }

                Spacer(minLength: 88)

                tabItem(
                    icon: "sparkles",
                    title: "我的页面",
                    isSelected: selectedTab == .me
                ) {
                    selectedTab = .me
                }
            }
            .padding(.horizontal, 34)
            .padding(.top, 12)
            .padding(.bottom, 14)

            Button(action: onTapScan) {
                VStack(spacing: 6) {
                    Image(systemName: "shield.lefthalf.filled.badge.checkmark")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                        .frame(width: 56, height: 56)
                        .background(
                            Circle()
                                .fill(Color(red: 0.12, green: 0.44, blue: 0.96))
                                .shadow(color: .black.opacity(0.22), radius: 16, x: 0, y: 6)
                        )

                    Text("点呼")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color.primary)
                }
            }
            .offset(y: -12)
            .buttonStyle(FloatingActionButtonStyle())
        }
        .frame(height: 94)
        .background(
            .regularMaterial,
            in: RoundedRectangle(cornerRadius: 22, style: .continuous)
        )
        .overlay(alignment: .top) {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(.white.opacity(0.8), lineWidth: 1)
        }
        .overlay(alignment: .top) {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [.white.opacity(0.55), .clear],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        }
        .shadow(color: .black.opacity(0.08), radius: 18, x: 0, y: 6)
        .padding(.horizontal, 12)
        .padding(.bottom, 6)
    }

    private func tabItem(icon: String, title: String, isSelected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 5) {
                Image(systemName: icon)
                    .font(.system(size: 19, weight: .semibold))
                Text(title)
                    .font(.system(size: 12, weight: .medium))
            }
            .foregroundColor(isSelected ? Color(red: 0.12, green: 0.44, blue: 0.96) : .gray)
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.plain)
    }
}

private struct LiquidBackdropView: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.97, green: 0.98, blue: 1.0),
                    Color(red: 0.93, green: 0.95, blue: 0.99)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            Circle()
                .fill(Color(red: 0.55, green: 0.76, blue: 1.0).opacity(0.24))
                .frame(width: 280, height: 280)
                .offset(x: -130, y: -260)
                .blur(radius: 8)

            Circle()
                .fill(Color(red: 0.56, green: 0.95, blue: 0.84).opacity(0.2))
                .frame(width: 240, height: 240)
                .offset(x: 150, y: -140)
                .blur(radius: 10)

            Circle()
                .fill(Color(red: 0.73, green: 0.68, blue: 1.0).opacity(0.16))
                .frame(width: 260, height: 260)
                .offset(x: 120, y: 220)
                .blur(radius: 12)
        }
        .ignoresSafeArea()
    }
}

private struct FloatingActionButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.94 : 1)
            .brightness(configuration.isPressed ? -0.06 : 0)
            .animation(.spring(response: 0.25, dampingFraction: 0.7), value: configuration.isPressed)
    }
}

#Preview {
    StudentAppShellView()
}
