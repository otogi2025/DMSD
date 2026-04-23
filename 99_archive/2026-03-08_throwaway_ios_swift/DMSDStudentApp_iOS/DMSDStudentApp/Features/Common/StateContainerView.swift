import SwiftUI

struct StateContainerView<Content: View>: View {
    let state: ScreenState
    let content: () -> Content

    var body: some View {
        switch state {
        case .loading:
            ProgressView("加载中...")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        case .content:
            content()
        case .empty:
            VStack(spacing: 8) {
                Image(systemName: "tray")
                    .font(.system(size: 28))
                    .foregroundColor(.secondary)
                Text("暂无数据")
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        case .error(let message):
            VStack(spacing: 8) {
                Image(systemName: "exclamationmark.triangle")
                    .font(.system(size: 28))
                    .foregroundColor(.orange)
                Text(message)
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
            }
            .padding()
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}
