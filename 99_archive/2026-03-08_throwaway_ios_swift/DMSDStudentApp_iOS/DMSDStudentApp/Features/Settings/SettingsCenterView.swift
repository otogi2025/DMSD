import SwiftUI

struct SettingsCenterView: View {
    @State private var rollcallReminderEnabled = true
    @State private var useMockMode = true

    var body: some View {
        NavigationView {
            Form {
                Section("提醒") {
                    Toggle("点呼提醒", isOn: $rollcallReminderEnabled)
                }

                Section("开发设置") {
                    Toggle("使用 Mock 数据", isOn: $useMockMode)
                    Text("当前版本：v1.0 Skeleton")
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("设置")
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

#Preview {
    SettingsCenterView()
}
