// Route.swift
// ⭐ Foundation · 全 App route 定义 · 32 case 对等 phaseB_src _template.html

import Foundation

enum Route: Hashable {
    // §0 认证 / 启动
    case splash
    case onboarding
    case registerStep1, registerStep2, registerStep3, registerStep4
    case registerDone
    case login
    case lockout
    case pwreset

    // §1 Home 主屏
    case home

    // §1.4 Home 子页 Community
    case homeNotifications
    case homePackages
    case homePackageDetail(id: Int)
    case homeLost
    case homeLostNew
    case homeLostDetail(id: Int)
    case homeMusic
    case homeMusicNew
    case homeMusicDetail(id: Int)
    case homeWall
    case homeWallNew
    case homeWallDetail(id: Int)
    case homeEvents
    case homeEventDetail(id: Int)
    case homeBus
    case homeSuggest
    case homeSuggestFeed

    // §2 申し込み
    case apply
    case applyNew
    case applyForm(kind: String)
    case applyPreview(kind: String)
    case applyDone(kind: String)
    case applyDetail(id: String)

    // §3 マイページ
    case my
    case myInfo
    case myInfoEdit
    case myRollcall
    case myRollcallDetail
    case myPoints
    case myPointsChart
    case myDiscipline
    case myHealth
    case myClean
    case myPackages
    case mySettings
    case myAbout

    // §4 V1 リファレンス系（老師 38 条 #5 / #8 / #9）
    case stayList                    // #5 申請履歴 一覧（GET /applications/mine）
    case stayDetail(id: String)      // #5 申請詳細 + 承認 chain（GET /applications/:id）
    case schedule                    // #9 行事予定 月历（GET /events）
    case busList                     // #8 寮生特別運航便 一覧（GET /buses）

    /// Breadcrumb 显示名（日本語）
    var displayName: String {
        switch self {
        case .splash: return "Splash"
        case .onboarding: return "紹介"
        case .registerStep1: return "基本情報"
        case .registerStep2: return "点呼区分"
        case .registerStep3: return "連絡先"
        case .registerStep4: return "パスワード"
        case .registerDone: return "完了"
        case .login: return "ログイン"
        case .lockout: return "ロック中"
        case .pwreset: return "パスワードリセット"
        case .home: return "ホーム"
        case .homeNotifications: return "通知"
        case .homePackages: return "宅配"
        case .homePackageDetail: return "宅配詳細"
        case .homeLost: return "落とし物"
        case .homeLostNew: return "投稿"
        case .homeLostDetail: return "詳細"
        case .homeMusic: return "リクエスト曲"
        case .homeMusicNew: return "投稿"
        case .homeMusicDetail: return "詳細"
        case .homeWall: return "寮ウォール"
        case .homeWallNew: return "投稿"
        case .homeWallDetail: return "詳細"
        case .homeEvents: return "活動"
        case .homeEventDetail: return "詳細"
        case .homeBus: return "バス時刻"
        case .homeSuggest: return "匿名建議"
        case .homeSuggestFeed: return "回答一覧"
        case .apply: return "申し込み"
        case .applyNew: return "新規申請"
        case .applyForm: return "入力"
        case .applyPreview: return "確認"
        case .applyDone: return "完了"
        case .applyDetail: return "詳細"
        case .my: return "マイページ"
        case .myInfo: return "個人情報"
        case .myInfoEdit: return "個人情報編集"
        case .myRollcall: return "点呼履歴"
        case .myRollcallDetail: return "詳細"
        case .myPoints: return "減点明細"
        case .myPointsChart: return "推移"
        case .myDiscipline: return "処分履歴"
        case .myHealth: return "体調報告履歴"
        case .myClean: return "掃除提出履歴"
        case .myPackages: return "宅配履歴"
        case .mySettings: return "設定"
        case .myAbout: return "Tomoshibi について"
        case .stayList: return "申請履歴"
        case .stayDetail: return "申請詳細"
        case .schedule: return "行事予定"
        case .busList: return "特別運航便"
        }
    }

    /// 是否为 tab root（bottom nav 里的 apply / my，或 home）
    var isTabRoot: Bool {
        switch self {
        case .home, .apply, .my: return true
        default: return false
        }
    }

    /// 属于 apply tab 子树（BottomNav 高亮用）
    var isApplyBranch: Bool {
        switch self {
        case .apply, .applyNew, .applyForm, .applyPreview, .applyDone, .applyDetail:
            return true
        default: return false
        }
    }

    /// 属于 my tab 子树
    var isMyBranch: Bool {
        switch self {
        case .my, .myInfo, .myInfoEdit, .myRollcall, .myRollcallDetail, .myPoints, .myPointsChart,
             .myDiscipline, .myHealth, .myClean, .myPackages, .mySettings, .myAbout,
             .stayList, .stayDetail, .schedule, .busList:
            return true
        default: return false
        }
    }

    /// 是否应隐藏 BottomNav（所有 auth flow + form preview/done 都隐藏）
    var hidesBottomNav: Bool {
        switch self {
        case .splash, .onboarding,
             .registerStep1, .registerStep2, .registerStep3, .registerStep4, .registerDone,
             .login, .lockout, .pwreset:
            return true
        default: return false
        }
    }

    /// 是否应隐藏 TopRollBar（auth flow 隐藏）
    var hidesTopBar: Bool {
        switch self {
        case .splash, .onboarding,
             .registerStep1, .registerStep2, .registerStep3, .registerStep4, .registerDone,
             .login, .lockout, .pwreset:
            return true
        default: return false
        }
    }
}
