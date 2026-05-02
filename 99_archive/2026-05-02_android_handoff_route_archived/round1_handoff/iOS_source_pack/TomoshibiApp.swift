// TomoshibiApp.swift
// ⭐ App entry · Foundation agent owns this file (Frozen after D1)
//
// 依据 ~/dev/DMSD/03_dev/demo_4-28/Student_iOS_new/IOS_DESIGN_LOG.md
// 架构: @main App → RootView with @StateObject router + app
// 全局 overlays (sheet / breadcrumb / toast) 挂在 RootView 内部 ZStack

import SwiftUI

@main
struct TomoshibiApp: App {
    @StateObject private var router = RouterStore()
    @StateObject private var app = AppStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(router)
                .environmentObject(app)
                .preferredColorScheme(app.isDark ? .dark : nil)
        }
    }
}
