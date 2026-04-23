import SwiftUI

struct DisciplineCenterView: View {
    var body: some View {
        NavigationView {
            List {
                Section("纪律") {
                    NavigationLink("我的纪律概览") {
                        DisciplineSummaryView()
                    }
                    NavigationLink("扣分流水") {
                        DisciplineLedgerView()
                    }
                }
            }
            .navigationTitle("我的纪律")
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

#Preview {
    DisciplineCenterView()
}
