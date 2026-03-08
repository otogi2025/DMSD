import SwiftUI

struct ApplicationCenterView: View {
    var body: some View {
        NavigationView {
            List {
                Section("申请") {
                    Text("申请中心骨架（后续接入 v1.1 页面）")
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("申请")
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

#Preview {
    ApplicationCenterView()
}
