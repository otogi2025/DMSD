// IOSStatusBar.swift · 模拟 iOS 状态栏（9:41 · Signal · WiFi · Battery）
// 实际 Simulator 里有真 status bar，这只在 Preview / 某些 sheet 上盖用

import SwiftUI

struct IOSStatusBar: View {
    var body: some View {
        HStack {
            Text("9:41")
                .font(.system(size: 15, weight: .semibold))
                .foregroundStyle(T.ink)
            Spacer()
            HStack(spacing: 4) {
                Image(systemName: "cellularbars")
                Image(systemName: "wifi")
                Image(systemName: "battery.100")
            }
            .font(.system(size: 13))
            .foregroundStyle(T.ink)
        }
        .padding(.horizontal, 20).padding(.vertical, 12)
    }
}
