package jp.tomoshibi.android.data.seed

import jp.tomoshibi.android.data.model.*

// Mock seed 数据 — 对应 React tokens.jsx DATA + app-shell.jsx DEFAULT_STATE 默认值
// v1.0 demo 用，P6 接 backend 时换成真实 Repository

object MockData {
    val DEFAULT_USER = User(
        name = "リュウイヒ",
        kana = "りゅういひ",
        email = "otogi2025@gmail.com",
        dorm = "M",
        room = "M101",
        avatar = "リ"
    )

    val DEFAULT_APPLICATIONS = listOf(
        Application(
            id = "A-2401",
            kind = "外泊",
            dest = "実家（神戸）",
            from = "2025-04-12",
            to = "2025-04-14",
            status = ApplicationStatus.APPROVED,
            reason = "家族行事のため",
            createdAt = "2025-04-08"
        ),
        Application(
            id = "A-2402",
            kind = "外出",
            dest = "梅田 紀伊國屋書店",
            from = "2025-04-19",
            to = "2025-04-19",
            status = ApplicationStatus.PENDING,
            reason = "研究資料の購入",
            createdAt = "2025-04-18"
        ),
        Application(
            id = "A-2403",
            kind = "その他",
            dest = "共用エリア掃除",
            from = "2025-04-05",
            to = "2025-04-05",
            status = ApplicationStatus.RETURNED,
            reason = "掃除当番交代依頼",
            createdAt = "2025-04-04"
        )
    )

    val DEFAULT_DEDUCTIONS = listOf(
        Deduction("D-101", "2026-04-05", 0.5, "朝点呼・遅刻", 4),
        Deduction("D-102", "2026-04-07", 0.5, "朝点呼・遅刻", 4),
        Deduction("D-103", "2026-04-12", 0.5, "朝点呼・遅刻", 4),
        Deduction("D-104", "2026-04-15", 1.0, "晩点呼・欠席", 4),
        Deduction("D-105", "2026-04-18", 0.5, "朝点呼・遅刻", 4),
        Deduction("D-106", "2026-04-20", 1.0, "晩点呼・欠席", 4),
        Deduction("D-107", "2026-04-21", 0.5, "朝点呼・遅刻", 4)
    )

    val DEFAULT_NOTIFICATIONS = listOf(
        Notification("N1", "点呼", "今夜の点呼は 22:30", "NFCタッチを忘れずに。", "今日 18:30", false),
        Notification("N2", "申請", "外泊申請が承認されました", "A-2401 が承認済みです。", "昨日 10:12", false),
        Notification("N3", "減点", "遅刻警告", "今月の遅刻が 5 回に到達。", "昨日 9:00", false),
        Notification("N4", "活動", "明日 18:00 新入生歓迎会", "食堂集合。", "昨日", false),
        Notification("N5", "お知らせ", "春の親睦会 4/29(土)", "芝生広場にて、雨天は食堂。", "4/15", true)
    )

    val DEFAULT_MUSIC = listOf(
        MusicRequest("M1", "春の歌", "中島みゆき", 12),
        MusicRequest("M2", "プラネタリウム", "大塚愛", 8),
        MusicRequest("M3", "Lemon", "米津玄師", 22)
    )

    // 申请类型选项 — 对应 React tokens.jsx applyKinds
    data class ApplyKind(val kind: String, val iconName: String, val sub: String)
    val APPLY_KINDS = listOf(
        ApplyKind("外出", "cal", "当日帰寮の外出"),
        ApplyKind("外泊", "home", "寮外での宿泊"),
        ApplyKind("帰省", "house", "実家帰省・長期休暇"),
        ApplyKind("帰国", "plane", "一時帰国（航空機利用）"),
        ApplyKind("早帰", "cal-clock", "門限前の早帰・遅帰"),
        ApplyKind("修繕", "wrench", "部屋・設備の修繕依頼"),
        ApplyKind("代理受取", "box", "不在時の荷物代理受取"),
        ApplyKind("来訪者", "people", "家族・友人の来訪"),
        ApplyKind("その他", "chat", "その他の申請"),
        ApplyKind("学習", "book", "自習室・学習関連")
    )

    // Bus 数据 — 对应 React tokens.jsx DATA.bus
    data class BusInfo(val time: String, val date: String, val route: String)
    val DEFAULT_BUS = BusInfo("09:20", "05/06(水)", "高校棟 → 金川駅")

    // Delivery
    data class DeliveryInfo(val count: Int, val source: String, val note: String)
    val DEFAULT_DELIVERY = DeliveryInfo(1, "Amazon", "本日到着")

    // 完整初始 AppState
    val INITIAL_STATE = AppState(
        authed = false,
        onboarded = false,
        user = DEFAULT_USER,
        themeMode = ThemeMode.LIGHT,
        applications = DEFAULT_APPLICATIONS,
        deductions = DEFAULT_DEDUCTIONS,
        notifications = DEFAULT_NOTIFICATIONS,
        musicRequests = DEFAULT_MUSIC
    )
}
