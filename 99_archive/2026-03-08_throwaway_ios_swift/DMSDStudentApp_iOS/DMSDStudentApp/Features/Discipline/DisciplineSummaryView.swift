import SwiftUI

struct DisciplineSummaryView: View {
    var body: some View {
        List {
            Section("当月统计（占位）") {
                row("当月累计分", "2.5")
                row("迟到次数", "3")
                row("缺席次数", "1")
            }

            Section("处分判定（按冻结规则）") {
                Text(">= 4.0 分：下月罚扫")
                Text(">= 9.0 分：下月禁足")
            }
        }
        .navigationTitle("纪律概览")
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
        DisciplineSummaryView()
    }
}
