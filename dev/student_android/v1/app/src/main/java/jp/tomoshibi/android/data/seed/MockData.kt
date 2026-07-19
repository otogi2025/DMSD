package jp.tomoshibi.android.data.seed

import jp.tomoshibi.android.data.model.*

// Mock seed 数据 — AppStore 初值 / 解析失败兜底 + 个别尚未接真后端的屏（夜学習履历）。
// 公告/巴士/行事/宅配/失物等已切真后端的假数据段已清掉（B14）。

object MockData {
    val DEFAULT_USER =
        User(
            name = "リュウ イヒ",
            kana = "りゅう いひ",
            email = "demo@example.com",
            dorm = "男寮",
            room = "A5",
            avatar = "リ",
            studentNo = "060218",
            gradeClass = "高3 B組 18番",
            category = "一般寮生",
            phone = "090-0000-0000",
            birthDate = "2006-10-14",
            gender = "男",
            isStudyTarget = false,
        )

    val DEFAULT_APPLICATIONS =
        listOf(
            Application(
                id = "A-2401",
                kind = "外泊",
                dest = "実家（神戸）",
                from = "2025-04-12",
                to = "2025-04-14",
                status = ApplicationStatus.APPROVED,
                reason = "家族行事のため",
                createdAt = "2025-04-08",
            ),
            Application(
                id = "A-2402",
                kind = "外出",
                dest = "梅田 紀伊國屋書店",
                from = "2025-04-19",
                to = "2025-04-19",
                status = ApplicationStatus.PENDING,
                reason = "研究資料の購入",
                createdAt = "2025-04-18",
            ),
            Application(
                id = "A-2403",
                kind = "その他",
                dest = "共用エリア掃除",
                from = "2025-04-05",
                to = "2025-04-05",
                status = ApplicationStatus.RETURNED,
                reason = "掃除当番交代依頼",
                createdAt = "2025-04-04",
            ),
        )

    // 7 条 = 4.5 点（0.5×5 + 1.0×2）— iOS 截图 21.55.04 真值。
    // tier 处罚档：月累计 <8 = 0（无）/ ≥8 = 8（禁足）。
    val DEFAULT_DEDUCTIONS =
        listOf(
            Deduction("D-101", "2026-04-05", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-102", "2026-04-07", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-103", "2026-04-12", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-104", "2026-04-15", 1.0, "晩点呼・欠席", 0),
            Deduction("D-105", "2026-04-18", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-106", "2026-04-20", 1.0, "晩点呼・欠席", 0),
            Deduction("D-107", "2026-04-21", 0.5, "朝点呼・遅刻", 0),
        )

    val DEFAULT_NOTIFICATIONS =
        listOf(
            Notification("N1", "宅配", "Amazon 荷物到着", "寮管理員室で受取り", "今日 14:20", false),
            Notification("N2", "申請", "外泊申請が承認されました", "田中先生が承認しました", "昨日 16:30", false),
            Notification("N3", "減点", "遅刻警告", "今月の遅刻が 5 回に到達", "昨日 9:00", false),
            Notification("N4", "活動", "明日 18:00 新入生歓迎会", "食堂集合", "昨日", false),
            Notification("N5", "リクエスト曲", "あなたの投稿曲が採用されました", "Lemon / 米津玄師", "2 日前", true),
        )

    val DEFAULT_MUSIC =
        listOf(
            MusicRequest("M1", "春の歌", "中島みゆき", 12),
            MusicRequest("M2", "プラネタリウム", "大塚愛", 8),
            MusicRequest("M3", "Lemon", "米津玄師", 22),
        )

    // 夜学习出席打卡履历假数据（MyStudyScreen 仍读这里；iOS 生产也是本地 NFC tap 记录，非 GET 列表）
    val DEFAULT_STUDY_HISTORY: List<StudyHistoryEntry> =
        listOf(
            StudyHistoryEntry("sh1", "2026-05-10", StudyTap.START.name, "19:38"),
            StudyHistoryEntry("sh2", "2026-05-10", StudyTap.END.name, "21:42"),
            StudyHistoryEntry("sh3", "2026-05-09", StudyTap.START.name, "19:52", note = "遅刻"),
            StudyHistoryEntry("sh4", "2026-05-09", StudyTap.END.name, "21:43"),
            StudyHistoryEntry("sh5", "2026-05-08", StudyTap.START.name, "19:39"),
        )

    // 当月夜学习欠席届累计（MyStudyScreen 仍引用）
    const val STUDY_LEAVE_COUNT = 2

    // 完整初始 AppState — fresh state（走完整 Onboarding → Account → Welcome → Login → Home）
    val INITIAL_STATE =
        AppState(
            authed = false,
            onboarded = false,
            user = DEFAULT_USER,
            themeMode = ThemeMode.LIGHT,
            rollState = RollState.IDLE,
            applications = DEFAULT_APPLICATIONS,
            deductions = DEFAULT_DEDUCTIONS,
            notifications = DEFAULT_NOTIFICATIONS,
            musicRequests = DEFAULT_MUSIC,
        )
}
