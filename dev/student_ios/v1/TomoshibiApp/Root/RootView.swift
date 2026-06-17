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
        // 全局令牌守卫（ios⑤ 上线缺口）：登录令牌变 nil（登出 / 静默恢复里过期 / 各处 401 清空）统一踢回登录页。
        // authToken 的 didSet 只清状态不导航；各 feature 散落手写 replace(.login) 易漏（StayList 曾 3 处漏跳 / 只 back）。
        // 守卫 splash/login 阶段不重复 replace（splash 启动 token 本就 nil、有自己的跳转动画，别打断）。
        // 用单参 onChange = iOS 16 兼容写法（部署目标 16.0，双参 oldValue/newValue 签名要 iOS 17）。
        .onChange(of: app.authToken) { newValue in
            if newValue == nil, router.current != .login, router.current != .splash {
                router.replace(.login)
            }
        }
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
        case let .homeAnnouncementDetail(id): AnnouncementDetailView(id: id)
        // §1.4 Home 子页 — Agent C 实装
        case .homeNotifications: NotificationsView()
        case .homePackages: PackagesView()
        case let .homePackageDetail(id): PackageDetailView(id: id)
        case .homeLost: LostView()
        case .homeLostNew: LostNewView()
        case let .homeLostDetail(id): LostDetailView(id: id)
        case .homeMusic: MusicView()
        case .homeMusicNew: MusicNewView()
        case let .homeMusicDetail(id): MusicDetailView(id: id)
        case let .homeEventDetail(id): EventDetailView(id: id)
        // §2 申し込み — Agent D 实装
        case .apply: ApplyListView()
        case .applyNew: ApplyNewView()
        case let .applyForm(kind): ApplyFormDispatcher(kind: kind)
        case let .applyPreview(kind): ApplyPreviewView(kind: kind)
        case let .applyDone(kind): ApplyDoneView(kind: kind)
        case let .applyDetail(id): ApplyDetailView(id: id)
        case .dormEventList: DormEventProposalListView()
        case let .dormEventResubmit(id): DormEventProposalForm(resubmitId: id)
        case .studyOnlineList: StudyOnlineRequestListView()
        case .fridgeList: FridgePurchaseListView()
        case .itemList: ItemPossessionListView()
        // §3 マイページ — Agent E 实装
        case .my: MyLandingView()
        case .myInfo: MyInfoView()
        case .myInfoEdit: MyInfoEditView()
        case .myRollcall: MyRollcallView()
        case let .myRollcallDetail(entryId): MyRollcallDetailView(entryId: entryId)
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
        case let .stayDetail(id): StayDetailView(id: id)
        case let .stayEdit(id): StayEditForm(id: id)
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
