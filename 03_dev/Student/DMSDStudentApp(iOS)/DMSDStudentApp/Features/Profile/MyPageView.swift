import SwiftUI

struct MyPageView: View {
    var body: some View {
        NavigationView {
            List {
                Section("我的页面") {
                    Text("个人信息与设置入口骨架")
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("我的页面")
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

#Preview {
    MyPageView()
}
