import SwiftUI

struct DisciplineLedgerView: View {
    private let demoRows: [(String, String, String)] = [
        ("2026-02-12 08:55", "absent", "+1.0"),
        ("2026-02-11 08:52", "late", "+0.5"),
        ("2026-02-10 08:49", "late", "+0.5")
    ]

    var body: some View {
        List {
            Section("扣分流水（占位）") {
                ForEach(demoRows, id: \.0) { row in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(row.0)
                        Text("类型：\(row.1)  分值：\(row.2)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .navigationTitle("扣分流水")
    }
}

#Preview {
    NavigationView {
        DisciplineLedgerView()
    }
}
