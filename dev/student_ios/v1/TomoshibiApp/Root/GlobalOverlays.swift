// GlobalOverlays.swift · 全局 overlay 挂载（sheet / breadcrumb / toast）
// TopRollBar / BottomNav 现在挂在 RootView 的 safeAreaInset 里（让 ScrollView 自动避让）

import SwiftUI

struct GlobalOverlays: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    var body: some View {
        ZStack {
            // Sheet backdrop + content
            if let kind = app.sheetOpen {
                GlassBackdrop { app.closeSheet() }
                sheetContent(for: kind)
            }

            // Breadcrumb popup
            if app.breadcrumbOpen {
                BreadcrumbOverlay()
            }

            // Toast
            if let t = app.toast {
                ToastView(text: t)
            }
        }
    }

    @ViewBuilder
    private func sheetContent(for kind: SheetKind) -> some View {
        switch kind {
        // 点呼 / 夜学習这两个签到弹窗只在演示版存在（HomeCheckinDemoSheets.swift）——
        // 生产版按钮直接开 CoreNFC，不经弹窗，所以这两个 case 在生产版永远不会被打开。
        case .rollcall:
            #if DEMO
                RollcallSheet()
            #else
                EmptyView()
            #endif
        case .studyCheckin:
            #if DEMO
                StudyCheckinSheet()
            #else
                EmptyView()
            #endif
        case .feedback: FeedbackSheet()
        case .health: HealthSheet()
        case .absence: AbsenceSheet()
        case .other: OtherSheet()
        case .logout: LogoutSheet()
        case .renewStudentNo: RenewStudentNoSheet()
        }
    }
}
