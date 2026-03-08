import SwiftUI

struct RollCallHistoryDetailView: View {
    let date: String
    let reason: String

    var body: some View {
        List {
            Section("详情") {
                row("日期", date)
                row("异常原因", reason)
                row("场次类型", "morning")
                row("基础状态", "absent")
                row("状态来源", "teacher_override")
            }

            Section("处理记录（占位）") {
                Text("老师改判原因：签到后离开现场")
                Text("审计记录 ID：audit_demo_001")
                    .foregroundColor(.secondary)
            }
        }
        .navigationTitle("历史详情")
    }

    @ViewBuilder
    private func row(_ title: String, _ value: String) -> some View {
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
        RollCallHistoryDetailView(date: "2026-02-12", reason: "teacher_override")
    }
}
