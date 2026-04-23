import SwiftUI

struct RollCallCenterView: View {
    var body: some View {
        NavigationView {
            List {
                Section("点呼") {
                    NavigationLink("点呼主页（含签到弹层）") {
                        RollCallHomeView()
                    }
                    NavigationLink("点呼历史总览（月历+异常）") {
                        RollCallHistoryMonthView()
                    }
                }
            }
            .navigationTitle("点呼")
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

#Preview {
    RollCallCenterView()
}
