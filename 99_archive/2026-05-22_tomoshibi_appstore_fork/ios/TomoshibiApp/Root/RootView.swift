// RootView.swift
// ⭐ 顶层 View · Router switch + GlobalOverlays 挂载

import SwiftUI

struct RootView: View {
    @EnvironmentObject var router: RouterStore
    @EnvironmentObject var app: AppStore

    var body: some View {
        ZStack {
            // 背景
            Color(.systemBackground)
                .ignoresSafeArea()

            // 当前 route 对应 View · safeAreaInset 让 ScrollView 自动避让 TopRollBar / BottomNav
            content(for: router.current)
                .transition(.opacity)
                .safeAreaInset(edge: .top, spacing: 0) {
                    // TopRollBar 只在 active/ done显示，idle 不显示
                    if !router.current.hidesTopBar && app.rollState != .idle {
                        TopRollBar()
                            .padding(.horizontal, 12)
                            .padding(.top, 6)
                            .padding(.bottom, 6)
                            .opacity(app.sheetOpen == nil ? 1 : 0)
                            .allowsHitTesting(app.sheetOpen == nil)
                            .animation(.easeInOut(duration: 0.2), value: app.sheetOpen)
                    }
                }
                .safeAreaInset(edge: .bottom, spacing: 0) {
                    if !router.current.hidesBottomNav {
                        BottomNav()
                            .padding(.horizontal, 16)
                            .opacity(app.sheetOpen == nil ? 1 : 0)
                            .allowsHitTesting(app.sheetOpen == nil)
                            .animation(.easeInOut(duration: 0.2), value: app.sheetOpen)
                    }
                }

            // 全局 overlays: sheet / breadcrumb / toast
            GlobalOverlays()
        }
        .animation(.easeInOut(duration: 0.2), value: router.current)
    }

    @ViewBuilder
    private func content(for route: Route) -> some View {
        switch route {
        // §0 认证 / 启动 — Agent A 实装
        case .splash: SplashView()
        case .onboarding: OnboardingView()
        case .registerStep1: RegisterStep1View()
        case .registerStep2: RegisterStep2View()
        case .registerStep3: RegisterStep3View()
        case .registerStep4: RegisterStep4View()
        case .registerStep5: RegisterStep5View()
        case .registerDone: RegisterDoneView()
        case .login: LoginView()
        case .lockout: LockoutView()
        case .pwreset: PwResetView()

        // §1 Home 主屏 — Agent B 实装
        case .home: HomeView()

        // §1.3 老师公告（2026-05-04 加，spec §7.15）
        case .homeAnnouncements: AnnouncementListView()
        case .homeAnnouncementDetail(let id): AnnouncementDetailView(id: id)

        // §1.4 Home 子页 — Agent C 实装
        case .homeNotifications: NotificationsView()
        case .homePackages: PackagesView()
        case .homePackageDetail(let id): PackageDetailView(id: id)
        case .homeLost: LostView()
        case .homeLostNew: LostNewView()
        case .homeLostDetail(let id): LostDetailView(id: id)
        case .homeMusic: MusicView()
        case .homeMusicNew: MusicNewView()
        case .homeMusicDetail(let id): MusicDetailView(id: id)
        case .homeWall: WallView()
        case .homeWallNew: WallNewView()
        case .homeWallDetail(let id): WallDetailView(id: id)
        case .homeEvents: EventsView()
        case .homeEventDetail(let id): EventDetailView(id: id)
        case .homeBus: BusView()
        case .homeSuggest: SuggestView()
        case .homeSuggestFeed: SuggestFeedView()

        // §2 申し込み — Agent D 实装
        case .apply: ApplyListView()
        case .applyNew: ApplyNewView()
        case .applyForm(let kind): ApplyFormDispatcher(kind: kind)
        case .applyPreview(let kind): ApplyPreviewView(kind: kind)
        case .applyDone(let kind): ApplyDoneView(kind: kind)
        case .applyDetail(let id): ApplyDetailView(id: id)

        // §3 マイページ — Agent E 实装
        case .my: MyLandingView()
        case .myInfo: MyInfoView()
        case .myInfoEdit: MyInfoEditView()
        case .myRollcall: MyRollcallView()
        case .myRollcallDetail: MyRollcallDetailView()
        case .myPoints: MyPointsView()
        case .myPointsChart: MyPointsChartView()
        case .myDiscipline: MyDisciplineView()
        case .myHealth: MyHealthView()
        case .myClean: MyCleanView()
        case .myPackages: MyPackagesView()
        case .mySettings: MySettingsView()
        case .myAbout: MyAboutView()
        case .myStudy: MyStudyView()

        // §4 V1 リファレンス系 — 老師 38 条 #5 / #8 / #9（会话 C 实装）
        case .stayList: StayListView()
        case .stayDetail(let id): StayDetailView(id: id)
        case .stayEdit(let id): StayEditForm(id: id)
        case .schedule: ScheduleView()
        case .busList: BusListView()
        }
    }
}

#Preview {
    RootView()
        .environmentObject(RouterStore())
        .environmentObject(AppStore())
}
