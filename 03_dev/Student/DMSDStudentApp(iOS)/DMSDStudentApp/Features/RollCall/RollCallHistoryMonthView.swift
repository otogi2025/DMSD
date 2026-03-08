import SwiftUI

struct RollCallHistoryMonthView: View {
    @State private var state: ScreenState = .loading
    @State private var historyData: StudentHistoryMonthData?

    var body: some View {
        StateContainerView(state: state) {
            List {
                Section("月份") {
                    Text(historyData?.month ?? "-")
                }

                Section("日历状态") {
                    ForEach(historyData?.dayItems ?? [], id: \.date) { item in
                        HStack {
                            Text(item.date)
                            Spacer()
                            Text(item.calendarStatus)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Section("异常列表") {
                    ForEach(historyData?.anomalyItems ?? [], id: \.date) { item in
                        NavigationLink {
                            RollCallHistoryDetailView(date: item.date, reason: item.reason)
                        } label: {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.date)
                                Text(item.reason)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
            }
        }
        .navigationTitle("历史总览")
        .onAppear(perform: loadMock)
    }

    private func loadMock() {
        guard state == .loading else { return }

        guard let envelope: APIEnvelope<StudentHistoryMonthData> = MockJSONLoader.load("history_month", as: APIEnvelope<StudentHistoryMonthData>.self) else {
            state = .error("未找到 history_month mock 文件")
            return
        }

        if envelope.ok, let data = envelope.data {
            historyData = data
            state = .content
        } else if let message = envelope.error?.message {
            state = .error(message)
        } else {
            state = .empty
        }
    }
}

#Preview {
    NavigationView {
        RollCallHistoryMonthView()
    }
}
