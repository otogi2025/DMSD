// Route.swift
// ⭐ Foundation · 全 App route 定义 · 32 case 对等 phaseB_src _template.html

import Foundation

enum Route: Hashable {
    // §0 认证 / 启动
    case splash
    case onboarding
    case registerStep1, registerStep2, registerStep3, registerStep4
    case registerStep5 // 注册码输入（2026-05-04 加，App Store 上架对策）
    case registerDone
    case login
    case lockout
    case pwreset

    /// §1 Home 主屏
    case home

    // §1.3 老师公告（2026-05-04 加，spec system_features.md §7.15）
    case homeAnnouncements // 公告一覧
    case homeAnnouncementDetail(id: String) // 公告详情 + 回复

    // §1.4 Home 子页 Community
    case homeNotifications
    case homePackages
    // id 用 String：演示构建是 SEED.PackageItem 的 Int（转字符串），生产构建是后端 FrontDeskItem 的 UUID 字符串
    case homePackageDetail(id: String)
    case homeLost
    case homeLostNew
    case homeLostDetail(id: String)
    case homeMusic
    case homeMusicNew
    case homeMusicDetail(id: String)
    case homeEvents
    case homeEventDetail(id: Int)

    // §2 申し込み
    case apply
    case applyNew
    case applyForm(kind: String)
    case applyPreview(kind: String)
    case applyDone(kind: String)
    case applyDetail(id: String)
    case dormEventList
    case studyOnlineList
    case fridgeList
    case itemList

    // §3 マイページ
    case my
    case myInfo
    case myInfoEdit
    case myRollcall
    case myRollcallDetail(entryId: String?) // IX-012: 带被点那行记录的 id，详情页据此渲染
    case myPoints
    case myPointsChart
    case myDiscipline
    case myHealth
    case myPackages
    case mySettings
    case myAbout
    case myStudy // 学習出席履歴 (system_features §7.3.10) — isStudyTarget のみ

    // §4 V1 リファレンス系（老師 38 条 #5 / #8 / #9）
    case stayList // #5 申請履歴 一覧（GET /applications/mine）
    case stayDetail(id: String) // #5 申請詳細 + 承認 chain（GET /applications/:id）
    case stayEdit(id: String) // 出寮届 修改届 (system_features §7.2.4-5)
    case schedule // #9 行事予定 月历（GET /events）
    case busList // #8 寮生特別運行便 一覧（GET /buses）

    /// Breadcrumb 显示名（日本語）
    var displayName: String {
        switch self {
        case .splash: return "Splash"
        case .onboarding: return "紹介"
        case .registerStep1: return "基本情報"
        case .registerStep2: return "点呼区分"
        case .registerStep3: return "連絡先"
        case .registerStep4: return "パスワード"
        case .registerStep5: return "認証コード"
        case .registerDone: return "完了"
        case .login: return "ログイン"
        case .lockout: return "ロック中"
        case .pwreset: return "パスワードリセット"
        case .home: return "ホーム"
        case .homeAnnouncements: return "お知らせ"
        case .homeAnnouncementDetail: return "お知らせ詳細"
        case .homeNotifications: return "通知"
        case .homePackages: return "宅配"
        case .homePackageDetail: return "宅配詳細"
        case .homeLost: return "落とし物"
        case .homeLostNew: return "投稿"
        case .homeLostDetail: return "詳細"
        case .homeMusic: return "リクエスト曲"
        case .homeMusicNew: return "投稿"
        case .homeMusicDetail: return "詳細"
        case .homeEvents: return "活動"
        case .homeEventDetail: return "詳細"
        case .apply: return "申し込み"
        case .applyNew: return "新規申請"
        case .applyForm: return "入力"
        case .applyPreview: return "確認"
        case .applyDone: return "完了"
        case .applyDetail: return "詳細"
        case .dormEventList: return "行事企画一覧"
        case .studyOnlineList: return "オンライン学習申請一覧"
        case .fridgeList: return "冷蔵庫購入届一覧"
        case .itemList: return "物品所持許可願一覧"
        case .my: return "マイページ"
        case .myInfo: return "個人情報"
        case .myInfoEdit: return "個人情報編集"
        case .myRollcall: return "点呼履歴"
        case .myRollcallDetail: return "詳細"
        case .myPoints: return "減点明細"
        case .myPointsChart: return "グラフ"
        case .myDiscipline: return "処分履歴"
        case .myHealth: return "体調報告履歴"
        case .myPackages: return "宅配履歴"
        case .mySettings: return "設定"
        case .myAbout: return "Tomoshibi について"
        case .myStudy: return "学習履歴"
        case .stayList: return "申請履歴"
        case .stayDetail: return "申請詳細"
        case .stayEdit: return "変更届"
        case .schedule: return "行事予定"
        case .busList: return "特別運行便"
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
        case .apply, .applyNew, .applyForm, .applyPreview, .applyDone, .applyDetail,
             .dormEventList, .studyOnlineList, .fridgeList, .itemList:
            return true
        default: return false
        }
    }

    /// 属于 my tab 子树
    var isMyBranch: Bool {
        switch self {
        case .my, .myInfo, .myInfoEdit, .myRollcall, .myRollcallDetail, .myPoints, .myPointsChart,
             .myDiscipline, .myHealth, .myPackages, .mySettings, .myAbout, .myStudy,
             .stayList, .stayDetail, .stayEdit, .schedule, .busList:
            return true
        default: return false
        }
    }

    /// 是否应隐藏 BottomNav（所有 auth flow + form preview/done 都隐藏）
    var hidesBottomNav: Bool {
        switch self {
        case .splash, .onboarding,
             .registerStep1, .registerStep2, .registerStep3, .registerStep4, .registerStep5,
             .registerDone,
             .login, .lockout, .pwreset:
            return true
        default: return false
        }
    }

    /// 是否应隐藏 TopRollBar（auth flow 隐藏）
    var hidesTopBar: Bool {
        switch self {
        case .splash, .onboarding,
             .registerStep1, .registerStep2, .registerStep3, .registerStep4, .registerStep5,
             .registerDone,
             .login, .lockout, .pwreset:
            return true
        default: return false
        }
    }
}
