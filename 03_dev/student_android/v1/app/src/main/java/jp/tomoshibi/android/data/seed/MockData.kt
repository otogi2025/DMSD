package jp.tomoshibi.android.data.seed

import jp.tomoshibi.android.data.model.*

// Mock seed 数据 — 对应 React tokens.jsx DATA + app-shell.jsx DEFAULT_STATE 默认值
// + iOS SEED.swift 的 060218 リュウイヒ 真值
// v1.0 demo 用，P6 接 backend 时换成真实 Repository

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
    // tier 按 §862 规则取「该条之后的月累计」对应处罚档：月累计 <4 = 0（无）/ ≥4 = 4（罚扫）/ ≥8 = 8（禁足）。
    // 本月累计 0.5→1.0→1.5→2.5→3.0→4.0→4.5：前 5 条 <4 = 0，第 6 条起 ≥4 = 4（罚扫），未达 8。
    val DEFAULT_DEDUCTIONS =
        listOf(
            Deduction("D-101", "2026-04-05", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-102", "2026-04-07", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-103", "2026-04-12", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-104", "2026-04-15", 1.0, "晩点呼・欠席", 0),
            Deduction("D-105", "2026-04-18", 0.5, "朝点呼・遅刻", 0),
            Deduction("D-106", "2026-04-20", 1.0, "晩点呼・欠席", 4),
            Deduction("D-107", "2026-04-21", 0.5, "朝点呼・遅刻", 4),
        )

    val DEFAULT_NOTIFICATIONS =
        listOf(
            Notification("N1", "宅配", "Amazon 荷物到着", "寮管理員室で受取り", "今日 14:20", false),
            Notification("N2", "申請", "外泊申請が承認されました", "田中先生が承認しました", "昨日 16:30", false),
            Notification("N3", "減点", "遅刻警告", "今月の遅刻が 5 回に到達", "昨日 9:00", false),
            Notification("N4", "活動", "明日 18:00 新入生歓迎会", "食堂集合", "昨日", false),
            Notification("N5", "リクエスト", "あなたの投稿曲が採用されました", "Lemon / 米津玄師", "2 日前", true),
        )

    val DEFAULT_MUSIC =
        listOf(
            MusicRequest("M1", "春の歌", "中島みゆき", 12),
            MusicRequest("M2", "プラネタリウム", "大塚愛", 8),
            MusicRequest("M3", "Lemon", "米津玄師", 22),
        )

    // 失物 — Home omnibus 3 色块 grid（对应 iOS / React DATA.lostFound）
    val DEFAULT_LOST_FOUND =
        listOf(
            LostItem("L1", "青いおりたたみ傘", "FFA9C8E8"),
            LostItem("L2", "黒の鍵", "FF9DA3A4"),
            LostItem("L3", "赤のペンケース", "FFEC9FAA"),
        )

    // 宅配 — 4 条（1 待領 + 3 領済），对齐 iOS SEED.packages
    val DEFAULT_PACKAGES =
        listOf(
            PackageItem(1, "本日", "Amazon", "待領", "JP1234567890"),
            PackageItem(2, "04-22", "佐川急便", "領済"),
            PackageItem(3, "04-18", "ヤマト運輸", "領済", "460-1234-5678"),
            PackageItem(4, "04-10", "郵便局", "領済"),
        )

    // 点呼履历 — 2026-04-05 ~ 04-21 每天朝/晩两条（对齐 iOS SEED.rollcall）
    // 遅刻日（朝）= 5/7/12/18/21；欠席日（晩）= 15/20；其余時間内
    val DEFAULT_ROLLCALL: List<RollcallEntry> =
        buildList {
            val lateMorning = setOf(5, 7, 12, 18, 21)
            val absentEvening = setOf(15, 20)
            for (d in 5..21) {
                val dd = "%02d".format(d)
                val date = "2026-04-$dd"
                val mStatus = if (d in lateMorning) "遅刻" else "時間内"
                add(RollcallEntry("RC-04$dd-AM", date, "朝点呼", mStatus, "NFC"))
                val eStatus = if (d in absentEvening) "欠席" else "時間内"
                add(RollcallEntry("RC-04$dd-PM", date, "晩点呼", eStatus, if (eStatus == "欠席") "―" else "NFC"))
            }
        }

    // 体调报告履历 — 2 条（对齐 iOS SEED.health）
    val DEFAULT_HEALTH =
        listOf(
            HealthRecord("H1", "2026-04-14", "頭痛", 37.2, "午後ずっと頭が重い"),
            HealthRecord("H2", "2026-04-03", "腹痛"),
        )

    // 扫除提出履历 — 2 条（对齐 iOS SEED.cleaning）
    val DEFAULT_CLEANING =
        listOf(
            CleaningRecord("C1", "2026-04-19", "部屋", "通過", 5),
            CleaningRecord("C2", "2026-04-05", "共用エリア", "退回", null, "床が汚れている"),
        )

    // 特別運航便假数据 — 5 个日别（对应 iOS SEED.busSchedule，含通学便/特別便/空港便）
    val DEFAULT_BUS_ROUTES =
        listOf(
            SpecialBusRoute("B1", "2026-04-29", "水", "08:30", "寮 → 高校棟", "通学便"),
            SpecialBusRoute("B2", "2026-04-29", "水", "18:00", "高校棟 → 寮", "通学便"),
            SpecialBusRoute("B3", "2026-05-06", "水", "07:00", "寮 → 関西空港", "特別便", isAirport = true, seats = "残り 8 席"),
            SpecialBusRoute("B4", "2026-05-06", "水", "09:20", "高校棟 → 金川駅", "通学便"),
            SpecialBusRoute("B5", "2026-05-16", "土", "10:00", "寮 → 伊丹空港", "特別便", isAirport = true, seats = "残り 3 席"),
            SpecialBusRoute("B6", "2026-05-23", "土", "08:00", "寮 → 高校棟", "通学便"),
            SpecialBusRoute("B7", "2026-05-31", "日", "13:00", "寮 → 関西空港", "特別便", isAirport = true, seats = "満席"),
        )

    // 老师公告列表假数据（对应 iOS announcement list）
    val DEFAULT_ANNOUNCEMENTS =
        listOf(
            AnnouncementBrief(
                "AN1",
                "ゴールデンウィークの帰省について",
                "GW 期間中の帰省届は 4/25 までに提出してください。バスの増便もあります。",
                "田中先生",
                "2 時間前",
                isRead = false,
                replyCount = 2,
            ),
            AnnouncementBrief(
                "AN2",
                "防災訓練のお知らせ",
                "5 月 16 日（土）10:00 より避難訓練を実施します。全寮生参加必須です。",
                "佐藤先生",
                "昨日",
                isRead = true,
                replyCount = 0,
            ),
        )

    // 公告详情假数据（按 id 取，含回复链）
    val DEFAULT_ANNOUNCEMENT_DETAILS =
        listOf(
            AnnouncementDetail(
                "AN1",
                "ゴールデンウィークの帰省について",
                "GW 期間中（4/29〜5/6）の帰省を希望する寮生は、帰省届を 4/25（金）までに寮務室へ提出してください。\n\n空港送迎便の増便も予定しています。詳細は「特別運航便」のページをご確認ください。",
                "田中先生",
                "2026/04/20 14:30",
                listOf(
                    AnnouncementReply("リュウ イヒ", "student", "2026/04/20 15:10", "バスの時刻表はどこで確認できますか？"),
                    AnnouncementReply("田中先生", "teacher", "2026/04/20 16:00", "アプリの「特別運航便」から確認できます。"),
                ),
            ),
            AnnouncementDetail(
                "AN2",
                "防災訓練のお知らせ",
                "5 月 16 日（土）10:00 より避難訓練を実施します。全寮生の参加が必須です。\n\n当日は寮玄関前に集合してください。",
                "佐藤先生",
                "2026/05/15 09:00",
                emptyList(),
            ),
        )

    // 今週の活動 14 件 + 2 行 preview（iOS Home 「行事」section）
    const val EVENTS_THIS_WEEK = 14
    val EVENTS_PREVIEW =
        listOf(
            EventItem("04-05", "留 4 アクティビティ", "08:30"),
            EventItem("04-07", "帰寮日", "15:33"),
        )

    // 申请类型选项 — 对应 React tokens.jsx applyKinds
    data class ApplyKind(
        val kind: String,
        val iconName: String,
        val sub: String,
    )

    val APPLY_KINDS =
        listOf(
            ApplyKind("外出", "cal", "当日帰寮の外出"),
            ApplyKind("外泊", "home", "寮外での宿泊"),
            ApplyKind("帰省", "house", "実家帰省・長期休暇"),
            ApplyKind("帰国", "plane", "一時帰国（航空機利用）"),
            ApplyKind("早帰", "cal-clock", "門限前の早帰・遅帰"),
            ApplyKind("修繕", "wrench", "部屋・設備の修繕依頼"),
            ApplyKind("代理受取", "box", "不在時の荷物代理受取"),
            ApplyKind("来訪者", "people", "家族・友人の来訪"),
            ApplyKind("その他", "chat", "その他の申請"),
            ApplyKind("学習", "book", "自習室・学習関連"),
        )

    // Bus 数据 — 对应 React tokens.jsx DATA.bus
    data class BusInfo(
        val time: String,
        val date: String,
        val route: String,
    )

    val DEFAULT_BUS = BusInfo("09:20", "05/06(水)", "高校棟 → 金川駅")

    // Delivery
    data class DeliveryInfo(
        val count: Int,
        val source: String,
        val note: String,
    )

    val DEFAULT_DELIVERY = DeliveryInfo(1, "Amazon", "本日到着")

    // 完整初始 AppState — fresh state（走完整 Onboarding → Account → Welcome → Login → Home）
    // Account 注册各 step 默认预填 demo seed，itsuki 一路点「次へ」走完，不用手动填
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
