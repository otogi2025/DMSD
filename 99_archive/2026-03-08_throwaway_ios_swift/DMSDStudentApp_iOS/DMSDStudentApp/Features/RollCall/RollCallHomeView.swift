import SwiftUI

struct RollCallHomeView: View {
    @State private var state: ScreenState = .loading
    @State private var homeData: StudentHomeData?

    var body: some View {
        StateContainerView(state: state) {
            List {
                Section("本场信息") {
                    infoRow("场次 ID", homeData?.sessionId ?? "-")
                    infoRow("场次类型", homeData?.sessionType.rawValue ?? "-")
                    infoRow("场次状态", homeData?.sessionStatus.rawValue ?? "-")
                    infoRow("服务器时间", homeData?.serverNow ?? "-")
                    infoRow("倒计时(秒)", "\(homeData?.remainingSeconds ?? 0)")
                }

                Section("我的状态") {
                    infoRow("基础状态", homeData?.baseStatus.rawValue ?? "-")
                    infoRow("状态来源", homeData?.statusSource.rawValue ?? "-")
                    infoRow("叠加标记", badgeText(homeData?.overlayBadges ?? []))
                }

                Section("快捷操作（占位）") {
                    Button("NFC 签到") {}
                    Button("健康上报") {}
                    Button("本场不点呼申请") {}
                }
            }
        }
        .navigationTitle("点呼主页")
        .onAppear(perform: loadMock)
    }

    private func loadMock() {
        guard state == .loading else { return }

        guard let envelope: APIEnvelope<StudentHomeData> = MockJSONLoader.load("student_home", as: APIEnvelope<StudentHomeData>.self) else {
            state = .error("未找到 student_home mock 文件")
            return
        }

        if envelope.ok, let data = envelope.data {
            homeData = data
            state = .content
        } else if let message = envelope.error?.message {
            state = .error(message)
        } else {
            state = .empty
        }
    }

    private func badgeText(_ badges: [OverlayBadge]) -> String {
        if badges.isEmpty { return "无" }
        return badges.map { $0.rawValue }.joined(separator: ", ")
    }

    @ViewBuilder
    private func infoRow(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    NavigationView {
        RollCallHomeView()
    }
}
